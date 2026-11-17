#!/usr/bin/env python3
"""v2.114 · Banco visual de la etapa 4 (TREN) sobre el juego REAL (vórtice pegado a la red).

- Sirve game/ por HTTP (los campeonatos necesitan fetch).
- Jugador «foro3d» (window.__PP_DEBUG) + pp_champ_oeste_stage=4.
- Lanza el campeonato del Oeste y el gatillo de la etapa del tren.
- Cámara proxy: renderiza con una cámara NUESTRA dentro del vagón
  (ventana izquierda, ventana derecha, pirámide, vista general).
- Traza del bote de la bola tras el saque (y, vy, z) para calibrar.
- Capturas PNG en /tmp/trenshot/.
"""
import asyncio, json, os, sys, threading, functools, time
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

def serve():
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), _H)
    httpd.serve_forever()

JS_SAMPLER = """
window.__ballLog = [];
(() => {
  const loop = () => {
    try {
      const g = window.__PP_GAME;
      if (g && g.ball) {
        window.__ballLog.push([performance.now()/1000,
          +g.ball.pos.y.toFixed(3), +g.ball.vel.y.toFixed(2),
          +g.ball.pos.z.toFixed(2), +g.ball.pos.x.toFixed(2)]);
        if (window.__ballLog.length > 4000) window.__ballLog.shift();
      }
    } catch (e) {}
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
})();
"""

JS_CAM = """
/* Sustituye la cámara del render por la nuestra (el juego sigue su lógica). */
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
  } else if (mode === 'red') {
    c.position.set(0.0, 1.30, -0.72); c.lookAt(0, 0.86, -1.52);
  } else if (mode === 'wide') {
    c.position.set(0.0, 1.75, 1.35); c.lookAt(0, 1.05, -3.4);
  } else if (mode === 'off') {
    g.renderer.render = window.__origRender;
  }
  return 'ok';
};
"""

async def main():
    threading.Thread(target=serve, daemon=True)
    # inicia el servidor (el hilo daemon muere si no se guarda la ref)
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
        # modo depuración + etapa 4 directamente
        await page.evaluate("""() => {
            localStorage.setItem('pp_player_name', 'foro3d');
            localStorage.setItem('pp_champ_oeste_stage', '4');
        }""")
        await page.reload()
        await page.wait_for_timeout(3500)
        dbg = await page.evaluate("!!window.__PP_DEBUG")
        print("debug:", dbg)
        # 2D activo + portada fuera (el bucle completo corre en escritorio)
        await page.evaluate("""() => {
            window.__pp2DPlay = true;
            const ov = document.getElementById('overlay');
            if (ov) ov.style.display = 'none';
        }""")

        # lanza el campeonato del Oeste
        await page.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
        await page.wait_for_timeout(5000)
        st = await page.evaluate("""() => {
            const m = window.__PP_GAME.champs.mod;
            return m ? ('mod:' + (m.id || 'oeste')) : 'no-mod';
        }""")
        print("modulo:", st)

        # traza del bote instalada ANTES del saque
        await page.evaluate(JS_SAMPLER)
        await page.evaluate(JS_CAM)

        # salto DIRECTO a la etapa 4: repetimos el gatillo hasta que el
        # cartel de instrucciones aparezca (el anti-gesto _armT corre a
        # 0,25x en SwiftShader; un único disparo se lo come).
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
        # esperamos en TIEMPO DE JUEGO (cartel 7,5 s + salida + intro 4,2 + saque)
        print("esperando cartel+intro+saque (tiempo de juego)…")
        vivo = False
        for i in range(300):          # hasta 150 s de reloj
            await page.wait_for_timeout(500)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return {
                    ta: g.champs.mod.testActive(),
                    instr: g._instr ? g._instr.t.toFixed(1) : 'none',
                    by: +(g.ball ? g.ball.pos.y : -9).toFixed(2),
                };
            }""")
            if st["ta"] and st["by"] > 0.95:
                vivo = True
                print(f"  bola viva tras {i*0.5:.0f}s de reloj")
                break
            if i % 24 == 0:
                print(f"  …{i*0.5:.0f}s ta={st['ta']} cartel={st['instr']} y={st['by']}")
        if not vivo:
            print("SIN BOLA VIVA — sigo con las capturas igualmente")
        # captura INMEDIATA del vórtice en el saque (visible ~1,6 s)
        await page.evaluate("() => window.__camView('port')")
        await page.screenshot(path=f"{OUT}/portal_saque.png")
        print("captura: portal_saque (justo tras el saque)")
        await page.wait_for_timeout(2500)
        await page.screenshot(path=f"{OUT}/portal_apagado.png")
        print("captura: portal_apagado (2,5 s después)")
        # v2.114: primer plano red+vórtice en el SIGUIENTE recambio (0,55 s)
        await page.evaluate("() => window.__camView('red')")
        for i in range(40):
            await page.wait_for_timeout(500)
            st = await page.evaluate("() => { const g=window.__PP_GAME; return g.ball ? g.ball.pos.y : -9; }")
            if st > 0.9:
                await page.screenshot(path=f"{OUT}/portal_red.png")
                print("captura: portal_red (primer plano red+vórtice)")
                break

        # capturas mientras corre
        for mode, name in [("winL", "ventana_izq"), ("winR", "ventana_der"),
                           ("pir", "piramide"), ("port", "portal"),
                           ("wide", "general")]:
            await page.evaluate(f"() => window.__camView('{mode}')")
            await page.wait_for_timeout(900)
            await page.screenshot(path=f"{OUT}/{name}.png")
            print("captura:", name)

        # traza de la bola
        log = await page.evaluate("() => window.__ballLog || []")
        # busca el primer frame con la bola viva (y > 0.7) y muestra 6 s
        t0 = None
        rows = []
        for r in log:
            if t0 is None and r[1] > 0.9 and r[3] > -1.2:
                t0 = r[0]
            if t0 is not None and r[0] - t0 <= 7.0:
                rows.append(r)
        with open(f"{OUT}/bote.json", "w") as f:
            json.dump(rows, f)
        # resumen: máximos locales de y (ápices)
        apex = []
        for i in range(2, len(rows) - 2):
            y0, y1, y2 = rows[i - 1][1], rows[i][1], rows[i + 1][1]
            if y1 >= y0 and y1 >= y2 and y1 > 0.95:
                if not apex or rows[i][0] - apex[-1][0] > 0.25:
                    apex.append((round(rows[i][0] - t0, 2), y1,
                                 rows[i][3], rows[i][4]))
        print("ápices del bote (t, y, z, x):")
        for a in apex[:22]:
            print("   ", a)
        print("errores pagina:", len(errors))
        for e in errors[:8]:
            print("  ", e[:160])
        await browser.close()

asyncio.run(main())
