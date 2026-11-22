#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r70_patch_c12.py — FASE 164 · r70 · parche del motor del menú en c12.

Reemplazos por marcadores (seguros, idempotentes por aserción):
  1 · drawMenuMulti  → landing REJILLA (C) + estados de sala candy virtual
  2 · _invitaCard    → _invitaCardVirtual (coords virtuales de la C)
  3 · drawMenuChamps → landing REJILLA C+R + drawMenuChampUno (detalle)
  4 · drawMenuCarrera→ landing REJILLA divisiones + drawMenuCarreraDiv
  5 · drawMenuRankIni(nuevo) · backs legados fuera (rank/champhist)
  6 · drawMenu: ramas train/trainext/rankini/champuno/carreradiv
  7 · despachador: whitelist page · tab:multi · wrl tab/open · champsel ·
      champs:musica · carrera:sel abre división
"""
import sys
from pathlib import Path

P = Path('/home/z/my-project/upload/src/game/core/c12_pingponggame.js')
t = P.read_text(encoding='utf-8')

FAIL = []


def repl(marca, viejo, nuevo):
    global t
    if viejo not in t:
        FAIL.append(marca)
        return
    if t.count(viejo) != 1:
        FAIL.append(marca + ' (no único: %d)' % t.count(viejo))
        return
    t = t.replace(viejo, nuevo, 1)


def reemplaza_bloque(marca, inicio, fin, nuevo, incluir_fin=False):
    """Reemplaza [inicio, fin) — fin exclusivo salvo incluir_fin."""
    global t
    if inicio not in t:
        FAIL.append(marca + ' (inicio)')
        return
    i = t.index(inicio)
    j = t.index(fin, i + len(inicio))
    if incluir_fin:
        j += len(fin)
    t = t[:i] + nuevo + t[j:]


MULTI_NUEVO = '''  /** r70 · FASE 164 · página MULTIJUGADOR con el FORMATO AJUSTES (petición
   *  del dueño: «Deben estar bien montados con un formato similar al botón
   *  Ajustes»). LANDING = rejilla data-driven en la panela C (dos modos +
   *  unirse con código) + tarjeta de invitación viva. Los ESTADOS de sala
   *  (creando · código · conectado · error · elegir modo) pintan SU panel
   *  candy en la C — fuera la pantalla legada de 1024×1536. Ids del
   *  despachador INTACTOS (mjnorm · mjduel · net:* · mjsoc:* · mjsel). */
  drawMenuMulti(rects) {
    const net = this.net;
    const st = net.online ? 'online' : net.status;
    if (net.online || st !== 'off') {
      this._multiSala(rects, st);          // sala viva: estados en la C
      return;
    }
    if (this._mjMode) {
      this._multiSalaElegir(rects);        // modo elegido: crear/unirse
      return;
    }
    // LANDING: rejilla del apartado (CONFIG_SECCIONES.rejillas.multi)
    this._menuRejilla(rects, 'multi', {
      mjnorm: T('mj_norm_s'),
      mjduel: T('mj_duel_s'),
      'net:join': T('mj_off_hint'),
    });
    // r87 · invitación pendiente: tarjeta ámbar bajo la rejilla (ids vivos)
    if (this.social && this.social.hayInvitas()) this._invitaCardVirtual(rects);
  }

  /** r70 · LIENZO VIRTUAL en la panela C: helper de los estados de sala —
   *  identidad + mapa nulo, coords VIRTUALES, sin placa legada. */
  _multiEnC() {
    return {
      pC: CONFIG_MENUS.arco.panelas[1],
      x0: CONFIG_MENUS.arco.panelas[1].x + 120,
      w0: CONFIG_MENUS.arco.panelas[1].w - 240,
    };
  }

  /** r70 · panel de SALA en la C: conectado · esperando código · creando ·
   *  error. Misma mecánica que la pantalla legada (voz, cancelar, lista del
   *  pulso con INVITAR, avisos de build), vestida con la línea nueva. */
  _multiSala(rects, st) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const net = this.net;
    const { pC, x0, w0 } = this._multiEnC();
    const mm0 = this._menuMap;
    this._menuMap = null;                  // coords VIRTUALES
    c.save();
    c.setTransform(1, 0, 0, 1, 0, 0);
    // placa serena de la C
    this._vestRR(c, x0 - 24, 240, w0 + 48, 1060, 26);
    c.fillStyle = 'rgba(8,12,24,0.72)';
    c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.35)';
    c.lineWidth = 3;
    c.stroke();
    let y = 300;
    const centro = pC.x + pC.w / 2;
    const titulo = (txt, col, f) => {
      c.fillStyle = col;
      c.font = `800 ${f || 44}px system-ui, sans-serif`;
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(txt, centro, y);
    };
    const nota = (txt, col, f) => {
      c.fillStyle = col;
      c.font = `600 ${f || 24}px system-ui, sans-serif`;
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      wrapText(c, txt, centro, y, w0 - 40, 34);
    };
    if (st === 'online') {
      titulo(T('mj_connected'), '#7fb069');
      y += 64;
      const ping = (net.v2 === 'ok' && net.pingMs() >= 0)
        ? ' · ' + T('mj_ping', { n: net.pingMs() }) + (net.degraded() ? ' ·' : '')
        : '';
      nota(T('mj_rival', { code: net.code,
        st: this.rules.state === 'over' ? T('mj_over') : T('mj_playing') }) + ping,
        '#cfd8e0', 26);
      y += 76;
      const voz = net.voiceState === 'on'
        ? (net.micOn ? T('voz_on_mic') : T('voz_on_silent'))
        : net.voiceState === 'asking' ? T('voz_asking')
        : net.voiceState === 'denied' ? T('voz_denied')
        : T('voz_off');
      nota(voz, '#9aa7b4', 23);
      y += 72;
      btn('net:mic', x0, y, (w0 - 24) / 2, 78,
        T('btn_voz', { v: net.micOn ? T('yes') : T('no') }),
        net.micOn && net.voiceState === 'on', undefined, !!net.micOn, 27);
      btn('net:hangup', x0 + (w0 + 24) / 2, y, (w0 - 24) / 2, 78,
        T('btn_hangup'), false, undefined, undefined, 27);
      y += 108;
      // r126/r127 · aviso de build distinto (prioridad del autodiagnóstico)
      const bm126 = net.buildMismatch ? net.buildMismatch() : null;
      const sc126 = this._selfWarnInfo || null;
      if (sc126) nota(T('net_selfcheck_warn',
        { a: sc126.siteC, b: sc126.mineC }), '#ff6b57', 24);
      else if (bm126) nota(T('net_build_warn',
        { a: bm126.peerC, b: bm126.mineC }), '#ff6b57', 24);
      else nota(T('mj_rematch_hint'), '#9aa7b4', 22);
    } else if (st === 'waiting') {
      titulo(T('mj_room_code'), '#e8b45a', 34);
      y += 70;
      c.fillStyle = '#f2f4f6';
      c.font = '900 130px ui-monospace, monospace';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(net.code, centro, y + 66);
      y += 168;
      nota(T('mj_waiting'), '#9aa7b4', 24);
      y += 56;
      btn('net:cancel', x0, y, w0, 74, T('btn_cancel_room'), false,
        undefined, undefined, 27);
      y += 100;
      // r87 · LISTA DEL PULSO: jugadores online con INVITAR (el anfitrión
      // convoca sin que nadie teclee el código)
      const rsW = this.social;
      if (rsW && rsW.lista.length) {
        const filas = rsW.lista.slice(0, 4);
        c.fillStyle = '#7fb069';
        c.font = '700 26px system-ui, sans-serif';
        c.textAlign = 'left';
        c.textBaseline = 'middle';
        c.fillText(T('rs_online', { n: rsW.nOnline }) + ':', x0 + 12, y);
        y += 44;
        filas.forEach((j, i) => {
          const fy = y + i * 84;
          const stTxt = j.st === 'sala' ? '🟡 sala ' + (j.code || '')
            : (j.st === 'juego' ? '🔴 jugando' : '🟢 libre');
          const nm104 = String(j.n || 'Jugador');
          const nmT104 = nm104.length > 16 ? nm104.slice(0, 15) + '…' : nm104;
          c.fillStyle = '#e2e8f0';
          c.font = '600 26px system-ui, sans-serif';
          c.fillText('● ' + nmT104 + '  ·  ' + stTxt, x0 + 12, fy + 32);
          btn('mjsoc:inv:' + j.pid, x0 + w0 - 336, fy, 336, 64,
            T('rs_invitar'), false, 'green', undefined, 24);
        });
      }
    } else if (st === 'creating' || st === 'joining') {
      titulo(st === 'creating' ? T('mj_creating')
        : T('mj_connecting', { code: net.code }), '#e8b45a', 34);
      y += 84;
      btn('net:cancel', x0, y, w0, 74, T('btn_cancel'), false,
        undefined, undefined, 27);
    } else if (st === 'error') {
      titulo(T('mj_error'), '#ff6b57', 34);
      y += 76;
      nota(net.statusMsg || T('mj_error'), '#ff6b57', 26);
      y += 84;
      btn('net:host', x0, y, (w0 - 24) / 2, 74, T('btn_retry'), false,
        undefined, undefined, 26);
      btn('net:cancel', x0 + (w0 + 24) / 2, y, (w0 - 24) / 2, 74,
        T('btn_back'), false, undefined, undefined, 26);
    }
    c.restore();
    this._menuMap = mm0;
  }

  /** r70 · modo elegido sin sala abierta: panel CREAR / UNIRSE en la C
   *  (los dos pasos r80 intactos — «al pulsar el modo aparecen las opciones
   *  de sala y código»). */
  _multiSalaElegir(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const { x0, w0 } = this._multiEnC();
    const mm0 = this._menuMap;
    this._menuMap = null;
    c.save();
    c.setTransform(1, 0, 0, 1, 0, 0);
    this._vestRR(c, x0 - 24, 240, w0 + 48, 760, 26);
    c.fillStyle = 'rgba(8,12,24,0.72)';
    c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.35)';
    c.lineWidth = 3;
    c.stroke();
    const centro = CONFIG_MENUS.arco.panelas[1].x +
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
  }

'''

INVITA_NUEVA = '''  /** r87→r70 · TARJETA DE INVITACIÓN en VIRTUALES de la panela C —
   *  Fortnite/Steam: anfitrión + código + UNIRSE / DESCARTAR (ids vivos). */
  _invitaCardVirtual(rects) {
    const rs = this.social;
    if (!rs || !rs.hayInvitas()) return;
    const inv = rs.invitas[0];
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const { x0, w0 } = this._multiEnC();
    const h = 130, y = 1180;
    const mm0 = this._menuMap;
    this._menuMap = null;
    c.save();
    c.setTransform(1, 0, 0, 1, 0, 0);
    this._vestRR(c, x0 - 24, y, w0 + 48, h + 36, 24);
    c.fillStyle = 'rgba(44,28,4,0.88)';
    c.fill();
    c.lineWidth = 3;
    c.strokeStyle = '#ffb340';
    c.stroke();
    c.textAlign = 'left';
    c.textBaseline = 'middle';
    c.fillStyle = '#ffd45e';
    c.font = '800 30px system-ui, sans-serif';
    const deN104 = String(inv.deN || 'Jugador');
    c.fillText('🎮 ' + T('rs_invita_de', {
      n: deN104.length > 14 ? deN104.slice(0, 13) + '…' : deN104 }),
      x0, y + 38);
    c.fillStyle = '#e8dfc8';
    c.font = '600 26px system-ui, sans-serif';
    c.fillText(T('rs_invita_code', { c: inv.code }), x0, y + 86);
    btn('mjsoc:aceptar', x0 + w0 - 640, y + 26, 300, 76, T('rs_unirse'),
      false, 'green', undefined, 26);
    btn('mjsoc:desc', x0 + w0 - 320, y + 26, 300, 76, T('rs_descartar'),
      false, undefined, undefined, 26);
    c.restore();
    this._menuMap = mm0;
  }

'''

CHAMPS_NUEVO = '''  /* r70 · FASE 164 · página CAMPEONATOS con el FORMATO AJUSTES: landing =
   *  REJILLA C+R con tarjeta VIVA por campeonato (subtítulo con su estado:
   *  LEYENDA · SUPERADO · etapa · victorias · candado) + música global +
   *  historial. Cada tarjeta abre el DETALLE (champuno) con JUGAR,
   *  presentación y sus controles — ids del despachador intactos. */
  drawMenuChamps(rects) {
    const AM = this.audio;
    const chList = this.champs ? this.champs.list() : [];
    // tarjetas VIVAS (rejilla con datos del índice de campeonatos)
    const tarjetas = [{
      id: 'champs:musica', icono: 'audio', etiqueta: T('arc_music_global'),
      gradiente: ['#7e57c2', '#4527a0'],
    }];
    for (const ch of chList) {
      let hint = '';
      let done = false;
      let leyenda = false;
      try {
        const ent = (this.champs.entries || []).find((e) => e.id === ch.id);
        const base = String((ent && ent.storage) || '').replace(/\\*$/, '');
        if (base) hint = this.champs._stageHint(ch.id, base) || hint;
        if (base && !hint) {
          const w = parseInt(localStorage.getItem(base + 'wins') || '0', 10) || 0;
          if (w > 0) hint = T('best_arcade', { n: w });
        }
        try { if (this.champs.championFlag(ch.id)) {
          done = true; hint = T('champ_done_hint'); } } catch (eC1) { /* */ }
        try { if (this.champs.leyendaFlag && this.champs.leyendaFlag(ch.id)) {
          done = true; hint = T('champ_leyenda_hint'); leyenda = true;
        } } catch (eC2) { /* */ }
      } catch (eC3) { /* sin registro */ }
      const lockado = !!ch.locked;
      tarjetas.push({
        id: 'champsel:' + ch.id,
        icono: 'campeonatos',
        etiqueta: String(ch.label || '').replace(/^▶\\s*/, ''),
        gradiente: lockado ? ['#5f7183', '#3a4754']
          : leyenda ? ['#ffd25e', '#e8a80e'] : ['#ffca1e', '#d88c00'],
        sub: lockado ? T('champ_locked_hint')
          : (hint || T('hub_champ_hint')),
        leyenda,
      });
    }
    tarjetas.push({
      id: 'page:champhist', icono: 'campeonatos', etiqueta: T('hist_btn'),
      gradiente: ['#ffca1e', '#d88c00'],
    });
    // r73 · estado honesto si el índice no llega (nunca un hueco vacío)
    const subsM = { 'champs:musica': AM.arcMute ? T('arc_music_off_word')
      : Math.round(AM.arcVol * 100) + '%' };
    if (!chList.length) {
      if (this.champs && this.champs.cargando) {
        subsM['champs:musica'] = T('champ_cargando');
      } else {
        subsM['champs:musica'] = T('arc_no_data');
        tarjetas.splice(1, 0, {
          id: 'champretry', icono: 'consola',
          etiqueta: T('champ_reintentar'),
          gradiente: ['#96a8c2', '#586884'],
        });
      }
    }
    this._menuRejilla(rects, 'champs', subsM, tarjetas);
    // M7e (r124) · sellado barato al pintar (el historial queda al día)
    try { this.champs.historialTorneos(); } catch (eH7) { /* */ }
  }

  /** r70 · DETALLE DE CAMPEONATO (página champuno): el campeonato elegido
   *  (_champSel) con JUGAR como héroe verde, VER PRESENTACIÓN y SUS
   *  controles de módulo (música, atajos, récord) — la mecánica íntegra
   *  de las filas legadas, vestida con la línea nueva en la panela C. */
  drawMenuChampUno(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const pC = CONFIG_MENUS.arco.panelas[1];
    const x0 = pC.x + 120, w0 = pC.w - 240;
    const ch = (this.champs ? this.champs.list() : [])
      .find((x) => x.id === this._champSel);
    const mm0 = this._menuMap;
    this._menuMap = null;
    c.save();
    c.setTransform(1, 0, 0, 1, 0, 0);
    this._vestRR(c, x0 - 24, 240, w0 + 48, 1080, 26);
    c.fillStyle = 'rgba(8,12,24,0.72)';
    c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.35)';
    c.lineWidth = 3;
    c.stroke();
    const centro = pC.x + pC.w / 2;
    let y = 300;
    if (!ch) {
      c.fillStyle = '#9aa7b4';
      c.font = '600 28px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(T('arc_no_data'), centro, y);
      c.restore();
      this._menuMap = mm0;
      return;
    }
    const lockado = !!ch.locked;
    if (lockado) {
      // r72 · puerta cerrada: candado + chip PLATEADO PRÓXIMAMENTE
      this._vestMedallion(c, centro, y + 60, 64, 'campeonatos');
      y += 160;
      c.fillStyle = '#c9d4de';
      c.font = '800 34px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      const chipTxt = T('champ_locked_chip');
      const hint = T('champ_locked_hint');
      c.fillText(chipTxt + ' · ' + hint, centro, y);
      y += 90;
    } else {
      // héroe JUGAR (verde, protagonismo) + presentación
      const hovered = this.menuHover.includes(rects.length);
      this._vestCandy(c, x0, y, w0, 200,
        hovered ? ['#4af05e', '#189e2c'] : ['#2f9e44', '#1e7c33'], 30);
      const irH = 64;
      this._vestMedallion(c, x0 + 40 + irH, y + 100, irH, 'partido');
      c.fillStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.97)';
      c.font = '900 62px system-ui, sans-serif';
      c.textAlign = 'left';
      c.textBaseline = 'middle';
      c.fillText(T('hub_play'), x0 + 160, y + 100);
      rects.push({ x: x0 - 6, y: y - 4, w: w0 + 12, h: 208,
        id: 'ppchamp:' + ch.id });
      y += 226;
      btn('champintro:' + ch.id, x0, y, w0, 76, T('champ_intro_btn'),
        false, undefined, undefined, 27);
      y += 100;
    }
    // controles propios del módulo (música, atajos, récord… filas vivas)
    const chMod = this.champs.moduleIfLoaded(ch.id);
    const chItems = (chMod && chMod.menuItems) ? chMod.menuItems() : [];
    for (const it of chItems) {
      if (y > 1180) break;
      if (it.row === 'label') {
        c.fillStyle = '#c9d3dd';
        c.font = '700 26px system-ui, sans-serif';
        c.textAlign = 'left';
        c.textBaseline = 'middle';
        c.fillText(it.text, x0 + 8, y + 16);
        y += 44;
      } else if (it.row === 'btnrow') {
        const bs = (it.btns || []);
        const bw2 = bs.length ? (w0 - (bs.length - 1) * 20) / bs.length : w0;
        bs.forEach((b, bi) => {
          btn('champact:' + ch.id + '\\u203A' + b.act,
            x0 + bi * (bw2 + 20), y, bw2, 70, b.label, !!b.on,
            undefined, undefined, 24);
        });
        y += 88;
      } else if (it.row === 'btn') {
        btn('champact:' + ch.id + '\\u203A' + it.act, x0, y, w0, it.h || 74,
          it.label, false, it.tone || 'surv', undefined, it.fs || 27);
        y += (it.h || 74) + 14;
      } else if (it.row === 'center') {
        c.fillStyle = it.color || '#ffd98a';
        c.font = '700 26px system-ui, sans-serif';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.fillText(it.text || '', centro, y + 18);
        y += 52;
      } else if (it.row === 'locked' || it.row === 'locked2') {
        c.fillStyle = '#98a6b4';
        c.font = '600 24px system-ui, sans-serif';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.fillText(it.text, centro, y + 16);
        y += 48;
      }
    }
    c.restore();
    this._menuMap = mm0;
  }

'''

CARRERA_NUEVA = '''  /* ============ M5b (r115→r70) · ESCALERA DE CARRERA ==============
   *  LANDING = REJILLA de DIVISIONES en la panela C (petición del dueño:
   *  «formato similar al botón Ajustes»): una tarjeta viva por división
   *  (BRONCE → LEYENDA) con su estado (n/3 · superada · bloqueada). La
   *  tarjeta abre la DIVISIÓN (carreradiv) con los rivales en candy,
   *  DESAFIAR verde y la corona — mecánica r115 intacta. */
  drawMenuCarrera(rects) {
    const st = this._carreraEstado();
    const tarjetas = CARRERA_DIVISIONES.map((div, i) => {
      const esActual = i === st.div;
      const superada = i < st.div;
      let sub = '';
      if (esActual) {
        const n = div.rivales.filter((r) => st.done[r.id]).length;
        sub = n + '/3 · ' + T('carrera_actual');
      } else if (superada) sub = '✓ ' + T('carrera_superada');
      else sub = T('carrera_bloqueada');
      return {
        id: 'carrera:sel:' + i,
        icono: 'carrera',
        etiqueta: T(div.nameKey),
        gradiente: superada ? ['#7fb069', '#3f6e3a']
          : esActual ? ['#ffd25e', '#e8a80e']
          : ['#5f7183', '#3a4754'],
        sub,
        bloq: !superada && !esActual,
      };
    });
    const subsC = {};
    this._menuRejilla(rects, 'carrera', subsC, tarjetas);
    // corona de leyenda bajo la rejilla (si el dueño ya la alzó)
    if (st.crowned) {
      const c = this.menuCanvas.getContext('2d');
      const pC = CONFIG_MENUS.arco.panelas[1];
      c.save();
      c.setTransform(1, 0, 0, 1, 0, 0);
      c.fillStyle = '#ffd257';
      c.font = '900 34px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText('✦ ' + T('carrera_crown_msg') + ' ✦', pC.x + pC.w / 2, 1310);
      c.restore();
    }
  }

  /** r70 · DIVISIÓN ABIERTA (carreradiv): los rivales de la división vista
   *  en tarjetas candy (nombre + estilo + récord), DESAFIAR héroe verde
   *  para el próximo pendiente y revancha en TU división — ids
   *  'carrera:des:<i>:<rivalId>' intactos. */
  drawMenuCarreraDiv(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const pC = CONFIG_MENUS.arco.panelas[1];
    const x0 = pC.x + 120, w0 = pC.w - 240;
    const st = this._carreraEstado();
    const vi = Math.min(this._carreraSel || 0, st.div);
    const divV = CARRERA_DIVISIONES[vi];
    const esTuDiv = vi === st.div;
    const mm0 = this._menuMap;
    this._menuMap = null;
    c.save();
    c.setTransform(1, 0, 0, 1, 0, 0);
    this._vestRR(c, x0 - 24, 240, w0 + 48, 1080, 26);
    c.fillStyle = 'rgba(8,12,24,0.72)';
    c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.35)';
    c.lineWidth = 3;
    c.stroke();
    let y = 292;
    // división vista (color propio) + estado
    c.fillStyle = divV.col;
    c.font = '900 36px system-ui, sans-serif';
    c.textAlign = 'left';
    c.textBaseline = 'middle';
    c.fillText(T(divV.nameKey) + (esTuDiv ? ' · ' + T('carrera_actual') : ''),
      x0 + 8, y + 22);
    y += 64;
    for (const r of divV.rivales) {
      const vencido = !!st.done[r.id];
      const retable = esTuDiv;
      const hovered = this.menuHover.includes(rects.length);
      const rh = 118;
      this._vestCandy(c, x0, y, w0, rh, vencido
        ? ['#7fb069', '#3f6e3a'] : ['#4a5872', '#28324a'], 22);
      if (hovered && retable) {
        this._vestRR(c, x0, y, w0, rh, 22);
        c.strokeStyle = '#ffffff';
        c.lineWidth = 4;
        c.stroke();
      }
      const ir = 42;
      this._vestMedallion(c, x0 + 34 + ir, y + rh / 2, ir, 'partido');
      c.textAlign = 'left';
      c.fillStyle = '#ffffff';
      c.font = '800 32px system-ui, sans-serif';
      c.fillText((__ppLang === 'en' ? r.en : r.es), x0 + 112, y + rh * 0.36);
      const estDef = OPPONENT_STYLES.find((s) => s.id === r.estilo);
      c.fillStyle = 'rgba(255,255,255,0.72)';
      c.font = '600 22px system-ui, sans-serif';
      c.fillText(estDef ? (__ppLang === 'en' ? estDef.en : estDef.es)
        : r.estilo, x0 + 112, y + rh * 0.70);
      c.textAlign = 'right';
      if (vencido) {
        const rec = st.rec[r.id] || { w: 1, l: 0 };
        c.fillStyle = '#cfe8bd';
        c.font = '700 24px system-ui, sans-serif';
        c.fillText('✓ ' + T('carrera_vencido') + '  ' + rec.w + '-' + rec.l,
          x0 + w0 - 24, y + rh / 2);
      } else {
        c.fillStyle = '#ffd257';
        c.font = '700 24px system-ui, sans-serif';
        c.fillText('▶ ' + (estDef ? (__ppLang === 'en' ? estDef.en
          : estDef.es) : ''), x0 + w0 - 24, y + rh / 2);
      }
      if (retable) {
        rects.push({ x: x0 - 6, y: y - 4, w: w0 + 12, h: rh + 8,
          id: 'carrera:des:' + vi + ':' + r.id });
      }
      y += rh + 18;
    }
    // DESAFIAR / corona
    const prox = this._carreraProximo(st);
    if (prox && esTuDiv) {
      const nm = (__ppLang === 'en' ? prox.rival.en : prox.rival.es);
      btn('carrera:des:' + st.div + ':' + prox.rival.id, x0, y, w0, 104,
        T('carrera_challenge', { v: nm }), true, 'green', undefined, 32);
    } else if (st.crowned) {
      c.textAlign = 'center';
      c.fillStyle = '#ffd257';
      c.font = '900 30px system-ui, sans-serif';
      c.textBaseline = 'middle';
      c.fillText('✦ ' + T('carrera_crown_msg') + ' ✦', pC.x + pC.w / 2,
        y + 40);
    }
    c.textAlign = 'center';
    c.fillStyle = '#9aa7b4';
    c.font = '500 22px system-ui, sans-serif';
    c.fillText(T('carrera_hint'), pC.x + pC.w / 2, 1276);
    c.restore();
    this._menuMap = mm0;
  }

'''

RANKINI_NUEVO = '''  /** r70 · landing RANKING MUNDIAL (formato Ajustes): tabla global + mi
   *  posición en la panela C. La tabla profunda vive en la página 'rank'. */
  drawMenuRankIni(rects) {
    const subTab = WORLDRANK.status === 'online' ? T('wrl_online')
      : (WORLDRANK.status === 'offline' ? T('wrl_offline') : T('wrl_loading'));
    const D = (this.stats && this.stats.data) || { elo: 1000 };
    this._menuRejilla(rects, 'rank', {
      'wrl:tab': subTab,
      'page:rankme': T('rankme_sub', { v: D.elo || 1000 }),
    });
    // r70 · WORLDRANK fresco al aterrizar (silencioso, como r67)
    WORLDRANK.load(true).then(() => {
      if (this.menuOpen && this.menuPage === 'rankini') this.drawMenu();
    }).catch(() => { /* nunca rompe */ });
  }

'''

# ---------- 1 · drawMenuMulti + helpers ----------
reemplaza_bloque('multi', '\n  /** Página MULTIJUGADOR: crear/unirse por código, estado y voz (v2.19;',
  '\n  // r84 · La tarjeta DUELOS LOCOS ya no necesita pintor propio',
  '\n' + MULTI_NUEVO)

# ---------- 2 · invitación virtual ----------
reemplaza_bloque('invita', '\n  /** r87 · TARJETA DE INVITACIÓN en el submenú Multijugador — Fortnite/',
  '\n    return h + 14;\n  }\n', '\n' + INVITA_NUEVA, incluir_fin=True)

# ---------- 3 · carrera landing + carreradiv (antes de champs: el
# marcador final de carrera es el comentario antiguo de champs) ----------
reemplaza_bloque('carrera', '\n  /* ================== M5b (r115) · ESCALERA DE CARRERA ==================',
  '\n' + '  /** v2.110 · página CAMPEONATOS', '\n' + CARRERA_NUEVA)

# ---------- 4 · champs landing + champuno ----------
reemplaza_bloque('champs', '\n  /** v2.110 · página CAMPEONATOS: música global + TARJETA por campeonato',
  '\n  /** M7e (r124) · página HISTORIAL DE TORNEOS', '\n' + CHAMPS_NUEVO)

# ---------- 5 · rankini nuevo + back legado fuera ----------
repl('rankini', '\n  drawMenuRank(rects) {',
  '\n' + RANKINI_NUEVO + '\n  drawMenuRank(rects) {')

repl('rank-back',
  "    if (!ppPlayerName()) label(T('wrl_need_name'), 966, 19, '#98a6b4', 'center');\n"
  "    btn('tab:main', 56, 1380, 912, 76, '◀  ' + T('btn_back'), false, undefined, undefined, 28);\n  }",
  "    if (!ppPlayerName()) label(T('wrl_need_name'), 966, 19, '#98a6b4', 'center');\n  }")

repl('champhist-back',
  "    this.drawMenuHeader(rects);\n    btn('page:champs', 40, 216, 240, 60, T('page_back'), false, undefined, undefined, 25);\n",
  "    this.drawMenuHeader(rects);\n")

repl('champhist-close',
  "    const closeY = Math.min(Math.max(y + 4, 1392), 1428);\n"
  "    btn('close', 56, closeY, 912, 68, T('close_menu') + ' · B', false, undefined, undefined, 26);\n  }\n\n  /** v2.110 · página AJUSTES",
  "  }\n\n  /** v2.110 · página AJUSTES")

# ---------- 6 · ramas de drawMenu ----------
RAMAS_VIEJAS = """    // v3.0 · PRO TRAINING: páginas del hub de entrenamiento
    if (this.menuPage === 'train' && window.__PP_TRAIN) {
      window.__PP_TRAIN.drawHub(this, c, rects, this._menuBtn, this._menuLabel);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this._menuTipDraw(c, rects);   // r96 · tooltip del control apuntado
      this._menuTexSube();
      return;
    }
    if (this.menuPage === 'trainarea' && window.__PP_TRAIN) {
      window.__PP_TRAIN.drawArea(this, c, rects, this._menuBtn, this._menuLabel);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this._menuTipDraw(c, rects);   // r96 · tooltip del control apuntado
      this._menuTexSube();
      return;
    }
"""
RAMAS_NUEVAS = """    // r70 · ENTRENAR: landing REJILLA (formato Ajustes) — el hub legado
    // se retira; el área y el perfil/extras son páginas profundas
    if (this.menuPage === 'train') {
      this.drawMenuTrain(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this._menuTipDraw(c, rects);   // r96 · tooltip del control apuntado
      this._menuTexSube();
      return;
    }
    if (this.menuPage === 'trainext' && window.__PP_TRAIN &&
        window.__PP_TRAIN.drawExtras) {
      window.__PP_TRAIN.drawExtras(this, c, rects, this._menuBtn,
        this._menuLabel);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this._menuTipDraw(c, rects);   // r96 · tooltip del control apuntado
      this._menuTexSube();
      return;
    }
    if (this.menuPage === 'trainarea' && window.__PP_TRAIN) {
      window.__PP_TRAIN.drawArea(this, c, rects, this._menuBtn, this._menuLabel);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this._menuTipDraw(c, rects);   // r96 · tooltip del control apuntado
      this._menuTexSube();
      return;
    }
"""
repl('ramas-train', RAMAS_VIEJAS, RAMAS_NUEVAS)

# rankini branch antes de rankme
ANCHOR_RANKME = "    // M4 (r118) · página MI RANKING (ELO personal local, sin servidor)\n    if (this.menuPage === 'rankme') {"
repl('rama-rankini', ANCHOR_RANKME,
  "    // r70 · landing RANKING MUNDIAL (formato Ajustes)\n"
  "    if (this.menuPage === 'rankini') {\n"
  "      this.drawMenuRankIni(rects);\n"
  "      this.menuRects = rects;\n      this._menuState = this.rules.state;\n"
  "      this._menuTipDraw(c, rects);\n      this._menuTexSube();\n      return;\n    }\n"
  + ANCHOR_RANKME)

# champuno branch tras champhist
ANCHOR_CHAMPHIST = """    // M7e (r124) · página HISTORIAL DE TORNEOS
    if (this.menuPage === 'champhist') {
      this.drawMenuChampHist(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this._menuTipDraw(c, rects);   // r96 · tooltip del control apuntado
      this._menuTexSube();
      return;
    }
"""
repl('rama-champuno', ANCHOR_CHAMPHIST, ANCHOR_CHAMPHIST +
  "    // r70 · DETALLE DE CAMPEONATO (formato Ajustes)\n"
  "    if (this.menuPage === 'champuno') {\n"
  "      this.drawMenuChampUno(rects);\n"
  "      this.menuRects = rects;\n      this._menuState = this.rules.state;\n"
  "      this._menuTipDraw(c, rects);\n      this._menuTexSube();\n      return;\n    }\n")

# carreradiv branch tras carrera
ANCHOR_CARRERA = """    // M5b (r115) · página de la ESCALERA DE CARRERA
    if (this.menuPage === 'carrera') {
      this.drawMenuCarrera(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this._menuTipDraw(c, rects);   // r96 · tooltip del control apuntado
      this._menuTexSube();
      return;
    }
"""
repl('rama-carreradiv', ANCHOR_CARRERA, ANCHOR_CARRERA +
  "    // r70 · DIVISIÓN ABIERTA (rivales candy + DESAFIAR)\n"
  "    if (this.menuPage === 'carreradiv') {\n"
  "      this.drawMenuCarreraDiv(rects);\n"
  "      this.menuRects = rects;\n      this._menuState = this.rules.state;\n"
  "      this._menuTipDraw(c, rects);\n      this._menuTexSube();\n      return;\n    }\n")

# ---------- 7 · despachador ----------
repl('whitelist-page',
  "        if (arg === 'main' || arg === 'champs' || arg === 'champhist' || arg === 'opts' ||\n"
  "            arg === 'optsJuego' || arg === 'optsSala' || arg === 'optsSonido' ||\n"
  "            arg === 'optsVisual' || arg === 'optsPerfil' || arg === 'optsRendi' ||\n"
  "            arg === 'optsPala' ||",
  "        if (arg === 'main' || arg === 'champs' || arg === 'champhist' || arg === 'opts' ||\n"
  "            arg === 'rankini' || arg === 'rankme' || arg === 'multi' ||\n"
  "            arg === 'trainext' || arg === 'carreradiv' ||\n"
  "            arg === 'optsJuego' || arg === 'optsSala' || arg === 'optsSonido' ||\n"
  "            arg === 'optsVisual' || arg === 'optsPerfil' || arg === 'optsRendi' ||\n"
  "            arg === 'optsPala' ||")

repl('tab-multi-landing',
  "        if (arg === 'multi') {\n"
  "          this._mjMode = (this.net.online || this.net.status !== 'off') ? 'normal' : null;\n"
  "        }",
  "        if (arg === 'multi') {\n"
  "          // r70 · la landing REJILLA primero: el modo se elige en su\n"
  "          // tarjeta (mjnorm/mjduel abren el panel de sala en la C)\n"
  "          this._mjMode = null;\n"
  "        }")

repl('wrl-open-rankini',
  "        if (arg === 'open') {\n          this.menuPage = 'rank';",
  "        if (arg === 'open') {\n          this.menuPage = 'rankini';")

repl('wrl-tab',
  "        } else if (arg === 'left' || arg === 'right') {",
  "        } else if (arg === 'tab') {\n"
  "          // r70 · landing → TABLA mundial (página profunda)\n"
  "          this.menuPage = 'rank';\n"
  "          this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);\n"
  "          this.drawMenu();\n"
  "        } else if (arg === 'left' || arg === 'right') {")

ANCHOR_CHAMPRETRY = """      case 'champretry':
        // r73 · REINTENTAR la carga del índice de campeonatos (índice o
        // manifest perdidos por la red ya no son un callejón sin salida).
        if (this.champs) this.champs.recargar();
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.drawMenu();
        break;
"""
repl('champsel+musica', ANCHOR_CHAMPRETRY, ANCHOR_CHAMPRETRY +
  """      case 'champsel':
        // r70 · landing CAMPEONATOS → DETALLE del campeonato elegido
        if (arg) {
          this._champSel = arg;
          this.menuPage = 'champuno';
          this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
          this.drawMenu();
        }
        break;
      case 'champs':
        // r70 · música global de campeonatos como TARJETA de la landing
        if (arg === 'musica') {
          const AM70 = this.audio;
          AM70.setArcMute(!AM70.arcMute);
          this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
          this.rules.message = T('arc_music_msg', {
            v: AM70.arcMute ? T('arc_music_off_word')
              : Math.round(AM70.arcVol * 100) + '%',
          });
          this.drawMenu();
        }
        break;
""")

repl('carrera-sel-div',
  "            if (i <= st.div) this._carreraSel = i;\n"
  "            this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);",
  "            if (i <= st.div) this._carreraSel = i;\n"
  "            // r70 · la tarjeta de división ABRE la división (rivales)\n"
  "            this.menuPage = 'carreradiv';\n"
  "            this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);")

# ---------- 8 · rejilla: sub directo de la tarjeta viva ----------
repl('rejilla-sub',
  "        const sub = subs && subs[t.id.replace('page:', '')];",
  "        // r70 · la tarjeta viva trae su sub (campeonatos, divisiones)\n"
  "        const sub = (t.sub !== undefined && t.sub !== null)\n"
  "          ? t.sub : (subs && subs[t.id.replace('page:', '')]);")

P.write_text(t, encoding='utf-8')
if FAIL:
  print('FALLOS:')
  for f in FAIL:
    print('  ·', f)
  sys.exit(1)
print('c12 parcheado OK')
