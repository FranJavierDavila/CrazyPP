#!/usr/bin/env python3
"""gen_release_v3667 — hereda scripts/release-v3666 → scripts/release-v3667
e inserta las NOTAS de la FASE 69 «TODO ENCAJA» en build_zip.py.

Idempotente: si release-v3667 ya existe, se regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3666"
DEST = RAIZ / "scripts" / "release-v3667"
BS_N = chr(92) + "n"

# ── marcadores del bloque de notas del build_zip (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 68 — EL MANDO DE SIEMPRE: el informe\\n'"
BLOQUE_FIN = "    '    los 5 campeonatos).\\n\\n'"

BLOQUE_NUEVO = (
    "    'Rama    : main · SDK6 (FASE 69 — TODO ENCAJA: el informe del@NL@'\n"
    "    'dueño tras probar V3.6.66 en el Quest)@NL@@NL@'\n"
    "    'Novedades de esta versión (frente a V3.6.66-SDK6):@NL@@NL@'\n"
    "    '  · LA PANTALLA DE LOS MODOS, TODO DENTRO DE SU CAJA (el dueño:@NL@'\n"
    "    '    «en la pantalla del tutorial de Modos algunos textos quedan@NL@'\n"
    "    '    fuera del contenedor; es preciso recolocarlos de otra forma@NL@'\n"
    "    '    para que se lean bien y quede todo bien encajado»): diagnóstico@NL@'\n"
    "    '    MEDIDO EN VIVO — la línea de detalle ámbar de las tarjetas de@NL@'\n"
    "    '    abajo (RANKING MUNDIAL 353 px · ENTRENAR 324 px; también en@NL@'\n"
    "    '    inglés: 333/341) agotaba el mínimo de fuente (10 px) y seguía@NL@'\n"
    "    '    midiendo MÁS que los 214 px disponibles de la tarjeta: el texto@NL@'\n"
    "    '    SALÍA de la tarjeta y se comía la vecina. Arreglo de raíz:@NL@'\n"
    "    '    (1) CARDWRAP — reduce la fuente (fitFont) y, si aún no cabe,@NL@'\n"
    "    '    ENVUELVE por palabras en ≤2 líneas que miden TODAS dentro del@NL@'\n"
    "    '    ancho de la tarjeta (con elipsis de seguridad para cualquier@NL@'\n"
    "    '    texto futuro); (2) MODECARD reorganizada — título, subtítulo y@NL@'\n"
    "    '    extra pasan por cardWrap y las filas suben (modo COMPACTO)@NL@'\n"
    "    '    cuando la extra se parte en 2, con separación de tinta@NL@'\n"
    "    '    verificada: nada pisa nada; (3) WRAP2 blindada — la caja@NL@'\n"
    "    '    PODERES re-ajusta cada mitad a su ancho. VERIFICADO EN VIVO:@NL@'\n"
    "    '    las funciones SERVIDAS pintan las 6 tarjetas en ES y EN y cada@NL@'\n"
    "    '    línea queda DENTRO de su marco (49 comprobaciones), con@NL@'\n"
    "    '    capturas de la pizarra para el dueño.@NL@@NL@'\n"
    "    '  · Conserva TODO lo anterior (r74: B en el Pro Training, menú@NL@'\n"
    "    '    sobre el cartel EMPEZAR, glow que sigue la mano, devoluciones@NL@'\n"
    "    '    sin atascos, modos con calma y sin bola sonora, orden@NL@'\n"
    "    '    Clow→Wizard→Forajido, telón común y zona muerta del suelo;@NL@'\n"
    "    '    r73: menú al cielo del render, candados bien colocados, índice@NL@'\n"
    "    '    resiliente y telón de teatro; r72: panel sin solapes y telón@NL@'\n"
    "    '    con espera honesta; r71: saque reglamentario del profesor y@NL@'\n"
    "    '    AJUSTES por subcategorías; r69-r67: una sola raqueta, golpes@NL@'\n"
    "    '    honestos, academia en tus manos; r66-r65: sobre la mesa,@NL@'\n"
    "    '    onboarding hablado; r61: estela de poderes, rival adaptativo y@NL@'\n"
    "    '    repetición; 5 poderes, voz del selector, expresiones,@NL@'\n"
    "    '    passthrough en caliente, SALÓN, PRO CIRCUITO, CCD, CRAZY TV y@NL@'\n"
    "    '    los 5 campeonatos).@NL@@NL@'"
)

GLOBALES = [
    ("V3.6.66-SDK6", "V3.6.67-SDK6"),
    ("3.6.66-SDK6", "3.6.67-SDK6"),
    ("v3666-sdk6", "v3667-sdk6"),
    ("3.6.66", "3.6.67"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.67-SDK6", "frente a V3.6.66-SDK6"),
    ("tras probar V3.6.67", "tras probar V3.6.66"),
]


def main():
    if DEST.exists():
        print("regenerando (release-v3667 ya existía)…")
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
            print(f"  ✓ {f.name}: notas FASE 69 insertadas")
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
