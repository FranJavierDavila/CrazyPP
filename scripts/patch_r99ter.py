#!/usr/bin/env python3
# r99ter · sustituye el núcleo de la cadena: segmentos polilínea → JINETE
# SOBRE LA CURVA (Catmull-Rom continua, seguimiento de la bola por frame,
# contacto por proximidad, follow-through = la misma curva frenando).
import re, sys

RAIZ = '/home/z/my-project'
FIC = RAIZ + '/src/game/core/c06_logros_stats_ia_rival.js'
src = open(FIC, encoding='utf-8').read()

def splice(ini, fin, nuevo, que):
    i = src.find(ini)
    j = src.find(fin, i + len(ini))
    assert i >= 0 and j > i, 'marcadores no encontrados: ' + que
    return src[:i] + nuevo + src[j:]

SRC = src

# ── 1 · helpers CR: tabla por cadena (4 IAs vivas) ──
nuevo_helpers = '''/* r99ter · SPLINE Catmull-Rom del GESTO COMPLETO — la pala es el extremo de
 * una cadena cinemática y recorre UNA SOLA CURVA continua [cuerpo → carga B
 * → contacto C → cruce F]. La tabla es POR CADENA (hay 4 IAs vivas: rival,
 * compañero, rival 2 y demo — una tabla módulo se pisaría entre ellas). */
const CR_N = 48;                              // muestras de la curva
const _crK = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3(),
  new THREE.Vector3()];                       // nudos cur/B/C/F (rascadores)
const _crPh = new THREE.Vector3();            // nudo fantasma (extensión)
const _crA = new THREE.Vector3();
const _crB = new THREE.Vector3();

function _crTablaNueva() {
  const pts = [];
  for (let i = 0; i < CR_N; i++) pts.push(new THREE.Vector3());
  return { pts, len: new Float32Array(CR_N), total: 0 };
}

/** evalúa el tramo CR del nudo i al i+1 en t∈[0,1] (fórmula estándar) */
function _crSeg(i, t, out) {
  const p0 = i === 0 ? _crPh.copy(_crK[0]).multiplyScalar(2).sub(_crK[1])
    : _crK[i - 1];
  const p1 = _crK[i], p2 = _crK[i + 1];
  const p3 = i === 2 ? _crPh.copy(_crK[3]).multiplyScalar(2).sub(_crK[2])
    : _crK[i + 2];
  const t2 = t * t, t3 = t2 * t;
  out.copy(p1).multiplyScalar(2)
    .addScaledVector(_crA.copy(p2).sub(p0), t)
    .addScaledVector(_crB.copy(p0).addScaledVector(p1, -5).addScaledVector(p2, 4)
      .sub(p3), t2)
    .addScaledVector(_crB.copy(p0).addScaledVector(p1, 3).addScaledVector(p2, -3)
      .add(p3), t3)
    .multiplyScalar(0.5);
  return out;
}

/** rellena la tabla de la curva desde los nudos [cur, B, C, F]; devuelve la
 *  longitud de arco en la que está el CONTACTO (nudo C, fracción 2/3) */
function _crRellena(curva) {
  let len = 0;
  curva.len[0] = 0;
  curva.pts[0].copy(_crK[0]);
  for (let i = 0; i < CR_N - 1; i++) {
    const u = (i + 1) / (CR_N - 1) * 3;
    const seg = Math.min(2, Math.floor(u));
    _crSeg(seg, u - seg, curva.pts[i + 1]);
    len += curva.pts[i].distanceTo(curva.pts[i + 1]);
    curva.len[i + 1] = len;
  }
  curva.total = len;
  return curva.len[Math.round((CR_N - 1) * 2 / 3)];   // arco hasta el contacto
}

/** punto de la curva en la longitud de arco s (interp. lineal de la tabla) */
function _crPunto(curva, s, out) {
  const s2 = THREE.MathUtils.clamp(s, 0, curva.total);
  let lo = 0, hi = CR_N - 1;
  while (hi - lo > 1) { const mid = (lo + hi) >> 1;
    if (curva.len[mid] < s2) lo = mid; else hi = mid; }
  const seg = curva.len[hi] - curva.len[lo];
  const f = seg > 1e-9 ? (s2 - curva.len[lo]) / seg : 0;
  return out.copy(curva.pts[lo]).lerp(curva.pts[hi], f);
}

/** tangente de la curva en la longitud de arco s (diferencia finita) */
function _crTangente(curva, s, out) {
  const h = Math.max(0.01, curva.total * 0.01);
  _crPunto(curva, Math.max(0, s - h), _crA);
  _crPunto(curva, Math.min(curva.total, s + h), _crB);
  return out.copy(_crB).sub(_crA);
}

'''
src = splice('/* r99ter · SPLINE', 'export class OpponentAI', nuevo_helpers,
             'helpers CR')

# ── 2 · planCadena: el plan ya no traza fases — arma la curva ──
nuevo_plan = '''  /** r99ter · PLAN del golpe (nace con la primera predicción válida): ya no
   *  hay fases con la pala aparcada («se coloca en posiciones muy raras») —
   *  el gesto entero es UNA CURVA continua que updateCadena recorre con
   *  velocidad tangente y regenera CADA FRAME para seguir a la bola.
   *  kind/fh/roll conservan la firma de cada golpe. */
  planCadena(contact, tBall, kind, fh) {
    const chVieja = this.chain;
    this.chain = {
      phase: 'back', t: 0, kind, fh, flat: !!(chVieja && chVieja.flat),
      contact: contact.clone(), tBall,
      dir: new THREE.Vector3(0, 0, -this.sign),
      vdir: new THREE.Vector3(0, 0, -this.sign),
      roll: this._rollCadena(kind),
      cur: chVieja ? chVieja.cur.clone() : this.pos.clone(),
      vel: chVieja ? chVieja.vel.clone() : new THREE.Vector3(),
      u: 0, s: 0, speed: 0, contactoHecho: false, dRem0: 0,
      jit: 0.88 + Math.random() * 0.24,
      curva: _crTablaNueva(),
    };
    this._armaCurva(contact, tBall);
  }

'''
src = splice('  /** r91 · PLAN del golpe', '  /** r91 · RE-ANCLAJE',
             nuevo_plan, 'planCadena')

# ── 3 · _reanclaCadena → _armaCurva (regeneración del gesto) ──
nuevo_arma = '''  /** r99ter · ARMA/REGENERA la curva del gesto [cur → carga B → contacto C
   *  → cruce F] (Catmull-Rom, tabla de 48 muestras con longitudes de arco).
   *  Se llama al planificar Y CADA FRAME de la aproximación: C persigue la
   *  posición futura de la bola — el dueño: «la pala no realiza el
   *  seguimiento de la bola». La pala siempre está SOBRE el gesto que
   *  enmarca la bola real: nada de esperas ni posiciones raras. */
  _armaCurva(contact, tBall) {
    const ch = this.chain;
    if (!ch || ch.contactoHecho) return;   // tras el contacto la curva ES sagrada
    const G = CADENA_GOLPE[ch.kind] || CADENA_GOLPE.drive;
    // dirección de SALIDA: la del disparo pendiente si ya se decidió (la
    // tangente del gesto en C empuja hacia donde va la bola); si no, hacia
    // el campo del jugador y el golpe la refinará al decidirse
    const dv = this._disparo ? _cadV.copy(this._disparo.v)
      : _cadV.set((Math.random() - 0.5) * 0.4 - contact.x * 0.5, 0.22,
          DIMS.tableCenterZ - this.sign * DIMS.tableHalfLength * 0.7 - contact.z);
    _cadD.copy(dv).normalize();
    ch.dir.copy(_cadD);
    ch.vdir.copy(dv).normalize();
    ch.roll = this._rollCadena(ch.kind);
    ch.contact.copy(contact);
    ch.tBall = tBall;
    // amplitudes con el TIEMPO: mucho tiempo → loop amplio y leído; poco →
    // gesto compacto (la calabaza, mitad de amplitud: piel, no pirueta)
    const dil = THREE.MathUtils.clamp(tBall / 0.55, 0.35, 1) *
      (ch.flat ? 0.5 : 1) * ch.jit;
    const B = _cadA.copy(contact).addScaledVector(_cadD, -G.dbs * dil);
    B.x += ch.fh * this.sign * G.dbs * 0.85 * dil;    // r92 · carga al lado
    B.y = Math.max(0.5, contact.y - G.hbs * dil);
    const F = _cadB.copy(contact).addScaledVector(_cadD, G.dft * ch.jit);
    F.x -= ch.fh * this.sign * G.dft * 0.62 * ch.jit; // r92 · cruce al otro
    F.y = Math.max(0.5, contact.y + G.hft * ch.jit);
    _crK[0].copy(ch.cur); _crK[1].copy(B);
    _crK[2].copy(contact); _crK[3].copy(F);
    ch.sC = _crRellena(ch.curva);      // arco del nudo contacto C
    ch.s = 0;                          // el jinete SIEMPRE nace en cur
  }

'''
src = splice('  /** r91 · RE-ANCLAJE', '  /** r91 · IMPACTO REAL',
             nuevo_arma, '_armaCurva')

# ── 4 · cadenaContacto → re-arma al intercepto real (API intacta) ──
nuevo_contacto = '''  /** r91/r99ter · IMPACTO REAL: al DECIDIRSE el golpe (barrido de siempre)
   *  la curva se re-arma al intercepto exacto con la dirección de salida
   *  REAL — el gesto apunta ya a donde va la bola (cadena cinemática). */
  cadenaContacto(cx, cy, cz, v, TBola) {
    const ch = this.chain;
    if (!ch || ch.contactoHecho) return;
    ch.roll = this._rollCadena(ch.kind);
    this._armaCurva(_cadA.set(cx, cy, cz),
      TBola !== undefined ? TBola : Math.max(this.predictT, 0.15));
  }

'''
src = splice('  /** r91 · IMPACTO REAL', '  /** r91 · frame de la cadena',
             nuevo_contacto, 'cadenaContacto')

# ── 5 · updateCadena + _enContacto → el JINETE sobre la curva ──
nuevo_update = '''  /** r99ter · frame del JINETE SOBRE LA CURVA: regenera el gesto (seguimiento
   *  de la bola), cronometra la velocidad tangente para llegar al punto
   *  dulce CUANDO llega la bola, dispara el contacto POR PROXIMIDAD (nada
   *  de teletransportes) y sigue la MISMA curva frenando suave — el
   *  acompañamiento continuo que pide el dueño: «la pala forma parte de una
   *  cadena cinemática; golpea en el punto dulce e impulsa continuando la
   *  trayectoria previa curva con el empuje correspondiente». */
  updateCadena(dt, ball) {
    // r99 · VIGÍA DEL DISPARO DIFERIDO: sin cadena viva o con espera
    // excesiva, la salida se aplica igualmente — jamás se pierde un rallye.
    if (this._disparo) {
      this._disparo.t += dt;
      if (!this.chain || this._disparo.t > this._disparo.tMax) this._aplicaDisparo();
    }
    const ch = this.chain;
    if (!ch) return;
    ch.t += dt;
    const vivo = ball || null;
    if (!ch.contactoHecho) {
      // ── 1 · SEGUIMIENTO: el contacto C = la posición FUTURA de la bola ──
      let cx, cy, cz, tRem;
      if (this.predictValid && vivo) {
        cx = this.predict.x; cy = this.predict.y; cz = this.predict.z;
        tRem = Math.max(this.predictT, 0.05);
      } else if (vivo) {
        // persecución lineal al punto de encuentro estimado
        tRem = THREE.MathUtils.clamp(ch.cur.distanceTo(vivo.pos) / 6, 0.06, 0.35);
        cx = vivo.pos.x + vivo.vel.x * tRem * 0.9;
        cy = vivo.pos.y + vivo.vel.y * tRem * 0.9;
        cz = vivo.pos.z + vivo.vel.z * tRem * 0.9;
      } else {
        cx = ch.contact.x; cy = ch.contact.y; cz = ch.contact.z;
        tRem = Math.max(ch.tBall, 0.12);
      }
      this._armaCurva(_cadA.set(cx, cy, cz), tRem);
      // ── 2 · CRONÓMETRO: vC para llegar al punto dulce CON la bola ──
      const dRem = Math.max(0.02, ch.sC);            // arco restante cur→C
      if (!ch.dRem0) ch.dRem0 = Math.max(dRem, 0.12);
      const vC = THREE.MathUtils.clamp(dRem / Math.max(tRem, 0.06), 2.0, 7.8);
      const a = THREE.MathUtils.clamp(
        (vC * vC - ch.speed * ch.speed) / (2 * dRem), 6, 45);
      ch.speed = Math.min(vC, ch.speed + a * dt);
      ch.phase = dRem > 0.30 ? 'back' : 'strike';
      ch.u = 1 - THREE.MathUtils.clamp(dRem / ch.dRem0, 0, 1);
      // ── 3 · AVANCE sobre la curva (velocidad tangente REAL) ──
      ch.s = Math.min(ch.sC, ch.speed * dt);         // no se pasa de C sin bola
      _crPunto(ch.curva, ch.s, ch.cur);
      _crTangente(ch.curva, ch.s, ch.vel).normalize().multiplyScalar(ch.speed);
      // ── 4 · CONTACTO POR PROXIMIDAD: la pala ALCANZA a la bola real ──
      if (this._disparo && vivo &&
          ch.cur.distanceTo(vivo.pos) < 0.085 &&
          ch.vel.dot(_cadP.copy(vivo.pos).sub(ch.cur)) > 0) {
        ch.sContacto = ch.s;                          // donde la curva tocó la bola
        this._aplicaDisparo();
        ch.contactoHecho = true;
        ch.phase = 'follow';
        return;
      }
      // ── 4b · la bola escapó (pasó de largo y se aleja): soltar la cadena
      // en vez de perseguir fantasmas detrás del cuerpo (el vigía aplicó) ──
      if (this._disparo && vivo && this._disparo.t > 0.35 &&
          ch.cur.distanceTo(vivo.pos) > 0.22 &&
          ch.vel.dot(_cadP.copy(vivo.pos).sub(ch.cur)) < 0) {
        this.chain = null;
        return;
      }
    } else {
      // ── 5 · ACOMPAÑAMIENTO: la MISMA curva continúa, frenando suave ──
      ch.speed *= Math.exp(-dt / 0.22);
      ch.s = Math.min(ch.curva.total, ch.s + ch.speed * dt);
      _crPunto(ch.curva, ch.s, ch.cur);
      _crTangente(ch.curva, ch.s, ch.vel).normalize().multiplyScalar(ch.speed);
      const finCurva = ch.s >= ch.curva.total - 0.02 || ch.speed < 0.45;
      if (!finCurva) {
        ch.phase = 'follow';
        ch.u = THREE.MathUtils.clamp(
          (ch.s - (ch.sContacto || ch.sC)) /
          Math.max(0.05, ch.curva.total - (ch.sContacto || ch.sC)), 0, 1);
      } else {
        // ── 6 · RECUPERACIÓN: fusión exponencial al cuerpo (sin tirón) ──
        ch.phase = 'recover';
        ch.u = 0;
        ch.vel.multiplyScalar(Math.exp(-dt / 0.15));
        ch.cur.lerp(this.pos, Math.min(1, dt * 2.2));
        if (ch.cur.distanceTo(this.pos) < 0.05) { this.chain = null; return; }
      }
    }
    // r99bis · TOPE DE PASO (garantía dura): ≤ 13 cm por frame pase lo que
    // pase — el gesto se ve SIEMPRE progresivo, jamás brusco.
    if (!ch._curPrev) ch._curPrev = ch.cur.clone();
    _cadP.copy(ch.cur).sub(ch._curPrev);
    if (_cadP.length() > 0.13) {
      _cadP.setLength(0.13);
      ch.cur.copy(ch._curPrev).add(_cadP);
      ch.vel.copy(_cadP).multiplyScalar(60);
    }
    ch._curPrev.copy(ch.cur);
    if (!Number.isFinite(ch.cur.x + ch.cur.y + ch.cur.z)) this.chain = null;
  }

'''
src = splice('  /** r91 · frame de la cadena', '  reset() {', nuevo_update,
             'updateCadena+enContacto')

# ── 6 · _aplicaDisparo: SIN teleport de bola + sesgo a la tangente ──
viejo_apl = '''  /** r99 · APLICADOR DEL DISPARO: la pala GOLPEA la bola donde esté —
   *  si la bola está en el punto de barrido (±8 cm) se ajusta (deriva de
   *  predicción invisible); si pasó de largo (la pala llegó tarde), la
   *  PALA la atrapa: chain.cur salta a la bola (toque de muñeca real) y
   *  el follow-through arranca de ahí. El tiro se RECALCULA desde la
   *  posición real de la bola hacia el MISMO blanco: bota donde apunta,
   *  con contacto visible, sonido y árbitro sincronizados. */
  _aplicaDisparo() {
    const d = this._disparo;
    if (!d) return;
    this._disparo = null;
    const b = d.ball;
    if (b.pos.distanceTo(d.pos) < 0.08) b.pos.copy(d.pos);
    const vReal = d.target
      ? computeShotVelocityReal(b.pos, d.target, d.T, d.maxV, d.spin)
      : d.v;
    b.vel.copy(vReal);'''
nuevo_apl = '''  /** r99ter · APLICADOR DEL DISPARO: NADA de teletransportes (el dueño vio
   *  «la bola y la pala teletransportándose»): la bola JAMÁS se recoloca —
   *  el tiro nace de DONDE ESTÁ, recalculado hacia el mismo blanco. Y su
   *  dirección se SESGA a la tangente del swing en el contacto (35 %): la
   *  cadena cinemática EMPUJA — la bola continúa la trayectoria curva de la
   *  pala con el empuje correspondiente. Contacto, sonido y árbitro aquí. */
  _aplicaDisparo() {
    const d = this._disparo;
    if (!d) return;
    this._disparo = null;
    const b = d.ball;
    const vReal = d.target
      ? computeShotVelocityReal(b.pos, d.target, d.T, d.maxV, d.spin)
      : d.v;
    const chX = this.chain;
    if (chX && chX.vel && chX.vel.lengthSq() > 1) {
      const tan = _cadT.copy(chX.vel).normalize();
      const mag = vReal.length();
      _cadD.copy(vReal).normalize().lerp(tan, 0.35).normalize()
        .multiplyScalar(mag);
      vReal.copy(_cadD);
    }
    b.vel.copy(vReal);'''
assert viejo_apl in src, 'aplicador'
src = src.replace(viejo_apl, nuevo_apl)

# el bloque que ATRAPABA la bola con la pala (salto) desaparece
viejo_atrapa = '''    // la pala ATRAPA: su cur (y el arranque del follow) quedan EN la bola
    if (this.chain) {
      this.chain.cur.copy(b.pos);
      const s0 = this.chain.segs[this.chain.segIdx];
      if (s0) s0.p0.copy(b.pos);
    }
    this._retPend = vReal;'''
nuevo_atrapa = '''    this._retPend = vReal;'''
assert viejo_atrapa in src, 'atrapa'
src = src.replace(viejo_atrapa, nuevo_atrapa)

# ── 7 · el frame de update pasa la BOLA al jinete (seguimiento) ──
viejo_llamada = '    this.updateCadena(dt);'
assert viejo_llamada in src, 'llamada'
src = src.replace(viejo_llamada, '    this.updateCadena(dt, ball);')

open(FIC, 'w', encoding='utf-8').write(src)
print('r99ter aplicado: jinete sobre la curva (7 parches)')
