#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_train_zonas_v3619.py · QA del ENTRENAMIENTO POR ZONAS (ronda 26).

Cierra el informe del dueño («la zona amarilla no es la buena y zonas sin
marcar dan buenas; al rotar, nunca se ve la zona nueva marcada») y congela
la regresión. Verificación AIRTIGHT vía GPU (render top-down + readPixels):

  1 · ALINEACIÓN t1a: para deep/mid × L/R, el amarillo que el JUGADOR ve en
      la mesa cae DENTRO de la franja que el JUEZ acepta (±4 cm de borde).
  2 · EVITA: la franja roja central se ve a lo largo de toda la mesa y
      NUNCA hay amarillo en |x| < 0.15 (columna prohibida).
  3 · ROTACIÓN EN VIVO: un acierto (okHit real) rota el objetivo y el quad
      SE REPINTA solo — la zona nueva es visible sin tocar nada.
  4 · MODOS HERMANOS del quad: t1b (bandas+FONDO 12 cm), t4a (doble bote
      junto a la red) y t4b (FONDO 15 cm) se muestran donde el juez juzga.
  5 · Cero pageerrors durante toda la batería.

Uso: python3 scripts/qa_train_zonas_v3619.py  (necesita dev :3000)
Salida: RESULTADO: N OK · N fallos  ·  exit 0/1."""
import asyncio
import sys

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'
ok_n = [0]
fail_n = [0]
errs = []


def chk(cond, label):
    if cond:
        ok_n[0] += 1
        print('  ✓ ' + label)
    else:
        fail_n[0] += 1
        print('  ✗ FALLO: ' + label)


BOOT = r"""
async () => {
  const G = window.__PP_GAME;
  const T = window.__PP_TRAIN;
  if (!G || !T) return { err: 'sin juego/entrenamiento' };
  T.startMode(G, 't1a');                       // active necesario para okHit (MODES[active])
  await new Promise(r => setTimeout(r, 150));
  return { ok: true, activo: T.__debug ? 't1a' : '?' };
};
"""

# ── barrido GPU reutilizable ────────────────────────────────────────────
# monta cámara top-down propia, barre dz y devuelve los tramos de dz donde
# el píxel en pantalla cumple el predicado (lo visible NO es el canvas:
# es la textura ya subida con su flipY real).
SWEEP_JS = r"""
(cfg) => {
  const G = window.__PP_GAME;
  const T = window.__PP_TRAIN;
  const st = T.__debug.st;
  const grp = G.rig.getObjectByName('ppTrainGrp');
  const quad = grp.children.find(m => m.isMesh && m.geometry && m.geometry.type === 'PlaneGeometry');
  const HL = quad.geometry.parameters.height;
  const HW = quad.geometry.parameters.width / 2;
  const C  = quad.position.z + HL / 2;
  const yT = quad.position.y;
  const V3 = quad.position.constructor;
  const CamC = G.camera.constructor;
  const halfW = HW + 0.15, halfH = HL / 2 + 0.15;
  const cam = new CamC(50, 1, 0.1, 30);
  cam.aspect = halfW / halfH;
  const dCam = 2.2 - yT;                     // altura REAL sobre la MESA (no sobre el suelo)
  if (cam.isPerspectiveCamera) {
    cam.fov = 2 * Math.atan(halfH / dCam) * 180 / Math.PI;
    cam.position.set(0, 2.2, C - HL / 2);
  } else {
    cam.left = -halfW; cam.right = halfW; cam.top = halfH; cam.bottom = -halfH;
    cam.position.set(0, 2.2, C - HL / 2);
  }
  cam.up = new V3(0, 0, -1);
  cam.lookAt(0, 0, C - HL / 2);
  cam.updateProjectionMatrix();
  G.renderer.render(G.scene, cam);
  const gl = G.renderer.getContext();
  const cw = gl.drawingBufferWidth, ch = gl.drawingBufferHeight;
  const buf = new Uint8Array(4);
  const proj = (x, y, z) => {
    const p = new V3(x, y, z).project(cam);
    return { sx: Math.round((p.x + 1) / 2 * cw), sy: Math.round((1 - (p.y + 1) / 2) * ch) };
  };
  const at = (x, dz) => {
    const { sx, sy } = proj(x, yT + 0.01, C - dz);
    if (sx < 0 || sx >= cw || sy < 0 || sy >= ch) return null;
    gl.readPixels(sx, ch - 1 - sy, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    return [buf[0], buf[1], buf[2], buf[3]];
  };
  const base = at(cfg.x, cfg.baseDz) || [255, 255, 255, 255];   // madera sin pintar (fuera de zonas)
  const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const N = 72;
  const mask = [];
  for (let i = 0; i <= N; i++) {
    const dz = HL * i / N;
    const px = at(cfg.x, dz);
    mask.push(px ? dist(px, base) : 0);
  }
  // tramos contiguos donde el píxel difiere de la madera (> umbral)
  const UMB = 42;
  const tramos = [];
  let ini = -1;
  for (let i = 0; i <= N; i++) {
    const d = mask[i];
    if (d > UMB && ini < 0) ini = i;
    if ((d <= UMB || i === N) && ini >= 0) {
      tramos.push([+(HL * ini / N).toFixed(3), +(HL * i / N).toFixed(3)]);
      ini = -1;
    }
  }
  // y además: píxeles amarillos "puros" (para t1a) por predicado directo
  let y0 = null, y1 = null;
  if (cfg.amarillo) {
    for (let i = 0; i <= N; i++) {
      const dz = HL * i / N;
      const px = at(cfg.x, dz);
      if (px && px[3] > 100 && px[0] > 190 && px[1] > 145 && px[1] < 235 && px[2] < 150) {
        if (y0 === null) y0 = dz;
        y1 = dz;
      }
    }
  }
  G.renderer.render(G.scene, G.camera);   // devolver la cámara al juego
  return { HL, tramos, amarillo: y0 === null ? null : [+y0.toFixed(3), +y1.toFixed(3)] };
};
"""

SET_TARGET_JS = r"""
(cfg) => {
  const T = window.__PP_TRAIN;
  const st = T.__debug.st;
  st.target = { z: cfg.z, x: cfg.x };
  T.__test.drawQuad('t1a');
  return Object.assign({}, st.target);
};
"""

ROTACION_JS = r"""
async () => {
  const G = window.__PP_GAME;
  const T = window.__PP_TRAIN;
  const st = T.__debug.st;
  const grp = G.rig.getObjectByName('ppTrainGrp');
  const quad = grp.children.find(m => m.isMesh && m.geometry && m.geometry.type === 'PlaneGeometry');
  const cv = quad.material.map.image;
  const ctx2 = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  // señal robusta de repintado: filas AMARILLAS y CENTROIDE de columna
  // (una rotación L→R no cambia filas: lo que cambia es la columna)
  const yellowSig = () => {
    let y0 = -1, y1 = -1;
    let sumX = 0, nX = 0;
    for (let y = 0; y < H; y += 2) {
      for (let x = 8; x < W - 8; x += 4) {
        const d = ctx2.getImageData(x, y, 1, 1).data;
        if (d[3] > 120 && d[0] > 200 && d[1] > 150 && d[1] < 225 && d[2] < 130) {
          if (y0 < 0) y0 = y;
          y1 = y; sumX += x; nX++;
        }
      }
    }
    return { y0, y1, cx: nX ? Math.round(sumX / nX) : -1 };
  };
  // fijar un objetivo concreto para saber desde dónde rotamos
  st.target = { z: 'mid', x: -1 };
  T.__test.drawQuad('t1a');
  await new Promise(r => setTimeout(r, 60));
  const antes = yellowSig();
  const tgt0 = Object.assign({}, st.target);
  let pasos = 0, roto = null;
  for (let k = 0; k < 16; k++) {
    T.__test.okHit('ok_zona', 1);              // camino REAL: acierto → rotación
    await new Promise(r => setTimeout(r, 40)); // frames del bucle (sin drawQuad manual)
    pasos++;
    const t = Object.assign({}, st.target);
    if (JSON.stringify(t) !== JSON.stringify(tgt0)) { roto = t; break; }
  }
  const despues = yellowSig();
  const cambioFuerte = Math.abs(antes.cx - despues.cx) > 30 ||
    Math.abs(antes.y0 - despues.y0) > 8 || Math.abs(antes.y1 - despues.y1) > 8;
  return {
    tgt0, roto, pasos, antes, despues,
    repintoSolo: cambioFuerte,
  };
};
"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded')
        await page.wait_for_function("() => window.__PP_GAME && window.__PP_TRAIN", timeout=45000)

        boot = await page.evaluate(BOOT)
        if boot.get('err'):
            print('  ✗ FALLO:', boot['err'])
            print('RESULTADO: 0 OK · 1 fallos')
            return 1

        print('== 1 · ALINEACIÓN t1a (GPU: lo visible == lo juzgado) ==')
        JUEZ = {   # dz aceptado por zoneOf() por fila (HL=1.37)
            'deep': (0.685, 1.37), 'mid': (0.3425, 0.685),
        }
        HL = 1.37
        for z in ('deep', 'mid'):
            for x in (-1, 1):
                await page.evaluate(SET_TARGET_JS, {'z': z, 'x': x})
                r = await page.evaluate(SWEEP_JS, {'x': x * (0.15 + 0.76) / 2, 'amarillo': True, 'baseDz': 0.35 * HL})
                am = r['amarillo']
                jlo, jhi = JUEZ[z]
                dentro = am and am[0] >= jlo - 0.04 and am[1] <= jhi + 0.04 and (am[1] - am[0]) > 0.15
                chk(dentro, f"t1a {z}{'L' if x < 0 else 'R'}: amarillo visible dz={am} ⊆ juez [{jlo}, {jhi}]")

        print('== 2 · FRANJA EVITA (roja central, nunca amarilla) ==')
        # EVITA: rojo dominante en 3 profundidades (la franja cubre toda la mesa)
        RED_JS = r"""
(cfg) => {
  const G = window.__PP_GAME;
  const grp = G.rig.getObjectByName('ppTrainGrp');
  const quad = grp.children.find(m => m.isMesh && m.geometry && m.geometry.type === 'PlaneGeometry');
  const HL = quad.geometry.parameters.height;
  const C = quad.position.z + HL / 2;
  const V3 = quad.position.constructor;
  const CamC = G.camera.constructor;
  const halfW = 0.76 + 0.15, halfH = HL / 2 + 0.15;
  const cam = new CamC(50, 1, 0.1, 30);
  cam.aspect = halfW / halfH;
  cam.fov = 2 * Math.atan(halfH / (2.2 - quad.position.y)) * 180 / Math.PI;
  cam.position.set(0, 2.2, C - HL / 2);
  cam.up = new V3(0, 0, -1);
  cam.lookAt(0, 0, C - HL / 2);
  cam.updateProjectionMatrix();
  G.renderer.render(G.scene, cam);
  const gl = G.renderer.getContext();
  const ch = gl.drawingBufferHeight, cw = gl.drawingBufferWidth;
  const buf = new Uint8Array(4);
  const out = [];
  for (const dz of cfg.dzs) {
    const p = new V3(0, quad.position.y + 0.01, C - dz).project(cam);
    const sx = Math.round((p.x + 1) / 2 * cw), sy = Math.round((1 - (p.y + 1) / 2) * ch);
    gl.readPixels(sx, ch - 1 - sy, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    out.push([buf[0], buf[1], buf[2]]);
  }
  G.renderer.render(G.scene, G.camera);
  return out;
}"""
        rojos = await page.evaluate(RED_JS, {'dzs': [0.2, 0.7, 1.2]})
        es_rojo = lambda rgb: rgb[0] > rgb[1] + 35 and rgb[0] > rgb[2] + 35
        chk(all(es_rojo(r) for r in rojos), f'EVITA roja en dz 0.2/0.7/1.2 → {rojos}')
        r = await page.evaluate(SWEEP_JS, {'x': 0.0, 'amarillo': True, 'baseDz': 0.35 * HL})
        chk(r['amarillo'] is None, 'sin amarillo en la columna prohibida (|x|<0.15)')

        print('== 3 · ROTACIÓN EN VIVO (okHit repinta el quad) ==')
        s = await page.evaluate(ROTACION_JS)
        chk(bool(s['roto']), f"okHit rotó el objetivo {s['tgt0']} → {s['roto']} en {s['pasos']} aciertos")
        chk(s['repintoSolo'], f"el quad SE REPINTÓ solo (antes cx={s['antes']['cx']},y {s['antes']['y0']}-{s['antes']['y1']} → después cx={s['despues']['cx']},y {s['despues']['y0']}-{s['despues']['y1']})")

        print('== 4 · MODOS HERMANOS del quad (t1b / t4a / t4b) ==')
        for modo, col, base_dz, dz_esp, tol in (
            ('t1b', 0.0, 0.40, (HL - 0.13, HL + 0.01), 0.05),    # FONDO 12 cm + borde
            ('t4a', 0.0, 0.75, (0.03, 0.58), 0.04),              # doble bote junto a la red
            ('t4b', 0.0, 0.40, (HL - 0.17, HL + 0.01), 0.05),    # FONDO 15 cm + borde
        ):
            await page.evaluate(f"() => window.__PP_TRAIN.startMode(window.__PP_GAME, '{modo}')")
            await page.wait_for_timeout(80)
            r = await page.evaluate(SWEEP_JS, {'x': col, 'amarillo': False, 'baseDz': base_dz * HL})
            cuerpo = max(r['tramos'], key=lambda t: t[1] - t[0]) if r['tramos'] else None
            bien = cuerpo and cuerpo[0] >= dz_esp[0] - tol and cuerpo[1] <= dz_esp[1] + tol
            chk(bien, f"{modo}: franja visible dz={cuerpo} ⊆ esperado [{dz_esp[0]:.2f}, {dz_esp[1]:.2f}]")
        # volver a t1a para el estado final limpio
        await page.evaluate("() => window.__PP_TRAIN.startMode(window.__PP_GAME, 't1a')")

        print('== 5 · pageerrors ==')
        chk(len(errs) == 0, f'0 pageerrors durante la batería ({len(errs)} vistos)')

        total = f"RESULTADO: {ok_n[0]} OK · {fail_n[0]} fallos"
        print(total)
        await browser.close()
        return 0 if fail_n[0] == 0 else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
