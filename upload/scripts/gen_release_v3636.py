#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 44 · GENERADOR DEL DIRECTORIO DE RELEASE v3636
======================================================================
Crea scripts/release-v3636/ a partir de scripts/release-v3635/ con:
  · reemplazos de versión (3.6.35-SDK6 → 3.6.36-SDK6 · v3635-sdk6 → v3636-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 38 — SUPERPODER DE PALA
    MATRIZ + SÚPER EFECTO: poder distinto ENTRA en la matriz · joystick ⟷
    con flechas ‹ › sin envolver · SOLO campeonatos · SÚPER EFECTO 8 s /
    5 golpes con spin ×2 y tope · voces NATIVAS castellanas/inglesas),
    sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4, manifest del oeste v56
    y manifest de la locura v26 se CONSERVAN sin cambios (esta ronda no
    toca SDK ni módulos de campeonato; la mecánica vive en el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3636 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3635"
DEST = RAIZ / "scripts" / "release-v3636"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 37"
BLOQUE_FIN = ("    '    carácter, CRAZY TV en directo y los 5 campeonatos."
              + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 38 — SUPERPODER DE PALA · MATRIZ +@NL@'
    'SÚPER EFECTO: PODER DISTINTO ENTRA EN LA MATRIZ (NO SUSTITUYE) ·@NL@'
    'JOYSTICK ⟷ CICLA EL SELECCIONADO CON FLECHAS ‹ › SIN ENVOLVER ·@NL@'
    'SOLO EN CAMPEONATOS · SÚPER EFECTO: 8 S O 5 GOLPES, SPIN GENERADO@NL@'
    '×2 CON TOPE · VOCES NATIVAS CASTELLANAS + INGLÉS EMBEBIDAS)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.35-SDK6):@NL@'
    '  · FASE 38 (ronda 44, diseño del dueño sobre la norma ×3): «en@NL@'
    '    caso de salir un potenciador distinto que NO elimine los@NL@'
    '    actuales… una flecha al lado del icono… con el joystick del@NL@'
    '    mando lo podemos seleccionar dando a derecha o izquierda como@NL@'
    '    si de una matriz de potenciadores cargados… en todo momento@NL@'
    '    solo tenemos 1 visible en la pala… si estamos en el potenciador@NL@'
    '    0 no aparece flecha a la izquierda… si hemos cogido 2 y estamos@NL@'
    '    en el índice 1 no aparecerá flecha para la derecha».@NL@'
    '  · MATRIZ DE PODERES: un poder distinto ENTRA en la matriz (orden@NL@'
    '    de llegada; NUNCA sustituye); mismo poder → acumula ×2/×3 (tope@NL@'
    '    3, intacto). Joystick ⟷ de CUALQUIER mando cicla el seleccionado@NL@'
    '    (en escritorio, ←/→), con flanco + antirrebote y SIN envolver en@NL@'
    '    los bordes: flechas ‹ › en el icono SOLO cuando hay vecino —@NL@'
    '    exactamente donde el stick no puede pasar. SOLO UN icono visible@NL@'
    '    en la pala en todo momento (el seleccionado; oculto mientras SU@NL@'
    '    efecto está activo). El gatillo gasta el SELECCIONADO; al quedar@NL@'
    '    a 0 cargas la entrada SALE de la matriz y el índice se clampea.@NL@'
    '  · NUEVO PODER «SÚPER EFECTO» (4 reglas del dueño): (1) el jugador@NL@'
    '    GENERA el efecto — spin del brush real del golpe; (2) ×2 al spin@NL@'
    '    GENERADO (nunca al acumulado) con TOPE de seguridad 2×spinMax;@NL@'
    '    (3) el BOTE exagera el efecto SOLO en la bola marcada — Magnus@NL@'
    '    ×1,5 en vuelo y acople de bote ×1,8 (topspin patea más hacia@NL@'
    '    delante, sidespin desvía más, backspin frena más) — con el tope@NL@'
    '    de Coulomb como seguro: el rival hábil PUEDE contrarrestarlo;@NL@'
    '    (4) ventana de 8 SEGUNDOS O 5 GOLPES con efecto, lo que ocurra@NL@'
    '    primero (activo + gatillo = recarga). Golpe sin efecto@NL@'
    '    significativo: ni cuenta ni bonifica. La predicción de la IA y@NL@'
    '    el solver del saque siguen con la física canónica (la marca no@NL@'
    '    existe para ellos). Golden de física determinista INTACTO.@NL@'
    '  · SOLO EN CAMPEONATOS (petición del dueño): los potenciadores NO@NL@'
    '    aparecen en un partido contra la máquina fuera de la Modalidad@NL@'
    '    Campeonato — gate champs.active en megaEnabled(). HALL y@NL@'
    '    calibración siguen siendo zona neutra.@NL@'
    '  · VOCES NATIVAS (petición del dueño: «la voz que anuncia el poder@NL@'
    '    es horrible, no es voz nativa castellana»): fuera la voz tongtong@NL@'
    '    — ahora Piper es_ES-davefx (LA MISMA voz castellana de la@NL@'
    '    megafonía del juego): «¡Potenciador de pala gigante!» y@NL@'
    '    «¡Potenciador de súper efecto!»; jugando en inglés, el banco@NL@'
    '    en_US-lessac con el audio traducido («Giant paddle booster!» /@NL@'
    '    «Super spin booster!»). 4 MP3 embebidos data-URI, selección por@NL@'
    '    __ppLang, decode+caché (cero red, offline en el Quest).@NL@'
    '  · Icono del poder EFECTO: provisional de la casa (insignia azul@NL@'
    '    con bola y flechas de giro cian, misma familia que el Crece del@NL@'
    '    dueño) — el PNG definitivo del dueño se sustituye en un minuto@NL@'
    '    cuando lo adjunte (scripts/_poder36_insertar_assets.py).@NL@'
    '  · REGISTRO EXTENSIBLE PODERES_PALA: entrada con voz ES + voz EN +@NL@'
    '    PNG — la matriz, el ciclo y el reparto aleatorio lo incluyen@NL@'
    '    solo. TODOS los campeonatos y la plantilla heredan la norma@NL@'
    '    (PLANTILLA-GUIA 2.4 reescrita: matriz + solo-campeonatos +@NL@'
    '    súper efecto). Conmutador «Pala Mejorada» sigue siendo la llave.@NL@'
    '  · Capa AE nueva (qa_poderes_matriz_v3636, en vivo): 106 checks —@NL@'
    '    agujas de matriz/ciclo/efecto/voces/física marcada + mecánica@NL@'
    '    real headless (fuera de campeonato NO carga · 11 carga · 22/33@NL@'
    '    acumula · 44 tope · matriz [mega ×3, efecto ×1] · ciclo sin@NL@'
    '    envolver · ventana 8 s/5 golpes · recarga · FX cian · alarga ·@NL@'
    '    5.º golpe cierra · conmutador · hall · 4 voces · 2 PNG). Capa AD@NL@'
    '    retirada del listado (historial conservado).@NL@'
    '  · Conserva TODO: el menú de campeonatos v3.6.31 (texto fantasma@NL@'
    '    fuera · intro opcional · menú prioritario · haz-puntero), el HALL@NL@'
    '    SIN PALA NI BOLA (FASE 32), la SALA DEL PARTIDO y el MEJOR DE 3@NL@'
    '    (FASE 31), el SALÓN DEL ARTISTA (FASE 30), la coronación épica y@NL@'
    '    la RUTA LEYENDA del Oeste, el tren 100 % sonoro, el ESCUDO DE@NL@'
    '    PALA, el REACTOR DE IMPULSO, la CCD SDF de contacto, el saque VR@NL@'
    '    realista, PRO CIRCUITO, intro oficial, física viva, palas con@NL@'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.35-SDK6", "V3.6.36-SDK6"),
    ("3.6.35-SDK6", "3.6.36-SDK6"),
    ("v3635-sdk6", "v3636-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 38 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.35"' in txt:
                txt = txt.replace('grep -c "3.6.35"', 'grep -c "3.6.36"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.36")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.35" in txt:
                txt = txt.replace("menciones 3.6.35", "menciones 3.6.36")
                txt = txt.replace("n3635 = int", "n3636 = int").replace("{n3635}", "{n3636}").replace("if n3635 < 4", "if n3636 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.36")
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
    print(f"\nSiguiente: build_zip → sella_r44 (tamaños reales) → QA TOTAL.")


if __name__ == "__main__":
    main()
