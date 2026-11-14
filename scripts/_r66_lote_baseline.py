#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r66_lote_baseline.py — DEMOSTRACIÓN DE ROJOS HEREDADOS (método r64):
corre el lote de capas caídas contra el game.html de la BASELINE r65
(git HEAD a86d747) y compara con los números r66 del qa_todo. Si los
números coinciden, el rojo es HEREDADO (cero regresión r66)."""
import subprocess
import sys

CAPAS = [
    'qa_poderes_v3638.py',        # AG 62/4
    'qa_poderes_reset_v3639.py',  # AH 33/4
    'qa_poderes_activo_v3640.py', # AI (13 s, sin conteos)
    'qa_portal_v3642.py',         # AK 87/2
    'qa_superpoderes_v3643.py',   # AL 55/3
    'qa_bomba_v3644.py',          # AM 77/1
    'qa_electrico_v3645.py',      # AN 59/1
    'qa_clon_voz_v3650.py',       # AS 67/2
    'qa_r61_v3653.py',            # AV 32/3
    'qa_r62_v3654.py',            # AW 39/7
    'qa_hall_salon_v3628.py',     # W 37/6
    'qa_partido_sala_v3629.py',   # X
    'qa_r71_v3663.py',            # BF 40/38
    'qa_r72_v3664.py',            # BG 67/7
    'qa_r78_v3670.py',            # BM 21/18
    'qa_r79_v3671.py',            # BN 55/4
    'qa_r80_v3672.py',            # BO 78/3
    'qa_r82_v3674.py',            # BR 47/1
    'qa_r83_v3675.py',            # BS 123/3
]

for cap in CAPAS:
    try:
        r = subprocess.run(
            [sys.executable, 'scripts/' + cap],
            capture_output=True, text=True, timeout=240, cwd='/home/z/my-project/upload')
        out = (r.stdout or '') + (r.stderr or '')
        lineas = [l for l in out.splitlines() if 'RESULTADO' in l]
        res = lineas[-1] if lineas else (out.strip().splitlines()[-1]
                                         if out.strip() else '(sin salida)')
        print(f'{cap:32s} r65-baseline: {res}')
    except subprocess.TimeoutExpired:
        print(f'{cap:32s} r65-baseline: TIMEOUT >240 s')
