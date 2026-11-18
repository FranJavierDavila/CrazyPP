#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r52_produccion.py — verificación byte-exacto de la FASE 146
(v3.6.144-SDK6) contra GitHub Pages, patrón r49/r50:
  1 · PAGES-VERSION.txt con version=3.6.144-SDK6 (sondeo hasta 6 min)
  2 · game.html servido byte-exacto (sha256 con las 2 reescrituras aplicadas)
  3 · AGUJAS de la fase presentes en el game.html servido
  4 · sw.js servido con CACHE crazypp-v3.6.144-SDK6
"""
import hashlib
import re
import sys
import time
import urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126 Safari/537.36')
REPO = '/home/z/my-project/upload'
OK = True


def chk(cond, msg):
    global OK
    print(f'  [{"OK" if cond else "FALLO"}] {msg}')
    OK = OK and bool(cond)


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# — 1 · PAGES-VERSION (sondeo: el builder de Pages tarda 1-3 min) —
print('· sondeando PAGES-VERSION.txt…')
pv = None
for i in range(36):                       # 36 × 10 s = 6 min máx
    try:
        pv = get(BASE + 'PAGES-VERSION.txt?v=' + str(int(time.time())),
                 timeout=20).decode('utf-8', 'replace')
        if 'version=3.6.144-SDK6' in pv:
            break
    except Exception:
        pass
    time.sleep(10)
chk(pv is not None and 'version=3.6.144-SDK6' in pv,
    f'PAGES-VERSION: version=3.6.144-SDK6 '
    f'(contiene: {pv[:80] if pv else "nada"})')
m_sha = re.search(r'game_sha256=([0-9a-f]{64})', pv or '')
chk(bool(m_sha), 'PAGES-VERSION lleva game_sha256')

# — 2 · game.html servido byte-exacto —
esperado = open(REPO + '/public/game.html', 'rb').read()
esperado = esperado.replace(b'src="/vendor/socket.io.min.js"',
                            b'src="vendor/socket.io.min.js"')
esperado = esperado.replace(b'href="/tv.html"', b'href="tv.html"')
sha_esperado = hashlib.sha256(esperado).hexdigest()
if m_sha:
    chk(m_sha.group(1) == sha_esperado,
        f'game_sha256 registrado == esperado ({sha_esperado[:12]}…)')
print('· descargando game.html servido (~11,5 MB)…')
servido = get(BASE + 'game.html?v=3.6.144-SDK6', timeout=180)
sha_servido = hashlib.sha256(servido).hexdigest()
chk(sha_servido == sha_esperado,
    f'game.html servido byte-exacto ({len(servido):,} B · '
     f'sha {sha_servido[:12]}…)')

# — 3 · agujas de la FASE 146 —
agujas = [
    (b'this._arconoPrecalentar();', 1),
    (b'for (const p of PODERES_PALA) this._arconoIconoImg(p.id);', 1),
    (b'const vivo = PODERES_PALA[this._arconoIdx];', 1),
    (b'if (vivo && vivo.id === id) this._arconoRepinta(false);', 1),
    (b"const VERSION = '3.6.144-SDK6'", 1),
    # conservación de fases anteriores
    (b'gunConsuma = this.champs.fireGun(i) === true;', 1),
    (b"window.__PP_TELE.ev('anim_shield', { msg: sig });", 1),
    (b"musica: 'assets/hall/cabana/cabana.mp3'", 1),
]
for a, esp in agujas:
    n = servido.count(a)
    chk(n == esp, f'aguja x{n} (esperado {esp}): {a.decode()[:44]}')

# — 4 · sw.js servido —
sw = get(BASE + 'sw.js?v=' + str(int(time.time())), timeout=60)
chk(b"crazypp-v3.6.144-SDK6" in sw, 'sw.js servido: CACHE crazypp-v3.6.144-SDK6')

print('VERIFICACIÓN PRODUCCIÓN r52: ' + ('TODO OK' if OK else 'FALLO'))
sys.exit(0 if OK else 1)
