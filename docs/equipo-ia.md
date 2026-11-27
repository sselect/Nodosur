# Equipo IA de NodoSur: Claude + Codex trabajando juntos

## Roles

| Rol | Quién | Herramienta | Entrega |
|---|---|---|---|
| CEO / Product Owner | Ely | GitHub, panel admin | Prioridades, aprobación de PRs, relación con clientes |
| Arquitecto + DevOps + QA | Claude | Claude Code | Specs, tests de aceptación, CI/CD, infraestructura, revisión, deploy |
| Desarrollador fullstack | Codex | Codex CLI / Codex en GitHub | Implementación de features y agentes según specs |

Los dos agentes leen las mismas reglas: `AGENTS.md` (Codex lo lee directo; `CLAUDE.md` lo importa).

## Instalación (una vez, en tu computador)

Requisitos: Node.js 18.18+, Git, Python 3.12, cuenta de Claude (Claude Code) y cuenta de ChatGPT/OpenAI (Codex).

```bash
# 1. Clonar el repo
git clone git@github.com:sselect/Nodosur.git && cd Nodosur

# 2. Instalar Claude Code y Codex CLI
curl -fsSL https://claude.ai/install.sh | bash
npm install -g @openai/codex
codex login                    # inicia sesión con tu cuenta de ChatGPT u OpenAI

# 3. Conectar Codex dentro de Claude Code (plugin oficial de OpenAI)
claude
> /plugin marketplace add openai/codex-plugin-cc
> /plugin install codex@openai-codex
> /reload-plugins
> /codex:setup
```

El plugin usa tu Codex CLI local, así que el uso de Codex cuenta contra los límites de tu plan de OpenAI.
Desde ahí, Claude puede pedirle a Codex que implemente una tarea o que revise código, sin salir de la sesión.

Opcional: activa **Codex Code Review** en GitHub para este repo. Revisa cada PR usando las
"Reglas de revisión" de `AGENTS.md`, como segunda opinión además de la revisión de Claude.

## Flujo de trabajo (de idea a producción)

```
Ely: "quiero X"  →  Claude: spec + tests de aceptación (docs/ + tests/)
                 →  Codex: implementa en rama feat/x, abre PR
                 →  CI (lint, tests SQLite + Postgres, build Docker)
                 →  Claude: revisión + pruebas + (opcional) Codex Code Review
                 →  Ely: aprueba  →  merge a main  →  Render despliega  →  Claude verifica en PRD
```

### Reglas del flujo

1. **Una tarea = una rama = un PR.** Ninguno de los dos agentes hace push directo a `main`.
2. **La spec manda.** Si Codex encuentra un hueco en la spec, lo anota en el PR en vez de inventar.
3. **Tests primero.** Claude deja los tests de aceptación; Codex no los borra ni los relaja para que pasen.
4. **Handoff por escrito.** Cada PR describe: qué cambió, cómo probarlo y qué quedó pendiente.
5. **Sin secretos en prompts.** Claves y contraseñas viven en Render o en los secrets de GitHub.
6. **Ely aprueba el merge** de todo lo que toque precios, datos de clientes o acciones automáticas.

### Prompts de ejemplo

En Claude Code:
- "Escribe la spec y los tests de aceptación para el agente IA-03 en `docs/agentes/` y `tests/`, y delega la implementación a Codex."
- "Revisa el PR #12 de Codex contra AGENTS.md, corre la suite y dime si se puede mergear."

En Codex:
- "Implementa `docs/agentes/ia-02-automatizacion.md` (fase 1) en `solutions/ia02/`. Los tests de `tests/solutions/test_ia02.py` deben pasar. Abre PR."

## Primer backlog sugerido

| # | Tarea | Spec | Dueño |
|---|---|---|---|
| 1 | Chatbot IA-01 empaquetado para clientes (widget + WhatsApp) | `docs/agentes/ia-01-chatbot.md` | Codex implementa, Claude prueba |
| 2 | Agente de operaciones IT (demo con logs de ejemplo) | `docs/agentes/ia-03-ops-it.md` | Codex |
| 3 | Asistente ERP con SQL de solo lectura (demo sobre BD de ejemplo) | `docs/agentes/ia-04-erp-datos.md` | Codex |
| 4 | Migraciones con Alembic antes de cambiar el esquema en PRD | — | Claude |
| 5 | Dominio propio nodosur.cl + correo corporativo | `docs/operacion.md` | Ely + Claude |
