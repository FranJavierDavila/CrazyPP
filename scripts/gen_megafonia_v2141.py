#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.141 · MEGAFONÍA — NOMBRES NUEVOS de las estaciones del Oeste.

El dueño renombra el trayecto para que la voz diga LOS NOMBRES DE LOS
CARTELES del artista: parada 1 «Bravos» (PARADA1.png nueva) · parada 2
«GOLD DUST» · parada 3 «Silver Creek». BRAVOS ya tenía átomos (v2.140);
faltan los de GOLD DUST y SILVER CREEK → 4 claves nuevas × 2 idiomas.

Misma receta del banco (gen_voice.py / gen_megafonia_v2140.py):
Piper TTS → WAV 22050 Hz mono → OGG Opus 28k mono (ffmpeg libopus).
El ES de los nombres anglosajones se genera en DOS variantes (literal y
fonética: «Gol Dast» · «Silver Cric») para elegir por ASR la que suene
mejor — el ES LITERAL fue la elección de v2.140 para «Dry Gulch».

Salidas:
  scripts/voice/wav/mega_*.wav          (sufijo de idioma: keys es/en COEXISTEN)
  scripts/voice/ogg/mega_*.ogg          (ES)
  scripts/voice/ogg_en/mega_*.ogg       (EN)
  scripts/megafonia_v2141_report.json
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

# (key, lang, texto TTS) — la KEY es la MISMA en ambos idiomas. Las claves
# _fon son CANDIDATOS es para comparar por ASR (no se inyectan tal cual).
CLIPS = [
    # ---------- CASTELLANO (es_ES-davefx-medium) ----------
    ("mega_salida_gd", "es", "Pasajeros al tren, partimos hacia Gold Dust."),
    ("mega_salida_gd_fon", "es", "Pasajeros al tren, partimos hacia Gol Dast."),
    ("mega_salida_sc", "es", "Pasajeros al tren, partimos hacia Silver Creek."),
    ("mega_salida_sc_fon", "es", "Pasajeros al tren, partimos hacia Silver Cric."),
    ("mega_llega_gd", "es", "En menos de veinticinco segundos llegaremos a Gold Dust."),
    ("mega_llega_gd_fon", "es", "En menos de veinticinco segundos llegaremos a Gol Dast."),
    ("mega_llega_sc", "es", "En menos de veinticinco segundos llegaremos a Silver Creek."),
    ("mega_llega_sc_fon", "es", "En menos de veinticinco segundos llegaremos a Silver Cric."),
    # ---------- INGLÉS (en_US-lessac-medium) ----------
    ("mega_salida_gd", "en", "All aboard! We are departing towards Gold Dust."),
    ("mega_salida_sc", "en", "All aboard! We are departing towards Silver Creek."),
    ("mega_llega_gd", "en", "In less than twenty-five seconds we will arrive at Gold Dust."),
    ("mega_llega_sc", "en", "In less than twenty-five seconds we will arrive at Silver Creek."),
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
    out = f"{BASE}/scripts/megafonia_v2141_report.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"\nOK -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
