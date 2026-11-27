"""Rutas públicas: landing, catálogo, contacto, asistente y salud."""

import html
import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agent.notifier import send_email
from app.ai.assistant import answer
from app.catalog import CATALOG_PATH, build_catalog
from app.config import get_settings
from app.content import AREAS, COMPANY, FAQ, PROCESS, STATS, format_clp
from app.db import get_db
from app.events import bus
from app.models import Lead
from app.security import RateLimiter, client_ip, contact_limiter

log = logging.getLogger("nodosur.public")
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["clp"] = format_clp

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.IGNORECASE)
assistant_limiter = RateLimiter(limit=30, window=3600)


@router.get("/", include_in_schema=False)
def landing(request: Request):
    return templates.TemplateResponse(
        request,
        "landing.html",
        {
            "company": COMPANY,
            "areas": AREAS,
            "stats": STATS,
            "process": PROCESS,
            "faq": FAQ,
            "service_count": sum(len(a["services"]) for a in AREAS),
        },
    )


@router.get("/descargas/catalogo-servicios-nodosur.xlsx", include_in_schema=False)
def download_catalog():
    if not CATALOG_PATH.exists():
        build_catalog()
    return FileResponse(
        CATALOG_PATH,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="catalogo-servicios-nodosur.xlsx",
    )


class ContactIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(max_length=200)
    company: str = Field(default="", max_length=160)
    phone: str = Field(default="", max_length=40)
    service: str = Field(default="", max_length=120)
    message: str = Field(default="", max_length=3000)
    kind: str = Field(default="contact", pattern="^(contact|erp_demo|ai_demo)$")
    website: str = Field(default="", max_length=200)  # honeypot anti-spam


@router.post("/api/contact")
async def contact(payload: ContactIn, request: Request, db: Session = Depends(get_db)):
    if payload.website:  # bots llenan el campo oculto: respondemos OK sin guardar
        return {"ok": True}
    if not EMAIL_RE.match(payload.email.strip()):
        raise HTTPException(422, "Correo inválido")
    if not contact_limiter.hit(client_ip(request)):
        raise HTTPException(429, "Demasiados envíos, intenta más tarde")
    lead = Lead(
        kind=payload.kind,
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        company=payload.company.strip(),
        phone=payload.phone.strip(),
        service=payload.service.strip(),
        message=payload.message.strip(),
    )
    db.add(lead)
    db.commit()
    bus.publish("lead_new", lead.to_dict())
    settings = get_settings()
    to = settings.contact_to or settings.notify_to
    safe = {k: html.escape(str(v)) for k, v in lead.to_dict().items()}
    await send_email(
        to,
        f"NodoSur · Nuevo contacto: {lead.name} ({lead.service or lead.kind})",
        "<h3>Nuevo contacto desde la web</h3>" + "".join(f"<p><b>{k}</b>: {v}</p>" for k, v in safe.items() if v),
        "\n".join(f"{k}: {v}" for k, v in lead.to_dict().items() if v),
    )
    return {"ok": True, "id": lead.id}


class ChatIn(BaseModel):
    messages: list[dict] = Field(default_factory=list, max_length=20)


@router.post("/api/assistant")
async def assistant(payload: ChatIn, request: Request):
    if not assistant_limiter.hit(client_ip(request)):
        raise HTTPException(429, "Límite de mensajes alcanzado, intenta en una hora")
    return await answer(payload.messages)


@router.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "app": get_settings().app_name}


@router.get("/robots.txt", include_in_schema=False)
def robots():
    base = get_settings().public_base_url.rstrip("/")
    return PlainTextResponse(f"User-agent: *\nDisallow: /admin\nDisallow: /api\nSitemap: {base}/sitemap.xml\n")


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap():
    base = get_settings().public_base_url.rstrip("/")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>{base}/</loc></url></urlset>"
    )
    return PlainTextResponse(xml, media_type="application/xml")
