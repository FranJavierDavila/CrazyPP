# CRAZY PING PONG · live-service (relay de CRAZY TV)

Servidor relay de emisiones en vivo. No simula nada: recibe el estado de la
Quest (~30 Hz), le sella su reloj y lo reparte a todos los espectadores.

## Arranque

```bash
npm install
node server.mjs              # puerto 3004
LIVE_PORT=8080 node server.mjs   # otro puerto
```

Funciona con Node >= 18 (también con Bun: `bun server.mjs`).

Comprobación de vida: `http://localhost:3004/api/health`

## Canal de demostración (sin Quest)

```bash
node tools/mock_host.mjs     # canal 'demo-qa' infinito
```

Abre `tv.html` (con `?relay=http://IP:3004` si el relay no está en el mismo
dominio que la web) y elige el canal DEMO.

## Endpoints REST

- `GET /api/channels` — guía de canales: `{ ok, channels: [{ matchId, name, p1, p2, mode, viewers, startedAt, live }], ts }`
- `GET /api/health` — `{ ok, service: 'live-tv', channels: n, ts }`

## Protocolo Socket.io (path `/live/socket.io`)

| Evento | Quién | Payload |
|---|---|---|
| `publish` | host | `{ matchId, meta: { name, p1, p2, mode } }` |
| `state` | host | `(matchId, estado)` — el servidor añade `t` (su reloj) |
| `event` | host | `(matchId, evt)` — `hit/bounce/net/point/serve/match-end` |
| `unpublish` | host | — |
| `watch` | espectador | `(matchId, ack)` → ack con meta + último estado |
| `leave-watch` | espectador | — |
| `list-channels` | espectador | → responde `channels` |
| `state` / `event` / `viewers` / `channels-updated` | servidor → sala | — |

Sala por canal: `live:<matchId>`. Un canal se retira por `unpublish`,
`match-end`, desconexión del host o 12 s sin estado (barrido cada 5 s).

CORS abierto (`*`): el juego y los espectadores pueden conectar desde
cualquier origen. Detrás de un proxy propio (nginx), enruta
`/live/socket.io/` y `/api/` a este puerto (ver LEEME-DESPLIEGUE.txt).
