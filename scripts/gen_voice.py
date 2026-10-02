#!/usr/bin/env python3
"""v2.20 · Genera los átomos de voz del megáfono con Piper TTS (es_ES-davefx-medium).

Produce:
  scripts/voice/wav/<key>.wav  (22050 Hz mono, salida nativa de piper)
  scripts/voice/ogg/<key>.ogg  (Opus 28k mono, para incrustar en el HTML)

Los átomos son las piezas mínimas que el juego concatena para anunciar:
números 0-29, decenas, 'y'/'a', frases completas, nombres de logros, etc.
"""
import os, subprocess, sys, json

BASE = "/home/z/my-project"
VOICE_DIR = f"{BASE}/scripts/voice"
MODEL = f"{VOICE_DIR}/models/es_ES-davefx-medium.onnx"
PIPER = f"{VOICE_DIR}/piper/piper"       # binario oficial (release 2023.11.14-2)
WAV_DIR = f"{VOICE_DIR}/wav"
OGG_DIR = f"{VOICE_DIR}/ogg"

for d in (WAV_DIR, OGG_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- átomos ---
NUM_WORDS = [
    "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis",
    "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidós",
    "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete",
    "veintiocho", "veintinueve",
]
ATOMS = {}
for i, w in enumerate(NUM_WORDS):
    ATOMS[f"n{i}"] = w
for t in (30, 40, 50, 60, 70, 80, 90):
    ATOMS[f"n{t}"] = {30: "treinta", 40: "cuarenta", 50: "cincuenta", 60: "sesenta",
                      70: "setenta", 80: "ochenta", 90: "noventa"}[t]
ATOMS["y"] = "y"
ATOMS["a"] = "a"
ATOMS.update({
    # frases completas del juego (part3)
    "modo_supervivencia": "Modo supervivencia. ¡Aguanta el rallye!",
    "modo_partido": "Modo partido. ¡Buena suerte!",
    "bienvenido": "Bienvenido al partido. ¡Buena suerte!",
    "rival_conectado": "Rival conectado. ¡A jugar!",
    "rival_desconectado": "Rival desconectado",
    "sala_pabellon": "Sala Pabellón",
    "sala_neon": "Sala Neón",
    "sala_atardecer": "Sala Atardecer",
    "sala_artico": "Sala Ártico",
    "dificultad_facil": "Dificultad fácil",
    "dificultad_media": "Dificultad media",
    "dificultad_dificil": "Dificultad difícil",
    "logro_desbloqueado": "¡Logro desbloqueado!",
    # nombres de los 6 logros (ACHIEVEMENTS en part1)
    "ach_primera": "Primera victoria",
    "ach_racha": "En racha",
    "ach_gigante": "Gigante",
    "ach_maraton": "Maratonista",
    "ach_superviv": "Superviviente",
    "ach_aces": "Saque directo",
    # piezas del marcador dinámico
    "rallye_de": "Rallye de",
    "golpes": "golpes",
    "nuevo_record": "¡Nuevo récord!",
    "saque_para_ti": "Saque para ti",
    "saque_para_rival": "Saque para tu rival",
    "saque_para_maquina": "Saque para la máquina",
    "victoria": "¡Victoria!",
    "partido_para_cpu": "Partido para la máquina.",
    "partido_para_rival": "Partido para tu rival.",
})

# ------------------------------------------------------------- síntesis ---
def synth(key, text):
    wav = f"{WAV_DIR}/{key}.wav"
    # el binario oficial lee el texto por STDIN (archivo positional se bloquea)
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
        print(f"{key:22s} {d:5.2f}s  {report[key]['ogg_b']:6d}B  {text}{flag}")
    total_b = sum(v["ogg_b"] for v in report.values())
    print(f"\n{len(report)} átomos · {total_b/1024:.0f} KB en OGG "
          f"(~{total_b*4/3/1024:.0f} KB en base64)")
    with open(f"{VOICE_DIR}/gen_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
