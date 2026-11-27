"""Orquestador del agente: buscar -> filtrar -> puntuar -> deduplicar -> guardar -> notificar."""

import asyncio
import logging
from datetime import timedelta

import httpx
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.agent.notifier import render_jobs_digest, send_email
from app.agent.scoring import is_excluded, score_job
from app.agent.sources import REGISTRY, JobPosting, JobSource
from app.agent.sources.base import USER_AGENT
from app.config import get_settings
from app.events import bus
from app.models import AgentConfig, AgentRun, Job, SourceState, utcnow

log = logging.getLogger("nodosur.agent")

_run_lock = asyncio.Lock()


def get_config(db: Session) -> AgentConfig:
    cfg = db.get(AgentConfig, 1)
    if cfg is None:
        cfg = AgentConfig(id=1, notify_email=get_settings().notify_to)
        db.add(cfg)
        db.commit()
    return cfg


def last_finished_run(db: Session) -> AgentRun | None:
    stmt = select(AgentRun).where(AgentRun.status.in_(["ok", "partial"])).order_by(AgentRun.started_at.desc()).limit(1)
    return db.scalars(stmt).first()


def is_due(db: Session, cfg: AgentConfig) -> bool:
    last = last_finished_run(db)
    if last is None:
        return True
    return utcnow() - last.started_at >= timedelta(minutes=max(cfg.interval_minutes, 5))


def _source_due(db: Session, source: JobSource) -> bool:
    state = db.get(SourceState, source.name)
    if state is None or state.last_fetch_at is None:
        return True
    return utcnow() - state.last_fetch_at >= timedelta(minutes=source.min_interval_minutes)


async def _fetch_one(client: httpx.AsyncClient, source: JobSource, keywords: list[str]) -> list[JobPosting]:
    return await source.fetch(client, keywords)


async def run_agent(
    db: Session,
    trigger: str = "manual",
    force: bool = False,
    client: httpx.AsyncClient | None = None,
) -> AgentRun:
    """Ejecuta una vuelta del agente. Seguro ante llamadas concurrentes."""
    if _run_lock.locked():
        return AgentRun(trigger=trigger, status="skipped", message="Ya hay una ejecución en curso")

    async with _run_lock:
        cfg = get_config(db)
        if not force and not cfg.active:
            return AgentRun(trigger=trigger, status="skipped", message="Agente pausado")
        if not force and not is_due(db, cfg):
            return AgentRun(trigger=trigger, status="skipped", message="Aún no toca según el intervalo")

        run = AgentRun(trigger=trigger, status="running")
        db.add(run)
        db.commit()
        bus.publish("run_started", {"run_id": run.id, "trigger": trigger})

        sources = [
            REGISTRY[name] for name in cfg.sources if name in REGISTRY and (force or _source_due(db, REGISTRY[name]))
        ]
        # Aun con force se respetan los límites estrictos (p.ej. Remotive: 4/día)
        sources = [s for s in sources if s.min_interval_minutes < 360 or _source_due(db, s)]

        owns_client = client is None
        settings = get_settings()
        client = client or httpx.AsyncClient(
            timeout=settings.http_timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            follow_redirects=True,
        )
        try:
            results = await asyncio.gather(
                *(_fetch_one(client, s, cfg.keywords) for s in sources), return_exceptions=True
            )
        finally:
            if owns_client:
                await client.aclose()

        per_source: dict[str, dict] = {}
        postings: list[JobPosting] = []
        errors = 0
        for source, result in zip(sources, results, strict=True):
            state = db.get(SourceState, source.name) or SourceState(source=source.name)
            state.last_fetch_at = utcnow()
            if isinstance(result, Exception):
                errors += 1
                state.last_status, state.last_count = "error", 0
                state.last_error = f"{type(result).__name__}: {result}"[:500]
                per_source[source.name] = {"status": "error", "error": state.last_error}
                log.warning("Fuente %s falló: %s", source.name, result)
            else:
                state.last_status, state.last_count, state.last_error = "ok", len(result), ""
                per_source[source.name] = {"status": "ok", "fetched": len(result), "new": 0}
                postings.extend(result)
            db.merge(state)
            bus.publish("source_done", {"source": source.name, **per_source[source.name]})
        db.commit()

        cutoff = utcnow() - timedelta(days=cfg.max_age_days)
        new_jobs: list[Job] = []
        matched = 0
        seen_fps: set[str] = set()
        for posting in postings:
            if posting.published_at and posting.published_at < cutoff:
                continue
            if is_excluded(posting, cfg.exclude_keywords):
                continue
            score, hits = score_job(posting, cfg.keywords, cfg.locations)
            if score < cfg.min_score:
                continue
            matched += 1
            fp = posting.fingerprint
            if fp in seen_fps:
                continue
            seen_fps.add(fp)
            exists = db.scalars(
                select(Job.id).where(
                    or_(
                        (Job.source == posting.source) & (Job.external_id == posting.external_id),
                        Job.fingerprint == fp,
                    )
                )
            ).first()
            if exists:
                continue
            job = Job(
                source=posting.source,
                external_id=posting.external_id[:200],
                fingerprint=fp,
                url=posting.url[:1000],
                title=posting.title[:300],
                company=posting.company[:200],
                location=posting.location[:200],
                country=posting.country[:80],
                remote=posting.remote,
                modality=posting.modality[:40],
                tags=posting.tags,
                salary_min=posting.salary_min,
                salary_max=posting.salary_max,
                currency=posting.currency[:10],
                description=posting.description,
                published_at=posting.published_at,
                score=score,
                matched_keywords=hits,
            )
            db.add(job)
            new_jobs.append(job)
            per_source.setdefault(posting.source, {"status": "ok"})
            per_source[posting.source]["new"] = per_source[posting.source].get("new", 0) + 1
        db.commit()

        for job in new_jobs:
            bus.publish("job_new", job.to_dict())

        notified = 0
        to_notify = [j for j in new_jobs if j.score >= cfg.notify_min_score]
        if to_notify:
            recipient = cfg.notify_email or settings.notify_to
            top = sorted(to_notify, key=lambda j: j.score, reverse=True)[:25]
            subject, html_body, text_body = render_jobs_digest([j.to_dict() for j in top], settings.public_base_url)
            if await send_email(recipient, subject, html_body, text_body):
                for job in top:
                    job.notified = True
                notified = len(top)

        run.fetched = len(postings)
        run.matched = matched
        run.new_jobs = len(new_jobs)
        run.notified = notified
        run.per_source = per_source
        run.finished_at = utcnow()
        if not sources:
            run.status, run.message = "ok", "Ninguna fuente tocaba en esta vuelta (límites de API)"
        elif errors == len(sources):
            run.status, run.message = "error", "Todas las fuentes fallaron"
        elif errors:
            run.status, run.message = "partial", f"{errors} fuente(s) con error"
        else:
            run.status, run.message = "ok", ""
        db.commit()
        bus.publish("run_finished", run.to_dict())
        log.info("Agente: %s nuevas / %s coincidencias / %s leídas", len(new_jobs), matched, len(postings))
        return run


async def scheduler_loop(stop: asyncio.Event) -> None:
    """Planificador interno (solo si ENABLE_SCHEDULER=true, p.ej. plan pago siempre encendido)."""
    from app.db import SessionLocal

    while not stop.is_set():
        db = SessionLocal()
        try:
            cfg = get_config(db)
            if cfg.active and is_due(db, cfg):
                await run_agent(db, trigger="scheduler")
        except Exception:  # noqa: BLE001 - el planificador nunca debe morir
            log.exception("Error en el planificador del agente")
        finally:
            db.close()
        try:
            await asyncio.wait_for(stop.wait(), timeout=60)
        except TimeoutError:
            pass
