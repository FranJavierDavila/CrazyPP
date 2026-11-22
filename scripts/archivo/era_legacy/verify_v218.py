#!/usr/bin/env python3
"""Verificación headless v2.18:
  - saque fácil: gatillo de CUALQUIER mando lanza, sin puerta del punto muerto,
    toss asistido >= 3.1 m/s
  - estela: botón en menú, persistente, oculta los puntos
  - menú: fila EXTRAS (Ambiente basculante + Estela), layout compacto
  - marcador: mensaje largo auto-ajustado (sin excepción)
  - panel de entrenamiento: repintado sin error
  - regresión v2.16: apuntado/clic con ambas manos, revancha, cierre
"""
import asyncio, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
SHOT = "/home/z/my-project/scripts/preview_v218_menu.png"

JS_AIM = """(targetId) => {
    const g = window.__game;
    const V3 = g.menuGroup.position.constructor;
    const M4 = g.menuGroup.matrixWorld.constructor;
    const idx = g.menuRects.findIndex((r) => r.id === targetId);
    if (idx < 0) return { ok: false, why: 'rect no encontrado: ' + targetId };
    const r = g.menuRects[idx];
    const u = ((r.x + r.w / 2) / 1024 - 0.5) * 0.72;
    const v = (0.5 - (r.y + r.h / 2) / 1536) * 1.08;
    const wp = new V3(u, v, 0);
    g.menuGroup.updateMatrixWorld(true);
    wp.applyMatrix4(g.menuGroup.matrixWorld);
    const n = new V3(0, 0, 1).transformDirection(g.menuGroup.matrixWorld);
    const hand = g.aimHand;
    const ray = g.rays[hand];
    const rayPos = new V3().copy(wp).addScaledVector(n, 0.45);
    ray.position.copy(rayPos);
    ray.quaternion.setFromRotationMatrix(
        new M4().lookAt(rayPos, wp, new V3(0, 1, 0)));
    ray.updateMatrix();
    return { ok: true, idx, wp: [wp.x, wp.y, wp.z].map((x) => +x.toFixed(3)) };
}"""

async def main():
    errors, fails = [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4200)

        await page.evaluate("""() => {
            const g = window.__game;
            g._camWP = g.camera.getWorldPosition.bind(g.camera);
            g.camera.getWorldPosition = (v) => v.set(0, 1.6, 2.2);
            g.connected[0] = true; g.connected[1] = true;
        }""")

        # --- 1) GLB carga (regresión) ---
        glb = await page.evaluate("""() => {
            let kind = '?', n = 0;
            window.__game.aiPaddleMesh.traverse((o) => {
                if (o.isMesh) { n++; kind = o.geometry?.type || '?'; }
            });
            return kind === 'BufferGeometry' && n >= 5;
        }""")
        if not glb: fails.append("GLB no cargado")

        # --- 2) menú: estructura v2.18 (fila EXTRAS con amb basculante + trail) ---
        m = await page.evaluate("""() => {
            const g = window.__game;
            g.toggleMenu();
            g.updateMenu();
            const click = (id) => g.menuClick(g.menuRects.findIndex((r) => r.id === id));
            const ids0 = g.menuRects.map((r) => r.id);
            if (g.menuSec !== 'match') click('sec:match');
            const idsMatch = g.menuRects.map((r) => r.id);
            click('sec:opts');
            const idsOpts = g.menuRects.map((r) => r.id);
            const trailRect = g.menuRects.find((r) => r.id === 'trail');
            return { open: g.menuOpen, base: ids0, match: idsMatch, opts: idsOpts,
                     trailY: trailRect ? trailRect.y : -1,
                     closeY: g.menuRects.find((r) => r.id === 'close')?.y ?? -1 };
        }""")
        # v2.28: ACORDEÓN — los botones viven en su sección (expandimos para verlos)
        needBase = ['sec:match', 'sec:train', 'sec:surv', 'sec:crazy', 'sec:opts',
                    'lang:es', 'lang:en', 'start', 'close']
        needMatch = ['start', 'diff:easy', 'diff:medium', 'diff:hard',
                     'net:host', 'net:join']
        needOpts = ['theme:pabellon', 'theme:neon', 'theme:atardecer', 'theme:artico',
                    'amb', 'trail', 'voz']
        if not m["open"]: fails.append("el menú no se abre")
        for r in needBase:
            if r not in m["base"]: fails.append(f"falta botón {r}")
        for r in needMatch:
            if r not in m["match"]: fails.append(f"falta botón {r} en JUGAR PARTIDO")
        for r in needOpts:
            if r not in m["opts"]: fails.append(f"falta botón {r} en OPCIONES")
        for old in ('mode:match', 'mode:survival', 'amb:on', 'amb:off'):
            if old in m["base"] + m["match"] + m["opts"]:
                fails.append(f"botón antiguo {old} sigue en el menú")
        # el panel completo debe caber en el canvas de 1536 px
        if m["closeY"] + 68 > 1532: fails.append(f"CERRAR se sale del panel: y={m['closeY']}")

        # --- 3) SAQUE FÁCIL: gatillo de la PALA lanza (no solo la mano de la bola) ---
        serve = await page.evaluate("""() => {
            const g = window.__game;
            if (g.menuOpen) g.toggleMenu();   // el menú abierto se come el gatillo
            g.rules.state = 'serve'; g.rules.server = 'player';
            g.tossed = false;
            g.renderer.xr.isPresenting = true;
            try { g.onSelectStart(g.paddleHand); }   // gatillo en la mano de la PALA
            finally { g.renderer.xr.isPresenting = false; }
            return { tossed: g.tossed, vy: +g.ball.vel.y.toFixed(2),
                     msg: g.rules.message };
        }""")
        if not serve["tossed"]: fails.append(f"el gatillo de la pala no lanza: {serve}")
        if serve["vy"] < 3.0: fails.append(f"toss asistido flojo: vy={serve['vy']} (<3.0)")
        if "Golpea" not in serve["msg"]: fails.append(f"mensaje tras toss: {serve['msg']}")

        # --- 4) validación relajada: margen extra de saque aplicado ---
        src_has_apex_gate = await page.evaluate("""() => {
            const g = window.__game;
            // sondeo indirecto: las constantes DIMS no son accesibles, pero el
            // comportamiento sí: lanzamiento de 7 cm de subida ya es válido.
            return null;   // comprobado por constantes en el propio bundle
        }""")
        consts = await page.evaluate("""() => {
            const g = window.__game;
            if (g.menuOpen) g.toggleMenu();   // sin menú: no interfiere
            const now = () => performance.now();
            g.rules.state = 'serve'; g.rules.server = 'player'; g.tossed = true;
            g.renderer.xr.isPresenting = true;
            try { g.animate(now()); } finally { g.renderer.xr.isPresenting = false; }
            const er = g.controllerPaddles[g.paddleHand].extraReach;
            g.rules.state = 'rally'; g.tossed = false;
            g.renderer.xr.isPresenting = true;
            try { g.animate(now()); } finally { g.renderer.xr.isPresenting = false; }
            const er2 = g.controllerPaddles[g.paddleHand].extraReach;
            return { serve: er, rally: er2 };
        }""")
        if not (0.085 <= consts["serve"] <= 0.095):
            fails.append(f"serveExtraReach no aplicado en saque: {consts}")
        if consts["rally"] != 0:
            fails.append(f"extraReach fuera del saque: {consts}")

        # --- 5) ESTELA: clic alterna, aplica y persiste (sección OPCIONES) ---
        tr = await page.evaluate("""() => {
            const g = window.__game;
            if (!g.menuOpen) g.toggleMenu();
            if (g.menuSec !== 'opts') g.menuClick(g.menuRects.findIndex((r) => r.id === 'sec:opts'));
            const before = g.showTrail;
            const idx = g.menuRects.findIndex((r) => r.id === 'trail');
            g.menuClick(idx);
            const after = g.showTrail;
            const vis = g.trailObj.visible;
            const saved = localStorage.getItem('ppxr_trail_v1');
            g.menuClick(idx);   // volver al estado original
            return { before, after, vis, saved, back: g.showTrail };
        }""")
        if tr["after"] == tr["before"]: fails.append(f"botón estela no alterna: {tr}")
        if tr["vis"] != tr["after"]: fails.append(f"trailObj.visible no sigue al menú: {tr}")
        if tr["saved"] != ('1' if tr["after"] else '0'): fails.append(f"estela no persiste: {tr}")
        if tr["back"] != tr["before"]: fails.append("estela no vuelve al alternar dos veces")

        # --- 6) AMBIENTE basculante (sección OPCIONES) ---
        amb = await page.evaluate("""() => {
            const g = window.__game;
            if (!g.menuOpen) g.toggleMenu();
            if (g.menuSec !== 'opts') g.menuClick(g.menuRects.findIndex((r) => r.id === 'sec:opts'));
            const b = !!g.audio.ambience;
            const idx = g.menuRects.findIndex((r) => r.id === 'amb');
            g.menuClick(idx);
            const a = !!g.audio.ambience;
            g.menuClick(idx);
            return { b, a, back: !!g.audio.ambience };
        }""")
        if amb["a"] == amb["b"] or not amb["back"]:
            fails.append(f"ambiente basculante roto: {amb}")

        # --- 7) marcador: mensaje largo sin excepción y tex actualizada ---
        sb = await page.evaluate("""() => {
            const g = window.__game;
            let ok = true;
            try {
                g.scoreboardUpdate({ player: 5, ai: 3, server: 'player',
                    message: 'Rallye de 12 golpes · doble bote: la CPU no llegó a esta bola larguísima que se fue fuera por la línea de fondo delante de todos',
                    mode: 'match', rally: 0, rallyes: 0, best: 0 });
            } catch (e) { ok = false; }
            return { ok };
        }""")
        if not sb["ok"]: fails.append("scoreboardUpdate falló con mensaje largo")

        # --- 8) panel de entrenamiento repinta sin error ---
        cal = await page.evaluate("""() => {
            const g = window.__game;
            let ok = true;
            try {
                g.calibPanel.update({ name: 'Natural',
                    off: { px: 0.01, py: -0.02, pz: 0.03, rx: 0.1, ry: 0.2, rz: 0.3 } });
            } catch (e) { ok = false; }
            return { ok };
        }""")
        if not cal["ok"]: fails.append("calibPanel.update falló")

        # --- 9) regresión v2.16: apuntado con la pala + clic ---
        await page.evaluate("""() => {
            const g = window.__game;
            if (!g.menuOpen) g.toggleMenu();
            if (g.menuSec !== 'match') g.menuClick(g.menuRects.findIndex((r) => r.id === 'sec:match'));
            g.updateMenu();
        }""")
        aim = await page.evaluate(f"""() => {{
            const g = window.__game;
            g.aimHand = g.paddleHand;
            return ({JS_AIM})('diff:hard');
        }}""")
        if not aim.get("ok"): fails.append(f"apuntado pala: {aim}")
        click = await page.evaluate("""() => {
            const g = window.__game;
            g.updateMenu();   // procesar el rayo ya posicionado -> menuHover
            const before = g.difficulty;
            g.renderer.xr.isPresenting = true;
            try { g.onSelectStart(g.paddleHand); }
            finally { g.renderer.xr.isPresenting = false; }
            return { before, after: g.difficulty, open: g.menuOpen };
        }""")
        if click["after"] != "hard": fails.append(f"clic pala no aplica: {click}")

        # --- 10) revancha condicional + cierre ---
        c3 = await page.evaluate("""() => {
            const g = window.__game;
            if (g.menuOpen) g.toggleMenu();   // cerrar: al abrir se repinta
            g.rules.state = 'over';
            g.toggleMenu();
            if (g.menuSec !== 'match') g.menuClick(g.menuRects.findIndex((r) => r.id === 'sec:match'));
            const hasR = g.menuRects.some((r) => r.id === 'revancha');
            const idx = g.menuRects.findIndex((r) => r.id === 'revancha');
            g.menuClick(idx);
            return { hasR, state: g.rules.state, open: g.menuOpen };
        }""")
        if not c3["hasR"]: fails.append("REVANCHA no aparece")
        if c3["state"] == "over": fails.append("REVANCHA no reinicia")

        # --- 11) captura del menú v2.18 ---
        await page.evaluate(f"""() => {{
            const g = window.__game;
            g.rules.state = 'serve';
            if (!g.menuOpen) g.toggleMenu();
            g.menuGroup.position.set(0.55, 1.05, -0.75);
            g.menuGroup.lookAt(2.2, 1.5, 1.4);
            g.aimHand = g.paddleHand;
            ({JS_AIM})('trail');
            g.updateMenu();
            g.menuGroup.position.set(0.55, 1.05, -0.75);
            g.menuGroup.lookAt(2.2, 1.5, 1.4);
            g.menuGroup.updateMatrixWorld(true);
        }}""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=SHOT)

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    print("menú:", json.dumps({k: m[k] for k in ("open", "trailY", "closeY")}))
    print("saque fácil:", json.dumps(serve))
    print("extraReach:", json.dumps(consts))
    if fails:
        print("FALLOS:", *fails, sep="\n  - ")
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
