# -*- coding: utf-8 -*-
"""RONDA 45 (línea viva) · RE-ANCLADO de los sellos de los tests de
regresión a 3.6.139-SDK6 (FASE 141 — la vitrina del cielo: candado.png
del dueño en la esquina sup-izquierda del icono con su halo rojo,
constelación de palas trazada a bolígrafo en la bóveda del Arcano, la
skin de pala del peer visible en el multijugador vía HELLO `sp` y
rankings mundiales — pid+nombre firmados, perfil/resultado/logro,
worker ?rank=1 y sección en el panel).

Patrón de la casa (sella_r31…r43): versión, tamaño, golden y faseNombre
de los tests de rondas anteriores se re-anclan IN SITU a los valores
VIGENTES tras el bump.

Uso: python3 scripts/sella_r45_viva.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')

GOLDEN_VIEJO = '3e454e33b855c335e6a291764077e96078ef724cc5171067029fe03abcc6e93a'
GOLDEN_NUEVO = '42d07e64e1071243ecac63700080cf37350928d2e57a2089111e3af9e3d5edc6'

TOKENS = [
    ('3.6.138-SDK6', '3.6.139-SDK6'),
    ('V3.6.138-SDK6', 'V3.6.139-SDK6'),
    ('v3.6.138-SDK6', 'v3.6.139-SDK6'),
    ('v36138-sdk6', 'v36139-sdk6'),
    ('v36138', 'v36139'),
    ('3.6.138', '3.6.139'),
    ('vjson.fase === 140', 'vjson.fase === 141'),
    ('FASE 140', 'FASE 141'),
    ('fase 140', 'fase 141'),
    ("vjson.faseNombre === 'El suelo de destellos — duelo honesto y fluido'",
     "vjson.faseNombre === 'La vitrina del cielo — candado del dueño, constelación de palas y rankings mundiales'"),
    ('EL SUELO DE DESTELLOS — DUELO HONESTO Y FLUIDO',
     'LA VITRINA DEL CIELO — CANDADO DEL DUEÑO, CONSTELACIÓN DE PALAS Y RANKINGS MUNDIALES'),
    ('11485463', '11507255'),
    ('11.485.463', '11.504.235'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('3e454e33', '10a24300'),
]

# la r45 (test propio) no se toca
EXCLUIDOS = {'test_r45_vitrina_cielo_v36139.mjs'}


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
