#!/usr/bin/env python3
"""inventario_limpieza_r113.py — inventario TRACKED de main y pages para la
propuesta de organización del repositorio (r113). SOLO ANALIZA: no borra,
no mueve, no escribe en el repo.

Fuentes:
  · git ls-tree -r -l main   → tamaño de cada blob trackeado
  · git log --name-only      → fecha de último commit por fichero (1 pasada)
  · git ls-tree -r pages     → contenido de la rama desplegada
  · grep sobre ficheros ACTIVOS → quién referencia cada candidato
Salida: resumen por pantalla + scripts/_inventario_r113.json
"""
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

RAIZ = Path('/home/z/my-project')
OUT_JSON = RAIZ / 'scripts/_inventario_r113.json'


def sh(cmd, timeout=300):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=RAIZ)
    if r.returncode != 0:
        sys_exit(f'fallo {cmd[0]}: {r.stderr[:200]}')
    return r.stdout


def sys_exit(msg):
    raise SystemExit(f'✗ {msg}')


# ── 1. ficheros trackeados + tamaños ──────────────────────────────
ficheros = {}          # path → tamaño (bytes)
for line in sh(['git', 'ls-tree', '-r', '-l', 'main']).splitlines():
    meta, _, path = line.partition('\t')
    parts = meta.split()
    if len(parts) == 4 and parts[1] == 'blob':
        ficheros[path] = int(parts[3])

total = sum(ficheros.values())
print(f'== 1 · TOTALES main ==\n  ficheros trackeados: {len(ficheros)} · '
      f'tamaño blobs: {total/1e6:.1f} MB')

# ── 2. fecha de último commit por fichero (una pasada) ────────────
ultima = {}
for line in sh(['git', 'log', '--name-only', '--format=@%ad', '--date=short'],
               timeout=600).splitlines():
    if line.startswith('@'):
        fecha = line[1:]
    elif line.strip() and fecha:
        if line not in ultima or fecha > ultima[line]:
            ultima[line] = fecha
print(f'  mapa de fechas: {len(ultima)} ficheros con historia')

# ── 3. tamaños por carpeta de primer nivel ────────────────────────
por_carpeta = defaultdict(lambda: [0, 0])
for p, s in ficheros.items():
    top = p.split('/')[0] if '/' in p else '(raíz)'
    por_carpeta[top][0] += 1
    por_carpeta[top][1] += s
print('\n== 2 · CARPETAS PRIMER NIVEL (orden por tamaño) ==')
for top, (n, s) in sorted(por_carpeta.items(), key=lambda x: -x[1][1]):
    print(f'  {top:22s} {n:>5} ficheros {s/1e6:>9.2f} MB')

# ── 4. candidatos a revisión ──────────────────────────────────────
CAND_PATRONES = [
    (re.compile(r'^pasted_image_\d+\.png$'), 'imagen pegada en chat (residuo)'),
    (re.compile(r'^tmp_'), 'temporal (prefijo tmp_)'),
    (re.compile(r'\.zip$'), 'ZIP en raíz (paquete de era antigua)'),
]
RAIZ_MEDIA = re.compile(
    r'^[a-z_0-9]+\.(png|jpg|mp3|glb|ogg|webp)$')   # medios sueltos en raíz
CAND_ACTIVOS_SCRIPTS = re.compile(
    r'^(deploy_pages|limpieza_github|backup_completo|check_live_service|'
    r'test_r112_live_service|test_worker_r169|actualiza_kit_relay_r112|'
    r'completa_assets_r112|inventario_limpieza_r113|diag_tele_produccion|'
    r'probe_tele_prod|alerta_telemetria)\.')
ONEOFF_SCRIPTS = re.compile(
    r'^(gen_leeme_v|gen_release_v|fix_release_assets|_r\d|auditoria|informe|'
    r'reporte|rep_|arregla|parcha|verifica_r|test_r(?:\d)0?\d*(?:_|\.))')
cand_raiz, scripts_all = [], []
for p in ficheros:
    base = p.split('/')[-1]
    if '/' not in p:
        if any(rx.match(base) for rx, _ in CAND_PATRONES) or RAIZ_MEDIA.match(base):
            cand_raiz.append(p)
    if p.startswith('scripts/'):
        scripts_all.append(p)
print(f'\n== 3 · CANDIDATOS EN RAÍZ: {len(cand_raiz)} · scripts/: {len(scripts_all)} ==')

# ── 5. escaneo de referencias activas ─────────────────────────────
SCAN_DIRS = ['src', 'public', 'mini-services', 'scripts', 'docs', 'tests',
             'prisma', 'db', 'examples', 'mockups', '.zscripts', 'three-pkg']
SCAN_ROOT = ['package.json', 'next.config.ts', 'Caddyfile', '.gitignore',
             'tailwind.config.ts', 'tsconfig.json', 'components.json',
             'eslint.config.mjs', 'postcss.config.mjs', 'worklog.md']
textos = {}
for d in SCAN_DIRS:
    base = RAIZ / d
    if not base.exists():
        continue
    for f in base.rglob('*'):
        if f.is_file() and f.stat().st_size < 3_000_000 and \
           f.suffix in {'.js', '.mjs', '.ts', '.tsx', '.json', '.md', '.txt',
                        '.html', '.py', '.toml', '.css', '.webmanifest'}:
            try:
                textos[str(f.relative_to(RAIZ))] = f.read_text(
                    encoding='utf-8', errors='replace')
            except Exception:
                pass
for name in SCAN_ROOT:
    f = RAIZ / name
    if f.exists() and f.stat().st_size < 3_000_000:
        textos[name] = f.read_text(encoding='utf-8', errors='replace')
print(f'  corpus de referencia: {len(textos)} ficheros de texto activos')

referencias = defaultdict(list)   # basename → [ficheros que lo mencionan]
for nombre, txt in textos.items():
    for p in cand_raiz:
        base = p.split('/')[-1]
        if nombre == p:
            continue
        if base in txt:
            referencias[base].append(nombre)


def refs_de(path):
    base = path.split('/')[-1]
    fuera = [r for r in referencias.get(base, []) if r != 'worklog.md']
    return fuera, base in referencias


print('\n== 4 · CANDIDATOS RAÍZ: tamaño · fecha · referencias activas ==')
detalle_raiz = []
for p in sorted(cand_raiz, key=lambda x: -ficheros[x]):
    activas, en_worklog = refs_de(p)
    tag = 'REFERENCIADO' if activas else 'SIN REFERENCIA'
    detalle_raiz.append({'fichero': p, 'bytes': ficheros[p],
                         'fecha': ultima.get(p, '?'), 'refs': activas,
                         'solo_worklog': en_worklog and not activas})
    print(f'  {tag:14s} {p:38s} {ficheros[p]/1e6:>7.2f} MB  {ultima.get(p, "?")}')

# ── 6. scripts/: clasificación ────────────────────────────────────
oneoff = [p for p in scripts_all
          if p != 'scripts/' and ONEOFF_SCRIPTS.match(p.split('/')[-1])
          and not CAND_ACTIVOS_SCRIPTS.match(p.split('/')[-1])]
keep_scripts = [p for p in scripts_all if p.split('/')[-1].count('.') and
                CAND_ACTIVOS_SCRIPTS.match(p.split('/')[-1])]
otros_scripts = [p for p in scripts_all if p not in oneoff and
                 p not in keep_scripts]
print(f'\n== 5 · SCRIPTS/ ==\n  total: {len(scripts_all)} ficheros')
for nombre, lista in (('activos identificados', keep_scripts),
                      ('one-off (patrón de era antigua)', oneoff),
                      ('resto (kits, worker-tele, LEEME…)', otros_scripts)):
    mb = sum(ficheros[p] for p in lista) / 1e6
    print(f'  {nombre}: {len(lista)} · {mb:.1f} MB')

# ── 7. duplicados byte-exactos (ficheros < 8 MB, fuera de public/assets grandes)
hashes = defaultdict(list)
for p, s in ficheros.items():
    if s < 8_000_000:
        f = RAIZ / p
        if f.exists():
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            hashes[h].append(p)
dupes = [v for v in hashes.values() if len(v) > 1]
print(f'\n== 6 · DUPLICADOS BYTE-EXACTOS: {len(dupes)} grupos ==')
for grupo in dupes[:15]:
    g = sorted(grupo, key=lambda x: -ficheros[x])
    print(f'  {ficheros[g[0]]/1e6:>7.2f} MB  ' + '  ⧉  '.join(g[:4]) +
          (' …' if len(g) > 4 else ''))

# ── 8. carpetas dudosas: resumen ─────────────────────────────────
print('\n== 7 · CARPETAS DUDOSAS ==')
for d in ('docs', 'examples', 'mockups', '.zscripts', 'three-pkg', 'db',
          'tests', 'tmp_owner_backup', 'mini-services', 'prisma'):
    lista = sorted(p for p in ficheros if p == d or p.startswith(d + '/'))
    if not lista:
        print(f'  {d}: NO trackeada')
        continue
    mb = sum(ficheros[p] for p in lista) / 1e6
    fechas = sorted(ultima.get(p, '?') for p in lista)
    print(f'  {d:18s} {len(lista):>4} ficheros {mb:>8.2f} MB  '
          f'fechas {fechas[0]} … {fechas[-1]}  ej: {lista[0]}')

# ── 9. rama pages ─────────────────────────────────────────────────
pages_files = [l.split('\t')[-1] for l in
               sh(['git', 'ls-tree', '-r', 'pages', '--name-only']).splitlines()]
print(f'\n== 8 · RAMA PAGES ==\n  ficheros: {len(pages_files)}')
top_pages = defaultdict(int)
for p in pages_files:
    top_pages[p.split('/')[0] if '/' in p else '(raíz)'] += 1
print('  ' + ' · '.join(f'{k}:{v}' for k, v in
                         sorted(top_pages.items(), key=lambda x: -x[1])[:10]))

# ── 10. JSON ──────────────────────────────────────────────────────
OUT_JSON.write_text(json.dumps({
    'total_ficheros': len(ficheros), 'total_bytes': total,
    'por_carpeta': {k: v for k, v in por_carpeta.items()},
    'candidatos_raiz': detalle_raiz,
    'scripts': {'total': len(scripts_all), 'oneoff': oneoff,
                'activos': keep_scripts, 'otros': otros_scripts[:80]},
    'dupes': dupes,
    'pages_n': len(pages_files),
}, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'\n✓ JSON: {OUT_JSON}')
