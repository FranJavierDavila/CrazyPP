#!/usr/bin/env python3
"""
INTRO OFICIAL DE CRAZY PING PONG (v3.0.6-SRV1)
Genera assets/intro.mp4 (1024x576, H.264+AAC, ~19 s) en el estilo casa de los
intros de campeonato: diapositivas oscuras con acentos ámbar/cian, bilingüe
ES grande + EN pequeño, progreso de puntos, BSO sintetizada suave.
  python3 scripts/make_intro_v306.py
"""
import math, subprocess, wave, struct, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 576
FPS = 24
SLIDE_S = 3.5          # duración de cada diapositiva
XF = 0.8               # fundido cruzado
OUT = '/home/z/my-project/public/assets/intro.mp4'

FD = '/usr/share/fonts/truetype/dejavu/'
def F(sz, bold=True):
    return ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), sz)

BG      = (13, 20, 32)
BG2     = (16, 27, 41)
AMBER   = (242, 193, 78)
CYAN    = (99, 200, 240)
PINK    = (246, 135, 179)
GREEN   = (104, 211, 145)
PURPLE  = (192, 122, 255)
ORANGE  = (255, 138, 42)
CREAM   = (255, 248, 239)
GREY    = (143, 160, 184)

def base_bg(seed=0):
    """fondo oscuro con halos suaves estilo sala"""
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    for (cx, cy, r, col) in [(180, 120, 320, (24, 38, 58)), (880, 460, 300, (20, 34, 52)),
                             (760, 90, 220, (26, 30, 48))]:
        halo = Image.new('L', (W, H), 0)
        dh = ImageDraw.Draw(halo)
        dh.ellipse([cx-r, cy-r, cx+r, cy+r], fill=90)
        halo = halo.filter(ImageFilter.GaussianBlur(120))
        img = Image.composite(Image.new('RGB', (W, H), col), img, halo)
    d = ImageDraw.Draw(img)
    # rejilla sutil
    for x in range(0, W, 64):
        d.line([(x, 0), (x, H)], fill=(18, 27, 40), width=1)
    for y in range(0, H, 64):
        d.line([(0, y), (W, y)], fill=(18, 27, 40), width=1)
    return img

def rr(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)

def paddle(img, cx, cy, s=1.0, face=(230, 70, 70), rot=-18):
    """pala cartoon plana: hoja elíptica + mango (pega sobre la Image)"""
    pad = Image.new('RGBA', (int(220*s), int(300*s)), (0, 0, 0, 0))
    dd = ImageDraw.Draw(pad)
    ew, eh = 88*s, 108*s
    dd.ellipse([110*s-ew/2, 96*s-eh/2, 110*s+ew/2, 96*s+eh/2], fill=face + (255,),
               outline=(20, 26, 36, 255), width=max(2, int(5*s)))
    dd.ellipse([110*s-ew/2+9*s, 96*s-eh/2+9*s, 110*s+ew/2-9*s, 96*s+eh/2-9*s],
               outline=(255, 255, 255, 70), width=max(2, int(3*s)))
    dd.rounded_rectangle([110*s-16*s, 96*s+eh/2-8*s, 110*s+16*s, 96*s+eh/2+96*s],
                         radius=int(14*s), fill=(146, 104, 62, 255),
                         outline=(20, 26, 36, 255), width=max(2, int(4*s)))
    pad = pad.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.paste(pad, (int(cx-pad.width/2), int(cy-pad.height/2)), pad)

def ball(dr, cx, cy, r=16, col=CREAM):
    dr.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col, outline=(20, 26, 36), width=3)

def progress(dr, idx, total=5):
    r = 7; gap = 22
    x0 = W//2 - (total-1)*gap//2
    for i in range(total):
        cx = x0 + i*gap
        col = AMBER if i == idx else (58, 72, 92)
        dr.ellipse([cx-r, H-46-r, cx+r, H-46+r], fill=col)

def brand(dr, small=True):
    dr.text((44, 34), 'CRAZY PING PONG', font=F(24), fill=CREAM)
    if small:
        dr.text((W-44, 40), 'META QUEST 3 · WEBXR', font=F(17, False), fill=GREY, anchor='ra')

# ── diapositivas ─────────────────────────────────────────────────────
def slide_title():
    img = base_bg(); dr = ImageDraw.Draw(img)
    brand(dr, small=False)
    # mesita estilizada al fondo
    dr.rounded_rectangle([312, 392, 712, 428], radius=10, fill=(23, 83, 158),
                         outline=(14, 58, 115), width=4)
    dr.line([(512, 300), (512, 392)], fill=(70, 90, 110), width=5)
    paddle(img, 330, 330, 0.92, (230, 70, 70), -24)
    paddle(img, 694, 330, 0.92, (60, 60, 66), 24)
    ball(dr, 512, 316, 15)
    dr.text((W//2, 132), 'CRAZY PING PONG', font=F(64), fill=CREAM, anchor='mm',
            stroke_width=6, stroke_fill=(20, 26, 36))
    dr.text((W//2, 196), 'TENIS DE MESA ARCADE · META QUEST 3', font=F(22), fill=AMBER, anchor='mm')
    dr.text((W//2, 228), 'Arcade table tennis for Meta Quest 3', font=F(17, False), fill=GREY, anchor='mm')
    progress(dr, 0)
    return img

def slide_modos():
    img = base_bg(); dr = ImageDraw.Draw(img)
    brand(dr)
    dr.text((W//2, 78), '5 MODOS DE JUEGO', font=F(38), fill=CREAM, anchor='mm',
            stroke_width=4, stroke_fill=(20, 26, 36))
    dr.text((W//2, 142), 'Five game modes', font=F(17, False), fill=GREY, anchor='mm')
    items = [
        ('PARTIDO', 'a 11 · ITTF', AMBER, 'VS'),
        ('PRO TRAINING', '5 áreas + skins', CYAN, '▲'),
        ('SUPERVIVENCIA', 'rallye infinito', GREEN, '∞'),
        ('ARKANOID', 'ladrillos 3D', PINK, '▦'),
        ('ONLINE P2P', 'código de sala', PURPLE, '⇄'),
    ]
    cw, ch, gap = 176, 240, 10
    x0 = (W - 5*cw - 4*gap)//2
    for i, (t, s, col, ico) in enumerate(items):
        x = x0 + i*(cw+gap)
        rr(dr, [x, 180, x+cw, 180+ch], 18, fill=(24, 36, 54), outline=col, width=3)
        rr(dr, [x+18, 202, x+cw-18, 280], 14, fill=col)
        dr.text((x+cw/2, 241), ico, font=F(44), fill=(16, 24, 38), anchor='mm')
        for ln, y in [(t, 312), (s, 344)]:
            f = F(19) if ln == t else F(15, False)
            dr.text((x+cw/2, y), ln, font=f, fill=CREAM if ln == t else GREY, anchor='mm')
    dr.text((W//2, 456), 'Partido · PRO Training · Supervivencia · Arkanoid · Multijugador online',
            font=F(17, False), fill=GREY, anchor='mm')
    progress(dr, 1)
    return img

def slide_fisica():
    img = base_bg(); dr = ImageDraw.Draw(img)
    brand(dr)
    dr.text((W//2, 102), 'FÍSICA VIVA', font=F(40), fill=CREAM, anchor='mm',
            stroke_width=4, stroke_fill=(20, 26, 36))
    dr.text((W//2, 142), 'Living physics', font=F(17, False), fill=GREY, anchor='mm')
    rows = [
        ('EFECTO REAL', 'Magnus + arrastre: el topspin patea, el cortado frena', CYAN),
        ('BOTE FÍSICO', 'la goma de la mesa agarra según el impacto', GREEN),
        ('PUNTO DULCE', 'el canto de la pala pega sordo: centra el golpe', AMBER),
        ('SAQUE VIVO', 'tu gesto manda: la asistencia sólo endereza', ORANGE),
    ]
    y = 186
    for t, s, col in rows:
        rr(dr, [130, y, W-130, y+62], 14, fill=(24, 36, 54), outline=col, width=3)
        dr.ellipse([152, y+17, 184, y+45], fill=col)
        dr.text((208, y+18), t, font=F(22), fill=CREAM)
        dr.text((208, y+40), s, font=F(16, False), fill=GREY)
        y += 74
    # bola con estela
    for i, r in enumerate([26, 20, 15, 10]):
        ball(dr, 860 - i*26, 300 - i*0, r, tuple(int(c*0.75) for c in CREAM) if i else CREAM)
    progress(dr, 2)
    return img

def slide_skins():
    img = base_bg(); dr = ImageDraw.Draw(img)
    brand(dr)
    dr.text((W//2, 102), 'PALAS CON CARÁCTER', font=F(40), fill=CREAM, anchor='mm',
            stroke_width=4, stroke_fill=(20, 26, 36))
    dr.text((W//2, 142), 'Paddles with character · each rubber plays different', font=F(17, False), fill=GREY, anchor='mm')
    skins = [
        ('FUEGO', 'OFENSIVA', ORANGE), ('HIELO', 'DEFENSIVA', CYAN),
        ('ORO', 'POTENCIA', AMBER), ('ARCOÍRIS', 'EFECTO', PURPLE),
        ('PRO CARBON', 'DOBLE GOMA', (60, 60, 66)), ('CLÁSICA', 'NEUTRA', GREY),
    ]
    cw, ch, gap = 150, 250, 16
    x0 = (W - 6*cw - 5*gap)//2
    for i, (t, s, col) in enumerate(skins):
        x = x0 + i*(cw+gap)
        rr(dr, [x, 172, x+cw, 172+ch], 18, fill=(24, 36, 54), outline=col, width=3)
        paddle(img, x+cw/2, 246, 0.62, col, -12)
        dr.text((x+cw/2, 350), t, font=F(17), fill=CREAM, anchor='mm')
        dr.text((x+cw/2, 376), s, font=F(13, False), fill=GREY, anchor='mm')
    dr.text((W//2, 456), 'Gana puntos en el PRO Training para desbloquearlas · la IA juega neutra',
            font=F(17, False), fill=GREY, anchor='mm')
    progress(dr, 3)
    return img

def slide_tv_end():
    img = base_bg(); dr = ImageDraw.Draw(img)
    brand(dr)
    # televisor CRAZY TV
    rr(dr, [W//2-190, 150, W//2+190, 330], 22, fill=(10, 14, 22), outline=AMBER, width=5)
    rr(dr, [W//2-170, 168, W//2+170, 296], 12, fill=(23, 83, 158))
    dr.text((W//2, 214), '● EN VIVO', font=F(26), fill=(255, 82, 82), anchor='mm')
    dr.text((W//2, 256), 'CRAZY TV · emite tus partidas', font=F(18), fill=CREAM, anchor='mm')
    dr.line([(W//2-60, 330), (W//2-60, 362)], fill=(70, 90, 110), width=8)
    dr.line([(W//2+60, 330), (W//2+60, 362)], fill=(70, 90, 110), width=8)
    dr.text((W//2, 404), '¡A JUGAR!', font=F(52), fill=AMBER, anchor='mm',
            stroke_width=5, stroke_fill=(20, 26, 36))
    dr.text((W//2, 452), 'Pulsa ENTRAR EN VR · Press ENTER VR', font=F(19, False), fill=GREY, anchor='mm')
    progress(dr, 4)
    return img

SLIDES = [slide_title(), slide_modos(), slide_fisica(), slide_skins(), slide_tv_end()]

# ── BSO sintetizada (arpegio suave + bajo) ───────────────────────────
SR = 22050
TOTAL_S = SLIDE_S*len(SLIDES) + XF*(len(SLIDES)-1) + 0.4
N = int(TOTAL_S*SR)
buf = bytearray()
CHORDS = [  # (semitonos relativos a A3) progresa por diapositiva
    [0, 4, 7, 12], [-3, 0, 4, 9], [-5, -1, 2, 7], [-3, 0, 4, 7], [0, 4, 7, 12],
]
def note_hz(st):
    return 220.0 * (2 ** (st / 12.0))
for i in range(N):
    t = i / SR
    # acorde según el tiempo (uno por diapositiva, con fundidos suaves)
    seg = t / (SLIDE_S + XF)
    ci = min(len(CHORDS)-1, int(seg))
    chord = CHORDS[ci]
    s = 0.0
    arp_idx = int(t * 4.4) % 4
    for j, st in enumerate(chord):
        amp = 0.16 if j == arp_idx else (0.05 if j == 0 else 0.028)
        s += amp * math.sin(2*math.pi*note_hz(st+12)*t) * (0.6 + 0.4*math.sin(2*math.pi*0.55*t))
    # bajo suave
    s += 0.10 * math.sin(2*math.pi*note_hz(chord[0]-12)*t)
    # envolvente global: fade in/out
    env = min(1.0, t/1.2, max(0.0, (TOTAL_S-t)/1.5))
    v = max(-1.0, min(1.0, s*env))
    buf += struct.pack('<h', int(v*32000))
with wave.open('/tmp/intro_bso.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(bytes(buf))

# ── vídeo: fundidos cruzados + zoom sutil, pipe raw a ffmpeg ────────
def frame_at(idx):
    """compone el fotograma idx con fundidos entre diapositivas"""
    t = idx / FPS
    n = len(SLIDES)
    starts = [i*(SLIDE_S+XF) for i in range(n)]
    # diapositiva activa y siguiente
    cur = 0
    for i in range(n):
        if t >= starts[i] - 1e-6:
            cur = i
    if cur == n-1:
        return SLIDES[cur]
    x0 = starts[cur] + SLIDE_S
    if t >= x0:
        a = (t - x0) / XF
        a = max(0.0, min(1.0, a))
        return Image.blend(SLIDES[cur], SLIDES[cur+1], a)
    return SLIDES[cur]

FF = ['ffmpeg', '-y', '-v', 'error',
      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
      '-i', '/tmp/intro_bso.wav',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p',
      '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', OUT]
total_frames = int(TOTAL_S*FPS)
proc = subprocess.Popen(FF, stdin=subprocess.PIPE)
for i in range(total_frames):
    proc.stdin.write(frame_at(i).tobytes())
proc.stdin.close()
proc.wait()
if proc.returncode != 0:
    raise SystemExit('ffmpeg falló')
sz = os.path.getsize(OUT)
print(f'OK · {OUT} · {sz/1e6:.2f} MB · {TOTAL_S:.1f} s · {len(SLIDES)} diapositivas')
