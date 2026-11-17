#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r64_medir.py — FASE 158 · mide agujas sobre el game.html ensamblado
EN MEMORIA (método r63: ensamblado exacto de build_game.py) para clavar
los conteos del sellador sella_r64_medallas.py. No escribe nada."""
import importlib.util
import re
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SRC = RAIZ / 'src' / 'game'

def ensambla() -> bytes:
    spec = importlib.util.spec_from_file_location('bg', RAIZ / 'scripts' / 'build_game.py')
    bg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bg)
    return b''.join(
        bg.pieza_pura((SRC / n).read_bytes()) if n.startswith('core/')
        else (SRC / n).read_bytes()
        for n, _ in bg.ORDER
    )

datos = ensambla()
print(f'ensamblado en memoria: {len(datos):,} B')
gh = datos.decode('utf-8', 'replace')

EXACTAS = [
    # NUEVO r64 · CONFIG_MEDALLAS (tabla c02)
    'const CONFIG_MEDALLAS = {',
    'estrellas: { bronce: 1, plata: 2, oro: 3 },',
    'precision: { plata: 70, oro: 85 },',
    # NUEVO r64 · lector c13
    'const MDE = CONFIG_MEDALLAS.estrellas, MDP = CONFIG_MEDALLAS.precision;',
    'if (stN >= MDE.oro) return (S.acc[id] || 0) >= MDP.oro ? 3 : 2;',
    'if (stN >= MDE.plata) return (S.acc[id] || 0) >= MDP.plata ? 2 : 1;',
    'if (stN >= MDE.bronce) return 1;',
    'la escalera vive en CONFIG_MEDALLAS (c02)',
    'umbrales = DATO (CONFIG_MEDALLAS en c02)',
    # CONSERVACIÓN r63 · CONFIG_RALLY (clave: ¿cambia algún conteo?)
    'const CONFIG_RALLY = {',
    'metas: { t5a: [30, 50, 100], t5b: [20, 40, 80] },',
    'bonos: { t5a: [15, 25, 50], t5b: [15, 25, 50] },',
    'const RALLY_MILL = CONFIG_RALLY.metas;',
    'const RALLY_BONUS = CONFIG_RALLY.bonos;',
    'RALLY_MILL.t5a.includes(st.rally)',
    'const MI = RALLY_MILL[id];',
    'const MI = RALLY_MILL[active], MO = RALLY_BONUS[active];',
    'RALLY_BONUS.t5a[hi]',
    'const CONFIG_PIELES = {',
    'const SKINS = CONFIG_PIELES.pieles;',
    'const CONFIG_TORNEOS = {',
    'const CONFIG_LOGROS = {',
    'const CONFIG_DIFICULTAD = {',
    'const ARCANO_CFG = {',
    'const CONFIG_MENU = {',
    'const CONFIG_AUDIO = {',
    'const stN = S.stars[id] || 0;',
]

REGEX = [
    r'CONFIG_MEDALLAS\.\w+', r'CONFIG_MEDALLAS\.estrellas\b', r'CONFIG_MEDALLAS\.precision\b',
    r'MDE\.\w+', r'MDP\.\w+', r'stN >= MDE\.\w+', r'>= MDP\.\w+',
    # r63 (re-medir: el comentario c13 nuevo añade CONFIG_RALLY.metas)
    r'CONFIG_RALLY\.\w+', r'CONFIG_RALLY\.metas\b', r'CONFIG_RALLY\.bonos\b',
    r'RALLY_MILL\.\w+', r'RALLY_BONUS\.\w+', r'RALLY_MILL\[\w+\]', r'RALLY_BONUS\[\w+\]',
    r'CONFIG_PIELES\.\w+', r'CONFIG_TORNEOS\.\w+', r'CONFIG_LOGROS\.\w+',
    r'CONFIG_DIFICULTAD\.\w+', r'CONFIG_MENU\.salir', r'CONFIG_AUDIO\.buses\.\w+',
]

print('== EXACTAS ==')
for a in EXACTAS:
    print(f'  x{gh.count(a)}  {a[:90]}')
print('== REGEX ==')
for p in REGEX:
    print(f'  x{len(re.findall(p, gh))}  RE {p}')
print(f'VERSION vieja presente: {gh.count("const VERSION = \x273.6.154-SDK6\x27")} (pre-sellado, esperado 1)')
