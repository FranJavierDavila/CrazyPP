#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 68 · SELLADO EN CASCADA de las capas QA a 3.6.60-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-67).
El SDK (1.5.4) y los manifests del oeste (v56), locura (v27), magia (v33)
y valle_neon (v5) NO cambian esta ronda.

Tamaños byte-exactos de los ZIPs v3660 (ronda 68):
  COMPLETO   133.101.039 · ligera 18.046.683 · CLOUDFLARE 133.087.653

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.59-SDK6', '3.6.60-SDK6'), ('v3659-sdk6', 'v3660-sdk6')]
TAMANOS = [  # tamaños byte-exactos de los ZIPs v3660 (ronda 68)
    ('133099308', '133101039'),   # COMPLETO
    ('18044952', '18046683'),     # ligera
    ('133085922', '133087653'),   # CLOUDFLARE
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('qa_poderes_iman_v3637.py', VERSIONES[:1]),
    ('qa_poderes_v3638.py', VERSIONES[:1]),
    ('qa_poderes_reset_v3639.py', VERSIONES[:1]),
    ('qa_poderes_activo_v3640.py', VERSIONES[:1]),
    ('qa_bomba_v3644.py', VERSIONES[:1]),
    ('qa_electrico_v3645.py', VERSIONES[:1]),
    ('qa_superpoderes_v3643.py', VERSIONES[:1]),
    ('qa_portal_v3642.py', VERSIONES[:1]),
    ('qa_descargas_v366.py', VERSIONES + [tuple(TAMANOS[0]), tuple(TAMANOS[1]),
                                          tuple(TAMANOS[2])]),
]

fallos = 0
for nombre, pares in PLAN:
    f = SCR / nombre
    if not f.exists():
        print(f'FALLO: {nombre} no existe')
        fallos += 1
        continue
    txt = f.read_text(encoding='utf-8')
    for viejo, nuevo in pares:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            print(f'  ✓ {nombre}: {viejo} → {nuevo} (×{n})')
        elif nuevo in txt:
            print(f'  · {nombre}: {nuevo} ya sellado')
        else:
            print(f'  ? {nombre}: ni {viejo} ni {nuevo} (¿capa sin sello?)')
    f.write_text(txt, encoding='utf-8')

print('SELLADO r68:', 'OK' if fallos == 0 else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)
