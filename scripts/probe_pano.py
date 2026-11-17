#!/usr/bin/env python3
"""Sonda 4: contenido del canvas cosido P1 + traza del bote v2.112."""
import asyncio, threading, json
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
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 760, "height": 460})
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
            window.__ballLog = [];
            const loop = () => {
                try {
                    const g = window.__PP_GAME;
                    if (g && g.ball) window.__ballLog.push([
                        performance.now()/1000, +g.ball.pos.y.toFixed(3),
                        +g.ball.vel.y.toFixed(2), +g.ball.pos.z.toFixed(2)]);
                } catch (e) {}
                requestAnimationFrame(loop);
            };
            requestAnimationFrame(loop);
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
        for i in range(300):
            await page.wait_for_timeout(500)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return { ta: g.champs.mod.testActive(),
                         by: +(g.ball ? g.ball.pos.y : -9).toFixed(2) };
            }""")
            if st["ta"] and st["by"] > 1.2:
                print(f"bola alta ({st['by']}) tras {i*0.5:.0f}s")
                break
        await page.wait_for_timeout(5000)

        # contenido del canvas cosido P1 (muestreo de filas)
        pano = await page.evaluate("""() => {
            const g = window.__PP_GAME;
            let found = null;
            g.scene.traverse((o) => {
                if (found || !o.isMesh || !o.geometry || !o.geometry.parameters) return;
                if (o.geometry.parameters.width === 530 && o.material.map) {
                    const im = o.material.map.image;
                    if (im && im.width === 4344) found = im;
                }
            });
            if (!found) return 'sin-canvas-4344';
            const cv = document.createElement('canvas');
            cv.width = found.width; cv.height = found.height;
            const c = cv.getContext('2d');
            c.drawImage(found, 0, 0);
            const rows = [];
            for (const yy of [0, 100, 200, 260, 300, 350, 420, 500]) {
                const d = c.getImageData(2000, yy, 1, 1).data;
                rows.push([yy, d[0], d[1], d[2], d[3]]);
            }
            return { w: found.width, h: found.height, rows };
        }""")
        print("pano:", json.dumps(pano))

        # trazas del bote: ápices
        log = await page.evaluate("() => window.__ballLog || []")
        with open('/tmp/trenshot/bote_v2112.json', 'w') as f:
            json.dump(log[-1200:], f)
        apex = []
        for i in range(2, len(log) - 2):
            y0, y1, y2 = log[i-1][1], log[i][1], log[i+1][1]
            if y1 >= y0 and y1 >= y2 and y1 > 1.0:
                if not apex or log[i][0] - apex[-1][0] > 0.3:
                    apex.append((round(log[i][0], 1), y1, log[i][3]))
        print("ápices (t, y, z):")
        for a in apex[:18]:
            print("   ", a)
        await browser.close()

asyncio.run(main())
