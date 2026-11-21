#!/usr/bin/env python3
"""Reconstruye el c06 PRE-cambios (3.6.198 golden) invirtiendo las 12 ediciones
de r87, para medir la línea base del arnés r99ter. Escribe /tmp/c06_pre.mjs."""
C06 = '/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js'
OUT = '/tmp/c06_pre.mjs'

s = open(C06, encoding='utf-8').read()

def inv(name, nuevo, viejo):
    global s
    n = s.count(nuevo)
    assert n == 1, f'{name}: {n} apariciones del texto NUEVO (esperaba 1)'
    s = s.replace(nuevo, viejo)

# 12 · empuje acotado → 35 % ciego
inv('empuje',
    """    // r101 · EL EMPUJE DEL SWING, ACOTADO: la tangente del gesto solo sesga
    // la salida si ACOMPAÑA al tiro (afinidad > 0.45) y con fuerza mínima
    // (12 % × afinidad) — antes un 35 % CIEGO desviaba el blanco del solver
    // y mandaba la bola fuera de la mesa «de manera ridícula» (informe del
    // dueño r101). Se excluyen además las picos de velocidad del homing
    // (> 10 m/s: no son swing, son el paso de caza a 60 m/s aparentes).
    const chX = this.chain;
    if (chX && chX.vel && chX.vel.lengthSq() > 1 && chX.vel.lengthSq() < 100 &&
        !chX.persec) {
      const tan = _cadT.copy(chX.vel).normalize();
      const mag = vReal.length();
      const afinidad = tan.dot(_cadD.copy(vReal).normalize());
      if (afinidad > 0.45) {
        _cadD.lerp(tan, 0.12 * afinidad).normalize().multiplyScalar(mag);
        vReal.copy(_cadD);
      }
    }""",
    """    const chX = this.chain;
    if (chX && chX.vel && chX.vel.lengthSq() > 1 && !chX.persec) {
      const tan = _cadT.copy(chX.vel).normalize();
      const mag = vReal.length();
      _cadD.copy(vReal).normalize().lerp(tan, 0.35).normalize()
        .multiplyScalar(mag);
      vReal.copy(_cadD);
    }""")

# 11 · nudos del gesto → sin clamp
inv('nudos_gesto',
    """    _crK[2].copy(ch.contact); _crK[3].copy(F);
    // r101 · espacio de trabajo en TODOS los nudos: la carga y la prolonga-
    // ción nacen dentro del espacio humano — el backswing ya no se hunde
    // bajo la losa de la mesa ni la prolongación cruza la red
    for (let _nk = 0; _nk < 4; _nk++) _clampPalaMesa(_crK[_nk], this.sign);
    ch.sC = _crRellena(ch.curva);      // arco del nudo contacto C""",
    """    _crK[2].copy(ch.contact); _crK[3].copy(F);
    ch.sC = _crRellena(ch.curva);      // arco del nudo contacto C""")

# 10 · nudos de la persecución → sin clamp
inv('nudos_persec',
    """      _crK[3].copy(contact);
      // r101 · espacio de trabajo en TODOS los nudos: la caza nunca se
      // planifica atravesando la mesa ni cruzando la red
      for (let _nk = 0; _nk < 4; _nk++) _clampPalaMesa(_crK[_nk], this.sign);
      ch.sC = _crRellena(ch.curva);""",
    """      _crK[3].copy(contact);
      ch.sC = _crRellena(ch.curva);""")

# 9 · cierre updateCadena → sin clamp ni _palaVis
inv('cierre',
    """    // r101 · ESPACIO DE TRABAJO (garantía dura, todos los caminos): el
    // punto de la pala jamás bajo la losa de la mesa, en la red, bajo el
    // suelo ni fuera del espacio humano — ni siquiera un frame
    // («la pala atraviesa la mesa», informe del dueño).
    _clampPalaMesa(ch.cur, this.sign);
    // r101 · ÚLTIMO PUNTO VISIBLE de la pala: lo consulta el vigía honesto
    // cuando la cadena ya murió (referencia del contacto real).
    this._palaVis.copy(ch.cur);
    ch._curPrev.copy(ch.cur);""",
    """    ch._curPrev.copy(ch.cur);""")

# 8 · muerta honesta → reserva
inv('muerta',
    """      const muerta = vivo && (vivo.pos.y < 0.30 ||
        Math.abs(vivo.pos.x) > 1.35 ||
        // r101 · fronteras relativas a la RED real (C_RED = −1,6): antes
        // z=0 daba la bola por muerta aún SOBRE la mesa (z<−2,6 era dentro
        // del tablero) y la «vuelta al campo del jugador» se detectaba
        // 1,6 m tarde — de ahí persecuciones allende la red
        (this.sign < 0 ? vivo.pos.z < C_RED - 2.6 : vivo.pos.z > C_RED + 2.6) ||
        // la bola VOLVIÓ al campo del jugador (devuelta antes del cruce o
        // saque propio en vuelo): perseguirla allende la red SACA la pala
        // de su campo — el punto se juega al otro lado y el árbitro manda.
        (this.sign < 0 ? vivo.pos.z > C_RED + 0.04 : vivo.pos.z < C_RED - 0.04));
      if (muerta) {
        // r101 · la bola MUERTA JAMÁS se devuelve: antes el disparo de
        // reserva salía desde donde estuviera (golpes «desde el suelo» y
        // desde puntos donde no hay pala — informe del dueño). El punto ya
        // lo cantó el árbitro: la pala suelta y vuelve al cuerpo a la vista.
        this._disparo = null;
        this.chain = null;
        return;
      }""",
    """      const muerta = vivo && (vivo.pos.y < 0.30 ||
        Math.abs(vivo.pos.x) > 1.35 ||
        (this.sign < 0 ? vivo.pos.z < -2.6 : vivo.pos.z > 2.6) ||
        // r99ter-2 · la bola VOLVIÓ al campo del jugador (devuelta antes del
        // cruce o saque propio en vuelo): perseguirla allende la red SACA la
        // pala de su campo — el punto se juega al otro lado y el árbitro
        // manda. Este era el bloqueo que vio el dueño.
        (this.sign < 0 ? vivo.pos.z > 0.04 : vivo.pos.z < -0.04));
      if (muerta) {
        if (this._disparo) { this._aplicaDisparo(); return; }
        this.chain = null;    // sin disparo pendiente: soltar y volver al cuerpo
        return;
      }""")

# 7 · ventana 9,5 → 8,5 cm
inv('ventana',
    "        (ch.cur.distanceTo(vivo.pos) < 0.095 ||\n"
    "         ch.cur.distanceTo(_cadT.copy(vivo.pos)\n"
    "           .addScaledVector(vivo.vel, anticipa)) < 0.095);",
    "        (ch.cur.distanceTo(vivo.pos) < 0.085 ||\n"
    "         ch.cur.distanceTo(_cadT.copy(vivo.pos)\n"
    "           .addScaledVector(vivo.vel, anticipa)) < 0.085);")

# 6 · caza frontera real → z=0
inv('caza_red',
    """        // ...pero la caza NUNCA cruza la red (r101 · la frontera es la RED
        // REAL en C_RED, no z=0): C vive en el campo propio
        if (this.sign < 0) cz = Math.min(cz, C_RED - 0.06);
        else cz = Math.max(cz, C_RED + 0.06);""",
    """        // ...pero la caza NUNCA cruza la red: C vive en el campo propio
        if (this.sign < 0) cz = Math.min(cz, -0.06); else cz = Math.max(cz, 0.06);""")

# 5 · C_RED → sin ella
inv('C_RED',
    """    const vivo = ball || null;
    // r101 · FRONTERA REAL DE LA RED: la pista se mide desde tableCenterZ
    // (−1,6) — antes la cadena usaba z=0 y la pala cruzaba la red 1,5 m
    // (la queja «la pala atraviesa la mesa»).
    const C_RED = DIMS.tableCenterZ;
""",
    "    const vivo = ball || null;\n")

# 4 · vigía honesto → vigía fantasma
inv('vigia',
    """    // r101 · VIGÍA DEL DISPARO DIFERIDO, HONESTO: la salida solo se aplica
    // si la pala VISIBLE está en la bola (contacto real, ≤ 13 cm) — con la
    // cadena muerta o el reloj vencido y la pala lejos, el rival FALLA a la
    // vista: la bola sigue su vuelo y el árbitro manda. Adiós al golpe que
    // «nace desde otro sitio donde la pala no se ve» (queja del dueño r101).
    if (this._disparo) {
      this._disparo.t += dt;
      if (!this.chain || this._disparo.t > this._disparo.tMax) {
        // la referencia es el punto visible de la pala: cur de la cadena
        // viva o el ÚLTIMO punto visible (_palaVis) si ya murió
        const pv = this.chain ? this.chain.cur : this._palaVis;
        if (pv && pv.distanceTo(this._disparo.ball.pos) < 0.13) {
          this._aplicaDisparo();
        } else {
          // la pala no llegó: fallo A LA VISTA — se suelta todo y el punto
          // se resuelve solo con la física (nunca un golpe fantasma)
          this._disparo = null;
          this.chain = null;
          this._retPend = null;
        }
      }
    }""",
    """    // r99 · VIGÍA DEL DISPARO DIFERIDO: sin cadena viva o con espera
    // excesiva, la salida se aplica igualmente — jamás se pierde un rallye.
    if (this._disparo) {
      this._disparo.t += dt;
      if (!this.chain || this._disparo.t > this._disparo.tMax) this._aplicaDisparo();
    }""")

# 3 · _palaVis del constructor → sin ella
inv('palaVis',
    """    this._disparo = null;
    this._retPend = null;
    // r101 · ÚLTIMO PUNTO VISIBLE de la pala (referencia del vigía honesto
    // cuando la cadena murió): nace en el cuerpo y updateCadena lo mantiene
    this._palaVis = this.pos.clone();
  }""",
    """    this._disparo = null;
    this._retPend = null;
  }""")

# 2 · _clampPalaMesa → fuera
i = s.find('\n/* r101 · ESPACIO DE TRABAJO de la mano del rival')
assert i >= 0
j = s.find('}\n', s.find('  return v;\n', i))
assert j >= 0
s = s[:i] + s[j + 1:]

# 1 · helpers de brazo devueltos (bloque entero entre CADENA_GOLPE y rascadores)
marca = '/* rascadores de la cadena (cero allocs por frame) */'
assert s.count(marca) == 1
helpers = """/* r91 · quíntico de Hermite con velocidades en los extremos (v0=v1=0 ⇒
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

export function zonaDulceNudge(grip, ballPos, bladeCenter, bladeR, out) {
  const dx = ballPos.x - bladeCenter.x;
  const dy = ballPos.y - bladeCenter.y;
  const dz = ballPos.z - bladeCenter.z;
  const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
  const exceso = d - bladeR * 0.62;
  if (exceso <= 0) return out.copy(grip);
  const k = Math.min(exceso, 0.04) / (d || 1e-6);
  return out.set(grip.x + dx * k, grip.y + dy * k, grip.z + dz * k);
}

class OneEuroV3 {
  constructor(fcMin = 1.2, beta = 0.045) {
    this.fcMin = fcMin; this.beta = beta;
    this.init = false;
    this.prev = new THREE.Vector3();
    this.dPrev = new THREE.Vector3();
    this.tmp = new THREE.Vector3();
  }
  reset() { this.init = false; this.dPrev.set(0, 0, 0); }
  _alfa(dt, fc) {
    const tau = 1 / (2 * Math.PI * Math.max(fc, 0.01));
    return 1 / (1 + tau / Math.max(dt, 1e-4));
  }
  filtrar(v, dt) {
    if (!this.init) { this.init = true; this.prev.copy(v); this.dPrev.set(0, 0, 0); return this.tmp.copy(v); }
    this.tmp.copy(v).sub(this.prev).divideScalar(Math.max(dt, 1e-4));
    const ad = this._alfa(dt, this.fcMin + this.beta * this.tmp.length());
    this.dPrev.lerp(this.tmp, ad);
    this.prev.addScaledVector(this.dPrev, dt);
    return this.tmp.copy(this.prev);
  }
}

const _oeqA = new THREE.Quaternion();

"""
s = s.replace(marca, helpers + marca, 1)

open(OUT, 'w', encoding='utf-8').write(s)
print(f'c06 pre-cambios escrito: {len(s):,} B')
