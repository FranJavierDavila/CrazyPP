#!/usr/bin/env python3
"""Capturas del panel del menú de muñeca sin overlay (modo espectador)."""
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
        await page.wait_for_timeout(800)
        await page.evaluate("""() => {
            const g = window.__game;
            g.setTheme('pabellon', true);
            g.menuGroup.position.set(0.62, 1.02, -0.72);
            g.menuGroup.lookAt(2.2, 1.5, 1.4);
            g.toggleMenu();
        }""")
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"{OUT}/shot_v215_menu.png")
        # con hover en 'Difícil' (índice 4) y tema Neón activo
        await page.evaluate("""() => {
            const g = window.__game;
            g.menuHover = 4;
            g.drawMenu();
            g.menuDot.visible = true;
            const r = g.menuRects[4];
            g.menuDot.position.set(
                ((r.x + r.w / 2) / 512 - 0.5) * 0.28,
                (0.5 - (r.y + r.h / 2) / 640) * 0.35, 0.004);
        }""")
        await page.wait_for_timeout(300)
        await page.screenshot(path=f"{OUT}/shot_v215_menu_hover.png")
        await browser.close()
    print("capturas listas")

asyncio.run(main())
