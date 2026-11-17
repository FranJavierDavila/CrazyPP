#!/usr/bin/env python3
"""Sonda 7: maxTextureSize + experimento de textura nueva sobre el pano."""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8940

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
        await page.wait_for_timeout(5000)
        await page.evaluate(JS_CAM)
        await page.evaluate("() => window.__camView('winL')")
        await page.wait_for_timeout(500)

        # estado
        info = await page.evaluate("""() => {
            const g = window.__PP_GAME;
            const r = g.renderer;
            const out = { maxTex: r.capabilities.maxTextureSize, planes: [] };
            g.scene.traverse((o) => {
                if (!o.isMesh || !o.geometry || !o.geometry.parameters) return;
                if (o.geometry.parameters.width === 530 && o.material.map) {
                    const im = o.material.map.image;
                    out.planes.push({
                        img: im ? im.width + 'x' + im.height : 'null',
                        ver: o.material.map.version,
                        src: o.material.map.source ? o.material.map.source.uuid.slice(0, 8) : '-',
                    });
                }
            });
            return out;
        }""")
        print("estado:", info)
        await page.screenshot(path="/tmp/trenshot/tex_antes.png")

        # EXPERIMENTO: textura NUEVA desde el mismo canvas
        await page.evaluate("""() => {
            const g = window.__PP_GAME;
            let cv = null;
            g.scene.traverse((o) => {
                if (cv || !o.isMesh || !o.geometry || !o.geometry.parameters) return;
                if (o.geometry.parameters.width === 530 && o.material.map &&
                    o.material.map.image && o.material.map.image.width > 3000) {
                    cv = o.material.map.image;
                }
            });
            if (!cv) return 'sin-canvas';
            g.scene.traverse((o) => {
                if (!o.isMesh || !o.geometry || !o.geometry.parameters) return;
                if (o.geometry.parameters.width === 530 && o.material.map) {
                    const nt = new (o.material.map.constructor)(cv);
                    nt.colorSpace = o.material.map.colorSpace;
                    nt.wrapS = THREE_Wrap || 1000;
                    nt.wrapS = o.material.map.wrapS; nt.wrapT = o.material.map.wrapT;
                    nt.anisotropy = o.material.map.anisotropy;
                    nt.repeat.copy(o.material.map.repeat);
                    o.material.map = nt;
                    o.material.needsUpdate = true;
                }
            });
            return 'swap-ok ' + cv.width + 'x' + cv.height;
        }""")
        await page.wait_for_timeout(1200)
        await page.screenshot(path="/tmp/trenshot/tex_nueva.png")

        # EXPERIMENTO 2: canvas a la mitad (2048) — ¿pasa el límite?
        await page.evaluate("""() => {
            const g = window.__PP_GAME;
            let cv = null;
            g.scene.traverse((o) => {
                if (cv || !o.isMesh || !o.geometry || !o.geometry.parameters) return;
                if (o.geometry.parameters.width === 530 && o.material.map &&
                    o.material.map.image && o.material.map.image.width > 3000) {
                    cv = o.material.map.image;
                }
            });
            if (!cv) return 'sin-canvas';
            const cv2 = document.createElement('canvas');
            cv2.width = 2048; cv2.height = Math.round(cv.height * 2048 / cv.width);
            const c = cv2.getContext('2d');
            c.drawImage(cv, 0, 0, cv2.width, cv2.height);
            g.scene.traverse((o) => {
                if (!o.isMesh || !o.geometry || !o.geometry.parameters) return;
                if (o.geometry.parameters.width === 530 && o.material.map) {
                    const nt = new (o.material.map.constructor)(cv2);
                    nt.colorSpace = o.material.map.colorSpace;
                    nt.wrapS = o.material.map.wrapS; nt.wrapT = o.material.map.wrapT;
                    nt.anisotropy = o.material.map.anisotropy;
                    o.material.map = nt;
                    o.material.needsUpdate = true;
                }
            });
            return 'mitad-ok';
        }""")
        await page.wait_for_timeout(1200)
        await page.screenshot(path="/tmp/trenshot/tex_2048.png")
        await browser.close()

asyncio.run(main())
