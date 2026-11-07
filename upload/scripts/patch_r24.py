#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 24 · PARCHE POST-CAMPEÓN (coronación épica + RUTA LEYENDA NG+)
=======================================================================
Sólo positivo: el camino NORMAL queda byte-idéntico (todas las agujas
devuelven el MISMO valor cuando los flags están apagados). Lo nuevo:

  · CORONACIÓN: _championFlow registra la fecha y lanza el panel del
    núcleo con título propio + fila de estadísticas + confeti grande.
  · RUTA LEYENDA (NG+): siendo campeón, TODA rejugada del mapa es
    LEYENDA (duelo aiMul ×1.15/chance +0.06/cooldown −1.5 · asedio
    +1 forajido por oleada · tren +1 lingote por parada). Cada etapa
    superada sella leyenda_N; 5/5 → _leyendaFlow (medalla + champ_rank
    prueba 'leyenda' + registro <base>leyenda).
  · HUB: tier LEYENDA > SUPERADO (chip, hint de tarjeta y menuHint).

Ficheros: public/championships/oeste/index.js (FUENTE legítima — el build
no regenera championships/) + src/game/core/{c00,c11,c12}.js.
Idempotente: aguja ×0 + cambio ya presente = «ya aplicado».
"""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
OESTE = RAIZ / 'public/championships/oeste/index.js'
C00 = RAIZ / 'src/game/core/c00_pre_three.js'
C11 = RAIZ / 'src/game/core/c11_champloader.js'
C12 = RAIZ / 'src/game/core/c12_pingponggame.js'


def parcha(ruta, aguja, cambio, veces=1, etiqueta=''):
    txt = ruta.read_text(encoding='utf-8')
    n = txt.count(aguja)
    if n == 0:
        if cambio in txt:
            print(f'  · {etiqueta}: ya aplicado')
            return
        print(f'✗ FALLO {etiqueta}: aguja ×0 y cambio NO presente')
        sys.exit(1)
    if n != veces:
        print(f'✗ FALLO {etiqueta}: aguja ×{n} (esperaba ×{veces})')
        sys.exit(1)
    ruta.write_text(txt.replace(aguja, cambio, veces), encoding='utf-8')
    print(f'  ✓ {etiqueta} ({veces}×)')


# ══════════════════════════ OESTE ══════════════════════════
print('— oeste/index.js —')

parcha(OESTE, """    replay_hint: 'Apunta con la pala a una etapa superada y dispara para rejugarla',
""", """    replay_hint: 'Apunta con la pala a una etapa superada y dispara para rejugarla',
    // v3.6.18 (ronda 24 · POST-CAMPEÓN): RUTA LEYENDA — siendo campeón,
    // cada rejugada es una etapa LEYENDA (más dura) y sella el camino 5/5.
    leyenda_on: '¡RUTA LEYENDA! Rejuega las 5 etapas: cada una sella tu leyenda (5/5)',
    leyenda_ribbon: 'RUTA LEYENDA · ETAPA {n} · ¡GATILLO!',
    leyenda_up: '¡ETAPA {n} DE LEYENDA! El Oeste va en serio…',
    leyenda_sello: '¡SELLO DE LEYENDA {n}/5! El Oeste te va temiendo…',
    leyenda_cstat: 'Sellos de leyenda: {n}/5',
    leyenda_completa: '★ LEYENDA DEL OESTE ★ · camino sellado 5/5 en modo leyenda',
    leyenda_medalla_titulo: '¡LEYENDA DEL OESTE!',
    leyenda_medalla_msg: '5/5 sellos · tu nombre ya es canción de cantina',
    coronacion_titulo: '¡CAMPEÓN DEL SALVAJE OESTE!',
    coronacion_msg: 'El forajido entrega su estrella: el Oeste es TUYO, sheriff',
    coronacion_pts: 'Puntos',
    coronacion_duelos: 'Duelos ganados',
    coronacion_fecha: 'Coronado',
""", 1, 'O1 · diccionario ES')

parcha(OESTE, """    replay_hint: 'Aim the paddle at a cleared stage and pull the trigger to replay it',
""", """    replay_hint: 'Aim the paddle at a cleared stage and pull the trigger to replay it',
    // v3.6.18 (ronda 24 · POST-CHAMPION): LEGEND ROUTE
    leyenda_on: 'LEGEND ROUTE! Replay all 5 stages: each one seals your legend (5/5)',
    leyenda_ribbon: 'LEGEND ROUTE · STAGE {n} · TRIGGER!',
    leyenda_up: 'LEGEND STAGE {n}! The West means business…',
    leyenda_sello: 'LEGEND SEAL {n}/5! The West is starting to fear you…',
    leyenda_cstat: 'Legend seals: {n}/5',
    leyenda_completa: '★ WEST LEGEND ★ · route sealed 5/5 in legend mode',
    leyenda_medalla_titulo: 'WEST LEGEND!',
    leyenda_medalla_msg: '5/5 seals · your name is already a saloon song',
    coronacion_titulo: 'WILD WEST CHAMPION!',
    coronacion_msg: 'The outlaw hands over his star: the West is YOURS, sheriff',
    coronacion_pts: 'Points',
    coronacion_duelos: 'Duels won',
    coronacion_fecha: 'Crowned',
""", 1, 'O2 · diccionario EN')

parcha(OESTE, "    this._replayReal = null; this._hoverNodo = -1;   // v2.96: rejugada + nodo apuntado",
       "    this._replayReal = null; this._hoverNodo = -1;   // v2.96: rejugada + nodo apuntado\n"
       "    this._leyendaOn = false;   // v3.6.18 (ronda 24): rejugada LEYENDA activa (sólo campeón)",
       1, 'O3 · constructor _leyendaOn')

parcha(OESTE, """    if (this._stageMode || this._duelOn) return;
    if (n === st) return this.serveTrigger();     // nodo VIGENTE: camino normal
    if (this._armT > 0) return;                   // anti-gesto accidental
    this._replayReal = st;                        // el progreso real se conserva
    this.stage = n;
    this._refreshMap();
    this.paintCartel();
    g.rules.message = tx('replay_up').replace('{n}', String(n));
    g.audio.announce(g.rules.message, true);
""", """    if (this._stageMode || this._duelOn) return;
    // v3.6.18 (ronda 24): siendo CAMPEÓN, hasta el nodo VIGENTE es una
    // rejugada LEYENDA (el camino normal ya no existe: estás coronado).
    if (n === st && !this._champion) return this.serveTrigger();  // nodo VIGENTE: camino normal
    if (this._armT > 0) return;                   // anti-gesto accidental
    this._replayReal = st;                        // el progreso real se conserva
    this._leyendaOn = !!this._champion;           // v3.6.18 (ronda 24): sólo campeón rejuga en LEYENDA
    this.stage = n;
    this._refreshMap();
    this.paintCartel();
    g.rules.message = tx(this._leyendaOn ? 'leyenda_up' : 'replay_up').replace('{n}', String(n));
    g.audio.announce(g.rules.message, true);
""", 1, 'O4 · replayLaunch LEYENDA')

parcha(OESTE, "      c.fillText(tx('replay_ribbon').replace('{n}', String(hv + 1)), W / 2, 330);",
       "      c.fillText(tx(this._champion ? 'leyenda_ribbon' : 'replay_ribbon').replace('{n}', String(hv + 1)), W / 2, 330);   // v3.6.18 (ronda 24)",
       1, 'O5a · cinta LEYENDA al apuntar')

parcha(OESTE, "      c.fillText(tx('replay_hint'), W / 2, 662);",
       "      c.fillText(tx(this._champion ? 'leyenda_on' : 'replay_hint'), W / 2, 662);   // v3.6.18 (ronda 24)",
       1, 'O5b · pista LEYENDA en el cartel')

parcha(OESTE, "    c.fillText(this._champion ? tx('champ_sub') : tx('falta'), W / 2, 700);",
       "    // v3.6.18 (ronda 24): el pie del campeón cuenta sus SELLOS de leyenda\n"
       "    c.fillText(this._champion\n"
       "      ? (this._sellosLeyenda() >= 5 ? tx('leyenda_completa') : tx('leyenda_cstat', { n: this._sellosLeyenda() }))\n"
       "      : tx('falta'), W / 2, 700);",
       1, 'O5c · pie con sellos')

parcha(OESTE, "  _nvCfg() { return DUELO_NV[(this._duelNv || 1) - 1] || DUELO_NV[0]; }",
       """  _nvCfg() {
    const base = DUELO_NV[(this._duelNv || 1) - 1] || DUELO_NV[0];
    // v3.6.18 (ronda 24): en rejugada LEYENDA el forajido afila la puntería
    // (sólo campeón; el camino normal queda EXACTAMENTE igual).
    if (!this._leyendaOn) return base;
    return {
      aiMul: base.aiMul * 1.15,
      chance: Math.min(0.60, base.chance + 0.06),
      cooldown: Math.max(6.0, base.cooldown - 1.5),
      primer: Math.max(3.0, base.primer - 1.0),
      warn: base.warn,
    };
  }""", 1, 'O6 · _nvCfg con LEYENDA')

parcha(OESTE, "  _waveNeed() { return ASEDIO.perWave[this.wave - 1] || 5; }",
       "  _waveNeed() { return (this.ctrl && this.ctrl._leyendaOn ? 1 : 0) + (ASEDIO.perWave[this.wave - 1] || 5); }   // v3.6.18 (ronda 24): LEYENDA +1 forajido",
       1, 'O7 · _waveNeed con LEYENDA')

parcha(OESTE, "    const meta = TREN.meta[this.wave - 1] || 3;",
       "    const meta = (TREN.meta[this.wave - 1] || 3) + (this.ctrl && this.ctrl._leyendaOn ? 1 : 0);   // v3.6.18 (ronda 24): LEYENDA +1 lingote",
       3, 'O8a · TREN.meta ×3')

parcha(OESTE, "    return { n: this.ingots, m: TREN.meta[this.wave - 1] || 3 };",
       "    return { n: this.ingots, m: (TREN.meta[this.wave - 1] || 3) + (this.ctrl && this.ctrl._leyendaOn ? 1 : 0) };   // v3.6.18 (ronda 24)",
       1, 'O8b · TREN.meta HUD')

parcha(OESTE, """    if (!won && this._replayReal != null) {
      this.stage = this._replayReal;
      this._replayReal = null;
      this._refreshMap();
    }
""", """    if (!won && this._replayReal != null) {
      this.stage = this._replayReal;
      this._replayReal = null;
      this._leyendaOn = false;   // v3.6.18 (ronda 24): la LEYENDA se corta al caer
      this._refreshMap();
    }
""", 1, 'O9 · derrota corta LEYENDA')

parcha(OESTE, """  _stageClear(stage) {
    const g = this.game;
    if (stage >= 5) {
      this._championFlow();
      return;
    }
    // v2.96: REJUGADA superada — el progreso REAL se conserva (ni avanza
    // ni retrocede); el mapa y el cartel vuelven a la etapa vigente.
    if (this._replayReal != null) {
      this.stage = this._replayReal;
      this._replayReal = null;
      try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e9) { /* */ }
      this._refreshMap();
      g.rules.message = tx('replay_done');
      g.audio.announce(tx('replay_done'), true);
      this._setStateSilent('surprised', 2.2);
      this.sfx('diana', 0);
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.8, 200);
      return;
    }
""", """  _stageClear(stage) {
    const g = this.game;
    // v3.6.18 (ronda 24): las REJUGADAS se resuelven ANTES del gate del
    // campeón — repetir la coronación no existe (el camino ya está sellado)
    // y la LEYENDA del duelo final necesita su sello, no otra corona.
    if (this._replayReal != null) {
      const nReplay = stage;
      this.stage = this._replayReal;
      this._replayReal = null;
      try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e9) { /* */ }
      this._refreshMap();
      // v3.6.18 (ronda 24): SELLO DE LEYENDA — la etapa rejugada en modo
      // leyenda queda sellada; 5/5 dispara la medalla LEYENDA DEL OESTE.
      if (this._leyendaOn) {
        this._leyendaOn = false;
        try { localStorage.setItem(this.storageKey('leyenda_' + nReplay), '1'); } catch (eL) { /* */ }
        const sellos = this._sellosLeyenda();
        g.rules.message = sellos >= 5 ? tx('leyenda_medalla_msg') : tx('leyenda_sello').replace('{n}', String(nReplay));
        g.audio.announce(g.rules.message, true);
        this._setStateSilent('surprised', 2.2);
        this.sfx('diana', 0);
        if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.8, 200);
        if (sellos >= 5) this._leyendaFlow();
        return;
      }
      g.rules.message = tx('replay_done');
      g.audio.announce(tx('replay_done'), true);
      this._setStateSilent('surprised', 2.2);
      this.sfx('diana', 0);
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.8, 200);
      return;
    }
    if (stage >= 5) {
      this._championFlow();
      return;
    }
""", 1, 'O10 · _stageClear reordenado + sello')

parcha(OESTE, """    // v2.128: INSIGNIA «¡CONSEGUIDO!» en grande (panel del núcleo)
    try { const C = window.__PP_CORE; if (C && C.showChampConseguido) C.showChampConseguido('oeste'); } catch (e) { /* */ }
""", """    // v3.6.18 (ronda 24 · CORONACIÓN): fecha del título + panel épico del
    // núcleo con título propio, mensaje del forajido y fila de ESTADÍSTICAS.
    try { localStorage.setItem(this.storageKey('fecha'), new Date().toISOString()); } catch (eF) { /* */ }
    try {
      const C = window.__PP_CORE;
      if (C && C.showChampConseguido) {
        const fecha = new Date();
        const fTxt = (C.lang && C.lang() === 'en')
          ? fecha.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })
          : fecha.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });
        C.showChampConseguido('oeste', {
          campeon: true,
          title: tx('coronacion_titulo'),
          msg: tx('coronacion_msg'),
          dur: 14,
          stats: [
            [tx('coronacion_pts'), String(this.puntos | 0)],
            [tx('coronacion_duelos'), String(this.duelWins | 0)],
            [tx('coronacion_fecha'), fTxt],
          ],
        });
      }
    } catch (e) { /* */ }
""", 1, 'O11 · _championFlow CORONACIÓN')

parcha(OESTE, """  /** v2.94 · INSIGNIA del sheriff (assets/insignia.png): panel dorado con""",
       """  /** v3.6.18 (ronda 24): cuántos sellos de leyenda lleva el campeón. */
  _sellosLeyenda() {
    let n = 0;
    for (let i = 1; i <= 5; i++) {
      try { if (localStorage.getItem(this.storageKey('leyenda_' + i)) === '1') n++; } catch (e) { /* */ }
    }
    return n;
  }

  /** v3.6.18 (ronda 24 · ¡LEYENDA DEL OESTE!): las 5 etapas selladas en
   *  modo leyenda — medalla, registro, telemetría y una última risa. */
  _leyendaFlow() {
    const g = this.game;
    try { localStorage.setItem(this.storageKey('leyenda'), '1'); } catch (e) { /* */ }
    try {
      __PP_TELE.ev('champ_rank', {
        champ: 'oeste', prueba: 'leyenda', win: true,
        score: this.puntos | 0, stars: 3,
      });
    } catch (eT) { /* el reporte nunca rompe */ }
    try {
      const C = window.__PP_CORE;
      if (C && C.showChampConseguido) {
        C.showChampConseguido('oeste', {
          campeon: true,
          title: tx('leyenda_medalla_titulo'),
          msg: tx('leyenda_medalla_msg'),
          dur: 12,
        });
      }
    } catch (e) { /* */ }
    this._setStateSilent('defeated', 4);
    this.sfx('diana', 0);
    this._playLaugh(0.9);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 1.0, 260);
  }

  /** v2.94 · INSIGNIA del sheriff (assets/insignia.png): panel dorado con""", 1, 'O12 · métodos _sellosLeyenda + _leyendaFlow')

# ══════════════════════════ CORE ══════════════════════════
print('— c00_pre_three.js —')

parcha(C00, "    champ_stage_hint: 'Etapa {n}/{total} · sigue donde la dejaste',   // v3.6.17 (ronda 21, la de la ronda 19 al fin en producción)\n",
       "    champ_stage_hint: 'Etapa {n}/{total} · sigue donde la dejaste',   // v3.6.17 (ronda 21, la de la ronda 19 al fin en producción)\n"
       "    champ_leyenda_chip: '★ LEYENDA',   // v3.6.18 (ronda 24)\n"
       "    champ_leyenda_hint: '★ LEYENDA · camino sellado 5/5 en modo leyenda',\n", 1, 'C1 · strings ES')

parcha(C00, "    champ_stage_hint: 'Stage {n}/{total} · pick up where you left off',   // v3.6.17 (ronda 21)\n",
       "    champ_stage_hint: 'Stage {n}/{total} · pick up where you left off',   // v3.6.17 (ronda 21)\n"
       "    champ_leyenda_chip: '★ LEGEND',   // v3.6.18 (ronda 24)\n"
       "    champ_leyenda_hint: '★ LEGEND · route sealed 5/5 in legend mode',\n", 1, 'C2 · strings EN')

print('— c11_champloader.js —')

parcha(C11, "        if (this.championFlag(e.id)) return T('champ_done_hint');   // v2.128",
       "        if (this.leyendaFlag(e.id)) return T('champ_leyenda_hint');   // v3.6.18 (ronda 24): LEYENDA > SUPERADO\n"
       "        if (this.championFlag(e.id)) return T('champ_done_hint');   // v2.128",
       1, 'C3 · menuHint precedencia')

parcha(C11, "  /** v3.6.17 · ronda 21 · «Etapa X/5 · sigue donde la dejaste» — hint de",
       """  /** v3.6.18 · ronda 24 · ¿LEYENDA? — el campeón que selló las 5 etapas
   *  en modo leyenda (registro <base>leyenda = '1'; hoy sólo oeste,
   *  convención extensible a cualquier campeonato por su storage). */
  leyendaFlag(id) {
    try {
      const ent = (this.entries || []).find((x) => x.id === id);
      const base = String((ent && ent.storage) || '').replace(/\\*$/, '');
      if (base && localStorage.getItem(base + 'leyenda') === '1') return true;
    } catch (e) { /* */ }
    return false;
  }

  /** v3.6.17 · ronda 21 · «Etapa X/5 · sigue donde la dejaste» — hint de""", 1, 'C4 · leyendaFlag()')

print('— c12_pingponggame.js —')

parcha(C12, "      let done = false;   // v2.128: ¿campeonato superado?",
       "      let done = false;   // v2.128: ¿campeonato superado?\n"
       "      let leyenda = false;   // v3.6.18 (ronda 24): ¿sellado 5/5 en leyenda?",
       1, 'C5 · local leyenda')

parcha(C12, "        try { if (this.champs.championFlag(ch.id)) { done = true; hint = T('champ_done_hint'); } } catch (e) { /* */ }",
       "        try { if (this.champs.championFlag(ch.id)) { done = true; hint = T('champ_done_hint'); } } catch (e) { /* */ }\n"
       "        // v3.6.18 (ronda 24): LEYENDA pisa a SUPERADO en la tarjeta\n"
       "        try { if (this.champs.leyendaFlag && this.champs.leyendaFlag(ch.id)) { done = true; hint = T('champ_leyenda_hint'); leyenda = true; } } catch (eL2) { /* */ }",
       1, 'C6 · tarjeta LEYENDA')

parcha(C12, "        const chipTxt = T('champ_done_chip');",
       "        const chipTxt = leyenda ? T('champ_leyenda_chip') : T('champ_done_chip');   // v3.6.18 (ronda 24)",
       1, 'C7 · chip LEYENDA')

parcha(C12, """      this.champDone = {
        id, group, cv, c, tex, t: 0, dur: opts.dur || 9.5,
        title: ttl, img: null, mat: mesh.material,
      };""", """      this.champDone = {
        id, group, cv, c, tex, t: 0, dur: opts.dur || 9.5,
        title: ttl, img: null, mat: mesh.material,
        stats: Array.isArray(opts.stats) ? opts.stats.slice(0, 3) : null,   // v3.6.18 (ronda 24): coronación con estadísticas
        campeon: !!opts.campeon,   // v3.6.18 (ronda 24): coronación = más confeti
      };""", 1, 'C8 · champDone stats/campeon')

parcha(C12, "      try { this.confettiBurst = Math.max(this.confettiBurst || 0, 8); } catch (e2) { /* */ }",
       "      try { this.confettiBurst = Math.max(this.confettiBurst || 0, this.champDone && this.champDone.campeon ? 14 : 8); } catch (e2) { /* */ }   // v3.6.18 (ronda 24)",
       1, 'C9 · confeti de coronación')

parcha(C12, """      c.fillStyle = '#9fb2c4';
      c.font = '600 30px system-ui, sans-serif';
      c.fillText(T('champdone_replay'), W / 2, H * 0.912);
      S.tex.needsUpdate = true;""", """      // v3.6.18 (ronda 24): CORONACIÓN — fila de estadísticas en lugar del
      // recordatorio de rejuego (puntos · duelos ganados · fecha).
      if (S.stats && S.stats.length) {
        const nS = S.stats.length, colW = (W - 220) / Math.max(1, nS);
        for (let i = 0; i < nS; i++) {
          const lab = String((S.stats[i] && S.stats[i][0]) || '');
          const val = String((S.stats[i] && S.stats[i][1]) || '');
          const cx = 110 + colW * (i + 0.5);
          c.fillStyle = '#9fb2c4';
          c.font = '600 28px system-ui, sans-serif';
          c.fillText(lab.toUpperCase(), cx, H * 0.872);
          c.fillStyle = '#ffd257';
          c.font = '900 44px system-ui, sans-serif';
          c.fillText(val, cx, H * 0.922);
        }
      } else {
        c.fillStyle = '#9fb2c4';
        c.font = '600 30px system-ui, sans-serif';
        c.fillText(T('champdone_replay'), W / 2, H * 0.912);
      }
      S.tex.needsUpdate = true;""", 1, 'C10 · pintado de estadísticas')

print('✓ PARCHE R24 COMPLETO')
