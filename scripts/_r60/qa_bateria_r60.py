#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_bateria_r60.py — batería VERDE completa r60 (FASE 154).
Ejecuta en serie las capas verdes de r59 + las dirigidas r112/r113/r118/r119
que ejercitan DIRECTAMENTE CONFIG_DIFICULTAD. Guarda log y resumen."""
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
LOG = RAIZ / 'scripts' / '_r60' / 'bateria_r60.log'

CAPAS = [
    # (comando, timeout_s)
    ('node scripts/test_fisica.mjs', 180),
    ('node scripts/test_fisica_c05.mjs', 180),
    ('python3 scripts/qa_r54_poderes_agotados.py', 240),
    ('node scripts/test_r21_bolas_v36117.mjs', 240),
    ('node scripts/test_r24_spin_cabana_v36119.mjs', 240),
    ('node scripts/test_r26b_sorpresa_v36122.mjs', 240),
    ('node scripts/test_r30_fenix_salones_v36126.mjs', 240),
    ('node scripts/test_r31_higiene_v36127.mjs', 240),
    ('node scripts/test_r32_salones_v36128.mjs', 240),
    ('node scripts/test_r33_poderes_v36129.mjs', 240),
    ('node scripts/test_r34_fixes_v36130.mjs', 240),
    ('node scripts/test_r35_prisma_v36131.mjs', 240),
    ('node scripts/test_r36_red_v36132.mjs', 240),
    ('node scripts/test_r37_red_v36133.mjs', 240),
    ('node scripts/test_r38_rascacielos_v36134.mjs', 240),
    ('node scripts/test_r39_arcano_v36135.mjs', 240),
    ('node scripts/test_r40_arcano_v36136.mjs', 240),
    ('node scripts/test_r41_arcano_holo_v36137.mjs', 240),
    ('node scripts/test_r43_destellos_red_v36138.mjs', 240),
    ('node scripts/test_r45_vitrina_cielo_v36139.mjs', 240),
    ('node scripts/test_red_nucleo.mjs', 240),
    ('python3 scripts/qa_version.py', 180),
    ('python3 scripts/qa_sup1_v366.py', 300),
    ('python3 scripts/qa_r84_v3676.py', 300),
    ('python3 scripts/qa_rendimiento.py', 300),
    ('python3 scripts/qa_r50_gatillo_oeste.py', 240),
    ('python3 scripts/qa_r46_humo_gobernador.py', 180),
    ('python3 scripts/qa_telemetria.py', 240),
    ('python3 scripts/qa_dashboard_r53.py', 240),
    ('python3 scripts/qa_dashboard_r56.py', 240),
    # r60 · dirigidas que tocan CONFIG_DIFICULTAD
    ('python3 scripts/qa_r112_v36102.py', 240),
    ('python3 scripts/qa_r113_v36103.py', 240),
    ('python3 scripts/qa_r118_dirigida.py', 240),
    ('python3 scripts/qa_r119_dirigida.py', 240),
]

def main() -> None:
    filtro = sys.argv[1] if len(sys.argv) > 1 else 'todo'
    capas = [c for c in CAPAS
             if (filtro == 'node' and c[0].startswith('node'))
             or (filtro == 'py' and c[0].startswith('python3'))
             or filtro == 'todo']
    log = open(LOG, 'a', encoding='utf-8')
    log.write(f'\n=== TANDA {filtro} ({len(capas)} capas) ===\n')
    log.flush()
    ok, fallos = [], []
    for cmd, tmo in capas:
        t0 = time.time()
        try:
            r = subprocess.run(cmd, shell=True, cwd=RAIZ, capture_output=True,
                               text=True, timeout=tmo)
            dt = time.time() - t0
            cola = (r.stdout or '').strip().splitlines()[-3:]
            log.write(f'$ {cmd}\n' + '\n'.join(cola) + f'\n[rc={r.returncode} {dt:.0f}s]\n\n')
            log.flush()
            linea = f'{"OK " if r.returncode == 0 else "FAL"} {dt:4.0f}s  {cmd}'
            print(linea, flush=True)
            (ok if r.returncode == 0 else fallos).append(cmd)
        except subprocess.TimeoutExpired:
            print(f'TMO {tmo:4d}s  {cmd}', flush=True)
            fallos.append(cmd + ' (timeout)')
            log.write(f'$ {cmd}\n[TIMEOUT {tmo}s]\n\n')
            log.flush()
    log.write(f'\nRESUMEN: {len(ok)} OK · {len(fallos)} FALLOS\n')
    for f in fallos:
        log.write(f'  FALLO: {f}\n')
    log.close()
    print(f'RESUMEN: {len(ok)} OK · {len(fallos)} FALLOS (log: {LOG})', flush=True)
    sys.exit(1 if fallos else 0)

if __name__ == '__main__':
    main()
