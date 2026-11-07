#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.42 · FASE 44 — RONDA 50: assets del SÚPER PORTAL corregidos.

El dueño (r50): «el icono te lo he pasado con transparencia y no lo has
recortado (todos aparecen recortados)» — el icono embebido en r49 era RGB
(alfa destruido) y sin recorte. Aquí se regenera COMO LOS DEMÁS poderes:
    1) SuperPala_Portal.png → recorte al contenido (getbbox + margen) →
       256×256 con alfa PRESERVADO → 64 colores (FASTOCTREE conserva la
       transparencia) → scripts/_poder50/icono_portal_64.png
    2) portals.png (FX del mundo pedido por el dueño: el portal que ya se
       empleó con el rival wizard) → 512×512 RGBA → 96 colores con alfa →
       scripts/_poder50/portal_fx.png
    3) Re-EMBEDE en c12: sustituye el literal de PNG_PODER_PORTAL y añade
       PNG_PORTAL_FX justo detrás (idempotente por prefijo exacto).
"""
import base64
import re
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
OUT = RAIZ / 'scripts' / '_poder50'
OUT.mkdir(parents=True, exist_ok=True)


def recortar_con_alfa(im, lado, margen=6):
    """Recorte al contenido con margen, canvas cuadrado, alfa intacto."""
    im = im.convert('RGBA')
    bb = im.getbbox()
    if bb:
        x0, y0, x1, y1 = bb
        x0 = max(0, x0 - margen)
        y0 = max(0, y0 - margen)
        x1 = min(im.width, x1 + margen)
        y1 = min(im.height, y1 + margen)
        im = im.crop((x0, y0, x1, y1))
    # canvas cuadrado transparente, contenido centrado y encajado
    lado_img = max(im.width, im.height)
    escala = (lado - 8) / lado_img
    nw, nh = max(1, round(im.width * escala)), max(1, round(im.height * escala))
    im2 = im.resize((nw, nh), Image.LANCZOS)
    lienzo = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    lienzo.paste(im2, ((lado - nw) // 2, (lado - nh) // 2), im2)
    return lienzo


fallos = []

# ── 1) ICONO del poder (recortado + alfa + 64 colores) ──────────────
ico = recortar_con_alfa(Image.open(RAIZ / 'upload/SuperPala_Portal.png'), 256)
ico_q = ico.quantize(colors=64, method=Image.FASTOCTREE)
p_ico = OUT / 'icono_portal_64.png'
ico_q.save(p_ico)
print(f'  ✓ icono_portal_64.png {p_ico.stat().st_size:,} B '
      f'modo={ico_q.mode} (alfa={ico_q.mode in ("RGBA", "PA")})')

# ── 2) FX del mundo (portals.png del dueño, 512, alfa, 96 colores) ──
fx = Image.open(RAIZ / 'upload/portals.png').convert('RGBA')
fx = fx.resize((512, 512), Image.LANCZOS)
fx_q = fx.quantize(colors=96, method=Image.FASTOCTREE)
p_fx = OUT / 'portal_fx.png'
fx_q.save(p_fx)
print(f'  ✓ portal_fx.png {p_fx.stat().st_size:,} B modo={fx_q.mode}')

# ── 3) EMBEBIDO en c12 (sustitución EXACTA del literal completo) ────
txt = C12.read_text(encoding='utf-8')

uri_ico = 'data:image/png;base64,' + base64.b64encode(p_ico.read_bytes()).decode('ascii')
uri_fx = 'data:image/png;base64,' + base64.b64encode(p_fx.read_bytes()).decode('ascii')

n_ico = len(re.findall(r"const PNG_PODER_PORTAL = '[^']+';", txt))
if n_ico == 1:
    txt = re.sub(r"const PNG_PODER_PORTAL = '[^']+';",
                 "const PNG_PODER_PORTAL = '" + uri_ico + "';", txt, count=1)
    print('  ✓ PNG_PODER_PORTAL re-embedido (recortado, con alfa)')
elif ("'" + uri_ico + "'") in txt:
    print('  = PNG_PODER_PORTAL ya insertado')
else:
    fallos.append('PNG_PODER_PORTAL: patrón no encontrado')

if 'const PNG_PORTAL_FX' not in txt:
    txt = txt.replace("const PNG_PODER_PORTAL = '" + uri_ico + "';",
                      "const PNG_PODER_PORTAL = '" + uri_ico + "';\n"
                      "// v3.6.42 · FX del MUNDO para el portal (portals.png del dueño:\n"
                      "// la misma imagen de portal del rival wizard) — anillos de ENTRADA\n"
                      "// y SALIDA en la zona de impacto y sobre la mesa rival (FASE 44).\n"
                      "const PNG_PORTAL_FX = '" + uri_fx + "';", 1)
    print('  ✓ PNG_PORTAL_FX insertado')
elif ("'" + uri_fx + "'") in txt:
    print('  = PNG_PORTAL_FX ya insertado')
else:
    fallos.append('PNG_PORTAL_FX: no insertado y patrón ausente')

C12.write_text(txt, encoding='utf-8')

if fallos:
    print('ASSETS PORTAL r50:', fallos)
    sys.exit(1)
print('ASSETS PORTAL r50: OK')
