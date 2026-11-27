# DESIGN.md · NodoSur

Dirección: **"producto en escena"**. Página negra de punta a punta, titulares blancos grandes y
cortos, y la tecnología (red de nodos, consola del agente, ERP, chat) presentada como un producto
premium que se revela con el scroll. Patrón tomado de la página de producto de OBSBOT Meet 4K que
entregó Ely (medido en 1440 px): fondo negro, titulares centrados de 2 a 6 palabras, secciones
fijadas de 100vh, bento de tarjetas, comparador antes/después y revelado del producto con scroll.
**Se toma el patrón, nunca marca, imágenes, textos ni código.** Todo lo que se ve es nuestro.

## Color (tokens en `app/static/css/tokens.css`) · un solo tema, oscuro

| Token | Valor | Rol |
|---|---|---|
| `--bg` | `#000000` | Fondo de página |
| `--surface` / `--surface-2` | `#0c0f0e` / `#151a18` | Tarjetas, formularios, inputs |
| `--line` | `#232a27` | Bordes y divisores |
| `--text` | `#ffffff` | Titulares y texto principal (21:1) |
| `--text-muted` | `#a3aca8` | Texto secundario (9:1 sobre negro) |
| `--text-faint` | `#848e89` | Textos chicos, notas y pasos inactivos (6,2:1, cumple AA) |
| `--signal` | `#c8f25c` | **Primario**: CTA, "en vivo", foco, borde de luz. Texto encima: negro (16:1) |
| `--signal-strong` / `--signal-glow` | `#dafa86` / lima al 14 % | Hover del primario / halo de foco y nodos activos |
| `--teal` | `#3ccb9f` | Acento secundario: links, datos, gráficos |
| `--ok` / `--warn` / `--error` | `#4ade80` / `#fbbf24` / `#f87171` | Estados en consolas y mockups |
| `--paper` / `--paper-ink` | `#f4f6f2` / `#0a0f0d` | Solo dentro del mockup claro del ERP |

Reglas: nada de colores sueltos en CSS (todo por token). Para atenuar algo inactivo se cambia el
**color** a `--text-faint`, nunca la opacidad del texto (la opacidad rompe el contraste AA).

## Tipografía

- **Montserrat** variable (títulos 700, texto 400/500, botones 600) e **IBM Plex Mono 500** para
  etiquetas, códigos de servicio y consolas. Alojadas en `app/static/vendor/fonts/` (OFL), con
  `preload` de Montserrat; sin Google Fonts.
- Escala medida en la referencia: H1/H2 `clamp(1.875rem, 3.9vw, 3.5rem)` (56 px a 1440) · H3
  `clamp(1.75rem, 3.4vw, 3rem)` · cuerpo 16 px con interlínea 1.875 · títulos interlínea 1.21.
- Titulares de 2 a 6 palabras con `text-wrap: balance`; centrados en escenas, a la izquierda en contenido.

## Espaciado, forma y profundidad

- Escala de 4 px: 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 160. Contenido máx. 1200 px.
- Barra global de 60 px que se va con el scroll + sub-nav fija de 52 px (marca, anclas, CTA píldora).
- Radio: 8 px inputs · 16 px tarjetas · píldora en botones y chips.
- Sin sombras grises: la profundidad sale de bordes `--line`, halos lima y degradados radiales.

## Escenas de la landing (`landing.html` + `landing.css`)

| # | Escena | Alto | Qué pasa con el scroll |
|---|---|---|---|
| 1 | Hero `.hero` | 360vh | La **red de nodos** (canvas, esfera de Fibonacci con borde de luz) emerge y gira; el texto sube y se va; la consola del agente entra en 3D y sus líneas se encienden |
| 2 | Bento `.features` | normal | 6 tarjetas con micro-animaciones (anillo SLA, precios, orbes IA, escaneo de seguridad) |
| 3 | Señales `.signals` | 320vh | Matriz de puntos: los focos pasan de alerta a lima; zoom 0,85 → 1,09 |
| 4 | Áreas `#servicios` | 6 × 100vh | Carrusel horizontal fijado, una área por pantalla, con puntos y contador |
| 5 | Antes/después `#comparar` | 230vh | Comparador que se corre de 85 % a 50 %: tickets apilados vs. panel sano |
| 6 | IA `#ia` | 400vh | Pasos que se activan y un pipeline de nodos que se ilumina |
| 7 | ERP `#erp` | 320vh | Ventana de app que cambia de vista (inventario, ventas, consulta IA) |
| 8+ | Planes, proceso, nosotros, FAQ, contacto | normal | Apariciones fade-up |

## Movimiento (`app/static/js/landing.js`)

- Librerías vendorizadas (ver `vendor/LICENSES.md`): **GSAP 3.15 + ScrollTrigger + SplitText**,
  **Lenis 1.3** (scroll suave, solo escritorio) y **AOS 2.3** (apariciones de bloques).
- Escenas: `position: sticky` en CSS + timelines de ScrollTrigger con `scrub: .6`.
- Titulares `.split`: SplitText por líneas con máscara, `yPercent 110 → 0`, 1,1 s, `power4.out`, desfase 0,1 s.
- Párrafos y botones `.sfx`: fade-up de 80 px, 1 s, `power3.out`, desfase 0,12 s. Bloques `[data-aos]`: 800 ms, una vez.
- **Celular (≤ 860 px)**: sin escenas fijadas, todo apilado; el hero se pinta al tiro (sin animación de entrada) y el globo queda en pose fija detrás de la consola.
- **`prefers-reduced-motion`**: sin Lenis, SplitText ni scrub; se muestran los estados finales.

## Rendimiento y accesibilidad (presupuesto)

- Lighthouse en local: escritorio 100/100/100/100, celular ≥ 95 en rendimiento y 100 en el resto.
  Medir con `npx lighthouse http://localhost:8000/` antes de un cambio grande de la landing.
- La inicialización de escenas cede el hilo principal entre pasos (ninguna tarea larga en celular).
- Canvas: el globo usa 300 puntos en pantallas chicas, degradado cónico para el borde de luz y se
  pausa fuera de pantalla. HTML, CSS y JS viajan con gzip; librerías con caché de 7 días.
- Contraste AA en todo texto, foco visible (anillo lima de 3 px), botones solo-ícono con `aria-label`.

## Componentes

- Botón primario: píldora lima, texto negro. Secundario: píldora con borde blanco. Chips de área: borde `--line`.
- Consola del agente, ventana del ERP y chat "Nodo": interfaces hechas en HTML/CSS, nunca capturas.
- Formulario: etiquetas visibles, inputs de 48 px, errores con texto.

## Imágenes, íconos y redes

- Íconos de línea propios (`_icons.html`). Sin emojis, fotos de stock, logos de clientes ni testimonios hasta tenerlos reales.
- Imagen para compartir `static/img/og-nodosur.png` (1200×630) y `apple-touch-icon.png` (180×180):
  se regeneran con `python scripts/build_social_images.py` si cambia el titular o la marca.
