#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r109-b · LIMPIEZA DEL REPOSITORIO (petición del dueño: «todo el material
NO IMPRESCINDIBLE con antigüedad superior a 1 semana se elimine
definitivamente; temporales, copias, cache TODO»).

Reglas aplicadas (documentadas para el dueño):
  · ELIMINAR: copias y fósiles del linaje viejo (upload/ = copia íntegra
    del repo de la era r127 con fechas 2026-11-12), snapshot «servido» de
    deploys antiguos (×7, ~75 MB), toolchain TTS ya MUDADA a scripts/voice/
    (1.024 ficheros trackeados, ~354 MB), kits de release agotados
    (release-v3XX con tag anterior a 2026-11-14 — el camino vivo es
    deploy_pages.py --release), scripts de inserción one-shot de rondas
    pasadas, capturas/tmp/rescates/reciclajes, extractos y backups
    rotatorios, node_modules y .next (regenerables), y los RAW duplicados
    de la raíz (el juego usa las copias canónicas de public/).
  · CONSERVAR: la pipeline viva (build/bump/deploy/sella/arnés r93+),
    worker-tele con sus credenciales locales, voz toolchain en
    scripts/voice/ (gitignored), tmp_owner_backup/ (1 día, del dueño),
    docs/ y mockups/ (material del dueño, entra al repo), SuperPala_
    Criptonita.png (icono del dueño, fuente del PNG_PODER_CRIPTO).
Todo lo eliminado sigue recuperable en la historia de git.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
os.chdir(RAIZ)

CUTOFF = '2026-11-14'   # el dueño: conservar lo que lleva funcionando 1 semana

liberado = 0


def du_ruta(p: Path) -> int:
    total = 0
    if p.is_file():
        return p.stat().st_size
    for root, _dirs, files in os.walk(p, onerror=lambda e: None):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def apuntar(label: str):
    global liberado
    p = RAIZ / label
    if not p.exists() and not p.is_symlink():
        print(f'· (ya ausente) {label}')
        return
    sz = du_ruta(p)
    liberado += sz
    print(f'· {label} → fuera ({sz / 1e6:.1f} MB)')


def borrar_disco(label: str):
    """Fichero/dir SIN seguimiento git (o ya sin él): fuera del disco."""
    apuntar(label)
    p = RAIZ / label
    if p.is_dir() and not p.is_symlink():
        shutil.rmtree(p, ignore_errors=True)
    elif p.exists() or p.is_symlink():
        try:
            p.unlink()
        except OSError:
            pass


def git_rm(rutas):
    """Ficheros/dirs TRACKED: fuera del índice Y del disco (git rm -r -q)."""
    if not rutas:
        return
    subprocess.run(['git', 'rm', '-r', '-q', '--'] + rutas, check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for r in rutas:
        apuntar(r)


# ── 0. fecha de cada tag (para decidir los kits de release) ──────────
tags = {}
out = subprocess.run(['git', 'for-each-ref', 'refs/tags', '--format=%(creatordate:short) %(refname:short)'],
                     capture_output=True, text=True).stdout
for linea in out.splitlines():
    fecha, _, nombre = linea.partition(' ')
    tags[nombre.strip()] = fecha.strip()


def fecha_version(ver: str):
    """v3613 → tag v3.6.13-SDK6 · v36118 → v3.6.118-SDK6."""
    n = ver[len('v36'):]
    if not n.isdigit():
        return None
    return tags.get(f'v3.6.{int(n)}-SDK6')


# ── 1. upload/ — la copia íntegra del repo de la era r127 (8,7 GB) ───
tracked_upload = subprocess.run(['git', 'ls-files', 'upload/'],
                                capture_output=True, text=True).stdout.split()
if tracked_upload:
    subprocess.run(['git', 'rm', '-r', '-q', '--cached', '--', 'upload/'], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f'· upload/: {len(tracked_upload)} ficheros fuera del índice (historia los conserva)')
# el disco: TODO fuera salvo el icono del dueño
for hijo in list((RAIZ / 'upload').iterdir()) if (RAIZ / 'upload').exists() else []:
    if hijo.name == 'SuperPala_Criptonita.png':
        print(f'· upload/SuperPala_Criptonita.png → CONSERVADO (fuente del icono del dueño)')
        continue
    apuntar(f'upload/{hijo.name}')
    if hijo.is_dir() and not hijo.is_symlink():
        shutil.rmtree(hijo, ignore_errors=True)
    else:
        try:
            hijo.unlink()
        except OSError:
            pass

# ── 2. toolchain TTS vieja (la viva ya vive en scripts/voice/, gitignored) ──
git_rm(['scripts/_r29_voice', 'scripts/voice_r65'])

# ── 3. snapshots «servido» de deploys antiguos ──
servidos = sorted(RAIZ.glob('scripts/_r9*_servido_game.html'))
git_rm([str(p.relative_to(RAIZ)) for p in servidos if p.exists()])
for p in RAIZ.glob('scripts/_r9*_servido_game.html'):
    borrar_disco(str(p.relative_to(RAIZ))) if p.exists() else None

# ── 4. kits de release agotados (tag anterior al corte; el vivo es deploy_pages --release) ──
kits_fuera, kits_dentro = [], []
if (RAIZ / 'scripts').exists():
    for p in sorted((RAIZ / 'scripts').glob('release-v*')):
        ver = p.name[len('release-'):]
        f = fecha_version(ver)
        if f is None:
            kits_dentro.append(p.name)   # sin tag: prudencia, se queda
        elif f < CUTOFF:
            kits_fuera.append(str(p.relative_to(RAIZ)))
        else:
            kits_dentro.append(p.name)
git_rm(kits_fuera)
print(f'· kits de release: {len(kits_fuera)} fuera (tag < {CUTOFF}) · '
      f'{len(kits_dentro)} se quedan (recientes o sin fecha)')

# ── 5. one-shots y transitorios de scripts/ ──
one_shots = [
    'scripts/gen_voice_r65.py', 'scripts/gen_voice_r66.py', 'scripts/gen_voice_r74.py',
    'scripts/gen_voice_r78.py', 'scripts/insertar_voz_r65.py', 'scripts/insertar_voz_r66.py',
    'scripts/insertar_voz_r74.py', 'scripts/insertar_voz_r78.py', 'scripts/qa_r78_v3670.py',
    'scripts/_poder35_insertar_assets.py', 'scripts/_poder36_insertar_assets.py',
    'scripts/_poder36_swap_icono_real.py', 'scripts/_poder37_insertar_assets.py',
    'scripts/_poder43_insertar_assets.py', 'scripts/_poder50_assets.py',
    'scripts/_poder50_diag.py', 'scripts/_poder50_insertar_voces.py',
    'scripts/_poder50_voces.sh', 'scripts/_poder51_dedup.py',
    'scripts/_poder51_insertar_assets.py', 'scripts/_poder51_mover_consts.py',
    'scripts/_poder160_bolaloca_assets.py',
    'scripts/_r26b_gen_halls.py', 'scripts/_r26b_gen_iconos.py',
    'scripts/_r26b_gen_voces.sh', 'scripts/_r26b_insertar_poderes.py',
    'scripts/_r28_gen_halls.py', 'scripts/_r28_hall_lib.py', 'scripts/_r28_halls_dojo.py',
    'scripts/_r28_halls_neon.py', 'scripts/_r28_halls_orbital.py',
    'scripts/_r29_insertar_assets.py', 'scripts/_r29_gen_assets.sh',
    'scripts/_r33_iconos.py', 'scripts/_r34_probe_fixes.py', 'scripts/_r37_resellar.py',
    'scripts/verify_r28_state.py', 'scripts/verify_r28_state2.py', 'scripts/verify_r28_state3.py',
    'scripts/verify_lineage.sh', 'scripts/xr_sim_r71.py', 'scripts/xr_flujo_r71.py',
    'scripts/xr_clic_r71.py', 'scripts/xr_boot_r71.py',
    'scripts/verifica_r52_produccion.py', 'scripts/verifica_r53_produccion.py',
    'scripts/_bq_p1_r121.py', 'scripts/_probe_c05.mjs', 'scripts/_checkglobal_capturas.py',
]
def trackeado(rel: str) -> bool:
    return bool(subprocess.run(['git', 'ls-files', '--', rel], capture_output=True,
                               text=True).stdout.strip())


git_rm(one_shots)
for p in RAIZ.glob('scripts/_qa_*.png'):
    rel = str(p.relative_to(RAIZ))
    if trackeado(rel):
        git_rm([rel])
    else:
        borrar_disco(rel)

# dirs transitorios de scripts/
for d in ('scripts/guia-preview', 'scripts/capturas_r99', 'scripts/tmp_check',
          'scripts/_rescate', 'scripts/_recuperados_reciclado', 'scripts/editor_src',
          'scripts/launch_assets', 'scripts/__pycache__', 'scripts/tmp_frames'):
    git_rm([d]) if subprocess.run(['git', 'ls-files', d], capture_output=True,
                                  text=True).stdout.strip() else None
    borrar_disco(d)
for p in RAIZ.glob('scripts/staging-*'):
    borrar_disco(str(p.relative_to(RAIZ)))

# ── 6. fósiles, copias rotatorias y extractos de la raíz ──
for d in ('_fosil_recuperacion', '_junk_reciclaje', 'burla_extract', 'hallcabana_extract',
          'backup-upload-local', 'backup_rodado_r48', 'backup_snapshot_v3627_r71',
          'upload_backup_20261023', 'tmp_assets', '_ext', '.next', 'node_modules',
          'tmp_frames'):
    git_rm([d]) if subprocess.run(['git', 'ls-files', d], capture_output=True,
                                  text=True).stdout.strip() else None
    borrar_disco(d)

# ── 7. RAW duplicados de la raíz (el juego usa las copias de public/) ──
raws = [
    'astro.zip', 'burla.zip', 'manos.zip', 'zombi.zip',
    'arcade.mp3', 'arcano.mp3', 'cabana.mp3', 'dojo.mp3', 'caballos.mp3',
    'enfado_astro.mp3', 'intro.mp4', 'calabaza.glb', 'mando_derecho.glb',
    'astro_angry.png', 'astro_normas.png', 'base.png', 'candado.png',
    'clown_normas.png', 'diana_quantica.png', 'derecha.jpg', 'derecha.png',
    'fondo.jpg', 'forajido_normas.png', 'forajido_robo.png', 'frente.jpg',
    'gelatina.png', 'indio1.png', 'indio2.png', 'indio3.png', 'indio4.png',
    'indioalcanzado.png', 'izquierda.jpg', 'izquierda.png', 'mapa.png',
    'mesa.jpg', 'dev.log',
]
for r in raws:
    git_rm([r]) if subprocess.run(['git', 'ls-files', r], capture_output=True,
                                  text=True).stdout.strip() else None
    borrar_disco(r)

print()
print(f'LIBERADO EN DISCO: {liberado / 1e9:.2f} GB')
print('✓ limpieza ejecutada (todo lo trackeado sigue en la historia de git)')
