#!/usr/bin/env python3
"""Restaura el árbol de trabajo desde origin/main, path a path, tolerando fallos."""
import subprocess, sys

paths = [l.strip() for l in open('/tmp/checkout_ok.txt') if l.strip()]
print(f"Total: {len(paths)}")

fail, ok = [], 0
CHUNK = 40
for i in range(0, len(paths), CHUNK):
    chunk = paths[i:i+CHUNK]
    r = subprocess.run(['git', 'checkout', 'origin/main', '--'] + chunk,
                       capture_output=True, text=True, cwd='/home/z/my-project')
    if r.returncode == 0:
        ok += len(chunk)
    else:
        # reintento uno a uno para aislar el fichero problemático
        for p in chunk:
            r1 = subprocess.run(['git', 'checkout', 'origin/main', '--', p],
                                capture_output=True, text=True, cwd='/home/z/my-project')
            if r1.returncode == 0:
                ok += 1
            else:
                fail.append(p)

print(f"OK: {ok}  FALLOS: {len(fail)}")
for p in fail[:40]:
    print('  FAIL:', p)
