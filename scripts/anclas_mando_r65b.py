#!/usr/bin/env python3
"""r65c · Clustering denso de la CABEZA del mando (Z>0.015) para anclas
exactas: stick (lo más alto), 4 botones (elevados sobre la placa),
gatillo (protrusión trasera-superior) y grip (lateral del mango)."""
import numpy as np

P = np.load("/tmp/mando_P.npy")

head = P[P[:, 2] > 0.015]
print(f"puntos en cabeza: {len(head)}")

# rejilla de clusters (bin 7 mm) sobre X-Y
BIN = 0.007
cx = np.floor(head[:, 0] / BIN).astype(int)
cy = np.floor(head[:, 1] / BIN).astype(int)
from collections import defaultdict
g = defaultdict(list)
for i in range(len(head)):
    g[(cx[i], cy[i])].append(i)

cands = []
for k, idx in g.items():
    if len(idx) < 25:
        continue
    pts = head[idx]
    c = pts.mean(0)
    cands.append((len(idx), c, pts[:, 1].max() - pts[:, 1].min(), pts[:, 0].max() - pts[:, 0].min()))
cands.sort(key=lambda t: -t[0])
print("clusters (n, centro X/Y/Z, dy, dx):")
for n, c, dy, dx in cands[:18]:
    print(f"  n={n:4d}  ({c[0]:+.4f}, {c[1]:+.4f}, {c[2]:+.4f})  dy={dy:.3f} dx={dx:.3f}")

# top absoluto: vértices más altos (Y grande) = cabeza del stick
alto = P[P[:, 1] > np.percentile(P[:, 1], 99)]
print(f"\nY máximo: {P[:,1].max():.4f} · vértices p99+: centro {alto.mean(0).round(4)} n={len(alto)}")

# el stick sobresale: vértices con Y > Yplaca+3mm en la zona X<0.005
placa_y = np.percentile(head[:, 1], 75)
sobre = head[head[:, 1] > placa_y + 0.003]
if len(sobre):
    print(f"sobre la placa (>{placa_y+0.003:.4f}): n={len(sobre)} centro {sobre.mean(0).round(4)}")
    for xs in (-1, 1):
        m = sobre[:, 0] * xs > 0
        if m.sum() > 10:
            print(f"   lado {'+X' if xs>0 else '-X'}: n={int(m.sum())} centro {sobre[m].mean(0).round(4)}")

# gatillo: en la cabeza, lado -Y (detrás de la placa), protruyendo
atras = head[head[:, 1] < np.percentile(head[:, 1], 30)]
if len(atras):
    print(f"cabeza lado -Y: n={len(atras)} centro {atras.mean(0).round(4)} · Zmax {atras[:,2].max():.4f}")

# grip: zona lateral del mango (Z<0, X extremo)
mango = P[P[:, 2] < 0.0]
for xs in (-1, 1):
    m = mango[:, 0] * xs > np.abs(mango[:, 0]).max() * 0.55
    if m.sum() > 20:
        print(f"mango lado {'+X' if xs>0 else '-X'}: n={int(m.sum())} centro {mango[m].mean(0).round(4)}")
