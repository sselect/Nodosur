"""Puntaje 0-100 de cada oferta según la configuración del agente.

Regla simple y explicable:
- Sin ninguna palabra clave -> 0 (se descarta).
- Palabra clave en el título: +35 la primera, +10 cada extra.
- Palabra clave en etiquetas/descripción: +15 la primera, +5 cada extra.
- Ubicación preferida (país o remoto): +20.
- Publicada hace <= 3 días: +10 (<= 7 días: +5).
- Informa sueldo: +5.
"""

import re
from datetime import UTC, datetime

from app.agent.sources.base import JobPosting, normalize

REMOTE_WORDS = {"remoto", "remote", "anywhere", "worldwide", "global", "latam", "teletrabajo"}


def _contains(haystack: str, needle: str) -> bool:
    if len(needle) <= 3:  # "qa", "sre", "erp": palabra completa
        return re.search(rf"\b{re.escape(needle)}\b", haystack) is not None
    return needle in haystack


def is_excluded(job: JobPosting, exclude: list[str]) -> bool:
    text = normalize(f"{job.title} {' '.join(job.tags)}")
    return any(_contains(text, normalize(word)) for word in exclude if word.strip())


def location_match(job: JobPosting, locations: list[str]) -> bool:
    if not locations:
        return True
    prefs = {normalize(loc) for loc in locations}
    place = normalize(f"{job.location} {job.country}")
    wants_remote = bool(prefs & {"remoto", "remote"})
    if job.remote and wants_remote:
        return True
    return any(p and p in place for p in prefs if p not in {"remoto", "remote"})


def score_job(
    job: JobPosting,
    keywords: list[str],
    locations: list[str],
    now: datetime | None = None,
) -> tuple[int, list[str]]:
    title = normalize(job.title)
    body = normalize(f"{' '.join(job.tags)} {job.description}")

    in_title, in_body = [], []
    for raw in keywords:
        kw = normalize(raw)
        if not kw:
            continue
        if _contains(title, kw):
            in_title.append(raw)
        elif _contains(body, kw):
            in_body.append(raw)

    if not in_title and not in_body:
        return 0, []

    score = 0
    if in_title:
        score += 35 + 10 * (len(in_title) - 1)
    if in_body:
        score += 15 + 5 * (len(in_body) - 1)
    if location_match(job, locations):
        score += 20
    if job.published_at:
        reference = now or datetime.now(UTC).replace(tzinfo=None)
        age_days = (reference - job.published_at).days
        if age_days <= 3:
            score += 10
        elif age_days <= 7:
            score += 5
    if job.salary_min or job.salary_max:
        score += 5

    return min(score, 100), in_title + in_body
