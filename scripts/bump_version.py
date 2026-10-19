#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · BUMP DE VERSIÓN (una sola fuente: src/game/VERSION.json).

Es el ÚNICO camino legítimo para cambiar la versión del juego. En una sola
pasada, asertada y re-entrante:
  1. Verifica que los sellos actuales casan con VERSION.json (si alguien
     editó un sello a mano, ABORTA).
  2. Parchea los 3 sellos físicos: c00_pre_three.js (const VERSION),
     03_body.html (#verBadge) y el hub /descargas (todas las menciones).
  3. Reescribe VERSION.json (fecha de hoy + fase/sdk si se pasan).
  4. Regenera public/game.html (build_game.py --escribir) y refresca el
     GOLDEN_SHA256.txt con el comentario estándar.

Los manifests de campeonatos NO se tocan aquí: los suben los scripts de
cada fase junto con sus notas de historial.

Uso:
  python3 scripts/bump_version.py 3.6.6-SDK6
  python3 scripts/bump_version.py 3.7.0-P1 --fase 8 --fase-nombre "Roadmap P1" --sdk 1.4.0
"""
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src' / 'game'
C00 = SRC / 'core' / 'c00_pre_three.js'
BODY = SRC / '03_body.html'
HUB = RAIZ / 'src' / 'app' / 'descargas' / 'page.tsx'
VJSON = SRC / 'VERSION.json'
GOLDEN = SRC / 'GOLDEN_SHA256.txt'
GAME = RAIZ / 'public' / 'game.html'

RE_VERSION = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+-[A-Z0-9]+[0-9]*$')


def hub_tag(ver: str) -> str:
    '3.6.5-SDK5 → v365-sdk5 · 3.7.0-P1 → v370-p1'
    if '-' in ver:
        base, suf = ver.split('-', 1)
        return 'v' + base.replace('.', '') + '-' + suf.lower()
    return 'v' + ver.replace('.', '')


def aborta(msg):
    sys.exit('ABORTA (nada escrito): ' + msg)


def main():
    args = sys.argv[1:]
    flags = {'--fase': None, '--fase-nombre': None, '--sdk': None}
    nueva = None
    i = 0
    while i < len(args):
        a = args[i]
        if a in flags:
            if i + 1 >= len(args):
                aborta(f'{a} necesita un valor')
            flags[a] = args[i + 1]
            i += 2
        elif a.startswith('--'):
            aborta(f'flag desconocida {a!r}')
        else:
            if nueva is not None:
                aborta('solo se admite UNA versión nueva')
            nueva = a
            i += 1
    if nueva is None:
        print(__doc__)
        sys.exit(1)
    if not RE_VERSION.match(nueva):
        aborta(f'la versión {nueva!r} no sigue el formato X.Y.Z-NAME (p. ej. 3.6.6-SDK6)')

    vdat = json.loads(VJSON.read_text(encoding='utf-8'))
    actual = vdat.get('version')
    nuevo_tag = hub_tag(nueva)
    viejo_tag = vdat.get('hub') or hub_tag(actual)
    print(f'· bump: {actual} → {nueva} (hub {viejo_tag} → {nuevo_tag})')

    # 1. sellos actuales = VERSION.json (nada de edits a mano)
    c00 = C00.read_text(encoding='utf-8')
    if c00.count(f"const VERSION = '{actual}'") != 1:
        aborta(f'c00_pre_three.js no lleva exactamente una vez const VERSION = {actual!r}')
    body = BODY.read_text(encoding='utf-8')
    if body.count(f'>V{actual}</span>') != 1:
        aborta(f'03_body.html: el badge #verBadge no es V{actual!r}')
    hub = HUB.read_text(encoding='utf-8')
    n_ver_hub = hub.count(actual)
    n_tag_hub = hub.count(viejo_tag)
    if n_ver_hub < 3 or n_tag_hub < 3:
        aborta(f'hub con menciones inesperadas: {n_ver_hub}×{actual}, {n_tag_hub}×{viejo_tag}')
    # re-entrante: si los sellos EXACTOS ya son la nueva versión, no escribir
    # nada (los sellos van acotados por comillas/cierre, así que un sufijo
    # tipo 3.6.5-SDK5B no dispara el guard del 3.6.5-SDK5)
    if f"const VERSION = '{nueva}'" in c00 or f'>V{nueva}</span>' in body:
        aborta('los sellos ya son la versión nueva (¿bump repetido?)')

    # 2. parchear los 3 sellos
    C00.write_text(
        c00.replace(f"const VERSION = '{actual}'", f"const VERSION = '{nueva}'", 1),
        encoding='utf-8')
    BODY.write_text(
        body.replace(f'>V{actual}</span>', f'>V{nueva}</span>', 1),
        encoding='utf-8')
    HUB.write_text(
        hub.replace(actual, nueva).replace(viejo_tag, nuevo_tag),
        encoding='utf-8')
    print(f'· sellos parcheados: c00 (1) · badge (1) · hub ({n_ver_hub}×{nueva} + {n_tag_hub}×{nuevo_tag})')

    # 3. VERSION.json nuevo
    vdat2 = dict(vdat)
    vdat2['version'] = nueva
    vdat2['fecha'] = date.today().isoformat()
    vdat2['hub'] = nuevo_tag
    vdat2.pop('golden', None)          # lo rellena el paso 4 con el sha real
    if flags['--fase'] is not None:
        vdat2['fase'] = int(flags['--fase'])
    if flags['--fase-nombre'] is not None:
        vdat2['faseNombre'] = flags['--fase-nombre']
    if flags['--sdk'] is not None:
        vdat2['sdk'] = flags['--sdk']
    VJSON.write_text(json.dumps(vdat2, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # 4. build + golden nuevo
    r = subprocess.run([sys.executable, str(RAIZ / 'scripts' / 'build_game.py'), '--escribir'],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stdout.write(r.stderr)
        aborta('build_game.py --escribir falló (los sellos parcheados quedan: revisa y re-ejecuta)')
    sha = __import__('hashlib').sha256(GAME.read_bytes()).hexdigest()
    tam = GAME.stat().st_size
    GOLDEN.write_text(
        f'# SHA256 del game.html que produjo esta división ({nueva}, fase '
        f'{vdat2.get("fase")} · {vdat2.get("faseNombre", "")}; sello actualizado\n'
        f'# por bump_version.py desde {actual})\n{sha}\n', encoding='utf-8')
    vdat2['golden'] = sha
    VJSON.write_text(json.dumps(vdat2, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'· golden nuevo: {sha[:16]}… ({tam:,} B) · VERSION.json actualizado')

    # 5. contra-verificación con el guard del ensamblador
    r2 = subprocess.run([sys.executable, str(RAIZ / 'scripts' / 'build_game.py')],
                        capture_output=True, text=True)
    if 'BYTE-EXACTO' not in r2.stdout:
        aborta('la contra-verificación del build no sale BYTE-EXACTO')
    print('· contra-verificación BYTE-EXACTO: OK')

    print(f'\nSiguiente: QA (qa_sup1 + imp2 + escudo + descargas + smoke) → release → commit.')


if __name__ == '__main__':
    main()
