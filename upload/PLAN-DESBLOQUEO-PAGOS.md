# PLAN · DEMO + PAGOS Y PROTECCIÓN DEL JUEGO (FASE 145 · 11-nov-2026)

Respuesta a las dos preguntas del dueño. Escrito contra el stack REAL del
proyecto: juego web estático (GitHub Pages), worker de telemetría en
Cloudflare con D1 (`crazypp-tele`), campeonatos modulares cargados por el
ChampLoader desde carpetas con manifest, y `ChampLoader.LOCKED` +
`candado.png` + `ppDebugMode` ya existentes.

════════════════════════════════════════════════════════════════════
1 · CÓMO PERMITIR SÓLO ALGUNAS SECCIONES COMO DEMO Y COBRAR EL RESTO
════════════════════════════════════════════════════════════════════

REGLA DE ORO
  El desbloqueo NO puede vivir sólo en el cliente. Un booleano en
  localStorage (o un `if (premium)` en game.html) se salta en 30 s desde
  la consola. La protección útil tiene DOS mitades:
    (a) un servidor que decide SIEMPRE qué contenido entrega, y
    (b) el contenido premium NO se descarga sin licencia.
  Si los assets premium viajan en el bundle público, cualquier candado
  es decorado.

ARQUITECTURA (todo en su Cloudflare actual)

  Navegador (Quest) ──► Worker Cloudflare ──► D1 (licencias, ya existe la BD)
        │                     │
        │                     └──► R2 (assets premium: GLB/PNG/MP3 de los
        │                          campeonatos cerrados) con URLs FIRMADAS
        └──► Páginas estáticas (demo: Halloween + modo libre + sala)

  · PROVEEDOR DE PAGO: Stripe Checkout (tarjeta+Bizum, manual de IVA) o
    Paddle / Lemon Squeezy (actúan de "Merchant of Record" y liquidan el
    IVA español por ti — recomendable si no quieres tocar fiscalidad).
    Pago único por licencia (simple) o suscripción (recurrente).
  · FLUJO:
    1. El juego arranca y pide `GET /api/lic?tok=…` (token guardado en
       IndexedDB). Sin token → modo DEMO.
    2. Modo DEMO: campeonatos marcados con el candado que YA existe
       (extender `ChampLoader.LOCKED` → `DEMO_LOCKED`); el gatillo sobre
       ellos dice «Desbloquea el Salvaje Oeste» y abre el Checkout.
    3. Pago OK → el webhook del proveedor llama al worker → valida la
       firma del webhook → inserta la licencia en D1 → responde.
    4. El worker emite un TOKEN FIRMADO (Ed25519/ECDSA vía WebCrypto;
       payload: {lic, scopes:['oeste','magia','locura','orbital'], exp}).
    5. El juego guarda el token y lo verifica LOCALMENTE con la clave
       pública (funciona OFFLINE en el Quest; `exp` corto + revalidación
       al haber red). La licencia no expira; el token sí, y se renueva
       gratis al arrancar con red.
  · EL PASO CLAVE: `championships.json` pasa a servirlo el worker
    FILTRADO por scopes del token, y las carpetas premium (oeste/, magia/,
    locura/, estacion_orbital/) se mueven a R2: el manifest y los assets
    se piden con URL firmada de corta vida SOLO si el token vale.
    El ChampLoader ya descubre por índice — cambio pequeño en el fetch.
  · QUÉ QUEDA EN LA DEMO (propuesta): Halloween + partido libre + sala +
    academia. Premium: Oeste, Magia, Locura, Orbital (los 4 con más
    contenido). Precio ancla típico: 4,99–7,99 € pago único.

ESFUERZO ESTIMADO (con el stack ya montado)
  · Checkout + webhook + tabla licencias en D1 + token firmado … 1 día
  · championships.json dinámico + assets premium en R2 con URLs
    firmadas y reenganche del ChampLoader …………………… 1 día
  · Verificación WebCrypto en el cliente + UI de candado/compra … ½ día
  · Minificado del bundle (ver §2, capa 4) …………………………… ½ día
  TOTAL: 2–3 días de trabajo.

VÍA ALTERNATIVA SIN CÓDIGO
  Distribuir por App Lab / SideQuest: Meta gestiona pago y licencia por
  cuenta Oculus. Coste: se pierde el "abierto a todo el mundo" web que
  hoy es el pitch del juego.

════════════════════════════════════════════════════════════════════
2 · CÓMO PROTEGER EL JUEGO DE COPIAS E INGENIERÍA INVERSA (HONESTO)
════════════════════════════════════════════════════════════════════

LA VERDAD PRIMERO
  En la web, TODO lo que corre en el navegador es inspeccionable: no
  existe la protección absoluta (tampoco en nativo, ni en consolas).
  El objetivo realista es doble:
    · que copiar CUESTE más de lo que rinde, y
    · que una copia NO LLEVE las partes que valen (contenido, ranking,
      multijugador).

CAPAS, DE MÁS A MENOS EFECTIVA
  1 · NO ENVIAR EL CONTENIDO PREMIUM SIN LICENCIA (la única protección
      REAL): assets de campeonatos premium en R2 con URLs firmadas de
      corta vida tras validar el token. Un HTML copiado sin assets no
      es jugable. Sin esta capa, el resto es maquillaje.
  2 · ÍNDICE DINÁMICO: `championships.json` servido por el worker según
      licencia — la copia ni siquiera sabe qué campeonatos existen.
  3 · TOKEN FIRMADO + vínculo suave a dispositivo (hash UA+GPU+almacen-
      miento): dificulta compartir licencias; revalidación online
      periódica; offline tolerante (exp + gracia de días).
  4 · MINIFICADO + OFUSCACIÓN del bundle (Terser/obfuscator): hoy
      game.html es texto claro de 11,5 MB. Minificar sube el coste de
      leer el código y, de paso, baja el peso de carga (mejora también
      el primer arranque en el Quest). No es seguridad, es fricción.
  5 · AUTORIDAD DEL SERVIDOR EN LO COMPETITIVO: el ranking/ELO ya viven
      en el worker (D1). Si el worker exige un token de sesión por
      partida para aceptar resultados, una copia pirata queda como
      "juguete sin leaderboard" — y el leaderboard es el anzuelo real
      de recompra. La telemetría ya distingue copias (sid de sesión).
  6 · MARCA DE AGUA POR LICENCIA: el id de licencia viaja en la
      telemetría y en los assets personalizados — si una copia se
      filtra, se sabe de qué licencia salió (disuade compartir).
  7 · LEGAL: copyright visible en portada + EULA de un párrafo + el
      registro de licencias en D1 como prueba de compra.

LO QUE NO FUNCIONA (para no perder el tiempo)
  · Desactivar F12 / detectar devtools: se salta en dos clics.
  · Cifrar el JS y decodificarlo con eval(): se decodifica igual y mata
    el rendimiento del Quest.
  · "DRM del navegador": no existe para WebGL/WebXR.
  · Ocultar secretos (claves) en el cliente: toda clave en el cliente
    está comprometida; las claves privadas viven SOLO en el worker.

RESUMEN EN UNA LÍNEA
  Pago con Stripe/Paddle → webhook → licencia en D1 → token firmado →
  contenido premium servido desde R2 sólo a tokens válidos + ranking
  authority en el worker + bundle minificado. 2–3 días. Con eso la copia
  sale vacía: sin contenido, sin ranking, sin multijugador oficial.
