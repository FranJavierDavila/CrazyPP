#!/usr/bin/env python3
"""QA del centro de descargas V3.0.6-SRV1:
  1) /descargas carga sin pageerrors
  2) 4 enlaces de descarga con los nombres v306-srv1 correctos
  3) cabecera menciona V3.0.6-SRV1 y el intro oficial
  4) 0 restos de la v305-fis1 en enlaces
  5) los 4 ZIP responden 200 y el intro dentro del paquete es el oficial
     (verificado en disco por build_zip.py)
Captura: download/qa_srv1_descargas_hub.png
"""
import asyncio, urllib.request
from playwright.async_api import async_playwright

URL = "http://localhost:3000/descargas"
OUT = "/home/z/my-project/download/qa_srv1_descargas_hub.png"

ZIPS = [
    "/descargas/crazypp-v306-srv1-COMPLETO.zip",
    "/descargas/crazypp-v306-srv1-ligera.zip",
    "/descargas/crazypp-v306-srv1-CLOUDFLARE.zip",
    "/descargas/crazypp-live-service-SOLO.zip",
]

def head(url):
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, int(r.headers.get("Content-Length", 0))

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        body = await page.inner_text("body")
        hrefs = await page.eval_on_selector_all(
            "a[download]", "els => els.map(e => e.getAttribute('href'))")
        print("enlaces descarga:", hrefs)

        # menciones de versión
        v306 = body.upper().count("V3.0.6-SRV1") + body.upper().count("3.0.6")
        intro = body.upper().count("INTRO")
        v305_links = [h for h in hrefs if h and "v305" in h.lower()]
        print(f"menciones 3.0.6: {v306} · menciones INTRO: {intro}")
        print("enlaces v305 residuales:", v305_links or "ninguno")

        await page.screenshot(path=OUT, full_page=True)
        await browser.close()

    # los 4 ZIP accesibles con tamaño esperado
    esperado = {
        ZIPS[0]: (106_000_000, 108_000_000),
        ZIPS[1]: (11_000_000, 12_500_000),
        ZIPS[2]: (106_000_000, 108_000_000),
        ZIPS[3]: (4_000, 12_000),   # 12 KB sin comprimir, ~6 KB en zip
    }
    zips_ok = True
    for z in ZIPS:
        st, n = head("http://localhost:3000" + z)
        lo, hi = esperado[z]
        okz = st == 200 and lo <= n <= hi
        zips_ok = zips_ok and okz
        print(f"  {z}: HTTP {st}, {n:,} B → {'OK' if okz else 'REVISAR'}")

    ok = (errors == []
          and sorted(hrefs) == sorted(ZIPS)
          and v306 >= 3 and intro >= 2
          and not v305_links
          and zips_ok)
    print("pageerrors :", errors or "ninguno")
    print("CAPTURA    :", OUT)
    print("RESULTADO  :", "OK" if ok else "REVISAR")

asyncio.run(main())
