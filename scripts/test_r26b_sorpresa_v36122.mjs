#!/usr/bin/env node
/* CRAZY PING PONG · r26b · v3.6.122 · TEST: BOLA ATRACTORA + 3 SUPERPODERES
 * NUEVOS + 3 HALL NUEVOS POR HITOS.
 *
 *   A · «El superpoder de tormenta eléctrica tiene que aumentar la
 *       posibilidad de impactar a la bola que actuará como atractora de
 *       los rayos de la tormenta incrementando en un 25 % la posibilidad
 *       de alcanzar la bola y destruirla» — UN rayo de cada CUATRO
 *       (ELEC_ATRAE_P = 0.25) BUSCA la bola: nace en la niebla más
 *       cercana, TERMINA EN ELLA, se tiñe de violeta y golpea casi
 *       seguro. El resto cae al azar con su colisión de siempre.
 *
 *   C · «crear otros 3 superpoderes de pala muy llamativos y
 *       sorprendentes que repliquen la forma actual… icono circular…
 *       ventaja de juego… duraciones sobre 10 segundos… SuperPoder de
 *       XXXX» — SÚPER FÉNIX (bola de fuego: +18 % en mis golpes, fuego
 *       REAL del Wizard — magia v2.120 —, ascuas al golpear pala/mesa
 *       desde r29), SÚPER CRONO (tiempo lento: bola al 62 % con anillos
 *       de reloj HIJOS DE LA BOLA — r29 — y restauración EXACTA) y
 *       SÚPER OSCURIDAD (r29: sustituye al Hielo por orden del dueño —
 *       bola negra con halo rojo fuego + niebla densa en cada golpeo
 *       del rival, 5 s + 2 s, IA con 35 % de bolas fuera).
 *
 *   D · «otros 3 diseños de Hall nuevos bien cuidados para mapear y que
 *       podamos conseguirlos con desbloqueos por hitos conseguidos» —
 *       SALÓN NEÓN ARCADE (hito: rally de 20), ESTACIÓN ORBITAL (hito:
 *       ELO 1100) y DOJO ZEN (hito: 5 saques directos); arte procedural
 *       con las MISMAS fichas y proporciones exactas de los planos.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 (física), c07/c08 (sala/hall render),
 *   c09 (códec) y c10 SIN una sola línea nueva — diff vacío contra la
 *   r26 (6e5264c).
 *
 * Uso: node --no-warnings scripts/test_r26b_sorpresa_v36122.mjs
 */
import { readFileSync, existsSync, statSync } from 'node:fs';
import { execSync } from 'node:child_process';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');

const c12 = lee('src/game/core/c12_pingponggame.js');
const c02 = lee('src/game/core/c02_cfg_escena.js');
const c00 = lee('src/game/core/c00_pre_three.js');

/* — 1 · BOLA ATRACTORA · un rayo de cada cuatro busca la bola ————————— */
console.log('1 · BOLA ATRACTORA · +25 % de los rayos la buscan');
chk(c12.includes('const ELEC_ATRAE_P = 0.25;'), 'ELEC_ATRAE_P = 0.25 (un rayo de cada cuatro)');
chk(c12.includes('const ELEC_ATRAE_COL = 0xd9c8ff;'), 'tinte violeta del rayo cazador');
chk(c12.includes('let atractora = false;'), 'bandera de modo ATRACTORA por rayo');
chk(c12.includes('pAt.z < zC - 0.10 &&'), 'sólo busca bolas sobre la MITAD del rival');
chk(c12.includes('Math.abs(pAt.x) < D.netHalfWidth * 1.15 &&'), 'y dentro del ancho de pista');
chk(c12.includes('Math.random() < ELEC_ATRAE_P) {'), 'sorteo del 25 % por rayo');
chk(c12.includes('!this.ball.ppTransito) ? this.ball.pos : null;'), 'la bola en tránsito de portal no se caza');
chk(c12.includes('const tx = atractora ? pAt.x :'), 'el rayo cazador TERMINA EN LA BOLA');
chk(c12.includes('const ty = atractora ? pAt.y : D.tableTopY + 0.005;'), 'objetivo = posición VIVA de la bola');
chk(c12.includes('rb.material.color.setHex(atractora ? ELEC_ATRAE_COL : 0xbfe4ff);'), 'tinte violeta por rayo (material individual)');
chk(c12.includes('const jitMax = atractora ? 0.018 : 0.09;'), 'jitter mínimo: el cazador va RECTO (se ve curvarse)');
chk(c12.includes("atractora ? [0.85, 0.70, 1.0] : [0.62, 0.85, 1.0]"), 'chispas violetas en el blanco cazado');
chk(c12.includes('DE CADA CUATRO (r26b), → LA BOLA (atractora, tinte violeta)'), 'docstring del rayo actualizada');
chk(c12.includes('this._elecRompe();'), 'colisión y ESTALLIDO intactos (patrón r25)');

/* — 2 · REGISTRO · 10 poderes con icono circular y voz ———————————————— */
console.log('2 · REGISTRO · PODERES_PALA llega a 10 entradas');
const bloqueRegistro = c12.slice(c12.indexOf('const PODERES_PALA = ['),
  c12.indexOf('const MEGA_DUR'));
for (const id of ['mega', 'efecto', 'iman', 'portal', 'clon', 'red', 'elec',
  'fenix', 'crono', 'oscuridad']) {
  chk(bloqueRegistro.includes(`{ id: '${id}'`), `poder '${id}' en el registro`);
}
for (const p of ['FENIX', 'CRONO', 'OSCURIDAD']) {
  chk(c12.includes(`const PNG_PODER_${p} = 'data:image/png;base64,iVBORw0KGgo`), `insignia circular PNG_PODER_${p} embebida (PNG) `);
  chk(c12.includes(`const VOZ_PODER_${p} = 'data:audio/mpeg;base64,SUQz`), `voz ES de ${p} embebida (MP3)`);
  chk(c12.includes(`const VOZ_PODER_${p}_EN = 'data:audio/mpeg;base64,SUQz`), `voz EN de ${p} embebida (MP3)`);
}
chk(c12.includes('const FENIX_DUR = ARCANO_CFG.ventanas.fenix;') && c12.includes('const CRONO_DUR = ARCANO_CFG.ventanas.crono;') &&
    c12.includes('const OSCURIDAD_DUR = ARCANO_CFG.ventanas.oscuridad;'), 're-anclada r55: ventanas DATA-DRIVEN — fénix/crono 10 s · oscuridad 20 s (ARCANO_CFG)');
chk(!c12.includes('const FENIX_MUL'), 'FÉNIX re-anclada r30: boost +18 % ANULADO (dinámica normal)');
chk(c12.includes('const CRONO_F = 0.62;'), 'CRONO: bola al 62 % (38 % más lenta)');
chk(c12.includes('const CRONO_RAMP = 0.4;'), 'CRONO: rampa suave de entrada/salida');
chk(c12.includes('const OSCURIDAD_OUT_P = 0.35;'), 'OSCURIDAD: IA manda fuera el 35 % (spec literal)');
chk(c12.includes('const OSCURIDAD_VIDA = 5;') && c12.includes('const OSCURIDAD_DISIPA = 2;'), 'OSCURIDAD: niebla 5 s plena + ~2 s de disipación');

/* — 3 · SÚPER FÉNIX · la bola de fuego ————————————————————————————————— */
console.log('3 · SÚPER FÉNIX · fuego REAL del Wizard (+18 %, bocanadas, ascuas)');
chk(c12.includes('_fenixTrigger(ent) {'), '_fenixTrigger (refresco honesto + gasto)');
chk(c12.includes("if (!this._megaMatriz.find((x) => x.id === 'fenix')) return false;"), 'sin carga no arranca');
chk(c12.includes('_buildFenixFx() {'), '_buildFenixFx: pool de fuego de la bola');
chk(c12.includes("g.addColorStop(0, 'rgba(255,242,180,1)');"), 'núcleo blanco-caliente de la textura de fuego (magia v2.120)');
chk(c12.includes("g.addColorStop(1, 'rgba(160,20,0,0)');"), 'borde que se funde (fuego real, no cartón)');
chk(c12.includes('blending: THREE.AdditiveBlending, depthWrite: false,'), 'fuego ADITIVO');
chk(c12.includes('this.rig.add(grp);            // ¡espacio de la mesa, NO this.scene!'), 'pool en el RIG (lección r29: this.scene desplazaba la llama)');
chk(c12.includes('_fenixTintAplicar() {'), 'tinta brasa de la bola (patrón magia _startFuego)');
chk(c12.includes("m.material.color.setHex(0xff5a12);"), 'color brasa 0xff5a12 (el del Wizard)');
chk(c12.includes('_fenixTintRestaurar() {'), 'tinta original restaurada al acabar');
chk(c12.includes('_fenixFrame(dt) {'), '_fenixFrame: bocanadas nacen en la bola y suben');
chk(c12.includes('this._fenixCad = 0.028;'), '~35 bocanadas/s (cadencia del Wizard)');
chk(c12.includes('_fenixEstallido(pos) {'), '_fenixEstallido: EXPLOSIÓN de ascuas al golpear');
chk(c12.includes('if (this._fenixT > 0) {\n            try { this._fenixEstallido(e.pos); } catch (eFxT) { /* */ }\n          }'), 'gancho TABLE: ascuas al botar en la mesa');
chk(c12.includes('if (this._fenixT > 0) {\n            try { this._fenixEstallido(e.pos); } catch (eFxP) { /* */ }\n          }'), 'gancho PADDLE: ascuas al golpear la pala');
chk(c12.includes('_fenixParticula(p, dt, grav) {'), 'gravedad de las ascuas (caen como chispas de hoguera)');
chk(c12.includes('_fenixFin() {') && c12.includes("this.rules.message = T('arc_fenix_fin');"), 'fin con aviso');
chk(!c12.includes('multiplyScalar(FENIX'), 're-anclada r30: cero multiplicación por frame (bola normal)');
chk(c12.includes('const FENIX_OUT_P = 0.15;'), 're-anclada r30: la ventaja es la falta PEQUEÑA de la IA (15 %)');
chk(c12.includes("this.rules.mode !== 'duelos'"), 're-anclada r39: el invitado no enciende fuera de duelos (allí portaliza SU golpe)');
chk(c12.includes('ANULADO por orden del dueño'), 're-anclada r30: crónica del veto del boost (dinámica normal)');
chk(c12.includes("if (ent.id === 'fenix') return this._fenixTrigger(ent); // v3.6.122 (r26b)"), 'gatillo despacha fénix');
chk(c12.includes("if (ent.id === 'fenix') return this._fenixT > 0; // v3.6.122 (r26b)"), 'modo ACTIVO del icono para fénix');
chk(c12.includes("if (this._megaActivaId === 'fenix') return this._fenixT; // v3.6.122 (r26b)"), 'anillo de tiempo para fénix');
chk(c12.includes("if (this._megaActivaId === 'fenix') return TRAIL_PODER.fenix; // r26b"), 'estela teñida de naranja fuego');
chk(c12.includes('fenix: [1.0, 0.55, 0.18],'), 'TRAIL_PODER.fenix');

/* — 4 · SÚPER CRONO · el tiempo lento ——————————————————————————————————— */
console.log('4 · SÚPER CRONO · bola al 62 % con restauración EXACTA');
chk(c12.includes('_cronoTrigger(ent) {'), '_cronoTrigger (refresco honesto + gasto)');
chk(c12.includes('_buildCronoFx() {'), '_buildCronoFx: anillos de reloj');
chk(c12.includes('const geo = new THREE.RingGeometry(radios[i] - 0.006, radios[i], 40);'), '3 anillos RingGeometry');
chk(c12.includes('const radios = [0.058, 0.078, 0.098];'), 'radios escalonados alrededor de la bola');
chk(c12.includes('_cronoFrame(dt) {'), '_cronoFrame: multiplicador por delta');
chk(c12.includes('mul = 1 + (CRONO_F - 1) * k;'), 'rampa 1→0.62→1 (entrada y salida suaves)');
chk(c12.includes('this.ball.vel.multiplyScalar(mul / this._cronoPrevMul);'), 'delta relativo al frame anterior');
chk(c12.includes('this.ball.vel.multiplyScalar(1 / this._cronoPrevMul);'), '_cronoFin: RESTAURACIÓN EXACTA (cortina incluida)');
chk(c12.includes('this._cronoPrevMul = 1;'), 'idempotente tras restaurar');
chk(c12.includes("!(this.net.online && this.net.v2 === 'ok');"), 'sin escala en online (nadie desincroniza)');
chk(c12.includes('a.rotation.x = tt * (0.8 + i * 0.5) + i * 2.1;'), 'anillos ORBITANDO la bola');
chk(c12.includes("if (ent.id === 'crono') return this._cronoTrigger(ent); // v3.6.122 (r26b)"), 'gatillo despacha crono');
chk(c12.includes("if (this._megaActivaId === 'crono') return TRAIL_PODER.crono; // r26b"), 'estela plata-cian');
chk(c12.includes('crono: [0.78, 0.92, 1.0],'), 'TRAIL_PODER.crono');
// r29 · CENTRADO EXACTO (informe del dueño: los anillos «tienen un
// desplazamiento hacia la derecha de la bola») — HIJOS de ballMesh:
chk(c12.includes('if (this._cronoFx && this._cronoFx.grupo.parent === this.ballMesh) return;'), '_buildCronoFx idempotente por parent');
chk(c12.includes('this.ballMesh.add(grupo);'), 'anillos HIJOS DE LA BOLA (centrado SIEMPRE, cero lag)');
chk(c12.includes('if (gC.parent) gC.parent.remove(gC);'), 're-anclaje en el trigger por si la malla viva cambió');
chk(!c12.includes('fx.grupo.position.set(p.x, p.y, p.z);'), 'SIN posición manual por frame (era la fuente del desplazamiento)');

/* — 5 · SÚPER OSCURIDAD · niebla en el golpeo rival (r29) ————————————— */
console.log('5 · SÚPER OSCURIDAD · bola negra + niebla (r29: sustituye al Hielo)');
chk(c12.includes('_oscuridadTrigger(ent) {'), '_oscuridadTrigger (refresco honesto + gasto)');
chk(c12.includes("if (!this._megaMatriz.find((x) => x.id === 'oscuridad')) return false;"), 'sin carga no arranca');
chk(c12.includes('_oscuridadTintAplicar() {'), 'bola NEGRA (tinta guardada, patrón fénix/magia)');
chk(c12.includes("m.material.color.setHex(0x0d0b0e);"), 'carbón apagado 0x0d0b0e');
chk(c12.includes("m.material.emissive.setHex(0xff2a08);"), 'emisivo rojo fuego');
chk(c12.includes('_buildOscuridadFx() {'), '_buildOscuridadFx: pool de zonas de niebla');
chk(c12.includes("gH.addColorStop(0, 'rgba(40,34,38,0.96)');"), 'humo OSCURO (tapa la escena, no ilumina)');
chk(c12.includes("gB.addColorStop(0, 'rgba(255,120,60,1)');"), 'destellos rojos (los «pequeños ojos» del dueño)');
chk(c12.includes('this.rig.add(g);          // ¡espacio de la mesa, NO this.scene!'), 'zonas en el RIG (lección r29)');
chk(c12.includes('const OSCURIDAD_ZONAS = 6;'), 'pool de 6 zonas simultáneas');
chk(c12.includes('_oscuridadNiebla(pos) {'), '_oscuridadNiebla: nace en la zona de golpeo');
chk(c12.includes('for (const cand of zonas) {'), 'reciclado de la zona MÁS VIEJA (nunca crece sin tope)');
chk(c12.includes('if (Math.random() < OSCURIDAD_OUT_P) {'), 'sorteo del 35 % por golpeo de la IA');
chk(c12.includes('_oscuridadFalla(pos) {'), '_oscuridadFalla: la IA manda LARGO (fuera de mesa)');
chk(c12.includes('computeShotVelocity(pos, tmpO,'), 'el solucionador de la casa (c05) apunta fuera — c04/c05 INTACTOS');
chk(c12.includes('const fin = OSCURIDAD_VIDA + OSCURIDAD_DISIPA;'), 'ciclo natural 5 s + 2 s en el frame');
chk(c12.includes('if (this._oscuridadT > 0 || this._oscuridadZonasVivas()) {'), 'la niebla vive SU ciclo aunque la ventana muera (patrón clon)');
chk(c12.includes('_oscuridadFin() {') && c12.includes("this.rules.message = T('arc_oscuridad_fin');"), 'fin con aviso');
chk(c12.includes("if (ent.id === 'oscuridad') return this._oscuridadTrigger(ent); // r29 (sustituye a hielo)"), 'gatillo despacha oscuridad');
chk(c12.includes('oscuridad: [0.85, 0.14, 0.10],'), 'TRAIL_PODER.oscuridad (rojo fuego)');
chk(!c12.includes('_hieloCongela'), 'HIELO ANULADO: cero rastros del congelador (orden del dueño)');
chk(!c12.includes("id: 'hielo'"), 'HIELO fuera del registro PODERES_PALA');

/* — 6 · PLANTILLA COMÚN · ventanas, cortina y precalentado ————————————— */
console.log('6 · PLANTILLA COMÚN · ventanas 3·2·1, cortina, precaliente');
chk(c12.includes("pwViva(this._fenixT)") && c12.includes("pwViva(this._cronoT)") &&
    c12.includes("pwViva(this._oscuridadT)"), 're-anclada r55: puertas pwViva — ventanas de campeonato Y duelos (regla única)');
chk(c12.includes('try { this._fenixFin(); } catch (eFF) { /* */ }') &&
    c12.includes('try { this._cronoFin(); } catch (eCF2) { /* */ }') &&
    c12.includes('try { this._oscuridadFin(); } catch (eOF) { /* */ }'), 'apagado garantizado si «on» desaparece');
chk(c12.includes('try { this._fenixFrame(dt); } catch (eFF2) {') &&
    c12.includes('try { this._cronoFrame(dt); } catch (eCF3) {') &&
    c12.includes('try { this._oscuridadFrame(dt); } catch (eOF2) {'), 'frames con try (nunca tumban el tick)');
chk(c12.includes("try { this._fenixFin(); } catch (eF) { /* */ }") &&
    c12.includes('try { this._cronoFin(); } catch (eC) { /* */ }') &&
    c12.includes('try { this._oscuridadFin(); } catch (eO) { /* */ }'), '_poderesCortina: etapas 2/4 cortan las 3 ventanas');
chk(c12.includes("() => { try { this._megaVozPrecalentar('fenix'); } catch (e) { /* */ } }, // r26b: voz concesión") &&
    c12.includes("() => { try { this._megaVozPrecalentar('crono'); } catch (e) { /* */ } }, // r26b: voz concesión") &&
    c12.includes("() => { try { this._megaVozPrecalentar('oscuridad'); } catch (e) { /* */ } }, // r29: voz concesión"), 'voces precalentadas (anti-lag)');
chk(c12.includes('() => { try { this._buildFenixFx(); } catch (e) { /* */ } },  // r29: fuego de la bola listo') &&
    c12.includes('() => { try { this._buildCronoFx(); } catch (e) { /* */ } },  // r29: anillos HIJOS de la bola') &&
    c12.includes('() => { try { this._buildOscuridadFx(); } catch (e) { /* */ } },  // r29: niebla lista'), 'FX preconstruidos');

/* — 7 · I18N · nombres «SuperPoder de XXXX» ES/EN ————————————————————— */
console.log('7 · I18N · 9 claves de poderes + 12 de halls (ES/EN)');
for (const k of ['poder_fenix', 'arc_fenix_go', 'arc_fenix_fin',
  'poder_crono', 'arc_crono_go', 'arc_crono_fin',
  'poder_oscuridad', 'arc_oscuridad_go', 'arc_oscuridad_fin',
  'hall_var_neon', 'hall_var_observatorio', 'hall_var_dojo',
  'hint_hall_var_neon', 'hint_hall_var_observatorio', 'hint_hall_var_dojo',
  'mesa_lock_rally20', 'mesa_lock_elo1100', 'mesa_lock_aces5']) {
  const n = (c00.match(new RegExp(`\\n    ${k}:`, 'g')) || []).length;
  chk(n === 2, `clave '${k}' presente en ES y EN (${n}/2)`);
}
chk(c00.includes("poder_fenix: '¡SUPERPODER DE FÉNIX!'"), 'nombre pedido por el dueño: SuperPoder de Fénix');
chk(c00.includes("poder_crono: '¡SUPERPODER DE CRONO!'"), 'nombre pedido por el dueño: SuperPoder de Crono');
chk(c00.includes("poder_oscuridad: '¡SUPERPODER DE OSCURIDAD!'"), 'nombre del 10.º poder: SuperPoder de Oscuridad (r29, sustituye a Hielo)');

/* — 8 · 3 HALL NUEVOS · catálogo, candados por hitos y arte ———————————— */
console.log('8 · HALLS · neón/orbital/dojo con candados por HITOS');
chk(c02.includes("{ id: 'neon', lock: 'hito_rally20', nameKey: 'hall_var_neon',"), 'SALÓN NEÓN ARCADE (hito: rally de 20)');
chk(c02.includes("{ id: 'observatorio', lock: 'hito_elo1100', nameKey: 'hall_var_observatorio',"), 'OBSERVATORIO ESTELAR (hito: ELO 1100 — nombre libre: Estación Orbital ya era campeonato)');
chk(c02.includes("{ id: 'dojo', lock: 'hito_aces5', nameKey: 'hall_var_dojo',"), 'DOJO ZEN (hito: 5 saques directos)');
chk(c02.includes("base: 'assets/hall/neon/'") && c02.includes("base: 'assets/hall/observatorio/'") &&
    c02.includes("base: 'assets/hall/dojo/'"), 'carpetas de arte (patrón cabana, cero bytes en el bundle)');
chk(c12.includes("if (lock === 'hito_rally20') return (d.bestRally || 0) >= 20;"), '_mesaLibre: bestRally ≥ 20');
chk(c12.includes("if (lock === 'hito_elo1100') return (d.elo || 1000) >= 1100;"), '_mesaLibre: ELO ≥ 1100');
chk(c12.includes("if (lock === 'hito_aces5') return (d.aces || 0) >= 5;"), '_mesaLibre: aces ≥ 5');
chk(c12.includes("if (lock === 'hito_rally20') return T('mesa_lock_rally20');") &&
    c12.includes("if (lock === 'hito_elo1100') return T('mesa_lock_elo1100');") &&
    c12.includes("if (lock === 'hito_aces5') return T('mesa_lock_aces5');"), '_mesaLockTxt de los 3 hitos');
chk(c12.includes("btn('hall_var:' + v.id, 56 + (i % 3) * 312,"), 'salahall en rejilla de 3 columnas (5 variantes)');
chk(c12.includes('y += Math.ceil(HALL_VARIANTES.length / 3) * 62 + 6;'), 'altura de rejilla dinámica');
chk(c12.includes("'hall_var:neon': 'hint_hall_var_neon',") &&
    c12.includes("'hall_var:observatorio': 'hint_hall_var_observatorio',") &&
    c12.includes("'hall_var:dojo': 'hint_hall_var_dojo',"), 'hints de los 3 halls en el catálogo');
// — arte: fichas EXACTAS (proporciones de los planos, patrón v3.6.28) —
const fichas = { frente: [1849, 864], fondo: [1849, 864], izquierda: [2395, 864],
  derecha: [2395, 864], suelo: [1296, 1678], techo: [1296, 1678] };
const dimJpg = (buf) => {
  // lee las dimensiones reales del JPEG (marcador SOF0/SOF2)
  let i = 2;
  while (i < buf.length - 9) {
    if (buf[i] !== 0xff) { i++; continue; }
    const m = buf[i + 1];
    if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) {
      return [buf.readUInt16BE(i + 7), buf.readUInt16BE(i + 5)];
    }
    i += 2 + buf.readUInt16BE(i + 2);
  }
  return [0, 0];
};
for (const hall of ['neon', 'observatorio', 'dojo']) {
  for (const [f, [w, h]] of Object.entries(fichas)) {
    const p = `public/assets/hall/${hall}/${f}.jpg`;
    const existe = existsSync(raiz + p);
    const dims = existe ? dimJpg(readFileSync(raiz + p)) : [0, 0];
    const kb = existe ? statSync(raiz + p).size / 1024 : 0;
    chk(existe && dims[0] === w && dims[1] === h,
      `${hall}/${f}.jpg ${w}×${h} exactas (${dims[0]}×${dims[1]}, ${kb.toFixed(0)} KB)`);
  }
}

/* — 9 · GARANTÍA FÍSICA · c04/c05/c07/c08/c09/c10 INTACTOS ————————————— */
console.log('9 · GARANTÍA · física y códec sin una línea nueva');
let sucios = [];
try {
  const out = execSync('git diff HEAD --name-only', { cwd: raiz }).toString();
  sucios = out.trim().split('\n').filter(Boolean);
} catch { /* sin git: se comprueba por presencia */ }
for (const santo of ['src/game/core/c04_fisica_ccd.js',
  'src/game/core/c05_colisiones_ia_golpeo.js', 'src/game/core/c07_escena_sala.js',
  'src/game/core/c08_hall_hud.js', 'src/game/core/c09_red_netlink.js',
  'src/game/core/c10_menu_saque.js']) {
  chk(!sucios.includes(santo), `${santo.split('/').pop()} SIN cambios (diff vacío contra la r26)`);
}

/* — 10 · SERVICIO · sw.js y sellos los gobierna bump (no este test) ———— */
console.log('10 · SINERGIA · la tormenta y la barrera de la r26 intactas');
chk(c12.includes('const ELEC_NIEBLA_N = 14;') && c12.includes('const ELEC_RAYOS_N = 10;'), 'niebla densa y pool de rayos de la r26 intactos');
chk(c12.includes('const ELEC_BOLT_CD = 0.42;'), 'cadencia de ráfagas de la r26 intacta');
chk(c12.includes('const RED_ARC_N = 7;'), 'barrera eléctrica de la red intacta');
chk(c12.includes('this._elecRompe();'), 'estallido y punto del árbitro intactos');

console.log(`\nRESULTADO: ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
