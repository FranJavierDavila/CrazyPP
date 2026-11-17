#!/usr/bin/env python3
"""v2.113 · Banco visual del ROBO v2: lado forzado y tiempos justos."""
import asyncio, os, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8941
OUT = "/tmp/trenshot"
os.makedirs(OUT, exist_ok=True)

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
                walk(mod, 0); window.__act = act;
                return act ? act.phase : 'no';
            }""")
            if st == 'run':
                print("fase run en", i * 0.5, "s")
                break
        # jinete FORZADO en la ventana IZQUIERDA (la cámara mira ahí)
        await page.evaluate("""() => {
            const act = window.__act;
            if (act._fjState !== 'off') act._fjGone();
            act._fjSpawn();
            act._fjSide = -1;
            act._fjState = 'ventana'; act._fjAtk = true;
            act._fjZ = -1.82; act._fjT = 0.2;
            act._fjDianaPos(); act.fjDiana.visible = true;
            act._fjSetFrame('dispara'); act._fjPose(0.03);
        }""")
        await page.wait_for_timeout(120)
        await page.screenshot(path=f"{OUT}/jinete_ventana2.png")
        print("captura: jinete_ventana2")
        # ROBO: pila + robo y captura a ~0,45 s de juego (congelando el bucle real)
        await page.evaluate("""() => {
            const act = window.__act;
            const V = act.cubos[0].mesh.position.constructor;
            act._lanzaLingote(new V(-0.2, 0.78, -2.05));
            act._lanzaLingote(new V(0.0, 0.78, -2.43));
            for (const it of act.ingotes) { it.t = it.T; it.volando = true; }
            act.fxStep(1/60);
            act._robaLingote();
        }""")
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
            c.position.set(0.4, 1.7, 0.1);
            c.lookAt(0.0, 1.6, -2.35);
        }""")
        # avanza SOLO el sintético (el bucle real sigue; con SwiftShader es lento)
        for k in range(16):
            await page.evaluate("() => window.__act.fxStep(1/60);")
            await page.wait_for_timeout(14)
        await page.screenshot(path=f"{OUT}/robo_levitando2.png")
        print("captura: robo_levitando2 — estado:",
              await page.evaluate("""() => {
                  const it = window.__act.ingotes.find((i) => i.robado);
                  if (!it) return 'sin-robo';
                  return 'robo=' + it.robo + ' y=' + it.mesh.position.y.toFixed(2) +
                    ' x=' + it.mesh.position.x.toFixed(2);
              }"""))
        print("errores pagina:", len(errs))
        await browser.close()

asyncio.run(main())
