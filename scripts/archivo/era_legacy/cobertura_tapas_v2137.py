#!/usr/bin/env python3
"""V2.137 — SIMULACIÓN 2D de la cobertura de las tapas sobre el arte nuevo.
Geometría correcta: el medallón (círculo inscrito r = 145,5·ts px de arte,
centrado en tx/ty) debe contener ① el CÍRCULO EXTERIOR del anillo dorado
(distancia entre centros + r_ext ≤ r_tapa) y ② el RECT del DÍGITO numerado
(4 esquinas dentro). La pestaña decorativa del anillo PUEDE asomar (como las
estrellas del Oeste aprobadas). Pinta el resultado para inspección humana."""
import numpy as np
from PIL import Image, ImageDraw

SRC = '/home/z/my-project/upload/Mapa.png'
im = Image.open(SRC).convert('RGB')

# nodos v2.137 (magia/index.js) — tapa: (tx, ty, ts)
NODOS = [
    dict(x=229,  y=258, r=126, tapa=False),
    dict(x=456,  y=508, r=131, tapa=True, tx=456,  ty=490, ts=1.18),
    dict(x=701,  y=253, r=122, tapa=True, tx=701,  ty=220, ts=1.20),
    dict(x=966,  y=506, r=132, tapa=True, tx=966,  ty=477, ts=1.25),
    dict(x=1232, y=162, r=126, tapa=True, tx=1205, ty=150, ts=1.22),
]
# ① anillo exterior: centro = nodo, radio exterior = banda media + 27 px margen
# (claves 0-INDEXADAS como los nodos; nodo 5 sin anillo → semiancho de la figura)
R_EXT = {0: 112 + 27, 1: 117 + 27, 2: 109 + 27, 3: 118 + 27, 4: 105}
# ② rect del dígito numerado [x0,y0,x1,y1] (medido en crops)
DIGITO = {
    1: [410, 325, 460, 395],     # «2»
    2: [678, 75, 727, 145],      # «3»
    3: [940, 320, 990, 390],     # «4»
    4: [1052, 82, 1128, 228],    # «5» (dígito alto en la burbuja)
}

img = im.copy()
d = ImageDraw.Draw(img)
ok_all = True
for i, n in enumerate(NODOS):
    if not n['tapa']:
        continue
    r = 145.5 * n['ts']
    cx, cy = n['tx'], n['ty']
    # ① anillo entero
    dr = ((cx - n['x']) ** 2 + (cy - n['y']) ** 2) ** 0.5
    cubre_anillo = (dr + R_EXT[i]) <= r
    # ② dígito entero
    x0, y0, x1, y1 = DIGITO[i]
    peq = max(((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
              for px in (x0, x1) for py in (y0, y1))
    cubre_digito = peq <= r
    ok_all &= cubre_anillo and cubre_digito
    print(f"nodo {i+1}: tapa r={r:.0f} en ({cx},{cy}) · anillo: {dr:.0f}+{R_EXT[i]}"
          f"={dr + R_EXT[i]:.0f} ≤ {r:.0f} → {'✓' if cubre_anillo else '✗'} · "
          f"dígito: peor esquina {peq:.0f} ≤ {r:.0f} → {'✓' if cubre_digito else '✗'}")
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 0, 0), width=3)
    d.circle([n['x'], n['y']], R_EXT[i], outline=(0, 160, 255), width=2)
    d.rectangle([x0, y0, x1, y1], outline=(0, 255, 0), width=2)

# los medallones NO deben invadir los anillos de nodos actuales (1 y, tras
# ganar, el siguiente): anillo 1 vivo siempre al empezar
r1 = R_EXT[1]
for i, n in enumerate(NODOS):
    if not n['tapa']:
        continue
    r = 145.5 * n['ts']
    dist = ((n['tx'] - 229) ** 2 + (n['ty'] - 258) ** 2) ** 0.5
    libre = (dist - r) > r1
    ok_all &= libre
    print(f"nodo {i+1} vs anillo 1: dist-r={dist - r:.0f} > {r1} → "
          f"{'LIBRE ✓' if libre else 'INVADE ✗'}")

img.save('/home/z/my-project/scripts/_tapa_cobertura_v2137.png')
print('\nresultado:', 'TODO CUBRE ✓' if ok_all else 'HAY HUECOS ✗',
      '→ scripts/_tapa_cobertura_v2137.png')
