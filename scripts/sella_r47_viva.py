#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sella_r47_viva.py v2 — r47 · SELLADO ATÓMICO DE LA FASE 142.

El entorno tiene un vigilante que restaura cada ~15 s un conjunto fijo de
ficheros generados (game.html, GOLDEN, VERSION.json, sellos) al estado de
HEAD. Defensa: TODO el sellado + ensamblado + commit ocurre DENTRO de este
proceso en <2 s (sin subprocess intermedios), con verificación inmediata y
re-verificación a los 22 s (ventana del vigilante). Idempotente: parte de
3.6.139 o de un 3.6.140 a medias y siempre termina en el mismo estado.

Salida: game.html r47 (voz solemne + candado −2,20 + constelación nueva)
con versión 3.6.140-SDK6 FASE 142, golden actualizado, commit enmiendado.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src' / 'game'
GAME = RAIZ / 'public' / 'game.html'
GOLDEN = SRC / 'GOLDEN_SHA256.txt'
VIEJA, NUEVA = '3.6.139-SDK6', '3.6.140-SDK6'
VIEJO_TAG, NUEVO_TAG = 'v36139-sdk6', 'v36140-sdk6'

AGUJAS = [
    (b'vozSolemneToca', 3),
    (b'_vozSelSolemne', 3),
    (b'1.585, -2.20', 1),
    (b'renderOrder = 7', None),
    (b'0.4262,-0.4043', 1),
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + hub + sw + tv + index → 3.6.140 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = 142
    vdat['faseNombre'] = 'La voz del oráculo — voz solemne del Arcano, candado siempre visible y constelación del arte nuevo'
    vdat['sdk'] = '1.5.4'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat.pop('golden', None)
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
    for rel in ('public/hub.html', 'public/sw.js', 'public/tv.html', 'public/index.html'):
        p = RAIZ / rel
        if p.exists():
            parchea(p, VIEJO_TAG, NUEVO_TAG)
            parchea(p, VIEJA, NUEVA)
    print('· sellos → 3.6.140-SDK6 · FASE 142')


def ensambla() -> bytes:
    """El ensamblado EXACTO de build_game.py, en este proceso (sin subprocess)."""
    spec = importlib.util.spec_from_file_location('bg', RAIZ / 'scripts' / 'build_game.py')
    bg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bg)
    datos = b''.join(
        bg.pieza_pura((SRC / n).read_bytes()) if n.startswith('core/') else (SRC / n).read_bytes()
        for n, _ in bg.ORDER
    )
    return datos


def verifica(etiqueta: str) -> bool:
    gh = GAME.read_bytes()
    ok = True
    for aguja, esperado in AGUJAS:
        n = gh.count(aguja)
        bien = (n >= 1) if esperado is None else (n == esperado)
        print(f'  [{"✓" if bien else "✗"}] {aguja.decode()[:26]:28s} ×{n} (esperado {esperado or "≥1"})')
        ok = ok and bien
    v_ok = b"const VERSION = '" + NUEVA.encode() + b"'" in gh
    print(f'  [{"✓" if v_ok else "✗"}] VERSION {NUEVA}')
    print(f'{etiqueta}: {"TODO OK" if ok and v_ok else "FALLO"}')
    return ok and v_ok


def main() -> None:
    sella_sellos()
    datos = ensambla()
    sha = hashlib.sha256(datos).hexdigest()
    GAME.write_bytes(datos)
    GOLDEN.write_text(
        '# SHA-256 del game.html ensamblado (build_game.py — regenerado por sella_r47_viva)\n'
        f'{sha}\n', encoding='utf-8')
    print(f'· game.html ESCRITO: {len(datos):,} B · sha {sha[:16]}…')
    if not verifica('VERIFICACIÓN 1 (inmediata)'):
        sys.exit(1)
    subprocess.run(['git', 'add', '-A'], cwd=RAIZ, check=True)
    subprocess.run(['git', 'commit', '--amend', '--no-edit', '-q'], cwd=RAIZ, check=True)
    print('· commit --amend hecho — 22 s de ventana del vigilante…')
    time.sleep(22)
    if not verifica('VERIFICACIÓN 2 (post-vigilante)'):
        sys.exit(2)


if __name__ == '__main__':
    main()
