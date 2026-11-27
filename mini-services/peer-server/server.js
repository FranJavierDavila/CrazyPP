/**
 * CRAZY PING PONG · A2 (r129 · ola 3) · PEERSERVER PROPIO
 * -------------------------------------------------------
 * El hallazgo A2 de la auditoría r120: openPeer registraba las salas en el
 * cloud público de PeerJS (0.peerjs.com) — sin SLA, sin alternativa. Este
 * servicio (el proyecto ya opera su live-service igual) es el mismo
 * protocolo PeerJS servido en casa: el cliente NO cambia — el juego lee
 * globalThis.PP_SIGNAL_ENDPOINT y montas las salas aquí.
 *
 *   bun install            (o npm install)
 *   PORT=3005 bun start    (o npm start)
 *
 * Detrás del Caddy del dueño:  handle /peerjs/*  →  localhost:3005
 * En el juego:  globalThis.PP_SIGNAL_ENDPOINT = 'https://TU-DOMINIO/peerjs'
 * (antes de host/join; si no está, se usa el cloud de PeerJS como hoy).
 */
const { PeerServer } = require('peer');

const PORT = Number(process.env.PORT || 3005);

const srv = PeerServer({
  port: PORT,
  path: '/peerjs',
  // la clave por defecto de peerjs-server ('peerjs') NO se toca: así el
  // cliente funciona sin configurar nada en el servidor.
});

srv.on('connection', (id) => {
  console.log(new Date().toISOString(), 'peer conectado:', id);
});
srv.on('disconnect', (id) => {
  console.log(new Date().toISOString(), 'peer fuera:', id);
});
srv.on('error', (e) => {
  console.error('peer-server error:', e);
});

console.log('crazypp-peer-server en :' + PORT + ' (path /peerjs, key por defecto)');
