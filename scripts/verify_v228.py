#!/usr/bin/env python3
"""v2.28 · Verificación del nuevo arranque y del menú principal VR.

1) ESTÁTICOS: placeholders incrustados (hero, palas, botones, música, logo),
   portada minimalista (sin tarjeta antigua), acordeón y new i18n keys.
2) PORTADA HEADLESS: se ve el hero, palas ES/EN activas, botón JUGAR/PLAY
   cambia con el idioma, música (ogg) y footer demo.
3) MENÚ PRINCIPAL (simulado como presenting): se abre SOLO, acordeón con UNA
   sección, Crazy muestra el mensaje, EMPEZAR arranca y cierra, gate del
   saque IA con el menú abierto, multi/join reescalados.
4) Capturas: portada ES/EN + menú ES/EN.
"""
import asyncio, base64, json, sys
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
        for needle in ("data:image/jpeg;base64,/9j", "data:image/png;base64,iVBOR",
                       "data:audio/ogg;base64", "menuSec", "anchorMenu",
                       "sec_match", "crazy_msg", "btn_start", "survgo", "traingo"):
            check(needle in src, f"HTML contiene {needle}")
        # portada: SIN la tarjeta antigua (sin input de agarres ni botones viejos)
        for gone in ("gripSel", "gripSave", "trainbtn", "survbtn", "ambbtn", "statsLine"):
            check(gone not in src, f"portada sin elemento antiguo {gone}")
        # la palas de idioma viven en la portada y el menú las reutiliza
        check('id="padEs"' in src and 'id="padEn"' in src, "palas de idioma en portada")

        # ============ 2) PORTADA ============
        print("== portada ==")
        land = await page.evaluate("""() => {
          const ov = document.getElementById('overlay');
          const hero = document.querySelector('.hero-wrap img');
          const act = document.querySelector('.padbtn.active');
          const st = document.getElementById('status').textContent;
          const playEs = getComputedStyle(document.getElementById('playEs')).display;
          const playEn = getComputedStyle(document.getElementById('playEn')).display;
          return { hidden: ov.classList.contains('hidden'),
                   heroOk: !!hero && hero.src.startsWith('data:image/jpeg'),
                   actLang: act ? act.dataset.lang : null,
                   status: st, playEs, playEn,
                   demoGone: !document.getElementById('spectate'),   // v2.30
                   mute: !!document.getElementById('mutebtn') };
        }""")
        check(not land["hidden"], "portada visible al cargar")
        check(land["heroOk"], "hero con arte JPEG incrustado")
        check(land["actLang"] == "es", "idioma por defecto ES activo")
        check(land["playEs"] != "none" and land["playEn"] == "none", "botón JUGAR (ES)")
        check(land["demoGone"] and land["mute"], "v2.30: sin demo + botón música presentes")
        await page.screenshot(path="/home/z/my-project/download/captura-v228-portada-es.png")

        # cambio de idioma con la pala EN
        await page.click(".padbtn[data-lang='en']")
        await page.wait_for_timeout(400)
        en = await page.evaluate("""() => ({
          act: document.querySelector('.padbtn.active').dataset.lang,
          playEs: getComputedStyle(document.getElementById('playEs')).display,
          playEn: getComputedStyle(document.getElementById('playEn')).display,
          lang: window.__TLang(), stored: localStorage.getItem('pp_lang'),
          demoGone: !document.getElementById('spectate'),   // v2.30
        })""")
        check(en["act"] == "en" and en["lang"] == "en" and en["stored"] == "en",
              "pala EN selecciona inglés y persiste")
        check(en["playEs"] == "none" and en["playEn"] != "none", "botón cambia a PLAY IN VR")
        await page.screenshot(path="/home/z/my-project/download/captura-v228-portada-en.png")
        await page.click(".padbtn[data-lang='es']")
        await page.wait_for_timeout(300)

        # ============ 3) MENÚ PRINCIPAL ============
        print("== menú principal ==")
        menu = await page.evaluate("""() => {
            const g = window.__game;
            if (!g) return { err: 'no __game' };
            g.rules.startMatch('match');
            g.connected = [true, true];
            g.renderer.xr.isPresenting = false;   // render con cámara 2D (sin sesión XR)
            // el menú principal se abre SOLO (simulando onSessionStart)
            g.menuPage = 'main'; g.menuSec = 'match'; g.menuOpen = true;
            g.menuGroup.visible = true;
            g.camera.position.set(0, 1.4, 0.9);
            g.camera.lookAt(0, 1.2, -1.2);
            g.camera.updateMatrixWorld(true);
            g.anchorMenu();
            g.drawMenu();
            const ids = g.menuRects.map((r) => r.id);
            const j = { ids, open: g.menuSec,
                        canvas: [g.menuCanvas.width, g.menuCanvas.height],
                        plane: [g.menuMesh.geometry.parameters.width,
                                g.menuMesh.geometry.parameters.height] };
            return j;
        }""")
        if "err" in menu:
            fails.append(menu["err"])
            print(menu)
        else:
            print(json.dumps(menu["ids"]))
            check(menu["canvas"] == [1024, 1536], "lienzo 1024x1536")
            check(menu["plane"] == [0.72, 1.08], "plano 0.72x1.08 m")
            check(menu["open"] == "match", "sección abierta por defecto: JUGAR PARTIDO")
            for need in ("sec:match", "sec:train", "sec:surv", "sec:crazy", "sec:opts",
                         "lang:es", "lang:en", "start", "close"):
                check(need in menu["ids"], f"rect {need} visible")
            # con match abierto: dificultad + online visibles, opts NO
            for need in ("diff:easy", "diff:medium", "diff:hard", "net:host", "net:join"):
                check(need in menu["ids"], f"contenido match: {need}")
            check("theme:pabellon" not in menu["ids"] and "trail" not in menu["ids"],
                  "contenido de otras secciones contraído")

        # acordeón: solo una abierta + crazy muestra el mensaje
        acc = await page.evaluate("""() => {
            const g = window.__game;
            const click = (id) => g.menuClick(g.menuRects.findIndex((r) => r.id === id));
            click('sec:opts');
            const idsOpts = g.menuRects.map((r) => r.id);
            const optsOpen = g.menuSec;
            const optsHasThemes = idsOpts.includes('theme:neon') && idsOpts.includes('trail');
            const optsHasStart = idsOpts.includes('start');
            click('sec:crazy');
            const idsCrazy = g.menuRects.map((r) => r.id);
            const crazyOpen = g.menuSec;
            const msg = g.rules.message;   // al pulsar CRAZY, el mensaje directo
            click('sec:crazy');            // segunda pulsación: contrae
            const closed = g.menuSec;
            click('sec:match');
            return { optsOpen, optsHasThemes, optsHasStart, crazyOpen, msg, closed,
                     matchAgain: g.menuSec };
        }""")
        check(acc["optsOpen"] == "opts" and acc["optsHasThemes"] and not acc["optsHasStart"],
              "acordeón: OPTS despliega salas/extras y contrae MATCH")
        check(acc["crazyOpen"] == "crazy" and acc["msg"].startswith("¡Sorpresas"),
              f"CRAZY muestra el mensaje ({acc['msg']})")
        check(acc["closed"] == "" and acc["matchAgain"] == "match",
              "segunda pulsación contrae; MATCH vuelve a abrirse")

        # EMPEZAR: arranca y cierra; con el menú abierto la CPU no saca
        startRes = await page.evaluate("""() => new Promise((res) => {
            const g = window.__game;
            const click = (id) => g.menuClick(g.menuRects.findIndex((r) => r.id === id));
            g.menuOpen = true; g.menuSec = 'match'; g.drawMenu();
            // congelación del saque IA: aiServeTimer no baja mientras menuOpen
            g.aiServeTimer = 1.0; g.aiServeWait = 5;
            const t0 = g.aiServeTimer;
            click('start');
            const closedAfterStart = !g.menuOpen;
            const stateAfter = g.rules.state;
            // restauramos un estado limpio para capturas
            res({ closedAfterStart, stateAfter, t0 });
        })""")
        check(startRes["closedAfterStart"], "EMPEZAR cierra el menú")
        check(startRes["stateAfter"] in ("serve", "rally"), "EMPEZAR deja el partido en marcha")

        # gate del saque IA comprobado con el bucle real
        # (v2.30: en 2D el juego está en pausa — el gate se prueba con el
        #  modo de pruebas __pp2DPlay, igual que un partido en VR)
        gate = await page.evaluate("""() => new Promise((res) => {
            const g = window.__game;
            window.__pp2DPlay = true;
            g.rules.startMatch('match');
            g.rules.server = 'ai';
            g.aiServeTimer = 0.4; g.aiServeWait = 9; g.aiToss = null;
            g.menuOpen = true;
            const t0 = g.aiServeTimer;
            setTimeout(() => {
                const frozen = g.aiServeTimer === t0 && !g.aiToss;
                g.menuOpen = false;
                setTimeout(() => {
                    res({ frozen, resumed: g.aiServeTimer < t0 || !!g.aiToss });
                }, 1600);
            }, 700);
        })""")
        check(gate["frozen"], "menú abierto: el saque de la CPU queda congelado")
        check(gate["resumed"], "menú cerrado: el saque de la CPU se reanuda")

        # capturas del menú (ES y EN) — en UN solo evaluate (el bucle 2D orbita
        # la cámara y se llevaría la vista entre evaluates)
        for lang, path in (("es", "/home/z/my-project/download/captura-v228-menu-es.png"),
                           ("en", "/home/z/my-project/download/captura-v228-menu-en.png")):
            shot = await page.evaluate(f"""() => {{
                const g = window.__game;
                window.__setLang('{lang}', g);
                g.rules.startMatch('match');
                g.menuPage = 'main'; g.menuSec = 'match'; g.menuOpen = true;
                g.menuGroup.visible = true;
                g.camera.position.set(0, 1.4, 0.9);
                g.camera.lookAt(0, 1.3, -1.2);
                g.camera.updateMatrixWorld(true);
                g.anchorMenu(); g.drawMenu();
                g.renderer.render(g.scene, g.camera);
                return g.renderer.domElement.toDataURL('image/png');
            }}""")
            open(path, "wb").write(base64.b64decode(shot.split(",", 1)[1]))
        await page.evaluate("() => { window.__setLang('es', window.__game); }")

        # página multi reescalada
        multi = await page.evaluate("""() => {
            const g = window.__game;
            g.menuOpen = true; g.menuPage = 'multi'; g.drawMenu();
            const ids = g.menuRects.map((r) => r.id);
            const okHost = ids.includes('net:host') && ids.includes('net:join') && ids.includes('tab:main');
            g.menuPage = 'join'; g.drawMenu();
            const idsJ = g.menuRects.map((r) => r.id);
            g.menuPage = 'main'; g.drawMenu();
            return { okHost, keys: idsJ.filter((i) => i.startsWith('key:')).length };
        }""")
        check(multi["okHost"], "página multi: host/join/volver presentes")
        check(multi["keys"] >= 30, f"teclado de código completo ({multi['keys']} teclas)")

        # la página carga sin errores JS
        check(not errors, f"sin errores de página ({errors[:2]})")

        await browser.close()

    if fails:
        print("\nFALLOS:", len(fails))
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("\nTODO OK")

asyncio.run(main())
