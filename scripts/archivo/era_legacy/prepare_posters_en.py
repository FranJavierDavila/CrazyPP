#!/usr/bin/env python3
"""v2.27 · Normaliza los carteles ingleses (1344x768) al formato del juego:
1024x683 (3:2) JPEG q82 — recorte centrado tipo 'cover' para no deformar."""
from PIL import Image
import os

JOBS = [
    ("/home/z/my-project/scripts/poster_win_en_raw.png", "/home/z/my-project/scripts/poster_win_en.jpg"),
    ("/home/z/my-project/scripts/poster_lose_en_raw.png", "/home/z/my-project/scripts/poster_lose_en.jpg"),
]
TARGET_W, TARGET_H = 1024, 683

for src, dst in JOBS:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    s = max(TARGET_W / w, TARGET_H / h)          # cover
    nw, nh = round(w * s), round(h * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - TARGET_W) // 2
    y0 = (nh - TARGET_H) // 2
    im = im.crop((x0, y0, x0 + TARGET_W, y0 + TARGET_H))
    im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"{dst}: {TARGET_W}x{TARGET_H}  {os.path.getsize(dst)/1024:.0f} KB")
