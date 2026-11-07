#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3662 — clona scripts/release-v3661 → scripts/release-v3662
y mete las NOTAS de la FASE 64 «LA ACADEMIA PERFECTA» en build_zip.py
(marcadores reales del bloque), heredando guards intactos.

Idempotente: si release-v3662 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3661"
DEST = RAIZ / "scripts" / "release-v3662"
BS_N = chr(92) + "n"

# ── marcadores del bloque de notas del build_zip r69 (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 63 — UNA RAQUETA, CERO FANTASMAS: el\\n'"
BLOQUE_FIN = "    '    taparlos en silencio.\\n\\n'"

BLOQUE_NUEVO = "    'Rama    : main · SDK6 (FASE 64 — LA ACADEMIA PERFECTA: el@NL@'\n    'informe del dueño tras probar V3.6.61 en el Quest, punto por punto,@NL@'\n    '«Vamos a hacerlo bien y dejar la academia PERFECTA»)@NL@@NL@'\n    'Novedades de esta versión (frente a V3.6.61-SDK6):@NL@@NL@'\n    '  · TROQUELES DE VUELTA EN TODOS LOS CAMPEONATOS (el dueño: «devuelve@NL@'\n    '    los 4 troqueles de decoración a todos los campeonatos»): la@NL@'\n    '    condición !inAR los ESCONDÍA en todas las sesiones con@NL@'\n    '    passthrough del Quest — por eso «habían desaparecido» aunque la@NL@'\n    '    QA los viera. Ahora están SIEMPRE: los 5 campeonatos montan sus@NL@'\n    '    piezas también con passthrough (verificado con inAR=true).@NL@@NL@'\n    '  · PANEL SIN TEXTOS SUPERPUESTOS (el dueño: «ese panel superpone@NL@'\n    '    los textos»): la píldora «TU MANDO ES TU RAQUETA» y la@NL@'\n    '    instrucción del vaivén se comían (cajas 406..478 y 441..463).@NL@'\n    '    Nuevo reparto vertical: píldora 392..448 · instrucción 472 ·@NL@'\n    '    barra 500 — aire limpio entre los tres bloques.@NL@@NL@'\n    '  · LA VOZ DEL VAIVÉN SUENA (el dueño: «si además la voz aquí dice@NL@'\n    '    ”Mueve tu raqueta hacia los lados rápidamente“ reforzaría el@NL@'\n    '    mensaje»): el átomo tutv2b («Muévela de lado a lado, con@NL@'\n    '    firmeza») existía desde r66 y jamás se narraba — ahora suena en@NL@'\n    '    el momento exacto del vaivén.@NL@@NL@'\n    '  · LA VOZ MUERE AL SALIR (el dueño: «al pulsar B y aparecer en el@NL@'\n    '    Hall la voz sigue sonando y debe terminar»): stop() corta la@NL@'\n    '    locución viva (audio.callaVoz: buffer compuesto + respaldo de@NL@'\n    '    speechSynthesis) y limpia las narraciones pendientes.@NL@@NL@'\n    '  · BLINDAJE TOTAL (el dueño: «al salir del tutorial NADA de este@NL@'\n    '    persista en las otras escenas»): al cerrar se cancelan también@NL@'\n    '    los golpes pendientes y el árbitro vuelve a estado limpio — ni@NL@'\n    '    voces, ni halo, ni raqueta, ni aros, ni holo, ni estados@NL@'\n    '    fantasma en partido/campeonatos.@NL@@NL@'\n    '  · SAQUE CON LOS DOS BOTES (el dueño: «debe botar en ambos campos@NL@'\n    '    y esto no lo comprueba, dando por bueno un servicio aunque bote@NL@'\n    '    en 1 sola parte del campo, mío o de mi rival»): la cuenta@NL@'\n    '    exigía solo CRUZAR al campo rival — voleas y medios saques@NL@'\n    '    contaban. Ahora la secuencia es reglamentaria: bote en TU campo@NL@'\n    '    y DESPUÉS en el del rival (los aros guía marcan el camino).@NL@@NL@'\n    '  · LA RAQUETA DEL PROFESOR, POR FIN EN SU SITIO (el dueño: «el@NL@'\n    '    rival golpea pero no aparece su raqueta que debería estar bien@NL@'\n    '    colocada»): vivía en la escena-mundo mientras la mesa, la bola@NL@'\n    '    y la pala IA viven en el RIG (espacio de referencia XR) — el@NL@'\n    '    recentrado del Quest la descolocaba («problemas de colocación»,@NL@'\n    '    «desfasada y no golpea»). Ahora raqueta, aros guía y holo@NL@'\n    '    viven EN EL RIG como la mesa, con visibilidad defensiva en cada@NL@'\n    '    arma y golpe.@NL@@NL@'\n    '  · Conserva TODO lo anterior (una sola raqueta y golpes honestos@NL@'\n    '    r69; la raqueta del rival r68 con saques al paso de la hoja;@NL@'\n    '    la academia en tus manos r67: voz única, mandos anclados a los@NL@'\n    '    grips reales al 75%; la academia sobre la mesa r66; el@NL@'\n    '    onboarding hablado r65; la academia a punto r64; el toque@NL@'\n    '    profesional r62; la estela de poderes, el rival adaptativo y la@NL@'\n    '    repetición r61; 5 poderes, voz del selector, expresiones, bomba@NL@'\n    '    y eléctrico, passthrough en caliente, SALÓN, PRO CIRCUITO, CCD,@NL@'\n    '    CRAZY TV y los 5 campeonatos).@NL@@NL@'\n"

GLOBALES = [
    ("V3.6.61-SDK6", "V3.6.62-SDK6"),
    ("3.6.61-SDK6", "3.6.62-SDK6"),
    ("v3661-sdk6", "v3662-sdk6"),
    ("3.6.61", "3.6.62"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.62-SDK6", "frente a V3.6.61-SDK6"),
    ("tras probar V3.6.62", "tras probar V3.6.61"),
]


def main():
    if DEST.exists():
        print("regenerando (release-v3662 ya existía)…")
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    print(f"copiado {ORIGEN.name} → {DEST.name}")

    for f in sorted(DEST.iterdir()):
        if not f.is_file():
            continue
        txt = f.read_text(encoding="utf-8")
        if f.name == "build_zip.py":
            i = txt.find(BLOQUE_INI)
            if i < 0:
                print("FALLO: marcador INI del bloque no encontrado")
                sys.exit(1)
            j = txt.find(BLOQUE_FIN, i)
            if j < 0:
                print("FALLO: marcador FIN del bloque no encontrado")
                sys.exit(1)
            j += len(BLOQUE_FIN)
            txt = txt[:i] + BLOQUE_NUEVO.replace("@NL@", BS_N) + txt[j:]
            print(f"  ✓ {f.name}: notas FASE 64 insertadas")
        for viejo, nuevo in GLOBALES:
            n = txt.count(viejo)
            if n:
                txt = txt.replace(viejo, nuevo)
                print(f"  ✓ {f.name}: {viejo} → {nuevo} (×{n})")
        if f.name == "build_zip.py":
            for viejo, nuevo in RESTAURA:
                n = txt.count(viejo)
                if n:
                    txt = txt.replace(viejo, nuevo)
                    print(f"  ✓ {f.name}: restaurado {viejo} → {nuevo} (×{n})")
        f.write_text(txt, encoding="utf-8")

    print(f"OK → {DEST}")


if __name__ == "__main__":
    main()
