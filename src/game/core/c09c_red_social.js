export class RedSocial {   /* r87 · RED SOCIAL DEL PULSO — presencia + buzón de invitaciones (c09c)
   * PETICIÓN DEL DUEÑO: «medallón sobre el botón Multijugador con el número
   * de jugadores online con el juego funcionando» y «al pulsar, indicar
   * visualmente si hemos recibido una invitación y su código».
   *
   * CÓMO LO HACEN LOS DEMÁS (estudio previo):
   *  · Fortnite/Steam — badge numerado sobre la pestaña social + tarjeta de
   *    invitación con Aceptar/Rechazar. → NUESTRO MEDALLÓN numerado + tarjeta.
   *  · VRChat/Rec Room — lista de amigos en el reloj/menú, invitación a la
   *    instancia desde la lista. → NUESTRA LISTA de jugadores online.
   *  · PokerStars VR/Demeo — código de sala + unirse tecleándolo.
   *    → NUESTRO código existente (intacto) como respaldo del bucle manual.
   *
   * PIEZAS:
   *  · PID anónimo PERSISTENTE (localStorage pp_pid): la identidad mínima
   *    para recibir invitaciones — sin cuenta, sin PII, sin IP.
   *  · LATIDO cada 20 s al worker (/api/presencia): estado 'libre'|'sala'
   *    (con código)|'juego'. El worker purga a los 90 s — el medallón cuenta
   *    latidos frescos, nunca sesiones muertas.
   *  · BUZÓN: el anfitrión con sala abierta INVITA a un pid de la lista
   *    (POST /api/invita); el destinatario consulta /api/invita cada 20 s
   *    y el menú muestra la TARJETA de invitación con UNIRSE directo.
   *  · ADIÓS por sendBeacon en pagehide (baja inmediata, no espera la purga).
   *
   * ROBUSTEZ (regla de la casa): TODO tolerante a fallos — sin endpoint
   * (desarrollo sin mock) la capa queda OFF y el medallón no se pinta;
   * con red caída, cada latido reintenta solo; JAMÁS toca el netcode ni
   * el bucle de render (solo fetch espaciados + lectura de estado).
   * r87-QA: el worker REAL (crazypp-tele) sirve /api/presencia y /api/invita
   * desde esta ronda — verificado E2E contra producción (D1). */

/* =====================================================================
 *  v3.6.78 · r86 · RED SOCIAL DEL PULSO — PRESENCIA + BUZÓN DE INVITACIONES
 *  (petición del dueño: «medallón sobre el botón Multijugador con el número
 *  de jugadores online con el juego funcionando» y «al pulsar, indicar
 *  visualmente si hemos recibido una invitación y su código»).
 *
 *  CÓMO LO HACEN LOS DEMÁS (estudio previo):
 *   · Fortnite/Steam — badge numerado sobre la pestaña social + tarjeta de
 *     invitación con Aceptar/Rechazar. → NUESTRO MEDALLÓN numerado + tarjeta.
 *   · VRChat/Rec Room — lista de amigos en el reloj/menú, invitación a la
 *     instancia desde la lista. → NUESTRA LISTA de jugadores online.
 *   · PokerStars VR/Demeo — código de sala + unirse tecleándolo.
 *     → NUESTRO código existente (intacto) como respaldo del bucle manual.
 *
 *  PIEZAS:
 *   · PID anónimo PERSISTENTE (localStorage pp_pid): la identidad mínima
 *     para recibir invitaciones — sin cuenta, sin PII, sin IP.
 *   · LATIDO cada 20 s al worker (/api/presencia): estado 'libre'|'sala'
 *     (con código)|'juego'. El worker purga a los 90 s — el medallón cuenta
 *     latidos frescos, nunca sesiones muertas.
 *   · BUZÓN: el anfitrión con sala abierta INVITA a un pid de la lista
 *     (POST /api/invita); el destinatario consulta /api/invita cada 20 s
 *     y el menú muestra la TARJETA de invitación con UNIRSE directo.
 *   · ADIÓS por sendBeacon en pagehide (baja inmediata, no espera la purga).
 *
 *  ROBUSTEZ (regla de la casa): TODO tolerante a fallos — sin endpoint
 *  (desarrollo sin mock) la capa queda OFF y el medallón no se pinta;
 *  con red caída, cada latido reintenta solo; JAMÁS toca el netcode ni
 *  el bucle de render (solo fetch espaciados + lectura de estado).
 *  ===================================================================== */

  constructor(game) {
    this.game = game;
    this.pid = this._loadPid();
    this.on = false;            // endpoint vivo → latido/poll activos
    this.nOnline = 0;           // jugadores detectados (sin contar a YO)
    this.onlineOk = null;       // último poll del número con éxito
    this.lista = [];            // jugadores online [{pid, n, st, code}]
    this.invitas = [];          // buzón [{id, de, deN, code, hace}]
    this.invitaLeida = -1;      // mayor id ya visto (badge «nuevo»)
    this.lastErr = '';
    this._beatAcc = 1.5;        // primer latido casi inmediato
    this._pollNAcc = 4;         // primer poll del número a los 4 s
    this._pollIAcc = 6;         // primer poll del buzón a los 6 s
    this._pendBeat = null;      // en vuelo (anti-solape)
    this._pendN = null;
    this._pendI = null;
    this._pendPost = null;
    this._byeHecho = false;
    this._lastSt = '';          // último estado anunciado (latido inmediato al cambiar)
    this._onHide = () => { this._bye(true); };
    try {
      window.addEventListener('pagehide', this._onHide, { passive: true });
      window.addEventListener('beforeunload', this._onHide, { passive: true });
    } catch { /* */ }
  }

  /** pid anónimo persistente (16 hex). NUNCA sale del dispositivo salvo
   *  como clave de buzón — sin valor identificativo por sí solo. */
  _loadPid() {
    try {
      let p = localStorage.getItem('pp_pid');
      if (!p || !/^[a-f0-9]{16}$/.test(p)) {
        p = '';
        const h = '0123456789abcdef';
        for (let i = 0; i < 16; i++) p += h[(Math.random() * 16) | 0];
        localStorage.setItem('pp_pid', p);
      }
      return p;
    } catch { return 'anon-' + Date.now().toString(36); }
  }

  /** URL base de la API social: PP_SOCIAL_ENDPOINT manda (QA/banco); si
   *  no, se deriva del endpoint de telemetría (mismo worker): /api/tele
   *  → /api. Vacío = capa OFF silenciosa. */
  base() {
    try {
      if (typeof window !== 'undefined' && window.PP_SOCIAL_ENDPOINT) {
        return String(window.PP_SOCIAL_ENDPOINT).replace(/\/+$/, '');
      }
      const ep = (typeof window !== 'undefined' && window.PP_TELEMETRY_ENDPOINT) || '';
      if (!ep) return '';
      const m = ep.match(/^(.*\/)api\/tele\/?$/);
      return m ? m[1] + 'api' : '';
    } catch { return ''; }
  }

  nombre() {
    try { return ppPlayerName() || 'Jugador'; } catch { return 'Jugador'; }
  }

  /** estado que viaja en el latido: libre | sala (code) | juego */
  estado() {
    const net = this.game && this.game.net;
    if (!net) return { st: 'libre' };
    if (net.online || net.status === 'online') return { st: 'juego' };
    if (net.status === 'waiting' && net.code) return { st: 'sala', code: net.code };
    return { st: 'libre' };
  }

  async _fetch(path, opts, pendKey, ms) {
    const base = this.base();
    if (!base) return null;
    const ctrl = new AbortController();
    const to = setTimeout(() => { try { ctrl.abort(); } catch { /* */ } }, ms || 8000);
    this[pendKey] = ctrl;
    try {
      const r = await fetch(base + path, Object.assign({ signal: ctrl.signal }, opts));
      if (!r.ok) { this.lastErr = 'HTTP ' + r.status; return null; }
      const txt = await r.text();
      this.lastErr = '';
      try { return txt ? JSON.parse(txt) : {}; } catch { return {}; }
    } catch (e) {
      this.lastErr = (e && e.name === 'AbortError') ? 'timeout' : 'red';
      return null;
    } finally {
      clearTimeout(to);
      this[pendKey] = null;
    }
  }

  /* ------------------------- LATIDO DE PRESENCIA ---------------------- */
  async latido() {
    if (this._pendBeat) return;
    const e = this.estado();
    const body = JSON.stringify({
      pid: this.pid, n: this.nombre(), v: (typeof VERSION !== 'undefined') ? VERSION : '',
      st: e.st, code: e.code || '',
    });
    this._pendBeat = true;
    try {
      await this._fetch('/presencia', {
        method: 'POST', headers: { 'Content-Type': 'text/plain;charset=UTF-8' }, body,
      }, '_pendBeatCtl', 8000);
      this.on = this.lastErr === '';
    } finally {
      this._pendBeat = false;
    }
  }

  /** baja inmediata (pagehide): sendBeacon si existe, fetch keepalive si no */
  _bye(forzado) {
    if (this._byeHecho || !this.pid) return;
    if (!forzado) return;                     // sólo en el cierre real
    this._byeHecho = true;
    const base = this.base();
    if (!base) return;
    const body = JSON.stringify({ pid: this.pid, bye: 1 });
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(base + '/presencia',
          new Blob([body], { type: 'text/plain;charset=UTF-8' }));
        return;
      }
    } catch { /* */ }
    try {
      fetch(base + '/presencia', {
        method: 'POST', keepalive: true,
        headers: { 'Content-Type': 'text/plain;charset=UTF-8' }, body,
      }).catch(() => { /* */ });
    } catch { /* */ }
  }

  /* -------------------- POLLS (número + lista + buzón) ---------------- */
  async pollNumero() {
    if (this._pendN) return;
    this._pendN = true;
    try {
      const r = await this._fetch('/presencia', null, '_pendNCtl', 6000);
      if (r && r.ok && typeof r.n === 'number') {
        // el worker cuenta TODOS los latidos (yo incluido): el medallón y el
        // pie muestran LOS OTROS — resta 1 (mi latido está vivo si hay dato).
        const nuevo = Math.max(0, (r.n | 0) - 1);
        if (nuevo !== this.nOnline) { this.nOnline = nuevo; this._avisaUi(); }
        else this.nOnline = nuevo;
        this.onlineOk = true;
      }
    } finally {
      this._pendN = false;
    }
  }

  async pollLista() {
    if (this._pendN) return;
    this._pendN = true;
    try {
      const r = await this._fetch('/presencia?lista=1', null, '_pendNCtl', 7000);
      if (r && r.ok && Array.isArray(r.jugadores)) {
        this.lista = r.jugadores.filter((j) => j && j.pid && j.pid !== this.pid);
        const nuevo = Math.max(0, (r.n | 0) - 1);
        if (nuevo !== this.nOnline) { this.nOnline = nuevo; this._avisaUi(); }
        else this.nOnline = nuevo;
        this.onlineOk = true;
      }
    } finally {
      this._pendN = false;
    }
  }

  async pollInvitas() {
    if (this._pendI) return;
    this._pendI = true;
    try {
      const r = await this._fetch('/invita?pid=' + encodeURIComponent(this.pid),
        null, '_pendICtl', 7000);
      if (r && r.ok && Array.isArray(r.invitas)) {
        const antes = this.invitas.length;
        this.invitas = r.invitas.slice(0, 8);
        if (this.invitas.length !== antes) this._avisaUi();
      } else if (r && r.ok) {
        if (this.invitas.length) this._avisaUi();
        this.invitas = [];
      }
    } finally {
      this._pendI = false;
    }
  }

  /** INVITAR: manda mi sala (code) al pid elegido. Requiere sala abierta. */
  async invitar(pidRival) {
    const net = this.game && this.game.net;
    if (!net || net.status !== 'waiting' || !net.code) return false;
    if (this._pendPost) return false;
    this._pendPost = true;
    try {
      const r = await this._fetch('/invita', {
        method: 'POST', headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
        body: JSON.stringify({
          de: this.pid, deN: this.nombre(), para: pidRival, code: net.code,
        }),
      }, '_pendPostCtl', 8000);
      return !!(r && r.ok);
    } finally {
      this._pendPost = false;
    }
  }

  /** UNIRSE desde la invitación: consume el buzón y entra en la sala. */
  async aceptar() {
    const inv = this.invitas[0];
    if (!inv || !inv.code) return false;
    this._borrarBuzon();
    const g = this.game;
    if (!g || !g.net) return false;
    try {
      g._mjMode = 'normal';                 // el panel de sala/código visible
      g.net.joinRoom(inv.code);
      return true;
    } catch { return false; }
  }

  /** DESCARTAR: vacía el buzón (el worker borra TODAS las del pid). */
  async descartar() {
    this.invitas = [];
    this._borrarBuzon();
  }

  _borrarBuzon() {
    try {
      const base = this.base();
      if (!base) return;
      fetch(base + '/invita?pid=' + encodeURIComponent(this.pid),
        { method: 'DELETE', mode: 'cors' }).catch(() => { /* */ });
    } catch { /* */ }
  }

  hayInvitas() { return this.invitas.length > 0; }

  /* ¿hay medallón vivo? (presencia detectada o buzón con algo) */
  medallonVivo() {
    return this.on && (this.nOnline > 0 || this.invitas.length > 0);
  }

  /* r87 · AVISO DE UI: el menú repinta cuando el medallón cambia de valor
   * (entró/salió gente, invitación nueva) — drawMenu es caro: sólo en
   * cambio real y con el menú abierto. Si está cerrado, el mensaje del
   * árbitro (rules.message) avisa una vez por invitación nueva. */
  _avisaUi() {
    const g = this.game;
    if (!g) return;
    try {
      if (g.menuOpen) { if (g.drawMenu) g.drawMenu(); }
      else if (this.invitas.length && this.invitas[0].id !== this._avisadaId) {
        this._avisadaId = this.invitas[0].id;
        if (g.rules) g.rules.message = (typeof T === 'function') ? T('rs_aviso') : '¡Invitación recibida! Menú ▸ Multijugador';
      }
    } catch (e) { /* nunca rompe */ }
  }

  /* ------------------------------ TICK ------------------------------- */
  tick(dt) {
    const base = this.base();
    if (!base || !this.pid) { this.on = false; return; }
    this._beatAcc += dt;
    this._pollNAcc += dt;
    this._pollIAcc += dt;
    // r86 · cambio de estado (sala creada/cerrada, entra en partida) →
    // LATIDO INMEDIATO: la sala se anuncia en el worker en el mismo frame
    // que nace (si no, «invitar» chocaría con el anuncio atrasado hasta
    // 20 s y el worker la rechazaría como sala no activa).
    const e = this.estado();
    const stKey = e.st + (e.code || '');
    if (stKey !== this._lastSt) {
      this._lastSt = stKey;
      this._beatAcc = 20;                    // fuerza el latido de abajo
    }
    if (this._beatAcc >= 20) {
      this._beatAcc = 0;
      this.latido().catch(() => { /* */ });
    }
    if (this._pollNAcc >= (this.nOnline > 0 ? 30 : 10)) {
      this._pollNAcc = 0;
      // intervalo ADAPTATIVO: sin gente detectada se sondea cada 10 s (el
      // medallón aparece pronto); con gente, 30 s basta (el dato no baila).
      // la lista sólo interesa con el submenú multi abierto (sala waiting):
      // el resto del tiempo, número barato.
      const quieroLista = this.game && this.game.net &&
        this.game.net.status === 'waiting';
      (quieroLista ? this.pollLista() : this.pollNumero()).catch(() => { /* */ });
    }
    if (this._pollIAcc >= 20) {
      this._pollIAcc = 0;
      // el buzón se consulta SIEMPRE (el aviso vive en el HUB, no sólo con
      // el menú abierto) — consulta ligera, respuesta pequeña.
      this.pollInvitas().catch(() => { /* */ });
    }
  }
}
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { T, ppPlayerName } from './c00_pre_three.js';
/* DEPS-FASE2-FIN */

