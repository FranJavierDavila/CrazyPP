/* ============================================================================
 *  NUEVO TRUCO DE MAGIA · rival WIZARD  (championships/magia/index.js)
 * ----------------------------------------------------------------------------
 *  v2.137 (módulo v28) · MAPA NUEVO del dueño (mapa.png 1380×752, mismo
 *  lienzo): nodos NUMERADOS con espiral azul — 1/3/5 magos, 2/4 orbes, el 5
 *  en burbuja sin anillo — y centros algo movidos → nodesPx RE-MEDIDOS
 *  (Hough + bbox dorado + perfil radial; r = 120×banda/107,5 para que el
 *  anillo dorado abrace el borde del arte) y TAPAS con centro/escala
 *  propios (tx/ty/ts) para cubrir anillo + espiral numeradas ENTERAS.
 *  Cero cambios de gameplay.
 *  v2.120 (módulo v23) · AUDITORÍA + DOS SUPERPODERES NUEVOS DEL WIZARD:
 *  BOLA DE FUEGO (tinta brasa + estela aditiva de 16 sprites, 8 s) y NOCHE
 *  ARCANA (el salón se apaga por exposición — nunca a ciegas — y la bola
 *  se vuelve luna arcana con halo que la persigue, 7 s) — bolsa del
 *  Wizard = 4 (bola loca · portales · fuego · sombras) y el cartel enseña
 *  el ICONO (arte nueva). Auditoría: guard anti-NaN en la atracción del
 *  orbe, aviso de prórroga por cruce de umbral, listener pp-lang con
 *  nombre, conteo de bolas sin filter por frame. TODO lo demás intacto.
 *  v2.121 (módulo v24) · MINIATURAS PARA LOS PODERES CLÁSICOS: bola loca y
 *  portales estrenan powerloca.png y powerportal.png — los CUATRO poderes
 *  lucen SU icono propio en el cartel. Cero cambios de gameplay.
 *  v2.73 · AJUSTES DEL ARTISTA (mapa + regalo + estrellas + portales):
 *  (1) MAPA actualizado — el artista rehace el arte oficial (mapa.webp):
 *      los nodos de las PRUEBAS (2 y 4) muestran ahora los ORBES (antes
 *      salían retratos del mago). Círculos en las MISMAS posiciones →
 *      nodesPx / marcadores de progreso intactos.
 *  (2) ESFERA del mago (regalo.webp) ARREGLADA: ya no gira de canto (lo
 *      hacía sobre el eje Y vertical y se le veía de perfil) — ahora gira
 *      SOBRE SÍ MISMA (en su propio plano, rotation.z) y queda SIEMPRE
 *      PERPENDICULAR a la cámara (billboard de guiñada): tapa la parte
 *      baja del mago desde cualquier ángulo. El WIZARD sube ~15 cm en los
 *      duelos (dy −0,38→−0,23) y la esfera lo acompaña (y 0,68→0,83).
 *  (3) ESTRELLAS de la mesa y del corredor ARREGLADAS: el polígono de 5
 *      puntas saltaba cada 144° y zigzagueaba sobre sí mismo (manchas, no
 *      estrellas) — ahora puntas cada 72° + valles a +36° (estrella real)
 *      y halo suave para que titilen como magia. Mismo fix en la textura
 *      del anillo de derrota del WIZARD (starTexture).
 *  (4) portals.webp NUEVO del artista (anillo más grueso, interior brumoso)
 *      en TODOS sus usos: portal del fondo, mini-portales del orbe y los
 *      DOS portales de mesa del superpoder.
 *  (5) PORTALES MÁGICOS (superpoder) MÁS GRANDES y en la PARTE CENTRAL de
 *      la mesa: agujero 0,14→0,19 m · anillo 0,46→0,62 m · offX 0,34→0,18
 *      · offZ 0,52→0,34 (los dos flanqueando la red, casi en el eje). El
 *      glow acompaña la escala nueva.
 *  ----------------------------------------------------------------------------
 *  v2.71 · REGLA FIJA + ESFERA + SUPERPODERES + ORBE FÁCIL + LIMPIEZA:
 *  (1) REGLA FIJA de duelos (cualquier campeonato, siempre): el rival en
 *      persona se coloca ~0,50 m a la DERECHA del borde derecho de la mesa
 *      (DUEL_X = tableHalfWidth + 0,5 ≈ 1,26) — nunca centrado tras ella;
 *      el CLOWN (La Locura) recibe la misma norma desde su manifest.
 *  (2) La ESFERA del mago (regalo.webp) VUELVE en los duelos: tapa su mitad
 *      inferior y GIRA sobre su centro (el «portal pequeño» de la v2.60 con
 *      papel nuevo, como el regalo del CLOWN pero con giro propio).
 *  (3) SUPERPODERES PROPIOS del WIZARD en duelos (v2.72: LOS ORIGINALES,
 *      no los del CLOWN — el mismo motor de dos fases: aviso «SUPERPODER
 *      DE WIZARD!» 2 s con la partida congelada → efecto en pleno rallye):
 *      · BOLA LOCA — la bola se hace MÁS GRANDE, CAMBIA DE COLOR sin
 *        parar (ciclo arcoíris arcano) y navega con movimiento ALGO
 *        ERRÁTICO (vaivén lateral + ráfagas aleatorias).
 *      · PORTALES MÁGICOS — se abren DOS agujeros SOBRE la mesa, uno a
 *        cada lado de la red (anillo portals.webp del artista girando
 *        sobre cada agujero): la bola que bota dentro de un agujero
 *        SALE DISPARADA por el otro. Cooldown 13 s, máx 1 por rallye,
 *        sólo con la bola viniendo hacia el jugador.
 *  (4) Orbe NORMAL de la etapa 2 más SENCILLO: ladrillos 0,125 m y radios
 *      4,6/3,0/1,5 → mismo tamaño y posición pero LA MITAD de ladrillos
 *      (925 → 437, −52,8%) y dianas un 25% más grandes. La variante COMPLEJA
 *      conserva su rejilla histórica (0,088/7/4/2 ≈ 1419, radios fijados).
 *      El centro del orbe se DERIVA del cfg: repone la celda inferior sobre
 *      la mesa con cualquier rejilla (la bola rastrera no pasa por debajo).
 *  (5) SALVAGUARDA de finalización: _playStep termina el nivel en cuanto
 *      aliveBricks llega a 0 (las capas 2 y 3, las interiores, incluidas),
 *      y LIMPIEZA TOTAL entre etapas: stop() oculta ladrillos/núcleo (viven
 *      en el rig), fxGroup (escombros/glow) y retira los haces del láser
 *      del padre CORRECTO (rig desde v2.62 — antes quedaban flotando).
 * ----------------------------------------------------------------------------
 *  v2.65 · BOLA NEGRA-BOMBA + CERO BOTES EN EL SITIO: (1) aleatoriamente un
 *  recambio nace BOLA NEGRA (bombChance, y si llevan bombEvery s sin salir
 *  una sale obligatoria): vuela como una bola más y su PRIMER contacto con
 *  el orbe DETONA una explosión que arranca los ladrillos vivos más próximos
 *  al impacto (hasta blastMax dentro de blastRadius) con lluvia de cubitos,
 *  doble flash, booms y háptica fuerte; la bola se consume y el vórtice trae
 *  otra. (2) NINGUNA bola se queda lejos del jugador para siempre: los botes
 *  casi verticales (mesa y corredor) reciben una patada de deriva hacia el
 *  jugador, y una guardia definitiva (6 s sin alcanzar la zona del jugador)
 *  relanza la bola hacia él. (3) FIX: los
 *  flashes de impacto de v2.63 se llamaban con 4 argumentos y quedaban en
 *  NaN (invisibles) — _flash ahora acepta (x,y,z,escala).
 * ----------------------------------------------------------------------------
 *  v2.64 · ARCO MÍNIMO + MARCADOR ALTO: (1) la bola que VUELVE del orbe ya
 *  NUNCA llega rastrera — la mesa del core (fricción 0.94, restitución 0.88)
 *  encogía los botes hasta dejarla arrastrarse y sin poder golpearla; ahora
 *  CADA bote en mesa o corredor relanza un ARCO mínimo de minBounceHeight
 *  (0.45 m, casi el arco del vórtice) y re-asegura minReturnSpeed; (2) el
 *  marcador de puntos/tiempo se SUBE a y=2.48 para no tapar la cima del orbe
 *  (2.02) — visión completa del orbe.
 * ----------------------------------------------------------------------------
 *  v2.63 · FRENESÍ + POLISH: (1) el WIZARD no aparece en la fase del orbe
 *  (MAGIA.wizardOn=false: sin sprite, sin voces, sin reacciones); (2) FÍSICA
 *  FRENÉTICA — la bola NO pierde velocidad al taladrar (energyLoss 1.0) ni al
 *  rebotar (restitution 1.0), y sale de CUALQUIER impacto con mínimo
 *  minReturnSpeed m/s hacia el jugador: cero paradas, cero bolas muertas;
 *  (3) DOS bolas a la vez, cada una nace de SU vórtice (izq/der); (4) el
 *  cartel SUPERPODER ya no sale (no hay poder especial en esta fase); (5)
 *  FIX de reintento: _startLevel restaura el árbitro/escena/pistola EXACTO
 *  igual que un arranque fresco y el gatillo se autocura si el nivel se
 *  desincroniza — la pistola dispara SIEMPRE tras perder; (6) ladrillos con
 *  BISEL y marco (textura en escala de grises × color de instancia, el
 *  estilo del ARKANOID de La Locura) y destrucción en CUBITOS con gravedad
 *  real y color del ladrillo roto.
 * ----------------------------------------------------------------------------
 *  v2.62 · FIX ESPACIAL: TODOS los objetos del nivel viven en el RIG (los
 *  ladrillos del orbe y las estelas iban a la ESCENA y con el recentrado de
 *  la Quest el orbe aparecía fuera de la mesa, junto al Wizard). El láser
 *  sale ahora de la BOCA del cañón de pistol.glb (offset _gunMuzzle) y el
 *  disparo rompe SOLO ladrillos ROJOS (capa exterior); las capas internas
 *  absorben el disparo — la bola sigue rompiendo cualquier ladrillo. Bote en
 *  espera ×3 (H 0.52 m).
 * ----------------------------------------------------------------------------
 *  v2.60 · MAPA NUEVO (diseño definitivo del artista) — el campeonato ya no
 *  es un clon de La Locura con partidas: es UN NIVEL, el ORBE MÁGICO.
 *
 *  ESCENA
 *    · La mesa pierde la red y se alarga como un CORREDOR hasta la pared del
 *      fondo de la sala; allí GIRA el portal mágico (arte portals.webp) y
 *      delante de él flota el ORBE: una esfera de LADRILLOS de 3 capas
 *      (núcleo amarillo r≤3, medio marrón r≤6, exterior rojo r≤9, ladrillo
 *      de 6 cm) montada en un InstancedMesh (sólo se dibujan los ladrillos
 *      «expuestos», ~1.000 de los ~3.000).
 *    · WIZARD flota junto a su creación con sus 12 pinturas y reacciona
 *      (focused → hungry → panic → crazy según el orbe se desmorona).
 *
 *  MÁQUINA DE ESTADOS
 *    CARGA (cartel + mago) → MONTAJE (los ladrillos vuelan del portal a su
 *    sitio capa a capa, 5–8 s, sin reloj y sin bolas, SALTABLE con el
 *    gatillo) → JUEGO (el reloj corre; las bolas nacen de MINI-PORTALES en
 *    tu mitad, máx. 3, cada una con estela de color; la ATRACCIÓN curva la
 *    bola hacia el orbe SIN cambiar su velocidad) → ALERTA FINAL (t ≤ 30 s:
 *    alarma + bloque RELOJ flotante de 4 s; DISPARO con la pistola de la
 *    mano libre = +60 s, máx. 2 prórrogas) → VICTORIA (orbe a cero) o
 *    DERROTA (tiempo a cero) → RESULTADOS (puntos, 1–3 estrellas por tiempo
 *    restante, ranking y reporte con validación de sanidad) → reintento.
 *
 *  COLISIÓN POR REJILLA (sin física de ladrillos)
 *    · Barrido por SUBPASO (extra() de stepPhysics corre a 480 Hz): muestra
 *      cada medio ladrillo → imposible atravesar el orbe incluso a smash.
 *    · Impacto: si la bola llega RÁPIDA (≥ minChainSpeed) taladra una
 *      CADENA de hasta maxChain ladrillos en la dirección de vuelo (cada
 *      ladrillo cuesta energyLossPerHit de velocidad); si llega LENTA rebota
 *      (restitution). La normal sale del eje que cambió entre celdas.
 *    · ATRACCIÓN (ayuda de dificultad): sólo bolas que se ACERCAN al orbe y
 *      a menos de attractionRange; gira la dirección hacia el ideal
 *      min(ángulo, attractionMaxAngle)·attractionStrength·dt — la VELOCIDAD
 *      no cambia. Último 5% de ladrillos: atracción ×1.5 apuntando al
 *      ladrillo vivo más cercano.
 *
 *  REGLA DE ORO: el núcleo, La Locura y el multijugador NO se tocan. El
 *  módulo recibe window.__PP_CORE (DIMS, stepPhysics, T) y usa los mismos
 *  ganchos de ChampLoader (init/start/leave/update/onPoint/onMatchOver/
 *  aiMul/serveTrigger/reenter/testStep/testActive). Los 19 parámetros del
 *  nivel viven en manifest.json (bloque «level») y se fusionan en caliente.
 *  ============================================================================ */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// v3.6.2-SDK2 · FASE 4 de la modularización P0: kernel compartido de los 5
// campeonatos (championships/sdk/champ_sdk.js) — la risa del mago y el
// congelado del aviso delegan en él (el fix «forma promesa» v2.125 llegó a
// estar copiado 2 veces aquí). Desde el SDK v1.2.0 también la BSO en bucle
// vive en el SDK (createMusic).
import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js';

/* Primitivas del NÚCLEO vía window.__PP_CORE (v2.53). ChampLoader importa
 * este módulo SOLO tras cargar el juego, así que el puente ya está puesto. */
// v3.6.2-SDK2: el puente al núcleo vive en el SDK (getCore) — una sola fuente.
const __CORE = getCore() || {};
const DIMS = __CORE.DIMS;
const stepPhysics = __CORE.stepPhysics;
const T = __CORE.T;

/* v2.108 · MODO DEPURACIÓN («foro3d»): el núcleo publica window.__PP_DEBUG
 * cuando el nombre del jugador es foro3d. Con él, el mapa del camino
 * muestra las 5 ETAPAS y el gatillo salta a cualquiera SIN requisitos de
 * progreso (revisión directa del creador). El núcleo, además, no persiste
 * registros ni publica rankings ni telemetría de este jugador. */
function ppDbg() {
  try { return typeof window !== 'undefined' && !!window.__PP_DEBUG; } catch { return false; }
}

/* ----------------------------- mini-i18n propia ---------------------------- */
let TL = 'es';
const TXT = {
  es: {
    champ: 'NUEVO TRUCO DE MAGIA',
    announce: 'Bienvenido al Nuevo truco de Magia. Vence a WIZARD y destruye sus orbes mágicos.',
    // v2.106 · cartel explicativo de la prueba del ORBE MÁGICO
    instr_orb_t: 'PRUEBA · EL ORBE MÁGICO',
    instr_orb: [
      'Una ESFERA de bloques mágicos flota ante ti: golpéala con la BOLA usando las PALAS para romper sus bloques.',
      'Se rompe por CAPAS: primero la corteza, luego el interior… hasta apagar el NÚCLEO que brilla.',
      'Tendrás tiempo extra y una PISTOLA MÁGICA en la mano libre para rematar los bloques que la bola no alcanza.',
      'En la versión COMPLEJA el orbe gira y se protege más: ¡calcula bien los ángulos!',
    ],
    msg_enter: '¡NUEVO TRUCO DE MAGIA! Destruye el ORBE MÁGICO',
    cartel_new: '¡EL ORBE MÁGICO!',
    cartel_vs: 'Intento {n} · destruye el orbe entero',
    // v2.70 · DUELOS del camino (etapas 1/3/5)
    duel_new: '¡DUELO MÁGICO!',
    duel_vs: 'VS WIZARD · Ronda {n}',
    msg_duel: '¡DUELO vs WIZARD Nv. 1! Partida a 11 puntos',
    wiz2_up: '¡WIZARD Nv. 2 · más difícil!',
    wiz3_up: '¡WIZARD Nv. 3 · JEFE FINAL!',
    rank_title: 'RANKING',
    rank_empty1: 'Aún no hay intentos.',
    rank_empty2: '¡Revienta el orbe para abrir tu palmarés!',
    rank_win: '¡Destruído!',
    rank_lose: 'Resistió',
    rank_tot: 'Victorias: {n} · Mejor: {b}',
    rec_rally: 'Mejor rallye: {n}', rec_streak: 'Mejor racha: {n}', rec_surv: 'Supervivencia: {n}',
    trophy_rank: 'CAMPEÓN DEL TRUCO DE MAGIA',
    trophy_get: '¡¡TROFEO: VARITA DORADA!!',
    montaje_hint: 'Gatillo: saltar el montaje',
    montaje_sub: 'El vórtice está forjando su orbe…',
    play_hint: '¡Rompe el orbe antes de que acabe el tiempo!',
    gun_hint: 'PISTOLA MÁGICA · el gatillo rompe SOLO los ladrillos ROJOS',
    alert_msg: '¡DISPARA AL RELOJ! +{n} s',
    alert_gone: 'El reloj ha desaparecido…',
    no_more_ext: 'No quedan prórrogas',
    ext_get: '¡PRÓRROGA +{n} s!',
    ext_left: 'Prórrogas: {n}',
    last_bricks: '¡El orbe resiste! Atracción MÁGICA al máximo',
    chain_n: 'CADENA ×{n}',
    time_warn: '¡ÚLTIMOS {n} SEGUNDOS!',
    win_title: '¡ORBE MÁGICO DESTRUIDO!',
    win_score: '{n} puntos',
    lose_title: 'EL ORBE RESISTIÓ',
    lose_time: '¡Se acabó el tiempo!',
    lose_sub: 'La magia se renueva… ¡otro intento!',
    win_sub: 'El trofeo te espera en la sala',
    retry_sub: 'El orbe se reconstruye…',
    bricks_left: 'Ladrillos: {n}',
    score_lbl: '{n} pts',
    bomb_spawn: '¡BOLA NEGRA! Lánzala al orbe',
    bomb_boom: '¡BOOM! {n} ladrillos',
    // v2.72 · SUPERPODERES PROPIOS del WIZARD (los originales de antes de
    // las etapas de habilidad — NO los del CLOWN): BOLA LOCA y PORTALES.
    pw_warn: '¡SUPERPODER DE WIZARD!',
    pw_ball: '¡BOLA LOCA! Grande, multicolor y errática',
    pw_portal: '¡PORTALES MÁGICOS! La bola salta entre ellos',
    pw_fuego: '¡BOLA DE FUEGO! La bola arde y deja estela · no te quemes',
    pw_sombras: '¡NOCHE ARCANA! Todo se apaga · la bola BRILLA',
  },
  en: {
    champ: 'NEW MAGIC TRICK',
    announce: 'Welcome to the New Magic Trick. Beat WIZARD and smash his magic orbs.',
    // v2.106 · instruction poster for the MAGIC ORB test
    instr_orb_t: 'TEST · THE MAGIC ORB',
    instr_orb: [
      'A SPHERE of magic bricks floats ahead: hit it with the BALL using your PADDLES to break its bricks.',
      'It breaks by LAYERS: shell first, then the inner layers… until the glowing CORE goes dark.',
      'You get extra time and a MAGIC GUN in your free hand to finish the bricks the ball cannot reach.',
      'In the COMPLEX version the orb spins and protects itself better: mind your angles!',
    ],
    msg_enter: 'NEW MAGIC TRICK! Destroy the MAGIC ORB',
    cartel_new: 'THE MAGIC ORB!',
    cartel_vs: 'Attempt {n} · smash the whole orb',
    // v2.70 · DUELOS del camino (etapas 1/3/5)
    duel_new: 'MAGIC DUEL!',
    duel_vs: 'VS WIZARD · Round {n}',
    msg_duel: 'DUEL vs WIZARD Lv. 1! Match to 11 points',
    wiz2_up: 'WIZARD Lv. 2 · harder!',
    wiz3_up: 'WIZARD Lv. 3 · FINAL BOSS!',
    rank_title: 'RANKING',
    rank_empty1: 'No attempts yet.',
    rank_empty2: 'Blow up the orb to open your record!',
    rank_win: 'Destroyed!',
    rank_lose: 'It held',
    rank_tot: 'Wins: {n} · Best: {b}',
    rec_rally: 'Best rally: {n}', rec_streak: 'Best streak: {n}', rec_surv: 'Survival: {n}',
    trophy_rank: 'MAGIC TRICK CHAMPION',
    trophy_get: '!!TROPHY: GOLDEN WAND!!',
    montaje_hint: 'Trigger: skip assembly',
    montaje_sub: 'The vortex is forging the orb…',
    play_hint: 'Break the orb before time runs out!',
    gun_hint: 'MAGIC PISTOL · trigger breaks RED bricks only',
    alert_msg: 'SHOOT THE CLOCK! +{n} s',
    alert_gone: 'The clock is gone…',
    no_more_ext: 'No extensions left',
    ext_get: 'OVERTIME +{n} s!',
    ext_left: 'Extensions: {n}',
    last_bricks: 'The orb resists! Magic attraction MAXED OUT',
    chain_n: 'CHAIN ×{n}',
    time_warn: 'LAST {n} SECONDS!',
    win_title: 'MAGIC ORB DESTROYED!',
    win_score: '{n} points',
    lose_title: 'THE ORB HELD ON',
    lose_time: "Time's up!",
    lose_sub: 'The magic renews itself… try again!',
    win_sub: 'The trophy awaits in the room',
    retry_sub: 'The orb rebuilds itself…',
    bricks_left: 'Bricks: {n}',
    score_lbl: '{n} pts',
    bomb_spawn: 'BLACK BALL! Throw it at the orb',
    bomb_boom: 'BOOM! {n} bricks',
    // v2.72 · WIZARD's OWN superpowers (the originals — not the CLOWN's):
    // CRAZY BALL and MAGIC PORTALS. Same two-phase system (2 s warning).
    pw_warn: "WIZARD'S SUPERPOWER!",
    pw_ball: 'CRAZY BALL! Big, multicolor and erratic',
    pw_portal: 'MAGIC PORTALS! The ball jumps between them',
    pw_fuego: 'FIREBALL! The ball burns with a trail · do not get burned',
    pw_sombras: 'ARCANE NIGHT! Everything goes dark · the ball GLOWS',
  },
};
function tx(key, params) {
  const pack = TXT[TL] || TXT.es;
  let s = (pack[key] !== undefined) ? pack[key] : (TXT.es[key] !== undefined ? TXT.es[key] : key);
  if (params) for (const k of Object.keys(params)) s = s.split('{' + k + '}').join(String(params[k]));
  return s;
}

/* ------------------------------ configuración ------------------------------ */
/* Parámetros del NIVEL (19 del diseño + ayudas). Los valores de manifest.json
 * (bloque «level») se fusionan encima en init() — así el artista ajusta SIN
 * tocar código. */
const LEVEL = {
  // v2.71 · ORBE MÁS SENCILLO (petición del artista para la etapa 2):
  // ladrillos MÁS GRANDES (0,125 m) y radios más cortos (4,6/3,0/1,5) —
  // el orbe mide LO MISMO (≈0,58 m de radio, misma posición) pero con LA
  // MITAD de ladrillos (925 → 437, −52,8%) y dianas un 25% más grandes.
  brickSize: 0.125,         // m por ladrillo (v2.71: 0,125 — dianas más fáciles)
  radiusOuter: 4.6,         // radio EXTERIOR en ladrillos (capa roja)
  radiusMid: 3.0,           // radio MEDIO en ladrillos (capa marrón)
  radiusCore: 1.5,          // radio del NÚCLEO en ladrillos (capa amarilla)
  timeStart: 120,           // s de reloj
  timeBonus: 60,            // s de la prórroga (bloque reloj)
  maxExtensions: 2,         // prórrogas MÁXIMAS por intento
  alertThreshold: 30,       // s: umbral de la ALERTA FINAL
  clockBlockLife: 4,        // s que flota el bloque reloj
  clockRetryDelay: 9,       // s para re-sacar el reloj si se falló (opcional)
  lastBricksPercent: 5,     // % restante = fase final (atracción reforzada)
  maxBalls: 2,              // bolas simultáneas (v2.63: DOS, cada una con su vórtice)
  respawnDelay: 0.9,        // s para recambiar una bola perdida (v2.63: más rápido)
  restitution: 1.0,         // v2.63: rebote SIN pérdida (juego frenético)
  energyLossPerHit: 1.0,    // v2.63: taladrar NO frena la bola (antes 0.9)
  maxChain: 6,              // v2.63: taladra hasta 6 ladrillos por impacto
  minChainSpeed: 1.2,       // m/s: por debajo sólo rompe 1 y rebota
  minReturnSpeed: 2.8,      // v2.63: la bola sale de CUALQUIER impacto con esta mínima
  minBounceHeight: 0.45,    // v2.64: ARCO MÍNIMO de cada bote (m) — la bola que
                            // vuelve nunca llega rastrera: casi el arco del vórtice
  bombChance: 0.18,         // v2.65: probabilidad de que un recambio salga BOLA NEGRA
  bombEvery: 30,            // v2.65: s sin bola negra → el próximo recambio ES negra
  blastRadius: 0.55,        // v2.65: radio (m) de la explosión al chocar con el orbe
  blastMax: 60,             // v2.65: tope de ladrillos destruidos por explosión
  attractionStrength: 0.35, // giro direccional por segundo (fracción del ángulo)
  attractionMaxAngle: 15,   // grados máximos de corrección por segundo
  attractionRange: 6,       // m de alcance de la atracción
  montajeTime: 7.0,         // s del montaje (5–8 s del diseño)
  layerPoints: [30, 20, 10],// puntos por ladrillo: núcleo/medio/exterior
  chainBonus: 5,            // puntos extra por ladrillo dentro de la cadena
  star3Frac: 0.25,          // fracción de tiempo restante para 3 estrellas
  star2Frac: 0.08,          // … para 2 estrellas
};

/* v2.70 · VARIANTE COMPLEJA del orbe (etapa 4 del camino): MISMO espacio en
 * el corredor pero ladrillos MÁS FINOS (0,088 m) y una capa exterior más
 * (radio 7) — OTRO orbe, no una copia: ~60% más de ladrillos que el orbe
 * NORMAL de la v2.69, SIN prórrogas, cadenas más exigentes y el bloque-reloj
 * más efímero. Encaja perfecto: cima ≈ 2,09 m (< HUD 2,28) y base ≈ 0,76 m
 * (apoyado en la mesa).
 * v2.71: radiusMid/radiusCore se FIJAN a sus valores históricos (4/2) para
 * que el cambio de dificultad del orbe NORMAL no altere la variante difícil
 * (mismo nº de ladrillos de siempre: ~1.419). */
const ORBE_COMPLEJO = {
  brickSize: 0.088,
  radiusOuter: 7,
  radiusMid: 4,             // v2.71: FIJADO (antes heredaba del orbe normal)
  radiusCore: 2,            // v2.71: FIJADO (antes heredaba del orbe normal)
  maxExtensions: 0,        // la prueba difícil no da prórrogas
  minChainSpeed: 1.35,
  clockBlockLife: 3,
};

/* v2.71 · REGLA FIJA DE DUELOS (cualquier campeonato, siempre): el rival en
 * persona se coloca a ~0,50 m a la DERECHA del borde derecho de la mesa y su
 * esfera/regalo ~0,50 m por detrás del borde lejano. DUEL_X se calcula en
 * init() con el DIMS real: tableHalfWidth + 0,50 ≈ 1,26 m. */
let DUEL_X = 1.2625;

/* v2.75 · AJUSTE DEL ARTISTA: en los duelos el WIZARD se coloca 25 cm más a
 * la DERECHA y 25 cm más ARRIBA de la REGLA FIJA (v2.71). La esfera y el aro
 * de chispas lo acompañan: la composición aprobada no cambia, solo se
 * recoloca entera. El hueco del ORBE (fuera de duelos) queda como siempre. */
const WIZ_DUEL_OFF = { x: 0.25, y: 0.25 };

/* v2.72 · SUPERPODERES PROPIOS del WIZARD en duelos (LOS ORIGINALES de
 * antes de las etapas de habilidad — NO los del CLOWN). Mismo motor de dos
 * fases (aviso «SUPERPODER» de 2 s con la partida congelada → efecto en
 * pleno rallye), pero los efectos son los SUYOS:
 *  · BOLA LOCA — la bola se hace MÁS GRANDE, CAMBIA DE COLOR sin parar
 *    (ciclo arcoíris arcano) y navega con movimiento ALGO ERRÁTICO
 *    (vaivén lateral sinusoidal + ráfagas aleatorias cortas).
 *  · PORTALES MÁGICOS — se abren DOS agujeros SOBRE la mesa (uno a cada
 *    lado de la red, anillo portals.webp del artista girando encima):
 *    la bola que bota dentro de un agujero SALE DISPARADA por el otro. */
const WIZ_POWER = {
  chance: 0.32,        // probabilidad por bola que viene hacia ti
  cooldown: 13.0,      // s entre superpoderes
  minRallyHits: 1,     // mínimo de golpes del rallye
  warn: 2.0,           // s de aviso con el cartel SUPERPODER
  duration: 8.0,       // s de duración de la BOLA LOCA
};
const LOCA_BALL = {
  scale: 1.65,         // la bola crece (x1,65 — radio físico acompaña)
  hueSpeed: 0.30,      // vueltas de rueda de color por segundo
  swayAmp: 4.0,        // vaivén lateral sinusoidal (m/s²)
  swayFreq: 8.5,       // frecuencia del vaivén (rad/s ≈ 1,35 Hz)
  jitter: 2.5,         // ráfaga aleatoria extra (m/s², signo alternante)
  jitterEvery: 0.22,   // s entre ráfagas aleatorias
};
const WIZ_PORTALS = {
  duration: 9.0,       // s con los portales abiertos
  // v2.73 (petición del artista): MÁS GRANDES y en la PARTE CENTRAL de la
  // mesa — agujero 0,14→0,19 m, anillo 0,46→0,62 m, offX 0,34→0,18 y
  // offZ 0,52→0,34 (los dos flanqueando la red, casi en el eje).
  holeR: 0.19,         // radio del AGUJERO sobre la mesa (m, diana)
  ring: 0.62,          // tamaño del anillo portals.webp (m)
  offX: 0.18,          // separación lateral desde el eje central (m)
  offZ: 0.34,          // distancia de cada agujero a la red (m)
  pop: 1.15,           // impulso vertical mínimo al salir (m/s)
  centerNudge: 0.9,    // empujón suave hacia el centro de la mesa (m/s)
  cd: 0.45,            // s mínimo entre teletransportes (anti-bucle)
};

/* Escena del nivel (posiciones en el RIG del juego). La mesa vive en
 * tableCenterZ=-1.6 con halfLength 1.37; el corredor llega hasta la pared
 * del fondo de la sala (roomFrontZ=-5.55) y el portal cuelga en ella. */
function sceneConfig() {
  const cz = (DIMS && DIMS.tableCenterZ) || -1.6;
  const hl = (DIMS && DIMS.tableHalfLength) || 1.37;
  const hw = (DIMS && DIMS.tableHalfWidth) || 0.7625;
  const top = (DIMS && DIMS.tableTopY) || 0.76;
  return {
    tableNearZ: cz + hl,          // -0.23 borde del jugador
    corridorZ0: cz - hl,          // -2.97 borde lejano de la mesa original
    corridorZ1: -5.40,            // extremo del corredor (pared en -5.55)
    halfW: hw,
    topY: top,
    wallH: 0.9,                   // altura de los cristales mágicos
    // v2.61: el ORBE flota sobre el CENTRO del corredor (zona de ampliación
    // de la mesa), sin tapar al mago; el portal apenas despega de la pared.
    // v2.71: la Y real del centro se DERIVA en build() del cfg activo
    // (topY + floor(radiusOuter)·brickSize + brickSize/2) para que el orbe
    // repose SIEMPRE sobre la mesa con cualquier rejilla (normal/compleja).
    // y referencial histórica: 1.42 (normal v2.69 y compleja).
    orb: { y: 1.42, z: -4.19 },   // centro del ORBE (y real = derivada en build)
    portal: { x: 0, y: 1.18, z: -5.44, size: 1.7, rotSpeed: 0.9 },
    wizard: { x: 1.62, z: -4.5, baseY: 1.0, width: 1.7 },
    // v2.64: marcador SUBIDO (y 2.06→2.48) — con y=2.06 su borde inferior
    // (1.86) cortaba la parte alta del orbe (cima 2.02) y tapaba la visión;
    // ahora flota 0.26 m por encima de la cima, sin tocarla nunca.
    hud: { y: 2.48, z: -3.6 },
    // v2.70: cartel de entrada MUY POR ENCIMA de todo — el orbe llega a 2,09
    // (variante compleja), el HUD flota en 2,28–2,68 y el marcador del núcleo
    // llega a 2,375; el cartel a 2,95 nunca interfiere con personajes ni
    // elementos del diseño (petición del artista: nada en la línea de visión).
    // v2.130 · FIX: el techo de la sala está en 2,85 m (roomHeight) y el
    // cartel a 2,95 metía su borde superior (3,18) DENTRO del techo. Baja a
    // 2,55: borde superior 2,78 (0,07 de aire) y sigue por encima del
    // marcador (2,375) y de la cabeza del mago.
    cartel: { y: 2.55, z: -2.9 },
    ban: { y: 1.52, z: -3.3 },
    ballColors: [0x7fe3ff, 0xffd257, 0xd98cff],
  };
}
let SC = null;   // se rellena en init() (DIMS ya disponible)

/* MAGIA: parámetros heredados de la temática (mesa de estrellas, audio…) */
const MAGIA = {
  wizardOn: false,          // v2.63: el mago NO participa en la fase del orbe
  spriteWidth: 1.7, baseY: 1.0, z: -4.5,          // WIZARD (junto al orbe)
  portal: { size: 1.7, y: 1.18, z: -5.44, x: 0, rotSpeed: 0.9 },
  thresholds: { picandoRallyHits: 7, loosingDiff: 6, comboRally: 6, surprisedRally: 3 },
  apexMin: 0.38, wallRest: 0.82,
  musicVol: 0.15,   // BSO real del campeonato, bajita como la de La Locura
};

/* ------------------------------- utilidades -------------------------------- */
function magiaCanvas(w, h) { const cv = document.createElement('canvas'); cv.width = w; cv.height = h; return cv; }

function mistTexture() {
  const cv = magiaCanvas(128, 128);
  const c = cv.getContext('2d');
  const gr = c.createLinearGradient(0, 0, 128, 0);
  gr.addColorStop(0, 'rgba(220,205,255,0.0)');
  gr.addColorStop(0.5, 'rgba(220,205,255,0.55)');
  gr.addColorStop(1, 'rgba(220,205,255,0.0)');
  c.fillStyle = gr; c.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(cv);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(3, 1);
  return t;
}

function starTexture() {
  const cv = magiaCanvas(64, 64);
  const c = cv.getContext('2d');
  c.translate(32, 32);
  c.fillStyle = '#fff';
  c.beginPath();
  // v2.73 FIX: puntas cada 72° + valles a +36° — la versión anterior
  // saltaba cada 144° y zigzagueaba sobre sí misma (no parecía estrella)
  for (let i = 0; i < 5; i++) {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / 5;
    const a2 = a + Math.PI / 5;
    c.lineTo(Math.cos(a) * 26, Math.sin(a) * 26);
    c.lineTo(Math.cos(a2) * 11, Math.sin(a2) * 11);
  }
  c.closePath(); c.fill();
  return new THREE.CanvasTexture(cv);
}

/** Disco suave (glow/estelas) — radial gradient con alfa real. */
function softTexture() {
  const cv = magiaCanvas(64, 64);
  const c = cv.getContext('2d');
  const g = c.createRadialGradient(32, 32, 2, 32, 32, 30);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.4, 'rgba(255,255,255,0.55)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  c.fillStyle = g; c.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(cv);
}

function starTextureMagia() {
  const cv = magiaCanvas(64, 64);
  const c = cv.getContext('2d');
  c.translate(32, 32);
  // v2.73: halo suave alrededor — se lee como estrella titilante mágica
  const halo = c.createRadialGradient(0, 0, 2, 0, 0, 30);
  halo.addColorStop(0, 'rgba(191,227,255,0.5)');
  halo.addColorStop(1, 'rgba(191,227,255,0)');
  c.fillStyle = halo;
  c.beginPath(); c.arc(0, 0, 30, 0, Math.PI * 2); c.fill();
  // v2.73 FIX: ESTRELLA de 5 puntas bien construida (puntas cada 72°,
  // valles a +36°) — antes el trazo zigzagueaba y salía una mancha
  c.strokeStyle = '#bfe3ff'; c.fillStyle = 'rgba(191,227,255,0.9)';
  c.lineWidth = 2.5;
  c.beginPath();
  for (let i = 0; i < 5; i++) {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / 5;
    const a2 = a + Math.PI / 5;
    c.lineTo(Math.cos(a) * 26, Math.sin(a) * 26);
    c.lineTo(Math.cos(a2) * 10.5, Math.sin(a2) * 10.5);
  }
  c.closePath(); c.fill(); c.stroke();
  return new THREE.CanvasTexture(cv);
}

/** Cara del BLOQUE RELOJ (prórroga): esfera negra, índice dorado, manecillas. */
function clockTexture() {
  const cv = magiaCanvas(256, 256);
  const c = cv.getContext('2d');
  c.fillStyle = '#0d0d12'; c.fillRect(0, 0, 256, 256);
  c.strokeStyle = '#f6d34c'; c.lineWidth = 10;
  c.beginPath(); c.arc(128, 128, 104, 0, Math.PI * 2); c.stroke();
  c.lineWidth = 5;
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * Math.PI * 2;
    c.beginPath();
    c.moveTo(128 + Math.cos(a) * 92, 128 + Math.sin(a) * 92);
    c.lineTo(128 + Math.cos(a) * 102, 128 + Math.sin(a) * 102);
    c.stroke();
  }
  c.strokeStyle = '#fff'; c.lineWidth = 8; c.lineCap = 'round';
  c.beginPath(); c.moveTo(128, 128); c.lineTo(128, 66); c.stroke();
  c.beginPath(); c.moveTo(128, 128); c.lineTo(172, 148); c.stroke();
  c.fillStyle = '#f6d34c';
  c.beginPath(); c.arc(128, 128, 9, 0, Math.PI * 2); c.fill();
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* v2.63 · BISEL de los ladrillos del orbe (el estilo del ARKANOID de La
 * Locura): textura en ESCALA DE GRISES con luz arriba, sombra abajo, marco
 * oscuro exterior y bisel claro interior. El material la multiplica por el
 * color de instancia (rojo/marrón) → ladrillo tallado en las 6 caras. */
function brickBevelTexture() {
  const cv = magiaCanvas(128, 128);
  const c = cv.getContext('2d');
  const grd = c.createLinearGradient(0, 0, 0, 128);
  grd.addColorStop(0, '#d2d2d2');
  grd.addColorStop(0.14, '#ffffff');      // bisel superior iluminado
  grd.addColorStop(0.55, '#a8a8a8');
  grd.addColorStop(0.86, '#717171');      // sombra inferior
  grd.addColorStop(1, '#5a5a5a');
  c.fillStyle = grd;
  c.fillRect(0, 0, 128, 128);
  // junta oscura entre ladrillos (marco exterior)
  c.strokeStyle = 'rgba(0,0,0,0.62)';
  c.lineWidth = 7;
  c.strokeRect(0, 0, 128, 128);
  // bisel interior claro tallado
  c.strokeStyle = 'rgba(255,255,255,0.4)';
  c.lineWidth = 3;
  c.strokeRect(5, 5, 118, 118);
  // destello especular diagonal suave
  const sh = c.createLinearGradient(0, 128, 128, 0);
  sh.addColorStop(0.32, 'rgba(255,255,255,0)');
  sh.addColorStop(0.5, 'rgba(255,255,255,0.17)');
  sh.addColorStop(0.68, 'rgba(255,255,255,0)');
  c.fillStyle = sh;
  c.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* ============================================================================
 *  WizardRival — el mago con las 12 pinturas del artista (mismo pipeline
 *  asíncrono que siempre). v2.60: flota JUNTO AL ORBE (posición nueva del
 *  mapa) y sin portal-regalo delante (el portal grande es el del fondo).
 *  v2.71 · DUELOS: el mago en persona se coloca según la REGLA FIJA
 *  (~0,50 m a la derecha del borde derecho de la mesa) y recupera su
 *  ESFERA (regalo.webp): el elemento gráfico que tapa su mitad inferior y
 *  GIRA sobre su centro (como el regalo del CLOWN, con giro propio).
 *  ============================================================================ */
/* Esfera del mago en duelos: tamaño/altura calibrados para cubrir SU MITAD
 * INFERIOR sin tocar la cara (sprite 1,7×0,85 flotando con dy duelDy).
 * v2.73 (petición del artista): el WIZARD sube ~15 cm en los duelos
 * (duelDy −0,38 → −0,23) y la esfera lo acompaña (y 0,68 → 0,83) para
 * seguir tapando exactamente la misma parte baja. Además YA NO gira de
 * canto: gira SOBRE SÍ MISMA (en su propio plano) y queda SIEMPRE
 * PERPENDICULAR a la cámara (billboard de guiñada en update()).
 * v2.78: la esfera «un 33% más grande» NO SE VIO — el dibujo de regalo.webp
 * sólo ocupa el 75% de su lienzo (el resto es brillo transparente), así que
 * agrandar el PLANO 0,85 → 1,13 dejó el círculo VISIBLE en ~0,85 m.
 * v2.80 (petición del artista): regalo.webp RECORTADO a su círculo real
 * (772×781 px, sin margen transparente — misma regla que los troqueles) y
 * esfera de 1,34 m VISIBLES con la base en el suelo (centro a size/2).
 * Con R=0,67 el círculo cubre por completo el corte inferior del sprite
 * (borde a 1,02 m y ±0,45 m de ancho incluso en la pose focused, la más
 * ancha) aunque el jugador se incline, y su parte alta (1,34 m) queda por
 * debajo de la cara del mago (~1,5–1,85 m): tapa la parte de abajo, deja
 * ver al personaje. Por anclar la base al suelo NO sube/baja con duelDy. */
const WIZ_GIFT = { size: 1.34, y: 0.67, z: -3.5, spin: 0.9, duelDy: -0.23 };
class WizardRival {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.data = ctrl.manifest;
    this.inited = false;
    this.state = '';
    this.applied = false;
    this.texs = {};
    this.spriteBaseY = MAGIA.baseY + 0.525;
    this._starBaseY = MAGIA.baseY + 0.855 + 0.055;  // v2.70: base real de las estrellas
    this._duel = false;                             // v2.70: modo DUELO (centrado)
  }

  build() {
    if (this.inited) return;
    this.inited = true;
    const mat = new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });
    this.sprite = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.75), mat);
    this.sprite.position.set(MAGIA.portal.x + SC.wizard.x, this.spriteBaseY, SC.wizard.z);
    this.sprite.renderOrder = 6;
    this.sprite.visible = false;
    this.game.rig.add(this.sprite);

    // anillo de GOTAS (victoria de WIZARD = derrota del jugador)
    this.stars = new THREE.Group();
    const dropTex = starTexture();
    const starGeo = new THREE.PlaneGeometry(0.1, 0.1);
    for (let i = 0; i < 6; i++) {
      const sm = new THREE.MeshBasicMaterial({ map: dropTex, transparent: true, depthWrite: false });
      const st = new THREE.Mesh(starGeo, sm);
      const a = (Math.PI * 2 / 6) * i;
      st.position.set(Math.cos(a) * 0.26, Math.sin(a) * 0.12, 0.02);
      st.userData.phase = i;
      this.stars.add(st);
    }
    // v2.75 · «el círculo circular girador» — el aro de chispas que gira sobre
    // la cabeza del mago: 1,5 VECES más grande (petición del artista). El
    // scale del grupo agranda JUNTO el radio de la órbita y las chispas.
    this.stars.scale.setScalar(1.5);
    this.stars.position.set(MAGIA.portal.x + SC.wizard.x, MAGIA.baseY + 1.05, SC.wizard.z);
    this.stars.visible = false;
    this.game.rig.add(this.stars);
    this.applySpriteAspect(1024 / 512);

    // ESFERA del mago (regalo.webp) — v2.71 RECUPERADA para los DUELOS:
    // el elemento gráfico que tapa su mitad inferior y GIRA sobre su centro
    // (el «portal pequeño» retirado del mapa v2.60 vuelve con otro papel).
    // Se crea oculta y se muestra SOLO con el mago en persona (setDuel). 
    const GS = WIZ_GIFT;
    this.gift = new THREE.Group();
    this.giftMat = new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });
    this.giftPlane = new THREE.Mesh(new THREE.PlaneGeometry(GS.size, GS.size), this.giftMat);
    this.giftPlane.renderOrder = 7;   // SIEMPRE por encima del sprite del mago
    this.gift.add(this.giftPlane);
    this.gift.position.set(DUEL_X, GS.y, GS.z);
    this.gift.visible = false;
    this.game.rig.add(this.gift);
    const bimg = new Image();
    bimg.onload = () => {
      const t = new THREE.Texture();
      t.colorSpace = THREE.SRGBColorSpace;
      t.image = bimg; t.needsUpdate = true;
      this.giftMat.map = t; this.giftMat.needsUpdate = true;
    };
    bimg.src = this.data.giftUrl;
    this.loadTextures();
  }

  loadTextures() {
    const urls = (this.data && this.data.stateUrls) || {};
    for (const st of Object.keys(urls)) {
      const tex = new THREE.Texture();
      tex.colorSpace = THREE.SRGBColorSpace;
      const img = new Image();
      img.onload = () => {
        tex.image = img;
        tex.needsUpdate = true;
        if (!this._aspectHooked) {
          this._aspectHooked = true;
          this.applySpriteAspect(img.width / img.height);
        }
        this.texs[st] = tex;
        if (this.state === st && !this.applied) this.applyStateTexture();
      };
      img.onerror = () => { /* sin arte para ese estado: sigue el anterior */ };
      img.src = urls[st];
    }
  }

  applySpriteAspect(ar) {
    if (!this.inited || !ar || !isFinite(ar)) return;
    let w = 1.4, h = 1.75;
    if (ar > 1.2) { w = MAGIA.spriteWidth; h = w / ar; }
    this.sprite.geometry.dispose();
    this.sprite.geometry = new THREE.PlaneGeometry(w, h);
    this.spriteBaseY = MAGIA.baseY + h / 2;
    this.sprite.position.y = this.spriteBaseY;
    this._starBaseY = MAGIA.baseY + h + 0.055;
    this.stars.position.y = this._starBaseY;
  }

  /** v2.71 · Modo DUELO: el mago se coloca según la REGLA FIJA de duelos
   *  (~0,50 m a la derecha del borde derecho de la mesa, detrás del borde
   *  lejano) — igual que el CLOWN en La Locura desde v2.71. En su hueco del
   *  orbe sigue flotando donde siempre. La esfera acompaña la x del duelo. */
  setDuel(on) {
    this._duel = !!on;
    if (!this.inited || !this.sprite) return;
    const cx = this._duel ? (DUEL_X + WIZ_DUEL_OFF.x) : (MAGIA.portal.x + SC.wizard.x);   // v2.75: +25 cm derecha
    const cz = this._duel ? -3.82 : SC.wizard.z;
    const dy = this._duel ? (WIZ_GIFT.duelDy + WIZ_DUEL_OFF.y) : 0;   // v2.73: +15 cm · v2.75: +25 cm más
    this.sprite.position.set(cx, this.spriteBaseY + dy, cz);
    this.stars.position.set(cx, this._starBaseY + dy, cz);
    if (this.gift) {   // la esfera sigue al mago (x) — v2.78: base SIEMPRE en el suelo
      this.gift.position.x = cx;
      this.gift.position.y = WIZ_GIFT.y;   // size/2: la parte baja toca el suelo
    }
  }

  setState(name) {
    if (this.state === name) return;
    this.state = name;
    this.applied = false;
    this.applyStateTexture();
  }

  applyStateTexture() {
    const tex = this.texs[this.state];
    if (tex) {
      this.sprite.material.map = tex;
      this.sprite.material.needsUpdate = true;
      this.applied = true;
    }
  }

  update(dt, t) {
    void dt;
    if (!this.inited || !this.sprite.visible) return;
    // v2.71: posición según modo (duelo REGLA FIJA vs hueco del orbe)
    // v2.75: en duelo, +25 cm a la derecha y +25 cm arriba (WIZ_DUEL_OFF)
    const cx = this._duel ? (DUEL_X + WIZ_DUEL_OFF.x) : (MAGIA.portal.x + SC.wizard.x);
    const cz = this._duel ? -3.82 : SC.wizard.z;
    const dy = this._duel ? (WIZ_GIFT.duelDy + WIZ_DUEL_OFF.y) : 0;
    this.sprite.position.set(cx, this.spriteBaseY + dy, cz);
    this.stars.position.set(cx, this._starBaseY + dy, cz);
    // v2.73: la ESFERA queda SIEMPRE PERPENDICULAR a la cámara (billboard
    // de guiñada) y gira SOBRE SÍ MISMA (en su propio plano) — tapa la
    // parte baja del mago desde cualquier ángulo; nunca más de canto.
    if (this.gift && this.gift.visible && this.giftPlane) {
      if (this.game.camera) {
        if (!this._wp) this._wp = new THREE.Vector3();
        this.game.camera.getWorldPosition(this._wp);
        this.gift.rotation.y = Math.atan2(
          this._wp.x - this.gift.position.x,
          this._wp.z - this.gift.position.z,
        );
      }
      this.giftPlane.rotation.z = -t * WIZ_GIFT.spin;
    }
    if (this.stars.visible) {
      this.stars.rotation.y = t * 1.6;
      for (const st of this.stars.children) {
        st.position.y = Math.sin(t * 3 + st.userData.phase) * 0.045;
        st.rotation.z = t * 2.2 + st.userData.phase;
      }
    }
  }

  hide() {
    if (!this.inited) return;
    this.sprite.visible = false;
    this.stars.visible = false;
    if (this.gift) this.gift.visible = false;
  }
}

/* ============================================================================
 *  WizardCartel — cartel de entrada «¡EL ORBE MÁGICO! · Intento N»
 *  ============================================================================ */
class WizardCartel {
  constructor(ctrl) { this.game = ctrl.game; this.t = -1; }
  build() {
    this.cv = magiaCanvas(1024, 280);
    this.tex = new THREE.CanvasTexture(this.cv);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, depthWrite: false });
    this.group = new THREE.Group();
    this.plane = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 1.7 * 280 / 1024), mat);
    this.group.add(this.plane);
    // v2.70: MUY por encima de todo (SC.cartel) — nunca en la línea de visión
    // del mago, del orbe ni del marcador (petición del artista).
    this.group.position.set(0, (SC.cartel || { y: 2.95 }).y, (SC.cartel || { z: -2.9 }).z);
    this.group.visible = false;
    this.game.rig.add(this.group);
  }
  show(round, kind) {
    const duel = kind === 'duel';   // v2.70: 'duel' = VS WIZARD · 'orb' = orbe
    const g = this.cv.getContext('2d');
    g.clearRect(0, 0, 1024, 280);
    g.fillStyle = 'rgba(18,12,38,0.92)';
    g.strokeStyle = '#c9a6ff';
    g.lineWidth = 10;
    const r = 40;
    g.beginPath();
    g.moveTo(r, 10); g.arcTo(1014, 10, 1014, 270, r); g.arcTo(1014, 270, 10, 270, r);
    g.arcTo(10, 270, 10, 10, r); g.arcTo(10, 10, 1014, 10, r);
    g.closePath(); g.fill(); g.stroke();
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillStyle = '#e2d6f6';
    g.font = '800 92px system-ui, sans-serif';
    g.fillText(tx(duel ? 'duel_new' : 'cartel_new'), 512, 105);
    g.fillStyle = '#eef2f6';
    g.font = '700 58px system-ui, sans-serif';
    g.fillText(tx(duel ? 'duel_vs' : 'cartel_vs', { n: round }), 512, 205);
    this.tex.needsUpdate = true;
    this.t = 0;
    this.group.visible = true;
  }
  update(dt) {
    if (this.t < 0 || !this.group.visible) return;
    this.t += dt;
    const sIn = Math.min(1, this.t / 0.45);
    const ease = 1 - Math.pow(1 - sIn, 3);
    const pulse = 1 + Math.sin(Math.max(0, this.t) * 6) * 0.05 * Math.max(0, 1 - this.t / 2.5);
    this.group.scale.setScalar(0.25 + 0.75 * ease * pulse);
    this.plane.material.opacity = this.t > 2.6 ? Math.max(0, 1 - (this.t - 2.6) / 0.5) : 1;
    if (this.t > 3.1) { this.group.visible = false; this.t = -1; }
  }
  hide() { if (this.group) { this.group.visible = false; this.t = -1; } }
}

/* ============================================================================
 *  WizardRanking — panel lateral. v2.60: filas del ORBE MÁGICO
 *  (R{n} · estrellas · puntos) y mejor puntuación persistente.
 *  ============================================================================ */
class WizardRanking {
  constructor(ctrl) { this.ctrl = ctrl; this.game = ctrl.game; }
  build() {
    this.cv = magiaCanvas(512, 720);
    this.tex = new THREE.CanvasTexture(this.cv);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, depthWrite: false });
    this.group = new THREE.Group();
    this.plane = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.62 * 720 / 512), mat);
    this.group.add(this.plane);
    this.group.position.set(1.46, 1.12, -1.7);
    this.group.rotation.y = -0.42;
    this.group.visible = false;
    this.game.rig.add(this.group);
    // v2.75 · INSIGNIA del campeonato (arte del artista): el LOGRO que se
    // gana al completar el camino. Carga perezosa; al llegar repinta el
    // panel y preside el palmarés (flanquea el título) si hay trofeo.
    try {
      const im = new Image();
      im.onload = () => { this._insignia = im; this.refresh(); };
      im.src = new URL('./assets/insignia.png', import.meta.url).href;
    } catch (e) { /* sin insignia: el panel queda como siempre */ }
    this.refresh();
  }
  refresh() {
    if (!this.cv) return;
    const c = this.ctrl;
    const g = this.cv.getContext('2d');
    g.clearRect(0, 0, 512, 720);
    g.fillStyle = 'rgba(18,12,38,0.9)';
    g.strokeStyle = 'rgba(201,166,255,0.85)';
    g.lineWidth = 8;
    g.beginPath();
    const r = 30;
    g.moveTo(r, 6); g.arcTo(506, 6, 506, 714, r); g.arcTo(506, 714, 6, 714, r);
    g.arcTo(6, 714, 6, 6, r); g.arcTo(6, 6, 506, 6, r);
    g.closePath(); g.fill(); g.stroke();
    g.textAlign = 'center'; g.textBaseline = 'alphabetic';
    g.fillStyle = '#e2d6f6';
    g.font = '800 46px system-ui, sans-serif';
    g.fillText(tx('rank_title'), 256, 66);
    // v2.75: la INSIGNIA preside el ranking (sólo con el trofeo ganado):
    // dos copias flanqueando el título, como medallas del palmarés.
    if (c.trophy && this._insignia) {
      const _iw = this._insignia.naturalWidth || 512;
      const _ih = this._insignia.naturalHeight || 512;
      const _s = 68 / Math.max(_iw, _ih);
      const _w = _iw * _s, _h = _ih * _s;
      g.drawImage(this._insignia, 112 - _w / 2, 56 - _h / 2, _w, _h);
      g.drawImage(this._insignia, 400 - _w / 2, 56 - _h / 2, _w, _h);
    }
    g.fillStyle = '#9aa7b4';
    g.font = '600 27px system-ui, sans-serif';
    // v2.66: el nombre del jugador preside SU ranking (si lo escribió)
    let _pn = '';
    try { _pn = String(localStorage.getItem('pp_player_name') || '').trim().slice(0, 12); } catch (e) { /* */ }
    g.fillText(_pn ? '★ ' + _pn + ' ★' : tx('champ'), 256, 110);
    g.strokeStyle = 'rgba(255,255,255,0.18)';
    g.lineWidth = 3;
    g.beginPath(); g.moveTo(40, 136); g.lineTo(472, 136); g.stroke();
    const rank = c.rank || [];
    const rows = rank.slice(-4).reverse();
    g.textBaseline = 'middle';
    if (c.trophy) {
      g.fillStyle = '#f6d34c';
      g.font = '800 30px system-ui, sans-serif';
      g.fillText('★ ' + tx('trophy_rank') + ' ★', 256, 168);
    }
    if (!rows.length) {
      g.fillStyle = '#75828f';
      g.font = '500 28px system-ui, sans-serif';
      g.fillText(tx('rank_empty1'), 256, c.trophy ? 250 : 236);
      g.fillText(tx('rank_empty2'), 256, c.trophy ? 290 : 276);
    }
    rows.forEach((row, i) => {
      const y = (c.trophy ? 222 : 186) + i * 64;
      g.textAlign = 'left';
      g.fillStyle = '#8b949c';
      g.font = '700 30px system-ui, sans-serif';
      g.fillText(`R${rank.length - i}`, 44, y);
      g.textAlign = 'center';
      g.fillStyle = row.w ? '#f6d34c' : '#75828f';
      g.font = '800 32px system-ui, sans-serif';
      const st3 = row.stars | 0;
      g.fillText(st3 > 0 ? '★'.repeat(st3) : (row.w ? '★' : '—'), 256, y);
      g.textAlign = 'right';
      g.fillStyle = row.w ? '#7fb069' : '#c8ced4';
      g.font = '700 30px system-ui, sans-serif';
      g.fillText(String(row.score | 0), 468, y);
    });
    // bloque de RÉCORDS (datos reales del juego — mismo bloque que La Locura)
    g.strokeStyle = 'rgba(255,255,255,0.18)';
    g.beginPath(); g.moveTo(40, 446); g.lineTo(472, 446); g.stroke();
    {
      const st = (this.game.stats && this.game.stats.data) || null;
      const surv = this.game.survivalBest || 0;
      const recs = [
        st && st.bestRally > 0 ? tx('rec_rally', { n: st.bestRally }) : '',
        st && st.bestStreak > 0 ? tx('rec_streak', { n: st.bestStreak }) : '',
        surv > 0 ? tx('rec_surv', { n: surv }) : '',
      ].filter(Boolean);
      g.textAlign = 'left';
      g.font = '600 27px system-ui, sans-serif';
      recs.forEach((t2, i) => {
        const y = 484 + i * 44;
        g.fillStyle = i === 0 ? '#f6b73c' : '#c8ced4';
        g.fillText(t2, 48, y);
      });
    }
    g.strokeStyle = 'rgba(255,255,255,0.18)';
    g.beginPath(); g.moveTo(40, 648); g.lineTo(472, 648); g.stroke();
    g.textAlign = 'center';
    g.fillStyle = '#e2d6f6';
    g.font = '700 30px system-ui, sans-serif';
    g.fillText(tx('rank_tot', { n: c.wins || 0, b: c.best || 0 }), 256, 688);
    this.tex.needsUpdate = true;
  }
  hide() { if (this.group) this.group.visible = false; }
}

/* Letrero procedural de reserva para el cartel de superpoder (sin arte). */
function paintPowerBanner() {
  const W = 1024, H = 557;
  const cv = magiaCanvas(W, H);
  const c = cv.getContext('2d');
  c.clearRect(0, 0, W, H);
  const r = 54;
  c.beginPath();
  c.moveTo(r, 14); c.arcTo(W - 14, 14, W - 14, H - 14, r); c.arcTo(W - 14, H - 14, 14, H - 14, r);
  c.arcTo(14, H - 14, 14, 14, r); c.arcTo(14, 14, W - 14, 14, r);
  c.closePath();
  c.fillStyle = 'rgba(20,12,40,0.94)'; c.fill();
  c.strokeStyle = '#c9a6ff'; c.lineWidth = 12; c.stroke();
  c.fillStyle = '#f6d34c';
  for (const [x, y, s] of [[170, 430, 1.0], [860, 140, 0.9], [880, 420, 0.7], [150, 150, 0.7]]) {
    c.save(); c.translate(x, y); c.scale(s, s);
    c.beginPath();
    c.moveTo(0, -34); c.quadraticCurveTo(7, -7, 34, 0);
    c.quadraticCurveTo(7, 7, 0, 34);
    c.quadraticCurveTo(-7, 7, -34, 0);
    c.quadraticCurveTo(-7, -7, 0, -34);
    c.fill(); c.restore();
  }
  c.fillStyle = '#ffffff';
  c.textAlign = 'center'; c.textBaseline = 'middle';
  c.font = '900 118px system-ui, sans-serif';
  c.fillText('SUPERPODER', W / 2, 218);
  c.fillStyle = '#c9a6ff';
  c.font = '900 96px system-ui, sans-serif';
  c.fillText('DE WIZARD!!', W / 2, 350);
  return cv.toDataURL('image/png');
}

/* ============================================================================
 *  WizardPowerSign — cartel anclado a la cabeza (mecánica v2.40 intacta).
 *  v2.60: anuncia la PISTOLA MÁGICA al empezar el JUEGO (el arte real del
 *  artista superpoder.webp, mismo mecanismo de recorte transparente v2.59).
 *  ============================================================================ */
class WizardPowerSign {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    // v3.6.4-SDK4 · FASE 6: la fábrica del SDK (createPowerSign) sustituye
    // la copia — UNA sola fuente para el tablón de superpoder (WizardPowerSign).
    this._impl = createPowerSign(THREE, () => this.game, {
      coreo: 'clasica',
      arte: 'canvas1024',
      url: () => this.ctrl.manifest && this.ctrl.manifest.powerUrl,
      fallbackURL: () => paintPowerBanner(),
      dims: () => (window.__PP_CORE && window.__PP_CORE.DIMS) || null,
    });
    this.T_IN = this._impl.T_IN;
    this.T_HOLD = this._impl.T_HOLD;
    this.T_OUT = this._impl.T_OUT;
  }
  build() { this._impl.build(); }
  show(iconUrl) { this._impl.show(iconUrl); }
  hide() { this._impl.hide(); }
  update(dt) { this._impl.update(dt); }
  dispose() { this._impl.dispose(); }
  get group() { return this._impl.group; }   // acceso QA/interno (solo lectura)
}
/* ============================================================================
 *  WizardMap (v2.60) — el MISMO póster del artista anclado a la PARED
 *  IZQUIERDA, ahora con la ruta NUEVA de 2 paradas: ORBE MÁGICO → TROFEO.
 *  Mientras no haya trofeo, el anillo señala el ORBE y la casilla del
 *  TROFEO va tapada con el tapa.png de siempre. PERFECTAMENTE ESTÁTICO.
 *  ============================================================================ */
class WizardMap {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.t = 0;
    // nodos del camino EN PÍXELES DEL ARTE oficial (medidos sobre mapa.webp):
    // v2.137: ARTE NUEVO del dueño (mapa.png 1380×752, MISMO lienzo) — nodos
    // NUMERADOS con espiral azul (1/3/5 magos · 2/4 orbes; el 5 va en BURBUJA,
    // sin anillo) → centros re-medidos con Hough + bbox dorado + perfil radial
    // (r = 120 × banda/107,5 para que el anillo abrace el borde dorado) y las
    // tapas usan tx/ty/ts PROPIOS (centro y escala) para cubrir anillo +
    // espiral numerada ENTERAS (un dígito cortado por el medallón se lee roto).
    // 0 WIZARD Nv. 1 · 1 PRUEBA: ORBE · 2 WIZARD Nv. 2 ·
    // 3 PRUEBA: ORBE COMPLEJO · 4 WIZARD Nv. 3 (JEFE FINAL). Al final del
    // camino espera el TROFEO (Varita Dorada, nodo 4 vencido).
    this.nodesPx = [
      { x: 229,  y: 258, r: 126, kind: 'wizard', lvl: 1, tapa: false },  // WIZARD Nv. 1
      { x: 456,  y: 508, r: 131, kind: 'orbe', lvl: 1, tapa: true,      // PRUEBA: ORBE
        tx: 456, ty: 490, ts: 1.18 },
      { x: 701,  y: 253, r: 122, kind: 'wizard', lvl: 2, tapa: true,    // WIZARD Nv. 2
        tx: 701, ty: 220, ts: 1.20 },
      { x: 966,  y: 506, r: 132, kind: 'orbe', lvl: 2, tapa: true,      // PRUEBA: ORBE COMPLEJO
        tx: 966, ty: 477, ts: 1.25 },
      { x: 1232, y: 162, r: 126, kind: 'wizard', lvl: 3, tapa: true,    // WIZARD Nv. 3 (final)
        tx: 1205, ty: 150, ts: 1.22 },
    ];
    this.currentIdx = 0;
    this.IMG_W = 1380;
    this.IMG_H = 752;
    this.PW = 1.68;
    this.PH = 1.68 * 752 / 1380;
    this.TAPA_W = 290 / 1380 * this.PW;
    this.TAPA_H = 300 / 752 * this.PH;
  }

  build() {
    if (this.inited) return;
    this.inited = true;
    this.group = new THREE.Group();
    const back = new THREE.Mesh(
      new THREE.BoxGeometry(this.PW + 0.06, this.PH + 0.06, 0.022),
      new THREE.MeshStandardMaterial({ color: 0x1a1424, roughness: 0.85, metalness: 0.1 }),
    );
    back.position.z = -0.013;
    this.group.add(back);
    this.plane = new THREE.Mesh(
      new THREE.PlaneGeometry(this.PW, this.PH),
      new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, opacity: 0 }),
    );
    this.group.add(this.plane);
    const murl = (this.ctrl.manifest && this.ctrl.manifest.mapUrl) || '';
    if (murl) {
      new THREE.TextureLoader().load(murl, (tex) => {
        tex.colorSpace = THREE.SRGBColorSpace;
        if (this.plane) {
          this.plane.material.map = tex;
          this.plane.material.opacity = 1;
          this.plane.material.needsUpdate = true;
        }
      });
    }
    this.tapas = [];
    this.tapasReady = false;
    const turl = (this.ctrl.manifest && this.ctrl.manifest.tapaUrl) || '';
    if (turl) {
      new THREE.TextureLoader().load(turl, (tex) => {
        tex.colorSpace = THREE.SRGBColorSpace;
        this.nodesPx.forEach((n, i) => {
          if (!n.tapa) return;
          // v2.137: la tapa puede llevar CENTRO y ESCALA propios (tx/ty/ts) —
          // en el arte nuevo la espiral numerada sube el punto de cobertura.
          const s = n.ts || n.tapaScale || 1;
          const m = new THREE.Mesh(
            new THREE.PlaneGeometry(this.TAPA_W * s, this.TAPA_H * s),
            new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }),
          );
          const p = this._pxToLocal(
            (n.tx !== undefined) ? n.tx : n.x,
            (n.ty !== undefined) ? n.ty : n.y,
          );
          m.position.set(p[0], p[1], 0.003);
          m.renderOrder = 2;
          this.group.add(m);
          this.tapas.push({ idx: i, mesh: m });
        });
        this.tapasReady = true;
        this.refresh();
      });
    }
    this.marker = new THREE.Mesh(
      new THREE.RingGeometry(0.118, 0.144, 48),
      new THREE.MeshBasicMaterial({
        color: 0xf6d34c, transparent: true, depthWrite: false,
        side: THREE.DoubleSide,
      }),
    );
    this.marker.material.opacity = 0.9;
    this.marker.position.z = 0.006;
    this.marker.renderOrder = 3;
    this.group.add(this.marker);
    this.group.position.set(-2.98, 1.5, -0.9);
    this.group.rotation.y = Math.PI / 2;
    this.group.visible = false;
    this.game.rig.add(this.group);
    this.refresh();
  }

  _pxToLocal(px, py) {
    return [(px / this.IMG_W - 0.5) * this.PW, (0.5 - py / this.IMG_H) * this.PH];
  }

  /** Nodo actual: campeón = ruta completa sin anillo; si no, la etapa del
   *  camino (0–4) señala el reto actual (v2.70: ruta de 5 etapas). */
  _computeCurrent() {
    if (this.ctrl && this.ctrl.trophy) return -1;
    return Math.min(Math.max((this.ctrl && this.ctrl.stage) | 0, 0), 4);
  }

  refresh() {
    if (!this.group) return;
    this.currentIdx = this._computeCurrent();
    const champion = this.currentIdx < 0;
    if (this.tapas && this.tapas.length) {
      for (const t of this.tapas) {
        // v2.108: en MODO DEPURACIÓN todas las tapas levantadas — las 5
        // etapas son visibles y apuntables con la pala desde el principio.
        t.mesh.visible = !champion && !ppDbg() && this.currentIdx < t.idx;
      }
    }
    if (this.marker) {
      this.marker.material.color.setHex(0xf6d34c);   // v2.96: dorado de nuevo
      this.marker.visible = !champion;
      if (!champion) {
        const n = this.nodesPx[this.currentIdx];
        const p = this._pxToLocal(n.x, n.y);
        this.marker.position.x = p[0];
        this.marker.position.y = p[1];
        this.marker.scale.setScalar(n.r / 120);
      }
    }
  }

  /** v2.96 · REJUGAR: resalta el nodo apuntado con la pala (azul y algo
   *  mayor); -1 devuelve el anillo dorado al nodo actual. */
  hover(idx) {
    if (!this.marker) return;
    if (idx < 0 || idx >= this.nodesPx.length) { this.refresh(); return; }
    const n = this.nodesPx[idx];
    const p = this._pxToLocal(n.x, n.y);
    this.marker.visible = true;
    this.marker.material.color.setHex(0x7ec8ff);
    this.marker.position.x = p[0];
    this.marker.position.y = p[1];
    this.marker.scale.setScalar((n.r / 120) * 1.22);
  }

  update() {
    /* estático a propósito (v2.37) */
  }

  hide() { if (this.group) this.group.visible = false; }
}

/* ============================================================================
 *  OrbeMagico (v2.60) — EL NIVEL NUEVO. Máquina de estados:
 *    intro → montaje → play (con sub-estado de ALERTA FINAL) → result.
 *  Toma el control de la física vía testStep() mientras active (igual que
 *  ARKANOID en La Locura): el árbitro duerme con rules.state='champtest'.
 *  ============================================================================ */
class OrbeMagico {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.active = false;
    this.inited = false;
    this.phase = 'idle';
    this.phaseT = 0;
    this._complex = false;                      // v2.70: prueba COMPLEJA (etapa 4)
    this.L = this.buildCfg();                   // v2.70: NORMAL o COMPLEJO
    // rejilla
    this.R = 0; this.S = 0; this.cells = 0;
    this.cellKey = null;      // Int32Array (2R+1)^3 → índice de celda o -1
    this.ci = null; this.cj = null; this.ck = null;      // Int8/Int16Array
    this.layer = null; this.alive = null; this.exposed = null;
    this.wx = null; this.wy = null; this.wz = null;      // posición mundo
    this.totalBricks = 0; this.aliveBricks = 0;
    this.aliveByLayer = [0, 0, 0];
    this.coreIdx = [];        // celdas de capa 0 (glow)
    this.shellIdx = [];       // celdas de capas 1-2
    this.coreMap = null; this.shellMap = null;           // celda→instancia
    this.maxScore = 1;
    // GPU
    this.brickMesh = null; this.coreMesh = null;
    this.brickGeo = null; this.coreGeo = null;
    this.brickMat = null; this.coreMat = null;
    this._m4 = new THREE.Matrix4();
    this._col = new THREE.Color();
    // estado de juego
    this.time = 0;
    this.score = 0;
    this.extUsed = 0;
    this.montajeT = 0;
    this.montajeSkipped = false;
    this._anim = null;        // Float32Array [t0, dur] por celda
    this._layerDone = [false, false, false];
    // bolas
    this.balls = [];
    this.spawnCd = 0;
    // alerta / prórroga
    this.block = null;
    this.retryCd = 0;
    this._noExtAnnounced = false;
    // pistola
    this._beams = [];
    this._gunLast = 0;
    this._gunHintDone = false;
    this._gunArt = [];        // clones del modelo del artista en las monturas
    this._gunArtModel = null; // escena GLB cargada (caché)
    this._gunArtLoading = false;
    // fx
    this._debris = [];
    this._flashes = [];
    this._miniPortals = [];
    this._lastChainMsg = 0;
    this._hudDirty = true;
    this._msg = '';
    this._msgT = 0;
    this._lastSec = -1;
    this._warned = false;
    this._lastBreakSnd = 0;
    this._tokCd = 0;
    // temps (sin GC en el bucle)
    this._tA = new THREE.Vector3();
    this._tB = new THREE.Vector3();
    this._tC = new THREE.Vector3();
    this._tD = new THREE.Vector3();
    this._extra = (ball) => this._collide(ball);
    this._netParts = null;
  }

  get center() { return this._center; }

  /** v2.70 · cfg del nivel: NORMAL o COMPLEJO (etapa 4 del camino — OTRO
   *  orbe: ladrillos más finos y una capa exterior más, sin prórrogas). */
  buildCfg() {
    return this._complex ? Object.assign({}, LEVEL, ORBE_COMPLEJO)
                         : Object.assign({}, LEVEL);
  }
  applyComplexity(complex) {
    const changed = this.inited && (!!complex !== this._complex);
    this._complex = !!complex;
    this.L = this.buildCfg();
    if (changed) this.dispose();   // reconstruye con la rejilla nueva en start()
  }

  /* --------------------------------- escena -------------------------------- */
  build() {
    if (this.inited) return;
    this.inited = true;
    const g = this.game;
    const L = this.L;
    SC = sceneConfig();
    // RESET de pools (el nivel puede reconstruirse tras un dispose)
    this.balls = [];
    this._miniPortals = [];
    this._debris = [];
    this._flashes = [];
    this._beams = [];
    // v2.71 · CENTRO DEL ORBE DERIVADO del cfg activo: la celda más baja
    // (floor(radiusOuter)·brickSize por debajo del centro) apoya su cara
    // inferior en el tablero (topY) — la bola rastrera entra en la celda
    // inferior y NO pasa por debajo, con la rejilla NORMAL y con la COMPLEJA.
    const reach = Math.floor(L.radiusOuter);
    this._center = new THREE.Vector3(
      0,
      SC.topY + reach * L.brickSize + L.brickSize / 2,
      SC.orb.z,
    );
    this.fieldGroup = new THREE.Group();
    this.hudGroup = new THREE.Group();
    this.fxGroup = new THREE.Group();
    g.rig.add(this.fieldGroup);
    g.rig.add(this.hudGroup);
    g.rig.add(this.fxGroup);

    /* --- CORREDOR: la mesa se alarga hasta la pared del fondo --- */
    // suelo del corredor (continuación de la mesa, mismo grosor y altura)
    const corrLen = SC.tableNearZ - SC.corridorZ1;               // hasta -0.23→-5.40
    this.floorMesh = new THREE.Mesh(
      new THREE.BoxGeometry(SC.halfW * 2, DIMS.tableThickness, corrLen - (SC.tableNearZ - SC.corridorZ0)),
      new THREE.MeshStandardMaterial({ color: 0x2f3138, roughness: 0.82, metalness: 0.05 }),
    );
    const flZ = (SC.corridorZ1 + SC.corridorZ0) / 2;
    this.floorMesh.position.set(0, SC.topY - DIMS.tableThickness / 2, flZ);
    this.fieldGroup.add(this.floorMesh);
    // cristales mágicos laterales (campo de fuerza del corredor)
    this.glassMat = new THREE.MeshStandardMaterial({
      color: 0x9a7ae8, transparent: true, opacity: 0.22,
      roughness: 0.3, metalness: 0.05, side: THREE.DoubleSide, depthWrite: false,
    });
    const midZ = (SC.tableNearZ + SC.corridorZ1) / 2;
    const wallLen = SC.tableNearZ - SC.corridorZ1;
    for (const sx of [-1, 1]) {
      const glass = new THREE.Mesh(new THREE.PlaneGeometry(wallLen, SC.wallH), this.glassMat);
      glass.rotation.y = sx * Math.PI / 2;
      glass.position.set(sx * SC.halfW, SC.topY + SC.wallH / 2, midZ);
      this.fieldGroup.add(glass);
      const edge = new THREE.Mesh(
        new THREE.BoxGeometry(0.025, 0.025, wallLen),
        new THREE.MeshBasicMaterial({ color: 0xc9a6ff, transparent: true, opacity: 0.5, depthWrite: false }),
      );
      edge.position.set(sx * SC.halfW, SC.topY + SC.wallH, midZ);
      this.fieldGroup.add(edge);
    }
    // estrellitas tenues sobre el corredor nuevo (temática de la mesa)
    this._corrStars = [];
    {
      const tex = starTextureMagia();
      this._corrStarTex = tex;
      for (let i = 0; i < 8; i++) {
        const mat = new THREE.MeshBasicMaterial({
          map: tex, transparent: true, depthWrite: false,
          blending: THREE.AdditiveBlending, opacity: 0,
        });
        const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat);
        m.rotation.x = -Math.PI / 2;
        m.renderOrder = 3;
        m.position.set(
          (Math.random() * 2 - 1) * (SC.halfW - 0.15),
          SC.topY + 0.006,
          SC.corridorZ0 - 0.3 - Math.random() * (SC.corridorZ0 - SC.corridorZ1 - 0.6),
        );
        m.scale.setScalar(0.08 + Math.random() * 0.1);
        this.fieldGroup.add(m);
        this._corrStars.push({ mesh: m, mat, phase: Math.random() * 6.28, spd: 0.4 + Math.random() * 0.5, base: 0.22 + Math.random() * 0.16 });
      }
    }

    /* --- PORTAL del fondo (arte real del artista, portals.webp) --- */
    const P = SC.portal;
    this.portalGroup = new THREE.Group();
    this.portalGroup.position.set(P.x, P.y, P.z);
    // v2.61: agujero y anillo giran JUNTOS en un mismo nodo (antes el disco
    // quieto «competía» con el anillo y el efecto se veía roto); el glow es
    // un sprite radial y queda fuera del giro.
    this.portalSpin = new THREE.Group();
    this.portalGroup.add(this.portalSpin);
    // disco oscuro detrás del anillo (el «agujero» del portal)
    const hole = new THREE.Mesh(
      new THREE.CircleGeometry(P.size * 0.42, 40),
      new THREE.MeshBasicMaterial({ color: 0x140a24 }),
    );
    hole.position.z = -0.012;
    this.portalSpin.add(hole);
    // anillo de fuego giratorio
    this.portalRingMat = new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, side: THREE.DoubleSide, opacity: 0,
    });
    this.portalRing = new THREE.Mesh(new THREE.PlaneGeometry(P.size, P.size), this.portalRingMat);
    this.portalRing.renderOrder = 8;
    this.portalSpin.add(this.portalRing);
    this._portalSpeed = P.rotSpeed;
    // glow cálido alrededor
    this._softTex = softTexture();
    this.portalGlowMat = new THREE.SpriteMaterial({
      map: this._softTex, color: 0xffb45e, transparent: true,
      blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0,
    });
    this.portalGlow = new THREE.Sprite(this.portalGlowMat);
    this.portalGlow.scale.setScalar(P.size * 1.35);
    this.portalGroup.add(this.portalGlow);
    this.portalLight = new THREE.PointLight(0xffb45e, 0, 4.5);
    this.portalGroup.add(this.portalLight);
    this.fieldGroup.add(this.portalGroup);
    const pimg = new Image();
    pimg.onload = () => {
      const t = new THREE.Texture();
      t.colorSpace = THREE.SRGBColorSpace;
      t.image = pimg; t.needsUpdate = true;
      this.portalRingMat.map = t;
      this.portalRingMat.opacity = 1;
      this.portalRingMat.needsUpdate = true;
      this.portalGlowMat.opacity = 0.4;
      this.portalLight.intensity = 1.1;
    };
    pimg.src = this.ctrl.manifest.portalsUrl || '';

    /* --- REJILLA del orbe --- */
    this._buildGrid();
    this._buildInstances();

    // luz cálida del núcleo (el amarillo «brilla» sin emisivo por instancia)
    this.coreLight = new THREE.PointLight(0xffd76e, 1.3, 2.4);
    this.coreLight.position.copy(this._center);
    this.fieldGroup.add(this.coreLight);
    // v2.61: pistola del ARTISTA (pistol.glb) en la mano libre
    this._loadGunArt();

    /* --- HUD + cartel de resultados --- */
    this.hudCv = magiaCanvas(1024, 214);
    this.hudTex = new THREE.CanvasTexture(this.hudCv);
    this.hudTex.colorSpace = THREE.SRGBColorSpace;
    this.hudPlane = new THREE.Mesh(
      new THREE.PlaneGeometry(1.9, 1.9 * 214 / 1024),
      new THREE.MeshBasicMaterial({ map: this.hudTex, transparent: true, depthWrite: false }),
    );
    this.hudPlane.position.set(0, SC.hud.y, SC.hud.z);
    this.hudGroup.add(this.hudPlane);

    this.banCv = magiaCanvas(1024, 400);
    this.banTex = new THREE.CanvasTexture(this.banCv);
    this.banTex.colorSpace = THREE.SRGBColorSpace;
    this.banPlane = new THREE.Mesh(
      new THREE.PlaneGeometry(1.9, 1.9 * 400 / 1024),
      new THREE.MeshBasicMaterial({ map: this.banTex, transparent: true, depthWrite: false }),
    );
    this.banPlane.position.set(0, SC.ban.y, SC.ban.z);
    this.hudGroup.add(this.banPlane);

    /* --- FX v2.63: ESCOMBROS EN CUBITOS + flashes de luz ---------------- */
    // pool de cubitos (estilo La Locura): gravedad real, giro y encogido;
    // cada cubito hereda el MATERIAL de la capa del ladrillo roto.
    const dGeo = new THREE.BoxGeometry(0.05, 0.05, 0.05);
    for (let i = 0; i < 48; i++) {
      const m = new THREE.Mesh(dGeo, this._debrisMats ? this._debrisMats[2] : null);
      m.visible = false;
      this.fxGroup.add(m);
      this._debris.push({ mesh: m, vel: new THREE.Vector3(), life: 0 });
    }
    // flashes aditivos (sprites radiales SIEMPRE de cara al jugador)
    for (let i = 0; i < 6; i++) {
      const m = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this._softTex, color: 0xffc27a, transparent: true, opacity: 0,
        blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      m.visible = false;
      this.fxGroup.add(m);
      this._flashes.push({ mesh: m, life: 0 });
    }
    // v2.65: BRASA de la BOLA NEGRA (1 por slot) — sigue a la bola y pulsa;
    // vive en fxGroup → dispose() la libera con el resto.
    this._bombGlows = [];
    this._bombGlowT = 0;
    for (let i = 0; i < this.L.maxBalls; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this._softTex, color: 0xc23bff, transparent: true, opacity: 0,
        blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      s.visible = false;
      s.scale.setScalar(0.22);
      this.fxGroup.add(s);
      this._bombGlows.push(s);
    }

    /* --- BLOQUE RELOJ (prórroga) — v2.61: icono reloj.png del artista --- */
    this.blockGroup = new THREE.Group();
    const bMat = new THREE.MeshStandardMaterial({
      color: 0x0d0d12, roughness: 0.4, metalness: 0.15,
      emissive: 0x332200, emissiveIntensity: 0.5,
    });
    this.blockMesh = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.3, 0.3), bMat);
    this.blockGroup.add(this.blockMesh);
    // el ICONO va pegado a las 4 caras laterales (el cubo gira sobre Y);
    // textura procedural de reserva hasta que cargue reloj.png (o si falla)
    this._clockTex = clockTexture();
    this._relojTex = null;
    this._blockIcons = [];
    for (let f = 0; f < 4; f++) {
      const icon = new THREE.Mesh(
        new THREE.PlaneGeometry(0.24, 0.24),
        new THREE.MeshBasicMaterial({
          map: this._clockTex, transparent: true, alphaTest: 0.08,
          depthWrite: false, toneMapped: false,
        }),
      );
      icon.renderOrder = 2;
      if (f === 0) { icon.position.z = 0.1512; }
      else if (f === 1) { icon.position.z = -0.1512; icon.rotation.y = Math.PI; }
      else if (f === 2) { icon.position.x = 0.1512; icon.rotation.y = Math.PI / 2; }
      else { icon.position.x = -0.1512; icon.rotation.y = -Math.PI / 2; }
      this.blockMesh.add(icon);
      this._blockIcons.push(icon);
    }
    if (this.ctrl.manifest.relojUrl) {
      const rimg = new Image();
      rimg.onload = () => {
        const t = new THREE.Texture();
        t.colorSpace = THREE.SRGBColorSpace;
        t.image = rimg; t.needsUpdate = true;
        this._relojTex = t;
        for (const ic of this._blockIcons) {
          ic.material.map = t;
          ic.material.needsUpdate = true;
        }
      };
      rimg.src = this.ctrl.manifest.relojUrl;
    }
    this.blockGlow = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this._softTex, color: 0xf6d34c, transparent: true,
      blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.55,
    }));
    this.blockGlow.scale.setScalar(0.85);
    this.blockGroup.add(this.blockGlow);
    this.blockGroup.visible = false;
    this.fieldGroup.add(this.blockGroup);

    /* --- MINI-PORTALES de nacimiento de bolas (uno por hueco del pool) --- */
    for (let i = 0; i < this.L.maxBalls; i++) {
      const grp = new THREE.Group();
      const ring = new THREE.Mesh(
        new THREE.PlaneGeometry(0.38, 0.38),
        new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide, opacity: 0 }),
      );
      // v2.61: vórtice PARALELO a la mesa (disco horizontal, un pelín por
      // encima de la superficie) y SIEMPRE junto al borde del jugador
      ring.rotation.x = -Math.PI / 2;
      // MISMO arte del artista (portals.webp) que el portal del fondo
      const mimg = new Image();
      mimg.onload = () => {
        const t = new THREE.Texture();
        t.colorSpace = THREE.SRGBColorSpace;
        t.image = mimg; t.needsUpdate = true;
        ring.material.map = t;
        ring.material.needsUpdate = true;
      };
      mimg.src = this.ctrl.manifest.portalsUrl || '';
      grp.add(ring);
      const glow = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this._softTex, color: 0xffb45e, transparent: true,
        blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0,
      }));
      glow.scale.setScalar(0.55);
      grp.add(glow);
      grp.visible = false;
      g.rig.add(grp);
      this._miniPortals.push({ grp, ring, glow, t: -1, ballDelay: 0, slot: i });
    }

    /* --- BOLAS (pool) --- */
    this._softTex2 = this._softTex;   // misma textura para estelas
    const trailTex = this._softTex;
    for (let i = 0; i < this.L.maxBalls; i++) {
      const col = SC.ballColors[i % SC.ballColors.length];
      const b = {
        slot: i,
        active: false,        // en juego
        waiting: false,       // esperando respawn
        portalT: -1,          // animación de portal en curso
        pos: new THREE.Vector3(), vel: new THREE.Vector3(), spin: new THREE.Vector3(),
        ignoreNet: true,
        color: col,
        mesh: null,
        evs: [],
        stuckT: 0,
        trailT: 0,
        trail: [],
        __exPrev: new THREE.Vector3(),
        // v2.61: bote EN ESPERA (la bola bota en el vórtice hasta el golpe)
        hold: false, holdT: 0, holdX: 0, holdZ: 0, holdBaseY: 0,
        // v2.65: BOLA NEGRA (bomba) + guardia anti-bote-en-el-sitio
        bomb: false, _farT: 0,
      };
      if (i === 0) {
        b.isMain = true;      // usa g.ball / g.ballMesh del núcleo (ALIAS vivo)
        b.pos = g.ball.pos;
        b.vel = g.ball.vel;
        b.spin = g.ball.spin;
      } else {
        const mesh = new THREE.Mesh(
          new THREE.SphereGeometry(DIMS.ballRadius + 0.006, 14, 10),
          new THREE.MeshStandardMaterial({ color: col, roughness: 0.3, metalness: 0.05, emissive: col, emissiveIntensity: 0.25 }),
        );
        mesh.visible = false;
        g.rig.add(mesh);          // v2.62: mismo espacio que la física (rig)
        b.mesh = mesh;
      }
      for (let k = 0; k < 10; k++) {
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({
          map: trailTex, color: col, transparent: true,
          blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0,
        }));
        sp.visible = false;
        sp.scale.setScalar(0.09);
        g.rig.add(sp);            // v2.62: estelas también en el rig
        b.trail.push({ sp, life: 0 });
      }
      this.balls.push(b);
    }
  }

  /* --------------------------- rejilla del orbe ---------------------------- */
  _buildGrid() {
    const L = this.L;
    const R = Math.ceil(L.radiusOuter);
    this.R = R;
    this.S = 2 * R + 1;
    const S = this.S;
    // RESET COMPLETO (la rejilla puede reconstruirse tras un dispose)
    this.totalBricks = 0;
    this.aliveBricks = 0;
    this.aliveByLayer = [0, 0, 0];
    this.coreIdx = [];
    this.shellIdx = [];
    this.cellKey = new Int32Array(S * S * S).fill(-1);
    const ci = [], cj = [], ck = [], cl = [];
    const rC = L.radiusCore + 1e-4, rM = L.radiusMid + 1e-4, rO = L.radiusOuter + 1e-4;
    for (let x = -R; x <= R; x++) {
      for (let y = -R; y <= R; y++) {
        for (let z = -R; z <= R; z++) {
          const d = Math.sqrt(x * x + y * y + z * z);
          let layer = -1;
          if (d <= rC) layer = 0;
          else if (d <= rM) layer = 1;
          else if (d <= rO) layer = 2;
          if (layer < 0) continue;
          const key = (x + R) * S * S + (y + R) * S + (z + R);
          this.cellKey[key] = ci.length;
          ci.push(x); cj.push(y); ck.push(z); cl.push(layer);
        }
      }
    }
    this.cells = ci.length;
    this.ci = Int16Array.from(ci); this.cj = Int16Array.from(cj); this.ck = Int16Array.from(ck);
    this.layer = Uint8Array.from(cl);
    this.alive = new Uint8Array(this.cells).fill(1);
    this.exposed = new Uint8Array(this.cells);
    this.wx = new Float32Array(this.cells);
    this.wy = new Float32Array(this.cells);
    this.wz = new Float32Array(this.cells);
    const BR = L.brickSize;
    const cx = this._center.x, cy = this._center.y, cz = this._center.z;
    const N6 = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
    for (let i = 0; i < this.cells; i++) {
      this.wx[i] = cx + this.ci[i] * BR;
      this.wy[i] = cy + this.cj[i] * BR;
      this.wz[i] = cz + this.ck[i] * BR;
      let exp = false;
      for (const [dx, dy, dz] of N6) {
        const nx = this.ci[i] + dx, ny = this.cj[i] + dy, nz = this.ck[i] + dz;
        if (Math.abs(nx) > R || Math.abs(ny) > R || Math.abs(nz) > R) { exp = true; break; }
        const k2 = (nx + R) * S * S + (ny + R) * S + (nz + R);
        if (this.cellKey[k2] < 0) { exp = true; break; }
      }
      this.exposed[i] = exp ? 1 : 0;
      this.totalBricks++;
      this.aliveByLayer[this.layer[i]]++;
      (this.layer[i] === 0 ? this.coreIdx : this.shellIdx).push(i);
    }
    this.aliveBricks = this.totalBricks;
    // mapa celda→instancia (dos InstancedMesh: glow del núcleo + ladrillos)
    this.coreMap = new Int32Array(this.cells).fill(-1);
    this.shellMap = new Int32Array(this.cells).fill(-1);
    this.coreIdx.forEach((c, i) => { this.coreMap[c] = i; });
    this.shellIdx.forEach((c, i) => { this.shellMap[c] = i; });
    // puntos por capa y tope de sanidad del marcador
    const pts = L.layerPoints;
    let base = 0;
    for (let l = 0; l < 3; l++) base += this.aliveByLayer[l] * (pts[l] || 10);
    this.maxScore = base + this.totalBricks * (L.chainBonus || 5);
  }

  _buildInstances() {
    const g = this.game;
    const BR = this.L.brickSize;
    const edge = BR * 0.94;   // ranura fina entre ladrillos
    this.brickGeo = new THREE.BoxGeometry(edge, edge, edge);
    this.coreGeo = new THREE.BoxGeometry(edge, edge, edge);
    // v2.63: BISEL + MARCO (textura gris × color de instancia) — adiós al
    // ladrillo plano; mismo truco que el muro del ARKANOID de La Locura.
    this._bevelTex = brickBevelTexture();
    this.brickMat = new THREE.MeshStandardMaterial({
      color: 0xffffff, map: this._bevelTex, roughness: 0.48, metalness: 0.08,
    });
    this.coreMat = new THREE.MeshBasicMaterial({ color: 0xffdf6e, map: this._bevelTex });
    // v2.63: materiales de los ESCOMBROS (cubitos del color de SU capa)
    this._debrisMats = [
      new THREE.MeshStandardMaterial({ color: 0xffd257, map: this._bevelTex, roughness: 0.4, metalness: 0.05, emissive: 0x553c00, emissiveIntensity: 0.55 }),
      new THREE.MeshStandardMaterial({ color: 0x9a6438, map: this._bevelTex, roughness: 0.5, metalness: 0.06 }),
      new THREE.MeshStandardMaterial({ color: 0xd23a2a, map: this._bevelTex, roughness: 0.48, metalness: 0.08 }),
    ];
    this.brickMesh = new THREE.InstancedMesh(this.brickGeo, this.brickMat, this.shellIdx.length);
    this.coreMesh = new THREE.InstancedMesh(this.coreGeo, this.coreMat, this.coreIdx.length);
    this.brickMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    this.coreMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    this.brickMesh.frustumCulled = false;
    this.coreMesh.frustumCulled = false;
    // color por instancia con ligera variación de tono (textura visual)
    // v2.63: algo más CLAROS para compensar el bisel gris de la textura
    const mid = new THREE.Color(0xa06a3c);
    const out = new THREE.Color(0xe0432f);
    for (let i = 0; i < this.shellIdx.length; i++) {
      const c = this.shellIdx[i];
      const base = this.layer[c] === 1 ? mid : out;
      const v = 0.9 + Math.random() * 0.2;
      this._col.setRGB(base.r * v, base.g * v, base.b * v);
      this.brickMesh.setColorAt(i, this._col);
    }
    if (this.brickMesh.instanceColor) this.brickMesh.instanceColor.needsUpdate = true;
    // todo oculto hasta el MONTAJE
    this._m4.makeScale(0, 0, 0);
    for (let i = 0; i < this.shellIdx.length; i++) this.brickMesh.setMatrixAt(i, this._m4);
    for (let i = 0; i < this.coreIdx.length; i++) this.coreMesh.setMatrixAt(i, this._m4);
    this.brickMesh.instanceMatrix.needsUpdate = true;
    this.coreMesh.instanceMatrix.needsUpdate = true;
    // v2.62 · FIX CRÍTICO: los ladrillos van al RIG (no a la escena). Las
    // matrices de instancia están en coordenadas del RIG (el espacio de la
    // mesa); con el recentrado de la Quest rig.rotation.y ≠ 0 y en la escena
    // el orbe aparecía FUERA de la mesa, desalineado del corredor.
    g.rig.add(this.brickMesh);
    g.rig.add(this.coreMesh);
  }

  /** Escribe la matriz de UNA celda en su InstancedMesh. */
  _writeCell(c, scale) {
    this._m4.makeScale(scale, scale, scale);
    this._m4.setPosition(this.wx[c], this.wy[c], this.wz[c]);
    if (this.layer[c] === 0) {
      const inst = this.coreMap[c];
      if (inst >= 0) { this.coreMesh.setMatrixAt(inst, this._m4); this.coreMesh.instanceMatrix.needsUpdate = true; }
    } else {
      const inst = this.shellMap[c];
      if (inst >= 0) { this.brickMesh.setMatrixAt(inst, this._m4); this.brickMesh.instanceMatrix.needsUpdate = true; }
    }
  }

  /** Escribe la matriz de una celda en una posición INTERMEDIA (montaje). */
  _writeCellAt(c, x, y, z, scale) {
    this._m4.makeScale(scale, scale, scale);
    this._m4.setPosition(x, y, z);
    if (this.layer[c] === 0) {
      const inst = this.coreMap[c];
      if (inst >= 0) { this.coreMesh.setMatrixAt(inst, this._m4); this.coreMesh.instanceMatrix.needsUpdate = true; }
    } else {
      const inst = this.shellMap[c];
      if (inst >= 0) { this.brickMesh.setMatrixAt(inst, this._m4); this.brickMesh.instanceMatrix.needsUpdate = true; }
    }
  }

  /* ------------------------------ montaje ---------------------------------- */
  _startMontaje() {
    const L = this.L;
    this.phase = 'montaje';
    this.montajeT = 0;
    this.montajeSkipped = false;
    this._layerDone = [false, false, false];
    const T = Math.max(5, Math.min(8, L.montajeTime));
    this._montajeDur = T;
    // ventanas por capa: núcleo → medio → exterior (con pequeño solape)
    const w0 = [0, 0.28 * T, 0.60 * T];
    const w1 = [0.28 * T, 0.60 * T, T];
    this._anim = new Float32Array(this.cells * 2);
    for (let c = 0; c < this.cells; c++) {
      const l = this.layer[c];
      const dur = 0.5;
      const span = Math.max(0.05, (w1[l] - w0[l]) - dur);
      const t0 = w0[l] + Math.random() * span;
      this._anim[c * 2] = t0;
      this._anim[c * 2 + 1] = dur;
      this._writeCell(c, 0);      // oculto hasta que llegue su turno
    }
    this._montajeFrom = new Float32Array(this.cells * 3);
    const P = SC.portal;
    for (let c = 0; c < this.cells; c++) {
      this._montajeFrom[c * 3] = P.x + (Math.random() - 0.5) * 0.5;
      this._montajeFrom[c * 3 + 1] = P.y + (Math.random() - 0.5) * 0.5;
      this._montajeFrom[c * 3 + 2] = P.z + 0.1 + Math.random() * 0.3;
    }
    this._msg = tx('montaje_hint');
    this._msgT = 3.2;
    this._hudDirty = true;
    this._sndMontaje(0);
    this.ctrl._setStateSilent('focused', 0);
  }

  _sndMontaje(layer) {
    const g = this.game;
    if (!g.audio || !g.audio.playOsc) return;
    const O = (f1, f2, d, vol, dl, type) => {
      try { g.audio.playOsc(f1, f2, d, type || 'sine', vol, dl); } catch (e) { /* */ }
    };
    // whoosh de capa + acorde que SUBE con cada capa (núcleo→medio→exterior)
    const f = [392, 523, 659][layer] || 523;
    O(160, 640, 0.5, 0.1, 0, 'sine');
    O(f, f, 0.14, 0.11, 0.12, 'triangle');
    O(f * 1.25, f * 1.25, 0.14, 0.11, 0.26, 'triangle');
    O(f * 1.5, f * 1.5, 0.3, 0.12, 0.4, 'triangle');
  }

  _montajeStep(dt) {
    const T = this._montajeDur;
    this.montajeT += dt;
    const t = this.montajeT;
    const marks = [0.28 * T, 0.60 * T, T];
    for (let l = 0; l < 3; l++) {
      if (!this._layerDone[l] && t >= marks[l]) {
        this._layerDone[l] = true;
        this._sndMontaje(l + 1);   // jingle de capa completada (sube el tono)
      }
    }
    // v2.61: el giro del portal vive en _anims() (antes se congelaba al
    // acabar el montaje: ¡el portal dejaba de girar en plena partida!)
    this._portalSpeed = (t < T) ? 2.2 : SC.portal.rotSpeed;
    let allDone = true;
    for (let c = 0; c < this.cells; c++) {
      const t0 = this._anim[c * 2], dur = this._anim[c * 2 + 1];
      if (t < t0) { allDone = false; continue; }
      let p = (t - t0) / dur;
      if (p >= 1) {
        if (this._anim[c * 2 + 1] > 0) {   // aún no asentado: escribe final UNA vez
          this._anim[c * 2 + 1] = 0;
          this._writeCellAt(c, this.wx[c], this.wy[c], this.wz[c], 1);
        }
        continue;
      }
      allDone = false;
      const k = 1 - Math.pow(1 - p, 3);    // easeOutCubic
      const x = this._montajeFrom[c * 3] + (this.wx[c] - this._montajeFrom[c * 3]) * k;
      const y = this._montajeFrom[c * 3 + 1] + (this.wy[c] - this._montajeFrom[c * 3 + 1]) * k;
      const z = this._montajeFrom[c * 3 + 2] + (this.wz[c] - this._montajeFrom[c * 3 + 2]) * k;
      this._writeCellAt(c, x, y, z, 0.25 + 0.75 * k);
    }
    if (t >= T + 0.15 || this.montajeSkipped) {
      // asienta TODO y aplica el CULLING de expuestos (sólo se ven los
      // ladrillos con algún vecino vacío)
      for (let c = 0; c < this.cells; c++) {
        this._writeCellAt(c, this.wx[c], this.wy[c], this.wz[c],
          this.exposed[c] ? 1 : 0);
      }
      this._startJuego();
      return;
    }
  }

  _skipMontaje() {
    if (this.phase !== 'montaje') return;
    this.montajeSkipped = true;
  }

  /* ------------------------------- JUEGO ----------------------------------- */
  _startJuego() {
    const g = this.game;
    this.phase = 'play';
    this.time = this.L.timeStart;
    this._lastSec = Math.ceil(this.time) + 1;
    this._warned = false;
    this.score = 0;
    this.extUsed = 0;
    this._noExtAnnounced = false;
    this.retryCd = 0;
    this.spawnCd = 0.6;
    this._msg = tx('play_hint');
    this._msgT = 3.0;
    this._hudDirty = true;
    // pistola lista en la mano libre (el gatillo dispara rayos)
    this._gunHintDone = false;
    this._paintBanner(null);
    g.audio.playOsc(523, 1046, 0.22, 'square', 0.14, 0);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 110);
    // v2.63: el cartel SUPERPODER ya NO sale — aquí no se activa ningún
    // poder especial (el artista lo pidió expresamente)
    if (this.ctrl.powerSign) this.ctrl.powerSign.hide();
    // v2.63: la pistola SIEMPRE lista y visible al empezar el juego
    // (recuperación perezosa tras stop/leave/reintento)
    this._gunUpdate(0);
    if (g.renderer.xr.isPresenting && this._gunArtModel && this._gunArt.length === 0) {
      this._attachGunArt();
    }
  }

  /* ------------------------------ bolas ------------------------------------ */
  /** Nacimiento: mini-portal en tu mitad de la mesa; la bola cae y bota. */
  _spawnBall(b) {
    const g = this.game;
    b.active = true;
    b.waiting = false;
    b.stuckT = 0;
    b.portalT = 0;
    // v2.61: el vórtice nace EN LA MESA, pegado al borde del jugador, y la
    // bola aparece encima; bota EN SITIO hasta que el jugador la golpee.
    // v2.63: CADA slot tiene SU vórtice (izq / der) — dos bolas, dos portales
    const px = (b.slot === 0 ? -1 : 1) * 0.26 + (Math.random() - 0.5) * 0.06;
    const pz = SC.tableNearZ - 0.38;
    const py = SC.topY + 0.12;
    b.spawnPos = new THREE.Vector3(px, py, pz);
    const mp = this._miniPortals[b.slot];
    mp.grp.position.set(px, SC.topY + 0.06, pz);
    mp.t = 0;
    mp.ballDelay = 0.22;
    mp.grp.visible = true;
    // la bola se materializa dentro del portal (vel cero hasta abrirse)
    b.vel.set(0, 0, 0);
    b.spin.set(0, 0, 0);
    b.hold = false; b.holdT = 0;
    // v2.65 · ¿BOLA NEGRA? — azar (bombChance) + garantía: si llevan
    // bombEvery s sin salir una, el próximo recambio ES negra. La bomba vuela
    // como una bola más (mismos botes mínimos) y DETONA en su primer
    // contacto con el orbe.
    this._playT = this._playT || 0;
    let isBomb = Math.random() < (this.L.bombChance || 0.18);
    if (this._playT - (this._lastBombAt || 0) >= (this.L.bombEvery || 30)) isBomb = true;
    b.bomb = isBomb;
    if (b.isMain) g.ball.bomb = isBomb;    // _impact lee ball.bomb (raw)
    if (isBomb) this._lastBombAt = this._playT;
    this._applyBallSkin(b);
    b.pos.copy(b.spawnPos);
    b.__exPrev.copy(b.pos);
    if (b.isMain && g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
    if (b.isMain) {
      g.ball.pos.copy(b.pos); g.ball.vel.set(0, 0, 0); g.ball.spin.set(0, 0, 0);
      g.ballMesh.visible = true;
    } else if (b.mesh) {
      b.mesh.position.copy(b.pos);
      b.mesh.visible = false;    // aparece al abrirse el portal
    }
    if (b.bomb) {
      // aviso ominoso: tono grave + cartel (es un REGALO, no una pérdida)
      g.audio.playOsc(140, 52, 0.5, 'sawtooth', 0.2, 0);
      g.audio.playOsc(70, 40, 0.55, 'triangle', 0.16, 0.04);
      this._msg = tx('bomb_spawn');
      this._msgT = 2.4;
      this._hudDirty = true;
    } else {
      g.audio.playOsc(220, 880, 0.18, 'sine', 0.1, 0);
    }
  }

  /** v2.65: piel de la bola — normal (color del slot) o NEGRA-bomba (casi
   *  negra con brasa violeta). La bola principal usa ballMesh del core. */
  _applyBallSkin(b) {
    const g = this.game;
    if (b.isMain) {
      const m = g.ballMesh;
      if (m && m.material && this._ballSaved) {
        if (b.bomb) {
          m.material.color.setHex(0x0b0b12);
          if (m.material.emissive) m.material.emissive.setHex(0x8a26e0);
          if (m.material.emissiveIntensity !== undefined) m.material.emissiveIntensity = 1.15;
        } else {
          m.material.color.setHex(SC.ballColors[0]);
          if (m.material.emissive) m.material.emissive.setHex(0x0a2a33);
          if (m.material.emissiveIntensity !== undefined && this._ballSaved.ei !== undefined) {
            m.material.emissiveIntensity = this._ballSaved.ei;
          }
        }
      }
    } else if (b.mesh) {
      if (b.bomb) {
        b.mesh.material.color.setHex(0x0b0b12);
        b.mesh.material.emissive.setHex(0x8a26e0);
        b.mesh.material.emissiveIntensity = 1.15;
      } else {
        b.mesh.material.color.setHex(b.color);
        b.mesh.material.emissive.setHex(b.color);
        b.mesh.material.emissiveIntensity = 0.25;
      }
    }
  }

  _openPortalFx(mp, dt) {
    const g = this.game;
    mp.t += dt;
    const k = Math.min(1, mp.t / 0.22);
    mp.ring.rotation.z += dt * 6;
    mp.ring.material.opacity = k;
    mp.glow.material.opacity = 0.75 * k;
    mp.grp.rotation.y = Math.sin(mp.t * 9) * 0.12;
    if (mp.ballDelay > 0) {
      mp.ballDelay -= dt;
      if (mp.ballDelay <= 0) {
        // v2.61: ¡sale la bola! queda BOTANDO en el vórtice (altura fija)
        // hasta que el jugador la golpee con la pala
        const b = this.balls[mp.slot];
        b.vel.set(0, 0, 0);
        b.hold = true; b.holdT = 0;
        b.holdX = b.spawnPos.x; b.holdZ = b.spawnPos.z;
        b.holdBaseY = SC.topY + DIMS.ballRadius;
        if (b.mesh) b.mesh.visible = true;
        g.audio.playOsc(660, 1320, 0.12, 'sine', 0.12, 0);
        if (g.renderer.xr.isPresenting) g.haptic(g.ballHand, 0.25, 60);
      }
    }
    if (mp.t > 0.55) {
      const fade = Math.max(0, 1 - (mp.t - 0.55) / 0.25);
      mp.ring.material.opacity = fade;
      mp.glow.material.opacity = 0.75 * fade;
      if (mp.t > 0.8) { mp.grp.visible = false; mp.t = -1; }
    }
  }

  _ballLost(b) {
    const g = this.game;
    b.active = false;
    b.waiting = true;
    b.respawnT = this.L.respawnDelay;
    b.stuckT = 0;
    if (b.isMain) {
      g.ball.vel.set(0, 0, 0); g.ball.spin.set(0, 0, 0);
      g.ball.pos.set(0, -10, 0);       // aparcada bajo el suelo
      g.ballMesh.visible = false;
    } else if (b.mesh) {
      b.mesh.visible = false;
      b.vel.set(0, 0, 0);
    }
    for (const t of b.trail) { t.life = 0; t.sp.visible = false; }
  }

  /** ATRACCIÓN direccional: gira la velocidad hacia el orbe (o hacia el
   *  ladrillo vivo más cercano en la fase final) SIN tocar la velocidad. */
  _attract(b, dt) {
    const L = this.L;
    const toC = this._tA.subVectors(this._center, b.pos);
    const dist = toC.length();
    if (dist > L.attractionRange || dist < 1e-4) return;
    if (b.vel.dot(toC) <= 0) return;              // sólo si SE ACERCA
    const speed = b.vel.length();
    if (speed < 0.2) return;
    const lastPhase = this.aliveBricks <=
      Math.max(1, Math.floor(this.totalBricks * L.lastBricksPercent / 100));
    let target = this._tB.copy(toC).normalize();
    if (lastPhase) {
      // apunta al ladrillo vivo más cercano (mira SOLO en fase final)
      const near = this._nearestAliveBrick(b.pos);
      if (near >= 0) {
        // v2.120: guard anti-NaN (vector cero si la bola pisa el centro)
        const dx = this.wx[near] - b.pos.x;
        const dy = this.wy[near] - b.pos.y;
        const dz = this.wz[near] - b.pos.z;
        if (dx * dx + dy * dy + dz * dz > 1e-12) {
          target.set(dx, dy, dz).normalize();
        }
      }
    }
    const vhat = this._tC.copy(b.vel).divideScalar(speed);
    const ang = vhat.angleTo(target);
    if (ang < 1e-4) return;
    const maxAng = (L.attractionMaxAngle * Math.PI) / 180;
    const turn = Math.min(ang, maxAng) * L.attractionStrength * dt * (lastPhase ? 1.5 : 1);
    const axis = this._tD.crossVectors(vhat, target);
    if (axis.lengthSq() < 1e-8) return;
    axis.normalize();
    vhat.applyAxisAngle(axis, turn).normalize();
    b.vel.copy(vhat).multiplyScalar(speed);       // MISMA velocidad, otra dirección
  }

  _nearestAliveBrick(from) {
    let best = -1, bestD = Infinity;
    // barrido barato: en fase final quedan cientos, no miles
    for (let c = 0; c < this.cells; c++) {
      if (!this.alive[c]) continue;
      if (!this.exposed[c]) continue;             // sólo alcanzables
      const dx = this.wx[c] - from.x, dy = this.wy[c] - from.y, dz = this.wz[c] - from.z;
      const d = dx * dx + dy * dy + dz * dz;
      if (d < bestD) { bestD = d; best = c; }
    }
    return best;
  }

  /* --------------------------- colisión (subpaso) --------------------------- */
  /** Colisionador extra POR SUBPASO (480 Hz): cristales del corredor,
   *  suelo del tramo nuevo, pared del fondo, MESA (v2.64: arco mínimo) y la
   *  REJILLA del orbe. */
  _collide(ball) {
    const p = ball.pos, v = ball.vel;
    const r = DIMS.ballRadius;
    // v2.64 · ARCO DE BOTE MÍNIMO: vy que produce un bote de minBounceHeight
    // (0.45 m — casi el arco del vórtice de salida). La queja del artista:
    // la bola que VUELVE del orbe «bota poquito o se arrastra y no se le
    // puede golpear». Causa: la mesa del CORE sigue viva en el tramo de la
    // mesa original y su fricción (0.94) + restitución (0.88) encogen los
    // botes a cada toque. Ahora CADA bote (mesa o corredor) relanza el arco
    // y re-asegura la velocidad mínima de retorno: cero bolas rastreras.
    let vyMin = 0;
    if (!ball.hold) {
      const gAbs = DIMS.gravity < 0 ? -DIMS.gravity : DIMS.gravity;
      vyMin = Math.sqrt(2 * gAbs * (this.L.minBounceHeight || 0.45));
    }
    // 1) campo de fuerza lateral del corredor (todo el corredor, toda altura)
    if (p.z < SC.tableNearZ) {
      const lim = SC.halfW - r;
      if (p.x < -lim) { p.x = -lim; if (v.x < 0) { v.x = -v.x * MAGIA.wallRest; this._tok(p.x); } }
      else if (p.x > lim) { p.x = lim; if (v.x > 0) { v.x = -v.x * MAGIA.wallRest; this._tok(p.x); } }
      // 1b) v2.64: MESA ORIGINAL (z corridorZ0..tableNearZ) — bote recién
      // producido (pos clavada a topR y subiendo): relanza el arco mínimo
      // y garantiza la velocidad de retorno. Sólo dispara EN el bote.
      const topR = DIMS.tableTopY + r;
      if (vyMin > 0 && v.y > 0.15 && p.y <= topR + 0.004 &&
          Math.abs(p.x) <= DIMS.tableHalfWidth + r * 0.5 &&
          Math.abs(p.z - DIMS.tableCenterZ) <= DIMS.tableHalfLength) {
        if (v.y < vyMin) v.y = vyMin;
        const minRet = this.L.minReturnSpeed || 2.8;
        if (v.lengthSq() > 1e-6 && v.length() < minRet) v.setLength(minRet);
        // v2.65: bote CASI VERTICAL en la mesa = bota en el sitio lejos del
        // jugador → patada de deriva HACIA EL JUGADOR
        if (Math.hypot(v.x, v.z) < 0.9 && v.z < minRet * 0.85) v.z = minRet * 0.85;
      }
      // 2) suelo del TRAMO NUEVO (más allá del borde lejano de la mesa)
      if (p.z < SC.corridorZ0) {
        const fl = SC.topY + r;
        if (p.y < fl && v.y < 0) {
          p.y = fl;
          v.y = -v.y * DIMS.tableRestitution;
          // v2.64: ARCO MÍNIMO también aquí (con 0.88 los botes se iban
          // apagando y la bola llegaba rastrera al jugador)
          if (v.y < vyMin) v.y = vyMin;
          // v2.63: SIN fricción horizontal + energía mínima en cada bote del
          // corredor cuando la bola VUELVE al jugador — nada de bolas moritas
          const minFloor = (this.L.minReturnSpeed || 2.8) * 0.8;
          if (v.lengthSq() > 1e-6 && v.length() < minFloor) {
            v.setLength(minFloor);
          }
          // v2.65: bote CASI VERTICAL en el corredor → patada HACIA EL JUGADOR
          if (Math.hypot(v.x, v.z) < 0.9 && v.z < minFloor) v.z = minFloor;
        }
        // 3) pared del fondo (tras el portal)
        if (p.z < SC.corridorZ1 + r && v.z < 0) {
          p.z = SC.corridorZ1 + r;
          v.z = -v.z * MAGIA.wallRest;
          this._tok(0);
        }
      }
    }
    // 4) ORBE: barrido de la trayectoria del subpaso (mitad de ladrillo)
    let prev = ball.__exPrev;
    if (!prev) prev = ball.__exPrev = new THREE.Vector3().copy(ball.pos);
    const dx = p.x - prev.x, dy = p.y - prev.y, dz = p.z - prev.z;
    const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (dist > 1e-9) {
      const BR = this.L.brickSize;
      const orbR = this.L.radiusOuter * BR + BR * 0.5 + r;
      // coarse: sólo si el segmento se acerca al orbe
      const cx = this._center.x, cy = this._center.y, cz = this._center.z;
      const mx = (p.x + prev.x) * 0.5 - cx, my = (p.y + prev.y) * 0.5 - cy, mz = (p.z + prev.z) * 0.5 - cz;
      if (mx * mx + my * my + mz * mz < (orbR + dist * 0.5) * (orbR + dist * 0.5)) {
        const steps = Math.max(1, Math.ceil(dist / (BR * 0.5)));
        for (let s = 1; s <= steps; s++) {
          const t = s / steps;
          const sx = prev.x + dx * t, sy = prev.y + dy * t, sz = prev.z + dz * t;
          const cell = this._cellAt(sx, sy, sz);
          if (cell >= 0 && this.alive[cell]) {
            this._impact(ball, cell, sx, sy, sz);
            break;
          }
        }
      }
    }
    prev.copy(p);
    // 5) bloque reloj (la bola también puede reventarlo)
    if (this.block && this.block.active) {
      const bc = this.block.pos;
      const bh = 0.15 + r;
      if (Math.abs(p.x - bc.x) < bh && Math.abs(p.y - bc.y) < bh && Math.abs(p.z - bc.z) < bh) {
        this._hitBlock('bola');
      }
    }
  }

  /** Celda que CONTIENE el punto (centro de ladrillo en múltiplos de BR). */
  _cellAt(x, y, z) {
    const R = this.R, S = this.S, BR = this.L.brickSize;
    const i = Math.round((x - this._center.x) / BR);
    const j = Math.round((y - this._center.y) / BR);
    const k = Math.round((z - this._center.z) / BR);
    if (i < -R || i > R || j < -R || j > R || k < -R || k > R) return -1;
    return this.cellKey[(i + R) * S * S + (j + R) * S + (k + R)];
  }

  /** IMPACTO: cadena de rotura + rebote. dir = dirección de vuelo. */
  _impact(ball, cell, sx, sy, sz) {
    const L = this.L;
    const g = this.game;
    // v2.65 · BOLA NEGRA: su PRIMER contacto con el orbe DETONA la explosión
    if (ball.bomb) { this._bombBlast(ball, cell); return; }
    const speed0 = ball.vel.length();
    const dir = this._tA.set(ball.vel.x, ball.vel.y, ball.vel.z).divideScalar(Math.max(1e-6, speed0));
    const canDrill = speed0 >= L.minChainSpeed;
    const chainN = canDrill ? L.maxChain : 1;
    // --- CADENA: marcha desde el ladrillo golpeado en la dirección de vuelo
    const destroyed = [];
    let px = this.wx[cell], py = this.wy[cell], pz = this.wz[cell];
    const BR = L.brickSize;
    const maxD = (L.radiusOuter + 1.2) * BR;
    for (let k = 0; k < chainN * 3 + 2 && destroyed.length < chainN; k++) {
      const c = k === 0 ? cell : this._cellAt(px, py, pz);
      if (c >= 0 && this.alive[c]) destroyed.push(c);
      px += dir.x * BR; py += dir.y * BR; pz += dir.z * BR;
      const ddx = px - this._center.x, ddy = py - this._center.y, ddz = pz - this._center.z;
      if (ddx * ddx + ddy * ddy + ddz * ddz > maxD * maxD) break;
    }
    // --- destruir + puntuar
    const n = destroyed.length;
    let pts = 0;
    for (let i = 0; i < n; i++) {
      const c = destroyed[i];
      pts += (L.layerPoints[this.layer[c]] || 10);
      this._destroyCell(c);
    }
    if (n > 1) pts += (n - 1) * (L.chainBonus || 5);
    if (pts > 0) {
      this.score += pts;
      this._hudDirty = true;
      if (n >= 3) this.ctrl._setStateSilent('surprised', 1.4);   // ¡cadena grande!
      if (n >= 2 && performance.now() - this._lastChainMsg > 900) {
        this._lastChainMsg = performance.now();
        this._msg = tx('chain_n', { n });
        this._msgT = 1.1;
        this._hudDirty = true;
      }
    }
    // sonido + háptica (throttle)
    const now = performance.now();
    if (now - this._lastBreakSnd > 55) {
      this._lastBreakSnd = now;
      const lay = this.layer[cell];
      const f = [880, 640, 480][lay] || 600;
      g.audio.playOsc(f * (1 + 0.09 * Math.min(n, 4)), f * 0.5, 0.09, 'square', 0.13, 0);
      g.audio.playOsc(180 + Math.random() * 60, 80, 0.07, 'triangle', 0.1, 0.01);
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.2 + 0.09 * Math.min(n, 4), 40);
    }
    // v2.63: CADA ladrillo de la cadena revienta en cubitos de SU color
    for (let i = 0; i < n; i++) {
      const c = destroyed[i];
      this._puff(this.wx[c], this.wy[c], this.wz[c], 2, this.layer[c]);
    }
    this._flash(this.wx[cell], this.wy[cell], this.wz[cell], 0.5 + Math.min(n, 4) * 0.16);
    // --- velocidad restante (v2.63: taladrar NO frena — frenesí puro)
    const spd = speed0 * Math.pow(L.energyLossPerHit, n);
    // --- ¿rebote o túnel? mira la celda SIGUIENTE en la dirección de vuelo
    const nx = ball.pos.x + dir.x * BR * 0.75;
    const ny = ball.pos.y + dir.y * BR * 0.75;
    const nz = ball.pos.z + dir.z * BR * 0.75;
    const nextC = this._cellAt(nx, ny, nz);
    if (nextC >= 0 && this.alive[nextC]) {
      // normal del eje DOMINANTE de la dirección (rebote estable tipo cubo)
      const ax = Math.abs(dir.x), ay = Math.abs(dir.y), az = Math.abs(dir.z);
      let nX = 0, nY = 0, nZ = 0;
      if (ax >= ay && ax >= az) nX = -Math.sign(dir.x);
      else if (ay >= az) nY = -Math.sign(dir.y);
      else nZ = -Math.sign(dir.z);
      const dot = ball.vel.x * nX + ball.vel.y * nY + ball.vel.z * nZ;
      ball.vel.set(
        (ball.vel.x - 2 * dot * nX),
        (ball.vel.y - 2 * dot * nY),
        (ball.vel.z - 2 * dot * nZ),
      ).multiplyScalar(L.restitution);
      if (ball.vel.length() > spd) ball.vel.setLength(spd);
      // recoloca la bola FUERA del ladrillo vivo siguiente
      const BRh = BR * 0.5 + DIMS.ballRadius + 0.002;
      ball.pos.set(
        this.wx[nextC] + nX * BRh,
        this.wy[nextC] + nY * BRh,
        this.wz[nextC] + nZ * BRh,
      );
      ball.__exPrev.copy(ball.pos);
    } else {
      // túnel: sigue volando por el agujero que acaba de abrir
      ball.vel.setLength(spd);
    }
    // v2.63 · ENERGÍA GARANTIZADA: la bola sale de CUALQUIER impacto del
    // orbe con mínimo minReturnSpeed hacia el jugador — nada de bolas
    // moribundas que se quedan paradas junto al orbe (juego frenético).
    const minRet = L.minReturnSpeed || 2.8;
    if (ball.vel.lengthSq() > 1e-6 && ball.vel.length() < minRet) {
      ball.vel.setLength(minRet);
    }
    // ¿orbe destruido?
    if (this.aliveBricks <= 0) this._finish(true);
  }

  /** v2.65 · EXPLOSIÓN DE LA BOLA NEGRA: arranca los ladrillos VIVOS más
   *  próximos al impacto (hasta blastMax dentro de blastRadius), con lluvia
   *  de cubitos por capa, doble flash, booms y háptica fuerte. La bola se
   *  consume y el vórtice trae de nuevo otra (que puede volver a ser negra). */
  _bombBlast(ball, cell) {
    const L = this.L;
    const g = this.game;
    const bx = this.wx[cell], by = this.wy[cell], bz = this.wz[cell];
    const R = L.blastRadius || 0.55, cap = L.blastMax || 60;
    const R2 = R * R;
    const cand = [];
    for (let c = 0; c < this.cells; c++) {
      if (!this.alive[c]) continue;
      const dx = this.wx[c] - bx, dy = this.wy[c] - by, dz = this.wz[c] - bz;
      const d2 = dx * dx + dy * dy + dz * dz;
      if (d2 <= R2) cand.push([d2, c]);
    }
    cand.sort((a, b) => a[0] - b[0]);
    const n = Math.min(cand.length, cap);
    let pts = 0;
    for (let i = 0; i < n; i++) {
      const c = cand[i][1];
      pts += (L.layerPoints[this.layer[c]] || 10);
      this._destroyCell(c);
      this._puff(this.wx[c], this.wy[c], this.wz[c], i < 22 ? 2 : 1, this.layer[c]);
    }
    if (pts > 0) { this.score += pts; this._hudDirty = true; }
    // estallido central: ráfaga de cubitos + doble flash grande
    for (let i = 0; i < 10; i++) this._puff(bx, by, bz, 1, (Math.random() * 3) | 0);
    this._flash(bx, by, bz, 2.6);
    this._flash(bx, by, bz, 1.7);
    g.audio.playOsc(150, 28, 0.55, 'sawtooth', 0.42, 0);
    g.audio.playOsc(90, 22, 0.7, 'triangle', 0.36, 0.02);
    g.audio.playOsc(400, 60, 0.3, 'square', 0.18, 0.01);
    if (g.renderer.xr.isPresenting) {
      g.haptic(g.paddleHand, 0.95, 160);
      window.setTimeout(() => g.haptic(g.paddleHand, 0.4, 110), 200);
    }
    this._msg = tx('bomb_boom', { n });
    this._msgT = 1.6;
    this._hudDirty = true;
    // la bola SE CONSUME con la explosión → recambio desde su vórtice
    const slot = (ball === g.ball) ? this.balls[0] : ball;
    this._ballLost(slot);
    if (this.aliveBricks <= 0) this._finish(true);
  }

  _destroyCell(c) {
    this.alive[c] = 0;
    this.aliveBricks--;
    this.aliveByLayer[this.layer[c]]--;
    // expone a los 6 vecinos (entran en el InstancedMesh visible)
    const R = this.R, S = this.S;
    const N6 = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
    for (const [dx, dy, dz] of N6) {
      const nx = this.ci[c] + dx, ny = this.cj[c] + dy, nz = this.ck[c] + dz;
      if (Math.abs(nx) > R || Math.abs(ny) > R || Math.abs(nz) > R) continue;
      const k2 = (nx + R) * S * S + (ny + R) * S + (nz + R);
      const nb = this.cellKey[k2];
      if (nb < 0) continue;
      if (!this.alive[nb]) continue;
      if (!this.exposed[nb]) {
        this.exposed[nb] = 1;
        if (this.phase === 'play') this._writeCell(nb, 1);   // aparece al descubierto
      }
    }
    this._writeCell(c, 0);    // fuera del dibujo
  }

  /* --------------------------- bucle del nivel ----------------------------- */
  step(dt) {
    if (!this.active || !this.inited) return;
    const g = this.game;
    if (this.phase === 'intro') {
      this.phaseT -= dt;
      this._parkMainBall();
      if (this.phaseT <= 0) this._startMontaje();
    } else if (this.phase === 'montaje') {
      this._parkMainBall();
      this._montajeStep(dt);
    } else if (this.phase === 'play') {
      this._playStep(dt);
    } else if (this.phase === 'result') {
      this.phaseT -= dt;
      this._parkMainBall();
      if (this.phaseT <= 0) this._afterResult();
    }
    this._anims(dt);
    this._starsCorr(dt);
    if (this._msgT > 0) {
      this._msgT -= dt;
      if (this._msgT <= 0) { this._msg = ''; this._hudDirty = true; }
    }
    if (this._hudDirty) this._hud();
  }

  _parkMainBall() {
    const g = this.game;
    // bola principal aparcada bajo el suelo mientras no juega
    if (g.ball.pos.y > -5) {
      g.ball.pos.set(0, -10, 0);
      g.ball.vel.set(0, 0, 0);
      g.ball.spin.set(0, 0, 0);
      g.ballMesh.visible = false;
    }
  }

  _playStep(dt) {
    const g = this.game;
    const L = this.L;
    // v2.71 · SALVAGUARDA DE FINALIZACIÓN: el nivel termina SIEMPRE que el
    // orbe quede a cero — aunque el último ladrillo (de las capas 2 y 3,
    // las interiores, o de cualquiera) caiga por un camino que no pase por
    // _impact/_bombBlast/_shotBreak. Verificado en verify_v271.sh.
    if (this.aliveBricks <= 0) { this._finish(true); return; }
    // reloj
    this.time -= dt;
    this._playT = (this._playT || 0) + dt;   // v2.65: tiempo de juego (bombas)
    if (this.time <= 0) { this.time = 0; this._hudDirty = true; this._finish(false); return; }
    const sec = Math.ceil(this.time);
    if (sec !== this._lastSec) {
      const prevSec = this._lastSec;   // v2.120: segundo anterior real
      this._lastSec = sec;
      this._hudDirty = true;
      if (sec <= 10 && sec >= 1) {
        g.audio.playOsc(980, 620, 0.14, 'sawtooth', 0.16, 0);
        if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.25, 60);
      } else if (prevSec !== null && prevSec !== undefined &&
                 prevSec > L.alertThreshold && sec <= L.alertThreshold) {
        // v2.120: cruce del umbral (antes === con valor configurable: un
        // alertThreshold decimal saltaba el aviso en silencio)
        this._msg = tx('time_warn', { n: L.alertThreshold });
        this._msgT = 2.6;
        this._hudDirty = true;
      }
    }
    // nacimiento de bolas (v2.63: DOS bolas — la segunda sale rápido y cada
    // recambio rellena su hueco desde SU vórtice)
    this.spawnCd -= dt;
    // v2.120: conteo con bucle plano (antes filter() = un array por frame)
    let alive = 0;
    for (const b of this.balls) if (b.active) alive++;
    if (this.spawnCd <= 0 && alive < L.maxBalls) {
      const free = this.balls.find((b) => !b.active);
      if (free) this._spawnBall(free);
      this.spawnCd = (alive === 0) ? 0.7 : 1.0 + Math.random() * 1.0;
    } else if (this.spawnCd <= 0) {
      this.spawnCd = 0.4;
    }
    // recambios (respawnDelay tras perder una bola)
    for (const b of this.balls) {
      if (b.waiting) {
        b.respawnT -= dt;
        if (b.respawnT <= 0) b.waiting = false;
      }
    }
    // animación de los MINI-PORTALES (apertura → suelta la bola → cierre)
    for (const mp of this._miniPortals) {
      if (mp.t >= 0) this._openPortalFx(mp, dt);
    }
    // ALERTA FINAL: bloque reloj mientras queden prórrogas
    this._alertStep(dt);
    // física de TODAS las bolas (stepPhysics + colisionador propio)
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    const pads = (g.renderer.xr.isPresenting && ps && ps.active) ? [ps] : [];
    for (const b of this.balls) {
      if (!b.active) continue;
      if (b.portalT < 0.26) {   // aún materializándose: sin física
        b.portalT += dt;
        continue;
      }
      this._attract(b, dt);
      const evs = b.isMain ? g.events : b.evs;
      evs.length = 0;
      stepPhysics(dt, b.isMain ? g.ball : b, pads, evs, this._extra);
      // sonidos de los eventos de los clones (el principal ya suena solo)
      if (!b.isMain && evs.length) {
        for (const e of evs) {
          if (e.type === 'paddle') {
            g.audio.paddle(0, e.speed || 1);
            if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 70);
          } else if (e.type === 'table') {
            g.audio.tableBounce(0, Math.min(1, (e.speed || 1) / 5));
          } else if (e.type === 'wall') {
            this._tok(b.pos.x);
          }
        }
      }
      // ¿la bola principal volvió tras el portal? el clon sigue a su malla
      if (!b.isMain && b.mesh) b.mesh.position.copy(b.pos);
      // v2.61: BOTE EN ESPERA — mientras nadie la golpee, la bola rebota en
      // el vórtice con arco determinista (siempre a la misma altura). El
      // primer toque de pala la libera con la velocidad del impacto.
      if (b.hold) {
        let hit = false;
        for (const e of evs) { if (e.type === 'paddle') { hit = true; break; } }
        if (hit) {
          b.hold = false;               // el golpe la libera (vel ya viene del impacto)
        } else {
          b.holdT += dt;
          // v2.62: bote MUCHO MÁS ALTO (el artista pidió más del doble del
          // anterior): H 0.16→0.52 m — apex = mesa+0.52 ≈ 1.30 m, zona de
          // golpeo natural. Periodo 0.95 s (cae con naturalidad).
          const T = 0.95, H = 0.52;
          const p = (b.holdT % T) / T;
          b.pos.set(b.holdX, b.holdBaseY + 4 * H * p * (1 - p), b.holdZ);
          b.vel.set(0, (4 * H * (1 - 2 * p)) / T, 0);
          b.spin.multiplyScalar(Math.max(0, 1 - dt * 2));
        }
      }
      // v2.65: brasa de la BOLA NEGRA sigue a la bola
      const bg = this._bombGlows && this._bombGlows[b.slot];
      if (bg) {
        if (b.active && b.bomb) {
          this._bombGlowT += dt;
          bg.visible = true;
          bg.position.copy(b.pos);
          const pulse = 0.75 + Math.sin(this._bombGlowT * 7) * 0.25;
          bg.material.opacity = 0.55 * pulse;
          bg.scale.setScalar(0.19 + 0.07 * pulse);
        } else if (bg.visible) { bg.visible = false; bg.material.opacity = 0; }
      }
      // v2.65 · NUNCA LEJOS PARA SIEMPRE: si la bola lleva >6 s sin acercarse
      // a la zona del jugador (bote en el sitio, ping-pong lateral, rincón),
      // se le fuerza un bote HACIA EL JUGADOR. Los botes casi verticales ya
      // reciben la patada de deriva en _collide; esta es la red definitiva.
      if (!b.hold && b.pos.z > -0.45) {
        b._farT = 0;
      } else if (!b.hold) {
        b._farT = (b._farT || 0) + dt;
        if (b._farT > 6) {
          const minRet = this.L.minReturnSpeed || 2.8;
          const sp = Math.max(b.vel.length(), minRet);
          b.vel.set((Math.random() - 0.5) * 0.7, Math.max(0.8, Math.abs(b.vel.y) * 0.4), sp * 0.92).setLength(sp);
          b._farT = 0;
        }
      } else {
        b._farT = 0;
      }
      // estela de color
      this._trail(b, dt);
      // pérdida: fuera del corredor / detrás del jugador / quieta 10 s / suelo
      this._checkLost(b, evs, dt);
      if (!b.active) continue;
    }
    // pistola visible en la mano libre durante el juego
    this._gunUpdate(dt);
  }

  _trail(b, dt) {
    b.trailT -= dt;
    if (b.trailT <= 0 && b.vel.lengthSq() > 0.5) {
      b.trailT = 0.03;
      for (const t of b.trail) {
        if (t.life > 0) continue;
        t.life = 0.32;
        t.sp.visible = true;
        t.sp.position.copy(b.pos);
        t.sp.material.opacity = 0.7;
        t.sp.scale.setScalar(0.085);
        break;
      }
    }
    for (const t of b.trail) {
      if (t.life <= 0) continue;
      t.life -= dt;
      if (t.life <= 0) { t.sp.visible = false; continue; }
      t.sp.material.opacity = t.life * 2.1;
      t.sp.scale.multiplyScalar(1 - dt * 1.6);
    }
  }

  _checkLost(b, evs, dt) {
    const g = this.game;
    const p = b.pos, v = b.vel;
    let lost = false;
    for (const e of evs) {
      if (e.type === 'floor') { lost = true; break; }
    }
    if (!lost) {
      if (p.z > 0.7) lost = true;                                  // tras el jugador
      else if (p.y < 0.2) lost = true;                             // bajo el corredor
      else if (Math.abs(p.x) > DIMS.roomHalfX - 0.05) lost = true; // escapó lateral
      else if (p.z < SC.corridorZ1 - 0.1) lost = true;             // tras la pared
      else if (v.lengthSq() < 0.0225) {                            // quieta > 4 s
        b.stuckT += dt;
        if (b.stuckT > 4) lost = true;
      } else b.stuckT = 0;
    }
    if (lost) this._ballLost(b);
  }

  /* ------------------------- ALERTA FINAL / prórroga ----------------------- */
  _alertStep(dt) {
    const L = this.L;
    if (this.block && this.block.active) {
      const bl = this.block;
      bl.life -= dt;
      bl.t += dt;
      bl.pos.y = bl.homeY + Math.sin(bl.t * 2.2) * 0.07;
      bl.pos.x = bl.homeX + Math.sin(bl.t * 1.3) * 0.12;
      this.blockGroup.position.copy(bl.pos);
      this.blockMesh.rotation.y += dt * 1.4;
      this.blockMesh.rotation.x = Math.sin(bl.t * 0.9) * 0.18;
      // parpadeo en el último tramo de vida
      this.blockGlow.material.opacity = bl.life < 1.5
        ? 0.3 + 0.45 * Math.abs(Math.sin(bl.t * 9))
        : 0.55 + Math.sin(bl.t * 3.5) * 0.15;
      if (bl.life <= 0) {
        this._despawnBlock();
        this.retryCd = L.clockRetryDelay;
        if (this.extUsed < L.maxExtensions) {
          this._msg = tx('alert_gone');
          this._msgT = 1.8;
          this._hudDirty = true;
        }
      }
      return;
    }
    // ¿toca sacar bloque?
    if (this.extUsed >= L.maxExtensions) {
      if (!this._noExtAnnounced && this.time <= L.alertThreshold) {
        this._noExtAnnounced = true;
        this._msg = tx('no_more_ext');
        this._msgT = 2.4;
        this._hudDirty = true;
      }
      return;
    }
    if (this.time > L.alertThreshold) return;
    if (this.retryCd > 0) { this.retryCd -= dt; return; }
    this._spawnBlock();
  }

  _spawnBlock() {
    const L = this.L;
    this.block = {
      active: true,
      t: 0,
      life: L.clockBlockLife,
      pos: new THREE.Vector3(),
      homeX: (Math.random() * 2 - 1) * 0.5,
      homeY: 0.95 + Math.random() * 0.55,
      homeZ: -(1.2 + Math.random() * 2.2),   // entre el jugador y el orbe
    };
    this.block.pos.set(this.block.homeX, this.block.homeY, this.block.homeZ);
    this.blockGroup.visible = true;
    this.blockGroup.position.copy(this.block.pos);
    this.blockGlow.material.opacity = 0.55;
    // alarma: dos tonos descendentes ×3
    const g = this.game;
    for (let i = 0; i < 3; i++) {
      g.audio.playOsc(980, 620, 0.16, 'square', 0.17, i * 0.42);
      g.audio.playOsc(980, 620, 0.16, 'square', 0.17, i * 0.42 + 0.2);
    }
    this._msg = tx('alert_msg', { n: L.timeBonus });
    this._msgT = Math.max(2.2, L.clockBlockLife);
    this._hudDirty = true;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 160);
  }

  _hitBlock(by) {
    if (!this.block || !this.block.active) return;
    const g = this.game;
    const L = this.L;
    this.time += L.timeBonus;
    this.extUsed++;
    this._lastSec = -1;
    this._hudDirty = true;
    // fx: flash dorado + campana de reloj
    this._flash(this.block.pos, 1.4);
    g.audio.playOsc(1568, 1568, 0.5, 'sine', 0.2, 0);
    g.audio.playOsc(784, 784, 0.6, 'triangle', 0.14, 0.02);
    g.audio.playOsc(523, 1046, 0.3, 'sine', 0.12, 0.3);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 180);
    this._msg = tx('ext_get', { n: L.timeBonus });
    this._msgT = 2.2;
    this._hudDirty = true;
    this._despawnBlock();
    this.ctrl._setStateSilent('surprised', 1.6);
    console.info('[magia] prórroga', by, '+', L.timeBonus, 's · total', this.extUsed);
  }

  _despawnBlock() {
    this.block = null;
    // v2.70: guard — antes de build() el blockGroup no existe (la prueba
    // headless llama _finish sin nivel construido; también hardening general)
    if (this.blockGroup) this.blockGroup.visible = false;
  }

  /* ---------------------------- pistola de rayos --------------------------- */
  /** v2.61: carga pistol.glb del artista y la monta en las monturas del core
   *  (oculta la procedural SIN destruirla; se restaura en stop()). */
  _loadGunArt() {
    const g = this.game;
    if (!g.gunMounts) return;
    if (this._gunArtModel) { this._attachGunArt(); return; }
    const url = this.ctrl.manifest.gunUrl;
    if (!url || this._gunArtLoading) return;
    this._gunArtLoading = true;
    try {
      new GLTFLoader().load(url, (gltf) => {
        this._gunArtLoading = false;
        try {
          const model = this._normalizeGun(gltf.scene);
          if (!model) return;
          this._gunArtModel = model;
          this._attachGunArt();
          console.info('[magia] pistol.glb del artista montada (mano libre)');
        } catch (e) { console.warn('[magia] pistola: normalización KO', e); }
      }, undefined, () => {
        this._gunArtLoading = false;
        console.warn('[magia] pistol.glb no disponible — se mantiene la del core');
      });
    } catch (e) { this._gunArtLoading = false; }
  }

  /** Encaja el GLB del artista: escala real (≈32 cm de largo), cañón hacia
   *  -Z y empuñadura en el origen de la montura (donde agarra la mano). */
  _normalizeGun(scene) {
    const box = new THREE.Box3().setFromObject(scene);
    if (box.isEmpty()) return null;
    const size = box.getSize(new THREE.Vector3());
    const root = new THREE.Group();
    root.add(scene);
    // eje MÁS LARGO → Z (cañón); el segundo más largo → Y (altura)
    const ax = [['x', size.x], ['y', size.y], ['z', size.z]].sort((a, b) => b[1] - a[1]);
    if (ax[0][0] === 'x') scene.rotation.y = Math.PI / 2;
    else if (ax[0][0] === 'y') scene.rotation.x = -Math.PI / 2;
    const s2 = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
    const ax2 = [['x', s2.x], ['y', s2.y]].sort((a, b) => b[1] - a[1])[0][0];
    if (ax2 === 'x') scene.rotateZ(Math.PI / 2);   // rollo: anchura → altura
    // escala: longitud objetivo 32 cm (bien visible en la mano)
    const s3 = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
    const len = Math.max(s3.x, s3.y, s3.z) || 1;
    root.scale.setScalar(0.32 / len);
    // v2.62 · ENCARAR: la boca del cañón hacia -Z. El punto MÁS BAJO del
    // modelo es la base de la empuñadura; si cae en la mitad -Z el cañón
    // mira a +Z → giro 180°. (El haz sale por -Z de la montura.)
    try {
      root.updateMatrixWorld(true);
      const lv = new THREE.Vector3(), tv = new THREE.Vector3();
      let found = false;
      root.traverse((o) => {
        if (!o.isMesh || !o.geometry || !o.geometry.attributes) return;
        const pa = o.geometry.attributes.position;
        if (!pa) return;
        for (let i = 0; i < pa.count; i++) {
          tv.fromBufferAttribute(pa, i).applyMatrix4(o.matrixWorld);
          if (!found || tv.y < lv.y) { lv.copy(tv); found = true; }
        }
      });
      if (found && lv.z < 0) root.rotation.y += Math.PI;
    } catch (e) { /* orientación original si el barrido falla */ }
    // centrar: puño en el origen (base de la empuñadura algo bajo el origen)
    const b4 = new THREE.Box3().setFromObject(root);
    const c = b4.getCenter(new THREE.Vector3());
    root.position.set(-c.x, -b4.min.y - 0.055, -c.z);
    // v2.62 · BOCA DEL CAÑÓN en espacio de MONTURA (el láser sale de aquí y
    // no del puño). Caja final en montura: y ∈ [-0.055, h-0.055], z centrado.
    // Ánima ≈ 2 cm bajo el plano superior del arma.
    try {
      const bFin = new THREE.Box3().setFromObject(root);
      const dimF = bFin.getSize(new THREE.Vector3());
      this._gunMuzzle = new THREE.Vector3(0, dimF.y - 0.075, bFin.min.z + 0.015);
    } catch (e) { this._gunMuzzle = new THREE.Vector3(0, 0.02, -0.16); }
    // diagnóstico headless (tamaño final en metros tras el encaje)
    try {
      const fin = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
      const mz = this._gunMuzzle || new THREE.Vector3();
      window.__MAGIA_GUN_INFO = {
        len: +fin.z.toFixed(3), alto: +fin.y.toFixed(3), ancho: +fin.x.toFixed(3),
        escala: +(0.32 / len).toFixed(4),
        boca: { x: +mz.x.toFixed(3), y: +mz.y.toFixed(3), z: +mz.z.toFixed(3) },
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
      for (const ch of gm.children) ch.visible = false;   // la del core, oculta
      const art = this._gunArtModel.clone(true);
      art.userData.__magiaArt = true;
      gm.add(art);
      this._gunArt.push({ mount: gm, art });
    }
  }

  /** Devuelve las monturas a su estado original (pistola del core visible). */
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
    const present = g.renderer.xr.isPresenting;
    if (g.gunMounts) {
      const free = 1 - g.paddleHand;
      for (let k = 0; k < 2; k++) {
        if (g.gunMounts[k]) g.gunMounts[k].visible = present && k === free;
      }
      // reenganche perezoso del arte del artista (tras stop/leave/relanzar)
      if (present && this._gunArtModel && this._gunArt.length === 0) {
        this._attachGunArt();
      }
    }
    if (present && !this._gunHintDone) {
      this._gunHintDone = true;
      g.rules.message = tx('gun_hint');
    }
    // rayos en vuelo (0.16 s de vida, como los de La Locura)
    for (let i = this._beams.length - 1; i >= 0; i--) {
      const b = this._beams[i];
      b.t += dt;
      const f = 1 - b.t / 0.16;
      if (f <= 0) {
        for (const m of [b.mesh, b.glow]) {
          if (!m) continue;
          g.rig.remove(m);   // v2.62: haces en el rig
          if (m.geometry) m.geometry.dispose();
          if (m.material) m.material.dispose();
        }
        this._beams.splice(i, 1);
        continue;
      }
      b.mesh.material.opacity = 0.95 * f;
      if (b.glow) b.glow.material.opacity = 0.4 * f;
    }
  }

  /** DISPARO (gatillo de la mano libre). v2.62:
   *  · el haz SALE DE LA BOCA DEL CAÑÓN (offset _gunMuzzle del modelo), no
   *    del puño;
   *  · TODO el cálculo vive en el ESPACIO DEL RIG (inmune al recentrado de
   *    la Quest, antes el rayo y los objetivos estaban en mundos distintos);
   *  · el rayo atraviesa el orbe: si el primer ladrillo es ROJO (capa
   *    exterior) lo ROMPE; si es interior (marrón/amarillo) el disparo se
   *    ABSORBE con chispa. La BOLA sigue rompiendo cualquier ladrillo. */
  _fireBeam() {
    const g = this.game;
    const now = performance.now() / 1000;
    if (now - this._gunLast < 0.16) return;
    this._gunLast = now;
    const mount = g.gunMounts && g.gunMounts[1 - g.paddleHand];
    if (!mount) return;
    const pos = new THREE.Vector3();
    const q = new THREE.Quaternion();
    mount.getWorldPosition(pos);
    mount.getWorldQuaternion(q);
    // origen REAL: boca del cañón (offset local de la montura, girado por la
    // pose mundial de la montura — incluye el giro del rig)
    const muzzle = this._gunMuzzle || new THREE.Vector3(0, 0.02, -0.16);
    pos.add(muzzle.clone().applyQuaternion(q));
    const dirW = new THREE.Vector3(0, 0, -1).applyQuaternion(q).normalize();
    // ---- al ESPACIO DEL RIG (el orbe, el bloque y las celdas viven ahí)
    const qRig = g.rig.getWorldQuaternion(new THREE.Quaternion()).invert();
    const rPos = g.rig.worldToLocal(pos.clone());
    const rDir = dirW.clone().applyQuaternion(qRig).normalize();
    // ---- objetivos: bloque reloj (distancia del rayo a su centro) y orbe
    let blockT = Infinity;
    if (this.block && this.block.active) {
      const bc = this.block.pos.clone().sub(rPos);
      const t = THREE.MathUtils.clamp(bc.dot(rDir), 0, 6);
      const closest = rDir.clone().multiplyScalar(t).add(rPos);
      if (closest.distanceTo(this.block.pos) < 0.22) blockT = t;
    }
    let brickC = -1, brickT = Infinity;
    if (this.aliveBricks > 0) {
      const BR = this.L.brickSize;
      const orbR = this.L.radiusOuter * BR + BR;
      const toC = this._center.clone().sub(rPos);
      const tProj = toC.dot(rDir);                    // acotación al orbe
      if (tProj > -orbR && tProj < 9) {
        const t0 = Math.max(0.05, tProj - orbR - 0.1);
        const t1 = Math.min(tProj + orbR + 0.1, 9, blockT - 0.01);
        for (let t = t0; t <= t1; t += BR * 0.45) {
          const c = this._cellAt(rPos.x + rDir.x * t, rPos.y + rDir.y * t, rPos.z + rDir.z * t);
          if (c >= 0 && this.alive[c]) { brickC = c; brickT = t; break; }
        }
      }
    }
    const len = isFinite(blockT) || isFinite(brickT)
      ? Math.max(0.2, Math.min(blockT, brickT)) : 6;
    // v2.62: telemetría del último disparo (depuración en consola/visor)
    this._lastShot = { rPos, rDir, brickC, brickT, blockT };
    // haz: núcleo violeta-blanco + glow aditivo — EN EL RIG (misma
    // convención que el resto del nivel; lookAt manual por si acaso)
    const core = new THREE.Mesh(
      new THREE.BoxGeometry(0.008, 0.008, len),
      new THREE.MeshBasicMaterial({ color: 0xe8d9ff, transparent: true, opacity: 0.95 }),
    );
    const glow = new THREE.Mesh(
      new THREE.BoxGeometry(0.03, 0.03, len),
      new THREE.MeshBasicMaterial({
        color: 0xc9a6ff, transparent: true, opacity: 0.4,
        blending: THREE.AdditiveBlending, depthWrite: false,
      }),
    );
    const AXIS_Z = new THREE.Vector3(0, 0, 1);
    core.position.copy(rPos).addScaledVector(rDir, len / 2);
    glow.position.copy(core.position);
    core.quaternion.setFromUnitVectors(AXIS_Z, rDir);
    glow.quaternion.copy(core.quaternion);
    g.rig.add(core);
    g.rig.add(glow);
    this._beams.push({ mesh: core, glow, t: 0 });
    // pew bajito
    g.audio.playOsc(880, 220, 0.12, 'sawtooth', 0.12, 0);
    // ---- consecuencias (el más cercano gana)
    if (brickC >= 0 && brickT <= blockT) {
      if (this.layer[brickC] === 2) {
        this._shotBreak(brickC);                 // ROJO → lo rompe
      } else {
        this._absorbFx(rPos, rDir, brickT);      // interior → chispa, sin daño
      }
    } else if (isFinite(blockT)) {
      this._hitBlock('rayo');
    }
  }

  /** El disparo acierta un ladrillo ROJO: rompe UNO (sin cadena) + puntos. */
  _shotBreak(c) {
    const L = this.L, g = this.game;
    const pts = (L.layerPoints[this.layer[c]] || 10);
    this._destroyCell(c);
    this.score += pts;
    this._hudDirty = true;
    const now = performance.now();
    if (now - this._lastBreakSnd > 55) {
      this._lastBreakSnd = now;
      g.audio.playOsc(480, 240, 0.09, 'square', 0.13, 0);
      g.audio.playOsc(180 + Math.random() * 60, 80, 0.07, 'triangle', 0.1, 0.01);
      if (g.renderer.xr.isPresenting) g.haptic(1 - g.paddleHand, 0.25, 40);
    }
    // v2.63: cubitos del color de la capa + destello en el punto de impacto
    this._puff(this.wx[c], this.wy[c], this.wz[c], 3, this.layer[c]);
    this._flash(this.wx[c], this.wy[c], this.wz[c], 0.55);
    if (this.aliveBricks <= 0) this._finish(true);
  }

  /** El disparo da en una capa INTERNA (marrón/amarilla): chispa sin daño. */
  _absorbFx(rPos, rDir, t) {
    const g = this.game;
    const p = rPos.clone().addScaledVector(rDir, t);
    this._puff(p.x, p.y, p.z, 1);
    this._flash(p.x, p.y, p.z, 0.35);
    g.audio.playOsc(1200, 700, 0.05, 'sine', 0.08, 0);
  }

  /* ------------------------------- FX -------------------------------------- */
  /** v2.63 · ESCOMBROS EN CUBITOS: cada ladrillo roto suelta cubitos del
   *  COLOR DE SU CAPA (rojo/marrón/dorado) con gravedad real, giro y
   *  encogido — nada de esferas pálidas. lay = capa del ladrillo (0/1/2). */
  _puff(x, y, z, n, lay) {
    let k = 0;
    for (const d of this._debris) {
      if (d.life > 0) continue;
      d.life = 0.55 + Math.random() * 0.3;
      d.mesh.visible = true;
      d.mesh.position.set(
        x + (Math.random() - 0.5) * 0.05,
        y + (Math.random() - 0.5) * 0.05,
        z + (Math.random() - 0.5) * 0.05,
      );
      // material del COLOR DE LA CAPA del ladrillo destruido
      const lm = (lay === undefined || lay === null)
        ? ((Math.random() * 3) | 0) : lay;
      d.mesh.material = this._debrisMats[lm] || this._debrisMats[2];
      const sp = 1.7 + Math.random() * 1.7;
      d.vel.set((Math.random() - 0.5) * sp, 0.5 + Math.random() * 1.6, (Math.random() - 0.5) * sp);
      d.mesh.rotation.set(Math.random() * 3, Math.random() * 3, Math.random() * 3);
      d.mesh.scale.setScalar(0.8 + Math.random() * 0.6);
      if (++k >= n) break;
    }
  }

  /** v2.65: acepta (pos, escala) O (x, y, z, escala) — las llamadas de 4
   *  argumentos de v2.63 dejaban el sprite en NaN y el flash NO se veía. */
  _flash(pos, s, z, s4) {
    let px, py, pz, sc;
    if (typeof pos === 'number') {
      px = pos; py = s; pz = z; sc = (s4 !== undefined ? s4 : 0.6);
    } else {
      px = pos.x; py = pos.y; pz = pos.z; sc = s;
    }
    for (const f of this._flashes) {
      if (f.life > 0) continue;
      f.life = 0.32;
      f.mesh.visible = true;
      f.mesh.position.set(px, py, pz);
      f.mesh.scale.setScalar(sc);
      f.mesh.material.opacity = 0.85;
      return;
    }
  }

  _anims(dt) {
    if (this._tokCd > 0) this._tokCd -= dt;
    for (const d of this._debris) {
      if (d.life <= 0) continue;
      d.life -= dt;
      if (d.life <= 0) { d.mesh.visible = false; continue; }
      // v2.63: cubitos con GRAVEDAD REAL, giro y encogido (estilo La Locura)
      d.vel.y -= (DIMS.gravity || 9.8) * 0.72 * dt;
      d.mesh.position.addScaledVector(d.vel, dt);
      d.mesh.rotation.x += dt * 6.5;
      d.mesh.rotation.y += dt * 4.6;
      d.mesh.scale.setScalar(Math.max(0.05, Math.min(1.4, d.life * 2.4)));
    }
    for (const f of this._flashes) {
      if (f.life <= 0) continue;
      f.life -= dt;
      if (f.life <= 0) { f.mesh.visible = false; continue; }
      f.mesh.scale.multiplyScalar(1 + dt * 5.5);
      f.mesh.material.opacity = f.life * 2.4;
    }
    // v2.61: giro del portal del fondo en TODAS las fases (agujero y anillo
    // giran juntos; el glow es un sprite radial y no compite por el movimiento)
    if (this.portalSpin) {
      this.portalSpin.rotation.z += dt * (this._portalSpeed || SC.portal.rotSpeed);
    }
    // pulso del núcleo (la luz «respira» con los ladrillos restantes)
    if (this.coreLight) {
      const frac = this.totalBricks ? this.aliveBricks / this.totalBricks : 0;
      this.coreLight.intensity = (0.7 + Math.sin(performance.now() / 400) * 0.25) * (0.35 + frac * 0.65);
    }
  }

  _starsCorr(dt) {
    if (!this._corrStars) return;
    const t = performance.now() / 1000;
    for (const s of this._corrStars) {
      s.mat.opacity = s.base * Math.max(0, Math.sin(t * s.spd + s.phase));
    }
  }

  _tok(x) {
    const g = this.game;
    if (this._tokCd > 0) return;
    this._tokCd = 0.09;
    const pan = THREE.MathUtils.clamp(x / 1.2, -1, 1);
    try { g.audio.thud(pan, 0.3); } catch (e) { /* */ }
  }

  /* ------------------------------- HUD ------------------------------------- */
  _hud() {
    this._hudDirty = false;
    const c = this.hudCv.getContext('2d');
    const W = 1024, H = 214;
    c.clearRect(0, 0, W, H);
    c.fillStyle = 'rgba(8,14,30,0.78)';
    const r = 30;
    c.beginPath();
    c.moveTo(r, 8); c.arcTo(W - 8, 8, W - 8, H - 8, r); c.arcTo(W - 8, H - 8, 8, H - 8, r);
    c.arcTo(8, H - 8, 8, 8, r); c.arcTo(8, 8, W - 8, 8, r);
    c.closePath(); c.fill();
    c.strokeStyle = 'rgba(201,166,255,0.6)'; c.lineWidth = 5; c.stroke();
    c.textAlign = 'center'; c.textBaseline = 'middle';
    // TIEMPO (ámbar en alerta)
    const alerta = this.time <= this.L.alertThreshold;
    const mm = Math.floor(this.time / 60);
    const ss = Math.floor(this.time % 60);
    c.fillStyle = alerta ? '#ff9a7a' : '#e2d6f6';
    c.font = '900 84px system-ui, sans-serif';
    c.fillText(`${mm}:${String(ss).padStart(2, '0')}`, 170, 96);
    // ladrillos restantes
    c.font = '800 40px system-ui, sans-serif';
    c.fillStyle = '#e2d6f6';
    c.fillText(tx('bricks_left', { n: this.aliveBricks }), 420, 78);
    // prórrogas (círculos de reloj: llenos = usadas, hueco = disponibles)
    for (let i = 0; i < this.L.maxExtensions; i++) {
      const x = 320 + i * 52, y = 150;
      c.strokeStyle = '#f6d34c'; c.lineWidth = 5;
      c.beginPath(); c.arc(x, y, 16, 0, Math.PI * 2);
      if (i < this.extUsed) { c.fillStyle = 'rgba(246,211,76,0.85)'; c.fill(); }
      c.stroke();
      c.strokeStyle = '#f6d34c'; c.lineWidth = 3;
      c.beginPath(); c.moveTo(x, y); c.lineTo(x, y - 9); c.stroke();
    }
    // PUNTOS
    c.font = '900 64px system-ui, sans-serif';
    c.fillStyle = '#f6d34c';
    c.fillText(tx('score_lbl', { n: this.score }), 760, 96);
    if (this._msg) {
      c.fillStyle = 'rgba(246,211,76,0.95)';
      c.font = this._msg.length > 26
        ? '800 34px system-ui, sans-serif'
        : '800 44px system-ui, sans-serif';
      c.fillText(this._msg, 512, 186);
    }
    this.hudTex.needsUpdate = true;
  }

  /** Estrella de 5 puntas en canvas (sin emojis). */
  _starPath(c, x, y, rOut) {
    const rIn = rOut * 0.42;
    c.beginPath();
    for (let i = 0; i < 5; i++) {
      const a = -Math.PI / 2 + (i * 2 * Math.PI * 2) / 5;
      const a2 = -Math.PI / 2 + ((i * 2 + 1) * Math.PI * 2) / 10;
      c.lineTo(x + Math.cos(a) * rOut, y + Math.sin(a) * rOut);
      c.lineTo(x + Math.cos(a2) * rIn, y + Math.sin(a2) * rIn);
    }
    c.closePath();
  }

  _paintBanner(res) {
    const c = this.banCv.getContext('2d');
    const W = 1024, H = 400;
    c.clearRect(0, 0, W, H);
    if (!res) { this.banTex.needsUpdate = true; return; }
    const r = 44;
    c.beginPath();
    c.moveTo(r, 10); c.arcTo(W - 10, 10, W - 10, H - 10, r); c.arcTo(W - 10, H - 10, 10, H - 10, r);
    c.arcTo(10, H - 10, 10, 10, r); c.arcTo(10, 10, W - 10, 10, r);
    c.closePath();
    c.fillStyle = 'rgba(8,14,30,0.93)'; c.fill();
    c.strokeStyle = res.col; c.lineWidth = 10; c.stroke();
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillStyle = res.col;
    c.font = '900 74px system-ui, sans-serif';
    c.fillText(res.title, 512, 92);
    c.fillStyle = '#eef2f6';
    c.font = '600 42px system-ui, sans-serif';
    c.fillText(res.sub, 512, 168);
    // ESTRELLAS (1–3 o ninguna en derrota)
    if (res.stars > 0) {
      for (let i = 0; i < 3; i++) {
        const x = 512 + (i - 1) * 130, y = 285;
        this._starPath(c, x, y, 52);
        if (i < res.stars) {
          c.fillStyle = '#f6d34c'; c.fill();
          c.strokeStyle = '#ffe9a8'; c.lineWidth = 5; c.stroke();
        } else {
          c.strokeStyle = 'rgba(246,211,76,0.35)'; c.lineWidth = 4; c.stroke();
        }
      }
    }
    c.fillStyle = '#c8ced4';
    c.font = '600 34px system-ui, sans-serif';
    c.fillText(res.foot || '', 512, res.stars > 0 ? 368 : 300);
    this.banTex.needsUpdate = true;
  }

  /* ------------------------- final y resultados ---------------------------- */
  _finish(win) {
    const g = this.game;
    const L = this.L;
    this.phase = 'result';
    this.phaseT = win ? 7.0 : 5.5;
    this._despawnBlock();
    // limpia bolas en vuelo
    for (const b of this.balls) {
      if (b.active) this._ballLost(b);
      for (const mp of this._miniPortals) { mp.t = -1; mp.grp.visible = false; }
    }
    this._gunVisible(false);
    let stars = 0;
    const frac = win ? (this.time / L.timeStart) : 0;
    if (win) {
      stars = frac >= L.star3Frac ? 3 : (frac >= L.star2Frac ? 2 : 1);
    }
    const firstTrophy = win && !this.ctrl.trophy;
    this._banner = {
      title: win ? tx('win_title') : tx('lose_title'),
      sub: win ? tx('win_score', { n: this.score }) : tx('lose_time'),
      foot: win ? (firstTrophy ? tx('win_sub') : tx('retry_sub')) : tx('lose_sub'),
      stars,
      col: win ? '#7fb069' : '#e06c5a',
    };
    this._paintBanner(this._banner);
    if (win) {
      g.confettiBurst = Math.max(g.confettiBurst, 3 + stars);
      g.audio.fanfare(true);
      if (stars >= 3) g.audio.announce(tx('win_title'), true);
      if (g.renderer.xr.isPresenting) {
        g.haptic(g.paddleHand, 0.8, 140);
        window.setTimeout(() => g.haptic(g.paddleHand, 0.5, 130), 220);
      }
      this.ctrl.onLevelWon(firstTrophy);
    } else {
      g.audio.fanfare(false);
      g.audio.announce(tx('lose_time'), true);
      this.ctrl.onLevelLost();
    }
    // ranking persistente + reporte con validación de sanidad
    this._recordResult(win, stars, firstTrophy);
    this._reportRank(win, stars);
  }

  _recordResult(win, stars, firstTrophy) {
    const a = this.ctrl;
    a.rank.push({ w: !!win, score: this.score | 0, stars: stars | 0 });
    if (a.rank.length > 10) a.rank = a.rank.slice(-10);
    if (win) { a.wins++; a.streak++; }
    else a.streak = 0;
    if (win && this.score > (a.best | 0)) a.best = this.score | 0;
    // v2.77: ¡un campeón más! (consigue la Varita Dorada por primera vez)
    // v3.6.8-SDK6 (ronda 11): el evento lleva el ID del campeonato — el panel
    // separa el embudo de Magia del de La Locura (tolerante con datos viejos).
    if (win && firstTrophy) { try { __PP_TELE.ev('champion', { id: 'magia' }); } catch (e) { /* */ } }
    try {
      localStorage.setItem(a.storageKey('rank'), JSON.stringify(a.rank));
      localStorage.setItem(a.storageKey('wins'), String(a.wins));
      localStorage.setItem(a.storageKey('streak'), String(a.streak));
      localStorage.setItem(a.storageKey('best'), String(a.best | 0));
    } catch (e) { /* */ }
    // v2.70: el RANKING MUNDIAL ya NO se publica aquí — la prueba del orbe
    // no puntúa; el mérito lo dan las VICTORIAS DE DUELO (onMatchOver).
    if (a.inited && a.rankPanel) a.rankPanel.refresh();
  }

  /** Reporte ANÓNIMO del resultado con VALIDACIÓN DE SANIDAD (los valores
   *  se recortan a rangos imposibles de falsear antes de salir del juego). */
  _reportRank(win, stars) {
    const clamp = (v, a2, b2) => Math.max(a2, Math.min(b2, v | 0));
    // v3.6.8-SDK6 (ronda 11): el champ_rank VIAJA POR __PP_TELE — así lleva la
    // versión REAL del juego (antes v2.81.0 clavada a mano), t y sid propios,
    // y RESPETA el opt-out (pp_tele=0) y el modo depuración (3 fallos cazados
    // de un plumazo). La cola persistida reintenta en el arranque siguiente si
    // el envío no sale; el reporte nunca rompe el juego (ev ya lo blinda).
    try {
      __PP_TELE.ev('champ_rank', {
        champ: 'magia',
        win: !!win,
        score: clamp(this.score, 0, this.maxScore),
        stars: clamp(stars, 0, 3),
        bricks: clamp(this.totalBricks - this.aliveBricks, 0, this.totalBricks),
        ext: clamp(this.extUsed, 0, this.L.maxExtensions),
        left: Math.max(0, Math.min(this.L.timeStart * 3, Math.round(this.time * 10) / 10)),
      });
    } catch (e) { /* el reporte nunca rompe */ }
  }

  _afterResult() {
    // v2.70 · PATRÓN ARKANOID (La Locura): tras el cartel de resultado el
    // nivel se apaga y el camino CONTINÚA — prueba superada: duelo siguiente;
    // prueba fallida: duelo anterior (el controlador ya ajustó la etapa).
    this.stop();
    this.ctrl._startDuel();
  }

  /** Arranque del nivel (usado por start() y por el reintento).
   *  v2.63 · RESET IDÉNTICO a un arranque fresco: el bug «tras perder, la
   *  pistola no dispara» venía de que el reintento NO restauraba árbitro,
   *  saque ni escena — ahora el reintento deja TODO exactamente igual que
   *  la primera vez (estado, bola, pistola, mensaje). */
  _startLevel() {
    const g = this.game;
    // --- escena + árbitro EXACTO igual que start() -------------------------
    if (!this._netParts) this._netParts = this._findNetParts();
    for (const m of this._netParts) m.visible = false;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    if (g.fanfareBanner && g.fanfareBanner.group) g.fanfareBanner.group.visible = false;
    g.confettiBurst = 0;
    g.rules.state = this.ctrl.stateName;   // el ÁRBITRO vuelve a pausa
    g.rules.message = tx('msg_enter');
    g.ball.ignoreNet = true;
    g.tossed = false;
    if (g.resetToss) g.resetToss();
    g.freezeT = 0;
    // --- nivel --------------------------------------------------------------
    this.phase = 'intro';
    this.phaseT = 2.4;
    this._banner = null;
    this._paintBanner(null);
    // v2.71: re-muestra lo que stop() ocultó (ladrillos, núcleo, fx) — cada
    // etapa empieza LIMPIA pero COMPLETA, sin restos ni ausencias.
    if (this.brickMesh) this.brickMesh.visible = true;
    if (this.coreMesh) this.coreMesh.visible = true;
    if (this.fxGroup) this.fxGroup.visible = true;
    // reconstruye la rejilla completa (orbe nuevo)
    this.alive.fill(1);
    this.aliveBricks = this.totalBricks;
    this.aliveByLayer = [0, 0, 0];
    for (let c = 0; c < this.cells; c++) {
      this.aliveByLayer[this.layer[c]]++;
      const R = this.R, S = this.S;
      let exp = false;
      const N6 = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
      for (const [dx, dy, dz] of N6) {
        const nx = this.ci[c] + dx, ny = this.cj[c] + dy, nz = this.ck[c] + dz;
        if (Math.abs(nx) > R || Math.abs(ny) > R || Math.abs(nz) > R) { exp = true; break; }
        const k2 = (nx + R) * S * S + (ny + R) * S + (nz + R);
        if (this.cellKey[k2] < 0) { exp = true; break; }
      }
      this.exposed[c] = exp ? 1 : 0;
    }
    for (let c = 0; c < this.cells; c++) this._writeCell(c, 0);
    this.score = 0;
    this.time = this.L.timeStart;   // el HUD marca el tiempo COMPLETO ya en montaje
    this._lastSec = -1;
    this.extUsed = 0;
    this._noExtAnnounced = false;
    this._despawnBlock();
    this.retryCd = 0;
    for (const b of this.balls) {
      b.active = false;
      b.waiting = false;
      b.portalT = -1;
      b.stuckT = 0;
      b.bomb = false;              // v2.65: sin bombas heredadas
      b._farT = 0;
      if (b.mesh) b.mesh.visible = false;
      for (const t of b.trail) { t.life = 0; t.sp.visible = false; }
    }
    if (this._bombGlows) for (const s of this._bombGlows) { s.visible = false; s.material.opacity = 0; }
    g.ball.bomb = false;           // v2.65: la bola del core nunca hereda bomba
    this._playT = 0;               // reloj de juego (bombas garantizadas)
    this._lastBombAt = 0;
    for (const mp of this._miniPortals) { mp.t = -1; mp.grp.visible = false; }
    this.spawnCd = 0.6;
    this._gunLast = -99;                     // el gatillo responde al instante
    this.fieldGroup.visible = true;
    this.hudGroup.visible = true;
    this._hudDirty = true;
    this._parkMainBall();
    this.ctrl._setStateSilent('present', 2.2);
    g.audio.playOsc(523, 523, 0.11, 'square', 0.11, 0);
    window.setTimeout(() => g.audio.playOsc(659, 659, 0.11, 'square', 0.11, 0), 130);
    window.setTimeout(() => g.audio.playOsc(784, 784, 0.2, 'square', 0.12, 0), 260);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 120);
  }

  /* ----------------------------- gatillo ----------------------------------- */
  /** v2.63 · GATILLO AUTOCURATIVO: montaje → salta · juego → DISPARO · y si
   *  el nivel llegó desincronizado (active=false tras un reintento raro) se
   *  RELANZA solo — la pistola responde SIEMPRE, con la partida que sea. */
  trigger() {
    if (!this.inited) return;
    if (!this.active) {
      // autocuración: el campeonato sigue activo pero el nivel no — relanza
      if (this.ctrl && this.ctrl.active) { this.start(); }
      return;
    }
    if (this.phase === 'montaje') { this._skipMontaje(); return; }
    if (this.phase === 'play') { this._fireBeam(); return; }
  }

  _gunVisible(on) {
    const g = this.game;
    if (!g.gunMounts) return;
    for (let k = 0; k < 2; k++) {
      if (g.gunMounts[k]) g.gunMounts[k].visible = !!on && k === (1 - g.paddleHand);
    }
  }

  /* --------------------------- ciclo de vida -------------------------------- */
  start() {
    const g = this.game;
    this.build();
    this.active = true;
    // escena: red fuera, marcador y rival fuera, corredor dentro
    if (!this._netParts) this._netParts = this._findNetParts();
    for (const m of this._netParts) m.visible = false;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    if (g.fanfareBanner && g.fanfareBanner.group) g.fanfareBanner.group.visible = false;
    g.confettiBurst = 0;
    g.rules.message = tx('msg_enter');
    g.rules.state = this.ctrl.stateName;   // el ÁRBITRO queda en pausa
    g.ball.ignoreNet = true;
    this._parkMainBall();
    // color de la bola principal (tinte del slot 0) con respaldo
    const m = g.ballMesh;
    if (m && m.material && !this._ballSaved) {
      this._ballSaved = {
        col: m.material.color.getHex(),
        em: m.material.emissive ? m.material.emissive.getHex() : null,
        ei: m.material.emissiveIntensity,   // v2.65: la bomba cambia la brasa
      };
      m.material.color.setHex(SC.ballColors[0]);
      if (m.material.emissive) m.material.emissive.setHex(0x0a2a33);
    }
    this._startLevel();
  }

  _findNetParts() {
    const g = this.game;
    try {
      return g.tableGroup.children.filter((m) =>
        Math.abs(m.position.z - DIMS.tableCenterZ) < 0.02 &&
        m.position.y > DIMS.tableTopY + 0.01);
    } catch (e) { return []; }
  }

  reenter() {
    if (!this.active) return;
    const g = this.game;
    g.rules.state = this.ctrl.stateName;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    for (const m of this._netParts || []) m.visible = false;
    this._parkMainBall();
    this._hudDirty = true;
  }

  stop() {
    this.active = false;
    this.phase = 'idle';
    if (!this.inited) return;
    const g = this.game;
    this._gunVisible(false);
    this._gunHintDone = false;
    this._restoreGun();   // v2.61: la pistola del artista se retira al salir
    this._despawnBlock();
    this.fieldGroup.visible = false;
    this.hudGroup.visible = false;
    // v2.71 · LIMPIEZA TOTAL (petición del artista: NINGÚN resto del nivel
    // superado en la etapa siguiente):
    //  · ladrillos y núcleo viven en el RIG (no en fieldGroup) — ocultarlos
    //    aquí es lo que evita los «ladrillos flotando» en el duelo siguiente;
    //  · fxGroup guarda escombros y destellos (el «glow perdido en el cielo»);
    //  · los HACES del láser se añadieron al RIG desde v2.62 pero stop()
    //    los retiraba de g.scene — el láser se quedaba flotando para siempre.
    if (this.brickMesh) this.brickMesh.visible = false;
    if (this.coreMesh) this.coreMesh.visible = false;
    if (this.fxGroup) this.fxGroup.visible = false;
    for (const b of this.balls) {
      if (b.mesh) b.mesh.visible = false;
      for (const t of b.trail) { t.life = 0; t.sp.visible = false; }
    }
    for (const mp of this._miniPortals) { mp.t = -1; mp.grp.visible = false; }
    for (const bm of this._beams) {
      for (const mm of [bm.mesh, bm.glow]) {
        if (!mm) continue;
        g.rig.remove(mm);      // v2.71: padre CORRECTO (viven en el rig)
        try { g.scene.remove(mm); } catch (e) { /* por si acaso */ }
        if (mm.geometry) mm.geometry.dispose();
        if (mm.material) mm.material.dispose();
      }
    }
    this._beams.length = 0;
    // red y mesa de vuelta
    for (const m2 of this._netParts || []) m2.visible = true;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = true;
    g.aiPaddleMesh.visible = true;
    g.ball.ignoreNet = false;
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    g.ball.pos.set(0, DIMS.tableTopY + DIMS.ballRadius, DIMS.tableCenterZ + 0.25);
    g.ballMesh.visible = true;
    g.ballMesh.scale.setScalar(1);
    g.ball.bomb = false;   // v2.65: la bola del core vuelve limpia
    if (g.ballMesh && g.ballMesh.material && this._ballSaved) {
      g.ballMesh.material.color.setHex(this._ballSaved.col);
      if (g.ballMesh.material.emissive && this._ballSaved.em !== null) {
        g.ballMesh.material.emissive.setHex(this._ballSaved.em);
      }
      if (g.ballMesh.material.emissiveIntensity !== undefined && this._ballSaved.ei !== undefined) {
        g.ballMesh.material.emissiveIntensity = this._ballSaved.ei;
      }
      this._ballSaved = null;
    }
  }

  /** Liberación COMPLETA de GPU (regla de la casa en Quest). */
  dispose() {
    const g = this.game;
    this.stop();
    const kill = (root) => {
      if (!root) return;
      g.rig.remove(root);
      root.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        if (o.material) {
          if (o.material.map && o.material.map.dispose) o.material.map.dispose();
          o.material.dispose();
        }
      });
    };
    kill(this.fieldGroup);
    kill(this.hudGroup);
    kill(this.fxGroup);
    for (const mp of this._miniPortals) kill(mp.grp);
    if (this.brickMesh) {
      g.rig.remove(this.brickMesh);   // v2.62: parent rig
      this.brickMesh.dispose();
    }
    if (this.coreMesh) {
      g.rig.remove(this.coreMesh);    // v2.62: parent rig
      this.coreMesh.dispose();
    }
    for (const b of this.balls) {
      if (b.mesh) {
        g.rig.remove(b.mesh);         // v2.62: parent rig
        if (b.mesh.geometry) b.mesh.geometry.dispose();
        if (b.mesh.material) b.mesh.material.dispose();
      }
      for (const t of b.trail) {
        g.rig.remove(t.sp);           // v2.62: parent rig
        if (t.sp.material) t.sp.material.dispose();
      }
    }
    this.brickMesh = this.coreMesh = null;
    this.brickGeo = this.coreGeo = this.brickMat = this.coreMat = null;
    // v2.63: textura de bisel + materiales de escombros (compartidos)
    if (this._debrisMats) {
      for (const dm of this._debrisMats) dm.dispose();
      this._debrisMats = null;
    }
    if (this._bevelTex) { this._bevelTex.dispose(); this._bevelTex = null; }
    if (this._corrStarTex) { this._corrStarTex.dispose(); this._corrStarTex = null; }
    if (this._clockTex) { this._clockTex.dispose(); this._clockTex = null; }
    if (this._relojTex) { this._relojTex.dispose(); this._relojTex = null; }
    if (this._softTex) { this._softTex.dispose(); this._softTex = null; }
    this.fieldGroup = this.hudGroup = this.fxGroup = null;
    this.hudCv = this.hudTex = this.banCv = this.banTex = null;
    this.inited = false;
  }
}

/* ============================================================================
 *  WizardController — orquestador del campeonato (v2.60): entrada, salida,
 *  ranking persistente, estados del mago, TROFEO, mesa temática y la cola
 *  hacia el nivel. SIN itinerario de partidas: el campeonato ES el nivel.
 *  ============================================================================ */
const WIZARD_SFX_KIND = {
  present: 'present', laughing: 'laugh', crazy: 'crazy', hungry: 'angry',
  surprised: 'surprised', defeated: 'sad', loosing: 'sad', picando: 'taunt',
  victory: 'victory', panic: 'panic',
};

class WizardController {
  constructor(mod, game, manifest) {
    this.mod = mod;
    this.game = game;
    this.manifest = manifest;
    this.active = false;
    this.inited = false;
    this.t = 0;
    this.state = 'idle';
    this._transient = 0;
    this.round = 1;
    // v2.70 · CAMINO DE 6 PASOS (arquitectura de 5 etapas + trofeo, idéntica
    // a La Locura): 0 duelo WIZARD Nv.1 · 1 PRUEBA orbe · 2 duelo WIZARD
    // Nv.2 (×1,22) · 3 PRUEBA orbe COMPLEJO · 4 duelo WIZARD Nv.3 JEFE
    // (×1,5) · 5 campeón (Varita Dorada en el palmarés).
    this.orbQueued = false;      // victoria de duelo pendiente de derivar al orbe
    this._replay = null;         // v2.96: rejugada en curso ({stage, round, play})
    this._orbDelay = 0;
    this.streakP = 0;
    this.streakAi = 0;
    this._lastTotal = 0;
    this._rivalOn = false;       // el WIZARD en persona (sólo DUELOS)
    this.duelWins = 0;           // victorias de DUELO (mérito del ranking mundial)
    // v2.71 · SUPERPODERES del WIZARD en duelos (motor de dos fases del
    // CLOWN: aviso «SUPERPODER» + efecto). Estado en el constructor.
    this._powerT = 0;            // s restantes del efecto activo
    this._powerCd = 8;           // s de cooldown al entrar en el duelo
    this._powerKind = '';        // 'crazyball' | 'portals'
    this._lastPower = '';
    this._pendingPower = null;   // cfg del poder armado (fase de aviso)
    this._pendT = 0;
    this._rallyFired = false;    // máximo 1 poder por rallye
    this._toward = false;        // flanco: la bola acaba de venir hacia ti
    this._ballFx = null;         // respaldo de DIMS/malla de la BOLA LOCA
    this._locaPh = 0;            // v2.72: fase del vaivén errático
    this._locaJx = 0;            // ráfaga aleatoria vigente…
    this._locaJt = 0;            // …y su contador
    this._tpCd = 0;              // v2.72: anti-bucle del teletransporte
    this._tablePortals = null;   // los DOS portales de mesa (build())
    // ranking persistente (NAMESPACE PROPIO — nunca pisa pp_arcade_*)
    let rank = [], wins = 0, streak = 0, best = 0;
    try {
      rank = JSON.parse(localStorage.getItem(this.storageKey('rank')) || '[]');
      if (!Array.isArray(rank)) rank = [];
      wins = parseInt(localStorage.getItem(this.storageKey('wins')) || '0', 10) || 0;
      streak = parseInt(localStorage.getItem(this.storageKey('streak')) || '0', 10) || 0;
      best = parseInt(localStorage.getItem(this.storageKey('best')) || '0', 10) || 0;
    } catch (e) { /* */ }
    this.rank = rank; this.wins = wins; this.streak = streak; this.best = best;
    let duelWins = 0;
    try { duelWins = parseInt(localStorage.getItem(this.storageKey('duelwins')) || '0', 10) || 0; } catch (e) { /* */ }
    this.duelWins = duelWins;
    let stage = 0;
    try { stage = parseInt(localStorage.getItem(this.storageKey('stage')) || '0', 10) || 0; } catch (e) { /* */ }
    this.stage = stage;
    let trophy = false;
    try { trophy = localStorage.getItem(this.storageKey('trophy')) === '1'; } catch (e) { /* */ }
    this.trophy = trophy;
    this.level = new OrbeMagico(this);
    this.loadLaugh();
  }

  storageKey(k) { return 'pp_champ_magia_' + k; }

  /** v2.70 · Nivel del WIZARD según la etapa del camino (como el CLOWN):
   *  etapa 0 → Nv.1 · etapas 2–3 → Nv.2 · etapas 4+ → Nv.3 (JEFE). */
  wizardLevel() {
    if (this.stage >= 4) return 2;
    if (this.stage >= 2) return 1;
    return 0;
  }

  /** v2.66: REINICIO de registros del campeonato (pedido desde Opciones
   *  del menú). Borra rank/wins/streak/best/stage/trophy de localStorage y
   *  resetea el estado VIVO (la próxima ronda ya cuenta desde cero). */
  resetRecords() {
    for (const k of ['rank', 'wins', 'streak', 'best', 'stage', 'trophy', 'duelwins']) {
      try { localStorage.removeItem(this.storageKey(k)); } catch (e) { /* */ }
    }
    this.rank = []; this.wins = 0; this.streak = 0; this.best = 0;
    this.stage = 0; this.trophy = false; this.duelWins = 0;
    this._replay = null;   // v2.96: fuera rejugadas colgadas
    try { if (this.rankPanel) this.rankPanel.refresh(); } catch (e) { /* */ }
    try { if (this.map) this.map.refresh(); } catch (e2) { /* */ }   // v2.96
  }

  /* ----------------------------- voz del mago ------------------------------ */
  voice(state) {
    const g = this.game;
    if (!g.audio || !g.audio.ctx) return;
    const kind = WIZARD_SFX_KIND[state] || state;
    if ((kind === 'laugh' || kind === 'crazy') && this._playLaugh()) return;
    if (!g.audio.playOsc) return;
    const O = (f1, f2, d, vol, dl, type) => {
      try { g.audio.playOsc(f1, f2, d, type || 'sine', vol, dl); } catch (e) { /* */ }
    };
    switch (kind) {
      case 'present': O(523, 523, 0.14, 0.12, 0); O(659, 659, 0.14, 0.12, 0.15); O(784, 988, 0.3, 0.12, 0.3); break;
      case 'crazy': for (let i = 0; i < 6; i++) O(500 + (i % 2) * 300, 1200, 0.07, 0.1, i * 0.08, 'triangle'); break;
      case 'angry': O(180, 120, 0.4, 0.16, 0, 'sawtooth'); O(150, 110, 0.3, 0.12, 0.3, 'sawtooth'); break;
      case 'surprised': O(660, 1180, 0.22, 0.14, 0); break;
      case 'sad': O(520, 260, 0.5, 0.12, 0, 'triangle'); break;
      case 'taunt': for (let i = 0; i < 3; i++) O(740, 980, 0.08, 0.1, i * 0.12); break;
      case 'victory': O(523, 523, 0.12, 0.12, 0); O(659, 659, 0.12, 0.12, 0.13); O(784, 784, 0.12, 0.12, 0.26); O(1046, 1046, 0.3, 0.12, 0.39); break;
      case 'panic': O(880, 620, 0.14, 0.15, 0, 'square'); O(880, 620, 0.14, 0.15, 0.22, 'square'); break;
      case 'powerup': O(240, 980, 0.55, 0.16, 0, 'triangle'); O(980, 1400, 0.3, 0.1, 0.5); break;
    }
  }

  /* v3.6.2-SDK2 · motor SFX del SDK de campeonatos (una instancia por
   * controlador, cache propia; assets relativos a ESTE módulo). */
  __sfxSDK() {
    if (!this.__sdkSfx) this.__sdkSfx = createSfx(import.meta.url, () => this.game);
    return this.__sdkSfx;
  }

  /* v3.6.2-SDK2 (FASE 4): la risa del mago la reproduce el SDK de
   * campeonatos (cache + lección v2.125 + silencio del arcade respetado,
   * como el orbital y La Locura). El anti-spam de 3,2 s se conserva aquí;
   * el panNode(0) del núcleo era paneo centrado (sin efecto audible) y el
   * motor canónico añade la regla de silencio de la familia. */
  loadLaugh() {
    try { this.__sfxSDK().precarga('risas.mp3'); } catch (e) { /* */ }
  }

  _playLaugh() {
    try {
      const g = this.game;
      if (!g.audio || !g.audio.ctx || g.audio.ctx.state !== 'running') return false;
      const now = Date.now();
      if (now - (this._lastLaugh || 0) < 3200) return true;
      const eng = this.__sfxSDK();
      if (!eng.tiene('risas.mp3')) {
        eng.precarga('risas.mp3');        // aún decodificando: sin gasto
        return false;
      }
      this._lastLaugh = now;
      eng.play('risas.mp3', 1.0);
      return true;
    } catch (e) { return false; }
  }

  /* ------------------------------- BSO -------------------------------------
   * v3.6.3-SDK3: el motor vive en el SDK (createMusic v1.2.0) — fundido de
   * entrada 0,8 s, resurrección v2.124, UNA MELODÍA con arcPlaying, sync
   * en vivo con rampa 0,15 s y decode v2.125, UNA sola fuente. */
  musicOn() {
    this._musSDK.on();
  }
  /* Motor de la BSO: instancia perezosa del SDK (createMusic). Los knobs
   * son los del motor v2.78+v2.124 que sustituye y van POR DEFECTO en el
   * SDK (sin el gate del tren del Oeste: aquí no hay vagón). */
  get _musSDK() {
    if (!this.__musSDK) {
      this.__musSDK = createMusic(() => this.game, {
        url: () => this.manifest && this.manifest.musicUrl,
        vol: () => this._musicEffVol(),
      });
    }
    return this.__musSDK;
  }
  /** v2.78: volumen EFECTIVO de la BSO según el ajuste global del núcleo
   *  (silencio del usuario + duck del menú + volumen pp_arcade_vol). Si el
   *  núcleo no está disponible, cae al volumen clásico del mago (0.15). */
  _musicEffVol() {
    try {
      const A = this.game && this.game.audio;
      if (!A) return MAGIA.musicVol;
      return (A.arcMute || A._arcDucked) ? 0.0001 : Math.max(0.0001, A.arcVol);
    } catch (e) { return MAGIA.musicVol; }
  }
  _syncMusicGain() {
    // sincronía en vivo + resurrección v2.124: delegadas en el SDK
    this._musSDK.sync();
  }
  musicOff() {
    // parada instantánea, como siempre: delega en el SDK
    this._musSDK.off();
  }

  build() {
    if (this.inited) return;
    this.inited = true;
    this.rival = new WizardRival(this);
    this.rival.build();
    this.cartel = new WizardCartel(this);
    this.cartel.build();
    this.rankPanel = new WizardRanking(this);
    this.rankPanel.build();
    this.powerSign = new WizardPowerSign(this);
    this.powerSign.build();
    this.map = new WizardMap(this);
    this.map.build();
    this._buildTrophy();
    this._buildTablePortals();   // v2.72: los DOS portales del superpoder
  }

  /** v2.72 · PORTALES DE MESA del superpoder «PORTALES MÁGICOS» (el
   *  ORIGINAL del WIZARD): dos AGUJEROS sobre la superficie de la mesa —
   *  uno a cada lado de la red — con el anillo portals.webp del artista
   *  girando sobre cada agujero. La bola que bota dentro de uno SALE por
   *  el otro. Construidos UNA vez (regla Quest: nada por partida), ocultos
   *  hasta que el poder los abre; _closeTablePortals los retira. */
  _buildTablePortals() {
    if (this._tablePortals) return;
    const g = this.game;
    const cz = (DIMS && DIMS.tableCenterZ != null) ? DIMS.tableCenterZ : -1.6;
    const topY = (DIMS && DIMS.tableTopY != null) ? DIMS.tableTopY : 0.76;
    const soft = softTexture();
    this._portalSoft = soft;
    const list = [];
    for (let i = 0; i < 2; i++) {
      const grp = new THREE.Group();
      // el AGUJERO: disco casi negro pegado a la superficie de la mesa
      const hole = new THREE.Mesh(
        new THREE.CircleGeometry(WIZ_PORTALS.holeR, 28),
        new THREE.MeshBasicMaterial({
          color: 0x08040f, transparent: true, opacity: 0,
          depthWrite: false,
        }),
      );
      hole.rotation.x = -Math.PI / 2;
      hole.renderOrder = 2;
      grp.add(hole);
      // el ANILLO mágico — MISMO arte del artista (portals.webp) que el
      // portal del fondo y los mini-portales del orbe, girando encima
      const ring = new THREE.Mesh(
        new THREE.PlaneGeometry(WIZ_PORTALS.ring, WIZ_PORTALS.ring),
        new THREE.MeshBasicMaterial({
          transparent: true, depthWrite: false, side: THREE.DoubleSide,
          opacity: 0,
        }),
      );
      ring.rotation.x = -Math.PI / 2;
      ring.renderOrder = 3;
      const rimg = new Image();
      rimg.onload = () => {
        const t = new THREE.Texture();
        t.colorSpace = THREE.SRGBColorSpace;
        t.image = rimg; t.needsUpdate = true;
        ring.material.map = t;
        ring.material.needsUpdate = true;
      };
      rimg.src = this.manifest.portalsUrl || '';
      grp.add(ring);
      // resplandor (pulso) + flash del teletransporte — v2.73: escala
      // ligada al anillo (los portales son MÁS GRANDES)
      const glow = new THREE.Sprite(new THREE.SpriteMaterial({
        map: soft, color: 0xffb45e, transparent: true,
        blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0,
      }));
      glow.scale.setScalar(WIZ_PORTALS.ring * 1.1);
      grp.add(glow);
      // posición: PARTE CENTRAL de la mesa — uno a cada lado de la red,
      // casi en el eje (v2.73: más grandes y más al centro, petición del
      // artista; antes diagonal hacia los lados)
      const sx = i === 0 ? 1 : -1;
      const sz = i === 0 ? 1 : -1;
      grp.position.set(
        WIZ_PORTALS.offX * sx,
        topY + 0.008,
        cz + WIZ_PORTALS.offZ * sz,
      );
      grp.visible = false;
      grp.scale.setScalar(0.001);
      g.rig.add(grp);
      list.push({ grp, hole, ring, glow, x: grp.position.x, z: grp.position.z, appear: 0, flash: 0, phase: i * Math.PI });
    }
    this._tablePortals = list;
  }

  /** Abre los DOS portales (entrada del superpoder). */
  _openTablePortals() {
    if (!this._tablePortals) this._buildTablePortals();
    for (const p of this._tablePortals) {
      p.appear = 0;
      p.flash = 0;
      p.grp.visible = true;
    }
  }

  /** Cierra los portales (fin del poder, nueva partida o salida). */
  _closeTablePortals() {
    if (!this._tablePortals) return;
    for (const p of this._tablePortals) {
      p.grp.visible = false;
      p.appear = 0;
      p.flash = 0;
    }
  }

  /** TROFEO «Varita Dorada» — el mismo del diseño (pedestal + varita con
   *  orbe arcánico); se revela al DESTRUIR el orbe por primera vez. */
  _buildTrophy() {
    const g = this.game;
    if (this.trophyGroup) return;
    const G = new THREE.Group();
    G.position.set(-1.25, 0, -0.95);
    G.rotation.y = 0.62;
    const darkMat = new THREE.MeshStandardMaterial({ color: 0x1b1626, roughness: 0.85, metalness: 0.08 });
    const goldMat = new THREE.MeshStandardMaterial({ color: 0xe8b45a, roughness: 0.35, metalness: 0.5, emissive: 0x3d2c08 });
    const orbMat = new THREE.MeshStandardMaterial({ color: 0xb48ce8, roughness: 0.25, metalness: 0.1, emissive: 0x4a2a80 });
    const peana = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.2, 0.06, 24), darkMat);
    peana.position.y = 0.03;
    G.add(peana);
    const fuste = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.034, 0.36, 12), goldMat);
    fuste.position.set(0.02, 0.26, 0);
    fuste.rotation.z = -0.42;
    G.add(fuste);
    const tipX = 0.02 + Math.sin(-0.42) * 0.18 * -1;
    const tipY = 0.26 + Math.cos(0.42) * 0.18;
    const orbe = new THREE.Mesh(new THREE.SphereGeometry(0.055, 16, 12), orbMat);
    orbe.position.set(tipX, tipY, 0);
    G.add(orbe);
    this._trophyHalo = new THREE.PointLight(0xc9a6ff, 0, 2.2);
    this._trophyHalo.position.set(0, 0.6, 0);
    G.add(this._trophyHalo);
    G.visible = !!this.trophy;   // v2.70: campeón previo — la varita ya vive en la sala
    g.rig.add(G);
    this.trophyGroup = G;
  }

  _revealTrophy() {
    if (this.trophyGroup) {
      this.trophyGroup.visible = true;
      if (this._trophyHalo) this._trophyHalo.intensity = 1.4;
      this._trophyPop = 1.2;
    }
  }

  /* =================== MESA TEMÁTICA (gris + estrellas) ==================== */
  _tableMagicOn() {
    const g = this.game;
    if (!this._tableSaved) {
      const top = g.tableGroup && g.tableGroup.getObjectByName('ppTableTop');
      this._tableSaved = (top && top.material)
        ? { mat: top.material, col: top.material.color.getHex() }
        : { mat: null, col: 0 };
      if (this._tableSaved.mat) {
        this._tableSaved.mat.color.setHex(0x2f3138);
      }
    }
    if (!this._stars) {
      const tex = starTextureMagia();
      this._starTex = tex;
      const grp = new THREE.Group();
      const stars = [];
      const hw = Math.max(0.2, (DIMS.tableHalfWidth || 0.76) - 0.10);
      const hl = Math.max(0.3, (DIMS.tableHalfLength || 1.37) - 0.12);
      for (let i = 0; i < 10; i++) {
        const mat = new THREE.MeshBasicMaterial({
          map: tex, transparent: true, depthWrite: false,
          blending: THREE.AdditiveBlending, opacity: 0, color: 0xbfe3ff,
        });
        const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat);
        m.rotation.x = -Math.PI / 2;
        m.renderOrder = 3;
        m.position.set(
          (Math.random() * 2 - 1) * hw,
          DIMS.tableTopY + 0.006 + Math.random() * 0.005,
          DIMS.tableCenterZ + (Math.random() * 2 - 1) * hl,
        );
        m.scale.setScalar(0.10 + Math.random() * 0.14);
        grp.add(m);
        stars.push({
          mesh: m, mat,
          phase: Math.random() * Math.PI * 2,
          speed: 0.45 + Math.random() * 0.5,
          base: 0.28 + Math.random() * 0.20,
          spin: (Math.random() < 0.5 ? -1 : 1) * (0.25 + Math.random() * 0.4),
        });
      }
      g.rig.add(grp);
      this._stars = { grp, stars, t: Math.random() * 10 };
    }
  }

  _starsUpdate(dt) {
    if (!this._stars) return;
    const S = this._stars;
    S.t += dt;
    for (const s of S.stars) {
      const cyc = Math.sin(S.t * s.speed + s.phase);
      s.mat.opacity = s.base * Math.max(0, cyc) * Math.max(0, cyc);
      s.mesh.rotation.z += dt * s.spin;
    }
  }

  _tableMagicOff() {
    const g = this.game;
    if (this._tableSaved) {
      if (this._tableSaved.mat) {
        this._tableSaved.mat.color.setHex(this._tableSaved.col);
      }
      this._tableSaved = null;
    }
    if (this._stars) {
      g.rig.remove(this._stars.grp);
      for (const s of this._stars.stars) {
        s.mat.dispose();
        if (s.mesh.geometry) s.mesh.geometry.dispose();
      }
      this._stars = null;
    }
    if (this._starTex) { this._starTex.dispose(); this._starTex = null; }
  }

  /** ENTRAR en el campeonato (botón del menú CRAZY → ChampLoader). */
  /* ============ v2.96 · REJUGAR etapas superadas (mapa + gatillo) ============
   *  El núcleo apunta con la pala (replayMap/replayHover) y el gatillo
   *  sobre un nodo SUPERADO relanza esa etapa con el progreso congelado:
   *  al acabar el intento (victoria O derrota) el camino real vuelve. */
  replayMap() {
    if (!this.active || !this.map || !this.map.group || !this.map.group.visible) return null;
    if (this.level && this.level.active) return null;   // en PRUEBA no
    return {
      plane: this.map.plane,
      nodesPx: this.map.nodesPx,
      imgW: this.map.IMG_W, imgH: this.map.IMG_H,
      // v2.108: MODO DEPURACIÓN — las 5 etapas seleccionables sin requisitos
      maxIdx: ppDbg() ? 4 : Math.min(this.stage | 0, 4),
    };
  }
  replayHover(idx) { if (this.map) this.map.hover(idx | 0); }
  replayLaunch(idx) {
    const g = this.game;
    if (this.level && this.level.active) return;
    if (g.net.online) { g.rules.message = T('msg_guest_mode'); return; }
    const i = idx | 0;
    // v2.108: en MODO DEPURACIÓN, CUALQUIER nodo distinto del vigente usa la
    // vía de rejugada (progreso real congelado y restaurado al terminar):
    // saltar a etapas FUTURAS no adelanta el camino en ningún caso.
    if (i >= this.stage && (!ppDbg() || i === this.stage)) {
      this.stage = i;              // nodo VIGENTE: camino normal (sin rejugada)
      return this.startChamp();
    }
    this._replay = { stage: this.stage, round: this.round, play: i + 1 };
    this.stage = i;
    g.rules.message = ppDbg()
      ? ('DEPURACIÓN · ETAPA ' + String(i + 1))
      : T('replay_up', { n: String(i + 1) });
    try { g.audio.announce(g.rules.message, true); } catch (e) { /* */ }
    this.startChamp();
  }

  startChamp() {
    const g = this.game;
    if (g.net.online) { g.rules.message = T('msg_guest_mode'); return; }
    this.build();
    this.level.stop();
    this.active = true;
    this._tableMagicOn();
    g.pendingMode = 'match';
    g.mode = 'arcade';
    g.rules.oppLabel = 'wizard';
    g.rules.startMatch('match');
    g.applyAISkill();
    g.closeMenu();
    g.resetToss();
    g.aiToss = null;
    g.demoToss = null;
    g.ai.reset();
    g.setupAIServe();
    this.round = this._replay ? this._replay.play : ((this.rank ? this.rank.length : 0) + 1);
    this.streakP = 0;
    this.streakAi = 0;
    g.freezeT = 0;
    // v2.70 · CAMINO: si la etapa actual es una PRUEBA (1 orbe · 3 orbe
    // complejo) se entra DIRECTAMENTE en ella (sin duelo del WIZARD);
    // en las etapas de lucha (0/2/4) toca el DUELO contra el mago.
    if (this.stage === 1 || this.stage === 3) {
      this.startOrb(this.stage === 3);
      return;
    }
    this._startDuel();
  }

  /** v2.70 · DUELO del camino (etapas 0/2/4): WIZARD EN PERSONA, partida de
   *  ping pong a 11 como La Locura (aiMul ×1/×1,22/×1,5 según el nivel). */
  _startDuel() {
    const g = this.game;
    this.level.stop();          // por si venimos de una prueba (restaura escena)
    this.active = true;
    this._tableMagicOn();
    g.mode = 'arcade';
    g.rules.oppLabel = 'wizard';
    g.rules.startMatch('match');
    g.applyAISkill();
    g.resetToss();
    g.aiToss = null;
    g.demoToss = null;
    g.ai.reset();
    g.setupAIServe();
    this.round = (this.rank ? this.rank.length : 0) + 1;
    this.streakP = 0;
    this.streakAi = 0;
    this._lastTotal = 0;
    g.freezeT = 0;
    // el WIZARD EN PERSONA según la REGLA FIJA (v2.71: ~50 cm a la derecha
    // del borde derecho de la mesa) y SU ESFERA delante, girando
    this._rivalOn = true;
    if (this.rival) {
      this.rival.setDuel(true);
      this.rival.sprite.visible = true;
      this.rival.stars.visible = false;
      if (this.rival.gift) this.rival.gift.visible = true;   // v2.71: esfera recuperada
      this.rival.setState('present');
    }
    // v2.71: duelo limpio de poderes previos (bola restaurada incluida)
    this._endPower();
    this._powerCd = 8;           // el primer superpoder tarda en llegar
    this._pendingPower = null;
    this._rallyFired = false;
    this.rankPanel.group.visible = true;
    this.rankPanel.refresh();
    if (this.map) { this.map.group.visible = true; this.map.refresh(); }
    const lvl = this.wizardLevel();
    g.rules.message = lvl >= 2 ? tx('wiz3_up') : (lvl >= 1 ? tx('wiz2_up') : tx('msg_duel'));
    this.cartel.show(this.round, 'duel');
    g.audio.announce(tx('announce'), true);
    this.voice('present');
    this.musicOn();
  }

  /** v2.70 · PRUEBA del camino (etapas 1/3): el ORBE MÁGICO (normal en la
   *  1, COMPLEJO en la 3). v2.63 se respeta: el mago no participa aquí. */
  startOrb(complex) {
    const g = this.game;
    // v2.106 · CARTEL EXPLICATIVO antes de entrar (todas las pruebas,
    // todos los campeonatos). Lo pinta el núcleo.
    if (this._instrK !== 'orb') {
      if (g && g.showInstrucciones) {
        this._instrK = 'orb';
        g.showInstrucciones(tx('instr_orb_t'), tx('instr_orb'), 7.5,
          () => { try { this.startOrb(complex); } catch (e) { /* */ } },
          'magia',   // v2.107: pergamino arcano de MAGIA
          { empezar: true });   // v2.130: espera al botón EMPEZAR (común)
        return;
      }
    }
    this._instrK = null;
    this.orbQueued = false;
    this._orbDelay = 0;
    this._rivalOn = false;
    this._endPower();            // v2.72: sin poderes ni portales en la prueba
    if (this.rival) {
      this.rival.setDuel(false);
      this.rival.hide();          // v2.63: el WIZARD no participa en la prueba
    }
    this.level.applyComplexity(!!complex);
    this.level.start();
    this.state = 'present';
    this._transient = 2.2;
    this.rankPanel.group.visible = true;
    this.rankPanel.refresh();
    if (this.map) { this.map.group.visible = true; this.map.refresh(); }
    this.cartel.show(this.round, 'orb');
    g.audio.announce(tx('announce'), true);
    this.voice('present');
    this.musicOn();
  }

  /** SALIR del campeonato (se juega otro modo). Todo se restaura. */
  leave() {
    if (!this.active && !this.inited) return;
    this.active = false;
    // v2.96: REJUGADA en curso — el progreso real vuelve
    if (this._replay) {
      this.stage = this._replay.stage;
      this._replay = null;
      try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e0) { /* */ }
      if (this.map) this.map.refresh();
    }
    this._rivalOn = false;
    this._endPower();            // v2.71: bola/restos de superpoder a cero
    this.orbQueued = false; this._orbDelay = 0;    // v2.70: sin derivas pendientes
    if (this.rival) this.rival.setDuel(false);
    const g = this.game;
    this.musicOff();
    g.freezeT = 0;
    if (this.level) this.level.dispose();   // libera TODO (regla Quest)
    if (g.rules.state === this.stateName) {
      g.rules.startMatch(g.mode === 'survival' ? 'survival' : 'match');
    }
    if (this.inited) {
      if (this.rival) this.rival.hide();
      if (this.rankPanel) this.rankPanel.hide();
      if (this.cartel) this.cartel.hide();
      if (this.powerSign) this.powerSign.hide();
      if (this.map) this.map.hide();
    }
    if (g.gunMounts) for (const gm of g.gunMounts) if (gm) gm.visible = false;
    this._tableMagicOff();
    if (g.rules.oppLabel === 'wizard') g.rules.oppLabel = 'cpu';
  }

  setState(state, dur) {
    this.state = state;
    this._transient = dur || 0;
    if (this.inited && this._rivalOn) this.rival.setState(state);   // v2.70: duelos
    if (this._rivalOn) this.voice(state);
  }
  _setStateSilent(state, dur) {
    this.state = state;
    this._transient = dur || 0;
    if (this.inited && this._rivalOn) this.rival.setState(state);
  }

  /* ========== v2.71 · SUPERPODERES DEL WIZARD (motor del CLOWN) =========== */

  /** ¿Toca lanzar superpoder? SOLO con la bola en juego y viniendo hacia el
   *  jugador (para ESTORBAR el golpeo, no cuando el punto está muerto).
   *  Puertas: duelo activo, rally vivo, cooldown, máximo 1 por rallye,
   *  azar y que no haya ya un aviso colgando — idéntico al CLOWN. */
  maybeTriggerPower() {
    if (!this.active || !this._rivalOn || this._pendingPower) return;
    if (this._powerT > 0 || this._powerCd > 0) return;
    if (this.level && this.level.active) return;   // sin mago en la prueba
    const g = this.game;
    const r = g.rules;
    const ball = g.ball;
    if (!ball || !ball.vel) return;
    if (r.state !== 'rally' || this._rallyFired) { this._toward = false; return; }
    const minHits = WIZ_POWER.minRallyHits;
    if ((r.rallyHits || 0) < minHits) { this._toward = false; return; }
    // flanco: la bola ACABA de ponerse rumbo al jugador (vel.z > 0)
    const toward = ball.vel.z > 0.35;
    const edge = toward && !this._toward;
    this._toward = toward;
    if (!edge) return;
    if (Math.random() < WIZ_POWER.chance) this.firePower();
  }

  /** Lista de poderes del WIZARD — LOS SUYOS (v2.72): BOLA LOCA y
   *  PORTALES MÁGICOS (no los del CLOWN).
   *  v2.121: TODOS llevan MINIATURA propia en el cartel — los clásicos
   *  bola loca/portales estrenan powerloca.png y powerportal.png. */
  _powerList() {
    // v2.120: BOLA DE FUEGO y NOCHE ARCANA entran en la rotación — 4 en total
    return [
      Object.assign({ kind: 'crazyball', duration: WIZ_POWER.duration, icon: 'powerloca.png' }, LOCA_BALL),
      Object.assign({ kind: 'portals', duration: WIZ_PORTALS.duration, icon: 'powerportal.png' }, WIZ_PORTALS),
      { kind: 'fuego', duration: 8, icon: 'powerfuego.png' },
      { kind: 'sombras', duration: 7, icon: 'powersombras.png' },
    ];
  }

  /** FASE 1 — AVISO: elige el poder, muestra el cartel «SUPERPODER DE
   *  WIZARD!» (anclado a la cabeza, arte superpoder.webp) con su voz y
   *  congela la partida el tiempo del aviso (el CLOWN lo hace igual). */
  firePower(forceKind) {
    const g = this.game;
    let list = this._powerList().filter((p) => p && p.kind);
    if (!list.length) return;
    if (forceKind) {
      const hit = list.filter((p) => p.kind === forceKind);
      if (hit.length) list = hit;
    } else if (list.length > 1) {
      const alt = list.filter((p) => p.kind !== this._lastPower);
      if (alt.length) list = alt;
    }
    const cfg = list[(Math.random() * list.length) | 0];
    const warn = WIZ_POWER.warn;
    this._pendingPower = cfg;
    this._pendT = warn;
    this._rallyFired = true;
    // el WIZARD ENLOQUECE al anunciar su poder (sólo arte + voz del aviso)
    this._setStateSilent('crazy', Math.min(3.4, Math.max(2.2, warn * 1.3)));
    // v2.120: el cartel muestra el ICONO del poder anunciado si lo tiene
    this.powerSign.show(cfg.icon ? this._A(cfg.icon) : null);
    // v3.6.2-SDK2: congela() del SDK (patrón locura v2.40, una sola fuente)
    congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1);
    this.voice('powerup');
    g.rules.message = tx('pw_warn');
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.6, 200);
  }

  /** FASE 2: el aviso terminó — el poder ENTRA en juego (si el punto
   *  sigue vivo; si no, se guarda para el siguiente rallye). */
  _launchPending() {
    const cfg = this._pendingPower;
    this._pendingPower = null;
    this._pendT = 0;
    if (!cfg) return;
    const g = this.game;
    if (g.rules.state !== 'rally') {
      // el punto murió durante el aviso: sin efecto, reintentará pronto
      this._powerCd = 3;
      this._rallyFired = false;
      return;
    }
    const dur = (cfg && cfg.duration) || WIZ_POWER.duration;
    this._powerKind = cfg.kind;
    this._lastPower = cfg.kind;
    this._powerT = dur;
    this._powerCd = WIZ_POWER.cooldown + dur;
    if (cfg.kind === 'crazyball') this._applyBallFx(cfg);
    else if (cfg.kind === 'portals') {
      // PORTALES MÁGICOS: dos agujeros sobre la mesa durante «dur» s
      this._openTablePortals();
      this._tpCd = 0;
    } else if (cfg.kind === 'fuego') {
      // v2.120 · BOLA DE FUEGO: la bola ARDE (tinta brasa + estela de fuego
      // aditiva) mientras dure el poder.
      this._startFuego();
    } else if (cfg.kind === 'sombras') {
      // v2.120 · NOCHE ARCANA: el salón se APAGA y sólo la bola brilla.
      this._startSombras();
    }
    g.rules.message = cfg.kind === 'crazyball' ? tx('pw_ball')
      : cfg.kind === 'portals' ? tx('pw_portal')
      : cfg.kind === 'fuego' ? tx('pw_fuego') : tx('pw_sombras');
  }

  /** BOLA LOCA (v2.72 — el ORIGINAL del WIZARD): la bola se hace MÁS
   *  GRANDE (x1,65, el radio físico DIMS.ballRadius acompaña para que
   *  botes/golpes sigan siendo fieles), CAMBIA DE COLOR sin parar (el
   *  ciclo arcoíris lo anima update()) y el movimiento errático llega
   *  con el vaivén lateral del update. La IA y las predicciones leen
   *  DIMS en vivo y se adaptan. */
  _applyBallFx(cfg) {
    if (this._ballFx) return;
    const g = this.game;
    const m = g.ballMesh;
    if (!m || !m.material) return;
    const scale = THREE.MathUtils.clamp(cfg.scale || LOCA_BALL.scale, 1.2, 2.2);
    this._ballFx = {
      r: DIMS.ballRadius,
      col: m.material.color.getHex(),
      em: m.material.emissive ? m.material.emissive.getHex() : 0x555044,
      ei: m.material.emissiveIntensity !== undefined ? m.material.emissiveIntensity : undefined,
    };
    DIMS.ballRadius = this._ballFx.r * scale;
    m.scale.setScalar(scale);
    // arranca MORADO arcano; el ciclo de color lo lleva update()
    m.material.color.setHex(0x8a4fff);
    if (m.material.emissive) m.material.emissive.setHex(0x3c1a80);
    this._locaPh = 0;
    this._locaJx = 0;
    this._locaJt = 0;
  }

  /** Restaura la bola (tamaño y color originales) tras el poder. */
  _restoreBall() {
    if (!this._ballFx) return;
    const f = this._ballFx;
    this._ballFx = null;
    DIMS.ballRadius = f.r;
    const m = this.game.ballMesh;
    if (m && m.material) {
      m.scale.setScalar(1);
      m.material.color.setHex(f.col);
      if (m.material.emissive) m.material.emissive.setHex(f.em);
      if (m.material.emissiveIntensity !== undefined && f.ei !== undefined) {
        m.material.emissiveIntensity = f.ei;
      }
    }
  }

  /** Fin del superpoder (timer agotado, salida del duelo o partida nueva). */
  _endPower() {
    this._powerT = 0;
    this._powerKind = '';
    this._restoreBall();
    this._closeTablePortals();   // v2.72: los portales se cierran también
    this._tpCd = 0;
    this._endFuego();            // v2.120: bola vuelve a su tinta + sin estela
    this._endSombras();          // v2.120: el salón vuelve a la luz
  }

  /* ======== v2.120 · TERCER Y CUARTO SUPERPODER DEL WIZARD ================
   *  BOLA DE FUEGO: la bola ARDE — tinta brasa + emisor alto + ESTELA de
   *  fuego (pool de 16 sprites aditivos que nacen en la bola, suben,
   *  encogen y se apagan). Física intacta: sólo arte + atención.
   *  NOCHE ARCANA: el salón se APAGA (toneMappingExposure animado) y la
   *  bola se vuelve una LUNA ARCANAI — emisor cian fuerte + halo aditivo
   *  que la persigue. VR comfort: sin flashes duros, envolvente suave.
   *  ======================================================================== */
  _A(p) {
    try { return new URL('./assets/' + p, import.meta.url).href; }
    catch (e) { return ''; }
  }
  _texFuego() {
    if (this._fuegoTex) return this._fuegoTex;
    const cv = document.createElement('canvas');
    cv.width = 64; cv.height = 64;
    const c = cv.getContext('2d');
    const g = c.createRadialGradient(32, 32, 2, 32, 32, 30);
    g.addColorStop(0, 'rgba(255,242,180,1)');
    g.addColorStop(0.4, 'rgba(255,160,50,0.9)');
    g.addColorStop(0.75, 'rgba(230,70,20,0.4)');
    g.addColorStop(1, 'rgba(160,20,0,0)');
    c.fillStyle = g; c.fillRect(0, 0, 64, 64);
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    this._fuegoTex = t;
    return t;
  }
  _buildFuegoPool() {
    const g = this.game;
    if (this._fuegoPool) return;
    const grp = new THREE.Group();
    const tex = this._texFuego();
    const parts = [];
    for (let i = 0; i < 16; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: tex, transparent: true, depthWrite: false,
        blending: THREE.AdditiveBlending, opacity: 0,
      }));
      s.renderOrder = 33;
      s.visible = false;
      grp.add(s);
      parts.push({ s, life: 0, t: 0, vx: 0, vy: 0, vz: 0, r0: 0.09 });
    }
    grp.visible = false;
    g.rig.add(grp);
    this._fuegoPool = { grp, parts };
  }
  _startFuego() {
    const g = this.game;
    const m = g.ballMesh;
    if (m && m.material && !this._fuegoFx) {
      this._fuegoFx = {
        col: m.material.color.getHex(),
        em: m.material.emissive ? m.material.emissive.getHex() : null,
        ei: m.material.emissiveIntensity,
      };
      m.material.color.setHex(0xff5a12);
      if (m.material.emissive) m.material.emissive.setHex(0xff3608);
      if (m.material.emissiveIntensity !== undefined) m.material.emissiveIntensity = 0.95;
    }
    this._buildFuegoPool();
    this._fuegoPool.grp.visible = true;
    this._fuegoT = 0;
    try { g.audio.playNoise(0.5, 300, 0.7, 0.07, 0); } catch (e) { /* */ }
  }
  _updateFuego(dt) {
    const g = this.game;
    if (!this._fuegoPool) return;
    const ball = g.ball;
    this._fuegoT = (this._fuegoT || 0) - dt;
    if (ball && ball.pos && this._fuegoT <= 0) {
      this._fuegoT = 0.028;                       // ~35 bocanadas/s
      for (const p of this._fuegoPool.parts) {
        if (p.life > 0) continue;
        p.life = 0.34 + Math.random() * 0.20;
        p.t = 0;
        p.s.position.copy(ball.pos);
        p.vx = (Math.random() - 0.5) * 0.35;
        p.vy = 0.45 + Math.random() * 0.55;
        p.vz = (Math.random() - 0.5) * 0.35;
        p.r0 = 0.055 + Math.random() * 0.06;
        p.s.material.rotation = Math.random() * Math.PI;
        p.s.visible = true;
        break;
      }
    }
    for (const p of this._fuegoPool.parts) {
      if (p.life <= 0) continue;
      p.t += dt;
      const f = 1 - p.t / p.life;
      if (f <= 0) { p.life = 0; p.s.visible = false; p.s.material.opacity = 0; continue; }
      p.s.position.x += p.vx * dt;
      p.s.position.y += p.vy * dt;
      p.s.position.z += p.vz * dt;
      const sc = p.r0 * (0.5 + 0.9 * f);
      p.s.scale.set(sc, sc, 1);
      p.s.material.opacity = 0.85 * f;
    }
  }
  _endFuego() {
    if (!this._fuegoFx) return;
    const g = this.game;
    const m = g.ballMesh;
    const f = this._fuegoFx;
    this._fuegoFx = null;
    if (m && m.material) {
      m.material.color.setHex(f.col);
      if (m.material.emissive && f.em !== null) m.material.emissive.setHex(f.em);
      if (m.material.emissiveIntensity !== undefined && f.ei !== undefined) {
        m.material.emissiveIntensity = f.ei;
      }
    }
    if (this._fuegoPool) {
      this._fuegoPool.grp.visible = false;
      for (const p of this._fuegoPool.parts) {
        p.life = 0; p.s.visible = false; p.s.material.opacity = 0;
      }
    }
  }
  _buildSombras() {
    const g = this.game;
    if (this._sombraGrp) return;
    const grp = new THREE.Group();
    // halo que persigue a la bola (renderOrder alto: encima de todo)
    const cv = document.createElement('canvas');
    cv.width = 128; cv.height = 128;
    const c = cv.getContext('2d');
    const rg = c.createRadialGradient(64, 64, 2, 64, 64, 62);
    rg.addColorStop(0, 'rgba(210,240,255,0.95)');
    rg.addColorStop(0.35, 'rgba(120,200,255,0.5)');
    rg.addColorStop(1, 'rgba(40,120,255,0)');
    c.fillStyle = rg; c.fillRect(0, 0, 128, 128);
    const tex = new THREE.CanvasTexture(cv);
    tex.colorSpace = THREE.SRGBColorSpace;
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: tex, transparent: true, depthWrite: false, depthTest: false,
      blending: THREE.AdditiveBlending, opacity: 0,
    }));
    halo.renderOrder = 61;
    halo.visible = false;
    grp.add(halo);
    grp.visible = false;
    g.rig.add(grp);
    this._sombraGrp = grp;
    this._sombraHalo = halo;
  }
  _startSombras() {
    const g = this.game;
    this._buildSombras();
    this._sombraGrp.visible = true;
    this._sombraT = 0;
    // tinta de la bola (se restaura en _endSombras)
    const m = g.ballMesh;
    if (m && m.material && !this._sombraBall) {
      this._sombraBall = {
        col: m.material.color.getHex(),
        em: m.material.emissive ? m.material.emissive.getHex() : null,
      };
    }
    // guardamos la exposición UNA vez (el núcleo la fija a 1,05 y no la toca)
    if (this._expoWas === undefined) {
      this._expoWas = (g.renderer && g.renderer.toneMappingExposure !== undefined)
        ? g.renderer.toneMappingExposure : 1.05;
    }
    try { g.audio.playOsc(220, 55, 0.9, 'sine', 0.12, 0); } catch (e) { /* */ }
  }
  _updateSombras(dt) {
    const g = this.game;
    if (this._sombraGrp === undefined || !this._sombraGrp) return;
    this._sombraT += dt;
    const dur = 7;
    const env = Math.pow(Math.sin(Math.min(1, this._sombraT / dur) * Math.PI), 0.7);
    // el salón se apaga (mínimo 0,30: el jugador NUNCA queda a ciegas)
    if (g.renderer && g.renderer.toneMappingExposure !== undefined) {
      g.renderer.toneMappingExposure = Math.max(0.30,
        (this._expoWas !== undefined ? this._expoWas : 1.05) * (1 - 0.72 * env));
    }
    // la bola se vuelve LUNA ARCANA + halo que la persigue
    const m = g.ballMesh;
    if (m && m.material) {
      m.material.color.setHex(0xbfe6ff);
      if (m.material.emissive) m.material.emissive.setHex(0x2f8fe0);
      if (m.material.emissiveIntensity !== undefined) m.material.emissiveIntensity = 1.5;
    }
    const ball = g.ball;
    const halo = this._sombraHalo;
    if (halo) {
      halo.visible = true;
      if (ball && ball.pos) halo.position.copy(ball.pos);
      const pul = 0.30 + Math.sin(this._sombraT * 3.1) * 0.05;
      halo.scale.setScalar(pul + (DIMS.ballRadius || 0.02) * 5);
      halo.material.opacity = 0.85 * Math.max(0.25, env);
    }
  }
  _endSombras() {
    if (this._sombraGrp === undefined || !this._sombraGrp) return;
    const g = this.game;
    // la exposición VUELVE EXACTA a su valor de fábrica
    if (g.renderer && g.renderer.toneMappingExposure !== undefined &&
        this._expoWas !== undefined) {
      g.renderer.toneMappingExposure = this._expoWas;
    }
    // la bola recupera SU tinta (la luna arcana no se queda pegada)
    const m = g.ballMesh;
    if (m && m.material && this._sombraBall) {
      m.material.color.setHex(this._sombraBall.col);
      if (m.material.emissive && this._sombraBall.em !== null) {
        m.material.emissive.setHex(this._sombraBall.em);
      }
      this._sombraBall = null;
    }
    this._sombraGrp.visible = false;
    if (this._sombraHalo) { this._sombraHalo.visible = false; this._sombraHalo.material.opacity = 0; }
    this._sombraT = 0;
  }

  /* --- ganchos de partidas del núcleo (v2.70: DUELOS contra el mago) ----- */
  /** Un punto acaba de puntuarse — personalidad del WIZARD, igual que el
   *  CLOWN en La Locura (SÓLO en duelos; en la prueba el árbitro duerme). */
  onPoint(it) {
    if (!this.active || !this._rivalOn || !it || it.survival) return;
    if (it.winner === 'player') {
      this.streakP++;
      this.streakAi = 0;
      const hits = it.rallyHits || 0;
      if (hits >= 6) {
        // combo del jugador: el mago pierde los papeles
        this.setState('hungry', 2.6);
      } else if (hits >= 3 || this.streakP >= 2) {
        this.setState('surprised', 1.7);
      } else {
        this.setState('surprised', 1.2);
      }
    } else {
      this.streakAi++;
      this.streakP = 0;
      if (this.streakAi >= 2) this.setState('crazy', 3.4);
      else this.setState('laughing', 2.4);
    }
  }

  /** Fin del DUELO: ranking persistente + camino (v2.70, igual que La
   *  Locura): ganar un WIZARD par (etapas 0/2) deriva a la PRUEBA del orbe;
   *  ganar el Nv. 3 (etapa 4) = ¡CAMPEÓN! + LOGRO «Varita Dorada» al
   *  palmarés. Perder = repites el paso actual. */
  onMatchOver(winner) {
    if (!this.active || !this._rivalOn) return;
    const g = this.game;
    const w = winner === 'player';
    const p = g.rules.scorePlayer;
    const a = g.rules.scoreAi;
    this.rank.push({ w, score: p | 0, stars: w ? 1 : 0, duel: true });
    if (this.rank.length > 10) this.rank = this.rank.slice(-10);
    if (w) {
      this.wins++;
      this.streak++;
      this.duelWins++;
      try { localStorage.setItem(this.storageKey('duelwins'), String(this.duelWins)); } catch (e) { /* */ }
      if (this._replay) {
        // v2.96: REJUGADA — victoria real, pero el camino NO avanza
      } else if (this.stage >= 5) {
        // ya campeón: auto-revancha libre (sin camino que recorrer)
      } else if (this.stage === 4) {
        // ¡¡CAMPEÓN!! — LOGRO «Varita Dorada» registrado en el palmarés
        this.trophy = true;
        try { localStorage.setItem(this.storageKey('trophy'), '1'); } catch (e) { /* */ }
        this._setStage(5);
        g.rules.stateTimer = 1e9;   // sin auto-revancha: brilla la varita
        g.rules.message = tx('trophy_get');
        g.confettiBurst = Math.max(g.confettiBurst, 6);
        g.audio.announce(tx('trophy_get'), true);
        // v2.128: INSIGNIA «¡CONSEGUIDO!» en grande (panel del núcleo)
        try { const C = window.__PP_CORE; if (C && C.showChampConseguido) C.showChampConseguido('magia'); } catch (e) { /* */ }
        if (g.renderer.xr.isPresenting) {
          g.haptic(g.paddleHand, 1.0, 300);
          window.setTimeout(() => g.haptic(g.paddleHand, 0.8, 240), 400);
        }
        this._revealTrophy();
        if (this.rankPanel) this.rankPanel.refresh();
        if (this.map) this.map.refresh();
      } else if (this.stage % 2 === 0) {
        // vencer a un WIZARD par manda a la PRUEBA del orbe que toque
        this._setStage(this.stage + 1);
        this.orbQueued = true;
        this._orbDelay = 4.4;
        g.rules.stateTimer = 1e9;   // sin auto-revancha: el camino avanza
      } else {
        this._setStage(this.stage + 1);
      }
    } else {
      this.streak = 0;
      // perder REPITE el paso actual (misma etapa)
    }
    try {
      localStorage.setItem(this.storageKey('rank'), JSON.stringify(this.rank));
      localStorage.setItem(this.storageKey('wins'), String(this.wins));
      localStorage.setItem(this.storageKey('streak'), String(this.streak));
    } catch (e) { /* */ }
    // v2.70 · RANKING MUNDIAL: cada VICTORIA de duelo se publica (victorias
    // de duelo acumuladas = mérito; 🏆 si esa victoria dio el logro).
    // Silencioso: si no hay red, no pasa nada y la partida sigue igual.
    try {
      const W = (typeof window !== 'undefined' && window.__PP_WORLD);
      if (w && W && typeof W.submit === 'function') {
        let nm = '';
        try { nm = String(localStorage.getItem('pp_player_name') || '').trim().slice(0, 12); } catch (e2) { /* */ }
        Promise.resolve(W.submit('magia', {
          n: nm || 'Anónimo',
          p: this.duelWins | 0,
          a: this.trophy ? '🏆' : '✔',
        })).catch(() => { /* nunca rompe */ });
      }
    } catch (e3) { /* */ }
    this.round = this._replay ? this._replay.play : this.rank.length + 1;
    // v2.96: REJUGADA terminada (ganada o perdida) — el progreso REAL vuelve
    if (this._replay) {
      this.stage = this._replay.stage;
      this.round = this._replay.round;
      try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e8) { /* */ }
      if (w) {
        g.rules.message = T('replay_done');
        try { g.audio.announce(T('replay_done'), true); } catch (e9) { /* */ }
      }
      this._replay = null;
    }
    if (this.rankPanel) this.rankPanel.refresh();
    if (this.map) this.map.refresh();   // progreso del mapa
    this.musicOff();            // la partida terminó — se detiene la BSO
    if (w) {
      this.setState('defeated', 5);
    } else {
      this.setState('victory', 5);
      if (this.inited && this.rival) this.rival.stars.visible = true;
    }
  }

  aiMul() {
    const g = GAME;
    if (!CTRL || !CTRL.active || !CTRL._rivalOn || !g ||
        g.rules.oppLabel !== 'wizard') return 1;
    return [1, 1.22, 1.5][CTRL.wizardLevel()] || 1;
  }

  /** El JUGADOR destruyó el orbe. v2.70: la prueba NO da el trofeo — avanza
   *  el camino (etapa +1); tras el cartel de resultado, el nivel devuelve
   *  el control al DUELO siguiente (patrón ARKANOID de La Locura). */
  onLevelWon() {
    this._setStateSilent('defeated', 5);
    if (this.active && (this.stage === 1 || this.stage === 3)) {
      if (this._replay) {   // v2.96: REJUGADA — el camino se queda como estaba
        const g2 = this.game;
        g2.rules.message = T('replay_done');
        try { g2.audio.announce(T('replay_done'), true); } catch (e9) { /* */ }
        this.stage = this._replay.stage; this.round = this._replay.round;
        try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e8) { /* */ }
        this._replay = null;
      } else {
        this._setStage(this.stage + 1);
      }
      if (this.map) this.map.refresh();
    }
  }

  /** El tiempo venció con orbe entero: v2.70 «vuelves al paso anterior» —
   *  perder la prueba devuelve al DUELO previo (igual que el ARKANOID de
   *  La Locura); tras el cartel de resultado el nivel te lleva a él. */
  onLevelLost() {
    this._setStateSilent('victory', 4);
    if (this.active && (this.stage === 1 || this.stage === 3)) {
      if (this._replay) {   // v2.96: REJUGADA — el camino real vuelve
        this.stage = this._replay.stage; this.round = this._replay.round;
        try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e8) { /* */ }
        this._replay = null;
      } else {
        this._setStage(this.stage - 1);
      }
      if (this.map) this.map.refresh();
    }
  }

  _setStage(s) {
    this.stage = s | 0;
    try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e) { /* */ }
    // v2.77: avance del campeonato (telemetría anónima, igual que la Locura)
    try { __PP_TELE.ev('stage', { n: this.stage, id: 'magia' }); } catch (e) { /* */ }
    // v2.85 · MOOD POR ETAPA del decorado de sala (room): en la etapa 4
    // (DUELO FINAL contra WIZARD Nv. 3 JEFE) el laboratorio se baña en
    // luz arcana violeta; en el resto vuelve el ámbar de las velas. Guard.
    try { if (GAME && GAME.champRoom) GAME.champRoom.useVariant(s === 4 ? 'final' : null); } catch (e) { /* */ }
  }

  update(dt) {
    if (!this.active || !this.inited) return;
    const g = this.game;
    const lv = this.level;
    const r = g.rules;
    this.t += dt;
    if (this.rival) this.rival.update(dt, this.t);   // v2.70: también en duelos
    this.cartel.update(dt);
    this.powerSign.update(dt);
    this.map.update(dt);
    this._syncMusicGain();   // v2.78: la BSO sigue en vivo el ajuste global
    // v2.72 · SUPERPODERES PROPIOS DEL WIZARD EN PLENO DUELO (sólo con el
    // mago en persona; la prueba del orbe sigue sin mago ni poderes).
    // Misma secuencia de siempre: aviso pendiente → efecto → cooldown.
    if (this._rivalOn) {
      if (this._pendingPower) {
        this._pendT -= dt;
        if (this._pendT <= 0) this._launchPending();
      }
      if (this._powerT > 0) {
        this._powerT -= dt;
        const ball = g.ball;
        const rally = r.state === 'rally';
        // v2.120: los dos poderes nuevos viven en SU update (mismo cerrojo)
        if (this._powerKind === 'fuego') this._updateFuego(dt);
        if (this._powerKind === 'sombras') this._updateSombras(dt);
        if (this._powerKind === 'crazyball') {
          /* --- BOLA LOCA: cambia de color + movimiento errático -------- */
          const m = g.ballMesh;
          if (m && m.material) {
            const hue = (this.t * LOCA_BALL.hueSpeed) % 1;
            m.material.color.setHSL(hue, 0.9, 0.58);
            if (m.material.emissive) m.material.emissive.setHSL(hue, 0.9, 0.22);
          }
          if (ball && ball.vel && rally) {
            // vaivén lateral sinusoidal + ráfagas aleatorias cortas
            this._locaPh += dt;
            this._locaJt -= dt;
            if (this._locaJt <= 0) {
              this._locaJt = LOCA_BALL.jitterEvery;
              this._locaJx = (Math.random() - 0.5) * 2 * LOCA_BALL.jitter;
            }
            const ax = Math.sin(this._locaPh * LOCA_BALL.swayFreq) *
              LOCA_BALL.swayAmp + this._locaJx;
            ball.vel.x += ax * dt;
            const cap = DIMS.maxBallSpeed;
            if (ball.vel.lengthSq() > cap * cap) ball.vel.setLength(cap);
          }
        } else if (this._powerKind === 'portals') {
          /* --- PORTALES MÁGICOS: anillos girando + teletransporte ------ */
          const TP = this._tablePortals;
          if (TP) {
            const topY = DIMS.tableTopY;
            const rB = DIMS.ballRadius;
            for (const p of TP) {
              // aparición (escala) + giro del anillo + pulso del glow
              if (p.appear < 1) p.appear = Math.min(1, p.appear + dt / 0.35);
              const k = 1 - Math.pow(1 - p.appear, 3);
              p.grp.scale.setScalar(0.25 + 0.75 * k);
              p.hole.material.opacity = 0.92 * k;
              p.ring.material.opacity = k;
              p.ring.rotation.z += dt * 2.6;
              p.glow.material.opacity = 0.30 + Math.sin(this.t * 5 + p.phase) * 0.10;
              if (p.flash > 0) {
                p.flash = Math.max(0, p.flash - dt * 2.4);
                p.glow.material.opacity += p.flash * 0.65;
              }
            }
            // TELETRANSPORTE: la bola que bota dentro de un agujero SALE
            // por el otro (post-física: el bote del núcleo ya ocurrió y
            // la bola asciende — la movemos al agujero hermano)
            if (this._tpCd > 0) this._tpCd -= dt;
            if (ball && ball.vel && rally && TP.length === 2 && this._tpCd <= 0 &&
                ball.vel.y > 0.15 && ball.pos.y - rB <= topY + 0.06) {
              for (let i = 0; i < 2; i++) {
                const p = TP[i];
                const dx = ball.pos.x - p.x;
                const dz = ball.pos.z - p.z;
                if (dx * dx + dz * dz > WIZ_PORTALS.holeR * WIZ_PORTALS.holeR) continue;
                const q = TP[1 - i];   // el OTRO portal
                const cx = DIMS.tableCenterZ;   // centro de la mesa (z)
                const ndx = 0 - q.x;
                const ndz = cx - q.z;
                const nl = Math.hypot(ndx, ndz) || 1;
                ball.pos.set(q.x, topY + rB + 0.02, q.z);
                ball.vel.y = Math.max(ball.vel.y, WIZ_PORTALS.pop);
                // empujón hacia el centro: no re-entra en el mismo portal
                ball.vel.x += (ndx / nl) * WIZ_PORTALS.centerNudge;
                ball.vel.z += (ndz / nl) * WIZ_PORTALS.centerNudge;
                this._tpCd = WIZ_PORTALS.cd;
                q.flash = 1;           // destello en el portal de SALIDA
                p.flash = 0.5;         // y uno menor en el de ENTRADA
                try {
                  g.audio.playOsc(420, 1660, 0.16, 'sine', 0.16, 0);
                  g.audio.playOsc(210, 90, 0.22, 'triangle', 0.08, 0.02);
                } catch (e) { /* */ }
                if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.35, 90);
                break;
              }
            }
          }
        }
        if (this._powerT <= 0) this._endPower();   // vuelta a la normalidad
      } else if (this._powerCd > 0) {
        this._powerCd -= dt;
      }
      if (r.state !== 'rally') this._rallyFired = false;
      this.maybeTriggerPower();
    }
    this._starsUpdate(dt);
    if (this._trophyPop > 0) {
      this._trophyPop -= dt;
      const s = 1 + Math.sin(Math.max(0, this._trophyPop) * 6) * 0.08;
      if (this.trophyGroup) this.trophyGroup.scale.setScalar(s);
    }

    // v2.70 · COLA AL ORBE: tras vencer a un WIZARD par el camino avanza
    // SOLO (si el jugador no relanza un partido antes).
    if (this.orbQueued) {
      if (r.state !== 'over') {
        this.orbQueued = false;   // hubo revancha manual: se cancela
      } else {
        this._orbDelay -= dt;
        if (this._orbDelay <= 0) {
          this.orbQueued = false;
          this.startOrb(this.stage === 3);
        }
      }
    }
    // PARTIDA NUEVA (auto-revancha del árbitro tras el cartel de fin):
    // el total de puntos vuelve a 0 -> cartel + presentación de nuevo.
    // Sólo con el WIZARD en persona (duelos).
    if (this._rivalOn && this._lastTotal > 0 && r.totalPoints === 0) {
      this.round = (this.rank ? this.rank.length : 0) + 1;
      this.streakP = 0;
      this.streakAi = 0;
      if (this.rival) this.rival.stars.visible = false;
      this._setStateSilent('present', 2.2);
      this.cartel.show(this.round, 'duel');
      if (this.map) this.map.refresh();   // progreso al nuevo round
      this.voice('present');
      this.musicOn();
    }
    if (this._rivalOn) this._lastTotal = r.totalPoints;

    // reacciones del mago según cuánto orbe queda (v2.63: sólo con mago en
    // escena — desde v2.70 el mago NO está en la prueba, así que esto es
    // residual y sólo actuaría con MAGIA.wizardOn a propósito)
    if (!MAGIA.wizardOn) return;
    if (this._transient > 0) {
      this._transient -= dt;
    } else if (lv.active && lv.phase === 'play' && lv.totalBricks > 0) {
      const frac = 1 - lv.aliveBricks / lv.totalBricks;
      const want = frac >= 0.9 ? 'crazy' : frac >= 0.65 ? 'panic' : frac >= 0.35 ? 'hungry' : 'focused';
      if (this.state !== want) this._setStateSilent(want, 0);
    }
  }
}

/* ============================================================================
 *  EXPORT — la interfaz que ChampLoader entiende (mismos ganchos que
 *  La Locura: start/leave/update/onPoint/onMatchOver + la toma de control
 *  del gatillo y la física durante el nivel).
 *  ============================================================================ */
let CTRL = null;
let _ppLangFnM = null;   // v2.120: handler con nombre (no apilar listeners)
let GAME = null;
let STATE_NAME = 'champtest';

export default {
  id: 'magia',
  /** v2.128: ¿campeonato superado? (cinta ★ SUPERADO del menú) */
  isChampion() { return !!(CTRL && CTRL.trophy); },
  /** v2.130 · INTRO de campeonato: silencia la BSO privada mientras suena
   *  el vídeo de la historia del rival (hook opcional del núcleo). */
  champIntroPause(on) {
    if (!CTRL) return;
    try { on ? CTRL.musicOff() : CTRL.musicOn(); } catch (e) { /* */ }
  },
  /* v2.81 · TROQUELES DE CARTÓN de ESTE campeonato (el Wizard). El núcleo
   * lee «decor» del módulo ACTIVO y monta las piezas ancladas a la mesa,
   * orientadas al jugador y con la base EXACTAMENTE en el suelo. Los PNG
   * del artista van recortados a su propia transparencia (0 px de margen,
   * mismo pipeline validado en v2.80) en championships/magia/assets/decor/.
   * Cada campeonato tiene los SUYOS: al activar Magia se retira el set de
   * La Locura (dispose de GPU) y se monta ÉSTE; y viceversa. POSICIONES
   * medidas contra la sala de Magia — ningún troquel tapa el panel
   * RANKING (1,46/-1,7), el rival (duelos x≈1,5 z≈-3,5 · sala 1,62/-4,5),
   * el ORBE (0/-4,19), el PORTAL (0/-5,44), el MAPA de etapas (pared izq.)
   * ni el TROFEO Varita Dorada (-1,25/-0,95). */
  decor: {
    pieces: [
      // file: ruta relativa a ESTA carpeta · h: alto del arte en metros
      // (el ancho lo deduce el núcleo del aspecto real del PNG) ·
      // x/z: coordenadas del RIG (mesa centrada en z=-1.6) · sway: vaivén.
      { file: 'assets/decor/castillo.png', h: 1.30, x: -2.55, z: -2.50, sway: 0.6 },
      { file: 'assets/decor/mesita.png',   h: 0.75, x: -2.15, z: -0.68, sway: 0.5 },
      { file: 'assets/decor/mundo.png',    h: 1.25, x:  1.95, z: -0.75, sway: 0.9 },
      { file: 'assets/decor/atril.png',    h: 1.05, x:  2.45, z: -2.35, sway: 0.8 },
    ],
  },

  /* v2.85 · DECORADO DE SALA («room») — EL LABORATORIO DEL ALQUIMISTA.
   * El núcleo (createChampRoom) viste los 6 PLANOS de la sala con el
   * arte de assets/room/ SOLO mientras este campeonato está activo:
   * losas de piedra con círculo mágico, bóveda de vigas con sigilo,
   * estanterías de pociones, chimenea con caldero y pizarrón de
   * fórmulas. Al salir, la sala vuelve a su tema clásico (dispose GPU).
   * variants.final: en la etapa 4 (DUELO FINAL vs. WIZARD JEFE) el
   * _setStage pide el mood «final» y el laboratorio se baña en luz
   * arcana violeta. Medidas reales: suelo/techo 6,10 × 7,90 m ·
   * frontal/trasera 6,10 × 2,85 m · laterales 7,90 × 2,85 m. */
  room: {
    floor: 'assets/room/suelo.jpg',
    ceil:  'assets/room/techo.jpg',
    back:  'assets/room/fondo.jpg',      // trasera: estanterías + luna
    front: 'assets/room/frente.jpg',     // pared del WIZARD: chimenea
    left:  'assets/room/izquierda.jpg',  // arco + espejo arcano
    right: 'assets/room/derecha.jpg',    // mesas de alquimia
    variants: {
      final: { tint: 0x9a7fd8 },         // ritual arcana del duelo JEFE
    },
  },

  get controller() { return CTRL; },

  /** ctx = { game, id, stateName } — lo entrega ChampLoader. */
  init(ctx) {
    if (!DIMS || !stepPhysics || !T) {
      throw new Error('magia: window.__PP_CORE no disponible (¿se cargó fuera del juego?)');
    }
    GAME = ctx.game;
    STATE_NAME = ctx.stateName || STATE_NAME;
    SC = sceneConfig();
    // v2.71 · REGLA FIJA de duelos con el DIMS real: ~0,50 m a la derecha
    // del borde derecho de la mesa (halfWidth 0,7625 → DUEL_X ≈ 1,26).
    DUEL_X = ((DIMS && DIMS.tableHalfWidth) || 0.7625) + 0.5;
    TL = (window.__PP_CORE && window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
    // LAS 12 POSES REALES del mago + portal, mapa, risa y BSO (assets de su
    // propia carpeta; import.meta.url resuelve la ruta sea cual sea el host).
    const A = (p) => new URL('./assets/' + p, import.meta.url).href;
    const stateUrls = {};
    for (const st of ['present', 'idle', 'focused', 'surprised', 'hungry', 'panic',
      'laughing', 'defeated', 'victory', 'crazy', 'picando', 'loosing']) {
      stateUrls[st] = A(st + '.webp');
    }
    const manifest = {
      stateUrls,
      giftUrl: A('regalo.webp'),
      powerUrl: A('superpoder.webp'),
      mapUrl: A('mapa.webp'),
      tapaUrl: A('tapa.webp'),
      portalsUrl: A('portals.webp'),
      relojUrl: A('reloj.png'),
      gunUrl: A('pistol.glb'),
      laughUrl: A('risas.mp3'),
      musicUrl: A('bso.mp3'),
    };
    CTRL = new WizardController(this, ctx.game, manifest);
    CTRL.stateName = STATE_NAME;
    CTRL.id = ctx.id;
    // sincroniza idioma con el del núcleo en caliente
    // (v2.120: handler con nombre — cada init() apilaba un listener nuevo)
    if (_ppLangFnM) {
      document.removeEventListener('pp-lang', _ppLangFnM);
    }
    _ppLangFnM = () => {
      try {
        TL = (window.__PP_CORE && window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
      } catch (e) { /* */ }
    };
    document.addEventListener('pp-lang', _ppLangFnM);
    // FUSIÓN EN CALIENTE de los parámetros del nivel (manifest.json, bloque
    // «level»): el artista ajusta SIN tocar código. Si el nivel ya está
    // construido, los nuevos valores valen para el próximo arranque.
    try {
      fetch(new URL('./manifest.json', import.meta.url))
        .then((r) => (r.ok ? r.json() : Promise.reject(new Error('sin manifest'))))
        .then((man) => {
          if (!man || !man.level) return;
          for (const k of Object.keys(LEVEL)) {
            const v = man.level[k];
            if (v === undefined) continue;
            if (k === 'layerPoints' && Array.isArray(v) && v.length === 3) LEVEL[k] = v.slice();
            else if (typeof LEVEL[k] === 'number' && typeof v === 'number' && isFinite(v)) LEVEL[k] = v;
          }
          if (CTRL && CTRL.level) CTRL.level.L = CTRL.level.buildCfg();
        })
        .catch(() => { /* valores por defecto del módulo */ });
    } catch (e) { /* */ }
    // puente de PRUEBAS headless (el CTRL vive en clausura)
    try { window.__PP_MAGIA = { ctrl: () => CTRL, cfg: LEVEL, level: () => CTRL && CTRL.level }; } catch (e) { /* */ }
  },

  start() { if (CTRL) CTRL.startChamp(); },
  leave() { if (CTRL) CTRL.leave(); },
  /** v2.66: borrado de registros del campeonato (Opciones → Reiniciar). */
  resetRecords() { if (CTRL) CTRL.resetRecords(); },
  update(dt) { if (CTRL) CTRL.update(dt); },
  /** v2.70 · DUELOS contra el mago: ganchos activos (antes el árbitro
   *  dormía todo el campeonato). */
  onPoint(it) { if (CTRL) CTRL.onPoint(it); },
  onMatchOver(w) { if (CTRL) CTRL.onMatchOver(w); },
  aiMul() {
    const g = GAME;
    if (!CTRL || !CTRL.active || !CTRL._rivalOn || !g ||
        g.rules.oppLabel !== 'wizard') return 1;
    return [1, 1.22, 1.5][CTRL.wizardLevel()] || 1;
  },
  /** GATILLO: salta el MONTAJE o dispara la pistola en JUEGO. */
  serveTrigger() { if (CTRL && CTRL.level) CTRL.level.trigger(); },
  reenter() { if (CTRL && CTRL.level && CTRL.level.active) CTRL.level.reenter(); },
  testStep(dt) { if (CTRL && CTRL.level) CTRL.level.step(dt); },
  testActive() { return !!(CTRL && CTRL.level && CTRL.level.active); },

  /* v2.96 · REJUGAR etapas superadas (mapa + gatillo, vía núcleo) */
  replayMap() { return CTRL ? CTRL.replayMap() : null; },
  replayHover(idx) { if (CTRL) CTRL.replayHover(idx); },
  replayLaunch(idx) { if (CTRL) CTRL.replayLaunch(idx); },
};
