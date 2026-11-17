#!/usr/bin/env python3
"""Sonda 8: bandas de color en el pano -> ¿dónde caen las filas del lienzo?"""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8941

class _H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=GAME, **kw)
    def log_message(self, *a):
        pass

JS_CAM = """
window.__camView = (mode) => {
  const g = window.__PP_GAME;
  if (!window.__origRender) {
    window.__origRender = g.renderer.render.bind(g.renderer);
    window.__cam2 = g.camera.clone();
    g.renderer.render = (scene, cam) => window.__origRender(scene, window.__cam2);
  }
  const c = window.__cam2;
  c.fov = g.camera.fov; c.aspect = g.camera.aspect; c.updateProjectionMatrix();
  if (mode === 'winL') { c.position.set(0.15, 1.62, 0.35); c.lookAt(-3.05, 1.25, -1.80); }
  return 'ok';
};
"""

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
        for i in range(240):
            await page.wait_for_timeout(500)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return { ta: g.champs.mod.testActive(),
                         by: +(g.ball ? g.ball.pos.y : -9).toFixed(2) };
            }""")
            if st["ta"] and st["by"] > 1.2:
                break
        await page.wait_for_timeout(4000)
        await page.evaluate(JS_CAM)
        await page.evaluate("() => window.__camView('winL')")
        await page.wait_for_timeout(400)

        # bandas de diagnóstico en el MISMO canvas del pano (6 bandas)
        out = await page.evaluate("""() => {
            const g = window.__PP_GAME;
            let tex = null;
            g.scene.traverse((o) => {
                if (tex || !o.isMesh || !o.geometry || !o.geometry.parameters) return;
                if (o.geometry.parameters.width === 530 && o.material.map) tex = o.material.map;
            });
            if (!tex) return 'sin-tex';
            const cv = tex.image;
            const c = cv.getContext('2d');
            const H = cv.height, cols = ['#f00', '#0f0', '#00f', '#ff0', '#f0f', '#0ff'];
            for (let i = 0; i < 6; i++) {
                c.fillStyle = cols[i];
                c.fillRect(0, i * H / 6, cv.width, H / 6);
            }
            tex.needsUpdate = true;
            return 'bandas-ok ' + cv.width + 'x' + H + ' flipY=' + tex.flipY;
        }""")
        print(out)
        await page.wait_for_timeout(1200)
        await page.screenshot(path="/tmp/trenshot/bandas.png")
        await browser.close()

asyncio.run(main())
