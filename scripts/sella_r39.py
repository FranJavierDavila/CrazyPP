#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 39 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.31-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-38:
cada bump necesita su sellado o el QA TOTAL compara contra la versión
vieja). El SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
ronda — sus pines se conservan tal cual.

Capas y sellos (configuración REAL heredada de las rondas 13-38):
  E · qa_sup1_v365.py    — versión (+ SDK v1.5.4 y oeste v56 intactos)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños (los ZIPs
                             cambian por el game.html del menú v3631)
  I · smoke_sdk5.py      — versión (+ sdkVer 1.5.4 intacto)
  (el tag de hub v3630-sdk6 → v3631-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.30-SDK6', '3.6.31-SDK6'), ('v3630-sdk6', 'v3631-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3631 (construidos esta ronda)
    ('130783840', '130786087'),   # COMPLETO
    ('15752576', '15754823'),     # ligera
    ('130770454', '130772701'),   # CLOUDFLARE
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('smoke_sdk5.py', VERSIONES[:1]),
    ('qa_descargas_v365.py', VERSIONES + TAMANOS),
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
            ya += 1
    p.write_text(txt, encoding='utf-8')
    estado = 'YA' if (total == 0 and ya) else 'OK'
    print(f'  · {nombre}: {total} agujas ({ya} ya selladas) {estado}')
    if total == 0 and ya == 0:
        print(f'    FALLO: ni aguja ni sello nuevo en {nombre}')
        fallos += 1

print('SELLA_R39', 'OK' if fallos == 0 else f'CON {fallos} FALLOS')
sys.exit(1 if fallos else 0)
