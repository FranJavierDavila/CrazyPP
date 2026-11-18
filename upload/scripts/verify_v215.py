#!/usr/bin/env python3
"""Verificación headless v2.15: GLB + menú de muñeca (apertura, clics, cierre)."""
import asyncio, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
SHOT = "/home/z/my-project/scripts/preview_v215_menu.png"

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
            g.toggleMenu();
            const ids = g.menuRects.map((r) => r.id);
            return {
                open: g.menuOpen, vis: g.menuGroup.visible,
                n: ids.length, ids,
                msg: g.rules.message,
            };
        }""")
        need = ['mode:match', 'mode:survival', 'diff:easy', 'diff:medium', 'diff:hard',
                'theme:pabellon', 'theme:neon', 'theme:atardecer', 'theme:artico',
                'amb:on', 'amb:off', 'close']
        if not m["open"] or not m["vis"]: fails.append("el menú no se abre")
        for r in need:
            if r not in m["ids"]: fails.append(f"falta botón {r}")
        if m["n"] != len(need): fails.append(f"botones: {m['n']} != {len(need)}")

        # --- 3) clics: dificultad, tema y sala se aplican y el menú sigue abierto ---
        c1 = await page.evaluate("""() => {
            const g = window.__game;
            const idx = (id) => g.menuRects.findIndex((r) => r.id === id);
            g.menuClick(idx('diff:hard'));
            const diff = g.difficulty;
            const msgD = g.rules.message;
            g.menuClick(idx('theme:neon'));
            const theme = g.theme;
            const saved = localStorage.getItem('ppxr_theme');
            const wall = '#' + g.roomGroup.userData.wallMat.color.getHexString();
            const stillOpen = g.menuOpen;
            g.menuClick(idx('amb:off'));
            const amb = g.audio.ambience;
            return { diff, msgD, theme, saved, wall, stillOpen, amb };
        }""")
        if c1["diff"] != "hard": fails.append(f"dificultad: {c1['diff']}")
        if "DIFICULTAD" not in c1["msgD"]: fails.append(f"mensaje dificultad: {c1['msgD']}")
        if c1["theme"] != "neon" or c1["saved"] != "neon" or c1["wall"] != "#0a0c16":
            fails.append(f"tema desde menú: {json.dumps(c1)}")
        if not c1["stillOpen"]: fails.append("el menú se cerró con diff/tema")
        if c1["amb"] is not False: fails.append(f"ambiente: {c1['amb']}")

        # --- 4) clic en MODO: aplica y CIERRA el menú ---
        c2 = await page.evaluate("""() => {
            const g = window.__game;
            const idx = g.menuRects.findIndex((r) => r.id === 'mode:survival');
            g.menuClick(idx);
            return { mode: g.mode, rules: g.rules.mode, open: g.menuOpen };
        }""")
        if c2["mode"] != "survival" or c2["rules"] != "survival":
            fails.append(f"modo desde menú: {json.dumps(c2)}")
        if c2["open"]: fails.append("el menú no se cerró al cambiar de modo")

        # --- 5) REVANCHA solo con partido terminado ---
        c3 = await page.evaluate("""() => {
            const g = window.__game;
            g.rules.state = 'over';
            g.toggleMenu();          // reabrir
            const hasR = g.menuRects.some((r) => r.id === 'revancha');
            const idx = g.menuRects.findIndex((r) => r.id === 'revancha');
            g.menuClick(idx);
            const state = g.rules.state;
            const open = g.menuOpen;
            return { hasR, state, open };
        }""")
        if not c3["hasR"]: fails.append("REVANCHA no aparece con partido terminado")
        if c3["state"] == "over": fails.append("REVANCHA no reinicia")
        if c3["open"]: fails.append("REVANCHA no cierra el menú")

        # --- 6) cierre con toggleMenu y botón 'close' ---
        c4 = await page.evaluate("""() => {
            const g = window.__game;
            const open1 = g.menuOpen;
            g.toggleMenu();                       // cierra (estaba abierto tras revancha? no: se cerró)
            const t1 = g.menuOpen;
            g.toggleMenu();                       // reabre
            const idx = g.menuRects.findIndex((r) => r.id === 'close');
            g.menuClick(idx);
            const t2 = g.menuOpen;
            return { open1, t1, t2 };
        }""")
        if c4["open1"]: fails.append("menú quedó abierto tras revancha")
        if c4["t2"]: fails.append("botón Cerrar no cierra")

        # --- 7) captura con el menú visible (posición manual, sin XR) ---
        await page.evaluate("""() => {
            const g = window.__game;
            g.rules.state = 'serve';
            g.toggleMenu();
            g.menuGroup.position.set(0.55, 1.05, -0.75);
            g.menuGroup.lookAt(2.2, 1.5, 1.4);   // hacia la cámara del escritorio
        }""")
        await page.wait_for_timeout(400)
        await page.screenshot(path=SHOT)

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    print("apertura:", json.dumps({k: m[k] for k in ("open", "n")}))
    if fails:
        print("FALLOS:", *fails, sep="\n  - ")
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
