#!/usr/bin/env python3
"""Capturas v2.22: la pala de la IA con orientación realista.
  - espera: la cara mira a la bola (inclinada, no pared vertical)
  - follow-through: la cara acompaña el tiro con roll de muñeca
Uso: python3 scripts/captura_ia_pose.py"""
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
        try:
            await page.click("#spectate", timeout=2500)
        except Exception:
            pass

        # preparar escena y devolver datos de la pala para encuadrar
        info = await page.evaluate("""() => {
            const g = window.__game;
            const V = Object.getPrototypeOf(g.ball.pos).constructor;
            g.rules.state = 'rally';
            // ESPERA: bola alta del lado del jugador (la cara debe mirarla)
            g.ball.pos.set(0.3, 1.35, 0.8);
            g.ai.swing = null;
            for (let i = 0; i < 90; i++) g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.016);
            const vp = new V(); g.aiPaddleMesh.getWorldPosition(vp);
            return { x: vp.x, y: vp.y, z: vp.z };
        }""")
        print("pala IA (espera):", info)

        async def shot(name, dx, dy, dz):
            b64 = await page.evaluate("""([bx, by, bz, dx, dy, dz]) => {
                const g = window.__game;
                g.camera.position.set(bx + dx, by + dy, bz + dz);
                g.camera.lookAt(bx, by, bz);
                g.camera.updateMatrixWorld(true);
                g.renderer.render(g.scene, g.camera);
                return g.renderer.domElement.toDataURL('image/png');
            }""", [info["x"], info["y"], info["z"], dx, dy, dz])
            png = base64.b64decode(b64.split(',', 1)[1])
            open(f"/home/z/my-project/scripts/ia_{name}.png", "wb").write(png)
            print("captura", name, len(png), "bytes")

        # vista del jugador (desde +Z mirando a la CPU)
        await shot("espera", 0.9, 0.55, 2.6)

        # FOLLOW-THROUGH tras un liftado
        await page.evaluate("""() => {
            const g = window.__game;
            const V = Object.getPrototypeOf(g.ball.pos).constructor;
            g.ball.vel.set(1, 0.7, 6); g.ball.spin.set(3.2, 0, 0);
            g.ball.pos.set(0, 1.0, -1.35);
            g.ai.swing = { t: 0.06, dur: 0.3, contact: new V(0, 0.95, -1.4),
                           dir: new V(0, 0, 1), speed: 1.2, roll: 0.18 };
            for (let i = 0; i < 10; i++) g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.016);
            const vp = new V(); g.aiPaddleMesh.getWorldPosition(vp);
            window.__pos2 = { x: vp.x, y: vp.y, z: vp.z };
        }""")
        info2 = await page.evaluate("() => window.__pos2")
        print("pala IA (swing):", info2)
        b64 = await page.evaluate("""([p, dx, dy, dz]) => {
            const g = window.__game;
            g.camera.position.set(p.x + dx, p.y + dy, p.z + dz);
            g.camera.lookAt(p.x, p.y, p.z);
            g.camera.updateMatrixWorld(true);
            g.renderer.render(g.scene, g.camera);
            return g.renderer.domElement.toDataURL('image/png');
        }""", [info2, 0.8, 0.5, 2.4])
        png = base64.b64decode(b64.split(',', 1)[1])
        open("/home/z/my-project/scripts/ia_swing.png", "wb").write(png)
        print("captura swing", len(png), "bytes")

        await browser.close()
    print("errores página:", errors if errors else "ninguno")

asyncio.run(main())
