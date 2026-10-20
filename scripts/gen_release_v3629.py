#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 37 · GENERADOR DEL DIRECTORIO DE RELEASE v3629
======================================================================
Crea scripts/release-v3629/ a partir de scripts/release-v3628/ con:
  · reemplazos de versión (3.6.28-SDK6 → 3.6.29-SDK6 · v3628-sdk6 → v3629-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 31 — SALA DEL PARTIDO +
    MEJOR DE 3), sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4 y manifest del oeste v56
    se CONSERVAN sin cambios (esta ronda no toca SDK ni módulos).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3629 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3628"
DEST = RAIZ / "scripts" / "release-v3629"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 30"
BLOQUE_FIN = "    '    TV en directo y los 5 campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 31 — LA CANCHA VISTE EL ARTE DEL PARTIDO@NL@'
    'Y EL DUELO LIBRE PASA AL MEJOR DE 3)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.28-SDK6):@NL@'
    '  · FASE 31 (ronda 37, petición del dueño: «hacer lo mismo para el@NL@'
    '    escenario del partido (Match)» con las caras de partido.zip y «la@NL@'
    '    única salvedad de que para las paredes izquierda y derecha se usará@NL@'
    '    la misma imagen, izquierda.jpg»): la cancha clásica viste ARTE POR@NL@'
    '    DEFECTO mapeado cara a cara, como las salas de campeonato.@NL@'
    '  · ARTE DEL PARTIDO (assets/partido/, 1,8 MB): frente.jpg y fondo.jpg@NL@'
    '    (6,10×2,85), izquierda.jpg en LAS DOS laterales (7,90×2,85 — UNA@NL@'
    '    sola carga, DOS materiales, petición expresa del dueño), suelo.jpg@NL@'
    '    y techo.jpg (6,10×7,90). Dimensiones canónicas de createRoom:@NL@'
    '    mapeo 1:1 sin distorsión ni espejos, SRGBColorSpace + anisotropía.@NL@'
    '  · LA CANCHA NUNCA ESTÁ DESNUDA: el arte por defecto vive en@NL@'
    '    createChampRoom — el campeonato activo con «room» propio GANA clave@NL@'
    '    a clave y las claves que falte vuelven al arte del partido; al salir@NL@'
    '    del campeonato la cancha recupera su vestido. Sin imagen (file://),@NL@'
    '    ese plano conserva su color del tema y el juego sigue.@NL@'
    '  · MEJOR DE 3 (petición del dueño: «al mejor de 3 partidos seguidos…@NL@'
    '    si un jugador gana 2 partidos ya es campeón del enfrentamiento»):@NL@'
    '    el PARTIDO libre (vs CPU y online P2P) se disputa al mejor de 3@NL@'
    '    JUEGOS a 11. Los duelos de CAMPEONATO siguen a juego único.@NL@'
    '  · ÁRBITRO: serie 1-0 tras cada juego, saque alternado por juego (el@NL@'
    '    otro abre, ITTF), marcador a cero sin tocar la serie; 2 victorias@NL@'
    '    = ENFRENTAMIENTO decidido (fanfarria, récord y campeonato SOLO ahí).@NL@'
    '  · MARCADOR 3D con la serie: pucks dorados por juego ganado a los@NL@'
    '    lados de «MEJOR DE 3», mensajes y megafonía nuevos (ES/EN):@NL@'
    '    «JUEGO PARA TI · serie 1-0» y «¡ENFRENTAMIENTO PARA TI!». Revancha@NL@'
    '    por gatillo = nuevo enfrentamiento (la serie respeta el contexto).@NL@'
    '  · ONLINE P2P: la serie viaja en el sync del anfitrión (bo/gp/ga) y el@NL@'
    '    resultado de cada juego con señal send-once (gw) — el invitado lo@NL@'
    '    anuncia en SU idioma y SU perspectiva, igual que los puntos.@NL@'
    '  · TELEMETRÍA (informe del dueño: «no se actualiza»): cadena completa@NL@'
    '    verificada END-TO-END desde producción con navegador real — el boot@NL@'
    '    de la sonda LLEGÓ al Worker (total +1 · sent=1 · sin errores). El@NL@'
    '    Worker está sano (POST 204 con lote y wrapper · D1 viva · latido@NL@'
    '    público). Si en el casco no llega: revisar Opciones → «Telemetría@NL@'
    '    anónima: Sí» (el opt-out vive en el localStorage del visor) y@NL@'
    '    reponer la clave de lectura (.clave-produccion) para el panel.@NL@'
    '  · Capa X nueva (qa_partido_sala_v3629, en vivo): 37 checks — las 6@NL@'
    '    caras con su map, izquierda/derecha compartiendo textura, rejilla@NL@'
    '    y paneles ocultos, contrato P2P de la serie, árbitro del mejor de@NL@'
    '    3 completo (2 juegos → serie → game-over), bestOf=1 para@NL@'
    '    campeonatos, marcador con la serie y los 5 JPG con peso real.@NL@'
    '  · Conserva TODO: el SALÓN DEL ARTISTA (FASE 30), la coronación épica@NL@'
    '    y la RUTA LEYENDA del Oeste, el tren 100 % sonoro, el ESCUDO DE@NL@'
    '    PALA, el REACTOR DE IMPULSO, la CCD SDF de contacto, el saque VR@NL@'
    '    realista, PRO CIRCUITO, intro oficial, física viva, palas con@NL@'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.28-SDK6", "V3.6.29-SDK6"),
    ("3.6.28-SDK6", "3.6.29-SDK6"),
    ("v3628-sdk6", "v3629-sdk6"),
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
        antes = len(txt)
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
            print(f"  ✓ {f.name}: notas FASE 31 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.28"' in txt:
                txt = txt.replace('grep -c "3.6.28"', 'grep -c "3.6.29"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.29")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.28" in txt:
                txt = txt.replace("menciones 3.6.28", "menciones 3.6.29")
                txt = txt.replace("n3628 = int", "n3629 = int").replace("{n3628}", "{n3629}").replace("if n3628 < 4", "if n3629 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.29")
            # el SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
            # ronda: sus guards se conservan tal cual (verificación abajo).
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.29-SDK6") == 1:
            txt = txt.replace("frente a V3.6.29-SDK6", "frente a V3.6.28-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.28)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3629 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.28-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n28 = bz.count("3.6.28-SDK6")
    if n28 != 1 or "frente a V3.6.28-SDK6" not in bz:
        print(f"aviso: 3.6.28-SDK6 queda ×{n28} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3628-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.29-SDK6" not in bz or "FASE 31" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # guards CONSERVADOS: SDK 1.5.4 y oeste v56 siguen pinchados
    if "const SDK_VERSION = '1.5.4'" not in bz:
        print("FALLO: el guard del SDK 1.5.4 se perdió")
        sys.exit(1)
    if "'oeste': (56," not in bz:
        print("FALLO: el guard del manifest v56 se perdió")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # el bloque nuevo debe citar el QA nuevo de esta ronda
    if "qa_partido_sala_v3629" not in bz:
        print("FALLO: las notas no citan la capa X nueva")
        sys.exit(1)
    print(f"\n✓ release-v3629 generada y verificada ({DEST})")


if __name__ == "__main__":
    main()
