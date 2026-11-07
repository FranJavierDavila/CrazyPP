#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 23 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.118-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los ZIPs
en las capas que los llevan clavados (lección de las rondas 10-21: cada bump
necesita su sellado o el QA TOTAL compara contra la versión vieja).

Capas y sellos (misma configuración que sella_r21):
  E · qa_sup1_v365.py    — versión (1 ×2 formas)
  F · qa_imp2_v351.py    — versión (1 ×2 formas)
  G · qa_escudo_v350.py  — versión + gateway (2 ×2 formas)
  H · qa_descargas_v365.py — versión + tag de hub + nombres/tamaños de ZIPs
  I · smoke_sdk5.py      — versión (1)
  (el tag de hub v3658-sdk6 → v36118-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.111-SDK6', '3.6.118-SDK6'), ('3.6.112-SDK6', '3.6.118-SDK6'),
             ('3.6.58-SDK6', '3.6.118-SDK6'), ('v3658-sdk6', 'v36118-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v36118 (construidos esta ronda)
    ('133096287', '146807263'),   # COMPLETO
    ('18041931', '18599995'),     # ligera
    ('133082901', '146793098'),   # CLOUDFLARE
]
# H · r23 · la capa quedó congelada en la r58: ADOPTANTES llevaba
# valle_neon (RETIRADO hace rondas) y el SDKinside del ZIP es 1.6.0
# desde la r97. Sellos de CONTENIDO (no solo de versión).
CONTENIDO_H = [
    ("ADOPTANTES = (('oeste', 56, 'v3.6.4-SDK4'), ('magia', 33, 'v3.6.4-SDK4'),\n"
     "              ('locura', 27, 'v3.6.4-SDK4'), ('valle_neon', 5, 'v3.6.5-SDK5'))",
     "ADOPTANTES = (('oeste', 56, 'v3.6.4-SDK4'), ('magia', 33, 'v3.6.4-SDK4'),\n"
     "              ('locura', 27, 'v3.6.4-SDK4'), ('estacion_orbital', 17, 'v3.6.6-SDK6'),\n"
     "              ('halloween', 3, 'v3.6.6-SDK6'))"),
    ("const SDK_VERSION = '1.5.4'", "const SDK_VERSION = '1.6.0'"),
    ('v1.4.0 (música', 'v1.6.0 (música'),
    ('v1.4.0 servido', 'v1.6.0 servido'),
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('smoke_sdk5.py', VERSIONES[1:2]),
    ('qa_descargas_v365.py', VERSIONES[2:] + TAMANOS + CONTENIDO_H),
]

fallos = 0
for nombre, regs in PLAN:
    p = SCR / nombre
    txt = p.read_text(encoding='utf-8')
    total = 0
    ya = 0
    for viejo, nuevo in regs:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            total += n
        elif nuevo in txt:
            ya += 1          # ya sellado por una pasada anterior: OK
        else:
            print(f'FALLO: {nombre}: sello {viejo!r} ×0 y {nuevo!r} ausente')
            fallos += 1
    p.write_text(txt, encoding='utf-8')
    print(f'· {nombre}: {total} sellos actualizados · {ya} ya sellados')

if fallos:
    sys.exit(f'{fallos} sellos sin casar — revisar')
print('· sellado en cascada a 3.6.118-SDK6 COMPLETO')
