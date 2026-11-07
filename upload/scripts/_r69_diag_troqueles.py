#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r69 · diagnóstico de TROQUELES sobre el juego real (V3.6.60).

El dueño: «los 4 troqueles de adorno que existen en los diferentes escenarios
de los campeonatos han desaparecido». En r60 se diagnosticó el cerrojo
champDecorHidden (autocurado en leaveAll) — pero el dueño lo sigue viendo
roto. Este diag recorre el flujo COMPLETO en los 5 campeonatos: launch real,
estado del decor (builtFor/piezas/listas/visible/hidden/inAR), salida por
leaveAll y relevo al siguiente campeonato. Además: ¿dónde cuelga el grupo
(padre, posición) y ¿qué URL de textura intenta cada pieza?"""
import asyncio
import json
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"

CAMPS = ['oeste', 'magia', 'locura', 'estacion_orbital', 'valle_neon']

ESTADO = """() => {
  const g = window.__game;
  const d = g.champDecor;
  return { activeId: (g.champs && g.champs.activeId) || '',
           builtFor: d ? d.builtFor : null,
           visible: d ? d.group.visible : null,
           piezas: d ? d.pieces.length : -1,
           listas: d ? d.pieces.filter(p => p.ready).length : -1,
           hidden: !!g.champDecorHidden, inAR: !!g.inAR,
           padreEsRig: !!(d && d.group.parent === g.rig),
           posGrupo: d ? [d.group.position.x, d.group.position.y,
                          d.group.position.z] : null,
           visibleRig: !!(g.rig && g.rig.visible) };
}"""

async def main():
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errors.append('PAGEERROR: ' + str(e)))
        page.on('requestfailed', lambda r: errors.append(
            'REQFAIL: ' + r.url[-90:] + ' · ' + str(r.failure)[:60]))
        await page.goto(URL, wait_until='load')
        await page.wait_for_function('() => window.__game && window.__game.champDecor',
                                     timeout=45000)
        await page.wait_for_timeout(1500)

        for cid in CAMPS:
            print(f'===== {cid} =====')
            r = await page.evaluate("""async (cid) => {
              const g = window.__game;
              await g.champs.launch(cid);
              // 45 ticks reales de update del decor (1.4 s) para texturas
              for (let i = 0; i < 45; i++) {
                g.champDecor.update(0.05, performance.now() / 1000);
                await new Promise(r2 => setTimeout(r2, 30));
              }
              const d = g.champDecor;
              const urls = d.pieces.map(p => p.cfg.file);
              const urlsCargadas = d.pieces.filter(p => p.ready).length;
              return { estado: null, urls, urlsCargadas,
                       mod: (() => { const m = g.champs.moduleIfLoaded(cid);
                                     return m ? (!!m.decor) : null; })(),
                       reglas: g.rules.state, modo: g.mode };
            }""", cid)
            e = await page.evaluate(ESTADO)
            print(json.dumps({**r, **e}, indent=1, ensure_ascii=False))
            # salida limpia por leaveAll (lo que hace el menú al cambiar de modo)
            await page.evaluate('() => window.__game.champs.leaveAll()')
            await page.wait_for_timeout(120)

        print('===== relevo sucio: asedio oeste → magia =====')
        r = await page.evaluate("""async () => {
          const g = window.__game;
          await g.champs.launch('oeste');
          g.champDecorHidden = true;          // estado que izan las pruebas
          g.champs.leaveAll();                // salida sucia
          const fuga = g.champDecorHidden;
          await g.champs.launch('magia');
          for (let i = 0; i < 45; i++) {
            g.champDecor.update(0.05, performance.now() / 1000);
            await new Promise(r2 => setTimeout(r2, 30));
          }
          const d = g.champDecor;
          return { flagTrasSalidaSucia: fuga, hiddenAhora: g.champDecorHidden,
                   visible: d.group.visible, piezas: d.pieces.length,
                   listas: d.pieces.filter(p => p.ready).length,
                   builtFor: d.builtFor };
        }""")
        print(json.dumps(r, indent=1, ensure_ascii=False))

        print('===== errores de red/página =====')
        for e in errors[:12]:
            print(' ', e[:150])
        if not errors:
            print('  (ninguno)')
        await browser.close()

exit(asyncio.run(main()))
