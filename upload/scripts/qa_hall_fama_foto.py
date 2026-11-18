#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fotografía del HALL OF FAME (v3.6.27): 4 tomas renderizadas con cámara
manual desde el punto de aparición — frontal (gloria + trofeo), izquierda
(logros), derecha (vitrinas de palas) y puerta (neón). Sólo render, no
toca el estado del juego."""
import asyncio
import base64

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
BASE = "/home/z/my-project/download/qa_hall_fama_"

TOMAS = [
    ("frontal", "0,1.62,-16.2", "0,1.55,-21.95", 72),
    ("logros",  "-1.4,1.62,-16.6", "-3.3,1.3,-19.0", 78),
    ("vitrinas", "1.4,1.62,-16.6", "3.3,1.2,-19.0", 78),
    ("neon",    "0,1.62,-17.6", "0,1.8,-14.9", 82),
]

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
        for nombre, pos, look, fov in TOMAS:
            data = await page.evaluate("""async ([pos, look, fov]) => {
              const G = window.__PP_GAME;
              if (!G.hallGroup || !G.hallGroup.visible) G.enterHall();
              await new Promise(r => setTimeout(r, 1200));
              const cam = G.camera.clone();
              cam.aspect = 16 / 9;
              cam.fov = fov;
              cam.updateProjectionMatrix();
              const V = G.camera.position.constructor;
              cam.position.set(...pos.split(',').map(Number));
              cam.lookAt(new V(...look.split(',').map(Number)));
              G.renderer.render(G.scene, cam);
              return G.renderer.domElement.toDataURL('image/png');
            }""", [pos, look, fov])
            png = base64.b64decode(data.split(",", 1)[1])
            out = BASE + nombre + ".png"
            with open(out, "wb") as f:
                f.write(png)
            print("toma", nombre, "→", out, f"({len(png):,} B)")
        await browser.close()
    print("pageerrors  :", errors or "ninguno")

asyncio.run(main())
