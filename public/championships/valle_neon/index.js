
/* ============================================================================
 *  MÓDULO PLANTILLA UNIVERSAL — campeonatos creados con EL TALLER (Crazy Ping Pong)
 *  ----------------------------------------------------------------------------
 *  Data-driven: TODO el comportamiento sale del manifest.json del campeonato
 *  (contrato 1). El Taller lo genera tal cual como index.js.
 *  Contrato ChampLoader: init/start/leave/resetRecords/update/onPoint/
 *  onMatchOver/aiMul/serveTrigger/reenter/replayMap/replayHover/replayLaunch/
 *  musicOff/testActive/testStep/champIntroPause/isChampion + decor/room.
 *  Superficie del núcleo usada (scripts/plataforma/AUDITORIA.md):
 *  __PP_CORE (DIMS, stepPhysics, lang, showChampConseguido), rules.state
 *  ('champtest' duerme al árbitro), audio (playOsc/playNoise/announce/
 *  fanfare), champRoom/champDecor por export, __PP_WORLD.submit, haptic,
 *  ignoreNet (documentado), showInstrucciones (cartel de normas).
 *  ============================================================================ */
import * as THREE from 'three';
// v3.6.2-SDK2 · FASE 4 de la modularización P0: el puente al núcleo vive en
// el SDK de campeonatos (championships/sdk/champ_sdk.js) — una sola fuente
// para los 5 módulos. Este módulo (data-driven del Taller) no tiene SFX mp3
// ni congelados propios: su música WAV en bucle conserva el motor propio
// (createMusic del SDK la unificará en una fase posterior).
import { getCore } from '../sdk/champ_sdk.js';

const CORE = getCore();
const GAME = { g: null };
let CTRL = null;
let TL = 'es';
const tx = (es, en) => (TL === 'en' ? (en || es) : es);

/* roundRect con reserva (navegadores antiguos) */
if (typeof document !== 'undefined' && !CanvasRenderingContext2D.prototype.roundRect) {
  CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    this.moveTo(x + r, y);
    this.arcTo(x + w, y, x + w, y + h, r);
    this.arcTo(x + w, y + h, x, y + h, r);
    this.arcTo(x, y + h, x, y, r);
    this.arcTo(x, y, x + w, y, r);
    this.closePath();
    return this;
  };
}

/* ------------------------------ constantes ------------------------------- */
const D = () => (CORE && CORE.DIMS) || { tableTopY: 0.76, tableCenterZ: -1.6, netTopY: 0.9125, ballRadius: 0.02 };
const HOLD = { x: 0, z: -0.5, T: 1.5, H: 0.42 };   // bote-en-espera del jugador (convención magia v2.61)
const KINDS_OK = ['confeti', 'mareo', 'globos', 'orbe', 'arena'];
const DUEL_X = 1.15, STAND_Z = -3.05;

/* ------------------------- fábricas de texturas -------------------------- */
function texDeCanvas(cv) {
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function cvMedallon(emojiForma, color1, color2) {
  const cv = document.createElement('canvas'); cv.width = 256; cv.height = 256;
  const c = cv.getContext('2d');
  const g = c.createRadialGradient(128, 118, 18, 128, 128, 124);
  g.addColorStop(0, color1); g.addColorStop(1, color2);
  c.beginPath(); c.arc(128, 128, 118, 0, Math.PI * 2); c.fillStyle = g; c.fill();
  c.lineWidth = 10; c.strokeStyle = 'rgba(255,255,255,.85)'; c.stroke();
  c.fillStyle = '#fff'; c.strokeStyle = 'rgba(0,0,0,.35)'; c.lineWidth = 6;
  const f = (fn) => { c.beginPath(); fn(); c.fill(); c.stroke(); };
  if (emojiForma === 'confeti') f(() => { for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; c.rect(128 + Math.cos(a) * 46 - 9, 128 + Math.sin(a) * 46 - 9, 18, 18); c.rotate(0); } });
  else if (emojiForma === 'mareo') f(() => { for (let r = 12; r <= 66; r += 13) c.arc(128, 128, r, 0, Math.PI * 1.35); });
  else if (emojiForma === 'globos') f(() => { c.ellipse(128, 108, 44, 54, 0, 0, Math.PI * 2); c.moveTo(128, 162); c.quadraticCurveTo(112, 196, 132, 218); });
  else if (emojiForma === 'orbe') f(() => { c.arc(128, 128, 62, 0, Math.PI * 2); c.moveTo(128, 84); c.arc(128, 128, 44, 0, Math.PI * 2); });
  else f(() => { for (let i = 0; i < 3; i++) { c.moveTo(52, 96 + i * 40); c.bezierCurveTo(86, 76 + i * 40, 118, 116 + i * 40, 152, 96 + i * 40); c.bezierCurveTo(186, 76 + i * 40, 210, 116 + i * 40, 236, 96 + i * 40); } });
  return cv;
}

/* ============================================================================
 *  DianasDelTaller — LA PRUEBA DE HABILIDAD (motor de dianas)
 *  Patrón Estación Orbital v3: física del núcleo (stepPhysics) + colisionador
 *  extra por SUBPASO (segmento prev→actual, anti-túnel), árbitro dormido en
 *  'champtest', bola en bote-en-espera hasta el primer golpe, ignoreNet.
 *  ============================================================================ */
class DianasDelTaller {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.built = false;
    this.running = false;
    this.result = false;
    this.cfg = null;                 // {modo, objetivo, premio, tiempo}
    this.targets = [];
    this.nacidas = 0; this.golpes = 0;
    this.tiempo = 0; this.t = 0;
    this.hold = true; this.holdT = 0; this.flight = 0; this.deadT = 0;
    this.bannerT = 0; this._endDone = false;
    this._extra = (ball, events) => this._collide(ball, events);
  }

  build() {
    if (this.built) return;
    this.built = true;
    const g = this.game;
    this.ownTex = new Set();
    this.grp = new THREE.Group();
    this.grp.visible = false;
    g.scene.add(this.grp);

    // textura de diana (vector: dibujada, sin arte externo)
    const cv = document.createElement('canvas'); cv.width = 256; cv.height = 256;
    const c = cv.getContext('2d');
    const anillos = [['#7f1d1d', 122], ['#f8fafc', 96], ['#dc2626', 70], ['#f8fafc', 44], ['#b91c1c', 20]];
    anillos.forEach(([col, r]) => { c.beginPath(); c.arc(128, 128, r, 0, Math.PI * 2); c.fillStyle = col; c.fill(); });
    c.beginPath(); c.arc(128, 128, 122, 0, Math.PI * 2); c.lineWidth = 8; c.strokeStyle = '#fbbf24'; c.stroke();
    this.texDiana = texDeCanvas(cv); this.ownTex.add(this.texDiana);

    // destello + fragmentos (pool, regla Quest: una vez)
    const cvF = document.createElement('canvas'); cvF.width = 64; cvF.height = 64;
    { const c2 = cvF.getContext('2d'); const gr = c2.createRadialGradient(32, 32, 2, 32, 32, 30);
      gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.4, 'rgba(255,230,120,.9)'); gr.addColorStop(1, 'rgba(255,140,40,0)');
      c2.fillStyle = gr; c2.fillRect(0, 0, 64, 64); }
    this.texFlash = texDeCanvas(cvF); this.ownTex.add(this.texFlash);
    const cvP = document.createElement('canvas'); cvP.width = 32; cvP.height = 32;
    { const c3 = cvP.getContext('2d'); c3.fillStyle = '#fecaca'; c3.beginPath(); c3.moveTo(16, 2); c3.lineTo(30, 22); c3.lineTo(16, 30); c3.lineTo(2, 22); c3.closePath(); c3.fill(); }
    this.texFrag = texDeCanvas(cvP); this.ownTex.add(this.texFrag);
    this.fx = [];
    for (let i = 0; i < 20; i++) this.fx.push(this._mkSprite(this.texFlash, 0.5, false));
    for (let i = 0; i < 22; i++) this.fx.push(this._mkSprite(this.texFrag, 0.28, true));

    // HUD + banner
    this.hudCv = document.createElement('canvas'); this.hudCv.width = 640; this.hudCv.height = 150;
    this.hudTex = texDeCanvas(this.hudCv); this.ownTex.add(this.hudTex);
    this.hud = new THREE.Mesh(new THREE.PlaneGeometry(1.55, 0.36),
      new THREE.MeshBasicMaterial({ map: this.hudTex, transparent: true, depthWrite: false }));
    this.hud.position.set(0, D().tableTopY + 1.18, D().tableCenterZ - 1.55);
    this.hud.rotation.x = -0.10;
    this.grp.add(this.hud);
    this.bnCv = document.createElement('canvas'); this.bnCv.width = 640; this.bnCv.height = 300;
    this.bnTex = texDeCanvas(this.bnCv); this.ownTex.add(this.bnTex);
    this.banner = new THREE.Mesh(new THREE.PlaneGeometry(1.9, 0.9),
      new THREE.MeshBasicMaterial({ map: this.bnTex, transparent: true, depthWrite: false }));
    this.banner.position.set(0, D().tableTopY + 1.28, D().tableCenterZ - 1.2);
    this.banner.visible = false;
    this.grp.add(this.banner);
  }
  _mkSprite(tex, tam, frag) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, opacity: 0 }));
    s.scale.setScalar(tam); s.renderOrder = 30;
    this.grp.add(s);
    return { s, t: 9, life: frag ? 0.9 : 0.5, vx: 0, vy: 0, vz: 0, frag: !!frag };
  }

  _A(p) { return this.ctrl._A(p); }

  start(cfg) {
    const g = this.game;
    this.build();
    this.cfg = cfg || { modo: 'objetivos', objetivo: 5, premio: '', tiempo: 75 };
    if (!this.cfg.tiempo) this.cfg.tiempo = Math.min(90, 20 + this.cfg.objetivo * 10);
    this.running = true; this.result = false;
    this.golpes = 0; this.nacidas = 0; this.t = 0;
    this.tiempo = this.cfg.tiempo;
    this.banner.visible = false;
    this.grp.visible = true;
    for (const f of this.fx) { f.t = 9; f.s.material.opacity = 0; }
    // nº de dianas vivas simultáneas
    this.nVivas = Math.max(2, Math.min(4, this.cfg.objetivo));
    this.targets.length = 0;
    for (let i = 0; i < this.nVivas; i++) this._naceDiana(true);
    this._spawnHeld();
    try { g.ball.ignoreNet = true; } catch (e) { /* */ }
    this._pintaHud();
  }
  stop() {
    const g = this.game;
    this.running = false; this.result = false;
    if (this.grp) this.grp.visible = false;
    try { g.ball.ignoreNet = false; } catch (e) { /* */ }
  }
  stepActive() { return this.running || this.result; }

  _naceDiana(primera) {
    const g = this.game;
    const movil = this.cfg.modo !== 'objetivos';
    const fijo = (this.cfg.modo === 'contrarreloj');
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.texDiana, transparent: true, depthWrite: false }));
    const r = fijo ? 0.13 : 0.155;
    sp.scale.setScalar(r * 2.6);
    sp.renderOrder = 25;
    this.grp.add(sp);
    const bx = (Math.random() * 1.7 - 0.85);
    const by = D().tableTopY + 0.45 + Math.random() * 0.85;
    const bz = D().tableCenterZ - (0.55 + Math.random() * 1.15);
    sp.position.set(bx, by, bz);
    this.targets.push({
      sp, r, alive: true, bx, by, bz,
      orbitA: movil ? (fijo ? 0.34 : 0.22) : 0.02,
      orbitW: movil ? (fijo ? 1.5 : 0.85) : 0.25,
      fase: Math.random() * Math.PI * 2,
    });
    this.nacidas++;
    if (!primera) {
      try { g.audio.playOsc(520, 880, 0.12, 'sine', 0.1, 0); } catch (e) { /* */ }
    }
  }

  _collide(ball, events) {
    const g = this.game;
    if (!this.running) { if (ball.__exPrev) ball.__exPrev.copy(ball.pos); return; }
    let prev = ball.__exPrev;
    if (!prev) prev = ball.__exPrev = new THREE.Vector3().copy(ball.pos);
    const p = ball.pos;
    const seg = new THREE.Vector3().subVectors(p, prev);
    const len = seg.length();
    if (len > 1e-6) {
      const dir = seg.clone().divideScalar(len);
      for (const it of this.targets) {
        if (!it.alive) continue;
        const w = new THREE.Vector3().subVectors(it.sp.position, prev);
        const proj = w.dot(dir);
        let hit = false;
        if (proj <= 0) hit = w.length() <= it.r;
        else if (proj >= len) hit = w.sub(dir.clone().multiplyScalar(len)).length() <= it.r;
        else hit = (w.sub(dir.clone().multiplyScalar(proj))).length() <= it.r;
        if (hit) {
          it.alive = false; it.sp.visible = false;
          this.golpes++;
          this._estalla(it.sp.position);
          try {
            g.audio.playNoise(0.16, 900, 1.1, 0.4, 0);
            g.audio.playOsc(880, 1320, 0.12, 'square', 0.2, 0);
            if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.42, 70);
          } catch (e) { /* */ }
          // recambio hasta el objetivo
          if (this.golpes + this._vivas() < this.cfg.objetivo + this.nVivas) { /* programado abajo */ }
          setTimeout(() => {
            try {
              if (this.running && this.golpes < this.cfg.objetivo) this._naceDiana(false);
            } catch (e) { /* */ }
          }, 900);
          this._pintaHud();
          if (this.golpes >= this.cfg.objetivo) { this._fin(true); return; }
        }
      }
    }
    ball.__exPrev.copy(p);
  }
  _vivas() { let n = 0; for (const it of this.targets) if (it.alive) n++; return n; }

  _estalla(pos) {
    let usados = 0;
    for (const f of this.fx) {
      if (f.t < f.life) continue;                  // ocupado
      f.t = 0;
      f.s.position.copy(pos);
      f.s.material.opacity = 1;
      f.s.scale.setScalar(f.frag ? 0.24 : 0.55);
      const ang = Math.random() * Math.PI * 2;
      const vel = f.frag ? 1.4 : 0.9;
      f.vx = Math.cos(ang) * vel; f.vz = Math.sin(ang) * vel;
      f.vy = f.frag ? 1.6 + Math.random() * 1.2 : 0.8;
      if (++usados >= 14) break;
    }
  }
  _fxStep(dt) {
    for (const f of this.fx) {
      if (f.t >= f.life) continue;
      f.t += dt;
      f.s.position.x += f.vx * dt; f.s.position.y += f.vy * dt; f.s.position.z += f.vz * dt;
      if (f.frag) f.vy -= 4.5 * dt;
      f.s.material.opacity = Math.max(0, 1 - f.t / f.life);
    }
  }

  _pintaHud() {
    const c = this.hudCv.getContext('2d');
    c.clearRect(0, 0, 640, 150);
    c.fillStyle = 'rgba(10,16,32,.78)';
    c.beginPath(); c.roundRect(6, 6, 628, 138, 26); c.fill();
    c.lineWidth = 4; c.strokeStyle = '#38bdf8'; c.stroke();
    c.fillStyle = '#e0f2fe'; c.textAlign = 'center';
    c.font = '700 44px "Baloo 2", sans-serif';
    c.fillText(this.ctrl.nombre.toUpperCase(), 320, 58);
    c.font = '700 52px "Baloo 2", sans-serif';
    c.fillStyle = '#fde047';
    c.fillText(this.golpes + ' / ' + this.cfg.objetivo, 320, 118);
    c.textAlign = 'right'; c.fillStyle = '#bae6fd'; c.font = '700 46px "Baloo 2", sans-serif';
    c.fillText(Math.ceil(this.tiempo) + ' s', 600, 118);
    this.hudTex.needsUpdate = true;
  }
  _pintaBanner(win) {
    const c = this.bnCv.getContext('2d');
    c.clearRect(0, 0, 640, 300);
    c.fillStyle = win ? 'rgba(22,101,52,.92)' : 'rgba(120,53,15,.92)';
    c.beginPath(); c.roundRect(8, 8, 624, 284, 30); c.fill();
    c.lineWidth = 6; c.strokeStyle = win ? '#86efac' : '#fcd34d'; c.stroke();
    c.textAlign = 'center'; c.fillStyle = '#fff';
    c.font = '800 64px "Baloo 2", sans-serif';
    c.fillText(win ? tx('¡PRUEBA SUPERADA!', 'TEST CLEARED!') : tx('TIEMPO AGOTADO', "TIME'S UP"), 320, 96);
    c.font = '600 38px "Nunito Sans", sans-serif';
    c.fillText(tx('Dianas: ' + this.golpes + ' / ' + this.cfg.objetivo, 'Targets: ' + this.golpes + ' / ' + this.cfg.objetivo), 320, 158);
    if (win && this.cfg.premio) {
      c.fillStyle = '#fde047'; c.font = '700 44px "Baloo 2", sans-serif';
      c.fillText('🏅 ' + this.cfg.premio, 320, 232);
    }
    this.bnTex.needsUpdate = true;
  }

  _spawnHeld() {
    const g = this.game;
    this.hold = true; this.holdT = 0; this.flight = 0;
    g.ball.pos.set(HOLD.x, D().tableTopY + 0.12, HOLD.z);
    g.ball.vel.set(0, 0, 0); g.ball.spin.set(0, 0, 0);
    if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
    g.ballMesh.visible = true;
    try { g.audio.playOsc(220, 880, 0.16, 'sine', 0.08, 0); } catch (e) { /* */ }
  }
  _bolaPerdida() {
    const g = this.game;
    this.hold = false;
    g.ball.vel.set(0, 0, 0); g.ball.spin.set(0, 0, 0);
    g.ballMesh.visible = false;
    this.deadT = 0.7;
    try { g.audio.playNoise(0.18, 300, 0.25, 0.12, 0); } catch (e) { /* */ }
  }

  step(dt) {
    const g = this.game;
    this.t += dt;
    if (this.result) {
      this.bannerT -= dt;
      this.banner.position.y += Math.sin(this.t * 2.1) * 0.0006;
      if (this.bannerT <= 0 && !this._endDone) { this._endDone = true; this._cleanup(); }
      return;
    }
    if (!this.running) return;
    this.tiempo -= dt;
    if (this.tiempo <= 0) { this.tiempo = 0; this._pintaHud(); this._fin(false); return; }
    this._pintaHud();
    for (const it of this.targets) {
      if (!it.alive) continue;
      const ph = this.t * it.orbitW + it.fase;
      it.sp.position.x = it.bx + Math.sin(ph) * it.orbitA;
      it.sp.position.y = it.by + Math.sin(this.t * 1.7 + it.fase) * 0.035;
    }
    this._fxStep(dt);
    if (this.deadT > 0) { this.deadT -= dt; if (this.deadT <= 0) this._spawnHeld(); }

    const pads = [];
    try {
      const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
      if (g.renderer.xr.isPresenting && ps && ps.active) pads.push(ps);
    } catch (e) { /* */ }
    g.events.length = 0;
    try { (CORE.stepPhysics || this._fallbackStep)(dt, g.ball, pads, g.events, this._extra); }
    catch (e) { console.warn('[taller.stepPhysics]', e); }

    if (this.hold) {
      let hit = false;
      for (const e of g.events) { if (e.type === 'paddle') { hit = true; break; } }
      if (hit) { this.hold = false; this.flight = 0; }
      else {
        this.holdT += dt;
        const T = HOLD.T, H = HOLD.H, pp = (this.holdT % T) / T;
        g.ball.pos.set(HOLD.x, D().tableTopY + 0.12 + 4 * H * pp * (1 - pp), HOLD.z);
        g.ball.vel.set(0, (4 * H * (1 - 2 * pp)) / T, 0);
        g.ball.spin.multiplyScalar(Math.max(0, 1 - dt * 2));
        if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
      }
    } else {
      this.flight += dt;
      const p = g.ball.pos;
      if (p.y < 0.05 || p.z > 1.2 || p.z < D().tableCenterZ - 2.6 || this.flight > 9) this._bolaPerdida();
    }
  }
  _fallbackStep(dt, ball, pads, evs, extra) {
    // sin física del núcleo la prueba no puede correr: bola quieta
    if (ball.__exPrev) ball.__exPrev.copy(ball.pos);
  }

  _fin(win) {
    const g = this.game;
    this.running = false; this.result = true;
    this.bannerT = 4.4; this._endDone = false;
    this._pintaBanner(win);
    this.banner.visible = true;
    if (win) {
      try { g.confettiBurst = Math.max(g.confettiBurst || 0, 3); } catch (e) { /* */ }
      try { g.audio.fanfare(true); } catch (e) { /* */ }
      try { g.audio.announce(tx('¡Prueba superada!', 'Test cleared!'), true); } catch (e) { /* */ }
      try { if (g.renderer.xr.isPresenting) { g.haptic(g.paddleHand, 0.7, 130); window.setTimeout(() => g.haptic(g.paddleHand, 0.5, 120), 220); } } catch (e) { /* */ }
    } else {
      try { g.audio.fanfare(false); } catch (e) { /* */ }
      try { g.audio.announce(tx('Tiempo agotado', 'Time is up'), true); } catch (e) { /* */ }
    }
    this.ctrl._pruebaFin(win);
  }
  _cleanup() {
    const g = this.game;
    this.result = false;
    this.banner.visible = false;
    try { g.ball.ignoreNet = false; } catch (e) { /* */ }
    this.grp.visible = false;
    try { g.rules.startMatch('match'); } catch (e) { /* */ }
    this.ctrl._despuesDePrueba();
  }
}

/* ============================================================================
 *  PlantillaCtrl — el controlador del camino (sala → duelo/prueba → … → final)
 *  ============================================================================ */
class PlantillaCtrl {
  constructor(g, manifest) {
    this.game = g;
    this.man = manifest || {};
    this.id = this.man.id || 'campeonato';
    this.base = String(this.man.storage || ('pp_champ_' + this.id + '_*')).replace(/\*$/, '');
    this.nombre = (this.man.title && (this.man.title.es || this.man.title.en)) || this.id;
    this.rivalNombre = (this.man.rival && this.man.rival.name) || 'RIVAL';
    this.puntosObjetivo = 11;

    /* camino: duelo → prueba → duelo → … → DUELO FINAL (patrón EO/Magia) */
    const difMul = { facil: 0.85, media: 1.0, dificil: 1.18 }[this._dificultad()] || 1.0;
    const personalidad = ((((this.man.rival || {}).personalidad || {}).agresividad || 3) - 3) * 0.03 +
      ((((this.man.rival || {}).personalidad || {}).precision || 3) - 3) * 0.03;
    const retos = (this.man.taller && Array.isArray(this.man.taller.retos)) ? this.man.taller.retos : [];
    this.etapas = [];
    retos.forEach((r, i) => {
      this.etapas.push({
        id: 'duelo' + (i + 1), name: tx('Duelo ' + (i + 1), 'Duel ' + (i + 1)),
        kind: 'duelo', aiMul: difMul * (1 + 0.15 * i + personalidad),
      });
      this.etapas.push({
        id: 'prueba' + (i + 1), name: r.nombre || ('Prueba ' + (i + 1)), kind: 'prueba',
        modo: r.tipo || 'objetivos', objetivo: Math.max(1, r.objetivo | 0),
        premio: r.premio || '', puntos: Math.max(1, r.puntos | 0),
      });
    });
    this.etapas.push({
      id: 'final', name: tx('DUELO FINAL', 'FINAL DUEL'), kind: 'duelo',
      aiMul: difMul * 1.35 + personalidad,
    });

    /* poderes del manifest, sólo kinds que este motor conoce */
    this.poderes = (this.man.powers || []).filter((p) => KINDS_OK.indexOf(p.kind) >= 0).slice(0, 4);

    /* progreso persistente */
    try { this.stage = Math.min(this.etapas.length - 1, parseInt(localStorage.getItem(this.base + 'stage') || '0', 10) || 0); } catch (e) { this.stage = 0; }
    try { this.victorias = parseInt(localStorage.getItem(this.base + 'wins') || '0', 10) || 0; } catch (e) { this.victorias = 0; }
    try { this._champion = localStorage.getItem(this.base + 'champ') === '1'; } catch (e) { this._champion = false; }

    this.state = 'sala';
    this._replay = null;
    this._ownTex = new Set();
    this._t = 0;
    this._bolsa = []; this._powerCd = 6; this._act = null; this._aviso = null; this._dueloT = 0; this._toward = false;
    this._marT = 0; this._marOn = false;
  }

  _dificultad() {
    return (this.man.taller && this.man.taller.dificultad) || 'media';
  }
  txMapa() {
    return tx('Camino: apunta a una etapa superada para revivirla · gatillo para jugar',
      'Path: aim at a cleared stage to replay it · trigger to play');
  }
  _A(p) { return new URL(p, new URL('.', import.meta.url)).href; }
  _etapa() { return this.etapas[Math.min(this.stage | 0, this.etapas.length - 1)]; }

  /* ------------------------------ escena ------------------------------- */
  build() {
    if (this.group) return;
    const g = this.game;
    this.group = new THREE.Group();
    g.scene.add(this.group);

    /* standee del rival (arte del campeonato o silueta de reserva) */
    this.standee = new THREE.Group();
    this.stTex = { base: null, idle: null, duelo: null, derrotado: null, triunfante: null };
    const cargaTex = (file, key) => {
      const t = new THREE.TextureLoader().load(this._A('assets/' + file), (tex) => {
        tex.colorSpace = THREE.SRGBColorSpace; this._ownTex.add(tex);
        if (this.standeeMat) {
          this.standeeMat.map = tex; this.standeeMat.needsUpdate = true;
          const asp = (tex.image && tex.image.width) ? tex.image.width / tex.image.height : 0.5;
          this.standeeMesh.scale.set(asp / 0.5, 1, 1);
        }
        if (key) this.stTex[key] = tex;
      }, undefined, () => { /* sin arte: silueta */ });
    };
    this.standeeMat = new THREE.MeshStandardMaterial({ color: 0xbfc9d6, transparent: true, alphaTest: 0.05, roughness: 0.9 });
    this.standeeMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.85), this.standeeMat);
    this.standeeMesh.position.y = 0.925;
    this.standeeMesh.castShadow = true;
    this.standee.add(this.standeeMesh);
    this.standee.position.set(DUEL_X, 0, STAND_Z);
    this.standee.rotation.y = Math.atan2(-DUEL_X, 0.55 - STAND_Z);
    this.group.add(this.standee);
    const rival = this.man.rival || {};
    cargaTex('rival.webp', null);
    (rival.states || []).forEach((st) => { if (this.stTex.hasOwnProperty(st)) cargaTex(st + '.webp', st); });

    /* cartel de sala (canvas) */
    this.cartelCv = document.createElement('canvas'); this.cartelCv.width = 1024; this.cartelCv.height = 512;
    this.cartelTex = texDeCanvas(this.cartelCv); this._ownTex.add(this.cartelTex);
    this.cartel = new THREE.Mesh(new THREE.PlaneGeometry(2.3, 1.15),
      new THREE.MeshBasicMaterial({ map: this.cartelTex, transparent: true, depthWrite: false }));
    this.cartel.position.set(-1.05, 1.62, -3.6);
    this.cartel.rotation.y = 0.42;
    this.group.add(this.cartel);

    /* mapa del camino (canvas — sin arte externo) */
    this.mapa = new MapaTaller(this);
    this.group.add(this.mapa.group);

    /* cartel del superpoder (dos fases) */
    this.powCv = document.createElement('canvas'); this.powCv.width = 512; this.powCv.height = 128;
    this.powTex = texDeCanvas(this.powCv); this._ownTex.add(this.powTex);
    this.powerSign = new THREE.Mesh(new THREE.PlaneGeometry(1.15, 0.29),
      new THREE.MeshBasicMaterial({ map: this.powTex, transparent: true, depthWrite: false }));
    this.powerSign.position.set(DUEL_X - 0.1, 2.05, STAND_Z + 0.55);
    this.powerSign.visible = false;
    this.group.add(this.powerSign);

    /* pools de efectos de poderes (una vez por sesión) */
    this._montaPoderes();

    /* motor de pruebas */
    this.prueba = new DianasDelTaller(this);
    this.prueba.build();
  }

  _montaPoderes() {
    const g = this.game;
    const med = (kind) => {
      const map = { confeti: ['#fde68a', '#f59e0b'], mareo: ['#c7d2fe', '#4f46e5'], globos: ['#fecdd3', '#e11d48'], orbe: ['#a5f3fc', '#0891b2'], arena: ['#fde68a', '#b45309'] };
      const m = map[kind] || ['#e2e8f0', '#475569'];
      const cv = cvMedallon(kind, m[0], m[1]);
      const t = texDeCanvas(cv);
      this._ownTex.add(t);
      return { cv, tex: t };
    };
    this.medCv = {};
    this.medTex = {};
    KINDS_OK.forEach((k) => { const r = med(k); this.medCv[k] = r.cv; this.medTex[k] = r.tex; });

    /* confeti */
    this.confeti = [];
    const cvC = document.createElement('canvas'); cvC.width = 24; cvC.height = 24;
    { const c = cvC.getContext('2d'); c.fillStyle = '#f472b6'; c.fillRect(2, 2, 20, 20); c.fillStyle = '#facc15'; c.fillRect(4, 8, 12, 8); }
    this.texConfeti = texDeCanvas(cvC); this._ownTex.add(this.texConfeti);
    for (let i = 0; i < 36; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.texConfeti, transparent: true, depthWrite: false, opacity: 0 }));
      s.scale.setScalar(0.05); s.renderOrder = 40; this.group.add(s);
      this.confeti.push({ s, t: 9, life: 3.2, x: 0, y: 0, z: 0, vy: 0, ph: Math.random() * 6 });
    }
    /* arena */
    this.arena = [];
    const cvA = document.createElement('canvas'); cvA.width = 48; cvA.height = 24;
    { const c = cvA.getContext('2d'); const gr = c.createLinearGradient(0, 0, 48, 0); gr.addColorStop(0, 'rgba(217,119,6,0)'); gr.addColorStop(.5, 'rgba(234,179,8,.9)'); gr.addColorStop(1, 'rgba(217,119,6,0)'); c.fillStyle = gr; c.fillRect(0, 6, 48, 12); }
    this.texArena = texDeCanvas(cvA); this._ownTex.add(this.texArena);
    for (let i = 0; i < 22; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.texArena, transparent: true, depthWrite: false, opacity: 0 }));
      s.scale.set(0.6, 0.3, 1); s.renderOrder = 40; this.group.add(s);
      this.arena.push({ s, t: 9, life: 2.4, x: 0, y: 0, z: 0, vx: 0 });
    }
    /* globos */
    this.globos = [];
    const cvG = document.createElement('canvas'); cvG.width = 128; cvG.height = 160;
    { const c = cvG.getContext('2d'); c.fillStyle = '#ef4444'; c.beginPath(); c.ellipse(64, 54, 40, 50, 0, 0, Math.PI * 2); c.fill(); c.strokeStyle = '#991b1b'; c.lineWidth = 4; c.beginPath(); c.moveTo(64, 104); c.quadraticCurveTo(52, 132, 68, 156); c.stroke(); }
    this.texGlobo = texDeCanvas(cvG); this._ownTex.add(this.texGlobo);
    for (let i = 0; i < 3; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.texGlobo, transparent: true, depthWrite: false, opacity: 0 }));
      s.scale.set(0.3, 0.375, 1); s.renderOrder = 40; this.group.add(s);
      this.globos.push({ s, activo: false, x: 0, y: 0, z: 0, v: 0 });
    }
    /* orbe */
    const cvO = document.createElement('canvas'); cvO.width = 128; cvO.height = 128;
    { const c = cvO.getContext('2d'); const gr = c.createRadialGradient(64, 64, 6, 64, 64, 60); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.35, 'rgba(103,232,249,.95)'); gr.addColorStop(.75, 'rgba(14,116,144,.55)'); gr.addColorStop(1, 'rgba(14,116,144,0)'); c.fillStyle = gr; c.fillRect(0, 0, 128, 128); }
    this.texOrbe = texDeCanvas(cvO); this._ownTex.add(this.texOrbe);
    this.orbe = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.texOrbe, transparent: true, depthWrite: false, opacity: 0 }));
    this.orbe.scale.setScalar(0.42); this.orbe.renderOrder = 40;
    this.group.add(this.orbe);

    /* mareo */
    this._mareoBase = null; this._mareoDelta = 0;
  }

  /* ---------------------------- cartel de sala -------------------------- */
  _pintaCartel() {
    const c = this.cartelCv.getContext('2d');
    const W = 1024, H = 512;
    c.clearRect(0, 0, W, H);
    c.fillStyle = 'rgba(8,13,28,.88)';
    c.beginPath(); c.roundRect(10, 10, W - 20, H - 20, 34); c.fill();
    c.lineWidth = 6; c.strokeStyle = '#f59e0b'; c.stroke();
    c.textAlign = 'center';
    c.fillStyle = '#fbbf24'; c.font = '800 74px "Baloo 2", sans-serif';
    c.fillText(this.nombre.toUpperCase().slice(0, 22), W / 2, 104);
    c.fillStyle = '#e2e8f0'; c.font = '600 40px "Nunito Sans", sans-serif';
    const et = this._etapa();
    const lbl = et.kind === 'duelo' ? tx('Etapa', 'Stage') : tx('Prueba', 'Test');
    c.fillText(lbl + ' ' + (this.stage + 1) + '/' + this.etapas.length + ' · ' + et.name, W / 2, 176);
    c.fillStyle = '#94a3b8'; c.font = '600 34px "Nunito Sans", sans-serif';
    c.fillText(tx('Rival: ' + this.rivalNombre, 'Rival: ' + this.rivalNombre), W / 2, 240);
    if (this._champion) {
      c.fillStyle = '#fde047'; c.font = '800 46px "Baloo 2", sans-serif';
      c.fillText('🏆 ' + tx('¡CAMPEÓN!', 'CHAMPION!'), W / 2, 316);
    }
    c.fillStyle = '#7dd3fc'; c.font = '700 36px "Nunito Sans", sans-serif';
    c.fillText(tx('Apunta al mapa con la pala', 'Aim at the map with the paddle'), W / 2, 392);
    c.fillText(tx('y aprieta el gatillo para jugar', 'and pull the trigger to play'), W / 2, 442);
    this.cartelTex.needsUpdate = true;
  }
  rivalEstado(st) {
    const t = this.stTex[st] || this.stTex.base || null;
    if (t && this.standeeMat) { this.standeeMat.map = t; this.standeeMat.needsUpdate = true; }
  }

  /* ------------------------------ música -------------------------------- */
  musicOn() {
    try {
      const g = this.game;
      const actx = g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      this._musWanted = true;
      if (g.audio.arcPlaying) return;               // invariante UNA MELODÍA
      if (!this._musBuf && !this._musBusy) this._loadMusic(actx);
      else if (this._musBuf && !this._mus) this._startMusic(actx);
    } catch (e) { /* */ }
  }
  _loadMusic(actx) {
    const url = this.man && this.man.audio && this.man.audio.music;
    if (!url) return;
    this._musBusy = true;
    fetch(this._A(url)).then((r) => r.arrayBuffer())
      .then((ab) => new Promise((res, rej) => { try { res(actx.decodeAudioData(ab.slice(0))); } catch (e) { rej(e); } }))
      .then((buf) => { this._musBuf = buf; this._musBusy = false; if (this._musWanted) this._startMusic(actx); })
      .catch(() => { this._musBusy = false; });
  }
  _startMusic(actx) {
    try {
      if (this._mus || !this._musBuf) return;
      const g = this.game;
      if (g.audio.arcPlaying) return;
      const src = actx.createBufferSource();
      src.buffer = this._musBuf; src.loop = true;
      const gn = actx.createGain();
      const vol = (this.man && this.man.audio && this.man.audio.musicVolume) || 0.18;
      gn.gain.value = 0.0001;
      src.connect(gn); gn.connect(actx.destination);
      src.start();
      gn.gain.linearRampToValueAtTime(vol, actx.currentTime + 1.2);
      this._mus = { src, gn, vol };
    } catch (e) { /* */ }
  }
  musicOff() {
    try {
      this._musWanted = false;
      if (!this._mus) return;
      const { src, gn } = this._mus;
      const actx = src.context;
      gn.gain.cancelScheduledValues(actx.currentTime);
      gn.gain.setValueAtTime(gn.gain.value, actx.currentTime);
      gn.gain.linearRampToValueAtTime(0.0001, actx.currentTime + 0.4);
      window.setTimeout(() => { try { src.stop(); } catch (e) { /* */ } }, 500);
    } catch (e) { /* */ }
    this._mus = null;
  }
  champIntroPause(on) { try { on ? this.musicOff() : this.musicOn(); } catch (e) { /* */ } }

  /* --------------------------- ciclo principal -------------------------- */
  startChamp() {
    const g = this.game;
    this.build();
    this.group.visible = true;
    this.state = 'sala';
    g.rules.state = 'champtest';                 // árbitro dormido en la sala
    try {
      g.ball.pos.set(0, D().tableTopY + (D().ballRadius || 0.02), D().tableCenterZ + 0.45);
      g.ball.vel.set(0, 0, 0); g.ball.spin.set(0, 0, 0);
      if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
      g.ballMesh.visible = true;
    } catch (e) { /* */ }
    this._pintaCartel();
    this.cartel.visible = true;
    if (this.mapa) this.mapa.show();
    g.rules.message = tx('¡Bienvenido a ' + this.nombre + '!', 'Welcome to ' + this.nombre + '!');
    try { g.audio.announce(g.rules.message, true); } catch (e) { /* */ }
    this.rivalEstado('idle');
    this.musicOn();
  }
  leave() {
    const g = this.game;
    this.musicOff();
    this._poderClear();
    if (this.prueba) this.prueba.stop();
    try { if (g.rules.state === 'champtest') g.rules.startMatch('match'); } catch (e0) { /* */ }
    if (this.mapa) this.mapa.dispose();
    if (this.group && this.group.parent) this.group.parent.remove(this.group);
    for (const t of this._ownTex) { try { t.dispose(); } catch (e) { /* */ } }
    this._ownTex.clear();
    this.group = null;
  }
  resetRecords() {
    try {
      const dead = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && String(k).indexOf(this.base) === 0) dead.push(k);
      }
      for (const k of dead) { try { localStorage.removeItem(k); } catch (e2) { /* */ } }
    } catch (e) { /* */ }
    this.victorias = 0; this.stage = 0; this._champion = false;
    this._pintaCartel();
    if (this.mapa) this.mapa.refresh();
  }

  serveTrigger() {
    if (this.state !== 'sala') return;
    const et = this._etapa();
    if (et.kind === 'prueba') this._empezarPrueba(et);
    else this._empezarDuelo(et);
  }
  _empezarDuelo(et) {
    const g = this.game;
    if (g.net.online) { g.rules.message = tx('Sin duelo en línea', 'No duel online'); return; }
    this.state = 'duelo';
    this.cartel.visible = false;
    this.rivalEstado('duelo');
    g.rules.oppLabel = (this.man.rival && this.man.rival.oppLabel) || 'rival';
    try { g.rules.startMatch('match'); } catch (e) { /* */ }
    try { if (g.applyAISkill) g.applyAISkill(); } catch (e) { /* */ }
    g.rules.message = (et.id === 'final')
      ? tx('¡DUELO FINAL contra ' + this.rivalNombre + '!', 'FINAL DUEL vs ' + this.rivalNombre + '!')
      : tx('¡Duelo contra ' + this.rivalNombre + '!', this.rivalNombre + ' duel!');
    try {
      g.showInstrucciones(
        tx('Duelo contra ' + this.rivalNombre, this.rivalNombre + ' duel'),
        (et.id === 'final') ? [
          tx('El rival pelea a MÁXIMA POTENCIA. Primero a ' + this.puntosObjetivo + ' puntos.',
            'The rival fights at FULL POWER. First to ' + this.puntosObjetivo + ' points.'),
          tx('¡Gana y el campeonato es tuyo!', 'Win and the championship is yours!'),
        ] : [
          tx('Primero a ' + this.puntosObjetivo + ' puntos. La dificultad sube con cada duelo ganado.',
            'First to ' + this.puntosObjetivo + ' points. Difficulty rises with every duel won.'),
          tx('¡Cuidado con los superpoderes de ' + this.rivalNombre + '!',
            "Beware " + this.rivalNombre + "'s super powers!"),
        ],
        5.0, null);
    } catch (e) { /* */ }
    this._poderClear();
    this._bolsa.length = 0;
    this._powerCd = 6; this._dueloT = 0; this._toward = false;
    this.musicOn();
  }
  _empezarPrueba(et) {
    const g = this.game;
    this.state = 'prueba';
    g.rules.state = 'champtest';
    this.cartel.visible = false;
    this.rivalEstado('idle');
    const lineas = (et.modo === 'objetivos') ? [
      tx('Rompe las ' + et.objetivo + ' dianas flotando sobre la mesa.',
        'Blast the ' + et.objetivo + ' targets floating over the table.'),
      tx('Golpea la bola con la pala. Bolas infinitas.',
        'Hit the ball with the paddle. Endless balls.'),
    ] : [
      tx('Dianas EN MOVIMIENTO: rompe ' + et.objetivo + ' antes de que acabe el tiempo.',
        'MOVING targets: blast ' + et.objetivo + ' before time runs out.'),
      tx('Golpea la bola con la pala. Bolas infinitas.',
        'Hit the ball with the paddle. Endless balls.'),
    ];
    try {
      g.showInstrucciones(
        tx('PRUEBA · ' + et.name.toUpperCase(), 'SKILL TEST · ' + et.name.toUpperCase()),
        lineas, 7.5,
        () => {
          try { this._arrancarPrueba(et); } catch (e) { /* */ }
        }, null, { empezar: true });
      return;
    } catch (e) { /* */ }
    this._arrancarPrueba(et);
  }
  _arrancarPrueba(et) {
    const g = this.game;
    this._poderClear();
    this.state = 'prueba';
    this.prueba.start({ modo: et.modo, objetivo: et.objetivo, premio: et.premio, tiempo: 0 });
    this.musicOn();
  }
  _pruebaFin(win) {
    if (this._replay) return;                    // rejugada: el camino no cambia
    if (win) {
      this.stage = Math.min(this.etapas.length - 1, this.stage + 1);
      try { localStorage.setItem(this.base + 'stage', String(this.stage)); } catch (e) { /* */ }
    }
    // derrota: la etapa se repite (flujo amable de la plantilla)
  }
  _despuesDePrueba() {
    const g = this.game;
    this.state = 'sala';
    g.rules.state = 'champtest';
    this.cartel.visible = true;
    if (this._replay) {
      this.stage = this._replay.stage;
      this._replay = null;
      this._pintaCartel();
    }
    if (this.mapa) this.mapa.refresh();
    const et = this._etapa();
    g.rules.message = tx('Siguiente: ' + et.name, 'Next: ' + et.name);
    this.rivalEstado('idle');
    this.musicOn();
  }

  aiMul() {
    if (this.state !== 'duelo') return 1;
    const et = this._etapa();
    return (et && et.aiMul) || 1;
  }
  onPoint() {
    // disparo por PUNTOS (activación «cada X puntos»)
    if (this.state !== 'duelo') return;
    this._puntosSeguidos = (this._puntosSeguidos || 0) + 1;
    for (const p of this.poderes) {
      if ((p.activacion || 'rally') !== 'puntos') continue;
      const cada = Math.max(1, p.cadaCuantos | 0);
      if (this._puntosSeguidos % cada === 0) { this._poderLanzar(p); break; }
    }
  }
  onMatchOver(w) {
    const g = this.game;
    const won = (w === true) || (w === 'player');
    if (this._replay) {
      g.rules.message = won
        ? tx('¡Revancha ganada! El camino sigue igual.', 'Replay won! The path stays the same.')
        : tx('Rejugada perdida · el camino sigue igual.', 'Replay lost · the path stays the same.');
      this.rivalEstado(won ? 'derrotado' : 'triunfante');
      const real = this._replay.stage | 0;
      this._replay = null;
      this.stage = real;
      try { localStorage.setItem(this.base + 'stage', String(this.stage)); } catch (e1) { /* */ }
      this.state = 'sala';
      this.cartel.visible = true;
      this._pintaCartel();
      if (this.mapa) this.mapa.refresh();
      try { g.rules.startMatch('match'); } catch (e) { /* */ }
      g.rules.state = 'champtest';
      this.musicOn();
      return;
    }
    this.rivalEstado(won ? 'derrotado' : 'triunfante');
    const et = this._etapa();
    if (won) {
      this.victorias++;
      try { localStorage.setItem(this.base + 'wins', String(this.victorias)); } catch (e) { /* */ }
      if (et.id === 'final' && !this._champion) {
        this._champion = true;
        try { localStorage.setItem(this.base + 'champ', '1'); } catch (e) { /* */ }
        g.rules.message = tx('¡¡' + this.nombre.toUpperCase() + ' CONSEGUIDO!!', this.nombre.toUpperCase() + ' COMPLETED!!');
        try { const C = window.__PP_CORE; if (C && C.showChampConseguido) C.showChampConseguido(this.id); } catch (e2) { /* */ }
        try {
          const W = (typeof window !== 'undefined' && window.__PP_WORLD);
          if (W && typeof W.submit === 'function') {
            let nm = '';
            try { nm = String(localStorage.getItem('pp_player_name') || '').trim().slice(0, 12); } catch (e3) { /* */ }
            Promise.resolve(W.submit(this.id, { n: nm || 'Anónimo', p: this.victorias | 0, a: '🏆' })).catch(() => { /* */ });
          }
        } catch (e4) { /* */ }
      } else if (et.id === 'final') {
        g.rules.message = tx('¡Revancha ganada! El título sigue siendo tuyo.', 'Rematch won! The title is still yours.');
      } else {
        const sig = this.etapas[Math.min(this.stage + 1, this.etapas.length - 1)];
        this.stage = Math.min(this.etapas.length - 1, this.stage + 1);
        try { localStorage.setItem(this.base + 'stage', String(this.stage)); } catch (e) { /* */ }
        g.rules.message = tx('¡Has ganado el duelo! Siguiente: ' + sig.name, 'Duel won! Next: ' + sig.name);
      }
    } else {
      g.rules.message = tx(this.rivalNombre + ' gana… revancha al servir.', this.rivalNombre + ' wins… rematch on serve.');
    }
    this.state = 'sala';
    this.cartel.visible = true;
    this._pintaCartel();
    if (this.mapa) this.mapa.refresh();
    try { g.rules.startMatch('match'); } catch (e) { /* */ }
    g.rules.state = 'champtest';
    this.musicOn();
  }

  /* ------------------------- superpoderes (motor) ----------------------- */
  _poderClear() {
    this._act = null; this._aviso = null;
    this.powerSign.visible = false;
    this._mareoQuita();
    for (const c of this.confeti) { c.t = 9; c.s.material.opacity = 0; }
    for (const a of this.arena) { a.t = 9; a.s.material.opacity = 0; }
    for (const gb of this.globos) { gb.activo = false; gb.s.material.opacity = 0; }
    this.orbe.material.opacity = 0;
  }
  _poderLanzar(p) {
    if (this._act || this._aviso) return;
    if ((this._cool || 0) > 0) return;
    this._cool = Math.max(4, p.cooldown || 20);
    this._aviso = { p, t: Math.max(0.8, p.warn || 2) };
    this._pintaPower(tx(this.rivalNombre + ' PREPARA…', this.rivalNombre + ' READIES…'), p, '#fbbf24');
    try { this.game.audio.playOsc(330, 440, 0.22, 'triangle', 0.25, 0); } catch (e) { /* */ }
  }
  _pintaPower(txt, p, color) {
    const c = this.powCv.getContext('2d');
    c.clearRect(0, 0, 512, 128);
    c.fillStyle = 'rgba(8,13,28,.9)';
    c.beginPath(); c.roundRect(6, 6, 500, 116, 26); c.fill();
    c.lineWidth = 5; c.strokeStyle = color || '#22d3ee'; c.stroke();
    if (p) c.drawImage(this.medCv[p.kind] || this.medCv.confeti, 18, 14, 100, 100);
    c.fillStyle = '#fff'; c.textAlign = 'left';
    c.font = '800 44px "Baloo 2", sans-serif';
    c.fillText(String(txt || (p && p.name) || '').slice(0, 24), 132, 60);
    c.font = '600 30px "Nunito Sans", sans-serif';
    c.fillStyle = '#cbd5e1';
    c.fillText(p ? p.kind.toUpperCase() : '', 132, 102);
    this.powTex.needsUpdate = true;
    this.powerSign.visible = true;
  }
  _quizasPoder() {
    // disparo por RALLY con probabilidad (activación «durante el rally»)
    if (this.state !== 'duelo' || this._act || this._aviso) return;
    if ((this._cool || 0) > 0) return;
    if ((this._garantia || 0) > 22) {
      const p = this.poderes[0];
      if (p) this._poderLanzar(p);
      this._garantia = 0;
      return;
    }
    for (const p of this.poderes) {
      if ((p.activacion || 'rally') !== 'rally') continue;
      const ch = (typeof p.chance === 'number') ? p.chance : 0.35;
      if (Math.random() < ch) { this._poderLanzar(p); break; }
    }
  }
  _mareoPon() {
    const rig = this.game.rig;
    if (!rig || this._mareoBase) return;
    this._mareoBase = { y: rig.rotation.y, x: rig.rotation.x, z: rig.rotation.z };
    this._mareoDelta = 0;
  }
  _mareoQuita() {
    const rig = this.game.rig;
    if (!rig || !this._mareoBase) { this._mareoBase = null; return; }
    try {
      rig.rotation.y = this._mareoBase.y; rig.rotation.x = this._mareoBase.x; rig.rotation.z = this._mareoBase.z;
    } catch (e) { /* */ }
    this._mareoBase = null; this._mareoDelta = 0;
  }
  _poderEfectoArrancar(p) {
    const g = this.game;
    const Dc = D();
    if (p.kind === 'confeti') {
      for (const c of this.confeti) {
        c.t = 0; c.life = Math.max(2.5, p.duration || 5) * (0.7 + Math.random() * 0.5);
        c.x = (Math.random() * 2.4 - 1.2); c.z = Dc.tableCenterZ + (Math.random() * 2.6 - 0.6);
        c.y = 2.3 + Math.random() * 0.6; c.vy = -(0.55 + Math.random() * 0.35);
        c.s.material.opacity = 1;
      }
    } else if (p.kind === 'arena') {
      for (const a of this.arena) {
        a.t = 0; a.life = Math.max(1.6, (p.duration || 5) * 0.4);
        a.x = -2.2; a.y = 0.8 + Math.random() * 1.1; a.z = Dc.tableCenterZ + (Math.random() * 3 - 1);
        a.vx = 2.6 + Math.random() * 1.2;
        a.s.material.opacity = 0.85;
      }
    } else if (p.kind === 'globos') {
      for (const gb of this.globos) {
        gb.activo = true; gb.v = 0.32 + Math.random() * 0.14;
        gb.x = Dc.tableCenterZ >= 0 ? 0 : (Math.random() * 1.6 - 0.8);
        gb.x = (Math.random() * 1.7 - 0.85);
        gb.y = Dc.tableTopY + 0.25;
        gb.z = Dc.tableCenterZ + (Math.random() * 2.2 - 1.4);
        gb.s.material.opacity = 1;
      }
    } else if (p.kind === 'orbe') {
      this.orbe.material.opacity = 0.95;
    } else if (p.kind === 'mareo') {
      this._mareoPon();
    }
  }
  _poderUpdate(dt) {
    const g = this.game;
    this._cool = Math.max(0, (this._cool || 0) - dt);
    // disparo por rally: bola viniendo al jugador (patrón Locura v2.132)
    const rally = g.rules.state === 'rally';
    if (rally && g.ball && g.ball.vel) {
      const vz = g.ball.vel.z;
      if (vz > 0.35 && !this._toward) { this._toward = true; this._quizasPoder(); }
      if (vz < 0) this._toward = false;
      this._garantia = (this._garantia || 0) + dt;
    }
    // fase AVISO
    if (this._aviso) {
      this._aviso.t -= dt;
      this.powerSign.scale.setScalar(1 + Math.sin(this._t * 5.5) * 0.035);
      if (this._aviso.t <= 0) {
        const p = this._aviso.p;
        this._aviso = null;
        this._act = { p, t: Math.max(1, p.duration || 5) };
        this._pintaPower(tx('¡' + (p.name || p.kind).toUpperCase() + '!', (p.name || p.kind).toUpperCase() + '!'), p, '#22d3ee');
        try { g.audio.playOsc(660, 990, 0.2, 'sawtooth', 0.2, 0); } catch (e) { /* */ }
        try { this._poderEfectoArrancar(p); } catch (e) { console.warn('[taller.poder]', e); this._act = null; this.powerSign.visible = false; }
      }
      return;
    }
    // fase ACTIVA
    if (this._act) {
      this._act.t -= dt;
      const p = this._act.p;
      const dur = Math.max(1, p.duration || 5);
      const k = Math.max(0, this._act.t / dur);
      if (p.kind === 'confeti') {
        for (const c of this.confeti) {
          if (c.t >= c.life) continue;
          c.t += dt;
          c.y += c.vy * dt;
          c.x += Math.sin(this._t * 3 + c.ph) * 0.12 * dt;
          if (c.y < D().tableTopY - 0.4) { c.y = 2.4; }
          c.s.position.set(c.x, c.y, c.z);
          c.s.material.opacity = Math.min(1, k * 2.5);
        }
      } else if (p.kind === 'arena') {
        for (const a of this.arena) {
          if (a.t >= a.life) { a.t = 0; a.y = 0.8 + Math.random() * 1.1; a.x = -2.2; a.z = D().tableCenterZ + (Math.random() * 3 - 1); }
          a.t += dt;
          a.x += a.vx * dt;
          if (a.x > 2.4) a.x = -2.2;
          a.s.position.set(a.x, a.y + Math.sin(this._t * 4 + a.t) * 0.05, a.z);
          a.s.material.opacity = 0.85 * k;
        }
      } else if (p.kind === 'globos') {
        for (const gb of this.globos) {
          if (!gb.activo) continue;
          gb.y += gb.v * dt;
          gb.x += Math.sin(this._t * 1.3 + gb.v * 10) * 0.06 * dt;
          gb.s.position.set(gb.x, gb.y, gb.z);
          // pop por contacto con la bola (barrido prev→cur)
          try {
            const b = g.ball;
            if (b && b.__exPrev && b.pos) {
              const d = b.pos.distanceTo(gb.s.position);
              const dp = b.__exPrev.distanceTo(gb.s.position);
              const rr = 0.16 + (D().ballRadius || 0.02);
              if (Math.min(d, dp) < rr && Math.max(d, dp) < rr * 2.6) {
                gb.activo = false; gb.s.material.opacity = 0;
                try { g.audio.playNoise(0.12, 1800, 1.5, 0.4, 0); } catch (e2) { /* */ }
              }
            }
          } catch (e3) { /* */ }
        }
      } else if (p.kind === 'orbe') {
        const ang = this._t * 1.7;
        this.orbe.position.set(Math.cos(ang) * 0.8, D().tableTopY + 0.95 + Math.sin(this._t * 2.2) * 0.16, D().tableCenterZ - 0.9 + Math.sin(ang) * 0.3);
        this.orbe.material.opacity = 0.95 * (0.55 + 0.45 * k);
      } else if (p.kind === 'mareo') {
        const rig = g.rig;
        if (rig && this._mareoBase) {
          const A = 0.2 * k;
          const dy = Math.sin(this._t * 1.9) * A;
          rig.rotation.y = this._mareoBase.y + dy;
          this._mareoDelta = dy;
        }
      }
      if (this._act.t <= 0) {
        const fin = this._act.p;
        this._act = null;
        this.powerSign.visible = false;
        this._mareoQuita();
        for (const c of this.confeti) c.s.material.opacity = 0;
        for (const a of this.arena) a.s.material.opacity = 0;
        for (const gb of this.globos) { gb.activo = false; gb.s.material.opacity = 0; }
        this.orbe.material.opacity = 0;
        try { g.audio.playOsc(520, 260, 0.25, 'sine', 0.18, 0); } catch (e) { /* */ }
      }
    }
  }

  /* ------------------------- mapa del camino ---------------------------- */
  replayMap() {
    if (!this.mapa || !this.mapa.group || !this.mapa.group.visible) return null;
    return this.mapa.replayData();
  }
  replayHover(idx) { if (this.mapa) this.mapa.hover(idx | 0); }
  replayLaunch(i) {
    const g = this.game;
    i = i | 0;
    if (this.state === 'duelo' || (this.prueba && this.prueba.stepActive())) return;
    if (i >= (this.stage | 0)) {
      this.stage = i;
      try { localStorage.setItem(this.base + 'stage', String(this.stage)); } catch (e) { /* */ }
      this.startChamp();
      return;
    }
    this._replay = { stage: this.stage | 0 };
    this.stage = i;
    g.rules.message = tx('REJUGANDO la etapa ' + (i + 1) + ' · tu progreso no cambia',
      'REPLAYING stage ' + (i + 1) + ' · your progress stays');
    try { g.audio.announce(g.rules.message, true); } catch (e) { /* */ }
    this.startChamp();
  }

  /* ------------------------------- update ------------------------------- */
  update(dt) {
    const g = this.game;
    this._t += dt;
    try { if (g.aiPaddleMesh) g.aiPaddleMesh.visible = (this.state === 'duelo'); } catch (e) { /* */ }
    if (this.state === 'duelo') this._poderUpdate(dt);
    if (this.powerSign && this.powerSign.visible) {
      this.powerSign.scale.setScalar(1 + Math.sin(this._t * 5.5) * 0.035);
    }
    // standee respira
    if (this.standeeMesh && this.state !== 'duelo') {
      this.standeeMesh.position.y = 0.925 + Math.sin(this._t * 1.4) * 0.012;
    }
    if (this.mapa) this.mapa.tick(dt);
  }
}

/* ============================================================================
 *  MapaTaller — mapa del camino DIBUJADO EN CANVAS (sin arte externo)
 *  Contrato del núcleo (v2.96): replayMap() → { plane, nodesPx, imgW, imgH,
 *  maxIdx }; el núcleo raycastea la pala y el módulo pinta el resaltado.
 *  ============================================================================ */
class MapaTaller {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.IMG_W = 1280; this.IMG_H = 720;
    this.PW = 1.66; this.PH = 1.66 * 720 / 1280;
    this.inited = false;
    this.hover = -1;
    this.nodes = [];
  }
  build() {
    if (this.inited) return;
    this.inited = true;
    const g = this.game;
    this.group = new THREE.Group();
    const back = new THREE.Mesh(
      new THREE.BoxGeometry(this.PW + 0.06, this.PH + 0.06, 0.022),
      new THREE.MeshStandardMaterial({ color: 0x1a2436, roughness: 0.85, metalness: 0.1 }));
    back.position.z = -0.013;
    this.group.add(back);
    this.cv = document.createElement('canvas'); this.cv.width = this.IMG_W; this.cv.height = this.IMG_H;
    this.tex = texDeCanvas(this.cv);
    this.plane = new THREE.Mesh(new THREE.PlaneGeometry(this.PW, this.PH),
      new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, depthWrite: false }));
    this.group.add(this.plane);
    this.group.position.set(-1.05, 1.45, -3.58);
    this.group.rotation.y = 0.42;
    this.group.visible = false;
  }
  show() { this.build(); this.group.visible = true; this.refresh(); }
  hide() { if (this.group) this.group.visible = false; }
  dispose() { this.hide(); this.inited = false; }
  tick() { /* la textura se repinta en refresh/hover */ }
  refresh() {
    this.build();
    const c = this.cv.getContext('2d');
    const W = this.IMG_W, H = this.IMG_H;
    const etapas = this.ctrl.etapas;
    const n = etapas.length;
    this.nodes = [];
    c.clearRect(0, 0, W, H);
    // fondo
    const gr = c.createLinearGradient(0, 0, 0, H);
    gr.addColorStop(0, '#0f172a'); gr.addColorStop(1, '#1e293b');
    c.fillStyle = gr; c.fillRect(0, 0, W, H);
    c.fillStyle = 'rgba(251,191,36,.9)'; c.textAlign = 'center';
    c.font = '800 54px "Baloo 2", sans-serif';
    c.fillText(this.ctrl.nombre.toUpperCase().slice(0, 24), W / 2, 78);
    // camino: filas alternas
    const cols = Math.min(4, n);
    const filas = Math.ceil(n / cols);
    const x0 = W / 2, yTop = 190, dy = Math.min(230, (H - 260) / Math.max(1, filas - 1) || 0);
    const spanX = Math.min(1000, 260 * (cols - 1));
    for (let i = 0; i < n; i++) {
      const fila = Math.floor(i / cols);
      const idxFila = i % cols;
      const enFila = Math.min(cols, n - fila * cols);
      const cx = (enFila === 1) ? x0 : x0 - spanX / 2 + (spanX / (enFila - 1)) * idxFila;
      const cy = yTop + fila * dy + (fila % 2 ? 0 : 0);
      const r = 86;
      this.nodes.push({ x: cx, y: cy, r });
      const et = etapas[i];
      const hecho = i < this.ctrl.stage;
      const vigente = i === this.ctrl.stage;
      // path
      if (i > 0) {
        const pv = this.nodes[i - 1];
        c.strokeStyle = hecho ? '#fbbf24' : '#475569';
        c.lineWidth = 10;
        c.beginPath(); c.moveTo(pv.x, pv.y); c.lineTo(cx, cy); c.stroke();
      }
      // nodo
      c.beginPath(); c.arc(cx, cy, r, 0, Math.PI * 2);
      c.fillStyle = vigente ? '#b45309' : (hecho ? '#166534' : '#0b1222');
      c.fill();
      c.lineWidth = 10; c.strokeStyle = vigente ? '#fbbf24' : (hecho ? '#86efac' : '#334155');
      c.stroke();
      if (i > this.ctrl.stage) {
        // tapa «?» de las etapas futuras
        c.fillStyle = '#1e293b';
        c.beginPath(); c.arc(cx, cy, r * 0.94, 0, Math.PI * 2); c.fill();
        c.fillStyle = '#94a3b8'; c.font = '800 96px "Baloo 2", sans-serif';
        c.fillText('?', cx, cy + 34);
      } else {
        c.fillStyle = '#fff'; c.font = '800 74px "Baloo 2", sans-serif';
        c.fillText(String(i + 1), cx, cy + 6);
        c.fillStyle = et.kind === 'duelo' ? '#fca5a5' : '#7dd3fc';
        c.font = '700 34px "Nunito Sans", sans-serif';
        c.fillText((et.kind === 'duelo' ? '⚔ ' : '🎯 ') + et.name.slice(0, 20), cx, cy + r + 42);
      }
      if (this.hover === i) {
        c.beginPath(); c.arc(cx, cy, r * 1.13, 0, Math.PI * 2);
        c.strokeStyle = '#fbbf24'; c.lineWidth = 14; c.stroke();
      }
      if (vigente) {
        c.beginPath(); c.arc(cx, cy, r * 1.22, 0, Math.PI * 2);
        c.strokeStyle = 'rgba(251,191,36,.6)'; c.lineWidth = 8; c.stroke();
      }
    }
    c.fillStyle = '#64748b'; c.font = '600 30px "Nunito Sans", sans-serif';
    c.textAlign = 'center';
    c.fillText(this.ctrl.txMapa(), W / 2, H - 34);
    this.tex.needsUpdate = true;
  }
  hover(idx) {
    if (idx !== this.hover) { this.hover = idx; this.refresh(); }
  }
  replayData() {
    return { plane: this.plane, nodesPx: this.nodes, imgW: this.IMG_W, imgH: this.IMG_H, maxIdx: this.ctrl.stage | 0 };
  }
}

/* ====================== MÓDULO (contrato ChampLoader) ==================== */
const API = {
  id: 'taller',
  decor: null,
  room: null,
  get controller() { return CTRL; },
  isChampion() { return !!(CTRL && CTRL._champion); },
  champIntroPause(on) { if (CTRL) { try { on ? CTRL.musicOff() : CTRL.musicOn(); } catch (e) { /* */ } } },
  init(ctx) {
    if (!window.__PP_CORE) {
      throw new Error('taller: window.__PP_CORE no disponible (¿se cargó fuera del juego?)');
    }
    GAME.g = ctx.game;
    const man = ctx.manifest || {};
    CTRL = new PlantillaCtrl(ctx.game, man);
    CTRL.manifest = man;
    // el núcleo (createChampDecor / createChampRoom) lee decor/room DEL MÓDULO
    API.decor = (man.decor && Array.isArray(man.decor.pieces)) ? man.decor : null;
    API.room = man.room || null;
    API.id = man.id || 'taller';
    TL = (window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
    document.addEventListener('pp-lang', () => {
      TL = (window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
    });
  },
  start() { if (CTRL) CTRL.startChamp(); },
  leave() { if (CTRL) CTRL.leave(); },
  resetRecords() { if (CTRL) CTRL.resetRecords(); },
  update(dt) { if (CTRL && CTRL.state) CTRL.update(dt); },
  onPoint(it) { if (CTRL) CTRL.onPoint(it); },
  onMatchOver(w) { if (CTRL) CTRL.onMatchOver(w); },
  aiMul() { return CTRL ? CTRL.aiMul() : 1; },
  serveTrigger(i) { if (CTRL) CTRL.serveTrigger(i); },
  reenter() {
    if (!CTRL) return;
    try {
      if (CTRL.state === 'duelo') { CTRL.game.rules.state = 'serve'; }
      else CTRL.startChamp();
    } catch (e) { /* */ }
  },
  replayMap() { return CTRL ? CTRL.replayMap() : null; },
  replayHover(idx) { if (CTRL) CTRL.replayHover(idx); },
  replayLaunch(idx) { if (CTRL) CTRL.replayLaunch(idx); },
  musicOff() { if (CTRL) CTRL.musicOff(); },
  testActive() { return !!(CTRL && CTRL.prueba && CTRL.prueba.stepActive()); },
  testStep(dt) {
    if (CTRL && CTRL.prueba && CTRL.prueba.stepActive()) {
      try { CTRL.prueba.step(dt); }
      catch (e) { console.warn('[taller.testStep]', e); }
    }
  },
};
export default API;

