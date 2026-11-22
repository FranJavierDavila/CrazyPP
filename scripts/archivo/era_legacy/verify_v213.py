#!/usr/bin/env python3
"""Verificación headless v2.13: GLB + stats/logros + dificultad en runtime."""
import asyncio, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
SHOT = "/home/z/my-project/scripts/preview_v213_stats.png"

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

        # --- 1) GLB carga ---
        glb = await page.evaluate("""() => {
            let kind = '?', n = 0;
            window.__game.aiPaddleMesh.traverse((o) => {
                if (o.isMesh) { n++; kind = o.geometry?.type || '?'; }
            });
            return kind === 'BufferGeometry' && n >= 5;
        }""")
        if not glb: fails.append("GLB no cargado")

        # --- 2) logros en runtime: primera victoria, racha3, gigante ---
        ach = await page.evaluate("""() => {
            const g = window.__game;
            const u1 = g.stats.recordMatch(true, 'medium');    // -> primera
            g.stats.recordMatch(true, 'medium');
            const u3 = g.stats.recordMatch(true, 'hard');      // -> racha3 + gigante
            g.stats.recordPoint('player', 1);                  // ace -> aces=1
            g.stats.recordSurvivalRally(26, 26);               // -> maraton + superviv
            return { u1, u3, data: g.stats.data };
        }""")
        d = ach["data"]
        if "primera" not in ach["u1"]: fails.append(f"primera no desbloqueado: {ach['u1']}")
        if "racha3" not in ach["u3"] or "gigante" not in ach["u3"]:
            fails.append(f"racha3/gigante no desbloqueados: {ach['u3']}")
        if d["won"] != 3 or d["streak"] != 3 or d["aces"] != 1 or d["bestRally"] < 26:
            fails.append(f"stats mal: {json.dumps(d)}")
        if not d["ach"].get("maraton") or not d["ach"].get("superviv"):
            fails.append("maraton/superviv no desbloqueados")

        # persistencia en localStorage
        saved = await page.evaluate("() => JSON.parse(localStorage.getItem('ppxr_stats_v1') || '{}')")
        if saved.get("won") != 3: fails.append("localStorage no persiste")

        # --- 3) renderStats en DOM (repintar tras mutaciones, como hace emitStats) ---
        dom = await page.evaluate("""() => {
            window.__game.emitStats();
            const chips = [...document.querySelectorAll('#achRow .ach')];
            return {
                line: document.getElementById('statsLine')?.textContent || '',
                total: chips.length,
                on: chips.filter((c) => c.classList.contains('on')).length,
            };
        }""")
        if dom["total"] != 6: fails.append(f"chips de logro: {dom['total']} != 6")
        if dom["on"] != 5: fails.append(f"chips activados: {dom['on']} != 5 (primera,racha3,gigante,maraton,superviv)")

        # --- 4) dificultad (comparando presets escalados, no k en empate) ---
        diff = await page.evaluate("""() => {
            const g = window.__game;
            g.setDifficulty('easy');
            const easyCfg = JSON.stringify(g.ai.cfg);
            g.setDifficulty('hard');
            const hardCfg = JSON.stringify(g.ai.cfg);
            return { changed: easyCfg !== hardCfg, restored: 'hard' };
        }""")
        if not diff["changed"]: fails.append("preset de dificultad no cambia la IA")

        # --- 5) reset ---
        await page.click("#statsReset")
        reset = await page.evaluate("""() => {
            const s = JSON.parse(localStorage.getItem('ppxr_stats_v1') || '{}');
            return { won: s.won || 0, achCount: Object.keys(s.ach || {}).length,
                     surv: window.__game.survivalBest };
        }""")
        if reset["won"] != 0 or reset["achCount"] != 0 or reset["surv"] != 0:
            fails.append(f"reset: {json.dumps(reset)}")

        await page.screenshot(path=SHOT)
        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    print("chips:", json.dumps(dom))
    if fails:
        print("FALLOS:", *fails, sep="\n  - ")
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
