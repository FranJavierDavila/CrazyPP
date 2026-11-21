#!/usr/bin/env python3
"""analisis_fino_r113.py — segunda pasada del inventario r113:
  · desglose de scripts/ por subcarpeta + top ficheros grandes
  · ZIPs de raíz (bug del patrón en la pasada 1)
  · calidad de referencias de los medios de raíz (¿apuntan a public/ o a la raíz?)
  · contenido único vs duplicado de tmp_owner_backup/
  · referencias de three-pkg, db, examples, tests, mockups
  · batería/arnés: scripts vivos
  · tamaños de directorios SOLO LOCALES (no están en GitHub)
"""
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

RAIZ = Path('/home/z/my-project')
INV = json.loads((RAIZ / 'scripts/_inventario_r113.json').read_text())


def sh(cmd, timeout=300):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=RAIZ)
    return r.stdout


fich = {}   # path → bytes (tracked)
for line in sh(['git', 'ls-tree', '-r', '-l', 'main']).splitlines():
    meta, _, path = line.partition('\t')
    parts = meta.split()
    if len(parts) == 4 and parts[1] == 'blob':
        fich[path] = int(parts[3])
ultima = {}
fecha = None
for line in sh(['git', 'log', '--name-only', '--format=@%ad', '--date=short'],
               timeout=600).splitlines():
    if line.startswith('@'):
        fecha = line[1:]
    elif line.strip() and fecha:
        if line not in ultima or fecha > ultima[line]:
            ultima[line] = fecha

# ── A. scripts/ por subcarpeta de 2º nivel ────────────────────────
print('== A · scripts/ por subcarpeta (top 20 por tamaño) ==')
sub = defaultdict(lambda: [0, 0, '?', '?'])
for p, s in fich.items():
    partes = p.split('/')
    clave = '/'.join(partes[:2]) if len(partes) > 2 else '(scripts raíz)'
    sub[clave][0] += 1
    sub[clave][1] += s
    f = ultima.get(p, '?')
    if sub[clave][2] == '?' or f < sub[clave][2]:
        sub[clave][2] = f
    if sub[clave][3] == '?' or f > sub[clave][3]:
        sub[clave][3] = f
for clave, (n, s, fmin, fmax) in sorted(sub.items(), key=lambda x: -x[1][1])[:20]:
    print(f'  {clave:36s} {n:>5} {s/1e6:>8.2f} MB  {fmin}…{fmax}')

print('\n== A2 · los 25 ficheros TRACKED más grandes de todo main ==')
for p, s in sorted(fich.items(), key=lambda x: -x[1])[:25]:
    print(f'  {s/1e6:>8.2f} MB  {ultima.get(p, "?")}  {p}')

# ── B. ZIPs de raíz ───────────────────────────────────────────────
print('\n== B · ZIPs en raíz (trackeados) ==')
for p in sorted(f for f in fich if '/' not in f and f.endswith('.zip')):
    print(f'  {fich[p]/1e6:>8.2f} MB  {ultima.get(p, "?")}  {p}')

# ── C. calidad de referencias de medios de raíz ───────────────────
SCAN_DIRS = ['src', 'public', 'mini-services', 'scripts', 'docs', 'tests',
             'prisma', 'db', 'examples', 'mockups', '.zscripts', 'three-pkg']
SCAN_ROOT = ['package.json', 'next.config.ts', 'Caddyfile', '.gitignore',
             'tailwind.config.ts', 'mockups', 'docs']
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
for name in ('package.json', 'next.config.ts', 'Caddyfile', '.gitignore'):
    f = RAIZ / name
    if f.exists():
        textos[name] = f.read_text(encoding='utf-8', errors='replace')

raiz_media = [p for p in fich if '/' not in p and
              re.match(r'^[a-z_0-9]+\.(png|jpg|mp3|glb|ogg|webp|zip)$', p)]
print('\n== C · medios/ZIP de raíz: ¿quién los referencia y a QUÉ copia? ==')
resumen_c = {}
for p in sorted(raiz_media, key=lambda x: -fich[x]):
    base = p.split('/')[-1]
    a_public, a_raiz, donde = 0, [], []
    for nombre, txt in textos.items():
        if nombre == p or nombre == 'worklog.md':
            continue
        ini = 0
        while True:
            i = txt.find(base, ini)
            if i < 0:
                break
            contexto = txt[max(0, i - 40):i]
            if re.search(r'(assets/|championships/|public/|descargas/)\S*$', contexto) \
               or contexto.rstrip().endswith('/'):
                a_public += 1
            else:
                a_raiz.append(nombre)
            ini = i + len(base)
    etiqueta = 'SOLO copia public/ (la raíz es residuo)' if a_raiz == [] else \
        f'REFERENCIA DIRECTA: {a_raiz[:3]}'
    resumen_c[p] = {'a_public': a_public, 'a_raiz': a_raiz}
    print(f'  {p:32s} {fich[p]/1e6:>7.2f} MB  refs public={a_public:>3}  {etiqueta}')

# ── D. tmp_owner_backup: único vs duplicado ───────────────────────
print('\n== D · tmp_owner_backup/ (104 ficheros, 87.74 MB) ==')
hashes_otros = {}
for p, s in fich.items():
    if p.startswith('tmp_owner_backup') or s > 8_000_000:
        continue
    f = RAIZ / p
    if f.exists():
        hashes_otros[hashlib.sha256(f.read_bytes()).hexdigest()] = p
unicos, dupes_mb = [], 0
for p in sorted(f for f in fich if f.startswith('tmp_owner_backup')):
    f = RAIZ / p
    if not f.exists():
        continue
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    if h in hashes_otros:
        dupes_mb += fich[p]
    else:
        unicos.append((p, fich[p]))
print(f'  bytes duplicados (ya existen en el repo): {dupes_mb/1e6:.1f} MB')
print(f'  ficheros ÚNICOS (solo existen aquí): {len(unicos)}')
for p, s in sorted(unicos, key=lambda x: -x[1])[:12]:
    print(f'    ÚNICO {s/1e6:>7.2f} MB  {p}')

# ── E. referencias de carpetas dudosas ────────────────────────────
print('\n== E · referencias de three-pkg / db / examples / tests / mockups ==')
for objetivo in ('three-pkg/', 'db/custom.db', 'examples/', 'tests/',
                 'mockups/', '.zscripts', 'scripts_release_r122_manual.py'):
    menciones = []
    patron = objetivo.rstrip('/')
    for nombre, txt in textos.items():
        if nombre.startswith(patron) or nombre == 'worklog.md':
            continue
        if patron in txt:
            menciones.append(nombre)
    print(f'  {objetivo:34s} → {len(menciones)} menciones: {menciones[:4]}')

# ── F. batería / arnés / golden — scripts vivos ───────────────────
print('\n== F · scripts que la casa considera vivos (batería/arnés/golden/smoke) ==')
vivos = []
for p in fich:
    if not p.startswith('scripts/'):
        continue
    base = p.split('/')[-1].lower()
    if any(k in base for k in ('bateria', 'arnes', 'golden', 'smoke', 'bater')):
        vivos.append(p)
for p in sorted(vivos)[:20]:
    print(f'  {ultima.get(p, "?")}  {p}  ({fich[p]/1e3:.0f} KB)')

# ── G. directorios SOLO locales (no en GitHub) ────────────────────
print('\n== G · SOLO LOCALES (invisibles en GitHub) ==')
r = subprocess.run(['du', '-sm', 'scripts/staging-v36207', 'scripts/staging-v36209',
                    'scripts/staging-cloudflare', 'scripts/staging-champs-bak',
                    'pages-site', 'download', 'node_modules', '.next',
                    'tmp_frames', 'tool-results', 'skills'],
                   capture_output=True, text=True, cwd=RAIZ)
print(r.stdout.rstrip())
