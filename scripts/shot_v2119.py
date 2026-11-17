#!/usr/bin/env python3
"""v2.119 · Capturas: ESTACIÓN PARADA1 SUBIDA (cuerpo en la ventana), TÚNEL
pared DERECHA cosida por u=1 (entrada/salida) + pared izquierda, INDIO
CABALGANTE en la ventana con su mirilla, y el HUD con el CHIP DE PUNTOS."""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8939
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
    c.position.set(0.0, 1.62, 0.40); c.lookAt(3.30, 1.40, -4.80);
  } else if (mode === 'preL') {
    c.position.set(0.0, 1.62, 0.40); c.lookAt(-3.30, 1.40, -4.80);
  } else if (mode === 'hud') {
    c.position.set(0, 1.55, 0.60); c.lookAt(0, 2.30, -2.55);
  } else if (mode === 'winR') {
    c.position.set(-0.15, 1.62, 0.35); c.lookAt(3.05, 1.55, -1.80);
  } else if (mode === 'winL') {
    c.position.set(0.15, 1.62, 0.35); c.lookAt(-3.05, 1.55, -1.80);
  } else if (mode === 'estacion') {
    c.position.set(0.0, 1.62, 0.40); c.lookAt(3.60, 1.80, -1.40);
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

        # 0) VERIFICACIÓN EN VIVO: bocas por pared, estación subida, HUD, indio
        geo = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            const bocas = m.tunelGrp.children.filter(c => c.userData && c.userData.boca);
            const inB = bocas.filter(c => Math.abs(c.position.z) < 1e-6);
            const outB = bocas.filter(c => c.position.z < -1);
            const izq = (c) => c.position.x < 0;
            const hud = m._hud;
            return {
                estY: m.estArt.map(e => +e.position.y.toFixed(3)),
                inL: inB.find(izq)?.scale.x, inR: inB.find(c => !izq(c))?.scale.x,
                outL: outB.find(izq)?.scale.x, outR: outB.find(c => !izq(c))?.scale.x,
                pool: m._indPool ? m._indPool.length : 0,
                hudPts: hud ? hud.pts : null,
            };
        }""")
        print("verificación en vivo:", geo)

        # 1) ESTACIÓN DE SALIDA: PARADA1 SUBIDA (cuerpo del edificio en la ventana)
        await page.evaluate("() => window.__camView('estacion')")
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"{OUT}/v2119_estacion_parada1.png")
        print("captura: v2119_estacion_parada1 (PARADA1 a y 1.85)")

        # preparar el vagón en marcha
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m.phase='run'; m._depart(); m.v = 2.6; }")
        await page.wait_for_timeout(800)

        # 2) TÚNEL PRE: boca de ENTRADA por la pared DERECHA (u=1 → arco a la banda)
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._tunnelPhase = 'pre'; m._tunnelT2 = 0;
            m._tunelZ = -4.6;
            m.tunelGrp.position.z = -4.6; m.tunelGrp.visible = true;
            m.tunelOscuro.material.opacity = 0; m.tunelOscuro.visible = false;
        }""")
        await page.wait_for_timeout(600)
        await page.evaluate("() => window.__camView('pre')")
        await page.screenshot(path=f"{OUT}/v2119_tunel_pre_der.png")
        print("captura: v2119_tunel_pre_der (entrada DER espejada-textura, arco A la banda)")
        await page.evaluate("() => window.__camView('preL')")
        await page.screenshot(path=f"{OUT}/v2119_tunel_pre_izq.png")
        print("captura: v2119_tunel_pre_izq (entrada IZQ normal)")

        # 3) BOCA DE SALIDA en ambas paredes (DER normal-textura, IZQ espejada)
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._tunnelPhase = 'out'; m._tunnelT2 = 0.2;
            m._tunelZ = 27.8;
            m.tunelGrp.position.z = 27.8; m.tunelGrp.visible = true;
            m.tunelOscuro.material.opacity = 0.30; m.tunelOscuro.visible = true;
        }""")
        await page.wait_for_timeout(600)
        await page.evaluate("() => window.__camView('winR')")
        await page.screenshot(path=f"{OUT}/v2119_tunel_salida_der.png")
        await page.evaluate("() => window.__camView('winL')")
        await page.screenshot(path=f"{OUT}/v2119_tunel_salida_izq.png")
        print("capturas: v2119_tunel_salida_der/izq")
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._tunnelPhase='none'; m.tunelGrp.visible=false; m.tunelOscuro.visible=false; m.tunelOscuro.material.opacity=0; }")

        # 4) EL INDIO CABALGANTE: grupo de 3 forzado, cabalgando en la ventana
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._fjState = 'off'; m._indCount = 0; m._indNext = 9999;
            m._indSpawn();
            if (m._inds.length < 3) {           // fuerza el trío para la foto
                while (m._inds.length < 3 && m._indCount < 9) m._indSpawn();
            }
        }""")
        await page.wait_for_timeout(2400)       # cabalgan hasta la ventana (1.6 s)
        ind = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            return { n: m._inds.length,
                     diana: m._inds.map(r => r.diana.visible),
                     y: m._inds.map(r => +r.grp.position.y.toFixed(2)),
                     side: m._inds.map(r => r.side) };
        }""")
        print("indios en pantalla:", ind)
        side = ind["side"][0] if ind["n"] else 1
        view = 'winL' if side < 0 else 'winR'
        await page.evaluate("() => window.__camView('%s')" % view)
        await page.wait_for_timeout(300)
        await page.screenshot(path=f"{OUT}/v2119_indio_ventana.png")
        print("captura: v2119_indio_ventana (grupo con mirilla)")
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._indGoneAll(); }")

        # 5) ASEDIO (etapa 2): HUD con el CHIP DE PUNTOS
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
        for i in range(80):
            await page.wait_for_timeout(500)
            ph = await page.evaluate("() => { const c = window.__PP_OESTE.ctrl(); return c && c._asedio ? c._asedio.phase : '-'; }")
            if ph in ('play', 'reveal'):
                print(f"asedio en {ph} tras {(i+1)*0.5:.0f}s")
                break
        # chip de puntos: da puntos y repinta el banderín
        hudinfo = await page.evaluate("""() => {
            const c = window.__PP_OESTE.ctrl();
            const a = c && c._asedio;
            if (!a || !a._hud) return 'sin-hud';
            c._puntosAdd(150, null); c._puntosAdd(100, null); c._puntosAdd(20, null);
            a._msg = '¡ESTRELLA DEL SHERIFF! ¡DALE CON UNA BOMBA O CON EL REVÓLVER!';
            a._msgT = 9;
            a._hud.set(a.time, a._prog(), a._hudMsg(), undefined, a._marc(), c.puntos);
            return { pts: c.puntos, hudPts: a._hud.pts,
                     y: +a._hud.group.position.y.toFixed(3) };
        }""")
        print("hud asedio con puntos:", hudinfo)
        await page.wait_for_timeout(500)
        await page.evaluate("() => window.__camView('hud')")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/v2119_asedio_hud_puntos.png")
        print("captura: v2119_asedio_hud_puntos (chip estrella + banderín)")
        print("errores pagina:", len(errors), errors[:3])
        await browser.close()

asyncio.run(main())
