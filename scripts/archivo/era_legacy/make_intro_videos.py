#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG — VÍDEOS DE INTRO DE CAMPEONATO (v2.130)
Genera championships/<id>/assets/intro.mp4 (~29 s, 1024×576, H.264+AAC):
  · 6 ESCENAS de 5,2 s (still 2048×1152 compuesto con PIL: fondo temático,
    arte del rival, leyenda ES + EN)
  · motion Ken Burns con zoompan + fundidos xfade (ffmpeg)
  · audio: los primeros ~29 s de la BSO del campeonato con fade
El vídeo es OPCIONAL en el juego (botón JUGAR siempre activo).
"""
import math
import os
import random
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = '/home/z/my-project/public/championships'
TMP = '/home/z/my-project/scripts/_intro_tmp'
os.makedirs(TMP, exist_ok=True)

_FDIR = '/usr/share/fonts/truetype/dejavu'
_FB = _FDIR + '/DejaVuSans-Bold.ttf'
_FR = _FDIR + '/DejaVuSans.ttf'
_fcache = {}


def F(sz, bold=True):
    k = (sz, bold)
    if k not in _fcache:
        _fcache[k] = ImageFont.truetype(_FB if bold else _FR, sz)
    return _fcache[k]


# ------------------------------------------------------------------ paletas
CIAN = (79, 216, 255)
AMBAR = (255, 190, 92)
BLANCO = (240, 246, 255)
NEGRO = (8, 11, 20)


def wrap(d, txt, font, maxw):
    words = txt.split()
    lines, line = [], ''
    for w in words:
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=font) > maxw and line:
            lines.append(line)
            line = w
        else:
            line = t
    if line:
        lines.append(line)
    return lines


# ----------------------------------------------------------- fondos (2048)
def bg_circo():
    img = Image.new('RGB', (2048, 1152), (120, 24, 20))
    d = ImageDraw.Draw(img)
    for y in range(1152):
        k = y / 1152
        d.line([0, y, 2048, y],
               fill=(int(58 + 30 * k), int(14 + 12 * k), int(16 + 10 * k)))
    # carpa: rayas radiales tenues arriba
    m = Image.new('RGBA', (2048, 1152), (0, 0, 0, 0))
    md = ImageDraw.Draw(m)
    for i in range(24):
        a0 = math.pi + i * (math.pi / 24)
        md.polygon([(1024, 700),
                    (1024 + 2400 * math.cos(a0), 700 + 2400 * math.sin(a0)),
                    (1024 + 2400 * math.cos(a0 + math.pi / 48),
                     700 + 2400 * math.sin(a0 + math.pi / 48))],
                   fill=(228, 84, 60, 26))
    img.paste(m, (0, 0), m)
    rs = random.Random(5)
    for i in range(90):
        x, y = rs.uniform(0, 2048), rs.uniform(0, 1152)
        col = rs.choice([(255, 209, 102), (110, 190, 250), (240, 98, 90),
                         (150, 220, 160)])
        md.rectangle([x, y, x + 14, y + 8], fill=col + (150,))
    img.paste(m, (0, 0), m)
    return img


def bg_arcano():
    img = Image.new('RGB', (2048, 1152), (24, 14, 46))
    d = ImageDraw.Draw(img)
    for y in range(1152):
        k = y / 1152
        d.line([0, y, 2048, y],
               fill=(int(26 + 14 * k), int(15 + 8 * k), int(50 + 22 * k)))
    rs = random.Random(9)
    d = ImageDraw.Draw(img)
    for i in range(220):
        x, y = rs.uniform(0, 2048), rs.uniform(0, 1152)
        r = 1 if rs.random() < 0.85 else 2
        col = (200, 176, 255) if rs.random() < 0.4 else (235, 240, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    m = Image.new('RGBA', (2048, 1152), (0, 0, 0, 0))
    md = ImageDraw.Draw(m)
    for i in range(9):
        x, y = rs.uniform(100, 1948), rs.uniform(80, 900)
        r = rs.uniform(24, 60)
        md.ellipse([x - r, y - r, x + r, y + r], fill=(255, 214, 110, 60))
    m = m.filter(ImageFilter.GaussianBlur(14))
    img.paste(m, (0, 0), m)
    return img


def bg_oeste():
    img = Image.new('RGB', (2048, 1152), (240, 150, 70))
    d = ImageDraw.Draw(img)
    for y in range(1152):
        k = y / 1152
        if k < 0.55:
            d.line([0, y, 2048, y],
                   fill=(int(250 - 80 * k / 0.55), int(160 - 40 * k / 0.55),
                         int(90 + 30 * k / 0.55)))
        else:
            kk = (k - 0.55) / 0.45
            d.line([0, y, 2048, y],
                   fill=(int(160 - 60 * kk), int(110 - 55 * kk), int(70 - 30 * kk)))
    # sol
    d.ellipse([880, 240, 1160, 520], fill=(255, 214, 130))
    # mesas/cactus lejanos (siluetas)
    d.rectangle([0, 800, 2048, 1152], fill=(70, 44, 34))
    for (x, w, h) in ((180, 90, 190), (520, 70, 130), (1500, 80, 170), (1850, 66, 120)):
        d.rectangle([x, 800 - h, x + w, 800], fill=(52, 32, 26))
        d.ellipse([x - 12, 800 - h - 40, x + w + 12, 800 - h + 40], fill=(52, 32, 26))
    rs = random.Random(3)
    for i in range(70):
        x, y = rs.uniform(0, 2048), rs.uniform(820, 1140)
        r = rs.uniform(3, 12)
        d.ellipse([x - r, y - r * 0.4, x + r, y + r * 0.4], fill=(58, 36, 28))
    return img


def bg_espacio():
    img = Image.new('RGB', (2048, 1152), (10, 16, 30))
    d = ImageDraw.Draw(img)
    for y in range(1152):
        k = y / 1152
        d.line([0, y, 2048, y],
               fill=(int(10 + 8 * k), int(16 + 10 * k), int(30 + 16 * k)))
    rs = random.Random(11)
    for i in range(260):
        x, y = rs.uniform(0, 2048), rs.uniform(0, 1152)
        r = 1 if rs.random() < 0.85 else 2
        col = (159, 216, 255) if rs.random() < 0.25 else (235, 242, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    m = Image.new('RGBA', (2048, 1152), (0, 0, 0, 0))
    md = ImageDraw.Draw(m)
    for i in range(40):
        x = rs.uniform(0, 2048)
        y = rs.uniform(100, 1050)
        r = rs.uniform(30, 110)
        col = rs.choice([(120, 70, 190, 34), (60, 130, 210, 40), (40, 170, 190, 26)])
        md.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=col)
    m = m.filter(ImageFilter.GaussianBlur(30))
    img.paste(m, (0, 0), m)
    # planeta anillado
    d = ImageDraw.Draw(img)
    px, py, R = 300, 260, 110
    d.ellipse([px - R, py - R, px + R, py + R], fill=(72, 140, 208))
    d.ellipse([px - R + 14, py - R + 18, px + R - 30, py + R - 40],
              fill=(96, 168, 226))
    for rr, aa in ((1.6, 200), (1.42, 140), (1.8, 120)):
        d.ellipse([px - R * rr, py - R * rr * 0.28, px + R * rr, py + R * rr * 0.28],
                  outline=(214, 196, 158), width=8)
    d.ellipse([px - R, py - R, px + R, py + R], fill=(72, 140, 208, 0))
    return img


# ----------------------------------------------------------- composición
def pega_art(img, art, cx, cy, alto=None):
    """Pega un PNG/WebP con alfa + sombra suave."""
    if not art or not os.path.exists(art):
        return
    a = Image.open(art).convert('RGBA')
    ah = alto or 720
    aw = int(a.width * ah / a.height)
    a = a.resize((aw, ah), Image.LANCZOS)
    sh = Image.new('RGBA', (aw + 60, ah + 60), (0, 0, 0, 0))
    shd = ImageDraw.Draw(sh)
    shd.ellipse([30, 30, aw + 30, ah + 30], fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    img.paste(sh, (cx - aw // 2 - 30 + 12, cy - ah // 2 - 30 + 18), sh)
    img.paste(a, (cx - aw // 2, cy - ah // 2), a)


def escena(champ, idx, total, titulo, sub, es, en, art=None, estilo='espacio'):
    img = {'circo': bg_circo, 'arcano': bg_arcano, 'oeste': bg_oeste,
           'espacio': bg_espacio}[estilo]()
    d = ImageDraw.Draw(img)
    if idx == 0:
        # PÓRTICO: título grande centrado
        d.rounded_rectangle([260, 330, 1788, 700], radius=48,
                            fill=(12, 18, 32), outline=AMBAR, width=10)
        lines = wrap(d, titulo.upper(), F(110), 1400)
        ty = 445 - (len(lines) - 1) * 62
        for ln in lines:
            d.text((1024, ty), ln, font=F(110), fill=BLANCO, anchor='mm')
            ty += 124
        d.text((1024, 620), sub, font=F(44, False), fill=CIAN, anchor='mm')
    else:
        # arte a la derecha, texto a la izquierda
        if art:
            pega_art(img, art, 1440, 520, alto=700)
        d.text((120, 120), 'CRAZY PING PONG', font=F(36), fill=(255, 255, 255, 160),
               anchor='lm')
        d.text((1928, 120), titulo.upper(), font=F(36), fill=AMBAR, anchor='rm')
        x0, y0, x1, y1 = 90, 840, 1300, 1102
        d.rounded_rectangle([x0, y0, x1, y1], radius=34, fill=(10, 15, 28))
        d.rounded_rectangle([x0, y0, x1, y1], radius=34, outline=(70, 90, 130), width=6)
        lines = wrap(d, es, F(52), 1130)[:2]
        ty = y0 + 52
        for ln in lines:
            d.text((x0 + 44, ty), ln, font=F(52), fill=BLANCO, anchor='lm')
            ty += 72
        d.text((x0 + 44, y1 - 38), en, font=F(31, False), fill=(150, 180, 210),
               anchor='lm')
        # progreso de escenas
        for i in range(total):
            col = AMBAR if i <= idx else (70, 84, 110)
            d.ellipse([1330 + i * 42, 1064, 1350 + i * 42, 1084], fill=col)
    return img


# ------------------------------------------------------------- guiones
def guiones():
    A = lambda cid, p: os.path.join(BASE, cid, 'assets', p)
    return [
        dict(cid='locura', estilo='circo', bso=A('locura', 'bso.ogg'),
             titulo='La Locura del Payaso', sub='CAMPEONATO · EL CIRCO',
             scenes=[
                 ('El circo llegó a la ciudad con una promesa: una partida imposible de ganar.',
                  'The circus came to town promising an impossible match.',
                  A('locura', 'idle.webp')),
                 ('Su estrella es CLOWN, el payaso que nunca pierde.',
                  'Its star is CLOWN, the clown who never loses.',
                  A('locura', 'laughing.webp')),
                 ('Confeti, globos y su nueva «Burla»: ¡todo vale!',
                  'Confetti, balloons and his new Mockery: anything goes!',
                  A('locura', 'crazy.webp')),
                 ('Si le vences, la insignia del circo será tuya.',
                  'Beat him and the circus badge is yours.',
                  A('locura', 'insignia.png')),
                 ('CLOWN ya sonríe. ¿Aceptas la partida?',
                  'CLOWN is already smiling. Do you accept the match?',
                  A('locura', 'idle.webp')),
             ]),
        dict(cid='magia', estilo='arcano', bso=A('magia', 'bso.mp3'),
             titulo='Nuevo truco de Magia', sub='CAMPEONATO · EL LABORATORIO',
             scenes=[
                 ('En un laboratorio oculto vive WIZARD, el mago arcano.',
                  'In a hidden lab lives WIZARD, the arcane mage.',
                  A('magia', 'present.webp')),
                 ('Su obsesión: el ping-pong mágico. Nadie supera sus trucos.',
                  'His obsession: magic ping-pong. No one beats his tricks.',
                  A('magia', 'focused.webp')),
                 ('Portales, orbes y sombras: sus trucos no son trucos.',
                  'Portals, orbs and shadows: his tricks are not tricks.',
                  A('magia', 'portals.webp')),
                 ('Su tesoro: la Varita Dorada. Si le vences, su insignia.',
                  'His treasure: the Golden Wand. Beat him: his badge.',
                  A('magia', 'insignia.png')),
                 ('WIZARD agita su varita. ¿Listo para el truco final?',
                  'WIZARD waves his wand. Ready for the final trick?',
                  A('magia', 'idle.webp')),
             ]),
        dict(cid='oeste', estilo='oeste', bso=A('oeste', 'bso.mp3'),
             titulo='El Salvaje Oeste', sub='CAMPEONATO · EL SALOON',
             scenes=[
                 ('En el saloon solo hay una ley: la mesa de ping-pong.',
                  'In the saloon there is only one law: the ping-pong table.',
                  A('oeste', 'idle.webp')),
                 ('FORAJIDO, el pistolero más rápido del condado, nunca pierde.',
                  'FORAJIDO, the fastest gunslinger in the county, never loses.',
                  A('oeste', 'focused.webp')),
                 ('Tormentas de arena, dinamita y paradas imposibles.',
                  'Sandstorms, dynamite and impossible saves.',
                  A('oeste', 'crazy.webp')),
                 ('La Estrella del Sheriff espera a quien le venza.',
                  'The Sheriff star awaits whoever beats him.',
                  A('oeste', 'insignia.png')),
                 ('FORAJIDO afila su puntería. ¿Desafías al Oeste?',
                  'FORAJIDO sharpens his aim. Do you dare the West?',
                  A('oeste', 'angry.webp')),
             ]),
        dict(cid='estacion_orbital', estilo='espacio', bso=A('estacion_orbital', 'bso.wav'),
             titulo='Estación Orbital', sub='CAMPEONATO · SECTOR 7',
             scenes=[
                 ('A bordo entrena el campeón de la galaxia.',
                  'Aboard the station trains the galaxy champion.',
                  A('estacion_orbital', 'idle.webp')),
                 ('AX-9: el androide que jamás perdió ante un humano.',
                  'AX-9: the android that never lost to a human.',
                  A('estacion_orbital', 'duelo.webp')),
                 ('Meteoritos, rayo tractor y gravedad cero: su entrenamiento.',
                  'Meteorites, tractor beam and zero gravity: his training.',
                  A('estacion_orbital', 'rival.webp')),
                 ('Su insignia solo la lleva quien le vence en su duelo.',
                  'His badge belongs only to whoever beats him.',
                  A('estacion_orbital', 'insignia.png')),
                 ('AX-9 flota, esperando. ¿Aceptas el duelo, humano?',
                  'AX-9 hovers, waiting. Do you accept the duel, human?',
                  A('estacion_orbital', 'idle.webp')),
             ]),
    ]


# ------------------------------------------------------------- ffmpeg
SEG = 5.2          # s por escena
FPS = 25
FADE = 0.5


def compila(g, out):
    cid = g['cid']
    total = len(g['scenes']) + 1
    stills = []
    for i in range(total):
        if i == 0:
            sc = escena(cid, 0, total, g['titulo'], g['sub'], '', '',
                        None, g['estilo'])
        else:
            es, en, art = g['scenes'][i - 1]
            sc = escena(cid, i, total, g['titulo'], '', es, en, art, g['estilo'])
        p = f'{TMP}/{cid}_{i}.png'
        sc.save(p)
        stills.append(p)
    # filtro: zoompan por escena + xfade en cadena + audio
    inputs = []
    for p in stills:
        inputs += ['-i', p]
    inputs += ['-i', g['bso']]
    fl = []
    n = len(stills)
    dframes = int(SEG * FPS)
    DF = str(dframes)
    for i in range(n):
        # v2 · variables 'on' (frame de SALIDA del segmento): semántica exacta
        if i % 4 == 0:      # zoom-in centrado
            z = f"1+0.10*on/{DF}"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
        elif i % 4 == 1:    # zoom-out centrado
            z = f"1.10-0.10*on/{DF}"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
        elif i % 4 == 2:    # paneo derecha
            z = "1.08"; x = f"(iw-iw/zoom)*on/{DF}"; y = "ih/2-(ih/zoom/2)"
        else:               # zoom-in desde abajo
            z = f"1+0.10*on/{DF}"; x = "iw/2-(iw/zoom/2)"; y = f"(ih-ih/zoom)*(1-on/{DF})"
        fl.append(
            f"[{i}:v]zoompan=z='{z}':d={dframes}:x='{x}':y='{y}':"
            f"s=1024x576:fps={FPS},settb=AVTB,format=yuv420p[v{i}]")
    dur = SEG - FADE
    last = 'v0'
    for i in range(1, n):
        outl = f"x{i}"
        fl.append(f"[{last}][v{i}]xfade=transition=fade:duration={FADE}:"
                  f"offset={i * dur:.2f}[{outl}]")
        last = outl
    total_s = (n - 1) * dur + SEG
    fl.append(f"[{n}:a]atrim=0:{total_s:.2f},asetpts=N/SR/TB,"
              f"afade=t=in:st=0:d=0.6,afade=t=out:st={total_s - 1.8:.2f}:d=1.8[aout]")
    cmd = (['ffmpeg', '-y'] + inputs +
           ['-filter_complex', ';'.join(fl),
            '-map', f'[{last}]', '-map', '[aout]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '24',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
            '-c:a', 'aac', '-b:a', '96k',
            '-t', f'{total_s:.2f}', out])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1800:])
        raise SystemExit(f'ffmpeg falló para {cid}')
    return total_s


if __name__ == '__main__':
    solo = sys.argv[1] if len(sys.argv) > 1 else None
    for g in guiones():
        if solo and g['cid'] != solo:
            continue
        out = os.path.join(BASE, g['cid'], 'assets', 'intro.mp4')
        t = compila(g, out)
        kb = os.path.getsize(out) // 1024
        print(f"OK {g['cid']}: {out} · {t:.1f} s · {kb} KB")
