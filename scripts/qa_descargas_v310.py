#!/usr/bin/env python3
"""QA del centro de descargas V3.1.0-SRV2:
  1) /descargas carga sin pageerrors
  2) 4 enlaces de descarga con los nombres v310-srv2 correctos
  3) cabecera menciona V3.1.0-SRV2 y el saque realista
  4) 0 restos de la v309-hall1 en enlaces
  5) los 4 ZIP responden 200 con el tamaño exacto de build_zip.py
Captura: download/qa_srv2_descargas_hub.png
"""
import asyncio, urllib.request
from playwright.async_api import async_playwright

URL = "http://localhost:3000/descargas"
OUT = "/home/z/my-project/download/qa_srv2_descargas_hub.png"

ZIPS = [
    "/descargas/crazypp-v310-srv2-CLOUDFLARE.zip",
    "/descargas/crazypp-v310-srv2-COMPLETO.zip",
    "/descargas/crazypp-v310-srv2-ligera.zip",
    "/descargas/crazypp-live-service-SOLO.zip",
]

# tamaños exactos producidos por release-v310/build_zip.py
EXACTO = {
    ZIPS[0]: 106_548_099,
    ZIPS[1]: 106_559_804,
    ZIPS[2]: 11_449_087,
    ZIPS[3]: 6_089,
}

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

        v310 = body.upper().count("V3.1.0-SRV2") + body.upper().count("3.1.0")
        saque = body.upper().count("SAQUE")
        v309_links = [h for h in hrefs if h and "v309" in h.lower()]
        print(f"menciones 3.1.0: {v310} · menciones SAQUE: {saque}")
        print("enlaces v309 residuales:", v309_links or "ninguno")

        await page.screenshot(path=OUT, full_page=True)
        await browser.close()

    zips_ok = True
    for z in ZIPS:
        st, n = head("http://localhost:3000" + z)
        okz = st == 200 and n == EXACTO[z]
        zips_ok = zips_ok and okz
        print(f"  {z}: HTTP {st}, {n:,} B (esperado {EXACTO[z]:,}) → {'OK' if okz else 'REVISAR'}")

    ok = (errors == []
          and sorted(hrefs) == sorted(ZIPS)
          and v310 >= 6 and saque >= 2
          and not v309_links
          and zips_ok)
    print("pageerrors :", errors or "ninguno")
    print("CAPTURA    :", OUT)
    print("RESULTADO  :", "OK" if ok else "REVISAR")

asyncio.run(main())
