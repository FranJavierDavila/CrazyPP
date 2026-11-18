#!/usr/bin/env node
/* CRAZY PING PONG · r124 · M7e PERSISTENCIA — TESTS DEL HISTORIAL DE TORNEOS
 * Ejecuta la FUENTE REAL (src/game/core/c11_champloader.js) en Node — el
 * mismo código que corre en el Quest — y verifica, sin visor y sin DOM:
 *
 *   1 · historialFusionar (pura): alta con fecha de sellado, idempotencia,
 *       refresh de victorias/leyenda, no-campeón jamás entra, cap 50,
 *       entradas corruptas toleradas.
 *   2 · historialTorneos con ChampLoader REAL + shim de localStorage:
 *       convenciones <base>champ y <base>trophy, victorias vivas del
 *       registro, LEYENDA, persistencia en pp_torneos_historial_v1,
 *       registro corrupto reconstruido, entries degenerados sin lanzar.
 *
 * Carga al estilo build_game.py: el bloque DEPS-FASE2 (imports generados
 * que en el monofile comparten ámbito) se elimina antes de importar —
 * c11 queda sin dependencias y el módulo es 100% el de producción.
 *
 * Uso: node --no-warnings scripts/test_m7e_persistencia_v36113.mjs
 * ( registrado como capa QA de la ronda r124 · M7e )
 */
import { readFileSync, writeFileSync } from 'node:fs';

/* shim THREE mínimo: c11 crea const top-level (Vector3/Quaternion/Raycaster)
 * que en el monofile resuelven contra el THREE global — aquí bastan stubs
 * inertes porque los tests sólo tocan historialFusionar/historialTorneos. */
globalThis.THREE = {
  Vector3: class { constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; } },
  Quaternion: class { constructor(x = 0, y = 0, z = 0, w = 1) { this.x = x; this.y = y; this.z = z; this.w = w; } },
  Raycaster: class { constructor() { this.far = 0; } },
};
/* precarga de pieles de cartel: new Image() al inicializar el módulo */
globalThis.Image = class {
  constructor() { this.complete = false; this.naturalWidth = 0; this.naturalHeight = 0; }
  set src(_v) { /* nunca carga en Node: los tests no pintan carteles */ }
};
/* gancho QA del módulo (window.__PP_NORMAS) y vecinos del navegador */
globalThis.window = globalThis;

const _src = readFileSync(new URL('../src/game/core/c11_champloader.js', import.meta.url), 'utf8')
  .replace(/\/\* DEPS-FASE2-INICIO[\s\S]*?DEPS-FASE2-FIN \*\/\n?/g, '');
const _tmp = '/tmp/c11_m7e_under_test.mjs';
writeFileSync(_tmp, _src);
const { ChampLoader, historialFusionar } = await import('file://' + _tmp);

/* ---- shim mínimo de localStorage (aislado por test) ---- */
let _store = new Map();
function lsReset() {
  _store = new Map();
  globalThis.localStorage = {
    getItem: (k) => (_store.has(k) ? _store.get(k) : null),
    setItem: (k, v) => { _store.set(k, String(v)); },
    removeItem: (k) => { _store.delete(k); },
  };
}

let OK = 0, FAIL = 0;
function check(nombre, cond) {
  if (cond) { OK++; console.log('  ✓ ' + nombre); }
  else { FAIL++; console.log('  ✗ ' + nombre); }
}
const HOY = new Date().toISOString().slice(0, 10);

console.log('1 · historialFusionar (función pura)');
{
  const [h0, d0] = historialFusionar([], []);
  check('vacío → [] y sin dirty', Array.isArray(h0) && h0.length === 0 && d0 === false);

  const f1 = [{ id: 'locura', esCampeon: true, wins: 12, leyenda: false }];
  const [h1, d1] = historialFusionar([], f1);
  check('campeón nuevo → fila con fecha de HOY (sellado)', d1 === true && h1.length === 1 && h1[0].fecha === HOY && h1[0].wins === 12);

  const [h2, d2] = historialFusionar(h1, f1);
  check('idempotente (mismos datos → sin dirty, misma fecha)', d2 === false && h2.length === 1 && h2[0].fecha === HOY);

  const f3 = [{ id: 'locura', esCampeon: true, wins: 13, leyenda: true }];
  const [h3, d3] = historialFusionar(h2, f3);
  check('refresh de victorias y leyenda marca dirty', d3 === true && h3[0].wins === 13 && h3[0].leyenda === true);
  check('la fecha de sellado NO cambia en el refresh', h3[0].fecha === HOY);

  const f4 = [{ id: 'locura', esCampeon: false, wins: 99, leyenda: false }];
  const [, d4] = historialFusionar(h3, f4);
  check('NO campeón: jamás entra ni toca la fila', d4 === false);

  const many = Array.from({ length: 60 }, (_, i) =>
    ({ id: 't' + String(i).padStart(2, '0'), esCampeon: true, wins: 1, leyenda: false }));
  const [h5] = historialFusionar([], many);
  check('cap 50 (60 filas → 50)', h5.length === 50);
  check('cap conserva las mayores por id (t10..t59)', h5[0].id === 't10' && h5[49].id === 't59');

  const [h6] = historialFusionar('basura', f1);
  check('hist corrupto (string) se tolera', h6.length === 1);

  const [h7] = historialFusionar([{ sin: 'id' }, null, { id: 'locura', fecha: HOY, wins: 12, leyenda: false }], f1);
  check('filas basura filtradas, una por id', h7.length === 1);
}

console.log('2 · historialTorneos (ChampLoader real + localStorage)');
{
  lsReset();
  const cl = new ChampLoader(null);
  cl.entries = [
    { id: 'locura', storage: 'pp_arcade_', title: { es: 'La Locura', en: 'Madness' } },
    { id: 'magia', storage: 'pp_champ_magia_', title: { es: 'Magia', en: 'Magic' } },
    { id: 'sinbase', storage: '', title: { es: 'x', en: 'x' } },
  ];
  localStorage.setItem('pp_arcade_champ', '1');
  localStorage.setItem('pp_arcade_wins', '12');

  const h1 = cl.historialTorneos();
  check('campeón sellado · no-campeón fuera · storage vacío ignorado', h1.length === 1 && h1[0].id === 'locura');
  check('victorias leídas del registro del campeonato', h1[0].wins === 12);
  const KEY = 'pp_torneos_historial_v1';
  check('persistido en pp_torneos_historial_v1', !!localStorage.getItem(KEY));

  const h2 = cl.historialTorneos();
  check('segunda pasada idempotente (misma fecha de sellado)', h2.length === 1 && h2[0].fecha === h1[0].fecha);

  localStorage.setItem('pp_arcade_leyenda', '1');
  localStorage.setItem('pp_arcade_wins', '15');
  const h3 = cl.historialTorneos();
  check('refresh: victorias 15 y LEYENDA visible', h3[0].wins === 15 && h3[0].leyenda === true);

  localStorage.setItem(KEY, '{corrupto');
  const h4 = cl.historialTorneos();
  check('registro corrupto tolerado (reconstruye)', h4.length === 1 && h4[0].id === 'locura');

  const cl2 = new ChampLoader(null);
  cl2.entries = [{ id: 'halloween', storage: 'pp_champ_halloween_', title: { es: 'H', en: 'H' } }];
  localStorage.setItem('pp_champ_halloween_trophy', '1');
  const h5 = cl2.historialTorneos();
  const filaHal = h5.find((x) => x.id === 'halloween');
  check('convención <base>trophy también sella', !!filaHal);
  check('fecha en formato YYYY-MM-DD', !!filaHal && /^\d{4}-\d{2}-\d{2}$/.test(filaHal.fecha));

  const cl3 = new ChampLoader(null);
  cl3.entries = [{ id: 'x' }];
  let sinLanzar = true;
  try { cl3.historialTorneos(); } catch { sinLanzar = false; }
  check('entries degenerados (sin storage) no lanzan', sinLanzar);
}

console.log(`\nM7e · ${OK}✓ / ${FAIL}✗`);
process.exit(FAIL ? 1 : 0);
