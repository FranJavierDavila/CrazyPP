#!/usr/bin/env python3
"""r65b · Anclas UV→3D: para cada región circular de la textura (stick,
botones A/X/B/Y, gatillo, grip) calcula el centroide 3D de los vértices
cuyo UV cae dentro. Y refina la zona interior de la pizarra."""
import numpy as np

P = np.load("/tmp/mando_P.npy")     # ya transformado (metros, cabeza +Z)
UV = np.load("/tmp/mando_UV.npy")   # u,v con origen arriba-izquierda (glTF)
TX = 1024.0

# regiones candidatas (px en la textura 1024): (cx, cy, r)
REG = {
    "stick_cap_grande":  (950, 330, 62),
    "stick_cap_bajo":    (795, 845, 62),
    "btn_A_top":         (985, 60, 26),
    "btn_B_top":         (935, 55, 26),
    "btn_X_top":         (880, 85, 26),
    "btn_Y_top":         (915, 135, 26),
    "btn_letra_X":       (905, 450, 22),
    "btn_letra_B":       (900, 695, 22),
    "btn_letra_Y":       (905, 830, 22),
    "placa_hueco_1":     (575, 320, 24),
    "placa_hueco_2":     (555, 372, 20),
    "placa_hueco_3":     (598, 373, 20),
    "placa_hueco_4":     (620, 352, 20),
    "gatillo_sup":       (545, 600, 55),
    "gatillo_inf":       (545, 690, 55),
    "cuerpo_shell1":     (215, 105, 90),
    "cuerpo_shell2":     (205, 395, 90),
    "piezas_peq_1":      (325, 210, 26),
    "piezas_peq_2":      (380, 205, 26),
}

for k, (cx, cy, r) in REG.items():
    u, v = cx / TX, cy / TX
    d = np.sqrt(((UV[:, 0] - u) * TX) ** 2 + ((UV[:, 1] - v) * TX) ** 2)
    m = d <= r
    if m.sum() < 8:
        print(f"{k:18s} → sin vértices ({int(m.sum())})")
        continue
    c = P[m].mean(0)
    print(f"{k:18s} → {int(m.sum()):4d} pts · centro3D ({c[0]:+.4f}, {c[1]:+.4f}, {c[2]:+.4f}) · r3D {P[m].std(0).round(4)}")

print()
print("HEAD (Z máximo 6%):")
hm = P[:, 2] > np.percentile(P[:, 2], 94)
print(f"  centro ({P[hm].mean(0)[0]:+.4f}, {P[hm].mean(0)[1]:+.4f}, {P[hm].mean(0)[2]:+.4f})")

# --- pizarra: interior real (el marco es la única zona oscura ancha) ---
from PIL import Image
im = Image.open("/home/z/my-project/upload/_r65/Pizarra.png").convert("RGBA")
a = np.array(im)
oscuro = (a[:, :, 3] > 200) & (a[:, :, :3].mean(axis=2) < 60)
# fila central: tramos oscuros continuos
fila = oscuro[400, :]
runs, ini = [], None
for x, v in enumerate(fila):
    if v and ini is None: ini = x
    if not v and ini is not None:
        runs.append((ini, x - 1)); ini = None
if ini is not None: runs.append((ini, len(fila) - 1))
runs = [r for r in runs if r[1] - r[0] > 50]
print("PIZARRA fila y=400 tramos oscuros anchos:", runs)
col = oscuro[:, 700]
runs2, ini = [], None
for y, v in enumerate(col):
    if v and ini is None: ini = y
    if not v and ini is not None:
        runs2.append((ini, y - 1)); ini = None
if ini is not None: runs2.append((ini, len(col) - 1))
runs2 = [r for r in runs2 if r[1] - r[0] > 50]
print("PIZARRA col x=700 tramos oscuros anchos:", runs2)
