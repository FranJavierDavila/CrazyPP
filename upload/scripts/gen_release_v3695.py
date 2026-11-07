#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3695 — hereda scripts/release-v3694 → scripts/release-v3695
e inserta las NOTAS de la FASE 97 «ETIQUETAS FUERA DE LA VISTA + RIVAL
ANCLADO A LA MESA (r103)».

Ronda 103: dos frentes del dueño — las etiquetas de la barra salen del
primer plano (fijas, en el plano de la barra, a su altura, a la derecha
fuera de la visión de la mesa) y el rival de los campeonatos SIEMPRE
anclado a la mesa (Halloween colgaba del scene y el recentrado lo
descolocaba).

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas (el FIN del bloque heredado ya queda a
3.6.95 tras la pasada de tokens). Idempotente (regenera desde v3694).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3694"
DEST = RAIZ / "scripts" / "release-v3695"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 96 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada ya dice 3.6.95)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 96 — PALA RIVAL FIEL + BARRA POR" + NL + "'"
BLOQUE_VIEJO_FIN = "    '  3.6.95" + NL + "'"

# líneas de texto PLANO de las notas FASE 97 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 97 — ETIQUETAS FUERA DE LA VISTA +",
    "    'RIVAL ANCLADO A LA MESA (r103).",
    "    'El dueño devuelve la r102 con dos frentes: «las etiquetas de",
    "    'altura de la barra no estén en primer plano: no dejan jugar con",
    "    'comodidad al estar sobre la línea de visión de mesa. Estarán",
    "    'fijas sin ningún cambio de orientación, ancladas a la altura de",
    "    'la barra que movemos y en su mismo plano, pero en la parte",
    "    'derecha fuera de la visión de la mesa», y «TODOS los rivales de",
    "    'los campeonatos a la derecha de la mesa fuera del campo de",
    "    'visión y SIEMPRE anclados a la posición de la mesa… si",
    "    'reorientamos la cámara o escaneamos una nueva zona condiciona",
    "    'su colocación y NO PUEDE SER». r103 cierra los dos.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.94-SDK6):",
    "    '",
    "    '  · ETIQUETAS FUERA DE LA VISTA: el rótulo de cm y las flechas",
    "    '    dejan el primer plano (estorbaban la línea de visión de la",
    "    '    mesa) y viven A LA DERECHA de la mesa (canto derecho +0,42 →",
    "    '    x≈1,18 m), en el MISMO PLANO que la barra (z = centro de",
    "    '    mesa) y ANCLADAS a su altura (cinta +0,075): suben y bajan",
    "    '    con ella en vivo. Son MALLAS DE ORIENTACIÓN FIJA (miran al",
    "    '    jugador de siempre, NUNCA giran con la cabeza — adiós",
    "    '    sprites).",
    "    '",
    "    '  · RIVAL SIEMPRE EN SU SITIO: Halloween era el ÚNICO campeonato",
    "    '    que colgaba el zombi (y cartel, manos, dianas, HUD, globos,",
    "    '    trozos, humo, manchas, insignia) de game.SCENE en vez de",
    "    '    game.RIG — al recentrar la vista (botón/escaneo) la mesa y",
    "    '    la sala giran con el rig y lo de scene se queda atrás: el",
    "    '    zombi acababa detrás de la mesa a la altura de la raqueta.",
    "    '    Ahora TODO lo anclado a mesa vive en el RIG (28 puntos de",
    "    '    anclaje): el rival está SIEMPRE a la derecha de la mesa,",
    "    '    fuera de la línea de juego, INDEPENDIENTE de recentrados y",
    "    '    escaneos. Los otros cuatro campeonatos ya nacían en el rig",
    "    '    (verificado). Conversiones mundo→rig donde el cambio lo",
    "    '    exige: billboard de las manos y rayo de la pistola contra",
    "    '    dianas (patrón c12 r73 worldToLocal); el haz visual sigue en",
    "    '    mundo (nace de la cámara XR) y el visor de moscas en cámara.",
    "    '",
    "    '  QA r103 49/0 (estática + en vivo: rótulo a x=1,1825 en el",
    "    '  plano de la barra y a su altura, mallas isMesh, viaje con la",
    "    '  barra, rayo convertido con el rig girado 90° da en la diana",
    "    '  err 5e-16, billboard en espacio rig, stick r102 intacto) ·",
    "    '  QA r102 51/0 re-anclada sobre el código r103 · cascada",
    "    '  sellada a 3.6.95",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3695 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.95.
    for viejo, nuevo in (("V3.6.94-SDK6", "V3.6.95-SDK6"),
                         ("3.6.94-SDK6", "3.6.95-SDK6"),
                         ("v3694-sdk6", "v3695-sdk6"),
                         ("3.6.94", "3.6.95"),
                         ("V3.6.94", "V3.6.95"),
                         ("v3694", "v3695"),
                         ("release-v3694", "release-v3695"),
                         ("staging-v3694", "staging-v3695")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 96 → FASE 97 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 96 → FASE 97 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 96 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
