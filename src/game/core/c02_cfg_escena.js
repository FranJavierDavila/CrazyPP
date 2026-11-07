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
  // r113 · FÍSICA DEL GOLPE FUERTE (petición del dueño: «la velocidad de
  // los golpes fuertes no es real, tiene que dar velocidad real según la
  // fuerza»): el techo 12 recortaba los swings ENÉRGICOS de verdad (un
  // smash de brazo supera 12 m/s con facilidad) y la bola salía débil.
  // 16 mantiene la guarda anti-picos de tracking (picos de 30+ m/s de un
  // frame siguen recortándose) pero deja pasar el swing real.
  paddleVelClamp: 16,       // r113: antes 12 — el smash real ya no se recorta
  // --- r100/r101 · CONTACTO DE REPOSO pala-bola (el estándar Eleven) ---
  // Petición del dueño: «si paramos la bola sobre la pala va a trompicones…
  // y si levanto la pala la bola la atraviesa». r100 lo implementó con
  // umbral dual 0,95/0,65 y el dueño lo devolvió: con 0,95 la pala
  // SECUESTRABA los botes legítimos (botar la bola sobre la pala moría
  // al tercer toque y las llegadas suaves quedaban pegadas). r101:
  // umbral ÚNICO 0,25 m/s — sólo se posa una bola REALMENTE quieta (el
  // redil de gravedad por frame a 72 Hz es ~0,14 m/s: la bola apoyada
  // re-captura en silencio cada frame, sin trompicones) y CUALQUIER
  // bote con vida (>0,25) BOTA con la física de golpe de siempre.
  paddleRestSpeed: 0.25,    // vRelN <= esto al llegar = APOYO (no golpe, sin rebote)
  paddleRestFric: 0.38,     // fricción tangencial por re-contacto (deslizar/rodar)
  paddleRestMuS: 0.35,      // fricción estática: gravedad tangencial menor no desliza
  paddleRestDrop: 0.09,     // s de edad del apoyo sin re-confirmar antes de soltar
  paddleRestCarry: 0.5,     // pala más lenta que esto ARRASTRA la bola apoyada
  // r113 · techo de bola sube con el techo de pala: un golpe fuerte AHORA
  // se siente fuerte (hasta 18 m/s ≈ 65 km/h, rango de un smash amateur
  // real). El validador del duelo online (c09b) no impone techo de
  // velocidad (sólo de giro MAX_SPIN) — cambio seguro para online.
  maxBallSpeed: 18,
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
  // r113 · FÍSICA DEL GOLPE FUERTE: ventana y lerp más rápidos — el pico
  // REAL del swing llega al contacto en lugar de promediarse (la ventana
  // 0,045 + lerp 0,85 retrasaban y achataban los golpes fuertes: la bola
  // salía con la velocidad de hace 45 ms, no con la de ahora). El filtro
  // sigue amortiguando el jitter (3 muestras a 72 Hz ≈ 42 ms → 2-3 muestras).
  velWindow: 0.032,       // r113: antes 0,045 — menos lag del filtro
  velLerp: 0.90,          // r113: antes 0,85 — respuesta más ágil
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

/* =====================================================================
 *  M4 (r118) · ELO — el número ÚNICO de habilidad (roadmap MEJORAS.md M4)
 *  ELO_CPU: el valor de referencia de cada preset de la CPU — ancla la
 *  matemática GANAR/PERDER (recordMatch) y el MATCHMAKING (propuesta de
 *  rival cerca de tu nivel). r109 (PWA) ya reservaba la página 'rank';
 *  esto es la base numérica local, sin servidor nuevo.
 * ===================================================================== */
export const ELO_CPU = { easy: 900, medium: 1050, hard: 1200 };

/** M4 · MATCHMAKING LOCAL POR ELO — rival propuesto cerca de tu nivel con
 *  variedad. Dado tu ELO y un jitter en ±120 (la VARIEDAD: cada propuesta
 *  es distinta), elige el preset por bandas y afina con scalePreset:
 *    bandas   <975 easy · <1125 medium · resto hard (los saltos de preset
 *             ya son grandes; k sólo afina dentro de la banda)
 *    k        10^((objetivo − base del preset)/400) acotado a [0.7, 1.6]
 *             (1.6 y no 2.2: el matchmaking nunca propone un muro)
 *  Devuelve {preset, k, elo} — elo = objetivo REAL tras el clamp de k.
 *  FUNCIÓN PURA (testable sin instancia de juego: qa_r118_dirigida). */
export function rivalPorElo(elo, jitter) {
  const j = THREE.MathUtils.clamp(Number(jitter) || 0, -120, 120);
  const objetivo = THREE.MathUtils.clamp(Math.round(elo + j), 400, 2000);
  const preset = objetivo < 975 ? 'easy' : objetivo < 1125 ? 'medium' : 'hard';
  const base = ELO_CPU[preset];
  const k = THREE.MathUtils.clamp(Math.pow(10, (objetivo - base) / 400), 0.7, 1.6);
  return { preset, k, elo: Math.round(base + 400 * Math.log10(k)) };
}

// M4 · gancho de tests (patrón __PP_WORLD/__PP_WRL_BADGE: visible para QA)
try { if (typeof window !== 'undefined') window.__PP_ELO = { rivalPorElo, ELO_CPU, AI_PRESETS }; } catch { }

/* =====================================================================
 *  M5a (r112) · IA CON ESTILOS — 12 PERSONALIDADES sobre la MISMA física.
 *  Cada estilo = multiplicadores ACOTADOS sobre la cfg ya escalada
 *  (dificultad × adaptativo × supervivencia) + colocación (zIdle/bias,
 *  el mismo canal que la personalidad de campeonato desde r95) + celebración.
 *  SIN TRAMPAS: la velocidad final sigue clamped por el solver legal, el
 *  error vive en ±55 % como mucho, minT/maxT y smash nunca salen de rango
 *  y las palas IA siguen ancladas a su mitad (invariante I3 del arnés).
 *  'clasico' = null en mul → comportamiento EXACTO de siempre (los arneses
 *  deterministas no tocan pp_estilo_v1: sus hashes quedan intactos).
 *  ===================================================================== */
export const OPPONENT_STYLES = [
  { id: 'clasico', es: 'Clásico', en: 'Classic',
    esSub: 'El rival de siempre', enSub: 'The usual rival',
    mul: null, zIdle: 0, bias: 0, celeb: 0.6 },
  { id: 'looper', es: 'Looper', en: 'Looper',
    esSub: 'Lifta desde lejos', enSub: 'Topspin from deep',
    mul: { speed: 0.95, err: 1.18, miss: 1.1, pred: 1.1, accel: 0.9, smash: 0.55, tLo: 1.08, tHi: 1.12 },
    zIdle: 0.34, bias: 0.02, celeb: 0.8 },
  { id: 'chopero', es: 'Chopero', en: 'Chopper',
    esSub: 'Cortada profunda y paciencia', enSub: 'Deep chop and patience',
    mul: { speed: 0.88, err: 0.92, miss: 0.88, pred: 1.15, accel: 0.85, smash: 0.4, tLo: 1.15, tHi: 1.2 },
    zIdle: 0.26, bias: 0.04, celeb: 0.45 },
  { id: 'bloqueador', es: 'Bloqueador', en: 'Blocker',
    esSub: 'Pegado a la mesa, reflejos', enSub: 'Glued to the table, reflexes',
    mul: { speed: 0.85, err: 0.85, miss: 0.8, pred: 0.85, accel: 1.3, smash: 0.9, tLo: 0.95, tHi: 0.9 },
    zIdle: -0.30, bias: 0.03, celeb: 0.5 },
  { id: 'atacante', es: 'Atacante', en: 'Attacker',
    esSub: 'Smash a la primera', enSub: 'Smash on sight',
    mul: { speed: 1.15, err: 1.28, miss: 1.22, pred: 1.0, accel: 1.12, smash: 2.1, tLo: 0.85, tHi: 0.8 },
    zIdle: -0.22, bias: 0.06, celeb: 1 },
  { id: 'defensivo', es: 'Defensivo', en: 'Defender',
    esSub: 'Bolas altas desde el fondo', enSub: 'High balls from the back',
    mul: { speed: 0.92, err: 1.08, miss: 1.05, pred: 1.05, accel: 0.95, smash: 0.35, tLo: 1.25, tHi: 1.3 },
    zIdle: 0.36, bias: 0.0, celeb: 0.35 },
  { id: 'dejadas', es: 'Dejadas', en: 'Drop-shot',
    esSub: 'Juego corto y maña', enSub: 'Short game and guile',
    mul: { speed: 0.9, err: 1.12, miss: 1.08, pred: 1.0, accel: 1.05, smash: 0.5, tLo: 0.72, tHi: 0.75 },
    zIdle: -0.06, bias: -0.10, celeb: 0.7 },
  { id: 'allround', es: 'All-round', en: 'All-round',
    esSub: 'Equilibrio total', enSub: 'Total balance',
    mul: { speed: 1.0, err: 0.95, miss: 0.95, pred: 1.0, accel: 1.0, smash: 1.0, tLo: 1.0, tHi: 1.0 },
    zIdle: 0.05, bias: 0.0, celeb: 0.6 },
  { id: 'nervioso', es: 'Joven nervioso', en: 'Nervous youth',
    esSub: 'Rápido pero desordenado', enSub: 'Fast but scatterbrained',
    mul: { speed: 1.1, err: 1.55, miss: 1.4, pred: 1.2, accel: 1.45, smash: 1.2, tLo: 1.0, tHi: 1.05 },
    zIdle: 0.0, bias: 0.02, celeb: 0.9 },
  { id: 'veterano', es: 'Veterano frío', en: 'Cold veteran',
    esSub: 'Nunca falla dos veces', enSub: 'Never misses twice',
    mul: { speed: 0.98, err: 0.68, miss: 0.7, pred: 1.15, accel: 0.85, smash: 0.8, tLo: 1.0, tHi: 1.0 },
    zIdle: 0.08, bias: 0.03, celeb: 0.25 },
  { id: 'gigante', es: 'Gigante', en: 'Giant',
    esSub: 'Alcance descomunal', enSub: 'Huge reach',
    mul: { speed: 0.9, err: 0.88, miss: 0.9, pred: 1.05, accel: 0.88, smash: 0.9, tLo: 1.0, tHi: 1.0 },
    zIdle: 0.10, bias: 0.16, celeb: 0.55 },
  { id: 'relampago', es: 'Relámpago', en: 'Lightning',
    esSub: 'Pequeño y velocísimo', enSub: 'Small and blazing fast',
    mul: { speed: 1.05, err: 1.22, miss: 1.18, pred: 0.78, accel: 1.6, smash: 1.1, tLo: 0.9, tHi: 0.85 },
    zIdle: -0.10, bias: 0.0, celeb: 1 },
];

/** M5a (r112) · aplica los multiplicadores de un estilo a una cfg YA
 *  escalada (dificultad × adaptativo × supervivencia). Devuelve una cfg
 *  NUEVA; con estilo nulo (o 'clasico') devuelve la cfg INTACTA. Todos los
 *  campos quedan clamped a los rangos legales de scalePreset/AI_PRESETS. */
export function estiloAplicar(cfg, estilo) {
  if (!estilo || !estilo.mul) return cfg;
  const m = estilo.mul;
  const cl = (v, a, b) => Math.min(b, Math.max(a, v));
  return {
    maxSpeed: cfg.maxSpeed * (m.speed || 1),
    accel: Math.min(30, cfg.accel * (m.accel || 1)),
    errStd: cl(cfg.errStd * (m.err || 1), 0.008, 0.16),
    missBase: cl(cfg.missBase * (m.miss || 1), 0.004, 0.45),
    minT: cl(cfg.minT * (m.tLo || 1), 0.24, 1.0),
    maxT: cl(cfg.maxT * (m.tHi || 1), 0.4, 1.3),
    maxShotSpeed: cfg.maxShotSpeed * (m.speed || 1),
    predictInterval: cl(cfg.predictInterval * (m.pred || 1), 0.03, 0.30),
    smash: cl(cfg.smash * (m.smash || 1), 0.01, 0.75),
    short: cfg.short,
  };
}

/* =====================================================================
 *  M5b (r115) · HERENCIA DE ESTILOS A CAMPEONATOS — la personalidad del
 *  manifest (agresividad/precision/constancia/caracter/cerebro) se
 *  traduce a UNO de los 12 estilos de OPPONENT_STYLES. Determinista,
 *  sin señales claras → null (el rival queda EXACTO como siempre).
 *  El toggle «Rivales con estilo visible» (pp_rivstyle_v1) sigue mandando:
 *  en NO la herencia se apaga y los campeonatos quedan byte-idénticos.
 *  ===================================================================== */
export function estiloDePersonalidad(pers) {
  if (!pers) return null;
  const ag = pers.agresividad || 3;
  const pr = pers.precision || 3;
  const co = pers.constancia || 3;
  const car = String(pers.caracter || '').toLowerCase();
  if (car === 'frio' || co >= 4) return 'veterano';   // paciente, no falla dos veces
  if (ag >= 4) return 'atacante';                     // viviendo del smash
  if (ag <= 2 && pr >= 4) return 'bloqueador';        // pegado y de reflejos
  if (ag <= 2) return 'defensivo';                    // bolas altas desde el fondo
  if (pr >= 4) return 'bloqueador';
  if (co <= 2) return 'nervioso';                     // rápido pero desordenado
  return null;                                        // sin señal: comportamiento clásico
}

/* =====================================================================
 *  M5b (r115) · LA ESCALERA DE CARRERA — divisiones de BRONCE a LEYENDA
 *  con rivales CONCRETOS (nombre propio + estilo de M5a + preset base y
 *  factor k). La cfg del desafío = scalePreset(AI_PRESETS[preset], k) +
 *  estiloAplicar(estilo) — SIEMPRE dentro de los topes legales (sin
 *  trampas: mismos clamps que el resto del juego). El progreso vive en
 *  localStorage pp_carrera_v1 (div, done, rec, crowned) — ver c12.
 *  ===================================================================== */
export const CARRERA_DIVISIONES = [
  { id: 'bronce', nameKey: 'carrera_d_bronce', col: '#c9935a',
    rivales: [
      { id: 'roko', es: 'ROKO EL ATREVIDO', en: 'ROKO THE BOLD', estilo: 'nervioso', preset: 'easy', k: 0.88 },
      { id: 'marta', es: 'MARTA MESITA', en: 'MARTY TABLETOP', estilo: 'allround', preset: 'easy', k: 1.0 },
      { id: 'paco', es: 'PACO CORTADA', en: 'CHOP CHOP CHARLIE', estilo: 'chopero', preset: 'easy', k: 1.08 },
    ] },
  { id: 'plata', nameKey: 'carrera_d_plata', col: '#c9ccd4',
    rivales: [
      { id: 'lulu', es: 'LULU LOOPER', en: 'LULU LOOPER', estilo: 'looper', preset: 'easy', k: 1.2 },
      { id: 'paola', es: 'PAOLA LA PARED', en: 'WALL-WALL PAULA', estilo: 'bloqueador', preset: 'easy', k: 1.25 },
      { id: 'fede', es: 'FEDE FONDO', en: 'DEEP-DAVE', estilo: 'defensivo', preset: 'medium', k: 0.9 },
    ] },
  { id: 'oro', nameKey: 'carrera_d_oro', col: '#ffd257',
    rivales: [
      { id: 'carla', es: 'CARLA CUCHILLA', en: 'CARLA THE BLADE', estilo: 'dejadas', preset: 'medium', k: 1.0 },
      { id: 'oscar', es: 'ÓSCAR OFENSIVA', en: 'OSCAR ONSLAUGHT', estilo: 'atacante', preset: 'medium', k: 1.05 },
      { id: 'tomas', es: 'TOMÁS TODO TERRENO', en: 'TOM ALL-TERRAIN', estilo: 'allround', preset: 'medium', k: 1.15 },
    ] },
  { id: 'diamante', nameKey: 'carrera_d_diamante', col: '#7de3ff',
    rivales: [
      { id: 'vera', es: 'VERA LA VETERANA', en: 'VERA THE VETERAN', estilo: 'veterano', preset: 'medium', k: 1.25 },
      { id: 'gus', es: 'GUS EL GIGANTE', en: 'GIANT GUS', estilo: 'gigante', preset: 'hard', k: 0.95 },
      { id: 'nina', es: 'NINA NÉBULA', en: 'NINA NEBULA', estilo: 'relampago', preset: 'hard', k: 1.02 },
    ] },
  { id: 'leyenda', nameKey: 'carrera_d_leyenda', col: '#b07cff',
    rivales: [
      { id: 'rayo', es: 'RAYO ROMERO', en: 'LIGHTNING RAY', estilo: 'relampago', preset: 'hard', k: 1.15 },
      { id: 'muro', es: 'EL MURO DE HIERRO', en: 'THE IRON WALL', estilo: 'bloqueador', preset: 'hard', k: 1.2 },
      { id: 'leyenda', es: 'LA LEYENDA', en: 'THE LEGEND', estilo: 'veterano', preset: 'hard', k: 1.3 },
    ] },
];

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
 *  r21 (v3.6.117) · ASPECTOS DE LA BOLA — skins 100 % COSMÉTICAS.
 *  Reglas de casa (idénticas a MESA_ASPECTOS, r96):
 *   · NUNCA tocan la física: radio, masa, rebote y Magnus son intocables —
 *     el material cambia color/mapa/roughness/metalness/emisivo, nada más.
 *   · CANDADOS igual que las mesas: lock 'wins10' (10 victorias o 6★ de
 *     retos) y 'streak5' (racha de 5 o 3★) — reutiliza _mesaLibre().
 *   · REGLA DEL DUEÑO en campeonato: la bola cae a la OFICIAL (blanca).
 *   · ONLINE: la bola viste la skin del HOST — viaja en el HELLO v2 (campo
 *     sk) y el invitado la adopta; builds viejos ignoran el campo (JSON
 *     tolerante, PROTO/PHYS intactos).
 *  Texturas: PROCEDURALES (canvas 2D en runtime, c07) — cero bytes nuevos
 *  en el bundle, cero descargas nuevas en el casco.
 *  Campos: id · lock · nameKey · tex (null = material plano) · color ·
 *  rough · metal · emis · emisInt · trail [r,g,b] del reposo de estela ·
 *  ring (Saturno: aro hijo decorativo).
 *  ===================================================================== */
export const BOLA_ASPECTOS = [
  /* — clásicas (3) — r24 · las 3 planas llevan costura + marca CRAZY
   * (bolaTex): color liso = giro invisible (queja del dueño en r24). */
  { id: 'blanca', lock: null, nameKey: 'bola_asp_blanca', tex: 'blanca',
    color: 0xfff8ef, rough: 0.35, metal: 0.0, emis: 0x555044, emisInt: 0.35,
    trail: [0.75, 0.75, 0.75], ring: false },
  { id: 'naranja', lock: null, nameKey: 'bola_asp_naranja', tex: 'naranja',
    color: 0xff8a3d, rough: 0.35, metal: 0.0, emis: 0x553418, emisInt: 0.35,
    trail: [1.0, 0.54, 0.24], ring: false },
  { id: 'menta', lock: null, nameKey: 'bola_asp_menta', tex: 'menta',
    color: 0x8fe3c8, rough: 0.35, metal: 0.0, emis: 0x2e5548, emisInt: 0.35,
    trail: [0.56, 0.89, 0.78], ring: false },
  /* — locura (5) — */
  { id: 'estrellas', lock: 'streak5', nameKey: 'bola_asp_estrellas', tex: 'estrellas',
    color: 0xffffff, rough: 0.35, metal: 0.0, emis: 0x555034, emisInt: 0.35,
    trail: [1.0, 0.82, 0.35], ring: false },
  { id: 'playa', lock: null, nameKey: 'bola_asp_playa', tex: 'playa',
    color: 0xffffff, rough: 0.4, metal: 0.0, emis: 0x555555, emisInt: 0.3,
    trail: [0.9, 0.9, 0.9], ring: false },
  { id: 'futbol', lock: 'wins10', nameKey: 'bola_asp_futbol', tex: 'futbol',
    color: 0xffffff, rough: 0.5, metal: 0.0, emis: 0x444444, emisInt: 0.3,
    trail: [0.9, 0.9, 0.95], ring: false },
  { id: 'ocho', lock: 'wins10', nameKey: 'bola_asp_ocho', tex: 'ocho',
    color: 0xffffff, rough: 0.22, metal: 0.0, emis: 0x2a2a33, emisInt: 0.4,
    trail: [0.2, 0.2, 0.25], ring: false },
  { id: 'ojo', lock: null, nameKey: 'bola_asp_ojo', tex: 'ojo',
    color: 0xffffff, rough: 0.3, metal: 0.0, emis: 0x555055, emisInt: 0.35,
    trail: [0.85, 0.75, 0.9], ring: false },
  /* — neón / arcade (3) — */
  { id: 'neon', lock: null, nameKey: 'bola_asp_neon', tex: 'neon',
    color: 0xff3fa4, rough: 0.25, metal: 0.0, emis: 0xff2f96, emisInt: 0.85,
    trail: [1.0, 0.25, 0.64], ring: false },
  { id: 'holo', lock: 'wins10', nameKey: 'bola_asp_holo', tex: 'holo',
    color: 0xffffff, rough: 0.3, metal: 0.1, emis: 0x446688, emisInt: 0.45,
    trail: [0.4, 0.8, 1.0], ring: false },
  { id: 'disco', lock: 'streak5', nameKey: 'bola_asp_disco', tex: 'disco',
    color: 0xcfd6de, rough: 0.12, metal: 0.9, emis: 0x333840, emisInt: 0.5,
    trail: [0.8, 0.84, 0.9], ring: false },
  /* — planetas (4) — */
  { id: 'marte', lock: null, nameKey: 'bola_asp_marte', tex: 'marte',
    color: 0xffffff, rough: 0.55, metal: 0.0, emis: 0x54301c, emisInt: 0.3,
    trail: [0.85, 0.4, 0.25], ring: false },
  { id: 'luna', lock: null, nameKey: 'bola_asp_luna', tex: 'luna',
    color: 0xffffff, rough: 0.6, metal: 0.0, emis: 0x555a60, emisInt: 0.3,
    trail: [0.8, 0.82, 0.86], ring: false },
  { id: 'tierra', lock: null, nameKey: 'bola_asp_tierra', tex: 'tierra',
    color: 0xffffff, rough: 0.4, metal: 0.0, emis: 0x1c3a55, emisInt: 0.35,
    trail: [0.3, 0.55, 0.9], ring: false },
  { id: 'lava', lock: 'streak5', nameKey: 'bola_asp_lava', tex: 'lava',
    color: 0xffffff, rough: 0.5, metal: 0.0, emis: 0xff5a1e, emisInt: 0.6,
    trail: [1.0, 0.35, 0.12], ring: false },
  { id: 'saturno', lock: 'wins10', nameKey: 'bola_asp_saturno', tex: 'saturno',
    color: 0xffffff, rough: 0.45, metal: 0.0, emis: 0x554a30, emisInt: 0.3,
    trail: [0.9, 0.78, 0.5], ring: true },
];
/* =====================================================================
 *  r24 (v3.6.119) · VARIANTES DEL HALL DEL ANFITRIÓN — el arte de la
 *  estancia que PRESUME. El hall es una caja de 6 planos con JPGs
 *  externos (assets/hall/ · patrón v3.6.28); cada variante apunta a SU
 *  carpeta de arte (mismos nombres de ficha y mismas proporciones exactas
 *  de los planos). 'cabana' viste el refugio de montaña del dueño
 *  (chimenea de piedra, barra, ventana nevada) y se libera con 10
 *  victorias ('wins10' — el mismo candado de las skins de gala, ver
 *  _mesaLibre). Online, el invitado ve la del ANFITRIÓN: hp lleva hv
 *  (id saneado contra este catálogo, patrón sk/hp de las r22/r23).
 *  ===================================================================== */
export const HALL_VARIANTES = [
  { id: 'anfitrion', lock: null, nameKey: 'hall_var_anfitrion',
    base: 'assets/hall/' },
  { id: 'cabana', lock: 'wins10', nameKey: 'hall_var_cabana',
    base: 'assets/hall/cabana/' },
];
/** r24 · variante por id SIN chequeo de candado (el id ya viaja saneado;
 *  el candado sólo gobierna ELEGIRLA, no verla en casa del anfitrión). */
export function hallVariantePorId(id) {
  return HALL_VARIANTES.find((v) => v.id === id) || HALL_VARIANTES[0];
}
/** r21 · id de la skin OFICIAL (campeonato y respaldo de red). */
export const BOLA_ID_OFICIAL = BOLA_ASPECTOS[0].id;
/** r21 · skin por id SIN chequeo de candado (para la skin del RIVAL: el
 *  anfitrión ya la tenía desbloqueada — el invitado confía el id si existe). */
export function bolaAspectoPorId(id) {
  return BOLA_ASPECTOS.find((s) => s.id === id) || BOLA_ASPECTOS[0];
}

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
