#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extracción ROBUSTA de claves: TODOS los literales de cadena dentro de T(...)
con paréntesis balanceados + claves dinámicas prefix_N verificadas."""
import re, io

C00 = '/home/z/my-project/src/game/core/c00_pre_three.js'
FILES = {
    'c08': '/home/z/my-project/src/game/core/c08_hall_hud.js',
    'c13': '/home/z/my-project/src/game/core/c13_ui_arranque.js',
    'c10': '/home/z/my-project/src/game/core/c10_menu_saque.js',
}

src = io.open(C00, encoding='utf-8').read()
lines = src.split('\n')
es_start = next(i for i, l in enumerate(lines) if l.strip() == 'es: {')
en_start = next(i for i, l in enumerate(lines) if l.strip() == 'en: {')

def block_keys(start, end):
    keys = set()
    for i in range(start, end):
        m = re.match(r"^    ([A-Za-z0-9_]+):\s*", lines[i])
        if m:
            keys.add(m.group(1))
    return keys

en_end = en_start
for i in range(en_start, len(lines)):
    if lines[i].startswith('  },'):
        en_end = i; break
ES = block_keys(es_start, en_start)
EN = block_keys(en_start, en_end)
ALL = ES | EN
print(f"es={len(ES)} en={len(EN)} union={len(ALL)}")

QSTR = re.compile(r"""(['"])((?:\\.|(?!\1).)*)\1""")

def calls_in(path):
    txt = io.open(path, encoding='utf-8').read()
    res = []
    for m in re.finditer(r"(?<![A-Za-z0-9_$])T\s*\(", txt):
        ln = txt[:m.start()].count('\n') + 1
        # balancear paréntesis desde el '('
        depth = 0; j = m.end() - 1; end = None
        while j < len(txt):
            c = txt[j]
            if c == '(': depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0: end = j; break
            elif c in '\'"`':
                q = c; j += 1
                while j < len(txt) and txt[j] != q:
                    if txt[j] == '\\': j += 1
                    j += 1
            j += 1
        if end is None: continue
        inner = txt[m.end():end]
        strs = [q.group(2) for q in QSTR.finditer(inner)]
        res.append((ln, inner.strip()[:90], strs))
    return res

missing, dyn = [], []
for name, path in FILES.items():
    for ln, inner, strs in calls_in(path):
        if not strs:
            dyn.append((name, ln, inner)); continue
        statics = [s for s in strs if re.fullmatch(r"[A-Za-z0-9_]+", s)]
        joined = ' + '.join(inner.split())[:90]
        # si hay concatenación con '+', las partes estáticas son prefijos
        if '+' in re.sub(r"'[^']*'|\"[^\"]*\"", '', inner):
            for s in strs:
                if re.fullmatch(r"[A-Za-z0-9_]+", s):
                    matches = [k for k in ALL if k.startswith(s)]
                    if not matches:
                        missing.append((name, ln, f"prefijo '{s}*' sin coincidencias", joined))
                    else:
                        dyn.append((name, ln, f"prefijo '{s}*' -> {matches[:14]}"))
        else:
            for s in statics:
                if s not in ALL:
                    missing.append((name, ln, f"clave '{s}' NO existe", joined))

print("\n== ESTÁTICAS FALTANTES ==")
for x in missing: print(" ", x)
print("\n== DINÁMICAS ==")
seen = set()
for name, ln, info in dyn:
    kk = (name, info[:60])
    if kk in seen: continue
    seen.add(kk)
    print(f"  {name}:{ln}  {info[:120]}")
