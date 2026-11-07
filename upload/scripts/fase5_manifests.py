#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FASE 5 (V3.6.3-SDK3): bump de los 3 manifests que migran su música al
SDK (createMusic v1.2.0) — oeste v49→v50, magia v29→v30, valle_neon v2→v3 —
con nota de historial. Re-entrante: si el bump ya está hecho, no toca nada."""
import json
from pathlib import Path

RAIZ = Path('/home/z/my-project')
PUB = RAIZ / 'public' / 'championships'

BUMPS = {
    'oeste': (50,
              '2026-10-19 v3.6.3-SDK3 · FASE 5 de la modularización P0 · '
              'createMusic (SDK v1.2.0): la BSO del saloon (motor v2.78+v2.124) y '
              'la música del vagón (v2.111) se migran al motor único del SDK con '
              'conducta idéntica — fundido de entrada 0,8 s, sincronía en vivo con '
              'el ajuste global (rampa 0,15 s), UNA MELODÍA, resurrección de '
              'contexto (v2.124), parada instantánea y el fix v2.125 del '
              'decodeAudioData ahora en UNA sola fuente; la exclusividad '
              'BSO↔vagón (antes, la ranura _mus compartida) se reproduce con '
              'opts.excluso.'),
    'magia': (30,
              '2026-10-19 v3.6.3-SDK3 · FASE 5 de la modularización P0 · '
              'createMusic (SDK v1.2.0): la BSO del Wizard (motor v2.78+v2.124) se '
              'migra al motor único del SDK con conducta idéntica — fundido de '
              'entrada 0,8 s, sincronía en vivo con el ajuste global, UNA MELODÍA, '
              'resurrección de contexto y parada instantánea; el fix v2.125 del '
              'decodeAudioData vive en UNA sola fuente.'),
    'valle_neon': (3,
                   '2026-10-19 v3.6.3-SDK3 · FASE 5 de la modularización P0 · '
                   'createMusic (SDK v1.2.0): la música WAV en bucle se migra al '
                   'motor único del SDK con conducta idéntica — volumen fijo del '
                   'manifest, fundido de entrada 1,2 s, gate UNA MELODÍA también '
                   'en musicOn, sin sync de volumen y parada con fundido de 0,4 s '
                   '(stop a 500 ms), como su motor v1 original.'),
}

for mod, (vnew, nota) in BUMPS.items():
    p = PUB / mod / 'manifest.json'
    m = json.loads(p.read_text(encoding='utf-8'))
    cur = m.get('version')
    if cur == vnew:
        print(f'· {mod}: manifest ya está en v{vnew} — sin cambios')
        continue
    if cur != vnew - 1:
        raise SystemExit(f'FALLO: manifest de {mod} está en v{cur}, esperaba v{vnew - 1}')
    m['version'] = vnew
    clave = 'notes' if isinstance(m.get('notes'), list) else 'cambios'
    m.setdefault(clave, []).append(nota)
    p.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'· {mod}: manifest v{vnew} · nota añadida a {clave!r}')

print('manifests de la FASE 5 listos.')
