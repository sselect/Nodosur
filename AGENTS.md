# AGENTS.md · NodoSur

Instrucciones compartidas para los agentes de código que trabajan en este repo (Codex lee este archivo;
Claude Code lo importa desde `CLAUDE.md`). Idioma del código: inglés en nombres técnicos, español en
textos de la interfaz, comentarios y documentación.

## Qué es este repo

Sitio y plataforma de NodoSur (empresa de servicios TI en Chile):
- **Landing** (`/`): servicios, precios, catálogo Excel descargable, chatbot "Nodo", formulario de leads.
- **Panel admin** (`/admin`): motor de búsqueda de empleo TI con agente 24/7, dashboard en vivo (SSE), leads.
- **API del agente** (`POST /api/agent/run`, con token): la dispara GitHub Actions cada 30 min.

Stack: Python 3.12 · FastAPI · SQLAlchemy 2 · Postgres (prod) / SQLite (dev, tests) · Jinja2 · JS vanilla · Chart.js (vendorizado) · Render.

## Equipo y roles

| Rol | Quién | Responsable de |
|---|---|---|
| Product Owner / CEO | Ely | Prioridades, aprobar PRs, hablar con clientes |
| Arquitecto, DevOps y QA | Claude (Claude Code) | Specs, CI/CD, infraestructura, tests, revisión de PRs, deploy |
| Desarrollador fullstack | Codex | Implementar features y agentes según las specs en `docs/` |

Flujo detallado en `docs/equipo-ia.md`.

## Comandos

```bash
pip install -r requirements-dev.txt      # dependencias
uvicorn app.main:app --reload            # app en http://localhost:8000 (admin: admin@nodosur.cl / admin en dev)
pytest                                   # tests (SQLite)
TEST_DATABASE_URL=postgresql://... pytest  # tests contra Postgres
ruff check . && ruff format --check .    # lint y formato
python scripts/build_catalog.py          # regenerar el Excel si cambias app/content.py
```

## Mapa del código

- `app/content.py`: **única fuente de verdad** de empresa, servicios y precios (landing, Excel y chatbot leen de aquí).
- `app/agent/sources/`: una clase por portal (solo APIs públicas oficiales; `parse()` puro + `fetch()`).
- `app/agent/runner.py`: orquestación (buscar → filtrar → puntuar → deduplicar → guardar → notificar → eventos).
- `app/agent/scoring.py`: puntaje 0-100 explicable.
- `app/routers/`: `public.py` (landing, contacto, asistente), `admin.py` (panel + API + SSE), `agent_api.py`.
- `app/ai/assistant.py`: chatbot Nodo (Claude Haiku 5.5 con modo básico de respaldo).
- `tests/`: pytest; `tests/payloads.py` simula las APIs con su formato real.
- `docs/agentes/`: specs de los agentes IA que vendemos (IA-01 a IA-04).

## Reglas de implementación

1. Todo cambio de comportamiento trae su test. CI exige cobertura ≥ 80 % y tests verdes en SQLite y Postgres.
2. Nada de scraping HTML ni de saltarse términos de uso: solo APIs públicas/oficiales, respetando su
   frecuencia (`min_interval_minutes`) y la atribución (enlace al aviso original).
3. Secretos solo por variables de entorno. Nunca en código, tests, logs ni commits.
4. Escrituras del panel: siempre con `require_admin_write` (sesión + cabecera `X-NodoSur`).
5. Textos de la UI en español de Chile, cortos. Respetar `DESIGN.md` (tokens en `app/static/css/tokens.css`; nada de colores sueltos).
6. Precios y servicios solo en `app/content.py`; luego `python scripts/build_catalog.py`.
7. Commits pequeños en español imperativo ("Agrega fuente X"). Ramas: `feat/…`, `fix/…`, `chore/…`. PR siempre a `main`.

## Reglas de revisión (code review)

Marca como bloqueante en un PR:
- Endpoints de escritura del admin sin `require_admin_write`, o endpoints nuevos sin autenticación que expongan datos.
- Secretos, tokens o datos personales en código, fixtures o logs.
- Fuentes de empleo que hagan scraping de HTML, ignoren límites de frecuencia o no guarden la URL original.
- Consultas SQL armadas con concatenación de strings (usar SQLAlchemy).
- HTML construido en JS sin escapar datos externos (usar `esc()` en `admin.js` o `textContent`).
- Agentes IA que ejecuten acciones de escritura sin paso de aprobación humana, o que usen credenciales con más permisos de los necesarios.
- Cambios de precios fuera de `app/content.py`, o Excel desactualizado (el test `test_catalogo_excel_descargable_y_completo` lo detecta).
