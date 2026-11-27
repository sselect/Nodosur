"""Panel de administración: login, configuración del agente, dashboard en vivo y leads."""

import asyncio
import csv
import io
from collections import Counter
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.agent.runner import get_config, is_due, last_finished_run, run_agent
from app.agent.sources import REGISTRY
from app.config import get_settings
from app.db import SessionLocal, get_db
from app.events import bus, format_sse
from app.models import JOB_STATUSES, AgentRun, Job, Lead, SourceState, utcnow
from app.security import (
    SESSION_KEY,
    check_credentials,
    client_ip,
    is_admin,
    login_limiter,
    require_admin,
    require_admin_write,
)

router = APIRouter(prefix="/admin")
api = APIRouter(prefix="/admin/api", dependencies=[Depends(require_admin)])
templates = Jinja2Templates(directory="app/templates")

# Palabras que indican que la empresa busca cubrir soporte/infra: prospectos para outsourcing
PROSPECT_WORDS = [
    "soporte",
    "support",
    "helpdesk",
    "mesa de ayuda",
    "infraestructura",
    "sysadmin",
    "devops",
    "sre",
    "erp",
]


# ---------------- Páginas ----------------
@router.get("/login", include_in_schema=False)
def login_page(request: Request):
    if is_admin(request):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(request, "admin/login.html", {"error": None})


@router.post("/login", include_in_schema=False)
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    if not login_limiter.hit(client_ip(request)):
        return templates.TemplateResponse(
            request, "admin/login.html", {"error": "Demasiados intentos. Espera 10 minutos."}, status_code=429
        )
    if not check_credentials(email, password, get_settings()):
        return templates.TemplateResponse(
            request, "admin/login.html", {"error": "Correo o contraseña incorrectos."}, status_code=401
        )
    request.session.clear()
    request.session[SESSION_KEY] = True
    return RedirectResponse("/admin", status_code=303)


@router.post("/logout", include_in_schema=False)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


@router.get("", include_in_schema=False)
def dashboard(request: Request):
    if not is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    sources = [{"name": s.name, "label": s.label, "homepage": s.homepage} for s in REGISTRY.values()]
    return templates.TemplateResponse(request, "admin/dashboard.html", {"sources": sources})


# ---------------- API ----------------
@api.get("/stats")
def stats(db: Session = Depends(get_db)):
    now = utcnow()
    total = db.scalar(select(func.count(Job.id))) or 0
    last_24h = db.scalar(select(func.count(Job.id)).where(Job.collected_at >= now - timedelta(hours=24))) or 0
    avg_score = db.scalar(select(func.avg(Job.score))) or 0
    by_source = dict(db.execute(select(Job.source, func.count(Job.id)).group_by(Job.source)).all())
    by_status = dict(db.execute(select(Job.status, func.count(Job.id)).group_by(Job.status)).all())
    remote = db.scalar(select(func.count(Job.id)).where(Job.remote.is_(True))) or 0

    since = now - timedelta(days=13)
    day = func.date(Job.collected_at)
    by_day_rows = db.execute(
        select(day, func.count(Job.id)).where(Job.collected_at >= since).group_by(day).order_by(day)
    ).all()
    by_day_map = {str(d): c for d, c in by_day_rows}
    by_day = []
    for i in range(14):
        key = (since + timedelta(days=i)).date().isoformat()
        by_day.append({"date": key, "count": by_day_map.get(key, 0)})

    buckets = {"0-49": 0, "50-69": 0, "70-84": 0, "85-100": 0}
    for (score,) in db.execute(select(Job.score)).all():
        if score >= 85:
            buckets["85-100"] += 1
        elif score >= 70:
            buckets["70-84"] += 1
        elif score >= 50:
            buckets["50-69"] += 1
        else:
            buckets["0-49"] += 1

    kw_counter: Counter = Counter()
    for (kws,) in db.execute(select(Job.matched_keywords).order_by(Job.collected_at.desc()).limit(1000)).all():
        kw_counter.update(k.lower() for k in (kws or []))

    cfg = get_config(db)
    last = last_finished_run(db)
    next_run = (last.started_at + timedelta(minutes=cfg.interval_minutes)).isoformat() if last else None
    states = {s.source: s for s in db.scalars(select(SourceState)).all()}
    new_leads = db.scalar(select(func.count(Lead.id)).where(Lead.status == "new")) or 0

    return {
        "total": total,
        "last_24h": last_24h,
        "avg_score": round(float(avg_score), 1),
        "remote": remote,
        "onsite": total - remote,
        "by_source": by_source,
        "by_status": {s: by_status.get(s, 0) for s in JOB_STATUSES},
        "by_day": by_day,
        "score_buckets": buckets,
        "top_keywords": kw_counter.most_common(10),
        "agent": {
            "active": cfg.active,
            "interval_minutes": cfg.interval_minutes,
            "due": is_due(db, cfg),
            "last_run": last.to_dict() if last else None,
            "next_run": next_run,
        },
        "sources": [
            {
                "name": s.name,
                "label": s.label,
                "enabled": s.name in cfg.sources,
                "last_fetch_at": states[s.name].last_fetch_at.isoformat()
                if s.name in states and states[s.name].last_fetch_at
                else None,
                "last_status": states[s.name].last_status if s.name in states else "",
                "last_count": states[s.name].last_count if s.name in states else 0,
                "last_error": states[s.name].last_error if s.name in states else "",
            }
            for s in REGISTRY.values()
        ],
        "new_leads": new_leads,
        "live_clients": bus.subscriber_count,
    }


@api.get("/jobs")
def list_jobs(
    db: Session = Depends(get_db),
    q: str = "",
    source: str = "",
    status: str = "",
    min_score: int = Query(0, ge=0, le=100),
    remote: str = "",
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    sort: str = Query("recent", pattern="^(recent|score)$"),
):
    stmt = select(Job)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Job.title.ilike(like), Job.company.ilike(like), Job.location.ilike(like)))
    if source:
        stmt = stmt.where(Job.source == source)
    if status in JOB_STATUSES:
        stmt = stmt.where(Job.status == status)
    if min_score:
        stmt = stmt.where(Job.score >= min_score)
    if remote in ("1", "0"):
        stmt = stmt.where(Job.remote.is_(remote == "1"))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    order = (Job.score.desc(), Job.collected_at.desc()) if sort == "score" else (Job.collected_at.desc(),)
    rows = db.scalars(stmt.order_by(*order).offset((page - 1) * per_page).limit(per_page)).all()
    return {"total": total, "page": page, "per_page": per_page, "items": [j.to_dict() for j in rows]}


class JobPatch(BaseModel):
    status: str


@api.patch("/jobs/{job_id}", dependencies=[Depends(require_admin_write)])
def update_job(job_id: int, payload: JobPatch, db: Session = Depends(get_db)):
    if payload.status not in JOB_STATUSES:
        raise HTTPException(422, "Estado inválido")
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Oferta no encontrada")
    job.status = payload.status
    db.commit()
    bus.publish("job_updated", {"id": job.id, "status": job.status})
    return job.to_dict()


@api.get("/jobs.csv")
def export_jobs(db: Session = Depends(get_db)):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["id", "fuente", "titulo", "empresa", "ubicacion", "remoto", "puntaje", "estado", "url", "recolectada"]
    )
    for j in db.scalars(select(Job).order_by(Job.collected_at.desc()).limit(5000)).all():
        writer.writerow(
            [j.id, j.source, j.title, j.company, j.location, j.remote, j.score, j.status, j.url, j.collected_at]
        )
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ofertas-nodosur.csv"},
    )


@api.get("/companies")
def prospects(db: Session = Depends(get_db), limit: int = Query(15, ge=1, le=50)):
    """Empresas que publican avisos de soporte/infra: candidatas a externalizar con NodoSur."""
    conditions = [Job.title.ilike(f"%{w}%") for w in PROSPECT_WORDS]
    rows = db.execute(
        select(Job.company, func.count(Job.id), func.max(Job.collected_at))
        .where(Job.company != "", or_(*conditions))
        .group_by(Job.company)
        .order_by(func.count(Job.id).desc())
        .limit(limit)
    ).all()
    return [{"company": c, "openings": n, "last_seen": d.isoformat() if d else None} for c, n, d in rows]


class ConfigIn(BaseModel):
    active: bool
    keywords: list[str] = Field(max_length=40)
    exclude_keywords: list[str] = Field(default_factory=list, max_length=40)
    locations: list[str] = Field(default_factory=list, max_length=20)
    sources: list[str] = Field(default_factory=list)
    min_score: int = Field(ge=0, le=100)
    notify_min_score: int = Field(ge=0, le=100)
    interval_minutes: int = Field(ge=15, le=1440)
    max_age_days: int = Field(ge=1, le=90)
    notify_email: str = Field(default="", max_length=200)

    @field_validator("keywords", "exclude_keywords", "locations")
    @classmethod
    def clean_list(cls, v: list[str]) -> list[str]:
        seen, out = set(), []
        for item in v:
            item = item.strip()[:60]
            if item and item.lower() not in seen:
                seen.add(item.lower())
                out.append(item)
        return out

    @field_validator("sources")
    @classmethod
    def valid_sources(cls, v: list[str]) -> list[str]:
        unknown = [s for s in v if s not in REGISTRY]
        if unknown:
            raise ValueError(f"Fuentes desconocidas: {unknown}")
        return v


@api.get("/config")
def read_config(db: Session = Depends(get_db)):
    return get_config(db).to_dict()


@api.put("/config", dependencies=[Depends(require_admin_write)])
def write_config(payload: ConfigIn, db: Session = Depends(get_db)):
    if not payload.keywords:
        raise HTTPException(422, "Agrega al menos una palabra clave")
    cfg = get_config(db)
    for key, value in payload.model_dump().items():
        setattr(cfg, key, value)
    db.commit()
    bus.publish("config_updated", cfg.to_dict())
    return cfg.to_dict()


async def _background_run() -> None:
    db = SessionLocal()
    try:
        await run_agent(db, trigger="manual", force=True)
    finally:
        db.close()


@api.post("/run", dependencies=[Depends(require_admin_write)])
async def run_now(background: BackgroundTasks):
    background.add_task(_background_run)
    return {"ok": True, "message": "Ejecución iniciada; sigue el progreso en vivo"}


@api.get("/runs")
def runs(db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=100)):
    rows = db.scalars(select(AgentRun).order_by(AgentRun.started_at.desc()).limit(limit)).all()
    return [r.to_dict() for r in rows]


@api.get("/leads")
def leads(db: Session = Depends(get_db), limit: int = Query(50, ge=1, le=200)):
    rows = db.scalars(select(Lead).order_by(Lead.created_at.desc()).limit(limit)).all()
    return [lead.to_dict() for lead in rows]


class LeadPatch(BaseModel):
    status: str = Field(pattern="^(new|contacted|proposal|won|lost)$")


@api.patch("/leads/{lead_id}", dependencies=[Depends(require_admin_write)])
def update_lead(lead_id: int, payload: LeadPatch, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead no encontrado")
    lead.status = payload.status
    db.commit()
    return lead.to_dict()


@api.get("/stream")
async def stream(request: Request):
    """Server-Sent Events: el dashboard recibe ofertas y ejecuciones en tiempo real."""
    queue = bus.subscribe()

    async def events():
        try:
            yield "retry: 5000\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15)
                    yield format_sse(payload)
                except TimeoutError:
                    yield ": keep-alive\n\n"
        finally:
            bus.unsubscribe(queue)

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
