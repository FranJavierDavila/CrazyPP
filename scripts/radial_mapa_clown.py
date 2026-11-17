#!/usr/bin/env python3
"""V2.138 — perfil radial DORADO de los 5 medallones del mapa clown nuevo.
Para cada centro Hough: rayos en 360 grados, primera/última aparición de
píxel DORADO (anillo) -> banda del anillo [r_in, r_out] por nodo.
Regla V2.137: r_config = r_in × (120/107,5) hace que el anillo de progreso
abrace el borde dorado (calibrada contra el arte viejo del clown)."""
import cv2
import numpy as np

SRC = '/home/z/my-project/upload/Mapa.png'
img = cv2.imread(SRC)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
H, W = img.shape[:2]

# centros Hough (medallones reales, en orden de ruta 0..4)
CENTERS = [(226, 253), (453, 507), (700, 256), (959, 508), (1208, 322)]

# máscara DORADA: hue ~18-38 (oro/naranja), saturación y valor altos
gold = ((hsv[:, :, 0] >= 15) & (hsv[:, :, 0] <= 38) &
        (hsv[:, :, 1] >= 110) & (hsv[:, :, 2] >= 120)).astype(np.uint8)

out = img.copy()
print('nodo   centro          r_in  r_out  mediana_out   r_config(120/107.5×r_in)')
for i, (cx, cy) in enumerate(CENTERS):
    rins, routs = [], []
    for a in np.linspace(0, 2 * np.pi, 720, endpoint=False):
        rs = np.arange(40, 220, 0.5)
        xs = (cx + rs * np.cos(a)).astype(int)
        ys = (cy + rs * np.sin(a)).astype(int)
        ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
        g = np.zeros_like(rs, dtype=bool)
        g[ok] = gold[ys[ok], xs[ok]]
        idx = np.where(g)[0]
        if len(idx) >= 6:                     # hay anillo dorado en este rayo
            rins.append(rs[idx[0]])
            routs.append(rs[idx[-1]])
    ri = float(np.median(rins)) if rins else float('nan')
    ro = float(np.median(routs)) if routs else float('nan')
    rc = ri * 120.0 / 107.5
    print(f'n{i}    ({cx:4d},{cy:3d})   {ri:6.1f} {ro:6.1f}   '
          f'{np.percentile(routs, 50) if routs else float("nan"):6.1f}     {rc:6.1f}  '
          f'(rayos con anillo: {len(rins)}/720)')
    cv2.circle(out, (cx, cy), int(round(rc)), (0, 0, 255), 3)
    cv2.circle(out, (cx, cy), int(round(ro)), (0, 255, 255), 2)
    cv2.drawMarker(out, (cx, cy), (0, 255, 0), cv2.MARKER_CROSS, 24, 3)

cv2.imwrite('/home/z/my-project/scripts/clown_mapa_radial.png', out)
print('guardado scripts/clown_mapa_radial.png')
