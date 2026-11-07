#!/usr/bin/env python3
"""Diagnóstico VISUAL del ASTRO en la sala del orbital (etapa 1).
Capturas desde el punto de vista del jugador VR y datos de posición.
Uso: python3 scripts/qa_rival_diag.py"""
import asyncio
import json

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
        info = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          if (!G) return { error: 'sin __PP_GAME' };
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod && mod.controller;
          // SALA de la etapa 1 (duelo 1): el ASTRO de pie
          ctrl.stage = 0;
          ctrl.state = 'sala';
          if (ctrl.rivalMesh) ctrl.rivalMesh.visible = true;
          const D = G.DIMS || (window.__ppDebug && window.__ppDebug.DIMS);
          const out = {};
          out.rival = ctrl.rivalMesh ? ctrl.rivalMesh.position.toArray().map(v => +v.toFixed(3)) : null;
          out.rivalScale = ctrl.rivalMesh ? [ctrl.rivalMesh.scale.x, ctrl.rivalMesh.scale.y] : null;
          out.room = D ? { halfX: D.roomHalfX, backZ: D.roomBackZ, frontZ: D.roomFrontZ, h: D.roomHeight } : null;
          out.table = { cz: D.tableCenterZ, hl: D.tableHalfLength, hw: D.tableHalfWidth };
          out.camPos = G.camera.position.toArray().map(v => +v.toFixed(2));
          out.presenting = !!G.renderer.xr.isPresenting;
          return out;
        }""")
        print('INFO:', json.dumps(info, ensure_ascii=False, indent=1))

        # Captura 1: vista del jugador VR (x0 · y1.62 · z0.9) mirando al ASTRO
        shot = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const c = G.camera;
          c.parent && c.parent.remove(c);
          G.scene.add(c);
          c.position.set(0, 1.62, 0.9);
          c.lookAt(1.62, 1.05, -4.5);
          c.fov = 75; c.aspect = 1280 / 800; c.updateProjectionMatrix();
          G.renderer.render(G.scene, c);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        import base64
        with open(OUT + '/rival_diag_vr.png', 'wb') as f:
            f.write(base64.b64decode(shot.split(',', 1)[1]))

        # Captura 2: vista general orbital (jugador → mesa → pared frontal)
        shot2 = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const c = G.camera;
          c.position.set(0, 1.62, 1.1);
          c.lookAt(0, 1.0, -5.55);
          G.renderer.render(G.scene, c);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open(OUT + '/rival_diag_sala.png', 'wb') as f:
            f.write(base64.b64decode(shot2.split(',', 1)[1]))

        # Captura 3: CENITAL (planta) — relación rival ↔ paredes
        shot3 = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const c = G.camera;
          c.position.set(1.62, 7.5, -4.5 + 0.01);
          c.up.set(0, 0, -1);
          c.lookAt(1.62, 0, -4.5);
          G.renderer.render(G.scene, c);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open(OUT + '/rival_diag_top.png', 'wb') as f:
            f.write(base64.b64decode(shot3.split(',', 1)[1]))

        # Captura 4: lateral derecha — ¿el rival queda DENTRO de la pared derecha?
        shot4 = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const c = G.camera;
          c.up.set(0, 1, 0);
          c.position.set(2.9, 1.4, 0.5);
          c.lookAt(1.62, 1.05, -4.5);
          G.renderer.render(G.scene, c);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open(OUT + '/rival_diag_side.png', 'wb') as f:
            f.write(base64.b64decode(shot4.split(',', 1)[1]))

        print('pageerrors:', errors[:3])
        await browser.close()

asyncio.run(main())
