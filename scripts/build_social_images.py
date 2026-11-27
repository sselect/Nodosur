"""Genera las imágenes para compartir: Open Graph (1200×630) y apple-touch-icon (180×180).

Uso (solo cuando cambie la marca o el titular):
    pip install playwright && playwright install chromium   (o CHROME_PATH=/ruta/a/chrome)
    python scripts/build_social_images.py

Las imágenes quedan en app/static/img/ y se versionan en el repo, así producción no depende de Playwright.
"""

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.content import COMPANY  # noqa: E402

OUT = ROOT / "app" / "static" / "img"
FONTS = "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=Montserrat:wght@600;700&display=swap"

LOGO = """<svg viewBox="0 0 28 28" width="{s}" height="{s}">
  <circle cx="6" cy="22" r="3" fill="#fff"/><circle cx="22" cy="6" r="3" fill="#fff"/>
  <circle cx="22" cy="22" r="3" fill="#c8f25c"/>
  <path d="M6 22L22 6M22 6v16M6 22h16" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/>
</svg>"""

# Globo de nodos: mismo algoritmo que el hero (esfera de Fibonacci + borde de luz), cuadro fijo.
GLOBE_JS = """
const c = document.querySelector('canvas'), ctx = c.getContext('2d');
const W = c.width, H = c.height, cx = W * 0.5, cy = H * 0.52, R = Math.min(W, H) * 0.42, N = 380;
let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
const pts = [];
for (let i = 0; i < N; i++) {
  const y = 1 - (i / (N - 1)) * 2, r = Math.sqrt(1 - y * y), th = Math.PI * (3 - Math.sqrt(5)) * i;
  pts.push([Math.cos(th) * r, y, Math.sin(th) * r]);
}
const rot = (p) => { const a = 0.7, b = 0.35; let [x, y, z] = p;
  [x, z] = [x * Math.cos(a) - z * Math.sin(a), x * Math.sin(a) + z * Math.cos(a)];
  [y, z] = [y * Math.cos(b) - z * Math.sin(b), y * Math.sin(b) + z * Math.cos(b)]; return [x, y, z]; };
const D = 3.2, proj = pts.map(rot).map(([x, y, z]) => { const k = D / (D - z); return [cx + x * R * k, cy + y * R * k, z]; });
ctx.lineWidth = 1;
pts.forEach((p, i) => {
  const near = pts.map((q, j) => [j, (p[0]-q[0])**2 + (p[1]-q[1])**2 + (p[2]-q[2])**2]).sort((a, b) => a[1] - b[1]).slice(1, 3);
  near.forEach(([j]) => { const z = (proj[i][2] + proj[j][2]) / 2, a = 0.05 + 0.2 * (z + 1) / 2;
    ctx.strokeStyle = `rgba(220,240,225,${a})`; ctx.beginPath(); ctx.moveTo(proj[i][0], proj[i][1]); ctx.lineTo(proj[j][0], proj[j][1]); ctx.stroke(); });
});
proj.forEach(([x, y, z]) => { const lit = rnd() < 0.06, a = 0.25 + 0.6 * (z + 1) / 2;
  ctx.fillStyle = lit ? `rgba(200,242,92,${a})` : `rgba(235,245,238,${a})`;
  ctx.beginPath(); ctx.arc(x, y, lit ? 2.6 : 1.4, 0, Math.PI * 2); ctx.fill(); });
const a0 = Math.PI * 1.02, a1 = Math.PI * 1.98, segs = 56;
ctx.lineCap = 'round'; ctx.shadowColor = 'rgba(200,242,92,.8)'; ctx.shadowBlur = 24;
for (let i = 0; i < segs; i++) { const u = i / segs, v = (i + 1) / segs, env = Math.sin(Math.PI * (u + v) / 2) ** 2;
  ctx.beginPath(); ctx.arc(cx, cy, R * 1.03, a0 + (a1 - a0) * u, a0 + (a1 - a0) * v + 0.004);
  ctx.strokeStyle = `rgba(240,255,200,${0.9 * env})`; ctx.lineWidth = 1.8 + 1.6 * env; ctx.stroke(); }
"""

OG_HTML = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<link href="{FONTS}" rel="stylesheet"><style>
  * {{ margin: 0; box-sizing: border-box; }}
  body {{ width: 1200px; height: 630px; background: #000; color: #fff; font-family: Montserrat, sans-serif; overflow: hidden; position: relative; }}
  .glow {{ position: absolute; inset: 0; background:
    radial-gradient(40% 50% at 76% 100%, rgb(200 242 92 / .22), transparent 70%),
    radial-gradient(60% 50% at 70% 115%, rgb(60 203 159 / .2), transparent 70%); }}
  canvas {{ position: absolute; right: -60px; top: 40px; width: 640px; height: 640px; }}
  .copy {{ position: absolute; left: 72px; top: 76px; width: 640px; }}
  .brand {{ display: flex; align-items: center; gap: 14px; font-size: 34px; font-weight: 700; letter-spacing: -.02em; }}
  .brand b {{ color: #c8f25c; font-weight: 700; }}
  h1 {{ margin-top: 64px; font-size: 64px; line-height: 1.12; font-weight: 700; letter-spacing: -.025em; }}
  h1 span {{ color: #c8f25c; }}
  p {{ margin-top: 34px; font: 500 21px/1.5 "IBM Plex Mono", monospace; color: #a3aca8; }}
</style></head><body>
  <div class="glow"></div><canvas width="1280" height="1280"></canvas>
  <div class="copy">
    <div class="brand">{LOGO.format(s=46)}<div>nodo<b>sur</b></div></div>
    <h1>Tecnología<br>que no se cae.<br><span>IA que sí trabaja.</span></h1>
    <p>Soporte TI N2/N3 · Cloud · Web · ERP · IA aplicada</p>
  </div>
  <script>{GLOBE_JS}</script>
</body></html>"""

ICON_HTML = f"""<!doctype html><html><head><style>
  * {{ margin: 0; }} body {{ width: 180px; height: 180px; background: #000; display: grid; place-items: center; }}
</style></head><body>{LOGO.format(s=112)}</body></html>"""


async def main() -> None:
    from playwright.async_api import async_playwright

    assert "Tecnología que no se cae" in COMPANY["tagline"], "El titular de la imagen OG ya no coincide con content.py"
    async with async_playwright() as p:
        # CHROME_PATH permite usar un Chrome ya instalado en vez del de Playwright
        browser = await p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        for html, size, name in [
            (OG_HTML, (1200, 630), "og-nodosur.png"),
            (ICON_HTML, (180, 180), "apple-touch-icon.png"),
        ]:
            page = await browser.new_page(viewport={"width": size[0], "height": size[1]})
            await page.set_content(html, wait_until="networkidle")
            await page.evaluate("document.fonts.ready")
            await page.screenshot(path=str(OUT / name))
            print("ok", OUT / name)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
