#!/usr/bin/env python3
"""r65 · Inserta los átomos tutv*/tutok/tutotra en los bancos de voz de
c00_pre_three.js (VOICE_B64 = es · VOICE_B64_EN = en). Idempotente: si la
clave ya existe, se sustituye por la versión nueva.

Regenerar átomos primero:  python3 scripts/gen_voice_r65.py
"""
import base64, os, re, sys

RAIZ = "/home/z/my-project"
C00 = f"{RAIZ}/src/game/core/c00_pre_three.js"
OGG_ES = f"{RAIZ}/scripts/voice_r65/ogg_es"
OGG_EN = f"{RAIZ}/scripts/voice_r65/ogg_en"

def entradas(directorio, indent="  "):
    filas = []
    for f in sorted(os.listdir(directorio)):
        if not f.endswith(".ogg"):
            continue
        k = f[:-4]
        b = open(f"{directorio}/{f}", "rb").read()
        b64 = base64.b64encode(b).decode("ascii")
        assert "</" not in b64, "base64 no puede contener </"
        filas.append(f'{indent}{k}: "{b64}",')
    return filas

def insertar(texto, nombre_const, filas):
    # localiza `const <nombre> = {` … y el cierre `};` al nivel 0
    ini = texto.index(f"const {nombre_const} = {{")
    fin = texto.index("\n};", ini)
    cuerpo = texto[ini:fin]
    nuevas = []
    sustituidas = 0
    for fila in filas:
        k = re.match(r"\s*([A-Za-z0-9_]+):", fila).group(1)
        patron = re.compile(rf"\n[ \t]+{k}: \"[^\"]*\",")
        if patron.search(cuerpo):
            cuerpo = patron.sub("\n" + fila.strip(), cuerpo, count=1)
            sustituidas += 1
        else:
            nuevas.append(fila)
    cuerpo = cuerpo + "\n" + "\n".join(nuevas) if nuevas else cuerpo
    return texto[:ini] + cuerpo + texto[fin:], len(nuevas), sustituidas

txt = open(C00, encoding="utf-8").read()
filas_es = entradas(OGG_ES)
filas_en = entradas(OGG_EN)
txt2, n_es, s_es = insertar(txt, "VOICE_B64", filas_es)
txt3, n_en, s_en = insertar(txt2, "VOICE_B64_EN", filas_en)
open(C00, "w", encoding="utf-8").write(txt3)
print(f"VOICE_B64   · {n_es} nuevas, {s_es} sustituidas")
print(f"VOICE_B64_EN· {n_en} nuevas, {s_en} sustituidas")
print(f"c00 ahora: {len(txt3)/1024:.0f} KB (antes {len(txt)/1024:.0f} KB)")
