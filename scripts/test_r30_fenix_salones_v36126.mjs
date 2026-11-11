#!/usr/bin/env node
/* CRAZY PING PONG · r30 · v3.6.144-SDK6 · FASE 146 · TEST: FÉNIX JUGABLE +
 * SALONES DE LUJO IA.
 *
 *   A · SÚPER FÉNIX — DINÁMICA NORMAL (orden del dueño tras probar la
 *       r29: «El efecto de Súper Fénix — no es jugable mantener los
 *       efectos pero que la dinámica del juego sea la de una partida
 *       normal con una pequeña penalización para la IA. … me daba la
 *       sensación de que al activar el superpoder la bola salía
 *       disparada a mucha velocidad de forma incontrolable… debe
 *       permitir una partida normal solo que con la pequeña
 *       penalización para la IA, los saques deben permitirse normales»)
 *       → CAUSA RAÍZ: el bloque 5.55b de r26b/r29 multiplicaba la
 *       velocidad de la bola CADA FRAME del rally (×1,18 compuesto,
 *       tope 26 m/s) — la bola se disparaba en décimas y arrastraba el
 *       saque. CURA: boost ANULADO (cero FENIX_MUL/FENIX_CAP en código,
 *       cero multiplyScalar del poder), los efectos SE QUEDAN (fuego
 *       del Wizard: _buildFenixFx + _fenixFrame + estallidos en los
 *       eventos 'table'/'paddle' + estela TRAIL_PODER.fenix + tinta
 *       brasa) y la ventaja es la PEQUEÑA penalización de la IA:
 *       FENIX_OUT_P = 0.15 en las DOS palas rivales (rival 1 y rival 2
 *       de dobles), guard state==='rally' (el saque de la IA — estado
 *       'serve' guiado — jamás se sabotea: SAQUES NORMALES), reutiliza
 *       el helper _oscuridadFalla (apunta 0,25–0,70 m más allá de la
 *       línea de fondo; c04/c05 intactos).
 *
 *   B · SALONES DE LUJO IA — «Vuelvo a insistir en lo cutre de los
 *       halles que has creado nuevos, fíjate en el arte y nivel de
 *       detalle del Campeonato de la Locura y el Campeonato de la
 *       magia… Debe invocar a los skills de arte y generación de
 *       imagen para decorar e ilustrar todos los planos con gran
 *       riqueza de detalles gráficos busca referencias reales de esos
 *       entornos y adáptalas a nuestro espacio» → los 6 planos de los
 *       3 salones (neon · observatorio · dojo) regenerados con el
 *       modelo de generación de imagen (18 ilustraciones ricas,
 *       referencias reales de arcades ochenteros / cúpula ISS /
 *       dojo japonés consultadas vía image-search), recortados al
 *       tamaño EXACTO de la spec v3.6.28 (frente/fondo 1849×864 ·
 *       laterales 2395×864 · suelo/techo 1296×1678) con
 *       _r30_gen_halls.mjs + _r30_postproceso_halls.py. Riqueza
 *       exigida: cada salón pesa MÁS que su versión plana r28.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 sha256 BYTE-EXACTO contra la r26b
 *   (df8f71a3… / 8bb62082…).
 *
 * Uso: node --no-warnings scripts/test_r30_fenix_salones_v36126.mjs
 */
import { readFileSync, statSync } from 'node:fs';
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
const vjson = JSON.parse(lee('src/game/VERSION.json'));

/* — 1 · SELLOS · v3.6.144-SDK6 · FASE 146 ————————————————————————————— */
console.log('1 · SELLOS · v3.6.144-SDK6 · FASE 146');
chk(vjson.version === '3.6.144-SDK6', 'VERSION.json: 3.6.144-SDK6');
chk(vjson.fase === 146, 'FASE 146');
chk(vjson.faseNombre === 'Los iconos del Arcano nacen cargados — precalentamiento de la galería y repintado onload de la ficha', 'faseNombre');
const game = lee('public/game.html');
chk(game.includes('3.6.144-SDK6'), 'bundle con sello vigente');
const c00 = lee('src/game/core/c00_pre_three.js');
chk(c00.includes("const VERSION = '3.6.144-SDK6'"), 'sello c00 = 3.6.144-SDK6');
chk(lee('public/sw.js').includes("CACHE = 'crazypp-v3.6.144-SDK6'"),
  'sw.js CACHE v3.6.144-SDK6 (purga de cachés viejas)');
chk(vjson.tamano === 11540068, 'tamaño del build: 11.504.235 B');
chk(lee('src/game/GOLDEN_SHA256.txt').includes(
  '0fd11519a5702477323ffc4f31c37f4badae5317c5b89174b56b8e9f5716eb1a'),
'golden 10a24300… (build byte-exacto)');
chk(sha256('public/game.html') ===
  '0fd11519a5702477323ffc4f31c37f4badae5317c5b89174b56b8e9f5716eb1a',
'game.html REAL casan con golden');

/* — 2 · FÉNIX · EL BOOST ESTÁ ANULADO (dinámica normal) ———————————————— */
console.log('2 · FÉNIX · dinámica NORMAL — cero boost de rapidez');
chk(!c12.includes('const FENIX_MUL'), 'constante FENIX_MUL retirada');
chk(!c12.includes('const FENIX_CAP'), 'constante FENIX_CAP retirada');
chk(!c12.includes('multiplyScalar(FENIX'), 'ningún multiplyScalar del poder');
chk(!c12.includes('setLength(FENIX_CAP'), 'ningún tope de velocidad del poder');
chk(!/5\.55b\).*\n.*FENIX_MUL/.test(c12), 'bloque 5.55b del boost desaparecido');
chk(c12.includes('const FENIX_DUR = 10;'), 'ventana Fénix intacta (10 s)');
chk(c12.includes('ANULADO por orden del dueño'), 'crónica del veto en el código');

/* — 3 · FÉNIX · LOS EFECTOS SE QUEDAN (el dueño: «mantener los efectos») */
console.log('3 · FÉNIX · efectos de fuego INTACTOS');
chk(c12.includes('_buildFenixFx()'), 'fuego real del Wizard (_buildFenixFx)');
chk(c12.includes('_fenixEstallido('), 'explosión de ascuas (_fenixEstallido)');
chk((c12.match(/_fenixEstallido\(e\.pos\)/g) || []).length >= 2,
  'ascuas en los DOS eventos (table y paddle)');
chk(c12.includes('_fenixFrame(dt)'), 'llamas por frame (_fenixFrame)');
chk(c12.includes('_fenixTintAplicar'), 'tinta brasa de la bola');
chk(c12.includes('TRAIL_PODER.fenix'), 'estela naranja');
chk(c12.includes('0xff5a12'), 'tinta brasa del fuego de magia v2.120');

/* — 4 · FÉNIX · LA PEQUEÑA PENALIZACIÓN DE LA IA (15 %) ———————————————— */
console.log('4 · FÉNIX · pequeña penalización IA (15 %, saques normales)');
chk(c12.includes('const FENIX_OUT_P = 0.15;'), 'FENIX_OUT_P = 0.15');
chk((c12.match(/Math\.random\(\) < FENIX_OUT_P/g) || []).length === 2,
  'sorteo de falta en las DOS palas rivales (rival 1 + rival 2 dobles)');
chk((c12.match(/this\._fenixT > 0 && this\.rules\.state === 'rally'/g) || []).length >= 2,
  'guard de rally en la penalización');
chk((c12.match(/catch \(eFeF2?\)/g) || []).length === 2,
  'helper _oscuridadFalla reutilizado (2 llamadas Fénix)');
chk(!/FENIX_OUT_P[\s\S]{0,200}'serve'/.test(c12), 'el saque de la IA no se toca');
chk(c12.includes('también come la falta pequeña'), 'dobles: rival 2 incluido');

/* — 5 · SALONES IA · 18 PLANOS CON LAS MEDIDAS EXACTAS ————————————————— */
console.log('5 · SALONES IA · 18 planos, spec EXACTA');
const SOF_JPEG = (buf) => {
  // dimensiones reales del JPEG (marcador SOF0/SOF2)
  for (let i = 2; i < buf.length - 9;) {
    if (buf[i] !== 0xff) { i++; continue; }
    const m = buf[i + 1];
    if (m === 0xc0 || m === 0xc1 || m === 0xc2 || m === 0xc3) {
      return [buf.readUInt16BE(i + 7), buf.readUInt16BE(i + 5)];
    }
    const len = buf.readUInt16BE(i + 2);
    i += 2 + len;
  }
  return null;
};
const SPEC = { frente: [1849, 864], fondo: [1849, 864], izquierda: [2395, 864],
  derecha: [2395, 864], suelo: [1296, 1678], techo: [1296, 1678] };
const RIQUEZA = { neon: 1_600_000, observatorio: 1_700_000, dojo: 1_500_000 };
for (const sala of ['neon', 'observatorio', 'dojo']) {
  let bytes = 0;
  for (const [plano, [an, al]] of Object.entries(SPEC)) {
    const p = `public/assets/hall/${sala}/${plano}.jpg`;
    let bien = false;
    try {
      const buf = readFileSync(raiz + p);
      bytes += buf.length;
      const dim = SOF_JPEG(buf);
      bien = !!dim && dim[0] === an && dim[1] === al;
    } catch { bien = false; }
    chk(bien, `${sala}/${plano}.jpg ${an}×${al} exacto`);
  }
  chk(bytes > RIQUEZA[sala],
    `${sala}: riqueza ${(bytes / 1048576).toFixed(2)} MB > arte plano r28`);
}

/* — 6 · GENERADORES DE LA RONDA ————————————————————————————————————————— */
console.log('6 · GENERADORES r30 (IA + postproceso)');
chk(statSync(raiz + 'scripts/_r30_gen_halls.mjs').size > 3000,
  '_r30_gen_halls.mjs (18 prompts IA con estilo Locura/Magia)');
chk(statSync(raiz + 'scripts/_r30_postproceso_halls.py').size > 1500,
  '_r30_postproceso_halls.py (recorte EXACTO + realce)');

/* — 7 · FÍSICA INTACTA · c04/c05 BYTE-EXACTO ——————————————————————————— */
console.log('7 · FÍSICA · c04/c05 byte-exacto contra la r26b');
chk(sha256('src/game/core/c04_fisica_ccd.js') ===
  'df8f71a3a91e06b6f3e31e21baf2eee78cb563defd358d4560a7bb6fb1aa70ec',
  'c04_fisica_ccd.js = df8f71a3…');
chk(sha256('src/game/core/c05_colisiones_ia_golpeo.js') ===
  '8bb620820e4974d4ccab8308060d4b8fd7328c812b103f9309bd98654cf81d65',
  'c05_colisiones_ia_golpeo.js = 8bb62082…');

/* — 8 · RESULTADO ————————————————————————————————————————————————————— */
console.log(`RESULTADO: ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
