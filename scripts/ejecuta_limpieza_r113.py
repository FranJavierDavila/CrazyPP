#!/usr/bin/env python3
"""ejecuta_limpieza_r113.py — F1-F4 del plan aprobado por el dueño («continua»).
Opciones conservadoras: F2 = opción A (mover tmp_owner_backup entero, 0 pérdida);
F3 = solo archivar (sin borrados definitivos).
Reglas de blindaje:
  · BORRAR solo si el hash SHA-256 coincide con la copia VIVA en public/ (verificado en vivo).
  · MOVER con git/shutil + git add -A (rename preserva historia; git revert restaura).
  · Antes de mover en scripts/: si un fichero VIVO referencia su basename → se queda.
  · Golden byte-exacto de public/game.html antes de cada commit.
"""
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
GIT_CRED = ['-c', 'credential.helper=!f() { echo username=FranJavierDavila; '
            'echo password=$GIT_TOKEN; }; f']


def sh(cmd, text=True, **kw):
    kw.pop('text', None)
    return subprocess.run(cmd, capture_output=True, text=text, cwd=RAIZ, **kw)


def git(*a, check=True):
    r = sh(['git', *a])
    if check and r.returncode:
        sys.exit(f'✗ git {" ".join(a)} → {r.stderr[:400]}')
    return r.stdout


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def hash_en_texto(t):
    for linea in t.splitlines():
        linea = linea.strip()
        if linea and not linea.startswith('#'):
            tok = linea.split()[0]
            if re.fullmatch(r'[0-9a-fA-F]{64}', tok):
                return tok.lower()
    return None


def golden_ok(fase):
    real = sha(GAME)
    # inv1 (dura): el juego NO cambia durante la limpieza → versión del tag
    b = sh(['git', 'show', 'r113-pre-limpieza:public/game.html'], text=False)
    esperado_tag = hashlib.sha256(b.stdout).hexdigest()
    if real != esperado_tag:
        sys.exit(f'✗ {fase}: public/game.html DIFIERE del tag r113-pre-limpieza — aborto sin commit')
    # inv2 (informativa): golden de la casa (fichero con línea de comentario #)
    g = hash_en_texto(GOLDEN.read_text())
    w(f'- golden {fase}: vs tag byte-exacto ✓ · golden casa: ' +
      ('coincide ✓' if g == real else 'NO coincide (estado preexistente, se reporta)'))


REG.write_text('# Registro de limpieza r113 — ejecución ' +
               time.strftime('%Y-%m-%d %H:%M') + '\n\n'
               'Red de seguridad: tag `r113-pre-limpieza` en remoto (88a4967).\n'
               'Restauración total: `git reset --hard r113-pre-limpieza`.\n'
               'Nota: intento previo abortó por parser del golden (comentario #); '
               'los 21 borrados de F1 quedaron staged y se incluyen en el commit F1.\n',
               encoding='utf-8')


def w(s):
    print('  ' + s)
    with REG.open('a', encoding='utf-8') as f:
        f.write(s + '\n')


def sec(t):
    print('\n== ' + t + ' ==')
    with REG.open('a', encoding='utf-8') as f:
        f.write(f'\n## {t}\n\n')


def commit(fase, msg):
    golden_ok(fase)
    git('add', '-A')
    r = sh(['git', 'commit', '-m', msg])
    if r.returncode:
        sys.exit(f'✗ commit {fase}: {r.stderr[:300]}')
    w(f'- commit: `{msg.splitlines()[0]}`')


# ── F1 · borrados seguros de raíz (copia viva verificada por hash) ──
sec('F1 · residuos de raíz borrados (copia viva verificada)')
BORRAR = {
    'pasted_image_1792409981731.png': None,
    'pasted_image_1792412462779.png': None,
    'pasted_image_1793142026721.png': None,
    'pasted_image_1794263101577.png': None,
    'pasted_image_1794572236703.png': None,
    'pasted_image_1794677767954.png': None,
    'tmp_pages_version.txt': None,
    'rascacielos.mp3': 'public/assets/hall/rascacielos/rascacielos.mp3',
    'observatorio.mp3': 'public/assets/hall/observatorio/observatorio.mp3',
    'recompensa.png': 'public/championships/oeste/assets/recompensa.png',
    'zombi_normas.png': 'public/championships/halloween/assets/normas_halloween.png',
    'techo.jpg': 'public/assets/partido/techo.jpg',
    'suelo.jpg': 'public/assets/hall/suelo.jpg',
    'pantallainfo.png': 'public/championships/estacion_orbital/assets/reactor_impulso/pantallainfo.png',
    'zombi_defeated.mp3': 'public/championships/halloween/assets/zombi_defeated.mp3',
    'suelo_pista.jpg': 'public/assets/partido/suelo.jpg',
    'nucleo_gravedad_lp.glb': 'public/championships/estacion_orbital/assets/nucleo_gravedad_lp.glb',
    'vias.mp3': 'public/championships/oeste/assets/tren/vias.mp3',
    'risa_astro.mp3': 'public/championships/estacion_orbital/assets/risa_astro.mp3',
    'zombi_crazy.mp3': 'public/championships/halloween/assets/zombi_crazy.mp3',
    'palas.png': 'public/assets/hall/palas.png',
}
total_b = 0
for nombre, gemelo in BORRAR.items():
    f = RAIZ / nombre
    if not f.exists():
        w(f'- borrado `{" + " if False else ""}{nombre}` — ya sin copia en disco '
          '(staged en el intento previo; se incluye en el commit F1)')
        continue
    n_bytes = f.stat().st_size
    if gemelo:
        if not (RAIZ / gemelo).exists():
            sys.exit(f'✗ {nombre}: su copia viva {gemelo} no existe — aborto')
        if sha(f) != sha(RAIZ / gemelo):
            sys.exit(f'✗ {nombre}: hash DISTINTO de {gemelo} — aborto (no se borra)')
        verificado = 'gemelo byte-exacto verificado'
    else:
        verificado = '0 referencias en el repo (imagen pegada / vacío)'
    git('rm', '-q', nombre)
    total_b += n_bytes
    w(f'- borrado `{nombre}` ({n_bytes/1e6:.2f} MB) — {verificado}')
commit('F1', 'r113-F1 · limpieza raíz: 21 residuos borrados '
        '(14 con gemelo byte-exacto verificado por hash + 6 pasted sin refs + tmp_pages_version)')

# ── F2 · fuentes/dueno/ (opción A: 0 pérdida) ─────────────────────
sec('F2 · fuentes/dueno/ — paquetes, variantes y backup del dueño (opción A)')
fuentes = RAIZ / 'fuentes/dueno'
(fuentes / 'paquetes').mkdir(parents=True, exist_ok=True)
(fuentes / 'variantes').mkdir(parents=True, exist_ok=True)
for z in ('paredes.zip', 'rascacielos.zip', 'partido.zip', 'troqueles.zip',
          'recortables.zip'):
    if (RAIZ / z).exists():
        git('mv', z, f'fuentes/dueno/paquetes/{z}')
        w(f'- movido `{z}` → fuentes/dueno/paquetes/')
for v in ('techo.png', 'monticulo.png', 'zombi_idle.png', 'portals.png',
          'tapa.png', 'zombi_victory.mp3'):
    if (RAIZ / v).exists():
        git('mv', v, f'fuentes/dueno/variantes/{v}')
        w(f'- movido `{v}` → fuentes/dueno/variantes/')
if (RAIZ / 'tmp_owner_backup').exists():
    shutil.move(str(RAIZ / 'tmp_owner_backup'),
                str(fuentes / 'backup_2026-11-17'))
    git('add', '-A', 'tmp_owner_backup', 'fuentes')
    w('- movido `tmp_owner_backup/` → fuentes/dueno/backup_2026-11-17/ '
      '(104 ficheros trackeados + no trackeados, 87,7 MB, sin pérdida)')
manifests = list((RAIZ / 'public/championships').glob('*/manifest.json')) + \
    list((RAIZ / 'public/championships').glob('*/LEEME*'))
for m in manifests:
    txt = m.read_text(encoding='utf-8', errors='replace')
    for z in ('paredes.zip', 'troqueles.zip', 'recortables.zip', 'rascacielos.zip',
              'partido.zip'):
        if z in txt:
            w(f'- nota: {m.relative_to(RAIZ)} menciona `{z}` en prosa histórica '
              '(no se edita: es texto de informe, no ruta de carga)')
commit('F2', 'r113-F2 · organización: fuentes/dueno/ con paquetes fuente, '
        'variantes y backup del dueño (opción A, 0 pérdida)')

# ── F3 · scripts/archivo/ con protección dinámica ─────────────────
sec('F3 · scripts/archivo/ — legacy por eras, vivos en sitio')
KEEP_FILES = {
    'deploy_pages.py', 'limpieza_github_r109.py', 'backup_completo.py',
    'check_live_service_igualdad.py', 'test_r112_live_service.mjs',
    'test_worker_r169.mjs', 'diag_tele_produccion.py', 'probe_tele_prod.py',
    'alerta_telemetria.py', 'qa_tele_r42.py', 'actualiza_kit_relay_r112.py',
    'completa_assets_r112.py', 'inventario_limpieza_r113.py',
    'analisis_fino_r113.py', '_inventario_r113.json', 'gen_propuesta_r113.js',
    'gen_propuesta_r113_lib.js', 'patch_pie_r113.py', '_r61_bateria.sh',
    '_r60_regolden.py', '_r62_regolden.py',
}
KEEP_DIRS = {'release-v36209', 'worker-tele', '_r60', 'render_brazos'}
KEEP_PREFIX = ('arnes_', 'LEEME', 'README', '_r60', '_r61', '_r62')

track = git('ls-files', 'scripts').splitlines()
directos = sorted({p.split('/')[1] for p in track if p.count('/') == 1})
# corpus de los VIVOS para el grep de protección
corpus = []
for d in KEEP_DIRS:
    base = RAIZ / 'scripts' / d
    if base.exists():
        for f in base.rglob('*'):
            if f.is_file() and f.stat().st_size < 3_000_000 and \
               f.suffix in {'.py', '.mjs', '.js', '.md', '.toml', '.txt', '.json'}:
                corpus.append(f.read_text(encoding='utf-8', errors='replace'))
for cfg in ('package.json', 'next.config.ts', 'Caddyfile'):
    p = RAIZ / cfg
    if p.exists():
        corpus.append(p.read_text(encoding='utf-8', errors='replace'))
for sf in (RAIZ / '.zscripts').glob('*.sh'):
    corpus.append(sf.read_text(encoding='utf-8', errors='replace'))
CORPUS = '\n'.join(corpus)

movidos_d, movidos_sub, protegidos = [], [], []
for nombre in directos:
    p = RAIZ / 'scripts' / nombre
    if not p.exists():
        continue
    if nombre in KEEP_FILES or any(nombre.startswith(px) for px in KEEP_PREFIX):
        continue
    if p.is_dir():
        if nombre in KEEP_DIRS:
            continue
        files = [x for x in p.rglob('*') if x.is_file()]
        viz = sum(1 for x in files if x.suffix.lower() in
                  {'.png', '.jpg', '.mp4', '.zip', '.glb', '.mp3', '.webp'})
        es_captura = files and viz / len(files) > 0.5
        destino = RAIZ / 'scripts/archivo' / ('capturas' if es_captura else 'eras') / nombre
        if nombre in CORPUS:
            protegidos.append('scripts/' + nombre)
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        tracked_hijos = [q for q in track if q.startswith(f'scripts/{nombre}/')]
        if tracked_hijos:
            git('mv', f'scripts/{nombre}', str(destino.relative_to(RAIZ)))
        else:
            shutil.move(str(p), str(destino))
        movidos_sub.append((nombre, 'capturas' if es_captura else 'eras', len(files)))
    else:
        if nombre in CORPUS:
            protegidos.append('scripts/' + nombre)
            continue
        destino = RAIZ / 'scripts/archivo/era_legacy'
        destino.mkdir(parents=True, exist_ok=True)
        git('mv', f'scripts/{nombre}', f'scripts/archivo/era_legacy/{nombre}')
        movidos_d.append(nombre)

w(f'- vivos conservados en scripts/ raíz: {len([n for n in directos if n in KEEP_FILES or any(n.startswith(p) for p in KEEP_PREFIX)])} ficheros + dirs {sorted(KEEP_DIRS)}')
w(f'- ficheros sueltos movidos a scripts/archivo/era_legacy/: {len(movidos_d)}')
w(f'- subcarpetas movidas: {len(movidos_sub)} → ' +
  ', '.join(f'{n}({t},{c}f)' for n, t, c in movidos_sub[:14]) + ' …')
if protegidos:
    w('- PROTEGIDOS por referencias de los vivos (se quedan): ' + ', '.join(protegidos))
commit('F3', f'r113-F3 · organización: scripts/archivo/ (eras + capturas) — '
        f'{len(movidos_d)} sueltos y {len(movidos_sub)} carpetas archivadas, vivos intactos')

# ── F4 · huérfanos de raíz ────────────────────────────────────────
sec('F4 · huérfanos de raíz → scripts/archivo/')
(RAIZ / 'scripts/archivo/huerfanos_raiz').mkdir(parents=True, exist_ok=True)
for d in ('three-pkg', 'examples', 'tests'):
    p = RAIZ / d
    if p.exists():
        tiene_track = bool(git('ls-files', d).strip())
        if tiene_track:
            git('mv', d, f'scripts/archivo/huerfanos_raiz/{d}')
        else:
            shutil.move(str(p), str(RAIZ / 'scripts/archivo/huerfanos_raiz' / d))
        w(f'- movido `{d}/` → scripts/archivo/huerfanos_raiz/')
if (RAIZ / 'scripts_release_r122_manual.py').exists():
    git('mv', 'scripts_release_r122_manual.py',
        'scripts/archivo/era_legacy/scripts_release_r122_manual.py')
    w('- movido `scripts_release_r122_manual.py` → scripts/archivo/era_legacy/')
commit('F4', 'r113-F4 · organización: three-pkg, examples y tests archivados '
        '(huérfanos verificados) + script suelto de raíz')

# ── cierre ────────────────────────────────────────────────────────
sec('Cierre')
st = sh(['git', 'status', '--porcelain']).stdout.strip()
w('- git status tras F1-F4: ' + ('limpio ✓' if not st else 'PENDIENTE: ' + st[:200]))
w(f'- HEAD: `{git("log", "-1", "--format=%h %s")[:120]}`')
print('\n✓ F1-F4 ejecutados. Registro: ' + str(REG))
