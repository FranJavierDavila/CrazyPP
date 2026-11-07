#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 126 · GENERADOR DEL DIRECTORIO DE RELEASE v36115
========================================================================
Crea scripts/release-v36115/ a partir de scripts/release-v36114/ con:
  · reemplazos de versión (3.6.114-SDK6 → 3.6.115-SDK6 · v36114 → v36115)
  · bloque de notas del VERSION.txt nuevo (FASE 117 — P4.1 · AVISO DE
    BUILD EN LA SALA + CACHE-BUSTING: la lección de la primera partida
    real), por MARCADORES (NL literal, patrón gen_release de la casa).
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36115 ya existe, lo regenera desde cero.
RAIZ apunta al repo real (/home/z/my-project/upload) — el mount vivo.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project/upload")
ORIGEN = RAIZ / "scripts" / "release-v36114"
DEST = RAIZ / "scripts" / "release-v36115"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 117 — P4.1 · LA LECCIÓN DE LA PRIMERA",
    "PARTIDA REAL: aviso de build EN LA SALA + cache-busting del landing).",
    "  · LO QUE PASÓ (telemetría real, 2 Quest por internet): el anfitrión",
    "    jugaba en 3.6.114 y el invitado en 3.6.102 (caché vieja del",
    "    navegador) — el HELLO v2 pasó (PROTO/PHYS iguales) y la partida",
    "    se rompió: bola espejada (cada uno la veía en la mano del",
    "    rival), pala con deriva de 45º y sin voz. El aviso de build de",
    "    r82 existía pero vivía SOLO en el menú: invisible con la visera.",
    "  · FIX A · CACHE-BUSTING: el landing enlaza game.html?v=<versión>",
    "    (deploy_pages.py) — cada release fuerza descarga fresca en el",
    "    navegador del Quest y los builds antiguos dejan de circular.",
    "  · FIX B · AVISO EN LA SALA: verCompara (c09b, pura y testable) +",
    "    hello2 (c09) avisa ahora DENTRO del casco: mensaje de pista",
    "    (rules.message), voz de megáfono y fila roja en el panel",
    "    multijugador; limpia el aviso si la pareja nueva coincide.",
    "  · TELEMETRÍA: nuevo evento ver_mismatch (una vez por sesión, con",
    "    versiones de ambos lados) — los desajustes quedan contados.",
    "  · I18N: net_build_warn ES/EN reescritos (sin la referencia muerta",
    "    v3674) + net_build_voice ES/EN nuevos.",
    "  · TEST NUEVO: test_p4_ver_mismatch_v36115 (27/0) — verCompara en",
    "    la fuente real + cableado c09/c12/c00 + cache-busting del",
    "    landing. QA r126 en verde: test_red_nucleo 60/0 ·",
    "    test_f1_decode 6/0 · test_m7e_persistencia 19/0 ·",
    "    test_p4_ice 21/0 · sintaxis del bundle OK.",
    "  SE CONSERVA TODO: M-RED3, M7e persistencia, CRAZY LINK v2, ELO",
    "    unificado, matchmaking, reto semanal, superpoderes y academia.",
    "  · sellada a",
    "  3.6.115",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36114", "release-v36115"),
    ("staging-v36114", "staging-v36115"),
    ("V3.6.114-SDK6", "V3.6.115-SDK6"),
    ("3.6.114-SDK6", "3.6.115-SDK6"),
    ("v36114-sdk6", "v36115-sdk6"),
    ("v36114", "v36115"),
    ("3.6.114", "3.6.115"),
]

INI_MARCADOR = "'Rama    : main · SDK6 (FASE 116"
FIN_MARCADOR = "'  3.6.114" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.114-SDK6 lista: P4 PRIMERA PARTIDA REAL (TURN de Cloudflare + diagnóstico ICE) — el camino con 2 Quest queda listo.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.115-SDK6 lista: P4.1 aviso de build EN LA SALA + cache-busting del landing — la lección de la primera partida real.')"

def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    for p in DEST.rglob("*"):
        if not p.is_file():
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        orig = t
        # 1 · notas FASE 117 (del marcador INI al FIN inclusive)
        i = t.find(INI_MARCADOR)
        if i >= 0:
            j = t.find(FIN_MARCADOR, i)
            if j >= 0:
                t = t[:i] + _NOTAS.rstrip("\n") + t[j + len(FIN_MARCADOR):]
        # 2 · línea final de resumen
        if LINEA_FINAL_VIEJA in t:
            t = t.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        # 3 · barrido de tokens de versión
        for viejo, nuevo in TOKENS:
            t = t.replace(viejo, nuevo)
        if t != orig:
            p.write_text(t, encoding="utf-8")
            tocados += 1
            print(f"  ✓ {p.relative_to(DEST)}")
    print(f"\nrelease-v36115 generado ({tocados} ficheros tocados).")
    print("Siguiente: copiar a /home/z/my-project/scripts/ y correr build_zip.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
