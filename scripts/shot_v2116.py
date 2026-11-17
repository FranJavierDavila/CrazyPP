#!/usr/bin/env python3
"""v2.116 · Capturas focalizadas: TÚNEL LEJANO (boca aproximándose con luz
normal), INTERIOR oscuro, boca de SALIDA espejada, medallón 5 s y MARCADOR
contador.png del asedio (etapa 2 del pueblo)."""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8936
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
  if (mode === 'pre') {
    c.position.set(0.0, 1.62, 0.40); c.lookAt(3.30, 1.25, -4.80);
  } else if (mode === 'hud') {
    c.position.set(0, 1.55, 0.60); c.lookAt(0, 2.25, -2.55);
  } else if (mode === 'winR') {
    c.position.set(-0.15, 1.62, 0.35); c.lookAt(3.05, 1.25, -1.80);
  } else if (mode === 'pod') {
    c.position.set(0.0, 1.9, -0.85); c.lookAt(0, 0.78, -2.3);
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
                print(f"tren activo tras {(i+1)*0.4:.0f}s")
                break
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m.phase='run'; m._depart(); m.v = 2.6; }")
        await page.wait_for_timeout(800)

        # 0) CALENTAMIENTO del túnel: decodificar tunelboca/tunel ANTES de
        #    fotografiar (el 1er estirón de decode hundía el fps)
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._tunnelT = 0.01; }")
        for i in range(120):
            await page.wait_for_timeout(500)
            ph = await page.evaluate("() => window.__PP_GAME.champs.mod.trenDebug._tunnelPhase")
            if ph in ('in', 'dur'):
                print(f"calentamiento: túnel en {ph} tras {(i+1)*0.5:.0f}s")
                break
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._tunnelPhase='none'; m._tunnelT=999; m.tunelGrp.visible=false; m.tunelOscuro.visible=false; m.tunelOscuro.material.opacity=0; }")
        await page.wait_for_timeout(400)

        # 1) TÚNEL PRE (estado forzado): la boca a 8 m, luz normal
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._tunnelPhase = 'pre'; m._tunnelT2 = 0;
            m._tunelZ = -4.6;
            m.tunelGrp.position.z = -4.6; m.tunelGrp.visible = true;
            m.tunelOscuro.material.opacity = 0; m.tunelOscuro.visible = false;
        }""")
        await page.wait_for_timeout(600)
        st = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            return { ph: m._tunnelPhase, z: m.tunelGrp.position.z.toFixed(2),
                     osc: m.tunelOscuro.material.opacity };
        }""")
        print("tunel pre:", st)
        await page.evaluate("() => window.__camView('pre')")
        await page.screenshot(path=f"{OUT}/v2116_tunel_pre.png")
        print("captura: v2116_tunel_pre (boca entrando por la ventana, luz normal)")

        # 2) DENTRO: oscuridad 20 %
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._tunnelPhase = 'dur'; m._tunnelT2 = 0;
            m.tunelOscuro.material.opacity = 0.80; m.tunelOscuro.visible = true;
        }""")
        await page.wait_for_timeout(600)
        osc = await page.evaluate("() => window.__PP_GAME.champs.mod.trenDebug.tunelOscuro.material.opacity")
        print("oscuridad dentro:", osc)
        await page.evaluate("() => window.__camView('winR')")
        await page.screenshot(path=f"{OUT}/v2116_tunel_dentro.png")
        print("captura: v2116_tunel_dentro (luz al 20 %)")

        # 3) BOCA DE SALIDA espejada EN la ventana
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._tunnelPhase = 'out'; m._tunnelT2 = 0.2;
            m._tunelZ = 26.6;
            m.tunelGrp.position.z = 26.6; m.tunelGrp.visible = true;
        }""")
        await page.wait_for_timeout(600)
        st = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            return { ph: m._tunnelPhase, z: m.tunelGrp.position.z.toFixed(2),
                     bocaOut: (m.tunelGrp.position.z - 26.6).toFixed(2) };
        }""")
        print("boca de salida:", st)
        await page.screenshot(path=f"{OUT}/v2116_tunel_salida.png")
        print("captura: v2116_tunel_salida (boca espejada en la ventana)")

        # 4) MEDALLÓN (5 s en escena)
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._tunnelPhase='none'; m._tunnelT=999; m.tunelGrp.visible=false; m.tunelOscuro.visible=false; m._podT = 0.01; }")
        pod = None
        for i in range(30):
            await page.wait_for_timeout(300)
            pod = await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; return m._pod ? m._pod.tipo : null; }")
            if pod: break
        print("medallón:", pod)
        vida = await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; return m._pod ? m._pod.vida.toFixed(1) : '-'; }")
        print("vida del medallón:", vida, "(esperado ~5.0)")
        await page.evaluate("() => window.__camView('pod')")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/v2116_medallon.png")
        print("captura: v2116_medallon (" + str(pod) + ")")

        # 5) ASEDIO (etapa 2): cerrar el TREN y lanzar el asedio
        await page.evaluate("() => { const c = window.__PP_OESTE.ctrl(); if (c && c._tren) c._endTren(true); }")
        await page.wait_for_timeout(2500)
        await page.evaluate("() => localStorage.setItem('pp_champ_oeste_stage','2')")
        launched = False
        for i in range(60):
            await page.evaluate("() => window.__PP_OESTE.ctrl().replayLaunch(1)")
            await page.wait_for_timeout(450)
            if await page.evaluate("() => { const c = window.__PP_OESTE.ctrl(); return !!(c && c._asedio); }"):
                launched = True
                print(f"asedio activo tras {(i+1)*0.45:.0f}s")
                break
        if not launched:
            print("replayLaunch(1) no arrancó el asedio: recarga completa")
            await page.reload()
            await page.wait_for_timeout(3500)
            await page.evaluate("() => { window.__pp2DPlay = true; const ov = document.getElementById('overlay'); if (ov) ov.style.display='none'; }")
            await page.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
            await page.wait_for_timeout(4000)
        # esperar a que el cartel de OLEADA termine (fase 'play')
        for i in range(80):
            await page.wait_for_timeout(500)
            ph = await page.evaluate("() => { const c = window.__PP_OESTE.ctrl(); return c && c._asedio ? c._asedio.phase : '-'; }")
            if ph in ('play', 'reveal'):
                print(f"asedio en {ph} tras {(i+1)*0.5:.0f}s")
                break
        marc = await page.evaluate("""() => {
            const ctrl = window.__PP_OESTE && window.__PP_OESTE.ctrl &&
                         window.__PP_OESTE.ctrl();
            if (!ctrl || !ctrl._asedio) return 'sin-asedio';
            const a = ctrl._asedio;
            return a && a._hud ? { wave: a.wave, marc: a._marc(),
                                   vis: a._hud.group.visible } : 'sin-hud';
        }""")
        print("marcador asedio:", marc)
        await page.evaluate("() => window.__camView('hud')")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/v2116_asedio_marcador.png")
        print("captura: v2116_asedio_marcador")
        print("errores pagina:", len(errors), errors[:3])
        await browser.close()

asyncio.run(main())
