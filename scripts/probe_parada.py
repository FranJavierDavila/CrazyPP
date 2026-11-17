#!/usr/bin/env python3
"""Sonda rápida: ¿por qué el arte PARADA no se aplica en el banco?"""
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
        ])
        page = await browser.new_page(viewport={"width": 640, "height": 400})
        fails = []
        page.on("response", lambda r: fails.append((r.status, r.url))
                if r.status >= 400 else None)
        await page.goto(f"http://127.0.0.1:{PORT}/index.html")
        await page.wait_for_timeout(2000)
        await page.evaluate("""() => {
            localStorage.setItem('pp_player_name', 'foro3d');
            localStorage.setItem('pp_champ_oeste_stage', '4');
        }""")
        await page.reload()
        await page.wait_for_timeout(3000)
        await page.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
        await page.wait_for_timeout(4000)
        for i in range(200):
            await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(3)")
            await page.wait_for_timeout(400)
            st = await page.evaluate("() => window.__PP_GAME.champs.mod.testActive()")
            if st: break
        await page.wait_for_timeout(8000)
        out = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            if (!m) return { inst: false };
            return {
              inst: true,
              try: JSON.stringify(m._paradaTry || {}),
              texs: Object.keys(m._paradaTex || {}),
              estArt: m.estArt ? m.estArt.map(a => ({
                vis: a.visible, map: !!a.material.map,
                matVis: m.station ? m.station.visible : null })) : null,
              parts: m._stationParts ? m._stationParts.filter(p=>p.visible).length : -1,
            };
        }""")
        print("estado:", out)
        # ¿la textura carga por fetch directo?
        r = await page.evaluate("""async () => {
            const u = new URL('./assets/PARADA1.png',
              new URL('championships/oeste/index.js', location.href)).href;
            try { const rr = await fetch(u); return u + ' → ' + rr.status; }
            catch (e) { return u + ' → ERR ' + e.message; }
        }""")
        print("fetch:", r)
        print("recursos >=400:", fails[:6])
        await browser.close()

asyncio.run(main())
