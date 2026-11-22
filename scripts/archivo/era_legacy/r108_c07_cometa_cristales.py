#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r108 · c07 — DOS fábricas:

1 · COMETA r108 (el dueño: «siguen muy cutres… pequeñas partículas de
    chispas que salen como la cola de un cometa dejando una estela de
    humo azulado; deben ser partículas densas y pequeñas»): TRES capas —
    CHISPAS más DENSAS (170/s) y MÁS PEQUEÑAS (0,0095) · RASTRO fino ·
    HUMO AZULADO (burbujas lentas azul-gris que quedan flotando y se
    disipan). Pools fijos, cero asignaciones por frame.
2 · createCristalesCripto — los cristales del SUPER CRIPTONITA: cuarzo
    verde VETEADO (textura procedural de vetas) que brota 1-5 por bote
    en la mesa del rival (20-50 cm aleatorio), pulsa en emisivo, y
    ROMPE al chocar con la bola. Pool fijo de 24.
"""
import io

R = '/home/z/my-project/src/game/core/'
c07 = io.open(R + 'c07_escena_sala.js', encoding='utf-8').read()

M_EST = '/* =====================================================================\n *  r107 (v3.6.205) · COMETA DEL PODER'
M_NUBE = '/* =====================================================================\n *  r107 (v3.6.205) · NUBE DE PRISMAS'
M_BLOB = 'export function createBlobShadow() {'
i1, i2, i3 = c07.find(M_EST), c07.find(M_NUBE), c07.find(M_BLOB)
assert 0 <= i1 < i2 < i3, f"c07: marcadores fuera de orden ({i1},{i2},{i3})"

COMET_TX = r'''/* =====================================================================
 *  r108 (v3.6.206) · COMETA DEL PODER — segunda reconstrucción (el dueño
 *  tras la r107: «las estelas siguen muy cutres, deben parecer pequeñas
 *  partículas de chispas que salen como si fuesen la cola de un cometa
 *  dejando una estela de humo azulado; debe ser partículas densas y
 *  pequeñas»). TRES capas en pools FIJOS (cero asignaciones por frame):
 *   · CHISPAS (220): MÁS PEQUEÑAS (0,0095) y MÁS DENSAS (~170/s) —
 *     nacen en la bola y SALEN HACIA ATRÁS (30 % del vuelo + jitter
 *     corto), aditivas, vida 0,5 s: la cola de chispas del cometa.
 *   · RASTRO (140): micro-polvo (0,0065) que marca la línea del vuelo
 *     y se disipa en ~1,1 s.
 *   · HUMO (110): burbujas AZULADAS grandes y lentas (0,055, 12 % de
 *     opacidad) que quedan flotando tras la bola y SE DISIPAN — la
 *     estela de humo del encargo.
 *  El color de chispas/rastro lo pone el NÚCLEO (firma del poder,
 *  _trailFirmaPoder r61 — el verde cripto incluido); el humo es SIEMPRE
 *  azulado (el dueño lo pidió literal). La emisión la manda emitir(pos,
 *  vel, dt, rgb) con deuda interna — el núcleo solo decide SI.
 *  ===================================================================== */
export function createEstelaPoder() {
  const mk = (N, size, opacity) => {
    const pos = new Float32Array(N * 3);
    const vel = new Float32Array(N * 3);
    const col = new Float32Array(N * 3);
    const base = new Float32Array(N * 3);
    const ages = new Float32Array(N).fill(99);      // nacidas muertas
    for (let i = 0; i < N; i++) pos[i * 3 + 1] = -10;   // fuera de vista
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const mat = new THREE.PointsMaterial({
      size, vertexColors: true, transparent: true, opacity,
      blending: THREE.AdditiveBlending, depthWrite: false,
    });
    const pts = new THREE.Points(geo, mat);
    pts.visible = false;
    pts.frustumCulled = false;
    pts.renderOrder = 67;
    return { pos, vel, col, base, ages, geo, mat, pts, N, prox: 0, VIDA: 0 };
  };
  const chispa = mk(220, 0.0095, 0.95);
  chispa.VIDA = 0.5;                                // chispa viva y breve
  const rastro = mk(140, 0.0065, 0.45);
  rastro.VIDA = 1.1;                                // polvo fino que linger
  const humo = mk(110, 0.055, 0.12);
  humo.VIDA = 1.45;                                 // burbuja azulada lenta
  const HUMO_AZUL = [0.5, 0.68, 0.95];              // el «humo azulado» literal
  const grp = new THREE.Group();
  grp.add(chispa.pts);
  grp.add(rastro.pts);
  grp.add(humo.pts);
  const _c = new THREE.Color();
  const naceEn = (L, px, py, pz, dx, dy, dz, rgb, mezclaAzul) => {
    const i = L.prox;
    L.prox = (L.prox + 1) % L.N;
    L.pos[i * 3] = px; L.pos[i * 3 + 1] = py; L.pos[i * 3 + 2] = pz;
    L.vel[i * 3] = dx; L.vel[i * 3 + 1] = dy; L.vel[i * 3 + 2] = dz;
    L.ages[i] = 0;
    if (rgb === 'arcoiris') {
      _c.setHSL(Math.random(), 0.95, 0.6);
      L.base[i * 3] = _c.r; L.base[i * 3 + 1] = _c.g; L.base[i * 3 + 2] = _c.b;
    } else if (mezclaAzul) {
      // el humo tira SIEMPRE al azul con un eco del color del poder
      L.base[i * 3] = HUMO_AZUL[0] * 0.75 + rgb[0] * 0.25;
      L.base[i * 3 + 1] = HUMO_AZUL[1] * 0.75 + rgb[1] * 0.25;
      L.base[i * 3 + 2] = HUMO_AZUL[2] * 0.75 + rgb[2] * 0.25;
    } else {
      L.base[i * 3] = rgb[0]; L.base[i * 3 + 1] = rgb[1]; L.base[i * 3 + 2] = rgb[2];
    }
    L.col[i * 3] = L.base[i * 3];
    L.col[i * 3 + 1] = L.base[i * 3 + 1];
    L.col[i * 3 + 2] = L.base[i * 3 + 2];
    L.pts.visible = true;
    L.geo.attributes.position.needsUpdate = true;
    L.geo.attributes.color.needsUpdate = true;
  };
  const paso = (L, dt, grav, freno) => {
    let vivo = false;
    const pa = L.geo.attributes.position.array;
    const ca = L.geo.attributes.color.array;
    for (let i = 0; i < L.N; i++) {
      if (L.ages[i] >= L.VIDA) continue;
      vivo = true;
      L.ages[i] += dt;
      if (L.ages[i] >= L.VIDA) { pa[i * 3 + 1] = -10; continue; }
      L.vel[i * 3 + 1] -= dt * grav;
      const f = Math.max(0, 1 - dt * freno);
      L.vel[i * 3] *= f;
      L.vel[i * 3 + 1] *= f;
      L.vel[i * 3 + 2] *= f;
      pa[i * 3] += L.vel[i * 3] * dt;
      pa[i * 3 + 1] += L.vel[i * 3 + 1] * dt;
      pa[i * 3 + 2] += L.vel[i * 3 + 2] * dt;
      const k = Math.max(0, 1 - L.ages[i] / L.VIDA);
      ca[i * 3] = L.base[i * 3] * k;
      ca[i * 3 + 1] = L.base[i * 3 + 1] * k;
      ca[i * 3 + 2] = L.base[i * 3 + 2] * k;
    }
    if (vivo) {
      L.geo.attributes.position.needsUpdate = true;
      L.geo.attributes.color.needsUpdate = true;
    } else if (L.pts.visible) L.pts.visible = false;
  };
  let accC = 0, accR = 0, accH = 0;
  return {
    group: grp,
    /** Emisión de cometa: chispas DETRÁS de la bola (contra el vuelo) +
     *  rastro fino + humo azulado. rgb: firma [r,g,b] — o 'arcoiris'. */
    emitir(pos, vel, dt, rgb) {
      accC += dt * 170;                       // DENSAS: ~170 chispas/s
      let n = Math.min(6, Math.floor(accC));
      accC -= n;
      while (n-- > 0) {
        naceEn(chispa,
          pos.x + (Math.random() - 0.5) * 0.016,
          pos.y + (Math.random() - 0.5) * 0.016,
          pos.z + (Math.random() - 0.5) * 0.016,
          -vel.x * 0.30 + (Math.random() - 0.5) * 0.14,
          -vel.y * 0.30 + (Math.random() - 0.5) * 0.14,
          -vel.z * 0.30 + (Math.random() - 0.5) * 0.14,
          rgb, false);
      }
      accR += dt * 70;
      let m = Math.min(3, Math.floor(accR));
      accR -= m;
      while (m-- > 0) {
        naceEn(rastro,
          pos.x + (Math.random() - 0.5) * 0.012,
          pos.y + (Math.random() - 0.5) * 0.012,
          pos.z + (Math.random() - 0.5) * 0.012,
          -vel.x * 0.08 + (Math.random() - 0.5) * 0.05,
          -vel.y * 0.08 + (Math.random() - 0.5) * 0.05,
          -vel.z * 0.08 + (Math.random() - 0.5) * 0.05,
          rgb, false);
      }
      accH += dt * 30;
      let h = Math.min(2, Math.floor(accH));
      accH -= h;
      while (h-- > 0) {
        naceEn(humo,
          pos.x + (Math.random() - 0.5) * 0.05,
          pos.y + (Math.random() - 0.5) * 0.05,
          pos.z + (Math.random() - 0.5) * 0.05,
          -vel.x * 0.05 + (Math.random() - 0.5) * 0.06,
          0.04 + Math.random() * 0.06,               // el humo SUBE despacio
          -vel.z * 0.05 + (Math.random() - 0.5) * 0.06,
          rgb, true);
      }
    },
    /** Paso por frame de las tres capas. */
    update(dt) {
      paso(chispa, dt, 0.5, 3.5);       // chispas: caen y frenan fuerte
      paso(rastro, dt, 0.1, 2.0);       // polvo: casi flota, se disipa
      paso(humo, dt, -0.02, 1.1);       // humo: asciende y se disipa lento
    },
    dispose() {
      try {
        chispa.geo.dispose(); chispa.mat.dispose();
        rastro.geo.dispose(); rastro.mat.dispose();
        humo.geo.dispose(); humo.mat.dispose();
      } catch { /* */ }
    },
  };
}

'''

CRIST_TX = r'''/* =====================================================================
 *  r108 (v3.6.206) · CRISTALES DE CRIPTONITA — SUPER CRIPTONITA (el
 *  dueño: «cuando la bola en este estado golpea la mesa hace crecer de
 *  uno a hasta 5 prismas de verde fosforito que simulan cristales de
 *  cuarzo verdosos (deberían parecer cristales veteados verdosos
 *  realistas) que pueden crecer desde 20 hasta 50 cm, aleatorio, sobre
 *  la superficie de la mesa del rival»). Cuarzo HEXAGONAL (prisma +
 *  punta piramidal) con textura de VETAS procedural (venas claras y
 *  oscuras onduladas) y emisivo fosforito que pulsa; crecen con
 *  rebote suave desde la superficie de la mesa. Si la bola los golpea
 *  se ROMPEN (encogido + giro) — el freno y la dirección aleatoria los
 *  aplica el núcleo. Pool fijo de 24 (las viejas se deshacen solas).
 *  ===================================================================== */
export function createCristalesCripto() {
  const N = 24, CRECE = 0.45, MUERTE = 0.3, VIDA = 11.0;
  // — textura de VETAS (cuarzo verdoso realista), lienzo procedural —
  const cv = document.createElement('canvas');
  cv.width = 128;
  cv.height = 256;
  const g = cv.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 128, 256);
  grad.addColorStop(0, '#0d2f16');
  grad.addColorStop(0.45, '#2f8f4a');
  grad.addColorStop(1, '#1a5c2e');
  g.fillStyle = grad;
  g.fillRect(0, 0, 128, 256);
  for (let v = 0; v < 16; v++) {
    const x0 = (v / 16) * 128 + Math.random() * 6;
    const claro = v % 2 === 0;
    g.strokeStyle = claro ? 'rgba(206, 255, 214, 0.5)' : 'rgba(4, 22, 10, 0.62)';
    g.lineWidth = claro ? 1.6 + Math.random() * 1.6 : 2.4 + Math.random() * 2.6;
    g.beginPath();
    let x = x0;
    g.moveTo(x, -6);
    for (let y = 0; y <= 256; y += 16) {
      x = x0 + Math.sin(y * 0.06 + v * 1.7) * 5 + (Math.random() - 0.5) * 2.4;
      g.lineTo(x, y);
    }
    g.stroke();
  }
  for (let b = 0; b < 6; b++) {                   // bandas horizontales sutiles
    g.fillStyle = 'rgba(11, 46, 22, 0.16)';
    g.fillRect(0, 24 + b * 42 + Math.random() * 8, 128, 5 + Math.random() * 7);
  }
  const tex = new THREE.CanvasTexture(cv);
  const mat = new THREE.MeshStandardMaterial({
    map: tex, emissiveMap: tex, emissive: new THREE.Color(0x39ff6e),
    emissiveIntensity: 0.55, roughness: 0.28, metalness: 0.08,
  });
  const geoC = new THREE.CylinderGeometry(0.55, 1.0, 3.0, 6, 1);  // prisma hex.
  const geoP = new THREE.ConeGeometry(0.55, 1.1, 6);               // punta
  const grupo = new THREE.Group();
  grupo.visible = true;
  const P = [];
  for (let i = 0; i < N; i++) {
    const prism = new THREE.Mesh(geoC, mat);
    prism.position.y = 1.5;
    const tip = new THREE.Mesh(geoP, mat);
    tip.position.y = 3.0 + 0.55;
    const g2 = new THREE.Group();
    g2.add(prism);
    g2.add(tip);
    g2.visible = false;
    grupo.add(g2);
    P.push({ grp: g2, t: -1, crece: 0, roto: -1, h: 0.3, r: 0.05,
      x: 0, y: 0, z: 0, vida: VIDA });
  }
  let prox = 0;
  const GEO_ALTO = 4.1;   // prisma 3,0 + punta 1,1 (unidades de la geometría)
  return {
    group: grupo,
    /** Nace UNA cosecha de 1-5 cristales cerca de p (el punto del bote en
     *  la mesa del rival). Alturas 20-50 cm y radios aleatorios. */
    nace(p, topY) {
      const ty = topY || 0.76;
      const cuantos = 1 + Math.floor(Math.random() * 5);   // 1..5 (spec)
      for (let k = 0; k < cuantos; k++) {
        const s = P[prox];
        prox = (prox + 1) % N;
        s.t = 0;
        s.crece = 0;
        s.roto = -1;
        s.vida = VIDA;
        s.h = 0.20 + Math.random() * 0.30;                 // 20-50 cm (spec)
        s.r = s.h * (0.14 + Math.random() * 0.07);
        s.x = p.x + (Math.random() - 0.5) * 0.18;
        s.z = p.z + (Math.random() - 0.5) * 0.18;
        s.y = ty;
        s.grp.position.set(s.x, s.y, s.z);
        s.grp.rotation.set((Math.random() - 0.5) * 0.24, Math.random() * Math.PI * 2,
          (Math.random() - 0.5) * 0.24);
        s.grp.scale.set(0.001, 0.001, 0.001);              // nace del suelo
        s.grp.visible = true;
      }
      return cuantos;
    },
    /** Crecimiento (con rebote suave) + pulso fosforito + muertes. */
    update(dt) {
      const ph = performance.now() * 0.001;
      mat.emissiveIntensity = 0.42 + 0.3 * (0.5 + 0.5 * Math.sin(ph * 5.2));
      for (let i = 0; i < N; i++) {
        const s = P[i];
        if (s.t < 0) continue;
        s.t += dt;
        if (s.roto >= 0) {
          s.roto += dt;
          const k = Math.max(0.001, 1 - s.roto / MUERTE);
          s.grp.scale.set(s.r * (1 + s.roto * 3), (s.h / GEO_ALTO) * k,
            s.r * (1 + s.roto * 3));
          s.grp.rotation.y += dt * 18;
          if (s.roto >= MUERTE) { s.t = -1; s.grp.visible = false; }
          continue;
        }
        s.vida -= dt;
        if (s.vida <= 0) { s.t = -1; s.grp.visible = false; continue; }
        if (s.crece < 1) {
          s.crece = Math.min(1, s.crece + dt / CRECE);
          // rebote suave al crecer (ease-out con overshoot corto)
          const e = s.crece;
          const reb = 1 + Math.sin(Math.min(1, e) * Math.PI) * 0.18;
          s.grp.scale.set(s.r * Math.min(1, e * 2.2), (s.h / GEO_ALTO) * e * reb,
            s.r * Math.min(1, e * 2.2));
        }
      }
    },
    /** ¿La bola choca con un cristal? Devuelve su índice o -1. */
    colisiona(pos, rBola) {
      for (let i = 0; i < N; i++) {
        const s = P[i];
        if (s.t < 0 || s.roto >= 0 || s.crece < 0.5) continue;
        const dx = pos.x - s.x;
        const dz = pos.z - s.z;
        const rr = s.r * 0.92 + rBola;
        const crecido = s.h * Math.min(1, s.crece * 1.18);
        if (dx * dx + dz * dz <= rr * rr &&
            pos.y >= s.y - 0.02 && pos.y <= s.y + crecido + 0.08) {
          return i;
        }
      }
      return -1;
    },
    /** Rompe el cristal i (el núcleo aplica el freno/dirección). */
    rompe(i) {
      if (i < 0 || i >= N) return;
      P[i].roto = 0;
    },
    /** Fin de la ventana: todos los cristales vivos se deshacen. */
    fin() {
      for (let i = 0; i < N; i++) {
        if (P[i].t >= 0 && P[i].roto < 0) P[i].roto = 0;
      }
    },
    vivos() {
      let n = 0;
      for (let i = 0; i < N; i++) if (P[i].t >= 0 && P[i].roto < 0) n++;
      return n;
    },
    dispose() {
      try { geoC.dispose(); geoP.dispose(); mat.dispose(); tex.dispose(); } catch { /* */ }
    },
  };
}

'''

c07 = c07[:i1] + COMET_TX + c07[i2:i3] + CRIST_TX + c07[i3:]
io.open(R + 'c07_escena_sala.js', 'w', encoding='utf-8').write(c07)
print("c07: cometa de 3 capas (chispas densas/pequeñas + rastro + humo azulado) + cristales de criptonita")
