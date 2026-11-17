#!/usr/bin/env python3
"""Sonda parallax: ¿se pidieron/cargaron los PNG p1? ¿el swap del pano corrió?"""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8935

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
        page = await browser.new_page(viewport={"width": 800, "height": 480})
        msgs = []
        page.on("console", lambda m: msgs.append(m.type + ": " + m.text))
        await page.goto(f"http://127.0.0.1:{PORT}/index.html")
        await page.wait_for_timeout(2000)
        await page.evaluate("""() => {
            localStorage.setItem('pp_player_name', 'foro3d');
            localStorage.setItem('pp_champ_oeste_stage', '4');
        }""")
        await page.reload()
        await page.wait_for_timeout(3000)
        await page.evaluate("""() => {
            window.__pp2DPlay = true;
            const ov = document.getElementById('overlay');
            if (ov) ov.style.display = 'none';
        }""")
        await page.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
        await page.wait_for_timeout(4000)
        for i in range(60):
            await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(3)")
            await page.wait_for_timeout(400)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return { ta: g.champs.mod.testActive(),
                         instr: g._instr ? 'si' : 'none' };
            }""")
            if st["ta"] or st["instr"] == "si":
                break
        print("esperando saque…")
        for i in range(240):
            await page.wait_for_timeout(500)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return { ta: g.champs.mod.testActive(),
                         by: +(g.ball ? g.ball.pos.y : -9).toFixed(2) };
            }""")
            if st["ta"] and st["by"] > 0.95:
                print(f"bola viva tras {i*0.5:.0f}s")
                break
        await page.wait_for_timeout(4000)

        # recursos parallax pedidos al servidor
        res = await page.evaluate("""() => performance.getEntriesByType('resource')
            .map(r => r.name)
            .filter(n => n.includes('parallax/'))
            .map(n => n.split('/').pop())""")
        print("recursos parallax:", len(res))
        p1 = [r for r in res if r.startswith('p1_')]
        print("p1 cargados:", p1)

        # ¿cúantos drawImage/canvas 4344 hay? Sondeo indirecto: buscamos el
        # textura P1 via el material de un mesh con ancho 530 en la escena.
        info = await page.evaluate("""() => {
            const g = window.__PP_GAME;
            const out = { bg: String(g.scene.background), pano: [] };
            g.scene.traverse((o) => {
                if (o.isMesh && o.geometry && o.geometry.parameters &&
                    o.geometry.parameters.width === 530) {
                    const m = o.material;
                    out.pano.push({
                        imgType: m.map && m.map.image ? m.map.image.constructor.name : 'null',
                        w: m.map && m.map.image ? m.map.image.width : 0,
                        h: m.map && m.map.image ? m.map.image.height : 0,
                        alphaTest: m.alphaTest, transparent: m.transparent,
                        visible: o.visible, pos: [o.position.x.toFixed(0), o.position.y.toFixed(0)],
                    });
                }
            });
            return out;
        }""")
        print("background:", info["bg"])
        for pn in info["pano"]:
            print("plano P1:", pn)
        await browser.close()

asyncio.run(main())
