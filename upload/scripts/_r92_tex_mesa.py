#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r92 · textura de mesa nueva del dueño (mesa.jpg 2048×1024, 4 losas con
grietas + sangre) → assets/mesa.webp del módulo Halloween. Mismo formato y
tamaño que losa.jpg (que se CONSERVA para rollback)."""
from PIL import Image
import os

SRC = '/home/z/my-project/upload/mesa.jpg'
DST = '/home/z/my-project/public/championships/halloween/assets/mesa.webp'

im = Image.open(SRC).convert('RGB')
assert im.size == (2048, 1024), im.size
im.save(DST, 'WEBP', quality=82, method=6)
print('mesa.webp:', os.path.getsize(DST), 'bytes', im.size)
