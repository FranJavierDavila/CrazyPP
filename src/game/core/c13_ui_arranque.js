function renderPlayBtn() {
  const en = TLang() === 'en';
  if (playEs && playEn) {
    playEs.style.display = en ? 'none' : '';
    playEn.style.display = en ? '' : 'none';
  }
}
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { T, TLang, WORLDRANK, __ppLang, applyLangDOM, ppPlayerName, setLang } from './c00_pre_three.js';
import { fixInvertedMeshes, loadGunModel, loadPaddleModel, makeGunVisual } from './c01_modelos_3d.js';
import { AI_PRESETS, DIMS, SERVE_ASSIST_TIERS, SERVE_TUNE, scalePreset } from './c02_cfg_escena.js';
import { CCD_TUNE, bladeNormalLocal, createPaddleSim, sdfBlade, setPaddleBasis, sweepBallVsBlade, tmpPrev } from './c04_fisica_ccd.js';
import { __ppServeTelemetry, applyServeProgressiveAssist, collidePaddleSweep, computeShotVelocityReal, findServeVelocity, simulateServePath, stepPhysics, testPaddleContact } from './c05_colisiones_ia_golpeo.js';
import { NetLink } from './c09_red_netlink.js';
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
  const game = new PingPongGame(document.getElementById('c'), paddleModel, {
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
      } else {
        overlay.classList.remove('hidden');
        statusEl.textContent = T('status_pause');
        window.__ppMusic?.resume();   // de vuelta en la portada suena otra vez
      }
    },
  });
  window.__game = game;
  window.__NetLink = NetLink;   // accesible para pruebas headless (módulo ES)
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
    };
    let S = (() => {
      try {
        const raw = localStorage.getItem(KEY);
        if (!raw) return JSON.parse(JSON.stringify(DEF));
        const d = Object.assign(JSON.parse(JSON.stringify(DEF)), JSON.parse(raw));
        d.fb = Object.assign({ marks: 1, line: 1, spin: 1 }, d.fb || {});
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
        m_t2a: 'PASE BAJO', m_t2a_d: 'Golpea drives profundos pasando ENTRE la red y la cinta naranja (17 cm). Si pasas por encima, el rival te remata.',
        m_t2b: 'GLOBO DEFENSIVO', m_t2b_d: 'Levanta {n} globos seguidos por encima del aro y que boten en el fondo rival. Gana tiempo cuando estás en apuros.',
        m_t3a: 'LEER EL CORTADO', m_t3a_d: 'La máquina lanza bolas con corte pesado. Devuélvelas {n} veces seguidas con la pala abierta: sin tocar la red y sin levantarla.',
        m_t3b: 'BLOQUEAR EL TOPSPIN', m_t3b_d: 'Bolas con lift fuerte y velocidad variable. Bloquea o contraataca {n} veces seguidas con la pala cerrada.',
        m_t4a: 'SAQUE CORTO · DOBLE BOTE', m_t4a_d: 'Saca y consigue que la bola BOTE DOS VECES en la zona marcada junto a la red. El saque corto evita el ataque rival.',
        m_t4b: 'SAQUE LARGO · AL FONDO', m_t4b_d: 'Coloca {n} primeros botes en la franja de los últimos 15 cm. Saque rápido y tenso pegado al fondo.',
        m_t5a: 'METRÓNOMO', m_t5a_d: 'Bolas a ritmo constante: devuelve el máximo número seguidas. Hitos a 30 · 50 · 100 con bonus.',
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
      },
      en: {
        hub_t: 'PRO TRAINING', hub_s: 'High performance center · CRAZY PING PONG',
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
        m_t2a: 'LOW PASS', m_t2a_d: 'Hit deep drives passing BETWEEN the net and the orange ribbon (17 cm). Over it and they smash you.',
        m_t2b: 'DEFENSIVE LOB', m_t2b_d: 'Lift {n} lobs in a row above the hoop landing deep. Buy time when you are in trouble.',
        m_t3a: 'READ THE CHOP', m_t3a_d: 'The machine fires heavy backspin. Return them {n} times in a row with an open blade: no net, no pop-up.',
        m_t3b: 'BLOCK THE TOPSPIN', m_t3b_d: 'Strong topspin at varying speed. Block or counter {n} times in a row with a closed blade.',
        m_t4a: 'SHORT SERVE · DOUBLE BOUNCE', m_t4a_d: 'Serve so the ball BOUNCES TWICE in the marked zone near the net. Short serves prevent attacks.',
        m_t4b: 'LONG SERVE · DEEP', m_t4b_d: 'Land {n} first bounces in the last 15 cm strip. Fast, tight serves to the baseline.',
        m_t5a: 'METRONOME', m_t5a_d: 'Balls at a steady beat: return as many as you can in a row. Milestones at 30 · 50 · 100 with bonuses.',
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
      },
    };
    const t = (k, vars) => {
      let s = (TR[LANG] && TR[LANG][k]) || TR.es[k] || k;
      if (vars) for (const kk of Object.keys(vars)) s = s.split('{' + kk + '}').join(String(vars[kk]));
      return s;
    };
  
    /* ---------------- niveles y skins ---------------- */
    const LEVELS = [
      { min: 0, k: 'lvl0' }, { min: 150, k: 'lvl1' }, { min: 400, k: 'lvl2' },
      { min: 800, k: 'lvl3' }, { min: 1500, k: 'lvl4' },
    ];
    const levelOf = (p) => { let l = LEVELS[0]; for (const it of LEVELS) if (p >= it.min) l = it; return l; };

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
    const ACHS = ['r10', 'r20', 'p1', 'p5', 'all9', 'm50', 'm100', 'x3', 'leg'];
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
      return comboMulN(active === 't5a' ? st.rally : st.streak);
    }
    function comboMulN(r) { return r >= 8 ? 3 : (r >= 4 ? 2 : 1); }
    function starsFor(faults) { return faults === 0 ? 3 : (faults <= 2 ? 2 : 1); }
    function recordStars(mode, n) {
      if (!GAMF() || !n) return;
      if ((S.stars[mode] || 0) < n) { S.stars[mode] = n; save(); panelDirty = true; }
    }
    function recordAcc(mode, pct) {
      if (!GAMF() || !isFinite(pct)) return;
      if ((S.acc[mode] || 0) < pct) { S.acc[mode] = pct; save(); panelDirty = true; }
    }
    function checkStreakAch() {
      const r = active === 't5a' ? st.rally : st.streak;
      if (r >= 10) grant('r10');
      if (r >= 20) grant('r20');
    }
    function checkGlobalAch() {
      const modes = Object.keys(MODES);
      if (modes.every((m) => (S.stars[m] || 0) >= 1)) grant('all9');
      if (modes.filter((m) => S.stars[m] === 3).length >= 5) grant('p5');
      if (S.pts >= 1500) grant('leg');
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
     *   anim     matiz animado (arcoíris) sobre la textura */
    const SKINS = [
      { id: 'clasica', name: { es: 'Clásica', en: 'Classic' }, min: 0, grip: 0x6b4a2f },
      { id: 'fuego', name: { es: 'Fuego', en: 'Fire' }, min: 150, tex: 'fuego', edge: 0xff5a2a, grip: 0xc22a12 },
      { id: 'hielo', name: { es: 'Hielo', en: 'Ice' }, min: 400, tex: 'hielo', edge: 0x35c4e8, grip: 0x1479a3 },
      { id: 'oro', name: { es: 'Oro', en: 'Gold' }, min: 800, tex: 'oro', edge: 0xf2c14e, grip: 0x3a2c10 },
      { id: 'arcoiris', name: { es: 'Arcoíris', en: 'Rainbow' }, min: 1500, tex: 'holo', edge: 0xb07aff, grip: 0x8e44ad, anim: true },
      { id: 'carbon', name: { es: 'Pro Carbon', en: 'Pro Carbon' }, min: 2500, tex: 'carbon', edge: 0xff2d2d, grip: 0x17181c, modelUrl: 'assets/pala/pala_pro.glb' },
    ];
  
    /* ---------------- registro de modos ---------------- */
    const AREAS = [
      { id: 'dir', ik: 'a_dir', sk: 'a_dir_s', g0: '#2b6cb0', g1: '#16324f', col: '#63b3ed' },
      { id: 'alt', ik: 'a_alt', sk: 'a_alt_s', g0: '#2f855a', g1: '#1a4433', col: '#68d391' },
      { id: 'spin', ik: 'a_spin', sk: 'a_spin_s', g0: '#805ad5', g1: '#44337a', col: '#d6bcfa' },
      { id: 'saque', ik: 'a_saq', sk: 'a_saq_s', g0: '#c05621', g1: '#652a12', col: '#f6ad55' },
      { id: 'rit', ik: 'a_rit', sk: 'a_rit_s', g0: '#b83280', g1: '#5f1e42', col: '#f687b3' },
    ];
    const MODES = {
      t1a: { area: 'dir', nk: 'm_t1a', dk: 'm_t1a_d', n: 5, ok: 'ok_zona', pts: 1, bonus: 15 },
      t1b: { area: 'dir', nk: 'm_t1b', dk: 'm_t1b_d', n: 5, ok: 'ok_banda', pts: 2, bonus: 20 },
      t2a: { area: 'alt', nk: 'm_t2a', dk: 'm_t2a_d', n: 5, ok: 'ok_bajo', pts: 2, bonus: 20 },
      t2b: { area: 'alt', nk: 'm_t2b', dk: 'm_t2b_d', n: 4, ok: 'ok_globo', pts: 2, bonus: 20 },
      t3a: { area: 'spin', nk: 'm_t3a', dk: 'm_t3a_d', n: 5, ok: 'ok_leido', pts: 2, bonus: 20 },
      t3b: { area: 'spin', nk: 'm_t3b', dk: 'm_t3b_d', n: 6, ok: 'ok_bloqueo', pts: 2, bonus: 25 },
      t4a: { area: 'saque', nk: 'm_t4a', dk: 'm_t4a_d', n: 3, ok: 'ok_doble', pts: 3, bonus: 15 },
      t4b: { area: 'saque', nk: 'm_t4b', dk: 'm_t4b_d', n: 3, ok: 'ok_fondo', pts: 3, bonus: 15 },
      t5a: { area: 'rit', nk: 'm_t5a', dk: 'm_t5a_d', n: 30, ok: 'ok_beat', pts: 1, bonus: 15 },
    };
  
  
    /* =================================================================
     *  ESTADO DE SESIÓN Y REFERENCIAS
     *  ================================================================= */
    let G = null;                    // instancia del juego (window.__PP_GAME)
    let grp = null;                  // grupo de escena del módulo
    let active = null;               // id del modo en curso (MODES key) o null
    let uiPage = 'hub';              // 'hub' | 'area'
    let uiArea = 'dir';
    let rainbowT = 0;
  
    const st = {
      streak: 0, goal: 0, sessPts: 0, rally: 0, bounces: 0,
      live: false, deadT: 0, wait: 0.8, phase: 'feed',
      cross: null, apex: 0, hitPos: null, bouncePos: null, lastBounce: null,
      target: null, toast: '', toastT: 0, feedT: 0, beat: 0, shotRec: false,
      aiTouched: false,   // v3.0.2 · la bola ya botó en el campo rival tras el golpe (metrónomo)
      shotPts: [], spinIconT: 0, spinIconCol: null, done: 0,
      tossReleaseY: 0, tossMaxY: 0,   // v3.0.8-TRN1 · validación del lanzamiento (como el núcleo)
      roundHits: 0, roundFaults: 0,   // v3.0.7-PLAY1 · precisión de la ronda en curso
    };
  
    /* ---------------- constantes geométricas locales ---------------- */
    const C = () => DIMS.tableCenterZ;
    const TOP = () => DIMS.tableTopY;
    const HW = () => DIMS.tableHalfWidth;
    const HL = () => DIMS.tableHalfLength;
    const RIBBON_Y = () => DIMS.netTopY + 0.17;          // cinta a 17 cm sobre la red
    const APEX_Y = 1.50;                                  // aro del globo defensivo
    const CROSS_LOW = () => DIMS.netTopY + 0.055;         // pase bajo correcto
    const CROSS_HI = () => DIMS.netTopY + 0.16;           // demasiado alto
  
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
      g.position.set(0, 0, C());
      g.visible = false;
      return g;
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
      g.position.set(0, APEX_Y, C() + 0.5);
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
        const big = active === 't5a' ? String(st.rally) : (String(st.streak) + ' / ' + M.n);
        g.textAlign = 'center';
        g.fillStyle = '#ffffff';
        g.font = '900 110px system-ui, sans-serif';
        g.fillText(big, W / 2, 216);
        g.fillStyle = '#8fa0b8';
        g.font = '700 26px system-ui, sans-serif';
        g.fillText(active === 't5a' ? t('hud_rally') : t('hud_racha') + ' · ' + t('hud_meta'), W / 2, 292);
        // toast
        if (st.toastT > 0) {
          g.fillStyle = st.toastOk ? '#68d391' : '#fc8181';
          g.font = '800 34px system-ui, sans-serif';
          g.fillText(st.toast, W / 2, 340);
        } else {
          g.fillStyle = '#a9b8cc';
          g.font = '600 24px system-ui, sans-serif';
          g.fillText(active === 't4a' || active === 't4b' ? t('sirve') : t('obj') + ': ' + M.n + ' ' + t('seg'), W / 2, 340);
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
          if (tries > 0 && active !== 't5a') {
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
        ? (st.rally === 30 || st.rally === 50 || st.rally === 100)
        : (st.streak >= M.n);
      if (hitGoal) {
        const bonus = active === 't5a' ? (st.rally === 30 ? 15 : st.rally === 50 ? 25 : 50) : M.bonus;
        addPts(bonus);
        if (active === 't5a') recordBest(active, st.rally);
        // v3.0.7-PLAY1 · estrellas + precisión + celebración al completar
        let suffix = '';
        if (GAMF()) {
          if (active === 't5a') {
            const stR = st.rally >= 100 ? 3 : (st.rally >= 50 ? 2 : 1);
            recordStars('t5a', stR);
            if (st.rally >= 50) grant('m50');
            if (st.rally >= 100) grant('m100');
          } else {
            const tries = st.roundHits + st.roundFaults;
            const acc = tries ? Math.round(st.roundHits / tries * 100) : 100;
            const stars = starsFor(st.roundFaults);
            recordStars(active, stars);
            recordAcc(active, acc);
            if (stars === 3) grant('p1');
            suffix = '  ' + '\u2605'.repeat(stars) + '\u2606'.repeat(3 - stars);
          }
          burst({ x: 0, y: TOP() + 0.5, z: C() }, active !== 't5a' && st.roundFaults === 0);
          checkGlobalAch();
        }
        toast(active === 't5a'
          ? t('hito', { n: st.rally, n2: bonus })
          : t('hecho', { n: bonus }) + suffix, true);
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
      if (active === 't5a' && st.rally > 0) {
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
        g.fillStyle = 'rgba(230,70,70,0.55)';
        g.fillRect(mx(-0.15), 0, mx(0.15) - mx(-0.15), H);
        g.strokeStyle = 'rgba(255,110,110,0.95)'; g.lineWidth = 4;
        g.strokeRect(mx(-0.15), 2, mx(0.15) - mx(-0.15), H - 4);
        g.fillStyle = 'rgba(255,150,150,1)';
        g.font = '700 26px system-ui, sans-serif'; g.textAlign = 'center';
        g.save();
        // v3.6.20 · TEXTO LEGIBLE + i18n: con flipY=false el jugador ve el
        // lienzo con la fila 0 en la RED (cerca) y la fila H al fondo (lejos);
        // para leerse de pie el texto debe dibujarse con la parte alta hacia
        // la fila H y avanzando hacia +x: eso es scale(1,-1). rotate(π) lo
        // dejaba en ESPEJO (orden de lectura invertido — informe del dueño
        // v3.6.19, confirmado por IoU GPU 0.999 vs 0.811).
        g.translate(mx(0), H - 26); g.scale(1, -1);
        g.textBaseline = 'middle';
        g.fillText(t('z_evita'), 0, 0);
        g.restore();
        // zona objetivo dorada
        // v3.0.8-TRN1 · ZONA FIEL AL JUEZ: lo pintado ES lo juzgado. Antes la
        // zona dorada cubría toda la mitad (incluida la franja central que
        // zoneOf() rechaza como 'C' EVITA) y el texto OBJETIVO a 64 px se
        // salía del rectángulo (se cortaba). Ahora la zona empieza donde el
        // juez acepta (|x| ≥ 15 cm) y el texto se reescala con measureText
        // para caber SIEMPRE dentro del área concreta.
        if (st.target) {
          const zr = st.target.z === 'deep' ? [C() - HL(), C() - HL() / 2] : [C() - HL() / 2, C() - HL() / 4];
          const xr = st.target.x < 0 ? [-HW(), -0.15] : [0.15, HW()];
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
        // bandas: laterales 10 cm + fondo 12 cm
        // v3.0.6-SRV1 · FIX zona FONDO: el eje Z del lienzo está INVERTIDO
        // respecto a mz() (fila 0 = red, fila H = fondo rival); pintar desde
        // la fila 0 cubría TODA la mesa MENOS la franja objetivo. Con el mismo
        // patrón rect(mz(z0), mz(z1)−mz(z0)) de t4a/t4b la franja cae EXACTA.
        g.fillStyle = 'rgba(99,179,237,0.8)';
        g.fillRect(0, 0, mx(-HW() + 0.10), H);
        g.fillRect(mx(HW() - 0.10), 0, W - mx(HW() - 0.10), H);
        const zb = [C() - HL(), C() - HL() + 0.12];   // franja de fondo real
        g.fillRect(0, mz(zb[0]), W, mz(zb[1]) - mz(zb[0]));
        g.strokeStyle = '#9fd4ff'; g.lineWidth = 9;
        g.strokeRect(4.5, 4.5, W - 9, H - 9);
        g.fillStyle = '#0c1826'; g.font = '900 40px system-ui, sans-serif'; g.textAlign = 'center';
        g.save(); g.translate(W / 2, (mz(zb[0]) + mz(zb[1])) / 2); g.scale(1, -1); g.textBaseline = 'middle'; g.fillText(t('z_fondo'), 0, 0); g.restore();
      } else if (mode === 't4a') {
        // zona de doble bote junto a la red (lado rival)
        const zr = [C() - 0.56, C() - 0.05];
        g.fillStyle = 'rgba(246,173,85,0.82)';
        g.fillRect(0, mz(zr[0]), W, mz(zr[1]) - mz(zr[0]));
        g.strokeStyle = '#ffc178'; g.lineWidth = 10;
        g.strokeRect(5, mz(zr[0]) + 5, W - 10, mz(zr[1]) - mz(zr[0]) - 10);
        g.fillStyle = '#241206'; g.font = '900 40px system-ui, sans-serif'; g.textAlign = 'center';
        g.save(); g.translate(W / 2, (mz(zr[0]) + mz(zr[1])) / 2); g.scale(1, -1); g.textBaseline = 'middle';
        g.fillText(t('z_doble'), 0, 0); g.restore();
      } else if (mode === 't4b') {
        // franja de fondo: últimos 15 cm
        const zr = [C() - HL(), C() - HL() + 0.15];
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
      quadMesh.visible = (active === 't1a' || active === 't1b' || active === 't4a' || active === 't4b');
      ribbonG.visible = (active === 't2a');
      apexG.visible = (active === 't2b');
      metroG.visible = (active === 't5a');
      panel.visible = !!active;
      if (quadMesh.visible) drawQuad(active);
    }
  
  
    /* =================================================================
     *  TICK · se llama cada frame desde el bucle del núcleo
     *  (siempre: actualiza cosmética global; entrena sólo si hay modo)
     *  ================================================================= */
    function modeFeed() {
      // alimentación específica por modo (máquina o soporte de saque)
      if (active === 't1a' || active === 't1b' || active === 't2a' || active === 't2b' || active === 't5a') {
        // v3.0.8-TRN1 · MÁQUINA DE SPARRING: bolas de rally directas y
        // profundas (tiro resuelto con Magnus, despeje de red garantizado)
        // en vez de saques del solver que a veces caían lentos y cortos. La
        // dificultad de cada modo sigue viviendo en lo que devuelve EL JUGADOR.
        feedToPlayer({ rally: true, max: active === 't5a' ? 7.2 : 7.8 });
        st.phase = 'rally';
        if (active === 't5a') st.live = true;   // el beat vigila el fallo aunque el jugador no la toque
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
      const dz = C() - p.z;
      const row = dz > HL() * 0.5 ? 'deep' : dz > HL() * 0.25 ? 'mid' : 'short';
      const col = p.x < -0.15 ? 'L' : p.x > 0.15 ? 'R' : 'C';
      return { row, col };
    }
  
    function judgeAiBounce(p) {
      // p = posición del bote en el campo rival (primer bote tras el golpe)
      if (active === 't1a') {
        const z = zoneOf(p);
        if (st.target && z.row === st.target.z && ((st.target.x < 0 && z.col === 'L') || (st.target.x > 0 && z.col === 'R'))) {
          okHit(MODES[active].ok, MODES[active].pts);
        } else if (z.col === 'C') {
          st.done = 0; failHit('mal_corta');
        } else {
          st.done = 0; failHit('mal_fuera');
        }
      } else if (active === 't1b') {
        const band = Math.abs(p.x) > HW() - 0.10 || p.z < C() - HL() + 0.12;
        if (band) okHit(MODES[active].ok, MODES[active].pts);
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
        const inZone = Math.abs(p.x) < HW() && p.z > C() - 0.56 && p.z < C() - 0.05;
        if (st.aiBounce === 0) {
          if (!inZone) { st.done = 0; failHit('mal_larga'); }
          else { st.aiBounce = 1; st.live = true; }          // espera el 2.º bote
        } else {
          okHit(MODES[active].ok, MODES[active].pts);        // doble bote ✓
        }
      } else if (active === 't4b') {
        const deep = p.z < C() - HL() + 0.15;
        if (deep) {
          if (st.cross && st.cross.spd > 4.5) addPts(1);   // bonus saque tenso
          okHit(MODES[active].ok, MODES[active].pts);
        } else { st.done = 0; failHit('mal_corta'); }        // v3.0.2: era 'mal_larga' (semántica invertida)
      } else if (active === 't5a') {
        // v3.0.2 · FIX metrónomo: el rally NUNCA se incrementaba (el juez no
        // tenía rama t5a) — el contador quedaba en 0 y no sumaba puntos.
        // aiTouched cierra el cómputo: los rebotes EXTRA de la misma bola no suman.
        if (!st.aiTouched) {
          st.aiTouched = true;
          st.rally++;
          addPts(MODES[active].pts);
          G.audio.playOsc(760, 1180, 0.07, 'sine', 0.13, 0);
          if (st.rally === 30 || st.rally === 50 || st.rally === 100) {
            const bonus = st.rally === 30 ? 15 : st.rally === 50 ? 25 : 50;
            addPts(bonus);
            recordBest(active, st.rally);
            toast(t('hito', { n: st.rally, n2: bonus }), true);
            G.audio.playOsc(660, 990, 0.1, 'triangle', 0.14, 0);
            G.audio.playOsc(880, 1320, 0.1, 'triangle', 0.14, 0.11);
            G.audio.playOsc(990, 1760, 0.14, 'triangle', 0.14, 0.22);
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
            if (active === 't5a') {
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
        if (st.wait <= 0) { modeFeed(); st.wait = active === 't5a' ? 1.65 : 2.2; }
      } else if (active === 't5a') {
        // v3.0.2 · FIX «la bola desaparece»: el beat ya NO roba la bola en
        // vuelo. Sólo sustituye cuando la anterior está ASENTADA (muerta, ya
        // botó en el campo rival o pasó de largo). Si el beat vence y el
        // jugador no la devolvió, el rally termina ANTES de alimentar.
        st.feedT += dt;
        const settled = !st.live || st.aiTouched || ballDead() || b.pos.z > C() + HL() + 0.4;
        if (st.feedT >= 1.65 && settled) {
          if (st.live && !st.aiTouched) failHit('mal_fuera');
          st.feedT = 0; modeFeed();
        }
      }
      // 5) metrónomo visual
      if (active === 't5a') {
        st.beat += dt;
        const ph = (st.beat % 1.65) / 1.65;
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
        const col = new THREE.Color().setHSL(rainbowT % 1, 0.75, 0.55);
        for (const m of skinMats) if (m.userData && m.userData.ppAnim) m.color.copy(col);
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
    function startMode(game, id) {
      if (!game) return;
      if (!MODES[id]) return;
      G = game;
      buildScene();
      LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
      active = id;
      const M = MODES[id];
      if (!game.calib) game.enterCalib();      // aísla: sin árbitro, sin IA, sin marcador
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
    /** El subapartado 0: posición de la pala (panel clásico). */
    function startCalib(game) {
      G = game;
      active = null;
      if (grp) { grp.visible = false; applyModeScene(); }
      if (game.trainV3) game.trainV3 = null;
      game.exitHall();                        // v3.1.0-SRV2: el ajuste vive en la cancha
      game.trainV3Hub = true;                 // v3.0.3 · salida con Y → hub
      game.enterCalib();
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
    /** Icono en AMBAS caras cuando el jugador aplica efecto (en TODO el juego). */
    function pulseFaceIcons(lift) {
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
      c.fillStyle = '#7d8ea6';
      c.font = '600 24px system-ui, sans-serif';
      c.fillText(subTxt || t('hub_s'), 40, 122);
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
        c.fillStyle = '#7d8ea6';
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
      const CW = 456, CH = 150, GX = 32, GY = 16, X0 = 40, X1 = X0 + CW + GX;
      let y = 190;
      const card = (x, yy, id, ik, sk, g0, g1, col, act) => {
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
        c.restore();
      };
      for (let i = 0; i < AREAS.length; i++) {
        const a = AREAS[i];
        card(i % 2 === 0 ? X0 : X1, y + Math.floor(i / 2) * (CH + GY), a.id, a.ik, a.sk, a.g0, a.g1, a.col);
      }
      // tarjeta POSICIÓN DE LA PALA (subapartado 0) a lo ancho
      const yPal = y + 3 * (CH + GY);
      btn('trv3:calib', X0, yPal, CW * 2 + GX, 96, '', false);
      c.save();
      c.beginPath();
      if (c.roundRect) c.roundRect(X0, yPal, CW * 2 + GX, 96, 20); else c.rect(X0, yPal, CW * 2 + GX, 96);
      c.fillStyle = 'rgba(232,180,90,0.14)'; c.fill();
      c.strokeStyle = 'rgba(232,180,90,0.55)'; c.lineWidth = 3; c.stroke();
      c.fillStyle = '#f0c85a'; c.textAlign = 'left'; c.textBaseline = 'middle';
      c.font = '800 32px system-ui, sans-serif';
      c.fillText('⌂ ' + t('a_pala'), X0 + 26, yPal + 34);
      c.fillStyle = 'rgba(255,255,255,0.75)'; c.font = '600 19px system-ui, sans-serif';
      c.fillText(t('a_pala_s'), X0 + 26, yPal + 66);
      c.restore();
      // ayudas técnicas
      const yFb = yPal + 112;
      label(t('fb_t'), yFb, 22, '#7d8ea6');
      const toggles = [['marks', t('fb_marks')], ['line', t('fb_line')], ['spin', t('fb_spin')]];
      let tx = X0;
      for (const [k, lbl] of toggles) {
        const w = 290;
        btn('trv3:fb:' + k, tx, yFb + 18, w, 64, lbl, !!S.fb[k], undefined, !!S.fb[k], 22);
        tx += w + 24;
      }
      // skins
      const ySk = yFb + 108;
      label(t('skins_t'), ySk, 22, '#7d8ea6');
      let sx = X0;
      for (const sk of SKINS) {
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
      drawHeader(game, c, rects, btn, label, t(a.ik) + ' · ' + t(a.sk));
      let y = 196;
      for (const id of Object.keys(MODES)) {
        const M = MODES[id];
        if (M.area !== a.id) continue;
        const isOn = active === id;
        // tarjeta del modo
        const idx = rects.length;
        btn('trv3:start:' + id, 40, y, 944, 172, '', false);
        c.save();
        c.beginPath();
        if (c.roundRect) c.roundRect(40, y, 944, 172, 22); else c.rect(40, y, 944, 172);
        const gr = c.createLinearGradient(40, y, 984, y + 172);
        gr.addColorStop(0, a.g0); gr.addColorStop(1, a.g1);
        c.fillStyle = gr; c.globalAlpha = isOn ? 0.95 : 0.8; c.fill(); c.globalAlpha = 1;
        c.strokeStyle = isOn ? '#f0c85a' : 'rgba(255,255,255,0.28)'; c.lineWidth = isOn ? 5 : 3;
        c.stroke();
        c.textAlign = 'left'; c.textBaseline = 'middle';
        c.fillStyle = '#ffffff'; c.font = '800 34px system-ui, sans-serif';
        c.fillText(t(M.nk), 68, y + 42);
        c.fillStyle = 'rgba(255,255,255,0.85)'; c.font = '600 20px system-ui, sans-serif';
        const desc = t(M.dk, { n: M.n });
        // cuerpo envuelto a 2 líneas
        let l1 = desc, l2 = '';
        if (c.measureText(desc).width > 700) {
          const words = desc.split(' ');
          l1 = ''; l2 = '';
          for (const w of words) {
            if (c.measureText(l1 + ' ' + w).width <= 700 && !l2) l1 = l1 ? l1 + ' ' + w : w;
            else l2 = l2 ? l2 + ' ' + w : w;
          }
        }
        c.fillText(l1, 68, y + 82);
        if (l2) c.fillText(l2, 68, y + 110);
        c.fillStyle = '#f0c85a'; c.font = '700 20px system-ui, sans-serif';
        c.fillText((S.best[id] ? t('mejor') + ': ' + S.best[id] + '  ·  ' : '') + t('obj') + ': ' + M.n, 68, y + 142);
        // v3.0.7-PLAY1 · estrellas logradas + mejor precisión de la prueba
        if (GAMF()) {
          const stN = S.stars[id] || 0;
          c.textAlign = 'right';
          let meta = '\u2605'.repeat(stN) + '\u2606'.repeat(3 - stN);
          if (S.acc[id]) meta += '  ' + S.acc[id] + '%';
          c.fillStyle = stN ? '#f0c85a' : 'rgba(255,255,255,0.35)';
          c.font = '800 22px system-ui, sans-serif';
          c.fillText(meta, 950, y + 142);
        }
        c.textAlign = 'right';
        c.fillStyle = isOn ? '#f0c85a' : '#ffffff';
        c.font = '900 26px system-ui, sans-serif';
        c.fillText(isOn ? t('activo') : t('iniciar'), 950, y + 86);
        c.restore();
        y += 190;
      }
      btn('trv3:back', 40, 1380, 944, 76, t('volver'), false, undefined, undefined, 28);
    }
  
    /* ---------------- acciones del menú (case 'trv3') ---------------- */
    function menuAction(game, arg) {
      const p = arg.split(':');
      const cmd = p[0];
      if (cmd === 'area') { uiArea = p[1] || 'dir'; uiPage = 'area'; game.menuPage = 'trainarea'; game.drawMenu(); }
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
      else if (cmd === 'fb') { S.fb[p[1]] = S.fb[p[1]] ? 0 : 1; save(); game.drawMenu(); }
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
        // detección de efecto del jugador en CUALQUIER modo (iconos en caras)
        if (faceIcons.length && G.events && G.events.length) {
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
      serveTrigger: () => { try { serveTossFromTee(true); } catch (e) { /* nunca rompe */ } },
      serveRelease: (i) => { try { if (G && i === G.ballHand) serveTossFromTee(false); } catch (e) { /* nunca rompe */ } },
      drawHub, drawArea,
      get state() { return { active, pts: S.pts, best: S.best, skin: S.skin, unlocked: S.unlocked.slice(),
        stars: Object.assign({}, S.stars), acc: Object.assign({}, S.acc),
        ach: Object.assign({}, S.ach), comboBest: S.comboBest || 0,
        round: { hits: st.roundHits, faults: st.roundFaults } }; },
      __debug: { S, st, MODES },
    __test: { okHit, failHit, judgeAiBounce, modeFeed, pickTarget, serveTee, drawQuad, drawPanel, serveAssist },
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
    game.enterVR()
      .catch((err) => {
        statusEl.textContent = '⚠️ ' + (err?.message || T('status_vr_fail'));
      });
  });

  // PASSTHROUGH: juega en TU habitación real (enlace discreto del pie)
  if (arBtn) {
    arBtn.addEventListener('click', () => {
      if (arBtn.disabled) return;
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

