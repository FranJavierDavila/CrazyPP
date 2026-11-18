#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""maquillaje_r73.py — FASE 167 «EL NIVEL 3, PLACA A PLACA» (r73).

Petición pendiente del dueño (r72: «todos los menús de tercer nivel siguen
en el formato antiguo sin maquetar con el nuevo diseño»): r72 maquetó el
BOTÓN compartido (_menuBtn) y Ajustes/Ranking; quedaban las TARJETAS de
rejilla pintadas a caramelo saturado. Con UNA pieza por familia:

  P1 · _menuRejilla      → PLACA DE MUSEO (base oscura + overlay sutil +
                            MARCO DE LATÓN); el gradiente de la tarjeta
                            sobrevive como ARO del medallón (wayfinding).
                            Viste: AJUSTES, SALA (4 tarjetas vía _modeCard
                            aparte), MULTIJUGADOR, RANKING, CAMPEONATOS,
                            ENTRENAR y CARRERA.
  P2 · _vestMedallion    → parámetro opcional `aro` (tinte de categoría);
                            sin tinte queda el blanco de siempre (Vestíbulo
                            y prompts intactos). Nuevo método _aroTinte.
  P3 · drawMenuCarreraDiv→ filas de rivales en placa de museo; estado
                            (vencido/pendiente) en el aro del medallón.
  P4 · _modeCard         → tarjetas de SALA (Room/Mesa/Bola/Hall) y del
                            hub legado en placa de museo; aro teñido.

NO se toca: el VESTÍBULO (referencia caramelo aprobada del dueño), los
prompts de confirmación, los héroes de acción (▶ JUGAR, JUGAR de champuno,
CHALLENGE verde) y el pintor _vestCandy en sí.

Parche EN LAS FUENTES (lección r72: el artefacto se regenera vía bump, no
a mano). Anchoras exactas: el script aborta si un ancla no aparece UNA vez.
"""
import pathlib
import sys

C12 = pathlib.Path('/home/z/my-project/upload/src/game/core/'
                   'c12_pingponggame.js')

PARCHES = []

# ── P2a · método _aroTinte + placa de museo, ANTES de _vestMedallion ──
PARCHES.append((
    'P2a · _aroTinte + _vestPlaca73 antes de _vestMedallion',
    '  _vestMedallion(c, cx, cy, r, nombre) {\n',
    '''  // r73 · FASE 167 · hex → rgba de ARO (0,62). Lo no-hex devuelve ''
  // (sin tinte: el medallón queda con su blanco de siempre).
  _aroTinte(col) {
    const s = String(col || '');
    if (!/^#[0-9a-fA-F]{6}$/.test(s)) return '';
    const n = parseInt(s.slice(1), 16);
    return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' +
      (n & 255) + ',0.62)';
  }

  // r73 · FASE 167 · LA PLACA DE MUSEO — mismo lenguaje que el botón
  // compartido r72: base oscura + overlay blanco sutil + MARCO DE LATÓN.
  // Visten así las rejillas del nivel 3 (AJUSTES, MULTIJUGADOR, RANKING,
  // CAMPEONATOS, ENTRENAR, CARRERA), las filas de rivales de la división
  // y las tarjetas de _modeCard. El Vestíbulo (referencia del dueño), los
  // prompts y los héroes de acción conservan su caramelo.
  _vestPlaca73(c, x, y, w, h, r) {
    this._vestRR(c, x, y, w, h, r);
    c.fillStyle = 'rgba(8,12,24,0.55)';
    c.fill();
    const g = c.createLinearGradient(0, y, 0, y + h);
    g.addColorStop(0, 'rgba(255,255,255,0.10)');
    g.addColorStop(1, 'rgba(255,255,255,0.045)');
    c.fillStyle = g;
    c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.32)';
    c.lineWidth = 2;
    c.stroke();
  }

  // r73 · FASE 167 · el medallón admite ARO teñido: en las placas del
  // nivel 3 el color de categoría sobrevive en el aro (no en el relleno).
  _vestMedallion(c, cx, cy, r, nombre, aro) {
'''))

# ── P2b · el aro del medallón responde al tinte ──
PARCHES.append((
    'P2b · aro del medallón teñible',
    '''    c.lineWidth = 4;
    c.strokeStyle = 'rgba(255,255,255,0.85)';
    c.stroke();
    const im = this._vestIcono(nombre);''',
    '''    c.lineWidth = 4;
    c.strokeStyle = this._aroTinte(aro) || 'rgba(255,255,255,0.85)';
    c.stroke();
    const im = this._vestIcono(nombre);'''))

# ── P1 · tarjeta de rejilla: caramelo → placa de museo ──
PARCHES.append((
    'P1 · _menuRejilla viste placa de museo',
    '''        const hovered = this.menuHover.includes(rects.length);
        this._vestCandy(c, gx, y, gw, hAuto, t.gradiente, 26);
        const ir = 44, icx = gx + 30 + ir, icy = y + hAuto / 2;
        this._vestMedallion(c, icx, icy, ir, t.icono);''',
    '''        const hovered = this.menuHover.includes(rects.length);
        // r73 · FASE 167 · la tarjeta de rejilla viste PLACA DE MUSEO
        // (r72 maquetó el botón compartido; aquí la tarjeta entera): el
        // color de categoría sobrevive como ARO del medallón — wayfinding
        // sin caramelo (petición del dueño sobre el formato antiguo).
        this._vestPlaca73(c, gx, y, gw, hAuto, 26);
        const ir = 44, icx = gx + 30 + ir, icy = y + hAuto / 2;
        this._vestMedallion(c, icx, icy, ir, t.icono,
          t.gradiente ? t.gradiente[0] : null);'''))

# ── P3 · filas de rivales en la división ──
PARCHES.append((
    'P3a · fila de rival en placa de museo',
    '''      const rh = 118;
      this._vestCandy(c, x0, y, w0, rh, vencido
        ? ['#7fb069', '#3f6e3a'] : ['#4a5872', '#28324a'], 22);''',
    '''      const rh = 118;
      // r73 · FASE 167 · placa de museo por RIVAL: el estado sobrevive en
      // el aro del medallón (vencido verde, pendiente acero), no en el
      // relleno saturado.
      this._vestPlaca73(c, x0, y, w0, rh, 22);'''))

PARCHES.append((
    'P3b · medallón del rival con aro de estado',
    '''      const ir = 42;
      this._vestMedallion(c, x0 + 34 + ir, y + rh / 2, ir, 'partido');''',
    '''      const ir = 42;
      this._vestMedallion(c, x0 + 34 + ir, y + rh / 2, ir, 'partido',
        vencido ? '#7fb069' : '#4a5872');'''))

# ── P4 · _modeCard (tarjetas de SALA + hub legado) ──
PARCHES.append((
    'P4 · _modeCard en placa de museo con aro teñido',
    '''    const g = c.createLinearGradient(x, y, x, y + h);
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
    c.strokeStyle = 'rgba(255,255,255,0.4)'; c.lineWidth = 2.5; c.stroke();''',
    '''    // r73 · FASE 167 · placa de museo en _modeCard (SALA y hub legado):
    // fuera el relleno saturado — base oscura + overlay sutil + marco de
    // latón (gold conserva su aro dorado); el color del modo sobrevive
    // como ARO del medallón, no como caramelo.
    this._vestPlaca73(c, x, y, w, h, 22);
    c.strokeStyle = hovered ? '#ffffff'
      : (gold ? 'rgba(255,210,87,0.85)' : 'rgba(232,180,90,0.32)');
    c.lineWidth = hovered ? 5 : 2;
    c.stroke();
    // insignia circular con el icono del modo (aro teñido por categoría)
    const cx = x + 76, cy = y + h / 2;
    c.beginPath(); c.arc(cx, cy, 50, 0, Math.PI * 2);
    c.fillStyle = 'rgba(0,0,0,0.30)'; c.fill();
    c.strokeStyle = this._aroTinte(g0) || 'rgba(255,255,255,0.4)';
    c.lineWidth = 2.5; c.stroke();'''))


def main():
    src = C12.read_text(encoding='utf-8')
    total = 0
    for nombre, ancla, nuevo in PARCHES:
        n = src.count(ancla)
        if n != 1:
            sys.exit('✗ ' + nombre + ': ancla aparece ' + str(n) +
                     ' veces (se exige exactamente 1)')
        src = src.replace(ancla, nuevo)
        total += 1
        print('✓ ' + nombre)
    C12.write_text(src, encoding='utf-8')
    print('PARCHES APLICADOS: ' + str(total) + '/' + str(len(PARCHES)) +
          ' · ' + str(C12) + ' (' + str(len(src.encode("utf-8"))) + ' B)')
    # conservación: el candy del Vestíbulo sigue vivo (3 usos)
    for pieza in ['_vestCandy(c, bx, by, bw, bh,',  # concha
                  'this._vestCandy(c, x, y, w, h, cardDef.gradiente, rad)',
                  '_vestCandy(c, cx - r, cy - r, r * 2, r * 2,']:
        k = src.count(pieza)
        print(('  OK  ' if k == 1 else '  ✗  ') + 'conservado: ' +
              pieza[:44] + ' x' + str(k))


if __name__ == '__main__':
    main()
