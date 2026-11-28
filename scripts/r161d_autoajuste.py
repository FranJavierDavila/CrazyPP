#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r161d · AUTOAJUSTE del rótulo al ancho del botón (CHAMPIONSHIPS se
salía en inglés): la fuente baja hasta caber (mínimo 22 px). Válido para
cualquier idioma y cualquier tema futuro."""
import sys

F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'
with open(F_C12, 'r', encoding='utf-8') as f: c12 = f.read()

old = """      const lbl = b.etiquetaKey ? T(b.etiquetaKey) : (b.etiqueta || '');
      if (lbl) {
        c.font = '800 ' + (b.f || 48) + 'px system-ui, sans-serif';
        c.textAlign = 'left';
        c.textBaseline = 'middle';
        c.fillStyle = 'rgba(255,255,255,0.98)';"""
new = """      const lbl = b.etiquetaKey ? T(b.etiquetaKey) : (b.etiqueta || '');
      if (lbl) {
        // r161d · AUTOAJUSTE: la fuente baja hasta que el rótulo cabe en
        // el botón (tx..borde-26) — cualquier idioma, cualquier tema
        let fUI = b.f || 48;
        const txMax = b.w - (b.tx || 150) - 26;
        c.textAlign = 'left';
        c.textBaseline = 'middle';
        for (; fUI > 22; fUI -= 2) {
          c.font = '800 ' + fUI + 'px system-ui, sans-serif';
          if (c.measureText(lbl).width <= txMax) break;
        }
        c.fillStyle = 'rgba(255,255,255,0.98)';"""
assert c12.count(old) == 1, f'parche autoajuste: {c12.count(old)} coincidencias'
c12 = c12.replace(old, new)
old2 = """        c.fillText(lbl, ox + b.x + (b.tx || 150), b.y + b.h / 2 + 2);
        c.shadowBlur = 0;"""
new2 = """        c.fillText(lbl, ox + b.x + (b.tx || 150), b.y + b.h / 2 + 2);
        c.shadowBlur = 0;
        c.font = '800 34px system-ui, sans-serif';   // restaura la del resto"""
assert c12.count(old2) == 1, 'restauración de fuente'
c12 = c12.replace(old2, new2)
with open(F_C12, 'w', encoding='utf-8') as fh:
    fh.write(c12)
print(f'✓ c12 autoajuste: {len(c12)} bytes')
