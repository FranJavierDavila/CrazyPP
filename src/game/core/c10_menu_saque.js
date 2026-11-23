export const MENU_LOGO_SRC = 'assets/externos/logo_menu.jpg';
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import * as THREE from 'three';
/* DEPS-FASE2-FIN */

export const BALL_HAND_LIFT = 0.08;   // bola "apoyada" sobre la palma de la mano libre
export const AI_TOSS_T = 0.55;        // duración del lanzamiento (y swing) del saque de la IA

// temporales del sistema de pose de las palas IA (no compartir con física)
const poseE = new THREE.Euler();
export const poseQ = new THREE.Quaternion();
const poseD = new THREE.Vector3();
export const swingV = new THREE.Vector3();   // vector del follow-through (v2.17)
// v2.22 · orientación de la cara de la pala (base ortonormal)
const aimV = new THREE.Vector3();     // dirección deseada de la normal de cara
const aimX = new THREE.Vector3();     // eje lateral del marco de la cara
const aimY = new THREE.Vector3();     // eje "arriba" de la hoja
export const aimM = new THREE.Matrix4();     // base -> cuaternión
const aimUP = new THREE.Vector3(0, 1, 0);
export const aimRollQ = new THREE.Quaternion();
export const aimPitchQ = new THREE.Quaternion();
// r90 · cierre de cara sobre el eje del mango: la CARA (no la base)
// rota alrededor del eje hoja — topspin la baja (cerrada), cortada la
// sube (abierta); el mango no se mueve (paralelo a la mesa siempre).
export const closQ = new THREE.Quaternion();
export const closAx = new THREE.Vector3();
export const closX = new THREE.Vector3();
export const AIM_Z = new THREE.Vector3(0, 0, 1);   // normal local de la cara (IA)
export const AIM_XA = new THREE.Vector3(1, 0, 0);  // eje local X (pitch de muñeca)
// v2.23 · POSE POR GOLPE: la pala se compone desde DOS direcciones mundiales
// (eje de la hoja mango→punta + normal de la cara) y un roll de muñeca.
export const AIM_FWD = new THREE.Vector3();      // hacia el campo contrario
export const AIM_RIGHT = new THREE.Vector3();    // lado de la mano derecha del jugador
export const AIM_BLADE = new THREE.Vector3();    // eje de la hoja deseado
export const AIM_FACE = new THREE.Vector3();     // normal de la cara deseada
export const AIM_BX = new THREE.Vector3();
export const AIM_BY = new THREE.Vector3();
export const AIM_BZ = new THREE.Vector3();

/** Firma de cada golpe (v2.23) — hace que la pala GIRE como la giraría un
 *  jugador real en vez de quedarse vertical:
 *  side0  inclinación de la punta hacia el lado del golpe en el contacto
 *  side1  cruce de la punta al lado contrario al terminar el follow-through
 *  fwd0/fwd1  inclinación de la hoja hacia delante (tap vertical en la
 *             cortada, barrido diagonal en el drive)
 *  clos0  cierre de la cara en el contacto (+ liftado · − cortada/slice)
 *  clos1  cierre extra durante el follow-through
 *  rise   elevación del brazo al terminar
 *  cross  cruce del cuerpo (posición) al terminar */
export const SWING_POSE = {
  drive:   { side0: 0.55, side1: 0.42, fwd0: 0.20, fwd1: 0.34, clos0: 0.14, clos1: 0.20, rise: 0.13, cross: 1.0 },
  smash:   { side0: 0.50, side1: 0.36, fwd0: 0.15, fwd1: 0.40, clos0: 0.24, clos1: 0.16, rise: 0.07, cross: 1.0 },
  push:    { side0: 0.42, side1: 0.26, fwd0: 0.06, fwd1: 0.16, clos0: -0.16, clos1: -0.08, rise: 0.05, cross: 0.6 },
  dejada:  { side0: 0.50, side1: 0.30, fwd0: 0.10, fwd1: 0.20, clos0: -0.12, clos1: -0.04, rise: 0.12, cross: 0.7 },
  bloqueo: { side0: 0.30, side1: 0.18, fwd0: 0.10, fwd1: 0.15, clos0: 0.05, clos1: 0.03, rise: 0.04, cross: 0.5 },
  // v2.84: GOLPE MALO — toque torpe de muñeca: casi sin barrido, cara plana
  // y el brazo apenas acompaña (así se VE que el fallo fue un mal contacto)
  mala:    { side0: 0.18, side1: 0.10, fwd0: 0.04, fwd1: 0.09, clos0: 0.02, clos1: -0.06, rise: 0.02, cross: 0.25 },
};

/* =====================================================================
 *  =====================================================================
 *  v2.69 · CAMPEONATOS — 100% CARPETAS AUTOCONTENIDAS (antes «externos»)
 *  ---------------------------------------------------------------------
 *  TODOS los campeonatos (La Locura y magia, y los que vengan) viven en
 *  championships/<id>/{manifest.json, index.js, data.json?, assets/} y
 *  replican POR SÍ MISMOS la arquitectura común:
 *    5 ETAPAS: 1 LUCHA rival Nv.1 -> 2 PRUEBA de habilidad -> 3 LUCHA
 *    rival Nv.2 (más difícil) -> 4 PRUEBA -> 5 LUCHA FINAL (JEFE).
 *    Al vencer: LOGRO = insignia que preside el palmares en el ranking,
 *    trofeo en la sala y mapa del camino (pared izquierda) revelado.
 *    Rival con arte por ESTADOS (12 poses), ranking lateral, cartel de
 *    «¡PARTIDA NUEVA!», superpoderes con aviso y trofeo final.
 *
 *  Para AÑADIR un campeonato: crear su carpeta y añadir UNA línea en
 *  championships/championships.json — el núcleo la descubre y la añade
 *  SOLO (botón en el menú CAMPEONATOS, ranking mundial, reinicio).
 *  Entrada «eager»: el módulo se importa e inicializa al arrancar (sin
 *  lanzarlo) para campeonatos que deben existir desde el primer frame.
 *
 *  El NÚCLEO no sabe NADA de cada campeonato: ChampLoader
 *  · descubre las carpetas (championships/championships.json; en
 *    file:// se omite en silencio: sin índice no hay botón),
 *  · dibuja UN botón por campeonato en la sección CAMPEONATOS,
 *  · lanza el módulo con import() dinámico y le entrega el juego,
 *  · delega en el módulo ACTIVO los ganchos del juego (update /
 *    onPoint / onMatchOver), el saque y la física durante las PRUEBAS
 *    (estado 'arkanoide' o 'champtest'), la pistola, la bola doble y
 *    el multiplicador de dificultad del rival (aiMul),
 *  · pinta sus controles extra de menú (menuItems) y enruta sus
 *    acciones (champact), y borra SUS registros al reiniciar.
 *  Todos los métodos delegan con guard: un módulo roto nunca tumba el
 *  frame. Los campeonatos son excluyentes entre sí (leaveAll).
 *  ===================================================================== */
export const CHAMPS_STATE = 'champtest';   // rules.state durante una prueba externa

/* v2.96 · REJUGAR ETAPAS SUPERADAS — temporales del rayo de la PALA sobre
 *  el mapa de la ruta (el muRaycaster del menú tiene far=2,5 m: el mapa
 *  cuelga en la pared a ~3 m del jugador, hace falta uno propio). */
export const rpRaycaster = new THREE.Raycaster();
rpRaycaster.far = 9;
export const rpOrigin = new THREE.Vector3();
export const rpQuat = new THREE.Quaternion();
export const rpDir = new THREE.Vector3();
export const _rpV1 = new THREE.Vector3();     // v2.120: temporal del pick del mapa
export const _rpSize = new THREE.Vector3();   // v2.120: tamaño fallback del plano
// v2.98: temporales del HAZ DE LUZ del selector de etapas
export const _rbV1 = new THREE.Vector3(); const _rbV2 = new THREE.Vector3();
export const _rbV3 = new THREE.Vector3(); const _rbV4 = new THREE.Vector3();
export const _rbQ = new THREE.Quaternion();
export const _dbV1 = new THREE.Vector3();                 // v2.108: pose del rótulo
export const _dbQ1 = new THREE.Quaternion(); const _dbQ2 = new THREE.Quaternion();

