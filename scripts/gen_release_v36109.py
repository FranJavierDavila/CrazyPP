#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 120 · GENERADOR DEL DIRECTORIO DE RELEASE v36109
========================================================================
Crea scripts/release-v36109/ a partir de scripts/release-v36108/ con:
  · reemplazos de versión (3.6.108-SDK6 → 3.6.109-SDK6 · v36108 → v36109)
  · bloque de notas del VERSION.txt nuevo (FASE 111 — M7d · PRO TRAINING
    EXTENDIDO: dos ejercicios nuevos + medallas por ejercicio, todo en
    la academia c13 sin tocar física, árbitro ni retos), por MARCADORES.
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36109 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36108"
DEST = RAIZ / "scripts" / "release-v36109"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 110 en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada «sellada a
#  3.6.108» ya quedó re-anclada a 3.6.109 por la pasada 1)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 110 — M7c · DOBLES 2v2 PROTOTIPO" + NL + "'"
BLOQUE_VIEJO_FIN = "    '  3.6.109" + NL + "'"

# líneas de texto PLANO de las notas FASE 111 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 111 — M7d · PRO TRAINING EXTENDIDO",
    "    '(r120).",
    "    " + "'" + "  Dos ejercicios nuevos y medallas por ejercicio, todo en",
    "    " + "'" + "  la academia (c13) y sin tocar física, árbitro ni retos.",
    "    " + "'" + "  · ESQUINA EXACTA (t1c · DIRECCIÓN): fondo Y banda a la",
    "    " + "'" + "    vez — los dos cuadros dorados, lo pintado ES lo",
    "    " + "'" + "    juzgado (mismo lenguaje de zonas que t1a/t1b).",
    "    " + "'" + "    Meta 3 esquinas · +3 pts · bonus 25.",
    "    " + "'" + "  · METRÓNOMO LOCO (t5b · RITMO): el mismo rally del",
    "    " + "'" + "    metrónomo con la máquina TRAICIONERA — cada bola",
    "    " + "'" + "    llega a una velocidad distinta (5,6–9,2) y el beat",
    "    " + "'" + "    late más rápido (1,45 s). Hitos a 20 · 40 · 80.",
    "    " + "'" + "  · MEDALLAS POR EJERCICIO: BRONCE (meta completada),",
    "    " + "'" + "    PLATA (2 estrellas y 70 %) y ORO (3 estrellas y",
    "    " + "'" + "    85 %). En los modos de rally manda la MARCA",
    "    " + "'" + "    (20/40/80 · 30/50/100). Derivadas de datos que ya",
    "    " + "'" + "    existen: RETROACTIVAS y sin migración. Medallero",
    "    " + "'" + "    por área en el hub y medalla en cada tarjeta.",
    "    " + "'" + "  · LOGRO NUEVO «MEDALLERO DE ORO» (5 oros): la fila",
    "    " + "'" + "    LOGROS del hub pasa a n/10.",
    "    " + "'" + "  · RE-ANCLADO EN EL CAMINO VIVO: las estrellas y los",
    "    " + "'" + "    logros m50/m100 del metrónomo vivían en un camino",
    "    " + "'" + "    muerto (el juez del rally jamás llamaba a okHit",
    "    " + "'" + "    desde la refactorización v3.0.2) — ahora los",
    "    " + "'" + "    registra el juez vivo. «CIRCUITO COMPLETO» sigue",
    "    " + "'" + "    prometiendo los 9 clásicos (PLAN_POOL).",
    "    " + "'" + "  · PLAN_POOL CONGELADO: el reto diario (r76) y el",
    "    " + "'" + "    semanal (r118) siguen byte-idénticos con los 9",
    "    " + "'" + "    clásicos; los ejercicios nuevos son entrenamiento",
    "    " + "'" + "    libre puro y JAMÁS entran en los retos.",
    "    " + "'" + "  · i18n ES/EN y costuras de QA al patrón de la casa",
    "    " + "'" + "    (__test/__debug).",
    "    " + "'" + "  SE CONSERVA TODO: ELO unificado con K por modo,",
    "    " + "'" + "    matchmaking por ELO, reto diario y semanal, MI",
    "    " + "'" + "    RANKING, estilos de IA, superpoderes, dobles 2v2,",
    "    " + "'" + "    academia y PRO TRAINING.",
    "    " + "'" + "  QA r120 en verde (39 OK · 0 fallos por GPU headless:",
    "    " + "'" + "    registro y pool congelado, determinismo FNV",
    "    " + "'" + "    independiente de los retos, medallas derivadas",
    "    " + "'" + "    retroactivas, juez real t1c/t5b con hitos y m50",
    "    " + "'" + "    re-anclado, menú real con las tarjetas nuevas y",
    "    " + "'" + "    anti-fugas de modos verificadas)",
    "    " + "'" + "  · sellada a",
    "    " + "'" + "  3.6.109",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36109 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.109.
    for viejo, nuevo in (("V3.6.108-SDK6", "V3.6.109-SDK6"),
                         ("3.6.108-SDK6", "3.6.109-SDK6"),
                         ("v36108-sdk6", "v36109-sdk6"),
                         ("3.6.108", "3.6.109"),
                         ("V3.6.108", "V3.6.109"),
                         ("v36108", "v36109"),
                         ("release-v36108", "release-v36109"),
                         ("staging-v36108", "staging-v36109")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 110 → FASE 111 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 110 → FASE 111 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 110 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip.py re-anclado ({n_ok} tokens) · notas FASE 111")

    # 3) el resto del directorio hereda tal cual (qa capas, plantillas).
    print("· release-v36109 LISTO (hereda qa/leanme del v36108)")


if __name__ == "__main__":
    main()
