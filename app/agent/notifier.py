"""Notificaciones por correo (SMTP). Si no hay SMTP configurado, no envía y lo informa."""

import asyncio
import html
import logging
import smtplib
from email.message import EmailMessage

from app.config import Settings, get_settings

log = logging.getLogger("nodosur.notifier")


def _send(settings: Settings, to: str, subject: str, html_body: str, text_body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)


async def send_email(to: str, subject: str, html_body: str, text_body: str) -> bool:
    settings = get_settings()
    if not settings.smtp_enabled or not to:
        log.info("SMTP no configurado o sin destinatario: correo omitido (%s)", subject)
        return False
    try:
        await asyncio.to_thread(_send, settings, to, subject, html_body, text_body)
        return True
    except (smtplib.SMTPException, OSError) as exc:
        log.warning("Error enviando correo: %s", exc)
        return False


def render_jobs_digest(jobs: list[dict], base_url: str) -> tuple[str, str, str]:
    subject = f"NodoSur · {len(jobs)} nuevas ofertas TI que calzan con tu búsqueda"
    rows, lines = [], []
    for job in jobs:
        title = html.escape(job["title"])
        company = html.escape(job.get("company") or "—")
        where = html.escape(job.get("location") or job.get("modality") or "")
        rows.append(
            f"<tr><td style='padding:10px 0;border-bottom:1px solid #e5e7eb'>"
            f"<a href='{html.escape(job['url'])}' style='color:#0f766e;font-weight:600;text-decoration:none'>{title}</a>"
            f"<div style='color:#475569;font-size:13px'>{company} · {where} · vía {html.escape(job['source'])}</div></td>"
            f"<td style='text-align:right;font-weight:700;color:#0f172a'>{job['score']}</td></tr>"
        )
        lines.append(f"[{job['score']}] {job['title']} — {job.get('company', '')} — {job['url']}")
    html_body = (
        "<div style='font-family:Inter,Arial,sans-serif;max-width:640px;margin:auto'>"
        "<h2 style='color:#0f172a'>Nuevas ofertas encontradas por tu agente</h2>"
        "<table style='width:100%;border-collapse:collapse'>"
        "<tr><th style='text-align:left'>Oferta</th><th style='text-align:right'>Puntaje</th></tr>"
        + "".join(rows)
        + f"</table><p><a href='{html.escape(base_url)}/admin'>Abrir dashboard</a></p>"
        "<p style='color:#94a3b8;font-size:12px'>Fuentes: APIs públicas de cada portal. "
        "Cada aviso enlaza a su publicación original.</p></div>"
    )
    return subject, html_body, "\n".join(lines)
