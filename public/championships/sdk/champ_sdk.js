/* ============================================================================
 *  CRAZY PING PONG · SDK DE CAMPEONATOS (champ_sdk.js) — v1.0.0
 * ----------------------------------------------------------------------------
 *  FASE 3 del plan de modularización P0 (acordado con el dueño).
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
 *  MIGRACIÓN (FASE 4, pendiente): oeste (7 copias SFX), magia (2), locura
 *  (motor propio ya correcto), valle_neon. Sala6/Rival/HUD compartidos
 *  llegarán en fases posteriores del SDK (v1.x).
 * ===================================================================== */

/* Versión del SDK (QA la verifica por window.__PP_SDK). */
const SDK_VERSION = '1.0.0';

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
 *      this._sdkSfx.play('risa_astro.mp3');
 *
 *  moduleURL: import.meta.url DEL CAMPEONATO (los assets cuelgan de su
 *  carpeta assets/). getGame: función que devuelve el objeto game del
 *  núcleo (se consulta en cada play — el game puede llegar tarde). */
export function createSfx(moduleURL, getGame) {
  const bufs = Object.create(null);   // nombre → AudioBuffer decodificado
  const busy = Object.create(null);   // nombre → petición en vuelo

  function url(p) { return assetURL(moduleURL, p); }

  function play(name, vol) {
    try {
      const g = (typeof getGame === 'function') ? getGame() : getGame;
      const actx = g && g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      if (!bufs[name] && !busy[name]) {
        busy[name] = true;
        fetch(url(name))
          .then((r) => r.arrayBuffer())
          .then((ab) => actx.decodeAudioData(ab.slice(0)))  // forma promesa (v2.125)
          .then((buf) => { bufs[name] = buf; busy[name] = false; })
          .catch(() => { busy[name] = false; });
      }
      const buf = bufs[name];
      if (!buf) return;                    // aún decodificando: en silencio
      const src = actx.createBufferSource();
      src.buffer = buf;
      const gn = actx.createGain();
      const A = g.audio;
      gn.gain.value = (A && (A.arcMute || A._arcDucked)) ? 0.0001
                                                         : (vol == null ? 0.65 : vol);
      src.connect(gn);
      gn.connect(actx.destination);
      src.start();
    } catch (e) { /* sin SFX: nunca rompe el frame */ }
  }

  function tiene(name) { return !!bufs[name]; }   // para diagnósticos/QA

  return { play, url, tiene };
}

/* — Export por defecto (comodidad para imports cortos) ——————————————— */
export default { SDK_VERSION, getCore, assetURL, congela, descongela, createSfx };
