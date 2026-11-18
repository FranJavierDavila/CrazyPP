#!/usr/bin/env python3
# Genera scripts/prod_smoke_r74.py desde prod_smoke_r73.py:
#  · versión 3.6.164 → 3.6.165 · FASE 167 → FASES 168-170 · r73 → r74
#  · fuente_commit <hash> (argumento)
#  · agujas nuevas: Escoger Hall, candado de Arcanos, Multi en zonas,
#    alerta de duelo (gate + icono + banco de voz)
import sys

SRC = '/home/z/my-project/upload/scripts/prod_smoke_r73.py'
DST = '/home/z/my-project/upload/scripts/prod_smoke_r74.py'
HASH = sys.argv[1] if len(sys.argv) > 1 else 'SINHASH'

t = open(SRC, encoding='utf-8').read()

for a, b in [('3.6.164-SDK6', '3.6.165-SDK6'),
             ('FASE 167', 'FASES 168-170'),
             ('prod_smoke_r73.py', 'prod_smoke_r74.py'),
             ('PAGES-VERSION.txt: 3.6.164', 'PAGES-VERSION.txt: 3.6.165'),
             ("'sw.js a 3.6.164'", "'sw.js a 3.6.165'"),
             ('05b0dc0ca661383bf5d4dde2b74190b63172ad48', HASH)]:
    t = t.replace(a, b)

t = t.replace(
    'prod_smoke_r73.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 167 · r73',
    'prod_smoke_r74.py — VERIFICACIÓN EN PRODUCCIÓN de las FASES 168-170 · r74')
r74_doc = """  · r74 · FASES 168-170: ESCOGER HALL en MI CASA (6 salones + candado de
    Arcanos sobre bloqueados — también campeonatos, carrera, bola, temas y
    variantes), áreas de Entrenamiento en museo, MULTIJUGADOR EN TRES
    ZONAS (crear pública/privada · partidas disponibles · sala privada,
    modalidad y visibilidad en la presencia mj/vis) y LA ALERTA DE DUELO
    (gate del anfitrión + icono 2 personas + pitidos + voz del banco).
"""
t = t.replace('  · ESTÁTICO: el game.html SERVIDO lleva EL APARTADO COMPLETO',
              r74_doc + '  · ESTÁTICO: el game.html SERVIDO lleva EL APARTADO COMPLETO')

ancla = "        ('_vestCandy(c, x0, y, w0, 200,', 'héroe JUGAR conserva caramelo'),"
nuevas = ancla + """
        ('drawMenuHallPick(rects)', 'ESCOGER HALL: página de las 6 variantes'),
        ("hall_pick_btn: '⌂ ESCOGER HALL'", 'MI CASA abre Escoger Hall'),
        ('PP_ICONS.candado(', 'candado de ARCANOS sobre bloqueados'),
        ('_multiZonas(rects)', 'MULTIJUGADOR en tres zonas'),
        ('case \\'mjvis\\':', 'crear sala PÚBLICA/PRIVADA'),
        ('case \\'mjsal\\':', 'ENTRAR en partida pública del listado'),
        ('LA ALERTA DE DUELO — quad pegado al RIG', 'alerta: icono 2 personas'),
        ('EL DUELO NO IRRUMPE', 'gate del anfitrión en startOnlineSession'),
        ('duelo_acepta:', 'banco de voz: fragmento de la alerta'),"""
assert t.count(ancla) == 1, 'ancla agujas no única'
t = t.replace(ancla, nuevas)

open(DST, 'w', encoding='utf-8').write(t)
print('prod_smoke_r74.py generado con hash', HASH)
