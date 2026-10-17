#!/usr/bin/env python3
"""V3.2.0-ORB1 · Port del ARKANOID de La Locura al módulo ESTACIÓN ORBITAL
+ vestido completo del decorado del dueño.

Ediciones sobre public/championships/estacion_orbital/index.js:
  1. import GLTFLoader
  2. cabecera v3.2.0
  3. CFG: rival 'ASTRO' + etapas muro1/muro2
  4. preámbulo ARK (T/DIMS/stepPhysics/GUN/arcadeCanvas/ARK_CFG/ARK2_CFG/texturas)
  5. clase EOArkanoid (1467-2927 de locura) con _finish/_afterResult adaptados
     al camino EO y refs a.rival/a.rankPanel neutralizadas
  6. StockController: constructor, serveTrigger, _empezarPrueba, _empezarMuro,
     _arrancarMuro, update, leave, poses crazy/duelo, cartel superpower con
     el arte de la casa, pistola (gunArmed/fireGun/_loadGunArt/_attachGunArt/
     _normalizeGun/_gunUpdate/_purgeBeams) y _testActivo
  7. MapaEO: arte nuevo 1376×768 + nodos re-medidos
  8. export del módulo: decor/room, testActive/testStep, reenter, GUN_ART_URL
Cada reemplazo se verifica UNA y SÓLO una vez; fallo = abort sin escribir.
"""
import re
import sys

LOC = '/home/z/my-project/public/championships/locura/index.js'
EO = '/home/z/my-project/public/championships/estacion_orbital/index.js'

loc = open(LOC, encoding='utf-8').read().split('\n')
# clase ArcadeArkanoid completa: líneas 1467..2927 (1-indexed, inclusive)
ark = '\n'.join(loc[1466:2927])
assert ark.startswith('class ArcadeArkanoid {'), ark[:80]
assert ark.rstrip().endswith('}'), ark[-80:]

REPL = []
def rep(txt, old, new, tag):
    n = txt.count(old)
    if n != 1:
        sys.exit(f'FALLO ({tag}): {n} coincidencias para:\n{old[:160]}')
    print(f'  ok {tag}')
    return txt.replace(old, new, 1)

# ── 1. nombre de clase ────────────────────────────────────────────────
ark = rep(ark, 'class ArcadeArkanoid {', 'class EOArkanoid {', 'clase')

# ── 2. start(): ocultar rival/cartel del controlador EO ─────────────
ark = rep(ark, """    const a = this.ctrl;
    a.rival.hide();
    a.cartel.hide();
    a.rankPanel.hide();
    a.powerSign.hide();""", """    const a = this.ctrl;
    if (a.rivalMesh) a.rivalMesh.visible = false;  // v3.2.0: el ASTRO no juega el muro
    if (a.cartel) a.cartel.visible = false;
    if (a.powerSign) a.powerSign.visible = false;""", 'start()')

# ── 3. _finish: flujo del camino EO ──────────────────────────────────
i0 = ark.index('  _finish(win, reason) {')
i1 = ark.index('  _afterResult() {')
EO_FINISH = """  _finish(win, reason) {
    const g = this.game;
    const a = this.ctrl;
    this.phase = 'result';
    this.phaseT = win ? 4.4 : 3.6;
    if (win) {
      // v3.2.0 · CAMINO EO: la prueba superada AVANZA la etapa (persiste
      // _pruebaFin) y la rejugada deja el camino como estaba (v2.96).
      if (a._replay) {
        this._banner = { title: this.variant === 2 ? T('ark2_win') : T('ark_win'),
          sub: T('replay_done'), col: '#7fb069' };
        try { g.audio.announce(T('replay_done'), true); } catch (e) { /* */ }
      } else {
        a._pruebaFin(true);
        const sig = CFG.etapas[Math.min(a.stage, CFG.etapas.length - 1)];
        this._banner = {
          title: this.variant === 2 ? T('ark2_win') : T('ark_win'),
          sub: tx('Siguiente: ' + sig.name, 'Next: ' + sig.name), col: '#7fb069',
        };
        try { g.audio.announce(this._banner.sub, true); } catch (e) { /* */ }
      }
      g.confettiBurst = 3;
      g.audio.fanfare(true);
      if (g.renderer.xr.isPresenting) {
        g.haptic(g.paddleHand, 0.8, 140);
        window.setTimeout(() => g.haptic(g.paddleHand, 0.5, 130), 220);
      }
    } else {
      // derrota: la etapa se REPITE (flujo amable de la plantilla EO)
      if (a._replay) {
        this._banner = { title: reason === 'lives' ? T('ark_nolives') : T('ark_timeup'),
          sub: T('replay_done'), col: '#e06c5a' };
      } else {
        this._banner = {
          title: reason === 'lives' ? T('ark_nolives') : T('ark_timeup'),
          sub: tx('La prueba se repite: vuelve a intentarlo cuando quieras',
                  'The test repeats: try again any time'), col: '#e06c5a',
        };
        a._pruebaFin(false);
      }
      g.audio.fanfare(false);
    }
    this._hudDirty = true;
    if (a.mapa) a.mapa.refresh();
  }

"""
ark = ark[:i0] + EO_FINISH + ark[i1:]
print('  ok _finish')

# ── 4. _afterResult: vuelta a la sala EO ─────────────────────────────
i0 = ark.index('  _afterResult() {')
i1 = ark.index('  /* ---------------- animaciones y HUD ----------------')
EO_AFTER = """  _afterResult() {
    const a = this.ctrl;
    this.stop();
    // v3.2.0: la SALA retoma el camino (cartel, mapa, árbitro dormido,
    // música) — el flujo propio de la plantilla Estación Orbital.
    a._despuesDePrueba();
  }

"""
ark = ark[:i0] + EO_AFTER + ark[i1:]
print('  ok _afterResult')

# ── 5. renombres de seguridad ────────────────────────────────────────
ark = ark.replace('a.map', 'a.mapa')
ark = ark.replace('__PP_LOCURA_GUN_INFO', '__PP_EO_GUN_INFO')
ark = ark.replace('__locuraArt', '__eoArt')
ark = ark.replace("[estacion] pistol.glb del artista montada", "[estacion] pistol.glb del artista montada")
ark = ark.replace("'[locura] pistol.glb del artista montada (ARKANOID 2)'", "'[estacion] pistol.glb del artista montada (MURO 2)'")
ark = ark.replace("'[locura] pistola: normalización KO'", "'[estacion] pistola: normalización KO'")
ark = ark.replace("'[locura] pistol.glb no disponible — se mantiene la del core'", "'[estacion] pistol.glb no disponible — se mantiene la del core'")
# restos locura que no deben quedar (con límite de palabra: a.rivalMesh ok)
for mal in (r'a\.rival\b', r'rankPanel', r'a\.round\b', r'a\.powers\b',
            r'a\.rank\b', r'a\.streakP\b', r'a\.streakAi\b'):
    m = re.search(mal, ark)
    if m:
        ln = ark[:m.start()].count('\n') + 1
        linea = ark.split('\n')[ln - 1]
        print(f'  RESTO {mal} en línea {ln}: {linea.strip()[:120]}', file=sys.stderr)
        sys.exit(f'FALLO: la clase portada aún menciona {mal}')
print('  ok renombres')

# ── preámbulo ARK (consts + texturas) ────────────────────────────────
PREAMBULO = """/* ============================================================================
 *  v3.2.0 · MUROS ORBITALES — port del ARKANOID de La Locura (QA de casas)
 *  ----------------------------------------------------------------------------
 *  El mapa nuevo del dueño dibuja las etapas 2 y 4 como MUROS DE LADRILLOS
 *  (misma iconografía que el mapa del clown): el camino de la plantilla
 *  pasa de las DIANAS a los MUROS. Variante 1: muro clásico de 30 ladrillos
 *  rojos (2 min, 5 vidas). Variante 2: 54 ladrillos rojos/azules + PISTOLA
 *  LÁSER pistol.glb en la mano libre (el azul explota y queda rojo; el rojo
 *  es inmune; los rojos vivos se vuelven azules con el tiempo; ladrillo
 *  negro del tiempo extra = +1 min). Física del núcleo intacta vía
 *  stepPhysics + colisionador extra por subpaso (anti-túnel).
 *  ========================================================================== */
const __CORE = (typeof window !== 'undefined' && window.__PP_CORE) || null;
const T = (k) => ((__CORE && __CORE.T) ? __CORE.T(k) : k);
const DIMS = (CORE && CORE.DIMS) || {
  tableHalfWidth: 0.7625, tableTopY: 0.76, tableCenterZ: -1.6,
  tableHalfLength: 1.37, ballRadius: 0.02, gravity: 9.6,
};
const stepPhysics = (CORE && CORE.stepPhysics) || null;
let GUN_ART_URL = '';
const GUN_MOUNT_PITCH = 0;
const GUN_MUZZLE = new THREE.Vector3(0.0003, 0.092, -0.163);

function arcadeCanvas(w, h) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  return cv;
}

"""
# ARK_CFG/ARK2_CFG + texturas: verbatim de locura (1307..1464)
arkcfg = '\\n'.join  # (no-op readability)
ark_cfg_src = '\n'.join(loc[1306:1464])
assert ark_cfg_src.startswith('const ARK_CFG = {'), ark_cfg_src[:60]
assert ark_cfg_src.rstrip().endswith('}'), ark_cfg_src[-60:]
PREAMBULO += ark_cfg_src + '\n\n'

eo = open(EO, encoding='utf-8').read()

# ── E1. import GLTFLoader ────────────────────────────────────────────
eo = rep(eo, "import * as THREE from 'three';   // importmap del núcleo: MISMA instancia",
         "import * as THREE from 'three';   // importmap del núcleo: MISMA instancia\n"
         "import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';   // v3.2.0: pistol.glb del MURO 2",
         'import GLTFLoader')

# ── E2. cabecera v3.2.0 ──────────────────────────────────────────────
eo = rep(eo, """ *  Estación Orbital (estacion_orbital) — v3.1 «PLANTILLA FINAL» (V2.131)
 *  ----------------------------------------------------------------------------
""",
""" *  Estación Orbital (estacion_orbital) — v3.1 «PLANTILLA FINAL» (V2.131)
 *  ----------------------------------------------------------------------------
 *  v3.2.0 (ORB1) · DECORADO REAL DEL DUEÑO + MUROS ORBITALES: (1) SALA con
 *    el arte del dueño en los 6 planos (literas, ventanal con la Tierra,
 *    esclusa, suelo y techo — patrón vagón del Oeste). (2) RIVAL ASTRO con
 *    las 12 poses del artista (convención clown assets/<estado>.webp; en
 *    duelo focused, con superpoder crazy, al caer defeated). (3) MAPA nuevo
 *    (1376×768) que define las pruebas como MUROS → port del ARKANOID de
 *    La Locura (2 variantes + pistola láser) con cartel explicativo sobre
 *    la plantilla del artista (normas_astro.png vía NORMAS_SKIN). (4) CARTEL
 *    DE SUPERPODER con la etiqueta de la casa (superpower.png) + miniatura
 *    del poder. (5) RECORTABLES reales por el suelo (cohete, astro, lander,
 *    telescopio). La física CCD/SRV2/FEEL1 del núcleo: INTACTA.
 *  ----------------------------------------------------------------------------
""", 'cabecera')

# ── E3. CFG: rival + etapas ──────────────────────────────────────────
eo = rep(eo, "  rival: 'Androide AX-9',", "  rival: 'ASTRO',   // v3.2.0: el astronauta del arte del dueño", 'rival')
eo = rep(eo, "    { kind: 'prueba', id: 'cinturon', name: 'Cinturón de asteroides' },",
         "    { kind: 'prueba', id: 'muro1', name: 'Arkanoid orbital' },   // v3.2.0: MURO según el mapa del dueño", 'etapa1')
eo = rep(eo, "    { kind: 'prueba', id: 'tormenta', name: 'Tormenta de meteoritos' },",
         "    { kind: 'prueba', id: 'muro2', name: 'Arkanoid II' },   // v3.2.0: MURO rojo/azul + láser", 'etapa2')

# ── E4. preámbulo tras HOLD ──────────────────────────────────────────
eo = rep(eo, "const HOLD = { x: 0.26, z: -0.50, T: 0.95, H: 0.42 };   // bote-en-espera\n",
         "const HOLD = { x: 0.26, z: -0.50, T: 0.95, H: 0.42 };   // bote-en-espera\n\n" + PREAMBULO, 'preámbulo')

# ── E5. clase EOArkanoid antes de StockController ────────────────────
eo = rep(eo, "/* ============================================================================\n *  StockController — SALA · CAMINO DE 5 ETAPAS · SUPERPODERES",
         ark + "\n\n/* ============================================================================\n *  StockController — SALA · CAMINO DE 5 ETAPAS · SUPERPODERES", 'clase EOArkanoid')

# ── E6. constructor ──────────────────────────────────────────────────
eo = rep(eo, "    this.prueba = new DianasOrbitales(this);",
         "    this.prueba = new DianasOrbitales(this);   // motor legacy (sin uso desde v3.2.0)\n"
         "    // v3.2.0: MUROS ORBITALES (port del ARKANOID de La Locura)\n"
         "    this.arkanoid = new EOArkanoid(this);\n"
         "    this._beams = []; this._gunArt = [];\n"
         "    this._gunLast = 0; this._gunHintDone = false;\n"
         "    this._gunArtModel = null; this._gunArtLoading = false; this._gunMuzzle = null;", 'constructor')

# ── E7. serveTrigger: el gatillo es del muro en prueba ───────────────
eo = rep(eo, """  serveTrigger() {
    if (this.state !== 'sala') return;""",
"""  serveTrigger() {
    // v3.2.0: en PRUEBA el gatillo lanza el SAQUE del muro (EOArkanoid)
    if (this.arkanoid && this.arkanoid.active) { this.arkanoid.serveTrigger(); return; }
    if (this.state !== 'sala') return;""", 'serveTrigger')

# ── E8. _empezarPrueba: branch muro ──────────────────────────────────
eo = rep(eo, """  _empezarPrueba(et) {
    const g = this.game;
    const compleja = et.id === 'tormenta';""",
"""  _empezarPrueba(et) {
    const g = this.game;
    // v3.2.0 · MUROS ORBITALES: las pruebas del camino son ahora ARKANOID
    if (et.id === 'muro1' || et.id === 'muro2') { this._empezarMuro(et); return; }
    const compleja = et.id === 'tormenta';""", '_empezarPrueba branch')

# ── E9. _empezarMuro + _arrancarMuro antes de _arrancarPrueba ────────
eo = rep(eo, "  _arrancarPrueba(compleja) {",
"""  /* — v3.2.0 · MUROS ORBITALES: cartel explicativo (piel del artista vía
   *  NORMAS_SKIN) + arranque del EOArkanoid ——————————————— */
  _empezarMuro(et) {
    const g = this.game;
    this.state = 'prueba';
    g.rules.state = 'champtest';       // árbitro dormido durante el cartel
    this.cartel.visible = false;
    this.rivalEstado('idle');
    if (this._instrK !== et.id) {
      this._instrK = et.id;
      try {
        const es2 = (et.id === 'muro2');
        g.showInstrucciones(
          tx('PRUEBA · ' + et.name.toUpperCase(), 'SKILL TEST · ' + et.name.toUpperCase()),
          es2 ? [
            tx('Muro de 54 ladrillos: los ROJOS sólo caen con la PALA; los AZULES sólo con el LÁSER (explotan y quedan rojos).',
               '54-brick wall: RED bricks fall to the PADDLE only; BLUE ones to the LASER only (they blow up and turn red).'),
            tx('La PISTOLA LÁSER va en tu mano libre. 2 min 30 s y 5 vidas; los rojos vivos se vuelven azules con el tiempo.',
               'The LASER PISTOL rides your free hand. 2 min 30 s, 5 lives; live reds turn blue over time.'),
          ] : [
            tx('Rompe TODOS los ladrillos del muro golpeando la bola con las palas: el rebote es real, calcula los ángulos.',
               'Break EVERY wall brick by hitting the ball with your paddles: real bounces, work the angles.'),
            tx('Tienes 2 minutos y 5 vidas (saques). Cada ladrillo roto suma.',
               '2 minutes and 5 lives (serves). Every broken brick counts.'),
          ],
          7.5,
          () => {
            this._instrK = null;          // próxima entrada re-explica (regla v2.106)
            try { this._arrancarMuro(et); } catch (e) { /* */ }
          },
          'estacion',
          { empezar: true });   // v2.130: espera al botón EMPEZAR (común)
        return;
      } catch (e) { this._instrK = null; }   // sin núcleo de carteles: arranca igual
    }
    this._instrK = null;
    this._arrancarMuro(et);
  }
  _arrancarMuro(et) {
    const g = this.game;
    this._poderClear();
    this.state = 'prueba';
    g.rules.state = 'arkanoid';        // el núcleo enruta testStep/gatillo/láser
    this.arkanoid.variant = (et.id === 'muro2') ? 2 : 1;
    this.arkanoid.start();
    this.musicOn();
  }

  _arrancarPrueba(compleja) {""", '_empezarMuro/_arrancarMuro')

# ── E10. update(): pistola por frame ─────────────────────────────────
eo = rep(eo, "    try { if (g.aiPaddleMesh) g.aiPaddleMesh.visible = (this.state === 'duelo'); } catch (e) { /* */ }",
         "    try { if (g.aiPaddleMesh) g.aiPaddleMesh.visible = (this.state === 'duelo'); } catch (e) { /* */ }\n"
         "    // v3.2.0: pistola láser del MURO 2 (montaje/visibilidad/fade de rayos)\n"
         "    if (this.arkanoid && this.arkanoid.active) this._gunUpdate(dt);", 'update gun')

# ── E11. leave(): muro fuera + rayos purgados + pistola restaurada ───
eo = rep(eo, """    this.musicOff();
    this._poderClear();
    this.prueba.stop();""",
"""    this.musicOff();
    this._poderClear();
    this.prueba.stop();
    if (this.arkanoid) this.arkanoid.stop();   // v3.2.0: fuera el muro
    this._purgeBeams();                        // v2.120: sin rayos huérfanos
    this._restoreGun();                        // v3.2.0: monturas al estado core
    try {
      if (this.game.gunMounts) {
        for (const gm of this.game.gunMounts) if (gm) gm.visible = false;
      }
    } catch (e) { /* */ }""", 'leave')

# ── E12. crazy en el superpoder + vuelta a duelo ─────────────────────
eo = rep(eo, "    this._psMuestra(def, false);          // v3.2: CARTEL con el identificador",
         "    this._psMuestra(def, false);          // v3.2: CARTEL con el identificador\n"
         "    this.rivalEstado('crazy');            // v3.2.0: ¡el ASTRO se revuelve!", 'warn crazy')
eo = rep(eo, """    this._act = null;
    this._powerCd = 10 + Math.random() * 5;      // v3.2: antes 12+8 (más ágil)
    this._psOculta();                            // v3.2: fuera el cartel""",
"""    this._act = null;
    this._powerCd = 10 + Math.random() * 5;      // v3.2: antes 12+8 (más ágil)
    this._psOculta();                            // v3.2: fuera el cartel
    if (this.state === 'duelo') this.rivalEstado('duelo');   // v3.2.0: cara de duelo""", 'fin poder')

# ── E13. _psMuestra con el arte de la casa ───────────────────────────
i0 = eo.index('  _psMuestra(def, activa) {')
i1 = eo.index('  _psOculta() {')
EO_PS = """  _psMuestra(def, activa) {
    if (!this.powerSign) return;
    const c = this._psCv.getContext('2d');
    c.clearRect(0, 0, 512, 256);
    // v3.2.0 · LA ETIQUETA DE LA CASA: el cartel «Super Power!!» del
    // artista (superpower.png, el mismo arte que lucen locura/magia/oeste)
    // como fondo del panel, con MINIATURA del poder + nombre en la banda.
    const art = this._psBanner;
    if (art && art.complete && art.naturalWidth) {
      const ar = art.naturalWidth / art.naturalHeight;
      let w = 512, h = w / ar;
      if (h > 256) { h = 256; w = h * ar; }
      c.drawImage(art, (512 - w) / 2, (256 - h) / 2, w, h);
    } else {
      c.fillStyle = 'rgba(8,14,26,0.92)';
      c.beginPath();
      if (c.roundRect) c.roundRect(8, 8, 496, 240, 30); else c.rect(8, 8, 496, 240);
      c.fill();
    }
    // banda inferior legible sobre el arte
    c.fillStyle = activa ? 'rgba(6,46,62,0.90)' : 'rgba(92,50,8,0.90)';
    c.fillRect(0, 198, 512, 58);
    c.strokeStyle = activa ? '#59e6ff' : '#ffb347';
    c.lineWidth = 6;
    c.beginPath(); c.moveTo(0, 198); c.lineTo(512, 198); c.stroke();
    try {
      const img = this._psIcons && this._psIcons[def.name];
      if (img && img.complete && img.naturalWidth) {
        c.drawImage(img, 12, 204, 46, 46);
      } else {
        c.fillStyle = activa ? '#59e6ff' : '#ffb347';
        c.beginPath(); c.arc(35, 227, 22, 0, 7); c.fill();
      }
    } catch (e) { /* */ }
    c.textAlign = 'left';
    const nm = String(def.name || '').toUpperCase();
    c.fillStyle = '#ffffff';
    c.font = 'bold ' + (nm.length > 15 ? 26 : 32) + 'px Trebuchet MS, sans-serif';
    c.fillText(nm, 70, 240);
    c.fillStyle = activa ? '#aef3ff' : '#ffe0b0';
    c.font = 'bold 19px Trebuchet MS, sans-serif';
    c.fillText(activa ? '¡ESQUIVA LA TRAMPA!' : String(CFG.rival).toUpperCase() + ' PREPARA…', 70, 216);
    this._psTex.needsUpdate = true;
    this.powerSign.visible = true;
  }
"""
eo = eo[:i0] + EO_PS + eo[i1:]
print('  ok _psMuestra')

# ── E14. carga del arte del cartel en build() ────────────────────────
eo = rep(eo, "        } catch (e) { /* sin icono: círculo de color */ }\n      }\n    }",
         "        } catch (e) { /* sin icono: círculo de color */ }\n      }\n"
         "      // v3.2.0: el arte «Super Power!!» de la casa (mismo sello que\n"
         "      // los otros campeonatos) como fondo del cartel del superpoder\n"
         "      this._psBanner = new Image();\n"
         "      this._psBanner.src = this._A('superpower.png');\n    }", 'banner img')

# ── E15. métodos de la pistola + _testActivo antes de aiMul() ────────
GUN_METHODS = """  /* ===================== v3.2.0 · PISTOLA LÁSER (MURO 2) ==================
   *  Port del pegamento de La Locura (v2.44/2.74): getter de armado,
   *  disparo con RAYCAST real sobre los ladrillos, carga perezosa del
   *  pistol.glb del artista, encaje normalizado y visibilidad por frame. */
  get gunArmed() {
    const g = this.game;
    const ark = this.arkanoid;
    return !!(this.state === 'prueba' && ark && ark.active && ark.variant === 2 &&
      ark.phase === 'play' &&
      g.gunMounts && g.gunMounts[1 - g.paddleHand] &&
      g.gunMounts[1 - g.paddleHand].visible);
  }

  fireGun(i) {
    const g = this.game;
    const mount = g.gunMounts && g.gunMounts[i];
    if (!mount) return;
    const now = performance.now() / 1000;
    if (now - this._gunLast < 0.16) return;
    this._gunLast = now;
    const pos = new THREE.Vector3();
    const q = new THREE.Quaternion();
    mount.getWorldPosition(pos);
    mount.getWorldQuaternion(q);
    const dir = new THREE.Vector3(0, Math.sin(GUN_MOUNT_PITCH), -Math.cos(GUN_MOUNT_PITCH))
      .applyQuaternion(q).normalize();
    pos.add((this._gunMuzzle || GUN_MUZZLE).clone().applyQuaternion(q));
    // RAYCAST: el primer ladrillo que cruza el haz recibe SU lógica
    let hitDist = 6.0;
    let hitBrick = null;
    let hitTime = false;
    const hitPoint = new THREE.Vector3();
    const ark = this.arkanoid;
    if (ark && ark.active && ark.bricks && ark.bricks.length) {
      const ray = new THREE.Raycaster(pos, dir, 0, 6.0);
      const meshes = ark.bricks.filter((b) => b.alive).map((b) => b.mesh);
      if (ark._timeBrick && ark.timeMesh) meshes.push(ark.timeMesh);
      const hits = ray.intersectObjects(meshes, false);
      if (hits.length) {
        hitDist = hits[0].distance;
        hitPoint.copy(hits[0].point);
        hitBrick = ark.bricks.find((b) => b.mesh === hits[0].object) || null;
        hitTime = !hitBrick && hits[0].object === ark.timeMesh;
      }
    }
    const mid = pos.clone().addScaledVector(dir, hitDist / 2);
    const beam = new THREE.Mesh(
      new THREE.CylinderGeometry(0.0042, 0.0042, hitDist, 6, 1, true),
      new THREE.MeshBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0.95,
        depthWrite: false, blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide,
      }),
    );
    beam.position.copy(mid);
    beam.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
    const glow = new THREE.Mesh(
      new THREE.CylinderGeometry(0.012, 0.012, hitDist, 8, 1, true),
      new THREE.MeshBasicMaterial({
        color: 0x66d9ff, transparent: true, opacity: 0.4,
        depthWrite: false, blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide,
      }),
    );
    glow.position.copy(mid);
    glow.quaternion.copy(beam.quaternion);
    g.scene.add(beam);
    g.scene.add(glow);
    this._beams.push({ mesh: beam, glow, t: 0 });
    if (hitBrick) {
      g.rig.updateWorldMatrix(true, false);
      const lp = g.rig.worldToLocal(hitPoint.clone());
      ark._flash(lp);
      ark.laserHit(hitBrick);
    } else if (hitTime) {
      g.rig.updateWorldMatrix(true, false);
      const lp = g.rig.worldToLocal(hitPoint.clone());
      ark._flash(lp);
      ark._breakTimeBrick();
    }
    g.audio.playOsc(1760, 320, 0.1, 'sawtooth', 0.07, 0);
    g.audio.playOsc(2640, 660, 0.08, 'sine', 0.045, 0);
    g.audio.playNoise(0.05, 3400, 2.2, 0.035, 0);
    if (g.renderer.xr.isPresenting) g.haptic(i, 0.4, 60);
  }

  _loadGunArt() {
    const g = this.game;
    if (!g.gunMounts) return;
    if (this._gunArtModel) { this._attachGunArt(); return; }
    if (!GUN_ART_URL || this._gunArtLoading) return;
    this._gunArtLoading = true;
    try {
      new GLTFLoader().load(GUN_ART_URL, (gltf) => {
        this._gunArtLoading = false;
        try {
          const model = this._normalizeGun(gltf.scene);
          if (!model) return;
          this._gunArtModel = model;
          this._attachGunArt();
          console.info('[estacion] pistol.glb del artista montada (MURO 2)');
        } catch (e) { console.warn('[estacion] pistola: normalización KO', e); }
      }, undefined, () => {
        this._gunArtLoading = false;
        console.warn('[estacion] pistol.glb no disponible — se mantiene la del core');
      });
    } catch (e) { this._gunArtLoading = false; }
  }

  _normalizeGun(scene) {
    const box = new THREE.Box3().setFromObject(scene);
    if (box.isEmpty()) return null;
    const size = box.getSize(new THREE.Vector3());
    const root = new THREE.Group();
    root.add(scene);
    const ax = [['x', size.x], ['y', size.y], ['z', size.z]].sort((a, b) => b[1] - a[1]);
    if (ax[0][0] === 'x') scene.rotation.y = Math.PI / 2;
    else if (ax[0][0] === 'y') scene.rotation.x = -Math.PI / 2;
    const s2 = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
    const ax2 = [['x', s2.x], ['y', s2.y]].sort((a, b) => b[1] - a[1])[0][0];
    if (ax2 === 'x') scene.rotateZ(Math.PI / 2);
    const s3 = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
    const len = Math.max(s3.x, s3.y, s3.z) || 1;
    root.scale.setScalar(0.32 / len);
    try {
      root.updateMatrixWorld(true);
      const lv = new THREE.Vector3(), tv = new THREE.Vector3();
      let found = false;
      root.traverse((o) => {
        if (!o.isMesh || !o.geometry || !o.geometry.attributes) return;
        const pa = o.geometry.attributes.position;
        if (!pa) return;
        for (let i2 = 0; i2 < pa.count; i2++) {
          tv.fromBufferAttribute(pa, i2).applyMatrix4(o.matrixWorld);
          if (!found || tv.y < lv.y) { lv.copy(tv); found = true; }
        }
      });
      if (found && lv.z < 0) root.rotation.y += Math.PI;
    } catch (e) { /* orientación original si el barrido falla */ }
    const b4 = new THREE.Box3().setFromObject(root);
    const c = b4.getCenter(new THREE.Vector3());
    root.position.set(-c.x, -b4.min.y - 0.055, -c.z);
    try {
      const bFin = new THREE.Box3().setFromObject(root);
      const dimF = bFin.getSize(new THREE.Vector3());
      this._gunMuzzle = new THREE.Vector3(0, dimF.y - 0.075, bFin.min.z + 0.015);
    } catch (e) { this._gunMuzzle = new THREE.Vector3(0, 0.02, -0.16); }
    try {
      const fin = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
      window.__PP_EO_GUN_INFO = {
        len: +fin.z.toFixed(3), alto: +fin.y.toFixed(3), ancho: +fin.x.toFixed(3),
      };
    } catch (e) { /* */ }
    return root;
  }

  _attachGunArt() {
    const g = this.game;
    if (!g.gunMounts || !this._gunArtModel) return;
    this._restoreGun();
    for (const gm of g.gunMounts) {
      if (!gm) continue;
      for (const ch of gm.children) ch.visible = false;
      const art = this._gunArtModel.clone(true);
      art.userData.__eoArt = true;
      gm.add(art);
      this._gunArt.push({ mount: gm, art });
    }
  }

  _restoreGun() {
    for (const rec of this._gunArt || []) {
      const gm = rec.mount;
      if (!gm) continue;
      gm.remove(rec.art);
      for (const ch of gm.children) ch.visible = true;
    }
    this._gunArt = [];
  }

  _gunUpdate(dt) {
    const g = this.game;
    const ark = this.arkanoid;
    const ark2On = !!(ark && ark.active && ark.variant === 2 &&
      g.renderer && g.renderer.xr && g.renderer.xr.isPresenting);
    const holdPhase = ark && (ark.phase === 'serve' || ark.phase === 'intro' ||
      ark.phase === 'result');
    const armed = ark2On && !holdPhase;
    if (armed && !this._gunHintDone) {
      this._gunHintDone = true;
      try { g.rules.message = T('ark_gun_on'); } catch (e) { /* */ }
    }
    if (ark2On && !this._gunArtModel) this._loadGunArt();
    if (ark2On && this._gunArtModel && (this._gunArt || []).length === 0) {
      this._attachGunArt();
    }
    if (g.gunMounts) {
      for (let k = 0; k < 2; k++) {
        if (g.gunMounts[k]) g.gunMounts[k].visible = armed && k === g.ballHand;
      }
    }
    for (let i = this._beams.length - 1; i >= 0; i--) {
      const b = this._beams[i];
      b.t += dt;
      const f = 1 - b.t / 0.16;
      if (f <= 0) {
        for (const m of [b.mesh, b.glow]) {
          if (!m) continue;
          g.scene.remove(m);
          m.geometry.dispose();
          m.material.dispose();
        }
        this._beams.splice(i, 1);
        continue;
      }
      b.mesh.material.opacity = 0.95 * f;
      if (b.glow) b.glow.material.opacity = 0.4 * f;
    }
  }

  _purgeBeams() {
    if (!this._beams || !this._beams.length) return;
    const g = this.game;
    for (const b of this._beams) {
      for (const m of [b.mesh, b.glow]) {
        if (!m) continue;
        g.scene.remove(m);
        try { m.geometry.dispose(); } catch (e) { /* */ }
        try { m.material.dispose(); } catch (e) { /* */ }
      }
    }
    this._beams.length = 0;
  }

  /** v3.2.0 · objeto de PRUEBA activo: el muro primero, las DIANAS legacy
   *  después (el contrato testActive/testStep del núcleo no cambia). */
  _testActivo() {
    if (this.arkanoid && this.arkanoid.active) return this.arkanoid;
    if (this.prueba && this.prueba.stepActive && this.prueba.stepActive()) return this.prueba;
    return null;
  }

  aiMul() {
    if (this.state !== 'duelo') return 1;"""
eo = rep(eo, "  aiMul() {\n    if (this.state !== 'duelo') return 1;", GUN_METHODS, 'métodos pistola')

# ── E16. MapaEO: arte nuevo + nodos re-medidos ───────────────────────
eo = rep(eo, """    this.IMG_W = 1380;
    this.IMG_H = 752;
    this.PW = 1.68;
    this.PH = 1.68 * 752 / 1380;""",
"""    this.IMG_W = 1376;               // v3.2.0: mapa nuevo del dueño
    this.IMG_H = 768;
    this.PW = 1.68;
    this.PH = 1.68 * 768 / 1376;""", 'MapaEO dims')
eo = rep(eo, '{ x: 210, y: 260, r: 100, tapa: false, ts: 1.0 },', '{ x: 210, y: 266, r: 100, tapa: false, ts: 1.0 },', 'nodo0')
eo = rep(eo, '{ x: 455, y: 500, r: 120, tapa: true, ts: 1.2 },', '{ x: 455, y: 511, r: 120, tapa: true, ts: 1.2 },', 'nodo1')
eo = rep(eo, '{ x: 700, y: 260, r: 100, tapa: true, ts: 1.0 },', '{ x: 700, y: 266, r: 100, tapa: true, ts: 1.0 },', 'nodo2')
eo = rep(eo, '{ x: 945, y: 500, r: 120, tapa: true, ts: 1.2 },', '{ x: 945, y: 511, r: 120, tapa: true, ts: 1.2 },', 'nodo3')
eo = rep(eo, '{ x: 1190, y: 260, r: 100, tapa: true, ts: 1.0 },', '{ x: 1190, y: 266, r: 100, tapa: true, ts: 1.0 },', 'nodo4')

# ── E17. export del módulo: decor + room + tests + reenter + gun url ──
eo = rep(eo, '  decor: {"pieces": [{"file": "assets/decor/troquel1.png", "h": 1.2, "x": -2.55, "z": -2.5, "sway": 0.5}, {"file": "assets/decor/troquel2.png", "h": 0.8, "x": 2.1, "z": -2.5, "sway": 0.3}, {"file": "assets/decor/troquel3.png", "h": 1, "x": 2.45, "z": -0.85, "sway": 0.4}]},',
         '  decor: {"pieces": [{"file": "assets/decor/escena_cohete.png", "h": 1.15, "x": -2.55, "z": -2.5, "sway": 0.5}, {"file": "assets/decor/escena_astro.png", "h": 1.0, "x": 2.1, "z": -2.5, "sway": 0.3}, {"file": "assets/decor/escena_lander.png", "h": 0.95, "x": 2.45, "z": -0.85, "sway": 0.4}, {"file": "assets/decor/escena_telescopio.png", "h": 0.62, "x": -2.45, "z": -0.85, "sway": 0.35}]},   // v3.2.0: recortables reales del dueño', 'export decor')
eo = rep(eo, """  testActive() { return !!(CTRL && CTRL.prueba && CTRL.prueba.stepActive()); },
  testStep(dt) {
    if (CTRL && CTRL.prueba && CTRL.prueba.stepActive()) {
      try { CTRL.prueba.step(dt); }
      catch (e) { console.warn('[estacion.testStep]', e); }
    }
  },""",
"""  testActive() { return !!(CTRL && CTRL._testActivo()); },   // v3.2.0: muro primero
  testStep(dt) {
    const o = CTRL && CTRL._testActivo();
    if (o) {
      try { o.step(dt); }
      catch (e) { console.warn('[estacion.testStep]', e); }
    }
  },""", 'export tests')
eo = rep(eo, "  reenter() { if (CTRL) CTRL.reenter(); },",
         "  reenter() {   // v3.2.0: en pleno muro, reanuda la prueba\n"
         "    if (CTRL && CTRL.arkanoid && CTRL.arkanoid.active) {\n"
         "      try { CTRL.arkanoid.reenter(); } catch (e) { /* */ }\n"
         "      return;\n"
         "    }\n"
         "    if (CTRL) CTRL.reenter();\n"
         "  },", 'export reenter')
eo = rep(eo, "    STEP = window.__PP_CORE.stepPhysics || null;",
         "    STEP = window.__PP_CORE.stepPhysics || null;\n"
         "    // v3.2.0: pistola real del artista para el MURO 2 (ARKANOID II)\n"
         "    try { GUN_ART_URL = new URL('./assets/pistol.glb', import.meta.url).href; } catch (e) { /* */ }", 'GUN_ART_URL')

open(EO, 'w', encoding='utf-8').write(eo)
print('\nEscrito', EO, f'({len(eo):,} B)')
