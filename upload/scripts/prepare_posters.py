#!/usr/bin/env python3
"""v2.26 · Prepara los carteles de victoria/derrota del usuario:
  - Redimensiona a 1024 px de ancho (mantiene aspecto) y guarda como JPEG
    q=82 optimizado -> poco peso para incrustar en base64.
  - Informe de dimensiones/peso para fijar el tamaño del plano 3D.
Salida: scripts/poster_win.jpg / scripts/poster_lose.jpg
"""
from PIL import Image
import os

SRC = [("/home/z/my-project/upload/victoria.png", "/home/z/my-project/scripts/poster_win.jpg"),
       ("/home/z/my-project/upload/derrota.png", "/home/z/my-project/scripts/poster_lose.jpg")]

for src, dst in SRC:
    im = Image.open(src)
    w, h = im.size
    print(f"{os.path.basename(src)}: {w}x{h}  aspecto={w/h:.4f}  {os.path.getsize(src)/1e6:.2f} MB  modo={im.mode}")
    if im.mode != "RGB":
        im = im.convert("RGB")
    nw = 1024
    nh = round(h * nw / w)
    im = im.resize((nw, nh), Image.LANCZOS)
    im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"   -> {dst}: {nw}x{nh}  aspecto={nw/nh:.4f}  {os.path.getsize(dst)/1e6:.3f} MB")
