#!/usr/bin/env node
/* CRAZY PING PONG · r23 · v3.6.118 · TEST: SPIN VISIBLE + HALL DEL ANFITRIÓN.
 * Dos peticiones del dueño, una ronda:
 *
 *   F1 · LA BOLA GIRA (spin visible) — la textura de las skins dejó a la
 *        vista que la bola no rotaba: «si se le imprime un efecto tendría
 *        cierto spin en la dirección del efecto, lo mismo al botar».
 *        · c12: _bolaSpinTick (rotateOnWorldAxis sobre el ω REAL de la
 *          física — el mismo que alimenta Magnus y el bote), ganancia
 *          visual 0.14, reposo honesto (< 0.5 rad/s sin giro), cero
 *          asignaciones (scratch de módulo), integrado en el tick §7.
 *        · El «latigazo» del bote sale gratis: bounceOnTable ya actualiza ω.
 *        · F1b RED: ω YA viaja (v1: 'h'/'p' con s:[x,y,z] + spinFromNet;
 *          v2: HIT/TOSS/HANDOFF con ev.s + fantasma con física real) —
 *          el invitado ve el MISMO giro sin código nuevo de red.
 *        · GARANTÍA: c04/c05 (física) no conocen el mesh ni el render.
 *
 *   F2 · HALL DEL ANFITRIÓN — «ambos jugadores pueden estar en el Hall
 *        del Anfitrión: presumir de lo conseguido (insignias y mejoras)
 *        para que otros quieran esos logros cosméticos».
 *        · c09: HELLO v2 lleva `hp` (perfil OPCIONAL, JSON tolerante).
 *        · c12: hallProfile() compacto · onPeerHall() SANEADO (números
 *          acotados, ids contra catálogo, arrays con tope) · _hallPerfil()
 *          (invitado online → EL DEL ANFITRIÓN) · drawHall repinta la
 *          pared de insignias · enterHall/exitHall con modo VISITA online
 *          (física de red intacta) · salida forzosa en MATCH_START y en
 *          desconexión · _bolaSkinEfectiva (la restauración del hall no
 *          desviste la skin del host) · avatar del rival dormido en el
 *          museo · tarjeta HALL + subpágina salahall + hall_entrar.
 *        · c08: drawHallGloria (placa 1024×640 procedural: 6 medallones,
 *          16 chips de bola, 5 paletas de mesa) + placa colgada en el
 *          frente del hall y registrada en userData.hall.gloria.
 *        · c00: 14 claves nuevas ES/EN (+ hint_sala_bola que la r21 dejó
 *          huérfano).
 *
 * Uso: node --no-warnings scripts/test_r23_hall_spin_v36118.mjs
 */
import { BOLA_ASPECTOS, MESA_ASPECTOS } from '../src/game/core/c02_cfg_escena.js';
import { readFileSync } from 'node:fs';
/* c00/c06 NO se importan: c00 toca window en el arranque (sólo navegador).
 * ACHIEVEMENTS se comprueba leyendo c06 (fuente), como el resto de fichas. */

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');

/* — 1 · F1 · spin visible (c12) ——————————————————————————————————— */
console.log('1 · F1 · SPIN VISIBLE (c12 · capa render)');
const c12 = lee('src/game/core/c12_pingponggame.js');
chk(c12.includes('const BOLA_SPIN_AX = new THREE.Vector3();'), 'scratch de módulo (cero asignaciones por frame)');
chk(c12.includes('BOLA_SPIN_GANANCIA = 0.45'), 'ganancia visual (r23: 0.14 → r24: 0.45 — «el giro era muy sutil»; |ω|=110 → ~7,9 rev/s)');
chk(c12.includes('_bolaSpinTick(dt) {'), '_bolaSpinTick: el giro vive en un método propio');
chk(c12.includes('this._bolaSpinTick(dt);'), 'integrado en el tick §7 (sincronizar visuales)');
chk(c12.includes('BOLA_SPIN_AX.set(spin.x, spin.y, spin.z).multiplyScalar(1 / w);'), 'eje = ω normalizado (el vector EXACTO de la física)');
chk(c12.includes('m.rotateOnWorldAxis(BOLA_SPIN_AX, w * dt * BOLA_SPIN_GANANCIA);'), 'rotateOnWorldAxis: giro sobre eje mundo (no Euler XY)');
chk(c12.includes('if (w < 0.5) return;'), 'reposo honesto: |ω|<0.5 rad/s → sin giro fantasma');
chk(!c12.includes('this.ballMesh.rotation.x += this.ball.spin.x'), 'adiós al Euler XY de 0.05 (la textura pintada y estática)');
chk(c12.includes('SPIN VISIBLE (F1)'), 'comentario de la ronda en el tick');

/* — 2 · F1b · ω ya viaja por la red (sin código nuevo) ————————————— */
console.log('2 · F1b · ω EN LA RED (v1 stream + v2 eventos · ya existía)');
const c09 = lee('src/game/core/c09_red_netlink.js');
chk(c09.includes("s: [+g.ball.spin.x.toFixed(2), +g.ball.spin.y.toFixed(2), +g.ball.spin.z.toFixed(2)]"), "v1: sendHit lleva s:[x,y,z]");
chk(c09.includes('static spinFromNet(a, out)'), 'v1: spinFromNet (espejo del pseudovector)');
chk(c09.includes('if (s.s) NetLink.spinFromNet(s.s, ball.spin);'), 'v1: applyBallStream aplica el spin al invitado');
chk(c09.includes('_spinNet(v3)'), 'v2: el estado de bola del host lleva spin saneado');
chk(c09.includes('NetLink.spinFromNetArr(ev.s)'), 'v2: HIT/TOSS/HANDOFF traen ev.s');
chk(c09.includes('this._spinNet(g.ball.spin)'), 'v2: netLocalHit/TITLE emiten el spin del golpe');
chk(c12.includes('stepPhysics(dtFis * this._dilF, this.ball, enMiMitad ? pads : [], this.events);'), 'v2: el fantasma del invitado simula con la FÍSICA REAL (spin vivo local — re-anclada r43: física en tiempo real dtFis)');
chk(c12.includes('_bolaSpinTick(dt) {') && c12.includes('this.ballMesh.position.copy(this.ball.pos);'), 'el mismo tick visual corre para host e invitado');

/* — 3 · F2 · perfil en la red (c09 + c12) ————————————————————————— */
console.log('3 · F2 · HALL DEL ANFITRIÓN · perfil en HELLO v2');
chk(c09.includes("hp: (this.game && typeof this.game.hallProfile === 'function') ? this.game.hallProfile() : undefined"), 'hello2 envía hp (opcional, con guardia de existencia)');
chk(c09.includes("if (m.hp && typeof m.hp === 'object') this.game?.onPeerHall?.(m.hp);"), 'recepción: sólo objetos → onPeerHall');
chk(c09.includes('try {\n          if (m.hp && typeof m.hp === \'object\') this.game?.onPeerHall?.(m.hp);\n        } catch'), 'envuelto en try (jamás rompe el enlace — patrón sk)');
chk(c12.includes('hallProfile() {'), 'hallProfile(): perfil compacto del dueño');
chk(c12.includes('w: d.won | 0, bs: d.bestStreak | 0, st: this._retosEstrellas() | 0,'), 'cifras acotadas (victorias, mejor racha, ★)');
chk(c12.includes('onPeerHall(hp) {'), 'onPeerHall: saneado a fondo');
chk(c12.includes('const num = (v) => { const n = +v; return isFinite(n) ? Math.max(0, Math.min(99999, n | 0)) : 0; };'), 'números: finitos, ≥0, ≤99999, enteros');
chk(c12.includes('.filter((s) => typeof s === \'string\' && ok.indexOf(s) >= 0)'), 'ids SOLO contra catálogo (sin inyección de strings)');
chk(c12.includes('a: ids(hp.a, A_OK, 8), bl: ids(hp.bl, B_OK, 16), ms: ids(hp.ms, M_OK, 8),'), 'arrays con tope (8 logros · 16 bolas · 8 mesas)');
/* r24: dentro del if ahora se viste TAMBIÉN el arte del anfitrión
 * (applyHallVariant con hp.hv) antes de repintar la placa. */
chk(c12.includes('if (this.net && this.net.online && this.net.role === \'guest\' && this.inHall) {\n        if (this._hallPeer.hv) {\n          try { applyHallVariant(this.hallGroup, hallVariantePorId(this._hallPeer.hv).base); } catch (eHV) { /* */ }\n        }\n        this.drawHall();'), 'si el invitado está DENTRO del hall: repinta al vuelo (r24: y viste el ARTE del anfitrión)');
chk(c12.includes('_hallPerfil() {'), '_hallPerfil: perfil ACTIVO (propio o del anfitrión)');
chk(c12.includes('return { p: this._hallPeer, peer: true };'), 'invitado online → EL DEL ANFITRIÓN');

/* — 4 · F2 · pared de insignias (c08) ————————————————————————————— */
console.log('4 · F2 · PARED DE INSIGNIAS (c08 · procedural)');
const c08 = lee('src/game/core/c08_hall_hud.js');
chk(c08.includes('export function drawHallGloria(cv, d) {'), 'drawHallGloria exportado');
chk(c08.includes("hallCanvas(1024, 640)"), 'lienzo 1024×640 (museo, como los carteles)');
chk(c08.includes("gloria: { cv: gloriaCv, tex: gloriaTex }"), 'registrada en userData.hall.gloria');
chk(c08.includes('gloriaMesh.position.set(0, 1.60, z0 + 0.012)'), 'colgada en el FRENTE (la primera pared que mira el anfitrión)');
chk(c08.includes('new THREE.CanvasTexture(gloriaCv)'), 'canvas → CanvasTexture (cero bytes en el bundle)');
chk(c08.includes("x.fillText(L.e || '★', cx, cy - 13);"), 'medallones con emoji (técnica drawHallMedal de la casa)');
chk(c08.includes("B.on ? 'rgba(233,184,60,0.85)' : '#3a4048'"), 'chips de bola: oro si abierta, gris si no (vitrina que anima)');
chk((c08.match(/drawHallGloria/g) || []).length >= 2, 'pintor definido y usado en createHall (y repintado en drawHall de c12)');
chk(c12.includes('drawHallGloria(udG.gloria.cv, {') && c12.includes('drawHallGloria, '), 'c12 lo importa y lo llama en drawHall');

/* — 5 · F2 · visita online (c12 · enterHall/exitHall/FSM) —————————— */
console.log('5 · F2 · VISITA ONLINE (c12 · museo con la red viva)');
chk(c12.includes('const online = !!(this.net && this.net.online);'), 'enterHall detecta online');
chk(c12.includes("if (online && this.rules.state === 'rally') return;"), 'en pleno rally NO se visita el museo');
chk(c12.includes('this._hallVisit = online;'), 'modo visita marcado (_hallVisit)');
chk(c12.includes('if (!online) {\n      // arranque LIMPIO local'), 'local: arranque limpio de siempre (intacto)');
chk(c12.includes('if (this.ballMesh) this.ballMesh.visible = false;\n      if (this.trailObj) this.trailObj.visible = false;\n      if (this.blob) this.blob.visible = false;'), 'visita: la bola se ESCONDE sin resetear (fantasma v2 sigue vivo)');
chk(c12.includes('if (!online) this._hallResetBall(true);   // r23: en visita la bola no se resetea'), 'visita: _hallResetBall NO toca la bola');
chk(c12.includes('const visita = !!this._hallVisit;   // r23 · visita online: salida sin tocar la bola'), 'exitHall distingue la visita');
chk(c12.includes('if (this.ballMesh) this.ballMesh.visible = true;\n      if (this.trailObj) this.trailObj.visible = this.showTrail !== false;\n      if (this.blob) this.blob.visible = true;'), 'salida de visita: la bola VUELVE tal cual');
chk(c12.includes('if (this.inHall) this.exitHall();'), 'MATCH_START saca al visitante (la cancha vuelve antes de la cuenta atrás)');
chk(c12.includes('this.aiPaddleMesh.visible = !this.inHall;'), 'avatar del rival dormido en el museo (v2 y v1)');
chk(c12.includes('const show = code >= 0 && stale < 500 && !this.inHall;'), 'visor del rival tampoco flota entre cuadros');
chk(c12.includes('if (this.net && this.net.online && this.net.role === \'guest\' && this._peerSkinId)'), '_bolaSkinEfectiva: online el invitado viste LA DEL ANFITRIÓN');
chk(c12.includes('try { this._bolaTinte(this._bolaSkinEfectiva()); } catch (eSkin)'), 'la restauración del hall no desviste la skin del host');
chk(c12.includes('this._hallPeer = null;\n    this._peerSkinId = null;'), 'desconexión: fuera perfiles del rival');
chk(c12.includes('this.exitHall();       // visita en curso: la cancha vuelve primero'), 'desconexión en visita: cancha primero…');
chk(c12.includes('this.enterHall();      // …y re-entra ya con TU perfil repintado'), '…y re-entra al hall PROPIO');

/* — 6 · F2 · menú (tarjeta + subpágina + dispatcher) ——————————————— */
console.log('6 · F2 · MENÚ · tarjeta HALL + subpágina + ENTRAR');
chk(c12.includes("'page:optsSalaHall'"), 'tarjeta HALL en SALA (4.ª)');
chk(c12.includes("arg === 'optsSalaBola' || arg === 'optsSalaHall'"), 'navegación permite optsSalaHall');
chk(c12.includes("case 'salahall': {"), 'subpágina salahall');
chk(c12.includes("case 'hall_entrar': {"), 'dispatcher hall_entrar');
chk(c12.includes("btn('hall_entrar', 56, y, 912, 62, T('hall_entrar')"), 'botón ENTRAR AL HALL');
chk(c12.includes("'page:optsSalaHall': 'hint_sala_hall', 'hall_entrar': 'hint_hall_entrar',"), 'tooltips del menú (norma r96)');
chk(c12.includes("this.closeMenu();\n          this.enterHall();"), 'ENTRAR: cierra menú y entra al hall');
chk(c12.includes("T('hall_stats', { w: pH.w, r: pH.bs, s: pH.st, e: pH.el })"), 'la subpágina muestra las cifras del perfil ACTIVO');

/* — 7 · c00 · i18n ES/EN ——————————————————————————————————————————— */
console.log('7 · c00_pre_three.js · i18n ES/EN');
const c00 = lee('src/game/core/c00_pre_three.js');
const claves = ['cat_salahall', 'sub_hall_sub', 'hall_gloria_t', 'hall_gloria_peer',
  'hall_gloria_sub', 'hall_gloria_sub_peer', 'hall_stats', 'hall_visitando',
  'hall_en_rally', 'hall_entrar', 'hall_cosmetica', 'hint_sala_bola',
  'hint_sala_hall', 'hint_hall_entrar'];
let i18nOk = true;
for (const k of claves) {
  // frontera de palabra EXCLUYENDO guion bajo previo (hint_hall_entrar ≠ hall_entrar)
  const n = (c00.match(new RegExp('(^|[^_A-Za-z])' + k + ':', 'g')) || []).length;
  if (n !== 2) { i18nOk = false; console.log(`      · ${k}: ${n} apariciones (deben ser 2 — ES y EN)`); }
}
chk(i18nOk, `las ${claves.length} claves nuevas están en ES y EN`);
chk(c00.includes("hall_gloria_peer: 'HALL DEL ANFITRIÓN'"), 'título de visita ES');
chk(c00.includes("hall_entrar: '⌂ ENTRAR AL HALL'") && c00.includes("hall_entrar: '⌂ ENTER THE HALL'"), 'botón ENTRAR ES/EN');
chk(c00.includes("hint_sala_bola:"), 'hint_sala_bola ya no es huérfano (r21 lo dejaba sin tooltip)');

/* — 8 · GARANTÍA · física intacta + cosmético puro ————————————————— */
console.log('8 · GARANTÍA · c04/c05 no saben NADA de esto');
const c04 = lee('src/game/core/c04_fisica_ccd.js');
const c05 = lee('src/game/core/c05_colisiones_ia_golpeo.js');
chk(!c04.includes('_bolaSpinTick') && !c05.includes('_bolaSpinTick'), 'ni c04 ni c05 conocen el giro visible');
chk(!c04.includes('ballMesh') && !c05.includes('ballMesh'), 'la física NO conoce el mesh (spin ≡ datos, el render decide)');
chk(!c04.includes('BOLA_SPIN') && !c05.includes('BOLA_SPIN'), 'scratch del giro SOLO en c12');
chk(!c04.includes('hallProfile') && !c05.includes('hallProfile'), 'el hall profile jamás entra en la física');
chk(!c04.includes('rotateOnWorldAxis') && !c05.includes('rotateOnWorldAxis'), 'cero rotación de mesh en la física');
chk(c04.includes('export function applyBounceSpin(vel, spin, kickMul)') &&
    c04.includes('export function bounceOnTable(vel, spin, impact, coupleMul)'), 'el bote sigue actualizando ω (el latigazo del F1 sale de AHÍ)');
chk(c04.includes('spin.multiplyScalar(0.72);'), 'fricción del bote intacta (0.72)');
chk(c12.includes('import * as THREE from \'three\';'), 'c12 usa el THREE real (rotateOnWorldAxis existe desde r101)');

/* — 9 · catálogos vivos (fuente c06 + importados c02) ———————————————— */
console.log('9 · catálogos vivos (c06 fuente + c02 importado)');
const c06 = lee('src/game/core/c06_logros_stats_ia_rival.js');
const mAch = c06.match(/export const ACHIEVEMENTS = \[([\s\S]*?)\];/);
const achItems = mAch ? (mAch[1].match(/\{ key:/g) || []).length : 0;
chk(achItems === 6, `6 logros en ACHIEVEMENTS (${achItems})`);
const achOk = /export const ACHIEVEMENTS = \[[\s\S]*?\];/.test(c06) &&
  c06.includes("emoji: '🥇'") && c06.includes("emoji: '🎯'");
chk(achOk, 'cada logro con emoji (los que pinta la placa)');
chk(BOLA_ASPECTOS.length === 16 && MESA_ASPECTOS.length === 5, '16 skins de bola + 5 mesas (los chips de la placa)');
chk(BOLA_ASPECTOS.every((s) => typeof s.color === 'number'), 'todas las skins con color (chip de la placa)');
chk(MESA_ASPECTOS.every((s) => typeof s.top === 'number'), 'todas las mesas con top (paleta de la placa)');
const hpFiltrado = (arr, ok2, max) => (Array.isArray(arr) ? arr : [])
  .filter((s) => typeof s === 'string' && ok2.indexOf(s) >= 0).slice(0, max);
const inyeccion = ['blanca', '"><script>', 'saturno', 'wins10; drop table', 42, null];
chk(hpFiltrado(inyeccion, BOLA_ASPECTOS.map((s) => s.id), 16).join() === 'blanca,saturno',
  'saneo de ids: la inyección cae (solo ids de catálogo, basura fuera)');
chk(hpFiltrado(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'], ['a','b','c','d','e','f','g','h','i'], 8).length === 8,
  'tope de array respetado (9 → 8)');

console.log(`\n${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
