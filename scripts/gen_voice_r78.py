#!/usr/bin/env python3
"""r78 · «EL NARRADOR HONESTO — CAMPEONATOS»: regenera los átomos del paso 7
(LOS MODOS) de LA ACADEMIA que mentían sobre los superpoderes, con el banco
de la casa (Piper es_ES-davefx-medium / en_US-lessac-medium, ajustes r66:
length-scale 1.16 + respiro 0.55).

Nota del dueño (r78): «En el audio del tutorial, en el apartado de modos, se
dice que cada 20 toques ganamos un superpoder, pero esto NO es para los
partidos normales: los superpoderes SOLO aparecen en los campeonatos. Cuando
describe los modos llega un momento que dice "…y más…" cuando lo que debería
decir es Campeonatos: el modo tipo arcade con poderes en juego tanto para el
rival como para el propio jugador cuando consigue superar los 20 toques
seguidos. Estos superpoderes se ven con un icono identificativo sobre el
mango de nuestra pala y se lanzan apretando el gatillo; duran 10 segundos.
¡Lucha con el rival y véncelo!»

Verdad del juego (c12): megaEnabled() = solo con champs.active (v3.6.36,
misma petición del dueño) · MEGA_GOLPES = 20 toques del rally · gatillo del
mando LIBRE lanza · icono del dueño sobre el mango · duraciones 10 s (Mega
Pala apila +15). CAMBIOS:
  tutv8a «…multijugador, Y MÁS.»      → «…multijugador Y CAMPEONATOS.»
  tutv8b «Y cada veinte golpes… carga» → FUERA (falso en partido normal)
  tutv9a «poderes locos en cada mesa»  → CAMPEONATOS = modo arcade + 20 toques
  tutv9c NUEVO                          → icono en el mango · gatillo · 10 s
  tutv9b «En los campeonatos…»          → rivales/historia + ranking + entrenar
  tutv8c SIN CAMBIOS (su OGG queda byte a byte).

Salida: OGG Opus 28k mono 48 kHz en scripts/voice_r65/ogg_es y ogg_en
(mismo formato del banco v2.20). Inserción: scripts/insertar_voz_r78.py
"""
import os
import subprocess
import sys

BASE = "/home/z/my-project"
M = f"{BASE}/scripts/voice_r65/models"
OUT_WAV = f"{BASE}/scripts/voice_r65/wav"
OUT_ES = f"{BASE}/scripts/voice_r65/ogg_es"
OUT_EN = f"{BASE}/scripts/voice_r65/ogg_en"
PIPER = "/tmp/my-project/scripts/voice/piper/piper"
LENGTH_SCALE = "1.16"
SENT_SILENCE = "0.55"

ES = {
    "tutv8a": "Te esperan seis modos de juego: partido, supervivencia, multijugador y campeonatos.",
    "tutv8b": "En el partido te mides a la CPU, al mejor de tres sets.",
    "tutv9a": "Los campeonatos son el modo arcade: aquí sí hay superpoderes, para el rival y para ti, cuando consigues superar veinte toques seguidos.",
    "tutv9c": "Cada superpoder se ve con un icono identificativo sobre el mango de tu pala. Se lanza apretando el gatillo y dura diez segundos. ¡Lucha con el rival y véncelo!",
    "tutv9b": "En los campeonatos te esperan rivales con su historia. El ranking mundial te mide con todo el planeta, y entrenar pule tu técnica en cinco áreas. Tómate tu tiempo para probarlos todos.",
}

EN = {
    "tutv8a": "Six game modes are waiting: match, survival, multiplayer and championships.",
    "tutv8b": "In a match you face the CPU, best of three sets.",
    "tutv9a": "Championships are the arcade mode: superpowers live here, for the rival and for you, when you get past twenty straight hits.",
    "tutv9c": "Each superpower shows its own icon on your paddle handle. Fire it with the trigger, and it lasts ten seconds. Fight the rival and beat them!",
    "tutv9b": "Championships bring rivals with their own story. The world ranking measures you against the whole planet, and training polishes your technique in five areas. Take your time to try them all.",
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
    print("Listo. Ahora: python3 scripts/insertar_voz_r78.py")
