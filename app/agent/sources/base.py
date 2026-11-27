"""Contrato común de las fuentes de empleo.

Solo se usan APIs públicas y oficiales de cada portal (sin scraping de HTML),
respetando sus límites de frecuencia y su exigencia de atribución (enlace al aviso original).
"""

import hashlib
import html
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import UTC, datetime

import httpx

USER_AGENT = "NodoSurJobAgent/1.0 (+https://nodosur.onrender.com)"


@dataclass
class JobPosting:
    source: str
    external_id: str
    url: str
    title: str
    company: str = ""
    location: str = ""
    country: str = ""
    remote: bool = False
    modality: str = ""
    tags: list[str] = field(default_factory=list)
    salary_min: float | None = None
    salary_max: float | None = None
    currency: str = ""
    description: str = ""
    published_at: datetime | None = None

    @property
    def fingerprint(self) -> str:
        """Huella para detectar el mismo aviso publicado en varios portales."""
        base = f"{normalize(self.title)}|{normalize(self.company)}"
        return hashlib.sha256(base.encode()).hexdigest()[:32]


class JobSource:
    name: str = ""
    label: str = ""
    homepage: str = ""
    # Mínimo de minutos entre consultas, según los términos de cada API
    min_interval_minutes: int = 30

    async def fetch(self, client: httpx.AsyncClient, keywords: list[str]) -> list[JobPosting]:
        raise NotImplementedError

    @staticmethod
    def parse(payload) -> list[JobPosting]:  # pragma: no cover - lo implementa cada fuente
        raise NotImplementedError


TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def strip_html(text: str | None, limit: int = 4000) -> str:
    if not text:
        return ""
    clean = html.unescape(TAG_RE.sub(" ", text))
    return SPACE_RE.sub(" ", clean).strip()[:limit]


def normalize(text: str | None) -> str:
    """Minúsculas y sin tildes, para comparar palabras clave."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower().strip()


def parse_datetime(value) -> datetime | None:
    if value in (None, "", 0):
        return None
    try:
        if isinstance(value, int | float):
            return datetime.fromtimestamp(float(value), UTC).replace(tzinfo=None)
        text = str(value).strip()
        if text.isdigit():
            return datetime.fromtimestamp(float(text), UTC).replace(tzinfo=None)
        text = text.replace("Z", "+00:00")
        if " " in text and "T" not in text:
            text = text.replace(" ", "T", 1)
        dt = datetime.fromisoformat(text)
        if dt.tzinfo:
            dt = dt.astimezone(UTC).replace(tzinfo=None)
        return dt
    except (ValueError, OSError, OverflowError):
        return None


def to_float(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None
