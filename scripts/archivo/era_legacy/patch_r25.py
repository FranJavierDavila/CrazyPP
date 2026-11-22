#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · r25 (v3.6.120-SDK6) · PATCH DE CÓDIGO.

Ronda del informe del dueño:
  A · Los superpoderes de pala JAMÁS aparecen en las etapas 2 y 4 de los
      campeonatos (pruebas de habilidad) — cortina total.
  B · SÚPER RED (SuperPala_Red.png, 6.º poder): la red crece AL DOBLE de
      su altura durante 10 s (DIMS.netTopY muta en vivo — física, IA y
      saque la leen; visual re-acomodado patrón relayoutMesa r95).
  C · SÚPER ELECTRICIDAD (SuperPala_Electrica.png, 7.º poder): tormenta
      sobre el campo rival 10 s — nubes a 1,5 m, rayos con trueno y
      destello, escena casi nocturna; si un rayo intercepta la bola del
      rival (colisión rápida punto-segmento), se rompe en pedacitos
      negros y pierde el punto (cauce del árbitro, causa 'elec').
  D · CONTROL TOTAL de la bola online (_bolaGuard): propiedad re-afirmada
      CADA FRAME desde el árbitro — la bola SIEMPRE visible en poder del
      sacador; guardia anti-NaN/anti-mundo en rallye; HELD re-armado.
      c04/c05/c09 INTACTOS (garantía de la casa).

Anclajes EXACTOS: si uno no se encuentra, el script ABORTA sin escribir.
"""
import json
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
C00 = RAIZ / 'src' / 'game' / 'core' / 'c00_pre_three.js'
DATA = Path('/home/z/my-project/scripts/r25_assets/r25_datauri.json')

DURIS = json.loads(DATA.read_text())


def parchea(ruta, ediciones):
    src = ruta.read_text()
    for i, (viejo, nuevo, tag) in enumerate(ediciones):
        n = src.count(viejo)
        if n != 1:
            print(f'✗ ANCLA {i} ({tag}): {n} apariciones (se espera 1) en {ruta.name}')
            sys.exit(1)
        src = src.replace(viejo, nuevo)
    ruta.write_text(src)
    print(f'✓ {ruta.name}: {len(ediciones)} ediciones aplicadas')


# ---------------------------------------------------------------- c12 ----
ASSETS = f"""/* =====================================================================
 *  r25 (v3.6.120) · SÚPER RED + SÚPER ELECTRICIDAD (6.º y 7.º poder del
 *  registro; petición del dueño). Iconos PNG DEL DUEÑO (SuperPala_Red /
 *  SuperPala_Electrica, cuantizados a 256 colores — 19/26 KB) + voces
 *  ES/EN (espeak-ng → MP3 embebido, mismo patrón data-URI de las voces
 *  de concesión) + DOS truenos sintetizados (ffmpeg brown noise) que la
 *  tormenta alterna. Cero peticiones de red: todo viaja dentro del HTML.
 *  ===================================================================== */
const PNG_PODER_RED = '{DURIS["SuperPala_Red_opt"]}';
const VOZ_PODER_RED = '{DURIS["voz_red_es"]}';
const VOZ_PODER_RED_EN = '{DURIS["voz_red_en"]}';
const PNG_PODER_ELEC = '{DURIS["SuperPala_Electrica_opt"]}';
const VOZ_PODER_ELEC = '{DURIS["voz_elec_es"]}';
const VOZ_PODER_ELEC_EN = '{DURIS["voz_elec_en"]}';
const AUDIO_TRUENO_A = '{DURIS["trueno_a"]}';
const AUDIO_TRUENO_B = '{DURIS["trueno_b"]}';

"""

CAT_ENTRIES = """  // r25 (v3.6.120) · SÚPER RED (sexto poder; spec literal del dueño):
  // «al activarlo hace crecer la altura de la red el doble del valor
  // actual, este superpoder dura activo 10 segundos». La red MUTA
  // DIMS.netTopY (física c04/c05, IA y saque la leen EN VIVO — la
  // lección r95: una sola fuente de verdad) y el visual se re-acomoda
  // con el patrón relayoutMesa (plano, cinta y postes). Al acabar,
  // la red vuelve EXACTA a su altura reglamentaria.
  { id: 'red', nombre: () => T('poder_red'),
    voz: VOZ_PODER_RED, vozEn: VOZ_PODER_RED_EN, png: PNG_PODER_RED },
  // r25 (v3.6.120) · SÚPER ELECTRICIDAD (séptimo poder; spec literal del
  // dueño): «de la bola salen rayos de electricidad… nubes a metro y
  // medio sobre la mesa del rival que descargan rayos sobre su parte de
  // la mesa con gran estruendo sonoro y destello… la luz de la escena se
  // vuelve bastante oscura (casi parece de noche)… si alguno de los
  // rayos intercepta la bola del rival, la rompe en múltiples pedacitos
  // negros y pierde el punto». Física c04/c05 INTACTA: el punto lo
  // aplica el árbitro (applyPoint causa 'elec') y la bola rota sólo se
  // oculta — nunca se toca el integrador.
  { id: 'elec', nombre: () => T('poder_elec'),
    voz: VOZ_PODER_ELEC, vozEn: VOZ_PODER_ELEC_EN, png: PNG_PODER_ELEC },
"""

DURACIONES = """// r25 (v3.6.120) · los DOS poderes nuevos (regla de la casa del dueño:
// ventanas de 10 s — patrón efecto/iman/portal/clon — y tope ×3 igual).
const RED_DUR = 10;         // s de red alta
const RED_MUL = 2;          // «el doble del valor actual» (spec literal)
const ELEC_DUR = 10;        // s de tormenta sobre el campo del rival
const ELEC_BOLT_CD = 1.15;  // s entre rayos (≈8-9 descargas por ventana)
const ELEC_BOLT_R = 0.17;   // radio de interceptación rayo↔bola (m) —
                            // colisión RÁPIDA: distancia punto-segmento
                            // (un hipot, cero asignaciones) < bola+margen
const ELEC_ALTO_NUBE = 1.5; // m sobre la mesa del rival (spec literal)
const ELEC_NEGRO = new THREE.Color(0x05070c);   // noche de la tormenta
"""

EDICIONES_C12 = [
    # 0 · consts de assets (PNG + voces + truenos) antes del registro
    ("""const PODERES_PALA = [""",
     ASSETS + """const PODERES_PALA = [""", 'consts-assets'),

    # 1 · entradas del registro (tras clon, antes del cierre ])
    ("""  { id: 'clon', nombre: () => T('poder_clon'),
    voz: VOZ_PODER_CLON, vozEn: VOZ_PODER_CLON_EN, png: PNG_PODER_CLON },
];""",
     """  { id: 'clon', nombre: () => T('poder_clon'),
    voz: VOZ_PODER_CLON, vozEn: VOZ_PODER_CLON_EN, png: PNG_PODER_CLON },
""" + CAT_ENTRIES + """];""", 'registro-7-poderes'),

    # 2 · duraciones/constantes tras MEGA_GOLPES
    ("""const MEGA_GOLPES = 20; // cada 20 toques del rally = +1 carga (r56: regla
                        // del dueño — «superados los 20 toques, no antes»)""",
     """const MEGA_GOLPES = 20; // cada 20 toques del rally = +1 carga (r56: regla
                        // del dueño — «superados los 20 toques, no antes»)
""" + DURACIONES, 'constantes-red-elec'),

    # 3 · firma de estela
    ("""  clon: [0.42, 0.72, 1.0],      // Clonación — azul fantasma (r58)
};""",
     """  clon: [0.42, 0.72, 1.0],      // Clonación — azul fantasma (r58)
  red: [0.36, 0.62, 0.98],      // Súper Red — azul red del icono (r25)
  elec: [0.62, 0.85, 1.0],      // Súper Electricidad — azul rayo (r25)
};""", 'trail-poder'),

    # 4 · estado del constructor
    ("""    this._megaPngs = {};              // Images por poder (async)""",
     """    // r25 (v3.6.120) · SÚPER RED: ventana de 10 s con la red AL DOBLE.
    this._redT = 0;
    this._redWarn = false;
    this._redTickN = 0;
    this._redNetH0 = 0;             // altura reglamentaria capturada (m)
    // r25 (v3.6.120) · SÚPER ELECTRICIDAD: tormenta sobre el campo rival.
    this._elecT = 0;
    this._elecWarn = false;
    this._elecTickN = 0;
    this._elecBoltCd = 0;           // cuenta atrás del próximo rayo
    this._elecFlashT = 0;           // destello vivo (s)
    this._elecRotoT = 0;            // bola rota: oculta mientras (s)
    this._elecThunderIx = 0;        // alterna los dos truenos
    this._elecBase = null;          // luces capturadas al activar
    this._elecFx = null;            // { nubes[], rayos[], rayosIx, metales[] }
    this._elecFxOn = false;
    this._elecTarget = new THREE.Vector3();   // objetivo del rayo (reuso)
    this._elecSegA = new THREE.Vector3();     // segmento rayo (reuso)
    this._elecSegB = new THREE.Vector3();
    // r25 (v3.6.120) · GUARDIÁN DE LA BOLA (control total online): el
    // dueño tras las partidas reales — «en algún saque no se ve la bola
    // hasta que se lanza… vemos la bola en la mano del rival cuando
    // debería estar en la nuestra, o incluso no vemos la bola ninguno».
    // La propiedad se re-afirma CADA FRAME desde el árbitro.
    this._bgHold = false;           // este frame la guardia sujeta la bola
    this._bgRival = 0;              // s sin pose fresca del rival (saque)
    this._bgTeleT = 0;              // telemetría acelerada (1/5 s)
    this._megaPngs = {};              // Images por poder (async)""", 'estado'),

    # 5 · detector de pruebas (antes de megaEnabled) + gate en megaEnabled
    ("""  megaEnabled() {
    if (this.palaMejorada === false) return false;
    return !!(this.champs && this.champs.active);
  }""",
     """  /** r25 (v3.6.120) · ¿PRUEBA DE HABILIDAD en marcha? — las etapas 2 y
   *  4 de TODOS los campeonatos (asedio, arkanoid, orbes, dianas, tren,
   *  reactor, escudo) son pruebas puras: los superpoderes de pala JAMÁS
   *  aparecen allí (reporte del dueño). Todos los módulos exponen el
   *  gancho testActive() — el ChampLoader ya lo consulta. */
  _poderesEnPrueba() {
    try {
      return !!(this.champs && this.champs.active && this.champs.testActive);
    } catch (ePP) { return false; }
  }

  megaEnabled() {
    if (this.palaMejorada === false) return false;
    // r25 (v3.6.120) · etapas 2/4: ni gatillo, ni carga, ni icono.
    if (this._poderesEnPrueba()) return false;
    return !!(this.champs && this.champs.active);
  }""", 'mega-enabled'),

    # 6 · _megaCharge: sin concesiones en pruebas
    ("""  _megaCharge() {
    const ids = PODERES_PALA.map((p) => p.id);""",
     """  _megaCharge() {
    if (this._poderesEnPrueba()) return;   // r25: etapas 2/4 sin cargas
    const ids = PODERES_PALA.map((p) => p.id);""", 'carga-gate'),

    # 7 · despacho del gatillo
    ("""    if (ent.id === 'clon') return this._clonTrigger(ent);   // v3.6.50 (r58)
    if (this._megaT > 0) {""",
     """    if (ent.id === 'clon') return this._clonTrigger(ent);   // v3.6.50 (r58)
    if (ent.id === 'red') return this._redTrigger(ent);     // v3.6.120 (r25)
    if (ent.id === 'elec') return this._elecTrigger(ent);   // v3.6.120 (r25)
    if (this._megaT > 0) {""", 'despacho-gatillo'),

    # 8 · _megaSelActiva
    ("""    if (ent.id === 'clon') return this._clonT > 0;   // v3.6.50 (r58)
    return false;
  }""",
     """    if (ent.id === 'clon') return this._clonT > 0;   // v3.6.50 (r58)
    if (ent.id === 'red') return this._redT > 0;     // v3.6.120 (r25)
    if (ent.id === 'elec') return this._elecT > 0;   // v3.6.120 (r25)
    return false;
  }""", 'sel-activa'),

    # 9 · _megaActivaRest
    ("""    if (this._megaActivaId === 'clon') return this._clonT;   // v3.6.50 (r58)
    return 0;
  }""",
     """    if (this._megaActivaId === 'clon') return this._clonT;   // v3.6.50 (r58)
    if (this._megaActivaId === 'red') return this._redT;     // v3.6.120 (r25)
    if (this._megaActivaId === 'elec') return this._elecT;   // v3.6.120 (r25)
    return 0;
  }""", 'activa-rest'),

    # 10 · _trailFirmaPoder
    ("""    if (this._megaActivaId === 'clon') return TRAIL_PODER.clon;
    return null;
  }""",
     """    if (this._megaActivaId === 'clon') return TRAIL_PODER.clon;
    if (this._megaActivaId === 'red') return TRAIL_PODER.red;     // r25
    if (this._megaActivaId === 'elec') return TRAIL_PODER.elec;   // r25
    return null;
  }""", 'trail-firma'),

    # 11 · bloque GRANDE de métodos r25 (tras _buildImanFx)
    ("""  _buildImanFx() { /* v3.6.46: canto del imán RETIRADO (pala limpia + metálica) */ }""",
     """  _buildImanFx() { /* v3.6.46: canto del imán RETIRADO (pala limpia + metálica) */ }

  /* =====================================================================
   *  r25 (v3.6.120) · SÚPER RED (6.º poder; spec literal del dueño):
   *  «al activarlo hace crecer la altura de la red el doble del valor
   *  actual, este superpoder dura activo 10 segundos». Ventana propia
   *  (patrón imán r57): refresco honesto si ya corre, gasto y arranque
   *  si no. La red MUTA DIMS.netTopY y el visual se re-acomoda vivo.
   *  ===================================================================== */
  _redTrigger(ent) {
    if (this._redT > 0) {
      // refresco honesto (patrón imán r57): la ventana vuelve a 10 s
      this._redT = RED_DUR;
      this._redWarn = false;
      this._redTickN = 0;
      this._megaActivaId = 'red';
      this._megaActivaDur = RED_DUR;
      this._megaTexDirty = true;
      this.rules.message = T('arc_red_go');
      return true;
    }
    if (!this._megaMatriz.find((x) => x.id === 'red')) return false;
    this._megaGasta(ent);
    this._redT = RED_DUR;
    this._redWarn = false;
    this._redTickN = 0;
    this._megaActivaId = 'red';
    this._megaActivaDur = RED_DUR;
    this._megaTexDirty = true;
    this._redCrecer();
    // firma sonora «red tensada»: dos voces ascendentes (triangle)
    try { this.audio.playOsc(220, 440, 0.18, 'triangle', 0.14, 0); } catch (e) { /* */ }
    try {
      window.setTimeout(() => {
        try { if (!this.disposed) this.audio.playOsc(440, 660, 0.16, 'triangle', 0.10, 0); } catch (e2) { /* */ }
      }, 120);
    } catch (e) { /* */ }
    this.rules.message = T('arc_red_go');
    if (this.renderer.xr && this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.7, 160); } catch (e2) { /* */ }
    }
    return true;
  }

  /** La red crece ×2: registra la altura de nacimiento del visual y muta
   *  DIMS.netTopY (física, IA y saque la leen EN VIVO — lección r95). */
  _redCrecer() {
    const D = DIMS;
    const h0 = Math.max(0.05,
      (D.netTopY != null ? D.netTopY : D.tableTopY + 0.1525) - D.tableTopY);
    this._redNetH0 = h0;
    const g = this.tableGroup;
    if (g) {
      for (const m of g.children) {
        if ((m.name === 'ppTableNet' || m.name === 'ppTablePost') &&
            !(m.userData && m.userData.h0)) {
          if (!m.userData) m.userData = {};
          m.userData.h0 = h0;          // altura de nacimiento (UNA vez)
        }
      }
    }
    D.netTopY = D.tableTopY + h0 * RED_MUL;
    this._redNetFit();
  }

  /** Re-acomoda la red VIVA a la altura vigente (patrón relayoutMesa
   *  r95): plano estirado contra su altura de nacimiento, cinta arriba
   *  y postes crecidos. Cero dispose — los objetos son los de siempre. */
  _redNetFit() {
    const D = DIMS;
    const topY = D.tableTopY;
    const netH = (D.netTopY != null ? D.netTopY - topY : 0.1525);
    const g = this.tableGroup;
    if (!g) return;
    for (const m of g.children) {
      if (m.name === 'ppTableNet') {
        const h0 = (m.userData && m.userData.h0) || Math.max(0.05, netH / RED_MUL);
        m.scale.y = netH / h0;
        m.position.y = topY + netH / 2;
      } else if (m.name === 'ppTableBand') {
        m.position.y = topY + netH;
      } else if (m.name === 'ppTablePost') {
        const h0 = (m.userData && m.userData.h0) || Math.max(0.05, netH / RED_MUL);
        m.scale.y = netH / h0;
        m.position.y = topY + netH / 2;
      }
    }
  }

  /** La red vuelve EXACTA a su altura reglamentaria. */
  _redRestaurar() {
    if (this._redNetH0 > 0) {
      DIMS.netTopY = DIMS.tableTopY + this._redNetH0;
      this._redNetH0 = 0;
      this._redNetFit();
    }
  }

  /** Fin de la SÚPER RED (los 10 s agotados). */
  _redFin() {
    this._redT = 0;
    this._redWarn = false;
    this._redTickN = 0;
    this._redRestaurar();
    this.rules.message = T('arc_red_fin');
    try { this.audio.playOsc(520, 260, 0.16, 'triangle', 0.12, 0); } catch (e) { /* */ }
  }

  /* =====================================================================
   *  r25 (v3.6.120) · SÚPER ELECTRICIDAD (7.º poder; spec literal del
   *  dueño) — la TORMENTA. Nubes a 1,5 m sobre la mesa del rival, rayos
   *  con trueno y destello, escena casi nocturna, colisión rápida
   *  punto-segmento contra la bola del rival: estalla en pedacitos
   *  negros y el punto es del jugador (cauce del árbitro, causa 'elec').
   *  Cero PointLights nuevos (lección v2.92: recompilan shaders y
   *  congelan el frame) — la noche y el destello van SOBRE las luces
   *  vivas del tema (hemi/dir/spot/env/fondo-niebla capturados).
   *  ===================================================================== */
  _elecTrigger(ent) {
    if (this._elecT > 0) {
      // refresco honesto: la tormenta vuelve a 10 s
      this._elecT = ELEC_DUR;
      this._elecWarn = false;
      this._elecTickN = 0;
      this._megaActivaId = 'elec';
      this._megaActivaDur = ELEC_DUR;
      this._megaTexDirty = true;
      this.rules.message = T('arc_elec_go');
      return true;
    }
    if (!this._megaMatriz.find((x) => x.id === 'elec')) return false;
    this._megaGasta(ent);
    this._elecT = ELEC_DUR;
    this._elecWarn = false;
    this._elecTickN = 0;
    this._elecBoltCd = 0.45;          // primera descarga casi inmediata
    this._elecFlashT = 0;
    this._elecRotoT = 0;
    this._megaActivaId = 'elec';
    this._megaActivaDur = ELEC_DUR;
    this._megaTexDirty = true;
    try { this._buildElecFx(); } catch (e) { this._elecFx = null; }
    this._elecLucesCapturar();
    this._elecFxVis(true);
    // firma sonora «tormenta»: chirrido descendente + golpe grave
    try { this.audio.playOsc(1200, 300, 0.30, 'sawtooth', 0.10, 0); } catch (e) { /* */ }
    try { this.audio.playOsc(90, 55, 0.4, 'sine', 0.16, 0.05); } catch (e) { /* */ }
    this.rules.message = T('arc_elec_go');
    if (this.renderer.xr && this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.8, 180); } catch (e2) { /* */ }
    }
    return true;
  }

  /** Captura las luces y el fondo VIVOS (tema o decorado del campeo-
   *  nato) para devolverlos EXACTOS al disiparse la tormenta. */
  _elecLucesCapturar() {
    const b = {
      hemi: this.hemi ? this.hemi.intensity : 0.95,
      dir: this.dirLight ? this.dirLight.intensity : 2.4,
      spot: (this.spots && this.spots[0]) ? this.spots[0].intensity : 0.5,
      env: (this.scene && this.scene.environmentIntensity != null)
        ? this.scene.environmentIntensity : 0.75,
      bg: null,
      fog: null,
    };
    try {
      if (this.scene.background && this.scene.background.isColor) {
        b.bg = this.scene.background.getHex();
      }
      if (this.scene.fog && this.scene.fog.color) {
        b.fog = this.scene.fog.color.getHex();
      }
    } catch (e) { /* */ }
    this._elecBase = b;
  }

  /** Nivel nocturno (k 0..1) + destello (f 0..1) sobre las luces vivas. */
  _elecLuces(k, f) {
    const b = this._elecBase;
    if (!b) return;
    const noche = 0.18;                 // «casi parece de noche»
    const flash = 1 + Math.max(0, f) * 2.4;
    const mez = (v) => v * (noche + (1 - noche) * (1 - k)) * flash;
    if (this.hemi) this.hemi.intensity = mez(b.hemi);
    if (this.dirLight) this.dirLight.intensity = mez(b.dir);
    for (const s of this.spots || []) s.intensity = mez(b.spot);
    try {
      if (this.scene && this.scene.environmentIntensity != null) {
        this.scene.environmentIntensity = b.env * (0.22 + 0.78 * (1 - k));
      }
      if (!(this.inAR && this.pstOn)) {   // el passthrough canjea fondo/niebla
        if (this.scene.background && this.scene.background.isColor) {
          this.scene.background.lerp(ELEC_NEGRO, k * 0.85);
        }
        if (this.scene.fog && this.scene.fog.color) {
          this.scene.fog.color.lerp(ELEC_NEGRO, k * 0.85);
        }
      }
    } catch (e) { /* */ }
  }

  /** Construye la tormenta UNA vez (pool reutilizable): 2 nubes sprite
   *  procedurales, 3 rayos de 9 puntos y 12 pedacitos negros. Cero
   *  asignaciones por rayo: posiciones recicladas (needsUpdate). */
  _buildElecFx() {
    if (this._elecFx) return;
    const D = DIMS;
    const zC = D.tableCenterZ;
    // — nubes: canvas procedural (borrones grises con panza oscura) —
    const cv = document.createElement('canvas');
    cv.width = 128; cv.height = 64;
    const c2 = cv.getContext('2d');
    if (c2) {
      const borron = (x, y, r, col) => {
        c2.fillStyle = col; c2.beginPath(); c2.arc(x, y, r, 0, Math.PI * 2); c2.fill();
      };
      borron(38, 30, 17, '#59616e'); borron(64, 22, 21, '#6b7482');
      borron(92, 31, 16, '#525a66'); borron(64, 38, 24, '#454c58');
      borron(64, 48, 18, '#31363f');
    }
    const tex = new THREE.CanvasTexture(cv);
    const nubes = [];
    for (let i = 0; i < 2; i++) {
      const mat = new THREE.SpriteMaterial({
        map: tex, transparent: true, opacity: 0, depthWrite: false,
      });
      const sp = new THREE.Sprite(mat);
      const sx = i === 0 ? -0.42 : 0.42;
      const sy = D.tableTopY + ELEC_ALTO_NUBE;      // a 1,5 m (spec literal)
      const sz = zC - D.tableHalfLength * 0.5;      // mitad del RIVAL
      sp.scale.set(1.05, 0.55, 1);
      sp.position.set(sx, sy, sz);
      sp.userData.x0 = sx; sp.userData.y0 = sy; sp.userData.f = i * 2.1;
      sp.renderOrder = 6;
      sp.visible = false;
      this.scene.add(sp);
      nubes.push(sp);
    }
    // — rayos: 3 líneas de 9 puntos, material aditivo azul-blanco —
    const rayos = [];
    for (let i = 0; i < 3; i++) {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position',
        new THREE.BufferAttribute(new Float32Array(9 * 3), 3));
      const mat = new THREE.LineBasicMaterial({
        color: 0xbfe4ff, transparent: true, opacity: 0,
        blending: THREE.AdditiveBlending, depthWrite: false,
      });
      const ln = new THREE.Line(geo, mat);
      ln.visible = false;
      ln.frustumCulled = false;
      ln.userData.vida = 0; ln.userData.f = i * 1.7;
      ln.renderOrder = 7;
      this.scene.add(ln);
      rayos.push(ln);
    }
    // — pedacitos negros: 12 tetraedros (pool de la explosión) —
    const metales = [];
    const geoM = new THREE.TetrahedronGeometry(0.022);
    for (let i = 0; i < 12; i++) {
      const matM = new THREE.MeshBasicMaterial({
        color: 0x0b0b0e, transparent: true, opacity: 0, depthWrite: false,
      });
      const mt = new THREE.Mesh(geoM, matM);
      mt.visible = false;
      mt.userData = { vida: 0, vx: 0, vy: 0, vz: 0, rx: 0, ry: 0 };
      this.scene.add(mt);
      metales.push(mt);
    }
    this._elecFx = { nubes, rayos, rayosIx: 0, metales };
  }

  _elecFxVis(vis) {
    this._elecFxOn = vis;
    const fx = this._elecFx;
    if (!fx) return;
    for (const nb of fx.nubes) nb.visible = vis;  // la opacidad la pone _elecFrame
    if (!vis) {
      for (const rb of fx.rayos) { rb.userData.vida = 0; rb.visible = false; }
      for (const mt of fx.metales) { mt.userData.vida = 0; mt.visible = false; }
    }
  }

  /** Frame de la tormenta: noche (lerp), vaivén de nubes, vida de rayos
   *  y pedacitos, bola rota oculta y cadencia de descargas. */
  _elecFrame(dt) {
    const k = Math.max(0, Math.min(
      Math.min(1, (ELEC_DUR - this._elecT) * 2.5),   // entra en 0,4 s
      Math.min(1, this._elecT / 0.6)));               // sale suave
    this._elecLuces(k, this._elecFlashT > 0 ? this._elecFlashT / 0.25 : 0);
    if (this._elecFlashT > 0) this._elecFlashT -= dt;
    const fx = this._elecFx;
    if (fx) {
      const tt = performance.now() * 0.001;
      for (const nb of fx.nubes) {
        nb.position.x = nb.userData.x0 + Math.sin(tt * 0.9 + nb.userData.f) * 0.10;
        nb.position.y = nb.userData.y0 + Math.sin(tt * 1.3 + nb.userData.f * 2.0) * 0.05;
        nb.material.opacity = 0.82 * k;   // entran y salen con la tormenta
      }
      for (const rb of fx.rayos) {
        const U = rb.userData;
        if (U.vida > 0) {
          U.vida -= dt;
          rb.material.opacity = Math.max(0, Math.min(1, U.vida / 0.26)) *
            (0.62 + 0.38 * Math.sin(performance.now() * 0.07 + U.f));
          rb.visible = rb.material.opacity > 0.02;
        } else if (rb.visible) rb.visible = false;
      }
      for (const mt of fx.metales) {
        const U = mt.userData;
        if (U.vida > 0) {
          U.vida -= dt;
          U.vy -= 4.4 * dt;               // gravedad visual propia
          mt.position.x += U.vx * dt;
          mt.position.y += U.vy * dt;
          mt.position.z += U.vz * dt;
          mt.rotation.x += U.rx * dt;
          mt.rotation.y += U.ry * dt;
          mt.material.opacity = Math.max(0, Math.min(1, U.vida / 0.45));
          mt.visible = mt.material.opacity > 0.02;
        } else if (mt.visible) mt.visible = false;
      }
    }
    // bola rota: oculta mientras dura el efecto (el árbitro ya aplicó el
    // punto; el siguiente saque la re-enciende por sus caminos de siempre)
    if (this._elecRotoT > 0) {
      this._elecRotoT -= dt;
      if (this._elecRotoT <= 0 && this.rules.state === 'rally') {
        if (this.ballMesh) this.ballMesh.visible = true;   // red de seguridad
      }
    }
    // cadencia de descargas (con jitter natural)
    this._elecBoltCd -= dt;
    if (this._elecBoltCd <= 0) {
      this._elecBoltCd = ELEC_BOLT_CD * (0.85 + Math.random() * 0.4);
      try { this._elecRayo(); } catch (eR) { /* un rayo nunca tumba el frame */ }
    }
  }

  /** UN RAYO: nube → punto aleatorio de la MITAD del rival. Destello,
   *  trueno, chispas… y COLISIÓN RÁPIDA contra la bola (punto-segmento:
   *  un hipot, cero asignaciones). Si la intercepta, ESTALLA. */
  _elecRayo() {
    const D = DIMS;
    const fx = this._elecFx;
    if (!fx || !fx.rayos.length) return;
    const zC = D.tableCenterZ;
    const tx = (Math.random() * 2 - 1) * D.netHalfWidth * 0.85;
    const tz = zC - 0.12 - Math.random() * (D.tableHalfLength - 0.22);
    const ty = D.tableTopY + 0.005;
    this._elecTarget.set(tx, ty, tz);
    // nube emisora: la más cercana al objetivo (coherencia visual)
    let nube = fx.nubes[0];
    if (fx.nubes.length > 1) {
      nube = (Math.abs(fx.nubes[0].position.x - tx) <=
              Math.abs(fx.nubes[1].position.x - tx))
        ? fx.nubes[0] : fx.nubes[1];
    }
    const rb = fx.rayos[fx.rayosIx % fx.rayos.length];
    fx.rayosIx++;
    // polilínea dentada nube→mesa (geometría reciclada, 9 puntos)
    const pos = rb.geometry.attributes.position;
    const N = pos.count;
    for (let i = 0; i < N; i++) {
      const f = i / (N - 1);
      const jit = (i === 0 || i === N - 1) ? 0 : 0.09;
      pos.setXYZ(i,
        nube.position.x + (tx - nube.position.x) * f + (Math.random() * 2 - 1) * jit,
        nube.position.y + (ty - nube.position.y) * f + (Math.random() * 2 - 1) * jit * 0.6,
        nube.position.z + (tz - nube.position.z) * f + (Math.random() * 2 - 1) * jit);
    }
    pos.needsUpdate = true;
    rb.geometry.computeBoundingSphere();
    rb.userData.vida = 0.26;
    rb.visible = true;
    // destello + trueno + chispas azules en el punto de impacto
    this._elecFlashT = 0.25;
    this._elecTrueno();
    if (this.chispas) {
      try { this.chispas.burst(this._elecTarget, [0.62, 0.85, 1.0]); } catch (e) { /* */ }
    }
    // COLISIÓN RÁPIDA rayo↔bola (aproximación medible, cálculo barato)
    if (this.rules.state === 'rally' && this._elecRotoT <= 0 && this.ball) {
      this._elecSegA.copy(nube.position);
      this._elecSegB.set(tx, ty, tz);
      const p = this.ball.pos;
      const abx = this._elecSegB.x - this._elecSegA.x;
      const aby = this._elecSegB.y - this._elecSegA.y;
      const abz = this._elecSegB.z - this._elecSegA.z;
      const apx = p.x - this._elecSegA.x;
      const apy = p.y - this._elecSegA.y;
      const apz = p.z - this._elecSegA.z;
      const ab2 = abx * abx + aby * aby + abz * abz;
      const t = ab2 > 0 ? Math.max(0, Math.min(1,
        (apx * abx + apy * aby + apz * abz) / ab2)) : 0;
      const dx = apx - abx * t;
      const dy = apy - aby * t;
      const dz = apz - abz * t;
      const d2 = dx * dx + dy * dy + dz * dz;
      const r = ELEC_BOLT_R + (D.ballRadius || 0.02);
      if (d2 <= r * r) this._elecRompe();
    }
  }

  /** LA BOLA DEL RIVAL ESTALLA: pedacitos negros + PUNTO para el jugador
   *  por el cauce del árbitro (applyPoint — mismos intents y mensajes). */
  _elecRompe() {
    const p = this.ball.pos;
    const fx = this._elecFx;
    if (fx) {
      let dados = 0;
      for (const mt of fx.metales) {
        if (mt.userData.vida > 0) continue;
        mt.position.set(
          p.x + (Math.random() * 2 - 1) * 0.03,
          p.y + (Math.random() * 2 - 1) * 0.03,
          p.z + (Math.random() * 2 - 1) * 0.03);
        const a = Math.random() * Math.PI * 2;
        const sp = 0.5 + Math.random() * 0.9;
        mt.userData.vx = Math.cos(a) * sp * 0.7;
        mt.userData.vy = 0.8 + Math.random() * 1.1;
        mt.userData.vz = Math.sin(a) * sp * 0.7;
        mt.userData.rx = (Math.random() * 2 - 1) * 9;
        mt.userData.ry = (Math.random() * 2 - 1) * 9;
        mt.userData.vida = 1.0;
        if (++dados >= 10) break;
      }
    }
    if (this.ballMesh) this.ballMesh.visible = false;   // estalló
    if (this.trailObj) this.trailObj.visible = false;
    this._elecRotoT = 0.9;
    // estruendo del estallido + háptica fuerte
    try { this.audio.playOsc(1400, 90, 0.32, 'sawtooth', 0.14, 0); } catch (e) { /* */ }
    try { this.audio.playOsc(70, 45, 0.5, 'sine', 0.18, 0.02); } catch (e) { /* */ }
    if (this.renderer.xr && this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 1.0, 220); } catch (e2) { /* */ }
    }
    // PUNTO por el cauce del árbitro (intents 'point' de siempre)
    try {
      this.processIntents(this.rules.applyPoint('player', 'elec'));
    } catch (eP) { /* */ }
  }

  /** Trueno ALTERNO (2 muestras sintetizadas) — fetch+decode+cache. */
  _elecTrueno() {
    try {
      const A = this.audio;
      if (!A || !A.ctx) return;
      this._elecThunderIx = (this._elecThunderIx + 1) & 1;
      const key = 'trueno_' + this._elecThunderIx;
      const fuente = key === 'trueno_0' ? AUDIO_TRUENO_A : AUDIO_TRUENO_B;
      A._megaVozBuf = A._megaVozBuf || {};
      const cached = A._megaVozBuf[key];
      const play = (buf) => {
        try {
          if (!A.ctx || !A.master) return;
          const out = A.panNode(0);
          if (!out) return;
          const src = A.ctx.createBufferSource();
          src.buffer = buf;
          const g = A.ctx.createGain();
          g.gain.value = 0.95;
          src.connect(g); g.connect(out);
          src.start();
        } catch { /* */ }
      };
      if (cached && cached.ctx === A.ctx && cached.buf) { play(cached.buf); return; }
      if (cached && (cached.busy || cached.failed)) return;
      const entry = { ctx: A.ctx, buf: null, busy: true };
      A._megaVozBuf[key] = entry;
      fetch(fuente)
        .then((r) => r.arrayBuffer())
        .then((ab) => A.ctx.decodeAudioData(ab))
        .then((buf) => { entry.buf = buf; entry.busy = false; play(buf); })
        .catch(() => { entry.busy = false; entry.failed = true; });
    } catch { /* el audio NUNCA rompe el bucle del juego */ }
  }

  /** r25 · precalienta los DOS truenos SIN sonar (anti-lag, patrón
   *  _megaVozPrecalentar): la primera descarga jamás decodifica audio. */
  _elecTruenoPrewarm() {
    try {
      const A = this.audio;
      if (!A || !A.ctx) return;
      A._megaVozBuf = A._megaVozBuf || {};
      const pares = [['trueno_0', AUDIO_TRUENO_A], ['trueno_1', AUDIO_TRUENO_B]];
      for (const [key, fuente] of pares) {
        const cached = A._megaVozBuf[key];
        if (cached && (cached.buf || cached.busy || cached.failed)) continue;
        const entry = { ctx: A.ctx, buf: null, busy: true };
        A._megaVozBuf[key] = entry;
        fetch(fuente)
          .then((r) => r.arrayBuffer())
          .then((ab) => A.ctx.decodeAudioData(ab))
          .then((buf) => { entry.buf = buf; entry.busy = false; })
          .catch(() => { entry.busy = false; entry.failed = true; });
      }
    } catch { /* */ }
  }

  /** Fin de la tormenta: luces y fondo EXACTOS de vuelta, FX fuera. */
  _elecFin() {
    this._elecT = 0;
    this._elecWarn = false;
    this._elecTickN = 0;
    this._elecFlashT = 0;
    this._elecFxVis(false);
    const b = this._elecBase;
    if (b) {
      if (this.hemi) this.hemi.intensity = b.hemi;
      if (this.dirLight) this.dirLight.intensity = b.dir;
      for (const s of this.spots || []) s.intensity = b.spot;
      try {
        if (this.scene && this.scene.environmentIntensity != null) {
          this.scene.environmentIntensity = b.env;
        }
        if (!(this.inAR && this.pstOn)) {
          if (b.bg != null && this.scene.background && this.scene.background.isColor) {
            this.scene.background.setHex(b.bg);
          }
          if (b.fog != null && this.scene.fog && this.scene.fog.color) {
            this.scene.fog.color.setHex(b.fog);
          }
        }
      } catch (e) { /* */ }
      this._elecBase = null;
    }
    if (this.rules.state === 'rally' && this._elecRotoT <= 0) {
      if (this.ballMesh) this.ballMesh.visible = true;   // red de seguridad
    }
    this.rules.message = T('arc_elec_fin');
    try { this.audio.playOsc(300, 180, 0.22, 'sine', 0.10, 0); } catch (e) { /* */ }
  }

  /* =====================================================================
   *  r25 (v3.6.120) · GUARDIÁN DE LA BOLA ONLINE (control total; informe
   *  del dueño tras las partidas reales): «en algún saque no se ve la
   *  bola hasta que se lanza… al iniciar una segunda partida vemos la
   *  bola en la mano del rival cuando debería estar en la nuestra, o
   *  incluso no vemos la bola ninguno, lo que impide jugar».
   *
   *  La propiedad se RE-AFIRMA CADA FRAME desde el árbitro (rules.server
   *  es determinista por marcador — idéntico en los dos extremos), sin
   *  tocar el códec de red (c09 INTACTO, spec §7/§9):
   *    · MI SAQUE: visible EN MI mano libre (o punto de saque en
   *      escritorio), vel/spin a cero hasta el lanzamiento — también
   *      durante la cuenta atrás del MATCH_START (3·2·1) y en el
   *      escritorio, donde antes la bola quedaba congelada o flotando.
   *    · SAQUE DEL RIVAL: visible EN SU mano libre mientras la pose de
   *      red llegue fresca; si se apaga (>0,6 s) o la mano no llega,
   *      PUNTO DE SAQUE REGLAMENTARIO del rival — JAMÁS invisible.
   *    · HELD re-armado si la FSM de la bola quedara 'idle' en saque
   *      (la causa raíz de «no la vemos ninguno»).
   *    · RALLYE: siempre visible (salvo portal/tormenta) + guardia
   *      anti-NaN y anti-mundo (bola perdida vuelve jugable a mi mitad).
   *  Idempotente, cero asignaciones por frame, telemetría 1/5 s.
   *  ===================================================================== */
  _bolaGuard(dt) {
    this._bgHold = false;
    try {
      if (this._bgTeleT > 0) this._bgTeleT -= dt;
      if (!this.net || !this.net.online || this.net.v2 !== 'ok' ||
          this.inHall || this.disposed || !this.rules || !this.ballMesh) {
        this._bgRival = 0;
        return;
      }
      const st = this.rules.state;
      if (st !== 'serve' && st !== 'rally') { this._bgRival = 0; return; }
      const exenta = this.ball.ppTransito || this._elecRotoT > 0 || this.calib;
      if (exenta) return;
      const D = DIMS;
      if (st === 'serve') {
        if (this.rules.server === 'player') {
          // — MI SAQUE: la bola vive EN MI mano libre hasta el lanzamiento
          if (!this.tossed) {
            this._bgHold = true;
            this.ballMesh.visible = true;
            this.ball.vel.set(0, 0, 0);
            if (this.ball.spin) this.ball.spin.set(0, 0, 0);
            const bh = this.controllerPaddles
              ? this.controllerPaddles[this.ballHand] : null;
            if (this.renderer.xr.isPresenting && bh && bh.active) {
              this.ball.pos.copy(bh.pos);
              this.ball.pos.y += BALL_HAND_LIFT;
            } else {
              // escritorio (sin visor): punto de saque reglamentario
              this.ball.pos.set(0.3, 1.05, D.tableCenterZ + D.tableHalfLength + 0.4);
            }
            this._bgTele('mi_saque');
          }
        } else if (!this._netTossLive) {
          // — SAQUE DEL RIVAL: su mano libre si la pose llega fresca;
          //   si no, punto de saque reglamentario (JAMÁS invisible)
          let fresca = false;
          const smp = this._netAvatarOut;
          if (smp && this.net.avatarSample(smp) >= 0 &&
              this.net.avatarStaleMs() < 500) {
            const padL = (smp.fl & 4) !== 0;
            if (smp.fl & (padL ? 2 : 1)) {
              NetLink.posFromNetPose(padL ? smp.rp : smp.lp, netTmpP);
              this.ball.pos.set(netTmpP.x, netTmpP.y + BALL_HAND_LIFT, netTmpP.z);
              fresca = true;
            }
          }
          if (fresca) {
            this._bgRival = 0;
            this.ballMesh.visible = true;
            this.ball.vel.set(0, 0, 0);
            if (this.ball.spin) this.ball.spin.set(0, 0, 0);
          } else {
            this._bgRival += dt;
            if (this._bgRival > 0.6 || !this.ballMesh.visible) {
              this.ballMesh.visible = true;
              this.ball.vel.set(0, 0, 0);
              if (this.ball.spin) this.ball.spin.set(0, 0, 0);
              this.ball.pos.set(-0.3, 1.05,
                D.tableCenterZ - D.tableHalfLength - 0.4);
              this._bgTele('rival_saque');
            }
          }
          // FSM 'idle' en saque (nadie tiene la bola) → re-armar HELD
          try {
            if (this.net.ballState && this.net.ballState() === 'idle') {
              this.net.setServeHeld(false);   // saca el rival (perspectiva local)
            }
          } catch (eFsm) { /* */ }
        }
      } else {
        // — RALLYE: visible + guardia anti-NaN / anti-mundo
        const p = this.ball.pos;
        const enMundo = isFinite(p.x) && isFinite(p.y) && isFinite(p.z) &&
          p.y > -2 && p.y < 7 && Math.abs(p.x) < 7 &&
          Math.abs(p.z - D.tableCenterZ) < 7.5;
        if (!enMundo) {
          p.set(0, D.tableTopY + 0.5, D.tableCenterZ + D.tableHalfLength * 0.4);
          this.ball.vel.set(0, 0, 0);
          if (this.ball.spin) this.ball.spin.set(0, 0, 0);
          this._bgTele('rally_loca');
        }
        if (!this.ballMesh.visible) {
          this.ballMesh.visible = true;   // portal/tormenta ya exentos arriba
          this._bgTele('rally_vis');
        }
      }
    } catch (eBG) { /* el guardián nunca tumba el frame */ }
  }

  /** Telemetría del guardián (1/5 s por tipo — nunca ametralla). */
  _bgTele(k) {
    if (this._bgTeleT > 0) return;
    this._bgTeleT = 5;
    try { __PP_TELE.ev('bola_guard', { k }); } catch (eT) { /* */ }
  }

  /** r25 (v3.6.120) · CORTINA de poderes en las PRUEBAS DE HABILIDAD
   *  (etapas 2 y 4 de TODOS los campeonatos — reporte del dueño: «los
   *  superpoderes de Pala del jugador nunca deben aparecer en las etapas
   *  2 y 4»). Idempotente y barata: apaga ventanas vivas, FX, icono y
   *  radio de golpeo. NO borra la matriz: las cargas no gastadas de un
   *  duelo siguen siendo del jugador en el duelo siguiente (la recogida
   *  completa sigue siendo la del startMatch de siempre). */
  _poderesCortina() {
    if (this._megaT > 0) this._megaT = 0;
    if (this._efectoT > 0) {
      this._efectoT = 0; this._efectoWarn = false; this._efectoTickN = 0;
      this._efectoFxVis(false);
    }
    if (this._imanT > 0) {
      this._imanT = 0; this._imanWarn = false; this._imanTickN = 0;
      this._imanFxVis(false);
      try { this._imanPalaOsc(false); } catch (eO) { /* */ }
    }
    if (this._portalT > 0) {
      this._portalT = 0; this._portalWarn = false; this._portalTickN = 0;
      this._portalFxVis(false);
    }
    if (this._clonT > 0) {
      this._clonT = 0; this._clonWarn = false; this._clonTickN = 0;
      this._clonVis(false);
    }
    if (this._redT > 0) {
      this._redT = 0; this._redWarn = false; this._redTickN = 0;
      try { this._redRestaurar(); } catch (eR) { /* */ }
    }
    if (this._elecT > 0) {
      this._elecT = 0; this._elecWarn = false; this._elecTickN = 0;
      try { this._elecFin(); } catch (eE) { /* */ }
    }
    this._megaActivaId = null;
    DIMS.hitAssistRadius = this._BASE_HIT;
    if (this._megaIconOn) this._megaIconVis(false);
  }""", 'metodos-r25'),

    # 12 · cortina al principio de updateMega
    ("""    const on = this.megaEnabled() && !this.inHall && !this.calib;
    // r84 · DUELOS LOCOS · GIGANTE: mismo radio de golpeo y misma escala
    // que la MEGA de campeonatos, gobernado por el estado duelos (§DUELOS)
    const dlGig = this._dlOn('gigante');""",
     """    const on = this.megaEnabled() && !this.inHall && !this.calib;
    // r25 (v3.6.120) · ETAPAS 2/4: CORTINA de poderes (nunca aparecen en
    // las pruebas de habilidad — ni icono, ni cargas nuevas, ni ventanas).
    if (this._poderesEnPrueba()) {
      this._poderesCortina();
    }
    // r84 · DUELOS LOCOS · GIGANTE: mismo radio de golpeo y misma escala
    // que la MEGA de campeonatos, gobernado por el estado duelos (§DUELOS)
    const dlGig = this._dlOn('gigante');""", 'cortina-update'),

    # 13 · temporizadores red/elec en updateMega (antes del clon frame)
    ("""    // v3.6.50 (r58) · el clon vive SUS 10 s (patrón portal): sigue la pala,""",
     """    // r25 (v3.6.120) · SÚPER RED ACTIVA: ventana PROPIA de 10 s; al
    // acabar la red vuelve EXACTA a su altura reglamentaria. Sin «on»
    // (salir del campeonato, prueba) la red se recoge YA: un entorno
    // mutado no puede sobrevivir a su contexto.
    if (on && this._redT > 0) {
      this._redT -= dt;
      if (this._redT <= 0) {
        this._redFin();                  // fin natural (10 s agotados)
      } else if (this._redT < 2 && !this._redWarn) {
        this._redWarn = true;
        this._poderTickBlip(2);          // cuenta sonora uniforme
      } else if (this._redT < 3 && (this._redTickN || 0) < 1) {
        this._redTickN = 1;
        this._poderTickBlip(1);
      } else if (this._redT < 1 && (this._redTickN || 0) < 3) {
        this._redTickN = 3;
        this._poderTickBlip(3);
      }
    } else if (this._redT > 0) {
      this._redT = 0;
      try { this._redFin(); } catch (eRF) { /* */ }
    }
    // r25 (v3.6.120) · SÚPER ELECTRICIDAD ACTIVA: tormenta viva (nubes,
    // rayos, truenos, noche, destello y colisión) durante SU ventana.
    if (on && this._elecT > 0) {
      this._elecT -= dt;
      if (this._elecT <= 0) {
        this._elecFin();                 // fin natural (10 s agotados)
      } else if (this._elecT < 2 && !this._elecWarn) {
        this._elecWarn = true;
        this._poderTickBlip(2);
      } else if (this._elecT < 3 && (this._elecTickN || 0) < 1) {
        this._elecTickN = 1;
        this._poderTickBlip(1);
      } else if (this._elecT < 1 && (this._elecTickN || 0) < 3) {
        this._elecTickN = 3;
        this._poderTickBlip(3);
      }
    } else if (this._elecT > 0) {
      this._elecT = 0;
      try { this._elecFin(); } catch (eEF2) { /* */ }
    }
    if (this._elecT > 0) {
      try { this._elecFrame(dt); } catch (eEF) { /* la tormenta nunca tumba el frame */ }
    } else if (this._elecFxOn) {
      this._elecFxVis(false);
    }
    // v3.6.50 (r58) · el clon vive SUS 10 s (patrón portal): sigue la pala,""", 'timers-update'),

    # 14 · _megaNormReset: recogida de red/elec
    ("""    this._clonVis(false);
    this._portalFxVis(false);""",
     """    this._clonVis(false);
    this._portalFxVis(false);
    // r25 (v3.6.120) · la RED vuelve a su altura y la TORMENTA se disipa
    // (recogida completa, patrón de los cinco poderes anteriores)
    this._redT = 0;
    this._redWarn = false;
    this._redTickN = 0;
    try { this._redRestaurar(); } catch (eR0) { /* */ }
    this._elecT = 0;
    this._elecWarn = false;
    this._elecTickN = 0;
    this._elecRotoT = 0;
    this._elecFlashT = 0;
    try { this._elecFin(); } catch (eR1) { /* */ }""", 'norm-reset'),

    # 15 · precaliente: voces + tormenta
    ("""      () => { try { this._vozSelPrewarm(); } catch (e) { /* */ } }, // r58: voces del selector
    ];""",
     """      () => { try { this._vozSelPrewarm(); } catch (e) { /* */ } }, // r58: voces del selector
      () => { try { this._megaVozPrecalentar('red'); } catch (e) { /* */ } },   // r25: voz concesión
      () => { try { this._megaVozPrecalentar('elec'); } catch (e) { /* */ } },  // r25: voz concesión
      () => { try { this._buildElecFx(); } catch (e) { /* */ } },   // r25: tormenta lista
      () => { try { this._elecTruenoPrewarm(); } catch (e) { /* */ } }, // r25: truenos
    ];""", 'precaliente'),

    # 16 · reservas del icono (red + elec antes del dorado genérico)
    ("""      } else {
        // RESERVA: el dibujo dorado de V3.6.34 (pala + 4 flechas de crecida)""",
     """      } else if (id === 'red') {
        // RESERVA de la SÚPER RED (r25): red estirada con flecha hacia arriba
        c2.lineWidth = 7; c2.strokeStyle = '#4d7fd6';
        c2.beginPath(); c2.moveTo(52, 150); c2.lineTo(204, 150); c2.stroke();
        for (let gx = 0; gx <= 6; gx++) {
          c2.beginPath();
          c2.moveTo(52 + gx * 25.3, 150); c2.lineTo(52 + gx * 25.3, 204);
          c2.stroke();
        }
        for (let gy = 0; gy <= 2; gy++) {
          c2.beginPath();
          c2.moveTo(52, 150 + gy * 27); c2.lineTo(204, 150 + gy * 27);
          c2.stroke();
        }
        c2.lineWidth = 12; c2.strokeStyle = '#8fc1ff';
        c2.beginPath(); c2.moveTo(128, 138); c2.lineTo(128, 58); c2.stroke();
        c2.fillStyle = '#8fc1ff';
        c2.beginPath(); c2.moveTo(128, 42); c2.lineTo(110, 70); c2.lineTo(146, 70);
        c2.closePath(); c2.fill();
      } else if (id === 'elec') {
        // RESERVA de la SÚPER ELECTRICIDAD (r25): bola radiante con rayos
        c2.beginPath(); c2.arc(128, 128, 34, 0, Math.PI * 2);
        c2.fillStyle = '#e8f4ff'; c2.fill();
        c2.lineWidth = 6; c2.strokeStyle = '#5b8fd6'; c2.stroke();
        c2.lineWidth = 8; c2.strokeStyle = '#7fd0ff';
        for (let ri = 0; ri < 6; ri++) {
          const a = ri * Math.PI / 3 + 0.35;
          c2.beginPath();
          c2.moveTo(128 + Math.cos(a) * 44, 128 + Math.sin(a) * 44);
          c2.lineTo(128 + Math.cos(a) * 86, 128 + Math.sin(a) * 86);
          c2.lineTo(128 + Math.cos(a + 0.22) * 62, 128 + Math.sin(a + 0.22) * 62);
          c2.stroke();
        }
      } else {
        // RESERVA: el dibujo dorado de V3.6.34 (pala + 4 flechas de crecida)""", 'icono-reservas'),

    # 17 · hook en animate + ballHeld de la guardia
    ("""    this.updateMega(dt);
    this._dlUpdate(dt);       // r84 · DUELOS LOCOS: tick de poderes online""",
     """    this.updateMega(dt);
    this._dlUpdate(dt);       // r84 · DUELOS LOCOS: tick de poderes online
    this._bolaGuard(dt);      // r25 (v3.6.120) · CONTROL TOTAL de la bola online""", 'animate-hook'),

    ("""    const ballHeld = holdLock;""",
     """    const ballHeld = holdLock || this._bgHold;   // r25: la guardia también sujeta""", 'ballheld'),

    # 18 · voz del selector: reutiliza las voces de concesión
    ("""    else if (id === 'clon') par = [VOZ_SEL_CLON, VOZ_SEL_CLON_EN];
    return par ? (en ? par[1] : par[0]) : null;""",
     """    else if (id === 'clon') par = [VOZ_SEL_CLON, VOZ_SEL_CLON_EN];
    // r25 · red/elec: sin voz corta propia — reutilizan la de concesión
    else if (id === 'red') par = [VOZ_PODER_RED, VOZ_PODER_RED_EN];
    else if (id === 'elec') par = [VOZ_PODER_ELEC, VOZ_PODER_ELEC_EN];
    return par ? (en ? par[1] : par[0]) : null;""", 'voz-selector'),

    # 19 · precaliente del selector: 8 ids
    ("""      const ids = ['mega', 'efecto', 'iman', 'portal', 'clon', 'nada'];""",
     """      const ids = ['mega', 'efecto', 'iman', 'portal', 'clon', 'nada', 'red', 'elec'];""", 'sel-prewarm'),
]

# ---------------------------------------------------------------- c00 ----
EDICIONES_C00 = [
    # ES · claves de poder (tras clon_salva/poder_clon)
    ("""    clon_salva: '¡LA PALA CLON TE HA SALVADO!',
    poder_clon: '¡POTENCIADOR DE CLONACIÓN!',
    sin_poder: 'Sin poder',""",
     """    clon_salva: '¡LA PALA CLON TE HA SALVADO!',
    poder_clon: '¡POTENCIADOR DE CLONACIÓN!',
    // v3.6.120 (r25) · SÚPER RED + SÚPER ELECTRICIDAD (6.º y 7.º poder)
    arc_red_go: '¡SÚPER RED! · la red crece AL DOBLE · 10 s',
    arc_red_fin: 'SÚPER RED agotada · la red vuelve a su altura',
    poder_red: '¡POTENCIADOR DE SÚPER RED!',
    arc_elec_go: '¡SÚPER ELECTRICIDAD! · tormenta sobre tu rival · 10 s',
    arc_elec_fin: 'la tormenta se disipa',
    poder_elec: '¡POTENCIADOR DE SÚPER ELECTRICIDAD!',
    sin_poder: 'Sin poder',""", 'es-claves'),

    # ES · causa del punto eléctrico
    ("""    cause_burla: 'comodín de la Burla',""",
     """    cause_burla: 'comodín de la Burla',
    cause_elec: 'fulminada por la SÚPER ELECTRICIDAD',""", 'es-causa'),

    # EN · claves de poder
    ("""    clon_salva: 'THE CLONE PADDLE SAVED YOU!',
    poder_clon: 'CLONE BOOSTER!',
    sin_poder: 'No power',""",
     """    clon_salva: 'THE CLONE PADDLE SAVED YOU!',
    poder_clon: 'CLONE BOOSTER!',
    // v3.6.120 (r25) · SUPER NET + SUPER ELECTRICITY (6th & 7th powers)
    arc_red_go: 'SUPER NET! · the net grows TWICE as tall · 10 s',
    arc_red_fin: 'SUPER NET worn off · the net is back to its height',
    poder_red: 'SUPER NET BOOSTER!',
    arc_elec_go: 'SUPER ELECTRICITY! · storm over your rival · 10 s',
    arc_elec_fin: 'the storm clears',
    poder_elec: 'SUPER ELECTRICITY BOOSTER!',
    sin_poder: 'No power',""", 'en-claves'),

    # EN · causa
    ("""    cause_burla: 'mock wildcard',""",
     """    cause_burla: 'mock wildcard',
    cause_elec: 'struck down by SUPER ELECTRICITY',""", 'en-causa'),
]

if __name__ == '__main__':
    parchea(C12, EDICIONES_C12)
    parchea(C00, EDICIONES_C00)
    print('PATCH r25 COMPLETO · 20 + 4 ediciones')
