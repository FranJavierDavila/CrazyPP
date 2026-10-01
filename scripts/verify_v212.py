#!/usr/bin/env python3
"""Verificación headless del index.html v2.12:
1. El GLB de la pala se carga (log 'Pala: ...' de éxito, sin error de parseo).
2. El modo de juego cambia en runtime (switchMode: match ⇄ survival).
3. Captura de pantalla para inspección visual."""
import asyncio, base64, json, re, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
SHOT = "/home/z/my-project/scripts/preview_v212_pala_glb.png"

async def main():
    errors, infos = [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--disable-web-security",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("console", lambda m: (infos if m.type in ("info", "log") else errors).append(
            f"[{m.type}] {m.text}") if m.type != "warning" else None)
        page.on("pageerror", lambda e: errors.append(f"[pageerror] {e}"))

        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4500)   # GLB (~1.4 MB base64) + parse

        # --- 1) ¿GLB cargado? ---
        ok_marker = any("Pala:" in t and "corregida" in t for t in infos)
        fail_marker = any("No se pudo cargar el GLB" in t for t in errors)
        glb_len = await page.evaluate("""() => {
            const g = window.__game;
            return g ? 'game-ok' : 'no-game';
        }""")

        # ¿el fallback procedural está activo? (pala del jugador = GLB si cargó)
        vis = await page.evaluate("""() => {
            const g = window.__game;
            if (!g) return null;
            // la pala IA es makePaddleVisual(model,'center'): si el GLB cargó,
            // sus hijos son clones del modelo (5 mallas, escala 0.026); el
            // fallback es un CilindroGeometry de radio 0.0795.
            const mesh = g.aiPaddleMesh;
            let kind = 'desconocido', nMeshes = 0, names = [];
            mesh.traverse((o) => {
                if (o.isMesh) {
                    nMeshes++;
                    names.push(o.geometry?.type || '?');
                    if (o.geometry?.type === 'CylinderGeometry') kind = 'FALLBACK';
                    else if (o.geometry?.type === 'BufferGeometry') kind = 'GLB';
                }
            });
            return {
                mode: g.mode,
                rulesMode: g.rules.mode,
                paddleVisual: kind + ' (' + nMeshes + ' mallas: ' + names.join(',') + ')',
                hasControllerPaddles: !!g.controllerPaddles,
            };
        }""")

        # --- 2) switchMode en runtime ---
        sw = await page.evaluate("""() => {
            const g = window.__game;
            if (!g || !g.switchMode) return 'sin switchMode';
            g.switchMode('survival');
            const a = { mode: g.mode, rules: g.rules.mode };
            g.switchMode('match');
            const b = { mode: g.mode, rules: g.rules.mode };
            return JSON.stringify({ survival: a, match: b });
        }""")

        await page.wait_for_timeout(1200)
        await page.screenshot(path=SHOT)
        await browser.close()

    print("== LOGS ==")
    for t in infos[:12]:
        print(" ", t)
    print("== ERRORES ==")
    for t in errors[:12]:
        print(" ", t)
    print("== ESTADO ==")
    print("  juego:", glb_len, "·", json.dumps(vis))
    print("  switchMode:", sw)
    print("== RESULTADO ==")
    print("  GLB cargado:", "SÍ" if ok_marker else ("NO (error)" if fail_marker else "SIN MARCA (¿fallback?)"))
    glb_ok = vis and str(vis.get("paddleVisual", "")).startswith("GLB")
    if not fail_marker and glb_len == "game-ok" and vis and vis["mode"] == "match":
        print("  Modos: OK")
        print("  Pala:", vis["paddleVisual"])
        sys.exit(0 if glb_ok else 2)
    sys.exit(1)

asyncio.run(main())
