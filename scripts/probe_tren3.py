#!/usr/bin/env python3
"""Sonda 3: ¿corre el bucle? ¿decae _armT? Reintenta serveTrigger en bucle."""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8934

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
        lt1 = await page.evaluate("() => window.__PP_GAME.lastTime")
        await page.wait_for_timeout(1200)
        lt2 = await page.evaluate("() => window.__PP_GAME.lastTime")
        print("lastTime:", lt1, "->", lt2, "| bucle corre:", (lt2 or 0) > (lt1 or 0))
        # reintento de gatillo cada 0,6 s hasta 14 s
        for i in range(24):
            await page.evaluate("() => window.__PP_GAME.champs.mod.serveTrigger()")
            await page.wait_for_timeout(600)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return {
                    ta: g.champs.mod.testActive(),
                    instr: g._instr ? g._instr.t.toFixed(1) : 'none',
                    msg: g.rules.message.slice(0, 40),
                };
            }""")
            if i % 4 == 0 or st["ta"] or st["instr"] != "none":
                print(f"{(i+1)*0.6:.1f}s", st)
            if st["ta"]:
                break
        print("--- consola oeste/tren ---")
        for m in msgs:
            if "oeste" in m or "tren" in m.lower() or "PAGEERROR" in m or m.startswith("error"):
                print("  ", m[:220])
        await browser.close()

asyncio.run(main())
