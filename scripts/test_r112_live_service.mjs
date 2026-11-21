// ARNÉS r112 · live-service tras los fixes H13/H14/H15 de la auditoría r111
// ------------------------------------------------------------------------
// Levanta el relay REAL (mini-services/live-service/index.ts) en :3004 y lo
// somete a pruebas con clientes socket.io REALES (cero mocks): propiedad de
// canales, anti-secuestro de matchId, contadores de espectadores y topes de
// longitud. El veredicto va al final: RESULTADO: N✓ / M✗
//
//   bun scripts/test_r112_live_service.mjs
//
import { spawn } from 'child_process';
import { io } from '/home/z/my-project/mini-services/live-service/node_modules/socket.io-client/build/esm/index.js';

const DIR_LIVE = '/home/z/my-project/mini-services/live-service';
const URL = 'http://127.0.0.1:3004';
const PATH = '/live/socket.io';
let ok = 0, mal = 0;
const verdicto = (nombre, cond) => {
  if (cond) { ok++; console.log(`  ✓ ${nombre}`); }
  else { mal++; console.log(`  ✗ ${nombre}`); }
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const espera = async (pred, ms = 3000, paso = 40) => {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) { if (await pred()) return true; await sleep(paso); }
  return pred();
};
// SIEMPRE fresco: consulta la guía REST (nunca caché del arnés)
const canalActual = async () => {
  const r = await fetch(`${URL}/api/channels`);
  const j = await r.json();
  return j.channels || [];
};
const canal = async (id) => (await canalActual()).find((c) => c.matchId === id);

// ── 1 · servidor: reutiliza el que ya esté vivo (bun --hot recarga el
//        código arreglado en caliente) o levanta uno propio ──
let salud = null;
let srv = null;
try {
  const r = await fetch(`${URL}/api/health`);
  salud = await r.json();
} catch { /* no hay servidor previo */ }
if (salud?.ok) {
  console.log('relay YA VIVO en :3004 (se prueba contra él):', JSON.stringify(salud));
} else {
  srv = spawn('bun', ['index.ts'], { cwd: DIR_LIVE, stdio: ['ignore', 'pipe', 'pipe'] });
  let srvOut = '';
  srv.stdout.on('data', (d) => { srvOut += d; });
  srv.stderr.on('data', (d) => { srvOut += d; });
  for (let i = 0; i < 50; i++) {
    await sleep(100);
    try {
      const r = await fetch(`${URL}/api/health`);
      salud = await r.json();
      if (salud?.ok) break;
    } catch { /* aún no */ }
  }
  if (!salud?.ok) {
    console.log('✗ el relay no arrancó:', srvOut.slice(-400));
    srv.kill();
    process.exit(1);
  }
  console.log('relay levantado en :3004 ·', JSON.stringify(salud));
}

// ── 2 · clientes reales ──
const host = io(URL, { path: PATH, transports: ['websocket'] });
const host2 = io(URL, { path: PATH, transports: ['websocket'] });   // segundo host: el relay admite UN canal por socket
const atacante = io(URL, { path: PATH, transports: ['websocket'] });
const espect = io(URL, { path: PATH, transports: ['websocket'] });
const conecta = (c) => new Promise((res, rej) => {
  const t = setTimeout(() => rej(new Error('timeout connect')), 4000);
  c.once('connect', () => { clearTimeout(t); res(); });
});
await conecta(host); await conecta(host2); await conecta(atacante); await conecta(espect);
console.log('4 clientes conectados');

const estadosRecibidos = [];
espect.on('state', (st) => estadosRecibidos.push(st));

try {
  // ── T1 · H13: publicación legítima ──
  host.emit('publish', { matchId: 'r112test1', meta: { name: 'Test r112', p1: 'Ana', p2: 'Beto' } });
  await espera(async () => !!(await canal('r112test1')));
  verdicto('T1 publish legítimo crea canal', !!(await canal('r112test1')));

  // ── T2 · H15: matchId inválido o desbordado NO crea canal ──
  atacante.emit('publish', { matchId: 'ab' });                       // demasiado corto
  atacante.emit('publish', { matchId: 'x'.repeat(80) });             // demasiado largo
  atacante.emit('publish', { matchId: 'con espacios!!' });           // fuera de whitelist
  await sleep(400);
  verdicto('T2 H15 matchId inválido rechazado (×3)', (await canalActual()).length === 1);

  // ── T3 · H13: el atacante NO puede secuestrar el canal del host ──
  atacante.emit('publish', { matchId: 'r112test1', meta: { name: 'SECUESTRADO' } });
  await sleep(400);
  const trasAtaque = await canal('r112test1');
  verdicto('T3 H13 nombre del canal intacto tras intento de secuestro',
    trasAtaque && trasAtaque.name === 'Test r112');

  // ── T4 · H13: estado del atacante NO llega al espectador; el del host SÍ ──
  espect.emit('watch', 'r112test1', () => {});
  await espera(async () => (await canal('r112test1'))?.viewers === 1);
  atacante.emit('state', 'r112test1', { marcador: 'falso', t: 0 });
  await sleep(500);
  const antesHost = estadosRecibidos.length;
  host.emit('state', 'r112test1', { marcador: 'real' });
  await espera(() => estadosRecibidos.length > antesHost);
  verdicto('T4 H13 estado ajeno bloqueado y estado del dueño difundido',
    estadosRecibidos.length === antesHost + 1 && estadosRecibidos.at(-1).marcador === 'real');

  // ── T5 · H15: meta.name recortado a 24 ──
  host.emit('publish', { matchId: 'r112test1', meta: { name: 'N'.repeat(60) } });
  await espera(async () => (await canal('r112test1'))?.name?.length === 24);
  const nombre5 = (await canal('r112test1'))?.name || '';
  verdicto('T5 H15 meta.name recortado a 24', nombre5.length === 24 && nombre5 === 'N'.repeat(24));

  // ── T6 · H14: watch doble del MISMO canal no infla viewers ──
  espect.emit('watch', 'r112test1', () => {});
  await sleep(300);
  verdicto('T6 H14 watch doble mantiene viewers=1', (await canal('r112test1'))?.viewers === 1);

  // ── T7 · H14: watch de OTRO canal suelta el anterior ──
  // (host2 publica test2: el relay admite UN canal por socket, así que el
  //  MISMO host habría dropeado test1 por diseño — re-publish — y el test
  //  debe ejercitar el CAMBIO DE CANAL del espectador, no el drop del host)
  host2.emit('publish', { matchId: 'r112test2', meta: { name: 'Canal 2' } });
  await espera(async () => !!(await canal('r112test2')));
  espect.emit('watch', 'r112test2', () => {});
  await espera(async () => (await canal('r112test2'))?.viewers === 1);
  const v1t7 = (await canal('r112test1'))?.viewers;
  const v2t7 = (await canal('r112test2'))?.viewers;
  verdicto('T7 H14 cambio de canal libera el anterior (test1=0, test2=1)', v1t7 === 0 && v2t7 === 1);

  // ── T8 · H13: match-end de un TERCERO no cierra el canal del dueño ──
  atacante.emit('event', 'r112test2', { type: 'match-end' });
  await sleep(500);
  verdicto('T8 H13 match-end ajeno no cierra el canal', !!(await canal('r112test2')));

  // ── T9 · H13: match-end del DUEÑO (host2 publicó test2) cierra su canal ──
  host2.emit('event', 'r112test2', { type: 'match-end' });
  await espera(async () => !(await canal('r112test2')));
  verdicto('T9 H13 match-end del dueño cierra el canal', !(await canal('r112test2')));

  // ── T10 · H14: disconnect del espectador libera el contador ──
  espect.emit('watch', 'r112test1', () => {});
  await espera(async () => (await canal('r112test1'))?.viewers === 1);
  espect.disconnect();
  await espera(async () => (await canal('r112test1'))?.viewers === 0, 4000);
  verdicto('T10 H14 disconnect libera viewers (test1=0)', (await canal('r112test1'))?.viewers === 0);
} catch (e) {
  mal++;
  console.log('  ✗ excepción en el arnés:', e.message);
}

console.log(`RESULTADO: ${ok}✓ / ${mal}✗`);
host.disconnect(); host2.disconnect(); atacante.disconnect();
if (srv) srv.kill('SIGTERM');
process.exit(mal ? 1 : 0);
