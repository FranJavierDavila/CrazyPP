function renderPlayBtn() {
  const en = TLang() === 'en';
  if (playEs && playEn) {
    playEs.style.display = en ? 'none' : '';
    playEn.style.display = en ? '' : 'none';
  }
}
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { PP_ICONS, T, TLang, WORLDRANK, __ppLang, applyLangDOM, ppPlayerName, setLang } from './c00_pre_three.js';
import { fixInvertedMeshes, loadGunModel, loadPaddleModel, makeGunVisual, makePaddleVisual } from './c01_modelos_3d.js';
import { AI_PRESETS, CONFIG_LOGROS, CONFIG_MEDALLAS, CONFIG_PIELES, CONFIG_RALLY, CONFIG_TORNEOS, DIMS, SERVE_ASSIST_TIERS, SERVE_TUNE, scalePreset } from './c02_cfg_escena.js';
import { CCD_TUNE, bladeNormalLocal, createPaddleSim, sdfBlade, setPaddleBasis, sweepBallVsBlade, tmpPrev } from './c04_fisica_ccd.js';
import { __ppServeTelemetry, applyServeProgressiveAssist, collidePaddleSweep, computeShotVelocityReal, findServeVelocity, simulateServePath, stepPhysics, testPaddleContact } from './c05_colisiones_ia_golpeo.js';
import { NetLink } from './c09_red_netlink.js';
import { PPNET } from './c09b_red_nucleo.js';
import { BALL_HAND_LIFT } from './c10_menu_saque.js';
import { PingPongGame, arBtn, overlay, playEn, playEs, statusEl, vrbtn } from './c12_pingponggame.js';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
/* DEPS-FASE2-FIN */

// v2.28: la portada ya no muestra agarres ni estadísticas — los callbacks
// se conservan (el progreso sigue persistiendo y anunciándose en el juego)
function refreshGrips() { /* el ajuste de agarres vive en VR (Entrenar) */ }
function renderStats() { /* el progreso persiste; sin chips en la portada */ }

// wrapText: parte un texto en líneas ajustadas al ancho dado. El menú lo
// usaba desde v2.19 SIN DEFINIR (bug latente en el estado de error de red):
// corregido en v2.28.
export function wrapText(c, text, x, y, maxW, lh) {
  const words = String(text || '').split(/\s+/);
  let line = '';
  let yy = y;
  for (const w of words) {
    const test = line ? line + ' ' + w : w;
    if (c.measureText(test).width > maxW && line) {
      c.fillText(line, x, yy);
      line = w;
      yy += lh;
    } else line = test;
  }
  if (line) c.fillText(line, x, yy);
  return yy;
}

// Cargar el modelo de la pala antes de arrancar la escena
loadPaddleModel().then((paddleModel) => {
  // r145 · sin canvas NO hay boot: el arnés de batería (Node) importa c12 y
  // por el bloque deps-fase2 evalúa c13 — sin guard, el boot construía un
  // WebGLRenderer(null) y mataba el proceso DEPRISA tras el import. En el
  // navegador el canvas #c siempre existe: el guard es transparente.
  const _bootCanvas = (typeof document !== 'undefined') ? document.getElementById('c') : null;
  if (!_bootCanvas) return;
  const game = new PingPongGame(_bootCanvas, paddleModel, {
    // v2.30: sin HUD de espectador — onScore/onMessage ya no tienen destino 2D
    onGrips(list, active) {
      refreshGrips(list, active);
    },
    onStats(stats) {
      renderStats(stats);
    },
    onTheme() { /* los chips de tema eran de la tarjeta antigua (2D) */ },
    onXRState(inVR) {
      if (inVR) {
        overlay.classList.add('hidden');
        window.__ppMusic?.pause();    // v2.28: la música de portada se queda fuera
        // r152: el aviso «toca para entrar» ya no sirve dentro del casco
        try { const _tv = document.getElementById('tapvr'); if (_tv) _tv.remove(); } catch (eTV) { /* */ }
      } else {
        overlay.classList.remove('hidden');
        statusEl.textContent = T('status_pause');
        window.__ppMusic?.resume();   // de vuelta en la portada suena otra vez
      }
    },
  });
  window.__game = game;
  // r151 · ARRANQUE DIRECTO AL SALÓN (petición del dueño): la portada se
  // retira y el Hall del usuario ES la pantalla de entrada — sin pantalla
  // intermedia. La sesión VR sigue necesitando un gesto del navegador
  // (requestSession es innegociable): el gran botón —compacto, abajo— la
  // pide exactamente igual que siempre.
  try { game.enterHall(); } catch (eHall2D) { /* nunca rompe el boot */ }
  try { _bootCanvas.classList.add('listo'); } catch (eVis) { /* */ }
  // Primer gesto en 2D: el AudioContext solo puede nacer DENTRO de un gesto
  // (política de autoplay del navegador). enterHall pidió la música del
  // salón sin contexto y c03 la descarta en silencio (_loadHallMusic sale
  // si !ctx) — el re-armado la devuelve cuando el usuario toca la pantalla.
  const _kick2D = () => {
    try { game.rearmHallAudio(); } catch (eRA) { /* */ }
    try {
      window.removeEventListener('pointerdown', _kick2D);
      window.removeEventListener('keydown', _kick2D);
    } catch (eOff) { /* */ }
  };
  try {
    window.addEventListener('pointerdown', _kick2D);
    window.addEventListener('keydown', _kick2D);
  } catch (eKick) { /* */ }
  // r152 · ENTRADA EN UN TOQUE (?vr=1 / ?ar=1 desde la LANDING-portada): la
  // raíz del dominio vuelve a ser la portada clásica y llega aquí con
  // game.html?vr=1. La activación del clic NO cruza la navegación (WebXR
  // exige un gesto DENTRO de este documento — imposible de esquivar), así
  // que el último toque se hace aquí: cualquier puntero/tecla dispara la
  // sesión VR directo al salón, sin segunda diana. El aviso es
  // pointer-events:none (00_head) y el listener vive en window: acepta el
  // toque en CUALQUIER parte del lienzo.
  try {
    const _q = new URLSearchParams(location.search);
    const _autoAR = _q.get('ar') === '1';
    if (_q.get('vr') === '1' || _autoAR) {
      const _es = TLang() !== 'en';
      const _hint = document.createElement('div');
      _hint.id = 'tapvr';
      _hint.textContent = _es
        ? (_autoAR ? 'TOCA EN CUALQUIER PARTE PARA ENTRAR EN TU HABITACIÓN'
                   : 'TOCA EN CUALQUIER PARTE PARA ENTRAR EN VR')
        : (_autoAR ? 'TAP ANYWHERE TO ENTER YOUR ROOM'
                   : 'TAP ANYWHERE TO ENTER VR');
      document.body.appendChild(_hint);
      if (_autoAR) {
        // mismo camino que el arbtn de la portada antigua: pref persistente
        // + pendingAR — enterVR pide immersive-ar si el visor la soporta y
        // el AJUSTES del juego alterna passthrough ⇄ sala al vuelo
        try { localStorage.setItem('ppxr_pending_ar', '1'); } catch (ePA) { /* */ }
        game.pendingAR = true;
      }
      const _goVR = () => {
        try {
          window.removeEventListener('pointerdown', _goVR);
          window.removeEventListener('keydown', _goVR);
        } catch (eOff) { /* */ }
        try { game.audio.ensure(); } catch (eAU) { /* */ }
        _hint.textContent = _es ? 'ARRANCANDO VR…' : 'STARTING VR…';
        game.enterVR(false, _autoAR)
          .catch((err) => {
            // sin WebXR (escritorio): mensaje honesto, el salón sigue en 2D
            _hint.textContent = '⚠️ ' + ((err && err.message)
              || (_es ? 'No se pudo entrar en VR' : 'Could not enter VR'));
            _hint.classList.add('mal');
          });
      };
      window.addEventListener('pointerdown', _goVR);
      window.addEventListener('keydown', _goVR);
    }
  } catch (eTap) { /* nunca rompe el boot */ }
  window.__NetLink = NetLink;   // accesible para pruebas headless (módulo ES)
  try { window.__PPNET = PPNET; } catch (e0) { /* r79: núcleo de red para QA */ }
  // v2.38: cargar la pistola de rayos y montarla en ambos mandos
  loadGunModel().then((gunModel) => {
    if (!game.gunMounts) return;
    for (const gm of game.gunMounts) gm.add(makeGunVisual(gunModel));
    window.__gunLoaded = true;
    console.info('Pistola de rayos montada (superpoder ARKANOID)');
  });
  // v2.27: ganchos de i18n para pruebas headless (el módulo no expone globales)
  window.__T = T; window.__TLang = TLang; window.__setLang = setLang;
  window.__applyLangDOM = applyLangDOM;
  // gancho de depuración para pruebas headless (física de saque y constantes)
  // v3.1.0-SRV2: SERVE_TUNE es VIVO (ajustable desde consola sin recargar) y
  // lastServe guarda la telemetría del último saque (error angular, mezcla
  // aplicada y veredicto del simulador) para QA y puesta a punto en casco.

  // v3.5.0-ESC1 · PUENTE CCD PARA EL ESCUDO DE PALA: el módulo del campeonato
  // no ve las funciones internas del núcleo; este adaptador expone el MISMO
  // barrido esfera-pala de CCD1 (collidePaddleSweep, espacio local de la
  // hoja, punto dulce, reflexión con la velocidad de la pala, efecto) para
  // cualquier proyectil con { pos, vel, spin } y su posición previa. La
  // especificación de la etapa lo pide explícito: «la misma detección
  // continua de colisiones» y «la física habitual de rebote, rozamiento y
  // efecto (spin)». El anti-rebote por ORBE lo gestiona el módulo (por eso
  // el cooldown de la pala se limpia aquí fuera — varios orbes a la vez).
  window.__PP_PADDLE_SWEEP = function (ballLike, prevPos, pad, events) {
    try {
      tmpPrev.copy(prevPos);
      const ok = collidePaddleSweep(ballLike, pad, 0, 1, events);
      if (ok) pad.cooldown = 0;
      return ok;
    } catch (e) { return false; }
  };

  window.__ppDebug = { findServeVelocity, simulateServePath, DIMS,
  serveTiers: SERVE_ASSIST_TIERS, serveTune: SERVE_TUNE, lastServe: null,
  applyServeProgressiveAssist,
  // v3.1.2-CCD1 · tune VIVO de la CCD + piezas para QA en casco/consola
  ccdTune: CCD_TUNE, sweepBallVsBlade, sdfBlade, bladeNormalLocal };
  // v3.1.0-SRV2 · LABORATORIO DE SAQUE (QA headless de los 9 casos del
  // requisito): monta una pala sintética contra una bola sintética y pasa
  // por la MISMA collidePaddle + asistencia que el juego real. Devuelve
  // {hit, event, faceSide, exitVel, exitSpeed, offC…} — sin tocar el juego.
  window.__PP_SERVE_LAB = (o) => {

    o = o || {};
    // geometría por defecto = SAQUE: goma mirando a la red (yaw 180°),
    // pala swingueando hacia la red (−z) y bola flotando delante de la goma
    const yaw = THREE.MathUtils.degToRad(o.yawDeg != null ? o.yawDeg : 180);
    const pitch = THREE.MathUtils.degToRad(o.pitchDeg || 0);
    const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(pitch, yaw, 0, 'YXZ'));
    const pad = createPaddleSim('player', 0);
    pad.active = true; pad.cooldown = 0;
    pad.serveFlight = o.serveFlight !== false;
    pad.extraReach = o.extraReach != null ? o.extraReach :
      (o.serveFlight === false ? 0 : SERVE_ASSIST_TIERS.medium.reach);
    setPaddleBasis(pad, q);
    // v3.1.1-FEEL1 · sincronizar LA BASE COMPLETA prev* (como hace
    // updatePaddleSim en el juego real): sin esto, la base interpolada del
    // CCD lerpea contra los (0,0,1) iniciales y el plano de contacto sale
    // inclinado fantasma (el flip de normal por velocidad lo enmascaraba).
    pad.prevNormal.copy(pad.normal);
    pad.prevRight.copy(pad.right);
    pad.prevUp.copy(pad.up);
    pad.pos.set(o.padX || 0.30, o.padY || 1.05, o.padZ == null ? -0.60 : o.padZ);
    pad.prev.copy(pad.pos);
    pad.vel.set(o.padVelX || 0, o.padVelY || 0, o.padVelZ == null ? -2.6 : o.padVelZ);
    pad.omega.set(0, 0, 0);
    // bola DELANTE de la goma (en el lado que mira la goma): n = normal real
    const n = new THREE.Vector3(0, 0, 1).applyQuaternion(q);
    const dist = o.dist != null ? o.dist : 0.05;
    const bp = pad.pos.clone().addScaledVector(n, dist);
    bp.x += o.offX || 0; bp.y += o.offY || 0;
    const bv = new THREE.Vector3(o.ballVelX || 0, o.ballVelY == null ? -0.2 : o.ballVelY,
      o.ballVelZ == null ? -0.1 : o.ballVelZ);
    const ball = { pos: bp, vel: bv.clone(), spin: new THREE.Vector3(),
      radius: DIMS.ballRadius };
    const prevPos = bp.clone();
    const dt = o.dt || 1 / 72;
    prevPos.addScaledVector(bv, -dt);          // dónde estaba la bola un frame atrás
    const events = [];
    testPaddleContact(ball, prevPos, [pad], events);
    const out = { hit: events.some((e) => e.type === 'paddle'),
      events: events.map((e) => e.type),
      exitVel: ball.vel.toArray(),
      exitSpeed: +ball.vel.length().toFixed(3),
      exitZ: +ball.vel.z.toFixed(3) };
    if (o.assist) {
      out.assist = applyServeProgressiveAssist(ball, pad,
        SERVE_ASSIST_TIERS[o.tier || 'medium']);
      out.assist.err = out.assist.err != null ? +out.assist.err.toFixed(4) : null;
      out.assist.w = +out.assist.w.toFixed(4);
      out.sim = out.assist.sim;
      out.finalSpeed = +ball.vel.length().toFixed(3);
    }
    return out;
  };
  /* v3.1.1-FEEL1 · LABORATORIO GAME-FEEL (QA headless de los 3 ajustes del
   * dueño). Tres escenarios con la MISMA física del juego (stepPhysics):
   *  mode 'grace'  — saque: la bola cruza el plano justo FUERA del borde de
   *                  la hoja y la pala, barriendo en diagonal, la alcanza unos
   *                  ms después. Con gracia (lateMs>0) conecta; con lateMs=0
   *                  no hay golpe. Devuelve {hit, hitMs}.
   *  mode 'decay'  — bola botando sobre la pala QUIETA en horizontal: los
   *                  botes DECAEN (sin suelo de salida) hasta el reposo; la
   *                  bola NUNCA atraviesa la hoja y los micro-contactos no
   *                  emiten eventos. Devuelve {bounces, restSpeed, fellThrough…}.
   *  mode 'stroke' — la pala en movimiento conserva el suelo de salida pleno
   *                  (2,3 m/s): el resto del juego no cambia. Devuelve {maxExit}. */
  window.__PP_FEEL_LAB = (o) => {
    o = o || {};
    const mode = o.mode || 'grace';
    const dt = o.dt || 1 / 240;
    if (mode === 'grace') {
      // SAQUE: bola llegando MUY JUSTA al borde de la hoja — su estela pasa
      // ~6,5 mm más allá del radio de asistencia normal (fuera del alcance
      // SIN gracia) pero dentro del margen lateInPlane. Sin gracia el golpe
      // no existe jamás (todos los pasos fallan); con la ventana lateMs la
      // detección sigue viva y el golpe CONECTA (lo que se ve, cuenta).
      const q = new THREE.Quaternion().setFromEuler(
        new THREE.Euler(0, Math.PI, 0, 'YXZ'));
      const pad = createPaddleSim('player', 0);
      pad.active = true; pad.cooldown = 0;
      pad.serveFlight = true;
      pad.extraReach = 0;                 // aislamos la gracia: sin margen extra
      setPaddleBasis(pad, q);
      pad.pos.set(o.padX || 0.30, o.padY || 1.05, o.padZ == null ? -0.60 : o.padZ);
      pad.prev.copy(pad.pos);
      pad.vel.set(o.padVelX == null ? 0 : o.padVelX, 0, o.padVelZ == null ? -2.0 : o.padVelZ);
      pad.omega.set(0, 0, 0);
      const reach0 = DIMS.bladeRadius + DIMS.ballRadius + SERVE_TUNE.serveFlightAssist;
      const offX = o.offX != null ? o.offX : reach0 + 0.0065;  // fuera del alcance normal
      const bp = new THREE.Vector3(pad.pos.x + offX,
        pad.pos.y + DIMS.bladeCenterUp,                      // a la ALTURA de la hoja
        pad.pos.z - (o.dist != null ? o.dist : 0.05));       // DELANTE de la goma (n = (0,0,-1))
      const ball = { pos: bp, vel: new THREE.Vector3(0, -0.2, o.ballVelZ == null ? -0.1 : o.ballVelZ),
        spin: new THREE.Vector3(), radius: DIMS.ballRadius };
      const steps = o.steps || 40;        // ~167 ms de vida del intento
      let hit = false, hitMs = -1;
      const trace = o.dbg ? [] : null;
      for (let s = 0; s < steps && !hit; s++) {
        // la pala barre hacia la bola; la bola la integra stepPhysics (con
        // subpasos de 1/480 y el decremento de gracia POR SUBPASO, igual que
        // el juego — testPaddleContact decrementa 16 ms fijos por llamada y
        // mataría la ventana en el primer paso a esta cadencia)
        pad.prev.copy(pad.pos);
        pad.prevNormal.copy(pad.normal);
        pad.prevRight.copy(pad.right);
        pad.prevUp.copy(pad.up);
        pad.pos.addScaledVector(pad.vel, dt);
        const ev2 = [];
        stepPhysics(dt, ball, [pad], ev2, null);
        if (ev2.some((e) => e.type === 'paddle')) { hit = true; hitMs = +(s * dt * 1000).toFixed(1); }
        // v3.1.2-CCD1 · traza de puesta a punto: gracia viva, distancia al
        // plano de la hoja y separación EN EL PLANO (centro de hoja)
        if (trace) {
          const c = new THREE.Vector3().copy(pad.pos)
            .addScaledVector(pad.up, DIMS.bladeCenterUp);
          const rel = new THREE.Vector3().copy(ball.pos).sub(c);
          trace.push({ s, graceMs: +((ball.__serveGrace || 0) * 1000).toFixed(2),
            dPlaneMm: +(rel.dot(pad.normal) * 1000).toFixed(2),
            inPlaneMm: +(Math.hypot(rel.dot(pad.right), rel.dot(pad.up)) * 1000).toFixed(2),
            ev: ev2.map((e) => e.type).join(',') || '-' });
        }
      }
      return { mode, hit, hitMs, lateMs: SERVE_TUNE.lateMs, offX: +offX.toFixed(4), trace };
    }
    // ---- decay / stroke: pala horizontal (goma arriba) en el aire libre ----
    const q = new THREE.Quaternion().setFromEuler(
      new THREE.Euler(-Math.PI / 2, 0, 0, 'YXZ'));
    const pad = createPaddleSim('player', 0);
    pad.active = true; pad.cooldown = 0;
    pad.serveFlight = false; pad.extraReach = 0;
    setPaddleBasis(pad, q);
    pad.pos.set(0.30, 1.00, 0.30);
    pad.prev.copy(pad.pos);
    pad.vel.set(0, 0, 0);
    pad.omega.set(0, 0, 0);
    const bladeCenter = new THREE.Vector3(0.30, 1.00, 0.30 - DIMS.bladeCenterUp);
    const ball = { pos: bladeCenter.clone().add(new THREE.Vector3(0, o.dropH || 0.35, 0)),
      vel: new THREE.Vector3(0, 0, 0), spin: new THREE.Vector3() };
    const events = [];
    const bounces = [];
    const trace = o.trace ? [] : null;
    const steps = o.steps || (mode === 'decay' ? 1500 : 150);
    if (mode === 'decay') {
      for (let s = 0; s < steps; s++) {
        // pala quieta: sincronizar prev Y LA BASE COMPLETA (como hace
        // updatePaddleSim en el juego real — si no, la base interpolada del
        // CCD lerpea contra los (0,0,1) iniciales y crea un plano fantasma)
        pad.prev.copy(pad.pos);
        pad.prevNormal.copy(pad.normal);
        pad.prevRight.copy(pad.right);
        pad.prevUp.copy(pad.up);
        const ev2 = [];
        stepPhysics(dt, ball, [pad], ev2, null);
        for (const e of ev2) if (e.type === 'paddle') bounces.push(+e.speed.toFixed(3));
        events.push(...ev2);
        if (trace) trace.push([+(s * dt).toFixed(4), +ball.pos.y.toFixed(4),
          +ball.vel.y.toFixed(3), +pad.cooldown.toFixed(3),
          ev2.map((e) => e.type).join(',') || '-']);
      }
      return { mode, bounces, eventCount: events.length,
        restSpeed: +ball.vel.length().toFixed(3),
        gap: +(ball.pos.y - 1.0).toFixed(4),
        fellThrough: ball.pos.y < 0.985, trace,
        dbg: { normal: pad.normal.toArray().map((v) => +v.toFixed(3)),
          up: pad.up.toArray().map((v) => +v.toFixed(3)),
          pos: pad.pos.toArray().map((v) => +v.toFixed(3)),
          vel: pad.vel.toArray().map((v) => +v.toFixed(4)) } };
    }
    // stroke: la pala SUBE a velocidad constante → suelo pleno intacto
    const vy = o.padVy == null ? 1.5 : o.padVy;
    let exitAtHit = -1;
    for (let s = 0; s < steps; s++) {
      pad.prev.copy(pad.pos);
      pad.prevNormal.copy(pad.normal);
      pad.prevRight.copy(pad.right);
      pad.prevUp.copy(pad.up);
      pad.pos.y += vy * dt;
      pad.vel.set(0, vy, 0);
      const ev2 = [];
      stepPhysics(dt, ball, [pad], ev2, null);
      for (const e of ev2) if (e.type === 'paddle') bounces.push(+e.speed.toFixed(3));
      events.push(...ev2);
      // v3.1.1-FEEL1 · la SALIDA tras el primer golpe (no la entrada): es lo
      // que demuestra si el suelo de salida está vivo
      if (exitAtHit < 0 && ev2.some((e) => e.type === 'paddle')) {
        exitAtHit = +ball.vel.length().toFixed(3);
      }
    }
    return { mode, bounces, maxExit: exitAtHit, eventCount: events.length };
  };
  /* =====================================================================
   *  v3.1.2-CCD1 · LABORATORIO DE LA CCD — window.__PP_CCD_LAB
   *  Banco de pruebas determinista (sin VR) de la detección por barrido
   *  SDF, con los criterios de aceptación del requisito del dueño:
   *   mode 'rain'  — bola a 40 m/s contra pala quieta, N offsets aleatorios
   *                  dentro del disco: 100 % de golpes, 0 túneles (+ variante
   *                  con ángulo de entrada hasta 25°). Detección pura.
   *   mode 'ref'   — comparación con referencia de FUERZA BRUTA (marcha de
   *                  60 000 pasos + bisección): error de TOI en ms y de
   *                  posición de contacto en mm sobre caras, cantos, esquinas
   *                  y rayos oblicuos.
   *   mode 'fastPad'    — pala a 20 m/s hacia bola quieta/lenta (física real
   *                  stepPhysics): golpe correcto.
   *   mode 'frameDrop'  — pala y bola cruzándose en UN frame de 33 ms
   *                  (bajón de FPS): golpe correcto.
   *   mode 'spinBlade'  — pala rotando a ~35 rad/s: golpe correcto con
   *                  normal coherente con la cara.
   *   mode 'edge'  — impactos en canto/esquina (98-104 % del radio): sin
   *                  túnel, normal razonable, SIN dobles golpes.
   *   mode 'energy'     — coherencia energética: la energía saliente nunca
   *                  supera lo que permiten e y la velocidad de la pala.
   *   mode 'perf'  — coste por barrido y por frame de stepPhysics.
   *  Todo con la geometría REAL de la hoja (sin asistencia: R = bladeRadius)
   *  salvo fastPad/frameDrop/spinBlade, que corren el juego completo.
   * ===================================================================== */
  window.__PP_CCD_LAB = (o) => {
    o = o || {};
    const mode = o.mode || 'rain';
    const R = DIMS.bladeRadius, hT = CCD_TUNE.bladeHalfT, rB = DIMS.ballRadius;

    // --- referencia de fuerza bruta: marcha fina + bisección del cruce ---
    const brute = (ax, ay, az, bx, by, bz, Rr) => {
      const N = 60000;
      const dx = (bx - ax) / N, dy = (by - ay) / N, dz = (bz - az) / N;
      let lo = 0, hi = -1, x = ax, y = ay, z = az;
      for (let i = 0; i <= N; i++) {
        if (sdfBlade(x, y, z, Rr, hT) - rB <= 0) { hi = i / N; break; }
        x += dx; y += dy; z += dz; lo = i / N;
      }
      if (hi < 0) return -1;
      for (let i = 0; i < 50; i++) {
        const m = (lo + hi) / 2;
        if (sdfBlade(ax + (bx - ax) * m, ay + (by - ay) * m,
          az + (bz - az) * m, Rr, hT) - rB <= 0) hi = m; else lo = m;
      }
      return (lo + hi) / 2;
    };

    if (mode === 'rain' || mode === 'rainAngled') {
      // determinista: LCG propio (nada de Math.random en QA)
      let seed = (o.seed != null ? o.seed : 12345) >>> 0;
      const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
      const n = o.n || 10000;
      const dtF = o.dt || 1 / 30;             // el peor caso: 33 ms por frame
      const speed = o.speed || 40;            // remate/saque fuerte
      const maxAng = mode === 'rainAngled' ? (o.maxAngDeg != null ? o.maxAngDeg : 25) : 0;
      let hits = 0, tunnels = 0, badT = 0;
      for (let i = 0; i < n; i++) {
        // impacto objetivo dentro del disco (distribución uniforme)
        const rho = R * Math.sqrt(rnd()) * 0.999;
        const th = rnd() * Math.PI * 2;
        const ox = Math.cos(th) * rho, oy = Math.sin(th) * rho;
        // rayo con ángulo de entrada (0 = perpendicular a la cara)
        const ang = maxAng ? rnd() * maxAng * Math.PI / 180 : 0;
        const phi = rnd() * Math.PI * 2;
        const dz = -Math.cos(ang), dxy = Math.sin(ang);
        const dxv = Math.cos(phi) * dxy, dyv = Math.sin(phi) * dxy;
        // inicio del segmento: fuera de la hoja, cruzándola entera en dtF
        const start = 0.5 * speed * dtF + hT + rB + 0.01;
        const ax = ox - dxv * start, ay = oy - dyv * start, az = -dz * start;
        const len = speed * dtF;
        const bx = ax + dxv * len, by = ay + dyv * len, bz = az + dz * len;
        const t = sweepBallVsBlade(ax, ay, az, bx, by, bz, R, hT, rB);
        if (t >= 0) { hits++; if (t < 0 || t > 1) badT++; }
        else {
          // ¿terminó la bola al OTRO lado de la hoja dentro del disco? túnel
          if (bz < -hT && Math.hypot(bx, by) < R) tunnels++;
        }
      }
      return { mode, n, hits, tunnels, badT,
        hitRate: +(hits / n).toFixed(5), dtMs: +(dtF * 1000).toFixed(1),
        speed };
    }

    if (mode === 'ref') {
      // caras, cantos, esquinas y oblicuos: barrido vs fuerza bruta
      let seed = 777 >>> 0;
      const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
      const n = o.n || 300;
      const dtF = 1 / 30, speed = 40;
      let maxDtMs = 0, maxPosMm = 0, hits = 0;
      for (let i = 0; i < n; i++) {
        const rhoFrac = [0, 0.5, 0.9, 0.999, 1.02][Math.floor(rnd() * 5)];
        const rho = R * rhoFrac;
        const th = rnd() * Math.PI * 2;
        const ox = Math.cos(th) * rho, oy = Math.sin(th) * rho;
        const ang = rnd() * 25 * Math.PI / 180;
        const phi = rnd() * Math.PI * 2;
        const dz = -Math.cos(ang), dxy = Math.sin(ang);
        const dxv = Math.cos(phi) * dxy, dyv = Math.sin(phi) * dxy;
        const start = 0.5 * speed * dtF + hT + rB + 0.01;
        const ax = ox - dxv * start, ay = oy - dyv * start, az = -dz * start;
        const len = speed * dtF;
        const bx = ax + dxv * len, by = ay + dyv * len, bz = az + dz * len;
        const t = sweepBallVsBlade(ax, ay, az, bx, by, bz, R, hT, rB);
        const tr = brute(ax, ay, az, bx, by, bz, R);
        if (t < 0 || tr < 0) continue;
        hits++;
        maxDtMs = Math.max(maxDtMs, Math.abs(t - tr) * dtF * 1000);
        maxPosMm = Math.max(maxPosMm, Math.abs(t - tr) * len * 1000);
      }
      return { mode, n: hits, maxDtMs: +maxDtMs.toFixed(4),
        maxPosMm: +maxPosMm.toFixed(4) };
    }

    // ---- casos end-to-end con la física real (stepPhysics completo) ----
    const mkCase = () => {
      // pala del jugador en el aire libre, cara mirando +Z (identity):
      // normal (0,0,1), hoja centrada 14 cm sobre el agarre
      const pad = createPaddleSim('player', 0);
      pad.active = true; pad.cooldown = 0;
      pad.serveFlight = false; pad.extraReach = 0;
      setPaddleBasis(pad, new THREE.Quaternion());
      pad.prevNormal.copy(pad.normal);
      pad.prevRight.copy(pad.right);
      pad.prevUp.copy(pad.up);
      pad.pos.set(0.30, 1.00, 0.30);
      pad.prev.copy(pad.pos);
      pad.vel.set(0, 0, 0);
      pad.omega.set(0, 0, 0);
      const ball = { pos: new THREE.Vector3(), vel: new THREE.Vector3(),
        spin: new THREE.Vector3(), radius: rB };
      return { pad, ball };
    };
    const bladeCenter = (pad) => pad.pos.clone().add(new THREE.Vector3(0, DIMS.bladeCenterUp, 0));

    if (mode === 'fastPad') {
      // pala a 20 m/s hacia una bola quieta/lenta: golpe correcto
      // (la bola está DELANTE de la cara, lado +Z: la pala corre hacia +Z)
      const c = mkCase();
      const spd = o.padSpeed || 20;
      const dt = 1 / 90;
      c.ball.pos.copy(bladeCenter(c.pad)).add(new THREE.Vector3(0, 0, 0.10));
      c.ball.vel.set(0, 0, o.ballVelZ != null ? o.ballVelZ : -0.5);
      let hit = false, exitSpeed = -1;
      for (let s = 0; s < 40 && !hit; s++) {
        c.pad.prev.copy(c.pad.pos);
        c.pad.prevNormal.copy(c.pad.normal);
        c.pad.prevRight.copy(c.pad.right);
        c.pad.prevUp.copy(c.pad.up);
        c.pad.pos.z += spd * dt;                 // la pala corre hacia la bola (+z)
        c.pad.vel.set(0, 0, spd);
        const ev = [];
        stepPhysics(dt, c.ball, [c.pad], ev, null);
        if (ev.some((e) => e.type === 'paddle')) {
          hit = true;
          exitSpeed = +c.ball.vel.length().toFixed(2);
        }
      }
      return { mode, hit, exitSpeed, through: c.ball.pos.z < c.pad.pos.z - rB };
    }

    if (mode === 'frameDrop') {
      // ambos se cruzan en UN frame de 33 ms (bajón de FPS): la bola corre
      // hacia −z a 12 m/s y la pala hacia +z a 6 m/s (cierre de 18 m/s)
      const c = mkCase();
      const dt = 1 / 30;
      c.ball.pos.copy(bladeCenter(c.pad)).add(new THREE.Vector3(0, 0, 0.14));
      c.ball.vel.set(0, 0, -(o.ballSpeed || 12));
      let hit = false;
      for (let s = 0; s < 30 && !hit; s++) {
        c.pad.prev.copy(c.pad.pos);
        c.pad.prevNormal.copy(c.pad.normal);
        c.pad.prevRight.copy(c.pad.right);
        c.pad.prevUp.copy(c.pad.up);
        c.pad.pos.z += 6 * dt;                   // la pala también cruza (6 m/s)
        c.pad.vel.set(0, 0, 6);
        const ev = [];
        stepPhysics(dt, c.ball, [c.pad], ev, null);
        if (ev.some((e) => e.type === 'paddle')) hit = true;
      }
      return { mode, hit, dtMs: +(dt * 1000).toFixed(0),
        gapEnd: +(c.ball.pos.z - c.pad.pos.z).toFixed(4) };
    }

    if (mode === 'spinBlade') {
      // pala rotando sobre el eje vertical: golpe correcto, normal coherente.
      // A 35 rad/s la cara barre 22°/frame: el contacto puede ser de cara o de
      // rim (física correcta en ambos); la coherencia FINA de la normal se
      // acredita con rotación lenta (spinSlow, 6 rad/s ⇒ golpe de cara).
      const c = mkCase();
      const dt = 1 / 90, w = o.omega || 35;
      const q = new THREE.Quaternion();
      c.ball.pos.copy(bladeCenter(c.pad)).add(new THREE.Vector3(0, 0, 0.08));
      c.ball.vel.set(0, 0, -1.2);
      let hit = false, ndot = -1, exitSpeed = -1;
      for (let s = 0; s < 40 && !hit; s++) {
        c.pad.prev.copy(c.pad.pos);
        c.pad.prevNormal.copy(c.pad.normal);
        c.pad.prevRight.copy(c.pad.right);
        c.pad.prevUp.copy(c.pad.up);
        q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), w * dt);
        c.pad.normal.applyQuaternion(q);
        c.pad.right.applyQuaternion(q);
        c.pad.up.applyQuaternion(q);
        const ev = [];
        stepPhysics(dt, c.ball, [c.pad], ev, null);
        if (ev.some((e) => e.type === 'paddle')) {
          hit = true;
          exitSpeed = +c.ball.vel.length().toFixed(2);
          ndot = +c.ball.vel.clone().normalize().dot(c.pad.normal).toFixed(3);
        }
      }
      return { mode, hit, ndot, exitSpeed, omega: w };
    }

    if (mode === 'edge') {
      // impactos en canto/esquina (98-104 % del radio): sin túnel, sin dobles
      let seed = 424242 >>> 0;
      const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
      const n = o.n || 400;
      let hits = 0, tunnels = 0, doubles = 0;
      for (let i = 0; i < n; i++) {
        const rho = R * (0.98 + rnd() * 0.06);   // 98-104 % del radio
        const th = rnd() * Math.PI * 2;
        const ox = Math.cos(th) * rho, oy = Math.sin(th) * rho;
        const c = mkCase();
        c.ball.pos.copy(bladeCenter(c.pad)).add(new THREE.Vector3(ox, oy, 0.09));
        c.ball.vel.set(0, 0, -8);
        let hitEv = 0;
        for (let s = 0; s < 25; s++) {
          c.pad.prev.copy(c.pad.pos);
          c.pad.prevNormal.copy(c.pad.normal);
          c.pad.prevRight.copy(c.pad.right);
          c.pad.prevUp.copy(c.pad.up);
          const ev = [];
          stepPhysics(1 / 90, c.ball, [c.pad], ev, null);
          for (const e of ev) if (e.type === 'paddle') hitEv++;
        }
        if (hitEv > 0) hits++;
        if (hitEv > 1) doubles++;                // dobles golpes en 25 pasos
        // túnel: la bola cruzó el plano de la hoja sin golpe
        const relZ = c.ball.pos.z - bladeCenter(c.pad).z;
        if (hitEv === 0 && relZ < -rB) tunnels++;
      }
      return { mode, n, hits, tunnels, doubles };
    }

    if (mode === 'energy') {
      // coherencia energética: salida ≤ (1+e)·aproximación + empuje del cuerpo
      const c = mkCase();
      const vIn = o.vIn || 10;
      c.ball.pos.copy(bladeCenter(c.pad)).add(new THREE.Vector3(0, 0, 0.10));
      c.ball.vel.set(0, 0, -vIn);
      let out = -1;
      for (let s = 0; s < 40 && out < 0; s++) {
        c.pad.prev.copy(c.pad.pos);
        c.pad.prevNormal.copy(c.pad.normal);
        c.pad.prevRight.copy(c.pad.right);
        c.pad.prevUp.copy(c.pad.up);
        const ev = [];
        stepPhysics(1 / 240, c.ball, [c.pad], ev, null);
        if (ev.some((e) => e.type === 'paddle')) out = +c.ball.vel.length().toFixed(3);
      }
      const e = DIMS.paddleRestitution;
      const cap = (1 + e) * vIn + 0.6;           // + holgura del cuerpo/soporte
      return { mode, vIn, out, cap: +cap.toFixed(3), ok: out > 0 && out <= cap };
    }

    if (mode === 'perf') {
      // coste por barrido (peor caso = fallo con rasante) y por frame
      const nS = o.n || 50000;
      const ax = 0, ay = 0, az = 0.30, bx = 0.001, by = 0.0005, bz = -0.30;
      let acc = 0;
      const t0 = performance.now();
      for (let i = 0; i < nS; i++) {
        acc += sweepBallVsBlade(ax + (i % 7) * 1e-4, ay, az, bx, by, bz,
          R, hT, rB) >= 0 ? 1 : 0;
      }
      const sweepUs = (performance.now() - t0) * 1000 / nS;
      // frame completo de física real
      const c = mkCase();
      c.ball.pos.copy(bladeCenter(c.pad)).add(new THREE.Vector3(0, 0, 0.3));
      c.ball.vel.set(0, 0, -6);
      const nF = o.frames || 300;
      const t1 = performance.now();
      for (let s = 0; s < nF; s++) {
        c.pad.prev.copy(c.pad.pos);
        c.pad.prevNormal.copy(c.pad.normal);
        c.pad.prevRight.copy(c.pad.right);
        c.pad.prevUp.copy(c.pad.up);
        const ev = [];
        stepPhysics(1 / 90, c.ball, [c.pad], ev, null);
      }
      const frameUs = (performance.now() - t1) * 1000 / nF;
      return { mode, sweepUs: +sweepUs.toFixed(3), frameUs: +frameUs.toFixed(1), acc };
    }

    return { mode, error: 'modo desconocido' };
  };
  // v2.57: puente de PRUEBAS headless — referencia al juego (los campeonatos
  // externos se lanzan desde él; no cambia ningún comportamiento)
  window.__PP_GAME = game;
  // r72 · sonda de QA: los ICONOS vectoriales (PP_ICONS) para verificarlos
  // pintándolos en canvas real desde la capa BG (qa_r72_v3664).
  try { game._ppIconsProbe = () => PP_ICONS; } catch (e) { /* decorativo */ }
  /* ===========================================================
   *  v3.0 · PRO TRAINING — módulo completo (autocontenido)
   *  =========================================================== */
/* =====================================================================
   *  v3.0 · PRO TRAINING — CENTRO DE ALTO RENDIMIENTO (CRAZY PING PONG)
   *  ---------------------------------------------------------------------
   *  Módulo AUTOCONTENIDO y AISLADO. Añade al apartado de entrenamiento:
   *   · Subapartado 0: posición de la pala (el panel de siempre, ahora
   *     plegado dentro del hub como un modo más).
   *   · 5 áreas profesionales × 2 modos (dirección, altura, efecto,
   *     saque y ritmo) con jueces propios, máquina de bolas con efecto
   *     real (Magnus incluido en el solver) y objetivos encadenados.
   *   · Feedback técnico: marcas de bote, línea de tiro real, indicador
   *     de efecto sobre la bola y panel flotante con el progreso.
   *   · Puntos → perfil (localStorage) → PIELS de pala desbloqueables
   *     seleccionables en TODOS los modos (única vía de salida).
   *   · Iconos de efecto en AMBAS caras de la pala (cosmética global,
   *     activa también en campeonatos: el efecto ya existía en la
   *     física del núcleo; aquí se HACE VISIBLE sin tocar la física).
   *  NUNCA modifica física, árbitro, IA ni campeonatos. Todo vive en
   *  window.__PP_TRAIN y en su grupo de escena propio (trainGrp).
   *  ===================================================================== */
  const PP_TRAIN = (() => {
    'use strict';
  
    /* ---------------- almacenamiento del perfil ---------------- */
    const KEY = 'ppxr_train_v1';
    const DEF = {
      pts: 0, best: {}, done: {}, unlocked: ['clasica'],
      skin: 'clasica', fb: { marks: 1, line: 1, spin: 1 },
      // v3.0.7-PLAY1 · PRO CIRCUITO: estrellas/precisión por prueba, logros
      // y mejor combo alcanzado (todo derivado del juez, nunca al revés)
      stars: {}, acc: {}, ach: {}, comboBest: 0,
      // v3.6.68 · EL PULSO CRAZY (r76): latido diario de la academia —
      // last='YYYY-MM-DD' del último reto cobrado · streak=racha viva de
      // asistencia · bestStreak=récord · done[dayKey]={m,res,g} cobros
      daily: { last: '', streak: 0, bestStreak: 0, done: {} },
      // M4 (r118) · RETO SEMANAL: bad=insignias acumuladas · done[weekKey]={m,res,g}
      semana: { bad: 0, done: {} },
    };
    let S = (() => {
      try {
        const raw = localStorage.getItem(KEY);
        if (!raw) return JSON.parse(JSON.stringify(DEF));
        const d = Object.assign(JSON.parse(JSON.stringify(DEF)), JSON.parse(raw));
        d.fb = Object.assign({ marks: 1, line: 1, spin: 1 }, d.fb || {});
        // r76 · migración defensiva del daily (perfiles antiguos sin la clave
        // o con basura: el PULSO nunca rompe la carga del perfil)
        d.daily = Object.assign({ last: '', streak: 0, bestStreak: 0, done: {} }, d.daily || {});
        d.daily.done = (d.daily.done && typeof d.daily.done === 'object' && !(d.daily.done instanceof Array)) ? d.daily.done : {};
        d.daily.streak = (+d.daily.streak || 0); d.daily.bestStreak = (+d.daily.bestStreak || 0);
        if (typeof d.daily.last !== 'string') d.daily.last = '';
        // M4 (r118) · migración defensiva del semanal (igual que el daily)
        d.semana = Object.assign({ bad: 0, done: {} }, d.semana || {});
        d.semana.done = (d.semana.done && typeof d.semana.done === 'object' && !(d.semana.done instanceof Array)) ? d.semana.done : {};
        d.semana.bad = (+d.semana.bad || 0);
        if (!Array.isArray(d.unlocked) || !d.unlocked.length) d.unlocked = ['clasica'];
        return d;
      } catch (e) { return JSON.parse(JSON.stringify(DEF)); }
    })();
    const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* */ } };
  
    /* ---------------- i18n mínima del módulo ---------------- */
    let LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
    const TR = {
      es: {
        hub_t: 'PRO TRAINING', hub_s: 'Centro de alto rendimiento · CRAZY PING PONG',
        // r104 · claves del MAPA DE CALOR (r97) en el diccionario propio:
        // antes caían en CRUDO («heat_t», «heat_sin»…) al pie del hub
        heat_t: 'MAPA DE CALOR',
        heat_sin: 'sin datos todavía — juega duelos',
        heat_total: '{n} puntos perdidos',
        heat_corta: 'corta',
        heat_media: 'media',
        heat_fondo: 'fondo',
        perfil: 'PERFIL', pts: 'puntos', nivel: 'Nivel', volver: '‹ Volver', menu: '‹ Menú',
        a_dir: 'DIRECCIÓN', a_dir_s: 'Profundidad y colocación',
        a_alt: 'ALTURA', a_alt_s: 'Control sobre la red',
        a_spin: 'EFECTO', a_spin_s: 'Lee y devuelve el giro',
        a_saq: 'SAQUE', a_saq_s: 'Corto de doble bote y largo',
        a_rit: 'RITMO', a_rit_s: 'Regularidad y consistencia',
        a_pala: 'POSICIÓN DE LA PALA', a_pala_s: 'Ajusta el agarre sobre tu mano',
        fb_t: 'AYUDAS TÉCNICAS', fb_marks: 'Marcas de bote', fb_line: 'Línea de tiro', fb_spin: 'Flecha de efecto',
        skins_t: 'PIEL DE LA PALA', skin_sel: 'Elegida', skin_lock: 'puntos',
        perk_eq: 'NEUTRA', perk_eq_d: 'piel de referencia · sin modulación de juego',
        perk_of: 'OFENSIVA', perk_of_d: '+12 % potencia · +8 % efecto · el canto castiga más',
        perk_de: 'DEFENSIVA', perk_de_d: '+30 % control · el canto perdona · bote más seguro',
        perk_po: 'POTENCIA', perk_po_d: 'golpes más fuertes · algo menos de efecto',
        perk_ef: 'EFECTO', perk_ef_d: '+22 % de brush y agarre · imprime muchísimo giro',
        perk_dg: 'DOBLE GOMA', perk_dg_d: 'cara A: goma de giro · cara B: goma dura de potencia',
        perk_aviso: 'Las pieles ya son JUEGO: cada goma modula tu pala (la IA juega neutra).',
        obj: 'Objetivo', mejor: 'Mejor', iniciar: '▶ INICIAR', activo: 'EN CURSO', parar: '■ Detener entrenamiento',
        seg: 'seguidas',
        m_t1a: 'MESA MARCADA', m_t1a_d: 'Lleva la bola {n} veces seguidas a la zona dorada. El centro (rojo) es la zona fácil del rival: evítala.',
        m_t1b: 'JUNTO A LA LÍNEA', m_t1b_d: 'Coloca {n} bolas seguidas rozando las bandas laterales o el fondo. Cuanto más cerca de la línea, más difícil es para el rival.',
        m_t2a: 'PASE BAJO', m_t2a_d: 'Golpea drives profundos pasando ENTRE la red y la cinta naranja. Ajusta la altura de la barra acercando la MANO LIBRE a la cinta y moviéndola arriba o abajo (aparta la mano para fijar). Si pasas por encima, el rival te remata.',
        m_t2b: 'GLOBO DEFENSIVO', m_t2b_d: 'Levanta {n} globos seguidos por encima del aro y que boten en el fondo rival. Gana tiempo cuando estás en apuros.',
        m_t3a: 'LEER EL CORTADO', m_t3a_d: 'La máquina lanza bolas con corte pesado. Devuélvelas {n} veces seguidas con la pala abierta: sin tocar la red y sin levantarla.',
        m_t3b: 'BLOQUEAR EL TOPSPIN', m_t3b_d: 'Bolas con lift fuerte y velocidad variable. Bloquea o contraataca {n} veces seguidas con la pala cerrada.',
        m_t4a: 'SAQUE CORTO · DOBLE BOTE', m_t4a_d: 'Saca y consigue que la bola BOTE DOS VECES en la zona marcada junto a la red. El saque corto evita el ataque rival.',
        m_t4b: 'SAQUE LARGO · AL FONDO', m_t4b_d: 'Coloca {n} primeros botes en la franja de los últimos 15 cm. Saque rápido y tenso pegado al fondo.',
        m_t5a: 'METRÓNOMO', m_t5a_d: 'Bolas a ritmo constante: devuelve el máximo número seguidas. Hitos a 30 · 50 · 100 con bonus.',
        /* M7d (r120) · PRO TRAINING extendido — dos ejercicios nuevos */
        m_t1c: 'ESQUINA EXACTA', m_t1c_d: 'Coloca {n} bolas seguidas en la ESQUINA: fondo Y banda a la vez (cuadros dorados). La esquina es el tiro más difícil de devolver.',
        m_t5b: 'METRÓNOMO LOCO', m_t5b_d: 'Como el metrónomo, pero la máquina TRAICIONA: cada bola llega a una velocidad distinta. Hitos a 20 · 40 · 80 con bonus.',
        ok_esq: '¡ESQUINA!',
        med_t: 'MEDALLAS', med_br: 'BRONCE', med_pl: 'PLATA', med_or: 'ORO',
        hud_racha: 'RACHA', hud_meta: 'META', hud_bote: 'BOTES', hud_rally: 'RALLY', hud_sesion: 'Sesión', hud_total: 'Total',
        ok_zona: '¡ZONA!', ok_banda: '¡A LA LÍNEA!', ok_bajo: '¡PASE BAJO!', ok_globo: '¡GLOBO!', ok_leido: '¡BIEN LEÍDO!', ok_bloqueo: '¡BLOQUEO!', ok_doble: '¡DOBLE BOTE!', ok_fondo: '¡AL FONDO!', ok_beat: '¡RITMO!',
        z_obj: 'OBJETIVO', z_evita: 'EVITA', z_fondo: 'FONDO', z_doble: 'DOBLE BOTE', z_f15: 'FONDO 15 cm',
        mal_alto: 'MUY ALTO · te rematan', mal_corta: 'CORTA · al centro', mal_red: 'A LA RED', mal_fuera: 'FUERA', mal_larga: 'LARGO', mal_pierde: 'SE PIERDE',
        hecho: '¡COMPLETADO! +{n} pts', nuevo_skin: 'PIEL NUEVA: {s} · elígela en el hub', hito: '¡HITO {n} RALLY! +{n2} pts',
        sirve: 'Bola en tu mano libre · suéltala (o gatillo) y golpéala en el aire',
        toss_alto: 'Lanza la bola un poco más arriba', fuera_linea: 'Saca desde detrás de la línea de fondo',
        fin_rally: 'Rally terminado: {n}',
        lvl0: 'Novato', lvl1: 'Amateur', lvl2: 'Competidor', lvl3: 'Maestro', lvl4: 'Leyenda',
        combo: 'COMBO ×{n}', acc: 'Precisión', logros: 'LOGROS', max: 'MÁX',
        nuevo_logro: '¡LOGRO: {a}!',
        ach_r10: 'RACHA DE 10', ach_r20: 'RACHA DE 20', ach_p1: 'PERFECTO',
        ach_p5: 'CINCO PERFECTOS', ach_all9: 'CIRCUITO COMPLETO',
        ach_m50: 'METRÓNOMO 50', ach_m100: 'METRÓNOMO 100',
        ach_x3: 'TRIPLE COMBO', ach_leg: 'LEYENDA',
        ach_or5: 'MEDALLERO DE ORO',   /* M7d (r120) · 5 medallas de ORO */
        /* v3.6.68 · EL PULSO CRAZY (r76) — el latido diario */
        daily_t: 'RETO DEL DÍA', daily_sub: 'un duelo nuevo cada medianoche · igual para toda la academia',
        daily_racha: 'RACHA', daily_dias: 'días', daily_record: 'récord',
        daily_hecho: '¡RETO DEL DÍA COMPLETADO! +{n} pts',
        daily_ya: 'COMPLETADO HOY', daily_vuelve: 'Vuelve mañana: duelo nuevo y racha que sigue',
        daily_recompensa: '+{n} pts', daily_fantasma_t: 'TU FANTASMA',
        daily_fantasma: '¡VENCISTE A TU FANTASMA! +15 pts',
        daily_fantasma_x: 'A vencer: {n}', daily_fantasma_no: 'sin marca aún',
        daily_iniciar: '▶ INICIAR RETO', daily_ya_btn: '✓ HECHO · vuelve mañana',
        daily_obj: '{n} seguidas',
        daily_hitos: 'Sólo la ASISTENCIA al Reto del Día libera estas pieles',
        daily_asist: 'PIEL DE ASISTENCIA',
        daily_prof: 'El profesor: «{tip}»',
        daily_t0: 'terminar el reto de hoy es la primera técnica: la constancia se entrena',
        daily_t1: 'aún no has cerrado este modo: {n} seguidas y sin prisa — la pala decide antes de botar',
        daily_t2: 'tu precisión ({a} %) manda sobre la velocidad: menos prisa, más lectura del bote',
        daily_t3: 'ya lo terminas: ahora SIN fallos — las 3 estrellas son de quien lee el juego',
        daily_t4: 'modo dominado: tu duelo es la racha — la constancia separa al campeón del resto',
        /* M4 (r118) · RETO DE LA SEMANA */
        semana_t: 'RETO DE LA SEMANA',
        semana_sub: '{m} · objetivo {n} seguidas · duelo de la septana',
        semana_iniciar: '▶ INICIAR RETO SEMANAL',
        semana_ya: '✓ SEMANA COMPLETADA',
        semana_insignia: 'Insignias ×{n}',
        semana_hecho: '¡RETO SEMANAL COMPLETADO! +{n} pts',
        daily_p0: 'La casa reta a tu profundidad', daily_p1: 'El hechizo exige control sobre la red',
        daily_p2: 'Lee el giro o pícate', daily_p3: 'El duelo se gana en el saque',
        daily_p4: 'El metrónomo no perdona',
      },
      en: {
        hub_t: 'PRO TRAINING', hub_s: 'High performance center · CRAZY PING PONG',
        heat_t: 'HEAT MAP',
        heat_sin: 'no data yet — play matches',
        heat_total: '{n} points lost',
        heat_corta: 'short',
        heat_media: 'mid',
        heat_fondo: 'deep',
        perfil: 'PROFILE', pts: 'points', nivel: 'Level', volver: '‹ Back', menu: '‹ Menu',
        a_dir: 'DIRECTION', a_dir_s: 'Depth and placement',
        a_alt: 'HEIGHT', a_alt_s: 'Net clearance control',
        a_spin: 'SPIN', a_spin_s: 'Read and return the spin',
        a_saq: 'SERVE', a_saq_s: 'Short double-bounce and long',
        a_rit: 'RHYTHM', a_rit_s: 'Consistency and regularity',
        a_pala: 'PALA POSITION', a_pala_s: 'Fit the grip to your hand',
        fb_t: 'TECH AIDS', fb_marks: 'Bounce marks', fb_line: 'Shot line', fb_spin: 'Spin arrow',
        skins_t: 'PALA SKIN', skin_sel: 'Selected', skin_lock: 'points',
        perk_eq: 'NEUTRAL', perk_eq_d: 'reference skin · no gameplay modulation',
        perk_of: 'OFFENSIVE', perk_of_d: '+12 % power · +8 % spin · the edge punishes more',
        perk_de: 'DEFENSIVE', perk_de_d: '+30 % control · forgiving edge · safer bounce',
        perk_po: 'POWER', perk_po_d: 'harder shots · slightly less spin',
        perk_ef: 'SPIN', perk_ef_d: '+22 % brush and grip · massive spin',
        perk_dg: 'DUAL RUBBER', perk_dg_d: 'face A: spin rubber · face B: hard power rubber',
        perk_aviso: 'Skins are GAMEPLAY now: each rubber modulates your paddle (AI stays neutral).',
        obj: 'Goal', mejor: 'Best', iniciar: '▶ START', activo: 'RUNNING', parar: '■ Stop training',
        seg: 'in a row',
        m_t1a: 'MARKED TABLE', m_t1a_d: 'Hit {n} balls in a row into the gold zone. The center (red) is the opponent\u2019s easy zone: avoid it.',
        m_t1b: 'HUG THE LINE', m_t1b_d: 'Place {n} balls in a row grazing the side bands or the baseline. The closer to the line, the harder to return.',
        m_t2a: 'LOW PASS', m_t2a_d: 'Hit deep drives passing BETWEEN the net and the orange ribbon. Adjust the bar height by bringing your FREE HAND to the ribbon and moving it up or down (pull away to set). Over it and they smash you.',
        m_t2b: 'DEFENSIVE LOB', m_t2b_d: 'Lift {n} lobs in a row above the hoop landing deep. Buy time when you are in trouble.',
        m_t3a: 'READ THE CHOP', m_t3a_d: 'The machine fires heavy backspin. Return them {n} times in a row with an open blade: no net, no pop-up.',
        m_t3b: 'BLOCK THE TOPSPIN', m_t3b_d: 'Strong topspin at varying speed. Block or counter {n} times in a row with a closed blade.',
        m_t4a: 'SHORT SERVE · DOUBLE BOUNCE', m_t4a_d: 'Serve so the ball BOUNCES TWICE in the marked zone near the net. Short serves prevent attacks.',
        m_t4b: 'LONG SERVE · DEEP', m_t4b_d: 'Land {n} first bounces in the last 15 cm strip. Fast, tight serves to the baseline.',
        m_t5a: 'METRONOME', m_t5a_d: 'Balls at a steady beat: return as many as you can in a row. Milestones at 30 · 50 · 100 with bonuses.',
        /* M7d (r120) · extended PRO TRAINING — two new drills */
        m_t1c: 'EXACT CORNER', m_t1c_d: 'Place {n} balls in a row in the CORNER: deep AND side band at once (gold squares). The corner is the hardest shot to return.',
        m_t5b: 'CRAZY METRONOME', m_t5b_d: 'Like the metronome, but the machine BETRAYS you: every ball arrives at a different speed. Milestones at 20 · 40 · 80 with bonuses.',
        ok_esq: 'CORNER!',
        med_t: 'MEDALS', med_br: 'BRONZE', med_pl: 'SILVER', med_or: 'GOLD',
        hud_racha: 'STREAK', hud_meta: 'GOAL', hud_bote: 'BOUNCES', hud_rally: 'RALLY', hud_sesion: 'Session', hud_total: 'Total',
        ok_zona: 'ZONE!', ok_banda: 'ON THE LINE!', ok_bajo: 'LOW PASS!', ok_globo: 'LOB!', ok_leido: 'WELL READ!', ok_bloqueo: 'BLOCK!', ok_doble: 'DOUBLE BOUNCE!', ok_fondo: 'DEEP!', ok_beat: 'RHYTHM!',
        z_obj: 'TARGET', z_evita: 'AVOID', z_fondo: 'DEEP', z_doble: 'DOUBLE BOUNCE', z_f15: 'DEEP 15 cm',
        mal_alto: 'TOO HIGH · they smash', mal_corta: 'SHORT · center', mal_red: 'INTO THE NET', mal_fuera: 'OUT', mal_larga: 'LONG', mal_pierde: 'LOST',
        hecho: 'COMPLETED! +{n} pts', nuevo_skin: 'NEW SKIN: {s} · pick it in the hub', hito: 'MILESTONE {n} RALLY! +{n2} pts',
        sirve: 'Ball resting on your free hand · release it (or trigger) and hit it in the air',
        toss_alto: 'Toss the ball a bit higher', fuera_linea: 'Serve from behind the end line',
        fin_rally: 'Rally over: {n}',
        lvl0: 'Rookie', lvl1: 'Amateur', lvl2: 'Contender', lvl3: 'Master', lvl4: 'Legend',
        combo: 'COMBO ×{n}', acc: 'Accuracy', logros: 'BADGES', max: 'MAX',
        nuevo_logro: 'BADGE: {a}!',
        ach_r10: 'STREAK OF 10', ach_r20: 'STREAK OF 20', ach_p1: 'PERFECT',
        ach_p5: 'FIVE PERFECTS', ach_all9: 'FULL CIRCUIT',
        ach_m50: 'METRONOME 50', ach_m100: 'METRONOME 100',
        ach_x3: 'TRIPLE COMBO', ach_leg: 'LEGEND',
        ach_or5: 'GOLD MEDAL HAUL',   /* M7d (r120) · 5 GOLD medals */
        /* v3.6.68 · EL PULSO CRAZY (r76) */
        daily_t: 'DAILY CHALLENGE', daily_sub: 'a new duel every midnight · the same for the whole academy',
        daily_racha: 'STREAK', daily_dias: 'days', daily_record: 'record',
        daily_hecho: 'DAILY CHALLENGE COMPLETE! +{n} pts',
        daily_ya: 'COMPLETED TODAY', daily_vuelve: 'Come back tomorrow: new duel, streak keeps going',
        daily_recompensa: '+{n} pts', daily_fantasma_t: 'YOUR GHOST',
        daily_fantasma: 'YOU BEAT YOUR GHOST! +15 pts',
        /* M4 (r118) · WEEKLY CHALLENGE */
        semana_t: 'WEEKLY CHALLENGE',
        semana_sub: '{m} · goal {n} in a row · this week\'s duel',
        semana_iniciar: '▶ START WEEKLY',
        semana_ya: '✓ WEEK DONE',
        semana_insignia: 'Badges ×{n}',
        semana_hecho: 'WEEKLY CHALLENGE COMPLETE! +{n} pts',
        daily_fantasma_x: 'To beat: {n}', daily_fantasma_no: 'no mark yet',
        daily_iniciar: '▶ START CHALLENGE', daily_ya_btn: '✓ DONE · back tomorrow',
        daily_obj: '{n} in a row',
        daily_hitos: 'Only DAILY CHALLENGE attendance unlocks these skins',
        daily_asist: 'ATTENDANCE SKIN',
        daily_prof: 'The professor: “{tip}”',
        daily_t0: 'finishing today\u2019s challenge is the first technique: consistency is trained',
        daily_t1: 'you have not closed this mode yet: {n} in a row, no rush — the blade decides before the bounce',
        daily_t2: 'your accuracy ({a} %) rules over speed: less rush, read the bounce',
        daily_t3: 'you already finish it: now with NO faults — 3 stars belong to those who read the game',
        daily_t4: 'mode mastered: your duel is the streak — consistency separates the champion',
        daily_p0: 'The house challenges your depth', daily_p1: 'The spell demands net control',
        daily_p2: 'Read the spin or bite the dust', daily_p3: 'The duel is won at the serve',
        daily_p4: 'The metronome shows no mercy',
      },
    };
    const t = (k, vars) => {
      let s = (TR[LANG] && TR[LANG][k]) || TR.es[k] || k;
      if (vars) for (const kk of Object.keys(vars)) s = s.split('{' + kk + '}').join(String(vars[kk]));
      return s;
    };
  
    /* ---------------- niveles y skins ---------------- */
    // r61 · FASE 155 · la escalera de niveles es DATO (CONFIG_TORNEOS
    // .circuito.niveles en c02) — puntos mínimos y clave i18n por nivel.
    const LEVELS = CONFIG_TORNEOS.circuito.niveles;
    const levelOf = (p) => { let l = LEVELS[0]; for (const it of LEVELS) if (p >= it.min) l = it; return l; };

    /* =================================================================
     *  v3.6.68 · EL PULSO CRAZY (r76) — el latido diario de la academia
     *  RETO DEL DÍA: duelo determinista por fecha LOCAL del visor (el
     *  mismo para todos, cambia a medianoche) sobre los 9 modos que ya
     *  existen. RACHA DE ASISTENCIA con pieles exclusivas que los puntos
     *  NO compran, y TU FANTASMA: tu mejor marca del modo del día como
     *  rival al que vencer. Todo local y honesto, con el economy de
     *  puntos existente (GAMF=0 ⇒ el PULSO no existe, flujo legacy).
     *  ================================================================= */
    const DAILY_BASE = 40, DAILY_PASO = 5, DAILY_TOPE = 7, DAILY_FANTASMA = 15;
    /* r85 · DIFICULTAD DEL RETO DIARIO — petición del dueño («subir la
     * dificultad del Reto Diario poco a poco», ya anticipada en r80:
     * «la dificultad irá subiendo con el tiempo»). UN solo mando central:
     * el reto del día sigue siendo IGUAL para toda la academia, pero su
     * objetivo crece +1 seguida (PASO) cada CADA días desde DESDE, con TOPE.
     * Nov 2026: +1 · mediados: +2 · finales: +3 (tope). Entrenamiento libre
     * NO se toca: manda el objetivo base del modo (M.n). */
    const DAILY_DIF = { DESDE: '2026-11-01', CADA: 14, PASO: 1, TOPE: 3 };
    function dailySub(k) {             // objetivo EXTRA del día (0..TOPE)
      try {
        const d0 = new Date(DAILY_DIF.DESDE + 'T00:00:00');
        const d1 = new Date(k + 'T00:00:00');
        const dias = Math.floor((d1 - d0) / 86400000);
        if (!(dias >= 0)) return 0;  // NaN/anterior a DESDE: sin subida
        return Math.min(DAILY_DIF.TOPE, DAILY_DIF.PASO * (1 + Math.floor(dias / DAILY_DIF.CADA)));
      } catch (e) { return 0; }
    }
    /* r85 · OBJETIVO EFECTIVO del modo activo: en el RETO DIARIO manda el
     * plan del día (con la subida); en el RETO SEMANAL (M4 r118) manda el
     * plan de la septana; en entrenamiento libre, el base (M.n).
     * ÚNICO punto de lectura del objetivo JUGABLE (HUD y meta). */
    function objN() {
      const M = MODES[active];
      const base = M ? M.n : 0;
      if (!st.daily || !active) return base;
      if (st.weekly) {
        const pw = weeklyPlan(weekKey());
        if (pw && pw.mode === active && pw.n > base) return pw.n;
      }
      const p = dailyPlan(dayKey());
      return (p && p.mode === active && p.n > base) ? p.n : base;
    }
    const DAILY_PODA = 90;                 // días recordados en done{}
    const CHAMPS_DIA = ['CLOW', 'WIZARD', 'FORAJIDO', 'ORBITAL', 'HALLOWEEN'];
    // RACHA_SKINS se define JUNTO A SKINS (abajo): TDZ — las constantes del
    // motor van aquí, lo que TOCA a SKINS va tras su declaración.

    function dayKey(off) {
      const d = new Date();
      if (off) d.setDate(d.getDate() + off);
      const p = (n) => (n < 10 ? '0' : '') + n;
      return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
    }
    function seedOf(s) {                   // FNV-1a 32 bits — estable y rápido
      let h = 0x811c9dc5;
      for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = (h * 0x01000193) >>> 0; }
      return h >>> 0;
    }
    function dailyPlan(k) {
      const seed = seedOf('ppx-' + k);
      const ids = PLAN_POOL;               /* M7d (r120): pool clásico congelado */
      const mode = ids[seed % ids.length];
      const M = MODES[mode];
      const areaIdx = AREAS.findIndex((a) => a.id === M.area);
      return {
        mode, n: M.n + dailySub(k), area: M.area, areaIdx: areaIdx < 0 ? 0 : areaIdx,
        champ: CHAMPS_DIA[(seed >>> 7) % CHAMPS_DIA.length],
        frase: 'daily_p' + (areaIdx < 0 ? 0 : areaIdx),
      };
    }
    function dailyTip(k) {                 // EL INFORME DEL PROFESOR (datos reales)
      const plan = dailyPlan(k);
      const best = S.best[plan.mode] || 0;
      const acc = S.acc[plan.mode] || 0;
      if (!best) return { k: 'daily_t0', v: { n: plan.n } };
      if (best < plan.n) return { k: 'daily_t1', v: { n: plan.n } };
      if (acc && acc < 75) return { k: 'daily_t2', v: { a: acc } };
      if ((S.stars[plan.mode] || 0) < 3) return { k: 'daily_t3', v: { n: plan.n } };
      return { k: 'daily_t4', v: { n: plan.n } };
    }
    function effStreak() {                 // racha VIVA: se enfría si fallas un día
      if (!S.daily.last) return 0;
      const hoy = dayKey(), ay = dayKey(-1);
      return (S.daily.last === hoy || S.daily.last === ay) ? S.daily.streak : 0;
    }
    function dailyComplete(mode, res, oldBest) {
      if (!GAMF()) return;                 // gamify=0 ⇒ el PULSO no existe
      const k = dayKey();
      if (S.daily.done[k]) return;         // ya cobrado hoy (jamás doble)
      const plan = dailyPlan(k);
      if (plan.mode !== mode) return;      // hoy toca OTRO modo
      const ay = dayKey(-1);
      const nk = (S.daily.last === ay || S.daily.last === k) ? S.daily.streak + 1 : 1;
      S.daily.streak = nk;
      if (nk > S.daily.bestStreak) S.daily.bestStreak = nk;
      S.daily.last = k;
      const fantasma = (res | 0) > (oldBest | 0);   // has batido tu mejor marca
      const pts = DAILY_BASE + Math.min(nk - 1, DAILY_TOPE) * DAILY_PASO + (fantasma ? DAILY_FANTASMA : 0);
      S.daily.done[k] = { m: mode, res: res | 0, g: fantasma ? 1 : 0 };
      const ks = Object.keys(S.daily.done);
      if (ks.length > DAILY_PODA) {        // poda: recuerda 90 días
        ks.sort();
        for (let i = 0; i < ks.length - DAILY_PODA; i++) delete S.daily.done[ks[i]];
      }
      addPts(pts);
      let aviso = t('daily_hecho', { n: pts }) + (fantasma ? '  ·  ' + t('daily_fantasma') : '');
      for (const sk of RACHA_SKINS) {
        if (nk >= sk.days && S.unlocked.indexOf(sk.id) < 0) {
          S.unlocked.push(sk.id);
          aviso = t('nuevo_skin', { s: sk.name[LANG] || sk.name.es }) + '  ·  ' + aviso;
          try { G.audio.playOsc(990, 1560, 0.2, 'triangle', 0.15, 0.1); } catch (e) { /* */ }
        }
      }
      toast(aviso, true);
      save(); panelDirty = true;
    }

    /* =================================================================
     *  M4 (r118) · RETO DE LA SEMANA — el hermano mayor del PULSO
     *  (roadmap MEJORAS.md M4). Misma mecánica determinista que el
     *  diario: semilla por septana (lunes→domingo, hora LOCAL), modo
     *  y objetivo iguales para todos, TU FANTASMA como rival y premio
     *  de INSIGNIA acumulable (S.semana.bad) + puntos mayores (120/30).
     *  Objetivo: base +2 con subida +1 por semana transcurrida (tope 4).
     *  Las RACHA_SKINS siguen siendo SOLO del diario (fila propia).
     *  ================================================================= */
    const WEEKLY_BASE = 120, WEEKLY_FANTASMA = 30;
    const WEEKLY_SUB = { DESDE: '2026-W1102', PASO: 1, TOPE: 4 };  // lunes 2026-11-02
    function weekKey(off) {
      const d = new Date();
      if (off) d.setDate(d.getDate() + off * 7);
      const dia = (d.getDay() + 6) % 7;            // lunes = 0
      d.setDate(d.getDate() - dia);                // el lunes de esta septana
      const p = (n) => (n < 10 ? '0' : '') + n;
      return d.getFullYear() + '-W' + p(d.getMonth() + 1) + p(d.getDate());
    }
    function weeklySub(k) {
      try {
        const lunesDe = (wk) => {
          const i = wk.indexOf('-W');
          return new Date(+wk.slice(0, i), +wk.slice(i + 2, i + 4) - 1, +wk.slice(i + 4));
        };
        const semanas = Math.floor((lunesDe(k) - lunesDe(WEEKLY_SUB.DESDE)) / 604800000);
        if (!(semanas >= 0)) return 0;
        return Math.min(WEEKLY_SUB.TOPE, WEEKLY_SUB.PASO * (1 + semanas));
      } catch (e) { return 0; }
    }
    function weeklyPlan(k) {
      const seed = seedOf('ppx-semana-' + k);
      const ids = PLAN_POOL;               /* M7d (r120): pool clásico congelado */
      const mode = ids[seed % ids.length];
      const M = MODES[mode];
      const areaIdx = AREAS.findIndex((a) => a.id === M.area);
      return {
        mode, n: M.n + 2 + weeklySub(k), area: M.area, areaIdx: areaIdx < 0 ? 0 : areaIdx,
        champ: CHAMPS_DIA[(seed >>> 7) % CHAMPS_DIA.length],
      };
    }
    function weeklyComplete(mode, res, oldBest) {
      if (!GAMF()) return;                 // gamify=0 ⇒ el PULSO no existe
      const k = weekKey();
      if (S.semana.done[k]) return;        // ya cobrada la septana (jamás doble)
      const plan = weeklyPlan(k);
      if (plan.mode !== mode) return;      // esta semana toca OTRO modo
      const fantasma = (res | 0) > (oldBest | 0);
      const pts = WEEKLY_BASE + (fantasma ? WEEKLY_FANTASMA : 0);
      S.semana.done[k] = { m: mode, res: res | 0, g: fantasma ? 1 : 0 };
      S.semana.bad++;
      const ks = Object.keys(S.semana.done);
      if (ks.length > 26) {                // poda: recuerda 26 semanas
        ks.sort();
        for (let i = 0; i < ks.length - 26; i++) delete S.semana.done[ks[i]];
      }
      addPts(pts);
      toast(t('semana_hecho', { n: pts }) + (fantasma ? '  ·  ' + t('daily_fantasma') : '') +
        '  ·  ' + t('semana_insignia', { n: S.semana.bad }), true);
      try { G.audio.playOsc(880, 1560, 0.22, 'triangle', 0.15, 0.1); } catch (e) { /* */ }
      save(); panelDirty = true;
    }

    /* =================================================================
     *  v3.0.7-PLAY1 · PRO CIRCUITO — capa de GAMIFICACIÓN de lectura
     *  -----------------------------------------------------------------
     *  Observa los eventos del JUEZ (okHit/failHit/hitos) y añade:
     *    · COMBO ×2/×3 por rachas de 4/8 (multiplica SOLO los puntos del
     *      golpe; el bonus de completado y el criterio quedan intactos)
     *    · ESTRELLAS 1-3★ por prueba: 3★ sin fallos en la ronda, 2★ con ≤2,
     *      1★ completada (metrónomo: hitos de rally 30/50/100)
     *    · PRECISIÓN % de la ronda (aciertos / intentos)
     *    · LOGROS (9) con toast y fanfarria propia
     *    · CELEBRACIÓN 3D de partículas al completar (un solo pool reutilizado)
     *  NUNCA toca física, juez, feeds ni reglas. Interruptor DIMS.trainGamify.
     *  ================================================================= */
    const GAMF = () => (typeof DIMS !== 'undefined' && DIMS.trainGamify === 0) ? 0 : 1;
    // r61 · FASE 155 · el catálogo de honores es DATO (CONFIG_LOGROS.train
    // en c02) — el orden del panel es el orden de inserción de la tabla.
    const ACHS = Object.keys(CONFIG_LOGROS.train);
    function grant(id) {
      if (!GAMF() || S.ach[id]) return;
      S.ach[id] = 1; save(); panelDirty = true;
      toast(t('nuevo_logro', { a: t('ach_' + id) }), true);
      G.audio.playOsc(520, 780, 0.09, 'triangle', 0.13, 0);
      G.audio.playOsc(780, 1170, 0.09, 'triangle', 0.13, 0.1);
      G.audio.playOsc(1170, 1560, 0.14, 'triangle', 0.13, 0.2);
    }
    function comboMul() {
      if (!GAMF() || !active) return 1;
      return comboMulN(isRallyM() ? st.rally : st.streak);
    }
    // r61 · FASE 155 · escalones del combo y estrellas por ronda: DATO
    // (CONFIG_TORNEOS.circuito.combo / .estrellas en c02).
    function comboMulN(r) {
      const C = CONFIG_TORNEOS.circuito.combo;
      return r >= C.x3Desde ? 3 : (r >= C.x2Desde ? 2 : 1);
    }
    function starsFor(faults) {
      const E = CONFIG_TORNEOS.circuito.estrellas;
      return faults === 0 ? E.tresSinFallo : (faults <= E.dosHastaFallos ? E.dosEstrellas : 1);
    }
    function recordStars(mode, n) {
      if (!GAMF() || !n) return;
      if ((S.stars[mode] || 0) < n) { S.stars[mode] = n; save(); panelDirty = true; }
    }
    function recordAcc(mode, pct) {
      if (!GAMF() || !isFinite(pct)) return;
      if ((S.acc[mode] || 0) < pct) { S.acc[mode] = pct; save(); panelDirty = true; }
    }
    function checkStreakAch() {
      const r = isRallyM() ? st.rally : st.streak;
      // r61 · FASE 155 · umbrales = DATO (CONFIG_LOGROS.train en c02)
      if (r >= CONFIG_LOGROS.train.r10.cond.valor) grant('r10');
      if (r >= CONFIG_LOGROS.train.r20.cond.valor) grant('r20');
    }
    function checkGlobalAch() {
      const modes = Object.keys(MODES);
      /* M7d (r120) · all9 queda anclado al CIRCUITO CLÁSICO (PLAN_POOL):
       * «CIRCUITO COMPLETO» prometía los 9 ejercicios de siempre — los
       * nuevos no endurecen retroactivamente un logro veterano. */
      // r61 · FASE 155 · umbrales = DATO (CONFIG_LOGROS.train en c02)
      if (PLAN_POOL.every((m) => (S.stars[m] || 0) >= CONFIG_LOGROS.train.all9.cond.estrellas)) grant('all9');
      if (modes.filter((m) => S.stars[m] === CONFIG_LOGROS.train.p5.cond.estrellas).length >= CONFIG_LOGROS.train.p5.cond.cuenta) grant('p5');
      /* M7d (r120) · MEDALLERO DE ORO: 5 ejercicios con medalla de ORO */
      if (modes.filter((m) => medallaDe(m) === 3).length >= CONFIG_LOGROS.train.or5.cond.cuenta) grant('or5');
      if (S.pts >= CONFIG_LOGROS.train.leg.cond.valor) grant('leg');
    }
    /* =================================================================
     *  M7d (r120) · MEDALLAS POR EJERCICIO — honor derivado de los datos
     *  que YA existen: sin migración y RETROACTIVO (quien ya dominó un
     *  ejercicio despierta con su medalla puesta).
     *  r64 · FASE 158 · umbrales = DATO (CONFIG_MEDALLAS en c02):
     *  · modos de HABILIDAD (t1/t2/t3/t4): estrellas + precisión
     *    🥉 1 bronce: meta completada alguna vez (stars ≥ MDE.bronce)
     *    🥈 2 plata:  MDE.plata estrellas y precisión ≥ MDP.plata
     *    🥇 3 oro:    MDE.oro estrellas y precisión ≥ MDP.oro
     *  · modos RALLY (t5a/t5b): la MARCA manda (no hay precisión que
     *    grabar en un rally infinito — los hitos SON la meta):
     *    🥉 marca ≥ meta1 · 🥈 ≥ meta2 · 🥇 ≥ meta3 (CONFIG_RALLY.metas)
     *  Con gamify=0 (GAMF=0) no hay medallas: flujo legacy intacto.
     *  ================================================================= */
    function medallaDe(id) {
      if (!GAMF()) return 0;
      const MI = RALLY_MILL[id];
      if (MI) {
        const best = S.best[id] || 0;
        if (best >= MI[2]) return 3;
        if (best >= MI[1]) return 2;
        if (best >= MI[0]) return 1;
        return 0;
      }
      /* r64 · FASE 158 · la escalera vive en CONFIG_MEDALLAS (c02) */
      const MDE = CONFIG_MEDALLAS.estrellas, MDP = CONFIG_MEDALLAS.precision;
      const stN = S.stars[id] || 0;
      if (stN >= MDE.oro) return (S.acc[id] || 0) >= MDP.oro ? 3 : 2;
      if (stN >= MDE.plata) return (S.acc[id] || 0) >= MDP.plata ? 2 : 1;
      if (stN >= MDE.bronce) return 1;
      return 0;
    }
    const MED_GLYPH = ['', '\u{1F949}', '\u{1F948}', '\u{1F947}'];
    /* M7d (r120) · costuras de QA al patrón de la casa (__test/__debug,
     * vivos desde r76/r80/r118): el juez REAL con botes sintéticos y el
     * apagado limpio. Cero caminos nuevos de juego. */
    function qaJudge(mode, p, crossY, apexY, rally) {
      if (!MODES[mode] || !p) return null;
      G = G || ((typeof window !== 'undefined' && window.__PP_GAME) || null);
      if (!G) return null;
      const antes = { pts: S.pts, streak: st.streak };
      active = mode;                      // juez directo (QA dirigida r120)
      st.live = true; st.shotRec = true; st.aiBounce = 0; st.aiTouched = false;
      st.cross = (crossY == null) ? null : { y: crossY, spd: 5 };
      st.apex = (apexY == null) ? 1.0 : apexY;
      if (rally != null) st.rally = rally;
      if (mode === 't1a' && !st.target) st.target = pickTarget();
      judgeAiBounce({ x: p.x, y: p.y, z: p.z });
      return { pts: S.pts, delta: S.pts - antes.pts, streak: st.streak,
        rally: st.rally, stars: Object.assign({}, S.stars) };
    }
    function qaOff() {
      active = null; st.live = false; st.daily = 0; st.weekly = 0;
      st.streak = 0; st.rally = 0;
    }
    function checkComboAch(mul) {
      if (mul > (S.comboBest || 0)) { S.comboBest = mul; save(); }
      if (mul >= 3) grant('x3');
    }
    // celebración 3D: UN solo pool de partículas reutilizado (coste ínfimo)
    let burstPts = null, burstVel = null, burstLife = 0, burstT = 0;
    function burst(pos, big) {
      if (!GAMF() || !grp) return;
      const N = big ? 150 : 90;
      if (!burstPts) {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
        burstVel = new Float32Array(N * 3);
        burstPts = new THREE.Points(geo, new THREE.PointsMaterial({
          color: 0xffd76a, size: 0.028, transparent: true, opacity: 0.95,
          depthWrite: false, blending: THREE.AdditiveBlending,
        }));
        burstPts.visible = false;
        burstPts.renderOrder = 6;
        grp.add(burstPts);
      }
      const p = burstPts.geometry.attributes.position.array;
      for (let i = 0; i < N; i++) {
        p[i * 3] = pos.x; p[i * 3 + 1] = pos.y; p[i * 3 + 2] = pos.z;
        const a = Math.random() * Math.PI * 2, up = 0.8 + Math.random() * 1.7;
        const sp = (0.7 + Math.random() * 1.1) * (big ? 1.25 : 1);
        burstVel[i * 3] = Math.cos(a) * sp;
        burstVel[i * 3 + 1] = up;
        burstVel[i * 3 + 2] = Math.sin(a) * sp * 0.7;
      }
      burstPts.geometry.setDrawRange(0, N);
      burstPts.geometry.attributes.position.needsUpdate = true;
      burstPts.material.opacity = 0.95;
      burstPts.material.color.setHex(big ? 0xffe9a8 : 0xffd76a);
      burstPts.visible = true;
      burstLife = big ? 1.5 : 1.15; burstT = 0;
    }
    function burstTick(dt) {
      if (!burstPts || !burstPts.visible) return;
      burstT += dt;
      const n = burstPts.geometry.drawRange.count;
      const p = burstPts.geometry.attributes.position.array;
      for (let i = 0; i < n * 3; i += 3) {
        p[i] += burstVel[i] * dt;
        p[i + 1] += burstVel[i + 1] * dt;
        p[i + 2] += burstVel[i + 2] * dt;
        burstVel[i + 1] -= 3.4 * dt;
      }
      burstPts.geometry.attributes.position.needsUpdate = true;
      burstPts.material.opacity = Math.max(0, 0.95 * (1 - burstT / burstLife));
      if (burstT >= burstLife) burstPts.visible = false;
    }
  
    /* v3.0.3 · SKINS DE PALA DE VERDAD — nada de aros ni cintas: cada piel
     * define TEXTURAS REALES (goma con pips en relieve, carbono, oro
     * cepillado, holográfica) que se aplican sobre los materiales REALES del
     * GLB (meshes «rubber»/«trim»/«handle»/«paddle») y la piel «Pro Carbon»
     * además SUSTITUYE EL MODELO 3D por un GLB externo
     * (assets/pala/pala_pro.glb). Campos:
     *   tex      clave de la fábrica de texturas (TEX_BUILDERS)
     *   edge     color del CANTO real de la hoja (mesh «trim»)
     *   grip     color de la cinta de agarre sobre el mango real
     *   modelUrl GLB externo que reemplaza el modelo entero (respaldo: tex)
     *   anim     matiz animado (arcoíris) sobre la textura
     * r62 · LA TABLA VIVE EN c02 (CONFIG_PIELES — única fuente de verdad;
     * séptima parada data-driven tras ARCANO_CFG/física/menú/audio/
     * dificultad/torneos+logros). c13 SÓLO CONSUME: añadir o retocar una
     * piel = editar la tabla de c02, cero lógica. */
    const SKINS = CONFIG_PIELES.pieles;
    // r76 · EL PULSO CRAZY: pieles de asistencia (derivadas por su vía —
    // sólo la racha de días del Reto del Diario las libera)
    const RACHA_SKINS = SKINS.filter((s) => s.via === 'racha');
  
    /* ---------------- registro de modos ----------------
     * r72 · cada área lleva ICONO propio (PP_ICONS en c00) — petición del
     * dueño: «faltan los iconos de los botones de los apartados de
     * Entrenamiento para dejarlo bonito». */
    const AREAS = [
      { id: 'dir', ic: 'dir', ik: 'a_dir', sk: 'a_dir_s', g0: '#2b6cb0', g1: '#16324f', col: '#63b3ed' },
      { id: 'alt', ic: 'alt', ik: 'a_alt', sk: 'a_alt_s', g0: '#2f855a', g1: '#1a4433', col: '#68d391' },
      { id: 'spin', ic: 'spin', ik: 'a_spin', sk: 'a_spin_s', g0: '#805ad5', g1: '#44337a', col: '#d6bcfa' },
      { id: 'saque', ic: 'saque', ik: 'a_saq', sk: 'a_saq_s', g0: '#c05621', g1: '#652a12', col: '#f6ad55' },
      { id: 'rit', ic: 'rit', ik: 'a_rit', sk: 'a_rit_s', g0: '#b83280', g1: '#5f1e42', col: '#f687b3' },
    ];
    /* hitos del rally por modo (M7d): [meta1, meta2, meta3] · bonus fijo 15/25/50
     * r63 · LA TABLA VIVE EN c02 (CONFIG_RALLY — única fuente de verdad;
     * octava parada data-driven). c13 SÓLO CONSUME: cambiar una meta o
     * un bonus = editar la tabla de c02, cero lógica. Vive ANTES de MODES
     * (TDZ): los modos rally DEDUPAN su meta1/bonus1 de la tabla — el
     * objetivo jugable (objN) y la fila de MODES son LA MISMA fila. */
    const RALLY_MILL = CONFIG_RALLY.metas;
    const RALLY_BONUS = CONFIG_RALLY.bonos;
    const MODES = {
      t1a: { area: 'dir', nk: 'm_t1a', dk: 'm_t1a_d', n: 5, ok: 'ok_zona', pts: 1, bonus: 15 },
      t1b: { area: 'dir', nk: 'm_t1b', dk: 'm_t1b_d', n: 5, ok: 'ok_banda', pts: 2, bonus: 20 },
      /* M7d (r120) · ESQUINA EXACTA: el tiro de campeón — fondo Y banda a la
       * vez. Entrenamiento libre: NUNCA entra en los retos (PLAN_POOL). */
      t1c: { area: 'dir', nk: 'm_t1c', dk: 'm_t1c_d', n: 3, ok: 'ok_esq', pts: 3, bonus: 25 },
      t2a: { area: 'alt', nk: 'm_t2a', dk: 'm_t2a_d', n: 5, ok: 'ok_bajo', pts: 2, bonus: 20 },
      t2b: { area: 'alt', nk: 'm_t2b', dk: 'm_t2b_d', n: 4, ok: 'ok_globo', pts: 2, bonus: 20 },
      t3a: { area: 'spin', nk: 'm_t3a', dk: 'm_t3a_d', n: 5, ok: 'ok_leido', pts: 2, bonus: 20 },
      t3b: { area: 'spin', nk: 'm_t3b', dk: 'm_t3b_d', n: 6, ok: 'ok_bloqueo', pts: 2, bonus: 25 },
      t4a: { area: 'saque', nk: 'm_t4a', dk: 'm_t4a_d', n: 3, ok: 'ok_doble', pts: 3, bonus: 15 },
      t4b: { area: 'saque', nk: 'm_t4b', dk: 'm_t4b_d', n: 3, ok: 'ok_fondo', pts: 3, bonus: 15 },
      t5a: { area: 'rit', nk: 'm_t5a', dk: 'm_t5a_d', n: RALLY_MILL.t5a[0], ok: 'ok_beat', pts: 1, bonus: RALLY_BONUS.t5a[0] },
      /* M7d (r120) · METRÓNOMO LOCO: el mismo rally con la máquina
       * TRAICIONERA (velocidad variable por bola). Hitos 20 · 40 · 80. */
      t5b: { area: 'rit', nk: 'm_t5b', dk: 'm_t5b_d', n: RALLY_MILL.t5b[0], ok: 'ok_beat', pts: 1, bonus: RALLY_BONUS.t5b[0] },
    };
    /* M7d (r120) · POOL DE LOS RETOS — el PULSO diario (r76) y el semanal
     * (r118) sembraban sobre Object.keys(MODES): con ejercicios nuevos el
     * pool cambiaría y el determinismo («igual para toda la academia»)
     * se rompería en mitad de la septana. PLAN_POOL congela los 9
     * clásicos EN ORDEN: los planes de hoy son byte-idénticos a 3.6.108
     * y los dos ejercicios nuevos son entrenamiento libre puro. */
    const PLAN_POOL = ['t1a', 't1b', 't2a', 't2b', 't3a', 't3b', 't4a', 't4b', 't5a'];
    /* M7d (r120) · modos RALLY (el contador manda sobre la racha): t5a y
     * t5b comparten juez, HUD y latido; la máquina del LOCO traiciona. */
    const isRallyM = () => active === 't5a' || active === 't5b';
    const BEAT_INT = () => (active === 't5b' ? 1.45 : 1.65);
  
  
    /* =================================================================
     *  ESTADO DE SESIÓN Y REFERENCIAS
     *  ================================================================= */
    let G = null;                    // instancia del juego (window.__PP_GAME)
    let grp = null;                  // grupo de escena del módulo
    let active = null;               // id del modo en curso (MODES key) o null
    let uiPage = 'hub';              // 'hub' | 'area'
    let uiArea = 'dir';
    let rainbowT = 0;
    let rainbowCol = null;        // r74 · color reciclado (cero allocs por frame)
  
    const st = {
      streak: 0, goal: 0, sessPts: 0, rally: 0, bounces: 0,
      live: false, deadT: 0, wait: 0.8, phase: 'feed',
      cross: null, apex: 0, hitPos: null, bouncePos: null, lastBounce: null,
      target: null, toast: '', toastT: 0, feedT: 0, beat: 0, shotRec: false,
      aiTouched: false,   // v3.0.2 · la bola ya botó en el campo rival tras el golpe (metrónomo)
      shotPts: [], spinIconT: 0, spinIconCol: null, done: 0,
      tossReleaseY: 0, tossMaxY: 0,   // v3.0.8-TRN1 · validación del lanzamiento (como el núcleo)
      roundHits: 0, roundFaults: 0,   // v3.0.7-PLAY1 · precisión de la ronda en curso
      daily: 0,           // r80 · 1 = sesión del RETO DIARIO: zonas el DOBLE de anchas (zonaDims)
    };
  
    /* ---------------- constantes geométricas locales ---------------- */
    const C = () => DIMS.tableCenterZ;
    const TOP = () => DIMS.tableTopY;
    const HW = () => DIMS.tableHalfWidth;
    const HL = () => DIMS.tableHalfLength;
    /* r101 · BARRA INTERACTIVA DEL PASE BAJO — AJUSTE POR PROXIMIDAD.
     * La r100 lo intentó con flechas + rayo de la mano libre y el GATILLO
     * consumido; el dueño lo retiró: «es inútil, cuesta enfocar, donde
     * apunto y donde están los botones nada tienen que ver y se pisa el
     * gatillo que suelta las bolas del tee». En el tee TODOS los botones
     * están vivos (gatillo = lanzar, grip = lanzamiento natural al soltar),
     * así que el ajuste NO usa NINGÚN botón: la MANO LIBRE entra en el
     * pasillo de la cinta (≥0,30 s) y la barra pasa a SEGUIR la altura de
     * la mano en vivo (pasos de 1 cm, blip y háptica por paso, clamps
     * 5..40 cm); al APARTAR la mano del pasillo la altura queda fijada y
     * guardada (persistencia pp_train_barra_v1). Interacción directa,
     * cómoda y cero interferencias con el juego. */
    let barraH = 0.17;
    let barraZona = false;       // mano libre dentro del pasillo de la cinta
    let barraZonaT = 0;          // dwell dentro del pasillo (s)
    let barraAgarrada = false;   // la barra sigue la mano AHORA
    try {
      const _bh = JSON.parse(localStorage.getItem('pp_train_barra_v1') || '{}');
      if (typeof _bh.h === 'number' && _bh.h >= 0.05 && _bh.h <= 0.40) barraH = _bh.h;
    } catch (e) { /* sin almacenamiento: 17 cm de siempre */ }
    const BARRA_MIN = 0.05, BARRA_MAX = 0.40;
    const BARRA_DWELL = 0.30;                // s en el pasillo para agarrar
    const BARRA_PASO = 0.01;                 // resolución: 1 cm
    const RIBBON_Y = () => DIMS.netTopY + barraH;         // cinta AJUSTABLE
    const BARRA_CM = () => Math.round((DIMS.netTopY + barraH - DIMS.tableTopY) * 100);
    const APEX_Y = 1.50;                                  // aro del globo defensivo
    const CROSS_LOW = () => DIMS.netTopY + 0.055;         // pase bajo correcto
    const CROSS_HI = () => DIMS.netTopY + 0.16;           // demasiado alto

    /* =================================================================
     *  r80 · EL RETO PERMISIVO — dimensiones de zona COMPARTIDAS por el
     *  PINTOR (drawQuad) y el JUEZ (judgeAiBounce): lo pintado ES lo
     *  juzgado (regla de la casa desde v3.0.8-TRN1). Petición del dueño
     *  para el RETO DIARIO: «las zonas de bote a las que debemos acertar
     *  sean más permisivas y grandes… digamos que el doble de anchas…
     *  para no desanimar al jugador» (la dificultad irá subiendo con el
     *  tiempo). En entrenamiento normal, TODO queda byte a byte igual.
     *  ================================================================= */
    function zonaDims() {
      const diario = !!st.daily;
      return {
        diario: diario ? 1 : 0,
        t1aCentro: diario ? 0.075 : 0.15,   // semiancho del centro prohibido (0,30 m → 0,15 m)
        // frontera de fila del objetivo como fracción de HL (dz > HL·f):
        // 'deep' 0,5 → 0,25 (abarca profunda+media) · 'mid' 0,25 → 0 (media+corta)
        t1aDeepF: diario ? 0.25 : 0.5,
        t1aMidF: diario ? 0 : 0.25,
        t1bBanda: diario ? 0.20 : 0.10,     // bandas laterales 10 cm → 20 cm
        t1bFondo: diario ? 0.24 : 0.12,     // franja de fondo 12 cm → 24 cm
        t4aProf: diario ? 1.07 : 0.56,      // borde del doble bote desde la red (vano 0,51 → 1,02 m)
        t4bFondo: diario ? 0.30 : 0.15,     // franja de fondo del saque largo 15 cm → 30 cm
      };
    }
  
    /* =================================================================
     *  CONSTRUCCIÓN DE ESCENA (una sola vez, grupo propio)
     *  ================================================================= */
    function mkCanvas(w, h) {
      const cv = document.createElement('canvas');
      cv.width = w; cv.height = h;
      return cv;
    }
    function texOf(cv) {
      const tx = new THREE.CanvasTexture(cv);
      tx.colorSpace = THREE.SRGBColorSpace;
      tx.anisotropy = 4;
      return tx;
    }
  
    // --- plano de mesa (cuadrantes / bandas / zona de saque) ---
    let quadTex = null, quadMesh = null, quadCtx = null;
    function buildQuadPlane() {
      const cv = mkCanvas(512, 512);
      quadCtx = cv.getContext('2d');
      quadTex = texOf(cv);
      // v3.6.19 (ronda 26) · FIX ZONAS: la fila 0 del canvas es la RED (convención
      // mz() de drawQuad). Con el flipY por defecto (true) y rotation.x = -π/2 la
      // fila 0 aterriza en el FONDO y todo el overlay se muestra ESPEJADO en
      // profundidad: la zona OBJETIVO pintaba en la profundidad CONTRARIA a la
      // que el juez acepta (prueba GPU: objetivo mid → el jugador veía el amarillo
      // en dz [0.66, 1.05] m y el juez aceptaba [0.34, 0.69]). flipY=false coloca
      // la fila 0 en la red: t1a, t1b, t4a y t4b quedan EXACTOS a lo pintado.
      quadTex.flipY = false;
      const m = new THREE.Mesh(
        new THREE.PlaneGeometry(HW() * 2, HL()),
        new THREE.MeshBasicMaterial({ map: quadTex, transparent: true, depthWrite: false, opacity: 0.94 }),
      );
      m.rotation.x = -Math.PI / 2;
      m.position.set(0, TOP() + 0.0045, C() - HL() / 2);
      m.renderOrder = 3;
      m.visible = false;
      return m;
    }
  
    // --- cinta sobre la red (pase bajo) ---
    // r101 · la cinta trae SUS MANDOS: rótulo con la lectura en cm sobre la
    // SUPERFICIE de la mesa y las dos flechas flanqueándolo — ya no son
    // botones de rayo: indican el ajuste por proximidad (mano libre).
    function barraChevronTex(dir) {
      const cv = mkCanvas(96, 96), x = cv.getContext('2d');
      x.fillStyle = '#16202c';
      x.beginPath();
      if (x.roundRect) x.roundRect(6, 6, 84, 84, 20); else x.rect(6, 6, 84, 84);
      x.fill();
      x.lineWidth = 4; x.strokeStyle = '#8f6a3a';
      x.stroke();
      x.lineWidth = 11; x.lineCap = 'round'; x.lineJoin = 'round';
      x.strokeStyle = '#ffbf5a';
      x.beginPath();
      if (dir > 0) { x.moveTo(26, 58); x.lineTo(48, 34); x.lineTo(70, 58); }
      else { x.moveTo(26, 38); x.lineTo(48, 62); x.lineTo(70, 38); }
      x.stroke();
      return texOf(cv);
    }
    function pistaBarra() {
      if (barraAgarrada) return LANG === 'en' ? 'PULL AWAY TO SET' : 'APARTA LA MANO PARA FIJAR';
      if (barraZona) return LANG === 'en' ? 'MOVE YOUR HAND ↑↓' : 'MUEVE LA MANO ↑↓';
      // r102 · pista por defecto = LOS DOS CAMINOS (petición del dueño:
      // «debemos informar de este control de altura al jugador»)
      return LANG === 'en' ? 'STICK ↑↓ OR HAND AT RIBBON' : 'JOYSTICK ↑↓ O MANO EN LA CINTA';
    }
    function barraLabelTex() {
      // r102 · lienzo 400 px (la pista nueva con el joystick cabe de sobra;
      // el sprite escala a 0,34 m para conservar la densidad de píxeles)
      const cv = mkCanvas(400, 110), x = cv.getContext('2d');
      x.clearRect(0, 0, 400, 110);
      x.fillStyle = 'rgba(20,26,36,0.88)';
      x.beginPath();
      if (x.roundRect) x.roundRect(4, 4, 392, 102, 22); else x.rect(4, 4, 392, 102);
      x.fill();
      x.lineWidth = 4; x.strokeStyle = barraAgarrada ? '#ffe08a' : '#ffb84d';
      x.stroke();
      x.textAlign = 'center'; x.textBaseline = 'middle';
      x.fillStyle = '#ffd27a';
      x.font = 'bold 56px "Noto Sans SC", sans-serif';
      x.fillText(String(BARRA_CM()) + ' cm', 200, 42);
      x.fillStyle = (barraZona || barraAgarrada) ? '#ffe8b0' : '#9fb3c8';
      x.font = '20px "Noto Sans SC", sans-serif';
      x.fillText(pistaBarra(), 200, 84);
      return texOf(cv);
    }
    let barraUp = null, barraDn = null, barraLbl = null;
    let barraRibbon = null;                 // cinta viva (band+glow) para barraLay
    let barraUltCm = -1;                    // repintado del rótulo sólo al cambiar
    let barraAvisoHecho = false;            // r102: toast informativo 1 vez/sesión
    const BARRA_SEP = 0.24;                 // flechas flanqueando el rótulo
    // r103 · ETIQUETAS FUERA DE LA VISTA (petición del dueño: «las etiquetas
    // de altura de la barra no estén en primer plano: no dejan jugar con
    // comodidad al estar sobre la línea de visión de mesa. Estarán FIJAS sin
    // ningún cambio de orientación, ancladas a la altura de la barra que
    // movemos y en su mismo plano, pero en la parte DERECHA fuera de la
    // visión de la mesa»): la pastilla de cm y las flechas viven en el
    // PLANO de la barra (z local 0 — el grupo vive en z=C()) y a la DERECHA
    // de la mesa, 0,42 m más allá del canto derecho (+0,76) → x ≈ 1,18 m:
    // fuera de la mesa y del tiro, a la vista con un mínimo giro de cabeza.
    // La altura SIGUE viva (RIBBON_Y + 0,075): sube y baja con la barra.
    const BARRA_LBL_X = () => HW() + 0.42;
    function barraLay() {
      // recoloca cinta + mandos a la altura viva (cada ajuste)
      const by = RIBBON_Y();
      const xl = BARRA_LBL_X();
      if (barraLbl) barraLbl.position.set(xl, by + 0.075, 0);
      if (barraUp) barraUp.position.set(xl - BARRA_SEP, by + 0.075, 0);
      if (barraDn) barraDn.position.set(xl + BARRA_SEP, by + 0.075, 0);
      if (barraRibbon) { barraRibbon.band.position.y = by; barraRibbon.glow.position.y = by + 0.02; }
    }
    function buildRibbon() {
      const g = new THREE.Group();
      const band = new THREE.Mesh(
        new THREE.BoxGeometry(1.86, 0.035, 0.012),
        new THREE.MeshBasicMaterial({ color: 0xff8a2a, transparent: true, opacity: 0.85 }),
      );
      band.position.y = RIBBON_Y();
      g.add(band);
      const glow = new THREE.Mesh(
        new THREE.BoxGeometry(1.86, 0.006, 0.016),
        new THREE.MeshBasicMaterial({ color: 0xffd27a, transparent: true, opacity: 0.95 }),
      );
      glow.position.y = RIBBON_Y() + 0.02;
      g.add(glow);
      barraRibbon = { band, glow };
      // r103 · MANDOS DE ALTURA: PLANOS DE ORIENTACIÓN FIJA (adiós sprites
      // que se re-orientan con la cabeza — petición del dueño: «fijas sin
      // ningún cambio de orientación»): miran a +z (al jugador de siempre),
      // NUNCA giran, y el ajuste sigue siendo por PROXIMIDAD de la mano
      // libre + joystick (sin gatillo).
      const mkBoton = (dir) => {
        const s = new THREE.Mesh(
          new THREE.PlaneGeometry(0.085, 0.085),
          new THREE.MeshBasicMaterial({
            map: barraChevronTex(dir), transparent: true, depthWrite: false,
            opacity: 0.94, side: THREE.DoubleSide,
          }),
        );
        g.add(s);
        return s;
      };
      barraUp = mkBoton(1);
      barraDn = mkBoton(-1);
      barraLbl = new THREE.Mesh(
        new THREE.PlaneGeometry(0.34, 0.0935),
        new THREE.MeshBasicMaterial({
          map: barraLabelTex(), transparent: true, depthWrite: false,
          opacity: 0.96, side: THREE.DoubleSide,
        }),
      );   // r102: lienzo 400 px · r103: plano fijo en vez de sprite
      g.add(barraLbl);
      barraLay();
      g.position.set(0, 0, C());
      g.visible = false;
      return g;
    }

    /* r101 · MÁQUINA DE AJUSTE (pura, verificable en QA): (px, py, pz) =
     * posición de la mano libre en mundo. Dentro del pasillo de la cinta
     * (|x| ≤ semiancho+0,30 · |z−cinta| ≤ 0,20 · altura cerca de la red)
     * durante ≥ BARRA_DWELL la barra se AGARRA y sigue la mano en pasos de
     * 1 cm; fuera del pasillo se suelta (fijar + guardar). Sin botones. */
    const hMano = () => G.ballHand;          // mano libre (getter del núcleo)
    function barraFijar(hRaw, salto) {
      const sube = hRaw >= barraH;
      const h = THREE.MathUtils.clamp(
        Math.round(hRaw / BARRA_PASO) * BARRA_PASO, BARRA_MIN, BARRA_MAX);
      const cambio = Math.abs(h - barraH) > 1e-9;
      barraH = h;
      if (cambio || salto) {
        barraUltCm = -1;
        barraLay();
        barraPinta();
      }
      if (cambio) {
        try { G.audio.playOsc(sube ? 640 : 480, sube ? 760 : 400, 0.05, 'sine', 0.10, 0); } catch (eBF) { /* */ }
        try { G.haptic(hMano(), 0.12, 18); } catch (eBF2) { /* */ }
      }
    }
    function barraSoltar() {
      barraAgarrada = false;
      barraUltCm = -1;
      barraPinta();
      try { localStorage.setItem('pp_train_barra_v1', JSON.stringify({ h: Math.round(barraH * 1000) / 1000 })); } catch (eBS) { /* */ }
      try { G.audio.playOsc(520, 340, 0.09, 'triangle', 0.12, 0); } catch (eBS2) { /* */ }
      toast((LANG === 'en' ? 'Bar: ' : 'Barra: ') + BARRA_CM() + ' cm', true);
    }
    function barraPinta() {
      const cm = BARRA_CM();
      if (barraLbl && barraUltCm !== cm) {
        barraLbl.material.map = barraLabelTex();
        barraLbl.material.needsUpdate = true;
        barraUltCm = cm;
      }
      const tinte = barraAgarrada ? 0xffffff : (barraZona ? 0xffe0a8 : 0xbfcfe0);
      if (barraUp) barraUp.material.color.setHex(tinte);
      if (barraDn) barraDn.material.color.setHex(tinte);
    }
    function barraUpdate(px, py, pz, dt) {
      if (!ribbonG || !ribbonG.visible) {
        barraZona = false; barraZonaT = 0;
        if (barraAgarrada) barraSoltar();
        return { zona: false, agarrada: false };
      }
      const dz = pz - ribbonG.position.z;
      const enZona = Math.abs(px) <= DIMS.tableHalfWidth + 0.30 &&
        Math.abs(dz) <= 0.20 &&
        py >= DIMS.netTopY - 0.06 && py <= DIMS.netTopY + 0.60;
      if (enZona) {
        barraZonaT += dt;
        if (!barraZona) { barraZona = true; barraPinta(); }
        if (!barraAgarrada && barraZonaT >= BARRA_DWELL) {
          barraAgarrada = true;
          barraFijar(py - DIMS.netTopY, true);      // agarre: la barra salta a la mano
          try { G.audio.playOsc(300, 520, 0.10, 'triangle', 0.16, 0); } catch (eGA) { /* */ }
        } else if (barraAgarrada) {
          barraFijar(py - DIMS.netTopY, false);     // sigue la mano en vivo
        }
      } else {
        barraZonaT = 0;
        if (barraZona) { barraZona = false; barraPinta(); }
        if (barraAgarrada) barraSoltar();
      }
      return { zona: barraZona, agarrada: barraAgarrada };
    }
    /* r102 · JOYSTICK (petición del dueño: «su altura se controla mejor con
     * cualquiera de los joysticks de los mandos… debemos informar de este
     * control al jugador»): el eje Y de CUALQUIER stick sube/baja la barra
     * en pasos de 1 cm (BARRA_STICK_V a plena deflexión, muerta 0,30; los
     * dos sticks SUMAN). El stick MANDA sobre la proximidad: suelta la
     * barra si estuviera agarrada y anula el dwell para que la mano no la
     * re-agarre sola. En el PRO TRAINING el stick no tiene OTRO uso
     * (updateCalibration retorna antes con trainV3 activo — sin conflicto). */
    const BARRA_STICK_V = 0.14;              // m/s a plena deflexión
    let barraStickAcc = 0;                   // fracción de paso de 1 cm pendiente
    function barraStick(dt) {
      if (!ribbonG || !ribbonG.visible) { barraStickAcc = 0; return false; }
      let y = 0;
      for (let h = 0; h < 2; h++) {
        const ax = G.stickAxis ? G.stickAxis(h) : null;
        if (ax && Math.abs(ax.y) > 0.30) y += -ax.y;   // stick arriba = subir
      }
      if (!y) { barraStickAcc = 0; return false; }
      if (barraAgarrada) barraSoltar();
      barraZona = false; barraZonaT = 0;               // el stick anula el dwell
      barraStickAcc += y * BARRA_STICK_V * dt / BARRA_PASO;
      const pasos = Math.trunc(barraStickAcc);
      if (pasos) {
        barraStickAcc -= pasos;
        barraFijar(barraH + pasos * BARRA_PASO, false);
        return true;
      }
      return false;
    }
    /* r101 · TICK: posición REAL de la mano libre → máquina de ajuste. */
    const _bW = new THREE.Vector3();
    function barraTick(dt) {
      if (!ribbonG || !ribbonG.visible) { barraUpdate(0, -1, 0, dt); return; }
      barraStick(dt);                        // r102: joystick, cualquier mando
      const h = G.ballHand;
      const ray = G.rays && G.rays[h];
      if (!ray || !G.connected || !G.connected[h]) {
        if (barraAgarrada || barraZona) barraUpdate(0, -1, 0, dt);
        return;
      }
      ray.getWorldPosition(_bW);
      barraUpdate(_bW.x, _bW.y, _bW.z, dt);
    }
    /* r101 · AJUSTE DIRECTO ±1 cm (QA; el juego usa barraUpdate). */
    function barraAjustar(dir) {
      if (!ribbonG || !ribbonG.visible) return false;
      barraH = THREE.MathUtils.clamp(
        Math.round((barraH + (dir > 0 ? BARRA_PASO : -BARRA_PASO)) * 1000) / 1000,
        BARRA_MIN, BARRA_MAX);
      barraUltCm = -1;
      barraLay();
      barraPinta();
      return true;
    }

    // --- aro de altura (globo defensivo) ---
    function buildApexRing() {
      const g = new THREE.Group();
      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(0.16, 0.012, 10, 40),
        new THREE.MeshBasicMaterial({ color: 0x53e0a8, transparent: true, opacity: 0.9 }),
      );
      ring.rotation.x = Math.PI / 2;
      g.add(ring);
      const beam = new THREE.Mesh(
        new THREE.CylinderGeometry(0.004, 0.004, APEX_Y - TOP(), 6),
        new THREE.MeshBasicMaterial({ color: 0x53e0a8, transparent: true, opacity: 0.28 }),
      );
      beam.position.y = -(APEX_Y - TOP()) / 2;
      g.add(beam);
      // r100 · ARO EN EL CENTRO DE LA MESA (duda del dueño: «aparece una
      // línea con un círculo o toro arriba… pensé que debería estar situado
      // en el medio de la mesa»). La representación ES correcta — el toro
      // horizontal es el ARO objetivo por encima del que pasa el globo y la
      // línea es el haz de guía hasta la mesa — pero vivía a +0,50 m hacia
      // el rival: flotaba sobre la media-cancha contraria y confundía. El
      // apex de un globo real ocurre junto a la red, así que el aro se ancla
      // al CENTRO de la mesa (sobre la línea): el juez no cambia (mide el
      // apex máximo del vuelo, no la posición del aro) — sólo la escena.
      g.position.set(0, APEX_Y, C());
      g.visible = false;
      return g;
    }
  
    // --- aro-metrónomo en el suelo ---
    function buildMetroRing() {
      const m = new THREE.Mesh(
        new THREE.TorusGeometry(0.22, 0.012, 8, 40),
        new THREE.MeshBasicMaterial({ color: 0xf687b3, transparent: true, opacity: 0.85 }),
      );
      m.rotation.x = -Math.PI / 2;
      m.position.set(0, 0.012, C() + 1.32);
      m.visible = false;
      return m;
    }
  
    // --- marcas de bote (pool) ---
    const MARKS_N = 10;
    let marks = [], markIdx = 0;
    function buildMarks() {
      const out = [];
      for (let i = 0; i < MARKS_N; i++) {
        const m = new THREE.Mesh(
          new THREE.TorusGeometry(0.05, 0.006, 6, 26),
          new THREE.MeshBasicMaterial({ color: 0xffe08a, transparent: true, opacity: 0 }),
        );
        m.rotation.x = -Math.PI / 2;
        m.visible = false;
        m.userData.ttl = 0;
        out.push(m);
      }
      return out;
    }
    function spawnMark(p, col) {
      if (!S.fb.marks) return;
      const m = marks[markIdx]; markIdx = (markIdx + 1) % MARKS_N;
      m.position.set(p.x, TOP() + 0.006, p.z);
      m.material.color.setHex(col || 0xffe08a);
      m.material.opacity = 0.95;
      m.userData.ttl = 1.6;
      m.visible = true;
    }
  
    // --- línea de tiro (trayectoria REAL del último golpe) ---
    const SHOT_N = 96;
    let shotLine = null, shotGeo = null, shotTtl = 0;
    function buildShotLine() {
      shotGeo = new THREE.BufferGeometry();
      shotGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(SHOT_N * 3), 3));
      const m = new THREE.Line(shotGeo, new THREE.LineBasicMaterial({
        color: 0x7ae0ff, transparent: true, opacity: 0, depthWrite: false,
      }));
      m.renderOrder = 4;
      m.frustumCulled = false;
      return m;
    }
    function shotLineShow() {
      const n = Math.min(st.shotPts.length, SHOT_N);
      const arr = shotGeo.attributes.position.array;
      for (let i = 0; i < n; i++) {
        arr[i * 3] = st.shotPts[i].x;
        arr[i * 3 + 1] = st.shotPts[i].y;
        arr[i * 3 + 2] = st.shotPts[i].z;
      }
      shotGeo.setDrawRange(0, n);
      shotGeo.attributes.position.needsUpdate = true;
      shotLine.material.opacity = 0.85;
      shotTtl = 2.4;
      shotLine.visible = true;
    }
  
    // --- flecha de efecto sobre la bola ---
    let spinSprite = null;
    function buildSpinSprite() {
      const cv = mkCanvas(64, 64);
      const g2 = cv.getContext('2d');
      g2.strokeStyle = '#ffffff';
      g2.lineWidth = 7;
      g2.beginPath();
      g2.arc(32, 32, 20, 0.25, Math.PI * 1.45);
      g2.stroke();
      g2.fillStyle = '#ffffff';
      g2.beginPath();
      g2.moveTo(46, 6); g2.lineTo(58, 20); g2.lineTo(38, 24);
      g2.closePath(); g2.fill();
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({
        map: texOf(cv), transparent: true, opacity: 0, depthWrite: false,
      }));
      sp.scale.setScalar(0.085);
      sp.renderOrder = 6;
      return sp;
    }
  
    // --- panel flotante HUD del entrenamiento ---
    let ribbonG = null, apexG = null, metroG = null;
    let panel = null, panelCv = null, panelCtx = null, panelTex = null, panelDirty = true;
    function buildPanel() {
      panelCv = mkCanvas(768, 400);
      panelCtx = panelCv.getContext('2d');
      panelTex = texOf(panelCv);
      const m = new THREE.Mesh(
        new THREE.PlaneGeometry(1.32, 0.687),
        new THREE.MeshBasicMaterial({ map: panelTex, transparent: true, depthWrite: false }),
      );
      m.position.set(0, 1.60, C() - 1.95);
      m.rotation.x = -0.05;
      m.scale.setScalar(1.15);
      m.renderOrder = 5;
      m.visible = false;
      return m;
    }
  
    function rr2(g, x, y, w, h, r) {
      g.beginPath();
      g.moveTo(x + r, y);
      g.arcTo(x + w, y, x + w, y + h, r);
      g.arcTo(x + w, y + h, x, y + h, r);
      g.arcTo(x, y + h, x, y, r);
      g.arcTo(x, y, x + w, y, r);
      g.closePath();
    }
  
    function drawPanel() {
      const g = panelCtx, W = 768, H = 400;
      const M = active ? MODES[active] : null;
      g.clearRect(0, 0, W, H);
      // fondo
      const bg = g.createLinearGradient(0, 0, 0, H);
      bg.addColorStop(0, 'rgba(10,14,24,0.96)');
      bg.addColorStop(1, 'rgba(16,22,38,0.96)');
      rr2(g, 6, 6, W - 12, H - 12, 26);
      g.fillStyle = bg; g.fill();
      g.strokeStyle = 'rgba(240,200,90,0.85)'; g.lineWidth = 5; g.stroke();
      // cabecera
      g.textAlign = 'left'; g.textBaseline = 'middle';
      g.fillStyle = '#f0c85a';
      g.font = '800 44px system-ui, sans-serif';
      g.fillText(t('hub_t'), 34, 52);
      g.fillStyle = '#8fa0b8';
      g.font = '600 22px system-ui, sans-serif';
      g.fillText(M ? t(M.nk) : t('hub_s'), 34, 96);
      if (M) {
        // contador grande
        const big = isRallyM() ? String(st.rally) : (String(st.streak) + ' / ' + objN());
        g.textAlign = 'center';
        g.fillStyle = '#ffffff';
        g.font = '900 110px system-ui, sans-serif';
        g.fillText(big, W / 2, 216);
        g.fillStyle = '#8fa0b8';
        g.font = '700 26px system-ui, sans-serif';
        g.fillText(isRallyM() ? t('hud_rally') : t('hud_racha') + ' · ' + t('hud_meta'), W / 2, 292);
        // toast
        if (st.toastT > 0) {
          g.fillStyle = st.toastOk ? '#68d391' : '#fc8181';
          g.font = '800 34px system-ui, sans-serif';
          g.fillText(st.toast, W / 2, 340);
        } else {
          g.fillStyle = '#a9b8cc';
          g.font = '600 24px system-ui, sans-serif';
          g.fillText(active === 't4a' || active === 't4b' ? t('sirve') : t('obj') + ': ' + objN() + ' ' + t('seg'), W / 2, 340);
        }
        // puntos
        g.textAlign = 'left';
        g.fillStyle = '#f0c85a';
        g.font = '800 30px system-ui, sans-serif';
        g.fillText('+' + st.sessPts, 34, H - 32);
        g.textAlign = 'right';
        g.fillStyle = '#8fa0b8';
        g.font = '600 24px system-ui, sans-serif';
        g.fillText(t('hud_total') + ' ' + S.pts, W - 34, H - 32);
        // v3.0.7-PLAY1 · PRO CIRCUITO: combo, estrellas del modo y precisión
        if (GAMF()) {
          const mul = comboMul();
          if (mul > 1) {
            g.textAlign = 'center';
            g.fillStyle = mul >= 3 ? '#ffb84d' : '#ffd76a';
            g.font = '900 ' + (46 + mul * 6) + 'px system-ui, sans-serif';
            g.fillText('×' + mul, W / 2 + 250, 216);
          }
          const stN = S.stars[active] || 0;
          g.textAlign = 'right';
          g.fillStyle = '#f0c85a';
          g.font = '800 30px system-ui, sans-serif';
          g.fillText('\u2605'.repeat(stN) + '\u2606'.repeat(3 - stN), W - 34, 52);
          const tries = st.roundHits + st.roundFaults;
          if (tries > 0 && !isRallyM()) {
            const acc = Math.round(st.roundHits / tries * 100);
            g.fillStyle = '#8fa0b8';
            g.font = '600 20px system-ui, sans-serif';
            g.fillText(t('acc') + ' ' + acc + '%', W - 34, 96);
          }
        }
      }
      panelTex.needsUpdate = true;
    }
  
    /* ---------------- montaje del grupo ---------------- */
    function buildScene() {
      if (grp || !G || !G.rig) return;
      grp = new THREE.Group();
      grp.name = 'ppTrainGrp';
      quadMesh = buildQuadPlane();
      grp.add(quadMesh);
      ribbonG = buildRibbon();
      grp.add(ribbonG);
      apexG = buildApexRing();
      grp.add(apexG);
      metroG = buildMetroRing();
      grp.add(metroG);
      marks = buildMarks();
      for (const m of marks) grp.add(m);
      shotLine = buildShotLine();
      grp.add(shotLine);
      spinSprite = buildSpinSprite();
      grp.add(spinSprite);
      panel = buildPanel();
      grp.add(panel);
      grp.visible = false;
      // V3.0.1 · FIX del casco: el grupo vive DENTRO del rig (el mismo espacio
      // que la bola, la mesa y los eventos de física). En V3.0 se colgaba de la
      // raíz de la escena y el RECENTRADO del rig (updateRecenter gira rig.y)
      // lo dejaba girado/desplazado: todas las marcas salían desfasadas de la
      // bola. Como hijo del rig, bola y marcas SIEMPRE coinciden.
      G.rig.add(grp);
    }
  
  
    /* =================================================================
     *  MÁQUINA DE BOLAS Y SAQUE
     *  ================================================================= */
    function resetSessJudge() {
      st.live = false; st.deadT = 0; st.cross = null; st.apex = 0;
      st.hitPos = null; st.bouncePos = null; st.aiBounce = 0; st.shotRec = false;
      st.aiTouched = false;
      st.shotPts.length = 0;
    }
    /** Saque reglamentario de la máquina hacia el jugador (opcionalmente
     *  con efecto real: el solver lo compensa con Magnus incluido). */
    function feedToPlayer(opts) {
      opts = opts || {};
      const b = G.ball;
      G.resetToss();
      b.pos.set(opts.x !== undefined ? opts.x : (Math.random() * 2 - 1) * 0.18,
        1.02, C() - HL() - 0.30);
      let v, sp;
      if (opts.target && opts.spin) {
        // tiro resuelto con efecto REAL (arrastre + Magnus simulados)
        v = computeShotVelocityReal(b.pos, opts.target, opts.tIn || 0.62, opts.max || 8.5, opts.spin);
        sp = opts.spin;
      } else if (opts.rally) {
        // v3.0.8-TRN1 · BOLA DE SPARRING: tiro directo y profundo al campo del
        // jugador, resuelto con Magnus (despeje de red garantizado). Antes la
        // máquina alimentaba con SAQUES del solver: cuando la fase rápida
        // fallaba caían bolas lentas y cortas («tiradas cortas a la red»).
        // Ahora viven en la zona media-profunda, como un rival real.
        const tx = (Math.random() * 2 - 1) * 0.24;
        const tz = C() + HL() * (0.52 + Math.random() * 0.26);
        v = computeShotVelocityReal(b.pos, new THREE.Vector3(tx, 0, tz),
          0.56 + Math.random() * 0.10, opts.max || 7.8, new THREE.Vector3());
        sp = new THREE.Vector3();
      } else {
        const r = findServeVelocity(b.pos, -1);
        v = r.v; sp = r.spin;
        if (opts.speedMul) v.multiplyScalar(opts.speedMul);
      }
      b.vel.copy(v);
      b.spin.copy(sp || new THREE.Vector3());
      G.audio.serve();
      resetSessJudge();
      st.beat = 0;
    }
    /** v3.0.8-TRN1 · SOPORTE DE SAQUE natural: la bola espera EN LA MANO
     *  LIBRE del jugador (antes flotaba fija detrás de la línea de fondo y
     *  antes aún SOBRE la mesa, inalcanzable). Se lanza SOLO con el gesto del
     *  jugador — soltar el grip (velocidad real de la mano) o el gatillo —
     *  y luego se golpea en el aire con el margen ampliado del saque. */
    function serveTee() {
      const b = G.ball;
      G.resetToss();
      // v3.0.8-TRN1 · SAQUE REAL: la bola descansa EN LA MANO LIBRE (misma
      // cinemática que el núcleo en partido: copia la mano + BALL_HAND_LIFT).
      // Sólo si no hay mano activa (1 mando / escritorio) flota en el punto
      // de apoyo clásico detrás de la línea de fondo.
      b.vel.set(0, 0, 0);
      b.spin.set(0, 0, 0);
      const bh = G.controllerPaddles && G.controllerPaddles[G.ballHand];
      if (bh && bh.active) {
        b.pos.copy(bh.pos);
        b.pos.y += BALL_HAND_LIFT;
      } else {
        b.pos.set(0.30, 1.05, C() + HL() + 0.35);
      }
      st.tossReleaseY = b.pos.y; st.tossMaxY = b.pos.y;
      resetSessJudge();
      st.phase = 'tee';
      st.teeT = 0;
    }
    /** v3.0.8-TRN1 · Lanzamiento con el GESTO DEL JUGADOR. v3.1.0-SRV2
     *  (requisito A): abrir el grip (serveRelease) lanza con la velocidad
     *  REAL de la mano libre — sin subida mínima escondida; el GATILLO
     *  (serveTrigger) es la ayuda explícita y da la subida asistida por
     *  dificultad. `assisted` separa los dos caminos. Nada de tiros
     *  automáticos: el jugador decide el momento. */
    function serveTossFromTee(assisted) {
      if (st.phase !== 'tee') return;
      const b = G.ball;
      const bh = G.controllerPaddles && G.controllerPaddles[G.ballHand];
      // v3.0.9-HALL1 · subida mínima del lanzamiento asistido POR DIFICULTAD
      const vyMin = (G.serveTier ? G.serveTier().vy : DIMS.serveAssistVy);
      const v = new THREE.Vector3(0, vyMin, 0);
      if (bh && bh.active) {
        v.copy(bh.vel);
        if (assisted) {
          // gatillo: la bola SIEMPRE sube lo suficiente para golpearla
          if (v.y < vyMin) v.y = vyMin;
          v.x *= 0.4; v.z *= 0.4;
        }
        // seguridad común: deriva horizontal acotada y tope de subida (~1 m)
        v.x = THREE.MathUtils.clamp(v.x, -1.2, 1.2);
        v.z = THREE.MathUtils.clamp(v.z, -1.2, 1.2);
      }
      if (assisted && v.y < vyMin) v.y = vyMin;
      if (v.y > 4.6) v.y = 4.6;
      b.vel.copy(v);
      b.spin.set(0, 0, 0);
      st.tossReleaseY = b.pos.y; st.tossMaxY = b.pos.y;
      st.phase = 'toss';
      st.tossT = 0;
      st.teeT = 0;
      G.audio.serve();
      try { G.haptic(G.ballHand, 0.45); } catch (e) { /* */ }
    }
    /** margen de detección ampliado SOLO mientras la bola del entrenamiento
     *  vuela tras el lanzamiento (el núcleo lo pone a 0 cada frame en calib).
     *  v3.1.0-SRV2: también activa el flag serveFlight (tolerancias y suelo
     *  de saque en collidePaddle). */
    function drillReach(on) {
      if (!G || !G.controllerPaddles) return;
      const reach = (G.serveTier ? G.serveTier().reach : DIMS.serveExtraReach);
      for (const ps of G.controllerPaddles) {
        if (ps) { ps.extraReach = on ? reach : 0; ps.serveFlight = on; }
      }
    }

    /** v3.0.8-TRN1 · ASISTENCIA DEL GOLPEO DE SAQUE en el entrenamiento.
     *  v3.1.0-SRV2 · EXACTAMENTE la pieza nueva del núcleo: impulso real
     *  (collidePaddle ya actuó con la orientación de la cara) + asistencia
     *  PROGRESIVA ACOTADA (applyServeProgressiveAssist: mezcla hacia una
     *  referencia legal sólo dentro del margen angular, decaída lineal,
     *  NUNCA convierte un mal gesto en saque válido). Fuera la cascada
     *  45 % → 75 % → solver y el suelo de 3,2 m/s. Sin asistencia el
     *  entrenamiento exigía un golpeo perfecto en seco: «el saque es
     *  imposible». Devuelve true si el saque sigue vivo. */
    function serveAssist() {
      const b = G.ball;
      const rise = (st.tossMaxY || 0) - (st.tossReleaseY || 0);
      if (rise < DIMS.tossMinRise) {
        toast(t('toss_alto'), false);
        serveTee();
        return false;
      }
      if (b.pos.z < C() + HL() - DIMS.serveEndLineTol) {
        toast(t('fuera_linea'), false);
        serveTee();
        return false;
      }
      if (b.vel.length() > SERVE_TUNE.serveMaxSpeed) {
        b.vel.setLength(SERVE_TUNE.serveMaxSpeed);
      }
      const pad = G.controllerPaddles ? G.controllerPaddles[G.paddleHand] : null;
      const tier = (G.serveTier ? G.serveTier() : SERVE_ASSIST_TIERS.medium);
      const res = applyServeProgressiveAssist(b, pad, tier);
      __ppServeTelemetry(res, { src: 'train', mode: active, tier: G.difficulty });
      try { G.haptic(G.paddleHand, 0.8, 90); } catch (e) { /* */ }
      return true;
    }
  
    /* ---------------- puntuación y avisos ---------------- */
    function toast(msg, ok) {
      st.toast = msg; st.toastT = 2.1; st.toastOk = !!ok; panelDirty = true;
    }
    function addPts(n) {
      S.pts += n; st.sessPts += n;
      // desbloqueo de skins
      for (const sk of SKINS) {
        if (S.pts >= sk.min && S.unlocked.indexOf(sk.id) < 0) {
          S.unlocked.push(sk.id);
          toast(t('nuevo_skin', { s: sk.name[LANG] || sk.name.es }), true);
          G.audio.playOsc(880, 1560, 0.16, 'triangle', 0.14, 0.12);
        }
      }
      save(); panelDirty = true;
    }
    function recordBest(mode, val) {
      if (!S.best[mode] || val > S.best[mode]) { S.best[mode] = val; save(); }
    }
    function okHit(key, pts) {
      st.streak++; st.done++;
      st.roundHits++;
      // r76 · EL PULSO CRAZY: valor logrado y marca PREVIA capturados ANTES
      // de cualquier reset del goal (el fantasma se juega con la marca vieja)
      const __dailyRes = (active === 't5a') ? st.rally : st.streak;
      const __dailyOld = S.best[active] || 0;
      // v3.0.7-PLAY1 · COMBO: los puntos del golpe se multiplican por la
      // racha (×2 a partir de 4, ×3 a partir de 8). Con gamify=0 mul es 1
      // y el flujo de puntos es IDÉNTICO al de v3.0.6.
      const mul = comboMul();
      const mulPrev = comboMulN((active === 't5a' ? st.rally : st.streak) - 1);
      addPts(pts * mul);
      checkComboAch(mul);
      checkStreakAch();
      if (mul > mulPrev) {
        toast(t('combo', { n: mul }), true);
        G.audio.playOsc(760 + mul * 160, 1180 + mul * 260, 0.09, 'sine', 0.14, 0);
      } else {
        toast(t(key), true);
        G.audio.playOsc(760, 1180, 0.07, 'sine', 0.13, 0);
      }
      const M = MODES[active];
      const hitGoal = active === 't5a'
        ? RALLY_MILL.t5a.includes(st.rally)   // r61: los hitos ya eran tabla (RALLY_MILL)
        : (st.streak >= objN());
      if (hitGoal) {
        // r61 · FASE 155 · el bonus del hito sale de RALLY_BONUS (la tabla
        // que ya existía junto a RALLY_MILL — adiós al literal duplicado)
        const hi = RALLY_MILL.t5a.indexOf(st.rally);
        const bonus = active === 't5a' ? RALLY_BONUS.t5a[hi] : M.bonus;
        addPts(bonus);
        // r97 · RETO SEMANAL «entrenamiento»: una meta completada cuenta
        try { if (G && G._retosEvento) G._retosEvento('entrenamiento', 1); } catch (eRE) { /* */ }
        if (active === 't5a') recordBest(active, st.rally);
        // v3.0.7-PLAY1 · estrellas + precisión + celebración al completar
        let suffix = '';
        if (GAMF()) {
          if (active === 't5a') {
            const MI5 = RALLY_MILL.t5a;   // r61: umbrales de estrella = la tabla
            const stR = st.rally >= MI5[2] ? 3 : (st.rally >= MI5[1] ? 2 : 1);
            recordStars('t5a', stR);
            if (st.rally >= CONFIG_LOGROS.train.m50.cond.valor) grant('m50');   // r61: dato
            if (st.rally >= CONFIG_LOGROS.train.m100.cond.valor) grant('m100');   // r61: dato
          } else {
            const tries = st.roundHits + st.roundFaults;
            const acc = tries ? Math.round(st.roundHits / tries * 100) : 100;
            const stars = starsFor(st.roundFaults);
            recordStars(active, stars);
            recordAcc(active, acc);
            if (stars === CONFIG_LOGROS.train.p1.cond.valor) grant('p1');   // r61: dato
            suffix = '  ' + '\u2605'.repeat(stars) + '\u2606'.repeat(3 - stars);
          }
          burst({ x: 0, y: TOP() + 0.5, z: C() }, active !== 't5a' && st.roundFaults === 0);
          checkGlobalAch();
        }
        toast(active === 't5a'
          ? t('hito', { n: st.rally, n2: bonus })
          : t('hecho', { n: bonus }) + suffix, true);
        // r76 · EL PULSO CRAZY: ¿era el modo del día y no está cobrado?
        // (después del toast del modo: el aviso del PULSO es el que manda)
        // M4 (r118) · sesión del RETO SEMANAL: el cobro va al plan de la
        // septana (insignia incluida); el diario queda intacto.
        try { if (st.weekly) weeklyComplete(active, __dailyRes, __dailyOld);
          else dailyComplete(active, __dailyRes, __dailyOld); } catch (eD) { /* nunca rompe */ }
        st.streak = 0; st.done = 0;
        if (active !== 't5a') { st.roundHits = 0; st.roundFaults = 0; }
        G.audio.playOsc(660, 990, 0.1, 'triangle', 0.14, 0.0);
        G.audio.playOsc(880, 1320, 0.1, 'triangle', 0.14, 0.11);
        G.audio.playOsc(990, 1760, 0.14, 'triangle', 0.14, 0.22);
        // v3.6.19 (ronda 26) · FIX ZONAS: al rotar el objetivo hay que REPINTAR
        // el quad — antes la zona nueva sólo existía para el juez y el jugador
        // seguía viendo congelada la zona inicial (informe del dueño: «se dan
        // por buenas nuevas áreas sin ver ninguna zona nueva marcada»).
        if (active === 't1a') { st.target = pickTarget(); if (quadMesh) drawQuad(active); }
        if (active === 't5a') { /* el rally continúa: los hitos suman */ }
      }
      if (active !== 't5a') recordBest(active, Math.max(st.streak, S.best[active] || 0));
      st.live = false; st.wait = 0.9; panelDirty = true;
    }
    function failHit(key) {
      st.streak = 0;
      st.roundFaults++;
      if (isRallyM() && st.rally > 0) {
        recordBest(active, st.rally);
        toast(t('fin_rally', { n: st.rally }), false);
      } else toast(t(key || 'mal_fuera'), false);
      st.rally = 0;
      G.audio.playOsc(340, 210, 0.12, 'sawtooth', 0.09, 0);
      st.live = false; st.wait = 1.0; panelDirty = true;
    }
  
    /* ---------------- objetivos y overlay de cada modo ---------------- */
    function pickTarget() {
      // zona dorada: profundas y medias izquierda/derecha (nunca centro)
      const zs = ['deep', 'mid'];
      const z = zs[(Math.random() * zs.length) | 0];
      const x = Math.random() < 0.5 ? -1 : 1;
      return { z, x };
    }
    function drawQuad(mode) {
      const g = quadCtx, W = 512, H = 512;
      g.clearRect(0, 0, W, H);
      const mx = (x) => W / 2 + (x / HW()) * (W / 2);          // x mundo -> lienzo
      const mz = (z) => H * ((C() - z) / HL());                // z mundo -> lienzo (0 = fondo rival)
      if (mode === 't1a') {
        // 6 zonas: profundas/medias/cortas × izq/der + centro prohibido
        // r80 · las dimensiones salen de zonaDims(): lo pintado ES lo
        // juzgado, también con el RETO DIARIO (zonas el doble de anchas)
        const ZD = zonaDims();
        const rows = [[C() - HL(), C() - HL() / 2], [C() - HL() / 2, C() - HL() / 4], [C() - HL() / 4, C()]];
        // v3.0.2 · FIX visibilidad: la parrilla casi no se veía en el casco —
        // trazos más gruesos/opacos y colores saturados.
        g.lineWidth = 5; g.strokeStyle = 'rgba(255,255,255,0.92)';
        for (const r of rows) {
          g.beginPath(); g.moveTo(mx(-HW()), mz(r[0])); g.lineTo(mx(HW()), mz(r[0])); g.stroke();
          g.beginPath(); g.moveTo(mx(-HW()), mz(r[1])); g.lineTo(mx(HW()), mz(r[1])); g.stroke();
        }
        g.beginPath(); g.moveTo(mx(0), 0); g.lineTo(mx(0), H); g.stroke();
        // centro prohibido (rojo translúcido con borde marcado)
        const cx0 = mx(-ZD.t1aCentro), cx1 = mx(ZD.t1aCentro);
        g.fillStyle = 'rgba(230,70,70,0.55)';
        g.fillRect(cx0, 0, cx1 - cx0, H);
        g.strokeStyle = 'rgba(255,110,110,0.95)'; g.lineWidth = 4;
        g.strokeRect(cx0, 2, cx1 - cx0, H - 4);
        g.fillStyle = 'rgba(255,150,150,1)';
        // r80 · EVITA cabe SIEMPRE en la banda (con el reto, la banda es el
        // doble de estrecha): shrink-to-fit honesto, nunca se sale
        {
          const bandW = cx1 - cx0;
          let evS = 26;
          g.font = '700 ' + evS + 'px system-ui, sans-serif'; g.textAlign = 'center';
          while (evS > 11 && g.measureText(t('z_evita')).width > bandW - 6) {
            evS -= 1; g.font = '700 ' + evS + 'px system-ui, sans-serif';
          }
          g.save();
          g.translate(mx(0), H - 26); g.scale(1, -1);
          g.textBaseline = 'middle';
          g.fillText(t('z_evita'), 0, 0);
          g.restore();
        }
        // zona objetivo dorada
        // v3.0.8-TRN1 · ZONA FIEL AL JUEZ: lo pintado ES lo juzgado. Antes la
        // zona dorada cubría toda la mitad (incluida la franja central que
        // zoneOf() rechaza como 'C' EVITA) y el texto OBJETIVO a 64 px se
        // salía del rectángulo (se cortaba). Ahora la zona empieza donde el
        // juez acepta (|x| ≥ 15 cm) y el texto se reescala con measureText
        // para caber SIEMPRE dentro del área concreta.
        if (st.target) {
          // r80 · las filas del objetivo crecen con el reto: 'deep' abarca
          // profunda+media (frontera HL·0,5→HL·0,25) y 'mid' abarca
          // media+corta (HL·0,25→toda la mitad); el centro prohibido se
          // estrecha a la mitad. Pintado y juzgado salen de zonaDims().
          const zr = st.target.z === 'deep'
            ? [C() - HL(), C() - HL() * ZD.t1aDeepF]
            : [C() - HL() / 2, C() - HL() * ZD.t1aMidF];
          const xr = st.target.x < 0 ? [-HW(), -ZD.t1aCentro] : [ZD.t1aCentro, HW()];
          const zx0 = mx(xr[0]), zx1 = mx(xr[1]), zy0 = mz(zr[0]), zy1 = mz(zr[1]);
          g.fillStyle = 'rgba(242,193,78,0.88)';
          g.fillRect(zx0, zy0, zx1 - zx0, zy1 - zy0);
          g.strokeStyle = '#ffd257'; g.lineWidth = 10;
          g.strokeRect(zx0 + 5, zy0 + 5, zx1 - zx0 - 10, zy1 - zy0 - 10);
          g.strokeStyle = 'rgba(60,36,0,0.9)'; g.lineWidth = 3;
          g.strokeRect(zx0 + 12, zy0 + 12, zx1 - zx0 - 24, zy1 - zy0 - 24);
          g.save();
          // v3.6.20 · TEXTO LEGIBLE + i18n: scale(1,-1) en vez de rotate(π)
          // (ver EVITA arriba): el dueño veía «OBJETIVO» en espejo y no legible.
          g.translate((zx0 + zx1) / 2, (zy0 + zy1) / 2);
          g.scale(1, -1);
          const ztW = Math.abs(zx1 - zx0) - 26, ztH = Math.abs(zy1 - zy0) - 18;
          let ztSize = Math.min(58, Math.floor(ztH * 0.62));
          g.font = '900 ' + ztSize + 'px system-ui, sans-serif';
          const ztText = t('z_obj');
          const ztWid = g.measureText(ztText).width;
          if (ztWid > ztW) ztSize = Math.max(20, Math.floor(ztSize * ztW / ztWid));
          g.font = '900 ' + ztSize + 'px system-ui, sans-serif';
          g.textAlign = 'center'; g.textBaseline = 'middle';
          g.lineWidth = 6; g.strokeStyle = 'rgba(40,24,0,0.85)';
          g.strokeText(ztText, 0, 0);
          g.fillStyle = '#1a1408';
          g.fillText(ztText, 0, 0);
          g.textBaseline = 'alphabetic';
          g.restore();
        }
      } else if (mode === 't1b') {
        // bandas: laterales 10 cm + fondo 12 cm (r80 · reto: 20/24 cm)
        // v3.0.6-SRV1 · FIX zona FONDO: el eje Z del lienzo está INVERTIDO
        // respecto a mz() (fila 0 = red, fila H = fondo rival); pintar desde
        // la fila 0 cubría TODA la mesa MENOS la franja objetivo. Con el mismo
        // patrón rect(mz(z0), mz(z1)−mz(z0)) de t4a/t4b la franja cae EXACTA.
        const ZB = zonaDims();
        g.fillStyle = 'rgba(99,179,237,0.8)';
        g.fillRect(0, 0, mx(-HW() + ZB.t1bBanda), H);
        g.fillRect(mx(HW() - ZB.t1bBanda), 0, W - mx(HW() - ZB.t1bBanda), H);
        const zb = [C() - HL(), C() - HL() + ZB.t1bFondo];   // franja de fondo real
        g.fillRect(0, mz(zb[0]), W, mz(zb[1]) - mz(zb[0]));
        g.strokeStyle = '#9fd4ff'; g.lineWidth = 9;
        g.strokeRect(4.5, 4.5, W - 9, H - 9);
        g.fillStyle = '#0c1826'; g.font = '900 40px system-ui, sans-serif'; g.textAlign = 'center';
        g.save(); g.translate(W / 2, (mz(zb[0]) + mz(zb[1])) / 2); g.scale(1, -1); g.textBaseline = 'middle'; g.fillText(t('z_fondo'), 0, 0); g.restore();
      } else if (mode === 't1c') {
        /* M7d (r120) · ESQUINA EXACTA — los DOS cuadros dorados: la ESQUINA
         * es la INTERSECCIÓN del fondo (dz > HL·0,5, la fila lejana) con la
         * banda lateral (mismo ancho que juzga t1b). Geometría calcada del
         * juez t1c: lo pintado ES lo juzgado. */
        const ZC = zonaDims();
        const zr = [C() - HL(), C() - HL() * 0.5];
        const y0 = mz(zr[0]), y1 = mz(zr[1]);
        const corners = [
          [0, mx(-HW() + ZC.t1bBanda)],
          [mx(HW() - ZC.t1bBanda), W],
        ];
        for (const [cx0, cx1] of corners) {
          g.fillStyle = 'rgba(242,193,78,0.88)';
          g.fillRect(cx0, y0, cx1 - cx0, y1 - y0);
          g.strokeStyle = '#ffd257'; g.lineWidth = 10;
          g.strokeRect(cx0 + 5, y0 + 5, cx1 - cx0 - 10, y1 - y0 - 10);
          g.strokeStyle = 'rgba(60,36,0,0.9)'; g.lineWidth = 3;
          g.strokeRect(cx0 + 12, y0 + 12, cx1 - cx0 - 24, y1 - y0 - 24);
        }
        // el resto de la mesa se apaga (el objetivo NO es la mesa entera)
        g.fillStyle = 'rgba(10,14,22,0.42)';
        g.fillRect(0, 0, W, y0);                     // mitad cercana: fuera
        g.fillRect(corners[0][1], y0, corners[1][0] - corners[0][1], y1 - y0);  // centro profundo: fuera
        g.fillRect(0, y1, W, H - y1);                // banda media/corta: fuera
      } else if (mode === 't4a') {
        // zona de doble bote junto a la red (lado rival) — r80 · reto: el
        // DOBLE de profunda (0,51 m → 1,02 m desde la red)
        const Z4 = zonaDims();
        const zr = [C() - Z4.t4aProf, C() - 0.05];
        g.fillStyle = 'rgba(246,173,85,0.82)';
        g.fillRect(0, mz(zr[0]), W, mz(zr[1]) - mz(zr[0]));
        g.strokeStyle = '#ffc178'; g.lineWidth = 10;
        g.strokeRect(5, mz(zr[0]) + 5, W - 10, mz(zr[1]) - mz(zr[0]) - 10);
        g.fillStyle = '#241206'; g.font = '900 40px system-ui, sans-serif'; g.textAlign = 'center';
        g.save(); g.translate(W / 2, (mz(zr[0]) + mz(zr[1])) / 2); g.scale(1, -1); g.textBaseline = 'middle';
        g.fillText(t('z_doble'), 0, 0); g.restore();
      } else if (mode === 't4b') {
        // franja de fondo: últimos 15 cm (r80 · reto: 30 cm)
        const Z5 = zonaDims();
        const zr = [C() - HL(), C() - HL() + Z5.t4bFondo];
        g.fillStyle = 'rgba(246,173,85,0.85)';
        g.fillRect(0, mz(zr[0]), W, mz(zr[1]) - mz(zr[0]));
        g.strokeStyle = '#ffc178'; g.lineWidth = 10;
        g.strokeRect(5, mz(zr[0]) + 5, W - 10, mz(zr[1]) - mz(zr[0]) - 10);
        g.fillStyle = '#241206'; g.font = '900 30px system-ui, sans-serif'; g.textAlign = 'center';
        g.save(); g.translate(W / 2, (mz(zr[0]) + mz(zr[1])) / 2); g.scale(1, -1); g.textBaseline = 'middle';
        g.fillText(t('z_f15'), 0, 0); g.restore();
      }
      quadTex.needsUpdate = true;
    }
  
    function applyModeScene() {
      quadMesh.visible = (active === 't1a' || active === 't1b' || active === 't1c' || active === 't4a' || active === 't4b');
      ribbonG.visible = (active === 't2a');
      apexG.visible = (active === 't2b');
      metroG.visible = (active === 't5a' || active === 't5b');
      panel.visible = !!active;
      if (quadMesh.visible) drawQuad(active);
      // r100 · al (re)entrar en el PASE BAJO el rótulo repinta cm + idioma
      if (ribbonG.visible && barraLbl) {
        barraLbl.material.map = barraLabelTex();
        barraLbl.material.needsUpdate = true;
        // r102 · AVISO AL JUGADOR (petición del dueño: «debemos informar de
        // este control de altura al jugador»): una vez por sesión, al entrar
        // por primera vez en el PASE BAJO
        if (!barraAvisoHecho) {
          barraAvisoHecho = true;
          toast((LANG === 'en'
            ? 'Bar: ' + BARRA_CM() + ' cm · adjust with EITHER STICK ↑↓ (or hand at the ribbon)'
            : 'Barra: ' + BARRA_CM() + ' cm · ajústala con CUALQUIER JOYSTICK ↑↓ (o la mano en la cinta)'), true);
        }
      }
    }
  
  
    /* =================================================================
     *  TICK · se llama cada frame desde el bucle del núcleo
     *  (siempre: actualiza cosmética global; entrena sólo si hay modo)
     *  ================================================================= */
    function modeFeed() {
      // alimentación específica por modo (máquina o soporte de saque)
      if (active === 't1a' || active === 't1b' || active === 't1c' || active === 't2a' || active === 't2b' || active === 't5a') {
        // v3.0.8-TRN1 · MÁQUINA DE SPARRING: bolas de rally directas y
        // profundas (tiro resuelto con Magnus, despeje de red garantizado)
        // en vez de saques del solver que a veces caían lentos y cortos. La
        // dificultad de cada modo sigue viviendo en lo que devuelve EL JUGADOR.
        feedToPlayer({ rally: true, max: active === 't5a' ? 7.2 : 7.8 });
        st.phase = 'rally';
        if (active === 't5a') st.live = true;   // el beat vigila el fallo aunque el jugador no la toque
      } else if (active === 't5b') {
        /* M7d (r120) · METRÓNOMO LOCO: la MISMA máquina, pero cada bola
         * llega a una velocidad distinta (5,6–9,2): leer el ritmo YA no
         * basta. El beat vigila el fallo igual que en t5a. */
        feedToPlayer({ rally: true, max: 5.6 + Math.random() * 3.6 });
        st.phase = 'rally';
        st.live = true;
      } else if (active === 't3a') {
        const spin = new THREE.Vector3(-(58 + Math.random() * 22), (Math.random() - 0.5) * 10, 0);
        feedToPlayer({
          spin, target: new THREE.Vector3((Math.random() * 2 - 1) * 0.22, 0, C() + HL() * 0.62),
          tIn: 0.6, max: 7.5,
        });
        st.phase = 'rally';
      } else if (active === 't3b') {
        const spin = new THREE.Vector3(62 + Math.random() * 26, (Math.random() - 0.5) * 8, 0);
        feedToPlayer({
          spin, target: new THREE.Vector3((Math.random() * 2 - 1) * 0.24, 0, C() + HL() * (0.5 + Math.random() * 0.3)),
          tIn: 0.52 + Math.random() * 0.18, max: 9.5,
        });
        st.phase = 'rally';
      } else if (active === 't4a' || active === 't4b') {
        serveTee();
      }
    }
  
    function zoneOf(p) {
      // clasifica un bote del lado rival: 'deep'|'mid'|'short' × 'L'|'R'|'C'
      // (r80 · el juez t1a usa zonaDims() — esta clasificación queda como
      // referencia documental de las fronteras de siempre)
      const dz = C() - p.z;
      const row = dz > HL() * 0.5 ? 'deep' : dz > HL() * 0.25 ? 'mid' : 'short';
      const col = p.x < -0.15 ? 'L' : p.x > 0.15 ? 'R' : 'C';
      return { row, col };
    }
  
    function judgeAiBounce(p) {
      // p = posición del bote en el campo rival (primer bote tras el golpe)
      if (active === 't1a') {
        // r80 · el JUEZ comparte zonaDims() con el pintor: con el RETO
        // DIARIO las filas crecen (deep → profunda+media · mid → media+corta)
        // y el centro prohibido se estrecha a la mitad. Sin reto, la
        // decisión es EXACTAMENTE la de zoneOf() de siempre (fronteras
        // incluidas: en ±centro cuenta como centro).
        const ZJ = zonaDims();
        const dz1 = C() - p.z;
        const colC = p.x >= -ZJ.t1aCentro && p.x <= ZJ.t1aCentro;
        const colOk = st.target && ((st.target.x < 0 && p.x < -ZJ.t1aCentro)
          || (st.target.x > 0 && p.x > ZJ.t1aCentro));
        const rowOk = (st.target && st.target.z === 'deep')
          ? (dz1 > HL() * ZJ.t1aDeepF)
          : (dz1 > HL() * ZJ.t1aMidF && dz1 <= HL() * 0.5);
        if (st.target && rowOk && colOk) {
          okHit(MODES[active].ok, MODES[active].pts);
        } else if (colC) {
          st.done = 0; failHit('mal_corta');
        } else {
          st.done = 0; failHit('mal_fuera');
        }
      } else if (active === 't1b') {
        const ZJ1 = zonaDims();
        const band = Math.abs(p.x) > HW() - ZJ1.t1bBanda || p.z < C() - HL() + ZJ1.t1bFondo;
        if (band) okHit(MODES[active].ok, MODES[active].pts);
        else { st.done = 0; failHit('mal_corta'); }
      } else if (active === 't1c') {
        /* M7d (r120) · ESQUINA EXACTA: fondo Y banda A LA VEZ (los dos
         * cuadros dorados del overlay). Mismo lenguaje de zonas que t1b
         * (ZJ.t1bBanda) y la frontera profunda de t1a (HL·0,5): lo pintado
         * ES lo juzgado. */
        const ZJ2 = zonaDims();
        const deep = (C() - p.z) > HL() * 0.5;
        const band = Math.abs(p.x) > HW() - ZJ2.t1bBanda;
        if (deep && band) okHit(MODES[active].ok, MODES[active].pts);
        else { st.done = 0; failHit('mal_corta'); }
      } else if (active === 't2a') {
        const deep = p.z < C() - 0.60;
        const under = st.cross && st.cross.y < RIBBON_Y();
        if (under && deep) okHit(MODES[active].ok, MODES[active].pts);
        else if (!under) { st.done = 0; failHit('mal_alto'); }
        else { st.done = 0; failHit('mal_corta'); }
      } else if (active === 't2b') {
        const deep = p.z < C() - 0.65;
        if (st.apex >= APEX_Y && deep) okHit(MODES[active].ok, MODES[active].pts);
        else if (st.apex < APEX_Y) { st.done = 0; failHit('mal_alto'); }
        else { st.done = 0; failHit('mal_corta'); }
      } else if (active === 't3a') {
        const low = st.cross && st.cross.y < CROSS_LOW();
        const popped = st.cross && st.cross.y > CROSS_HI();
        if (popped) { st.done = 0; failHit('mal_alto'); }
        else if (low) okHit(MODES[active].ok, MODES[active].pts);
        else { st.done = 0; failHit('mal_alto'); }
      } else if (active === 't3b') {
        okHit(MODES[active].ok, MODES[active].pts);       // bote rival = bloqueo válido
      } else if (active === 't4a') {
        // v3.0.2 · el juez verifica la zona pintada (51 cm junto a la red).
        // v3.0.6-SRV1 · SOLO el PRIMER bote rival debe caer en la zona (saque
        // corto); el SEGUNDO basta con que bote en el campo rival: exigir los
        // DOS dentro de 51 cm era casi imposible (el 2.º bote de un saque
        // corto real siempre cae más hondo que el 1.º).
        // r80 · reto diario: vano 0,51 m → 1,02 m (mismo zonaDims que pinta).
        const ZJ4 = zonaDims();
        const inZone = Math.abs(p.x) < HW() && p.z > C() - ZJ4.t4aProf && p.z < C() - 0.05;
        if (st.aiBounce === 0) {
          if (!inZone) { st.done = 0; failHit('mal_larga'); }
          else { st.aiBounce = 1; st.live = true; }          // espera el 2.º bote
        } else {
          okHit(MODES[active].ok, MODES[active].pts);        // doble bote ✓
        }
      } else if (active === 't4b') {
        const ZJ5 = zonaDims();
        const deep = p.z < C() - HL() + ZJ5.t4bFondo;
        if (deep) {
          if (st.cross && st.cross.spd > 4.5) addPts(1);   // bonus saque tenso
          okHit(MODES[active].ok, MODES[active].pts);
        } else { st.done = 0; failHit('mal_corta'); }        // v3.0.2: era 'mal_larga' (semántica invertida)
      } else if (active === 't5a' || active === 't5b') {
        // v3.0.2 · FIX metrónomo: el rally NUNCA se incrementaba (el juez no
        // tenía rama t5a) — el contador quedaba en 0 y no sumaba puntos.
        // aiTouched cierra el cómputo: los rebotes EXTRA de la misma bola no suman.
        // M7d (r120) · la rama sirve a t5a y a t5b (METRÓNOMO LOCO) con
        // hitos propios por modo (RALLY_MILL / RALLY_BONUS).
        if (!st.aiTouched) {
          st.aiTouched = true;
          st.rally++;
          addPts(MODES[active].pts);
          G.audio.playOsc(760, 1180, 0.07, 'sine', 0.13, 0);
          /* M7d (r120) · logros de racha por el CAMINO VIVO (idempotentes):
           * m50/m100 vivían sólo en okHit y el juez del rally jamás lo
           * llama (muerto desde la refactorización v3.0.2). */
          if (st.rally >= 50) grant('m50');
          if (st.rally >= 100) grant('m100');
          const MI = RALLY_MILL[active], MO = RALLY_BONUS[active];
          const mi = MI.indexOf(st.rally);
          if (mi >= 0) {
            const bonus = MO[mi];
            addPts(bonus);
            recordBest(active, st.rally);
            toast(t('hito', { n: st.rally, n2: bonus }), true);
            G.audio.playOsc(660, 990, 0.1, 'triangle', 0.14, 0);
            G.audio.playOsc(880, 1320, 0.1, 'triangle', 0.14, 0.11);
            G.audio.playOsc(990, 1760, 0.14, 'triangle', 0.14, 0.22);
            /* M7d (r120) · RE-ANCLADO EN EL CAMINO VIVO: estrellas y logros
             * globales del rally (antes en el okHit muerto): las medallas
             * del metrónomo ya nacen con estrella que las sustenta. */
            if (GAMF()) {
              recordStars(active, mi + 1);
              checkGlobalAch();
            }
            // r122 · EL PULSO (reto diario) y el RETO SEMANAL también en el
            // CAMINO VIVO: antes sólo vivían en el hitGoal del okHit muerto
            // (desde v3.0.2) — un día con plan t5a/t5b no podía cobrar el
            // PULSO ni la insignia semanal. Mismo patrón idempotente del
            // bloque vivo r120 (grant/record ya guardan por sí mismos).
            try { if (G && G._retosEvento) G._retosEvento('entrenamiento', 1); } catch (eRE) { /* */ }
            try { if (st.weekly) weeklyComplete(active, st.rally, S.best[active] || 0);
              else dailyComplete(active, st.rally, S.best[active] || 0); } catch (eD) { /* nunca rompe */ }
          }
          panelDirty = true;    // el rally sigue: el beat sustituirá la bola cuando la anterior repose
        }
      }
    }
  
    /** muestreo del cruce de red (entre el frame previo y el actual) */
    let prevBallZ = null;
    function sampleCross() {
      const b = G.ball;
      if (prevBallZ === null) { prevBallZ = b.pos.z; return; }
      const z0 = prevBallZ, z1 = b.pos.z, nz = C();
      if ((z0 - nz) * (z1 - nz) < 0) {
        if (st.live && b.vel.z < 0) {
          st.cross = { y: b.pos.y, spd: Math.abs(b.vel.z) };
        }
      }
      prevBallZ = b.pos.z;
    }
  
    function ballDead() {
      const b = G.ball;
      const restFloor = b.pos.y < DIMS.ballRadius + 0.04 && Math.abs(b.vel.y) < 0.6;
      const onTable = Math.abs(b.pos.x) < HW() + 0.05 &&
        Math.abs(b.pos.z - C()) < HL() + 0.05;
      const restTable = onTable && b.pos.y < TOP() + 0.06 && b.vel.length() < 0.45;
      const gone = Math.abs(b.pos.z - C()) > HL() + 1.5 || b.pos.y < -0.4;
      return restFloor || restTable || gone;
    }
  
    function trainTick(dt) {
      // 1) eventos del frame
      const evs = G.events || [];
      for (const ev of evs) {
        if (ev.type === 'paddle' && ev.who === 'player') {
          // v3.0.8-TRN1 · en fase 'tee' la bola está EN LA MANO LIBRE: un roce
          // de la pala no es un golpeo (se ignora). Y en los primeros mm del
          // lanzamiento tampoco (misma inmunidad que el núcleo: manos juntas).
          if (st.phase === 'tee') continue;
          if (st.phase === 'toss' &&
              (st.tossMaxY - st.tossReleaseY) < DIMS.tossMinRise) continue;
          st.hitPos = ev.pos ? ev.pos.clone() : null;
          // v3.0.6-SRV1 · 'toss' se añade: el golpe válido llega con la bola EN
          // EL AIRE (soporte → lanzamiento → golpeo, como el saque real).
          if (st.phase === 'toss') {
            drillReach(false);          // margen ampliado SOLO durante el vuelo
            // v3.0.8-TRN1 · asistencia del saque idéntica a la de PARTIDO
            // (validación de lanzamiento + cascada 45 % → 75 % → solver con
            // hint del swing). Si el lanzamiento no vale, vuelta al soporte.
            if (!serveAssist()) continue;
            st.phase = 'serve';
          }
          st.live = true; st.apex = G.ball.pos.y; st.aiBounce = 0;
          st.aiTouched = false;
          st.cross = null; st.deadT = 0; st.shotRec = true; st.shotPts.length = 0;
        } else if (ev.type === 'table') {
          if (ev.side === 'ai') {
            spawnMark(ev.pos, st.live ? 0xffe08a : 0x9fb3c8);
            // v3.0.2 · gate con shotRec: el bote PROPIO del saque de la máquina
            // (metrónomo con live=true desde el feed) no debe juzgarse como
            // devolución del jugador.
            if (st.live && st.shotRec) {
              st.bouncePos = ev.pos;
              judgeAiBounce(ev.pos.clone());
            }
          } else if (ev.side === 'player' && st.live) {
            spawnMark(ev.pos, 0x9fb3c8);
          }
        } else if (ev.type === 'net' && st.live) {
          spawnMark(ev.pos, 0xfc8181);
          failHit('mal_red');
        }
      }
      // 2) física viva del modo
      const b = G.ball;
      if (st.live) {
        if (b.pos.y > st.apex) st.apex = b.pos.y;
        if (st.shotRec && st.shotPts.length < 96) st.shotPts.push(b.pos.clone());
        if (ballDead()) {
          st.deadT += dt;
          // v3.0.2 · guard shotRec (cierra el juicio una sola vez) y caso t5a:
          // con bote rival YA puntuado la bola muere sola SIN fallo; sin bote
          // rival el jugador no la devolvió (el beat también lo detecta).
          if (st.deadT > 0.55 && st.shotRec) {
            if (isRallyM()) {
              if (st.aiTouched) st.shotRec = false;
              else { failHit('mal_fuera'); st.shotRec = false; }
            } else if (active === 't4a' && st.aiBounce === 1) { st.done = 0; failHit('mal_larga'); st.shotRec = false; }
            else if (st.live) { failHit('mal_fuera'); st.shotRec = false; }
          }
        } else st.deadT = 0;
      }
      sampleCross();
      // 3) SAQUE (t4a/t4b) · ciclo COMPLETO en el módulo: soporte →
      // lanzamiento → golpeo en el aire → punto → nuevo soporte. El paso 4 NO
      // alimenta t4 (antes el feed temporizada ROBABA la bola en pleno vuelo,
      // la misma clase de bug que el metrónomo sufría en v3.0.2).
      if (active === 't4a' || active === 't4b') {
        if (st.phase === 'tee') {
          // v3.0.8-TRN1 · bola EN LA MANO LIBRE (cinemática pura, como el
          // núcleo en partido): sigue a la mano frame a frame y espera el
          // gesto del jugador (soltar grip o gatillo). NUNCA se lanza sola:
          // el auto-toss de 1,1 s robaba el control y rompía la sensación.
          b.vel.set(0, 0, 0);
          b.spin.set(0, 0, 0);
          const bh = G.controllerPaddles && G.controllerPaddles[G.ballHand];
          if (bh && bh.active) {
            b.pos.copy(bh.pos);
            b.pos.y += BALL_HAND_LIFT;
          } else {
            b.pos.set(0.30, 1.05, C() + HL() + 0.35);
          }
          st.tossReleaseY = b.pos.y; st.tossMaxY = b.pos.y;
          st.teeT += dt;
        } else if (st.phase === 'toss') {
          // vuelo del lanzamiento: margen de golpeo ampliado (el núcleo lo
          // repone a 0 cada frame en calib; aquí se vuelve a activar)
          drillReach(true);
          st.tossT += dt;
          if (b.pos.y > st.tossMaxY) st.tossMaxY = b.pos.y;
          const fellBack = b.vel.y < 0 && b.pos.y < 1.02;
          if (st.tossT > 4 || fellBack || ballDead()) {
            drillReach(false);
            serveTee();                            // reintentar desde el soporte
          }
        } else if (!st.live) {
          // punto cerrado (el juez ya puntuó o falló) → nuevo soporte
          st.wait -= dt;
          if (st.wait <= 0) serveTee();
        }
      }
      // 4) alimentación temporizada (t4a/t4b la lleva el soporte del paso 3)
      if (!st.live && !(active === 't4a' || active === 't4b')) {
        st.wait -= dt;
        if (st.wait <= 0) { modeFeed(); st.wait = isRallyM() ? BEAT_INT() : 2.2; }
      } else if (isRallyM()) {
        // v3.0.2 · FIX «la bola desaparece»: el beat ya NO roba la bola en
        // vuelo. Sólo sustituye cuando la anterior está ASENTADA (muerta, ya
        // botó en el campo rival o pasó de largo). Si el beat vence y el
        // jugador no la devolvió, el rally termina ANTES de alimentar.
        // M7d (r120) · BEAT_INT: el LOCO late más rápido (1,45 s).
        st.feedT += dt;
        const settled = !st.live || st.aiTouched || ballDead() || b.pos.z > C() + HL() + 0.4;
        if (st.feedT >= BEAT_INT() && settled) {
          if (st.live && !st.aiTouched) failHit('mal_fuera');
          st.feedT = 0; modeFeed();
        }
      }
      // 5) metrónomo visual
      if (isRallyM()) {
        st.beat += dt;
        const ph = (st.beat % BEAT_INT()) / BEAT_INT();
        const s = 1 + 0.5 * Math.max(0, 1 - ph * 4);
        metroG.scale.set(s, s, 1);
        metroG.material.opacity = 0.35 + 0.55 * Math.max(0, 1 - ph * 3);
      }
      // 6) línea de tiro
      if (st.live && S.fb.line && st.shotPts.length > 1) shotLineShow();
    }
  
    /* ---------------- cosméticos globales (todo modos) ---------------- */
    function cosmeticsTick(dt) {
      // flecha de efecto sobre la bola (también en campeonatos: sólo avisa)
      if (!spinSprite) return;
      const b = G.ball;
      let show = false;
      if (S.fb.spin && b && b.vel && b.vel.lengthSq() > 1.2 && b.spin && b.spin.lengthSq() > 320) {
        const lift = b.spin.z * b.vel.x - b.spin.x * b.vel.z;   // (spin×vel).y
        const force = Math.min(1, Math.abs(lift) / 9);
        const side = Math.abs(b.spin.y) / 18;
        if (force > 0.12 || side > 0.5) {
          show = true;
          spinSprite.position.set(b.pos.x, b.pos.y + 0.1, b.pos.z);
          const col = lift < -0.8 ? 0xff9a4a : lift > 0.8 ? 0x4ab8ff : 0xc07aff;
          spinSprite.material.color.setHex(col);
          spinSprite.material.rotation += dt * (lift < 0 ? 6 : -6);
        }
      }
      spinSprite.material.opacity += ((show ? 0.9 : 0) - spinSprite.material.opacity) * Math.min(1, dt * 9);
      if (!show && spinSprite.material.opacity < 0.05) spinSprite.visible = false;
      else spinSprite.visible = true;
      // marcas: desvanecer
      for (const m of marks) {
        if (!m.visible) continue;
        m.userData.ttl -= dt;
        if (m.userData.ttl <= 0) { m.visible = false; continue; }
        m.material.opacity = Math.min(0.95, m.userData.ttl);
      }
      // línea de tiro: desvanecer
      if (shotTtl > 0) {
        shotTtl -= dt;
        shotLine.material.opacity = Math.max(0, Math.min(0.85, shotTtl * 0.5));
        if (shotTtl <= 0) shotLine.visible = false;
      }
      // skin arcoíris (v3.0.3: matiz animado SÓLO sobre los materiales
      // marcados ppAnim — la textura holográfica se tiñe, el resto fijo)
      if (S.skin === 'arcoiris' && skinMats.length) {
        rainbowT += dt * 0.6;
        // r74 · SIN asignación por frame: el color de módulo se recicla
        // (antes un THREE.Color nuevo cada frame con la piel arcoíris puesta).
        if (!rainbowCol) rainbowCol = new THREE.Color();
        rainbowCol.setHSL(rainbowT % 1, 0.75, 0.55);
        for (const m of skinMats) if (m.userData && m.userData.ppAnim) m.color.copy(rainbowCol);
      }
      // iconos de efecto en la pala
      if (st.spinIconT > 0) {
        st.spinIconT -= dt;
        const op = Math.max(0, Math.min(1, st.spinIconT / 0.5));
        for (const s of faceIcons) s.material.opacity = op;
        if (st.spinIconT <= 0) for (const s of faceIcons) s.visible = false;
      }
      // panel
      if (panelDirty && panel) { drawPanel(); panelDirty = false; }
      if (st.toastT > 0) {
        st.toastT -= dt;
        if (st.toastT <= 0) panelDirty = true;
      }
    }
  
  
    /* =================================================================
     *  CICLO DE VIDA DE LOS MODOS
     *  ================================================================= */
    function startMode(game, id, opts) {
      if (!game) return;
      if (!MODES[id]) return;
      G = game;
      buildScene();
      LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
      active = id;
      const M = MODES[id];
      // r80 · EL RETO PERMISIVO: arrancado desde el RETO DIARIO, las zonas
      // de bote se pintan y se juzgan el DOBLE de anchas (zonaDims) —
      // «para no desanimar al jugador; la dificultad irá subiendo con el
      // tiempo» (petición del dueño).
      st.daily = (opts && opts.daily) ? 1 : 0;
      st.weekly = (opts && opts.weekly) ? 1 : 0;   // M4 (r118) · sesiones del reto semanal
      if (!game.calib) game.enterCalib();      // aísla: sin árbitro, sin IA, sin marcador
      game.palaRecoger && game.palaRecoger();  // r83 · si el AJUSTE DE PALA estaba vivo, sus elementos se recogen
      game.exitHall();                          // v3.1.0-SRV2: un modo se juea en la cancha
      game.trainV3 = id;                        // el núcleo desactiva su rutina de calib
      game.trainV3Hub = true;                   // v3.0.3 · salida con Y → hub de entrenamiento
      game.calibPanel.group.visible = false;    // el panel de agarre fuera en los modos
      st.streak = 0; st.done = 0; st.sessPts = 0; st.rally = 0;
      st.roundHits = 0; st.roundFaults = 0;   // v3.0.7-PLAY1 · ronda limpia
      if (burstPts) burstPts.visible = false; // sin celebración de la sesión anterior
      // v3.0.2 · reset COMPLETO de la sesión (antes live/phase/aiTouched
      // quedaban sucios del modo anterior y el modo nuevo arrancaba mal):
      st.live = false; st.phase = 'feed'; st.aiTouched = false;
      st.deadT = 0; st.cross = null; st.apex = 0; st.shotRec = false; st.aiBounce = 0;
      st.target = pickTarget(); st.wait = 0.9; st.feedT = 0; st.toast = ''; st.toastT = 0;
      grp.visible = true;
      applyModeScene();
      panelDirty = true;
      game.audio.playOsc(720, 1080, 0.09, 'triangle', 0.13, 0);
      if (game.rules) game.rules.message = '';
    }
    /** v3.0.3 · Recoge la escena del entrenamiento SIN tocar el modo del
     *  juego (idempotente). La usa stopMode y el NÚCLEO (closeTrainingV3)
     *  para la estanqueidad total de los módulos. */
    function teardown(game) {
      active = null;
      st.daily = 0;         // r80 · fuera de sesión: zonas de entrenamiento normales
      st.weekly = 0;        // M4 (r118) · fuera de sesión: sin bandera semanal
      drillReach(false);   // v3.0.6-SRV1 · margen de saque fuera al recoger
      if (grp) grp.visible = false;
      applyModeScene();
      const g = game || G;
      if (g) { g.trainV3 = null; g.trainV3Hub = false; }
    }
    function stopMode(game) {
      const g = game || G;
      teardown(g);
      if (g && g.calib) g.exitCalib();          // vuelve al modo previo (match/survival)
      if (g && g.audio) g.audio.playOsc(900, 560, 0.1, 'sine', 0.1, 0);
    }
    /** r83 · startCalib: el AJUSTE DE PALA en modo puro (vive en AJUSTES). */
    /** r83 · El ajuste de la pala ya NO es un subapartado del PRO TRAINING
     *  («ahí no tiene sentido»): vive en AJUSTES › PALA. startCalib sigue
     *  siendo el camino (el menú lo llama con cmd 'palaGo') y ahora entra
     *  en el modo PURO (enterCalib(true): passthrough inmediato + ejes +
     *  panel frontal). Sin trainV3Hub: B abre el MENÚ COMÚN, no el hub. */
    function startCalib(game) {
      G = game;
      active = null;
      if (grp) { grp.visible = false; applyModeScene(); }
      if (game.trainV3) game.trainV3 = null;
      game.exitHall();                        // v3.1.0-SRV2: el ajuste vive en la cancha
      game.enterCalib(true);                  // r83 · ajuste PURO (passthrough + ejes)
    }
  
    /* =================================================================
     *  SKINS DE LA PALA + ICONOS DE EFECTO EN AMBAS CARAS (global)
     *  ================================================================= */
    let skinMats = [], faceIcons = [];
    /* V3.0.1 · Geometría REAL del GLB medida en espacio de montura
     * (scripts/mide_pala_v3.py): la hoja NO está centrada en el eje de la
     * montura (centro x +0.0182, y 0.1202, caras a z ±0.0047) y el mango
     * corre por x -0.033. Colocar aro/cinta/iconos en (0, y, 0) los dejaba
     * flotando AL LADO de la pala (el "cilindro marrón" que veía el dueño
     * era la cinta de agarre fuera del mango). */
    const TRN = {
      bladeX: 0.0182, bladeY: 0.1202,  // centro visual de la hoja (GLB)
      bladeZ: 0.0072,                  // caras ±0.0047 + holgura 2.5 mm
      ringR: 0.0845,                   // abraza el borde de la hoja (semialto 0.0854)
      gripX: -0.033, gripY: 0.0, gripZ: 0.0,  // mango real en la zona de agarre
    };
    // pala procedural de respaldo (sin GLB): geometría distinta
    const TRN_FB = {
      bladeX: 0, bladeY: 0.14, bladeZ: 0.0095, ringR: 0.0835,
      gripX: 0, gripY: 0.02, gripZ: -0.055,
    };
    function clearNamed(mount, name) {
      const dead = [];
      mount.traverse((o) => { if (o.userData && o.userData.ppTrainTag === name) dead.push(o); });
      for (const d of dead) if (d.parent) d.parent.remove(d);
    }

    /* ---------------- fábrica de TEXTURAS de las skins ----------------
     * v3.0.3 · Goma con PIPS de verdad (relieve pintado con luz propia),
     * fibra de carbono, oro cepillado y holográfica — canvas 512² que se
     * aplican como map de los materiales REALES del GLB. */
    const SKIN_TEX = {};   // id -> { map, cv }
    function buildPipTexture(o) {
      const S = 512;
      const cv = document.createElement('canvas'); cv.width = S; cv.height = S;
      const g = cv.getContext('2d');
      g.fillStyle = o.base; g.fillRect(0, 0, S, S);
      for (let i = 0; i < 900; i++) {   // micro-ruido de goma
        g.fillStyle = 'rgba(255,255,255,' + (Math.random() * 0.045).toFixed(3) + ')';
        g.fillRect(Math.random() * S, Math.random() * S, 2, 2);
      }
      const step = 26, r = 9;
      for (let row = 0, y = step / 2; y < S + step; y += step, row++) {
        for (let x = step / 2 + (row % 2 ? step / 2 : 0); x < S + step; x += step) {
          const gr = g.createRadialGradient(x - 3, y - 3, 1.5, x, y, r);
          gr.addColorStop(0, o.hi); gr.addColorStop(0.72, o.base); gr.addColorStop(1, o.lo);
          g.fillStyle = gr;
          g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
          if (o.glow) {   // brillo perimetral (brasas)
            g.strokeStyle = o.glowColor; g.globalAlpha = 0.55; g.lineWidth = 1.6;
            g.beginPath(); g.arc(x, y, r + 0.9, 0, Math.PI * 2); g.stroke();
            g.globalAlpha = 1;
          }
        }
      }
      return cv;
    }
    function buildFrostTexture() {
      const S = 512;
      const cv = document.createElement('canvas'); cv.width = S; cv.height = S;
      const g = cv.getContext('2d');
      g.fillStyle = '#bfe6f4'; g.fillRect(0, 0, S, S);
      const step = 26, r = 9;
      for (let row = 0, y = step / 2; y < S + step; y += step, row++) {
        for (let x = step / 2 + (row % 2 ? step / 2 : 0); x < S + step; x += step) {
          const p = g.createRadialGradient(x - 3, y - 3, 1.5, x, y, r);
          p.addColorStop(0, '#ffffff'); p.addColorStop(0.7, '#9fd4ea'); p.addColorStop(1, '#4f93b4');
          g.fillStyle = p;
          g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
        }
      }
      g.strokeStyle = 'rgba(255,255,255,0.5)'; g.lineWidth = 1.4;
      for (let i = 0; i < 46; i++) {   // cristales de escarcha
        const x = Math.random() * S, y = Math.random() * S, l2 = 8 + Math.random() * 18;
        const a = Math.random() * Math.PI;
        g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l2, y + Math.sin(a) * l2); g.stroke();
      }
      return cv;
    }
    function buildGoldTexture() {
      const S = 512;
      const cv = document.createElement('canvas'); cv.width = S; cv.height = S;
      const g = cv.getContext('2d');
      const gr = g.createLinearGradient(0, 0, S, S);
      gr.addColorStop(0, '#f6d879'); gr.addColorStop(0.45, '#c9992e');
      gr.addColorStop(0.55, '#f2c14e'); gr.addColorStop(1, '#8a6417');
      g.fillStyle = gr; g.fillRect(0, 0, S, S);
      for (let y = 0; y < S; y += 3) {   // cepillado
        g.fillStyle = 'rgba(255,255,255,' + (Math.random() * 0.08).toFixed(3) + ')';
        g.fillRect(0, y, S, 1);
      }
      const step = 26, r = 9;
      for (let row = 0, y = step / 2; y < S + step; y += step, row++) {
        for (let x = step / 2 + (row % 2 ? step / 2 : 0); x < S + step; x += step) {
          g.strokeStyle = 'rgba(60,40,5,0.35)'; g.lineWidth = 2;   // pips grabados
          g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.stroke();
          g.strokeStyle = 'rgba(255,240,190,0.30)'; g.lineWidth = 1.2;
          g.beginPath(); g.arc(x - 1, y - 1, r, 0, Math.PI * 2); g.stroke();
        }
      }
      return cv;
    }
    function buildHoloTexture() {
      const S = 512;
      const cv = document.createElement('canvas'); cv.width = S; cv.height = S;
      const g = cv.getContext('2d');
      const gr = g.createLinearGradient(0, 0, S, S);
      ['#ff6ec7', '#ffd86e', '#6effa8', '#6ec7ff', '#b06eff', '#ff6e6e'].forEach((c2, i, a) => gr.addColorStop(i / (a.length - 1), c2));
      g.fillStyle = gr; g.fillRect(0, 0, S, S);
      g.globalAlpha = 0.16; g.fillStyle = '#ffffff';   // bandas perladas
      for (let x = -S; x < S * 2; x += 64) {
        g.save(); g.translate(x, 0); g.rotate(Math.PI / 5); g.fillRect(0, -S, 22, S * 3); g.restore();
      }
      g.globalAlpha = 1;
      const step = 26, r = 9;
      for (let row = 0, y = step / 2; y < S + step; y += step, row++) {
        for (let x = step / 2 + (row % 2 ? step / 2 : 0); x < S + step; x += step) {
          const p = g.createRadialGradient(x - 3, y - 3, 1, x, y, r);
          p.addColorStop(0, 'rgba(255,255,255,0.95)');
          p.addColorStop(0.75, 'rgba(255,255,255,0.35)');
          p.addColorStop(1, 'rgba(0,0,0,0.25)');
          g.fillStyle = p;
          g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
        }
      }
      return cv;
    }
    function buildCarbonTexture() {
      const S = 512;
      const cv = document.createElement('canvas'); cv.width = S; cv.height = S;
      const g = cv.getContext('2d');
      g.fillStyle = '#14161b'; g.fillRect(0, 0, S, S);
      const t = 32;
      for (let y = 0; y < S; y += t) {
        for (let x = 0; x < S; x += t) {
          const horiz = ((x / t) + (y / t)) % 2 === 0;   // sarga 2×2
          const gr = horiz ? g.createLinearGradient(x, y, x, y + t) : g.createLinearGradient(x, y, x + t, y);
          gr.addColorStop(0, '#2c313c'); gr.addColorStop(0.5, '#191d24'); gr.addColorStop(1, '#2c313c');
          g.fillStyle = gr;
          g.fillRect(x, y, t, t);
          g.fillStyle = 'rgba(160,190,230,0.10)';   // brillo del hilo
          if (horiz) g.fillRect(x, y + t * 0.28, t, 3); else g.fillRect(x + t * 0.28, y, 3, t);
        }
      }
      return cv;
    }
    const TEX_BUILDERS = {
      fuego: () => buildPipTexture({ base: '#1c1c20', hi: '#5a5f68', lo: '#000000', glow: true, glowColor: 'rgba(255,90,42,0.85)' }),
      hielo: () => buildFrostTexture(),
      oro: () => buildGoldTexture(),
      holo: () => buildHoloTexture(),
      carbon: () => buildCarbonTexture(),
      /* r76 · pieles de asistencia: neón (goma oscura de pips verdes que
       * emiten) y fantasma (goma blanca espectral) — mismos builders de la
       * casa: cero shaders nuevos, cero coste nuevo por frame. */
      neon: () => buildPipTexture({ base: '#0c1410', hi: '#39ff88', lo: '#02120a', glow: true, glowColor: 'rgba(57,255,136,0.9)' }),
      fantasma: () => buildPipTexture({ base: '#dfeef8', hi: '#ffffff', lo: '#9dc2d6', glow: false }),
    };
    function getSkinTex(id) {
      if (!SKIN_TEX[id]) {
        const cv = TEX_BUILDERS[id] && TEX_BUILDERS[id]();
        if (!cv) return null;
        const map = new THREE.CanvasTexture(cv);
        map.anisotropy = 4;
        map.wrapS = map.wrapT = THREE.RepeatWrapping;
        try { if (THREE.SRGBColorSpace) map.colorSpace = THREE.SRGBColorSpace; } catch (e) { /* three viejo */ }
        SKIN_TEX[id] = { map, cv };
      }
      return SKIN_TEX[id];
    }
    /* miniatura de la piel para los chips del menú (mini-pala con la
     * textura real, no un círculo de color) */
    const SKIN_PREVIEW = {};
    function skinPreviewCv(sk) {
      if (SKIN_PREVIEW[sk.id]) return SKIN_PREVIEW[sk.id];
      const S = 64;
      const cv = document.createElement('canvas'); cv.width = S; cv.height = S;
      const g = cv.getContext('2d');
      const tx = sk.tex && getSkinTex(sk.tex);
      if (tx) g.fillStyle = g.createPattern(tx.cv, 'repeat');
      else g.fillStyle = '#' + (sk.edge || 0xd8d2c4).toString(16).padStart(6, '0');
      g.beginPath(); g.ellipse(S * 0.5, S * 0.42, S * 0.34, S * 0.40, 0, 0, Math.PI * 2); g.fill();
      g.fillStyle = '#' + (sk.grip || 0x6b4a2f).toString(16).padStart(6, '0');
      g.fillRect(S * 0.42, S * 0.74, S * 0.16, S * 0.24);
      SKIN_PREVIEW[sk.id] = cv;
      return cv;
    }

    /* ---------------- APLICACIÓN DE LA SKIN ----------------
     * v3.0.3 · Tres capas por montura:
     *  A. MODELO 3D ALTERNATIVO (sk.modelUrl): se oculta la pala base y se
     *     añade una instancia del GLB externo con la MISMA ancla (escala,
     *     posición y giro copiados del modelo en marcha) — cambiar de pala
     *     de verdad. Si el GLB no llega, respaldo: texturas sobre la base.
     *  B. MATERIALES CON TEXTURA en el modelo base: el GLB trae materiales
     *     con nombre («rubber» goma de las caras, «trim» canto, «handle»
     *     mango, «paddle»/«inner_padding» cuerpo) — se sustituyen por
     *     materiales con las texturas de la piel; el material original se
     *     guarda para restaurar la Clásica.
     *  C. Cinta de agarre sobre el mango real (geometría V3.0.1 medida). */
    const altModelCache = {};   // url -> Promise<THREE.Group|null>
    function loadAltModel(url) {
      if (!altModelCache[url]) {
        altModelCache[url] = new Promise((resolve) => {
          try {
            new GLTFLoader().load(url, (gltf) => {
              const m = gltf.scene;
              fixInvertedMeshes(m);
              m.traverse((o) => {
                if (o.isMesh) {
                  o.castShadow = true;
                  const mats = Array.isArray(o.material) ? o.material : [o.material];
                  for (const mt of mats) {
                    if (!mt) continue;
                    mt.side = THREE.DoubleSide;
                    if (mt.transparent && mt.opacity >= 1 && !mt.alphaTest) { mt.transparent = false; mt.depthWrite = true; }
                    mt.needsUpdate = true;
                  }
                }
              });
              console.info('[PP_TRAIN] skin GLB cargado:', url);
              resolve(m);
            }, undefined, () => {
              console.warn('[PP_TRAIN] skin GLB no disponible (respaldo con texturas):', url);
              resolve(null);
            });
          } catch (e) { resolve(null); }
        });
        // v3.0.3 · cuando el GLB llega, el cache guarda el MODELO (no la
        // promesa) para que refreshMounts pueda instanciarlo
        altModelCache[url].then((m) => { if (m) altModelCache[url] = m; });
      }
      return altModelCache[url];
    }
    function baseInstanceOf(mount) {
      // v3.0.3 · el hijo etiquetado «ppbase» (etiquetado en la 1ª pasada) o,
      // la primera vez, el hijo sin etiqueta (el grupo de makePaddleVisual)
      for (const ch of mount.children) {
        if (ch.userData && ch.userData.ppTrainTag === 'ppbase') return ch;
      }
      for (const ch of mount.children) {
        if (!ch.userData || !ch.userData.ppTrainTag) return ch;
      }
      return null;
    }
    function applySkinMaterials(mount, sk) {
      const want = sk.tex ? getSkinTex(sk.tex) : null;
      mount.traverse((o) => {
        if (!o.isMesh || !o.material) return;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        const name = (o.userData && o.userData.ppSkinPart) || (mats[0] && mats[0].name);
        if (name !== 'rubber' && name !== 'trim' && name !== 'handle' &&
            name !== 'paddle' && name !== 'inner_padding') return;
        if (!o.userData.ppSkinPart) o.userData.ppSkinPart = name;
        if (!o.userData.ppOrigMat) o.userData.ppOrigMat = o.material;
        if (!want) { o.material = o.userData.ppOrigMat; return; }   // Clásica: original
        const key = 'ppSkin_' + sk.id + '_' + name;
        let mat = skinMats.find((m2) => m2.name === key);
        if (!mat) {
          if (name === 'rubber') {
            mat = new THREE.MeshStandardMaterial({ map: want.map });
            if (sk.id === 'oro') { mat.roughness = 0.38; mat.metalness = 0.72; }
            else if (sk.id === 'hielo') { mat.roughness = 0.42; mat.metalness = 0.05; }
            else if (sk.id === 'holo') { mat.roughness = 0.5; mat.metalness = 0.25; }
            else { mat.roughness = 0.85; mat.metalness = 0.04; }
            if (sk.id === 'fuego') {   // brasas: la propia textura emite
              mat.emissive = new THREE.Color(0xff5a2a);
              mat.emissiveMap = want.map;
              mat.emissiveIntensity = 0.26;
            }
            if (sk.anim) mat.userData.ppAnim = true;
          } else if (name === 'trim') {
            mat = new THREE.MeshStandardMaterial({ color: sk.edge, roughness: 0.5, metalness: 0.2 });
          } else if (name === 'handle') {
            mat = (sk.tex === 'carbon' || sk.id === 'fuego')
              ? new THREE.MeshStandardMaterial({ map: getSkinTex('carbon').map, roughness: 0.55, metalness: 0.35 })
              : new THREE.MeshStandardMaterial({ color: sk.grip, roughness: 0.8 });
          } else {
            mat = new THREE.MeshStandardMaterial({ color: 0x23262c, roughness: 0.7 });
          }
          mat.name = key;
          skinMats.push(mat);
        }
        o.material = mat;
      });
    }
    function refreshMounts(sk) {
      if (!G || !G.paddleMounts) return;
      let alt = null;
      if (sk.modelUrl) {
        const p = altModelCache[sk.modelUrl];
        if (p && typeof p.then !== 'function') alt = p;   // cargado
        else if (!p) loadAltModel(sk.modelUrl).then(() => {
          if (S.skin === sk.id) { refreshMounts(sk); if (G && G.menuOpen) G.drawMenu(); }
        });
      }
      for (const mount of G.paddleMounts) {
        clearNamed(mount, 'skin');
        const base = baseInstanceOf(mount);
        if (base && !base.userData.ppTrainTag) base.userData.ppTrainTag = 'ppbase';
        if (base) base.visible = !alt;
        applySkinMaterials(mount, sk);
        // v3.0.9-HALL1 · la CINTA DE AGARRE (cilindro sobre el mango) se
        // RETIRA: el mango ya se viste con su material «handle» y el
        // cilindro extra se leía como un resto pegado a la pala. La pala
        // alternativa (Pro Carbon) sigue montándose con su propia
        // empuñadura, que es la que trae el GLB.
        if (alt && base && base.children[0]) {
          // A) instancia del modelo alternativo con la MISMA ancla que la base
          const src = base.children[0];
          const inst = alt.clone(true);
          inst.scale.copy(src.scale);
          inst.position.copy(src.position);
          inst.rotation.copy(src.rotation);
          inst.userData.ppTrainTag = 'skin';
          mount.add(inst);
        }
      }
    }
    /* r45 · PINTA UNA INSTANCIA CUALQUIERA de la pala con la skin pedida
     * (la usa el JUEGO para la pala del rival en red — c12 onPeerPala):
     * teñido de goma/canto/mango con la caché de pieles de la casa (claves
     * por skin.id — pieles distintas jamás sangran entre sí) y, si la piel
     * trae modelo alternativo (Pro Carbon), sustitución de la hoja base.
     * Las pieles de racha (neón/fantasma/campeón) van por tinte. Nunca
     * toca localStorage ni el perk del dueño: SOLO pintura. */
    function pintaPalaExterna(obj, skinId) {
      try {
        if (!obj || !obj.isObject3D) return;
        const sk = SKINS.find((s0) => s0.id === skinId) || SKINS[0];
        obj.userData.ppSkinWanted = sk.id;
        applySkinMaterials(obj, sk);
        if (sk.modelUrl) {
          const p = altModelCache[sk.modelUrl];
          if (p && typeof p.then !== 'function') _montaAltExterna(obj, sk);
          else if (!p) loadAltModel(sk.modelUrl).then(() => {
            if (obj.userData.ppSkinWanted === sk.id) _montaAltExterna(obj, sk);
          }).catch(() => { /* respaldo: queda el tinte */ });
        } else {
          // sin modelo alternativo: fuera la hoja sustituida (si la hubo)
          // y la base vuelve a la vista con su tinte nuevo
          clearNamed(obj, 'skin');
          for (const c0 of obj.children) {
            if (!c0.userData || c0.userData.ppTrainTag !== 'skin') c0.visible = true;
          }
        }
      } catch (e) { /* cosmético: jamás rompe el juego */ }
    }
    function _montaAltExterna(obj, sk) {
      const alt = altModelCache[sk.modelUrl];
      if (!alt || typeof alt.then === 'function') return;
      clearNamed(obj, 'skin');
      const base = obj.children.find((c0) => !c0.userData || c0.userData.ppTrainTag !== 'skin');
      if (!base) return;
      base.visible = false;
      const inst = alt.clone(true);
      inst.scale.copy(base.scale);
      inst.position.copy(base.position);
      inst.rotation.copy(base.rotation);
      inst.userData.ppTrainTag = 'skin';
      obj.add(inst);
    }
    try { window.__PP_TRAIN_PINTA_PALA = pintaPalaExterna; } catch (e) { /* */ }

    function applySkin(skinId) {
      const sk = SKINS.find((s) => s.id === skinId) || SKINS[0];
      S.skin = sk.id; save();
      skinMats = [];
      if (!G || !G.paddleMounts) return;
      refreshMounts(sk);
      if (typeof window !== 'undefined' && typeof window.__PP_SET_PADDLE_SKIN === 'function') {
        window.__PP_SET_PADDLE_SKIN(sk.id);
      }
      updateFaceHints();
    }
    /** v3.0.5 · DOBLE GOMA — en el Pro Carbon las dos caras quedan TEÑIDAS
     *  y marcadas (cian = goma de GIRO, naranja = goma DURA de potencia)
     *  para reconocerlas en el casco; en el resto de pieles, apagadas. */
    function updateFaceHints() {
      if (!faceIcons.length) return;
      const PP = (typeof window !== 'undefined' && window.__PP_PADDLE_PERKS)
        ? window.__PP_PADDLE_PERKS[S.skin] : null;
      const dual = !!(PP && PP.dual);
      for (const s of faceIcons) {
        const side = (s.userData && s.userData.ppFace) || 1;
        if (dual) {
          s.material.color.setHex(side === 1 ? 0x53d0ff : 0xff8a3a);
          s.material.opacity = 0.24;
          s.visible = true;
          s.userData.ppBaseOp = 0.24;
        } else {
          s.userData.ppBaseOp = 0;
          if (st.spinIconT <= 0) s.visible = false;
        }
      }
    }
    function buildFaceIcons() {
      if (!G || !G.paddleMounts) return;
      // limpiar previos
      for (const mount of G.paddleMounts) clearNamed(mount, 'faceicon');
      faceIcons = [];
      const mkTex = () => {
        const cv = mkCanvas(64, 64);
        const g2 = cv.getContext('2d');
        g2.strokeStyle = '#ffffff'; g2.lineWidth = 7;
        g2.beginPath(); g2.arc(32, 32, 19, 0.2, Math.PI * 1.5); g2.stroke();
        g2.fillStyle = '#ffffff';
        g2.beginPath(); g2.moveTo(44, 4); g2.lineTo(57, 17); g2.lineTo(37, 22);
        g2.closePath(); g2.fill();
        return texOf(cv);
      };
      const tx = mkTex();
      const T = G.paddleModelRef ? TRN : TRN_FB;
      for (const mount of G.paddleMounts) {
        for (const side of [1, -1]) {
          // V3.0.1 · icono PEGADO a cada cara de la hoja (plano sobre la cara,
          // como un adhesivo): antes eran sprites flotando a 17 mm del centro,
          // desplazados respecto a la hoja real.
          const sp = new THREE.Mesh(
            new THREE.PlaneGeometry(0.055, 0.055),
            new THREE.MeshBasicMaterial({ map: tx, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide }),
          );
          sp.position.set(T.bladeX, T.bladeY, side * T.bladeZ);
          if (side < 0) sp.rotation.y = Math.PI;
          sp.renderOrder = 7;
          sp.visible = false;
          sp.userData.ppTrainTag = 'faceicon';
          sp.userData.ppFace = side;   // v3.0.5: cara A (+1) / cara B (−1) para la DOBLE GOMA
          mount.add(sp);
          faceIcons.push(sp);
        }
      }
    }
    /** Icono en AMBAS caras cuando el jugador aplica efecto (en TODO el juego).
     *  ronda 27 (informe del dueño «sólo hace caso la línea de tiro»): ahora
     *  OBEDECE al interruptor «Flecha de efecto» (S.fb.spin) igual que el
     *  sprite de la bola — desmarcado, ningún icono de efecto aparece. */
    function pulseFaceIcons(lift) {
      if (!S.fb.spin) return;
      const col = lift < 0 ? 0xff9a4a : lift > 0 ? 0x4ab8ff : 0xc07aff;
      for (const s of faceIcons) {
        s.material.color.setHex(col);
        s.material.opacity = 1;
        s.visible = true;
      }
      st.spinIconT = 1.15;
    }
  
    /* =================================================================
     *  MENÚ VR · PRO TRAINING HUB (páginas 'train' y 'trainarea')
     *  ================================================================= */
    function drawHeader(game, c, rects, btn, label, subTxt) {
      c.fillStyle = '#f0c85a';
      c.font = '900 54px system-ui, sans-serif';
      c.textAlign = 'left'; c.textBaseline = 'middle';
      c.fillText(t('hub_t'), 40, 78);
      c.fillStyle = '#a9b8cc';
      c.font = '600 24px system-ui, sans-serif';
      // r104 · subtítulo RECORTADO: con la fuente escalada llegó a pisar el
      // bloque de puntos/nivel/logros (x ≥ 560). Nunca pasa de 500 px.
      let sub104 = subTxt || t('hub_s');
      while (sub104.length > 2 && c.measureText(sub104).width > 500) sub104 = sub104.slice(0, -1);
      if (sub104 !== (subTxt || t('hub_s'))) sub104 += '…';
      c.fillText(sub104, 40, 122);
      c.strokeStyle = 'rgba(240,200,90,0.55)'; c.lineWidth = 3;
      c.beginPath(); c.moveTo(40, 152); c.lineTo(984, 152); c.stroke();
      btn('trv3:back', 820, 34, 164, 56, t('menu'), false, undefined, undefined, 24);
    }
  
    function drawHub(game, c, rects, btn, label) {
      LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
      drawHeader(game, c, rects, btn, label);
      // chip de perfil
      const lvl = levelOf(S.pts);
      c.textAlign = 'right'; c.textBaseline = 'middle';
      c.fillStyle = '#f0c85a'; c.font = '800 30px system-ui, sans-serif';
      c.fillText(S.pts + ' ' + t('pts'), 800, 82);
      c.fillStyle = '#8fa0b8'; c.font = '600 20px system-ui, sans-serif';
      c.fillText(t('nivel') + ' · ' + t(lvl.k), 800, 112);
      // v3.0.7-PLAY1 · barra de progreso al siguiente nivel + LOGROS n/9
      if (GAMF()) {
        const li = LEVELS.indexOf(lvl), nx = LEVELS[li + 1] || null;
        const bw = 240, bx = 800 - bw, by = 134;
        const prog = nx ? Math.min(1, (S.pts - lvl.min) / (nx.min - lvl.min)) : 1;
        c.fillStyle = 'rgba(255,255,255,0.14)';
        c.fillRect(bx, by, bw, 7);
        c.fillStyle = nx ? '#f0c85a' : '#68d391';
        c.fillRect(bx, by, Math.max(4, bw * prog), 7);
        c.font = '600 15px system-ui, sans-serif';
        c.fillStyle = '#a9b8cc';
        c.fillText(nx ? (S.pts + ' / ' + nx.min) : t('max'), 800, by + 22);
        const got = ACHS.filter((a) => S.ach[a]).length;
        c.font = '700 15px system-ui, sans-serif';
        c.fillStyle = '#a9b8cc';
        c.fillText(t('logros') + ' ' + got + '/' + ACHS.length, 800, by + 44);
        for (let i = 0; i < ACHS.length; i++) {
          const cx = bx + i * ((bw - 8) / (ACHS.length - 1));
          c.beginPath(); c.arc(cx, by + 62, 6, 0, Math.PI * 2);
          c.fillStyle = S.ach[ACHS[i]] ? '#f0c85a' : 'rgba(255,255,255,0.16)';
          c.fill();
        }
      }
      // tarjetas de áreas (2 × 3)
      // r116 · la parrilla BAJA a 236 px (informe del dueño: los textos y
      // números de los LOGROS «están descolocados» — la fila LOGROS n/9 y
      // sus puntos quedaban encerrados DENTRO de las tarjetas, que nacían
      // en 190 y los tapaban). La fila de logros respira libre.
      const CW = 456, CH = 150, GX = 32, GY = 16, X0 = 40, X1 = X0 + CW + GX;
      let y = 236;
      const card = (x, yy, id, ik, sk, g0, g1, col, act, ic) => {
        const idx = rects.length;
        btn('trv3:area:' + id, x, yy, CW, CH, '', false);
        // repintar encima con estilo propio (btn pinta un botón plano)
        c.save();
        c.beginPath();
        if (c.roundRect) c.roundRect(x, yy, CW, CH, 20); else c.rect(x, yy, CW, CH);
        const gr = c.createLinearGradient(x, yy, x + CW, yy + CH);
        gr.addColorStop(0, g0); gr.addColorStop(1, g1);
        c.fillStyle = gr; c.fill();
        c.strokeStyle = act ? '#f0c85a' : (game.menuHover && game.menuHover.includes(idx) ? '#ffffff' : 'rgba(255,255,255,0.25)');
        c.lineWidth = act ? 5 : 3;
        c.stroke();
        c.fillStyle = col; c.globalAlpha = 0.16;
        c.beginPath(); c.arc(x + CW - 56, yy + CH / 2, 44, 0, Math.PI * 2); c.fill();
        c.globalAlpha = 1;
        // r72 · ICONO EXPLÍCITO del área dentro del medallón (PP_ICONS)
        const ico = ic && PP_ICONS[ic];
        if (ico) { try { ico(c, x + CW - 56, yy + CH / 2); } catch (eIco) { /* decorativo */ } }
        c.fillStyle = '#ffffff'; c.textAlign = 'left'; c.textBaseline = 'middle';
        let fs = 34;
        c.font = '800 ' + fs + 'px system-ui, sans-serif';
        while (fs > 22 && c.measureText(t(ik)).width > CW - 60) { fs -= 2; c.font = '800 ' + fs + 'px system-ui, sans-serif'; }
        c.fillText(t(ik), x + 26, yy + 52);
        c.fillStyle = 'rgba(255,255,255,0.8)'; c.font = '600 19px system-ui, sans-serif';
        let sub2 = t(sk);
        while (sub2.length > 2 && c.measureText(sub2).width > CW - 52) sub2 = sub2.slice(0, -1);
        if (sub2 !== t(sk)) sub2 += '…';
        c.fillText(sub2, x + 26, yy + 86);
        const bests = Object.keys(MODES).filter((m) => MODES[m].area === id && S.best[m]);
        c.fillStyle = '#f0c85a'; c.font = '700 18px system-ui, sans-serif';
        c.fillText(bests.length ? t('mejor') + ': ' + bests.map((m) => S.best[m]).join(' / ') : '·', x + 26, yy + 120);
        /* M7d (r120) · MEDALLERO del área a la derecha de la fila (sólo si
         * hay metal): 🥇n 🥈n 🥉n — el hub resume el honor de la academia */
        const mds = Object.keys(MODES).filter((m) => MODES[m].area === id);
        const tal = mds.reduce((acc, m) => { const d = medallaDe(m); if (d) acc[d - 1]++; return acc; }, [0, 0, 0]);
        if (tal[0] || tal[1] || tal[2]) {
          c.textAlign = 'right';
          c.fillText('\u{1F947}' + tal[2] + ' \u{1F948}' + tal[1] + ' \u{1F949}' + tal[0], x + CW - 24, yy + 120);
          c.textAlign = 'left';
        }
        c.restore();
      };
      for (let i = 0; i < AREAS.length; i++) {
        const a = AREAS[i];
        card(i % 2 === 0 ? X0 : X1, y + Math.floor(i / 2) * (CH + GY), a.id, a.ik, a.sk, a.g0, a.g1, a.col, false, a.ic);
      }
      /* M4 (r118) · RETO DE LA SEMANA en el HUECO 6 de la parrilla (el que
       * dejó la tarjeta de posición de la pala al mudarse a AJUSTES r83).
       * El hermano mayor del PULSO con SU insignia: mismo duelo
       * determinista por septana, puntos mayores (120/30). */
      if (GAMF()) {
        const wk = weekKey();
        const wp = weeklyPlan(wk);
        const hecho6 = !!S.semana.done[wk];
        const yy6 = y + 2 * (CH + GY);
        const idx6 = rects.length;
        btn('trv3:semana', X1, yy6, CW, CH, '', false);
        c.save();
        c.beginPath();
        if (c.roundRect) c.roundRect(X1, yy6, CW, CH, 20); else c.rect(X1, yy6, CW, CH);
        const gr6 = c.createLinearGradient(X1, yy6, X1 + CW, yy6 + CH);
        gr6.addColorStop(0, hecho6 ? '#4a5a34' : '#8c6d1f');
        gr6.addColorStop(1, hecho6 ? '#26301b' : '#4a3a10');
        c.fillStyle = gr6; c.fill();
        c.strokeStyle = (game.menuHover && game.menuHover.includes(idx6)) ? '#ffffff'
          : (hecho6 ? 'rgba(127,176,105,0.65)' : '#f0c85a');
        c.lineWidth = 3; c.stroke();
        // medallón con la INSIGNIA semanal (cuenta acumulada)
        c.fillStyle = hecho6 ? 'rgba(127,176,105,0.20)' : 'rgba(240,200,90,0.16)';
        c.beginPath(); c.arc(X1 + CW - 56, yy6 + CH / 2, 44, 0, Math.PI * 2); c.fill();
        c.fillStyle = hecho6 ? '#9ad17f' : '#f0c85a';
        c.font = '900 26px system-ui, sans-serif';
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText('\u{1F3C5}', X1 + CW - 56, yy6 + CH / 2 - 8);
        c.font = '700 15px system-ui, sans-serif';
        c.fillText('\u00D7' + S.semana.bad, X1 + CW - 56, yy6 + CH / 2 + 16);
        c.fillStyle = '#ffffff'; c.textAlign = 'left';
        c.font = '800 30px system-ui, sans-serif';
        c.fillText(t('semana_t'), X1 + 26, yy6 + 48);
        c.fillStyle = 'rgba(255,255,255,0.85)'; c.font = '600 18px system-ui, sans-serif';
        let sub6 = t('semana_sub', { m: t(MODES[wp.mode].nk), n: wp.n });
        while (sub6.length > 2 && c.measureText(sub6).width > CW - 130) sub6 = sub6.slice(0, -1);
        if (sub6 !== t('semana_sub', { m: t(MODES[wp.mode].nk), n: wp.n })) sub6 += '\u2026';
        c.fillText(sub6, X1 + 26, yy6 + 82);
        c.fillStyle = hecho6 ? '#9ad17f' : '#f0c85a';
        c.font = '700 19px system-ui, sans-serif';
        c.fillText(hecho6 ? t('semana_ya') : t('semana_iniciar'), X1 + 26, yy6 + 118);
        c.restore();
      }
      // r83 · la tarjeta POSICIÓN DE LA PALA se RETIRA del hub (se muda a
      // AJUSTES › PALA, subapartado propio con passthrough y ejes completos):
      // «Dentro del Pro Trainning tenemos el ajuste de la posición de la
      // pala, pero no tiene sentido ahí». Las ayudas técnicas suben a su
      // hueco y el hub queda 100 % entrenamiento (5 áreas + pieles).
      const yFb = y + 3 * (CH + GY) + 16;
      label(t('fb_t'), yFb, 22, '#a9b8cc');
      const toggles = [['marks', t('fb_marks')], ['line', t('fb_line')], ['spin', t('fb_spin')]];
      let tx = X0;
      for (const [k, lbl] of toggles) {
        const w = 290;
        btn('trv3:fb:' + k, tx, yFb + 18, w, 64, lbl, !!S.fb[k], undefined, !!S.fb[k], 22);
        tx += w + 24;
      }
      // skins
      const ySk = yFb + 108;
      label(t('skins_t'), ySk, 22, '#a9b8cc');
      let sx = X0;
      for (const sk of SKINS) {
        if (sk.via === 'racha') continue;   // r76: las de asistencia viven en EL PULSO (fila propia)
        const w = 150, h = 76;
        const un = S.unlocked.indexOf(sk.id) >= 0;
        const idb = 'trv3:skin:' + sk.id;
        const idx = rects.length;
        btn(idb, sx, ySk + 18, w, h, '', false);
        c.save();
        c.beginPath();
        if (c.roundRect) c.roundRect(sx, ySk + 18, w, h, 14); else c.rect(sx, ySk + 18, w, h);
        c.fillStyle = S.skin === sk.id ? 'rgba(240,200,90,0.30)' : 'rgba(255,255,255,0.06)';
        c.fill();
        c.strokeStyle = S.skin === sk.id ? '#f0c85a' : (un ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.15)');
        c.lineWidth = S.skin === sk.id ? 4 : 2;
        c.stroke();
        // v3.0.3 · miniatura de la piel: MINI-PALA con la textura real de
        // la goma (no un círculo de color)
        c.beginPath(); c.arc(sx + 30, ySk + 56, 22, 0, Math.PI * 2);
        c.fillStyle = un ? 'rgba(255,255,255,0.92)' : 'rgba(255,255,255,0.12)';
        c.fill();
        c.strokeStyle = 'rgba(255,255,255,0.5)'; c.lineWidth = 2; c.stroke();
        if (un) {
          c.save();
          c.beginPath(); c.arc(sx + 30, ySk + 56, 20, 0, Math.PI * 2); c.clip();
          c.drawImage(skinPreviewCv(sk), sx + 10, ySk + 36, 40, 40);
          c.restore();
        }
        c.fillStyle = un ? '#e9edf2' : '#5a6a7d';
        const nmFull = un ? (sk.name[LANG] || sk.name.es) : '\u{1F512} ' + sk.min;
        let nm = nmFull;
        c.font = '700 17px system-ui, sans-serif'; c.textAlign = 'left'; c.textBaseline = 'middle';
        while (nm.length > 2 && c.measureText(nm).width > 86) nm = nm.slice(0, -1);
        c.fillText(nm, sx + 58, ySk + 44);
        if (un) {
          // v3.0.5 · PALAS CON CARÁCTER — etiqueta de la goma en la tarjeta
          const PT = (typeof window !== 'undefined' && window.__PP_PADDLE_PERKS)
            ? window.__PP_PADDLE_PERKS[sk.id] : null;
          if (PT) {
            c.fillStyle = PT.col; c.font = '800 11px system-ui, sans-serif';
            c.fillText(t(PT.tag), sx + 58, ySk + 61);
          }
        }
        if (un && S.skin === sk.id) {
          c.fillStyle = '#f0c85a'; c.font = '600 13px system-ui, sans-serif';
          c.fillText(t('skin_sel'), sx + 58, ySk + 76);
        }
        c.restore();
        sx += w + 14;
      }
      // v3.0.5 · leyenda de CARÁCTER de la piel equipada
      {
        const PT = (typeof window !== 'undefined' && window.__PP_PADDLE_PERKS)
          ? window.__PP_PADDLE_PERKS[S.skin] : null;
        if (PT) label(t(PT.tag) + ' — ' + t(PT.tag + '_d'), ySk + 106, 14, PT.col);
      }
      /* =============================================================
       *  v3.6.72 (r80) · EL RETO SE MUDA A LA PUERTA — el dueño retira el
       *  panel del hub de entrenamiento: «La opción del reto del día debe
       *  estar especialmente destacada en la parte de abajo del menú
       *  principal (y la retiramos del apartado de entrenamiento)». Ahora
       *  es BOTÓN ESTRELLA al pie del menú principal (c12
       *  _retoDiarioCard: pala troquelada + resplandor, texto «Reto
       *  Diario!») y arranca el duelo de hoy vía PP_TRAIN.startDaily.
       *  Aquí queda el ESCAPARATE de las pieles de asistencia: lo que la
       *  racha de días libera poco a poco.
       *  ============================================================= */
      if (GAMF()) {
        const wD = CW * 2 + GX;
        // pieles de ASISTENCIA (r76): fila propia en el hueco del panel —
        // jamás en la fila de puntos; sólo la racha del RETO DIARIO libera
        const yA = 1064;
        label(t('daily_asist'), yA, 15, '#a9b8cc');
        let axD = X0;
        for (const sk of RACHA_SKINS) {
          const w = 150, h = 76;
          const un = S.unlocked.indexOf(sk.id) >= 0;
          btn('trv3:skin:' + sk.id, axD, yA + 18, w, h, '', false);
          c.save();
          c.beginPath();
          if (c.roundRect) c.roundRect(axD, yA + 18, w, h, 14); else c.rect(axD, yA + 18, w, h);
          c.fillStyle = S.skin === sk.id ? 'rgba(240,200,90,0.30)' : 'rgba(255,255,255,0.06)';
          c.fill();
          c.strokeStyle = S.skin === sk.id ? '#f0c85a' : (un ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.15)');
          c.lineWidth = S.skin === sk.id ? 4 : 2;
          c.stroke();
          c.beginPath(); c.arc(axD + 30, yA + 56, 22, 0, Math.PI * 2);
          c.fillStyle = un ? 'rgba(255,255,255,0.92)' : 'rgba(255,255,255,0.12)'; c.fill();
          c.strokeStyle = 'rgba(255,255,255,0.5)'; c.lineWidth = 2; c.stroke();
          if (un) {
            c.save();
            c.beginPath(); c.arc(axD + 30, yA + 56, 20, 0, Math.PI * 2); c.clip();
            c.drawImage(skinPreviewCv(sk), axD + 10, yA + 36, 40, 40);
            c.restore();
          } else {
            // r76 · el candado vive en el HUECO de la miniatura (slot de
            // inventario) — el nombre queda limpio y jamás se trunca
            c.font = '20px system-ui, sans-serif'; c.textAlign = 'center';
            c.fillText('\u{1F512}', axD + 30, yA + 57);
          }
          c.fillStyle = un ? '#e9edf2' : '#5a6a7d';
          // r76 · fila SUPERIOR = nombre limpio (fitFont: primero reduce la
          // fuente, jamás corta si cabe), fila INFERIOR = hito de racha
          let nmA = (sk.name[LANG] || sk.name.es);
          let fsA = 17;
          c.font = '700 ' + fsA + 'px system-ui, sans-serif'; c.textAlign = 'left'; c.textBaseline = 'middle';
          while (fsA > 13 && c.measureText(nmA).width > 86) { fsA -= 1; c.font = '700 ' + fsA + 'px system-ui, sans-serif'; }
          const _w4 = nmA;
          while (nmA.length > 2 && c.measureText(nmA).width > 86) nmA = nmA.slice(0, -1);
          if (nmA !== _w4) nmA += '…';
          c.fillText(nmA, axD + 58, yA + 46);
          c.font = '600 13px system-ui, sans-serif';
          if (S.skin === sk.id) {
            c.fillStyle = '#f0c85a';
            c.fillText(t('skin_sel'), axD + 58, yA + 64);
          } else if (un) {
            c.fillStyle = '#a9b8cc';
            c.fillText(sk.days + ' ' + t('daily_dias'), axD + 58, yA + 64);
          } else {
            c.fillStyle = '#5a6a7d';
            c.fillText('racha ' + sk.days + ' ' + t('daily_dias'), axD + 58, yA + 64);
          }
          c.restore();
          axD += w + 14;
        }
        c.textAlign = 'left'; c.textBaseline = 'middle';
        c.fillStyle = '#a9b8cc'; c.font = '600 14px system-ui, sans-serif';
        let htD = t('daily_hitos');
        const _w5 = htD;
        while (htD.length > 2 && c.measureText(htD).width > X0 + wD - (axD - 14) - 16) htD = htD.slice(0, -1);
        if (htD !== _w5) htD += '…';
        c.fillText(htD, axD - 14 + 16, yA + 56);
      }
      /* =============================================================
       *  r97 · MAPA DE CALOR (petición del dueño: «mapa de calor de zonas
       *  donde pierdes puntos — el entrenamiento ya mide zonas»): tarjeta
       *  con el HISTÓRICO global (pp_heat_v1 que alimenta el núcleo al
       *  perder un punto en partido). Rejilla 3×3 (corta/media/fondo ×
       *  izq/centro/der vistas del jugador), rojo = zonas donde te ganan
       *  más puntos. Sólo lectura: diagnóstico para dirigir el
       *  entrenamiento (si te ganan en el fondo-derecha: drills de fondo).
       *  ============================================================= */
      {
        const hg = (game && game.heatGlobal) ? game.heatGlobal() : [0, 0, 0, 0, 0, 0, 0, 0, 0];
        let tot = 0; for (let i = 0; i < 9; i++) tot += hg[i] | 0;
        let maxC = 1; for (let i = 0; i < 9; i++) maxC = Math.max(maxC, hg[i] | 0);
        const wD2 = CW * 2 + GX, yH = 1170, hH = 178;
        c.save();
        c.beginPath();
        if (c.roundRect) c.roundRect(X0, yH, wD2, hH, 20); else c.rect(X0, yH, wD2, hH);
        c.fillStyle = 'rgba(10,14,22,0.55)';
        c.fill();
        c.strokeStyle = 'rgba(255,255,255,0.16)';
        c.lineWidth = 2;
        c.stroke();
        c.fillStyle = '#f0c85a'; c.font = '800 24px system-ui, sans-serif';
        c.textAlign = 'left'; c.textBaseline = 'middle';
        c.fillText(t('heat_t'), X0 + 26, yH + 30);
        c.fillStyle = '#8fa0b8'; c.font = '600 16px system-ui, sans-serif';
        c.fillText(tot > 0 ? t('heat_total').replace('{n}', String(tot)) : t('heat_sin'), X0 + 26, yH + 58);
        // mini-mesa 3×3 (red arriba, jugador abajo) + etiquetas de fila
        const cwH = 52, chH = 34, gxH = X0 + 26, gyH = yH + 74;
        for (let r = 0; r < 3; r++) {
          for (let cI = 0; cI < 3; cI++) {
            const v = hg[r * 3 + cI] | 0;
            const alfa = v > 0 ? (0.18 + 0.72 * (v / maxC)) : 0.05;
            c.fillStyle = v > 0 ? 'rgba(255,82,70,' + alfa.toFixed(2) + ')'
              : 'rgba(255,255,255,0.05)';
            c.fillRect(gxH + cI * (cwH + 3), gyH + r * (chH + 3), cwH, chH);
          }
        }
        c.fillStyle = 'rgba(255,255,255,0.55)';
        c.fillRect(gxH - 3, gyH - 7, cwH * 3 + 12, 3);   // la red
        c.fillStyle = '#93a3b8'; c.font = '600 13px system-ui, sans-serif';
        c.fillText(t('heat_corta'), gxH + cwH * 3 + 16, gyH + chH * 0.5 + 1);
        c.fillText(t('heat_media'), gxH + cwH * 3 + 16, gyH + chH * 1.5 + 4);
        c.fillText(t('heat_fondo'), gxH + cwH * 3 + 16, gyH + chH * 2.5 + 7);
        c.restore();
      }
      // botón parar si hay modo activo + vuelta al HALL (v3.1.0-SRV2: el
      // hall es el hub — desde el propio hub de entrenamiento se sale a la
      // estancia sin pasar por el menú principal)
      if (active) btn('trv3:stop', X0, 1380, 452, 76, t('parar'), false, 'surv', undefined, 28);
      if (!game.inHall && !game.net.online) {
        btn('homehall', active ? X1 : X0, 1380, 452, 76, T('hall_home_btn'), false, undefined, undefined, 26);
      }
    }
  
    function drawArea(game, c, rects, btn, label) {
      LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
      const a = AREAS.find((x) => x.id === uiArea) || AREAS[0];
      // r84 · F180 · MIGRACIÓN al interior C del arco (la deuda r80: «hasta
      // su migración»): fuera el espacio legado 1024×1536, la placa y su
      // escala 0.911 — las tarjetas pintan NATIVAS a banda completa de la
      // panela C (gx/gw como _menuBandas). El informe del dueño: «los
      // subapartados de entrenamiento están con una maquetación antigua».
      // La división de área mantiene SU mecánica íntegra (ids intactos).
      game._menuMap = null;
      const pC = CONFIG_MENUS.arco.panelas.find((p) => p.id === 'C');
      const gx = pC.x + 80, gw = pC.w - 160;
      let y = 262;
      for (const id of Object.keys(MODES)) {
        const M = MODES[id];
        if (M.area !== a.id) continue;
        const isOn = active === id;
        // tarjeta del modo
        const idx = rects.length;
        btn('trv3:start:' + id, gx, y, gw, 180, '', false);
        c.save();
        c.beginPath();
        if (c.roundRect) c.roundRect(gx, y, gw, 180, 22); else c.rect(gx, y, gw, 180);
        // r74 · FASE 168 · placa de museo en las tarjetas del ÁREA (el
        // color del área sobrevive en el aro del medallón, no en el relleno
        // saturado) — la estética nueva hasta el último subnivel.
        if (game._vestPlaca73) game._vestPlaca73(c, gx, y, gw, 180, 22);
        c.strokeStyle = isOn ? '#f0c85a' : 'rgba(232,180,90,0.32)'; c.lineWidth = isOn ? 5 : 3;
        c.stroke();
        c.textAlign = 'left'; c.textBaseline = 'middle';
        c.fillStyle = '#ffffff'; c.font = '800 34px system-ui, sans-serif';
        c.fillText(t(M.nk), gx + 28, y + 40);
        c.fillStyle = 'rgba(255,255,255,0.85)';
        const desc = t(M.dk, { n: M.n });
        // r116 · CUERPO A PRUEBA DE DESBORDE — ahora a lo ancho de la C
        // (gw−72 = 1240 px: casi todas las descripciones caben en 1-2 líneas)
        let dFs = 22;
        const wrapAt = (fs) => {
          c.font = '600 ' + fs + 'px system-ui, sans-serif';
          const ls = [''];
          for (const w of desc.split(' ')) {
            const cur = ls[ls.length - 1];
            const cand = cur ? cur + ' ' + w : w;
            if (!cur || c.measureText(cand).width <= gw - 320) {
              ls[ls.length - 1] = cand;
            } else {
              ls.push(w);
            }
          }
          return ls;
        };
        let dLines = wrapAt(dFs);
        if (dLines.length > 2) { dFs = 20; dLines = wrapAt(dFs); }
        const dCorta = dLines.length > 3;
        dLines = dLines.slice(0, 3);
        for (let i = 0; i < dLines.length; i++) {
          while (dLines[i].length > 2 &&
              c.measureText(dLines[i]).width > gw - 320) {
            dLines[i] = dLines[i].slice(0, -1);
          }
        }
        if (dCorta && dLines[2]) dLines[2] += '…';
        c.font = '600 ' + dFs + 'px system-ui, sans-serif';
        if (dLines.length > 2) {
          c.fillText(dLines[0], gx + 28, y + 72);
          c.fillText(dLines[1], gx + 28, y + 96);
          c.fillText(dLines[2], gx + 28, y + 120);
        } else if (dLines.length === 2) {
          c.fillText(dLines[0], gx + 28, y + 84);
          c.fillText(dLines[1], gx + 28, y + 110);
        } else {
          c.fillText(dLines[0] || '', gx + 28, y + 96);
        }
        c.fillStyle = '#f0c85a'; c.font = '700 20px system-ui, sans-serif';
        c.fillText((S.best[id] ? t('mejor') + ': ' + S.best[id] + '  ·  ' : '') +
          t('obj') + ': ' + M.n, gx + 28, y + 148);
        // v3.0.7-PLAY1 · estrellas logradas + mejor precisión de la prueba
        // M7d (r120) · MEDALLA del ejercicio delante de las estrellas
        if (GAMF()) {
          const stN = S.stars[id] || 0;
          c.textAlign = 'right';
          const md = medallaDe(id);
          let meta = (md ? MED_GLYPH[md] + ' ' : '') +
            '\u2605'.repeat(stN) + '\u2606'.repeat(3 - stN);
          if (S.acc[id]) meta += '  ' + S.acc[id] + '%';
          c.fillStyle = stN ? '#f0c85a' : 'rgba(255,255,255,0.35)';
          c.font = '800 22px system-ui, sans-serif';
          c.fillText(meta, gx + gw - 34, y + 148);
        }
        c.textAlign = 'right';
        c.fillStyle = isOn ? '#f0c85a' : '#ffffff';
        c.font = '900 26px system-ui, sans-serif';
        c.fillText(isOn ? t('activo') : t('iniciar'), gx + gw - 34, y + 88);
        c.restore();
        y += 198;
      }
    }
    /* r70 · FASE 164 · PERFIL Y EXTRAS DE ENTRENAMIENTO (página trainext,
     *  destino de la tarjeta «Perfil y extras» del landing REJILLA): el
     *  chip de perfil (puntos, nivel, progreso, LOGROS), las ayudas
     *  visuales y las pieles de pala — lo que quedaba en el hub legado.
     *  FUERA «Volver al Hall» (petición del dueño: no tiene sentido
     *  dentro de Entrenar). La concha pinta ATRÁS sobre el bloque C. */
    function drawExtras(game, c, rects, btn, label) {
      LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
      // r84 · F180 · MIGRACIÓN al interior C del arco (la deuda r80):
      // chip de perfil, ayudas visuales y pieles NATIVOS a banda completa
      // de la panela C (gx/gw como _menuBandas) — fuera espacio legado,
      // placa y escala. El botón PARAR, que antes pintaba a y=1380 legado
      // (fuera de banda), ahora vive DENTRO del lienzo visible.
      game._menuMap = null;
      const pC = CONFIG_MENUS.arco.panelas.find((p) => p.id === 'C');
      const gx = pC.x + 80, gw = pC.w - 160;
      // — chip de perfil: puntos · nivel —
      const lvl = levelOf(S.pts);
      c.textAlign = 'left'; c.textBaseline = 'middle';
      c.fillStyle = '#f0c85a'; c.font = '900 58px system-ui, sans-serif';
      c.fillText(S.pts + ' ' + t('pts'), gx + 8, 316);
      c.fillStyle = '#a9b8cc'; c.font = '600 24px system-ui, sans-serif';
      c.fillText(t('nivel') + ' · ' + t(lvl.k), gx + 8, 364);
      // progreso al siguiente nivel + LOGROS n/9 (v3.0.7-PLAY1)
      if (GAMF()) {
        const li = LEVELS.indexOf(lvl), nx = LEVELS[li + 1] || null;
        const bw = 460, bx = gx + 8, by = 404;
        const prog = nx ? Math.min(1, (S.pts - lvl.min) / (nx.min - lvl.min)) : 1;
        c.fillStyle = 'rgba(255,255,255,0.14)';
        c.fillRect(bx, by, bw, 8);
        c.fillStyle = nx ? '#f0c85a' : '#68d391';
        c.fillRect(bx, by, Math.max(4, bw * prog), 8);
        c.font = '600 17px system-ui, sans-serif';
        c.fillStyle = '#a9b8cc';
        c.fillText(nx ? (S.pts + ' / ' + nx.min) : t('max'), bx + bw + 14, by + 5);
        const got = ACHS.filter((a2) => S.ach[a2]).length;
        c.font = '700 17px system-ui, sans-serif';
        c.fillText(t('logros') + ' ' + got + '/' + ACHS.length, bx, by + 34);
        for (let i = 0; i < ACHS.length; i++) {
          const cx = bx + i * 30;
          c.beginPath(); c.arc(cx, by + 62, 7, 0, Math.PI * 2);
          c.fillStyle = S.ach[ACHS[i]] ? '#f0c85a' : 'rgba(255,255,255,0.16)';
          c.fill();
        }
      }
      // — ayudas visuales (fb toggles, ids intactos) —
      // r84 · etiqueta de sección NATIVA: el helper label() del dispatcher
      // es LEGADO (firma (txt, y, size) y x fijo 56) — llamada como
      // (txt, x, y) pintaba «TECH AIDS» a 500 px en el centro del lienzo
      c.fillStyle = '#a9b8cc';
      c.font = '700 22px system-ui, sans-serif';
      c.textAlign = 'left';
      c.textBaseline = 'middle';
      c.fillText(t('fb_t'), gx + 8, 500);
      const toggles = [['marks', t('fb_marks')], ['line', t('fb_line')],
        ['spin', t('fb_spin')]];
      const wT = Math.floor((gw - 34) / 3);
      let tx2 = gx;
      for (const [k, lbl] of toggles) {
        btn('trv3:fb:' + k, tx2, 522, wT, 72, lbl, !!S.fb[k],
          undefined, !!S.fb[k], 22);
        tx2 += wT + 17;
      }
      // — pieles de pala (tarjetas miniatura, ahora a lo ancho de la C) —
      c.fillStyle = '#a9b8cc';
      c.fillText(t('skins_t'), gx + 8, 636);
      const wS = 180, hS = 92, pasoS = 208;   // 6 por fila (6×208 ≤ gw)
      let sx = gx, sy = 664;
      for (const sk of SKINS) {
        if (sk.via === 'racha') continue;   // r76: las de asistencia en EL PULSO
        if (sx + wS > gx + gw) { sx = gx; sy += hS + 16; }
        const un = S.unlocked.indexOf(sk.id) >= 0;
        const idb = 'trv3:skin:' + sk.id;
        const idx = rects.length;
        btn(idb, sx, sy, wS, hS, '', false);
        c.save();
        c.beginPath();
        if (c.roundRect) c.roundRect(sx, sy, wS, hS, 14); else c.rect(sx, sy, wS, hS);
        c.fillStyle = S.skin === sk.id ? 'rgba(240,200,90,0.30)' : 'rgba(255,255,255,0.06)';
        c.fill();
        c.strokeStyle = S.skin === sk.id ? '#f0c85a' : (un ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.15)');
        c.lineWidth = S.skin === sk.id ? 4 : 2;
        c.stroke();
        c.beginPath(); c.arc(sx + 36, sy + hS / 2, 26, 0, Math.PI * 2);
        c.fillStyle = un ? 'rgba(255,255,255,0.92)' : 'rgba(255,255,255,0.12)';
        c.fill();
        c.strokeStyle = 'rgba(255,255,255,0.5)'; c.lineWidth = 2; c.stroke();
        if (un) {
          c.save();
          c.beginPath(); c.arc(sx + 36, sy + hS / 2, 24, 0, Math.PI * 2); c.clip();
          c.drawImage(skinPreviewCv(sk), sx + 14, sy + 24, 44, 44);
          c.restore();
        }
        c.fillStyle = un ? '#e9edf2' : '#5a6a7d';
        const nmFull = un ? (sk.name[LANG] || sk.name.es) : '\u{1F512} ' + sk.min;
        let nm = nmFull;
        c.font = '700 17px system-ui, sans-serif'; c.textAlign = 'left'; c.textBaseline = 'middle';
        while (nm.length > 2 && c.measureText(nm).width > wS - 70) {
          nm = nm.slice(0, -1);
        }
        c.fillText(nm, sx + 70, sy + hS / 2 - 12);
        if (un && S.skin === sk.id) {
          c.fillStyle = '#f0c85a'; c.font = '600 13px system-ui, sans-serif';
          c.fillText(t('skin_sel'), sx + 70, sy + hS / 2 + 14);
        }
        c.restore();
        sx += pasoS;
      }
      // r70 · parar la prueba activa (si la hay) — sin HALL aquí
      if (active) {
        btn('trv3:stop', gx, 1140, gw, 76, t('parar'), false, 'surv',
          undefined, 28);
      }
    }
    /* ---------------- acciones del menú (case 'trv3') ---------------- */
    function menuAction(game, arg) {
      const p = arg.split(':');
      const cmd = p[0];
      if (cmd === 'area') { uiArea = p[1] || 'dir'; uiPage = 'area'; game._trainSel = p[1] || 'dir'; game.menuPage = 'trainarea'; game.drawMenu(); }
      else if (cmd === 'back') {
        // v3.0.3 · «VOLVER» desde un área regresa al HUB de entrenamiento
        // (antes: menú principal); el «MENÚ» de la cabecera, en el hub, sí
        // lleva al menú principal.
        game.menuPage = (game.menuPage === 'trainarea') ? 'train' : 'main';
        game.drawMenu();
      }
      else if (cmd === 'start') {
        game.closeMenu();
        startMode(game, p[1]);
      }
      else if (cmd === 'calib') { game.closeMenu(); startCalib(game); }
      else if (cmd === 'stop') {
        // v3.0.3 · parar una prueba devuelve al HUB de entrenamiento (no al
        // menú principal): seguido se encadena otra prueba.
        stopMode(game);
        game.menuPage = 'train';
        game.drawMenu();
      }
      else if (cmd === 'skin') { applySkin(p[1]); game.drawMenu(); }
      else if (cmd === 'daily') {
        // r76 · EL PULSO CRAZY: la tarjeta arranca el modo del día (si ya
        // está cobrado hoy, entrenar es gratis — la recompensa no se repite)
        // r80 · mismas zonas permisivas que el botón de la puerta
        game.closeMenu();
        startMode(game, dailyPlan(dayKey()).mode, { daily: 1 });
      }
      else if (cmd === 'semana') {
        // M4 (r118) · RETO DE LA SEMANA: mismo camino que el diario con
        // SU plan de septana — el cobro va a weeklyComplete (insignia).
        game.closeMenu();
        startMode(game, weeklyPlan(weekKey()).mode, { daily: 1, weekly: 1 });
      }
      else if (cmd === 'fb') {
        S.fb[p[1]] = S.fb[p[1]] ? 0 : 1; save();
        // ronda 27 (informe del dueño) · OBEDIENCIA INMEDIATA: al desmarcar
        // una ayuda, lo YA DIBUJADO se retira al momento. Antes las marcas
        // vivían hasta 1,6 s y la línea hasta ~1,7 s desvaneciéndose (y los
        // iconos de la pala ni siquiera consultaban la bandera): el jugador
        // desmarcaba y seguía viéndolas — «sólo hace caso la línea de tiro».
        if (!S.fb.marks) for (const m of marks) { m.userData.ttl = 0; m.visible = false; }
        if (!S.fb.line && shotLine) { shotTtl = 0; shotLine.visible = false; }
        if (!S.fb.spin) {
          if (spinSprite) { spinSprite.material.opacity = 0; spinSprite.visible = false; }
          st.spinIconT = 0;
          for (const s of faceIcons) { s.material.opacity = 0; s.visible = false; }
          // las pistas de goma de la DOBLE GOMA no son feedback de efecto:
          // updateFaceHints las restaura (identificación de la piel, v3.0.5)
          updateFaceHints();
        }
        game.drawMenu();
      }
    }
  
    /* ---------------- tick público ---------------- */
    function tick(dt) {
      if (!G) {
        const g = (typeof window !== 'undefined') ? window.__PP_GAME : null;
        if (!g) return;
        G = g;
        buildScene();
        applySkin(S.skin);
        buildFaceIcons();
        //Lang persistente
        LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
      }
      if (!G || G.disposed) return;
      try {
        cosmeticsTick(dt);
        burstTick(dt);
        if (active && G.trainV3 && G.calib) trainTick(dt);
        // r101 · mandos de la BARRA del pase bajo (t2a): la mano libre cerca
        // de la cinta la agarra (≥0,3 s) y la barra sigue su altura — sin gatillo
        barraTick(dt);
        // detección de efecto del jugador en CUALQUIER modo (iconos en caras)
        // ronda 27 · respeta también el interruptor «Flecha de efecto»
        if (S.fb.spin && faceIcons.length && G.events && G.events.length) {
          for (const ev of G.events) {
            if (ev.type === 'paddle' && ev.who === 'player' && G.ball && G.ball.spin &&
                G.ball.spin.lengthSq() > 330) {
              const lift = G.ball.spin.z * G.ball.vel.x - G.ball.spin.x * G.ball.vel.z;
              pulseFaceIcons(lift);
              break;
            }
          }
        }
      } catch (e) {
        // el módulo NUNCA rompe el bucle del juego — pero el error queda
        // visible para depurar (window.__PP_TRAIN_DEBUG = true)
        if (typeof window !== 'undefined' && window.__PP_TRAIN_DEBUG) {
          console.warn('[PP_TRAIN tick]', e && e.stack || e);
        }
      }
    }
  
    return {
      tick, startMode, stopMode, startCalib, menuAction, applySkin, teardown,
      // r80 · EL RETO DIARIO EN LA PUERTA: el botón estrella del menú
      // principal (c12 _retoDiarioCard) arranca el duelo de hoy con las
      // zonas el doble de anchas sin pasar por el hub de entrenamiento
      startDaily: (g) => {
        if (!g) return;
        g.closeMenu();
        startMode(g, dailyPlan(dayKey()).mode, { daily: 1 });
      },
      // M4 (r118) · RETO DE LA SEMANA: arranque desde cualquier llamada
      // externa (futuro botón estrella en la puerta si el dueño lo pide)
      startWeekly: (g) => {
        if (!g) return;
        g.closeMenu();
        startMode(g, weeklyPlan(weekKey()).mode, { daily: 1, weekly: 1 });
      },
      serveTrigger: () => { try { serveTossFromTee(true); } catch (e) { /* nunca rompe */ } },
      serveRelease: (i) => { try { if (G && i === G.ballHand) serveTossFromTee(false); } catch (e) { /* nunca rompe */ } },
      // r105 · FÍSICA IDÉNTICA (informe del dueño): el núcleo pregunta si el
      // módulo tiene la bola EN CINEMÁTICA (fase tee: bola en la mano libre).
      // Con true, c12 no integra la bola — la MISMA cinemática del saque en
      // partido (holdLock): sin captura del carry, sin peleas de amos.
      ballHeld: () => st.phase === 'tee',
      drawHub, drawArea,
      // r70 · puentes de la landing REJILLA de Entrenar: traductor local,
      // área por id, sub del reto semanal, sub del perfil y la página de
      // perfil/extras (trainext)
      tx: t,
      drawExtras,
      areaDe: (id) => AREAS.find((a) => a.id === id) || null,
      semanaSub: () => {
        const wp = weeklyPlan(weekKey());
        const hecho = !!(S.semana.done && S.semana.done[weekKey()]);
        return t('semana_sub', { m: t(MODES[wp.mode].nk), n: wp.n }) +
          (hecho ? ' · ' + t('semana_ya') : '');
      },
      perfilSub: () => {
        const lvl = levelOf(S.pts);
        return S.pts + ' ' + t('pts') + ' · ' + t('nivel') + ' · ' + t(lvl.k);
      },
      get state() { return { active, pts: S.pts, best: S.best, skin: S.skin, unlocked: S.unlocked.slice(),
        stars: Object.assign({}, S.stars), acc: Object.assign({}, S.acc),
        ach: Object.assign({}, S.ach), comboBest: S.comboBest || 0,
        round: { hits: st.roundHits, faults: st.roundFaults },
        daily: (function () { const _pD = dailyPlan(dayKey());
          return { last: S.daily.last, streak: S.daily.streak, bestStreak: S.daily.bestStreak,
            hoy: (S.daily.done && S.daily.done[dayKey()]) ? 1 : 0,
            modo: _pD.mode, modoName: t(MODES[_pD.mode].nk) }; })(),
        // r118 · RETO DE LA SEMANA: insignias, estado de la septana y plan
        semana: (function () { const _pW = weeklyPlan(weekKey());
          return { bad: S.semana.bad,
            hecho: (S.semana.done && S.semana.done[weekKey()]) ? 1 : 0,
            modo: _pW.mode, n: _pW.n }; })() }; },
      __debug: { S, st, MODES, PLAN_POOL },   /* M7d (r120): PLAN_POOL visible */
    __test: { okHit, failHit, judgeAiBounce, modeFeed, pickTarget, serveTee, drawQuad, drawPanel, serveAssist,
      // M7d (r120) · medallas por ejercicio + juez REAL sintético + dims
      // de mesa (HW/HL/C/TOP) + apagado limpio y estado del modo activo
      medallaDe, qaJudge, qaOff, activo: () => active,
      trainDims: () => ({ HW: HW(), HL: HL(), C: C(), TOP: TOP() }),
      checkGlobalAch,
      // r76 · EL PULSO CRAZY: internos expuestos para la QA (qa_r76_v3668)
      dayKey, dailyPlan, dailyTip, dailyComplete, effStreak, seedOf,
      // r118 · RETO DE LA SEMANA: internos para la QA (qa_r118_dirigida)
      weekKey, weeklyPlan, weeklyComplete, weeklySub,
      // r80 · EL RETO PERMISIVO: las dimensiones de zona compartidas por
      // pintor y juez (la QA verifica el doble en el reto y la igualdad
      // byte a byte en entrenamiento)
      zonaDims,
      // ronda 27 · internos de las AYUDAS TÉCNICAS (QA qa_train_ayudas):
      // accesores —nunca sustituciones— para verificar por GPU que cada
      // interruptor de la sección «AYUDAS TÉCNICAS» obedece de verdad.
      spawnMark, pulseFaceIcons, shotLineShow,
      marks: () => marks, spinSprite: () => spinSprite, shotLine: () => shotLine,
      faceIcons: () => faceIcons,
      // r101 · internos de la BARRA del pase bajo (qa_r101_v3693): accesores
      // —nunca sustituciones— de la altura viva, la lectura en cm, el estado
      // del agarre por proximidad y los mandos (flechas + rótulo + recolocación)
      barraH: () => barraH,
      barraCm: () => BARRA_CM(),
      barraEstado: () => ({ zona: barraZona, agarrada: barraAgarrada }),
      barraUpdate,
      barraStick,                                          // r102: máquina joystick
      barraStickEstado: () => ({ acc: barraStickAcc, avisado: barraAvisoHecho }),
      barraEtiquetaZ: () => (barraLbl
        ? barraLbl.position.z + (ribbonG ? ribbonG.position.z : 0) : 0),  // z MUNDO
      barraVisSet: (v) => { if (ribbonG) ribbonG.visible = !!v; },   // QA: estado t2a
      barraAjustar,
      barraLay,
      barraSpr: () => ({
        up: barraUp ? { x: barraUp.position.x, y: barraUp.position.y } : null,
        lbl: barraLbl ? { x: barraLbl.position.x, y: barraLbl.position.y } : null,
        dn: barraDn ? { x: barraDn.position.x, y: barraDn.position.y } : null,
        cinta: barraRibbon ? { band: barraRibbon.band.position.y } : null,
        grupo: ribbonG ? ribbonG.position.z : null,
      }),
      // r103 · QA: los mandos son MALLAS DE ORIENTACIÓN FIJA (isMesh, jamás
      // sprites) y el rótulo viaja con la cinta (delta y constante +0,075)
      barraFijo: () => ({
        lblMesh: barraLbl ? !!barraLbl.isMesh : null,
        upMesh: barraUp ? !!barraUp.isMesh : null,
        dnMesh: barraDn ? !!barraDn.isMesh : null,
        lblX: barraLbl ? barraLbl.position.x : null,
        lblYRel: (barraLbl && barraRibbon)
          ? Math.round((barraLbl.position.y - barraRibbon.band.position.y) * 1000) / 1000
          : null,
      }) },

    };
  })();
  window.__PP_TRAIN = PP_TRAIN;
  

  renderPlayBtn();

  // Compatibilidad WebXR (estado bajo el gran botón de la portada)
  let lastStatusKey = 'status_vr_checking';
  const setStatusKey = (k) => { lastStatusKey = k; statusEl.textContent = T(k); };
  let xrOK = false;
  if (navigator.xr && navigator.xr.isSessionSupported) {
    navigator.xr.isSessionSupported('immersive-vr')
      .then((ok) => {
        xrOK = ok;
        setStatusKey(ok ? 'status_vr_ok' : 'status_no_vr');
      })
      .catch(() => {
        setStatusKey('status_no_webxr');
      });
    if (arBtn) {
      navigator.xr.isSessionSupported('immersive-ar')
        .then((ok) => { arBtn.disabled = !ok; })
        .catch(() => { arBtn.disabled = true; });
    }
  } else {
    setStatusKey('status_no_2d');
  }

  // GRAN BOTÓN CARTOON (v2.28): entra en VR directamente. Sin visor avisa y
  // deja el modo demo al alcance (enlace discreto del pie de portada).
  vrbtn.addEventListener('click', () => {
    game.audio.ensure();
    if (!navigator.xr || !navigator.xr.isSessionSupported) {
      setStatusKey('status_no_vr');
      return;
    }
    if (!xrOK) { setStatusKey('status_no_vr'); return; }
    setStatusKey('status_starting_vr');
    // v3.6.42 · el conmutador de passthrough (AJUSTES en VR) persiste —
    // por defecto DESACTIVADO; JUGAR respeta lo que el dueño dejó fijado.
    let arPref = false;
    try { arPref = localStorage.getItem('ppxr_pending_ar') === '1'; } catch { /* */ }
    game.enterVR(false, arPref)
      .catch((err) => {
        statusEl.textContent = '⚠️ ' + (err?.message || T('status_vr_fail'));
      });
  });

  // PASSTHROUGH: juega en TU habitación real (enlace discreto del pie)
  if (arBtn) {
    arBtn.addEventListener('click', () => {
      if (arBtn.disabled) return;
      // v3.6.42 · fija el pref del conmutador (coherente con AJUSTES en VR)
      try { localStorage.setItem('ppxr_pending_ar', '1'); } catch { /* */ }
      game.pendingAR = true;
      setStatusKey('status_starting_ar');
      game.enterVR(false, true)
        .catch((err) => {
          statusEl.textContent = '⚠️ ' + (err?.message || T('status_ar_fail'));
        });
    });
  }

  // v2.27 · SELECTOR DE IDIOMA (palas con bandera de la portada + menú VR)
  document.querySelectorAll('[data-lang]').forEach((b) => {
    b.addEventListener('click', () => setLang(b.dataset.lang, game));
  });
  document.addEventListener('pp-lang', () => {
    renderPlayBtn();
    statusEl.textContent = T(lastStatusKey);
  });

  /* =====================================================================
   *  v2.68 · RANKING MUNDIAL EN LA PORTADA 2D (antes de entrar en VR)
   *  ---------------------------------------------------------------------
   *  El artista pidió ver el ranking mundial DESDE LA PÁGINA PRINCIPAL.
   *  Reutiliza el MISMO almacén y saneado que el menú VR (WORLDRANK =
   *  window.__PP_WORLD) y el MISMO paquete de textos i18n, así que:
   *   - la lista de campeonatos sale del índice championships.json (la
   *     misma que ChampLoader ya fetch-ea; si aún no acabó, se reintenta
   *     al abrir el panel),
   *   - offline sirve la caché local («últimos datos»),
   *   - la fila del jugador se resalta con TÚ igual que en VR.
   *  Nada de esto toca el juego: es DOM puro de la portada.
   *  ===================================================================== */
  const wrlov = document.getElementById('wrlov');
  const wrlsel = document.getElementById('wrlsel');
  const wrlbody = document.getElementById('wrlbody');
  const wrlstat = document.getElementById('wrlstat');
  const wrlthPts = document.getElementById('wrlthPts');
  const wrlcloseBtn = document.getElementById('wrlclose');
  const wrlrefBtn = document.getElementById('wrlref');
  const wrlBtn2D = document.getElementById('wrlbtn');

  /** Desplegable: La Locura primero + campeonatos externos descubiertos. */
  const wrlFillSelect = () => {
    const prev = wrlsel.value;
    const opts = ['locura'].concat(
      (game.champs && game.champs.list ? game.champs.list() : []).map((c) => c.id),
    ).filter((v, i, a) => a.indexOf(v) === i);
    wrlsel.innerHTML = '';
    for (const id of opts) {
      const o = document.createElement('option');
      o.value = id;
      let name;
      if (id === 'locura') name = T('arc_title');
      else {
        const ch = (game.champs && game.champs.list ? game.champs.list() : [])
          .find((x) => x.id === id);
        name = ch ? String(ch.label).replace(/^▶\s*/, '') : String(id).toUpperCase();
      }
      o.textContent = name;
      wrlsel.appendChild(o);
    }
    // conserva la elección previa si sigue existiendo
    if (opts.indexOf(prev) >= 0) wrlsel.value = prev;
  };

  /** Pinta la tabla top 10 del campeonato elegido. */
  const wrlRender2D = () => {
    const champ = wrlsel.value || 'locura';
    // cabecera de puntos: VICTORIAS en La Locura, PUNTOS en el resto
    // v2.70: VICTORIAS en todos los campeonatos
    wrlthPts.textContent = T('wrl_wins');
    const rows = WORLDRANK.list(champ).slice(0, 10);
    const me = (ppPlayerName() || '').toLowerCase();
    wrlbody.innerHTML = '';
    if (!rows.length) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 4;
      td.className = 'wrlnone';
      td.textContent = WORLDRANK.status === 'loading' ? T('wrl_loading') : '· · ·';
      tr.appendChild(td);
      wrlbody.appendChild(tr);
    } else {
      rows.forEach((e, i) => {
        const tr = document.createElement('tr');
        if (me && e.n.toLowerCase() === me) tr.className = 'me';
        const mk = (txt) => {
          const td = document.createElement('td');
          td.textContent = txt;
          return td;
        };
        tr.appendChild(mk(String(i + 1)));
        const nm = mk(e.n.length > 15 ? e.n.slice(0, 14) + '…' : e.n);
        if (me && e.n.toLowerCase() === me) {
          const tag = document.createElement('span');
          tag.className = 'meTag';
          tag.textContent = T('wrl_you');
          nm.appendChild(tag);
        }
        tr.appendChild(nm);
        tr.appendChild(mk(String(e.p)));
        // v2.128: la INSIGNIA del campeonato como LOGRO en la portada
        const tdA = document.createElement('td');
        if (e.a === '🏆') {
          const b = window.__PP_WRL_BADGE ? window.__PP_WRL_BADGE(champ) : null;
          if (b && b.complete && b.naturalWidth) {
            const im = document.createElement('img');
            im.src = b.src;
            im.className = 'wrlogro';
            im.alt = '🏆';
            tdA.appendChild(im);
          } else tdA.textContent = '🏆';
        } else tdA.textContent = e.a || '·';
        tr.appendChild(tdA);
        wrlbody.appendChild(tr);
      });
    }
    // estado de conexión (misma clave i18n que el menú VR)
    wrlstat.textContent = WORLDRANK.status === 'online' ? T('wrl_online')
      : WORLDRANK.status === 'offline' ? T('wrl_offline') : T('wrl_loading');
  };

  /** Abre el panel, rellena el desplegable y revalida contra el almacén. */
  const wrlOpen = () => {
    wrlFillSelect();
    wrlov.classList.add('open');
    wrlRender2D();
    WORLDRANK.load(true)
      .then(() => { if (wrlov.classList.contains('open')) wrlRender2D(); })
      .catch(() => { wrlRender2D(); });   // offline: sirve la caché igualmente
  };
  const wrlClose = () => { wrlov.classList.remove('open'); };

  if (wrlBtn2D && wrlov) {
    wrlBtn2D.addEventListener('click', wrlOpen);
    wrlcloseBtn.addEventListener('click', wrlClose);
    wrlrefBtn.addEventListener('click', () => {
      WORLDRANK.load(true)
        .then(() => { if (wrlov.classList.contains('open')) wrlRender2D(); })
        .catch(() => { wrlRender2D(); });
    });
    wrlsel.addEventListener('change', wrlRender2D);
    wrlov.addEventListener('click', (ev) => { if (ev.target === wrlov) wrlClose(); });
    document.addEventListener('keydown', (ev) => {
      if (ev.key === 'Escape' && wrlov.classList.contains('open')) wrlClose();
    });
    document.addEventListener('pp-lang', wrlRender2D);   // repinta con el idioma vivo
    // calienta la caché al cargar la portada (igual que hace el menú VR)
    WORLDRANK.load(false).catch(() => { /* nunca rompe la portada */ });
  }

  /* =====================================================================
   *  r109 · M3 PWA INSTALABLE (roadmap MEJORAS.md) — la portada se vuelve
   *  instaladora: registra el service worker, detecta standalone, captura
   *  beforeinstallprompt y enseña el camino manual si el navegador no
   *  dispara el diálogo. Cero juego: DOM puro + telemetría anónima.
   *  ===================================================================== */
  const pwaSt = { standalone: false, prompt: null, registered: false };
  try {
    window.__ppPwa = pwaSt;   // gancho de QA (qa_r109)
  } catch (e0) { /* */ }

  // (1) registro del service worker — sólo en contexto seguro (o localhost
  // para pruebas): en file:// no existe y en http:// simple se ignora en paz.
  try {
    const swOk = 'serviceWorker' in navigator &&
      (location.protocol === 'https:' || ['localhost', '127.0.0.1'].includes(location.hostname));
    if (swOk) {
      navigator.serviceWorker.register('sw.js', { scope: './' })
        .then(() => { pwaSt.registered = true; })
        .catch(() => { pwaSt.registered = false; });   // nunca rompe la portada
    }
  } catch (e1) { /* */ }

  // (2) detección de standalone: la app YA está instalada (arrancada desde
  // el icono). Oculta el botón y avisa una vez a telemetría.
  try {
    pwaSt.standalone = window.matchMedia('(display-mode: fullscreen)').matches ||
      window.matchMedia('(display-mode: standalone)').matches ||
      window.matchMedia('(display-mode: minimal-ui)').matches ||
      window.navigator.standalone === true;
    if (pwaSt.standalone) {
      const pb0 = document.getElementById('pwabtn');
      if (pb0) pb0.style.display = 'none';
      try { if (window.__PP_TELE) window.__PP_TELE.ev('pwa_standalone', {}); } catch (e2) { /* */ }
    }
  } catch (e3) { /* */ }

  // (3) toast discreto de la portada (mismo idioma vivo que el resto)
  let ppToastEl = null, ppToastTmr = 0;
  const ppToast = (html, ms) => {
    try {
      if (!ppToastEl) {
        ppToastEl = document.createElement('div');
        ppToastEl.id = 'ppToast';
        const ov = document.getElementById('overlay');
        (ov || document.body).appendChild(ppToastEl);
      }
      ppToastEl.innerHTML = html;
      ppToastEl.classList.add('show');
      if (ppToastTmr) clearTimeout(ppToastTmr);
      ppToastTmr = setTimeout(() => { if (ppToastEl) ppToastEl.classList.remove('show'); }, ms || 9000);
    } catch (e4) { /* */ }
  };
  window.__ppPwaToast = ppToast;   // reutilizable (M4 onboarding)

  // (4) botón INSTALAR EN EL CASCO: diálogo nativo si lo hay, manual si no.
  const pwaBtn = document.getElementById('pwabtn');
  try {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();               // el diálogo lo manda NUESTRO botón
      pwaSt.prompt = e;
      if (pwaBtn) pwaBtn.classList.add('pwaOn');
    });
    window.addEventListener('appinstalled', () => {
      pwaSt.prompt = null;
      if (pwaBtn) pwaBtn.style.display = 'none';
      ppToast(T('pwa_installed'), 8000);
      try { if (window.__PP_TELE) window.__PP_TELE.ev('pwa_installed', {}); } catch (e5) { /* */ }
    });
  } catch (e6) { /* */ }
  if (pwaBtn && !pwaSt.standalone) {
    pwaBtn.addEventListener('click', () => {
      const ev0 = pwaSt.prompt;
      if (ev0 && typeof ev0.prompt === 'function') {
        ev0.prompt();
        ev0.userChoice && ev0.userChoice.then((r) => {
          try { if (window.__PP_TELE) window.__PP_TELE.ev('pwa_prompt', { o: String(r && r.outcome || '?') }); } catch (e7) { /* */ }
          if (r && r.outcome === 'accepted') { pwaSt.prompt = null; pwaBtn.style.display = 'none'; }
        }).catch(() => { /* */ });
      } else {
        // Sin evento nativo (Quest Browser puede no dispararlo): caminito
        // manual — el toast enseña los 2 toques del menú del navegador.
        ppToast(T('pwa_manual'), 11000);
        try { if (window.__PP_TELE) window.__PP_TELE.ev('pwa_manual_hint', {}); } catch (e8) { /* */ }
      }
    });
  }

  applyLangDOM();   // primera pintura de la portada en el idioma guardado
});

// v2.30: eliminados los listeners de la demo (#spectate) y del HUD — ya no existen.

/* =====================================================================
 *  v2.53 · PUENTE PARA CAMPEONATOS EXTERNOS (window.__PP_CORE)
 *  ---------------------------------------------------------------------
 *  El juego vive en un <script type="module">: sus constantes y funciones
 *  (THREE, DIMS, stepPhysics, T…) NO son visibles desde los módulos de
 *  las carpetas championships/<id>/. Este puente expone SÓLO LECTURA de
 *  las primitivas que un clon de La Locura necesita — ES ADITIVO: no
 *  cambia ni una línea de comportamiento del juego. Los módulos además
 *  importan 'three' por el importmap (misma instancia que el núcleo).
 *  ===================================================================== */
window.__PP_CORE = {
  DIMS,                        // dimensiones/física compartidas (objeto vivo)
  stepPhysics,                 // física real del ping-pong (con extra colliders)
  T,                           // traductor del núcleo (árbitro/mensajes)
  lang: () => __ppLang,        // idioma actual ('es'|'en')
  aiPresets: AI_PRESETS,       // presets de dificultad (para clonar escalado)
  scalePreset,                 // escalado de presets (mismo criterio que el core)
  ppPlayerName,                // v2.69: TU NOMBRE (lo usan los rankings de campeonatos)
  // v2.128 · INSIGNIA «¡CONSEGUIDO!» — un campeonato llama aquí al ganar
  // su duelo FINAL: panel GRANDE con la insignia del campeonato, texto
  // ¡CONSEGUIDO!, fanfarria y confeti. opts: { title, sub, msg, dur }.
  showChampConseguido(id, opts) {
    const G = (typeof window !== 'undefined') ? window.__game : null;
    if (G && typeof G.showChampConseguido === 'function') {
      try { G.showChampConseguido(id, opts); } catch (e) { /* nunca rompe */ }
    }
  },
  // v2.130 · INTRO DE CAMPEONATO (vídeo de la historia + botón JUGAR):
  // la lanza ChampLoader.launch(); los puentes sirven para QA/consola.
  showChampIntro(id) {
    const G = (typeof window !== 'undefined') ? window.__game : null;
    if (G && typeof G.showChampIntro === 'function') {
      try { G.showChampIntro(id); } catch (e) { /* nunca rompe */ }
    }
  },
  hideChampIntro(resume) {
    const G = (typeof window !== 'undefined') ? window.__game : null;
    if (G && typeof G.hideChampIntro === 'function') {
      try { G.hideChampIntro(resume); } catch (e) { /* nunca rompe */ }
    }
  },
};

/* =====================================================================
 *  v3.6.59 (ronda 67) · LA ACADEMIA EN TUS MANOS — r67 (V3.6.59)
 *  =====================================================================
 *  Informe del dueño tras V3.6.58, punto por punto:
 *  (1) «Siguen apareciendo solapes en los textos» → guion REORGANIZADO a
 *      9 pasos con layout estricto dentro de la zona negra + rejilla de
 *      modos 2×3 (antes dos pizarras) y textos cortos propios.
 *  (2) «El audio se superpone dos veces en varios momentos» → speakPlan
 *      (c03) CANCELA la voz anterior: una sola voz viva, la última gana
 *      (cierre de tutok→voz del paso siguiente, STICK y reintentos).
 *  (3) «Los mandos 3D que he subido que estén anclados a las manos reales
 *      y a los mandos reales, NO un modelo 3D moviéndose en el aire» →
 *      cada GLB vive DENTRO del espacio grip XR de SU mando (G.grips[h],
 *      seguido 1:1, orientación real: cabeza arriba, cara hacia delante,
 *      75% del tamaño r66). Sin giro, sin flotación, sin poses.
 *  (4) «que la raqueta fantasma también sea la que está real ya en nuestra
 *      mano y solo 1 raqueta no 2» → ADIÓS clones fantasma: una AURA
 *      dorada pulsa sobre la PALA REAL del juego (mismo paddleMount) en
 *      el momento «el mando es tu raqueta».
 *  (5) «piensa tú la mejor forma de explicarlo, muy sencilla y divertida»
 *      → guion de 9 pasos (antes 11): 0 bienvenida · 1 TU MANDO, TU
 *      RAQUETA (4 acciones + vaivén, fusionados) · 2 EL SAQUE (demo del
 *      PROFESOR sobre la mesa real con AROS GUÍA que se iluminan con los
 *      botes + 3 saques tuyos) · 3 el intercambio · 4 el marcador ·
 *      5 la práctica (6 devoluciones) · 6 botones · 7 los modos (UNA
 *      pizarra) · 8 ¡a jugar!.
 *  ---------------------------------------------------------------------
 *  v3.6.51 (ronda 59) · LA ACADEMIA — TUTORIAL INTERACTIVO DEL JUEGO
 *  =====================================================================
 *  Petición del dueño: «la gente entra, hay tanto menú y opciones que no
 *  saben ni cómo hacer para sacar». Respuesta: una academia guiada de
 *  LA ACADEMIA SOBRE LA MESA · r66 (V3.6.58) — informe del dueño tras
 *  V3.6.57: (1) «sigo escuchando un ruido molesto de bote continuo» → la
 *  bola queda DORMIDA (sin física, sin sonidos) en los pasos quietos
 *  (tutBolaViva en c12); (2) «las voces más pausadas y mejor entonación»
 *  → átomos Piper regenerados (length-scale 1,16 + respiros) y respiro
 *  entre átomos; (3) «el mando delante en el centro, y pongo AMBOS: el
 *  izquierdo (Y/X) y el derecho (B y A)» → DOS GLB reales centrados con
 *  anclas espejo; (4) «las zonas de los pulsadores menos transparentes y
 *  más fáciles de identificar» → halos opacos + ETIQUETA de la pieza;
 *  (5) «después de enseñar los mandos, una raqueta fantasma sobre ellos»
 *  → clon de la pala REAL con material aditivo; (6) «los textos se
 *  solapan» → pizarra re-espaciada; (7) «la simulación de reglas a una
 *  distancia sobre la mesa no tiene sentido: explícalo pausadamente
 *  SOBRE la mesa real» → paso 3 (saque demo REAL con los mandos + 3
 *  saques tuyos), paso 4 (intercambio REAL contra el rival hasta que
 *  falla + rotación cada 2 saques) y paso 5 (marcador BAJO sobre la mesa
 *  con saques reales: 11 por 2 y 10-10 cada punto), todo repetible y
 *  con confirmación por paso.
 *  11 PASOS sobre la MESA REAL (física de verdad, árbitro dormido en calib,
 *  IA dormida) con práctica en cada paso:
 *    0 bienvenida (voz) · 1 TUS MANDOS (2 GLB reales + 4 acciones reales
 *      + RAQUETA FANTASMA al dominarlos) · 2 LA PALA (vaivén)
 *    3 EL SAQUE (demo real sobre la mesa → 3 SAQUES válidos tuyos) ·
 *    4 EL INTERCAMBIO REAL (el rival devuelve hasta fallar; rotación) ·
 *    5 EL MARCADOR (11, +2 y 10-10 con saques reales en bucle) ·
 *    6 LAS DEVOLUCIONES (6 del profesor) · 7 BOTONES A/X (de verdad)
 *    8/9 LOS MODOS · 10 ¡YA SABES JUGAR!
 *  VOZ: cada paso narra al entrar (ES/EN según idioma, más pausada) y el
 *  STICK la repite. Cada paso exige SU acción — onboarding gamificado.
 *  r68 · LA RAQUETA DEL RIVAL: el profesor tiene PALA visible (la misma
 *  del juego) en el lado lejano — arma, barre y golpea la bola en su
 *  saque (demo y marcador) y en cada devolución (intercambio y
 *  práctica); los saques salen cuando la hoja pasa por la bola (adiós
 *  al golpe fantasma) y el paso 5 vuelve a tener rally (bola viva).
 *  Puertas de entrada: banner dorado del HUB · oferta de PRIMERA VEZ
 *  (pp_tut_asked, la escribe onSessionStart) · botón en AJUSTES.
 *  Salida: B o Y en cualquier momento → HALL + menú (sin «done»).
 *  ESTANQUEIDAD: no toca árbitro, IA ni marcador; el núcleo lo invoca vía
 *  game.tutV1 (guardias r59) + window.__PP_TUT.tick/onTrigger/drawAsk.
 *  ===================================================================== */
(function () {
  'use strict';
  if (typeof window === 'undefined' || window.__PP_TUT) return;

  const STEPS = 9;              // r67 · guion REORGANIZADO (0..8): menos pizarra, más mesa
  const SWAY_META = 0.55;       // segundos de vaivén firme (paso 1, raqueta)
  const SAQ_META = 3;           // r64 · saques válidos para superar el paso 2
  const DEVOL_META = 6;         // r64 · devoluciones para superar el paso 5
  const DEMO_MIN = 6;           // r65 · segundos de demo de reglas antes del OK
  const MANDO_ESC = 0.154;      // r67 · 75% del tamaño r66 (0.205): petición del dueño

  let G = null;                 // PingPongGame activo mientras dura la academia
  let active = false;
  let grp = null, cv = null, cc = null, tex = null, mesh = null;
  let anclados = null;          // r67 · mandos ANCLADOS a los grips reales
                                //        [{mano, mont, glb, halos}, ×2]
  let mandosVis = 0;            // r67 · opacidad del conjunto anclado (fade)
  let mandosVisMeta = 0;        // r67 · objetivo: 1 = en las manos · 0 = oculto
  let auraMats = null;          // r67 · auras de la pala REAL (UNA sola raqueta)
  let auraOp = 0;               // r67 · opacidad actual de la aura
  let auraMeta = 0;             // r67 · objetivo del fade de la aura
  let etiqueta = null;          // sprite-etiqueta (hija del mando de la pala)
  let etiquetaTxt = '';         // texto de la etiqueta ya pintado
  let mando = null;             // mando anclado de la mano ACTIVA (compat QA)
  let mandoSpin = null;         // grupo interior del mando activo (compat QA)
  let mandoT = 0;               // reloj (pulso de halos)
  let mandoMats = [];           // materiales de AMBOS GLB (fade + pulso)
  let halos = null;             // r67 · { pieza: [Sprite izq, Sprite der] }
  let hlParte = null;           // pieza resaltada ahora mismo
  let pizImg = null;            // r65 · imagen de la pizarra decodificada

  let step = 0;
  let subfase = 0;              // r65 · acción actual del paso 1 (0..4)
  let sway = 0;                 // progreso del paso 2 (vaivén de la pala)
  let demoT = 0;                // r65 · segundos de demo de reglas ya vistos
  let saqCount = 0;             // saques válidos del paso 5
  let saqLatch = false;         // el lanzamiento EN VUELO ya contó (1 vez)
  let saqBote1 = false;         // r70 · la bola YA BOTÓ en TU campo (saque válido)
  let saqBote2 = false;         // r70 · y DESPUÉS en el campo del rival
  let flashOk = 0;              // aviso verde «saque válido» (s restantes)
  let hitCount = 0;             // devoluciones del paso 6
  let aiReturned = false;       // el profesor ya devolvió ESTE vuelo
  let farBounced = false;       // la bola ya botó en el campo lejano (paso 6)
  let fase = 'espera_golpe';    // submáquina del paso 6
  let deadT = 0;                // bola muerta acumulada (paso 6, refeed)
  let flashAgain = 0;           // aviso «otra vez» del paso 5 (s restantes)
  let lastHand = -1;            // paso 7: mano al entrar
  let narrKeys = null;          // r65 · último plan de voz (stick = repetir)
  let narrRetry = 0;            // r65 · reintento si el banco aún decodifica
  let holo = null;              // r65 · grupo del holo-demo de reglas (escena)
  let holoT = 0;                // r65 · reloj del holo
  let holoPips = null;          // r65 · pips del marcador (paso 5)
  let holoGhost = null;         // r65 · bola fantasma (marcador)
  let holoTokens = null;        // r65 · fichas de saque (paso 5)
  let holoCartel2 = null;       // r66 · cartel secundario (+2 PARA GANAR)
  let submodo = 'demo';         // r66 · paso 3: 'demo' | 'practica'
  let demoFase = 0;             // r66 · fase del ciclo de demo (saque/marcador)
  let demoFaseT = 0;            // r66 · segundos en la fase actual
  let demoTxt = null;           // r66 · aviso transitorio del demo ({txt,col,t})
  let demoBote1 = false;        // r66 · la demo ya botó en campo propio
  let demoBote2 = false;        // r66 · la demo ya botó en campo rival
  let demoCiclos = 0;           // r66 · ejemplos completos vistos (paso 3)
  let demoPtos = 0;             // r66 · puntos anotados en el marcador (paso 5)
  let demoDeuce = false;        // r66 · el marcador llegó a 10-10 (paso 5)
  let rfFase = 'saque';         // r66 · paso 4: saque→vuelo→devolución→…
  let rfVueltas = 0;            // r66 · devoluciones ya hechas en el paso 4
  let rfHecho = false;          // r66 · el intercambio del paso 4 ya se ganó
  let rfVueltaVista = false;    // r66 · la devolución del rival ya se ejecutó
  const btn5Prev = [true, true]; // B/Y por mando (true = no saltar al entrar)
  const btn1Prev = [true, true]; // r65 · grip por mando (borde)
  const btn3Prev = [true, true]; // r65 · stick-click por mando (repetir voz)
  const btn4Prev = [true, true]; // r65 · A/X por mando (borde)
  let repaintT = 0;
  let raqGrp = null;            // r68 · LA RAQUETA DEL RIVAL (escena mundo)
  let raqVis = null;            // r68 · visual interior (pala del juego)
  let raqModo = 'oculta';       // r68 · oculta | reposo | prep | golpe
  let raqT = 0;                 // r68 · reloj del modo actual
  let raqDe = null;             // r68 · origen del golpe (al iniciarlo)
  let raqContacto = null;       // r68 · punto de contacto con la bola
  let raqMeta = null;           // r68 · punto de acompañamiento
  let feed5T = 0;               // r68 · cuenta atrás del saque del profesor (paso 5)
  let quieta5T = 0;             // r74 · vigía de la práctica: bola quieta sin progreso
  let auraGrp = null;           // r69 · el grupo de la aura (para DESMONTARLO de verdad)
  let devPend = 0;              // r69 · cuenta atrás del lanzamiento (golpe honesto)
  let devFin = null;            // r69 · destino del golpe pendiente ('fallo'|'ida'|'practica')
  let devVelFn = null;          // r69 · fábrica de la velocidad (desde la bola VIVA)
  const _cero = (typeof THREE !== 'undefined')
    ? new THREE.Vector3(0, 0, 0) : null;

  const g = () => (typeof window !== 'undefined' ? window.__game : null);

  /* ---- ASSETS r65 · mando GLB del dueño + pizarra (ficheros externos, C2 r129) */
  const TUT_MANDO_GLB = 'assets/externos/mando_izq.glb';   // C2 (r129): antes base64 embebido
  const TUT_MANDO_DER_GLB = 'assets/externos/mando_der.glb';   // C2 (r129): antes base64 embebido

/* r83 · LOS MISMOS MANDOS para el AJUSTE DE PALA: los GLB reales del
 * tutorial (izq Mando.glb · der mando_derecho.glb) expuestos para que el
 * núcleo monte la RÉPLICA 3D de referencia cuando el passthrough no está
 * disponible (fallback del ajuste en AJUSTES › PALA). */
if (typeof window !== 'undefined') {
  window.__PP_MANDO_GLB = { izq: TUT_MANDO_GLB, der: TUT_MANDO_DER_GLB };
}

  const TUT_PIZARRA = 'assets/externos/pizarra.webp';   // C2 (r129): antes base64 embebido

  /* ---------------- panel del tutorial (colgado del RIG) ------------- */
  function buildPanel() {
    if (grp || !G || !G.rig || typeof THREE === 'undefined') return;
    cv = document.createElement('canvas');
    // r65 · PIZARRA del dueño: canvas 1408×768 (resolución nativa de
    // Pizarra.png) y plano 1.24×0.6765 (misma proporción 1.833) — texto
    // estilo tiza SOBRE LA ZONA NEGRA (interior x 170..1190 · y 168..618),
    // con los stickers (birrete y pala) siempre visibles en las esquinas.
    cv.width = 1408; cv.height = 768;
    cc = cv.getContext('2d');
    tex = new THREE.CanvasTexture(cv);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;
    mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(1.24, 0.6765),
      new THREE.MeshBasicMaterial({
        map: tex, transparent: true, depthTest: false, depthWrite: false,
        side: THREE.DoubleSide,
      }),
    );
    mesh.renderOrder = 985;
    grp = new THREE.Group();
    grp.add(mesh);
    grp.position.set(0, 1.52, -0.86);   // delante del jugador, sobre la mesa
    grp.rotation.x = 0.05;
    grp.visible = false;
    G.rig.add(grp);
    asegurarPizarra();                  // r65 · decodifica la pizarra (webp)
    buildMandosAnclados();              // r67 · mandos GLB ANCLADOS a los grips
    buildRaqueta();                     // r68 · LA RAQUETA DEL RIVAL (escena)
  }
  /* decodifica Pizarra.png (webp embebido) para pintarla de fondo */
  function asegurarPizarra() {
    if (pizImg || !TUT_PIZARRA) return;
    try {
      const im = new Image();
      im.onload = () => { pizImg = im; if (active) paintStep(); };
      im.onerror = () => { pizImg = null; };
      im.src = TUT_PIZARRA;
    } catch (e) { /* sin pizarra: fondo oscuro de respaldo */ }
  }
  function teardownPanel() {
    try { if (grp && G && G.rig) G.rig.remove(grp);
          else if (grp && grp.parent) grp.parent.remove(grp); } catch (e) { /* */ }
    // r67 · los mandos ANCLADOS salen de los grips reales (cada mont es
    // hijo de G.grips[h] — desmontarlos NO toca la pala ni el mando XR)
    if (anclados && G && G.grips) {
      for (const a of anclados) {
        try { if (a && a.mont && a.mont.parent) a.mont.parent.remove(a.mont); }
        catch (e2) { /* */ }
      }
    }
    limpiarRaqueta();                   // r68 · la pala del rival sale con el guion
    limpiarAura();                      // r69 · la AURA sale del mount (adiós al halo fantasma)
    grp = null; cv = null; cc = null; tex = null; mesh = null;
    anclados = null; mando = null; mandoSpin = null;
    mandoMats = []; halos = null;
    auraMats = null; auraOp = 0; auraMeta = 0;
    mandosVis = 0; mandosVisMeta = 0;
    etiqueta = null; etiquetaTxt = '';
    hlParte = null;
    pizImg = null;
  }

  function rr(c, x, y, w, h, r) {
    c.beginPath();
    if (c.roundRect) { c.roundRect(x, y, w, h, r); return; }
    c.moveTo(x + r, y);
    c.arcTo(x + w, y, x + w, y + h, r);
    c.arcTo(x + w, y + h, x, y + h, r);
    c.arcTo(x, y + h, x, y, r);
    c.arcTo(x, y, x + w, y, r);
    c.closePath();
  }
  /* ---------- MANDOS GLB REALES del dueño (Touch Plus) · r66 ---------
   * «El mando que te he pasado corresponde con el izquierdo (botones Y y
   * X), así que te voy a pasar el derecho también (mando_derecho.glb, con
   * los botones B y A) para que pongas ambos en el tutorial. El mando
   * debería mostrarse delante en el centro en un punto de visión cómodo».
   * DOS modelos EXACTOS (izq Mando.glb · der mando_derecho.glb, meshes
   * fusionados) flotando CENTRADOS bajo la pizarra, con HALOS OPACOS por
   * pieza (anclas espejo verificadas por clustering geométrico) +
   * ETIQUETA de la pieza pedida + RAQUETA FANTASMA que aparece sobre
   * ellos («para asociar que el mando va a ser nuestra raqueta»).        */
  const ANCLAS_MANDO = {
    gatillo: [-0.0189, -0.021, 0.036],
    stick:   [0.0076, 0.0192, 0.0342],
    botones: [-0.004, 0.0162, 0.0219],
    grip:    [-0.0157, -0.0079, -0.0102],
  };
  /* El derecho es el ESPEJO geométrico del izquierdo (verificado por
   * clustering de vértices r66: cabeza X negada, mango simétrico). */
  const ANCLAS_MANDO_DER = {
    gatillo: [0.0189, -0.021, 0.036],
    stick:   [-0.0076, 0.0192, 0.0342],
    botones: [0.004, 0.0162, 0.0219],
    grip:    [0.0157, -0.0079, -0.0102],
  };
  function _haloTex() {
    const cvh = document.createElement('canvas');
    cvh.width = 64; cvh.height = 64;
    const g2 = cvh.getContext('2d');
    // r66 · núcleo OPACO (el dueño: «las zonas deben verse mejor, menos
    // transparentes y más fáciles de identificar»): disco blanco sólido
    // con borde ámbar grueso y halo corto.
    const rg = g2.createRadialGradient(32, 32, 1, 32, 32, 30);
    rg.addColorStop(0, 'rgba(255,255,255,1)');
    rg.addColorStop(0.42, 'rgba(255,214,90,0.98)');
    rg.addColorStop(0.72, 'rgba(255,180,40,0.55)');
    rg.addColorStop(1, 'rgba(255,180,40,0)');
    g2.fillStyle = rg;
    g2.fillRect(0, 0, 64, 64);
    const t = new THREE.CanvasTexture(cvh);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }
  /* etiqueta de la pieza pedida: píldora legible (fondo oscuro + borde
   * ámbar + texto blanco grande), billboard sobre el mando */
  function _etiquetaSprite() {
    const cvh = document.createElement('canvas');
    cvh.width = 512; cvh.height = 160;
    const t = new THREE.CanvasTexture(cvh);
    t.colorSpace = THREE.SRGBColorSpace;
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: t, transparent: true, opacity: 0, depthTest: false,
    }));
    sp.scale.set(0.30, 0.094, 1);
    sp.renderOrder = 996;
    sp.__cv = cvh;
    return sp;
  }
  function pintaEtiqueta(sp, txt) {
    if (!sp || sp.__txt === txt) return;
    sp.__txt = txt;
    const g2 = sp.__cv.getContext('2d');
    g2.clearRect(0, 0, 512, 160);
    g2.font = '800 58px system-ui, sans-serif';
    const w = Math.min(488, g2.measureText(txt).width + 56);
    g2.fillStyle = 'rgba(10,14,22,0.86)';
    g2.beginPath();
    if (g2.roundRect) g2.roundRect((512 - w) / 2, 26, w, 108, 34);
    else g2.rect((512 - w) / 2, 26, w, 108);
    g2.fill();
    g2.strokeStyle = 'rgba(255,210,87,0.95)';
    g2.lineWidth = 7;
    g2.stroke();
    g2.fillStyle = '#ffffff';
    g2.textAlign = 'center'; g2.textBaseline = 'middle';
    let s = 58;
    g2.font = '800 ' + s + 'px system-ui, sans-serif';
    while (s > 30 && g2.measureText(txt).width > w - 40) {
      s -= 2;
      g2.font = '800 ' + s + 'px system-ui, sans-serif';
    }
    g2.fillText(txt, 256, 82);
    sp.material.map.needsUpdate = true;
  }
  /* ---------- MANDOS GLB REALES · r67 · ANCLADOS A LAS MANOS ----------
   * El dueño tras V3.6.58: «Los mandos 3D que he subido que estén anclados
   * a las manos reales y a los mandos reales, NO un modelo 3D moviéndose en
   * el aire. Que parezca que los tenemos en las manos… y más pequeños,
   * como un 75% del tamaño actual». Cada GLB (izq Y/X · der B/A) vive DENTRO
   * del espacio grip de SU mando XR (G.grips[h]) — sigue la mano 1:1, con
   * la orientación EXACTA del mando real: cabeza (+Y del GLB) hacia arriba
   * del mango y cara (+Z del GLB) hacia delante (-Z del grip, giro 180°).
   * Los HALOS y la ETIQUETA viajan con el mando REAL: las explicaciones se
   * dan SOBRE lo que el jugador tiene en la mano.                       */
  function _montaMando(gltf, anclas, texHalo) {
    const modelo = gltf.scene;
    const box = new THREE.Box3().setFromObject(modelo);
    const cen = box.getCenter(new THREE.Vector3());
    const tam = box.getSize(new THREE.Vector3());
    const esc = MANDO_ESC / Math.max(tam.x, tam.y, tam.z, 0.01);
    modelo.position.sub(cen);
    modelo.scale.setScalar(esc);
    modelo.traverse((o) => {
      if (o.isMesh) {
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        for (const m of mats) {
          m.transparent = true;               // r67 · fade del conjunto
          m.emissive = new THREE.Color('#ffd257');
          m.emissiveIntensity = 0;
          mandoMats.push(m);
        }
      }
    });
    // giro 180°: la cara del GLB (+Z, stick/botones) mira hacia -Z del grip
    // (hacia delante, como el mando REAL en la mano) y la cabeza queda arriba
    const glb = new THREE.Group();
    glb.rotation.y = Math.PI;
    glb.add(modelo);
    // halos OPACOS sobre las piezas (anclas en espacio GLB, escaladas)
    const hs = {};
    for (const k in anclas) {
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({
        map: texHalo, color: 0xffd257, transparent: true,
        opacity: 0, depthTest: false, blending: THREE.AdditiveBlending,
      }));
      sp.position.fromArray(anclas[k]).multiplyScalar(esc * 1.12);
      sp.scale.setScalar(0.046);              // r67 · con el mando al 75%
      sp.renderOrder = 990;
      glb.add(sp);
      hs[k] = sp;
    }
    return { glb, esc, halos: hs };
  }
  function buildMandosAnclados() {
    if (anclados || !G || !G.grips || typeof THREE === 'undefined' ||
        !GLTFLoader || !TUT_MANDO_GLB || !TUT_MANDO_DER_GLB) return;
    try {
      const texHalo = _haloTex();
      etiqueta = _etiquetaSprite();
      etiqueta.material.opacity = 0;
      anclados = [];
      const defs = [
        { mano: 'left', bin: TUT_MANDO_GLB, anclas: ANCLAS_MANDO },
        { mano: 'right', bin: TUT_MANDO_DER_GLB, anclas: ANCLAS_MANDO_DER },
      ];
      for (let h = 0; h < 2; h++) {
        const def = defs.find((d) => d.mano === G.handOf[h]) || defs[h];
        const mont = new THREE.Group();
        mont.name = 'ppTutMando' + h;
        // el origen del grip queda dentro del mango: el centro del modelo
        // sube un pelín (la cabeza por encima de la palma, mango abajo)
        mont.position.set(0, 0.024, 0);
        try { G.grips[h].add(mont); } catch (eG) { continue; }
        const reg = { mano: h, mont, glb: null, halos: null, esc: MANDO_ESC };
        anclados.push(reg);
        fetch(def.bin)
          .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error('HTTP ' + r.status))))
          .then((buf) => {
            new GLTFLoader().parse(buf, '', (gltf) => {
              if (!anclados || anclados.indexOf(reg) < 0) return;
              const m = _montaMando(gltf, def.anclas, texHalo);
              mont.add(m.glb);
              reg.glb = m.glb; reg.halos = m.halos; reg.esc = m.esc;
              if (h === (G ? G.paddleHand : 1)) {
                mando = m.glb;                    // compat QA: mando de la pala
                mandoSpin = m.glb;
              }
              _recolocaEtiqueta();
            }, () => { /* sin GLB: el panel funciona igual */ });
          })
          .catch(() => { /* sin GLB: el panel funciona igual */ });
      }
      _ponAuraPala();
    } catch (e) { /* nunca rompe el arranque de la academia */ }
  }
  /* la ETIQUETA vive sobre el mando REAL de la mano de la pala */
  function _recolocaEtiqueta() {
    try {
      if (!etiqueta || !anclados || !G) return;
      const a = anclados[G.paddleHand] || anclados[0];
      if (a && etiqueta.parent !== a.mont) {
        if (etiqueta.parent) etiqueta.parent.remove(etiqueta);
        a.mont.add(etiqueta);
        etiqueta.position.set(0, MANDO_ESC * 0.92, 0);   // sobre la cabeza
      }
    } catch (e) { /* decorativo */ }
  }
  /* LA ÚNICA RAQUETA: la pala REAL que ya está en la mano (el dueño: «la
   * raqueta fantasma también sea la que está real ya en nuestra mano y solo
   * 1 raqueta no 2»). Sin clones: una AURA dorada sobre la hoja de la pala
   * del juego, montada en el MISMO paddleMount que la pala visual.       */
  function _ponAuraPala() {
    try {
      if (auraMats || !G || !G.paddleMounts || typeof THREE === 'undefined') return;
      const mount = G.paddleMounts[G.paddleHand];
      if (!mount) return;
      const texHalo = _haloTex();
      const mats = [];
      const grpA = new THREE.Group();
      grpA.name = 'ppTutAuraPala';
      for (const yy of [0.10, 0.17]) {
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({
          map: texHalo, color: 0xffd257, transparent: true,
          opacity: 0, depthTest: false, blending: THREE.AdditiveBlending,
        }));
        sp.position.set(0, yy, 0);
        sp.scale.setScalar(yy > 0.12 ? 0.24 : 0.18);   // halo grande en la hoja
        sp.renderOrder = 993;
        grpA.add(sp);
        mats.push(sp.material);
      }
      const viejo = mount.getObjectByName('ppTutAuraPala');
      if (viejo) { try { mount.remove(viejo); } catch (eV) { /* */ } }   // r69 · autocura
      mount.add(grpA);
      auraGrp = grpA;                    // r69 · referencia para DESMONTARLO
      auraMats = mats;
    } catch (e) { /* decorativo: sin aura todo sigue */ }
  }
  /* resalte por paso/subfase: ¿qué pieza menciona el guion ahora mismo? */
  function hlDePaso() {
    if (step === 1 && subfase < 4) {
      return ['gatillo', 'grip', 'stick', 'botones'][Math.min(subfase, 3)];
    }
    return null;
  }
  function txtDeEtiqueta(parte) {
    if (!parte) return '';
    if (parte === 'botones') {
      return T('tut_lab_btns_i') + '  ·  ' + T('tut_lab_btns_d');
    }
    return T('tut_lab_' + parte) || '';
  }
  /* r67 · tick de los mandos ANCLADOS: NADA de giro ni flotación (van
   * pegados a los mandos reales) — sólo fades, pulso de halos y etiqueta */
  function tickMandos(dt) {
    if (!G) return;
    mandoT += dt;
    const k = Math.min(1, dt * 4.5);
    mandosVis += (mandosVisMeta - mandosVis) * k;
    // fade de los GLB anclados (opacidad de TODOS sus materiales)
    for (const m of mandoMats) {
      try {
        m.opacity = mandosVis;
        m.emissiveIntensity = hlParte ? (0.16 + 0.1 * Math.sin(mandoT * 5)) : 0;
      } catch (e) { /* */ }
    }
    for (const a of (anclados || [])) {
      try { if (a.mont) a.mont.visible = mandosVis > 0.02; } catch (e) { /* */ }
    }
    // LA ÚNICA RAQUETA: aura sobre la pala real (fade)
    // r74 · LA AURA SIGUE LA MANO (informe del dueño: «si cambiamos la pala
    // de mano ese efecto de glow no está presente»): la aura se montaba UNA
    // vez sobre el paddleMount de LA MANO DE ENTONCES — con A/X la pala
    // viaja a la otra montura y el glow quedaba huérfano en la mano vacía.
    // Ahora, cada frame y sin coste, si la aura no cuelga de la montura
    // ACTIVA se re-papa inmediatamente (remove + add, misma identidad).
    auraOp += (auraMeta - auraOp) * Math.min(1, dt * 3.2);
    if (auraMats) {
      try {
        if (auraGrp && G.paddleMounts && auraGrp.parent !==
            G.paddleMounts[G.paddleHand | 0] &&
            G.paddleMounts[G.paddleHand | 0]) {
          const viejo = auraGrp.parent;
          if (viejo) { try { viejo.remove(auraGrp); } catch (eR) { /* */ } }
          G.paddleMounts[G.paddleHand | 0].add(auraGrp);
        }
      } catch (eAura) { /* decorativo */ }
      const pulso = 0.55 + 0.45 * Math.sin(mandoT * 4.2);
      for (const m of auraMats) {
        try { m.opacity = auraOp * pulso; } catch (e) { /* */ }
      }
    }
    // halos de la pieza pedida (en el mando REAL de cada mano)
    hlParte = hlDePaso();
    const pulso = (0.72 + 0.28 * Math.sin(mandoT * 5)) * mandosVis;
    for (const a of (anclados || [])) {
      if (!a.halos) continue;
      for (const kk in a.halos) {
        try {
          a.halos[kk].material.opacity = (kk === hlParte) ? pulso : 0;
        } catch (e) { /* */ }
      }
    }
    if (etiqueta) {
      const t = hlParte ? txtDeEtiqueta(hlParte)
        : (auraMeta > 0.3 ? T('tut_lab_pala') : '');
      if (t) {
        pintaEtiqueta(etiqueta, t);
        etiqueta.material.opacity = Math.min(1,
          etiqueta.material.opacity + dt * 6) * mandosVis;
      } else {
        etiqueta.material.opacity = Math.max(0, etiqueta.material.opacity - dt * 6);
      }
    }
  }
  function bolaPalmDemo() {
    // r71 · bola de la demo del PROFESOR: ELEVADA y justo detrás del borde
    // (la pala del rival es la referencia visual). La posición antigua
    // (apoyada a la ALTURA de la mesa, 17 cm detrás del borde) hacía
    // IMPOSIBLE el saque reglamentario: ningún arco que parte descendiendo
    // desde la altura de la mesa puede botar antes en SU campo — el solver
    // no encontraba candidatos y caía SIEMPRE al fallback (lob directo al
    // campo del jugador: UN solo bote, el fallo que vio el dueño).
    // Verificado empíricamente (scripts/_r71_verifica_palma.mjs): desde
    // aquí el solver devuelve 100/100 saques con bote propio profundo en
    // SU campo + bote cómodo en el nuestro (margen de red ≥ 49 mm) y la
    // bola queda a 100 mm de la guardia de la raqueta (barrido natural).
    const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TY = DIMS.tableTopY;
    return new THREE.Vector3(0.10, TY + 0.34, C - HL - 0.16);
  }

  /* ---------------- LA RAQUETA DEL RIVAL (r68) ------------------------
   * El dueño tras V3.6.59: «la pelota en el saque y en el juego debe ser
   * golpeada por la raqueta del rival; en estos momentos permanece quieta
   * y la pelota la golpea un fantasma». Hasta hoy el PROFESOR no tenía
   * pala: la bola salía (saque demo, devoluciones y feeds de práctica)
   * desde el aire vacío. Esta es SU pala — la MISMA del juego
   * (makePaddleVisual 'center': la hoja en el origen, pensado para la IA)
   * — viva en la escena mundo al lado lejano de la mesa: ARMA (retroceso
   * siguiendo la bola), BARRE hasta ella y el golpe REAL sale cuando la
   * hoja pasa por la bola (los saques quietos esperan al blade: el launch
   * se dispara a RAQ_T_GOLPE, el mismo tramo de la barra). Sólo actúa en
   * los pasos 2-5 (los de mesa); en el resto ni está. Además el paso 5
   * (devoluciones) tenía la bola CONGELADA tras el feed (nadie ponía
   * tutBolaViva=true en ese paso desde la renumeración r67): el saque del
   * profesor ahora sale con la hoja y pone la bola viva — el rally
   * vuelve a existir.                                                   */
  const RAQ_T_GOLPE = 0.13;     // s de la barra hasta la bola (contacto)
  const RAQ_T_FT = 0.30;        // s de acompañamiento tras el golpe
  function buildRaqueta() {
    if (raqGrp || !G || !G.scene || typeof THREE === 'undefined') return;
    raqGrp = new THREE.Group();
    raqGrp.name = 'ppTutRaquetaRival';
    raqVis = makePaddleVisual(G.paddleModelRef, 'center');
    raqVis.rotation.set(-0.42, 0.08, 0);   // cara al jugador (+z), en guardia
    raqGrp.add(raqVis);
    raqGrp.position.set(0.17, DIMS.tableTopY + 0.38,
      DIMS.tableCenterZ - DIMS.tableHalfLength - 0.10);
    raqGrp.visible = false;
    // r70 · AL RIG, COMO LA MESA Y LA BOLA: la raqueta del profesor vivía
    // en G.scene (mundo crudo) mientras mesa, bola y pala IA viven en el
    // RIG (el espacio de referencia XR) — con el recentrado del Quest la
    // raqueta quedaba DESPLAZADA respecto a la mesa («problemas de
    // colocación», «desfasada y no golpea la pelota» y, ya en v3.6.61,
    // «el rival golpea pero no aparece su raqueta»: golpeaba fuera de
    // campo visual). El rig es SU espacio — las mismas coordenadas que la
    // física usa para la bola y el barrido.
    G.rig.add(raqGrp);
    raqDe = new THREE.Vector3();
    raqContacto = new THREE.Vector3();
    raqMeta = new THREE.Vector3();
    raqModo = 'oculta'; raqT = 0; feed5T = 0;
  }
  function limpiarRaqueta() {
    if (raqGrp) {
      try { if (raqGrp.parent) raqGrp.parent.remove(raqGrp); } catch (e) { /* */ }
    }
    raqGrp = null; raqVis = null; raqDe = null; raqContacto = null;
    raqMeta = null; raqModo = 'oculta'; raqT = 0; feed5T = 0;
  }
  /* r69 · LA AURA SE DESMONTA DE VERDAD: hasta hoy teardownPanel anulaba
   * auraMats pero el grupo ppTutAuraPala SE QUEDABA colgado del
   * paddleMount con la última opacidad del pulso congelada — el «halo
   * marcado sobre nuestra propia pala» que el dueño veía en partido y
   * campeonatos después de la academia. Ahora sale del grafo y libera
   * sus materiales; si quedara algún huérfano, sale por nombre.        */
  function limpiarAura() {
    if (auraGrp) {
      try { if (auraGrp.parent) auraGrp.parent.remove(auraGrp); } catch (eA) { /* */ }
      try {
        auraGrp.traverse((o) => {
          if (o.material) { try { o.material.dispose(); } catch (eD) { /* */ } }
        });
      } catch (eT) { /* */ }
    } else {
      try {
        if (G && G.paddleMounts) {
          const m2 = G.paddleMounts[G.paddleHand];
          const viejo = m2 && m2.getObjectByName && m2.getObjectByName('ppTutAuraPala');
          if (viejo) m2.remove(viejo);
        }
      } catch (eN) { /* */ }
    }
    auraGrp = null; auraMats = null; auraOp = 0; auraMeta = 0;
  }
  function raquetaReposo() {
    if (raqGrp) { raqModo = 'reposo'; raqT = 0; }
  }
  function raquetaPreparar() {
    if (!raqGrp) return;
    raqModo = 'prep'; raqT = 0;
    raqGrp.visible = true;          // r70 · defensivo: el arma NUNCA queda oculta
  }
  function raquetaGolpe(x, y, z, fx) {
    if (!raqGrp || !raqDe) return;
    raqGrp.visible = true;          // r70 · defensivo: el golpe SIEMPRE se ve
    raqDe.copy(raqGrp.position);
    raqContacto.set(x, y, z);
    const f = (fx === undefined) ? 1 : fx;
    raqMeta.set(x + 0.03, y + 0.16, z + 0.55 * f);
    raqModo = 'golpe'; raqT = 0;
  }
  function tickRaqueta(dt) {
    if (!raqGrp || !raqVis || !G || !G.ball) return;
    const conRival = (step >= 2 && step <= 5);
    raqGrp.visible = conRival;
    if (!conRival) { raqModo = 'oculta'; return; }
    raqT += dt;
    const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TY = DIMS.tableTopY;
    const k = 1 - Math.exp(-dt * 7.5);
    if (raqModo === 'golpe') {
      const tB = RAQ_T_GOLPE + RAQ_T_FT;
      if (raqT <= RAQ_T_GOLPE) {
        // TRAMO A · la hoja BARRE hasta la bola (ease-in: arranca suave y
        // llega EXACTO al contacto cuando el saque/devolución sale).
        // r69 · CONTACTO VIVO: el punto de contacto persigue a la bola en
        // vuelo (devoluciones) — al cerrar el tramo el blade está EXACTO
        // sobre ella aunque la bola avance (saques quietos: idéntico).
        const u = (raqT / RAQ_T_GOLPE) * (raqT / RAQ_T_GOLPE);
        try { raqContacto.copy(G.ball.pos); } catch (eC) { /* */ }
        raqGrp.position.lerpVectors(raqDe, raqContacto, u);
        raqVis.rotation.x = -0.55 + 0.45 * u;   // la cara cierra al impactar
      } else if (raqT <= tB) {
        // TRAMO B · acompañamiento hacia la red (ease-out, cara abierta)
        const u = 1 - Math.pow(1 - (raqT - RAQ_T_GOLPE) / RAQ_T_FT, 2);
        raqGrp.position.lerpVectors(raqContacto, raqMeta, u);
        raqVis.rotation.x = -0.10 + 0.40 * u;
      } else { raqModo = 'reposo'; raqT = 0; }
      return;
    }
    if (raqModo === 'prep') {
      // ARMA el golpe: detrás y por encima de la bola, siguiéndola
      const b = G.ball;
      const tx = Math.max(-0.55, Math.min(0.55, b.pos.x - 0.07));
      const ty = Math.max(TY + 0.05, Math.min(TY + 0.75, b.pos.y + 0.17));
      const tz = Math.max(C - HL - 0.55, Math.min(C - 0.12, b.pos.z - 0.30));
      raqGrp.position.x += (tx - raqGrp.position.x) * k;
      raqGrp.position.y += (ty - raqGrp.position.y) * k;
      raqGrp.position.z += (tz - raqGrp.position.z) * k;
      raqVis.rotation.x += (-0.55 - raqVis.rotation.x) * k;
      return;
    }
    // REPOSO: guardia del rival al lado lejano, vaivén vivo
    const rx = 0.17 + 0.010 * Math.sin(raqT * 1.1);
    const ry = TY + 0.38 + 0.012 * Math.sin(raqT * 1.8);
    const rz = C - HL - 0.10;
    raqGrp.position.x += (rx - raqGrp.position.x) * k;
    raqGrp.position.y += (ry - raqGrp.position.y) * k;
    raqGrp.position.z += (rz - raqGrp.position.z) * k;
    raqVis.rotation.x += (-0.42 - raqVis.rotation.x) * k;
  }

  /* r69 · GOLPES HONESTOS EN LAS DEVOLUCIONES — el dueño: la raqueta del
   * profesor «está desfasada y no golpea la pelota». Causa real: la
   * velocidad de la devolución se aplicaba EN EL MISMO FRAME en que el
   * barrido ARRANCABA — la hoja llegaba 0.13 s TARDE siempre (el saque
   * demo sí esperaba al blade, las devoluciones no). Ahora el golpe se
   * ARMA (devPend = RAQ_T_GOLPE) y la bola despega EXACTAMENTE cuando el
   * tramo A se cierra sobre ella; el punto de contacto es VIVO (persigue
   * a la bola), así que el blade la alcanza de verdad, venga la bola en
   * vuelo. Si la bola muere durante el viaje, el golpe se cancela: jamás
   * un lanzamiento fantasma.                                             */
  function armaDevolucion(fin, velFn) {
    if (!G || !G.ball) return;
    devPend = RAQ_T_GOLPE;
    devFin = fin;
    devVelFn = velFn;
    raquetaGolpe(G.ball.pos.x, G.ball.pos.y, G.ball.pos.z,
      fin === 'fallo' ? 0.45 : 1);
  }
  function cancelaDevolucion() {
    devPend = 0; devFin = null; devVelFn = null;
  }
  function tickDevolucion(dt) {
    if (devPend <= 0 || !G || !G.ball) return;
    const b = G.ball;
    devPend -= dt;
    const muertaD = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
      b.pos.y < -0.4;
    if (muertaD) { cancelaDevolucion(); return; }
    if (devPend > 0) return;
    // el TRAMO A se cierra: la hoja está SOBRE la bola — AHORA despega
    try {
      b.vel.copy(devVelFn(b.pos));
      b.spin.set(0, 0, 0);
    } catch (eV) {
      b.vel.set(0, 1.4, 2.2);
      b.spin.set(0, 0, 0);
    }
    if (devFin === 'ida') {
      try { G.audio.paddle(0, 0.45); } catch (eS) { /* */ }
      try { G.haptic(G.paddleHand, 0.3, 70); } catch (eH) { /* */ }
      rfFase = 'ida';
    } else if (devFin === 'fallo') {
      rfFase = 'fallo';
    } else if (devFin === 'practica') {
      try { G.audio.playOsc(300, 170, 0.07, 'square', 0.13, 0); } catch (eS2) { /* */ }
      try { G.haptic(G.paddleHand, 0.3, 70); } catch (eH2) { /* */ }
      fase = 'espera_golpe';
    }
    cancelaDevolucion();
  }

  /* ---------------- pintura del panel (PIZARRA) · r65 ----------------
   * Todo el texto va SOBRE LA ZONA NEGRA de la pizarra del dueño
   * (interior x 170..1190 · y 168..618 de 1408×768) con estilo tiza:
   * blanco/ámbar con halo suave. Los stickers del birrete y la pala
   * quedan SIEMPRE visibles en las esquinas. Nada cortado: fitFont.  */
  const LINE_MAXW = 960;        // ancho útil de la zona negra
  const PIZ_CX = 680;           // centro de la zona negra
  function fitFont(c, txt, size, weight, maxW, minSize) {
    let s = size;
    const min = minSize || 15;
    c.font = weight + ' ' + s + 'px system-ui, sans-serif';
    while (s > min && c.measureText(txt).width > maxW) {
      s -= 1;
      c.font = weight + ' ' + s + 'px system-ui, sans-serif';
    }
    return s;
  }
  function line(c, txt, y, size, col, align, x, maxW) {
    fitFont(c, txt, size, '600', maxW || LINE_MAXW);
    c.shadowColor = 'rgba(255,255,255,0.30)';
    c.shadowBlur = 7;
    c.fillStyle = col || '#eef2f5';
    c.textAlign = align || 'center';
    c.textBaseline = 'middle';
    c.fillText(txt, x || PIZ_CX, y);
    c.shadowBlur = 0;
  }
  /* parte un texto largo en 2 líneas centradas (por el espacio más
   * cercano al centro) tras intentar reducirlo.
   * r75 · cada MITAD se re-ajusta a maxW (antes las mitades se pintaban al
   * ancho que dieran: un medio-línea largo se salía de su caja). Hoy las
   * dos mitades de LOS MODOS caben (252/261 ≤ 312), así que el dibujado
   * es idéntico — el ajuste es blindaje para cualquier cadena futura. */
  function wrap2(c, txt, y, size, col, maxW, lh, x) {
    fitFont(c, txt, size, '600', maxW, 12);
    if (c.measureText(txt).width <= maxW) { line(c, txt, y, size, col, undefined, x); return; }
    const sep = txt.lastIndexOf(' ', Math.ceil(txt.length / 2));
    if (sep <= 0) { line(c, txt, y, size, col, undefined, x); return; }
    const l1 = txt.slice(0, sep), l2 = txt.slice(sep + 1);
    const s1 = fitFont(c, l1, size, '600', maxW, 9);
    line(c, l1, y - (lh || 14), s1, col, undefined, x, maxW);
    const s2 = fitFont(c, l2, size, '600', maxW, 9);
    line(c, l2, y + (lh || 14), s2, col, undefined, x, maxW);
  }
  /* píldora estilo TIZA: borde blanco translúcido, relleno ámbar/verde
   * suave y texto blanco — auto-dimensionada al texto (nada cortado). */
  function pill(c, txt, y, opts) {
    opts = opts || {};
    let size = opts.size || 30;
    c.font = '800 ' + size + 'px system-ui, sans-serif';
    const need = c.measureText(txt).width + 76;
    const w = Math.max(opts.w || 640, Math.min(need, 1000));
    if (c.measureText(txt).width > w - 48) {
      fitFont(c, txt, size, '800', w - 48, 17);
    }
    const h = opts.h || 72;
    // r72 · centro PROPIO (opts.x): la píldora puede vivir fuera del
    // centro de la pizarra (p. ej. junto al título de LOS MODOS).
    const cx = (opts.x != null) ? opts.x : PIZ_CX;
    const x = cx - w / 2;
    rr(c, x, y, w, h, 22);
    c.fillStyle = opts.col || 'rgba(47,158,68,0.30)';
    c.fill();
    c.strokeStyle = opts.borde || 'rgba(255,255,255,0.75)';
    c.lineWidth = 3;
    c.stroke();
    c.fillStyle = '#ffffff';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(txt, cx, y + h / 2 + 1);
  }
  function paintHeader(c) {
    // título a la izquierda de la zona negra (el birrete NO se tapa)
    c.textAlign = 'left';
    c.textBaseline = 'middle';
    fitFont(c, T('tut_title'), 40, '900', 600, 26);
    c.shadowColor = 'rgba(255,210,87,0.4)';
    c.shadowBlur = 8;
    c.fillStyle = '#ffd257';
    c.fillText(T('tut_title'), 300, 212);
    c.shadowBlur = 0;
    // contador + puntos de progreso (11) a la derecha, bajo el sticker
    c.font = '700 20px system-ui, sans-serif';
    c.fillStyle = '#cfd8e0';
    c.textAlign = 'right';
    c.fillText(T('tut_step', { n: step + 1, m: STEPS }), 1150, 206);
    for (let i = 0; i < STEPS; i++) {
      const dx = 1146 - (STEPS - 1 - i) * 24;
      c.beginPath();
      c.arc(dx, 240, i === step ? 7.5 : 5, 0, Math.PI * 2);
      c.fillStyle = i < step ? '#7fb069' : (i === step ? '#ffd257' : 'rgba(255,255,255,0.28)');
      c.fill();
    }
  }
  function modeRow(c, y, col0, ini, title, sub) {
    rr(c, 190, y, 980, 68, 16);
    c.fillStyle = 'rgba(255,255,255,0.07)';
    c.fill();
    c.strokeStyle = col0;
    c.lineWidth = 2.5;
    c.stroke();
    c.beginPath(); c.arc(248, y + 34, 23, 0, Math.PI * 2);
    c.fillStyle = col0; c.fill();
    c.fillStyle = '#ffffff';
    c.font = '800 24px system-ui, sans-serif';
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(ini, 248, y + 35);
    c.textAlign = 'left';
    fitFont(c, title, 25, '800', 740, 17);
    c.fillText(title, 288, y + 24);
    c.fillStyle = 'rgba(255,255,255,0.85)';
    fitFont(c, sub, 17, '500', 740, 12);
    c.fillText(sub, 288, y + 50);
  }
  /* r75 · ENVOLTURA GARANTIZADA DENTRO de la tarjeta (informe del dueño:
   * «en la pantalla del tutorial de Modos algunos textos quedan fuera del
   * contenedor»): diagnóstico medido en vivo — la línea extra de RANKING
   * MUNDIAL (353 px) y la de ENTRENAR (324 px) agotaban el mínimo de
   * fitFont (10 px) y seguían midiendo MÁS que los 214 px disponibles de
   * las tarjetas de 300: el ámbar salía de la tarjeta y se comía la
   * vecina. cardWrap reduce la fuente (fitFont) y, si aún no cabe, ENVUELVE
   * por palabras en ≤maxLines líneas que miden TODAS ≤maxW; si ni así
   * cabe, recorta con elipsis al mínimo. Nada sale del marco, con
   * cualquier fuente del visor, en ES y en EN. */
  function cardWrap(c, txt, size, weight, minS, maxW, maxLines) {
    const words = String(txt).split(' ');
    const envuelve = (s, n) => {
      // envoltura glotona a s px en ≤n líneas; null si no cabe entera
      c.font = weight + ' ' + s + 'px system-ui, sans-serif';
      const lines = [];
      let cur = '';
      for (let i = 0; i < words.length; i++) {
        const test = cur ? cur + ' ' + words[i] : words[i];
        if (c.measureText(test).width <= maxW) { cur = test; continue; }
        if (cur) { lines.push(cur); cur = ''; }
        if (c.measureText(words[i]).width > maxW) return null;
        if (lines.length >= n) return null;
        cur = words[i];
      }
      if (cur) lines.push(cur);
      if (!lines.length || lines.length > n) return null;
      let wide = 0;
      for (let i = 0; i < lines.length; i++) {
        wide = Math.max(wide, c.measureText(lines[i]).width);
      }
      return wide <= maxW ? lines : null;
    };
    // 1.ª preferencia: UNA línea si cabe con fuente legible (≥11 px) —
    // las tarjetas altas conservan el dibujado r74 tal cual.
    const suelo1 = Math.max(minS, 11);
    for (let s = size; s >= suelo1; s--) {
      const unica = envuelve(s, 1);
      if (unica) return { size: s, lines: unica };
    }
    // 2.ª preferencia: partir en ≤maxLines líneas a la MAYOR fuente posible
    for (let s = size; s >= minS; s--) {
      const partes = envuelve(s, maxLines);
      if (partes) return { size: s, lines: partes };
    }
    // 3.ª: una línea aunque sea al mínimo
    const ultima = envuelve(minS, 1);
    if (ultima) return { size: minS, lines: ultima };
    // red de seguridad: elipsis al mínimo (jamás fuera del contenedor)
    c.font = weight + ' ' + minS + 'px system-ui, sans-serif';
    let t2 = String(txt);
    while (t2.length > 4 && c.measureText(t2 + '…').width > maxW) t2 = t2.slice(0, -1);
    return { size: minS, lines: [t2 + '…'] };
  }
  /* r67 · tarjeta compacta de la rejilla de modos (2×3)
   * r75 · título, subtítulo y extra pasan por cardWrap (≤1/1/2 líneas) y
   * las anclas bajan cuando la tarjeta es baja (h<88) para que la extra
   * de 2 líneas respire sin pisar al subtítulo. cardWrap prefiere UNA
   * línea legible (≥11 px): con la fuente del visor las tarjetas ALTAS
   * (480) se ven EXACTAMENTE igual que r74, y las BAJAS (300) meten su
   * extra en 2 líneas DENTRO del marco: 353→~206 px y 324→~213 px por
   * línea, con separación de tinta verificada (sub ↔ extra ≥1 px). */
  function modeCard(c, x, y, w, h, col0, ini, title, sub, extra) {
    rr(c, x, y, w, h, 16);
    c.fillStyle = 'rgba(255,255,255,0.07)'; c.fill();
    c.strokeStyle = col0; c.lineWidth = 2.5; c.stroke();
    c.beginPath(); c.arc(x + 36, y + h / 2, 21, 0, Math.PI * 2);
    c.fillStyle = col0; c.fill();
    c.fillStyle = '#ffffff';
    c.font = '800 22px system-ui, sans-serif';
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(ini, x + 36, y + h / 2 + 1);
    c.textAlign = 'left';
    const tw = w - 86;
    const tt = cardWrap(c, title, 21, '800', 14, tw, 1);
    c.fillStyle = 'rgba(255,255,255,0.85)';
    const ts = cardWrap(c, sub, 15, '500', 10, tw, 1);
    const te = extra ? cardWrap(c, extra, 13, '600', 9, tw, 2) : null;
    const filaAlta = h >= 88;
    // r75 · COMPACTA: las tarjetas bajas (h<88) y las altas cuya extra se
    // parte en 2 líneas suben sus filas (título 24 · sub 42) para que la
    // 2.ª línea de la extra respire SIN colisión de tinta (verificado en
    // vivo con métricas reales del canvas); las altas con extra en 1 línea
    // conservan el dibujado r74 EXACTO (título 27 · sub 50 · extra y+h−14).
    const compacta = !filaAlta || (te && te.lines.length === 2);
    c.fillText(tt.lines[0], x + 68, y + (compacta ? 24 : 27));
    c.fillText(ts.lines[0], x + 68, y + (compacta ? 42 : 50));
    // r74 · EXPLICACIÓN LARGA del modo (el dueño: «esta parte de los modos
    // no está bien explicada, deberías pararte un poco más»): cada tarjeta
    // gana SU línea de detalle (cómo se juega y cuánto dura), en ámbar.
    // r75 · y SIEMPRE dentro de la tarjeta: cardWrap la parte en 2 líneas
    // si el ancho de la tarjeta no da para más.
    if (te) {
      c.fillStyle = 'rgba(255,224,138,0.80)';
      c.font = '600 ' + te.size + 'px system-ui, sans-serif';
      if (te.lines.length === 2) {
        c.fillText(te.lines[0], x + 68, y + h - 25);
        c.fillText(te.lines[1], x + 68, y + h - 12);
      } else {
        c.fillText(te.lines[0], x + 68, y + h - 14);
      }
    }
  }
  const PAINTERS = [
    // 0 · BIENVENIDA (voz tutv0a/b)
    (c) => {
      line(c, T('tut_s0_t'), 262, 48, '#ffd257');
      line(c, T('tut_s0_l1'), 340, 26);
      line(c, T('tut_s0_l2'), 384, 26);
      pill(c, T('tut_s0_go'), 462, { col: 'rgba(232,180,90,0.30)', size: 32 });
    },
    // 1 · TU MANDO, TU RAQUETA (r67 · fusiona mandos+pala: 4 acciones reales
    //     sobre los mandos ANCLADOS a tus manos y después el vaivén con la
    //     ÚNICA raqueta — la pala real que ya tienes en la mano)
    (c) => {
      // r72 · TÍTULO EN SU FILA: la cabecera (LA ACADEMIA CRAZY · PASO X DE 9
      // · puntos) ocupa 168..248 — todo título de paso baja a y=272. Antes
      // «TU MANDO, TU RAQUETA» en 236 pisaba el título de la cabecera.
      line(c, T('tut_m_t'), 272, 40, '#ffd257');
      line(c, T('tut_s1_l2'), 320, 20, '#c9d4de');
      line(c, T('tut_s1_l1'), 350, 17, '#8b98a5');
      const tareas = [T('tut_m1_gat'), T('tut_m1_grip'), T('tut_m1_stick'), T('tut_m1_a')];
      for (let i = 0; i < 4; i++) {
        c.beginPath();
        c.arc(512 + i * 42, 386, subfase > i ? 9 : 6.5, 0, Math.PI * 2);
        c.fillStyle = subfase > i ? '#7fb069' : 'rgba(255,255,255,0.30)';
        c.fill();
      }
      if (subfase >= 4) {
        // momento RAQUETA: barra de vaivén con la pala real en la mano.
        // r69 · INSTRUCCIÓN EXPLÍCITA en el momento (el dueño: «es preciso
        // que se le diga que la mueva hacia los lados sino no nos
        // enteramos») — latiendo mientras la barra sigue vacía.
        // r70 · SIN SOLAPE: la píldora (caja 406..478 con h=72) y la línea
        // de la instrucción (glifos 441..463) se comían — DOS textos
        // superpuestos (el dueño: «ese panel superpone los textos»).
        // r72 · el reparto r70 baja 20 px con el título (píldora 412..468,
        // instrucción 494, barra 524..564) — mismos aires, nueva fila libre.
        pill(c, T('tut_m1_raf'), 412, { col: 'rgba(90,160,255,0.30)', size: 24, h: 56 });
        const p = Math.min(1, sway / SWAY_META);
        c.globalAlpha = p > 0.02 ? 1 : (0.55 + 0.45 * Math.sin(mandoT * 5.2));
        line(c, T('tut_m1_lado'), 494, 21, '#7fb069');
        c.globalAlpha = 1;
        rr(c, 280, 524, 800, 40, 20);
        c.fillStyle = 'rgba(255,255,255,0.12)'; c.fill();
        if (p > 0.01) {
          rr(c, 280, 524, Math.max(26, 800 * p), 40, 20);
          c.fillStyle = 'rgba(127,176,105,0.75)'; c.fill();
        }
        c.fillStyle = '#eef2f5';
        c.font = '700 18px system-ui, sans-serif';
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText(Math.round(p * 100) + '%', PIZ_CX, 545);
      } else {
        pill(c, tareas[Math.min(subfase, 3)], 412,
          { col: 'rgba(232,180,90,0.28)', size: 26 });
      }
    },
    // 2 · EL SAQUE · demo del PROFESOR sobre la mesa real y luego 3 saques TUYOS
    //     r72 · título a 272 (fuera de la cabecera) y cuerpo reexpandido:
    //     la práctica reparte sus 6 filas con aire (líneas 316/348/380,
    //     contador 418+466, píldora 514..578) — antes el título en 214
    //     chocaba con «LA ACADEMIA CRAZY» y el contador vivía apretado.
    (c) => {
      if (submodo === 'demo') {
        line(c, T('tut_d3_t'), 272, 38, '#ffd257');
        line(c, T('tut_d3_l1'), 336, 22);
        line(c, T('tut_d3_l2'), 376, 22);
        line(c, T('tut_d3_l3'), 416, 22);
        const aviso = demoTxt && demoTxt.t > 0
          ? { txt: demoTxt.txt, col: demoTxt.col || 'rgba(47,158,68,0.35)' }
          : (demoT > 4 ? { txt: T('tut_d3_go'), col: 'rgba(232,180,90,0.30)' }
                       : { txt: T('tut_rep'), col: 'rgba(255,255,255,0.10)' });
        pill(c, aviso.txt, 478, { col: aviso.col, size: 26 });
      } else {
        line(c, T('tut_s3_t'), 272, 40, '#ffd257');
        line(c, T('tut_s3_l1'), 316, 20);
        line(c, T('tut_s3_l2'), 348, 20);
        line(c, T('tut_s3_l3'), 380, 20);
        line(c, T('tut_s3_cnt'), 418, 18, '#9fb0bd');
        c.fillStyle = '#ffffff';
        c.shadowColor = 'rgba(255,255,255,0.4)'; c.shadowBlur = 10;
        c.font = '900 50px system-ui, sans-serif';
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText(Math.min(saqCount, SAQ_META) + ' / ' + SAQ_META, PIZ_CX, 466);
        c.shadowBlur = 0;
        if (flashOk > 0) pill(c, T('tut_s3_ok'), 514, { col: 'rgba(47,158,68,0.35)', size: 26, h: 64 });
        else if (flashAgain > 0) pill(c, T('tut_s3_again'), 514, { col: 'rgba(240,135,63,0.32)', size: 26, h: 64 });
        else pill(c, T('tut_s3_task'), 514, { size: 28, h: 64 });
      }
    },
    // 3 · EL INTERCAMBIO REAL (saque tuyo + rival que devuelve hasta fallar)
    //     r72 · título a 272: «EL INTERCAMBIO» en 236 se pintaba ENCIMA de
    //     la cabecera (el dueño: «se pisa con el texto que tiene arriba»).
    (c) => {
      line(c, T('tut_d4_t'), 272, 40, '#ffd257');
      line(c, T('tut_d4_l1'), 322, 21);
      line(c, T('tut_d4_l2'), 360, 21);
      line(c, T('tut_d4_l3'), 398, 21);
      if (rfHecho) {
        pill(c, T('tut_d4_ok'), 440, { col: 'rgba(47,158,68,0.35)', size: 27, h: 64 });
        pill(c, T('tut_hint_next'), 520, { w: 520, h: 50, col: 'rgba(232,180,90,0.28)', size: 23 });
      } else {
        pill(c, T('tut_d4_task'), 452, { size: 24 });
      }
    },
    // 4 · EL MARCADOR (holo sobre la mesa + saques reales en bucle) · r72: título a 272
    (c) => {
      line(c, T('tut_d5_t'), 272, 40, '#ffd257');
      line(c, T('tut_d5_l1'), 330, 22);
      line(c, T('tut_d5_l2'), 368, 22);
      line(c, T('tut_d5_l3'), 406, 22);
      pill(c, demoT >= DEMO_MIN ? T('tut_ent')
        : T('tut_h_saq') + '… ' + Math.ceil(DEMO_MIN - demoT) + ' s',
        478, { col: demoT >= DEMO_MIN ? 'rgba(47,158,68,0.35)' : 'rgba(255,255,255,0.10)', size: 27 });
    },
    // 5 · LA PRÁCTICA (el profesor devuelve 6 bolas) · r72: título a 272
    //     («EL INTERCAMBIO» en 224 con s42 arrancaba DENTRO de la cabecera).
    (c) => {
      line(c, T('tut_s4_t'), 272, 42, '#ffd257');
      line(c, T('tut_s4_l1'), 330, 23);
      line(c, T('tut_s4_l2'), 366, 23);
      c.fillStyle = '#ffffff';
      c.shadowColor = 'rgba(255,255,255,0.4)'; c.shadowBlur = 10;
      c.font = '900 74px system-ui, sans-serif';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText(T('tut_s4_n', { n: Math.min(hitCount, DEVOL_META) }), PIZ_CX, 446);
      c.shadowBlur = 0;
      pill(c, T('tut_s4_task'), 510, { size: 27, h: 64 });
    },
    // 6 · LOS BOTONES EN JUEGO · r72: título a 272 (en 240 rozaba la
    //     cabecera y apretaba todo el bloque — «textos algo pegados»)
    (c) => {
      line(c, T('tut_s5_t'), 272, 40, '#ffd257');
      line(c, T('tut_s5_l1'), 330, 23);
      line(c, T('tut_s5_l2'), 370, 23);
      for (const [lb, kx] of [['A', 600], ['X', 760]]) {
        rr(c, kx - 38, 412, 76, 76, 17);
        c.fillStyle = 'rgba(255,255,255,0.10)'; c.fill();
        c.strokeStyle = '#e8b45a'; c.lineWidth = 3.5; c.stroke();
        c.fillStyle = '#ffe08a';
        c.font = '900 42px system-ui, sans-serif';
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText(lb, kx, 452);
      }
      pill(c, T('tut_s5_task'), 522, { w: 600, h: 56, size: 25 });
    },
    // 7 · LOS MODOS · rejilla 2×3 (r67 · UNA sola pizarra, antes eran dos)
    //     r72 · REENCUADRE COMPLETO (el dueño: «los textos están mal
    //     colocados»): (1) el título baja a 262 — en 208 se pintaba DENTRO
    //     de la cabecera; (2) la píldora «GATILLO · continuar» sube a la
    //     fila del título, a su DERECHA (x=986) — antes caía en 552 ENCIMA
    //     de la fila inferior (496..566); (3) el texto PODERES se dibuja
    //     DENTRO de su caja ámbar con centro x=996 — el wrap2 antiguo
    //     pintaba SIEMPRE en el centro de la pizarra (680), o sea ENCIMA
    //     de la tarjeta ENTRENAR. Fila de tarjetas con aire limpio.
    (c) => {
      line(c, T('tut_mods_t'), 262, 34, '#ffd257');
      pill(c, T('tut_hint_next'), 252, { w: 300, h: 32, x: 986, col: 'rgba(232,180,90,0.28)', size: 18 });
      const W = 480, H = 88;
      const cards = [
        [190, 296, 'rgba(47,158,68,0.8)', 'P', T('hub_match'), T('tut_mod_p'), T('tut_s6_m1')],
        [690, 296, 'rgba(232,89,12,0.8)', 'S', T('sec_surv'), T('tut_mod_s'), T('tut_s6_m2')],
        [190, 396, 'rgba(112,72,232,0.8)', 'M', T('hub_multi'), T('tut_mod_m'), T('tut_s6_m3')],
        [690, 396, 'rgba(184,134,11,0.8)', 'C', T('sec_crazy'), T('tut_mod_c'), T('tut_s7_m1')],
      ];
      for (const [x, y, col, ini, ti, su, ex] of cards) {
        modeCard(c, x, y, W, H, col, ini, ti, su, ex);
      }
      // fila inferior: RANKING + ENTRENAR (más estrechas, con la caja de poderes)
      modeCard(c, 190, 496, 300, 80, 'rgba(12,166,120,0.8)', 'R', T('sec_rank'), T('tut_mod_r'), T('tut_s7_m2'));
      modeCard(c, 506, 496, 300, 80, 'rgba(28,126,214,0.8)', 'T', T('sec_train'), T('tut_mod_t'), T('tut_s7_m3'));
      rr(c, 822, 496, 348, 80, 14);
      c.fillStyle = 'rgba(232,180,90,0.14)'; c.fill();
      c.strokeStyle = 'rgba(232,180,90,0.45)'; c.lineWidth = 2; c.stroke();
      wrap2(c, T('tut_pow_t'), 536, 14, '#ffe08a', 312, 11, 996);
    },
    // 8 · ¡YA SABES JUGAR!
    (c) => {
      line(c, T('tut_s8_t'), 268, 52, '#ffd257');
      line(c, T('tut_s8_l1'), 352, 25);
      line(c, T('tut_s8_l2'), 396, 25);
      pill(c, T('tut_s8_go'), 466, { w: 760, h: 88, col: 'rgba(127,176,105,0.38)', size: 36 });
    },
  ];
  function paintStep() {
    if (!cc) return;
    const c = cc;
    c.clearRect(0, 0, 1408, 768);
    if (pizImg) {
      c.drawImage(pizImg, 0, 0, 1408, 768);   // la PIZARRA del dueño de fondo
    } else {
      rr(c, 8, 8, 1392, 752, 30);
      const bg = c.createLinearGradient(0, 0, 0, 768);
      bg.addColorStop(0, 'rgba(13,19,34,0.97)');
      bg.addColorStop(1, 'rgba(8,11,20,0.97)');
      c.fillStyle = bg;
      c.fill();
      c.strokeStyle = 'rgba(232,180,90,0.75)';
      c.lineWidth = 4;
      c.stroke();
    }
    paintHeader(c);
    try { PAINTERS[step](c); } catch (e) { /* decorativo */ }
    line(c, T('tut_hint_skip'), 604, 18, '#8b98a5');
    if (tex) tex.needsUpdate = true;
  }

  /* ---------------- VOZ NATIVA (r65) · narra cada paso ---------------
   * Banco Piper es/en (tutv*): cada paso narra al ENTRAR y el STICK la
   * repite. Respeta el interruptor del megáfono (audio.voice). Si el
   * banco aún decodifica, reintenta hasta 3 veces.                   */
  function narra(keys) {
    narrKeys = keys;
    if (!G || !G.audio || !G.audio.speakPlan) return;
    try {
      if (G.audio.voice === false) return;   // el dueño apagó el megáfono
      // r66 · MÁS PAUSADA (petición del dueño): respiro entre átomos
      const plan = keys.map((k) => ({ k, gap: 0.32 }));
      if (G.audio.speakPlan(plan)) { narrRetry = 0; return; }
      narrRetry = 1.4;
    } catch (e) { /* nunca rompe */ }
  }
  let narrTries = 0;
  function tickNarr(dt) {
    if (narrRetry > 0 && narrKeys) {
      narrRetry -= dt;
      if (narrRetry <= 0 && narrTries < 3) {
        narrTries++;
        const ks = narrKeys;
        narrKeys = null;
        narra(ks);
      }
    }
  }

  /* ---------------- HOLO-MARCADOR sobre la mesa (r65→r66) -------------
   * El marcador vive EN LA MESA (bajo, sobre la mitad rival — el dueño:
   * «la simulación a una distancia sobre la mesa no tiene sentido») y los
   * PUNTOS los anotan saques REALES del bucle demo del paso 5 (no un
   * reloj abstracto): pip a pip hasta 11 ganando por 2, fichas de saque
   * 2·2 y CADA punto desde 10-10, cartel «+2 PARA GANAR» en la igualada. */
  function _holoMat(col, op) {
    return new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: op || 0.85 });
  }
  function _cartelTxt(txt, col, px, w, h) {
    const cvh = document.createElement('canvas');
    cvh.width = 256; cvh.height = 128;
    const g2 = cvh.getContext('2d');
    // r71 · AUTOAJUSTE: el cartel es un canvas de 256 px y un texto largo
    // («¡+2 PARA GANAR!» a 54 px) se SALÍA del lienzo — en el Quest se veía
    // la palabra RECORTADA («GAN» en vez de «GANAR», el fallo del dueño en
    // la explicación del 10-10). Se mide el texto y la fuente se encoge
    // hasta caber con margen (12 px por lado): el cartel SIEMPRE entero,
    // en ES y en EN, para cualquier cadena futura.
    const MARGEN = 244;                       // ancho útil del lienzo (256−2×6)
    let px2 = px || 64;
    g2.font = '900 ' + px2 + 'px system-ui, sans-serif';
    let ancho = g2.measureText(txt).width;
    if (ancho > MARGEN) {
      px2 = Math.max(20, Math.floor(px2 * (MARGEN / ancho)));
      g2.font = '900 ' + px2 + 'px system-ui, sans-serif';
    }
    g2.textAlign = 'center'; g2.textBaseline = 'middle';
    g2.shadowColor = 'rgba(255,255,255,0.5)';
    g2.shadowBlur = 8;
    g2.fillStyle = col || '#ffffff';
    g2.fillText(txt, 128, 64);
    const t = new THREE.CanvasTexture(cvh);
    t.colorSpace = THREE.SRGBColorSpace;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w || 0.30, h || 0.15),
      new THREE.MeshBasicMaterial({ map: t, transparent: true, depthTest: false }));
    m.renderOrder = 986;
    return m;
  }
  function limpiarHolo() {
    if (!holo) return;
    try { if (holo.parent) holo.parent.remove(holo); } catch (e) { /* */ }
    holo = null; holoPips = null; holoGhost = null; holoTokens = null;
    holoCartel2 = null;
  }
  /* ---- AROS GUÍA del saque (r67) ----------------------------------
   * Dos aros PLANOS sobre la MESA REAL que marcan DÓNDE debe botar un
   * saque válido: primero en TU campo y después en el del rival. Pulsan
   * suave y SE ILUMINAN en verde cuando la bola botó en su zona — la
   * regla se VE, no se lee (el profesor la usa en su demo y tú en la
   * práctica). Sin mallas raras: torus fino reutilizando el material holo. */
  let arosGrp = null;
  let aroIzq = null, aroDer = null;
  function construirAros() {
    limpiarAros();
    if (!G || !G.scene || typeof THREE === 'undefined') return;
    const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TY = DIMS.tableTopY;
    arosGrp = new THREE.Group();
    const geo = new THREE.TorusGeometry(0.085, 0.008, 8, 28);
    aroIzq = new THREE.Mesh(geo, _holoMat('#ffd257', 0.5));
    aroIzq.rotation.x = -Math.PI / 2;
    aroIzq.position.set(0.10, TY + 0.006, C + HL * 0.62);   // TU campo
    aroDer = new THREE.Mesh(geo, _holoMat('#ffd257', 0.5));
    aroDer.rotation.x = -Math.PI / 2;
    aroDer.position.set(0.10, TY + 0.006, C - HL * 0.62);   // campo del rival
    arosGrp.add(aroIzq); arosGrp.add(aroDer);
    arosGrp.__t = 0;
    G.rig.add(arosGrp);   // r70 · al RIG: las DIMS son coordenadas del rig
  }
  function limpiarAros() {
    if (!arosGrp) return;
    try { if (arosGrp.parent) arosGrp.parent.remove(arosGrp); } catch (e) { /* */ }
    arosGrp = null; aroIzq = null; aroDer = null;
  }
  function tickAros(dt) {
    if (!arosGrp) return;
    arosGrp.__t += dt;
    const t = arosGrp.__t;
    const base = 0.42 + 0.18 * Math.sin(t * 3.2);
    try {
      if (aroIzq) aroIzq.material.opacity = aroIzq.__ok ? 0.95 : base;
      if (aroDer) aroDer.material.opacity = aroDer.__ok ? 0.95 : base;
      if (aroIzq) aroIzq.material.color.set(aroIzq.__ok ? '#7fb069' : '#ffd257');
      if (aroDer) aroDer.material.color.set(aroDer.__ok ? '#7fb069' : '#ffd257');
    } catch (e) { /* decorativo */ }
  }
  function _holoBase() {
    limpiarHolo();
    if (!G || !G.scene || typeof THREE === 'undefined') return null;
    holo = new THREE.Group();
    // r66 · BAJO, sobre la mitad rival de la MESA (nunca flotando lejos)
    holo.position.set(0, DIMS.tableTopY + 0.22, DIMS.tableCenterZ - DIMS.tableHalfLength * 0.34);
    // r70 · al RIG (espacio de la mesa/bola): en G.scene el recentrado del
    // Quest lo descolocaba igual que a la raqueta del profesor
    G.rig.add(holo);
    holoT = 0;
    return holo;
  }
  function construirHoloMarcador() {
    const H = _holoBase();
    if (!H) return;
    holoPips = { izq: [], der: [] };
    const geo = new THREE.SphereGeometry(0.014, 10, 8);
    for (let i = 0; i < 11; i++) {
      const a = new THREE.Mesh(geo, _holoMat('#7fb069', 0.20));
      a.position.set(-0.30 + i * 0.030, 0.10, 0);
      H.add(a); holoPips.izq.push(a);
      const b = new THREE.Mesh(geo, _holoMat('#e8590c', 0.20));
      b.position.set(0.30 - i * 0.030, 0.10, 0);
      H.add(b); holoPips.der.push(b);
    }
    const tI = _cartelTxt(T('tut_h_tu'), '#a8e0b0', 56, 0.20, 0.10);
    tI.position.set(-0.30, 0.24, 0); H.add(tI);
    const tD = _cartelTxt(T('tut_h_ia'), '#f0a878', 56, 0.20, 0.10);
    tD.position.set(0.30, 0.24, 0); H.add(tD);
    const t11 = _cartelTxt('11', '#ffd257', 90, 0.18, 0.18);
    t11.position.set(0, 0.25, 0); H.add(t11);
    // fichas de saque (2 por lado) al pie del marcador
    holoTokens = { fichas: [], cartel10: null };
    const geoF = new THREE.CylinderGeometry(0.014, 0.014, 0.007, 14);
    for (let lado = 0; lado < 2; lado++) {
      for (let f = 0; f < 2; f++) {
        const tk = new THREE.Mesh(geoF, _holoMat(lado === 0 ? '#7fb069' : '#e8590c', 0.18));
        tk.position.set((lado === 0 ? -1 : 1) * (0.062 + f * 0.056), 0.015, 0.13);
        H.add(tk);
        holoTokens.fichas.push(tk);
      }
    }
    holoTokens.cartel10 = _cartelTxt(T('tut_h_10'), '#ff8a3d', 62, 0.30, 0.15);
    holoTokens.cartel10.position.set(0, 0.42, 0);
    holoTokens.cartel10.visible = false;
    H.add(holoTokens.cartel10);
    // r71 · cartel «+2 PARA GANAR» más ANCHO (0.50 m): con el autoajuste la
    // fuente cabe entera y el plano grande la hace legible de golpe; sube
    // 25 mm para seguir sin tocar el cartel «¡10-10!» (su banda acaba en 0.495).
    holoCartel2 = _cartelTxt(T('tut_h_p2'), '#ffd257', 54, 0.50, 0.25);
    holoCartel2.position.set(0, 0.625, 0);
    holoCartel2.visible = false;
    H.add(holoCartel2);
  }

  /* ---------------- guion: entrada y avance de pasos ----------------- */
  function chime(subida) {
    if (!G || !G.audio || !G.audio.playOsc) return;
    try {
      if (subida) G.audio.playOsc(660, 990, 0.09, 'triangle', 0.15, 0);
      else G.audio.playOsc(520, 780, 0.12, 'triangle', 0.16, 0);
    } catch (e) { /* nunca rompe */ }
  }
  /* VOCES (r67 · remapeadas al guion de 9 pasos; los átomos Piper r66 se
   * REUSAN — sin regenerar TTS): 0 bienvenida · 1 mando+raqueta (c/d/e por
   * acción, f+2a/b en el vaivén) · 2 saque (profesor + práctica) · 3
   * intercambio · 4 marcador · 5 práctica · 6 botones · 7 modos (8a+9a) ·
   * 8 final.                                                       */
  const VOCES_PASO = [
    ['tutv0a', 'tutv0b'],                    // 0 bienvenida
    ['tutv1a', 'tutv1b'],                    // 1 mando+raqueta (c/d/e por acción)
    ['tutv3a', 'tutv3b'],                    // 2 saque: demo del profesor (d en práctica)
    ['tutv4a'],                              // 3 intercambio (b al ganarlo)
    ['tutv5a', 'tutv5b'],                    // 4 marcador
    ['tutv6a', 'tutv6b'],                    // 5 práctica (6 devoluciones)
    ['tutv7a'],                              // 6 botones
    ['tutv8a', 'tutv8b', 'tutv8c', 'tutv9a', 'tutv9c', 'tutv9b'],   // 7 modos (r74: con calma · r78: campeonatos = superpoderes)
    ['tutv10a', 'tutv10b'],                  // 8 final
  ];
  function enterStep() {
    if (!G) return;
    limpiarHolo();
    limpiarAros();                      // r67 · los aros salen con el paso
    raquetaReposo();                    // r68 · la pala del rival vuelve a su guardia
    narrTries = 0;
    demoTxt = null; demoFase = 0; demoFaseT = 0;
    demoBote1 = false; demoBote2 = false;
    // r67 · los mandos anclados SÓLO se muestran en los pasos 0-1: del 2 en
    // adelante ves EXACTAMENTE lo que vas a jugar (mando real + pala real)
    mandosVisMeta = (step <= 1) ? 1 : 0;
    auraMeta = 0;
    switch (step) {
      case 0:
        // BIENVENIDA: los mandos ANCLADOS a tus manos te saludan (halos
        // apagados, todo quieto: «parece que los tenemos en las manos»)
        G.rules.state = 'point';
        G.resetToss();
        G.rules.message = '';
        break;
      case 1:
        subfase = 0;
        G.rules.state = 'point';
        G.resetToss();
        G.rules.message = '';
        break;
      case 2:
        // EL SAQUE (r67): primero la DEMO del PROFESOR sobre la mesa real
        // (saque reglamentario con la bola del juego: bote en SU campo →
        // bote en el TUYO → «sin devolución: PUNTO») con AROS GUÍA en la
        // mesa, y después 3 SAQUES del jugador. El panel se aparta.
        G.rules.state = 'point';
        G.resetToss();
        G.rules.message = '';
        submodo = 'demo';
        demoT = 0; demoCiclos = 0;
        G.tutBolaViva = false;
        posaBolaDemo();
        construirAros();
        break;
      case 3:
        // EL INTERCAMBIO (r66): saque del jugador, el rival devuelve y el
        // intercambio corre hasta que él falla: así se ve la ROTACIÓN.
        G.rules.state = 'serve';
        G.rules.server = 'player';
        G.resetToss();
        G.rules.message = '';
        rfFase = 'saque'; rfVueltas = 0; rfHecho = false; rfVueltaVista = false;
        G.tutBolaViva = false;
        break;
      case 4:
        // EL MARCADOR (r66): holo BAJO sobre la mesa + saques reales en
        // bucle que anotan punto a punto hasta 11 por 2 y la igualada.
        G.rules.state = 'point';
        G.resetToss();
        G.rules.message = '';
        demoT = 0; demoPtos = 0; demoDeuce = false;
        construirHoloMarcador();
        construirAros();
        G.tutBolaViva = false;
        posaBolaDemo();
        break;
      case 5:
        // LA PRÁCTICA: rally sin árbitro; el profesor devuelve suave.
        G.rules.state = 'rally';
        G.rules.message = '';
        hitCount = 0; aiReturned = false; farBounced = false;
        fase = (G.ball && G.ball.pos.z < DIMS.tableCenterZ) ? 'vuelo_lejos' : 'espera_golpe';
        deadT = 0;
        feed5T = 0;                     // r68 · sin saque pendiente al entrar
        quieta5T = 0;                   // r74 · vigía a cero
        // r74 · EL PROFESOR SIRVE YA AL ENTRAR (el dueño: «si antes de empezar
        // a devolver pulsas o haces un saque, no puedes avanzar — no puedes
        // sacar»): antes el feed llegaba SOLO cuando la bola quedaba MUERTA a
        // ras de suelo; entrando con la bola en la palma del demo (alta y
        // quieta) «muerta» jamás era true y el paso se quedaba SIN bola para
        // siempre. Ahora: bola congelada en la palma del profesor + feed
        // honesto al paso de la hoja (el mismo camino del tick, nada nuevo).
        try {
          const b0 = G.ball;
          if (b0) {
            G.feedPracticeBall();
            b0.vel.set(0, 0, 0); b0.spin.set(0, 0, 0);
            G.tutBolaViva = false;
            feed5T = RAQ_T_GOLPE;
            raquetaGolpe(b0.pos.x, b0.pos.y, b0.pos.z, 1);
          }
        } catch (eF5) { /* el re-feed por bola muerta lo repone */ }
        break;
      case 6:
        G.rules.state = 'point';
        G.resetToss();
        G.rules.message = '';
        G.tutBolaViva = false;          // r74 · bola DORMIDA (adiós al bote infinito de fondo)
        posaBolaMesa();                 // r74 · descansa sobre la mesa, sin sonido
        lastHand = G.paddleHand;
        break;
      default:
        G.rules.state = 'point';
        G.resetToss();
        G.rules.message = '';
        G.tutBolaViva = false;          // r74 · pasos 7/8: bola dormida y sobre la mesa
        posaBolaMesa();
        break;
    }
    if (VOCES_PASO[step]) narra(VOCES_PASO[step]);
  }
  function advance() {
    if (!G || step >= STEPS - 1) return;
    step++;
    subfase = 0; demoT = 0;
    sway = 0; hitCount = 0; aiReturned = false; farBounced = false;
    deadT = 0; flashAgain = 0; flashOk = 0; saqCount = 0; saqLatch = false;
    saqBote1 = false; saqBote2 = false;   // r70 · saque en blanco al avanzar
    cancelaDevolucion();              // r69 · sin golpes pendientes al cambiar de paso
    chime(true);
    enterStep();
    paintStep();
    try { G.haptic(G.paddleHand, 0.45, 90); } catch (e) { /* */ }
  }
  /* r66 · apoya la bola, quieta y visible, en la palma del mando demo */
  function posaBolaDemo() {
    if (!G || !G.ball) return;
    const p = bolaPalmDemo();
    G.ball.pos.copy(p);
    G.ball.vel.set(0, 0, 0);
    G.ball.spin.set(0, 0, 0);
  }
  /* r74 · bola DORMIDA y VISIBLE sobre la mesa (pasos 6/7/8 — botones, modos
   * y final): con tutBolaViva=false el núcleo congela la bola donde esté;
   * dejándola donde la dejó el paso anterior quedaba flotando o botando en el
   * suelo con micro-botes sonoros («el sonido de la bola por debajo, muy
   * molesto»). Ahora descansa sobre la mesa, quieta y sin sonido. */
  function posaBolaMesa() {
    if (!G || !G.ball) return;
    G.ball.pos.set(0, DIMS.tableTopY + DIMS.ballRadius, DIMS.tableCenterZ + 0.30);
    G.ball.vel.set(0, 0, 0);
    G.ball.spin.set(0, 0, 0);
  }

  /* ---------------- el PROFESOR del paso 6 (devolución suave) -------- */
  function targetProfesor() {
    return new THREE.Vector3(
      (Math.random() * 2 - 1) * 0.38,
      DIMS.tableTopY,
      DIMS.tableCenterZ + DIMS.tableHalfLength * 0.5,
    );
  }

  /* ---------------- pose del panel (r64/r65) --------------------------
   * FRENTE: delante del jugador (pasos de texto). LADO: en los pasos que
   * pasan EN LA MESA (3/4 REGLAS con el holo y 5/6 PRÁCTICA real) el
   * panel se APARTA al lado contrario de la pala, más abajo y girado
   * hacia el jugador — la mesa COMPLETA a la vista (petición del dueño:
   * «no nos deja ver la mesa y así resulta inútil»). Transición suave
   * (lerp exponencial, sin saltos).                                */
  function poseDestino() {
    if (step === 2 || step === 3 || step === 4 || step === 5) {
      // pala en mano 1 (derecha) → panel a la IZQUIERDA del jugador (x<0)
      const sgn = (G && G.paddleHand === 1) ? -1 : 1;
      return {
        x: sgn * 0.66, y: 1.24, z: -0.60,
        rx: 0.02, ry: -sgn * 0.62, s: 0.72, nombre: 'lado',
      };
    }
    return { x: 0, y: 1.52, z: -0.86, rx: 0.05, ry: 0, s: 1, nombre: 'frente' };
  }
  function tickPose(dt) {
    if (!grp) return;
    const p = poseDestino();
    const k = 1 - Math.exp(-dt * 4.5);
    grp.position.x += (p.x - grp.position.x) * k;
    grp.position.y += (p.y - grp.position.y) * k;
    grp.position.z += (p.z - grp.position.z) * k;
    grp.rotation.x += (p.rx - grp.rotation.x) * k;
    grp.rotation.y += (p.ry - grp.rotation.y) * k;
    const s = grp.scale.x + (p.s - grp.scale.x) * k;
    grp.scale.setScalar(s);
  }

  /* ---------------- ciclo del tutorial (tick del núcleo) ------------- */
  function tick(dt) {
    if (!active || !G) return;
    try { _tick(dt); } catch (e) { /* nunca rompe el frame */ }
  }
  function _tick(dt) {
    if (!G.renderer || !G.renderer.xr || !G.renderer.xr.isPresenting) return;
    if (grp) grp.visible = true;
    // r69 · UNA SOLA RAQUETA POR LADO: la pala flotante de la IA (la de
    // los partidos, «visible en todo momento») NO pinta aquí — el dueño
    // veía DOS raquetas en el lado del profesor (la animada de la academia
    // + la de la IA parada, que jamás golpea: la que parecía «desfasada»).
    // La academia no tiene IA: oculta cada frame (idempotente) y stop()
    // la devuelve a su estado.
    try { if (G.aiPaddleMesh) G.aiPaddleMesh.visible = false; } catch (eI) { /* */ }
    pollSkip();
    pollVoz();                          // r65 · STICK = repetir la voz
    tickPose(dt);                       // el panel se aparta en la práctica
    tickMandos(dt);                     // r67 · mandos anclados + aura + halos
    try { tickRaqueta(dt); } catch (e) { /* decorativo */ } // r68 · raqueta rival
    try { tickDevolucion(dt); } catch (eD2) { /* decorativo */ } // r69 · lanzamientos honestos
    tickNarr(dt);                       // r65 · reintentos de la voz
    try { tickHolo(dt); } catch (e) { /* decorativo */ }   // holo-reglas
    try { tickAros(dt); } catch (e) { /* decorativo */ }   // r67 · aros guía
    repaintT -= dt;
    if (flashOk > 0) {
      flashOk -= dt;
      if (flashOk <= 0) paintStep();    // expira el aviso verde
    }
    switch (step) {
      case 1: {
        // TU MANDO, TU RAQUETA (r67): las 4 acciones REALES (gatillo → grip
        // → stick → botones) y después el VAIVÉN con la ÚNICA raqueta (la
        // pala real en tu mano). El gatillo llega por onTrigger; grip/stick
        // /botones se sondean aquí.
        if (subfase === 1 || subfase === 3) {
          for (let h = 0; h < 2; h++) {
            const gp = G.sources && G.sources[h] && G.sources[h].gamepad;
            if (!gp || !gp.buttons) continue;
            if (subfase === 1) {
              const g1 = !!(gp.buttons[1] && gp.buttons[1].pressed);
              if (g1 && !btn1Prev[h]) accionMandoOk();
              btn1Prev[h] = g1;
            } else {
              const b4 = !!(gp.buttons[4] && gp.buttons[4].pressed);
              if (b4 && !btn4Prev[h]) accionMandoOk();
              btn4Prev[h] = b4;
            }
          }
        } else if (subfase === 2) {
          // stick: cualquier eje con inclinación clara
          let movido = false;
          for (let h = 0; h < 2; h++) {
            const ax = G.stickAxis ? G.stickAxis(h) : null;
            if (ax && (Math.abs(ax.x) > 0.55 || Math.abs(ax.y) > 0.55)) movido = true;
          }
          if (movido) accionMandoOk();
        } else if (subfase === 4) {
          // el vaivén firme (velocidad del simulador de la pala): la raqueta
          // REAL se mueve con tu mano — el mando GLB ya se desvaneció
          const pad = G.controllerPaddles ? G.controllerPaddles[G.paddleHand] : null;
          const v = pad && pad.vel ? pad.vel.length() : 0;
          if (v > 2.2) {
            sway += dt;
            if (repaintT <= 0) { paintStep(); repaintT = 0.09; }
          }
          if (sway >= SWAY_META) advance();
        }
        break;
      }
      case 2: {
        // EL SAQUE (r67): DEMO del PROFESOR sobre la mesa real y después
        // 3 SAQUES del jugador con los AROS GUÍA en la mesa.
        demoT += dt;
        if (submodo === 'demo') {
          tickDemoSaque(dt, false);
          if (repaintT <= 0) { paintStep(); repaintT = 0.4; }
        } else {
          if (flashAgain > 0) {
            flashAgain -= dt;
            if (repaintT <= 0) { paintStep(); repaintT = 0.25; }
          }
          if (G.tossed) {
            const b = G.ball;
            const C = DIMS.tableCenterZ, TY = DIMS.tableTopY, HL = DIMS.tableHalfLength;
            // r70/r71 · EL SAQUE SE APRUEBA CON LOS DOS BOTES SOBRE LA MESA
            // (el dueño: «debe botar en ambos campos y esto no lo comprueba,
            // dando por bueno un servicio aunque bote en 1 sola parte»).
            // r71 · BOTES SOBRE LA MESA, NO EN EL SUELO: la valla antigua
            // (z + vel.y + y<TY+0.35) también pasaba el bote en el SUELO de
            // un saque largo que se iba fuera de la mesa (el suelo está a
            // −76 cm, muy por debajo de TY+0.35) — por eso un servicio que
            // solo botaba en el campo propio y se marchaba LARGO contaba
            // como bueno. Ahora cada bote exige el RECTÁNGULO real del
            // campo (x y z dentro de la mesa) y pegado a la superficie
            // (y < TY+12 cm). Volea, medio saque, largo y red = «OTRA VEZ».
            if (!saqBote1 && b.vel.y > 0.3 && b.pos.z > C + 0.06 &&
                b.pos.z < C + HL + 0.03 &&
                Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.02 &&
                b.pos.y < TY + 0.12) {
              saqBote1 = true;
              if (aroIzq) aroIzq.__ok = true;
            }
            if (saqBote1 && !saqBote2 && b.vel.y > 0.25 && b.pos.z < C - 0.05 &&
                b.pos.z > C - HL - 0.03 &&
                Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.02 &&
                b.pos.y < TY + 0.12) {
              saqBote2 = true;
              if (aroDer) aroDer.__ok = true;
            }
            if (!saqLatch && saqBote1 && saqBote2) {
              saqLatch = true;
              saqCount++;
              flashOk = 2.2; flashAgain = 0;
              paintStep();
              chime(true);
              if (saqCount >= SAQ_META) { advance(); break; }
            }
            const muerta = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
              (Math.abs(b.vel.x) < 0.5 && Math.abs(b.vel.y) < 0.5 && Math.abs(b.vel.z) < 0.5 &&
                b.pos.y < DIMS.tableTopY + 0.12) ||
              b.pos.y < -0.4;
            if (muerta) {
              // la bola vuelve a la mano libre (holdLock del núcleo)
              const valida = saqLatch;
              G.resetToss();
              saqLatch = false;
              saqBote1 = false; saqBote2 = false;   // r70 · saque nuevo, botes nuevos
              if (aroIzq) aroIzq.__ok = false;
              if (aroDer) aroDer.__ok = false;
              if (!valida && flashOk <= 0) {
                flashAgain = 2.6;
                paintStep();
                narra(['tutotra']);
                try { G.audio.playOsc(330, 220, 0.12, 'sine', 0.12, 0); } catch (e) { /* */ }
              }
            }
          }
        }
        break;
      }
      case 3: {
        // EL INTERCAMBIO REAL (r66→r67): sacas, el RIVAL devuelve y el
        // intercambio corre hasta que él falla; entonces rota el sacador.
        const b = G.ball;
        if (rfFase !== 'saque' && G.rules.state !== 'rally') G.rules.state = 'rally';
        switch (rfFase) {
          case 'saque':
            G.tutBolaViva = false;
            break;
          case 'vuelo': {
            // la bola va hacia el rival: espera el bote lejano para devolver
            // r116 · NEVERA DEL PASO 4 (informe del dueño: «cuando empezamos
            // la práctica de intercambio, como lancemos la bola y esta se
            // caiga al suelo ahí se queda sin poder hacer nada»): si la bola
            // del saque muere —en el suelo, sobre la mesa o más allá— sin que
            // llegue al profesor, el intercambio SE REPITE al instante (mismo
            // camino honesto que 'ida': vuelta al saque, sin castigo). Antes
            // no había control de bola muerta en 'vuelo': rfFase quedaba
            // clavado aquí para siempre y, como el gatillo exige 'saque',
            // el paso 4 era imposible de continuar.
            const muertaV = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
              (Math.abs(b.vel.x) < 0.4 && Math.abs(b.vel.y) < 0.4 && Math.abs(b.vel.z) < 0.4 &&
                b.pos.y < DIMS.tableTopY + 0.12) ||
              b.pos.y < -0.4;
            if (muertaV) {
              rfFase = 'saque';
              rfVueltas = 0; farBounced = false; rfVueltaVista = false;
              G.rules.state = 'serve';
              G.resetToss();
              G.tutBolaViva = false;
              flashAgain = 2.4;
              paintStep();
              narra(['tutotra']);
              break;
            }
            if (!rfVueltaVista && b.pos.z < (DIMS.tableCenterZ - 0.1)) {
              if (!farBounced && b.vel.y > 0.3 && b.pos.y < DIMS.tableTopY + 0.5) {
                farBounced = true;
                raquetaPreparar();        // r68 · el rival ARMA la devolución
              }
              if (farBounced && b.vel.y < 1.1 && _cero) {
                rfVueltaVista = true;
                rfVueltas++;
                if (rfVueltas >= 3) {
                  // el rival FALLA: la devolución se queda corta y muere en
                  // la red — punto limpio y visible (r69 · sale al paso de
                  // la hoja, como el saque: nada de lanzamientos fantasma)
                  armaDevolucion('fallo', (p) => {
                    try {
                      const v = computeShotVelocityReal(p, targetProfesor(), 1.15, 4.6, _cero);
                      return v.multiplyScalar(0.62);
                    } catch (e) { return new THREE.Vector3(0, 1.4, 2.2); }
                  });
                } else {
                  const tx = (Math.random() * 2 - 1) * 0.34;
                  armaDevolucion('ida', (p) => {
                    try {
                      const t = new THREE.Vector3(
                        tx, DIMS.tableTopY,
                        DIMS.tableCenterZ + DIMS.tableHalfLength * 0.52);
                      return computeShotVelocityReal(p, t, 1.05, 4.8, _cero);
                    } catch (e) {
                      return new THREE.Vector3((Math.random() * 2 - 1) * 0.4, 2.4, 3.1);
                    }
                  });
                }
              }
            }
            break;
          }
          case 'ida': {
            // tu turno: la bola viene; cruza = golpe válido del jugador
            const muertaI = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
              (Math.abs(b.vel.x) < 0.4 && Math.abs(b.vel.y) < 0.4 && Math.abs(b.vel.z) < 0.4 &&
                b.pos.y < DIMS.tableTopY + 0.12) ||
              b.pos.y < -0.4;
            if (muertaI) {
              // no llegaste: el intercambio se repite (sin castigo)
              rfFase = 'saque';
              rfVueltas = 0; farBounced = false; rfVueltaVista = false;
              G.rules.state = 'serve';
              G.resetToss();
              G.tutBolaViva = false;
              flashAgain = 2.4;
              paintStep();
              narra(['tutotra']);
              break;
            }
            if (b.pos.z < (DIMS.tableCenterZ - 0.06) && b.vel.z < -0.9) {
              farBounced = false; rfVueltaVista = false;
              rfFase = 'vuelo';
              try { G.haptic(G.paddleHand, 0.4, 80); } catch (e) { /* */ }
            }
            break;
          }
          case 'fallo': {
            const muertaF = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
              b.pos.y < -0.4 || (b.pos.y < DIMS.tableTopY + 0.12 &&
                Math.abs(b.vel.z) < 0.5);
            if (muertaF || demoFaseT > 2.6) {
              rfHecho = true;
              rfFase = 'hecho';
              demoTxt = { txt: T('tut_d4_ok'), col: 'rgba(47,158,68,0.35)', t: 3.4 };
              chime(true);
              narra(['tutv4b']);
              paintStep();
            }
            break;
          }
          case 'hecho':
            G.tutBolaViva = false;
            break;
          default:
            break;
        }
        demoFaseT += dt;
        if (repaintT <= 0) { paintStep(); repaintT = 0.4; }
        break;
      }
      case 4: {
        // EL MARCADOR (r66→r67): holo BAJO sobre la mesa; los puntos suben
        // rápido hasta 10-10 y desde ahí CADA punto la anota un saque REAL
        // del profesor — la igualada se ve con la bola de verdad.
        demoT += dt;
        tickDemoSaque(dt, true);
        if (demoPtos < 20) {
          holoT += dt;
          while (holoT > 0.45 && demoPtos < 20) {
            holoT -= 0.45;
            anotaPuntoMarcador();
          }
        }
        if (repaintT <= 0) { paintStep(); repaintT = 0.4; }
        break;
      }
      case 5: {
        // LA PRÁCTICA (r64): el jugador devuelve 6 bolas del profesor
        const b = G.ball;
        if (G.rules.state !== 'rally') G.rules.state = 'rally';
        if (G.tossed) G.resetToss();
        if (feed5T > 0) {
          // r68 · el saque del profesor sale cuando SU hoja llega a la bola:
          // la bola espera quieta (dormida, en la mano del rival) y despega
          // al paso del blade — y queda VIVA para el rally (antes nadie
          // la despertaba en este paso: bola congelada en el aire)
          feed5T -= dt;
          if (feed5T <= 0) {
            try {
              const sv = findServeVelocity(b.pos, -1);
              b.vel.copy(sv.v);
              b.spin.copy(sv.spin);
            } catch (e) {
              b.vel.set(0, 2.2, 2.6);
              b.spin.set(0, 0, 0);
            }
            G.tutBolaViva = true;    // bola en juego: el rally existe
          }
        }
        const muerta = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
          (Math.abs(b.vel.x) < 0.4 && Math.abs(b.vel.y) < 0.4 &&
            Math.abs(b.vel.z) < 0.4 && b.pos.y < DIMS.tableTopY + 0.12);
        if (feed5T <= 0 && muerta) {
          deadT += dt;
          if (deadT > 0.5) {
            deadT = 0; farBounced = false; aiReturned = false;
            fase = 'espera_golpe';
            G.feedPracticeBall();   // el profesor sirve otra bola suave
            try { G.audio.serve(); } catch (e) { /* */ }
            // r68 · la bola ESPERA el golpe visible: su raqueta barre y el
            // saque sale al paso de la hoja (feed5T) — nada de fantasmas
            b.vel.set(0, 0, 0);
            b.spin.set(0, 0, 0);
            G.tutBolaViva = false;
            feed5T = RAQ_T_GOLPE;
            raquetaGolpe(b.pos.x, b.pos.y, b.pos.z, 1);
          }
        } else if (feed5T <= 0) {
          deadT = 0;
          // r74 · VIGÍA DE LA PRÁCTICA: nada atasca el paso. Si la bola va
          // casi quieta (|v|<0,6 m/s — palma del demo, agarrada con grip,
          // perdida en cualquier rincón) y no hay feed en marcha, el profesor
          // VUELVE A SERVIR tras 1,6 s. En rally real la bola nunca está tan
          // lenta tan tiempo (los ápex duran <0,2 s y siempre cruzan con
          // velocidad horizontal), así que el vigía jamás dispara en juego.
          if (b.vel.lengthSq() < 0.36) {
            quieta5T += dt;
            if (quieta5T > 1.6) {
              quieta5T = 0;
              deadT = 0; farBounced = false; aiReturned = false;
              fase = 'espera_golpe';
              G.feedPracticeBall();
              b.vel.set(0, 0, 0);
              b.spin.set(0, 0, 0);
              G.tutBolaViva = false;
              feed5T = RAQ_T_GOLPE;
              raquetaGolpe(b.pos.x, b.pos.y, b.pos.z, 1);
              paintStep();
            }
          } else quieta5T = 0;
        }
        if (fase === 'espera_golpe' && !muerta &&
            b.pos.z < (DIMS.tableCenterZ - 0.06) && b.vel.z < -0.9) {
          // golpe válido del jugador: la bola cruza hacia el campo lejano
          hitCount++;
          paintStep();
          try { G.haptic(G.paddleHand, 0.4, 80); } catch (e) { /* */ }
          if (hitCount >= DEVOL_META) { advance(); break; }
          fase = 'vuelo_lejos';
          farBounced = false;
          aiReturned = false;   // r64 · cada golpe habilita UNA devolución
        }
        if (fase === 'vuelo_lejos' && !aiReturned && !muerta &&
            b.pos.z < (DIMS.tableCenterZ - 0.1)) {
          if (!farBounced && b.vel.y > 0.35 && b.pos.y < DIMS.tableTopY + 0.5) {
            farBounced = true;
            raquetaPreparar();              // r68 · el rival se arma
          }
          if (farBounced && b.vel.y < 1.1 && _cero) {
            aiReturned = true;
            // r69 · la bola despega al paso de la hoja (golpe honesto)
            armaDevolucion('practica', (p) => {
              try { return computeShotVelocityReal(p, targetProfesor(), 1.05, 5.4, _cero); }
              catch (e) {
                return new THREE.Vector3((Math.random() * 2 - 1) * 0.4, 2.4, 3.1);
              }
            });
          }
        }
        break;
      }
      case 6: {
        // A/X: cambiar la pala de mano DE VERDAD (el núcleo lo hace)
        if (G.paddleHand !== lastHand) { advance(); }
        break;
      }
      default:
        break;
    }
  }
  /* OK de una acción del paso 1: voz + halo siguiente + repintado. Al
   * dominar los mandos (subfase 4) aparece la RAQUETA FANTASMA sobre
   * ellos (r66, petición del dueño) y la voz lo celebra. */
  function accionMandoOk() {
    subfase++;
    chime(true);
    paintStep();
    try { G.haptic(G.paddleHand, 0.4, 70); } catch (e) { /* */ }
    if (subfase === 1) narra(['tutok', 'tutv1c']);
    else if (subfase === 2) narra(['tutok', 'tutv1d']);
    else if (subfase === 3) narra(['tutok', 'tutv1e']);
    else if (subfase === 4) {
      // EL MOMENTO RAQUETA (r67): la única raqueta es la PALA REAL que ya
      // tienes en la mano — aura dorada sobre ella y el mando GLB se
      // desvanece («el mando SE CONVIERTE en tu raqueta»)
      // r77 · MATERIALIZACIÓN EN EL INSTANTE EXACTO: hasta aquí la pala
      // viajó en modo fantasma (invisible, petición del dueño) — aparece
      // JUSTO cuando la voz lo dice, con la aura como destello de nacimiento.
      try { G.setPalaOculta(false); } catch (ePR) { /* sigue igual */ }
      auraMeta = 1;
      mandosVisMeta = 0;
      sway = 0;
      // r70 · LA VOZ DEL VAIVÉN, POR FIN COMPLETA: el banco Piper ya traía
      // el átomo tutv2b («Muévela de lado a lado, con firmeza») — generado
      // en r66 y jamás narrado (el vaivén solo decía 1f+2a). El dueño pide
      // la refuerzo hablado en este momento exacto.
      narra(['tutv1f', 'tutv2a', 'tutv2b']);
    }
  }
  /* ---------------- ciclo de la DEMO DE SAQUE (r67) --------------------
   * El PROFESOR saca desde SU lado sobre la MESA REAL (los mandos ya están
   * en tus manos, nada flota): bote en SU campo (aro rival se ilumina) →
   * cruce → bote en el TUYO (aro tuyo) → «sin devolución: PUNTO». Física,
   * sonidos y aros guía de verdad. El paso 2 lo enseña pausado; el paso 4
   * lo corre en bucle para anotar el marcador.                            */
  function tickDemoSaque(dt, esMarcador) {
    const b = G.ball;
    const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TY = DIMS.tableTopY;
    demoFaseT += dt;
    if (demoTxt && demoTxt.t > 0) {
      demoTxt.t -= dt;
      if (repaintT <= 0) { paintStep(); repaintT = 0.3; }
    }
    switch (demoFase) {
      case 0: {
        // POSTURA: la bola espera en el lado del PROFESOR (r68 · y su
        // raqueta se ARMA: retroceso visible antes de cada saque)
        G.tutBolaViva = false;
        posaBolaDemo();
        if (aroIzq) aroIzq.__ok = false;
        if (aroDer) aroDer.__ok = false;
        const espera = esMarcador ? 0.9 : 2.1;
        if (demoFaseT >= espera - 0.55) raquetaPreparar();
        else raquetaReposo();
        if (demoFaseT >= espera) {
          demoFase = 1; demoFaseT = 0;
          demoBote1 = false; demoBote2 = false;
          raquetaGolpe(b.pos.x, b.pos.y, b.pos.z, 1);   // r68 · la hoja barre
        }
        break;
      }
      case 1: {
        // r68 · SUELTA CON GOLPE VISIBLE: la raqueta del RIVAL barre hacia
        // la bola (que sigue quieta en su campo) y el SAQUE REAL sale
        // cuando la hoja la alcanza — adiós al golpe fantasma
        posaBolaDemo();
        if (demoFaseT < RAQ_T_GOLPE) break;
        try {
          const { v, spin } = findServeVelocity(b.pos, -1, { x: -0.05, spd: 1.22 });
          b.vel.copy(v);
          b.spin.copy(spin);
        } catch (e) {
          b.vel.set(-0.02, 2.6, 2.6);
          b.spin.set(0, 0, 0);
        }
        G.tutBolaViva = true;
        chime(false);
        demoFase = 2; demoFaseT = 0;
        break;
      }
      case 2: {
        // VUELO REAL: bote en SU campo → aro rival; bote en el TUYO → aro tuyo
        // r71 · BOTES REALES SOBRE LA MESA: la condición antigua (z y vel.y)
        // también daba por bueno un bote en el SUELO — un saque largo que se
        // iba fuera del fondo del campo rival «botaba» más allá de la mesa y
        // se encendía el aro igualmente. Ahora un bote cuenta SOLO si cae
        // DENTRO del rectángulo del campo correspondiente (x e z de la mesa)
        // y pegado a la superficie (y bajo TY+12 cm, el suelo está a −76 cm).
        if (!demoBote1 && b.vel.y > 0.3 && b.pos.z < C - 0.06 &&
            b.pos.z > C - HL - 0.03 && Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.02 &&
            b.pos.y < TY + 0.12) {
          demoBote1 = true;
          demoTxt = { txt: T('tut_p1r'), col: 'rgba(232,180,90,0.32)', t: 1.5 };
          if (aroDer) aroDer.__ok = true;
          chime(true);
          if (!esMarcador && demoCiclos === 0) narra(['tutv3b']);
        } else if (demoBote1 && !demoBote2 && b.vel.y > 0.25 && b.pos.z > C + 0.05 &&
                   b.pos.z < C + HL + 0.03 && Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.02 &&
                   b.pos.y < TY + 0.12) {
          demoBote2 = true;
          demoTxt = { txt: T('tut_d3_p2'), col: 'rgba(232,89,12,0.32)', t: 1.5 };
          if (aroIzq) aroIzq.__ok = true;
          chime(true);
        }
        const fuera = b.pos.z > C + HL + 0.3 || b.pos.y < TY - 0.6;
        if (fuera || demoFaseT > 4.5) {
          demoFase = 3; demoFaseT = 0;
          demoTxt = { txt: T('tut_d3_pto'), col: 'rgba(47,158,68,0.35)', t: 1.4 };
          chime(true);
          if (esMarcador) anotaPuntoMarcador();
          else if (demoCiclos === 0) narra(['tutv3c']);
        }
        break;
      }
      case 3: {
        // PUNTO: pausa didáctica y la bola vuelve al lado del profesor
        const pausa = esMarcador ? 0.7 : 1.5;
        if (demoFaseT >= pausa) {
          demoFase = 4; demoFaseT = 0;
          G.tutBolaViva = false;
          posaBolaDemo();
        }
        break;
      }
      case 4: {
        // RESET del ciclo
        const pausa = esMarcador ? 0.45 : 1.0;
        if (demoFaseT >= pausa) {
          demoCiclos++;
          demoFase = 0; demoFaseT = 0;
        }
        break;
      }
      default:
        demoFase = 0; demoFaseT = 0;
        break;
    }
  }
  /* anota el siguiente punto del marcador (paso 5) siguiendo las REGLAS
   * del árbitro: ganador alternado hasta 10-10, luego P·A·P·P a +2; el
   * sacador lo marca la ficha activa (2·2 y cada punto en la igualada) */
  function anotaPuntoMarcador() {
    if (!holoPips || demoPtos >= 24) return;
    const i = demoPtos;
    let ganaPlayer;
    if (i < 20) ganaPlayer = i % 2 === 0;
    else ganaPlayer = [true, false, true, true][i - 20];
    if (ganaPlayer) holoPips.__pi = Math.min(11, (holoPips.__pi || 0) + 1);
    else holoPips.__pd = Math.min(11, (holoPips.__pd || 0) + 1);
    demoPtos++;
    const deuce = demoPtos >= 20;
    if (deuce && !demoDeuce) {
      demoDeuce = true;
      if (holoTokens) holoTokens.cartel10.visible = true;
      narra(['tutv5b']);
      chime(false);
    }
    if (demoPtos >= 22 && holoCartel2) holoCartel2.visible = true;
    if (demoPtos >= 24) {
      // ¡JUEGO! flash del marcador y reinicio didáctico
      demoTxt = { txt: '11 - 10', col: 'rgba(47,158,68,0.4)', t: 2.4 };
      chime(true);
      setTimeout(() => {
        if (!holoPips) return;             // r67 · la academia pudo avanzar ya
        demoPtos = 0; demoDeuce = false;
        holoPips.__pi = 0; holoPips.__pd = 0;
        if (holoTokens) holoTokens.cartel10.visible = false;
        if (holoCartel2) holoCartel2.visible = false;
      }, 2600);
    }
    paintStep();
  }
  /* STICK-CLICK = repetir la última narración (r65) */
  function pollVoz() {
    if (!G.sources) return;
    for (let h = 0; h < 2; h++) {
      const gp = G.sources[h] && G.sources[h].gamepad;
      const b3 = !!(gp && gp.buttons && gp.buttons[3] && gp.buttons[3].pressed);
      if (b3 && !btn3Prev[h] && narrKeys) {
        const ks = narrKeys;
        narra(ks);
      }
      btn3Prev[h] = b3;
    }
  }

  /* visual del holo-marcador (paso 5): pips según el tanteo real, ficha
   * de saque activa (2·2 · cada punto en la igualada) y flash final */
  function tickHolo(dt) {
    if (!holo || !holoPips) return;
    holoT += dt;
    const t = holoT;
    const nI = holoPips.__pi || 0, nD = holoPips.__pd || 0;
    const flash = demoPtos >= 24;
    for (let i = 0; i < 11; i++) {
      holoPips.izq[i].material.opacity = flash ? (0.55 + 0.45 * Math.sin(t * 9))
        : (i < nI ? 0.95 : 0.20);
      holoPips.der[i].material.opacity = flash ? (0.55 + 0.45 * Math.sin(t * 9))
        : (i < nD ? 0.95 : 0.20);
    }
    if (holoTokens) {
      const ip = Math.max(0, demoPtos - 1);
      const deuce = ip >= 20;
      const ladoSaca = deuce ? (ip % 2) : (Math.floor(ip / 2) % 2);
      const usado = deuce ? (ip % 2) : (ip % 2);
      holoTokens.cartel10.visible = deuce && !flash;
      for (let k = 0; k < 4; k++) {
        const lado = k < 2 ? 0 : 1;
        const num = k % 2;
        const activo = lado === ladoSaca && num === usado && demoPtos > 0 && !flash;
        holoTokens.fichas[k].material.opacity =
          activo ? (0.75 + 0.25 * Math.sin(t * 7)) : (lado === ladoSaca ? 0.55 : 0.18);
      }
    }
  }

  /* ---------------- gatillo del tutorial (onSelectStart) ------------- */
  function onTrigger(i) {
    if (!active || !G) return false;
    if (G.menuOpen) return false;   // el menú manda (defensa: no vive en calib)
    switch (step) {
      case 0:
        advance();
        break;
      case 1:
        // r65/r67 · el gatillo es la PRIMERA acción pedida (subfase 0);
        // en el momento raqueta (subfase 4) el avance es automático al
        // completar el vaivén — el gatillo no adelanta
        if (subfase === 0) accionMandoOk();
        break;
      case 2:
        // r67 · demo del profesor: el gatillo pasa a la PRÁCTICA tras ver
        // la mesa; práctica: el gatillo LANZA (el saque de verdad)
        if (submodo === 'demo') {
          if (demoT > 2.5) {
            submodo = 'practica';
            G.rules.state = 'serve';
            G.rules.server = 'player';
            G.resetToss();
            saqCount = 0; saqLatch = false;
            saqBote1 = false; saqBote2 = false;   // r70 · saque en blanco al empezar
            if (aroIzq) aroIzq.__ok = false;
            if (aroDer) aroDer.__ok = false;
            narra(['tutv3d']);
            paintStep();
          }
        } else if (!G.tossed) {
          G.tossFromHand(G.ballHand, true);   // lanzamiento asistido del núcleo
          G.rules.message = T('hint_hit');
          G.tutBolaViva = true;
          saqBote1 = false; saqBote2 = false;   // r70 · saque nuevo, botes nuevos
        }
        break;
      case 3:
        // intercambio real: el gatillo SACA y, ganado el punto, confirma
        if (rfHecho) { advance(); }
        else if (rfFase === 'saque' && !G.tossed) {
          G.tossFromHand(G.ballHand, true);
          G.rules.message = T('hint_hit');
          G.tutBolaViva = true;
          rfFase = 'vuelo';
          farBounced = false; rfVueltaVista = false;
        }
        break;
      case 4:
        // r66 · ENTENDIDO: el gatillo confirma tras ver la demo completa
        if (demoT >= DEMO_MIN) { advance(); }
        break;
      case 7:
        advance();   // r67 · los modos (una pizarra) avanzan por gatillo
        break;
      case 8:
        stop({ aJugar: true, done: true });
        break;
      default:
        break;   // pasos físicos (1 vaivén / 5 práctica / 6 botones): nada aquí
    }
    return true;   // SIEMPRE consumido: nada del núcleo se dispara en la academia
  }

  /* ---------------- B / Y = saltar (polling con borde) --------------- */
  function pollSkip() {
    if (!G.sources) return;
    for (let h = 0; h < 2; h++) {
      const gp = G.sources[h] && G.sources[h].gamepad;
      const b5 = !!(gp && gp.buttons && gp.buttons[5] && gp.buttons[5].pressed);
      if (b5 && !btn5Prev[h]) { stop({ done: false }); return; }
      btn5Prev[h] = b5;
    }
  }

  /* ---------------- arranque de la academia -------------------------- */
  function start(gme) {
    const gm = gme || g();
    if (!gm || active) return;
    if (gm.net && gm.net.online) {
      gm.rules.message = T('tut_bad_online');
      try { gm.closeMenu(); } catch (e) { /* */ }
      return;
    }
    if (gm.champs && gm.champs.testActive) {
      gm.rules.message = T('tut_bad_busy');
      return;
    }
    G = gm;
    try { if (G._instr) G.hideInstrucciones(true); } catch (e) { /* */ }
    if (G.trainV3 || G.trainV3Hub) G.closeTrainingV3();   // estanqueidad
    if (G.champs) { try { G.champs.leaveAll(); } catch (e) { /* */ } }
    G.exitHall();
    G.enterCalib();                       // árbitro dormido, IA dormida
    if (G.calibPanel) G.calibPanel.group.visible = false;
    // r60 (petición del dueño): «se está superponiendo con otras ventanas
    // del menú y no es pulsable» — el menú NACE del clic que abre la
    // academia y si sigue abierto (delante del jugador, renderOrder 9998
    // sobre el 985 del panel, misma altura de ojos) se come los rayos del
    // gatillo y el paso 0 nunca arranca. NO vale closeMenu()/toggleMenu():
    // toggleMenu duerme con `if (this.calib) return` y la academia ESTÁ en
    // calib — se cierra DIRECTO replicando la rama de cierre. Cubre las 3
    // puertas (banner del HUB, oferta de primera vez y AJUSTES). Salida
    // SIEMPRE disponible dentro: B/Y = saltar (pollSkip) · JUGAR YA (paso 8).
    try {
      if (G.menuOpen) {
        G.menuOpen = false;
        G.menuFxInicia('out');   // r81 · la academia sale DE ESCENA
        for (const l of G.menuLines || []) l.visible = false;
        for (const d of G.menuDots || []) d.visible = false;
        G.menuHover = [-1, -1];
        try { G.audio.setMusicWanted(false); } catch (eM1) { /* */ }
        try { G.audio.setArcDuck(false); } catch (eM2) { /* */ }
      }
    } catch (eM0) { /* */ }
    G.trainV3 = null;
    G.trainV3Hub = false;
    G.tutV1 = true;                       // guardias r59 del núcleo
    // r77 · LA RAQUETA MODO FANTASMA (petición del dueño): en las fases
    // iniciales la raqueta se veía pegada al mando ANTES de tiempo, y el
    // momento «tu mando se convierte en tu raqueta» llegaba ya estropeado.
    // La pala REAL nace INVISIBLE: sólo los mandos GLB acompañan al jugador
    // hasta que el guion lo anuncia (subfase 4 → accionMandoOk la destapa).
    try { G.setPalaOculta(true); } catch (ePO) { /* sin fantasma, sigue */ }
    G.mode = 'match';
    G.rules.bestOf = 3;
    G.rules.startMatch('match');          // estado limpio del árbitro
    G.rules.server = 'player';            // r65 · el saque SIEMPRE del jugador:
                                          // con server='ai' corría el saque demo
                                          // del espectador (bote continuo, fix r65)
    G.resetToss();
    G.aiToss = null;
    G.demoToss = null;
    G.rules.message = '';
    G.tutBolaViva = false;                // r66 · bola DORMIDA salvo bola en juego
    try { G.ball.pos.set(0, DIMS.tableTopY + DIMS.ballRadius, DIMS.tableCenterZ + 0.30); } catch (eB0) { /* */ }
    step = 0; subfase = 0; demoT = 0;
    submodo = 'demo'; demoFase = 0; demoFaseT = 0; demoTxt = null;
    demoBote1 = false; demoBote2 = false; demoCiclos = 0;
    demoPtos = 0; demoDeuce = false;
    rfFase = 'saque'; rfVueltas = 0; rfHecho = false; rfVueltaVista = false;
    mandosVis = 0; mandosVisMeta = 1;    // r67 · los mandos nacen EN TUS MANOS
    auraOp = 0; auraMeta = 0;
    sway = 0; hitCount = 0; aiReturned = false; farBounced = false;
    cancelaDevolucion();              // r69 · sin golpes pendientes al entrar
    deadT = 0; flashAgain = 0; flashOk = 0; saqCount = 0; saqLatch = false;
    saqBote1 = false; saqBote2 = false;   // r70 · saque en blanco al entrar
    fase = 'espera_golpe';
    mandoT = 0; hlParte = null;
    narrKeys = null; narrRetry = 0;
    btn5Prev[0] = true; btn5Prev[1] = true;   // un B/Y recién soltado no salta
    btn1Prev[0] = true; btn1Prev[1] = true;
    btn3Prev[0] = true; btn3Prev[1] = true;
    btn4Prev[0] = true; btn4Prev[1] = true;
    active = true;
    buildPanel();
    enterStep();
    paintStep();
    if (grp) grp.visible = true;
    chime(false);
    try { G.haptic(G.paddleHand, 0.5, 110); } catch (e) { /* */ }
  }

  /* ---------------- cierre (jugar ya · saltar · fin) ----------------- */
  function stop(opts) {
    if (!active || !G) return;
    opts = opts || {};
    const gm = G;
    active = false;
    // r63 · ORDEN CRÍTICO (bug del dueño: «la última pantalla se queda fija
    // y no hay forma de eliminarla»): teardownPanel necesita G.rig para
    // QUITAR el panel de la escena — con G ya anulado el if cortocircuitaba
    // y el panel quedaba HUÉRFANO y VISIBLE delante del jugador para
    // siempre (el módulo ya no lo controla: activo=false). El panel se
    // desmonta PRIMERO, con G vivo; el fallback por grp.parent de
    // teardownPanel (también r63) cubre cualquier orden futuro.
    limpiarHolo();                        // r65 · el holo-reglas sale con el guion
    limpiarAros();                        // r67 · los aros guía también
    limpiarRaqueta();                     // r68 · la raqueta del rival también
    // r70 · BLINDAJE DE SALIDA — NADA de la academia sobrevive al Hall:
    // (1) la VOZ muere AHORA (el dueño: «al pulsar B y aparecer en el Hall
    // la voz sigue sonando y debe terminar») — buffer vivo + respaldo;
    // (2) sin reintentos de narración pendientes (tickNarr ya no corre,
    //     pero el estado queda limpio para la próxima sesión);
    // (3) sin golpes pendientes (devPend a cero);
    // (4) el árbitro vuelve a estado limpio (la academia tocaba
    //     state/server — que no se cuele un 'rally' fantasma al Hall).
    try { if (gm.audio && gm.audio.callaVoz) gm.audio.callaVoz(); } catch (eV) { /* */ }
    narrKeys = null; narrRetry = 0; narrTries = 0;
    cancelaDevolucion();
    try { gm.rules.state = 'point'; gm.rules.message = ''; } catch (eR) { /* */ }
    // r77 · BLINDAJE DE SALIDA (fantasma incluido): cualquier camino fuera
    // de la academia — jugar ya, saltar con B/Y o fin del guion — devuelve
    // la pala REAL a la mano. Nadie se queda sin raqueta jamás.
    try { gm.setPalaOculta(false); } catch (ePS) { /* */ }
    try { if (gm.aiPaddleMesh) gm.aiPaddleMesh.visible = true; } catch (eI0) { /* */ }
    teardownPanel();
    G = null;
    gm.tutV1 = null;
    gm.tutBolaViva = null;                // r66 · la bola vuelve al núcleo
    // M4 (r111) · TELEMETRÍA DEL EMBUDO: cómo acaba la academia ahora que
    // ya no bloquea la primera entrada (el HUB nace en ▶ JUGAR). done =
    // guion completo · aJugar = botón ▶ JUGAR YA · skip = B/Y.
    try {
      window.__PP_TELE.ev('tut_end', {
        res: opts.aJugar ? 'aJugar' : (opts.done ? 'done' : 'skip'),
        paso: typeof gm.tutPaso === 'number' ? gm.tutPaso : -1,
      });
    } catch (eTE) { /* la telemetría nunca rompe */ }
    if (opts.done) {
      try { localStorage.setItem('pp_tut_done', '1'); } catch (e) { /* */ }
      try { gm.audio.announce(T('tut_done_msg'), true); } catch (e) { /* */ }
      try { gm.confettiBurst = Math.max(gm.confettiBurst || 0, 6); } catch (e) { /* */ }
    }
    if (opts.aJugar) {
      gm.exitCalib();        // restaura MODO PARTIDO limpio (startMatch dentro)
      try { gm.closeMenu(); } catch (e) { /* */ }
      try { gm.haptic(gm.paddleHand, 0.6, 140); } catch (e) { /* */ }
    } else {
      gm.menuPage = 'main';
      const aCasa = gm.goHomeHall ? gm.goHomeHall() : false;
      if (aCasa) {
        if (!gm.menuOpen) gm.toggleMenu();
        else { gm.anchorMenu(); gm.drawMenu(); }
      } else {
        gm.exitCalib();      // passthrough online: al menos fuera de calib
        try { gm.closeMenu(); } catch (e) { /* */ }
      }
    }
  }

  /* ---------------- página «¿PRIMERA VEZ?» del menú ------------------ */
  function drawAsk(gme, c, rects, btn, label) {
    label(T('tutask_title'), 250, 56, '#e8b45a', 'center');
    label(T('tutask_sub'), 320, 27, '#9aa7b4', 'center');
    c.strokeStyle = 'rgba(232,180,90,0.35)';
    c.lineWidth = 2;
    c.beginPath(); c.moveTo(132, 372); c.lineTo(892, 372); c.stroke();
    btn('tut:go', 132, 446, 760, 168, T('tutask_yes'), true, 'green', undefined, 44);
    btn('tut:no', 132, 672, 760, 168, T('tutask_no'), false, undefined, undefined, 44);
    label(T('tut_hint_skip'), 936, 22, '#9aa7b4', 'center');
    gme.menuRects = rects;
    gme._menuState = gme.rules.state;
    if (gme.menuTex) gme.menuTex.needsUpdate = true;
  }

  /* ---------------- acciones de menú (banner / oferta / ajustes) ----- */
  function menuAction(gme, arg) {
    if (arg === 'go') start(gme);
    else if (arg === 'no') {
      gme.menuPage = 'main';
      gme.drawMenu();
      try { gme.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0); } catch (e) { /* */ }
    }
  }

  /* ---------------- registro público del módulo ---------------------- */
  window.__PP_TUT = {
    version: 'r70-academia-perfecta-todo-al-rig',
    STEPS,
    start, stop, tick, onTrigger, drawAsk, menuAction,
    // introspección para QA (solo lectura, sin tocar estado)
    // r67 · mandos anclados a grips, escala 75%, aura de la pala real
    estado() {
      let pose = 'frente';
      try { pose = poseDestino().nombre; } catch (e) { /* */ }
      let ancladosEnGrips = false, dosAnclados = false;
      try {
        dosAnclados = !!(anclados && anclados.length === 2 &&
          anclados[0].glb && anclados[1].glb);
        ancladosEnGrips = !!(dosAnclados && G && G.grips &&
          anclados[0].mont.parent === G.grips[0] &&
          anclados[1].mont.parent === G.grips[1]);
      } catch (e) { /* */ }
      return {
        activo: active,
        paso: step,
        total: STEPS,
        subfase,
        sway, hitCount, fase,
        saq: saqCount, metaSaq: SAQ_META, metaDevol: DEVOL_META,
        pose,
        demoT,
        voz: narrKeys ? narrKeys[0] : null,
        holo: !!holo,
        // r67 · anclaje REAL: hijo de los grips XR, no del rig
        anclados: dosAnclados,
        ancladosEnGrips,
        mandoAnclado: !!(anclados && anclados.length === 2),
        mandosPose: mandosVisMeta > 0.5 ? 'manos' : 'oculto',
        mandosVis: Math.round(mandosVis * 100) / 100,
        mandosVisMeta,
        escalaMando: MANDO_ESC,
        aura: Math.round(auraOp * 100) / 100,
        auraMeta,
        // r77 · modo fantasma de la pala REAL (introspección de QA)
        palaOculta: !!(G && G.tutPalaOculta),
        palaVisible: !!(G && G.paddleMounts && G.paddleMounts[G.paddleHand] &&
          G.paddleMounts[G.paddleHand].visible),
        tieneMando: !!mando,
        mandoHl: hlParte,
        etiqueta: hlParte ? (etiqueta ? Math.round(etiqueta.material.opacity * 100) / 100 : 0) : 0,
        tienePanel: !!grp,
        panelVisible: !!(grp && grp.visible),
        aros: !!arosGrp,
        submodo,
        demoFase,
        demoTxt: demoTxt ? demoTxt.txt : null,
        rfFase,
        rfHecho,
        demoPtos,
        demoDeuce,
        bolaViva: !!(G && G.tutBolaViva),
        // r68 · la raqueta del rival (introspección de QA)
        raquetaRival: !!raqGrp,
        raqModo,
        // r70 · anclaje y visibilidad de la raqueta (colocación perfecta)
        raqVisible: !!(raqGrp && raqGrp.visible),
        raqAnclada: !!(raqGrp && G && raqGrp.parent === G.rig),
        raqPos: raqGrp
          ? [Math.round(raqGrp.position.x * 1000) / 1000,
             Math.round(raqGrp.position.y * 1000) / 1000,
             Math.round(raqGrp.position.z * 1000) / 1000]
          : null,
        saqBote1, saqBote2,
        // r71 · botes de la demo del profesor + palma (introspección de QA)
        demoBote1, demoBote2,
        palma: bolaPalmDemo()
          ? [Math.round(bolaPalmDemo().x * 1000) / 1000,
             Math.round(bolaPalmDemo().y * 1000) / 1000,
             Math.round(bolaPalmDemo().z * 1000) / 1000]
          : null,
        arosAnclados: !!(arosGrp && G && arosGrp.parent === G.rig),
        holoAnclado: !!(holo && G && holo.parent === G.rig),
        // r69 · golpe honesto + una sola raqueta (introspección de QA)
        devPend: Math.round(devPend * 1000) / 1000,
        aiPadOculta: !!(G && G.aiPaddleMesh && !G.aiPaddleMesh.visible),
        raqContacto: raqContacto
          ? [Math.round(raqContacto.x * 1000) / 1000,
             Math.round(raqContacto.y * 1000) / 1000,
             Math.round(raqContacto.z * 1000) / 1000]
          : null,
      };
    },
  };
})();



