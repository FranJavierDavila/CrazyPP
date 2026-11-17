#!/usr/bin/env python3
"""Sonda 2: stage=5 + replayLaunch(3) para ver si _startTren llega a correr."""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8933

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
            localStorage.setItem('pp_champ_oeste_stage', '5');
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
        await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(3)")
        for i in range(22):
            await page.wait_for_timeout(1000)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return {
                    ta: g.champs.mod.testActive(),
                    msg: g.rules.message,
                    instr: g._instr ? ('banner t=' + g._instr.t.toFixed(1)) : 'none',
                    ballY: +(g.ball ? g.ball.pos.y : -9).toFixed(2),
                };
            }""")
            print(f"t+{i+1}s", st)
            if st["ta"] and st["ballY"] > 0.9:
                break
        print("--- consola warnings/errores ---")
        for m in msgs:
            if m.startswith("warning") or m.startswith("PAGEERROR") or "oeste" in m or "tren" in m.lower():
                print("  ", m[:220])
        await browser.close()

asyncio.run(main())
