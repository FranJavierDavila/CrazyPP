#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""split_editor.py — inverso de build_editor.py: recupera las piezas de
scripts/editor_src/ desde un index.html ensamblado (anti-rollback V2.128).

El ensamblado es: head con @@STYLE@@/@@BODY@@/@@APP1@@…@@APP3@@ sustituidos.
La inversión localiza cada marcador de PIEZA por sus cabeceras características
y reescribe los ficheros fuente con la versión V2.128.
"""
import pathlib, sys

SRC = pathlib.Path('/home/z/my-project/scripts/editor_src')
html_path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/editor128/index.html')
s = html_path.read_text(encoding='utf-8')

# --- localización por anclas estables (mismas cabeceras de las piezas) -----
def between(a, b, fallback_len=10**9):
    i = s.find(a)
    if i < 0:
        sys.exit(f'ancla no encontrada: {a[:60]}')
    j = s.find(b, i + len(a))
    if j < 0:
        sys.exit(f'ancla final no encontrada: {b[:60]}')
    return i, j

# style.css vive donde estaba @@STYLE@@; body entre @@BODY@@ y @@APP1@@…
# Recorremos el head real: el ensamblado conserva las líneas del head.html
# con los tokens ya sustituidos, así que usamos anclas del contenido.
i_style = s.find('/* ======  HOJA DE ESTILOS')
if i_style < 0:
    # fallback: primer <style> del documento
    i_style = s.find('<style>') + len('<style>')
j_style = s.find('</style>', i_style)

i_body = s.find('<!-- ======  PANTALLAS')
if i_body < 0:
    i_body = s.find('<body') + len('<body>')
    i_body = s.find('>', i_body) + 1
# body termina donde empieza el primer <script> de aplicación
j_body = s.find('<script>', i_body)

# app1/app2/app3: scripts seguidos al final
scripts = []
pos = j_body
while True:
    a = s.find('<script>', pos)
    if a < 0:
        break
    b = s.find('</script>', a)
    scripts.append((a + len('<script>'), b))
    pos = b + 1

parts = {
    'style.css': s[i_style:j_style].lstrip('\n'),
    'body.html': s[i_body:j_body].rstrip('\n'),
}
labels = ['app1.js', 'app2.js', 'app3.js']
for (a, b), name in zip(scripts, labels):
    parts[name] = s[a:b].strip('\n')

for name, content in parts.items():
    p = SRC / name
    old = p.read_text(encoding='utf-8') if p.exists() else ''
    p.write_text(content + '\n', encoding='utf-8')
    print(f'{name}: {len(old):,} → {len(content):,} chars')
print('editor_src restaurado a', html_path)
