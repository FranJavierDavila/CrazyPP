// Datos de la auditoría de calidad — CRAZY PING PONG r111 (8a8d9b2, 21-11-2026)
// Re-auditoría completa tras la r109 (669a08e). Todas las cifras y citas
// proceden de la verificación real del 21-11-2026 (batería re-ejecutada,
// contraste línea a línea de los 18 hallazgos r109 con dos revisores en
// paralelo, contrato cliente↔worker, build contra el golden e higiene).

const estadoHoy = {
  ABIERTO: 'ABIERTO', CERRADO: 'CERRADO', PARCIAL: 'PARCIAL', RETIRADO: 'RETIRADO',
};

const findings = [
  {
    sev: 'ALTO', id: 'H1', estado: 'ABIERTO',
    titulo: 'Portal de Duelos Locos online: el HIT del golpe portalizado viaja con velocidad (0,0,0)',
    donde: 'c12_pingponggame.js:14484 (bloque 5.55 en 19043) · c09_red_netlink.js:1923 (bloque 5.6 en 19092)',
    evidencia: [
      "c12:14483-14485 (bloque 5.55, _portalProcesa):",
      "  this._portalSalVel.copy(newV);",
      "  b.vel.set(0, 0, 0);                    // congelada (spin CONSERVADO, spec)",
      "c12:19092 (bloque 5.6, DESPUÉS) → c09:1923:",
      "  v: this._velNet(g.ball.vel)            ← ya congelada a cero",
      "_portalEnvioVel NO existe en todo el repo (grep 21-11-2026)",
    ],
    porque: [
      'El bloque 5.55 (portaliza la bola) se ejecuta en el mismo frame ANTES del bloque 5.6 (envío del HIT), y _portalProcesa congela ball.vel a cero justo en el frame en que sendHit la lee. El validador de PPNET (§12) solo comprueba techo de velocidad, así que un vector cero pasa sin rechazo: en el rival, el fantasma nace parado en el aire, cae por gravedad y su árbitro puede cantar bote(s) → CLAIM de un punto fantasma durante el tránsito de ~1 s, seguido de un BALL_HANDOFF tardío que choca contra el punto ya reclamado.',
      'Re-verificado hoy línea a línea: el orden 5.55→5.6 sigue intacto y la velocidad de salida solo se guarda en _portalSalVel (usada únicamente al SALIR del portal), no en el envío.',
    ],
    fix: 'Enviar la velocidad de salida real: en _portalProcesa guardar this._portalEnvioVel = newV (y posición _portalTmpC) y usarlos en el sendHit del bloque 5.6 cuando ppTransito esté activo; o ejecutar la sección 5.55 DESPUÉS de la 5.6. Es el hallazgo de mayor prioridad: continúa sin corrección desde r109.',
  },
  {
    sev: 'MEDIO', id: 'H2', estado: 'ABIERTO',
    titulo: 'HANDOFF sin guardia de estado (la rama HIT sí la tiene)',
    donde: 'c09_red_netlink.js:2302-2329 (guardia de la rama HIT en 2225-2228)',
    evidencia: [
      "rama HIT (2225-2228):",
      "  const stG = g.rules.state;",
      "  if (stG !== 'rally' && !(stG === 'serve' && (ev.kind === 1 || ev.kind === 2))) return;",
      "rama HANDOFF (2302):  if (ev.t === PPNET.VP.EV.HANDOFF) {   ← sin guardia",
    ],
    porque: [
      'Un HANDOFF con id nuevo que llegue atrasado (canal reliable encolado) se aplica en estado de punto o de saque: onHandoff pone state=auth/mine=true y las ramas smooth/snap copian la posición en g.ball.pos — teletransporte de la bola retenida del saque y robo de autoridad mientras el rival lanza. La guardia se añadió en r122 SOLO a la rama HIT.',
    ],
    fix: 'En ev.t === HANDOFF, if (g.rules.state !== \'rally\') return; y revisar por la misma lupa _applyRemoteClaim (2026), que llama forcePoint sin comprobar estado.',
  },
  {
    sev: 'MEDIO', id: 'H3', estado: 'ABIERTO',
    titulo: 'Watchdog de silencio inaccesible en v1 y ciego a la muerte del canal fast',
    donde: 'c09_red_netlink.js:1466-1469 (gate de v1 en 1394; tick() en 438 sin watchdog)',
    evidencia: [
      "1394:  if (this.v2 !== 'ok') { this.tick(dt); return; }   // v1 sale ANTES del watchdog",
      "1466-1469:  if (this._lastRelAt && now - this._lastRelAt > SILENCIO && this._lastFastAt &&",
      "             now - this._lastFastAt > SILENCIO) {           // exige rel Y fast mudos a la vez",
    ],
    porque: [
      'En modo v1 (túnel honesto) el watchdog nunca corre: si el rival muere sin cierre limpio, online queda en true indefinidamente. En v2, la condición AND exige que reliable Y fast estén ambos mudos: si solo muere el DataChannel fast, la partida queda congelada mientras rel siga respirando.',
    ],
    fix: 'Mover el watchdog antes del gate de v2 (en v1, usar la frescura de paquetes del túnel) y en v2 disparar también con now - this._lastFastAt > SILENCIO a secas cuando se esperan poses.',
  },
  {
    sev: 'MEDIO', id: 'H4', estado: 'ABIERTO',
    titulo: 'remapCause del CLAIM solo invierte para el invitado: el anfitrión lee las causas del rival sin espejo',
    donde: 'c09_red_netlink.js:2026-2027',
    evidencia: [
      "g.processIntents(g.rules.forcePoint(wMapped,",
      "  NetLink.remapCause(m.c, this.role === 'guest'), m.r));   // host → forGuest=false",
    ],
    porque: [
      'La causa del punto viaja en perspectiva del EMISOR. El remapeo se aplica solo si YO soy invitado, pero el claim SIEMPRE viene del otro lado: cuando el anfitrión aplica el claim de un invitado, el «culpa del rival» del rival se muestra tal cual como «culpa tuya» del anfitrión. El ganador llega bien; el daño es el texto del punto y la megafonía.',
    ],
    fix: 'En _applyRemoteClaim usar siempre NetLink.remapCause(m.c, true).',
  },
  {
    sev: 'MEDIO', id: 'H5', estado: 'ABIERTO',
    titulo: 'visDelta() es código muerto: la absorción de salto y el catch-up nunca se aplican',
    donde: 'c09_red_netlink.js:2377 (asignaciones en 2287 y 2314; cero llamadores en todo el repo)',
    evidencia: [
      "visDelta(dt) {                    // definición; c12 nunca la llama",
      "grep repo-wide (21-11-2026): solo la definición y su cita en el informe r109",
    ],
    porque: [
      'La función que absorbe el salto visual del HANDOFF smooth (_visOff) y el catch-up (_visOffMs) no tiene ningún llamador en el animate de c12: la bola teletransporta visualmente en cada handoff smooth, contrario a la spec §8, y los campos quedan asignados para siempre sin efecto.',
    ],
    fix: 'Llamar visDelta(dt) en el render de la bola de c12, o retirar la feature y sus campos (decisión del dueño).',
  },
  {
    sev: 'MEDIO', id: 'H6', estado: 'ABIERTO',
    titulo: 'Paquete SNAP sin clock.markSent: sus ecos jamás producen muestra NTP',
    donde: 'c09_red_netlink.js:1491-1508 (rama SNAP de _sendFast; _fastSend en 1580-1591)',
    evidencia: [
      "rama SNAP (1491-1508): construye el paquete y llama _fastSend SIN markSent",
      "los únicos markSent: rama pose (1541) y _flushEvents (1571)",
    ],
    porque: [
      'El rival ecoa el sendTime de TODO paquete recibido, pero al volver el eco el SNAP no tiene sello de envío y onPacket retorna antes de refinar el reloj. Con bola propia (SNAP a 30 Hz + pose a 60 Hz) cerca de un tercio de las llegadas no refinan el NTP — justo mientras la bola propia exige tHit preciso para el handoff. El jitter sí se actualiza (se calcula antes del return), lo que hace el fallo más silencioso.',
    ],
    fix: 'Añadir this._clock.markSent(now) en la rama SNAP de _sendFast (y en cualquier envío directo futuro).',
  },
  {
    sev: 'MEDIO', id: 'H7', estado: 'ABIERTO',
    titulo: '_flushEvents no envía nunca en modo túnel: HIT/HANDOFF sin flush inmediato',
    donde: 'c09_red_netlink.js:1561 (criterio correcto de _sendFast en 1477)',
    evidencia: [
      "_flushEvents(now) {",
      "  if (!this._pend.length || !this._fast || !this._fastOpen) return;  // túnel: _fastOpen=false",
      "_sendFast (1477): if (this._tunnel ? !(this.conn && this.conn.open) : (...))  ← sí lo gestiona",
    ],
    porque: [
      'En modo túnel (_tunnel=true) los DataChannels propios nunca abrieron, así que _fastOpen es falso por construcción y los flushes inmediatos de netLocalHit/netLocalToss/watchOwnCross son no-ops: los eventos críticos esperan al próximo tick de pose (túnel a 30 Hz: hasta ~33 ms extra de latencia en CADA golpe). No hay pérdida (viajan en el paquete de pose), solo latencia sistemática del modo de emergencia.',
    ],
    fix: 'Usar el mismo criterio de salida que _sendFast y delegar en _fastSend, que ya gestiona el túnel.',
  },
  {
    sev: 'MEDIO', id: 'H8', estado: 'ABIERTO',
    titulo: 'Contador de aces desplazado: un ace real nunca cuenta y un fallo del receptor sí',
    donde: 'c06_logros_stats_ia_rival.js:83 · espejo en c12:20539 · registerPaddleHit en c06:309-331',
    evidencia: [
      "c06:83:  if (rallyHits === 1) { this.data.aces++;   // con el comentario «ace: solo el sacador»",
      "c12:20539:  (it.rallyHits || 0) === 1                 // espejo del mismo umbral",
      "beginServeRally (c06:306) resetea rallyHits = 0 y el golpe de saque NO pasa por registerPaddleHit",
    ],
    porque: [
      'El golpe de saque nunca se registra en rallyHits: un ace verdadero termina con rallyHits = 0 y no cuenta; un punto donde el rival toca UNA vez y falla queda con rallyHits = 1 y cuenta como ace — la condición está invertida respecto a su propio comentario. Alimenta el logro aces10, el hito mesa_lock_aces5 y la puerta del dojo (5 aces).',
    ],
    fix: 'Cambiar la condición a rallyHits === 0 en los dos puntos (c06:83 y c12:20539).',
  },
  {
    sev: 'MEDIO', id: 'H9', estado: 'ABIERTO',
    titulo: 'El golpe torpe (mishit) pierde el spin al aplicarse el disparo diferido',
    donde: 'c06_logros_stats_ia_rival.js:1509 (firma 1668; vía limpia 1608; _aplicaDisparo usa d.spin en 1702)',
    evidencia: [
      "const _mv = this.mishit(ball, toca);",
      "this._preparaDisparo(ball, _mv, cx, cy, cz);        // sin el 6º argumento: spin",
      "…  spin: spin ? spin.clone() : new THREE.Vector3(),  // payload nace a cero",
    ],
    porque: [
      'mishit fija el giro del toque torpe en el mismo frame, pero _preparaDisparo se llama sin el argumento de spin: el payload nace a cero y _aplicaDisparo lo copia encima al aplicar el disparo diferido (hasta 0,75 s después). La bola vuela todo el periodo diferido curvándose y al contacto visual el giro desaparece de golpe. El camino limpio sí pasa shotSpin — es un refactor r99 incompleto en la única rama torpe.',
    ],
    fix: 'this._preparaDisparo(ball, _mv, cx, cy, cz, ball.spin) tras mishit (el payload ya clona).',
  },
  {
    sev: 'MEDIO', id: 'H10', estado: 'ABIERTO',
    titulo: 'La velocidad de superficie del apoyo omite bladeCenterUp: palanca de muñeca medida desde el punto equivocado',
    donde: 'c05_colisiones_ia_golpeo.js:853-858 (base de posición correcta en 894; rp.vel del grip en c04:382)',
    evidencia: [
      "c05:853:  _rsOff.set(0,0,0).addScaledVector(rp.right, rCx).addScaledVector(rp.up, rCy);",
      "  ← falta el término up·bladeCenterUp",
      "c04:382:  tmpV.copy(ps.pos).sub(ps.prev).divideScalar(dt)   // rp.vel es la velocidad del grip",
    ],
    porque: [
      '__ppRestLx/Dy se capturan respecto al CENTRO DE LA HOJA, pero rp.vel es la velocidad del punto seguido (el grip) y rp.omega la angular del cuerpo: la velocidad real del punto de contacto es rp.vel + omega x (right·rCx + up·(bladeCenterUp + rCy)) — falta el término up·0,14. Con una rotación de muñeca de 8 rad/s el error llega a ~1,1 m/s: el estado de fricción se decide con un deslizamiento falso y girar la muñeca despacio NO arrastra la bola, rompiendo la promesa del bloque r103 §6.',
    ],
    fix: '_rsOff…addScaledVector(rp.up, DIMS.bladeCenterUp + rCy). Los arneses golden no cubren apoyo+muñeca: conviene acompañar el cambio de un mini-arnés que lo ancle.',
  },
  {
    sev: 'MEDIO', id: 'H12', estado: 'ABIERTO',
    titulo: 'El gatillo del saque ignora la cuenta atrás del MATCH_START (a diferencia de la ruta natural)',
    donde: 'c12_pingponggame.js:9868-9872 y 9963-9965 (ruta protegida en 10006; netLocalToss en 10117; congelado en 18464-18468)',
    evidencia: [
      "10006 (grip):    if (this._netStart) return;   // r79: cuenta atrás en curso",
      "9868/9963 (gatillo): if (state === 'serve' && server === 'player' && !this.tossed …)",
      "                     { this.tossFromHand(this.ballHand, true); return; }   ← sin _netStart",
    ],
    porque: [
      'Durante los ~3 s de countdown el estado sigue siendo serve: un gatillo pulsado entonces lanza el toss — tossed=true y netLocalToss llegan al rival (su bola fantasma vuela de verdad) mientras MI bola queda congelada en la mano (holdLock + vel a cero cada frame). Al llegar a cero, el toss reanuda con velocidad (0,0,0): cae muerto, rescate de bola, saque desperdiciado y desincronización visual de ~3 s.',
    ],
    fix: 'Añadir if (this._netStart) return; en las ramas de saque de 9868 y 9963, igual que en 10006.',
  },
  {
    sev: 'MEDIO', id: 'H13', estado: 'ABIERTO',
    titulo: 'live-service: state/event sin verificación de propiedad — cualquier socket inyecta estado en cualquier canal',
    donde: 'mini-services/live-service/index.ts:103-112 (publish en 79-96; gemelas idénticas en staging-v36207/v36209 y release-v36209)',
    evidencia: [
      "socket.on('state', (matchId, state) => {",
      "  const ch = channels.get(matchId);",
      "  if (!ch) return;                 // sin comprobar matchId === hosting",
      "publish:92  channels.set(matchId, …)  // incondicional → secuestro de matchId ajeno",
    ],
    porque: [
      'El relay está expuesto públicamente (cors origin "*") y en state/event nunca se comprueba que el socket sea el anfitrión del canal: cualquier cliente puede falsificar el estado de la partida de otro o inyectar eventos — un match-end falso cierra el canal del rival. Y publish con un matchId ajeno sobrescribe el canal existente (secuestro de metadatos).',
    ],
    fix: 'En state/event exigir matchId === hosting; en publish, rechazar si el canal existe y el dueño original es otro socket. Aplicar en las 4 copias idénticas (ver N1).',
  },
  {
    sev: 'MEDIO', id: 'H14', estado: 'ABIERTO',
    titulo: 'live-service: watch sin leaveWatch previo — contadores de espectadores hinchados y salas fantasma',
    donde: 'mini-services/live-service/index.ts:125-135 (leaveWatch existe en 144-153, cableado solo a leave-watch y disconnect)',
    evidencia: [
      "socket.on('watch', (matchId, ack) => {",
      "  watching = matchId;               // ← sin leaveWatch() del canal anterior",
      "  socket.join(`live:${matchId}`); ch.viewers++;",
    ],
    porque: [
      'Si un mismo socket hace watch(A) y luego watch(B), el contador de A queda incrementado para siempre y el socket permanece en la sala live:A recibiendo estados fantasma. Un watch doble del mismo canal infla viewers a 2 con un solo espectador. La guía pública /api/channels muestra cifras falsas.',
    ],
    fix: 'Primera línea de watch: leaveWatch() (ya existe y es idempotente) y no re-incrementar si matchId === watching. Aplicar en las 4 copias idénticas (ver N1).',
  },
  {
    sev: 'MEDIO', id: 'H15', estado: 'PARCIAL',
    titulo: 'live-service: publish acepta matchId y meta sin validar tipo/longitud',
    donde: 'mini-services/live-service/index.ts:79-96 (validación parcial en 87; meta cruda en 94-97)',
    evidencia: [
      "87:  if (!matchId || typeof matchId !== 'string') return;   ← TIPO: validado desde r109 ✓",
      "94-97:  name: (meta && meta.name) || 'Partida en vivo'      // sin String() ni recorte",
      "  ← longitud SIN tope (matchId y meta)",
    ],
    porque: [
      'Estado hoy: la comprobación de TIPO de matchId existe, pero ni matchId ni meta.name/p1/p2/mode tienen tope de longitud ni normalización a string. Todo se guarda en el Map y se re-difunde a todos los clientes en cada channels-updated, con maxHttpBufferSize (1e6) como único límite.',
    ],
    fix: 'matchId con regex /^[A-Za-z0-9_-]{6,64}$/ y name/p1/p2/mode como String(x).slice(0, N) con N acotado (24/24/24/16). Aplicar en las 4 copias (ver N1).',
  },
  {
    sev: 'MEDIO', id: 'H16', estado: 'CERRADO',
    titulo: 'API presence: pid sin longitud máxima — amplificación de respuesta y memoria',
    donde: 'CERRADO en producción: scripts/worker-tele/worker.js:447-449 · PENDIENTE en la gemela QA: src/app/api/presence/route.ts:50',
    evidencia: [
      "worker.js:447-449:  const pidOk = /^[a-zA-Z0-9-]{4,32}$/   ← tope 32 chars + whitelist",
      "  aplicado en POST presencia (:488), POST invita (:544) y GET invita (:568)",
      "worker.js:458: cuerpo social limitado a 4096 B",
      "route.ts:50:  if (pid.length < 6) { … }        // gemela QA: SOLO mínimo, sin máximo",
    ],
    porque: [
      'La API que vive en PRODUCCIÓN (el worker de telemetría de Cloudflare, donde están los datos reales) impone hoy whitelist y tope de 32 caracteres al pid, más tope de cuerpo de 4096 B en la capa social: el hallazgo de amplificación está cerrado donde importa. La ruta de desarrollo de Next.js (gemela QA, explícitamente de desarrollo según el propio informe r109) conserva el patrón antiguo de solo-mínimo.',
    ],
    fix: 'Pendiente de higiene (no riesgo): replicar el saneo en route.ts si la gemela QA se vuelve a usar como receptor.',
  },
  {
    sev: 'BAJO', id: 'H17', estado: 'CERRADO',
    titulo: 'API invite: de/para sin tope de longitud (mismo patrón que presence)',
    donde: 'CERRADO en producción: scripts/worker-tele/worker.js:543-544 y 562 · PENDIENTE en la gemela QA: src/app/api/invite/route.ts:34',
    evidencia: [
      "worker.js:543-544:  de y para pasan por pidOk (whitelist + tope 32)",
      "worker.js:543/562:  code con texto(…,12) y deN con texto(…,20)   ← topes correctos",
      "route.ts:34:  if (de.length < 6 || para.length < 6 || sala.length !== 5 …)   // solo mínimos",
    ],
    porque: [
      'Misma resolución que H16: la API de invitaciones de PRODUCCIÓN sanea de/para con la whitelist de pidOk y recorta code y deN; la gemela QA de Next.js conserva los mínimos sin topes (sin riesgo real: receptor de desarrollo).',
    ],
    fix: 'Pendiente de higiene: replicar en route.ts si la gemela QA vuelve a usarse.',
  },
  {
    sev: 'BAJO', id: 'H18', estado: 'PARCIAL',
    titulo: 'API telemetria: CORS abierto + DELETE sin autenticación',
    donde: 'DELETE CERRADO en producción: worker.js:1318-1321 · CORS abierto por diseño: worker.js:74-78 · gemela QA sin token: route.ts:370',
    evidencia: [
      "worker.js:1318-1321 (producción):",
      "  if (metodo === \"DELETE\") { if (!claveOk(url, request, env)) return json({…403}) … }",
      "worker.js:74-78:  \"Access-Control-Allow-Origin\": \"*\"   ← sigue abierto",
      "route.ts:370 (QA):  export async function DELETE(req)   // sin ?clave ni token",
    ],
    porque: [
      'La mitad peligrosa del hallazgo está cerrada en producción: el DELETE de purga del worker exige hoy la clave de lectura (403 sin ella), coherente con el contrato de la cabecera del worker. El CORS abierto se mantiene por diseño: el cliente público del juego envía los lotes con sendBeacon/fetch text/plain y el latido es público sin detalle, así que restringir el origen rompería clientes legítimos sin añadir protección real. La gemela QA de Next.js sigue sin token en DELETE (receptor de desarrollo).',
    ],
    fix: 'Nada urgente en producción. Higiene opcional: token en el DELETE de route.ts si la gemela QA vuelve a exponerse.',
  },
  {
    sev: 'BAJO', id: 'H11', estado: 'RETIRADO',
    titulo: 'Los tres simuladores no reproducen la rama de APOYO (mesaEnter) de la física real',
    donde: 'Cobertura REAL ya existente al auditarse: scripts/arnes_anti_robotico_r102.mjs:40-77 + test_fisica_c05 escenario 7',
    evidencia: [
      "arnes_anti_robotico_r102.mjs:25-26 importa el stepPhysics REAL de c05",
      "A1-A4 (40-77): conduce mesaEnter y aserta b.__ppMesa > 0.5 (:52), rodadura con efecto (57-71)",
      "test_fisica_c05.mjs:189-216 (escenario 7 «stepPhysics.apoyoRodadura»)",
      "test_fisica_p0_r86/r87: acunar/despegue __ppRest (apoyo en pala)",
    ],
    porque: [
      'La carencia de cobertura que r109 documentó no se sostiene: el arnés anti-robótico r102 (anterior a r109) conduce la física REAL por la rama de apoyo en mesa y los arneses P0/c05 cubren el apoyo en pala. La divergencia sim/real de los tres predictores (rebotan al 93,5% donde la bola real se posa con impact < mesaEnter) sigue existiendo como matiz de precisión de la IA, pero NO como carencia de cobertura de regresión: el hallazgo original se retira.',
    ],
    fix: 'Sin acción. Si se quiere cerrar también el matiz sim/real: replicar el umbral mesaEnter en los predictores (mejora de precisión de la IA, no de cobertura).',
  },
  {
    sev: 'BAJO', id: 'N1', estado: 'ABIERTO',
    titulo: 'NUEVO · live-service replicado en 4 copias idénticas: riesgo de deriva de mantenimiento',
    donde: 'mini-services/live-service/index.ts · scripts/staging-v36207/live-service/server.mjs · scripts/staging-v36209/live-service/server.mjs · scripts/release-v36209/server.mjs',
    evidencia: [
      "diff entre las 4 copias: VACÍO hoy (lógica idéntica, incluidos los defectos H13/H14)",
      "cualquier corrección futura debe aterrizar en LAS 4, o convivirán versiones divergentes",
    ],
    porque: [
      'El relay de CRAZY TV existe en cuatro copias con lógica idéntica (verificado por diff hoy). Hoy es un alivio (arreglar una es arreglar todas), pero es una bomba de mantenimiento: una corrección aplicada a una sola copia produce silenciosamente versiones divergentes del mismo servicio. El repositorio ya sufrió este patrón con los sellos de versión (31 arneses caducados).',
    ],
    fix: 'Elegir UNA fuente de verdad (mini-services/) y hacer que staging/release se generen por empaquetado (patrón build_game.py), o al menos un check de igualdad en la batería que falle si las 4 copias divergen.',
  },
];

// Tabla-resumen del estado de los 18 hallazgos r109 + 1 nuevo
const estadoRows = [
  ['H1', 'ALTO', 'ABIERTO', 'HIT portalizado con velocidad cero — sin cambios'],
  ['H2', 'MEDIO', 'ABIERTO', 'HANDOFF sin guardia — sin cambios'],
  ['H3', 'MEDIO', 'ABIERTO', 'Watchdog v1/v2 — sin cambios'],
  ['H4', 'MEDIO', 'ABIERTO', 'remapCause condicional — sin cambios'],
  ['H5', 'MEDIO', 'ABIERTO', 'visDelta sin llamador — re-verificado repo-wide'],
  ['H6', 'MEDIO', 'ABIERTO', 'SNAP sin markSent — sin cambios'],
  ['H7', 'MEDIO', 'ABIERTO', '_flushEvents en túnel — sin cambios'],
  ['H8', 'MEDIO', 'ABIERTO', 'Aces con rallyHits===1 (c06 + espejo c12) — sin cambios'],
  ['H9', 'MEDIO', 'ABIERTO', 'mishit sin spin — sin cambios'],
  ['H10', 'MEDIO', 'ABIERTO', 'Apoyo sin bladeCenterUp — sin cambios'],
  ['H11', 'BAJO', 'RETIRADO', 'La cobertura existía (arnés r102 + c05 + P0) — hallazgo sin sustento'],
  ['H12', 'MEDIO', 'ABIERTO', 'Gatillo sin guardia de countdown — sin cambios'],
  ['H13', 'MEDIO', 'ABIERTO', 'live-service: inyección de estado — sin cambios'],
  ['H14', 'MEDIO', 'ABIERTO', 'live-service: watch hinchado — sin cambios'],
  ['H15', 'MEDIO', 'PARCIAL', 'Tipo de matchId validado ✓; longitudes sin tope'],
  ['H16', 'MEDIO', 'CERRADO', 'pidOk 4-32 + cuerpo 4096 B en el worker de producción; gemela QA pendiente de higiene'],
  ['H17', 'BAJO', 'CERRADO', 'de/para con pidOk y topes en el worker; gemela QA pendiente de higiene'],
  ['H18', 'BAJO', 'PARCIAL', 'DELETE con clave en producción ✓; CORS abierto por diseño del cliente; gemela QA sin token'],
  ['N1', 'BAJO', 'ABIERTO', 'NUEVO: live-service ×4 copias idénticas — riesgo de deriva'],
];

const descartes = [
  ['Fórmula Catmull-Rom de _crSeg (c06:679-713)', 'Verificada término a término (t², t³, cabecera 2p1, factor 0,5) tras la corrección r100: correcta, y el fantasma p0 = 2K0−K1 hace que el ajuste centrípeto no encoge patas.'],
  ['Convención de spin en los botes', 'Los tres call sites pasan (vel, spin) idéntico; ux = vx + r·wz, uz = vz − r·wx es exactamente la velocidad del punto de contacto y el par Δω coincide con −(3/2r)·(ŷ×Δv): algebraicamente correcta.'],
  ['Substeps de stepPhysics', 'dt = 0 es identidad, dt enorme queda acotado a 96 subpasos, mesa/red detectan por cruce de segmento (sin túnel) y la condición de salida es correcta.'],
  ['Vectores temporales compartidos (c04)', 'Descartada la reentrancia: integraVuelo usa solo su banco _rk*, los simuladores usan _sv* privados, y los tmp vivos del barrido no son pisados por la única llamada anidada real (imán → solver). c06 blindó el alias contacto (r100).'],
  ['Filtro de Kalman de la pala', 'La innovación fuera de puerta renace con la medida y P ancha; dentro de puerta la varianza de proceso lava una medida mala en pocos ticks; la cuarentena corre antes y el renace usa la velocidad instantánea con techo.'],
  ['CCD bola↔pala', 'Barrido conservador 1-Lipschitz sin salto de superficie, límites de Newton con holgura (32 iteraciones), caso rasante con desviación ≤ 0,2 mm y doble golpe v2.29 cubierto por cooldown + guardia de velocidad relativa.'],
  ['Espejo de red (host −z / invitado +z)', 'Emisión espeja una vez, recepción solo re-ancla Y y el render aplica la pose espejada una vez: trazados todos los caminos (pose, bola, causa, skins), sin doble espejo ni espejo perdido (la única excepción direccional es H4).'],
  ['Lectura binaria de paquetes', 'decodePacket lanza RangeError en paquetes truncados, pero el único llamador en producción lo envuelve en try (r123): una llegada corrupta no tumba el frame. La codificación no puede desbordar (máx ~420 B).'],
  ['Reloj NTP y jitter buffer', 'Mediana de las 4 muestras de menor RTT, salto solo si el error supera 30 ms fuera de rallye, deslizamiento de 1 ms/s y guardia de RTT absurdo; buffer vacío devuelve −1 (los llamadores comprueban), congelado devuelve la última pose, autoDelay clampado a [40, 220] ms.'],
  ['JSON.parse en el cliente', 'Los 27 puntos revisados uno a uno están en try/catch (c00, c04, c06, c09, c09b, c09c, c11, c12, c13).'],
  ['IDs de DOM', 'Cruce completo: los 27 IDs buscados por getElementById existen en los wrappers HTML y sin duplicados; los scripts no-module no dependen de exports del módulo.'],
  ['Interceptor de storage de c00', 'Parche transparente de Storage.prototype.setItem que solo actúa en modo depuración; no intercepta lecturas y no colisiona con PeerJS ni three.js.'],
  ['Bucle animate y dtFis', 'dtFis clampado (fisMax 1/12, primer frame a 0,016), la dilatación solo se arma en game-over local (deliberado) y la bola tiene rescate NaN/anti-mundo.'],
  ['_bolaGuard', 'Los límites (7 m) son inalcanzables para una bola legítima incluso a smash máximo (26 m/s × 1/12 s ≈ 2,2 m por frame) y exenta los estados de tránsito: no come bolas legítimas.'],
  ['Ciclo de vida de la partida', 'Sin listeners ni intervalos por partida (los del constructor son de por vida del objeto), el resync diferido usa clearTimeout y guarda net.online; la desconexión re-viste la pala remota y apaga los poderes del rival.'],
  ['ChampLoader y escena', 'JSON corrupto → reintentos exponenciales + olas de recuperación + aviso (el campeonato no aparece, no rompe); id con regex anti-traversal; createRoom/Table/Ball se llaman una vez; decorados con dispose completo; skins de bola cooperan con la regla de un solo poder vivo.'],
  ['Assets y rutas', 'Regeneración byte-exacto del build; los 36 avisos automáticos de assets resultaron falsos positivos (imports eliminados al construir, rutas por concatenación como championships/<id>/assets/insignia.png, y cadenas dentro de comentarios); las 5 variantes del hall tienen sus 6 texturas; socket.io y tv.html existen para las 2 reescrituras del deploy.'],
];

// Verificaciones adicionales de la re-auditoría r111 (nuevas o re-anchadas hoy)
const descartesNuevos = [
  ['Delta de código r109→r111 (75 líneas en c00/c07/c12)', 'Revisado completo: bump de versión (c00), vigilante de destrucción de cristales cripto r110 (c07/c12 — pendientes() y FIN_PLAZO correctos, la llamada de c12 está guardada y el try cubre el frame) y recalibración del gobernador VR r111 (PERF_LS v2, barra dependiente de tasa, gobernador activo en rallye). Sin defectos nuevos.'],
  ['Placeholders y marcas pendientes (TODO/FIXME/XXX) en las 16 fuentes', '0 reales: los 72 hits del barrido son la palabra española «TODO» en comentarios y cadenas de UI («BORRAR TODO», «TODOS los ladrillos»).'],
  ['Copias public/game.html y pages-site/game.html', 'Idénticas salvo las 2 reescrituras DOCUMENTADAS de deploy_pages.py (src="/vendor/socket.io.min.js" → relativo; href="/tv.html" → relativo). El empaquetador aborta si una reescritura no cuadra: sin deriva posible.'],
  ['Contrato cliente↔worker de telemetría y social', 'COMPLETO: las 6 llamadas de c09c/c09b/c00/c12 (presencia POST/GET/lista, invita POST/GET/DELETE, ice GET, tele POST) existen en el worker con el mismo método y forma; el campo k:"inv" extra del cliente es ignorado por el worker (inofensivo). Cero 404 potenciales, cero divergencias de forma.'],
  ['Worker de producción crazypp-tele (r111-b)', 'Sintaxis OK; parche anti-cupo operativo (caché 60 s del latido/salud, purga de presencia 1/20 con COUNT filtrado por TTL); bindings verificados por API (DB→24ee07a2, CLAVE, TURN_API_TOKEN preservado vía keep_bindings); desplegado y verificado en producción el 21-11-2026.'],
  ['Incidente operativo del día (cupo D1 free tier)', 'Causa única y confirmada por SQL directo: límite diario de lecturas del free tier agotado (error 7500 → 1101 del worker). NO es un defecto de código: se recupera solo a las 00:00 UTC. El parche r111-b ya desplegado recorta ~90% el quemado del patrón LED del panel para que no se repita.'],
  ['Sincronización del repositorio', 'El local va POR DELANTE de origin/main (6 commits sin push, pendiente GIT_TOKEN desde r109-c): se audita el local, que es la versión más avanzada. La batería y el delta se ejecutaron contra HEAD (8a8d9b2).'],
];

const bateriasOk = [
  ['test_fisica.mjs', 'Golden de trayectorias (12 escenarios)', '0 desviaciones'],
  ['test_fisica_c05.mjs', 'Golden c05 (17 escenarios)', '17 OK · 0 fallos'],
  ['test_fisica_ittf.mjs', 'Norma ITTF §12.1 (botes)', '8 OK · 0 fallos'],
  ['test_fisica_p0_r86.mjs', 'Arnés P0 r86', '21 OK · 0 fallos'],
  ['test_fisica_p0_r87.mjs', 'Arnés P0 r87', '50 OK · 0 fallos'],
  ['test_red_nucleo.mjs', 'PPNET puro (códecs, reloj, jitter)', '60 OK · 0 fallos'],
  ['test_disparo_diferido_r99.mjs', 'Jinete sobre la curva (golpeo)', '15 OK · 0 fallos'],
  ['test_f1_decode_v36112.mjs', 'Decodificador F1', '6 OK · 0 fallos'],
  ['test_p4_ice_v36114.mjs', 'ICE/TURN de red', '21 OK · 0 fallos'],
];

const bateriasFallidas = [
  ['test_r29…r32, r38…r41, r43, r45 (10)', 'Sellos de versión/fase/tamaño caducados (esperan 3.6.129-3.6.157 y FASE 160; el juego está en 3.6.209-SDK6)', 'CADUCADOS'],
  ['test_r21, r23, r24, r25, r26, r26b, r27 (7)', 'Expectativas de comportamiento cambiado intencionalmente (candado r109 con migración, FORO3D desbloqueado, rejilla de 5 halls, constantes de poderes movidas a config)', 'CADUCADOS'],
  ['test_r28 (1)', 'Patrones de código de la bola en salones (guard de _elecRompe) tras el refactor r109 de cristales', 'CADUCADO · revisar al re-anclar'],
  ['qa_net_unit_v3628 (1)', 'Exige ida y vuelta del códec con error < 1e-9; el códec vigente PROTO 2 es CUANTIZADO por diseño (precisión de milímetros)', 'CADUCADO por diseño'],
  ['test_p4_selfcheck, p4_ver_mismatch (2)', 'Detalles de UI de la era P4 (prioridad de fila del self-check, wrapText del panel de mismatch)', 'CADUCADOS probables'],
  ['test_cadena_r91, r33, r34, r35, r36, r37 (6)', 'Crash en el arranque del arnés (marco de código de Bun; dependencias/harnesses de su era) — re-verificado hoy: mismo modo de fallo', 'SIN EJECUTAR'],
  ['test_m7e_persistencia (1)', 'ReferenceError: CONFIG_TORNEOS — el arnés extrae c11 a /tmp e importa solo: la constante vive en c02 y el juego real la tiene (27 apariciones en el bundle)', 'ARTEFACTO DEL ARNÉS'],
  ['test_worker_r169, test_zip_editor (2)', 'Dependen de rutas eliminadas en la limpieza r109-b (upload/scripts/worker-tele/, scripts/editor_src/)', 'DEPENDENCIA ELIMINADA'],
  ['test_ai_returns.py (1)', 'Arnés asíncrono Python; traceback en runtime (dependencia de entorno/red)', 'SIN EJECUTAR'],
];

const estructura = [
  ['Sintaxis (node --check por fichero, como módulo)', '16/16 ficheros OK (re-ejecutado hoy) · worker y c09b/c09c también OK'],
  ['Colisiones de declaraciones top-level (ámbito compartido único)', '0 colisiones — sin cambios desde r109 (el único delta es el vigilante r110 y el gobernador r111, sin nombres nuevos)'],
  ['Imports entre subsistemas', 'Todos los nombres importados existen: 0 rotos (delta r109→r111 no añade exports)'],
  ['Externales del bundle (THREE, GLTFLoader, RoomEnvironment)', 'Vivos via importmap → CDN jsdelivr three@0.170.0 (pinnado)'],
  ['Regeneración del build (build_game.py)', 'BYTE-EXACTO contra el golden: public/game.html sha256 a627bed1… = src/game/GOLDEN_SHA256.txt (re-anclado en el bump v3.6.209)'],
  ['Versión única (c00:3260 vs badge vs releases)', '3.6.209-SDK6 coherente (VERSION.json, sello c00, zips release v36209)'],
  ['Copias del juego (public/ vs pages-site/)', 'Idénticas salvo las 2 reescrituras documentadas del empaquetador (socket.io y tv.html relativos) — aborta si no cuadran'],
  ['Contrato cliente↔worker (social, ICE, telemetría)', 'COMPLETO: 6 llamadas del cliente cubiertas por el worker con método y forma exactos; 0 divergencias'],
];

module.exports = { findings, estadoRows, descartes, descartesNuevos, bateriasOk, bateriasFallidas, estructura };
