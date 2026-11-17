#!/usr/bin/env python3
"""v2.115 · Banco visual de la etapa 4 (TREN) sobre el juego REAL.

- Sirve game/ por HTTP (los campeonatos necesitan fetch).
- Jugador «foro3d» (window.__PP_DEBUG) + pp_champ_oeste_stage=4.
- Lanza el campeonato del Oeste y el gatillo de la etapa del tren.
- Cámara proxy: renderiza con una cámara NUESTRA dentro del vagón
  (ventanas, pirámide, vórtice, ESTACIÓN del artista, medallones, TÚNEL).
- Capturas PNG en /tmp/trenshot/.
"""
import asyncio, json, os, sys, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8931
OUT = "/tmp/trenshot"
os.makedirs(OUT, exist_ok=True)

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
  if (mode === 'winL') {
    c.position.set(0.15, 1.62, 0.35); c.lookAt(-3.05, 1.25, -1.80);
  } else if (mode === 'winR') {
    c.position.set(-0.15, 1.62, 0.35); c.lookAt(3.05, 1.25, -1.80);
  } else if (mode === 'pir') {
    c.position.set(0.0, 1.62, 0.55); c.lookAt(0, 1.05, -4.62);
  } else if (mode === 'port') {
    c.position.set(0.0, 1.62, 0.45); c.lookAt(0, 0.88, -1.42);
  } else if (mode === 'pod') {
    // MESA RIVAL desde arriba: los medallones de superpoder
    c.position.set(0.0, 1.9, -0.85); c.lookAt(0, 0.78, -2.3);
  } else if (mode === 'est') {
    // ESTACIÓN DEL ARTISTA por la ventana derecha
    c.position.set(-0.2, 1.62, 0.35); c.lookAt(3.4, 1.35, -1.4);
  } else if (mode === 'wide') {
    c.position.set(0.0, 1.75, 1.35); c.lookAt(0, 1.05, -3.4);
  } else if (mode === 'off') {
    g.renderer.render = window.__origRender;
  }
  return 'ok';
};
"""

JS_ESTADO = """() => {
  const g = window.__PP_GAME;
  const m = g && g.champs && g.champs.mod ? g.champs.mod.trenDebug : null;
  const st = {};
  try {
    st.balls = 1 + (m && m.extras ? m.extras.filter(e => e.alive).length : 0);
    st.pod = m && m._pod ? m._pod.tipo : '-';
    st.tun = m ? m._tunnelPhase : '-';
    st.osc = m && m.tunelOscuro ? +m.tunelOscuro.material.opacity.toFixed(2) : 0;
    st.cubos = m ? m.cubos.filter(r => !r.muerto).length : 0;
    st.ingots = m ? m.ingots : 0;
    st.wave = m ? m.wave : 0;
    st.estArt = m && m.estArt ? m.estArt.map(a => a.visible && !!a.material.map) : [];
  } catch (e) { st.err = String(e); }
  return st;
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
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append("console: " + m.text)
                if m.type == "error" else None)

        await page.goto(f"http://127.0.0.1:{PORT}/index.html")
        await page.wait_for_timeout(2500)
        await page.evaluate("""() => {
            localStorage.setItem('pp_player_name', 'foro3d');
            localStorage.setItem('pp_champ_oeste_stage', '4');
        }""")
        await page.reload()
        await page.wait_for_timeout(3500)
        dbg = await page.evaluate("!!window.__PP_DEBUG")
        print("debug:", dbg)
        await page.evaluate("""() => {
            window.__pp2DPlay = true;
            const ov = document.getElementById('overlay');
            if (ov) ov.style.display = 'none';
        }""")
        await page.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
        await page.wait_for_timeout(5000)

        await page.evaluate(JS_CAM)
        print("gatillando replayLaunch(3) hasta el cartel…")
        for i in range(80):
            await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(3)")
            await page.wait_for_timeout(400)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return { ta: g.champs.mod.testActive(),
                         instr: g._instr ? 'si' : 'none' };
            }""")
            if st["ta"] or st["instr"] == "si":
                print(f"  cartel/etapa activa tras {(i+1)*0.4:.0f}s de reloj")
                break
        print("esperando cartel+intro+saque (tiempo de juego)…")
        vivo = False
        for i in range(300):
            await page.wait_for_timeout(500)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return {
                    ta: g.champs.mod.testActive(),
                    by: +(g.ball ? g.ball.pos.y : -9).toFixed(2),
                };
            }""")
            if st["ta"] and st["by"] > 0.95:
                vivo = True
                print(f"  bola viva tras {i*0.5:.0f}s de reloj")
                break
        if not vivo:
            print("SIN BOLA VIVA — sigo con las capturas igualmente")

        # captura del vórtice al saque
        await page.evaluate("() => window.__camView('port')")
        await page.screenshot(path=f"{OUT}/portal_saque.png")
        print("captura: portal_saque")

        # ESTADO de los sistemas v2.115 mientras corre
        for i in range(10):
            await page.wait_for_timeout(1000)
            st = await page.evaluate(JS_ESTADO)
            print(f"  [{i}] balls={st.get('balls')} pod={st.get('pod')} "
                  f"tun={st.get('tun')} osc={st.get('osc')} cubos={st.get('cubos')} "
                  f"estArt={st.get('estArt')}")
            if st.get('err'): print('   ESTADO ERR:', st['err'])
            if i == 2:
                await page.evaluate("() => window.__camView('pod')")
                await page.screenshot(path=f"{OUT}/pod_mesa_rival.png")
                print("captura: pod_mesa_rival")
            if i == 5:
                await page.evaluate("() => window.__camView('pir')")
                await page.screenshot(path=f"{OUT}/piramide.png")
                print("captura: piramide (separación 1/4 + lluvia si hubo)")

        # vistas fijas
        for mode, name in [("winL", "ventana_izq"), ("winR", "ventana_der"),
                           ("est", "estacion_artista"), ("wide", "general")]:
            await page.evaluate(f"() => window.__camView('{mode}')")
            await page.wait_for_timeout(900)
            await page.screenshot(path=f"{OUT}/{name}.png")
            print("captura:", name)

        print("errores pagina:", len(errors))
        for e in errors[:8]:
            print("  ", e[:160])
        await browser.close()

asyncio.run(main())
