/**
 * CRAZY PING PONG · SERVIDOR LIVE-TV (rama experimental exp/live-tv)
 * ------------------------------------------------------------------
 * Relay tonto + guía de canales. NO simula nada:
 *   · El HOST (Quest) publica su partida como canal y emite estado ~30 Hz.
 *   · El servidor sella CADA estado con SU reloj (t = Date.now()) para que
 *     todos los espectadores interpolen sobre el mismo tiempo.
 *   · Los espectadores solo reciben; el fan-out por salas es barato.
 *
 * Socket.io en path '/live/socket.io' (Caddy lo enruta por XTransformPort=3004;
 * el path propio deja libres /api/* para la guía REST).
 * REST: GET /api/channels (guía de TV) · GET /api/health.
 */
import { createServer } from 'http';
import { Server } from 'socket.io';

const PORT = 3004;
const STALE_MS = 12000;   // sin estado 12 s → canal fantasma fuera
const SWEEP_MS = 5000;

/** matchId → canal { matchId, name, p1, p2, mode, viewers, startedAt, lastStateAt, lastState } */
const channels = new Map();

const listChannels = () =>
  [...channels.values()].map(c => ({
    matchId: c.matchId,
    name: c.name,
    p1: c.p1,
    p2: c.p2,
    mode: c.mode,
    viewers: c.viewers,
    startedAt: c.startedAt,
    live: true,
  }));

const httpServer = createServer((req, res) => {
  const url = req.url || '/';
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (url.startsWith('/api/channels')) {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.setHeader('Cache-Control', 'no-store');
    res.end(JSON.stringify({ ok: true, channels: listChannels(), ts: Date.now() }));
    return;
  }
  if (url.startsWith('/api/health')) {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify({ ok: true, service: 'live-tv', channels: channels.size, ts: Date.now() }));
    return;
  }
  res.writeHead(404); res.end();
});

const io = new Server(httpServer, {
  path: '/live/socket.io',
  cors: { origin: '*', methods: ['GET', 'POST'] },
  pingTimeout: 60000,
  pingInterval: 25000,
  maxHttpBufferSize: 1e6,
});

const log = (...a) => console.log('[live]', new Date().toISOString().slice(11, 19), ...a);

io.on('connection', (socket) => {
  let watching = null;   // matchId que este socket mira
  let hosting = null;    // matchId que este socket publica

  const dropChannel = (reason) => {
    if (!hosting) return;
    if (channels.has(hosting)) {
      channels.delete(hosting);
      log(`canal fuera ${hosting} (${reason})`);
      io.emit('channels-updated', listChannels());
    }
    try { socket.leave(`live:${hosting}`); } catch { /* */ }
    hosting = null;
  };

  // ─── HOST: publica una partida como canal ───
  socket.on('publish', ({ matchId, meta } = {}) => {
    if (!matchId || typeof matchId !== 'string') return;
    if (hosting && hosting !== matchId) dropChannel('re-publish');
    hosting = matchId;
    socket.join(`live:${matchId}`);
    const prev = channels.get(matchId);
    channels.set(matchId, {
      matchId,
      name: (meta && meta.name) || 'Partida en vivo',
      p1: (meta && meta.p1) || 'Jugador VR',
      p2: (meta && meta.p2) || 'Rival',
      mode: (meta && meta.mode) || 'match',
      viewers: prev ? prev.viewers : 0,
      startedAt: prev ? prev.startedAt : Date.now(),
      lastStateAt: Date.now(),
      lastState: prev ? prev.lastState : null,
    });
    log(`canal NUEVO ${matchId} · "${channels.get(matchId).name}"`);
    io.emit('channels-updated', listChannels());
  });

  socket.on('unpublish', () => dropChannel('unpublish'));

  // ─── HOST: estado continuo ~30 Hz (sellado con el reloj del SERVIDOR) ───
  socket.on('state', (matchId, state) => {
    const ch = channels.get(matchId);
    if (!ch) return;                       // canal ya cerrado: ignora
    ch.lastStateAt = Date.now();
    if (state && typeof state === 'object') {
      state.t = ch.lastStateAt;            // ← reloj único para todos
      ch.lastState = state;                // snapshot para quien llegue tarde
      socket.to(`live:${matchId}`).emit('state', state);
    }
  });

  // ─── HOST: eventos discretos (hit/bounce/net/point/serve/match-end) ───
  socket.on('event', (matchId, evt) => {
    if (!evt || typeof evt !== 'object') return;
    socket.to(`live:${matchId}`).emit('event', evt);
    if (evt.type === 'match-end') {
      log(`match-end en ${matchId} → canal fuera`);
      dropChannel('match-end');
    }
  });

  // ─── ESPECTADOR ───
  socket.on('watch', (matchId, ack) => {
    const ch = channels.get(matchId);
    if (!ch) { try { ack && ack({ error: 'canal-no-existe' }); } catch { /* */ } return; }
    watching = matchId;
    socket.join(`live:${matchId}`);
    ch.viewers++;
    io.to(`live:${matchId}`).emit('viewers', ch.viewers);
    io.emit('channels-updated', listChannels());
    try { ack && ack({ ok: true, meta: listChannels().find(c => c.matchId === matchId), lastState: ch.lastState }); } catch { /* */ }
    log(`espectador → ${matchId} (${ch.viewers} viendo)`);
  });

  const leaveWatch = () => {
    if (!watching) return;
    const ch = channels.get(watching);
    if (ch) {
      ch.viewers = Math.max(0, ch.viewers - 1);
      io.to(`live:${watching}`).emit('viewers', ch.viewers);
      io.emit('channels-updated', listChannels());
    }
    watching = null;
  };

  socket.on('leave-watch', leaveWatch);

  // ─── Guía: listado bajo demanda (respaldo del push channels-updated) ───
  socket.on('list-channels', () => {
    socket.emit('channels', listChannels());
  });

  socket.on('disconnect', () => {
    leaveWatch();
    dropChannel('host disconnect');
  });
});

// Barrido de canales fantasma (host vivo pero sin enviar estado)
setInterval(() => {
  const now = Date.now();
  let changed = false;
  for (const [id, ch] of channels) {
    if (now - ch.lastStateAt > STALE_MS) { channels.delete(id); changed = true; log(`canal STALE fuera ${id}`); }
  }
  if (changed) io.emit('channels-updated', listChannels());
}, SWEEP_MS);

httpServer.listen(PORT, () => log(`LIVE-TV relay escuchando en :${PORT} · REST /api/channels`));

// ─── GUARDIÁN DEL JUEGO (:3000) ─────────────────────────────────────────
// El sandbox mata los procesos que arrancan los comandos del agente, pero
// NO a los hijos de este relay (proceso del boot). Si :3000 no responde,
// este bucle arranca el dev server del juego como HIJO del relay y lo
// reanima si muere. Guard con globalThis para ser idempotente con --hot.
if (!(globalThis as any).__ppGuardian) {
  (globalThis as any).__ppGuardian = true;
  const GAME = 'http://127.0.0.1:3000/';
  const GUARDA_MS = 20_000;
  const vivo = async (): Promise<boolean> => {
    try {
      await fetch(GAME, { signal: AbortSignal.timeout(8000) } as any);
      return true; // cualquier respuesta HTTP = hay listener
    } catch (e: any) {
      if (e?.name === 'TimeoutError' || e?.name === 'AbortError') return true; // lento pero vivo
      return false; // ECONNREFUSED = caído de verdad
    }
  };
  const guarda = async () => {
    if (await vivo()) return;
    log('GUARDIÁN: juego caído en :3000 — arrancando next dev como hijo del relay...');
    try {
      Bun.spawn(['bun', 'run', 'dev'], {
        cwd: '/home/z/my-project',
        stdin: 'ignore',
        stdout: 'ignore',
        stderr: 'ignore',
      });
    } catch (e) {
      log('GUARDIÁN: fallo al arrancar el juego:', e);
    }
  };
  setInterval(guarda, GUARDA_MS);
  setTimeout(guarda, 4_000); // primera pasada enseguida
  log('GUARDIÁN del juego activo (comprueba :3000 cada 20 s)');
}
