#!/usr/bin/env python3
"""Diagnóstico visual v2 del informe del dueño (etapa 1 rival en pared +
etapa 2 reactor). Captura el canvas WebGL directamente."""
import asyncio
import base64
import os

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'
OUT = '/home/z/my-project/download/diag_imp2'
os.makedirs(OUT, exist_ok=True)

SNAP_JS = """(pose) => {
  const G = window.__PP_GAME;
  const c = G.camera;
  if (c.parent) c.parent.remove(c);
  G.scene.add(c);
  c.position.set(pose[0], pose[1], pose[2]);
  c.lookAt(pose[3], pose[4], pose[5]);
  c.fov = 75; c.aspect = 1280 / 800; c.updateProjectionMatrix();
  G.renderer.render(G.scene, c);
  return G.renderer.domElement.toDataURL('image/png');
}"""

async def snap(page, name, pose):
    data = await page.evaluate(SNAP_JS, pose)
    with open(f'{OUT}/{name}.png', 'wb') as f:
        f.write(base64.b64decode(data.split(',', 1)[1]))
    print('  captura:', name)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        await page.goto(BASE + '/game.html', wait_until='networkidle')
        await page.wait_for_timeout(1200)

        info = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5000));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          try { G.hideChampIntro(false); } catch (e) { /* */ }
          return {
            rival: ctrl.rivalMesh ? ctrl.rivalMesh.position.toArray() : null,
            cartel: ctrl.cartel ? ctrl.cartel.position.toArray() : null,
            room: [window.__ppDebug.DIMS.roomHalfX, window.__ppDebug.DIMS.roomFrontZ],
          };
        }""")
        print('etapa 1 · rival =', info['rival'], '· room =', info['room'])

        # POV del jugador mirando al frente (como en el visor)
        await snap(page, 'e1_pov', (0, 1.62, 0.55, 0.3, 1.1, -4.0))
        # el rival de frente
        await snap(page, 'e1_rival', (0.1, 1.6, -1.1, 1.26, 1.0, -3.30))
        # lado derecho (como si mirara a la pared derecha)
        await snap(page, 'e1_derecha', (0.2, 1.6, -0.9, 3.05, 1.2, -3.8))

        # --- ETAPA 2: reactor de impulso
        imp = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          ctrl.stage = 1;
          ctrl._arrancarImpulso(ctrl._etapa());
          await new Promise(r => setTimeout(r, 600));
          const I = ctrl.impulso;
          for (let i = 0; i < 60; i++) I.step(0.1);
          return {
            active: I.active, phase: I.phase, wave: I.wave,
            cubes: I.cubes.filter(c => c.alive).length,
            mounts: (G.gunMounts || []).map(m => !!m && m.visible),
          };
        }""")
        print('etapa 2 · impulso =', imp)

        await snap(page, 'e2_pov', (0, 1.62, 0.5, 0, 1.5, -2.9))
        await snap(page, 'e2_ventana_der', (0.4, 1.55, -1.6, 3.05, 1.5, -1.6))
        await snap(page, 'e2_pantalla', (0, 1.72, -1.65, 0, 2.42, -3.6))
        await snap(page, 'e2_nucleo', (1.35, 1.95, -1.05, 0, 1.55, -2.75))
        await snap(page, 'e2_diana', (1.9, 1.75, -1.5, 1.2, 1.6, -2.4))

        # cubo de cerca
        cube = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const I = G.champs.moduleIfLoaded('estacion_orbital').controller.impulso;
          const c = I.cubes.find(k => k.alive);
          if (!c) return null;
          return c.pos.toArray();
        }""")
        if cube:
            await snap(page, 'e2_cubo',
                       (cube[0] + 0.85, cube[1] + 0.35, cube[2] + 1.0,
                        cube[0], cube[1], cube[2]))

        print('pageerrors:', len(errs))
        for e in errs[:6]:
            print('  ERR', e[:200])
        await browser.close()

asyncio.run(main())
