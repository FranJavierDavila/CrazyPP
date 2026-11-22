#!/usr/bin/env python3
"""r101 (V3.6.60) · RETIRO DEFINITIVO DE LOS BRAZOS del rival.

Borra del bundle el sistema de brazos que quedó MUERTO (r99 lo ocultó, r100
lo mantuvo sin llamar): cápsulas r91, vr_arm.glb r93, drivers r92-r99, IK,
filtros One Euro, poses de dedos y scratch. El rival es SOLO la pala.

Cada corte usa anclas únicas y ASERCIÓN de recuento — si algo no encaja,
el script aborta sin escribir.
"""
import re, sys

PATH = '/home/z/my-project/public/game.html'
src = open(PATH, encoding='utf-8').read()
orig_len = len(src)
cuts = []

def cut(name, start_anchor, end_anchor, replacement, include_end=True):
    """Corta [start_anchor .. end_anchor (incluido por defecto)) y pona replacement."""
    global src
    i = src.find(start_anchor)
    assert i >= 0, f'ANCLA INICIO NO ENCONTRADA: {name}'
    assert src.find(start_anchor, i + 1) == -1, f'ANCLA INICIO AMBIGUA: {name}'
    j = src.find(end_anchor, i)
    assert j >= 0, f'ANCLA FIN NO ENCONTRADA: {name}'
    j_end = j + len(end_anchor) if include_end else j
    cuts.append((name, i, j_end))
    src = src[:i] + replacement + src[j_end:]

# ── 1 · bloque de creación (cápsulas r91 + comentarios r93/r99 + carga GLB) ──
cut(
    'creacion_capsulas_r91',
    '    {\n      const _am = new THREE.MeshStandardMaterial({ color: 0x2b2e34, roughness: 0.55, metalness: 0.18 });',
    '    // this._cargarArmasGLB();\n',
    '    // r101 · RETIRO DEFINITIVO DE LOS BRAZOS: las cápsulas r91, el GLB\n'
    '    // r93 y TODOS sus drivers (IK, One Euro, dedos) están BORRADOS del\n'
    '    // bundle — el rival es SOLO la pala y su golpe nace SIEMPRE de ella.\n',
)

# ── 2 · métodos: updateAIArm (r91) + _cargarArmasGLB (r93) + updateAIArmGlb ──
cut(
    'metodos_brazo_capsulas_glb',
    '  /** r91 · BRAZO VISIBLE del rival: articulaciones hombro→codo→muñeca',
    '  updateAIPaddlePose(mesh, ai, who, dt) {',
    '  /* r101 · EL RIVAL ES SOLO LA PALA (decisión del dueño tras r100: el\n'
    '   * movimiento de brazos degradó el juego — pala congelada, golpes desde\n'
    '   * puntos invisibles, tiros fuera, la pala atravesando la mesa). Todo\n'
    '   * el sistema r91-r99 de brazos (cápsulas, GLB, IK, One Euro, dedos)\n'
    '   * está borrado; la pala se mueve SOLO con la cadena cinemática r91/\n'
    '   * r99ter-r101: curva continua hombro→mano→contacto→prolongación→\n'
    '   * recuperación, contacto honesto y espacio de trabajo sin mesa. */\n',
    include_end=False,
)

# ── 3 · rascadores y clases del brazo (mjQuintic, IK, zona dulce, One Euro) ──
cut(
    'helpers_brazo_modulo',
    '/* r91 · quíntico de Hermite con velocidades en los extremos (v0=v1=0 ⇒',
    'const _oeqA = new THREE.Quaternion();\n',
    '',
)

# ── 4 · scratch del brazo (arañas r91-r99, poses de dedos, tope angular) ──
cut(
    'scratch_brazos',
    '/* r91 · arañas del brazo visible del rival (cero allocs por frame). FUERA',
    'const _gRigP = new THREE.Vector3();\n',
    '',
)

# ── 5 · guardas de visibilidad en el bucle de render ──
cut(
    'guardas_visibilidad_render',
    '      if (this.aiArmGlb && this.aiArmGlb.root.visible) this.aiArmGlb.root.visible = false;\n'
    '      if (this.aiArm && this.aiArm.visible) this.aiArm.visible = false;\n',
    '      if (this.aiArmGlb && this.aiArmGlb.root.visible) this.aiArmGlb.root.visible = false;\n'
    '      if (this.aiArm && this.aiArm.visible) this.aiArm.visible = false;\n',
    '      // r101 · brazos retirados del bundle: nada que apagar aquí.\n',
)

# ── 6 · campo `glb` del informe freeze_report (telemetría del brazo GLB) ──
cut(
    'qa_campo_glb',
    '        glb: !!(G && G.aiArmGlb && G.aiArmGlb.listo),\n',
    '        glb: !!(G && G.aiArmGlb && G.aiArmGlb.listo),\n',
    '',
)

open(PATH, 'w', encoding='utf-8').write(src)
print(f'OK · {len(cuts)} cortes:')
for name, i, j in cuts:
    print(f'  - {name}: bytes {i}..{j} ({j - i} B)')
print(f'Tamaño: {orig_len} → {len(src)} B ({orig_len - len(src)} B menos)')
