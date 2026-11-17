#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación integral del estado r28/r29/r30 (una sola pasada por archivo)."""
import hashlib, json, os, re, sys

ROOT = '/home/z/my-project/upload'
report = {}

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

# --- c04/c05 zero-diff ---
for f in ('c04_fisica_ccd.js', 'c05_colisiones_ia_golpeo.js'):
    p = os.path.join(ROOT, 'src/game/core', f)
    report[f] = sha(p)[:16]

# --- c12: poderes ---
p12 = os.path.join(ROOT, 'src/game/core/c12_pingponggame.js')
c12 = open(p12, encoding='utf-8', errors='replace').read()
report['c12_bytes'] = len(c12.encode('utf-8', errors='replace'))
for pat in ['FENIX_OUT_P', 'OSCURIDAD_OUT_P', '_oscuridadFalla', 'TRAIL_PODER.fenix',
            'PNG_PODER_FENIX', 'PNG_PODER_CRONO', 'PNG_PODER_OSCURIDAD',
            'PNG_PODER_HIELO', 'FENIX_MUL', 'FENIX_CAP', 'Súper Hielo', 'SuperPoder de Hielo',
            '_bolaGuard', '_startFuego', '_updateFuego', 'esquinas de ojos', 'ojos dentro']:
    report[f'c12[{pat}]'] = len(re.findall(re.escape(pat), c12))

# --- c02: catálogo de poderes (entrada 10) ---
p02 = os.path.join(ROOT, 'src/game/core/c02_cfg_escena.js')
c02 = open(p02, encoding='utf-8', errors='replace').read()
report['c02_Oscuridad'] = c02.count('Oscuridad')
report['c02_Hielo'] = c02.count('Hielo')
report['c02_poder_names'] = re.findall(r"nombre:\s*'([^')]+)'", c02)[:14]

# --- salones: 6 imágenes EXACTAS por hall ---
HALL_SIZES = {
    'frente.png': (1849, 864), 'fondo.png': (1849, 864),
    'lateral_izquierda.png': (2395, 864), 'lateral_derecha.png': (2395, 864),
    'suelo.png': (1296, 1678), 'techo.png': (1296, 1678),
}
halls_dir = os.path.join(ROOT, 'public/assets/hall')
try:
    halls = sorted(os.listdir(halls_dir))
except OSError as e:
    halls = []
    report['halls_err'] = str(e)
hall_report = {}
for h in halls:
    hd = os.path.join(halls_dir, h)
    if not os.path.isdir(hd):
        continue
    files = {}
    for fn, (ew, eh) in HALL_SIZES.items():
        fp = os.path.join(hd, fn)
        if os.path.exists(fp):
            with open(fp, 'rb') as f:
                head = f.read(33)
            # PNG IHDR: width at offset 16, height at 20 (big-endian)
            w = int.from_bytes(head[16:20], 'big') if head[:8] == b'\x89PNG\r\n\x1a\n' else -1
            hgt = int.from_bytes(head[20:24], 'big') if head[:8] == b'\x89PNG\r\n\x1a\n' else -1
            files[fn] = 'OK' if (w == ew and hgt == eh) else f'BAD({w}x{hgt})'
        else:
            files[fn] = 'MISSING'
    total_kb = sum(os.path.getsize(os.path.join(hd, fn)) for fn in os.listdir(hd)
                   if fn.endswith('.png')) // 1024
    hall_report[h] = {'imgs': files, 'total_kb': total_kb}
report['halls'] = hall_report

# --- iconos del dueño: presencia en bundle (data URIs embebidos) ---
pg = os.path.join(ROOT, 'public/game.html')
gh = open(pg, encoding='utf-8', errors='replace').read()
report['game_bytes'] = os.path.getsize(pg)
report['game_sha16'] = sha(pg)[:16]
for pat in ['¡Súper fénix!', '¡Súper crono!', '¡Súper oscuridad!', 'Súper Fénix', 'Superpoder de la Oscuridad']:
    report[f'game[{pat}]'] = gh.count(pat)
report['game_Hielo'] = gh.count('Hielo')

print(json.dumps(report, ensure_ascii=False, indent=1))
