#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r48_viva.py — r48 · SELLADO VIVO a 3.6.141-SDK6 (FASE 143).

Petición del dueño de hoy:
  1. «incorpora en el Hall de la cabaña la melodia que te indico
     'cabana.mp3', puesto que no teníamos aún ninguna asignada a ese
     escenario» — la cabaña suena como el resto de salones.
  2. BATERÍA COMPLETA de agentes sobre el multijugador (dos modalidades,
     sin cuelgues, sincronización, fluido, media >60 FPS) para mañana
     testear con clientes reales.

Este sellador:
  · VERSION.json → 3.6.141-SDK6 · FASE 143 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html (build_game.py) y fija el golden real
  · re-ancla los sellos de versión de los tests de rondas (r34-r45)
  · verifica AGUJAS sobre el game.html final (idempotente, exit 1 si falla)
"""
import glob
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SRC = RAIZ / 'src' / 'game'
GAME = RAIZ / 'public' / 'game.html'
GOLDEN = SRC / 'GOLDEN_SHA256.txt'
VIEJA, NUEVA = '3.6.140-SDK6', '3.6.141-SDK6'
VIEJO_TAG, NUEVO_TAG = 'v36140-sdk6', 'v36141-sdk6'
FASE_VIEJA, FASE_NUEVA = 142, 143
VIEJO_NOMBRE = ('La voz del oráculo — voz solemne del Arcano, candado '
                'siempre visible y constelación del arte nuevo')
NOMBRE = ('La cabaña suena — cabana.mp3 en el Hall y batería multijugador '
          'lista para clientes reales')

AGUJAS = [
    (b"musica: 'assets/hall/cabana/cabana.mp3'", 1),
    (b"assets/hall/cabana/", None),         # base + musica (≥2; comentarios incluidos)
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.141 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vj.write_text(json.dumps(vdat, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def parchea(ruta: Path, viejo: str, nuevo: str) -> None:
        if not ruta.exists():
            return
        t = ruta.read_text(encoding='utf-8')
        if viejo in t:
            ruta.write_text(t.replace(viejo, nuevo), encoding='utf-8')

    parchea(SRC / 'core' / 'c00_pre_three.js',
            f"const VERSION = '{VIEJA}'", f"const VERSION = '{NUEVA}'")
    parchea(SRC / '03_body.html', f'>V{VIEJA}</span>', f'>V{NUEVA}</span>')
    parchea(RAIZ / 'public' / 'sw.js',
            f"crazypp-v{VIEJA}", f"crazypp-v{NUEVA}")
    # r47 dejó page.tsx apuntando a v36140 (ZIPs inexistentes); vuelve al
    # último Release real (v36139 — assets verificados en GitHub API hoy).
    parchea(RAIZ / 'src' / 'app' / 'descargas' / 'page.tsx',
            'v36140-sdk6', 'v36139-sdk6')
    print(f'· sellos → {NUEVA} · FASE {FASE_NUEVA}')


def ensambla() -> bytes:
    """El ensamblado EXACTO de build_game.py, en este proceso."""
    spec = importlib.util.spec_from_file_location('bg', RAIZ / 'scripts' / 'build_game.py')
    bg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bg)
    datos = b''.join(
        bg.pieza_pura((SRC / n).read_bytes()) if n.startswith('core/') else (SRC / n).read_bytes()
        for n, _ in bg.ORDER
    )
    return datos


def reancla_tests() -> None:
    """Re-ancla versión/fase/nombre/golden en los tests de rondas."""
    sha = hashlib.sha256(GAME.read_bytes()).hexdigest()
    vdat = json.loads((SRC / 'VERSION.json').read_text(encoding='utf-8'))
    golden_viejo = vdat.get('golden', '')
    cambios = [
        (VIEJA, NUEVA),
        (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
        (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
        (VIEJO_NOMBRE, NOMBRE),
        (VIEJO_NOMBRE.upper(), NOMBRE.upper()),
    ]
    if golden_viejo:
        cambios.append((golden_viejo, sha))
    n_fich = 0
    for f in sorted(glob.glob(str(RAIZ / 'scripts' / 'test_r*.mjs'))):
        p = Path(f)
        t = p.read_text(encoding='utf-8')
        orig = t
        for viejo, nuevo in cambios:
            t = t.replace(viejo, nuevo)
        if t != orig:
            p.write_text(t, encoding='utf-8')
            n_fich += 1
    print(f'· {n_fich} tests re-anclados (versión/fase/golden)')


def verifica(etiqueta: str) -> bool:
    gh = GAME.read_bytes()
    ok = True
    for aguja, esperado in AGUJAS:
        n = gh.count(aguja)
        bien = (n >= 1) if esperado is None else (n == esperado)
        print(f'  [{"✓" if bien else "✗"}] {aguja.decode()[:38]:40s} ×{n} (esperado {esperado or "≥1"})')
        ok = ok and bien
    v_ok = f"const VERSION = '{NUEVA}'".encode() in gh
    m_ok = b"musica: 'assets/hall/cabana/cabana.mp3'" in gh
    print(f'  [{"✓" if v_ok else "✗"}] VERSION {NUEVA}')
    print(f'  [{"✓" if m_ok else "✗"}] cabana.mp3 en HALL_VARIANTES (game.html)')
    ok = ok and v_ok and m_ok
    print(f'{etiqueta}: {"TODO OK" if ok else "FALLO"}')
    return ok


def main() -> None:
    sella_sellos()
    datos = ensambla()
    sha = hashlib.sha256(datos).hexdigest()
    GAME.write_bytes(datos)
    GOLDEN.write_text(
        '# SHA-256 del game.html ensamblado (build_game.py — regenerado por sella_r48_viva)\n'
        f'{sha}\n', encoding='utf-8')
    print(f'· game.html ESCRITO: {len(datos):,} B · sha {sha[:16]}…')
    # golden al VERSION.json (convención reancla_r47)
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['golden'] = sha
    vdat['tamano'] = len(datos)
    vj.write_text(json.dumps(vdat, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    reancla_tests()
    if not verifica('VERIFICACIÓN r48'):
        sys.exit(1)


if __name__ == '__main__':
    main()
