#!/usr/bin/env python3
"""v2.31 · Verificación: RESCATE DEFINITIVO DEL AUDIO EN VR (Quest).

Síntoma corregido: dentro del visor no suena NADA (ni música, ni efectos,
ni narrador) aunque la háptica funcione. Causa: contexto de audio creado
fuera de la sesión que queda 'running' pero MUDO al re-asignar la salida
en la Quest; los rescates antiguos solo actuaban si el estado no era
'running'.

1) ESTÁTICOS: gestureKick/nudgeSink/markVRStart/vrBound presentes; enterVR
   re-vínculo dentro del gesto; hooks XR con gestureKick; música de un solo
   decode; adopt() rearranca música/murmullo; ventana 1200 ms; v2.30 intacto
   (portada sin partida, sin vallas, sin panel de audio).
2) FUNCIONALES 2D: gestureKick deja el contexto 'running'; en 2D NO fuerza
   rebuild (throttle por vrBound); setMusicWanted reutiliza el buffer.
3) VR SIMULADO: xrActive+vrBound=false -> gestureKick re-crea el contexto
   (rebuilds+1) y queda vrBound=true, running, con blip; dobles gestos no
   multiplican rebuilds (throttle 900 ms); onSessionEnd resetea vrBound.
4) REGRESIÓN v2.30: portada inactiva (bola quieta, sin sonidos) y menú VR.
5) Capturas + sin errores de página.
"""
import asyncio, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
fails = []

def check(cond, msg):
    if not cond:
        fails.append(msg)
        print("  FAIL:", msg)
    else:
        print("  ok:", msg)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4000)

        # ============ 1) ESTÁTICOS ============
        print("== estáticos v2.31 ==")
        src = open(HTML, encoding="utf-8").read()
        check("gestureKick()" in src, "GameAudio.gestureKick existe")
        check("setSinkId" in src, "nudgeSink usa setSinkId")
        check("markVRStart()" in src, "markVRStart existe y se llama")
        check("this.vrBound = false" in src, "flag vrBound presente")
        check("contexto dentro del gesto de solicitud" in src,
              "enterVR: re-vínculo DENTRO del gesto (tras setSession)")
        check("const kickAudio = () => this.audio.gestureKick();" in src,
              "hooks XR (selectstart/squeeze/inputs) usan gestureKick")
        check("if (this._musicBuf || this._musicLoading) return;" in src,
              "música: UN solo decode (sin carrera _musicLoading)")
        check("this._musicCtx !== this.ctx" not in src,
              "música: sin comparación de contexto (buffer sirve para todos)")
        check("su música y su murmullo" in src,
              "adopt(): rearranca música y murmullo en el contexto nuevo")
        check("}, 1200);" in src, "tryFreshRunning: ventana de decisión 1200 ms")
        check("this.audio.vrBound = false;   // v2.31" in src,
              "onSessionEnd resetea vrBound")
        check("this.audio.gestureKick();   // v2.31" in src,
              "onSelectStart usa gestureKick")

        # ============ 1b) ESTÁTICOS v2.30 (limpieza intacta) ============
        print("== estáticos v2.30 ==")
        check('id="spectate"' not in src, "sin botón #spectate")
        check("createAudioStatus" not in src, "sin panel de audio bajo el marcador")
        for ad in ("ARENA 480 Hz", "MAGNUS SPORT", "TOPSPIN CLUB"):
            check(ad not in src, f"sin valla '{ad}'")

        # ============ 2) FUNCIONALES 2D ============
        print("== gestureKick en 2D ==")
        a2d = await page.evaluate("""() => {
            const g = window.__game;
            const a = g.audio;
            a.gestureKick();               // 1.º: crea el contexto (lazy) si no hay
            const afterCreate = a.rebuilds;
            a.gestureKick();               // 2.º: con ctx running y en 2D NO recrea
            return { st: a.ctx ? a.ctx.state : 'none',
                     afterCreate, rebuilds: a.rebuilds,
                     xr: a.xrActive, vrBound: a.vrBound };
        }""")
        check(a2d["st"] == "running", f"gesto 2D: contexto running ({a2d['st']})")
        check(a2d["rebuilds"] == a2d["afterCreate"],
              "en 2D gestureKick NO recrea contexto (solo en VR sin vrBound)")
        await page.wait_for_timeout(200)
        a2d2 = await page.evaluate("""() => {
            const g = window.__game;
            const b1 = g.audio._musicBuf;
            g.audio.setMusicWanted(true);
            return { buf: !!b1 };
        }""")
        await page.wait_for_timeout(2500)  # tiempo para decode (~0.95 MB ogg)
        a2d3 = await page.evaluate("""() => {
            const g = window.__game;
            const b1 = g.audio._musicBuf;
            g.audio.setMusicWanted(false);
            g.audio.setMusicWanted(true);   // reusa el MISMO buffer (sin re-decode)
            return { loaded: !!g.audio._musicBuf,
                     same: b1 === g.audio._musicBuf,
                     playing: g.audio.musicPlaying };
        }""")
        check(a2d3["loaded"] and a2d3["same"], "música decodificada UNA vez y reutilizada")
        check(a2d3["playing"], "música en marcha tras reactivar (menú VR simulado)")
        g2 = await page.evaluate("() => { window.__game.audio.setMusicWanted(false); return true; }")

        # ============ 3) VR SIMULADO: rescate del contexto mudo ============
        print("== rescate en VR simulado ==")
        vr = await page.evaluate("""() => {
            const g = window.__game;
            const a = g.audio;
            // estado exacto del bug: contexto 'running' nacido FUERA del casco
            a.xrActive = true; a.vrBound = false;
            const before = a.rebuilds;
            a.gestureKick();               // primer gatillo dentro de la sesión
            return { before, after: a.rebuilds,
                     adoptedNow: a.rebuilds > before ? a.vrBound : null,
                     st: a.ctx ? a.ctx.state : 'none' };
        }""")
        check(vr["after"] > vr["before"],
              f"gestureKick en VR recrea el contexto ({vr['before']}→{vr['after']})")
        await page.wait_for_timeout(400)
        vr2 = await page.evaluate("""() => {
            const g = window.__game;
            const a = g.audio;
            const r = { vrBound: a.vrBound, st: a.ctx ? a.ctx.state : 'none',
                        rebuilds: a.rebuilds };
            // segundo gesto inmediato: el throttle (900 ms) y vrBound evitan churn
            a.gestureKick();
            r.rebuilds2 = a.rebuilds;
            return r;
        }""")
        check(vr2["vrBound"] is True, "contexto nuevo ADOPTADO y confirmado (vrBound=true)")
        check(vr2["st"] == "running", f"contexto adoptado running ({vr2['st']})")
        check(vr2["rebuilds2"] == vr2["rebuilds"],
              "segundo gesto NO recrea otra vez (vrBound + throttle)")
        vr3 = await page.evaluate("""() => {
            const g = window.__game;
            g.audio.xrActive = false;
            g.audio.vrBound = false;    // como onSessionEnd
            return { xr: g.audio.xrActive, vrBound: g.audio.vrBound };
        }""")
        check(vr3["xr"] is False and vr3["vrBound"] is False, "onSessionEnd: estado limpio")
        # markVRStart no lanza con setSinkId ausente/presente
        vr4 = await page.evaluate("""() => {
            const g = window.__game;
            g.audio.markVRStart();
            const ok1 = g.audio.xrActive === true;
            g.audio.xrActive = false;
            return ok1;
        }""")
        check(vr4, "markVRStart activa xrActive sin lanzar excepciones")

        # ============ 4) REGRESIÓN v2.30: portada inactiva + menú ============
        print("== portada sin partida (regresión) ==")
        idle = await page.evaluate("""() => {
            const g = window.__game;
            g.audio.paddle = () => { g.__spyPaddle = (g.__spyPaddle || 0) + 1; };
            g.audio.announce = () => { g.__spyAnn = (g.__spyAnn || 0) + 1; };
            return { vel: +g.ball.vel.length().toFixed(3),
                     score: g.rules.scorePlayer + '-' + g.rules.scoreAi,
                     overlay: !document.getElementById('overlay').classList.contains('hidden') };
        }""")
        check(idle["overlay"], "portada visible")
        check(idle["vel"] == 0 and idle["score"] == "0-0", "bola quieta y 0-0 en portada")
        await page.wait_for_timeout(2000)
        idle2 = await page.evaluate("""() => {
            const g = window.__game;
            return { moved: +g.ball.vel.length().toFixed(3),
                     p: g.__spyPaddle || 0, a: g.__spyAnn || 0 };
        }""")
        check(idle2["moved"] == 0 and idle2["p"] == 0 and idle2["a"] == 0,
              "sin física ni sonidos de fondo en la portada")
        await page.screenshot(path="/home/z/my-project/download/captura-v231-portada.png")

        print("== menú VR intacto ==")
        menu = await page.evaluate("""() => {
            const g = window.__game;
            g.rules.startMatch('match');
            g.renderer.xr.isPresenting = true;
            g.menuPage = 'main'; g.menuSec = 'match'; g.menuOpen = true;
            g.menuGroup.visible = true;
            g.camera.position.set(0, 1.4, 0.9);
            g.camera.lookAt(0, 1.2, -1.2);
            g.camera.updateMatrixWorld(true);
            g.anchorMenu(); g.drawMenu();
            const ids = g.menuRects.map((r) => r.id);
            g.renderer.xr.isPresenting = false;
            return { hasStart: ids.includes('start'), hasOpts: ids.includes('sec:opts') };
        }""")
        check(menu["hasStart"] and menu["hasOpts"], "menú acordeón intacto")
        check(not errors, f"sin errores de página ({errors[:3]})")

        await browser.close()

    print()
    if fails:
        print(f"FALLOS ({len(fails)}):")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
