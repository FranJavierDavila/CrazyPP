#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · QA TOTAL (un comando, toda la cadena).
Encadena TODAS las capas de verificación del proyecto, de la más rápida a la
más lenta, y saca el marcador global. Descubre los QA de la versión actual
por nombre (qa_sup1_vNNN.py → el más alto), así que no hay que tocarlo en
cada release.

Capas:
  A. qa_version.py        — cadena de versión única (23 checks)
  B. test_fisica.mjs      — determinismo de la física (11 escenarios)
  C. qa_manifiestos.py    — schema + assets de los 5 campeonatos (29)
  D. qa_rendimiento.py    — presupuesto (tamaños/física/boot, 14)
  E. qa_sup1_vNNN.py      — el juego EN VIVO con el orbital cargado (~150)
  F. qa_imp2_vNNN.py      — reactor de impulso (~66)
  G. qa_escudo_vNNN.py    — escudo de pala (~54)
  H. qa_descargas_vNNN.py — hub + 4 ZIPs byte-exactos (~208)
  I. smoke_sdkN.py        — SDK + 5 módulos en cadena
  J. qa_telemetria.py     — telemetría anónima: catálogo, receptor, E2E (41)
  K. qa_hub_hints.py      — (POST-DEPLOY, --produccion) hints del hub en
                            producción contra el estado real del dueño (11)
  L. qa_champion_listo.py — (POST-DEPLOY, --produccion) estado champion de
                            los 5 campeonatos en producción (13)

Uso:
  python3 scripts/qa_todo.py                # TODO (A-J, pre-deploy)
  python3 scripts/qa_todo.py --rapido       # solo A-D (sin Playwright pesado)
  python3 scripts/qa_todo.py --produccion   # A-J + K/L contra PRODUCCIÓN
                                            # (tras el deploy: K/L exigen
                                            # que pages sirva la versión
                                            # de la FUENTE DE VERDAD)
Salida: marcador global. Exit 1 si CUALQUIER capa falla."""
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'
TIMEOUT = {  # segundos por capa
    'qa_version.py': 120, 'test_fisica.mjs': 90, 'qa_manifiestos.py': 60,
    'qa_rendimiento.py': 300,
}

def ultimo(pat):
    cand = sorted(SCR.glob(pat))
    return cand[-1].name if cand else None

CAPAS = [
    ('A · versión única', 'qa_version.py'),
    ('B · física determinista', 'test_fisica.mjs'),
    ('C · manifiestos', 'qa_manifiestos.py'),
    ('D · presupuesto', 'qa_rendimiento.py'),
    ('E · juego en vivo (sup1)', ultimo('qa_sup1_v*.py')),
    ('F · reactor de impulso', 'qa_imp2_v351.py'),
    ('G · escudo de pala', 'qa_escudo_v350.py'),
    ('H · hub + ZIPs', ultimo('qa_descargas_v*.py')),
    ('I · smoke del SDK', ultimo('smoke_sdk*.py')),
    ('J · telemetría', 'qa_telemetria.py'),
    ('T · zonas entrenamiento', 'qa_train_zonas_v3619.py'),
    ('U · ayudas entrenamiento', 'qa_train_ayudas_v3621.py'),
    ('V · sonido del tren', 'qa_tren_audio_v3625.py'),
]

# Capas POST-DEPLOY (--produccion): cargan game.html de PRODUCCIÓN y exigen
# que pages sirva la versión de la FUENTE DE VERDAD (src/game/VERSION.json).
CAPAS_PRODUCCION = [
    ('K · hints del hub (prod)', 'qa_hub_hints.py'),
    ('L · champion listo (prod)', 'qa_champion_listo.py'),
]

def main():
    rapido = '--rapido' in sys.argv
    produccion = '--produccion' in sys.argv
    capas = CAPAS + (CAPAS_PRODUCCION if produccion else [])
    filas = []
    fallos_total = 0
    t_global = time.monotonic()
    for nombre, script in capas:
        if not script or not (SCR / script).exists():
            filas.append((nombre, 'AUSENTE', '-', script or '(no encontrado)'))
            fallos_total += 1
            continue
        if rapido and script.startswith('qa_sup1'):
            break
        cmd = ['node', '--no-warnings', str(SCR / script)] if script.endswith('.mjs') \
            else [sys.executable, str(SCR / script)]
        t0 = time.monotonic()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=TIMEOUT.get(script, 600))
            dur = time.monotonic() - t0
            salida = r.stdout + r.stderr
            if script.endswith('.mjs'):
                # test_fisica: 'RESULTADO: N escenarios · 0 desviaciones'
                linea = next((l for l in salida.splitlines() if l.startswith('RESULTADO')), '')
                desv = '0 desviaciones' in linea and r.returncode == 0
                estado = 'OK' if desv else 'FALLO'
                resumen = linea.replace('RESULTADO: ', '').strip()
            else:
                linea = next((l for l in salida.splitlines()
                              if 'RESULTADO' in l.upper()), '')
                limpio = linea.replace('RESULTADO:', '').replace('RESULTADO', '').strip()
                n_fallos = 0
                for trozo in limpio.replace('OK ·', '·').split('·'):
                    t = trozo.strip().lower()
                    for pref in ('fallos', 'fallo', 'desviaciones'):
                        if t.startswith(pref):
                            try:
                                n_fallos = int(t.split()[0])
                            except (ValueError, IndexError):
                                n_fallos = 9999
                estado = 'OK' if (r.returncode == 0 and n_fallos == 0) else 'FALLO'
                resumen = f'{limpio} ({dur:.0f} s)'
        except subprocess.TimeoutExpired:
            dur = time.monotonic() - t0
            estado, resumen = 'TIMEOUT', f'>{dur:.0f} s'
        if estado != 'OK':
            fallos_total += 1
        filas.append((nombre, estado, resumen, script))

    print('=' * 72)
    print('CRAZY PING PONG · QA TOTAL')
    print('=' * 72)
    for nombre, estado, resumen, script in filas:
        marca = '✓' if estado == 'OK' else ('·' if estado == 'OMITIDA' else '✗')
        print(f'  {marca} {nombre:28s} [{estado:7s}] {resumen}  ({script})')
    print('=' * 72)
    print(f'  TIEMPO TOTAL: {time.monotonic() - t_global:.0f} s · '
          f'CAPAS EN FALLO: {fallos_total}')
    sys.exit(1 if fallos_total else 0)

if __name__ == '__main__':
    main()
