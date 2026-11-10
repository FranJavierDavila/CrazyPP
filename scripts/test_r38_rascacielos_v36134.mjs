#!/usr/bin/env node
/* CRAZY PING PONG · r38 · v3.6.137-SDK6 · FASE 139 · TEST: EL SALÓN DE LA
 * PARTIDA — RASCACIELOS (4.º hall del dueño + partidas en el hall del
 * anfitrión, IA y multijugador).
 *
 *   A · RASCACIELOS — «te doy material para un nuevo hall, "Rascacielos"
 *       rascacielos.zip y su melodía "rascacielos.mp3". Mismo comportamiento
 *       que el resto de halls»: 6 JPG byte-exactos contra el ZIP en las
 *       medidas EXACTAS de la spec v3.6.28 (frente/fondo 1849×864 ·
 *       laterales 2395×864 · suelo/techo 1296×1678 — comprobado al
 *       instalar), pista rascacielos.mp3 byte-exacta junto a su arte,
 *       variante en HALL_VARIANTES (c02) con candado hito_won25 (25
 *       victorias), i18n ES/EN (nombre + hint + candado), mobiliario 3D
 *       propio en montarProps (torres con ventanas + baliza que flicker).
 *
 *   B · EL SALÓN DE LA PARTIDA — «Vamos a permitir que las partidas se
 *       realicen en el hall que tenga configurado el anfitrión, tanto para
 *       las modalidades contra la IA como en el modo multijugador»:
 *       createChampRoom (c08) estrena la TERCERA fuente de arte por cara
 *       (campeonato → salón del anfitrión → arte por defecto del partido)
 *       con carga perezosa a prueba de fallos (buildHallFor + HALL_FICHAS);
 *       c12 resuelve QUÉ salón manda (_hallVariantePartido: local = TU
 *       variante validada; online invitado = la del ANFITRIÓN viajada en
 *       hp.hv / hallv) y aplica SU pista en CADA startMatch por el punto
 *       único del árbitro (onMatchStart → _hallMusicaPartidoAplicar —
 *       idempotente, calla en campeonato y en la estancia).
 *
 *   C · SALÓN EN VIVO POR LA RED — el anfitrión que cambia de salón lo
 *       anuncia por el evento FIABLE hallv (c09: lista de claves _onRel +
 *       despacho → game.onPeerHallVar); el invitado re-viste estancia (si
 *       visita), cancha (champRoom nota el cambio de base) y pista; hp
 *       recibido con el invitado EN LA CANCHA re-arma la pista (onPeerHall).
 *       Builds viejos: el switch ignora la clave sin romper (JSON tolerante).
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 sha256 BYTE-EXACTO contra la r26b
 *   (df8f71a3… / 8bb62082…).
 *
 * Uso: node --no-warnings scripts/test_r38_rascacielos_v36137.mjs
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
const leeB = (p) => readFileSync(raiz + p);
const sha256 = (p) =>
  createHash('sha256').update(leeB(p)).digest('hex');

const c02 = lee('src/game/core/c02_cfg_escena.js');
const c08 = lee('src/game/core/c08_hall_hud.js');
const c09 = lee('src/game/core/c09_red_netlink.js');
const c12 = lee('src/game/core/c12_pingponggame.js');
const c00 = lee('src/game/core/c00_pre_three.js');
const vjson = JSON.parse(lee('src/game/VERSION.json'));
const game = lee('public/game.html');
const cuerpo = lee('src/game/03_body.html');

/* — 1 · SELLOS · v3.6.137-SDK6 · FASE 139 ————————————————————————— */
console.log('1 · SELLOS · v3.6.137-SDK6 · FASE 139 · EL SALÓN DE LA PARTIDA');
chk(vjson.version === '3.6.137-SDK6', 'VERSION.json: 3.6.137-SDK6');
chk(vjson.fase === 139, 'FASE 139');
chk(vjson.faseNombre === 'El Arcano holográfico — pulido del dueño', 'faseNombre = EL SALÓN DE LA PARTIDA');
chk(vjson.tamano === 11473088, 'tamaño del build: 11.473.088 B');
chk(vjson.golden ===
  '543863157c0d8ab3348d7b78edc52a0d262c7ebd132c42db1933e878b1325227',
  'VERSION.json golden 54386315…');
chk(sha256('public/game.html') ===
  '543863157c0d8ab3348d7b78edc52a0d262c7ebd132c42db1933e878b1325227',
  'golden 54386315… (build byte-exacto)');
chk(game.includes('3.6.137-SDK6'), 'bundle con sello vigente');
chk(c00.includes("const VERSION = '3.6.137-SDK6'"), 'sello c00 = 3.6.137-SDK6');
chk(lee('public/sw.js').includes("CACHE = 'crazypp-v3.6.137-SDK6'"),
  'sw.js CACHE v3.6.137-SDK6 (purga de cachés viejas)');
chk(cuerpo.includes('>V3.6.137-SDK6</span>'), 'badge V3.6.137-SDK6 en 03_body');
chk(lee('src/app/descargas/page.tsx').includes('v36137-sdk6'),
  'hub /descargas sellado a v36137-sdk6');

/* — 2 · ARTE RASCACIELOS · 7 ficheros byte-exactos contra el ZIP ———— */
console.log('2 · ARTE RASCACIELOS · sha256 byte-exacto (ZIP del dueño → public/assets/hall/rascacielos)');
const ARTE = {
  'assets/hall/rascacielos/frente.jpg':     '96d7f5c7ff26f6cc',
  'assets/hall/rascacielos/fondo.jpg':      '2bcaca3ce10b45e6',
  'assets/hall/rascacielos/izquierda.jpg':  '8ee8655015704c20',
  'assets/hall/rascacielos/derecha.jpg':    '46955c95636a7107',
  'assets/hall/rascacielos/suelo.jpg':      '19a894e85061684e',
  'assets/hall/rascacielos/techo.jpg':      'd8d7a647d04fc5ac',
  'assets/hall/rascacielos/rascacielos.mp3': '81d284acb52cdee6',
};
for (const [p, h16] of Object.entries(ARTE)) {
  const bueno = sha256('public/' + p).startsWith(h16);
  chk(bueno, (bueno ? '' : 'FALTA/ALTERADO ') + p + ' · sha256 ' + h16 + '…');
}

/* — 3 · CATÁLOGO · HALL_VARIANTES + hito + i18n ———————————————————— */
console.log('3 · CATÁLOGO · variante rascacielos · hito_won25 · i18n ES/EN');
chk(c02.includes("{ id: 'rascacielos', lock: 'hito_won25', nameKey: 'hall_var_rascacielos',"),
  'HALL_VARIANTES: entrada rascacielos con hito_won25');
chk(c02.includes("base: 'assets/hall/rascacielos/'"), 'base = assets/hall/rascacielos/');
chk(c02.includes("musica: 'assets/hall/rascacielos/rascacielos.mp3'"),
  'musica = rascacielos.mp3 (pista del salón, canal c03 + icono c08)');
const bloqHv = (c02.split('const HALL_VARIANTES = [')[1] || '').split('];')[0];
chk((bloqHv.match(/\{ id: '/g) || []).length === 6,
  '6 variantes en el catálogo (anfitrion, cabana, neon, observatorio, dojo, rascacielos)');
chk(c12.includes("if (lock === 'hito_won25') return (d.won || 0) >= 25;"),
  '_mesaLibre: hito_won25 = 25 victorias');
chk(c12.includes("if (lock === 'hito_won25') return T('mesa_lock_won25');"),
  '_mesaLockTxt: hito_won25 → mesa_lock_won25');
chk(c00.includes("hall_var_rascacielos: 'RASCACIELOS'") &&
    c00.includes("hall_var_rascacielos: 'SKYSCRAPER'"),
  'i18n hall_var_rascacielos ES/EN');
chk(c00.includes('hint_hall_var_rascacielos: ') &&
    (c00.match(/hint_hall_var_rascacielos:/g) || []).length === 2,
  'i18n hint_hall_var_rascacielos ES/EN');
chk(c00.includes("mesa_lock_won25: 'Hito: 25 victorias'") &&
    c00.includes("mesa_lock_won25: 'Milestone: 25 wins'"),
  'i18n mesa_lock_won25 ES/EN');
chk(c08.includes("b === 'assets/hall/rascacielos/'"),
  'montarProps: mobiliario 3D del RASCACIELOS');
chk(c08.includes('baliza.userData.flicker = balizaMat'),
  'mobiliario rascacielos: baliza VIVA (flicker en updateHallFx)');
chk(c12.includes('HALL_VARIANTES.length / 3'), 'selector del menú: rejilla dinámica (6 → 2 filas)');

/* — 4 · EL SALÓN DE LA PARTIDA · arte (c08) + resolución (c12) ————— */
console.log('4 · SALÓN DE LA PARTIDA · cadena campeonato→salón→por defecto');
chk(c08.includes('buildHallFor(base)'), 'c08: buildHallFor (carga perezosa del vestido del salón)');
chk(c08.includes("floor: 'suelo.jpg', ceil: 'techo.jpg', left: 'izquierda.jpg'"),
  'c08: HALL_FICHAS — los 6 nombres exactos de la casa');
chk(c08.includes("const eff = (k) => champTex(k) || hallTex(k) || defaultTexs[k] || null;"),
  'c08: cadena EFECTIVA por cara — champ → hall → por defecto');
chk(c08.includes('game.mesaOcupada && game.mesaOcupada()'),
  'c08: el salón calla en campeonato (mesaOcupada gana su decorado)');
chk(c08.includes("if (hallSet !== mine) { try { tex.dispose(); } catch { /* */ } return; }"),
  'c08: carga a prueba de carreras (set sustituido → tex huérfano se libera)');
chk(c12.includes('hallBasePartido() {'), 'c12: hallBasePartido (la base que lee champRoom)');
chk(c12.includes('_hallVariantePartido() {'), 'c12: _hallVariantePartido (resolución local/anfitrión)');
chk(c12.includes("if (!id) return null;          // anfitrión build viejo: cancha clásica"),
  'c12: invitado sin hp (build viejo) → cancha clásica (JSON tolerante)');
chk(c12.includes('return hallVariantePorId(id);  // saneado contra el catálogo (r24)'),
  'c12: id del anfitrión SANEADO contra catálogo (sin candado — el dueño ya lo abrió)');
chk(c12.includes('try { this._hallMusicaPartidoAplicar(); } catch (eHM8) { /* */ }'),
  'c12: PUNTO ÚNICO onMatchStart → la pista del salón nace en TODA partida');
chk(c12.includes('if (this.inHall) return;               // la estancia manda (enterHall)'),
  'c12: en la estancia del hall manda enterHall (sin pisar la visita)');
chk(c12.includes('this.audio.setHallWanted(false, null);') &&
    c12.includes('// campeonato: SU aire (BSO)'),
  'c12: en campeonato la pista del salón CALLA (BSO del torneo)');

/* — 5 · SALÓN EN VIVO POR LA RED · hallv ——————————————————————————— */
console.log('5 · SALÓN EN VIVO · evento fiable hallv (host→invitado)');
chk(c09.includes("case 'pause': case 'resume': case 'mend': case 'v2off': case 'hallv':"),
  'c09: hallv en la lista de eventos FIABLES (_onRel)');
chk(c09.includes("case 'hallv': {") && c09.includes('this.game?.onPeerHallVar?.(m.v);'),
  'c09: despacho hallv → game.onPeerHallVar');
chk(c12.includes("this.net.sendRel({ k: 'hallv', v: hv.id });"),
  'c12: el anfitrión anuncia el salón nuevo EN VIVO (sendRel fiable)');
chk(c12.includes('this.net && this.net.online && this.net.role === \'host\'') &&
    c12.includes("k: 'hallv'"),
  'c12: sólo el anfitrión publica hallv');
chk(c12.includes('onPeerHallVar(id) {'), 'c12: onPeerHallVar (re-viste estancia/cancha + pista)');
chk(c12.includes("if (hv.id !== limpio) return;           // …un id que no existe NO viste"),
  'c12: id desconocido NO viste (saneo estricto, sin caer a museo por accidente)');
chk(c12.includes('try { this._hallMusicaPartidoAplicar(); } catch (eHM9) { /* */ }'),
  'c12: hp recibido con el invitado EN LA CANCHA re-arma la pista (onPeerHall)');

/* — 6 · GARANTÍA · física byte-exacto ————————————————————————————— */
console.log('6 · GARANTÍA · física c04/c05 INTACTA (byte-exacto r26b)');
chk(sha256('src/game/core/c04_fisica_ccd.js').startsWith('df8f71a3'),
  'c04_fisica_ccd.js byte-exacto (df8f71a3…)');
chk(sha256('src/game/core/c05_colisiones_ia_golpeo.js').startsWith('8bb62082'),
  'c05_colisiones_ia_golpeo.js byte-exacto (8bb62082…)');

/* — resumen ———————————————————————————————————————————————————————— */
console.log(`\nRESULTADO: ${ok} ✓ · ${fails} ✗`);
process.exit(fails ? 1 : 0);
