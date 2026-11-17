#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analiza los PNG del parallax del artista:
- dimensiones de cada pieza
- p1: fila del horizonte (primera fila desde arriba con >50% de opacidad)
- p2/p3/p4: pie más bajo opaco (para calibrar 'feet') y aspecto
"""
import os, json
from PIL import Image

D = '/home/z/my-project/game/championships/oeste/assets/parallax'
out = {}

def analyze(path, name):
    im = Image.open(path).convert('RGBA')
    w, h = im.size
    a = im.getchannel('A')
    aw = a.resize((min(w, 300), min(h, 300)))
    px = aw.load()
    sw, sh = aw.size
    # fila con >50% de pixeles opacos (horizonte/terreno) y min-y opaco por columna
    row_opaque = []
    col_first = []
    for y in range(sh):
        cnt = 0
        for x in range(sw):
            if px[x, y] > 100: cnt += 1
        row_opaque.append(cnt / sw)
    for x in range(sw):
        fy = None
        for y in range(sh):
            if px[x, y] > 100: fy = y; break
        col_first.append(fy if fy is not None else sh)
    # horizonte = primera fila (desde arriba) donde >50% opaco
    horizon = None
    for y, f in enumerate(row_opaque):
        if f > 0.5: horizon = y; break
    top_min = min(col_first)
    bottom_max = max(col_first)
    return {
        'file': name, 'w': w, 'h': h, 'aspect': round(w / h, 3),
        'horizon_frac_desde_arriba': round(horizon / sh, 3) if horizon is not None else None,
        'top_opaco_frac': round(top_min / sh, 3),
        'bottom_opaco_frac': round(bottom_max / sh, 3),
        'opaco_frac_medio': round(sum(row_opaque) / sh, 3),
    }

for f in sorted(os.listdir(D)):
    if f.endswith('.png'):
        out[f] = analyze(os.path.join(D, f), f)

for k, v in out.items():
    print(json.dumps(v, ensure_ascii=False))

# resumen por plano
print('\n=== RESUMEN ===')
for p in ['p1', 'p2', 'p3', 'p4']:
    items = [v for k, v in out.items() if k.startswith(p + '_')]
    ws = sorted(set(v['w'] for v in items)); hs = sorted(set(v['h'] for v in items))
    print(f"{p}: n={len(items)} anchos={ws} altos={hs}")
    if p == 'p1':
        for v in items:
            print(f"   {v['file']}: horizonte al {v['horizon_frac_desde_arriba']*100:.1f}% desde arriba, top_opaco={v['top_opaco_frac']}, opaco_medio={v['opaco_frac_medio']}")
