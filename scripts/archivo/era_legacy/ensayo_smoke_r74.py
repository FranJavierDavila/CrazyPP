#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ensayo_smoke_r74.py — ENSAYO del humo de producción CONTRA LOCAL.

Genera scripts/prod_smoke_r74_local.py (BASE → 127.0.0.1:3671), crea el
PAGES-VERSION.txt temporal con el MISMO formato que escribirá
deploy_pages.py, sirve public/ y ejecuta el humo completo (estático +
funcional). Al terminar retira el fichero temporal. Así, cuando el dueño
pegue el token, el humo de producción correrá sobre vías ya ensayadas.
"""
import hashlib
import pathlib
import shutil
import subprocess
import sys
import time

UP = pathlib.Path('/home/z/my-project/upload')
SRC = UP / 'scripts/prod_smoke_r74.py'
DST = UP / 'scripts/prod_smoke_r74_local.py'
PUB = UP / 'public'
HASH = '05f91cc23ff49823e5ffd855cc183bb042215764'
PORT = 3671

t = SRC.read_text(encoding='utf-8')
t = t.replace("BASE = 'https://franjavierdavila.github.io/CrazyPP'",
              "BASE = 'http://127.0.0.1:" + str(PORT) + "'")
t = t.replace('smoke de producción CONTRA PRODUCCIÓN',
              'ensayo del smoke contra LOCAL')
DST.write_text(t, encoding='utf-8')
print('humo local generado:', DST.name)

game = (PUB / 'game.html').read_bytes()
sha = hashlib.sha256(game).hexdigest()
info = ('version=3.6.165-SDK6\n'
        'fuente_commit=' + HASH + '\n'
        'game_sha256=' + sha + '\n'
        'reescrituras=0\n'
        'fecha=ensayo-local\n'
        'url=http://127.0.0.1:' + str(PORT) + '\n')
pv = PUB / 'PAGES-VERSION.txt'
pv.write_text(info, encoding='utf-8')
print('PAGES-VERSION.txt temporal (se retira al final)')

serv = subprocess.Popen(
    [sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1',
     '--directory', str(PUB)],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)
rc = 1
try:
    rc = subprocess.call([sys.executable, str(DST)])
finally:
    serv.terminate()
    pv.unlink(missing_ok=True)
    print('PAGES-VERSION.txt temporal retirado · servidor parado')
print('ENSAYO DEL HUMO rc=' + str(rc))
sys.exit(rc)
