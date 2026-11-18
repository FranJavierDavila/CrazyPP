#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_arnes_fisico_v3698.py — capa QA del ARNÉS FÍSICO (M2a).
Envuelve scripts/arnes_rallies_v3698.mjs (node puro: física c05 + árbitro c06
+ IA c06 reales, 200 rallies con invariantes I1-I5, determinista por semilla,
con canario opcional) y emite la línea RESULTADO que qa_todo.py parsea."""
import re
import subprocess
import sys
from pathlib import Path

SCR = Path('/home/z/my-project/scripts')
r = subprocess.run(
    ['node', '--no-warnings', str(SCR / 'arnes_rallies_v3698.mjs')],
    capture_output=True, text=True, timeout=300,
)
print(r.stdout)
if r.stderr:
    print(r.stderr, file=sys.stderr)
m = re.search(r'violaciones:\s*(\d+)', r.stdout)
viol = int(m.group(1)) if m else 9999
n = '200'
mn = re.search(r'ARNÉS FÍSICO · (\d+) rallies', r.stdout)
if mn:
    n = mn.group(1)
print(f'RESULTADO: {n} rallies · {viol} fallos')
sys.exit(r.returncode)
