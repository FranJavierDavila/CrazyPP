#!/usr/bin/env python3
"""r78 · Inserta los átomos del paso 7 REGENERADOS (tutv8a, tutv8b, tutv9a,
tutv9b) + el átomo NUEVO (tutv9c) en los bancos de voz de c00_pre_three.js
(VOICE_B64 = es · VOICE_B64_EN = en). Generados por gen_voice_r78.py.

Misma mecánica de insertar_voz_r74.py: NO re-sustituye el banco completo
(las demás claves quedan intactas, byte a byte — tutv8c incluida, que no
cambia esta ronda). Idempotente: si la clave ya existe, la sustituye.
"""
import base64
import os
import re

RAIZ = "/home/z/my-project"
C00 = f"{RAIZ}/src/game/core/c00_pre_three.js"
OGG_ES = f"{RAIZ}/scripts/voice_r65/ogg_es"
OGG_EN = f"{RAIZ}/scripts/voice_r65/ogg_en"
CLAVES = ["tutv8a", "tutv8b", "tutv9a", "tutv9b", "tutv9c"]


def filas(directorio):
    out = []
    for k in CLAVES:
        p = f"{directorio}/{k}.ogg"
        if not os.path.exists(p):
            raise SystemExit(f"FALTA {p} — ejecuta antes gen_voice_r78.py")
        b = open(p, "rb").read()
        b64 = base64.b64encode(b).decode("ascii")
        assert "</" not in b64, "base64 no puede contener </"
        out.append((k, f'  {k}: "{b64}",'))
    return out


def insertar(texto, nombre_const, entradas):
    ini = texto.index(f"const {nombre_const} = {{")
    fin = texto.index("\n};", ini)
    cuerpo = texto[ini:fin]
    nuevas = []
    sustituidas = 0
    for k, fila in entradas:
        patron = re.compile(rf"\n[ \t]*{k}: \"[^\"]*\",")
        if patron.search(cuerpo):
            cuerpo = patron.sub("\n" + fila, cuerpo, count=1)
            sustituidas += 1
        else:
            nuevas.append(fila)
    cuerpo = cuerpo + "\n" + "\n".join(nuevas) if nuevas else cuerpo
    return texto[:ini] + cuerpo + texto[fin:], len(nuevas), sustituidas


txt = open(C00, encoding="utf-8").read()
t2, n_es, s_es = insertar(txt, "VOICE_B64", filas(OGG_ES))
t3, n_en, s_en = insertar(t2, "VOICE_B64_EN", filas(OGG_EN))
open(C00, "w", encoding="utf-8").write(t3)
print(f"VOICE_B64   · {n_es} nuevas, {s_es} sustituidas")
print(f"VOICE_B64_EN· {n_en} nuevas, {s_en} sustituidas")
print(f"c00 ahora: {len(t3)/1024:.0f} KB (antes {len(txt)/1024:.0f} KB)")
