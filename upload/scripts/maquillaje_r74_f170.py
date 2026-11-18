#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""maquillaje_r74_f170.py — FASE 170 «LA ALERTA DE DUELO» (r74).

Petición del dueño: cuando alguien acepta la invitación del creador de una
sala pública, éste recibe SOBREIMPRESA en pantalla (esté donde esté:
entrenando, en un campeonato, en el tutorial…) una ALERTA de 5 segundos:
  · icono PARPADEANTE de DOS PERSONAS en una esquina superior,
  · alerta sonora de pitidos,
  · VOZ que dice «Un jugador ha aceptado tu invitación de duelo».
Al apuntar y gatillar sobre el icono se abre la pantalla de confirmación:
si acepta, se cierra lo que esté haciendo (perderá cualquier registro
generado) y salta a la partida del duelo directamente.

Implementación:
  · startOnlineSession() gana un GATE: si soy ANFITRIÓN, la sesión queda
    PENDIENTE (nada se cierra de golpe) y salta la alerta. El invitado
    entra igual que siempre (él la aceptó).
  · El icono es un quad pegado al RIG (esquina superior, renderOrder 90),
    parpadeo 3 Hz 5 s y fundido; gatillo sobre el icono → página
    'dueloask' (prompt caramelo SÍ/NO). SÍ = _dueloArrancar() (el cuerpo
    real de siempre); NO = colgar (el rival queda libre).
  · La VOZ entra al BANCO de c03 (VOICE_B64/VOICE_B64_EN de c00 + mapa
    VOICE_FULL): fragmentos OGG Opus generados para esta fase — en XR la
    Quest NO reproduce speechSynthesis, el banco sí.
"""
import base64
import pathlib
import sys

RAIZ = pathlib.Path('/home/z/my-project/upload/src/game/core')
C00 = RAIZ / 'c00_pre_three.js'
C02 = RAIZ / 'c02_cfg_escena.js'
C03 = RAIZ / 'c03_audio_voz.js'
C12 = RAIZ / 'c12_pingponggame.js'
VOZ_ES = pathlib.Path('/tmp/voz74/duelo_es.b64').read_text().strip()
VOZ_EN = pathlib.Path('/tmp/voz74/duelo_en.b64').read_text().strip()

PARCHES = []


def p(nombre, fichero, ancla, nuevo, veces=1):
    PARCHES.append((nombre, fichero, ancla, nuevo, veces))


# ── 170.1 · el fragmento de VOZ (es + en) al banco de c00 ──
p('170.1a · VOICE_B64 es', C00,
  'export const VOICE_B64 = {',
  'export const VOICE_B64 = {\n'
  '  /* r74 · FASE 170 · voz de LA ALERTA DE DUELO (tts de la casa, '
  'OGG Opus 24k mono) */\n'
  '  duelo_acepta: "' + VOZ_ES + '",\n')

p('170.1b · VOICE_B64 en', C00,
  'export const VOICE_B64_EN = {',
  'export const VOICE_B64_EN = {\n'
  '  /* r74 · FASE 170 · duel alert voice */\n'
  '  duelo_acepta: "' + VOZ_EN + '",\n')

p('170.1c · VOICE_FULL es', C03,
  """    'rival desconectado': ['rival_desconectado'],""",
  """    'rival desconectado': ['rival_desconectado'],
    'un jugador ha aceptado tu invitacion de duelo': ['duelo_acepta'],
    'un jugador ha aceptado tu invitacion de duelo ya': ['duelo_acepta'],""")

p('170.1d · VOICE_FULL en', C03,
  """    'opponent disconnected': ['rival_desconectado'],""",
  """    'opponent disconnected': ['rival_desconectado'],
    'a player has accepted your duel invitation': ['duelo_acepta'],""")

# ── 170.2 · i18n (es + en) ──
p('170.2a · i18n es', C00,
  """    rs_jugador: 'Jugador',""",
  """    rs_jugador: 'Jugador',
    // r74 · FASE 170 · LA ALERTA DE DUELO
    duelo_alerta_voz: 'Un jugador ha aceptado tu invitación de duelo',
    duelo_alerta_msg: 'DUELO EN ESPERA: un jugador aceptó tu invitación — icono arriba o Multijugador',
    dueloask_t: 'ACEPTAR EL DUELO',
    dueloask_sub: 'Un jugador ha aceptado tu invitación de duelo.',
    dueloask_hint: 'si aceptas, se cierra lo que estás haciendo y saltas a la partida — perderás cualquier registro generado',
    dueloask_si: 'SÍ, ACEPTAR Y JUGAR',
    dueloask_no: 'NO, SEGUIR AQUÍ (colgar)',""")

p('170.2b · i18n en', C00,
  """    rs_jugador: 'Player',""",
  """    rs_jugador: 'Player',
    // r74 · FASE 170 · THE DUEL ALERT
    duelo_alerta_voz: 'A player has accepted your duel invitation',
    duelo_alerta_msg: 'DUEL WAITING: a player accepted your invitation — icon above or Multiplayer',
    dueloask_t: 'ACCEPT THE DUEL',
    dueloask_sub: 'A player has accepted your duel invitation.',
    dueloask_hint: 'if you accept, what you are doing closes and you jump into the match — any progress will be lost',
    dueloask_si: 'YES, ACCEPT AND PLAY',
    dueloask_no: 'NO, STAY HERE (hang up)',""")

# ── 170.3 · concha: página dueloask ──
p('170.3 · shell dueloask', C02,
  """    salirask: { tituloKey: 'salirask_title', icono: 'salir', volver: 'page:main' },""",
  """    salirask: { tituloKey: 'salirask_title', icono: 'salir', volver: 'page:main' },
    // r74 · FASE 170 · la confirmación del DUELO PENDIENTE
    dueloask: { tituloKey: 'dueloask_t', icono: 'multijugador',
      volver: 'page:main' },""")

# ── 170.4 · el GATE de startOnlineSession (aplaza el arranque del anfitrión) ──
p('170.4 · gate startOnlineSession', C12,
  """  startOnlineSession() {
    if (this.calib) this.exitCalib();""",
  """  startOnlineSession() {
    // r74 · FASE 170 · EL DUELO NO IRRUMPE: si soy el ANFITRIÓN, la sesión
    // queda PENDIENTE y salta LA ALERTA DE DUELO (icono de DOS PERSONAS
    // parpadeante + pitidos + voz) — nada se cierra hasta que el dueño de
    // la sala acepte (petición del dueño: la alerta llega «estando en
    // cualquier parte del juego jugando: entrenando, en un campeonato, en
    // el tutorial…»). El INVITADO entra igual que siempre (él la aceptó).
    if (this.net && this.net.role === 'host') {
      this._dueloPend = true;
      this.rules.message = T('duelo_alerta_msg');
      this.alertaDuelo();
      return;
    }
    this._dueloArrancar();
  }

  /** r74 · FASE 170 · el arranque REAL de la sesión online (el cuerpo de
   *  siempre): lo llama el INVITADO al entrar y el ANFITRIÓN al aceptar
   *  la alerta (dueloask SÍ). */
  _dueloArrancar() {
    if (this.calib) this.exitCalib();""")

# ── 170.5 · el sistema de la alerta (icono + parpadeo + pitidos + voz) ──
p('170.5 · métodos de la alerta', C12,
  """  showChampCurtain(id) {""",
  """  /** r74 · FASE 170 · LA ALERTA DE DUELO — quad pegado al RIG en la
   *  esquina superior: icono de DOS PERSONAS parpadeando 5 s, cinco
   *  pitidos y la voz del banco. Apuntar y gatillar abre el ASK. */
  alertaDuelo() {
    try {
      if (!this.rig) { this._dueloAsk(); return; }   // sin rig (2D): al ask
      this.hideDueloAlerta(true);
      const cv = document.createElement('canvas');
      cv.width = 256; cv.height = 256;
      const c = cv.getContext('2d');
      this._pintaDueloIcono(c, 256, 256);
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true,
        depthTest: false, depthWrite: false, fog: false });
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.44), mat);
      mesh.renderOrder = 90;
      const group = new THREE.Group();
      group.add(mesh);
      group.position.set(0.58, 0.58, -1.35);   // esquina superior derecha
      this.rig.add(group);
      this.dueloAlerta = { group, mesh, mat, tex, cv, c, t: 0 };
      // los 5 PITIDOS (cada 0,9 s) …
      for (let i = 0; i < 5; i++) {
        setTimeout(() => {
          try {
            this.audio.playOsc(880, 1320, 0.12, 'square', 0.14, 0);
          } catch (eB) { /* */ }
        }, Math.round(i * 900));
      }
      // … y la VOZ al segundo (banco de c03: en XR speechSynthesis no va)
      setTimeout(() => {
        try { this.audio.announce(T('duelo_alerta_voz'), true); } catch (eV) { /* */ }
      }, 1000);
    } catch (e) {
      console.warn('[duelo-alerta]', e);
      this._dueloAsk();
    }
  }

  /** r74 · el ICONO: placa oscura + marco de latón + DOS PERSONAS
   *  (siluetas cabeza y cuerpo) y el signo de exclamación. */
  _pintaDueloIcono(c, W, H) {
    c.clearRect(0, 0, W, H);
    c.fillStyle = 'rgba(8,12,24,0.94)';
    c.beginPath();
    if (c.roundRect) c.roundRect(8, 8, W - 16, H - 16, 30);
    else c.rect(8, 8, W - 16, H - 16);
    c.fill();
    c.strokeStyle = '#e8b45a';
    c.lineWidth = 6;
    c.beginPath();
    if (c.roundRect) c.roundRect(8, 8, W - 16, H - 16, 30);
    else c.rect(8, 8, W - 16, H - 16);
    c.stroke();
    const persona = (cx, cy, r, col) => {
      c.fillStyle = col;
      c.beginPath(); c.arc(cx, cy, r, 0, Math.PI * 2); c.fill();
      c.beginPath();
      if (c.roundRect) c.roundRect(cx - r * 1.5, cy + r + 6, r * 3, r * 1.7,
        r * 0.8);
      else c.rect(cx - r * 1.5, cy + r + 6, r * 3, r * 1.7);
      c.fill();
    };
    persona(W * 0.38, H * 0.42, 26, '#c9d4de');
    persona(W * 0.62, H * 0.42, 26, '#e8b45a');
    c.fillStyle = '#ffd257';
    c.font = '900 44px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText('!', W * 0.5, H * 0.78);
  }

  /** r74 · latido de la alerta: PARPADEO 3 Hz durante 5 s y fundido — el
   *  duelo queda PENDIENTE (aceptable desde el Multijugador). */
  _updateDueloAlerta(dt) {
    const S = this.dueloAlerta;
    if (!S) return;
    S.t += dt;
    if (S.t < 5) {
      S.mat.opacity = 0.55 + 0.45 * Math.abs(Math.sin(S.t * Math.PI * 3));
    } else {
      S.mat.opacity = Math.max(0, 1 - (S.t - 5) / 0.8);
      if (S.t > 5.8) this.hideDueloAlerta(true);
    }
  }

  hideDueloAlerta(inmediato) {
    const S = this.dueloAlerta;
    if (!S) return;
    this.dueloAlerta = null;
    try {
      if (S.group.parent) S.group.parent.remove(S.group);
      S.group.clear();
      S.tex.dispose();
      S.mat.dispose();
      S.mesh.geometry.dispose();
    } catch (e) { /* */ }
  }

  /** r74 · ¿el gatillo del mando i pulsa el icono? (rayo del control) */
  _dueloAlertaPulsa(i) {
    try {
      const S = this.dueloAlerta;
      if (!S) return false;
      const ray = this.rays && this.rays[i | 0];
      if (!ray) return false;
      if (!this._dueloRC) {
        this._dueloRC = new THREE.Raycaster();
        this._dueloO = new THREE.Vector3();
        this._dueloQ = new THREE.Quaternion();
        this._dueloD = new THREE.Vector3();
      }
      ray.getWorldPosition(this._dueloO);
      ray.getWorldQuaternion(this._dueloQ);
      this._dueloD.set(0, 0, -1).applyQuaternion(this._dueloQ);
      this._dueloRC.set(this._dueloO, this._dueloD);
      return !!this._dueloRC.intersectObject(S.mesh, false)[0];
    } catch (e) { return false; }
  }

  /** r74 · abre la confirmación (el menú se pone encima de lo que sea) */
  _dueloAsk() {
    this.menuPage = 'dueloask';
    try { this.rules.message = ''; } catch (eM) { /* */ }
    if (!this.menuOpen) this.toggleMenu();
    else this.drawMenu();
  }

  showChampCurtain(id) {""")

# ── 170.6 · tick: la alerta respira (tras el telón r72) ──
p('170.6 · tick de la alerta', C12,
  """    // r72 · TELÓN DE CARGA de campeonatos (pinta puntos, funde y desmonta)
    this._updateChampCurtain();""",
  """    // r72 · TELÓN DE CARGA de campeonatos (pinta puntos, funde y desmonta)
    this._updateChampCurtain();
    // r74 · FASE 170 · LA ALERTA DE DUELO respira (parpadeo + fundido)
    this._updateDueloAlerta(dt);""")

# ── 170.7 · el gatillo sobre el icono (antes que todo lo demás) ──
p('170.7 · gatillo de la alerta en onSelectStart', C12,
  """    if (this._arconoOn) {
      this._arconoClic(i);
      return;
    }""",
  """    if (this._arconoOn) {
      this._arconoClic(i);
      return;
    }

    // r74 · FASE 170 · LA ALERTA DE DUELO manda: gatillo sobre el icono
    // de DOS PERSONAS abre la confirmación (antes que cualquier otra cosa)
    if (this.dueloAlerta && this._dueloAlertaPulsa(i)) {
      this.audio.playOsc(760, 1180, 0.08, 'triangle', 0.12, 0);
      this._dueloAsk();
      return;
    }""")

# ── 170.8 · la página del ASK en el despachador ──
p('170.8 · rama dueloask', C12,
  """    if (this.menuPage === 'hallask') {""",
  """    // r74 · FASE 170 · ASK DEL DUELO PENDIENTE: salir y aceptar = cerrar
    // lo que esté haciendo (perderás los registros) y saltar al duelo.
    if (this.menuPage === 'dueloask') {
      this._vestPrompt(rects, {
        icono: 'multijugador', tituloKey: 'dueloask_t',
        subKey: 'dueloask_sub', hintKey: 'dueloask_hint',
        si: { id: 'dueloask_si', key: 'dueloask_si' },
        no: { id: 'dueloask_no', key: 'dueloask_no' },
      });
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this._menuTipDraw(c, rects);
      this._menuTexSube();
      return;
    }
    if (this.menuPage === 'hallask') {""")

# ── 170.9 · despacho SÍ/NO del duelo pendiente ──
p('170.9 · dueloask_si / dueloask_no', C12,
  """      case 'hallask_si': {""",
  """      case 'dueloask_si': {
        // r74 · FASE 170 · SÍ: cerrar lo que esté haciendo y saltar al
        // duelo (el arranque real de la sesión online ya conectada).
        this._dueloPend = false;
        this.hideDueloAlerta(true);
        this.audio.playOsc(760, 1180, 0.08, 'triangle', 0.12, 0);
        this._dueloArrancar();
        break;
      }
      case 'dueloask_no': {
        // r74 · FASE 170 · NO: se cuelga la sala (el rival queda libre) y
        // el juego sigue donde estaba — nada se ha cerrado.
        this._dueloPend = false;
        this.hideDueloAlerta(true);
        try { this.net.hangup(); } catch (eH) { /* */ }
        this._mjMode = null;
        this.rules.message = '';
        this.audio.playOsc(420, 300, 0.06, 'sine', 0.08, 0);
        this.menuPage = 'main';
        this.drawMenu();
        break;
      }
      case 'hallask_si': {""")

# ── 170.10 · el duelo en espera se puede aceptar desde el Multijugador ──
p('170.10 · aviso en _multiZonas', C12,
  """    let y = 236;
    const zona = (txt, yy) => {""",
  """    let y = 236;
    if (this._dueloPend) {
      // r74 · FASE 170 · duelo EN ESPERA: aceptar también desde aquí
      btn('page:dueloask', x0, y, w0, 78, T('dueloask_t'), false,
        undefined, undefined, 26);
      y += 94;
    }
    const zona = (txt, yy) => {""")


def main():
    textos = {C00: C00.read_text(encoding='utf-8'),
              C03: C03.read_text(encoding='utf-8'),
              C02: C02.read_text(encoding='utf-8'),
              C12: C12.read_text(encoding='utf-8')}
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
