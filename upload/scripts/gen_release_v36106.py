#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 116 · GENERADOR DEL DIRECTORIO DE RELEASE v36106
========================================================================
Crea scripts/release-v36106/ a partir de scripts/release-v36105/ con:
  · reemplazos de versión (3.6.105-SDK6 → 3.6.106-SDK6 · v36105 → v36106)
  · bloque de notas del VERSION.txt nuevo (FASE 108 — LA ACADEMIA PASO 4
    SIN BLOQUEOS + «PASE BAJO»/LOGROS DEL PRO TRAINING), por MARCADORES.
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36106 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36105"
DEST = RAIZ / "scripts" / "release-v36106"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 107 en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada «sellada a
#  3.6.105» ya quedó re-anclada a 3.6.106 por la pasada 1)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 107 — DOS AJUSTES DEL DUEÑO" + NL + "'"
BLOQUE_VIEJO_FIN = "    '  3.6.106" + NL + "'"

# líneas de texto PLANO de las notas FASE 108 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 108 — LOS DOS ARREGLOS DEL DUEÑO",
    "    '(r116).",
    "    'La Academia nunca se queda clavada y el PRO TRAINING pinta",
    "    'sus textos dentro de su sitio.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.105-SDK6):",
    "    '",
    "    '  · ACADEMIA · PASO 4 SIN BLOQUEOS (informe del dueño: «cuando",
    "    '    empezamos la práctica de intercambio, como lancemos la",
    "    '    bola y esta se caiga al suelo ahí se queda sin poder hacer",
    "    '    nada»): la máquina de fases del intercambio NO tenía control",
    "    '    de bola muerta en su fase de vuelo — si el saque caía al",
    "    '    suelo sin cruzar, la fase quedaba clavada para siempre y",
    "    '    el gatillo (que exige la fase de saque) no respondía. Ahora",
    "    '    la bola muerta —en el suelo, sobre la mesa o más allá—",
    "    '    vuelve al saque AL INSTANTE con su «otra vez» hablado, el",
    "    '    mismo camino honesto del fallo de devolución. Paso 4",
    "    '    imposible de bloquear.",
    "    '  · PRO TRAINING · «PASE BAJO» A PRUEBA DE DESBORDE: la",
    "    '    descripción de la prueba se salía de su tarjeta — envoltura",
    "    '    propia a 620 px y hasta 3 líneas, rebaje de fuente si hace",
    "    '    falta y elipsis dura como red de seguridad. Nada sale del",
    "    '    contenedor en ninguna prueba ni en ningún idioma.",
    "    '  · PRO TRAINING · LOGROS EN SU SITIO (los «textos y números",
    "    '    descolocados» del hub): la fila LOGROS n/9 y sus puntos",
    "    '    nacían en y=178-202 y la parrilla de áreas tapaba la cola",
    "    '    (las tarjetas nacen en 190) — la parrilla baja a y=236 y",
    "    '    la fila de logros respira libre, alineada y completa.",
    "    '  · SE CONSERVA TODO: el retiro de la repetición del mejor",
    "    '    punto, el superpoder del rival en su golpeo exacto, la",
    "    '    chincheta por estancias, la física del golpe fuerte, la CPU",
    "    '    sin fallos regalados, la etapa 4 de La Locura relajada y",
    "    '    los 5 campeonatos.",
    "    '",
    "    '  QA r116 en verde (10 OK · 0 fallos por GPU headless: arranque,",
    "    '  paso 4 recorrido entero con bola muerta en vuelo, gatillo",
    "    '  recuperado, hub a y=236 y «PASE BAJO» dibujado sin excepción)",
    "    '  · sellada a",
    "    '  3.6.106",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36106 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.106.
    for viejo, nuevo in (("V3.6.105-SDK6", "V3.6.106-SDK6"),
                         ("3.6.105-SDK6", "3.6.106-SDK6"),
                         ("v36105-sdk6", "v36106-sdk6"),
                         ("3.6.105", "3.6.106"),
                         ("V3.6.105", "V3.6.106"),
                         ("v36105", "v36106"),
                         ("release-v36105", "release-v36106"),
                         ("staging-v36105", "staging-v36106")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 107 → FASE 108 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 107 → FASE 108 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 107 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    compile(t, "build_zip.py", "exec")
    print(f"· build_zip reescrito y compilable — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
