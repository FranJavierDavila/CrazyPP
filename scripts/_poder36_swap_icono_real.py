#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 44-b · Sustituye el icono PROVISIONAL del poder EFECTO por el PNG
DEFINITIVO del dueño (SuperPala_Efecto.png, adjuntado por chat y cuantizado
a 64 colores con la misma receta del Crece):
  1) c12_pingponggame.js  — data-URI de PNG_PODER_EFECTO (comparación EXACTA
     del URI completo; lección ronda 44: los prefijos base64 dan falsos
     positivos) + comentario de cabecera.
  2) release-v3636/build_zip.py — notas de release (la línea «provisional
     de la casa» ya no es cierta).
Idempotente: si el URI REAL ya está dentro, no rehace nada."""
import base64
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
BZ = RAIZ / 'scripts' / 'release-v3636' / 'build_zip.py'
P36 = RAIZ / 'scripts' / '_poder36'

PROV = P36 / 'icono_efecto_64.png'        # provisional de la casa (a sustituir)
REAL = P36 / 'icono_efecto_real_64.png'   # definitivo del dueño (64 colores)

def uri(fich):
    return 'data:image/png;base64,' + base64.b64encode(Path(fich).read_bytes()).decode('ascii')

uri_prov, uri_real = uri(PROV), uri(REAL)
fallos = 0

# ── 1) c12: data-URI ──────────────────────────────────────────────────────
txt = C12.read_text(encoding='utf-8')
if uri_real in txt:
    print('  = c12: el icono REAL ya está embebido')
elif uri_prov in txt:
    txt = txt.replace(uri_prov, uri_real, 1)
    print(f'  ✓ c12: data-URI EFECTO sustituido → SuperPala_Efecto.png '
          f'({REAL.stat().st_size:,} B, antes {PROV.stat().st_size:,} B)')
else:
    print('  ✗ c12: ni el provisional ni el real presentes')
    fallos += 1

# ── 1b) c12: comentario de cabecera ──────────────────────────────────────
com_viejo = (" *    · PNG_PODER_EFECTO — icono del poder de giro (el dueño lo traerá;\n"
             " *      provisional de la casa hasta entonces).")
com_nuevo = (" *    · PNG_PODER_EFECTO — icono del dueño (SuperPala_Efecto.png,\n"
             " *      insignia circular: pala, bola y flechas de giro).")
if com_nuevo in txt:
    print('  = c12: comentario ya actualizado')
elif com_viejo in txt:
    txt = txt.replace(com_viejo, com_nuevo, 1)
    print('  ✓ c12: comentario de cabecera actualizado')
else:
    print('  ✗ c12: comentario del icono no localizado (revisar a mano)')
    fallos += 1

if uri_prov not in txt or com_viejo not in txt:
    C12.write_text(txt, encoding='utf-8')

# ── 2) build_zip.py: notas de release ────────────────────────────────────
bz = BZ.read_text(encoding='utf-8')
notas_viejas = ("    '  · Icono del poder EFECTO: provisional de la casa (insignia azul\\n'\n"
                "    '    con bola y flechas de giro cian, misma familia que el Crece del\\n'\n"
                "    '    dueño) — el PNG definitivo del dueño se sustituye en un minuto\\n'\n"
                "    '    cuando lo adjunte (scripts/_poder36_insertar_assets.py).\\n'")
notas_nuevas = ("    '  · Icono del poder EFECTO: el DEFINITIVO del dueño\\n'\n"
                "    '    (SuperPala_Efecto.png — insignia circular con pala, bola y\\n'\n"
                "    '    flechas de giro; cuantizado a 64 colores, embebido data-URI).\\n'")
if notas_nuevas in bz:
    print('  = build_zip: notas ya actualizadas')
elif notas_viejas in bz:
    bz = bz.replace(notas_viejas, notas_nuevas, 1)
    BZ.write_text(bz, encoding='utf-8')
    print('  ✓ build_zip: notas de release actualizadas')
else:
    print('  ✗ build_zip: bloque de notas provisional no localizado')
    fallos += 1

print('SWAP ICONO REAL:', 'OK' if not fallos else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)
