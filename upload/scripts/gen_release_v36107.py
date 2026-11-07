#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 118 · GENERADOR DEL DIRECTORIO DE RELEASE v36107
========================================================================
Crea scripts/release-v36107/ a partir de scripts/release-v36106/ con:
  · reemplazos de versión (3.6.106-SDK6 → 3.6.107-SDK6 · v36106 → v36107)
  · bloque de notas del VERSION.txt nuevo (FASE 109 — M4 · ELO COMPLETO:
    unificado + matchmaking por ELO + reto de la semana + MI RANKING),
    por MARCADORES.
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36107 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36106"
DEST = RAIZ / "scripts" / "release-v36107"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 108 en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada «sellada a
#  3.6.106» ya quedó re-anclada a 3.6.107 por la pasada 1)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 108 — LOS DOS ARREGLOS DEL DUEÑO" + NL + "'"
BLOQUE_VIEJO_FIN = "    '  3.6.107" + NL + "'"

# líneas de texto PLANO de las notas FASE 109 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 109 — M4 · ELO COMPLETO",
    "    '(r118).",
    "    " + "'" + "El número único de habilidad llega a la casa: unificado,",
    "    " + "'" + "local y honesto, con matchmaking y panel propio.",
    "    '",
    "    " + "'" + "Novedades de esta version (frente a V3.6.106-SDK6):",
    "    '",
    "    " + "'" + "  · ELO UNIFICADO (c06): cada partido (IA, escalera y P2P",
    "    " + "'" + "    cuando exista) actualiza tu número con K por modo —",
    "    " + "'" + "    IA 24, escalera 20, humano 32. Se guarda en stats.data",
    "    " + "'" + "    (ppxr_stats_v1) con historial de los últimos 40 cambios",
    "    " + "'" + "    y mejor día por victorias. Las llamadas antiguas de dos",
    "    " + "'" + "    argumentos siguen funcionando byte-idénticas.",
    "    " + "'" + "  · MATCHMAKING POR ELO (c02+c12): botón «Rival a tu nivel»",
    "    " + "'" + "    en AJUSTES › JUEGO — propone un rival cerca de tu nivel",
    "    " + "'" + "    (±120 de variedad) mapeado a los presets reales de la",
    "    " + "'" + "    casa (bandas easy/medium/hard + factor k acotado 0.7-1.6:",
    "    " + "'" + "    jamás propone un muro). Vive sólo el partido armado; el",
    "    " + "'" + "    siguiente vuelve a tu dificultad. La escalera de carrera",
    "    " + "'" + "    manda si está activa (prioridad excluyente, cazada por",
    "    " + "'" + "    el arnés r118).",
    "    " + "'" + "  · RETO DE LA SEMANA (c13): el hermano mayor del PULSO en",
    "    " + "'" + "    el hueco 6 del hub de entrenamiento — duelo determinista",
    "    " + "'" + "    por septana (lunes→domingo, igual para toda la academia),",
    "    " + "'" + "    objetivo base+2 con subida por semana (tope 4), premio",
    "    " + "'" + "    de INSIGNIA acumulable + 120/30 pts. El reto diario y sus",
    "    " + "'" + "    pieles de asistencia quedan intactos.",
    "    " + "'" + "  · MI RANKING (c12): página propia desde AJUSTES › JUEGO —",
    "    " + "'" + "    ELO grande con el último delta, marca, rachas, mejor día",
    "    " + "'" + "    y los últimos cambios del historial. Todo local, sin",
    "    " + "'" + "    servidor nuevo.",
    "    '",
    "    " + "'" + "  SE CONSERVA TODO: la academia sin bloqueos, el PRO TRAINING",
    "    " + "'" + "    a prueba de desborde, la escalera de carrera, fuera la",
    "    " + "'" + "    repetición del mejor punto, el superpoder del rival en su",
    "    " + "'" + "    golpeo exacto, la chincheta por estancias y la física del",
    "    " + "'" + "    golpe fuerte.",
    "    '",
    "    " + "'" + "  QA r118 en verde (29 OK · 0 fallos por GPU headless: ELO y",
    "    " + "'" + "  K por modo, matchmaking con bandas/suelos/techos, reto",
    "    " + "'" + "  semanal determinista con cobro único, MI RANKING dibujado",
    "    " + "'" + "  y prioridad carrera>matchmaking verificada viva)",
    "    " + "'" + "  · sellada a",
    "    " + "'" + "  3.6.107",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36107 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.107.
    for viejo, nuevo in (("V3.6.106-SDK6", "V3.6.107-SDK6"),
                         ("3.6.106-SDK6", "3.6.107-SDK6"),
                         ("v36106-sdk6", "v36107-sdk6"),
                         ("3.6.106", "3.6.107"),
                         ("V3.6.106", "V3.6.107"),
                         ("v36106", "v36107"),
                         ("release-v36106", "release-v36107"),
                         ("staging-v36106", "staging-v36107")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 108 → FASE 109 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 108 → FASE 109 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 108 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    compile(t, "build_zip.py", "exec")
    print(f"· build_zip reescrito y compilable — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
