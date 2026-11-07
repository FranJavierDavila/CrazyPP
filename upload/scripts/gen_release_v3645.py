#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 53 · GENERADOR DEL DIRECTORIO DE RELEASE v3645
======================================================================
Crea scripts/release-v3645/ a partir de scripts/release-v3644/ con:
  · reemplazos de versión (3.6.44-SDK6 → 3.6.45-SDK6 · v3644-sdk6 → v3645-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 47 — la bomba marca el
    paso por INTERVALOS de 15 s y llega el LADRILLO ELÉCTRICO con su
    atracción por anillos y la reacción en cadena, sustituido por
    MARCADORES, método ronda 26)
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26 (la mecánica vive en el núcleo y en el
    módulo de la locura con sus assets).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3645 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3644"
DEST = RAIZ / "scripts" / "release-v3645"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 46"
BLOQUE_FIN = ("los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 47 — LA BOMBA MARCA EL PASO Y LA PARED@NL@'
    'SE ELECTRIFICA — variación del ARKANOID 2, etapa 4 del campeonato de@NL@'
    'La Locura, a petición del dueño)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.44-SDK6):@NL@'
    '  · LA BOMBA MARCA EL PASO (cadencia nueva): «que salga de manera@NL@'
    '    aleatoria pero con intervalos de 15 segundos si tiene ladrillos@NL@'
    '    disponibles donde aparecer». La 1.ª aparición cae DENTRO del@NL@'
    '    primer intervalo (entre 2 y 12 s, aleatoria) y cada aparición@NL@'
    '    programa la siguiente a +15 s: tras una desaparición (sin@NL@'
    '    azules) vuelve en SU intervalo, nunca antes. Lo demás intacto:@NL@'
    '    4 s por ladrillo, salto entre azules, detonación 2×2, no vuelve@NL@'
    '    tras consumirse y se reinicia con cada partida.@NL@'
    '  · EL LADRILLO ELÉCTRICO (nuevo — los últimos 30 s): uno de los@NL@'
    '    ladrillos azules (aleatorio) se convierte en eléctrico con@NL@'
    '    PEQUEÑOS RAYOS que salen de él (14 rayos dentados aditivos que@NL@'
    '    crepitan a 14 Hz), material azul que EMITE cian, icono del rayo@NL@'
    '    (familia reloj/bomba) y ZAP de sellado + CHISPORROTEO eléctrico@NL@'
    '    constante (petición literal: «cuando sela un ladrillo y pasa a@NL@'
    '    eléctrico que emita un sonido de chisporroteo de electricidad»).@NL@'
    '    SÓLO es destruible con la BOLA: el rayo del láser ni siquiera lo@NL@'
    '    ve (atraviesa su hueco) — el golpe de la bola es SU gatillo.@NL@'
    '  · LA ATRACCIÓN: al darle con la bola, el eléctrico ATRAE hacia sí@NL@'
    '    al resto de los ladrillos que queden en la pared y los reparte@NL@'
    '    en las celdas pegadas a su alrededor por ANILLOS — cubriendo@NL@'
    '    todas las casillas más próximas posibles (anillo 1: 8 vecinos,@NL@'
    '    anillo 2: 16, …) con un viaje animado de 0,35 s por ladrillo.@NL@'
    '    TODOS quedan eléctricos, con el mismo efecto de rayitos.@NL@'
    '  · LA REACCIÓN EN CADENA: desde ese momento y hasta el final del@NL@'
    '    tiempo, CUALQUIER impacto en cualquier ladrillo eléctrico@NL@'
    '    desencadena una reacción en cadena RAMIFICADA (ondas de 0,12 s@NL@'
    '    en todas direcciones, zap eléctrico por ladrillo) que destruye@NL@'
    '    TODOS los ladrillos en cadena — finalizando de forma EXITOSA la@NL@'
    '    misión. El reloj se CONGELA durante el destrozo: el gran final@NL@'
    '    se completa siempre (nadie pierde a mitad de la cascada).@NL@'
    '  · MURO DE FÁBRICA: cada partida recuerda el color ORIGINAL de cada@NL@'
    '    ladrillo (state0) — láser, conversiones y eléctricos no dejan@NL@'
    '    rastro al reiniciar. Y la bomba NO sale mientras el final@NL@'
    '    eléctrico esté en marcha (el gran final manda).@NL@'
    '  · Capa AN nueva (qa_electrico_v3645): agujas del módulo + mecánica@NL@'
    '    headless REAL (siembra, inmunidad al láser, bomba bloqueada en el@NL@'
    '    final, atracción con anillo ≤ 2 y celdas únicas, cadena 12/12 con@NL@'
    '    misión superada vía _finish(true), muro de fábrica) · AM@NL@'
    '    re-anclada a la cadencia de 15 s · AF/AL intactas.@NL@'
    '  · Conserva TODO: la matriz de poderes (mega · efecto · imán ·@NL@'
    '    portal) con ciclo ⟷ sin envolver, el PODER ACTIVO SE VE EN LA@NL@'
    '    PALA (anillo de tiempo, FASE 42), la PARTIDA NUEVA = PALA LIMPIA@NL@'
    '    (hook del árbitro, FASE 41), la INMEDIATEZ del gatillo, el portal@NL@'
    '    EXPLÍCITO de 3 fases con la IA penalizada en % (r50) y sus 3@NL@'
    '    golpes garantizados (r51), el passthrough EN CALIENTE (r51), el@NL@'
    '    PRECALIENTE anti-lag al empezar la partida (r50), las voces@NL@'
    '    nativas y los iconos recortados, el menú de campeonatos v3.6.31,@NL@'
    '    el HALL OF FAME (FASE 29), el SALÓN DEL ARTISTA (FASE 30), la SALA@NL@'
    '    DEL PARTIDO y el MEJOR DE 3 (FASE 31), el HALL SIN PALA NI BOLA@NL@'
    '    (FASE 32), la coronación épica y la RUTA LEYENDA del Oeste, el@NL@'
    '    tren 100 % sonoro, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la@NL@'
    '    CCD SDF de contacto, el saque VR realista, PRO CIRCUITO, intro@NL@'
    '    oficial, física viva, palas con carácter, CRAZY TV en directo y@NL@'
    '    los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.44-SDK6", "V3.6.45-SDK6"),
    ("3.6.44-SDK6", "3.6.45-SDK6"),
    ("v3644-sdk6", "v3645-sdk6"),
    ("3.6.44", "3.6.45"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.45-SDK6", "frente a V3.6.44-SDK6"),
    ("tras probar V3.6.45", "tras probar V3.6.44"),
]


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    print(f"· copiado {ORIGEN.name} → {DEST.name}")

    for f in sorted(DEST.iterdir()):
        if f.suffix not in (".py", ".txt", ".json", ".mjs"):
            continue
        txt = f.read_text(encoding="utf-8")
        if f.name == "build_zip.py":
            # ── bloque de notas por marcadores ──
            i = txt.find(BLOQUE_INI)
            if i < 0:
                print("FALLO: marcador INI del bloque no encontrado")
                sys.exit(1)
            j = txt.find(BLOQUE_FIN, i)
            if j < 0:
                print("FALLO: marcador FIN del bloque no encontrado")
                sys.exit(1)
            j += len(BLOQUE_FIN)
            txt = txt[:i] + BLOQUE_NUEVO.replace("@NL@", BS_N) + txt[j:]
            print(f"  ✓ {f.name}: notas FASE 47 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
        for viejo, nuevo in GLOBALES:
            n = txt.count(viejo)
            if n:
                txt = txt.replace(viejo, nuevo)
                print(f"  ✓ {f.name}: {viejo} → {nuevo} (×{n})")
        if f.name == "build_zip.py":
            for viejo, nuevo in RESTAURA:
                n = txt.count(viejo)
                if n:
                    txt = txt.replace(viejo, nuevo)
                    print(f"  ✓ {f.name}: restaurado {nuevo!r} (×{n})")
        f.write_text(txt, encoding="utf-8")

    # guard anti-rollback de la estirpe v369-sdk5 (FASE 7)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    if "v369-sdk5" not in bz:
        print("FALLO: la estirpe v369-sdk5 desapareció del build_zip")
        sys.exit(1)
    print("· guard v369-sdk5 intacto")

    # el VERSION.txt del paquete lleva guard del SDK y de manifests: sin cambios
    if "1.5.4" not in bz or "v56" not in bz or "v26" not in bz:
        print("FALLO: guards SDK/oeste/locura alterados")
        sys.exit(1)
    print("· guards SDK 1.5.4 / oeste v56 / locura v26 intactos")
    print("RELEASE v3645 LISTA")


if __name__ == "__main__":
    main()
