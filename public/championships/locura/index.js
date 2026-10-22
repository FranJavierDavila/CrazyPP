/* =====================================================================
 *  EL CAMPEONATO DE LA LOCURA (rival: CLOWN) — MÓDULO DE CARPETA v2.74
 *  ---------------------------------------------------------------------
 *  v2.138 (módulo v20) · MAPA NUEVO DEL CLOWN — el dueño reenvía el
 *  Mapa.png del clown (1380×752, el MISMO lienzo), que en V2.137 llegó
 *  con el MISMO nombre que el del wizard y fue SOBRESCRITO (sólo
 *  sobrevivió el del wizard). Arte nuevo: GLOBOS numerados (1/3/5
 *  clowns · 2/4 arkanoid) colgando sobre MEDALLONES redondos de anillo
 *  dorado uniforme (ya no hay escudo final ni medallones ovales) →
 *  mapa.webp reemplazado (q92, 183 KB) y NODOS re-medidos con Hough +
 *  banda de COBERTURA ANGULAR dorada (fracción de ángulos dorados por
 *  radio — inmune al pelo naranja, los globos 3/5 y el camino, que
 *  engañaban al ajuste de círculo): centros 226,253 · 453,507 ·
 *  700,256 · 959,508 · 1208,322 y anillos r 114/119/109/121/107 con la
 *  MISMA regla calibrada del wizard (r = 120 × banda/107,5 — el anillo
 *  de progreso abraza el borde dorado). Las TAPAS «?» estrenan centro y
 *  escala PROPIOS por nodo (tx/ty/ts, backward-compat — el patrón
 *  MAGIA v28) para cubrir cada medallón ENTERO con margen de seguridad
 *  (ts 0,94/0,86/0,95/0,85): los globos numerados ASOMAN encima, como
 *  las estrellas del Oeste (indicador de etapa, no se tapan).
 *  v2.133 (módulo v19) · LA BOLA DOBLE (split) YA SE VE — el dueño en el
 *  casco: «el poder de Clown que saca dos bolas no funciona». Causa raíz
 *  reproducida headless: la MALLA del clon se creaba SÓLO dentro del primer
 *  build() del ARKANOID (la prueba de las etapas 2/4) y el split sólo está
 *  en la bolsa del Nv. 3 (etapa 5, DUELO JEFE). Llegando a la etapa 5 con
 *  sesión fresca (etapa guardada, recarga de página, salto de depuración o
 *  rejugada por el mapa) el arkanoid NUNCA se había construido → el clon
 *  corría físico INVISIBLE (la «malla perezosa» de v2.120 dependía de
 *  _makeCloneMesh, definido también sólo en build): el cartel prometía
 *  «¡la bola se divide en dos!» y la segunda bola JAMÁS aparecía — y la
 *  bola oficial se ponía blanca y jugaba rara (salvaciones que no se
 *  entienden sin ver el clon). FIX: (1) cloneMesh + _makeCloneMesh al
 *  CONSTRUCTOR (una sola vez por sesión, regla Quest: nada se crea por
 *  partida); (2) el split ya no se desperdicia en punto muerto: si el
 *  aviso termina sin rallye se RE-ARMA 1,2 s y entra en el PRÓXIMO rallye
 *  (antes nacía y updateSplit lo mataba en el primer frame: cartel sin
 *  efecto). Todo lo demás intacto.
 *  v2.127 (módulo v18) · BURLA sustituye a MAREO (petición del artista:
 *  «vamos a cambiar el superpoder del clown de mareo que no funciona»):
 *  RAYO DE LUZ ARCOÍRIS que impacta en puntos distintos de la mesa (pequeño
 *  destello arcoíris en cada impacto) y en el punto de impacto se PLANTA un
 *  CARTÓN VERTICAL de ~50 cm con el clown en actitud burlesca (arte nuevo
 *  burla1-4.png). El cartón dura 2 s y desaparece. Son BARRERAS: si la bola
 *  impacta, se FRENA (cae muerta en el sitio) y el cartón ESTALLA en
 *  partículas arcoíris. 1 de cada 5 cartones es el COMODÍN (burlacomodin.png,
 *  clown de espaldas): la bola SIGUE su curso normal pero se pone NEGRA y
 *  MÁS GRANDE — si la golpeas con la pala ESTALLA en cintas negras y es
 *  PUNTO GANADOR para el jugador. Icono del cartel: powerburla.png
 *  (medallón arcoíris con la cara burlesca; sustituye a powergiro.png).
 *  v2.126 (módulo v17) · LOS 2 PODERES NUEVOS, A PRUEBA DE TODO:
 *  (1) LANZAMIENTO GARANTIZADO — el efecto entra aunque el punto muera
 *      durante el aviso (antes cualquier estado ≠ rally se comía el poder
 *      en silencio y el dueño lo vivía como «no funciona»);
 *  (2) BOLSA ROTATORIA — todos los poderes salen antes de repetir (desde
 *      v2.127 la bolsa lleva BURLA en lugar de MAREO);
 *  (3) POP de globos más generoso (radio 0,155→0,185 m: la bola rápida
 *      tunelaba el margen y no reventaba ninguno).
 *  v2.120 (módulo v13) · AUDITORÍA + DOS SUPERPODERES NUEVOS DEL CLOWN:
 *  LLUVIA DE GLOBOS (6 globos de 3 tintas flotan sobre tu campo, revientan
 *  con la bola y renacen, 9 s) y MAREO TOTAL (el rig se tambalea 7 s con
 *  envolvente y restauración exacta) — bolsa del Clown = MÁXIMO 4 por
 *  nivel (Nv.1/2: confeti·bola loca·globos·mareo · Nv.3: bola loca·split·
 *  globos·mareo) y el cartel SUPER POWER!! enseña el ICONO (arte nueva).
 *  Auditoría: confettiBurst se apaga al acabar el poder, rayos láser
 *  purgados al salir, guard anti-NaN del viento, clon del split con malla
 *  perezosa. TODO lo demás queda intacto.
 *  v2.121 (módulo v14) · FIXES DE LOS 2 PODERES NUEVOS + MINIATURAS:
 *  · GLOBOS: la banda era z POSITIVA (+0,10..+1,15) = DETRÁS de la cabeza
 *    del jugador (la mesa está en z<0) → invisibles en el visor. Ahora
 *    flotan sobre TU CAMPO (z −1,50..+0,05, como el confeti) y renacen
 *    SOBRE la mesa (y 0,84), no atravesándola.
 *  · MAREO: ±6,3° a 0,5 Hz era imperceptible en la Quest → vaivén que SE
 *    NOTA: yaw ±9,7° a 0,62 Hz + roll ±4,3° a 0,41 Hz (solo rotación,
 *    confort VR intacto).
 *  · MINIATURAS para los clásicos: confeti·bola loca·split también lucen
 *    SU icono propio en el cartel (powerconfeti/powerbola/powersplit.png).
 *  v2.74 · LEY DEL ARTISTA («si algo funciona, permanece»):
 *   1. EL MAPA DE LA PARED VUELVE: entrar con la etapa en una PRUEBA
 *      (1 ARKANOID · 3 ARKANOID 2) saltaba directo a la prueba ANTES de
 *      encender el mapa y éste desaparecía de la pared en toda la sesión
 *      (duelos incluidos). Ahora startArcade/startArkanoid lo encienden
 *      SIEMPRE.
 *   2. PISTOLA REAL del artista en el ARKANOID 2: pistol.glb (assets/,
 *      el MISMO modelo que magia monta desde v2.61) sustituye a la
 *      pistola minúscula de respaldo del núcleo. Encaje idéntico a magia
 *      (cañón a -Z, ~32 cm, empuñadura en el origen) y el LÁSER sale de
 *      la BOCA DEL CAÑÓN (_gunMuzzle). Convertir azul→rojo: intacta.
 *   3. EL MENÚ CAMPEONATOS MUESTRA SÓLO CAMPEONATOS: retirados los
 *      accesos «PRUEBA: ARKANOID/ARKANOID 2» (el camino entra SOLO en
 *      las pruebas: etapa impar = prueba directa; victoria = prueba en
 *      cola). Banda sonora y récord se quedan (los pidió el artista).
 *
 *  Hasta v2.68 este campeonato vivía DENTRO de index.html (~3.650 líneas
 *  + 2,7 MB de arte en data-URLs). Desde v2.69 es una CARPETA
 *  AUTOCONTENIDA igual que magia: championships/locura/{index.js,
 *  manifest.json, assets/}. Desde v2.71 la configuración del artista vive
 *  en el bloque «cfg» del manifest.json (MISMA filosofía que el bloque
 *  «level» de magia — un solo fichero de ajustes por campeonato; el
 *  data.json de la v2.69 se retiró). El NÚCLEO no sabe nada de él:
 *  ChampLoader descubre la carpeta vía championships/championships.json
 *  (entrada "eager": se importa e inicializa al arranque, sin lanzar),
 *  y le entrega los MISMOS ganchos que a cualquier campeonato:
 *
 *    init/start/leave/resetRecords/update/onPoint/onMatchOver
 *    aiMul · serveTrigger/reenter/testActive/testStep (pruebas)
 *    gunArmed/fireGun (pistola) · _split/splitFilterEvents/updateSplit
 *    menuItems/menuAction (controles del menú) · hint/refresh
 *
 *  ARQUITECTURA DEL CAMPEONATO (5 etapas + trofeo — se respeta tal cual):
 *    etapa 1  LUCHA  · CLOWN Nv. 1        (partida a 11)
 *    etapa 2  PRUEBA · ARKANOID           (muro de ladrillos)
 *    etapa 3  LUCHA  · CLOWN Nv. 2        (×1,22 de dificultad)
 *    etapa 4  PRUEBA · ARKANOID 2         (rojos/azules + pistola)
 *    etapa 5  LUCHA  · CLOWN Nv. 3 (JEFE) (×1,5 + bola doble)
 *    al vencer: LOGRO = insignia «Campeonato de la Locura» en el ranking
 *    + copa permanente en la sala. Mapa de ruta en la pared izquierda
 *    que revela cada etapa superada.
 *
 *  El código de abajo es el MISMO que vivía en el núcleo (v2.34→v2.68)
 *  con tres ajustes mecánicos: (a) import de three + puente __PP_CORE,
 *  (b) los 7 arte data-URL pasan a archivos de assets/, (c) el guard de
 *  WORLDRANK usa la referencia del módulo. Nada de lógica cambia.
 *  ===================================================================== */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';   // v2.74: pistol.glb
// v3.6.2-SDK2 · FASE 4 de la modularización P0: kernel compartido de los 5
// campeonatos (championships/sdk/champ_sdk.js). La Locura es el ORIGEN del
// patrón de congelado (v2.40): ese patrón vive ahora en el SDK y el módulo
// lo usa de allí — una sola fuente para la familia. Sin SFX mp3 propios
// (los sonidos del rival van por el núcleo vía manifest "sounds").
import { createPowerSign, congela, getCore } from '../sdk/champ_sdk.js';

// Puente de SOLO LECTURA con el núcleo (window.__PP_CORE)
// v3.6.2-SDK2: el puente vive en el SDK (getCore) — una sola fuente.
const __CORE = getCore() || {};
const T = __CORE.T;
const DIMS = __CORE.DIMS;
const stepPhysics = __CORE.stepPhysics;
const ppPlayerName = __CORE.ppPlayerName;
const WORLDRANK = (typeof window !== 'undefined' && window.__PP_WORLD) || null;

/* v2.108 · MODO DEPURACIÓN («foro3d»): el núcleo publica window.__PP_DEBUG
 * cuando el nombre del jugador es foro3d. Con él, el mapa del camino
 * muestra las 5 ETAPAS y el gatillo salta a cualquiera SIN requisitos de
 * progreso (revisión directa del creador). El núcleo, además, no persiste
 * registros ni publica rankings ni telemetría de este jugador. */
function ppDbg() {
  try { return typeof window !== 'undefined' && !!window.__PP_DEBUG; } catch { return false; }
}

let GAME = null;   // PingPongGame (lo entrega ChampLoader en init)
let CTRL = null;   // ArcadeController — el MISMO controller de siempre

// v2.74 · PISTOLA REAL del artista (pistol.glb en assets/). Es el MISMO
// modelo que ya monta magia desde v2.61: nada de la pistola minúscula de
// respaldo del núcleo. init() fija la URL; ArcadeController la carga con
// pereza al armar la pistola en el ARKANOID 2 y la encara igual que magia
// (cañón a -Z, ~32 cm, empuñadura en el origen — el LÁSER sale del CAÑÓN).
let GUN_ART_URL = '';
// v2.74 · CONSTANTES DE MONTAJE (antes vivían SOLO en el núcleo y fireGun
// las heredó sin traerlas: el disparo LANZABA ReferenceError y el láser no
// salía NUNCA desde la migración a carpeta — por eso «no funcionaba como
// antes»). Valores EXACTOS de siempre en el núcleo (v2.45): pitch 0 y boca
// del cañón del modelo de respaldo a 18,8 cm del puño.
const GUN_MOUNT_PITCH = 0;
const GUN_MUZZLE = new THREE.Vector3(0.0003, 0.092, -0.163);

// Configuración POR DEFECTO del campeonato (el bloque «cfg» del manifest
// la funde encima: el artista ajusta sin tocar código, igual que el
// bloque «level» de magia). REGLA FIJA v2.71: en los duelos el rival se
// coloca ~0,50 m a la DERECHA del borde derecho de la mesa
// (giftBox.x = tableHalfWidth + 0,50 ≈ 1,26) y su regalo ~0,50 m por
// detrás del borde lejano (giftBox.z = -3,5). Nunca delante de la mesa.
const LOCURA_CFG = {
  id: 'clown',
  name: 'CLOWN',
  championship: 'Campeonato de la Locura',
  championship_en: 'Championship of Madness',
  version: 11,
  spriteWidth: 2.1,
  baseY: 0.52,
  z: -3.82,
  giftBox: { w: 2.1, h: 1.05, z: -3.5, x: 1.26 },
  rival: { followK: 0, followMax: 0 },
  powers: [
    { kind: 'confetti', duration: 8.0 },
    { kind: 'redball', duration: 8.0, scale: 2.0, speedMul: 0.62, gravityMul: 0.55 },
  ],
  powerTrigger: { chance: 0.32, cooldown: 13.0, minRallyHits: 1, warn: 2.0 },
  // v3.6.34: el PODER DE PALA es NORMATIVA del núcleo (MEGA PALA en
  // todos los campeonatos: rally de 11+ golpes la carga, gatillo la
  // suelta). Línea histórica — el módulo ya no implementa nada.
  playerPower: { kind: 'mega_pala', reachMul: 1.38, duration: 8.0, trigger: 'norma_rally11' },
  thresholds: { picandoRallyHits: 7, loosingDiff: 6, comboRally: 6, surprisedRally: 3 },
  powerBanner: 'superpoder.webp',
  music: 'bso.ogg',
  musicVolume: 0.18,
  champId: 'clown',
};

// v3.6.34 · la MEGA PALA vive en el NÚCLEO (MEGA PALA NORMATIVA): carga
// por rally de 11+ golpes, ICONO sobre el mango + jingle propio, gatillo
// voluntaria y conmutador «Pala Mejorada» en AJUSTES. Aquí ya no quedan
// constantes ni FX de pala (adiós núcleo dorado, halo, aro y chispas).

/* =====================================================================
 *  v2.41 · ARCADE — "CAMPEONATO DE LA LOCURA" (rival: CLOWN)
 *  ---------------------------------------------------------------------
 *  Capa de campeonato sobre el partido a 11: el rival es el CLOWN, un
 *  personaje con arte por ESTADOS (12 pinturas oficiales) y voz por
 *  estado (risa burlona, gruñido, sorpresa, risa loca, tristeza…).
 *
 *  Novedades v2.41:
 *   - REGALO 2D (regalo.png): fuera la caja 3D — un elemento GRÁFICO con
 *     alfa delante del Clown tapa su mitad inferior y devuelve fluidez
 *     (nada de geometría sólida). 100 % ESTÁTICO y con FIX de reaparición:
 *     al volver del ARKANOID (derrota) el regalo vuelve a verse.
 *   - ARKANOID REDISEÑADO (jugable):
 *     · El MURO se apoya SOBRE LA MESA, en el fondo del campo del rival
 *       (donde estaría su pala), con modelo cuidado (ladrillos biselados,
 *       peana, pilares y rieles ámbar).
 *     · El perímetro del CAMPO DEL RIVAL (de la red al fondo de la mesa)
 *       se cierra con 3 PAREDES que rebotan la bola de forma física: 2
 *       laterales de cristal + la pared del FONDO.
 *     · Detrás del muro, la imagen del SUPERPODER (superpoder_pistola.jpg)
 *       sobre la pared del fondo: se va desvelando a través de los huecos
 *       y ESA PARED también rebota la bola.
 *     · Cada impacto DESTRUYE el ladrillo (flash + escombros + sonido) y
 *       el rebote DEVUELVE la bola al jugador como lo haría la pala del
 *       rival (trayectoria con arco hacia su posición, llegada golpeable).
 *     · SIN RED: la mesa se juega sin red para esta variante.
 *     · SAQUE igual que en una partida normal: bola en la mano libre,
 *       gatillo para lanzarla (asistido) y golpeo con la pala; la mesa
 *       OTORGA una FUERZA MÍNIMA en cada bote: la bola nunca queda muerta.
 *     · 5 vidas contra el reloj (2:00, aviso <1 min, alarma ≤10 s); se
 *       pierde una vida SOLO si la bola cruzó la red y se pierde detrás.
 *
 *  Novedades v2.39:
 *   - FIX CRÍTICO · CONGELACIÓN AL GANAR: onMatchOver usaba la variable
 *     inexistente `g` («g.rules.stateTimer») y el ReferenceError mataba
 *     el bucle de render dentro del intent 'game-over': el juego quedaba
 *     bloqueado en la pantalla de fin de partida y nunca pasaba al
 *     ARKANOID. Corregido (this.game) y además TODOS los hooks del
 *     campeonato (onPoint/onMatchOver/update/arkanoid.step) quedan
 *     protegidos con try/catch: ninguna excepción futura puede volver a
 *     congelar la partida.
 *   - RIVAL ESTÁTICO: el Clown ya NO sigue tu raqueta — permanece SIEMPRE
 *     en la misma posición respecto a la mesa (donde estaba, pero 10 cm
 *     MÁS BAJO: baseY 0,62 -> 0,52; se le ve mejor saliendo de la caja).
 *   - CAJA DE REGALO 100 % ESTÁTICA: es decorado puro del campeonato,
 *     nunca se mueve (antes acompañaba la X del Clown).
 *
 *  Novedades v2.38:
 *   - CAJA DE REGALO PEQUEÑA y en el LADO DERECHO: el CLOWN SALE de la
 *     caja — su cuerpo se coloca justo encima de modo que parece emerger
 *     DETRÁS del regalo y se le ve BIEN completo.
 *   - MAPA DE RUTA como GRAN PÓSTER en la pared izquierda: panel con
 *     RESPALDO y marco propios, paralelo a la pared, separado 7 cm para
 *     que se vea COMPLETO y nunca "dentro" de la pared.
 *   - PRUEBA ARKANOID (2ª parada del camino): muro de ladrillos de UN
 *     color en lugar de la mesa; la bola rebota en las paredes perdiendo
 *     fuerza pero garantizando una ALTURA MÍNIMA de rebote; el rebote en
 *     un ladrillo es FÍSICO (reflexión especular) y solo se "falsea" su
 *     dirección para orientarla hacia el jugador cuando ya viene de
 *     vuelta. 2 minutos con contador descendente, aviso sonoro al bajar
 *     de 1 minuto y ALARMA en los últimos 10 s. 5 vidas (saques). Ganar
 *     = SUPERPODER PISTOLA (pistola.glb en la mano libre, dispara rayos);
 *     perder = vuelves al paso anterior (nueva partida CLOWN Nv. 1).
 *
 *  Novedades v2.36:
 *   - RIVAL UN POQUITO MÁS ALTO: misma posición (detrás de la mesa,
 *     z=-3,82) pero el borde inferior sube de 0,245 a 0,34 m (manifest
 *     "baseY") para que la cabeza no quede tan baja.
 *   - AVISO DE SUPERPODER CON 2 s DE MARGEN: el cartel "SUPER POWER!!"
 *     aparece ANTES (manifest "powerTrigger.warn", 2 s) y el poder NO se
 *     aplica hasta que el aviso termina — el jugador se entera y se
 *     prepara. Si el punto muere durante el aviso, el poder se guarda
 *     (cooldown corto) y volverá a intentarlo en el siguiente rallye.
 *   - RISA REAL: al ganar el Clown un punto se ríe con el archivo del
 *     campeonato (manifest "sounds": laugh/crazy -> risas.mp3).
 *   - BANDA SONORA DEL CAMPEONATO: "Four Funny Voices" suena BAJITA y en
 *     bucle SOLO mientras dura la partida (empieza al empezar, se detiene
 *     al acabar); volumen regulable y silenciable desde el menú CRAZY.
 *   - MAPA DE RUTA: panel con el camino del campeonato (inicio, pruebas
 *     de habilidad con la pala, rivales y trofeo) con el progreso.
 *
 *  Novedades v2.35:
 *   - RIVAL COMO ANTES: detrás de la mesa (z=-3,82) y pequeño (2,1 m),
 *     y AHORA con un movimiento LIGERO siguiendo tu raqueta: se desliza
 *     lateralmente un poco como si te siguiera con la mirada (factores
 *     "rival.followK" y "rival.followMax" del manifest).
 *   - SUPERPODERES EN PLENO JUEGO: el rival ya no lanza su poder cuando
 *     el punto está muerto: lo dispara mientras la bola está en juego y
 *     viene hacia ti, para ESTORBAR. Dos poderes (manifest "powers"):
 *       · CONFETI CAÓTICO — 8 s de lluvia densa sobre tu campo.
 *       · BOLA LOCA — bola ROJA, el DOBLE de tamaño, más ligera y
 *         lenta durante 8 s; al terminar todo vuelve a la normalidad.
 *   - CARTEL "SUPER POWER!!": al activarse CUALQUIER poder rival aparece
 *     un instante el arte oficial (manifest "powerBanner") en el centro
 *     de la vista, con destello y barrido de brillo, y se desvanece.
 *   - VOCES REALES POR ARCHIVO: el manifest "sounds" admite archivos de
 *     audio por tipo (laugh, crazy, angry, surprised, sad, panic, taunt,
 *     victory, present, powerup) que se embeben y suenan EN SU LUGAR;
 *     la síntesis procedural mejorada (vocales con formantes) queda de
 *     respaldo cuando no hay archivo.
 *
 *  v2.34:
 *   - RIVAL MÁS PEQUEÑO: ancho del plano configurable ("spriteWidth").
 *   - SFX DE PERSONALIDAD por cambio de estado (con throttle).
 *
 *  Estados del Clown (manifest "states"):
 *   present  presentación (inicio de ronda)        → fanfarria de circo
 *   idle     pausa entre puntos (arte en silencio)
 *   focused  rallye en curso (arte en silencio)
 *   surprised punto del jugador en rallye medio    → "¡Oh!"
 *   hungry   enfado por combo bueno del jugador    → gruñido (arte angry)
 *   panic    match-point en contra (arte; 1 aviso sonoro)
 *   laughing punto del Clown (burla)               → risa burlona
 *   crazy    2 puntos seguidos del Clown           → risa loca + CONFETI
 *   picando  rallye largo del jugador (7+ golpes)  → "ña ña ña"
 *   loosing  el Clown pierde por 6+ (arte en silencio)
 *   victory  gana el Clown la ronda                → fanfarria + estrellas
 *   defeated el Clown pierde la ronda              → trombón triste
 *
 *  Poderes:
 *   - CLOWN (v2.35, EN PLENO RALLYE): confeti caótico 8 s o BOLA LOCA
 *     (roja, 2x, ligera y lenta) 8 s — se lanzan con la bola viniendo
 *     hacia ti y avisan con el cartel "SUPER POWER!!".
 *   - JUGADOR (CRAZY COMBO): punto ganado con rallye de 6+ golpes ->
 *     MEGA PALA 8 s (radio de detección x1,38) si el poder "mega_pala"
 *     está desbloqueado (se gana al vencer al Clown; persistente).
 *
 *  Ranking lateral: panel 3D a la derecha de la mesa (solo en arcade)
 *  con las últimas rondas + rondas ganadas + racha (localStorage).
 *  Cartel "¡PARTIDA NUEVA!": banner 3D sobre la red al empezar cada
 *  ronda (VS CLOWN · Ronda N).
 *  ===================================================================== */

const ARCADE_DEFAULTS = {
  spriteWidth: 2.1,          // v2.34: antes 2,8 — el personaje distraía
  baseY: 0.245,              // respaldo; el manifest del clown usa 0,52 (v2.39)
  z: -3.82,                  // detrás de la mesa, centrado sobre la pala IA
  // v2.41: REGALO 2D (plano con alfa) — delante del Clown (z mayor) para
  // tapar su mitad inferior. ESTÁTICO. v2.71: x según la REGLA FIJA de
  // duelos (~0,50 m a la derecha del borde derecho de la mesa).
  giftBox: { w: 1.05, h: 0.525, z: -3.5, x: 1.26 },
  followK: 0.32,             // v2.35: seguimiento LIGERO de tu raqueta
  followMax: 0.5,            // v2.35: desplazamiento lateral máximo (m)
  powerChance: 0.32,         // v2.35: probabilidad por bola que viene hacia ti
  powerCooldown: 13,         // v2.35: segundos entre superpoderes
  powerWarn: 2.0,            // v2.36: cartel SUPER POWER!! 2 s ANTES del poder
  picandoRallyHits: 7,
  loosingDiff: 6,
  comboRally: 6,
  surprisedRally: 3,
};

// v2.41: arte embebido del REGALO 2D del campeonato y del PÓSTER del
// superpoder que se esconde tras el muro ARKANOID (build_html los inyecta)
// v2.45: __PP_WIND_URL = imagen del VIENTO tras el muro del ARKANOID 2
// v2.46: reloj.png (superpuesto al ladrillo negro del TIEMPO EXTRA) y
// extra.png ("+1 MIN" que flota al destruirlo)
// v2.47: mapa OFICIAL del campeonato (mapa.png del artista) y la TAPA de las
// etapas aún no alcanzadas (tapa.png con alfa — se oculta al llegar a la etapa)
// v2.138: mapa.webp = arte NUEVO del clown (globos numerados) y las tapas
// con centro/escala PROPIOS por nodo (tx/ty/ts — cubren el medallón entero)

// v2.35: respaldo del poder BOLA LOCA si el manifest no lo declara
const REDBALL_DEFAULTS = { scale: 2.0, speedMul: 0.62, gravityMul: 0.55 };

const RIVAL_SFX = {
  present: 'present',
  laughing: 'laugh',
  crazy: 'crazy',
  hungry: 'angry',
  surprised: 'surprised',
  defeated: 'sad',
  loosing: 'sad',
  picando: 'taunt',
  victory: 'victory',
  panic: 'panic',
};

/* ---------- utilidades de canvas para los paneles del arcade ---------- */
function arcadeCanvas(w, h) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  return cv;
}

function arcadeStarTexture() {
  const cv = arcadeCanvas(64, 64);
  const g = cv.getContext('2d');
  g.translate(32, 32);
  g.beginPath();
  for (let i = 0; i < 10; i++) {
    const r = i % 2 === 0 ? 28 : 12;
    const a = (Math.PI / 5) * i - Math.PI / 2;
    const x = Math.cos(a) * r;
    const y = Math.sin(a) * r;
    if (i === 0) g.moveTo(x, y); else g.lineTo(x, y);
  }
  g.closePath();
  g.fillStyle = '#ffd257';
  g.shadowColor = '#ffb347';
  g.shadowBlur = 8;
  g.fill();
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/* =====================================================================
 *  ArcadeRival — el CLOWN: plano del sprite + anillo de estrellas
 *  ===================================================================== */
class ArcadeRival {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.data = ctrl.data;
    this.inited = false;
    this._aspectHooked = false;
    this.state = '';
    this.applied = false;
    this.texs = {};
    this.spriteBaseY = (this.data.spriteBaseY0 || ARCADE_DEFAULTS.baseY) + 0.573;
  }

  build() {
    if (this.inited) return;
    this.inited = true;
    const mat = new THREE.MeshBasicMaterial({
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
    });
    // plano provisional (el aspecto real llega al decodificar la 1ª textura)
    this.sprite = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.75), mat);
    this.sprite.position.set(0, this.spriteBaseY, ARCADE_DEFAULTS.z);
    this.sprite.renderOrder = 6;
    this.sprite.visible = false;
    // v2.44: ANCLAJE AL RIG (espacio de la mesa) — el recentrado gira el rig;
    // todo lo del campeonato vive en el MISMO espacio que la mesa y la sala,
    // así se ven SIEMPRE en el mismo sitio relativo (nunca dentro de la pared).
    this.game.rig.add(this.sprite);

    // anillo de estrellas (victoria del Clown): 6 estrellas orbitando
    this.stars = new THREE.Group();
    const starTex = arcadeStarTexture();
    const starGeo = new THREE.PlaneGeometry(0.1, 0.1);
    this._starMats = [];
    for (let i = 0; i < 6; i++) {
      const sm = new THREE.MeshBasicMaterial({
        map: starTex, transparent: true, depthWrite: false,
      });
      this._starMats.push(sm);
      const st = new THREE.Mesh(starGeo, sm);
      const a = (Math.PI * 2 / 6) * i;
      st.position.set(Math.cos(a) * 0.26, Math.sin(a) * 0.12, 0.02);
      st.userData.phase = i;
      this.stars.add(st);
    }
    this.stars.position.set(0, this.spriteBaseY + 0.6, ARCADE_DEFAULTS.z);
    this.stars.visible = false;
    this.game.rig.add(this.stars);   // v2.44: anclado al rig (junto a la mesa)

    // v2.41: REGALO 2D (regalo.webp) — sustituye a la CAJA 3D: un elemento
    // GRÁFICO (plano con alfa) delante del Clown que tapa su mitad inferior
    // y añade FLUIDEZ (nada de geometría sólida en escena). Es decorado
    // PURO: se construye una vez, en posición fija, y NUNCA se mueve.
    // v2.71 · REGLA FIJA: el eje x del regalo MANDA también la x del
    // Clown (separación ~50 cm a la derecha del borde derecho de la mesa).
    const GB = (this.data && this.data.giftBox) || ARCADE_DEFAULTS.giftBox;
    this.giftBox = GB;
    this.giftX = GB.x || 0;
    // posición inicial YA alineada con el regalo (derecha)
    this.sprite.position.x = this.giftX;
    this.stars.position.x = this.giftX;
    this.gift = new THREE.Group();
    const GW = GB.w || 1.05, GH = GB.h || GW / 2;
    this.giftMat = new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
    });
    this.giftPlane = new THREE.Mesh(new THREE.PlaneGeometry(GW, GH), this.giftMat);
    this.giftPlane.renderOrder = 7;   // SIEMPRE por encima del sprite del Clown
    this.gift.add(this.giftPlane);
    // base apoyada en el suelo, delante del Clown (z mayor)
    this.gift.position.set(this.giftX, GH / 2 + 0.004, GB.z || -3.5);
    this.gift.visible = false;
    this.game.rig.add(this.gift);   // v2.44: anclado al rig (junto a la mesa)
    // arte embebido (data URL) — asíncrono como las pinturas del Clown
    if (typeof window !== 'undefined' && window.__PP_GIFT_URL) {
      const gimg = new Image();
      gimg.onload = () => {
        const gtex = new THREE.Texture();
        gtex.colorSpace = THREE.SRGBColorSpace;
        gtex.image = gimg;
        gtex.needsUpdate = true;
        this.giftMat.map = gtex;
        this.giftMat.needsUpdate = true;
      };
      gimg.src = window.__PP_GIFT_URL;
    }

    this.loadTextures();
  }

  loadTextures() {
    const urls = (this.data && this.data.urls) || {};
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
        // si ya estábamos mostrando este estado, aplícalo al llegar
        if (this.state === st && !this.applied) this.applyStateTexture();
      };
      img.onerror = () => { /* sin arte para ese estado: sigue el anterior */ };
      img.src = urls[st];
    }
  }

  /** Plano ADAPTATIVO: arte horizontal (ar > 1,2) -> ancho del campeonato
   *  (v2.34: 2,1 m); arte vertical -> clásico 1,4 x 1,75. El borde inferior
   *  queda SIEMPRE fijo en baseY (0,245 m) y las estrellas sobre la cabeza. */
  applySpriteAspect(ar) {
    if (!this.inited || !ar || !isFinite(ar)) return;
    let w = 1.4, h = 1.75;
    if (ar > 1.2) {
      w = (this.data && this.data.spriteWidth) || ARCADE_DEFAULTS.spriteWidth;
      h = w / ar;
    }
    const base = (this.data && this.data.baseY) || ARCADE_DEFAULTS.baseY;
    this.sprite.geometry.dispose();
    this.sprite.geometry = new THREE.PlaneGeometry(w, h);
    this.spriteBaseY = base + h / 2;
    this.sprite.position.y = this.spriteBaseY;
    this.stars.position.y = base + h + 0.055;
  }

  applyStateTexture() {
    const tex = this.texs[this.state];
    if (tex) {
      this.sprite.material.map = tex;
      this.sprite.material.needsUpdate = true;
      this.applied = true;
    }
  }

  /** Cambia el arte (SIN sonido: el sonido lo decide el controlador). */
  setState(name) {
    if (this.state === name) return;
    this.state = name;
    this.applied = false;
    this.applyStateTexture();
  }

  update(dt, t) {
    if (!this.inited || !this.sprite.visible) return;
    // v2.39: el Clown ya NO sigue tu raqueta — permanece SIEMPRE en la
    // misma posición respecto a la mesa (x fija del manifest, la de la
    // caja de regalo, lado derecho). Solo flota suavemente sobre esa base.
    const cx = this.giftX || 0;
    this.sprite.position.x = cx;
    this.stars.position.x = cx;
    // v2.39: la CAJA DE REGALO es DECORADO PURO — nunca se mueve (su
    // posición es la fija de la construcción; aquí ya no se toca).
    // flotación suave sobre la base fija
    this.sprite.position.y = this.spriteBaseY + Math.sin(t * 2.1) * 0.015;
    // estrellas: giro orbital + vaivén individual
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
    if (this.gift) this.gift.visible = false;   // v2.37
  }
}

/* =====================================================================
 *  ArcadeCartel — "¡PARTIDA NUEVA! · VS CLOWN · Ronda N" sobre la red
 *  ===================================================================== */
class ArcadeCartel {
  constructor(ctrl) {
    this.game = ctrl.game;
    this.t = -1;   // -1 = oculto
  }

  build() {
    this.cv = arcadeCanvas(1024, 280);
    this.tex = new THREE.CanvasTexture(this.cv);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.MeshBasicMaterial({
      map: this.tex, transparent: true, depthWrite: false,
    });
    this.group = new THREE.Group();
    this.plane = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 1.7 * 280 / 1024), mat);
    this.group.add(this.plane);
    // v2.70: cartel MUY POR ENCIMA del Clown (su cabeza llega a ~1,67 m) y
    // del marcador del núcleo (borde superior 2,375 m) — nunca en la línea
    // de visión del personaje (petición del artista: el cartel tapaba al
    // CLOWN en la zona de intersección).
    // v2.130 · FIX: a 2,62 su borde superior (2,85) rozaba el techo de la
    // sala (2,85 m) — baja a 2,58 para dejar 3 cm de aire.
    this.group.position.set(0, 2.58, -2.05);
    this.group.visible = false;
    this.game.rig.add(this.group);   // v2.44: anclado al rig (junto a la mesa/red)
  }

  show(round) {
    const g = this.cv.getContext('2d');
    g.clearRect(0, 0, 1024, 280);
    // tarjeta
    g.fillStyle = 'rgba(8,14,30,0.92)';
    g.strokeStyle = '#e8b45a';
    g.lineWidth = 10;
    const r = 40;
    g.beginPath();
    g.moveTo(r, 10); g.arcTo(1014, 10, 1014, 270, r); g.arcTo(1014, 270, 10, 270, r);
    g.arcTo(10, 270, 10, 10, r); g.arcTo(10, 10, 1014, 10, r);
    g.closePath(); g.fill(); g.stroke();
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    g.fillStyle = '#ffd257';
    g.font = '800 92px system-ui, sans-serif';
    g.fillText(T('cartel_new'), 512, 105);
    g.fillStyle = '#eef2f6';
    g.font = '700 64px system-ui, sans-serif';
    g.fillText(T('cartel_vs', { n: round }), 512, 205);
    this.tex.needsUpdate = true;
    this.t = 0;
    this.group.visible = true;
  }

  update(dt) {
    if (this.t < 0 || !this.group.visible) return;
    this.t += dt;
    // entra con rebote, aguanta y se apaga
    const sIn = Math.min(1, this.t / 0.45);
    const ease = 1 - Math.pow(1 - sIn, 3);
    const pulse = 1 + Math.sin(Math.max(0, this.t) * 6) * 0.05 * Math.max(0, 1 - this.t / 2.5);
    this.group.scale.setScalar(0.25 + 0.75 * ease * pulse);
    this.plane.material.opacity = this.t > 2.6 ? Math.max(0, 1 - (this.t - 2.6) / 0.5) : 1;
    if (this.t > 3.1) {
      this.group.visible = false;
      this.t = -1;
    }
  }

  hide() { if (this.group) { this.group.visible = false; this.t = -1; } }
}

/* =====================================================================
 *  ArcadeRanking — panel lateral con las últimas rondas del campeonato
 *  ===================================================================== */
class ArcadeRanking {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
  }

  build() {
    this.cv = arcadeCanvas(512, 720);
    this.tex = new THREE.CanvasTexture(this.cv);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.MeshBasicMaterial({
      map: this.tex, transparent: true, depthWrite: false,
    });
    this.group = new THREE.Group();
    this.plane = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.62 * 720 / 512), mat);
    this.group.add(this.plane);
    this.group.position.set(1.46, 1.12, -1.7);
    this.group.rotation.y = -0.42;
    this.group.visible = false;
    this.game.rig.add(this.group);   // v2.44: anclado al rig (junto a la mesa)
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
    // tarjeta
    g.fillStyle = 'rgba(8,14,30,0.9)';
    g.strokeStyle = 'rgba(232,180,90,0.85)';
    g.lineWidth = 8;
    g.beginPath();
    const r = 30;
    g.moveTo(r, 6); g.arcTo(506, 6, 506, 714, r); g.arcTo(506, 714, 6, 714, r);
    g.arcTo(6, 714, 6, 6, r); g.arcTo(6, 6, 506, 6, r);
    g.closePath(); g.fill(); g.stroke();
    g.textAlign = 'center';
    g.fillStyle = '#ffd257';
    g.font = '800 46px system-ui, sans-serif';
    g.fillText('RANKING', 256, 66);
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
    const _pnCard = ppPlayerName();
    g.fillText(_pnCard ? '★ ' + _pnCard + ' ★' : T('arc_title'), 256, 110);
    // separador
    g.strokeStyle = 'rgba(255,255,255,0.18)';
    g.lineWidth = 3;
    g.beginPath(); g.moveTo(40, 136); g.lineTo(472, 136); g.stroke();
    // filas: últimas 4 rondas (la más reciente arriba) — v2.48: 4 en vez
    // de 6 para dejar sitio al bloque de RÉCORDS del palmarés
    const rank = c.rank || [];
    const rows = rank.slice(-4).reverse();
    g.textBaseline = 'middle';
    if (c.trophy) {
      // v2.44: TROFEO del Campeonato registrado en el palmarés
      g.fillStyle = '#ffd257';
      g.font = '800 30px system-ui, sans-serif';
      g.fillText('★ ' + T('trophy_rank') + ' ★', 256, 168);
    }
    if (!rows.length) {
      // dos líneas para que el aviso quepa en la tarjeta
      g.fillStyle = '#75828f';
      g.font = '500 28px system-ui, sans-serif';
      g.fillText(T('arc_rank_empty1'), 256, c.trophy ? 250 : 236);
      g.fillText(T('arc_rank_empty2'), 256, c.trophy ? 290 : 276);
    }
    rows.forEach((row, i) => {
      const y = (c.trophy ? 222 : 186) + i * 64;
      g.textAlign = 'left';
      g.fillStyle = '#8b949c';
      g.font = '700 30px system-ui, sans-serif';
      g.fillText(`R${rank.length - i}`, 44, y);
      g.textAlign = 'center';
      g.fillStyle = row.w ? '#7fb069' : '#e06c5a';
      g.font = '800 34px system-ui, sans-serif';
      g.fillText(row.w ? T('arc_rank_win') : T('arc_rank_lose'), 256, y);
      g.textAlign = 'right';
      g.fillStyle = '#c8ced4';
      g.font = '700 30px system-ui, sans-serif';
      g.fillText(`${row.p}-${row.a}`, 468, y);
    });
    // v2.48 · bloque de RÉCORDS del palmarés (datos reales persistidos)
    g.strokeStyle = 'rgba(255,255,255,0.18)';
    g.beginPath(); g.moveTo(40, 446); g.lineTo(472, 446); g.stroke();
    {
      const st = (this.game.stats && this.game.stats.data) || null;
      const surv = this.game.survivalBest || 0;
      const achN = st && st.ach ? Object.keys(st.ach).length : 0;
      const achM = (typeof ACHIEVEMENTS !== 'undefined' && ACHIEVEMENTS.length) || 0;
      const recs = [
        st && st.bestRally > 0 ? T('arc_rec_rally', { n: st.bestRally }) : '',
        st && st.bestStreak > 0 ? T('arc_rec_streak', { n: st.bestStreak }) : '',
        surv > 0 ? T('arc_rec_surv', { n: surv }) : '',
        st && achM > 0 ? T('arc_rec_ach', { n: achN, m: achM }) : '',
      ].filter(Boolean);
      g.textAlign = 'left';
      g.font = '600 27px system-ui, sans-serif';
      recs.forEach((txt, i) => {
        const y = 484 + i * 44;
        g.fillStyle = i === 0 ? '#f6b73c' : '#c8ced4';
        g.fillText(txt, 48, y);
      });
    }
    // pie: totales
    g.strokeStyle = 'rgba(255,255,255,0.18)';
    g.beginPath(); g.moveTo(40, 648); g.lineTo(472, 648); g.stroke();
    g.textAlign = 'center';
    g.fillStyle = '#ffd257';
    g.font = '700 30px system-ui, sans-serif';
    g.fillText(T('arc_rank_tot', { n: c.wins || 0, s: c.streak || 0 }), 256, 688);
    this.tex.needsUpdate = true;
  }

  hide() { if (this.group) this.group.visible = false; }
}

/* =====================================================================
 *  ArcadePowerSign (v2.35 → v2.40) — ANUNCIO ÉPICO de «SUPER POWER!!»
 *  v2.40: al anunciar el rival su superpoder, la PARTIDA SE CONGELA
 *  (game_part3 la gatea con freezeT) y el arte oficial hace su número:
 *    · ENTRADA rápida desde el lado IZQUIERDO de la vista (0 → 0,40 s)
 *    · PARADA en el centro con leve movimiento oscilatorio y un HALO DE
 *      CONTORNO dorado que respira (silueta real del arte, sin bolas de
 *      luz) hasta 1,45 s
 *    · SALIDA rápida por el lado DERECHO, el contrario (1,45 → 1,90 s)
 *  Total ≈ 2 s. Fuera el antiguo destello radial y el barrido de luz que
 *  no se entendían. Sigue anclado a la CABEZA para que siempre esté «en
 *  la pantalla»; al reanudarse la partida el poder entra en juego.
 *  ===================================================================== */
class ArcadePowerSign {
  constructor(ctrl) {
    this.game = ctrl.game;
    this.ctrl = ctrl;
    // v3.6.4-SDK4 · FASE 6: la fábrica del SDK (createPowerSign) sustituye
    // la copia — UNA sola fuente para el tablón de superpoder (ArcadePowerSign).
    this._impl = createPowerSign(THREE, () => this.game, {
      coreo: 'v240',
      halo: true,
      arte: 'fit1833',
      url: () => (ctrl.data && ctrl.data.powerBannerUrl) || '',
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
const ppSignPos = new THREE.Vector3();
const ppSignQuat = new THREE.Quaternion();
const ppSignDir = new THREE.Vector3();

/* =====================================================================
 *  ArcadeMap (v2.36 → v2.44) — MAPA DE RUTA DEL CAMPEONATO
 *  v2.44: la ruta COMPLETA de 6 paradas — CLOWN Nv.1 → ARKANOID →
 *  CLOWN Nv.2 → ARKANOID 2 → CLOWN Nv.3 → TROFEO. El progreso (anillo
 *  dorado) sale DIRECTO de la etapa del camino (0..5).
 *  ===================================================================== */
/* =====================================================================
 *  ArcadeMap (v2.36 → v2.138) — MAPA OFICIAL DEL CAMPEONATO (mapa.webp)
 *
 *  v2.138 · ARTE NUEVO del dueño (el Mapa.png del clown, reenviado tras
 *  pisarse con el del wizard en V2.137): globos NUMERADOS (1/3/5 clowns,
 *  2/4 arkanoid) sobre medallones redondos. Nodos RE-MEDIDOS con Hough
 *  + banda de cobertura angular dorada; anillo con la regla del wizard
 *  (r = 120×banda/107,5) y TAPAS con centro/escala propios (tx/ty/ts).
 *  Los globos numerados asoman sobre las tapas (decoración indicadora
 *  de etapa, como las estrellas del Oeste).
 *
 *  v2.47 · El mapa procedural (canvas) se SUSTITUYE por el arte oficial
 *  del artista embebido como __PP_MAPA_URL y las etapas NO alcanzadas
 *  nacen CUBIERTAS con la tapa oficial (__PP_TAPA_URL). Al ALCANZAR una
 *  etapa (pp_arcade_stage >= N) su tapa se oculta.
 *
 *  Nodos (px sobre 1380x752 — medidos sobre el arte V2.138):
 *    0 CLOWN Nv.1 (226,253) — SIEMPRE visible (nunca se tapa)
 *    1 ARKANOID   (453,507) — tapa hasta stage >= 1
 *    2 CLOWN Nv.2 (700,256) — tapa hasta stage >= 2
 *    3 ARKANOID 2 (959,508) — tapa hasta stage >= 3
 *    4 CLOWN Nv.3 (1208,322) — tapa hasta stage >= 4
 *  Etapa 5 = CAMPEÓN: ruta completa (sin tapas y sin anillo).
 *  ===================================================================== */
class ArcadeMap {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.t = 0;
    // nodos del camino EN PÍXELES DEL ARTE oficial (el orden ES la ruta);
    // tapa: nace cubierto con tapa.png hasta que se alcanza su etapa
    // v2.138: nodos RE-MEDIDOS sobre el arte nuevo (Hough + cobertura
    // angular; r = 120×banda/107,5) y tapas con centro/escala PROPIOS
    // (tx/ty/ts): cubren el medallón ENTERO con margen — el globo numerado
    // asoma encima, como las estrellas del Oeste.
    this.nodesPx = [
      { x: 226, y: 253, r: 114, kind: 'clown', lvl: 1, tapa: false },   // CLOWN Nv. 1
      { x: 453, y: 507, r: 119, kind: 'arkanoid', lvl: 1, tapa: true,   // PRUEBA: ARKANOID
        tx: 453, ty: 507, ts: 0.94 },
      { x: 700, y: 256, r: 109, kind: 'clown', lvl: 2, tapa: true,      // CLOWN Nv. 2
        tx: 700, ty: 256, ts: 0.86 },
      { x: 959, y: 508, r: 121, kind: 'arkanoid', lvl: 2, tapa: true,   // PRUEBA: ARKANOID 2
        tx: 959, ty: 508, ts: 0.95 },
      { x: 1208, y: 322, r: 107, kind: 'clown', lvl: 3, tapa: true,     // CLOWN Nv. 3 (final)
        tx: 1208, ty: 322, ts: 0.85 },
    ];
    this.currentIdx = 0;   // por defecto: el Clown Nv. 1 es el reto actual
    // dimensiones del arte y del plano (misma proporción 1380:752)
    this.IMG_W = 1380;
    this.IMG_H = 752;
    this.PW = 1.68;                       // ancho físico del póster (m)
    this.PH = 1.68 * 752 / 1380;          // 0,9157 m — respeta el aspecto
    // tamaño de cada tapa en metros (290x300 px del diff del artista)
    this.TAPA_W = 290 / 1380 * this.PW;   // 0,3530 m
    this.TAPA_H = 300 / 752 * this.PH;    // 0,3652 m
  }

  build() {
    if (this.inited) return;
    this.inited = true;
    this.group = new THREE.Group();
    // RESPALDO del póster — caja fina oscura que garantiza profundidad
    // propia: el mapa queda FISICAMENTE delante de la pared (v2.38)
    const back = new THREE.Mesh(
      new THREE.BoxGeometry(this.PW + 0.06, this.PH + 0.06, 0.022),
      new THREE.MeshStandardMaterial({ color: 0x131820, roughness: 0.85, metalness: 0.1 }),
    );
    back.position.z = -0.013;
    this.group.add(back);
    // v2.47 · ARTE OFICIAL: plano con mapa.png (textura asíncrona; mientras
    // carga, opacity 0 — NUNCA un quad blanco)
    this.plane = new THREE.Mesh(
      new THREE.PlaneGeometry(this.PW, this.PH),
      new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, opacity: 0 }),
    );
    this.group.add(this.plane);
    const murl = (typeof window !== 'undefined' && window.__PP_MAPA_URL) || '';
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
    // v2.47 · TAPAS de las etapas no alcanzadas (tapa.png con alfa); la
    // textura es COMÚN y cada tapa es un plano sobre su medallón
    this.tapas = [];
    this.tapasReady = false;
    const turl = (typeof window !== 'undefined' && window.__PP_TAPA_URL) || '';
    if (turl) {
      new THREE.TextureLoader().load(turl, (tex) => {
        tex.colorSpace = THREE.SRGBColorSpace;
        this.nodesPx.forEach((n, i) => {
          if (!n.tapa) return;
          // v2.138: la tapa puede llevar CENTRO y ESCALA propios (tx/ty/ts,
          // patrón MAGIA v28) — en el arte nuevo cada medallón mide lo suyo.
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
    // anillo del PROGRESO sobre el medallón ACTUAL — ESTÁTICO (v2.37);
    // v2.47: tamaño base al radio del Clown (120 px) y escala por nodo
    this.marker = new THREE.Mesh(
      new THREE.RingGeometry(0.118, 0.144, 48),
      new THREE.MeshBasicMaterial({
        color: 0xffd257, transparent: true, depthWrite: false,
        side: THREE.DoubleSide,
      }),
    );
    this.marker.material.opacity = 0.9;
    this.marker.position.z = 0.006;
    this.marker.renderOrder = 3;
    this.group.add(this.marker);
    // PARED IZQUIERDA (x=-3,05): póster separado 7 cm del muro, paralelo a
    // él (rotación +90°) y mirando al interior — dentro del RIG (v2.44)
    this.group.position.set(-2.98, 1.5, -0.9);
    this.group.rotation.y = Math.PI / 2;
    this.group.visible = false;
    this.game.rig.add(this.group);
    this.refresh();
  }

  /** Píxeles del arte -> coordenadas locales del plano. */
  _pxToLocal(px, py) {
    return [(px / this.IMG_W - 0.5) * this.PW, (0.5 - py / this.IMG_H) * this.PH];
  }

  /** Nodo actual según la ETAPA persistente del campeonato (v2.44):
   *  0 CLOWN Nv.1 · 1 ARKANOID · 2 CLOWN Nv.2 · 3 ARKANOID 2 ·
   *  4 CLOWN Nv.3 · 5 TROFEO (campeón: ruta completa, sin anillo). */
  _computeCurrent() {
    const st = this.ctrl ? this.ctrl.stage : 0;
    return Math.max(0, Math.min(this.nodesPx.length - 1, st | 0));
  }

  refresh() {
    // v2.47 · SIN CANVAS: el arte ES la textura; aquí sólo se ajustan las
    // tapas (visibles mientras la etapa NO se alcanzó) y el anillo actual.
    if (!this.group) return;
    this.currentIdx = this._computeCurrent();
    const st = this.ctrl ? (this.ctrl.stage | 0) : 0;
    const champion = st >= 5;             // etapa TROFEO: todo descubierto
    if (this.tapas && this.tapas.length) {
      for (const t of this.tapas) {
        // v2.108: en MODO DEPURACIÓN todas las tapas levantadas — las 5
        // etapas son visibles y apuntables con la pala desde el principio.
        t.mesh.visible = !champion && !ppDbg() && this.currentIdx < t.idx;
      }
    }
    if (this.marker) {
      this.marker.material.color.setHex(0xffd257);   // v2.96: dorado de nuevo
      this.marker.visible = !champion;
      const n = this.nodesPx[this.currentIdx];
      const p = this._pxToLocal(n.x, n.y);
      this.marker.position.x = p[0];
      this.marker.position.y = p[1];
      this.marker.scale.setScalar(n.r / 120);   // radio del medallón actual
      this._markerBase = { x: p[0], y: p[1] };
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

  /** v2.37: el mapa es PERFECTAMENTE ESTÁTICO — nada late, nada se mueve.
   *  El método se conserva por compatibilidad con el bucle del arcade. */
  update() {
    /* estático a propósito (v2.37) */
  }

  hide() { if (this.group) this.group.visible = false; }
}

/* =====================================================================
 *  ArcadeArkanoid (v2.41) — PRUEBA ARKANOID DEL CAMPEONATO
 *  2ª parada del camino: un MURO de ladrillos de UN color APOYADO SOBRE
 *  LA MESA, en el fondo del campo del rival (donde estaría su pala).
 *  La pala dirige la bola; cada impacto rompe un ladrillo y el muro
 *  DEVUELVE la bola al jugador como lo haría la pala del rival.
 *
 *  Escenario (v2.41):
 *   · La MESA permanece en escena (el muro se apoya en su superficie) y
 *     SIN RED: esta variante se juega sin red.
 *   · El CAMPO DEL RIVAL (de la red al fondo de la mesa) queda perimetra-
 *     do por 3 PAREDES que rebotan la bola de forma física y real: 2
 *     laterales de cristal + la pared del FONDO.
 *   · Detrás del muro, sobre la pared del fondo, la imagen del SUPERPODER
 *     (superpoder_pistola.jpg): oculta por los ladrillos, se va viendo a
 *     través de los huecos; ESA PARED también rebota la bola.
 *
 *  Física:
 *   · La bola rebota en paredes/suelo/techo perdiendo un poco de fuerza,
 *     pero SIEMPRE se garantiza una ALTURA MÍNIMA de rebote (ápice >=
 *     ~0,95 m) para que sea posible volver a golpearla.
 *   · LA MESA OTORGA UNA FUERZA MÍNIMA en cada bote: la bola nunca queda
 *     muerta sobre la superficie.
 *   · El impacto en un ladrillo es REAL (reflexión especular) y después
 *     el muro DEVUELVE la bola: trayectoria con arco hacia la posición
 *     del jugador (llegada golpeable), igual que una devolución rival.
 *   · SAQUE igual que en una partida normal: bola en la mano libre,
 *     GATILLO para lanzarla (asistido) y golpeo con la pala.
 *   · Bola perdida por detrás del jugador (solo si cruzó la red) = saque
 *     nuevo (5 vidas).
 *
 *  Regla: 2 minutos con contador descendente. Aviso sonoro al bajar de
 *  1 minuto y ALARMA en los últimos 10 s. Ganar = SUPERPODER PISTOLA
 *  (pistola.glb en la mano libre). Perder (tiempo o vidas) = vuelves al
 *  paso anterior: nueva partida contra el CLOWN Nv. 1.
 *  ===================================================================== */
const ARK_CFG = {
  // v2.42 · TODO ALINEADO CON LA MESA (DIMS): el muro ocupa el ancho EXACTO
  // de la mesa y está ENRASADO con su borde de fondo; las 3 paredes del
  // perímetro nacen EN LOS BORDES de la mesa (laterales ±tableHalfWidth,
  // fondo en el borde lejano) y la red se retira (también sus físicas).
  // v2.44 · PAREDES LATERALES +30 cm HACIA EL JUGADOR (sideZ0 = red + 0,30):
  // los cristales llegan MÁS CERCA del jugador y la bola ya no se cuela por
  // los laterales de su campo.
  cols: 6, rows: 5, gap: 0.014, depth: 0.12,
  bw: (DIMS.tableHalfWidth * 2 - 5 * 0.014) / 6,   // 0,2425 m: muro = ancho de mesa
  bh: 0.165,
  baseY: DIMS.tableTopY + 0.005,     // APOYADO en la superficie de la mesa
  sideX: DIMS.tableHalfWidth,        // 0,7625 — cristales EN el borde de la mesa
  // v2.47 · MISMAS DIMENSIONES DE MUROS QUE EL ARKANOID 2 (petición expresa):
  // los cristales del ARKANOID 1 llegan también a red + 80 cm, así ambos
  // niveles comparten el recinto EXACTO (visual y colisión con this.C).
  sideZ0: DIMS.tableCenterZ + 0.80,  // v2.47: red + 80 cm — IGUAL que ARK2
  sideZ1: DIMS.tableCenterZ - DIMS.tableHalfLength,  // -2,97 — borde de FONDO
  backY: 1.5,        // pared del fondo: 1,5 m SOBRE la mesa (sostiene el póster)
  glassY: 1.05,      // cristales laterales: 1,05 m SOBRE la mesa
  // FÍSICA = la de una PARTIDA NORMAL (DIMS.gravity + aerodinámica + Magnus
  // + MISMO golpeo de pala). La mesa otorga FUERZA MÍNIMA de bote (la bola
  // nunca queda muerta) y el recinto pierde energía de forma realista.
  apexMin: 0.38,     // bote mínimo que la mesa OTORGA (sobre la superficie)
  brickRest: 0.86,   // pérdida de la componente normal en el ladrillo
  wallRest: 0.82,    // pérdida en las paredes perimetrales
  time: 120,         // 2 minutos
  lives: 5,          // 5 saques
  serveAutoT: 12,    // saque automático si no actúas (bola nunca atascada)
  variant: 1,        // v2.44: ARKANOID clásico (30 ladrillos rojos + póster)
};

/* ---------- v2.44 · ARKANOID 2 (variante 2 del camino) -----------------
 * · MUCHOS más ladrillos (9 x 6 = 54) y 2,5 minutos.
 * · Ladrillos ROJOS (sólo la PALA los rompe) y AZULES (sólo el LÁSER los
 *   destruye: al impactar, el azul EXPLOTA y queda ROJO, no desaparece).
 * · Parte de los ladrillos nacen AZULES; y los ROJOS que quedan vivos se
 *   van VOLVIENDO AZULES con el tiempo (uno cada pocos segundos).
 * · La pistola láser (pistola.glb) va TODO EL RATO en la mano libre:
 *   sólo desaparece el instante del saque (esa mano lanza la bola).
 * · SIN póster-escondite del superpoder tras el muro: pared neutra.
 * · Cristales laterales OTRO +30 cm hacia el jugador (red + 0,60). */
const ARK2_CFG = Object.assign({}, ARK_CFG, {
  variant: 2,
  cols: 9, rows: 6, gap: 0.012,
  bw: (DIMS.tableHalfWidth * 2 - 8 * 0.012) / 9,   // 0,1586 m
  bh: 0.15,
  // v2.46 · +20 cm MÁS: red + 80 cm (30+30+20). Y ojo: la colisión del
  // perímetro usa SIEMPRE this.C (antes _extraCollide leía ARK_CFG fijo y
  // los 50 cm nuevos NO colisionaban — bug del "cristal sin comportamiento").
  sideZ0: DIMS.tableCenterZ + 0.80,  // v2.46: red + 80 cm hacia ti
  time: 150,         // 2,5 minutos (muro del doble de ladrillos)
  lives: 5,
  blueStart: 0.30,   // ~30% de los ladrillos nacen AZULES
  convertFirst: 12,  // gracia (s) antes de la conversión temporal
  convertEvery: 7,   // cada 7 s un ROJO vivo pasa a AZUL
  bombaCada: 15,     // v3.6.45: la bomba sale por INTERVALOS de 15 s
});
ARK_CFG.z = ARK_CFG.sideZ1 + ARK_CFG.depth / 2 + 0.004;
ARK2_CFG.z = ARK2_CFG.sideZ1 + ARK2_CFG.depth / 2 + 0.004;

/* ---------- texturas del muro v2.41 (biselado + flash de destrucción) -- */
function arkBrickTexture() {
  const cv = arcadeCanvas(128, 64);
  const g2 = cv.getContext('2d');
  // textura en ESCALA DE GRISES: el color del material la multiplica
  const grd = g2.createLinearGradient(0, 0, 0, 64);
  grd.addColorStop(0, '#c9c9c9');
  grd.addColorStop(0.16, '#ffffff');      // bisel superior iluminado
  grd.addColorStop(0.52, '#a2a2a2');
  grd.addColorStop(0.88, '#6e6e6e');      // sombra inferior
  grd.addColorStop(1, '#585858');
  g2.fillStyle = grd;
  g2.fillRect(0, 0, 128, 64);
  g2.strokeStyle = 'rgba(0,0,0,0.6)';
  g2.lineWidth = 5;
  g2.strokeRect(0, 0, 128, 64);
  g2.strokeStyle = 'rgba(255,255,255,0.35)';
  g2.lineWidth = 2;
  g2.strokeRect(4, 4, 120, 56);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function arkFlashTexture() {
  const cv = arcadeCanvas(128, 128);
  const g2 = cv.getContext('2d');
  const grd = g2.createRadialGradient(64, 64, 4, 64, 64, 62);
  grd.addColorStop(0, 'rgba(255,240,200,0.95)');
  grd.addColorStop(0.4, 'rgba(255,190,110,0.55)');
  grd.addColorStop(1, 'rgba(255,150,60,0)');
  g2.fillStyle = grd;
  g2.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/* v2.44 · textura de las PARTÍCULAS DE VIENTO del abanico (chorro suave) */
function arkWindTexture() {
  const cv = arcadeCanvas(64, 64);
  const g2 = cv.getContext('2d');
  const grd = g2.createRadialGradient(32, 32, 2, 32, 32, 30);
  grd.addColorStop(0, 'rgba(235,250,255,0.95)');
  grd.addColorStop(0.45, 'rgba(160,225,255,0.5)');
  grd.addColorStop(1, 'rgba(140,210,255,0)');
  g2.fillStyle = grd;
  g2.beginPath();
  g2.ellipse(32, 32, 32, 20, 0, 0, Math.PI * 2);
  g2.fill();
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/* v2.45 · textura del vidrio ESCARCHADO de las paredes laterales: base
 * helada + moteado determinista + panel vertical + brillo diagonal. Da
 * cuerpo al cristal (antes opacity 0,12 liso = "no hay nada"). */
function arkGlassTexture() {
  const cv = arcadeCanvas(256, 256);
  const g2 = cv.getContext('2d');
  const grd = g2.createLinearGradient(0, 0, 0, 256);
  grd.addColorStop(0, '#eaf7fc');
  grd.addColorStop(0.5, '#cfe9f2');
  grd.addColorStop(1, '#b6dae7');
  g2.fillStyle = grd;
  g2.fillRect(0, 0, 256, 256);
  // escarcha (pseudoaleatorio determinista)
  for (let i = 0; i < 460; i++) {
    const x = (i * 97 + 31) % 256, y = (i * 173 + 57) % 256;
    g2.fillStyle = (i % 2) ? 'rgba(255,255,255,0.5)' : 'rgba(110,165,190,0.3)';
    g2.beginPath();
    g2.arc(x, y, 1 + (i % 3) * 0.7, 0, Math.PI * 2);
    g2.fill();
  }
  // banda de brillo diagonal
  const sh = g2.createLinearGradient(0, 256, 256, 0);
  sh.addColorStop(0.32, 'rgba(255,255,255,0)');
  sh.addColorStop(0.5, 'rgba(255,255,255,0.45)');
  sh.addColorStop(0.68, 'rgba(255,255,255,0)');
  g2.fillStyle = sh;
  g2.fillRect(0, 0, 256, 256);
 // junta central del panel de vidrio
  g2.strokeStyle = 'rgba(40,80,100,0.45)';
  g2.lineWidth = 3;
  g2.beginPath(); g2.moveTo(128, 0); g2.lineTo(128, 256); g2.stroke();
  g2.strokeStyle = 'rgba(255,255,255,0.55)';
  g2.lineWidth = 1;
  g2.beginPath(); g2.moveTo(131, 0); g2.lineTo(131, 256); g2.stroke();
  g2.beginPath(); g2.moveTo(125, 0); g2.lineTo(125, 256); g2.stroke();
  // marco sutil
  g2.strokeStyle = 'rgba(30,60,80,0.5)';
  g2.lineWidth = 6;
  g2.strokeRect(0, 0, 256, 256);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}


class ArcadeArkanoid {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.active = false;
    this.inited = false;
    this.variant = 1;          // v2.44: 1 = clásico · 2 = ARKANOID 2 (rojos/azules)
    this.C = ARK_CFG;          // config ACTIVA (se fija en start())
    this.phase = 'idle';       // intro | serve | play | result
    this.phaseT = 0;
    this.time = ARK_CFG.time;
    this.lives = ARK_CFG.lives;
    this.bricksLeft = 0;
    this._hudDirty = true;
    this._lastSec = -1;
    this._warn60 = false;
    this._banner = null;
    this._msg = '';
    this._msgT = 0;
    this._dying = [];
    this._debris = [];
    this._flashes = [];        // v2.41: flashes de destrucción (pool)
    this._netParts = null;     // v2.41: malla/banda/postes de la red
    this._serveT = 0;          // v2.41: tiempo esperando el saque
    this._crossed = false;     // v2.41: la bola cruzó la red en este intento
    this._stuckT = 0;          // v2.42: anti-atasco (bola no jugable)
    this._tokCd = 0;           // v2.42: anti-spam del «tok» de las paredes
    // v2.44 · conversión temporal ROJO->AZUL (sólo variante 2)
    this._convT = 0;
    // v2.46 · LADRILLO NEGRO del TIEMPO EXTRA (sólo variante 2): aparece
    // en los últimos 30 s en huecos de ladrillos destruidos, salta cada 2 s
    // y al destruirlo (bola o láser) regala +1 minuto (UNA sola vez).
    this._timeBrick = null;    // { slot, t, min, max } — activo o null
    this._timeUsed = false;    // el +1 min ya se cogió en esta prueba
    this._time30 = false;      // el aviso sonoro de apremio ya sonó
    this._extraFx = null;      // { pos, t } — plano "+1 MIN" flotando
    // v3.6.44 (ronda 52) · LADRILLO BOMBA (sólo ARKANOID 2): sustituye a un
    // AZUL vivo al azar, dura 4 s en cada ladrillo y SALTA a otro azul;
    // sin azules vivos se esconde. v3.6.45 (ronda 53): la aparición pasa a
    // ser ALEATORIA por INTERVALOS DE 15 s (si hay ladrillos disponibles
    // donde aparecer). Al romperlo (bola o láser) DETONA y arrasa todos
    // los ladrillos en radio de 2 filas × 2 columnas; consumida, no vuelve
    // en toda la partida (se reinicia con cada intento).
    this._bombBrick = null;    // { slot, t } — activo o null
    this._bombUsed = false;    // la bomba ya DETONÓ en esta partida
    this._bombWait = false;    // sin azules vivos: esperando intervalo + azul
    this._bombNext = 2 + Math.random() * 10;  // s: 1.ª aparición (2-12 s)
    this._bombT = 0;           // s en el ladrillo actual (salto a los 4 s)
    this._stageT = 0;          // s de juego de la etapa (intervalos de 15 s)
    // v3.6.45 (ronda 53) · LADRILLO ELÉCTRICO (sólo ARKANOID 2): en los
    // ÚLTIMOS 30 s un azul al azar se ELECTRIFICA (rayitos + chisporroteo;
    // sólo se activa con la BOLA — el láser no lo ve). Al darle con la
    // bola ATRAE hacia sí al resto de los ladrillos y los reparte en las
    // celdas pegadas a su alrededor (anillos, las casillas más próximas
    // primero); todos quedan eléctricos y desde entonces CUALQUIER impacto
    // desencadena una REACCIÓN EN CADENA ramificada que arrasa la pared —
    // misión superada. Se reinicia con cada partida.
    this._eFase = 0;           // 0 nada · 1 sembrado · 2 cadena armada
    this._eSeed = null;        // ladrillo eléctrico sembrado
    this._eMove = [];          // tweens de atracción { b, fx, fy, tx, ty, t }
    this._eCadena = [];        // cola de la reacción en cadena [{ b, t }]
    this._eBoltT = 0;          // flicker de los rayos (regeneración 0,07 s)
    this._eChispT = 0;         // chisporroteo aleatorio
    // v2.44 · ABANICO (corriente de aire para desatascar la bola)
    this._fanSamp = [];        // muestras {t, vx} de la velocidad lateral
    this._fanT = 0;            // segundos restantes de viento activo
    this._fanCd = 0;           // cooldown del abanico
    this._fanKick = 0;         // impulso acumulado (0..1) hasta el empujón
    this._fanBlowT = 0;        // temporizador del soplido sonoro
    this._fanHintDone = false; // el aviso del gesto sólo se muestra una vez
    this._wind = [];           // partículas de viento (pool)
    // v2.42: hook de colisiones ARKANOID por SUBPASO de la física NORMAL
    this._extra = (ball) => this._extraCollide(ball);
    this._spot = new THREE.Vector3();
    this._tmpA = new THREE.Vector3();
    this._tmpB = new THREE.Vector3();
    // v2.133 · BOLA CLON del superpoder (CLOWN Nv. 3: bola doble) — la malla
    // se crea AQUÍ (constructor: UNA vez por sesión) y NO en build(): el
    // split sólo sale en el DUELO JEFE (Nv. 3) y llegando a la etapa 5 con
    // sesión fresca el arkanoid nunca llegó a construirse → clon físico e
    // INVISIBLE (reporte del dueño: «el poder de dos bolas no funciona»). Regla
    // Quest intacta: nada se crea por partida (esto corre una vez, al montar).
    const g0 = this.game;
    this.cloneMesh = new THREE.Mesh(
      g0.ballMesh ? g0.ballMesh.geometry
        : new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),
      new THREE.MeshStandardMaterial({
        color: 0xffffff, roughness: 0.3, emissive: 0xbfd4ff, emissiveIntensity: 0.55,
      }));
    this.cloneMesh.castShadow = true;
    this.cloneMesh.visible = false;
    g0.rig.add(this.cloneMesh);
    // cinturón y tirantes: _startSplit puede exigir la malla en cualquier
    // momento (idempotente) — antes vivía SÓLO en el primer build()
    this._makeCloneMesh = () => {
      if (this.cloneMesh) return;
      const gg = this.game;
      this.cloneMesh = new THREE.Mesh(
        gg.ballMesh ? gg.ballMesh.geometry
          : new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),
        new THREE.MeshStandardMaterial({
          color: 0xffffff, roughness: 0.3, emissive: 0xbfd4ff,
          emissiveIntensity: 0.55,
        }));
      this.cloneMesh.castShadow = true;
      this.cloneMesh.visible = false;
      gg.rig.add(this.cloneMesh);
    };
  }

  build() {
    // v2.44: build con RECONSTRUCCIÓN por variante — el ARKANOID 2 cambia
    // muro (54 ladrillos rojos/azules), perímetro (cristales +60 cm) y
    // pared del fondo (sin póster). Se rellena sólo si cambia la variante.
    if (this.inited && this._builtV === this.variant) return;
    const g = this.game;
    const first = !this.inited;
    this.inited = true;
    const C = this.C;
    const W = C.cols * C.bw + (C.cols - 1) * C.gap;
    const H = C.rows * C.bh + (C.rows - 1) * C.gap;
    this.wallW = W; this.wallH = H;

    if (first) {
      // contenedores y materiales compartidos del decorado arcade
      this.railMat = new THREE.MeshStandardMaterial({
        color: 0xe8b45a, roughness: 0.4, metalness: 0.3, emissive: 0x3d2c08,
      });
      this.darkMat = new THREE.MeshStandardMaterial({
        color: 0x1b2233, roughness: 0.85, metalness: 0.08,
      });
      // v2.45 · CRISTALES con textura de vidrio ESCARCHADO: el material
      // semitransparente se ve LA PARED (moteado + paneles + brillo), no un
      // cristal invisible — se nota que hay un muro contra el que golpear.
      this.glassMat = new THREE.MeshStandardMaterial({
        color: 0xd6eef6, map: arkGlassTexture(), transparent: true,
        opacity: 0.52, roughness: 0.32, metalness: 0.06,
        side: THREE.DoubleSide, depthWrite: false,
      });
      this.fieldGroup = new THREE.Group();
      this.wallGroup = new THREE.Group();
      g.rig.add(this.fieldGroup);   // v2.44: anclado al rig (espacio de la mesa)
      g.rig.add(this.wallGroup);
      // textura de los ladrillos + materiales por COLOR (rojo/azul)
      const brickTex = arkBrickTexture();
      this.redMats = [0xd94f3d, 0xcf4536, 0xe25a46].map((c) =>
        new THREE.MeshStandardMaterial({
          color: c, map: brickTex, roughness: 0.55, metalness: 0.05,
          emissive: 0x2a0705,
        }));
      this.blueMats = [0x2f7fd4, 0x2a6fbe, 0x3a8ce4].map((c) =>
        new THREE.MeshStandardMaterial({
          color: c, map: brickTex, roughness: 0.42, metalness: 0.12,
          emissive: 0x061c38,
        }));
      this.brickGeo = new THREE.BoxGeometry(C.bw, C.bh, C.depth);
      // pools de escombros y flashes (compartidos)
      const dGeo = new THREE.BoxGeometry(0.05, 0.05, 0.05);
      for (let i = 0; i < 30; i++) {
        const dm = new THREE.Mesh(dGeo, this.redMats[0]);
        dm.visible = false;
        this.wallGroup.add(dm);
        this._debris.push({ mesh: dm, vel: new THREE.Vector3(), life: 0 });
      }
      const flashTex = arkFlashTexture();
      for (let i = 0; i < 6; i++) {
        const fm = new THREE.Mesh(
          new THREE.PlaneGeometry(0.55, 0.55),
          new THREE.MeshBasicMaterial({
            map: flashTex, transparent: true, opacity: 0, depthWrite: false,
            blending: THREE.AdditiveBlending,
          }));
        fm.visible = false;
        fm.renderOrder = 9;
        this.wallGroup.add(fm);
        this._flashes.push({ mesh: fm, t: 0 });
      }
      // v2.44 · PARTÍCULAS DE VIENTO del abanico (pool aditivo)
      const wTex = arkWindTexture();
      for (let i = 0; i < 26; i++) {
        const wm = new THREE.Mesh(
          new THREE.PlaneGeometry(0.05, 0.05),
          new THREE.MeshBasicMaterial({
            map: wTex, transparent: true, opacity: 0, depthWrite: false,
            blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
          }));
        wm.visible = false;
        wm.renderOrder = 8;
        g.rig.add(wm);
        this._wind.push({ mesh: wm, vel: new THREE.Vector3(), life: 0 });
      }
      // v2.133: la BOLA CLON (split) vive en el CONSTRUCTOR — aquí ya no se
      // crea (llegar al duelo JEFE sin build del arkanoid dejaba el clon
      // invisible). _makeCloneMesh sigue disponible como cinturón.
      // identificación de la RED (plano + banda + postes) para ocultarla
      this._netParts = g.tableGroup.children.filter((m) =>
        Math.abs(m.position.z - DIMS.tableCenterZ) < 0.02 &&
        m.position.y > DIMS.tableTopY + 0.01);
      // HUD (tiempo + ladrillos + vidas + banners)
      this.hudCv = arcadeCanvas(1024, 214);
      this.hudTex = new THREE.CanvasTexture(this.hudCv);
      this.hudTex.colorSpace = THREE.SRGBColorSpace;
      this.hudGroup = new THREE.Group();
      this.hudPlane = new THREE.Mesh(
        new THREE.PlaneGeometry(2.4, 2.4 * 214 / 1024),
        new THREE.MeshBasicMaterial({
          map: this.hudTex, transparent: true, depthWrite: false,
        }),
      );
      this.hudGroup.add(this.hudPlane);
      this.hudGroup.position.set(0, 2.56, C.z + 0.05);
      this.hudGroup.visible = false;
      g.rig.add(this.hudGroup);   // v2.44: anclado al rig (espacio de la mesa)
    } else {
      // reconstrucción: vaciar los grupos de la variante anterior
      this._clearGroup(this.fieldGroup);
      this._clearGroup(this.wallGroup);
      // el tamaño de los ladrillos cambia entre variantes
      if (this.brickGeo) this.brickGeo.dispose();
      this.brickGeo = new THREE.BoxGeometry(C.bw, C.bh, C.depth);
    }
    this._builtV = this.variant;
    this.bricks = [];

    /* ---- PERÍMETRO = BORDES DE LA MESA (fieldGroup) ------------------ */
    // pared del FONDO (tras el muro): nace en el suelo; sostiene el PÓSTER
    // de la variante (v2.45: AMBAS variantes tienen arte — en la 1 el
    // superpoder, en la 2 la imagen del VIENTO del jugador).
    const wallH = DIMS.tableTopY + C.backY;
    const backWall = new THREE.Mesh(
      new THREE.BoxGeometry(2 * C.sideX + 0.12, wallH, 0.08), this.darkMat);
    backWall.position.set(0, wallH / 2, C.sideZ1 - 0.04);
    this.fieldGroup.add(backWall);
    {
      // v2.45 · PÓSTER tras el muro: DETRÁS de los ladrillos y DELANTE de la
      // pared del fondo (a 1 mm), como en el ARKANOID 1 — el arte cambia
      // según la variante (superpoder · viento.png).
      const pw = W - 0.05, ph = pw * 768 / 1365;
      this.posterMat = new THREE.MeshBasicMaterial({
        color: 0x23282e, depthWrite: false,
      });
      this.poster = new THREE.Mesh(
        new THREE.PlaneGeometry(pw, ph), this.posterMat);
      this.poster.position.set(0, C.baseY + H / 2, C.sideZ1 + 0.001);
      this.fieldGroup.add(this.poster);
      // arte embebido (data URL) — llega asíncrono
      const purl = (this.variant === 1) ?
        (typeof window !== 'undefined' && window.__PP_GUNPOSTER_URL) :
        (typeof window !== 'undefined' && window.__PP_WIND_URL);
      if (purl) {
        const pimg = new Image();
        pimg.onload = () => {
          const ptex = new THREE.Texture();
          ptex.colorSpace = THREE.SRGBColorSpace;
          ptex.image = pimg;
          ptex.needsUpdate = true;
          this.posterMat.map = ptex;
          this.posterMat.color.setHex(0xffffff);
          this.posterMat.needsUpdate = true;
        };
        pimg.src = purl;
      }
    }
    // v2.46 · LADRILLO NEGRO del TIEMPO EXTRA: malla negra + reloj.png
    // superpuesto (aparece en huecos de ladrillos destruidos en los últimos
    // 30 s del ARKANOID 2) y plano extra.png "+1 MIN" que flota al reventar.
    this.blackMat = this.blackMat || new THREE.MeshStandardMaterial({
      color: 0x0b0b0e, roughness: 0.35, metalness: 0.5,
      emissive: 0x16181d, emissiveIntensity: 0.5,
    });
    this.timeMesh = new THREE.Mesh(this.brickGeo, this.blackMat);
    this.timeMesh.castShadow = true;
    this.timeMesh.visible = false;
    this.wallGroup.add(this.timeMesh);
    this.timeClockMat = this.timeClockMat || new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, side: THREE.FrontSide,
    });
    this.timeClock = new THREE.Mesh(
      new THREE.PlaneGeometry(C.bw * 0.62, C.bw * 0.62), this.timeClockMat);
    this.timeClock.visible = false;
    this.timeClock.renderOrder = 6;
    this.wallGroup.add(this.timeClock);
    if (!this._relojLoading) {
      this._relojLoading = true;
      const rurl = (typeof window !== 'undefined' && window.__PP_RELOJ_URL);
      if (rurl) {
        const rimg = new Image();
        rimg.onload = () => {
          const rt = new THREE.Texture();
          rt.colorSpace = THREE.SRGBColorSpace;
          rt.image = rimg;
          rt.needsUpdate = true;
          this.timeClockMat.map = rt;
          this.timeClockMat.needsUpdate = true;
        };
        rimg.src = rurl;
      }
    }
    this.extraGeo = this.extraGeo || new THREE.PlaneGeometry(0.34, 0.34);
    this.extraMat = this.extraMat || new THREE.MeshBasicMaterial({
      transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide,
    });
    this.extraPlane = new THREE.Mesh(this.extraGeo, this.extraMat);
    this.extraPlane.visible = false;
    this.extraPlane.renderOrder = 8;
    this.wallGroup.add(this.extraPlane);
    if (!this._extraLoading) {
      this._extraLoading = true;
      const eurl = (typeof window !== 'undefined' && window.__PP_EXTRA_URL);
      if (eurl) {
        const eimg = new Image();
        eimg.onload = () => {
          const et = new THREE.Texture();
          et.colorSpace = THREE.SRGBColorSpace;
          et.image = eimg;
          et.needsUpdate = true;
          this.extraMat.map = et;
          this.extraMat.needsUpdate = true;
        };
        eimg.src = eurl;
      }
    }
    // v3.6.44 (ronda 52) · LADRILLO BOMBA: malla NEGRA (misma blackMat del
    // tiempo extra) + icono bomba.webp superpuesto DELANTE — diseño del
    // estilo del reloj (cartela blanca, silueta negra), a petición del
    // dueño: «similar al ladrillo del reloj pero con el dibujo de una
    // bomba». La bola lo REVIENTA (detonación) y el láser también.
    this.bombMesh = new THREE.Mesh(this.brickGeo, this.blackMat);
    this.bombMesh.castShadow = true;
    this.bombMesh.visible = false;
    this.wallGroup.add(this.bombMesh);
    this.bombIconMat = this.bombIconMat || new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, side: THREE.FrontSide,
    });
    this.bombIcon = new THREE.Mesh(
      new THREE.PlaneGeometry(C.bw * 0.62, C.bw * 0.62), this.bombIconMat);
    this.bombIcon.visible = false;
    this.bombIcon.renderOrder = 6;
    this.wallGroup.add(this.bombIcon);
    if (!this._bombaLoading) {
      this._bombaLoading = true;
      const burl = (typeof window !== 'undefined' && window.__PP_BOMBA_URL);
      if (burl) {
        const bimg = new Image();
        bimg.onload = () => {
          const bt = new THREE.Texture();
          bt.colorSpace = THREE.SRGBColorSpace;
          bt.image = bimg;
          bt.needsUpdate = true;
          this.bombIconMat.map = bt;
          this.bombIconMat.needsUpdate = true;
        };
        bimg.src = burl;
      }
    }
    // v3.6.45 (ronda 53) · LADRILLO ELÉCTRICO: material AZUL que EMITE
    // cian (la pared electrificada SE VE brillar), icono del RAYO (cartela
    // blanca + silueta negra + chispa cian — familia del reloj/bomba,
    // dibujado EN CÓDIGO: cero assets nuevos) y pool de 14 RAYOS 3D
    // (líneas dentadas aditivas) que CHISPORROTEAN sobre los ladrillos
    // eléctricos. Nada se crea por partida: todo nace aquí (regla Quest).
    this.eBrickMat = this.eBrickMat || new THREE.MeshStandardMaterial({
      color: 0x2f7fd4, roughness: 0.25, metalness: 0.65,
      emissive: 0x36c9ff, emissiveIntensity: 0.8,
    });
    this.eIconMat = this.eIconMat || new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, side: THREE.FrontSide,
    });
    this.eIcon = new THREE.Mesh(
      new THREE.PlaneGeometry(C.bw * 0.62, C.bw * 0.62), this.eIconMat);
    this.eIcon.visible = false;
    this.eIcon.renderOrder = 6;
    this.wallGroup.add(this.eIcon);
    if (!this._eIconReady) {
      this._eIconReady = true;
      const cvE = document.createElement('canvas');
      cvE.width = 256; cvE.height = 256;
      const ge = cvE.getContext('2d');
      // cartela blanca redondeada (la misma familia del reloj y la bomba)
      ge.fillStyle = '#f4f4f0';
      ge.beginPath();
      if (ge.roundRect) ge.roundRect(18, 18, 220, 220, 26);
      else ge.rect(18, 18, 220, 220);
      ge.fill();
      ge.strokeStyle = 'rgba(30,60,80,0.5)'; ge.lineWidth = 7;
      ge.stroke();
      // silueta NEGRA del rayo (como la bomba y el reloj: silueta negra)
      ge.fillStyle = '#111114';
      ge.beginPath();
      ge.moveTo(148, 44); ge.lineTo(92, 138); ge.lineTo(126, 138);
      ge.lineTo(104, 212); ge.lineTo(172, 112); ge.lineTo(134, 112);
      ge.lineTo(160, 44);
      ge.closePath(); ge.fill();
      // chispa cian (la firma eléctrica que lo distingue de la familia)
      ge.strokeStyle = '#22b1e0'; ge.lineWidth = 6; ge.lineCap = 'round';
      ge.beginPath();
      ge.moveTo(196, 60); ge.lineTo(184, 78); ge.lineTo(198, 82);
      ge.lineTo(182, 102);
      ge.moveTo(70, 178); ge.lineTo(84, 166); ge.lineTo(74, 156);
      ge.lineTo(92, 146);
      ge.stroke();
      const etx = new THREE.CanvasTexture(cvE);
      etx.colorSpace = THREE.SRGBColorSpace;
      this.eIconMat.map = etx;
      this.eIconMat.needsUpdate = true;
    }
    this.eBoltMat = this.eBoltMat || new THREE.LineBasicMaterial({
      color: 0xaee9ff, transparent: true, opacity: 0.95,
      blending: THREE.AdditiveBlending, depthWrite: false,
    });
    if (!this.eBolts) {
      this.eBolts = [];
      for (let i = 0; i < 14; i++) {
        const geoB = new THREE.BufferGeometry();
        geoB.setAttribute('position',
          new THREE.BufferAttribute(new Float32Array(4 * 3), 3));
        const ln = new THREE.Line(geoB, this.eBoltMat);
        ln.visible = false;
        ln.renderOrder = 7;
        ln.frustumCulled = false;
        this.wallGroup.add(ln);
        this.eBolts.push(ln);
      }
    }
    // 2 PAREDES LATERALES de cristal (marco ámbar + rodapié + remate),
    // EN EL BORDE de la mesa (4 mm fuera para no z-fight con el canto).
    // v2.44: longitud C.sideZ0 - C.sideZ1 — con la extensión hacia el
    // jugador (30 cm en la variante 1, 60 cm en la 2) ya NO hay huecos.
    const sl = C.sideZ0 - C.sideZ1;
    const sz = (C.sideZ0 + C.sideZ1) / 2;
    const glassH = DIMS.tableTopY + C.glassY;
    // v2.46 · MARCOS FINOS (2,2 cm) y centrados FUERA del plano del vidrio:
    // antes (5 cm, centrados EN la pared) tapaban las esquinas de los
    // ladrillos de los extremos del muro.
    for (const sx of [-C.sideX - 0.013, C.sideX + 0.013]) {
      const pane = new THREE.Mesh(new THREE.PlaneGeometry(sl, glassH), this.glassMat);
      pane.rotation.y = Math.PI / 2;
      pane.position.set(sx, glassH / 2, sz);
      this.fieldGroup.add(pane);
      const foot = new THREE.Mesh(
        new THREE.BoxGeometry(0.022, 0.035, sl), this.darkMat);
      foot.position.set(sx, 0.0175, sz);
      this.fieldGroup.add(foot);
      const cap = new THREE.Mesh(
        new THREE.BoxGeometry(0.022, 0.022, sl), this.railMat);
      cap.position.set(sx, glassH - 0.011, sz);
      this.fieldGroup.add(cap);
      for (const pz of [C.sideZ0 - 0.011, C.sideZ1 + 0.011]) {
        const post = new THREE.Mesh(
          new THREE.BoxGeometry(0.022, glassH, 0.022), this.railMat);
        post.position.set(sx, glassH / 2, pz);
        this.fieldGroup.add(post);
      }
    }

    /* ---- MURO DE LADRILLOS (wallGroup): SOBRE la mesa, ENRASADO ------ */
    // v2.46 · estructura FINA: pilares de 2,2 cm PEGADOS AL CANTO EXTERIOR
    // (antes 6 cm centrados dentro del muro = tapaban los ladrillos de los
    // extremos) y listón superior fino sin voladizo.
    const stand = new THREE.Mesh(
      new THREE.BoxGeometry(W, 0.03, C.depth + 0.02), this.darkMat);
    stand.position.set(0, C.baseY - 0.016, C.z);
    this.wallGroup.add(stand);
    const mkRail = (w, h, x, y, d) => {
      const r = new THREE.Mesh(new THREE.BoxGeometry(w, h, d || 0.05), this.railMat);
      r.position.set(x, y, C.z);
      this.wallGroup.add(r);
    };
    mkRail(W, 0.016, 0, C.baseY + H + 0.008, 0.04);
    for (const px of [-W / 2 - 0.011, W / 2 + 0.011]) {
      const pil = new THREE.Mesh(
        new THREE.BoxGeometry(0.022, H + 0.02, C.depth), this.railMat);
      pil.position.set(px, C.baseY + (H + 0.02) / 2, C.z);
      this.wallGroup.add(pil);
    }
    // LADRILLOS — variante 1: todos ROJOS · variante 2: rojos + azules
    for (let r = 0; r < C.rows; r++) {
      for (let c = 0; c < C.cols; c++) {
        const blue = this.variant === 2 &&
          ((r * 7 + c * 5 + 3) % 10) < Math.round(C.blueStart * 10);
        const m = new THREE.Mesh(this.brickGeo,
          blue ? this.blueMats[(r * 3 + c) % 3] : this.redMats[(r * 3 + c) % 3]);
        const x = -W / 2 + C.bw / 2 + c * (C.bw + C.gap);
        const y = C.baseY + C.bh / 2 + r * (C.bh + C.gap);
        m.position.set(x, y, C.z);
        m.castShadow = true;
        this.wallGroup.add(m);
        this.bricks.push({
          mesh: m, home: m.position.clone(), alive: true,
          state: blue ? 'blue' : 'red',   // v2.44: color lógico del ladrillo
          state0: blue ? 'blue' : 'red',  // v3.6.45: original (start restaura)
          matIdx: (r * 3 + c) % 3,        // v2.44: tono dentro de su paleta
          min: new THREE.Vector3(x - C.bw / 2, y - C.bh / 2, C.z - C.depth / 2),
          max: new THREE.Vector3(x + C.bw / 2, y + C.bh / 2, C.z + C.depth / 2),
        });
      }
    }
    this.wallGroup.visible = false;
    this.fieldGroup.visible = false;
    this._hudDirty = true;
  }

  /** Vacía un grupo (v2.44: reconstrucción entre variantes). */
  _clearGroup(gr) {
    if (!gr) return;
    for (let i = gr.children.length - 1; i >= 0; i--) {
      const ch = gr.children[i];
      const isPool = this._debris.some((d) => d.mesh === ch) ||
        this._flashes.some((f) => f.mesh === ch);
      if (isPool) continue;   // los pools sobreviven a la reconstrucción
      gr.remove(ch);
    }
  }

  /* ---------------- ciclo de vida ---------------- */

  start() {
    const g = this.game;
    // v2.44: la ETAPA del camino elige la variante (3 = ARKANOID 2)
    this.variant = (this.ctrl && this.ctrl.stage >= 3) ? 2 : 1;
    this.C = this.variant === 2 ? ARK2_CFG : ARK_CFG;
    this.build();
    if (this.active) return;
    this.active = true;
    this.phase = 'intro';
    this.phaseT = 2.6;
    this.time = this.C.time;
    this._lastSec = Math.ceil(this.time) + 1;
    this._warn60 = false;
    this.lives = this.C.lives;
    // v2.44: estado de la conversión temporal y del abanico
    this._convT = 0;
    this._fanSamp.length = 0;
    this._fanT = 0; this._fanCd = 0; this._fanKick = 0; this._fanBlowT = 0;
    // v2.46: el ladrillo negro del tiempo vuelve a estar disponible en cada
    // intento (UNO por prueba); fuera restos del intento anterior
    this._timeBrick = null;
    this._timeUsed = false;
    this._time30 = false;
    this._extraFx = null;
    if (this.timeMesh) this.timeMesh.visible = false;
    if (this.timeClock) this.timeClock.visible = false;
    if (this.extraPlane) this.extraPlane.visible = false;
    // v3.6.44 · la BOMBA también SE REINICIA CON CADA PARTIDA (petición
    // del dueño: «se reinicia con cada partida»); v3.6.45: la 1.ª aparición
    // vuelve a caer ALEATORIA dentro del primer intervalo (2-12 s).
    this._bombBrick = null;
    this._bombUsed = false;
    this._bombWait = false;
    this._bombNext = 2 + Math.random() * 10;
    this._bombT = 0;
    this._stageT = 0;
    if (this.bombMesh) this.bombMesh.visible = false;
    if (this.bombIcon) this.bombIcon.visible = false;
    // v3.6.45 · el ELÉCTRICO se reinicia con cada partida (fase 0, sin
    // semilla, sin cadena ni tweens, rayos e icono fuera; cada ladrillo
    // recupera su color ORIGINAL — state0 — y su sitio en el muro).
    this._eFase = 0;
    this._eSeed = null;
    this._eMove.length = 0;
    this._eCadena.length = 0;
    this._eBoltT = 0;
    this._eChispT = 0;
    if (this.eIcon) this.eIcon.visible = false;
    for (const ln of this.eBolts || []) ln.visible = false;
    this.bricksLeft = this.bricks.length;
    for (const b of this.bricks) {
      b.alive = true;
      b.mesh.visible = true;
      b.mesh.scale.setScalar(1);
      b.mesh.rotation.set(0, 0, 0);
      b.mesh.position.copy(b.home);
      if (b.state0) b.state = b.state0;   // v3.6.45: color ORIGINAL de fábrica
      // v2.44: el material refleja el color lógico (rojo/azul al reiniciar)
      b.mesh.material = b.state === 'blue' ? this.blueMats[b.matIdx] : this.redMats[b.matIdx];
    }
    this._dying.length = 0;
    for (const d of this._debris) d.mesh.visible = false;
    for (const f of this._flashes) { f.t = 0; f.mesh.visible = false; }
    for (const w of this._wind) { w.life = 0; w.mesh.visible = false; }
    this._banner = this.variant === 2
      ? { title: T('ark2_title'), sub: T('ark2_intro'), col: '#ffd257' }
      : { title: T('ark_title'), sub: T('ark_intro'), col: '#ffd257' };
    this._msg = '';
    this._msgT = 0;
    this._hudDirty = true;
    // v2.41: la MESA SIGUE en escena (¡el muro se apoya en ella!) pero SIN
    // RED: esta variante se juega sin red. Marcador y pala IA fuera.
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    for (const m of this._netParts || []) m.visible = false;
    g.fanfareBanner.group.visible = false;
    g.confettiBurst = 0;
    g.ballMesh.scale.setScalar(1);        // v2.42: bola NORMAL (ni x2 ni roja)
    g.ball.ignoreNet = true;              // v2.42: la mesa va SIN red (ni físicas)
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    this._crossed = false;
    this._stuckT = 0;
    this._tokCd = 0;
    const a = this.ctrl;
    a.rival.hide();
    a.cartel.hide();
    a.rankPanel.hide();
    a.powerSign.hide();
    g.rules.state = 'arkanoid';           // el árbitro queda en pausa
    g.rules.message = T('ark_title');
    this.wallGroup.visible = true;
    this.fieldGroup.visible = true;
    this.hudGroup.visible = true;
    // jingle de arranque
    g.audio.playOsc(523, 523, 0.11, 'square', 0.11, 0);
    window.setTimeout(() => g.audio.playOsc(659, 659, 0.11, 'square', 0.11, 0), 130);
    window.setTimeout(() => g.audio.playOsc(784, 784, 0.2, 'square', 0.12, 0), 260);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 120);
  }

  /** Reanudar al volver a VR: el árbitro vuelve a pausa y SAQUE de nuevo
   *  SIN coste de vida (el tiempo y los ladrillos quedan como estaban). */
  reenter() {
    if (!this.active) return;
    const g = this.game;
    g.rules.state = 'arkanoid';
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    for (const m of this._netParts || []) m.visible = false;
    if (this.phase === 'play' || this.phase === 'intro') {
      this.phase = 'serve';
      this._serveT = 0;
      this._msg = T('ark_serve_hint');
    }
    this._hudDirty = true;
  }

  /** Devuelve la escena a la normalidad (mesa CON red, marcador, rival). */
  stop() {
    this.active = false;
    this.phase = 'idle';
    if (!this.inited) return;
    const g = this.game;
    this.wallGroup.visible = false;
    this.fieldGroup.visible = false;
    this.hudGroup.visible = false;
    for (const b of this.bricks) {
      b.alive = true;
      b.mesh.visible = true;
      b.mesh.scale.setScalar(1);
      b.mesh.rotation.set(0, 0, 0);
      b.mesh.position.copy(b.home);
    }
    this._dying.length = 0;
    for (const d of this._debris) d.mesh.visible = false;
    for (const f of this._flashes) { f.t = 0; f.mesh.visible = false; }
    // v2.46: fuera el ladrillo negro del tiempo y el "+1 MIN"
    this._timeBrick = null;
    this._extraFx = null;
    if (this.timeMesh) this.timeMesh.visible = false;
    if (this.timeClock) this.timeClock.visible = false;
    if (this.extraPlane) this.extraPlane.visible = false;
    // v2.41: la red vuelve a la mesa
    for (const m of this._netParts || []) m.visible = true;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = true;
    g.aiPaddleMesh.visible = true;
    g.ballMesh.scale.setScalar(1);
    g.ball.ignoreNet = false;             // v2.42: la red vuelve a colisionar
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
  }

  /* ---------------- bucle de la prueba ---------------- */

  step(dt) {
    if (!this.active || !this.inited) return;
    const g = this.game;
    const ball = g.ball;
    if (this.phase === 'intro') {
      this.phaseT -= dt;
      this._holdBallInHand();       // v2.41: la bola espera en tu mano libre
      if (this.phaseT <= 0) this._enterServe();
    } else if (this.phase === 'serve') {
      // v2.41: SAQUE de partida normal — bola en la mano libre, gatillo
      // para lanzarla. Sin acción, saque automático (nunca se atasca).
      this._serveT += dt;
      this._holdBallInHand();
      if (!this._msg) {
        this._msg = T('ark_serve_hint');
        this._hudDirty = true;
      }
      if (this._serveT > this.C.serveAutoT) {
        this._msg = T('ark_autoserve');
        this.serveTrigger(true);
      }
    } else if (this.phase === 'play') {
      this._tokCd = Math.max(0, this._tokCd - dt);
      // v3.6.45 · la REACCIÓN EN CADENA congela el contador: el gran final
      // eléctrico se completa SIEMPRE (nadie pierde a mitad del destrozo)
      if (!this._eCadena.length) this.time -= dt;
      if (this.time <= 0) {
        this.time = 0;
        this._hudDirty = true;
        this._finish(false, 'time');
        return;
      }
      const sec = Math.ceil(this.time);
      if (sec <= 60 && !this._warn60) {
        // AVISO: se baja de 1 minuto (doble pitido)
        this._warn60 = true;
        this._hudDirty = true;
        g.audio.playOsc(880, 880, 0.12, 'square', 0.16, 0);
        window.setTimeout(() => g.audio.playOsc(880, 880, 0.12, 'square', 0.16, 0), 190);
      }
      if (sec !== this._lastSec) {
        this._lastSec = sec;
        this._hudDirty = true;
        if (this._warn60 && sec > 10) {
          g.audio.playOsc(760, 760, 0.045, 'sine', 0.07, 0);
        }
        if (sec <= 10 && sec >= 1) {
          // ALARMA: últimos 10 segundos
          g.audio.playOsc(980, 620, 0.16, 'sawtooth', 0.2, 0);
          if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.3, 60);
        }
      }
      // v2.46 · APREMIO: al entrar en los ÚLTIMOS 30 s suena un aviso de
      // urgencia (tres dobles-bips) y se activa el ladrillo negro del
      // TIEMPO EXTRA. Una sola vez: con el +1 min cogido, no repite.
      if (this.variant === 2 && sec <= 30 && !this._time30) {
        this._time30 = true;
        this._hudDirty = true;
        for (let k = 0; k < 3; k++) {
          window.setTimeout(() => {
            g.audio.playOsc(640, 980, 0.09, 'square', 0.13, 0);
          }, k * 230);
          window.setTimeout(() => {
            g.audio.playOsc(640, 980, 0.09, 'square', 0.13, 0);
          }, k * 230 + 105);
        }
      }
      // v3.6.45 · LADRILLO ELÉCTRICO: al entrar en los ÚLTIMOS 30 s UN azul
      // al azar se electrifica (si no hay azules aún, reintenta hasta que
      // la conversión temporal genere uno)
      if (this.variant === 2 && sec <= 30 && !this._eFase) this._eSembrar();
      // v2.44 · CONVERSIÓN TEMPORAL ROJO->AZUL (sólo variante 2): cada pocos
      // segundos UN ladrillo ROJO vivo pasa a AZUL. Los AZULES NUNCA se
      // eligen (el bug del ladrillo negro: azul elegido = se rompía la
      // lógica); sólo los ROJOS son candidatos.
      if (this.variant === 2 && this.C.convertEvery) {
        this._convT += dt;
        if (this._convT >= this.C.convertEvery) {
          this._convT -= this.C.convertEvery;
          if (this._convT < 0) this._convT = 0;
          this._convertRandomRed();
        }
      }
      // v2.46 · LADRILLO NEGRO del tiempo extra (aparición y saltos)
      this._timeUpdate(dt);
      // v3.6.44 · LADRILLO BOMBA (aparición, saltos y espera por azules)
      this._bombUpdate(dt);
      // v2.44 · ABANICO: corriente de aire para empujar la bola al muro
      this._fanUpdate(dt);
      this._physics(dt);
      if (!this.active) return;             // pudo terminar dentro
      if (this.bricksLeft <= 0) {
        this._finish(true);
        return;
      }
    } else if (this.phase === 'result') {
      this.phaseT -= dt;
      if (this.phaseT <= 0) {
        this._afterResult();
        return;
      }
    }
    this._eUpdate(dt);                    // v3.6.45: rayos · chisporroteo · cadena
    this._anims(dt);
    if (this._msgT > 0) {
      this._msgT -= dt;
      if (this._msgT <= 0) { this._msg = ''; this._hudDirty = true; }
    }
    if (this._hudDirty) this._hud();
  }

  /* ---------------- saque (v2.41: como en partida normal) ---------------- */

  /** Fallback del punto de saque (sin mano activa): igual que el del
   *  juego normal (bola sobre la línea de fondo de tu campo). */
  _serveSpot() {
    return this._spot.set(0.3, 1.05,
      DIMS.tableCenterZ + DIMS.tableHalfLength + 0.4);
  }

  /** La bola "apoyada" en la mano libre (igual que el saque normal). */
  _holdBallInHand() {
    const g = this.game;
    const bh = g.controllerPaddles && g.controllerPaddles[g.ballHand];
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    if (bh && bh.active && bh.pos) {
      g.ball.pos.copy(bh.pos);
      g.ball.pos.y += 0.08;                     // BALL_HAND_LIFT
    } else {
      g.ball.pos.copy(this._serveSpot());
    }
  }

  _enterServe() {
    this.phase = 'serve';
    this._serveT = 0;
    this._msg = T('ark_serve_hint');
    this._hudDirty = true;
  }

  /** v2.41 · GATILLO = lanzamiento asistido (mismo gesto que el saque
   *  asistido de una partida normal): la bola sale de la mano libre y la
   *  golpeas con la pala; la física de la prueba la mantiene viva hasta
   *  que la devuelvas al muro. force = saque automático (ignora la mano). */
  serveTrigger(force) {
    if (!this.active || this.phase !== 'serve') return;
    const g = this.game;
    const hand = g.controllerPaddles && g.controllerPaddles[g.ballHand];
    const v = (!force && hand && hand.active && hand.vel)
      ? this._tmpA.copy(hand.vel)
      : this._tmpA.set(0, 0, 0);
    if (v.y < DIMS.serveAssistVy) {
      v.y = DIMS.serveAssistVy;
      v.x *= 0.4;
      v.z *= 0.4;
    }
    // v2.42: asistencia de alcance como en el SAQUE NORMAL (bola recién
    // lanzada); se retira en el primer golpeo de pala
    const ps2 = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    if (ps2) ps2.extraReach = DIMS.serveExtraReach;
    this.phase = 'play';
    this._lastSec = Math.ceil(this.time) + 1;
    this._crossed = false;
    this._msg = '';
    this._hudDirty = true;
    g.ball.vel.copy(v);
    g.ball.spin.set(0, 0, 0);
    g.audio.serve();
    g.rules.message = T('hint_hit');
    if (g.renderer.xr.isPresenting) g.haptic(g.ballHand, 0.45);
  }

  /* ------------- física (v2.42: la de una PARTIDA NORMAL) ------------- */

  /** FÍSICA DE PARTIDA NORMAL: MISMA integración (gravedad real, arrastre
   *  aerodinámico, Magnus), MISMO golpeo de pala (colocas la bola igual que
   *  en un rally: la pala manda) y MISMA mesa. Los eventos van al array del
   *  juego, así que processEvents() suena solo (pala, mesa, suelo) y el
   *  árbitro los ignora (estado 'arkanoid'). Lo ÚNICO añadido son las
   *  colisiones del recinto, por SUBPASO (this._extra): ladrillos que se
   *  rompen, 3 paredes perimetrales y bote MÍNIMO de mesa. */
  _physics(dt) {
    const g = this.game;
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    const pads = (ps && ps.active) ? [ps] : [];
    stepPhysics(dt, g.ball, pads, g.events, this._extra);
    // el alcance extra del SAQUE se retira en el primer golpeo de pala
    if (ps && ps.extraReach) {
      for (const e of g.events) {
        if (e.type === 'paddle') { ps.extraReach = 0; break; }
      }
    }
    // marcador de cruce (para el coste de vida justo)
    if (!this._crossed && g.ball.pos.z < this.C.sideZ0 - 0.05) {
      this._crossed = true;
    }
    this._checkLost(dt);
  }

  /** Bola perdida: al SUELO o por detrás del jugador (SOLO si cruzó al
   *  campo rival en este intento) o ATASCADA (bola casi parada en zona
   *  rival — p. ej. sobre el muro — o bajo la mesa). Sin cruce previo no
   *  hay coste: saque nuevo sin perder vida (toss fallado, p. ej.). */
  _checkLost(dt) {
    const g = this.game;
    const p = g.ball.pos, v = g.ball.vel;
    let lost = false;
    for (const e of g.events) {
      if (e.type === 'floor') { lost = true; break; }
    }
    if (!lost) {
      const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
      const lostZ = Math.min(2.05, (ps && ps.active && ps.pos)
        ? THREE.MathUtils.clamp(ps.pos.z, -0.5, 1.2) + 0.8 : 1.4);
      if (this._crossed && p.z > lostZ && v.z > 0) lost = true;
    }
    if (!lost && v.length() < 0.6 &&
        (p.z < this.C.sideZ0 || p.y < DIMS.tableTopY - 0.06)) {
      this._stuckT += dt;
      if (this._stuckT > 1.5) lost = true;
    } else {
      this._stuckT = 0;
    }
    if (!lost) return;
    if (this._crossed) this._lifeLost();
    else { this._crossed = false; this._enterServe(); }
  }

  /** v2.42 · COLISIONES ARKANOID (por SUBPASO de la física normal):
   *  1) perímetro EN LOS BORDES DE LA MESA — 2 cristales laterales + pared
   *     del fondo (donde brilla el póster del superpoder): reflexión física
   *     con pequeña pérdida;  2) la MESA OTORGA FUERZA MÍNIMA de bote (la
   *  bola nunca queda muerta sobre la superficie);  3) LADRILLOS: esfera vs
   *  AABB con reflexión ESPECULAR (físicamente correcta: un golpe en la cara
   *  frontal vuelve hacia el jugador, como devolvería cualquier superficie
   *  rígida) + destrucción con efecto. */
  _extraCollide(ball) {
    const p = ball.pos, v = ball.vel;
    const r = DIMS.ballRadius;           // bola NORMAL de 40 mm
    // v2.46 · SIEMPRE la config de la VARIANTE activa: antes leía ARK_CFG
    // fijo y en el ARKANOID 2 la zona ampliada de los cristales (red +80 cm)
    // se veía pero NO colisionaba más allá de red +30 cm.
    const C = this.C;
    if (p.z < C.sideZ0) {
      // --- laterales: EXACTAMENTE en los bordes de la mesa
      if (p.x < -C.sideX + r) {
        p.x = -C.sideX + r;
        if (v.x < 0) { v.x = -v.x * C.wallRest; this._wallTok(p.x); }
      } else if (p.x > C.sideX - r) {
        p.x = C.sideX - r;
        if (v.x > 0) { v.x = -v.x * C.wallRest; this._wallTok(p.x); }
      }
      // --- pared del FONDO (tras el muro: el póster del superpoder)
      if (p.z < C.sideZ1 + 0.032) {
        p.z = C.sideZ1 + 0.032;
        if (v.z < 0) { v.z = -v.z * C.wallRest; this._wallTok(0); }
      }
    }
    // --- MESA con FUERZA MÍNIMA: tras el bote normal de collideTable, si
    // la subida no alcanzaría apexMin se OTORGA la energía que falte
    if (v.y >= 0 && p.y <= DIMS.tableTopY + r + 0.004 &&
        Math.abs(p.x) <= DIMS.tableHalfWidth &&
        Math.abs(p.z - DIMS.tableCenterZ) <= DIMS.tableHalfLength) {
      const need = Math.sqrt(2 * Math.abs(DIMS.gravity) * C.apexMin);
      if (v.y < need) v.y = need;
    }
    // --- LADRILLOS: esfera vs AABB — reflexión especular + rotura
    const r2 = (r + 0.002) * (r + 0.002);
    for (const b of this.bricks) {
      if (!b.alive) continue;
      // v3.6.44 · el slot ocupado por la BOMBA no colisiona (su ladrillo
      // azul está OCULTO debajo — la bomba captura esa zona con SU bloque)
      if (this._bombBrick && b === this._bombBrick.slot) continue;
      if (p.z - r > b.max.z || p.z + r < b.min.z) continue;
      if (p.x - r > b.max.x || p.x + r < b.min.x) continue;
      if (p.y - r > b.max.y || p.y + r < b.min.y) continue;
      const cx = THREE.MathUtils.clamp(p.x, b.min.x, b.max.x);
      const cy = THREE.MathUtils.clamp(p.y, b.min.y, b.max.y);
      const cz = THREE.MathUtils.clamp(p.z, b.min.z, b.max.z);
      let nx = p.x - cx, ny = p.y - cy, nz = p.z - cz;
      const d2 = nx * nx + ny * ny + nz * nz;
      if (d2 > r2) continue;
      if (d2 > 1e-9) {
        const d = Math.sqrt(d2);
        nx /= d; ny /= d; nz /= d;
        p.x = cx + nx * (r + 0.003);
        p.y = cy + ny * (r + 0.003);
        p.z = cz + nz * (r + 0.003);
      } else {
        // centro dentro del ladrillo: eje de MÍNIMA penetración
        const dxs = Math.min(p.x - b.min.x, b.max.x - p.x);
        const dys = Math.min(p.y - b.min.y, b.max.y - p.y);
        const dzs = Math.min(p.z - b.min.z, b.max.z - p.z);
        nx = 0; ny = 0; nz = 0;
        if (dzs <= dxs && dzs <= dys) {
          nz = (p.z - (b.min.z + b.max.z) / 2) >= 0 ? 1 : -1;
          p.z = nz > 0 ? b.max.z + r + 0.003 : b.min.z - r - 0.003;
        } else if (dxs <= dys) {
          nx = (p.x - (b.min.x + b.max.x) / 2) >= 0 ? 1 : -1;
          p.x = nx > 0 ? b.max.x + r + 0.003 : b.min.x - r - 0.003;
        } else {
          ny = (p.y - (b.min.y + b.max.y) / 2) >= 0 ? 1 : -1;
          p.y = ny > 0 ? b.max.y + r + 0.003 : b.min.y - r - 0.003;
        }
      }
      const vn = v.x * nx + v.y * ny + v.z * nz;
      if (vn < 0) {
        // reflexión especular y pérdida SOLO de la componente normal
        v.x -= 2 * vn * nx;
        v.y -= 2 * vn * ny;
        v.z -= 2 * vn * nz;
        const vno = v.x * nx + v.y * ny + v.z * nz;
        v.x -= nx * vno * (1 - C.brickRest);
        v.y -= ny * vno * (1 - C.brickRest);
        v.z -= nz * vno * (1 - C.brickRest);
      }
      // v3.6.45 · ELÉCTRICO: el golpe de la BOLA es su gatillo — con la
      // semilla (fase 1) ATRAE al resto y electrifica la pared; armada la
      // cadena (fase 2), CUALQUIER impacto desencadena la reacción en
      // cadena ramificada. Inmune al láser (el rayo ni siquiera lo ve).
      if (b.state === 'elec') {
        if (this._eFase === 1) this._eAtraer(b);
        else if (this._eFase === 2) this._eCadenaDesde(b);
      } else if (b.state === 'blue') {
        // v2.44 · LÓGICA POR COLOR: la PALA (bola) sólo rompe los ROJOS; los
        // AZULES REBOTAN (metálico: «clink») — sólo el LÁSER los destruye
        // (explosión y quedan ROJOS, no desaparecen).
        this._brickClink(b);
      } else {
        this._breakBrick(b);
      }
      break;   // un ladrillo por subpaso
    }
    // v2.46 · LADRILLO NEGRO del tiempo extra: la bola también lo revienta
    // (misma reflexión especular que los ladrillos + recompensa de +1 min)
    if (this._timeBrick) {
      const tb = this._timeBrick;
      if (p.z - r <= tb.max.z && p.z + r >= tb.min.z &&
          p.x - r <= tb.max.x && p.x + r >= tb.min.x &&
          p.y - r <= tb.max.y && p.y + r >= tb.min.y) {
        const cx = THREE.MathUtils.clamp(p.x, tb.min.x, tb.max.x);
        const cy = THREE.MathUtils.clamp(p.y, tb.min.y, tb.max.y);
        const cz = THREE.MathUtils.clamp(p.z, tb.min.z, tb.max.z);
        let nx = p.x - cx, ny = p.y - cy, nz = p.z - cz;
        const d2 = nx * nx + ny * ny + nz * nz;
        if (d2 <= r2) {
          if (d2 > 1e-9) {
            const d = Math.sqrt(d2);
            nx /= d; ny /= d; nz /= d;
            p.x = cx + nx * (r + 0.003);
            p.y = cy + ny * (r + 0.003);
            p.z = cz + nz * (r + 0.003);
          } else {
            nz = 1;
            p.z = tb.max.z + r + 0.003;
          }
          const vn = v.x * nx + v.y * ny + v.z * nz;
          if (vn < 0) {
            v.x -= 2 * vn * nx;
            v.y -= 2 * vn * ny;
            v.z -= 2 * vn * nz;
            const vno = v.x * nx + v.y * ny + v.z * nz;
            v.x -= nx * vno * (1 - C.brickRest);
            v.y -= ny * vno * (1 - C.brickRest);
            v.z -= nz * vno * (1 - C.brickRest);
          }
          this._breakTimeBrick();
        }
      }
    }
    // v3.6.44 · LADRILLO BOMBA: la bola lo revienta y DETONA (mismo esquema
    // de reflexión que el ladrillo del tiempo — la destrucción la hace
    // _detonarBomba, que arrasa el radio 2×2 de filas y columnas).
    if (this._bombBrick) {
      const bb = this._bombBrick.slot;
      if (p.z - r <= bb.max.z && p.z + r >= bb.min.z &&
          p.x - r <= bb.max.x && p.x + r >= bb.min.x &&
          p.y - r <= bb.max.y && p.y + r >= bb.min.y) {
        const cx = THREE.MathUtils.clamp(p.x, bb.min.x, bb.max.x);
        const cy = THREE.MathUtils.clamp(p.y, bb.min.y, bb.max.y);
        const cz = THREE.MathUtils.clamp(p.z, bb.min.z, bb.max.z);
        let nx = p.x - cx, ny = p.y - cy, nz = p.z - cz;
        const d2 = nx * nx + ny * ny + nz * nz;
        if (d2 <= r2) {
          if (d2 > 1e-9) {
            const d = Math.sqrt(d2);
            nx /= d; ny /= d; nz /= d;
            p.x = cx + nx * (r + 0.003);
            p.y = cy + ny * (r + 0.003);
            p.z = cz + nz * (r + 0.003);
          } else {
            nz = 1;
            p.z = bb.max.z + r + 0.003;
          }
          const vn = v.x * nx + v.y * ny + v.z * nz;
          if (vn < 0) {
            v.x -= 2 * vn * nx;
            v.y -= 2 * vn * ny;
            v.z -= 2 * vn * nz;
            const vno = v.x * nx + v.y * ny + v.z * nz;
            v.x -= nx * vno * (1 - C.brickRest);
            v.y -= ny * vno * (1 - C.brickRest);
            v.z -= nz * vno * (1 - C.brickRest);
          }
          this._detonarBomba();
        }
      }
    }
  }

  /** Golpecito sonoro de las paredes del perímetro (v2.41, con anti-spam). */
  _wallTok(x) {
    if (this._tokCd > 0) return;
    this._tokCd = 0.07;
    const g = this.game;
    g.audio.playOsc(320, 210, 0.06, 'triangle', 0.1,
      THREE.MathUtils.clamp(x / 2, -1, 1));
  }

  /** v2.44 · «clink» metálico de la bola contra un ladrillo AZUL (no rompe). */
  _brickClink(b) {
    if (this._tokCd > 0) return;
    this._tokCd = 0.09;
    const g = this.game;
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(1250, 900, 0.05, 'square', 0.09, pan);
    this._flash(b.mesh.position);
  }

  /** v2.44 · LÁSER impacta en un ladrillo: aplica SU lógica.
   *  AZUL  -> destruido por el láser: EXPLOTA y queda ROJO (no desaparece).
   *  ROJO  -> inmune al láser (sólo la pala lo rompe): chispa y «tick». */
  laserHit(b) {
    if (!b || !b.alive) return false;
    if (b.state === 'elec') {            // v3.6.45: sólo la BOLA lo activa
      this._laserSpark(b);
      return false;
    }
    if (b.state === 'blue') {
      this._laserConvert(b);
      return true;
    }
    this._laserSpark(b);
    return false;
  }

  /** v2.44 · el láser CONVIERTE el azul en rojo: explosión + cambio de color. */
  _laserConvert(b) {
    const g = this.game;
    b.state = 'red';
    b.mesh.material = this.redMats[b.matIdx];
    this._flash(b.mesh.position);
    // ráfaga de escombros azules (visual: la explosión del láser)
    let spawned = 0;
    for (const d of this._debris) {
      if (d.life > 0) continue;
      d.life = 0.45 + Math.random() * 0.2;
      d.mesh.visible = true;
      d.mesh.material = this.blueMats[b.matIdx];
      d.mesh.position.copy(b.mesh.position);
      d.mesh.position.x += (Math.random() - 0.5) * 0.2;
      d.mesh.position.y += (Math.random() - 0.5) * 0.12;
      d.vel.set((Math.random() - 0.5) * 2.0, Math.random() * 1.4,
        0.8 + Math.random() * 1.4);
      if (++spawned >= 5) break;
    }
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playNoise(0.12, 900, 0.9, 0.16, pan);
    g.audio.playOsc(880, 220, 0.16, 'sawtooth', 0.14, pan);
    if (g.renderer.xr.isPresenting) g.haptic(g.ballHand, 0.35, 55);
    this._hudDirty = true;
  }

  /** v2.44 · chispa del láser sobre un ROJO (no hace nada: es inmune). */
  _laserSpark(b) {
    const g = this.game;
    this._flash(b.mesh.position);
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(1600, 1200, 0.04, 'square', 0.07, pan);
  }

  /** v2.44 · conversión temporal: UN ladrillo ROJO vivo pasa a AZUL.
   *  Sólo se eligen ROJOS (los azules ya lo están: nunca «negros»). */
  _convertRandomRed() {
    if (this.variant !== 2) return;
    const cands = this.bricks.filter((b) => b.alive && b.state === 'red');
    if (!cands.length) return;
    const b = cands[(Math.random() * cands.length) | 0];
    b.state = 'blue';
    b.mesh.material = this.blueMats[b.matIdx];
    this._flash(b.mesh.position);
    const g = this.game;
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(520, 880, 0.14, 'sine', 0.09, pan);
    this._hudDirty = true;
  }

  /* ---------------------------------------------------------------------
   * v2.46 · LADRILLO NEGRO del TIEMPO EXTRA (sólo ARKANOID 2): cuando el
   * contador baja de 30 s (con sonido de APREMIO) aparece en un hueco de
   * ladrillo ya destruido con un reloj superpuesto, se queda 2 s y SALTA a
   * otro hueco libre distinto. La bola o el láser lo revientan: escombros
   * NEGROS, +1 MINUTO de tiempo y el cartel extra.png flotando. UNO solo
   * por prueba: cogido éste, nunca vuelve a aparecer.
   * ------------------------------------------------------------------- */
  _timeUpdate(dt) {
    if (this.variant !== 2) return;
    if (!this._timeUsed && this.time <= 30 && !this._timeBrick) {
      this._timeSpawn();
    }
    if (!this._timeBrick) return;
    this._timeBrick.t += dt;
    if (this._timeBrick.t >= 2) this._timeJump();
  }

  _freeSlots() {
    return this.bricks.filter((b) => !b.alive);
  }

  _timeSpawn() {
    // v2.46: blindaje — si el extra ya se cogió (o ya está en escena),
    // NUNCA vuelve a aparecer aunque se llame directamente
    if (this._timeUsed || this._timeBrick) return;
    const free = this._freeSlots();
    if (!free.length) return;          // sin huecos destruidos: no aparece
    this._timePlace(free[(Math.random() * free.length) | 0]);
    const g = this.game;
    const pan = THREE.MathUtils.clamp(this.timeMesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(980, 620, 0.12, 'square', 0.11, pan);
  }

  _timePlace(b) {
    this._timeBrick = { slot: b, t: 0, min: b.min, max: b.max };
    this.timeMesh.visible = true;
    this.timeMesh.scale.setScalar(1);
    this.timeMesh.rotation.set(0, 0, 0);
    this.timeMesh.position.copy(b.home);
    this.timeClock.visible = true;     // reloj ANCLADO al ladrillo especial
    this.timeClock.position.copy(b.home);
    this.timeClock.position.z += this.C.depth / 2 + 0.003;
  }

  _timeJump() {
    const cur = this._timeBrick.slot;
    const free = this._freeSlots().filter((b) => b !== cur);
    if (!free.length) { this._timeBrick.t = 0; return; }  // sólo un hueco
    this._flash(cur.home);             // destello en el hueco que abandona
    this._timePlace(free[(Math.random() * free.length) | 0]);
    const g = this.game;
    const pan = THREE.MathUtils.clamp(this.timeMesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(760, 1150, 0.07, 'sine', 0.08, pan);
  }

  /** La bola o el láser revientan el ladrillo negro: escombros NEGROS,
   *  +1 MINUTO y el plano extra.png "+1 MIN" que sube y se desvanece. */
  _breakTimeBrick() {
    if (!this._timeBrick) return;
    const g = this.game;
    const pos = this.timeMesh.position.clone();
    this._timeBrick = null;
    this._timeUsed = true;             // sólo UN tiempo extra por prueba
    this.timeMesh.visible = false;
    this.timeClock.visible = false;
    this.time += 60;                   // +1 MINUTO al contador
    this._hudDirty = true;
    let spawned = 0;
    for (const d of this._debris) {
      if (d.life > 0) continue;
      d.life = 0.55 + Math.random() * 0.25;
      d.mesh.visible = true;
      d.mesh.material = this.blackMat; // trocitos NEGROS
      d.mesh.position.copy(pos);
      d.mesh.position.x += (Math.random() - 0.5) * 0.2;
      d.mesh.position.y += (Math.random() - 0.5) * 0.12;
      d.vel.set((Math.random() - 0.5) * 2.2, Math.random() * 1.5,
        0.7 + Math.random() * 1.5);
      if (++spawned >= 6) break;
    }
    this._flash(pos);
    // "+1 MIN" un poco DELANTE del muro: sube despacio y se apaga en 2 s
    this._extraFx = { pos, t: 0 };
    this.extraPlane.visible = true;
    this.extraPlane.position.copy(pos);
    this.extraPlane.position.z += 0.09;
    this.extraPlane.material.opacity = 1;
    const pan = THREE.MathUtils.clamp(pos.x / 2.5, -1, 1);
    g.audio.playNoise(0.1, 1800, 1.0, 0.12, pan);
    g.audio.playOsc(520, 1040, 0.16, 'sine', 0.16, pan);
    window.setTimeout(() => g.audio.playOsc(780, 1560, 0.22, 'sine', 0.16, pan), 140);
    this._msg = T('ark_extra_min');
    this._msgT = 2.0;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 70);
  }

  /* ---------------------------------------------------------------------
   * v3.6.44 (ronda 52) · LADRILLO BOMBA del ARKANOID 2 (etapa 4 del
   * campeonato de La Locura — petición literal del dueño):
   * «aleatoriamente y al menos 1 vez por partida aparezca un bloque de
   * ladrillo negro sustituyendo a uno azul con un dibujo de una bomba,
   * permanece 4 segundos y salta a otro bloque azul si está presente y
   * sino desaparece hasta que aparezca otro azul, una vez consumido ya no
   * aparecen más durante la partida, se reinicia con cada partida» y «si
   * se destruye, con el disparo o con la pelota detone estrepitosamente
   * todos los bloques que están al menos hasta un rango de 2 filas y
   * columnas de donde se encuentra». RESULTADO: la etapa Arkanoid tiene
   * DOS ayudas aseguradas — el reloj (+1 min) y la bomba (el destrozo).
   * ------------------------------------------------------------------- */
  _bombUpdate(dt) {
    if (this.variant !== 2) return;
    if (this._eFase > 0) return;    // v3.6.45: el final ELÉCTRICO manda — bomba fuera
    if (this._bombUsed) return;             // consumida: nunca más en la partida
    this._stageT += dt;          // reloj de la etapa (intervalos de 15 s)
    if (this._bombBrick) {
      this._bombT += dt;
      if (this._bombT >= 4) this._bombJump();   // 4 s en el ladrillo → salta
      return;
    }
    const azules = this.bricks.filter((b) => b.alive && b.state === 'blue');
    // v3.6.45 (ronda 53, petición del dueño): la bomba sale de manera
    // ALEATORIA pero por INTERVALOS DE 15 SEGUNDOS — «si tiene ladrillos
    // disponibles donde aparecer». La 1.ª aparición cae DENTRO del primer
    // intervalo (2-12 s, aleatoria); tras cada aparición se programa la
    // siguiente a +15 s, así que tras una desaparición (sin azules) vuelve
    // en su intervalo, nunca antes.
    if (this._bombWait) {
      // desaparecida por falta de azules: espera a SU intervalo y a un azul
      if (azules.length && this._stageT >= this._bombNext) {
        this._bombSpawn(azules);
      }
      return;
    }
    if (azules.length && this._stageT >= this._bombNext) {
      this._bombSpawn(azules);
    }
  }

  _bombSpawn(azules) {
    if (!azules || !azules.length) azules =
      this.bricks.filter((b) => b.alive && b.state === 'blue');
    if (!azules.length) { this._bombWait = true; return; }
    this._bombWait = false;
    const b = azules[(Math.random() * azules.length) | 0];
    this._bombPlace(b);
    // v3.6.45: la SIGUIENTE aparición se programa a +15 s (intervalos)
    this._bombNext = this._stageT + (this.C.bombaCada || 15);
    const g = this.game;
    const pan = THREE.MathUtils.clamp(this.bombMesh.position.x / 2.5, -1, 1);
    // aparición: «plombeo» grave + tic metálico (amenaza que llega)
    g.audio.playOsc(180, 96, 0.2, 'triangle', 0.2, pan);
    g.audio.playNoise(0.08, 2400, 1.4, 0.1, pan);
  }

  _bombPlace(b) {
    this._bombBrick = { slot: b, t: 0 };
    this._bombT = 0;
    b.mesh.visible = false;              // el azul se OCULTA (sigue vivo)
    this.bombMesh.visible = true;
    this.bombMesh.scale.setScalar(1);
    this.bombMesh.rotation.set(0, 0, 0);
    this.bombMesh.position.copy(b.home);
    this.bombIcon.visible = true;        // icono bomba DELANTE del ladrillo
    this.bombIcon.position.copy(b.home);
    this.bombIcon.position.z += this.C.depth / 2 + 0.003;
  }

  _bombJump() {
    const cur = this._bombBrick.slot;
    const otros = this.bricks.filter((b) => b.alive && b.state === 'blue' &&
      b !== cur);
    if (!otros.length) {
      // sin azules vivos: DESAPARECE (el azul actual vuelve) y espera a
      // que aparezca otro azul (_convertRandomRed crea azules nuevos)
      cur.mesh.visible = true;
      this.bombMesh.visible = false;
      this.bombIcon.visible = false;
      this._bombBrick = null;
      this._bombWait = true;
      return;
    }
    this._flash(cur.home);               // destello en el ladrillo que abandona
    cur.mesh.visible = true;             // el azul original REAPARECE
    this._bombPlace(otros[(Math.random() * otros.length) | 0]);
    const g = this.game;
    const pan = THREE.MathUtils.clamp(this.bombMesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(340, 620, 0.09, 'sine', 0.1, pan);
  }

  /** La bola o el láser revientan la BOMBA: DETONACIÓN ESTREPITOSA —
   *  arrasa TODOS los ladrillos vivos en radio de 2 filas × 2 columnas
   *  (rojos Y azules — la bomba no distingue), escombros negros, flash
   *  doble, BOOM grave con sub-tono y sacudida háptica fuerte. */
  _detonarBomba() {
    if (!this._bombBrick) return;
    const g = this.game;
    const slot = this._bombBrick.slot;
    const pos = slot.home.clone();
    const C = this.C;
    const idx = this.bricks.indexOf(slot);
    const rC = (idx >= 0 && C.cols) ? Math.floor(idx / C.cols) : -1;
    const cC = (idx >= 0 && C.cols) ? idx % C.cols : -1;
    this._bombBrick = null;              // consumida: NUNCA más en la partida
    this._bombUsed = true;
    this.bombMesh.visible = false;
    this.bombIcon.visible = false;
    slot.mesh.visible = true;            // el azul vuelve para romperse
    // DETONACIÓN: radio 2 filas × 2 columnas alrededor del ladrillo bomba
    if (rC >= 0) {
      for (let dr = -2; dr <= 2; dr++) {
        for (let dc = -2; dc <= 2; dc++) {
          const rr = rC + dr, cc = cC + dc;
          if (rr < 0 || rr >= C.rows || cc < 0 || cc >= C.cols) continue;
          const b2 = this.bricks[rr * C.cols + cc];
          if (b2 && b2.alive) this._breakBrick(b2);
        }
      }
    }
    // escombros NEGROS de la propia bomba (8 trozos)
    let spawned = 0;
    for (const d of this._debris) {
      if (d.life > 0) continue;
      d.life = 0.6 + Math.random() * 0.3;
      d.mesh.visible = true;
      d.mesh.material = this.blackMat;
      d.mesh.position.copy(pos);
      d.mesh.position.x += (Math.random() - 0.5) * 0.2;
      d.mesh.position.y += (Math.random() - 0.5) * 0.12;
      d.vel.set((Math.random() - 0.5) * 3.2, Math.random() * 2.2,
        1.0 + Math.random() * 2.0);
      if (++spawned >= 8) break;
    }
    this._flash(pos);                    // doble flash de la detonación
    this._flash(pos.clone().add(new THREE.Vector3(
      (Math.random() - 0.5) * 0.3, (Math.random() - 0.5) * 0.2, 0.02)));
    // BOOM: trueno grave + caída al sub-grave (el destrozo SUENA enorme)
    const pan = THREE.MathUtils.clamp(pos.x / 2.5, -1, 1);
    g.audio.playNoise(0.32, 180, 0.7, 0.4, pan);
    g.audio.playOsc(320, 55, 0.4, 'sawtooth', 0.32, pan);
    g.audio.playOsc(110, 42, 0.5, 'sine', 0.3, pan);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.95, 220);
    this._msg = T('ark_bomba_boom');
    this._msgT = 2.0;
    this._hudDirty = true;
  }

  /* ---------------------------------------------------------------------
   * v3.6.45 (ronda 53) · EL LADRILLO ELÉCTRICO del ARKANOID 2 (etapa 4 del
   * campeonato de La Locura — petición literal del dueño): «En los últimos
   * 30 segundos uno de los ladrillos azules (aleatorio) se convierte en
   * eléctrico con pequeños rayos que salen de él (solo es destructible con
   * la bola). Si se le consigue dar con la pelota, atrae hacia sí al resto
   * de los ladrillos que queden en la pared distribuyéndolos en las celdas
   * pegadas a su alrededor cubriendo todas las casillas más próximas
   * posibles y todos cogen el mismo efecto de rayitos pegándolos a su
   * alrededor; en ese momento y hasta el final del tiempo cualquier
   * impacto en cualquiera de los ladrillos en el nuevo estado de eléctrico
   * desencadena una reacción en cadena destruyéndolos de forma ramificada
   * desde el que recibe el impacto hasta los siguientes hasta destruir
   * todos en cadena, finalizando de forma exitosa la misión. Y cuando sella
   * un ladrillo y pasa a eléctrico que emita un sonido de chisporroteo de
   * electricidad». FASES: 0 = nada · 1 = sembrado (espera la bola) ·
   * 2 = pared electrificada y cadena armada (el gran final).
   * ------------------------------------------------------------------- */

  /** Siembra: UN azul vivo al azar pasa a ELÉCTRICO (rayitos + zap +
   *  chisporroteo). Si no hay azules aún, reintenta en el frame siguiente
   *  (la conversión temporal genera azules nuevos cada 7 s). */
  _eSembrar() {
    if (this._eFase !== 0 || this.variant !== 2) return;
    const cands = this.bricks.filter((b) => b.alive && b.state === 'blue' &&
      !(this._bombBrick && b === this._bombBrick.slot));
    if (!cands.length) return;            // sin azules: reintenta
    const g = this.game;
    const b = cands[(Math.random() * cands.length) | 0];
    this._eFase = 1;
    this._eSeed = b;
    b.state = 'elec';
    b.mesh.material = this.eBrickMat;
    if (this.eIcon) {
      this.eIcon.visible = true;
      this.eIcon.position.copy(b.home);
      this.eIcon.position.z += this.C.depth / 2 + 0.003;
    }
    this._flash(b.mesh.position);
    // ZAP de sellado: chirrido eléctrico + chispa aguda — «cuando sella un
    // ladrillo y pasa a eléctrico que emita un sonido» (petición literal)
    const pan = THREE.MathUtils.clamp(b.home.x / 2.5, -1, 1);
    g.audio.playOsc(2400, 700, 0.16, 'sawtooth', 0.2, pan);
    g.audio.playOsc(3400, 2600, 0.08, 'square', 0.1, pan);
    g.audio.playNoise(0.12, 3200, 1.6, 0.16, pan);
    this._msg = T('ark_elec_on');
    this._msgT = 2.6;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.45, 90);
    this._hudDirty = true;
  }

  /** ATRACCIÓN (fase 1 → 2): la bola golpea la semilla — el resto de los
   *  ladrillos VIVOS es atraído y se reparte en las celdas contiguas por
   *  ANILLOS desde la semilla (las casillas más próximas primero, huecos
   *  de ladrillos destruidos incluidos). TODOS quedan eléctricos: la
   *  reacción en cadena queda armada hasta el final del tiempo. */
  _eAtraer(seed) {
    if (this._eFase !== 1 || !seed || !seed.alive) return;
    const g = this.game;
    const C = this.C;
    const cols = C.cols, rows = C.rows;
    const iS = this.bricks.indexOf(seed);
    const rS = Math.floor(iS / cols), cS = iS % cols;
    const W = cols * C.bw + (cols - 1) * C.gap;
    // celdas destino por ANILLOS (Chebyshev) y, dentro de cada anillo, por
    // distancia euclídea a la semilla — «cubriendo todas las casillas más
    // próximas posibles» (los anillos cubren todo el muro: siempre caben)
    const dests = [];
    for (let ring = 1; ring <= Math.max(rows, cols); ring++) {
      const celdas = [];
      for (let r = rS - ring; r <= rS + ring; r++) {
        for (let c = cS - ring; c <= cS + ring; c++) {
          if (Math.max(Math.abs(r - rS), Math.abs(c - cS)) !== ring) continue;
          if (r < 0 || r >= rows || c < 0 || c >= cols) continue;
          const i2 = r * cols + c;
          if (i2 === iS) continue;
          celdas.push({ i2, d: (r - rS) * (r - rS) + (c - cS) * (c - cS) });
        }
      }
      celdas.sort((a, b2) => a.d - b2.d);
      for (const cd of celdas) dests.push(cd.i2);
    }
    const vivos = this.bricks.filter((b) => b.alive && b !== seed);
    const usadas = new Set([iS]);
    let k = 0;
    for (const b of vivos) {
      while (k < dests.length && usadas.has(dests[k])) k++;
      if (k >= dests.length) break;
      const dst = dests[k++];
      usadas.add(dst);
      const r2 = Math.floor(dst / cols), c2 = dst % cols;
      const x = -W / 2 + C.bw / 2 + c2 * (C.bw + C.gap);
      const y = C.baseY + C.bh / 2 + r2 * (C.bh + C.gap);
      b.state = 'elec';
      b.mesh.material = this.eBrickMat;
      // AABB nuevo YA (colisión = disposición final); la malla viaja con
      // un tween corto de 0,35 s (_eMove, procesado en _anims)
      b.min.set(x - C.bw / 2, y - C.bh / 2, C.z - C.depth / 2);
      b.max.set(x + C.bw / 2, y + C.bh / 2, C.z + C.depth / 2);
      this._eMove.push({ b, fx: b.mesh.position.x, fy: b.mesh.position.y,
        tx: x, ty: y, t: 0 });
    }
    this._eFase = 2;
    this._eChispT = 0.05;                 // el chisporroteo sube YA
    this._flash(seed.mesh.position);
    for (let i = 0; i < 5; i++) {
      const b2 = vivos.length
        ? vivos[(Math.random() * vivos.length) | 0] : null;
      if (b2) this._flash(b2.mesh.position);
    }
    // gran ZAP de electrificación de la pared
    const pan = THREE.MathUtils.clamp(seed.home.x / 2.5, -1, 1);
    g.audio.playOsc(300, 1900, 0.4, 'sawtooth', 0.24, pan);
    g.audio.playNoise(0.3, 2800, 1.4, 0.22, pan);
    g.audio.playOsc(1900, 400, 0.3, 'square', 0.12, pan);
    this._msg = T('ark_elec_aran');
    this._msgT = 3.0;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 160);
    this._hudDirty = true;
  }

  /** Celda ACTUAL de un ladrillo, derivada de su AABB — tras la atracción
   *  los ladrillos viven en celdas NUEVAS (el índice del array ya no vale). */
  _eCeldaDe(b) {
    const C = this.C;
    const W = C.cols * C.bw + (C.cols - 1) * C.gap;
    const cx = (b.min.x + b.max.x) / 2;
    const cy = (b.min.y + b.max.y) / 2;
    const c = Math.round((cx + W / 2 - C.bw / 2) / (C.bw + C.gap));
    const r = Math.round((cy - C.baseY - C.bh / 2) / (C.bh + C.gap));
    return { r: Math.max(0, Math.min(C.rows - 1, r)),
      c: Math.max(0, Math.min(C.cols - 1, c)) };
  }

  /** REACCIÓN EN CADENA (fase 2): BFS ramificado desde el ladrillo
   *  impactado — cada onda (0,12 s) revienta los eléctricos vecinos en
   *  todas direcciones hasta arrasar TODOS los de la pared: la cola se
   *  procesa en _eCadenaStep y al vaciarla con el muro muerto la misión
   *  termina de forma EXITOSA (_finish(true)). La propagación va por la
   *  celda ACTUAL de cada ladrillo (AABB — tras la atracción el índice
   *  del array ya no coincide con su sitio en el muro). */
  _eCadenaDesde(b0) {
    if (this._eFase !== 2 || !b0 || !b0.alive || b0.state !== 'elec') return;
    if (this._eCadena.length) return;     // la cadena ya corre: no re-dispara
    const cols = this.C.cols;
    // mapa celda ACTUAL → ladrillo (sólo eléctricos vivos)
    const mapa = new Map();
    for (const b of this.bricks) {
      if (!b.alive || b.state !== 'elec') continue;
      const cd = this._eCeldaDe(b);
      mapa.set(cd.r * cols + cd.c, b);
    }
    if (!mapa.size) return;
    const c0 = this._eCeldaDe(b0);
    const i0 = c0.r * cols + c0.c;
    const enCola = new Set([i0]);
    let frente = [i0];
    this._eCadena.push({ b: mapa.get(i0) || b0, t: 0 });
    let t = 0;
    while (frente.length) {
      t += 0.12;
      const sig = [];
      for (const i of frente) {
        const r0 = Math.floor(i / cols), c0i = i % cols;
        for (let dr = -1; dr <= 1; dr++) {
          for (let dc = -1; dc <= 1; dc++) {
            if (!dr && !dc) continue;
            const rr = r0 + dr, cc = c0i + dc;
            if (rr < 0 || rr >= this.C.rows || cc < 0 || cc >= cols) continue;
            const i2 = rr * cols + cc;
            if (enCola.has(i2) || !mapa.has(i2)) continue;
            enCola.add(i2);
            this._eCadena.push({ b: mapa.get(i2), t });
            sig.push(i2);
          }
        }
      }
      frente = sig;
    }
    const g = this.game;
    const pan = THREE.MathUtils.clamp(b0.mesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(2600, 240, 0.22, 'sawtooth', 0.26, pan);
    g.audio.playNoise(0.18, 3000, 1.5, 0.2, pan);
  }

  /** Paso de la cadena: revienta la cola POR ONDAS (zap eléctrico por
   *  ladrillo + escombros del _breakBrick normal). Al vaciarse la cola con
   *  la pared muerta → VICTORIA (la misión se finaliza con éxito). */
  _eCadenaStep(dt) {
    if (!this._eCadena.length) return;
    const g = this.game;
    for (const c of this._eCadena) c.t -= dt;
    while (this._eCadena.length && this._eCadena[0].t <= 0) {
      const c = this._eCadena.shift();
      if (!c.b.alive || c.b.state !== 'elec') continue;
      // mata su tween si aún viajaba (la malla se queda donde esté)
      this._eMove = this._eMove.filter((m) => m.b !== c.b);
      this._breakBrick(c.b);
      const pan = THREE.MathUtils.clamp(c.b.mesh.position.x / 2.5, -1, 1);
      g.audio.playOsc(2100, 320, 0.07, 'sawtooth', 0.13, pan);
      g.audio.playNoise(0.05, 3000, 1.3, 0.1, pan);
    }
    if (!this._eCadena.length &&
        (this.phase === 'play' || this.phase === 'serve') &&
        this.bricksLeft <= 0) {
      this._finish(true);                 // misión finalizada con ÉXITO
    }
  }

  /** Objetivos vivos de los rayos (la semilla en fase 1 · todos en fase 2). */
  _eBoltTargets() {
    return this.bricks.filter((b) => b.alive && b.state === 'elec');
  }

  /** RAYITOS: cada 0,07 s los 14 rayos del pool se REGENERAN sobre los
   *  ladrillos eléctricos — líneas dentadas aditivas que salen del
   *  ladrillo hacia fuera («pequeños rayos que salen de él»). */
  _eBoltUpdate(dt) {
    if (!this.eBolts || !this.eBolts.length) return;
    const elec = this._eBoltTargets();
    if (!elec.length) {
      for (const ln of this.eBolts) if (ln.visible) ln.visible = false;
      return;
    }
    this._eBoltT -= dt;
    if (this._eBoltT > 0) return;
    this._eBoltT = 0.07;
    const C = this.C;
    const zf = C.z + C.depth / 2 + 0.006;
    for (let i = 0; i < this.eBolts.length; i++) {
      const ln = this.eBolts[i];
      const b = elec[(Math.random() * elec.length) | 0];
      const px = b.mesh.position.x + (Math.random() - 0.5) * C.bw * 0.7;
      const py = b.mesh.position.y + (Math.random() - 0.5) * C.bh * 0.7;
      const pos = ln.geometry.attributes.position;
      let x = px, y = py, z = zf;
      pos.setXYZ(0, x, y, z);
      const L = 0.05 + Math.random() * 0.09;
      const ang = Math.random() * Math.PI * 2;
      for (let s = 1; s < 4; s++) {
        x += Math.cos(ang) * (L / 3) + (Math.random() - 0.5) * 0.035;
        y += Math.sin(ang) * (L / 3) + (Math.random() - 0.5) * 0.035;
        z += 0.008 + Math.random() * 0.02;
        pos.setXYZ(s, x, y, z);
      }
      pos.needsUpdate = true;
      ln.visible = true;
    }
  }

  /** CHISPORROTEO de electricidad: ráfagas cortas aleatorias mientras hay
   *  ladrillos eléctricos (petición literal del dueño) — crepita sin parar
   *  hasta que la cadena arrasa la pared. */
  _eChispUpdate(dt) {
    const g = this.game;
    this._eChispT -= dt;
    if (this._eChispT > 0) return;
    this._eChispT = 0.12 + Math.random() * 0.26;
    const elec = this._eBoltTargets();
    if (!elec.length) return;
    const b = elec[(Math.random() * elec.length) | 0];
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playNoise(0.03 + Math.random() * 0.04,
      2600 + Math.random() * 2600, 1.2 + Math.random() * 0.8,
      0.05 + Math.random() * 0.08, pan);
    if (Math.random() < 0.12) {
      g.audio.playOsc(2200 + Math.random() * 1400,
        800 + Math.random() * 900, 0.05, 'square', 0.05, pan);
    }
  }

  /** Dispatch del ELÉCTRICO (rayos · chisporroteo · cadena) — corre en
   *  play y serve (el crepitar no se apaga entre saques). */
  _eUpdate(dt) {
    if (!this._eFase || this.variant !== 2) return;
    this._eBoltUpdate(dt);
    this._eChispUpdate(dt);
    this._eCadenaStep(dt);
  }

  /* ---------------------------------------------------------------------
   * v2.44 · ABANICAR — anti-atasco divertido: si mueves la pala RÁPIDO de
   * derecha a izquierda (y viceversa) se genera una CORRIENTE DE AIRE que
   * empuja la bola hacia el muro como si la hubieras golpeado. Sirve para
   * alcanzar bolas botando lejos de la mesa (zona inaccesible).
   * · Detección: 2+ inversiones laterales fuertes (|vx| > 1,2 m/s) en 0,55 s.
   * · Efecto: aceleración sostenida hacia el muro + EMPUJÓN final tipo golpe.
   * · Feedback: partículas de viento pala->bola + sonido de soplido.
   * ------------------------------------------------------------------- */
  _fanUpdate(dt) {
    const g = this.game;
    this._fanCd = Math.max(0, this._fanCd - dt);
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    const ball = g.ball;
    if (!ball || !ball.pos) return;

    // 1) muestrear la velocidad lateral de la pala (ventana de 0,55 s)
    const nowT = performance.now() / 1000;
    if (ps && ps.active && ps.vel) {
      this._fanSamp.push({ t: nowT, vx: ps.vel.x });
      while (this._fanSamp.length && nowT - this._fanSamp[0].t > 0.55) {
        this._fanSamp.shift();
      }
      if (this._fanCd <= 0 && this._fanT <= 0) {
        // contar INVERSIONES de dirección con impulso suficiente
        let flips = 0;
        let lastSign = 0;
        for (const s of this._fanSamp) {
          if (Math.abs(s.vx) < 1.2) continue;
          const sg = Math.sign(s.vx);
          if (lastSign && sg !== lastSign) flips++;
          lastSign = sg;
        }
        if (flips >= 2) {
          // ¡ABANICO! corriente de aire activa durante 1,2 s
          this._fanT = 1.2;
          this._fanCd = 3.2;
          this._fanKick = 0;
          this._fanBlowT = 0;
          if (!this._fanHintDone) {
            this._fanHintDone = true;
            this._msg = T('fan_hint');
            this._msgT = 2.2;
            this._hudDirty = true;
          }
        }
      }
    }

    // 2) mientras sopla el viento: acelerar la bola hacia el muro
    if (this._fanT > 0) {
      this._fanT -= dt;
      // sólo si la bola está en la zona alejada (no al alcance de la pala)
      const p = ball.pos;
      const padPos = (ps && ps.active && ps.pos) ? ps.pos : null;
      const far = !padPos || p.distanceTo(padPos) > 0.45;
      if (far && p.z < this.C.sideZ0 + 0.2) {
        this._tmpA.set(
          THREE.MathUtils.clamp(p.x, -this.C.sideX * 0.6, this.C.sideX * 0.6),
          DIMS.tableTopY + 0.35,
          this.C.sideZ1 + 0.4,
        ).sub(p);
        if (this._tmpA.lengthSq() > 1e-6) {
          this._tmpA.normalize();
          ball.vel.addScaledVector(this._tmpA, 2.6 * dt);   // corriente continua
          if (p.y < DIMS.tableTopY + 0.15) ball.vel.y += 1.4 * dt;
          // EMPUJÓN final tipo golpe (acumulado ~0,8 s de viento)
          this._fanKick += dt;
          if (this._fanKick >= 0.8) {
            this._fanT = 0;
            const sp = Math.max(3.4, ball.vel.length() * 1.15);
            ball.vel.copy(this._tmpA).multiplyScalar(sp);
            if (ball.vel.y < 1.4) ball.vel.y = 1.4;
            g.audio.playNoise(0.28, 700, 0.7, 0.2, 0);
            g.audio.playOsc(300, 140, 0.2, 'triangle', 0.1, 0);
          }
        }
      }
      // soplido en bucle corto mientras dura la corriente
      this._fanBlowT -= dt;
      if (this._fanBlowT <= 0) {
        this._fanBlowT = 0.16;
        g.audio.playNoise(0.15, 520, 0.6, 0.07, 0);
      }
      // 3) partículas de viento: nacen en la pala y vuelan hacia la bola
      if (ps && ps.active && ps.pos) {
        let spawned = 0;
        for (const w of this._wind) {
          if (w.life > 0) continue;
          w.life = 0.4 + Math.random() * 0.18;
          w.mesh.visible = true;
          w.mesh.position.copy(ps.pos);
          w.mesh.position.y += 0.05;
          this._tmpB.copy(ball.pos).sub(w.mesh.position);
          if (this._tmpB.lengthSq() > 1e-8) this._tmpB.normalize();
          else this._tmpB.set(0, 1, 0);   // v2.120: sin NaN si la bola está encima
          w.vel.copy(this._tmpB).multiplyScalar(2.4 + Math.random() * 1.4);
          w.vel.x += (Math.random() - 0.5) * 0.7;
          w.vel.y += (Math.random() - 0.5) * 0.5;
          w.vel.z += (Math.random() - 0.5) * 0.7;
          if (++spawned >= 2) break;
        }
      }
    }

    // 4) animación de las partículas (siempre)
    for (const w of this._wind) {
      if (w.life <= 0) continue;
      w.life -= dt;
      if (w.life <= 0) { w.mesh.visible = false; continue; }
      w.mesh.position.addScaledVector(w.vel, dt);
      const k = Math.min(1, w.life / 0.4);
      w.mesh.material.opacity = 0.75 * k;
      w.mesh.scale.setScalar(0.7 + (1 - k) * 1.6);
      w.mesh.quaternion.copy(g.camera ? g.camera.quaternion : new THREE.Quaternion());
    }
  }

  /** Flash de destrucción (v2.41): estallido aditivo en el ladrillo roto. */
  _flash(pos) {
    for (const f of this._flashes) {
      if (f.t > 0) continue;
      f.t = 0.0001;
      f.mesh.visible = true;
      f.mesh.position.copy(pos);
      f.mesh.scale.setScalar(0.5);
      return;
    }
  }

  _breakBrick(b) {
    const g = this.game;
    b.alive = false;
    this.bricksLeft--;
    this._dying.push({ mesh: b.mesh, t: 0, spin: (Math.random() - 0.5) * 3 });
    this._flash(b.mesh.position);            // v2.41: estallido de luz
    // escombros
    let spawned = 0;
    for (const d of this._debris) {
      if (d.life > 0) continue;
      d.life = 0.55 + Math.random() * 0.25;
      d.mesh.visible = true;
      // v2.45 · ESCOMBROS DEL COLOR DEL LADRILLO: rojos → trocitos ROJOS
      // (los azules ya sueltan trocitos AZULES en _laserConvert)
      d.mesh.material = this.redMats[b.matIdx];
      d.mesh.position.copy(b.mesh.position);
      d.mesh.position.x += (Math.random() - 0.5) * 0.3;
      d.mesh.position.y += (Math.random() - 0.5) * 0.15;
      d.vel.set((Math.random() - 0.5) * 2.4, Math.random() * 1.6,
        0.6 + Math.random() * 1.6);
      if (++spawned >= 6) break;
    }
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playNoise(0.07, 1500, 1.2, 0.15, pan);
    g.audio.playOsc(620 + b.mesh.position.y * 120, 260, 0.09, 'square', 0.13, pan);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 50);
    this._hudDirty = true;
  }

  _lifeLost() {
    const g = this.game;
    this.lives--;
    this._hudDirty = true;
    if (this.lives > 0) {
      this._msg = T('ark_life', { n: this.lives });
      this._msgT = 1.6;
      g.audio.playOsc(392, 240, 0.24, 'triangle', 0.15, 0);
      // v2.41: SAQUE de partida normal (bola en la mano libre)
      this._crossed = false;
      this._enterServe();
      this._msg = T('ark_life', { n: this.lives });   // sobre el hint
      this._msgT = 1.6;
    } else {
      this._finish(false, 'lives');
    }
  }

  _finish(win, reason) {
    if (this.phase === 'result') return;   // v3.6.45: nunca un doble final
    const g = this.game;
    const a = this.ctrl;
    this._lastWin = !!win;   // v3.6.12 (ronda 15): _afterResult distingue
    // v3.6.14 (ronda 17 · EMBUDO VIVO): champ_rank de la PRUEBA. Magia lo
    // emite desde la ronda 11 pero La Locura no — champRank llevaba CERO
    // datos pese a los intentos reales (3 sesiones VR y 45 min sin un solo
    // reporte). El agregador del worker sólo lee champ/win/score/stars (la
    // prueba no puntúa ni da estrellas → 0, igual que el orbe de Magia);
    // bricks/lives/left viajan crudos en el JSON para análisis futuro.
    try {
      const tot = this.C.cols * this.C.rows;
      __PP_TELE.ev('champ_rank', {
        champ: 'locura',
        win: !!win,
        score: 0, stars: 0,
        bricks: Math.max(0, Math.min(tot, tot - this.bricksLeft)),
        lives: Math.max(0, Math.min(this.C.lives, this.lives)),
        left: Math.max(0, Math.round(this.time * 10) / 10),
      });
    } catch { /* el reporte nunca rompe */ }
    this.phase = 'result';
    this.phaseT = win ? 4.4 : 3.6;
    if (win) {
      // v2.44: el CAMINO avanza — ARKANOID 1 (etapa 1) entrega el superpoder
      // PISTOLA y pasa a CLOWN Nv. 2; ARKANOID 2 (etapa 3) pasa a CLOWN Nv. 3
      if (this.variant === 1) {
        const firstGun = !(a.powers || []).includes('pistola');
        if (firstGun) a.powers.push('pistola');
        try { localStorage.setItem('pp_arcade_powers', JSON.stringify(a.powers)); } catch { /* */ }
        if (a._replay) {   // v2.96: REJUGADA — el camino se queda como estaba
          this._banner = { title: T('ark_win'), sub: T('replay_done'), col: '#7fb069' };
          g.audio.announce(T('replay_done'), true);
          a.stage = a._replay.stage; a.round = a._replay.round;
          try { localStorage.setItem('pp_arcade_stage', String(a.stage)); } catch { /* */ }
          a._replay = null;
        } else {
          a._setStage(2);
          this._banner = {
            title: T('ark_win'),
            sub: firstGun ? T('ark_gun_get') : T('clown2_up'), col: '#7fb069',
          };
          g.audio.announce(firstGun ? T('ark_gun_get') : T('clown2_up'), true);
        }
      } else if (a._replay) {
        this._banner = { title: T('ark2_win'), sub: T('replay_done'), col: '#7fb069' };
        g.audio.announce(T('replay_done'), true);
        a.stage = a._replay.stage; a.round = a._replay.round;
        try { localStorage.setItem('pp_arcade_stage', String(a.stage)); } catch { /* */ }
        a._replay = null;
      } else {
        a._setStage(4);
        this._banner = { title: T('ark2_win'), sub: T('ark2_next'), col: '#7fb069' };
        g.audio.announce(T('ark2_next'), true);
      }
      g.confettiBurst = 3;
      g.audio.fanfare(true);
      if (g.renderer.xr.isPresenting) {
        g.haptic(g.paddleHand, 0.8, 140);
        window.setTimeout(() => g.haptic(g.paddleHand, 0.5, 130), 220);
      }
    } else {
      // v3.6.12 (ronda 15 · SEGUNDA OPORTUNIDAD): perder la prueba YA NO
      // retrocede el camino — el dato mandó: en la 3.6.10 el dueño ganó el
      // CLOWN Nv. 1 (stage 0→1), perdió el ARKANOID y el retroceso a 0 lo
      // hizo abandonar 16 s después; 3 sesiones VR (20 min) y 0 campeonatos
      // completos. Se aplica la MISMA política v2.44 de los DUELOS («perder
      // REPITE el paso actual»): la etapa no cambia y _afterResult() relanza
      // esta misma prueba. La rejugada (v2.96) restaura su paso de origen.
      if (a._replay) {
        a.stage = a._replay.stage; a.round = a._replay.round;
        try { localStorage.setItem('pp_arcade_stage', String(a.stage)); } catch { /* */ }
        a._replay = null;
      }   // v2.96
      this._banner = {
        title: reason === 'lives' ? T('ark_nolives') : T('ark_timeup'),
        sub: T('ark_retry'), col: '#e06c5a',
      };
      g.audio.fanfare(false);
      g.audio.announce(T('ark_timeup'), true);
    }
    this._hudDirty = true;
    if (a.map) a.map.refresh();
  }

  _afterResult() {
    const g = this.game;
    const a = this.ctrl;
    this.stop();
    // v3.6.12 (ronda 15): DERROTA → la MISMA prueba se relanza (segunda
    // oportunidad, con su cartel explicativo y botón EMPEZAR); el duelo
    // del camino sólo vuelve tras VICTORIA o fuera de la prueba.
    if (this._lastWin === false) {
      a.startArkanoid();
      return;
    }
    // nueva partida con el CLOWN (el camino sigue en su paso actual):
    // v2.44 — etapa 2 = CLOWN Nv. 2 · etapa 4 = CLOWN Nv. 3
    g.rules.startMatch('match');
    g.applyAISkill();
    g.resetToss();
    g.aiToss = null;
    g.ai.reset();
    g.setupAIServe();
    a.round = (a.rank ? a.rank.length : 0) + 1;
    a.streakP = 0;
    a.streakAi = 0;
    a._lastTotal = 0;          // evita el doble cartel de PARTIDA NUEVA
    a.state = 'present';
    a._transient = 2.2;
    a.rival.sprite.visible = true;
    if (a.rival.gift) a.rival.gift.visible = true;   // v2.41 FIX: el REGALO
    a.rival.setState('present');                     // reaparece al volver
    a.rankPanel.group.visible = true;
    a.rankPanel.refresh();
    a.cartel.show(a.round);
    if (a.map) a.map.refresh();
    g.rules.message = T('msg_arcade');
    g.audio.rivalSfx('present');
    g.audio.setArcWanted(true);
    // v2.44: mensaje del nivel que toca (nunca se auto-equipa la pistola:
    // sólo entra en escena dentro del ARKANOID 2)
    if (a.stage >= 4) g.rules.message = T('clown3_up');
    else if (a.stage >= 2) g.rules.message = T('clown2_up');
  }

  /* ---------------- animaciones y HUD ---------------- */

  _anims(dt) {
    // v3.6.45 · tweens de la ATRACCIÓN eléctrica: cada ladrillo viaja a su
    // celda nueva en 0,35 s (ease suave); al llegar, destello de llegada
    for (let i = this._eMove.length - 1; i >= 0; i--) {
      const mv = this._eMove[i];
      mv.t += dt / 0.35;
      const k = mv.t >= 1 ? 1 : mv.t * mv.t * (3 - 2 * mv.t);
      mv.b.mesh.position.set(
        mv.fx + (mv.tx - mv.fx) * k, mv.fy + (mv.ty - mv.fy) * k, this.C.z);
      if (mv.t >= 1) {
        this._eMove.splice(i, 1);
        this._flash(mv.b.mesh.position);
      }
    }
    // v2.41: flashes de destrucción (estallido aditivo que crece y muere)
    for (const f of this._flashes) {
      if (f.t <= 0) continue;
      f.t += dt;
      const k = f.t / 0.22;
      if (k >= 1) { f.t = 0; f.mesh.visible = false; continue; }
      f.mesh.material.opacity = 0.85 * (1 - k);
      f.mesh.scale.setScalar(0.5 + k * 1.1);
    }
    for (let i = this._dying.length - 1; i >= 0; i--) {
      const d = this._dying[i];
      d.t += dt * 3.4;
      if (d.t >= 1) {
        d.mesh.visible = false;
        this._dying.splice(i, 1);
        continue;
      }
      d.mesh.scale.setScalar(Math.max(0.01, 1 - d.t));
      d.mesh.rotation.z += d.spin * dt;
      d.mesh.rotation.x += d.spin * 0.6 * dt;
    }
    for (const d of this._debris) {
      if (d.life <= 0) continue;
      d.life -= dt;
      if (d.life <= 0) { d.mesh.visible = false; continue; }
      d.vel.y += DIMS.gravity * 0.72 * dt;   // v2.42: gravedad REAL (escombros)
      d.mesh.position.addScaledVector(d.vel, dt);
      d.mesh.rotation.x += dt * 6;
      d.mesh.rotation.y += dt * 4.4;
      d.mesh.scale.setScalar(Math.max(0.05, Math.min(1, d.life * 2.2)));
    }
    // v2.46 · "+1 MIN" (extra.png): sube despacio y se desvanece en 2 s
    if (this._extraFx && this.extraPlane) {
      const g = this.game;
      const fx = this._extraFx;
      fx.t += dt;
      const k = fx.t / 2;
      if (k >= 1) {
        this._extraFx = null;
        this.extraPlane.visible = false;
      } else {
        this.extraPlane.position.y = fx.pos.y + 0.16 * k;
        this.extraPlane.material.opacity =
          k < 0.15 ? k / 0.15 : Math.max(0, 1 - (k - 0.15) / 0.85);
        this.extraPlane.quaternion.copy(
          g.camera ? g.camera.quaternion : new THREE.Quaternion());
      }
    }
  }

  _hud() {
    this._hudDirty = false;
    const cv = this.hudCv, g2 = cv.getContext('2d');
    const W = 1024, H = 214;
    g2.clearRect(0, 0, W, H);
    // tarjeta
    g2.fillStyle = 'rgba(8,14,30,0.92)';
    g2.strokeStyle = 'rgba(232,180,90,0.9)';
    g2.lineWidth = 7;
    g2.beginPath();
    const rr = 30;
    g2.moveTo(rr, 6); g2.arcTo(W - 6, 6, W - 6, H - 6, rr);
    g2.arcTo(W - 6, H - 6, 6, H - 6, rr);
    g2.arcTo(6, H - 6, 6, 6, rr);
    g2.arcTo(6, 6, W - 6, 6, rr);
    g2.closePath(); g2.fill(); g2.stroke();

    const banner = this._banner;
    if (banner && (this.phase === 'intro' || this.phase === 'result')) {
      g2.textAlign = 'center'; g2.textBaseline = 'middle';
      g2.fillStyle = banner.col;
      g2.font = '900 78px system-ui, sans-serif';
      g2.fillText(banner.title, 512, this.phase === 'intro' ? 88 : 84);
      g2.fillStyle = '#dfe6ec';
      g2.font = '600 40px system-ui, sans-serif';
      g2.fillText(banner.sub, 512, this.phase === 'intro' ? 160 : 156);
      this.hudTex.needsUpdate = true;
      return;
    }
    // línea de juego: tiempo · ladrillos · vidas
    const sec = Math.max(0, Math.ceil(this.time));
    const mm = Math.floor(sec / 60), ss = sec % 60;
    const tcol = sec <= 10 ? '#ff5a48' : sec <= 60 ? '#ffd257' : '#eef2f6';
    g2.textAlign = 'left'; g2.textBaseline = 'middle';
    g2.fillStyle = tcol;
    g2.font = '900 86px ui-monospace, SFMono-Regular, Menlo, monospace';
    g2.fillText(`${mm}:${ss < 10 ? '0' : ''}${ss}`, 56, 104);
    g2.fillStyle = '#9aa7b4';
    g2.font = '700 26px system-ui, sans-serif';
    g2.fillText(T('hud_time'), 58, 172);
    g2.textAlign = 'center';
    g2.fillStyle = '#eef2f6';
    g2.font = '800 52px system-ui, sans-serif';
    g2.fillText(`${this.bricks.length - this.bricksLeft} / ${this.bricks.length}`, 512, 96);
    g2.fillStyle = '#9aa7b4';
    g2.font = '700 26px system-ui, sans-serif';
    g2.fillText(T('hud_bricks'), 512, 166);
    // vidas
    g2.textAlign = 'right';
    const full = ARK_CFG.lives, lost = full - Math.max(0, this.lives);
    let dots = '';
    for (let i = 0; i < full; i++) dots += i < (full - lost) ? '\u25CF ' : '\u25CB ';
    g2.fillStyle = this.lives <= 1 ? '#ff5a48' : '#7fb069';
    g2.font = '800 46px system-ui, sans-serif';
    g2.fillText(dots.trim(), 972, 96);
    g2.fillStyle = '#9aa7b4';
    g2.font = '700 26px system-ui, sans-serif';
    g2.fillText(T('hud_lives'), 970, 166);
    if (this._msg) {
      g2.textAlign = 'center';
      g2.fillStyle = '#ffd257';
      g2.font = '800 40px system-ui, sans-serif';
      g2.fillText(this._msg, 512, 40);
    }
    this.hudTex.needsUpdate = true;
  }
}

/* =====================================================================
 *  ArcadeController — cerebro del campeonato (modos, estados, poderes)
 *  ===================================================================== */
class ArcadeController {
  constructor(game) {
    this.game = game;
    this.data = (typeof window !== 'undefined' && window.__PP_ARCADE_DATA) || null;
    // v2.120: resolvedor de assets (iconos de los superpoderes nuevos)
    try { this._A = (p) => new URL('./assets/' + p, import.meta.url).href; }
    catch (e) { this._A = () => ''; }
    this.active = false;
    this.inited = false;
    this.t = 0;
    // estado del rival
    this.state = 'idle';
    this._transient = 0;        // segundos restantes del estado transitorio
    this._picandoDone = false;  // el aviso de picando ya salió en este rallye
    this._panicWarned = false;  // el aviso sonoro de match-point ya sonó
    this._lastTotal = -1;       // para detectar PARTIDA NUEVA (auto-revancha)
    this.streakP = 0;
    this.streakAi = 0;
    this.round = 1;
    // ranking persistente
    let rank = [];
    let wins = 0;
    let streak = 0;
    try {
      rank = JSON.parse(localStorage.getItem('pp_arcade_rank') || '[]');
      if (!Array.isArray(rank)) rank = [];
      wins = parseInt(localStorage.getItem('pp_arcade_wins') || '0', 10) || 0;
      streak = parseInt(localStorage.getItem('pp_arcade_streak') || '0', 10) || 0;
    } catch { /* localStorage bloqueado: sesión sin ranking */ }
    this.rank = rank;
    this.wins = wins;
    this.streak = streak;
    // poderes persistentes (mega_pala se gana al vencer al Clown; pistola
    // se gana superando la prueba ARKANOID)
    let powers = [];
    try { powers = JSON.parse(localStorage.getItem('pp_arcade_powers') || '[]'); } catch { /* */ }
    if (!Array.isArray(powers)) powers = [];
    this.powers = powers;
    // v2.38: ETAPA del camino (v2.44 — 6 pasos):
    //  0 CLOWN Nv.1 · 1 ARKANOID · 2 CLOWN Nv.2 · 3 ARKANOID 2 ·
    //  4 CLOWN Nv.3 · 5 CAMPEÓN (trofeo Campeonato de la Locura)
    let stage = 0;
    try { stage = parseInt(localStorage.getItem('pp_arcade_stage') || '0', 10) || 0; } catch { /* */ }
    if (!stage) {
      // compatibilidad: sin etapa guardada, dedúcela del ranking
      try {
        const rk = JSON.parse(localStorage.getItem('pp_arcade_rank') || '[]');
        if (Array.isArray(rk) && rk.length && rk[rk.length - 1].w) {
          stage = powers.includes('pistola') ? 2 : 1;
        }
      } catch { /* */ }
    }
    this.stage = stage;
    // v2.44: TROFEO del campeonato (gana el CLOWN Nv. 3 = paso 4)
    let trophy = false;
    try { trophy = localStorage.getItem('pp_arcade_trophy') === '1'; } catch { /* */ }
    this.trophy = trophy;
    this.arkQueued = false;   // victoria pendiente de derivar a ARKANOID
    this._replay = null;      // v2.96: rejugada en curso ({stage, round, play})
    this._arkDelay = 0;
    this.arkanoid = new ArcadeArkanoid(this);
    // v2.38: pistola de rayos (superpoder) y sus disparos en vuelo
    this._beams = [];
    this._gunLast = 0;
    this._gunHintDone = false;
    // v2.74 · PISTOLA REAL del artista (pistol.glb): estado de carga/montaje
    this._gunArt = [];          // clones del modelo en las monturas
    this._gunArtModel = null;   // escena GLB cargada (caché)
    this._gunArtLoading = false;
    this._gunMuzzle = null;     // boca del cañón (espacio montura) — el láser sale de aquí
    // v3.6.34: la MEGA PALA es NORMATIVA del NÚCLEO (carga por rally de
    // 11+ golpes, icono sobre el mango, gatillo voluntaria) — el módulo
    // ya no guarda estado ni pinta FX de pala (cero duplicados).
    // v2.35: superpoderes del rival EN PLENO JUEGO
    this._powerT = 0;          // segundos restantes del poder activo
    this._powerKind = '';      // 'confetti' | 'redball'
    this._powerCd = 0;         // cooldown hasta el próximo poder
    this._toward = false;      // la bola venía hacia el jugador (flanco)
    this._rallyFired = false;  // ya se lanzó un poder en este rallye
    this._lastPower = '';      // para alternar confeti/bola
    this._ballFx = null;       // respaldo de DIMS/malla de la BOLA LOCA
    // v2.36: aviso con 2 s de margen — el poder se SUELTA cuando el aviso
    // acaba (cartel SUPER POWER!! primero, efecto después)
    this._pendingPower = null; // poder anunciado esperando su momento
    this._pendT = 0;           // segundos restantes del aviso
    // v2.44 · BOLA DOBLE (superpoder del CLOWN Nv. 3): la bola se divide en
    // dos blancas; puedes perder UNA, la otra mantiene el rally vivo
    this._split = null;        // { ball, lastT } — clon vivo de la bola
    this._splitEvents = [];    // eventos del clon (SÓLO sonido, nunca árbitro)
  }

  get th() {
    const t = (this.data && this.data.thresholds) || {};
    return {
      picandoRallyHits: t.picandoRallyHits || ARCADE_DEFAULTS.picandoRallyHits,
      loosingDiff: t.loosingDiff || ARCADE_DEFAULTS.loosingDiff,
      comboRally: t.comboRally || ARCADE_DEFAULTS.comboRally,
      surprisedRally: t.surprisedRally || ARCADE_DEFAULTS.surprisedRally,
    };
  }

  build() {
    if (this.inited) return;
    this.inited = true;
    this.rival = new ArcadeRival(this);
    this.rival.build();
    this.cartel = new ArcadeCartel(this);
    this.cartel.build();
    this.rankPanel = new ArcadeRanking(this);
    this.rankPanel.build();
    this.powerSign = new ArcadePowerSign(this);   // v2.35: SUPER POWER!!
    this.powerSign.build();
    this.map = new ArcadeMap(this);               // v2.36: ruta del campeonato
    this.map.build();
    this._buildTrophy();      // v2.48: COPA del Campeonato (visible si ya eres campeón)
    // v2.127: PRECALENTADO del pool de BURLA (cartones + rayos + partículas)
    // en el arranque de sesión — texturas en decodificación asíncrona para
    // que la primera activación del poder no tire un frame en la Quest.
    try { this._buildBurla(); } catch (e) { console.warn('[burla.pool]', e); }
  }

  /* ---------- v2.48 · COPA «CAMPEONATO DE LA LOCURA» ----------
   * La copa 3D de la v2.44 se perdió con la reconstrucción del workspace
   * (sólo sobrevivió el estado persistente). Vuelve COMO PIEZA PERMANENTE:
   * pedestal + copa dorada que se revela al ganar la etapa 4 y, desde
   * entonces, vive en la sala (anclada al rig, junto a la mesa) en TODOS
   * los modos — tu sala de trofeos particular. */

  _buildTrophy() {
    const g = this.game;
    if (this.trophyGroup) return;
    const G = new THREE.Group();
    G.position.set(1.18, 0, -1.05);
    G.rotation.y = -0.62;                  // mirando al centro de la sala
    const darkMat = new THREE.MeshStandardMaterial({
      color: 0x1b2233, roughness: 0.85, metalness: 0.08,
    });
    const railMat = new THREE.MeshStandardMaterial({
      color: 0xe8b45a, roughness: 0.4, metalness: 0.3, emissive: 0x3d2c08,
    });
    const goldMat = new THREE.MeshStandardMaterial({
      color: 0xf6b73c, roughness: 0.22, metalness: 0.9,
      emissive: 0x8a5a08, emissiveIntensity: 0.4,
    });
    // pedestal: peana oscura + remates ámbar (el lenguaje del arcade)
    const foot = new THREE.Mesh(
      new THREE.CylinderGeometry(0.20, 0.24, 0.06, 24), darkMat);
    foot.position.y = 0.03; G.add(foot);
    const col = new THREE.Mesh(
      new THREE.CylinderGeometry(0.10, 0.14, 0.86, 20), darkMat);
    col.position.y = 0.49; G.add(col);
    const trim2 = new THREE.Mesh(
      new THREE.CylinderGeometry(0.135, 0.135, 0.03, 24), railMat);
    trim2.position.y = 0.13; G.add(trim2);
    const trim1 = new THREE.Mesh(
      new THREE.CylinderGeometry(0.165, 0.165, 0.035, 24), railMat);
    trim1.position.y = 0.90; G.add(trim1);
    const top = new THREE.Mesh(
      new THREE.CylinderGeometry(0.15, 0.15, 0.045, 24), railMat);
    top.position.y = 0.935; G.add(top);
    // placa con el nombre (canvas)
    const cv = document.createElement('canvas');
    cv.width = 256; cv.height = 96;
    const c2 = cv.getContext('2d');
    c2.fillStyle = '#101623'; c2.fillRect(0, 0, 256, 96);
    c2.strokeStyle = 'rgba(232,180,90,0.9)'; c2.lineWidth = 5;
    c2.strokeRect(4, 4, 248, 88);
    c2.textAlign = 'center'; c2.fillStyle = '#ffd257';
    c2.font = '800 26px system-ui, sans-serif';
    c2.fillText('CAMPEÓN', 128, 40);
    c2.fillStyle = '#c8ced4';
    c2.font = '600 15px system-ui, sans-serif';
    c2.fillText('CAMPEONATO DE LA LOCURA', 128, 70);
    const ptex = new THREE.CanvasTexture(cv);
    ptex.colorSpace = THREE.SRGBColorSpace;
    const plate = new THREE.Mesh(new THREE.PlaneGeometry(0.19, 0.071),
      new THREE.MeshBasicMaterial({ map: ptex }));
    plate.position.set(0, 0.62, 0.128); G.add(plate);
    // copa dorada: base + tallo + cuerpo torneado + asas
    const cup = new THREE.Group();
    cup.position.y = 0.958; G.add(cup);
    const base = new THREE.Mesh(
      new THREE.CylinderGeometry(0.055, 0.065, 0.018, 20), goldMat);
    cup.add(base);
    const stem = new THREE.Mesh(
      new THREE.CylinderGeometry(0.012, 0.018, 0.055, 12), goldMat);
    stem.position.y = 0.038; cup.add(stem);
    const prof = [];
    for (let i = 0; i <= 16; i++) {
      const t = i / 16;                    // 0 cuello → 1 labio (copa que se abre)
      prof.push(new THREE.Vector2(0.028 + 0.042 * Math.pow(t, 1.6), t * 0.115));
    }
    const body = new THREE.Mesh(new THREE.LatheGeometry(prof, 28), goldMat);
    body.position.y = 0.062; cup.add(body);
    for (const sx of [-1, 1]) {
      const h = new THREE.Mesh(
        new THREE.TorusGeometry(0.03, 0.0065, 10, 22, Math.PI), goldMat);
      h.position.set(sx * 0.062, 0.13, 0);
      h.rotation.z = -sx * Math.PI / 2;    // arco abriéndose hacia fuera
      cup.add(h);
    }
    // halo aditivo que respira detrás de la copa
    const hcv = document.createElement('canvas');
    hcv.width = 128; hcv.height = 128;
    const h2 = hcv.getContext('2d');
    const grd = h2.createRadialGradient(64, 64, 6, 64, 64, 62);
    grd.addColorStop(0, 'rgba(255,214,120,0.85)');
    grd.addColorStop(0.5, 'rgba(255,180,60,0.25)');
    grd.addColorStop(1, 'rgba(255,150,60,0)');
    h2.fillStyle = grd; h2.fillRect(0, 0, 128, 128);
    const htex = new THREE.CanvasTexture(hcv);
    htex.colorSpace = THREE.SRGBColorSpace;
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: htex, transparent: true, opacity: 0.3,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    halo.scale.setScalar(0.52); halo.position.y = 1.12; G.add(halo);
    // animación (sólo cuando es visible — onBeforeRender no cuesta oculto):
    // giro lento de la copa + halo que respira + pop de escala al revelarse.
    // OJO: onBeforeRender vive en la MALLA del cuerpo (un Group NO la recibe)
    G.userData.t0 = performance.now() / 1000;
    G.userData.halo = halo;
    G.userData.reveal = 1;                 // 1 = ya asentada (sin pop)
    body.onBeforeRender = () => {
      const t = performance.now() / 1000 - G.userData.t0;
      cup.rotation.y = t * 0.55;
      halo.material.opacity = 0.22 + 0.1 * (0.5 + 0.5 * Math.sin(t * 2.1));
      if (G.userData.reveal < 1) {
        G.userData.reveal = Math.min(1, G.userData.reveal + 0.022);
        const s = 0.55 + 0.45 * G.userData.reveal;
        const e = 1 + Math.sin(G.userData.reveal * Math.PI) * 0.12;
        G.scale.setScalar(s * e);
      } else if (G.scale.x !== 1) {
        G.scale.setScalar(1);
      }
    };
    G.visible = !!this.trophy;             // campeón previo: ya vive en la sala
    g.rig.add(G);                          // anclado al rig (junto a la mesa)
    this.trophyGroup = G;
    this._cup = cup;
  }

  /** v2.48: REVELACIÓN de la copa al ganar la etapa 4 (pop + halo). */
  _revealTrophy() {
    this._buildTrophy();
    if (!this.trophyGroup || this.trophyGroup.visible) return;
    this.trophyGroup.visible = true;
    this.trophyGroup.userData.reveal = 0;    // dispara la animación de escala
    // v2.50 · FASE 1: ¡un campeón más! (evento anónimo de hito)
    // v3.6.8-SDK6 (ronda 11): lleva el ID del campeonato — embudo por champ.
    try { __PP_TELE.ev('champion', { id: 'locura' }); } catch { /* */ }
  }

  /** ENTRAR en el campeonato (botón del menú ARCADE). */
  /* ============ v2.96 · REJUGAR etapas superadas (mapa + gatillo) ============
   *  El núcleo apunta con la pala (replayMap/replayHover) y el gatillo
   *  sobre un nodo SUPERADO relanza esa etapa con el progreso congelado:
   *  al acabar el intento (victoria O derrota) el camino real vuelve. */
  replayMap() {
    if (!this.active || !this.map || !this.map.group || !this.map.group.visible) return null;
    if (this.arkanoid && this.arkanoid.active) return null;   // en PRUEBA no
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
    if (this.arkanoid && this.arkanoid.active) return;
    if (g.net.online) { g.rules.message = T('msg_guest_mode'); return; }
    if (!this.data) { g.rules.message = T('arc_no_data'); return; }
    const i = idx | 0;
    // v2.108: en MODO DEPURACIÓN, CUALQUIER nodo distinto del vigente usa la
    // vía de rejugada (progreso real congelado y restaurado al terminar):
    // saltar a etapas FUTURAS no adelanta el camino en ningún caso.
    if (i >= this.stage && (!ppDbg() || i === this.stage)) {
      this.stage = i;              // nodo VIGENTE: camino normal (sin rejugada)
      return this.startArcade();
    }
    this._replay = { stage: this.stage, round: this.round, play: i + 1 };
    this.stage = i;
    g.rules.message = ppDbg()
      ? ('DEPURACIÓN · ETAPA ' + String(i + 1))
      : T('replay_up', { n: String(i + 1) });
    try { g.audio.announce(g.rules.message, true); } catch (e) { /* */ }
    this.startArcade();
  }

  startArcade() {
    const g = this.game;
    if (!this.data) {
      g.rules.message = T('arc_no_data');
      return;
    }
    if (g.net.online) {
      g.rules.message = T('msg_guest_mode');
      return;
    }
    this.build();
    // v2.74 · LEY DEL ARTISTA: lo que funciona NO se toca — el MAPA DE LA
    // PARED se recupera en TODAS las entradas. Antes, entrar con la etapa
    // en una PRUEBA (1 ARKANOID · 3 ARKANOID 2) saltaba directo a la prueba
    // ANTES de encender el mapa: el mapa desaparecía de la pared en toda la
    // sesión (duelos incluidos). Ahora se enciende SIEMPRE, también aquí.
    if (this.map) { this.map.group.visible = true; this.map.refresh(); }
    // v2.38: si la prueba ARKANOID estaba activa, devolver la escena
    this.arkanoid.stop();
    this.active = true;
    g.pendingMode = 'match';
    g.mode = 'arcade';
    g.rules.oppLabel = 'clown';
    g.rules.startMatch('match');
    g.applyAISkill();
    g.closeMenu();
    g.resetToss();
    g.aiToss = null;
    g.demoToss = null;
    g.ai.reset();
    g.setupAIServe();
    // ronda = rondas completadas + 1 (v2.96: en REJUGADA manda la rejugada)
    this.round = this._replay ? this._replay.play : ((this.rank ? this.rank.length : 0) + 1);
    this.streakP = 0;
    this.streakAi = 0;
    this._picandoDone = false;
    this._panicWarned = false;
    this._lastTotal = 0;
    // v2.35: superpoderes a cero al entrar (y bola restaurada)
    this._powerT = 0;
    this._powerKind = '';
    this._powerCd = 0;
    this._toward = false;
    this._rallyFired = false;
    this._lastPower = '';
    this._pendingPower = null;   // v2.36: sin avisos colgados de antes
    this._pendT = 0;
    g.freezeT = 0;               // v2.40: sin congelaciones heredadas
    this._restoreBall();
    // v2.44 · CAMINO: si la etapa actual es una PRUEBA (impar: 1 ARKANOID ·
    // 3 ARKANOID 2) se entra DIRECTAMENTE en ella (sin partida del Clown).
    if (this.stage === 1 || this.stage === 3) {
      this.startArkanoid();
      return;
    }
    if (this.powerSign) this.powerSign.hide();
    this.state = 'present';
    this._transient = 2.2;   // la presentación aguanta antes de pasar a idle
    // visibilidad de las piezas del arcade
    this.rival.sprite.visible = true;
    this.rival.stars.visible = false;
    if (this.rival.gift) this.rival.gift.visible = true;   // v2.37: regalo
    this.rival.setState('present');
    this.rankPanel.group.visible = true;
    this.rankPanel.refresh();
    if (this.map) { this.map.group.visible = true; this.map.refresh(); }
    this.cartel.show(this.round);
    // megáfono + fanfarria de presentación del rival
    g.rules.message = T('msg_arcade');
    g.audio.announce(T('arc_announce'), true);
    g.audio.rivalSfx('present');
    // v2.36: BANDA SONORA del campeonato — empieza con la partida (bajita)
    g.audio.setArcWanted(true);
    // v2.44 · anuncio del nivel del CLOWN que se pelea (2/3)
    if (this.stage >= 4) {
      g.rules.message = T('clown3_up');
    } else if (this.stage >= 2) {
      g.rules.message = T('clown2_up');
    }
  }

  /** SALIR del arcade (se juega otro modo). */
  leave() {
    if (!this.active && !this.inited) return;
    this.active = false;
    // v2.96: REJUGADA en curso — el progreso real vuelve
    if (this._replay) {
      this.stage = this._replay.stage;
      this._replay = null;
      try { localStorage.setItem('pp_arcade_stage', String(this.stage)); } catch { /* */ }
      if (this.map && this.map.refresh) this.map.refresh();
    }
    const g = this.game;
    // v2.36: la BSO SOLO suena durante la partida — fuera también
    g.audio.setArcWanted(false);
    this._pendingPower = null;   // v2.36: un aviso colgado ya no dispara nada
    this._pendT = 0;
    g.freezeT = 0;               // v2.40: nunca salir del arcade congelado
    this.arkQueued = false;      // v2.38: sin derivas pendientes
    if (this.arkanoid) this.arkanoid.stop();   // v2.38: restaurar la prueba
    // v2.38: el árbitro no puede quedarse en el estado de la prueba
    if (g.rules.state === 'arkanoid') {
      g.rules.startMatch(g.mode === 'survival' ? 'survival' : 'match');
    }
    if (this.inited) {
      this.rival.hide();
      this.rankPanel.hide();
      this.cartel.hide();
      this.powerSign.hide();   // v2.35
      this.map.hide();         // v2.36
    }
    // v2.74: la pistola del artista vuelve a su sitio (monturas como estaban)
    this._restoreGun();
    this._purgeBeams();        // v2.120: sin rayos atrapados (0,16 s de vida)
    this._endPower();          // v2.35: bola/confeti de vuelta a la normalidad
    if (g.rules.oppLabel === 'clown') g.rules.oppLabel = 'cpu';
  }

  /** Cambio de estado con PERSONALIDAD SONORA (v2.34). */
  setState(state, dur) {
    this.state = state;
    this._transient = dur || 0;
    if (this.inited) this.rival.setState(state);
    const kind = RIVAL_SFX[state];
    if (kind) this.game.audio.rivalSfx(kind);
  }

  /** v2.36: cambio de estado SIN voz (solo arte). Lo usa el aviso de
   *  superpoder para no solapar la risa con el sonido "powerup". */
  _setStateSilent(state, dur) {
    this.state = state;
    this._transient = dur || 0;
    if (this.inited) this.rival.setState(state);
  }

  /** Un punto acaba de puntuarse (hook de processIntents). */
  onPoint(it) {
    if (!this.active || it.survival) return;
    const th = this.th;
    if (it.winner === 'player') {
      this.streakP++;
      this.streakAi = 0;
      const hits = it.rallyHits || 0;
      if (hits >= th.comboRally) {
        // v3.6.34 · los rallyes largos SIGUEN poniendo al Clown hambriento,
        // pero la MEGA PALA ya no vive aquí: es NORMATIVA del núcleo y su
        // carga (rally de 11+ golpes) la pone el núcleo EN PLENO RALLYE.
        this.setState('hungry', 2.6);
      } else if (hits >= th.surprisedRally || this.streakP >= 2) {
        this.setState('surprised', 1.7);
      } else {
        this.setState('surprised', 1.2);
      }
    } else {
      this.streakAi++;
      this.streakP = 0;
      if (this.streakAi >= 2) {
        // el Clown ENLOQUECE (arte + voz): el PODER ya no se lanza aquí —
        // v2.35 lo dispara en pleno rallye para estorbar de verdad
        this.setState('crazy', 3.4);
      } else {
        this.setState('laughing', 2.4);
      }
    }
  }

  /** Fin de la ronda: ranking persistente + estado final del Clown.
   *  v2.44 · CAMINO DE 6 PASOS: ganar un CLOWN avanza una etapa
   *  (0→1→2→3→4) y ganar el CLOWN Nv. 3 (paso 4) da el TROFEO del
   *  «Campeonato de la Locura» (registrado en el palmarés, paso 5).
   *  Perder = repites el paso actual. Tras vencer a un Clown par (0/2/4)
   *  el camino deriva SOLO a la prueba ARKANOID que toque. */
  onMatchOver(winner) {
    if (!this.active) return;
    const w = winner === 'player';
    const p = this.game.rules.scorePlayer;
    const a = this.game.rules.scoreAi;
    this.rank.push({ w, p, a });
    if (this.rank.length > 10) this.rank = this.rank.slice(-10);
    if (w) {
      this.wins++;
      this.streak++;
      if (!this.powers.includes('mega_pala')) this.powers.push('mega_pala');
      try { localStorage.setItem('pp_arcade_powers', JSON.stringify(this.powers)); } catch { /* */ }
      if (this._replay) {
        // v2.96: REJUGADA — victoria real, pero el camino NO avanza
      } else if (this.stage >= 5) {
        // ya campeón: auto-revancha libre (sin camino que recorrer)
      } else if (this.stage === 4) {
        // ¡¡CAMPEÓN!! — TROFEO «Campeonato de la Locura» registrado
        this.trophy = true;
        try { localStorage.setItem('pp_arcade_trophy', '1'); } catch { /* */ }
        this._setStage(5);
        this.game.rules.stateTimer = 1e9;   // sin auto-revancha: brilla el trofeo
        this.game.rules.message = T('trophy_get');
        this.game.confettiBurst = Math.max(this.game.confettiBurst, 6);
        this.game.audio.announce(T('trophy_get'), true);
        // v2.128: INSIGNIA «¡CONSEGUIDO!» en grande (panel del núcleo)
        try { const C = window.__PP_CORE; if (C && C.showChampConseguido) C.showChampConseguido('locura'); } catch (e) { /* */ }
        if (this.game.renderer.xr.isPresenting) {
          this.game.haptic(this.game.paddleHand, 1.0, 300);
          window.setTimeout(() => this.game.haptic(this.game.paddleHand, 0.8, 240), 400);
        }
        this._revealTrophy();   // v2.48: la COPA aparece en la sala (pop + halo)
        if (this.inited) this.rankPanel.refresh();
        if (this.map) this.map.refresh();
        // (el bloque de abajo registra el ranking y detiene la BSO igualmente)
      } else if (this.stage % 2 === 0) {
        // v2.44: vencer a un CLOWN manda a la prueba ARKANOID que toque
        this._setStage(this.stage + 1);
        this.arkQueued = true;
        this._arkDelay = 4.4;
        this.game.rules.stateTimer = 1e9;   // sin auto-revancha: el camino avanza
      } else {
        this._setStage(this.stage + 1);
      }
    } else {
      this.streak = 0;
      // v2.44: perder REPITE el paso actual (misma etapa)
    }
    try {
      localStorage.setItem('pp_arcade_rank', JSON.stringify(this.rank));
      localStorage.setItem('pp_arcade_wins', String(this.wins));
      localStorage.setItem('pp_arcade_streak', String(this.streak));
    } catch { /* */ }
    // v2.67 · RANKING MUNDIAL: cada victoria de La Locura se publica
    // (victorias acumuladas = mérito; 🏆 si esa victoria dio el trofeo).
    // Silencioso: si no hay red, no pasa nada y la partida sigue igual.
    if (w && WORLDRANK && WORLDRANK.submit) {
      Promise.resolve(WORLDRANK.submit('locura', {
        n: ppPlayerName() || 'Anónimo',
        p: this.wins | 0,
        a: this.trophy ? '🏆' : '✔',
      })).catch(() => { /* nunca rompe */ });
    }
    this.round = this._replay ? this._replay.play : this.rank.length + 1;
    // v2.96: REJUGADA terminada (ganada o perdida) — el progreso REAL vuelve
    if (this._replay) {
      this.stage = this._replay.stage;
      this.round = this._replay.round;
      try { localStorage.setItem('pp_arcade_stage', String(this.stage)); } catch { /* */ }
      if (w) {
        this.game.rules.message = T('replay_done');
        try { this.game.audio.announce(T('replay_done'), true); } catch (e9) { /* */ }
      }
      this._replay = null;
    }
    if (this.inited) this.rankPanel.refresh();
    if (this.map) this.map.refresh();   // v2.36: progreso del mapa
    // v2.36: la partida terminó — SE DETIENE la banda sonora
    this.game.audio.setArcWanted(false);
    if (w) {
      this.setState('defeated', 5);
    } else {
      this.setState('victory', 5);
      if (this.inited) this.rival.stars.visible = true;
    }
  }

  update(dt) {
    if (!this.active || !this.inited) return;
    const g = this.game;
    const r = g.rules;
    const th = this.th;
    this.t += dt;
    this.rival.update(dt, this.t);
    this.cartel.update(dt);
    this.powerSign.update(dt);   // v2.35: cartel SUPER POWER!!
    this.map.update(dt);         // v2.36: anillo de progreso del mapa

    // v2.36 · AVISO ANTES DEL PODER: el cartel SuperPower aparece 2 s ANTES
    // y el efecto se suelta cuando el aviso termina (el jugador se prepara).
    if (this._pendingPower) {
      this._pendT -= dt;
      if (this._pendT <= 0) this._launchPending();
    }

    // v2.35 · SUPERPODERES DEL RIVAL EN PLENO JUEGO
    if (this._powerT > 0) {
      this._powerT -= dt;
      if (this._powerKind === 'redball') {
        // techo de velocidad VIVO: aunque la IA o el jugador golpeen fuerte,
        // la BOLA LOCA nunca supera su velocidad limitada
        const ball = g.ball;
        const cap = this._ballFx ? this._ballFx.msCap : Infinity;
        if (ball && ball.vel && ball.vel.lengthSq() > cap * cap) {
          ball.vel.setLength(cap);
        }
      }
      // v2.120: los dos poderes nuevos viven en SU update (mismo cerrojo)
      if (this._powerKind === 'globos') this._updateGlobos(dt);
      if (this._powerKind === 'burla') this._updateBurla(dt);
      if (this._powerT <= 0) this._endPower();   // vuelta a la normalidad
    } else if (this._powerCd > 0) {
      this._powerCd -= dt;
    }
    if (r.state !== 'rally') this._rallyFired = false;
    this.maybeTriggerPower();

    // PARTIDA NUEVA (auto-revancha del árbitro tras el cartel de fin):
    // el total de puntos vuelve a 0 -> cartel + presentación de nuevo
    if (this._lastTotal > 0 && r.totalPoints === 0) {
      this.round = this._replay ? this._replay.play : ((this.rank ? this.rank.length : 0) + 1);
      this.streakP = 0;
      this.streakAi = 0;
      this._panicWarned = false;
      this.rival.stars.visible = false;
      this.rival.setState('present');
      this.cartel.show(this.round);
      if (this.map) this.map.refresh();   // v2.36: progreso al nuevo round
      g.audio.rivalSfx('present');
      // v2.36: la nueva partida REARRANCA la banda sonora
      g.audio.setArcWanted(true);
    }
    this._lastTotal = r.totalPoints;

    // v2.38 · COLA HACIA ARKANOID: tras vencer al CLOWN Nv. 1 el camino
    // avanza SOLO (si el jugador no relanza un partido antes).
    if (this.arkQueued) {
      if (r.state !== 'over') {
        this.arkQueued = false;   // hubo revancha manual: se cancela
      } else {
        this._arkDelay -= dt;
        if (this._arkDelay <= 0) {
          this.arkQueued = false;
          this.startArkanoid();
        }
      }
    }
    // v2.38: pistola en la mano libre + rayos en vuelo
    this.updateGun(dt);

    // aviso sonoro ÚNICO de match-point en contra
    if (r.scorePlayer >= 10 && !this._panicWarned) {
      this._panicWarned = true;
      g.audio.rivalSfx('panic');
    } else if (r.scorePlayer < 10) {
      this._panicWarned = false;
    }

    // estados transitorios: vuelven a la base al agotarse
    if (this._transient > 0) {
      this._transient -= dt;
      if (this._transient <= 0) {
        this.state = (r.state === 'rally') ? 'focused' : 'idle';
        this.rival.setState(this.state);
      }
    } else if (this.state !== 'victory' && this.state !== 'defeated' &&
               this.state !== 'crazy' && this.state !== 'hungry') {
      // vigilancia del rallye: SOLO cambia el arte (sin sonido)
      if (r.state === 'rally') {
        if (r.rallyHits >= th.picandoRallyHits && !this._picandoDone) {
          // rallye largo del jugador: el Clown se pone PICANTO (con voz)
          this._picandoDone = true;
          this.setState('picando', 2.2);
        } else if (r.scorePlayer - r.scoreAi >= th.loosingDiff) {
          this.rival.setState('loosing');
        } else if (r.scorePlayer >= 10) {
          this.rival.setState('panic');
        } else {
          this.rival.setState('focused');
        }
      } else if (r.scorePlayer - r.scoreAi >= th.loosingDiff) {
        this.rival.setState('loosing');
      } else if (r.scorePlayer >= 10) {
        this.rival.setState('panic');
      } else {
        this.rival.setState('idle');
      }
    }
    if (r.state !== 'rally') this._picandoDone = false;
  }

  /* ============ v2.35 · SUPERPODERES DEL RIVAL (en pleno rallye) ============ */

  /** ¿Toca lanzar superpoder? SOLO con la bola en juego y viniendo hacia el
   *  jugador (para ESTORBAR el golpeo, no cuando el punto está muerto).
   *  Puertas: rally activo, cooldown, máximo 1 por rallye, azar y que no
   *  haya ya un aviso colgando (v2.36). */
  maybeTriggerPower() {
    if (!this.active || this._pendingPower) return;
    if (this._powerT > 0 || this._powerCd > 0) return;
    const g = this.game;
    const r = g.rules;
    const ball = g.ball;
    if (!ball || !ball.vel) return;
    if (r.state !== 'rally' || this._rallyFired) { this._toward = false; return; }
    const minHits = (this.data && this.data.powerTrigger &&
      this.data.powerTrigger.minRallyHits) || 1;
    if ((r.rallyHits || 0) < minHits) { this._toward = false; return; }
    // flanco: la bola ACABA de ponerse rumbo al jugador (vel.z > 0)
    const toward = ball.vel.z > 0.35;
    const edge = toward && !this._toward;
    this._toward = toward;
    if (!edge) return;
    const chance = (this.data && this.data.powerTrigger &&
      this.data.powerTrigger.chance) || ARCADE_DEFAULTS.powerChance;
    if (Math.random() < chance) this.firePower();
  }

  /** Lista de poderes del campeonato (respaldo: confeti + bola loca).
   *  v2.44: el CLOWN Nv. 3 (etapa >= 4) añade la BOLA DOBLE (split).
   *  v2.120: LLUVIA DE GLOBOS y MAREO entran en la rotación — y la bolsa
   *  se queda en UN MÁXIMO DE 4 (petición expresa): en Nv. 3 el confeti
   *  (lluvia plana) cede su sitio a los globos, su versión evolucionada.
   *  El confeti sigue íntegro en Nv. 1/2.
   *  v2.121: TODOS los poderes llevan MINIATURA propia en el cartel
   *  (los clásicos confeti/bola loca/split estrenan powerconfeti/
   *  powerbola/powersplit.png).
   *  v2.127: BURLA sustituye a MAREO en la bolsa (el mareo «no funciona»
   *  según el dueño; el rayo arcoíris con cartones burlescos sí se ve,
   *  se toca y decide puntos). */
  _powerList() {
    const list = (this.data && this.data.powers) || [];
    const base = Array.isArray(list) && list.length
      ? list
      : [{ kind: 'confetti', duration: 8 },
         Object.assign({ kind: 'redball', duration: 8 }, REDBALL_DEFAULTS)];
    const nuevos = [{ kind: 'globos', duration: 9, icon: 'powerglobos.png' },
                    { kind: 'burla', duration: 9, icon: 'powerburla.png' }];
    let out;
    if (this.clownLevel() >= 2) {
      // Nv. 3: redball + split + los 2 nuevos = 4 (confeti cede el turno)
      const b2 = base.filter((p) => p && p.kind !== 'confetti');
      out = b2.concat([{ kind: 'split', duration: 10, icon: 'powersplit.png' }], nuevos);
    } else {
      out = base.concat(nuevos);
    }
    // v2.121: miniatura de los CLÁSICOS (la base puede venir del manifest
    // sin icon; aquí se completa por kind — idempotente)
    const ICONOS = { confetti: 'powerconfeti.png', redball: 'powerbola.png' };
    for (const p of out) {
      if (p && p.kind && !p.icon && ICONOS[p.kind]) p.icon = ICONOS[p.kind];
    }
    return out;
  }

  /** v2.44 · Nivel del CLOWN según la etapa del camino:
   *  etapa 0/1 = Nv. 1 · etapa 2/3 = Nv. 2 · etapa 4+ = Nv. 3. */
  clownLevel() {
    if (this.stage >= 4) return 2;
    if (this.stage >= 2) return 1;
    return 0;
  }

  /** v2.36 · AVISO + LANZAMIENTO EN DOS FASES:
   *  1) firePower() — elige el poder, muestra el cartel "SUPER POWER!!"
   *     con su voz y deja el efecto ARMADO durante "powerTrigger.warn"
   *     segundos (2 s) para que el jugador se entere y se prepare.
   *  2) _launchPending() — pasado el aviso (y con la bola AÚN en juego)
   *     suelta el efecto de verdad. Si el punto murió durante el aviso,
   *     el poder se guarda (cooldown corto) para el siguiente rallye. */
  firePower(forceKind) {
    const g = this.game;
    let list = this._powerList().filter((p) => p && p.kind);
    if (!list.length) return;
    if (forceKind) {
      const hit = list.filter((p) => p.kind === forceKind);
      if (hit.length) list = hit;
    } else if (list.length > 1) {
      // v2.126 (módulo v17) · BOLSA ROTATORIA: todos los poderes salen antes
      // de repetir — GLOBOS y BURLA quedan garantizados dentro de los
      // primeros anuncios de la sesión. Antes el azar puro podía esconder
      // un poder muchos partidos seguidos y el dueño lo vivía como
      // «ese superpoder no funciona».
      if (!this._powerBag || !this._powerBag.length) {
        this._powerBag = list.map((p) => p.kind);
        for (let i = this._powerBag.length - 1; i > 0; i--) {
          const j = (Math.random() * (i + 1)) | 0;
          const t = this._powerBag[i];
          this._powerBag[i] = this._powerBag[j];
          this._powerBag[j] = t;
        }
      }
      let kind = this._powerBag.pop();
      if (kind === this._lastPower && this._powerBag.length) {
        // último recurso anti-repetición inmediata (la bolsa ya evita
        // repetir hasta agotarse; esto cubre el recorte de fuerzaKind)
        const alt = this._powerBag.shift();
        this._powerBag.push(kind);
        kind = alt;
      }
      const hit = list.filter((p) => p.kind === kind);
      if (hit.length) list = hit;
    }
    const cfg = list[(Math.random() * list.length) | 0];
    const warn = ((this.data && this.data.powerTrigger &&
      this.data.powerTrigger.warn) || ARCADE_DEFAULTS.powerWarn);
    this._pendingPower = cfg;
    this._pendT = warn;
    this._rallyFired = true;
    // el Clown ENLOQUECE al anunciar su poder (SOLO arte: la voz la pone
    // el aviso "powerup", la risa la reservamos para ganar el punto)
    this._setStateSilent('crazy', Math.min(3.4, Math.max(2.2, warn * 1.3)));
    // aviso INMEJORABLE: cartel SUPER POWER!! en la cara + voz + vibración
    // v2.40 · ANUNCIO ÉPICO: el cartel hace su número (≈2 s) con la PARTIDA
    // CONGELADA (game_part3 gatea IA/física/saque/árbitro/prueba con
    // freezeT). El aviso (pendT) sigue contando durante la congelación, así
    // que al reanudarse la partida en el punto exacto el poder entra en
    // juego: se anuncia el superpoder sin molestar a la partida.
    // v2.120: el cartel muestra el ICONO del poder anunciado si lo tiene.
    this.powerSign.show(cfg.icon ? this._A(cfg.icon) : null);
    // v3.6.2-SDK2: congela() del SDK — el patrón v2.40 que nació aquí vive
    // ahora en UNA sola fuente para los 5 campeonatos.
    congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1);
    g.audio.rivalSfx('powerup');
    g.rules.message = T('arc_power_warn');
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.6, 200);
  }

  /** Fase 2: el aviso terminó — el poder ENTRA en juego (si el punto
   *  sigue vivo; si no, se guarda para el siguiente rallye). */
  _launchPending() {
    const cfg = this._pendingPower;
    this._pendingPower = null;
    this._pendT = 0;
    if (!cfg) return;
    const g = this.game;
    if (g.rules.state !== 'rally') {
      // v2.126 (módulo v17) · LANZAMIENTO GARANTIZADO: el aviso ya se pagó
      // (cartel SUPER POWER!! + congelación + voz + háptica) — el efecto
      // entra AUNQUE el punto haya muerto durante el aviso (saque/reposo):
      // globos y burla no necesitan rallye para existir. Sólo se respeta el
      // fin de partida y las pruebas (arkanoid), donde un poder sobrante
      // estorbaría. Antes: cualquier estado distinto de 'rally' se comía el
      // poder en silencio (el dueño lo vivía como «este poder no funciona»).
      if (g.rules.state === 'over' || g.rules.state === 'arkanoid') {
        this._powerCd = 3;
        this._rallyFired = false;
        return;
      }
      // v2.133 · BOLA DOBLE necesita rallye VIVO: el clon muere en el primer
      // frame fuera del rallye (updateSplit lo extingue con estado != rally) →
      // lanzarlo en saque/reposo era un cartel que prometía dos bolas y no
      // se veía NINGUNA. Se RE-ARMA 1,2 s y entra en el PRÓXIMO rallye (el
      // guard de maybeTriggerPower impide anunciar otro poder mientras el
      // aviso siga pendiente, así el split está GARANTIZADO). 'over' y
      // 'arkanoid' siguen cortando arriba.
      if (cfg.kind === 'split') {
        this._pendingPower = cfg;
        this._pendT = 1.2;
        return;
      }
    }
    const dur = (cfg && cfg.duration) || 8;
    this._powerKind = cfg.kind;
    this._lastPower = cfg.kind;
    this._powerT = dur;
    const cd = (this.data && this.data.powerTrigger && this.data.powerTrigger.cooldown) ||
      ARCADE_DEFAULTS.powerCooldown;
    this._powerCd = cd + dur;
    if (cfg.kind === 'redball') this._applyBallFx(cfg);
    else if (cfg.kind === 'confetti') {
      // lluvia DENSA sobre tu campo (8 s): estorba la visión y el golpeo
      g.confettiBurst = Math.max(g.confettiBurst, dur);
    } else if (cfg.kind === 'split') {
      // v2.44 · BOLA DOBLE: la bola se divide en DOS blancas con trayectoria
      // ligeramente distinta. Puedes perder UNA (se anula el punto) si la
      // OTRA sigue viva; la viva continúa el rallye como bola oficial.
      this._startSplit();
    } else if (cfg.kind === 'globos') {
      // v2.120 · LLUVIA DE GLOBOS: flotan sobre TU campo, estorban la vista
      // y REVIENTAN con la bola (mini-confeti); renacen hasta el final.
      this._startGlobos();
    } else if (cfg.kind === 'burla') {
      // v2.127 · BURLA: rayo arcoíris + cartones burlescos de 50 cm (2 s)
      // que frenan la bola; el comodín la ennegrece y da PUNTO GANADOR.
      this._startBurla();
    }
    g.rules.message = cfg.kind === 'redball'
      ? T('arc_power_ball') : cfg.kind === 'split'
        ? T('arc_power_split') : cfg.kind === 'globos'
          ? T('arc_power_globos') : cfg.kind === 'burla'
            ? T('arc_power_burla') : T('arc_power_confetti');
  }

  /* ============ v2.44 · BOLA DOBLE (superpoder del CLOWN Nv. 3) ========== */

  /** Divide la bola: clon blanco con velocidad ligeramente desviada. */
  _startSplit() {
    const g = this.game;
    if (this._split || !g.ball) return;
    const main = g.ball;
    const clone = {
      pos: main.pos.clone(),
      vel: main.vel.clone(),
      spin: main.spin.clone(),
      ignoreNet: !!main.ignoreNet,
      radius: DIMS.ballRadius,
    };
    // desviación de trayectoria: giro vertical ±8° y velocidad ±8%
    const dev = (Math.random() < 0.5 ? 1 : -1) * (0.10 + Math.random() * 0.05);
    const cos = Math.cos(dev), sin = Math.sin(dev);
    const vx = clone.vel.x * cos - clone.vel.y * sin;
    clone.vel.y = clone.vel.x * sin + clone.vel.y * cos;
    clone.vel.x = vx;
    clone.vel.multiplyScalar(0.92);
    this._split = { ball: clone, born: performance.now() / 1000 };
    if (this.arkanoid) {
      // v2.120: el clon visual se crea PEREZOSO — con saltos de depuración
      // a etapa >= 2 (sin build del arkanoid) el clon corría físico e
      // invisible; ahora siempre hay malla.
      if (!this.arkanoid.cloneMesh && this.arkanoid._makeCloneMesh) {
        this.arkanoid._makeCloneMesh();
      }
      if (this.arkanoid.cloneMesh) this.arkanoid.cloneMesh.visible = true;
    }
    // AMBAS bolas se vuelven BLANCAS mientras dure el poder
    const m = g.ballMesh;
    if (m && m.material) {
      this._splitMainCol = m.material.color.getHex();
      this._splitMainEm = m.material.emissive ? m.material.emissive.getHex() : null;
      m.material.color.setHex(0xffffff);
      if (m.material.emissive) m.material.emissive.setHex(0xbfd4ff);
    }
    g.audio.playOsc(660, 1320, 0.22, 'sine', 0.16, 0);
    g.audio.playOsc(990, 1980, 0.22, 'triangle', 0.1, 0);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 130);
  }

  /** Fin de la bola doble: el clon desaparece y la bola oficial recupera su color. */
  _endSplit() {
    const g = this.game;
    if (!this._split) return;
    this._split = null;
    if (this.arkanoid && this.arkanoid.cloneMesh) {
      this.arkanoid.cloneMesh.visible = false;
    }
    const m = g.ballMesh;
    if (m && m.material && this._splitMainCol !== undefined) {
      m.material.color.setHex(this._splitMainCol);
      if (m.material.emissive && this._splitMainEm !== null) {
        m.material.emissive.setHex(this._splitMainEm);
      }
      this._splitMainCol = undefined;
    }
  }

  /** v2.44 · FILTRO DE MUERTE POR BOLA DOBLE — se llama ANTES del árbitro:
   *  si la bola oficial muere (suelo/pared) mientras el CLON sigue vivo y
   *  el punto sería PARA EL RIVAL (lastHitter = 'ai': bola del Clown que
   *  no llegaste a devolver), el clon pasa a ser la bola oficial, los
   *  eventos de muerte se retiran y el rallye CONTINÚA con la otra bola.
   *  Si el punto sería para ti (el Clown no llegó), el clon simplemente
   *  desaparece y el punto se juega normal. */
  splitFilterEvents(events) {
    if (!this._split) return;
    const g = this.game;
    if (g.rules.state !== 'rally') return;
    let save = false;
    let dead = false;
    for (let i = events.length - 1; i >= 0; i--) {
      const e = events[i];
      if (e.type !== 'floor' && e.type !== 'wall') continue;
      dead = true;
      if (g.rules.lastHitter === 'ai') {
        events.splice(i, 1);   // el árbitro jamás ve esta muerte
        save = true;
      }
    }
    if (!dead) return;
    if (save) {
      const clone = this._split.ball;
      g.ball.pos.copy(clone.pos);
      g.ball.vel.copy(clone.vel);
      g.ball.spin.copy(clone.spin);
      this._endSplit();
      g.rules.message = T('split_saved');
      g.audio.playOsc(880, 1180, 0.18, 'sine', 0.15, 0);
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 90);
    } else {
      // el punto juega normal: sin clon que lo salve
      this._endSplit();
    }
  }

  /** Física del CLON (v2.44): integración ligera con la física normal.
   *  Los eventos van a _splitEvents: SÓLO sonido/marcadores — el árbitro
   *  jamás los ve (el clon no puede puntuar ni cometer faltas). Si la PALA
   *  golpea al clon, el clon pasa a ser la bola oficial (swap) y el golpe
   *  se registra como golpe del jugador en el rallye. */
  updateSplit(dt) {
    if (!this._split) return;
    const g = this.game;
    // seguridad: fuera del rallye (o demasiado tiempo) se extingue
    if (g.rules.state !== 'rally' || performance.now() / 1000 - this._split.born > 14) {
      this._endSplit();
      return;
    }
    const pads = [];
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    if (g.renderer.xr.isPresenting && ps && ps.active) pads.push(ps);
    const evs = this._splitEvents;
    evs.length = 0;
    const clone = this._split.ball;
    stepPhysics(dt, clone, pads, evs, null);
    let converted = false;
    for (const e of evs) {
      if (e.type === 'paddle' && e.who === 'player') {
        // ¡Golpeaste al clon! El clon pasa a ser la bola oficial y el golpe
        // entra en el rallye como golpe del jugador (un solo evento).
        g.ball.pos.copy(clone.pos);
        g.ball.vel.copy(clone.vel);
        g.ball.spin.copy(clone.spin);
        this._endSplit();
        converted = true;
        g.events.push({ type: 'paddle', who: 'player', speed: e.speed,
          pos: g.ball.pos.clone(), paddleIndex: e.paddleIndex });
        break;
      }
    }
    if (converted) { evs.length = 0; return; }   // el evento sintético suena por sí solo
    // visual del clon
    if (this._split && this.arkanoid && this.arkanoid.cloneMesh) {
      this.arkanoid.cloneMesh.position.copy(clone.pos);
    }
    // sonido/háptica de los eventos del clon (SIN árbitro)
    if (evs.length) g.processEvents(evs);
    // el clon tocó el suelo: muere en silencio (puedes perder UNA)
    if (this._split) {
      for (const e of evs) {
        if (e.type === 'floor') { this._endSplit(); break; }
      }
    }
  }

  /** BOLA LOCA: bola ROJA, el DOBLE de tamaño, más LIGERA (menos gravedad)
   *  y LENTA (techo de velocidad). La malla escala x2 y el radio físico
   *  (DIMS.ballRadius) acompaña para que botes/golpes sigan siendo fieles.
   *  La IA y las predicciones leen DIMS en vivo, así que se adaptan solas. */
  _applyBallFx(cfg) {
    if (this._ballFx) return;
    const g = this.game;
    const m = g.ballMesh;
    if (!m || !m.material) return;
    const scale = THREE.MathUtils.clamp(cfg.scale || REDBALL_DEFAULTS.scale, 1.3, 2.6);
    const speedMul = THREE.MathUtils.clamp(cfg.speedMul || REDBALL_DEFAULTS.speedMul, 0.4, 0.95);
    const gravMul = THREE.MathUtils.clamp(cfg.gravityMul || REDBALL_DEFAULTS.gravityMul, 0.3, 0.9);
    this._ballFx = {
      r: DIMS.ballRadius,
      g: DIMS.gravity,
      ms: DIMS.maxBallSpeed,
      col: m.material.color.getHex(),
      em: m.material.emissive ? m.material.emissive.getHex() : 0x555044,
      msCap: DIMS.maxBallSpeed * speedMul,
    };
    DIMS.ballRadius = this._ballFx.r * scale;
    DIMS.gravity = this._ballFx.g * gravMul;
    DIMS.maxBallSpeed = this._ballFx.msCap;
    if (g.ball && g.ball.vel) g.ball.vel.multiplyScalar(speedMul);
    m.scale.setScalar(scale);
    m.material.color.setHex(0xe02430);       // ROJO Clown
    if (m.material.emissive) m.material.emissive.setHex(0x8a1016);
  }

  /** Restaura la bola (tamaño, color, gravedad, velocidad) tras el poder. */
  _restoreBall() {
    if (!this._ballFx) return;
    const f = this._ballFx;
    this._ballFx = null;
    DIMS.ballRadius = f.r;
    DIMS.gravity = f.g;
    DIMS.maxBallSpeed = f.ms;
    const m = this.game.ballMesh;
    if (m && m.material) {
      m.scale.setScalar(1);
      m.material.color.setHex(f.col);
      if (m.material.emissive) m.material.emissive.setHex(f.em);
    }
  }

  /** Fin del superpoder (timer agotado o salida del arcade). */
  _endPower() {
    this._powerT = 0;
    this._powerKind = '';
    // v2.120: el confeti de 'confetti' NO sobrevive al poder (si sales del
    // campeonato en pleno poder llovía hasta 8 s en el modo siguiente).
    if (this.game && this.game.confettiBurst) this.game.confettiBurst = 0;
    this._restoreBall();
    this._endSplit();     // v2.44: la bola doble también se extingue
    this._endGlobos();    // v2.120: sin globos flotando
    this._endBurla();     // v2.127: sin cartones ni comodín activo
  }

  /* ======== v2.120 · QUINTO Y SEXTO SUPERPODER DEL CLOWN ==================
   *  LLUVIA DE GLOBOS: 6 globos de colores suben y flotan sobre TU campo
   *  (9 s). Estorban la vista y REVIENTAN si la bola los toca (mini-confeti
   *  + pop); renacen desde el suelo mientras dure el poder. Arte: globo.png
   *  (3 tintas por rotación de tono). Icono en el cartel: powerglobos.png.
   *  MAREO TOTAL: el RIG se tambalea 7 s (vaivén senoidal con envolvente,
   *  amplitud 6,3° yaw / 2,6° roll) — VR comfort: sin traslación, sin
   *  sacudidas bruscas; la base del rig se GUARDA y se RESTAURA exacta.
   *  ======================================================================== */
  _assetUrlLoc(p) {
    try { return new URL('./assets/' + p, import.meta.url).href; }
    catch (e) { return ''; }
  }
  /** Pool de globos UNA vez por sesión (regla Quest: nada por partida). */
  _buildGlobos() {
    const g = this.game;
    if (this._globos) return;
    const N = 6;
    const grp = new THREE.Group();
    const items = [];
    const mkTintas = (tex0) => {
      // 3 tintas: rojo original + 2 rotaciones de tono (canvas perezoso)
      const out = [tex0, tex0, tex0];
      try {
        const im = new Image();
        im.onload = () => {
          const filtros = ['none', 'hue-rotate(115deg) saturate(1.05)', 'hue-rotate(250deg) saturate(1.05)'];
          for (let i = 1; i < 3; i++) {
            try {
              const cv = document.createElement('canvas');
              cv.width = im.width; cv.height = im.height;
              const c = cv.getContext('2d');
              c.filter = filtros[i];
              c.drawImage(im, 0, 0);
              const t = new THREE.CanvasTexture(cv);
              t.colorSpace = THREE.SRGBColorSpace;
              out[i] = t;
              for (const it of items) {
                if (it.variante === i) { it.s.material.map = t; it.s.material.needsUpdate = true; }
              }
            } catch (e) { /* sin tinta: rojo */ }
          }
        };
        im.src = this._assetUrlLoc('globo.png');
      } catch (e) { /* sin arte: reserva pintada */ }
      return out;
    };
    // reserva pintada (si globo.png no llegara nunca)
    const cvR = document.createElement('canvas');
    cvR.width = 128; cvR.height = 160;
    const cR = cvR.getContext('2d');
    cR.fillStyle = '#e03028';
    cR.beginPath(); cR.ellipse(64, 62, 50, 60, 0, 0, Math.PI * 2); cR.fill();
    cR.fillStyle = 'rgba(255,255,255,0.55)';
    cR.beginPath(); cR.ellipse(44, 40, 14, 20, -0.5, 0, Math.PI * 2); cR.fill();
    cR.strokeStyle = '#b02220'; cR.lineWidth = 2;
    cR.beginPath(); cR.moveTo(64, 122); cR.quadraticCurveTo(58, 138, 66, 152); cR.stroke();
    const texRes = new THREE.CanvasTexture(cvR);
    texRes.colorSpace = THREE.SRGBColorSpace;
    const tintas = mkTintas(texRes);
    for (let i = 0; i < N; i++) {
      const variante = i % 3;
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: tintas[variante], transparent: true, depthWrite: false,
        opacity: 0.97,
      }));
      s.scale.set(0.30, 0.30 * 160 / 128, 1);
      s.renderOrder = 32;
      s.visible = false;
      grp.add(s);
      items.push({
        s, variante, alive: false, popT: 0,
        x: 0, y: 0.2, z: 0, vy: 0, ph: Math.random() * Math.PI * 2,
      });
    }
    grp.visible = false;
    g.rig.add(grp);
    this._globos = { grp, items, tintas };
  }
  _startGlobos() {
    const g = this.game;
    this._buildGlobos();
    const G = this._globos;
    G.grp.visible = true;
    for (const it of G.items) this._respawnGlobo(it, true);
    try { g.audio.playOsc(520, 880, 0.25, 'sine', 0.14, 0); } catch (e) { /* */ }
  }
  _respawnGlobo(it, seed) {
    it.alive = true; it.popT = 0;
    // v2.121 · FIX: la banda era z POSITIVA (+0,10..+1,15) = DETRÁS de la
    // cabeza del jugador (él mira hacia -z, la mesa está en z<0): los globos
    // eran INVISIBLES en el visor. Ahora flotan SOBRE TU CAMPO, como el
    // confeti clásico (que funciona: banda hasta z≈+0,6): de la red a tu cara.
    it.z = -1.50 + Math.random() * 1.55;   // z ∈ [-1,50 .. +0,05]
    it.x = (Math.random() * 2 - 1) * 1.05;
    it.y = seed ? (1.0 + Math.random() * 0.55) : 0.84;   // renace SOBRE la mesa (0,76), no bajo ella
    it.vy = 0.55 + Math.random() * 0.35;
    it.s.visible = true;
    it.s.material.opacity = 0.97;
  }
  _updateGlobos(dt) {
    const g = this.game;
    if (!this._globos) return;
    const G = this._globos;
    const ball = g.ball;
    const rB = (window.__PP_CORE.DIMS && window.__PP_CORE.DIMS.ballRadius) || 0.02;
    for (const it of G.items) {
      if (!it.alive) {
        it.popT -= dt;
        if (it.popT <= 0) this._respawnGlobo(it, false);   // renace mientras dure
        continue;
      }
      // sube hasta su altura de patrulla y flota (bob senoidal)
      const objetivo = 1.05 + (it.ph % 1) * 0.5;
      if (it.y < objetivo) it.y += it.vy * dt;
      it.x += Math.sin(performance.now() / 1000 * 0.9 + it.ph) * dt * 0.22;
      it.s.position.set(it.x, it.y + Math.sin(performance.now() / 1000 * 1.3 + it.ph) * 0.05, it.z);
      // POP: la bola toca el globo (v2.126: radio +19% — la bola rápida
      // tunelaba el margen anterior y el dueño no veía reventar NINGUNO)
      if (ball && ball.pos) {
        const dx = ball.pos.x - it.x, dy = ball.pos.y - (it.y + 0.06), dz = ball.pos.z - it.z;
        if (dx * dx + dy * dy + dz * dz < (0.185 + rB) * (0.185 + rB)) {
          this._popGlobo(it);
          continue;
        }
      }
      // v2.121 · POP CON LA PALA (lo promete el cartel: «¡revienta la pala!»):
      // el centro de CUALQUIER pala activa del jugador dentro del globo
      // (0,20 m) lo revienta — sin allocs por frame (solo escalares).
      const pads = g.controllerPaddles;
      if (pads) {
        for (let pi = 0; pi < 2; pi++) {
          const p = pads[pi];
          if (!p || !p.active || !p.pos) continue;
          const px = p.pos.x - it.x, py = p.pos.y - (it.y + 0.06), pz = p.pos.z - it.z;
          if (px * px + py * py + pz * pz < 0.04) { this._popGlobo(it); break; }
        }
      }
    }
  }
  _popGlobo(it) {
    const g = this.game;
    it.alive = false; it.popT = 0.8 + Math.random() * 0.7;
    it.s.visible = false;
    // mini-confeti + pop (nunca rompe el frame)
    try { g.confettiBurst = Math.max(g.confettiBurst || 0, 0.35); } catch (e) { /* */ }
    try { g.audio.playNoise(0.12, 1800, 0.7, 0.16, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(700, 180, 0.10, 'square', 0.10, 0); } catch (e) { /* */ }
    if (g.renderer.xr.isPresenting) { try { g.haptic(g.paddleHand, 0.22, 40); } catch (e) { /* */ } }
  }
  _endGlobos() {
    if (!this._globos) return;
    this._globos.grp.visible = false;
    for (const it of this._globos.items) { it.alive = false; it.s.visible = false; }
  }
  /* ======== v2.127 · SÉPTIMO SUPERPODER DEL CLOWN: BURLA ==================
   *  Sustituye al MAREO (retirado por petición del dueño: «no funciona»).
   *  RAYO DE LUZ ARCOÍRIS que golpea la mesa en un punto DISTINTO cada vez
   *  (con un pequeño destello arcoíris en el impacto) y en ese punto se
   *  PLANTA un CARTÓN VERTICAL de ~50 cm (25 × 50 cm, cartón real) con el
   *  clown en actitud burlesca (arte del artista: burla1-4.png). Cada cartón
   *  está presente 2 SEGUNDOS y desaparece. Son BARRERAS: la bola que los
   *  cruza se FRENA (cae muerta en el sitio) y el cartón ESTALLA en
   *  partículas de color arcoíris. EL COMODÍN (burlacomodin.png, clown de
   *  espaldas, ~1 de cada 5 cartones): la bola SIGUE su curso normal pero
   *  se pone NEGRA y MÁS GRANDE — si la golpeas con la pala ESTALLA en
   *  cintas pequeñas negras y el punto es GANADOR para el jugador.
   *  Icono del cartel: powerburla.png (medallón arcoíris + cara burlesca).
   *  Regla Quest: TODOS los objetos son pools creados UNA VEZ por sesión
   *  (construidos en build(), texturas en decodificación asíncrona).       */
  _buildBurla() {
    const g = this.game;
    if (this._burla) return;
    const D = (window.__PP_CORE && window.__PP_CORE.DIMS) || {};
    const tableTopY = D.tableTopY || 0.76;
    const grp = new THREE.Group();
    grp.visible = false;

    /* --- texturas procedurales del rayo y del destello (canvas 1 vez) --- */
    const mkBeamTex = () => {
      const cv = document.createElement('canvas');
      cv.width = 64; cv.height = 256;
      const c = cv.getContext('2d');
      const COLORES = ['#ff3040', '#ff9a20', '#ffe83a', '#37e05a', '#2f9cff', '#b04dff'];
      const bh = 256 / COLORES.length;
      for (let i = 0; i < COLORES.length; i++) {
        c.fillStyle = COLORES[i];
        c.fillRect(0, i * bh, 64, bh + 1);
      }
      // fundido alfa en los extremos (el rayo nace y muere suave)
      const gd = c.createLinearGradient(0, 0, 0, 256);
      gd.addColorStop(0, 'rgba(0,0,0,1)');
      gd.addColorStop(0.18, 'rgba(0,0,0,0)');
      gd.addColorStop(0.82, 'rgba(0,0,0,0)');
      gd.addColorStop(1, 'rgba(0,0,0,1)');
      c.globalCompositeOperation = 'destination-out';
      c.fillStyle = gd;
      c.fillRect(0, 0, 64, 256);
      const t = new THREE.CanvasTexture(cv);
      t.colorSpace = THREE.SRGBColorSpace;
      return t;
    };
    const mkFlashTex = () => {
      const cv = document.createElement('canvas');
      cv.width = 128; cv.height = 128;
      const c = cv.getContext('2d');
      const cx = 64, cy = 64;
      const COLORES = ['rgba(255,255,255,1)', 'rgba(255,230,90,0.9)',
        'rgba(90,255,140,0.75)', 'rgba(80,170,255,0.6)', 'rgba(255,90,220,0.4)',
        'rgba(0,0,0,0)'];
      for (let i = 0; i < COLORES.length - 1; i++) {
        c.beginPath();
        c.arc(cx, cy, 60 - i * 11, 0, Math.PI * 2);
        c.fillStyle = COLORES[i];
        c.fill();
      }
      const t = new THREE.CanvasTexture(cv);
      t.colorSpace = THREE.SRGBColorSpace;
      return t;
    };
    const beamTex = mkBeamTex();
    const flashTex = mkFlashTex();

    /* --- cartones: 5 piezas (4 diseños + comodín), pool fijo ----------- */
    const CART_ART = ['burla1.png', 'burla2.png', 'burla3.png', 'burla4.png',
      'burlacomodin.png'];
    const cartGeo = new THREE.PlaneGeometry(0.25, 0.50);
    const cartones = CART_ART.map((art, i) => {
      const mat = new THREE.MeshBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0,
        side: THREE.DoubleSide, depthWrite: true,
      });
      const mesh = new THREE.Mesh(cartGeo, mat);
      mesh.visible = false;
      mesh.renderOrder = 30;
      grp.add(mesh);
      // arte asíncrono (la reserva blanca-brillos se ve el 1er instante)
      try {
        new THREE.TextureLoader().load(this._assetUrlLoc(art), (tex) => {
          tex.colorSpace = THREE.SRGBColorSpace;
          mat.map = tex;
          mat.color.setHex(i === 4 ? 0xffffff : 0xf2f2f2);
          mat.needsUpdate = true;
        }, undefined, () => { /* sin arte: cartón claro pintado */ });
      } catch (e) { /* */ }
      return {
        mesh, mat, kind: i === 4 ? 'comodin' : 'burla' + (i + 1),
        alive: false, age: 0, ph: Math.random() * Math.PI * 2,
        x: 0, z: 0, cx: 0, cz: 0,
      };
    });

    /* --- rayos arcoíris + destellos (pool de 2) ------------------------- */
    const beamGeo = new THREE.CylinderGeometry(0.016, 0.034, 1, 10, 1, true);
    const flashGeo = new THREE.PlaneGeometry(0.26, 0.26);
    const beams = [];
    for (let i = 0; i < 2; i++) {
      const bmat = new THREE.MeshBasicMaterial({
        map: beamTex, transparent: true, opacity: 0,
        blending: THREE.AdditiveBlending, depthWrite: false,
        side: THREE.DoubleSide,
      });
      const bm = new THREE.Mesh(beamGeo, bmat);
      bm.visible = false;
      bm.renderOrder = 33;
      grp.add(bm);
      const fmat = new THREE.MeshBasicMaterial({
        map: flashTex, transparent: true, opacity: 0,
        blending: THREE.AdditiveBlending, depthWrite: false,
        side: THREE.DoubleSide,
      });
      const fm = new THREE.Mesh(flashGeo, fmat);
      fm.rotation.x = -Math.PI / 2;
      fm.visible = false;
      fm.renderOrder = 34;
      grp.add(fm);
      beams.push({ bm, bmat, fm, fmat, t: 9, x: 0, z: 0 });
    }

    /* --- partículas arcoíris (explosión de cartones) -------------------- */
    const pGeo = new THREE.PlaneGeometry(0.03, 0.03);
    const RAINBOW = [0xff3040, 0xff9a20, 0xffe83a, 0x37e05a, 0x2f9cff, 0xb04dff];
    const parts = [];
    for (let i = 0; i < 26; i++) {
      const mat = new THREE.MeshBasicMaterial({
        color: RAINBOW[i % RAINBOW.length], transparent: true, opacity: 0,
        depthWrite: false, side: THREE.DoubleSide,
        blending: THREE.AdditiveBlending,
      });
      const m = new THREE.Mesh(pGeo, mat);
      m.visible = false;
      m.renderOrder = 35;
      grp.add(m);
      parts.push({ m, mat, vx: 0, vy: 0, vz: 0, t: 9, life: 0.7 });
    }

    /* --- cintas negras (estallido del comodín) -------------------------- */
    const rGeo = new THREE.PlaneGeometry(0.055, 0.012);
    const ribbons = [];
    for (let i = 0; i < 18; i++) {
      const mat = new THREE.MeshBasicMaterial({
        color: 0x0c0c10, transparent: true, opacity: 0,
        depthWrite: false, side: THREE.DoubleSide,
      });
      const m = new THREE.Mesh(rGeo, mat);
      m.visible = false;
      m.renderOrder = 35;
      grp.add(m);
      ribbons.push({ m, mat, vx: 0, vy: 0, vz: 0, rz: 0, t: 9, life: 1.1 });
    }

    g.rig.add(grp);
    this._burla = { grp, cartones, beams, parts, ribbons, tableTopY };
  }

  /** Un rayo golpea la mesa y PLANTA un cartón burlesco (o el comodín). */
  _spawnCarton() {
    const B = this._burla;
    if (!B) return;
    const libres = B.cartones.filter((c) => !c.alive);
    if (!libres.length) return;
    const comodinVivo = B.cartones.some((c) => c.alive && c.kind === 'comodin');
    let it;
    if (!comodinVivo && !this._comodinFx && Math.random() < 0.22) {
      it = libres.find((c) => c.kind === 'comodin');
    }
    if (!it) {
      const normales = libres.filter((c) => c.kind !== 'comodin');
      if (!normales.length) return;
      it = normales[(Math.random() * normales.length) | 0];
    }
    // punto de impacto SOBRE la mesa: de media pista rival a tu borde
    const D = (window.__PP_CORE && window.__PP_CORE.DIMS) || {};
    const cz = D.tableCenterZ || -1.6;
    it.x = (Math.random() * 2 - 1) * 0.58;
    it.z = (cz - 1.20) + Math.random() * 2.05;
    it.cx = it.x; it.cz = it.z;
    it.alive = true; it.age = 0;
    it.mesh.visible = true;
    it.mesh.position.set(it.x, B.tableTopY + 0.25, it.z);
    it.mesh.rotation.set(0, (Math.random() - 0.5) * 0.34, 0);
    it.mat.opacity = 0;
    // RAYO ARCOÍRIS: baja desde arriba + destello en el impacto
    const beam = B.beams.find((b) => b.t >= 0.5);
    if (beam) {
      beam.t = 0; beam.x = it.x; beam.z = it.z;
      beam.bm.visible = true;
      beam.bm.scale.set(1, 1.35, 1);
      beam.bm.position.set(it.x, B.tableTopY + 0.675, it.z);
      beam.bmat.opacity = 0;
      beam.fm.visible = true;
      beam.fm.position.set(it.x, B.tableTopY + 0.006, it.z);
      beam.fm.rotation.z = Math.random() * Math.PI;
      beam.fm.scale.setScalar(0.5);
      beam.fmat.opacity = 0;
    }
    try {
      this.game.audio.playOsc(1480, 220, 0.30, 'sawtooth', 0.10, 0);
      this.game.audio.playNoise(0.22, 2600, 0.5, 0.08, 0.02);
    } catch (e) { /* */ }
  }

  _startBurla() {
    const g = this.game;
    this._buildBurla();
    const B = this._burla;
    B.grp.visible = true;
    this._burlaSpawn = 0.25;      // el primer rayo entra casi al instante
    this._comodinFx = null;       // por si quedó algo de una activación previa
    this._burlaHasPrev = false;
    try { g.audio.playOsc(320, 880, 0.3, 'triangle', 0.12, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(880, 1320, 0.3, 'sine', 0.09, 0.05); } catch (e) { /* */ }
  }

  /** COMODÍN tocado: la bola SIGUE su curso, pero NEGRA y MÁS GRANDE. */
  _applyComodin() {
    const g = this.game;
    if (this._comodinFx) return;
    const m = g.ballMesh;
    if (!m || !m.material) return;
    this._comodinFx = {
      r: window.__PP_CORE.DIMS.ballRadius,
      col: m.material.color.getHex(),
      em: m.material.emissive ? m.material.emissive.getHex() : null,
    };
    window.__PP_CORE.DIMS.ballRadius = this._comodinFx.r * 1.75;
    m.scale.setScalar(1.75);
    m.material.color.setHex(0x0b0b0e);          // NEGRA
    if (m.material.emissive) m.material.emissive.setHex(0x2a1050);
    try {
      g.audio.playOsc(520, 130, 0.42, 'sawtooth', 0.14, 0);
      g.audio.playOsc(1040, 260, 0.42, 'triangle', 0.08, 0.02);
    } catch (e) { /* */ }
    try { g.rules.message = T('burla_comodin'); } catch (e) { /* */ }
    if (g.renderer.xr.isPresenting) { try { g.haptic(g.paddleHand, 0.5, 120); } catch (e) { /* */ } }
  }

  /** Devuelve la bola a su estado natural (fin del comodín). */
  _restoreComodin() {
    if (!this._comodinFx) return;
    const f = this._comodinFx;
    this._comodinFx = null;
    window.__PP_CORE.DIMS.ballRadius = f.r;
    const m = this.game.ballMesh;
    if (m && m.material) {
      m.scale.setScalar(1);
      m.material.color.setHex(f.col);
      if (m.material.emissive && f.em !== null) m.material.emissive.setHex(f.em);
    }
  }

  /** Golpeaste la bola negra del comodín: CINTAS NEGRAS + PUNTO GANADOR. */
  _comodinBoom() {
    const g = this.game;
    const B = this._burla;
    try {
      const p = g.ball.pos;
      // estallido de cintas pequeñas negras
      if (B) {
        for (const r of B.ribbons) {
          r.t = 0;
          r.m.visible = true;
          r.m.position.set(p.x, p.y, p.z);
          const a = Math.random() * Math.PI * 2;
          const sp = 0.9 + Math.random() * 1.7;
          r.vx = Math.cos(a) * sp;
          r.vz = Math.sin(a) * sp * 0.6;
          r.vy = 1.1 + Math.random() * 1.6;
          r.rz = (Math.random() - 0.5) * 12;
          r.m.rotation.set(Math.random() * 3, Math.random() * 3, 0);
          r.mat.opacity = 1;
        }
      }
      try { g.audio.playNoise(0.30, 900, 0.6, 0.20, 0); } catch (e) { /* */ }
      try { g.audio.playOsc(220, 60, 0.30, 'square', 0.12, 0); } catch (e) { /* */ }
      try { g.audio.playOsc(1600, 3200, 0.18, 'sine', 0.10, 0.04); } catch (e) { /* */ }
      if (g.renderer.xr.isPresenting) { try { g.haptic(g.paddleHand, 0.9, 160); } catch (e) { /* */ } }
      // la bola se queda quieta en el punto del golpe: el estallido manda
      if (g.ball && g.ball.vel) g.ball.vel.set(0, 0, 0);
    } catch (e) { /* */ }
    this._restoreComodin();
    // PUNTO GANADOR para el jugador (vía árbitro estándar: marcador, voz,
    // aplausos, celebración y reacción del Clown — todo el ceremonial)
    try {
      if (g.rules.state === 'rally') {
        const intents = g.rules.applyPoint('player', 'burla');
        if (intents && intents.length && g.processIntents) g.processIntents(intents);
      }
    } catch (e) { console.warn('[burla.punto]', e); }
  }

  _updateBurla(dt) {
    const B = this._burla;
    if (!B) return;
    const g = this.game;
    const D = window.__PP_CORE.DIMS;
    const rB = (D && D.ballRadius) || 0.02;

    // — cadencia de rayos/cartones mientras dure el poder —
    if (this._powerT > 1.2) {
      this._burlaSpawn -= dt;
      if (this._burlaSpawn <= 0) {
        this._spawnCarton();
        // 1,35–1,80 s < vida del cartón (2 s): SIEMPRE hay al menos uno en
        // pie y cada rayo cae en un punto distinto del tablero
        this._burlaSpawn = 1.35 + Math.random() * 0.45;
      }
    }

    // — rayos y destellos (vida 0,5 s) —
    for (const b of B.beams) {
      if (b.t >= 0.5) { b.bm.visible = false; b.fm.visible = false; continue; }
      b.t += dt;
      const fadeIn = Math.min(1, b.t / 0.08);
      const fadeOut = Math.max(0, 1 - Math.max(0, b.t - 0.10) / 0.40);
      b.bmat.opacity = 0.85 * fadeIn * fadeOut;
      b.fmat.opacity = Math.max(0, (1 - b.t / 0.42)) * fadeIn;
      const s = 0.5 + b.t * 3.2;
      b.fm.scale.setScalar(Math.min(1.7, s));
    }

    // — cartones: vida de 2 s, vaivén cómico y fundido de salida —
    for (const it of B.cartones) {
      if (!it.alive) continue;
      it.age += dt;
      it.mat.opacity = it.age < 0.12 ? it.age / 0.12
        : it.age > 1.78 ? Math.max(0, 1 - (it.age - 1.78) / 0.22) : 1;
      it.mesh.rotation.z = Math.sin(it.age * 3.1 + it.ph) * 0.03;
      if (it.age >= 2.0) {
        it.alive = false;
        it.mesh.visible = false;
        it.mat.opacity = 0;
        continue;
      }
    }

    // — colisiones bola ↔ cartones (sólo en rallye) —
    const ball = g.ball;
    if (ball && ball.pos && g.rules.state === 'rally' && this._burlaHasPrev) {
      const cur = ball.pos;
      const prev = this._burlaPrevV;
      for (const it of B.cartones) {
        if (!it.alive || it.mat.opacity < 0.5) continue;
        // cruce del plano del cartón (anti-túnel: segmento prev→actual)
        const dz0 = prev.z - it.cz;
        const dz1 = cur.z - it.cz;
        let hit = false;
        if (dz0 * dz1 <= 0 && Math.abs(dz0 - dz1) > 1e-6) {
          const f = dz0 / (dz0 - dz1);
          const xc = prev.x + (cur.x - prev.x) * f;
          const yc = prev.y + (cur.y - prev.y) * f;
          hit = Math.abs(xc - it.cx) < 0.125 + rB &&
                yc > B.tableTopY - 0.03 && yc < B.tableTopY + 0.50 + rB;
        }
        // proximidad para bolas lentas/verticales
        if (!hit && Math.abs(cur.z - it.cz) < 0.035 + rB &&
            Math.abs(cur.x - it.cx) < 0.125 + rB &&
            cur.y > B.tableTopY - 0.03 && cur.y < B.tableTopY + 0.50 + rB) {
          hit = true;
        }
        if (!hit) continue;
        // ESTALLIDO ARCOÍRIS del cartón
        it.alive = false;
        it.mesh.visible = false;
        it.mat.opacity = 0;
        const cy = B.tableTopY + 0.25;
        for (const p of B.parts) {
          if (p.t < p.life) continue;
          p.t = 0;
          p.m.visible = true;
          p.m.position.set(it.cx, cy, it.cz);
          const a = Math.random() * Math.PI * 2;
          const sp = 0.6 + Math.random() * 1.5;
          p.vx = Math.cos(a) * sp;
          p.vz = Math.sin(a) * sp * 0.6;
          p.vy = 0.8 + Math.random() * 1.9;
          p.mat.opacity = 1;
        }
        try { g.confettiBurst = Math.max(g.confettiBurst || 0, 0.3); } catch (e) { /* */ }
        try { g.audio.playNoise(0.16, 1400, 0.6, 0.14, 0); } catch (e) { /* */ }
        try { g.audio.playOsc(600, 160, 0.14, 'square', 0.10, 0); } catch (e) { /* */ }
        if (g.renderer.xr.isPresenting) { try { g.haptic(g.paddleHand, 0.35, 70); } catch (e) { /* */ } }
        // ¿cartón normal (frena) o COMODÍN (bola negra y grande)?
        if (it.kind === 'comodin') {
          this._applyComodin();        // la bola SIGUE su curso
        } else if (ball && ball.vel) {
          ball.vel.set(0, -0.4, 0);    // FRENADA: cae muerta en el sitio
          if (ball.spin) ball.spin.multiplyScalar(0.15);
        }
        break;   // un solo cartón por frame
      }
      // — comodín: golpeaste la bola negra → CINTAS NEGRAS + PUNTO GANADOR —
      if (this._comodinFx) {
        const evs = g.events;
        if (evs && evs.length) {
          for (const e of evs) {
            if (e && e.type === 'paddle' && e.who === 'player') {
              this._comodinBoom();
              break;
            }
          }
        }
      }
    }

    // memoria del segmento bola (anti-túnel del próximo frame)
    if (ball && ball.pos) {
      if (!this._burlaPrevV) this._burlaPrevV = new THREE.Vector3();
      this._burlaPrevV.copy(ball.pos);
      this._burlaHasPrev = true;
    }

    // — partículas arcoíris —
    for (const p of B.parts) {
      if (p.t >= p.life) { p.m.visible = false; continue; }
      p.t += dt;
      p.vy -= 4.6 * dt;
      p.m.position.x += p.vx * dt;
      p.m.position.y += p.vy * dt;
      p.m.position.z += p.vz * dt;
      p.m.rotation.z += dt * 7;
      p.mat.opacity = Math.max(0, 1 - p.t / p.life);
    }
    // — cintas negras —
    for (const r of B.ribbons) {
      if (r.t >= r.life) { r.m.visible = false; continue; }
      r.t += dt;
      r.vy -= 3.4 * dt;
      r.vx *= (1 - 1.6 * dt);
      r.vz *= (1 - 1.6 * dt);
      r.m.position.x += r.vx * dt;
      r.m.position.y += r.vy * dt;
      r.m.position.z += r.vz * dt;
      r.m.rotation.z += r.rz * dt;
      r.mat.opacity = Math.max(0, 1 - r.t / r.life);
    }
  }

  _endBurla() {
    this._restoreComodin();          // la bola vuelve a ser ella misma SIEMPRE
    if (!this._burla) return;
    const B = this._burla;
    B.grp.visible = false;
    for (const it of B.cartones) {
      it.alive = false;
      it.mesh.visible = false;
      it.mat.opacity = 0;
    }
    for (const b of B.beams) {
      b.t = 9;
      b.bm.visible = false;
      b.fm.visible = false;
    }
    for (const p of B.parts) { p.t = 9; p.m.visible = false; }
    for (const r of B.ribbons) { r.t = 9; r.m.visible = false; }
    this._burlaHasPrev = false;
  }

  /* ============ v2.38 · CAMINO Y PRUEBA ARKANOID ============ */

  /** Etapa del camino persistente: 0 CLOWN Nv. 1 · 1 ARKANOID · 2 pistola. */
  _setStage(s) {
    this.stage = s | 0;
    try { localStorage.setItem('pp_arcade_stage', String(this.stage)); } catch { /* */ }
    // v2.50 · FASE 1: avance del campeonato (telemetría anónima, sin PII)
    // v3.6.8-SDK6 (ronda 11): lleva el ID del campeonato — embudo por champ.
    try { __PP_TELE.ev('stage', { n: this.stage, id: 'locura' }); } catch { /* */ }
    // v2.85 · MOOD POR ETAPA del decorado de sala (room): en la etapa 4
    // (DUELO FINAL contra el CLOWN Nv. 3 JEFE) la carpa se tiñe de penumbra
    // roja; en el resto de etapas vuelve el circo de día. Guard: nunca rompe.
    try { if (GAME && GAME.champRoom) GAME.champRoom.useVariant(s === 4 ? 'final' : null); } catch { /* */ }
  }

  /** Lanza la prueba ARKANOID (cola automática tras vencer al Clown o
   *  botón «PRUEBA: ARKANOID» del menú CRAZY).
   *  v2.106 · CARTEL EXPLICATIVO antes de entrar (petición global: todas
   *  las pruebas de todos los campeonatos). Lo pinta el núcleo. */
  startArkanoid() {
    if (!this.active || !this.data) return;
    const g = GAME;
    if (this._instrK !== 'ark') {
      if (g && g.showInstrucciones) {
        this._instrK = 'ark';
        g.showInstrucciones(T('instr_ark_t'), T('instr_ark'), 7.5,
          () => { try { this.startArkanoid(); } catch (e) { /* */ } },
          'locura',   // v2.107: carpa de circo de LA LOCURA
          { empezar: true });   // v2.130: espera al botón EMPEZAR (común)
        return;
      }
    }
    this._instrK = null;
    this.arkQueued = false;
    // v2.74: el mapa de la pared sigue presente durante las pruebas
    if (this.map) { this.map.group.visible = true; this.map.refresh(); }
    this.arkanoid.start();
  }

  /** ¿Puede disparar la pistola la mano libre? (v2.44: SOLO dentro del
   *  ARKANOID 2 — la pistola NO se auto-equipa en otros modos/niveles) */
  get gunArmed() {
    const g = this.game;
    const ark = this.arkanoid;
    return !!(this.active && ark && ark.active && ark.variant === 2 &&
      ark.phase === 'play' &&
      g.gunMounts && g.gunMounts[1 - g.paddleHand] &&
      g.gunMounts[1 - g.paddleHand].visible);
  }

  /** DISPARO de la pistola de rayos (v2.44):
   *  · RAYO fino y brillante con glow (núcleo blanco + halo aditivo).
   *  · «pew» bajito de láser.
   *  · RAYCAST real: el haz sale en línea recta y DETECTA lo que atraviesa
   *    (ladrillos del muro): el primer objeto impactado recibe SU lógica —
   *    AZUL -> explota y queda ROJO · ROJO -> chispa (inmune al láser).
   *  · El haz termina EN el punto de impacto (o a 6 m si no hay nada). */
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
    // el cañón apunta AL FRENTE (-Z del grip, v2.45: pitch 0)
    const dir = new THREE.Vector3(0, Math.sin(GUN_MOUNT_PITCH), -Math.cos(GUN_MOUNT_PITCH))
      .applyQuaternion(q).normalize();
    // v2.74: el rayo nace de la BOCA DEL CAÑÓN del pistol.glb del artista
    // (_gunMuzzle, mismo encaje que magia); si el arte no cargó, el offset
    // de siempre del modelo del core.
    pos.add((this._gunMuzzle || GUN_MUZZLE).clone().applyQuaternion(q));

    // --- RAYCAST: qué atraviesa el rayo ---
    let hitDist = 6.0;
    let hitBrick = null;
    let hitTime = false;   // v2.46: impacto en el ladrillo negro del tiempo
    let hitBomb = false;   // v3.6.44: impacto en el ladrillo BOMBA
    const hitPoint = new THREE.Vector3();
    const ark = this.arkanoid;
    if (ark && ark.active && ark.bricks && ark.bricks.length) {
      const ray = new THREE.Raycaster(pos, dir, 0, 6.0);
      // v3.6.44 · el slot ocupado por la BOMBA se EXCLUYE (su azul está
      // oculto debajo — un rayo al ladrillo bomba debe dar a la bomba)
      const meshes = ark.bricks
        // v3.6.45 · el ELÉCTRICO es invisible al rayo (sólo la bola lo
        // activa — el láser ATRAVIESA su hueco)
        .filter((b) => b.alive && b.state !== 'elec' &&
          !(ark._bombBrick && b === ark._bombBrick.slot))
        .map((b) => b.mesh);
      // v2.46: el ladrillo NEGRO del tiempo extra también recibe el láser
      if (ark._timeBrick && ark.timeMesh) meshes.push(ark.timeMesh);
      // v3.6.44: el ladrillo BOMBA recibe el láser → detonación
      if (ark._bombBrick && ark.bombMesh) meshes.push(ark.bombMesh);
      const hits = ray.intersectObjects(meshes, false);
      if (hits.length) {
        hitDist = hits[0].distance;
        hitPoint.copy(hits[0].point);
        hitBrick = ark.bricks.find((b) => b.mesh === hits[0].object) || null;
        hitTime = !hitBrick && hits[0].object === ark.timeMesh;
        hitBomb = !hitBrick && !hitTime && hits[0].object === ark.bombMesh;
      }
    }

    // --- HAZ fino y brillante: núcleo + halo con glow aditivo ---
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

    // destello en el punto de impacto (convertido a espacio RIG: los
    // flashes del muro viven en el espacio de la mesa)
    if (hitBrick) {
      g.rig.updateWorldMatrix(true, false);
      const lp = g.rig.worldToLocal(hitPoint.clone());
      ark._flash(lp);
      ark.laserHit(hitBrick);   // SU lógica: azul->rojo (explosión) · rojo->chispa
    } else if (hitTime) {
      // v2.46: el láser revienta el ladrillo negro => +1 MINUTO
      g.rig.updateWorldMatrix(true, false);
      const lp = g.rig.worldToLocal(hitPoint.clone());
      ark._flash(lp);
      ark._breakTimeBrick();
    } else if (hitBomb) {
      // v3.6.44: el láser revienta la BOMBA => DETONACIÓN del radio 2×2
      g.rig.updateWorldMatrix(true, false);
      const lp = g.rig.worldToLocal(hitPoint.clone());
      ark._flash(lp);
      ark._detonarBomba();
    }

    // «pew» BAJITO de láser + vibración corta
    g.audio.playOsc(1760, 320, 0.1, 'sawtooth', 0.07, 0);
    g.audio.playOsc(2640, 660, 0.08, 'sine', 0.045, 0);
    g.audio.playNoise(0.05, 3400, 2.2, 0.035, 0);
    if (g.renderer.xr.isPresenting) g.haptic(i, 0.4, 60);
  }

  /** Pistola LÁSER (v2.44): visible SOLO dentro del ARKANOID 2 — en la mano
   *  LIBRE todo el rato, salvo el instante del saque (esa mano lanza la
   *  bola). Fuera del ARKANOID 2 la pistola NO se auto-equipa nunca.
   *  v2.74 · EL MODELO REAL: pistol.glb del artista (el mismo que magia
   *  monta desde v2.61), NO la pistola minúscula de respaldo del núcleo. */
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
          console.info('[locura] pistol.glb del artista montada (ARKANOID 2)');
        } catch (e) { console.warn('[locura] pistola: normalización KO', e); }
      }, undefined, () => {
        this._gunArtLoading = false;
        console.warn('[locura] pistol.glb no disponible — se mantiene la del core');
      });
    } catch (e) { this._gunArtLoading = false; }
  }

  /** Encaja el GLB del artista (MISMO encaje aprobado en magia v2.61/2.62):
   *  escala real ≈32 cm de largo, cañón hacia -Z, empuñadura en el origen
   *  de la montura (donde agarra la mano) y BOCA DEL CAÑÓN (_gunMuzzle)
   *  de la que sale el láser. */
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
    // BOCA DEL CAÑÓN en espacio de MONTURA (el láser sale de aquí y no del
    // puño) — misma fórmula que magia: ánima ≈ 2 cm bajo el plano superior.
    try {
      const bFin = new THREE.Box3().setFromObject(root);
      const dimF = bFin.getSize(new THREE.Vector3());
      this._gunMuzzle = new THREE.Vector3(0, dimF.y - 0.075, bFin.min.z + 0.015);
    } catch (e) { this._gunMuzzle = new THREE.Vector3(0, 0.02, -0.16); }
    // diagnóstico headless (tamaño final en metros tras el encaje)
    try {
      const fin = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
      window.__PP_LOCURA_GUN_INFO = {
        len: +fin.z.toFixed(3), alto: +fin.y.toFixed(3), ancho: +fin.x.toFixed(3),
        boca: this._gunMuzzle ? {
          x: +this._gunMuzzle.x.toFixed(3),
          y: +this._gunMuzzle.y.toFixed(3),
          z: +this._gunMuzzle.z.toFixed(3),
        } : null,
      };
    } catch (e) { /* */ }
    return root;
  }

  /** Monta el arte del artista en las DOS monturas (oculta la del core sin
   *  destruirla; la visibilidad real la gobierna updateGun por montura). */
  _attachGunArt() {
    const g = this.game;
    if (!g.gunMounts || !this._gunArtModel) return;
    this._restoreGun();
    for (const gm of g.gunMounts) {
      if (!gm) continue;
      for (const ch of gm.children) ch.visible = false;   // la del core, oculta
      const art = this._gunArtModel.clone(true);
      art.userData.__locuraArt = true;
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

  updateGun(dt) {
    const g = this.game;
    const ark = this.arkanoid;
    const ark2On = this.active && ark && ark.active && ark.variant === 2 &&
      (this.powers || []).includes('pistola') && g.renderer.xr.isPresenting;
    // fases con la mano libre OCUPADA (lanza la bola): intro/serve/result
    const holdPhase = ark && (ark.phase === 'serve' || ark.phase === 'intro' ||
      ark.phase === 'result');
    const armed = ark2On && !holdPhase;
    if (armed && !this._gunHintDone) {
      this._gunHintDone = true;
      g.rules.message = T('ark_gun_on');
    }
    // v2.74: carga PEREZOSA del pistol.glb del artista (sólo cuando la
    // pistola se arma por primera vez en el ARKANOID 2) + reenganche si
    // alguna limpieza anterior la retiró.
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
  /** v2.120 · PURGA DE RAYOS: los beams sólo se retiran en updateGun() (con
   *  la partida activa) — un leave() en los 0,16 s tras un disparo dejaba
   *  mallas+geometrías+materiales huérfanas en escena para siempre. */
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
}


/* ==================== INTERFAZ DEL MÓDULO (v2.69) =====================
 *  La misma familia de ganchos que magia. ChampLoader los llama TODOS
 *  con guard: un error del campeonato nunca tumba el frame.
 *  ===================================================================== */
export default {
  id: 'locura',
  /** v2.128: ¿campeonato superado? (cinta ★ SUPERADO del menú) */
  isChampion() { return !!(CTRL && CTRL.trophy); },
  /** Acceso de LECTURA al controller para las capas QA (la capa no
   *  escribe). La MEGA PALA es del núcleo desde v3.6.34. */
  get impl() { return CTRL; },
  /** Único módulo «legacy»: hasta v2.68 el núcleo leía SU estado directo.
   *  Hoy todo el acoplamiento pasa por los ganchos de abajo. */
  legacy: true,

  /* v2.80 · TROQUELES DE CARTÓN de ESTE campeonato (el payaso). El núcleo
   * lee «decor» del módulo ACTIVO y monta las piezas ancladas a la mesa,
   * orientadas al jugador y con la base EXACTAMENTE en el suelo. Los PNG
   * del artista van recortados a su propia transparencia (v2.80: SIN
   * borde añadido) en championships/locura/assets/decor/. Cada
   * campeonato tiene los SUYOS: un módulo sin «decor» no muestra
   * troquel alguno (el mago hoy — los de Wizard llegarán después). */
  decor: {
    pieces: [
      // file: ruta relativa a ESTA carpeta · h: alto del arte en metros
      // (el ancho lo deduce el núcleo del aspecto real del PNG) ·
      // x/z: coordenadas del RIG (mesa centrada en z=-1.6) · sway: vaivén.
      { file: 'assets/decor/caseta.png',   h: 1.15, x:  2.62, z: -1.95, sway: 0.5 },
      { file: 'assets/decor/globos.png',   h: 1.55, x: -1.95, z: -0.75, sway: 0.9 },
      { file: 'assets/decor/elefante.png', h: 1.05, x: -2.55, z: -2.45, sway: 0.7 },
      { file: 'assets/decor/canon.png',    h: 0.95, x:  1.95, z: -0.75, sway: 0.6 },
    ],
  },

  /* v2.85 · DECORADO DE SALA («room») — la GRAN CARPA DE CIRCO. El núcleo
   * (createChampRoom) viste los 6 PLANOS de la sala con el arte de
   * assets/room/ SOLO mientras este campeonato está activo: suelo de
   * pista de circo, cúpula de lona a franjas en el techo, cortinas de
   * telón, gradas con público y taquilla en la entrada. Al salir, la
   * sala vuelve EXACTAMENTE a su tema clásico (dispose de GPU incluido).
   * variants.final: en la etapa 4 (DUELO FINAL vs. el CLOWN JEFE) el
   * _setStage pide el mood «final» y la carpa se tiñe de penumbra roja.
   * Medidas reales de los planos: suelo/techo 6,10 × 7,90 m · paredes
   * frontal/trasera 6,10 × 2,85 m · laterales 7,90 × 2,85 m. */
  room: {
    floor: 'assets/room/suelo.jpg',
    ceil:  'assets/room/techo.jpg',
    back:  'assets/room/fondo.jpg',      // trasera: la entrada de la carpa
    front: 'assets/room/frente.jpg',     // pared del CLOWN: el escenario
    left:  'assets/room/izquierda.jpg',  // gradas + público
    right: 'assets/room/derecha.jpg',    // puestos y trapecio
    variants: {
      final: { tint: 0xc26a55 },         // penumbra roja del duelo JEFE
    },
  },


  get controller() { return CTRL; },

  /** ctx = { game, id, stateName }. Devuelve promesa: ChampLoader no
   *  considera el módulo listo hasta fusionar el bloque «cfg» del manifest. */
  init(ctx) {
    if (!DIMS || !stepPhysics || !T) {
      throw new Error('locura: window.__PP_CORE no disponible (¿fuera del juego?)');
    }
    GAME = ctx.game;
    const A = (p) => new URL('./assets/' + p, import.meta.url).href;
    const STS = ['present', 'idle', 'focused', 'surprised', 'hungry', 'panic',
      'laughing', 'defeated', 'victory', 'crazy', 'picando', 'loosing'];
    const wire = (cfg) => {
      const urls = {};
      for (const st of STS) urls[st] = A(st + '.webp');
      // (antes: data-URLs incrustadas en index.html — ahora ARCHIVOS propios)
      const data = Object.assign({}, LOCURA_CFG, cfg || {}, {
        urls,
        sounds: { laugh: A('risas.mp3'), crazy: A('risas.mp3') },
        powerBannerUrl: A('superpoder.webp'),
        musicUrl: A('bso.ogg'),
      });
      window.__PP_ARCADE_DATA = data;   // lo lee el NÚCLEO (BSO + voces)
      window.__PP_GIFT_URL = A('regalo.webp');
      window.__PP_GUNPOSTER_URL = A('poster_pistola.webp');
      window.__PP_WIND_URL = A('viento.webp');
      window.__PP_RELOJ_URL = A('reloj.webp');
      window.__PP_EXTRA_URL = A('extra.webp');
      window.__PP_BOMBA_URL = A('bomba.webp');   // v3.6.44: ladrillo BOMBA
      window.__PP_MAPA_URL = A('mapa.webp');
      window.__PP_TAPA_URL = A('tapa.webp');
      GUN_ART_URL = A('pistol.glb');   // v2.74: pistola REAL del artista
      CTRL = new ArcadeController(GAME);
      try { window.__PP_LOCURA = { ctrl: () => CTRL, data }; } catch (e) { /* */ }
    };
    // v2.71: la cfg del artista vive en el bloque «cfg» del manifest.json
    // (unificación con magia; data.json retirado). Fallo de red/parseo =
    // los por defecto de LOCURA_CFG siguen en pie.
    return fetch(new URL('./manifest.json', import.meta.url))
      .then((r) => (r.ok ? r.json() : null))
      .then((man) => wire(man && man.cfg))
      .catch(() => wire(null));
  },

  start() { if (CTRL) CTRL.startArcade(); },
  leave() { if (CTRL) CTRL.leave(); },

  /** v2.66/2.69: borrado TOTAL (Opciones → Reiniciar registros): claves
   *  legacy pp_arcade_* + estado vivo a cero (rank/ronda/trofeo/mapa).
   *  v3.6.33: también la pista única de la MEGA PALA (mega_hint). */
  resetRecords() {
    for (const k of ['rank', 'wins', 'streak', 'powers', 'stage', 'trophy', 'mega_hint']) {
      try { localStorage.removeItem('pp_arcade_' + k); } catch (e) { /* */ }
    }
    if (CTRL) {
      CTRL.rank = []; CTRL.wins = 0; CTRL.streak = 0;
      CTRL.powers = []; CTRL.stage = 0; CTRL.trophy = false; CTRL.round = 1;
      CTRL._replay = null;   // v2.96: fuera rejugadas colgadas
      if (CTRL.trophyGroup) CTRL.trophyGroup.visible = false;
      if (CTRL.rankPanel && CTRL.rankPanel.refresh) CTRL.rankPanel.refresh();
      if (CTRL.map && CTRL.map.refresh) CTRL.map.refresh();
    }
  },

  update(dt) { if (CTRL) CTRL.update(dt); },
  onPoint(it) { if (CTRL) CTRL.onPoint(it); },
  onMatchOver(w) { if (CTRL) CTRL.onMatchOver(w); },

  /** v2.44 (antes en el núcleo): nivel del CLOWN — Nv.2 ×1,22 · Nv.3 ×1,5.
   *  Sólo multiplica en PARTIDAS contra él (no en las pruebas). */
  aiMul() {
    const g = GAME;
    // v2.70: FIX — g.mode es 'arcade' dentro de los campeonatos; el guard
    // antiguo (g.mode !== 'match') anulaba SIEMPRE el multiplicador y los
    // niveles Nv.2/Nv.3 no eran realmente más difíciles.
    if (!CTRL || !CTRL.active || !g || g.mode !== 'arcade' ||
        g.rules.oppLabel !== 'clown') return 1;
    return [1, 1.22, 1.5][CTRL.clownLevel()] || 1;
  },

  /* ---- PRUEBAS (mismo patrón que magia; el árbitro duerme) ---- */
  serveTrigger() { if (CTRL && CTRL.arkanoid) CTRL.arkanoid.serveTrigger(); },
  reenter() { if (CTRL && CTRL.arkanoid && CTRL.arkanoid.active) CTRL.arkanoid.reenter(); },
  testActive() { return !!(CTRL && CTRL.arkanoid && CTRL.arkanoid.active); },
  testStep(dt) { if (CTRL && CTRL.arkanoid && CTRL.arkanoid.active) CTRL.arkanoid.step(dt); },

  /* v2.96 · REJUGAR etapas superadas (mapa + gatillo, vía núcleo) */
  replayMap() { return CTRL ? CTRL.replayMap() : null; },
  replayHover(idx) { if (CTRL) CTRL.replayHover(idx); },
  replayLaunch(idx) { if (CTRL) CTRL.replayLaunch(idx); },

  /* ---- PISTOLA (v2.38) y BOLA DOBLE (v2.44) — enrutados por el núcleo.
   *     (La MEGA PALA es NORMATIVA del núcleo desde v3.6.34: el módulo ya
   *     no expone megaTrigger ni pinta FX de pala.) ---- */
  get gunArmed() { return !!(CTRL && CTRL.gunArmed); },
  fireGun(i) { if (CTRL) CTRL.fireGun(i); },
  get _split() { return (CTRL && CTRL.active && CTRL._split) ? CTRL._split : null; },
  splitFilterEvents(evs) { if (CTRL) CTRL.splitFilterEvents(evs); },
  updateSplit(dt) { if (CTRL) CTRL.updateSplit(dt); },

  /** v2.66: al guardar TU NOMBRE, el ranking lateral se repinta. */
  refresh() { if (CTRL && CTRL.rankPanel) CTRL.rankPanel.refresh(); },

  /** Subtítulo de la sección CAMPEONATOS (antes: this.arcade.wins). */
  hint() { return (CTRL && CTRL.wins > 0) ? T('best_arcade', { n: CTRL.wins }) : ''; },

  /** v2.69: controles extra bajo el botón del campeonato (los dibuja el
   *  núcleo con un esquema genérico; aquí sólo se describen).
   *  v2.74 · EL MENÚ CAMPEONATOS MUESTRA SÓLO CAMPEONATOS: fuera los
   *  accesos a las PRUEBAS (ARKANOID/ARKANOID 2) — no son campeonatos y
   *  el flujo del camino ya entra SOLO en ellas (etapa impar = prueba
   *  directa; victoria en duelo = prueba en cola). Banda sonora y récord
   *  se quedan: son controles del campeonato que el artista pidió. */
  menuItems() {
    if (!CTRL || !GAME) return [];
    const items = [];
    // v2.78: la BANDA SONORA ya NO se ajusta aquí — vive en el núcleo como
    // «Música de los campeonatos (todos por igual)», PRIMERA fila de la
    // sección CAMPEONATOS del menú principal. Mismo canal de siempre
    // (pp_arcade_vol / pp_arcade_mute): el volumen de este campeonato no
    // cambia y ahora el Wizard queda ajustado por el mismo control.
    // RÉCORD (v2.34)
    items.push({
      row: 'center', color: '#ffd98a',
      text: CTRL.wins > 0 ? T('arcade_record', { n: CTRL.wins, s: CTRL.streak || 0 })
                          : T('arcade_none'),
    });
    return items;
  },

  /** v2.69: pulsaciones de los controles extra (champact:locura›<act>).
   *  v2.74: sin accesos a pruebas (arkgo/arkgo2 retirados del menú — el
   *  camino entra en ellas por sí solo).
   *  v2.78: sin «arcmus» — la música de los campeonatos se gobierna desde
   *  el ajuste GLOBAL del menú principal (case 'chmus' del núcleo). No
   *  llega ninguna acción de música: el método queda como salvaguarda. */
  menuAction(act) {
    const g = GAME;
    if (!g || !CTRL) return;
    const a = String(act || '').split(':')[1];
    if (a === 'off' || a === 'down' || a === 'up') {
      // v2.78: compatibilidad — si algo antiguo enviase «arcmus», se
      // redirige al MISMO canal global (mismo resultado que el menú nuevo).
      const A = g.audio;
      if (a === 'off') A.setArcMute(!A.arcMute);
      else if (a === 'down') A.setArcVol(A.arcVol - 0.1);
      else if (a === 'up') A.setArcVol(A.arcVol + 0.1);
      g.rules.message = T('arc_music_msg', {
        v: A.arcMute ? T('arc_music_off_word') : Math.round(A.arcVol * 100) + '%',
      });
      g.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
      g.drawMenu();
    }
  },
};
