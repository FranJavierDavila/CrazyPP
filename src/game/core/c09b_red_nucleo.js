export const PPNET = (() => {
  /* =====================================================================
   *  c09b_red_nucleo.js · PPNET — NÚCLEO DE RED MULTIJUGADOR BINARIO (r79)
   *  Spec: «Netcode multijugador online — Ping Pong VR (WebXR)» v1.0 ·
   *  26-oct-2026 (dictada por el dueño). Principios:
   *    1. El golpe propio es SAGRADO (se resuelve local, sin esperar red).
   *    2. AUTORIDAD POR MITAD DE MESA: quien tiene la bola en SU mitad
   *       decide botes, fallos y puntos de esa mitad.
   *    3. Lo visual del rival nunca afecta a la jugabilidad.
   *    4. Todo se mide (simulador de red + telemetría desde el hito 1).
   *  MÓDULO PURO: sin THREE, sin DOM, sin window — corre idéntico en el
   *  Quest (game.html), en QA Playwright (bucle local) y en Node
   *  (scripts/test_red_nucleo.mjs). Constantes VERSIONADAS (VP) — el
   *  HELLO compara PROTO y PHYS y rechaza pareja incompatible.
   *  =====================================================================
   *  Canales (net/transport):
   *    · fast     — RTCDataChannel {ordered:false, maxRetransmits:0}
   *                 (tipo UDP): paquetes binarios de pose + eventos.
   *    · reliable — RTCDataChannel {ordered:true}: JSON de control
   *                 (HELLO, READY, MATCH_START, POINT_CLAIM/ACK,
   *                 PAUSE/RESUME, RESYNC_STATE, MATCH_END, LEAVE).
   *  Espacio común de mesa: origen en el CENTRO de la superficie, x
   *  ancho, y arriba, z a lo largo; el HOST vive en -z y el invitado en
   *  +z (el espejo 180° de NetLink ya lo implementa — aquí todo viaja
   *  en crudo y cada extremo aplica su espejo UNA vez al recibir).
   *  ===================================================================== */

  /* ---------- 0 · PARÁMETROS (spec §17 — valores iniciales) ----------- */
  const VP = {
    PROTO: 1,             // versión del protocolo binario (HELLO)
    PHYS: 1,              // versión de ballPhysics compartida (HELLO)
    BUILD: '',            // hash de build (lo rellena el juego: VERSION)

    POSE_HZ: 60,          // frecuencia de pose (30 en degradado)
    POSE_HZ_LOW: 30,      // conexión degradada (pérdida sostenida >10 %)
    SNAP_HZ: 20,          // BALL_SNAP mientras la bola vuela en mi lado

    INTERP_MIN: 40,       // retraso de reproducción del avatar (ms)
    INTERP_MAX: 120,
    EXTRAP_MAX: 0.100,    // extrapolación máxima del avatar (s)

    FF_K: 0.6,            // avance de la bola al nacer (× tiempo en tránsito)
    FF_MAX: 0.120,        // avance máximo (s)

    CATCHUP_MS: 200,      // retraso visual inicial en el golpe del rival (ms)
    CORR_MIN: 0.02,       // <2 cm: nada
    CORR_MAX: 0.30,       // 2-30 cm: corregir + absorber salto (80 ms)
    CORR_SMOOTH: 0.080,   // >30 cm: salto directo + registro
    HANDOFF_TIMEOUT: 0.300, // s sin traspaso tras el cruce → autoridad provisional

    ICE_RESTART_MS: 10000,   // reintento de ICE antes de abandonar (ms)
    ICE_RESTART_MAX: 2,

    MAX_RTT_PAIR: 0.200,  // emparejamiento: RTT máximo aceptado (s) — spec §3.1

    MAX_BALL_SPEED: 30,   // validación: rapidez máxima aceptada (m/s)
    MAX_SPIN: 160,        // validación: giro máximo aceptado (rad/s)
    MIN_HIT_GAP: 0.150,   // no más de un golpe cada 150 ms
    HIT_NEAR_PAD: 0.60,   // el golpe ocurrió a <60 cm de la pala del rival

    LOSS_LOW: 0.10,       // pérdida sostenida >10 % → avisar y bajar pose

    HDR: 21,              // cabecera fast: 21 bytes exactos (spec §5)
    POSE: 31,             // bloque de pose: 31 bytes exactos (spec §5)
    MAX_EVENTS: 8,        // eventos reenviables por paquete (spec §5)
    MAX_PKT: 1200,        // tamaño absoluto máximo de paquete fast

    EV: { HIT: 1, HANDOFF: 2, SNAP: 3 },

    CLK_N: 16,            // muestras de reloj retenidas
    CLK_LOW: 4,           // mediana del offset de las 4 de menor RTT
    CLK_SMOOTH: 1.0,      // deslizar el offset como máximo 1 ms por segundo
    CLK_JUMP: 30,         // saltar el offset sólo si el error supera 30 ms

    COUNTDOWN_MS: 3000,   // MATCH_START: startAt = hostNow + 3000 (spec §3.8)
    PAUSE_GRACE: 3.0,     // s de pausa del rival antes de detener el reloj
    CLAIM_TIMEOUT: 0.7,   // s esperando el CLAIM del rival antes de aplicar el mío
  };

  /* ---------- 1 · matemáticas puras ---------------------------------- */
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const lerp = (a, b, t) => a + (b - a) * t;

  /** diferencia con envoltura u32 (los relojes viajan como u32 ms) */
  function wrapDiff(a, b) {
    let d = (a - b) >>> 0;
    if (d > 0x80000000) d -= 0x100000000;
    return d;                     // con signo, ms
  }
  const u32 = (x) => x >>> 0;

  function median(arr) {
    if (!arr.length) return 0;
    const s = arr.slice().sort((a, b) => a - b);
    const m = s.length >> 1;
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }

  /** cuaternión [x,y,z,w] normalizado (arrays planos, sin THREE) */
  function qNorm(q) {
    const l = Math.hypot(q[0], q[1], q[2], q[3]) || 1;
    return [q[0] / l, q[1] / l, q[2] / l, q[3] / l];
  }
  /** slerp de cuaterniones planos (mínimo camino) */
  function qSlerp(a, b, t) {
    let dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
    let bb = b;
    if (dot < 0) { bb = [-b[0], -b[1], -b[2], -b[3]]; dot = -dot; }
    if (dot > 0.9995) {
      return qNorm([
        lerp(a[0], bb[0], t), lerp(a[1], bb[1], t),
        lerp(a[2], bb[2], t), lerp(a[3], bb[3], t),
      ]);
    }
    const th = Math.acos(clamp(dot, -1, 1));
    const s = Math.sin(th);
    const wa = Math.sin((1 - t) * th) / s, wb = Math.sin(t * th) / s;
    return [
      a[0] * wa + bb[0] * wb, a[1] * wa + bb[1] * wb,
      a[2] * wa + bb[2] * wb, a[3] * wa + bb[3] * wb,
    ];
  }
  const pLerp = (a, b, t, out) => {
    out[0] = lerp(a[0], b[0], t); out[1] = lerp(a[1], b[1], t); out[2] = lerp(a[2], b[2], t);
    return out;
  };

  /* ---------- 2 · códec binario (spec §5) ----------------------------
   * Cabecera 21 B: [ver|flags u8][seq u16][ack u16][ackBits u32]
   *                [sendTime u32][echoTime u32][echoDelay u16][nEvs u16]
   * Pose 31 B (flag bit0): 3 nodos (cabeza, mano izq., mano der.) ×
   *   (pos 3×i16 @0,5 mm anclada al tapete + quat «smallest three» 32 bit)
   *   + 1 B de flags de pose (bit0: pala en mano IZQ; bit2: cabeza rastreada;
   *   bit3: manos rastreadas).
   * Eventos (flag bit1): u16 n + n × [tipo u8][eventId u16][carga]:
   *   HIT(0x01)     kind u8 · shot u16 · tHit u32 · pos/vel/spin 3×f32
   *   HANDOFF(0x02) shot u16 · tCross u32 · pos/vel/spin 3×f32
   *   SNAP(0x03)    shot u16 · tSnap u32 · pos 3×f32 · vel 3×f32
   * F flags: bit0 lleva pose · bit1 lleva eventos.                            */
  const F_POSE = 1, F_EV = 2;

  class Writer {
    constructor(buf) { this.dv = new DataView(buf); this.n = 0; }
    w8(v) { this.dv.setUint8(this.n, v); this.n += 1; return this; }
    w16(v) { this.dv.setUint16(this.n, v, true); this.n += 2; return this; }
    w32(v) { this.dv.setUint32(this.n, v >>> 0, true); this.n += 4; return this; }
    i16(v) { this.dv.setInt16(this.n, v, true); this.n += 2; return this; }
    f32(v) { this.dv.setFloat32(this.n, v, true); this.n += 4; return this; }
  }
  class Reader {
    constructor(buf) { this.dv = new DataView(buf); this.n = 0; this.len = buf.byteLength; }
    r8() { const v = this.dv.getUint8(this.n); this.n += 1; return v; }
    r16() { const v = this.dv.getUint16(this.n, true); this.n += 2; return v; }
    r32() { const v = this.dv.getUint32(this.n, true); this.n += 4; return v; }
    ri16() { const v = this.dv.getInt16(this.n, true); this.n += 2; return v; }
    rf32() { const v = this.dv.getFloat32(this.n, true); this.n += 4; return v; }
  }

  /** quat → 32 bit «smallest three»: 2 bit índice + 3×10 bit. Se ENVÍA el
   *  componente de MAYOR magnitud como índice y los tres MENORES (siempre
   *  en [-√3/2, √3/2], pues el mayor ≥ 0,5) mapeados a [0, 1023] con
   *  centro 511,5; el mayor se reconstruye con raíz y convención >= 0
   *  (negando el cuaternión entero si hace falta — q ≡ −q).              */
  const QSCALE = 511.5 / 0.8660254037844386;   // ≈ 590,53 unidades por 1
  function quatPack(q) {
    const n = qNorm(q);
    // convención: el componente DESCARTADO (el mayor) es >= 0
    let mi = 0, ma = Math.abs(n[0]);
    for (let i = 1; i < 4; i++) if (Math.abs(n[i]) > ma) { mi = i; ma = Math.abs(n[i]); }
    const s = n[mi] < 0 ? -1 : 1;
    let out = 0, sh = 20;
    for (let i = 0; i < 4; i++) {
      if (i === mi) continue;
      const v = clamp(Math.round(n[i] * s * QSCALE + 511.5), 0, 1023);
      out |= v << sh;
      sh -= 10;
    }
    out |= mi << 30;
    return out >>> 0;
  }
  function quatUnpack(u, out) {
    const mi = (u >>> 30) & 3;
    const rest = [];
    for (let i = 0, sh = 20; i < 3; i++, sh -= 10) {
      rest.push((((u >>> sh) & 1023) - 511.5) / QSCALE);
    }
    let sumSq = 0;
    for (const r of rest) sumSq += r * r;
    const s0 = Math.sqrt(Math.max(0, 1 - sumSq));
    const q = [0, 0, 0, 0];
    let k = 0;
    for (let i = 0; i < 4; i++) {
      if (i === mi) q[i] = s0; else q[i] = rest[k++];
    }
    out[0] = q[0]; out[1] = q[1]; out[2] = q[2]; out[3] = q[3];
    return out;
  }

  const P16 = 2000;   // 0,5 mm por unidad (spec §5: ±16 m con i16)
  function wPos(w, p, yAnchor) {
    for (let i = 0; i < 3; i++) {
      const v = (i === 1 && yAnchor) ? p[1] - yAnchor : p[i];
      w.i16(clamp(Math.round(v * P16), -32768, 32767));
    }
  }
  function rPos(r, out, yAnchor) {
    for (let i = 0; i < 3; i++) {
      const v = r.ri16() / P16;
      out[i] = (i === 1 && yAnchor) ? v + yAnchor : v;
    }
    return out;
  }

  /** codifica un paquete fast completo; devuelve el nº de bytes escritos */
  function encodePacket(buf, p) {
    const w = new Writer(buf);
    let flags = 0;
    if (p.pose) flags |= F_POSE;
    if (p.evs && p.evs.length) flags |= F_EV;
    w.w8((VP.PROTO << 4) | (flags & 15));
    w.w16(p.seq & 0xffff).w16(p.ack & 0xffff).w32(p.ackBits >>> 0);
    w.w32(u32(p.sendTime)).w32(u32(p.echoTime)).w16(p.echoDelay & 0xffff);
    const nEvs = p.evs ? Math.min(p.evs.length, VP.MAX_EVENTS) : 0;
    w.w16(nEvs);
    if (p.pose) {
      const yA = p.yAnchor || 0;
      // orden fijo: cabeza · mano izquierda · mano derecha
      wPos(w, p.pose.hp, yA); w.w32(quatPack(p.pose.hq));
      wPos(w, p.pose.lp, yA); w.w32(quatPack(p.pose.lq));
      wPos(w, p.pose.rp, yA); w.w32(quatPack(p.pose.rq));
      w.w8(p.pose.fl & 255);
    }
    for (let i = 0; i < nEvs; i++) {
      const e = p.evs[i];
      w.w8(e.t).w16(e.id & 0xffff);
      if (e.t === VP.EV.HIT) {
        w.w8(e.kind & 255).w16(e.shot & 0xffff).w32(u32(e.tHit));
        for (let k = 0; k < 3; k++) w.f32(e.p[k]);
        for (let k = 0; k < 3; k++) w.f32(e.v[k]);
        for (let k = 0; k < 3; k++) w.f32(e.s[k]);
      } else if (e.t === VP.EV.HANDOFF) {
        w.w16(e.shot & 0xffff).w32(u32(e.tCross));
        for (let k = 0; k < 3; k++) w.f32(e.p[k]);
        for (let k = 0; k < 3; k++) w.f32(e.v[k]);
        for (let k = 0; k < 3; k++) w.f32(e.s[k]);
      } else if (e.t === VP.EV.SNAP) {
        w.w16(e.shot & 0xffff).w32(u32(e.tSnap));
        for (let k = 0; k < 3; k++) w.f32(e.p[k]);
        for (let k = 0; k < 3; k++) w.f32(e.v[k]);
      }
    }
    if (w.n > VP.MAX_PKT) return 0;   // violación del tamaño: paquete nulo
    return w.n;
  }

  /** decodifica; si `out` existe reutiliza sus arrays (cero asignaciones) */
  function decodePacket(buf, out) {
    if (buf.byteLength < VP.HDR) return null;
    const r = new Reader(buf);
    const b0 = r.r8();
    const ver = (b0 >>> 4) & 15, flags = b0 & 15;
    if (ver !== VP.PROTO) return null;
    const o = out || {};
    o.seq = r.r16(); o.ack = r.r16(); o.ackBits = r.r32();
    o.sendTime = r.r32(); o.echoTime = r.r32(); o.echoDelay = r.r16();
    const nEvs = r.r16();
    o.pose = null; o.evs = [];
    if (flags & F_POSE) {
      const yA = o.yAnchor || 0;
      const pv = o._pose || (o._pose = {
        hp: [0, 0, 0], hq: [0, 0, 0, 1],
        lp: [0, 0, 0], lq: [0, 0, 0, 1],
        rp: [0, 0, 0], rq: [0, 0, 0, 1], fl: 0,
      });
      rPos(r, pv.hp, yA); quatUnpack(r.r32(), pv.hq);
      rPos(r, pv.lp, yA); quatUnpack(r.r32(), pv.lq);
      rPos(r, pv.rp, yA); quatUnpack(r.r32(), pv.rq);
      pv.fl = r.r8();
      o.pose = pv;
    }
    for (let i = 0; i < nEvs && i < VP.MAX_EVENTS + 8; i++) {
      const t = r.r8(), id = r.r16();
      if (t === VP.EV.HIT) {
        const kind = r.r8(), shot = r.r16(), tHit = r.r32();
        const p = [r.rf32(), r.rf32(), r.rf32()];
        const v = [r.rf32(), r.rf32(), r.rf32()];
        const s = [r.rf32(), r.rf32(), r.rf32()];
        o.evs.push({ t, id, kind, shot, tHit, p, v, s });
      } else if (t === VP.EV.HANDOFF) {
        const shot = r.r16(), tCross = r.r32();
        const p = [r.rf32(), r.rf32(), r.rf32()];
        const v = [r.rf32(), r.rf32(), r.rf32()];
        const s = [r.rf32(), r.rf32(), r.rf32()];
        o.evs.push({ t, id, shot, tCross, p, v, s });
      } else if (t === VP.EV.SNAP) {
        const shot = r.r16(), tSnap = r.r32();
        const p = [r.rf32(), r.rf32(), r.rf32()];
        const v = [r.rf32(), r.rf32(), r.rf32()];
        o.evs.push({ t, id, shot, tSnap, p, v });
      } else {
        return null;   // tipo desconocido: paquete inválido
      }
    }
    return o;
  }

  /* ---------- 3 · reloj compartido, RTT y jitter (spec §4) -----------
   * Sin pings aparte: la cabecera de CADA paquete fast lleva
   * sendTime/echoTime/echoDelay. Cada llegada produce una muestra NTP:
   *   t1 = mi sendTime que el otro acaba de ecoar (mi reloj, completo)
   *   t2 = sendTime del otro − echoDelay (su reloj al recibir mi paquete)
   *   t3 = sendTime del otro (su reloj al enviarme)
   *   t4 = mi reloj al recibir
   *   rtt    = (t4 − t1) − echoDelay
   *   offset = ((t2 − t1) + (t3 − t4)) / 2   (otro − mío)
   * La envoltura u32 de los relojes se resuelve con un ANCLA GRUESA por
   * el canal fiable (números completos, sin envoltura): guest/host
   * intercambian una vez su performance.now() y fijan offset±rtt/2; a
   * partir de ahí cada sendTime u32 del rival se reconstruye completo
   * prediciendo con el offset vigente y corrigiendo por envoltura. El
   * HOST es el reloj de la partida (isRef): sus marcas de tiempo ya son
   * de host; el invitado sella con local + offset.
   * Filtro: últimas 16 muestras → mediana del offset de las 4 de menor
   * RTT. Suavizado: deslizar ≤1 ms/s; salto sólo si el error >30 ms y
   * NUNCA durante un rallye (spec §4).                                     */
  class NetClock {
    constructor(isRef) {
      this.isRef = !!isRef;     // el host no aplica offset para sellar
      this.offset = 0;          // ms; otro − mío
      this.coarse = false;      // ancla gruesa recibida
      this.rtt = 0;
      this.jitter = 0;          // ms (EMA estilo RFC 3550)
      this.rttMin = Infinity;
      this.rtts = [];
      this.samples = [];        // {rtt, off}
      this._sent = [];          // ring de mis sendTime completos
      this._prevArr = 0;
      this._lastApply = 0;
      this._target = undefined;
      this.ready = false;
    }
    /** registro de envío para recuperar t1 completo desde el eco u32 */
    markSent(fullMs) {
      this._sent.push(fullMs);
      if (this._sent.length > 8) this._sent.shift();
    }
    _fullFromEcho(echoU32) {
      for (let i = this._sent.length - 1; i >= 0; i--) {
        if (u32(this._sent[i]) === echoU32) return this._sent[i];
      }
      return null;
    }
    /** ANCLA GRUESA por canal fiable (spec §3.6: ráfaga inicial de 8
     *  intercambios; aquí cada intercambio fija un candidato y el
     *  filtro de abajo elige). mySent/myRecv en MI reloj completo. */
    anchor(mySentFull, peerFull, myRecvFull) {
      const rtt = Math.max(0, myRecvFull - mySentFull);
      const off = peerFull - (mySentFull + rtt / 2);
      this.coarse = true;
      this._sample(rtt, off);
      return rtt;
    }
    /** llamada al llegar CADA paquete fast */
    onPacket(pkt, localNowMs) {
      // jitter de llegada (EMA de la desviación del intervalo esperado)
      if (this._prevArr) {
        const iv = Math.max(1, localNowMs - this._prevArr);
        this.jitter += (Math.abs(iv - 16.7) - this.jitter) / 16;
      }
      this._prevArr = localNowMs;
      const t1 = this._fullFromEcho(pkt.echoTime);
      if (t1 === null) return;                    // aún no ecoó nada mío
      // t3 completo: predecir con el offset vigente + corrección de envoltura
      const pred = localNowMs + this.offset;
      const t3full = pred + wrapDiff(pkt.sendTime, u32(pred));
      const t2 = t3full - pkt.echoDelay;
      const t4 = localNowMs;
      const rtt = (t4 - t1) - pkt.echoDelay;
      if (rtt < 0 || rtt > 3000) return;          // muestra anómala
      const off = ((t2 - t1) + (t3full - t4)) / 2;
      this._sample(rtt, off);
    }
    _sample(rtt, off) {
      this.rtt = rtt;
      if (rtt < this.rttMin) this.rttMin = rtt;
      this.rtts.push(rtt);
      if (this.rtts.length > 64) this.rtts.shift();
      this.samples.push({ rtt, off });
      if (this.samples.length > VP.CLK_N) this.samples.shift();
      const byRtt = this.samples.slice().sort((a, b) => a.rtt - b.rtt);
      const low = byRtt.slice(0, Math.min(VP.CLK_LOW, byRtt.length));
      this._target = median(low.map((s) => s.off));
      this.ready = this.samples.length >= 4;
    }
    /** aplica el offset objetivo con suavizado (espec §4) */
    apply(nowMs, inRally) {
      if (this._target === undefined) return;
      if (!this._lastApply) this._lastApply = nowMs;
      const err = this._target - this.offset;
      if (!this.ready) { this.offset = this._target; this._lastApply = nowMs; return; }
      if (Math.abs(err) > VP.CLK_JUMP && !inRally) {
        this.offset = this._target;               // salto sólo fuera de rallye
        this._lastApply = nowMs;
        return;
      }
      const maxStep = (VP.CLK_SMOOTH / 1000) * Math.max(0, nowMs - this._lastApply);
      this._lastApply = nowMs;
      this.offset += clamp(err, -maxStep, maxStep);
    }
    /** reloj del HOST en ms (el invitado suma su offset; el host es ref) */
    nowHost(localNowMs) { return this.isRef ? localNowMs : localNowMs + this.offset; }
    /** RTT mediana y p95 (ms) para telemetría e icono de ping */
    rttStats() {
      if (!this.rtts.length) return { med: 0, p95: 0, min: 0 };
      const s = this.rtts.slice().sort((a, b) => a - b);
      return {
        med: Math.round(median(this.rtts)),
        p95: Math.round(s[Math.min(s.length - 1, Math.floor(s.length * 0.95))]),
        min: Math.round(this.rttMin === Infinity ? 0 : this.rttMin),
      };
    }
  }

  /* ---------- 4 · jitter buffer del avatar (spec §6) -----------------
   * Reproducción con retraso controlado: sample(nowHost - interpDelay);
   * interpolación lineal de posición + slerp de rotación; sin datos →
   * extrapolar ≤100 ms con velocidad y después CONGELAR (contador de
   * vaciados para telemetría).                                        */
  class JitterBuf {
    constructor(cap) {
      this.cap = cap || 64;
      this.s = [];              // {t, hp,hq,lp,lq,rp,rq, vx,vy,vz}
      this.delayMs = VP.INTERP_MIN;
      this.starves = 0;         // veces que el buffer se vació (telemetría)
      this.extraps = 0;
      this._frozen = false;
    }
    push(tHost, sam) {
      // descartar muestras antiguas (paquetes desordenados)
      if (this.s.length && tHost <= this.s[this.s.length - 1].t) return false;
      this.s.push({ t: tHost, hp: sam.hp, hq: sam.hq, lp: sam.lp, lq: sam.lq, rp: sam.rp, rq: sam.rq, fl: sam.fl });
      if (this.s.length > this.cap) this.s.shift();
      this._frozen = false;
      return true;
    }
    clear() { this.s.length = 0; this._frozen = false; }
    /** retraso adaptativo: clamp(2·intervalo + 2·jitter, 40, 120) ms */
    autoDelay(poseHz, jitterMs) {
      const iv = 1000 / Math.max(1, poseHz);
      this.delayMs = clamp(2 * iv + 2 * jitterMs, VP.INTERP_MIN, VP.INTERP_MAX);
    }
    /** muestreo en tNowHost - delayMs; out = {hp,hq,lp,lq,rp,rq,fl}
     *  devuelve 0 OK · 1 extrapolada · 2 congelada · -1 vacío */
    sample(tNowHost, out) {
      const t = tNowHost - this.delayMs;
      if (!this.s.length) { this.starves++; return -1; }
      if (t <= this.s[0].t) { this._copy(this.s[0], out); return 0; }
      const last = this.s[this.s.length - 1];
      if (t >= last.t) {
        const gap = (t - last.t) / 1000;
        const prev2 = this.s.length > 1 ? this.s[this.s.length - 2] : null;
        if (gap <= VP.EXTRAP_MAX && prev2) {
          // EXTRAPOLACIÓN con la velocidad de las dos últimas muestras
          // (spec §6: hasta 100 ms, después congelar)
          const dtS = Math.max(1e-3, (last.t - prev2.t) / 1000);
          this._copy(last, out);
          out.hp[0] += ((last.hp[0] - prev2.hp[0]) / dtS) * gap;
          out.hp[1] += ((last.hp[1] - prev2.hp[1]) / dtS) * gap;
          out.hp[2] += ((last.hp[2] - prev2.hp[2]) / dtS) * gap;
          this.extraps++;
          return 1;
        }
        if (!this._frozen) this.starves++;
        this._frozen = true;
        this._copy(last, out);
        return 2;
      }
      // búsqueda del par que rodea t (buffer pequeño: lineal desde el final)
      let i = this.s.length - 1;
      while (i > 0 && this.s[i - 1].t > t) i--;
      const a = this.s[i - 1], b = this.s[i];
      const k = clamp((t - a.t) / Math.max(1e-6, b.t - a.t), 0, 1);
      pLerp(a.hp, b.hp, k, out.hp);
      const q = qSlerp(a.hq, b.hq, k); out.hq[0] = q[0]; out.hq[1] = q[1]; out.hq[2] = q[2]; out.hq[3] = q[3];
      pLerp(a.lp, b.lp, k, out.lp);
      const ql = qSlerp(a.lq, b.lq, k); out.lq[0] = ql[0]; out.lq[1] = ql[1]; out.lq[2] = ql[2]; out.lq[3] = ql[3];
      pLerp(a.rp, b.rp, k, out.rp);
      const qr = qSlerp(a.rq, b.rq, k); out.rq[0] = qr[0]; out.rq[1] = qr[1]; out.rq[2] = qr[2]; out.rq[3] = qr[3];
      out.fl = b.fl;
      return 0;
    }
    _copy(s, out) {
      for (let i = 0; i < 3; i++) { out.hp[i] = s.hp[i]; out.lp[i] = s.lp[i]; out.rp[i] = s.rp[i]; }
      for (let i = 0; i < 4; i++) { out.hq[i] = s.hq[i]; out.lq[i] = s.lq[i]; out.rq[i] = s.rq[i]; }
      out.fl = s.fl;
    }
    /** v3.6.73 · r81: muestra del buffer MÁS PRÓXIMA a tHost (la de mayor
     *  t ≤ tHost dentro de la ventana) — para VALIDAR un golpe en SU
     *  instante exacto (spec §12), no en el instante retrasado de
     *  reproducción del avatar (interpDelay 40-120 ms). Sin muestra dentro
     *  de la ventana devuelve null (el validador no puede juzgar).
     *  out opcional: {hp,hq,lp,lq,rp,rq,fl} reutilizable. */
    nearest(tHost, out, winMs) {
      const W = winMs || 250;
      if (!this.s.length) return null;
      let pick = null;
      for (let i = this.s.length - 1; i >= 0; i--) {
        if (this.s[i].t <= tHost) { pick = this.s[i]; break; }
      }
      if (!pick) pick = this.s[0];                     // todas futuras: la más antigua
      if (Math.abs(tHost - pick.t) > W) return null;   // desfasada: no juzga
      if (out) { this._copy(pick, out); return out; }
      return pick;
    }
  }

  /* ---------- 5 · FSM de la bola: autoridad por mitad (spec §7) -------
   * HELD(remoto) → GHOST_FLIGHT (simulación visual del saque/golpe del
   * rival) → (traspaso) AUTH_MY_SIDE → (mi golpe) OWN_FLIGHT →
   * (cruce limpio de la red) GHOST_FLIGHT → … · DEAD = punto terminado.
   * Regla de oro: SOLO puedo golpear con la bola en AUTH_MY_SIDE (o
   * OWN_FLIGHT justo tras mi golpe, blindado por cooldown).             */
  class BallAuth {
    constructor() {
      this.state = 'idle';      // idle|held|own|ghost|auth|dead
      this.holder = null;       // en 'held': 'me' | 'opp'
      this.mine = false;        // la física de la bola la conduzco YO
      this.shot = 0;            // nº de golpe del rallye (correlativo)
      this.rally = 0;           // rallyId (totalPoints en el momento del saque)
      this._crossT = 0;         // ms host del cruce pendiente de traspaso
      this._crossed = false;    // mi fantasma cruzó y espero BALL_HANDOFF
      this._provAuth = false;   // autoridad provisional activa (spec §7)
      this._catchT = 0;         // catch-up visual restante (ms)
      this._corr = null;        // corrección visual pendiente {vx,vy,vz,ms}
      this.lastHitHostT = 0;    // mi último golpe (para cadencia propia)
    }
    reset() {
      this.state = 'idle'; this.holder = null; this.mine = false;
      this.shot = 0; this._crossed = false; this._provAuth = false;
      this._catchT = 0; this._corr = null;
    }
    setHeld(mine) {
      this.state = 'held'; this.holder = mine ? 'me' : 'opp';
      this.mine = !!mine; this.shot = 0;
      this._crossed = false; this._provAuth = false; this._catchT = 0; this._corr = null;
    }
    /** golpeo LOCAL (sagrado): emite el evento y pasa a OWN_FLIGHT */
    localHit(isServe, state, nowHostMs) {
      this.shot++;
      this.state = 'own'; this.mine = true;
      this.lastHitHostT = nowHostMs;
      this._crossed = false; this._provAuth = false;
      return {
        t: VP.EV.HIT, kind: isServe ? 1 : 0, shot: this.shot,
        tHit: Math.round(nowHostMs), p: state.p, v: state.v, s: state.s,
      };
    }
    /** lanzamiento al aire del saque (visual para el rival, spec §10) */
    localToss(state, nowHostMs) {
      return {
        t: VP.EV.HIT, kind: 2, shot: this.shot,
        tHit: Math.round(nowHostMs), p: state.p, v: state.v, s: state.s,
      };
    }
    /** recibo el golpe del rival: nace mi fantasma; el glue lo avanza
     *  dt·k con tope (spec §8). Devuelve el avance a simular (s). */
    onRemoteHit(ev, nowHostMs, k, ffMax) {
      this.shot = ev.shot;
      this.state = 'ghost';
      this.mine = false;
      this._crossed = false; this._provAuth = false;
      const el = Math.max(0, nowHostMs - ev.tHit) / 1000;
      return { adv: Math.min(ffMax, el * k), el };
    }
    /** mi bola cruza limpiamente el plano de la red → BALL_HANDOFF */
    crossedNet(state, nowHostMs) {
      if (this.state !== 'own') return null;
      this.state = 'ghost'; this.mine = false;
      this._crossed = false;
      return {
        t: VP.EV.HANDOFF, shot: this.shot, tCross: Math.round(nowHostMs),
        p: state.p, v: state.v, s: state.s,
      };
    }
    /** recibo el traspaso: corrección según umbrales 2 cm / 30 cm (spec §8) */
    onHandoff(ev, myPos, nowHostMs) {
      this.shot = ev.shot;
      const wasGhost = this.state === 'ghost' || this.state === 'auth';
      this.state = 'auth'; this.mine = true;
      this._crossed = false;
      const dtErr = Math.max(0, nowHostMs - ev.tCross) / 1000;
      // error contra mi fantasma (el glue ya avanzó myPos hasta ahora)
      const ex = myPos[0] - ev.p[0], ey = myPos[1] - ev.p[1], ez = myPos[2] - ev.p[2];
      const err = Math.hypot(ex, ey, ez);
      let kind = 'snap';
      if (wasGhost && err < VP.CORR_MIN) kind = 'none';
      else if (wasGhost && err < VP.CORR_MAX) kind = 'smooth';
      return { kind, err, dtErr, vec: kind === 'smooth' ? [ex, ey, ez] : null, ms: VP.CORR_SMOOTH * 1000 };
    }
    /** SNAP del rival: corrección suave del fantasma (sin ack, spec §5) */
    onSnap() { /* el glue aplica el lerp; aquí sólo estadística */ }
    /** el fantasma cruzó y no llega traspaso: autoridad provisional */
    maybeProvisional(nowHostMs) {
      if (this.state !== 'ghost' || !this._crossed || this._provAuth) return false;
      if ((nowHostMs - this._crossT) / 1000 < VP.HANDOFF_TIMEOUT) return false;
      this.state = 'auth'; this.mine = true; this._provAuth = true;
      return true;
    }
    /** registra el cruce del fantasma (observado por el glue cada frame) */
    observeGhostCross(nowHostMs) {
      if (this.state === 'ghost' && !this._crossed) {
        this._crossed = true; this._crossT = nowHostMs;
      }
    }
    die() { this.state = 'dead'; this.mine = false; return true; }
    canHit() { return this.mine; }
  }

  /* ---------- 6 · validación de eventos recibidos (spec §12) ----------
   * Trampas groseras: rapidez/giro máximos, shot correlativo, cadencia
   * ≥150 ms y golpe a <60 cm de la pala del avatar rival. Tres fallos
   * graves en una partida → partida marcada como sospechosa.            */
  class Validator {
    constructor() { this.rejects = 0; this.serious = 0; this.log = []; }
    hit(ev, ctx) {
      const r = this._hit(ev, ctx);
      if (!r.ok) {
        this.rejects++;
        if (r.serious) this.serious++;
        if (this.log.length < 20) this.log.push(r.why);
      }
      return r;
    }
    _hit(ev, ctx) {
      const sp = Math.hypot(ev.v[0], ev.v[1], ev.v[2]);
      if (!(sp <= VP.MAX_BALL_SPEED)) return { ok: false, why: `vel ${sp.toFixed(1)} > ${VP.MAX_BALL_SPEED}`, serious: true };
      const sp2 = Math.hypot(ev.s[0], ev.s[1], ev.s[2]);
      if (!(sp2 <= VP.MAX_SPIN)) return { ok: false, why: `spin ${sp2.toFixed(0)} > ${VP.MAX_SPIN}`, serious: true };
      if (ctx.nowHost !== undefined && ev.tHit > ctx.nowHost + 60) {
        return { ok: false, why: 'tHit en el futuro', serious: true };
      }
      if (ctx.lastShot !== undefined && ev.shot !== ctx.lastShot + 1) {
        return { ok: false, why: `shot ${ev.shot} ≠ ${ctx.lastShot + 1}`, serious: true };
      }
      if (ctx.lastHitT !== undefined && ev.kind !== 2 &&
          (ev.tHit - ctx.lastHitT) < VP.MIN_HIT_GAP * 1000) {
        return { ok: false, why: 'cadencia <150 ms', serious: false };
      }
      if (ctx.padPos && ctx.padPos.length === 3) {
        const d = Math.hypot(ev.p[0] - ctx.padPos[0], ev.p[1] - ctx.padPos[1], ev.p[2] - ctx.padPos[2]);
        if (d > VP.HIT_NEAR_PAD) return { ok: false, why: `golpe a ${d.toFixed(2)} m de la pala`, serious: true };
      }
      return { ok: true, why: '' };
    }
  }

  /* ---------- 7 · simulador de red (solo desarrollo, spec §14) -------- */
  class NetSim {
    constructor(cfg) {
      this.lat = cfg.lat || 0;      // ms de latencia fija (uno-way)
      this.jit = cfg.jit || 0;      // ms de jitter
      this.loss = cfg.loss || 0;    // 0..1
      this.dup = cfg.dup || 0;      // 0..1
      this.reorder = cfg.reorder || 0;
      this.seed = (cfg.seed || 123456789) >>> 0;
      this.q = [];
    }
    _rnd() {   // xorshift determinista (tests reproducibles)
      let x = this.seed;
      x ^= x << 13; x >>>= 0; x ^= x >> 17; x ^= x << 5; x >>>= 0;
      this.seed = x;
      return x / 4294967296;
    }
    /** entrega programada de un paquete saliente */
    emit(buf, nowMs, deliver) {
      if (this._rnd() < this.loss) return;                  // perdido
      const d = this.lat + (this.jit ? (this._rnd() * 2 - 1) * this.jit : 0);
      const t = nowMs + Math.max(0, d);
      const n = this._rnd() < this.dup ? 2 : 1;
      for (let i = 0; i < n; i++) {
        const tt = t + (i > 0 ? 4 + this._rnd() * 12 : 0);
        this.q.push({ t: tt, buf, deliver });
      }
      if (this._rnd() < this.reorder && this.q.length > 2) {
        const i = this.q.length - 1;
        const j = this.q.length - 2;
        const tmp = this.q[i]; this.q[i] = this.q[j]; this.q[j] = tmp;
      }
    }
    pump(nowMs) {
      let n = 0;
      this.q.sort((a, b) => a.t - b.t);
      while (this.q.length && this.q[0].t <= nowMs) {
        const it = this.q.shift();
        it.deliver(it.buf);
        n++;
      }
      return n;
    }
  }

  /* ---------- 8 · telemetría por partida (spec §14) ------------------- */
  class NetStats {
    constructor(role) {
      this.role = role;
      this.t0 = 0; this.tEnd = 0;
      this.turn = false;          // pasó por TURN
      this.hits = 0; this.handoffs = 0; this.snaps = 0;
      this.corrNone = 0; this.corrSmooth = 0; this.corrSnap = 0;
      this.provAuth = 0;
      this.claims = 0; this.acks = 0; this.disputes = 0;
      this.maxBallSpeed = 0;
      this.result = '';           // 'win' | 'loss' | 'abandono' | ''
      this.suspect = false;
    }
    summary(clock) {
      const rs = clock ? clock.rttStats() : { med: 0, p95: 0, min: 0 };
      return {
        role: this.role, dur: this.tEnd ? Math.round((this.tEnd - this.t0) / 1000) : 0,
        rtt: rs, jitter: Math.round((clock && clock.jitter) || 0),
        turn: this.turn, hits: this.hits, handoffs: this.handoffs, snaps: this.snaps,
        corr: [this.corrNone, this.corrSmooth, this.corrSnap],
        provAuth: this.provAuth, claims: this.claims, acks: this.acks,
        disputes: this.disputes, vmax: Math.round(this.maxBallSpeed * 10) / 10,
        result: this.result, suspect: this.suspect,
      };
    }
  }

  /* ---------- 9 · libro de reclamos de punto (spec §7/§9) -------------
   * Quien tiene AUTORIDAD cuando la bola muere reclama (POINT_CLAIM con
   * rallyId, ganador, motivo, marcador y shotNumber). El otro responde
   * POINT_ACK si el reclamo encaja con SUS hechos. Reclamos simultáneos
   * del mismo rallyId: gana el primero que recibe el HOST.               */
  class MatchSync {
    constructor(role) {
      this.role = role;                 // 'host' | 'guest'
      this.pending = null;              // mi CLAIM en vuelo {r, w, c, sp, sa}
      this.applied = -1;                // último rallyId resuelto localmente
      this.appliedW = null;             // ganador LOCAL con el que lo resolví
      this.disputes = 0;
    }
    /** mi árbitro detectó un punto: AMBOS lados aplican su detección
     *  local (el fantasma es la misma física); el CLAIM/ACK confronta
     *  ambos resultados y el HOST resincroniza si discrepan (spec §7). */
    localPoint(r, w, c, sp, sa, isAuth, nowMs) {
      if (this.applied === r) return { apply: false, send: null };
      this.applied = r;
      this.appliedW = w;
      if (isAuth) {
        this.pending = { r, w, c, sp, sa };
        return { apply: true, send: { k: 'claim', r, w, c, sp, sa } };
      }
      return { apply: true, send: null };   // mi detección vale; el claim
                                            // del rival confirmará o rescindirá
    }
    /** llega CLAIM del rival; devuelve el ACK y si debo aplicar.
     *  mappedW = el ganador del claim YA espejado a MI perspectiva. */
    onClaim(cl, mappedW) {
      if (this.applied === cl.r) {
        const agree = (mappedW === undefined) || (cl.w === 'let') ||
          (this.appliedW === mappedW);
        return { ack: { k: 'ack', r: cl.r, agree }, apply: false, agree };
      }
      this.applied = cl.r;
      this.appliedW = mappedW || null;
      this.pending = null;
      return { ack: { k: 'ack', r: cl.r, agree: true }, apply: true, agree: true };
    }
    /** llega ACK a mi CLAIM; comparar marcadores (perspectiva propia) */
    onAck(ack) {
      if (!this.pending) return { ok: true };
      this.pending = null;
      if (ack.agree === false) { this.disputes++; return { ok: false, dispute: true }; }
      return { ok: true };
    }
    /** RESYNC del host (autoridad final): adoptar tal cual */
    onResync() { this.pending = null; this.applied = -1; this.appliedW = null; }
  }

  return {
    VP, clamp, lerp, wrapDiff, u32, median, qNorm, qSlerp, pLerp,
    Writer, Reader, quatPack, quatUnpack, encodePacket, decodePacket,
    F_POSE, F_EV,
    NetClock, JitterBuf, BallAuth, Validator, NetSim, NetStats, MatchSync,
  };
})();
