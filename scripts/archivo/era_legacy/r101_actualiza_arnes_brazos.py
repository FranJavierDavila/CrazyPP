#!/usr/bin/env python3
"""r101 · ACTUALIZA arnes_brazos_r95.mjs: las agujas que vigilaban el driver
de brazos GLB (dedos, agarre, crease, envoltura, cuerpo, material, rig) se
RETIRAN — el dueño eliminó ese sistema y la pala es SOLO pala. Las agujas de
cadena (retiro, contacto honesto, sin teletransportes) se re-ancan a r101."""
import re

P = '/home/z/my-project/scripts/arnes_brazos_r95.mjs'
src = open(P, encoding='utf-8').read()

def needle_span(title):
    m = re.search(r"aguja\('" + re.escape(title), src)
    assert m, f'aguja no encontrada: {title}'
    i = m.start()
    depth = 0
    j = i
    while True:
        c = src[j]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return i, j + 1
        elif c in '\'"':
            q = c
            j += 1
            while src[j] != q:
                if src[j] == '\\':
                    j += 1
                j += 1
        elif src[j:j+2] == '//':
            j = src.find('\n', j)
        elif src[j:j+2] == '/*':
            j = src.find('*/', j) + 1
        j += 1

def drop(title):
    global src
    i, j = needle_span(title)
    k = j
    while k < len(src) and src[k] in ' \n':
        k += 1
        if src[k-1] == '\n':
            break
    src = src[:i] + src[k:]

def replace(title, new_text):
    global src
    i, j = needle_span(title)
    src = src[:i] + new_text + src[j:]

drop('bundle · r99 CURL DINÁMICO POR POSE (flexión +Y, relativa al bind)')
drop('bundle · r95 pulgarY por brazo (A −1 · B +1)')
drop('bundle · r95 ENVOLTURA NATURAL (tan 0.96 / 1.25 + radio 88 %)')
drop('bundle · r95 EL CUERPO ES UNA PERSONA (borde +0.42 · x ±1.15)')
drop('bundle · r99 EL MANGO VIVE EN LA CREASE DE LA MANO (offset medido)')
drop('bundle · r94 el material y el marco rig-local siguen íntegros')

replace('bundle · r95 la zona dulce SOLO en strike (adiós al látigo del follow)',
    """  aguja('r101 · el follow-through ES la cola de la curva (misma curva, frenado exp.)',
    b.includes("ch.phase = 'follow'") && b.includes('finCurva') &&
    b.includes('Math.exp(-dt / 0.22)'));""")

replace('r99 · el GLB de brazos NO se carga (la llamada queda comentada)',
    """  aguja('r101 · el GLB de brazos NI SE PIDE (fetch borrado del bundle)',
    !b.includes("fetch('./vr_arm.glb')") && !b.includes('_cargarArmasGLB'));""")

replace('r99 · NI GLB NI cápsulas se pintan (puerta única de ocultación)',
    """  aguja('r101 · ni aiArm ni aiArmGlb EXISTEN (cápsulas y rig borrados de la clase)',
    !b.includes('this.aiArm') && !b.includes('aiArmGlb') &&
    !b.includes('updateAIArmGlb'));""")

replace('r99ter · el contacto dispara el ACOMPAÑAMIENTO (curva propia [cur → cruce F])',
    """  aguja('r101 · el contacto dispara el ACOMPAÑAMIENTO (contactoHecho · la MISMA curva continúa)',
    b.includes('contactoHecho = true') && b.includes("ch.phase = 'follow'") &&
    b.includes('contactoHecho congela'));""")

open(P, 'w', encoding='utf-8').write(src)
print('arnés de brazos actualizado a r101')
