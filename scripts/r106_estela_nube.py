#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r106 · ESTELA DE PARTÍCULAS POR PODER + NUBE DE PRISMAS DEL ARCOÍRIS.

Petición literal del dueño:
 · «siempre que el usuario lance un superpoder de pala la bola genere una
   estela de partículas pequeñas de un determinado color según el
   superpoder (para generar golpes espectaculares)».
 · «en el superpoder del arcoíris, siempre que esté activo y el rival
   golpee la bola durante el tiempo que esté activo generará un conjunto
   de prismas 3d brillantes de todos los colores que se esparcirán como
   una nube de partículas y quedarán flotando en el aire unos 5 segundos
   hasta desaparecer… pretende dificultarle la visión».

c07 recibe dos fábricas FX (patrón de la casa: pools FIJOS pre-alocados,
cero asignaciones por frame) y c12 los cables en 8 puntos.
"""
import re

R = '/home/z/my-project/src/game/core/'

# ════════════════════════════════════ c07 · LAS DOS FÁBRICAS FX ═══
c07 = open(R + 'c07_escena_sala.js').read()

ANCHOR07 = """export function createBlobShadow() {"""

FX07 = r"""/* =====================================================================
 *  r106 (v3.6.204) · ESTELA DE PARTÍCULAS DEL PODER ACTIVO — petición
 *  del dueño: «la bola genere una estela de partículas pequeñas de un
 *  determinado color según el superpoder (para generar golpes
 *  espectaculares)». Pool FIJO de 150 puntos en UN solo THREE.Points
 *  (ring buffer), cero asignaciones por frame, vida 0,55 s, aditivo.
 *  El color lo pone el NÚCLEO con la firma del poder (TRAIL_PODER — la
 *  MISMA fuente de la estela-línea r61 vía _trailFirmaPoder); para el
 *  arcoíris (prisma) cada partícula nace con su PROPIO matiz HSL.
 *  ===================================================================== */
export function createEstelaPoder() {
  const N = 150, VIDA = 0.55;
  const pos = new Float32Array(N * 3);
  const vel = new Float32Array(N * 3);
  const col = new Float32Array(N * 3);   // color VIVO (base × vida)
  const base = new Float32Array(N * 3);  // color de nacimiento
  const ages = new Float32Array(N).fill(VIDA + 1);   // nacidas muertas
  for (let i = 0; i < N; i++) pos[i * 3 + 1] = -10;  // fuera de vista
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const mat = new THREE.PointsMaterial({
    size: 0.016, vertexColors: true, transparent: true, opacity: 0.95,
    blending: THREE.AdditiveBlending, depthWrite: false,
  });
  const pts = new THREE.Points(geo, mat);
  pts.visible = false;
  pts.frustumCulled = false;
  pts.renderOrder = 67;
  let prox = 0;
  const _c = new THREE.Color();
  return {
    group: pts,
    /** Nace una partícula en (px,py,pz) con deriva (dx,dy,dz).
     *  rgb: [r,g,b] de la firma del poder — o 'arcoiris' para prisma. */
    nace(px, py, pz, dx, dy, dz, rgb) {
      const i = prox;
      prox = (prox + 1) % N;
      pos[i * 3] = px; pos[i * 3 + 1] = py; pos[i * 3 + 2] = pz;
      vel[i * 3] = dx; vel[i * 3 + 1] = dy; vel[i * 3 + 2] = dz;
      ages[i] = 0;
      if (rgb === 'arcoiris') {
        _c.setHSL(Math.random(), 0.95, 0.6);
        base[i * 3] = _c.r; base[i * 3 + 1] = _c.g; base[i * 3 + 2] = _c.b;
      } else {
        base[i * 3] = rgb[0]; base[i * 3 + 1] = rgb[1]; base[i * 3 + 2] = rgb[2];
      }
      col[i * 3] = base[i * 3];
      col[i * 3 + 1] = base[i * 3 + 1];
      col[i * 3 + 2] = base[i * 3 + 2];
      pts.visible = true;
      geo.attributes.position.needsUpdate = true;
      geo.attributes.color.needsUpdate = true;
    },
    /** Paso por frame: gravedad suave + freno + apagado (sólo vivas). */
    update(dt) {
      let vivo = false;
      const pa = geo.attributes.position.array;
      const ca = geo.attributes.color.array;
      for (let i = 0; i < N; i++) {
        if (ages[i] >= VIDA) continue;
        vivo = true;
        ages[i] += dt;
        if (ages[i] >= VIDA) { pa[i * 3 + 1] = -10; continue; }
        vel[i * 3 + 1] -= dt * 0.7;                       // gravedad suave
        vel[i * 3] *= Math.max(0, 1 - dt * 1.6);          // freno
        vel[i * 3 + 2] *= Math.max(0, 1 - dt * 1.6);
        pa[i * 3] += vel[i * 3] * dt;
        pa[i * 3 + 1] += vel[i * 3 + 1] * dt;
        pa[i * 3 + 2] += vel[i * 3 + 2] * dt;
        const k = Math.max(0, 1 - ages[i] / VIDA);        // apagado lineal
        ca[i * 3] = base[i * 3] * k;
        ca[i * 3 + 1] = base[i * 3 + 1] * k;
        ca[i * 3 + 2] = base[i * 3 + 2] * k;
      }
      if (vivo) {
        geo.attributes.position.needsUpdate = true;
        geo.attributes.color.needsUpdate = true;
      } else if (pts.visible) pts.visible = false;
    },
    dispose() {
      try { geo.dispose(); mat.dispose(); } catch { /* */ }
    },
  };
}

/* =====================================================================
 *  r106 (v3.6.204) · NUBE DE PRISMAS DEL ARCOÍRIS — petición literal del
 *  dueño: «un conjunto de prismas 3d brillantes de todos los colores que
 *  se esparcirán como una nube de partículas y quedarán flotando en el
 *  aire unos 5 segundos hasta desaparecer… pretende dificultarle la
 *  visión». InstancedMesh de prismas TRIANGULARES (cilindro de 3 lados)
 *  con instanceColor arcoíris, N fija (36), vida ~5 s (±0,5), deriva
 *  amortiguada (flotan), giro vivo por instancia y encogido al morir.
 *  Cero asignaciones por frame (matrices y vectores re-usados).
 *  ===================================================================== */
export function createNubePrismas() {
  const N = 36, VIDA = 5.0, FADE = 0.8;
  const geo = new THREE.CylinderGeometry(0.024, 0.024, 0.06, 3);
  const mat = new THREE.MeshBasicMaterial({
    transparent: true, opacity: 0.95, side: THREE.DoubleSide,
    depthWrite: false,
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

"""

assert ANCHOR07 in c07, "c07: ancla createBlobShadow no encontrada"
c07 = c07.replace(ANCHOR07, FX07 + ANCHOR07, 1)
open(R + 'c07_escena_sala.js', 'w').write(c07)
print("c07: createEstelaPoder + createNubePrismas añadidas")

# ════════════════════════════════════ c12 · LOS CABLES ═════════════
c12 = open(R + 'c12_pingponggame.js').read()
n0 = len(c12)

def edit(old, new, tag, cnt=1):
    global c12
    assert old in c12, f"c12: ancla {tag} NO encontrada"
    assert c12.count(old) == cnt, f"c12: ancla {tag} ambigua ({c12.count(old)} apariciones)"
    c12 = c12.replace(old, new)
    print(f"c12: {tag} ✓")

# 1) import de las fábricas
edit(
  "import { applyBallSkin, createBall, createBlobShadow, createChampDecor, createChispas, createRoom, createTable, relayoutMesa } from './c07_escena_sala.js';",
  "import { applyBallSkin, createBall, createBlobShadow, createChampDecor, createChispas, createEstelaPoder, createNubePrismas, createRoom, createTable, relayoutMesa } from './c07_escena_sala.js';",
  "1 import")

# 2) campo del espejo remoto (junto a _dlRemotoT)
edit(
  "    this._dlRemotoT = 0;              // aviso del poder del rival (solo UX)",
  "    this._dlRemotoT = 0;              // aviso del poder del rival (solo UX)\n"
  "    // r106 · ventana de PRISMA del RIVAL en duelos: mientras corre, cada\n"
  "    // golpeo MÍO cria la nube de prismas EN MI MITAD (me estorba a mí —\n"
  "    // el espejo exacto del efecto local con la IA).\n"
  "    this._dlPrismaRemotoT = 0;",
  "2 campo remoto")

# 3) construcción de los pools (junto a las chispas)
edit(
  "    this.chispas = createChispas();\n    this.rig.add(this.chispas.group);",
  "    this.chispas = createChispas();\n    this.rig.add(this.chispas.group);\n"
  "    // r106 · FX DE PODERES: estela de partículas del poder activo y\n"
  "    // nube de prismas del arcoíris (ambas en el espacio del rig/mesa,\n"
  "    // pools fijos de c07 — cero asignaciones por frame).\n"
  "    this.estelaPoder = createEstelaPoder();\n    this.rig.add(this.estelaPoder.group);\n"
  "    this.nubePrisma = createNubePrismas();\n    this.rig.add(this.nubePrisma.group);\n"
  "    this._estelaAcc = 0;             // deuda de emisión (partículas/frame)",
  "3 build pools")

# 4) reset de duelos: la ventana remota muere con la sesión
edit(
  "    this._dlRemotoT = 0;\n",
  "    this._dlRemotoT = 0;\n    this._dlPrismaRemotoT = 0;   // r106 · la nube del rival muere con la sesión\n",
  "4 reset dl", 1)

# 5) _dlUpdate: decremento de la ventana remota
edit(
  "    if (this._dlRemotoT > 0) this._dlRemotoT -= dt;",
  "    if (this._dlRemotoT > 0) this._dlRemotoT -= dt;\n"
  "    if (this._dlPrismaRemotoT > 0) this._dlPrismaRemotoT -= dt;   // r106",
  "5 tick remoto")

# 6) onRemoteDueloPower: armar la ventana de prisma del rival
edit(
  "    this._dlRemotoT = 12;\n    try {\n      this.rules.message = T('dl_' + id) + ' · ' + T('dl_rival');",
  "    // r106 · LA NUBE DEL ARCOÍRIS VIVE EN MI GOLPEO: el rival lanzó\n"
  "    // prisma — durante SU ventana, cada golpeo MÍO cria la nube de\n"
  "    // prismas en MI mitad, delante de mí (su efecto: dificultarme la\n"
  "    // visión — el espejo del efecto local con la IA). El ANCLA propia\n"
  "    // ya devolvió arriba: si bloqueó, nunca llego aquí.\n"
  "    if (id === 'prisma') this._dlPrismaRemotoT = DL_DUR.prisma || 10;\n"
  "    this._dlRemotoT = 12;\n    try {\n      this.rules.message = T('dl_' + id) + ' · ' + T('dl_rival');",
  "6 armar remoto")

# 7) emisión por frame + drenaje de pools (junto a chispas.update)
edit(
  """    // r21 · chispas de bote: paso de física visual (barato, pool fijo)
    if (this.chispas) {
      try { this.chispas.update(dt); } catch { /* */ }
    }""",
  """    // r21 · chispas de bote: paso de física visual (barato, pool fijo)
    if (this.chispas) {
      try { this.chispas.update(dt); } catch { /* */ }
    }
    // r106 · ESTELA DE PARTÍCULAS DEL PODER ACTIVO (petición del dueño):
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
  "7 emisión")

# 8) golpe de la IA: nube de prismas (local y rival 1 de dobles)
edit(
  """      if (this._prismaT > 0 && this.rules.state === 'rally') {
        if (Math.random() < PRISMA_OUT_P) {
          try { this._oscuridadFalla(this.ball.pos); } catch (ePrF) { /* */ }
        }
      }""",
  """      if (this._prismaT > 0 && this.rules.state === 'rally') {
        // r106 · LA NUBE DE PRISMAS (petición literal del dueño): cada
        // golpeo del rival con el arcoíris activo esparce 30 prismas 3d
        // brillantes de todos los colores en SU punto de golpeo — nube
        // que flota ~5 s (vida 4,5-5,5 s) y le estorba la visión. Local
        // es espectáculo ante la IA; en duelos el espejo remoto la cria
        // en la pantalla del propio rival (ventana _dlPrismaRemotoT).
        try { this.nubePrisma.nace(this.ball.pos); } catch (ePNb1) { /* */ }
        try { this.audio.playOsc(900, 1900, 0.22, 'sine', 0.07, 0); } catch (ePNs1) { /* */ }
        if (Math.random() < PRISMA_OUT_P) {
          try { this._oscuridadFalla(this.ball.pos); } catch (ePrF) { /* */ }
        }
      }""",
  "8 nube IA")

# 9) dobles: el rival 2 también cría la nube
edit(
  """          // r33 · PRISMA y ONDA también alcanzan al rival 2 (dobles)
          if (this._prismaT > 0 && this.rules.state === 'rally') {
            if (Math.random() < PRISMA_OUT_P) {
              try { this._oscuridadFalla(this.ball.pos); } catch (ePrF2) { /* */ }
            }
          }""",
  """          // r33 · PRISMA y ONDA también alcanzan al rival 2 (dobles)
          if (this._prismaT > 0 && this.rules.state === 'rally') {
            // r106 · la nube también nace en el golpeo del rival 2
            try { this.nubePrisma.nace(this.ball.pos); } catch (ePNb2) { /* */ }
            try { this.audio.playOsc(900, 1900, 0.22, 'sine', 0.07, 0); } catch (ePNs2) { /* */ }
            if (Math.random() < PRISMA_OUT_P) {
              try { this._oscuridadFalla(this.ball.pos); } catch (ePrF2) { /* */ }
            }
          }""",
  "9 nube rival 2")

# 10) espejo online: MI golpeo con la ventana del prisma del rival viva
edit(
  """              if (this._prismaT > 0) {
                try {
                  this._prismaGuiaNace(this.ball.pos, this.ball.vel);
                } catch (ePG33) { /* */ }
              }""",
  """              if (this._prismaT > 0) {
                try {
                  this._prismaGuiaNace(this.ball.pos, this.ball.vel);
                } catch (ePG33) { /* */ }
              }
              // r106 · ESPEJO ONLINE DEL ARCOÍRIS: el RIVAL lanzó prisma
              // (_dlPrismaRemotoT corriendo) y este golpeo es MÍO — la
              // nube de prismas nace AQUÍ, en MI pantalla y MI mitad:
              // su efecto es dificultarme la visión (petición del dueño).
              if (this._dlPrismaRemotoT > 0) {
                try { this.nubePrisma.nace(this.ball.pos); } catch (ePN33) { /* */ }
                try { this.audio.playOsc(900, 1900, 0.22, 'sine', 0.07, 0); } catch (ePNs33) { /* */ }
              }""",
  "10 espejo online")

open(R + 'c12_pingponggame.js', 'w').write(c12)
print(f"c12: {len(c12) - n0} bytes añadidos · 10 cables aplicados")
