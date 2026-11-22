#!/usr/bin/env python3
"""Ronda 28 · seguimiento — el bloque de sonido v2.142 pasa de Web Audio en
crudo a MOTORES createMusic del SDK. Motivo: la puerta de descargas de la
casa exige «decodeAudioData solo en el SDK (0 en el módulo)» — el fetch +
decode del mp3 debe vivir UNA vez en el SDK (regla v1.2.0: «ningún
campeonato conserva ya un decodeAudioData propio»).

Diseño nuevo (mismo comportamiento):
  · vias.mp3     — motor createMusic 'direct' con vol getter = 0,22·(v/vMax)
                   (volumen con la marcha, cero en paradas), sync por frame.
  · caballos.mp3 — un motor POR INSTANCIA ('fj' + 'ind0…2'): vol getter por
                   instancia, arranque DESFASADO (k×0,45 s), fundido
                   PROGRESIVO degradando el volumen y CORTE BRUSCO con off().
  · one-shots (tren_llegada / tunel) — igual que ya estaban (motor SFX).
  · cero pan (createMusic no lo lleva; no lo pidió el dueño)."""

import io
import sys

F = "/home/z/my-project/public/championships/oeste/index.js"

EDITS = []


def edit(old, new, tag):
    EDITS.append((tag, old, new))


# ---------------------------------------------- E1 bloque completo reescrito
OLD_BLOCK = """  /* ======================================================================
   *  v2.142 · SONIDOS DEL RECORRIDO (mp3 del dueño) — Web Audio en crudo
   *  para los BUCLES con control de volumen (el mismo camino del rumor):
   *   · vias.mp3     — roce de vías EN BUCLE mientras el vagón SE MUEVE:
   *                    el volumen sigue a la velocidad (cero en paradas).
   *   · caballos.mp3 — GALOPE por INSTANCIA: uno al aparecer el forajido
   *                    y UNO POR CADA INDIO (grupo desfasado 0,45 s), con
   *                    paneo al SU lado de la ventana; fundido PROGRESIVO
   *                    al alejarse (fuga) y CORTE BRUSCO al abatir.
   *  Los one-shots (tren_llegada.mp3 al frenar en la estación ·
   *  tunel.mp3 al entrar en el túnel) van por el motor SFX del SDK.
   *  ====================================================================== */
  _sndBuf(name) {
    /* decode UNA vez (forma promesa, lección v2.125); el fallo se SELLA
     * (null) para no re-pedir cada frame. */
    const g = this.game;
    const actx = g.audio && g.audio.ctx;
    if (!actx) return null;
    if (!this._rawBufs) this._rawBufs = {};
    const B = this._rawBufs;
    if (name in B) return B[name];
    if (!B['_' + name]) {
      B['_' + name] = true;                    // petición en vuelo
      try {
        fetch(this.__sfxSDK().url(name))
          .then((r) => r.arrayBuffer())
          .then((ab) => actx.decodeAudioData(ab.slice(0)))
          .then((buf) => { B[name] = buf; delete B['_' + name]; })
          .catch(() => { B[name] = null; delete B['_' + name]; });
      } catch (e) { B[name] = null; delete B['_' + name]; }
    }
    return null;
  }
  /* Precarga de los cuatro sonidos nuevos (start). */
  _sndTren() {
    try { this.__sfxSDK().precarga('tren_llegada.mp3'); } catch (e) { /* */ }
    try { this.__sfxSDK().precarga('tunel.mp3'); } catch (e) { /* */ }
    this._sndBuf('vias.mp3');
    this._sndBuf('caballos.mp3');
  }
  /* — VÍAS en bucle (volumen con la marcha) ——————————————————— */
  _viasEnsure() {
    const ctx = this._sndCtx();
    if (!ctx) return;                          // sin audio aún: reintento suave
    if (!this._viasSrc) {
      const buf = this._sndBuf('vias.mp3');
      if (!buf) return;                        // aún decodificando
      try {
        const src = ctx.createBufferSource();
        src.buffer = buf;
        src.loop = true;
        const gain = ctx.createGain();
        gain.gain.value = 0;
        src.connect(gain); gain.connect(ctx.destination);
        src.start();
        this._viasSrc = { src, gain };
      } catch (e) { this._viasSrc = null; }
    }
  }
  _viasSet(k) {
    this._viasEnsure();
    if (!this._viasSrc) return;
    try { this._viasSrc.gain.gain.value = 0.22 * clamp(k, 0, 1); } catch (e) { /* */ }
  }
  _viasStop() {
    if (!this._viasSrc) return;
    try { this._viasSrc.src.stop(); } catch (e) { /* */ }
    try { this._viasSrc.gain.disconnect(); } catch (e) { /* */ }
    this._viasSrc = null;
  }
  /* — GALOPE por instancia (forajido · cada indio) ————————————— */
  _cabStart(key, side, delay) {
    const ctx = this._sndCtx();
    if (!ctx) return;
    if (!this._cabMap) this._cabMap = {};
    if (this._cabMap[key]) return;             // sin dobles por clave
    const buf = this._sndBuf('caballos.mp3');
    if (!buf) return;                          // aún decodificando
    try {
      const t0 = ctx.currentTime + Math.max(0, delay || 0);
      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.loop = true;
      const gain = ctx.createGain();
      gain.gain.setValueAtTime(0.0001, t0);
      gain.gain.exponentialRampToValueAtTime(0.45, t0 + 0.16);  // sin chasquido
      let nodo = gain;
      if (ctx.createStereoPanner) {
        const pn = ctx.createStereoPanner();
        pn.pan.value = clamp((side || 0) * 0.5, -1, 1);   // SU lado de la ventana
        gain.connect(pn);
        nodo = pn;
      }
      nodo.connect(ctx.destination);
      src.start(t0);
      this._cabMap[key] = { src, gain };
    } catch (e) { /* el sonido nunca rompe el frame */ }
  }
  _cabFade(key, T) {
    /* PROGRESIVO: el jinete se aleja (fuga) o desaparece (túnel/andén). */
    const it = this._cabMap && this._cabMap[key];
    if (!it) return;
    delete this._cabMap[key];
    try {
      const ctx = this.game.audio.ctx;
      const t0 = ctx.currentTime;
      const t1 = t0 + Math.max(0.05, T || 0.6);
      it.gain.gain.cancelScheduledValues(t0);
      it.gain.gain.setValueAtTime(Math.max(0.0001, it.gain.gain.value), t0);
      it.gain.gain.exponentialRampToValueAtTime(0.0001, t1);
      it.src.stop(t1 + 0.08);
    } catch (e) { /* */ }
  }
  _cabStop(key) {
    /* BRUSCO: el jinete ha sido ABATIDO. */
    const it = this._cabMap && this._cabMap[key];
    if (!it) return;
    delete this._cabMap[key];
    try { it.gain.gain.cancelScheduledValues(0); } catch (e) { /* */ }
    try { it.gain.gain.value = 0.0001; } catch (e) { /* */ }
    try { it.src.stop(); } catch (e) { /* */ }
  }
  _cabStopAll() {
    if (!this._cabMap) return;
    for (const k of Object.keys(this._cabMap)) this._cabStop(k);
    this._cabMap = {};
  }
"""

NEW_BLOCK = """  /* ======================================================================
   *  v2.142 · SONIDOS DEL RECORRIDO (mp3 del dueño) — TODO por motores
   *  createMusic del SDK (cero decodeAudioData propio: regla de la casa
   *  «el decode vive UNA vez, en el SDK»). Variante «direct» del vagón
   *  sin exclusividades: el volumen manda POR FRAME desde el getter.
   *   · vias.mp3     — roce de vías EN BUCLE mientras el vagón SE MUEVE:
   *                    el volumen sigue a la velocidad (cero en paradas).
   *   · caballos.mp3 — GALOPE por INSTANCIA: un motor para el forajido y
   *                    uno POR CADA INDIO del pool (los grupos salen
   *                    DESFASADOS 0,45 s por jinete); fundido PROGRESIVO
   *                    degradando el volumen y CORTE BRUSCO con off().
   *  Los one-shots (tren_llegada.mp3 al frenar · tunel.mp3 al entrar en
   *  el túnel) van por el motor SFX del SDK (play + precarga).
   *  ====================================================================== */
  /* Fábrica de motor de AMBIENTE (una instancia por sonido/jinete). */
  _ambEng(file, volFn) {
    return createMusic(() => this.game, {
      url: () => this.__sfxSDK().url(file),
      vol: volFn,
      fadeIn: 0.16,               // entrada sin chasquido
      syncMode: 'direct',         // el volumen manda POR FRAME (vagón)
      gateStart: false, gateOn: false,
      renace: true, puede: () => true, excluso: () => false,
    });
  }
  /* Precarga de los cuatro sonidos nuevos (start). */
  _sndTren() {
    try { this.__sfxSDK().precarga('tren_llegada.mp3'); } catch (e) { /* */ }
    try { this.__sfxSDK().precarga('tunel.mp3'); } catch (e) { /* */ }
    try { this.__sfxSDK().precarga('vias.mp3'); } catch (e) { /* */ }
    try { this.__sfxSDK().precarga('caballos.mp3'); } catch (e) { /* */ }
  }
  /* — VÍAS en bucle (volumen con la marcha, cero en paradas) ——— */
  _viasVol() {
    return 0.22 * clamp((this.v || 0) / TREN.vMax, 0, 1);
  }
  _viasStart() {
    if (!this._viasEng) {
      this._viasEng = this._ambEng('vias.mp3', () => this._viasVol());
    }
    this._viasEng.on();
  }
  _viasStop() {
    if (this._viasEng) { try { this._viasEng.off(); } catch (e) { /* */ } }
  }
  /* — GALOPE por instancia (forajido 'fj' · cada indio 'ind0…2') — */
  _cabEngs() {
    if (!this._cab) {
      this._cab = ['fj', 'ind0', 'ind1', 'ind2'].map((key) => {
        const c = { key, k: 0, onT: -1, fadeT: 0, fadeT0: 1, fadeK0: 0, eng: null };
        c.eng = this._ambEng('caballos.mp3', () => c.k);
        return c;
      });
    }
    return this._cab;
  }
  _cabGet(key) {
    return this._cabEngs().find((c) => c.key === key) || null;
  }
  /* GALOPE arranca (delay 0 = forajido · k×0,45 s = jinete k del grupo) */
  _cabStart(key, delay) {
    const c = this._cabGet(key);
    if (!c) return;
    c.k = 0.45;
    c.onT = Math.max(0, delay || 0);
    if (c.onT <= 0) { c.onT = -1; c.eng.on(); }
  }
  _cabFade(key, T) {
    /* PROGRESIVO: degrada el volumen hasta 0 en T s (el jinete se aleja) */
    const c = this._cabGet(key);
    if (!c) return;
    c.fadeT0 = Math.max(0.05, T || 0.6);
    c.fadeT = c.fadeT0;
    c.fadeK0 = c.k;
  }
  _cabCut(key) {
    /* BRUSCO: el jinete ha sido ABATIDO. */
    const c = this._cabGet(key);
    if (!c) return;
    c.k = 0; c.onT = -1; c.fadeT = 0;
    try { c.eng.off(); } catch (e) { /* */ }
  }
  _cabStopAll() {
    if (!this._cab) return;
    for (const c of this._cab) {
      c.k = 0; c.onT = -1; c.fadeT = 0;
      try { c.eng.off(); } catch (e) { /* */ }
    }
  }
  /* Paso POR FRAME de los bucles de ambiente (fxStep): retrasos de los
   * galopes, fundidos y sync 'direct' de TODOS los motores. */
  _ambStep(dt) {
    if (this._viasEng) this._viasEng.sync();
    if (!this._cab) return;
    for (const c of this._cab) {
      if (c.onT > 0) {
        c.onT -= dt;
        if (c.onT <= 0) { c.onT = -1; c.eng.on(); }
      }
      if (c.fadeT > 0) {
        c.fadeT -= dt;
        const f = Math.max(0, c.fadeT / c.fadeT0);
        c.k = c.fadeK0 * f;
        if (c.fadeT <= 0 && c.eng.sonando()) c.eng.off();
      }
      c.eng.sync();
    }
  }
"""

edit(OLD_BLOCK, NEW_BLOCK, "bloque createMusic")

# --------------------------------------------------------------- E2 fxStep
edit(
    """    // v2.142 · ROCE DE VÍAS: mp3 del dueño EN BUCLE, volumen con la marcha
    this._viasSet(this.v / TREN.vMax);""",
    """    // v2.142 · AMBIENTE: vias con la marcha + galopes (retrasos y fundidos)
    this._ambStep(dt);""",
    "fxStep _ambStep",
)

# ------------------------------------------------------------ E3 start hook
edit(
    """    this._startRumble();
    this._setRumble(0);""",
    """    this._startRumble();
    this._setRumble(0);
    this._viasStart();   // v2.142: roce de vías EN BUCLE (volumen con la marcha)""",
    "start _viasStart",
)

# --------------------------------------------------- E4 galope del forajido
edit(
    """    this._cabStart('fj', this._fjSide, 0);   // v2.142: GALOPE del dueño""",
    """    this._cabStart('fj', 0);   // v2.142: GALOPE del dueño""",
    "forajido spawn",
)

# ---------------------------------------------------- E5 galopes de indios
edit(
    """      this._cabStart('ind' + k, side, k * 0.45);   // v2.142: UN galope por jinete, DESFASADOS""",
    """      this._cabStart('ind' + k, k * 0.45);   // v2.142: UN galope por jinete, DESFASADOS""",
    "indios spawn",
)


def main():
    with io.open(F, "r", encoding="utf-8") as f:
        src = f.read()
    for tag, old, new in EDITS:
        n = src.count(old)
        if n != 1:
            print(f"FALLO [{tag}]: ancla encontrada {n} veces (esperaba 1)")
            sys.exit(1)
    for tag, old, new in EDITS:
        src = src.replace(old, new, 1)
        print(f"OK  [{tag}]")
    with io.open(F, "w", encoding="utf-8") as f:
        f.write(src)
    # verificación dura: el módulo ya NO decodifica audio
    n_dec = src.count("decodeAudioData(")
    print(f"decodeAudioData en el módulo: {n_dec} (debe ser 0)")
    if n_dec:
        sys.exit(1)
    print(f"{len(EDITS)} ediciones aplicadas en {F}")


if __name__ == "__main__":
    main()
