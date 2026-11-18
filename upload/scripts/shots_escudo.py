#!/usr/bin/env python3
"""Capturas de la etapa ESCUDO DE PALA para revisión del dueño.
Uso: python3 scripts/shots_escudo.py"""
import asyncio
import base64

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'
OUT = '/home/z/my-project/download'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.goto(BASE + '/game.html', wait_until='networkidle')
        await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const ctrl = G.champs.moduleIfLoaded('estacion_orbital').controller;
          ctrl.stage = 3;
          ctrl._arrancarEscudo(ctrl._etapa());
          const E = ctrl.escudo;
          for (let i = 0; i < 40; i++) E.step(0.1);   // prep → fase 1
          try { G.hideChampIntro(false); } catch (e) { /* */ }
          // esperar a que las 6 texturas de la sala estén cargadas
          for (let k = 0; k < 100; k++) {
            const ok = E.grp.children.every(m => !m.material || !m.material.map ||
              (m.material.map.image && m.material.map.image.width));
            if (ok) break;
            await new Promise(r => setTimeout(r, 100));
          }
          await new Promise(r => setTimeout(r, 600));
          // un orbe enemigo en vuelo para la foto
          const d0 = E.drones.find(d => d.alive);
          d0.shootT = 0; E.step(0.05);
          d0.chargeT = 0.01; E.step(0.05); E.step(0.3);
          window.__ESC = E;
        }""")
        for name, cam, look in (
            ('escudo_fase1', (0, 1.62, 0.4), (0, 1.6, -9)),
            ('escudo_barrera', (0, 1.5, -1.2), (0, 1.5, 2)),
            ('escudo_pantalla', (0, 1.62, 1.0), (0, 3.6, -6.4)),
        ):
            # render + captura ATÓMICOS (el bucle rAF no puede colarse en medio)
            shot = await page.evaluate("""([cx, cy, cz, lx, ly, lz]) => {
              const G = window.__PP_GAME;
              const c = G.camera;
              c.parent && c.parent.remove(c);
              G.scene.add(c);
              c.position.set(cx, cy, cz);
              c.lookAt(lx, ly, lz);
              c.fov = 75; c.aspect = 1280 / 800; c.updateProjectionMatrix();
              G.renderer.render(G.scene, c);
              return G.renderer.domElement.toDataURL('image/png');
            }""", [*cam, *look])
            with open(f'{OUT}/v350_{name}.png', 'wb') as f:
                f.write(base64.b64decode(shot.split(',', 1)[1]))
            print('captura', name)
        print('pageerrors:', errors[:3])
        await browser.close()

asyncio.run(main())
