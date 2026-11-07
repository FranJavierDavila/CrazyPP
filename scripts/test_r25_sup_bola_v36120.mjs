#!/usr/bin/env node
/* CRAZY PING PONG · r25 · v3.6.120 · TEST: SÚPER RED + SÚPER ELECTRICIDAD
 * + CORTINA EN ETAPAS 2/4 + CONTROL TOTAL DE LA BOLA ONLINE.
 *
 * Las tres peticiones del dueño (informe tras la r24):
 *
 *   A · «Revisar que los superpoderes de Pala del jugador nunca deben
 *        aparecer en las etapas 2 y 4 de los campeonatos (pruebas de
 *        habilidad)» — los 5 módulos exponen testActive(); el núcleo
 *        corta gatillo (megaEnabled), concesiones (_megaCharge) y CUELGA
 *        LA CORTINA (_poderesCortina: ventanas, FX, icono, radio).
 *
 *   B · «Vamos a añadir otro superpoder de Pala… "Super Red"
 *        (SuperPala_Red.png)… hace crecer la altura de la red el doble
 *        del valor actual… dura activo 10 segundos» — 6.º poder del
 *        registro: DIMS.netTopY ×2 EN VIVO (física/IA/saque la leen,
 *        lección r95) + re-acomodado visual (plano/cinta/postes) +
 *        restauración exacta.
 *
 *   C · «Otro superpoder nuevo será Super Electricidad
 *        (SuperPala_Electrica.png)… rayos… nubes a metro y medio sobre
 *        la mesa del rival… gran estruendo sonoro y destello… la luz de
 *        la escena se vuelve bastante oscura (casi parece de noche)…
 *        si alguno de los rayos intercepta la bola del rival (aproxima-
 *        ción medible con un sistema de colisiones que permita un
 *        cálculo rápido), la rompe en múltiples pedacitos negros y
 *        pierde el punto» — 7.º poder: tormenta de 10 s (nubes sprite a
 *        1,5 m, pool de 3 rayos, 2 truenos MP3 sintetizados, noche 0,18
 *        sobre las luces vivas SIN PointLights nuevos — lección v2.92,
 *        colisión punto-segmento (un hipot), 12 pedacitos negros, punto
 *        por el cauce del árbitro (applyPoint causa 'elec').
 *
 *   D · «las partidas en red… no se ve la bola hasta que se lanza…
 *        vemos la bola en la mano del rival cuando debería estar en la
 *        nuestra, o incluso no vemos la bola ninguno… asegurar que
 *        siempre esté visible en poder del jugador que debe sacar» —
 *        _bolaGuard: propiedad re-afirmada CADA FRAME desde el árbitro
 *        (determinista), saque propio en mano, saque del rival en su
 *        mano o punto reglamentario, HELD re-armado si FSM 'idle',
 *        rallye anti-NaN/anti-mundo, telemetría 1/5 s. c09 intacto.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 (física) y c09 (códec) SIN una sola
 *   línea nueva — verificado pordiff contra el commit de la r24.
 *
 * Uso: node --no-warnings scripts/test_r25_sup_bola_v36120.mjs
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
const c09 = lee('src/game/core/c09_red_netlink.js');

/* — 1 · CORTINA · etapas 2 y 4 sin superpoderes de pala ——————————————— */
console.log('1 · CORTINA · etapas 2/4 (pruebas de habilidad)');
chk(c12.includes('_poderesEnPrueba() {'), 'detector _poderesEnPrueba (testActive de los 5 módulos)');
chk(c12.includes("!!(this.champs && this.champs.active && this.champs.testActive)"), 'usa el gancho testActive del ChampLoader');
chk(c12.includes('megaEnabled() {\n    if (this.palaMejorada === false) return false;\n    // r25 (v3.6.120) · etapas 2/4: ni gatillo, ni carga, ni icono.\n    if (this._poderesEnPrueba()) return false;'), 'megaEnabled corta el GATILLO en pruebas');
chk(c12.includes('if (this._poderesEnPrueba()) return;   // r25: etapas 2/4 sin cargas'), '_megaCharge no concede cargas en pruebas');
chk(c12.includes('if (this._poderesEnPrueba()) {\n      this._poderesCortina();\n    }'), 'updateMega cuelga la CORTINA cada frame en pruebas');
chk(c12.includes('_poderesCortina() {'), 'la cortina existe');
chk((c12.match(/this\._poderesCortina\(\)/g) || []).length >= 1, 'la cortina se llama desde updateMega');
chk(c12.includes('DIMS.hitAssistRadius = this._BASE_HIT;\n    if (this._megaIconOn) this._megaIconVis(false);'), 'cortina: radio de golpeo restaurado + icono fuera');
for (const id of ['_megaT', '_efectoT', '_imanT', '_portalT', '_clonT', '_redT', '_elecT']) {
  chk(c12.includes(`if (this.${id} > 0)`), `cortina apaga la ventana ${id}`);
}

/* — 2 · REGISTRO · 7 poderes con icono y voz —————————————————————————— */
console.log('2 · REGISTRO · PODERES_PALA con 7 entradas');
const bloqueRegistro = c12.slice(c12.indexOf('const PODERES_PALA = ['),
  c12.indexOf('const MEGA_DUR'));
for (const id of ['mega', 'efecto', 'iman', 'portal', 'clon', 'red', 'elec']) {
  chk(bloqueRegistro.includes(`{ id: '${id}'`), `poder '${id}' en el registro`);
}
chk(bloqueRegistro.includes("png: PNG_PODER_RED"), 'SÚPER RED lleva el PNG del dueño');
chk(bloqueRegistro.includes("voz: VOZ_PODER_RED, vozEn: VOZ_PODER_RED_EN"), 'SÚPER RED lleva voz ES/EN');
chk(bloqueRegistro.includes("png: PNG_PODER_ELEC"), 'SÚPER ELECTRICIDAD lleva el PNG del dueño');
chk(bloqueRegistro.includes("voz: VOZ_PODER_ELEC, vozEn: VOZ_PODER_ELEC_EN"), 'SÚPER ELECTRICIDAD lleva voz ES/EN');
chk(c12.includes('const MEGA_TOPE = 3;'), 'tope ×3 por poder intacto (máx 3 almacenados)');
chk(c12.includes('const MEGA_GOLPES = 20;'), 'concesión cada 20 toques intacta (bolsa aleatoria)');
chk(c12.includes("const ids = PODERES_PALA.map((p) => p.id);") &&
    c12.includes('const id = ids[Math.floor(Math.random() * ids.length)]'), 'sorteo ALEATORIO sobre TODO el registro (red y elec entran)');

/* — 3 · SÚPER RED · red ×2 durante 10 s ———————————————————————————————— */
console.log('3 · SÚPER RED · la red crece al doble (10 s)');
chk(c12.includes('const RED_DUR = 10;'), 'RED_DUR = 10 s (regla de la casa)');
chk(c12.includes('const RED_MUL = 2;'), 'RED_MUL = 2 («el doble del valor actual»)');
chk(c12.includes('D.netTopY = D.tableTopY + h0 * RED_MUL;'), 'DIMS.netTopY muta ×2 EN VIVO (física/IA/saque la leen — r95)');
chk(c12.includes('DIMS.netTopY = DIMS.tableTopY + this._redNetH0;'), 'restauración EXACTA de la altura reglamentaria');
chk(c12.includes('_redTrigger(ent) {'), '_redTrigger (refresco honesto + gasto + arranque)');
chk(c12.includes("if (!this._megaMatriz.find((x) => x.id === 'red')) return false;"), 'sin carga no arranca');
chk(c12.includes('_redNetFit() {'), 're-acomodado visual (patrón relayoutMesa r95)');
chk(c12.includes("m.name === 'ppTableNet'"), 'plano de la red estirado');
chk(c12.includes("m.name === 'ppTableBand'"), 'cinta reposicionada arriba');
chk(c12.includes("m.name === 'ppTablePost'"), 'postes crecidos');
chk(c12.includes("m.userData.h0 = h0;          // altura de nacimiento (UNA vez)"), 'altura de nacimiento registrada UNA vez (idempotente)');
chk(c12.includes('_redFin() {') && c12.includes("this.rules.message = T('arc_red_fin');"), 'fin con aviso');
chk(c12.includes("if (ent.id === 'red') return this._redTrigger(ent);     // v3.6.120 (r25)"), 'gatillo despacha red');
chk(c12.includes("if (ent.id === 'red') return this._redT > 0;     // v3.6.120 (r25)"), 'modo ACTIVO del icono para red');
chk(c12.includes("if (this._megaActivaId === 'red') return this._redT;     // v3.6.120 (r25)"), 'anillo de tiempo para red');
chk(c12.includes("if (this._megaActivaId === 'red') return TRAIL_PODER.red;     // r25"), 'estela teñida de azul red');
chk(c12.includes('red: [0.36, 0.62, 0.98],'), 'TRAIL_PODER.red');
chk(c12.includes('} else if (this._redT > 0) {\n      this._redT = 0;\n      try { this._redFin(); } catch (eRF) { /* */ }\n    }'), 'red de seguridad: sin «on» la red se recoge YA');
chk(c12.includes("try { this._redRestaurar(); } catch (eR0) { /* */ }"), 'startMatch recoge la red (patrón _megaNormReset)');
chk(c12.includes("this.rules.message = T('arc_red_go');"), 'mensaje de activación');
chk(c12.includes("this.audio.playOsc(220, 440, 0.18, 'triangle', 0.14, 0);"), 'firma sonora propia (red tensada)');
chk(c12.includes("c2.moveTo(128, 42); c2.lineTo(110, 70); c2.lineTo(146, 70);"), 'reserva del icono sin PNG');

/* — 4 · SÚPER ELECTRICIDAD · tormenta sobre el rival ——————————————————— */
console.log('4 · SÚPER ELECTRICIDAD · tormenta (nubes, rayos, noche, estallido)');
chk(c12.includes('const ELEC_DUR = 10;'), 'ELEC_DUR = 10 s');
chk(c12.includes('const ELEC_BOLT_CD = 1.15;'), 'cadencia de rayos (≈8-9 por ventana)');
chk(c12.includes('const ELEC_BOLT_R = 0.17;'), 'radio de interceptación rayo↔bola');
chk(c12.includes('const ELEC_ALTO_NUBE = 1.5; // m sobre la mesa del rival (spec literal)'), 'nubes a 1,5 m (spec literal)');
chk(c12.includes('D.tableTopY + ELEC_ALTO_NUBE;      // a 1,5 m (spec literal)'), 'posición Y de las nubes = mesa + 1,5 m');
chk(c12.includes('zC - D.tableHalfLength * 0.5;      // mitad del RIVAL'), 'nubes SOBRE LA MITAD DEL RIVAL');
chk(c12.includes('_elecTrigger(ent) {'), '_elecTrigger');
chk(c12.includes('_buildElecFx() {'), 'tormenta pre-construida (pool reutilizable)');
chk(c12.includes('const rayos = [];') && c12.includes('new Float32Array(9 * 3)'), 'pool de 3 rayos de 9 puntos (cero asignaciones por rayo)');
chk(c12.includes("pos.needsUpdate = true;"), 'posiciones recicladas (needsUpdate)');
chk(c12.includes('_elecRayo() {'), 'descarga: nube → punto aleatorio del campo rival');
chk(c12.includes('(Math.random() * 2 - 1) * D.netHalfWidth * 0.85'), 'objetivo dentro de la mesa rival');
chk(c12.includes('this._elecFlashT = 0.25;'), 'destello de 0,25 s por rayo');
chk(c12.includes('_elecTrueno() {') && c12.includes("AUDIO_TRUENO_A") && c12.includes("AUDIO_TRUENO_B"), 'truenos alternos (2 muestras MP3)');
chk(c12.includes('const noche = 0.18;                 // «casi parece de noche»'), 'escena casi nocturna (0,18)');
chk(c12.includes('const flash = 1 + Math.max(0, f) * 2.4;'), 'destello CLAVA las luces (×3,4 pico)');
chk(c12.includes('this.scene.background.lerp(ELEC_NEGRO, k * 0.85);'), 'fondo/niebla a noche (respetando passthrough)');
chk(c12.includes('if (!(this.inAR && this.pstOn)) {   // el passthrough canjea fondo/niebla'), 'passthrough respetado');
const bloqueR25 = c12.slice(c12.indexOf('r25 (v3.6.120) · SÚPER RED (6.º poder'), c12.indexOf('r25 (v3.6.120) · CORTINA de poderes'));
chk(!bloqueR25.includes('new THREE.PointLight'), 'CERO PointLight en la tormenta (lección v2.92: no recompila shaders) — el único del juego nació en la sala base');
chk(c12.includes('_elecLucesCapturar() {'), 'luces capturadas al activar');
chk(c12.includes('this.scene.background.setHex(b.bg);'), 'luces y fondo EXACTOS de vuelta al disiparse');
chk(c12.includes('apx * abx + apy * aby + apz * abz'), 'colisión RÁPIDA punto-segmento (un hipot)');
chk(c12.includes('if (d2 <= r * r) this._elecRompe();'), 'si el rayo intercepta la bola → ESTALLA');
chk(c12.includes('_elecRompe() {'), '_elecRompe');
chk(c12.includes('const geoM = new THREE.TetrahedronGeometry(0.022);'), 'pedacitos: tetraedros negros');
chk(c12.includes('color: 0x0b0b0e'), 'pedacitos NEGROS');
chk(c12.includes('if (++dados >= 10) break;'), 'hasta 10 pedacitos por estallido (pool de 12)');
chk(c12.includes('this.processIntents(this.rules.applyPoint(\'player\', \'elec\'));'), 'PUNTO por el cauce del árbitro (causa elec)');
chk(c12.includes('this._elecRotoT = 0.9;'), 'bola rota oculta 0,9 s (nunca se toca el integrador)');
chk(c12.includes('try { this.chispas.burst(this._elecTarget, [0.62, 0.85, 1.0]); } catch (e) { /* */ }'), 'chispas azules en el punto de impacto');
chk(c12.includes('_elecFrame(dt) {'), 'frame de la tormenta (nubes/rayos/pedacitos/cadencia)');
chk(c12.includes('} else if (this._elecT > 0) {\n      this._elecT = 0;\n      try { this._elecFin(); } catch (eEF2) { /* */ }\n    }'), 'red de seguridad: sin «on» la tormenta se disipa YA');
chk(c12.includes("try { this._elecFin(); } catch (eR1) { /* */ }"), 'startMatch disipa la tormenta');
chk(c12.includes("() => { try { this._buildElecFx(); } catch (e) { /* */ } },   // r25: tormenta lista"), 'tormenta en el precaliente (gatillo sin lag)');
chk(c12.includes("() => { try { this._elecTruenoPrewarm(); } catch (e) { /* */ } }, // r25: truenos"), 'truenos precalentados sin sonar');
chk(c12.includes("() => { try { this._megaVozPrecalentar('elec'); } catch (e) { /* */ } },  // r25: voz concesión"), 'voz de concesión precalentada');

/* — 5 · ASSETS EMBEBIDOS · PNG del dueño + voces + truenos ————————————— */
console.log('5 · ASSETS · PNG + voces ES/EN + truenos (data-URI, cero red)');
const pngRed = c12.match(/const PNG_PODER_RED = 'data:image\/png;base64,([^']*)'/);
const pngElec = c12.match(/const PNG_PODER_ELEC = 'data:image\/png;base64,([^']*)'/);
chk(!!pngRed && pngRed[1].length > 20000 && pngRed[1].length < 60000,
  `PNG_RED embebido (${pngRed ? (pngRed[1].length / 1024).toFixed(1) : '—'} KB base64)`);
chk(!!pngElec && pngElec[1].length > 20000 && pngElec[1].length < 80000,
  `PNG_ELEC embebido (${pngElec ? (pngElec[1].length / 1024).toFixed(1) : '—'} KB base64)`);
const cabeceraPng = (b64) => Buffer.from(b64.slice(0, 12), 'base64').toString('hex');
chk(pngRed && cabeceraPng(pngRed[1]) .startsWith('89504e470d0a1a0a'), 'PNG_RED con cabecera PNG real');
chk(pngElec && cabeceraPng(pngElec[1]) .startsWith('89504e470d0a1a0a'), 'PNG_ELEC con cabecera PNG real');
for (const [k, min] of [['VOZ_PODER_RED', 8000], ['VOZ_PODER_RED_EN', 8000],
                        ['VOZ_PODER_ELEC', 12000], ['VOZ_PODER_ELEC_EN', 12000],
                        ['AUDIO_TRUENO_A', 12000], ['AUDIO_TRUENO_B', 14000]]) {
  const m = c12.match(new RegExp(`const ${k} = '([^']*)'`));
  chk(!!m && m[1].startsWith('data:audio/mpeg;base64,') && m[1].length >= min,
    `${k} embebido (${m ? (m[1].length / 1024).toFixed(1) : '—'} KB)`);
}
chk(c12.includes("else if (id === 'red') par = [VOZ_PODER_RED, VOZ_PODER_RED_EN];"), 'voz del selector reutiliza la de concesión (red)');
chk(c12.includes("else if (id === 'elec') par = [VOZ_PODER_ELEC, VOZ_PODER_ELEC_EN];"), 'voz del selector reutiliza la de concesión (elec)');
chk(c12.includes("const ids = ['mega', 'efecto', 'iman', 'portal', 'clon', 'nada', 'red', 'elec'];"), 'precaliente del selector cubre los 8 ids');

/* — 6 · CONTROL TOTAL DE LA BOLA ONLINE ———————————————————————————————— */
console.log('6 · CONTROL TOTAL · _bolaGuard (propiedad re-afirmada cada frame)');
chk(c12.includes('_bolaGuard(dt) {'), 'guardián _bolaGuard');
chk(c12.includes('this._bolaGuard(dt);      // r25 (v3.6.120) · CONTROL TOTAL de la bola online'), 'llamado en animate (tras updateMega/_dlUpdate, antes de sync visual)');
chk(c12.includes('const ballHeld = holdLock || this._bgHold;   // r25: la guardia también sujeta'), 'el brillo de bola sujetada también lo da la guardia');
chk(c12.includes('if (!this.net || !this.net.online || this.net.v2 !== \'ok\' ||'), 'solo con red v2 (local y v1 intactos)');
chk(c12.includes('const exenta = this.ball.ppTransito || this._elecRotoT > 0 || this.calib;'), 'exenciones honestas: portal, bola estallada, calibración');
chk(c12.includes('this.inHall || this.disposed'), 'hall y dispose fuera del guardián');
chk(c12.includes('// — MI SAQUE: la bola vive EN MI mano libre hasta el lanzamiento'), 'mi saque: bola en MI mano');
chk(c12.includes('this.ball.pos.copy(bh.pos);\n              this.ball.pos.y += BALL_HAND_LIFT;'), 'anclada a la mano libre real');
chk(c12.includes('this.ball.pos.set(0.3, 1.05, D.tableCenterZ + D.tableHalfLength + 0.4);'), 'escritorio: punto de saque reglamentario (antes quedaba congelada)');
chk(c12.includes('// — SAQUE DEL RIVAL: su mano libre si la pose llega fresca;'), 'saque del rival: mano si hay pose');
chk(c12.includes('this.net.avatarSample(smp) >= 0 &&\n              this.net.avatarStaleMs() < 500'), 'pose de red con frescura <500 ms');
chk(c12.includes('this._bgRival += dt;\n            if (this._bgRival > 0.6 || !this.ballMesh.visible) {'), 'sin pose >0,6 s o bola oculta → punto reglamentario');
chk(c12.includes('this.ball.pos.set(-0.3, 1.05,\n                D.tableCenterZ - D.tableHalfLength - 0.4);'), 'punto de saque REGLAMENTARIO del rival (jamás invisible)');
chk(c12.includes('this.net.setServeHeld(false);   // saca el rival (perspectiva local)'), 'FSM idle en saque → HELD re-armado (nadie sin bola)');
chk(c12.includes('const enMundo = isFinite(p.x) && isFinite(p.y) && isFinite(p.z) &&'), 'rallye: guardia anti-NaN');
chk(c12.includes('p.y > -2 && p.y < 7 && Math.abs(p.x) < 7 &&'), 'rallye: guardia anti-mundo (bola perdida)');
chk(c12.includes('p.set(0, D.tableTopY + 0.5, D.tableCenterZ + D.tableHalfLength * 0.4);'), 'bola perdida vuelve jugable a mi mitad');
chk(c12.includes('_bgTele(k) {') && c12.includes('if (this._bgTeleT > 0) return;\n    this._bgTeleT = 5;'), 'telemetría del guardián 1/5 s');
chk(c12.includes("__PP_TELE.ev('bola_guard', { k });"), 'evento bola_guard (mi_saque/rival_saque/rally_vis/rally_loca)');
chk(c12.includes('} catch (eBG) { /* el guardián nunca tumba el frame */ }'), 'el guardián nunca tumba el frame');
chk(c12.includes('this._bgHold = false;'), 'bandera _bgHold se renueva cada frame');

/* — 7 · I18N · ES/EN ——————————————————————————————————————————————————— */
console.log('7 · I18N · 7 claves nuevas ES y EN');
for (const k of ['poder_red', 'arc_red_go', 'arc_red_fin', 'poder_elec',
                 'arc_elec_go', 'arc_elec_fin', 'cause_elec']) {
  const es = (c00.match(new RegExp(`\\n    ${k}: '([^']*)',`)) || [])[1];
  const nEs = c00.split(`\n    ${k}: '`).length - 1;
  chk(nEs >= 2, `${k} existe en ES y EN (${nEs} idiomas)`);
  chk(!!es && es.length > 3, `${k} con contenido`);
}
chk(c00.includes("arc_red_go: '¡SÚPER RED! · la red crece AL DOBLE · 10 s',"), 'ES: red al doble');
chk(c00.includes("arc_elec_go: '¡SÚPER ELECTRICIDAD! · tormenta sobre tu rival · 10 s',"), 'ES: tormenta sobre tu rival');
chk(c00.includes("cause_elec: 'fulminada por la SÚPER ELECTRICIDAD',"), 'ES: causa del punto eléctrico');
chk(c00.includes("arc_red_go: 'SUPER NET! · the net grows TWICE as tall · 10 s',"), 'EN: super net');
chk(c00.includes("cause_elec: 'struck down by SUPER ELECTRICITY',"), 'EN: struck down by super electricity');

/* — 8 · GARANTÍAS · física y códec intactos ———————————————————————————— */
console.log('8 · GARANTÍAS · c04/c05/c09 sin una línea nueva (diff vs r24)');
for (const f of ['c04_fisica_ccd.js', 'c05_colisiones_ia_golpeo.js', 'c09_red_netlink.js']) {
  let diff = '';
  try {
    diff = execSync(
      `git -C ${raiz} diff bdd5707 -- src/game/core/${f} | head -40`,
      { encoding: 'utf8' });
  } catch (e) { diff = 'ERR ' + e.message; }
  chk(diff.trim() === '', `${f}: diff vacío contra la r24 (garantía intacta)`);
}
chk(!c12.slice(c12.indexOf('r25 (v3.6.120) · SÚPER RED (6.º poder'), c12.indexOf('_redTrigger(ent) {')).includes('stepPhysics'), 'SÚPER RED no toca el integrador (solo DIMS + visual)');
chk(!c12.includes("ball.ppElec"), 'SÚPER ELECTRICIDAD sin marcas nuevas en la bola (solo ocultación)');
chk(!c07.includes('ELEC_') && !c07.includes('PODER_RED'), 'c07 sin r25 (la tormenta vive en c12)');

/* — 9 · SELLOS ————————————————————————————————————————————————————————— */
console.log('9 · SELLOS de la ronda');
chk((c12.match(/r25 \(v3\.6\.120\)/g) || []).length >= 8, 'comentarios r25 (v3.6.120) por todo c12');
chk(c12.includes('«al activarlo hace crecer la altura de la red el doble del valor'), 'spec literal del dueño citada (red)');
chk(c12.includes('«de la bola salen rayos de electricidad'), 'spec literal del dueño citada (electricidad)');
chk(c12.includes('«en algún saque no se ve la bola'), 'informe del dueño citado (bola online)');

console.log(`\nR25 · ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
