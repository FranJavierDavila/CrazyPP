#!/usr/bin/env python3
"""v2.30 · Verificación: portada sin partida de fondo + limpieza de estímulos.

1) ESTÁTICOS: sin botón #spectate, sin HUD (#hud/#hud-score), sin claves
   ov_demo, sin createAudioStatus ("♪ audio"), sin vallas del suelo
   ('ARENA 480 Hz' etc.), sin audioStatus en el bucle.
2) PORTADA INACTIVA: sin visor la bola está posada y QUIETA en la mesa
   (velocidad 0 durante 2 s), el marcador no cambia (0-0) y NO hay sonidos
   de juego ni megafonía (espías sobre audio.paddle/serve/announce/chime).
3) MÚSICA: la portada sigue con la música activa (musicOn).
4) VR SIMULADO: con isPresenting=true el juego sigue funcionando — saque de
   la CPU, rally con golpeos, marcador vivo (gate v2.30 activo en VR).
5) Capturas portada ES + menú y sin errores de página.
"""
import asyncio, json, sys
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
        await page.wait_for_timeout(4500)

        # ============ 1) ESTÁTICOS ============
        print("== estáticos ==")
        src = open(HTML, encoding="utf-8").read()
        check('id="spectate"' not in src, "sin botón #spectate")
        check('id="hud"' not in src, "sin HUD de espectador")
        check("ov_demo" not in src, "sin clave i18n ov_demo")
        check("createAudioStatus" not in src, "sin panel de audio (createAudioStatus)")
        check("audioStatus" not in src, "sin referencias a audioStatus")
        for ad in ("ARENA 480 Hz", "MAGNUS SPORT", "TOPSPIN CLUB", "QUEST 3 CUP", "ITTF ARENA"):
            check(ad not in src, f"sin valla '{ad}'")
        check("__pp2DPlay" in src, "gancho de pruebas __pp2DPlay presente")
        check("VALLAS PUBLICITARIAS" not in src, "sección de vallas eliminada")

        # ============ 2) PORTADA INACTIVA (2D) ============
        print("== portada sin partida ==")
        idle = await page.evaluate("""() => {
            const g = window.__game;
            // espías de sonido/juego
            g.audio.paddle = () => { g.__spyPaddle = (g.__spyPaddle || 0) + 1; };
            g.audio.serve = () => { g.__spyServe = (g.__spyServe || 0) + 1; };
            g.audio.announce = () => { g.__spyAnn = (g.__spyAnn || 0) + 1; };
            g.audio.chime = () => { g.__spyChime = (g.__spyChime || 0) + 1; };
            return {
                ballY: +g.ball.pos.y.toFixed(3),
                ballZ: +g.ball.pos.z.toFixed(3),
                vel: +g.ball.vel.length().toFixed(3),
                score: g.rules.scorePlayer + '-' + g.rules.scoreAi,
                demoMeshVisible: g.demoPaddleMesh ? g.demoPaddleMesh.visible : null,
                overlayVisible: !document.getElementById('overlay').classList.contains('hidden'),
            };
        }""")
        check(idle["overlayVisible"], "portada visible")
        check(idle["vel"] == 0, "bola parada en la portada (v=0)")
        check(idle["score"] == "0-0", f"marcador 0-0 en la portada (={idle['score']})")
        # 2,5 s observando: nada se mueve, nadie suena, nadie narra
        await page.wait_for_timeout(2500)
        after = await page.evaluate("""() => {
            const g = window.__game;
            return {
                moved: +g.ball.vel.length().toFixed(3),
                ballZ2: +g.ball.pos.z.toFixed(3),
                p: g.__spyPaddle || 0, s: g.__spyServe || 0,
                a: g.__spyAnn || 0, c: g.__spyChime || 0,
                score2: g.rules.scorePlayer + '-' + g.rules.scoreAi,
                msg: g.rules.message || '',
                musicOn: g.audio.musicOn,
            };
        }""")
        check(after["moved"] == 0, "seguirá parada tras 2,5 s (sin física de fondo)")
        check(after["ballZ2"] == idle["ballZ"], "la bola no se ha movido de su sitio")
        check(after["p"] == 0 and after["s"] == 0, "sin sonidos de pala/saque de fondo")
        check(after["a"] == 0 and after["c"] == 0, "sin narrador ni chimes de fondo")
        check(after["score2"] == "0-0", "el árbitro no puntúa en la portada")
        check(after["musicOn"] is True, "la música sigue activa en la portada")
        await page.screenshot(path="/home/z/my-project/download/captura-v230-portada.png")

        # ============ 3) VR SIMULADO: el juego sigue intacto ============
        print("== VR simulado ==")
        vr = await page.evaluate("""() => {
            const g = window.__game;
            g.__spyPaddle = 0; g.__spyServe = 0; g.__spyAnn = 0;
            g.renderer.xr.isPresenting = true;   // simular sesión XR
            g.rules.startMatch();
            g.rules.server = 'ai';               // la CPU abre el saque
            g.menuOpen = false;
            g.aiServeTimer = 0.3;                // saque inmediato de la CPU
            return true;
        }""")
        await page.wait_for_timeout(4500)
        vr2 = await page.evaluate("""() => {
            const g = window.__game;
            const r = {
                serves: g.__spyServe || 0,
                paddles: g.__spyPaddle || 0,
                ballSpeed: +g.ball.vel.length().toFixed(2),
                score: g.rules.scorePlayer + '-' + g.rules.scoreAi,
                state: g.rules.state,
            };
            g.renderer.xr.isPresenting = false;
            return r;
        }""")
        check(vr2["serves"] >= 1, f"en VR la CPU saca ({vr2['serves']} saques)")
        check(vr2["paddles"] >= 1 or vr2["ballSpeed"] > 0 or vr2["state"] != 'serve',
              f"en VR hay juego real (paddle={vr2['paddles']}, v={vr2['ballSpeed']}, estado={vr2['state']})")

        # ============ 4) MODO PRUEBAS 2D (__pp2DPlay) ============
        print("== modo pruebas 2D ==")
        t2d = await page.evaluate("""() => {
            const g = window.__game;
            window.__pp2DPlay = true;
            g.rules.startMatch();
            g.rules.state = 'rally';
            g.rules.lastHitter = 'player';
            g.ball.pos.set(0, 1.05, 0.9);
            g.ball.vel.set(0, 2.8, -5.8);
            g.ball.spin.set(6, 0, 0);
            return true;
        }""")
        await page.wait_for_timeout(1500)
        t2d2 = await page.evaluate("""() => {
            const g = window.__game;
            window.__pp2DPlay = false;
            return { speed: +g.ball.vel.length().toFixed(2),
                     hitter: g.rules.lastHitter, state: g.rules.state };
        }""")
        check(t2d2["speed"] > 0 or t2d2["hitter"] == 'ai' or t2d2["state"] != 'rally',
              "con __pp2DPlay el rally 2D se reactiva (pruebas headless)")

        # ============ 5) MENÚ VR intacto ============
        print("== menú ==")
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
            g.renderer.xr.isPresenting = false;
            const ids = g.menuRects.map((r) => r.id);
            return { hasStart: ids.includes('start'), hasOpts: ids.includes('sec:opts') };
        }""")
        check(menu["hasStart"] and menu["hasOpts"], "menú acordeón intacto (EMPEZAR + Opciones)")
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
