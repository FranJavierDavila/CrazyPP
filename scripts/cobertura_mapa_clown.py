#!/usr/bin/env python3
"""V2.138 — medición ROBUSTA de los 5 medallones del mapa clown (arte nuevo).
Método de COBERTURA ANGULAR: para cada radio r, fracción de ángulos con
píxel dorado. El anillo del medallón = banda con cobertura > 0.6 (un círculo
completo cubre todos los ángulos; el pelo/globos/camino sólo abarcan pocos).
Inmune a blobs dorados localizados (pelo naranja, globos 3/5, piedras).
Regla V2.137: r_config = r_in × (120/107,5)."""
import cv2
import numpy as np

SRC = '/home/z/my-project/upload/Mapa.png'
img = cv2.imread(SRC)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
H, W = img.shape[:2]

C0 = [(226, 253), (453, 507), (700, 256), (959, 508), (1208, 322)]

gold = ((hsv[:, :, 0] >= 15) & (hsv[:, :, 0] <= 38) &
        (hsv[:, :, 1] >= 110) & (hsv[:, :, 2] >= 120)).astype(np.uint8)

THETAS = np.linspace(0, 2 * np.pi, 720, endpoint=False)
CT, ST = np.cos(THETAS), np.sin(THETAS)

def coverage_profile(cx, cy):
    rs = np.arange(50, 210, 1.0)
    cov = []
    for r in rs:
        xs = np.clip((cx + r * CT).astype(int), 0, W - 1)
        ys = np.clip((cy + r * ST).astype(int), 0, H - 1)
        cov.append(gold[ys, xs].mean())
    return rs, np.array(cov)

def band_from(cov, rs, thr=0.45, max_gap=5):
    """Banda más larga con cobertura >= thr, tolerando huecos <= max_gap
    (el cordel del globo y los guantes cortan el anillo en pocos ángulos)."""
    m = cov >= thr
    # cierra huecos cortos
    k = 0
    while k < len(m):
        if not m[k]:
            j = k
            while j < len(m) and not m[j]:
                j += 1
            if 0 < k and j < len(m) and (j - k) <= max_gap:
                m[k:j] = True
            k = j
        else:
            k += 1
    best, cur = None, None
    for k, v in enumerate(m):
        if v and cur is None:
            cur = k
        elif not v and cur is not None:
            if best is None or (k - cur) > (best[1] - best[0]):
                best = (cur, k - 1)
            cur = None
    if cur is not None and (best is None or (len(m) - cur) > (best[1] - best[0])):
        best = (cur, len(m) - 1)
    return (rs[best[0]], rs[best[1]]) if best else (None, None)

def gold_centroid_in_band(cx, cy, r_lo, r_hi):
    ys, xs = np.where(gold > 0)
    d = np.hypot(xs - cx, ys - cy)
    m = (d >= r_lo - 6) & (d <= r_hi + 6)
    return xs[m].mean(), ys[m].mean(), m.sum()

out = img.copy()
print('nodo   centro_final        r_in   r_out  ancho   r_config')
FINAL = []
for i, (cx0, cy0) in enumerate(C0):
    cx, cy = float(cx0), float(cy0)
    for _ in range(2):                      # 2 iteraciones centro->banda->centro
        rs, cov = coverage_profile(cx, cy)
        r_lo, r_hi = band_from(cov, rs)
        gx, gy, npx = gold_centroid_in_band(cx, cy, r_lo, r_hi)
        cx, cy = round(gx, 1), round(gy, 1)
    rs, cov = coverage_profile(cx, cy)
    r_lo, r_hi = band_from(cov, rs)
    rin, rout = float(r_lo), float(r_hi)
    rcfg = rin * 120.0 / 107.5
    FINAL.append((cx, cy, rin, rout, rcfg))
    peak = cov[(rs >= rin) & (rs <= rout)].mean()
    print(f'n{i}: centro=({cx:6.1f},{cy:6.1f})  r_in={rin:6.1f}  r_out={rout:6.1f}  '
          f'ancho={rout-rin:5.1f}  r_config={rcfg:6.1f}  (cobertura media en banda: {peak:.2f})')
    cv2.circle(out, (int(cx), int(cy)), int(round(rcfg)), (0, 0, 255), 3)
    cv2.circle(out, (int(cx), int(cy)), int(round(rout)), (0, 255, 255), 2)
    cv2.drawMarker(out, (int(cx), int(cy)), (0, 255, 0), cv2.MARKER_CROSS, 24, 3)

cv2.imwrite('/home/z/my-project/scripts/clown_mapa_cobertura.png', out)
print('guardado scripts/clown_mapa_cobertura.png')
print()
print('JSON final:', [(a, b, round(c, 1), round(d, 1), round(e, 1)) for a, b, c, d, e in FINAL])
