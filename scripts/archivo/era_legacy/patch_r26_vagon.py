#!/usr/bin/env python3
"""Ronda 26 · EL VAGÓN SUENA + CADENA INMEDIATA + CAJONES EN LA VENTANA
peticiones del dueño sobre la etapa 4 «ASALTO AL TREN» del oeste:

  (1) CADENA DE LA DINAMITA INMEDIATA: al tocar la bola el medallón de
      dinamita sale YA cazando la caja viva más cercana (tiro balístico).
      La cadena de v2.134 existe pero ARRANCABA TARDE: la bola conservaba
      su trayectoria tras tocar el medallón y podía morir en la pared sin
      estallar nunca (el vigilante de 3,2 s llegaba a veces tarde).
  (2) CAJONES DEL ORO JUNTO A LAS VENTANAS: x 1,35 → 2,45 m (pared ±3,05).
  (3) LINGOTES TUMBADOS: el GLB del artista trae la barra DE PIE (eje
      largo Y 6,32×13,80×3,06 — medido con inspecciona_glb_lingote.py):
      se tumba al montarla (cara ancha abajo) y la pila pasa a capas
      reales de ~0,038 m en vez de torres de 0,17 que se atraviesan.
  (4) SONIDOS DEL DUEÑO: tren_llegada.mp3 al frenar · vias.mp3 en bucle
      mientras el vagón se mueve · tunel.mp3 al entrar en el túnel ·
      caballos.mp3 por instancia (forajido / cada indio, desfasados),
      fundido progresivo en la fuga y corte brusco al abatir.

Estilo de la casa: cada sustitución con ancla ÚNICA verificada (== 1)."""

import io
import sys

F = "/home/z/my-project/public/championships/oeste/index.js"

EDITS = []


def edit(old, new, tag):
    EDITS.append((tag, old, new))


# ---------------------------------------------------------------- E1 cabecera
edit(
    """ *  v2.141 (módulo v48) · LOS CAJONES DEL ORO + PARADAS CON NOMBRE — ajustes""",
    """ *  v2.142 (módulo v49) · EL VAGÓN SUENA + CADENA INMEDIATA + CAJONES EN LA
 *      VENTANA — peticiones del dueño sobre la etapa 4: (1) CADENA DE LA
 *      DINAMITA INMEDIATA: al tocar la bola el medallón de dinamita SALE YA
 *      cazando la caja viva más cercana (tiro balístico) — la cadena de
 *      v2.134 (estalla, rebota y agota TODAS las cajas de la foto) arranca
 *      SIEMPRE, antes podía perderse si la bola moría sin estallar. (2)
 *      CAJONES DEL ORO JUNTO A LAS VENTANAS: x 1,35 → 2,45 m (pared ±3,05)
 *      — «ahora están muy cerca de la mesa y casi no se ven». (3) LINGOTES
 *      TUMBADOS: el GLB del artista trae la barra DE PIE (eje largo Y,
 *      6,32×13,80×3,06 medidos) — se tumba al montarla (eje largo → x,
 *      cara ancha abajo): pila realista de barras planas con capas de la
 *      altura REAL (~0,038 m) y holguras que no solapan. (4) SONIDOS DEL
 *      DUEÑO: tren_llegada.mp3 al REALIZAR LA PARADA (frenado) · vias.mp3
 *      EN BUCLE mientras el vagón SE MUEVE (volumen con la velocidad, cero
 *      en las paradas) · tunel.mp3 al ENTRAR en el túnel · caballos.mp3
 *      por INSTANCIA al aparecer el forajido o los indios (indios
 *      DESFAZADOS 0,45 s, paneo a su lado), fundido PROGRESIVO en la fuga
 *      y CORTE BRUSCO al abatir.
 *  v2.141 (módulo v48) · LOS CAJONES DEL ORO + PARADAS CON NOMBRE — ajustes""",
    "cabecera v2.142",
)

# ------------------------------------------------------------- E2 cajonOro x
edit(
    """   * (0,36). Uno a CADA LADO de la mesa, CERCA DEL CENTRO DE LAS VENTANAS
   * laterales (centros medidos sobre el arte 2395×864: izquierda u=0,472
   * → z -1,38 · derecha u=0,501 → z -1,59). En su cara superior (y = h)
   * se apilan los lingotes en rejilla 3×3 con capas EXACTAS y una
   * PEQUEÑA VARIACIÓN (jX/jZ/yaw) «para que no parezca tan perfecta» —
   * con holguras que NUNCA llegan a solapar (lingote 0,17×0,08). */
  cajonOro: {
    w: 0.72, h: 0.18, d: 0.36,   // doble de ancho · mitad de alto (cajón 0,36)
    x: 1.35,                     // entre la mesa (x ±0,76) y la pared (±3,05)""",
    """   * (0,36). Uno a CADA LADO de la mesa PEGADOS A LAS VENTANAS laterales
   * (v2.142: x 1,35 → 2,45 con la pared en ±3,05 — el dueño: «ahora están
   * muy cerca de la mesa y casi no se ven») a la altura de los CENTROS de
   * las ventanas (arte 2395×864: izquierda u=0,472 → z -1,38 · derecha
   * u=0,501 → z -1,59). En su cara superior (y = h) se apilan los
   * lingotes TUMBADOS (v2.142) en rejilla 3×3 con capas EXACTAS y una
   * PEQUEÑA VARIACIÓN (jX/jZ/yaw) «para que no parezca tan perfecta» —
   * con holguras que NUNCA llegan a solapar (lingote 0,17×0,078). */
  cajonOro: {
    w: 0.72, h: 0.18, d: 0.36,   // doble de ancho · mitad de alto (cajón 0,36)
    x: 2.45,                     // v2.142: junto a las ventanas (pared ±3,05)""",
    "cajonOro x 2,45",
)

# ----------------------------------------------------------- E3 GLB tumbado
edit(
    """          const s = 0.17 / (Math.max(sz.x, sz.y, sz.z) || 0.17);
          root.scale.setScalar(s);
          const wrap = new THREE.Group();""",
    """          const s = 0.17 / (Math.max(sz.x, sz.y, sz.z) || 0.17);
          root.scale.setScalar(s);
          /* v2.142 · EL GLB DEL ARTISTA TRAE LA BARRA DE PIE (eje largo en
           * Y: 6,32×13,80×3,06 medidos del propio fichero) — se TIUMBA al
           * montarla: eje largo → x y cara ANCHA del trapecio hacia abajo
           * (Rx(−π/2)·Rz(π/2)). Pila REALISTA del dueño: barras planas por
           * capas de la altura real, nunca torres que se atraviesan. */
          if (sz.y > sz.x && sz.y > sz.z) {
            root.rotation.set(-Math.PI / 2, 0, Math.PI / 2);
          }
          const wrap = new THREE.Group();""",
    "GLB barra tumbada",
)
edit(
    """          /* v2.140 · ALTURA REAL del lingote para el apilado EXACTO de la
           * pila (capas «unos perfectamente encima de otros»). */
          this._lingoteH = bb.getSize(new THREE.Vector3()).y + 0.0015;""",
    """          /* v2.140 · ALTURA REAL del lingote para el apilado EXACTO de la
           * pila (capas «unos perfectamente encima de otros»). v2.142:
           * tumbada mide ~0,038 m — capas DE VERDAD, no torres de 0,17. */
          this._lingoteH = bb.getSize(new THREE.Vector3()).y + 0.0015;""",
    "altura real comentada",
)

# ------------------------------------------------- E4 cadena dinámica inmediata
edit(
    """        e.mesh.material.color.setHex(0x181310);
        if (e.fuse) e.fuse.visible = true;
      }
    }
  }
  /** BOOM de la bola-bomba (v2.134 · CADENA): revienta el cajón impactado""",
    """        e.mesh.material.color.setHex(0x181310);
        if (e.fuse) e.fuse.visible = true;
      }
    }
    /* v2.142 · AL TOCAR EL MEDALLÓN la bola sale YA CAZANDO la caja viva
     * más cercana (tiro balístico) — antes conservaba SU trayectoria y
     * podía morir en la pared sin estallar nunca (la cadena de v2.134 se
     * perdía): la cadena ARRANCA SIEMPRE. */
    if (serie.rest.size > 0) this._bombaReapunta(b, serie);
  }
  /** BOOM de la bola-bomba (v2.134 · CADENA): revienta el cajón impactado""",
    "cadena inmediata",
)

# ------------------------------------------- E5 bloque de sonido (pre dispose)
edit(
    """      o1.onended = () => { try { g.disconnect(); } catch (e) { /* */ } };
    } catch (e) { /* el sonido nunca rompe el frame */ }
  }

  dispose() {""",
    """      o1.onended = () => { try { g.disconnect(); } catch (e) { /* */ } };
    } catch (e) { /* el sonido nunca rompe el frame */ }
  }

  /* ======================================================================
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

  dispose() {""",
    "bloque de sonido v2.142",
)

# ------------------------------------------------------------ E6 start hook
edit(
    """    this.loadRisasForajido();""",
    """    this.loadRisasForajido();
    this._sndTren();   // v2.142: precarga de los sonidos del recorrido""",
    "start _sndTren",
)

# ------------------------------------------------- E7 llegada a la estación
edit(
    """    this.phase = 'arrive';
    this._msg = tx('tren_llega');
    this._msgT = 3.2;
    this.ctrl.sfx('whistle', 0);
  }""",
    """    this.phase = 'arrive';
    this._msg = tx('tren_llega');
    this._msgT = 3.2;
    this.ctrl.sfx('whistle', 0);
    /* v2.142 · EL TREN REALIZA LA PARADA: frenado/llegada (mp3 del dueño) */
    try { this.__sfxSDK().play('tren_llegada.mp3', 0.8); } catch (e) { /* */ }
  }""",
    "tren_llegada al frenar",
)

# ------------------------------------------------------------ E8 túnel entra
edit(
    """      if (this._tunelZ >= TU.ojo + TU.bh / 2) {
        this._tunnelPhase = 'in';
        this._tunnelT2 = 0;
      }""",
    """      if (this._tunelZ >= TU.ojo + TU.bh / 2) {
        this._tunnelPhase = 'in';
        this._tunnelT2 = 0;
        /* v2.142 · ENTRAMOS EN EL TÚNEL (mp3 del dueño) */
        try { this.__sfxSDK().play('tunel.mp3', 0.7); } catch (e) { /* */ }
      }""",
    "tunel.mp3 al entrar",
)

# --------------------------------------------------------------- E9 vias set
edit(
    """    // rumor de la locomotora acorde a la velocidad
    this._setRumble(this.v / TREN.vMax);""",
    """    // rumor de la locomotora acorde a la velocidad
    this._setRumble(this.v / TREN.vMax);
    // v2.142 · ROCE DE VÍAS: mp3 del dueño EN BUCLE, volumen con la marcha
    this._viasSet(this.v / TREN.vMax);""",
    "vias por frame",
)

# ------------------------------------------------------------ E10 dispose
edit(
    """  dispose() {
    const g = this.game;
    this._stopRumble();""",
    """  dispose() {
    const g = this.game;
    this._stopRumble();
    this._viasStop();      // v2.142: fuera el roce de vías
    this._cabStopAll();    // v2.142: fuera los galopes""",
    "dispose sonidos",
)

# -------------------------------------------------------- E11 forajido hooks
edit(
    """    this._sndYihha();   // v2.113: ¡ALERTA! grito del jinete al acercarse
  }""",
    """    this._sndYihha();   // v2.113: ¡ALERTA! grito del jinete al acercarse
    this._cabStart('fj', this._fjSide, 0);   // v2.142: GALOPE del dueño
  }""",
    "forajido spawn galope",
)
edit(
    """  _fjHerido() {
    this.fjDiana.visible = false;
    this._fjState = 'herido';""",
    """  _fjHerido() {
    this.fjDiana.visible = false;
    this._cabStop('fj');   // v2.142: el galope CORTA DE GOLPE al abatirlo
    this._fjState = 'herido';""",
    "forajido herido corte",
)
edit(
    """  _fjFuga() {
    this._fjState = 'fuga';
    this._fjT = 0; this._fjFrame = 0; this._fjV = 1.2;
    this.fjDiana.visible = false;
    this._fjSetFrame('paso');
  }""",
    """  _fjFuga() {
    this._fjState = 'fuga';
    this._fjT = 0; this._fjFrame = 0; this._fjV = 1.2;
    this.fjDiana.visible = false;
    this._fjSetFrame('paso');
    this._cabFade('fj', 1.3);   // v2.142: se aleja — galope PROGRESIVO fuera
  }""",
    "forajido fuga fundido",
)
edit(
    """  _fjGone() {
    this.fj.visible = false;
    this.fjDiana.visible = false;
    this._fjState = 'off';""",
    """  _fjGone() {
    this.fj.visible = false;
    this.fjDiana.visible = false;
    this._fjState = 'off';
    this._cabFade('fj', 0.5);   // v2.142: fundido del galope al irse""",
    "forajido gone fundido",
)

# ----------------------------------------------------------- E12 indios hooks
edit(
    """      this._indPose(rec, 0);
      this._inds.push(rec);""",
    """      this._indPose(rec, 0);
      this._cabStart('ind' + k, side, k * 0.45);   // v2.142: UN galope por jinete, DESFASADOS
      this._inds.push(rec);""",
    "indios galopes desfasados",
)
edit(
    """  _indHerido(rec) {
    rec.diana.visible = false;
    rec.state = 'alcanzado';""",
    """  _indHerido(rec) {
    rec.diana.visible = false;
    this._cabStop('ind' + rec.k);   // v2.142: galope CORTA al abatirlo
    rec.state = 'alcanzado';""",
    "indio herido corte",
)
edit(
    """      if (rec.state === 'ida' || rec.state === 'ventana') {
        rec.state = 'fuga';
        rec.v = 1.2;
        rec.diana.visible = false;
      }""",
    """      if (rec.state === 'ida' || rec.state === 'ventana') {
        rec.state = 'fuga';
        rec.v = 1.2;
        rec.diana.visible = false;
        this._cabFade('ind' + rec.k, 1.3);   // v2.142: galope PROGRESIVO fuera
      }""",
    "indios fuga en andén",
)
edit(
    """  _indGoneAll() {
    for (const rec of this._inds) {
      rec.grp.visible = false;
      rec.diana.visible = false;
    }""",
    """  _indGoneAll() {
    for (const rec of this._inds) {
      rec.grp.visible = false;
      rec.diana.visible = false;
      this._cabFade('ind' + rec.k, 0.4);   // v2.142: fundido del galope
    }""",
    "indios gone fundido",
)
edit(
    """        if (rec.t >= I.atkT) {
          this._indDispara(rec);                // SIEMPRE dispara la flecha
          rec.state = 'fuga';
          rec.v = 1.2;
        }""",
    """        if (rec.t >= I.atkT) {
          this._indDispara(rec);                // SIEMPRE dispara la flecha
          rec.state = 'fuga';
          rec.v = 1.2;
          this._cabFade('ind' + rec.k, 1.3);   // v2.142: galope PROGRESIVO fuera
        }""",
    "indio fuga tras flecha",
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
    print(f"\n{len(EDITS)} ediciones aplicadas en {F}")


if __name__ == "__main__":
    main()
