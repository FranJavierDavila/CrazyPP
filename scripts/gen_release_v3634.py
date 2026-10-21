#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 42 · GENERADOR DEL DIRECTORIO DE RELEASE v3634
======================================================================
Crea scripts/release-v3634/ a partir de scripts/release-v3633/ con:
  · reemplazos de versión (3.6.33-SDK6 → 3.6.34-SDK6 · v3633-sdk6 → v3634-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 36 — MEGA PALA NORMATIVA
    DEL NÚCLEO: carga por rally de 11+ golpes · icono sobre el mango +
    jingle · gatillo voluntaria · conmutador «Pala Mejorada» en AJUSTES),
    sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4 y manifest del oeste
    v56 se CONSERVAN sin cambios (esta ronda no toca SDK ni módulos del
    oeste; la LOCURA sube a v26 — sus guards del build_zip se ajustan).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3634 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3633"
DEST = RAIZ / "scripts" / "release-v3634"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 35"
BLOQUE_FIN = ("    '    carácter, CRAZY TV en directo y los 5 campeonatos."
              + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 36 — MEGA PALA NORMATIVA DEL NÚCLEO:@NL@'
    'CARGA POR RALLY DE 11+ GOLPES · ICONO SOBRE EL MANGO + JINGLE ·@NL@'
    'GATILLO VOLUNTARIA · CONMUTADOR «PALA MEJORADA» EN AJUSTES)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.33-SDK6):@NL@'
    '  · FASE 36 (ronda 42, correcciones del dueño tras V3.6.33:@NL@'
    '    «eliminar el núcleo dorado… un pequeño icono sobre el mango,@NL@'
    '    por ejemplo un dibujo de la pala con una referencia a que se@NL@'
    '    hace grande… puede venir acompañado de un sonido característico@NL@'
    '    e identificable… se puede activar cuando un rally supera los@NL@'
    '    10 golpes… extensivo a todos los campeonatos y las plantillas»@NL@'
    '    + conmutador «Pala Mejorada» en opciones del menú principal).@NL@'
    '  · ADIÓS NÚCLEO DORADO: fuera el núcleo de la garganta, el halo,@NL@'
    '    el aro de carga y las chispas — NADA que viva dentro o sobre la@NL@'
    '    hoja. El indicador de carga es un ICONO pequeño (5,6 cm) sobre@NL@'
    '    el mango: sprite-billboard dibujado en canvas (pala dorada + 4@NL@'
    '    flechas de crecida) con pop y vaivén — el jugador sabe SI tiene@NL@'
    '    el poder y CUÁL es mirando el icono sobre el mando, sin que@NL@'
    '    estorbe durante el juego.@NL@'
    '  · SONIDO CARACTERÍSTICO de carga: jingle propio (tríada mayor@NL@'
    '    ascendente 523→659→784→1568 + brillo) DISTINTO del arpegio de@NL@'
    '    activación (420→860→1400 square) + háptica + megáfono «¡CRAZY@NL@'
    '    COMBO! ¡MEGA PALA CARGADA!» (pista «norma nueva» UNA vez).@NL@'
    '  · LA NORMA: un rally que SUPERA los 10 golpes (11+) CARGA la pala@NL@'
    '    — una carga por rally; sin gastar, se conserva. Nada de arrancar@NL@'
    '    cargado ni de recargas a tiempo (la recarga de 14 s desaparece).@NL@'
    '  · EN EL NÚCLEO (game.html): megaTrigger/_megaCharge/updateMega son@NL@'
    '    del juego base — TODOS los campeonatos (locura, magia, oeste,@NL@'
    '    estacion_orbital, valle_neon) y cualquier campeonato nuevo de la@NL@'
    '    plantilla heredan la mecánica sin escribir una línea (los@NL@'
    '    módulos corren sobre rules/paddleMounts del núcleo).@NL@'
    '  · LA LOCURA módulo v26: mega interna RETIRADA (-20 KB) — sin@NL@'
    '    estado, sin FX y sin megaTrigger propio; el CRAZY COMBO del@NL@'
    '    rally 6 deja de recargar (el Clown sigue poniéndose hungry:@NL@'
    '    solo sabor). PLANTILLA-GUIA 2.4 + regla de oro 6: prohibido a@NL@'
    '    los módulos tocar DIMS.hitAssistRadius, escalar paddleMounts o@NL@'
    '    definir megaTrigger.@NL@'
    '  · CONMUTADOR «PALA MEJORADA» en la página AJUSTES (ancho@NL@'
    '    completo, persistente pp_pala_mejorada_v1): activado PERMITE los@NL@'
    '    superpoderes; desactivado la pala se comporta NORMAL (recogida@NL@'
    '    inmediata con dispose). El gatillo en saque sigue SACANDO; con@NL@'
    '    carga y bola en juego LIBERA 8 s (canto de energía silueta@NL@'
    '    ×1,055 + pala ×1,30 + radio ×1,38 + onda de choque + power-up +@NL@'
    '    háptica); el HALL es zona neutra.@NL@'
    '  · Capa AC nueva (qa_mega_norma_v3634, en vivo): 80 checks —@NL@'
    '    agujas del núcleo/locura/manifest/plantilla servidos + mecánica@NL@'
    '    real headless (10 sin carga · 11 carga · icono sobre el mango ·@NL@'
    '    saque respetado · liberación · 2.º gatillo comido · agotamiento ·@NL@'
    '    una carga por rally · re-arma · conmutador por el menú con@NL@'
    '    persistencia · hall neutro). Capa AB retirada del listado.@NL@'
    '  · Conserva TODO: el menú de campeonatos v3.6.31 (texto fantasma@NL@'
    '    fuera · intro opcional · menú prioritario · haz-puntero), el HALL@NL@'
    '    SIN PALA NI BOLA (FASE 32), la SALA DEL PARTIDO y el MEJOR DE 3@NL@'
    '    (FASE 31), el SALÓN DEL ARTISTA (FASE 30), la coronación épica y@NL@'
    '    la RUTA LEYENDA del Oeste, el tren 100 % sonoro, el ESCUDO DE@NL@'
    '    PALA, el REACTOR DE IMPULSO, la CCD SDF de contacto, el saque VR@NL@'
    '    realista, PRO CIRCUITO, intro oficial, física viva, palas con@NL@'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.33-SDK6", "V3.6.34-SDK6"),
    ("3.6.33-SDK6", "3.6.34-SDK6"),
    ("v3633-sdk6", "v3634-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 36 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.33"' in txt:
                txt = txt.replace('grep -c "3.6.33"', 'grep -c "3.6.34"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.34")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.33" in txt:
                txt = txt.replace("menciones 3.6.33", "menciones 3.6.34")
                txt = txt.replace("n3633 = int", "n3634 = int").replace("{n3633}", "{n3634}").replace("if n3633 < 4", "if n3634 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.34")
            # el SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
            # ronda: sus guards se conservan tal cual (verificación abajo).
            # v3.6.34 (ronda 42): LA LOCURA sube a v26 (mega al núcleo) —
            # sus guards del build_zip se actualizan (lección ronda 41).
            if "'locura': (25," in txt:
                txt = txt.replace("'locura': (25,", "'locura': (26,")
                txt = txt.replace('locura v25', 'locura v26')
                print("  ✓ build_zip.py: guards del manifest de locura v25 → v26")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        if len(txt) != antes if False else False:
            pass
        f.write_text(txt, encoding="utf-8")

    # verificación de los guards que DEBEN seguir intactos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    ok = True
    if "SDK_VERSION = '1.5.4'" not in bz:
        print("FALLO: guard del SDK 1.5.4 perdido")
        ok = False
    if "('oeste': (56," not in bz and "'oeste': (56, (" not in bz:
        # patrón tolerante: el pin del oeste debe seguir en 56
        if "('oeste': (56," not in bz:
            print("FALLO: guard del manifest del oeste v56 perdido")
            ok = False
    if "'locura': (26," not in bz:
        print("FALLO: guard del manifest de locura v26 no aplicado")
        ok = False
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la estirpe histórica v369-sdk5 se ha visto afectada")
        ok = False
    if not ok:
        sys.exit(1)
    print("· guards intactos: SDK 1.5.4 · oeste v56 · locura v26 · estirpe v369-sdk5")
    print(f"\nSiguiente: build_zip → sella_r42 (tamaños reales) → QA TOTAL.")


if __name__ == "__main__":
    main()
