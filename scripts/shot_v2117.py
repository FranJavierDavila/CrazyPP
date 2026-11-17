#!/usr/bin/env python3
"""v2.117 · Capturas focalizadas: TÚNEL COSIDO (boca 3,4 m entrando, interior
20 %, boca de SALIDA espejada cosida a la banda), ESTACIÓN PARADA1 en la
salida, y en el ASEDIO el MARCADOR REAL (carta contador.png + reloj de la
oleada) y la CASA DEL SHERIFF LLEGANDO AL SUELO."""
import asyncio, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8937
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
  } else if (mode === 'hud') {
    c.position.set(0, 1.55, 0.60); c.lookAt(0, 2.25, -2.55);
  } else if (mode === 'winR') {
    c.position.set(-0.15, 1.62, 0.35); c.lookAt(3.05, 1.30, -1.80);
  } else if (mode === 'casa') {
    c.position.set(0.0, 1.55, 2.30); c.lookAt(0, 1.20, -3.80);
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

        # 0) ESTACIÓN DE SALIDA: la parada de salida muestra PARADA1.png
        geo = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            const bocas = m.tunelGrp.children.filter(c => c.userData && c.userData.boca);
            const bandas = m.tunelGrp.children.filter(c => !(c.userData && c.userData.boca));
            return {
                bh: bocas[0].geometry.parameters.width,
                bocaY: bocas[0].position.y,
                len: bandas[0].geometry.parameters.width,
                cosidoIn: (bandas[0].position.z + bandas[0].geometry.parameters.width/2
                           + bocas[0].geometry.parameters.width/2).toFixed(4),
                cosidoOut: (bandas[0].position.z - bandas[0].geometry.parameters.width/2
                            + bocas[1].position.z * -1 - bocas[1].geometry.parameters.width/2).toFixed(4),
                stationVis: m.station.visible,
            };
        }""")
        print("geometría del túnel:", geo)
        await page.evaluate("() => window.__camView('estacion')")
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"{OUT}/v2117_estacion_parada1.png")
        print("captura: v2117_estacion_parada1 (salida = PARADA1)")

        # preparar el vagón en marcha
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m.phase='run'; m._depart(); m.v = 2.6; }")
        await page.wait_for_timeout(800)

        # 0b) CALENTAMIENTO del túnel (decode de texturas)
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._tunnelT = 0.01; }")
        for i in range(120):
            await page.wait_for_timeout(500)
            ph = await page.evaluate("() => window.__PP_GAME.champs.mod.trenDebug._tunnelPhase")
            if ph in ('in', 'dur'):
                print(f"calentamiento: túnel en {ph} tras {(i+1)*0.5:.0f}s")
                break
        await page.evaluate("() => { const m = window.__PP_GAME.champs.mod.trenDebug; m._tunnelPhase='none'; m._tunnelT=999; m.tunelGrp.visible=false; m.tunelOscuro.visible=false; m.tunelOscuro.material.opacity=0; }")
        await page.wait_for_timeout(400)

        # 1) TÚNEL PRE: boca de 3,4 m acercándose con luz normal
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
        await page.screenshot(path=f"{OUT}/v2117_tunel_pre.png")
        print("captura: v2117_tunel_pre (boca de 3,4 m entrando, luz normal)")

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
        await page.screenshot(path=f"{OUT}/v2117_tunel_dentro.png")
        print("captura: v2117_tunel_dentro (luz al 20 %)")

        # 3) BOCA DE SALIDA espejada COSIDA a la banda, asomando en la ventana
        await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            m._tunnelPhase = 'out'; m._tunnelT2 = 0.2;
            m._tunelZ = 27.8;
            m.tunelGrp.position.z = 27.8; m.tunelGrp.visible = true;
            m.tunelOscuro.material.opacity = 0.35; m.tunelOscuro.visible = true;
        }""")
        await page.wait_for_timeout(600)
        st = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod.trenDebug;
            const TU = 26.4 + 3.4 / 2;
            return { ph: m._tunnelPhase, z: m.tunelGrp.position.z.toFixed(2),
                     bocaOutEdge: (m.tunelGrp.position.z - TU).toFixed(2) };
        }""")
        print("boca de salida:", st)
        await page.screenshot(path=f"{OUT}/v2117_tunel_salida.png")
        print("captura: v2117_tunel_salida (boca espejada cosida a la banda)")

        # 4) ASEDIO (etapa 2): cerrar el TREN y lanzar el asedio
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
        # VESTIR las 3 casas como SHERIFF (casa 1) y diana en zona verde
        vest = await page.evaluate("""() => {
            const c = window.__PP_OESTE.ctrl();
            const a = c && c._asedio;
            if (!a) return 'sin-asedio';
            a.casasOleada = [[1, 1, 1]];
            a._visteCasas();
            a._spawnTarget();
            const b = a.edif[1];
            return { fac: b.fac.material.map && b.fac.material.map.image ?
                     b.fac.material.map.image.src.split('/').pop() : '?',
                     int: b.interior.material.map && b.interior.material.map.image ?
                     b.interior.material.map.image.src.split('/').pop() : '?',
                     casa: b.casa,
                     zonaV: (a.zonas && a.zonas.find(z => z.b === b) || {}).v };
        }""")
        print("casas vestidas de sheriff:", vest)
        await page.wait_for_timeout(700)
        marc = await page.evaluate("""() => {
            const ctrl = window.__PP_OESTE && window.__PP_OESTE.ctrl &&
                         window.__PP_OESTE.ctrl();
            if (!ctrl || !ctrl._asedio) return 'sin-asedio';
            const a = ctrl._asedio;
            return a && a._hud ? { wave: a.wave, marc: a._marc(),
                                   time: a.time.toFixed(0),
                                   vis: a._hud.group.visible,
                                   reloj: !!a._hud.relojImg,
                                   cnt: !!a._hud.cntImg } : 'sin-hud';
        }""")
        print("marcador asedio:", marc)
        await page.evaluate("() => window.__camView('hud')")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/v2117_asedio_marcador.png")
        print("captura: v2117_asedio_marcador (carta contador + reloj de la oleada)")
        # LA CASA: vista de la calle (edificio central = sheriff)
        await page.evaluate("() => window.__camView('casa')")
        await page.wait_for_timeout(400)
        await page.screenshot(path=f"{OUT}/v2117_asedio_casa_suelo.png")
        print("captura: v2117_asedio_casa_suelo (sheriff llega al suelo)")
        print("errores pagina:", len(errors), errors[:3])
        await browser.close()

asyncio.run(main())
