#!/usr/bin/env python3
"""r74 · Genera los TRES átomos NUEVOS de voz para el paso 7 (LOS MODOS) de
LA ACADEMIA, con el banco de la casa (Piper es_ES-davefx-medium /
en_US-lessac-medium, ajustes r66: length-scale 1.16 + respiro 0.55).

El dueño: «esta parte de los modos no está bien explicada, deberías pararte
un poco más para explicarla mejor». VOCES_PASO[7] pasa de 2 átomos a 5:
  tutv8a (existente) + tutv8b/tutv8c (NUEVOS: partido/supervivencia/multi)
  + tutv9a (existente) + tutv9b (NUEVO: campeonatos/ranking/entrenar).

Salida: OGG Opus 28k mono 48 kHz en scripts/voice_r65/ogg_es y ogg_en
(mismo formato del banco v2.20). Inserción: scripts/insertar_voz_r74.py
"""
import os
import subprocess
import sys

BASE = "/home/z/my-project"
M = f"{BASE}/scripts/voice_r65/models"
OUT_WAV = f"{BASE}/scripts/voice_r65/wav"
OUT_ES = f"{BASE}/scripts/voice_r65/ogg_es"
OUT_EN = f"{BASE}/scripts/voice_r65/ogg_en"
PIPER = "/tmp/piper/piper"
LENGTH_SCALE = "1.16"
SENT_SILENCE = "0.55"

ES = {
    "tutv8b": "En el partido te mides a la CPU, al mejor de tres sets. Y cada veinte golpes del intercambio, ganas una carga de poder.",
    "tutv8c": "La supervivencia aguanta el máximo de rallyes seguidos, y el multijugador conecta online con un código de cinco letras.",
    "tutv9b": "En los campeonatos te esperan rivales con su historia, el ranking mundial te mide con todo el planeta, y entrenar pule tu técnica en cinco áreas. Tómate tu tiempo para probarlos todos.",
}

EN = {
    "tutv8b": "In a match you face the CPU, best of three sets. And every twenty hits of a rally earn you a power charge.",
    "tutv8c": "Survival holds as many consecutive rallies as you can, and multiplayer connects online with a five-letter code.",
    "tutv9b": "Championships bring rivals with their own story, the world ranking measures you against the whole planet, and training polishes your technique in five areas. Take your time to try them all.",
}


def synth(atoms, model, ogg_dir, tag):
    total = 0
    for k, txt in atoms.items():
        wav = f"{OUT_WAV}/{tag}_{k}.wav"
        ogg = f"{ogg_dir}/{k}.ogg"
        if os.path.exists(wav):
            os.remove(wav)
        r = subprocess.run(
            [PIPER, "-m", model, "--length-scale", LENGTH_SCALE,
             "--sentence-silence", SENT_SILENCE, "-f", wav],
            input=txt, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(wav):
            sys.exit(f"FALLO piper {tag}:{k}: {r.stderr[:300]}")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-c:a", "libopus", "-b:a", "28k", "-ac", "1",
                        "-ar", "48000", ogg], check=True)
        total += os.path.getsize(ogg)
        print(f"  {tag}:{k}  {os.path.getsize(ogg)/1024:.1f} KB")
    print(f"OK {tag}: {len(atoms)} átomos · {total/1024:.0f} KB OGG")


if __name__ == "__main__":
    os.makedirs(OUT_WAV, exist_ok=True)
    print("· ES (davefx, pausado r66)…")
    synth(ES, f"{M}/es_ES-davefx-medium.onnx", OUT_ES, "es")
    print("· EN (lessac, pausado r66)…")
    synth(EN, f"{M}/en_US-lessac-medium.onnx", OUT_EN, "en")
    print("Listo. Ahora: python3 scripts/insertar_voz_r74.py")
