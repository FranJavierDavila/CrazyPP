#!/usr/bin/env python3
"""Capturas v2.19: páginas del menú de muñeca (principal, multijugador, join)."""
import asyncio
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
OUT = "/home/z/my-project/download"

PLACE = """() => {
    const g = window.__game;
    g.setTheme('pabellon', true);
    g.menuGroup.position.set(0.62, 1.02, -0.72);
    g.menuGroup.lookAt(2.2, 1.5, 1.4);
    g.toggleMenu();
    g.menuGroup.updateMatrixWorld(true);
}"""

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
        await page.evaluate(PLACE)
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/captura-v219-menu-ajustes.png")

        # página MULTIJUGADOR con sala esperando (código visible)
        await page.evaluate("""() => {
            const g = window.__game;
            g.menuPage = 'multi';
            g.net.status = 'waiting';
            g.net.code = 'K7F2Q';
            g.drawMenu();
            g.menuGroup.updateMatrixWorld(true);
        }""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/captura-v219-menu-multi.png")

        # página JOIN con código a medias
        await page.evaluate("""() => {
            const g = window.__game;
            g.menuPage = 'join';
            g.net.status = 'off';
            g._joinCode = 'AB2';
            g.drawMenu();
            g.menuGroup.updateMatrixWorld(true);
        }""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/captura-v219-menu-teclado.png")

        await browser.close()
        print("capturas OK")

asyncio.run(main())
