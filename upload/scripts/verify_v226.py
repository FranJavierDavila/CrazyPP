#!/usr/bin/env python3
"""Verificación headless v2.26 — carteles oficiales de victoria/derrota.

  1) ESTÁTICOS: las dos imágenes JPEG oficiales van incrustadas (data URL),
     los mensajes de fin de partido dicen ¡HAS GANADO!/¡HAS PERDIDO! en la
     rama del anfitrión (Rules.update) y en la del invitado (applySync),
     y no queda rastro de los textos antiguos (¡VICTORIA!/DERROTA).
  2) FIN DE PARTIDO REAL: applyPoint -> 11-x dispara cartel + mensaje +
     megafonía; la revancha retira el cartel; el invitado ve SU perspectiva.
  3) CARTEL PINTADO CON EL ARTE: lectura directa del canvas del cartel
     (franja superior = cielo azul del arte oficial en AMBOS carteles) y
     capturas PNG para revisión visual.
"""
import asyncio, base64, io, json, sys
from PIL import Image
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

src = open(HTML, encoding="utf-8").read()
fails = []

# ---------------- 1) estáticos ----------------
def static_check():
    n = src.count("data:image/jpeg;base64,")
    if n < 2: fails.append(f"esperados >=2 carteles incrustados, hay {n}")
    if src.count("¡HAS GANADO! ·") < 1:
        fails.append("falta '¡HAS GANADO!' en anfitrión+invitado")
    if src.count("¡HAS PERDIDO! ·") < 1:
        fails.append("falta '¡HAS PERDIDO!' en anfitrión+invitado")
    for old in ("¡VICTORIA! ·", "DERROTA ·"):
        if old in src: fails.append(f"quedan textos antiguos: '{old}'")
    if "PlaneGeometry(1.5, 1.0)" not in src:
        fails.append("el cartel no usa el plano 3:2 (1.5 x 1.0)")
    if "return { group, draw, canvas, langChanged };" not in src:
        fails.append("falta el gancho de diagnóstico del canvas")

# ---------------- utilidades ----------------
def save_png(dataurl, path):
    png = base64.b64decode(dataurl.split(",", 1)[1])
    open(path, "wb").write(png)
    return png

def blue_share(png_bytes, tag):
    """Fracción de píxeles AZULES del cielo en el recorte central-superior
    (el cartel ocupa gran parte de esa zona; sin él la escena es oscura)."""
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    w, h = im.size
    box = im.crop((int(w*0.25), int(h*0.05), int(w*0.75), int(h*0.55)))
    px = list(box.getdata())
    n = len(px)
    blue = sum(1 for p in px if p[2] > 90 and p[2] > p[0] + 30)
    mr = sum(p[0] for p in px) / n
    mb = sum(p[2] for p in px) / n
    print(f"   {tag}: {100*blue/n:.1f}% píxeles azul-cielo (R medio {mr:.0f}, B medio {mb:.0f})")
    return blue / n

READ_TOP_STRIP = """() => {
    const g = window.__game;
    const c = g.fanfareBanner.canvas;
    const x = c.getContext('2d');
    const d = x.getImageData(0, 0, 1024, 45).data;   // cielo del arte oficial
    let r = 0, gr = 0, b = 0, n = d.length / 4;
    for (let i = 0; i < d.length; i += 4) { r += d[i]; gr += d[i+1]; b += d[i+2]; }
    return { r: r / n, g: gr / n, b: b / n, w: c.width, h: c.height };
}"""

# ---------------- 2+3) headless ----------------
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
        ok = await page.evaluate("() => !!window.__game")
        if not ok: fails.append("no hay __game")

        # --- sonido espiado (sin alterar el resto) ---
        await page.evaluate("""() => {
            const g = window.__game;
            g.__ann = []; g.__points = []; g.__apla = [];
            g.audio.announce = (t, f) => { g.__ann.push(String(t)); };
            g.audio.point = (w) => { g.__points.push(w); };
            g.audio.applause = (w) => { g.__apla.push(w); };
        }""")

        # marco de cámara para el cartel (banco de pruebas 2D)
        await page.evaluate("""() => {
            const g = window.__game;
            g.connected = [true, true];
            g.renderer.xr.isPresenting = false;
            g.camera.position.set(0, 1.35, 1.15);
            g.camera.lookAt(0, 1.7, -1.6);
            g.camera.updateMatrixWorld(true);
        }""")

        # ============ 2) VICTORIA real (11-x) ============
        win = await page.evaluate("""() => {
            const g = window.__game;
            g.rules.startMatch('match');
            g.rules.scorePlayer = 10; g.rules.scoreAi = 4;
            g.rules.state = 'rally'; g.rules.lastHitter = 'ai';
            g.rules.isServeBall = false; g.rules.serveOwnPending = false;
            g.rules.mustBounceOpp = false; g.rules.validBounce = false;
            g.processIntents(g.rules.applyPoint('player', 'noret_you'));
            const its = g.rules.update(2.5);          // pausa del punto -> 'over'
            const msg = g.rules.message;              // ANTES del logro (lo pisa)
            g.processIntents(its);                    // cartel + fanfarria + logro
            return { msg, st: g.rules.state,
                     visible: g.fanfareBanner.group.visible,
                     win: g.fanfareWin, ann: g.__ann.slice() };
        }""")
        if win["st"] != "over": fails.append(f"11-4 no acaba el partido: {win['st']}")
        if win["msg"] != "¡HAS GANADO! · 11-4 · gatillo: revancha":
            fails.append(f"mensaje de victoria: '{win['msg']}'")
        if not win["visible"] or win["win"] is not True:
            fails.append(f"cartel de victoria no visible: {json.dumps(win)}")
        if not any("Victoria" in a for a in win["ann"]):
            fails.append(f"megafonía de victoria: {win['ann']}")

        await page.wait_for_timeout(450)          # decodificación JPEG + repintado
        art = await page.evaluate(READ_TOP_STRIP)
        if art["w"] != 1024 or art["h"] != 683:
            fails.append(f"canvas del cartel {art['w']}x{art['h']} (esperado 1024x683)")
        if not (art["b"] > 110 and art["b"] > art["r"] + 30):
            fails.append(f"el cartel de victoria NO muestra el arte (RGB {art})")
        shot = await page.evaluate("""() => {
            const g = window.__game;
            g.renderer.render(g.scene, g.camera);
            return g.renderer.domElement.toDataURL('image/png');
        }""")
        png = save_png(shot, "/home/z/my-project/download/captura-v226-victoria.png")
        share = blue_share(png, "victoria")
        if share < 0.10:
            fails.append(f"captura victoria: cartel sin arte ({100*share:.0f}% azul)")

        # revancha: el cartel se retira al salir de 'over' (bucle animate)
        await page.evaluate("""() => { window.__game.rules.startMatch('match'); }""")
        await page.wait_for_timeout(300)
        rem = await page.evaluate("""() => ({
            visible: window.__game.fanfareBanner.group.visible,
            st: window.__game.rules.state })""")
        if rem["visible"]: fails.append(f"el cartel no se retira con la revancha: {rem}")

        # ============ 2) DERROTA real (x-11) ============
        lose = await page.evaluate("""() => {
            const g = window.__game;
            g.__ann.length = 0;
            g.rules.scorePlayer = 6; g.rules.scoreAi = 10;
            g.rules.state = 'rally'; g.rules.lastHitter = 'player';
            g.rules.isServeBall = false; g.rules.serveOwnPending = false;
            g.rules.mustBounceOpp = false; g.rules.validBounce = false;
            g.processIntents(g.rules.applyPoint('ai', 'wall'));
            const its = g.rules.update(2.5);
            const msg = g.rules.message;
            g.processIntents(its);
            return { msg, st: g.rules.state,
                     visible: g.fanfareBanner.group.visible, win: g.fanfareWin };
        }""")
        if lose["st"] != "over": fails.append(f"6-11 no acaba el partido: {lose['st']}")
        if lose["msg"] != "¡HAS PERDIDO! · 6-11 · gatillo: revancha":
            fails.append(f"mensaje de derrota: '{lose['msg']}'")
        if not lose["visible"] or lose["win"] is not False:
            fails.append(f"cartel de derrota no visible: {json.dumps(lose)}")

        await page.wait_for_timeout(450)
        art2 = await page.evaluate(READ_TOP_STRIP)
        if not (art2["b"] > 110 and art2["b"] > art2["r"] + 30):
            fails.append(f"el cartel de derrota NO muestra el arte (RGB {art2})")
        shot2 = await page.evaluate("""() => {
            const g = window.__game;
            g.renderer.render(g.scene, g.camera);
            return g.renderer.domElement.toDataURL('image/png');
        }""")
        png2 = save_png(shot2, "/home/z/my-project/download/captura-v226-derrota.png")
        share2 = blue_share(png2, "derrota")
        if share2 < 0.10:
            fails.append(f"captura derrota: cartel sin arte ({100*share2:.0f}% azul)")

        # ============ 2) INVITADO: mensaje con perspectiva ============
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
        if guest["msg"] != "¡HAS PERDIDO! · 5-11 · gatillo: revancha":
            fails.append(f"mensaje del invitado sin perspectiva: '{guest['msg']}'")
        if (guest["sp"], guest["sa"]) != (5, 11):
            fails.append(f"marcador del invitado: {json.dumps(guest)}")

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    if errors: fails.append("hubo errores de página")
    if fails:
        print("FALLOS:")
        for f in fails: print("  -", f)
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
