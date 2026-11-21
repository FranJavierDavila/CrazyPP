#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r107 · PUNTUALIZACIÓN DEL DUEÑO sobre la r106 (6 encargos):

1 · COMETA, NO CONFETI: la estela del poder se reconstruye — chispas que
    salen DETRÁS de la bola (contra el vuelo) + un rastro tenue que se
    queda flotando y se disipa.
2 · SOLO EL LANZADOR: el cometa jamás se dibuja en la pantalla del rival
    (_megaActivaMia — las ventanas que el relay remoto arma no emiten).
3 · SOLO ENVÍOS PROPIOS: la bola viajando hacia el rival (vel.z < 0 en
    ambos clientes — convención «mi mitad = z > centro», r84/r43). Nada
    en las devoluciones del rival.
4 · SIN DUPLICAR ESTELAS: los poderes con vestido propio (fénix, prisma,
    crono, elec, oscuridad, salva, bolaloca) NO llevan el cometa.
5 · PRISMAS 3D REALES: sombreado de facetas HORNEADO en vértices (dos
    luces fijas + tono frío/cálido por cara) — nada plano.
6 · SÚPER EFECTO: bote INESPERADO en la mesa del rival (patada lateral
    imprevisible + profundidad + hop) · ONDA DE CHOQUE: esfera-escudo
    azulona semitransparente con pentágonos, centrada en la pala al
    impacto, crece empujando la bola con su superficie, la bola viaja AL
    DOBLE, muere en suelo/pala rival, con energía grave creciente.
"""
import io

R = '/home/z/my-project/src/game/core/'

# ════════════════════════ c07 · RECONSTRUCCIÓN DE LAS FÁBRICAS ═════
c07 = io.open(R + 'c07_escena_sala.js', encoding='utf-8').read()

M_EST = '/* =====================================================================\n *  r106 (v3.6.204) · ESTELA DE PARTÍCULAS DEL PODER'
M_NUBE = '/* =====================================================================\n *  r106 (v3.6.204) · NUBE DE PRISMAS DEL ARCOÍRIS'
M_BLOB = 'export function createBlobShadow() {'
i1, i2, i3 = c07.find(M_EST), c07.find(M_NUBE), c07.find(M_BLOB)
assert 0 <= i1 < i2 < i3, f"c07: marcadores fuera de orden ({i1},{i2},{i3})"

COMET_TX = r'''/* =====================================================================
 *  r107 (v3.6.205) · COMETA DEL PODER — reconstrucción de la estela
 *  r106 (el dueño: «la estela actual parece confeti, queremos un efecto
 *  más chulo de cometa, una cola de color como chispas que salen detrás
 *  de la bola dejando un rastro tenue que se acaba disipando»).
 *  DOS capas en pools FIJOS (cero asignaciones por frame):
 *   · CHISPAS (120): nacen en la bola y SALEN HACIA ATRÁS — contra el
 *     vuelo (30 % de su velocidad + jitter corto) — brillantes,
 *     aditivas, gravedad ligera y freno fuerte: la cola luminosa.
 *   · RASTRO (90): más tenues, más lentas, vida larga (1,15 s): la
 *     estela suave que queda flotando y SE DISIPA.
 *  El color lo pone el NÚCLEO (firma del poder, _trailFirmaPoder r61).
 *  La emisión la manda emitir(pos, vel, dt, rgb) con deuda interna
 *  (chispas ~100/s, rastro ~45/s) — el núcleo solo decide SI.
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
  const chispa = mk(120, 0.014, 0.95);
  chispa.VIDA = 0.5;                                // chispa viva y breve
  const rastro = mk(90, 0.009, 0.4);
  rastro.VIDA = 1.15;                               // rastro tenue que linger
  const grp = new THREE.Group();
  grp.add(chispa.pts);
  grp.add(rastro.pts);
  const _c = new THREE.Color();
  const naceEn = (L, px, py, pz, dx, dy, dz, rgb) => {
    const i = L.prox;
    L.prox = (L.prox + 1) % L.N;
    L.pos[i * 3] = px; L.pos[i * 3 + 1] = py; L.pos[i * 3 + 2] = pz;
    L.vel[i * 3] = dx; L.vel[i * 3 + 1] = dy; L.vel[i * 3 + 2] = dz;
    L.ages[i] = 0;
    if (rgb === 'arcoiris') {
      _c.setHSL(Math.random(), 0.95, 0.6);
      L.base[i * 3] = _c.r; L.base[i * 3 + 1] = _c.g; L.base[i * 3 + 2] = _c.b;
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
      L.vel[i * 3 + 1] -= dt * grav;                        // gravedad suave
      const f = Math.max(0, 1 - dt * freno);                // freno (disipa)
      L.vel[i * 3] *= f;
      L.vel[i * 3 + 1] *= f;
      L.vel[i * 3 + 2] *= f;
      pa[i * 3] += L.vel[i * 3] * dt;
      pa[i * 3 + 1] += L.vel[i * 3 + 1] * dt;
      pa[i * 3 + 2] += L.vel[i * 3 + 2] * dt;
      const k = Math.max(0, 1 - L.ages[i] / L.VIDA);        // apagado lineal
      ca[i * 3] = L.base[i * 3] * k;
      ca[i * 3 + 1] = L.base[i * 3 + 1] * k;
      ca[i * 3 + 2] = L.base[i * 3 + 2] * k;
    }
    if (vivo) {
      L.geo.attributes.position.needsUpdate = true;
      L.geo.attributes.color.needsUpdate = true;
    } else if (L.pts.visible) L.pts.visible = false;
  };
  let accC = 0, accR = 0;
  return {
    group: grp,
    /** Emisión de cometa: chispas DETRÁS de la bola (contra el vuelo) +
     *  rastro tenue. rgb: firma [r,g,b] — o 'arcoiris'. */
    emitir(pos, vel, dt, rgb) {
      accC += dt * 100;
      let n = Math.min(4, Math.floor(accC));
      accC -= n;
      while (n-- > 0) {
        naceEn(chispa,
          pos.x + (Math.random() - 0.5) * 0.02,
          pos.y + (Math.random() - 0.5) * 0.02,
          pos.z + (Math.random() - 0.5) * 0.02,
          -vel.x * 0.30 + (Math.random() - 0.5) * 0.18,
          -vel.y * 0.30 + (Math.random() - 0.5) * 0.18,
          -vel.z * 0.30 + (Math.random() - 0.5) * 0.18,
          rgb);
      }
      accR += dt * 45;
      let m = Math.min(2, Math.floor(accR));
      accR -= m;
      while (m-- > 0) {
        naceEn(rastro,
          pos.x + (Math.random() - 0.5) * 0.015,
          pos.y + (Math.random() - 0.5) * 0.015,
          pos.z + (Math.random() - 0.5) * 0.015,
          -vel.x * 0.10 + (Math.random() - 0.5) * 0.07,
          -vel.y * 0.10 + (Math.random() - 0.5) * 0.07,
          -vel.z * 0.10 + (Math.random() - 0.5) * 0.07,
          rgb);
      }
    },
    /** Paso por frame de las dos capas. */
    update(dt) {
      paso(chispa, dt, 0.5, 3.5);       // chispas: caen y frenan fuerte
      paso(rastro, dt, 0.12, 2.0);      // rastro: casi flota, se disipa
    },
    dispose() {
      try {
        chispa.geo.dispose(); chispa.mat.dispose();
        rastro.geo.dispose(); rastro.mat.dispose();
      } catch { /* */ }
    },
  };
}

'''

NUBE_TX = r'''/* =====================================================================
 *  r107 (v3.6.205) · NUBE DE PRISMAS — RECONSTRUIDA (el dueño: «que
 *  parezcan prismas 3d con caras brillantes o de diferentes tonos para
 *  apreciarlos en 3d, no quiero efecto planos»). El sombreado de
 *  facetas va HORNEADO en los VÉRTICES (dos luces fijas por normal +
 *  tono frío en los flancos y cálido en las tapas): cada cara de cada
 *  prisma refleja distinto aunque la sala no tenga luz — gema facetada
 *  siempre brillante, y el instanceColor arcoíris multiplica por
 *  encima. Pool fijo de 36 instancias (r106 intacto: nace/anillo/vida
 *  4,5-5,5 s/flotación/encogido).
 *  ===================================================================== */
export function createNubePrismas() {
  const N = 36, VIDA = 5.0, FADE = 0.8;
  let geo = new THREE.CylinderGeometry(0.024, 0.024, 0.06, 3);
  geo = geo.toNonIndexed();                  // caras planas: vértices propios
  {
    // SOMBREADO DE FACETAS HORNEADO (el anti-plano del dueño)
    const posA = geo.attributes.position;
    const nV = posA.count;
    const colArr = new Float32Array(nV * 3);
    const A = new THREE.Vector3(), B = new THREE.Vector3(), C = new THREE.Vector3();
    const AB = new THREE.Vector3(), AC = new THREE.Vector3(), NR = new THREE.Vector3();
    const L1 = new THREE.Vector3(0.42, 0.78, 0.46).normalize();
    const L2 = new THREE.Vector3(-0.5, 0.25, -0.65).normalize();
    for (let f = 0; f < nV; f += 3) {
      A.fromBufferAttribute(posA, f);
      B.fromBufferAttribute(posA, f + 1);
      C.fromBufferAttribute(posA, f + 2);
      AB.copy(B).sub(A);
      AC.copy(C).sub(A);
      NR.copy(AB).cross(AC).normalize();
      if (NR.lengthSq() < 0.5) NR.set(0, 1, 0);
      let brillo = 0.55 + 0.45 * Math.max(0, NR.dot(L1)) +
        0.18 * Math.max(0, NR.dot(L2));
      // tono por cara: flancos fríos, tapas cálidas (se aprecia el 3D)
      let tr, tg, tb;
      if (Math.abs(NR.y) > 0.7) { tr = 1.06; tg = 1.0; tb = 0.9; }
      else { tr = 0.88; tg = 0.98; tb = 1.1; }
      const k = Math.min(1.15, brillo);
      for (let v = 0; v < 3; v++) {
        colArr[(f + v) * 3] = tr * k;
        colArr[(f + v) * 3 + 1] = tg * k;
        colArr[(f + v) * 3 + 2] = tb * k;
      }
    }
    geo.setAttribute('color', new THREE.BufferAttribute(colArr, 3));
  }
  const mat = new THREE.MeshBasicMaterial({
    vertexColors: true, transparent: true, opacity: 0.96,
    side: THREE.DoubleSide, depthWrite: false,
  });
  const mesh = new THREE.InstancedMesh(geo, mat, N);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  mesh.frustumCulled = false;
  mesh.renderOrder = 68;
  mesh.visible = false;
  const P = [];
  const _m = new THREE.Matrix4(), _q = new THREE.Quaternion();
  const _p = new THREE.Vector3(), _s = new THREE.Vector3();
  const _ax = new THREE.Vector3(), _c = new THREE.Color();
  for (let i = 0; i < N; i++) {
    P.push({ t: -1, vida: VIDA, x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0,
      ax: 0, ay: 1, az: 0, w: 3, ang: 0, esc: 1 });
    _c.setHSL(i / N, 0.95, 0.55);
    mesh.setColorAt(i, _c);                    // instanceColor desde el build
    _m.makeScale(0, 0, 0);
    mesh.setMatrixAt(i, _m);                   // muertas: invisibles
  }
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  mesh.instanceMatrix.needsUpdate = true;
  let prox = 0;
  return {
    group: mesh,
    /** Nace la nube en p (30 prismas por defecto, anillo de instancias —
     *  dos nubes seguidas re-usan las más viejas, jamás asigna). */
    nace(p, n) {
      const cuantos = Math.min(n || 30, N);
      for (let k = 0; k < cuantos; k++) {
        const i = prox;
        const s = P[i];
        prox = (prox + 1) % N;
        s.t = 0;
        s.vida = VIDA + (Math.random() - 0.5) * 1.0;   // 4,5-5,5 s
        s.x = p.x + (Math.random() - 0.5) * 0.10;
        s.y = p.y + 0.12 + (Math.random() - 0.5) * 0.10;
        s.z = p.z + (Math.random() - 0.5) * 0.10;
        const a = Math.random() * Math.PI * 2;
        const sp = 0.22 + Math.random() * 0.5;
        s.vx = Math.cos(a) * sp;
        s.vy = 0.35 + Math.random() * 0.55;             // brotan hacia arriba
        s.vz = Math.sin(a) * sp;
        const b = Math.random() * Math.PI * 2;
        s.ax = Math.cos(b); s.ay = Math.sin(b); s.az = (Math.random() - 0.5) * 2;
        s.w = 2.2 + Math.random() * 2.6;
        s.ang = Math.random() * Math.PI * 2;
        s.esc = 0.8 + Math.random() * 0.6;
        _c.setHSL(Math.random(), 0.95, 0.55);           // «todos los colores»
        mesh.setColorAt(i, _c);
      }
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
      mesh.visible = true;
    },
    /** Paso por frame: flotar (deriva amortiguada + casi sin gravedad),
     *  girar y encogerse en el último 0,8 s hasta desaparecer. */
    update(dt) {
      let vivo = false;
      for (let i = 0; i < N; i++) {
        const s = P[i];
        if (s.t < 0) continue;
        vivo = true;
        s.t += dt;
        if (s.t >= s.vida) {
          s.t = -1;
          _m.makeScale(0, 0, 0);
          mesh.setMatrixAt(i, _m);
          continue;
        }
        const d = Math.max(0, 1 - dt * 1.5);            // freno del esparcir
        s.vx *= d; s.vz *= d;
        s.vy += (-0.06 + Math.sin(s.t * 2.1 + i * 1.7) * 0.05) * dt;  // flota
        s.x += s.vx * dt; s.y += s.vy * dt; s.z += s.vz * dt;
        s.ang += s.w * dt;
        let esc = s.esc;
        const rest = s.vida - s.t;
        if (rest < FADE) esc *= Math.max(0.001, rest / FADE);
        _p.set(s.x, s.y, s.z);
        _ax.set(s.ax, s.ay, s.az).normalize();
        _q.setFromAxisAngle(_ax, s.ang);
        _s.setScalar(esc);
        _m.compose(_p, _q, _s);
        mesh.setMatrixAt(i, _m);
      }
      if (vivo) mesh.instanceMatrix.needsUpdate = true;
      else if (mesh.visible) mesh.visible = false;
    },
    dispose() {
      try { geo.dispose(); mat.dispose(); } catch { /* */ }
    },
  };
}

'''

ONDA_TX = r'''/* =====================================================================
 *  r107 (v3.6.205) · ESFERA-ESCUDO DE LA ONDA DE CHOQUE — el encargo del
 *  dueño: «emite una onda en forma de esfera azulona semitransparente
 *  con dibujos de pentágonos en su superficie (que simulan una especie
 *  de escudo) desde la pala del jugador empujando la bola cuando este la
 *  golpea; la esfera se centra en la pala en el momento del impacto y
 *  crece empujando la bola con la propia superficie de la esfera». Textura
 *  de pentágonos PROCEDURAL (lienzo, sin assets), aditiva y translúcida;
 *  la superficie PERSIGUE a la bola (radio = distancia al centro + margen,
 *  con crecimiento propio mínimo) — la bola viaja pegada al frente de la
 *  burbuja que la empuja. Muere encogiéndose (el núcleo la corta cuando
 *  la bola toca el suelo o la pala del rival; tope de vida 1,6 s).
 *  ===================================================================== */
export function createOndaEsfera() {
  const MAXR = 1.5, VIDA = 1.6, MUERTE = 0.18, OP = 0.34;
  // — textura de pentágonos (escudo) dibujada en un lienzo —
  const cv = document.createElement('canvas');
  cv.width = 1024;
  cv.height = 512;
  const g = cv.getContext('2d');
  const penta = (x, y, r, rot) => {
    g.beginPath();
    for (let k = 0; k < 5; k++) {
      const a = rot + k * Math.PI * 2 / 5;
      const px = x + Math.cos(a) * r;
      const py = y + Math.sin(a) * r;
      if (k === 0) g.moveTo(px, py); else g.lineTo(px, py);
    }
    g.closePath();
  };
  for (let row = 0; row < 6; row++) {
    for (let col = 0; col < 12; col++) {
      const x = (col + (row % 2 ? 0.5 : 0)) * (1024 / 12);
      const y = (row + 0.5) * (512 / 6);
      const r = 30 + ((row * 7 + col * 13) % 3) * 7;
      penta(x, y, r, (row + col) * 0.7);
      g.fillStyle = 'rgba(150, 205, 255, 0.13)';
      g.fill();
      g.strokeStyle = 'rgba(212, 238, 255, 0.9)';
      g.lineWidth = 3.5;
      g.shadowColor = '#8fd2ff';
      g.shadowBlur = 10;
      g.stroke();
      g.shadowBlur = 0;
    }
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.wrapS = THREE.RepeatWrapping;
  const geo = new THREE.SphereGeometry(1, 30, 22);
  const mat = new THREE.MeshBasicMaterial({
    map: tex, transparent: true, opacity: 0,
    blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    depthWrite: false,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.renderOrder = 63;
  mesh.visible = false;
  mesh.frustumCulled = false;
  let t = -1, radio = 0.1, muriendo = -1;
  const centro = new THREE.Vector3();
  const _v = new THREE.Vector3();
  return {
    group: mesh,
    viva() { return t >= 0 && muriendo < 0; },
    /** Nace centrada en el punto del impacto (la pala en el golpeo). */
    nace(pos) {
      centro.copy(pos);
      t = 0;
      radio = 0.1;
      muriendo = -1;
      mesh.position.copy(centro);
      mesh.scale.setScalar(radio);
      mat.opacity = 0;
      mesh.visible = true;
    },
    /** Crece empujando: persigue la bola (bola = pos actual o null). */
    update(dt, bola) {
      if (t < 0) return;
      if (muriendo >= 0) {
        muriendo += dt;
        const k = Math.max(0, 1 - muriendo / MUERTE);
        mesh.scale.setScalar(Math.max(0.001, radio * k));
        mat.opacity = OP * k;
        if (muriendo >= MUERTE) { t = -1; mesh.visible = false; }
        return;
      }
      t += dt;
      if (t >= VIDA) { this.muere(); return; }
      let objetivo = radio + dt * 1.4;            // crecimiento propio mínimo
      if (bola) {
        _v.copy(bola).sub(centro);
        const d = _v.length() + 0.06;             // la superficie la alcanza
        if (d > objetivo) objetivo = d;
      }
      radio = Math.min(MAXR, objetivo);
      mesh.scale.setScalar(radio);
      mat.opacity = Math.min(OP, OP * t * 6);     // fade-in rápido
    },
    /** Muere encogiéndose rápido (el núcleo corta con golpe sonoro). */
    muere() {
      if (t < 0) return;
      muriendo = 0;
    },
    dispose() {
      try { geo.dispose(); mat.dispose(); tex.dispose(); } catch { /* */ }
    },
  };
}

'''

c07 = c07[:i1] + COMET_TX + NUBE_TX + ONDA_TX + c07[i3:]
io.open(R + 'c07_escena_sala.js', 'w', encoding='utf-8').write(c07)
print("c07: cometa (2 capas) + prismas facetados + esfera-escudo reconstruidos")

# ════════════════════════ c12 · LOS CABLES ═════════════════════════
c12 = io.open(R + 'c12_pingponggame.js', encoding='utf-8').read()
n0 = len(c12)

def edit(old, new, tag, cnt=1):
    global c12
    assert old in c12, f"c12: ancla {tag} NO encontrada"
    assert c12.count(old) == cnt, f"c12: ancla {tag} ambigua ({c12.count(old)})"
    c12 = c12.replace(old, new)
    print(f"c12: {tag} ✓")

# 1) import de la esfera
edit(
  "import { applyBallSkin, createBall, createBlobShadow, createChampDecor, createChispas, createEstelaPoder, createNubePrismas, createRoom, createTable, relayoutMesa } from './c07_escena_sala.js';",
  "import { applyBallSkin, createBall, createBlobShadow, createChampDecor, createChispas, createEstelaPoder, createNubePrismas, createOndaEsfera, createRoom, createTable, relayoutMesa } from './c07_escena_sala.js';",
  "1 import")

# 2) campo _megaActivaMia (¿la ventana la armé YO?)
edit(
  "    // r106 · ventana de PRISMA del RIVAL en duelos: mientras corre, cada\n"
  "    // golpeo MÍO cria la nube de prismas EN MI MITAD (me estorba a mí —\n"
  "    // el espejo exacto del efecto local con la IA).\n"
  "    this._dlPrismaRemotoT = 0;",
  "    // r106 · ventana de PRISMA del RIVAL en duelos: mientras corre, cada\n"
  "    // golpeo MÍO cria la nube de prismas EN MI MITAD (me estorba a mí —\n"
  "    // el espejo exacto del efecto local con la IA).\n"
  "    this._dlPrismaRemotoT = 0;\n"
  "    // r107 · ¿la ventana ACTIVA la armé YO? (false = la armó el relay\n"
  "    // del rival: SU cometa jamás se dibuja en mi pantalla — el cometa\n"
  "    // es solo del jugador que lanza el poder).\n"
  "    this._megaActivaMia = true;",
  "2 campo mia")

# 3) build de la esfera en el rig (y fuera la deuda vieja del cometa)
edit(
  "    this.nubePrisma = createNubePrismas();\n    this.rig.add(this.nubePrisma.group);\n"
  "    this._estelaAcc = 0;             // deuda de emisión (partículas/frame)",
  "    this.nubePrisma = createNubePrismas();\n    this.rig.add(this.nubePrisma.group);\n"
  "    // r107 · la ESFERA-ESCUDO de la onda de choque (pentágonos, nace en\n"
  "    // la pala al golpeo, crece empujando la bola al doble de velocidad)\n"
  "    this.ondaEsfera = createOndaEsfera();\n    this.rig.add(this.ondaEsfera.group);",
  "3 build esfera")

# 4) megaTrigger: el gatillo LOCAL arma → cometa propio
edit(
  "    if (ent.id === 'bolaloca') return this._bolalocaTrigger(ent); // FASE 160",
  "    this._megaActivaMia = true;   // r107: esta ventana la arma YO\n"
  "    if (ent.id === 'bolaloca') return this._bolalocaTrigger(ent); // FASE 160",
  "4 megaTrigger mia")

# 5) _dlTrigger (duelos locales): lanzamiento PROPIO
edit(
  "      this._dlArma(id);\n      this.net.sendDueloPower(id);       // aviso fiable al rival ('pow')",
  "      this._dlArma(id);\n      this._megaActivaMia = true;      // r107: lanzamiento PROPIO en duelos\n"
  "      this.net.sendDueloPower(id);       // aviso fiable al rival ('pow')",
  "5 dlTrigger mia")

# 6) onRemoteDueloPower: la ventana del rival NUNCA emite cometa
edit(
  "        this._dlArma(id);              // …y el trigger de la casa arma TODO\n      } else if (id === 'onda') {",
  "        this._dlArma(id);              // …y el trigger de la casa arma TODO\n"
  "        this._megaActivaMia = false;   // r107: la armó EL RIVAL — su cometa no es mío\n"
  "      } else if (id === 'onda') {",
  "6 remote no-cometa")

# 7) bloque de emisión r106 → COMETA r107 (+ paso de la esfera)
edit(
  """    // r106 · ESTELA DE PARTÍCULAS DEL PODER ACTIVO (petición del dueño):
    // mientras la ventana corre, la bola suelta chispas del color del
    // poder — la MISMA firma de la estela-línea r61 (_trailFirmaPoder:
    // para el arcoíris, la regla r34 del dueño se respeta — las chispas
    // nacen SOLO en el campo rival, como su estela). La nube de prismas
    // drena su pool aquí también (barato: sólo instancias vivas).
    if (this.estelaPoder) {
      try { this.estelaPoder.update(dt); } catch (eEPu) { /* */ }
      try { this.nubePrisma.update(dt); } catch (eNPu) { /* */ }
      const bE = this.ball;
      if (bE && !this.inHall && !frozen && !(bE.ppTransito) &&
          bE.vel && bE.vel.lengthSq() > 1.4) {
        const firmaE = this._trailFirmaPoder();
        if (firmaE) {
          this._estelaAcc += dt * 110;              // ~110 partículas/s
          let nE = Math.floor(this._estelaAcc);
          if (nE > 4) nE = 4;                       // tope por frame
          this._estelaAcc -= nE;
          const arcoE = this._megaActivaId === 'prisma';
          while (nE-- > 0) {
            this.estelaPoder.nace(
              bE.pos.x + (Math.random() - 0.5) * 0.03,
              bE.pos.y + (Math.random() - 0.5) * 0.03,
              bE.pos.z + (Math.random() - 0.5) * 0.03,
              -bE.vel.x * 0.12 + (Math.random() - 0.5) * 0.3,
              -bE.vel.y * 0.12 + (Math.random() - 0.5) * 0.3,
              -bE.vel.z * 0.12 + (Math.random() - 0.5) * 0.3,
              arcoE ? 'arcoiris' : firmaE,
            );
          }
        } else this._estelaAcc = 0;
      }
    }""",
  """    // r107 · EL COMETA DEL PODER (reconstrucción del encargo r106: «un
    // efecto más chulo de cometa, una cola de color como chispas que
    // salen detrás de la bola dejando un rastro tenue que se acaba
    // disipando»). TRES verjas del dueño, literales:
    //  · SOLO EL LANZADOR lo ve (_megaActivaMia: las ventanas que el
    //    relay remoto arma en mi cliente no emiten jamás).
    //  · SOLO ENVÍOS PROPIOS: la bola viajando HACIA EL RIVAL
    //    (vel.z < 0 — convención «mi mitad = z > centro» en ambos
    //    clientes, r84/r43); en las devoluciones del rival, nada.
    //  · SIN DUPLICAR ESTELAS: poderes con vestido propio (fénix que
    //    arde, prisma arcoíris, crono con anillos, elec con rayos,
    //    oscuridad que tinta, salva con estela warp, bolaloca) NO lo
    //    llevan — solo los que no tienen estela.
    if (this.estelaPoder) {
      try { this.estelaPoder.update(dt); } catch (eEPu) { /* */ }
      try { this.nubePrisma.update(dt); } catch (eNPu) { /* */ }
      const bE = this.ball;
      if (bE && !this.inHall && !frozen && !(bE.ppTransito) &&
          bE.vel && bE.vel.lengthSq() > 1.4 && bE.vel.z < -0.05 &&
          this._megaActivaMia && this._megaActivaRest() > 0 &&
          !R107_SIN_COMETA[this._megaActivaId]) {
        const firmaE = this._trailFirmaPoder();
        if (firmaE) {
          this.estelaPoder.emitir(bE.pos, bE.vel, dt, firmaE);
        }
      }
    }
    // r107 · LA ESFERA-ESCUDO de la onda: crece empujando la bola con su
    // superficie; MUERE cuando la bola toca el suelo (cayó fuera) o el
    // punto ya no está en rally — la pala rival la corta en su gancho.
    if (this.ondaEsfera) {
      try {
        if (this.ondaEsfera.viva()) {
          if (!this.rules || this.rules.state !== 'rally' ||
              (this.ball && this.ball.pos.y < DIMS.tableTopY - 0.35)) {
            this._ondaEsferaMuere();            // el suelo / punto muerto
          } else {
            this.ondaEsfera.update(dt, this.ball ? this.ball.pos : null);
          }
        } else {
          this.ondaEsfera.update(dt, null);     // drena el encogido final
        }
      } catch (eOEf) { /* la esfera nunca tumba el frame */ }
    }""",
  "7 cometa+esfera frame")

# 8) el gancho onda del golpe propio → ESFERA (y el ×2 dentro)
edit(
  """              if (this._ondaT > 0 && this.ball.vel && this.ball.vel.z < -0.5 &&
                  this.ball.vel.length() >= ONDA_SMASH_V) {
                try { this._ondaNace(this.ball.pos); } catch (eON33) { /* */ }
              }""",
  """              if (this._ondaT > 0 && this.ball.vel) {
                // r107 · LA ESFERA-ESCUDO (petición del dueño): CADA
                // golpeo propio en rally (ya no solo el smash) nace
                // centrado en la pala y crece empujando la bola con su
                // superficie — la bola viaja AL DOBLE de la velocidad del
                // golpe (ver _ondaEsferaNace). El SAQUE queda fuera (este
                // bloque ya exige rally).
                try { this._ondaEsferaNace(this.ball.pos, this.ball.vel); }
                catch (eON33) { /* */ }
              }""",
  "8 gancho esfera")

# 9) el bote INESPERADO de Súper Efecto (tras el bucle de golpe propio)
edit(
  """              break;   // un golpe propio por frame basta
            }
          }""",
  """              break;   // un golpe propio por frame basta
            }
          }
          // r107 · SÚPER EFECTO — EL BOTE INESPERADO (petición del dueño:
          // «que la pelota al botar en la mesa del rival genere un bote
          // inesperado y sorpresivo»): cada bote en la mesa del RIVAL
          // (mi envío ya cayó en su campo) recibe una patada lateral
          // IMPREVISIBLE + variación de profundidad y un hop ocasional —
          // la IA no puede preleerlo y el rival humano tampoco. El SAQUE
          // queda fuera (este bloque exige rally) y los cantos (edge)
          // no se patean.
          if (this._efectoT > 0) {
            for (const eE of this.events) {
              if (eE.type !== 'table' || eE.side !== 'ai' || eE.edge) continue;
              const vEf = this.ball.vel;
              vEf.x += (Math.random() - 0.5) * 2 * EFECTO_SORPRESA_X;
              vEf.z += (Math.random() - 0.5) * EFECTO_SORPRESA_Z;
              if (Math.random() < 0.3) vEf.y += EFECTO_SORPRESA_HOP;
              try { this.chispas.burst(eE.pos, TRAIL_PODER.efecto); }
              catch (eCE1) { /* */ }
              try { this.audio.playOsc(680, 180, 0.16, 'square', 0.12, 0); }
              catch (eCE2) { /* */ }
              break;             // un bote sorpresivo por frame basta
            }
          }""",
  "9 bote sorpresivo")

# 10) la esfera MUERE en la pala del rival (IA) — spec literal
edit(
  "    if (aiHit) {\n      this.ball.vel.copy(aiHit);",
  "    if (aiHit) {\n      this.ball.vel.copy(aiHit);\n"
  "      // r107 · la esfera-escudo MUERE al impactar la bola en la pala\n"
  "      // del rival (spec literal del dueño) con su golpe seco final.\n"
  "      try { if (this.ondaEsfera && this.ondaEsfera.viva()) this._ondaEsferaMuere(); }\n"
  "      catch (eOEa) { /* */ }",
  "10 muerte pala IA")

# 11) dobles: el compañero y el rival 2 también la cortan
edit(
  "        if (compHit) {\n          this.ball.vel.copy(compHit);",
  "        if (compHit) {\n          this.ball.vel.copy(compHit);\n"
  "          // r107 · el golpe del COMPAÑERO también dispersa la esfera\n"
  "          try { if (this.ondaEsfera && this.ondaEsfera.viva()) this._ondaEsferaMuere(); }\n"
  "          catch (eOEc) { /* */ }",
  "11a muerte comp")

edit(
  "        if (r2Hit) {\n          this.ball.vel.copy(r2Hit);",
  "        if (r2Hit) {\n          this.ball.vel.copy(r2Hit);\n"
  "          // r107 · la pala del rival 2 también corta la esfera (spec)\n"
  "          try { if (this.ondaEsfera && this.ondaEsfera.viva()) this._ondaEsferaMuere(); }\n"
  "          catch (eOEr2) { /* */ }",
  "11b muerte rival 2")

# 12) fin de la ventana de onda: la esfera se disipa con ella
edit(
  "    this._ondaShakeT = 0;\n    this._ondaFxVis(false);\n    if (this._megaActivaId === 'onda') this._megaActivaId = null;",
  "    this._ondaShakeT = 0;\n    this._ondaFxVis(false);\n"
  "    // r107 · la ventana cerró: la esfera se disipa (encogido suave)\n"
  "    try { if (this.ondaEsfera) this.ondaEsfera.muere(); } catch (eOEfin) { /* */ }\n"
  "    if (this._megaActivaId === 'onda') this._megaActivaId = null;",
  "12 fin ventana")

# 13) los métodos nuevos junto al viejo _ondaNace
edit(
  """    try { this.audio.playOsc(190, 62, 0.3, 'sawtooth', 0.16, 0); } catch (e) { /* */ }
    try { this.audio.playNoise(0.25, 300, 0.4, 0.1, 0, 'lowpass'); } catch (e2) { /* */ }
    if (this.renderer.xr && this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.6, 90); } catch (e3) { /* */ }
    }
  }
""",
  """    try { this.audio.playOsc(190, 62, 0.3, 'sawtooth', 0.16, 0); } catch (e) { /* */ }
    try { this.audio.playNoise(0.25, 300, 0.4, 0.1, 0, 'lowpass'); } catch (e2) { /* */ }
    if (this.renderer.xr && this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.6, 90); } catch (e3) { /* */ }
    }
  }

  /** r107 · LA ESFERA-ESCUDO DE LA ONDA DE CHOQUE (petición literal del
   *  dueño): nace centrada en la PALA en el momento del impacto y crece
   *  empujando la bola con la propia superficie de la esfera — la bola
   *  viaja AL DOBLE de la velocidad del golpe. Desaparece cuando la bola
   *  impacta en el suelo o en la pala del rival (ganchos r107). El
   *  «en pleno swing» (devolución IA floja) y el temblor del rig se
   *  conservan del anillo r33. Sustituye a _ondaNace en el gancho. */
  _ondaEsferaNace(pos, vel) {
    if (!this.ondaEsfera) {
      try {
        this.ondaEsfera = createOndaEsfera();
        this.rig.add(this.ondaEsfera.group);
      } catch (eOB2) { return; }
    }
    const vOn = this.ball.vel;
    if (vOn && vOn.lengthSq() > 0.01) vOn.multiplyScalar(2);   // AL DOBLE
    try { this.ondaEsfera.nace(pos); } catch (eON2) { /* */ }
    // «en pleno swing»: la próxima devolución de la IA sale al 75 %
    this._ondaFlojoT = ONDA_FLOJO_T;
    // temblor breve del rig (comodidad VR: 0,35 s, ±9 mm, restauración exacta)
    this._ondaShakeT = 0.35;
    if (!this._ondaRigBase && this.rig) this._ondaRigBase = this.rig.position.clone();
    // ENERGÍA GRAVE QUE CRECE hasta el impacto (sub + sierra, barrido 2 s)
    try { this.audio.playOsc(52, 118, 0.5, 'sawtooth', 0.2, 0); } catch (eOEs1) { /* */ }
    try { this.audio.playOsc(36, 82, 0.5, 'sine', 0.24, 0); } catch (eOEs2) { /* */ }
    if (this.renderer.xr && this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.7, 90); } catch (eOEs3) { /* */ }
    }
  }

  /** r107 · muerte de la esfera (suelo / pala rival / fin de ventana): la
   *  energía grave CORTA con un golpe seco — «crece hasta desaparecer con
   *  el impacto». */
  _ondaEsferaMuere() {
    try { this.ondaEsfera.muere(); } catch (eOM1) { /* */ }
    try { this.audio.playOsc(110, 40, 0.18, 'sawtooth', 0.16, 0); } catch (eOM2) { /* */ }
    try { this.audio.playNoise(0.14, 210, 0.3, 0.12, 0, 'lowpass'); } catch (eOM3) { /* */ }
  }
""",
  "13 métodos esfera")

# 14) constantes de módulo (junto a PRISMA_DUR)
edit(
  "const PRISMA_DUR = ARCANO_CFG.ventanas.prisma;      // s de ventana",
  "const PRISMA_DUR = ARCANO_CFG.ventanas.prisma;      // s de ventana\n"
  "\n"
  "// r107 · EL COMETA DEL PODER: los poderes con estela o vestido PROPIO\n"
  "// jamás lo llevan (petición del dueño: «si el superpoder ya tiene\n"
  "// estela no se le coloca otra estela nueva») — fénix ARDE (bocanadas),\n"
  "// prisma tiene su estela arcoíris, crono sus anillos de reloj, elec sus\n"
  "// rayos, oscuridad tinta la bola, salva lleva la estela warp y bolaloca\n"
  "// muda el tamaño de la bola. Los demás (mega, efecto, imán, portal,\n"
  "// clon, red, onda, ancla) visten el cometa de su color.\n"
  "const R107_SIN_COMETA = {\n"
  "  fenix: 1, prisma: 1, crono: 1, elec: 1, oscuridad: 1, salva: 1, bolaloca: 1,\n"
  "};\n"
  "// r107 · SÚPER EFECTO: el BOTE INESPERADO en la mesa del rival (patada\n"
  "// lateral imprevisible + variación de profundidad + hop ocasional).\n"
  "const EFECTO_SORPRESA_X = 1.1;    // m/s de patada lateral (±)\n"
  "const EFECTO_SORPRESA_Z = 0.5;    // m/s de variación de profundidad\n"
  "const EFECTO_SORPRESA_HOP = 0.3;  // m/s del hop ocasional (30 %)",
  "14 constantes")

io.open(R + 'c12_pingponggame.js', 'w', encoding='utf-8').write(c12)
print(f"c12: {len(c12) - n0} bytes · 14 cables r107 aplicados")
