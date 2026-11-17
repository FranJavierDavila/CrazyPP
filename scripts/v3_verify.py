#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3.0 · verificación estructural del módulo PRO TRAINING instalado."""
import io, sys, re

P = '/home/z/my-project/public/game.html'
h = io.open(P, encoding='utf-8').read()
fails = 0

def chk(lbl, ok, extra=''):
    global fails
    print(('  OK  ' if ok else '  FAIL') + '  ' + lbl + (('  [' + extra + ']') if extra else ''))
    fails += not ok

m = re.search(r'<script type="module">(.*?)</script>', h, re.S)
M = m.group(1) if m else ''

print('== VERSION Y NÚCLEO ==')
chk('VERSION 3.0.1', "VERSION = '3.0.1'" in h)
chk('guardia updateCalibration', 'if (this.trainV3) return;' in h)
chk('gancho tick en bucle', 'window.__PP_TRAIN.tick(dt)' in h)
chk('traingo abre hub', "this.menuPage = 'train';" in h)
chk('páginas train/trainarea', "menuPage === 'trainarea'" in h)
chk('case trv3', "case 'trv3':" in h)
chk('window.__PP_TRAIN exportado', 'window.__PP_TRAIN = PP_TRAIN;' in h)
chk('sin regressión V2.141 (paradas)', 'Silver Creek' in h and 'GOLD DUST' in h)

print('== MÓDULO PRO TRAINING ==')
for k, lbl in [
    ('ppxr_train_v1', 'storage propio'),
    ('const MODES', 'registro de modos'),
    ('t1a:', 'modo MESA MARCADA'), ('t1b:', 'modo LÍNEA'),
    ('t2a:', 'modo PASE BAJO'), ('t2b:', 'modo GLOBO'),
    ('t3a:', 'modo CORTADO'), ('t3b:', 'modo TOPSPIN'),
    ('t4a:', 'modo DOBLE BOTE'), ('t4b:', 'modo SAQUE LARGO'),
    ('t5a:', 'modo METRÓNOMO'),
    ('computeShotVelocityReal', 'máquina con efecto real'),
    ('RIBBON_Y', 'cinta 17 cm sobre red'),
    ('APEX_Y', 'aro de altura'),
    ('drawHub', 'menú artístico hub'),
    ('drawArea', 'páginas de área'),
    ('applySkin', 'skins de pala'),
    ('pulseFaceIcons', 'iconos de efecto en caras'),
    ("'arcoiris'", 'skin arcoíris'),
    ('try {', 'tick blindado con try/catch'),
]:
    chk(lbl, k in M)

print('== AISLAMIENTO ==')
chk('grupo de escena propio', "grp.name = 'ppTrainGrp'" in M)
chk('usa enterCalib (sin tocar árbitro)', 'game.enterCalib()' in M or 'g.enterCalib()' in M)
chk('no modifica DIMS', 'DIMS.tableTopY =' not in M and 'DIMS.magnus =' not in M)
M_nc = re.sub(r'//.*', '', M)   # sin comentarios de línea (no hay URLs en el módulo)
chk('no escribe rules.state', not re.search(r'rules\.state\s*=[^=]', M_nc))
chk('física intacta (magnus 0.0035)', 'magnus: 0.0035' in h)
chk('colisión pala intacta (spinImpulse)', 'spinImpulse: 10' in h)

print()
print('RESULTADO: ' + ('VERIFICACIÓN SUPERADA' if fails == 0 else f'{fails} FALLOS'))
sys.exit(1 if fails else 0)
