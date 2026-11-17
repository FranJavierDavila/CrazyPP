#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación 3: iconos embebidos (data URIs) + voces + Oscuridad spec en c12."""
import re, json, base64, hashlib, os

ROOT = '/home/z/my-project/upload'
c12 = open(os.path.join(ROOT, 'src/game/core/c12_pingponggame.js'),
           encoding='utf-8', errors='replace').read()
out = {}

# 1) data URIs embebidos y sus longitudes cerca de PNG_PODER_*
defs = re.findall(r"PNG_PODER_(FENIX|CRONO|OSCURIDAD|MEGA|EFECTO|IMAN|RED|ELECTRICA|PORTAL|CRECE)\s*=\s*(data:image/png;base64,[A-Za-z0-9+/=]+|'[^']*\.png')", c12)
resumen = {}
for nombre, val in defs:
    if val.startswith('data:'):
        b64 = val.split(',', 1)[1]
        try:
            raw = base64.b64decode(b64[:64] + '===' * 3)  # sólo cabecera
            hdr = raw[:8].hex()
        except Exception:
            hdr = 'ERR'
        resumen[nombre] = f'dataURI {len(b64)//1024}KB hdr={hdr[:16]}'
    else:
        resumen[nombre] = val
out['iconos'] = resumen

# 2) voces: buscar referencias a mp3/voz en los tres poderes
for poder in ('fenix', 'crono', 'oscuridad'):
    idx = [m.start() for m in re.finditer(poder, c12, re.I)][:60]
    snippets = set()
    for i in idx:
        chunk = c12[max(0, i-200):i+200]
        for m in re.finditer(r'[A-Za-z0-9_/.-]*voz[A-Za-z0-9_/.-]*|súper\s+\w+|SÚPER\s+\w+', chunk, re.I):
            snippets.add(m.group(0)[:60])
    out[f'voz_ctx_{poder}'] = sorted(snippets)[:8]

# 3) Oscuridad: constantes clave de la spec
for pat in ['OSCURIDAD_S', 'OSCURIDAD_DUR', 'OSCURIDAD_VIDA', 'OSCURIDAD_RADIO',
            'OSCURIDAD_ZONA', '_oscuridadZonas', '_oscuridadTick', '0.35', '20 *']:
    out[f'osc[{pat}]'] = len(re.findall(re.escape(pat), c12))

# 4) Crono: anillos hijos de ballMesh
m = re.search(r'anillos?[^;\n]{0,120}ballMesh|ballMesh\.add\(grupoAnillos|addChild.*anillo', c12, re.I)
out['crono_anillos_hijos'] = bool(m)
out['CRONO'] = sorted(set(re.findall(r'CRONO_[A-Z_]+', c12)))[:10]

print(json.dumps(out, ensure_ascii=False, indent=1))
