#!/usr/bin/env node
/* CRAZY PING PONG · r26 · v3.6.121 · TEST: NIEBLA DENSA + MÁS RAYOS +
 * BARRERA ELÉCTRICA EN LA SÚPER RED.
 *
 * Las dos peticiones del dueño (informe tras la r25):
 *
 *   A · «El super efecto de electricidad tenemos que mejorarlo bastante,
 *        las nubes están muy cutres debemos sustituirlas por una especie
 *        de niebla muy densa que simula que son nubes, y deben descargar
 *        bastantes más rayos de tormenta» — el banco de 2 borrones sprite
 *        muere: NIEBLA DENSA de ELEC_NIEBLA_N=14 puffs suaves (textura de
 *        gradiente radial, cero bordes duros) que HIERVE con fase propia
 *        por puff y se ILUMINA con cada descarga (gris pizarra ↔ azul
 *        pálido con el destello). Los rayos pasan de 3 → ELEC_RAYOS_N=10
 *        con RÁFAGAS de hasta 3 por descarga y cadencia 1.15→0.42 s
 *        (≈35 rayos por ventana de 10 s). Trueno con volumen vivo.
 *
 *   B · «En el super poder de red, el efecto también más vistoso que la
 *        red al crecer parezca una barrera de electricidad» — BARRERA
 *        ELÉCTRICA: cuerpo aditivo cian pegado a la red VIVA (lee DIMS
 *        cada frame), 7 arcos dentados regenerados cada 0,085 s con
 *        parpadeo, riel superior nervioso, chispas del pool de la casa
 *        y zumbido eléctrico. Sólo capa de render: DIMS.netTopY sigue
 *        siendo la única verdad y la física c04/c05 no sabe que existe.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 (física), c09 (códec) y c02/c07 SIN
 *   una sola línea nueva — diff vacío contra el commit de la r25.
 *
 * Uso: node --no-warnings scripts/test_r26_sup_v36121.mjs
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
const c07 = lee('src/game/core/c07_escena_sala.js');

/* — 1 · NIEBLA DENSA · adiós borrones ————————————————————————————————— */
console.log('1 · NIEBLA DENSA · banco de puffs que hierve');
chk(c12.includes('const ELEC_NIEBLA_N = 14;'), 'ELEC_NIEBLA_N = 14 puffs (antes 2 borrones)');
chk(c12.includes('const ELEC_RAYOS_N = 10;'), 'ELEC_RAYOS_N = 10 rayos en el pool (antes 3)');
chk(!c12.includes('const borron'), 'fuera el pintor de BORRONES (nubes cutres)');
chk(c12.includes("createRadialGradient(64, 64, 4, 64, 64, 62)"), 'textura suave: gradiente radial (bordes que se funden)');
chk(c12.includes("gRad.addColorStop(0, 'rgba(255,255,255,0.95)');"), 'núcleo opaco del puff');
chk(c12.includes("gRad.addColorStop(1, 'rgba(255,255,255,0)');"), 'borde transparente del puff (niebla, no cartón)');
chk(c12.includes('cv.width = 128; cv.height = 128;'), 'lienzo del puff 128×128');
chk(c12.includes('const niebla = [];'), 'banco de niebla');
chk(c12.includes('let sem = 20261126;'), 'LCG semillado (misma niebla en cada build/QA — patrón casa)');
chk(c12.includes('const NIEBLA_COLS = [0x39404e, 0x454e5e, 0x2f3542, 0x525c6e, 0x3c4453];'), 'paleta pizarra de tormenta');
chk(c12.includes('const lit = new THREE.Color(0xbdd3ea);       // iluminada por el rayo'), 'color de niebla ILUMINADA por la descarga');
chk(c12.includes('op: 0.34 + rnd() * 0.18,                   // solape → densidad'), 'opacidades solapadas = DENSIDAD');
chk(c12.includes('orb: 0.06 + rnd() * 0.10,                  // radio de hervor'), 'hierve: radio orbital por puff');
chk(c12.includes('sp: 0.22 + rnd() * 0.30,                   // velocidad de hervor'), 'hierve: velocidad propia por puff');
chk(c12.includes('f: rnd() * Math.PI * 2,                    // fase propia de hervor'), 'fase propia (nada de movimiento de bloque)');
chk(c12.includes('this._elecFx = { niebla, rayos, rayosIx: 0, metales };'), 'el pool lleva la niebla');
chk(c12.includes('for (const nb of fx.niebla) nb.visible = vis; // la opacidad la pone _elecFrame'), 'visibilidad del banco en _elecFxVis');

/* — 2 · HIERVO + ILUMINACIÓN · frame de la niebla ————————————————————— */
console.log('2 · FRAME · la niebla hierve y se ilumina con cada rayo');
chk(c12.includes('const fl = this._elecFlashT > 0 ? Math.min(1, this._elecFlashT / 0.25) : 0;'), 'flash normalizado del destello');
chk(c12.includes('nb.position.x = U.x0 + Math.sin(tt * U.sp + U.f) * U.orb;'), 'hervido X (fase + velocidad propias)');
chk(c12.includes('nb.position.z = U.z0 + Math.cos(tt * U.sp * 0.8 + U.f) * U.orb * 0.7;'), 'hervido Z (masa tridimensional)');
chk(c12.includes('const br = 1 + Math.sin(tt * 0.9 + U.f * 3.0) * 0.07;   // respiración'), 'respiración de escala (niebla viva)');
chk(c12.includes('nb.scale.set(U.sxB * br, U.syB * br, 1);'), 'escala respirando');
chk(c12.includes('nb.material.opacity = (U.op + fl * 0.30) * k;   // con la tormenta'), 'el destello GANA densidad de niebla');
chk(c12.includes('c.setRGB(U.r0 + (U.r1 - U.r0) * fl, U.g0 + (U.g1 - U.g0) * fl,'), 'la niebla se ILUMINA con el rayo (setRGB, cero Color nuevos)');
chk(c12.includes('const U = nb.userData;'), 'userData directo (cero asignaciones por frame)');

/* — 3 · BASTANTES MÁS RAYOS · ráfagas ————————————————————————————————— */
console.log('3 · MÁS RAYOS · cadencia 0,42 s + ráfagas de hasta 3');
chk(c12.includes('const ELEC_BOLT_CD = 0.42;'), 'cadencia 1.15 → 0.42 s');
chk(c12.includes('// cadencia de descargas (con jitter natural) — r26 (v3.6.121): RÁFAGAS'), 'bloque de ráfagas r26');
chk(c12.includes('if (Math.random() < 0.38) {\n        try { this._elecRayo(); } catch (eR2) { /* */ }\n      }'), 'ráfaga: 2.º rayo (38 %)');
chk(c12.includes('if (Math.random() < 0.16) {\n        try { this._elecRayo(); } catch (eR3) { /* */ }\n      }'), 'ráfaga: 3.er rayo (16 %)');
chk(c12.includes('// puff emisora: el MÁS CERCANO al objetivo del banco de niebla (r26)'), 'emisora = puff más cercano (coherencia niebla↔rayo)');
chk(c12.includes('if (dN < md) { md = dN; nube = nbN; }'), 'búsqueda del emisor sin asignaciones');
chk(c12.includes('g.gain.value = 0.55 + Math.random() * 0.4;   // r26: volumen vivo'), 'trueno con volumen variable (35 rayos sin fatiga)');
chk(c12.includes("geo.setAttribute('position',\n        new THREE.BufferAttribute(new Float32Array(9 * 3), 3));"), 'rayos siguen siendo polilíneas recicladas de 9 puntos');
chk(c12.includes('for (let i = 0; i < ELEC_RAYOS_N; i++) {'), 'pool de rayos por constante');

/* — 4 · BARRERA ELÉCTRICA · la SÚPER RED se viste de campo ———————————— */
console.log('4 · BARRERA ELÉCTRICA · la red crecida es un campo de energía');
chk(c12.includes('const RED_ARC_N = 7;        // polilíneas de arco en la barrera de la red'), 'RED_ARC_N = 7 arcos');
chk(c12.includes('const RED_ARC_PTS = 12;     // puntos por arco (jitter vivo)'), 'RED_ARC_PTS = 12 puntos');
chk(c12.includes('const RED_ARC_CD = 0.085;   // s entre regeneraciones de arcos (parpadeo)'), 'regeneración cada 0,085 s (parpadeo eléctrico)');
chk(c12.includes('const RED_BODY_OP = 0.13;   // opacidad base del cuerpo del campo eléctrico'), 'cuerpo del campo al 0,13');
chk(c12.includes('const RED_BUZZ_CD = 0.42;   // s entre zumbidos eléctricos'), 'zumbido periódico');
chk(c12.includes('const RED_SPARK_CD = 1.4;   // s entre chispas del riel superior'), 'chispas del riel periódicas');
chk(c12.includes('_buildRedFx() {'), '_buildRedFx (pool reutilizable, una vez)');
chk(c12.includes('_redFxVis(vis) {'), '_redFxVis');
chk(c12.includes('_redFrame(dt) {'), '_redFrame');
chk(c12.includes('new THREE.PlaneGeometry(1, 1),'), 'cuerpo: plano unidad (se ajusta en vivo)');
chk(c12.includes('color: 0x59d6ff, transparent: true, opacity: RED_BODY_OP,'), 'cuerpo cian eléctrico');
chk(c12.includes('side: THREE.DoubleSide, blending: THREE.AdditiveBlending,'), 'cuerpo aditivo doble cara (visible desde ambos campos)');
chk(c12.includes('color: i % 2 ? 0x9fd8ff : 0xbfe4ff, transparent: true, opacity: 0,'), 'arcos alternando dos azules');
chk(c12.includes('color: 0xdff2ff, transparent: true, opacity: 0,'), 'riel superior más brillante');
chk(c12.includes('new THREE.BufferAttribute(new Float32Array(RED_ARC_PTS * 3), 3));'), 'geometrías recicladas (cero asignaciones por frame)');
chk(c12.includes('if (this._redFx) return;'), 'build idempotente');
chk(c12.includes('fx.cuerpo.scale.set(W * 2, netH, 1);'), 'cuerpo pegado a la red VIVA (ancho)');
chk(c12.includes('fx.cuerpo.position.set(0, topY + netH / 2, zC);'), 'cuerpo pegado a la red VIVA (posición)');
chk(c12.includes('(D.netTopY != null ? D.netTopY : topY + 0.1525) - topY);'), 'lee DIMS cada frame (una sola verdad)');
chk(c12.includes('const pulso = 0.75 + 0.25 * Math.sin(tt * 9.0);'), 'pulso del campo');
chk(c12.includes('fx.cuerpo.material.opacity = (RED_BODY_OP + fl * 0.30) * pulso;'), 'destello de energizado sobre el cuerpo');
chk(c12.includes('if (Math.random() < 0.45) continue;    // no todos cada ciclo'), 'arcos aleatorios por ciclo (nervio eléctrico)');
chk(c12.includes('const h = topY + netH * (0.08 + Math.random() * 0.86);'), 'arcos a TODAS las alturas del campo');
chk(c12.includes('const zL = zC + (Math.random() < 0.5 ? -0.006 : 0.006);'), 'arcos a ambas caras de la red');
chk(c12.includes('a.userData.vida = 0.16;'), 'vida corta de arco = parpadeo');
chk(c12.includes('(0.45 + 0.55 * Math.sin(tt * 21 + U.f));'), 'flicker rápido de arco');
chk(c12.includes('fx.rielCd <= 0) {\n      fx.rielCd = 0.11;'), 'riel regenerado cada 0,11 s');
chk(c12.includes('const yR = topY + netH;'), 'riel en la coronación ACTUAL de la red');
chk(c12.includes('fx.riel.material.opacity = Math.min(1,\n      0.55 + 0.30 * Math.sin(tt * 17) + fl * 0.3);'), 'riel con parpadeo + energizado (clamp ≤1)');
chk(c12.includes('this._redSpark.set(\n            (Math.random() * 2 - 1) * W * 0.9, topY + netH, zC);'), 'chispas sobre el riel (Vector3 de reuso)');
chk(c12.includes('this.chispas.burst(this._redSpark, [0.55, 0.85, 1.0]);'), 'chispas cian del pool de la casa');
chk(c12.includes("try { this.audio.playOsc(108, 96, 0.09, 'sawtooth', 0.035, 0); } catch (eB2) { /* */ }"), 'zumbido eléctrico suave');
chk(c12.includes('fx.buzzCd = RED_BUZZ_CD * (0.8 + Math.random() * 0.4);'), 'zumbido con jitter (no metrónomo)');

/* — 5 · CICLO DE VIDA · arranque, apagado, tick, precaliente ——————————— */
console.log('5 · CICLO DE VIDA · la barrera nace y muere con la SÚPER RED');
chk(c12.includes('try { this._buildRedFx(); } catch (eB) { this._redFx = null; }\n    this._redFxVis(true);'), '_redCrecer monta y enciende la barrera');
chk(c12.includes('this._redFlashT = 0.3;          // destello de energizado al crecer'), 'energizado al crecer (0,3 s)');
chk(c12.includes("try { this.audio.playOsc(1500, 240, 0.14, 'square', 0.07, 0); } catch (eZ) { /* */ }"), 'zap de energizado');
chk(c12.includes('this._redFxVis(false);          // r26: la barrera eléctrica se apaga'), '_redRestaurar apaga la barrera SIEMPRE (fin/salida/startMatch)');
chk(c12.includes('// r26 (v3.6.121) · BARRERA ELÉCTRICA viva mientras la SÚPER RED corre.'), 'gancho en el tick');
chk(c12.includes("try { this._redFrame(dt); } catch (eRB) { /* la barrera nunca tumba el frame */ }"), 'frame blindado con try');
chk(c12.includes('} else if (this._redFxOn) {\n      this._redFxVis(false);\n    }'), 'red de seguridad: sin ventana, barrera fuera');
chk(c12.includes('() => { try { this._buildRedFx(); } catch (e) { /* */ } },    // r26: barrera lista'), 'barrera en el precaliente (gatillo sin lag)');
chk(c12.includes('this._redFx = null;             // { cuerpo, arcos[], riel, cd, … }'), 'estado _redFx inicializado');
chk(c12.includes('this._redFxOn = false;'), 'estado _redFxOn inicializado');
chk(c12.includes('this._redFlashT = 0;            // destello de energizado al crecer'), 'estado _redFlashT inicializado');
chk(c12.includes('this._redSpark = new THREE.Vector3();     // chispa del riel (reuso)'), 'Vector3 de chispa de reuso (cero asignaciones)');

/* — 6 · PRESERVACIÓN r25 · nada de lo bueno se pierde ————————————————— */
console.log('6 · PRESERVACIÓN r25 · la tormenta sigue siendo la de la r25');
chk(c12.includes('const ELEC_DUR = 10;'), 'ELEC_DUR = 10 s intacto');
chk(c12.includes('const ELEC_BOLT_R = 0.17;'), 'radio de interceptación intacto');
chk(c12.includes('const ELEC_ALTO_NUBE = 1.5; // m sobre la mesa del rival (spec literal)'), 'niebla a 1,5 m (spec literal intacta)');
chk(c12.includes('const sy0 = D.tableTopY + ELEC_ALTO_NUBE;      // a 1,5 m (spec literal)'), 'centro Y del banco intacto');
chk(c12.includes('const sz0 = zC - D.tableHalfLength * 0.5;      // mitad del RIVAL'), 'banco SOBRE LA MITAD DEL RIVAL intacto');
chk(c12.includes('this._elecFlashT = 0.25;'), 'destello de 0,25 s intacto');
chk(c12.includes("this.processIntents(this.rules.applyPoint('player', 'elec'));"), 'PUNTO por el árbitro intacto');
chk(c12.includes('this._elecRotoT = 0.9;'), 'bola rota oculta 0,9 s intacto');
chk(c12.includes("try { this.chispas.burst(this._elecTarget, [0.62, 0.85, 1.0]); } catch (e) { /* */ }"), 'chispas del impacto intactas');
chk(c12.includes('if (d2 <= r * r) this._elecRompe();'), 'colisión rápida intacta');
chk(c12.includes('const RED_DUR = 10;') && c12.includes('const RED_MUL = 2;'), 'SÚPER RED: 10 s ×2 intactos');
chk(c12.includes('D.netTopY = D.tableTopY + h0 * RED_MUL;'), 'mutación de DIMS.netTopY intacta');
chk(c12.includes('DIMS.netTopY = DIMS.tableTopY + this._redNetH0;'), 'restauración exacta intacta');
chk(c12.includes('megaEnabled() {\n    if (this.palaMejorada === false) return false;'), 'megaEnabled intacto');
chk(c12.includes('if (this._poderesEnPrueba()) {\n      this._poderesCortina();\n    }'), 'cortina de etapas 2/4 intacta');
chk(c12.includes('const ELEC_NEGRO = new THREE.Color(0x05070c);   // noche de la tormenta'), 'noche de la tormenta intacta');

/* — 7 · GARANTÍA · física y módulos neutrales ————————————————————————— */
console.log('7 · GARANTÍA · c04/c05/c09/c02/c07 sin una línea nueva');
for (const f of ['src/game/core/c04_fisica_ccd.js', 'src/game/core/c05_colisiones_ia_golpeo.js',
  'src/game/core/c09_red_netlink.js', 'src/game/core/c02_cfg_escena.js',
  'src/game/core/c07_escena_sala.js']) {
  let diff = '';
  try {
    diff = execSync(`git diff HEAD -- ${f}`, { cwd: raiz, encoding: 'utf8' });
  } catch (e) { diff = 'ERR'; }
  chk(diff.trim() === '', `${f}: diff vacío contra la r25 (garantía intacta)`);
}
chk(!c12.slice(c12.indexOf('r26 (v3.6.121) · BARRERA ELÉCTRICA de la SÚPER RED'), c12.indexOf('_redTrigger(ent) {')).includes('stepPhysics'), 'la barrera no toca el integrador (solo render)');
chk(!c12.includes('ball.ppRedBarrera'), 'la barrera no marca la bola');
chk(!c07.includes('RED_ARC') && !c07.includes('ELEC_NIEBLA'), 'c07 sin r26 (todo vive en c12)');

/* — 8 · SELLOS ———————————————————————————————————————————————————————— */
console.log('8 · SELLOS de la ronda');
chk((c12.match(/r26 \(v3\.6\.121\)/g) || []).length >= 6, 'comentarios r26 (v3.6.121) por todo c12');
chk(c12.includes('«que la red al crecer parezca una barrera de electricidad»'), 'spec literal del dueño citada (barrera)');
chk(c12.includes('«están muy cutres… debemos sustituirlas por una especie de niebla'), 'spec literal del dueño citada (niebla densa)');
chk(c12.includes('bastantes más\n// rayos de tormenta»'), 'spec literal del dueño citada (más rayos)');
chk(c00.includes('poder_red:') && c00.includes('poder_elec:'), 'I18N de los poderes intacto');
chk(c12.includes('_redFin() {') && c12.includes("this.rules.message = T('arc_red_fin');"), 'fin de la SÚPER RED con aviso intacto');

console.log(`\nR26 · ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
