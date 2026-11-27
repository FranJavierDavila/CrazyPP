#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auditoría T(): extrae claves de I18N_STRINGS (es/en) en c00 y TODOS los
usos T('...') y data-i18n* en c08/c10/c13; compara y lista faltantes."""
import re, io, sys

C00 = '/home/z/my-project/src/game/core/c00_pre_three.js'
FILES = {
    'c08': '/home/z/my-project/src/game/core/c08_hall_hud.js',
    'c10': '/home/z/my-project/src/game/core/c10_menu_saque.js',
    'c13': '/home/z/my-project/src/game/core/c13_ui_arranque.js',
}

src = io.open(C00, encoding='utf-8').read()
lines = src.split('\n')

# --- límites de bloques es/en -------------------------------------------------
es_start = next(i for i, l in enumerate(lines) if l.strip() == 'es: {')
en_start = next(i for i, l in enumerate(lines) if l.strip() == 'en: {')

def block_keys(start, end):
    """claves `key: 'value'` a nivel 1 del bloque (indent 4 espacios)."""
    keys = {}
    for i in range(start, end):
        m = re.match(r"^    ([A-Za-z0-9_]+):\s*", lines[i])
        if m:
            keys[m.group(1)] = i + 1
    return keys

# fin del bloque en: buscar la línea `},` al nivel 2 que cierra en:
en_end = en_start
for i in range(en_start, len(lines)):
    if lines[i].startswith('  },'):
        en_end = i
        break
es_end = en_start

es_keys = block_keys(es_start, es_end)
en_keys = block_keys(en_start, en_end)

print(f"es: {len(es_keys)} claves (líneas {es_start+1}-{es_end})")
print(f"en: {len(en_keys)} claves (líneas {en_start+1}-{en_end})")

only_es = sorted(set(es_keys) - set(en_keys))
only_en = sorted(set(en_keys) - set(es_keys))
print("\n== claves SOLO en es (fallará en en, cae a fallback es => sale en español) ==")
for k in only_es:
    print(f"  {k}  (es@{es_keys[k]})")
print("\n== claves SOLO en en (huérfanas, nunca se pintan) ==")
for k in only_en:
    print(f"  {k}  (en@{en_keys[k]})")

# --- usos T('...') en c08/c10/c13 ---------------------------------------------
def used_keys(path):
    txt = io.open(path, encoding='utf-8').read()
    out = []
    for m in re.finditer(r"\bT\(\s*['\"`]([^'\"`]+)['\"`]", txt):
        ln = txt[:m.start()].count('\n') + 1
        out.append((m.group(1), ln))
    # claves dinámicas data-i18n en HTML generado
    for m in re.finditer(r"data-i18n(?:-html|-ph|-title)?[=\s]+['\"`]([^'\"`]+)['\"`]", txt):
        ln = txt[:m.start()].count('\n') + 1
        out.append((m.group(1), ln, 'data-i18n'))
    return out

missing = {}
dyn = {}
for name, path in FILES.items():
    for u in used_keys(path):
        key = u[0]
        if key in es_keys:
            continue
        missing.setdefault(key, []).append((name, u[1], u[2] if len(u) > 2 else 'T()'))

print("\n== CLAVES USADAS EN C08/C10/C13 Y AUSENTES EN I18N (pintan clave cruda) ==")
for k in sorted(missing):
    print(f"  {k}  <- {missing[k]}")

# --- dinámicas: T('prefix_'+x) y T('diff_'...) --------------------------------
print("\n== usos dinámicos (prefijo concatenado) ==")
for name, path in FILES.items():
    txt = io.open(path, encoding='utf-8').read()
    for m in re.finditer(r"\bT\(\s*['\"`]([A-Za-z0-9_]+)['\"`]\s*\+", txt):
        ln = txt[:m.start()].count('\n') + 1
        print(f"  {name}:{ln}  T('{m.group(1)}' + ...)")
    for m in re.finditer(r"T\(([^'\")][^)]*)\)", txt):
        arg = m.group(1).strip()
        if arg.startswith("'") or arg.startswith('"') or arg.startswith('`'):
            continue
        ln = txt[:m.start()].count('\n') + 1
        if 'T(' in arg or arg in ('key',):
            continue
        print(f"  [VAR] {name}:{ln}  T({arg[:70]})")
