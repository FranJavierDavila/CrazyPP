#!/usr/bin/env python3
"""v2.27 · Construye scripts/game_voice_en.js con los átomos OGG ingleses
(mismas claves que el banco español; el juego elige banco según el idioma)."""
import base64, os

VOICE_DIR = "/home/z/my-project/scripts/voice"
OUT = "/home/z/my-project/scripts/game_voice_en.js"

keys = sorted(f[:-4] for f in os.listdir(f"{VOICE_DIR}/ogg_en") if f.endswith(".ogg"))
lines = []
total = 0
for k in keys:
    b = open(f"{VOICE_DIR}/ogg_en/{k}.ogg", "rb").read()
    total += len(b)
    b64 = base64.b64encode(b).decode("ascii")
    assert "</" not in b64, "base64 no puede contener </"
    lines.append(f'  {k}: "{b64}",')
js = (
    "/* =====================================================================\n"
    " *  v2.27 · BANCO DE VOZ EN INGLÉS del megáfono. Misma estructura de\n"
    " *  claves que VOICE_B64 (game_voice.js) — los planes de voz valen para\n"
    " *  ambos. Clips en-US generados con Piper TTS (en_US-lessac-medium) y\n"
    " *  comprimidos a Opus 28k mono. Regenerar: gen_voice_en.py + este.\n"
    " * ===================================================================== */\n"
    "const VOICE_B64_EN = {\n" + "\n".join(lines) + "\n};\n"
)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(js)
print(f"OK -> {OUT} ({len(keys)} átomos, {total/1024:.0f} KB OGG, "
      f"{os.path.getsize(OUT)/1024:.0f} KB JS)")
