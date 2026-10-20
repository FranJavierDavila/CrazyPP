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
  5 · TEXTOS del quad (EVITA/OBJETIVO/FONDO/DOBLE BOTE/FONDO 15 cm) pintados
      con el patrón LEGIBLE para el jugador. Con flipY=false el jugador ve el
      lienzo con la fila 0 en la RED, así que un texto se lee de pie sólo si
      se dibuja con scale(1,-1) (parte alta hacia la fila H = fondo). El
      rotate(π) histórico lo dejaba en ESPEJO (informe del dueño v3.6.19).
      Método: réplica exacta del bloque de pintado nuevo (vflip) vs antiguo
      (rot180) sobre el canvas real → IoU con búsqueda de desplazamiento ±3.
  6 · Cero pageerrors durante toda la batería.

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

# ── chequeo de TEXTOS del quad ──────────────────────────────────────────
# Réplica EXACTA de los dos bloques de pintado posibles dentro de drawQuad:
#   · vflip  = código NUEVO (v3.6.20): translate → scale(1,-1) → baseline
#     middle  ⇒ el jugador (que ve el lienzo con la fila 0 en la red) lee
#     el texto de pie.
#   · rot180 = código ANTIGuo: translate → rotate(π) (baseline alphabetic
#     salvo OBJETIVO, que ya usaba middle) ⇒ el jugador lo ve en ESPEJO.
# Sólo cambia el transform/baseline entre refs; todo lo demás (fuente,
# colores, ancla, stroke) se copia del drawQuad real. Gana el patrón con
# mayor IoU contra la tinta real del canvas del juego (±3 px de búsqueda).
TEXTCHECK_JS = r"""
(cfg) => {
  const G = window.__PP_GAME;
  const T = window.__PP_TRAIN;
  const grp = G.rig.getObjectByName('ppTrainGrp');
  const quad = grp.children.find(m => m.isMesh && m.geometry && m.geometry.type === 'PlaneGeometry');
  const cv = quad.material.map.image;
  const g = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  const HW = quad.geometry.parameters.width / 2;
  const HL = quad.geometry.parameters.height;
  const C = quad.position.z + HL / 2;
  const mx = (x) => W / 2 + (x / HW) * (W / 2);
  const mz = (z) => H * ((C - z) / HL);
  // ancla + estilo, réplica del drawQuad por clave
  let ax, ay, font, fill, stroke = null, lw = 0, baseOld = 'alphabetic';
  const text = cfg.text;
  if (cfg.k === 'evita') {
    ax = mx(0); ay = H - 26;
    font = '700 26px system-ui, sans-serif';
    fill = 'rgba(255,150,150,1)';
  } else if (cfg.k === 'objetivo') {
    const st = T.__debug.st;
    const zr = st.target.z === 'deep' ? [C - HL, C - HL / 2] : [C - HL / 2, C - HL / 4];
    const xr = st.target.x < 0 ? [-HW, -0.15] : [0.15, HW];
    const zx0 = mx(xr[0]), zx1 = mx(xr[1]), zy0 = mz(zr[0]), zy1 = mz(zr[1]);
    ax = (zx0 + zx1) / 2; ay = (zy0 + zy1) / 2;
    let ztSize = Math.min(58, Math.floor((Math.abs(zy1 - zy0) - 18) * 0.62));
    const ztW = Math.abs(zx1 - zx0) - 26;
    const mc = document.createElement('canvas').getContext('2d');
    mc.font = '900 ' + ztSize + 'px system-ui, sans-serif';
    const wid = mc.measureText(text).width;
    if (wid > ztW) ztSize = Math.max(20, Math.floor(ztSize * ztW / wid));
    font = '900 ' + ztSize + 'px system-ui, sans-serif';
    fill = '#1a1408';
    stroke = 'rgba(40,24,0,0.85)'; lw = 6;
    baseOld = 'middle';
  } else if (cfg.k === 'fondo_t1b') {
    const zb = [C - HL, C - HL + 0.12];
    ax = W / 2; ay = (mz(zb[0]) + mz(zb[1])) / 2;
    font = '900 40px system-ui, sans-serif'; fill = '#0c1826';
  } else if (cfg.k === 'doble') {
    const zr = [C - 0.56, C - 0.05];
    ax = W / 2; ay = (mz(zr[0]) + mz(zr[1])) / 2;
    font = '900 40px system-ui, sans-serif'; fill = '#241206';
  } else if (cfg.k === 'f15') {
    const zr = [C - HL, C - HL + 0.15];
    ax = W / 2; ay = (mz(zr[0]) + mz(zr[1])) / 2;
    font = '900 30px system-ui, sans-serif'; fill = '#241206';
  }
  // ventana de muestreo (relativa al ancla; esquiva rejillas/bordes pintados)
  const OFF = {
    evita: [-45, -28, 90, 48],
    objetivo: [-80, -34, 160, 68],
    fondo_t1b: [-90, -22, 180, 30],   // dentro de la franja azul, fuera del borde de 9 px
    doble: [-240, -44, 480, 88],
    f15: [-110, -17, 220, 34],
  }[cfg.k];
  const x0 = Math.round(ax + OFF[0]), y0 = Math.round(ay + OFF[1]);
  const ww = OFF[2], hh = OFF[3];
  // fondo de referencia: color DOMINANTE de la ventana (buckets de 8 por
  // canal) — robusto aunque la ventana pise dos fondos (madera+franja).
  const img = g.getImageData(x0, y0, ww, hh).data;
  const buckets = new Map();
  for (let i = 0; i < img.length; i += 4) {
    const key = ((img[i] >> 3) << 10) | ((img[i + 1] >> 3) << 5) | (img[i + 2] >> 3);
    let b = buckets.get(key);
    if (!b) { b = [0, 0, 0, 0]; buckets.set(key, b); }
    b[0]++; b[1] += img[i]; b[2] += img[i + 1]; b[3] += img[i + 2];
  }
  let bestB = null;
  for (const b of buckets.values()) if (!bestB || b[0] > bestB[0]) bestB = b;
  const bg = [Math.round(bestB[1] / bestB[0]), Math.round(bestB[2] / bestB[0]), Math.round(bestB[3] / bestB[0])];
  const dist = (r, g2, b, c) => Math.hypot(r - c[0], g2 - c[1], b - c[2]);
  const maskOf = (data, bgc) => {
    const m = new Uint8Array(ww * hh);
    for (let i = 0, p = 0; i < data.length; i += 4, p++) {
      m[p] = dist(data[i], data[i + 1], data[i + 2], bgc) > 60 ? 1 : 0;
    }
    return m;
  };
  const A = maskOf(img, bg);
  let ink = 0;
  for (let p = 0; p < A.length; p++) ink += A[p];
  // refs: mismas propiedades, SÓLO cambia transform/baseline (nuevo vs antiguo)
  const refMask = (modo) => {
    const rc = document.createElement('canvas');
    rc.width = ww; rc.height = hh;
    const r = rc.getContext('2d');
    r.fillStyle = 'rgb(' + bg.join(',') + ')';
    r.fillRect(0, 0, ww, hh);
    r.save();
    r.translate(-x0, -y0);
    r.translate(ax, ay);
    if (modo === 'vflip') { r.scale(1, -1); r.textBaseline = 'middle'; }
    else { r.rotate(Math.PI); r.textBaseline = baseOld; }
    r.font = font; r.textAlign = 'center';
    if (stroke) { r.lineWidth = lw; r.strokeStyle = stroke; r.strokeText(text, 0, 0); }
    r.fillStyle = fill;
    r.fillText(text, 0, 0);
    r.restore();
    return maskOf(r.getImageData(0, 0, ww, hh).data, bg);
  };
  const RV = refMask('vflip'), RR = refMask('rot180');
  const iou = (Bm) => {
    let best = 0;
    for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) {
      let inter = 0, uni = 0;
      for (let y = 0; y < hh; y++) for (let x = 0; x < ww; x++) {
        const xs = x + dx, ys = y + dy;
        const a = A[y * ww + x];
        const b = (xs >= 0 && xs < ww && ys >= 0 && ys < hh) ? Bm[ys * ww + xs] : 0;
        if (a || b) uni++;
        if (a && b) inter++;
      }
      if (uni) best = Math.max(best, inter / uni);
    }
    return best;
  };
  const iouV = iou(RV), iouR = iou(RR);
  let winner = 'indeciso';
  if (iouV >= iouR + 0.10) winner = 'vflip';
  else if (iouR >= iouV + 0.10) winner = 'rot180';
  return { k: cfg.k, ink, iouV: +iouV.toFixed(3), iouR: +iouR.toFixed(3), winner,
           font, ax: Math.round(ax), ay: Math.round(ay) };
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

        print('== 5 · TEXTOS del quad legibles desde el jugador (vflip vs espejo) ==')
        TEXTOS = [
            ('t1a', 'evita', 'EVITA'),
            ('t1a', 'objetivo', 'OBJETIVO'),
            ('t1b', 'fondo_t1b', 'FONDO'),
            ('t4a', 'doble', 'DOBLE BOTE'),
            ('t4b', 'f15', 'FONDO 15 cm'),
        ]
        modo_act = None
        for modo, k, txt in TEXTOS:
            if modo != modo_act:
                await page.evaluate(f"() => window.__PP_TRAIN.startMode(window.__PP_GAME, '{modo}')")
                await page.wait_for_timeout(90)
                modo_act = modo
            if k == 'objetivo':
                await page.evaluate(SET_TARGET_JS, {'z': 'deep', 'x': -1})
            r = await page.evaluate(TEXTCHECK_JS, {'k': k, 'text': txt})
            if r.get('err') or r['ink'] < 40:
                chk(False, f"{modo}/{k}: tinta insuficiente ({r.get('ink')} px) — revisar ventana/fuente")
            else:
                chk(r['winner'] == 'vflip' and r['iouV'] > 0.30,
                    f"{modo}/{k}: patrón LEGIBLE para el jugador (IoU nuevo={r['iouV']} vs espejo={r['iouR']}, tinta={r['ink']})")
        await page.evaluate("() => window.__PP_TRAIN.startMode(window.__PP_GAME, 't1a')")

        print('== 6 · pageerrors ==')
        chk(len(errs) == 0, f'0 pageerrors durante la batería ({len(errs)} vistos)')

        total = f"RESULTADO: {ok_n[0]} OK · {fail_n[0]} fallos"
        print(total)
        await browser.close()
        return 0 if fail_n[0] == 0 else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
