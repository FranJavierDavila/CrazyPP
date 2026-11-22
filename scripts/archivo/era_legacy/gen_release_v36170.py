#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36170.py — FASE 175 · r79 · generador del release.
Re-sella scripts/release-v36169/build_zip.py → scripts/release-v36170/:
  · tokens de versión (v36169→v36170 · 3.6.169→3.6.170) + veto explícito
    de la versión anterior en el hub.
  · notas del release: FASE 174 → FASE 175 (SIEMPRE ANCLADO + los 8
    arreglos del informe del dueño en el casco).
Auxiliares se copian del kit v36169 intactos.
"""
import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(os.environ.get('CPP_RAIZ') or '/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36169'
DESTINO = RAIZ / 'scripts' / 'release-v36170'

if not (ORIGEN / 'build_zip.py').exists():
    sys.exit('ABORTA: release-v36169/build_zip.py no existe')

t = (ORIGEN / 'build_zip.py').read_text(encoding='utf-8')

ini = t.find("'Rama    : main · SDK6 (FASE 174")
fin = t.find("'  3.6.169\\n'")
if ini < 0 or fin < 0:
    sys.exit('ABORTA: bloque de notas FASE 174 no hallado')
fin += len("'  3.6.169\\n'")

NOTAS = """'Rama    : main · SDK6 (FASE 175 — SIEMPRE ANCLADO: informe del dueño\\n'
    'tras probar la V3.6.169 en el casco — «el menú aparece colocado en una\\n'
    'parte incorrecta del escenario y debe aparecer ANCLADO SIEMPRE EN EL\\n'
    'CENTRO… no se desancle NUNCA salvo que el usuario desactiva la\\n'
    'chincheta… repasa los menús»). OCHO arreglos:\\n'
    '  · ANCLA AL CENTRO DEL CUERPO: el arco nace en el yaw del RIG (ya no\\n'
    '    de la mirada — sacarlo con la cabeza girada no lo coloca de lado)\\n'
    '    y el HEAL r114 JAMÁS suelta la chincheta: re-ancla en cada estancia\\n'
    '    pero el panel vuelve a quedar FIJO (antes soltaba el pin y el menú\\n'
    '    quedaba siguiendo a la cabeza para siempre).\\n'
    '  · MULTI: ATRÁS desde «Sala en espera» vuelve al SUBNIVEL anterior\\n'
    '    (las zonas CREAR/PRIVADA con la sala VIVA en segundo plano) +\\n'
    '    tarjeta naranja «SALA {c} EN ESPERA» con GESTIONAR/CANCELAR.\\n'
    '  · RANKINGS: el MUNDIAL y MI RANKING (ELO) a BANDAS a panel completo\\n'
    '    (fuera la maquetación antigua de la tarjeta) + el HISTORIAL de\\n'
    '    campeonatos indica GRANDE cuando aún no hay registros.\\n'
    '  · ESCOGER HALL: FIX «no hace nada» — hallpick faltaba en el despacho\\n'
    '    page (id muerto); los hitos de los 6 halls ya se muestran.\\n'
    '  · CAMPEONATOS: la música gana CONTROL DESLIZANTE a banda completa\\n'
    '    (barra clicable chmus:set + −/+, arrastre en vivo).\\n'
    '  · ESCALERA DE CARRERA: superadas VERDES con ASPA grande superpuesta,\\n'
    '    liga actual con aro DORADO ANIMADO (pulso encadenado), bloqueadas\\n'
    '    con candado GRANDE y SIN rect — jamás entran (antes el clamp las\\n'
    '    llevaba a la liga actual). FIX técnico: el push doble del motor de\\n'
    '    rejilla duplicaba rects y solapaba.\\n'
    '  · PALA EN VR: el panel de ajuste queda FIJO (fuera el lerp a la\\n'
    '    cabeza de cada frame) y la salida es con B pidiendo AUTORIZACIÓN\\n'
    '    (SÍ/NO en AJUSTES › PALA) — la Y ya no sale del ajuste.\\n'
    '  · ENTRENAR: sondas de acceso — áreas y TU PROGRESO entran y pintan\\n'
    '    contenido (verificado con menuClick en el arnés).\\n'
    '  · QA: test_red_nucleo 60/0 · qa_vestibulo_r79 112/0 — NUEVAS vivas:\\n'
    '    chincheta ON por defecto y el heal no la suelta, hallpick navega,\\n'
    '    espera↔zonas con sala viva, train accede, autorización PALA, 7\\n'
    '    páginas en banda sin solapes, escalera sin ligas bloqueadas +\\n'
    '    regresión r78/r77/r76/r75/r74 íntegra, 0 pageerrors.\\n'
    '  · Ensamblado 12.273.786 B.\\n'
    '  SE CONSERVA TODO: r55-r78 íntegro (menús en profundidad, sala\\n'
    '    pública en espera, sistema de alertas, garantía de red, Hall, ELO,\\n'
    '    taller UGC, PWA).\\n'
    '  · sellada a\\n'
    '  3.6.170\\n'"""

t = t[:ini] + NOTAS + t[fin:]

for a, b in [('v36169-sdk6', 'v36170-sdk6'),
             ('V3.6.169-SDK6', 'V3.6.170-SDK6'),
             ('3.6.169-SDK6', '3.6.170-SDK6'),
             ('v36169', 'v36170'),
             ('3.6.169', '3.6.170')]:
    t = t.replace(a, b)

t = t.replace("'v36170-sdk6' not in hub",
              "'v36170-sdk6' not in hub or 'v36169-sdk6' in hub")

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

print(f'gen_release_v36170 OK → {DESTINO} (notas FASE 175 · vetos: {t.count("36169")})')
