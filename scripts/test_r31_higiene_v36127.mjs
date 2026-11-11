#!/usr/bin/env node
/* CRAZY PING PONG · r31 · v3.6.146-SDK6 · FASE 149 · TEST: HIGIENE TEXTUAL
 * FÉNIX.
 *
 *   A · DEUDA COSMÉTICA PAGADA — el comentario del registro PODERES_PALA
 *       de SÚPER FÉNIX seguía presumiendo el «+18 % de rapidez» de r29
 *       cuando el boost quedó ANULADO en r30 (orden del dueño: dinámica
 *       NORMAL, saques normales, toda la ventaja = FENIX_OUT_P 0.15).
 *       r31 reescribe el bloque: sin la afirmación en tiempo presente,
 *       con la nota histórica del veto. NADA de lógica tocada: solo
 *       comentario (+216 B en el build).
 *
 *   B · COHERENCIA VENTANA↔TEXTO — FENIX_DUR/CRONO_DUR/OSCURIDAD_DUR
 *       (10/10/20 s en código) casan con los avisos del casco i18n
 *       arc_fenix_go / arc_crono_go / arc_oscuridad_go en ES y EN.
 *
 *   C · ÚNICO ×1,18 RESTANTE — el único multiplyScalar(1.18) de c12 es
 *       el poder FUEGO de DUELOS LOCOS (r84, online, por golpeo — NO
 *       por frame, activo por diseño): guard _dlOn('fuego') encima.
 *       Protege contra re-introducir un boost en la ruta de Fénix.
 *
 *   D · SÚPER HIELO sigue anulado (cero rastros vivos) y los sellos de
 *       la ronda: VERSION.json 3.6.146-SDK6 / FASE 149 / build
 *       11.504.235 B / golden 10a24300… / sw.js / badge / hub.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 sha256 BYTE-EXACTO contra la r26b
 *   (df8f71a3… / 8bb62082…).
 *
 * Uso: node --no-warnings scripts/test_r31_higiene_v36127.mjs
 */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');
const sha256 = (p) =>
  createHash('sha256').update(readFileSync(raiz + p)).digest('hex');

const c12 = lee('src/game/core/c12_pingponggame.js');
const c00 = lee('src/game/core/c00_pre_three.js');
const vjson = JSON.parse(lee('src/game/VERSION.json'));
const game = lee('public/game.html');
const cuerpo = lee('src/game/03_body.html');

/* — 1 · SELLOS · v3.6.146-SDK6 · FASE 149 ————————————————————————— */
console.log('1 · SELLOS · v3.6.146-SDK6 · FASE 149');
chk(vjson.version === '3.6.146-SDK6', 'VERSION.json: 3.6.146-SDK6');
chk(vjson.fase === 149, 'FASE 149');
chk(vjson.tamano === 11547159, 'tamaño del build: 11.504.235 B');
chk(vjson.golden ===
  'f8d1859df863f709c7cf0f12bc5a2314087915e6d88cf46c2374e74fb807f1e4',
  'VERSION.json golden 10a24300…');
chk(sha256('public/game.html') ===
  'f8d1859df863f709c7cf0f12bc5a2314087915e6d88cf46c2374e74fb807f1e4',
  'golden 10a24300… (build byte-exacto)');
chk(game.includes('3.6.146-SDK6'), 'bundle con sello vigente');
chk(c00.includes("const VERSION = '3.6.146-SDK6'"), 'sello c00 = 3.6.146-SDK6');
chk(lee('public/sw.js').includes("CACHE = 'crazypp-v3.6.146-SDK6'"),
  'sw.js CACHE v3.6.146-SDK6 (purga de cachés viejas)');
chk(cuerpo.includes('>V3.6.146-SDK6</span>'), 'badge V3.6.146-SDK6 en 03_body');
chk(lee('src/app/descargas/page.tsx').includes('v36139-sdk6'),
  'hub /descargas sellado a v36139-sdk6');

/* — 2 · LA CURA r31 — comentario del registro SIN el boost ———————— */
console.log('2 · HIGIENE FÉNIX · el registro ya no presume el «+18 %»');
// 2a. el bloque nuevo está (con la nota histórica del veto)
chk(c12.includes('este comentario ya NO presume el «+18 % de rapidez» de r29'),
  'registro Fénix: nota r31 del veto presente');
chk(c12.includes('boost quedó ANULADO en r30 por orden del dueño'),
  'registro Fénix: causa del veto documentada');
chk(c12.includes('toda la ventaja de juego es FENIX_OUT_P 0.15'),
  'registro Fénix: la ventaja real es la falta de la IA (15 %)');
// 2b. la frase vieja en tiempo presente desapareció del registro:
//     la ÚNICA «+18 % de rapidez» restante en c12 es la cita entre
//     comillas de la propia nota r31 (línea con «NO presume»)
const lineas18 = c12.split('\n').filter((l) => l.includes('+18 % de rapidez'));
chk(lineas18.length === 1 && lineas18[0].includes('NO presume'),
  `«+18 % de rapidez» solo en la cita del veto (${lineas18.length} línea)`);
// 2c. sin constantes ni multiplicaciones del boost en la ruta Fénix
chk(!c12.includes('FENIX_MUL') || c12.indexOf('FENIX_MUL') ===
      c12.indexOf('FENIX_MUL/FENIX_CAP retiradas'),
  'FENIX_MUL/FENIX_CAP solo en la anotación histórica (retiradas)');
chk(!/fenix[^\n]*multiplyScalar/i.test(c12),
  'cero multiplyScalar en cualquier línea que hable de fenix');
// 2d. la penalización sigue viva en las DOS palas rivales
chk(c12.includes('const FENIX_OUT_P = 0.15'), 'FENIX_OUT_P = 0.15');
chk((c12.match(/FENIX_OUT_P/g) || []).length >= 5,
  'FENIX_OUT_P usado en los bloqueos de la IA (rival 1 y rival 2)');

/* — 3 · ÚNICO ×1,18 RESTANTE = DUELOS LOCOS (r84, por diseño) ————— */
console.log('3 · ÚNICO ×1,18 · FUEGO de DUELOS LOCOS (r84), no Fénix');
const ms118 = [...c12.matchAll(/multiplyScalar\(1\.18\)/g)];
chk(ms118.length === 1,
  `exactamente 1 multiplyScalar(1.18) en c12 (${ms118.length})`);
if (ms118.length === 1) {
  const pre = c12.slice(Math.max(0, ms118.index - 700), ms118.index);
  chk(pre.includes("_dlOn('fuego')"),
    'el ×1,18 vive bajo el guard _dlOn(\'fuego\') (DUELOS LOCOS online)');
  chk(pre.includes('_localHit') || pre.includes('5.6'),
    '…en el bloque de anuncio de MI golpeo (por golpeo, no por frame)');
}

/* — 4 · COHERENCIA VENTANA↔TEXTO (10/10/20 s en ES y EN) —————————— */
console.log('4 · VENTANAS · código↔i18n casan');
chk(c12.includes('const FENIX_DUR = ARCANO_CFG.ventanas.fenix;'), 're-anclada r55: FENIX_DUR = ARCANO_CFG (10 s)');
chk(c12.includes('const CRONO_DUR = ARCANO_CFG.ventanas.crono;'), 're-anclada r55: CRONO_DUR = ARCANO_CFG (10 s)');
chk(c12.includes('const OSCURIDAD_DUR = ARCANO_CFG.ventanas.oscuridad;'), 're-anclada r55: OSCURIDAD_DUR = ARCANO_CFG (20 s)');
for (const [arc, seg] of [['arc_fenix_go', '10 s'],
  ['arc_crono_go', '10 s'], ['arc_oscuridad_go', '20 s']]) {
  const esc = seg.replace('.', '\\.');
  // ES: la línea con «¡» inicial (solo el bloque castellano) — exactamente 1
  chk((c00.match(new RegExp(`${arc}: '¡[^']*${esc}`, 'g')) || []).length === 1,
    `ES ${arc} anuncia ${seg}`);
  // ES+EN: las dos líneas del aviso (count global con flag g)
  chk((c00.match(new RegExp(`${arc}: '[^']*${esc}`, 'g')) || []).length === 2,
    `ES+EN ${arc} anuncia ${seg}`);
}

/* — 5 · SÚPER HIELO sigue anulado (cero rastros vivos) ———————————— */
console.log('5 · HIELO · sigue anulado desde r29');
chk(!c12.includes("{ id: 'hielo'"), 'PODERES_PALA sin entrada hielo');
chk(!/superHielo|SUPER_HIELO|_hieloT/.test(c12),
  'cero identificadores vivos de superHielo');
chk(c12.includes('sustituye a hielo'),
  'solo queda la anotación histórica «sustituye a hielo»');

/* — 6 · FÍSICA INTACTA · c04/c05 byte-exacto contra la r26b ———————— */
console.log('6 · FÍSICA · c04/c05 byte-exacto');
chk(sha256('src/game/core/c04_fisica_ccd.js') ===
  'df8f71a3a91e06b6f3e31e21baf2eee78cb563defd358d4560a7bb6fb1aa70ec',
  'c04_fisica_ccd.js = df8f71a3…');
chk(sha256('src/game/core/c05_colisiones_ia_golpeo.js') ===
  '8bb620820e4974d4ccab8308060d4b8fd7328c812b103f9309bd98654cf81d65',
  'c05_colisiones_ia_golpeo.js = 8bb62082…');

/* — 7 · EL RESTO DEL REGISTRO intacto (10 poderes) ————————————————— */
console.log('7 · REGISTRO · 10 poderes con voz e icono');
for (const id of ['mega', 'efecto', 'iman', 'portal', 'clon', 'red',
  'elec', 'fenix', 'crono', 'oscuridad']) {
  chk(c12.includes(`{ id: '${id}'`), `poder ${id} en PODERES_PALA`);
}
chk((c12.match(/data:image\/png;base64,/g) || []).length >= 11,
  'iconos base64 embebidos (≥11)');
chk((c12.match(/data:audio\/mpeg;base64,/g) || []).length >= 34,
  'voces MP3 embebidas (≥34)');

console.log(`\nRESULTADO: ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
