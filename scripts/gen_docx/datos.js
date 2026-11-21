// Datos de la auditoría de calidad — CRAZY PING PONG r109 (669a08e, 21-11-2026)
// Todas las cifras y citas proceden de la verificación real del 21-11-2026.

const findings = [
  {
    sev: 'ALTO', id: 'H1',
    titulo: 'Portal de Duelos Locos online: el HIT del golpe portalizado viaja con velocidad (0,0,0)',
    donde: 'c12_pingponggame.js:14483-14485 + 19030/19049 · c09_red_netlink.js:1922-1924 · c09b_red_nucleo.js:696-697',
    evidencia: [
      "c12:14483-14485 (bloque 5.55, _portalProcesa):",
      "  this._portalSalVel.copy(newV);",
      "  b.vel.set(0, 0, 0);                   // congelada (spin CONSERVADO, spec)",
      "  b.ppTransito = true;",
      "c12:19049-19052 (bloque 5.6, DESPUÉS): if (this.net.online && this._localHit)",
      "  → c09:1922-1924 envía v: this._velNet(g.ball.vel)  ← ya congelada a cero",
    ],
    porque: [
      'El bloque 5.55 (portaliza la bola) se ejecuta en el mismo frame ANTES del bloque 5.6 (envío del HIT), y _portalProcesa congela ball.vel a cero justo en el frame en que sendHit la lee. El comentario del envío promete que «la trayectoria viaja en el propio HIT», pero la orden de ejecución lo hace imposible. El validador de PPNET (§12) solo comprueba techo de velocidad (sp <= MAX_BALL_SPEED), así que un vector cero pasa sin rechazo; en el rival, el fantasma nace parado en el aire, cae por gravedad en su mitad y su árbitro puede cantar bote(s) → CLAIM de un punto fantasma durante el tránsito de ~1 s, seguido de un BALL_HANDOFF tardío que choca contra el punto ya reclamado (resync).',
      'Impacto: cada golpe portalizado en un duelo online (el portal es armable por ambos lados en Duelos Locos) produce una bola congelada ~1 s, un salto visual y riesgo de punto/CLAIM alterado. Es el único hallazgo con efecto directo y visible en partidas online normales.',
    ],
    fix: 'Enviar la velocidad de salida real: en _portalProcesa guardar this._portalEnvioVel = newV (y posición _portalTmpC) y usarlos en el sendHit del bloque 5.6 cuando ppTransito esté activo; o alternativamente ejecutar la sección 5.55 DESPUÉS de la 5.6 (portalizar tras el envío, como ya hace la 5.5 con el enderezado). Verificado por lectura directa del código (el auditor principal re-comprobó las tres piezas).',
  },
  {
    sev: 'MEDIO', id: 'H2',
    titulo: 'HANDOFF sin guardia de estado (la rama HIT sí la tiene)',
    donde: 'c09_red_netlink.js:2302 (guardia de la rama HIT en 2225-2228)',
    evidencia: [
      "rama HIT (2225-2228):",
      "  const stG = g.rules.state;",
      "  if (stG !== 'rally' && !(stG === 'serve' && (ev.kind === 1 || ev.kind === 2))) return;",
      "rama HANDOFF (2302):  if (ev.t === PPNET.VP.EV.HANDOFF) {   ← sin guardia",
    ],
    porque: [
      'La guardia de estado se añadió en r122 SOLO a la rama HIT; el HANDOFF se quedó sin ella. Un HANDOFF con id nuevo que llegue atrasado (canal reliable encolado; el dedupe _seenEv solo descarta ids ya vistos) se aplica en estado de punto o de saque: onHandoff pone state=auth/mine=true y las ramas smooth/snap copian la posición en g.ball.pos — teletransporte de la bola retenida del saque y robo de autoridad mientras el rival lanza.',
    ],
    fix: 'Replicar la guardia: en ev.t === HANDOFF, if (g.rules.state !== \'rally\') return; (un HANDOFF solo tiene sentido en rallye vivo). Revisar por la misma lupa _applyRemoteClaim (2026), que llama forcePoint sin comprobar estado.',
  },
  {
    sev: 'MEDIO', id: 'H3',
    titulo: 'Watchdog de silencio inaccesible en v1 y ciego a la muerte del canal fast',
    donde: 'c09_red_netlink.js:1467 (gate de v1 en 1394)',
    evidencia: [
      "1394:  if (this.v2 !== 'ok') { this.tick(dt); return; }   // v1 sale ANTES del watchdog",
      "1467:  if (this._lastRelAt && now - this._lastRelAt > SILENCIO && this._lastFastAt &&",
      "           now - this._lastFastAt > SILENCIO) {           // exige que rel Y fast estén mudos",
    ],
    porque: [
      'En modo v1 (túnel honesto) el watchdog nunca corre: si el rival muere sin cierre limpio (app matada, SCTP sin FIN), online queda en true indefinidamente y solo el evento conn close —que puede tardar minutos— saca del punto. En v2, la condición AND exige que el canal reliable Y el fast estén ambos mudos: si solo muere el DataChannel fast (dc.onclose con transporte vivo), la partida queda congelada (avatar estático, sin fin) mientras rel siga respirando.',
    ],
    fix: 'Mover el watchdog antes del gate de v2 (en v1, usar la frescura de paquetes del túnel) y en v2 disparar también con now - this._lastFastAt > SILENCIO a secas cuando se esperan poses.',
  },
  {
    sev: 'MEDIO', id: 'H4',
    titulo: 'remapCause del CLAIM solo invierte para el invitado: el anfitrión lee las causas del rival sin espejo',
    donde: 'c09_red_netlink.js:2026-2027',
    evidencia: [
      "g.processIntents(g.rules.forcePoint(wMapped,",
      "  NetLink.remapCause(m.c, this.role === 'guest'), m.r));   // host → forGuest=false",
    ],
    porque: [
      'La causa del punto viaja en perspectiva del EMISOR (handleEvents produce own_you/own_opp/…relativos a quien detecta). El remapeo se aplica solo si YO soy invitado, pero el claim SIEMPRE viene del otro lado: cuando el anfitrión aplica el claim de un invitado, el own_you del rival («la culpa fue del rival») se muestra tal cual como «culpa tuya» del anfitrión. El ganador (wMapped) llega bien; el daño es el texto del punto y la megafonía.',
    ],
    fix: 'En _applyRemoteClaim usar siempre NetLink.remapCause(m.c, true): la causa del claim siempre procede del extremo contrario.',
  },
  {
    sev: 'MEDIO', id: 'H5',
    titulo: 'visDelta() es código muerto: la absorción de salto y el catch-up nunca se aplican',
    donde: 'c09_red_netlink.js:2377 (cero llamadores en todo src/)',
    evidencia: [
      "visDelta(dt) {                    // solo definición; c12 nunca la llama",
      "  if (this._visOff && this._visOff.t > 0) { ... }",
      "  if (this._visOffMs > 0) { const frac = this._visOffMs / PPNET.VP.CATCHUP_MS; ...",
    ],
    porque: [
      'La función que absorbe el salto visual del HANDOFF smooth (2314-2315 fija _visOff) y el catch-up (_visOffMs = CATCHUP_MS en 2287) no tiene ningún llamador en el animate de c12: la bola teletransporta visualmente en cada handoff smooth, contrario a la spec §8, y los campos quedan asignados para siempre sin efecto.',
    ],
    fix: 'Llamar visDelta(dt) en el render de la bola de c12 y aplicar el desplazamiento al mesh, o retirar la feature y sus campos si se decide que el snap directo es aceptable (decisión del dueño).',
  },
  {
    sev: 'MEDIO', id: 'H6',
    titulo: 'Paquete SNAP sin clock.markSent: sus ecos jamás producen muestra NTP',
    donde: 'c09_red_netlink.js:1501 (ruta de pose correcta en 1541)',
    evidencia: [
      "const pk = { seq: ..., sendTime: now, ... };",
      "this._seq = pk.seq;",
      "const n = PPNET.encodePacket(this._txBuf, pk);",
      "if (n) this._fastSend(this._txOut(n), now);      // SIN this._clock.markSent(now)",
    ],
    porque: [
      'El rival ecoa el sendTime de TODO paquete recibido, pero al volver el eco el SNAP no tiene sello de envío (_fullFromEcho no lo encuentra) y onPacket retorna antes de refinar el reloj. Con bola propia (SNAP a 30 Hz + pose a 60 Hz) cerca de un tercio de las llegadas no refinan el NTP — justo mientras la bola propia exige tHit preciso para el handoff. El jitter sí se actualiza (se calcula antes del return), lo que hace el fallo más silencioso.',
    ],
    fix: 'Añadir this._clock.markSent(now) en la rama SNAP de _sendFast (y en cualquier envío directo futuro).',
  },
  {
    sev: 'MEDIO', id: 'H7',
    titulo: '_flushEvents no envía nunca en modo túnel: HIT/HANDOFF sin flush inmediato',
    donde: 'c09_red_netlink.js:1560',
    evidencia: [
      "_flushEvents(now) {",
      "  if (!this._pend.length || !this._fast || !this._fastOpen) return;  // túnel: _fastOpen=false",
    ],
    porque: [
      'En modo túnel (_tunnel=true) los DataChannels propios nunca abrieron, así que _fastOpen es falso por construcción y los flushes inmediatos de netLocalHit/netLocalToss/watchOwnCross son no-ops: los eventos críticos esperan al próximo tick de pose (túnel a 30 Hz: hasta ~33 ms extra de latencia en CADA golpe, pese a que el comentario promete envío «inmediato, sin esperar tick»). No hay pérdida (viajan en el paquete de pose), solo latencia sistemática del modo de emergencia.',
    ],
    fix: 'Usar el mismo criterio de salida que _sendFast: if (this._tunnel ? !(this.conn && this.conn.open) : (!this._fast || !this._fastOpen)) return; y delegar en _fastSend, que ya gestiona el túnel.',
  },
  {
    sev: 'MEDIO', id: 'H8',
    titulo: 'Contador de aces desplazado: un ace real nunca cuenta y un fallo del receptor sí',
    donde: 'c06_logros_stats_ia_rival.js:83 (registerPaddleHit en 310-311)',
    evidencia: [
      "// SAQUE DIRECTO (ace): solo tocó la bola el sacador",
      "if (rallyHits === 1) {",
      "  this.data.aces++;",
      // registerPaddleHit: "if (this.state !== 'rally') return [];"
    ],
    porque: [
      'El golpe de saque nunca se registra en rallyHits: el evento paddle del saque se marca consumed y beginServeRally corre antes de rules.handleEvents, además registerPaddleHit rechaza todo con estado distinto de rally. Un ace verdadero (el rival no toca la bola) termina con rallyHits = 0 y no cuenta; en cambio un punto donde el rival toca UNA vez y luego falla queda con rallyHits = 1 y cuenta como ace — la condición está invertida respecto a su propio comentario. Alimenta el logro aces10, el hito mesa_lock_aces5 y la puerta del dojo (5 aces).',
    ],
    fix: 'Cambiar la condición a rallyHits === 0 (mínimo riesgo, no toca bestRally ni maraton); alternativamente que beginServeRally haga this.rallyHits = 1 (semánticamente fiel a la docstring, pero desplaza +1 los contadores de rallye). Verificado por lectura directa.',
  },
  {
    sev: 'MEDIO', id: 'H9',
    titulo: 'El golpe torpe (mishit) pierde el spin al aplicarse el disparo diferido',
    donde: 'c06_logros_stats_ia_rival.js:1509 (payload en 1673, copia en 1722)',
    evidencia: [
      "const _mv = this.mishit(ball, toca);",
      "this._preparaDisparo(ball, _mv, cx, cy, cz);        // sin el 6º argumento: spin",
      "…  spin: spin ? spin.clone() : new THREE.Vector3(),  // 1673 → d.spin = (0,0,0)",
      "…  b.spin.copy(d.spin);                             // 1722 → borra el spin",
    ],
    porque: [
      'mishit fija el giro del toque torpe en el mismo frame (spin aleatorio visible con Magnus activo), pero _preparaDisparo se llama sin el argumento de spin: el payload nace a cero y _aplicaDisparo lo copia encima al aplicar el disparo diferido (hasta 0,75 s después). La bola vuela todo el periodo diferido curvándose y al contacto visual el giro desaparece de golpe. El camino limpio sí pasa shotSpin — es un refactor r99 incompleto en la única rama torpe.',
    ],
    fix: 'this._preparaDisparo(ball, _mv, cx, cy, cz, ball.spin) tras mishit (el payload ya clona). Cambio aislado al fallo decidido de la IA; el golden de física no lo ve.',
  },
  {
    sev: 'MEDIO', id: 'H10',
    titulo: 'La velocidad de superficie del apoyo omite bladeCenterUp: palanca de muñeca medida desde el punto equivocado',
    donde: 'c05_colisiones_ia_golpeo.js:853-858',
    evidencia: [
      "const rCx = ball.__ppRestLx || 0, rCy = ball.__ppRestDy || 0;",
      "_rsOff.set(0, 0, 0).addScaledVector(rp.right, rCx).addScaledVector(rp.up, rCy);",
      "_rsSurf.copy(rp.vel);",
      "if (rp.omega && rp.omega.lengthSq() > 1e-8) { _rsOm.copy(rp.omega).cross(_rsOff); _rsSurf.add(_rsOm); }",
    ],
    porque: [
      '__ppRestLx/Dy se capturan respecto al CENTRO DE LA HOJA (ccdC1 = padPos + ipUp·bladeCenterUp), pero rp.vel es la velocidad del punto seguido (el grip) y rp.omega la angular del cuerpo: la velocidad real del punto de contacto es rp.vel + omega x (right·rCx + up·(bladeCenterUp + rCy)) — falta el término up·0,14. El propio despegue por swing sí lo incluye, lo que confirma el olvido. Con una rotación de muñeca de 8 rad/s el error llega a ~1,1 m/s: el estado de fricción (estática frente a cinética) se decide con un deslizamiento falso y girar la muñeca despacio NO arrastra la bola, rompiendo la promesa del bloque r103 §6; la migración del punto de apoyo usa el mismo vector corrompido.',
    ],
    fix: '_rsOff…addScaledVector(rp.up, DIMS.bladeCenterUp + rCy) (y mismo criterio en el re-proyecto de posición, que ya está bien). Los arneses golden no cubren apoyo+muñeca, así que el cambio no debería mover las trayectorias golden.',
  },
  {
    sev: 'BAJO', id: 'H11',
    titulo: 'Los tres simuladores no reproducen la rama de APOYO (mesaEnter) de la física real',
    donde: 'c05_colisiones_ia_golpeo.js:1016, 1240, 1093 (rama real en 526-528)',
    evidencia: [
      "real (526-528):  if (impact < SOLVER_TUNE.mesaEnter) { ball.__ppMesa = 1e-6; vel.y = 0; }",
      "predictores:     bounceOnTable(vel, spin, -vel.y);   // siempre impulso, rest 0,935",
    ],
    porque: [
      'Los comentarios doctrinales dicen que los tres simuladores predicen con la física real, pero ante impacto vertical inferior a 1,0 m/s la bola real entra en apoyo (se posa y rueda) mientras los predictores la rebotan al 93,5%. Ante una dejada o push muy suave, predictStrike fabrica un segundo bote simulado (candidato de golpeo a ~0,8 m o urgent) que en la mesa real nunca ocurre — la IA se prepara para una bola que se queda rodando y falla a la vista. Divergencia sim/real acotada: no rompe el árbitro ni el golden (las trayectorias de referencia usan impactos mayores).',
    ],
    fix: 'Replicar el umbral en los tres simuladores (if (-vel.y < SOLVER_TUNE.mesaEnter) vel.y = 0) o al menos en predictStrike tras el bote propio.',
  },
  {
    sev: 'MEDIO', id: 'H12',
    titulo: 'El gatillo del saque ignora la cuenta atrás del MATCH_START (a diferencia de la ruta natural)',
    donde: 'c12_pingponggame.js:9868-9873 y 9963-9965 (ruta protegida: 10006)',
    evidencia: [
      "10006 (grip):    if (this.rules.state !== 'serve' || server !== 'player') return;",
      "                 if (this._netStart) return;   // r79: cuenta atrás en curso",
      "9868/9963 (gatillo): if (state === 'serve' && server === 'player' && !this.tossed …)",
      "                     { this.tossFromHand(this.ballHand, true); return; }   ← sin _netStart",
    ],
    porque: [
      'Durante los ~3 s de countdown el estado sigue siendo serve: un gatillo pulsado entonces pasa las guardias de las dos rutas del gatillo y lanza el toss — tossed=true y netLocalToss llegan al rival (su bola fantasma vuela de verdad) mientras MI bola queda congelada en la mano (holdLock + vel a cero cada frame). Al llegar a cero, el toss reanuda con velocidad (0,0,0): cae muerto, rescate de bola, saque desperdiciado y desincronización visual de ~3 s. La ruta natural (soltar el grip) sí está protegida — la inconsistencia demuestra que la guardia se olvidó en las dos rutas del gatillo.',
    ],
    fix: 'Añadir if (this._netStart) return; en las ramas de saque de 9868 y 9963, igual que en 10006.',
  },
  {
    sev: 'MEDIO', id: 'H13',
    titulo: 'live-service: state/event sin verificación de propiedad — cualquier socket inyecta estado en cualquier canal',
    donde: 'mini-services/live-service/index.ts:103-121 (publish en 79-96)',
    evidencia: [
      "socket.on('state', (matchId, state) => {",
      "  const ch = channels.get(matchId);",
      "  if (!ch) return;                 // sin comprobar matchId === hosting",
      "socket.on('event', (matchId, evt) => { … socket.to(`live:${matchId}`).emit('event', evt); …",
    ],
    porque: [
      'El relay está expuesto públicamente (cors origin "*") y en state/event nunca se comprueba que el socket sea el anfitrión del canal: cualquier cliente puede falsificar el estado de la partida de otro (los espectadores ven una partida tergiversada) o inyectar eventos — un match-end falso cierra el canal del rival. Además, publish con un matchId ajeno sobrescribe el canal existente (secuestro de metadatos) y el primer disconnect de los dos anfitriones borra el canal del legítimo.',
    ],
    fix: 'En state/event exigir matchId === hosting (o comparar socket.id con el hostSocketId del canal); en publish, rechazar si el canal existe y el dueño original es otro socket.',
  },
  {
    sev: 'MEDIO', id: 'H14',
    titulo: 'live-service: watch sin leaveWatch previo — contadores de espectadores hinchados y salas fantasma',
    donde: 'mini-services/live-service/index.ts:125-135',
    evidencia: [
      "socket.on('watch', (matchId, ack) => {",
      "  const ch = channels.get(matchId); if (!ch) { … return; }",
      "  watching = matchId;               // ← sin leaveWatch() del canal anterior",
      "  socket.join(`live:${matchId}`); ch.viewers++;",
    ],
    porque: [
      'Si un mismo socket hace watch(A) y luego watch(B), el contador de A queda incrementado para siempre (leaveWatch ya no decrementa A porque watching apunta a B) y el socket permanece en la sala live:A recibiendo estados fantasma. Un watch doble del mismo canal infla viewers a 2 con un solo espectador. La guía pública /api/channels muestra cifras falsas.',
    ],
    fix: 'Primera línea de watch: leaveWatch() (ya existe y es idempotente) y no re-incrementar si matchId === watching.',
  },
  {
    sev: 'MEDIO', id: 'H15',
    titulo: 'live-service: publish acepta matchId y meta sin validar tipo/longitud',
    donde: 'mini-services/live-service/index.ts:79-96',
    evidencia: [
      "socket.on('publish', ({ matchId, meta } = {}) => {",
      "  if (!matchId || typeof matchId !== 'string') return;   // sin longitud ni caracteres",
      "  name: (meta && meta.name) || 'Partida en vivo',        // sin String() ni recorte",
    ],
    porque: [
      'matchId puede tener cualquier contenido y longitud, y meta.name/p1/p2/mode no se normalizan a string ni se recortan (un objeto o un mega-texto pasan tal cual). Todo se guarda en el Map y se re-difunde a todos los clientes en cada channels-updated, con maxHttpBufferSize (1e6) como único límite: un cliente malicioso infla memoria y ancho de banda de la guía.',
    ],
    fix: 'matchId con regex /^[A-Za-z0-9_-]{6,64}$/ y name/p1/p2/mode como String(x).slice(0, N) con N acotado (24/24/24/16).',
  },
  {
    sev: 'MEDIO', id: 'H16',
    titulo: 'API presence: pid sin longitud máxima — amplificación de respuesta y memoria',
    donde: 'src/app/api/presence/route.ts:49-51 (eco en 72-75)',
    evidencia: [
      "const pid = String(b.pid ?? \"\").replace(/[^A-Za-z0-9-]/g, \"\");",
      "if (pid.length < 6) { return … 400 }        // solo MÍNIMO, sin máximo",
      "eco: .map(([pid2, v]) => ({ pid: pid2, n: v.n, st: v.st, c: v.c }))",
    ],
    porque: [
      'Las rutas de App Router no imponen límite de cuerpo (telemetria sí se autocapara a 256 KB): un POST con un pid de cientos de KB se guarda como clave del Map y se devuelve íntegro en el campo jugadores a los otros clientes en cada latido de 20 s (amplificación de respuesta). El Map solo se poda por TTL de 70 s, sin tope de entradas.',
    ],
    fix: 'pid.slice(0, 64) tras el saneado (y rechazar si queda vacío); tope global del Map (p. ej. 500 entradas, caen las más viejas).',
  },
  {
    sev: 'BAJO', id: 'H17',
    titulo: 'API invite: de/para sin tope de longitud (mismo patrón que presence)',
    donde: 'src/app/api/invite/route.ts:29-34',
    evidencia: [
      "const de = String(b.de ?? \"\").replace(/[^A-Za-z0-9-]/g, \"\");",
      "const para = String(b.para ?? \"\").replace(/[^A-Za-z0-9-]/g, \"\");",
      "// sala y n SÍ están recortados (5 y 12); de/para solo tienen mínimo",
    ],
    porque: [
      'Entradas con para de gran tamaño viven 120 s en memoria (el cap de 5 invitaciones vivas es por destinatario, no global) y para se usa como clave de filtrado en cada POST de presence. Riesgo bajo (QA interno) pero el mismo patrón corregible de un vistazo.',
    ],
    fix: 'de.slice(0, 64) y para.slice(0, 64), igual que el pid de presence.',
  },
  {
    sev: 'BAJO', id: 'H18',
    titulo: 'API telemetria: CORS abierto + DELETE sin autenticación',
    donde: 'src/app/api/telemetria/route.ts:39-43 y 370-392',
    evidencia: [
      "const CORS = { \"Access-Control-Allow-Origin\": \"*\", … };",
      "export async function DELETE(req) {",
      "  const sid = req.nextUrl.searchParams.get(\"sid\");",
      "  const quedan = sid ? … : [];   // sin ?sid= → purga total",
    ],
    porque: [
      'Con Access-Control-Allow-Origin en GET/POST/DELETE, cualquier página web que visite el equipo puede purgar el histórico completo (DELETE sin sid borra todo) o leer el resumen. Mitigado: el receptor es explícitamente de desarrollo — en producción la telemetría va al worker de Cloudflare — pero si esta ruta se despliega tal cual, la purga queda abierta.',
    ],
    fix: 'Restringir el origen CORS al del juego local o exigir un token compartido en DELETE; en producción, ni exponer DELETE ni CORS abierto.',
  },
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
  ['test_r29…r32, r38…r41, r43, r45 (10)', 'Sellos de versión/fase/tamaño caducados (esperan 3.6.129-3.6.157 y FASE 160; el juego está en 3.6.207 y FASE 184)', 'CADUCADOS'],
  ['test_r21, r23, r24, r25, r26, r26b, r27 (7)', 'Expectativas de comportamiento cambiado intencionalmente (candado r109 con migración, FORO3D desbloqueado, rejilla de 5 halls, constantes de poderes movidas a config)', 'CADUCADOS'],
  ['test_r28 (1)', 'Patrones de código de la bola en salones (guard de _elecRompe) tras el refactor r109 de cristales', 'CADUCADO · revisar al re-anclar'],
  ['qa_net_unit_v3628 (1)', 'Exige ida y vuelta del códec con error < 1e-9; el códec vigente PROTO 2 es CUANTIZADO por diseño (precisión de milímetros)', 'CADUCADO por diseño'],
  ['test_p4_selfcheck, p4_ver_mismatch (2)', 'Detalles de UI de la era P4 (prioridad de fila del self-check, wrapText del panel de mismatch)', 'CADUCADOS probables'],
  ['test_cadena_r91, r33, r34, r35, r36, r37 (6)', 'Crash en el arranque del arnés (marco de código de Bun; dependencias/harnesses de su era)', 'SIN EJECUTAR'],
  ['test_m7e_persistencia (1)', 'ReferenceError: CONFIG_TORNEOS — el arnés extrae c11 a /tmp e importa solo: la constante vive en c02 y el juego real la tiene (27 apariciones en el bundle)', 'ARTEFACTO DEL ARNÉS'],
  ['test_worker_r169, test_zip_editor (2)', 'Dependen de rutas eliminadas en la limpieza r109-b (upload/scripts/worker-tele/, scripts/editor_src/)', 'DEPENDENCIA ELIMINADA'],
  ['test_ai_returns.py (1)', 'Arnés asíncrono Python; traceback en runtime (dependencia de entorno/red)', 'SIN EJECUTAR'],
];

const estructura = [
  ['Sintaxis (node --check por fichero, como módulo)', '16/16 ficheros OK'],
  ['Colisiones de declaraciones top-level (ámbito compartido único)', '0 colisiones en 16 ficheros'],
  ['Imports entre subsistemas (se eliminan al construir)', 'Todos los nombres importados existen en el fichero exportador: 0 rotos'],
  ['Externales del bundle (THREE, GLTFLoader, RoomEnvironment)', 'Vivos via importmap → CDN jsdelivr three@0.170.0 (pinnado)'],
  ['Regeneración del build (build_game.py)', 'BYTE-EXACTO contra el golden: 12.502.469 B · sha256 7c645570…'],
  ['Versión única (VERSION.json vs sellos c00/badge)', '3.6.207-SDK6 coherente'],
  ['Assets case-sensitive (GitHub Pages)', '5 variantes del hall con 6/6 texturas; socket.io y tv.html presentes; 36 avisos automáticos = falsos positivos (concatenaciones y comentarios)'],
];

module.exports = { findings, descartes, bateriasOk, bateriasFallidas, estructura };
