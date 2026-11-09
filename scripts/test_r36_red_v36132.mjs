#!/usr/bin/env node
/* CRAZY PING PONG · r36 (v3.6.132, FASE 134) — TEST de la ronda.
 * Revisión del multijugador pedida por el dueño («revisa el funcionamiento
 * de las partidas multijugador por si cazas algún bug»). TRES BUGS cazados
 * en la auditoría completa de c09/c09b/c12:
 *   A · _trackLoss acumulativo de por vida: tras ~15 paquetes perdidos en
 *       TODA la sesión (o UN atasco de ICE ≥5 s = cientos de huecos) la
 *       pose caía a 30 Hz PARA SIEMPRE (recuperación exigía <4 % vital).
 *       FIX: ventana viva (span del anillo − recibidos) + los saltos >64
 *       son PARADAS, no pérdida.
 *   B · watchdog de 12 s mataba la partida con el rival EN PAUSA LEGAL
 *       (avisó 'pause', visor quitado). FIX: con pausa anunciada el
 *       silencio tolerado sube a 60 s.
 *   C · _sendFast/_flushEvents etiquetaban con el seq a TODOS los eventos
 *       pendientes (hasta 24) cuando el paquete sólo lleva los 8 primeros
 *       → un ack posterior daba por ENTREGADOS eventos jamás enviados
 *       (pérdida silenciosa de HIT/HANDOFF). FIX: seq sólo a los que
 *       viajan.
 * Uso: node scripts/test_r36_red_v36132.mjs */
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
const vjson = JSON.parse(readFileSync(`${RAIZ}/src/game/VERSION.json`, 'utf8'));
const game = readFileSync(`${RAIZ}/public/game.html`, 'utf8');

console.log('== 1) FIX A · PÉRDIDA POR VENTANA VIVA (no vitalicia) ==');
chk(c09.includes('if (d > 1 && d <= 64) this._gaps += d - 1;'),
  'hueco de pérdida acotado a 2..64 (>64 = PARADA, no pérdida)');
chk(!c09.includes('this._recvs = this._recvRing.length + this._gaps;'),
  'fuera la recalibración vitalicia (_recvs = anillo + gaps)');
chk(c09.includes('_lossWin() {'), 'helper de ventana _lossWin()');
chk(c09.includes('const span = PPNET.wrapDiff(ring[n - 1], ring[0]);') &&
    c09.includes('const g = Math.max(0, Math.min(this._gaps, span - (n - 1)));'),
  'ventana = span del anillo − recibidos (clamp ≥0 y al contado)');
chk(c09.includes('const lw = this._lossWin();') &&
    c09.includes('this._recvs = lw.n;'),
  '_trackLoss se alimenta de la ventana');
chk(!c09.includes('const loss = this._gaps / Math.max(1, this._gaps + this._recvs);'),
  'fuera el ratio de pérdida vitalicio');
chk(c09.includes('const lw = this._lossWin();   // r36 (v3.6.132): pérdida de la VENTANA') &&
    c09.includes('loss: Math.round((1 - lw.n / Math.max(1, lw.g + lw.n)) * 100),'),
  'netInfo() enseña la MISMA ventana (HUD/telemetría coherentes)');
chk(c09.includes('if (this._lossLowT > 90 && !this._degraded)') &&
    c09.includes('if (this._degraded && loss < 0.04)'),
  'umbrales spec §11 intactos (>10 % sostenido · recuperación <4 %)');

// — aritmética REAL del algoritmo (réplica exacta de _lossWin/_trackLoss) —
const wrapDiff = (a, b) => { let d = (a - b) >>> 0; if (d > 0x80000000) d -= 0x100000000; return d; };
function simular(seqs) {
  const ring = []; let gaps = 0; let degradado = false; let lowT = 0; let hz = 60;
  const lossWin = () => {
    const n = ring.length;
    if (n < 2) return { g: 0, n };
    const span = wrapDiff(ring[n - 1], ring[0]);
    return { g: Math.max(0, Math.min(gaps, span - (n - 1))), n };
  };
  for (const s of seqs) {
    const d = ring.length ? wrapDiff(s, ring[ring.length - 1]) : 0;
    if (d > 1 && d <= 64) gaps += d - 1;
    ring.push(s); if (ring.length > 128) ring.shift();
    const lw = lossWin();
    const loss = lw.g / Math.max(1, lw.g + lw.n);
    if (loss > 0.10) { lowT++; if (lowT > 90 && !degradado) { degradado = true; hz = 30; } }
    else { lowT = Math.max(0, lowT - 2); if (degradado && loss < 0.04) { degradado = false; hz = 60; } }
  }
  return { degradado, hz, gaps };
}
// A1 · atasco de ICE de 5 s (300 paquetes de salto): SIN degradación
const atasco = [];
for (let i = 1; i <= 300; i++) atasco.push(i);
atasco.push(600);   // el salto de la parada
for (let i = 601; i <= 900; i++) atasco.push(i);
const r1 = simular(atasco);
chk(!r1.degradado && r1.hz === 60,
  `A1 · atasco de 300 paquetes NO degrada (antes: 30 Hz para siempre) → hz=${r1.hz}`);
// A2 · pérdida REAL sostenida del 20 % durante 400 paquetes: DEGRADA…
// (el seq avanza SIEMPRE — se envía — y sólo se registra al recibir)
const rafaga = [];
let n = 0;
for (let i = 1; i <= 400; i++) { n++; if (i % 5 !== 0) rafaga.push(n); }   // 20 % perdidos
for (let i = 0; i < 200; i++) { n++; rafaga.push(n); }                     // …y luego limpia
const r2 = simular(rafaga);
chk(r2.hz === 60,
  `A2 · tras la ráfaga del 20 % la pose RECUPERA 60 Hz (antes imposible) → hz=${r2.hz}`);
// A2b · durante la ráfaga SÍ llegó a degradar (la ventana no es sorda)
const r2b = simular(rafaga.slice(0, 400));
chk(r2b.degradado, 'A2b · la ráfaga sostenida del 20 % SÍ degradó en su momento');
// A3 · pérdida crónica del 12,5 % (en el límite): degrada y MANTIENE
const cronica = []; n = 0;
for (let i = 1; i <= 600; i++) { n++; if (i % 8 !== 0) cronica.push(n); }   // 12,5 % perdidos
const r3 = simular(cronica);
chk(r3.degradado && r3.hz === 30,
  `A3 · pérdida crónica del 12,5 % mantiene la degradación honesta → hz=${r3.hz}`);

console.log('== 2) FIX B · PAUSA ANUNCIADA NO MUERE (60 s de gracia) ==');
chk(c09.includes('const SILENCIO = this._pausedRemote ? 60000 : 12000;'),
  'watchdog consciente de la pausa (60 s anunciada · 12 s sin pausa)');
chk(cuenta(c09, "now - this._lastRelAt > SILENCIO") === 1 &&
    cuenta(c09, "now - this._lastFastAt > SILENCIO") === 1,
  'ambos relojes (rel + fast) usan el mismo SILENCIO');

console.log('== 3) FIX C · SEQ SÓLO A LOS EVENTOS QUE VIAJAN ==');
chk(cuenta(c09, 'for (const e of this._pend.slice(0, PPNET.VP.MAX_EVENTS)) e.seqs.push(pk.seq);') === 2,
  'los DOS puntos de etiquetado (_sendFast + _flushEvents) corregidos');
chk(!c09.includes('for (const e of this._pend) e.seqs.push(pk.seq);'),
  'fuera el etiquetado en masa de los 24 pendientes');
chk(cuenta(c09, 'this._pend.slice(0, PPNET.VP.MAX_EVENTS).map((e) => e.ev)') === 2,
  'el paquete sigue llevando exactamente los 8 primeros (spec §5)');

console.log('== 4) SIN REGRESIONES · núcleo y juego intactos ==');
chk(c09b.includes('PROTO: 3,'), 'PPNET PROTO 3 (el cable no cambia: fixes locales)');
chk(c09.includes("this.game?.onNetMatchStart?.(this._mstart);"), 'mstart intacto');
chk(c09.includes("if (this.role === 'host') this._sendResync();"), 'resync del host intacto');
chk(c09.includes('this._ball.setHeld(serverLocal === \'player\');'), 'HELD del saque intacto');
chk(c09.includes('startOnlineSession'), 'enganche de sesión intacto');
const sha = (p) => createHash('sha256').update(readFileSync(p)).digest('hex');
chk(sha(`${RAIZ}/src/game/core/c04_fisica_ccd.js`).startsWith('df8f71a3'),
  'c04 sha256 df8f71a3… (física byte-exacta)');
chk(sha(`${RAIZ}/src/game/core/c05_colisiones_ia_golpeo.js`).startsWith('8bb62082'),
  'c05 sha256 8bb62082… (física byte-exacta)');

console.log('== 5) VERSIÓN Y SELLOS ==');
chk(vjson.version === '3.6.132-SDK6', `VERSION.json 3.6.132-SDK6 (${vjson.version})`);
chk(vjson.fase === 134, `FASE 134 (${vjson.fase})`);
chk(game.includes('const VERSION') && game.includes('3.6.132-SDK6'),
  'game.html sellado a 3.6.132-SDK6');
chk(cuenta(game, '_lossWin') === 3, `game.html: _lossWin (def + trackLoss + netInfo) ×3: ${cuenta(game, '_lossWin')}`);
chk(game.includes('const SILENCIO = this._pausedRemote ? 60000 : 12000;'),
  'game.html lleva el watchdog consciente de pausa');
chk(cuenta(game, 'this._pend.slice(0, PPNET.VP.MAX_EVENTS)) e.seqs.push(pk.seq);') === 2,
  'game.html lleva los dos etiquetados corregidos');

console.log(`\nRESULTADO: ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);
