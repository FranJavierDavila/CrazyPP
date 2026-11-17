"""Navega la V2.122 hasta el menú de campeonatos y verifica que cargan."""
from playwright.sync_api import sync_playwright

errores = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.on("pageerror", lambda e: errores.append(str(e)))
    pg.goto("http://localhost:8901/", wait_until="load", timeout=60000)
    pg.wait_for_timeout(4000)
    try:
        pg.get_by_text("ESPAÑOL", exact_ok := True).first.click(timeout=4000)
        pg.wait_for_timeout(2500)
    except Exception as e:
        print("selector idioma:", type(e).__name__)
    pg.screenshot(path="/home/z/my-project/download/captura-v2122-menu.png")
    txt = pg.inner_text("body")
    print("MENU:", " | ".join([l for l in txt.splitlines() if l.strip()][:22]))
    # buscar y entrar en campeonatos
    for candidata in ["CAMPEONATOS", "Campeonatos", "CAMPEONATO"]:
        try:
            pg.get_by_text(candidata).first.click(timeout=3000)
            pg.wait_for_timeout(3000)
            break
        except Exception:
            continue
    pg.screenshot(path="/home/z/my-project/download/captura-v2122-campeonatos.png")
    txt2 = pg.inner_text("body")
    claves = [c for c in ["OESTE", "Oeste", "MAGIA", "Magia", "LOCURA", "Locura", "RANKING"] if c in txt2]
    print("Encontrados en menú campeonatos:", claves)
    print("Errores JS:", len(errores), errores[:3])
    b.close()
