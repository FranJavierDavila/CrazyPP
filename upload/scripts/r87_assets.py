#!/usr/bin/env python3
# r87 · ASSETS DE LOS ARREGLOS DE HALLOWEEN (informe del dueño tras V3.6.78)
#  · monticulo.png del dueño → assets/monticulo.webp (512², alfa intacto):
#    el montículo APARECE sobre la mesa ANTES de que salga la mano.
#  · mosca nueva: 2 frames de aleteo (mosca_a / mosca_b, 128²) dibujados
#    por la casa — el dueño pidió «más trabajadas, aleteo, más cantidad y
#    calidad». El mosca.webp viejo se conserva por compat.
#  · fly_buzz.wav → mp3 (ffmpeg, perfil probado del casco 44100 Hz).
from PIL import Image, ImageDraw
import math, os, subprocess

RAIZ = '/home/z/my-project'
HALL = RAIZ + '/public/championships/halloween/assets'
TMP = RAIZ + '/tmp'

# ── 1 · MONTÍCULO (arte del dueño, tal cual, redimensionado) ────────────
im = Image.open(RAIZ + '/upload/monticulo.png').convert('RGBA')
im = im.resize((512, 512), Image.LANCZOS)
im.save(HALL + '/monticulo.webp', 'WEBP', quality=90, method=6)
print('monticulo.webp', im.size, os.path.getsize(HALL + '/monticulo.webp'), 'B')

# ── 2 · MOSCAS con ALETEO (2 frames, cuerpo brillante + alas membranosas)
def mosca_frame(alas_arriba, ruta):
    S = 128
    cv = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(cv)
    cx, cy = 64, 74
    # sombra sutil bajo el cuerpo
    d.ellipse([cx-22, cy+26, cx+22, cy+34], fill=(0, 0, 0, 40))
    # ALAS (dos, membranosas, semitransparentes) — ángulo según frame
    ang = math.radians(-64) if alas_arriba else math.radians(-18)
    for lado in (-1, 1):
        a = ang * 1  # ambas alas suben/bajan juntas (apertura espejada)
        L, W_ = 46, 16
        # ala izquierda
        ax, ay = cx - 6, cy - 10
        tipx = ax - L * math.cos(a - 0.35) * 1.0
        tipy = ay - L * math.sin(a - 0.35)
        perpx, perpy = math.sin(a), math.cos(a)
        poly = [(ax, ay), (tipx - perpx*W_/2, tipy + perpy*W_/2),
                (tipx + perpx*W_/2, tipy - perpy*W_/2), (ax, ay)]
        d.polygon(poly, fill=(216, 228, 240, 108), outline=(255, 255, 255, 130))
        # ala derecha
        tipx = ax + L * math.cos(a - 0.35)
        tipy = ay - L * math.sin(a - 0.35)
        poly = [(ax, ay), (tipx - perpx*W_/2, tipy + perpy*W_/2),
                (tipx + perpx*W_/2, tipy - perpy*W_/2), (ax, ay)]
        d.polygon(poly, fill=(216, 228, 240, 108), outline=(255, 255, 255, 130))
    # CUERPO (tórax + abdomen, negro brillante con brillo)
    d.ellipse([cx-15, cy-16, cx+15, cy+8], fill=(24, 22, 24, 255))     # tórax
    d.ellipse([cx-11, cy-2, cx+11, cy+30], fill=(28, 24, 26, 255))     # abdomen
    d.ellipse([cx-9, cy-13, cx-1, cy-6], fill=(95, 100, 108, 200))     # brillo
    d.ellipse([cx-7, cy+2, cx-1, cy+16], fill=(70, 62, 66, 180))       # brillo 2
    # OJOS rojos
    d.ellipse([cx-14, cy-14, cx-4, cy-4], fill=(200, 40, 34, 255))
    d.ellipse([cx+4, cy-14, cx+14, cy-4], fill=(200, 40, 34, 255))
    d.ellipse([cx-12, cy-12, cx-8, cy-8], fill=(255, 120, 110, 255))
    d.ellipse([cx+6, cy-12, cx+10, cy-8], fill=(255, 120, 110, 255))
    # PATAS finas
    for dx, dy, ex, ey in [(-14, 8, -26, 18), (-12, 14, -24, 26), (14, 8, 26, 18), (12, 14, 24, 26)]:
        d.line([cx+dx, cy+dy, cx+ex, cy+ey], fill=(30, 26, 28, 235), width=3)
    cv.save(ruta, 'WEBP', quality=92, method=6)
    print(os.path.basename(ruta), cv.size, os.path.getsize(ruta), 'B')

mosca_frame(True, HALL + '/mosca_a.webp')
mosca_frame(False, HALL + '/mosca_b.webp')

# ── 3 · ZUMBIDO de enjambre (loop sin costura ~1.1 s) ───────────────────
#  síntesis: sierra 168 Hz + 172 Hz (batido) + AM 26 Hz + ruido suave
import struct, wave, random
SR = 44100
DUR = 1.1
N = int(SR * DUR)
samples = []
for i in range(N):
    t = i / SR
    f0 = 168.0 + 2.5 * math.sin(2 * math.pi * 0.9 * t)          # deriva viva
    ph = 2 * math.pi * f0 * t
    v = (math.sin(ph) * 0.5 + math.sin(2 * ph + 0.7) * 0.22 +
         math.sin(3 * ph + 1.9) * 0.10 + math.sin(2 * math.pi * (f0 + 3.7) * t) * 0.18)
    am = 0.62 + 0.38 * math.sin(2 * math.pi * 26.0 * t)          # aleteo
    # ruido de alas (chispear suave)
    ruido = (random.random() * 2 - 1) * 0.05
    s = (v * am + ruido) * 0.5
    # fundido corto en los extremos para loop sin click
    k = min(1.0, i / (SR * 0.02), (N - i) / (SR * 0.02))
    samples.append(s * k)
ruta_wav = TMP + '/fly_buzz.wav'
with wave.open(ruta_wav, 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h', max(-32767, min(32767, int(s * 32767)))) for s in samples))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', ruta_wav,
                '-codec:a', 'libmp3lame', '-b:a', '256k', '-ar', '44100',
                HALL + '/fly_buzz.mp3'], check=True)
print('fly_buzz.mp3', os.path.getsize(HALL + '/fly_buzz.mp3'), 'B')
print('OK ASSETS r87')
