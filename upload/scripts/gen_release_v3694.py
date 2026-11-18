#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3694 — hereda scripts/release-v3693 → scripts/release-v3694
e inserta las NOTAS de la FASE 96 «PALA RIVAL FIEL + BARRA POR
JOYSTICK (r102)».

Ronda 102: cierra los cuatro frentes que el dueño tenía abiertos: la pala
del rival EN VIVO y EN SU SITIO (multijugador), la etiqueta de la barra
pegada al jugador, el ajuste por joystick con aviso al jugador y la barra
fija salvo ajuste deliberado.

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas (el FIN del bloque heredado ya queda a
3.6.94 tras la pasada de tokens). Idempotente (regenera desde v3693).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3693"
DEST = RAIZ / "scripts" / "release-v3694"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 95 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada ya dice 3.6.94)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 95 — SAQUE RESTAURADO + BARRA POR" + NL + "'"
BLOQUE_VIEJO_FIN = "    '  sellada a 3.6.94" + NL + "'"

# líneas de texto PLANO de las notas FASE 96 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 96 — PALA RIVAL FIEL + BARRA POR",
    "    'JOYSTICK (r102).",
    "    'El dueño cerró la r101 con cuatro frentes abiertos: «la partida",
    "    'multijugador es imposible… no ven la colocación de la raqueta de",
    "    'forma correcta… la orientación de la pala no se corresponde», la",
    "    'etiqueta informativa debía quedar «sobre la mesa pero pegada al",
    "    'jugador, no en el centro bajo la red», la altura de la barra se",
    "    'controla «mejor con cualquiera de los joysticks de los mandos» y",
    "    '«debemos informar de este control al jugador». r102 cierra los",
    "    'cuatro.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.93-SDK6):",
    "    '",
    "    '  · LA PALA DEL RIVAL, POR FIN FIEL (multijugador): la pose v2",
    "    '    enviaba el grip CRUDO y el receptor multiplicaba la montura",
    "    '    SIN conjugarla por el espejo de 180° — la cara llegaba",
    "    '    volteada ~166° y el centro de la hoja desplazado ~26 cm en",
    "    '    dirección contraria a la hoja (medido en QA: 26,1 cm).",
    "    '    Ahora la mano con pala viaja como CUATERNIÓN VISUAL completo",
    "    '    (grip ⊗ montura viva — la misma fórmula probada del camino",
    "    '    v1) y el receptor lo conjuga ENTERO sin multiplicar nada:",
    "    '    el rival ve la pala EXACTAMENTE donde y como está (extremos",
    "    '    derechos/izquierdos incluidos). PROTO 1→2: dos cascos con",
    "    '    versiones distintas caen a v1 y se AVISAN, jamás interpretan",
    "    '    mal el cable.",
    "    '",
    "    '  · ETIQUETA PEGADA AL JUGADOR: el rótulo de cm y las flechas",
    "    '    flotan sobre el CUADRANTE PROPIO de la mesa (30 cm del borde",
    "    '    cercano, z=-0,53 m), no en el centro bajo la red; la cinta",
    "    '    sigue en la red como referencia del pase bajo y el conjunto",
    "    '    viaja con su altura.",
    "    '",
    "    '  · BARRA POR JOYSTICK (cualquiera de los dos mandos): el eje Y",
    "    '    del stick sube/baja la barra en pasos de 1 cm (14 cm/s a",
    "    '    plena deflexión, muerta 0,30, clamps 5..40 cm, persistencia",
    "    '    pp_train_barra_v1). El stick MANDA sobre la proximidad:",
    "    '    suelta la barra si estuviera agarrada y anula el dwell para",
    "    '    que la mano no la re-agarre sola. En el PRO TRAINING el",
    "    '    stick no tiene otro uso (sin conflictos). La barra queda",
    "    '    FIJA salvo ajuste deliberado.",
    "    '",
    "    '  · AVISO AL JUGADOR: la pista del rótulo nombra los DOS caminos",
    "    '    (JOYSTICK ↑↓ O MANO EN LA CINTA) y al entrar por primera vez",
    "    '    al PASE BAJO un toast lo explica (ES/EN).",
    "    '",
    "    '  QA r102 51/0 (estática + en vivo: códec PROTO=2 ida y vuelta,",
    "    '  quatFromNet del servido == R⊗q⊗R⁻¹ exacto, fórmula vieja",
    "    '  medida a 26,1 cm, rótulo a z=-0,53, stick: 1 cm por paso,",
    "    '  clamps 5/40, suelta el agarre y anula el dwell) · QA r101",
    "    '  58/0 re-verificada sobre el código r102 · cascada sellada a",
    "    '  3.6.94",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3694 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.94.
    for viejo, nuevo in (("V3.6.93-SDK6", "V3.6.94-SDK6"),
                         ("3.6.93-SDK6", "3.6.94-SDK6"),
                         ("v3693-sdk6", "v3694-sdk6"),
                         ("3.6.93", "3.6.94"),
                         ("V3.6.93", "V3.6.94"),
                         ("v3693", "v3694"),
                         ("release-v3693", "release-v3694"),
                         ("staging-v3693", "staging-v3694")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 95 → FASE 96 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 95 → FASE 96 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 95 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
