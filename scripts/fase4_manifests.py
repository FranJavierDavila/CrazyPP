#!/usr/bin/env python3
"""FASE 4 (V3.6.2-SDK2): bump de manifest + entrada de historial para los 4
campeonatos adoptantes (oeste/magia/locura/valle_neon). Idempotente: si la
versión ya es la nueva y la nota está, no toca nada."""
import json
from pathlib import Path

RAIZ = Path('/home/z/my-project/public/championships')

NOTAS = {
    'oeste': ('2026-10-19 v3.6.2-SDK2 · FASE 4 de la modularización P0 · SDK DE '
              'CAMPEONATOS: los 4 motores SFX one-shot (risa del forajido, risa del '
              'pueblo, jingle de oleada y risas del robo del vagón) y los 3 congelados '
              '(duelo de revólver ×2 y aviso de superpoder) delegan en '
              'championships/sdk/champ_sdk.js v1.1.0 con conducta idéntica (volúmenes, '
              'anti-spam de 3,2 s y paneo 0,4 intactos; el silencio del arcade ahora se '
              'respeta como en el orbital y La Locura); el puente al núcleo pasa a '
              'getCore(). La MÚSICA en bucle (BSO del saloon y vagón) conserva su motor '
              'propio (fundido, resurrección de contexto y UNA MELODÍA) hasta que el '
              'SDK estrene createMusic.'),
    'magia': ('2026-10-19 v3.6.2-SDK2 · FASE 4 de la modularización P0 · SDK DE '
              'CAMPEONATOS: la risa del mago y el congelado del aviso de superpoder '
              'delegan en championships/sdk/champ_sdk.js v1.1.0 con conducta idéntica '
              '(anti-spam de 3,2 s intacto; el panNode(0) era paneo centrado sin efecto '
              'audible, y ahora la risa respeta además el silencio del arcade como en el '
              'orbital y La Locura); el puente al núcleo pasa a getCore(). La BSO en '
              'bucle conserva su motor propio hasta createMusic.'),
    'locura': ('2026-10-19 v3.6.2-SDK2 · FASE 4 de la modularización P0 · SDK DE '
               'CAMPEONATOS: el congelado del aviso de superpoder — el patrón v2.40 que '
               'NACIÓ en este módulo — y el puente al núcleo pasan a vivir en '
               'championships/sdk/champ_sdk.js v1.1.0 (congela()/getCore): una sola '
               'fuente para los 5 campeonatos. Sin cambios de conducta: la partida se '
               'congela exactamente igual (warn + T_OUT + 0,1 s).'),
    'valle_neon': ('2026-10-19 v3.6.2-SDK2 · FASE 4 de la modularización P0 · SDK DE '
                   'CAMPEONATOS: el puente al núcleo pasa a getCore() de '
                   'championships/sdk/champ_sdk.js v1.1.0 (una sola fuente para los 5 '
                   'módulos). Sin SFX mp3 ni congelados propios: la música WAV en bucle '
                   'conserva su motor propio hasta que el SDK estrene createMusic.'),
}

VERSION_NUEVA = {'oeste': 49, 'magia': 29, 'locura': 21, 'valle_neon': 2}

for mod, nota in NOTAS.items():
    p = RAIZ / mod / 'manifest.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    nueva = VERSION_NUEVA[mod]
    ya = d.get('version') == nueva and any('v3.6.2-SDK2' in n for n in d.get('notes', []))
    if ya:
        print(f'· {mod}: ya en v{nueva} con nota SDK2 (sin cambios)')
        continue
    d['version'] = nueva
    d.setdefault('notes', []).append(nota)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'· {mod}: manifest v{d["version"] - 1} → v{nueva} + nota SDK2')
print('manifests FASE 4 listos.')
