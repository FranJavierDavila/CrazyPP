#!/usr/bin/env python3
"""v2.118 · Capturas: ESTACIÓN PARADA1 AL SUELO (fin del hueco), TÚNEL con
boca de ENTRADA normal y boca de SALIDA espejada en AMBAS paredes, y en el
ASEDIO el HUD CLARO (banderín de 2 líneas, cartel de oleada sin taparlo)."""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8938
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
    c.position.set(0.0, 1.62, 0.40); c.lookAt(3.30, 1.30, -4.80);
  } else if (mode === 'preL') {
    c.position.set(0.0, 1.62, 0.40); c.lookAt(-3.30, 1.30, -4.80);
  } else if (mode === 'hud') {
    c.position.set(0, 1.55, 0.60); c.lookAt(0, 2.30, -2.55);
  } else if (mode === 'winR') {
    c.position.set(-0.15, 1.62, 0.35); c.lookAt(3.05, 1.30, -1.80);
  } else if (mode === 'winL') {
    c.position.set(0.15, 1.62, 0.35); c.lookAt(-3.05, 1.30, -1.80);
  } else if (mode === 'estacion') {
    c.position.set(0.0, 1.62, 0.40); c.lookAt(3.60, 1.70, -1.40);
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

        # 0) VERIFICACIÓN EN VIVO: bocas (escalas), estación (altura) y HUD
        geo = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            const bocas = m.tunelGrp.children.filter(c => c.userData && c.userData.boca);
            const inB = bocas.filter(c => Math.abs(c.position.z) < 1e-6);
            const outB = bocas.filter(c => c.position.z < -1);
            const hud = m._hud;
            return {
                estY: m.estArt.map(e => +e.position.y.toFixed(3)),
                inScales: inB.map(c => c.scale.x),
                outScales: outB.map(c => c.scale.x),
                hudY: hud ? +hud.group.position.y.toFixed(3) : null,
                hudH: hud ? hud.cv.height : null,
                bannerY: 1.38,
            };
        }""")
        print("verificación en vivo:", geo)

        # 1) ESTACIÓN DE SALIDA: PARADA1 con la base del arte en el suelo
        await page.evaluate("() => window.__camView('estacion')")
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"{OUT}/v2118_estacion_parada1.png")
        print("captura: v2118_estacion_parada1 (PARADA1 al suelo)")

        # preparar el vagón en marcha
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m.phase='run'; m._depart(); m.v = 2.6; }")
        await page.wait_for_timeout(800)
        # calentamiento de texturas del túnel
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._tunnelT = 0.01; }")
        for i in range(120):
            await page.wait_for_timeout(500)
            ph = await page.evaluate("() => window.__PP_GAME.champs.mod.trenDebug._tunnelPhase")
            if ph in ('in', 'dur'):
                print(f"calentamiento: túnel en {ph} tras {(i+1)*0.5:.0f}s")
                break
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._tunnelPhase='none'; m._tunnelT=999; m.tunelGrp.visible=false; m.tunelOscuro.visible=false; m.tunelOscuro.material.opacity=0; }")
        await page.wait_for_timeout(400)

        # 2) TÚNEL PRE: boca de ENTRADA (NORMAL) por la pared DERECHA…
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._tunnelPhase = 'pre'; m._tunnelT2 = 0;
            m._tunelZ = -4.6;
            m.tunelGrp.position.z = -4.6; m.tunelGrp.visible = true;
            m.tunelOscuro.material.opacity = 0; m.tunelOscuro.visible = false;
        }""")
        await page.wait_for_timeout(600)
        await page.evaluate("() => window.__camView('pre')")
        await page.screenshot(path=f"{OUT}/v2118_tunel_pre_der.png")
        print("captura: v2118_tunel_pre_der (entrada NORMAL pared derecha)")
        # …y por la IZQUIERDA (antes iba espejada: ahora NORMAL también)
        await page.evaluate("() => window.__camView('preL')")
        await page.screenshot(path=f"{OUT}/v2118_tunel_pre_izq.png")
        print("captura: v2118_tunel_pre_izq (entrada NORMAL pared izquierda)")

        # 3) BOCA DE SALIDA ESPEJADA en AMBAS paredes
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._tunnelPhase = 'out'; m._tunnelT2 = 0.2;
            m._tunelZ = 27.8;
            m.tunelGrp.position.z = 27.8; m.tunelGrp.visible = true;
            m.tunelOscuro.material.opacity = 0.30; m.tunelOscuro.visible = true;
        }""")
        await page.wait_for_timeout(600)
        await page.evaluate("() => window.__camView('winR')")
        await page.screenshot(path=f"{OUT}/v2118_tunel_salida_der.png")
        await page.evaluate("() => window.__camView('winL')")
        await page.screenshot(path=f"{OUT}/v2118_tunel_salida_izq.png")
        print("capturas: v2118_tunel_salida_der/izq (salida ESPEJADA ambas paredes)")
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._tunnelPhase='none'; m.tunelGrp.visible=false; m.tunelOscuro.visible=false; m.tunelOscuro.material.opacity=0; }")

        # 4) ASEDIO (etapa 2): HUD claro + cartel de oleada sin solape
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
        # mensaje LARGO en el banderín (2 líneas) con el marcador activo
        largo = await page.evaluate("""() => {
            const c = window.__PP_OESTE.ctrl();
            const a = c && c._asedio;
            if (!a || !a._hud) return 'sin-hud';
            a._msg = '¡ESTRELLA DEL SHERIFF! ¡DALE CON UNA BOMBA O CON EL REVÓLVER!';
            a._msgT = 9;
            a._hud.set(a.time, a._prog(), a._hudMsg(), undefined, a._marc());
            return { y: +a._hud.group.position.y.toFixed(3),
                     prog: a._prog(), marc: a._marc(),
                     hudH: a._hud.cv.height };
        }""")
        print("hud asedio:", largo)
        await page.wait_for_timeout(500)
        await page.evaluate("() => window.__camView('hud')")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/v2118_asedio_hud_2lineas.png")
        print("captura: v2118_asedio_hud_2lineas (banderín envuelto + marcador + reloj)")

        # 5) CARTEL DE OLEADA a y 1.38 — visible COMPLETO y sin tapar el HUD
        await page.evaluate("""() => {
            const c = window.__PP_OESTE.ctrl();
            const a = c && c._asedio;
            if (!a) return 'sin-asedio';
            a._showBanner(2);
        }""")
        await page.wait_for_timeout(1300)
        bpos = await page.evaluate("""() => {
            const c = window.__PP_OESTE.ctrl();
            const a = c && c._asedio;
            const b = a && a.bannerGrp;
            const h = a && a._hud;
            if (!b || !h) return 'sin-objetos';
            return { bannerY: +b.position.y.toFixed(3), hudY: +h.group.position.y.toFixed(3) };
        }""")
        print("posiciones banner/hud:", bpos)
        await page.evaluate("() => window.__camView('hud')")
        await page.wait_for_timeout(300)
        await page.screenshot(path=f"{OUT}/v2118_asedio_banner_hud.png")
        print("captura: v2118_asedio_banner_hud (cartel y HUD sin solape)")
        print("errores pagina:", len(errors), errors[:3])
        await browser.close()

asyncio.run(main())
