#!/usr/bin/env python3
"""Verificación headless v2.24 — los 4 bugs del menú/multijugador:
  1) CURSOR SIN ESPEJO VERTICAL: el punto del panel se dibuja en (uv.y-0.5);
     apuntando con un rayo sintético a la zona de un botón, el hover y el
     cursor caen EXACTAMENTE ahí (arriba->arriba, abajo->abajo).
  2) SIN DOBLE PULSACIÓN: dos onSelectStart seguidos (simulan el duplicado de
     three.js) = UN solo efecto: basculantes basculan 1 vez, teclado no
     duplica, hostRoom no se llama dos veces.
  3) TECLADO DEL CÓDIGO: escribir A,B,2,C,D paso a paso -> 'AB2CD'.
  4) CREAR SALA: clic (duplicado incluido) -> sala 'waiting' con código de 5.
Estáticos: 1 listener de selectstart/squeeze, fórmula del cursor corregida,
guardias de re-entrada en NetLink.
"""
import asyncio, base64 as b64, json, sys, re
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

# ---------------- estáticos sobre la build ----------------
src = open(HTML, encoding="utf-8").read()
fails = []

def static_check():
    # listener por ESPACIO de mando (session.addEventListener es el kick de
    # audio y es intencional; no duplica clicks)
    n_sel_tr = len(re.findall(r"targetRay\.addEventListener\(\s*['\"]selectstart['\"]", src))
    n_sel_gr = len(re.findall(r"grip\.addEventListener\(\s*['\"]selectstart['\"]", src))
    n_sq_gr = len(re.findall(r"grip\.addEventListener\(\s*['\"]squeezestart['\"]", src))
    n_sq_tr = len(re.findall(r"targetRay\.addEventListener\(\s*['\"]squeezestart['\"]", src))
    print(f"estáticos: select targetRay={n_sel_tr} grip={n_sel_gr} · squeeze grip={n_sq_gr} targetRay={n_sq_tr}")
    if n_sel_tr != 1 or n_sel_gr != 0: fails.append(f"selectstart mal registrado: targetRay={n_sel_tr} grip={n_sel_gr}")
    if n_sq_gr != 1 or n_sq_tr != 0: fails.append(f"squeeze mal registrado: grip={n_sq_gr} targetRay={n_sq_tr}")
    if "(0.5 - hit.uv.y)" in src:
        fails.append("el cursor sigue con la fórmula espejada (0.5 - hit.uv.y)")
    if "(hit.uv.y - 0.5) * 1.08" not in src:
        fails.append("no se encuentra la fórmula corregida (hit.uv.y - 0.5) * 1.08")
    if "this._lastSelect[i] = nowSel" not in src:
        fails.append("falta la guardia temporal anti-duplicado en onSelectStart")
    if "this.status === 'creating' || this.status === 'waiting'" not in src:
        fails.append("falta la guardia de re-entrada en hostRoom")
    if "if (this.status === 'joining' || this.status === 'online') return;" not in src:
        fails.append("falta la guardia de re-entrada en joinRoom")

# ---------------- helpers in-page ----------------
JS_HELPERS = """
() => {
  const g = window.__game;
  g.renderer.xr.isPresenting = true;          // simular sesión XR
  g.connected = [true, true];                 // mandos presentes (para updateMenu)
  g.camera.position.set(0, 1.4, 0.9);         // de frente al panel (sin tilte)
  g.camera.lookAt(0, 1.3, -1);
  g.camera.updateMatrixWorld(true);
  if (!g.menuOpen) g.toggleMenu();
  g.anchorMenu();                             // v2.28: panel DELANTE de la cabeza
  g._menuAnchorUntil = 0;                     // test determinista: sin flotación
  g.drawMenu();
  return true;
}
"""

JS_AIM = """(rectId) => {
  const g = window.__game;
  // centro del rect (px canvas) -> coords del plano 0.28×0.35
  const r = g.menuRects.find((q) => q.id === rectId);
  if (!r) return { ok: false, why: 'no rect ' + rectId };
  const cx = r.x + r.w / 2, cy = r.y + r.h / 2;
  const ux = cx / 1024, uy = 1 - cy / 1536;
  const lx = (ux - 0.5) * 0.72, ly = (uy - 0.5) * 1.08;
  // rayo vertical -Z que atraviesa ese punto exacto del plano del panel
  // (v2.28: el panel está DELANTE del jugador; su centro es menuGroup.position,
  // con yaw ~0 porque la cámara mira recto hacia él).
  // OJO: three.js pone matrixAutoUpdate=false en los controladores XR ->
  // hay que reactivarlo para que el position.set() tenga efecto.
  // re-anclar en cada apuntado (congelar la flotación) y refrescar matrices
  g.anchorMenu();
  g._menuAnchorUntil = 0;
  g.menuGroup.updateMatrixWorld(true);
  g.rays[0].matrixAutoUpdate = true;
  g.rays[0].position.set(lx, g.menuGroup.position.y + ly, 0.5);
  g.rays[0].quaternion.set(0, 0, 0, 1);
  g.rig.updateMatrixWorld(true);
  g.menuHover = [-1, -1];
  g.updateMenu();
  const dot = g.menuDots[0];
  const idxHover = g.menuHover[0];
  return {
    ok: true, lx: +lx.toFixed(4), ly: +ly.toFixed(4),
    hoverId: idxHover >= 0 ? g.menuRects[idxHover].id : null,
    dot: dot.visible ? { x: +dot.position.x.toFixed(4), y: +dot.position.y.toFixed(4), z: +dot.position.z.toFixed(4) } : null,
    beamVisible: g.menuLines[0].visible,
  };
}"""

async def main():
    static_check()
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(3600)

        ok = await page.evaluate("() => { const g = window.__game; g.audio.kick(); return !!g; }")
        if not ok: fails.append("no hay window.__game")

        # ---------- 1) CURSOR SIN ESPEJO VERTICAL ----------
        await page.evaluate(JS_HELPERS)
        # arriba del panel: 'start' (sección JUGAR PARTIDO desplegada)
        aim = await page.evaluate(JS_AIM, "start")
        print("aim start:", json.dumps(aim))
        if not aim.get("ok"):
            fails.append("no se pudo apuntar (rect no encontrado): " + str(aim))
        else:
            if aim["hoverId"] != "start":
                fails.append(f"el hover NO cae en el botón apuntado: {aim['hoverId']}")
            if not aim["dot"]:
                fails.append("el cursor no aparece sobre el panel")
            else:
                if abs(aim["dot"]["x"] - aim["lx"]) > 0.004 or abs(aim["dot"]["y"] - aim["ly"]) > 0.004:
                    fails.append(f"el cursor no coincide con el impacto: {aim['dot']} vs ({aim['lx']},{aim['ly']})")
                if aim["dot"]["y"] <= 0:
                    fails.append(f"el cursor sigue ESPEJADO (y<=0 apuntando arriba): {aim['dot']}")
        # abajo del panel: 'close' (y≈506-552)
        aim2 = await page.evaluate(JS_AIM, "close")
        print("aim close:", json.dumps(aim2))
        if aim2.get("ok"):
            if aim2["hoverId"] != "close":
                fails.append(f"apuntando abajo el hover no es 'close': {aim2['hoverId']}")
            if aim2["dot"] and aim2["dot"]["y"] >= 0:
                fails.append(f"cursor espejado apuntando abajo (y>=0): {aim2['dot']}")
            if aim2["dot"] and abs(aim2["dot"]["y"] - aim2["ly"]) > 0.004:
                fails.append(f"cursor no coincide abajo: {aim2['dot']} vs {aim2['ly']}")

        # ---------- captura con el cursor EN el botón inferior ----------
        # (isPresenting=true fuerza la ruta XR del renderer → frames negros sin
        # sesión real; se desactiva SOLO para el render de la captura)
        shot = await page.evaluate("""() => {
            const g = window.__game;
            g.renderer.xr.isPresenting = false;
            g.camera.position.set(0, 0.16, 0.75);
            g.camera.lookAt(0, 0.16, 0);
            g.camera.updateMatrixWorld(true);
            g.renderer.render(g.scene, g.camera);
            const d = g.renderer.domElement.toDataURL('image/png');
            g.renderer.xr.isPresenting = true;
            return d;
        }""")
        png = b64.b64decode(shot.split(",", 1)[1])
        open("/home/z/my-project/download/captura-v224-cursor.png", "wb").write(png)

        # ---------- 2) SIN DOBLE PULSACIÓN (basculantes) ----------
        # press(): resetea la guardia temporal y simula el evento duplicado de
        # three.js (2 entregas del MISMO disparo) → debe valer UNA sola vez.
        toggles = await page.evaluate("""() => {
            const g = window.__game;
            const out = {};
            const idx = (id) => g.menuRects.findIndex((r) => r.id === id);
            const press = (id) => {
                g._lastSelect[0] = 0;            // aíslar de pulsaciones previas del test
                g.menuHover = [idx(id), -1];
                g.onSelectStart(0); g.onSelectStart(0);
            };
            g.menuPage = 'main';
            if (g.menuSec !== 'opts') {
                const i = g.menuRects.findIndex((r) => r.id === 'sec:opts');
                if (i >= 0) g.menuClick(i);
            }
            g.drawMenu();
            const amb0 = g.audio.ambience;
            press('amb');
            out.ambAfterDouble = g.audio.ambience; out.amb0 = amb0;
            press('amb');   // pulsación siguiente (guardia reseteada) = restaurar
            out.ambAfterSingle = g.audio.ambience;
            const v0 = g.audio.voice;
            press('voz');
            out.voz0 = v0; out.vozAfterDouble = g.audio.voice;
            out.vozPersist = localStorage.getItem('ppxr_voz_v1');
            press('voz');
            out.vozRestored = g.audio.voice === v0;
            const t0 = g.showTrail;
            press('trail');
            out.trailAfterDouble = g.showTrail; out.trail0 = t0;
            press('trail');
            out.trailRestored = g.showTrail === t0;
            return out;
        }""")
        print("toggles:", json.dumps(toggles))
        # Con dedup, doble pulsación = UNA basculación (antes: dos = estado original)
        if toggles["ambAfterDouble"] == toggles["amb0"]:
            fails.append("la doble pulsación no basculó NI UNA vez (seguiría muerto)")
        if toggles["ambAfterSingle"] != toggles["amb0"]:
            fails.append("la pulsación simple no restaura el estado del ambiente")
        if (toggles["vozAfterDouble"] == toggles["voz0"]):
            fails.append("el megáfono no basculó con la doble pulsación (sigue muerto)")
        if (toggles["vozPersist"] == '1') != toggles["vozAfterDouble"]:
            fails.append("el estado persistido del megáfono no coincide con el visible")
        if toggles["vozPersist"] not in ('0', '1'):
            fails.append("el megáfono no persiste")
        if not toggles["vozRestored"]:
            fails.append("el megáfono no se restauró")
        if toggles["trailAfterDouble"] == toggles["trail0"]:
            fails.append("la estela no basculó con la doble pulsación")
        if not toggles["trailRestored"]:
            fails.append("la estela no se restauró")

        # ---------- 3) TECLADO SIN DUPLICAR ----------
        kb = await page.evaluate("""() => {
            const g = window.__game;
            const out = {};
            const idx = (id) => g.menuRects.findIndex((r) => r.id === id);
            const press = (id) => {
                g._lastSelect[0] = 0;
                g.menuHover = [idx(id), -1];
                g.onSelectStart(0); g.onSelectStart(0);
            };
            g.menuPage = 'multi'; g.drawMenu();
            press('net:join');
            out.pageAfterJoin = g.menuPage;
            g._joinCode = '';
            press('key:A'); out.afterA = g._joinCode;
            press('key:B'); out.afterB = g._joinCode;
            press('key:2'); out.after2 = g._joinCode;
            press('key:C'); out.afterC = g._joinCode;
            press('key:D'); out.full = g._joinCode;
            press('key:del'); out.afterDel = g._joinCode;
            return out;
        }""")
        print("teclado:", json.dumps(kb))
        if kb["pageAfterJoin"] != 'join':
            fails.append("el botón INTRODUCIR CÓDIGO no abre el teclado")
        if kb["afterA"] != "A":
            fails.append(f"la primera letra quedó mal: '{kb['afterA']}' (esperado 'A')")
        if kb["afterB"] != "AB" or kb["after2"] != "AB2" or kb["afterC"] != "AB2C":
            fails.append(f"la escritura acumula mal: {kb}")
        if kb["full"] != "AB2CD":
            fails.append(f"el código se escribió mal: '{kb['full']}' (esperado 'AB2CD')")
        if kb["afterDel"] != "AB2C":
            fails.append(f"el borrado no funciona: '{kb['afterDel']}'")

        # ---------- 4) CREAR SALA (con doble pulsación incluida) ----------
        await page.evaluate("() => { const g = window.__game; g._joinCode=''; g.menuPage='multi'; g.drawMenu(); }")
        host = await page.evaluate("""() => {
            const g = window.__game;
            const idx = g.menuRects.findIndex((r) => r.id === 'net:host');
            g._lastSelect[0] = 0;
            g.menuHover = [idx, -1];
            g.onSelectStart(0); g.onSelectStart(0);   // duplicado simulado
            return { status: g.net.status, code: g.net.code, page: g.menuPage };
        }""")
        print("crear sala (tras clic):", json.dumps(host))
        if len(host["code"]) != 5:
            fails.append(f"el código de sala no se generó: '{host['code']}'")
        if host["status"] not in ('creating', 'waiting'):
            fails.append(f"estado inesperado tras crear sala: {host['status']}")
        # esperar a 'waiting' (peer abierto en el servidor de salas)
        wait = await page.evaluate("""() => new Promise((res) => {
            const g = window.__game;
            let n = 0;
            const iv = setInterval(() => {
                n++;
                if (g.net.status === 'waiting') { clearInterval(iv); res({ ok: true, code: g.net.code }); }
                else if (n > 80) { clearInterval(iv); res({ ok: false, status: g.net.status, msg: g.net.statusMsg }); }
            }, 100);
        })""")
        print("sala:", json.dumps(wait))
        if not wait.get("ok"):
            fails.append(f"la sala no llegó a 'waiting': {wait}")
        else:
            if len(wait["code"]) != 5:
                fails.append(f"código de sala inválido: {wait['code']}")
            # el panel debe tener SOLO el botón cancelar en 'waiting' (sin crear/unirse)
            ids = await page.evaluate("""() => { const g = window.__game; g.drawMenu(); return g.menuRects.map((r) => r.id); }""")
            if 'net:cancel' not in ids:
                fails.append(f"la página de espera no muestra CANCELAR SALA: {ids}")
            # el código dibujado en el canvas: comprobar que el texto del código aparece
            codeDrawn = await page.evaluate("""() => {
                const g = window.__game;
                g.drawMenu();
                const c = g.menuCanvas.getContext('2d');
                const data = c.getImageData(0, 130, 512, 110).data;   // zona del código
                let ink = 0;
                for (let k = 3; k < data.length; k += 4) if (data[k] > 200) ink++;
                return ink;
            }""")
            if codeDrawn < 500:
                fails.append(f"el código no se dibuja grande en el panel (tinta={codeDrawn})")
        await page.evaluate("() => { window.__game.net.cancel(); }")

        # capturas de páginas del menú
        for page_id, name in (("main", "menu"), ("multi", "multi")):
            shot = await page.evaluate("""(pid) => {
                const g = window.__game;
                g.menuPage = pid; g.menuHover = [-1, -1]; g.drawMenu();
                g.renderer.xr.isPresenting = false;
                g.camera.position.set(0, 0.16, 0.75);
                g.camera.lookAt(0, 0.16, 0);
                g.camera.updateMatrixWorld(true);
                g.renderer.render(g.scene, g.camera);
                const d = g.renderer.domElement.toDataURL('image/png');
                g.renderer.xr.isPresenting = true;
                return d;
            }""", page_id)
            png = b64.b64decode(shot.split(",", 1)[1])
            open(f"/home/z/my-project/download/captura-v224-{name}.png", "wb").write(png)

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    if errors: fails.append("hubo errores de página")
    if fails:
        print("FALLOS:"); [print(" -", f) for f in fails]; sys.exit(1)
    print("TODO OK")

asyncio.run(main())
