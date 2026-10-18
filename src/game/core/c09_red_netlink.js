class NetLink {
  constructor(game) {
    this.game = game;
    this.peer = null;
    this.conn = null;          // DataConnection
    this.call = null;          // MediaConnection (voz)
    this.micStream = null;
    this.remoteAudio = null;   // <audio autoplay> con la voz del rival
    this.role = null;          // 'host' | 'guest'
    this.status = 'off';       // off|creating|waiting|joining|online|error
    this.code = '';            // código de sala (propio o introducido)
    this.online = false;
    this.micOn = true;
    this.voiceState = 'off';   // off|asking|on|denied|error
    this.statusMsg = '';
    this.owner = 'host';       // quién simula la bola ('host'|'guest')
    this.remotePaddle = null;  // { p:[x,y,z], q:[x,y,z,w], t }
    this.remoteBall = null;    // { p:[x,y,z], v:[x,y,z], s:[x,y,z], t }
    this.remoteBallT = 0;
    this._outEvs = [];         // eventos locales pendientes de enviar
    this._inEvs = [];          // eventos del rival pendientes de aplicar
    this._pendingHits = [];    // golpeos del rival pendientes (host)
    this._sendAcc = 0;
    this._lastSyncKey = '';
    this._overKey = '';
    this._padPrev = null;      // v2.91: muestra anterior de la pala rival
    this._retryIds = 0;
    this._lastHitSent = 0;   // v2.51: marca temporal del último golpeo propio
    this._joinTO = null;     // v2.51: watchdog de unión
    // v2.25: paquete de PUNTO/LET pendiente de adjuntar al próximo sync
    // (el anfitrión lo captura en processIntents; send-once)
    this.lastPoint = null;   // { w:'player'|'ai', c:causa, rh:n }
    this.lastRetry = null;   // causa del LET (texto neutro)
  }

  available() { return typeof Peer !== 'undefined'; }

  static CODE_CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';   // sin 0/O/1/I/L
  static ROOM_PREFIX = 'ppxr3-';
  static TABLE_CZ = -1.6;   // DIMS.tableCenterZ (eje de giro del espejo)
  // v2.27: causas que provocan el "ohh" del público (antes un regex sobre el
  // texto; ahora claves — válido en ambos idiomas)
  static OHH_CAUSES = new Set([
    'let', 'serve_net', 'serve_net_touch', 'serve_out', 'net_stay', 'wall', 'out',
  ]);

  genCode() {
    let s = '';
    for (let i = 0; i < 5; i++) {
      s += NetLink.CODE_CHARS[Math.floor(Math.random() * NetLink.CODE_CHARS.length)];
    }
    return s;
  }

  mySide() { return this.role === 'host' ? 'host' : 'guest'; }
  oppSide() { return this.role === 'host' ? 'guest' : 'host'; }

  /* --- transformación de marcos: mi marco <-> marco del rival -----------
   * Rotación de 180° en Y alrededor del centro de la mesa: (x,z) -> (-x, -3.2-z).
   * Es una involución. v2.25: se aplica UNA sola vez y SOLO al RECIBIR —
   * se emite en crudo (posiciones locales) y el otro extremo la aplica al
   * pintar la pala rival, aplicar la bola por red y validar golpeos/botes.
   * v2.91 · ALTURA ANCLADA A LA MESA: la Y viaja RELATIVA AL TAPALETTE
   * (y - tableTopY) y el receptor la restituye con SU tapa (y + tableTopY).
   * Antes la Y cruzaba en crudo y cada instalación con su suelo del
   * guardian a distinta altura veía la bola del rival botar sobre una
   * «mesa fantasma» 10 cm por encima de la propia. */
  static posToNet(p) {
    const T = DIMS.tableTopY;
    return [-p.x, p.y - T, -3.2 - p.z];
  }
  static posFromNet(a, out) {
    const T = DIMS.tableTopY;
    out.set(-a[0], a[1] + T, -3.2 - a[2]);
    return out;
  }
  static vecToNet(v) { return [-v.x, v.y, -v.z]; }
  static vecFromNet(a, out) { out.set(-a[0], a[1], -a[2]); return out; }
  /** v2.25: helpers de EMISIÓN en crudo (THREE -> array plano). */
  static rawPos(p) { return [p.x, p.y, p.z]; }
  static rawQuat(q) { return [q.x, q.y, q.z, q.w]; }
  /** v2.25: el spin TAMBIÉN se espeja al recibir (pseudovector bajo giro
   *  propio de 180° en Y: (-x, y, -z)) — si no, el efecto Magnus curvaría
   *  la bola al revés en el marco del receptor. */
  static spinFromNet(a, out) { out.set(-a[0], a[1], -a[2]); return out; }

  /* v2.25 · REMAPEO DE CAUSAS por punto de vista. El anfitrión redacta la
   * causa del punto desde SU perspectiva ('tu rival' = el invitado). En el
   * invitado la frase debe contarme la historia INVERSA.
   * Pares exactos producidos por Rules (host-relativo <-> invitado): */
  static CAUSE_SWAP = [
    // v2.27: las causas viajan como CLAVES (neutras por idioma); aquí solo
    // se intercambian las que cambian de perspectiva (yo <-> mi rival).
    ['own_you', 'own_opp'],
    ['dbl_you', 'dbl_opp'],
    ['back_you', 'back_opp'],
    ['noret_you', 'noret_opp'],
  ];
  static remapCause(c, forGuest) {
    if (!forGuest || !c) return c || '';
    for (const [a, b] of NetLink.CAUSE_SWAP) {
      if (c === a) return b;
      if (c === b) return a;
    }
    return c;   // causas neutras (doble golpe, LET, saque fuera…)
  }
  static quatFromNet(a, out) {
    // v2.91 · CONJUGACIÓN COMPLETA por el espejo: q' = R ⊗ q ⊗ R⁻¹ con
    // R = giro de 180° en Y = (0,1,0,0). Antes sólo R ⊗ q: la orientación
    // llegaba mal girada (pala vertical vista horizontal/tumbada).
    out.set(a[0], a[1], a[2], a[3]);
    const RX = 0, RY = 1, RZ = 0, RW = 0;
    const qx = out.x, qy = out.y, qz = out.z, qw = out.w;
    // t = R ⊗ q
    const tx = RW * qx + RX * qw + RY * qz - RZ * qy;
    const ty = RW * qy - RX * qz + RY * qw + RZ * qx;
    const tz = RW * qz + RX * qy - RY * qx + RZ * qw;
    const tw = RW * qw - RX * qx - RY * qy - RZ * qz;
    // out = t ⊗ R⁻¹  (R⁻¹ = (0,-1,0,0): el 180° es su propia inversa)
    const ix = -RX, iy = -RY, iz = -RZ, iw = RW;
    out.set(
      tw * ix + tx * iw + ty * iz - tz * iy,
      tw * iy - tx * iz + ty * iw + tz * ix,
      tw * iz + tx * iy - ty * ix + tz * iw,
      tw * iw - tx * ix - ty * iy - tz * iz,
    );
    return out;
  }
  static quatToNet(q) {
    // v2.91: se envía el cuaternión VISUAL en crudo (q_grip ⊗ q_mount);
    // el receptor aplica la conjugación completa en quatFromNet.
    return [q.x, q.y, q.z, q.w];
  }

  /** v2.91 · La propiedad de la bola SIGUE AL SACADOR durante el saque:
   *  si saco YO, yo simulo (toss real + físicas + contacto propio); si
   *  saca el rival, sigo su emisión. Antes el dueño quedaba fijo en
   *  'host': el INVITADO no podía sacar — su lanzamiento era pisado en
   *  cada frame por la emisión atrasada del anfitrión y la bola se caía
   *  al suelo sin poder golpearla. */
  syncServeOwner() {
    if (!this.online || !this.game || !this.game.rules) return;
    const r = this.game.rules;
    if (r.state !== 'serve') return;
    // r.server está en perspectiva LOCAL ('player' = yo) en ambos roles:
    // el anfitrión manda su 'sv' y applySync lo remapea al invitado.
    const iServe = r.server === 'player';
    const want = iServe ? this.mySide() : this.oppSide();
    if (this.owner !== want) this.owner = want;
  }

  setStatus(st, msg) {
    this.status = st;
    if (msg !== undefined) this.statusMsg = msg || '';
    this.game?.onNetStatus?.();
  }

  /* ---------------- crear sala (anfitrión) ---------------- */
  hostRoom() {
    if (!this.available()) { this.setStatus('error', T('net_unavailable')); return; }
    // v2.24: guardia de re-entrada (evita destruir una sala que ya se está
    // creando si el evento llega duplicado o se insiste a cañón)
    if (this.status === 'creating' || this.status === 'waiting') return;
    this.teardown();
    this.role = 'host';
    this.code = this.genCode();
    this.setStatus('creating', T('status_creating'));
    // v2.25: micrófono TEMPRANO, en este gesto 2D del menú (fuera de VR).
    // Pedirlo en plena sesión XR provoca el cambio de ruta de audio de
    // Android en el casco y dejaba el WebAudio del juego mudo. Si se
    // deniega, se sigue sin voz (igual que antes).
    this.initVoice().catch(() => { /* sin voz, sin problema */ });
    this.openPeer(NetLink.ROOM_PREFIX + this.code, () => {
      this.setStatus('waiting', T('status_waiting', { c: this.code }));
    });
  }

  /* ---------------- unirse con código (invitado) ---------------- */
  joinRoom(code) {
    if (!this.available()) { this.setStatus('error', T('net_unavailable')); return; }
    if (this.status === 'joining' || this.status === 'online') return;   // v2.24
    this.teardown();
    this.role = 'guest';
    this.code = (code || '').toUpperCase().trim();
    if (!/^[A-Z0-9]{5}$/.test(this.code)) {
      this.setStatus('error', T('invalid_code'));
      return;
    }
    this.setStatus('joining', T('status_joining', { c: this.code }));
    // v2.51: watchdog — si la sala no responde en 15 s (código muerto u
    // ocupada), error claro en vez de quedarse en 'joining' para siempre.
    this._joinTO = window.setTimeout(() => {
      if (this.status === 'joining' && !this.online) {
        this.setStatus('error', T('room_not_found', { c: this.code }));
      }
    }, 15000);
    // v2.25: micrófono temprano (mismo motivo que en hostRoom)
    this.initVoice().catch(() => { /* sin voz, sin problema */ });
    this.openPeer(null, () => {
      const conn = this.peer.connect(NetLink.ROOM_PREFIX + this.code, { reliable: true });
      this.wireConn(conn);
    });
  }

  openPeer(id, onReady) {
    try {
      this.peer = id ? new Peer(id) : new Peer();
    } catch (e) {
      this.setStatus('error', T('net_fail', { m: e.message }));
      return;
    }
    this.peer.on('open', () => { this._retryIds = 0; onReady && onReady(); });
    this.peer.on('connection', (conn) => {     // lado anfitrión
      if (this.conn && this.conn.open) { conn.close(); return; }  // una sala = un rival
      this.wireConn(conn);
    });
    this.peer.on('call', (call) => {           // voz entrante (anfitrión)
      this.call = call;
      const answer = (stream) => {
        try { call.answer(stream || undefined); this.wireCall(call); }
        catch { try { call.answer(); this.wireCall(call); } catch { /* */ } }
      };
      if (this.micStream) answer(this.micStream);
      // v2.25: con tope — si el micro no responde, se responde igualmente
      // (con silencio) para que la voz del otro llegue
      else this.initVoiceWithCap().then(answer).catch(() => answer());
    });
    this.peer.on('error', (err) => {
      const t = err?.type || '';
      if (t === 'unavailable-id' && this.role === 'host' && this._retryIds < 4) {
        this._retryIds++;
        this.code = this.genCode();
        try { this.peer.destroy(); } catch { /* */ }
        this.peer = null;
        this.openPeer(NetLink.ROOM_PREFIX + this.code, () => {
          this.setStatus('waiting', T('status_waiting', { c: this.code }));
        });
        return;
      }
      if (t === 'peer-unavailable') {
        this.setStatus('error', T('room_not_found', { c: this.code }));
      } else if (t === 'network' || t === 'server-error' || t === 'socket-error') {
        this.setStatus('error', T('no_lobby_server'));
      } else if (this.status !== 'online') {
        this.setStatus('error', T('mj_error') + ': ' + t);
      }
    });
    this.peer.on('disconnected', () => {
      try { this.peer.reconnect(); } catch { /* */ }
    });
  }

  wireConn(conn) {
    this.conn = conn;
    conn.on('open', () => {
      this.online = true;
      this.owner = 'host';       // el saque inicial siempre es del anfitrión
      this.setStatus('online', T('opp_connected'));
      this.game?.startOnlineSession();
      this.game?.audio?.kick();  // v2.25: rescate de audio al abrir la sesión
      this.initVoice().catch(() => { /* sin voz, sin problema */ });
      if (this.role === 'guest' && this.peer) {
        // v2.25: la llamada de voz la INICIA EL INVITADO hacia el ID de la
        // sala (el anfitrión responde en peer.on('call')). Antes la iniciaba
        // el anfitrión hacia su PROPIO id: bucle consigo mismo y el rival
        // sin voz ni en un sentido ni en el otro. Con tope de micro: si
        // getUserMedia cuelga, se llama con el stream silencioso.
        this.initVoiceWithCap().then((stream) => {
          if (this.peer && this.online) {
            const c = this.peer.call(NetLink.ROOM_PREFIX + this.code, stream || undefined);
            if (c) this.wireCall(c);
          }
        });
      }
    });
    conn.on('data', (d) => this.onData(d));
    conn.on('close', () => this.onPeerGone(T('peer_gone')));
    conn.on('error', () => this.onPeerGone(T('conn_lost')));
  }

  wireCall(call) {
    call.on('stream', (remote) => {
      this.voiceState = 'on';
      try {
        if (!this.remoteAudio) {
          this.remoteAudio = document.createElement('audio');
          this.remoteAudio.autoplay = true;
          document.body.appendChild(this.remoteAudio);
        }
        this.remoteAudio.srcObject = remote;
        this.remoteAudio.play?.().catch(() => { /* */ });
      } catch { /* */ }
      // v2.25: al llegar la voz del rival el sistema puede haber re-enrutado
      // la salida (foco de audio de Android): rescate suave del WebAudio.
      this.game?.audio?.kick();
      this.game?.onNetStatus?.();
    });
    call.on('close', () => { if (this.voiceState === 'on') this.voiceState = 'off'; });
  }

  async initVoice() {
    if (this.micStream) return this.micStream;
    this.voiceState = 'asking';
    this.game?.onNetStatus?.();
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
        video: false,
      });
      this.micStream = stream;
      stream.getAudioTracks().forEach((t) => { t.enabled = this.micOn; });
      this.voiceState = 'on';
      this.game?.onNetStatus?.();
      return stream;
    } catch (e) {
      this.voiceState = 'denied';
      this.game?.onNetStatus?.();
      throw e;
    }
  }

  /** v2.25: stream SILENTE de respaldo (sin micrófono). Si getUserMedia se
   *  queda colgado o se deniega, la llamada igualmente se establece y la
   *  voz del RIVAL se oye (solo no se transmitirá la nuestra). */
  silentStream() {
    if (this._silent) return this._silent;
    try {
      const Ctor = window.AudioContext || window.webkitAudioContext;
      if (!Ctor) return null;
      const ctx = new Ctor();
      const dst = ctx.createMediaStreamDestination();
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      g.gain.value = 0;                     // silencio total
      osc.connect(g); g.connect(dst);
      osc.start();
      this._silent = dst.stream;
      return this._silent;
    } catch { return null; }
  }

  /** v2.25: initVoice con TOPE de 4 s. Algunos navegadores dejan
   *  getUserMedia colgado sin responder nunca: sin este tope, la llamada de
   *  voz no llegara a iniciarse jamás y nadie oirá a nadie. Al vencer el
   *  tope se sigue con el stream silencioso. */
  initVoiceWithCap() {
    return new Promise((resolve) => {
      let done = false;
      const finish = (s, st) => {
        if (done) return;
        done = true;
        window.clearTimeout(t);
        if (st) this.voiceState = st;
        this.game?.onNetStatus?.();
        resolve(s || this.silentStream());
      };
      const t = window.setTimeout(() => finish(this.micStream, this.micStream ? 'on' : 'error'), 4000);
      this.initVoice().then((s) => finish(s)).catch(() => finish(null, 'denied'));
    });
  }

  toggleMic() {
    this.micOn = !this.micOn;
    if (this.micStream) this.micStream.getAudioTracks().forEach((t) => { t.enabled = this.micOn; });
    return this.micOn;
  }

  send(msg) {
    try { if (this.conn && this.conn.open) this.conn.send(msg); } catch { /* */ }
  }

  /* --------------- bucle: emitir pose/bola/eventos/sync (20 Hz) --------------- */
  tick(dt) {
    if (!this.online) return;
    this._sendAcc += dt;
    if (this._sendAcc < 0.033) return;   // v2.91: 30 Hz (antes 20 — partida a trompicones)
    this._sendAcc = 0;
    const g = this.game;
    const pad = g.controllerPaddles[g.paddleHand];
    const pkt = { k: 'p', pad: null, b: null, e: null };
    if (pad?.active && g.grips[g.paddleHand]) {
      // v2.91 · Se envía el CENTRO DE LA PALETA y la orientación VISUAL
      // completa (q_grip ⊗ q_montura de la mano que la sostiene). Antes se
      // enviaba el punto de agarre en crudo y sin el giro de montura: el
      // receptor pintaba la pala del rival RODADA (vertical⇔horizontal) y
      // desplazada (origen de hoja vs origen de agarre).
      const hand = g.paddleHand;
      const gp = g.grips[hand];
      const mq = (g.paddleMounts[hand] && g.paddleMounts[hand].quaternion)
        || mountQuatFor(hand);
      if (!NetLink._sQ1) {
        NetLink._sQ1 = new THREE.Quaternion();
        NetLink._sV1 = new THREE.Vector3();
      }
      const qVis = NetLink._sQ1.copy(gp.quaternion).multiply(mq);
      NetLink._sV1.set(0, (PALA_BLADE_Y - PALA_GRIP_Y) * PALA_SCALE, 0)
        .applyQuaternion(qVis).add(gp.position);   // centro de la hoja en rig
      pkt.pad = NetLink.posToNet(NetLink._sV1).concat(NetLink.quatToNet(qVis));
    }
    if (this.owner === this.mySide()) {
      pkt.b = {
        p: NetLink.posToNet(g.ball.pos),
        v: NetLink.rawPos(g.ball.vel),
        s: [+g.ball.spin.x.toFixed(2), +g.ball.spin.y.toFixed(2), +g.ball.spin.z.toFixed(2)],
      };
    }
    if (this._outEvs.length) { pkt.e = this._outEvs; this._outEvs = []; }
    if (this.role === 'host') {
      const r = g.rules;
      pkt.y = {
        st: r.state, sv: r.server, sp: r.scorePlayer, sa: r.scoreAi,
        ms: r.message, md: r.mode, ow: this.owner, rh: r.rallyHits,
      };
      // v2.25: causa estructural del último punto / LET (send-once)
      if (this.lastPoint) { pkt.y.pt = this.lastPoint; this.lastPoint = null; }
      if (this.lastRetry) { pkt.y.rt = this.lastRetry; this.lastRetry = null; }
      if (r.state === 'over') pkt.y.wn = r.scorePlayer > r.scoreAi ? 'player' : 'ai';
    }
    this.send(pkt);
  }

  /** Recoge los eventos de física del ÚLTIMO frame (el dueño los emite).
   *  v2.51 CRÍTICO: los eventos REENVIADOS por la red (drainNetwork los
   *  inyecta con remote:true) NO se re-emiten — antes cada bote del rival
   *  volvía a la red en bucle infinito a 20 Hz: tormenta de eventos (más de
   *  55.000 en 45 s medida en el banco), puntos fantasma en el árbitro del
   *  anfitrión, marcas eternas en la mesa y audio en ametralladora. */
  collectEvents(events) {
    if (!this.online) return;
    const T = DIMS.tableTopY;
    for (const e of events) {
      if (e.remote) continue;                    // v2.51: jamás re-emitir
      // v2.91: la Y viaja anclada al tapete (y - T), como toda posición
      if (e.type === 'table') this._outEvs.push(['T', e.pos.x, e.pos.y - T, e.pos.z]);
      else if (e.type === 'net') this._outEvs.push(['N', e.pos.x, e.pos.y - T, e.pos.z]);
      else if (e.type === 'floor') this._outEvs.push(['F', e.pos.x, e.pos.y - T, e.pos.z]);
      else if (e.type === 'wall') this._outEvs.push(['W', e.pos.x, e.pos.y - T, e.pos.z]);
    }
  }

  /** Anuncia un golpeo local (tras aplicar la velocidad ya corregida).
   *  v2.25: emisión EN CRUDO — el receptor aplica el espejo UNA vez.
   *  v2.51: se marca _lastHitSent para que applySync no pise el claim
   *  local con el ow atrasado del anfitrión (flap de propiedad). */
  sendHit(isServe) {
    if (!this.online) return;
    const g = this.game;
    this.owner = this.mySide();
    this._lastHitSent = performance.now();
    this.send({
      k: 'h', sv: isServe ? 1 : 0,
      p: NetLink.posToNet(g.ball.pos),
      v: NetLink.rawPos(g.ball.vel),
      s: [+g.ball.spin.x.toFixed(2), +g.ball.spin.y.toFixed(2), +g.ball.spin.z.toFixed(2)],
    });
  }

  sendRematch() { this.send({ k: 'r' }); }
  sendMode(md) { this.send({ k: 'm', md }); }

  /* --------------- recepción --------------- */
  onData(d) {
    if (!d || typeof d !== 'object') return;
    if (d.k === 'p') {
      if (d.pad) {
        // v2.91: se guarda TAMBIÉN la muestra anterior para estimar la
        // velocidad de la pala rival (muerte adelantada suave)
        if (this.remotePaddle) this._padPrev = this.remotePaddle;
        this.remotePaddle = { p: d.pad.slice(0, 3), q: d.pad.slice(3, 7), t: performance.now() };
      }
      if (d.b) {
        this.remoteBall = d.b;
        this.remoteBallT = performance.now();
      }
      if (d.e) this._inEvs.push(...d.e);
      if (d.y) this.applySync(d.y);
      return;
    }
    if (d.k === 'h') {
      // v2.25: solo el anfitrión encola golpeos para validarlos. En el
      // invitado un golpeo del anfitrión significa "la bola ahora es suya":
      // se cambia el dueño AL INSTANTE (sin esperar al siguiente sync) y no
      // se encola (antes crecía sin límite en el invitado: fuga de memoria).
      // v2.51: la bola del golpeo se aplica INMEDIATAMENTE (posición,
      // velocidad y spin del paquete) — antes el invitado mostraba la bola
      // congelada hasta el siguiente paquete 'p' (hasta 50 ms de bola muerta
      // en cada golpeo del anfitrión).
      if (this.role === 'host') this._pendingHits.push(d);
      else {
        if (this.owner !== 'host') this.owner = 'host';
        const g = this.game;
        if (g && d.p && d.v) {
          NetLink.posFromNet(d.p, g.ball.pos);
          NetLink.vecFromNet(d.v, g.ball.vel);
          if (d.s) NetLink.spinFromNet(d.s, g.ball.spin);
          this.remoteBall = { p: d.p.slice(), v: d.v.slice(),
            s: d.s ? d.s.slice() : null };
          this.remoteBallT = performance.now();
        }
      }
      return;
    }
    if (d.k === 'r') {    // el invitado pide revancha
      if (this.role === 'host') this.game.startOnlineMatch();
      return;
    }
    if (d.k === 'm') {
      if (this.role === 'host' && (d.md === 'match' || d.md === 'survival')) {
        this.game.switchMode(d.md);
      }
      return;
    }
    if (d.k === 'bye') this.onPeerGone(T('peer_closed'));
  }

  /** Estado del partido recibido del anfitrión (reglas sombra).
   *  v2.25 · SINCRONÍA POR PUNTO DE VISTA: el anfitrión etiqueta TODO desde
   *  su perspectiva ('player'=anfitrión, 'ai'=invitado). En el invitado esas
   *  etiquetas significan lo contrario ('player' soy YO), así que se
   *  intercambian marcador y sacador y se remapea el ganador. Antes el
   *  invitado veía el marcador invertido, sostenía la bola cuando sacaba el
   *  rival y celebraba los puntos del otro. Los MENSAJES del anfitrión están
   *  en su perspectiva: se regeneran localmente, nunca se copian. */
  applySync(y) {
    const g = this.game;
    const r = g.rules;
    // v2.51 · ANTI-FLAP: tras un golpeo propio el invitado RECLAMA la bola
    // (owner='guest' en sendHit). El sync del anfitrión todavía lleva su
    // ow='host' ANTIGUO durante ~RTT+50 ms; aceptarlo anulaba el golpeo:
    // la bola saltaba de mi simulación a su emisión atrasada y volvía
    // (movimiento caótico en cada intercambio). Con un claim local reciente
    // y en rallye, se ignora el ow='host' hasta que el anfitrión confirma
    // ('guest') o el estado cambia (la autoridad del árbitro manda siempre
    // fuera de 'rally').
    const localClaim = this.role === 'guest' && this.owner === 'guest' &&
      r.state === 'rally' && this._lastHitSent &&
      (performance.now() - this._lastHitSent) < 600;
    if (y.ow === 'guest' || !localClaim) this.owner = y.ow || 'host';
    const guest = this.role === 'guest';
    const my = guest ? y.sa : y.sp;        // MI marcador
    const op = guest ? y.sp : y.sa;        // el del rival
    const srv = (guest ? y.sv === 'ai' : y.sv === 'player') ? 'player' : 'ai';
    const prevMy = r.scorePlayer, prevOp = r.scoreAi;
    const prevState = r.state, prevMode = r.mode;
    r.state = y.st; r.server = srv;
    r.scorePlayer = my; r.scoreAi = op;
    r.mode = y.md; r.rallyHits = y.rh || 0;
    g.mode = y.md; g.pendingMode = y.md;
    if (y.pt) this.lastPoint = y.pt;
    if (y.rt) this.lastRetry = y.rt;

    // ---- MENSAJES LOCALES (perspectiva propia; nunca el texto del rival) --
    if (r.state === 'point' && this.lastPoint) {
      const lp = this.lastPoint;
      const wLocal = guest ? (lp.w === 'player' ? 'ai' : 'player') : lp.w;
      const c = T('cause_' + NetLink.remapCause(lp.c, guest), { opp: r.opp() });
      const rallyTxt = lp.rh >= 6 ? T('rally_suffix', { n: lp.rh }) : '';
      r.message = wLocal === 'player'
        ? T('point_you', { cause: c, rally: rallyTxt })
        : T('point_opp', { opp: r.opp(), cause: c, rally: rallyTxt });
    } else if (r.state === 'serve') {
      if (this.lastRetry) r.message = T('retry_serve', { cause: T('cause_' + this.lastRetry, { opp: r.opp() }) });
      else r.message = srv === 'player'
        ? T('serve_go')
        : T('serve_opp', { opp: r.opp() });
    } else if (r.state === 'over') {
      const won = my > op;
      // v2.26/2.27: mensajes alineados con los carteles oficiales, en el idioma local
      r.message = won
        ? T('over_win', { p: my, q: op })
        : T('over_lose', { p: my, q: op });
    }
    if (r.state !== 'point') this.lastPoint = null;
    if (r.state !== 'serve') this.lastRetry = null;

    // ---- SONIDO/MEGAFONÍA LOCAL (el invitado antes callaba en online) -----
    const OHH_CAUSES = NetLink.OHH_CAUSES;
    if ((my !== prevMy || op !== prevOp) && r.state !== 'over') {
      const iWon = my > prevMy;
      g.audio.point(iWon);
      if (iWon) g.audio.applause(false);
      else if (this.lastPoint?.c && OHH_CAUSES.has(this.lastPoint.c)) g.audio.ohh();
      if (g.renderer.xr.isPresenting) {
        g.haptic(g.paddleHand, iWon ? 0.85 : 0.4, iWon ? 110 : 60);
      }
    }
    if (r.state === 'serve' && prevState !== 'serve' && r.mode !== 'survival') {
      g.audio.announce(T('ann_score', { p: r.scorePlayer, q: r.scoreAi,
        who: srv === 'player' ? T('who_you') : T('opp_rival') }));
    }
    if (prevMode !== r.mode && (r.mode === 'match' || r.mode === 'survival')) {
      g.audio.announce(r.mode === 'survival' ? T('mode_survival') : T('mode_match'), true);
    }

    // ---- FIN DE PARTIDO con perspectiva remapeada ----
    if (y.st === 'over' && y.wn) {
      const k = `${y.wn}|${my}-${op}`;
      if (k !== this._overKey) {
        this._overKey = k;
        const iWon = guest ? y.wn === 'ai' : y.wn === 'player';
        g.startFanfare(iWon);
        g.audio.applause(iWon);
        g.audio.announce(iWon
          ? T('ann_victory', { p: r.scorePlayer, q: r.scoreAi })
          : T('ann_match_end', { opp: r.opp(), p: r.scoreAi, q: r.scorePlayer }), true);
        g.celebrate(g.stats.recordMatch(iWon, g.difficulty));
        g.emitStats();
      }
    } else {
      this._overKey = '';
    }
  }

  /** Aplica la bola recibida por red (solo cuando el dueño es el rival).
   *  v2.91 · MUERTE ADELANTADA (dead reckoning): la muestra llega a 30 Hz
   *  por una red con jitter; entre paquetes se integra la gravedad local
   *  sobre la (pos, vel) recibida según la EDAD del paquete y se persigue
   *  esa trayectoria predicha. Antes el lerp puro hacia la última muestra
   *  frenaba la bola y cortaba el arco: rallye «a trompicones». */
  applyBallStream(ball, dt) {
    const s = this.remoteBall;
    if (!s) return false;
    const tmp = this._tv || (this._tv = new THREE.Vector3());
    const tvv = this._tv2 || (this._tv2 = new THREE.Vector3());
    const age = Math.min(0.22, Math.max(0, (performance.now() - this.remoteBallT) / 1000));
    NetLink.posFromNet(s.p, tmp);
    NetLink.vecFromNet(s.v, tvv);
    // cinemática EXACTA: p += v·age + ½g·age² con la velocidad SIN tocar;
    // después v += g·age (v2.91: el orden equivocado aplicaba 1,5 g)
    tmp.addScaledVector(tvv, age);
    tmp.y += 0.5 * DIMS.gravity * age * age;
    tvv.y += DIMS.gravity * age;
    const f = 1 - Math.exp(-20 * dt);
    ball.pos.lerp(tmp, f);
    ball.vel.lerp(tvv, 1 - Math.exp(-14 * dt));
    if (s.s) NetLink.spinFromNet(s.s, ball.spin);   // v2.25: spin espejado
    return true;
  }

  /** Host: aplica golpeos pendientes del invitado; ambos: suena la bola rival. */
  drainNetwork(game) {
    // eventos del rival (botes/red/suelo): al marco LOCAL
    if (this._inEvs.length) {
      const C = NetLink.TABLE_CZ;
      const T = DIMS.tableTopY;
      const evs = this._inEvs; this._inEvs = [];
      for (const [t, x, y, z] of evs) {
        // v2.91: espejo + reanclar la Y al TAPALETTE propio (y + T)
        const lx = -x, ly = y + T, lz = -3.2 - z;
        const pos = new THREE.Vector3(lx, ly, lz);
        // v2.51: remote:true — marca los eventos REENVIADOS para que
        // collectEvents NO los mande otra vez por la red (eco infinito)
        if (t === 'T') game.events.push({ type: 'table', side: lz > C ? 'player' : 'ai', speed: 1.5, pos, remote: true });
        else if (t === 'N') game.events.push({ type: 'net', speed: 1.5, pos, remote: true });
        else if (t === 'F') game.events.push({ type: 'floor', speed: 1.5, pos, remote: true });
        else if (t === 'W') game.events.push({ type: 'wall', speed: 1.5, pos, remote: true });
      }
    }
    // golpeos del rival (solo el anfitrión valida y puntúa)
    if (this.role === 'host' && this._pendingHits.length) {
      const hits = this._pendingHits; this._pendingHits = [];
      for (const h of hits) {
        const g = game;
        // v2.51: un golpeo del rival SOLO es procesable en rallye, o en
        // saque si se declara como tal (sv=1). En 'point'/'over' el golpeo
        // llega atrasado: se descarta sin teleportar la bola ni robar el
        // dueño (antes desplazaba la bola a una posición fantasma).
        const st = g.rules.state;
        if (st !== 'rally' && !(st === 'serve' && h.sv)) continue;
        NetLink.posFromNet(h.p, g.ball.pos);
        NetLink.vecFromNet(h.v, g.ball.vel);
        if (h.s) NetLink.spinFromNet(h.s, g.ball.spin);   // v2.25: espejado
        this.owner = 'guest';
        g.audio.paddle(
          THREE.MathUtils.clamp(g.ball.pos.x / 2.5, -1, 1),
          Math.min(1, g.ball.vel.length() / 9),
        );
        g.haptic(g.paddleHand, 0.3, 40);
        if (h.sv) g.rules.beginServeRally('ai');
        else g.processIntents(g.rules.registerPaddleHit('ai'));
      }
    }
  }

  onPeerGone(msg) {
    const wasOnline = this.online;
    this.teardown();
    this.setStatus('off', wasOnline ? msg : '');
    if (wasOnline) this.game?.onNetEnded?.(msg);
  }

  cancel() {
    this.teardown();
    this.setStatus('off', '');
  }

  hangup() { this.send({ k: 'bye' }); this.onPeerGone('Has cerrado la conexión'); }

  teardown() {
    try { this.conn?.close(); } catch { /* */ }
    try { this.call?.close(); } catch { /* */ }
    try { this.peer?.destroy(); } catch { /* */ }
    try { this.micStream?.getTracks().forEach((t) => t.stop()); } catch { /* */ }
    if (this.remoteAudio) { try { this.remoteAudio.srcObject = null; } catch { /* */ } }
    this.conn = null; this.call = null; this.peer = null; this.micStream = null;
    this._silent = null;
    this.online = false;
    this.remotePaddle = null; this.remoteBall = null;
    this._padPrev = null;                               // v2.91
    this._outEvs = []; this._inEvs = []; this._pendingHits = [];
    this.lastPoint = null; this.lastRetry = null;   // v2.25
    this._lastHitSent = 0;                          // v2.51
    if (this._joinTO) { window.clearTimeout(this._joinTO); this._joinTO = null; }
    this.voiceState = 'off';
    this.owner = 'host';
  }
}


/* =====================================================================
 *  ORQUESTADOR · sesión WebXR, mandos Quest 3, saque con mano libre,
 *  háptica y bucle principal
 * ===================================================================== */
// v2.28: arte de la cabecera del MENÚ PRINCIPAL (data URL JPEG incrustado
// por build_html.py — recorte del logo CRAZY PING PONG del arte del juego)
