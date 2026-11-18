#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 119 · GENERADOR DEL DIRECTORIO DE RELEASE v36108
========================================================================
Crea scripts/release-v36108/ a partir de scripts/release-v36107/ con:
  · reemplazos de versión (3.6.107-SDK6 → 3.6.108-SDK6 · v36107 → v36108)
  · bloque de notas del VERSION.txt nuevo (FASE 110 — M7c · DOBLES 2v2
    PROTOTIPO: investigación + prototipo jugable, todo con la física y el
    árbitro del 1v1), por MARCADORES.
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36108 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36107"
DEST = RAIZ / "scripts" / "release-v36108"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 109 en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada «sellada a
#  3.6.107» ya quedó re-anclada a 3.6.108 por la pasada 1)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 109 — M4 · ELO COMPLETO" + NL + "'"
BLOQUE_VIEJO_FIN = "    '  3.6.108" + NL + "'"

# líneas de texto PLANO de las notas FASE 110 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 110 — M7c · DOBLES 2v2 PROTOTIPO",
    "    '(r119).",
    "    " + "'" + "La investigación del motor dijo que el 2v2 no necesita",
    "    " + "'" + "tocar física ni árbitro: OpponentAI es simétrico por sign",
    "    " + "'" + "(+1 jugador / -1 CPU — lo demostró la pala demo) y el",
    "    " + "'" + "árbitro ya puntúa por EQUIPO con falta de doble golpe.",
    "    " + "'" + "El prototipo se apoya EXACTAMENTE en eso.",
    "    " + "'" + "  · EL MODO (c12): botón «DOBLES 2v2 — pruébalo» en",
    "    " + "'" + "    AJUSTES › JUEGO — arma y arranca el partido en un",
    "    " + "'" + "    gesto (mismo arranque que JUGAR). El modo vive SOLO",
    "    " + "'" + "    un partido: el game-over lo recoge y ▶ JUGAR, la",
    "    " + "'" + "    escalera, la sesión online y los campeonatos lo",
    "    " + "'" + "    limpian al entrar (anti-fugas).",
    "    " + "'" + "  · CUATRO PALAS: tú + COMPAÑERO IA (easy fijo, mitad",
    "    " + "'" + "    izquierda, jamás sirve) contra RIVAL 1 + RIVAL 2 IA",
    "    " + "'" + "    (el segundo con la MISMA cfg efectiva que el primero).",
    "    " + "'" + "    Nadie roba la bola a su compañero: ARBITRAJE DE",
    "    " + "'" + "    ALCANCE de 0,50 m sobre el barrido anti-túnel — el",
    "    " + "'" + "    jugador manda; la IA extra cubre lo que no llegas.",
    "    " + "'" + "  · ÁRBITRO INTACTO: registerPaddleHit player/ai",
    "    " + "'" + "    comparte marcador por equipos y el segundo toque del",
    "    " + "'" + "    mismo equipo sigue siendo FALTA (dblhit). El saque es",
    "    " + "'" + "    siempre del titular del equipo.",
    "    " + "'" + "  · CERO COSTE EN 1v1: las palas extra nacen ocultas y",
    "    " + "'" + "    sus IA dormidas; sin dobles ni un píxel nuevo en",
    "    " + "'" + "    pantalla y sin trabajo por frame.",
    "    " + "'" + "  · i18n ES/EN (dobles_btn · dobles_msg) y telemetría",
    "    " + "'" + "    del arranque del modo (evento dobles).",
    "    " + "'" + "  SE CONSERVA TODO: ELO unificado con K por modo,",
    "    " + "'" + "    matchmaking por ELO, reto diario y semanal, MI",
    "    " + "'" + "    RANKING, estilos de IA, superpoderes, academia y",
    "    " + "'" + "    PRO TRAINING.",
    "    " + "'" + "  QA r119 en verde (26 OK · 0 fallos por GPU headless:",
    "    " + "'" + "  botón real por menuClick, cfg espejo del rival 2 y",
    "    " + "'" + "  compañero anclado, rallies reales de las dos palas",
    "    " + "'" + "  extra con el árbitro intacto, arbitraje de alcance",
    "    " + "'" + "  completo (cerca no roba · lejos toma · simétrico en",
    "    " + "'" + "  el lado CPU), doble golpe = falta y anti-fugas de",
    "    " + "'" + "  modos verificadas vivas)",
    "    " + "'" + "  · sellada a",
    "    " + "'" + "  3.6.108",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36108 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.108.
    for viejo, nuevo in (("V3.6.107-SDK6", "V3.6.108-SDK6"),
                         ("3.6.107-SDK6", "3.6.108-SDK6"),
                         ("v36107-sdk6", "v36108-sdk6"),
                         ("3.6.107", "3.6.108"),
                         ("V3.6.107", "V3.6.108"),
                         ("v36107", "v36108"),
                         ("release-v36107", "release-v36108"),
                         ("staging-v36107", "staging-v36108")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 109 → FASE 110 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 109 → FASE 110 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 109 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip.py re-anclado ({n_ok} tokens) · notas FASE 110")

    # 3) el resto del directorio hereda tal cual (qa capas, plantillas).
    print("· release-v36108 LISTO (hereda qa/leanme del v36107)")


if __name__ == "__main__":
    main()
