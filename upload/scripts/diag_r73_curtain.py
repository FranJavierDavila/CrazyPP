#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_r73_curtain — telón de teatro en vivo: nace, sigue la cabeza a 2 m,
la esfera traga el mundo, y se desmonta solo. Screenshot del canvas WebGL."""
import asyncio
import base64
import json
import subprocess
import sys
import time
import os
import signal

from playwright.async_api import async_playwright

PORT = 8875
URL = f"http://localhost:{PORT}/game.html"
OUT = "/home/z/my-project/scripts/_r73"


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
            for _ in range(120):
                listo = await page.evaluate("() => !!window.__PP_GAME")
                if listo:
                    break
                await page.wait_for_timeout(500)
            for _ in range(40):
                n = await page.evaluate("() => (window.__PP_GAME.champs.entries||[]).length")
                if n >= 5:
                    break
                await page.wait_for_timeout(500)

            info = await page.evaluate("""async () => {
                const g = window.__PP_GAME;
                localStorage.removeItem('pp_intro_locura');
                g.champs.introPendiente = () => false;
                await g.champs.launch('locura');
                const S = g.champCurtain;
                if (!S) return { telon: false };
                const gp = S.group.position, ep = S.esfera.position;
                return {
                    telon: true,
                    esfera: !!S.esfera,
                    esferaPadre: S.esfera.parent === g.rig,
                    radio: S.esfera.geometry.parameters.radius,
                    backside: S.esfera.material.side === 1,
                    ordenEsfera: S.esfera.renderOrder,
                    ordenPanel: S.mesh.renderOrder,
                    distPanelCabeza: Number(Math.hypot(gp.x - ep.x, gp.z - ep.z).toFixed(3)),
                    panelEnRig: S.group.parent === g.rig,
                    ttl: S.ttl,
                };
            }""")
            print("curtain:", json.dumps(info, ensure_ascii=False))

            await page.wait_for_timeout(600)
            await page.screenshot(path=OUT + "/page.png")
            # el lienzo 2D del telón (la tarjeta), directo
            card = await page.evaluate("""() => {
                const S = window.__PP_GAME.champCurtain;
                return S ? S.cv.toDataURL('image/png') : '';
            }""")
            if card:
                with open(OUT + "/curtain_card.png", "wb") as f:
                    f.write(base64.b64decode(card.split(',')[1]))
            else:
                # ya se desmontó: repíntalo a mano para la foto
                card = await page.evaluate("""() => {
                    const g = window.__PP_GAME;
                    const S = { id:'locura', ttl:'Campeonato de la Locura',
                        cols:g._telonCols('locura'),
                        cv: document.createElement('canvas'), t: 1.3 };
                    S.cv.width = 1024; S.cv.height = 640;
                    S.c = S.cv.getContext('2d');
                    g._pintaCurtain(S, 3, 1.3);
                    return S.cv.toDataURL('image/png');
                }""")
                with open(OUT + "/curtain_card.png", "wb") as f:
                    f.write(base64.b64decode(card.split(',')[1]))

            # desmonte solo
            desmonta = await page.evaluate("""() => new Promise((res) => {
                const t0 = Date.now();
                const iv = setInterval(() => {
                    if (!window.__PP_GAME.champCurtain) { clearInterval(iv); res(Date.now()-t0); }
                    else if (Date.now() - t0 > 16000) { clearInterval(iv); res(-1); }
                }, 250);
            })""")
            print("desmonta en ms:", desmonta)
            print("pageerrors:", errs[:5])
            await browser.close()
    finally:
        os.killpg(os.getpgid(srv.pid), signal.SIGTERM)


asyncio.run(main())
