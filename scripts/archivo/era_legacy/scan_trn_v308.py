#!/usr/bin/env python3
"""Escaneo rápido de game.html: localizar bloques clave del entrenamiento."""
import re, sys

PATH = '/home/z/my-project/public/game.html'
with open(PATH, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f'total lines: {len(lines)}')

pats = {
    'OBJETIVO_text':   r"fillText\('OBJETIVO'",
    'targetZone':      r"targetZone|zonaObjetivo|zona_objetivo|ZONA OBJETIVO",
    't4a':             r"\bt4a\b",
    't1b':             r"\bt1b\b",
    'SAQUE':           r"SAQUE VIVO|serveTee|serve_tee|teeBall|ballTee",
    'serve':           r"serveState|servePhase|tossBall|doToss",
    'rival':           r"rivalShot|rivalAI|rival_target|chooseRival|rivalPlan",
    'trainDef':        r"TRAIN_TESTS|trainTests|TESTS\s*=|PRUEBAS",
    'zonaCheck':       r"inTargetZone|checkZone|zoneHit|dentroZona",
    'gamify':          r"trainGamify|combo|COMBO",
}

for name, pat in pats.items():
    rx = re.compile(pat)
    hits = [i + 1 for i, ln in enumerate(lines) if rx.search(ln)]
    print(f'{name:14s} n={len(hits):4d}  lines: {hits[:40]}')

# long lines warning
lens = [(len(ln), i + 1) for i, ln in enumerate(lines)]
lens.sort(reverse=True)
print('longest lines:', [(l, n) for l, n in lens[:5]])
