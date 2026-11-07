#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3691 — hereda scripts/release-v3690 → scripts/release-v3691
e inserta las NOTAS de la FASE 93 «AJUSTES FINOS DEL MENÚ (r99)».

Ronda 99, dos ajustes finos del dueño sobre la interfaz de la r98:
 1) % DE LOS DESLIZADORES ENCIMA DE LA BARRA: la lectura de % vivía DENTRO
    de la barra y la bola del deslizador la tapaba al pasar — sube SOBRE
    el raíl (ámbar 17 px) y nunca se pisan.
 2) ALTURA DE LA MESA SOBRE LA MESA: el rótulo flotante pasa a DECAL PLANO
    sobre la superficie del lado del dueño (texto algo más pequeño y
    paralelo al tablero, legible mirando la mesa).

Lección de la r93 aplicada (dos veces): los guards en MINÚSCULA se heredan
REEMPLAZADOS aquí — nada de correcciones post-gen. Idempotente (si
release-v3691 existe, se REGENERA desde v3690 para garantizar un bloque de
notas íntegro).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3690"
DEST = RAIZ / "scripts" / "release-v3691"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 92 completo en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 92 — GESTOS CONTINUOS DEL MENÚ (r98)." + NL + "'"
# (los tokens se reemplazan ANTES: el bloque heredado ya dice 3.6.91)
BLOQUE_VIEJO_FIN = "    '  (boot 1809 ms) · cascada sellada a 3.6.91 (34 capas)" + NL + "'"

# líneas de texto PLANO de las notas FASE 93 (sin escapes: se unen abajo,
# patrón exacto del gen r99: ln + NL + "'" unidos con saltos reales)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 93 — AJUSTES FINOS DEL MENÚ (r99).",
    "    'Dos ajustes finos del dueño sobre la interfaz de la r98: los",
    "    'porcentajes de los deslizadores se pisan con la barra al moverla",
    "    '(van DENTRO del raíl) y la indicación de altura de la mesa debe",
    "    'vivir SOBRE la propia mesa, con texto algo más pequeño y paralelo",
    "    'a la superficie, que se pueda leer bien.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.90-SDK6):",
    "    '",
    "    '  · % ENCIMA DE LA BARRA: la lectura de los deslizadores de",
    "    '    volumen (música y efectos) sube SOBRE el raíl (ámbar, 17 px)",
    "    '    — la bola del deslizador ya no la tapa nunca al moverla.",
    "    '",
    "    '  · ALTURA SOBRE LA MESA: el rótulo flotante de la r98 pasa a",
    "    '    DECAL PLANO sobre la superficie del lado del dueño — plano",
    "    '    tumbado (texto mirando al techo, paralelo al tablero),",
    "    '    1,04 × 0,26 m y texto 96 px (algo más pequeño), a 6 mm del",
    "    '    tablero y 34 cm hacia la red desde el borde cercano, con",
    "    '    seguimiento POR FRAME de la superficie mientras se agarra",
    "    '    (nunca hundido ni flotando entre pasos). El gesto de agarre",
    "    '    de la r98 no cambia: apuntar (rayo de selección), gatillo y",
    "    '    mover arriba/abajo; los campeonatos siguen INTOCABLES.",
    "    '",
    "    '  QA r99 44/0 (estática + en vivo: % ámbar sobre el raíl y cero",
    "    '  tinta dentro de la barra, decal 1,04×0,26 tumbado a 6 mm en",
    "    '  z −0,57, pegado por frame, agarre 1:1 y clamps 0,70/0,84",
    "    '  intactos, persistencia, fundido y limpieza) · qa_r98",
    "    '  re-anclada con honestidad (rótulo decal — 69/0) · presupuesto",
    "    '  refrescado (boot 1795 ms) · cascada sellada a 3.6.91 (36 capas)",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3691 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP)
    #    (el -SDK6 PRIMERO; el token desnudo 3.6.90 cubre los guards
    #    tardíos del paquete — lección r93: nada queda sin re-anclar)
    for viejo, nuevo in (("v3691-sdk6", "v3691-sdk6"),
                         ("V3.6.91-SDK6", "V3.6.91-SDK6"),
                         ("3.6.91-SDK6", "3.6.91-SDK6"),
                         ("3.6.90", "3.6.91"),
                         ("V3.6.90", "V3.6.91"),
                         ("v3690", "v3691"),
                         ("release-v3690", "release-v3691"),
                         ("staging-v3690", "staging-v3691")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 92 → FASE 93
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 92 → FASE 93 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 92 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
