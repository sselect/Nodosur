"""Autenticación del panel admin y utilidades de seguridad."""

import hmac
import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, Request, status

from app.config import Settings, get_settings

SESSION_KEY = "admin"


class RateLimiter:
    """Límite simple en memoria: máx `limit` eventos por `window` segundos por clave."""

    def __init__(self, limit: int, window: float) -> None:
        self.limit = limit
        self.window = window
        self._hits: dict[str, deque] = defaultdict(deque)

    def hit(self, key: str) -> bool:
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            return False
        hits.append(now)
        return True

    def reset(self) -> None:
        self._hits.clear()


login_limiter = RateLimiter(limit=5, window=600)
contact_limiter = RateLimiter(limit=5, window=3600)


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_credentials(email: str, password: str, settings: Settings) -> bool:
    ok_email = hmac.compare_digest(email.strip().lower(), settings.admin_email.strip().lower())
    ok_pass = hmac.compare_digest(password, settings.admin_password)
    return ok_email and ok_pass


def is_admin(request: Request) -> bool:
    return bool(request.session.get(SESSION_KEY))


def require_admin(request: Request) -> None:
    if not is_admin(request):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado")


def require_admin_write(request: Request) -> None:
    """Escritura desde el panel: sesión + cabecera propia (bloquea CSRF de formularios externos)."""
    require_admin(request)
    if request.headers.get("x-nodosur") != "1":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Falta cabecera X-NodoSur")


def require_agent_token(request: Request, settings: Settings = Depends(get_settings)) -> None:
    auth = request.headers.get("authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if not token or not hmac.compare_digest(token, settings.agent_token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
