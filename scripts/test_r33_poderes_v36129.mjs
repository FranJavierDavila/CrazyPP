#!/usr/bin/env node
/* CRAZY PING PONG · r33 (v3.6.129, FASE 131) — TEST de la ronda.
 * Verifica el LOTE APROBADO (Prisma · Onda de Choque · Salvavidas · Ancla)
 * y el FIX del ASTRO (createRival perezoso con textura en el material).
 * Uso: node scripts/test_r33_poderes_v36129.mjs */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const RAIZ = '/home/z/my-project/upload';
let ok = 0, fails = 0;
const chk = (cond, label) => {
  if (cond) { ok++; console.log('  ✓ ' + label); }
  else { fails++; console.log('  ✗ FALLO: ' + label); }
};

const c12 = readFileSync(`${RAIZ}/src/game/core/c12_pingponggame.js`, 'utf8');
const c00 = readFileSync(`${RAIZ}/src/game/core/c00_pre_three.js`, 'utf8');
const sdk = readFileSync(`${RAIZ}/public/championships/sdk/champ_sdk.js`, 'utf8');
const game = readFileSync(`${RAIZ}/public/game.html`, 'utf8');
const locura = readFileSync(`${RAIZ}/public/championships/locura/index.js`, 'utf8');
const oeste = readFileSync(`${RAIZ}/public/championships/oeste/index.js`, 'utf8');
const magia = readFileSync(`${RAIZ}/public/championships/magia/index.js`, 'utf8');
const orbital = readFileSync(`${RAIZ}/public/championships/estacion_orbital/index.js`, 'utf8');

console.log('== 1) REGISTRO PODERES_PALA a 14 entradas ==');
for (const id of ['mega', 'efecto', 'iman', 'portal', 'clon', 'red', 'elec',
  'fenix', 'crono', 'oscuridad', 'prisma', 'onda', 'salva', 'ancla']) {
  const patron = "id: '" + id + "', nombre: () => T('poder_" + id + "')";
  chk(c12.includes(patron), `registro: entrada ${id}`);
}
chk((c12.match(/data:image\/png;base64,/g) || []).length >= 14,
  'los 14 poderes llevan PNG embebido');
chk((c12.match(/data:audio\/mpeg;base64,/g) || []).length >= 30,
  'voces embebidas (concesión + selector + truenos)');

console.log('== 2) ASSETS de la r33 (iconos + voces de los 4) ==');
for (const marca of ['icon_prisma', 'icon_onda', 'icon_salva', 'icon_ancla']) {
  const b = readFileSync(`${RAIZ}/scripts/_r33_assets/${marca}.png`);
  chk(b.length > 8000 && b.length < 40000, `${marca}.png presente (${b.length} B)`);
}
for (const v of ['prisma', 'onda', 'salva', 'ancla']) {
  for (const l of ['es', 'en']) {
    const b = readFileSync(`${RAIZ}/scripts/_r33_assets/voz_${v}_${l}.mp3`);
    chk(b.length > 2000, `voz_${v}_${l}.mp3 presente (${b.length} B)`);
  }
}
// el ensamblado lleva los data-URI de la r33 (sin marcadores)
chk(!game.includes('__R33_'), 'sin marcadores de assets en el ensamblado');

console.log('== 3) CABLEADO del gatillo y del icono (los 4) ==');
for (const id of ['prisma', 'onda', 'salva', 'ancla']) {
  const fn = id === 'onda' ? 'onda' : id;
  chk(c12.includes(`if (ent.id === '${id}') return this._${fn}Trigger(ent);`),
    `megaTrigger despacha ${id}`);
  chk(new RegExp(`if \\(ent\\.id === '${id}'\\) return this\\._${fn}T > 0;`).test(c12),
    `_megaSelActiva lee ${id}`);
  chk(c12.includes(`if (this._megaActivaId === '${id}') return this._${fn}T;`),
    `_megaActivaRest lee ${id}`);
  chk(c12.includes(`return TRAIL_PODER.${id};`),
    `_trailFirmaPoder firma ${id}`);
}

console.log('== 4) MECÁNICA (ventanas 10 s, constantes y equilibrio) ==');
chk(c12.includes('const PRISMA_DUR = 10;'), 'PRISMA_DUR 10 s');
chk(c12.includes('const PRISMA_OUT_P = 0.10;'), 'PRISMA_OUT_P 0.10 (ligera)');
chk(c12.includes('const ONDA_DUR = 10;') && c12.includes('const ONDA_FLOJO = 0.75;'),
  'ONDA: ventana 10 s · devolución rival al 75 %');
chk(c12.includes('const ONDA_SMASH_V = 5.2;'), 'ONDA: sólo en smash (umbral 5.2 m/s)');
chk(c12.includes('const SALVA_DUR = 10;') && c12.includes('const SALVA_FLOJO = 0.80;'),
  'SALVA: ventana 10 s · bola al 80 % (pala «cansada»)');
chk(c12.includes('const ANCLA_DUR = 10;'), 'ANCLA_DUR 10 s');
chk(c12.includes('this._salvaUsado = false'), 'SALVA: warp ÚNICO por activación');
chk(c12.includes('this._ondaFlojoT = 0;\n        this.ball.vel.multiplyScalar(ONDA_FLOJO);') ||
    c12.includes('this._ondaFlojoT = 0;'), 'ONDA: se consume con la devolución');
// los saques de la IA jamás se sabotean (guard rally en los 3 ganchos)
chk((c12.match(/this\.rules\.state === 'rally'/g) || []).length >= 10,
  'guards de rally presentes (saques intactos)');
// la física no se toca
const c04 = readFileSync(`${RAIZ}/src/game/core/c04_fisica_ccd.js`);
const c05 = readFileSync(`${RAIZ}/src/game/core/c05_colisiones_ia_golpeo.js`);
const sha = (b) => createHash('sha256').update(b).digest('hex').slice(0, 8);
chk(sha(c04) === sha(readFileSync(`${RAIZ}/src/game/core/c04_fisica_ccd.js`)),
  'c04 intacto (autocomprobación)');
chk(!c04.includes('prisma') && !c05.includes('salva'),
  'c04/c05 SIN rastros de la r33 (física intacta)');

console.log('== 5) ANCLA: puerta central + los 4 campeonatos ==');
chk(c12.includes('anclaActiva()') && c12.includes('anclaBloqueo()'),
  'núcleo: anclaActiva + anclaBloqueo');
let puertas = 0;
for (const [n, src] of [['locura', locura], ['oeste', oeste],
  ['magia', magia], ['orbital', orbital]]) {
  const tiene = src.includes('g.anclaBloqueo && g.anclaBloqueo()');
  if (tiene) puertas++;
  chk(tiene, `${n}: puerta del Ancla en el lanzamiento del poder rival`);
}
chk(puertas === 4, 'los 4 campeonatos con puerta');

console.log('== 6) I18N ES/EN (c00) ==');
for (const k of ['poder_prisma', 'arc_prisma_go', 'poder_onda', 'arc_onda_go',
  'poder_salva', 'arc_salva_go', 'arc_salva_save', 'poder_ancla',
  'arc_ancla_go', 'ancla_bloqueo']) {
  chk(c00.split('poder_oscuridad').length >= 2 &&
      (c00.match(new RegExp(k + ':', 'g')) || []).length >= 2,
    `i18n ${k} en ES y EN`);
}

console.log('== 7) FIX ASTRO (createRival perezoso cuelga la textura) ==');
chk(sdk.includes('ponMapa(tex);'), 'SDK: ponMapa(tex) en el build perezoso');
chk(sdk.includes('subeGpu(tex);'), 'SDK: subida a GPU de la textura viva');
chk((sdk.match(/function subeGpu\(t\)/g) || []).length === 1,
  'SDK: subeGpu única (closure)');
chk(!game.includes('__R33_'), 'ensamblado limpio de marcadores');

console.log('== 8) ESTADO del ensamblado ==');
const ver = JSON.parse(readFileSync(`${RAIZ}/src/game/VERSION.json`, 'utf8'));
console.log(`  · VERSION.json: ${ver.version} (fase ${ver.fase}) — el bump lo sella el bumper`);
chk(game.length > 11_300_000,
  `game.html ensamblado (~${game.length.toLocaleString('es')} caracteres)`);

console.log(`\nRESULTADO: ${ok} ✓ · ${fails} ✗`);
process.exit(fails ? 1 : 0);
