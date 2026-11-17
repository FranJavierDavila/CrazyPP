#!/usr/bin/env python3
"""v2.113 · Banco visual del ROBO: lingote levitando en rojo sobre la mesa
rival y captura del jinete con la diana en la ventana."""
import asyncio, os, threading, base64
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8939
OUT = "/tmp/trenshot"
os.makedirs(OUT, exist_ok=True)

class _H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=GAME, **kw)
    def log_message(self, *a):
        pass

JS_CAM = """() => {
  const g = window.__PP_GAME;
  if (!window.__origRender) {
    window.__origRender = g.renderer.render.bind(g.renderer);
    window.__cam2 = g.camera.clone();
    g.renderer.render = (scene, cam) => window.__origRender(scene, window.__cam2);
  }
  const c = window.__cam2;
  c.fov = g.camera.fov; c.aspect = g.camera.aspect;
  c.near = g.camera.near; c.far = g.camera.far;
  c.updateProjectionMatrix();
  return 'ok';
}"""

async def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 900, "height": 520})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
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
        for i in range(80):
            await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(3)")
            await page.wait_for_timeout(400)
            if await page.evaluate("() => window.__PP_GAME.champs.mod.testActive()"): break
        # espera a que el tren CORRA (fase run, tras cartel+intro)
        for i in range(300):
            await page.wait_for_timeout(500)
            st = await page.evaluate("""() => {
                const mod = window.__PP_GAME.champs.mod;
                let act = null;
                const walk = (o, d) => {
                    if (!o || d > 4 || act) return;
                    if (o.cubos && o.group) { act = o; return; }
                    for (const k of Object.keys(o)) { try { walk(o[k], d + 1); } catch (e) {} }
                };
                window.__act = act; walk(mod, 0);
                window.__act = act;
                return act ? act.phase : 'no';
            }""")
            if st == 'run':
                print("fase run alcanzada en", i * 0.5, "s")
                break
        # monta el robo: 2 lingotes en la pila y robo del último
        await page.evaluate("""() => {
            const act = window.__act;
            const T = act.constructor;
            // THREE via el mesh del primer cubo
            act._lanzaLingote(new (act.cubos[0].mesh.position.constructor)(
                -0.2, 0.78, -2.05));
            act._lanzaLingote(new (act.cubos[0].mesh.position.constructor)(
                0.0, 0.78, -2.43));
            for (const it of act.ingotes) { it.t = it.T; it.volando = true; }
        }""")
        await page.wait_for_timeout(300)
        await page.evaluate("() => { window.__act.fxStep(1/60); }")
        await page.evaluate("() => { window.__act._robaLingote(); }")
        # cámara sobre la pila del rival
        await page.evaluate("""() => {
            const g = window.__PP_GAME;
            if (!window.__origRender) {
                window.__origRender = g.renderer.render.bind(g.renderer);
                window.__cam2 = g.camera.clone();
                g.renderer.render = (scene, cam) => window.__origRender(scene, window.__cam2);
            }
            const c = window.__cam2;
            c.fov = g.camera.fov; c.aspect = g.camera.aspect;
            c.near = g.camera.near; c.far = g.camera.far;
            c.updateProjectionMatrix();
            c.position.set(0.4, 1.75, 0.2);
            c.lookAt(-0.05, 1.45, -2.3);
        }""")
        # espera a mitad de levitación (~0,55 s de juego) y captura
        for k in range(30):
            await page.evaluate("() => window.__act.fxStep(1/60); window.__act.step(1/60);")
            await page.wait_for_timeout(18)
        await page.screenshot(path=f"{OUT}/robo_levitando.png")
        print("captura: robo_levitando")
        # y 0,5 s más tarde (salida por la ventana)
        for k in range(30):
            await page.evaluate("() => window.__act.fxStep(1/60); window.__act.step(1/60);")
            await page.wait_for_timeout(18)
        await page.evaluate("""() => {
            const c = window.__cam2;
            c.position.set(0.0, 1.62, 0.35);
            c.lookAt(-3.05, 1.25, -1.80);
        }""")
        await page.screenshot(path=f"{OUT}/robo_salida.png")
        print("captura: robo_salida")
        # jinete en ventana (forzar spawn + ida instantánea)
        await page.evaluate("""() => {
            const act = window.__act;
            act._fjSpawn();
            act._fjState = 'ventana'; act._fjAtk = true;
            act._fjZ = -1.82; act._fjT = 0.1;
            act._fjDianaPos(); act.fjDiana.visible = true;
            act._fjSetFrame('dispara'); act._fjPose(0.03);
        }""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/jinete_ventana.png")
        print("captura: jinete_ventana")
        print("errores pagina:", len(errs))
        for e in errs[:5]:
            print("  ", e[:150])
        await browser.close()

asyncio.run(main())
