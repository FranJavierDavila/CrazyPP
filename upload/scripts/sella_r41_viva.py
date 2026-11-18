# -*- coding: utf-8 -*-
"""RONDA 41 (línea viva) · RE-ANCLADO de los sellos de los tests de
regresión r24-r40 a 3.6.137-SDK6 (FASE 139 — el Arcano holográfico:
motas de polvo circulares, suelo negro con matriz fina y rellenos que
nacen/mueren al azar, flechas intercambiadas, iconos a sangre completa,
panel HOLOGRÁFICO con voz propia, ojos del búho azul↔rojo y candado
flotante con halo rojo pulsante).

Patrón de la casa (sella_r31…r40): versión, tamaño, golden y faseNombre
de los tests de rondas anteriores se re-anclan IN SITU a los valores
VIGENTES tras el bump. Además, las agujas de la r40 que describen el
suelo QUE MUTA (8 m, 9×9) se re-anclan al suelo NEGRO de la r41 (48×48
de 1,5 m con rellenos que nacen y mueren al azar — petición del dueño).

Uso: python3 scripts/sella_r41_viva.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')

GOLDEN_VIEJO = '3e54690b9abd48818ec97ff3fc87262988fde2c0cacb74e7a201aafbaf2ff997'
GOLDEN_NUEVO = '543863157c0d8ab3348d7b78edc52a0d262c7ebd132c42db1933e878b1325227'

TOKENS = [
    ('3.6.136-SDK6', '3.6.137-SDK6'),
    ('V3.6.136-SDK6', 'V3.6.137-SDK6'),
    ('v3.6.136-SDK6', 'v3.6.137-SDK6'),
    ('v36136-sdk6', 'v36137-sdk6'),
    ('v36136', 'v36137'),
    ('3.6.136', '3.6.137'),
    ('vjson.fase === 138', 'vjson.fase === 139'),
    ('FASE 138', 'FASE 139'),
    ('fase 138', 'fase 139'),
    ("vjson.faseNombre === 'El Arcano a la vista — revisión del dueño'",
     "vjson.faseNombre === 'El Arcano holográfico — pulido del dueño'"),
    ('11461098', '11473088'),
    ('11472617', '11473088'),
    ('11.461.098', '11.473.088'),
    ('11.472.617', '11.473.088'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('ff28d036130a84c54e29a47d2855c8817e328c3097578cf849aa9c899529393f', GOLDEN_NUEVO),
    ('3e54690b', '54386315'),
    ('ff28d036', '54386315'),
    # r41 · EL SUELO cambia de mecanismo (petición del dueño): la r40
    # MUTABA los tonos de 9×9 losetas de 8 m; la r41 pinta un suelo NEGRO
    # con matriz FIJA de 48×48 losetas de 1,5 m y RELLENOS que nacen y
    # mueren completamente al azar. Las agujas de la r40 se re-anclan.
    ("""chk(c08.includes('const N = 9;') && c08.includes('new THREE.PlaneGeometry(N * 8, N * 8)'),
  'c08: plano 72×72 m con losetas GRANDES de 8 m (9×9)');""",
     """chk(c08.includes('const N = 48;') && c08.includes('const LADO = N * 1.5;') &&
    c08.includes('new THREE.PlaneGeometry(LADO, LADO)'),
  're-anclada r41: plano 72 m con losetas PEQUEÑAS de 1,5 m (48×48)');"""),
    ("""chk(c08.includes("x.strokeStyle = 'rgba(140,205,255,' + (0.10 * f).toFixed(3) + ')'"),
  'c08: retícula fina y sutil en los cantos, desvanecida por la viñeta');""",
     """chk(c08.includes("gx.strokeStyle = 'rgba(130,195,252,' + (0.16 * f).toFixed(3) + ')'"),
  're-anclada r41: matriz fina SIEMPRE visible, desvanecida al horizonte');"""),
    ("""chk(c08.includes('S.acc += dt;') && c08.includes('if (S.acc >= 0.35) {'),
  'c08: las losetas MUTAN cada 0,35 s');""",
     """chk(c08.includes('S.lit.length < 140') && c08.includes('Math.random() < 0.55'),
  're-anclada r41: losetas que NACEN al azar (tope ~140 vivas)');"""),
    ("""chk(c08.includes('for (let k = 0; k < 7; k++) {'),
  'c08: 7 losetas eligen tono nuevo por tick (aleatorio)');""",
     """chk(c08.includes('i: (Math.random() * S.N) | 0, j: (Math.random() * S.N) | 0,'),
  're-anclada r41: posición de nacimiento TOTALMENTE aleatoria');"""),
    ("""chk(c08.includes('c[0] += Math.round((t[0] - c[0]) * 0.35);'),
  'c08: mordisco suave hacia el tono objetivo (transición viva)');""",
     """chk(c08.includes('const aV = q.t < q.tIn ? q.t / q.tIn'),
  're-anclada r41: envolvente nace→aguanta→muere (apagado aleatorio)');"""),
    ("""chk(c08.includes('S.pinta(i % S.N, (i / S.N) | 0);') &&
    c08.includes('if (cambio) S.tex.needsUpdate = true;'),
  'c08: re-pintado SÓLO de las losetas que cambian');""",
     """chk(c08.includes('fx.clearRect(0, 0, 512, 512);') &&
    c08.includes('S.tex.needsUpdate = true;'),
  're-anclada r41: capa de rellenos viva repintada (matriz estática)');"""),
    ("""chk(c08.includes('new THREE.MeshBasicMaterial({ map: tex, fog: false }));'),
  'c08: el suelo sin niebla (la Fog(9,18) de la cancha jamás lo toca)');""",
     """chk(c08.includes("new THREE.MeshBasicMaterial({ map: bTex, fog: false }));"),
  're-anclada r41: la BASE NEGRA del suelo sin niebla');"""),
]

TESTS = [
    'scripts/test_r24_spin_cabana_v36119.mjs',
    'scripts/test_r26b_sorpresa_v36122.mjs',
    'scripts/test_r27_foro3d_v36123.mjs',
    'scripts/test_r30_fenix_salones_v36126.mjs',
    'scripts/test_r31_higiene_v36127.mjs',
    'scripts/test_r32_salones_v36128.mjs',
    'scripts/test_r33_poderes_v36129.mjs',
    'scripts/test_r34_fixes_v36130.mjs',
    'scripts/test_r35_prisma_v36131.mjs',
    'scripts/test_r36_red_v36132.mjs',
    'scripts/test_r37_red_v36133.mjs',
    'scripts/test_r38_rascacielos_v36134.mjs',
    'scripts/test_r39_arcano_v36135.mjs',
    'scripts/test_r40_arcano_v36136.mjs',
]


def main():
    for rel in TESTS:
        p = RAIZ / rel
        txt = p.read_text(encoding='utf-8')
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            print('· re-anclado', rel)
        else:
            print('· sin cambios', rel)
    print('OK sella_r41_viva')


if __name__ == '__main__':
    main()
