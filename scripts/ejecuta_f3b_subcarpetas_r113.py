#!/usr/bin/env python3
"""ejecuta_f3b_subcarpetas_r113.py — completa la F3: mueve las subcarpetas
legacy de scripts/ (capturas, assets de era, kits de release viejos) a
scripts/archivo/. Protección dinámica: si un fichero VIVO referencia el
nombre de la carpeta, se queda. Golden (vs tag) antes del commit."""
import hashlib
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project')
REG = RAIZ / 'download/registro_limpieza_r113.md'
GOLDEN = RAIZ / 'src/game/GOLDEN_SHA256.txt'
GAME = RAIZ / 'public/game.html'
TAG = 'r113-pre-limpieza'


def sh(cmd, text=True, **kw):
    kw.pop('text', None)
    return subprocess.run(cmd, capture_output=True, text=text, cwd=RAIZ, **kw)


def git(*a, check=True):
    r = sh(['git', *a])
    if check and r.returncode:
        sys.exit(f'✗ git {" ".join(a)} → {r.stderr[:400]}')
    return r.stdout


def hash_en_texto(t):
    for linea in t.splitlines():
        linea = linea.strip()
        if linea and not linea.startswith('#'):
            tok = linea.split()[0]
            if re.fullmatch(r'[0-9a-fA-F]{64}', tok):
                return tok.lower()
    return None


def w(s):
    print('  ' + s)
    with REG.open('a', encoding='utf-8') as f:
        f.write(s + '\n')


# keep-set idéntico al de F3 (+ el contenido de la batería en el corpus)
KEEP_DIRS = {'_r60', 'release-v36209', 'render_brazos', 'worker-tele', 'archivo'}
KEEP_FILES = {
    'deploy_pages.py', 'limpieza_github_r109.py', 'backup_completo.py',
    'check_live_service_igualdad.py', 'test_r112_live_service.mjs',
    'test_worker_r169.mjs', 'diag_tele_produccion.py', 'probe_tele_prod.py',
    'alerta_telemetria.py', 'qa_tele_r42.py', 'actualiza_kit_relay_r112.py',
    'completa_assets_r112.py', 'inventario_limpieza_r113.py',
    'analisis_fino_r113.py', '_inventario_r113.json', 'gen_propuesta_r113.js',
    'gen_propuesta_r113_lib.js', 'patch_pie_r113.py', 'ejecuta_limpieza_r113.py',
    '_r61_bateria.sh', '_r60_regolden.py', '_r62_regolden.py',
}
KEEP_PREFIX = ('arnes_', 'LEEME', 'README', '_r60', '_r61', '_r62')

corpus = []
for d in KEEP_DIRS:
    base = RAIZ / 'scripts' / d
    if base.exists():
        for f in base.rglob('*'):
            if f.is_file() and f.stat().st_size < 3_000_000 and \
               f.suffix in {'.py', '.mjs', '.js', '.md', '.toml', '.txt', '.json', '.sh'}:
                corpus.append(f.read_text(encoding='utf-8', errors='replace'))
for nombre in KEEP_FILES:
    f = RAIZ / 'scripts' / nombre
    if f.exists() and f.is_file() and f.stat().st_size < 3_000_000:
        corpus.append(f.read_text(encoding='utf-8', errors='replace'))
for cfg in ('package.json', 'next.config.ts', 'Caddyfile'):
    p = RAIZ / cfg
    if p.exists():
        corpus.append(p.read_text(encoding='utf-8', errors='replace'))
for sf in (RAIZ / '.zscripts').glob('*.sh'):
    corpus.append(sf.read_text(encoding='utf-8', errors='replace'))
CORPUS = '\n'.join(corpus)

w('\n## F3b · subcarpetas legacy de scripts/ → scripts/archivo/\n')
track = git('ls-files', 'scripts').splitlines()
subs = sorted({p.split('/')[1] for p in track if p.count('/') >= 2})
movid, proteg, detalle = [], [], []
for nombre in subs:
    if nombre in KEEP_DIRS or any(nombre.startswith(px) for px in KEEP_PREFIX):
        continue
    p = RAIZ / 'scripts' / nombre
    if not p.is_dir():
        continue
    if nombre in CORPUS:
        proteg.append(nombre)
        continue
    files = [x for x in p.rglob('*') if x.is_file()]
    viz = sum(1 for x in files if x.suffix.lower() in
              {'.png', '.jpg', '.jpeg', '.mp4', '.webp', '.gif'})
    tipo = 'capturas' if files and viz / len(files) > 0.4 else 'eras'
    destino = RAIZ / 'scripts/archivo' / tipo / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    git('mv', f'scripts/{nombre}', f'scripts/archivo/{tipo}/{nombre}')
    movid.append(nombre)
    detalle.append(f'{nombre}({tipo},{len(files)}f)')

w(f'- subcarpetas movidas: {len(movid)} → ' + ' · '.join(detalle[:20]) +
  (' …' if len(detalle) > 20 else ''))
if proteg:
    w('- PROTEGIDAS por referencias de los vivos: ' + ', '.join(proteg))

# golden + commit
real = hashlib.sha256(GAME.read_bytes()).hexdigest()
b = sh(['git', 'show', f'{TAG}:public/game.html'], text=False)
if real != hashlib.sha256(b.stdout).hexdigest():
    sys.exit('✗ F3b: game.html difiere del tag — aborto')
g = hash_en_texto(GOLDEN.read_text())
w(f'- golden F3b: vs tag ✓ · golden casa: ' + ('coincide ✓' if g == real else 'NO coincide (preexistente)'))
git('add', '-A')
r = sh(['git', 'commit', '-m', f'r113-F3b · completa scripts/archivo/: {len(movid)} '
        'subcarpetas legacy (capturas, assets de era, kits release-v36156…v36207) '
        'archivadas; vivos y protegidos intactos'])
if r.returncode:
    sys.exit('✗ commit F3b: ' + r.stderr[:300])
w(f'- commit F3b · HEAD: `{git("log","-1","--format=%h")}`')
print('\n✓ F3b completado (' + time.strftime('%H:%M') + ')')
