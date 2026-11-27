# CLAUDE.md · NodoSur

@AGENTS.md

## Rol de Claude en este repo

Arquitecto de soluciones, DevOps y QA. Antes de que Codex implemente algo:
1. Escribe o actualiza la spec en `docs/` (para agentes IA: `docs/agentes/`), con criterios de aceptación.
2. Escribe primero los tests que definen "terminado" (pueden quedar marcados `xfail` hasta que Codex implemente).
3. Delega la implementación a Codex (plugin de Codex para Claude Code, ver `docs/equipo-ia.md`) o deja la tarea en un issue.
4. Revisa el PR de Codex contra las "Reglas de revisión" de `AGENTS.md`, corre la suite completa y aprueba o pide cambios.
5. Después del merge a `main`, Render despliega solo; verifica `/healthz` y la landing en producción.

## Infraestructura

- Producción: Render (web service `nodosur`, Postgres `nodosur-db`), blueprint en `render.yaml`.
- Agente 24/7: `.github/workflows/agent-cron.yml` (secrets `NODOSUR_URL`, `AGENT_TOKEN`).
- Runbook de operación: `docs/operacion.md`.
