#!/usr/bin/env node
/**
 * CRAZY PING PONG · HOST SIMULADO para QA de la TV en vivo.
 * Publica un canal 'demo-qa' y emite un rally sintético a 30 Hz
 * con eventos (hit/bounce/point/serve) — permite probar el espectador
 * sin una Quest. Uso: node scripts/mock_host.mjs [duracion_seg]
 */
import { io } from '/home/z/my-project/mini-services/live-service/node_modules/socket.io-client/build/esm/index.js';


const PORT = process.env.LIVE_PORT || 3004;
const DUR = parseInt(process.argv[2] || '0', 10) || Infinity;
const socket = io(`http://localhost:${PORT}`, { path: '/live/socket.io', transports: ['websocket'] });

const MATCH = 'demo-qa';
const T0 = Date.now();
let seq = 0, score = [0, 0], serving = 0, rally = 0, lastHit = 0;

// Trayectoria sintética: parábolas entre pala A y pala B con botes reales
function syntheticState(t) {
  const period = 1.7;                       // seg por golpe
  const k = Math.floor(t / period);
  const a = (t % period) / period;          // 0..1 dentro del golpe
  const fromLeft = k % 2 === 0;
  const x0 = fromLeft ? -0.45 : 0.4, x1 = fromLeft ? 0.35 : -0.42;
  const z0 = fromLeft ? 1.45 : -1.45, z1 = fromLeft ? -1.45 : 1.45;
  const apex = 1.35 + 0.18 * Math.sin(k * 2.7);
  const x = x0 + (x1 - x0) * a;
  const z = z0 + (z1 - z0) * a;
  const y = 0.8 + 4 * (apex - 0.8) * a * (1 - a);   // parábola
  const vx = (x1 - x0) / period, vz = (z1 - z0) / period;
  const vy = (4 * (apex - 0.8) * (1 - 2 * a)) / period;
  // palas: siguen la bola con retardo
  const px = fromLeft ? x0 : x1, pz = fromLeft ? z0 : z1;
  const sw = Math.max(0, Math.sin(t * 9)) * 0.18;
  const q = [0.05 * Math.sin(t), 0.7 * (fromLeft ? 1 : -1), 0, 0.7];
  return {
    seq: seq++,
    ball: { p: [x, y, z], v: [vx, vy, vz] },
    p1: { p: [px, 1.0, pz + (fromLeft ? sw : -sw)], q },
    p2: { p: [-px, 1.0, -pz], q: [0, -q[1], 0, q[3]] },
    score: [...score], serving, rally, state: 'rally',
  };
}

socket.on('connect', () => {
  console.log('[mock-host] conectado', socket.id);
  socket.emit('publish', {
    matchId: MATCH,
    meta: { name: 'DEMO · Rally sintético (QA)', p1: 'Host Demo', p2: 'CPU QA', mode: 'match' },
  });
});

socket.on('connect_error', (e) => { console.error('[mock-host] error', e.message); process.exit(1); });

const freq = 33; const t0 = Date.now();
let nextPointAt = t0 + 9000;
const timer = setInterval(() => {
  const now = Date.now();
  const t = (now - t0) / 1000;
  if (now - t0 > DUR * 1000) { console.log('[mock-host] fin'); socket.emit('unpublish'); process.exit(0); }
  socket.emit('state', MATCH, syntheticState(t));
  // eventos sintéticos
  if (now - lastHit > 1700) { lastHit = now; rally++; socket.emit('event', MATCH, { type: 'hit', side: rally % 2 ? 1 : 2, speedKmh: 38 + Math.round(Math.random() * 40) }); socket.emit('event', MATCH, { type: 'bounce', side: 'table' }); }
  if (now > nextPointAt) {
    nextPointAt = now + 9000 + Math.random() * 3000;
    const scorer = Math.random() > 0.5 ? 1 : 2;
    score[scorer - 1]++; rally = 0; serving = 1 - serving;
    socket.emit('event', MATCH, { type: 'point', scorer, score: [...score] });
    console.log('[mock-host] punto para', scorer, '→', score.join('-'));
    // el demo NO termina nunca (canal estable para QA); reinicia el marcador a 11
    if (score[0] >= 11 || score[1] >= 11) score = [0, 0];
  }
}, freq);
process.on('SIGINT', () => { socket.emit('unpublish'); process.exit(0); });
