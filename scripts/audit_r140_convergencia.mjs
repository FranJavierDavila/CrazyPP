/* Verificación read-only de los fixes r140 (auditoría de convergencia).
 * 1) matchSync.onClaim: guardia monótona — no regresa el libro.
 * 2) claimPlausible: ¿acepta rallyId FRACCIONARIO (mint de puntos)?
 * 3) Rules.forcePoint: ¿falla cerrado con rallyId no finito y aplica fracción?
 * 4) decodePacket: NaN en eventos de HIT rechaza el paquete entero.
 * No modifica ficheros del juego. */
import { PPNET } from '../src/game/core/c09b_red_nucleo.js';

/* stubs mínimos de navegador: c06 arrastra c00 (window/document/localStorage) */
globalThis.window = globalThis;
globalThis.T = (k) => k;   // c06 llama a T() como global (bundle concatenado)
globalThis.document = { createElement: () => ({ style: {} }), addEventListener: () => {}, body: { appendChild: () => {} } };
globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
try { globalThis.navigator = { userAgent: 'node-audit' }; } catch { /* getter-only en Node 24 */ }
const { Rules } = await import('../src/game/core/c06_logros_stats_ia_rival.js');

let ok = 0, fail = 0;
const chk = (cond, msg) => {
  if (cond) { ok++; console.log('  ✓ ' + msg); }
  else { fail++; console.log('  ✗ FALLO: ' + msg); }
};

console.log('--- 1) MatchSync.onClaim guardia monótona ---');
const s = new PPNET.MatchSync('guest');
let r = s.onClaim({ r: 5, w: 'player' }, 'ai');
chk(r.apply === true && s.applied === 5, 'claim r=5 nuevo → aplicado, applied=5');
r = s.onClaim({ r: 3, w: 'player' }, 'ai');           // atrasado
chk(r.apply === false && s.applied === 5, 'claim r=3 (<applied) → NO aplica, libro NO regresa (applied sigue 5)');
r = s.onClaim({ r: 'x', w: 'player' }, 'ai');
chk(r.apply === false && r.ack.r === -1, 'claim r="x" (no numérico) → no aplica, ack r=-1');
r = s.onClaim({ r: NaN, w: 'ai' }, 'ai');
chk(r.apply === false, 'claim r=NaN → no aplica');
r = s.onClaim({ r: 5, w: 'ai' }, 'ai');               // duplicado exacto
chk(r.apply === false, 'claim r=5 duplicado → no aplica');

console.log('--- 2) claimPlausible con rallyId FRACCIONARIO ---');
const T0 = 100000;
chk(PPNET.claimPlausible({ r: 2.5, w: 'player', c: 'out' }, 2, T0, 0) === true,
  'claimPlausible ACEPTA r=2.5 con applied=2 (mint fraccionario posible)');
chk(PPNET.claimPlausible({ r: 0.5, w: 'player', c: 'out' }, -1, T0, 0) === true,
  'claimPlausible ACEPTA r=0.5 con applied=-1');
let s2 = new PPNET.MatchSync('host');
let r2 = s2.onClaim({ r: 0.5, w: 'ai' }, 'player');
chk(r2.apply === true && s2.applied === 0.5, 'onClaim APLICA r=0.5 (applied=0.5 — libro contaminado)');

console.log('--- 3) Rules.forcePoint fail-closed / fracción ---');
const rules = new Rules();
rules.startMatch('match');
rules._netGuard = true;
const a0 = rules.forcePoint('player', 'out', NaN);
chk(a0.length === 0, 'forcePoint(NaN) → [] (fail-closed r140)');
const a1 = rules.forcePoint('player', 'out', undefined);
chk(a1.length === 0, 'forcePoint(undefined) → []');
const a2 = rules.forcePoint('player', 'out', '7');
chk(a2.length === 0, 'forcePoint("7" string) → []');
const a3 = rules.forcePoint('player', 'out', 0.5);
chk(a3.length === 1, 'forcePoint(0.5) → APLICA el intent (fracción pasa la guardia); marcador ' +
  rules.scorePlayer + '-' + rules.scoreAi);
const antes = rules.scorePlayer;
rules.beginServeRally('player');            // rallySeq=1
rules.applyPoint('player', 'out');          // _appliedRally=1
const dup = rules.applyPoint('player', 'out');
chk(dup.length === 0, 'applyPoint con rallySeq ya aplicado → [] (netGuard)');
rules.beginServeRally('player');            // rallySeq=2, _appliedRally=1
const a4 = rules.applyPoint('ai', 'out');   // _appliedRally=2
chk(a4.length === 1, 'rallySeq nuevo aplica (sanidad)');
// tras _appliedRally=2 un claim 0.5 ya no colisiona, pero 1.5/2.5 sí colisionan? no:
// 2.5 !== 2 → aplicaría TAMBIÉN sobre el rallye 2 ya resuelto localmente
const a5 = rules.forcePoint('player', 'out', 2.5);
chk(a5.length === 1, 'forcePoint(2.5) con _appliedRally=2 → APLICA DOBLE sobre el rallye 2');

console.log('--- 4) decodePacket NaN en HIT ---');
const buf = new ArrayBuffer(PPNET.VP.MAX_PKT);
const pk = {
  seq: 1, ack: 0, ackBits: 0, sendTime: 1000, echoTime: 0, echoDelay: 0,
  yAnchor: 0.76,
  pose: { hp: [0, 1, 0], hq: [0, 0, 0, 1], lp: [0, 1, 0], lq: [0, 0, 0, 1],
          rp: [0, 1, 0], rq: [0, 0, 0, 1], fl: 3 },
  evs: [{ t: PPNET.VP.EV.HIT, id: 1, kind: 0, shot: 1, tHit: 900,
          p: [0, 1, NaN], v: [1, 0, 0], s: [0, 0, 0] }],
};
const n = PPNET.encodePacket(buf, pk);
chk(n > 0, 'paquete con HIT NaN codifica (' + n + ' B)');
const out = { yAnchor: 0.76, evs: [] };
const dec = PPNET.decodePacket(buf.slice(0, n), out);
chk(dec === null, 'decodePacket → null (paquete entero rechazado por NaN en ev.p)');
// pose cuantizada inmune
const pk2 = { seq: 1, ack: 0, ackBits: 0, sendTime: 1000, echoTime: 0, echoDelay: 0,
  yAnchor: 0.76, evs: [],
  pose: { hp: [1.5, 1.2, -3.9], hq: [0, 0.7, 0, 0.7], lp: [0.2, 1, 0.1], lq: [0, 0, 0, 1],
          rp: [-0.2, 1, 0.1], rq: [0, 0, 0, 1], fl: 3 } };
const n2 = PPNET.encodePacket(buf, pk2);
const out2 = { yAnchor: 0.76, evs: [] };
const d2 = PPNET.decodePacket(buf.slice(0, n2), out2);
const finitos = d2 && d2.pose && [d2.pose.hp, d2.pose.hq, d2.pose.lp, d2.pose.lq,
  d2.pose.rp, d2.pose.rq].every((a) => a.every(Number.isFinite));
chk(finitos === true, 'pose cuantizada siempre finita tras decodificar');
// header echoDelay corrupto (undefined) → off NaN → _sample lo frena
const clk = new PPNET.NetClock(false);
clk.markSent(500);
clk.onPacket({ sendTime: 900, echoTime: 500, echoDelay: undefined, seq: 3 }, 1000);
chk(Number.isFinite(clk.offset), 'offset sigue finito tras echoDelay corrupto (guard _sample r140)');
const clk2 = new PPNET.NetClock(false);
let bad = 0;
for (let i = 0; i < 6; i++) bad += (clk2.anchor(0, 1e15, i + 1), 0);
chk(clk2.offset === 0 && clk2.coarse === false,
  '6 anchors basura (peer 1e15) NO tocan el reloj (anchor r140)');

console.log('RESULTADO: ' + ok + ' OK · ' + fail + ' FALLOS');
