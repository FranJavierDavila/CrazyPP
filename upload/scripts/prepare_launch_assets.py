#!/usr/bin/env python3
"""v2.28 · Prepara los assets del nuevo arranque y del menú principal VR.

- hero.jpg       : Cabecera.png (1672x941) -> JPEG 1280 ancho (portada web)
- menulogo.jpg   : recorte de la franja del logo para la cabecera del menú VR
                   (1024x220, misma proporción que el recorte de origen)
- pad_es/en.png  : palas con bandera 256x256 -> 160x160 PNG (alfa intacta)
- play_es/en.png : botones cartoon 512x128 (tal cual, PNG con alfa)
- star.ogg       : música de la portada (89,7 s) recomprimida a OGG Vorbis
"""
import subprocess, os
from PIL import Image

UP = "/home/z/my-project/upload"
OUT = "/home/z/my-project/scripts/launch_assets"
os.makedirs(OUT, exist_ok=True)

# ---- 1) hero de la portada -------------------------------------------------
im = Image.open(f"{UP}/Cabecera.png").convert("RGB")
w = 1280
hero = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
hero.save(f"{OUT}/hero.jpg", quality=84, optimize=True)
print("hero.jpg", hero.size, os.path.getsize(f"{OUT}/hero.jpg") // 1024, "KB")

# ---- 2) franja del logo para la cabecera del menú VR -----------------------
# Recorte 1672x360 (y 100..460) -> escala 1024x220 (proporción idéntica 4,64)
band = im.crop((0, 100, 1672, 460))
logo = band.resize((1024, 220), Image.LANCZOS)
logo.save(f"{OUT}/menulogo.jpg", quality=86, optimize=True)
print("menulogo.jpg", logo.size, os.path.getsize(f"{OUT}/menulogo.jpg") // 1024, "KB")

# ---- 3) palas de idioma ----------------------------------------------------
for src, dst in (("Castellano.png", "pad_es.png"), ("English.png", "pad_en.png")):
    p = Image.open(f"{UP}/{src}").convert("RGBA")
    # recorte con margen: la pala ocupa el centro (256x256 con aire)
    bbox = p.getbbox()
    p2 = p.crop(bbox)
    side = max(p2.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(p2, ((side - p2.width) // 2, (side - p2.height) // 2))
    sq = sq.resize((160, 160), Image.LANCZOS)
    sq.save(f"{OUT}/{dst}", optimize=True)
    print(dst, os.path.getsize(f"{OUT}/{dst}") // 1024, "KB", "bbox:", bbox)

# ---- 4) botones cartoon JUGAR / PLAY ---------------------------------------
for src, dst in (("jugar.png", "play_es.png"), ("play.png", "play_en.png")):
    p = Image.open(f"{UP}/{src}").convert("RGBA")
    bbox = p.getbbox()
    p2 = p.crop(bbox)
    p2.save(f"{OUT}/{dst}", optimize=True)
    print(dst, p2.size, os.path.getsize(f"{OUT}/{dst}") // 1024, "KB")

# ---- 5) música de portada ---------------------------------------------------
r = subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", f"{UP}/star.mp3",
    "-c:a", "libvorbis", "-q:a", "2", f"{OUT}/star.ogg",
], capture_output=True, text=True)
if r.returncode != 0:
    print("ffmpeg err:", r.stderr)
else:
    print("star.ogg", os.path.getsize(f"{OUT}/star.ogg") // 1024, "KB")

print("LISTO ->", OUT)
