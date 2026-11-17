"""Prueba de arranque de la V2.122 del usuario: portada + errores de consola."""
from playwright.sync_api import sync_playwright

errores = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errores.append(str(e)))
    page.goto("http://localhost:8901/", wait_until="load", timeout=60000)
    page.wait_for_timeout(8000)
    page.screenshot(path="/home/z/my-project/download/captura-v2122-portada.png")
    # capturar textos visibles clave para confirmar build nueva
    texto = page.inner_text("body")[:400]
    browser.close()

print("Errores de consola:", len(errores))
for e in errores[:8]:
    print("  -", e[:160])
print("Texto visible:", texto.replace(chr(10), " | ")[:350])
