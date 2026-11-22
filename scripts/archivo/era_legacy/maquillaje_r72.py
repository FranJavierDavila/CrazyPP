#!/usr/bin/env python3
# r72 · MAQUILLAJE DEL NIVEL 3 — el contenido legado viste el lenguaje nuevo.
# (petición del dueño: «todos los menús de tercer nivel siguen en el formato
#  antiguo sin maquetar con el nuevo diseño»)
#
# Tres cambios quirúrgicos, cero cambios de ids/conducta:
#  1 · btn compartido: relleno en degradado sutil + MARCO DE LATÓN en reposo
#      (antes gris neutro) — moderniza de golpe optsCat, teclados, asks,
#      sala, estados de multi y las páginas c13 (reciben este mismo pintor).
#  2 · rank: cabeceras de columna en oro (estilo placa de museo).
#  3 · rankme: ELO en oro + tarjetas de estadística con marco de latón.
import sys

PATH = '/home/z/my-project/upload/public/game.html'
s = open(PATH, encoding='utf-8').read()
orig_len = len(s)

EDITS = []

# ── 1 · btn compartido: lenguaje nuevo en reposo ──
old1 = """      const hovered = this.menuHover.includes(rects.length);
      rr(x, y, w, h, 14);
      if (active) {"""
new1 = """      const hovered = this.menuHover.includes(rects.length);
      rr(x, y, w, h, 16);
      if (active) {"""
EDITS.append(('1a · radio 14→16', old1, new1, 1))

old2 = """      } else {
        c.fillStyle = 'rgba(255,255,255,0.07)';
        c.fill();
        // r104 · borde más DEFINIDO (0.18 → 0.30): «opciones más claras y
        // mejor definidas» — cada botón se recorta bien sobre el fondo
        c.strokeStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.30)';"""
new2 = """      } else {
        // r72 · maquillaje del NIVEL 3 (petición del dueño: «los menús de
        // tercer nivel siguen en el formato antiguo»): el botón compartido
        // viste el lenguaje de las landings — relleno en degradado sutil y
        // MARCO DE LATÓN en reposo (antes gris neutro). OptCat, teclados,
        // asks, sala y las páginas de c13 reciben el mismo pintor: el nivel
        // 3 entero se maqueta en una sola pieza.
        const _g72 = c.createLinearGradient(x, y, x, y + h);
        _g72.addColorStop(0, 'rgba(255,255,255,0.10)');
        _g72.addColorStop(1, 'rgba(255,255,255,0.045)');
        c.fillStyle = _g72;
        c.fill();
        // r104 · borde DEFINIDO (conservado) · r72 · reposo en latón
        c.strokeStyle = hovered ? '#ffffff' : 'rgba(232,180,90,0.32)';"""
EDITS.append(('1b · btn reposo latón+degradado', old2, new2, 1))

# ── 2 · rank: cabeceras de columna en oro ──
old3 = """    // cabecera de columnas
    c.fillStyle = '#98a6b4';
    c.font = '700 20px system-ui, sans-serif';
    c.textAlign = 'left';
    c.fillText(T('wrl_col_name'), 150, 372);"""
new3 = """    // cabecera de columnas — r72 · en ORO (placa de museo, lenguaje nuevo)
    c.fillStyle = '#e8b45a';
    c.font = '800 22px system-ui, sans-serif';
    c.textAlign = 'left';
    c.fillText(T('wrl_col_name'), 150, 372);"""
EDITS.append(('2 · rank cabeceras oro', old3, new3, 1))

# ── 3a · rankme: ELO grande en oro ──
old4 = """    c.fillStyle = '#ffffff';
    c.font = '900 92px system-ui, sans-serif';
    c.fillText(String(D.elo || 1000), 512, 445);"""
new4 = """    // r72 · ELO en ORO (placa de RÉCORD del museo, lenguaje nuevo)
    c.fillStyle = '#ffd257';
    c.font = '900 92px system-ui, sans-serif';
    c.fillText(String(D.elo || 1000), 512, 445);"""
EDITS.append(('3a · rankme ELO oro', old4, new4, 1))

# ── 3b · rankme: tarjetas de estadística con marco de latón ──
old5 = """      c.fillStyle = 'rgba(255,255,255,0.06)';
      c.beginPath();
      if (c.roundRect) c.roundRect(cx - 140, colY, 280, 92, 14) : c.rect(cx - 140, colY, 280, 92);"""
# ojo: la variante real usa if/else de dos líneas
old5 = """      c.fillStyle = 'rgba(255,255,255,0.06)';
      c.beginPath();
      if (c.roundRect) c.roundRect(cx - 140, colY, 280, 92, 14); else c.rect(cx - 140, colY, 280, 92);
      c.fill();"""
new5 = """      c.fillStyle = 'rgba(255,255,255,0.06)';
      c.beginPath();
      if (c.roundRect) c.roundRect(cx - 140, colY, 280, 92, 14); else c.rect(cx - 140, colY, 280, 92);
      c.fill();
      // r72 · marco de latón (lenguaje de las landings)
      c.strokeStyle = 'rgba(232,180,90,0.35)';
      c.lineWidth = 2;
      c.stroke();"""
EDITS.append(('3b · rankme tarjetas latón', old5, new5, 1))

fail = False
for name, old, new, expect in EDITS:
    n = s.count(old)
    print(f'[{name}] ocurrencias old={n} (esperadas {expect})')
    if n != expect:
        print('  !! FALLO: conteo inesperado, NO se aplica')
        fail = True
        continue
    s = s.replace(old, new)
    print(f'  OK · delta {len(new)-len(old):+d} B')

if fail:
    print('RESULTADO: PARCIAL — revisar')
    sys.exit(1)

open(PATH, 'w', encoding='utf-8').write(s)
print(f'TAMAÑO: {orig_len} → {len(s)} B (delta {len(s)-orig_len:+d})')

s2 = open(PATH, encoding='utf-8').read()
print('CHECK btn latón (>=1):', s2.count("MARCO DE LATÓN en reposo (antes gris neutro)"))
print('CHECK radio 16 en btn (>=1):', s2.count('rr(x, y, w, h, 16);'))
print('CHECK ELO oro (>=1):', s2.count('ELO en ORO (placa de RÉCORD del museo'))
