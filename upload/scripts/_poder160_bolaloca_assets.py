#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FASE 160 (v3.6.157 · r66) · BOLA LOCA — assets EMBEBIDOS del 15.º poder:
  · VOCES NATIVAS de la casa: Piper es_ES-davefx-medium (LA MISMA de la
    megafonía) y en_US-lessac-medium — «¡Bola loca!» / «Crazy ball!» con
    el PERFIL PROBADO en el Quest (recorte de silencios + loudnorm +
    atempo animoso + MP3 mono 48 kHz 64k — receta de _poder36/gen_voces.sh).
  · ICONO del dueño: SuperPala_BolaLoca.png → recorte al contenido con
    alfa PRESERVADO → 256×256 → 64 colores FASTOCTREE (receta _poder50).
  · INSERTA los tres data-URI en c12 (placeholders __PODER160_*__).
Idempotente: lo ya hecho no se rehace (comparación EXACTA del URI).
"""
import base64
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

RAIZ = Path('/home/z/my-project/upload')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
OUT = RAIZ / 'scripts' / '_poder160'
OUT.mkdir(parents=True, exist_ok=True)

PIPER_CANDIDATOS = [
    Path('/tmp/my-project/scripts/voice/piper/piper'),
    Path('/home/z/my-project/scripts/voice/piper/piper'),
]
MODELOS_CANDIDATOS = [
    Path('/tmp/my-project/scripts/voice/models'),
    Path('/home/z/my-project/upload/scripts/voice_r65/models'),
]

fallos = []


def buscar(pistas):
    for p in pistas:
        if p.exists():
            return p
    return None


PIPER = buscar(PIPER_CANDIDATOS)
MODELOS = buscar(MODELOS_CANDIDATOS)
if not PIPER or not PIPER.exists():
    print('  ✗ binario piper no encontrado')
    fallos.append('piper')
if not MODELOS:
    print('  ✗ modelos piper no encontrados')
    fallos.append('modelos')

FFMPEG = shutil.which('ffmpeg')
if not FFMPEG:
    print('  ✗ ffmpeg no encontrado')
    fallos.append('ffmpeg')


def gen_voz(texto, modelo, wav_sal):
    """Piper → wav (parámetros exactos de gen_voces.sh de la casa)."""
    cmd = [str(PIPER), '--model', str(MODELOS / modelo),
           '--length-scale', '0.92', '--sentence-silence', '0.08',
           '--output_file', str(wav_sal)]
    subprocess.run(cmd, input=texto.encode('utf-8'),
                   check=True, capture_output=True, timeout=120)


def post_wav(wav_ent, mp3_sal):
    """Perfil PROBADO en el Quest (receta literal de la casa)."""
    subprocess.run(
        [FFMPEG, '-y', '-hide_banner', '-loglevel', 'error', '-i', str(wav_ent),
         '-af', 'silenceremove=start_periods=1:start_threshold=-45dB,'
                'areverse,silenceremove=start_periods=1:start_threshold=-45dB,'
                'areverse,loudnorm=I=-16:TP=-1.5:LRA=11,atempo=1.04',
         '-ar', '48000', '-ac', '1', '-b:a', '64k', str(mp3_sal)],
        check=True, timeout=120)


def recortar_con_alfa(im, lado, margen=6):
    """Recorte al contenido con margen, canvas cuadrado, alfa intacto."""
    im = im.convert('RGBA')
    bb = im.getbbox()
    if bb:
        x0, y0, x1, y1 = bb
        x0 = max(0, x0 - margen)
        y0 = max(0, y0 - margen)
        x1 = min(im.width, x1 + margen)
        y1 = min(im.height, y1 + margen)
        im = im.crop((x0, y0, x1, y1))
    lado_img = max(im.width, im.height)
    escala = (lado - 8) / lado_img
    nw = max(1, round(im.width * escala))
    nh = max(1, round(im.height * escala))
    im2 = im.resize((nw, nh), Image.LANCZOS)
    lienzo = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    lienzo.paste(im2, ((lado - nw) // 2, (lado - nh) // 2), im2)
    return lienzo


def uri(fich, mime):
    return mime + base64.b64encode(Path(fich).read_bytes()).decode('ascii')


# ── 1) VOCES (Piper nativo de la casa) ──────────────────────────────────
p_es = OUT / 'voz_bolaloca_es.mp3'
p_en = OUT / 'voz_bolaloca_en.mp3'
if not fallos:
    if p_es.exists() and p_en.exists():
        print(f'  = voces ya generadas ({p_es.stat().st_size:,} B / '
              f'{p_en.stat().st_size:,} B)')
    else:
        try:
            with tempfile.TemporaryDirectory() as td:
                tdes = Path(td) / 'es.wav'
                tden = Path(td) / 'en.wav'
                print('  … Piper es_ES-davefx: «¡Bola loca!»')
                gen_voz('¡Bola loca!', 'es_ES-davefx-medium.onnx', tdes)
                print('  … Piper en_US-lessac: «Crazy ball!»')
                gen_voz('Crazy ball!', 'en_US-lessac-medium.onnx', tden)
                post_wav(tdes, p_es)
                post_wav(tden, p_en)
            print(f'  ✓ voz ES {p_es.stat().st_size:,} B · '
                  f'voz EN {p_en.stat().st_size:,} B (48 kHz mono 64k)')
        except Exception as eV:
            print(f'  ✗ voces: {eV}')
            fallos.append('voces')

# ── 2) ICONO del dueño (recorte + alfa + 64 colores) ────────────────────
p_ico = OUT / 'icono_bolaloca_64.png'
orig = RAIZ / 'SuperPala_BolaLoca.png'   # el PNG del dueño vive en la raíz del repo
if not orig.exists():
    print(f'  ✗ icono origen ausente: {orig}')
    fallos.append('icono')
else:
    ico = recortar_con_alfa(Image.open(orig), 256)
    ico_q = ico.quantize(colors=64, method=Image.FASTOCTREE)
    ico_q.save(p_ico)
    print(f'  ✓ icono_bolaloca_64.png {p_ico.stat().st_size:,} B '
          f'modo={ico_q.mode} (de {orig.stat().st_size:,} B)')

# ── 3) INSERTA en c12 (comparación EXACTA del placeholder/URI) ──────────
txt = C12.read_text(encoding='utf-8')
for ph, fich, mime in [
    ('__PODER160_PNG_BOLALOCA__', p_ico, 'data:image/png;base64,'),
    ('__PODER160_VOZ_BOLALOCA_ES__', p_es, 'data:audio/mpeg;base64,'),
    ('__PODER160_VOZ_BOLALOCA_EN__', p_en, 'data:audio/mpeg;base64,'),
]:
    if not Path(fich).exists():
        print(f'  ✗ asset ausente para {ph}: {fich}')
        fallos.append(ph)
        continue
    u = uri(fich, mime)
    if ph in txt:
        txt = txt.replace(ph, u, 1)
        print(f'  ✓ {ph} ← {Path(fich).name} ({Path(fich).stat().st_size:,} B)')
    elif ("'" + u + "'") in txt:
        print(f'  = {ph} ya insertado (URI exacto presente)')
    else:
        print(f'  ✗ {ph}: ni placeholder ni URI')
        fallos.append(ph)

quedan = [ph for ph in ('__PODER160_PNG_BOLALOCA__',
                        '__PODER160_VOZ_BOLALOCA_ES__',
                        '__PODER160_VOZ_BOLALOCA_EN__') if ph in txt]
if quedan and 'voces' not in fallos and 'icono' not in fallos \
        and 'piper' not in fallos:
    print('  ✗ placeholders sin resolver:', quedan)
    fallos.extend(quedan)
elif not quedan:
    C12.write_text(txt, encoding='utf-8')

print('ASSETS BOLA LOCA (FASE 160):', 'OK' if not fallos
      else f'{len(fallos)} FALLOS: {fallos}')
sys.exit(1 if fallos else 0)
