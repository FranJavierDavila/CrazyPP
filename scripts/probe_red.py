#!/usr/bin/env python3
"""Sonda 6: tiñe el plano P1 de ROJO y captura — ¿dónde renderiza?"""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8939

class _H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=GAME, **kw)
    def log_message(self, *a):
        pass

JS_CAM = """
window.__camView = (mode) => {
  const g = window.__PP_GAME;
  if (!g || !g.renderer) return 'no-game';
  if (!window.__origRender) {
    window.__origRender = g.renderer.render.bind(g.renderer);
    window.__cam2 = g.camera.clone();
    g.renderer.render = (scene, cam) => window.__origRender(scene, window.__cam2);
  }
  const c = window.__cam2;
  c.fov = g.camera.fov; c.aspect = g.camera.aspect;
  c.near = g.camera.near; c.far = g.camera.far;
  c.updateProjectionMatrix();
  if (mode === 'winL') { c.position.set(0.15, 1.62, 0.35); c.lookAt(-3.05, 1.25, -1.80); }
  else if (mode === 'winR') { c.position.set(-0.15, 1.62, 0.35); c.lookAt(3.05, 1.25, -1.80); }
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
                print(f"bola viva tras {i*0.5:.0f}s")
                break
        await page.wait_for_timeout(5000)
        await page.evaluate(JS_CAM)

        # 1) captura normal
        await page.evaluate("() => window.__camView('winL')")
        await page.wait_for_timeout(600)
        await page.screenshot(path="/tmp/trenshot/red_normal.png")

        # 2) P1 en ROJO puro (sin textura) + sin cielo para aislar
        await page.evaluate("""() => {
            const g = window.__PP_GAME;
            g.scene.traverse((o) => {
                if (!o.isMesh || !o.geometry || !o.geometry.parameters) return;
                const gp = o.geometry.parameters;
                if (gp.width === 530) {
                    o.material.map = null;
                    o.material.color.setHex(0xff0000);
                    o.material.alphaTest = 0;
                    o.material.needsUpdate = true;
                }
                if (gp.width === 400) o.visible = false;   // cielo fuera
            });
        }""")
        await page.wait_for_timeout(600)
        await page.screenshot(path="/tmp/trenshot/red_plain.png")

        # 3) P1 rojo CON textura (color rojo multiplica) — muestra dónde cae el mapa
        await page.evaluate("""() => {
            const g = window.__PP_GAME;
            g.scene.traverse((o) => {
                if (!o.isMesh || !o.geometry || !o.geometry.parameters) return;
                const gp = o.geometry.parameters;
                if (gp.width === 530) {
                    o.material.color.setHex(0xffffff);
                    o.material.alphaTest = 0.5;
                    o.material.needsUpdate = true;
                }
            });
        }""")
        await page.wait_for_timeout(600)
        await page.screenshot(path="/tmp/trenshot/red_textured.png")
        await browser.close()

asyncio.run(main())
