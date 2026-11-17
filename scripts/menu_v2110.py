# -*- coding: utf-8 -*-
"""v2.110 · Cirugía del MENÚ en index.html:
A) páginas nuevas en el dispatcher (champs/opts)
B) sustituir el acordeón de la página principal por el HUB
C) métodos nuevos (_modeCard, drawMenuHub, drawMenuChamps, drawMenuOpts)
D) casos de menú nuevos ('page', 'themecyc')
E) iconos PP_ICONS a nivel de módulo
"""
import io, sys

P = '/home/z/my-project/game/index.html'
src = io.open(P, encoding='utf-8').read()
n0 = len(src)


def splice(text, anchor_start, anchor_end, replacement, tag):
    i = text.find(anchor_start)
    if i < 0:
        sys.exit('NO START ANCHOR: ' + tag)
    j = text.find(anchor_end, i)
    if j < 0:
        sys.exit('NO END ANCHOR: ' + tag)
    j += len(anchor_end)
    print(tag, '->', i, '..', j)
    return text[:i] + replacement + text[j:]


# ------------------------- E) PP_ICONS (módulo) -------------------------
anchorE = """window.__PP_WRL_BADGE = wrlBadgeImg;   // visible para tests y módulos (patrón __PP_WORLD)
"""
icons = anchorE + """
/* v2.110 · ICONOS del HUB del menú (dibujo vectorial sobre el canvas:
 * pala, diana, llama, palas cruzadas, trofeo y podio — sin imágenes). */
const PP_ICONS = {
  match(c, x, y) {          // pala + bola
    c.save(); c.translate(x, y); c.rotate(-0.5);
    c.fillStyle = '#ffdb99';
    c.beginPath(); c.ellipse(0, -6, 16, 21, 0, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#c98a4b';
    c.fillRect(-4, 12, 8, 17);
    c.restore();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(x + 22, y + 17, 8, 0, Math.PI * 2); c.fill();
  },
  train(c, x, y) {          // diana + bola
    c.strokeStyle = '#bfe3ff'; c.lineWidth = 5;
    c.beginPath(); c.arc(x, y + 2, 25, 0, Math.PI * 2); c.stroke();
    c.beginPath(); c.arc(x, y + 2, 13, 0, Math.PI * 2); c.stroke();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(x + 19, y - 19, 9, 0, Math.PI * 2); c.fill();
  },
  surv(c, x, y) {           // llama
    c.fillStyle = '#ffe0b3';
    c.beginPath();
    c.moveTo(x, y - 30);
    c.bezierCurveTo(x + 26, y - 6, x + 20, y + 26, x, y + 28);
    c.bezierCurveTo(x - 20, y + 26, x - 26, y - 6, x, y - 30);
    c.fill();
    c.fillStyle = '#ff9d3f';
    c.beginPath();
    c.moveTo(x, y - 8);
    c.bezierCurveTo(x + 13, y + 6, x + 10, y + 22, x, y + 24);
    c.bezierCurveTo(x - 10, y + 22, x - 13, y + 6, x, y - 8);
    c.fill();
  },
  multi(c, x, y) {          // dos palas cruzadas
    c.save();
    c.strokeStyle = '#e0d1ff'; c.lineWidth = 7; c.lineCap = 'round';
    c.beginPath(); c.moveTo(x - 21, y - 21); c.lineTo(x + 21, y + 21); c.stroke();
    c.beginPath(); c.moveTo(x + 21, y - 21); c.lineTo(x - 21, y + 21); c.stroke();
    c.restore();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(x, y, 7, 0, Math.PI * 2); c.fill();
  },
  champ(c, x, y) {          // trofeo
    c.fillStyle = '#ffe08a';
    c.beginPath();
    c.moveTo(x - 16, y - 22); c.lineTo(x + 16, y - 22);
    c.lineTo(x + 12, y + 2);
    c.quadraticCurveTo(x, y + 12, x - 12, y + 2);
    c.closePath(); c.fill();
    c.strokeStyle = '#ffe08a'; c.lineWidth = 4;
    c.beginPath(); c.arc(x - 21, y - 14, 8, Math.PI * 0.5, Math.PI * 1.5); c.stroke();
    c.beginPath(); c.arc(x + 21, y - 14, 8, Math.PI * 1.5, Math.PI * 0.5); c.stroke();
    c.fillRect(x - 4, y + 10, 8, 8);
    c.fillRect(x - 14, y + 18, 28, 6);
  },
  rank(c, x, y) {           // podio + estrella
    c.fillStyle = '#a5f0d8';
    c.fillRect(x - 26, y + 4, 15, 22);
    c.fillRect(x + 11, y + 12, 15, 14);
    c.fillRect(x - 7, y - 10, 14, 36);
    c.fillStyle = '#ffffff';
    c.beginPath();
    for (let i = 0; i < 5; i++) {
      const a = -Math.PI / 2 + i * Math.PI * 2 / 5;
      const a2 = a + Math.PI / 5;
      c.lineTo(x + Math.cos(a) * 11, y - 24 + Math.sin(a) * 11);
      c.lineTo(x + Math.cos(a2) * 4.5, y - 24 + Math.sin(a2) * 4.5);
    }
    c.closePath(); c.fill();
  },
};
"""
src = src.replace(anchorE, icons, 1)

# ------------------ A) dispatcher: páginas champs/opts ------------------
anchorA = """    // v2.67: página RANKING MUNDIAL (top 10 por campeonato)
    if (this.menuPage === 'rank') {
      this.drawMenuRank(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
"""
extraA = anchorA + """    // v2.110 · páginas del HUB: CAMPEONATOS y AJUSTES
    if (this.menuPage === 'champs') {
      this.drawMenuChamps(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
    if (this.menuPage === 'opts') {
      this.drawMenuOpts(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
"""
if anchorA not in src:
    sys.exit('NO ANCHOR A')
src = src.replace(anchorA, extraA, 1)

# ------------- B) página principal: acordeón -> HUB -------------
startB = """    this.drawMenuHeader(rects);

    // ---------- ACORDEÓN (v2.28) ----------"""
endB = """    c.fillText(T('menu_hint'), 512, Math.min(closeY + 92, 1520));
"""
replB = """    this.drawMenuHeader(rects);

    // ---------- v2.110 · HUB DE MODOS ----------
    // Tarjetas grandes con ACCESO DIRECTO a cada modo (adiós acordeón):
    // Partido · Entrenar · Supervivencia · Multijugador · Campeonatos ·
    // Ranking. Debajo, dificultad de la CPU y AJUSTES RÁPIDOS; TODAS las
    // opciones siguen vivas: las completas en la página AJUSTES y en las
    // páginas propias (Multijugador, Campeonatos, Ranking, Tu nombre).
    this.drawMenuHub(rects);
"""
src = splice(src, startB, endB, replB, 'B-hub')

# --------------------- C) métodos nuevos ---------------------
anchorC = """  toggleMenu() {
    if (this.calib) return;   // en entrenamiento manda el panel propio"""
methods = """  /* ================== v2.110 · MENÚ HUB ==================
   * El feedback fue claro: el acordeón quedó «lioso» y con demasiadas
   * opciones a la vista. Ahora el menú es un HUB de TARJETAS grandes,
   * cada una un ACCESO DIRECTO a un modo, con icono, color propio y una
   * sola línea de contexto. La dificultad de la CPU queda a la vista
   * (afecta a PARTIDO) y los mandos frecuentes en AJUSTES RÁPIDOS; el
   * resto de opciones NO desaparece: vive en la página AJUSTES y en las
   * páginas propias (Multijugador, Campeonatos, Ranking, Tu nombre). */

  /** Tarjeta de modo: degradado + insignia circular con icono + títulos. */
  _modeCard(rects, id, x, y, w, h, title, sub, g0, g1, icon, gold) {
    const c = this.menuCanvas.getContext('2d');
    const hovered = this.menuHover.includes(rects.length);
    c.beginPath();
    if (c.roundRect) c.roundRect(x, y, w, h, 22); else c.rect(x, y, w, h);
    const g = c.createLinearGradient(x, y, x, y + h);
    g.addColorStop(0, g0);
    g.addColorStop(1, g1);
    c.fillStyle = g;
    c.fill();
    c.strokeStyle = hovered ? '#ffffff'
      : (gold ? 'rgba(255,210,87,0.85)' : 'rgba(255,255,255,0.24)');
    c.lineWidth = hovered ? 5 : 2;
    c.stroke();
    // insignia circular con el icono del modo
    const cx = x + 76, cy = y + h / 2;
    c.beginPath(); c.arc(cx, cy, 50, 0, Math.PI * 2);
    c.fillStyle = 'rgba(0,0,0,0.30)'; c.fill();
    c.strokeStyle = 'rgba(255,255,255,0.4)'; c.lineWidth = 2.5; c.stroke();
    try { icon(c, cx, cy); } catch (e) { /* icono decorativo */ }
    // títulos
    c.textAlign = 'left';
    c.textBaseline = 'alphabetic';
    c.fillStyle = '#ffffff';
    c.font = '800 36px system-ui, sans-serif';
    c.fillText(title, x + 142, y + h / 2 - 4);
    c.fillStyle = 'rgba(255,255,255,0.85)';
    c.font = '600 20px system-ui, sans-serif';
    c.fillText(sub, x + 142, y + h / 2 + 30);
    // chevron ›
    c.fillStyle = 'rgba(255,255,255,0.85)';
    c.beginPath();
    c.moveTo(x + w - 46, y + h / 2 - 15);
    c.lineTo(x + w - 26, y + h / 2);
    c.lineTo(x + w - 46, y + h / 2 + 15);
    c.closePath(); c.fill();
    rects.push({ x, y: y - 3, w, h: h + 6, id });
  }

  /** Página principal: el HUB. 6 tarjetas (2×3) + dificultad + dock. */
  drawMenuHub(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    const over = this.rules.state === 'over';
    const diffName = { easy: T('diff_easy_btn'), medium: T('diff_medium_btn'),
      hard: T('diff_hard_btn') }[this.difficulty] || '';

    this.drawMenuHeader(rects);

    const CW = 456, CH = 176, GX = 32, GY = 18;
    const X0 = 40, X1 = X0 + CW + GX;
    let y = 240;
    // fila 1 · PARTIDO — ENTRENAR
    this._modeCard(rects, 'start', X0, y, CW, CH, T('hub_match'),
      over ? T('btn_rematch') : T('hub_vs', { v: diffName }),
      '#2f9e44', '#1e7c33', PP_ICONS.match);
    this._modeCard(rects, 'traingo', X1, y, CW, CH, T('sec_train'),
      T('hub_train_sub'), '#1c7ed6', '#145c9e', PP_ICONS.train);
    y += CH + GY;
    // fila 2 · SUPERVIVENCIA — MULTIJUGADOR
    this._modeCard(rects, 'survgo', X0, y, CW, CH, T('sec_surv'),
      this.survivalBest > 0 ? T('best_surv', { n: this.survivalBest })
        : T('hub_surv_sub'),
      '#e8590c', '#b0420a', PP_ICONS.surv);
    this._modeCard(rects, 'tab:multi', X1, y, CW, CH, T('hub_multi'),
      this.net.online ? T('hub_multi_on', { c: this.net.code })
        : T('hub_multi_sub'),
      '#7048e8', '#4c2bb0', PP_ICONS.multi);
    y += CH + GY;
    // fila 3 · CAMPEONATOS — RANKING MUNDIAL
    this._modeCard(rects, 'page:champs', X0, y, CW, CH, T('sec_crazy'),
      (this.champs && this.champs.menuHint()) || T('hub_champ_sub'),
      '#b8860b', '#7c5a08', PP_ICONS.champ, true);
    this._modeCard(rects, 'wrl:open', X1, y, CW, CH, T('sec_rank'),
      WORLDRANK.status === 'online' ? T('wrl_online') : T('hub_rank_sub'),
      '#0ca678', '#087354', PP_ICONS.rank);
    y += CH + GY;

    // dificultad de la CPU (afecta a PARTIDO) — siempre visible
    label(T('hub_diff'), y + 24, 22, '#9aa7b4', 'center');
    btn('diff:easy', 56, y + 46, 292, 60, T('diff_easy_btn'),
      this.difficulty === 'easy', undefined, undefined, 25);
    btn('diff:medium', 366, y + 46, 292, 60, T('diff_medium_btn'),
      this.difficulty === 'medium', undefined, undefined, 25);
    btn('diff:hard', 676, y + 46, 292, 60, T('diff_hard_btn'),
      this.difficulty === 'hard', undefined, undefined, 25);

    // ajustes rápidos: lo más usado a un golpe de rayo
    label(T('dock_label'), y + 138, 22, '#9aa7b4', 'center');
    const yn = (v) => (v ? T('yes') : T('no'));
    const W3 = 292, XS = [56, 366, 676], R1 = y + 160, R2 = R1 + 64, R3 = R2 + 64;
    btn('music', XS[0], R1, W3, 56, T('btn_music', { v: yn(this.audio.musicOn) }), !!this.audio.musicOn, undefined, !!this.audio.musicOn, 22);
    btn('amb', XS[1], R1, W3, 56, T('btn_amb', { v: yn(this.audio.ambience) }), !!this.audio.ambience, undefined, !!this.audio.ambience, 22);
    btn('voz', XS[2], R1, W3, 56, T('btn_mic', { v: yn(this.audio.voice) }), !!this.audio.voice, undefined, !!this.audio.voice, 22);
    btn('hapt', XS[0], R2, W3, 56, T('btn_hapt', { v: yn(this.hapticsOn) }), !!this.hapticsOn, undefined, !!this.hapticsOn, 22);
    btn('trail', XS[1], R2, W3, 56, T('btn_trail', { v: yn(this.showTrail) }), !!this.showTrail, undefined, !!this.showTrail, 22);
    const themeDef = ROOM_THEMES.find((t) => t.key === this.theme);
    const themeName = themeDef ? (themeDef.nameKey ? T(themeDef.nameKey) : themeDef.name) : '';
    btn('themecyc', XS[2], R2, W3, 56, T('room_label') + ': ' + themeName, false, undefined, undefined, 21);
    const _pn = ppPlayerName();
    btn('pname', XS[0], R3, 456, 56, T('opts_name', { v: _pn || T('no_name') }), !!_pn, undefined, undefined, 21);
    btn('page:opts', XS[0] + 474, R3, 456, 56, T('page_opts'), false, undefined, undefined, 24);

    // cierre + ayuda
    btn('close', 56, R3 + 96, 912, 68, T('close_menu') + ' · B', false, undefined, undefined, 26);
    c.fillStyle = '#5c6672';
    c.font = '500 20px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(T('menu_hint'), 512, R3 + 192);
  }

  /** v2.110 · página CAMPEONATOS: música global + TARJETA por campeonato
   *  (insignia + récord) con sus controles propios debajo (igual que en el
   *  acordeón: música, atajos de pruebas, récord… los declare el módulo). */
  drawMenuChamps(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    this.drawMenuHeader(rects);
    btn('page:main', 40, 216, 240, 60, T('page_back'), false, undefined, undefined, 25);
    c.fillStyle = '#ffd257';
    c.font = '900 42px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(T('page_champs'), 664, 246);

    let y = 304;
    // música global de los campeonatos (v2.78 — mismo canal del núcleo)
    const AM = this.audio;
    label(T('arc_music_global'), y + 10, 22);
    y += 32;
    btn('chmus:off', 56, y, 316, 58,
      AM.arcMute ? T('arc_music_muted') : '♪ ' + T('yes'), !AM.arcMute,
      undefined, undefined, 24);
    btn('chmus:down', 388, y, 150, 58, '−', false, undefined, undefined, 24);
    btn('chmus:up', 554, y, 150, 58, '+', false, undefined, undefined, 24);
    c.fillStyle = '#ffd257';
    c.font = '800 30px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(AM.arcMute ? T('arc_music_off_word')
      : Math.round(AM.arcVol * 100) + '%', 810, y + 29);
    c.fillStyle = '#5c6672';
    c.font = '600 22px system-ui, sans-serif';
    c.textAlign = 'left';
    c.fillText(T('arc_music_hint'), 886, y + 29);
    y += 76;

    const chList = this.champs ? this.champs.list() : [];
    if (!chList.length) {
      label(T('arc_no_data'), y + 12, 22, '#75828f', 'center');
      y += 44;
    }
    for (const ch of chList) {
      const hovered = this.menuHover.includes(rects.length);
      // récord propio del campeonato (victorias de SU storage)
      let hint = '';
      try {
        const ent = (this.champs.entries || []).find((e) => e.id === ch.id);
        const base = String((ent && ent.storage) || '').replace(/\\*$/, '');
        if (base) {
          const w = parseInt(localStorage.getItem(base + 'wins') || '0', 10) || 0;
          if (w > 0) hint = T('best_arcade', { n: w });
        }
      } catch (e) { /* sin registro */ }
      // tarjeta del campeonato
      c.beginPath();
      if (c.roundRect) c.roundRect(56, y, 912, 110, 18); else c.rect(56, y, 912, 110);
      const g = c.createLinearGradient(56, y, 56, y + 110);
      g.addColorStop(0, hovered ? '#4a3a12' : '#3a2e0e');
      g.addColorStop(1, hovered ? '#2e240c' : '#241d09');
      c.fillStyle = g;
      c.fill();
      c.strokeStyle = hovered ? '#ffffff' : 'rgba(255,210,87,0.65)';
      c.lineWidth = hovered ? 5 : 2;
      c.stroke();
      const img = wrlBadgeImg(ch.id);
      if (img && img.complete && img.naturalWidth) {
        const S = 86;
        const k = Math.min(S / img.naturalWidth, S / img.naturalHeight);
        const w = img.naturalWidth * k, h = img.naturalHeight * k;
        c.drawImage(img, 74 + (S - w) / 2, y + (110 - h) / 2, w, h);
      } else {
        c.font = '800 44px system-ui, sans-serif';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.fillText('🏆', 117, y + 55);
      }
      c.textAlign = 'left';
      c.textBaseline = 'alphabetic';
      c.fillStyle = '#ffe9b3';
      c.font = '800 32px system-ui, sans-serif';
      c.fillText(String(ch.label || '').replace(/^▶\\s*/, ''), 186, y + 48);
      c.fillStyle = '#9aa7b4';
      c.font = '600 21px system-ui, sans-serif';
      c.fillText(hint || T('hub_champ_hint'), 186, y + 82);
      c.fillStyle = 'rgba(255,210,87,0.9)';
      c.beginPath();
      c.moveTo(924, y + 40); c.lineTo(944, y + 55); c.lineTo(924, y + 70);
      c.closePath(); c.fill();
      rects.push({ x: 56, y: y - 3, w: 912, h: 116, id: 'ppchamp:' + ch.id });
      y += 122;
      // controles propios del módulo (música, atajos, récord…)
      const chMod = this.champs.moduleIfLoaded(ch.id);
      const chItems = (chMod && chMod.menuItems) ? chMod.menuItems() : [];
      for (const it of chItems) {
        if (it.row === 'label') {
          label(it.text, y + 14, 22);
          y += 34;
        } else if (it.row === 'btnrow') {
          (it.btns || []).forEach((b, bi) => {
            const XW = [[56, 316], [388, 150], [554, 150]][bi];
            if (XW) btn('champact:' + ch.id + '\\u203A' + b.act, XW[0], y, XW[1], 58, b.label, !!b.on, undefined, undefined, 24);
          });
          c.fillStyle = '#ffd257';
          c.font = '800 30px system-ui, sans-serif';
          c.textAlign = 'center';
          c.textBaseline = 'middle';
          c.fillText(it.pct || '', 810, y + 29);
          c.fillStyle = '#5c6672';
          c.font = '600 22px system-ui, sans-serif';
          c.textAlign = 'left';
          c.fillText(it.hint || '', 886, y + 29);
          y += 70;
        } else if (it.row === 'btn') {
          btn('champact:' + ch.id + '\\u203A' + it.act, 56, y, 912, it.h || 74, it.label, false, it.tone || 'surv', undefined, it.fs || 27);
          y += (it.h || 74) + 12;
        } else if (it.row === 'locked') {
          label(it.text, y + 12, 22, '#75828f', 'center');
          y += 40;
        } else if (it.row === 'locked2') {
          label(it.text, y + 10, 20, '#75828f', 'center');
          y += 36;
        } else if (it.row === 'center') {
          label(it.text || '', y + 20, 24, it.color || '#ffd98a', 'center');
          y += 48;
        }
      }
    }
    c.fillStyle = '#9aa7b4';
    c.font = '500 22px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    wrapText(c, T('arcade_hint'), 512, y + 22, 860, 30);
    y += 56;
    const closeY = Math.min(Math.max(y + 4, 1392), 1428);
    btn('close', 56, closeY, 912, 68, T('close_menu') + ' · B', false, undefined, undefined, 26);
  }

  /** v2.110 · página AJUSTES: TODAS las opciones juntas (nada se pierde:
   *  sala, ambiente, voz, música, vibración, estela, consejos, prueba de
   *  sonido, telemetría, nombre, reinicio y Ko-fi). */
  drawMenuOpts(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    this.drawMenuHeader(rects);
    btn('page:main', 40, 216, 240, 60, T('page_back'), false, undefined, undefined, 25);
    c.fillStyle = '#ffd257';
    c.font = '900 42px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(T('opts_title'), 664, 246);

    let y = 310;
    label(T('room_label'), y + 10, 22);
    y += 34;
    const themes = [
      ['theme:pabellon', T('theme_pabellon')], ['theme:neon', T('theme_neon')],
      ['theme:atardecer', T('theme_atardecer')], ['theme:artico', T('theme_artico')],
    ];
    themes.forEach(([id, name], i) => {
      btn(id, 56 + (i % 2) * 464, y + Math.floor(i / 2) * 64, 448, 56, name,
        this.theme === id.split(':')[1], undefined, undefined, 23);
    });
    y += 136;
    const yn = (v) => (v ? T('yes') : T('no'));
    btn('amb', 56, y, 448, 56, T('btn_amb', { v: yn(this.audio.ambience) }), !!this.audio.ambience, undefined, !!this.audio.ambience, 23);
    btn('voz', 520, y, 448, 56, T('btn_mic', { v: yn(this.audio.voice) }), !!this.audio.voice, undefined, !!this.audio.voice, 23);
    y += 64;
    btn('music', 56, y, 448, 56, T('btn_music', { v: yn(this.audio.musicOn) }), !!this.audio.musicOn, undefined, !!this.audio.musicOn, 23);
    btn('hapt', 520, y, 448, 56, T('btn_hapt', { v: yn(this.hapticsOn) }), !!this.hapticsOn, undefined, !!this.hapticsOn, 23);
    y += 64;
    btn('trail', 56, y, 448, 56, T('btn_trail', { v: yn(this.showTrail) }), !!this.showTrail, undefined, !!this.showTrail, 23);
    btn('tips', 520, y, 448, 56, T('btn_tips', { v: yn(this.showTips) }), !!this.showTips, undefined, !!this.showTips, 23);
    y += 64;
    // prueba de sonido con AUTO-REPARACIÓN (v2.29) + telemetría (v2.50)
    btn('sndtest', 56, y, 448, 56, T('btn_sndtest'), false, undefined, undefined, 23);
    btn('tele', 520, y, 448, 56, T('btn_tele', { v: yn(__PP_TELE.on) }), !!__PP_TELE.on, undefined, !!__PP_TELE.on, 23);
    y += 66;
    const _pn = ppPlayerName();
    btn('pname', 56, y, 448, 58, T('opts_name', { v: _pn || T('no_name') }), !!_pn, undefined, undefined, 22);
    btn('reset', 520, y, 448, 58, this._resetArm ? T('reset_arm') : T('reset_btn'), false, this._resetArm ? 'surv' : undefined, undefined, 21);
    y += 70;
    // apoyo Ko-fi (v2.50)
    btn('kofi', 56, y, 912, 56, T('btn_kofi'), false, 'green', undefined, 23);
    y += 68;
    label(T('tele_hint'), y + 10, 18, '#75828f');
    y += 30;
    const closeY = Math.min(Math.max(y + 4, 1392), 1428);
    btn('close', 56, closeY, 912, 68, T('close_menu') + ' · B', false, undefined, undefined, 26);
  }

""" + anchorC
src = src.replace(anchorC, methods, 1)

# --------------------- D) casos de menú nuevos ---------------------
anchorD = """      case 'ppchamp':"""
cases = """      case 'page':
        // v2.110 · HUB: navegación entre páginas del menú
        if (arg === 'main' || arg === 'champs' || arg === 'opts') {
          this.menuPage = arg;
          this._resetArm = false;
          if (arg === 'champs') {
            // el megáfono presenta los campeonatos al entrar (v2.28)
            this.rules.message = T('msg_arcade_menu');
            this.audio.playOsc(880, 1320, 0.09, 'triangle', 0.14, 0);
            window.setTimeout(() => {
              try { if (!this.disposed) this.audio.playOsc(1100, 1660, 0.12, 'triangle', 0.12, 0); } catch (e) { /* */ }
            }, 110);
          } else {
            this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
          }
          this.drawMenu();
        }
        break;
      case 'themecyc': {
        // v2.110 · ciclo rápido de SALA desde el HUB (las 4 en AJUSTES)
        const ti = ROOM_THEMES.findIndex((t) => t.key === this.theme);
        const nxt = ROOM_THEMES[(ti + 1 + ROOM_THEMES.length) % ROOM_THEMES.length];
        this.setTheme(nxt.key);
        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        this.drawMenu();
        break;
      }
""" + anchorD
src = src.replace(anchorD, cases, 1)

io.open(P, 'w', encoding='utf-8').write(src)
print('OK index.html:', n0, '->', len(src), '(+%d)' % (len(src) - n0))
