#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r163e · RÓTULOS a prueba de cualquier fuente (la medición viva dio
'PLAY AGAINST THE MACHINE' = 565 px a 30 pt con la fuente ancha del
entorno: el bucle r161d salía por el suelo 22 SIN fijar la fuente y el
texto pintaba con la anterior → desborde del borde del botón, visto en la
captura). FIX:
· la fuente pintada SIEMPRE es la última medida (while en vez de for) y el
  suelo baja a 14 px — cualquier idioma cabe;
· tx 150 en los botones de JUGAR (el icono del arte llega a ~145 px — el
  rótulo a 118 le pisaba);
· el rótulo pasa a NAVY cuando el botón está en dorado _on (blanco sobre
  oro se lavaba — misma idea que los botones activos del legado)."""
import sys

F_C02 = '/home/z/my-project/src/game/core/c02_cfg_escena.js'
F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'

B = {}
for f in (F_C02, F_C12):
    with open(f, 'r', encoding='utf-8') as fh:
        B[f] = fh.read()

P = [
    # c02 · tx de los 5 botones de Jugar (el icono del arte llega a ~145)
    (F_C02, "etiquetaKey: 'jug_maquina', tx: 118, f: 40 },",
     "etiquetaKey: 'jug_maquina', tx: 150, f: 40 },", 1),
    (F_C02, "etiquetaKey: 'jug_entrena', tx: 118, f: 40 },",
     "etiquetaKey: 'jug_entrena', tx: 150, f: 40 },", 1),
    (F_C02, "etiquetaKey: 'sec_surv', tx: 118, f: 40 },",
     "etiquetaKey: 'sec_surv', tx: 150, f: 40 },", 1),
    (F_C02, "etiquetaKey: 'jug_escalera', tx: 118, f: 40 },",
     "etiquetaKey: 'jug_escalera', tx: 150, f: 40 },", 1),
    (F_C02, "etiquetaKey: 'tut_hub', tx: 118, f: 40 },",
     "etiquetaKey: 'tut_hub', tx: 150, f: 40 },", 1),
    # c12 · autoajuste a prueba de todo (while + suelo 14 + fuente exacta)
    (F_C12, """        // r161d · AUTOAJUSTE: la fuente baja hasta que el rótulo cabe en
        // el botón (tx..borde-26) — cualquier idioma, cualquier tema
        // r163 · TAPA MÁS BAJA: los rótulos solapaban partes del arte del
        // botón (informe del dueño) — la fuente arranca en min(f, 40).
        let fUI = Math.min(b.f || 48, 40);
        const txMax = b.w - (b.tx || 150) - 26;
        c.textAlign = 'left';
        c.textBaseline = 'middle';
        for (; fUI > 22; fUI -= 2) {
          c.font = '800 ' + fUI + 'px system-ui, sans-serif';
          if (c.measureText(lbl).width <= txMax) break;
        }
        c.fillStyle = 'rgba(255,255,255,0.98)';""",
     """        // r161d · AUTOAJUSTE: la fuente baja hasta que el rótulo cabe en
        // el botón (tx..borde-26) — cualquier idioma, cualquier tema
        // r163 · TAPA MÁS BAJA: los rótulos solapaban partes del arte del
        // botón (informe del dueño) — la fuente arranca en min(f, 40).
        // r163e · A PRUEBA DE FUENTES: la medición viva dio 565 px a 30 pt
        // con la fuente ancha del entorno y el for salía por el suelo SIN
        // fijar la fuente (pintaba con la anterior → desborde). Ahora el
        // while garantiza fuente pintada = fuente medida y el suelo baja a
        // 14 px: cualquier idioma cabe. tx 150 libra el icono del arte.
        let fUI = Math.min(b.f || 48, 40);
        const txMax = b.w - (b.tx || 150) - 18;
        c.textAlign = 'left';
        c.textBaseline = 'middle';
        c.font = '800 ' + fUI + 'px system-ui, sans-serif';
        while (fUI > 14 && c.measureText(lbl).width > txMax) {
          fUI -= 2;
          c.font = '800 ' + fUI + 'px system-ui, sans-serif';
        }
        // r163e · rótulo NAVY sobre el dorado _on (blanco sobre oro se
        // lavaba — la misma idea de los botones activos del legado)
        c.fillStyle = hov ? 'rgba(16,19,26,0.95)'
          : 'rgba(255,255,255,0.98)';""", 1),
]

mal = []
for i, (f, old, new, nn) in enumerate(P):
    cc = B[f].count(old)
    if cc != nn:
        mal.append((i, f.split('/')[-1], old[:60], cc, nn))
        continue
    B[f] = B[f].replace(old, new)
if mal:
    for i, nom, o, cc, nn in mal:
        print(f'✗ parche {i} [{nom}] «{o}…»: {cc} coincidencias (esperaba {nn})')
    sys.exit(1)
for f, s in B.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f"✓ {f.split('/')[-1]}: {len(s)} bytes")
print('✓ r163e: rótulos a prueba de fuentes · tx 150 · navy sobre _on')
