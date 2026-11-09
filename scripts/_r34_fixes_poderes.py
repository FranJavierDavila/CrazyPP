#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r34 (v3.6.130, FASE 132) · CORRECCIONES A LOS SUPERPODERES DE PALA
(informe del dueño tras V3.6.129):

  A · BARRERA DE LA SÚPER RED DESALINEADA — «el efecto de electricidad
      sobre la red no está correctamente alineado con el plano de la red».
      Causa raíz: los FX de r25 (cuerpo/arcos/riel de la red, niebla/
      rayos/metales de la tormenta, anillo de bote del SÚPER EFECTO y
      sprites del portal) cuelgan de this.scene EN COORDENADAS DE MESA,
      pero la MESA vive dentro de this.rig — y onSessionStart gira el rig
      (updateRecenter, 25 frames) según hacia dónde mire el dueño al
      entrar en el visor. La r33 ya aprendió la lección (prisma: «¡espacio
      de la mesa, NO this.scene!»); ahora se repatriona TODO FX de mesa al
      rig. Mismas coordenadas, misma visibilidad: cero cambios de lógica.

  B · VOZ DEL SELECTOR PARA TODOS LOS PODERES — «todos los nuevos deben
      tener el audio disparador cuando se seleccionan (en inglés el poder
      de Fénix no tiene su audio)». Fénix/Crono/Oscuridad (r26b/r29)
      estaban FUERA del mapeo _vozSelFuente: el joystick los ciclaba en
      SILENCIO (los dos idiomas; el dueño lo cazó en EN). Entran con su
      voz de concesión (mismo patrón red/elec r25) + precaliente.

  C · SÚPER ELECTRICIDAD TERMINA CON LA BAJA — «si al aplicarlo en algún
      momento el rival pierde una bola, el superpoder se suspende y
      termina (la penalización no puede ser mayor de 1 bola perdida)».
      _elecRompe ahora cierra la tormenta al instante (_elecFin(true),
      sin pisar el mensaje del punto): máximo UNA bola perdida por
      activación; un nuevo gatillo puede reabrirla con otra carga.

  D · EL RAYO SE VÉ ALCANZAR LA BOLA — «no te enteras de que un rayo ha
      alcanzado la bola; más bien reforzar el efecto cuando existe
      alcance parando la bola 1 segundo con un halo de luz y pequeños
      rayos saliendo de ella antes de ser destruida». El impacto YA NO
      rompe al vuelo: _elecAgarra congela la bola con el ppTransito del
      portal (c04 no la integra, c05 no la golpea, el árbitro no ve un
      evento — FÍSICA INTACTA), la bola cuelga 1 s con halo de luz y 6
      mini-rayos saltando, y al agotarse ESTALLA (punto + fin por baja).
      Las salidas de emergencia (cortina 2/4, salida del partido, fin de
      ventana) LIBERAN el agarre en _elecFin — la bola nunca queda
      congelada para siempre (lección r28). El bloque del portal que
      oculta la bola en tránsito queda EXENTO durante el agarre.

  E · PRISMA SÓLO EN CAMPO RIVAL — «estaría bien que el jugador pudiese
      ver el efecto solo en el campo del rival para que no le molestase
      cuando la bola entra en nuestro campo». _trailFirmaPoder devuelve
      la firma arcoíris SOLO con la bola en la mitad rival (z < centro):
      en nuestro campo la estela vuelve al color de la skin (lerp suave
      del frame; los puntos ya nacidos se apagan solos en 0,42 s).

También: i18n arc_elec_caza ES/EN + constante ELEC_AGARRA_T.

Uso:  python3 scripts/_r34_fixes_poderes.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
C00 = RAIZ / 'src' / 'game' / 'core' / 'c00_pre_three.js'

EDITS_C12 = [
    # ── FIX A · ESPACIO DE LA MESA (rig) para todo FX de mesa ──────────
    # 1) cuerpo de la barrera de la SÚPER RED
    ("""    cuerpo.visible = false;
    cuerpo.renderOrder = 6;
    cuerpo.frustumCulled = false;
    this.scene.add(cuerpo);""",
     """    cuerpo.visible = false;
    cuerpo.renderOrder = 6;
    cuerpo.frustumCulled = false;
    // r34 (v3.6.130) · ESPACIO DE LA MESA (this.rig — patrón r33 de
    // prisma/oscuridad/onda): el recentrado del visor ROTA el rig y los
    // FX en this.scene quedaban DESALINEADOS del plano de la red (informe
    // del dueño). La red vive en el rig: la barrera también.
    this.rig.add(cuerpo);""", 1),
    # 2) arcos de la barrera
    ("""      ln.visible = false;
      ln.frustumCulled = false;
      ln.renderOrder = 7;
      ln.userData.vida = 0; ln.userData.f = i * 1.31;
      this.scene.add(ln);""",
     """      ln.visible = false;
      ln.frustumCulled = false;
      ln.renderOrder = 7;
      ln.userData.vida = 0; ln.userData.f = i * 1.31;
      this.rig.add(ln);   // r34: espacio de la mesa""", 1),
    # 3) riel superior
    ("""    riel.visible = false;
    riel.frustumCulled = false;
    riel.renderOrder = 8;
    riel.userData.vida = 1;
    this.scene.add(riel);""",
     """    riel.visible = false;
    riel.frustumCulled = false;
    riel.renderOrder = 8;
    riel.userData.vida = 1;
    this.rig.add(riel);   // r34: espacio de la mesa""", 1),
    # 4) niebla de la tormenta
    ("""      sp.renderOrder = 6;
      sp.visible = false;
      this.scene.add(sp);
      niebla.push(sp);""",
     """      sp.renderOrder = 6;
      sp.visible = false;
      // r34 (v3.6.130) · ESPACIO DE LA MESA (this.rig): la tormenta vive
      // sobre el campo del RIVAL de la mesa — con el recentrado del visor
      // quedaba rotada (misma causa raíz que la barrera desalineada).
      this.rig.add(sp);
      niebla.push(sp);""", 1),
    # 5) rayos de la tormenta
    ("""      ln.userData.vida = 0; ln.userData.f = i * 1.7;
      ln.renderOrder = 7;
      this.scene.add(ln);""",
     """      ln.userData.vida = 0; ln.userData.f = i * 1.7;
      ln.renderOrder = 7;
      this.rig.add(ln);   // r34: espacio de la mesa""", 1),
    # 6) pedacitos negros
    ("""      mt.visible = false;
      mt.userData = { vida: 0, vx: 0, vy: 0, vz: 0, rx: 0, ry: 0 };
      this.scene.add(mt);""",
     """      mt.visible = false;
      mt.userData = { vida: 0, vx: 0, vy: 0, vz: 0, rx: 0, ry: 0 };
      this.rig.add(mt);   // r34: espacio de la mesa""", 1),
    # 7) anillo de bote del SÚPER EFECTO
    ("""    this._efectoBoteFx.visible = false;
    this.scene.add(this._efectoBoteFx);""",
     """    this._efectoBoteFx.visible = false;
    this.rig.add(this._efectoBoteFx);   // r34: espacio de la mesa""", 1),
    # 8) sprites del portal del mundo
    ("""      sp.userData.ppVida = 0;
      this.scene.add(sp);
      return sp;""",
     """      sp.userData.ppVida = 0;
      this.rig.add(sp);   // r34: espacio de la mesa (Sprite: billboard propio)
      return sp;""", 1),

    # ── FIX B · VOZ DEL SELECTOR para fenix/crono/oscuridad ────────────
    ("""    // r33 · los 4 nuevos: sin voz corta propia — reutilizan la de concesión
    else if (id === 'prisma') par = [VOZ_PODER_PRISMA, VOZ_PODER_PRISMA_EN];""",
     """    // r34 (v3.6.130) · informe del dueño: «todos los nuevos deben tener
    // el audio disparador al seleccionarlos — en inglés el poder de Fénix
    // no tiene su audio». Fénix/Crono/Oscuridad (r26b/r29) no estaban en
    // el selector: el joystick los ciclaba EN SILENCIO. Entran con su voz
    // de concesión (mismo patrón red/elec de la r25).
    else if (id === 'fenix') par = [VOZ_PODER_FENIX, VOZ_PODER_FENIX_EN];
    else if (id === 'crono') par = [VOZ_PODER_CRONO, VOZ_PODER_CRONO_EN];
    else if (id === 'oscuridad') par = [VOZ_PODER_OSCURIDAD, VOZ_PODER_OSCURIDAD_EN];
    // r33 · los 4 nuevos: sin voz corta propia — reutilizan la de concesión
    else if (id === 'prisma') par = [VOZ_PODER_PRISMA, VOZ_PODER_PRISMA_EN];""", 1),
    ("""      const ids = ['mega', 'efecto', 'iman', 'portal', 'clon', 'nada', 'red', 'elec',
        'prisma', 'onda', 'salva', 'ancla'];   // r33: los 4 nuevos precalientan""",
     """      const ids = ['mega', 'efecto', 'iman', 'portal', 'clon', 'nada', 'red', 'elec',
        'fenix', 'crono', 'oscuridad',          // r34: el selector YA los habla
        'prisma', 'onda', 'salva', 'ancla'];   // r33: los 4 nuevos precalientan""", 1),

    # ── FIX C+D · constantes y estado de la RETENCIÓN ──────────────────
    ("""const ELEC_ATRAE_P = 0.25;  // probabilidad por rayo de modo ATRACTORA
const ELEC_ATRAE_COL = 0xd9c8ff; // tinte violeta del rayo cazador""",
     """const ELEC_ATRAE_P = 0.25;  // probabilidad por rayo de modo ATRACTORA
const ELEC_ATRAE_COL = 0xd9c8ff; // tinte violeta del rayo cazador
// r34 (v3.6.130) · RETENCIÓN DEL RAYO + FIN TRAS LA BAJA (informe del
// dueño: «no te enteras de que un rayo ha alcanzado la bola; más bien
// reforzar el efecto cuando existe alcance parando la bola 1 segundo
// con un halo de luz y pequeños rayos saliendo de ella antes de ser
// destruida» y «si al aplicarlo en algún momento el rival pierde una
// bola, el superpoder se suspende y termina — la penalización no puede
// ser mayor de 1 bola perdida»).
const ELEC_AGARRA_T = 1.0;  // s de retención visible antes del estallido""", 1),
    ("""    this._elecSegA = new THREE.Vector3();     // segmento rayo (reuso)
    this._elecSegB = new THREE.Vector3();""",
     """    this._elecSegA = new THREE.Vector3();     // segmento rayo (reuso)
    this._elecSegB = new THREE.Vector3();
    // r34 (v3.6.130) · RETENCIÓN del rayo: bola congelada 1 s (ppTransito
    // del portal — c04/c05 INTACTOS) con halo de luz y mini-rayos; al
    // agotarse ESTALLA, cae el punto y la TORMENTA TERMINA (máx. 1 bola
    // perdida por activación — fin por baja).
    this._elecAgarraT = 0;                     // s de retención restantes
    this._elecAgarraPos = new THREE.Vector3(); // punto de agarre (reuso)
    this._elecAgarraFx = null;                 // { halo, rayos[], cd }""", 1),

    # ── FIX D · el impacto AGARRA (no rompe al vuelo) ──────────────────
    ("""      const r = ELEC_BOLT_R + (D.ballRadius || 0.02);
      if (d2 <= r * r) this._elecRompe();""",
     """      const r = ELEC_BOLT_R + (D.ballRadius || 0.02);
      // r34 (v3.6.130) · el impacto YA NO rompe al vuelo: AGARRA la bola
      // (retención visible de 1 s con halo de luz y mini-rayos — Fix D
      // del dueño); el estallido llega al agotarse la retención.
      if (d2 <= r * r && this._elecAgarraT <= 0) this._elecAgarra();""", 1),

    # ── FIX D · métodos del agarre (antes de _elecRompe) ───────────────
    ("""  /** LA BOLA DEL RIVAL ESTALLA: pedacitos negros + PUNTO para el jugador
   *  por el cauce del árbitro (applyPoint — mismos intents y mensajes). */
  _elecRompe() {""",
     """  /** r34 (v3.6.130) · FX del AGARRE: halo de luz + 6 mini-rayos que
   *  saltan de la bola retenida (pool propio, cero asignaciones por
   *  frame — las posiciones se reciclan en _elecFrame). ESPACIO DE LA
   *  MESA (this.rig — patrón r33: el recentrado rota el rig). */
  _buildElecAgarraFx() {
    if (this._elecAgarraFx) return;
    const cv = document.createElement('canvas');
    cv.width = cv.height = 128;
    const c2 = cv.getContext('2d');
    if (c2) {
      const gR = c2.createRadialGradient(64, 64, 6, 64, 64, 62);
      gR.addColorStop(0, 'rgba(235,248,255,0.95)');
      gR.addColorStop(0.4, 'rgba(170,220,255,0.5)');
      gR.addColorStop(1, 'rgba(120,180,255,0)');
      c2.fillStyle = gR;
      c2.fillRect(0, 0, 128, 128);
    }
    const tex = new THREE.CanvasTexture(cv);
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: tex, transparent: true, opacity: 0, depthWrite: false,
      blending: THREE.AdditiveBlending,
    }));
    halo.renderOrder = 66;
    halo.visible = false;
    halo.frustumCulled = false;
    this.rig.add(halo);           // ¡espacio de la mesa, NO this.scene!
    const rayos = [];
    for (let i = 0; i < 6; i++) {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position',
        new THREE.BufferAttribute(new Float32Array(2 * 3), 3));
      const mat = new THREE.LineBasicMaterial({
        color: 0xbfe4ff, transparent: true, opacity: 0.8,
        blending: THREE.AdditiveBlending, depthWrite: false,
      });
      const ln = new THREE.Line(geo, mat);
      ln.visible = false;
      ln.frustumCulled = false;
      ln.renderOrder = 67;
      this.rig.add(ln);           // ¡espacio de la mesa!
      rayos.push(ln);
    }
    this._elecAgarraFx = { halo, rayos, cd: 0 };
  }

  /** r34 · apaga el FX del agarre (halo y mini-rayos fuera). */
  _elecAgarraFxOff() {
    const fx = this._elecAgarraFx;
    if (!fx) return;
    if (fx.halo) fx.halo.visible = false;
    for (const r2 of fx.rayos) r2.visible = false;
  }

  /** r34 (v3.6.130) · EL RAYO AGARRA LA BOLA (informe del dueño: «no te
   *  enteras de que un rayo ha alcanzado la bola… parando la bola 1
   *  segundo con un halo de luz y pequeños rayos saliendo de ella antes
   *  de ser destruida»): se congela con el ppTransito del PORTAL (c04 no
   *  la integra, c05 no la golpea, el árbitro no ve un evento — física
   *  INTACTA), cuelga VISTA con su halo y al agotarse el segundo estalla
   *  en _elecFrame → _elecRompe. */
  _elecAgarra() {
    const b = this.ball;
    if (!b || this._elecAgarraT > 0) return;    // ya agarrada: UNA vez
    this._elecAgarraPos.copy(b.pos);
    b.vel.set(0, 0, 0);                          // congelada
    b.ppTransito = true;
    if (this.ballMesh) this.ballMesh.visible = true;
    this._elecAgarraT = ELEC_AGARRA_T;
    try { this._buildElecAgarraFx(); } catch (eA34) { this._elecAgarraFx = null; }
    const fx = this._elecAgarraFx;
    if (fx) {
      if (fx.halo) {
        fx.halo.position.copy(this._elecAgarraPos);
        fx.halo.visible = true;
      }
      for (const r2 of fx.rayos) r2.visible = true;
    }
    // firma sonora de la caza: zumbido ascendente + crujido seco
    try { this.audio.playOsc(220, 880, 0.5, 'sawtooth', 0.10, 0); } catch (eS34) { /* */ }
    try { this.audio.playOsc(1500, 500, 0.16, 'square', 0.08, 0.02); } catch (eS35) { /* */ }
    this._elecFlashT = 0.25;
    try { this.rules.message = T('arc_elec_caza'); } catch (eM34) { /* */ }
    if (this.renderer.xr && this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.6, 120); } catch (eH34) { /* */ }
    }
  }

  /** LA BOLA DEL RIVAL ESTALLA: pedacitos negros + PUNTO para el jugador
   *  por el cauce del árbitro (applyPoint — mismos intents y mensajes). */
  _elecRompe() {""", 1),

    # ── FIX C+D · _elecRompe: suelta la bola, sin hide, y CIERRA ───────
    ("""    // v3.6.124 (r28) · SOLO se oculta si la bola está VOLANDO (informe
    // del dueño: con el rival sacando, la bola «no se veía… imposibilita
    // el juego»). Bola quieta o preparando un saque = estallido visual
    // + punto del árbitro SIN ocultarla (nada que "revivir" después).
    const vR28 = (this.ball && this.ball.vel) || null;
    const volandoR28 = !vR28 ||
      (Math.abs(vR28.x) + Math.abs(vR28.y) + Math.abs(vR28.z)) > 0.5;
    if (volandoR28) {
      if (this.ballMesh) this.ballMesh.visible = false;   // estalló
      if (this.trailObj) this.trailObj.visible = false;
      this._elecRotoT = 0.9;
    } else {
      this._elecRotoT = 0;   // bola quieta (saque): visible y al asunto
    }""",
     """    // r34 (v3.6.130) · SIN ocultamiento: la tormenta TERMINA con la baja
    // (petición del dueño: «el superpoder se suspende y termina — la
    // penalización no puede ser mayor de 1 bola perdida») y la bola sale
    // del agarre para caer MUERTA y VISIBLE (patrón de punto normal: el
    // árbitro ya decidió y la bola vuela de adorno). El hide+revive del
    // r28 vivía del ciclo CONTINUADO de la tormenta: tras un estallido ya
    // no hay más ciclo — nada que "revivir", nada que ocultar (el saque
    // del rival sigue indemne: bola quieta nunca llegó a ocultarse).
    try { this._elecAgarraFxOff(); } catch (eRl34) { /* */ }
    this._elecAgarraT = 0;
    if (this.ball) this.ball.ppTransito = false;""", 1),
    ("""    // PUNTO por el cauce del árbitro (intents 'point' de siempre)
    try {
      this.processIntents(this.rules.applyPoint('player', 'elec'));
    } catch (eP) { /* */ }
  }""",
     """    // PUNTO por el cauce del árbitro (intents 'point' de siempre)
    try {
      this.processIntents(this.rules.applyPoint('player', 'elec'));
    } catch (eP) { /* */ }
    // r34 (v3.6.130) · FIN POR BAJA (petición del dueño: «si al aplicarlo
    // en algún momento el rival pierde una bola, el superpoder se suspende
    // y termina — la penalización no puede ser mayor de 1 bola perdida»):
    // la tormenta SE DISIPA al instante y SIN mensaje propio (el del
    // punto debe verse); un nuevo gatillo puede reabrirla con otra carga.
    try { this._elecFin(true); } catch (eF34) { /* */ }
  }""", 1),

    # ── FIX D · _elecFin libera el agarre + porBaja ────────────────────
    ("""  /** Fin de la tormenta: luces y fondo EXACTOS de vuelta, FX fuera. */
  _elecFin() {
    this._elecT = 0;""",
     """  /** Fin de la tormenta: luces y fondo EXACTOS de vuelta, FX fuera.
   *  r34 (v3.6.130) · porBaja=true cuando el fin llega POR ESTALLAR la
   *  bola (no pisa el mensaje del punto). Toda salida LIBERA el AGARRE
   *  si la tormenta muere con la bola retenida (cortina etapas 2/4,
   *  salida del partido, fin de ventana): la bola viva cae — nunca
   *  congelada para siempre (lección r28). */
  _elecFin(porBaja) {
    if (this._elecAgarraT > 0) {
      this._elecAgarraT = 0;
      try { this._elecAgarraFxOff(); } catch (eRl35) { /* */ }
      try {
        if (this.ball) {
          this.ball.ppTransito = false;
          this.ball.vel.set(0, 0, 0);
        }
        if (this.ballMesh) this.ballMesh.visible = true;
      } catch (eRl36) { /* */ }
    }
    this._elecT = 0;""", 1),
    ("""    this.rules.message = T('arc_elec_fin');""",
     """    if (!porBaja) this.rules.message = T('arc_elec_fin');   // r34: la baja no pisa el punto""", 1),

    # ── FIX D · _elecFrame: el segundo de retención, vivo ──────────────
    ("""    this._elecLuces(k, this._elecFlashT > 0 ? this._elecFlashT / 0.25 : 0);
    if (this._elecFlashT > 0) this._elecFlashT -= dt;
    const fx = this._elecFx;""",
     """    this._elecLuces(k, this._elecFlashT > 0 ? this._elecFlashT / 0.25 : 0);
    if (this._elecFlashT > 0) this._elecFlashT -= dt;
    // r34 (v3.6.130) · RETENCIÓN viva (informe del dueño: «parando la
    // bola 1 segundo con un halo de luz y pequeños rayos saliendo de
    // ella antes de ser destruida»): la bola cuelga CONGELADA (ppTransito
    // — c04 ni la integra, c05 no la golpea), el halo late y los
    // mini-rayos saltan; al agotarse el segundo, ESTALLA (punto por el
    // árbitro + FIN de la tormenta — máx. 1 bola perdida por activación).
    if (this._elecAgarraT > 0) {
      this._elecAgarraT -= dt;
      if (this.ball) {
        this.ball.pos.copy(this._elecAgarraPos);
        this.ball.vel.set(0, 0, 0);
      }
      const fxA = this._elecAgarraFx;
      if (fxA) {
        const ttA = performance.now() * 0.001;
        if (fxA.halo.visible) {
          fxA.halo.position.copy(this._elecAgarraPos);
          const plA = 0.78 + 0.22 * Math.sin(ttA * 9.0);
          fxA.halo.material.opacity = 0.9 * plA;
          const esA = 0.30 + 0.06 * Math.sin(ttA * 7.3);
          fxA.halo.scale.set(esA, esA, 1);
        }
        fxA.cd -= dt;
        if (fxA.cd <= 0) {
          fxA.cd = 0.055;
          for (const rA of fxA.rayos) {
            const aA = Math.random() * Math.PI * 2;
            const lA = 0.07 + Math.random() * 0.10;
            const pA = rA.geometry.attributes.position;
            pA.setXYZ(0, this._elecAgarraPos.x, this._elecAgarraPos.y,
              this._elecAgarraPos.z);
            pA.setXYZ(1,
              this._elecAgarraPos.x + Math.cos(aA) * lA,
              this._elecAgarraPos.y + (Math.random() * 2 - 1) * lA * 0.7,
              this._elecAgarraPos.z + Math.sin(aA) * lA);
            pA.needsUpdate = true;
            rA.material.opacity = 0.45 + Math.random() * 0.55;
          }
        }
      }
      if (this._elecAgarraT <= 0) {
        try { this._elecRompe(); } catch (eR34) { /* */ }
        return;           // la tormenta terminó DENTRO de _elecRompe
      }
    }
    const fx = this._elecFx;""", 1),

    # ── FIX D · el tránsito del portal NO oculta la bola agarrada ──────
    ("""    } else if (this.ball && this.ball.ppTransito && this.ballMesh) {
      this.ballMesh.visible = false;                          // viaje oculto
    }""",
     """    } else if (this.ball && this.ball.ppTransito &&
               this._elecAgarraT <= 0 && this.ballMesh) {
      this.ballMesh.visible = false;    // viaje oculto (r34: el AGARRE de
      // la SÚPER ELECTRICIDAD mantiene la bola VISTA mientras cuelga)
    }""", 1),

    # ── FIX E · Prisma: arcoíris sólo en el campo del rival ────────────
    ("""    if (this._megaActivaId === 'prisma') return TRAIL_PODER.prisma; // r33""",
     """    if (this._megaActivaId === 'prisma') {
      // r34 (v3.6.130) · petición del dueño: el arcoíris SÓLO se ve en el
      // campo del RIVAL — cuando la bola entra en NUESTRO campo la estela
      // vuelve al color de la skin (el efecto no molesta en casa). El
      // lerp del frame (kT = dt·6) suaviza el tránsito y los puntos ya
      // nacidos se apagan solos (color por vértice, vida 0,42 s).
      const enCampoRival = this.ball && this.ball.pos.z < DIMS.tableCenterZ;
      if (!enCampoRival) return null;
      return TRAIL_PODER.prisma;
    }""", 1),
]

EDITS_C00 = [
    # i18n ES
    ("""    arc_elec_fin: 'la tormenta se disipa',
    poder_elec: '¡POTENCIADOR DE SÚPER ELECTRICIDAD!',""",
     """    arc_elec_fin: 'la tormenta se disipa',
    // r34 (v3.6.130) · el rayo ALCANZA la bola: retención visible de 1 s
    arc_elec_caza: '¡ALCANZADA! · el rayo retiene la bola',
    poder_elec: '¡POTENCIADOR DE SÚPER ELECTRICIDAD!',""", 1),
    # i18n EN
    ("""    arc_elec_fin: 'the storm clears',
    poder_elec: 'SUPER ELECTRICITY BOOSTER!',""",
     """    arc_elec_fin: 'the storm clears',
    // r34 (v3.6.130) · the bolt CATCHES the ball: 1 s visible hold
    arc_elec_caza: 'CAUGHT! · the bolt holds the ball',
    poder_elec: 'SUPER ELECTRICITY BOOSTER!',""", 1),
]


def aplica(ruta, edits, etiqueta):
    txt = ruta.read_text(encoding='utf-8')
    total = 0
    for viejo, nuevo, esperado in edits:
        n = txt.count(viejo)
        if n != esperado:
            raise SystemExit(
                f'ABORTA ({etiqueta}): ancla con {n} apariciones '
                f'(esperadas {esperado}):\n---\n{viejo[:160]}\n---')
        txt = txt.replace(viejo, nuevo)
        total += 1
    ruta.write_text(txt, encoding='utf-8')
    print(f'✓ {etiqueta}: {total} ediciones aplicadas '
          f'({ruta.stat().st_size:,} B)')


if __name__ == '__main__':
    aplica(C12, EDITS_C12, 'c12_pingponggame.js')
    aplica(C00, EDITS_C00, 'c00_pre_three.js')
    print('\nr34 · parche completo. Siguiente:')
    print('  python3 scripts/build_game.py          (ensayo)')
    print('  python3 scripts/bump_version.py 3.6.130-SDK6 --fase 132')
