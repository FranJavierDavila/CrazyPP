#!/usr/bin/env python3
"""r87 (fase 183) · PORTA a las FUENTES src/game/core/ los arreglos de la
pala del rival (contacto honesto, frontera real de la red, espacio de
trabajo, retiro definitivo de los brazos).

El bloque c06 se aplicó en la primera ejecución; esta pasada lo VERIFICA y
aplica SOLO el bloque c12 (los dos fallaron por el ancla fin==inicio).
Cada corte con ancla única + aserción; aborta sin escribir si algo no encaja.
"""

C06 = '/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js'
C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'

def load(p):
    return open(p, encoding='utf-8').read()

def save(p, s):
    open(p, 'w', encoding='utf-8').write(s)

def cut(src, name, a, b, repl, include_end=True):
    i = src.find(a)
    assert i >= 0, f'{name}: ancla INICIO no encontrada'
    assert src.find(a, i + 1) == -1, f'{name}: ancla INICIO ambigua'
    j = src.find(b, i)
    assert j >= 0, f'{name}: ancla FIN no encontrada'
    j_end = j + len(b) if include_end else j
    return src[:i] + repl + src[j_end:]

def swap(src, name, a, b):
    n = src.count(a)
    assert n == 1, f'{name}: {n} apariciones (esperaba 1)'
    return src.replace(a, b)

# ══════════════ c06 · verificación del portado ya aplicado ══════════════
s = load(C06)
for marca in ('_clampPalaMesa', 'VIGÍA DEL DISPARO DIFERIDO, HONESTO',
              'const C_RED = DIMS.tableCenterZ;', 'this._palaVis = this.pos.clone();',
              '0.095', 'la bola MUERTA JAMÁS se devuelve', 'afinidad > 0.45'):
    assert marca in s, f'c06: falta la marca {marca!r} (portado incompleto)'
assert 'mjQuintic' not in s and 'OneEuro' not in s, 'c06: quedan helpers de brazo'
assert 'if (this.sign < 0) cz = Math.min(cz, -0.06);' not in s, 'c06: frontera vieja'
assert 'lerp(tan, 0.35)' not in s, 'c06: sesgo tangencial viejo'
print(f'c06 VERIFICADO · {len(s)} B')

# ════════════════════════════════ c12 ════════════════════════════════
s = load(C12)

# 1 · creación de cápsulas r91 + comentarios r93/r99 + carga GLB comentada
s = cut(s, 'c12.creacion_capsulas',
    '    {\n      const _am = new THREE.MeshStandardMaterial({ color: 0x2b2e34, roughness: 0.55, metalness: 0.18 });',
    '    // this._cargarArmasGLB();\n',
    '    // r101 · RETIRO DEFINITIVO DE LOS BRAZOS: las cápsulas r91, el GLB\n'
    '    // r93 y TODOS sus drivers (IK, One Euro, dedos) están BORRADOS del\n'
    '    // bundle — el rival es SOLO la pala y su golpe nace SIEMPRE de ella.\n')

# 2 · métodos del brazo: updateAIArm + _cargarArmasGLB + updateAIArmGlb
s = cut(s, 'c12.metodos_brazo',
    '  /** r91 · BRAZO VISIBLE del rival: articulaciones hombro→codo→muñeca',
    '  updateAIPaddlePose(mesh, ai, who, dt) {',
    '  /* r101 · EL RIVAL ES SOLO LA PALA (decisión del dueño tras r100: el\n'
    '   * movimiento de brazos degradó el juego — pala congelada, golpes desde\n'
    '   * puntos invisibles, tiros fuera, la pala atravesando la mesa). Todo\n'
    '   * el sistema r91-r99 de brazos (cápsulas, GLB, IK, One Euro, dedos)\n'
    '   * está borrado; la pala se mueve SOLO con la cadena cinemática r91/\n'
    '   * r99ter-r101: curva continua hombro→mano→contacto→prolongación→\n'
    '   * recuperación, contacto honesto y espacio de trabajo sin mesa. */\n',
    include_end=False)

# 3 · guardas de visibilidad en el bucle (inicio == fin: corte de 2 líneas)
s = cut(s, 'c12.guardas',
    '      if (this.aiArmGlb && this.aiArmGlb.root.visible) this.aiArmGlb.root.visible = false;\n'
    '      if (this.aiArm && this.aiArm.visible) this.aiArm.visible = false;\n',
    '      if (this.aiArm && this.aiArm.visible) this.aiArm.visible = false;\n',
    '      // r101 · brazos retirados del bundle: nada que apagar aquí.\n')

# 4 · campo glb del freeze_report (una línea: inicio == fin)
s = cut(s, 'c12.glb_field',
    '        glb: !!(G && G.aiArmGlb && G.aiArmGlb.listo),\n',
    'G.aiArmGlb && G.aiArmGlb.listo),\n',
    '')

# 5 · scratch de brazos (arañas r91-r99 + poses de dedos + tope angular + rig)
s = cut(s, 'c12.scratch',
    '/* r91 · arañas del brazo visible del rival (cero allocs por frame). FUERA',
    'const _gRigP = new THREE.Vector3();\n', '')

assert 'aiArmGlb' not in s.replace('glb: !!(G && G.aiArmGlb', ''), 'c12: queda aiArmGlb'
assert 'updateAIArm' not in s, 'c12: queda updateAIArm'
assert '_cargarArmasGLB' not in s, 'c12: queda _cargarArmasGLB'
assert 'R99_POSE_AGARRE' not in s, 'c12: queda scratch R99'

save(C12, s)
print(f'c12 PORTADO · {len(s)} B')
print('PORTADO COMPLETO')
