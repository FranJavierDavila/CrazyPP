#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r161c · ROTULADO de los botones de la cartela: el arte del dueño trae
barra+icono SIN texto (verificado) — la etiqueta la pinta el juego con T()
(claves i18n EXISTENTES del vestíbulo: hub_jugar, hub_multi, sec_crazy,
perfil_title, opts_title, dock_salir — es/en gratis, cero claves nuevas)."""
import sys

F_C02 = '/home/z/my-project/src/game/core/c02_cfg_escena.js'
F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'
with open(F_C02, 'r', encoding='utf-8') as f: c02 = f.read()
with open(F_C12, 'r', encoding='utf-8') as f: c12 = f.read()

P = []


def p(f, old, new, n=1):
    P.append((f, old, new, n))


# ── c02 · manifiesto: etiquetaKey + métricas del rótulo por botón ──────
p(F_C02, """          botones: [
            { id: 'page:jugar', img: 'Main/btn_Play', x: 898, y: 490, w: 520, h: 130 },
            { id: 'tab:multi', img: 'Main/btn_multijugador', x: 898, y: 638, w: 520, h: 130 },
            { id: 'page:champs', img: 'Main/btn_campeonatos', x: 898, y: 786, w: 520, h: 130 },
            { id: 'page:perfil', img: 'Main/btn_Perfil', x: 898, y: 934, w: 520, h: 130 },
            { id: 'page:opts', img: 'Main/btn_Ajustes', x: 898, y: 1082, w: 520, h: 130 },
            { id: 'salirweb', img: 'Main/btn_Salir', x: 898, y: 1230, w: 520, h: 130 },
          ],""",
"""          // r161c · ROTULADO: el arte trae barra+icono SIN texto — la
          // etiqueta la pinta el juego con T() (claves EXISTENTES del
          // vestíbulo → continuidad visual y es/en sin claves nuevas).
          // tx = x del texto dentro del botón · f = tamaño de fuente.
          botones: [
            { id: 'page:jugar', img: 'Main/btn_Play', x: 898, y: 490, w: 520, h: 130,
              etiquetaKey: 'hub_jugar', tx: 150, f: 48 },
            { id: 'tab:multi', img: 'Main/btn_multijugador', x: 898, y: 638, w: 520, h: 130,
              etiquetaKey: 'hub_multi', tx: 118, f: 48 },
            { id: 'page:champs', img: 'Main/btn_campeonatos', x: 898, y: 786, w: 520, h: 130,
              etiquetaKey: 'sec_crazy', tx: 118, f: 48 },
            { id: 'page:perfil', img: 'Main/btn_Perfil', x: 898, y: 934, w: 520, h: 130,
              etiquetaKey: 'perfil_title', tx: 118, f: 48 },
            { id: 'page:opts', img: 'Main/btn_Ajustes', x: 898, y: 1082, w: 520, h: 130,
              etiquetaKey: 'opts_title', tx: 118, f: 48 },
            { id: 'salirweb', img: 'Main/btn_Salir', x: 898, y: 1230, w: 520, h: 130,
              etiquetaKey: 'dock_salir', tx: 118, f: 48 },
          ],""")

# ── c12 · painter: rótulo blanco con sombra suave junto al icono ───────
p(F_C12, """    // botones: estado _on al apuntar (misma nomenclatura + _on)
    for (const b of def.botones || []) {
      const bi = this._uiK(b.img);
      const hov = this.menuHover.includes(rects.length);
      const img = (hov && im(bi + '_on')) || im(bi);
      if (img) c.drawImage(img, ox + b.x, b.y, b.w, b.h);
      rects.push(this._mapRect({ x: ox + b.x, y: b.y, w: b.w, h: b.h, id: b.id }));
    }
    return true;""",
"""    // botones: estado _on al apuntar (misma nomenclatura + _on) y
    // RÓTULO vivo (r161c · el arte del tema no hornea texto — T() manda)
    for (const b of def.botones || []) {
      const bi = this._uiK(b.img);
      const hov = this.menuHover.includes(rects.length);
      const img = (hov && im(bi + '_on')) || im(bi);
      if (img) c.drawImage(img, ox + b.x, b.y, b.w, b.h);
      const lbl = b.etiquetaKey ? T(b.etiquetaKey) : (b.etiqueta || '');
      if (lbl) {
        c.font = '800 ' + (b.f || 48) + 'px system-ui, sans-serif';
        c.textAlign = 'left';
        c.textBaseline = 'middle';
        c.fillStyle = 'rgba(255,255,255,0.98)';
        c.shadowColor = 'rgba(6,20,44,0.6)';
        c.shadowBlur = 8;
        c.fillText(lbl, ox + b.x + (b.tx || 150), b.y + b.h / 2 + 2);
        c.shadowBlur = 0;
      }
      rects.push(this._mapRect({ x: ox + b.x, y: b.y, w: b.w, h: b.h, id: b.id }));
    }
    return true;""")

mal = [(i, f.split('/')[-1], cc, nn) for i, (f, old, new, nn) in enumerate(P)
       if (cc := B[f].count(old) if (B := {F_C02: c02, F_C12: c12}) else 0) != nn]
if mal:
    for i, nom, cc, nn in mal:
        print(f'✗ parche {i} [{nom}]: {cc} coincidencias (esperaba {nn})')
    sys.exit(1)
for f, old, new, _ in P:
    B[f] = B[f].replace(old, new)
for f, s in B.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f"✓ {f.split('/')[-1]}: {len(s)} bytes")
assert B[F_C02].count('etiquetaKey') >= 12, 'etiquetas faltan en manifiesto'
print('✓ rotulado: 6 etiquetaKey en manifiesto + pintado T() en painter')
