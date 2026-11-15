#!/usr/bin/env python3
# Genera scripts/prod_smoke_r73.py desde prod_smoke_r72.py:
#  · versión 3.6.163 → 3.6.164 · FASE 166 → 167 · r72 → r73
#  · fuente_commit <hash> (argumento)
#  · agujas nuevas de la FASE 167 (placa de museo + aro teñido)
import sys

SRC = '/home/z/my-project/upload/scripts/prod_smoke_r72.py'
DST = '/home/z/my-project/upload/scripts/prod_smoke_r73.py'
HASH = sys.argv[1] if len(sys.argv) > 1 else 'SINHASH'

t = open(SRC, encoding='utf-8').read()

for a, b in [('3.6.163-SDK6', '3.6.164-SDK6'),
             ('FASE 166', 'FASE 167'),
             ('prod_smoke_r72.py', 'prod_smoke_r73.py'),
             ("'sw.js a 3.6.163'", "'sw.js a 3.6.164'"),
             ('PAGES-VERSION.txt: 3.6.163', 'PAGES-VERSION.txt: 3.6.164'),
             ('2d5bc8302e50f5be1ea23e1ad3745fa01fc130f2', HASH)]:
    t = t.replace(a, b)

# docstring r73
t = t.replace('prod_smoke_r72.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 166 · r72',
              'prod_smoke_r73.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 167 · r73')
r73_doc = """  · r73 · EL NIVEL 3, PLACA A PLACA: las tarjetas de TODAS las rejillas
    del nivel 3 + filas de rivales + tarjetas de Sala visten PLACA DE
    MUSEO (base oscura + overlay sutil + marco de latón) y el color de
    categoría sobrevive como ARO del medallón (_aroTinte); Vestíbulo,
    prompts y héroes de acción conservan su caramelo.
"""
t = t.replace('  · ESTÁTICO: el game.html SERVIDO lleva EL APARTADO COMPLETO',
              r73_doc + '  · ESTÁTICO: el game.html SERVIDO lleva EL APARTADO COMPLETO')

# agujas nuevas (tras la aguja de MI RANKING ELO oro)
ancla = "        ('ELO en ORO (placa de RÉCORD del museo', 'MI RANKING: ELO en oro'),"
nuevas = ancla + """
        ('LA PLACA DE MUSEO — mismo lenguaje que el botón', 'placa de museo (_vestPlaca73)'),
        ('_vestMedallion(c, cx, cy, r, nombre, aro)', 'medallón con aro teñido (_aroTinte)'),
        ('la tarjeta de rejilla viste PLACA DE MUSEO', 'rejillas del nivel 3 en placa'),
        ('placa de museo por RIVAL', 'filas de rivales en placa'),
        ('placa de museo en _modeCard', 'tarjetas de SALA en placa'),
        ('_vestCandy(c, x0, y, w0, 200,', 'héroe JUGAR conserva caramelo'),"""
assert t.count(ancla) == 1, 'ancla agujas no única'
t = t.replace(ancla, nuevas)

open(DST, 'w', encoding='utf-8').write(t)
print('prod_smoke_r73.py generado con hash', HASH)
