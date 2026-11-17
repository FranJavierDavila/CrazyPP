#!/usr/bin/env python3
"""V2.140 · Verificación ASR de los átomos de MEGAFONÍA (rate-limit friendly).

Comprueba que los nombres de estación suenen bien:
  · mega_salida_dg (es)  — literal «Dry Gulch» vs fonética «Drai Gulch»
  · mega_salida_dg (en)
  · mega_salida_pd (es)  · mega_salida_br (es) · mega_oro (es)
  · mega_llega_dg (en)   · mega_oro (en)
"""
import json, os, subprocess, sys, time, unicodedata

BASE = "/home/z/my-project"
VOICE_DIR = f"{BASE}/scripts/voice"
WAV_DIR = f"{VOICE_DIR}/wav"

CHECK = {
    ("mega_salida_dg", "es"): "Pasajeros al tren, partimos hacia Dry Gulch.",
    ("mega_salida_dg_fon", "es"): "Pasajeros al tren, partimos hacia Drai Gulch.",
    ("mega_salida_pd", "es"): "Pasajeros al tren, partimos hacia Perdido.",
    ("mega_salida_br", "es"): "Pasajeros al tren, partimos hacia Bravos.",
    ("mega_oro", "es"): "Cargamento de oro a buen recaudo.",
    ("mega_salida_dg", "en"): "All aboard! We are departing towards Dry Gulch.",
    ("mega_llega_dg", "en"): "In less than twenty-five seconds we will arrive at Dry Gulch.",
    ("mega_oro", "en"): "The gold shipment is safe and sound.",
}

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    for ch in ".,!?¡¿:;":
        s = s.replace(ch, " ")
    return " ".join(s.split())

def asr(path, tries=4):
    out = f"{VOICE_DIR}/_asr_tmp_v2140.json"
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

def close(expected, got):
    if not got:
        return False
    e, g = norm(expected), norm(got)
    if e == g:
        return True
    ew, gw = set(e.split()), set(g.split())
    return ew.issubset(gw) or len(ew & gw) >= max(1, len(ew) - 1)

def main():
    results = {}
    for (key, lang), expected in CHECK.items():
        wav = f"{WAV_DIR}/{key}_{lang}.wav"
        got = asr(wav)
        ok = close(expected, got)
        results[f"{key}:{lang}"] = {"esperado": expected, "asr": got, "ok": ok}
        print(f"{'OK ' if ok else 'MAL'} {key}:{lang}\n     ASR: {got}")
        time.sleep(6)
    with open(f"{BASE}/scripts/megafonia_v2140_asr.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    bad = [k for k, v in results.items() if not v["ok"]]
    print(f"\n{'TODOS OK' if not bad else 'FALLOS: ' + ', '.join(bad)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
