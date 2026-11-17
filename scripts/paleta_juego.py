# -*- coding: utf-8 -*-
"""Extrae la paleta dominante del arte original del juego y una vista previa."""
from PIL import Image
import os, collections

SRC = "/home/z/my-project/upload/Menú de ping-pong futurista sin texto.png"
OUT = "/tmp/render/menu_ref.jpg"

im = Image.open(SRC).convert("RGB")
print("Tamano:", im.size)

# Paleta dominante: cuantizar a 32 colores por canal -> 8 niveles? mejor adaptive palette
q = im.resize((im.width // 4, im.height // 4)).quantize(colors=16, method=Image.Quantize.MEDIANCUT)
pal = q.getpalette()
counts = collections.Counter(q.getdata())
total = sum(counts.values())
print("\n-- Paleta dominante (16 colores) --")
for idx, n in counts.most_common(16):
    r, g, b = pal[idx * 3:idx * 3 + 3]
    print("#%02X%02X%02X  %5.1f%%" % (r, g, b, 100.0 * n / total))

# Zonas: mitad superior (cielo/ambiente), centro (panel), franja inferior
w, h = im.size
zones = {"arriba": im.crop((0, 0, w, h // 3)), "centro": im.crop((0, h // 3, w, 2 * h // 3)),
         "abajo": im.crop((0, 2 * h // 3, w, h))}
print("\n-- Por zonas --")
for zn, z in zones.items():
    zq = z.resize((z.width // 4, z.height // 4)).quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    zp = zq.getpalette()
    zc = collections.Counter(zq.getdata())
    zt = sum(zc.values())
    top = "  ".join("#%02X%02X%02X(%.0f%%)" % (zp[i * 3], zp[i * 3 + 1], zp[i * 3 + 2], 100.0 * n / zt)
                    for i, n in zc.most_common(6))
    print("%-7s %s" % (zn, top))

# Vista previa para inspeccion visual
prev = im.copy()
prev.thumbnail((880, 880))
prev.save(OUT, quality=80)
print("\nPreview:", OUT, prev.size)
