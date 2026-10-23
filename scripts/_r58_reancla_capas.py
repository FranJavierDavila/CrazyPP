#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r58 · RE-ANCLA las capas vecinas al nuevo estado del juego:
  · 5 PODERES en el registro (clon entra): los stubs Math.random de las
    capas AI/AK/AL que sembraban imán/portal con 4 entradas ahora
    apuntan al índice correcto con 5 (floor(r*5)).
  · PRECALIENTE de 16 piezas (r58 añade clon-fx + voz-clon + vozSel).
  · manifest de la locura v27 en la capa H (ZIPs y gateway).
Idempotente por sustitución literal."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

FALLOS = 0


def sust(q, pares, obligatorio=True):
    global FALLOS
    p = SCR / q
    t = p.read_text(encoding='utf-8')
    for viejo, nuevo in pares:
        if viejo in t:
            t = t.replace(viejo, nuevo)
            print(f'  ✓ {q}: {viejo[:44]!r} → {nuevo[:44]!r}')
        elif nuevo in t:
            print(f'  = {q}: ya re-anclado ({nuevo[:36]!r})')
        elif obligatorio:
            print(f'  ✗ {q}: ni viejo ni nuevo ({viejo[:44]!r})')
            FALLOS += 1
    p.write_text(t, encoding='utf-8')


# AI · qa_poderes_activo_v3640 — siembra del imán con 5 poderes
sust('qa_poderes_activo_v3640.py', [
    ("Math.random = () => 0.6;", "Math.random = () => 0.5;"),   # imán idx2/5
])

# AK · qa_portal_v3642 — siembra del portal con 5 poderes
sust('qa_portal_v3642.py', [
    ("Math.random = () => 0.75;", "Math.random = () => 0.65;"),  # portal idx3/5
])

# AL · qa_superpoderes_v3643 — cola de 16 + siembras con 5 poderes
sust('qa_superpoderes_v3643.py', [
    ("cola de 13 piezas", "cola de 16 piezas"),
    ("_megaPrewarmQ.length === 13", "_megaPrewarmQ.length === 16"),
    ("Math.random = () => 0.6;", "Math.random = () => 0.5;"),    # imán
    ("Math.random = () => 0.75;", "Math.random = () => 0.65;"),  # portal
    ("Math.random = () => 0.3;", "Math.random = () => 0.25;"),   # efecto idx1/5
])

# H · qa_descargas_v365 — manifest locura v27 en ZIPs y gateway
sust('qa_descargas_v365.py', [
    ("manifest v26", "manifest v27"),
    ("'locura': 26", "'locura': 27"),
    ('"locura": 26', '"locura": 27'),
    ("locura v26", "locura v27"),
])

if FALLOS:
    print('RE-ANCLA r58: FALLOS', FALLOS)
    sys.exit(1)
print('RE-ANCLA r58 OK')
