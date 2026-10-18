/* ============================================================================
 *  CRAZY PING PONG · SDK DE CAMPEONATOS (champ_sdk.js) — v1.2.0
 * ----------------------------------------------------------------------------
 *  FASE 3 del plan de modularización P0 (acordado con el dueño).
 *  v1.1.0 (FASE 4): precarga() (pedir+decodificar sin sonar, para los
 *  patrones load* de la casa) y play(name, vol, opts) con opts.pan
 *  (StereoPanner opcional, el paneo de la risa del Oeste).
 *  v1.2.0 (FASE 5): createMusic() — los tres motores de MÚSICA en bucle
 *  que seguían duplicados (BSO del saloon v2.78+v2.124, música del vagón
 *  v2.111 y la WAV de Valle Neón) convergen en UNA sola máquina de
 *  estados con variantes por opciones, CONDUCTA IDÉNTICA a cada motor
 *  original: fundido de entrada, sincronía en vivo con el ajuste global
 *  del núcleo, UNA MELODÍA, resurrección de contexto (v2.124) y parada
 *  instantánea o con fundido.
 *
 *  POR QUÉ EXISTE — LA FAMILIA DE BUGS:
 *  Los 5 campeonatos son módulos autocontenidos que reimplementaban una y
 *  otra vez las mismas piezas del kernel. Cada reimplementación era una
 *  oportunidad nueva para el mismo bug:
 *    · El fix «v2.125: forma promesa» de decodeAudioData (la forma callback
 *      puede NO dispararse jamás en Chromium con la GPU saturada) está
 *      copy-pasted 7 veces en oeste y 2 en magia — y el orbital lo volvió a
 *      escribir distinto en v3.6.0.
 *    · El congelado del aviso de superpoder (g.freezeT, patrón de La Locura
 *      v2.40) NO existía en el orbital hasta SUP1: cada módulo decide por su
 *      cuenta si congela → conducta desigual e informes del dueño.
 *    · El puente al núcleo (window.__PP_CORE) está duplicado en los 5
 *      módulos (48 referencias).
 *  Desde esta fase, el kernel vive AQUÍ y los campeonatos lo importan. Un
 *  bug del kernel se arregla UNA vez y sirven los 5.
 *
 *  REGLAS DEL SDK:
 *    · Cero dependencias (ni siquiera THREE): sólo WebAudio/fetch/window.
 *    · NUNCA rompe el frame: todo método está blindado con try/catch.
 *    · Los campeonatos pasan SU propia URL de módulo (import.meta.url) para
 *      que los assets se resuelvan relativos a SU carpeta assets/.
 *    · Comportamiento canónico = la implementación más reciente con QA
 *      verde (orbital v3.6.0-SUP1 · locura v2.40).
 *
 *  MIGRACIÓN — FASE 5 HECHA (v3.6.3-SDK3): además de lo anterior, la
 *  MÚSICA en bucle se unifica con createMusic — oeste (BSO del saloon
 *  + música del vagón, manifest v50), magia (BSO, v30) y valle_neon
 *  (música WAV, v3) — y el fix v2.125 del decodeAudioData vive UNA vez
 *  aquí también para la música. PENDIENTE en SDK v1.x: Sala6/Rival/HUD
 *  compartidos.
 * ===================================================================== */

/* Versión del SDK (QA la verifica por window.__PP_SDK). */
const SDK_VERSION = '1.2.0';

try {
  if (typeof window !== 'undefined') window.__PP_SDK = SDK_VERSION;
} catch (e) { /* sin window: silencio */ }

/* — Puente al núcleo ————————————————————————————————————————————————
 *  Sustituye el patrón `const CORE = (typeof window !== 'undefined' &&
 *  window.__PP_CORE) || null;` duplicado en los 5 campeonatos. */
export function getCore() {
  try {
    return (typeof window !== 'undefined' && window.__PP_CORE) || null;
  } catch (e) { return null; }
}

/* — URL de asset del campeonato —————————————————————————————————————
 *  Igual que el método _A() de la casa: resuelve './assets/<p>' relativo
 *  al MÓDULO DEL CAMPEONATO (no del SDK) — por eso hay que pasarle el
 *  import.meta.url del llamador. */
export function assetURL(moduleURL, p) {
  try { return new URL('./assets/' + p, moduleURL).href; }
  catch (e) { return p; }
}

/* — CONGELADO DE PARTIDA (patrón de la casa, La Locura v2.40) ————————
 *  game.freezeT gatea IA/física/saque/árbitro en el núcleo. congela()
 *  alarga la congelación SIN acortar una ya en curso (Math.max) y
 *  descongela() la limpia al salir de un estado (locura: «nunca salir
 *  del arcade congelado»). Nunca rompe si el juego no lo permite. */
export function congela(game, seg) {
  try { game.freezeT = Math.max(game.freezeT || 0, seg); }
  catch (e) { /* sin congelación: nunca rompe */ }
}

export function descongela(game) {
  try { game.freezeT = 0; }
  catch (e) { /* */ }
}

/* — MOTOR DE SFX (fetch + decodeAudioData + cache + mute) ————————————
 *  La implementación CANÓNICA de la familia (orbital v3.6.0-SUP1, QA
 *  verde en 75 checks):
 *    · fetch + decodeAudioData EN FORMA PROMESA (lección v2.125: la forma
 *      callback puede quedarse SIN llamar a sus callbacks en Chromium con
 *      la GPU saturada — la música del vagón del oeste moría y el busy
 *      quedaba colgado para siempre).
 *    · decode UNA vez por sonido, cache por nombre, guard anti-doble-petición.
 *    · Respeta el silencio del arcade (arcMute / _arcDucked → 0,0001).
 *    · Si el AudioContext no está running, no hace nada (y NO pide).
 *    · Jamás lanza: un SFX fallido no rompe el frame.
 *
 *  Uso desde un campeonato:
 *      import { createSfx } from '../sdk/champ_sdk.js';
 *      ...
 *      this._sdkSfx = createSfx(import.meta.url, () => this.game);
 *      this._sdkSfx.precarga('risa_astro.mp3');   // opcional: calienta cache
 *      this._sdkSfx.play('risa_astro.mp3');
 *      this._sdkSfx.play('risas.mp3', 0.8, { pan: 0.4 });  // paneo derecho
 *
 *  moduleURL: import.meta.url DEL CAMPEONATO (los assets cuelgan de su
 *  carpeta assets/). getGame: función que devuelve el objeto game del
 *  núcleo (se consulta en cada play — el game puede llegar tarde). */
export function createSfx(moduleURL, getGame) {
  const bufs = Object.create(null);   // nombre → AudioBuffer decodificado
  const busy = Object.create(null);   // nombre → petición en vuelo

  function url(p) { return assetURL(moduleURL, p); }

  /* Petición + decodificación UNA vez (la lección v2.125: forma promesa).
   * No exige ctx running (decodificar vale con el contexto suspendido):
   * así la precarga del patrón load* funciona igual que los motores
   * antiguos. Guard anti-doble-petición por nombre. */
  function pedir(name) {
    const g = (typeof getGame === 'function') ? getGame() : getGame;
    const actx = g && g.audio && g.audio.ctx;
    if (!actx) return;                   // sin contexto: nada que decodificar
    if (bufs[name] || busy[name]) return;
    busy[name] = true;
    fetch(url(name))
      .then((r) => r.arrayBuffer())
      .then((ab) => actx.decodeAudioData(ab.slice(0)))  // forma promesa (v2.125)
      .then((buf) => { bufs[name] = buf; busy[name] = false; })
      .catch(() => { busy[name] = false; });
  }

  function play(name, vol, opts) {
    try {
      const g = (typeof getGame === 'function') ? getGame() : getGame;
      const actx = g && g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      pedir(name);
      const buf = bufs[name];
      if (!buf) return;                    // aún decodificando: en silencio
      const src = actx.createBufferSource();
      src.buffer = buf;
      const gn = actx.createGain();
      const A = g.audio;
      gn.gain.value = (A && (A.arcMute || A._arcDucked)) ? 0.0001
                                                         : (vol == null ? 0.65 : vol);
      let nodo = gn;
      const pan = opts && opts.pan;      // v1.1.0: paneo estéreo opcional
      if (pan && actx.createStereoPanner) {
        const pn = actx.createStereoPanner();
        pn.pan.value = pan;              // −1 izquierda · +1 derecha
        gn.connect(pn);
        nodo = pn;
      }
      nodo.connect(actx.destination);
      src.start();
    } catch (e) { /* sin SFX: nunca rompe el frame */ }
  }

  /* Pedir + decodificar SIN sonar (patrón load* de la casa). */
  function precarga(name) {
    try { pedir(name); } catch (e) { /* nunca rompe */ }
  }

  function tiene(name) { return !!bufs[name]; }   // para diagnósticos/QA

  return { play, url, tiene, precarga };
}

/* — Export por defecto (comodidad para imports cortos) ——————————————— */
/* — MOTOR DE MÚSICA EN BUCLE (createMusic · v1.2.0 · FASE 5) ——————————
 *  La familia de motores de música que la casa llevaba años copiando y
 *  divergiendo, unificada CON CONDUCTA IDÉNTICA por variante:
 *    · BSO canónica (oeste saloon v2.78+v2.124 · magia): fundido de
 *      entrada 0,8 s con ancla explícita, volumen efectivo del núcleo
 *      EN VIVO (arcMute/_arcDucked/arcVol, rampa 0,15 s con guard de
 *      fundido), gate UNA MELODÍA (arcPlaying) al arrancar, RESURREC-
 *      CIÓN de contexto (v2.124: renace al re-bind de VR) y parada
 *      instantánea.
 *    · Música del vagón del oeste (v2.111): sin fundido (volumen
 *      directo), sync directo sin rampa, sin gate arcPlaying y sin
 *      resurrección; la exclusividad con la BSO (ranura _mus compartida
 *      del original) se reproduce con opts.excluso.
 *    · Valle Neón (v1): volumen FIJO del manifest, fundido de entrada
 *      1,2 s SIN ancla, gate arcPlaying también dentro de on(), SIN
 *      sync de volumen y parada CON fundido 0,4 s (+ stop a 500 ms).
 *  El fix v2.125 (decodeAudioData EN FORMA PROMESA — la callback puede
 *  NO dispararse jamás en Chromium con la GPU saturada) vive AQUÍ de
 *  una vez para TODAS las músicas.
 *
 *  Uso desde un campeonato (el estado vive DENTRO del motor — la
 *  ranura UNA MELODÍA es privada de cada instancia):
 *      // pereza: se crea al primer uso y el módulo conserva sus métodos
 *      get _musSDK() {
 *        if (!this.__musSDK) this.__musSDK = createMusic(() => this.game, {
 *          url: () => this.manifest && this.manifest.musicUrl,
 *          vol: () => this._musicEffVol(),
 *          puede: () => this._stageMode !== 'tren',   // sólo oeste
 *        });
 *        return this.__musSDK;
 *      }
 *      musicOn()        → this._musSDK.on()
 *      musicOff()       → this._musSDK.off()
 *      _syncMusicGain() → this._musSDK.sync()
 *
 *  opts (todo opcional salvo url y vol; los POR DEFECTO = BSO canónica):
 *    url        () => string|undefined — de dónde bajar el bucle
 *    vol        () => number           — volumen objetivo (se consulta VIVO)
 *    puede      () => bool             — gate extra para (re)arrancar en sync
 *    fadeIn     s (0,8)                — 0 = volumen directo sin fundido
 *    ancla      bool (true)            — setValueAtTime(0.0001,t0) antes de rampa
 *    syncMode   'ramp'|'direct'|'none' — cómo sigue el volumen en vivo
 *    gateStart  bool (true)            — gate arcPlaying al arrancar
 *    gateOn     bool (false)           — gate arcPlaying dentro de on()
 *    renace     bool (true)            — resurrección de contexto (v2.124)
 *    stopFade   s (0)                  — fundido al parar (0 = instantáneo)
 *    excluso    () => bool             — true = NO arrancar (otra música suena) */
export function createMusic(getGame, opts) {
  const o = opts || {};
  let mus = null;        // { gain, src } — la RANURA (una melodía por motor)
  let buf = null;        // AudioBuffer decodificado (una sola vez)
  let busy = false;      // petición en vuelo
  let wanted = false;    // el _musWanted de la casa
  let rampHasta = 0;     // el _musRamp de la casa (guard del fundido)

  function gg() { return (typeof getGame === 'function') ? getGame() : getGame; }
  function ctx() {
    try { const a = gg() && gg().audio; return a && a.ctx; } catch (e) { return null; }
  }
  function objetivo() { try { return o.vol ? o.vol() : 0.15; } catch (e) { return 0.15; } }
  function srcURL() { try { return o.url ? o.url() : undefined; } catch (e) { return undefined; } }
  function puede() { try { return o.puede ? !!o.puede() : true; } catch (e) { return false; } }
  function excluso() { try { return o.excluso ? !!o.excluso() : false; } catch (e) { return true; } }
  function arcPlaying() {
    try { const a = gg() && gg().audio; return !!(a && a.arcPlaying); } catch (e) { return false; }
  }

  /* Carga UNA vez (lección v2.125: forma promesa). Sin exigir ctx running
   * para DECODIFICAR — igual que los motores antiguos. */
  function cargar(actx) {
    const u = srcURL();
    if (!u || busy || buf) return;
    busy = true;
    fetch(u)
      .then((r) => r.arrayBuffer())
      .then((ab) => new Promise((res, rej) => {
        // v2.125: FORMA PROMESA — la callback puede quedarse SIN llamar
        try { res(actx.decodeAudioData(ab.slice(0))); } catch (e) { rej(e); }
      }))
      .then((b) => { buf = b; busy = false; if (wanted) arrancar(actx); })
      .catch(() => { busy = false; });
  }

  function arrancar(actx) {
    try {
      if (mus || !buf) return;
      if (o.gateStart !== false && arcPlaying()) return;   // UNA MELODÍA
      if (excluso()) return;                               // ranura ocupada
      const gain = actx.createGain();
      const v = objetivo();
      const fi = (o.fadeIn == null) ? 0.8 : o.fadeIn;
      if (fi > 0) {
        const t0 = actx.currentTime;
        // v2.124: ENTRADA CON FUNDIDO — ancla explícita (BSO) o no (valle)
        if (o.ancla !== false) gain.gain.setValueAtTime(0.0001, t0);
        else gain.gain.value = 0.0001;
        gain.gain.linearRampToValueAtTime(v, t0 + fi);
        if (o.ancla !== false) rampHasta = t0 + fi;
      } else {
        gain.gain.value = v;
      }
      gain.connect(actx.destination);
      const src = actx.createBufferSource();
      src.buffer = buf;
      src.loop = true;
      src.connect(gain);
      src.start();
      mus = { gain, src };
    } catch (e) { mus = null; }
  }

  /* Encender: la secuencia musicOn() de la casa (wanted + cargar/arrancar). */
  function on() {
    try {
      const actx = ctx();
      if (!actx || actx.state !== 'running') return;
      // v2.124: el contexto murió (re-bind de VR): soltar para revivir
      if (o.renace !== false && mus && mus.src.context !== actx) mus = null;
      wanted = true;
      if (o.gateOn && arcPlaying()) return;      // invariante UNA MELODÍA (valle)
      if (!buf && !busy) cargar(actx);
      else if (buf && !mus) arrancar(actx);
    } catch (e) { /* sin música: nunca rompe */ }
  }

  /* Sincronía EN VIVO con el ajuste global (llamada frame a frame). */
  function sync() {
    try {
      const modo = (o.syncMode == null) ? 'ramp' : o.syncMode;
      const a = (gg() && gg().audio) || null;
      // v2.124: RESURRECCIÓN — contexto cambiado → renacer aquí si toca
      if (o.renace !== false && mus && a && a.ctx && mus.src.context !== a.ctx) {
        mus = null;
        if (wanted && buf && a.ctx.state === 'running' && puede()) {
          arrancar(a.ctx);
          return;
        }
      }
      if (modo === 'none' || !mus || !mus.gain) return;
      const g = mus.gain.gain;
      const eff = objetivo();
      if (modo === 'ramp') {
        // durante el fundido de entrada no se retoca la ganancia (v2.124)
        if (rampHasta && a && a.ctx && a.ctx.currentTime < rampHasta) return;
        if (a && a.ctx && Math.abs((g.value || 0) - eff) > 0.001) {
          const t = a.ctx.currentTime;
          g.cancelScheduledValues(t);
          g.setValueAtTime(Math.max(0.0001, g.value || 0.0001), t);
          g.linearRampToValueAtTime(eff, t + 0.15);
        }
      } else if (modo === 'direct') {
        if (Math.abs((g.value || 0) - eff) > 0.001) g.value = eff;
      }
    } catch (e) { /* nunca rompe el juego */ }
  }

  /* Apagar: instantáneo (BSO/vagón) o con fundido 0,4 s (valle, stop 500 ms). */
  function off() {
    try {
      wanted = false;
      if (!mus) return;
      const sf = o.stopFade || 0;
      if (sf > 0) {
        const s = mus.src, gn = mus.gain;
        const c = s.context;
        gn.gain.cancelScheduledValues(c.currentTime);
        gn.gain.setValueAtTime(gn.gain.value, c.currentTime);
        gn.gain.linearRampToValueAtTime(0.0001, c.currentTime + sf);
        window.setTimeout(() => { try { s.stop(); } catch (e) { /* */ } }, 500);
      } else {
        try { mus.src.stop(); } catch (e) { /* */ }
        try { mus.gain.disconnect(); } catch (e) { /* */ }
      }
    } catch (e) { /* */ }
    mus = null;
  }

  function sonando() { return !!mus; }                  // para QA/diagnóstico
  function estado() {
    return { sonando: !!mus, querido: wanted, cargado: !!buf, cargando: busy };
  }

  return { on, off, sync, sonando, estado };
}

export default { SDK_VERSION, getCore, assetURL, congela, descongela, createSfx, createMusic };
