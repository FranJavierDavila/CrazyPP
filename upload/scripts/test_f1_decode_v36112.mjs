#!/usr/bin/env node
/* CRAZY PING PONG · r123 · TESTS F1 — ENDURECIMIENTO DEL DECODIFICADOR FAST.
 * Ejecuta la FUENTE REAL (src/game/core/c09b_red_nucleo.js) y verifica el
 * hardening del canal fast sin visor y sin red:
 *
 *   1 · paquete honesto con 8 eventos (MAX_EVENTS) sigue decodificando 8
 *   2 · paquete hostil que declara 16 eventos sólo entrega 8 (cap spec §5)
 *   3 · paquete MALFORMADO (nEvs > bytes reales) no debe escapar del
 *       patrón de escudo del llamador (_onFast: try/catch → descartar)
 *   4 · cabecera truncada (< 21 B) → null (guard pre-existente, regresión)
 *   5 · PROTO distinto → null (guard HELLO, regresión)
 *   6 · roundtrip de un HIT válido intacto (el camino honesto no se toca)
 *
 * Uso: node --no-warnings scripts/test_f1_decode_v36112.mjs
 */
import { PPNET } from '../src/game/core/c09b_red_nucleo.js';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};

const P = PPNET;
const VP = P.VP;

/* — helpers de construcción ——————————————————————————————————————— */
/** cabecera fast de 21 B con ver/flags/nEvs dados */
function cabecera(nEvs, flags) {
  const buf = new ArrayBuffer(21);
  const dv = new DataView(buf);
  dv.setUint8(0, ((VP.PROTO & 15) << 4) | (flags & 15));
  dv.setUint16(1, 7, true);            // seq
  dv.setUint16(3, 0, true);            // ack
  dv.setUint32(5, 0, true);            // ackBits
  dv.setUint32(9, 1000, true);         // sendTime
  dv.setUint32(13, 0, true);           // echoTime
  dv.setUint16(17, 0, true);           // echoDelay
  dv.setUint16(19, nEvs, true);        // nEvs
  return buf;
}
/** HIT de 46 B (kind,shot,tHit,p,v,s) — el más grande de los eventos */
function hit(id) {
  const buf = new ArrayBuffer(46);
  const dv = new DataView(buf);
  let n = 0;
  dv.setUint8(n, VP.EV.HIT); n += 1;
  dv.setUint16(n, id, true); n += 2;
  dv.setUint8(n, 0); n += 1;           // kind
  dv.setUint16(n, id, true); n += 2;   // shot
  dv.setUint32(n, 1500 + id, true); n += 4;  // tHit
  for (let i = 0; i < 9; i++) { dv.setFloat32(n, 0.5 + i * 0.01, true); n += 4; }
  return buf;
}
/** concatena cabecera + eventos; si `cortar` > 0, trunca ahí */
function paquete(nEvsDeclarados, nEventosReales, cortar) {
  const partes = [cabecera(nEvsDeclarados, 2)];   // F_EV
  for (let i = 0; i < nEventosReales; i++) partes.push(hit(i + 1));
  let total = partes.reduce((a, b) => a + b.byteLength, 0);
  if (cortar > 0) total = Math.min(total, 21 + cortar);
  const out = new Uint8Array(total);
  let off = 0;
  for (const p of partes) {
    if (off + p.byteLength > total) {
      out.set(new Uint8Array(p, 0, total - off), off);
      break;
    }
    out.set(new Uint8Array(p), off);
    off += p.byteLength;
  }
  return out.buffer;
}
/** escudo del llamador (réplica EXACTA del patrón de _onFast en c09) */
function decodificarConEscudo(buf) {
  try { return P.decodePacket(buf, {}); } catch (_e) { return null; }
}

/* — 1 · honesto: 8 eventos (máximo del protocolo) ————————————————— */
{
  const buf = paquete(8, 8, 0);
  const pkt = decodificarConEscudo(buf);
  chk(!!pkt && pkt.evs.length === 8, 'honesto: paquete con 8 eventos (MAX_EVENTS) decodifica 8');
}

/* — 2 · hostil: declara 16, sólo se aceptan 8 ————————————————————— */
{
  const buf = paquete(16, 16, 0);
  let pkt = null, lanzo = false;
  try { pkt = P.decodePacket(buf, {}); } catch (_e) { lanzo = true; }
  chk(!lanzo && !!pkt && pkt.evs.length === VP.MAX_EVENTS,
    'hostil: paquete que declara 16 eventos entrega exactamente MAX_EVENTS (8) sin lanzar');
}

/* — 3 · malformado: nEvs > bytes reales → el escudo lo descarta ———— */
{
  const buf = paquete(8, 8, 46);            // bytes para sólo 1 evento
  let sinEscudo = 'sin-lanzar';
  try { P.decodePacket(buf, {}); } catch (_e) { sinEscudo = 'lanza'; }
  const conEscudo = decodificarConEscudo(buf);
  chk(sinEscudo === 'lanza' && conEscudo === null,
    'malformado: decodificador lanza y el escudo del llamador lo convierte en descarte (null)');
}

/* — 4 · cabecera truncada → null (regresión del guard pre-existente) */
{
  const corto = new ArrayBuffer(VP.HDR - 1);
  let r = null;
  try { r = P.decodePacket(corto, {}); } catch (_e) { r = 'lanza'; }
  chk(r === null, 'regresión: buffer < HDR devuelve null (no lanza)');
}

/* — 5 · PROTO distinto → null (regresión del guard HELLO) —————————— */
{
  const buf = new ArrayBuffer(21);
  const dv = new DataView(buf);
  dv.setUint8(0, (((VP.PROTO + 1) & 15) << 4) | 2);
  dv.setUint16(19, 1, true);
  let r = null;
  try { r = P.decodePacket(buf, {}); } catch (_e) { r = 'lanza'; }
  chk(r === null, 'regresión: PROTO distinto devuelve null (no lanza)');
}

/* — 6 · roundtrip honesto intacto: encode → decode de un HIT ——————— */
{
  const buf = new ArrayBuffer(256);
  const pkt = {
    seq: 42, ack: 7, ackBits: 0x3, sendTime: 5000, echoTime: 4980, echoDelay: 12,
    evs: [{ t: VP.EV.HIT, id: 9, kind: 0, shot: 3, tHit: 5555,
      p: [0.1, 0.9, -1.2], v: [1.5, 2.5, -3.5], s: [0, 8, 0] }],
  };
  const n = P.encodePacket(buf, pkt);
  const out = decodificarConEscudo(buf.slice(0, n));
  const ev = out && out.evs && out.evs[0];
  chk(n > 0 && !!ev && ev.t === VP.EV.HIT && ev.id === 9 && ev.shot === 3 && ev.tHit === 5555
    && Math.abs(ev.v[2] - (-3.5)) < 1e-5,
    'roundtrip: HIT honesto (id/shot/tHit/vel) intacto tras el hardening');
}

console.log(`\nF1 · ${ok}✓ / ${fails}✗`);
process.exit(fails ? 1 : 0);
