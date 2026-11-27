"""Punto de entrada de la aplicación NodoSur."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.db import init_db
from app.routers import admin, agent_api, public

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("nodosur")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.validate_for_prod()
    init_db()
    stop = asyncio.Event()
    task = None
    if settings.enable_scheduler:
        from app.agent.runner import scheduler_loop

        task = asyncio.create_task(scheduler_loop(stop))
        log.info("Planificador interno del agente activo")
    yield
    stop.set()
    if task:
        await task


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="NodoSur API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None if settings.is_prod else "/docs",
        redoc_url=None,
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="nodosur_session",
        max_age=60 * 60 * 12,
        same_site="lax",
        https_only=settings.is_prod,
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if settings.is_prod:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(public.router)
    app.include_router(agent_api.router)
    app.include_router(admin.router)
    app.include_router(admin.api)
    return app


app = create_app()
