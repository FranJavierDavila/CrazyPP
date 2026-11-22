#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 125 · GENERADOR DEL DIRECTORIO DE RELEASE v36114
========================================================================
Crea scripts/release-v36114/ a partir de scripts/release-v36113/ con:
  · reemplazos de versión (3.6.113-SDK6 → 3.6.114-SDK6 · v36113 → v36114)
  · bloque de notas del VERSION.txt nuevo (FASE 116 — P4 · PRIMERA
    PARTIDA REAL: TURN de Cloudflare + diagnóstico ICE), por MARCADORES
    (NL literal, patrón gen_release de la casa).
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36114 ya existe, lo regenera desde cero.
RAIZ apunta al repo real (/home/z/my-project/upload) — el mount vivo.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project/upload")
ORIGEN = RAIZ / "scripts" / "release-v36113"
DEST = RAIZ / "scripts" / "release-v36114"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 116 — P4 · PRIMERA PARTIDA REAL:",
    "TURN DE CLOUDFLARE + DIAGNÓSTICO ICE (r125): el camino para jugar",
    "con 2 Quest por internet queda listo.",
    "  · TURN VIVO: el TURN público OpenRelay/metered.ca del juego",
    "    está MUERTO — fuera. El worker crazypp-tele estrena /api/ice,",
    "    que acuña credenciales EFÍMERAS de TURN de Cloudflare Realtime",
    "    (TTL 6 h · rtc.live generate-ice-servers) y las reparte al",
    "    juego: NAT simétrico ya no bloquea la partida. Sin token aún:",
    "    STUN honesto y turn:false — degradación limpia.",
    "  · AUTO-PROVISIONADO: el worker crea su TURN key solo (POST",
    "    accounts/*/calls/turn_keys) y la recuerda en la tabla cfg de",
    "    D1; con TURN_KEY_ID/CF_ACCOUNT_ID explícitos también vale.",
    "  · JUEGO (c09): ICE_CFG local = STUN Google + Cloudflare (sin",
    "    credenciales fijas jamás en código público) y nuevo ICE_ASYNC():",
    "    consulta /api/ice (tope 4 s), cachea 4 min, no martillea 60 s",
    "    si el worker falla; _v2Offer/_v2RemoteDesc la usan. Saneo doble",
    "    (worker + juego): urls stun/turn/turns, puerto 53 fuera",
    "    (nota oficial CF), TURN sin credencial fuera.",
    "  · DIAGNÓSTICO DEL ENLACE REAL: nuevo net_ice en telemetría —",
    "    qué camino abrió la partida (host=LAN · srflx=internet directo",
    "    · relay=TURN) y RTT; failed si el ICE muere. Con el net_match",
    "    existente, la primera partida real queda contada de principio",
    "    a fin.",
    "  · RUNBOOK NUEVO LEEME-P4-PRIMERA-PARTIDA.md: token Realtime TURN",
    "    (3 min), variable TURN_API_TOKEN, verificación /api/ice, la",
    "    partida paso a paso con 2 Quest y cómo leer el diagnóstico.",
    "  · TESTS NUEVOS: test_p4_ice_v36114 (21/0, fuente real de c09 sin",
    "    DEPS-FASE2) + worker test_local 79/0 (11 checks /api/ice).",
    "  SE CONSERVA TODO: M-RED3, M7e persistencia, CRAZY LINK v2, ELO",
    "    unificado, matchmaking, reto semanal, superpoderes y academia.",
    "  QA r125 en verde: test_p4_ice 21/0 · test_red_nucleo 60/0 ·",
    "    test_f1_decode 6/0 · test_m7e_persistencia 19/0 · worker",
    "    test_local 79/0.",
    "  · sellada a",
    "  3.6.114",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36113", "release-v36114"),
    ("staging-v36113", "staging-v36114"),
    ("V3.6.113-SDK6", "V3.6.114-SDK6"),
    ("3.6.113-SDK6", "3.6.114-SDK6"),
    ("v36113-sdk6", "v36114-sdk6"),
    ("v36113", "v36114"),
    ("3.6.113", "3.6.114"),
]

INI_MARCADOR = "'Rama    : main · SDK6 (FASE 115"
FIN_MARCADOR = "'  3.6.113" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.113-SDK6 lista: M7e PERSISTENCIA COMPLETA (historial de torneos + perfil recordado) — se cierra el M7 del roadmap.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.114-SDK6 lista: P4 PRIMERA PARTIDA REAL (TURN de Cloudflare + diagnóstico ICE) — el camino con 2 Quest queda listo.')"

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
        # 1 · notas FASE 116 (del marcador INI al FIN inclusive)
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
    print(f"\nrelease-v36114 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36114/build_zip.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
