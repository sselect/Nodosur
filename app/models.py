"""Modelos de datos."""

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


DEFAULT_KEYWORDS = [
    "soporte",
    "support",
    "devops",
    "cloud",
    "oracle",
    "fusion",
    "erp",
    "qa",
    "infraestructura",
    "sre",
    "python",
]
DEFAULT_EXCLUDE = ["practicante", "internship", "unpaid"]
DEFAULT_LOCATIONS = ["Chile", "Remoto", "LatAm", "España"]
DEFAULT_SOURCES = ["getonboard", "remotive", "remoteok", "arbeitnow", "himalayas", "jobicy"]

JOB_STATUSES = ("new", "saved", "applied", "discarded")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_job_source_ext"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(40), index=True)
    external_id: Mapped[str] = mapped_column(String(200))
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[str] = mapped_column(String(300))
    company: Mapped[str] = mapped_column(String(200), default="", index=True)
    location: Mapped[str] = mapped_column(String(200), default="")
    country: Mapped[str] = mapped_column(String(80), default="")
    remote: Mapped[bool] = mapped_column(Boolean, default=False)
    modality: Mapped[str] = mapped_column(String(40), default="")
    tags: Mapped[list] = mapped_column(JSON, default=list)
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    matched_keywords: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)
    notified: Mapped[bool] = mapped_column(Boolean, default=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "url": self.url,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "country": self.country,
            "remote": self.remote,
            "modality": self.modality,
            "tags": self.tags or [],
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "currency": self.currency,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
            "score": self.score,
            "matched_keywords": self.matched_keywords or [],
            "status": self.status,
            "notified": self.notified,
        }


class AgentConfig(Base):
    """Configuración del agente (fila única id=1), editable desde el panel."""

    __tablename__ = "agent_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    keywords: Mapped[list] = mapped_column(JSON, default=lambda: list(DEFAULT_KEYWORDS))
    exclude_keywords: Mapped[list] = mapped_column(JSON, default=lambda: list(DEFAULT_EXCLUDE))
    locations: Mapped[list] = mapped_column(JSON, default=lambda: list(DEFAULT_LOCATIONS))
    sources: Mapped[list] = mapped_column(JSON, default=lambda: list(DEFAULT_SOURCES))
    min_score: Mapped[int] = mapped_column(Integer, default=35)
    notify_min_score: Mapped[int] = mapped_column(Integer, default=60)
    interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    max_age_days: Mapped[int] = mapped_column(Integer, default=21)
    notify_email: Mapped[str] = mapped_column(String(200), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self) -> dict:
        return {
            "active": self.active,
            "keywords": self.keywords or [],
            "exclude_keywords": self.exclude_keywords or [],
            "locations": self.locations or [],
            "sources": self.sources or [],
            "min_score": self.min_score,
            "notify_min_score": self.notify_min_score,
            "interval_minutes": self.interval_minutes,
            "max_age_days": self.max_age_days,
            "notify_email": self.notify_email,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trigger: Mapped[str] = mapped_column(String(20), default="manual")
    status: Mapped[str] = mapped_column(String(20), default="running", index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fetched: Mapped[int] = mapped_column(Integer, default=0)
    matched: Mapped[int] = mapped_column(Integer, default=0)
    new_jobs: Mapped[int] = mapped_column(Integer, default=0)
    notified: Mapped[int] = mapped_column(Integer, default=0)
    per_source: Mapped[dict] = mapped_column(JSON, default=dict)
    message: Mapped[str] = mapped_column(Text, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "trigger": self.trigger,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "fetched": self.fetched,
            "matched": self.matched,
            "new_jobs": self.new_jobs,
            "notified": self.notified,
            "per_source": self.per_source or {},
            "message": self.message,
        }


class SourceState(Base):
    """Última consulta por fuente, para respetar los límites de cada API."""

    __tablename__ = "source_state"

    source: Mapped[str] = mapped_column(String(40), primary_key=True)
    last_fetch_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_status: Mapped[str] = mapped_column(String(20), default="")
    last_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str] = mapped_column(Text, default="")


class Lead(Base):
    """Contacto o solicitud recibida desde la landing."""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    kind: Mapped[str] = mapped_column(String(20), default="contact")  # contact | erp_demo
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(160), default="")
    phone: Mapped[str] = mapped_column(String(40), default="")
    service: Mapped[str] = mapped_column(String(120), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="new")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "kind": self.kind,
            "name": self.name,
            "email": self.email,
            "company": self.company,
            "phone": self.phone,
            "service": self.service,
            "message": self.message,
            "status": self.status,
        }
