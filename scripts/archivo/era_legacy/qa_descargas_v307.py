#!/usr/bin/env python3
"""QA visual del centro de descargas V3.0.7-PLAY1:
   - /descargas carga sin pageerrors
   - 4 tarjetas con hrefs a los ZIP v307-play1 (SOLO conserva su nombre histórico)
   - HTTP 200/206 en los 4 ZIP servidos
   - captura en download/qa_play1_descargas_hub.png
"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://localhost:3000/descargas"
OUT = "/home/z/my-project/download/qa_play1_descargas_hub.png"

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 1000})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1500)

        cards = await page.evaluate("""() => {
          const links = [...document.querySelectorAll('a[download]')]
            .map(a => a.getAttribute('href'));
          const txt = document.body.innerText;
          return {
            links,
            play1: (txt.match(/V3\\.0\\.7-PLAY1/g) || []).length,
            v306_leftover: txt.includes('V3.0.6-SRV1'),
          };
        }""")
        print("enlaces descarga:", cards["links"])
        print("menciones V3.0.7-PLAY1:", cards["play1"])
        print("¿quedan rastros V3.0.6?:", cards["v306_leftover"])

        # los 4 ZIP deben servirse (200/206) desde la preview
        import urllib.request
        codes = []
        for l in cards["links"]:
            req = urllib.request.Request("http://localhost:3000" + l,
                                         headers={"Range": "bytes=0-1023"})
            try:
                with urllib.request.urlopen(req) as r:
                    codes.append(r.status)
            except Exception as e:
                codes.append(str(e))
        print("HTTP (range) de los ZIP:", codes)

        big_ok = all("v307-play1" in l for l in cards["links"][:3])
        solo_ok = cards["links"][3].endswith("crazypp-live-service-SOLO.zip") if len(cards["links"]) > 3 else False
        http_ok = all(c in (200, 206) for c in codes)
        ok = (len(cards["links"]) == 4 and big_ok and solo_ok
              and cards["play1"] >= 4 and not cards["v306_leftover"] and http_ok)
        await page.screenshot(path=OUT, full_page=True)
        await browser.close()
        print("pageerrors:", errors or "ninguno")
        print("CAPTURA:", OUT)
        print("RESULTADO:", "OK" if ok and not errors else "FALLO")

asyncio.run(main())
