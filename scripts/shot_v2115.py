#!/usr/bin/env python3
"""v2.115 · Capturas focalizadas: ESTACIÓN del artista en el andén (intro),
medallón de superpoder forzado y TÚNEL oscuro forzado."""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8935
OUT = "/tmp/trenshot"

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
  if (mode === 'estL') {
    c.position.set(0.2, 1.62, 0.35); c.lookAt(-3.4, 1.35, -1.4);
  } else if (mode === 'estR') {
    c.position.set(-0.2, 1.62, 0.35); c.lookAt(3.4, 1.35, -1.4);
  } else if (mode === 'pod') {
    c.position.set(0.0, 1.9, -0.85); c.lookAt(0, 0.78, -2.3);
  } else if (mode === 'winR') {
    c.position.set(-0.15, 1.62, 0.35); c.lookAt(3.05, 1.25, -1.80);
  } else if (mode === 'pir') {
    c.position.set(0.0, 1.62, 0.55); c.lookAt(0, 1.05, -4.62);
  }
  return 'ok';
};
"""

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
        await page.wait_for_timeout(5000)
        await page.evaluate(JS_CAM)
        for i in range(200):
            await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(3)")
            await page.wait_for_timeout(400)
            if await page.evaluate("() => window.__PP_GAME.champs.mod.testActive()"):
                print(f"etapa activa tras {(i+1)*0.4:.0f}s")
                break
        # 1) INTRO: el tren DETENIDO en BRAVOS → estación del artista visible
        for i in range(120):
            await page.wait_for_timeout(500)
            intro = await page.evaluate("""() => {
                const m = window.__PP_GAME.champs.mod.trenDebug;
                return m && m.phase === 'intro' && m.station && m.station.visible;
            }""")
            if intro:
                break
        await page.wait_for_timeout(2500)      # textura PARADA1 aplicada
        await page.evaluate("() => window.__camView('estR')")
        await page.screenshot(path=f"{OUT}/v2115_estacion_der.png")
        print("captura: v2115_estacion_der (intro en BRAVOS)")
        await page.evaluate("() => window.__camView('estL')")
        await page.screenshot(path=f"{OUT}/v2115_estacion_izq.png")
        print("captura: v2115_estacion_izq")

        # 2) MEDALLÓN forzado en la mesa rival
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m.phase = 'run'; m._podT = 0.01;
        }""")
        for i in range(30):
            await page.wait_for_timeout(300)
            pod = await page.evaluate("""() => {
                const m = window.__PP_GAME.champs.mod.trenDebug;
                return m._pod ? m._pod.tipo : null;
            }""")
            if pod: break
        print("medallón:", pod)
        await page.evaluate("() => window.__camView('pod')")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/v2115_medallon.png")
        print("captura: v2115_medallon (" + str(pod) + ")")

        # 3) TÚNEL forzado: fundido + oscuridad + pared del artista
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._tunnelT = 0.01; m.v = 2.6;
        }""")
        await page.wait_for_timeout(2600)      # boca cruzando + oscureciendo
        await page.evaluate("() => window.__camView('winR')")
        await page.screenshot(path=f"{OUT}/v2115_tunel_entrada.png")
        print("captura: v2115_tunel_entrada")
        await page.wait_for_timeout(2500)      # dentro: luz 20 %
        osc = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            return m.tunelOscuro.material.opacity;
        }""")
        print("oscuridad dentro:", osc)
        await page.screenshot(path=f"{OUT}/v2115_tunel_dentro.png")
        print("captura: v2115_tunel_dentro (luz al 20 %)")
        print("errores pagina:", len(errors), errors[:3])
        await browser.close()

asyncio.run(main())
