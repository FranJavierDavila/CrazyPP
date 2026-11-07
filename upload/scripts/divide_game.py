#!/usr/bin/env python3
"""
CRAZY PING PONG · FASE 1 de modularización P0 — DIVISOR BYTE-EXACTO de game.html.
Trocea public/game.html (v3.6.0-SUP1, SHA de00...) en src/game/: wrappers HTML/CSS
+ 14 subsistemas JS del núcleo (core/). Cada corte se valida con un token esperado
en la primera línea del trozo. La recomposición debe ser byte-exacta (sha256 igual).
NO toca public/game.html: solo escribe src/game/.
"""
import hashlib
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
GAME = RAIZ / 'public' / 'game.html'
OUT = RAIZ / 'src' / 'game'
CORE = OUT / 'core'

data = GAME.read_bytes()
GOLDEN = hashlib.sha256(data).hexdigest()
print(f'· game.html leído: {len(data):,} B · sha256 {GOLDEN[:16]}…')

# Split en bytes, pero los cortes son por LÍNEAS (1-based, inclusivos).
lines = data.split(b'\n')          # split('\n'): línea N = lines[N-1]; el último elemento es '' si EOF con \n
NL = len(lines)
print(f'· líneas: {NL}')

# (nombre, primera, última, token que DEBE estar en la primera línea del trozo)
# nota: última de cada trozo = (siguiente_primera - 1)
PLAN = [
    ('00_head.html',       1,     None, b'<!DOCTYPE html>'),   # doctype+head+CSS (corte real se fija abajo)
    ('01_vendor.html',     271,   271,  b'socket.io.min.js'),
    ('02_importmap.html',  272,   279,  b'importmap'),
    ('03_body.html',       280,   365,  None),                 # marcado de la portada
    ('04_boot.html',       366,   380,  b'<script>'),
    ('05_module_open.html', 381,  381,  b'type="module"'),
]
CORES = [
    ('c00_pre_three.js',   382,   2226,  b'/* ===='),
    ('c01_modelos_3d.js',  2227,  2531,  b"import * as THREE"),
    ('c02_cfg_escena.js',  2532,  2780,  b'const DIMS'),
    ('c03_audio_voz.js',   2781,  4412,  b'const VOICE_FULL'),
    ('c04_fisica_ccd.js',  4413,  4749,  b'const MAX_SUBSTEP_DT'),
    ('c05_colisiones_ia_golpeo.js', 4750, 5588, b'function collidePaddle('),
    ('c06_logros_stats_ia_rival.js', 5589, 6279, b'const ACHIEVEMENTS'),
    ('c07_escena_sala.js', 6280,  6760,  b'function createRoom'),
    ('c08_hall_hud.js',    6761,  7547,  b'const HALL = {'),
    ('c09_red_netlink.js', 7548,  8272,  b'class NetLink'),
    ('c10_menu_saque.js',  8273,  8376,  b"const MENU_LOGO_SRC"),
    ('c11_champloader.js', 8377,  9020,  b'class ChampLoader'),
    ('c12_pingponggame.js', 9021, 14123, b'class PingPongGame'),
    ('c13_ui_arranque.js', 14124, 17031, b'function renderPlayBtn'),
]

# cortes dependientes: 00_head acaba en 270 (</style>); cierre del módulo y cola al final
PLAN[0] = ('00_head.html', 1, 270, b'<!DOCTYPE html>')
PLAN.append(('06_module_close.html', 17032, 17033, b'</script>'))
PLAN.append(('07_tail.html', 17034, NL - 1, b'<script>'))

def linea(n: int) -> bytes:
    return lines[n - 1]

def token_ok(n: int, tok) -> bool:
    return tok is None or tok in linea(n)

errores = []
# verificación dura de tokens ANTES de escribir nada
for nombre, ini, fin, tok in PLAN + CORES:
    if not token_ok(ini, tok):
        errores.append(f'{nombre}: línea {ini} no contiene {tok!r} → {linea(ini)[:80]!r}')
if errores:
    sys.exit('FALLO de identidad de cortes:\n  ' + '\n  '.join(errores))

# el cierre del módulo debe abrir con </script> y 17033 debe ser vacía
if linea(17032).strip() != b'</script>':
    sys.exit(f'FALLO: línea 17032 no es </script> → {linea(17032)[:60]!r}')
if not linea(17033).lstrip().startswith(b'<!--'):
    sys.exit(f'FALLO: línea 17033 no es comentario HTML → {linea(17033)[:60]!r}')

# escribir trozos (cada trozo conserva sus \n internos; entre trozos NO se añade nada:
# el salto del último renglón de cada trozo se guarda como parte del propio trozo)
OUT.mkdir(parents=True, exist_ok=True)
CORE.mkdir(parents=True, exist_ok=True)

piezas = []
nombres_core = {t[0] for t in CORES}
for nombre, ini, fin, _ in PLAN + CORES:
    # reconstrucción en bytes: únete con \n los elementos [ini-1 .. fin-1] y añade \n final
    cuerpo = b'\n'.join(lines[ini - 1:fin]) + b'\n'
    p = (CORE if nombre in nombres_core else OUT) / nombre
    p.write_bytes(cuerpo)
    piezas.append((nombre, p, len(cuerpo)))
    print(f'  {("core/" + nombre) if nombre in nombres_core else nombre:41s}'
          f' líneas {ini:>5}..{fin:>5}  {len(cuerpo):>10,} B')

# recomposición y comparación byte-exacta (orden canónico: wrappers 0..5, core, close, tail)
canon = PLAN[:6] + CORES + PLAN[6:]
rec = b''.join(((CORE if n in nombres_core else OUT) / n).read_bytes() for n, _, _, _ in canon)
rec_sha = hashlib.sha256(rec).hexdigest()
if rec != data:
    sys.exit(f'FALLO: recomposición DIFFERENTE (sha {rec_sha[:16]}≠{GOLDEN[:16]})')
print(f'\n✓ RECOMPOSICIÓN BYTE-EXACTA: {len(rec):,} B · sha256 {rec_sha[:16]}…')
(OUT / 'GOLDEN_SHA256.txt').write_text(
    f'# SHA256 del game.html que produjo esta división (v3.6.0-SUP1, Task 89)\n{GOLDEN}\n',
    encoding='utf-8')
print('· src/game/GOLDEN_SHA256.txt escrito')
