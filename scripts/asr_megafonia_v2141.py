#!/usr/bin/env python3
"""V2.141 · Verificación ASR de los átomos NUEVOS de MEGAFONÍA.

Compara las variantes es LITERAL vs FONÉTICA de los nombres nuevos:
  · mega_salida_gd (es) — «Gold Dust» literal vs «Gol Dast»
  · mega_salida_sc (es) — «Silver Creek» literal vs «Silver Cric»
  · mega_llega_gd / mega_llega_sc (es)
  · los 4 átomos EN (literal, el lessac los lee bien)
El criterio de v2.140 se mantiene: si el ASR (que traduce el audio ES a
chino) no discrimina, gana el LITERAL — consistente con «Dry Gulch»,
«Perdido» y «Bravos» ya sellados.
"""
import json, os, subprocess, sys, time, unicodedata

BASE = "/home/z/my-project"
VOICE_DIR = f"{BASE}/scripts/voice"
WAV_DIR = f"{VOICE_DIR}/wav"

CHECK = {
    ("mega_salida_gd", "es"): "Pasajeros al tren, partimos hacia Gold Dust.",
    ("mega_salida_gd_fon", "es"): "Pasajeros al tren, partimos hacia Gold Dust.",
    ("mega_salida_sc", "es"): "Pasajeros al tren, partimos hacia Silver Creek.",
    ("mega_salida_sc_fon", "es"): "Pasajeros al tren, partimos hacia Silver Creek.",
    ("mega_llega_gd", "es"): "En menos de veinticinco segundos llegaremos a Gold Dust.",
    ("mega_llega_gd_fon", "es"): "En menos de veinticinco segundos llegaremos a Gold Dust.",
    ("mega_llega_sc", "es"): "En menos de veinticinco segundos llegaremos a Silver Creek.",
    ("mega_llega_sc_fon", "es"): "En menos de veinticinco segundos llegaremos a Silver Creek.",
    ("mega_salida_gd", "en"): "All aboard! We are departing towards Gold Dust.",
    ("mega_salida_sc", "en"): "All aboard! We are departing towards Silver Creek.",
    ("mega_llega_gd", "en"): "In less than twenty-five seconds we will arrive at Gold Dust.",
    ("mega_llega_sc", "en"): "In less than twenty-five seconds we will arrive at Silver Creek.",
}

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    for ch in ".,!?¡¿:;":
        s = s.replace(ch, " ")
    return " ".join(s.split())

def asr(path, tries=4):
    out = f"{VOICE_DIR}/_asr_tmp_v2141.json"
    for i in range(tries):
        r = subprocess.run(["z-ai", "asr", "-f", path, "-o", out],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and os.path.isfile(out):
            try:
                return json.load(open(out, encoding="utf-8"))["text"].strip()
            except Exception:
                pass
        time.sleep(18 * (i + 1))
    return None

def nombre_en(got, nombres):
    """¿El ASR 'oyó' el nombre (o su eco fonético) en cualquier idioma?"""
    if not got:
        return False
    g = norm(got)
    eco = {"gold dust": ["gold dust", "gol dust", "goldust", "gold dust."],
           "silver creek": ["silver creek", "silver cric", "silber creek", "silvercreek"]}
    for n in nombres:
        for e in eco[n] + [n]:
            if e in g or e.replace(" ", "") in g.replace(" ", ""):
                return True
    # el ASR chino traduce el nombre (p.ej. «戈尔德斯特»): buscamos pistas
    hints = {"gold dust": ["金", "戈", "达斯特", "多斯特"],
             "silver creek": ["银", "西尔弗", "克里克", "溪"]}
    for n in nombres:
        if any(h in got for h in hints[n]):
            return True
    return False

def main():
    results = {}
    for (key, lang), expected in CHECK.items():
        wav = f"{WAV_DIR}/{key}_{lang}.wav"
        got = asr(wav)
        ok = nombre_en(got, ["gold dust"] if "gd" in key else ["silver creek"]) \
            if lang == "es" else (norm(expected) == norm(got)
                                  or norm(expected) in norm(got))
        results[f"{key}:{lang}"] = {"esperado": expected, "asr": got, "ok": bool(ok)}
        print(f"{'OK ' if ok else 'MAL'} {key}:{lang}\n     ASR: {got}")
        time.sleep(6)
    with open(f"{BASE}/scripts/megafonia_v2141_asr.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    lit = all(results[f"{k}:es"]["ok"] for k in
              ("mega_salida_gd", "mega_salida_sc", "mega_llega_gd", "mega_llega_sc"))
    fon = all(results[f"{k}:es"]["ok"] for k in
              ("mega_salida_gd_fon", "mega_salida_sc_fon",
               "mega_llega_gd_fon", "mega_llega_sc_fon"))
    print(f"\nES literal {'VERDE' if lit else 'dudoso'} · ES fonético {'VERDE' if fon else 'dudoso'}"
          f" → elegido: {'literal (consistente con v2.140)' if lit or not fon else 'FONÉTICO'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
