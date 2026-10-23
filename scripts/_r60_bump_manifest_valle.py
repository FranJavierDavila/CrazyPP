#!/usr/bin/env python3
"""r60 · bump del manifest de valle_neon: version 4→5 + historial nuevo
(mapa del taller re-enganchado — bug pinzado al auditar los solapes)."""
import json
from pathlib import Path

P = Path('/home/z/my-project/public/championships/valle_neon/manifest.json')
m = json.loads(P.read_text(encoding='utf-8'))
assert m['version'] == 4, f"versión inesperada: {m['version']}"
m['version'] = 5
nota = ('2026-10-24 v3.6.52-SDK6 · r60: el MAPA DEL TALLER vuelve a verse en '
        'escena — MapaTaller nace perezoso (su group lo crea build()) y '
        'PlantillaCtrl.build lo colgaba ANTES de existir (THREE rechazaba el '
        'add con «Object3D.add: object not an instance»): detached desde la '
        'migración SDK5. build() idempotente llamado antes de colgar; show() '
        'intacto.')
m['historial'] = [nota]
P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n',
             encoding='utf-8')
print('valle_neon manifest → version', m['version'], '· historial creado')
