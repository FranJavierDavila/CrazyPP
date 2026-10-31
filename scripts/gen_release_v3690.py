#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3690 — hereda scripts/release-v3689 → scripts/release-v3690
e inserta las NOTAS de la FASE 92 «GESTOS CONTINUOS DEL MENÚ (r98)».

Ronda 98, tres peticiones del dueño sobre la interfaz de los menús:
 1) TOOLTIPS BONITOS: bocadillo sobre fondo blanco, texto en negro y cola
    que apunta con precisión a cada apartado.
 2) DESLIZADORES ARRASTRABLES: gatillo apretado sobre el deslizador +
    mando a derecha/izquierda (más intuitivo que tocar un punto).
 3) MESA AGARRABLE: apuntar a la mesa (rayo de selección), gatillo y
    mover arriba/abajo; texto BIEN GRANDE sobre el lado del dueño con la
    altura; el tooltip explica cómo se ajusta.

Lección de la r93 aplicada: los guards en MINÚSCULA se heredan REEMPLAZADOS
aquí — nada de correcciones post-gen. Idempotente (si release-v3690 existe,
se REGENERA desde v3689 para garantizar un bloque de notas íntegro).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3689"
DEST = RAIZ / "scripts" / "release-v3690"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 91 completo en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 91 — LA CALABAZA ES LA BOLA VIVA (r97)." + NL + "'"
BLOQUE_VIEJO_FIN = "    '  presupuesto refrescado · fisica 11/0)" + NL + "'"

# líneas de texto PLANO de las notas FASE 92 (sin escapes: se unen abajo,
# patrón exacto del gen r96: ln + NL + "'" unidos con saltos reales)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 92 — GESTOS CONTINUOS DEL MENÚ (r98).",
    "    'Tres peticiones del dueño sobre la interfaz de los menús: los",
    "    'tooltips no convencen (quiero un bocadillo blanco con texto negro",
    "    'que apunte con precisión), los deslizadores deben poder arrastrarse",
    "    'con el gatillo apretado moviendo el mando a derecha e izquierda, y",
    "    'la altura de la mesa se agarra apuntándole con el mando (rayo de",
    "    'selección) subiéndola o bajándola, con un texto bien grande sobre",
    "    'nuestro lado de la mesa con su altura.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.90-SDK6):",
    "    '",
    "    '  · BOCADILLO BLANCO DEL DUEÑO: el tooltip del menú deja la caja",
    "    '    oscura con borde ámbar y pasa a BOCADILLO — burbuja BLANCA con",
    "    '    sombra suave, texto NEGRO y una COLA (triángulo) que aterriza",
    "    '    en el centro EXACTO del control apuntado; si la burbuja se",
    "    '    recorta en los bordes, la cola sale inclinada y aun así llega.",
    "    '",
    "    '  · DESLIZADORES ARRASTRABLES: las barras de volumen (música y",
    "    '    efectos) fijan el valor al PULSAR (como hasta ahora) y SIGUEN",
    "    '    ajustando EN VIVO mientras el gatillo va apretado y el mando se",
    "    '    desplaza a izquierda/derecha (_menuDrag por mano, actualizado",
    "    '    cada frame, deciles honestos, tick por paso y cierre limpio en",
    "    '    selectend — nada queda agarrado si el rayo sale del panel).",
    "    '",
    "    '  · MESA AGARRABLE (adiós al raíl): en AJUSTES › Sala y Escena ›",
    "    '    Mesa, apuntar a la mesa REAL enciende el RAYO DE SELECCIÓN (el",
    "    '    haz llega hasta ella y un anillo marca el punto de contacto);",
    "    '    con el gatillo apretado la mesa SUBE/BAJA siguiendo la altura",
    "    '    del mando 1:1 (clamp 0,70-0,84 m) y un RÓTULO BIEN GRANDE sobre",
    "    '    el lado del dueño muestra los cm vivos (76 cm · Media) con tick",
    "    '    por cm y fundido de despedida. El TOOLTIP del control explica el",
    "    '    gesto («Apunta a la mesa, mantén el gatillo y súbela o bájala»),",
    "    '    la página MESA muestra la lectura viva y los − / + de 1 cm",
    "    '    siguen ahí. Los campeonatos siguen INTOCABLES (regla r96).",
    "    '",
    "    '  · HUB /descargas al día con la versión (la r97 no lo llevó).",
    "    '",
    "    '  QA r98 69/0 (estatica + en vivo: bocadillo blanco con texto negro",
    "    '  y cola al píxel, arrastre de las dos barras por ambas manos,",
    "    '  agarre 1:1 con clamps 0,70/0,84, rótulo sobre el lado del dueño,",
    "    '  persistencia, limpieza total fuera de la página MESA, mesa",
    "    '  intocable en campeonato y 0 pageerrors) · qa_r96 re-anclada con",
    "    '  honestidad (raíl retirado — 91/0) · presupuesto refrescado",
    "    '  (boot 1809 ms) · cascada sellada a 3.6.90 (34 capas)",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3690 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP)
    #    (el -SDK6 PRIMERO; el token desnudo 3.6.89 cubre los guards
    #    tardíos del paquete — lección r93: nada queda sin re-anclar)
    for viejo, nuevo in (("v3690-sdk6", "v3690-sdk6"),
                         ("V3.6.90-SDK6", "V3.6.90-SDK6"),
                         ("3.6.90-SDK6", "3.6.90-SDK6"),
                         ("3.6.89", "3.6.90"),
                         ("V3.6.89", "V3.6.90"),
                         ("v3689", "v3690"),
                         ("release-v3689", "release-v3690"),
                         ("staging-v3689", "staging-v3690")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 91 → FASE 92
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 91 → FASE 92 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 91 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
