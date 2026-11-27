# NodoSur

**Tecnología que no se cae. IA que sí trabaja.** Sitio y plataforma de NodoSur, empresa chilena de
soporte TI N2/N3, infraestructura cloud, web, ERP para pymes e IA aplicada.

| Pieza | Ruta | Qué hace |
|---|---|---|
| Landing | `/` | Servicios y precios, escenas con scroll, catálogo Excel, chatbot "Nodo", formulario de leads |
| Catálogo | `/descargas/catalogo-servicios-nodosur.xlsx` | 25 servicios en 6 áreas, IVA calculado y cotizador |
| Panel admin | `/admin` | Motor de búsqueda de empleo TI: dashboard en vivo, ofertas, configuración del agente y leads |
| Agente 24/7 | `POST /api/agent/run` | Busca en 6 portales con API pública, puntúa, deduplica, guarda y avisa por correo |

## Arquitectura

```
GitHub Actions (cada 30 min) ──POST /api/agent/run──▶ ┌──────────────── Render ────────────────┐
                                                      │ FastAPI (web service)                  │
Visitantes ──▶ Landing / chatbot / contacto ─────────▶│  ├─ agente: fuentes → puntaje → BD     │──▶ Postgres
Ely ──▶ /admin (sesión) ◀── SSE en vivo ──────────────│  ├─ panel admin + API + SSE            │
                                                      │  └─ correo SMTP (alertas y leads)      │──▶ Gmail
                                                      └────────────────────────────────────────┘
Fuentes (APIs públicas): Get on Board · Remotive · Remote OK · Arbeitnow · Himalayas · Jobicy
```

## Desarrollo local

```bash
pip install -r requirements-dev.txt
cp .env.example .env                 # en dev puedes dejar los valores por defecto
uvicorn app.main:app --reload        # http://localhost:8000  ·  admin: admin@nodosur.cl / admin
pytest                               # 50 tests, cobertura ≥ 80 %
docker compose up --build            # app + Postgres, con el planificador interno activo
```

## Despliegue

- `main` → Render despliega automáticamente (`render.yaml`). CI: lint, tests en SQLite y Postgres, build Docker y smoke test.
- Secrets del repo para el agente 24/7: `NODOSUR_URL` y `AGENT_TOKEN` (el mismo valor que en Render).
- Operación, variables y runbook: [`docs/operacion.md`](docs/operacion.md).

## Equipo

Trabajan juntos Claude (arquitectura, DevOps, QA) y Codex (desarrollo), con reglas compartidas en
[`AGENTS.md`](AGENTS.md) y el flujo en [`docs/equipo-ia.md`](docs/equipo-ia.md). Specs de los agentes IA
que vendemos: [`docs/agentes/`](docs/agentes/). Diseño: [`DESIGN.md`](DESIGN.md).
