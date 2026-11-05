#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 122 · GENERADOR DEL DIRECTORIO DE RELEASE v36111
========================================================================
Crea scripts/release-v36111/ a partir de scripts/release-v36110/ con:
  · reemplazos de versión (3.6.110-SDK6 → 3.6.111-SDK6 · v36110 → v36111)
  · bloque de notas del VERSION.txt nuevo (FASE 113 — M-RED2 · REVISIÓN
    COMPLETA PEDIDA POR EL DUEÑO: 12 hallazgos del netcode reparados
    (resync con perspectiva = marcador invertido, guardia de estado ante
    HIT atrasados, claim sin autoridad, toss caído, higiene RTC/timers),
    fuga del 2v2 a la academia y PULSO/reto semanal en el camino vivo),
    por MARCADORES (NL literal, patrón gen_release de la casa).
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36111 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36110"
DEST = RAIZ / "scripts" / "release-v36111"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 113 — M-RED2 · REVISIÓN COMPLETA DEL",
    "NETCODE (r122), a petición expresa del dueño («revisión completa",
    "para ver si tenemos algún bug»). Dos revisiones con ojos frescos",
    "(netcode íntegro + diffs r119/r120) más la cadena QA al completo:",
    "12 hallazgos reales, todos reparados quirúrgicamente.",
    "  · RESYNC CON PERSPECTIVA (c09, CRÍTICO): _applyResync aplicaba",
    "    sp/sa/sv/fs/gp/ga/lh EN CRUDO — el único camino que no",
    "    remapeaba (v1 applySync y mstart sí): el invitado quedaba con",
    "    el MARCADOR DEL REVÉS tras una resincronización y podía",
    "    coronar victoria/ELO falsos. Ahora espeja exactamente como",
    "    applySync; el RESYNC transporta también gameOpener (rotación",
    "    de saque correcta si el resync cruza un cambio de juego).",
    "  · GUARDIA DE ESTADO (c09): un HIT atrasado/duplicado ya NO",
    "    resucita un rallye puntuado (espejo de la guardia v1); el",
    "    rechazo del validador pide RESYNC (resync-req) — un saque",
    "    legal rechazado ya no deja a un lado atascado para siempre.",
    "  · CLAIM SIN AUTORIDAD (c09b): tras un cruce ambos extremos son",
    "    ghost y NADIE reclamaba — puntos opuestos divergían en",
    "    silencio. Ahora ambos reclaman: onClaim confronta y el host",
    "    resincroniza (la divergencia es detectable y reparable).",
    "  · TOSS CAÍDO (c12): resetToss re-arma el HELD del enlace (antes",
    "    el rival simulaba una bola fantasma rodando tras un",
    "    lanzamiento fallido).",
    "  · HIGIENE (c09): _helloTO en teardown (no mata la sesión nueva",
    "    en reconexión rápida), AudioContext del stream silencioso",
    "    cerrado (fuga por reconexión), marca de reloj también en los",
    "    SNAP (eco NTP completo), carrera de dos invitados en",
    "    wireConn resuelta (una sala = un rival).",
    "  · FUGA DEL 2v2 (c12): entrar a la academia o a AJUSTES›PALA",
    "    cierra el DOBLES 2v2 (antes palas extra congeladas en escena",
    "    y un 2v2 fantasma re-armado al salir); testActive en la",
    "    puerta de golpes por simetría.",
    "  · PULSO Y RETO SEMANAL EN EL CAMINO VIVO (c13): cobraban sólo",
    "    en el hitGoal del okHit muerto (desde v3.0.2) — un día con",
    "    plan t5a/t5b no podía cobrar el PULSO ni la insignia.",
    "  · QA TOOLING: smoke_sdk re-anclado a 3.6.111; aguja del claim",
    "    re-anclada al nuevo contrato (60 checks).",
    "  SE CONSERVA TODO: CRAZY LINK v2 (reloj compartido, FSM de",
    "    bola por mitades, túnel PeerJS, claims/resync), ELO",
    "    unificado con K por modo, matchmaking, reto diario y",
    "    semanal, MI RANKING, estilos de IA, superpoderes,",
    "    dobles 2v2, academia y PRO TRAINING.",
    "  QA r122 en verde: test_red_nucleo 60/0, qa_r81 136/0,",
    "    qa_r82 48/0, qa_r80 81/0, qa_r120_dirigida 39/0,",
    "    duelo NetLink VERDE, cadena qa_todo por trozos.",
    "  · sellada a",
    "  3.6.111",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36110", "release-v36111"),
    ("staging-v36110", "staging-v36111"),
    ("V3.6.110-SDK6", "V3.6.111-SDK6"),
    ("3.6.110-SDK6", "3.6.111-SDK6"),
    ("v36110-sdk6", "v36111-sdk6"),
    ("v36110", "v36111"),
    ("3.6.110", "3.6.111"),
]

INI_MARCADOR = "'Rama    : main · SDK6 (FASE 112"
FIN_MARCADOR = "'  3.6.110" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.110-SDK6 lista: MULTIJUGADOR verificado (pose fresca + cadencia sin toss; saque del invitado con rotación ITTF en banco S3 y batería de 4 puntos) sobre el CRAZY LINK v2 cerrado.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.111-SDK6 lista: REVISIÓN COMPLETA del netcode (resync con perspectiva, guardia de estado, claim sin autoridad, toss caído, higiene) + fuga del 2v2 + PULSO en el camino vivo.')"

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
        # 1 · notas FASE 113 (del marcador INI al FIN inclusive)
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
    print(f"\nrelease-v36111 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36111/build_zip.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
