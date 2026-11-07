#!/usr/bin/env python3
"""r62 · re-sellado del golden tras regenerar las muestras SFX con el
contenedor WAV completo (bump_version aborta en re-ejecución; replica su
paso 4/5 — patrón _r60_regolden)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src' / 'game'
GOLDEN = SRC / 'GOLDEN_SHA256.txt'
GAME = RAIZ / 'public' / 'game.html'
VJSON = SRC / 'VERSION.json'

r = subprocess.run([sys.executable, str(RAIZ / 'scripts' / 'build_game.py'),
                    '--escribir'], capture_output=True, text=True)
sys.stdout.write(r.stdout[-500:])
if r.returncode != 0:
    sys.stdout.write(r.stderr)
    sys.exit('build falló')

sha = hashlib.sha256(GAME.read_bytes()).hexdigest()
tam = GAME.stat().st_size
vdat = json.loads(VJSON.read_text(encoding='utf-8'))
GOLDEN.write_text(
    f'# SHA256 del game.html que produjo esta división ({vdat["version"]}, fase '
    f'{vdat.get("fase")} · {vdat.get("faseNombre", "")}; sello actualizado\n'
    f'# por re-golden_r62.py tras regenerar las muestras SFX reales con el\n'
    f'# contenedor WAV completo (RIFF incluido — la 1.ª iba sin cabecera))\n{sha}\n',
    encoding='utf-8')
vdat['golden'] = sha
VJSON.write_text(json.dumps(vdat, ensure_ascii=False, indent=2) + '\n',
                 encoding='utf-8')
print(f'· golden nuevo: {sha[:16]}… ({tam:,} B)')

r2 = subprocess.run([sys.executable, str(RAIZ / 'scripts' / 'build_game.py')],
                    capture_output=True, text=True)
ok = 'BYTE-EXACTO' in r2.stdout
print('· contra-verificación BYTE-EXACTO:', 'OK' if ok else 'FALLO')
sys.exit(0 if ok else 1)
