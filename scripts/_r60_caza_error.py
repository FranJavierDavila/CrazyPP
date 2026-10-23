#!/usr/bin/env python3
"""r60 · caza mínima del error «THREE.Object3D.add: object not an instance»
— secuencias separadas para localizar el paso que lo dispara."""
import asyncio
import sys

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

PASOS = [
    ("carga", "() => {}"),
    ("menuClick tut:go (start academia)",
     "() => { const g = window.__game; g.menuPage='main'; if (!g.menuOpen) g.toggleMenu(); g.drawMenu();"
     " const i=(g.menuRects||[]).findIndex(r=>r&&r.id==='tut:go'); if(i>=0) g.menuClick(i); }"),
    ("stop({}) salida B",
     "() => { try { window.__PP_TUT.stop({}); } catch(e) { return String(e); } }"),
    ("drawMenu tutask",
     "() => { const g = window.__game; g.menuPage='tutask'; if (!g.menuOpen) g.toggleMenu(); g.drawMenu(); }"),
    ("menuClick tut:go otra vez",
     "() => { const g = window.__game; const i=(g.menuRects||[]).findIndex(r=>r&&r.id==='tut:go'); if(i>=0) g.menuClick(i); }"),
    ("stop + launch oeste",
     "async () => { const g = window.__game; try { window.__PP_TUT.stop({}); } catch(e) {} await g.champs.launch('oeste'); }"),
    ("leaveAll + launch magia",
     "async () => { const g = window.__game; g.champs.leaveAll(); await g.champs.launch('magia'); }"),
    ("leaveAll + launch locura",
     "async () => { const g = window.__game; g.champs.leaveAll(); await g.champs.launch('locura'); }"),
    ("leaveAll + launch valle_neon",
     "async () => { const g = window.__game; g.champs.leaveAll(); await g.champs.launch('valle_neon'); }"),
    ("leaveAll + launch estacion_orbital",
     "async () => { const g = window.__game; g.champs.leaveAll(); await g.champs.launch('estacion_orbital'); }"),
    ("leaveAll final",
     "() => { window.__game.champs.leaveAll(); }"),
]

async def main():
    errs = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on("pageerror", lambda e: errs.append((paso, str(e))))
        page.on("console", lambda m: errs.append((paso, m.text))
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(1000)
        paso = "carga"
        for nombre, fn in PASOS[1:]:
            paso = nombre
            r = await page.evaluate(f"(async () => {{ {fn} }})()" if "async" in fn
                                    else f"(() => {{ {fn} }})()")
            if r: print(f"[{nombre}] retorno: {r}")
            await page.wait_for_timeout(400)
        await browser.close()

    print("\nerrores por paso:")
    for p, e in errs:
        print(f"  [{p}] {e[:180]}")
    if not errs:
        print("  (ninguno)")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
