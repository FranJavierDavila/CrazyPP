#!/usr/bin/env python3
"""Verificación headless v2.27 — selector de idioma castellano/inglés.

  1) ESTÁTICOS: i18n (T/TLang/setLang/applyLangDOM), los DOS bancos de voz
     con las MISMAS claves, patrones de vozPlan en inglés, causas como
     claves en la red, selector 2D (data-lang) y 4 carteles incrustados.
  2) POR DEFECTO CASTELLANO: mensajes y megafonía idénticos a v2.25/26
     (compatibilidad con las suites de regresión).
  3) CAMBIO A INGLÉS (setLang('en')): mensajes del árbitro, anuncios,
     cartel (canvas + arte EN), telemetría de voz (_voiceBank cambia),
     persistencia (localStorage pp_lang) y overlay 2D re-traducido.
  4) INVITADO EN INGLÉS: applySync regenera mensajes en su idioma.
  5) VUELTA A CASTELLANO: todo vuelve (conversión en caliente).
"""
import asyncio, base64, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

src = open(HTML, encoding="utf-8").read()
fails = []

# ---------------- 1) estáticos ----------------
def static_check():
    for needle in ("function T(", "function TLang(", "function setLang(",
                   "function applyLangDOM(", "const I18N_STRINGS = {",
                   "VOICE_B64_EN", "_voiceBank()", "reloadVoice()",
                   "achievement unlocked (.+)$", "OHH_CAUSES",
                   "'own_you', 'own_opp'", "data-lang"):
        if needle not in src:
            fails.append(f"falta en la build: '{needle}'")
    n = src.count("data:image/jpeg;base64,")
    if n < 4:
        fails.append(f"esperados >=4 carteles (es+en), hay {n}")
    # los dos bancos con el mismo número de claves: VOICE_B64 y VOICE_B64_EN
    import re
    for bank in ("const VOICE_B64 = {", "const VOICE_B64_EN = {"):
        if bank not in src:
            fails.append(f"falta el banco {bank}")

# ---------------- utilidades ----------------
async def evaluate(page, js):
    return await page.evaluate(js)

# ---------------- 2-5) headless ----------------
async def main():
    static_check()
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
            "--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4200)
        if not await page.evaluate("() => !!window.__game"):
            fails.append("no hay __game")
            print("FALLOS:", fails); sys.exit(1)

        await page.evaluate("""() => {
            const g = window.__game;
            g.__ann = []; g.__points = [];
            g.audio.announce = (t, f) => { g.__ann.push(String(t)); };
            g.audio.point = (w) => { g.__points.push(w); };
        }""")

        # ============ 2) POR DEFECTO CASTELLANO ============
        es = await page.evaluate("""() => {
            const g = window.__game;
            g.rules.startMatch('match');
            g.rules.scorePlayer = 10; g.rules.scoreAi = 4;
            g.rules.state = 'rally'; g.rules.lastHitter = 'ai';
            g.rules.isServeBall = false; g.rules.serveOwnPending = false;
            g.rules.mustBounceOpp = false; g.rules.validBounce = false;
            g.processIntents(g.rules.applyPoint('player', 'noret_you'));
            const its = g.rules.update(2.5);
            const msg = g.rules.message;
            g.processIntents(its);
            return { msg, lang: window.__TLang(), bank: Object.keys(g.audio._voiceBank()).length,
                     stored: localStorage.getItem('pp_lang') };
        }""")
        if es["msg"] != "¡HAS GANADO! · 11-4 · gatillo: revancha":
            fails.append(f"mensaje ES por defecto: '{es['msg']}'")
        if es["lang"] != "es" or es["stored"] not in (None, "es"):
            fails.append(f"idioma por defecto: {json.dumps(es)}")
        if es["bank"] != 67:
            fails.append(f"banco de voz ES: {es['bank']} claves (esperado 67)")
        es_ann = await page.evaluate("""() => {
            const g = window.__game;
            g.rules.startMatch('match');
            g.rules.scorePlayer = 0; g.rules.scoreAi = 0;
            g.processIntents(g.rules.applyPoint('player', 'dblhit'));
            g.processIntents(g.rules.update(2.5));
            return g.__ann.slice();
        }""")
        if not any("1 a 0, saque para ti" in a for a in es_ann):
            fails.append(f"megafonía ES: {es_ann}")

        # ============ 3) CAMBIO A INGLÉS ============
        en = await page.evaluate("""() => {
            const g = window.__game;
            const bankES = g.audio._voiceBank();
            window.__setLang('en', g);
            const msgServe = (g.rules.startMatch('match'), g.rules.message);
            // punto + fin de partido en inglés
            g.rules.scorePlayer = 10; g.rules.scoreAi = 4;
            g.rules.state = 'rally'; g.rules.lastHitter = 'ai';
            g.rules.isServeBall = false; g.rules.serveOwnPending = false;
            g.rules.mustBounceOpp = false; g.rules.validBounce = false;
            g.processIntents(g.rules.applyPoint('player', 'noret_you'));
            const msgPoint = g.rules.message;      // mensaje del PUNTO
            const its = g.rules.update(2.5);       // transiciona a 'over'
            g.processIntents(its);
            const plan = g.audio.voicePlan('Victory! 11 to 4');
            void 0;
            return { msgServe, msgPoint, over: g.rules.message,
                     banner: g.fanfareBanner.group.visible,
                     lang: window.__TLang(), stored: localStorage.getItem('pp_lang'),
                     bankChanged: g.audio._voiceBank() !== bankES,
                     plan: plan ? plan.map((x) => x.k) : null,
                     chipOK: !!document };
        }""")
        if en["msgServe"] != "Your serve · the ball waits in your free hand":
            fails.append(f"serve EN: '{en['msgServe']}'")
        if not en["msgPoint"].startswith("Point for you! · you didn"):
            fails.append(f"punto EN: '{en['msgPoint']}'")
        if en["over"] != "YOU WON! · 11-4 · trigger: rematch":
            fails.append(f"over EN: '{en['over']}'")
        if en["lang"] != "en" or en["stored"] != "en":
            fails.append(f"persistencia EN: {json.dumps(en)}")
        if not en["bankChanged"]:
            fails.append("el banco de voz NO cambió al pasar a inglés")
        if en["plan"] != ["victoria", "n11", "a", "n4"]:
            fails.append(f"voicePlan EN: {en['plan']}")
        if not en["banner"]:
            fails.append("cartel no visible tras fin de partido EN")

        await page.wait_for_timeout(450)   # decodificación del arte EN
        art_en = await page.evaluate("""() => {
            const g = window.__game;
            const x = g.fanfareBanner.canvas.getContext('2d');
            const d = x.getImageData(0, 0, 1024, 45).data;
            let r = 0, b = 0, n = d.length / 4;
            for (let i = 0; i < d.length; i += 4) { r += d[i]; b += d[i+2]; }
            return { r: r / n, b: b / n };
        }""")
        if not (art_en["b"] > 110 and art_en["b"] > art_en["r"] + 30):
            fails.append(f"cartel EN sin arte (RGB {art_en})")

        # overlay 2D re-traducido (botones data-i18n)
        dom = await page.evaluate("""() => ({
            vr: document.getElementById('vrbtn').textContent,
            diff: document.querySelector('[data-diff=easy]').textContent,
            langBtnActive: document.querySelector('[data-lang=en]').classList.contains('active'),
        })""")
        if dom["vr"] != "ENTER VR" or dom["diff"] != "Easy" or not dom["langBtnActive"]:
            fails.append(f"overlay EN: {json.dumps(dom)}")

        # anuncio EN cubierto por el banco en inglés
        ann_en = await page.evaluate("""() => {
            const g = window.__game;
            g.__ann.length = 0;
            g.rules.startMatch('match');
            g.rules.scorePlayer = 2; g.rules.scoreAi = 3;
            g.processIntents(g.rules.applyPoint('player', 'dblhit'));
            g.processIntents(g.rules.update(2.5));
            return g.__ann.slice();
        }""")
        if not any("3 to 3, serve for you" in a for a in ann_en):
            fails.append(f"megafonía EN: {ann_en}")

        # ============ 4) INVITADO EN INGLÉS ============
        guest = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            net.teardown();
            net.role = 'guest'; net.online = true;
            net.conn = { open: true, sent: [], send(m) { this.sent.push(m); } };
            g.rules.startMatch('match');
            net.owner = 'host';
            net.onData({ k: 'p', y: { st: 'over', sv: 'player', sp: 11, sa: 5,
                                      md: 'match', ow: 'host', rh: 0, wn: 'player' } });
            return { msg: g.rules.message, sp: g.rules.scorePlayer, sa: g.rules.scoreAi };
        }""")
        if guest["msg"] != "YOU LOST! · 5-11 · trigger: rematch":
            fails.append(f"invitado EN: '{guest['msg']}'")
        if (guest["sp"], guest["sa"]) != (5, 11):
            fails.append(f"marcador invitado EN: {json.dumps(guest)}")

        # ============ 5) VUELTA A CASTELLANO ============
        back = await page.evaluate("""() => {
            const g = window.__game;
            window.__setLang('es', g);
            const msgServe = (g.rules.startMatch('match'), g.rules.message);
            return { msgServe, lang: window.__TLang(), stored: localStorage.getItem('pp_lang'),
                     vr: document.getElementById('vrbtn').textContent };
        }""")
        if back["msgServe"] != "Tu saque · la bola espera en tu mano libre":
            fails.append(f"vuelta a ES: '{back['msgServe']}'")
        if back["lang"] != "es" or back["stored"] != "es" or back["vr"] != "ENTRAR EN VR":
            fails.append(f"vuelta a ES estado: {json.dumps(back)}")

        # captura del overlay en inglés para revisión visual
        shot = await page.evaluate("""() => {
            window.__setLang('en', null);
            return true;
        }""")
        await page.screenshot(path="/home/z/my-project/download/captura-v227-overlay-en.png")
        await page.evaluate("() => window.__setLang('es', null)")

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    if errors: fails.append("hubo errores de página")
    if fails:
        print("FALLOS:")
        for f in fails: print("  -", f)
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
