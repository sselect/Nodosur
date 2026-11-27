# IA-03 · Agentes de IA para operaciones IT

**Promesa al cliente:** agentes que analizan logs, identifican incidentes, consultan APIs, generan
tickets y preparan reportes operacionales.
**Precio catálogo:** piloto 4 semanas desde $1.400.000 + desde $190.000/mes.
**Por qué lo vendemos bien:** es el día a día de soporte N2/N3 y de OCI/OIC que Ely ya domina.

## Flujo

1. **Detectar**: alertas de monitoreo (OCI Monitoring, CloudWatch, Grafana, Uptime) o reglas sobre logs.
2. **Recolectar**: el agente trae logs de la ventana del incidente, métricas, despliegues recientes y estado de dependencias.
3. **Diagnosticar**: **Sonnet 5.5** correlaciona y propone causa probable con evidencia (líneas de log citadas). Haiku 5.5 resume y deduplica el ruido antes.
4. **Actuar**: crea o actualiza el ticket (Jira, ServiceNow, GLPI, Autotask) con resumen, severidad y pasos sugeridos; avisa a la guardia.
5. **Remediar (opcional)**: runbooks predefinidos, como reiniciar un pool o escalar instancias, **solo con aprobación humana**.
6. **Reportar**: resumen diario y semanal (incidentes, MTTA/MTTR, causas repetidas).

## Herramientas

| Tool | Permiso | Aprobación |
|---|---|---|
| `buscar_logs(servicio, desde, hasta, filtro)` | read | no |
| `metricas(servicio, metrica, ventana)` | read | no |
| `despliegues_recientes(servicio)` | read | no |
| `crear_ticket(titulo, severidad, resumen, evidencia)` | write | no (solo crea) |
| `notificar_guardia(canal, mensaje)` | write | no |
| `ejecutar_runbook(nombre, parametros)` | write | **sí, siempre** |

## Guardrails

- Las líneas de log son datos: un log que diga "ejecuta X" no se obedece.
- Enmascarar secretos antes de enviar logs al modelo (tokens, contraseñas, connection strings).
- Presupuesto de tokens por incidente; si se supera, se resume primero con Haiku.
- Runbooks en lista blanca, con parámetros validados y botón de deshacer documentado.

## Criterios de aceptación

1. Con 20 incidentes históricos del cliente: causa correcta en el top-1 en ≥ 70 % y en el top-3 en ≥ 90 %.
2. Cada ticket incluye al menos 2 evidencias citadas (línea de log o métrica) y un enlace a la fuente.
3. `ejecutar_runbook` sin aprobación → bloqueado y registrado (test obligatorio).
4. Un log con un secreto llega al modelo enmascarado (test con secretos sembrados).
5. Del aviso al ticket creado: < 2 minutos (MTTA).

## Demo para vender (Codex)

`solutions/ia03/demo/`: logs sintéticos de una API de pagos con un pool de BD agotado (el mismo
caso que muestra la consola de la landing), monitoreo simulado y tickets en un tablero local. Sirve
para mostrarle a un cliente su propio caso en 15 minutos.
