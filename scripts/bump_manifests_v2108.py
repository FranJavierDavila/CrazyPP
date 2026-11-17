#!/usr/bin/env python3
"""v2.108 · Bump de versión + nota del MODO DEPURACIÓN en los 3 manifests."""
import json, io

BASE = '/home/z/my-project/crazypp/championships'
NOTA = ('v2.108 · MODO DEPURACIÓN «foro3d»: nombre del jugador = foro3d → el mapa '
        'levanta todas las tapas y el gatillo salta a cualquier etapa sin requisitos '
        '(vía rejugada, progreso real congelado). El núcleo no persiste registros de '
        'este jugador (pp_champ_*/pp_arcade_*/stats), no publica ranking mundial ni '
        'telemetría, y muestra rótulo «MODO DEPURACIÓN» (2D portada + 3D visor).')

for cid in ('oeste', 'locura', 'magia'):
    p = f'{BASE}/{cid}/manifest.json'
    with io.open(p, encoding='utf-8') as f:
        m = json.load(f)
    m['version'] = int(m.get('version', 0)) + 1
    m['note_dbg'] = NOTA
    with io.open(p, 'w', encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'{cid}: version -> {m["version"]}')

# índice de campeonatos: sin cambios de contenido, se revalida que existe
import os
idx = f'{BASE}/championships.json'
print('índice championships.json existe:', os.path.exists(idx))
