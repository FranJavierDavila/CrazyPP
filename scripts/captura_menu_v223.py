#!/usr/bin/env python3
"""Captura v2.23: el menú con casillas ☑/☐ y botones activos con hover.
Abre el menú, apunta con el mando 0 a un basculante (hover activo) y vuelca
el canvas 2D del panel a PNG."""
import asyncio, base64
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(3600)

        # 1) menú sin hover
        b64 = await page.evaluate("""() => {
            const g = window.__game;
            if (g.menuOpen) g.toggleMenu();
            g.toggleMenu();
            g.menuHover = [-1, -1];
            g.drawMenu();
            return g.menuCanvas.toDataURL('image/png');
        }""")
        png = base64.b64decode(b64.split(',', 1)[1])
        open("/home/z/my-project/download/captura-v223-menu.png", "wb").write(png)
        print("captura menú:", len(png), "bytes")

        # 2) hover sobre el megáfono (botón activo): borde blanco visible
        b64 = await page.evaluate("""() => {
            const g = window.__game;
            const idx = g.menuRects.findIndex((r) => r.id === 'voz');
            g.menuHover = [idx, -1];
            g.drawMenu();
            return g.menuCanvas.toDataURL('image/png');
        }""")
        png = base64.b64decode(b64.split(',', 1)[1])
        open("/home/z/my-project/download/captura-v223-menu-hover.png", "wb").write(png)
        print("captura menú hover:", len(png), "bytes")

        await browser.close()
    print("errores página:", errors if errors else "ninguno")

asyncio.run(main())
