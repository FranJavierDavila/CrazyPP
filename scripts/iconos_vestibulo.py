#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iconos_vestibulo.py — FASE 161 · r67 · SET DE ICONOS DEL VESTÍBULO.
16 iconos diseñados a mano en SVG (viewBox 96×96, rasterizados a 256 px con
cairosvg) bajo un sistema de diseño común «CRAZY ICONOS v1»:
  · glifo principal en trazo blanco (linecap/linejoin round, 5-6/96)
  · sub-trazo oscuro translúcido debajo (contraste sobre cualquier fondo)
  · acentos con degradado del color de su tarjeta (claro→oscuro)
  · brillo especular (elipse blanca translúcida arriba-izquierda)
  · remates de detalle por icono (remaches, laureles, costuras, chispas)
Salida: scripts/iconos_v67.json (registro base64 para ICONOS_MENUS en c02)
        download/iconos_vestibulo_hoja.png (hoja de contactos 4×4 para revisión)
"""
import base64
import json

import cairosvg
from PIL import Image
import io

OUT_JSON = '/home/z/my-project/upload/scripts/iconos_v67.json'
OUT_SHEET = '/home/z/my-project/download/iconos_vestibulo_hoja.png'

# paleta de acentos por icono (claro, oscuro) — casan con las tarjetas del hub
A = {
    'partido': ('#7dff92', '#1e9e3c'),
    'carrera': ('#ff7ad9', '#c4089b'),
    'academia': ('#ffcf5e', '#e07c00'),
    'entrenar': ('#74c6ff', '#0c60d6'),
    'supervivencia': ('#ff9a5e', '#d42a00'),
    'multijugador': ('#d29dff', '#7a1fd0'),
    'campeonatos': ('#ffe066', '#d88c00'),
    'ranking': ('#5ef0e4', '#0a8892'),
    'ajustes': ('#c4d2e6', '#5b6b85'),
    'arcano': ('#d9b3ff', '#8a4fd8'),
    'vestibulo': ('#b8c9e8', '#4a6288'),
    'salir': ('#d0dae8', '#6a7a94'),
    'tv': ('#7ac4ff', '#1868d8'),
    'intro': ('#ffe08a', '#e8a80e'),
    'instalar': ('#7ef2e6', '#0e9e9a'),
    'apoyar': ('#ffb3c8', '#e05580'),
}

DARK = 'rgba(0,0,0,0.45)'   # sub-trazo de contraste
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


def gfill(extra=''):
    return f'fill="url(#ac)" {extra}'


ICONS = {}

# — partido: pala diagonal roja con goma + bola con estela (héroe) —
ICONS['partido'] = svg(f'''
<g transform="rotate(38 48 48)">
 <rect x="41" y="64" width="9" height="26" rx="4" fill="{DARK}"/>
 <rect x="42.5" y="65" width="6" height="23" rx="3" fill="#b98356"/>
 <ellipse cx="46" cy="40" rx="23" ry="26" fill="{DARK}" transform="translate(2 3)"/>
 <ellipse cx="46" cy="40" rx="23" ry="26" fill="url(#ac)" stroke="rgba(0,0,0,0.5)" stroke-width="2"/>
 <ellipse cx="46" cy="40" rx="14" ry="17" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="2.5" stroke-dasharray="1 6"/>
 <ellipse cx="39" cy="29" rx="9" ry="6" fill="rgba(255,255,255,0.45)" transform="rotate(-18 39 29)"/>
</g>
<circle cx="72" cy="22" r="9" fill="{DARK}"/>
<circle cx="72" cy="22" r="9" fill="#ffffff" stroke="rgba(0,0,0,0.4)" stroke-width="1.5"/>
<path d="M 20 78 Q 34 84 52 80" fill="none" stroke="{WHITE}" stroke-width="3" stroke-dasharray="2 7" stroke-linecap="round"/>
''', A['partido'])

# — carrera: podio de 3 peldaños con escalera y estrella ascendente —
ICONS['carrera'] = svg(f'''
<g stroke-linecap="round" stroke-linejoin="round">
 <g stroke="{DARK}" stroke-width="7" fill="none">
  <path d="M 30 74 V 34 M 62 74 V 22 M 30 40 H 62 M 30 52 H 62 M 30 64 H 62"/>
 </g>
 <g stroke="{WHITE}" stroke-width="4.5" fill="none">
  <path d="M 30 74 V 34 M 62 74 V 22 M 30 40 H 62 M 30 52 H 62 M 30 64 H 62"/>
 </g>
</g>
<path d="M 66 12 l 2.6 5.4 6 .8 -4.4 4.2 1.1 5.9 -5.3 -2.8 -5.3 2.8 1.1 -5.9 -4.4 -4.2 6 -.8 z" {gfill('stroke="rgba(0,0,0,0.45)" stroke-width="1.5"')}/>
''', A['carrera'])

# — academia: birrete con borla + libro —
ICONS['academia'] = svg(f'''
<path d="M 48 26 L 82 41 L 48 56 L 14 41 Z" fill="{DARK}" transform="translate(2 3)"/>
<path d="M 48 26 L 82 41 L 48 56 L 14 41 Z" {gfill('stroke="rgba(0,0,0,0.45)" stroke-width="2"')}/>
<path d="M 30 48 V 62 Q 30 68 48 71 Q 66 68 66 62 V 48" fill="none" stroke="{WHITE}" stroke-width="4.5" stroke-linecap="round"/>
<line x1="76" y1="44" x2="76" y2="62" stroke="{WHITE}" stroke-width="3.5" stroke-linecap="round"/>
<circle cx="76" cy="66" r="4.5" {gfill()}/>
<rect x="26" y="74" width="30" height="9" rx="2.5" fill="none" stroke="{WHITE}" stroke-width="3.5"/>
<line x1="41" y1="74" x2="41" y2="83" stroke="{WHITE}" stroke-width="3"/>
''', A['academia'])

# — entrenar: diana de 3 aros con cruces y bola central —
ICONS['entrenar'] = svg(f'''
<g fill="none" stroke-linecap="round">
 <g stroke="{DARK}" stroke-width="7">
  <circle cx="48" cy="48" r="28"/><circle cx="48" cy="48" r="17"/>
 </g>
 <g stroke="{WHITE}" stroke-width="4.5">
  <circle cx="48" cy="48" r="28"/><circle cx="48" cy="48" r="17"/>
 </g>
 <g stroke="{WHITE}" stroke-width="3.5">
  <line x1="48" y1="12" x2="48" y2="22"/><line x1="48" y1="74" x2="48" y2="84"/>
  <line x1="12" y1="48" x2="22" y2="48"/><line x1="74" y1="48" x2="84" y2="48"/>
 </g>
</g>
<circle cx="48" cy="48" r="7.5" {gfill('stroke="rgba(0,0,0,0.45)" stroke-width="1.5"')}/>
<circle cx="45.5" cy="45.5" r="2.2" fill="rgba(255,255,255,0.8)"/>
''', A['entrenar'])

# — supervivencia: llama con núcleo y chispas —
ICONS['supervivencia'] = svg(f'''
<path d="M 48 14 Q 60 30 70 42 Q 78 52 74 64 Q 70 78 48 82 Q 26 78 22 64 Q 18 52 26 42 Q 34 32 40 22 Q 44 17 48 14 Z"
 fill="{DARK}" transform="translate(2 3)"/>
<path d="M 48 14 Q 60 30 70 42 Q 78 52 74 64 Q 70 78 48 82 Q 26 78 22 64 Q 18 52 26 42 Q 34 32 40 22 Q 44 17 48 14 Z"
 {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<path d="M 48 44 Q 56 54 58 61 Q 60 70 48 73 Q 36 70 38 61 Q 40 54 48 44 Z" fill="{WHITE}" opacity="0.92"/>
<path d="M 48 52 Q 52 58 53 62 Q 54 67 48 68 Q 42 67 43 62 Q 44 58 48 52 Z" fill="url(#ac)"/>
<circle cx="26" cy="22" r="3" fill="{WHITE}" opacity="0.85"/>
<circle cx="70" cy="18" r="2.2" fill="{WHITE}" opacity="0.7"/>
''', A['supervivencia'])

# — multijugador: dos palas cruzadas (rallye compartido) —
ICONS['multijugador'] = svg(f'''
<g transform="rotate(40 48 48)">
 <rect x="45" y="52" width="6" height="30" rx="3" fill="#b98356" stroke="{DARK}" stroke-width="1.5"/>
 <ellipse cx="48" cy="32" rx="17" ry="21" fill="url(#ac)" stroke="rgba(0,0,0,0.5)" stroke-width="2"/>
 <ellipse cx="48" cy="32" rx="9.5" ry="13" fill="none" stroke="rgba(255,255,255,0.55)" stroke-width="2" stroke-dasharray="1 5"/>
</g>
<g transform="rotate(-40 48 48)">
 <rect x="45" y="52" width="6" height="30" rx="3" fill="#b98356" stroke="{DARK}" stroke-width="1.5"/>
 <ellipse cx="48" cy="32" rx="17" ry="21" fill="url(#ac)" stroke="rgba(0,0,0,0.5)" stroke-width="2"/>
 <ellipse cx="48" cy="32" rx="9.5" ry="13" fill="none" stroke="rgba(255,255,255,0.55)" stroke-width="2" stroke-dasharray="1 5"/>
 <ellipse cx="43" cy="23" rx="6" ry="4" fill="rgba(255,255,255,0.4)" transform="rotate(-20 43 23)"/>
</g>
<circle cx="48" cy="80" r="6" fill="{WHITE}" stroke="rgba(0,0,0,0.4)" stroke-width="1.5"/>
''', A['multijugador'])

# — campeonatos: copa con asas, laureles y estrella —
ICONS['campeonatos'] = svg(f'''
<path d="M 34 22 H 62 V 40 Q 62 54 48 56 Q 34 54 34 40 Z" fill="{DARK}" transform="translate(2 3)"/>
<path d="M 34 22 H 62 V 40 Q 62 54 48 56 Q 34 54 34 40 Z" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<path d="M 34 26 Q 20 28 22 38 Q 23 46 34 46" fill="none" stroke="url(#ac)" stroke-width="4.5" stroke-linecap="round"/>
<path d="M 62 26 Q 76 28 74 38 Q 73 46 62 46" fill="none" stroke="url(#ac)" stroke-width="4.5" stroke-linecap="round"/>
<line x1="48" y1="56" x2="48" y2="66" stroke="{WHITE}" stroke-width="4.5" stroke-linecap="round"/>
<path d="M 36 70 H 60 L 63 78 H 33 Z" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="1.5"')}/>
<path d="M 48 30 l 2.4 4.9 5.4 .7 -4 3.8 1 5.3 -4.8 -2.5 -4.8 2.5 1 -5.3 -4 -3.8 5.4 -.7 z" fill="{WHITE}"/>
<g stroke="{WHITE}" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.9">
 <path d="M 16 62 Q 14 74 24 82"/><path d="M 80 62 Q 82 74 72 82"/>
</g>
<circle cx="17" cy="58" r="2.6" fill="{WHITE}"/><circle cx="79" cy="58" r="2.6" fill="{WHITE}"/>
''', A['campeonatos'])

# — ranking: globo con meridianos, bola orbitando y podio —
ICONS['ranking'] = svg(f'''
<g fill="none" stroke-linecap="round">
 <g stroke="{DARK}" stroke-width="7">
  <circle cx="48" cy="44" r="26"/><ellipse cx="48" cy="44" rx="11" ry="26"/>
  <line x1="22" y1="44" x2="74" y2="44"/>
 </g>
 <g stroke="{WHITE}" stroke-width="4.5">
  <circle cx="48" cy="44" r="26"/><ellipse cx="48" cy="44" rx="11" ry="26"/>
  <line x1="22" y1="44" x2="74" y2="44"/>
 </g>
 <g stroke="{WHITE}" stroke-width="3.5">
  <path d="M 28 28 Q 48 20 68 28"/><path d="M 28 60 Q 48 68 68 60"/>
 </g>
</g>
<g stroke-linejoin="round">
 <rect x="26" y="72" width="13" height="12" rx="2" fill="{DARK}"/>
 <rect x="41.5" y="64" width="13" height="20" rx="2" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="1.5"')}/>
 <rect x="57" y="70" width="13" height="14" rx="2" fill="{DARK}"/>
</g>
<circle cx="74" cy="20" r="7" fill="{WHITE}" stroke="rgba(0,0,0,0.4)" stroke-width="1.5"/>
''', A['ranking'])

# — ajustes: engranaje de 8 dientes con remaches —
ICONS['ajustes'] = svg(f'''
<g transform="translate(48 48)">
 <g {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="1.5"')}>
  <path transform="rotate(0)" d="M -8 -30 Q 0 -34 8 -30 L 8 -20 L -8 -20 Z"/>
  <path transform="rotate(45)" d="M -8 -30 Q 0 -34 8 -30 L 8 -20 L -8 -20 Z"/>
  <path transform="rotate(90)" d="M -8 -30 Q 0 -34 8 -30 L 8 -20 L -8 -20 Z"/>
  <path transform="rotate(135)" d="M -8 -30 Q 0 -34 8 -30 L 8 -20 L -8 -20 Z"/>
  <path transform="rotate(180)" d="M -8 -30 Q 0 -34 8 -30 L 8 -20 L -8 -20 Z"/>
  <path transform="rotate(225)" d="M -8 -30 Q 0 -34 8 -30 L 8 -20 L -8 -20 Z"/>
  <path transform="rotate(270)" d="M -8 -30 Q 0 -34 8 -30 L 8 -20 L -8 -20 Z"/>
  <path transform="rotate(315)" d="M -8 -30 Q 0 -34 8 -30 L 8 -20 L -8 -20 Z"/>
 </g>
 <circle r="24" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
 <circle r="15" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="2.5"/>
 <circle r="9" fill="rgba(10,16,34,0.9)" stroke="{WHITE}" stroke-width="3"/>
 <circle cx="0" cy="-17" r="1.8" fill="rgba(255,255,255,0.75)"/>
 <circle cx="15" cy="8.5" r="1.8" fill="rgba(255,255,255,0.75)"/>
 <circle cx="-15" cy="8.5" r="1.8" fill="rgba(255,255,255,0.75)"/>
</g>
''', A['ajustes'])

# — arcano: puerta en arco con estrella de 4 puntas y destellos —
ICONS['arcano'] = svg(f'''
<path d="M 30 78 V 42 Q 30 22 48 22 Q 66 22 66 42 V 78 Z" fill="{DARK}" transform="translate(2 3)"/>
<path d="M 30 78 V 42 Q 30 22 48 22 Q 66 22 66 42 V 78 Z" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<path d="M 36 74 V 44 Q 36 29 48 29 Q 60 29 60 44 V 74 Z" fill="rgba(10,16,34,0.55)" stroke="rgba(255,255,255,0.5)" stroke-width="2"/>
<path d="M 48 38 L 51.5 48.5 L 62 52 L 51.5 55.5 L 48 66 L 44.5 55.5 L 34 52 L 44.5 48.5 Z" fill="{WHITE}"/>
<circle cx="42" cy="34" r="2" fill="{WHITE}" opacity="0.9"/>
<circle cx="58" cy="62" r="2.4" fill="{WHITE}" opacity="0.8"/>
<circle cx="24" cy="26" r="2.6" fill="{WHITE}" opacity="0.7"/>
<circle cx="74" cy="72" r="2" fill="{WHITE}" opacity="0.6"/>
''', A['arcano'])

# — vestibulo: casita con puerta-pala y bola en el tejado —
ICONS['vestibulo'] = svg(f'''
<path d="M 20 46 L 48 20 L 76 46" fill="none" stroke="{DARK}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 20 46 L 48 20 L 76 46" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="27" y="46" width="42" height="30" rx="3" fill="{DARK}" transform="translate(2 2)"/>
<rect x="27" y="46" width="42" height="30" rx="3" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<g transform="rotate(8 48 62)">
 <rect x="44.5" y="66" width="6" height="10" rx="3" fill="#b98356" stroke="{DARK}" stroke-width="1.2"/>
 <ellipse cx="48" cy="58" rx="10.5" ry="11" fill="rgba(10,16,34,0.85)" stroke="{WHITE}" stroke-width="2.5"/>
</g>
<circle cx="48" cy="14" r="5" fill="{WHITE}" stroke="rgba(0,0,0,0.4)" stroke-width="1.4"/>
''', A['vestibulo'])

# — salir: puerta abierta con flecha hacia fuera —
ICONS['salir'] = svg(f'''
<rect x="20" y="22" width="30" height="52" rx="3" fill="{DARK}" transform="translate(2 2)"/>
<rect x="20" y="22" width="30" height="52" rx="3" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<circle cx="43" cy="50" r="3" fill="rgba(10,16,34,0.9)"/>
<g stroke-linecap="round" stroke-linejoin="round">
 <g stroke="{DARK}" stroke-width="8" fill="none">
  <line x1="52" y1="48" x2="78" y2="48"/><path d="M 68 38 L 78 48 L 68 58"/>
 </g>
 <g stroke="{WHITE}" stroke-width="5" fill="none">
  <line x1="52" y1="48" x2="78" y2="48"/><path d="M 68 38 L 78 48 L 68 58"/>
 </g>
</g>
''', A['salir'])

# — tv: televisor retro con antenas y play —
ICONS['tv'] = svg(f'''
<g stroke="{WHITE}" stroke-width="3.5" stroke-linecap="round">
 <line x1="38" y1="30" x2="28" y2="16"/><line x1="58" y1="30" x2="68" y2="16"/>
</g>
<rect x="18" y="30" width="60" height="44" rx="8" fill="{DARK}" transform="translate(2 2)"/>
<rect x="18" y="30" width="60" height="44" rx="8" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<rect x="25" y="37" width="38" height="30" rx="4" fill="rgba(10,16,34,0.75)" stroke="rgba(255,255,255,0.55)" stroke-width="2"/>
<path d="M 40 44 L 52 52 L 40 60 Z" fill="{WHITE}"/>
<circle cx="70" cy="42" r="2.4" fill="{WHITE}"/><circle cx="70" cy="50" r="2.4" fill="rgba(255,255,255,0.7)"/>
<line x1="62" y1="68" x2="72" y2="68" stroke="rgba(255,255,255,0.5)" stroke-width="3" stroke-linecap="round"/>
''', A['tv'])

# — intro: chispa de 4 puntas con estrellitas —
ICONS['intro'] = svg(f'''
<path d="M 48 16 C 51 34 54 38 72 44 C 54 50 51 54 48 76 C 45 54 42 50 24 44 C 42 38 45 34 48 16 Z"
 fill="{DARK}" transform="translate(2 3)"/>
<path d="M 48 16 C 51 34 54 38 72 44 C 54 50 51 54 48 76 C 45 54 42 50 24 44 C 42 38 45 34 48 16 Z"
 {gfill('stroke="rgba(0,0,0,0.35)" stroke-width="1.5"')}/>
<path d="M 72 62 C 73 68 74 69 80 71 C 74 73 73 74 72 80 C 71 74 70 73 64 71 C 70 69 71 68 72 62 Z" fill="{WHITE}"/>
<circle cx="26" cy="24" r="3" fill="{WHITE}" opacity="0.85"/>
<circle cx="76" cy="22" r="2.2" fill="{WHITE}" opacity="0.7"/>
''', A['intro'])

# — instalar: casco VR con flecha de descarga —
ICONS['instalar'] = svg(f'''
<g stroke-linecap="round" stroke-linejoin="round">
 <g stroke="{DARK}" stroke-width="8" fill="none">
  <line x1="48" y1="16" x2="48" y2="34"/><path d="M 40 28 L 48 36 L 56 28"/>
 </g>
 <g stroke="{WHITE}" stroke-width="5" fill="none">
  <line x1="48" y1="16" x2="48" y2="34"/><path d="M 40 28 L 48 36 L 56 28"/>
 </g>
</g>
<rect x="22" y="46" width="52" height="26" rx="12" fill="{DARK}" transform="translate(2 2)"/>
<rect x="22" y="46" width="52" height="26" rx="12" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<rect x="27" y="52" width="19" height="14" rx="6" fill="rgba(10,16,34,0.75)" stroke="rgba(255,255,255,0.5)" stroke-width="2"/>
<rect x="50" y="52" width="19" height="14" rx="6" fill="rgba(10,16,34,0.75)" stroke="rgba(255,255,255,0.5)" stroke-width="2"/>
<rect x="44" y="56" width="8" height="6" rx="2" fill="rgba(255,255,255,0.35)"/>
''', A['instalar'])

# — apoyar: taza de café con vapor en forma de corazón —
ICONS['apoyar'] = svg(f'''
<path d="M 40 24 Q 36 30 40 34 Q 44 38 40 44" fill="none" stroke="{WHITE}" stroke-width="3.5" stroke-linecap="round"/>
<path d="M 52 22 Q 48 28 52 32 Q 56 36 52 42" fill="none" stroke="{WHITE}" stroke-width="3.5" stroke-linecap="round"/>
<rect x="26" y="46" width="38" height="26" rx="6" fill="{DARK}" transform="translate(2 2)"/>
<rect x="26" y="46" width="38" height="26" rx="6" {gfill('stroke="rgba(0,0,0,0.4)" stroke-width="2"')}/>
<path d="M 64 50 Q 76 50 76 58 Q 76 66 64 66" fill="none" stroke="url(#ac)" stroke-width="4.5" stroke-linecap="round"/>
<path d="M 45 56 C 42 51 34 52 34 58 C 34 63 40 66 45 69 C 50 66 56 63 56 58 C 56 52 48 51 45 56 Z" fill="{WHITE}" opacity="0.95"/>
<rect x="22" y="74" width="48" height="6" rx="3" {gfill()}/>
''', A['apoyar'])

# — atras: chevron doble redondeado —
ICONS['atras'] = svg(f'''
<g fill="none" stroke-linecap="round" stroke-linejoin="round">
 <g stroke="{DARK}" stroke-width="9" opacity="0.55">
  <path d="M 54 24 L 30 48 L 54 72"/>
 </g>
 <g stroke="{WHITE}" stroke-width="6">
  <path d="M 54 24 L 30 48 L 54 72"/>
 </g>
 <g stroke="{WHITE}" stroke-width="4" opacity="0.55">
  <path d="M 68 32 L 50 48 L 68 64"/>
 </g>
</g>
''', A['salir'])

# — rasterizar todo (cuantización 64 colores, patrón de la casa r66) —
reg = {'version': 1, 'resolucion': 256, 'iconos': {}}
for name, src in ICONS.items():
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
    print(f'{name:14s} {len(png):7d} B png')

with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(reg, f, ensure_ascii=False)
total = sum(len(v['src']) for v in reg['iconos'].values())
print(f'REGISTRO: {len(reg["iconos"])} iconos · {total/1024:.0f} KB base64 → {OUT_JSON}')

# hoja de contactos 4×4 para revisión visual
names = list(ICONS.keys())
cell, pad = 200, 24
cols, rows = 4, (len(names) + 3) // 4
sheet = Image.new('RGBA', (cols * cell + (cols + 1) * pad,
                           rows * cell + (rows + 1) * pad), (10, 14, 32, 255))
for i, name in enumerate(names):
    png = base64.b64decode(reg['iconos'][name]['src'].split(',', 1)[1])
    im = Image.open(io.BytesIO(png))
    im = im.resize((cell, cell), Image.LANCZOS)
    x = pad + (i % cols) * (cell + pad)
    y = pad + (i // cols) * (cell + pad)
    sheet.alpha_composite(im, (x, y))
sheet.convert('RGB').save(OUT_SHEET, 'PNG')
print('HOJA:', OUT_SHEET, sheet.size)
