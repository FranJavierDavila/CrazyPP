#!/usr/bin/env python3
"""Verificación headless v2.16: menú de muñeca con apuntado AMBAS manos
(la pala incluida) + anclaje tipo bandeja pegado a la muñeca."""
import asyncio, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
SHOT = "/home/z/my-project/scripts/preview_v216_menu.png"

JS_AIM = """(targetId) => {
    const g = window.__game;
    const V3 = g.menuGroup.position.constructor;   // clase Vector3 del módulo
    const M4 = g.menuGroup.matrixWorld.constructor; // clase Matrix4 del módulo
    const idx = g.menuRects.findIndex((r) => r.id === targetId);
    if (idx < 0) return { ok: false, why: 'rect no encontrado: ' + targetId };
    const r = g.menuRects[idx];
    // centro del botón en px de canvas -> coordenada local del plano 0.28x0.35
    const u = ((r.x + r.w / 2) / 512 - 0.5) * 0.28;
    const v = (0.5 - (r.y + r.h / 2) / 640) * 0.35;
    // punto mundial sobre el panel (usa matrixWorld ya anclada)
    const wp = new V3(u, v, 0);
    g.menuGroup.updateMatrixWorld(true);
    wp.applyMatrix4(g.menuGroup.matrixWorld);
    // normal del panel (+Z local) en mundo: el rayo entra por ese lado
    const n = new V3(0, 0, 1).transformDirection(g.menuGroup.matrixWorld);
    const hand = g.aimHand;
    const ray = g.rays[hand];
    const rayPos = new V3().copy(wp).addScaledVector(n, 0.45);
    ray.position.copy(rayPos);
    // orientar el rayo: los espacios targetRay apuntan por -Z. Matrix4.lookAt
    // (eye=rayo, target=panel) pone +Z de panel->rayo, así que -Z queda
    // apuntando al panel. (Object3D.lookAt NO sirve: lee la matrixWorld
    // obsoleta de estos objetos, matrixAutoUpdate=false en controladores XR.)
    ray.quaternion.setFromRotationMatrix(
        new M4().lookAt(rayPos, wp, new V3(0, 1, 0)));
    ray.updateMatrix();   // componer matrix a mano (XR lo hace cada frame)
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

        # La cámara de la demo orbita y el panel se reancla cada frame: para
        # poder apuntar con determinismo, congelamos la posición de la cabeza.
        await page.evaluate("""() => {
            const g = window.__game;
            g._camWP = g.camera.getWorldPosition.bind(g.camera);
            g.camera.getWorldPosition = (v) => v.set(0, 1.6, 2.2);
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

        # --- 2) apertura del menú y estructura de botones ---
        m = await page.evaluate("""() => {
            const g = window.__game;
            g.connected[0] = true; g.connected[1] = true;   // fingir mandos VR
            g.toggleMenu();
            g.updateMenu();                                 // ancla el panel
            const ids = g.menuRects.map((r) => r.id);
            return {
                open: g.menuOpen, vis: g.menuGroup.visible,
                hoverIsArray: Array.isArray(g.menuHover),
                lines: g.menuLines.length, dots: g.menuDots.length,
                n: ids.length, ids, ph: g.paddleHand,
            };
        }""")
        need = ['mode:match', 'mode:survival', 'diff:easy', 'diff:medium', 'diff:hard',
                'theme:pabellon', 'theme:neon', 'theme:atardecer', 'theme:artico',
                'amb:on', 'amb:off', 'close']
        if not m["open"] or not m["vis"]: fails.append("el menú no se abre")
        if not m["hoverIsArray"]: fails.append("menuHover no es array por mano")
        if m["lines"] != 2 or m["dots"] != 2: fails.append(
            f"líneas/puntos por mano: {m['lines']}/{m['dots']} != 2/2")
        for r in need:
            if r not in m["ids"]: fails.append(f"falta botón {r}")

        # --- 3) anclaje tipo bandeja: pegado a la muñeca libre ---
        anch = await page.evaluate("""() => {
            const g = window.__game;
            const ci = 1 - g.paddleHand;
            const gp = g.grips[ci].getWorldPosition(
                g.menuGroup.position.clone().set(0, 0, 0));
            const d = g.menuGroup.position.distanceTo(gp);
            return { d: +d.toFixed(3) };
        }""")
        if not (0.12 <= anch["d"] <= 0.20):
            fails.append(f"panel lejos de la muñeca: {anch['d']} m (esperado 0.16 constante)")

        # --- 4) APUNTADO CON LA PALA: hover + clic con el mando de la pala ---
        aim = await page.evaluate(f"""() => {{
            const g = window.__game;
            g.aimHand = g.paddleHand;          // la PALA apunta
            return ({JS_AIM})('diff:hard');
        }}""")
        if not aim.get("ok"): fails.append(f"apuntado pala: {aim}")
        hover = await page.evaluate("""() => {
            const g = window.__game;
            g.updateMenu();
            const ph = g.paddleHand;
            return {
                hover: g.menuHover[ph], other: g.menuHover[1 - ph],
                line: g.menuLines[ph].visible, dot: g.menuDots[ph].visible,
            };
        }""")
        if hover["hover"] != aim["idx"]:
            fails.append(f"hover pala: {hover['hover']} != {aim['idx']}")
        if not hover["line"] or not hover["dot"]:
            fails.append(f"láser/cursor de la pala no visibles: {json.dumps(hover)}")

        click = await page.evaluate("""() => {
            const g = window.__game;
            const before = g.difficulty;
            // el guardia isPresenting es correcto (en 2D no hay mandos):
            // simulamos sesión VR solo para probar la rama del gatillo
            g.renderer.xr.isPresenting = true;
            try { g.onSelectStart(g.paddleHand); }   // GATILLO de la mano de la pala
            finally { g.renderer.xr.isPresenting = false; }
            return { before, after: g.difficulty, msg: g.rules.message,
                     open: g.menuOpen };
        }""")
        if click["after"] != "hard":
            fails.append(f"clic con la pala no aplica dificultad: {json.dumps(click)}")
        if "DIFICULTAD" not in (click["msg"] or ""):
            fails.append(f"mensaje dificultad: {click['msg']}")
        if not click["open"]:
            fails.append("el menú se cerró al cambiar dificultad")

        # --- 5) hover INDEPENDIENTE por mano: la otra mano apunta a otro botón ---
        aim2 = await page.evaluate(f"""() => {{
            const g = window.__game;
            g.aimHand = 1 - g.paddleHand;      // la mano libre apunta a otra cosa
            return ({JS_AIM})('theme:neon');
        }}""")
        if not aim2.get("ok"): fails.append(f"apuntado mano libre: {aim2}")
        hov2 = await page.evaluate("""() => {
            const g = window.__game;
            g.updateMenu();
            return { ph: g.menuHover[g.paddleHand], oh: g.menuHover[1 - g.paddleHand],
                     diff: g.difficulty };
        }""")
        if hov2["oh"] != aim2["idx"]:
            fails.append(f"hover mano libre: {hov2['oh']} != {aim2['idx']}")
        if hov2["ph"] != aim["idx"]:
            fails.append(f"hover de la pala se perdió al apuntar con la otra: {json.dumps(hov2)}")

        # --- 6) tema aplicado desde la mano libre (persistencia) ---
        c1 = await page.evaluate("""() => {
            const g = window.__game;
            g.renderer.xr.isPresenting = true;
            try { g.onSelectStart(1 - g.paddleHand); }   // gatillo de la mano libre
            finally { g.renderer.xr.isPresenting = false; }
            return { theme: g.theme, saved: localStorage.getItem('ppxr_theme'),
                     wall: '#' + g.roomGroup.userData.wallMat.color.getHexString(),
                     open: g.menuOpen };
        }""")
        if c1["theme"] != "neon" or c1["saved"] != "neon" or c1["wall"] != "#0a0c16":
            fails.append(f"tema desde menú: {json.dumps(c1)}")

        # --- 7) MODO: aplica y CIERRA ---
        c2 = await page.evaluate("""() => {
            const g = window.__game;
            const idx = g.menuRects.findIndex((r) => r.id === 'mode:survival');
            g.menuClick(idx);
            return { mode: g.mode, rules: g.rules.mode, open: g.menuOpen };
        }""")
        if c2["mode"] != "survival" or c2["rules"] != "survival":
            fails.append(f"modo desde menú: {json.dumps(c2)}")
        if c2["open"]: fails.append("el menú no se cerró al cambiar de modo")

        # --- 8) REVANCHA solo con partido terminado ---
        c3 = await page.evaluate("""() => {
            const g = window.__game;
            g.rules.state = 'over';
            g.toggleMenu();
            const hasR = g.menuRects.some((r) => r.id === 'revancha');
            const idx = g.menuRects.findIndex((r) => r.id === 'revancha');
            g.menuClick(idx);
            return { hasR, state: g.rules.state, open: g.menuOpen };
        }""")
        if not c3["hasR"]: fails.append("REVANCHA no aparece con partido terminado")
        if c3["state"] == "over": fails.append("REVANCHA no reinicia")
        if c3["open"]: fails.append("REVANCHA no cierra el menú")

        # --- 9) cierre con toggleMenu y botón 'close' ---
        c4 = await page.evaluate("""() => {
            const g = window.__game;
            g.toggleMenu();
            const idx = g.menuRects.findIndex((r) => r.id === 'close');
            g.menuClick(idx);
            const t2 = g.menuOpen;
            const linesOff = !g.menuLines[0].visible && !g.menuLines[1].visible;
            return { t2, linesOff };
        }""")
        if c4["t2"]: fails.append("botón Cerrar no cierra")
        if not c4["linesOff"]: fails.append("láseres encendidos con menú cerrado")

        # --- 10) captura con la PALA apuntando a 'Difícil' ---
        await page.evaluate(f"""() => {{
            const g = window.__game;
            g.rules.state = 'serve';
            g.toggleMenu();
            g.menuGroup.position.set(0.55, 1.05, -0.75);
            g.menuGroup.lookAt(2.2, 1.5, 1.4);
            g.aimHand = g.paddleHand;
            ({JS_AIM})('diff:hard');
            g.updateMenu();
            // congelar el anclaje para la foto (sin XR la muñeca está en el origen)
            g.menuGroup.position.set(0.55, 1.05, -0.75);
            g.menuGroup.lookAt(2.2, 1.5, 1.4);
            g.menuGroup.updateMatrixWorld(true);
        }}""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=SHOT)

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    print("apertura:", json.dumps({k: m[k] for k in ("open", "n", "lines", "dots")}))
    if fails:
        print("FALLOS:", *fails, sep="\n  - ")
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
