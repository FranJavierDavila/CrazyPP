# -*- coding: utf-8 -*-
"""Extrae los <script> inline de public/game.html y los valida con node --check."""
import pathlib, re, subprocess, sys, tempfile

F = pathlib.Path('/home/z/my-project/public/game.html')
html = F.read_text(encoding='utf-8')
bloques = [(m.start(), m.group(2)) for m in
           re.finditer(r'<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>', html, re.S | re.I)]
# atributos de cada bloque para descartar importmap / json / módulos sin check clásico
atrib = [m.group(1).lower() for m in
         re.finditer(r'<script(?![^>]*\bsrc=)([^>]*)>', html, re.S | re.I)]
print('bloques inline:', len(bloques), '· total js:', sum(len(b) for _, b in bloques), 'bytes')

mal = 0
for i, ((_, b), at) in enumerate(zip(bloques, atrib)):
    if 'importmap' in at or 'application/json' in at:
        print('  salto bloque %d (importmap/json)' % i)
        continue
    ext = '.mjs' if 'module' in at else '.js'
    p = pathlib.Path(tempfile.mkdtemp()) / ('bloque_%02d%s' % (i, ext))
    p.write_text(b, encoding='utf-8')
    r = subprocess.run(['node', '--check', str(p)], capture_output=True, text=True)
    if r.returncode != 0:
        mal += 1
        print('FALLO bloque %d (%d bytes):' % (i, len(b)))
        print(r.stderr[:2000])
print('SINTAXIS:', 'OK' if mal == 0 else '%d BLOQUES MAL' % mal)
sys.exit(1 if mal else 0)
