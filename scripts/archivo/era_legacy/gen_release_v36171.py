#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36171.py — FASE 176 · r80 · generador del release.
Re-sella scripts/release-v36170/build_zip.py → scripts/release-v36171/:
  · tokens de versión (v36170→v36171 · 3.6.170→3.6.171) + veto explícito
    de la versión anterior en el hub.
  · notas del release: FASE 175 → FASE 176 (MENUS QUE RESPIRAN).
Auxiliares se copian del kit v36170 intactos.
"""
import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(os.environ.get('CPP_RAIZ') or '/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36170'
DESTINO = RAIZ / 'scripts' / 'release-v36171'

if not (ORIGEN / 'build_zip.py').exists():
    sys.exit('ABORTA: release-v36170/build_zip.py no existe')

t = (ORIGEN / 'build_zip.py').read_text(encoding='utf-8')

ini = t.find("'Rama    : main · SDK6 (FASE 175")
fin = t.find("'  3.6.170\\n'")
if ini < 0 or fin < 0:
    sys.exit('ABORTA: bloque de notas FASE 175 no hallado')
fin += len("'  3.6.170\\n'")

NOTAS = """'Rama    : main · SDK6 (FASE 176 — MENUS QUE RESPIRAN: informe del dueño\\n'
    'tras probar la V3.6.170 — «los apartados de Entrenamiento están todos\\n'
    'vacíos, no se pueden usar… el menú no debe aparecer flotando nada más\\n'
    'entrar en VR… más diseño, más bonito y moderno»). SIETE arreglos:\\n'
    '  · ENTRENAR USABLE DE VERDAD: la raíz del «todo vacío» era el bloque\\n'
    '    LEG/sinPlaca — al migrar páginas en r78, trainext/trainarea/tutask\\n'
    '    perdieron el transform LEG y sus ejercicios dibujaban en la esquina\\n'
    '    del lienzo (fuera de la panela). Vuelven al mapa: DIRECCIÓN, ALTURA,\\n'
    '    EFECTO, SAQUE y RITMO pintan SUS ejercicios dentro de la panela, con\\n'
    '    título traducido (adiós «a_dir» crudo) y el RETO DE LA SEMANA\\n'
    '    arranca su modo al primer clic.\\n'
    '  · ANCLA EN VR: firma XR del ancla + el heal re-ancla si la sesión\\n'
    '    cambia 2D↔XR + re-ancla al terminar el re-centrado de la entrada —\\n'
    '    el menú ya no aparece flotando donde lo dejó la portada.\\n'
    '  · RANKING MUNDIAL: fuera la placa legada que se pintaba DETRÁS de la\\n'
    '    tabla + medallas de PODIO (oro/plata/bronce) + filas que respiran a\\n'
    '    banda completa.\\n'
    '  · MULTIJUGADOR con aire: tarjetas de modo a BANDA COMPLETA (el\\n'
    '    subtítulo ya no se trunca) y zonas separadas — «que los botones y\\n'
    '    textos respiren».\\n'
    '  · ESCOGER HALL: filas más altas y el hito CON ENCOGIMIENTO — los\\n'
    '    textos ya no se pisan.\\n'
    '  · SALA Y ESCENA: medallones en las 5 celdas del ambiente (las claves\\n'
    '    «sala»/«mesa» no existían en el registro de iconos) + título en la\\n'
    '    concha. EL HALL SE RETIRA DE AJUSTES: su sitio natural es ESCOGER\\n'
    '    HALL en MI CASA.\\n'
    '  · VOLVER en nivel 3 → al menú ANTERIOR (Sala/Mesa/Bola ya no caen al\\n'
    '    principal por el fallback).\\n'
    '  · QA: test_red_nucleo 60/0 · qa_vestibulo_r80 121/0 — NUEVAS vivas:\\n'
    '    las áreas de ENTRENAR viven DENTRO de la panela C, el RETO DE LA\\n'
    '    SEMANA arranca su modo, MULTI a banda completa, bounds de 28 páginas\\n'
    '    con el LEG restaurado + regresión r79-r74 íntegra, 0 pageerrors.\\n'
    '  · Ensamblado verificado por capturas visuales de las 9 páginas\\n'
    '    reclamadas (render_r80).\\n'
    '  SE CONSERVA TODO: r55-r79 íntegro (ancla al centro, sala pública en\\n'
    '    espera, sistema de alertas, garantía de red, Hall, ELO, taller UGC,\\n'
    '    PWA).\\n'
    '  · sellada a\\n'
    '  3.6.171\\n'"""

t = t[:ini] + NOTAS + t[fin:]

for a, b in [('v36170-sdk6', 'v36171-sdk6'),
             ('V3.6.170-SDK6', 'V3.6.171-SDK6'),
             ('3.6.170-SDK6', '3.6.171-SDK6'),
             ('v36170', 'v36171'),
             ('3.6.170', '3.6.171')]:
    t = t.replace(a, b)

t = t.replace("'v36171-sdk6' not in hub",
              "'v36171-sdk6' not in hub or 'v36170-sdk6' in hub")

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

print(f'gen_release_v36171 OK → {DESTINO} (notas FASE 176 · vetos: {t.count("36170")})')
