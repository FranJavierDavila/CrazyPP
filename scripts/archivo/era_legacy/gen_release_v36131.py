#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.131-SDK6 (r35).
Crea scripts/release-v36131/ a partir de scripts/release-v36130/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 133
    (con ABORTE DURO si los marcadores no casan — lección r33)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36131 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36131.py
    python3 scripts/release-v36131/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36130"
DEST = RAIZ / "scripts" / "release-v36131"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 133 — PRISMA VISIBLE: LA BOLA ARCOÍRIS,",
    "petición del dueño tras V3.6.130 — «en el superpoder de prisma no se",
    "nota la desventaja ni que se está aplicado, refuerza visualmente",
    "cambiando el color de la bola por los colores del arcoiris de forma",
    "aleatoria mientras duré el super poder»).",
    "  · 1 · LA BOLA ARCOÍRIS: mientras la ventana de Prisma vive, la BOLA",
    "    pinta colores del arcoíris ALEATORIOS (~6 saltos/s con",
    "    Math.random — no barrido) con paleta viva (S 0,95 · L 0,62) y",
    "    brasa en el EMISIVO (L 0,30) para que el salto se vea también",
    "    con glow dentro del casco. El tinte se aplica AL ACTIVAR (primer",
    "    salto inmediato) y en el refresco honesto; la estela arcoíris de",
    "    la r34 sigue hablando sólo en el campo rival — la bola habla",
    "    SIEMPRE, desde los dos lados de la mesa.",
    "  · 2 · RESTAURACIÓN HONESTA (patrón de tinte de la Oscuridad):",
    "    _prismaBolaTintAplicar guarda color+emisivo originales (getHex)",
    "    y _prismaBolaTintRestaurar los devuelve en _prismaFin (fin",
    "    natural, cortina de etapas 2/4, salida del partido) — la bola",
    "    vuelve a SU tinta SIEMPRE; restauración idempotente (guard de",
    "    tinte nulo).",
    "  · 3 · COOPERATIVO: Prisma y Oscuridad son los dos pintores de bola",
    "    y ahora se CE DEN la bola — el ÚLTIMO poder disparado gana y el",
    "    anterior suelta sin dejar rastro (nadie guarda el arcoíris como",
    "    «original» y la bola nunca queda prisionera de un tinte ajeno).",
    "    Auto-soltado en _prismaFrame si otro poder toma el testigo",
    "    (_megaActivaId ≠ prisma) con la ventana aún viva.",
    "  · 4 · QA: test_r35_prisma_v36131 36/0 · probe EN VIVO (Playwright,",
    "    estacion_orbital): bola arcoíris muestreada en vivo (colores",
    "    distintos salto a salto) · refresco re-conquista la bola ·",
    "    cesión a Oscuridad y devolución intacta · auto-soltado con Onda",
    "    · fin natural restaura color+emisivo · 0 errores de página.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec en c09.",
    "  SE CONSERVA TODO: fixes r34 (Red alineada en el rig, voz de",
    "    selección de los 14, Electricidad con retención de 1 s y fin",
    "    por baja, Prisma por campos), lote aprobado r33, salones del",
    "    dueño r32 con su música y su icono de silencio, higiene Fénix",
    "    r31, Fénix jugable r30, Súper Oscuridad, Crono, voces Piper,",
    "    iconos del dueño, bola atractora r26b, barrera eléctrica,",
    "    FORO3D r27, skins r21, cortina etapas 2/4, _bolaGuard, P4,",
    "    CRAZY LINK v2, ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.131",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36130", "release-v36131"),
    ("staging-v36130", "staging-v36131"),
    ("V3.6.130-SDK6", "V3.6.131-SDK6"),
    ("3.6.130-SDK6", "3.6.131-SDK6"),
    ("v36130-sdk6", "v36131-sdk6"),
    ("v36130", "v36131"),
    ("3.6.130", "3.6.131"),
    ("fase 132", "fase 133"),
    ("FASE 132", "FASE 133"),
    ("Fase 132", "Fase 133"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36130 son las de la r34, ya re-selladas a FASE 133 por los tokens):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 133 — CORRECCIONES A LOS SUPERPODERES"
                + NL + "'")
FIN_MARCADOR = ("    '  3.6.131" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.131-SDK6 lista: los superpoderes corregidos "
                     "según el informe del dueño (Red alineada en el rig · voz de "
                     "selección para los 14 · Electricidad con retención de 1 s y fin "
                     "por baja · Prisma sólo en campo rival).')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.131-SDK6 lista: el Prisma SE VE — la bola "
                     "pinta arcoíris aleatorio mientras la ventana vive y la devuelve "
                     "intacta al morir (cesión Oscuridad y auto-soltado incluidos).')")


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    notas_ok = 0
    linea_ok = 0
    for f in sorted(DEST.iterdir()):
        if not f.is_file():
            continue
        txt = f.read_text(encoding='utf-8')
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        # bloque de notas → FASE 133 (sustitución ASERTADA — lección r33).
        # Sólo exige los marcadores en los ficheros que LLEVAN el bloque
        # (build_zip.py); los demás (chuleta, leemes) sólo reciben tokens.
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            j = txt.find(FIN_MARCADOR, i)
            if j < 0:
                raise SystemExit(
                    f'ABORTA: INI sin FIN en {f.name} — nada escrito.')
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR):]
            notas_ok += 1
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
            linea_ok += 1
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    if notas_ok != 1 or linea_ok != 1:
        raise SystemExit(
            f'ABORTA: sustituciones esperadas 1/1, obtenidas '
            f'notas={notas_ok} · linea_final={linea_ok}.')
    print(f"\nrelease-v36131 generado ({tocados} ficheros tocados · "
          f"notas sustituidas {notas_ok} · línea final {linea_ok}).")
    print("Siguiente: python3 scripts/release-v36131/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
