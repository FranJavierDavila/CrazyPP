#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r37 (v3.6.133) · RE-SELLADO del golden tras el refinamiento del FIX D
(puerta de invitado en el reinicio de ICE) HECHO DESPUÉS del bump.

El bump_version.py ya dejó los sellos de texto en 3.6.133-SDK6 y ABORTA en
una segunda pasada (patrón re-entrante de la casa). Este helper repite SOLO
el paso 4 del bump: sha real del build vigente → GOLDEN_SHA256.txt (mismo
formato de comentario) + VERSION.json (golden y tamaño).
Uso: python3 scripts/_r37_resellar.py
"""
import hashlib
import json
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
GAME = RAIZ / 'public' / 'game.html'
GOLDEN = RAIZ / 'src' / 'game' / 'GOLDEN_SHA256.txt'
VJSON = RAIZ / 'src' / 'game' / 'VERSION.json'

sha = hashlib.sha256(GAME.read_bytes()).hexdigest()
tam = GAME.stat().st_size
vdat = json.loads(VJSON.read_text(encoding='utf-8'))
nueva = vdat['version']
viejo_tag = 'v36132-sdk6'   # ronda anterior (la que precede a este bump)
actual = '3.6.132-SDK6'

GOLDEN.write_text(
    f'# SHA256 del game.html que produjo esta división ({nueva}, fase '
    f'{vdat.get("fase")} · {vdat.get("faseNombre", "")}; sello actualizado\n'
    f'# por bump_version.py desde {actual} · re-sellado por _r37_resellar.py)\n'
    f'{sha}\n', encoding='utf-8')
vdat['golden'] = sha
vdat['tamano'] = tam
VJSON.write_text(json.dumps(vdat, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'· golden re-sellado: {sha[:16]}… ({tam:,} B) · VERSION.json actualizado')
