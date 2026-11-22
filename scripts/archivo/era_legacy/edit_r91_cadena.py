#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""edit_r91_cadena.py — r91 · CADENA CINEMÁTICA del rival.
c06: helpers exportados (mjQuintic/mjQuinticVel/solveArmIK/CADENA_GOLPE/
adivinaKind) + plan de golpe en OpponentAI (planCadena/_reanclaCadena/
cadenaContacto/updateCadena) + anclaje en predicción/impacto/mishit.
c12: rama de pose por fases + brazo visible (hombro→codo→muñeca) + IK.
Cada edición con aserción de unicidad — aborta si el ancla no es exacta."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')

def editar(ruta, viejo, nuevo, etiqueta):
    p = RAIZ / ruta
    t = p.read_text(encoding='utf-8')
    n = t.count(viejo)
    if n != 1:
        sys.exit(f'ABORTA [{etiqueta}]: {n} apariciones del ancla en {ruta}')
    p.write_text(t.replace(viejo, nuevo), encoding='utf-8')
    print(f'  ✓ {etiqueta}')

# ============================ c06 ============================
C06 = 'src/game/core/c06_logros_stats_ia_rival.js'

HELPERS = '''/* =====================================================================
 *  r91 · CADENA CINEMÁTICA DEL RIVAL (informe del dueño: el movimiento de
 *  la pala «no es creíble… muy robótico, se posiciona de manera previsible
 *  y da un empujoncito»). Investigación aplicada (Bańkosz & Winiarski 2025
 *  J Sports Sci Med 24:311 · Bańkosz 2018 PMC5950751 · Malagoli Lanzoni
 *  2021 Appl Sci 11:5178 · Wong 2020 Appl Sci 10:5203 · Flash & Hogan
 *  1985 J Neurosci 5:1688):
 *   · La pala es el EXTREMO de un plan de golpe con fases humanas:
 *     reacción (190-300 ms) → carga (backswing, altura mínima de pala AQUÍ
 *     — medido en 550 Hz) → golpeo (pico de velocidad sincronizado a la
 *     LLEGADA de la bola) → acompañamiento (la pala sigue subiendo tras el
 *     contacto) → recuperación. Nada de teletransportes ni empujones.
 *   · Trayectorias de MÍNIMO JERK (quíntico de Hermite con velocidades en
 *     los extremos) y correcciones por EMPALME con continuidad de
 *     velocidad — el modelo neurocientífico real del brazo humano.
 *   · Variabilidad funcional por golpe (±12 % en amplitudes, codo con polo
 *     anatómico que cae en drive y sube en revés): el rival nunca repite
 *     pose idéntica, como los jugadores reales del estudio de 2025.
 *   · La FÍSICA del golpe (solver, árbitro, efectos) NO cambia: la cadena
 *     hace VISIBLE y SINCRONIZADO el golpe que ya existía.
 * ===================================================================== */

/* amplitudes por golpe (m) — dbs/hbs: carga detrás/abajo del contacto ·
 * dft/hft: acompañamiento delante/arriba · vPeakMul: velocidad visual de
 * pala × velocidad de salida de la bola */
export const CADENA_GOLPE = {
  drive:   { dbs: 0.24, hbs: 0.10, dft: 0.30, hft: 0.16, vPeakMul: 0.80 },
  smash:   { dbs: 0.28, hbs: 0.14, dft: 0.36, hft: 0.10, vPeakMul: 0.95 },
  push:    { dbs: 0.14, hbs: 0.03, dft: 0.18, hft: 0.04, vPeakMul: 0.60 },
  dejada:  { dbs: 0.16, hbs: 0.05, dft: 0.20, hft: 0.06, vPeakMul: 0.55 },
  bloqueo: { dbs: 0.09, hbs: 0.02, dft: 0.10, hft: 0.03, vPeakMul: 0.45 },
  mala:    { dbs: 0.07, hbs: 0.02, dft: 0.10, hft: 0.02, vPeakMul: 0.35 },
};

/* r91 · quíntico de Hermite con velocidades en los extremos (v0=v1=0 ⇒
 * MÍNIMO JERK exacto — Flash & Hogan 1985). Generador de TODAS las
 * trayectorias del brazo: acelera suave, pico en el punto planificado,
 * frena suave. */
export function mjQuintic(u, p0, v0, p1, v1, T, out) {
  u = THREE.MathUtils.clamp(u, 0, 1);
  const u2 = u * u, u3 = u2 * u, u4 = u3 * u, u5 = u4 * u;
  const h0 = 10 * u3 - 15 * u4 + 6 * u5;
  const h10 = u - 6 * u3 + 8 * u4 - 3 * u5;
  const h11 = -4 * u3 + 7 * u4 - 3 * u5;
  out.set(
    p0.x + (p1.x - p0.x) * h0 + T * (v0.x * h10 + v1.x * h11),
    p0.y + (p1.y - p0.y) * h0 + T * (v0.y * h10 + v1.y * h11),
    p0.z + (p1.z - p0.z) * h0 + T * (v0.z * h10 + v1.z * h11));
  return out;
}

/* derivada del quíntico (velocidad exacta de la trayectoria) */
export function mjQuinticVel(u, p0, v0, p1, v1, T, out) {
  u = THREE.MathUtils.clamp(u, 0, 1);
  const u2 = u * u, u3 = u2 * u, u4 = u3 * u;
  const d0 = (30 * u2 - 60 * u3 + 30 * u4) / T;
  const d10 = 1 - 18 * u2 + 32 * u3 - 15 * u4;
  const d11 = -12 * u2 + 28 * u3 - 15 * u4;
  out.set(
    (p1.x - p0.x) * d0 + v0.x * d10 + v1.x * d11,
    (p1.y - p0.y) * d0 + v0.y * d10 + v1.y * d11,
    (p1.z - p0.z) * d0 + v0.z * d10 + v1.z * d11);
  return out;
}

/* r91 · IK ANALÍTICA de 2 huesos (ley de cosenos) con polo anatómico del
 * codo: el codo CAE en el drive y sube en el revés, como un brazo real
 * (rango humano 25-145°). Objetivo imposible ⇒ brazo estirado al 94 % del
 * alcance — nunca NaN, nunca desarticulado. Devuelve { dist, flex }. */
export function solveArmIK(S, W, L1, L2, pole, outE) {
  const dx = W.x - S.x, dy = W.y - S.y, dz = W.z - S.z;
  const raw = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-6;
  const dist = THREE.MathUtils.clamp(raw, 0.30, 0.94 * (L1 + L2));
  const nx = dx / raw, ny = dy / raw, nz = dz / raw;
  const a1 = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist);
  const h = Math.sqrt(Math.max(L1 * L1 - a1 * a1, 1e-6));
  const dp = pole.x * nx + pole.y * ny + pole.z * nz;
  let px = pole.x - nx * dp, py = pole.y - ny * dp, pz = pole.z - nz * dp;
  const pl = Math.sqrt(px * px + py * py + pz * pz) || 1e-6;
  px /= pl; py /= pl; pz /= pl;
  outE.set(S.x + nx * a1 + px * h, S.y + ny * a1 + py * h, S.z + nz * a1 + pz * h);
  const cosE = THREE.MathUtils.clamp((L1 * L1 + L2 * L2 - dist * dist) / (2 * L1 * L2), -1, 1);
  return { dist, flex: 180 - Math.acos(cosE) * 180 / Math.PI };
}

/* r91 · adivinanza temprana del golpe (para la CARGA visual, antes de que
 * la bola llegue): el golpe REAL lo decide el cerebro en el contacto de
 * siempre — esto solo elige la firma del backswing. */
export function adivinaKind(ball, pt) {
  if (pt.y > 1.15) return 'smash';                  // bola alta: remate probable
  if (ball.vel.length() > 6.5) return 'bloqueo';    // bola rápida: bloqueo
  if (pt.y < 0.75) return 'push';                   // bola baja: push
  return 'drive';
}

/* rascadores de la cadena (cero allocs por frame) */
const _cadA = new THREE.Vector3();
const _cadB = new THREE.Vector3();
const _cadC = new THREE.Vector3();
const _cadD = new THREE.Vector3();
const _cadV = new THREE.Vector3();

export class OpponentAI {'''

editar(C06, 'export class OpponentAI {', HELPERS, 'c06 helpers + CADENA_GOLPE')

editar(C06,
  "    this.celebT = 0;   // celebración en curso (segundos que quedan)\n  }",
  "    this.celebT = 0;   // celebración en curso (segundos que quedan)\n"
  "    // r91 · CADENA CINEMÁTICA: plan de golpe vivo (fases reacción→carga→\n"
  "    // golpeo→acompañamiento→recuperación) + tiempo de vuelo predicho\n"
  "    this.chain = null;\n"
  "    this.predictT = 0;\n  }",
  'c06 constructor chain fields')

editar(C06,
  "  reset() {\n    this.pos.copy(this.home);\n    this.vel.set(0, 0, 0);\n    this.predictValid = false;\n    this.hitCooldown = 0;\n    this._ppPortalVisto = false;   // v3.6.42: el flanco del portal a limpio\n  }",
  "  reset() {\n    this.pos.copy(this.home);\n    this.vel.set(0, 0, 0);\n    this.predictValid = false;\n    this.hitCooldown = 0;\n    this._ppPortalVisto = false;   // v3.6.42: el flanco del portal a limpio\n    this.chain = null;          // r91: sin plan de golpe colgado\n    this.predictT = 0;\n  }",
  'c06 reset chain')

editar(C06,
  "    if (this.swing) {\n      this.swing.t += dt;\n      if (this.swing.t > this.swing.dur) this.swing = null;\n    }",
  "    if (this.swing) {\n      this.swing.t += dt;\n      if (this.swing.t > this.swing.dur) this.swing = null;\n    }\n"
  "    // r91 · el plan de golpe avanza (fases, re-anclaje con la predicción)\n    this.updateCadena(dt);",
  'c06 update() wiring')

editar(C06,
  "            const dxf = (strike.point.x - this.pos.x) * sign;\n            this.fhSide = Math.abs(dxf) > 0.05 ? (dxf > 0 ? 1 : -1) : (Math.random() < 0.55 ? 1 : -1);",
  "            const dxf = (strike.point.x - this.pos.x) * sign;\n            this.fhSide = Math.abs(dxf) > 0.05 ? (dxf > 0 ? 1 : -1) : (Math.random() < 0.55 ? 1 : -1);\n"
  "            // r91 · tiempo de vuelo a la bola (ancla del pico del golpeo)\n            this.predictT = strike.t;",
  'c06 predictT nueva bola')

editar(C06,
  "            // refinamiento de la MISMA bola: suavizar, sin saltos\n            this.predict.lerp(strike.point, 0.45);",
  "            // refinamiento de la MISMA bola: suavizar, sin saltos\n            this.predict.lerp(strike.point, 0.45);\n"
  "            this.predictT += (strike.t - this.predictT) * 0.45;   // r91",
  'c06 predictT refinamiento')

editar(C06,
  "          this.predictValid = true;\n        } else {",
  "          this.predictValid = true;\n"
  "          // r91 · CADENA: el plan de golpe nace con la PRIMERA predicción\n"
  "          // válida de la bola (reacción humana ANTES de que llegue) y se\n"
  "          // re-ancla en cada refinamiento; el impacto real lo afina.\n"
  "          if (!this.chain && this.predictT < 1.15) {\n"
  "            this.planCadena(this.predict, this.predictT,\n"
  "              adivinaKind(ball, strike.point), this.fhSide);\n"
  "          }\n        } else {",
  'c06 plan start')

editar(C06,
  "      return this.mishit(ball, toca);   // r93: el swing también toca la piel",
  "      // r91 · el golpe torpe TAMBIÉN se ve por el brazo (contacto sincronizado)\n"
  "      const _mv = this.mishit(ball, toca);\n"
  "      this.cadenaContacto(cx, cy, cz, _mv);\n"
  "      return _mv;   // r93: el swing también toca la piel",
  'c06 mishit cadena')

editar(C06,
  "    if (ball.ppIman) ball.ppIman.dv = 0;   // v3.6.37: Δv del imán a cero\n\n    // swing visual: follow-through del golpe en la dirección del tiro.",
  "    if (ball.ppIman) ball.ppIman.dv = 0;   // v3.6.37: Δv del imán a cero\n\n"
  "    // r91 · CADENA: el impacto REAL afina el plan (la pala llega al punto\n"
  "    // de barrido EXACTO con el pico de velocidad sincronizado a la salida\n"
  "    // de la bola — el empujón invisible se convierte en golpe visible).\n"
  "    this.cadenaContacto(cx, cy, cz, v);\n\n"
  "    // swing visual: follow-through del golpe en la dirección del tiro.",
  'c06 cadenaContacto golpe limpio')

editar(C06,
  "    this.swing = {\n      t: 0,\n      dur: 0.3,",
  "    // r91 · con la cadena activa el STROKE COMPLETO ya se dibuja (carga→\n"
  "    // golpeo→acompañamiento): el swing de emergencia solo nace si el plan\n"
  "    // no llegó a tiempo (bola sin predicción válida).\n"
  "    if (!this.chain || this.chain.phase === 'follow' ||\n"
  "        this.chain.phase === 'recover') this.swing = {\n      t: 0,\n      dur: 0.3,",
  'c06 guard swing emergencia')

METODOS = '''  setConfig(cfg) { this.cfg = cfg; }

  /* ============ r91 · MÉTODOS DE LA CADENA CINEMÁTICA ============ */

  /** roll de muñeca por efecto, ligado al kind (la firma r88: topspin
   *  cierra, cortada abre); cadenaContacto lo refresca con el REAL. */
  _rollCadena(kind) {
    const r = kind === 'smash' ? 0.30 : kind === 'push' ? -0.22 :
      kind === 'dejada' ? -0.16 : kind === 'bloqueo' ? 0.10 :
      kind === 'mala' ? (Math.random() - 0.5) * 0.4 : 0.20;
    return r + (Math.random() - 0.5) * 0.08;
  }

  /** r91 · PLAN del golpe (nace con la primera predicción válida): fases
   *  reacción→carga→golpeo (pico EN tBall)→acompañamiento→recuperación,
   *  amplitudes de CADENA_GOLPE con variabilidad funcional ±12 %. */
  planCadena(contact, tBall, kind, fh) {
    const G = CADENA_GOLPE[kind] || CADENA_GOLPE.drive;
    const jit = () => 0.88 + Math.random() * 0.24;
    // estimación de salida (el impacto real la refina): hacia el campo del
    // jugador con sesgo lateral aleatorio
    const tz = DIMS.tableCenterZ - this.sign * DIMS.tableHalfLength * 0.7;
    _cadD.set((Math.random() - 0.5) * 0.6 - contact.x,
      DIMS.tableTopY + 0.30 - contact.y, tz - contact.z).normalize();
    const vPeak = 6.5 * G.vPeakMul * (0.9 + Math.random() * 0.2);
    const esc = (this.chain && this.chain.flat) ? 0.5 : 1;   // calabaza: carga corta
    const T_react = THREE.MathUtils.clamp(tBall * 0.30, 0.12, 0.30);
    const T_back = THREE.MathUtils.clamp((tBall - T_react) * 0.45, 0.10, 0.24);
    let T_strike = tBall - T_react - T_back;
    if (T_strike < 0.07) {          // bola rápida: comprime reacción y carga
      T_back = Math.max(0.06, T_back - (0.07 - T_strike));
      T_strike = Math.max(0.07, tBall - T_react - T_back);
      if (T_react + T_back + T_strike > tBall)
        T_react = Math.max(0.04, tBall - T_back - T_strike);
    }
    const cur = this.chain ? this.chain.cur.clone() : this.pos.clone();
    const vel = this.chain ? this.chain.vel.clone() : new THREE.Vector3();
    const B = _cadA.copy(contact).addScaledVector(_cadD, -G.dbs * jit() * esc);
    B.y = Math.max(0.5, contact.y - G.hbs * jit() * esc);
    const F = _cadB.copy(contact).addScaledVector(_cadD, G.dft * jit());
    F.y = Math.max(0.5, contact.y + G.hft * jit());
    this.chain = {
      phase: 'react', t: 0, u: 0, kind, fh, flat: !!(this.chain && this.chain.flat),
      contact: contact.clone(), tBall,
      dir: _cadD.clone(), vdir: _cadD.clone(), roll: this._rollCadena(kind),
      cur, vel, segIdx: 0,
      segs: [
        { phase: 'react', T: T_react, p0: cur.clone(), v0: vel.clone(),
          p1: cur.clone().lerp(B, 0.25), v1: new THREE.Vector3() },
        { phase: 'back', T: T_back, p0: cur.clone(), v0: new THREE.Vector3(),
          p1: B.clone(), v1: new THREE.Vector3() },
        { phase: 'strike', T: T_strike, p0: B.clone(), v0: new THREE.Vector3(),
          p1: contact.clone(), v1: _cadD.clone().multiplyScalar(vPeak) },
        { phase: 'follow', T: 0.16 + Math.random() * 0.06,
          p0: contact.clone(), v0: _cadD.clone().multiplyScalar(vPeak),
          p1: F.clone(), v1: _cadD.clone().multiplyScalar(vPeak * 0.25) },
        { phase: 'recover', T: 0.30 + Math.random() * 0.10, p0: F.clone(),
          v0: _cadD.clone().multiplyScalar(vPeak * 0.25), p1: this.pos.clone(),
          v1: new THREE.Vector3() },
      ],
    };
    // continuidad exacta: cada segmento parte del extremo del anterior
    const sgs = this.chain.segs;
    sgs[0].p0 = cur; sgs[0].v0 = vel;
    for (let i = 1; i < sgs.length; i++) { sgs[i].p0 = sgs[i - 1].p1; sgs[i].v0 = sgs[i - 1].v1; }
  }

  /** r91 · RE-ANCLAJE con la predicción refinada: el plan restante se
   *  reconstruye desde el estado ACTUAL (cur/vel) — empalme con continuidad
   *  de velocidad, el submovimiento del modelo humano. */
  _reanclaCadena(newContact, newT) {
    const ch = this.chain;
    if (!ch) return;
    const G = CADENA_GOLPE[ch.kind] || CADENA_GOLPE.drive;
    const tRem = Math.max(0.10, newT);
    const T_back = THREE.MathUtils.clamp(tRem * 0.45, 0.05, 0.16);
    const T_strike = Math.max(0.05, tRem - T_back);
    const vPeak = 6.5 * G.vPeakMul;
    const B = _cadA.copy(newContact).addScaledVector(_cadD.copy(ch.dir), -G.dbs * 0.8);
    B.y = Math.max(0.5, newContact.y - G.hbs * 0.8);
    const F = _cadB.copy(newContact).addScaledVector(_cadD, G.dft);
    F.y = Math.max(0.5, newContact.y + G.hft);
    ch.contact.copy(newContact);
    ch.tBall = newT;
    ch.segs = [
      { phase: 'back', T: T_back, p0: ch.cur.clone(), v0: ch.vel.clone(),
        p1: B.clone(), v1: new THREE.Vector3() },
      { phase: 'strike', T: T_strike, p0: B.clone(), v0: new THREE.Vector3(),
        p1: newContact.clone(), v1: _cadD.clone().multiplyScalar(vPeak) },
      { phase: 'follow', T: 0.15 + Math.random() * 0.06, p0: newContact.clone(),
        v0: _cadD.clone().multiplyScalar(vPeak), p1: F.clone(),
        v1: _cadD.clone().multiplyScalar(vPeak * 0.25) },
      { phase: 'recover', T: 0.30 + Math.random() * 0.10, p0: F.clone(),
        v0: _cadD.clone().multiplyScalar(vPeak * 0.25), p1: this.pos.clone(),
        v1: new THREE.Vector3() },
    ];
    const sgs = ch.segs;
    for (let i = 1; i < sgs.length; i++) { sgs[i].p0 = sgs[i - 1].p1; sgs[i].v0 = sgs[i - 1].v1; }
    ch.t = 0; ch.segIdx = 0; ch.phase = 'back';
  }

  /** r91 · IMPACTO REAL: en el frame del golpe (barrido de siempre) el plan
   *  se afina al punto EXACTO del contacto con el pico de velocidad alineado
   *  a la salida real de la bola — el golpe visible ES el golpe físico. */
  cadenaContacto(cx, cy, cz, v) {
    const ch = this.chain;
    if (!ch || ch.phase === 'follow' || ch.phase === 'recover') return;
    const G = CADENA_GOLPE[ch.kind] || CADENA_GOLPE.drive;
    const vP = _cadV.copy(v).multiplyScalar(G.vPeakMul);
    if (vP.lengthSq() < 0.25) vP.setLength(3.0);
    _cadD.copy(vP).normalize();
    const pC = _cadA.set(cx, cy, cz);
    const d = ch.cur.distanceTo(pC);
    const T = THREE.MathUtils.clamp(d / Math.max(3, vP.length()), 0.03, 0.09);
    const F = _cadB.copy(pC).addScaledVector(_cadD, G.dft);
    F.y = Math.max(0.5, pC.y + G.hft);
    ch.contact.copy(pC);
    ch.dir.copy(_cadD);
    ch.vdir.copy(v).normalize();
    ch.roll = this._rollCadena(ch.kind);
    ch.segs = [
      { phase: 'strike', T, p0: ch.cur.clone(), v0: ch.vel.clone(),
        p1: pC.clone(), v1: vP.clone() },
      { phase: 'follow', T: 0.15 + Math.random() * 0.06, p0: pC.clone(),
        v0: vP.clone(), p1: F.clone(), v1: vP.clone().multiplyScalar(0.25) },
      { phase: 'recover', T: 0.30 + Math.random() * 0.10, p0: F.clone(),
        v0: vP.clone().multiplyScalar(0.25), p1: this.pos.clone(),
        v1: new THREE.Vector3() },
    ];
    const sgs = ch.segs;
    for (let i = 1; i < sgs.length; i++) { sgs[i].p0 = sgs[i - 1].p1; sgs[i].v0 = sgs[i - 1].v1; }
    ch.t = 0; ch.segIdx = 0; ch.phase = 'strike';
  }

  /** r91 · frame de la cadena: fase activa, cur/vel por quíntico, re-anclaje
   *  con la predicción refinada, recuperación viva sobre el cuerpo y guard
   *  anti-NaN (una cifra rara no tumba la partida). */
  updateCadena(dt) {
    const ch = this.chain;
    if (!ch) return;
    if ((ch.phase === 'react' || ch.phase === 'back') && this.predictValid &&
        ch.contact.distanceTo(this.predict) > 0.055) {
      this._reanclaCadena(this.predict, Math.max(this.predictT, 0.12));
      return;
    }
    ch.t += dt;
    let seg = ch.segs[ch.segIdx];
    let t = ch.t;
    while (seg && t > seg.T) {
      t -= seg.T;
      ch.segIdx++;
      seg = ch.segs[ch.segIdx];
      if (seg) ch.phase = seg.phase;
    }
    if (!seg) { this.chain = null; return; }
    ch.u = THREE.MathUtils.clamp(t / seg.T, 0, 1);
    mjQuintic(ch.u, seg.p0, seg.v0, seg.p1, seg.v1, seg.T, ch.cur);
    mjQuinticVel(ch.u, seg.p0, seg.v0, seg.p1, seg.v1, seg.T, ch.vel);
    if (ch.phase === 'recover') ch.cur.lerp(this.pos, Math.min(1, dt * 2.5));
    if (!Number.isFinite(ch.cur.x + ch.cur.y + ch.cur.z)) this.chain = null;
  }'''

editar(C06, "  setConfig(cfg) { this.cfg = cfg; }", METODOS, 'c06 métodos de la cadena')

print('c06 OK')
