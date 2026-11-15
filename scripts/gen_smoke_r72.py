#!/usr/bin/env python3
# Genera scripts/prod_smoke_r72.py desde prod_smoke_r71.py:
#  · versión 3.6.162 → 3.6.163 · FASE 165 → 166 · r71 → r72
#  · fuente_commit <hash> (argumento)
#  · agujas nuevas del nivel 3 + guarda anti-bucle
import sys

SRC = '/home/z/my-project/upload/scripts/prod_smoke_r71.py'
DST = '/home/z/my-project/upload/scripts/prod_smoke_r72.py'
HASH = sys.argv[1] if len(sys.argv) > 1 else 'SINHASH'

t = open(SRC, encoding='utf-8').read()

for a, b in [('3.6.162-SDK6', '3.6.163-SDK6'),
             ('FASE 165', 'FASE 166'),
             ('prod_smoke_r71.py', 'prod_smoke_r72.py'),
             ('prod_smoke_r70.py', 'prod_smoke_r72.py'),
             ('c5adb39', HASH)]:
    t = t.replace(a, b)

# docstring r72
t = t.replace('prod_smoke_r71.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 166 · r71',
              'prod_smoke_r72.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 166 · r72')
t = t.replace('(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.163-SDK6):',
              '(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.163-SDK6):')
r72_doc = """  · r72 · EL NIVEL 3 MAQUETADO: guarda anti-bucle _rankiniFresh (fin del
    congelamiento al pulsar Ranking Mundial), Ko-fi fuera de Ajustes,
    btn compartido en latón+degradado, RANKING/MI RANKING en oro de
    museo, 6 categorías de AJUSTES re-espaciadas.
"""
t = t.replace('  · ESTÁTICO: el game.html SERVIDO lleva EL APARTADO COMPLETO',
              r72_doc + '  · ESTÁTICO: el game.html SERVIDO lleva EL APARTADO COMPLETO')

# agujas nuevas (tras la aguja del landing de Ranking)
ancla = "        ('drawMenuRankIni', 'landing de Ranking'),"
nuevas = ancla + """
        ('if (!this._rankiniFresh) {', 'guarda anti-bucle del landing de Ranking'),
        ('this._rankiniFresh = false;', 're-arma del reloj único al entrar'),
        ('MARCO DE LATÓN en reposo (antes gris neutro)', 'btn nivel 3: latón+degradado'),
        ('FUERA «Apoyar el proyecto (Ko-fi)» de AJUSTES', 'kofi fuera de la rejilla'),
        ('cabecera de columnas — r72', 'RANKING: cabeceras en oro'),
        ('ELO en ORO (placa de RÉCORD del museo', 'MI RANKING: ELO en oro'),"""
assert t.count(ancla) == 1, 'ancla agujas no única'
t = t.replace(ancla, nuevas)

open(DST, 'w', encoding='utf-8').write(t)
print('prod_smoke_r72.py generado con hash', HASH)
