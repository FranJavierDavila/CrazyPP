#!/usr/bin/env python3
"""QA V3.1.1-FEEL1 del centro de descargas (/descargas).

Verifica: 4 tarjetas/enlaces v311-feel1, menciones de versión y de los 3
ajustes (gracia del saque, rebote real, prompt B), 0 residuos de versiones
anteriores, los 4 ZIP servidos con HTTP 200 y tamaños EXACTOS, el intro
oficial byte-perfecto vía gateway y 0 pageerrors en la sesión.
"""
import asyncio, sys, urllib.request
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"
GW = "http://localhost:81"
OUT_PNG = "/home/z/my-project/download/qa_feel1_descargas_hub.png"

FAILS = []
def check(name, ok, detail=""):
    tag = "OK " if ok else "FAIL"
    print(f"  [{tag}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()

def head(url):
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, int(r.headers.get("Content-Length", "0"))

ZIPS = {
    "crazypp-v311-feel1-COMPLETO.zip": 106563566,
    "crazypp-v311-feel1-ligera.zip": 11452849,
    "crazypp-v311-feel1-CLOUDFLARE.zip": 106552010,
    "crazypp-live-service-SOLO.zip": 6089,
}

# ---------------------------------------------------------------- estáticos
print("== HUB /descargas (estático) ==")
hub = fetch(BASE + "/descargas").decode("utf-8", "replace")
for z in ZIPS:
    check(f"enlace a {z}", f'/descargas/{z}"' in hub)
n311 = hub.count("3.1.1-FEEL1")
check("menciones 3.1.1-FEEL1 (≥ 6)", n311 >= 6, f"n={n311}")
for frase, minimo in [("gracia", 1), ("DECAE", 1), ("Menú Principal SI/No", 1)]:
    check(f"menciona «{frase}» (ajuste del dueño)", hub.count(frase) >= minimo,
          f"n={hub.count(frase)}")
for residuo in ["v309-hall1", "v310-srv2", "3.0.9", "3.1.0-SRV2"]:
    check(f"0 residuos {residuo}", residuo not in hub)

# ---------------------------------------------------------------- ZIPs
print("== ZIPs servidos (dev :3000) ==")
for z, exacto in ZIPS.items():
    st, n = head(BASE + "/descargas/" + z)
    check(f"ZIP {z}", st == 200 and n == exacto, f"{n:,} B (esperado {exacto:,})")

# ---------------------------------------------------------------- gateway
print("== Gateway :81 en vivo ==")
try:
    gw_hub = fetch(GW + "/descargas").decode("utf-8", "replace")
    check("gateway /descargas 200 con v311", "3.1.1-FEEL1" in gw_hub)
except Exception as e:
    check("gateway /descargas", False, str(e))
gw_game = fetch(GW + "/game.html").decode("utf-8", "replace")
check("gateway /game.html = V3.1.1-FEEL1", "const VERSION = '3.1.1-FEEL1'" in gw_game)
st, n = head(GW + "/assets/intro.mp4")
check("gateway /assets/intro.mp4 (intro oficial byte-perfecta)",
      st == 200 and n == 5779719, f"{n:,} B")
for z, exacto in ZIPS.items():
    st, n = head(GW + "/descargas/" + z)
    check(f"gateway ZIP {z}", st == 200 and n == exacto, f"{n:,} B")

# ---------------------------------------------------------------- sesión
print("== SESIÓN (pageerrors + captura) ==")
async def sesion():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(BASE + "/descargas", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        cards = await page.evaluate(
            "Array.from(document.querySelectorAll('a[download]')).map(a => a.getAttribute('href'))")
        check("4 botones de descarga en el DOM",
              sum(1 for h in cards if h and "v311-feel1" in h) == 3
              and sum(1 for h in cards if h and "SOLO" in h) == 1, str(cards))
        check("0 pageerrors en la sesión", len(errors) == 0, "; ".join(errors[:3]))
        await page.screenshot(path=OUT_PNG)
        await browser.close()

asyncio.run(sesion())

print()
if FAILS:
    print("RESULTADO: FALLOS ->", FAILS); sys.exit(1)
print("RESULTADO OK")
