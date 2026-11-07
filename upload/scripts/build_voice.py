#!/usr/bin/env python3
"""v2.20 · Construye scripts/game_voice.js con los átomos OGG en base64."""
import base64, os

VOICE_DIR = "/home/z/my-project/scripts/voice"
OUT = "/home/z/my-project/scripts/game_voice.js"

keys = sorted(f[:-4] for f in os.listdir(f"{VOICE_DIR}/ogg") if f.endswith(".ogg"))
lines = []
total = 0
for k in keys:
    b = open(f"{VOICE_DIR}/ogg/{k}.ogg", "rb").read()
    total += len(b)
    b64 = base64.b64encode(b).decode("ascii")
    assert "</" not in b64, "base64 no puede contener </"
    lines.append(f'  {k}: "{b64}",')
js = (
    "/* =====================================================================\n"
    " *  v2.20 · BANCO DE VOZ del megáfono. Meta Quest Browser NO reproduce\n"
    " *  speechSynthesis dentro de la sesión inmersiva (en la pestaña 2D sí):\n"
    " *  la voz del marcador pasa a ser audio real, decodificado con WebAudio\n"
    " *  (la misma vía por la que ya se oyen los efectos en el visor).\n"
    " *  Clips es-ES generados con Piper TTS (modelo es_ES-davefx-medium) y\n"
    " *  comprimidos a Opus 28k mono. El juego los concatena según el plan de\n"
    " *  cada anuncio (voicePlan en game_part1.js); speechSynthesis queda\n"
    " *  como respaldo en escritorio. Regenerar: gen_voice.py + build_voice.py\n"
    " * ===================================================================== */\n"
    "const VOICE_B64 = {\n" + "\n".join(lines) + "\n};\n"
)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(js)
print(f"OK -> {OUT} ({len(keys)} átomos, {total/1024:.0f} KB OGG, "
      f"{os.path.getsize(OUT)/1024:.0f} KB JS)")
