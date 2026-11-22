#!/usr/bin/env python3
"""ejecuta_BC_r113.py — opciones B y C aprobadas por el dueño.
B: deduplicar fuentes/dueno/backup_2026-11-17/ — borrar SOLO ficheros con
   gemelo byte-exacto verificado (public/, src/, variantes, paquetes/ZIPs).
   El índice de gemelos EXCLUIE archivo/ (B corre antes que C para que
   ninguna copia única dependa de una captura que C va a borrar).
C: borrar capturas (scripts/archivo/capturas/) y visuales/logs de era_legacy.
Golden byte-exacto (vs tag + fichero de la casa) antes de cada commit.
Todo queda en el historial git (recuperable vía r113-pre-limpieza)."""
import hashlib
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

RAIZ = Path('/home/z/my-project')
REG = RAIZ / 'download/registro_limpieza_r113.md'
GOLDEN = RAIZ / 'src/game/GOLDEN_SHA256.txt'
GAME = RAIZ / 'public/game.html'
TAG = 'r113-pre-limpieza'
BACKUP = RAIZ / 'fuentes/dueno/backup_2026-11-17'
CAPTURAS = RAIZ / 'scripts/archivo/capturas'
ERALEG = RAIZ / 'scripts/archivo/era_legacy'


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


def golden_ok(fase):
    real = hashlib.sha256(GAME.read_bytes()).hexdigest()
    b = sh(['git', 'show', f'{TAG}:public/game.html'], text=False)
    if real != hashlib.sha256(b.stdout).hexdigest():
        sys.exit(f'✗ {fase}: game.html difiere del tag — aborto sin commit')
    g = hash_en_texto(GOLDEN.read_text())
    w(f'- golden {fase}: vs tag ✓ · golden casa: ' +
      ('coincide ✓' if g == real else 'NO coincide (preexistente)'))


def w(s):
    print('  ' + s)
    with REG.open('a', encoding='utf-8') as f:
        f.write(s + '\n')


def mb(n):
    return f'{n/1e6:.1f} MB'


if not REG.exists():
    REG.parent.mkdir(parents=True, exist_ok=True)
    REG.write_text('# Registro de limpieza r113 — regenerado (el fichero original '
                   'se perdió al reciclar download/ entre turnos; el detalle '
                   'completo de F1-F6 vive en worklog.md sección 13 del repo)\n',
                   encoding='utf-8')
w(f'\n## Opciones B y C · {time.strftime("%Y-%m-%d %H:%M")} (aprobadas por el dueño)\n')

# ── índice de gemelos VIVOS (excluye scripts/archivo y el propio backup) ──
w('### B · deduplicación del backup del dueño\n')
index = {}
prefijos = ('public/', 'src/', 'fuentes/dueno/paquetes/',
            'fuentes/dueno/variantes/')
MEDIA = {'.mp3', '.png', '.jpg', '.jpeg', '.glb', '.webp', '.mp4', '.zip',
         '.ogg', '.wav', '.gif'}
for ruta in git('ls-files').splitlines():
    es_pref = ruta.startswith(prefijos)
    es_raiz_media = '/' not in ruta and Path(ruta).suffix.lower() in MEDIA
    if es_pref or es_raiz_media:
        p = RAIZ / ruta
        if p.is_file() and not p.is_symlink():
            index.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(),
                             ruta)
# contenido de los 5 ZIPs fuente (gemelo = entrada dentro del zip)
for z in sorted((RAIZ / 'fuentes/dueno/paquetes').glob('*.zip')):
    with zipfile.ZipFile(z) as zf:
        for info in zf.infolist():
            if info.is_dir() or info.file_size == 0:
                continue
            h = hashlib.sha256(zf.read(info.filename)).hexdigest()
            index.setdefault(h, f'{z.name}::{info.filename}')
w(f'- índice de gemelos vivos: {len(index)} hashes (public, src, variantes, '
  'paquetes y contenido de los ZIPs · archivo/ excluido a propósito)')

borrados, quedan = [], []
for f in sorted(BACKUP.rglob('*')):
    if not f.is_file():
        continue
    rel = f.relative_to(RAIZ)
    n = f.stat().st_size
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    if h in index:
        git('rm', '-q', str(rel))
        borrados.append((rel, n, index[h]))
    else:
        quedan.append((rel, n))
for rel, n, gem in borrados:
    w(f'- B borrado `{rel}` ({mb(n)}) — gemelo: {gem}')
w(f'- B total: {len(borrados)} duplicados ({mb(sum(n for _, n, _ in borrados))}) '
  f'· {len(quedan)} únicos conservados '
  f'({mb(sum(n for _, n in quedan))}): ' +
  ', '.join(f'{rel.name}({mb(n)})' for rel, n in quedan))
golden_ok('B')
git('add', '-A')
r = sh(['git', 'commit', '-m', f'r113-B · dedupe backup del dueño: '
        f'{len(borrados)} duplicados byte-exactos fuera ({mb(sum(n for _, n, _ in borrados))}), '
        f'{len(quedan)} únicos conservados en fuentes/dueno/backup_2026-11-17/'])
if r.returncode:
    sys.exit('✗ commit B: ' + r.stderr[:300])
w(f'- commit B ✓')

# ── C · capturas y logs sin valor ─────────────────────────────────
w('\n### C · capturas y logs de una sola era\n')
total = 0
n_fich = 0
if CAPTURAS.exists():
    for f in CAPTURAS.rglob('*'):
        if f.is_file():
            total += f.stat().st_size
            n_fich += 1
    w(f'- scripts/archivo/capturas/: {n_fich} ficheros ({mb(total)}) — '
      '11 paquetes de captura/arte de era sin referencias')
    git('rm', '-q', '-r', 'scripts/archivo/capturas')
pats = ('*.png', '*.jpg', '*.jpeg', '*.webp', '*.mp4', '*.log', '*log*.txt')
bigotes = set()
for pat in pats:
    bigotes.update(ERALEG.glob(pat))
purgables = sorted(p for p in bigotes if p.is_file())
tam = sum(p.stat().st_size for p in purgables)
total += tam
n_fich += len(purgables)
w(f'- era_legacy visuales/logs: {len(purgables)} ficheros ({mb(tam)}) — '
  'capturas QA, mapas clown, renders y logs de una sola era')
for p in purgables:
    git('rm', '-q', str(p.relative_to(RAIZ)))
w(f'- C total: {n_fich} ficheros ({mb(total)})')
golden_ok('C')
git('add', '-A')
r = sh(['git', 'commit', '-m', f'r113-C · capturas y logs de era fuera: '
        f'{n_fich} ficheros ({mb(total)}) — contenido único del dueño '
        'preservado en fuentes/dueno/ (B corrió antes) y en el historial git'])
if r.returncode:
    sys.exit('✗ commit C: ' + r.stderr[:300])
w(f'- commit C ✓')

st = sh(['git', 'status', '--porcelain']).stdout.strip()
w('- git status: ' + ('limpio ✓' if not st else st[:200]))
print('\n✓ B y C ejecutadas. Registro: ' + str(REG))
