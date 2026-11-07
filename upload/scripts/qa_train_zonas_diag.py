#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_train_zonas_diag.py · Diagnóstico empírico del entrenamiento por zonas (t1a).

Prueba AIRTIGHT vía GPU: render top-down real del overlay + gl.readPixels
→ ¿en qué profundidad de la mesa se MUESTRA el amarillo pintado?
Eso, comparado con la zona que el juez acepta, cierra el bug sin ambigüedad.
Además: staleness de la rotación (okHit → ¿se repinta el quad?).
Uso: python3 scripts/qa_train_zonas_diag.py
"""
import asyncio
import sys

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'

GPU_JS = r"""
() => {
  const G = window.__PP_GAME;
  const T = window.__PP_TRAIN;
  if (!G || !T) return { err: 'sin juego/entrenamiento' };
  T.startMode(G, 't1a');
  const st = T.__debug.st;
  const grp = G.rig.getObjectByName('ppTrainGrp');
  if (!grp) return { err: 'sin ppTrainGrp' };
  const quad = grp.children.find(m => m.isMesh && m.geometry && m.geometry.type === 'PlaneGeometry');
  if (!quad) return { err: 'sin quadMesh' };

  const HL = quad.geometry.parameters.height;
  const HW = quad.geometry.parameters.width / 2;
  const C  = quad.position.z + HL / 2;
  const yT = quad.position.y;

  // ── cámara top-down ortográfica propia (NO toca la del juego) ──
  const V3 = quad.position.constructor;
  const CamC = G.camera.constructor;
  const halfW = HW + 0.15, halfH = HL / 2 + 0.15;
  const cam = new CamC(50, 1, 0.1, 30);
  cam.aspect = halfW / halfH;
  if (cam.isPerspectiveCamera) { cam.fov = 2 * Math.atan(halfH / 2.2) * 180 / Math.PI; cam.position.set(0, 2.2, C - HL / 2); }
  else { cam.left = -halfW; cam.right = halfW; cam.top = halfH; cam.bottom = -halfH; cam.position.set(0, 2.2, C - HL / 2); }
  cam.up = new V3(0, 0, -1);                    // mira hacia -Z: el fondo arriba
  cam.lookAt(0, 0, C - HL / 2);
  cam.updateProjectionMatrix();
  const oldCam = G.camera;
  G.renderer.render(G.scene, cam);              // UN render propio, mismo frame

  const gl = G.renderer.getContext();
  const cw = gl.drawingBufferWidth, ch = gl.drawingBufferHeight;
  const isYellow = (d) => d[3] > 100 && d[0] > 190 && d[1] > 145 && d[1] < 230 && d[2] < 140;

  // columna del lado objetivo: mundo x fijo → pantalla
  const proj = (x, y, z) => {
    const p = new V3(x, y, z).project(cam);
    return { sx: Math.round((p.x + 1) / 2 * cw), sy: Math.round((1 - (p.y + 1) / 2) * ch) };
  };
  const xCol = st.target.x < 0 ? -(0.15 + HW) / 2 : (0.15 + HW) / 2;
  // barrido de profundidad: dz 0..HL en 64 pasos → ¿píxel amarillo en pantalla?
  const hits = [];
  const buf = new Uint8Array(4);
  for (let i = 0; i <= 64; i++) {
    const dz = HL * i / 64;
    const { sx, sy } = proj(xCol, yT + 0.01, C - dz);
    if (sx < 0 || sx >= cw || sy < 0 || sy >= ch) continue;
    gl.readPixels(sx, ch - 1 - sy, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    if (isYellow(buf)) hits.push(+dz.toFixed(3));
  }
  const zGood = st.target.z === 'deep' ? [HL / 2, HL] : [HL / 4, HL / 2];
  const shown = hits.length ? [hits[0], hits[hits.length - 1]] : null;

  // restaurar la cámara del juego
  G.renderer.render(G.scene, oldCam);
  return {
    target: Object.assign({}, st.target), HL, HW, C,
    amarilloSeMuestraEn_dz: shown,          // rango de profundidad donde el JUGADOR ve amarillo
    juezAcepta_dz: zGood,                   // rango que el JUEZ da por bueno
    solapa: !!shown && !(shown[1] < zGood[0] || shown[0] > zGood[1]),
  };
};
"""

STALE_JS = r"""
async () => {
  const G = window.__PP_GAME;
  const T = window.__PP_TRAIN;
  const st = T.__debug.st;
  const grp = G.rig.getObjectByName('ppTrainGrp');
  const quad = grp.children.find(m => m.isMesh && m.geometry && m.geometry.type === 'PlaneGeometry');
  const cv = quad.material.map.image;
  const ctx2 = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  const yellowRows = () => {
    let y0 = -1, y1 = -1, n = 0;
    for (let y = 0; y < H; y += 2) {
      const d = ctx2.getImageData(64, y, 1, 1).data;   // lado izquierdo (x≈-0.57)
      if (d[3] > 120 && d[0] > 200 && d[1] > 150 && d[1] < 225 && d[2] < 130) {
        if (y0 < 0) y0 = y; y1 = y; n++;
      }
    }
    return { y0, y1, n };
  };
  const pasos = [];
  const tgt0 = Object.assign({}, st.target);
  for (let k = 0; k < 14; k++) {
    T.__test.okHit(0.9, 1);
    await new Promise(r => setTimeout(r, 40));
    const t = Object.assign({}, st.target);
    const y = yellowRows();
    pasos.push({ k, tgt: t, y: [y.y0, y.y1], n: y.n });
    if (JSON.stringify(t) !== JSON.stringify(tgt0)) break;   // ¡rotó de verdad!
  }
  const yFinal = yellowRows();
  const rotó = JSON.stringify(st.target) !== JSON.stringify(tgt0);
  const pintóCambió = pasos.some(p => p.n > 0) &&
    JSON.stringify(pasos[0].y) !== JSON.stringify([yFinal.y0, yFinal.y1]);
  return { tgt0, rotó, yFinal: [yFinal.y0, yFinal.y1], pasos, pintóCambió };
};
"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded')
        await page.wait_for_function("() => window.__PP_GAME && window.__PP_TRAIN", timeout=45000)

        print('== PRUEBA GPU: ¿dónde se MUESTRA el amarillo? ==')
        r = await page.evaluate(GPU_JS)
        if 'err' in r:
            print('  ✗', r['err']); return 1
        print(f"  target={r['target']} · HL={r['HL']} · C={r['C']}")
        print(f"  el JUGADOR ve amarillo en dz = {r['amarilloSeMuestraEn_dz']} m (desde la red)")
        print(f"  el JUEZ acepta dz        = {r['juezAcepta_dz']} m ({r['target']['z']})")
        ok = r['solapa']
        print(f"  ¿LO PINTADO COINCIDE CON LO JUZGADO? {'SÍ' if ok else 'NO — ZONAS ESPEJADAS/DESPLAZADAS'}")

        print('== STALENESS: rotación real sin repintado ==')
        s = await page.evaluate(STALE_JS)
        if 'err' in s:
            print('  ✗', s['err']); return 1
        for pa in s['pasos']:
            print(f"    okHit#{pa['k']} target={pa['tgt']} filasAmarillas={pa['y']} (n={pa['n']})")
        print(f"  rotó objetivo={s['rotó']} · ¿el pintado cambió en vivo? {s['pintóCambió']}")

        if errs:
            print(f'  pageerrors: {len(errs)}'); [print('   ', e[:120]) for e in errs[:3]]
        await browser.close()
        return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
