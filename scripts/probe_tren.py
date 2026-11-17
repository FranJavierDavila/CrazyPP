#!/usr/bin/env python3
"""Sonda: ¿por qué no arranca la etapa del tren en 2D?"""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8932

class _H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=GAME, **kw)
    def log_message(self, *a):
        pass

async def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 900, "height": 560})
        msgs = []
        page.on("console", lambda m: msgs.append(m.type + ": " + m.text))
        page.on("pageerror", lambda e: msgs.append("PAGEERROR: " + str(e)))
        await page.goto(f"http://127.0.0.1:{PORT}/index.html")
        await page.wait_for_timeout(2200)
        await page.evaluate("""() => {
            localStorage.setItem('pp_player_name', 'foro3d');
            localStorage.setItem('pp_champ_oeste_stage', '4');
        }""")
        await page.reload()
        await page.wait_for_timeout(3200)
        await page.evaluate("""() => {
            window.__pp2DPlay = true;
            const ov = document.getElementById('overlay');
            if (ov) ov.style.display = 'none';
        }""")
        await page.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
        await page.wait_for_timeout(5000)
        print("replayMap:", await page.evaluate(
            "() => JSON.stringify(window.__PP_GAME.champs.mod.replayMap() ? {ok:1, maxIdx: window.__PP_GAME.champs.mod.replayMap().maxIdx} : null)"))
        print("testActive antes:", await page.evaluate(
            "() => window.__PP_GAME.champs.mod.testActive()"))
        await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(3)")
        for i in range(12):
            await page.wait_for_timeout(1000)
            st = await page.evaluate("""() => ({
                ta: window.__PP_GAME.champs.mod.testActive(),
                msg: window.__PP_GAME.rules.message,
                ballY: +(window.__PP_GAME.ball ? window.__PP_GAME.ball.pos.y : -9).toFixed(2),
                ballZ: +(window.__PP_GAME.ball ? window.__PP_GAME.ball.pos.z : -9).toFixed(2),
            })""")
            print(f"t+{i+1}s", st)
        print("--- consola (últimos 25) ---")
        for m in msgs[-25:]:
            print("  ", m[:200])
        await browser.close()

asyncio.run(main())
