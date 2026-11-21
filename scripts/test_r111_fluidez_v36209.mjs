// test_r111_fluidez_v36209.mjs — r111 · FLUIDEZ PRIMERO — LA CABEZA MANDA
// Bug de raíz (reporte del dueño, 21-11-2026): al girar la cabeza, la línea
// longitudinal central de la mesa se percibe DUPLICADA/a saltos (judder).
// Causa (cuatro piezas, todas del PerfManager):
//   1 · perfil Quest 3 a filo de navaja (1.40× @ 90 Hz): vr_end midió
//       55-78 fps — bajo el piso 72 la mayor parte del tiempo y cada frame
//       perdido lo repinta el compositor con la pose vieja (imagen doble).
//   2 · la barra de la sonda era FIJA (68 media / 55 peor segundo) — a
//       90 Hz objetivo eso es un 24% de frames perdidos y la sonda la daba
//       por buena.
//   3 · el gobernador dormía EN el rallye (solo degradaba bajo avg<50):
//       un intercambio a 55-70 fps — judder puro — seguía sin corregirse
//       hasta el fin del punto.
//   4 · la calibración sobre-affilada quedaba guardada en localStorage v1
//       y sobrevivía a cualquier mejora de defaults.
// Fix: tier con margen (1.25×/0.45) + barra 93%/83% de la tasa objetivo +
// gobernador que actúa EN el rallye con judder sostenido (solo imagen,
// la tasa no se cambia en caliente) + PERF_LS v2 (recalibración honesta).
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  if (cond) { ok++; console.log('  ✓ ' + label); }
  else { fails++; console.log('  ✗ FALLO: ' + label); }
};
const RAIZ = '/home/z/my-project';
const c12 = readFileSync(RAIZ + '/src/game/core/c12_pingponggame.js', 'utf8');
const vj = JSON.parse(readFileSync(RAIZ + '/src/game/VERSION.json', 'utf8'));

console.log('r111 · FLUIDEZ — perfil del casco con margen');
chk(/quest3: \{ label: 'Quest 3', scale: 1\.25, fovea: 0\.45, rate: 90 \}/.test(c12),
  'Quest 3 arranca 1.25× / fovea 0.45 (≈0,80× píxeles del 1.40×)');
chk(/quest2: \{ label: 'Quest 2', scale: 1\.05, fovea: 0\.65, rate: 72 \}/.test(c12),
  'Quest 2 intacto (ya era conservador)');
chk(/const PERF_PISO = 72;/.test(c12), 'el piso del dueño (72) intacto');
chk(/foveaMax\(\)[\s\S]{0,300}?return 0\.65;/.test(c12),
  'techo honesto de fovea 0.65 intacto (r96, sin anillos en la vista)');

console.log('r111 · FLUIDEZ — sonda con barra por tasa');
chk(/const pisoAvg = Math\.round\(this\.rate \* 0\.93\);/.test(c12) &&
    /const pisoMin = Math\.round\(this\.rate \* 0\.83\);/.test(c12),
  'barra de la sonda = 93% de la tasa / peor segundo ≥83%');
chk(/const pasa = fpsAvg >= pisoAvg && fpsMin >= pisoMin;/.test(c12),
  'la sonda pasa con la barra por tasa (ya no con 68 fijo)');
chk(!/fpsAvg >= 68 && fpsMin >= 55/.test(c12),
  'la barra fija vieja (68/55) ha desaparecido');
chk(Math.round(90 * 0.93) === 84 && Math.round(72 * 0.93) === 67 &&
    Math.round(90 * 0.83) === 75 && Math.round(72 * 0.83) === 60,
  'aritmética: 90 Hz → 84/75 · 72 Hz → 67/60');

console.log('r111 · FLUIDEZ — gobernador vivo en el rallye');
chk(/const judderRally = !bajandoTasa &&\s*\n\s*\(avg < PERF_PISO - 8 \|\| min < 45\);/.test(c12),
  'judder sostenido en rallye se detecta (avg < 64 o peor segundo < 45)');
chk(/if \(!rally \|\| avg < 50 \|\| judderRally\) this\._stepDown\(bajandoTasa\);/.test(c12),
  'el gobernador actúa en rallye con judder (solo imagen)');
chk(/const bajandoTasa = this\.rate > PERF_PISO \+ 0\.5 && avg < this\.rate \* 0\.87;/.test(c12),
  'el cambio de TASA sigue vetado en caliente (bajandoTasa intacto)');

console.log('r111 · FLUIDEZ — recalibración honesta del casco');
chk(c12.includes("const PERF_LS = 'ppxr_perf_v2';"), 'registro de calibración v2');
chk(!c12.includes('ppxr_perf_v1'), 'la clave v1 ya no se lee');
chk(/if \(d && PERF_FFR_MODOS\[d\.ffr\] != null\) this\.ffr = d\.ffr;/.test(c12),
  'la preferencia FFR del dueño sobrevive al cambio de registro');

console.log('r111 · SELLOS DE LA RONDA');
chk(vj.version === '3.6.209-SDK6', 'VERSION.json: 3.6.209-SDK6');
chk(vj.fase === 186, 'FASE 186');
chk(vj.hub === 'v36209-sdk6', 'hub v36209-sdk6');
chk((c12.match(/const VERSION = '([^']+)';/) || [])[1] === undefined ||
    c12.includes("const VERSION = '3.6.209-SDK6'") === false &&
    readFileSync(RAIZ + '/src/game/core/c00_pre_three.js', 'utf8')
      .includes("const VERSION = '3.6.209-SDK6'"),
  'sello c00 = 3.6.209-SDK6');
chk(readFileSync(RAIZ + '/src/game/03_body.html', 'utf8').includes('3.6.209'),
  'badge del arranque (#verBadge) = 3.6.209');
{
  const game = readFileSync(RAIZ + '/public/game.html');
  const sha = createHash('sha256').update(game).digest('hex');
  chk(sha === vj.golden, 'golden coincide con el build (' + sha.slice(0, 12) + '…)');
  chk(vj.tamano === game.length, 'tamaño del build en VERSION.json (' + game.length + ' B)');
  chk(game.toString('utf8').includes('ppxr_perf_v2'), 'el bundle lleva el registro v2');
  chk(game.toString('utf8').includes("scale: 1.25, fovea: 0.45, rate: 90"),
    'el bundle lleva el perfil con margen');
  chk(game.toString('utf8').includes('judderRally'), 'el bundle lleva el gobernador de rallye');
}

console.log('\nRESULTADO: ' + ok + ' OK · ' + fails + ' FALLOS' +
  (fails === 0 ? ' — FLUIDEZ PRIMERO' : ''));
process.exit(fails === 0 ? 0 : 1);
