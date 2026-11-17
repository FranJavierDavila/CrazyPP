"""Renderiza el panel del menú principal (HUB) del juego a PNG.

Usa el gancho de pruebas window.__PP_GAME: llama a drawMenu() (el mismo
método que pinta la textura del panel en VR) y vuelca menuCanvas a PNG.
Uso: python3 captura_hub.py http://localhost:8901/ /ruta/salida.png
"""
import base64
import sys

from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8901/"
out = sys.argv[2] if len(sys.argv) > 2 else "/home/z/my-project/scripts/hub.png"

errores = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.on("pageerror", lambda e: errores.append(str(e)))
    pg.goto(url, wait_until="load", timeout=60000)
    pg.wait_for_timeout(6000)
    data = pg.evaluate(
        """() => {
          const g = window.__PP_GAME;
          if (!g) return null;
          g.menuPage = 'main';
          g.drawMenu();
          return g.menuCanvas.toDataURL('image/png');
        }"""
    )
    b.close()

if not data or not data.startswith("data:image/png;base64,"):
    print("FALLO: sin canvas del menú", str(data)[:120])
    sys.exit(1)

b64 = data.split(",", 1)[1]
with open(out, "wb") as f:
    f.write(base64.b64decode(b64))
print("Panel del menú:", out)
print("Errores JS:", len(errores))
for e in errores[:5]:
    print("  -", e[:200])
