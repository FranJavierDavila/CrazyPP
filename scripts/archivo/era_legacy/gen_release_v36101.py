#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36101 — hereda scripts/release-v36100 → scripts/release-v36101
e inserta las NOTAS de la FASE 103 «M4 ONBOARDING (r111)».

Ronda 111: hito M4 del roadmap MEJORAS.md — un jugador nuevo está en un
rallye real en <60 s tocando sólo JUGAR: ▶ JUGAR botón único del HUB (la
academia deja de bloquear), LA MESA DE LA CASA (diorama IA-vs-IA en vivo
en el hall), guía del PRIMER SAQUE real (aros + una línea, localStorage),
idioma detectado antes del primer toque y altura de mesa autodetectada
para sentados. Telemetría nueva: primer_rally + tut_end (catálogo v6).

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas. Idempotente (regenera desde v36100).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36100"
DEST = RAIZ / "scripts" / "release-v36101"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 102 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada ya dice 3.6.101)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 102 — DUELO REPARADO" + NL + "'"
BLOQUE_VIEJO_FIN = " · sellada a 3.6.101" + NL + "'"

# líneas de texto PLANO de las notas FASE 103 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 103 — M4 ONBOARDING",
    "    '(r111).",
    "    " + "'" + "Hito M4 del roadmap MEJORAS.md: un jugador nuevo está en un rallye",
    "    'real en MENOS DE 60 SEGUNDOS sin tocar nada más que JUGAR (medible",
    "    'con la telemetría nueva primer_rally). Cuatro piezas y una medida:",
    "    '",
    "    'Novedades de esta version (frente a V3.6.100-SDK6):",
    "    '",
    "    '  · ▶ JUGAR, BOTÓN ÚNICO: el HUB abre con JUGAR a toda fila, verde",
    "    '    vivo, por delante de todo (antes PARTIDO compartía parrilla). El",
    "    '    AJUSTES baja a media celda (mismo acceso, el HUB cabe).",
    "    '  · LA ACADEMIA DEJA DE BLOQUEAR: la primera vez ya no aparece la",
    "    '    página «¿PRIMERA VEZ?» antes de jugar — la bienvenida queda en",
    "    '    UNA línea del árbitro y el banner dorado del HUB (r59) sigue a",
    "    '    un toque. El criterio <60 s exigía eliminar ese toque extra.",
    "    '  · LA MESA DE LA CASA: diorama en el hall (a la derecha del menú) con",
    "    '    un rallye IA-vs-IA SIEMPRE vivo — mesa miniatura sobre pedestal,",
    "    '    dos palas que siguen la bola y swings secos. Cinemática pura (par-",
    "    '    ábolas scriptadas): sin física, sin árbitro, coste CERO en cancha.",
    "    '    El jugador nuevo VE cómo se juega antes de tocar nada.",
    "    '  · GUÍA DEL PRIMER SAQUE REAL: los aros de la academia salen a la",
    "    '    cancha la primera vez que se juega de verdad (aros verde propio +",
    "    '    tenue rival, haz pulsante y UNA línea del árbitro). Tras 3 saques",
    "    '    legales se marcan como vistos (pp_srv_v1) y no vuelven. Nunca en",
    "    '    online ni en la academia; AJUSTES manda siempre.",
    "    '  · IDIOMA DETECTADO ANTES DEL PRIMER TOQUE: en 1.ª instalación el",
    "    '    idioma sale de navigator.language (es→ES, resto→EN); quien ya",
    "    '    jugaba no ve un solo cambio (huellas pp_tut_asked/pp_seen_v1).",
    "    '  · ALTURA DE MESA AUTODETECTADA: si nunca fijaste la mesa, la altura",
    "    '    de la cabeza (local-floor) elige preset «baja» si juegas sentado",
    "    '    (<1,30 m); una sola vez y siempre sobreescribible en AJUSTES.",
    "    '  · TELEMETRÍA DEL EMBUDO (catálogo v6, 16 eventos): primer_rally",
    "    '    (lat s desde vr_start · dif) y tut_end (done · aJugar · step).",
    "    '",
    "    '  QA r111 en verde (qa_telemetria 132/0 · presupuesto refrescado ·",
    "    '  boot limpio 0 pageerrors · GATE completo 14/14) · sellada a 3.6.101",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36101 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.101.
    for viejo, nuevo in (("V3.6.100-SDK6", "V3.6.101-SDK6"),
                         ("3.6.100-SDK6", "3.6.101-SDK6"),
                         ("v36100-sdk6", "v36101-sdk6"),
                         ("3.6.100", "3.6.101"),
                         ("V3.6.100", "V3.6.101"),
                         ("v36100", "v36101"),
                         ("release-v36100", "release-v36101"),
                         ("staging-v36100", "staging-v36101")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 102 → FASE 103 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 102 → FASE 103 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 102 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
