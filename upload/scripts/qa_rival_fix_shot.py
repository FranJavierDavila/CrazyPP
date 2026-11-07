#!/usr/bin/env python3
"""Verificación VISUAL del ASTRO recolocado (v3.4.1-RIV1).
Capturas del jugador + datos. Uso: python3 scripts/qa_rival_fix_shot.py"""
import asyncio
import base64
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
          ctrl.stage = 0;
          ctrl.state = 'sala';
          if (ctrl.rivalMesh) ctrl.rivalMesh.visible = true;
          const p = ctrl.rivalMesh.position;
          return {
            rival: p.toArray().map(v => +v.toFixed(3)),
            visible: ctrl.rivalMesh.visible,
            escalaY: ctrl.rivalMesh.scale.y,
          };
        }""")
        print('INFO:', json.dumps(info, ensure_ascii=False))

        # Vista del jugador VR con el ASTRO en el nuevo spot
        shot = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const c = G.camera;
          c.parent && c.parent.remove(c);
          G.scene.add(c);
          c.position.set(0, 1.62, 0.9);
          c.lookAt(1.26, 1.05, -3.82);
          c.fov = 75; c.aspect = 1280 / 800; c.updateProjectionMatrix();
          G.renderer.render(G.scene, c);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open(OUT + '/rival_fix_vr.png', 'wb') as f:
            f.write(base64.b64decode(shot.split(',', 1)[1]))

        # Vista general de la sala (composición completa)
        shot2 = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const c = G.camera;
          c.position.set(0, 1.62, 1.1);
          c.lookAt(0, 1.0, -5.55);
          G.renderer.render(G.scene, c);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open(OUT + '/rival_fix_sala.png', 'wb') as f:
            f.write(base64.b64decode(shot2.split(',', 1)[1]))

        # Vista lateral derecha: hueco real con la pared
        shot3 = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const c = G.camera;
          c.position.set(2.6, 1.4, 0.2);
          c.lookAt(1.26, 1.05, -3.82);
          G.renderer.render(G.scene, c);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open(OUT + '/rival_fix_side.png', 'wb') as f:
            f.write(base64.b64decode(shot3.split(',', 1)[1]))

        print('pageerrors:', errors[:3])
        await browser.close()

asyncio.run(main())
