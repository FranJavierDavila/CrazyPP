/**
 * CRAZY PING PONG · SERVIDOR DE SEÑALIZACIÓN PEERJS LOCAL (QA v3.6.28)
 * El QA de multijugador lo levanta para que las dos páginas se conecten
 * SIN depender de la nube pública de PeerJS (determinista y aislado).
 *   node scripts/peer_local.mjs   → puerto 9222, path /pp, key crazypp
 */
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { PeerServer } = require('peer');

PeerServer({ port: 9222, path: '/pp', key: 'crazypp', debug: false }, () => {
  console.log('PEER_LOCAL_LISTO');
});
