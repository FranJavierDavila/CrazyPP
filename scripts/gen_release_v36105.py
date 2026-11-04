#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 115 · GENERADOR DEL DIRECTORIO DE RELEASE v36105
========================================================================
Crea scripts/release-v36105/ a partir de scripts/release-v36104/ con:
  · reemplazos de versión (3.6.104-SDK6 → 3.6.105-SDK6 · v36104 → v36105)
  · bloque de notas del VERSION.txt nuevo (FASE 107 — RETIRO DE LA
    REPETICIÓN DEL MEJOR PUNTO + SUPERPODER EN EL GOLPEO RIVAL),
    sustituido por MARCADORES.
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36105 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36104"
DEST = RAIZ / "scripts" / "release-v36105"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 106 en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada «sellada a
#  3.6.104» ya quedó re-anclada a 3.6.105 por la pasada 1)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 106 — MENÚ ANCLA POR ESTANCIA" + NL + "'"
BLOQUE_VIEJO_FIN = "  3.6.105" + NL + "'"

# líneas de texto PLANO de las notas FASE 107 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 107 — DOS AJUSTES DEL DUEÑO",
    "    '(r115).",
    "    'Fuera las repeticiones del mejor punto y el superpoder del",
    "    'rival disparando EN EL GOLPEO, con la bola en su campo.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.104-SDK6):",
    "    '",
    "    '  · ADIÓS A LA REPETICIÓN DEL MEJOR PUNTO: al terminar la",
    "    '    partida ya NO se reproduce el mejor intercambio — ni",
    "    '    fantasmas, ni cartel azul, ni cámara lenta del replay.",
    "    '    Petición expresa: «no lo queremos». La fanfarria respira",
    "    '    sola y el gatillo es revancha desde el primer pulso.",
    "    '  · SUPERPODER DEL RIVAL EN SU JUSTO MOMENTO: el anuncio con",
    "    '    la partida congelada nace EXACTAMENTE cuando el rival",
    "    '    golpea la bola con la bola en SU campo (el motor lee el",
    "    '    golpeo real del árbitro: lastHitter pasa a rival en el",
    "    '    contacto). Ni en pleno vuelo hacia ti ni tras tu golpeo",
    "    '    (el flanco de r113 también se retira): el poder entra con",
    "    '    el golpe del rival y el efecto llega con esa bola.",
    "    '  · SE CONSERVA TODO: la chincheta por estancias (r114), la",
    "    '    física del golpe fuerte con dirección al objetivo, la CPU",
    "    '    sin fallos regalados, la etapa 4 de La Locura relajada,",
    "    '    la guía del primer saque, la telemetría del primer rallye",
    "    '    y los 5 campeonatos.",
    "    '",
    "    '  QA r115 en verde (repetición fuera del servido · flanco en",
    "    '  el golpeo en los 5 campeonatos · la dilatación del match",
    "    '  point intacta) · sellada a",
    "    '  3.6.105",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36105 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.105.
    for viejo, nuevo in (("V3.6.104-SDK6", "V3.6.105-SDK6"),
                         ("3.6.104-SDK6", "3.6.105-SDK6"),
                         ("v36104-sdk6", "v36105-sdk6"),
                         ("3.6.104", "3.6.105"),
                         ("V3.6.104", "V3.6.105"),
                         ("v36104", "v36105"),
                         ("release-v36104", "release-v36105"),
                         ("staging-v36104", "staging-v36105")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 106 → FASE 107 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 106 → FASE 107 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 106 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    compile(t, "build_zip.py", "exec")
    print(f"· build_zip reescrito y compilable — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
