#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36172.py — FASE 177 · r81 · generador del release.
Re-sella scripts/release-v36171/build_zip.py → scripts/release-v36172/:
  · tokens de versión (v36171→v36172 · 3.6.171→3.6.172) + veto explícito
    de la versión anterior en el hub.
  · notas del release: FASE 176 → FASE 177 (MENÚS EN ESCENA).
Auxiliares se copian del kit v36171 intactos.
"""
import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(os.environ.get('CPP_RAIZ') or '/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36171'
DESTINO = RAIZ / 'scripts' / 'release-v36172'

if not (ORIGEN / 'build_zip.py').exists():
    sys.exit('ABORTA: release-v36171/build_zip.py no existe')

t = (ORIGEN / 'build_zip.py').read_text(encoding='utf-8')

ini = t.find("'Rama    : main · SDK6 (FASE 176")
fin = t.find("'  3.6.171\\n'")
if ini < 0 or fin < 0:
    sys.exit('ABORTA: bloque de notas FASE 176 no hallado')
fin += len("'  3.6.171\\n'")

NOTAS = """'Rama    : main · SDK6 (FASE 177 — MENÚS EN ESCENA: el dueño pidió que al\\n'
    'pulsar B el menú salga FIJO, sin seguimiento de la vista, con las\\n'
    'animaciones y efectos de la competencia — el ancla fija ya vivía desde\\n'
    'la FASE 175 «SIEMPRE ANCLADO» y esta fase le da VIDA al arco:\\n'
    '  · ENTRADA EN ESCENA: el arco nace con CASCADA (panela central primero,\\n'
    '    laterales +70 ms), rebote easeOutBack y fundido — 320 ms de\\n'
    '    coreografía que acaba asentado exactamente en escala 1.\\n'
    '  · SALIDA DE ESCENA: al cerrar (B · fila CERRAR · academia) el arco\\n'
    '    encoge y se desvanece en 150 ms antes de esconderse, y se restaura\\n'
    '    (escala 1 · opacidad 1) para la próxima apertura.\\n'
    '  · PULSACIÓN VIVA: cada clic deja FLASH blanco en la fila pulsada (se\\n'
    '    hornea en el troceo _menuTexSube y decae en 170 ms con repintados a\\n'
    '    60 ms) + PULSO del arco (1→1.03→1 en 130 ms) + haptic fuerte.\\n'
    '  · FOCO VIVO: al ganar el foco una fila suena un tick (1180 Hz) y\\n'
    '    vibra el mando — la competencia navega «con vida».\\n'
    '  · HONESTIDAD PRESERVADA: el FX sólo escala panelas y opacidad — el\\n'
    '    ancla fija r69/r114 (chincheta, estancia, rig z, firma XR) queda\\n'
    '    INTACTA; la QA lo verifica EN VIVO (posición del grupo idéntica\\n'
    '    antes y después de entrada/pulso/salida).\\n'
    '  · QA: test_red_nucleo 60/0 · qa_vestibulo_r81 137/0 — NUEVAS: agujas\\n'
    '    estáticas del FX (6 aperturas EN ESCENA, 2 salidas, pulso, tick del\\n'
    '    bucle, sin visibilidad instantánea) y vivas (cascada C→L/R, asiento\\n'
    '    en escala 1, pulso 1→1.03→1, flash wired+decay, salida con ancla\\n'
    '    intacta) + regresión r80-r74 íntegra, 0 pageerrors.\\n'
    '  SE CONSERVA TODO: r55-r80 íntegro (ancla al centro, sala pública en\\n'
    '    espera, sistema de alertas, garantía de red, Hall, ELO, taller UGC,\\n'
    '    PWA).\\n'
    '  · sellada a\\n'
    '  3.6.172\\n'"""

t = t[:ini] + NOTAS + t[fin:]

for a, b in [('v36171-sdk6', 'v36172-sdk6'),
             ('V3.6.171-SDK6', 'V3.6.172-SDK6'),
             ('3.6.171-SDK6', '3.6.172-SDK6'),
             ('v36171', 'v36172'),
             ('3.6.171', '3.6.172')]:
    t = t.replace(a, b)

t = t.replace("'v36172-sdk6' not in hub",
              "'v36172-sdk6' not in hub or 'v36171-sdk6' in hub")

DESTINO.mkdir(exist_ok=True)
(DESTINO / 'build_zip.py').write_text(t, encoding='utf-8')
for f in ORIGEN.iterdir():
    if f.name == 'build_zip.py':
        continue
    d = DESTINO / f.name
    if f.is_dir():
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(f, d)
    else:
        shutil.copy2(f, d)

print(f'gen_release_v36172 OK → {DESTINO} (notas FASE 177 · vetos: {t.count("36171")})')
