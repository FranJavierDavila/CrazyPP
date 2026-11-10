CRAZY PING PONG · WORKER DE TELEMETRÍA DE PRODUCCIÓN (ronda 8)
================================================================

QUÉ ES
------
worker.js es el reemplazo del worker actual (crazypp-tele): acepta los lotes
de telemetría anónima del juego y los GUARDA en una base D1 (SQLite serverless
de Cloudflare, plan gratuito). A diferencia del anterior, EXPONE LECTURA con
tu clave, así que los datos del casco ya se pueden ver.

El juego NO cambia: ya apunta a este worker desde 3.6.5-SDK6 (ronda 7).

CONTRATO (hermano del receptor local /api/telemetria)
-----------------------------------------------------
  POST   /api/tele            lote → D1 · 204 (acepta array directo y wrapper)
  GET    /api/tele            latido público {ok, total, ts}
  GET    /api/tele?salud=1    PÚBLICO {ok, total, ultimoRec, haceSeg} (r42)
  GET    /api/tele?resumen=1  agregados completos   → REQUIERE clave
  GET    /api/tele?rank=1     RANKINGS MUNDIALES por pid (ELO/victorias/
                            puntos/logros)        → REQUIERE clave (r46)
  GET    /api/tele?eventos=N  últimos N crudos      → REQUIERE clave
  GET    /api/tele?csv=1      CSV crudo (tope 20.000)→ REQUIERE clave (r42)
  DELETE /api/tele?sid=…      purga (sin sid → todo)→ REQUIERE clave
  DELETE /api/tele?dias=N     retención: borra lo anterior a N días (r42)
  OPTIONS                      preflight CORS

Eventos con IDENTIDAD MÍNIMA (desde la build 3.6.139 · r45/r46): cada
evento lleva opcionalmente `pid` (16 hex anónimos persistentes) y `n`
(nombre elegido, ≤12 chars). Tres eventos alimentan los rankings y el
análisis de retención:
  perfil     {el,w,bs,st,pt,ach} → foto de progreso (al entrar/salir de VR)
  resultado  {m,a,b,w,bo}       → fin de partido (m: ia|p2p|carrera)
  logro      {id}               → desbloqueo NUEVO de un logro (uno por logro)
El resumen añade `retencion` (D1/D7/D30 por pid + % recurrentes) y
`logrosTop` (desbloqueos agregados); `?rank=1` agrega por jugador.

  Filtros (r42): ?dias=N limita por LLEGADA al servidor (columna rec) en
  resumen, eventos, csv y DELETE; combinable con ?sid= en todos.

La clave se declara como VARIABLE del worker con nombre exacto: CLAVE.
En las lecturas se pasa por ?clave=… o cabecera X-Clave. El POST no lleva
clave (el juego es código público: nunca puede guardar secretos).

PRIVACIDAD: se guarda exactamente el JSON del evento — sin IP, sin
user-agent, sin cabeceras. Verificado por la capa J (qa_telemetria.py).

DESPLIEGUE POR DASHBOARD (~10 minutos, sin CLI)
-----------------------------------------------
1.  Entra en dash.cloudflare.com → Workers & Pages.
2.  Crea la BASE DE DATOS:
    Storage & Databases → D1 SQL Database → Create.
    Nombre: crazypp-tele   ·   Location: automatic.
    (No hace falta ejecutar SQL: la tabla se crea sola al primer evento.)
3.  Abre el worker existente crazypp-tele (Workers & Pages → crazypp-tele)
    → botón «Edit code» (Editar código).
4.  BORRA todo el código del editor y PEGA el contenido íntegro de
    scripts/worker-tele/worker.js (este mismo directorio). → Deploy.
5.  Enlaza la base: Settings del worker → Bindings → Add binding →
    D1 DATABASE.  Variable name: DB   ·   D1 database: crazypp-tele. → Deploy.
6.  Pon la clave: Settings del worker → Variables and Secrets →
    Add variable.  Type: Secret   ·   Name: CLAVE   ·   Value: TU_SECRETO
    (inventado por ti, guárdalo aparte). → Deploy.
7.  Verificación (30 s): abre en el navegador
      https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele
    → debe responder {"ok":true,"total":N,"ts":…} (latido público).
    Y con tu clave:
      https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele?resumen=1&clave=TU_SECRETO
    → JSON completo (porEvento, sesiones, fps, champRank…).

ALTERNATIVA POR CLI (si prefieres)
----------------------------------
    cd scripts/worker-tele
    npx wrangler@3 d1 create crazypp-tele     # copia el database_id a wrangler.toml
    CLAVE=tu-secreto npx wrangler@3 deploy

EL PANEL (visor fácil)
----------------------
Panel /telemetria (en local :3000 o por el gateway :81) → botón
«Producción (D1)» → pega la CLAVE la primera vez (se recuerda en el
navegador, nunca sale del dispositivo). A partir de ahí verás EN VIVO los
eventos que llegan del casco y de cualquier jugador: KPIs, FPS medio VR,
errores top, champ_rank por campeonato y los últimos 20 crudos.

También en Pages: https://franjavierdavila.github.io/CrazyPP/telemetria.html
(mismo visor, sin tocar nada local — desde la ronda 18 muestra ARRIBA DEL
TODO la tarjeta «Alarmas de producción» con el nivel global y cada alarma).

ALARMAS (ronda 18 · M2b — ampliada en M5b)
-------------------------------------------
El resumen (?resumen=1) devuelve el bloque `alarmas` — interpreta los
agregados y avisa de los síntomas que matan la retención en el casco:

  fps_bajo    media de vr_end.fps < 72 (confort Quest) con ≥3 muestras →
              AMARILLO; < 60 (mínimo jugable) → ROJO.
  errores_js  media de eventos `error` por sesión ≥ 1 → AMARILLO;
              ≥ 3 → ROJO. El mensaje más frecuente viaja en `datos.top`.
  vr_cortas   sesiones VR cerradas (vr_end o fechadas por vr_ping) que
              duran < 60 s = posible crash al entrar: ≥ 25% con ≥ 3
              sesiones → AMARILLO; ≥ 50% → ROJO.
  sin_sonido  (M5b) golpes sin sonido: errores con marcador de audio en el
              mensaje (audio/sonido/decode/sfx) + eventos `golpe_sin_sonido`
              (el juego aún no los envía: la alarma queda preparada — el día
              que lleguen, disparan sin otro deploy). ≥ 1 por sesión →
              AMARILLO; ≥ 3 → ROJO.

Estructura: {"nivel": "verde"|"amarillo"|"rojo",
             "items": [{id, nivel, msg, datos}]}.
Sin datos suficientes → nivel «verde» y sin items (no se alarma con 1-2
muestras). El filtro ?sid reescala las alarmas al subconjunto. Nivel global
= el PEOR de los items. Nada previo cambia: es un campo NUEVO y tolerante
(paneles viejos simplemente no lo leen).

TURN SIN COSTE PARA JUGAR ENTRE CASAS (ronda 20 · P4-F4)
---------------------------------------------------------
Para partidas entre redes distintas, el relé TURN entra cuando el enlace
directo no se abre (NAT simétrico, CGNAT…). El TURN público Open Relay
está RETIRADO (verificado 2026-11-07: openrelay.metered.ca → 192.0.2.1,
IP-documentación). Dos rutas vivas, ambas sin coste real:

RUTA A · Cloudflare Realtime (recomendada · gratis hasta 1 TB/mes)
  1. dash.cloudflare.com → My Profile → API Tokens → Create Token →
     Custom Token → permiso Account · Realtime TURN · Edit.
  2. Worker crazypp-tele → Settings → Variables and Secrets →
     Add · Type: Secret · Name: TURN_API_TOKEN · Value: el token. → Deploy.
  3. Verifica: https://…workers.dev/api/ice → "turn":true,
     "fuente":"cloudflare". (Puede pedir tarjeta en el perfil de CF
     para productos medidos, pero NO cobra por debajo de 1 TB/mes.)

RUTA B · Metered / Open Relay (sin tarjeta · gratis 20 GB/mes)
  1. Crea la cuenta gratuita en metered.ca (sin tarjeta) y una app;
     copia el subdominio (p. ej. «crazypp» para crazypp.metered.live)
     y la apiKey del panel.
  2. Worker crazypp-tele → Settings → Variables and Secrets:
     - Add · Type: Text   · Name: METERED_APP      · Value: el subdominio
     - Add · Type: Secret · Name: METERED_API_KEY  · Value: la apiKey
     → Deploy.
  3. Verifica: https://…workers.dev/api/ice → "turn":true,
     "fuente":"metered". Sin tocar código: el worker ya lee esas
     variables y sanea las credenciales (fuera puerto 53, turn sin
     credencial descartado).

PRIORIDAD AUTOMÁTICA: TURN_API_TOKEN > METERED_* > STUN sólo (turn:false).
Mientras no haya ninguna configurada, /api/ice responde STUN honesto —
el juego funciona igual en la misma Wi-Fi y en muchas fibras entre casas
(STUN basta); TURN es la red de seguridad.

OJO: los despliegues por scripts/deploy_worker.py PRESERVAN los secrets
ya existentes del worker (se re-listan sin valor en el PUT); los valores
nunca pasan por el repo.

COSTES (plan gratuito de Cloudflare)
------------------------------------
D1 gratis: 100.000 filas escritas/día y 5 M leídas/día. Cada evento es una
fila pequeña (<2 KB). Para tener un problema real de coste necesitarías
cientos de jugadores diarios con sesiones larguísimas — y aún así el plan
de pago son 5 USD/mes.

REPORTE DEL DUEÑO (M5b · scripts/alerta_telemetria.py)
------------------------------------------------------
Lectura en un vistazo de las alarmas de producción, sin abrir el panel:

    python3 scripts/alerta_telemetria.py            # reporte humano
    python3 scripts/alerta_telemetria.py --json     # salida máquina (cron)
    python3 scripts/alerta_telemetria.py --sid XYZ  # reescala a una sesión

Códigos de salida para automatizar: 0 VERDE · 1 AMARILLO · 2 ROJO ·
3 ERROR de red/clave (no es alarma). Usa curl (workers.dev bloquea urllib)
y lee la clave de .clave-produccion. No duplica umbrales: reporta lo que el
worker declara y añade contexto (FPS medio, duraciones, versión más activa).

QA
--
La capa J (scripts/qa_telemetria.py) verifica el worker SIN nube: ejecuta el
mismo worker.js contra SQLite real (node:sqlite) con el harness
scripts/worker-tele/test_local.mjs — contrato completo, saneo, clave,
agregados SQL, ALARMAS (bloque O: perfil malo rojo, perfil sano verde,
fronteras amarillo/rojo, filtro sid, almacén vacío) y privacidad (67
checks tras M5b: O5/O5b/O5c cubren sin_sonido — amarillo, rojo, filtro sid,
los errores sin marcador NO cuentan y la purga vuelve a verde). Lo que pasa
esa prueba es byte a byte lo que se despliega.
