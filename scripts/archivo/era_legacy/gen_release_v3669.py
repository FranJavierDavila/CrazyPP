#!/usr/bin/env python3
"""gen_release_v3669 — hereda scripts/release-v3668 → scripts/release-v3669
e inserta las NOTAS de la FASE 71 «LA RAQUETA MODO FANTASMA» en build_zip.py.

Idempotente: si release-v3669 ya existe, se regenera desde cero.
"""
import re
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3668"
DEST = RAIZ / "scripts" / "release-v3669"

BZ = DEST / "build_zip.py"

# Bloque de notas FASE 70 (r76) que sale entero
BLOQUE_VIEJO_INI = ("    'Rama    : main · SDK6 (FASE 70 — EL PULSO CRAZY: la aprobación\\n'")
BLOQUE_VIEJO_FIN = ("    '    desactiva el Pulso por completo (flujo legacy intacto).\\n\\n'")

# Bloque nuevo FASE 71 (r77)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 71 — LA RAQUETA MODO FANTASMA: la nota\\n'
    'del dueño sobre la academia — «en el apartado de academia el\\n'
    'tutorial: en las fases iniciales, antes de que diga "Pulsa el botón\\n'
    'A… Tu mando se convierte en tu raqueta", en lugar de colocar la\\n'
    'raqueta visible con el mando puede aparecer en modo fantasma sin\\n'
    'verse aún, hasta que aparece cuando lo dice»)\\n\\n'
    'Novedades de esta versión (frente a V3.6.68-SDK6):\\n\\n'
    '  · LA RAQUETA MODO FANTASMA: en LA ACADEMIA la pala REAL nace\\n'
    '    INVISIBLE — sólo los mandos GLB anclados acompañan al jugador\\n'
    '    durante la bienvenida y las 4 acciones del paso 1. La raqueta\\n'
    '    MATERIALIZA en el instante EXACTO en que la voz dice «tu mando\\n'
    '    se convierte en tu raqueta» (subfase 4), con la aura dorada\\n'
    '    como destello de nacimiento: el momento llega INTACTO, sin la\\n'
    '    raqueta anticipada que lo estropeaba.\\n\\n'
    '  · A PRUEBA DE RESURRECCIÓN: la llave vive en el núcleo\\n'
    '    (setPalaOculta) con UNA sola regla de visibilidad que respetan\\n'
    '    el cambio de mano (A/X), la vuelta del Hall y CUALQUIER salida\\n'
    '    de la academia (jugar ya, B/Y, fin del guion). Nadie se queda\\n'
    '    sin raqueta jamás; fuera de la academia, CERO cambios.\\n\\n'
"""


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    # 1 · identidad de la release: v3668 → v3669 / V3.6.68 → V3.6.69
    txt = txt.replace("V3.6.68-SDK6", "V3.6.69-SDK6")
    txt = txt.replace("3.6.68-SDK6", "3.6.69-SDK6")   # guards contra game_src
    txt = txt.replace("v3668-sdk6", "v3669-sdk6")
    txt = txt.replace("release-v3668", "release-v3669")
    txt = txt.replace("staging-v3668", "staging-v3669")
    txt = txt.replace('grep -c "3.6.68"', 'grep -c "3.6.69"')
    txt = txt.replace("menciones 3.6.68", "menciones 3.6.69")
    txt = txt.replace("no es el v3668", "no es el v3669")
    txt = txt.replace("n3636 = int", "n3669 = int")
    txt = txt.replace("if n3636 < 4:", "if n3669 < 4:")

    # 2 · notas: bloque FASE 70 → bloque FASE 71
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 70 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + BLOQUE_NUEVO + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.69-SDK6'" in txt, "guard VERSION"
    assert "V3.6.69-SDK6" in txt, "badge"
    assert "FASE 71" in txt, "notas FASE 71"
    assert "FASE 70" not in txt, "quedan notas FASE 70"
    print("✓ release-v3669 creada (notas FASE 71, guards V3.6.69-SDK6)")


if __name__ == "__main__":
    main()
