#!/usr/bin/env python3
"""Captura visual del HALL DEL ANFITRIÓN: renderiza la escena con una cámara
manual colocada en el punto de aparición (mirando a la pared de trofeos) y
vuelca el canvas 3D a PNG. No toca el estado del juego (sólo render 1 frame)."""
import asyncio, base64
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT = "/home/z/my-project/download/qa_hall1_hall_3d.png"

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)

        data = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          G.enterHall();
          await new Promise(r => setTimeout(r, 1500));   // insignias y lienzos
          const cam = G.camera.clone();                  // misma lente, otra pose
          cam.aspect = 16 / 9;
          cam.fov = 72;
          cam.updateProjectionMatrix();
          cam.position.set(0, 1.62, -16.2);              // punto de aparición
          cam.lookAt(new (G.camera.position.constructor)(0, 1.55, -21.95));
          G.renderer.render(G.scene, cam);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        png = base64.b64decode(data.split(",", 1)[1])
        with open(OUT, "wb") as f:
            f.write(png)
        print("captura     :", OUT, f"({len(png):,} B)")
        await browser.close()
    print("pageerrors  :", errors or "ninguno")
    print("RESULTADO   :", "OK" if not errors else "REVISAR")

asyncio.run(main())
