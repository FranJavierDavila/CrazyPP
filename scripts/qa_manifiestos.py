#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA de MANIFIESTOS (roadmap P1 · config-as-data). Los manifest.json de los
5 campeonatos SON la configuración del juego: aquí se valida que
  1. cumplen championship.schema.json (jsonschema),
  2. sus versiones casan con VERSION.json (la única fuente),
  3. la estructura de etapas es jugable (ids únicos, kinds conocidos),
  4. TODO asset y audio referenciado EXISTE en disco con contenido real,
  5. los estados del rival apuntan a ficheros reales (la convención FASE 7:
     orbital <estado>.webp · valle <estado>.png — el bug del standee gris
     de Valle nació de una convención rota; este QA la pina).
Uso: python3 scripts/qa_manifiestos.py"""
import json
import sys
from pathlib import Path

import jsonschema

RAIZ = Path('/home/z/my-project')
CH = RAIZ / 'public' / 'championships'
MODOS = ('oeste', 'magia', 'locura', 'estacion_orbital', 'valle_neon')
KINDS_OK = {'duelo', 'objetos', 'custom', 'prueba', 'final', 'tren', 'escudo',
            'impulso', 'arkanoid'}
# convención de ficheros de estado del rival (FASE 7)
RIVAL_ESTADO = {
    'estacion_orbital': ('rival.webp', '.webp'),
    'valle_neon': ('rival_kraken.png', '.png'),
}
ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1

def fichero_ok(p: Path) -> bool:
    return p.is_file() and p.stat().st_size > 500

schema = json.loads((CH / 'championship.schema.json').read_text(encoding='utf-8'))
vjson = json.loads((RAIZ / 'src/game/VERSION.json').read_text(encoding='utf-8'))

for mod in MODOS:
    print(f'== {mod} ==')
    p = CH / mod / 'manifest.json'
    m = json.loads(p.read_text(encoding='utf-8'))

    # 1 · schema
    try:
        jsonschema.validate(m, schema)
        chk(True, 'cumple championship.schema.json')
    except jsonschema.ValidationError as e:
        chk(False, f'schema: {e.message[:120]}')

    # 2 · versión única
    esperada = vjson['manifests'][mod]
    chk(m.get('version') == esperada, f'version = v{esperada} (VERSION.json)')

    # 3 · etapas
    stages = m.get('stages') or []
    ids = [s.get('id') for s in stages]
    chk(len(stages) >= 3 and len(ids) == len(set(ids)) and all(ids),
        f'etapas únicas y nombradas ({len(stages)}: {"·".join(str(i) for i in ids)})')
    chk(all(s.get('kind') in KINDS_OK for s in stages), 'kinds de etapa conocidos')

    # 4 · audio referenciado existe
    audio = m.get('audio') or {}
    if isinstance(audio, dict):
        mus = audio.get('music')
        if mus:
            chk(fichero_ok(CH / mod / mus), f'audio.music existe ({mus})')
        else:
            chk(True, 'sin audio.music en el manifest (música por otra vía)')
    mu = m.get('musicUrl')
    if isinstance(mu, str) and mu:
        chk(fichero_ok(CH / mod / mu), f'musicUrl existe ({mu})')

    # 5 · rival: base + estados con ficheros reales
    rival = m.get('rival') or {}
    if mod in RIVAL_ESTADO and rival.get('states'):
        base, ext = RIVAL_ESTADO[mod]
        chk(fichero_ok(CH / mod / 'assets' / base), f'rival base existe ({base})')
        faltan = [st for st in rival['states']
                  if not fichero_ok(CH / mod / 'assets' / f'{st}{ext}')]
        chk(not faltan, f'estados del rival existen ({len(rival["states"])} · ext {ext})'
            + (f' — FALTAN: {faltan[:4]}' if faltan else ''))

print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
sys.exit(1 if fails else 0)
