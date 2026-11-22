#!/usr/bin/env python3
"""r101 · ACTUALIZA el arnés P0 (test_fisica_p0_r87.mjs) a la fase 183:

· Las agujas que vigilaban el SISTEMA DE BRAZOS (r91-r99: cápsulas, GLB,
  IK, One Euro, dedos, crease, zona dulce…) quedan RETIRADAS — el dueño
  decidió eliminar ese sistema y las agujas vigilaban código muerto.
  Las sustituyen las invariantes r101 (rival = solo pala honesta).
· Los sellos de versión pasan a leer VERSION.json (dinámicos).
· «SIN teletransportes» se alinea al código r100/r101 real (tope de paso,
  tCruce, jamás b.pos.copy, espacio de trabajo) — la aguja exigía
  _armaFollow, que r100 sustituyó por «la MISMA curva continúa».
"""
import json, re

P = '/home/z/my-project/scripts/test_fisica_p0_r87.mjs'
V = json.load(open('/home/z/my-project/src/game/VERSION.json'))
VER = V['version']

src = open(P, encoding='utf-8').read()

def needle_span(title):
    """localiza la llamada aguja('title'…) y devuelve (ini, fin) exclusivo"""
    m = re.search(r"aguja\('" + re.escape(title), src)
    assert m, f'aguja no encontrada: {title}'
    i = m.start()
    # consume hasta el cierre balanceado de paréntesis al nivel 0
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
        elif c == "'" or c == '"':
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

def replace_needle(title, new_text):
    global src
    i, j = needle_span(title)
    src = src[:i] + new_text + src[j:]

def drop_needle(title):
    global src
    i, j = needle_span(title)
    # come también la línea en blanco siguiente si la hay
    k = j
    while k < len(src) and src[k] in ' \n':
        k += 1
        if src[k-1] == '\n':
            break
    src = src[:i] + src[k:]

# ── r91: helpers de brazo exportados → ya no existen; se vigila SU AUSENCIA
replace_needle('r91 · cadena en el cerebro (quíntico + IK + tabla por golpe exportados)',
    """  aguja('r101 · el cerebro de la cadena SIN helpers de brazo (mjQuintic/IK/OneEuro borrados)',
    !c06s.includes('mjQuintic') && !c06s.includes('solveArmIK') &&
    !c06s.includes('OneEuro') && c06s.includes('_clampPalaMesa'));""")

# ── r99: «brazo retirado (método muerto…)» → ahora el método NO existe
replace_needle('r99 · brazo retirado (método muerto en bundle, gate eliminado, pala sola)',
    """  aguja('r101 · RETIRO DEFINITIVO: ni cápsulas ni GLB ni drivers en el bundle',
    !b95.includes('updateAIArm') && !b95.includes('_cargarArmasGLB') &&
    !b95.includes('aiArmGlb') && !b95.includes('OneEuro') &&
    b95.includes('EL RIVAL ES SOLO LA PALA'));""")

# ── r91-hotfix: arañas _arm* → retiradas con el sistema
drop_needle('r91-hotfix · arañas _arm* FUERA del bloque DEPS (sobreviven al ensamblado)')
replace_needle('r91-hotfix · el BUNDLE lleva la declaración _armS y ≥8 referencias',
    """  aguja('r101 · cero arañas de brazo (_armS/_gRig) en bundle y fuentes',
    !b95.includes('_armS') && !b95.includes('_gRigP') &&
    !c12s.includes('_armS') && !c12s.includes('R99_POSE_AGARRE'));""")

# ── sellos de versión → dinámicos (VERSION.json es la única fuente)
replace_needle('versión · c00 sella 3.6.198-SDK6',
    "  aguja('versión · c00 sella ' + VER_DIN, c00s.includes(VER_DIN));")
replace_needle('r94 · versión sella 3.6.198-SDK6 en el bundle',
    "  aguja('versión · el bundle sella ' + VER_DIN, b95.includes(VER_DIN));")

# ── r92/r93/r94: arco-pala-brazo, GLB, material, rig → invariantes r101
replace_needle('r92/r99ter · el BUNDLE lleva el ARCO del golpe (carga al lado + cruce en los nudos de la curva)',
    """  aguja('r101 · el BUNDLE lleva el ARCO DEL HOMBRO (nudos a radio de brazo + histéresis de caza)',
    b95.includes('EL HOMBRO MANDA') && b95.includes('HISTÉRESIS de la caza') &&
    b95.includes('_clampPalaMesa'));""")
replace_needle('r92 · el BUNDLE lleva LA PALA ES LA CONTINUACIÓN DEL BRAZO (giro mínimo premultiply)',
    """  aguja('r101 · la pala la mueve la cadena (updateAIPaddlePose copia ch.cur y clampPaddlePose cierra)',
    b95.includes('mesh.position.copy(ch.cur)') &&
    b95.includes('clampPaddlePose(mesh.position, mesh.quaternion, false)'));""")
replace_needle('r93 · el BUNDLE lleva los brazos GLB (carga + driver rígido)',
    """  aguja('r101 · sin driver de brazos GLB (updateAIArmGlb fuera del bundle)',
    !b95.includes('updateAIArmGlb') && !b95.includes('R99_CREASE'));""")
replace_needle('r94 · el BUNDLE reconstruye el MATERIAL del GLB (textura difusa embebida + respaldo piel)',
    """  aguja('r101 · la pose del rival es SOLO la cadena (rama chain en updateAIPaddlePose)',
    b95.includes("ai.chain && ai.chain.phase") &&
    b95.includes("ch.phase === 'strike' || ch.phase === 'follow'"));""")
drop_needle('r94 · la CAPTURA del rig es RIG-LOCAL (adiós al giro hornedado del recentrado)')
drop_needle('r94 · el DRIVER convierte rig-local ⇄ mundo (quats deseadas premultiply _gRigQ)')

# ── r99: curl dinámico y «solo pala» → forma r101
replace_needle('r99 · el BUNDLE lleva el CURL DINÁMICO por pose (+Y local, relativa al bind)',
    """  aguja('r101 · el contacto ES la pala: ventana por proximidad con anticipación de frames',
    b95.includes('const cerca = this._disparo && vivo') &&
    b95.includes('anticipa'));""")
replace_needle('r99 · el rival es SOLO pala (GLB de brazos sin cargar, cápsulas ocultas)',
    """  aguja('r101 · el rival es SOLO pala: ni vr_arm.glb se pide ni cápsulas existen',
    !b95.includes("fetch('./vr_arm.glb')") && !b95.includes('this.aiArm ='));""")

# ── r99ter: SIN teletransportes → invariante real (sin _armaFollow, r100)
replace_needle('r99ter · SIN teletransportes (tope de paso · bola jamás recolocada · follow propio)',
    """  aguja('r101 · SIN teletransportes (tope de paso 13 cm · bola jamás recolocada · misma curva continúa)',
    b95.includes('if (_cadP.length() > 0.13) {') &&
    b95.includes('tCruce') && b95.includes('contactoHecho') &&
    !b95.includes('b.pos.copy(d.pos)'));""")

# ── r95/r96/r97: patrones del driver GLB → retirados
replace_needle('r95 · la zona dulce SOLO en strike (el follow ya no persigue la bola: látigo=0)',
    """  aguja('r101 · el follow-through ES la cola de la curva (frenado exp. · fin por arco o velocidad)',
    b95.includes("ch.phase = 'follow'") && b95.includes('finCurva'));""")
drop_needle('r95 · ENVOLTURA NATURAL del alcance (tan 0.96/1.25 · radio 88 % con la mano alta)')
drop_needle('r95 · EL CUERPO ES UNA PERSONA (pecho 0.42 m detrás del borde · x ±1.15 · yaw suave)')
drop_needle('r99 · EL MANGO VIVE EN LA CREASE DE LA MANO (pala anclada a los nudillos)')
drop_needle('r95 · la bola del saque descansa SOBRE la palma (mano −4,5 cm bajo la bola)')
drop_needle('r96 · la muñeca anatómica tiene perpendicular GARANTIZADA (adiós al NaN de la cruz cero)')
drop_needle('r97 · FIX BLOQUEO: la cruz hand-Z es Vector3 (JAMÁS sobre un Quaternion)')

# VER_DIN: constante al inicio del bloque de identidad
a = "/* — identidad del build ————————————————————————————————————————————————— */\n{"
assert src.count(a) == 1
src = src.replace(a,
    "/* — identidad del build ————————————————————————————————————————————————— */\n"
    "const VER_DIN = JSON.parse(readFileSync(RAIZ + 'src/game/VERSION.json', 'utf-8')).version;\n{")

open(P, 'w', encoding='utf-8').write(src)
print(f'arnés P0 actualizado (versión dinámica {VER})')
