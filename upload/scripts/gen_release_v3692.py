#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3692 — hereda scripts/release-v3691 → scripts/release-v3692
e inserta las NOTAS de la FASE 94 «LA BOLA VIVA EN TU PALA + BARRA
INTERACTIVA (r100)».

Ronda 100, cuatro peticiones del dueño tras V3.6.91:
 1) BARRA INTERACTIVA del PASE BAJO (Pro Training): altura ajustable ±1 cm
    con flechas ↑/↓ a la altura de la barra, lectura en cm sobre la mesa y
    haz de selección de la mano libre.
 2) ARO DEL GLOBO DEFENSIVO al CENTRO de la mesa (vivía a +0,50 m del centro
    hacia el rival).
 3) PRIMER SAQUE FIEL: la velocidad INSTANTÁNEA del mando manda al soltar
    (el filtro de media móvil llegaba detrás del pico del flick).
 4) FÍSICA BOLA-PALA tipo Eleven: contacto de reposo (sin trompicones) y
    transporte de la bola apoyada (jamás la atraviesa al levantar la pala),
    con la física de golpes y el golden BYTE A BYTE intactos.

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS aquí.
Idempotente (si release-v3692 existe, se REGENERA desde v3691).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3691"
DEST = RAIZ / "scripts" / "release-v3692"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 93 completo en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 93 — AJUSTES FINOS DEL MENÚ (r99)." + NL + "'"
BLOQUE_VIEJO_FIN = "    '  refrescado (boot 1795 ms) · cascada sellada a 3.6.92 (36 capas)" + NL + "'"

# líneas de texto PLANO de las notas FASE 94 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 94 — LA BOLA VIVA EN TU PALA + BARRA",
    "    'INTERACTIVA (r100).",
    "    'Cuatro peticiones del dueño tras V3.6.91: la barra del PASE BAJO",
    "    'del Pro Training debe poder SUBIR y BAJAR de verdad (±1 cm) con",
    "    'flechas a su altura y la lectura en cm sobre la mesa; el aro del",
    "    'GLOBO DEFENSIVO debe flotar sobre el CENTRO de la mesa; el PRIMER",
    "    'saque debe salir con la velocidad REAL de la mano; y la bola",
    "    'depositada sobre la pala debe comportarse como en Eleven (rueda,",
    "    'se desliza, se recupera al empujar) sin romper la física de",
    "    'golpes que ya funcionaba.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.91-SDK6):",
    "    '",
    "    '  · BARRA INTERACTIVA (t2a): la cinta naranja del PASE BAJO deja",
    "    '    de ser fija — flecha ARRIBA y flecha ABAJO a su derecha con",
    "    '    rótulo de lectura en cm sobre la SUPERFICIE de la mesa (32 cm",
    "    '    de serie). El rayo de la MANO LIBRE las enfoca (haz de",
    "    '    selección + brillo + háptica) y el GATillo ajusta ±1 cm con",
    "    '    clamps 5..40 cm y persistencia (pp_train_barra_v1). El juez",
    "    '    de la prueba usa la altura VIVA (RIBBON_Y dinámica) — lo que",
    "    '    se ve ES lo que se juzga. i18n ES/EN (rótulo + descripción).",
    "    '",
    "    '  · ARO AL CENTRO: el toro verde del GLOBO DEFENSIVO (la línea con",
    "    '    el círculo arriba que preguntaba el dueño ES correcta: aro",
    "    '    objetivo + haz de guía) pasa de +0,50 m hacia el rival al",
    "    '    CENTRO de la mesa — el apex de un globo real ocurre junto a",
    "    '    la red. El juez no cambia (mide el apex del vuelo).",
    "    '",
    "    '  · PRIMER SAQUE FIEL: al soltar el grip la bola sale con la",
    "    '    velocidad INSTANTÁNEA de la mano cuando ésta es mayor que la",
    "    '    filtrada (velInst vs media móvil de 45 ms) — el flick del",
    "    '    lanzamiento ya no llega «cortado». El mismo criterio en el",
    "    '    tee del Pro Training (t4a/t4b). Gestos suaves: idéntico.",
    "    '",
    "    '  · BOLA VIVA EN LA PALA (el estándar Eleven, quirúrgico):",
    "    '    llegada MUY lenta a la CARA de la pala del jugador = APOYO",
    "    '    (sin rebote): proyección sin penetración, fricción tangencial",
    "    '    con acople de giro (rueda), umbral dual 0,95 con pala lenta /",
    "    '    0,65 con pala viva; y TRANSPORTE por frame de la bola apoyada",
    "    '    (viaja 1:1 con la pala, gravedad tangencial con fricción",
    "    '    estática — pala plana = bola quieta, pala inclinada = rueda",
    "    '    cuesta abajo, al acelerar se SUELTA y el CCD decide el golpe",
    "    '    natural: JAMÁS la atraviesa). «Toc» suave de goma al posar",
    "    '    (sin carga de poder, sin cuenta de golpes). Un GOLPE limpia",
    "    '    el apoyo; física de golpes, golden (11/0) e IA INTACTOS.",
    "    '",
    "    '  QA r100 81/0 (estática + en vivo: flick 4 m/s real, posar sin",
    "    '  golpe ni trompicones, transporte 1:1, swing golpea y despega,",
    "    '  barra ±1 cm con clamps y persistencia, mandos a 1,05 m sobre el",
    "    '  centro, rótulo de cm vivo) · golden de física 11/0 · presupuesto",
    "    '  refrescado · cascada sellada a 3.6.92",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3692 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: el bloque de notas heredado queda con su cola ya a 3.6.92
    #    (el FIN de BLOQUE_VIEJO_FIN arriba) — lección del primer intento.
    for viejo, nuevo in (("V3.6.91-SDK6", "V3.6.92-SDK6"),
                         ("3.6.91-SDK6", "3.6.92-SDK6"),
                         ("v3691-sdk6", "v3692-sdk6"),
                         ("3.6.91", "3.6.92"),
                         ("V3.6.91", "V3.6.92"),
                         ("v3691", "v3692"),
                         ("release-v3691", "release-v3692"),
                         ("staging-v3691", "staging-v3692")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 93 → FASE 94 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 93 → FASE 94 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 93 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
