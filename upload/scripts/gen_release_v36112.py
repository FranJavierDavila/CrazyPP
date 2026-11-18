#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 123 · GENERADOR DEL DIRECTORIO DE RELEASE v36112
========================================================================
Crea scripts/release-v36112/ a partir de scripts/release-v36111/ con:
  · reemplazos de versión (3.6.111-SDK6 → 3.6.112-SDK6 · v36111 → v36112)
  · bloque de notas del VERSION.txt nuevo (FASE 114 — M-RED3 ·
    ENDURECIMIENTO DEL DECODIFICADOR FAST: cap de eventos al máximo del
    protocolo (spec §5) y escudo try/catch en el canal fast; test F1
    nuevo 6/0), por MARCADORES (NL literal, patrón gen_release de la casa).
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36112 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36111"
DEST = RAIZ / "scripts" / "release-v36112"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 114 — M-RED3 · ENDURECIMIENTO DEL",
    "DECODIFICADOR FAST (r123): segunda ronda de análisis multijugador",
    "— blindaje del códec binario y del canal fast del CRAZY LINK v2.",
    "  · CAP AL MÁXIMO DEL PROTOCOLO (c09b, spec §5): el decodificador",
    "    aceptaba hasta MAX_EVENTS+8 (16) eventos por paquete aunque el",
    "    emisor YA sella a 8 al codificar — un paquete corrupto o hostil",
    "    no debe poder entregar más de lo que el protocolo permite.",
    "  · ESCUDO DEL CANAL FAST (c09 _onFast): un paquete malformado",
    "    (nEvs > bytes reales) lanzaba RangeError DENTRO del handler del",
    "    datachannel y abortaba el procesado del paquete (eco NTP, acks,",
    "    reloj, pérdida). Ahora se descarta como caído y el enlace",
    "    sigue — el siguiente paquete se procesa normal.",
    "  · TEST NUEVO test_f1_decode_v36112 (6/0): honesto con 8 eventos,",
    "    hostil 16→8, malformado→descarte limpio, regresiones de cabecera",
    "    (< HDR) y de PROTO, y roundtrip de un HIT honesto intacto.",
    "  SE CONSERVA TODO: la revisión completa M-RED2 (resync con",
    "    perspectiva, guardia de estado ante HIT atrasados, claim sin",
    "    autoridad, toss caído, higiene RTC), CRAZY LINK v2 (reloj",
    "    compartido, FSM de bola por mitades, túnel PeerJS, claims/resync),",
    "    ELO unificado, matchmaking, reto diario y semanal, MI RANKING,",
    "    estilos de IA, superpoderes, dobles 2v2, academia y PRO TRAINING.",
    "  QA r123 en verde: test_red_nucleo 60/0 · test_f1_decode 6/0 ·",
    "    cadena qa por trozos.",
    "  · sellada a",
    "  3.6.112",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36111", "release-v36112"),
    ("staging-v36111", "staging-v36112"),
    ("V3.6.111-SDK6", "V3.6.112-SDK6"),
    ("3.6.111-SDK6", "3.6.112-SDK6"),
    ("v36111-sdk6", "v36112-sdk6"),
    ("v36111", "v36112"),
    ("3.6.111", "3.6.112"),
]

INI_MARCADOR = "'Rama    : main · SDK6 (FASE 113"
FIN_MARCADOR = "'  3.6.111" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.111-SDK6 lista: REVISIÓN COMPLETA del netcode (resync con perspectiva, guardia de estado, claim sin autoridad, toss caído, higiene) + fuga del 2v2 + PULSO en el camino vivo.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.112-SDK6 lista: ENDURECIMIENTO del decodificador fast (cap de eventos spec §5 + escudo en el canal fast) sobre la revisión completa M-RED2.')"

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
        # 1 · notas FASE 114 (del marcador INI al FIN inclusive)
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
    print(f"\nrelease-v36112 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36112/build_zip.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
