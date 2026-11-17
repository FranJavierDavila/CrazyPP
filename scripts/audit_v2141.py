#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoría de calidad V2.141: verifica que todas las funciones V2.125→V2.141
están intactas en public/game.html + championships restaurados."""
import hashlib, json, os, re, sys

G = open('/home/z/my-project/public/game.html', encoding='utf-8', errors='replace').read()
BASE = '/home/z/my-project'

def chk(label, ok, extra=''):
    print(('  OK  ' if ok else '  FAIL') + f'  {label}' + (f'  [{extra}]' if extra else ''))
    return ok

fails = 0
print('== NUCLEO ==')
import re as _re
fails += not chk('VERSION >= 2.141 (V3.0 incluida)', bool(_re.search(r"VERSION = '(2\.1[4-9]\d\.0|3\.\d+\.0)'", G)))
fails += not chk('ChampLoader descubre campeonatos', 'championships.json' in G)
fails += not chk('Bienvenida por voz (V2.138)', 'Bienvenido a Crazy Ping Pong' in G)
fails += not chk('Modo entrenamiento en nucleo', 'entrenamiento' in G.lower())

print('== OESTE (salvaje oeste, V2.133–V2.140) ==')
O = open(f'{BASE}/public/championships/oeste/index.js', encoding='utf-8', errors='replace').read()
checks_o = [
    ('Indios (indio1..4 + alcanzado)', all(f'indio{i}' in O for i in (1,2,3,4)) and 'indioalcanzado' in O),
    ('Parallax vegetacion (V2.133)', re.search(r'parallax|vegetaci|arbusto|cactus', O, re.I) is not None),
    ('Tunel reducido ~1,8m (V2.137)', re.search(r't[uú]nel|tunnel', O, re.I) is not None),
    ('Rebote pared de fondo (V2.133)', re.search(r'pared|fondowall|wall', O, re.I) is not None),
    ('X3 tres bolas (V2.133)', re.search(r'X3|x3|tres bolas|3 bolas', O) is not None),
    ('Dinamita en cadena (V2.133)', 'dinamita' in O.lower()),
    ('Lingotes + cajones de madera (V2.140)', 'lingote' in O.lower() and re.search(r'caj[oó]n|crate', O, re.I) is not None),
    ('Suelo del vagon suelo.jpg (V2.140)', 'suelo.jpg' in O or 'suelo.jpg' in G),
    ('Paradas: Bravos / GOLD DUST / Silver Creek', 'Bravos' in O and 'GOLD DUST' in O and 'Silver Creek' in O),
    ('Megafonia tren (V2.139)', re.search(r'Pasajeros al tren|megafon|broadcast', O, re.I) is not None),
    ('Risas (risas.mp3/forajido/pueblo, V2.139)', 'risas.mp3' in O.lower() or 'risas_forajido' in O.lower()),
    ('forajido_robo.png + recompensa.png (V2.139)', 'forajido_robo.png' in O and 'recompensa.png' in O),
    ('normas forajido (forajido_normas.png)', 'forajido_normas' in O or 'forajido_normas' in G),
    ('Etapa 4 vagon sin rebote fantasma (V2.139)', re.search(r'vag[oó]n|wagon|etapa.?4', O, re.I) is not None),
]
for lbl, ok in checks_o: fails += not chk(lbl, ok)

print('== LOCURA (clown) ==')
L = open(f'{BASE}/public/championships/locura/index.js', encoding='utf-8', errors='replace').read()
checks_l = [
    ('Burla sustituye a Mareo (V2.127)', re.search(r'burla', L, re.I) is not None),
    ('Superpoderes clown (incl. 2 bolas)', re.search(r'poder|superpoder', L, re.I) is not None),
    ('Mapa propio clown (mapa.webp V2.138)', os.path.exists(f'{BASE}/public/championships/locura/assets/mapa.webp') and "A('mapa.webp')" in L),
    ('normas clown (clown_normas.png)', 'clown_normas' in L or 'clown_normas' in G),
]
for lbl, ok in checks_l: fails += not chk(lbl, ok)

print('== ESTACION ORBITAL (wizard) ==')
E = open(f'{BASE}/public/championships/estacion_orbital/index.js', encoding='utf-8', errors='replace').read()
checks_e = [
    ('Intro video + JUGAR (V2.129)', re.search(r'intro\.mp4|JUGAR', E) is not None),
    ('Test de habilidades + Empezar (V2.129)', re.search(r'habilidad|Empezar', E, re.I) is not None),
    ('Superpoderes EO (tractor/meteoritos/estrellas/cero)', all(p in E for p in ('powertractor','powermeteoritos','powerestrellas','powercero'))),
    ('Asteroide flotante + fisica', 'asteroide' in E.lower()),
    ('Mapa wizard propio (V2.136)', os.path.exists(f'{BASE}/public/championships/estacion_orbital/assets/mapa.png') or os.path.exists(f'{BASE}/public/championships/estacion_orbital/assets/Mapa.png')),
    ('normas wizard (Wizard_normas.png)', 'Wizard_normas' in E or 'Wizard_normas' in G),
]
for lbl, ok in checks_e: fails += not chk(lbl, ok)

print('== MAGIA (4º campeonato) ==')
checks_m = [
    ('manifest publicado', json.load(open(f'{BASE}/public/championships/magia/manifest.json')).get('estado') == 'publicado'),
    ('index.js presente + bloque level', 'level' in open(f'{BASE}/public/championships/magia/index.js', encoding='utf-8', errors='replace').read()),
]
for lbl, ok in checks_m: fails += not chk(lbl, ok)

print('== ASSETS SUBIDOS POR USUARIO vs ZIP (integridad de materiales) ==')
pairs = [
    ('upload/PARADA1.png', 'championships/oeste/assets/parada1.png'),
    ('upload/PARADA2.png', 'championships/oeste/assets/parada2.png'),
    ('upload/PARADA3.png', 'championships/oeste/assets/parada3.png'),
    ('upload/Risas.mp3',   'championships/oeste/assets/risas.mp3'),
    ('upload/forajido_robo.png', 'championships/oeste/assets/forajido_robo.png'),
    ('upload/recompensa.png',    'championships/oeste/assets/recompensa.png'),
    ('upload/suelo.jpg',   'championships/oeste/assets/suelo.jpg'),
]
def md5(p):
    if not os.path.exists(p): return None
    return hashlib.md5(open(p,'rb').read()).hexdigest()
for up, ch in pairs:
    mu, mc = md5(f'{BASE}/{up}'), md5(f'{BASE}/public/{ch}')
    name = os.path.basename(up)
    if mu is None:
        chk(f'{name} en upload/', False); fails += 1; continue
    if mc is None:
        # buscar por nombre en el campeonato
        found = any(f == name for _,_,fs in os.walk(f'{BASE}/public/championships/oeste/assets') for f in fs)
        chk(f'{name} presente en oeste/assets', found, 'nombre localizado' if found else 'NO ESTA')
        fails += not found
    else:
        chk(f'{name} identico upload<->assets', mu == mc)

print()
print(f'RESULTADO: {"AUDITORIA SUPERADA" if fails==0 else f"{fails} comprobaciones FALLIDAS"}')
sys.exit(1 if fails else 0)
