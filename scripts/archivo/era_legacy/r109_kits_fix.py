#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r109-b2 · KITS DE RELEASE — cierre de la limpieza: conserva SOLO los kits
de versiones con tag de fecha ≥ 2026-11-14 (regla del dueño: 1 semana) más el
kit nuevo release-v36207. Fuera los de la vieja numeración (v304-v364, octubre)
y cualquier otro sin tag reciente. Los ficheros trackeados van con git rm; los
restos sin seguimiento, fuera del disco."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
os.chdir(RAIZ)
CUTOFF = '2026-11-14'

# versiones (N de v3.6.N) con tag ≥ corte
out = subprocess.run(['git', 'for-each-ref', 'refs/tags',
                      '--format=%(creatordate:short) %(refname:short)'],
                     capture_output=True, text=True).stdout
keep = set()
for linea in out.splitlines():
    fecha, _, nombre = linea.partition(' ')
    nombre = nombre.strip()
    if fecha >= CUTOFF and nombre.startswith('v3.6.') and nombre.endswith('-SDK6'):
        keep.add(int(nombre[len('v3.6.'):-len('-SDK6')]))

kits = sorted((RAIZ / 'scripts').glob('release-v*'))
fuera, dentro = [], []
for p in kits:
    nombre = p.name[len('release-'):]
    if nombre == 'v36207':
        dentro.append(nombre)
        continue
    n = nombre[len('v36'):] if nombre.startswith('v36') else None
    if n and n.isdigit() and int(n) in keep:
        dentro.append(nombre)
        continue
    fuera.append(nombre)

for nombre in fuera:
    d = RAIZ / 'scripts' / f'release-{nombre}'
    tr = subprocess.run(['git', 'ls-files', '--', str(d.relative_to(RAIZ))],
                        capture_output=True, text=True).stdout.strip()
    if tr:
        subprocess.run(['git', 'rm', '-r', '-q', '--', str(d.relative_to(RAIZ))],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)

print(f'kits FUERA: {len(fuera)} → {", ".join(fuera[:18])}{"…" if len(fuera) > 18 else ""}')
print(f'kits SE QUEDAN: {len(dentro)} → {", ".join(dentro)}')
restan = sorted(p.name for p in (RAIZ / 'scripts').glob('release-v*'))
print(f'kits en disco tras la limpieza: {len(restan)} → {", ".join(restan)}')
print(f'trackeados en release-v*: {len(subprocess.run(["git", "ls-files", "--", "scripts/release-v"], capture_output=True, text=True).stdout.splitlines())} (pathspec por prefijo)')
