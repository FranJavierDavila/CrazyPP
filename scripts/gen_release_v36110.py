#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 121 · GENERADOR DEL DIRECTORIO DE RELEASE v36110
========================================================================
Crea scripts/release-v36110/ a partir de scripts/release-v36109/ con:
  · reemplazos de versión (3.6.109-SDK6 → 3.6.110-SDK6 · v36109 → v36110)
  · bloque de notas del VERSION.txt nuevo (FASE 112 — M-RED · MULTIJUGADOR
    VERIFICADO: pose fresca para juzgar + cadencia sin toss en el validador;
    saque del invitado con rotación ITTF en el banco S3 y en la batería de
    4 puntos), por MARCADORES (NL literal, patrón gen_release de la casa).
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36110 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36109"
DEST = RAIZ / "scripts" / "release-v36110"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 112 — M-RED · MULTIJUGADOR VERIFICADO",
    "(r121).",
    "  El requisito número 1 del dueño: partidas online entre dos",
    "  humanos con garantías. Dos defectos REALES del validador",
    "  cazados por el banco de duelo y reparados; cobertura nueva",
    "  del hueco que quedaba sin probar: el SAQUE DEL INVITADO.",
    "  · POSE FRESCA PARA JUZGAR (c09 §12 + c09b VP): la muestra",
    "    de pose con la que se valida un golpe o saque remoto es",
    "    la MÁS PRÓXIMA a tHit en ambas direcciones y a ±150 ms",
    "    (POSE_FRESH_MS). Antes, un hueco sin pose (arranque,",
    "    degradación, ráfaga de pérdida) juzgaba el saque contra",
    "    una pala FANTASMA de hace segundos → rechazo injusto →",
    "    «no deja sacar». Sin pose fiable se OMITE el chequeo de",
    "    distancia; los frenos duros (velocidad, giro, cadencia,",
    "    correlativo) siguen intactos.",
    "  · LA CADENCIA CUENTA GOLPES, NO LANZAMIENTOS (c09): el",
    "    toss (kind 2) ya no sella _lastRemoteHitT — un saque",
    "    ejecutado rápido tras el lanzamiento es juego legal, no",
    "    trampa (antes el validador lo rechazaba por «cadencia",
    "    <150 ms» → «no deja sacar»).",
    "  · BANCO DE DUELO S3 (diag_multijugador_r110): saque del",
    "    invitado con la ROTACIÓN ITTF tras 2 puntos — toss kind",
    "    2 visible en el anfitrión, saque kind 1 con correlativo,",
    "    autoridad por HANDOFF y devolución del anfitrión. Verde",
    "    también con red adversaria (120 ms ±40, 5 % pérdida).",
    "    El banco se auto-repara en clones limpios (ppdiag).",
    "  · BATERÍA MULTI DE 4 PUNTOS (bateria_multi_v3674): puntos",
    "    3-4 con el invitado SACANDO — rotación de sacador en",
    "    vivo. P1 LAN 67 · P2 WIFI 68 · P3 TÚNEL 69 checks con",
    "    0 fallos, 0 rechazos del validador y 0 pageerrors.",
    "  SE CONSERVA TODO: CRAZY LINK v2 (reloj compartido, FSM de",
    "    bola por mitades, túnel PeerJS, claims/resync), ELO",
    "    unificado con K por modo, matchmaking, reto diario y",
    "    semanal, MI RANKING, estilos de IA, superpoderes,",
    "    dobles 2v2, academia y PRO TRAINING.",
    "  QA r121 en verde: banco 18/0 (nominal y adversaria),",
    "    test_red_nucleo 59/0, qa_r81 136/0, qa_r82 48/0,",
    "    batería P1/P2/P3 con 4 puntos cada una 0 fallos.",
    "  · sellada a",
    "  3.6.110",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36109", "release-v36110"),
    ("staging-v36109", "staging-v36110"),
    ("V3.6.109-SDK6", "V3.6.110-SDK6"),
    ("3.6.109-SDK6", "3.6.110-SDK6"),
    ("v36109-sdk6", "v36110-sdk6"),
    ("v36109", "v36110"),
    ("3.6.109", "3.6.110"),
]

INI_MARCADOR = "'Rama    : main · SDK6 (FASE 111"
FIN_MARCADOR = "'  3.6.109" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.109-SDK6 lista: TELEMETRÍA reparada (array directo + routing por host, FASE 8) sobre el SDK v1.x cerrado (FASE 7).')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.110-SDK6 lista: MULTIJUGADOR verificado (pose fresca + cadencia sin toss; saque del invitado con rotación ITTF en banco S3 y batería de 4 puntos) sobre el CRAZY LINK v2 cerrado.')"

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
        # 1 · notas FASE 112 (del marcador INI al FIN inclusive)
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
    print(f"\nrelease-v36110 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36110/build_zip.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
