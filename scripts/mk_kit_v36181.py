#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36181.py — r90 · clona el kit release-v36180 → release-v36181.
Tokens: v36180→v36181 · V3.6.180→V3.6.181 · staging · guard del hub heredado ·
nota FASE 186 «POSE ITTF + §12.1 DEL ESTUDIO» (cara ⟂ mesa / mango ∥ mesa con
cierre de cara sobre el eje + arnés ITTF: restitución 0,935, drag Cd 0,445,
túnel 10 000 bolas) · lecciones heredadas: guard del hub con versión NUEVA,
cabecera de nota SIN comilla final (\\n literal de cierre)."""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36180'
DESTINO = RAIZ / 'scripts' / 'release-v36181'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales
t = t.replace('release-v36180', 'release-v36181')
t = t.replace('staging-v36180', 'staging-v36181')
t = t.replace('v36180-sdk6', 'v36181-sdk6')
t = t.replace('V3.6.180-SDK6', 'V3.6.181-SDK6')
t = t.replace('3.6.180-SDK6', '3.6.181-SDK6')

# 2. nota de la ficha: FASE 185 → FASE 186 (marker-based, respeta el pie)
i = t.find('FASE 185 — MANO LIBRE SIN JÚPITER')
if i < 0:
    sys.exit('ABORTA: nota FASE 185 no encontrada')
a = t.rfind("'Rama", 0, i)
fin_marcador = 'SAQUE LIBRE) intacta —\\n'   # \n LITERAL (lección r88)
j = t.find(fin_marcador, i)
if a < 0 or j < 0:
    sys.exit('ABORTA: span de la nota no acotado')
nueva_cabecera = (
    "'Rama    : main · SDK6 (FASE 186 — POSE ITTF + §12.1 DEL ESTUDIO:\\n'\n"
    "    'cuarto informe del dueño y adopción física · «la pala del rival no\\n'\n"
    "    'suele estar con la superficie paralela a la mesa sino PERPENDICULAR\\n'\n"
    "    'con el mango PARALELO» — geometría exacta en las TRES posturas: el\\n'\n"
    "    'eje de la hoja (mango→punta) va HORIZONTAL cruzado (espera: hacia el\\n'\n"
    "    'lado de la bola · golpeo: la firma side cruza al lado contrario en\\n'\n"
    "    'el follow-through · preparación del saque) y la CARA vive en el\\n'\n"
    "    'plano vertical que mira a la red (AIM_FACE.y ×0,35 en el golpeo) —\\n'\n"
    "    'y el cierre por efecto ya no es un pitch de la base sino una\\n'\n"
    "    'ROTACIÓN DE LA CARA SOBRE EL EJE DEL MANGO (closQ con el eje\\n'\n"
    "    'signado para que la cruz mire ARRIBA: topspin baja la cara —\\n'\n"
    "    'cerrada, cortada la sube — abierta; el mango NO se mueve) · §12.1\\n'\n"
    "    'DEL ESTUDIO como arnés nuevo (test_fisica_ittf.mjs, 8 checks con la\\n'\n"
    "    'física real del motor): T1 REBOTE ITTF — caída 300 mm ⇒ apex ∈\\n'\n"
    "    '[230,260] mm: con el drag real e=0,88 daba 214 mm ⇒\\n'\n"
    "    'tableRestitution 0,935 ⇒ apex 240,7 mm; T2 VELOCIDAD TERMINAL —\\n'\n"
    "    'airDragK 0,142 (Cd 0,5, v_t 8,31) ⇒ 0,1267 (Cd 0,445, crisis de\\n'\n"
    "    'arrastre): v_t 8,799 m/s analítica y simulada; T3 TÚNEL 10 000\\n'\n"
    "    'BOLAS — golpes dirigidos con computeShotVelocityReal y efectos\\n'\n"
    "    'sembrados por stepPhysics completo: 10 000/10 000 cruzan la red y\\n'\n"
    "    'botan en campo rival · 0 NaN · vmax 9,04 ≤ 16 · 0 penetraciones bajo\\n'\n"
    "    'la losa · 0 túneles de red · QA TODO VERDE: goldens c04 12/12 + c05\\n'\n"
    "    '17/17 RE-BASELINEADOS (cambio físico intencionado del estudio) ·\\n'\n"
    "    'arnés P0 r86 21/21 · arnés r87-90 27/27 (agujas r90: pose ITTF +\\n'\n"
    "    'constantes §12.1) · red 60/60 · rallies I1-I5 con hash nuevo\\n'\n"
    "    '614004af (cambio físico documentado, 0 violaciones) · INCIDENTE\\n'\n"
    "    'SÉPTIMO del .git (rodó a ronda 35): disco íntegro, rama realineada a\\n'\n"
    "    'origin/main por plumbing sin perder nada · La FASE 185 (MANO LIBRE\\n'\n"
    "    'SIN JÚPITER + MANGO NATURAL) intacta —\\n"
)
t = t[:a] + nueva_cabecera + t[j + len(fin_marcador):]

# 3. guard del hub DESACTUALIZADO (lección r86 #1, heredada)
t = t.replace('grep -c "3.6.180"', 'grep -c "3.6.181"')
t = t.replace('menciones 3.6.180', 'menciones 3.6.181')
t = t.replace('el hub empaquetado no es el v36180',
              'el hub empaquetado no es el v36181')
bz.write_text(t, encoding='utf-8')

# 4. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36180-sdk6', 'v36181-sdk6')
          .replace('release-v36180', 'release-v36181')
          .replace('staging-v36180', 'staging-v36181')
          .replace('V3.6.180-SDK6', 'V3.6.181-SDK6')
          .replace('3.6.180-SDK6', '3.6.181-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36181 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36180 restante={s.count("v36180-sdk6")} · '
          f'v36181={s.count("v36181-sdk6")} · V3.6.180={s.count("V3.6.180-SDK6")}')
