#!/usr/bin/env node
/* Sonda de protocolo PeerJS · descubre el contrato EXACTO del PeerServer
 * real (npm «peer») para el arnés vivo de r146: URL de upgrade, OPEN,
 * relay de OFFER/ANSWER y los errores ID-TAKEN / peer-unavailable. */
import http from 'node:http';
import { createRequire } from 'node:module';
import { WebSocket as WS } from 'ws';

const require_ = createRequire(import.meta.url);
const { PeerServer } = require_('/home/z/my-project/node_modules/peer/dist/index.cjs');
const srv = PeerServer({ port: 3005, path: '/' });
await new Promise((r) => setTimeout(r, 300));

const log = (tag, m = '') => console.log(tag, JSON.stringify(m) === undefined ? String(m) : JSON.stringify(m).slice(0, 220));

function cliente(nombre, id) {
  return new Promise((res) => {
    const url = id
      ? `ws://127.0.0.1:3005/peerjs?id=${id}&token=tok-${nombre}&key=peerjs`
      : `ws://127.0.0.1:3005/peerjs?token=tok-${nombre}&key=peerjs`;
    const ws = new WS(url);
    const out = { nombre, ws, mensajes: [] };
    ws.on('open', () => {
      log(`[${nombre}] ws OPEN`);
      ws.send(JSON.stringify({ type: 'OPEN', payload: { token: `tok-${nombre}` } }));
    });
    ws.on('message', (d) => {
      let m = null;
      try { m = JSON.parse(d.toString()); } catch { m = { tipo: 'no-json', crudo: d.toString().slice(0, 60) }; }
      out.mensajes.push(m);
      log(`[${nombre}] <-`, m);
      if (m.type === 'OPEN') out.id = (m.payload && m.payload.id) || id || out.id;
      res(out);
    });
    ws.on('error', (e) => { log(`[${nombre}] WS ERR`, { msg: e.message }); res(out); });
    ws.on('close', (c) => { log(`[${nombre}] WS CLOSE`, { code: c }); });
    return out;
  });
}

// 1 · cliente con id fijo (anfitrión de sala pp-SONDA)
const A = await cliente('A', 'ppxr3-SONDA');
// 2 · cliente con id TOMADO (debe recibir ID-TAKEN)
const B = await cliente('B', 'ppxr3-SONDA');
// 3 · cliente sin id (el broker asigna)
const C = await cliente('C', 'pp-auto-C1');
// 4 · OFFER de C a A (debe relayarse a A con src=C)
C.ws.send(JSON.stringify({ type: 'OFFER', dst: 'ppxr3-SONDA',
  payload: { connectionId: 'conn-x', sdp: 'v=0…' } }));
await new Promise((r) => setTimeout(r, 400));
// 5 · OFFER de C a un id MUERTO (debe volver peer-unavailable a C)
C.ws.send(JSON.stringify({ type: 'OFFER', dst: 'ppxr3-MUERTO',
  payload: { connectionId: 'conn-y', sdp: 'v=0…' } }));
await new Promise((r) => setTimeout(r, 400));
// 6 · ANSWER de A a C (relay inverso)
A.ws.send(JSON.stringify({ type: 'ANSWER', dst: C.id,
  payload: { connectionId: 'conn-x', sdp: 'v=0…' } }));
await new Promise((r) => setTimeout(r, 400));
console.log('A.mensajes:', A.mensajes.map((m) => m.type).join(','));
console.log('B.mensajes:', B.mensajes.map((m) => m.type).join(','));
console.log('C.mensajes:', C.mensajes.map((m) => m.type).join(','));
process.exit(0);
