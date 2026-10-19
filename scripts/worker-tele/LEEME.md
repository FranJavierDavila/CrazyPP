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
  GET    /api/tele?resumen=1  agregados completos   → REQUIERE clave
  GET    /api/tele?eventos=N  últimos N crudos      → REQUIERE clave
  DELETE /api/tele?sid=…      purga (sin sid → todo)→ REQUIERE clave
  OPTIONS                      preflight CORS

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

COSTES (plan gratuito de Cloudflare)
------------------------------------
D1 gratis: 100.000 filas escritas/día y 5 M leídas/día. Cada evento es una
fila pequeña (<2 KB). Para tener un problema real de coste necesitarías
cientos de jugadores diarios con sesiones larguísimas — y aún así el plan
de pago son 5 USD/mes.

QA
--
La capa J (scripts/qa_telemetria.py) verifica el worker SIN nube: ejecuta el
mismo worker.js contra SQLite real (node:sqlite) con el harness
scripts/worker-tele/test_local.mjs — contrato completo, saneo, clave,
agregados SQL y privacidad (30 checks). Lo que pasa esa prueba es byte a
byte lo que se despliega.
