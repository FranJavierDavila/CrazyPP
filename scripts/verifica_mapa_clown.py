#!/usr/bin/env python3
"""V2.138 — verificación VISUAL de los nodos medidos del mapa clown nuevo.
Dibuja: anillo de progreso (r_config) en ROJO + cobertura de tapa (rect
290×300 × ts) en CIAN sobre el arte, y recortes ampliados por nodo."""
import cv2
import numpy as np

SRC = '/home/z/my-project/upload/Mapa.png'
img = cv2.imread(SRC)

# (x, y, r_config = r_in×120/107.5, r_out medido, ts tapa)
NODES = [
    (226, 253, 114, 119, 0.88),   # CLOWN Nv.1  (sin tapa)
    (453, 507, 119, 126, 0.94),   # ARKANOID
    (700, 256, 109, 114, 0.86),   # CLOWN Nv.2
    (959, 508, 121, 128, 0.95),   # ARKANOID 2
    (1208, 322, 107, 113, 0.85),  # CLOWN Nv.3
]

out = img.copy()
for i, (x, y, rc, ro, ts) in enumerate(NODES):
    cv2.circle(out, (x, y), rc, (0, 0, 255), 3)          # anillo progreso
    hw, hh = int(290 * ts / 2), int(300 * ts / 2)        # tapa
    cv2.rectangle(out, (x - hw, y - hh), (x + hw, y + hh), (255, 255, 0), 2)
    cv2.drawMarker(out, (x, y), (0, 255, 0), cv2.MARKER_CROSS, 22, 3)
    crop = img[max(0, y - ro - 30):y + ro + 30, max(0, x - ro - 30):x + ro + 30]
    if crop.size:
        crop = cv2.resize(crop, (crop.shape[1] * 2, crop.shape[0] * 2),
                          interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(f'/home/z/my-project/scripts/clown_nodo{i}.png', crop)

cv2.imwrite('/home/z/my-project/scripts/clown_mapa_final.png', out)
print('guardado clown_mapa_final.png + clown_nodo{i}.png')
