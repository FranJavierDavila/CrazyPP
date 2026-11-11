#!/usr/bin/env node
/* CRAZY PING PONG · r35 (v3.6.139, FASE 150) — TEST de la ronda.
 * Petición del dueño: «en el superpoder de prisma no se nota la desventaja
 * ni que se está aplicado, refuerza visualmente cambiando el color de la
 * bola por los colores del arcoiris de forma aleatoria mientras duré el
 * super poder».
 *   A · la BOLA pinta arcoíris ALEATORIO (~6 saltos/s) mientras Prisma vive.
 *   B · restauración honesta en _prismaFin (patrón tinte de la Oscuridad).
 *   C · cooperativo: Prisma ↔ Oscuridad se ceden la bola (nadie queda
 *       prisionero de un tinte ajeno; la bola nunca acaba rota).
 *   D · física c04/c05 BYTE-EXACTA (intocada, como siempre).
 * Uso: node scripts/test_r35_prisma_v36139.mjs */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const RAIZ = '/home/z/my-project/upload';
let ok = 0, fails = 0;
const chk = (cond, label) => {
  if (cond) { ok++; console.log('  ✓ ' + label); }
  else { fails++; console.log('  ✗ FALLO: ' + label); }
};
const cuenta = (pajaro, aguja) => pajaro.split(aguja).length - 1;

const c12 = readFileSync(`${RAIZ}/src/game/core/c12_pingponggame.js`, 'utf8');
const vjson = JSON.parse(readFileSync(`${RAIZ}/src/game/VERSION.json`, 'utf8'));
const game = readFileSync(`${RAIZ}/public/game.html`, 'utf8');

console.log('== 1) FIX A · LA BOLA ARCOÍRIS (aleatoria, mientras vive) ==');
chk(cuenta(c12, 'this._prismaBolaT = 0;') === 2,
  `reloj del salto: constructor + aplicar (×2): ${cuenta(c12, 'this._prismaBolaT = 0;')}`);
chk(c12.includes('this._prismaBolaTint = null;    // r35: tinta original de la bola (restaurar)'),
  'estado del tinte en el constructor');
chk(cuenta(c12, 'this._prismaBolaTintAplicar();') === 2,
  'las DOS ramas del trigger aplican el tinte (activar + refresco)');
chk(c12.includes("const h35 = Math.random();      // arcoíris ALEATORIO (no barrido)"),
  'salto ALEATORIO (Math.random, no barrido)');
chk(c12.includes('this._prismaBolaT = 0.16;'),
  'cadencia ~6 saltos/s (0.16 s)');
chk(c12.includes('this.ballMesh.material.color.copy(_colPrisma);'),
  'pinta el COLOR de la bola');
chk(c12.includes('this.ballMesh.material.emissive.copy(_colPrisma);'),
  'pinta el EMISIVO (glow visible en el casco)');
chk(c12.includes('_colPrisma.setHSL(h35, 0.95, 0.62)'),
  'paleta viva (S 0.95 · L 0.62)');
chk(c12.includes('_colPrisma.setHSL(h35, 0.95, 0.30)'),
  'brasa del salto (emisivo L 0.30)');
chk(c12.includes("this._prismaBolaT -= dt;"), 'reloj con dt del frame');
chk(c12.includes("} catch (eB35) { /* el color nunca tumba el frame */ }"),
  'el color nunca tumba el frame (guard)');

console.log('== 2) FIX B · RESTAURACIÓN HONESTA (patrón Oscuridad) ==');
chk(cuenta(c12, '_prismaBolaTintAplicar() {') === 1, 'aplicar: definición única');
chk(cuenta(c12, '_prismaBolaTintRestaurar() {') === 1, 'restaurar: definición única');
chk(c12.includes("this._prismaBolaTintRestaurar();  // r35: la bola vuelve a SU tinta"),
  '_prismaFin restaura la bola SIEMPRE');
chk(c12.includes('if (!this._prismaBolaTint) return;'),
  'restaurar idempotente (guard de tinte nulo)');
chk(c12.includes('col: m.material.color.getHex(),'),
  'guarda el color ORIGINAL (getHex)');
chk(c12.includes("em: m.material.emissive ? m.material.emissive.getHex() : null,"),
  'guarda el emisivo ORIGINAL (o null)');
chk(c12.includes("if (m.material.emissive && f.em !== null) m.material.emissive.setHex(f.em);"),
  'restaura el emisivo sólo si existía');

console.log('== 3) FIX C · COOPERATIVO (nadie queda prisionero) ==');
chk(c12.includes("if (this._prismaBolaTint && this._megaActivaId !== 'prisma') {") &&
    c12.includes('this._prismaBolaTintRestaurar();    // otro poder mandó: soltar YA'),
  'auto-soltado si otro poder toma el testigo');
chk(c12.includes('if (this._oscuridadTint) this._oscuridadTintRestaurar();  // cede la bola'),
  'Prisma cede la bola si Oscuridad la tenía');
chk(c12.includes('if (this._prismaBolaTint) this._prismaBolaTintRestaurar();  // r35: cede la bola'),
  'Oscuridad cede la bola si Prisma la tenía');
chk(cuenta(c12, 'this._prismaBolaTintRestaurar();') === 3,
  `restaurar llamado exactamente 3 veces (fin + autosoltado + cesión de Oscuridad): ${cuenta(c12, 'this._prismaBolaTintRestaurar();')}`);
chk(c12.includes('if (this._oscuridadTint) this._oscuridadTintRestaurar();  // cede la bola') &&
    c12.includes('if (this._prismaBolaTint) this._prismaBolaTintRestaurar();  // r35: cede la bola'),
  'las dos cesiones cruzadas presentes (cada una con SU restaurar)');

console.log('== 4) SIN REGRESIONES · r34 intacto ==');
chk(c12.includes('const enCampoRival = this.ball && this.ball.pos.z < DIMS.tableCenterZ;'),
  'r34: estela arcoíris sólo en campo rival');
chk(c12.includes('return TRAIL_PODER.prisma;'), 'firma de estela prisma intacta');
chk(c12.includes("try { this._prismaFin(); } catch (eP33) { /* */ }"),
  'cortina etapas 2/4 sigue cerrando Prisma');
chk(cuenta(c12, 'this._prismaGuiaT = PRISMA_GUIA_T;') === 1, 'guía del golpeo intacta');
chk(c12.includes('_prismaGuiaNace(pos, vel)'), 'guía nace en el golpeo');

console.log('== 5) FÍSICA BYTE-EXACTA (c04/c05 intocados) ==');
const sha = (p) => createHash('sha256').update(readFileSync(p)).digest('hex');
const c04 = sha(`${RAIZ}/src/game/core/c04_fisica_ccd.js`);
const c05 = sha(`${RAIZ}/src/game/core/c05_colisiones_ia_golpeo.js`);
chk(c04.startsWith('e4abb6eb'), `c04 sha256 e4abb6eb… (${c04.slice(0, 8)})`);
chk(c05.startsWith('8bb62082'), `c05 sha256 8bb62082… (${c05.slice(0, 8)})`);

console.log('== 6) VERSIÓN Y SELLOS ==');
chk(vjson.version === '3.6.147-SDK6', `VERSION.json 3.6.147-SDK6 (${vjson.version})`);
chk(vjson.fase === 150, `FASE 150 (${vjson.fase})`);
chk(game.includes('const VERSION') && game.includes('3.6.147-SDK6'),
  'game.html sellado a 3.6.147-SDK6');
chk(cuenta(game, '_prismaBolaTintAplicar') === 3,
  `game.html: aplicar (def + 2 llamadas) ×3: ${cuenta(game, '_prismaBolaTintAplicar')}`);
chk(cuenta(game, '_prismaBolaTintRestaurar') === 4,
  `game.html: restaurar (def + fin + autosoltado + cesión de Oscuridad) ×4: ${cuenta(game, '_prismaBolaTintRestaurar')}`);
chk(game.includes('const h35 = Math.random()'), 'game.html lleva el salto aleatorio');

console.log(`\nRESULTADO: ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);
