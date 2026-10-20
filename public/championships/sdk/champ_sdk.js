/* ============================================================================
 *  CRAZY PING PONG · SDK DE CAMPEONATOS (champ_sdk.js) — v1.5.0
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
 *  v1.3.0 (FASE 6): createPowerSign() — el cartel de SUPERPODER («¡Super
 *  Power!!») que los 4 campeonatos con duelos copiaban (Forajido/Wizard/
 *  Arcade/PwSignEO) converge en UNA fábrica con DOS coreografías exactas
 *  («clasica» v2.120 de oeste/magia y «v240» de locura/orbital, con su
 *  halo que respira) y knobs por módulo (arte, respaldo, ownTex, dims).
 *  v1.4.0 (FASE 7 · CIERRE DEL SDK v1.x): createRival() — el STANDEE del
 *  rival (la silueta-cartón con sus estados de cara) que orbital y Valle
 *  Neón duplicaban — con DOS motores exactos («perezoso» del orbital:
 *  cambia la IMAGEN de la misma textura con guard anti-recarga; «precarga»
 *  de Valle: swap de mapas precargados con caída a la cara base) — y
 *  createCartel() — el tablero de etapa (canvas → textura → plano →
 *  redibujable) cuya fontanería repetían ambos. Además el orbital entrega
 *  SU ÚLTIMO motor de audio propio (el decodeAudioData de arsenal de su
 *  bso.wav) a createMusic, y la migración destapa un bug familiar: el
 *  standee de Valle Neón cargaba «rival.webp / <estado>.webp» que NUNCA
 *  existieron (los assets reales son .png) — llevaba pintada la silueta
 *  gris de reserva desde su v1. Ahora carga el arte ZETA-7 real.
 *  v1.5.0 (FASE 8 · SONIDO DEL TREN DEL OESTE): createBucle() — motor de
 *  BUCLE con control POR INSTANCIA, lo que createMusic no puede dar (una
 *  sola ranura, sin desfase, sin volumen vivo): on(desfase, pan) arranca
 *  el bucle en un punto arbitrario del audio (varios caballos «ligeramente
 *  desfasados»), setVol(v) cambia el volumen EN VIVO frame a frame
 *  (desvanecer por distancia, mute del arcade respetado) y off(seco)
 *  para con fundido o BRUSCO (el jinete abatido). El reloj de parada es
 *  el del PROPIO AudioContext (src.stop(cuando) + onended → disconnect):
 *  cero setTimeout. Decode en forma promesa (lección v2.125) y nunca
 *  lanza — las mismas reglas de la casa.
 *  v1.5.1 (FASE 9 · EL TREN QUE NO SE OÍA): (a) «ignoraMute» — opción para
 *  createBucle y createSfx: el gate arcMute/_arcDucked es el silencio de la
 *  MÚSICA del arcade (BSO/vagón), no de los SFX — el dueño con la música
 *  del arcade apagada no oía rodadura, galopes, llegadas ni túneles
 *  (ganancia 0,0001) mientras los sonidos sintéticos de la casa (que
 *  nunca consultaron ese interruptor) sí sonaban. Los motores con
 *  ignoraMute:true obedecen SIEMPRE; por defecto (false) el contrato
 *  anterior queda intacto para el resto de campeonatos. (b) createSfx
 *  «primer play mudo» — play() antes de tener el buffer guardaba silencio
 *  para siempre si la pista sólo sonaba una vez; ahora el play queda
 *  PENDIENTE y se auto-dispara al terminar el decode.
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
 *  MIGRACIÓN — FASES 3-7 COMPLETAS (SDK v1.x CERRADO en v3.6.5-SDK5):
 *  SFX (createSfx) · congelados (congela) · puente al núcleo (getCore) ·
 *  MÚSICA en bucle (createMusic: oeste v50, magia v30, locura vía
 *  manifest, valle v3, orbital v16 — el «arsenal» era su bso.wav) ·
 *  CARTEL de superpoder (createPowerSign: oeste v51, magia v31, locura
 *  v22, orbital v15) · STANDEE del rival (createRival: orbital v16,
 *  valle v4) · TABLERO de etapa (createCartel: orbital v16, valle v4).
 *  Ningún campeonato conserva ya un decodeAudioData propio.
 * ===================================================================== */

/* Versión del SDK (QA la verifica por window.__PP_SDK). */
const SDK_VERSION = '1.5.1';

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
export function createSfx(moduleURL, getGame, opts) {
  const O = opts || {};               // v1.5.1: { ignoraMute }
  const bufs = Object.create(null);   // nombre → AudioBuffer decodificado
  const busy = Object.create(null);   // nombre → petición en vuelo
  const pend = Object.create(null);   // v1.5.1: nombre → play pendiente

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
      .then((buf) => {
        bufs[name] = buf; busy[name] = false;
        /* v1.5.1: un play() que llegó antes del buffer suena AHORA. */
        const p = pend[name];
        if (p) { delete pend[name]; play(name, p.vol, p.opts); }
      })
      .catch(() => { busy[name] = false; delete pend[name]; });
  }

  function play(name, vol, opts) {
    try {
      const g = (typeof getGame === 'function') ? getGame() : getGame;
      const actx = g && g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      pedir(name);
      const buf = bufs[name];
      if (!buf) {                       // v1.5.1: pendiente, no silencio eterno
        pend[name] = { vol, opts };
        return;
      }
      const src = actx.createBufferSource();
      src.buffer = buf;
      const gn = actx.createGain();
      const A = g.audio;
      /* v1.5.1: el mute del arcade es de MÚSICA — ignoraMute lo pasa. */
      const silencio = !O.ignoraMute && A && (A.arcMute || A._arcDucked);
      gn.gain.value = silencio ? 0.0001 : (vol == null ? 0.65 : vol);
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

/* — MOTOR DE BUCLE CON CONTROL POR INSTANCIA (createBucle · v1.5.0) ————
 *  Lo que createMusic NO puede dar: bucles que conviven (uno por jinete),
 *  que arrancan DESFASADOS (varios caballos no galopan al compás), cuyo
 *  volumen cambia EN VIVO (el jinete se aleja y el galope se desvanece)
 *  y que callan BRUSCAMENTE (el jinete abatido). Un motor por instancia.
 *
 *  Uso desde un campeonato:
 *      import { createBucle } from '../sdk/champ_sdk.js';
 *      const b = createBucle(() => this.game, {
 *        url: () => assetURL(import.meta.url, 'tren/caballos.mp3'),
 *        vol: () => 0.5,                 // volumen base (mute lo aplica el motor)
 *        fadeIn: 0.3, stopFade: 0.45,
 *      });
 *      b.on(1.7, -0.55);   // arranque a 1,7 s del audio · paneo izquierda
 *      b.setVol(0.12);     // volumen vivo (frame a frame: distancia)
 *      b.off(true);        // SECO (muerte) · b.off() con fundido (alejarse)
 *
 *  opts: url () => string — fuente del bucle (assets del módulo)
 *        vol () => number — volumen objetivo (consultado al arrancar)
 *        fadeIn s (0,35)  — fundido de entrada
 *        stopFade s (0,45) — fundido de off() sin «seco»
 *  Devuelve { on, off, setVol, suena, estado }. El mute del arcade
 *  (arcMute/_arcDucked) se respeta en el arranque Y en cada setVol.
 *  ====================================================================== */

export function createBucle(getGame, opts) {
  const o = opts || {};
  let buf = null;        // AudioBuffer decodificado (una sola vez)
  let busy = false;      // petición en vuelo
  let wanted = false;    // on() pidió antes de tener el buffer
  let inst = null;       // { gain, src, pan } — LA instancia viva

  function gg() { return (typeof getGame === 'function') ? getGame() : getGame; }
  function ctx() {
    try { const a = gg() && gg().audio; return a && a.ctx; } catch (e) { return null; }
  }
  function objetivo() {
    try {
      const A = gg() && gg().audio;
      const v = o.vol ? o.vol() : 0.5;
      /* v1.5.1: ignoraMute — el gate es de MÚSICA, no de SFX/ambiente. */
      if (!o.ignoraMute && A && (A.arcMute || A._arcDucked)) return 0.0001;
      return Math.max(0.0001, Math.min(1, v));
    } catch (e) { return 0.0001; }
  }
  function srcURL() { try { return o.url ? o.url() : undefined; } catch (e) { return undefined; } }

  /* Carga UNA vez (lección v2.125: forma promesa). */
  function cargar(actx) {
    const u = srcURL();
    if (!u || busy || buf) return;
    busy = true;
    fetch(u)
      .then((r) => r.arrayBuffer())
      .then((ab) => new Promise((res, rej) => {
        try { res(actx.decodeAudioData(ab.slice(0))); } catch (e) { rej(e); }
      }))
      .then((b) => { buf = b; busy = false; if (wanted) arrancar(actx, 0, 0); })
      .catch(() => { busy = false; });
  }

  function arrancar(actx, desfase, panv) {
    try {
      if (inst || !buf) return;
      const gain = actx.createGain();
      const fi = (o.fadeIn == null) ? 0.35 : o.fadeIn;
      const t0 = actx.currentTime;
      gain.gain.setValueAtTime(0.0001, t0);
      gain.gain.linearRampToValueAtTime(objetivo(), t0 + fi);
      let nodo = gain;
      let pan = null;
      if (panv && actx.createStereoPanner) {
        try {
          pan = actx.createStereoPanner();
          pan.pan.value = Math.max(-1, Math.min(1, panv));
          gain.connect(pan);
          nodo = pan;
        } catch (e) { pan = null; nodo = gain; }
      }
      nodo.connect(actx.destination);
      const src = actx.createBufferSource();
      src.buffer = buf;
      src.loop = true;
      src.connect(gain);
      src.start(t0, desfase > 0 ? (desfase % buf.duration) : 0); // DESFASE
      inst = { gain, src, pan };
    } catch (e) { inst = null; }
  }

  /* Arrancar el bucle: on(desfaseSegundos, panN1a1) — ambos opcionales. */
  function on(desfase, panv) {
    try {
      const actx = ctx();
      if (!actx || actx.state !== 'running') return;
      // contexto muerto (re-bind de VR): soltar la instancia vieja
      if (inst && inst.src.context !== actx) inst = null;
      wanted = true;
      if (!buf && !busy) cargar(actx);
      else if (buf && !inst) arrancar(actx, desfase || 0, panv || 0);
    } catch (e) { /* nunca rompe */ }
  }

  /* Volumen EN VIVO (desvanecer por distancia · mute del arcade). */
  function setVol(v) {
    try {
      if (!inst) return;
      const A = gg() && gg().audio;
      const eff = (A && (A.arcMute || A._arcDucked))
        ? 0.0001 : Math.max(0.0001, Math.min(1, v));
      inst.gain.gain.value = eff;
    } catch (e) { /* */ }
  }

  /* Parar: off(true) SECO (jinete abatido) · off() con fundido (se aleja).
   * El reloj es el del AudioContext: sin setTimeout, desconecta onended. */
  function off(seco) {
    let moribundo = null;
    try {
      wanted = false;
      if (!inst) return;
      const s = inst.src, gn = inst.gain, c = s.context;
      const sf = seco ? 0 : (o.stopFade == null ? 0.45 : o.stopFade);
      if (sf > 0) {
        gn.gain.cancelScheduledValues(c.currentTime);
        gn.gain.setValueAtTime(Math.max(0.0001, gn.gain.value || 0.0001), c.currentTime);
        gn.gain.linearRampToValueAtTime(0.0001, c.currentTime + sf);
        s.stop(c.currentTime + sf + 0.05);
        moribundo = { gn, pan: inst.pan };
        s.onended = () => {
          try { gn.disconnect(); } catch (e) { /* */ }
          try { if (moribundo.pan) moribundo.pan.disconnect(); } catch (e) { /* */ }
        };
      } else {
        try { s.stop(); } catch (e) { /* */ }
        try { gn.disconnect(); } catch (e) { /* */ }
        try { if (inst.pan) inst.pan.disconnect(); } catch (e) { /* */ }
      }
    } catch (e) { /* */ }
    inst = null;
  }

  function suena() { return !!inst; }                   // para QA/diagnóstico
  function estado() {
    return { sonando: !!inst, querido: wanted, cargado: !!buf, cargando: busy };
  }

  return { on, off, setVol, suena, estado };
}

/* — CARTEL DE SUPERPODER (createPowerSign · v1.3.0 · FASE 6) ——————————
 *  El tablón «¡Super Power!!» que los 4 campeonatos con duelos copiaban
 *  (ForajidoPowerSign oeste · WizardPowerSign magia · ArcadePowerSign
 *  locura · PwSignEO orbital) converge en UNA fábrica con DOS coreografías
 *  EXACTAS y knobs por módulo. Conducta idéntica por variante:
 *    · «clasica» (v2.120 — oeste y magia, verbatim): entrada por la
 *      izquierda (1,4 m, rot 0,22, easeOutCubic) → parada con vaivén
 *      (sin 5.2/3.4/4.1) → salida por la derecha (1,5·e², rot −0,24,
 *      fundido 1−e). Sin escala, sin halo.
 *    · «v240» (locura + orbital, verbatim): entrada con escala 0,92→1 y
 *      opacidad t/0,12 → vaivén (sin 6.4/5.1/8.2) → salida easeInCubic
 *      con recorte de opacidad en k>0,72 + HALO DE CONTORNO que respira
 *      (0,78±0,22 @9 Hz, salto 0,4 en la entrada, apagón final 0,12 s).
 *  El anclado a la RED (netTopY+0,14 · tableCenterZ+0,30 · mira al
 *  jugador girando en XZ — v2.88) y el icono circular del poder
 *  anunciado (v2.120, cache perezosa) son COMUNES a las 4.
 *
 *  Uso desde un campeonato (la clase del módulo queda en un delegador):
 *      this._impl = createPowerSign(THREE, () => this.game, {
 *        coreo: 'clasica' | 'v240',
 *        arte: 'plano' | 'canvas1024' | 'fit1833',
 *        url: () => urlDelArte,
 *        fallbackURL: () => dataURL,        // sólo magia (canvas1024)
 *        pintar: (aplicar) => void,         // sólo oeste (respaldo pintado)
 *        dims: () => ({ netTopY, tableCenterZ }),
 *        onTex: (tex) => void,              // sólo orbital (ownTex)
 *      });
 *
 *  opts (los por defecto = clasica sin halo):
 *    coreo       'clasica'|'v240'  — coreografía del tablón
 *    arte        'plano'|'canvas1024'|'fit1833' — cómo se aplica el arte
 *    url         () => string      — arte del cartel (superpoder.webp/png)
 *    fallbackURL () => string      — arte de respaldo como imagen (magia)
 *    pintar      (aplicar) => void — respaldo pintado por el módulo (oeste)
 *    dims        () => D|null      — dimensiones del núcleo (netTopY/tableCenterZ)
 *    onTex       (tex) => void     — registro de texturas propias (orbital)
 *  THREE se pasa como PRIMER parámetro a propósito: el SDK sigue sin
 *  dependencias (el campeonato ya lo importa). */
export function createPowerSign(THREE, getGame, opts) {
  const o = opts || {};
  const V240 = o.coreo === 'v240';
  const HALO = !!o.halo;
  const ARTE = o.arte || 'plano';
  const T_IN = 0.40, T_HOLD = 1.45, T_OUT = 1.90;
  let group = null, pivot = null, mat = null, plane = null;
  let haloMat = null, halo = null, iconPlane = null;
  let inited = false;
  let t = -1;                                  // -1 = oculto
  const iconCache = new Map();

  function gg() { return (typeof getGame === 'function') ? getGame() : getGame; }
  function dims() { try { return o.dims ? o.dims() : null; } catch (e) { return null; } }

  /* v2.40: HALO DE CONTORNO — la silueta REAL del arte (su canal alfa)
   * estampada con sombra difusa dorada + halo ámbar exterior, en aditivo. */
  function construirHalo() {
    haloMat = new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, depthTest: false,
      blending: THREE.AdditiveBlending, opacity: 0,
    });
    haloMat.renderOrder = 48;
    halo = new THREE.Mesh(new THREE.PlaneGeometry(0.92, 0.502), haloMat);
    halo.renderOrder = 48;
    halo.scale.setScalar(1.2);
    pivot.add(halo);
  }
  function haloDesde(src, w, h) {
    try {
      const mk = (blur, color) => {
        const cv = document.createElement('canvas');
        cv.width = w; cv.height = h;
        const c = cv.getContext('2d');
        c.shadowColor = color;
        c.shadowBlur = blur;
        c.shadowOffsetX = 0;
        c.shadowOffsetY = 0;
        for (let i = 0; i < 3; i++) c.drawImage(src, 0, 0, w, h);
        return cv;
      };
      const wide = mk(Math.max(14, Math.round(h * 0.16)), 'rgba(255,150,40,0.85)');
      const core = mk(Math.max(8, Math.round(h * 0.07)), 'rgba(255,214,110,0.95)');
      const c2 = core.getContext('2d');
      c2.globalCompositeOperation = 'lighter';
      c2.drawImage(wide, 0, 0);
      const tex = new THREE.CanvasTexture(core);
      tex.colorSpace = THREE.SRGBColorSpace;
      haloMat.map = tex;
      haloMat.needsUpdate = true;
      if (o.onTex) { try { o.onTex(tex); } catch (e) { /* */ } }
    } catch (e) { console.warn('[powerSign.halo]', e); }
  }

  /* Respaldo BUILTIN «SUPER POWER!!» (el pintor de locura, adoptado por el
   * orbital — idéntico, con guard de roundRect por cortesía del orbital). */
  function pintorSuperPower() {
    const cv = document.createElement('canvas');
    cv.width = 1024; cv.height = 512;
    const g = cv.getContext('2d');
    g.fillStyle = 'rgba(10,16,38,0.85)';
    g.beginPath();
    if (g.roundRect) g.roundRect(24, 24, 976, 464, 56); else g.rect(24, 24, 976, 464);
    g.fill();
    g.lineWidth = 14;
    g.strokeStyle = '#e8b45a';
    g.stroke();
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    g.shadowColor = '#ffd257';
    g.shadowBlur = 34;
    g.fillStyle = '#ffd257';
    g.font = '900 190px system-ui, sans-serif';
    g.fillText('SUPER', 512, 190);
    g.fillStyle = '#bfe3ff';
    g.font = '900 170px system-ui, sans-serif';
    g.fillText('POWER!!', 512, 380);
    return cv;
  }

  function build() {
    if (inited) return;
    inited = true;
    group = new THREE.Group();     // ancla a la RED (posición/rotación)
    pivot = new THREE.Group();     // coreografía local del cartel
    group.add(pivot);
    mat = new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, depthTest: false, opacity: 0,
    });
    mat.renderOrder = 49;
    plane = new THREE.Mesh(new THREE.PlaneGeometry(0.92, 0.502), mat);
    plane.renderOrder = 49;
    pivot.add(plane);
    if (HALO) construirHalo();
    group.visible = false;
    // v2.88: bajo el RIG (con la mesa) — anclado a la RED, no a la cabeza
    const g = gg();
    if (g && g.rig) g.rig.add(group);
    cargarArte();
  }

  function cargarArte() {
    try {
      const url = o.url ? o.url() : '';
      if (ARTE === 'canvas1024') {
        /* magia: el arte se re-renderiza a un canvas de 1024 de ancho y el
         * plano se reescala al aspecto real (0,92·H/W sobre 0,502). */
        const apply = (img) => {
          if (!mat) return;
          const ar = img.width / Math.max(1, img.height);
          const W = 1024, H = Math.max(64, Math.round(1024 / Math.max(0.5, ar)));
          const cv = document.createElement('canvas');
          cv.width = W; cv.height = H;
          const c = cv.getContext('2d');
          if (c) {
            c.clearRect(0, 0, W, H);
            c.drawImage(img, 0, 0, W, H);
          }
          const tex = new THREE.CanvasTexture(cv);
          tex.colorSpace = THREE.SRGBColorSpace;
          mat.map = tex;
          mat.needsUpdate = true;
          plane.scale.set(1, (0.92 * H / W) / 0.502, 1);
        };
        const img = new Image();
        img.onload = () => apply(img);
        img.onerror = () => {
          const fb = new Image();
          fb.onload = () => apply(fb);
          fb.src = o.fallbackURL ? o.fallbackURL() : '';
        };
        img.src = url || (o.fallbackURL ? o.fallbackURL() : '');
      } else {
        /* plano (oeste: textura directa sin reescala) y fit1833 (locura +
         * orbital: alto acorde al aspecto real 1408×768 → 1,833 + halo). */
        const img = new Image();
        img.onload = () => {
          const tex = new THREE.Texture();
          tex.colorSpace = THREE.SRGBColorSpace;
          tex.image = img;
          tex.needsUpdate = true;
          if (ARTE === 'fit1833') {
            const ar = img.width / Math.max(1, img.height);
            const fit = Math.min(1, 1.833 / Math.max(0.5, ar));
            plane.scale.set(1, fit, 1);
            if (HALO) halo.scale.set(1.2, 1.2 * fit, 1);
            haloDesde(img, 512, Math.max(64, Math.round(512 / Math.max(0.5, ar))));
          }
          mat.map = tex;
          mat.needsUpdate = true;
          if (o.onTex) { try { o.onTex(tex); } catch (e) { /* */ } }
        };
        img.onerror = () => {
          if (ARTE === 'fit1833') {
            const cv = pintorSuperPower();
            const tex = new THREE.CanvasTexture(cv);
            tex.colorSpace = THREE.SRGBColorSpace;
            mat.map = tex;
            mat.needsUpdate = true;
            haloDesde(cv, 512, 256);
            if (o.onTex) { try { o.onTex(tex); } catch (e) { /* */ } }
          } else if (o.pintar) {
            o.pintar((tex2) => {
              mat.map = tex2;
              mat.needsUpdate = true;
            });
          }
        };
        img.src = url;
      }
    } catch (e) {
      if (ARTE !== 'canvas1024' && o.pintar) {
        try { o.pintar((tex2) => { mat.map = tex2; mat.needsUpdate = true; }); } catch (e2) { /* */ }
      }
    }
  }

  /* v2.88: ANCLADO A LA RED — centro del cartel a la altura de la red
   * (netTopY + 0,14), 30 cm del lado del jugador; gira en XZ para mirar
   * al jugador. IGUAL en los cuatro (petición del artista). */
  function anclado() {
    const g = gg();
    const D = dims();
    if (!D || !group) return;
    group.position.set(0, D.netTopY + 0.14, D.tableCenterZ + 0.30);
    try {
      const c = g && g.camera;
      if (c) {
        const dx = c.position.x - group.position.x;
        const dz = c.position.z - group.position.z;
        if (Math.abs(dx) > 1e-4 || Math.abs(dz) > 1e-4) {
          group.rotation.y = Math.atan2(dx, dz);
        }
      }
    } catch (e) { /* se queda mirando al lado del jugador (+Z) */ }
  }

  /* v2.120 · show(iconUrl): muestra el cartel + el ICONO del poder. */
  function show(iconUrl) {
    if (!inited) build();
    t = 0;
    group.visible = true;
    iconShow(iconUrl);
    if (V240) {
      // v2.40: parte del lado IZQUIERDO, sin arte visible aún
      if (pivot) {
        pivot.position.set(-1.15, 0, 0);
        pivot.rotation.z = 0;
        pivot.scale.setScalar(0.92);
      }
      mat.opacity = 0;
      haloMat.opacity = 0;
    } else {
      anclado();
    }
  }

  /* Icono circular bajo el cartel (textura perezosa en caché, v2.120). */
  function iconShow(iconUrl) {
    if (!iconUrl) {
      if (iconPlane) iconPlane.visible = false;
      return;
    }
    if (!iconPlane) {
      iconPlane = new THREE.Mesh(
        new THREE.PlaneGeometry(0.30, 0.30),
        new THREE.MeshBasicMaterial({
          transparent: true, depthWrite: false, depthTest: false,
          opacity: 0,
        }));
      // v2.120: el renderOrder va en el OBJETO (el del material se ignora
      // en el orden transparente) — si no, el tablón lo tapaba
      iconPlane.renderOrder = 51;
      iconPlane.position.set(0.30, -0.16, 0.012);
      pivot.add(iconPlane);
    }
    const imat = iconPlane.material;
    let tex = iconCache.get(iconUrl);
    if (!tex) {
      tex = new THREE.TextureLoader().load(iconUrl, () => {
        if (imat) imat.needsUpdate = true;
      }, undefined, () => { /* sin icono: oculto */ });
      tex.colorSpace = THREE.SRGBColorSpace;
      iconCache.set(iconUrl, tex);
    }
    imat.map = tex;
    imat.opacity = 1;
    imat.needsUpdate = true;
    iconPlane.visible = true;
  }

  function hide() {
    if (V240) {
      t = -1;
      if (group) group.visible = false;
      if (iconPlane) iconPlane.visible = false;
    } else {
      if (group) group.visible = false;
      if (iconPlane) iconPlane.visible = false;
      t = -1;
      if (mat) mat.opacity = 0;
    }
  }

  function update(dt) {
    if (V240) {
      if (t < 0 || !group || !group.visible) return;
      t += dt;
      // v2.120: el icono acompaña SIEMPRE al fundido del cartel
      if (iconPlane && iconPlane.visible) {
        iconPlane.material.opacity = mat.opacity;
      }
      anclado();
      // v2.40 · COREOGRAFÍA: entrada rápida desde la IZQUIERDA → parada con
      // leve vaivén y halo que respira → salida rápida por la DERECHA.
      const X = 1.15;                  // media anchura del recorrido lateral (m)
      if (t < T_IN) {
        const k = t / T_IN;
        const e = 1 - Math.pow(1 - k, 3);          // easeOutCubic
        pivot.position.x = -X * (1 - e);
        pivot.rotation.z = (1 - e) * 0.1;
        pivot.scale.setScalar(0.92 + 0.08 * e);
        mat.opacity = Math.min(1, t / 0.12);
      } else if (t < T_HOLD) {
        pivot.position.x = Math.sin(t * 6.4) * 0.012;
        pivot.rotation.z = Math.sin(t * 5.1) * 0.035;
        pivot.scale.setScalar(1 + Math.sin(t * 8.2) * 0.022);
        mat.opacity = 1;
      } else if (t < T_OUT) {
        const k = (t - T_HOLD) / (T_OUT - T_HOLD);
        const e = k * k * k;                       // easeInCubic
        pivot.position.x = X * e;
        pivot.rotation.z = -0.06 * e;
        pivot.scale.setScalar(1);
        mat.opacity = k > 0.72 ? Math.max(0, 1 - (k - 0.72) / 0.28) : 1;
      } else {
        hide();
        return;
      }
      // halo de contorno: entra con el cartel y respira mientras está parado
      const breathe = 0.78 + Math.sin(t * 9.0) * 0.22;
      haloMat.opacity = mat.opacity * (t < T_IN ? 0.4 : breathe) * 0.9;
      if (t >= T_OUT - 0.12) {
        haloMat.opacity *= Math.max(0, (T_OUT - t) / 0.12);
      }
    } else {
      if (t < 0 || !group.visible) return;
      t += dt;
      anclado();
      const P = pivot;
      // v2.120: el icono acompaña SIEMPRE al fundido del tablón
      if (iconPlane && iconPlane.visible) {
        iconPlane.material.opacity = mat.opacity;
      }
      if (t <= T_IN) {
        const k = 1 - Math.pow(1 - t / T_IN, 3);
        P.position.set(-1.4 * (1 - k), 0, 0);
        P.rotation.z = 0.22 * (1 - k);
        mat.opacity = k;
      } else if (t <= T_HOLD) {
        const k = (t - T_IN) / (T_HOLD - T_IN);
        P.position.set(Math.sin(k * 5.2) * 0.055, Math.sin(k * 3.4) * 0.03, 0);
        P.rotation.z = Math.sin(k * 4.1) * 0.03;
        mat.opacity = 1;
      } else if (t <= T_OUT) {
        const k = (t - T_HOLD) / (T_OUT - T_HOLD);
        const e = k * k;
        P.position.set(1.5 * e, 0, 0);
        P.rotation.z = -0.24 * e;
        mat.opacity = 1 - e;
      } else {
        group.visible = false;
        t = -1;
        mat.opacity = 0;
      }
    }
  }

  /* Dispose completo (regla Quest: nada queda colgado al salir — el
   * orbital lo llevaba; ahora lo tienen los cuatro). */
  function dispose() {
    try { if (group && group.parent) group.parent.remove(group); } catch (e) { /* */ }
    for (const tt of iconCache.values()) { try { tt.dispose(); } catch (e) { /* */ } }
    iconCache.clear();
    group = null; pivot = null; plane = null; halo = null;
    iconPlane = null;
    inited = false; t = -1;
  }

  return {
    build, show, hide, update, dispose, T_IN, T_HOLD, T_OUT,
    // acceso de solo lectura al grupo (QA/depuración: ctrl.pwSign.group.visible)
    get group() { return group; },
  };
}

/* — STANDEE DEL RIVAL (createRival · v1.4.0 · FASE 7) ———————————————————
 *  La silueta-cartón del rival con sus CARAS (estados) que el orbital y
 *  Valle Neón escribieron por separado, unificada con DOS motores exactos
 *  (conducta idéntica por variante):
 *    · «perezoso» (orbital v3.2.1): UNA sola textura viva; rivalEstado()
 *      cambia su .image con un Image() nuevo por estado y GUARD
 *      anti-recarga (si el estado no cambia NO recarga — reasignar el
 *      mismo webp 60 veces/s no es gratis en Quest). Estado inexistente:
 *      la cara actual se queda (el onload jamás llega).
 *    · «precarga» (valle v1): TODAS las caras se precargan al construir
 *      (base primero, luego los estados); cada llegada ajusta el mapa y
 *      la ESCALA por aspecto real (asp/0,5). rivalEstado() hace swap de
 *      mapa con caída a la cara base. Estado inexistente: cara base.
 *
 *  Uso desde un campeonato:
 *      this._rivalSDK = createRival(THREE, () => this.game, { ... });
 *      this.group.add(this._rivalSDK.node);   // node = grupo o malla
 *      this._rivalSDK.rivalEstado('duelo');
 *
 *  opts (ninguno obligatorio salvo resuelve para tener arte):
 *    modo        'perezoso'|'precarga' (defecto 'perezoso')
 *    base        'rival.webp'          — cara base (cartón de la sala)
 *    estados     ['idle',…]            — caras precargables (precarga)
 *    resuelve    (f) => url            — resuelve el fichero de cara
 *    alto        2.15                  — altura del plano (m)
 *    anchoFijo   alto*0.5              — ancho si aspecto:false
 *    aspecto     bool (false)          — precarga: escala.x = asp/0,5
 *    material    'basic'|'standard'    — Basic (orbital) / Standard (valle)
 *    matParams   {}                    — color/roughness extra del material
 *    alphaTest   0.25                  — recorte de alfa
 *    depthWrite  false
 *    renderOrder 0                     — sólo orbital lo fijaba (6)
 *    castShadow  false                 — sólo valle lo fijaba (true)
 *    grupo       bool (false)          — true = envoltorio Group con
 *                                      pos/rotY propio (valle); false =
 *                                      la malla se posiciona directa
 *                                      (orbital — el poder de meteoritos
 *                                      teletransporta rivalMesh a pelo)
 *    pos         [x,y,z]               — posición del node (grupo) o malla
 *    meshY       alto/2                — Y local de la malla dentro del grupo
 *    rotY        0                     — giro del grupo (valle: mira a mesa)
 *    onTex       (tex) => void         — registro en _ownTex del módulo
 *    onEstado    (st) => void          — eco del estado (QA lee el eco del
 *                                      orbital this._rivalEstado) */
export function createRival(THREE, getGame, opts) {
  const o = opts || {};
  const PRE = o.modo === 'precarga';
  const ALTO = o.alto || 2.15;
  const ANCHO = o.anchoFijo || ALTO * 0.5;
  const EXT = o.ext || 'webp';   // extensión de las caras por estado
  let tex = null;                // LA textura viva (sólo perezoso)
  const stTex = {};              // caras precargadas (sólo precarga; la base
                                 // NUNCA se guarda aquí — igual que valle)
  let mesh = null, group = null, mat = null;
  let estado_ = '';

  function resuelve(f) { try { return o.resuelve ? o.resuelve(f) : f; } catch (e) { return f; } }
  function eco(st) { if (o.onEstado) { try { o.onEstado(st); } catch (e) { /* */ } } }
  function registrar(t) { if (o.onTex) { try { o.onTex(t); } catch (e) { /* */ } } }

  function construir() {
    mat = (o.material === 'standard')
      ? new THREE.MeshStandardMaterial(Object.assign({
          color: 0xbfc9d6, transparent: true,
          alphaTest: (o.alphaTest == null) ? 0.05 : o.alphaTest, roughness: 0.9,
        }, o.matParams || {}))
      : new THREE.MeshBasicMaterial(Object.assign({
          transparent: true,
          alphaTest: (o.alphaTest == null) ? 0.25 : o.alphaTest,
          depthWrite: (o.depthWrite == null) ? false : !!o.depthWrite,
        }, o.matParams || {}));
    mesh = new THREE.Mesh(new THREE.PlaneGeometry(ANCHO, ALTO), mat);
    mesh.castShadow = !!o.castShadow;
    if (o.renderOrder) mesh.renderOrder = o.renderOrder;
    if (o.grupo) {
      group = new THREE.Group();
      mesh.position.y = (o.meshY == null) ? ALTO / 2 : o.meshY;
      group.add(mesh);
      const p = o.pos || [0, 0, 0];
      group.position.set(p[0], p[1], p[2]);
      group.rotation.y = o.rotY || 0;
    } else {
      const p = o.pos || [0, 0, 0];
      mesh.position.set(p[0], p[1], p[2]);
    }
  }

  /* Corazón común de las caras: pintar una textura en el material. */
  function ponMapa(t) {
    if (t && mat) { mat.map = t; mat.needsUpdate = true; }
  }

  /* Escala por aspecto real de la cara llegada (sólo valle la pedía). */
  function escalaAspecto(t) {
    if (!o.aspecto) return;
    try {
      const asp = (t.image && t.image.width) ? t.image.width / t.image.height : 0.5;
      mesh.scale.set(asp / 0.5, 1, 1);
    } catch (e) { /* escala por defecto */ }
  }

  /* «perezoso»: la cara llega por Image() sobre LA MISMA textura. */
  function estadoPerezoso(st) {
    try {
      const img = new Image();
      img.onload = () => { if (tex) { tex.image = img; tex.needsUpdate = true; } };
      img.src = resuelve(st + '.' + EXT);
    } catch (e) { estado_ = ''; eco(''); }
  }

  /* «precarga»: swap entre caras ya en memoria (caída a la base — que en
   * la casa era SIEMPRE null: estado desconocido = no-op, igual queda). */
  function estadoPrecarga(st) {
    ponMapa(stTex[st] || stTex.base || null);
  }

  function build() {
    if (mesh) return;
    construir();
    if (PRE) {
      // base primero (orden del original: rival.webp → estados); su llegada
      // pinta el mapa PERO no entra en stTex (key null en el original)
      new THREE.TextureLoader().load(resuelve(o.base || ('rival.' + EXT)), (t) => {
        t.colorSpace = THREE.SRGBColorSpace;
        registrar(t);
        ponMapa(t);
        escalaAspecto(t);
      }, undefined, () => { /* sin arte: silueta */ });
      (o.estados || []).forEach((st) => {
        new THREE.TextureLoader().load(resuelve(st + '.' + EXT), (t) => {
          t.colorSpace = THREE.SRGBColorSpace;
          registrar(t);
          stTex[st] = t;
          ponMapa(t);
          escalaAspecto(t);
        }, undefined, () => { /* cara ausente: silueta */ });
      });
    } else {
      // perezoso (orbital): textura viva SIN callback — colorSpace y registro
      // síncronos, exactamente como el original v3.2.1
      tex = new THREE.TextureLoader().load(resuelve(o.base || ('rival.' + EXT)));
      tex.colorSpace = THREE.SRGBColorSpace;
      registrar(tex);
    }
  }

  function rivalEstado(st) {
    if (!mesh) build();
    // v3.2.1 (perezoso): si el estado no cambia NO recarga (decode + subida
    // a GPU). En precarga valle no tenía guard — se conserva así.
    if (!PRE && estado_ === st) return;
    estado_ = st;
    eco(st);
    if (PRE) estadoPrecarga(st);
    else estadoPerezoso(st);
  }

  function dispose() {
    try {
      const n = group || mesh;
      if (n && n.parent) n.parent.remove(n);
    } catch (e) { /* */ }
    if (tex) { try { tex.dispose(); } catch (e) { /* */ } }
    for (const k of Object.keys(stTex)) { try { if (stTex[k]) stTex[k].dispose(); } catch (e) { /* */ } }
    if (mesh) { try { mesh.geometry.dispose(); } catch (e) { /* */ } }
    if (mat) { try { mat.dispose(); } catch (e) { /* */ } }
    tex = null; mesh = null; group = null; mat = null;
    for (const k of Object.keys(stTex)) delete stTex[k];
  }

  build();
  return {
    rivalEstado, dispose,
    node: group || mesh,        // lo que el módulo añade a SU grupo
    mesh, mat,
    estado: () => estado_,      // QA/diagnóstico
    get group() { return group; },
    get tex() { return tex; },
  };
}

/* — TABLERO DE ETAPA (createCartel · v1.4.0 · FASE 7) ———————————————————
 *  La fontanería del cartel de sala/bienvenida que el orbital («cartel de
 *  bienvenida, redibujable por etapa») y Valle Neón («cartel de sala»)
 *  repetían a pelo: canvas → CanvasTexture (SRGB) → plano en la pared →
 *  pintar → needsUpdate. EL ARTE de cada cartel sigue siendo del módulo
 *  (se pasa como pintor); lo COMPARTIDO — el ciclo de vida del lienzo, el
 *  redibujado y el dispose — vive aquí.
 *
 *  Uso desde un campeonato:
 *      this._cartelSDK = createCartel(THREE, () => this.game, { ... });
 *      this.group.add(this._cartelSDK.mesh);
 *      this._cartelSDK.pinta((c, W, H) => { …arte del módulo… });
 *
 *  opts:
 *    cvW, cvH    512, 256          — resolución del lienzo
 *    w, h        1.15, 0.575       — tamaño del plano (m)
 *    pos         [x,y,z]           — posición del plano
 *    rot         [x,y,z]           — rotación (rad)
 *    transparent false             — orbital no lo era; valle sí
 *    depthWrite  false
 *    onTex       (tex) => void     — registro en _ownTex del módulo
 *  pinta(pintor) ejecuta pintor(ctx, W, H) y marca needsUpdate — NUNCA
 *  lanza (el cartel nunca tumba el frame). */
export function createCartel(THREE, getGame, opts) {
  const o = opts || {};
  const CW = o.cvW || 512, CH = o.cvH || 256;
  let cv = null, tex = null, mesh = null;

  function build() {
    if (cv) return;
    cv = document.createElement('canvas');
    cv.width = CW; cv.height = CH;
    tex = new THREE.CanvasTexture(cv);
    tex.colorSpace = THREE.SRGBColorSpace;
    if (o.onTex) { try { o.onTex(tex); } catch (e) { /* */ } }
    mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(o.w || 1.15, o.h || 0.575),
      new THREE.MeshBasicMaterial({
        map: tex,
        transparent: !!o.transparent,
        depthWrite: o.depthWrite == null ? false : !!o.depthWrite,
      }));
    const p = o.pos || [0, 0, 0];
    mesh.position.set(p[0], p[1], p[2]);
    const r = o.rot || [0, 0, 0];
    mesh.rotation.set(r[0], r[1], r[2]);
  }

  function pinta(pintor) {
    try {
      build();
      const c = cv.getContext('2d');
      if (typeof pintor === 'function') pintor(c, CW, CH);
      tex.needsUpdate = true;
    } catch (e) { /* el cartel nunca rompe el frame */ }
  }

  function dispose() {
    try { if (mesh && mesh.parent) mesh.parent.remove(mesh); } catch (e) { /* */ }
    if (tex) { try { tex.dispose(); } catch (e) { /* */ } }
    cv = null; tex = null; mesh = null;
  }

  build();
  return {
    pinta, dispose,
    mesh, tex,
    get cv() { return cv; },
  };
}

export default { SDK_VERSION, getCore, assetURL, congela, descongela, createSfx, createMusic, createBucle, createPowerSign, createRival, createCartel };
