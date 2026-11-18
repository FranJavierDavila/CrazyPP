#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""maquillaje_r74_f168.py — FASE 168 «ESCOGER HALL · EL CANDADO AVISA» (r74).

Encargos del dueño que cierra:
  1 · MI CASA: «Volver al Hall» no tiene sentido → «ESCOGER HALL»: página
      nueva con las 6 variantes de HALL_VARIANTES como placas de museo;
      activa en oro, libres con aro de latón y las BLOQUEADAS con el
      candado de ARCANOS pintado SOBRE la placa + su hito.
  2 · SIEMPRE que un apartado esté bloqueado: el candado de la sala de
      Arcanos (PP_ICONS.candado — el mismo pintor canvas) dibujado sobre
      el botón: tarjetas de CAMPEONATOS lockadas, divisiones de CARRERA
      bloqueadas, SKINS de BOLA, TEMAS de sala y variantes del HALL en
      Ajustes (fuera el prefijo textual 🔒).
  3 · Todos los subniveles, por profundos que sean, en la estética nueva:
      las tarjetas del ÁREA de Entrenamiento (Dirección/Altura/Giro/
      Saque/Ritmo) pasan del degradado saturado a la PLACA DE MUSEO con
      el color del área en el aro del medallón.
"""
import pathlib
import sys

RAIZ = pathlib.Path('/home/z/my-project/upload/src/game/core')
C00 = RAIZ / 'c00_pre_three.js'
C02 = RAIZ / 'c02_cfg_escena.js'
C12 = RAIZ / 'c12_pingponggame.js'
C13 = RAIZ / 'c13_ui_arranque.js'

PARCHES = []


def p(nombre, fichero, ancla, nuevo, veces=1):
    PARCHES.append((nombre, fichero, ancla, nuevo, veces))


# ── 168.1 · MI CASA: «Volver al Hall» → «ESCOGER HALL» ──
p('168.1 · tarjeta MI CASA page:hallpick', C02,
  """        { id: 'homehall', icono: 'vestibulo', etiquetaKey: 'hall_home_btn',
          gradiente: ['#7c94c4', '#3c5280'] },""",
  """        { id: 'page:hallpick', icono: 'vestibulo', etiquetaKey: 'hall_pick_btn',
          gradiente: ['#7c94c4', '#3c5280'] },""")

# ── 168.2 · concha: página hallpick ──
p('168.2 · shell hallpick', C02,
  """    champhist: { tituloKey: 'hist_title', icono: 'campeonatos', volver: 'page:champs' },""",
  """    champhist: { tituloKey: 'hist_title', icono: 'campeonatos', volver: 'page:champs' },
    // r74 · FASE 168 · ESCOGER HALL (MI CASA): las 6 variantes + candados
    hallpick: { tituloKey: 'hall_pick_t', icono: 'vestibulo',
      volver: 'page:main' },""")

# ── 168.3 · i18n (es + en) ──
p('168.3a · i18n es', C00,
  """    hall_home_hint: 'El hall es tu casa: ajustes y cambio de modo viven allí',""",
  """    hall_home_hint: 'El hall es tu casa: ajustes y cambio de modo viven allí',
    // r74 · FASE 168 · ESCOGER HALL
    hall_pick_btn: '⌂ ESCOGER HALL',
    hall_pick_t: 'ESCOGER HALL',
    hall_pick_hint: 'tu estancia: el museo clásico y los salones que desbloquees',
    hall_actual: 'ACTUAL',
    hall_disponible: 'disponible',
    hall_visita: 'De visita online ves el salón del ANFITRIÓN',""")

p('168.3b · i18n en', C00,
  """    hall_home_hint: 'The hall is home: settings and mode changes live there',""",
  """    hall_home_hint: 'The hall is home: settings and mode changes live there',
    // r74 · FASE 168 · PICK A HALL
    hall_pick_btn: '⌂ PICK A HALL',
    hall_pick_t: 'PICK A HALL',
    hall_pick_hint: 'your room: the classic museum and the halls you unlock',
    hall_actual: 'CURRENT',
    hall_disponible: 'available',
    hall_visita: 'Online visits show the hall of the HOST',""")

# ── 168.4 · hint del hallpick en el Vestíbulo ──
p('168.4 · _vestSubPorId hallpick', C12,
  """      case 'homehall': return T('hall_home_hint');""",
  """      case 'homehall': return T('hall_home_hint');
      // r74 · FASE 168 · la tarjeta de MI CASA abre el ESCOGER HALL
      case 'page:hallpick': return T('hall_pick_hint');""")

# ── 168.5 · despacho de la página hallpick ──
p('168.5 · dispatcher hallpick', C12,
  """    if (this.menuPage && this.menuPage.indexOf('opts') === 0 &&
        this.menuPage !== 'opts') {""",
  """    // r74 · FASE 168 · ESCOGER HALL: MI CASA ya no «vuelve» — elige.
    if (this.menuPage === 'hallpick') {
      this.drawMenuHallPick(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this._menuTipDraw(c, rects);
      this._menuTexSube();
      return;
    }
    if (this.menuPage && this.menuPage.indexOf('opts') === 0 &&
        this.menuPage !== 'opts') {""")

# ── 168.6 · el pintor de la página (antes de _vestPrompt) ──
p('168.6 · drawMenuHallPick', C12,
  """  _vestPrompt(rects, cfg) {""",
  """  /** r74 · FASE 168 · ESCOGER HALL (MI CASA → sustituye «Volver al
   *  Hall», que no tenía sentido en el primer nivel): las 6 variantes de
   *  HALL_VARIANTES como placas de museo — la ACTIVA en oro, las libres
   *  con aro de latón y las BLOQUEADAS con el candado de ARCANOS pintado
   *  SOBRE la placa + su hito (petición del dueño). La elección reusa el
   *  handler hallv:<id> (LS + re-viste el salón EN VIVO). */
  drawMenuHallPick(rects) {
    const c = this.menuCanvas.getContext('2d');
    const per = this._hallPerfil();
    const pC = CONFIG_MENUS.arco.panelas[1];
    const mm0 = this._menuMap;
    this._menuMap = null;
    c.save();
    c.setTransform(1, 0, 0, 1, 0, 0);
    const x0 = pC.x + 40, w0 = pC.w - 80;
    let y = 300;
    if (per.peer) {
      c.fillStyle = '#b07aff';
      c.font = '600 26px system-ui, sans-serif';
      c.textAlign = 'left';
      c.textBaseline = 'alphabetic';
      c.fillText(T('hall_visita'), x0, y + 20);
      y += 56;
    }
    for (const v of HALL_VARIANTES) {
      const libreH = !v.lock || this._mesaLibre(v.lock);
      const activoH = this._hallVarDef().id === v.id;
      const hR = 136;
      const hovered = this.menuHover.includes(rects.length);
      this._vestPlaca73(c, x0, y, w0, hR, 22);
      this._vestRR(c, x0, y, w0, hR, 22);
      c.strokeStyle = activoH ? 'rgba(255,210,87,0.85)'
        : (hovered && libreH ? '#ffffff' : 'rgba(232,180,90,0.32)');
      c.lineWidth = (activoH || hovered) ? 4 : 2;
      c.stroke();
      const ir = 46;
      this._vestMedallion(c, x0 + 34 + ir, y + hR / 2, ir, 'vestibulo',
        activoH ? '#ffd25e' : (libreH ? null : '#5f7183'));
      c.textAlign = 'left';
      c.textBaseline = 'alphabetic';
      c.fillStyle = '#ffffff';
      c.font = '800 34px system-ui, sans-serif';
      c.fillText(T(v.nameKey), x0 + 112, y + 56);
      c.font = '600 22px system-ui, sans-serif';
      c.fillStyle = activoH ? '#ffd257'
        : (libreH ? 'rgba(228,240,255,0.92)' : '#93a1b0');
      c.fillText(activoH ? T('hall_actual')
        : (libreH ? T('hall_disponible')
          : (this._mesaLockTxt(v.lock) || T('mesa_lock_hint'))),
        x0 + 112, y + 98);
      // r74 · el candado de ARCANOS sobre las variantes bloqueadas
      if (!libreH) PP_ICONS.candado(c, x0 + w0 - 64, y + hR / 2, 1.15);
      rects.push({ x: x0 - 6, y: y - 4, w: w0 + 12, h: hR + 8,
        id: 'hallv:' + v.id });
      y += hR + 20;
    }
    c.restore();
    this._menuMap = mm0;
  }

  _vestPrompt(rects, cfg) {""")

# ── 168.7 · candado en las rejillas (tarjetas con bloq) ──
p('168.7 · candado en _menuRejilla', C12,
  """        const ir = 44, icx = gx + 30 + ir, icy = y + hAuto / 2;
        this._vestMedallion(c, icx, icy, ir, t.icono,
          t.gradiente ? t.gradiente[0] : null);""",
  """        const ir = 44, icx = gx + 30 + ir, icy = y + hAuto / 2;
        this._vestMedallion(c, icx, icy, ir, t.icono,
          t.gradiente ? t.gradiente[0] : null);
        // r74 · FASE 168 · SIEMPRE que un apartado está bloqueado: el
        // candado de ARCANOS pintado SOBRE la placa (petición del dueño)
        if (t.bloq) PP_ICONS.candado(c, gx + gw - 56, y + hAuto / 2, 1.0);""")

# ── 168.8 · champs lockadas llevan bloq ──
p('168.8 · champs: bloq en lockadas', C12,
  """        sub: lockado ? T('champ_locked_hint')
          : (hint || T('hub_champ_hint')),
        leyenda,""",
  """        sub: lockado ? T('champ_locked_hint')
          : (hint || T('hub_champ_hint')),
        bloq: lockado,
        leyenda,""")

# ── 168.9 · SKINS DE BOLA: fuera el 🔒 textual, dentro el candado ──
p('168.9 · candado en skins de bola', C12,
  """          btn('bola_skin:' + s.id, 56 + (i % 3) * 312, y + Math.floor(i / 3) * 62,
            288, 54, (libre ? '' : '🔒 ') + T(s.nameKey),""",
  """          btn('bola_skin:' + s.id, 56 + (i % 3) * 312, y + Math.floor(i / 3) * 62,
            288, 54, T(s.nameKey),""")
# tras el btn de bola_skin: dibujar el candado (cierre del forEach)
p('168.9b · candado pintado en skins de bola', C12,
  """            288, 54, T(s.nameKey),
            activo, undefined, activo, 21);
        });""",
  """            288, 54, T(s.nameKey),
            activo, undefined, activo, 21);
          if (!libre) {
            PP_ICONS.candado(c, 56 + (i % 3) * 312 + 288 - 30,
              y + Math.floor(i / 3) * 62 + 27, 0.8);
          }
        });""", veces=1)

# ── 168.10 · TEMAS DE SALA: igual tratamiento ──
p('168.10a · temas sin 🔒 textual', C12,
  """        const themes = ROOM_THEMES.map((t0) => ['theme:' + t0.key,
          (t0.lock && !this._salaTemaLibre(t0.lock) ? '🔒 ' : '') +
          (t0.nameKey ? T(t0.nameKey) : t0.name)]);
        themes.forEach(([id, name], i) => {
          btn(id, 56 + (i % 2) * 464, y + Math.floor(i / 2) * 64, 448, 56, name,
            this.theme === id.split(':')[1], undefined, undefined, 23);
        });""",
  """        // r74 · FASE 168 · los temas bloqueados llevan el candado de
        // ARCANOS dibujado sobre el botón (fuera el prefijo textual 🔒)
        const themes = ROOM_THEMES.map((t0) => ['theme:' + t0.key,
          (t0.nameKey ? T(t0.nameKey) : t0.name),
          t0.lock && !this._salaTemaLibre(t0.lock)]);
        themes.forEach(([id, name, cerrado], i) => {
          btn(id, 56 + (i % 2) * 464, y + Math.floor(i / 2) * 64, 448, 56, name,
            this.theme === id.split(':')[1], undefined, undefined, 23);
          if (cerrado) {
            PP_ICONS.candado(c, 56 + (i % 2) * 464 + 448 - 30,
              y + Math.floor(i / 2) * 64 + 28, 0.8);
          }
        });""")

# ── 168.11 · variantes del HALL en salahall: igual ──
p('168.11 · candado en variantes (salahall)', C12,
  """            btn('hall_var:' + v.id, 56 + (i % 3) * 312,
              y + Math.floor(i / 3) * 62, 288, 54,
              (libreH ? '' : '🔒 ') + T(v.nameKey),
              activoH, undefined, activoH, 21);""",
  """            btn('hall_var:' + v.id, 56 + (i % 3) * 312,
              y + Math.floor(i / 3) * 62, 288, 54,
              T(v.nameKey),
              activoH, undefined, activoH, 21);
            if (!libreH) {
              PP_ICONS.candado(c, 56 + (i % 3) * 312 + 288 - 30,
                y + Math.floor(i / 3) * 62 + 27, 0.8);
            }""")

# ── 168.12 · división CARRERA: el bloqueo en el botón de la división ──
# (la tarjeta de división bloqueada de drawMenuCarrera ya lleva bloq; el
#  candado en filas de rivales no aplica: los rivales no se bloquean)
p('168.12 · carreradiv: candado en cabecera bloqueada', C12,
  """      const ir = 42;
      this._vestMedallion(c, x0 + 34 + ir, y + rh / 2, ir, 'partido',
        vencido ? '#7fb069' : '#4a5872');""",
  """      const ir = 42;
      this._vestMedallion(c, x0 + 34 + ir, y + rh / 2, ir, 'partido',
        vencido ? '#7fb069' : '#4a5872');
      if (!retable) {
        // r74 · FASE 168 · rivales de OTRAS divisiones: candado de ARCANOS
        PP_ICONS.candado(c, x0 + w0 - 56, y + rh / 2, 1.0);
      }""")

# ── 168.13 · ÁREAS de Entrenamiento en placa de museo (c13) ──
p('168.13 · drawArea en placa de museo', C13,
  """        const gr = c.createLinearGradient(40, y, 984, y + 172);
        gr.addColorStop(0, a.g0); gr.addColorStop(1, a.g1);
        c.fillStyle = gr; c.globalAlpha = isOn ? 0.95 : 0.8; c.fill(); c.globalAlpha = 1;
        c.strokeStyle = isOn ? '#f0c85a' : 'rgba(255,255,255,0.28)'; c.lineWidth = isOn ? 5 : 3;""",
  """        // r74 · FASE 168 · placa de museo en las tarjetas del ÁREA (el
        // color del área sobrevive en el aro del medallón, no en el relleno
        // saturado) — la estética nueva hasta el último subnivel.
        if (game._vestPlaca73) game._vestPlaca73(c, 40, y, 944, 172, 22);
        c.strokeStyle = isOn ? '#f0c85a' : 'rgba(232,180,90,0.32)'; c.lineWidth = isOn ? 5 : 3;""")


def main():
    textos = {C00: C00.read_text(encoding='utf-8'),
              C02: C02.read_text(encoding='utf-8'),
              C12: C12.read_text(encoding='utf-8'),
              C13: C13.read_text(encoding='utf-8')}
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
    for f in (C00, C02, C12, C13):
        print('  ' + f.name + ': ' + str(len(f.read_text(encoding="utf-8").encode("utf-8"))) + ' B')


if __name__ == '__main__':
    main()
