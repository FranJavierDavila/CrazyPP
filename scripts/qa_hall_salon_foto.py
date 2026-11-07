#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fotografía del SALÓN DEL ARTISTA (v3.6.28): 5 tomas renderizadas con
cámara manual — frontal (trofeo + pared de insignias), izquierda (ventanal
panorámico), derecha (insignias + puerta CRAZY PING PONG), puerta pintada
(fondo) y primer plano del trofeo sobre el emblema. Sólo render, no toca
el estado del juego."""
import asyncio
import base64

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
BASE = "/home/z/my-project/download/qa_hall_salon_"

TOMAS = [
    ("frontal", "0,1.62,-16.2", "0,1.35,-20.6", 75),
    ("ventanal", "-1.3,1.62,-17.0", "-3.0,1.25,-18.5", 78),
    ("insignias", "1.3,1.62,-17.0", "3.0,1.2,-18.5", 78),
    ("puerta",   "0,1.62,-19.6", "0,1.8,-14.6", 82),
    ("trofeo",   "0,1.5,-16.6", "0,0.85,-18.5", 68),
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
              await new Promise(r => setTimeout(r, 1500));
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
