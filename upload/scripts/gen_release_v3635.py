#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 43 · GENERADOR DEL DIRECTORIO DE RELEASE v3635
======================================================================
Crea scripts/release-v3635/ a partir de scripts/release-v3634/ con:
  · reemplazos de versión (3.6.34-SDK6 → 3.6.35-SDK6 · v3634-sdk6 → v3635-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 37 — SUPERPODER DE PALA
    CARGAS ×3: cada 11 golpes del rally = +1 carga (tope ×3, distinto
    sustituye) · icono DEL DUEÑO anclado al mango con etiqueta ×N · voz
    animosa TTS embebida · gatillo del mando LIBRE),
    sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4, manifest del oeste v56
    y manifest de la locura v26 se CONSERVAN sin cambios (esta ronda no
    toca SDK ni módulos de campeonato; la mecánica vive en el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3635 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3634"
DEST = RAIZ / "scripts" / "release-v3635"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 36"
BLOQUE_FIN = ("    '    carácter, CRAZY TV en directo y los 5 campeonatos."
              + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 37 — SUPERPODER DE PALA · CARGAS ×3:@NL@'
    'CADA 11 GOLPES DEL RALLY = +1 CARGA (TOPE ×3) · ICONO DEL DUEÑO@NL@'
    'ANCLADO AL MANGO CON ETIQUETA ×N · VOZ ANIMOSA TTS EMBEBIDA ·@NL@'
    'GATILLO DEL MANDO LIBRE)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.34-SDK6):@NL@'
    '  · FASE 37 (ronda 43, diseño aprobado por el dueño sobre la norma@NL@'
    '    de FASE 36: «los superpoderes de pala se obtienen cada 11 golpes@NL@'
    '    por norma… si jugando te vuelve a salir el mismo superpoder te@NL@'
    '    ponga al lado del icono un +2… si lo usas descuentas 1… cuando se@NL@'
    '    consigue un superpoder una voz muy animosa lo comunique… usa como@NL@'
    '    icono el que te adjunto… anclado al mango de la pala… ligeramente@NL@'
    '    por encima del mando de la pala en su base»).@NL@'
    '  · CARGAS ×3: CADA 11 golpes del rally (11, 22, 33…) = +1 carga —@NL@'
    '    el rally largo premia con más cargas (la resistencia se premia@NL@'
    '    sola, sin niveles). MISMO poder → acumula ×2/×3 (tope 3: con la@NL@'
    '    mano llena, «toc» honesto y nada); PODER DISTINTO → sustituye@NL@'
    '    (cargas a 1). Las cargas viven SOLO en la partida en curso.@NL@'
    '  · ICONO DEL DUEÑO (SuperPala_Crece.png — tres palas que crecen)@NL@'
    '    EMBEBIDO como data-URI y ANCLADO AL MANGO (4,8 cm, base de la@NL@'
    '    mano, justo sobre el mando: «forma parte de la pala y no@NL@'
    '    distrae»), con ETIQUETA ×N roja al acumular. Si el PNG faltara,@NL@'
    '    cae al dibujo canvas dorado de V3.6.34 (respaldo).@NL@'
    '  · VOZ ANIMOSA: «¡Potenciador de pala gigante!» (TTS pre-generado,@NL@'
    '    MP3 embebido data-URI — cero latencia, cero red, offline en el@NL@'
    '    Quest) + jingle propio de carga + háptica. Megáfono ES/EN con@NL@'
    '    ×N («¡POTENCIADOR DE PALA GIGANTE! ×2»).@NL@'
    '  · GATILLO DEL MANDO LIBRE (el que NO tiene la pala — conmuta solo@NL@'
    '    al cambiar de mano) suelta una carga: 15 s de MEGA PALA (canto@NL@'
    '    de energía silueta ×1,055 + pala ×1,30 + radio ×1,38 + onda de@NL@'
    '    choque + power-up + háptica). ACTIVA + gatillo con cargas =@NL@'
    '    ALARGA +15 s por carga (el tamaño NUNCA se apila). En saque el@NL@'
    '    gatillo sigue SACANDO; si el campeonato ocupa la mano libre@NL@'
    '    (pistola del Oeste armada), el gatillo de la pala queda de@NL@'
    '    respaldo. HALL = zona neutra.@NL@'
    '  · REGISTRO EXTENSIBLE PODERES_PALA en el núcleo: añadir un poder@NL@'
    '    nuevo = una entrada (id + nombre i18n + voz) — el reparto@NL@'
    '    aleatorio lo incluye solo. TODOS los campeonatos (locura, magia,@NL@'
    '    oeste, estacion_orbital, valle_neon) y cualquier campeonato nuevo@NL@'
    '    de la plantilla heredan el sistema sin escribir una línea.@NL@'
    '    PLANTILLA-GUIA 2.4 reescrita con la norma ×3.@NL@'
    '  · CONMUTADOR «PALA MEJORADA» en AJUSTES (pp_pala_mejorada_v1):@NL@'
    '    activado PERMITE los superpoderes; desactivado la pala se@NL@'
    '    comporta NORMAL (recogida inmediata con dispose, mano vacía).@NL@'
    '  · Capa AD nueva (qa_mega_cargas_v3635, en vivo): 92 checks —@NL@'
    '    agujas del núcleo/locura/manifest/plantilla servidos + mecánica@NL@'
    '    real headless (10 sin carga · 11 ×1 · 22 ×2 · 33 ×3 · 44 tope ·@NL@'
    '    gatillo libre libera 15 s · alarga +15 s · agotamiento · icono@NL@'
    '    anclado · PNG decodificado · rally nuevo resetea · conmutador@NL@'
    '    por el menú con persistencia · hall neutro). Capa AC retirada@NL@'
    '    del listado (historial conservado).@NL@'
    '  · Conserva TODO: el menú de campeonatos v3.6.31 (texto fantasma@NL@'
    '    fuera · intro opcional · menú prioritario · haz-puntero), el HALL@NL@'
    '    SIN PALA NI BOLA (FASE 32), la SALA DEL PARTIDO y el MEJOR DE 3@NL@'
    '    (FASE 31), el SALÓN DEL ARTISTA (FASE 30), la coronación épica y@NL@'
    '    la RUTA LEYENDA del Oeste, el tren 100 % sonoro, el ESCUDO DE@NL@'
    '    PALA, el REACTOR DE IMPULSO, la CCD SDF de contacto, el saque VR@NL@'
    '    realista, PRO CIRCUITO, intro oficial, física viva, palas con@NL@'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.34-SDK6", "V3.6.35-SDK6"),
    ("3.6.34-SDK6", "3.6.35-SDK6"),
    ("v3634-sdk6", "v3635-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 37 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.34"' in txt:
                txt = txt.replace('grep -c "3.6.34"', 'grep -c "3.6.35"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.35")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.34" in txt:
                txt = txt.replace("menciones 3.6.34", "menciones 3.6.35")
                txt = txt.replace("n3634 = int", "n3635 = int").replace("{n3634}", "{n3635}").replace("if n3634 < 4", "if n3635 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.35")
            # el SDK (1.5.4), el oeste (v56) y la locura (v26) NO cambian
            # esta ronda: sus guards se conservan tal cual (verificación abajo).
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        f.write_text(txt, encoding="utf-8")

    # verificación de los guards que DEBEN seguir intactos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    ok = True
    if "SDK_VERSION = '1.5.4'" not in bz:
        print("FALLO: guard del SDK 1.5.4 perdido")
        ok = False
    if "('oeste': (56," not in bz and "'oeste': (56, (" not in bz:
        print("FALLO: guard del manifest del oeste v56 perdido")
        ok = False
    if "'locura': (26," not in bz:
        print("FALLO: guard del manifest de locura v26 perdido")
        ok = False
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la estirpe histórica v369-sdk5 se ha visto afectada")
        ok = False
    if not ok:
        sys.exit(1)
    print("· guards intactos: SDK 1.5.4 · oeste v56 · locura v26 · estirpe v369-sdk5")
    print(f"\nSiguiente: build_zip → sella_r43 (tamaños reales) → QA TOTAL.")


if __name__ == "__main__":
    main()
