export const DIMS = {
  tableTopY: 0.76,
  tableHalfLength: 1.37,
  tableHalfWidth: 0.7625,
  tableThickness: 0.05,
  netTopY: 0.9125,
  netHalfWidth: 0.915,
  ballRadius: 0.02,
  tableCenterZ: -1.6,
  gravity: -9.81,
  // AERODINÁMICA REAL (bola reglamentaria de 40 mm y 2,7 g):
  // arrastre cuadrático a = k·|v|·v  con k = ½·ρ·Cd·A/m (ρ=1.225, Cd=0.5)
  airDragK: 0.142,
  tableRestitution: 0.88,   // ITTF: rebote ~23 cm desde 30.5 cm (e ≈ 0.87)
  tableFriction: 0.94,
  paddleRestitution: 0.85,  // goma viva: los golpes salen con cuerpo
  bladeRadius: 0.0795,      // radio de la hoja (16 cm de diámetro)
  bladeCenterUp: 0.14,      // centro de la hoja sobre el punto de agarre
  hitAssistRadius: 0.05,    // margen generoso de detección alrededor de la hoja
  serveExtraReach: 0.09,    // margen EXTRA solo durante el saque (bola lanzada) — v2.18 más fácil
  minExitSpeed: 2.3,        // velocidad mínima de salida tras golpear (solidez)
  // v2.29: 0,08 s permitía el DOBLE GOLPE fantasma en golpeos rápidos: la
  // pala alcanzaba a la bola, la sobrepasaba y al frenar el brazo ésta
  // recruzaba el plano por DETRÁS cuando el cooldown ya había caducado ->
  // segundo "tok" y bola disparada hacia atrás. 0,24 s lo elimina (la
  // re-ida legítima de tu propio golpeo nunca baja de ~0,5 s).
  paddleHitCooldown: 0.24,
  paddleVelClamp: 12,       // v2.29: techo de velocidad de pala (picos de tracking)
  // --- r100 · CONTACTO DE REPOSO pala-bola (el estándar Eleven) ---
  // Petición del dueño tras V3.6.91: «si paramos la bola sobre la pala su
  // movimiento va a trompicones… y si levanto la pala la bola la atraviesa y
  // desaparece. Eleven rueda y se desliza sobre la superficie». El reposo
  // NO toca los golpes (por debajo de este umbral no llega ningún swing):
  // la física de golpes, el golden y la IA quedan byte a byte intactos.
  paddleRestSpeed: 0.65,    // vRelN <= esto al llegar = APOYO (no golpe, sin rebote)
  paddleRestSpeedPad: 0.95, // umbral APLICADO con la pala lenta (posar la bola
                            // desde 3-4 cm de caída llega a ~0,9 m/s) — un
                            // bloqueo real con la pala quieta a <0,9 m/s es
                            // exactamente eso: posar la bola (estándar Eleven)
  paddleRestFric: 0.38,     // fricción tangencial por re-contacto (deslizar/rodar)
  paddleRestMuS: 0.35,      // fricción estática: gravedad tangencial menor no desliza
  paddleRestDrop: 0.09,     // s de edad del apoyo sin re-confirmar antes de soltar
  paddleRestCarry: 0.5,     // pala más lenta que esto ARRASTRA la bola apoyada
  paddleRestBounce: 0.35,   // fricción (Coulomb suavizado) del apoyo en un bote suave
  maxBallSpeed: 14,
  // --- efecto (spin) ---
  magnus: 0.0035,           // a = Cm·(ω × v)
  bounceSpinKick: 0.012,
  spinImpulse: 10,
  spinMax: 110,             // ≈ 1.050 rpm
  spinDecayAir: 0.3,
  paddleWristSpin: 0.16,    // contribución de la rotación de la muñeca
  // --- v3.0.5-FIS1 · FÍSICA VIVA ---------------------------------------
  // Interruptores maestros: 0 = comportamiento EXACTO de v2.x (legacy),
  // 1 = modelos de contacto reales (por defecto). Rollback instantáneo.
  physicsRealism: 1,        // P1 golpe vivo + P2 bote físico slip-coupled
  paddlePerks: 1,           // PALAS CON CARÁCTER: las skins del entrenamiento
                            // modulan la goma del jugador (0 = todas neutras)
  // --- v3.0.7-PLAY1 · PRO CIRCUITO -------------------------------------
  // Gamificación del PRO TRAINING como CAPA de lectura (combos, estrellas,
  // precisión, logros, celebración): NUNCA toca juez, física ni feeds.
  // 0 = modo puro profesional (solo puntos y récords, como siempre).
  trainGamify: 1,
  // P1 · goma (contacto pala-bola) — impulso tangencial con I de cascarón:
  rubberGrip: 0.45,         // agarre de la goma (1 = frenaría el deslizamiento entero)
  // v3.6.36 · SÚPER EFECTO (poder de pala): amplificación del Magnus en
  // vuelo, del acople giro-mesa al botar y del tope de rotación — SOLO
  // para la bola MARCADA (ball.ppEfecto: sale del golpe del jugador con
  // el poder activo). Sin marca, multiplicador 1: física idéntica.
  // v3.6.43 (ronda 51 · el dueño: «no noto los efectos… es preciso
  // exagerarlo para que visualmente veamos el resultado»): TODO el bloque
  // del Súper Efecto sube un escalón — brush ×3 y curva ×2,2 en vuelo
  // (SIEMPRE solo en la bola marcada; sin poder: física igual).
  // v3.6.49 (ronda 57): efectoBoteMul (acople del bote ×2,4) RETIRADO —
  // el dueño: «la ventaja del efecto en los botes sólo es para el jugador,
  // el perjudicado siempre es el rival»: un bote amplificado dependía del
  // giro real y podía salir amable y favorecer AL RIVAL. La ventaja en
  // los botes es hoy SÓLO la firma tipificada (abajo), que siempre castiga.
  efectoSpinTope: 3,        // tope de rotación = 3 × spinMax (antes ×2)
  efectoMagnusMul: 2.2,     // Magnus ×2,2 en vuelo (antes ×1,5: curva VISIBLE)
  // v3.6.46 (ronda 54 · el dueño redefine el SÚPER EFECTO: la estela se
  // retira y el efecto pasa a ser REAL según el movimiento de la pala al
  // golpear): el brush se CLASIFICA en tres spins y el BOTE traduce cada
  // uno con su firma exacta — topspin sale muy acelerado hacia delante y
  // bajo, backspin casi se PARA, sidespin exagera el desvío hacia el lado
  // del barrido. Constantes calibrables (una fuente de verdad por regla).
  efectoTipoUmbral: 0.55,    // barrido mínimo (m/s) para clasificar el tipo
  efectoBoteTopAvance: 1.55, // TOPSPIN: horizontal tras el bote ×1,55 (+0,4 m/s de piso)
  efectoBoteTopVy: 0.62,     // TOPSPIN: bote BAJO (vy tras el bote ×0,62)
  efectoBoteBackH: 0.16,     // BACKSPIN: horizontal ×0,16 (prácticamente se para)
  efectoBoteBackVy: 0.32,    // BACKSPIN: vy ×0,32 (saltito mínimo)
  efectoBoteBackFx: 0.35,    // BACKSPIN: también frena el componente lateral (x ×0,35)
  efectoBoteSideKick: 0.42,  // SIDESPIN: patada lateral = 0,42 × |vz| (piso 0,45 m/s)
  efectoBoteSideMax: 1.5,    // SIDESPIN: tope de la patada lateral (m/s)
  // v3.6.37 · SÚPER EFECTO NOTORIO (petición del dueño): el rival SUFRE la
  // bola marcada — «dificultar en un %» su éxito de impacto. Dos palancas
  // (solo con la bola marcada viniendo; sin poder: 1 = IA idéntica):
  efectoRivalErrMul: 2.0,   // error de puntería de la IA ×2 al sortear la bola
  efectoRivalVel: 0.85,     // piernas de la IA ×0,85 (−15 % de velocidad)
  // v3.6.41 · SÚPER PORTAL (4.º poder; penalización honesta al rival IA,
  // petición del dueño: «deberá penalizarlo para que le resulte más
  // complicado acertar el golpe»). Solo con la bola marcada viniendo
  // (ball.ppPortal, el portal del jugador); sin poder: IA idéntica.
  portalRivalErrMul: 1.6,   // error de puntería de la IA ×1,6 tras el portal
  portalRivalVel: 0.75,     // piernas de la IA ×0,75 mientras sufre el portal
  portalMissExtra: 0.10,    // +10 % de fallo decidido (golpe torpe extra)
  // v3.6.37 · SÚPER IMÁN (3.er poder; parámetros PROTOTIPO del dueño, a
  // calibrar con las velocidades reales — NO son física de imán real):
  // campo que atrae SUAVE la bola al punto dulce de la pala del jugador.
  // v3.6.43 (ronda 51 · el dueño: «ampliar un poco el radio de influencia…
  // si la bola entra dentro del mismo… indicando que está siendo atraída…
  // permite que una bola que se nos escapa la atraigamos hacia la pala»):
  // el campo crece (radio 0,45→0,75 m, plena 0,12→0,20), empuja MÁS fuerte
  // y gana el RESCATE (imanRescate*): bolas que NO se acercan a la pala
  // (se van largas/cruzadas) son atraídas de verdad hacia el punto dulce.
  // v3.6.44 (ronda 52 · el dueño: «el Super iman no hace nada, no se ve
  // efecto ni se nota nada sobre la pala»): el campo CRECE otra vez y empuja
  // MÁS FUERTE — radio 0,75→0,95 m (la bola entra en el campo mucho antes),
  // plena 0,26, acel 6,5 m/s² y Δv 0,80; el RESCATE de bolas escapadas sube
  // a 7,5 m/s² / 1,05 m/s (la bola cruzada CURVA hacia la pala a la vista).
  imanRadio: 0.95,          // radio de influencia del campo (m; antes 0,75)
  imanPlena: 0.26,          // distancia de máxima asistencia (plena dentro)
  imanAcelMax: 6.5,         // aceleración lateral máxima (m/s²; antes 5)
  imanDvMax: 0.80,          // incremento lateral máximo POR APROXIMACIÓN (m/s)
  imanTPred: 0.15,          // horizonte máximo de predicción del impacto (s)
  imanRescateAcel: 7.5,     // (heredado r52 — applyIman ya no lo usa; se
  imanRescateDv: 1.05,      //  conserva para rollback instantáneo)
  // v3.6.49 (ronda 57 · el dueño redefine OTRA VEZ el SÚPER IMÁN: «olvide-
  // mos el efecto anterior de atracción y ralentización»): GUÍA DE TIRO —
  // cada golpe del jugador con la ventana viva y dirección hacia la mitad
  // rival se CORRIGE para botar SIEMPRE en la mesa del rival (solver de
  // la casa, despeje de red garantizado) y sale reforzado: golpes muy
  // fuertes y a gran velocidad. El gancho/freno de r54-r56 (imanGancho*,
  // imanFreno*) queda RETIRADO — sin campo por subpaso.
  imanAimVzMin: -0.4,       // sólo tiros que YA van hacia la mitad rival (m/s)
  imanAimProfundidad: 0.62, // objetivo: 62 % de la media mesa rival (bote seguro)
  imanAimPisoVel: 9.5,      // piso de potencia del golpe guiado (m/s) — «muy fuertes»
  imanAimEmpuje: 1.2,       // empuje sobre la velocidad real del golpe (×)
  imanAimTopeFrac: 0.8,     // tope honesto: 0,8 × maxBallSpeed (m/s)
  rubberMu: 0.55,           // tope de Coulomb: |Δv tangencial| ≤ mu·(1+e)·|vRelN|
  edgeRestLoss: 0.35,       // PUNTO DULCE: el canto pega sordo, rest × (1 − loss·offC²)
  edgeSpinLoss: 0.45,       // el canto imprime menos efecto
  edgeJitter: 0.4,          // bamboleo disperso cerca del canto (m/s)
  // P2 · bote (contacto mesa-bola, compartido por física/IA/solver de saque):
  bounceGripMin: 0.22,      // agarre de la mesa con impacto suave
  bounceGripMax: 0.60,      // agarre con impacto fuerte (~4,5 m/s): patea más
  // --- saque (regla ITTF relajada v2.18: varios usuarios lo encuentran duro) ---
  // v2.44: lanzamiento libre aún más generoso (casi cualquier toss vale)
  tossMinRise: 0.035,       // lanzamiento mínimo ~3,5 cm
  serveEndLineTol: 0.45,    // margen tras la línea de fondo (muy indulgente)
  serveAssistVy: 3.1,       // vy mínimo del saque asistido (toss más alto = más tiempo para golpear)
  // --- sala ---
  roomHalfX: 3.05,
  roomBackZ: 2.35,
  roomFrontZ: -5.55,
  roomHeight: 2.85,
};
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import * as THREE from 'three';
/* DEPS-FASE2-FIN */

export const AI_PRESETS = {
  easy:   { maxSpeed: 2.0, accel: 6,  errStd: 0.09,  missBase: 0.15, minT: 0.62, maxT: 0.88, maxShotSpeed: 4.8, predictInterval: 0.16, smash: 0.04, short: 0.03 },
  medium: { maxSpeed: 2.7, accel: 9,  errStd: 0.05,  missBase: 0.08, minT: 0.52, maxT: 0.78, maxShotSpeed: 6.2, predictInterval: 0.10, smash: 0.15, short: 0.05 },
  hard:   { maxSpeed: 3.8, accel: 14, errStd: 0.024, missBase: 0.03, minT: 0.42, maxT: 0.62, maxShotSpeed: 10,  predictInterval: 0.06, smash: 0.30, short: 0.06 },
};

/* v3.0.9-HALL1 · ASISTENCIA DEL SAQUE POR DIFICULTAD — el pilar «sentirse
 * dueño del juego» escala con la CPU elegida: en FÁCIL el saque perdona
 * (más ayuda), en DIFÍCIL casi no endereza (el saque es TUYO). Palancas
 * (v3.1.0-SRV2): reach = margen extra de contacto mientras la bola del
 * lanzamiento vuela (REBAJADO: la tolerancia no puede crear golpes a
 * distancia — la CCD fina es la que garantiza el contacto real), vy =
 * subida mínima del saque asistido SOLO con el gatillo (soltar el grip es
 * SIEMPRE el gesto real), angleMul/assistMul = margen angular e intensidad
 * de la asistencia progresiva (v3.1.0-SRV2). La legalidad NO cambia:
 * tossMinRise y línea de fondo son reglas, no asistencia. */
export const SERVE_ASSIST_TIERS = {
  easy:   { reach: 0.060, vy: 3.5,  angleMul: 1.4,  assistMul: 1.35 },
  medium: { reach: 0.045, vy: 3.10, angleMul: 1.0,  assistMul: 1.0  },
  hard:   { reach: 0.028, vy: 2.70, angleMul: 0.7,  assistMul: 0.6  },
};

/* =====================================================================
 *  v3.1.0-SRV2 · SAQUE VR REALISTA CON ASISTENCIA LIMITADA — parámetros
 *  del requisito del dueño (F: todo configurable). Filosofía:
 *    · El IMPULSO sale SIEMPRE del modelo de contacto real (collidePaddle:
 *      orientación real de la cara, velocidad lineal+angular, restitución,
 *      fricción, punto dulce). NUNCA se sustituye por una velocidad ideal.
 *    · La tolerancia de contacto es PEQUEÑA (compensa el tracking, no
 *      inventa golpes a distancia) y la CCD fina (TOI en 2 pasadas con el
 *      plano interpolado) hace que el contacto REAL no se pierda nunca.
 *    · La asistencia es PROGRESIVA y ACOTADA: mezcla hacia una referencia
 *      legal sólo si la salida real queda dentro de un margen angular
 *      pequeño, con peso que decae linealmente hasta 0 en el margen. Un
 *      saque claramente mal orientado NO se convierte en válido jamás.
 *    · La VALIDACIÓN es del árbitro (rules): bote propio → bote rival →
 *      LET/falta con la trayectoria REAL post-impacto.
 *  window.__ppDebug.serveTune expone este objeto VIVO: se puede ajustar
 *  desde la consola sin reconstruir (QA y puesta a punto en casco).
 * ===================================================================== */
export const SERVE_TUNE = {
  // --- B · tolerancias de contacto (CCD bola-pala) ---
  skin: 0.02,             // margen normal del plano de la hoja (antes 0.03 fijo)
  skinServe: 0.022,       // margen normal EXTRA durante el vuelo del saque (antes +0.045)
  assistInPlane: 0.05,    // radio de asistencia en el plano de la hoja (rally, = hitAssistRadius)
  serveFlightAssist: 0.032, // radio en el plano durante el vuelo del saque (antes heredaba 0.05)
  serveMinExit: 0.65,     // suelo de salida tras un roce en saque (m/s); el rally mantiene minExitSpeed
  // --- C/D · asistencia progresiva acotada ---
  assistAngle: 0.30,      // margen angular a plena asistencia en MEDIUM (rad ≈ 17°) × tier.angleMul
  assistMax: 0.35,        // mezcla máxima hacia la referencia legal con error → 0 (medium) × tier.assistMul
  assistMinSpeed: 1.2,    // por debajo de esta salida (m/s) no hay asistencia: un roce es un roce
  // --- A · filtrado de velocidad de la mano (updatePaddleSim) ---
  velWindow: 0.045,       // ventana de la media móvil (s) — antes VEL_WINDOW fijo
  velLerp: 0.85,          // respuesta del filtro — antes lerp fijo
  // --- E · límites post-impacto del saque ---
  serveMaxSpeed: 8.8,     // techo del saque (antes fijo)
  serveMinSpeed: 0,       // suelo del saque: 0 = DESACTIVADO (antes 3.2 forzados: disfrazaba roces)
  // --- v3.1.1-FEEL1 · game-feel (requisito del dueño) ------------------
  // Ajuste 1 · GRACE del saque: un cruce «muy justo» que se va por el borde
  // de la hoja no se pierde — durante unos ms (SOLO en el vuelo del saque)
  // la detección sigue viva por si la hoja, que sigue barriendo, alcanza a
  // la bola. Ventana corta y acotada: no inventa golpes a distancia.
  lateMs: 14,             // ventana de gracia (ms): «unos milisegundos» más de detección
  lateInPlane: 0.02,      // margen extra EN EL PLANO durante la gracia (m)
  lateSkin: 0.012,        // margen normal extra durante la gracia (m)
  // Ajuste 2 · el suelo de salida es de los GOLPES, no del rebote: con la
  // pala quieta NO hay suelo (los botes decaen con su restitución natural
  // hasta pararse); con swing real el suelo pleno de 2,3 m/s sigue íntegro.
  exitFloorFrom: 0.15,    // velocidad de pala donde el suelo empieza a aplicar (m/s)
  exitFloorTo: 1.0,       // velocidad de pala con suelo completo (m/s)
  restPadSpeed: 0.45,     // pala «quieta»: el contacto de reposo ignora el cooldown
  restEventMin: 0.35,     // bajo este |vRelN| el contacto NO emite evento (ni audio ni árbitro)
  debug: 1,               // 1 = registra el último saque en window.__ppDebug.lastServe
};

/** Escala un preset de IA por un factor de habilidad k (0,7…2,2):
 *  k > 1 → más rápida, precisa y agresiva; k < 1 → más lenta y falona.
 *  Se usa para la IA ADAPTATIVA (según el marcador) y el modo SUPERVIVENCIA
 *  (la CPU acelera rallye a rallye). Devuelve un preset NUEVO. */
export function scalePreset(cfg, k) {
  const kk = THREE.MathUtils.clamp(k, 0.7, 2.2);
  return {
    maxSpeed: cfg.maxSpeed * THREE.MathUtils.clamp(kk, 0.55, 1.9),
    accel: Math.min(30, cfg.accel * Math.pow(kk, 1.4)),
    errStd: cfg.errStd / Math.max(0.6, Math.pow(kk, 0.8)),
    missBase: THREE.MathUtils.clamp(cfg.missBase * Math.max(0.25, 2 - kk), 0.005, 0.45),
    minT: THREE.MathUtils.clamp(cfg.minT / Math.max(0.6, Math.pow(kk, 0.5)), 0.24, 1.0),
    maxT: THREE.MathUtils.clamp(cfg.maxT / Math.max(0.6, Math.pow(kk, 0.5)), 0.4, 1.3),
    maxShotSpeed: cfg.maxShotSpeed * THREE.MathUtils.clamp(kk, 0.5, 1.8),
    predictInterval: cfg.predictInterval / Math.max(0.6, Math.pow(kk, 0.8)),
    smash: THREE.MathUtils.clamp(cfg.smash * Math.max(0.5, kk), 0.01, 0.75),
    short: cfg.short,
  };
}

export const COLORS = {
  tableBlue: 0x17539e, tableEdge: 0x0e3a73, frame: 0x22262b,
  floor: 0x37302b, wall: 0x1a1e23,
  ball: 0xfff8ef, accentAmber: 0xe8b45a, accentGreen: 0x7fb069,
};

/* =====================================================================
 *  r95 · MESA (AJUSTES › SALA Y ESCENA › MESA) — altura y aspecto.
 *  La altura MUTA DIMS.tableTopY/netTopY (una sola fuente de verdad:
 *  física, IA, saque y escena la leen EN VIVO) y la mesa viva se
 *  reacomoda con relayoutMesa() (c07). El aspecto tiñe ppTableTop y el
 *  marco (ppTableApron/ppTableLeg comparten material). 3 opciones por
 *  defecto + 2 bloqueadas que se liberan con RECOMPENSAS (victorias y
 *  racha del Hall — ver _mesaLibre en el juego).
 * ===================================================================== */
export const MESA_ALTOS = [
  { id: 'baja', y: 0.70, nameKey: 'mesa_alto_baja' },
  { id: 'normal', y: 0.76, nameKey: 'mesa_alto_normal' },
  { id: 'alta', y: 0.84, nameKey: 'mesa_alto_alta' },
];
/* r96 · RANGO CONTINUO del DESLIZADOR de altura (AJUSTES › SALA Y ESCENA ›
 * MESA): la mesa ya no elige entre 3 presets — un raíl ajusta el tablero
 * entre Baja (0,70) y Alta (0,84) con PASO FINO de 1 cm y feedback en vivo
 * (la mesa de la sala de partidos sube y baja al mover el deslizador).
 * MESA_ALTOS se conserva como extremos/zonas de referencia y para la
 * compatibilidad (QA y migración del ajuste antiguo pp_mesaalto). */
export const MESA_ALTO_MIN = 0.70;
export const MESA_ALTO_MAX = 0.84;
export const MESA_ASPECTOS = [
  { id: 'azul', top: 0x17539e, edge: 0x0e3a73, lock: null, nameKey: 'mesa_asp_azul' },
  { id: 'verde', top: 0x1c6b47, edge: 0x125033, lock: null, nameKey: 'mesa_asp_verde' },
  { id: 'neon', top: 0x8a2be2, edge: 0x5b1c9e, lock: null, nameKey: 'mesa_asp_neon' },
  { id: 'oro', top: 0xc9932f, edge: 0x8f6a1e, lock: 'wins10', nameKey: 'mesa_asp_oro' },
  { id: 'carbon', top: 0x171a20, edge: 0x0d0f13, lock: 'streak5', nameKey: 'mesa_asp_carbon' },
];
/** Altura de red REGLAMENTARIA sobre la mesa (15,25 cm — ITTF). */
export const MESA_NET_H = 0.1525;

/* =====================================================================
 *  TEMAS DE SALA (v2.14): ambientes visuales intercambiables al vuelo.
 *  Cada tema redefine suelo/paredes/techo/paneles de luz/tira LED/rejilla,
 *  las tres luces de la escena, el fondo y la niebla. La mesa, las vallas
 *  LED y la bola NO cambian (legibilidad del juego).
 *  Ciclo en VR: flick LATERAL del stick (los ejes están libres; el click
 *  de stick ya es dificultad, B modo, A/X mano de la pala — v2.78: la tecla
 *  Y queda ANULADA, ya no lanza el entrenamiento).
 * ===================================================================== */
export const ROOM_THEMES = [
  {
    key: 'pabellon', name: 'Pabellón', nameKey: 'theme_pabellon', emoji: '🏓',
    floor: 0x37302b, gridC: 0x4a4038, gridG: 0x2c2622,
    wall: 0x1a1e23, ceil: 0x14171b, panel: 0xf5efe2,
    strip: 0xe8b45a, ring: 0xe8b45a,
    bg: 0x0b0e11, fogNear: 9, fogFar: 18,
    hemiSky: 0xffe6c4, hemiGround: 0x35271b, hemiInt: 0.95,
    dirCol: 0xfff1dc, dirInt: 2.4, spotCol: 0xffe2b8, spotInt: 0.5,
    envInt: 0.75,
  },
  {
    key: 'neon', name: 'Neón', nameKey: 'theme_neon', emoji: '💜',
    floor: 0x10121f, gridC: 0x2b3f8f, gridG: 0x181d3a,
    wall: 0x0a0c16, ceil: 0x05060d, panel: 0xbfe3ff,
    strip: 0x35f0ff, ring: 0xff3fa4,
    bg: 0x04050b, fogNear: 10, fogFar: 20,
    hemiSky: 0x8ab5ff, hemiGround: 0x0a0e1a, hemiInt: 0.7,
    dirCol: 0xbfd4ff, dirInt: 1.7, spotCol: 0x57c7ff, spotInt: 0.75,
    envInt: 0.45,
  },
  {
    key: 'atardecer', name: 'Atardecer', nameKey: 'theme_atardecer', emoji: '🌅',
    floor: 0x4a3527, gridC: 0x7a5136, gridG: 0x402c1e,
    wall: 0x3a2430, ceil: 0x241a22, panel: 0xffd9a8,
    strip: 0xff8a5c, ring: 0xffb070,
    bg: 0x1a0f14, fogNear: 9, fogFar: 18,
    hemiSky: 0xffc08a, hemiGround: 0x4a2330, hemiInt: 1.0,
    dirCol: 0xffb070, dirInt: 2.1, spotCol: 0xff9a6a, spotInt: 0.6,
    envInt: 0.8,
  },
  {
    key: 'artico', name: 'Ártico', nameKey: 'theme_artico', emoji: '❄️',
    floor: 0x2e3a42, gridC: 0x55707f, gridG: 0x2c3a44,
    wall: 0x1c2830, ceil: 0x111a20, panel: 0xffffff,
    strip: 0x8fd3e8, ring: 0xbfe3ff,
    bg: 0x0d1418, fogNear: 9, fogFar: 19,
    hemiSky: 0xeaf4ff, hemiGround: 0x2a3a44, hemiInt: 1.0,
    dirCol: 0xffffff, dirInt: 2.3, spotCol: 0xdff0ff, spotInt: 0.55,
    envInt: 0.85,
  },
  /* r97 · TEMA NOCTURNA — sala DESBLOQUEABLE con las estrellas de los
   * RETOS SEMANALES (lock stars4): la recompensa visual que los retos
   * «alimentan». Azul medianoche, luz de luna fría y niebla corta. */
  {
    key: 'nocturna', name: 'Nocturna', nameKey: 'theme_nocturna', emoji: '🌙',
    floor: 0x141a24, gridC: 0x26334a, gridG: 0x11161f,
    wall: 0x0d1119, ceil: 0x090c12, panel: 0xd9e8ff,
    strip: 0x6f9fe8, ring: 0x9fc4ff,
    bg: 0x04060a, fogNear: 8, fogFar: 16,
    hemiSky: 0xbcd4ff, hemiGround: 0x0e1622, hemiInt: 0.72,
    dirCol: 0xd6e5ff, dirInt: 2.0, spotCol: 0xa8c8ff, spotInt: 0.5,
    envInt: 0.62,
    lock: 'stars4',
  },
];

// Montura de la pala sobre el mando (espacio "grip" de WebXR):
//  · -Z_grip sale por la parte alta del mando siguiendo el mango -> la HOJA
//    continúa la línea del mango: el AGARRE DEL MANDO COINCIDE con el AGARRE
//    DE LA PALA (punto de agarre en el origen del grip, sin desplazamientos).
//  · La cara queda casi vertical (roll ≈83° desde la cara del pulgar), la
//    postura natural de preparación; espejo para la mano izquierda.
const PALA_MOUNT_ROLL = Math.PI / 2 - 0.12;
function makeMountQuat(roll) {
  const pitch = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2);
  const rollQ = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), roll);
  return new THREE.Quaternion().multiplyQuaternions(rollQ, pitch);
}
export const MOUNT_QUAT_RIGHT = makeMountQuat(PALA_MOUNT_ROLL);
const MOUNT_QUAT_LEFT = makeMountQuat(-PALA_MOUNT_ROLL);
export const mountQuatFor = (hand) => (hand === 'left' ? MOUNT_QUAT_LEFT : MOUNT_QUAT_RIGHT);
const UP = new THREE.Vector3(0, 1, 0);

/* =====================================================================
 *  AUDIO · sintetizado con Web Audio (sin assets externos)
 * ===================================================================== */

/* ----- v2.20/2.27 · PLAN DE VOZ del megáfono --------------------------
 * Cada anuncio del juego se traduce a una secuencia de fragmentos del
 * banco de voz (VOICE_B64 castellano / VOICE_B64_EN inglés — MISMAS
 * claves, distinto audio). Los patrones de texto dependen del idioma
 * activo (TLang()): VOICE_FULL/VOICE_ACH por idioma. Claves NORMALIZADAS
 * (minúsculas, sin acentos ni signos).
 * -------------------------------------------------------------------- */
