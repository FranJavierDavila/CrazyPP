#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reancla_r47_tests.py — r47 · RE-ANCLA los sellos de versión de los tests
de rondas (r39-r45) al nuevo estado FASE 142 (misma convención que usó
el r46 con "QA re-anclada (r39-r45, ...)"): versión, fase, faseNombre,
golden de VERSION.json y sellos de bundle. Además corrige el sdk de la
casa (1.6.0) en src/game/VERSION.json y le pone el golden real del build.
"""
import glob
import hashlib
import json
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src' / 'game'
VIEJA, NUEVA = '3.6.139-SDK6', '3.6.140-SDK6'
VIEJO_GOLDEN = '42d07e64e1071243ecac63700080cf37350928d2e57a2089111e3af9e3d5edc6'
FASE_VIEJA, FASE_NUEVA = 141, 142
NOMBRE = ('La voz del oráculo — voz solemne del Arcano, candado siempre '
          'visible y constelación del arte nuevo')

# 1 · VERSION.json: sdk 1.6.0 + golden = sha real del game.html
vj = SRC / 'VERSION.json'
vdat = json.loads(vj.read_text(encoding='utf-8'))
sha = hashlib.sha256((RAIZ / 'public' / 'game.html').read_bytes()).hexdigest()
vdat['version'] = NUEVA
vdat['fase'] = FASE_NUEVA
vdat['faseNombre'] = NOMBRE
vdat['sdk'] = '1.6.0'
vdat['fecha'] = time.strftime('%Y-%m-%d')
vdat['golden'] = sha
vj.write_text(json.dumps(vdat, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'· VERSION.json → {NUEVA} · fase {FASE_NUEVA} · sdk 1.6.0 · golden {sha[:12]}…')

# 2 · tests: re-ancla los sellos (texto plano, convención de la casa)
cambios = [
    (VIEJA, NUEVA),
    (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
    (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
    ('La vitrina del cielo — candado del dueño, constelación de palas y rankings mundiales', NOMBRE),
    ('LA VITRINA DEL CIELO — CANDADO DEL DUEÑO, CONSTELACIÓN DE PALAS Y RANKINGS MUNDIALES',
     NOMBRE.upper()),
    ('EL ARCANO HOLOGRÁFICO', NOMBRE),
    (VIEJO_GOLDEN, sha),
]
n_fich = 0
for f in sorted(glob.glob(str(RAIZ / 'scripts' / 'test_r*.mjs'))):
    p = Path(f)
    t = p.read_text(encoding='utf-8')
    orig = t
    for viejo, nuevo in cambios:
        t = t.replace(viejo, nuevo)
    if t != orig:
        p.write_text(t, encoding='utf-8')
        n_fich += 1
        print(f'  re-anclado {p.name}')
print(f'· {n_fich} tests re-anclados')
