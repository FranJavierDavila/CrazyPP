#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 127 · GENERADOR DEL DIRECTORIO DE RELEASE v36116
========================================================================
Crea scripts/release-v36116/ a partir de scripts/release-v36115/ con:
  · reemplazos de versión (3.6.115-SDK6 → 3.6.116-SDK6 · v36115 → v36116)
  · bloque de notas del VERSION.txt nuevo (FASE 118 — P4.2 ·
    AUTODIAGNÓSTICO DE VERSIÓN AL ARRANCAR), por MARCADORES (NL literal,
    patrón gen_release de la casa).
  · ORDEN CORREGIDO respecto a r126: el barrido de tokens corre ANTES de
    insertar las notas — la historia (r126: host 3.6.114 vs invitado
    3.6.102) queda honesta en el VERSION.txt en vez de ser barrida.
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36116 ya existe, lo regenera desde cero.
RAIZ apunta al repo real (/home/z/my-project/upload) — el mount vivo.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project/upload")
ORIGEN = RAIZ / "scripts" / "release-v36115"
DEST = RAIZ / "scripts" / "release-v36116"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 118 — P4.2 · AUTODIAGNÓSTICO DE VERSIÓN",
    "AL ARRANCAR: ningún build viejo vuelve a colarse en silencio).",
    "  · EL RESIDUO DE P4.1: el aviso por HELLO (verCompara, r126) sólo",
    "    ve al RIVAL. Si los DOS cascos retoman pestañas viejas de la",
    "    MISMA versión (boots de 3.6.100/107/108/110/111 conviviendo en",
    "    el Quest Browser), el enlace queda limpio y el desajuste con la",
    "    web es invisible: el HELLO no puede verlo.",
    "  · FIX C · SELF-CHECK AL ARRANCAR: verSelf (c09b, pura y testable)",
    "    + PPNET.selfcheckVersion — el constructor del juego (c12) la",
    "    dispara tras crear el enlace: el build corriendo se compara",
    "    contra PAGES-VERSION.txt?now=<ts> (cache: no-store, tope 4 s),",
    "    que el service worker sirve RED PRIMERO (VIVAS) — fresco siempre",
    "    que hay Internet. Distinto → aviso EN LA SALA: mensaje de pista",
    "    (rules.message), voz de megáfono y fila roja del panel",
    "    multijugador con PRIORIDAD sobre la del rival (recargar MI",
    "    visor lo arregla todo, el rival incluido si era caché).",
    "  · TELEMETRÍA: ver_selfcheck UNA vez por sesión y SIEMPRE",
    "    (coincida o no) — censo de builds vivos para ver los «boots",
    "    conviviendo» que hundieron la primera partida real.",
    "  · OFFLINE REINA: sin red, timeout o fichero sin sello → silencio",
    "    absoluto; fire-and-forget, jamás bloquea el arranque.",
    "  · I18N: net_selfcheck_warn / net_selfcheck_voice en ES y EN.",
    "  · HIGIENE: bump_version.py y build_game.py apuntan de nuevo al",
    "    mount vivo del repo (upload) como deploy_pages.py desde la r126.",
    "  · TEST NUEVO: test_p4_selfcheck_v36116 (41/0) — verSelf y",
    "    selfcheckVersion en la fuente real (fetch simulado: aviso,",
    "    censo único, silencio sin red/404/sin sello) + cableado c12/c00",
    "    + garantías del sw.js. QA r127 en verde: test_red_nucleo 60/0 ·",
    "    test_p4_ver_mismatch 27/0 · test_p4_ice 21/0 · test_f1_decode",
    "    6/0 · test_m7e_persistencia 19/0 · worker local 79/0 ·",
    "    sintaxis del bundle OK · bump BYTE-EXACTO (10.731.285 B).",
    "  SE CONSERVA TODO: P4.1 (aviso EN LA SALA + cache-busting),",
    "    M-RED3, M7e persistencia, CRAZY LINK v2, ELO unificado,",
    "    matchmaking, reto semanal, superpoderes y academia.",
    "  · sellada a",
    "  3.6.116",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36115", "release-v36116"),
    ("staging-v36115", "staging-v36116"),
    ("V3.6.115-SDK6", "V3.6.116-SDK6"),
    ("3.6.115-SDK6", "3.6.116-SDK6"),
    ("v36115-sdk6", "v36116-sdk6"),
    ("v36115", "v36116"),
    ("3.6.115", "3.6.116"),
]

# Marcadores sobre el ESTADO POST-SWEEP (el sweep ya convirtió el bloque
# de notas de r126 a 3.6.116; lo sustituimos entero por el de FASE 118).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 117"
FIN_MARCADOR = "'  3.6.116" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.116-SDK6 lista: P4.1 aviso de build EN LA SALA + cache-busting del landing — la lección de la primera partida real.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.116-SDK6 lista: P4.2 autodiagnóstico de versión al arrancar — ningún build viejo vuelve a colarse en silencio.')"

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
        # 1 · barrido de tokens de versión (ANTES de las notas: la
        #     historia de r126 que queda fuera del bloque no se corrompe)
        for viejo, nuevo in TOKENS:
            t = t.replace(viejo, nuevo)
        # 2 · notas FASE 118 (del marcador INI al FIN inclusive)
        i = t.find(INI_MARCADOR)
        if i >= 0:
            j = t.find(FIN_MARCADOR, i)
            if j >= 0:
                t = t[:i] + _NOTAS.rstrip("\n") + t[j + len(FIN_MARCADOR):]
        # 3 · línea final de resumen
        if LINEA_FINAL_VIEJA in t:
            t = t.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        if t != orig:
            p.write_text(t, encoding="utf-8")
            tocados += 1
            print(f"  ✓ {p.relative_to(DEST)}")
    print(f"\nrelease-v36116 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36116/build_zip.py (ZIPs)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
