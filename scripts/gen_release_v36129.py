#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.129-SDK6 (r33).
Crea scripts/release-v36129/ a partir de scripts/release-v36128/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 130
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36129 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36128.py
    python3 scripts/release-v36129/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36128"
DEST = RAIZ / "scripts" / "release-v36129"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 131 — LOTE APROBADO: los 4 superpoderes",
    "de pala elegidos de la propuesta + el ASTRO de la Estación Orbital",
    "vuelve a verse en las partidas).",
    "  · 1 · LOS 4 PODERES NUEVOS (11.º-14.º del registro PODERES_PALA,",
    "    con icono-insignia propio en la sintonía de la familia SuperPala",
    "    y voces ES/EN Piper de la casa; ventanas de 10 s, blips 3·2·1,",
    "    cortina en etapas 2/4 y precaliente — patrón fenix/oscuridad):",
    "    · PRISMA: estela arcoíris VIVA (matiz rotando), guía sutil de",
    "      trayectoria 3 s tras CADA golpeo propio y la desventaja ligera",
    "      del rival traducida a la IA (10 % de faltas largas; saques",
    "      intactos). La guía nunca aparece en defensa.",
    "    · ONDA DE CHOQUE: cada SMASH propio (golpeo ≥ 5,2 m/s hacia el",
    "      rival) nace un anillo expansivo en el plano de la mesa +",
    "      temblor breve del rig (0,35 s, ±9 mm) y la devolución de la IA",
    "      «en pleno swing» (1,0 s de margen) sale al 75 % — se consume",
    "      con esa devolución; sólo en smash, jamás en golpe normal.",
    "    · SALVAVIDAS: UNA vez por activación, si la bola supera nuestra",
    "      línea de fondo volando hacia fuera (y nuestra pala real está a",
    "      más de 0,55 m), la pala fantasma de luz la intercepta y la",
    "      devuelve AL 80 % por el camino LEGAL del clon (solver de la",
    "      casa + golpe de jugador). El warp se recarga con cada",
    "      activación; si llegamos nosotros, NO se gasta.",
    "    · SÚPER ANCLA: 10 s de cadenas de energía siguiendo la pala —",
    "      inmune a los poderes del rival: la PUERTA CENTRAL",
    "      anclaBloqueo() la consultan los 4 campeonatos (locura, oeste,",
    "      magia y orbital) justo cuando el poder rival va a entrar en",
    "      juego: se ESTRELLA con destello metálico, mensaje y háptica.",
    "      Sin bonus activo: si el rival no lanza nada, no hace nada.",
    "  · 2 · FIX ASTRO (informe del dueño: «en el campeonato de Estación",
    "    Estelar no aparece el rival Astro en las partidas»): el",
    "    createRival modo «perezoso» del SDK llevaba desde la FASE 7",
    "    (r72) sin colgar la textura viva del material (mat.map = null) —",
    "    el standee era un plano blanco invisible. Ahora el build",
    "    perezoso llama ponMapa(tex) y cada cara de estado sube a GPU",
    "    (initTexture). Verificado en vivo: mat.map con imagen 512×1024",
    "    en sala y duelo, con leave()/re-launch incluido.",
    "  · 3 · Física c04/c05 INTACTA (sha256 byte-exacto contra la r26b:",
    "    df8f71a3 / 8bb62082) — las faltas y flojedades son decisiones",
    "    del solver, jamás del integrador; los saques JAMÁS se tocan.",
    "  · 4 · QA: test_r33_poderes_v36129 77/0 · regresión re-anclada r33:",
    "    r32 49/0 · r31 47/0 · r30 54/0 · r29 75/0 · r28 37/0 · r27 40/0.",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36128", "release-v36129"),
    ("staging-v36127", "staging-v36128"),
    ("V3.6.127-SDK6", "V3.6.128-SDK6"),
    ("3.6.127-SDK6", "3.6.128-SDK6"),
    ("v36127-sdk6", "v36128-sdk6"),
    ("v36127", "v36128"),
    ("3.6.127", "3.6.128"),
    ("fase 129", "fase 130"),
    ("FASE 129", "FASE 130"),
    ("Fase 129", "Fase 130"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r31 a FASE 130/3.6.128 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 130 — HIGIENE TEXTUAL"
FIN_MARCADOR = "'  3.6.128" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.128-SDK6 lista: el registro de poderes ya cuenta la verdad de Fénix (dinámica normal, saques normales, la falta del 15 % para la IA) — deuda cosmética de la r30 pagada sin tocar una línea de lógica.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.128-SDK6 lista: los 3 salones visten el ARTE DEL DUEÑO con su música ambiental (prioridad sobre el menú) y el icono de silencio en la pared frontal.')"


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
        # bloque de notas → FASE 130 (sustitución EXACTA, lección r24:
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
    print(f"\nrelease-v36129 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36129/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
