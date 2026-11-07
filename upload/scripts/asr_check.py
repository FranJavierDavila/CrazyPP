#!/usr/bin/env python3
"""Verificación ASR de un subconjunto de átomos de voz (rate-limit friendly)."""
import json, os, subprocess, sys, time, unicodedata

BASE = "/home/z/my-project"
VOICE_DIR = f"{BASE}/scripts/voice"

CHECK = {
    "n0": "cero", "n11": "once", "n16": "dieciséis", "n21": "veintiuno",
    "n29": "veintinueve", "n30": "treinta", "y": "y", "a": "a",
    "rallye_de": "Rallye de", "golpes": "golpes", "nuevo_record": "Nuevo récord",
    "sala_artico": "Sala Ártico", "modo_supervivencia": "Modo supervivencia. Aguanta el rallye.",
    "partido_para_cpu": "Partido para la máquina.", "dificultad_dificil": "Dificultad difícil",
    "ach_maraton": "Maratonista", "saque_para_rival": "Saque para tu rival",
}

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    for ch in ".,!?¡¿:;":
        s = s.replace(ch, " ")
    return " ".join(s.split())

def asr(path, tries=4):
    out = f"{VOICE_DIR}/_asr_tmp.json"
    for i in range(tries):
        r = subprocess.run(["z-ai", "asr", "-f", path, "-o", out],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and os.path.isfile(out):
            try:
                return json.load(open(out, encoding="utf-8"))["text"].strip()
            except Exception:
                pass
        time.sleep(20 * (i + 1))     # 429 -> esperar y reintentar
    return None

def close(expected, got):
    if not got:
        return False
    e, g = norm(expected), norm(got)
    if e == g:
        return True
    # tolerancia para átomos de una letra y palabras sueltas
    if len(e) <= 3:
        return e in g.split() or g in e
    # contención difusa: todas las palabras esperadas aparecen
    ew = set(e.split())
    gw = set(g.split())
    return ew.issubset(gw) or len(ew & gw) >= max(1, len(ew) - 1)

def main():
    only = sys.argv[1:] or list(CHECK)
    ok, bad = 0, []
    for i, key in enumerate(only):
        exp = CHECK[key]
        wav = f"{VOICE_DIR}/wav/{key}.wav"
        if not os.path.isfile(wav):
            bad.append((key, exp, "sin wav")); continue
        time.sleep(3.5)
        got = asr(wav)
        if close(exp, got):
            ok += 1
            print(f"OK   {key:20s} esp='{exp}'  asr='{got}'")
        else:
            bad.append((key, exp, got))
            print(f"MAL  {key:20s} esp='{exp}'  asr='{got}'")
    print(f"\n{ok}/{ok+len(bad)} átomos verificados correctamente")
    if bad:
        print("REVISAR:", json.dumps(bad, ensure_ascii=False))
    sys.exit(0 if not bad else 1)

if __name__ == "__main__":
    main()
