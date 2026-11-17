#!/usr/bin/env python3
"""Sonda mínima: ¿qué pasa al lanzar oeste etapa 4?"""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8937

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
        ])
        page = await browser.new_page(viewport={"width": 900, "height": 520})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append("console:" + m.text) if m.type == "error" else None)
        await page.goto(f"http://127.0.0.1:{PORT}/index.html")
        await page.wait_for_timeout(2500)
        await page.evaluate("""() => {
            localStorage.setItem('pp_player_name', 'foro3d');
            localStorage.setItem('pp_champ_oeste_stage', '4');
        }""")
        await page.reload()
        await page.wait_for_timeout(3500)
        await page.evaluate("""() => {
            window.__pp2DPlay = true;
            const ov = document.getElementById('overlay');
            if (ov) ov.style.display = 'none';
        }""")
        await page.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
        await page.wait_for_timeout(6000)
        st = await page.evaluate("""() => {
            const g = window.__PP_GAME;
            const ch = g && g.champs;
            return {
              game: !!g, champs: !!ch, mod: ch ? !!ch.mod : null,
              active: ch && ch.mod ? ch.mod.testActive() : null,
              stage: ch && ch.mod ? (ch.mod.testStage ? ch.mod.testStage() : '-') : null,
              keys: ch ? Object.keys(ch).slice(0, 20) : null,
            };
        }""")
        print("estado:", st)
        for i in range(30):
            await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(4)")
            await page.wait_for_timeout(400)
            act = await page.evaluate("() => window.__PP_GAME.champs.mod.testActive()")
            if act:
                print(f"activo tras {(i+1)*0.4:.0f}s")
                break
        st2 = await page.evaluate("""() => {
            const ch = window.__PP_GAME.champs;
            return { active: ch.mod.testActive(),
                     tren: !!(ch.mod.trenDebug),
                     phase: ch.mod.trenDebug ? ch.mod.trenDebug.phase : null };
        }""")
        print("estado2:", st2)
        print("errores:", len(errors), errors[:5])
        await browser.close()

asyncio.run(main())
