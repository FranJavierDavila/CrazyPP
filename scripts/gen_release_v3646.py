#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 54 · GENERADOR DEL DIRECTORIO DE RELEASE v3646
======================================================================
Crea scripts/release-v3646/ a partir de scripts/release-v3645/ con:
  · reemplazos de versión (3.6.45-SDK6 → 3.6.46-SDK6 · v3645-sdk6 → v3646-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 48 — el SÚPER EFECTO es
    SPIN REAL (topspin/backspin/sidespin según el barrido de la pala, con
    su bote firma), el SÚPER IMÁN es un GANCHO al centro de la pala con
    PALA METÁLICA −80 %, y la pala del rival JAMÁS atraviesa la mesa),
    sustituido por MARCADORES, método ronda 26.
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3646 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3645"
DEST = RAIZ / "scripts" / "release-v3646"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 47"
BLOQUE_FIN = ("los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 48 — EL EFECTO ES SPIN REAL Y EL IMÁN,@NL@'
    'UN GANCHO METÁLICO — redefinición de los dos superpoderes de pala y@NL@'
    'arreglo del palo del rival en la mesa, a petición del dueño)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.45-SDK6):@NL@'
    '  · SÚPER EFECTO = SPIN REAL (la estela desfasada se RETIRA): el@NL@'
    '    movimiento de la pala AL GOLPEAR clasifica el giro — barrido de@NL@'
    '    abajo hacia arriba = TOPSPIN (liftado), de arriba hacia abajo =@NL@'
    '    BACKSPIN (cortado), lateral = SIDESPIN — y el BOTE traduce cada@NL@'
    '    uno con su firma exacta: topspin sale MUY ACELERADA hacia@NL@'
    '    delante del bote (×1,55 y bajo), backspin prácticamente SE QUEDA@NL@'
    '    PARADA (×0,16 con saltito mínimo) y sidespin EXAGERA el bote@NL@'
    '    hacia el lado del barrido (patada 0,42 × la velocidad de vuelo).@NL@'
    '    Golpe recto sin barrido claro = comportamiento de siempre (bote@NL@'
    '    acoplado ×2,4). El rival ya sufre la bola marcada (error ×2 y@NL@'
    '    piernas ×0,85 — la penalización en % del dueño, viva desde r51).@NL@'
    '  · SEÑAL VISUAL POR TIPO: el halo de la bola marcada y el anillo del@NL@'
    '    bote se TIÑEN con el spin (naranja = topspin, cian = backspin,@NL@'
    '    verde = sidespin, rojo = sin tipo) y el barrido sonoro firma cada@NL@'
    '    bote tipificado. La IA limpia tipo y lado al devolver (marca@NL@'
    '    completa, sin rastros entre rallies).@NL@'
    '  · SÚPER IMÁN = GANCHO al CENTRO de la pala: «la bola se redirige@NL@'
    '    automáticamente al centro de nuestra pala en su movimiento como@NL@'
    '    atraída por la pala para que podamos dar un buen golpe, ojo@NL@'
    '    siempre que venga en nuestra dirección de golpeo». Fuera el campo@NL@'
    '    suave y el rescate: cualquier bola que VENGA hacia nosotros (v.z@NL@'
    '    > 0,2) dentro del radio del gancho (1,8 m) es arrastrada al@NL@'
    '    CENTRO VIVO de la pala (26 m/s², tope Δv 3,2 m/s por aproximación@NL@'
    '    — nunca teleporta: la salida la calcula el contacto de siempre,@NL@'
    '    golden intacto). Solo la pala del jugador gana asistencia.@NL@'
    '  · PALA METÁLICA (visual limpia): FUERA flechas, disco de campo y@NL@'
    '    canto azul — la señal del imán es la PALA OSCURECIDA al 80 % de@NL@'
    '    su color mientras dura el efecto (metalness alto: simula un@NL@'
    '    imán). Materiales AISLADOS por clon propio (la pala del rival y@NL@'
    '    la del demo jamás se tiñen) y restauración EXACTA al apagarse,@NL@'
    '    con cambio de mano a mitad de ventana incluido.@NL@'
    '  · EL RIVAL JAMÁS ATRAVIESA LA MESA: el clamp anti-clipping subestimaba@NL@'
    '    el mango (solo contaba su radio, no su media longitud bajo el@NL@'
    '    agarre) — ahora la pala completa (hoja + palo hasta la punta) se@NL@'
    '    levanta por encima de la losa, y la puerta de la mesa incluye@NL@'
    '    también al punto de agarre (hoja fuera del borde con el mango@NL@'
    '    colgando también cuenta). La mano bajo la mesa sigue libre.@NL@'
    '  · PRECALIENTE a 13 piezas (fuera campo/flechas/estela) · capas AF/@NL@'
    '    AG/AL/AM re-ancladas a la nueva spec (con NEGATIVAS: las piezas@NL@'
    '    retiradas NO pueden volver) · capa AO nueva (qa_spin_pala_v3646,@NL@'
    '    58 checks): clasificación headless real, los tres botes con su@NL@'
    '    firma, convergencia del gancho con negativas, oscurecido −80 %@NL@'
    '    con aislamiento y restauración exacta, y clamp del mango.@NL@'
    '    Golden de física INTACTO (11/11).@NL@'
    '  · Conserva TODO: la bomba por intervalos de 15 s y el ladrillo@NL@'
    '    eléctrico con su cadena (FASE 47), la matriz de poderes (mega ·@NL@'
    '    efecto · imán · portal) con ciclo ⟷ sin envolver, el PODER ACTIVO@NL@'
    '    SE VE EN LA PALA (anillo de tiempo, FASE 42), la PARTIDA NUEVA =@NL@'
    '    PALA LIMPIA, la INMEDIATEZ del gatillo, el portal EXPLÍCITO de 3@NL@'
    '    fases con la IA penalizada en % y sus 3 golpes garantizados, el@NL@'
    '    passthrough EN CALIENTE, las voces nativas y los iconos, el menú@NL@'
    '    de campeonatos v3.6.31, el HALL OF FAME (FASE 29), el SALÓN DEL@NL@'
    '    ARTISTA (FASE 30), la SALA DEL PARTIDO y el MEJOR DE 3 (FASE 31),@NL@'
    '    la coronación épica y la RUTA LEYENDA del Oeste, el tren 100 %@NL@'
    '    sonoro, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD SDF de@NL@'
    '    contacto, el saque VR realista, PRO CIRCUITO, intro oficial,@NL@'
    '    física viva, palas con carácter, CRAZY TV en directo y los 5@NL@'
    '    campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.45-SDK6", "V3.6.46-SDK6"),
    ("3.6.45-SDK6", "3.6.46-SDK6"),
    ("v3645-sdk6", "v3646-sdk6"),
    ("3.6.45", "3.6.46"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.46-SDK6", "frente a V3.6.45-SDK6"),
    ("tras probar V3.6.46", "tras probar V3.6.45"),
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
            print(f"  ✓ {f.name}: notas FASE 48 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3646 LISTA")


if __name__ == "__main__":
    main()
