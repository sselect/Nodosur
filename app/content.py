"""Contenido de la empresa: única fuente de verdad para la landing, el catálogo Excel y el asistente.

Precios referenciales en CLP, netos (+IVA). Revisar trimestralmente.
"""

COMPANY = {
    "name": "NodoSur",
    "legal_name": "NodoSur SpA (en constitución)",
    "tagline": "Tecnología que no se cae. IA que sí trabaja.",
    "pitch": (
        "Soporte TI nivel 2 y 3, infraestructura cloud, desarrollo web, ERP para pymes y agentes "
        "de IA aplicados a tu operación. Un solo equipo, con SLA claros y precios publicados."
    ),
    "mission": (
        "Dar a pymes y equipos de TI de Chile y LatAm la capacidad técnica de una gran empresa: "
        "sistemas estables, datos ordenados y automatización con IA, sin contratar un área completa."
    ),
    "vision": (
        "Ser al 2030 el partner tecnológico de referencia para 300 empresas de LatAm, combinando "
        "ingenieros senior y agentes de IA que trabajan 24/7."
    ),
    "values": [
        ("Claridad", "Precios publicados, SLA por escrito y reportes que se entienden."),
        ("Responsabilidad", "Si lo instalamos, lo monitoreamos. Si falla, lo resolvemos y explicamos por qué."),
        ("Seguridad primero", "Mínimo privilegio, respaldos probados y datos del cliente que no salen de su control."),
        ("Automatizar con criterio", "Usamos IA donde ahorra tiempo real, con humanos revisando lo que importa."),
    ],
    "location": "Santiago, Chile · servicio remoto en LatAm y España",
    "email": "contacto@nodosur.cl",
    "founder": {
        "name": "Ely Santiago Hernández Díaz",
        "role": "Fundador · Arquitecto de soluciones",
        "bio": (
            "Más de 10 años en TI: 6 años en soporte N1/N2, 4 años en aplicaciones Oracle "
            "(OCI, Oracle Integration Cloud, EBS Inventarios y Fusion Cloud SCM), QA funcional y de integración."
        ),
    },
}

STATS = [
    ("10+", "años en TI"),
    ("N2/N3", "soporte especializado"),
    ("24/7", "agentes de IA monitoreando"),
    ("< 4 h", "respuesta SLA estándar"),
]

PROCESS = [
    ("Diagnóstico gratis", "45 minutos para entender tu operación, riesgos y prioridades."),
    ("Propuesta con precio cerrado", "Alcance, SLA y entregables por escrito en 48 horas."),
    ("Implementación", "Sprints cortos, avances visibles cada semana."),
    ("Operación y mejora continua", "Monitoreo, reportes mensuales y automatización progresiva."),
]

# Cada área agrupa servicios. Campos de servicio:
# code, name, description, deliverables, modality, sla, price_from (CLP neto), unit
AREAS = [
    {
        "key": "ia",
        "name": "IA aplicada",
        "icon": "spark",
        "summary": "Agentes y automatizaciones con modelos de IA que trabajan sobre tus datos y sistemas.",
        "services": [
            {
                "code": "IA-01",
                "name": "Chatbot inteligente para empresas",
                "description": "Atención de clientes, consultas de productos, agendamiento y respuestas automáticas por WhatsApp o sitio web.",
                "deliverables": "Bot entrenado con tu catálogo/FAQ, integración web o WhatsApp Business, derivación a humano, panel de conversaciones",
                "modality": "Remoto",
                "sla": "Monitoreo diario; corrección de respuestas < 24 h",
                "price_from": 690000,
                "unit": "implementación + desde $79.000/mes",
            },
            {
                "code": "IA-02",
                "name": "Automatización de procesos con IA",
                "description": "Automatizar correos, procesamiento de documentos, carga de información, generación de reportes y workflows entre aplicaciones.",
                "deliverables": "Mapa del proceso, flujo automatizado con revisión humana, registro de cada ejecución, manual de operación",
                "modality": "Remoto",
                "sla": "Alertas ante fallas del flujo; soporte hábil < 4 h",
                "price_from": 850000,
                "unit": "por flujo + desde $59.000/mes",
            },
            {
                "code": "IA-03",
                "name": "Agentes de IA para operaciones IT",
                "description": "Agentes que analizan logs, identifican incidentes, consultan APIs, generan tickets y preparan reportes operacionales.",
                "deliverables": "Agente conectado a logs/monitoreo, creación de tickets, resumen diario de incidentes, playbooks",
                "modality": "Remoto",
                "sla": "Operación 24/7; revisión humana de acciones críticas",
                "price_from": 1400000,
                "unit": "piloto 4 semanas + desde $190.000/mes",
            },
            {
                "code": "IA-04",
                "name": "IA integrada con ERP y bases de datos",
                "description": "Asistentes para inventarios, análisis de órdenes, conciliaciones, consultas SQL controladas y detección de anomalías en ERP.",
                "deliverables": "Asistente con acceso de solo lectura, catálogo de consultas aprobadas, alertas de anomalías, auditoría de cada consulta",
                "modality": "Remoto / híbrido",
                "sla": "Soporte hábil < 4 h; revisión mensual de precisión",
                "price_from": 1600000,
                "unit": "piloto + desde $220.000/mes",
            },
        ],
    },
    {
        "key": "soporte",
        "name": "Soporte TI N2 / N3",
        "icon": "lifebuoy",
        "summary": "Mesa de ayuda avanzada y especialistas para incidentes que tu equipo no alcanza a cubrir.",
        "services": [
            {
                "code": "SOP-01",
                "name": "Plan mensual soporte N2",
                "description": "Soporte remoto a usuarios y sistemas: correo, accesos, equipos, redes y aplicaciones de negocio.",
                "deliverables": "Mesa de ayuda con tickets, inventario de equipos, reporte mensual de incidentes",
                "modality": "Remoto + visita programada",
                "sla": "Respuesta < 4 h hábiles",
                "price_from": 390000,
                "unit": "mes (hasta 20 usuarios)",
            },
            {
                "code": "SOP-02",
                "name": "Bolsa de horas N2",
                "description": "Horas prepagadas para incidentes, configuraciones y mejoras puntuales.",
                "deliverables": "Registro de horas y trabajos realizados",
                "modality": "Remoto",
                "sla": "Respuesta < 8 h hábiles",
                "price_from": 350000,
                "unit": "10 horas",
            },
            {
                "code": "SOP-03",
                "name": "Especialista N3",
                "description": "Bases de datos, middleware, integraciones, Oracle EBS/Fusion/OIC y análisis de causa raíz.",
                "deliverables": "Informe técnico de causa raíz y plan de corrección",
                "modality": "Remoto",
                "sla": "Respuesta < 4 h hábiles",
                "price_from": 55000,
                "unit": "hora",
            },
            {
                "code": "SOP-04",
                "name": "Guardia crítica 24/7",
                "description": "Cobertura fuera de horario para sistemas críticos, con escalamiento y bitácora.",
                "deliverables": "Runbooks, monitoreo y bitácora de guardia",
                "modality": "Remoto",
                "sla": "Respuesta < 1 h, 24/7",
                "price_from": 1200000,
                "unit": "mes",
            },
        ],
    },
    {
        "key": "infra",
        "name": "Infraestructura & Cloud",
        "icon": "cloud",
        "summary": "Nube, redes, respaldos y seguridad bien configurados desde el día uno.",
        "services": [
            {
                "code": "INF-01",
                "name": "Migración a la nube",
                "description": "Migración de servidores y aplicaciones a OCI, AWS o Azure con plan de reversa.",
                "deliverables": "Arquitectura objetivo, migración, pruebas y documentación",
                "modality": "Remoto",
                "sla": "Ventana acordada, sin pérdida de datos",
                "price_from": 1200000,
                "unit": "proyecto",
            },
            {
                "code": "INF-02",
                "name": "Administración cloud mensual",
                "description": "Monitoreo, parches, control de costos y respaldos de tu infraestructura.",
                "deliverables": "Dashboard de salud, reporte mensual de costos y riesgos",
                "modality": "Remoto",
                "sla": "Alertas 24/7, respuesta < 4 h",
                "price_from": 290000,
                "unit": "mes",
            },
            {
                "code": "INF-03",
                "name": "Auditoría de seguridad cloud (IAM)",
                "description": "Revisión de usuarios, grupos, políticas y configuración contra buenas prácticas.",
                "deliverables": "Informe de hallazgos priorizados y plan de remediación",
                "modality": "Remoto",
                "sla": "Entrega en 10 días hábiles",
                "price_from": 650000,
                "unit": "proyecto",
            },
            {
                "code": "INF-04",
                "name": "Respaldo y recuperación (DR)",
                "description": "Respaldos automáticos, pruebas de restauración y plan de continuidad.",
                "deliverables": "Política de respaldo, prueba de restauración trimestral",
                "modality": "Remoto",
                "sla": "RPO/RTO acordados por escrito",
                "price_from": 180000,
                "unit": "mes",
            },
        ],
    },
    {
        "key": "web",
        "name": "Web & Diseño",
        "icon": "layout",
        "summary": "Sitios rápidos, seguros y pensados para vender, con identidad visual consistente.",
        "services": [
            {
                "code": "WEB-01",
                "name": "Landing page profesional",
                "description": "Página de una sección orientada a conversión, con formulario y analítica.",
                "deliverables": "Diseño, desarrollo, dominio conectado y SEO básico",
                "modality": "Remoto",
                "sla": "Entrega en 10 días hábiles",
                "price_from": 290000,
                "unit": "proyecto",
            },
            {
                "code": "WEB-02",
                "name": "Sitio corporativo",
                "description": "Sitio de 5 a 8 secciones con administrador de contenidos.",
                "deliverables": "Diseño a medida, CMS, capacitación y SEO técnico",
                "modality": "Remoto",
                "sla": "Entrega en 3-4 semanas",
                "price_from": 650000,
                "unit": "proyecto",
            },
            {
                "code": "WEB-03",
                "name": "Tienda online",
                "description": "E-commerce con pasarela de pago, inventario y despacho.",
                "deliverables": "Tienda configurada, medios de pago y capacitación",
                "modality": "Remoto",
                "sla": "Entrega en 4-6 semanas",
                "price_from": 990000,
                "unit": "proyecto",
            },
            {
                "code": "WEB-04",
                "name": "Identidad visual",
                "description": "Logo, paleta, tipografías y manual básico de marca.",
                "deliverables": "Logo en todos los formatos y manual de marca",
                "modality": "Remoto",
                "sla": "Entrega en 2 semanas",
                "price_from": 220000,
                "unit": "proyecto",
            },
            {
                "code": "WEB-05",
                "name": "Mantención y hosting",
                "description": "Actualizaciones, respaldos, certificados y cambios menores.",
                "deliverables": "Sitio actualizado y monitoreado",
                "modality": "Remoto",
                "sla": "Cambios menores < 48 h",
                "price_from": 35000,
                "unit": "mes",
            },
        ],
    },
    {
        "key": "software",
        "name": "Software & DevOps",
        "icon": "code",
        "summary": "Arquitectura, integraciones y desarrollo a medida con calidad de producción.",
        "services": [
            {
                "code": "SW-01",
                "name": "Arquitectura de soluciones",
                "description": "Diagnóstico técnico y diseño de arquitectura antes de invertir en desarrollo.",
                "deliverables": "Documento de arquitectura, diagramas y estimación",
                "modality": "Remoto",
                "sla": "Entrega en 5-10 días hábiles",
                "price_from": 450000,
                "unit": "proyecto",
            },
            {
                "code": "SW-02",
                "name": "Integraciones y APIs",
                "description": "Conectar sistemas (ERP, CRM, e-commerce, bancos) vía API, OIC o middleware.",
                "deliverables": "Integración documentada, monitoreo y manejo de errores",
                "modality": "Remoto",
                "sla": "Según alcance",
                "price_from": 600000,
                "unit": "proyecto",
            },
            {
                "code": "SW-03",
                "name": "Aplicación web a medida (MVP)",
                "description": "Producto mínimo viable con backend, frontend y despliegue en la nube.",
                "deliverables": "Código fuente, CI/CD, pruebas automatizadas y documentación",
                "modality": "Remoto",
                "sla": "Sprints de 2 semanas",
                "price_from": 2500000,
                "unit": "proyecto",
            },
            {
                "code": "SW-04",
                "name": "DevOps & QA automatizado",
                "description": "Pipelines CI/CD, contenedores, infraestructura como código y pruebas automatizadas.",
                "deliverables": "Pipeline funcionando, pruebas y guía de operación",
                "modality": "Remoto",
                "sla": "Entrega en 2-3 semanas",
                "price_from": 550000,
                "unit": "proyecto",
            },
        ],
    },
    {
        "key": "erp",
        "name": "ERP & Oracle",
        "icon": "boxes",
        "summary": "NodoSur ERP para pymes y consultoría Oracle para empresas grandes.",
        "services": [
            {
                "code": "ERP-01",
                "name": "NodoSur ERP · Plan Emprende",
                "description": "Inventario, ventas y clientes en la nube para 1 a 3 usuarios.",
                "deliverables": "Acceso web, respaldos diarios y soporte por correo",
                "modality": "Nube (SaaS)",
                "sla": "Disponibilidad 99,5%",
                "price_from": 29990,
                "unit": "mes",
            },
            {
                "code": "ERP-02",
                "name": "NodoSur ERP · Plan Pyme",
                "description": "Hasta 10 usuarios: inventario multibodega, compras, ventas y reportes.",
                "deliverables": "Acceso web, reportes, soporte prioritario",
                "modality": "Nube (SaaS)",
                "sla": "Disponibilidad 99,5%, soporte < 4 h",
                "price_from": 69990,
                "unit": "mes",
            },
            {
                "code": "ERP-03",
                "name": "Implementación y migración de datos",
                "description": "Carga de productos, clientes y saldos iniciales; capacitación del equipo.",
                "deliverables": "Datos migrados y validados, capacitación",
                "modality": "Remoto / presencial",
                "sla": "Entrega en 2-3 semanas",
                "price_from": 350000,
                "unit": "proyecto",
            },
            {
                "code": "ERP-04",
                "name": "Consultoría Oracle EBS / Fusion",
                "description": "QA funcional y de integración, inventarios/SCM, OIC y OCI para empresas grandes.",
                "deliverables": "Casos de prueba, evidencias, configuración y documentación",
                "modality": "Remoto / híbrido",
                "sla": "Según contrato",
                "price_from": 60000,
                "unit": "hora",
            },
        ],
    },
]

FAQ = [
    (
        "¿Los precios incluyen IVA?",
        "No. Todos los precios publicados son netos, en pesos chilenos, y referenciales: la propuesta final se cierra después del diagnóstico.",
    ),
    (
        "¿Atienden fuera de Santiago?",
        "Sí. Casi todo el servicio es remoto para Chile, LatAm y España. Las visitas presenciales se coordinan en Santiago.",
    ),
    (
        "¿Qué pasa con mis datos cuando usan IA?",
        "Los agentes trabajan con acceso de solo lectura y mínimo privilegio, registran cada acción y no usamos tus datos para entrenar modelos. Las acciones sensibles requieren aprobación humana.",
    ),
    (
        "¿Cuánto cuesta usar los modelos de IA?",
        "Depende del volumen. Para un chatbot de pyme el consumo de modelo suele ser bajo; lo estimamos en la propuesta y lo mostramos mes a mes en tu reporte.",
    ),
    (
        "¿Hay permanencia mínima?",
        "Los planes mensuales no tienen permanencia: se pueden cancelar con 30 días de aviso.",
    ),
]


def all_services() -> list[dict]:
    rows = []
    for area in AREAS:
        for svc in area["services"]:
            rows.append({**svc, "area": area["name"], "area_key": area["key"]})
    return rows


def format_clp(value: int) -> str:
    return "$" + f"{value:,.0f}".replace(",", ".")
