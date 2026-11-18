#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 114 · GENERADOR DEL DIRECTORIO DE RELEASE v36104
========================================================================
Crea scripts/release-v36104/ a partir de scripts/release-v36103/ con:
  · reemplazos de versión (3.6.103-SDK6 → 3.6.104-SDK6 · v36103 → v36104)
  · bloque de notas del VERSION.txt nuevo (FASE 106 — MENÚ ANCLA POR
    ESTANCIA + RETIRO DEL DIORAMA), sustituido por MARCADORES.
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36104 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36103"
DEST = RAIZ / "scripts" / "release-v36104"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 105 en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada «sellada a
# 3.6.103» ya quedó re-anclada a 3.6.104 por la pasada 1)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 105 — AJUSTES DEL DUEÑO" + NL + "'"
BLOQUE_VIEJO_FIN = " · sellada a 3.6.104" + NL + "'"

# líneas de texto PLANO de las notas FASE 106 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 106 — MENÚ ANCLA POR ESTANCIA",
    "    '(r114).",
    "    'La corrección BLOQUEANTE que pediste a gritos: el menú ya no",
    "    'puede desaparecer al cambiar de escena, y la mesa con las dos",
    "    'palas jugando del Hall se retira DE VERDAD.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.103-SDK6):",
    "    '",
    "    '  · ANCLA POR ESTANCIA: tu informe era exacto — «si anclamos el",
    "    '    menú y nos vamos a otro escenario al volver a sacar el menú",
    "    '    ya no se ve por quedar descolocado». Cada ancla del menú se",
    "    '    firma con la ESTANCIA donde nace (Hall / cancha / AR /",
    "    '    online) y con la posición del rig de ese momento. Si viajas",
    "    '    de escena (o el rig se teletransporta: vista previa de la",
    "    '    sala, re-entrada en VR), el ancla vieja se INVALIDA sola:",
    "    '    la chincheta se suelta y el menú reaparece SIEMPRE delante",
    "    '    de ti. En la escena donde lo clavaste sigue anclado; en",
    "    '    cualquier otra se comporta normal — como pediste.",
    "    '  · PROMPT B INVISIBLE, ARREGLADO: en un partido, pulsar B saca",
    "    '    el prompt «Menú principal ¿SI/No?» DELANTE DE TU CARA",
    "    '    SIEMPRE — si el ancla quedó lejos (>2,5 m) o en otra",
    "    '    estancia, se suelta sola antes de abrir. Nunca más «no lo",
    "    '    veo».",
    "    '  · LA MESA DE LA CASA, RETIRADA: el diorama IA-vs-IA sobre",
    "    '    pedestal del Hall (mesa miniatura + dos palas disco + bola",
    "    '    en parábolas) sale del Hall Of Fame — petición expresa y",
    "    '    reiterada: «ya dijimos que no la queremos, no aporta nada».",
    "    '    El centro de la estancia queda libre; el museo conserva su",
    "    '    arte de las cuatro paredes y sus 7 bolas doradas.",
    "    '  · SE CONSERVA TODO: la chincheta de r113 (clava/suelta con",
    "    '    sonido y vibración), la física del golpe fuerte con",
    "    '    dirección al objetivo, la CPU sin fallos regalados, los",
    "    '    superpoderes justos (anuncio sólo con la bola hacia el",
    "    '    rival), la etapa 4 de La Locura relajada, la guía del",
    "    '    primer saque, la telemetría del primer rallye y los 5",
    "    '    campeonatos.",
    "    '",
    "    '  QA r114 en verde (capa nueva: heal del ancla EN VIVO — viaja",
    "    '  de estancia con el pin puesto y se suelta sola · diorama",
    "    '  fuera del servido · gate completo re-anclado) · sellada a",
    "    '  3.6.104",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36104 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.104.
    for viejo, nuevo in (("V3.6.103-SDK6", "V3.6.104-SDK6"),
                         ("3.6.103-SDK6", "3.6.104-SDK6"),
                         ("v36103-sdk6", "v36104-sdk6"),
                         ("3.6.103", "3.6.104"),
                         ("V3.6.103", "V3.6.104"),
                         ("v36103", "v36104"),
                         ("release-v36103", "release-v36104"),
                         ("staging-v36103", "staging-v36104")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 105 → FASE 106 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 105 → FASE 106 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 105 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    compile(t, "build_zip.py", "exec")
    print(f"· build_zip reescrito y compilable — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
