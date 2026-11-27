"""Conexión a base de datos (SQLite en local/test, Postgres en producción)."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _make_engine(url: str):
    kwargs: dict = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **kwargs)


engine = _make_engine(get_settings().sqlalchemy_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def configure_engine(url: str) -> None:
    """Permite a los tests apuntar a otra base de datos."""
    global engine
    engine = _make_engine(url)
    SessionLocal.configure(bind=engine)


def init_db() -> None:
    from app import models  # noqa: F401  (registra los modelos)

    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
