# Operación de NodoSur (runbook)

## Variables de entorno (Render → servicio `nodosur` → Environment)

| Variable | Obligatoria | Para qué |
|---|---|---|
| `ENV` | sí | `prod` (activa cookies seguras, HSTS y rechaza secretos débiles) |
| `DATABASE_URL` | sí | Postgres de Render (`nodosur-db`) |
| `SECRET_KEY` | sí | Firma de la sesión del admin (≥ 12 caracteres, aleatoria) |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | sí | Login de `/admin` |
| `AGENT_TOKEN` | sí | Token del disparador del agente (mismo valor en el secret de GitHub) |
| `PUBLIC_BASE_URL` | no | Dominio propio (enlaces en correos, sitemap, Open Graph). Si falta, se usa `RENDER_EXTERNAL_URL`, que Render define solo |
| `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASSWORD` | para correos | Gmail: `smtp.gmail.com`, `587`, tu Gmail y una **contraseña de aplicación** |
| `NOTIFY_TO` / `CONTACT_TO` | para correos | Destino de alertas de empleo y de leads |
| `ANTHROPIC_API_KEY` | opcional | Activa el chatbot Nodo con IA (sin clave usa el modo básico) |
| `ENABLE_SCHEDULER` | no | `true` solo en un plan siempre encendido |

Generar valores seguros: `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

## Agente 24/7

- GitHub → repo → Settings → Secrets and variables → Actions → crear `NODOSUR_URL` (por ejemplo `https://nodosur.onrender.com`) y `AGENT_TOKEN`.
- El workflow "Agente de empleos 24/7" corre cada 30 min. También se puede lanzar a mano (Actions → Run workflow → force).
- La frecuencia real la define el panel (Agente → "Cada (minutos)"). Cada fuente respeta además su propio límite (Remotive: 1 vez cada 6 h).
- GitHub pausa los workflows programados de repos sin actividad por 60 días. Si pasa, reactívalo en la pestaña Actions.

## Plan Free de Render: límites a vigilar

- El servicio se duerme tras 15 min sin tráfico y tarda alrededor de 1 minuto en despertar. El cron de GitHub lo despierta.
- **La base Postgres Free vence 30 días después de creada** (hay 14 días de gracia para subirla a un plan pago antes de que se borren los datos). Antes de esa fecha: Render → `nodosur-db` → Upgrade.
- Respaldo manual: `pg_dump "$DATABASE_URL" > backup-$(date +%F).sql` (la URL externa está en Render → `nodosur-db` → Connect).

## Despliegue y reversa

- Deploy: merge a `main` → Render construye y despliega (auto-deploy).
- Verificación: `curl -fsS https://<url>/healthz` y revisar la landing y `/admin`.
- Reversa: Render → `nodosur` → Events → elegir el deploy anterior → "Rollback".

## Incidentes frecuentes

| Síntoma | Causa probable | Acción |
|---|---|---|
| Panel sin ofertas nuevas | Faltan los secrets de GitHub o el agente está pausado | Revisar Actions y la pestaña Agente |
| Una fuente en `error` | API caída o cambió su formato | Ver `last_error` en "Estado de fuentes"; si cambió el formato, actualizar `parse()` y su payload de test |
| No llegan correos | SMTP sin configurar o contraseña de aplicación inválida | Revisar las variables `SMTP_*` y los logs de Render |
| Error 500 al arrancar en prod | Secretos débiles o por defecto | Definir `SECRET_KEY`, `ADMIN_PASSWORD` y `AGENT_TOKEN` fuertes |
