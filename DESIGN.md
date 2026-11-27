# DESIGN.md · NodoSur

Dirección: **"producto en escena"**: página oscura de punta a punta, titulares blancos grandes y
cortos, y la tecnología (consola del agente, ERP, chat) presentada como un producto premium que
se revela con el scroll. Referencia de patrón entregada por Ely: página de producto de OBSBOT
Meet 4K (fondo negro, titulares centrados de 2-5 palabras, secciones fijadas de 100vh, bento de
tarjetas, revelado del producto con scroll). Se toma el patrón, nunca marca, imágenes ni textos.

## Color (tokens en `app/static/css/tokens.css`) · un solo tema, oscuro

| Token | Valor | Rol |
|---|---|---|
| `--bg` | `#050807` | Fondo de página |
| `--surface` | `#0D1311` | Tarjetas, formularios |
| `--surface-2` | `#141C19` | Inputs, bandas alternas |
| `--line` | `#1F2A26` | Bordes y divisores |
| `--text` | `#F2F5F3` | Titulares y texto principal |
| `--text-muted` | `#9AA8A3` | Texto secundario (contraste 7.9:1 sobre `--bg`) |
| `--signal` | `#C8F25C` | **Primario**: CTA, estado "en vivo", foco. Texto encima: `--bg` |
| `--signal-strong` | `#DAFA86` | Hover del primario |
| `--teal` | `#3CCB9F` | Acento secundario: links, datos, íconos |
| `--warn / --error / --ok` | `#FBBF24 / #F87171 / #4ADE80` | Estados en consolas y mockups |
| `--paper` | `#F4F6F2` | Solo dentro de mockups claros (pantalla del ERP) |

## Tipografía

- Titulares: **Space Grotesk 700**, tracking -0.02em. Texto: **IBM Plex Sans** 400/500. Etiquetas y códigos: **IBM Plex Mono** 500.
- Escala: 0.75 · 0.875 · 1 (cuerpo 16-17px) · 1.125 · 1.375 · 2 · clamp(2.25, 4.5vw, 3.5) H2 · clamp(2.75, 7vw, 6) H1/declaraciones.
- Titulares de 2 a 6 palabras, centrados en secciones de escena; alineados a la izquierda en secciones de contenido.

## Movimiento (`app/static/js/landing.js`)

- **Revelado del hero**: contenedor de 220vh con escena fijada; la consola pasa de `scale(.82) rotateX(28deg)` y opacidad .2 a su estado normal según el progreso del scroll (variable `--p` de 0 a 1).
- **Escenas fijadas**: secciones `.scene` de N×100vh con un panel `position: sticky` de 100vh; `--p` controla qué paso está activo.
- **Aparición**: `[data-reveal]` hace fade-up de 24px en 600ms al entrar en pantalla (IntersectionObserver).
- **Contadores**: `[data-count]` suben hasta su valor la primera vez que se ven.
- `prefers-reduced-motion: reduce` desactiva todo el movimiento y muestra el estado final.

## Espaciado y forma

- Escala de 4px: 4, 8, 12, 16, 24, 32, 48, 64, 96, 160. Escenas: 100vh. Secciones normales: 128px escritorio / 72px móvil.
- Contenido máx. 1200px. Radio: 8px (inputs) · 20px (tarjetas) · 999px (botones). Sin sombras: profundidad con bordes `--line` y brillo `--signal` al 12%.

## Componentes

- Botón primario: píldora lima con texto oscuro. Secundario: píldora con borde `--line` y texto claro. Foco: anillo de 3px `--signal`.
- Barra superior fija con marca + anclas + CTA píldora (patrón sub-nav de la referencia).
- Bento: tarjetas oscuras con título arriba a la izquierda; IA ocupa 2 columnas.
- Formulario: etiquetas visibles, inputs de 48px, estados de error con texto.

## Imágenes e íconos

- Íconos de línea propios (trazo 1.75). Sin emojis, sin fotos de stock, sin logos de clientes ni testimonios hasta tenerlos reales.
- Los "productos" son interfaces construidas en HTML/CSS: consola de operaciones, ERP, chat.
