#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.127-SDK6 (r31).
Crea scripts/release-v36127/ a partir de scripts/release-v36126/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 129
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36127 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36127.py
    python3 scripts/release-v36127/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36126"
DEST = RAIZ / "scripts" / "release-v36127"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 129 — HIGIENE TEXTUAL: el registro de",
    "poderes ya no presume el boost anulado de Fénix — deuda cosmética",
    "de la r30 pagada, CERO lógica tocada).",
    "  · 1 · LA DEUDA: el comentario de SÚPER FÉNIX en PODERES_PALA",
    "    (escrito en la r29) seguía diciendo «+18 % de rapidez» cuando",
    "    el boost quedó ANULADO en la r30 por orden del dueño («no es",
    "    jugable… la dinámica del juego sea la de una partida normal con",
    "    una pequeña penalización para la IA… los saques deben",
    "    permitirse normales»).",
    "  · 2 · LA CURA (solo comentario, +216 B en el build): el bloque",
    "    del registro describe ahora el estado REAL — fuego del Wizard",
    "    intacto, dinámica NORMAL, saques normales y toda la ventaja en",
    "    FENIX_OUT_P 0.15 — con la nota histórica del veto. El único",
    "    ×1,18 restante en c12 es el FUEGO de DUELOS LOCOS (r84, online,",
    "    por golpeo con guard _dlOn(fuego)) — activo por diseño, no es",
    "    Fénix.",
    "  · 3 · TEST NUEVO: test_r31_higiene_v36127 (47/0) — sellos de la",
    "    ronda (3.6.127-SDK6 · FASE 129 · 11.166.858 B · golden",
    "    6badce1b… · sw.js · badge · hub), registro sin la afirmación",
    "    vieja, único ×1,18 = DUELOS LOCOS, ventanas código↔i18n",
    "    (Fénix/Crono 10 s · Oscuridad 20 s en ES y EN), Hielo anulado,",
    "    10 poderes con icono y voz, c04/c05 byte-exacto. Regresión",
    "    re-anclada r31: r30 54/0, r29 75/0, r28 37/0, r27 40/0,",
    "    r26b 171/0.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO contra la r26b; cero cambios de códec en c09.",
    "  · bump BYTE-EXACTO (11.166.858 B · golden 6badce1b…).",
    "  SE CONSERVA TODO: Fénix jugable r30, salones IA r30, Súper",
    "    Oscuridad, Crono centrado, voces Piper animosas, iconos del",
    "    dueño, bug de la bola oculta cerrado (r28), FORO3D completo",
    "    (r27), bola atractora y ráfagas r26/r26b, barrera eléctrica,",
    "    skins r21, hall cabaña, cortina etapas 2/4, _bolaGuard, P4,",
    "    CRAZY LINK v2, ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.127",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36126", "release-v36127"),
    ("staging-v36126", "staging-v36127"),
    ("V3.6.126-SDK6", "V3.6.127-SDK6"),
    ("3.6.126-SDK6", "3.6.127-SDK6"),
    ("v36126-sdk6", "v36127-sdk6"),
    ("v36126", "v36127"),
    ("3.6.126", "3.6.127"),
    ("fase 128", "fase 129"),
    ("FASE 128", "FASE 129"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r30 a FASE 129/3.6.127 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 129 — FÉNIX JUGABLE"
FIN_MARCADOR = "'  3.6.127" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.127-SDK6 lista: Fénix ya es JUGABLE (dinámica normal, saques normales y solo la pequeña falta del 15 % para la IA) y los 3 salones lucen ilustraciones IA ricas al nivel de Locura y Magia.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.127-SDK6 lista: el registro de poderes ya cuenta la verdad de Fénix (dinámica normal, saques normales, la falta del 15 % para la IA) — deuda cosmética de la r30 pagada sin tocar una línea de lógica.')"


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    for f in sorted(DEST.iterdir()):
        if not f.is_file():
            continue
        txt = f.read_text(encoding='utf-8')
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        # bloque de notas → FASE 129 (sustitución EXACTA, lección r24:
        # sin conservar la comilla de cierre del marcador FIN)
        i = txt.find(INI_MARCADOR)
        j = txt.find(FIN_MARCADOR, i) if i >= 0 else -1
        if i >= 0 and j >= 0:
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR):]
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f"\nrelease-v36127 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36127/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
