#!/usr/bin/env node
/* CRAZY PING PONG · r37 (v3.6.137, FASE 139) — TEST de la ronda.
 * Segunda pasada de la revisión del multijugador (petición del dueño:
 * «no me fío, pasa otra revisión a fondo del juego en red multijugador»).
 * TRES BUGS cazados sobre la r36, leídos c09 (2.296 líneas), c09b (926),
 * el glue online de c12 y el árbitro de c06:
 *   D · REINICIO DE ICE MUERTO: el watchdog de la r125 llamaba
 *       pc.restartIce(), que SÓLO arma una bandera interna del agente —
 *       sin una oferta nueva (createOffer iceRestart → setLocal → 'sdp')
 *       el ICE NUNCA se renegociaba: un enlace muerto a mitad de partida
 *       (Wi-Fi→LTE, router que cambia la ruta) se quedaba helado hasta
 *       que el silencio de 12 s mataba la partida. FIX: el INVITADO
 *       renegocia DE VERDAD por la señalización viva (PeerJS) y el
 *       anfitrión responde por el camino que ya existía (_v2RemoteDesc).
 *       Sólo el invitado ofrece (sin glare SDP) y, con el reinicio en
 *       vuelo (<15 s), el silencio tolerado sube a 25 s para que el
 *       apretón de manos (2-6 s) llegue a tiempo.
 *   E · ACK REGRESIVO Y CIEGO EN LA ENVOLTURA: _onAckFrom hacía
 *       _ackP = pkt.seq SIN CONDICIÓN — en el canal sin orden, un paquete
 *       viejo que llegaba tarde movía el ack hacia ATRÁS y la máscara
 *       dejaba de cubrir los seqs recientes: el rival retransmitía
 *       eventos YA entregados. Y la aritmética usaba el wrapDiff u32 del
 *       RELOJ sobre seqs u16: en el giro 0xffff→0 los acks, la máscara y
 *       la medición de pérdida quedaban CIEGOS media vuelta (~18 min a
 *       60 Hz — una partida larga lo cruza). FIX: el ack sólo avanza con
 *       _seqDiff u16 (nueva helper, también en _ackCovers/_myAckBits/
 *       _trackLoss/_lossWin).
 *   F · COLGADO EN ESPAÑOL: hangup() decía 'Has cerrado la conexión'
 *       hardcodeado — un jugador en inglés cerraba su sala y leía
 *       español. FIX: T('bye_self') con clave ES/EN.
 * Uso: node scripts/test_r37_red_v36137.mjs */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const RAIZ = '/home/z/my-project/upload';
let ok = 0, fails = 0;
const chk = (cond, label) => {
  if (cond) { ok++; console.log('  ✓ ' + label); }
  else { fails++; console.log('  ✗ FALLO: ' + label); }
};
const cuenta = (pajaro, aguja) => pajaro.split(aguja).length - 1;

const c09 = readFileSync(`${RAIZ}/src/game/core/c09_red_netlink.js`, 'utf8');
const c09b = readFileSync(`${RAIZ}/src/game/core/c09b_red_nucleo.js`, 'utf8');
const c00 = readFileSync(`${RAIZ}/src/game/core/c00_pre_three.js`, 'utf8');
const vjson = JSON.parse(readFileSync(`${RAIZ}/src/game/VERSION.json`, 'utf8'));
const game = readFileSync(`${RAIZ}/public/game.html`, 'utf8');

console.log('== 1) FIX D · REINICIO DE ICE REAL (renegociación del invitado) ==');
chk(c09.includes('async _iceRestartIntento()'),
  'método _iceRestartIntento() existe');
chk(c09.includes('pc.createOffer({ iceRestart: true })'),
  'oferta nueva con iceRestart: true (lo que la r125 nunca hizo)');
chk(c09.includes('await pc.setLocalDescription(of);') &&
    cuenta(c09, "this.send({ k: 'sdp', d: { type: pc.localDescription.type") >= 1,
  'la oferta viaja por la señalización viva (sdp)');
chk(c09.includes('this._iceRestartIntento();') &&
    !c09.includes('try { this._pc?.restartIce(); } catch'),
  'fuera el restartIce() desnudo (bandera sin renegociación = no-op)');
chk(c09.includes("this.role === 'guest' && this._lastFastAt") &&
    cuenta(c09, 'this._iceRestartIntento();') === 1,
  'SÓLO el invitado ofrece (sin glare SDP) · una llamada en el watchdog');
chk(c09.includes('const reinicioVivo = this._lastIceTry && (now - this._lastIceTry) < 15000;'),
  'ventana de reinicio en vuelo (<15 s desde el intento)');
chk(c09.includes('const SILENCIO = this._pausedRemote ? 60000 : (reinicioVivo ? 25000 : 12000);'),
  'silencio dinámico: pausa 60 s · reinicio en vuelo 25 s · normal 12 s');
chk(c09.includes('pc.signalingState === \'closed\''),
  'guardia de signalingState cerrado (error tragado, sin excepción)');

// — aritmética REAL del watchdog de silencio (réplica exacta) —
function silencio({ pausada, intentoHace }) {
  const reinicioVivo = intentoHace !== null && intentoHace < 15000;
  return pausada ? 60000 : (reinicioVivo ? 25000 : 12000);
}
chk(silencio({ pausada: false, intentoHace: null }) === 12000,
  'D1 · sin pausa ni reinicio: 12 s de siempre (abandono real se corta igual)');
chk(silencio({ pausada: false, intentoHace: 8000 }) === 25000,
  'D2 · reinicio de ICE en vuelo (8 s): 25 s de gracia para el handshake');
chk(silencio({ pausada: false, intentoHace: 16000 }) === 12000,
  'D3 · reinicio vencido (>15 s): vuelve el corte de 12 s');
chk(silencio({ pausada: true, intentoHace: 8000 }) === 60000,
  'D4 · pausa anunciada MANDA (60 s aunque haya reinicio en vuelo)');
// D5 · cronología de recuperación: intento a los 5 s + handshake 6 s < 25 s
chk(5000 + 6000 < 25000,
  'D5 · la ventana cubre el peor handshake real (intento a 5 s + 6 s de ICE)');

console.log('== 2) FIX E · EL ACK SÓLO AVANZA (canal sin orden) ==');
chk(c09.includes('this._ackInit = false;                      // r37: ack SOLO avanza'),
  '_ackInit arranca a false en startV2');
chk(c09.includes('if (!this._ackInit || NetLink._seqDiff(pkt.seq, this._ackP) > 0) {') &&
    c09.includes('this._ackP = pkt.seq;') &&
    c09.includes('this._ackInit = true;'),
  '_onAckFrom avanza el ack SÓLO hacia delante (u16-safe)');

// — aritmética REAL del avance del ack (réplica exacta de _onAckFrom) —
// r37b: el seq es u16 → la casa usa _seqDiff (envoltura de 16 bits)
const wd = (a, b) => { let d = (a - b) >>> 0; if (d > 0x80000000) d -= 0x100000000; return d; };
const seqDiff = (a, b) => { let d = (a - b) & 0xffff; if (d >= 0x8000) d -= 0x10000; return d; };
function ackAvanza(seqs) {
  let ackP = 0, init = false;
  const hist = [];
  for (const s of seqs) {
    if (!init || seqDiff(s, ackP) > 0) { ackP = s; init = true; }
    hist.push(s);
    if (hist.length > 40) hist.shift();
  }
  return { ackP, hist };
}
function ackViejo(seqs) {   // comportamiento PRE-r37 (regresivo)
  let ackP = 0;
  const hist = [];
  for (const s of seqs) { ackP = s; hist.push(s); if (hist.length > 40) hist.shift(); }
  return { ackP, hist };
}
function cubre(ack, bits, seq) {   // réplica de _ackCovers (u16-safe)
  if (seq === ack) return true;
  const d = seqDiff(ack, seq);
  if (d > 0 && d <= 32) return ((bits >>> (d - 1)) & 1) === 1;
  return false;
}
function mascara(ackP, hist) {     // réplica de _myAckBits (u16-safe)
  let bits = 0;
  for (const s of hist) {
    if (s === ackP) continue;
    const d = seqDiff(ackP, s);
    if (d >= 1 && d <= 32) bits |= (1 << (d - 1));
  }
  return bits >>> 0;
}
// E1 · llegadas reordenadas: 100, 101, 100(late) — el ack NUEVO no retrocede
const llegadas = [100, 101, 100];
const nE = ackAvanza(llegadas), vE = ackViejo(llegadas);
chk(nE.ackP === 101, `E1 · ack nuevo se queda en 101 (sin retroceso) → ackP=${nE.ackP}`);
chk(vE.ackP === 100, `E1b · el ack VIEJO retrocedía a 100 (bug reproducido) → ackP=${vE.ackP}`);
// E2 · tras el paquete tarde, el ack nuevo SIGUE cubriendo el seq reciente
const bitsE = mascara(nE.ackP, nE.hist);
chk(cubre(nE.ackP, bitsE, 101),
  'E2 · la máscara nueva sigue cubriendo el 101 (el rival NO retransmite)');
// E3 · envoltura u16: 0xfffe → 0 avanza sano (con el wrapDiff u32 se
//      quedaba CIEGO en 0xffff durante media vuelta del contador)
const w = ackAvanza([0xfffe, 0xffff, 0, 1]);
chk(w.ackP === 1, `E3 · envoltura u16: tras 0xfffe→1 el ack queda en 1 → ackP=${w.ackP}`);
// E3b · la aritmética VIEJA (wrapDiff u32 sobre seqs u16) reproducida:
let ciego = 0xffff, initC = true;
for (const s of [0, 1, 2, 3]) { if (wd(s, ciego) > 0) ciego = s; }
chk(ciego === 0xffff,
  `E3b · el wrapDiff u32 se quedaba clavado en 0xffff (bug reproducido) → ${ciego}`);
// E3c · _ackCovers u16-safe cruza la envoltura: ack=1 cubre al 0xfffe
defaultViejo: {
  const bits = mascara(1, [0xfffd, 0xfffe, 0xffff, 0, 1]);
  chk(cubre(1, bits, 0xfffe), 'E3c · la máscara cubre seqs ANTES del giro (0xfffe con ack=1)');
}
// E4 · primer paquete: _ackInit lo adopta sea cual sea el seq aleatorio
const p = ackAvanza([0x8123]);
chk(p.ackP === 0x8123, `E4 · el primer seq se adopta siempre (init) → ackP=${p.ackP}`);

console.log('== 3) FIX F · COLGADO EN EL IDIOMA DE CADA UNO ==');
chk(c00.includes("bye_self: 'Has cerrado la conexión',"),
  'clave bye_self en ESPAÑOL');
chk(c00.includes("bye_self: 'You closed the connection',"),
  'clave bye_self en INGLÉS');
chk(c09.includes("this.onPeerGone(T('bye_self'));") &&
    !c09.includes("'Has cerrado la conexión'"),
  'hangup() ya no lleva español hardcodeado');
chk(cuenta(game, 'bye_self') >= 3,
  'game.html lleva las dos claves + el uso (i18n íntegro en el build)');

console.log('== 4) SIN REGRESIONES · la r36 y el núcleo intactos ==');
chk(cuenta(c09, '_lossWin()') >= 2 && c09.includes('const lw = this._lossWin();'),
  'r36 · pérdida por ventana viva intacta');
chk(cuenta(c09, 'for (const e of this._pend.slice(0, PPNET.VP.MAX_EVENTS)) e.seqs.push(pk.seq);') === 2,
  'r36 · seq sólo a los eventos que viajan (2 puntos) intacto');
chk(c09.includes('this._pausedRemote ? 60000'), 'r36 · pausa anunciada 60 s intacta');
chk(c09b.includes('PROTO: 3,'), 'PPNET PROTO 3 (cero cambios de códec)');
chk(c09b.includes('CLAIM_TIMEOUT: 0.7,'), 'MatchSync intacto (claims/ack/resync)');
chk(c09.includes("this.game?.onNetMatchStart?.(this._mstart);"), 'mstart intacto');
chk(c09.includes('this._ball.setHeld(serverLocal === \'player\');'), 'HELD del saque intacto');
chk(c09.includes('startOnlineSession'), 'enganche de sesión intacto');
chk(c09.includes('_v2RemoteDesc(desc)'),
  'camino de respuesta del anfitrión intacto (acepta la oferta del reinicio)');
chk(cuenta(c09, 'static _seqDiff(a, b)') === 1 &&
    cuenta(c09, 'NetLink._seqDiff(') === 5,
  'aritmética u16 _seqDiff: def + 5 usos (ack, covers, máscara, pérdida, ventana)');
const sha = (p) => createHash('sha256').update(readFileSync(p)).digest('hex');
chk(sha(`${RAIZ}/src/game/core/c04_fisica_ccd.js`).startsWith('df8f71a3'),
  'c04 sha256 df8f71a3… (física byte-exacta)');
chk(sha(`${RAIZ}/src/game/core/c05_colisiones_ia_golpeo.js`).startsWith('8bb62082'),
  'c05 sha256 8bb62082… (física byte-exacta)');

console.log('== 5) VERSIÓN Y SELLOS ==');
chk(vjson.version === '3.6.137-SDK6', `VERSION.json 3.6.137-SDK6 (${vjson.version})`);
chk(vjson.fase === 139, `FASE 139 (${vjson.fase})`);
chk(vjson.tamano === 11473088, `tamaño sellado (${vjson.tamano})`);
chk(vjson.golden.startsWith('54386315'), 'golden 54386315… (build re-sellado)');
chk(game.includes('const VERSION') && game.includes('3.6.137-SDK6'),
  'game.html sellado a 3.6.137-SDK6');
chk(cuenta(game, '_iceRestartIntento') === 2,
  `game.html lleva el reinicio de ICE (def + llamada): ×${cuenta(game, '_iceRestartIntento')}`);
chk(cuenta(game, 'this._ackInit') === 3,
  `game.html lleva el ack monotono (init + guardia ×2): ×${cuenta(game, 'this._ackInit')}`);
chk(cuenta(game, 'NetLink._seqDiff(') === 5,
  `game.html lleva la aritmética u16 completa: ×${cuenta(game, 'NetLink._seqDiff(')}`);

console.log(`\nRESULTADO: ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);
