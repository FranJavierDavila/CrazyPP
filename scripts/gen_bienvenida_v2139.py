#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.139 · BIENVENIDA HABLADA — genera los átomos de voz del mensaje de
bienvenida que el juego dice al entrar en VR (menú principal abierto):

    es: «Bienvenido a Crazy Ping Pong, escoge una modalidad de juego»
    en: «Welcome to Crazy Ping Pong, choose a game mode»

Misma receta del banco (gen_voice.py): Piper TTS → WAV 22050 Hz mono →
OGG Opus 28k mono (ffmpeg libopus). El ES se genera en DOS variantes
(literal y fonética «Kreisi») para elegir por ASR la que pronuncie mejor
la marca «Crazy Ping Pong».

Salidas:
  scripts/voice/wav/bienvenida_modo*.wav
  scripts/voice/ogg/bienvenida_modo*.ogg      (ES)
  scripts/voice/ogg_en/bienvenida_modo.ogg    (EN)
  scripts/bienvenida_v2139_report.json
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

# key → (lang, texto TTS)
CLIPS = {
    # variante literal de la marca en castellano
    "bienvenida_modo": ("es", "Bienvenido a Crazy Ping Pong, escoge una modalidad de juego."),
    # variante fonética (por si el modelo inglés lee «Crazy» mejor castellanizado)
    "bienvenida_modo_fon": ("es", "Bienvenido a Kreisi Ping Pong, escoge una modalidad de juego."),
    # inglés
    "bienvenida_modo_en": ("en", "Welcome to Crazy Ping Pong, choose a game mode."),
}


def synth(key: str, text: str, lang: str) -> str:
    wav = f"{WAV_DIR}/{key}.wav"
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
    for key, (lang, text) in CLIPS.items():
        wav = synth(key, text, lang)
        ogg = to_opus(wav, key, lang)
        d = duration(wav)
        raw = open(ogg, "rb").read()
        b64 = base64.b64encode(raw).decode("ascii")
        assert "</" not in b64, f"base64 con </ en {key}"
        report[key] = {
            "lang": lang, "text": text, "seg": round(d, 2),
            "wav_kb": round(os.path.getsize(wav) / 1024, 1),
            "ogg_b": len(raw), "b64_b": len(b64),
        }
        flag = "" if 1.2 <= d <= 8.0 else "  << DURACIÓN SOSPECHOSA"
        print(f"{key:22s} {d:5.2f}s  {len(raw):6d}B ogg  {len(b64):6d}B b64  {text}{flag}")
    out = f"{BASE}/scripts/bienvenida_v2139_report.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"\nOK -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
