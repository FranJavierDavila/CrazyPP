#!/usr/bin/env node
/* CRAZY PING PONG · r126 · P4.1 · TEST DE AVISO DE BUILD DISTINTO.
 * La primera partida real (host 3.6.114 vs invitado 3.6.102) jugó «a
 * medias»: bola espejada, pala a 45º y sin voz, con el HELLO v2 en verde
 * (PROTO/PHYS iguales) y el aviso de build SOLO en el menú — invisible
 * con la visera puesta. Verifica la fuente REAL que corre en el Quest:
 *
 *   1 · PPNET.verCompara: decisión pura (igual / distinto / vacío / basura)
 *   2 · c09 hello2: usa verCompara, llama onBuildMismatch, telemetría
 *       ver_mismatch y accesorio vivo buildMismatch()
 *   3 · c12: onBuildMismatch entra en la sala (mensaje de pista + voz)
 *       y el panel online pinta la fila roja
 *   4 · c00 i18n: net_build_warn sin la referencia muerta v3674 +
 *       net_build_voice en ES y EN
 *   5 · deploy_pages.py: el landing enlaza game.html?v=@@VERSION@@
 *       (cache-busting: mata los builds antiguos del navegador del Quest)
 *
 * Uso: node --no-warnings scripts/test_p4_ver_mismatch_v36115.mjs
 */
import { PPNET } from '../src/game/core/c09b_red_nucleo.js';
import { readFileSync } from 'node:fs';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');

/* — 1 · verCompara (pura, en el núcleo que corre en el Quest) ———— */
console.log('1 · PPNET.verCompara');
const V = PPNET.verCompara;
chk(typeof V === 'function', 'verCompara exportada por PPNET');
chk(V('3.6.115-SDK6', '3.6.115-SDK6').igual === true, 'builds idénticos → igual');
const vm = V('3.6.102-SDK6', '3.6.115-SDK6');
chk(vm.igual === false, 'builds distintos → aviso');
chk(vm.peerC === '3.6.102-SDK6'.slice(-6), 'versión corta del rival (últimos 6)');
chk(vm.mineC === '3.6.115-SDK6'.slice(-6), 'versión corta propia');
chk(V('', '3.6.115-SDK6').igual === false && V('', '3.6.115-SDK6').peerC === '?', 'rival sin build → aviso con ?');
chk(V('3.6.115-SDK6', '').igual === false && V('3.6.115-SDK6', '').mineC === '?', 'propio sin build → aviso con ?');
chk(V(undefined, null).igual === false, 'entradas basura → aviso sin petar');
chk(V(123, {}).igual === false, 'no-cadenas → aviso sin petar');
chk(V('a', 'a').peerC === 'a', 'cadenas cortas sin recorte roto');

/* — 2 · c09 · hello2 avisado + telemetría ————————————————————— */
console.log('2 · c09_red_netlink.js · hello2');
const c09 = lee('src/game/core/c09_red_netlink.js');
chk(c09.includes('PPNET.verCompara(m.b, PPNET.VP.BUILD)'), 'hello2 decide con verCompara');
chk(c09.includes("onBuildMismatch?.(vc)") && c09.includes("onBuildMismatch?.(null)"), 'avisa EN LA SALA (y limpia pareja nueva)');
chk(c09.includes("ver_mismatch"), 'telemetría ver_mismatch (una vez por sesión)');
chk(c09.includes('__PP_TELE?.ev?.') , 'emisor de telemetría con guardia opcional');
chk(c09.includes('buildMismatch()') && c09.includes('this._buildWarn ? PPNET.verCompara'), 'accesorio vivo buildMismatch()');
chk(c09.includes('this._verTele = false;'), 'flag de telemetría se resetea por sesión');

/* — 3 · c12 · el aviso entra en la sala y el panel lo pinta ———— */
console.log('3 · c12_pingponggame.js · sala');
const c12 = lee('src/game/core/c12_pingponggame.js');
chk(c12.includes('onBuildMismatch(vc) {'), 'onBuildMismatch en el juego');
chk(c12.includes("this.rules.message = T('net_build_warn'"), 'mensaje de pista (rules.message)');
chk(c12.includes("this.audio.announce(T('net_build_voice')"), 'voz de megáfono');
chk(c12.includes('net.buildMismatch ? net.buildMismatch() : null'), 'panel online consulta el estado vivo');
chk(c12.includes("wrapText(c, T('net_build_warn'"), 'fila roja del panel con wrapText');

/* — 4 · c00 · i18n ES/EN sin textos muertos ———————————————————— */
console.log('4 · c00_pre_three.js · i18n');
const c00 = lee('src/game/core/c00_pre_three.js');
chk(c00.includes("net_build_voice: 'rival con otra versión recargad el juego en los dos visores'"), 'net_build_voice ES');
chk(c00.includes("net_build_voice: 'rival on another build reload the game on both headsets'"), 'net_build_voice EN');
chk(c00.includes('net_build_warn') && !c00.includes('v3674'), 'net_build_warn sin la referencia muerta v3674');
chk((c00.match(/net_build_warn:/g) || []).length === 2, 'net_build_warn presente en ES y EN');

/* — 5 · deploy_pages.py · cache-busting del landing ———————————— */
console.log('5 · deploy_pages.py · landing');
const dp = lee('scripts/deploy_pages.py');
chk(dp.includes('href="game.html?v=@@VERSION@@"'), 'JUGAR enlaza game.html?v=VERSION');
chk((dp.match(/href="game\.html/g) || []).length === 1, 'único enlace game.html del landing, ya busteado');

console.log(`\n${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
