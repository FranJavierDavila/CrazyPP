// r156 · TEST DE DATOS MI PERFIL (node directo, importa c02 real)
// Verifica: escala de rangos sin huecos, curva XP monótona calibrada al
// mock (L27≈5.000), catálogos únicos con costes/locks válidos y helpers
// de saneado. Ejecutar: node scripts/test_perfil_datos.mjs
import {
  RANGOS_ELO, XP_CURVA, XP_ACCION, MONEDAS_ACCION,
  PAISES, AVATARES, MARCOS,
  rangoDeElo, xpPara, xpAcum, nivelDe, paisDe, avatarDe, marcoDe,
} from '../src/game/core/c02_cfg_escena.js';

let ok = 0, fails = [];
const CHK = (cond, msg) => { if (cond) ok++; else fails.push(msg); };

// 1 · Escala de rangos: 21 entradas, ordenadas, cubren 0..∞ sin huecos
CHK(RANGOS_ELO.length === 21, `rangos=${RANGOS_ELO.length} (esperado 21)`);
let prevMax = -1, hueco = false;
for (const r of RANGOS_ELO) {
  if (r.min !== prevMax + 1 && !(prevMax < 0 && r.min === 0)) hueco = true;
  prevMax = r.max;
}
CHK(!hueco && prevMax === Infinity, `huecos en la escala (fin=${prevMax})`);
CHK(RANGOS_ELO[0].min === 0 && RANGOS_ELO[3].min === 1000,
  'inicio: Novato III en 0 y Amateur III en 1000 (ELO inicial del juego)');

// 2 · rangoDeElo: bordes exactos de la tabla del dueño
const bordes = [[0, 'Novato III'], [799, 'Novato III'], [800, 'Novato II'],
  [999, 'Novato I'], [1000, 'Amateur III'], [1299, 'Amateur I'],
  [1599, 'Club I'], [1899, 'Competidor I'], [2199, 'Semiprofesional I'],
  [2499, 'Profesional I'], [2500, 'Maestro'], [2899, 'Gran Maestro'],
  [2900, 'Leyenda Olímpica'], [9999, 'Leyenda Olímpica'], [-50, 'Amateur III']];
for (const [elo, esperado] of bordes) {
  CHK(rangoDeElo(elo).es === esperado, `rangoDeElo(${elo})=${rangoDeElo(elo).es} ≠ ${esperado}`);
}

// 3 · Curva XP monótona + calibración al mock del dueño (L27→28 ≈ 5.000)
let mono = true;
for (let n = 1; n < 80; n++) if (xpPara(n + 1) <= xpPara(n)) mono = false;
CHK(mono, 'curva XP monótona creciente');
CHK(Math.abs(xpPara(27) - 5000) <= 600, `xpPara(27)=${xpPara(27)} ≈ 5.000 (mock del dueño)`);
CHK(nivelDe(0) === 1 && nivelDe(xpAcum(10)) === 10 && nivelDe(xpAcum(28)) === 28,
  'nivelDe deriva el nivel del XP exactamente');
CHK(nivelDe(-5) === 1 && nivelDe('x') === 1, 'nivelDe tolera basura');

// 4 · Catálogos: ids únicos, costes enteros ≥0 o null, locks con gramática
const LOGROS_OK = ['primera', 'racha3', 'gigante', 'maraton', 'superviv', 'aces10',
  'r10', 'r20', 'p1', 'p5', 'all9', 'm50', 'm100', 'x3', 'leg', 'or5'];
const lockOk = (l) => l == null ||
  (typeof l === 'string' && l.indexOf('logro:') === 0 && LOGROS_OK.indexOf(l.slice(6)) >= 0) ||
  (typeof l === 'string' && l.indexOf('elo:') === 0 && parseInt(l.slice(4), 10) > 0);
const costOk = (c) => c == null || (Number.isInteger(c) && c > 0);
CHK(new Set(PAISES.map((p) => p.id)).size === PAISES.length && PAISES.length >= 60,
  `países únicos=${PAISES.length}`);
CHK(new Set(AVATARES.map((a) => a.id)).size === AVATARES.length && AVATARES.length === 20,
  `avatares únicos=20 (${AVATARES.length})`);
CHK(new Set(MARCOS.map((m) => m.id)).size === MARCOS.length && MARCOS.length === 10,
  `marcos únicos=10 (${MARCOS.length})`);
CHK(PAISES.every((p) => /^[A-Z]{2}$/.test(p.id) && p.es && p.en && p.f && Array.isArray(p.f.c) && p.f.c.length),
  'países: ISO-2 + nombres es/en + spec de bandera');
CHK(AVATARES.every((a) => costOk(a.coste) && lockOk(a.lock) && a.f && a.f.tipo),
  'avatares: coste/lock válidos');
CHK(MARCOS.every((m) => costOk(m.coste) && lockOk(m.lock) && m.col && m.esp > 0),
  'marcos: coste/lock válidos');
CHK(AVATARES[0].id === 'pinguino' && AVATARES[0].coste == null && AVATARES[0].lock == null,
  'avatar por defecto SIEMPRE existe (pinguino, gratis)');
CHK(MARCOS[0].id === 'bronce' && MARCOS[0].coste == null && MARCOS[0].lock == null,
  'marco por defecto SIEMPRE existe (bronce, gratis)');
// algún desbloqueo por logro y por ELO (petición del dueño: mezcla)
CHK(AVATARES.some((a) => a.lock && a.lock.indexOf('logro:') === 0) &&
    MARCOS.some((m) => m.lock && m.lock.indexOf('elo:') === 0),
  'mezcla de desbloqueos logro+ELO presente');

// 5 · Helpers de fallback: id inválido → default, jamás undefined
CHK(paisDe('ZZ') === null && paisDe('ES').id === 'ES', 'paisDe sanea');
CHK(avatarDe('hack').id === 'pinguino' && avatarDe('gato').id === 'gato', 'avatarDe sanea');
CHK(marcoDe('x').id === 'bronce' && marcoDe('neon').id === 'neon', 'marcoDe sanea');

// 6 · Tablas de economía: números del PLAN (verificados con Python)
CHK(MONEDAS_ACCION.iaV === 25 && MONEDAS_ACCION.iaD === 8 && MONEDAS_ACCION.p2pV === 40 &&
    MONEDAS_ACCION.p2pTopeDia === 10, 'economía v2: IA 25/8 · P2P 40 tope 10/día');
CHK(XP_ACCION.partidoV === 40 && XP_ACCION.p2pV === 60 && XP_ACCION.champTitulo === 250,
  'XP por acción del PLAN');

console.log(`\nDATOS MI PERFIL r156: ${ok} OK · ${fails.length} FALLOS`);
if (fails.length) { fails.forEach((f) => console.log('  ✗ ' + f)); process.exit(1); }
