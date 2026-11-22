#!/usr/bin/env node
/* CRAZY PING PONG · r127 · P4.2 · TEST DEL AUTODIAGNÓSTICO DE VERSIÓN.
 * La lección de la primera partida real dejó un residuo: el aviso por
 * HELLO (verCompara, r126) sólo ve al RIVAL. Si los DOS cascos retoman
 * pestañas viejas de la MISMA versión (3.6.100/107/108/110/111
 * conviviendo en el Quest Browser), el enlace queda limpio y el
 * desajuste con la web es invisible. r127 añade el AUTODIAGNÓSTICO: al
 * arrancar, el build corriendo se compara contra PAGES-VERSION.txt
 * (el SW lo sirve RED PRIMERO). Verifica la fuente REAL del Quest:
 *
 *   1 · PPNET.verSelf: decisión pura (igual / distinto / vacío / basura)
 *   2 · PPNET.selfcheckVersion: fetch PAGES-VERSION.txt?now= (no-store),
 *       parse del sello, aviso al juego SOLO si difiere, telemetría
 *       ver_selfcheck UNA vez por sesión SIEMPRE, silencio sin red
 *   3 · c12: el constructor dispara el self-check (fire-and-forget),
 *       onSelfcheckOutdated entra en la sala (pista + megáfono) y el
 *       panel online da PRIORIDAD a esta fila sobre la del rival
 *   4 · c00 i18n: net_selfcheck_warn / net_selfcheck_voice en ES y EN
 *   5 · public/sw.js: PAGES-VERSION.txt en VIVAS (red primero) — la
 *       garantía de que el self-check ve la web fresca; y el swr con
 *       ignoreSearch de game.html es justamente el residuo que cubre
 *   6 · VERSION.json y el sello const VERSION de c00 no van desacoplados
 *
 * Uso: node --no-warnings scripts/test_p4_selfcheck_v36116.mjs
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

/* — 1 · verSelf (pura, en el núcleo que corre en el Quest) ———————————— */
console.log('1 · PPNET.verSelf');
const V = PPNET.verSelf;
chk(typeof V === 'function', 'verSelf exportada por PPNET');
chk(V('3.6.115-SDK6', '3.6.115-SDK6').igual === true, 'build == web → igual');
const vm = V('3.6.115-SDK6', '3.6.116-SDK6');
chk(vm.igual === false, 'build viejo → aviso');
chk(vm.mineC === '3.6.115-SDK6'.slice(-6), 'versión corta propia (últimos 6)');
chk(vm.siteC === '3.6.116-SDK6'.slice(-6), 'versión corta de la web');
chk(V('', '3.6.116-SDK6').igual === false && V('', '3.6.116-SDK6').mineC === '?', 'build desconocido → aviso con ?');
chk(V('3.6.115-SDK6', '').igual === false && V('3.6.115-SDK6', '').siteC === '?', 'web sin sello → aviso con ?');
chk(V(undefined, null).igual === false, 'entradas basura → aviso sin petar');
chk(V(123, {}).igual === false, 'no-cadenas → aviso sin petar');
chk(V('a', 'a').mineC === 'a', 'cadenas cortas sin recorte roto');

/* — 2 · selfcheckVersion (comportamiento vivo con fetch simulado) ————— */
console.log('2 · PPNET.selfcheckVersion');
chk(typeof PPNET.selfcheckVersion === 'function', 'selfcheckVersion exportada por PPNET');
{
  const tele = [];
  globalThis.__PP_TELE = { ev: (k, d) => tele.push({ k, d }) };
  let ultimaUrl = null, ultimaInit = null;
  const conWeb = (texto, okResp = true) => {
    globalThis.fetch = async (url, init) => {
      ultimaUrl = url; ultimaInit = init || {};
      return { ok: okResp, status: okResp ? 200 : 404, text: async () => texto };
    };
  };
  const fichero = 'version=3.6.116-SDK6\nfuente_commit=abc123\ngame_sha256=deadbeef\n';
  const juego = { avisos: [], onSelfcheckOutdated(v) { this.avisos.push(v); } };

  // llamada 1: web con versión NUEVA → aviso + censo telemétrico
  conWeb(fichero);
  await PPNET.selfcheckVersion(juego);
  chk(juego.avisos.length === 1, 'build viejo + web nueva → onSelfcheckOutdated');
  chk(juego.avisos[0]?.igual === false
    && juego.avisos[0]?.mineC === '?'
    && juego.avisos[0]?.siteC === '3.6.116-SDK6'.slice(-6), 'aviso verSelf con corte a 6 y ? en build vacío');
  chk(ultimaUrl === 'PAGES-VERSION.txt?now=' + ultimaUrl?.split('?now=')[1], 'URL relativa PAGES-VERSION.txt con cache-buster now=');
  chk(ultimaInit.cache === 'no-store', 'fetch con cache no-store');
  chk(ultimaInit.signal instanceof AbortSignal, 'tope de 4 s vía AbortSignal');
  chk(tele.length === 1 && tele[0].k === 'ver_selfcheck', 'telemetría ver_selfcheck emitida (censo)');
  chk(tele[0].d.site === '3.6.116-SDK6', 'censo con la versión de la web');

  // llamada 2: el censo NO se repite (una vez por sesión)
  conWeb(fichero);
  await PPNET.selfcheckVersion(juego);
  chk(juego.avisos.length === 2, 'la segunda llamada sigue avisando');
  chk(tele.length === 1, 'censo ver_selfcheck UNA sola vez por sesión');

  // fichero SIN línea version= → silencio (la igualdad real la cubre verSelf en la sección 1)
  juego.avisos.length = 0;
  conWeb('fuente_commit=solo\n');
  await PPNET.selfcheckVersion(juego);
  chk(juego.avisos.length === 0, 'fichero sin sello version= → silencio');

  conWeb(fichero, false);           // 404
  await PPNET.selfcheckVersion(juego);
  chk(juego.avisos.length === 0, 'resp no ok → silencio');

  globalThis.fetch = async () => { throw new Error('sin red'); };
  await PPNET.selfcheckVersion(juego);
  chk(juego.avisos.length === 0, 'fetch que revienta → silencio (offline reina)');

  // juego sin el gancho → no peta
  conWeb(fichero);
  await PPNET.selfcheckVersion(null);
  chk(tele.length === 1, 'sin juego (null) → no peta y no duplica censo');

  delete globalThis.fetch; delete globalThis.__PP_TELE;
}

/* — 3 · c12 · arranque, sala y panel ——————————————————————————————————— */
console.log('3 · c12_pingponggame.js');
const c12 = lee('src/game/core/c12_pingponggame.js');
chk(c12.includes('this._selfWarnInfo = null;'), 'estado del aviso propio inicializado');
chk(c12.includes('PPNET.selfcheckVersion?.(this)'), 'constructor dispara el self-check (fire-and-forget)');
const ctor = c12.slice(c12.indexOf('this.net = new NetLink(this);'), c12.indexOf('this.net = new NetLink(this);') + 600);
chk(ctor.indexOf('selfcheckVersion') > -1 && ctor.indexOf('this.menuPage') > ctor.indexOf('selfcheckVersion'),
  'el self-check se dispara justo tras crear el enlace');
chk(c12.includes('onSelfcheckOutdated(vs) {'), 'onSelfcheckOutdated en el juego');
chk(c12.includes("this.rules.message = T('net_selfcheck_warn'"), 'mensaje de pista (rules.message)');
chk(c12.includes("this.audio.announce(T('net_selfcheck_voice')"), 'voz de megáfono');
chk(c12.includes('const sc126 = this._selfWarnInfo || null;'), 'panel consulta el estado del self-check');
chk(c12.indexOf('if (sc126) {') > -1 && c12.indexOf('if (sc126) {') < c12.indexOf('} else if (bm126) {'),
  'la fila del self-check tiene PRIORIDAD sobre la del rival');

/* — 4 · c00 · i18n ES/EN ——————————————————————————————————————————————— */
console.log('4 · c00_pre_three.js · i18n');
const c00 = lee('src/game/core/c00_pre_three.js');
chk((c00.match(/net_selfcheck_warn:/g) || []).length === 2, 'net_selfcheck_warn en ES y EN');
chk((c00.match(/net_selfcheck_voice:/g) || []).length === 2, 'net_selfcheck_voice en ES y EN');
chk(c00.includes("net_selfcheck_warn: 'Estás en una versión ANTIGUA ({b}) · en la web hay la {a}: cierra y reabre la web para actualizarte'"), 'texto ES con las dos versiones vivas');
chk(c00.includes("net_selfcheck_voice: 'versión antigua cierra y reabre la web para actualizarte'"), 'voz ES');
chk(c00.includes("net_selfcheck_warn: 'You are on an OLD build ({b}) · the web has {a}: close and reopen the web to update'"), 'texto EN');
chk(c00.includes("net_selfcheck_voice: 'old version close and reopen the web to update'"), 'voz EN');

/* — 5 · sw.js · la garantía de frescura ———————————————————————————————— */
console.log('5 · public/sw.js');
const sw = lee('public/sw.js');
chk(/\/\\\/PAGES-VERSION\\.txt\$\//.test(sw) || sw.includes('PAGES-VERSION\\.txt$'), 'PAGES-VERSION.txt en VIVAS (red primero)');
chk(sw.includes('ignoreSearch: true') && sw.includes("endsWith('/game.html')"), 'game.html en SWR con ignoreSearch — el residuo que este self-check cubre');

/* — 6 · VERSION.json y c00 van de la mano —————————————————————————————— */
console.log('6 · sellos coherentes');
const ver = JSON.parse(lee('src/game/VERSION.json'));
chk(c00.includes(`const VERSION = '${ver.version}';`), 'const VERSION de c00 == VERSION.json (' + ver.version + ')');

console.log(`\n${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
