#!/usr/bin/env python3
"""Verificación headless v2.14: GLB (regresión) + temas de sala en runtime."""
import asyncio, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
SHOTS = "/home/z/my-project/scripts"

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

        # --- 2) tema por defecto + aplicación de temas ---
        info = await page.evaluate("""() => {
            const g = window.__game;
            const hex = (m) => '#' + m.color.getHexString();
            const snap = () => ({
                wall: hex(g.roomGroup.userData.wallMat),
                floor: hex(g.roomGroup.userData.floorMat),
                panel: hex(g.roomGroup.userData.panelMat),
                strip: hex(g.roomGroup.userData.stripMat),
                bg: '#' + g.scene.background.getHexString(),
                fogNear: g.scene.fog.near,
                hemiInt: g.hemi.intensity,
                dirInt: g.dirLight.intensity,
                envInt: g.scene.environmentIntensity,
                gridN: !!g.roomGroup.userData.grid,
                gridInGroup: !g.roomGroup.userData.grid.parent ||
                             g.roomGroup.userData.grid.parent === g.roomGroup,
            });
            const def = snap();
            const t0 = g.theme;
            g.setTheme('neon', true);      const neon = snap();
            g.setTheme('atardecer', true); const ata = snap();
            g.setTheme('artico', true);    const art = snap();
            const saved = localStorage.getItem('ppxr_theme');
            return { def, t0, neon, ata, art, saved };
        }""")
        if info["t0"] != "pabellon": fails.append(f"tema inicial: {info['t0']}")
        if info["saved"] != "artico": fails.append(f"localStorage tema: {info['saved']}")
        d, n = info["def"], info["neon"]
        if not (d["wall"] != n["wall"] and d["bg"] != n["bg"] and d["strip"] != n["strip"]):
            fails.append(f"neón no cambia materiales: {json.dumps({k: [d[k], n[k]] for k in ('wall','bg','strip')})}")
        if n["hemiInt"] == d["hemiInt"] or n["dirInt"] == d["dirInt"]:
            fails.append("neón no cambia luces")
        if info["ata"]["floor"] == d["floor"] or info["art"]["panel"] == d["panel"]:
            fails.append("atardecer/ártico no cambian materiales")
        if not (info["neon"]["gridInGroup"] and info["art"]["gridInGroup"] and info["neon"]["gridN"]):
            fails.append("rejilla reconstruida incorrecta")

        # --- 3) ciclo completo con cycleTheme (como el flick del stick) ---
        cyc = await page.evaluate("""() => {
            const g = window.__game;
            g.setTheme('artico', true);
            g.cycleTheme(1);   // artico -> pabellon (wrap)
            const a = g.theme;
            g.cycleTheme(-1);  // pabellon -> artico
            const b = g.theme;
            return { wrap: a, back: b, msg: g.rules.message };
        }""")
        if cyc["wrap"] != "pabellon" or cyc["back"] != "artico":
            fails.append(f"cycleTheme: {json.dumps(cyc)}")
        if "SALA" not in (cyc["msg"] or ""):
            fails.append(f"mensaje del marcador: {cyc['msg']}")

        # --- 4) persistencia: recarga y comprueba que arranca en artico ---
        await page.reload()
        await page.wait_for_timeout(3800)
        re = await page.evaluate("""() => {
            const g = window.__game;
            return {
                theme: g.theme,
                wall: '#' + g.roomGroup.userData.wallMat.color.getHexString(),
                bg: '#' + g.scene.background.getHexString(),
            };
        }""")
        if re["theme"] != "artico": fails.append(f"tema tras recarga: {re['theme']}")
        if re["bg"] != "#0d1418": fails.append(f"fondo tras recarga: {re['bg']}")

        # --- 5) chips del overlay sincronizados + clic en chip ---
        ui = await page.evaluate("""() => {
            const chips = [...document.querySelectorAll('[data-theme]')];
            const activeBefore = chips.filter((c) => c.classList.contains('active')).length;
            const keyBefore = chips.find((c) => c.classList.contains('active'))?.dataset.theme;
            document.querySelector('[data-theme="neon"]').click();
            const g = window.__game;
            const activeAfter = chips.filter((c) => c.classList.contains('active')).length;
            return { n: chips.length, activeBefore, keyBefore,
                     theme: g.theme, activeAfter,
                     activeKey: chips.find((c) => c.classList.contains('active'))?.dataset.theme };
        }""")
        if ui["n"] != 4 or ui["activeBefore"] != 1 or ui["keyBefore"] != "artico":
            fails.append(f"chips iniciales: {json.dumps(ui)}")
        if ui["theme"] != "neon" or ui["activeAfter"] != 1 or ui["activeKey"] != "neon":
            fails.append(f"clic en chip neón: {json.dumps(ui)}")

        # --- 6) capturas de los 4 temas ---
        for key in ("pabellon", "neon", "atardecer", "artico"):
            await page.evaluate(f"window.__game.setTheme('{key}', true)")
            await page.wait_for_timeout(350)
            await page.screenshot(path=f"{SHOTS}/preview_v214_{key}.png")

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    print("recarga:", json.dumps(re))
    print("ui:", json.dumps(ui))
    if fails:
        print("FALLOS:", *fails, sep="\n  - ")
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
