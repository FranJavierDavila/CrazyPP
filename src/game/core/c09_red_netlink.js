export class NetLink {
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
  /* v3.6.73 · r81 · CONVENCIÓN ÚNICA DEL CABLE: el paquete viaja YA en el
   * marco del RECEPTOR (el emisor aplica el espejo 180° UNA vez con
   * posToNet/_stateNet — la involución R(z) = −3.2−z manda «mi lado» al
   * «lado del otro»). Antes el receptor VOLVÍA a aplicar R al recibir
   * (posFromNet/posFromNetArr): R∘R = identidad → la bola y la pala del
   * rival aterrizaban en el marco CRUDO del emisor (¡lado contrario de la
   * mesa!) — el defecto de fondo del multijugador «cosmético» desde v2.19.
   * Al recibir solo queda re-anclar la Y al tapete propio (la Y viaja
   * relativa a la mesa desde v2.91). Los VECTORES (velocidad/spin) ya
   * viajan espejados por el emisor en v2 (_velNet/_spinNet) → identidad;
   * en v1 el emisor los manda en crudo → sus receptores SÍ espejan una
   * vez (vecFromNet/spinFromNet intactos). Eventos v1 (botes): crudo →
   * espejo al recibir (drainNetwork, intacto). UN solo espejo por camino. */
  static posFromNet(a, out) {
    const T = DIMS.tableTopY;
    out.set(a[0], a[1] + T, a[2]);
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
  /** r79: inversos de arrays planos (eventos fast → marco local).
   *  r81: el wire ya viene en MI marco (espejo del emisor) — solo Y+T. */
  static posFromNetArr(a) {
    const T = DIMS.tableTopY;
    return new THREE.Vector3(a[0], a[1] + T, a[2]);
  }
  static vecFromNetArr(a) { return new THREE.Vector3(a[0], a[1], a[2]); }
  static spinFromNetArr(a) { return new THREE.Vector3(a[0], a[1], a[2]); }

  /* v3.6.73 · r81 · ESPEJO DE POSE (solo X/Z):
   * La POSE del rival viaja con la Y ANCLADA AL TAPETE por el códec
   * (wPos/rPos con yAnchor: sale y−T_anfitrión y entra y+T_propio —
   * v2.91), así que al recibir YA está a la altura correcta sobre MI
   * mesa. Añadir T OTRA VEZ (posFromNet) flotaba al rival ~76 cm por
   * encima de su altura real («los movimientos no calibran bien»).
   * El espejo de pose sólo gira X/Z (la involución de 180°); la Y pasa
   * tal cual. NUEVO para poses; posFromNet sigue para BOLAS/eventos
   * (esas viajan con Y relativa y SÍ necesitan el +T al recibir). */
  static posFromNetPose(a, out) {
    out.set(-a[0], a[1], -3.2 - a[2]);
    return out;
  }
  /** pose cruda (marco del emisor, Y ya anclada a MI tapete) → marco NET
   *  canónico de eventos ([-x, y−T, −3.2−z]) — el MISMO marco de ev.p
   *  para que el validador compare peras con peras (spec §12). */
  static poseToNetFrame(a) {
    const T = DIMS.tableTopY;
    return [-a[0], a[1] - T, -3.2 - a[2]];
  }

  /** v2.91 · La propiedad de la bola SIGUE AL SACADOR durante el saque:
   *  si saco YO, yo simulo (toss real + físicas + contacto propio); si
   *  saca el rival, sigo su emisión. Antes el dueño quedaba fijo en
   *  'host': el INVITADO no podía sacar — su lanzamiento era pisado en
   *  cada frame por la emisión atrasada del anfitrión y la bola se caía
   *  al suelo sin poder golpearla.
   *  v3.6.71 · r79: con transporte v2 el dueño lo conduce la FSM de la
   *  bola (HELD/OWN/GHOST/AUTH) — aquí sólo se sincroniza desde ella. */
  syncServeOwner() {
    if (!this.online || !this.game || !this.game.rules) return;
    if (this.v2 === 'ok') { this._syncOwnerFromBall(); return; }
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
      // v3.6.71 · r79: subir el transporte binario v2 (fast + reliable) —
      // la partida arrancará con el MATCH_START sincronizado (spec §3.8)
      this.startV2();
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
    if (this.v2 === 'pending') return;   // r79: durante la subida no hay v1
    if (this.v2 === 'ok') return;        // r79: el transporte v2 usa frame()
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
        // v3.6.29 · MEJOR DE 3: la serie viaja con el estado (bo=objetivo,
        // gp/ga juegos ganados; el invitado los espeja con perspectiva)
        bo: r.bestOf, gp: r.gamesPlayer, ga: r.gamesAi,
      };
      // v2.25: causa estructural del último punto / LET (send-once)
      if (this.lastPoint) { pkt.y.pt = this.lastPoint; this.lastPoint = null; }
      if (this.lastRetry) { pkt.y.rt = this.lastRetry; this.lastRetry = null; }
      // v3.6.29: resultado del ÚLTIMO JUEGO terminado (send-once, como pt/rt)
      if (this.lastGame) { pkt.y.gw = this.lastGame; this.lastGame = null; }
      if (r.state === 'over') pkt.y.wn = r.scorePlayer > r.scoreAi ? 'player' : 'ai';
    }
    this.send(pkt);
  }

  /** Recoge los eventos de física del ÚLTIMO frame (el dueño los emite).
   *  v2.51 CRÍTICO: los eventos REENVIADOS por la red (drainNetwork los
   *  inyecta con remote:true) NO se re-emiten — antes cada bote del rival
   *  volvía a la red en bucle infinito a 20 Hz: tormenta de eventos (más de
   *  55.000 en 45 s medida en el banco), puntos fantasma en el árbitro del
   *  anfitrión, marcas eternas en la mesa y audio en ametralladora.
   *  v3.6.71 · r79: el transporte v2 NO envía botes — el rival los oye de
   *  SU simulación local (fantasma o autoridad), como dicta la spec §8. */
  collectEvents(events) {
    if (!this.online) return;
    if (this.v2 === 'ok') return;
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
   *  local con el ow atrasado del anfitrión (flap de propiedad).
   *  v3.6.71 · r79: el transporte v2 no pasa por aquí (netLocalHit). */
  sendHit(isServe) {
    if (!this.online) return;
    if (this.v2 === 'ok') { this.netLocalHit(isServe); return; }
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
    // v3.6.71 · r79: señalización y control del transporte v2 (por la
    // DataConnection PeerJS o por el canal reliable propio, mismo formato)
    if (d.k === 'sdp') { this._v2RemoteDesc(d.d); return; }
    if (d.k === 'ice') { this._onIce(d.c); return; }
    // v3.6.74 · r82 · paquete fast encapsulado por el TÚNEL PeerJS: mismo
    // camino que un paquete del DataChannel propio (binario intacto)
    if (d.k === 'f2' && d.b) {
      let b = d.b;
      if (!(b instanceof ArrayBuffer) && b.buffer) {
        b = b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
      }
      if (b instanceof ArrayBuffer) this._onFast(b);
      return;
    }
    switch (d.k) {
      case 'hello2': case 'tick2': case 'tock2': case 'ready2':
      case 'mstart': case 'claim': case 'ack': case 'resync':
      case 'pause': case 'resume': case 'mend': case 'v2off':
        this._onRel(d);
        return;
    }
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
    // v3.6.29: la serie del anfitrión se espeja CON PERSPECTIVA (gp es suyo)
    r.bestOf = y.bo || 1;
    r.gamesPlayer = guest ? (y.ga || 0) : (y.gp || 0);
    r.gamesAi = guest ? (y.gp || 0) : (y.ga || 0);
    g.mode = y.md; g.pendingMode = y.md;
    if (y.pt) this.lastPoint = y.pt;
    if (y.rt) this.lastRetry = y.rt;
    if (y.gw) this.lastGame = y.gw;

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
      // v3.6.29 · MEJOR DE 3: el cierre anuncia el ENFRENTAMIENTO completo
      r.message = (r.bestOf > 1 && r.mode === 'match')
        ? (won
          ? T('over_win_bo', { p: my, q: op, a: r.gamesPlayer, b: r.gamesAi })
          : T('over_lose_bo', { opp: r.opp(), p: my, q: op, a: r.gamesPlayer, b: r.gamesAi }))
        : (won
          ? T('over_win', { p: my, q: op })
          : T('over_lose', { p: my, q: op }));
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
    if (r.state === 'serve' && prevState !== 'serve' && r.mode !== 'survival' && !this.lastGame) {
      g.audio.announce(T('ann_score', { p: r.scorePlayer, q: r.scoreAi,
        who: srv === 'player' ? T('who_you') : T('opp_rival') }));
    }
    // v3.6.29 · MEJOR DE 3: fin de juego SIN fin del enfrentamiento — el
    // anfitrión lo señala con gw (una sola vez, como pt/rt); el invitado lo
    // anuncia en SU idioma y SU perspectiva y consume la señal.
    if (r.state === 'serve' && this.lastGame && r.mode === 'match' && r.bestOf > 1) {
      const gw = this.lastGame;
      const wLocal = guest ? (gw.w === 'player' ? 'ai' : 'player') : gw.w;
      const pL = guest ? gw.q : gw.p;
      const qL = guest ? gw.p : gw.q;
      g.audio.announce(wLocal === 'player'
        ? T('ann_game_you', { p: pL, q: qL, a: r.gamesPlayer, b: r.gamesAi })
        : T('ann_game_opp', { opp: r.opp(), p: pL, q: qL, a: r.gamesPlayer, b: r.gamesAi }), true);
      this.lastGame = null;
    }
    if (r.state !== 'serve') this.lastGame = null;
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
   *  v3.6.71 · r79: con transporte v2 la bola rival NO llega por stream —
   *  la simula el fantasma con la física real (devuelve false siempre). */
  applyBallStream(ball, dt) {
    if (this.v2 === 'ok') return false;
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
        else g.processIntents(g.rules.registerPaddleHit('ai', true));   // r81: golpe remoto
      }
    }
  }

  /* =====================================================================
   *  v3.6.71 · r79 — CRAZY LINK v2 · TRANSPORTE BINARIO DE DOBLE CANAL
   *  Spec «Netcode multijugador online — Ping Pong VR (WebXR)» v1.0:
   *    · El GOLPE PROPIO es sagrado: colisión local, sonido y háptica en
   *      el mismo frame; la red nunca la retrasa.
   *    · AUTORIDAD POR MITAD DE MESA: quien tiene la bola en su mitad
   *      decide botes/fallos/puntos; traspaso (BALL_HANDOFF) al cruzar
   *      la red limpiamente; autoridad provisional a los 300 ms.
   *    · Puntos por POINT_CLAIM → POINT_ACK (rallyId = totalPoints) y
   *      RESYNC_STATE del anfitrión como árbitro final.
   *    · Reloj compartido (ancla gruesa por reliable + refinado NTP por
   *      la cabecera fast), jitter buffer del avatar y validación.
   *  PeerJS sigue siendo la SALA (código, presencia, voz) y además el
   *  canal de SEÑALIZACIÓN (SDP/ICE) de una RTCPeerConnection propia con
   *  dos DataChannels: fast {ordered:false, maxRetransmits:0} (tipo UDP)
   *  y reliable {ordered:true} (control JSON, mensajes raros).
   *  Si la subida falla → degradación HONESTA al modo v1 (30 Hz JSON).
   *  ===================================================================== */

  static ICE_CFG() {
    // STUN público + TURN libre (openrelay/metered) — decisión abierta de la
    // spec §18 (coturn propio y regiones: hito posterior, ver worklog).
    return {
      iceServers: [
        { urls: ['stun:stun.l.google.com:19302', 'stun:stun1.l.google.com:19302'] },
        {
          urls: ['turn:openrelay.metered.ca:80', 'turn:openrelay.metered.ca:443',
            'turn:openrelay.metered.ca:443?transport=tcp'],
          username: 'openrelayproject', credential: 'openrelayproject',
        },
      ],
      iceCandidatePoolSize: 4,
    };
  }

  /** FASE 0 · subida del transporte. El INVITADO ofrece; el anfitrión
   *  responde; el ICE viaja por la DataConnection PeerJS existente. */
  startV2() {
    if (typeof PPNET === 'undefined' || typeof RTCPeerConnection === 'undefined') {
      this._v2Fail(T('net_legacy'));           // sin piezas: v1 honesto
      return;
    }
    this.v2 = 'pending';                        // pending|ok|fail
    this._pc = null; this._fast = null; this._rel = null;
    this._fastOpen = false; this._relOpen = false;
    this._seq = (Math.random() * 0xffff) | 0;
    this._ackP = 0; this._ackBits = 0;
    this._echoTime = 0; this._echoAt = 0;       // eco del último paquete recibido
    this._pend = [];                            // eventos pendientes de ack
    this._evId = 1;
    this._fastIn = [];                          // eventos entrantes a drenar
    this._seenEv = new Map();                   // dedupe por eventId
    this._recvRing = [];                        // seqs recibidos (pérdida)
    this._recvHist = [];                        // seqs recibidos (ack/ackBits)
    this._lastPoseAt = 0;                       // frescura del avatar
    this._gaps = 0; this._recvs = 0;
    this._poseAcc = 0; this._snapAcc = 0;
    this._poseHz = PPNET.VP.POSE_HZ;
    this._lossLowT = 0; this._degraded = false;
    this._lastFastAt = 0; this._iceRestarts = 0;
    this._helloDone = false; this._helloTO = null;
    this._iceQ = [];                            // r81: ICE tempranos en cola
    this._tunnel = false;                       // r82: túnel PeerJS (emergencia)
    this._v2T0 = performance.now();             // r82: nacimiento de la subida
    this._buildWarn = false;                    // r82: HELLO con build distinto
    this._anchors = 0; this._readyMe = false; this._readyOpp = false;
    this._mstart = null;                        // {startAt, fs, bo}
    this._clock = new PPNET.NetClock(this.role === 'host');
    this._jb = new PPNET.JitterBuf();
    this._ball = new PPNET.BallAuth();
    this._sync = new PPNET.MatchSync(this.role);
    this._val = new PPNET.Validator();
    this._stats = new PPNET.NetStats(this.role);
    // r79: la guardia anti-doble-punto del árbitro SOLO con red v2
    try { if (this.game && this.game.rules) this.game.rules._netGuard = true; } catch { /* */ }
    this._visOff = null; this._visOffMs = 0;    // corrección/catch-up visual
    this._pausedSelf = false; this._pausedRemote = false; this._pausedAt = 0;
    this._lastRelAt = 0; this._claimFallback = null;
    PPNET.VP.BUILD = (typeof VERSION !== 'undefined') ? VERSION : '';
    // pausa por visor quitado / pestaña oculta (spec §10)
    this._onVis = () => {
      if (this.v2 !== 'ok' || !this.online) return;
      this._pausedSelf = document.hidden;
      if (document.hidden) this.sendRel({ k: 'pause', t: this._clock.nowHost(performance.now()) });
      else this.sendRel({ k: 'resume', t: this._clock.nowHost(performance.now()) });
    };
    document.addEventListener('visibilitychange', this._onVis);
    if (this.role === 'guest') this._v2Offer();
    // r81 · watchdog de HELLO con ventanas GENEROSAS: el ICE de redes reales
    // (hotspots, NAT simétricos con STUN lento) puede tardar 10-15 s en
    // abrir; con 9 s el transporte moría ANTES de nacer y la partida caía
    // al modo compatible v1. 22 s de gracia total antes de degradar.
    this._helloTO = window.setTimeout(() => {
      if (this.v2 === 'pending') this._v2Fail(T('net_legacy'));
    }, 22000);
  }

  async _v2Offer() {
    try {
      const pc = new RTCPeerConnection(NetLink.ICE_CFG());
      this._pc = pc;
      this._fast = pc.createDataChannel('fast', { ordered: false, maxRetransmits: 0 });
      this._rel = pc.createDataChannel('rel', { ordered: true });
      this._wireDC();
      pc.onicecandidate = (e) => {
        if (e.candidate) this.send({ k: 'ice', c: e.candidate.toJSON ? e.candidate.toJSON() : e.candidate });
      };
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      this.send({ k: 'sdp', d: { type: pc.localDescription.type, sdp: pc.localDescription.sdp } });
    } catch (e) {
      this._v2Fail(T('net_legacy'));
    }
  }

  /** descripción remota SDP: el anfitrión recibe la OFERTA (y responde);
   *  el invitado recibe la RESPUESTA. */
  async _v2RemoteDesc(desc) {
    try {
      if (!desc || !desc.type) return;
      if (!this._pc) {
        const pc = new RTCPeerConnection(NetLink.ICE_CFG());
        this._pc = pc;
        pc.onicecandidate = (e) => {
          if (e.candidate) this.send({ k: 'ice', c: e.candidate.toJSON ? e.candidate.toJSON() : e.candidate });
        };
        pc.ondatachannel = (e) => {
          if (e.channel.label === 'fast') this._fast = e.channel;
          else if (e.channel.label === 'rel') this._rel = e.channel;
          this._wireDC();
        };
      }
      await this._pc.setRemoteDescription(desc);
      // r81 · ICE tempranos: los candidatos que llegaron ANTES de la
      // descripción remota se encolaban y morían en silencio (addIceCandidate
      // rechaza sin remoteDescription) — en redes reales dejaba el ICE a medio
      // abrir y la partida sin canal fast. Se drenan ahora, en orden.
      const q = this._iceQ || [];
      this._iceQ = [];
      for (const c of q) {
        try { this._pc.addIceCandidate(c).catch(() => { /* */ }); } catch { /* */ }
      }
      if (desc.type === 'offer') {
        const ans = await this._pc.createAnswer();
        await this._pc.setLocalDescription(ans);
        this.send({ k: 'sdp', d: { type: ans.type, sdp: ans.sdp } });
      }
    } catch (e) {
      this._v2Fail(T('net_legacy'));
    }
  }

  /** r81 · candidato ICE entrante: si la descripción remota aún no está,
   *  se ENCOLA (se drena en _v2RemoteDesc); si ya está, se aplica. */
  _onIce(c) {
    if (!c) return;
    try {
      const rd = this._pc && this._pc.remoteDescription;
      if (this._pc && rd && rd.type) this._pc.addIceCandidate(c).catch(() => { /* */ });
      else (this._iceQ = this._iceQ || []).push(c);
    } catch { /* */ }
  }

  _wireDC() {
    if (this._fast) {
      this._fast.binaryType = 'arraybuffer';
      this._fast.onopen = () => {
        this._fastOpen = true;
        this._v2ChannelsUp();
      };
      this._fast.onmessage = (e) => this._onFast(e.data);
      this._fast.onerror = () => { /* el watchdog de ICE decide */ };
      this._fast.onclose = () => { this._fastOpen = false; };
    }
    if (this._rel) {
      this._rel.onopen = () => {
        this._relOpen = true;
        this._v2ChannelsUp();
      };
      this._rel.onmessage = (e) => {
        try { this._onRel(JSON.parse(typeof e.data === 'string' ? e.data : String(e.data))); }
        catch { /* json inválido: ignorar */ }
      };
      this._rel.onclose = () => { this._relOpen = false; };
    }
  }

  _v2ChannelsUp() {
    // v3.6.74 · r82 · los canales «suben» por DOS caminos: DC propios abiertos
    // (P2P) o túnel PeerJS activo (el ICE no llegó a abrir pero la sala vive)
    if (!((this._fastOpen && this._relOpen) || this._tunnel) || this.v2 !== 'pending') return;
    // HELLO (reliable): versión de protocolo, build y ballPhysics (spec §3.5)
    this.sendRel({ k: 'hello2', v: PPNET.VP.PROTO, ph: PPNET.VP.PHYS, b: PPNET.VP.BUILD });
    if (this._helloTO) { window.clearTimeout(this._helloTO); this._helloTO = null; }
    // r81 · 15 s para el HELLO de respuesta (el ICE ya está abierto aquí:
    // esto sólo cubre un peer colgado a medias)
    this._helloTO = window.setTimeout(() => {
      if (this.v2 === 'pending') this._v2Fail(T('net_legacy'));
    }, 15000);
  }

  _onRel(m) {
    if (!m || typeof m !== 'object') return;
    this._lastRelAt = performance.now();
    switch (m.k) {
      case 'hello2': {
        if (m.v !== PPNET.VP.PROTO || m.ph !== PPNET.VP.PHYS) {
          this._v2Fail(T('net_legacy'));        // protocolo/física distintos → v1
          return;
        }
        // v3.6.74 · r82 · BUILD TOLERANTE: el número de build ya NO rompe el
        // enlace — el cable v2 depende de PROTO/PHYS y el códec es idéntico.
        // Antes, dos cascos con la caché desigual (uno en 3.6.72 y otro en
        // 3.6.73) rechazaban el HELLO y caían EN SILENCIO al v1 cosmético:
        // el dueño veía «movimiento de palas pero poco más». Ahora el enlace
        // sube igual y se AVISA (menú + voz) para recargar ambos visores.
        this._buildWarn = m.b !== PPNET.VP.BUILD;
        if (this._buildWarn) {
          this.statusMsg = T('net_build_warn', { a: (m.b || '?').slice(-6), b: (PPNET.VP.BUILD || '?').slice(-6) });
          this.game?.onNetStatus?.();
        }
        this._helloDone = true;
        // ráfaga de reloj: 8 intercambios a ~50 ms (spec §3.6)
        for (let i = 0; i < 8; i++) {
          window.setTimeout(() => {
            if (this.v2 === 'ok' || this.v2 === 'pending') {
              this.sendRel({ k: 'tick2', t: performance.now() });
            }
          }, i * 50);
        }
        break;
      }
      case 'tick2': {
        this.sendRel({ k: 'tock2', t: performance.now(), e: m.t });
        break;
      }
      case 'tock2': {
        // ancla gruesa: mi t de envío, su t completo, mi t de recepción
        this._clock.anchor(m.e, m.t, performance.now());
        this._clock.apply(performance.now(), false);
        this._anchors++;
        if (this._anchors >= 6 && !this._readyMe) {
          this._readyMe = true;
          this.sendRel({ k: 'ready2' });
          this._v2MaybeStart();
        }
        break;
      }
      case 'ready2': {
        this._readyOpp = true;
        this._v2MaybeStart();
        break;
      }
      case 'mstart': {
        // MATCH_START del anfitrión: instante futuro + primer sacador
        this._mstart = { startAt: m.sa, fs: m.fs, bo: m.bo || 3 };
        this.game?.onNetMatchStart?.(this._mstart);
        break;
      }
      case 'claim': {
        this._stats.claims++;
        const g = this.game;
        // el ganador del claim viaja en perspectiva DEL EMISOR: espejar a
        // la mía para confrontarlo con lo que YO apliqué (spec §7/§9).
        // r81 · el espejo es SIEMPRE el intercambio (el emisor llama
        // «player» a SÍ mismo; para mí ese mismo jugador es «ai»): antes
        // el anfitrión NO intercambiaba y un CLAIM del invitado se leía
        // al revés (punto al revés y desacuerdos enmascarados).
        const wMapped = m.w === 'let' ? 'let'
          : (m.w === 'player' ? 'ai' : 'player');
        const r = this._sync.onClaim(m, wMapped);
        this.sendRel(r.ack);
        if (r.apply && g) this._applyRemoteClaim(m, wMapped);
        if (!r.agree && this.role === 'host') this._sendResync();
        break;
      }
      case 'ack': {
        const r = this._sync.onAck(m);
        if (r.dispute && this.role === 'host') this._sendResync();
        break;
      }
      case 'resync': {
        if (this.role === 'guest') this._applyResync(m);
        break;
      }
      case 'pause': {
        this._pausedRemote = true;
        this._pausedAt = performance.now();
        this.game?.onNetPause?.(true);
        break;
      }
      case 'resume': {
        this._pausedRemote = false;
        this.game?.onNetPause?.(false);
        break;
      }
      case 'mend': {
        this.game?.onNetMatchEnd?.(m);
        break;
      }
      case 'v2off': {
        this._v2Fail(T('net_legacy'));
        break;
      }
    }
  }

  _v2MaybeStart() {
    if (!(this._readyMe && this._readyOpp) || this.v2 !== 'pending') return;
    this.v2 = 'ok';
    this._stats.t0 = performance.now();
    if (this.role === 'host') {
      // el anfitrión fija el instante de inicio en SU reloj (spec §3.8)
      const startAt = this._clock.nowHost(performance.now()) + PPNET.VP.COUNTDOWN_MS;
      const fs = 'host';
      this.sendRel({ k: 'mstart', sa: startAt, fs, bo: 3 });
      this._mstart = { startAt, fs, bo: 3 };
      this.game?.onNetMatchStart?.(this._mstart);
    }
    this.game?.onNetV2Ready?.();     // r79: arranque diferido si pidió revancha durante la subida
    this.game?.onNetStatus?.();
  }

  /** FASE 1 · bucle por frame (c12 animate): pose 60 Hz + eventos + snaps */
  frame(dt) {
    if (!this.online) return;
    // v3.6.74 · r82 · TÚNEL DE EMERGENCIA (antes del gate de v2: en
    // 'pending' este bucle es el único latido que puede activarlo): si el
    // ICE del transporte propio no abre en 8 s PERO la sala PeerJS sigue
    // viva (el dueño VEÍA a su rival moverse — ese camino DEMOSTRADO
    // funciona hasta tras CGNAT), el canal fast viaja ENCAPSULADO por la
    // DataConnection PeerJS: la FSM v2 entera (reloj, FS de bola,
    // validador, claims) corre idéntica sobre un tubo fiable. Adiós a la
    // degradación silenciosa al v1 cosmético.
    if (this.v2 === 'pending' && !this._tunnel && !this._fastOpen &&
        performance.now() - (this._v2T0 || 0) > 11000 &&
        this.conn && this.conn.open) {
      this._enterTunnel();
    }
    if (this.v2 !== 'ok') { this.tick(dt); return; }   // v1 honesto
    const now = performance.now();
    this._clock.apply(now, this.game?.rules?.state === 'rally');
    // watchdog de ICE: sin paquetes fast 5 s → restartIce (spec §11)
    // (r82: sólo en modo P2P — con túnel el ICE es irrelevante)
    if (!this._tunnel && this._lastFastAt && now - this._lastFastAt > 5000 &&
        now - (this._lastIceTry || 0) > PPNET.VP.ICE_RESTART_MS &&
        this._iceRestarts < PPNET.VP.ICE_RESTART_MAX) {
      this._iceRestarts++;
      this._lastIceTry = now;
      try { this._pc?.restartIce(); } catch { /* */ }
    }
    if (this._lastRelAt && now - this._lastRelAt > 12000 && this._lastFastAt &&
        now - this._lastFastAt > 12000) {
      this.onPeerGone(T('conn_lost'));
      return;
    }
    this._sendFast(dt, now);
    this._drainFast();
  }

  _sendFast(dt, now) {
    if (!this._tunnel && (!this._fast || !this._fastOpen)) return;
    // pose a POSE_HZ (o 30 en degradado), desde el RAF de la sesión XR
    const iv = 1 / this._poseHz;
    this._poseAcc += dt;
    const g = this.game;
    const hasPose = !!(g && g.camera && g.grips);
    let evs = null;
    // BALL_SNAP a 20 Hz mientras la bola vuela en MI lado (spec §5)
    if (this._ball.mine && (this._ball.state === 'own' || this._ball.state === 'auth')) {
      this._snapAcc += dt;
      if (this._snapAcc >= 1 / PPNET.VP.SNAP_HZ) {
        this._snapAcc = 0;
        evs = evs || [];
        evs.push({
          t: PPNET.VP.EV.SNAP, id: this._evId++, shot: this._ball.shot,
          tSnap: Math.round(this._clock.nowHost(now)),
          p: this._stateNet(g.ball.pos, null), v: this._velNet(g.ball.vel),
        });
        this._stats.snaps++;
        // SNAP no es fiable ni con ack (spec §5): va directo
        const pk = { seq: (this._seq + 1) & 0xffff, ack: this._ackP, ackBits: this._myAckBits(),
          sendTime: now, echoTime: this._echoTime, echoDelay: this._echoAt ? Math.min(65535, now - this._echoAt) : 0,
          pose: null, evs };
        this._seq = pk.seq;
        const buf = new ArrayBuffer(PPNET.VP.MAX_PKT);
        const n = PPNET.encodePacket(buf, { ...pk, yAnchor: DIMS.tableTopY });
        if (n) this._fastSend(buf.slice(0, n), now);
        evs = null;
      }
    }
    if (this._poseAcc < iv) {
      // los eventos de golpe/traspaso NO esperan al tick de pose (spec §5)
      if (this._pend.length) this._flushEvents(now);
      return;
    }
    this._poseAcc = 0;
    const pose = hasPose ? this._samplePose(g) : null;
    // reenvío de eventos no confirmados (spec §5: hasta ack, máx 8/paquete)
    const pendEvs = this._pend.slice(0, PPNET.VP.MAX_EVENTS).map((e) => e.ev);
    const pk = {
      seq: (this._seq + 1) & 0xffff,
      ack: this._ackP, ackBits: this._myAckBits(),
      sendTime: now, echoTime: this._echoTime,
      echoDelay: this._echoAt ? Math.min(65535, now - this._echoAt) : 0,
      pose,
      evs: pendEvs.length ? pendEvs : null,
    };
    this._seq = pk.seq;
    this._clock.markSent(now);
    const buf = new ArrayBuffer(PPNET.VP.MAX_PKT);
    const n2 = PPNET.encodePacket(buf, { ...pk, yAnchor: DIMS.tableTopY });
    if (!n2) return;
    for (const e of this._pend) e.seqs.push(pk.seq);
    this._fastSend(buf.slice(0, n2), now);
  }

  _flushEvents(now) {
    if (!this._pend.length || !this._fast || !this._fastOpen) return;
    const pk = {
      seq: (this._seq + 1) & 0xffff, ack: this._ackP, ackBits: this._myAckBits(),
      sendTime: now, echoTime: this._echoTime,
      echoDelay: this._echoAt ? Math.min(65535, now - this._echoAt) : 0,
      pose: null,
      evs: this._pend.slice(0, PPNET.VP.MAX_EVENTS).map((e) => e.ev),
    };
    this._seq = pk.seq;
    this._clock.markSent(now);
    const buf = new ArrayBuffer(PPNET.VP.MAX_PKT);
    const n = PPNET.encodePacket(buf, { ...pk, yAnchor: DIMS.tableTopY });
    if (!n) return;
    for (const e of this._pend) e.seqs.push(pk.seq);
    this._fastSend(buf.slice(0, n), now);
  }

  _fastSend(buf, now) {
    // v3.6.74 · r82 · vía TÚNEL: el paquete binario viaja encapsulado por
    // la DataConnection PeerJS (binario intacto; el receptor lo desenreda
    // en onData y entra por el MISMO _onFast). PeerJS serializa ArrayBuffer
    // como binario sin tocar — a cambio de fiabilidad/orden (SCTP fiable):
    // el jitter buffer y la FSM ya toleran ese régimen.
    if (this._tunnel) {
      try { this.conn.send({ k: 'f2', b: buf }); } catch { /* conn cerrándose */ }
      return;
    }
    try { this._fast.send(buf); } catch { /* DC cerrándose */ }
  }

  /** v3.6.74 · r82 · activa el túnel PeerJS para el canal fast */
  _enterTunnel() {
    if (this._tunnel || this.v2 !== 'pending') return;
    this._tunnel = true;
    this._stats.turn = true;   // reutiliza la marca «camino no directo»
    this._v2ChannelsUp();
  }

  /** muestreo de pose: cabeza (cámara XR) + manos (grips), en marco NET */
  _samplePose(g) {
    const out = this._poseSmp || (this._poseSmp = {
      hp: [0, 0, 0], hq: [0, 0, 0, 1], lp: [0, 0, 0], lq: [0, 0, 0, 1],
      rp: [0, 0, 0], rq: [0, 0, 0, 1], fl: 0,
    });
    const cam = g.camera;
    out.hp[0] = cam.position.x; out.hp[1] = cam.position.y; out.hp[2] = cam.position.z;
    out.hq[0] = cam.quaternion.x; out.hq[1] = cam.quaternion.y;
    out.hq[2] = cam.quaternion.z; out.hq[3] = cam.quaternion.w;
    let fl = 0;
    for (let i = 0; i < 2; i++) {
      const grip = g.grips[i];
      const tgt = i === 0 ? out.lp : out.rp;
      const tq = i === 0 ? out.lq : out.rq;
      if (grip) {
        tgt[0] = grip.position.x; tgt[1] = grip.position.y; tgt[2] = grip.position.z;
        tq[0] = grip.quaternion.x; tq[1] = grip.quaternion.y;
        tq[2] = grip.quaternion.z; tq[3] = grip.quaternion.w;
        fl |= 1 << i;                                  // mano rastreada
        if (i === g.paddleHand) fl |= 4;               // pala en esta mano
      }
    }
    // v3.6.74 · r82 · LATERALIDAD FÍSICA de la mano de la pala (bit 8):
    // el hueco del mando (slot 0/1) NO es la mano física — un jugador
    // diestro puede llevar la pala en el slot izquierdo. El avatar del
    // rival necesita la MANO REAL para su montura (mountQuatFor), si no
    // la pala del avatar nace rodada 90° en los jugadores con huecos
    // cruzados. (La pala del validador usa la POSICIÓN — sin cambio.)
    if (g.grips[g.paddleHand] && g.handOf && g.handOf[g.paddleHand] === 'left') fl |= 8;
    out.fl = fl;
    return out;
  }

  /** estado de bola a arrays de marco NET (espejo de emisión, en crudo) */
  _stateNet(v3, arr) {
    const T = DIMS.tableTopY;
    if (arr) {
      arr[0] = -v3.x; arr[1] = v3.y - T; arr[2] = -3.2 - v3.z;
      return arr;
    }
    return [-v3.x, v3.y - T, -3.2 - v3.z];
  }
  _velNet(v3) { return [-v3.x, v3.y, -v3.z]; }
  _spinNet(v3) { return [-v3.x, v3.y, -v3.z]; }

  _onFast(buf) {
    if (this.v2 !== 'ok') return;
    const now = performance.now();
    this._lastFastAt = now;
    const o = this._pktIn || (this._pktIn = {});
    o.yAnchor = DIMS.tableTopY;                    // ancla Y del tapete
    o.evs = [];
    const pkt = PPNET.decodePacket(buf, o);
    if (!pkt) return;
    // v3.6.74 · r82 · ECO NTP VIVO: la cabecera fast lleva echoTime/echoDelay
    // para que EL OTRO reconstruya t1 y refine el reloj (spec §4) — pero
    // estos dos campos nunca se escribían (solo a 0 en startV2): el refinado
    // NTP estaba MUERTO y el offset quedaba congelado en el ancla gruesa.
    // Con el ancla sesgada (fácil ±30-80 ms en Wi-Fi real) el validador
    // rechazaba por «tHit en el futuro» TODOS los golpes remotos del
    // partido, sin UI y sin recuperación. Ahora cada paquete recibido
    // alimenta el eco del siguiente.
    this._echoTime = pkt.sendTime;
    this._echoAt = now;
    this._onAckFrom(pkt);
    this._clock.onPacket(pkt, now);
    this._trackLoss(pkt.seq);
    if (pkt.pose) {
      // muestra del rival al jitter buffer (marco NET, reloj HOST)
      this._lastPoseAt = now;
      // v3.6.74 · r82 · SELLO POR CAPTURA, no por llegada: la muestra se
      // estampa con el sendTime del EMISOR reconstruido en reloj HOST
      // (mismo truco wrap-safe de NetClock.onPacket). Estampar con la
      // llegada retrasaba cada muestra un one-way entero (~17-50 ms) y el
      // validador juzgaba el golpe con la pose ANTERIOR al instante real.
      const tRef = this._clock.nowHost(now);
      const tHost = tRef + PPNET.wrapDiff(pkt.sendTime, PPNET.u32(tRef));
      this._jb.push(tHost, {
        hp: pkt.pose.hp, hq: pkt.pose.hq, lp: pkt.pose.lp, lq: pkt.pose.lq,
        rp: pkt.pose.rp, rq: pkt.pose.rq, fl: pkt.pose.fl,
      });
      this._jb.autoDelay(this._poseHz, this._clock.jitter);
    }
    for (const ev of pkt.evs) {
      if (this._seenEv.has(ev.id)) continue;             // dedupe (spec §10)
      this._seenEv.set(ev.id, now);
      if (this._seenEv.size > 256) {
        // poda del mapa de dedupe
        for (const [k, t] of this._seenEv) if (now - t > 5000) this._seenEv.delete(k);
      }
      if (ev.t !== PPNET.VP.EV.SNAP) this._fastIn.push(ev);
      else this._fastIn.push(ev);
    }
  }

  _onAckFrom(pkt) {
    // (a) confirma MIS eventos contenidos en paquetes ya acked (spec §5)
    for (let i = this._pend.length - 1; i >= 0; i--) {
      const e = this._pend[i];
      for (const s of e.seqs) {
        if (this._ackCovers(pkt.ack, pkt.ackBits, s)) { e.done = true; break; }
      }
      if (e.done) this._pend.splice(i, 1);
    }
    // (b) registra el seq recibido para mi própi ack/ackBits de envío
    this._ackP = pkt.seq;
    this._recvHist.push(pkt.seq);
    if (this._recvHist.length > 40) this._recvHist.shift();
  }
  _ackCovers(ack, bits, seq) {
    if (seq === ack) return true;
    const d = PPNET.wrapDiff(ack, seq);
    if (d > 0 && d <= 32) return ((bits >>> (d - 1)) & 1) === 1;
    return false;
  }
  /** máscara de los 32 seq anteriores al último recibido (spec §5) */
  _myAckBits() {
    let bits = 0;
    for (const s of this._recvHist) {
      if (s === this._ackP) continue;
      const d = PPNET.wrapDiff(this._ackP, s);
      if (d >= 1 && d <= 32) bits |= (1 << (d - 1));
    }
    return bits >>> 0;
  }
  _trackLoss(seq) {
    this._recvs++;
    const last = this._recvRing.length ? this._recvRing[this._recvRing.length - 1] : seq;
    if (PPNET.wrapDiff(seq, last) > 1) this._gaps += PPNET.wrapDiff(seq, last) - 1;
    this._recvRing.push(seq);
    if (this._recvRing.length > 128) {
      this._recvRing.shift();
      this._recvs = this._recvRing.length + this._gaps;
    }
    // degradación honesta: pérdida sostenida >10 % → pose 30 Hz (spec §11)
    const loss = this._gaps / Math.max(1, this._gaps + this._recvs);
    if (loss > PPNET.VP.LOSS_LOW) {
      this._lossLowT += 1;
      if (this._lossLowT > 90 && !this._degraded) { this._degraded = true; this._poseHz = PPNET.VP.POSE_HZ_LOW; }
    } else {
      this._lossLowT = Math.max(0, this._lossLowT - 2);
      if (this._degraded && loss < 0.04) { this._degraded = false; this._poseHz = PPNET.VP.POSE_HZ; }
    }
  }

  /* ---- eventos de bola del juego (llamados por c12) ---- */

  /** golpeo LOCAL (sagrado): mismo frame, sin esperar red (spec §1) */
  netLocalHit(isServe) {
    if (this.v2 !== 'ok') { this.sendHit(isServe); return; }
    const g = this.game;
    const nowH = this._clock.nowHost(performance.now());
    const ev = this._ball.localHit(isServe, {
      p: this._stateNet(g.ball.pos), v: this._velNet(g.ball.vel), s: this._spinNet(g.ball.spin),
    }, nowH);
    this._queueEv(ev);
    this._flushEvents(performance.now());   // inmediato, sin esperar tick
    this._stats.hits++;
    this._stats.maxBallSpeed = Math.max(this._stats.maxBallSpeed, g.ball.vel.length());
    this._syncOwnerFromBall();
    // el catch-up visual nace en el PRÓXIMO golpe del rival
    this._visOffMs = 0; this._visOff = null;
  }

  /** lanzamiento al aire del saque (visual para el rival, spec §10) */
  netLocalToss() {
    if (this.v2 !== 'ok') return;
    const g = this.game;
    const nowH = this._clock.nowHost(performance.now());
    const ev = this._ball.localToss({
      p: this._stateNet(g.ball.pos), v: this._velNet(g.ball.vel), s: [0, 0, 0],
    }, nowH);
    this._queueEv(ev);
    this._flushEvents(performance.now());
  }

  /** cruce limpio del plano de la red con bola propia → BALL_HANDOFF */
  watchOwnCross(ball) {
    if (this.v2 !== 'ok') return;
    const cz = DIMS.tableCenterZ;
    const pz = ball.__netZ === undefined ? ball.pos.z : ball.__netZ;
    ball.__netZ = ball.pos.z;
    if (this._ball.state !== 'own') return;
    if ((pz - cz) * (ball.pos.z - cz) > 0) return;      // sin cruce aún
    const nowH = this._clock.nowHost(performance.now());
    const ev = this._ball.crossedNet({
      p: this._stateNet(ball.pos), v: this._velNet(ball.vel), s: this._spinNet(ball.spin),
    }, nowH);
    if (ev) {
      this._queueEv(ev);
      this._flushEvents(performance.now());
      this._stats.handoffs++;
      this._syncOwnerFromBall();
    }
  }

  /** observación del fantasma (cruce sin traspaso → provisional, spec §7) */
  observeGhost(ball) {
    if (this.v2 !== 'ok') return;
    const cz = DIMS.tableCenterZ;
    const pz = ball.__netZ === undefined ? ball.pos.z : ball.__netZ;
    ball.__netZ = ball.pos.z;
    if (this._ball.state === 'ghost' &&
        (pz - cz) * (ball.pos.z - cz) <= 0) {
      this._ball.observeGhostCross(this._clock.nowHost(performance.now()));
    }
    if (this._ball.maybeProvisional(this._clock.nowHost(performance.now()))) {
      this._stats.provAuth++;
      this._syncOwnerFromBall();
    }
  }

  /** la bola murió en MI mitad (doble bote/fuera/red/…): reclamo (spec §7)
   *  r81: la identidad del rallye es rules.rallySeq (rallyId NO existía:
   *  undefined en los CLAIM → el libro de reclamos colisionaba a partir del
   *  primer punto y el marcador se congelaba en ambos extremos). */
  ballDiedLocal(winnerLocal, cause) {
    if (this.v2 !== 'ok') return null;
    const g = this.game;
    const r = g.rules;
    const rallyId = r.rallySeq;
    const isAuth = this._ballMineAtDeath();
    const dec = this._sync.localPoint(rallyId, winnerLocal, cause,
      r.scorePlayer, r.scoreAi, isAuth, performance.now());
    if (dec.send) {
      this._stats.claims++;
      this.sendRel(dec.send);
      this._claimFallback = { r: rallyId, t: performance.now() };
    }
    return dec;
  }

  _ballMineAtDeath() {
    // la autoridad al morir: la bola estaba en mi poder (auth/own/provisional)
    return this._ball.mine;
  }

  /** LET detectado localmente: con física idéntica en ambos extremos, los
   *  dos lados detectan el LET de sus botes (reales o fantasma) y aplican
   *  retryServe sin red — el siguiente saque re-alinea rallySeq. */
  retryLet(cause) {
    if (this.v2 !== 'ok') return { apply: true, send: null };
    return { apply: true, send: null };
  }

  _applyRemoteClaim(m, wMapped) {
    const g = this.game;
    if (!g) return;
    if (m.w === 'let') {
      // LET del rival (su mitad): repetir saque si mi árbitro no lo vio
      if (g.rules.state === 'rally') {
        g.processIntents(g.rules.retryServe(m.c || 'let'));
      }
      return;
    }
    // reclamo en perspectiva YA espejada (wMapped): imponer el punto
    g.processIntents(g.rules.forcePoint(wMapped, NetLink.remapCause(m.c,
      this.role === 'guest'), m.r));
  }

  _sendResync() {
    const r = this.game?.rules;
    if (!r) return;
    this._stats.disputes++;
    this.sendRel({
      k: 'resync', sp: r.scorePlayer, sa: r.scoreAi, sv: r.server,
      st: r.state, tp: r.totalPoints, gp: r.gamesPlayer, ga: r.gamesAi,
      gn: r.gameNo, fs: r.firstServer,
      // v3.6.74 · r82 · banderas del ÁRBITRO: sin ellas el resincronizado
      // seguía juzgando el rally con lastHitter/validBounce suyos (puntos
      // fantasma tras un RESYNC en pleno intercambio)
      lh: r.lastHitter || null, vb: !!r.validBounce,
    });
  }

  _applyResync(m) {
    const r = this.game?.rules;
    if (!r) return;
    this._sync.onResync();
    r.scorePlayer = m.sp; r.scoreAi = m.sa;
    r.server = m.sv; r.state = m.st; r.totalPoints = m.tp;
    r.gamesPlayer = m.gp; r.gamesAi = m.ga; r.gameNo = m.gn;
    r.firstServer = m.fs;
    // r82: el árbitro de mitad hereda las banderas del anfitrión
    if (m.lh !== undefined) r.lastHitter = m.lh;
    if (m.vb !== undefined) r.validBounce = !!m.vb;
  }

  /** intents de PUNTO local (processIntents, c12): enviar/suprimir
   *  r81: rallySeq como identidad del rallye (ver ballDiedLocal). */
  onLocalPointIntent(it) {
    if (this.v2 !== 'ok') return true;    // v1: siempre aplicar (host arbiter)
    const g = this.game;
    const isAuth = this._ballMineAtDeath();
    const dec = this._sync.localPoint(g.rules.rallySeq, it.winner, it.cause || '',
      g.rules.scorePlayer, g.rules.scoreAi, isAuth, performance.now());
    if (dec.send) {
      this._stats.claims++;
      this.sendRel(dec.send);
      // r82: rallyId NO existía (undefined) — la identidad real es rallySeq
      this._claimFallback = { r: g.rules.rallySeq, t: performance.now() };
    }
    return dec.apply;
  }

  onLocalRetryIntent(it) {
    return this.retryLet(it.cause || 'let');
  }

  /** saque determinista desde el marcador (spec §9): HELD del sacador */
  setServeHeld(serverLocal) {
    if (this.v2 !== 'ok') return;
    this._ball.setHeld(serverLocal === 'player');
    this._syncOwnerFromBall();
    const g = this.game;
    if (g && serverLocal !== 'player') {
      // bola del rival: quieta hasta su lanzamiento (visual honesta)
      g.ball.vel.set(0, 0, 0);
      g.ball.spin.set(0, 0, 0);
    }
  }

  _syncOwnerFromBall() {
    this.owner = this._ball.mine ? this.mySide() : this.oppSide();
  }

  _queueEv(ev) {
    // v3.6.74 · r82 · IDENTIDAD ÚNICA EN LA COLA (punto de estrangulamiento):
    // HIT (netLocalHit), TOSS (localToss) y HANDOFF (crossedNet) nacían SIN
    // id y el códec los sellaba con `e.id & 0xffff` = **0** — el dedupe del
    // receptor (`_seenEv.has(ev.id)`) se comía TODO evento tras el primero:
    // punto 1 «funcionaba» (la autoridad provisional de 300 ms enmascaraba
    // el traspaso deduplicado) y desde el punto 2 el receptor jamás veía
    // saques, golpes ni traspasos («veo las palas pero no puedo jugar la
    // bola»). Los SNAP ya traían id propio; el resto lo recibe AQUÍ.
    if (ev.id === undefined || ev.id === null) ev.id = this._evId++;
    this._pend.push({ ev, seqs: [], done: false });
    if (this._pend.length > 24) this._pend.shift();   // techo duro
  }

  /** drenado de eventos entrantes (c12 animate, antes de la física) */
  _drainFast() {
    if (!this._fastIn.length) return;
    const g = this.game;
    if (!g) { this._fastIn.length = 0; return; }
    const evs = this._fastIn;
    this._fastIn = [];
    for (const ev of evs) this._applyFastEv(ev, g);
  }

  _applyFastEv(ev, g) {
    const nowH = this._clock.nowHost(performance.now());
    if (ev.t === PPNET.VP.EV.SNAP) {
      // corrección suave del fantasma (sin ack, spec §5/§8)
      if (this._ball.state === 'ghost') {
        const p = NetLink.posFromNetArr(ev.p);
        const v = NetLink.vecFromNetArr(ev.v);
        g.ball.pos.lerp(p, 0.25);
        g.ball.vel.lerp(v, 0.12);
      }
      return;
    }
    if (ev.t === PPNET.VP.EV.HIT) {
      // validación del receptor (spec §12) — r81: pose en el marco NET y
      // en el instante del golpe (antes: marco crudo del emisor contra
      // ev.p espejado → TODO golpe remoto rechazado por distancia absurda)
      const pad = this._remotePadNet(ev.kind, ev.tHit);
      const ctx = {
        nowHost: nowH, lastShot: this._ball.shot, lastHitT: this._lastRemoteHitT,
        padPos: pad,
      };
      const v = this._val.hit(ev, ctx);
      if (!v.ok) {
        if (this._val.serious >= 3) { this._stats.suspect = true; }
        return;
      }
      this._lastRemoteHitT = ev.tHit;
      // r81 · posFromNetArr devuelve THREE.Vector3: el glue r79 lo INDEXABA
      // (p[0] = undefined → bola NaN → «no llega nada del rival»). copy().
      const p = NetLink.posFromNetArr(ev.p);
      const vl = NetLink.vecFromNetArr(ev.v);
      const sl = NetLink.spinFromNetArr(ev.s);
      g.ball.pos.copy(p);
      g.ball.vel.copy(vl);
      g.ball.spin.copy(sl);
      if (ev.kind === 2) {
        // lanzamiento al aire del saque del rival: SOLO visual (spec §10)
        // r81: la bola HELD se libera YA en mi lado (el rival la tiene en
        // el aire) — antes seguía holdLock y congelada hasta el golpe
        this._ball.state = 'ghost';
        this._ball.mine = false;
        g.ballMesh.visible = true;
        g._netTossLive = true;
        return;
      }
      // avance de nacimiento: dt·k con tope (spec §8)
      const ff = this._ball.onRemoteHit(ev, nowH, PPNET.VP.FF_K, PPNET.VP.FF_MAX);
      if (ff.adv > 0.001) {
        const ghostEvs = this._ghostEvs || (this._ghostEvs = []);
        stepPhysics(ff.adv, g.ball, [], ghostEvs);
        ghostEvs.length = 0;   // los botes del fantasma suenan por processEvents
      }
      this._stats.hits++;
      this._stats.maxBallSpeed = Math.max(this._stats.maxBallSpeed, g.ball.vel.length());
      // catch-up visual: la bola se dibuja retrasada interpDelay→0 en 200 ms
      this._visOffMs = PPNET.VP.CATCHUP_MS;
      // regla: saque (kind 1) o golpe de rallye (kind 0)
      if (ev.kind === 1) {
        g.rules.beginServeRally('ai');
      } else {
        g.processIntents(g.rules.registerPaddleHit('ai', true));   // r81: golpe remoto
      }
      // sonido del golpe del rival DESDE la simulación local (spec §8)
      g.audio.paddle(
        THREE.MathUtils.clamp(g.ball.pos.x / 2.5, -1, 1),
        Math.min(1, g.ball.vel.length() / 9),
      );
      this._syncOwnerFromBall();
      return;
    }
    if (ev.t === PPNET.VP.EV.HANDOFF) {
      // mi fantasma ya voló hasta ahora: comparar y corregir (spec §8)
      const mineNet = this._stateNet(g.ball.pos);
      const corr = this._ball.onHandoff(ev, mineNet, nowH);
      if (corr.kind === 'smooth' && corr.vec) {
        const p = NetLink.posFromNetArr(ev.p);
        const vl = NetLink.vecFromNetArr(ev.v);
        const sl = NetLink.spinFromNetArr(ev.s);
        g.ball.pos.copy(p);     // r81: Vector3 — copy, no indexado
        g.ball.vel.copy(vl);
        g.ball.spin.copy(sl);
        // absorber el salto en lo visual (decae en 80 ms)
        this._visOff = { x: -corr.vec[0], y: -corr.vec[1], z: -corr.vec[2],
          ms: corr.ms, t: corr.ms };
      } else if (corr.kind === 'snap') {
        const p = NetLink.posFromNetArr(ev.p);
        const vl = NetLink.vecFromNetArr(ev.v);
        const sl = NetLink.spinFromNetArr(ev.s);
        g.ball.pos.copy(p);     // r81: Vector3 — copy, no indexado
        g.ball.vel.copy(vl);
        g.ball.spin.copy(sl);
        this._stats.corrSnap++;
      } else {
        this._stats.corrNone++;
      }
      if (corr.kind === 'smooth') this._stats.corrSmooth++;
      this._syncOwnerFromBall();
    }
  }

  /** v3.6.73 · r81: pose de la pala del rival EN EL INSTANTE del evento,
   *  en el MISMO marco NET canónico de ev.p ([-x, y−T, −3.2−z]) para que
   *  la validación §12 compare distancias reales.
   *  · MARCO: la pose cruda del JB vive en el marco del EMISOR (con Y ya
   *    anclada a MI tapete por el códec). Antes se comparaba CONTRA ev.p
   *    (marco espejado, Y relativa) → distancia absurda (>2 m) y TODO
   *    golpe remoto rechazado: «no deja sacar ni jugar». Ahora la
   *    convertimos con poseToNetFrame (espejo exacto de _stateNet).
   *  · INSTANTE: se muestrea la muestra más próxima a ev.tHit (reloj
     *  host) — no la de reproducción retrasada del avatar (JB.sample).
   *  · MANO: en el golpe (kind 0/1) la PALA (fl&4); en el LANZAMIENTO del
   *    saque (kind 2) la mano LIBRE de la bola (la que lanza no es la que
   *    lleva la pala) — si sólo hay una mano rastreada, esa. */
  _remotePadNet(kind, tHit) {
    if (!this._jb || !this._jb.s.length) return null;
    const s = (tHit !== undefined && tHit !== null)
      ? this._jb.nearest(tHit, this._padSmp || (this._padSmp = {
          hp: [0, 0, 0], hq: [0, 0, 0, 1], lp: [0, 0, 0], lq: [0, 0, 0, 1],
          rp: [0, 0, 0], rq: [0, 0, 0, 1], fl: 0,
        }))
      : this._jb.s[this._jb.s.length - 1];
    if (!s) return null;
    const leftTrk = !!(s.fl & 1), rightTrk = !!(s.fl & 2), padLeft = !!(s.fl & 4);
    let hand;
    if (kind === 2) {
      // lanzamiento: la mano de la bola (la NO pala, si está rastreada)
      if (padLeft && rightTrk) hand = s.rp;
      else if (!padLeft && leftTrk) hand = s.lp;
      else hand = padLeft ? s.lp : s.rp;
    } else {
      hand = padLeft ? s.lp : s.rp;
    }
    if (!hand) return null;
    return NetLink.poseToNetFrame(hand);
  }

  /** delta visual de la bola (catch-up + correcciones) o null */
  visDelta(dt) {
    if (this.v2 !== 'ok') return null;
    let out = null;
    if (this._visOff && this._visOff.t > 0) {
      const k = this._visOff.t / this._visOff.ms;
      this._visOff.t -= dt * 1000;
      out = out || new THREE.Vector3();
      out.set(this._visOff.x * k, this._visOff.y * k, this._visOff.z * k);
      if (this._visOff.t <= 0) this._visOff = null;
    }
    if (this._visOffMs > 0) {
      const frac = this._visOffMs / PPNET.VP.CATCHUP_MS;
      this._visOffMs = Math.max(0, this._visOffMs - dt * 1000);
      const g = this.game;
      const v = g.ball.vel;
      const d = (this._jb.delayMs / 1000) * frac;
      out = out || new THREE.Vector3();
      out.set(-v.x * d, -v.y * d, -v.z * d);
    }
    return out;
  }

  /** muestra del avatar rival para el render (spec §6) */
  avatarSample(out) {
    if (this.v2 !== 'ok') return -1;
    const tHost = this._clock.nowHost(performance.now());
    return this._jb.sample(tHost, out);
  }

  pingMs() {
    if (this.v2 !== 'ok') return -1;
    return this._clock.rttStats().med;
  }
  hostNowMs() {
    return this.v2 === 'ok' ? this._clock.nowHost(performance.now()) : performance.now();
  }
  avatarStaleMs() {
    if (this.v2 !== 'ok' || !this._jb || !this._jb.s.length) return 1e9;
    return performance.now() - this._lastPoseAt;
  }
  degraded() { return this.v2 === 'ok' && this._degraded; }
  ballMine() { return this.v2 === 'ok' ? this._ball.mine : this.owner === this.mySide(); }
  ballState() { return this.v2 === 'ok' ? this._ball.state : 'legacy'; }
  v2Paused() { return this.v2 === 'ok' && (this._pausedSelf || this._pausedRemote); }
  pausedRemoteLong() {
    return this._pausedRemote && (performance.now() - this._pausedAt) > PPNET.VP.PAUSE_GRACE * 1000;
  }
  netReport() {
    if (this.v2 !== 'ok') return { mode: 'legacy-v1' };
    this._stats.tEnd = performance.now();
    return { mode: 'binario-v2', ...this._stats.summary(this._clock),
      val: { rejects: this._val.rejects, serious: this._val.serious,
             // r82: las CAUSAS de rechazo viajan en telemetría — diagnóstico
             // a distancia de un partido real fallido sin pedir logs al dueño
             log: this._val.log.slice(0, 8) } };
  }

  /** v3.6.74 · r82 · estado del enlace para HUD/QA/telemetría (visible:
   *  el dueño SABE en qué viaja la partida — P2P, túnel, v1 — y con qué
   *  salud de reloj/validador). window.__PP_NET = this en c12. */
  netInfo() {
    if (this.v2 !== 'ok') {
      return { v2: this.v2 || 'off', via: this.online ? 'sala' : '-',
        online: !!this.online, buildWarn: !!this._buildWarn };
    }
    const rs = this._clock ? this._clock.rttStats() : { med: 0, p95: 0, min: 0 };
    return {
      v2: 'ok', via: this._tunnel ? 'tunel' : 'p2p', online: true,
      buildWarn: !!this._buildWarn,
      rtt: rs.med, rttP95: rs.p95, jitter: Math.round(this._clock.jitter || 0),
      clockOff: Math.round(this._clock.offset || 0), clockReady: !!this._clock.ready,
      jbDelay: Math.round(this._jb.delayMs || 0), starves: this._jb.starves || 0,
      loss: Math.round((1 - (this._recvs || 0) / Math.max(1, (this._recvs || 0) + (this._gaps || 0))) * 100),
      ball: this._ball.state, shot: this._ball.shot, mine: this._ball.mine,
      val: { rej: this._val.rejects, serious: this._val.serious,
             log: this._val.log.slice(0, 6) },
    };
  }

  /** r82 · telemetría del enlace en CUALQUIER fin (no solo game-over):
   *  una sesión rota a mitad también deja huella diagnosticable */
  _teleReport(reason) {
    try {
      if (window.__PP_TELE && window.__PP_TELE.ev && this.v2) {
        const rep = this.netReport();
        rep.end = reason || 'fin';
        window.__PP_TELE.ev('net_match', rep);
      }
    } catch { /* telemetría jamás rompe la red */ }
  }

  _v2Fail(msg) {
    if (this.v2 === 'fail') return;
    this.v2 = 'fail';
    try { this._pc && this._pc.close(); } catch { /* */ }
    this._pc = null; this._fast = null; this._rel = null;
    this._fastOpen = this._relOpen = false;
    if (this._onVis) { document.removeEventListener('visibilitychange', this._onVis); this._onVis = null; }
    if (this._helloTO) { window.clearTimeout(this._helloTO); this._helloTO = null; }
    this.setStatus(this.online ? 'online' : 'off', msg);
    this.send({ k: 'v2off' });   // avisa al otro para que degrade igual
    this.game?.onNetStatus?.();
  }

  /** fimre del match (reliable) al terminar */
  sendMatchEnd(result) {
    if (this.v2 !== 'ok') return;
    this._stats.result = result;
    this._teleReport(result);
    this.sendRel({ k: 'mend', r: result });
  }

  sendRel(m) {
    if (this._rel && this._relOpen) {
      try { this._rel.send(JSON.stringify(m)); return; } catch { /* */ }
    }
    this.send(m);   // fallback: DataConnection PeerJS (fiable y ordenada)
  }

  onPeerGone(msg) {
    const wasOnline = this.online;
    if (wasOnline && this.v2) this._teleReport('peer_gone');   // r82: diagnóstico
    this.teardown();
    this.setStatus('off', wasOnline ? msg : '');
    if (wasOnline) this.game?.onNetEnded?.(msg);
  }


  cancel() {
    this.teardown();
    this.setStatus('off', '');
  }

  hangup() {
    // r79: firma honesta del abandono antes de cortar (spec §11)
    try { if (this.v2 === 'ok') this.sendMatchEnd('abandono'); } catch { /* */ }
    this.send({ k: 'bye' });
    this.onPeerGone('Has cerrado la conexión');
  }

  teardown() {
    // v3.6.71 · r79: limpieza del transporte v2
    try { if (this._onVis) document.removeEventListener('visibilitychange', this._onVis); } catch { /* */ }
    this._onVis = null;
    try { this._pc && this._pc.close(); } catch { /* */ }
    this._pc = null; this._fast = null; this._rel = null;
    this._fastOpen = this._relOpen = false;
    this.v2 = null;
    this._clock = null; this._jb = null; this._ball = null;
    this._sync = null; this._val = null; this._stats = null;
    this._pend = []; this._fastIn = []; this._seenEv = null;
    this._recvHist = null; this._mstart = null;
    this._pausedSelf = this._pausedRemote = false;
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
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { T } from './c00_pre_three.js';
import { PALA_BLADE_Y, PALA_GRIP_Y, PALA_SCALE } from './c01_modelos_3d.js';
import { DIMS, mountQuatFor } from './c02_cfg_escena.js';
import { stepPhysics } from './c05_colisiones_ia_golpeo.js';
import { PPNET } from './c09b_red_nucleo.js';
import * as THREE from 'three';
/* DEPS-FASE2-FIN */


/* =====================================================================
 *  ORQUESTADOR · sesión WebXR, mandos Quest 3, saque con mano libre,
 *  háptica y bucle principal
 * ===================================================================== */
// v2.28: arte de la cabecera del MENÚ PRINCIPAL (data URL JPEG incrustado
// por build_html.py — recorte del logo CRAZY PING PONG del arte del juego)
