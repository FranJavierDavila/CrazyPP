#!/usr/bin/env python3
"""Auditoría mecánica del juego — fase 1 (estática).
  A · sintaxis por fichero (node --check sobre copias .mjs)
  B · imports cross-file: cada nombre importado debe existir como declaración
      top-level en el fichero exportador (los imports se STRIPPEAN al construir)
  C · colisiones de declaraciones top-level entre los 14 subsistemas
      (comparten un ÚNICO ámbito en game.html)
  D · externales (three, io…) que el bundle debe proveer
  E · rutas de assets referenciadas vs ficheros reales en public/
      (GitHub Pages es case-sensitive: una mayúscula equivocada = 404 en vivo)
Salida: resumen en consola + informe completo en scripts/auditoria_mecanica_informe.txt
"""
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src' / 'game'
CORE = SRC / 'core'
PUB = RAIZ / 'public'
INFO = RAIZ / 'scripts' / 'auditoria_mecanica_informe.txt'

ORDER = ['c00_pre_three.js', 'c01_modelos_3d.js', 'c02_cfg_escena.js', 'c03_audio_voz.js',
         'c04_fisica_ccd.js', 'c05_colisiones_ia_golpeo.js', 'c06_logros_stats_ia_rival.js',
         'c07_escena_sala.js', 'c08_hall_hud.js', 'c09_red_netlink.js', 'c09b_red_nucleo.js',
         'c09c_red_social.js', 'c10_menu_saque.js', 'c11_champloader.js', 'c12_pingponggame.js',
         'c13_ui_arranque.js']

RE_DECL = re.compile(r'^(?:export\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+([A-Za-z_$][\w$]*)')
RE_IMPORT = re.compile(r"^import\s+(?:\{([^}]*)\}|(?:\*\s+as\s+([A-Za-z_$][\w$]*))|([A-Za-z_$][\w$]*))\s+from\s+['\"]([^'\"]+)['\"]")
RE_PATH = re.compile(r"['\"]([^'\"\n]{3,200}?\.(?:glb|gltf|mp3|ogg|wav|png|jpe?g|webp|gif|mp4|json|js|css|html|webmanifest|wasm))['\"]", re.I)

problemas = []   # (severidad, zona, mensaje)
out = []

def log(s=''):
    out.append(s)

# ── carga de ficheros core ──
texto = {}
for n in ORDER:
    texto[n] = (CORE / n).read_text(encoding='utf-8', errors='replace')

# ── A · sintaxis por fichero ──
log('=== A · SINTAXIS POR FICHERO (node --check como .mjs) ===')
tmp = Path('/tmp/audit_check.mjs')
for n in ORDER:
    tmp.write_text(texto[n], encoding='utf-8')
    r = subprocess.run(['node', '--check', str(tmp)], capture_output=True, text=True)
    if r.returncode != 0:
        problemas.append(('ALTO', f'sintaxis {n}', r.stderr.strip()[:400]))
        log(f'  ✗ {n}: {r.stderr.strip()[:200]}')
    else:
        log(f'  ✓ {n}')

# ── B/C · declaraciones top-level e imports ──
log('')
log('=== B · IMPORTS CROSS-FILE (nombre importado ∈ declaraciones del exportador) ===')
decls = {}   # fichero -> set nombres
for n in ORDER:
    d = set()
    for m in re.finditer(r'(?m)^(?:export\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+([A-Za-z_$][\w$]*)', texto[n]):
        d.add(m.group(1))
    decls[n] = d

por_nombre = {}
for n in ORDER:
    for x in decls[n]:
        por_nombre.setdefault(x, []).append(n)

ext_names = {}   # nombre externo -> lista de ficheros que lo importan
for n in ORDER:
    for m in RE_IMPORT.finditer(texto[n]):
        nombres = [x.strip() for x in (m.group(1).split(',') if m.group(1) else []) if x.strip()]
        nombres = [re.sub(r'\s+as\s+.*$', '', x).strip() for x in nombres]
        spec = m.group(4)
        if spec.startswith('.'):
            destino = 'core/' + Path(spec).name
            if destino not in {f'core/{x}' for x in ORDER}:
                problemas.append(('ALTO', f'import {n}', f'objetivo inexistente {spec}'))
                continue
            dset = decls[Path(destino).name]
            faltan = [x for x in nombres if x and x not in dset]
            if faltan:
                problemas.append(('ALTO', f'import {n} ← {destino}', f'NO declarado en el exportador: {", ".join(faltan)}'))
                log(f'  ✗ {n} importa de {destino} lo que no existe: {faltan}')
        else:
            for x in (nombres or [m.group(2) or m.group(3)]):
                if x:
                    ext_names.setdefault(x, []).append(n)

log(f'  imports cross-file revisados — problemas: '
    f'{sum(1 for s, z, _ in problemas if z.startswith("import"))}')

log('')
log('=== C · COLISIONES DE DECLARACIONES TOP-LEVEL (ámbito compartido único) ===')
dup = {x: fs for x, fs in por_nombre.items() if len(fs) > 1}
if dup:
    for x, fs in sorted(dup.items()):
        problemas.append(('MEDIO', 'colisión top-level',
                          f'{x} declarado en: {", ".join(sorted(fs))}'))
    log(f'  {len(dup)} nombres duplicados (ver informe)')
else:
    log('  ✓ sin duplicados')

log('')
log('=== D · EXTERNALES que el bundle debe proveer ===')
for x, fs in sorted(ext_names.items()):
    dónde = ''
    for n in ORDER:  # ¿existe como decl top-level en algún fichero?
        if x in decls[n]:
            dónde = n
            break
    if dónde:
        log(f'  ✓ {x} ← importado por {len(fs)} ficheros · provisto por {dónde}')
    else:
        problemas.append(('ALTO', 'externo sin proveedor',
                          f'{x} importado por {", ".join(fs)} y NO declarado top-level en ningún core/*.js'))
        log(f'  ✗ {x}: importado por {fs} · NO declarado top-level en core/')

# ── E · assets ──
log('')
log('=== E · ASSETS REFERENCIADOS vs public/ (case-sensitive) ===')
reales = {}
for p in PUB.rglob('*'):
    if p.is_file():
        rel = str(p.relative_to(PUB))
        reales[rel] = True
        reales.setdefault(rel.lower(), []).append(rel) if isinstance(reales.get(rel.lower()), list) else None
bajo = {}
for p in PUB.rglob('*'):
    if p.is_file():
        bajo.setdefault(str(p.relative_to(PUB)).lower(), str(p.relative_to(PUB)))

vistas = set()
for n in ORDER:
    for m in RE_PATH.finditer(texto[n]):
        ruta = m.group(1)
        if ruta.startswith(('data:', 'http', 'blob:', '#', 'canvas')) or ruta in vistas:
            continue
        vistas.add(ruta)
        limpia = ruta.split('?')[0].split('#')[0]
        if limpia.startswith('../'):
            problemas.append(('MEDIO', f'asset {n}', f'ruta ../ fuera de public/: {ruta}'))
            continue
        limpia = limpia.lstrip('./')
        if limpia in reales:
            continue
        baja = limpia.lower()
        if baja in bajo:
            problemas.append(('ALTO', f'asset {n}', f'CASO DISTINTO: código pide «{ruta}» · existe «{bajo[baja]}» → 404 en GitHub Pages'))
            log(f'  ✗ {n}: {ruta} ≠ {bajo[baja]}')
        else:
            problemas.append(('ALTO', f'asset {n}', f'NO EXISTE en public/: {ruta}'))
            log(f'  ✗ {n}: {ruta} no existe')

log(f'  rutas únicas revisadas: {len(vistas)}')

# ── informe ──
log('')
log('=== PROBLEMAS (%d) ===' % len(problemas))
sev_ord = {'ALTO': 0, 'MEDIO': 1, 'BAJO': 2}
for s, z, m in sorted(problemas, key=lambda p: sev_ord.get(p[0], 3)):
    log(f'[{s}] {z}: {m}')

INFO.write_text('\n'.join(out), encoding='utf-8')
altos = sum(1 for s, _, _ in problemas if s == 'ALTO')
print(f'problemas: {len(problemas)} (ALTO: {altos}) · informe completo: {INFO.name}')
for s, z, m in sorted(problemas, key=lambda p: sev_ord.get(p[0], 3))[:25]:
    print(f'[{s}] {z}: {m[:160]}')
sys.exit(0)
