#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.140 · MEGAFONÍA DE LAS ESTACIONES del Salvaje Oeste (etapa 4 TREN).

El dueño pide voz pregrabada de estación de tren:
  · SALIDAS  → «Pasajeros al tren, partimos hacia…» [siguiente estación]
  · LLEGADAS → «En menos de 25 segundos llegaremos a…» [estación]
               (anuncio a los 30 s del final del reloj de la parada)
  · ARRIBO OK→ «¡Cargamento de oro a buen recaudo!» (con recompensa.png)
  · ARRIBO KO→ risas del forajido (risas_forajido.mp3) + forajido_robo.png

Estaciones del trayecto (TREN.stationNames): BRAVOS (salida) · DRY GULCH ·
PERDIDO · BRAVOS (final). Frases COMPLETAS por estación (Piper entona mejor
una frase entera que dos clips pegados) → 7 átomos ES + 7 átomos EN.

Misma receta del banco (gen_voice.py / gen_bienvenida_v2139.py):
Piper TTS → WAV 22050 Hz mono → OGG Opus 28k mono (ffmpeg libopus).
El ES de «Dry Gulch» se genera en DOS variantes (literal y fonética
«Drai Gulch») para elegir por ASR la que suene mejor.

Salidas:
  scripts/voice/wav/mega_*.wav
  scripts/voice/ogg/mega_*.ogg      (ES)
  scripts/voice/ogg_en/mega_*.ogg   (EN)
  scripts/megafonia_v2140_report.json
"""
import base64
import json
import os
import subprocess
import sys

BASE = "/home/z/my-project"
VOICE_DIR = f"{BASE}/scripts/voice"
PIPER = f"{VOICE_DIR}/piper/piper"
MODELS = {
    "es": f"{VOICE_DIR}/models/es_ES-davefx-medium.onnx",
    "en": f"{VOICE_DIR}/models/en_US-lessac-medium.onnx",
}
WAV_DIR = f"{VOICE_DIR}/wav"
OGG_DIR = f"{VOICE_DIR}/ogg"
OGG_EN_DIR = f"{VOICE_DIR}/ogg_en"

# (key, lang, texto TTS) — la KEY es la MISMA en ambos idiomas (el banco
# se elige por idioma en el núcleo; ver _voiceBank de game.html).
CLIPS = [
    # ---------- CASTELLANO (es_ES-davefx-medium) ----------
    ("mega_salida_dg", "es", "Pasajeros al tren, partimos hacia Dry Gulch."),
    ("mega_salida_dg_fon", "es", "Pasajeros al tren, partimos hacia Drai Gulch."),
    ("mega_salida_pd", "es", "Pasajeros al tren, partimos hacia Perdido."),
    ("mega_salida_br", "es", "Pasajeros al tren, partimos hacia Bravos."),
    ("mega_llega_dg", "es", "En menos de veinticinco segundos llegaremos a Dry Gulch."),
    ("mega_llega_dg_fon", "es", "En menos de veinticinco segundos llegaremos a Drai Gulch."),
    ("mega_llega_pd", "es", "En menos de veinticinco segundos llegaremos a Perdido."),
    ("mega_llega_br", "es", "En menos de veinticinco segundos llegaremos a Bravos."),
    ("mega_oro", "es", "¡Cargamento de oro a buen recaudo!"),
    # ---------- INGLÉS (en_US-lessac-medium) ----------
    ("mega_salida_dg", "en", "All aboard! We are departing towards Dry Gulch."),
    ("mega_salida_pd", "en", "All aboard! We are departing towards Perdido."),
    ("mega_salida_br", "en", "All aboard! We are departing towards Bravos."),
    ("mega_llega_dg", "en", "In less than twenty-five seconds we will arrive at Dry Gulch."),
    ("mega_llega_pd", "en", "In less than twenty-five seconds we will arrive at Perdido."),
    ("mega_llega_br", "en", "In less than twenty-five seconds we will arrive at Bravos."),
    ("mega_oro", "en", "The gold shipment is safe and sound!"),
]


def synth(key: str, text: str, lang: str) -> str:
    wav = f"{WAV_DIR}/{key}_{lang}.wav"   # sufijo de idioma: las keys es/en COEXISTEN
    r = subprocess.run([PIPER, "-m", MODELS[lang], "-f", wav],
                       input=text.encode("utf-8"), capture_output=True, timeout=90)
    if r.returncode != 0 or not os.path.isfile(wav) or os.path.getsize(wav) < 2000:
        raise RuntimeError(f"piper falló para {key}: rc={r.returncode} {r.stderr[-300:]}")
    return wav


def to_opus(wav: str, key: str, lang: str) -> str:
    ogg = f"{OGG_EN_DIR}/{key}.ogg" if lang == "en" else f"{OGG_DIR}/{key}.ogg"
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav,
                        "-c:a", "libopus", "-b:a", "28k", "-ac", "1",
                        "-application", "audio", ogg],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or not os.path.isfile(ogg) or os.path.getsize(ogg) < 400:
        raise RuntimeError(f"ffmpeg falló para {key}: {r.stderr[-300:]}")
    return ogg


def duration(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0


def main() -> int:
    os.makedirs(WAV_DIR, exist_ok=True)
    os.makedirs(OGG_DIR, exist_ok=True)
    os.makedirs(OGG_EN_DIR, exist_ok=True)
    report = {}
    for key, lang, text in CLIPS:
        wav = synth(key, text, lang)
        ogg = to_opus(wav, key, lang)
        d = duration(wav)
        raw = open(ogg, "rb").read()
        b64 = base64.b64encode(raw).decode("ascii")
        assert "</" not in b64, f"base64 con </ en {key}"
        report[f"{key}:{lang}"] = {
            "lang": lang, "text": text, "seg": round(d, 2),
            "wav_kb": round(os.path.getsize(wav) / 1024, 1),
            "ogg_b": len(raw), "b64_b": len(b64),
        }
        flag = "" if 1.0 <= d <= 9.0 else "  << DURACIÓN SOSPECHOSA"
        print(f"{key:22s} {lang} {d:5.2f}s  {len(raw):6d}B ogg  {len(b64):6d}B b64{flag}")
    out = f"{BASE}/scripts/megafonia_v2140_report.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"\nOK -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
