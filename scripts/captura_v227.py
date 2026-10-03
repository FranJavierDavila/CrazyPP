#!/usr/bin/env python3
"""Capturas v2.27: menú de muñeca en INGLÉS (dentro del visor simulado) y
cartel de fin de partido en inglés."""
import asyncio, base64, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4200)
        await page.click("#spectate")
        await page.wait_for_timeout(300)

        # ---- menú VR en ENGLISH ----
        shot = await page.evaluate("""() => {
            const g = window.__game;
            window.__setLang('en', g);
            g.rules.startMatch('match');
            g.connected = [true, true];
            g.toggleMenu();
            g.renderer.xr.isPresenting = false;
            g.camera.position.set(0.32, 0.1, 0.62);
            g.camera.lookAt(0, 0.1, 0);
            g.camera.updateMatrixWorld(true);
            g.renderer.render(g.scene, g.camera);
            const d = g.renderer.domElement.toDataURL('image/png');
            g.renderer.xr.isPresenting = true;
            g.toggleMenu();
            return d;
        }""")
        open("/home/z/my-project/download/captura-v227-menu-en.png", "wb").write(
            base64.b64decode(shot.split(",", 1)[1]))

        # ---- cartel YOU WON! en inglés ----
        shot2 = await page.evaluate("""() => {
            const g = window.__game;
            window.__setLang('en', g);
            g.rules.startMatch('match');
            g.rules.scorePlayer = 11; g.rules.scoreAi = 7;
            g.rules.state = 'over';
            g.rules.stateTimer = 8;      // el bucle no reinicia durante la captura
            g.startFanfare(true);
            g.connected = [true, true];
            g.renderer.xr.isPresenting = false;
            g.camera.position.set(0, 1.35, 1.15);
            g.camera.lookAt(0, 1.7, -1.6);
            g.camera.updateMatrixWorld(true);
            return new Promise((res) => setTimeout(() => {
                g.renderer.render(g.scene, g.camera);
                res(g.renderer.domElement.toDataURL('image/png'));
            }, 450));
        }""")
        open("/home/z/my-project/download/captura-v227-victoria-en.png", "wb").write(
            base64.b64decode(shot2.split(",", 1)[1]))
        await browser.close()
        print("capturas OK")

asyncio.run(main())
