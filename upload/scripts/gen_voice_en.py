#!/usr/bin/env python3
"""v2.27 · Genera los átomos de voz EN INGLÉS del megáfono con Piper TTS
(modelo en_US-lessac-medium). Misma estructura de claves que el banco
español (gen_voice.py) para que los planes de voz (voicePlan) funcionen
con CUALQUIERA de los dos bancos.

Produce:
  scripts/voice/wav_en/<key>.wav  (22050 Hz mono)
  scripts/voice/ogg_en/<key>.ogg  (Opus 28k mono)
"""
import os, subprocess, sys, json

BASE = "/home/z/my-project"
VOICE_DIR = f"{BASE}/scripts/voice"
MODEL = f"{VOICE_DIR}/models/en_US-lessac-medium.onnx"
PIPER = f"{VOICE_DIR}/piper/piper"
WAV_DIR = f"{VOICE_DIR}/wav_en"
OGG_DIR = f"{VOICE_DIR}/ogg_en"

for d in (WAV_DIR, OGG_DIR):
    os.makedirs(d, exist_ok=True)

NUM_WORDS = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty one",
    "twenty two", "twenty three", "twenty four", "twenty five", "twenty six",
    "twenty seven", "twenty eight", "twenty nine",
]
ATOMS = {}
for i, w in enumerate(NUM_WORDS):
    ATOMS[f"n{i}"] = w
for t in (30, 40, 50, 60, 70, 80, 90):
    ATOMS[f"n{t}"] = {30: "thirty", 40: "forty", 50: "fifty", 60: "sixty",
                      70: "seventy", 80: "eighty", 90: "ninety"}[t]
ATOMS["y"] = "to"          # conector del marcador: "11 to 5" (misma clave que es "a")
ATOMS["a"] = "to"
ATOMS.update({
    # frases completas del juego (part3)
    "modo_supervivencia": "Survival mode. Keep the rally going!",
    "modo_partido": "Match mode. Good luck!",
    "bienvenido": "Welcome to the match. Good luck!",
    "rival_conectado": "Opponent connected. Let's play!",
    "rival_desconectado": "Opponent disconnected",
    "sala_pabellon": "Gym arena",
    "sala_neon": "Neon arena",
    "sala_atardecer": "Sunset arena",
    "sala_artico": "Arctic arena",
    "dificultad_facil": "Easy difficulty",
    "dificultad_media": "Medium difficulty",
    "dificultad_dificil": "Hard difficulty",
    "logro_desbloqueado": "Achievement unlocked!",
    # nombres de los 6 logros (ACHIEVEMENTS en part1)
    "ach_primera": "First victory",
    "ach_racha": "On a roll",
    "ach_gigante": "Giant",
    "ach_maraton": "Marathoner",
    "ach_superviv": "Survivor",
    "ach_aces": "Ace serve",
    # piezas del marcador dinámico
    "rallye_de": "Rally of",
    "golpes": "hits",
    "nuevo_record": "New record!",
    "saque_para_ti": "Your serve",
    "saque_para_rival": "Serve for your opponent",
    "saque_para_maquina": "Serve for the machine",
    "victoria": "Victory!",
    "partido_para_cpu": "Match for the machine.",
    "partido_para_rival": "Match for your opponent.",
})

def synth(key, text):
    wav = f"{WAV_DIR}/{key}.wav"
    r = subprocess.run([PIPER, "-m", MODEL, "-f", wav],
                       input=text.encode("utf-8"),
                       capture_output=True, timeout=90)
    if r.returncode != 0 or not os.path.isfile(wav) or os.path.getsize(wav) < 2000:
        raise RuntimeError(f"piper falló para {key}: rc={r.returncode} {r.stderr[-200:]}")
    return wav

def to_opus(wav, key):
    ogg = f"{OGG_DIR}/{key}.ogg"
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav,
                        "-c:a", "libopus", "-b:a", "28k", "-ac", "1",
                        "-application", "audio", ogg],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or not os.path.isfile(ogg) or os.path.getsize(ogg) < 400:
        raise RuntimeError(f"ffmpeg falló para {key}: {r.stderr[-200:]}")
    return ogg

def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0

def main():
    only = sys.argv[1:] or None
    report = {}
    for key, text in ATOMS.items():
        if only and key not in only:
            continue
        wav = synth(key, text)
        ogg = to_opus(wav, key)
        d = duration(wav)
        report[key] = {"text": text, "seg": round(d, 2),
                       "wav_kb": round(os.path.getsize(wav) / 1024, 1),
                       "ogg_b": os.path.getsize(ogg)}
        flag = "" if 0.12 <= d <= 8.0 else "  << DURACIÓN SOSPECHOSA"
        print(f"{key:22s} {d:5.2f}s  {report[key]['ogg_b']:6d}B  {text}{flag}", flush=True)
    total_b = sum(v["ogg_b"] for v in report.values())
    print(f"\n{len(report)} átomos · {total_b/1024:.0f} KB en OGG "
          f"(~{total_b*4/3/1024:.0f} KB en base64)")
    with open(f"{VOICE_DIR}/gen_report_en.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
