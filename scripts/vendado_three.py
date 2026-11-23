#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vendado_three.py — E1 de la auditoría r120: three.js al mismo origen.

Descarga three@0.170.0 (build + los addons que el juego usa) desde jsdelivr
a public/vendor/three/ con su ESTRUCTURA relativa intacta, para que el
importmap del juego deje de depender del CDN. Recorre los imports relativos
en BFS (cada addon puede importar utilidades hermanas) y deja los bare
specifiers ('three') intactos: los resuelve el import map.

Uso: python3 scripts/vendado_three.py            # descarga y verifica
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DEST = RAIZ / 'public' / 'vendor' / 'three'
BASE = 'https://cdn.jsdelivr.net/npm/three@0.170.0'
RAICES = [
    ('build/three.module.js', 'build/three.module.js'),
    ('examples/jsm/environments/RoomEnvironment.js', 'addons/environments/RoomEnvironment.js'),
    ('examples/jsm/loaders/GLTFLoader.js', 'addons/loaders/GLTFLoader.js'),
]
RE_FROM = re.compile(r"""(?:from|import|import\()\s*['"]([^'"]+)['"]""")

vistos = {}
pendientes = [(src, dst) for src, dst in RAICES]

def ruta_de(src, spec):
    """Resuelve un specifier relativo dentro del paquete npm de three."""
    base = src.rsplit('/', 1)[0]
    combinado = base + '/' + spec if not spec.startswith('/') else spec[1:]
    partes = []
    for p in combinado.split('/'):
        if p == '.' or p == '':
            continue
        if p == '..':
            if partes:
                partes.pop()
            continue
        partes.append(p)
    return '/'.join(partes)

def descarga(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'vendado_three/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def main():
    if not DEST.exists():
        DEST.mkdir(parents=True)
    while pendientes:
        src, dst = pendientes.pop(0)
        if dst in vistos:
            continue
        url = f'{BASE}/{src}'
        datos = descarga(url)
        destino = DEST / dst
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(datos)
        vistos[dst] = len(datos)
        print(f'  · {dst}  {len(datos):,} B')
        txt = datos.decode('utf-8', 'replace')
        for spec in RE_FROM.findall(txt):
            if spec.startswith('.'):
                rel = ruta_de(src, spec)
                nuevo_dst = ('build/' + rel[len('build/'):] if rel.startswith('build/')
                             else 'addons/' + rel[len('examples/jsm/'):])
                if nuevo_dst not in vistos:
                    pendientes.append((rel, nuevo_dst))
    total = sum(vistos.values())
    print(f'\nvendado: {len(vistos)} ficheros · {total:,} B en public/vendor/three/')
    man = {'origen': BASE, 'ficheros': {k: v for k, v in sorted(vistos.items())}}
    (DEST / 'MANIFEST.json').write_text(
        json.dumps(man, indent=1) + '\n', encoding='utf-8')
    # verificación: cada import relativo resuelto existe en disco
    huecos = []
    for dst in vistos:
        txt = (DEST / dst).read_text(encoding='utf-8', errors='replace')
        for spec in RE_FROM.findall(txt):
            if not spec.startswith('.'):
                continue
            src0 = ('build/' + dst[len('build/'):] if dst.startswith('build/')
                    else 'examples/jsm/' + dst[len('addons/'):])
            rel = ruta_de(src0, spec)
            nuevo_dst = ('build/' + rel[len('build/'):] if rel.startswith('build/')
                         else 'addons/' + rel[len('examples/jsm/'):])
            if nuevo_dst not in vistos:
                huecos.append((dst, spec))
    if huecos:
        sys.exit('FALLO: imports relativos sin cubrir: ' + repr(huecos[:6]))
    print('verificación: todos los imports relativos resueltos ✓')


if __name__ == '__main__':
    main()
