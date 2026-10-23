#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r58 · re-ancla los stubs restantes (portal/efecto/manifest H)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'
FALLOS = 0


def sust(q, pares):
    global FALLOS
    p = SCR / q
    t = p.read_text(encoding='utf-8')
    for viejo, nuevo in pares:
        if viejo in t:
            t = t.replace(viejo, nuevo)
            print(f'  ✓ {q}: {viejo[:46]!r} → {nuevo[:46]!r}')
        elif nuevo in t:
            print(f'  = {q}: ya re-anclado ({nuevo[:36]!r})')
        else:
            print(f'  ✗ {q}: ni viejo ni nuevo ({viejo[:46]!r})')
            FALLOS += 1
    p.write_text(t, encoding='utf-8')


sust('qa_portal_v3642.py', [
    ("Math.random = () => 0.9;", "Math.random = () => 0.65;"),  # portal idx3/5
])
sust('qa_superpoderes_v3643.py', [
    ("Math.random = () => 0.98;               // siembra PORTAL (último)",
     "Math.random = () => 0.65;               // siembra PORTAL (4.º de 5)"),
])
sust('qa_descargas_v365.py', [
    ("('locura', 26, 'v3.6.4-SDK4')", "('locura', 27, 'v3.6.4-SDK4')"),
])

if FALLOS:
    print('FALLOS', FALLOS)
    sys.exit(1)
print('RE-ANCLA 2 OK')
