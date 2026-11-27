/* r132 · 10ª — prueba del codificador ante pose NaN (sospecha #14:
   encodePacket devuelve 0 → el emisor enmudece y el watchdog mata). */
import { PPNET as PP } from '../src/game/core/c09b_red_nucleo.js';

const buf = new ArrayBuffer(1200);
const base = { seq: 1, ack: 0, ackBits: 0, sendTime: 123, echoTime: 0, echoDelay: 0,
  evs: null, yAnchor: 1 };
const sana = { ...base, pose: { hp: [1, 2, 3], hq: [0, 0, 0, 1], lp: [0, 0, 0],
  lq: [0, 0, 0, 1], rp: [0, 0, 0], rq: [0, 0, 0, 1], fl: 0 } };
const nan = { ...sana, pose: { ...sana.pose, hq: [NaN, 0, 0, 1] } };

try {
  const nOk = PP.encodePacket(buf, sana);
  const nNan = PP.encodePacket(buf, nan);
  console.log('pose sana  → encodePacket:', nOk);
  console.log('pose NaN   → encodePacket:', nNan,
    nNan === 0 ? '← SILENCIO CONFIRMADO (mechanism #14)' : '→ se envía igual');
} catch (e) {
  console.log('encodePacket LANZÓ con pose NaN:', e.message, '— el try de _sendFast no existe: ¿crash?');
}
