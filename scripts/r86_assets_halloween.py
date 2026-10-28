#!/usr/bin/env python3
"""
CRAZY PING PONG · r86 (V3.6.78) · Escenario REAL del Campeonato de Halloween
============================================================================
Procesa los assets del dueño (tmp_assets/) hacia
public/championships/halloween/assets/:

  · paredes.zip  → sala_front/left/right/back/floor/ceil.jpg (regla: nombres
                   de contrato del bloque room; máx 2048 px, q80)
  · troqueles.zip→ decor_arana/calabaza/lapida/ojos.png (PNG con alfa intacto)
  · manos.zip    → mano1/2/3.webp (las manos del artista TRAEN el montículo
                   integrado: salen de su propia tierra, no hace falta
                   monticulo.png)
  · mesa.jpg     → losa.jpg (textura de losa de piedra para la mesa)
  · SuperPower.png → superpower.webp (cartel del anuncio de superpoder)
  · gelatina.png → gelatina.webp (manchas de Gelatina Asquerosa)
  · calabaza.glb → calabaza.glb (la bola-calabaza)
  · 4 medallones circulares de superpoder (diseño de la casa, PIL):
                   power_mano/power_moscas/power_calabaza/power_gelatina.webp
  · mosca.webp   (sprite de la Plaga de Moscas)
  · RETIRA los provisionales power_0.png / power_1.png (Niebla/Orbe)
  · REESCRIBE LEEME-ASSETS.txt con qué es del dueño y qué es de la casa
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps

RAIZ = '/home/z/my-project'
TMP = os.path.join(RAIZ, 'tmp_assets')
DST = os.path.join(RAIZ, 'public', 'championships', 'halloween', 'assets')
os.makedirs(DST, exist_ok=True)

informe = []


def ap(*a):
    print(*a)
    informe.append(' '.join(str(x) for x in a))


def grabar_webp(im, nombre, q=85):
    p = os.path.join(DST, nombre)
    im.save(p, 'WEBP', quality=q, method=6)
    ap(f'  webp {nombre:26s} {im.size} {os.path.getsize(p)//1024} KB')


def grabar_jpg(im, nombre, q=80):
    p = os.path.join(DST, nombre)
    im.convert('RGB').save(p, 'JPEG', quality=q, optimize=True)
    ap(f'  jpg  {nombre:26s} {im.size} {os.path.getsize(p)//1024} KB')


def grabar_png(im, nombre):
    p = os.path.join(DST, nombre)
    im.save(p, 'PNG', optimize=True)
    ap(f'  png  {nombre:26s} {im.size} {os.path.getsize(p)//1024} KB')


def copiar(nombre):
    src = os.path.join(TMP, nombre)
    dst = os.path.join(DST, nombre)
    with open(src, 'rb') as a, open(dst, 'wb') as b:
        b.write(a.read())
    ap(f'  copia {nombre:25s} {os.path.getsize(dst)//1024} KB')


print('== 1 · PAREDES del dueño → contrato sala_*.jpg (máx 2048 px, q80) ==')
MAPA_PAREDES = {
    'frente.jpg': 'sala_front.jpg',
    'izquierda.jpg': 'sala_left.jpg',
    'derecha.jpg': 'sala_right.jpg',
    'fondo.jpg': 'sala_back.jpg',
    'suelo.jpg': 'sala_floor.jpg',
    'techo.jpg': 'sala_ceil.jpg',
}
for origen, destino in MAPA_PAREDES.items():
    im = Image.open(os.path.join(TMP, 'paredes', origen)).convert('RGB')
    l, a = im.size
    if max(l, a) > 2048:
        f = 2048.0 / max(l, a)
        im = im.resize((int(l * f), int(a * f)), Image.LANCZOS)
    grabar_jpg(im, destino, 80)

print('== 2 · TROQUELES del dueño → decor_*.png (alfa intacto) ==')
TROQUELES = {
    'escena_arana.png': 'decor_arana.png',
    'escena_calabaza.png': 'decor_calabaza.png',
    'escena_lapida.png': 'decor_lapida.png',
    'escena_ojos.png': 'decor_ojos.png',
}
for origen, destino in TROQUELES.items():
    grabar_png(Image.open(os.path.join(TMP, 'troqueles', origen)), destino)

print('== 3 · MANOS del dueño (traen el montículo integrado) → webp q85 ==')
for i in (1, 2, 3):
    im = Image.open(os.path.join(TMP, 'manos', f'mano{i}.png'))
    grabar_webp(im, f'mano{i}.webp', 85)

print('== 4 · MESA LOSA del dueño → losa.jpg q82 ==')
im = Image.open(os.path.join(TMP, 'mesa.jpg')).convert('RGB')
grabar_jpg(im, 'losa.jpg', 82)

print('== 5 · CARTEL SUPERPOWER del dueño → superpower.webp q90 ==')
im = Image.open(os.path.join(TMP, 'SuperPower.png'))
grabar_webp(im, 'superpower.webp', 90)

print('== 6 · GELATINA del dueño → gelatina.webp q90 ==')
im = Image.open(os.path.join(TMP, 'gelatina.png'))
grabar_webp(im, 'gelatina.webp', 90)

print('== 7 · CALABAZA del dueño → calabaza.glb (binario intacto) ==')
copiar('calabaza.glb')

print('== 8 · MEDALLONES circulares de superpoder (diseño de la casa) ==')
L = 256
CX = CY = L // 2
R = 118


def medallon():
    im = Image.new('RGBA', (L, L), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # fondo radial azul-negro profundo (familia del cartel SuperPower)
    fondo = Image.new('RGBA', (L, L), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fondo)
    for r in range(R, 0, -2):
        t = r / R
        c = (int(26 + 16 * t), int(34 + 22 * t), int(66 + 40 * t), 255)
        fd.ellipse([CX - r, CY - r, CX + r, CY + r], fill=c)
    im.alpha_composite(fondo)
    # anillos dorados
    d.ellipse([CX - R, CY - R, CX + R, CY + R], outline=(246, 166, 35, 255), width=9)
    d.ellipse([CX - R + 11, CY - R + 11, CX + R - 11, CY + R - 11],
              outline=(246, 166, 35, 110), width=3)
    return im, d


def encajar(im, alto):
    w0, h0 = im.size
    f = alto / h0
    return im.resize((max(1, int(w0 * f)), alto), Image.LANCZOS)


# — MANO: arte del dueño (la mano sale de su montículo) —
im, d = medallon()
mano = Image.open(os.path.join(TMP, 'manos', 'mano1.png'))
mano = encajar(mano, 196)
x = CX - mano.width // 2
y = CY - 92
im.alpha_composite(mano, (x, y))
grabar_webp(im, 'power_mano.webp', 92)

# — MOSCAS: 3 moscas dibujadas + remolino —
im, d = medallon()


def mosca(dd, cx, cy, esc=1.0, ang=0.0):
    import math
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def P(px, py):
        return (cx + px * ca - py * sa, cy + px * sa + py * ca)
    # alas (dos elipses translúcidas hacia arriba)
    for sx in (-1, 1):
        w1, w2 = P(6 * sx, -10), P(24 * sx, -24)
        dd.ellipse([min(w1[0], w2[0]) - 7, min(w1[1], w2[1]) - 4,
                    max(w1[0], w2[0]) + 7, max(w1[1], w2[1]) + 4],
                   fill=(226, 232, 244, 185))
    # cuerpo
    b1, b2 = P(-16, 6), P(14, -4)
    dd.ellipse([min(b1[0], b2[0]) - 9, min(b1[1], b2[1]) - 7,
                max(b1[0], b2[0]) + 9, max(b1[1], b2[1]) + 7], fill=(30, 30, 40, 255))
    h = P(15, -7)
    dd.ellipse([h[0] - 8, h[1] - 8, h[0] + 8, h[1] + 8], fill=(40, 40, 52, 255))
    e1, e2 = P(20, -11), P(23, -4)
    dd.ellipse([e1[0] - 3, e1[1] - 3, e1[0] + 3, e1[1] + 3], fill=(212, 58, 58, 255))
    dd.ellipse([e2[0] - 3, e2[1] - 3, e2[0] + 3, e2[1] + 3], fill=(212, 58, 58, 255))


def mosca_peq(dd, cx, cy, esc=1.0, ang=0.0):
    import math
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def P(px, py):
        return (cx + (px * ca - py * sa) * esc, cy + (px * sa + py * ca) * esc)
    for sx in (-1, 1):
        w1, w2 = P(4 * sx, -8), P(16 * sx, -19)
        dd.ellipse([min(w1[0], w2[0]) - 4, min(w1[1], w2[1]) - 3,
                    max(w1[0], w2[0]) + 4, max(w1[1], w2[1]) + 3],
                   fill=(210, 218, 234, 205))
    b1, b2 = P(-11, 4), P(10, -3)
    dd.ellipse([min(b1[0], b2[0]) - 6, min(b1[1], b2[1]) - 5,
                max(b1[0], b2[0]) + 6, max(b1[1], b2[1]) + 5], fill=(28, 28, 38, 255))
    h = P(10, -5)
    dd.ellipse([h[0] - 5, h[1] - 5, h[0] + 5, h[1] + 5], fill=(40, 40, 54, 255))
    e = P(13, -8)
    dd.ellipse([e[0] - 2, e[1] - 2, e[0] + 2, e[1] + 2], fill=(220, 62, 62, 255))


mosca_peq(d, CX - 34, CY + 40, esc=1.25, ang=-16)
mosca_peq(d, CX + 40, CY - 8, esc=1.05, ang=12)
mosca_peq(d, CX - 14, CY - 52, esc=0.95, ang=-2)
mosca_peq(d, CX + 22, CY + 62, esc=0.8, ang=6)
# remolinos punteados
import math
for r, pasos in ((92, 30), (72, 24)):
    for k in range(pasos):
        t = k / pasos * 2.6 * math.pi
        px = CX + r * math.cos(t)
        py = CY + r * 0.66 * math.sin(t)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(214, 220, 234, 135))
grabar_webp(im, 'power_moscas.webp', 92)

# — CALABAZA: jack-o-lantern dibujado —
im, d = medallon()
# cuerpo con lóbulos
for dx, w in ((-46, 40), (0, 52), (46, 40)):
    d.ellipse([CX - w + dx, CY - 52, CX + w + dx, CY + 78], fill=(232, 119, 34, 255),
              outline=(158, 74, 14, 255), width=3)
# costillas
for k in (-30, 0, 30):
    d.arc([CX + k - 46, CY - 50, CX + k + 46, CY + 76], 60, 120,
          fill=(185, 92, 20, 220), width=4)
# talo verde
d.rounded_rectangle([CX - 9, CY - 84, CX + 11, CY - 44], 6, fill=(63, 125, 44, 255))
d.ellipse([CX - 20, CY - 92, CX + 2, CY - 74], fill=(82, 148, 56, 255))
# ojos y boca
d.polygon([(CX - 44, CY - 6), (CX - 18, CY - 6), (CX - 31, CY - 32)], fill=(16, 12, 8, 255))
d.polygon([(CX + 18, CY - 6), (CX + 44, CY - 6), (CX + 31, CY - 32)], fill=(16, 12, 8, 255))
d.rounded_rectangle([CX - 34, CY + 26, CX + 34, CY + 44], 8, fill=(16, 12, 8, 255))
for k in (-22, -6, 10, 26):
    d.polygon([(CX + k, CY + 26), (CX + k + 8, CY + 26), (CX + k + 4, CY + 36)],
              fill=(232, 119, 34, 255))
grabar_webp(im, 'power_calabaza.webp', 92)

# — GELATINA: arte del dueño (blob central) RECORTADO AL CÍRCULO con aro verde —
im, d = medallon()
gel = Image.open(os.path.join(TMP, 'gelatina.png'))
gel = gel.crop((96, 96, 416, 416))
gel = encajar(gel, 204)
gel = gel.resize((206, 206), Image.LANCZOS)
masc = Image.new('L', (206, 206), 0)
md = ImageDraw.Draw(masc)
md.ellipse([3, 3, 203, 203], fill=255)
put = Image.new('RGBA', (L, L), (0, 0, 0, 0))
put.paste(gel, (CX - 103, CY - 96), masc)
im.alpha_composite(put)
d.ellipse([CX - 101, CY - 99, CX + 101, CY + 103], outline=(120, 255, 60, 200), width=5)
grabar_webp(im, 'power_gelatina.webp', 92)

print('== 9 · SPRITE de mosca (Plaga de Moscas) ==')
S = 96
fly = Image.new('RGBA', (S, S), (0, 0, 0, 0))
fd = ImageDraw.Draw(fly)
fd.ellipse([14, 10, 52, 40], fill=(228, 234, 246, 190))     # ala izq
fd.ellipse([46, 6, 86, 34], fill=(228, 234, 246, 190))      # ala dcha
fd.ellipse([26, 34, 74, 66], fill=(26, 26, 36, 255))        # cuerpo
fd.ellipse([60, 30, 84, 56], fill=(38, 38, 52, 255))        # cabeza
fd.ellipse([66, 34, 74, 42], fill=(212, 58, 58, 255))       # ojo 1
fd.ellipse([74, 44, 82, 52], fill=(212, 58, 58, 255))       # ojo 2
for k, yy in ((58, 62), (50, 70), (40, 72)):                # patitas
    fd.line([(k, yy), (k - 10, yy + 12)], fill=(20, 20, 28, 230), width=3)
fly = fly.filter(ImageFilter.GaussianBlur(0.4))
grabar_webp(fly, 'mosca.webp', 92)

print('== 10 · RETIRO de provisionales (Niebla de tumba / Orbe espectral) ==')
for n in ('power_0.png', 'power_1.png'):
    p = os.path.join(DST, n)
    if os.path.exists(p):
        os.remove(p)
        ap(f'  retirado {n}')

LEEME = """LEEME-ASSETS · Campeonato de Halloween (r86 / manifest v2)
===========================================================
DEL ARTISTA (el dueño):
  sala_front/left/right/back.jpg  → paredes.zip (paredes de la estancia)
  sala_floor.jpg · sala_ceil.jpg  → paredes.zip (suelo y techo)
  decor_arana/calabaza/lapida/ojos.png → troqueles.zip (los 4 troqueles)
  mano1/2/3.webp                  → manos.zip (manos zombi; traen el montículo
                                    de tierra INTEGRADO — no existe
                                    monticulo.png como pieza aparte: las manos
                                    salen de su propia tierra)
  losa.jpg                        → mesa.jpg (losa de piedra de la mesa)
  superpower.webp                 → SuperPower.png (cartel del anuncio)
  gelatina.webp                   → gelatina.png (manchas Gelatina Asquerosa)
  calabaza.glb                    → calabaza.glb (bola-calabaza)
  zombi *.webp (12 poses) · mapa.webp · normas_halloween.png · insignia.png

DE LA CASA (provisional hasta que el artista mande lo suyo):
  power_mano/power_moscas/power_calabaza/power_gelatina.webp
    → medallones circulares del anuncio de superpoder (diseño PIL sobre el
      arte del dueño donde fue posible: mano y gelatina usan su arte).
  mosca.webp → sprite de la Plaga de Moscas.
  bso.wav (del valle) · risas.mp3 · insignia.png → siguen PROVISIONALES.
RETIRADO en r86: power_0.png / power_1.png (Niebla de tumba / Orbe espectral,
poderes provisionales de la r85 — sustituidos por los 4 reales del dueño).
"""
with open(os.path.join(DST, 'LEEME-ASSETS.txt'), 'w') as f:
    f.write(LEEME)
ap('  LEEME-ASSETS.txt reescrito')
print('\nR86 ASSETS OK')
