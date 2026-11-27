# IA-04 · IA integrada con ERP y bases de datos

**Promesa al cliente:** asistentes para inventarios, análisis de órdenes, conciliaciones, consultas
SQL controladas y detección de anomalías en ERP.
**Precio catálogo:** piloto desde $1.600.000 + desde $220.000/mes.
**Ventaja de NodoSur:** experiencia real en Oracle EBS Inventarios y Fusion Cloud SCM (tablas INV/RCV/CST, OTBI/BIP).

## Capacidades

1. **Preguntas en lenguaje natural → SQL controlado**: "¿qué SKUs quedan sin stock esta semana en la bodega central?"
2. **Análisis de órdenes**: atrasos, órdenes abiertas por proveedor, tiempos de ciclo.
3. **Conciliaciones**: inventario físico vs sistema, recepciones vs facturas, con diferencias explicadas.
4. **Anomalías**: ajustes de inventario inusuales, costos fuera de rango, movimientos fuera de horario.

## Arquitectura (seguridad primero)

- Conexión con **usuario de BD de solo lectura** y acceso solo a vistas aprobadas, nunca a tablas base completas.
- **Capa semántica**: catálogo de vistas con descripción de columnas y joins válidos (YAML versionado). El modelo ve el catálogo, no la BD entera.
- Generación: **Sonnet 5.5** escribe el SQL. Antes de ejecutarlo, un validador en código lo parsea (sqlglot) y rechaza todo lo que no sea `SELECT` sobre vistas permitidas. También agrega `LIMIT` y un timeout.
- Consultas frecuentes como **plantillas aprobadas** con parámetros (más rápido y 100 % predecible).
- Respuesta: tabla + explicación corta + el SQL usado (transparencia), con exportación a Excel.
- Anomalías: reglas estadísticas en código (z-score, IQR) en un job nocturno; el modelo solo redacta la explicación con Haiku 5.5.

## Guardrails

- Cero escritura en el ERP. Si el usuario pide un ajuste, se genera un borrador para el proceso normal del ERP (por ejemplo, una carga FBDI revisada por una persona).
- Filtros por rol: cada usuario ve solo sus bodegas u organizaciones (se aplican en la vista, no en el prompt).
- Bitácora de cada pregunta, SQL, filas devueltas y usuario.

## Criterios de aceptación

1. Set de 40 preguntas de negocio con resultado esperado: ≥ 90 % exactas.
2. `DELETE`, `UPDATE`, `DROP`, múltiples sentencias o tablas fuera del catálogo → rechazadas antes de llegar a la BD (test obligatorio).
3. Toda consulta tiene `LIMIT` y timeout; una consulta pesada no bloquea la BD.
4. Un usuario con rol "bodega norte" no puede ver datos de "bodega central", aunque lo pida explícitamente.
5. La conciliación de un mes de prueba cuadra al peso con el cálculo manual.

## Encaje con NodoSur ERP

El mismo asistente viene integrado en NodoSur ERP (plan Pyme) sobre su propio esquema: es la
demostración más barata de construir y sirve de entrada a clientes con Oracle u otro ERP.
