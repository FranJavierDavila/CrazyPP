/* ============================================================================
 *  @TITULO_ES@ (@ID@) — campeonato generado por crear_campeonato.py
 *  ----------------------------------------------------------------------------
 *  PLANTILLA «STOCK» del sistema común de campeonatos (contrato 1, v2.125).
 *  Usa SOLO la superficie documentada en scripts/plataforma/AUDITORIA.md:
 *    · sala de espera propia (cartel + rival + BSO privada del módulo)
 *    · DUELO = partida del NÚCLEO con la dificultad del campeonato (aiMul)
 *    · superpoderes del stock (confeti) con el motor de dos fases
 *  El artista rellena assets/ (ver LEEME-ASSETS.txt); la lógica ya funciona.
 *  ========================================================================== */
import * as THREE from 'three';   // importmap del núcleo: MISMA instancia

const CORE = (typeof window !== 'undefined' && window.__PP_CORE) || null;
const GAME = { g: null };
let CTRL = null;
let TL = 'es';

const tx = (es, en) => (TL === 'en' ? (en || es) : es);

/* ----------------------------- CONFIRACIÓN ------------------------------- */
const CFG = {
  rival: '@RIVAL_NOMBRE@',
  duelo: {
    aiMul: @DIFICULTAD@,            // multiplicador de IA del núcleo
    puntos: @PUNTOS@,               // puntos para ganar el duelo
  },
  poderes: @PODERES_JSON@,          // [{kind,name,chance,cooldown,duration}]
};

/* ------------------------- TEXTURA DE CONFETI ---------------------------- */
function _texConfeti() {
  const cv = document.createElement('canvas');
  cv.width = 32; cv.height = 32;
  const c = cv.getContext('2d');
  const colores = ['#ff5252', '#ffd740', '#40c4ff', '#69f0ae', '#ff4081'];
  c.fillStyle = colores[(Math.random() * colores.length) | 0];
  c.fillRect(4, 4, 24, 24);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* ============================ CONTROLADOR ================================ */
class StockController {
  constructor(game) {
    this.game = game;
    this.group = new THREE.Group();
    this.state = 'sala';           // sala | duelo
    this.ronda = 1;
    this.victorias = 0;
    this._ownTex = new Set();
    this._confeti = null;          // poder activo
    this._powerCd = 0;
    this._mus = null;
    this._musBuf = null;
    this._musBusy = false;
    this._musWanted = false;
    this._musRamp = 0;
  }

  _A(p) { return new URL('./assets/' + p, import.meta.url).href; }
  _ct(cv) {
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    this._ownTex.add(t);
    return t;
  }

  /* --------------------------- CONSTRUCCIÓN ----------------------------- */
  build() {
    const g = this.game;
    const D = (CORE && CORE.DIMS) || { tableCenterZ: -1.6, tableTopY: 0.76 };
    const zRival = D.tableCenterZ - 1.9;

    // RIVAL: standee con el arte del artista (assets/rival.webp)
    const texRival = this._ct(new Image());
    texRival.onload = () => { this._rival.needsUpdate = true; };
    texRival.src = this._A('rival.webp');
    this._rival = texRival;
    const rivalMat = new THREE.MeshBasicMaterial({
      map: texRival, transparent: true, alphaTest: 0.25, depthWrite: false,
    });
    this.rivalMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.75), rivalMat);
    this.rivalMesh.position.set(0, 0.875, zRival);
    this.group.add(this.rivalMesh);
    this.rivalEstado('idle');

    // CARTEL de bienvenida sobre la mesa
    const cv = document.createElement('canvas');
    cv.width = 512; cv.height = 256;
    const c = cv.getContext('2d');
    c.fillStyle = '#1b2130';
    c.fillRect(0, 0, 512, 256);
    c.strokeStyle = '@COLOR@'; c.lineWidth = 10;
    c.strokeRect(8, 8, 496, 240);
    c.fillStyle = '#f4ecdd';
    c.textAlign = 'center';
    c.font = 'bold 44px Trebuchet MS, sans-serif';
    c.fillText(tx('@TITULO_ES@'.toUpperCase(), '@TITULO_EN@'.toUpperCase()), 256, 92);
    c.font = '26px Trebuchet MS, sans-serif';
    c.fillText(tx('APUNTA AL CARTEL Y PULSA EL GATILGO', 'AIM AT THE SIGN AND PULL THE TRIGGER'), 256, 152);
    c.fillText(tx('para empezar el duelo', 'to start the duel'), 256, 190);
    const texCartel = this._ct(cv);
    this.cartel = new THREE.Mesh(new THREE.PlaneGeometry(1.15, 0.575),
      new THREE.MeshBasicMaterial({ map: texCartel, depthWrite: false }));
    this.cartel.position.set(0, D.tableTopY + 0.62, D.tableCenterZ + 0.55);
    this.cartel.rotation.x = -0.42;
    this.group.add(this.cartel);

    g.scene.add(this.group);
  }

  rivalEstado(estado) {
    // assets/<estado>.webp si existe; si no, mantiene el actual
    try {
      const img = new Image();
      img.onload = () => { this._rival.image = img; this._rival.needsUpdate = true; };
      img.src = this._A(estado + '.webp');
    } catch (e) { /* sin estado: sigue */ }
  }

  /* ------------------------------ MÚSICA --------------------------------
   *  Motor privado siguiendo el patrón magia/oeste v2.124+2.125:
   *  fundido de entrada 0,8 s · sigue el ajuste global del núcleo ·
   *  resucita si el contexto cambia (re-bind de VR) · NO entra si la BSO
   *  del núcleo ya está sonando (UNA MELODÍA). decodeAudioData SIEMPRE en
   *  forma promesa y con copia (la forma callback puede no dispararse). */
  _musicEffVol() {
    try {
      const A = this.game && this.game.audio;
      if (!A) return 0.18;
      return (A.arcMute || A._arcDucked) ? 0.0001 : Math.max(0.0001, A.arcVol);
    } catch (e) { return 0.18; }
  }
  musicOn() {
    try {
      const g = this.game;
      const actx = g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      if (this._mus && this._mus.src.context !== actx) this._mus = null;
      this._musWanted = true;
      const A0 = g.audio;
      if (A0 && A0.arcPlaying) return;               // UNA MELODÍA
      if (!this._musBuf && !this._musBusy) this._loadMusic(actx);
      else if (this._musBuf && !this._mus) this._startMusic(actx);
    } catch (e) { /* sin música: nunca rompe */ }
  }
  _loadMusic(actx) {
    try {
      let url = null;
      try { url = (this.manifest && this.manifest.audio && this.manifest.audio.music)
        ? new URL('./' + this.manifest.audio.music, import.meta.url).href : this._A('bso.mp3');
      } catch (e) { url = this._A('bso.mp3'); }
      if (!url || this._musBusy) return;
      this._musBusy = true;
      fetch(url)
        .then((r) => r.arrayBuffer())
        .then((ab) => actx.decodeAudioData(ab.slice(0)))
        .then((buf) => {
          this._musBuf = buf; this._musBusy = false;
          if (this._musWanted) this._startMusic(actx);
        })
        .catch(() => { this._musBusy = false; });
    } catch (e) { /* */ }
  }
  _startMusic(actx) {
    try {
      if (this._mus || !this._musBuf) return;
      const A0 = this.game && this.game.audio;
      if (A0 && A0.arcPlaying) return;               // UNA MELODÍA
      const gain = actx.createGain();
      const t0 = actx.currentTime;
      gain.gain.setValueAtTime(0.0001, t0);
      gain.gain.linearRampToValueAtTime(this._musicEffVol(), t0 + 0.8);
      this._musRamp = t0 + 0.8;
      gain.connect(actx.destination);
      const src = actx.createBufferSource();
      src.buffer = this._musBuf;
      src.loop = true;
      src.connect(gain);
      src.start();
      this._mus = { gain, src };
    } catch (e) { this._mus = null; }
  }
  _syncMusicGain() {
    try {
      const A = this.game && this.game.audio;
      if (this._mus && A && A.ctx && this._mus.src.context !== A.ctx) {
        this._mus = null;                            // re-bind: resucita
        if (this._musWanted && this._musBuf && A.ctx.state === 'running') {
          this._startMusic(A.ctx);
          return;
        }
      }
      if (!this._mus || !this._mus.gain) return;
      const gn = this._mus.gain.gain;
      const eff = this._musicEffVol();
      if (this._musRamp && A && A.ctx && A.ctx.currentTime < this._musRamp) return;
      if (A && A.ctx && Math.abs((gn.value || 0) - eff) > 0.001) {
        const t = A.ctx.currentTime;
        gn.cancelScheduledValues(t);
        gn.setValueAtTime(Math.max(0.0001, gn.value || 0.0001), t);
        gn.linearRampToValueAtTime(eff, t + 0.15);
      }
    } catch (e) { /* */ }
  }
  musicOff() {
    this._musWanted = false;
    if (this._mus) {
      try { this._mus.src.stop(); } catch (e) { /* */ }
      try { this._mus.gain.disconnect(); } catch (e) { /* */ }
      this._mus = null;
    }
  }

  /* --------------------------- CICLO / CONTRATO ------------------------- */
  startChamp() {
    const g = this.game;
    this.build();
    this.group.visible = true;
    this.state = 'sala';
    g.rules.message = tx('¡Bienvenido a @TITULO_ES@!', 'Welcome to @TITULO_EN@!');
    this.musicOn();
  }
  leave() {
    this.musicOff();
    if (this.group.parent) this.group.parent.remove(this.group);
    for (const t of this._ownTex) { try { t.dispose(); } catch (e) { /* */ } }
    this._ownTex.clear();
  }
  resetRecords() {
    try {
      const dead = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && String(k).indexOf('@STORAGE@') === 0) dead.push(k);
      }
      for (const k of dead) { try { localStorage.removeItem(k); } catch (e2) { /* */ } }
    } catch (e) { /* */ }
    this.victorias = 0;
    this.ronda = 1;
  }

  /* DUELO = partida del NÚCLEO (a 11, árbitro estándar): el campeonato
   * aporta sala, rival, música, dificultad (aiMul) y superpoderes. */
  _empezarDuelo() {
    const g = this.game;
    if (g.net.online) { g.rules.message = tx('Sin duelo en línea', 'No duel online'); return; }
    this.state = 'duelo';
    this.cartel.visible = false;
    g.rules.startMatch('match');      // marcador a cero + saque propio
    g.rules.message = tx('¡Duelo contra ' + CFG.rival + '!', CFG.rival + ' duel!');
    this.rivalEstado('duelo');
    this._showInstr();
  }
  _showInstr() {
    try {
      this.game.showInstrucciones(tx('Duelo contra ' + CFG.rival, CFG.rival + ' duel'), [
        tx('Primero a 11 puntos. La dificultad sube con cada duelo ganado.',
           'First to 11 points. Difficulty rises with every duel won.'),
        tx('¡Cuidado con los superpoderes de ' + CFG.rival + '!',
           'Beware ' + CFG.rival + '\'s super powers!'),
      ], 5.0, null, '@ID@');
    } catch (e) { /* */ }
  }

  serveTrigger() {
    if (this.state === 'sala') { this._empezarDuelo(); return; }
  }
  aiMul() {
    if (this.state !== 'duelo') return 1;
    return CFG.duelo.aiMul * (1 + Math.min(0.5, (this.ronda - 1) * 0.08));
  }
  onPoint(it) {
    // superpoder: probabilidad por punto jugado (motor simple del stock)
    if (this.state === 'duelo') this._quizasPoder();
  }
  onMatchOver(won) {
    const g = this.game;
    this.rivalEstado(won ? 'derrotado' : 'triunfante');
    if (won) {
      this.victorias++;
      try { localStorage.setItem('@STORAGE@wins', String(this.victorias)); } catch (e) { /* */ }
      g.rules.message = tx('¡Has ganado el duelo!', 'Duel won!');
    } else {
      g.rules.message = tx(CFG.rival + ' gana… revancha al servir.', CFG.rival + ' wins… rematch on serve.');
    }
    this.state = 'sala';
    this.cartel.visible = true;
    this.ronda++;
    g.rules.startMatch('match');      // el árbitro queda limpio y en saque
    this.musicOn();
  }
  update(dt) {
    this._syncMusicGain();
    if (this._powerCd > 0) this._powerCd -= dt;
    if (this._confeti) this._confetiStep(dt);
  }
  reenter() {
    // vuelta de VR: el árbitro vuelve a dormir y la música resucita sola
    const g = this.game;
    g.rules.state = 'serve';
    this.musicOn();
  }

  /* --------------------------- SUPERPODER STOCK -------------------------
   *  CONFETI: lluvia sobre TU campo (z −1,50..+0,05 — convención del núcleo),
   *  pool construido UNA vez (regla Quest), estorba la vista ~8 s. */
  _quizasPoder() {
    for (const p of CFG.poderes) {
      if (p.kind !== 'confeti') continue;          // los demás: módulo propio
      if (this._powerCd > 0) continue;
      if (Math.random() < (p.chance || 0.3)) {
        this._confetiStart(p);
        this._powerCd = p.cooldown || 25;
      }
      break;
    }
  }
  _confetiStart(p) {
    const g = this.game;
    if (!this._poolConfeti) {
      this._poolConfeti = [];
      const tex = _texConfeti();
      this._ownTex.add(tex);
      for (let i = 0; i < 40; i++) {
        const s = new THREE.Sprite(new THREE.SpriteMaterial({
          map: tex, transparent: true, depthWrite: false, opacity: 0,
        }));
        s.renderOrder = 30;
        g.rig.add(s);
        this._poolConfeti.push({ s, on: false, x: 0, y: 0, z: 0, vy: 0, vr: 0 });
      }
    }
    this._confeti = { t: 0, dur: (p.duration || 8) };
    g.rules.message = tx('¡' + p.name + '!', p.name + '!');
    try { g.audio.playNoise(0.5, 900, 0.4, 0.05, 0); } catch (e) { /* */ }
  }
  _confetiStep(dt) {
    const c = this._confeti;
    c.t += dt;
    const dentro = c.t < c.dur;
    for (const p of this._poolConfeti) {
      if (!p.on && dentro && Math.random() < dt * 8) {
        p.on = true;
        p.x = (Math.random() * 2 - 1) * 1.2;
        p.y = 2.0 + Math.random() * 0.4;
        p.z = -1.50 + Math.random() * 1.55;        // TU campo (confeti del núcleo)
        p.vy = -(0.35 + Math.random() * 0.3);
        p.vr = (Math.random() - 0.5) * 6;
      }
      if (p.on) {
        p.y += p.vy * dt;
        p.s.material.rotation += p.vr * dt;
        p.s.position.set(p.x, p.y, p.z);
        p.s.material.opacity = Math.min(1, p.y * 2);
        if (p.y < 0.1 || !dentro) { p.on = false; p.s.material.opacity = 0; }
      }
    }
    if (!dentro && c.t > c.dur + 1.5) { this._confeti = null; }
  }
}

/* ====================== MÓDULO (contrato ChampLoader) ==================== */
export default {
  id: '@ID@',
  decor: @DECOR_JSON@,
  room: @ROOM_JSON@,
  get controller() { return CTRL; },
  init(ctx) {
    if (!window.__PP_CORE) {
      throw new Error('@ID@: window.__PP_CORE no disponible (¿se cargó fuera del juego?)');
    }
    GAME.g = ctx.game;
    CTRL = new StockController(ctx.game);
    CTRL.manifest = ctx.manifest || null;   // v2.125: el núcleo lo entrega
    TL = (window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
    const onLang = () => {
      TL = (window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
    };
    document.addEventListener('pp-lang', onLang);
  },
  start() { if (CTRL) CTRL.startChamp(); },
  leave() { if (CTRL) CTRL.leave(); },
  resetRecords() { if (CTRL) CTRL.resetRecords(); },
  update(dt) { if (CTRL && CTRL.state) CTRL.update(dt); },
  onPoint(it) { if (CTRL) CTRL.onPoint(it); },
  onMatchOver(w) { if (CTRL) CTRL.onMatchOver(w); },
  aiMul() { return CTRL ? CTRL.aiMul() : 1; },
  serveTrigger(i) { if (CTRL) CTRL.serveTrigger(i); },
  reenter() { if (CTRL) CTRL.reenter(); },
  musicOff() { if (CTRL) CTRL.musicOff(); },   // invariante UNA MELODÍA v2.125
  testActive() { return false; },              // el duelo del stock usa el árbitro del núcleo
};
