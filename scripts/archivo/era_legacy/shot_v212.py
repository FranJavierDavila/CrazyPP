#!/usr/bin/env python3
"""Captura el modo demo (sin overlay) para verificar visualmente la pala GLB."""
import asyncio
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
OUT1 = "/home/z/my-project/scripts/preview_v212_demo_nova.png"
OUT2 = "/home/z/my-project/scripts/preview_v212_demo_nova2.png"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4000)
        # ocultar overlay y capturar la escena demo (órbita): pala GLB visible
        await page.evaluate("""() => {
            document.getElementById('overlay').classList.add('hidden');
        }""")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=OUT1)
        await page.wait_for_timeout(3500)
        await page.screenshot(path=OUT2)
        await browser.close()
        print("errores:", errs if errs else "ninguno")
        print("OK ->", OUT1, "·", OUT2)

asyncio.run(main())
