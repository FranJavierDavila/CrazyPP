#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3697 — hereda scripts/release-v3696 → scripts/release-v3697
e inserta las NOTAS de la FASE 99 «DERIVA DEL PUNTERO + RENDIMIENTO DEL
MENÚ (r105)».

Ronda 105: informe del dueño tras V3.6.96 — «muchísimo mejor ahora los
menús, PERO debes revisar que existe una DERIVA entre los punteros y el
menú y no se corresponde donde apuntas con los botones. Lo que me parece
es que ahora tenemos bastante pérdida de rendimiento y eso es muy
importante no perderlo».

r105: (1) FIX deriva — el cursor del menú proyectaba en el plano antiguo
0,72×1,08 mientras el panel es 0,90×1,35 (desviación hasta 0,09/0,135 m
hacia el centro); (2) rendimiento — mips OFF en la textura del menú
(magnificación pura a ~1 m, cada repintado pagaba mipgen inútil) y
repintado por HOVER throttled a 90 ms (barrer el panel encadenaba
15-20 repintados/s del lienzo 1024×1536).

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas. Idempotente (regenera desde v3696).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3696"
DEST = RAIZ / "scripts" / "release-v3697"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 98 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada ya dice 3.6.97)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 98 — MENÚS A PANTALLA COMPLETA (r104)." + NL + "'"
BLOQUE_VIEJO_FIN = " · sellada a 3.6.97" + NL + "'"

# líneas de texto PLANO de las notas FASE 99 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 99 — DERIVA DEL PUNTERO + RENDIMIENTO DEL",
    "    'MENÚ (r105).",
    "    'Informe del dueño tras V3.6.96: «muchísimo mejor ahora los menús,",
    "    'PERO debes revisar que existe una DERIVA entre los punteros y el",
    "    'menú y no se corresponde donde apuntas con los botones. Lo que me",
    "    'parece es que ahora tenemos bastante pérdida de rendimiento y eso",
    "    'es muy importante no perderlo».",
    "    '",
    "    'Novedades de esta version (frente a V3.6.96-SDK6):",
    "    '",
    "    '  · FIX DERIVA DEL PUNTERO: el punto/cursor del menú seguía",
    "    '    proyectándose en el plano ANTIGUO 0,72×1,08 m mientras el",
    "    '    panel es 0,90×1,35 m desde r104 — el cursor quedaba desviado",
    "    '    hasta 0,09 m (X) y 0,135 m (Y) hacia el centro respecto al",
    "    '    rayo real. Ahora el punto coincide EXACTAMENTE con donde",
    "    '    apunta el rayo y con el botón que activa el gatillo (el",
    "    '    hit-test de botones y los sliders ya usaban el punto exacto:",
    "    '    solo el dibujo del cursor estaba desviado).",
    "    '",
    "    '  · RENDIMIENTO (el menú ya no paga de más): (1) mips OFF en la",
    "    '    textura del menú — el panel vive a ~1 m (magnificación pura:",
    "    '    el visor pide MÁS píxeles de los que tiene la textura), así",
    "    '    que cada repintado pagaba la generación de ~12 niveles de mip",
    "    '    encima del upload de 6 MB sin ninguna ganancia visual (a 1 m",
    "    '    ya se usaba mip 0 + bilineal); (2) el repintado por HOVER va",
    "    '    THROTTLED a 90 ms (≈11 Hz): barriendo el panel con el rayo se",
    "    '    encadenaban 15-20 repintados por segundo del lienzo entero",
    "    '    1024×1536 y eso se notaba en los FPS del casco. El highlight",
    "    '    sigue fluido y los repintados por ACCIÓN (clicks, páginas,",
    "    '    sliders, estado del partido, medallón vivo) siguen siendo",
    "    '    inmediatos.",
    "    '",
    "    '  · NADA de gameplay tocado: física, saque, rivales, campeonatos",
    "    '    y multijugador heredan r104 sin un byte de cambio (los 6",
    "    '    módulos core pasan node --check; física determinista 11/0).",
    "    '",
    "    '  QA r105 en verde (agujas estáticas + juego en vivo: cursor",
    "    '  exacto sobre el panel 0,90×1,35, textura sin mips, throttle de",
    "    '  hover a 90 ms, renderOrder 9999/9998 intactos, regresión r104",
    "    '  del panel/fuentes/contraste) · sellada a 3.6.97",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3697 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.97.
    for viejo, nuevo in (("V3.6.96-SDK6", "V3.6.97-SDK6"),
                         ("3.6.96-SDK6", "3.6.97-SDK6"),
                         ("v3696-sdk6", "v3697-sdk6"),
                         ("3.6.96", "3.6.97"),
                         ("V3.6.96", "V3.6.97"),
                         ("v3696", "v3697"),
                         ("release-v3696", "release-v3697"),
                         ("staging-v3696", "staging-v3697")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 98 → FASE 99 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 98 → FASE 99 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 98 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
