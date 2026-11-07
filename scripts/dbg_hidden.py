#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        h = await b.new_page(viewport={"width": 1100, "height": 650})
        g = await b.new_page(viewport={"width": 1100, "height": 650})
        for pg, n in ((h, "H"), (g, "G")):
            await pg.goto("http://localhost:3000/game.html", wait_until="domcontentloaded")
        for i in range(10):
            hh = await h.evaluate("() => document.hidden + '/' + document.visibilityState")
            gg = await g.evaluate("() => document.hidden + '/' + document.visibilityState")
            print(f"t={i*2}s  host={hh}  guest={gg}", flush=True)
            await g.wait_for_timeout(2000)
        await b.close()

asyncio.run(main())
