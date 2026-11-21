#!/usr/bin/env python3
"""actualiza_kit_relay_r112.py — lleva los fixes H13/H14/H15 del relay al kit
de empaquetado de la versión (scripts/release-v36209/server.mjs), que es la
FUENTE de los ZIPs de release (build_zip.py lo copia a cada paquete).

Transformación: mini-services/live-service/index.ts → server.mjs
  · quita la anotación de tipos de txt() (única TS-ism del fichero)
  · node --check del resultado antes de escribir el kit
"""
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
TS = RAIZ / 'mini-services/live-service/index.ts'
KIT = RAIZ / 'scripts/release-v36209/server.mjs'

src = TS.read_text(encoding='utf-8')
src2 = re.sub(r'\(v: unknown, max: number, def: string\)', '(v, max, def)', src)
if src2 == src:
    print('· nota: sin anotación de tipos que quitar (¿ya convertida?)')
restos = re.findall(r':\s*(?:unknown|string|number|boolean)\b', src2)
if restos:
    sys.exit(f'✗ quedan anotaciones de tipos sin despojar: {restos[:5]}')

tmp = Path('/tmp/kit_relay_check.mjs')
tmp.write_text(src2, encoding='utf-8')
r = subprocess.run(['node', '--check', str(tmp)], capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[:600])
    sys.exit('✗ el server.mjs convertido no compila')
print('✓ node --check del server.mjs convertido: OK')

viejo = KIT.read_text(encoding='utf-8')
KIT.write_text(src2, encoding='utf-8')
print(f'✓ kit actualizado: {KIT} ({len(viejo):,} → {len(src2):,} B)')
# sanity: las 3 firmas r112 deben estar en el kit
for marca in ('H13', 'H14', 'H15'):
    assert marca in src2, f'✗ falta la marca {marca} en el kit'
print('✓ marcas H13/H14/H15 presentes en el kit')
