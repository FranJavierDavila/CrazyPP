#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C2 (r129 · ola 3) · sella el nuevo golden tras la externalización de recursos.
Actualiza src/game/GOLDEN_SHA256.txt y los campos tamano/golden de VERSION.json
manteniendo la versión 3.6.210-SDK6 (mismo patrón que r128)."""
import hashlib
import json
from pathlib import Path

RAIZ = Path('/home/z/my-project')
GAME = RAIZ / 'public/game.html'

sha = hashlib.sha256(GAME.read_bytes()).hexdigest()
tamano = GAME.stat().st_size
print(f'game.html: {tamano} B · sha256 {sha}')

# GOLDEN_SHA256.txt (mismo formato de 2 líneas de cabecera + hash)
golden_txt = RAIZ / 'src/game/GOLDEN_SHA256.txt'
golden_txt.write_text(
    f'# SHA256 del game.html que produjo esta división (3.6.210-SDK6, fase 188 · OLA 3: C2 '
    f'separa los recursos del HTML — el artefacto baja de 12,5 MB a {tamano} B)\n'
    f'{sha}\n', encoding='utf-8')

# VERSION.json
vj = RAIZ / 'src/game/VERSION.json'
datos = json.loads(vj.read_text(encoding='utf-8'))
antes = (datos.get('tamano'), datos.get('golden'), datos.get('fase'))
datos['tamano'] = tamano
datos['golden'] = sha
if 'fase' in datos:
    datos['fase'] = 188
vj.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'VERSION.json: tamano {antes[0]}→{tamano} · golden {str(antes[1])[:8]}…→{sha[:8]}… · fase {antes[2]}→{datos.get("fase")}')
