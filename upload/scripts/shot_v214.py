#!/usr/bin/env python3
"""Capturas de los 4 temas de sala con el overlay oculto (modo espectador)."""
import asyncio
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
OUT = "/home/z/my-project/scripts"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4200)
        await page.click("#spectate")
        await page.wait_for_timeout(1200)
        for key in ("pabellon", "neon", "atardecer", "artico"):
            await page.evaluate(f"window.__game.setTheme('{key}', true)")
            await page.wait_for_timeout(500)
            await page.screenshot(path=f"{OUT}/shot_v214_{key}.png")
        await browser.close()
    print("capturas listas")

asyncio.run(main())
