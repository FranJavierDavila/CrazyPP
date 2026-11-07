#!/usr/bin/env python3
"""r60 · reproducción del flujo REAL del dueño: launch() de verdad, fuga del
flag champDecorHidden tras salir de una prueba a mitad (asedio de oeste), y
estado de los troqueles en el campeonato SIGUIENTE (magia)."""
import asyncio
import json
import sys

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

async def main():
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on("pageerror", lambda e: errors.append("PAGEERROR: " + str(e)))
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(1200)

        print("=== 1 · launch() REAL de magia (camino del menú) ===")
        r1 = await page.evaluate("""async () => {
          const g = window.__game;
          await g.champs.launch('magia');
          for (let i = 0; i < 30; i++) {
            g.champDecor.update(0.05, performance.now() / 1000);
            await new Promise(r => setTimeout(r, 30));
          }
          const d = g.champDecor;
          return { activeId: g.champs.activeId, builtFor: d.builtFor,
                   visible: d.group.visible, piezas: d.pieces.length,
                   listas: d.pieces.filter(p => p.ready).length,
                   hidden: g.champDecorHidden, inAR: g.inAR,
                   rulesState: g.rules.state, mode: g.mode };
        }""")
        print(json.dumps(r1, indent=1))

        print("=== 2 · FUGA del flag: prueba especial activa + salida sucia ===")
        r2 = await page.evaluate("""async () => {
          const g = window.__game;
          // el dueño juega el asedio de oeste (champDecorHidden=true) y sale
          // por el menú a mitad de prueba — simulamos el estado tras el start
          // de la prueba y una leaveAll «sucia» que no pasa por su dispose:
          await g.champs.launch('oeste');
          g.champDecorHidden = true;          // estado que deja el asedio al activarse
          g.champs.leaveAll();                // salida sucia (B/menú → otro modo)
          const fugado = { flagTrasSalidaSucia: g.champDecorHidden };
          // ahora el dueño entra al campeonato de Wizard:
          await g.champs.launch('magia');
          for (let i = 0; i < 30; i++) {
            g.champDecor.update(0.05, performance.now() / 1000);
            await new Promise(r => setTimeout(r, 30));
          }
          const d = g.champDecor;
          return { ...fugado, activeId: g.champs.activeId, builtFor: d.builtFor,
                   visible: d.group.visible, piezas: d.pieces.length,
                   hiddenAhora: g.champDecorHidden };
        }""")
        print(json.dumps(r2, indent=1))

        print("=== 3 · ¿leave() de oeste restaura en salida LIMPIA? ===")
        r3 = await page.evaluate("""async () => {
          const g = window.__game;
          await g.champs.launch('oeste');
          g.champDecorHidden = true;
          g.champs.leaveAll();                 // leaveAll SÍ llama a m.leave()
          const m = g.champs.moduleIfLoaded('oeste');
          return { flagTrasLeaveAll: g.champDecorHidden,
                   stageModeVivo: !!(m && m._stageMode) };
        }""")
        print(json.dumps(r3, indent=1))

        await browser.close()

    print("\nERRORES:", len(errors))
    for e in errors[:5]:
        print("  ·", e[:180])
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
