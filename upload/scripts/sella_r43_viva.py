# -*- coding: utf-8 -*-
"""RONDA 43 (línea viva) · RE-ANCLADO de los sellos de los tests de
regresión r30-r42 a 3.6.138-SDK6 (FASE 140 — el suelo de destellos:
la trama fina sólo existe donde un destello la dibuja, letrero
«Salir/Exit» sobre el búho, la esfera del casco remoto en el RIG,
saques sin bola invisible, convergencia del fantasma en la zona de
juicio y física en tiempo real con TX sin allocations).

Patrón de la casa (sella_r31…r41): versión, tamaño, golden y faseNombre
de los tests de rondas anteriores se re-anclan IN SITU a los valores
VIGENTES tras el bump.

Uso: python3 scripts/sella_r43_viva.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')

GOLDEN_VIEJO = '543863157c0d8ab3348d7b78edc52a0d262c7ebd132c42db1933e878b1325227'
GOLDEN_NUEVO = '3e454e33b855c335e6a291764077e96078ef724cc5171067029fe03abcc6e93a'

TOKENS = [
    ('3.6.137-SDK6', '3.6.138-SDK6'),
    ('V3.6.137-SDK6', 'V3.6.138-SDK6'),
    ('v3.6.137-SDK6', 'v3.6.138-SDK6'),
    ('v36137-sdk6', 'v36138-sdk6'),
    ('v36137', 'v36138'),
    ('3.6.137', '3.6.138'),
    ('vjson.fase === 139', 'vjson.fase === 140'),
    ('FASE 139', 'FASE 140'),
    ('fase 139', 'fase 140'),
    ("vjson.faseNombre === 'El Arcano holográfico — pulido del dueño'",
     "vjson.faseNombre === 'El suelo de destellos — duelo honesto y fluido'"),
    ('11473088', '11485463'),
    ('11472617', '11485463'),
    ('11.473.088', '11.485.463'),
    ('11.472.617', '11.485.463'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('54386315', '3e454e33'),
]

# la r43 (test propio) y los tests RETIRADOS de la batería viva no se tocan
EXCLUIDOS = {'test_r43_destellos_red_v36138.mjs'}


def main():
    tocados = 0
    for f in sorted((RAIZ / 'scripts').glob('test_r*.mjs')):
        if f.name in EXCLUIDOS:
            continue
        txt = f.read_text(encoding='utf-8')
        nuevo = txt
        for viejo, nuevo_s in TOKENS:
            nuevo = nuevo.replace(viejo, nuevo_s)
        if nuevo != txt:
            f.write_text(nuevo, encoding='utf-8')
            print('· re-anclado:', f.name)
            tocados += 1
    print(f'tests re-anclados: {tocados}')


if __name__ == '__main__':
    main()
