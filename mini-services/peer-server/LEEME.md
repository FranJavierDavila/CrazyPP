# crazypp-peer-server · A2 (auditoría r120 · ola 3)

PeerServer **propio** para la señalización de salas. Hoy el juego registra
las salas en el cloud público de PeerJS (`0.peerjs.com`) — si ese servicio
cae o se satura, `hostRoom`/`joinRoom` mueren con `no_lobby_server` y no hay
ruta alternativa. Este mini-servicio elimina esa dependencia con el mismo
protocolo: el cliente del juego no cambia.

## Uso

```bash
bun install          # o npm install (depende de 'peer' ^1.5)
PORT=3005 bun start  # o npm start
```

## Ruta del gateway (Caddy)

El `Caddyfile` del repo ya lleva la ruta fija por prefijo (r129):

```
handle /peerjs/* {
    reverse_proxy localhost:3005
}
```

En el VPS de producción añade la misma ruta al Caddy real.

## Encenderlo en el juego

Antes de crear/unirse a una sala (por ejemplo en la consola o en un script
previo):

```js
globalThis.PP_SIGNAL_ENDPOINT = 'https://TU-DOMINIO/peerjs';
```

- Sin la variable: cloud de PeerJS (comportamiento de siempre).
- Con la variable: las salas se registran en ESTE servidor.
- La variable se lee al abrir el peer (`NetLink._signalOpts()`), así que
  puede fijarse en cualquier momento antes de `host/join`.

## Qué NO es

No es un servidor de juego: el transporte (DataChannels v2, voz, túnel de
emergencia) sigue siendo WebRTC punto a punto entre los cascos. El
PeerServer sólo hace el registro inicial y el intercambio offer/answer/ICE.
