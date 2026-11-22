#!/usr/bin/env python3
"""V2.138 — medición FINA de los 5 medallones del mapa clown nuevo.
Por nodo: 720 rayos desde el centro Hough -> primer tramo CONTIGUO dorado
(>=6 px) = anillo del medallón -> puntos del borde interior -> ajuste de
círculo (Kasa) -> centro y r_in precisos; r_out = fin del tramo contiguo.
Regla V2.137: r_config = r_in × (120/107,5) — el anillo de progreso abraza
el borde dorado."""
import cv2
import numpy as np

SRC = '/home/z/my-project/upload/Mapa.png'
img = cv2.imread(SRC)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
H, W = img.shape[:2]

C0 = [(226, 253), (453, 507), (700, 256), (959, 508), (1208, 322)]

gold = ((hsv[:, :, 0] >= 15) & (hsv[:, :, 0] <= 38) &
        (hsv[:, :, 1] >= 110) & (hsv[:, :, 2] >= 120)).astype(np.uint8)

def ring_points(cx, cy):
    """Devuelve puntos (x,y) del borde INTERIOR y grosor del anillo por rayo."""
    pts_in, widths = [], []
    for a in np.linspace(0, 2 * np.pi, 720, endpoint=False):
        rs = np.arange(40, 200, 0.5)
        xs = (cx + rs * np.cos(a)).astype(int)
        ys = (cy + rs * np.sin(a)).astype(int)
        ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
        g = np.zeros(len(rs), dtype=bool)
        g[ok] = gold[ys[ok], xs[ok]]
        # primer tramo contiguo >= 6 muestras (3 px)
        run, start = 0, None
        end = None
        for k in range(len(rs)):
            if g[k]:
                if start is None:
                    start = k
                run += 1
                end = k
            else:
                if start is not None and run >= 12:   # tramo válido (6 px)
                    break
                if start is not None and run < 12:
                    start, run, end = None, 0, None
        if start is not None and run >= 12:
            pts_in.append((cx + rs[start] * np.cos(a),
                           cy + rs[start] * np.sin(a)))
            widths.append(rs[end] - rs[start])
    return np.array(pts_in), np.array(widths)

def kasa(pts):
    x, y = pts[:, 0], pts[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x ** 2 + y ** 2
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = sol[0], sol[1]
    r = np.sqrt(sol[2] + cx ** 2 + cy ** 2)
    return cx, cy, r

out = img.copy()
res = []
for i, (cx, cy) in enumerate(C0):
    pts, wid = ring_points(cx, cy)
    fx, fy, rin = kasa(pts)
    # segunda pasada: recalcula con centro ajustado y filtra outliers
    pts2, wid2 = ring_points(fx, fy)
    d = np.hypot(pts2[:, 0] - fx, pts2[:, 1] - fy)
    keep = np.abs(d - np.median(d)) < 6
    fx2, fy2, rin2 = kasa(pts2[keep])
    wmed = float(np.median(wid2[keep]))
    rout = rin2 + wmed
    rcfg = rin2 * 120.0 / 107.5
    res.append((fx2, fy2, rin2, rout, wmed, rcfg, int(keep.sum())))
    print(f'n{i}: centro=({fx2:6.1f},{fy2:6.1f})  r_in={rin2:6.1f}  '
          f'ancho={wmed:5.1f}  r_out={rout:6.1f}  r_config={rcfg:6.1f}  '
          f'({keep.sum()}/{len(pts2)} rayos)')
    cv2.circle(out, (int(round(fx2)), int(round(fy2))), int(round(rcfg)), (0, 0, 255), 3)
    cv2.circle(out, (int(round(fx2)), int(round(fy2))), int(round(rout)), (0, 255, 255), 2)
    cv2.drawMarker(out, (int(round(fx2)), int(round(fy2))), (0, 255, 0), cv2.MARKER_CROSS, 24, 3)

cv2.imwrite('/home/z/my-project/scripts/clown_mapa_fino.png', out)
print('guardado scripts/clown_mapa_fino.png')
print()
print('JSON:', [(round(a, 1), round(b, 1), round(c, 1), round(d, 1), round(e, 1)) for a, b, c, d, e, _, _ in res])
