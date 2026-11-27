import asyncio

from openpyxl import load_workbook

from app.agent import notifier
from app.catalog import build_catalog
from app.config import get_settings
from app.content import AREAS, all_services, format_clp


def test_build_catalog_formulas(tmp_path):
    path = build_catalog(tmp_path / "cat.xlsx")
    wb = load_workbook(path)
    cat = wb["Catálogo"]
    n = len(all_services())
    assert cat.cell(row=5, column=9).value == "=H5*Notas!$B$6"  # IVA desde la celda de supuestos
    assert cat.cell(row=5, column=10).value == "=H5+I5"
    assert wb["Notas"]["B6"].value == 0.19
    assert cat.auto_filter.ref == f"A4:K{4 + n}"
    quote = wb["Cotizador"]
    assert quote.cell(row=5, column=3).value.startswith("=INDEX(")
    assert wb["Resumen por área"].cell(row=4 + len(AREAS), column=1).value == "Total"


def test_formato_clp():
    assert format_clp(1234567) == "$1.234.567"


def test_digest_html_escapa_contenido():
    jobs = [
        {
            "title": "<script>x</script>",
            "company": "A&B",
            "location": "Chile",
            "url": "https://x/1",
            "source": "getonboard",
            "score": 90,
        }
    ]
    subject, html_body, text = notifier.render_jobs_digest(jobs, "https://nodosur.onrender.com")
    assert "1 nuevas ofertas" in subject
    assert "<script>" not in html_body and "&lt;script&gt;" in html_body
    assert "https://nodosur.onrender.com/admin" in html_body
    assert "[90]" in text


def test_envio_smtp(monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            sent["host"] = (host, port)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def starttls(self):
            sent["tls"] = True

        def login(self, user, pwd):
            sent["login"] = user

        def send_message(self, msg):
            sent["to"] = msg["To"]

    settings = get_settings()
    monkeypatch.setattr(settings, "smtp_host", "smtp.gmail.com")
    monkeypatch.setattr(settings, "smtp_user", "ely@gmail.com")
    monkeypatch.setattr(settings, "smtp_password", "app-pass")
    monkeypatch.setattr(notifier.smtplib, "SMTP", FakeSMTP)
    ok = asyncio.run(notifier.send_email("dest@x.cl", "Hola", "<p>hola</p>", "hola"))
    assert ok and sent == {"host": ("smtp.gmail.com", 587), "tls": True, "login": "ely@gmail.com", "to": "dest@x.cl"}


def test_sin_smtp_no_envia():
    assert asyncio.run(notifier.send_email("a@b.cl", "s", "h", "t")) is False
