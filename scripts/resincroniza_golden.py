#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-sincroniza golden tras un ajuste tardío del fuente MISMA versión.
Replica EXACTAMENTE el paso 4/5 de bump_version.py (única fuente: VERSION.json):
build --escribir → sha256 nuevo en GOLDEN_SHA256.txt + VERSION.json.golden →
contra-verificación BYTE-EXACTO. No toca sellos de versión."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src' / 'game'
GOLDEN = SRC / 'GOLDEN_SHA256.txt'
VJSON = SRC / 'VERSION.json'
GAME = RAIZ / 'public' / 'game.html'


def main():
    v = json.loads(VJSON.read_text(encoding='utf-8'))
    r = subprocess.run([sys.executable, str(RAIZ / 'scripts' / 'build_game.py'), '--escribir'],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout[-400:])
    if r.returncode != 0:
        sys.stdout.write(r.stderr)
        sys.exit('ABORTA: build_game.py --escribir falló')
    sha = hashlib.sha256(GAME.read_bytes()).hexdigest()
    tam = GAME.stat().st_size
    GOLDEN.write_text(
        f'# SHA256 del game.html que produjo esta división ({v["version"]}, fase '
        f'{v.get("fase")} · {v.get("faseNombre", "")}; golden re-sincronizado tras '
        f'ajuste tardío del fuente (misma versión, ganchos de QA)\n'
        f'# por scripts/resincroniza_golden.py (pasos 4/5 de bump_version.py)\n{sha}\n',
        encoding='utf-8')
    v['golden'] = sha
    VJSON.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'· golden nuevo: {sha[:16]}… ({tam:,} B) · VERSION.json actualizado')
    r2 = subprocess.run([sys.executable, str(RAIZ / 'scripts' / 'build_game.py')],
                        capture_output=True, text=True)
    if 'BYTE-EXACTO' not in r2.stdout:
        sys.exit('ABORTA: la contra-verificación del build no sale BYTE-EXACTO')
    print('· contra-verificación BYTE-EXACTO: OK')


if __name__ == '__main__':
    main()
