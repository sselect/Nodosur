import os
import tempfile

import httpx
import pytest

_tmp = tempfile.mkdtemp(prefix="nodosur-test-")
os.environ.update(
    {
        "ENV": "test",
        # En CI se prueba también contra Postgres real con TEST_DATABASE_URL
        "DATABASE_URL": os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{_tmp}/test.db",
        "SECRET_KEY": "test-secret-key-123456",
        "ADMIN_EMAIL": "admin@nodosur.cl",
        "ADMIN_PASSWORD": "clave-de-prueba-123",
        "AGENT_TOKEN": "token-de-prueba-123",
        "ANTHROPIC_API_KEY": "",
        "SMTP_HOST": "",
        "SMTP_USER": "",
        "SMTP_PASSWORD": "",
        "PUBLIC_BASE_URL": "http://testserver",
    }
)

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()

from fastapi.testclient import TestClient  # noqa: E402

from app import security  # noqa: E402
from app.db import Base, engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.routers import public  # noqa: E402
from tests import payloads  # noqa: E402


@pytest.fixture(autouse=True)
def clean_db():
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)
    security.login_limiter.reset()
    security.contact_limiter.reset()
    public.assistant_limiter.reset()


@pytest.fixture
def db():
    from app.db import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin(client):
    resp = client.post(
        "/admin/login",
        data={"email": "admin@nodosur.cl", "password": "clave-de-prueba-123"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    client.headers.update({"X-NodoSur": "1"})
    return client


def make_transport(fail: set[str] | None = None, calls: list | None = None) -> httpx.MockTransport:
    """Simula las APIs públicas. `fail` = hosts que responden 503."""
    fail = fail or set()

    def handler(request: httpx.Request) -> httpx.Response:
        host = request.url.host
        if calls is not None:
            calls.append(host)
        if host in fail:
            return httpx.Response(503, json={"error": "unavailable"})
        builder = payloads.ROUTES.get(host)
        if builder is None:
            return httpx.Response(404)
        return httpx.Response(200, json=builder())

    return httpx.MockTransport(handler)


@pytest.fixture
def mock_client():
    def _make(**kw):
        return httpx.AsyncClient(transport=make_transport(**kw))

    return _make
