#!/usr/bin/env python3
"""extrae_base64_r114.py — localiza TODAS las imágenes/audio incrustados en
base64 dentro del código fuente del juego y les saca ficha (dimensiones,
formato, peso, dónde viven). Sirve para conocer las características REALES
de las piezas de arte que no son ficheros externos."""
import base64
import io
import json
import re
import subprocess
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src/game'
OUT = RAIZ / 'scripts/_menu_base64.json'
TMP = RAIZ / 'scripts/_tmp_extract'

FICHEROS = ['00_head.html', '03_body.html', '04_boot.html', '07_tail.html',
            'core/c00_pre_three.js', 'core/c01_modelos_3d.js',
            'core/c03_audio_voz.js', 'core/c08_hall_hud.js',
            'core/c10_menu_saque.js', 'core/c12_pingponggame.js']

PAT = re.compile(
    r'data:(image/(?:png|jpeg|jpg|webp|gif)|audio/ogg|audio/mpeg|audio/wav);'
    r'base64,([A-Za-z0-9+/=]{500,})')


def ficha_img(tipo, bruto):
    from PIL import Image
    im = Image.open(io.BytesIO(bruto))
    alfa = 'A' in im.mode or (im.mode == 'P' and 'transparency' in im.info)
    return {'tipo': 'imagen', 'mime': tipo, 'formato': im.format,
            'ancho': im.width, 'alto': im.height, 'modo': im.mode, 'alfa': alfa}


def ficha_audio(tipo, bruto):
    p = TMP / f'aud_{abs(hash(bruto[:200]))}.bin'
    p.write_bytes(bruto)
    try:
        r = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json',
                            '-show_format', str(p)],
                           capture_output=True, text=True, timeout=30)
        dur = json.loads(r.stdout).get('format', {}).get('duration', '?')
    except Exception:
        dur = '?'
    p.unlink(missing_ok=True)
    return {'tipo': 'audio', 'mime': tipo, 'duracion_s': dur}


hallados, vistos = [], set()
for fn in FICHEROS:
    txt = (SRC / fn).read_text(encoding='utf-8', errors='replace')
    for m in PAT.finditer(txt):
        mime, b64 = m.group(1), m.group(2)
        bruto = base64.b64decode(b64 + '=' * (-len(b64) % 4))
        huella = (mime, len(bruto))
        linea = txt[:m.start()].count('\n') + 1
        if huella in vistos:
            for h in hallados:
                if (h['mime'], h['peso_bytes']) == huella:
                    h['tambien_en'].append(f'{fn}:{linea}')
            continue
        vistos.add(huella)
        try:
            d = (ficha_img(mime, bruto) if mime.startswith('image/')
                 else ficha_audio(mime, bruto))
        except Exception as e:
            d = {'tipo': 'desconocido', 'err': str(e)[:80]}
        d.update({'mime': mime, 'peso_bytes': len(bruto), 'b64_kb': round(len(b64) / 1024),
                  'donde': f'{fn}:{linea}', 'tambien_en': []})
        hallados.append(d)

TMP.rmdir() if TMP.exists() and not any(TMP.iterdir()) else None
OUT.write_text(json.dumps(hallados, ensure_ascii=False, indent=1), encoding='utf-8')
hallados.sort(key=lambda d: -d['peso_bytes'])
for d in hallados:
    res = f"{d.get('ancho', '')}x{d.get('alto', '')}" if 'ancho' in d else ''
    dur = f"{d.get('duracion_s')}s" if d['tipo'] == 'audio' else ''
    print(f"{d['donde']:38s} {d['mime']:16s} {res:10s} {dur:8s} "
          f"{d['peso_bytes']/1024:9.1f} KB fichero ({d['b64_kb']} KB b64)")
print(f"\n✓ {len(hallados)} piezas incrustadas únicas → {OUT}")
