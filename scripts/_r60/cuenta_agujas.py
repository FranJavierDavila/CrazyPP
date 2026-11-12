#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cuenta_agujas.py — contadores EXACTOS de las agujas r60 sobre el ensamblado."""
import importlib.util
import re
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SRC = RAIZ / 'src' / 'game'

spec = importlib.util.spec_from_file_location('bg', RAIZ / 'scripts' / 'build_game.py')
bg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bg)
datos = b''.join(
    bg.pieza_pura((SRC / n).read_bytes()) if n.startswith('core/')
    else (SRC / n).read_bytes()
    for n, _ in bg.ORDER
)
txt = datos.decode('utf-8', 'replace')
print(f'ensamblado: {len(datos):,} B')

EXACTAS = [
    'const CONFIG_DIFICULTAD = {',
    'const AI_PRESETS = CONFIG_DIFICULTAD.presets;',
    'const SERVE_ASSIST_TIERS = CONFIG_DIFICULTAD.saque;   // r60: dato',
    'const ELO_CPU = CONFIG_DIFICULTAD.elo.cpu;   // r60: dato',
    'presets: {',
    'saque: {',
    'escala: {',
    'elo: {',
    'adaptativo: { pasoSube: 0.055, pasoBaja: 0.05, topeDif: 6 },',
    'supervivencia: { porRallye: 0.08, techo: 2.1 },',
    'esfuerzo: {',
    'baseFrac: 0.25,',
    'cpu: { easy: 900, medium: 1050, hard: 1200 },',
    'kModo: { ia: 24, carrera: 20, p2p: 32 },',
    'const E = CONFIG_DIFICULTAD.escala;   // r60: topes y exponentes como datos',
    'const M = CONFIG_DIFICULTAD.elo;   // r60: bandas, jitter y paso como datos',
    'const EF = CONFIG_DIFICULTAD.esfuerzo;   // r60: la fórmula del fallo vive en datos',
    'elo: CONFIG_DIFICULTAD.elo.inicial,   // r60: dato (fábrica del número)',
    'const AD = CONFIG_DIFICULTAD.adaptativo;   // r60: el paso vive en datos',
    'const SV = CONFIG_DIFICULTAD.supervivencia;   // r60: la rampa vive en datos',
    'const ES = CONFIG_DIFICULTAD.escala;   // r60: rango legal de la tabla',
    'this.hitCooldown = EF.cooldownS;   // r60: cadencia de la tabla',
    'this.data.elo = Math.max(M.piso, miElo + delta);   // r60: piso de la tabla',
]
for a in EXACTAS:
    print(f'  x{txt.count(a)}  {a[:70]}')

RES = [
    r'CONFIG_DIFICULTAD\.\w+',
    r'CONFIG_DIFICULTAD\.elo\.\w+',
    r'CONFIG_DIFICULTAD\.escala\.\w+',
    r'CONFIG_DIFICULTAD\.esfuerzo\.\w+',
    r'CONFIG_DIFICULTAD\.presets\b',
    r'CONFIG_DIFICULTAD\.saque\b',
    r'CONFIG_DIFICULTAD\.elo\b',
    r'CONFIG_DIFICULTAD\.elo\.cpu\b',
    r'CONFIG_DIFICULTAD\.adaptativo\b',
    r'CONFIG_DIFICULTAD\.supervivencia\b',
    # conservación r59 (audio) — deben seguir intactas
    r'CONFIG_AUDIO\.buses\.\w+',
    r'CONFIG_AUDIO\.sfx\.\w+',
]
for p in RES:
    print(f'  RE x{len(re.findall(p, txt))}  {p}')
