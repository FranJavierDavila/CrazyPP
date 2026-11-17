"""Captura la portada de la build final servida en la preview raíz."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto("http://localhost:3000/", wait_until="load", timeout=60000)
    page.wait_for_timeout(7000)  # dejar cargar arte de portada y escena
    page.screenshot(path="/home/z/my-project/download/captura-preview-build-final.png")
    # segundo plano: dentro del visor (2D) si hay botón de entrar
    try:
        page.get_by_text("JUGAR EN VR").click(timeout=3000)
        page.wait_for_timeout(5000)
        page.screenshot(path="/home/z/my-project/download/captura-preview-juego-final.png")
    except Exception as e:
        print("Nota:", type(e).__name__)
    browser.close()
print("Capturas listas")
