#!/usr/bin/env python3
"""Ensambla el manual del editor (V2.127) reutilizando el sistema visual de
la guía: toma de la guía los DOS bloques <style> (fuentes + diseño), pega el
body_manual.html y añade un ajuste de paleta propio del manual.
Salida: download/manual-editor-campeonatos.html (HTML autónomo)."""
import re, sys

GUIA = '/home/z/my-project/download/guia-campeonatos-crazy-pingpong.html'
BODY = '/home/z/my-project/scripts/manual_editor_src/body_manual.html'
OUT  = '/home/z/my-project/download/manual-editor-campeonatos.html'

guia = open(GUIA, encoding='utf-8').read()
bloques = re.findall(r'<style>(.*?)</style>', guia, re.S)
assert len(bloques) == 2, f'esperaba 2 bloques style, hay {len(bloques)}'
fuentes, diseno = bloques

body = open(BODY, encoding='utf-8').read()
if 'A开机' in body:
    sys.exit('body contiene texto basura — regenerar')

extra_css = '''
<style>
/* Ajustes propios del manual (mismo sistema visual que la guía) */
.s-body h4{ font-size:16.5px; font-weight:800; color:var(--c-blue); margin-bottom:4px; }
.s-body p{ margin:0; font-size:14.6px; line-height:1.55; }
.s-num{ flex-shrink:0; width:34px; height:34px; border-radius:50%; background:var(--c-orange);
  color:#fff; font-weight:900; display:flex; align-items:center; justify-content:center; }
.s-card h4{ font-size:16px; font-weight:800; color:var(--c-blue); }
.s-card p{ margin:2px 0 0 0; font-size:14.4px; line-height:1.5; }
.check li{ position:relative; padding-left:26px; margin-bottom:8px; font-size:14.6px; line-height:1.5; }
.check li::before{ content:'✔'; position:absolute; left:0; top:0; color:var(--c-orange); font-weight:900; }
.mini-list li{ position:relative; padding-left:22px; margin-bottom:6px; font-size:14.6px; line-height:1.5; }
.mini-list li::before{ content:'▸'; position:absolute; left:2px; color:var(--c-orange); font-weight:900; }
.f-node{ font-size:12.5px; font-weight:800; color:var(--c-blue); line-height:1.25; padding:9px 6px; }
.f-arrow{ color:var(--c-orange); font-weight:900; }
.two-col{ break-inside:avoid; }
.two-col .card{ flex:1; margin-bottom:0; }
.two-col{ margin-bottom:13px; }
h4{ font-size:16px; }
</style>
'''

html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>CRAZY PING PONG · Manual del editor de campeonatos · V2.127</title>
<style>{fuentes}</style>
<style>{diseno}</style>
{extra_css}
</head>
<body>
{body}
</body>
</html>
'''
open(OUT, 'w', encoding='utf-8').write(html)
import os
print(f'OK → {OUT} ({os.path.getsize(OUT):,} B)')
print('V2.127:', html.count('V2.127'), '| V2.127:', html.count('V2.127'), '| Estación Orbital:', html.count('Estación Orbital'))
