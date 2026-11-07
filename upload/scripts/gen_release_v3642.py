#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 50 · GENERADOR DEL DIRECTORIO DE RELEASE v3642
======================================================================
Crea scripts/release-v3642/ a partir de scripts/release-v3641/ con:
  · reemplazos de versión (3.6.41-SDK6 → 3.6.42-SDK6 · v3641-sdk6 → v3642-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 44 — el portal SE ENTIENDE
    y la IA RESPONDE, sustituido por MARCADORES, método ronda 26)
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26 (la mecánica vive en el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3642 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3641"
DEST = RAIZ / "scripts" / "release-v3642"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 43"
BLOQUE_FIN = ("CRAZY TV en directo y los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 44 — EL PORTAL SE ENTIENDE Y LA IA@NL@'
    'RESPONDE — informe del dueño tras probar V3.6.41 en el Quest 3,@NL@'
    'corregido pieza a pieza)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.41-SDK6):@NL@'
    '  · CRÍTICO — «he sacado y no las devuelve»: la penalización de la@NL@'
    '    IA vuelve a ser un PORCENTAJE y jamás una anulación. Causa raíz:@NL@'
    '    la predicción de la IA moría CADA FRAME con la marca del portal@NL@'
    '    viva. FIX: flanco ÚNICO (muere una vez al cruzar el portal y la@NL@'
    '    IA reacciona tras su intervalo natural). Las desventajas mueren@NL@'
    '    CON el poder (fin de ventana y fin de punto = IA 100 % normal).@NL@'
    '  · EL PORTAL SE ENTIENDE (presentación EXPLÍCITA del dueño): al@NL@'
    '    golpear se abre el portal de ENTRADA en la zona de impacto (el@NL@'
    '    arte portals.png del dueño — el del rival wizard — al 50 % de su@NL@'
    '    tamaño real) con su halo creciente; la bola se hunde en su centro@NL@'
    '    y viaja OCULTA 1 SEGUNDO (física congelada: ni un evento, ni una@NL@'
    '    colisión fantasma, UNA identidad); al segundo el MISMO portal se@NL@'
    '    abre SOBRE la mesa del rival y la bola SALE DISPARADA por su@NL@'
    '    centro con trayectoria del solver (bote jugable: el rival SIEMPRE@NL@'
    '    puede intentarlo). El tránsito se CUMPLE aunque el poder expire.@NL@'
    '  · ICONO RECORTADO: el PNG del dueño vuelve a llevar TRANSPARENCIA@NL@'
    '    (r49 lo embebió en RGB con el alfa destruido) y recorte al@NL@'
    '    contenido, como los demás poderes.@NL@'
    '  · VOZ EN CASTELLANO: la ES de r49 estaba corrupta (2,78 s) — nueva@NL@'
    '    voz nativa Piper es_ES-davefx (0,82 s) verificada por ASR, con su@NL@'
    '    EN (lessac) correspondiente.@NL@'
    '  · ANTI-LAG TOTAL: «una congelación de la imagen realmente molesta»@NL@'
    '    — el precaliente arranca AL EMPEZAR LA PARTIDA (13 piezas: 4@NL@'
    '    cantos + halo + anillo de bote + flechas + imagen del portal +@NL@'
    '    icono + 4 voces del idioma vivo). La carga y el gatillo ya no@NL@'
    '    construyen ni decodifican NADA: solo encienden.@NL@'
    '  · PASSTHROUGH EN AJUSTES (petición del dueño): conmutador de tu@NL@'
    '    habitación real DENTRO de la sesión, por defecto DESACTIVADO,@NL@'
    '    con cambio de modo en vivo (fin de sesión + re-entrada automática@NL@'
    '    al modo contrario) y preferencia persistente — coherente con el@NL@'
    '    enlace de la portada web.@NL@'
    '  · Capa AK nueva (qa_portal_v3642, 88 checks en vivo): agujas de las@NL@'
    '    6 correcciones + mecánica real headless (tránsito de 3 fases,@NL@'
    '    salida por el centro del portal B, IA que VUELVE a predecir,@NL@'
    '    marca muere con ventana/punto, recogida con la bola EN VIAJE) +@NL@'
    '    verificación PIL del PNG (recorte + alfa) y de las voces. Capas@NL@'
    '    AG/AH re-ancladas al precaliente de 13 piezas al empezar.@NL@'
    '  · Conserva TODO: la matriz de poderes (mega · efecto · imán ·@NL@'
    '    portal) con ciclo ⟷ sin envolver, el PODER ACTIVO SE VE EN LA@NL@'
    '    PALA (anillo de tiempo, FASE 42), la PARTIDA NUEVA = PALA LIMPIA@NL@'
    '    (hook del árbitro, FASE 41), la INMEDIATEZ del gatillo, el halo@NL@'
    '    rojo HIJO de la bola, las flechas EN EL PLANO del icono, SÚPER@NL@'
    '    EFECTO notorio (rival castigado ×2/×0,85), SÚPER IMÁN con la spec@NL@'
    '    completa del dueño, voces nativas e iconos embebidos, el menú de@NL@'
    '    campeonatos v3.6.31, el HALL OF FAME (FASE 29), el SALÓN DEL@NL@'
    '    ARTISTA (FASE 30), la SALA DEL PARTIDO y el MEJOR DE 3 (FASE 31),@NL@'
    '    el HALL SIN PALA NI BOLA (FASE 32), la coronación épica y la RUTA@NL@'
    '    LEYENDA del Oeste, el tren 100 % sonoro, el ESCUDO DE PALA, el@NL@'
    '    REACTOR DE IMPULSO, la CCD SDF de contacto, el saque VR realista,@NL@'
    '    PRO CIRCUITO, intro oficial, física viva, palas con carácter,@NL@'
    '    CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.41-SDK6", "V3.6.42-SDK6"),
    ("3.6.41-SDK6", "3.6.42-SDK6"),
    ("v3641-sdk6", "v3642-sdk6"),
    ("3.6.41", "3.6.42"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.42-SDK6", "frente a V3.6.41-SDK6"),
    ("tras probar V3.6.42", "tras probar V3.6.41"),
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
            print(f"  ✓ {f.name}: notas FASE 44 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3642 LISTA")


if __name__ == "__main__":
    main()
