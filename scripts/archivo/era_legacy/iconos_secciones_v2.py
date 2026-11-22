#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iconos_secciones_v2.py — FASE 162 · r68 · AMPLIACIÓN DEL SET.
7 iconos nuevos del sistema «CRAZY ICONOS v1» (mismo contrato que
iconos_vestibulo.py) para los subapartados rediseñados:
  audio (altavoz con ondas) · ojo (visuales) · usuario (perfil) ·
  gauge (rendimiento) · consola (gamepad/juego) · plus (crear sala) ·
  entrar (puerta con flecha hacia dentro / unirse).
Fusiona con iconos_v67.json → iconos_v68.json (24 iconos)."""
import base64
import io
import json

import cairosvg
from PIL import Image

BASE = '/home/z/my-project/upload/scripts/'
OUT = BASE + 'iconos_v68.json'

A = {
    'audio': ('#9fb6ff', '#3f5ed8'),
    'ojo': ('#7ef0c8', '#0a9e78'),
    'usuario': ('#8ecfff', '#1f6fd0'),
    'gauge': ('#ffd25e', '#e07c00'),
    'consola': ('#c9a3ff', '#6a35d8'),
    'plus': ('#8dff9e', '#1e9e3c'),
    'entrar': ('#ffc98a', '#d8720e'),
}
DARK = 'rgba(0,0,0,0.45)'
WHITE = '#ffffff'


def svg(body, accent):
    hi, lo = accent
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">
<defs>
 <linearGradient id="ac" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{hi}"/><stop offset="1" stop-color="{lo}"/>
 </linearGradient>
 <radialGradient id="disc" cx="0.5" cy="0.42" r="0.62">
  <stop offset="0" stop-color="rgba(255,255,255,0.16)"/>
  <stop offset="1" stop-color="rgba(0,0,0,0.30)"/>
 </radialGradient>
</defs>
<circle cx="48" cy="48" r="45" fill="url(#disc)"
        stroke="rgba(255,255,255,0.55)" stroke-width="2.5"/>
<ellipse cx="38" cy="26" rx="22" ry="10" fill="rgba(255,255,255,0.20)"/>
{body}
</svg>'''


def gf(extra=''):
    return f'fill="url(#ac)" {extra}'


NUEVOS = {}

# — audio: altavoz con dos ondas y tornillos —
NUEVOS['audio'] = svg(f'''
<path d="M 22 40 H 34 L 50 26 V 70 L 34 56 H 22 Z" fill="{DARK}" transform="translate(2 3)"/>
<path d="M 22 40 H 34 L 50 26 V 70 L 34 56 H 22 Z" {gf('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<rect x="26" y="42" width="8" height="12" rx="2" fill="rgba(10,16,34,0.55)"/>
<path d="M 58 36 Q 66 48 58 60" fill="none" stroke="{DARK}" stroke-width="7" stroke-linecap="round"/>
<path d="M 58 36 Q 66 48 58 60" fill="none" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>
<path d="M 68 28 Q 80 48 68 68" fill="none" stroke="{DARK}" stroke-width="7" stroke-linecap="round"/>
<path d="M 68 28 Q 80 48 68 68" fill="none" stroke="url(#ac)" stroke-width="4" stroke-linecap="round"/>
<circle cx="34" cy="70" r="2.2" fill="rgba(255,255,255,0.8)"/>
''', A['audio'])

# — ojo: visuales (pupila con brillo + pestañas de rayos) —
NUEVOS['ojo'] = svg(f'''
<path d="M 16 48 Q 48 20 80 48 Q 48 76 16 48 Z" fill="{DARK}" transform="translate(2 3)"/>
<path d="M 16 48 Q 48 20 80 48 Q 48 76 16 48 Z" {gf('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<circle cx="48" cy="48" r="13" fill="rgba(10,16,34,0.92)" stroke="{WHITE}" stroke-width="3"/>
<circle cx="48" cy="48" r="5.5" fill="{WHITE}"/>
<circle cx="44" cy="44" r="2.2" fill="rgba(255,255,255,0.9)"/>
<g stroke="{WHITE}" stroke-width="3" stroke-linecap="round" opacity="0.85">
 <line x1="48" y1="16" x2="48" y2="24"/><line x1="26" y1="24" x2="31" y2="30"/>
 <line x1="70" y1="24" x2="65" y2="30"/>
</g>
''', A['ojo'])

# — usuario: perfil (cabeza + hombros + aro de estado) —
NUEVOS['usuario'] = svg(f'''
<circle cx="48" cy="38" r="14" fill="{DARK}" transform="translate(2 3)"/>
<circle cx="48" cy="38" r="14" {gf('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<circle cx="43.5" cy="34" r="4" fill="rgba(255,255,255,0.4)"/>
<path d="M 22 76 Q 24 56 48 56 Q 72 56 74 76 Q 48 84 22 76 Z" fill="{DARK}" transform="translate(2 2)"/>
<path d="M 22 76 Q 24 56 48 56 Q 72 56 74 76 Q 48 84 22 76 Z" {gf('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<circle cx="70" cy="30" r="7" fill="#5ef08a" stroke="{WHITE}" stroke-width="2.5"/>
''', A['usuario'])

# — gauge: rendimiento (velocímetro con aguja y arco de color) —
NUEVOS['gauge'] = svg(f'''
<path d="M 20 62 A 30 30 0 1 1 76 62" fill="none" stroke="{DARK}" stroke-width="9" stroke-linecap="round"/>
<path d="M 20 62 A 30 30 0 1 1 76 62" fill="none" stroke="url(#ac)" stroke-width="5.5" stroke-linecap="round"/>
<path d="M 30 62 A 20 20 0 1 1 66 62" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="2.5" stroke-dasharray="2 6"/>
<line x1="48" y1="62" x2="64" y2="40" stroke="{WHITE}" stroke-width="4.5" stroke-linecap="round"/>
<circle cx="48" cy="62" r="6" {gf('stroke="rgba(0,0,0,0.4)" stroke-width="1.5"')}/>
<circle cx="48" cy="62" r="2.2" fill="rgba(10,16,34,0.9)"/>
<rect x="38" y="72" width="20" height="7" rx="3.5" fill="{DARK}"/>
<rect x="41" y="73.5" width="14" height="4" rx="2" fill="{WHITE}" opacity="0.85"/>
''', A['gauge'])

# — consola: gamepad (juego) —
NUEVOS['consola'] = svg(f'''
<rect x="16" y="32" width="64" height="34" rx="17" fill="{DARK}" transform="translate(2 3)"/>
<rect x="16" y="32" width="64" height="34" rx="17" {gf('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<line x1="28" y1="49" x2="40" y2="49" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>
<line x1="34" y1="43" x2="34" y2="55" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>
<circle cx="62" cy="43" r="3.2" fill="{WHITE}"/>
<circle cx="70" cy="50" r="3.2" fill="rgba(255,255,255,0.75)"/>
<circle cx="54" cy="50" r="3.2" fill="rgba(255,255,255,0.75)"/>
<circle cx="62" cy="57" r="3.2" fill="rgba(255,255,255,0.75)"/>
''', A['consola'])

# — plus: crear sala —
NUEVOS['plus'] = svg(f'''
<g stroke-linecap="round">
 <g stroke="{DARK}" stroke-width="11"><line x1="48" y1="24" x2="48" y2="72"/><line x1="24" y1="48" x2="72" y2="48"/></g>
 <g stroke="{WHITE}" stroke-width="7"><line x1="48" y1="24" x2="48" y2="72"/><line x1="24" y1="48" x2="72" y2="48"/></g>
</g>
<circle cx="72" cy="24" r="5" fill="url(#ac)" opacity="0.9"/>
<circle cx="24" cy="72" r="3.5" fill="{WHITE}" opacity="0.7"/>
''', A['plus'])

# — entrar: puerta con flecha hacia dentro (unirse) —
NUEVOS['entrar'] = svg(f'''
<rect x="20" y="22" width="30" height="52" rx="3" fill="{DARK}" transform="translate(2 2)"/>
<rect x="20" y="22" width="30" height="52" rx="3" {gf('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<circle cx="43" cy="50" r="3" fill="rgba(10,16,34,0.9)"/>
<g stroke-linecap="round" stroke-linejoin="round">
 <g stroke="{DARK}" stroke-width="8" fill="none">
  <line x1="78" y1="48" x2="54" y2="48"/><path d="M 62 38 L 52 48 L 62 58"/>
 </g>
 <g stroke="{WHITE}" stroke-width="5" fill="none">
  <line x1="78" y1="48" x2="54" y2="48"/><path d="M 62 38 L 52 48 L 62 58"/>
 </g>
</g>
''', A['entrar'])

reg = json.loads(open(BASE + 'iconos_v67.json', encoding='utf-8').read())
reg['version'] = 2
for name, src in NUEVOS.items():
    png = cairosvg.svg2png(bytestring=src.encode('utf-8'),
                           output_width=256, output_height=256)
    im = Image.open(io.BytesIO(png)).convert('RGBA')
    im = im.quantize(colors=64, method=Image.FASTOCTREE).convert('RGBA')
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    png = buf.getvalue()
    reg['iconos'][name] = {
        'src': 'data:image/png;base64,' + base64.b64encode(png).decode(),
        'escala': 1.0,
    }
    print(f'{name:10s} {len(png):7d} B png')

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(reg, f, ensure_ascii=False)
total = sum(len(v['src']) for v in reg['iconos'].values())
print(f'REGISTRO v2: {len(reg["iconos"])} iconos · {total/1024:.0f} KB → {OUT}')
