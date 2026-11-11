#!/usr/bin/env node
/* CRAZY PING PONG · r27 · v3.6.123 · TEST: MODO DEPURACIÓN (FORO3D) COMPLETO.
 *
 *   A · «recuerda que teníamos una clave secreta de tal forma que si el
 *       nombre de usuario es "FORO3D" entramos en el modo de depuración
 *       que nos permite ver o acceder a cualquier recurso aunque esté
 *       bloqueado, o nos permite entrar en cualquier prueba o etapa de
 *       los campeonatos aunque no estén disponibles para otros usuarios».
 *
 *   La r26b dejó TRES agujeros que este parche cierra:
 *     1) _mesaLibre() NO consultaba window.__PP_DEBUG → los 3 SALONES
 *        nuevos (Neón Arcade, Observatorio Estelar, Dojo Zen) y los
 *        aspectos de mesa/bola seguían CERRADOS con foro3d.
 *     2) halloween maxIdx() sin debug → mapa con tapas y gatillo
 *        limitado al progreso real (oeste/locura/magia sí lo hacían
 *        desde v2.108 con su patrón ppDbg).
 *     3) estacion_orbital replayData().maxIdx sin debug → ídem.
 *
 *   GARANTÍAS DE SIEMPRE:
 *     · c04/c05 (física) SIN una sola línea nueva — sha256 idéntico a
 *       la r26b (9ba1d4a).
 *     · oeste/locura/magia conservan su patrón ppDbg INTACTO.
 *     · El interceptor de registros de c00 sigue descartando pp_champ_*,
 *       pp_arcade_*, pp_worldrank_cache y ppxr_stats_v1 con __PP_DEBUG.
 *
 * Uso: node --no-warnings scripts/test_r27_foro3d_v36123.mjs
 */
import { readFileSync } from 'node:fs';
import { execSync } from 'node:child_process';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');

const c12 = lee('src/game/core/c12_pingponggame.js');
const c00 = lee('src/game/core/c00_pre_three.js');
const c11 = lee('src/game/core/c11_champloader.js');
const game = lee('public/game.html');
const hal = lee('public/championships/halloween/index.js');
const est = lee('public/championships/estacion_orbital/index.js');
const oes = lee('public/championships/oeste/index.js');
const loc = lee('public/championships/locura/index.js');
const mag = lee('public/championships/magia/index.js');

/* — 1 · NÚCLEO · la clave secreta existe y publica el flag ———————————— */
console.log('1 · NÚCLEO · clave foro3d → window.__PP_DEBUG');
chk(c00.includes("toLowerCase() === 'foro3d'"), 'ppDebugMode() compara en minúsculas (FORO3D vale)');
chk(c00.includes("window.__PP_DEBUG = ppDebugMode()"), 'el núcleo publica window.__PP_DEBUG al arrancar');
chk(c00.includes('window.ppDebugRefresh'), 're-evaluación en vivo al guardar el nombre (ppDebugRefresh)');
chk(game.includes("toLowerCase() === 'foro3d'"), 'la clave está en el BUNDLE generado');

/* — 2 · CANDADO ÚNICO · _mesaLibre() abre TODO con foro3d ————————————— */
console.log('2 · SALONES + ASPECTOS · _mesaLibre() consulta __PP_DEBUG');
chk(/_mesaLibre\(lock\) \{\s*\n\s*\/\/ v3\.6\.123 \(r27\)/.test(c12),
  'el bypass vive ARRIBA del todo en _mesaLibre() (cubre 14 llamadas)');
chk(c12.includes('window.__PP_DEBUG) return true'), 'con __PP_DEBUG devuelve true ANTES de mirar hitos');
chk(c12.includes("hito_rally20"), 'los 3 hitos r26b siguen en el candado (regresión)');
chk(c12.includes("hito_elo1100") && c12.includes("hito_aces5"), 'hito_elo1100 + hito_aces5 intactos');
chk(c12.includes("wins10") && c12.includes("streak5"), 'aspectos mesa Oro/Carbono intactos');
const antesBypass = c12.indexOf('window.__PP_DEBUG) return true');
const despuesBypass = c12.indexOf("if (lock === 'hito_rally20')");
chk(antesBypass > 0 && despuesBypass > antesBypass, 'orden correcto: bypass → hitos (el debug GANA)');

/* — 3 · HALLOWEEN · mapa completo en depuración ———————————————————————— */
console.log('3 · HALLOWEEN · maxIdx debug-aware');
chk(hal.includes('MODO DEPURACIÓN («foro3d»)'), 'halloween documenta el parche r27');
chk(hal.includes('window.__PP_DEBUG) return ctrl.totalEtapas() - 1'),
  'con __PP_DEBUG el mapa muestra TODAS las etapas');
chk(hal.includes('return Math.max(0, Math.min(ctrl.totalEtapas() - 1, ctrl.indiceReal() - 1));'),
  'el criterio clásico (sin debug) queda INTACTO');
chk(hal.includes('idx > this.mapa.maxIdx() || this.pruebaActiva()'),
  'rejugar() sigue guardado para jugadores normales');

/* — 4 · ESTACIÓN ORBITAL · mapa completo en depuración ————————————————— */
console.log('4 · ESTACIÓN ORBITAL · replayData maxIdx debug-aware');
chk(est.includes('MODO DEPURACIÓN («foro3d»)'), 'estacion_orbital documenta el parche r27');
chk(est.includes('!!window.__PP_DEBUG)') && est.includes('? 4'),
  'con __PP_DEBUG maxIdx = 4 (mapa completo)');
chk(est.includes('this.ctrl._champion ? 4 : Math.min(this.ctrl.stage | 0, 4)'),
  'el criterio clásico (sin debug) queda INTACTO');
chk(est.includes("localStorage.setItem('pp_champ_estacion_orbital_stage'"),
  'el salto de etapa sigue anclado al progreso (regresión)');

/* — 5 · PATRÓN V2.108 · oeste/locura/magia intactos ———————————————————— */
console.log('5 · OESTE/LOCURA/MAGIA · patrón ppDbg sin tocar');
for (const [nom, src] of [['oeste', oes], ['locura', loc], ['magia', mag]]) {
  chk(src.includes('function ppDbg()'), nom + ' conserva su helper ppDbg()');
  chk(/ppDbg\(\) \? 4/.test(src), nom + ' mantiene maxIdx: ppDbg() ? 4 (v2.108)');
}

/* — 6 · CAMPEONATOS BLOQUEADOS · c11 abre con foro3d ——————————————————— */
console.log('6 · C11 · candado de campeonatos (Estación Orbital)');
chk(c11.includes("static LOCKED = ['estacion_orbital'];"), 'LOCKED intacto (regresión)');
chk(c11.includes('return !ppDebugMode();'), 'isLocked() consulta ppDebugMode (foro3d entra)');
chk(c11.includes('window.__PP_DEBUG) &&'), 'rótulo «MODO DEPURACIÓN» en el visor sigue vivo');

/* — 7 · NO REGISTRA · interceptor de c00 sin cambios ——————————————————— */
console.log('7 · INTERCEPTOR · nada se persiste con foro3d');
chk(c00.includes("s.indexOf('pp_champ_') === 0 || s.indexOf('pp_arcade_') === 0"),
  'descarta pp_champ_* (cubre halloween y estacion_orbital) y pp_arcade_*');
chk(c00.includes("s === 'pp_worldrank_cache' || s === 'ppxr_stats_v1'"),
  'descarta ranking mundial y stats reales');

/* — 8 · GARANTÍA FÍSICA · c04/c05 diff VACÍO contra la r26b ———————————— */
console.log('8 · FÍSICA INTACTA · c04/c05 sha256 = r26b (9ba1d4a)');
const SHA_C04 = 'e4abb6ebb55bcfa7d412df50f72e09c3afc44dc4f0390a5c85661d4b77be6eb2';
const SHA_C05 = '8bb620820e4974d4ccab8308060d4b8fd7328c812b103f9309bd98654cf81d65';
const sha = (p) => execSync(`sha256sum "${raiz}${p}"`).toString().split(' ')[0];
chk(sha('src/game/core/c04_fisica_ccd.js') === SHA_C04, 'c04_fisica_ccd.js BYTE-EXACTO r26b');
chk(sha('src/game/core/c05_colisiones_ia_golpeo.js') === SHA_C05, 'c05_colisiones_ia_golpeo.js BYTE-EXACTO r26b');

/* — 9 · BUILD · sellos de versión ——————————————————————————————————————— */
console.log('9 · BUILD · sello vigente (re-anclada r33: 3.6.125)');
const vj = JSON.parse(lee('src/game/VERSION.json'));
chk(vj.version === '3.6.129-SDK6', 'VERSION.json = 3.6.129-SDK6 (re-anclada r33)');
chk(vj.fase === 131, 'FASE 131 (re-anclada r33)');
chk(game.includes('3.6.129-SDK6'), 'el bundle lleva el sello vigente (re-anclada r33)');
const golden = (lee('src/game/GOLDEN_SHA256.txt').match(/\b[0-9a-f]{64}\b/) || [''])[0];
chk(vj.golden === golden, 'golden refrescado y coherente con VERSION.json');
chk(vj.tamano === game.length || vj.tamano === Buffer.byteLength(game), 'tamaño del bundle coherente');

/* — 10 · DESCARGAS · el modo no abre el hub con candados falsos ———————— */
console.log('10 · SANIDAD · sin regresiones de ronda');
chk(game.includes('ELEC_ATRAE_P') || game.includes('ELEC_ATRAE'), 'r26b: bola atractora sigue en el bundle');
chk(game.includes('TRAIL_PODER') && game.includes('fenix'), 'r26b: Súper Fénix sigue en el bundle');
chk(game.includes('CRONO_F'), 'r26b: Súper Crono sigue en el bundle');
chk(game.includes('hito_rally20') && game.includes('Neon') || game.includes('NEON'),
  'r26b: Salón Neón Arcade sigue en el bundle');

console.log(`\nR27 · ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
