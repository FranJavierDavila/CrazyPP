#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_r73 — sonda visual del menú CAMPEONATOS (r73).
Sirve public/ y fotografía el canvas del menú real en 2 páginas:
hub principal + CAMPEONATOS. Además vuelca champs.list() y los rects."""
import asyncio
import json
import subprocess
import sys
import time
import os
import signal

from playwright.async_api import async_playwright

PORT = 8873
URL = f"http://localhost:{PORT}/game.html"
OUT = "/home/z/my-project/scripts/_r73"
os.makedirs(OUT, exist_ok=True)


async def main():
    srv = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd="/home/z/my-project/public",
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )
    time.sleep(1.2)
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
            page = await browser.new_page(viewport={"width": 1280, "height": 720})
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            # esperar juego
            for _ in range(120):
                listo = await page.evaluate("() => !!(window.__PP_GAME && window.__PP_GAME.champs && window.__PP_GAME.menuCanvas)")
                if listo:
                    break
                await page.wait_for_timeout(500)
            print("juego listo:", listo)
            # esperar el índice asíncrono de campeonatos (fetch secuencial)
            for _ in range(40):
                n = await page.evaluate("() => (window.__PP_GAME.champs.entries||[]).length")
                if n >= 5:
                    break
                await page.wait_for_timeout(500)
            data = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                const lst = g.champs ? g.champs.list() : null;
                return { list: lst, entries: (g.champs.entries||[]).map(e=>({id:e.id,estado:e.estado,error:e.error})),
                         canvas: [g.menuCanvas.width, g.menuCanvas.height] };
            }""")
            print("list():", json.dumps(data["list"], ensure_ascii=False))
            print("entries:", json.dumps(data["entries"], ensure_ascii=False))

            # abrir menú y navegar a CAMPEONATOS
            await page.evaluate("""() => {
                const g = window.__PP_GAME;
                g.menuOpen = true;
                g.menuGroup.visible = true;
                g.menuPage = 'champs';
                g.drawMenu();
            }""")
            await page.wait_for_timeout(800)
            shot1 = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return g.menuCanvas.toDataURL('image/png');
            }""")
            import base64
            with open(OUT + "/champs.png", "wb") as f:
                f.write(base64.b64decode(shot1.split(',')[1]))
            # rects visibles en la página champs
            rects = await page.evaluate("() => window.__PP_GAME.menuRects.map(r=>({id:r.id,y:r.y,h:r.h}))")
            print("rects champs:", json.dumps(rects, ensure_ascii=False))
            # página principal hub
            await page.evaluate("() => { const g=window.__PP_GAME; g.menuPage='main'; g.drawMenu(); }")
            await page.wait_for_timeout(400)
            shot2 = await page.evaluate("() => window.__PP_GAME.menuCanvas.toDataURL('image/png')")
            with open(OUT + "/hub.png", "wb") as f:
                f.write(base64.b64decode(shot2.split(',')[1]))
            print("pageerrors:", errs[:6])
            await browser.close()
    finally:
        os.killpg(os.getpgid(srv.pid), signal.SIGTERM)


asyncio.run(main())
