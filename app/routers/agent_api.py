"""Disparador externo del agente (GitHub Actions cron / Render cron / curl)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agent.runner import run_agent
from app.db import get_db
from app.security import require_agent_token

router = APIRouter(prefix="/api/agent", dependencies=[Depends(require_agent_token)])


@router.post("/run")
async def trigger_run(force: bool = False, db: Session = Depends(get_db)):
    """Ejecuta el agente si corresponde según el intervalo configurado (o siempre con force=true)."""
    run = await run_agent(db, trigger="cron", force=force)
    return run.to_dict()
