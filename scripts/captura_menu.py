"""Captura el menú principal (HUB) del juego en modo espectador 2D."""
import sys
from playwright.sync_api import sync_playwright

out1 = sys.argv[1] if len(sys.argv) > 1 else "/home/z/my-project/download/menu-actual.png"

errores = []
with sync_playwright() as p:
    browser = p.chromium.launch(args=["--use-webgl", "--enable-webgl"])
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.on("pageerror", lambda e: errores.append(str(e)))
    page.goto("http://localhost:8901/", wait_until="load", timeout=60000)
    page.wait_for_timeout(6000)
    # entrar al juego (espectador si no hay VR): el botón es img#playEs
    try:
        page.locator("#playEs").click(timeout=5000)
    except Exception as e:
        print("Nota clic:", type(e).__name__)
    page.wait_for_timeout(8000)
    page.screenshot(path=out1)
    browser.close()

print("Captura:", out1)
print("Errores JS:", len(errores))
for e in errores[:5]:
    print("  -", e[:200])
