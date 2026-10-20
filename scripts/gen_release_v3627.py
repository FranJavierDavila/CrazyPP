#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 35 · GENERADOR DEL DIRECTORIO DE RELEASE v3627
======================================================================
Crea scripts/release-v3627/ a partir de scripts/release-v3626/ con:
  · reemplazos de versión (3.6.26-SDK6 → 3.6.27-SDK6 · v3626-sdk6 → v3627-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 29 — HALL OF FAME),
    sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4 y manifest del oeste v56
    se CONSERVAN sin cambios (esta ronda no toca SDK ni módulos).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3627 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3626"
DEST = RAIZ / "scripts" / "release-v3627"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 28"
BLOQUE_FIN = "    '    con carácter, CRAZY TV en directo y los 5 campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 29 — HALL OF FAME: EL HALL DEL ANFITRIÓN@NL@'
    'SE CONVIERTE EN MUSEO)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.26-SDK6):@NL@'
    '  · FASE 29 (ronda 35, petición del dueño: «decorar las paredes del@NL@'
    '    Hall como un Hall Of Fame de Ping Pong… por un lado nuestros@NL@'
    '    logros, por otro nuestro ranking e insignias y en otra pared las@NL@'
    '    palas… suelo y techos con buen gusto artístico y sorpresas»):@NL@'
    '    la estancia de entrada es ahora un MUSEO COMPLETO del ping pong.@NL@'
    '  · PARED DE LA GLORIA: cartel HALL OF FAME con subtítulo en oro,@NL@'
    '    insignias de campeonatos en marcos de latón con placa de nombre@NL@'
    '    y placa de RÉCORD Y RANKING grabada en bronce (victorias, mejor@NL@'
    '    racha, mejor rallye, saques directos, PRO CIRCUITO ★ y victorias@NL@'
    '    por dificultad — cifras reales de la carrera del anfitrión).@NL@'
    '  · PARED DE LOGROS CRAZY: cabecera dorada + 6 medallones individuales@NL@'
    '    con aro de latón (encendidos si conseguidos, apagados si faltan)@NL@'
    '    y cita de museo grabada bajo la galería.@NL@'
    '  · PARED DE VITRINAS: 6 escaparates de madera y latón, uno por piel@NL@'
    '    de pala, con la hoja teñida de su color cuando está conseguida y@NL@'
    '    placa BLOQUEADA cuando falta (Clásica, Fuego, Hielo, Oro, Arcoíris,@NL@'
    '    Pro Carbon).@NL@'
    '  · PARED DE LA PUERTA: neón CRAZY PING PONG en rosa y cian con triple@NL@'
    '    pasada de brillo (halo → cuerpo → alma) + apliques de latón.@NL@'
    '  · SUELO: parqué de roble con el EMBLEMA DE LA CASA (palas cruzadas@NL@'
    '    y bola en oro) + alfombra roja de bienvenida con filete de latón.@NL@'
    '    TECHO: artesonado con vigas, paneles de luz cálida y anillo dorado.@NL@'
    '  · LA SORPRESA: TROFEO DE CAMPEÓN torneado en 3D (copa Lathe + dos@NL@'
    '    asas + bola dorada) sobre peana de mármol bajo un haz de luz@NL@'
    '    volumétrico que respira — GIRA lentísimo y está PLATEADO mientras@NL@'
    '    espera al primer campeón; al coronar el primer campeonato se funde@NL@'
    '    a ORO con placa de SALÓN DE CAMPEONES. 7 bolas doradas flotan en@NL@'
    '    vaivén de museo (updateHallFx, sólo con la estancia visible).@NL@'
    '  · Capa W nueva (qa_hall_fama_v3627, en vivo): 24 checks del museo —@NL@'
    '    estructura completa, sorpresas vivas (giro del trofeo y vaivén de@NL@'
    '    bolas), trofeo plateado sin campeón, agujas del fichero servido y@NL@'
    '    pintores antiguos (drawHallAchs / drawHallCirc) retirados.@NL@'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del@NL@'
    '    Oeste, el tren 100 % sonoro, el ESCUDO DE PALA, el REACTOR DE@NL@'
    '    IMPULSO, la CCD SDF de contacto, el saque VR realista, PRO@NL@'
    '    CIRCUITO, intro oficial, física viva, palas con carácter, CRAZY@NL@'
    '    TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.26-SDK6", "V3.6.27-SDK6"),
    ("3.6.26-SDK6", "3.6.27-SDK6"),
    ("v3626-sdk6", "v3627-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 29 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.26"' in txt:
                txt = txt.replace('grep -c "3.6.26"', 'grep -c "3.6.27"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.27")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.26" in txt:
                txt = txt.replace("menciones 3.6.26", "menciones 3.6.27")
                txt = txt.replace("n3626 = int", "n3627 = int").replace("{n3626}", "{n3627}").replace("if n3626 < 4", "if n3627 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.27")
            # el SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
            # ronda: sus guards se conservan tal cual (verificación abajo).
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.27-SDK6") == 1:
            txt = txt.replace("frente a V3.6.27-SDK6", "frente a V3.6.26-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.26)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3627 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.26-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n26 = bz.count("3.6.26-SDK6")
    if n26 != 1 or "frente a V3.6.26-SDK6" not in bz:
        print(f"aviso: 3.6.26-SDK6 queda ×{n26} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3626-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.27-SDK6" not in bz or "FASE 29" not in bz:
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
    if "qa_hall_fama_v3627" not in bz:
        print("FALLO: el bloque nuevo no cita qa_hall_fama_v3627")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3627 listo → python3 scripts/release-v3627/build_zip.py")


if __name__ == "__main__":
    main()
