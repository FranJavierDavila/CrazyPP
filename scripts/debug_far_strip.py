#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug_far_strip.py · ¿qué ocluye la franja lejana de la mesa en t1b?"""
import asyncio
from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'
JS = r"""
async () => {
  const G = window.__PP_GAME;
  const T = window.__PP_TRAIN;
  T.startMode(G, 't1b');
  await new Promise(r => setTimeout(r, 120));
  const grp = G.rig.getObjectByName('ppTrainGrp');
  const quad = grp.children.find(m => m.isMesh && m.geometry && m.geometry.type === 'PlaneGeometry');
  const HL = quad.geometry.parameters.height, HW = quad.geometry.parameters.width / 2;
  const C = quad.position.z + HL / 2, yT = quad.position.y;
  const V3 = quad.position.constructor;
  const CamC = G.camera.constructor;
  const cam = new CamC(50, 1, 0.1, 30);
  cam.aspect = 1; cam.fov = 2 * Math.atan((HL / 2 + 0.15) / 2.2) * 180 / Math.PI;
  cam.position.set(0, 2.2, C - HL / 2); cam.up = new V3(0, 0, -1);
  cam.lookAt(0, 0, C - HL / 2); cam.updateProjectionMatrix();
  G.renderer.render(G.scene, cam);
  const gl = G.renderer.getContext();
  const cw = gl.drawingBufferWidth, ch = gl.drawingBufferHeight;
  const buf = new Uint8Array(4);
  const out = { pix: [], ray: [] };
  for (const dz of [1.15, 1.22, 1.26, 1.31, 1.36]) {
    const p = new V3(0, yT + 0.01, C - dz).project(cam);
    const sx = Math.round((p.x + 1) / 2 * cw), sy = Math.round((1 - (p.y + 1) / 2) * ch);
    gl.readPixels(sx, ch - 1 - sy, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    out.pix.push({ dz, rgb: [buf[0], buf[1], buf[2], buf[3]], sx, sy, ch });
  }
  // objetos cerca de la franja lejana (nombres + visibilidad + posición)
  out.objs = [];
  G.scene.traverse((o) => {
    if (!o.visible) return;
    const wp = o.getWorldPosition ? o.getWorldPosition(new V3()) : null;
    if (wp && Math.abs(wp.x) < 0.6 && wp.z < C - HL * 0.72 && wp.z > C - HL - 0.6 && wp.y > yT - 0.01) {
      out.objs.push({ n: o.name || o.type, y: +wp.y.toFixed(3), z: +wp.z.toFixed(3), x: +wp.x.toFixed(3) });
    }
  });
  G.renderer.render(G.scene, G.camera);
  return out;
};
"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        page = await b.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded')
        await page.wait_for_function("() => window.__PP_GAME && window.__PP_TRAIN", timeout=45000)
        r = await page.evaluate(JS)
        for e in r['pix']:
            print(f"  dz={e['dz']}: rgb={e['rgb']}  (sx={e['sx']}, sy={e['sy']}/{e['ch']})")
        print('  objetos cerca de la franja lejana:')
        for o in r['objs'][:12]:
            print('   ', o)
        await b.close()

asyncio.run(main())
