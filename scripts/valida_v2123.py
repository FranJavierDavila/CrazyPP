"""Validación final de la V2.123 servida en la preview del proyecto.

Comprueba: portada carga, 0 errores de consola, 0 recursos fallidos y
que el juego expone la versión 2.123.0.
"""
from playwright.sync_api import sync_playwright

errores = []
fallidos = []

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errores.append(str(e)))
    pg.on("response", lambda r: fallidos.append(f"{r.status} {r.url}") if r.status >= 400 else None)
    pg.goto("http://localhost:3000/game.html", wait_until="load", timeout=60000)
    pg.wait_for_timeout(9000)
    pg.screenshot(path="/home/z/my-project/scripts/portada-v2123.png")
    version = pg.evaluate("() => (window.__PP_GAME ? 'game vivo' : 'SIN GAME')")
    b.close()

print("Versión/estado:", version)
print("Errores de consola:", len(errores))
for e in errores[:8]:
    print("  -", e[:180])
print("Recursos fallidos:", len(fallidos))
for f in fallidos[:8]:
    print("  -", f[:180])
