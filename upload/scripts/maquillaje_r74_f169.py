#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""maquillaje_r74_f169.py — FASE 169 «EL MULTIJUGADOR EN TRES ZONAS» (r74).

Petición del dueño: el apartado Multijugador no se entiende (dos modos que
también muestran «introducir código», y un tercer botón de código suelto).
Rediseño en TRES ZONAS:
  · ZONA CREAR PARTIDA — los dos modos (Duelo Normal · Duelos Locos) crean
    sala directamente, eligiendo PÚBLICA (se anuncia a los conectados y se
    publica en «Partidas disponibles») o PRIVADA (sólo entra con código).
  · ZONA PARTIDAS DISPONIBLES — listado VIVO de salas públicas del pulso:
    modalidad + nombre del retador + ENTRAR.
  · ZONA SALA PRIVADA — el código que te pasó el creador.

Conducta: la modalidad y la VISIBILIDAD viajan en el LATIDO de presencia
(net.modoSala / net.visSala → worker mj/vis; PRIVADA por defecto — una
sala jamás se anuncia salvo elección expresa). Las invitaciones (r87)
llevan también su modalidad y «aceptar» abre el modo correcto.
Worker (worker-tele/worker.js): ALTER idempotente + passthrough mj/vis.
"""
import pathlib
import sys

RAIZ = pathlib.Path('/home/z/my-project/upload/src/game/core')
C09 = RAIZ / 'c09_red_netlink.js'
C09C = RAIZ / 'c09c_red_social.js'
C12 = RAIZ / 'c12_pingponggame.js'
C00 = RAIZ / 'c00_pre_three.js'
WORKER = pathlib.Path('/home/z/my-project/upload/scripts/worker-tele/worker.js')

PARCHES = []


def p(nombre, fichero, ancla, nuevo, veces=1):
    PARCHES.append((nombre, fichero, ancla, nuevo, veces))


# ── 169.1 · netlink: modo + visibilidad de MI sala ──
p('169.1 · net.modoSala/visSala', C09,
  """    this.role = null;          // 'host' | 'guest'
    this.status = 'off';       // off|creating|waiting|joining|online|error""",
  """    this.role = null;          // 'host' | 'guest'
    // r74 · FASE 169 · modalidad y visibilidad de MI sala (viajan en el
    // latido de presencia): el listado público sólo anuncia vis='pub'.
    // PRIVADA por defecto: una sala jamás se anuncia salvo elección.
    this.modoSala = 'normal';  // 'normal' | 'duelos'
    this.visSala = 'pri';      // 'pub' | 'pri'
    this.status = 'off';       // off|creating|waiting|joining|online|error""")

# ── 169.2 · presencia: el estado lleva modalidad + visibilidad ──
p('169.2a · estado() con mj/vis', C09C,
  """    if (net.online || net.status === 'online') return { st: 'juego' };
    if (net.status === 'waiting' && net.code) return { st: 'sala', code: net.code };
    return { st: 'libre' };""",
  """    if (net.online || net.status === 'online') return { st: 'juego' };
    if (net.status === 'waiting' && net.code) {
      // r74 · FASE 169 · la sala anuncia SU modalidad y visibilidad
      return { st: 'sala', code: net.code,
        mj: net.modoSala === 'duelos' ? 'duelos' : 'normal',
        vis: net.visSala === 'pub' ? 'pub' : 'pri' };
    }
    return { st: 'libre' };""")

p('169.2b · latido viaja mj/vis', C09C,
  """    const body = JSON.stringify({
      pid: this.pid, n: this.nombre(), v: (typeof VERSION !== 'undefined') ? VERSION : '',
      st: e.st, code: e.code || '',
    });""",
  """    const body = JSON.stringify({
      pid: this.pid, n: this.nombre(), v: (typeof VERSION !== 'undefined') ? VERSION : '',
      st: e.st, code: e.code || '',
      mj: e.mj || 'normal', vis: e.vis || 'pri',   // r74 · FASE 169
    });""")

# ── 169.3 · invitaciones con modalidad ──
p('169.3a · invitar lleva mj', C09C,
  """        body: JSON.stringify({
          de: this.pid, deN: this.nombre(), para: pidRival, code: net.code,
        }),""",
  """        body: JSON.stringify({
          de: this.pid, deN: this.nombre(), para: pidRival, code: net.code,
          k: 'inv',                                        // r74 · FASE 169
          mj: net.modoSala === 'duelos' ? 'duelos' : 'normal',
        }),""")

p('169.3b · aceptar abre el modo de la invitación', C09C,
  """      g._mjMode = 'normal';                 // el panel de sala/código visible""",
  """      // r74 · FASE 169 · la invitación viaja con SU modalidad
      g._mjMode = (inv.mj === 'duelos') ? 'duelos' : 'normal';""")

# ── 169.4 · listado público + lista fresca en el landing ──
p('169.4 · publicas() + pideLista()', C09C,
  """  hayInvitas() { return this.invitas.length > 0; }""",
  """  hayInvitas() { return this.invitas.length > 0; }

  /** r74 · FASE 169 · partidas PÚBLICAS disponibles ahora mismo: salas
   *  vivas del pulso anunciadas con vis='pub' — las PRIVADAS jamás se
   *  listan (y si el worker viejo no manda vis, tampoco: seguro). */
  publicas() {
    return (this.lista || []).filter((j) =>
      j && j.st === 'sala' && j.code && j.vis === 'pub');
  }

  /** r74 · FASE 169 · el landing MULTIJUGADOR quiere la lista fresca:
   *  fuerza pollLista (el tick también la sondea con la página abierta). */
  pideLista() {
    if (!this.on) return;
    this.pollLista().catch(() => { /* */ });
  }""")

p('169.4b · tick: lista viva en el landing MULTI', C09C,
  """    if (this._pollNAcc >= (this.nOnline > 0 ? 30 : 10)) {""",
  """    // r74 · FASE 169 · con el landing MULTI abierto la lista se sondea
    // cada 6 s («partidas disponibles en ese momento»); el resto, igual.
    if (this._pollNAcc >= ((this.game && this.game.menuPage === 'multi')
      ? 6 : (this.nOnline > 0 ? 30 : 10))) {""")

p('169.4c · tick: quieroLista incluye el landing', C09C,
  """      const quieroLista = this.game && this.game.net &&
        this.game.net.status === 'waiting';""",
  """      const quieroLista = (this.game && this.game.net &&
        this.game.net.status === 'waiting') ||
        (this.game && this.game.menuPage === 'multi');""")

# ── 169.5 · worker: ALTER idempotente + passthrough mj/vis ──
p('169.5a · socialInit ALTERs', WORKER,
  """  await env.DB.batch(SOCIAL_SCHEMA.map((s) => env.DB.prepare(s)));
  socialListo = true;""",
  """  await env.DB.batch(SOCIAL_SCHEMA.map((s) => env.DB.prepare(s)));
  // r74 · FASE 169 · MODALIDAD + VISIBILIDAD de las salas (listado público
  // del Multijugador) y MODALIDAD de las invitaciones. ALTER idempotente:
  // si la columna ya existe el error se ignora — nunca se borra nada.
  for (const ALTER of [
    "ALTER TABLE presencia ADD COLUMN mj TEXT",
    "ALTER TABLE presencia ADD COLUMN vis TEXT",
    "ALTER TABLE invitas ADD COLUMN mj TEXT",
  ]) {
    try { await env.DB.prepare(ALTER).run(); } catch (e) { /* ya existe */ }
  }
  socialListo = true;""")

p('169.5b · presencia POST guarda mj/vis', WORKER,
  """      const st = ["libre", "sala", "juego"].includes(cuerpo.st) ? cuerpo.st : "libre";
      const code = texto(cuerpo.code, 12).toUpperCase();
      await env.DB.prepare(
        `INSERT INTO presencia (pid, n, v, st, code, t) VALUES (?, ?, ?, ?, ?, ?)
         ON CONFLICT(pid) DO UPDATE SET n=excluded.n, v=excluded.v,
           st=excluded.st, code=excluded.code, t=excluded.t`
      ).bind(pid, n, v, st, st === "sala" ? code : "", ahora).run();""",
  """      const st = ["libre", "sala", "juego"].includes(cuerpo.st) ? cuerpo.st : "libre";
      const code = texto(cuerpo.code, 12).toUpperCase();
      // r74 · FASE 169 · modalidad ('normal'|'duelos') y visibilidad de la
      // sala ('pub'|'pri'): PRIVADA por defecto — el listado público sólo
      // muestra salas anunciadas expresamente como PÚBLICAS.
      const mj = cuerpo.mj === "duelos" ? "duelos" : "normal";
      const vis = cuerpo.vis === "pub" ? "pub" : "pri";
      await env.DB.prepare(
        `INSERT INTO presencia (pid, n, v, st, code, mj, vis, t) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
         ON CONFLICT(pid) DO UPDATE SET n=excluded.n, v=excluded.v,
           st=excluded.st, code=excluded.code, mj=excluded.mj, vis=excluded.vis, t=excluded.t`
      ).bind(pid, n, v, st, st === "sala" ? code : "",
        st === "sala" ? mj : "normal", st === "sala" ? vis : "pri", ahora).run();""")

p('169.5c · presencia GET lista devuelve mj/vis', WORKER,
  """      const { results } = await env.DB.prepare(
        "SELECT pid, n, st, code, t FROM presencia ORDER BY t DESC LIMIT 30"
      ).all();
      const jugadores = (results || []).map((r) => ({
        pid: r.pid, n: r.n, st: r.st, code: r.code || "",
        hace: Math.max(0, Math.round((ahora - (r.t || ahora)) / 1000)),
      }));""",
  """      const { results } = await env.DB.prepare(
        "SELECT pid, n, st, code, mj, vis, t FROM presencia ORDER BY t DESC LIMIT 30"
      ).all();
      const jugadores = (results || []).map((r) => ({
        pid: r.pid, n: r.n, st: r.st, code: r.code || "",
        mj: r.mj || "normal", vis: r.vis || "pri",   // r74 · FASE 169
        hace: Math.max(0, Math.round((ahora - (r.t || ahora)) / 1000)),
      }));""")

p('169.5d · invita POST guarda mj', WORKER,
  """      const r = await env.DB.prepare(
        "INSERT INTO invitas (de, deN, para, code, t) VALUES (?, ?, ?, ?, ?)"
      ).bind(de, texto(cuerpo.deN, 20) || "Jugador", para, code, ahora).run();""",
  """      const mjI = cuerpo.mj === "duelos" ? "duelos" : "normal";   // r74
      const r = await env.DB.prepare(
        "INSERT INTO invitas (de, deN, para, code, mj, t) VALUES (?, ?, ?, ?, ?, ?)"
      ).bind(de, texto(cuerpo.deN, 20) || "Jugador", para, code, mjI, ahora).run();""")

p('169.5e · invita GET devuelve mj', WORKER,
  """      const { results } = await env.DB.prepare(
        "SELECT id, de, deN, code, t FROM invitas WHERE para = ? ORDER BY t DESC LIMIT 8"
      ).bind(pid).all();
      const invitas = (results || []).map((r) => ({
        id: r.id, de: r.de, deN: r.deN, code: r.code || "",
        hace: Math.max(0, Math.round((ahora - (r.t || ahora)) / 1000)),
      }));""",
  """      const { results } = await env.DB.prepare(
        "SELECT id, de, deN, code, mj, t FROM invitas WHERE para = ? ORDER BY t DESC LIMIT 8"
      ).bind(pid).all();
      const invitas = (results || []).map((r) => ({
        id: r.id, de: r.de, deN: r.deN, code: r.code || "",
        mj: r.mj || "normal",                          // r74 · FASE 169
        hace: Math.max(0, Math.round((ahora - (r.t || ahora)) / 1000)),
      }));""")

# ── 169.6 · c12: landing en tres zonas + creación Pública/Privada ──
p('169.6a · landing → _multiZonas', C12,
  """    // LANDING: rejilla del apartado (CONFIG_SECCIONES.rejillas.multi)
    this._menuRejilla(rects, 'multi', {
      mjnorm: T('mj_norm_s'),
      mjduel: T('mj_duel_s'),
      'net:join': T('mj_off_hint'),
    });""",
  """    // LANDING r74 · TRES ZONAS (petición del dueño): «Zona Crear
    // partida · Zona Partidas disponibles · Zona Privada» — fuera la
    // rejilla de tres tarjetas sueltas que no se entendía.
    this._multiZonas(rects);""")

p('169.6b · métodos _multiZonas + _multiSalaElegir nuevo', C12,
  """  /** r70 · LIENZO VIRTUAL en la panela C: helper de los estados de sala —
   *  identidad + mapa nulo, coords VIRTUALES, sin placa legada. */
  _multiEnC() {""",
  """  /** r74 · FASE 169 · LANDING DEL MULTIJUGADOR EN TRES ZONAS:
   *  1 · CREAR PARTIDA — dos modalidades (cada una abre la elección
   *      PÚBLICA/PRIVADA); 2 · PARTIDAS DISPONIBLES — salas públicas vivas
   *      del pulso (modalidad + retador + ENTRAR); 3 · SALA PRIVADA — el
   *      código del creador. La tarjeta de invitación (r87) sigue viva. */
  _multiZonas(rects) {
    const c = this.menuCanvas.getContext('2d');
    const soc = this.social;
    const { x0, w0 } = this._multiEnC();
    const mm0 = this._menuMap;
    this._menuMap = null;
    c.save();
    c.setTransform(1, 0, 0, 1, 0, 0);
    let y = 236;
    const zona = (txt, yy) => {
      c.fillStyle = '#e8b45a';
      c.font = '800 27px system-ui, sans-serif';
      c.textAlign = 'left';
      c.textBaseline = 'alphabetic';
      c.fillText(txt, x0, yy);
    };
    const nota = (txt, yy, col) => {
      c.fillStyle = col || '#9aa7b4';
      c.font = '600 22px system-ui, sans-serif';
      c.textAlign = 'left';
      c.textBaseline = 'alphabetic';
      c.fillText(txt, x0, yy);
    };
    // — ZONA 1 · CREAR PARTIDA —
    zona(T('mj_crear_t'), y);
    y += 20;
    this._modeCard(rects, 'mjnorm', x0, y, w0 / 2 - 14, 124,
      T('mj_norm_t'), T('mj_norm_s'), '#2f9e44', '#1e7c33',
      PP_ICONS.match);
    this._modeCard(rects, 'mjduel', x0 + w0 / 2 + 14, y, w0 / 2 - 14, 124,
      T('mj_duel_t'), T('mj_duel_s'), '#ba58ff', '#7a1fd0',
      PP_ICONS.match);
    y += 160;
    // — ZONA 2 · PARTIDAS DISPONIBLES (públicas del pulso, en vivo) —
    zona(T('mj_disp_t'), y);
    y += 20;
    const pub = soc ? soc.publicas() : [];
    if (!pub.length) {
      nota(soc ? T('mj_sin_pub') : T('mj_sin_soc'), y + 34);
      y += 66;
    } else {
      pub.slice(0, 3).forEach((fila, i) => {
        const hF = 86;
        const hovered = this.menuHover.includes(rects.length);
        this._vestPlaca73(c, x0, y, w0, hF, 20);
        this._vestRR(c, x0, y, w0, hF, 20);
        c.strokeStyle = hovered ? '#ffffff' : 'rgba(232,180,90,0.32)';
        c.lineWidth = hovered ? 4 : 2;
        c.stroke();
        const esDuel = fila.mj === 'duelos';
        const ir = 30;
        this._vestMedallion(c, x0 + 24 + ir, y + hF / 2, ir, 'partido',
          esDuel ? '#ba58ff' : '#2f9e44');
        c.textAlign = 'left';
        c.textBaseline = 'alphabetic';
        c.fillStyle = '#ffffff';
        c.font = '800 28px system-ui, sans-serif';
        const nom = String(fila.n || T('rs_jugador')).slice(0, 22);
        c.fillText(nom, x0 + 70, y + 36);
        c.fillStyle = esDuel ? '#d6bcfa' : '#8ce99a';
        c.font = '700 19px system-ui, sans-serif';
        c.fillText(T(esDuel ? 'mj_duel_t' : 'mj_norm_t') +
          (fila.hace ? ' · ' + T('mj_hace', { n: fila.hace }) : ''),
          x0 + 70, y + 66);
        btn('mjsal:' + i, x0 + w0 - 214, y + 15, 190, 56,
          T('mj_entrar'), false, undefined, undefined, 25);
        y += hF + 14;
      });
      if (pub.length > 3) {
        nota(T('mj_mas_pub', { n: pub.length - 3 }), y + 10);
        y += 40;
      }
    }
    y += 10;
    // — ZONA 3 · SALA PRIVADA (el código del creador) —
    zona(T('mj_priv_t'), y);
    y += 20;
    btn('net:join', x0, y, w0, 92, T('join_title'), false,
      undefined, undefined, 27);
    y += 108;
    nota(T('mj_priv_hint'), y + 4);
    c.restore();
    this._menuMap = mm0;
    // r87 · invitación pendiente: tarjeta ámbar bajo las zonas (ids vivos)
    if (this.social && this.social.hayInvitas()) this._invitaCardVirtual(rects);
  }

  /** r70 · LIENZO VIRTUAL en la panela C: helper de los estados de sala —
   *  identidad + mapa nulo, coords VIRTUALES, sin placa legada. */
  _multiEnC() {""")

p('169.6c · _multiSalaElegir = CREAR SALA Pública/Privada', C12,
  """    const centro = CONFIG_MENUS.arco.panelas[1].x +
      CONFIG_MENUS.arco.panelas[1].w / 2;
    c.fillStyle = '#cfd8e0';
    c.font = '600 28px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(T('mj_off_hint'), centro, 330);
    btn('net:host', x0, 400, w0, 108, T('btn_host'), false, 'green',
      undefined, 30);
    btn('net:join', x0, 540, w0, 108, T('btn_join'), false,
      undefined, undefined, 30);
    btn('mjsel', x0, 700, w0, 76, T('mj_sel_back'), false,
      undefined, undefined, 26);
    c.restore();
    this._menuMap = mm0;
  }""",
  """    const centro = CONFIG_MENUS.arco.panelas[1].x +
      CONFIG_MENUS.arco.panelas[1].w / 2;
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    // r74 · FASE 169 · CREAR SALA (la modalidad ya se eligió en la Zona 1):
    // sólo falta la VISIBILIDAD — PÚBLICA se anuncia en «Partidas
    // disponibles» a los conectados; PRIVADA vive sólo para el código.
    c.fillStyle = '#cfd8e0';
    c.font = '600 28px system-ui, sans-serif';
    c.fillText((this._mjMode === 'duelos' ? T('mj_duel_t') : T('mj_norm_t')) +
      ' · ' + T('mj_crear_t'), centro, 316);
    c.fillStyle = '#9aa7b4';
    c.font = '600 23px system-ui, sans-serif';
    c.fillText(T('mj_vis_pregunta'), centro, 362);
    btn('mjvis:pub', x0, 420, w0, 118, T('mj_vis_pub'), false,
      undefined, undefined, 28);
    c.fillStyle = '#9aa7b4';
    c.font = '600 20px system-ui, sans-serif';
    c.fillText(T('mj_vis_pub_sub'), centro, 564);
    btn('mjvis:pri', x0, 600, w0, 118, T('mj_vis_pri'), false,
      undefined, undefined, 28);
    c.fillStyle = '#9aa7b4';
    c.font = '600 20px system-ui, sans-serif';
    c.fillText(T('mj_vis_pri_sub'), centro, 744);
    btn('mjsel', x0, 796, w0, 72, T('mj_sel_back'), false,
      undefined, undefined, 26);
    c.restore();
    this._menuMap = mm0;
  }""")

p('169.6d · despacho mjvis + mjsal', C12,
  """      case 'mjsel':""",
  """      case 'mjvis':
        // r74 · FASE 169 · CREAR SALA con la visibilidad elegida: PÚBLICA
        // se anuncia en el latido (mj/vis → «Partidas disponibles»);
        // PRIVADA vive sólo para quien tenga el código.
        if (arg === 'pub' || arg === 'pri') {
          this.net.modoSala = (this._mjMode === 'duelos') ? 'duelos' : 'normal';
          this.net.visSala = arg;
          this.menuPage = 'multi';
          this.net.hostRoom();
        }
        this.audio.playOsc(760, 1140, 0.08, 'triangle', 0.12, 0);
        this.drawMenu();
        break;
      case 'mjsal':
        // r74 · FASE 169 · ENTRAR en una partida PÚBLICA del listado: la
        // modalidad viaja en la presencia (mj); el mstart del anfitrión
        // sigue sellando el modo real (spec §3.8).
        {
          const filas = (this.social && this.social.publicas) ?
            this.social.publicas() : [];
          const fila = filas[parseInt(arg, 10) || 0];
          if (fila && fila.code && this.net &&
              (this.net.status === 'off' || this.net.status === 'error')) {
            this._mjMode = (fila.mj === 'duelos') ? 'duelos' : 'normal';
            this.menuPage = 'multi';
            this.net.joinRoom(fila.code);
          }
          this.audio.playOsc(760, 1180, 0.08, 'triangle', 0.12, 0);
          this.drawMenu();
        }
        break;
      case 'mjsel':""")

# ── 169.7 · i18n (es + en) ──
p('169.7a · i18n es', C00,
  """    mj_duel_s: '1 vs 1 online con poderes locos · gatillo para lanzarlos',""",
  """    mj_duel_s: '1 vs 1 online con poderes locos · gatillo para lanzarlos',
    // r74 · FASE 169 · EL MULTIJUGADOR EN TRES ZONAS
    mj_crear_t: 'CREAR PARTIDA',
    mj_disp_t: 'PARTIDAS DISPONIBLES',
    mj_priv_t: 'SALA PRIVADA',
    mj_priv_hint: 'entra con el código que te haya pasado el creador',
    mj_sin_pub: 'no hay partidas públicas ahora mismo · crea la tuya',
    mj_sin_soc: 'la capa social está sin conexión: sin listado en vivo',
    mj_entrar: 'ENTRAR',
    mj_hace: 'hace {n}s',
    mj_mas_pub: '+{n} más en la lista del pulso',
    mj_vis_pregunta: '¿Cómo abres la sala?',
    mj_vis_pub: 'PÚBLICA · para todos',
    mj_vis_pub_sub: 'se anuncia a los conectados y aparece en Partidas disponibles',
    mj_vis_pri: 'PRIVADA · sólo código',
    mj_vis_pri_sub: 'nadie la ve: entra quien tenga el código que les pases',
    rs_jugador: 'Jugador',""")

p('169.7b · i18n en', C00,
  """    mj_duel_s: '1 v 1 online with crazy powers · trigger to fire them',""",
  """    mj_duel_s: '1 v 1 online with crazy powers · trigger to fire them',
    // r74 · FASE 169 · MULTIJUGADOR IN THREE ZONES
    mj_crear_t: 'CREATE MATCH',
    mj_disp_t: 'OPEN MATCHES',
    mj_priv_t: 'PRIVATE ROOM',
    mj_priv_hint: 'join with the code the host gave you',
    mj_sin_pub: 'no public matches right now · create yours',
    mj_sin_soc: 'social layer is offline: no live listing',
    mj_entrar: 'JOIN',
    mj_hace: '{n}s ago',
    mj_mas_pub: '+{n} more in the pulse list',
    mj_vis_pregunta: 'How do you open the room?',
    mj_vis_pub: 'PUBLIC · for everyone',
    mj_vis_pub_sub: 'announced to connected players and listed under Open matches',
    mj_vis_pri: 'PRIVATE · code only',
    mj_vis_pri_sub: 'nobody sees it: only players with your code can join',
    rs_jugador: 'Player',""")


def main():
    textos = {C09: C09.read_text(encoding='utf-8'),
              C09C: C09C.read_text(encoding='utf-8'),
              C12: C12.read_text(encoding='utf-8'),
              C00: C00.read_text(encoding='utf-8'),
              WORKER: WORKER.read_text(encoding='utf-8')}
    total = 0
    for nombre, fichero, ancla, nuevo, veces in PARCHES:
        src = textos[fichero]
        n = src.count(ancla)
        if n != veces:
            sys.exit('✗ ' + nombre + ': ancla aparece ' + str(n) +
                     ' veces (se exige ' + str(veces) + ')')
        textos[fichero] = src.replace(ancla, nuevo, veces)
        total += 1
        print('✓ ' + nombre)
    for f, t in textos.items():
        f.write_text(t, encoding='utf-8')
    print('PARCHES APLICADOS: ' + str(total) + '/' + str(len(PARCHES)))


if __name__ == '__main__':
    main()
