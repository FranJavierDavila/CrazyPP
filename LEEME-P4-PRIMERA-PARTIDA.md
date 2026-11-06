# CRAZY PING PONG · P4 — TU PRIMERA PARTIDA REAL ONLINE (2 Quest 3)

Esta guía es para el dueño. En 10 minutos dejas el terreno preparado y
después juegas la primera partida entre dos cascos por internet.

QUÉ SE HA HECHO (r125 · 3.6.114-SDK6)
-------------------------------------
El juego ya no depende del TURN público OpenRelay (muerto desde hace más
de un año): ahora el worker crazypp-tele reparte **TURN de Cloudflare
Realtime** con credenciales efímeras (valen 6 horas, se acuñan al vuelo).
Si el worker no responde, el juego sigue con STUN (suficiente en la
mayoría de redes domésticas) y, como última red, el túnel PeerJS.
Además cada partida deja en telemetría un evento `net_ice` que dice POR
DÓNDE viajó el enlace (LAN, internet directo o relé) y su RTT.

PASO 1 · Crear el token de Cloudflare (3 min, una sola vez)
-----------------------------------------------------------
1. Entra en dash.cloudflare.com → arriba a la derecha, icono de perfil →
   **My Profile** → **API Tokens** → **Create Token**.
2. Plantilla «Create Custom Token»:
   - Permiso: **Account** · **Realtime TURN** · **Edit**
     (si tu consola lo llama «Calls TURN», es el mismo).
   - Account Resources: tu cuenta (Escala3dcorreoia).
3. Create Token → **copia el token** (no vuelve a mostrarse).

PASO 2 · Dar el token al worker (2 min)
---------------------------------------
1. dash.cloudflare.com → Workers & Pages → **crazypp-tele** → Settings →
   **Variables and Secrets** → Add variable.
   - Type: **Secret** · Name: **TURN_API_TOKEN** · Value: el token del paso 1.
2. (Opcional) Si ya creaste una TURN key en Realtime → TURN, añade su
   **TURN_KEY_ID** igual que arriba. Si no, NO hace falta: el worker
   crea la key solo y la recuerda en la base D1 (tabla `cfg`).
3. Deploy.

PASO 3 · Comprobar que el TURN vive (30 s)
------------------------------------------
Abre en el navegador:

    https://crazypp-tele.escala3dcorreoia.workers.dev/api/ice

Debes ver:  `"turn": true`  y una lista iceServers con urls
`turn:turn.cloudflare.com...` y username/credential.
Si ves `"turn": false`, repasa los pasos 1-2 (con `error: "turn_upstream"`
el token llegó pero Cloudflare lo rechazó: revisa el permiso Realtime TURN).

PASO 4 · LA PARTIDA (el momento)
--------------------------------
1. **Quest A** (anfitrión): navegador del Quest →
   https://franjavierdavila.github.io/CrazyPP/ → entrar en VR →
   MULTIJUGADOR → CREAR SALA → apunta el código de 5 letras (p. ej. KX7QW).
2. **Quest B** (invitado): misma web → MULTIJUGADOR → UNIRSE → escribe el
   código. (O vía invitación del medallón de jugadores online.)
3. Acepta el micro (hay voz integrada). Cuenta atrás de 3 s y a jugar.
4. Si estuvieran en la MISMA red WiFi no hace falta TURN (va directo);
   TURN brilla cuando cada casco está en una casa/red distinta.

PASO 5 · Comprobar POR DÓNDE viajó (diagnóstico)
------------------------------------------------
Al terminar, abre con tu clave de lectura:

    https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele?resumen=1&clave=TU_CLAVE

y busca los eventos `net_ice`:
  - `lt`/`rt` = tipo de candidato local/remoto:
      host  = misma red (LAN) — lo más rápido
      srflx = internet directo (STUN bastó) — lo normal entre casas
      relay = viajó por TURN — NAT duro, pero FUNCIONA (para eso está)
  - `rtt` = ida y vuelta en ms (LAN 1-20 · misma ciudad 10-40 ·
    internacional 80-200; por encima de 250 se nota el retardo).
  - `st: "failed"` = el ICE murió → mira el apartado de problemas.
El reporte `net_match` del fin de partida trae además pérdida, jitter y
salud del reloj compartido.

PROBLEMAS TÍPICOS
-----------------
- «Sala no responde» al crear/código muerto: el código caducó (la sala
  vive mientras el anfitrión está en el menú). Crea otra.
- Tarda en conectar (10-20 s): normal en redes con NAT duro — el juego
  espera 22 s antes de degradar; el túnel PeerJS saca la partida.
- Se conecta y luego se cae: en telemetría habrá net_ice failed +
  net_match end — mándame el resumen y lo afino.
- Sin voz: revisa el permiso de micro del navegador del Quest
  (Ajustes del casco → Permisos → Cámara/Micro del navegador).

COSTE Y LÍMITES DEL TURN
------------------------
El plan gratuito de Cloudflare Realtime incluye un generoso volumen de
relé mensual; una partida de ping pong (poses ~20 KB/s por lado) ni lo
nota. Los límites por asignación (≥5-10 kpps, ≥50-100 Mbps) son de
sobra para el juego.

— r125 · Task 230 · P4 del roadmap. Dulce espera del primer saque real.
