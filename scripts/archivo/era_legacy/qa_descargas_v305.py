#!/usr/bin/env python3
"""QA visual del centro de descargas V3.0.5-FIS1:
   - /descargas carga sin pageerrors
   - 4 tarjetas con hrefs a los ZIP v305
   - captura en download/qa_fis1_descargas_hub.png
"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://localhost:3000/descargas"
OUT = "/home/z/my-project/download/qa_fis1_descargas_hub.png"

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
            fis1: (txt.match(/V3\\.0\\.5-FIS1/g) || []).length,
            v304_leftover: txt.includes('V3.0.4-EXP'),
          };
        }""")
        print("enlaces descarga:", cards["links"])
        print("menciones V3.0.5-FIS1:", cards["fis1"])
        print("¿quedan rastros V3.0.4?:", cards["v304_leftover"])
        big_ok = all("v305-fis1" in l for l in cards["links"][:3])
        solo_ok = cards["links"][3].endswith("crazypp-live-service-SOLO.zip") if len(cards["links"]) > 3 else False
        ok = (len(cards["links"]) == 4 and big_ok and solo_ok
              and cards["fis1"] >= 4 and not cards["v304_leftover"])
        await page.screenshot(path=OUT, full_page=True)
        await browser.close()
        print("pageerrors:", errors or "ninguno")
        print("CAPTURA:", OUT)
        print("RESULTADO:", "OK" if ok and not errors else "FALLO")

asyncio.run(main())
