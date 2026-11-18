#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 57 · GENERADOR DEL DIRECTORIO DE RELEASE v3649
======================================================================
Crea scripts/release-v3649/ a partir de scripts/release-v3648/ con:
  · reemplazos de versión (3.6.48-SDK6 → 3.6.49-SDK6 · v3648-sdk6 → v3649-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 51 — EL IMÁN APUNTA, EL EFECTO OBEDECE:
    20 TOQUES Y 10 SEGUNDOS, la norma íntegra del dueño: concesión sólo
    pasados los 20 toques, Súper Efecto y Súper Imán con ventanas de 10 s
    puramente temporales, el imán FRENA la bola y nunca arma sobre el
    saque del rival),
    sustituido por MARCADORES, método ronda 26.
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3649 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3648"
DEST = RAIZ / "scripts" / "release-v3649"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 50"
BLOQUE_FIN = ("los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 51 — EL IMÁN APUNTA, EL EFECTO@NL@'
    'OBEDECE — revisión del dueño tras V3.6.48)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.48-SDK6):@NL@'
    '  · BUG DEL EFECTO (informe del dueño: «persiste más allá del@NL@'
    '    tiempo indicado y favorece también en los botes al rival»):@NL@'
    '    la LEY DE LOS 10 s es ABSOLUTA — a los 10 s mueren TODAS las@NL@'
    '    marcas de la bola (ppEfecto/tipo/lado) incluso en pleno vuelo,@NL@'
    '    con red de seguridad por frame; todo golpe honesto (eMul=1,@NL@'
    '    incluidos los saques) mata cualquier marca vieja que la bola@NL@'
    '    arrastrara. Y se RETIRA el acople ×2,4 del bote sin tipo (r51):@NL@'
    '    un bote amplificado dependía del giro real y podía salir@NL@'
    '    «amable» y BENEFICIAR AL RIVAL — la ventaja del efecto en los@NL@'
    '    botes es hoy SÓLO la firma tipificada (top acelera y achica,@NL@'
    '    back mata el ritmo en su campo, side patada lateral a@NL@'
    '    perseguir): el perjudicado SIEMPRE el rival.@NL@@NL@'
    '  · SÚPER IMÁN REESCRITO (el dueño: «olvidemos el efecto anterior@NL@'
    '    de atracción y ralentización»): GUÍA DE TIRO — cada golpe del@NL@'
    '    jugador con la ventana viva y dirección hacia la mitad rival@NL@'
    '    sale con el SOLVER DE LA CASA (computeShotVelocityReal, el@NL@'
    '    mismo de la IA, con arrastre real y despeje de red garantizado)@NL@'
    '    y BOTA SIEMPRE en la mesa del rival (objetivo 62 % de la media@NL@'
    '    mesa, dirección errónea = corregida dentro), reforzado ×1,2@NL@'
    '    con piso de 9,5 m/s y tope honesto 0,8×max: golpes muy fuertes@NL@'
    '    y a gran velocidad con bote correcto asegurado. El gancho y el@NL@'
    '    freno de r54-r56 quedan RETIRADOS (sin campo por subpaso, sin@NL@'
    '    gasto de cargas por asistencia — la ventana vive SUS 10 s). El@NL@'
    '    saque propio y los tiros hacia atrás son juego normal; el@NL@'
    '    golpe guiado se SIENTE (zap + háptica extra).@NL@@NL@'
    '  · NORMA DE EMOCIONES DEL RIVAL (regla del dueño, REGLA en TODOS@NL@'
    '    los campeonatos): espera/principio → _idle · superpoder del@NL@'
    '    rival → _crazy · rival pierde punto → _angry + queja · jugador@NL@'
    '    falla → _laughing + risas burlonas y luego _victory · 5 toques@NL@'
    '    → _focused · 10 → _picando · 15 → _surprised · 20 → _panic ·@NL@'
    '    a partir de 20 pool aleatorio _loosing/_surprised/_panic cada@NL@'
    '    5 toques · pierde el partido → _defeated (persistente). El@NL@'
    '    núcleo reparte (rivalEmocion) y los 6 módulos visten SU arte@NL@'
    '    (convención <estado>.webp) y SUS sonidos; las reacciones@NL@'
    '    locales de punto quedan SUSTITUIDAS por la norma.@NL@@NL@'
    '  · IMÁGENES NUEVAS del dueño: pared IZQUIERDA y SUELO del Hall@NL@'
    '    (izquierda.jpg / suelo.jpg) y SUELO DE PISTA para el partido y@NL@'
    '    el entrenamiento (suelo_pista.jpg → assets/partido/suelo.jpg).@NL@@NL@'
    '  · VERIFICACIÓN: capa AR nueva (qa_norma_rival_v3649) + AF@NL@'
    '    REESCRITA para la guía (44 checks con física viva: tres tiros@NL@'
    '    mal aimados botan EN la mesa rival, saque y tiros atrás limpios)@NL@'
    '    + AO/AP/AQ/AG/AH/AI re-ancladas a la r57 · golden de física@NL@'
    '    INTACTO (la guía vive en el golpe, no en el paso físico).@NL@@NL@'
    '  · Conserva TODO: la norma de 20 toques, las ventanas de 10 s, el@NL@'
    '    spin real por barrido con su firma SÓLO en la mesa del rival,@NL@'
    '    la pala honesta fuera del rally, la PALA METÁLICA −80 %, el@NL@'
    '    clamp del mango del rival, la bomba por intervalos y el@NL@'
    '    ladrillo eléctrico con su cadena, el portal EXPLÍCITO con la@NL@'
    '    IA penalizada, la matriz con ciclo ⟷, las voces nativas, el@NL@'
    '    passthrough EN CALIENTE, el HALL OF FAME, el SALÓN DEL@NL@'
    '    ARTISTA, la SALA DEL PARTIDO, PRO CIRCUITO, el ESCUDO DE PALA,@NL@'
    '    el REACTOR DE IMPULSO, la CCD SDF, el saque VR realista, CRAZY@NL@'
    '    TV en directo y los 5 campeonatos.@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.48-SDK6", "V3.6.49-SDK6"),
    ("3.6.48-SDK6", "3.6.49-SDK6"),
    ("v3648-sdk6", "v3649-sdk6"),
    ("3.6.48", "3.6.49"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.49-SDK6", "frente a V3.6.48-SDK6"),
    ("tras probar V3.6.49", "tras probar V3.6.48"),
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
            print(f"  ✓ {f.name}: notas FASE 51 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3649 LISTA")


if __name__ == "__main__":
    main()
