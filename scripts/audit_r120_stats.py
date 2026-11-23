#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_r120_stats.py — métricas mecánicas del juego CrazyPP (SOLO LECTURA).

Mide, sin modificar nada:
  1 · núcleo src/game/core/*.js: tamaño, carga base64 (líneas gigantes),
      funciones, marcadores de deuda (TODO/FIXME/HACK), console.*, catch vacíos,
      temporizadores, allocaciones `new THREE.`, DOM/innerHTML/eval, localStorage.
  2 · artefacto public/game.html: composición aprox. (base64 embebido vs código).
  3 · public/: peso por extensión, ficheros más pesados y duplicados byte-exactos.
  4 · src/ (Next): módulos de juego del andamio inicial — ¿se importan desde algún sitio?
  5 · dependencias de package.json sin ningún import en src/.

Uso: python3 scripts/audit_r120_stats.py [sección]
"""
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

RAIZ = '/home/z/my-project'
CORE = os.path.join(RAIZ, 'src/game/core')
SECC = sys.argv[1] if len(sys.argv) > 1 else 'todo'


def kb(n):
    return '%.1f KB' % (n / 1024.0)


def mb(n):
    return '%.2f MB' % (n / 1048576.0)


# ── 1 · núcleo ───────────────────────────────────────────────────────────
PATRONES = [
    ('funciones', re.compile(r'^\s*(?:async\s+)?function\s+\w+|^\s{2,}(?:async\s+)?[A-Za-z_]\w*\s*\([^)]*\)\s*\{\s*$|=>')),
    ('TODO/FIXME/HACK', re.compile(r'\b(TODO|FIXME|HACK|XXX)\b')),
    ('console.*', re.compile(r'\bconsole\.(log|warn|error|debug|info)\s*\(')),
    ('catch {} vacío', re.compile(r'catch\s*(\([^)]*\))?\s*\{\s*\}')),
    ('setTimeout/Interval', re.compile(r'\bset(Timeout|Interval)\s*\(')),
    ('new THREE.', re.compile(r'new\s+THREE\.')),
    ('innerHTML/outerHTML', re.compile(r'\.(innerHTML|outerHTML|insertAdjacentHTML)\b')),
    ('eval/Function', re.compile(r'\beval\s*\(|new\s+Function\s*\(')),
    ('localStorage', re.compile(r'\blocalStorage\b')),
    ('try {', re.compile(r'\btry\s*\{')),
]


def nucleo():
    print('=' * 100)
    print('1 · NÚCLEO src/game/core/*.js')
    print('=' * 100)
    filas = []
    tot = Counter()
    for f in sorted(os.listdir(CORE)):
        p = os.path.join(CORE, f)
        if not os.path.isfile(p) or not f.endswith(('.js', '.pre_r83')):
            continue
        txt = open(p, encoding='utf-8', errors='replace').read()
        lineas = txt.split('\n')
        b64 = sum(len(l) for l in lineas if len(l) > 5000)
        c = Counter()
        for nombre, rx in PATRONES:
            c[nombre] = len(rx.findall(txt))
        pre = f.endswith('.pre_r83')
        filas.append((f, len(lineas), len(txt.encode()), b64, c, pre))
        if not pre:
            tot['lineas'] += len(lineas)
            tot['bytes'] += len(txt.encode())
            tot['b64'] += b64
            for k, v in c.items():
                tot[k] += v
    print('%-30s %7s %10s %11s %5s %5s %6s %5s %5s %6s %5s %5s %5s' % (
        'fichero', 'líneas', 'bytes', 'base64', 'func', 'deuda', 'consol', 'catch0',
        'timer', 'newTH', 'html', 'eval', 'ls'))
    for f, n, b, b64, c, pre in filas:
        print('%-30s %7d %10s %11s %5d %5d %6d %5d %5d %6d %5d %5d %5d%s' % (
            f, n, kb(b), kb(b64), c['funciones'], c['TODO/FIXME/HACK'], c['console.*'],
            c['catch {} vacío'], c['setTimeout/Interval'], c['new THREE.'],
            c['innerHTML/outerHTML'], c['eval/Function'], c['localStorage'],
            '   (copia de respaldo .pre_r83)' if pre else ''))
    print('-' * 100)
    print('VIVO (sin .pre_r83): %d líneas · %s · del cual base64 embebido %s (%.0f%%)' % (
        tot['lineas'], mb(tot['bytes']), mb(tot['b64']),
        100.0 * tot['b64'] / max(tot['bytes'], 1)))
    for k, _ in PATRONES:
        print('   %-20s %d' % (k, tot[k]))
    resp = sum(n for f, n, b, b64, c, pre in filas if pre)
    print('COPIAS .pre_r83 dentro de src/game/core: %d líneas (%d ficheros)' % (
        resp, sum(1 for x in filas if x[5])))


# ── 2 · artefacto ────────────────────────────────────────────────────────
def artefacto():
    print()
    print('=' * 100)
    print('2 · ARTEFACTO public/game.html')
    print('=' * 100)
    p = os.path.join(RAIZ, 'public/game.html')
    txt = open(p, encoding='utf-8', errors='replace').read()
    n = len(txt.encode())
    lineas = txt.split('\n')
    gigantes = [l for l in lineas if len(l) > 5000]
    b64 = sum(len(l.encode()) for l in gigantes)
    print('bytes totales: %s (%d) · líneas: %d · líneas >5.000 car.: %d' % (mb(n), n, len(lineas), len(gigantes)))
    print('bytes en líneas gigantes (payload embebido): %s (%.0f%%)' % (mb(b64), 100.0 * b64 / n))
    clases = Counter()
    for l in gigantes:
        m = re.search(r'(?:const|let|var)\s+([A-Za-z_]\w*)', l[:400])
        nom = m.group(1) if m else '?'
        tipo = 'otro'
        if re.search(r'glb|model|pala|pistola|mang[oa]|GLTF', nom, re.I):
            tipo = 'modelo 3D (GLB)'
        elif re.search(r'VOZ|voz|mp3|ogg|wav|audio|AUDIO', nom, re.I):
            tipo = 'audio'
        elif l.lstrip().startswith('data:image') or re.search(r'png|jpg|webp|img|logo|textur', nom, re.I):
            tipo = 'imagen'
        clases[tipo] += len(l.encode())
    for t, b in clases.most_common():
        print('   %-22s %s (%.0f%% del fichero)' % (t, mb(b), 100.0 * b / n))
    # recursos externos que el HTML referencia
    urls = set(re.findall(r'["\'](/[A-Za-z0-9_\-./]+\.(?:js|css|png|jpg|jpeg|webp|glb|gltf|mp3|ogg|wav|json|webmanifest))["\']', txt))
    cdn = set(re.findall(r'https?://[A-Za-z0-9.\-]+', txt))
    print('URLs locales distintas referenciadas: %d · hosts externos: %s' % (len(urls), sorted(cdn)[:12]))


# ── 3 · public/ ──────────────────────────────────────────────────────────
def publico():
    print()
    print('=' * 100)
    print('3 · public/ (lo que descarga el visor)')
    print('=' * 100)
    por_ext = Counter()
    cnt_ext = Counter()
    hashes = defaultdict(list)
    todos = []
    for d, _, fs in os.walk(os.path.join(RAIZ, 'public')):
        for f in fs:
            p = os.path.join(d, f)
            b = os.path.getsize(p)
            ext = f.rsplit('.', 1)[-1].lower() if '.' in f else '(sin)'
            por_ext[ext] += b
            cnt_ext[ext] += 1
            todos.append((b, os.path.relpath(p, RAIZ)))
            if b > 20000:
                hashes[hashlib.sha256(open(p, 'rb').read()).hexdigest()].append(os.path.relpath(p, RAIZ))
    total = sum(por_ext.values())
    print('total: %s en %d ficheros' % (mb(total), len(todos)))
    print('--- por extensión ---')
    for ext, b in por_ext.most_common(18):
        print('   .%-10s %10s  %4d ficheros' % (ext, mb(b), cnt_ext[ext]))
    print('--- 20 más pesados ---')
    for b, rel in sorted(todos, reverse=True)[:20]:
        print('   %10s  %s' % (kb(b), rel))
    dup = [(h, v) for h, v in hashes.items() if len(v) > 1]
    perdido = sum(os.path.getsize(os.path.join(RAIZ, v[0])) * (len(v) - 1) for _, v in dup)
    print('--- duplicados byte-exactos (>20 KB): %d grupos · %s redundantes ---' % (len(dup), mb(perdido)))
    for h, v in sorted(dup, key=lambda x: -len(x[1]))[:12]:
        print('   x%d  %s (%s cada uno)' % (len(v), v[0], kb(os.path.getsize(os.path.join(RAIZ, v[0])))))
    sub = Counter()
    for b, rel in todos:
        partes = rel.split(os.sep)
        clave = os.sep.join(partes[:3]) if len(partes) > 3 else os.sep.join(partes[:2])
        sub[clave] += b
    print('--- peso por carpeta (top 14) ---')
    for k, b in sub.most_common(14):
        print('   %10s  %s' % (mb(b), k))


# ── 4 · andamio inicial ──────────────────────────────────────────────────
def andamio():
    print()
    print('=' * 100)
    print('4 · src/lib/game/*.ts y ping-pong-canvas.tsx (motor del andamio inicial)')
    print('=' * 100)
    mods = [os.path.join(RAIZ, 'src/lib/game', f) for f in sorted(os.listdir(os.path.join(RAIZ, 'src/lib/game')))]
    mods.append(os.path.join(RAIZ, 'src/components/ping-pong-canvas.tsx'))
    fuentes = []
    for d, _, fs in os.walk(os.path.join(RAIZ, 'src')):
        for f in fs:
            if f.endswith(('.ts', '.tsx')):
                fuentes.append(os.path.join(d, f))
    for m in mods:
        nombre = os.path.splitext(os.path.basename(m))[0]
        importadores = []
        for f in fuentes:
            if f == m:
                continue
            txt = open(f, encoding='utf-8', errors='replace').read()
            if re.search(r"""from\s+['"][^'"]*/%s['"]""" % re.escape(nombre), txt):
                importadores.append(os.path.relpath(f, RAIZ))
        print('   %-24s %4d líneas  importado por: %s' % (
            nombre, len(open(m, encoding='utf-8').read().split('\n')), importadores or 'NADIE'))
    print('src/app/page.tsx:')
    for l in open(os.path.join(RAIZ, 'src/app/page.tsx'), encoding='utf-8').read().split('\n'):
        print('   | ' + l)


# ── 5 · dependencias ─────────────────────────────────────────────────────
def deps():
    print()
    print('=' * 100)
    print('5 · dependencias de package.json')
    print('=' * 100)
    pk = json.load(open(os.path.join(RAIZ, 'package.json')))
    cuerpo = ''
    for d, _, fs in os.walk(os.path.join(RAIZ, 'src')):
        for f in fs:
            if f.endswith(('.ts', '.tsx', '.js', '.mjs', '.css')):
                cuerpo += open(os.path.join(d, f), encoding='utf-8', errors='replace').read()
    mini = ''
    md = os.path.join(RAIZ, 'mini-services/live-service')
    for f in os.listdir(md):
        if f.endswith(('.ts', '.mjs', '.js')):
            mini += open(os.path.join(md, f), encoding='utf-8', errors='replace').read()
    sin = []
    for dep in sorted(pk['dependencies']):
        rx = re.compile(r"""['"]%s(/|['"])""" % re.escape(dep))
        donde = []
        if rx.search(cuerpo):
            donde.append('src')
        if rx.search(mini):
            donde.append('mini-services')
        if re.search(r'\bnext-intl\b', dep) and 'next-intl' in cuerpo:
            donde.append('src(cfg)')
        if not donde:
            sin.append(dep)
    print('dependencias de producción: %d · sin ningún import en src/ ni mini-services/: %d' % (
        len(pk['dependencies']), len(sin)))
    print('   ' + ', '.join(sin))
    print('scripts npm: ' + ', '.join(sorted(pk['scripts'])))
    for lk in ('package-lock.json', 'bun.lock', 'yarn.lock', 'pnpm-lock.yaml', 'bun.lockb'):
        p = os.path.join(RAIZ, lk)
        if os.path.exists(p):
            print('lockfile en disco: %-18s %s' % (lk, kb(os.path.getsize(p))))


if SECC in ('todo', '1'):
    nucleo()
if SECC in ('todo', '2'):
    artefacto()
if SECC in ('todo', '3'):
    publico()
if SECC in ('todo', '4'):
    andamio()
if SECC in ('todo', '5'):
    deps()
