#!/usr/bin/env python3
"""inventario_menu_r114.py — ficha técnica de todos los activos del menú/hall
de CrazyPP: imágenes (formato, dimensiones, modo, alfa), audio (duración,
canales, bitrate), vídeo (resolución, duración) y modelos GLB (peso).
Salida: scripts/_menu_activos.json + tabla en stdout."""
import json
import struct
import subprocess
from pathlib import Path

RAIZ = Path('/home/z/my-project')
DIRS = [RAIZ / 'public/assets']
JSON_OUT = RAIZ / 'scripts/_menu_activos.json'


def ffprobe(p):
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'error', '-print_format', 'json',
             '-show_format', '-show_streams', str(p)],
            capture_output=True, text=True, timeout=30)
        return json.loads(r.stdout) if r.returncode == 0 else None
    except Exception:
        return None


def ficha_img(p):
    from PIL import Image
    im = Image.open(p)
    modo = im.mode
    alfa = 'A' in modo or (modo == 'P' and 'transparency' in im.info)
    d = {'tipo': 'imagen', 'formato': im.format, 'ancho': im.width,
         'alto': im.height, 'modo': modo, 'alfa': alfa}
    icc = im.info.get('icc_profile')
    if icc:
        d['perfil_icc'] = f'{len(icc)} bytes'
    return d


def ficha_audio(p):
    md = ffprobe(p)
    if not md:
        return {'tipo': 'audio', 'nota': 'ffprobe no disponible'}
    st = next((s for s in md['streams'] if s.get('codec_type') == 'audio'), {})
    fmt = md.get('format', {})
    return {'tipo': 'audio', 'duracion_s': round(float(fmt.get('duration', 0)), 1),
            'bitrate_kbps': round(int(fmt.get('bit_rate', 0)) / 1000),
            'codec': st.get('codec_name'), 'canales': st.get('channels'),
            'sample_rate': st.get('sample_rate')}


def ficha_video(p):
    md = ffprobe(p)
    if not md:
        return {'tipo': 'video', 'nota': 'ffprobe no disponible'}
    st = next((s for s in md['streams'] if s.get('codec_type') == 'video'), {})
    fmt = md.get('format', {})
    return {'tipo': 'video', 'duracion_s': round(float(fmt.get('duration', 0)), 1),
            'ancho': st.get('width'), 'alto': st.get('height'),
            'codec': st.get('codec_name'),
            'fps': st.get('avg_frame_rate'), 'bitrate_kbps': round(int(fmt.get('bit_rate', 0)) / 1000)}


def ficha_glb(p):
    """GLB: cabecera + chunk JSON da meshes/materiales aproximados."""
    with p.open('rb') as f:
        cab = f.read(12)
        if cab[:4] != b'glTF':
            return {'tipo': 'modelo3d'}
        _ver, _lon = struct.unpack('<II', cab[4:12])
        _lon_chunk, = struct.unpack('<I', f.read(4))
        js = json.loads(f.read(_lon_chunk))
    mallas = len(js.get('meshes', []))
    mats = [m.get('name', '?') for m in js.get('materials', [])]
    imgs = len(js.get('images', []))
    return {'tipo': 'modelo3d', 'version_gltf': _ver, 'mallas': mallas,
            'materiales': mats[:8], 'imagenes_embebidas': imgs}


activos = {}
for carpeta in DIRS:
    for p in sorted(carpeta.rglob('*')):
        if not p.is_file():
            continue
        rel = str(p.relative_to(RAIZ / 'public'))
        ext = p.suffix.lower()
        peso = p.stat().st_size
        try:
            if ext in {'.png', '.jpg', '.jpeg', '.webp'}:
                d = ficha_img(p)
            elif ext in {'.mp3', '.ogg', '.wav'}:
                d = ficha_audio(p)
            elif ext in {'.mp4', '.webm'}:
                d = ficha_video(p)
            elif ext == '.glb':
                d = ficha_glb(p)
            else:
                continue
        except Exception as e:
            d = {'tipo': 'error', 'err': str(e)[:120]}
        d['peso_kb'] = round(peso / 1024, 1)
        activos[rel] = d

JSON_OUT.write_text(json.dumps(activos, ensure_ascii=False, indent=1),
                    encoding='utf-8')
for rel, d in activos.items():
    res = f"{d.get('ancho', '?')}x{d.get('alto', '?')}" if 'ancho' in d else ''
    extra = {k: d[k] for k in ('duracion_s', 'canales', 'materiales', 'alfa') if k in d}
    print(f"{rel:52s} {d.get('tipo', '?'):8s} {res:11s} {d['peso_kb']:9.1f} KB  {extra}")
print(f"\n✓ {len(activos)} activos → {JSON_OUT}")
