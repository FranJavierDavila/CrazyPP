#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3693 — hereda scripts/release-v3692 → scripts/release-v3693
e inserta las NOTAS de la FASE 95 «SAQUE RESTAURADO + BARRA POR
PROXIMIDAD (r101)».

Ronda 101: el dueño devolvió la r100 con tres defectos (gatillo comido por
las flechas · saque estropeado por el velInst · reposo que secuestraba
botes) y pidió un ajuste de barra sencillo y sin interferencias.

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas (el FIN del bloque heredado ya queda a
3.6.93 tras la pasada de tokens). Idempotente (regenera desde v3692).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3692"
DEST = RAIZ / "scripts" / "release-v3693"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 94 completo en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 94 — LA BOLA VIVA EN TU PALA + BARRA" + NL + "'"
BLOQUE_VIEJO_FIN = "    '  refrescado · cascada sellada a 3.6.93" + NL + "'"

# líneas de texto PLANO de las notas FASE 95 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 95 — SAQUE RESTAURADO + BARRA POR",
    "    'PROXIMIDAD (r101).",
    "    'El dueño devolvió la r100: el gatillo del entrenamiento se",
    "    'trababa (las flechas se COMÍAN el gesto y la bola del tee no",
    "    'salía), el saque había quedado estropeado por el velInst, el",
    "    'contacto de reposo secuestraba los botes suaves y el ajuste de",
    "    'la barra por rayo era inútil («donde apunto y donde están los",
    "    'botones nada tienen que ver»). r101 restaura lo que funcionaba y",
    "    'simplifica lo que no.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.92-SDK6):",
    "    '",
    "    '  · GATILLO LIBRE: serveTrigger vuelve a ser el EXACTO de",
    "    '    V3.6.91 — el gatillo SIEMPRE lanza la bola del tee (ninguna",
    "    '    función del juego vuelve a consumirlo).",
    "    '",
    "    '  · SAQUE RESTAURADO: fuera el velInst del lanzamiento (núcleo",
    "    '    y tee) — la bola sale con el filtro de velocidad de",
    "    '    V3.6.91, el gesto que funcionaba de memoria.",
    "    '",
    "    '  · BOTE NATURAL RECUPERADO (el estándar Eleven, sin tocar los",
    "    '    golpes): umbral de reposo ÚNICO 0,25 m/s (el dual 0,95/0,65",
    "    '    de r100 secuestraba botes legítimos). La bola que llega con",
    "    '    vida BOTA y decae; sólo se posa lo que llega muerto — y la",
    "    '    bola apoyada sigue viajando 1:1 con la pala, rueda con la",
    "    '    inclinación y el swing la lanza limpia (transporte r100",
    "    '    intacto). «Toc» suave de goma al posar.",
    "    '",
    "    '  · BARRA DEL PASE BAJO POR PROXIMIDAD (adiós flechas y rayo):",
    "    '    la MANO LIBRE entra en el pasillo de la cinta (≥0,30 s) y",
    "    '    la barra sigue su altura en vivo, en pasos de 1 cm (blip +",
    "    '    háptica por paso, clamps 5..40 cm, persistencia",
    "    '    pp_train_barra_v1); al APARTAR la mano queda fijada (toast",
    "    '    de confirmación). SIN NINGÚN BOTÓN: gatillo y grip quedan",
    "    '    100% para el juego. Rótulo con pista por estado (ALTURA",
    "    '    BARRA / MUEVE LA MANO / APARTA LA MANO PARA FIJAR) y",
    "    '    flechas indicadoras pegadas a la cinta.",
    "    '",
    "    '  QA r101 58/0 (estática + en vivo: saque = filtro V3.6.91,",
    "    '  reposo real sin trompicones, bote natural a 1,2 m/s que",
    "    '  decae y se posa, transporte 1:1 + swing, barra que",
    "    '  agarra/sigue/fija/clampa) · golden de física 11/0 · cascada",
    "    '  sellada a 3.6.93",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3693 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.93.
    for viejo, nuevo in (("V3.6.92-SDK6", "V3.6.93-SDK6"),
                         ("3.6.92-SDK6", "3.6.93-SDK6"),
                         ("v3692-sdk6", "v3693-sdk6"),
                         ("3.6.92", "3.6.93"),
                         ("V3.6.92", "V3.6.93"),
                         ("v3692", "v3693"),
                         ("release-v3692", "release-v3693"),
                         ("staging-v3692", "staging-v3693")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 94 → FASE 95 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 94 → FASE 95 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 94 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
