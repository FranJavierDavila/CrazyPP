"""gen_release_v3665 — hereda scripts/release-v3664 → scripts/release-v3665
e inserta las NOTAS de la FASE 67 «EL MENÚ MANDA» en build_zip.py.

EXTRA (limpieza heredada): el bloque de notas de v3664 dejaba una COLA
VIEJA duplicada (el «Conserva TODO (la raqueta del rival r68…)» de la
v3663) después del bloque nuevo — esta ronda lo sustituye por UN solo
bloque limpio de la FASE 67: INI (Rama FASE 66) → FIN (el segundo
«campeonatos).\n\n'», fin de la cola vieja).

Idempotente: si release-v3665 ya existe, se regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3664"
DEST = RAIZ / "scripts" / "release-v3665"
BS_N = chr(92) + "n"

# ── marcadores del bloque de notas del build_zip r72 (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 66 — EL TELÓN Y EL CANDADO: el\\n'"
# la COLA VIEJA termina en el SEGUNDO «campeonatos).\n\n'» (la limpieza r73)
BLOQUE_FIN = "    '    campeonatos).\\n\\n'"

BLOQUE_NUEVO = (
    "    'Rama    : main · SDK6 (FASE 67 — EL MENÚ MANDA: el informe del@NL@'\n"
    "    'dueño tras probar V3.6.64 en el Quest, punto por punto)@NL@@NL@'\n"
    "    'Novedades de esta versión (frente a V3.6.64-SDK6):@NL@@NL@'\n"
    "    '  · EL MENÚ MANDA, ESTEMOS DONDE ESTEMOS (el dueño: «cuando@NL@'\n"
    "    '    desplegamos un Menú debe ser la ventana que manda y debe verse@NL@'\n"
    "    '    siempre la primera, aunque por debajo tengamos cualquier@NL@'\n"
    "    '    otra»): la familia del menú sube al cielo del render — panel@NL@'\n"
    "    '    9998, cursores 9999, rayos 9997 — POR ENCIMA de las@NL@'\n"
    "    '    instrucciones de campeonato (9994/9995), del mapa de etapas del@NL@'\n"
    "    '    Oeste (9990..9996) y del telón (65/70). Al abrir el menú sobre@NL@'\n"
    "    '    cualquier ventana, el menú gana; al cerrarlo, la otra vuelve@NL@'\n"
    "    '    intacta.@NL@@NL@'\n"
    "    '  · CANDADOS BIEN COLOCADOS (el dueño: «el texto Próximamente está@NL@'\n"
    "    '    bien puesto pero los candados están mal colocados y aparecen@NL@'\n"
    "    '    desplazados»): causa raíz — PP_ICONS.candado hacía scale(1,35)@NL@'\n"
    "    '    ANTES de dibujar en las coordenadas absolutas, así que el@NL@'\n"
    "    '    candado se pintaba a 1,35× la posición pedida (un candado@NL@'\n"
    "    '    fantasma flotaba junto al pie del menú). Ahora traslada al@NL@'\n"
    "    '    ancla y escala después: el candado nace pegado al nombre,@NL@'\n"
    "    '    centrado con el título. Verificado píxel a píxel.@NL@@NL@'\n"
    "    '  · EL SALVAJE OESTE, SIEMPRE EN EL MENÚ (el dueño: «me ha@NL@'\n"
    "    '    desaparecido el campeonato del Salvaje Oeste, recupéralo y@NL@'\n"
    "    '    ponlo accesible»): el índice y los manifest se pedían UNA sola@NL@'\n"
    "    '    vez — una petición perdida (WiFi del visor, un 502 puntual) lo@NL@'\n"
    "    '    borraba del menú PARA SIEMPRE. Ahora: fetch con cache:@NL@'\n"
    "    '    no-cache, reintentos con espera exponencial, manifest en@NL@'\n"
    "    '    PARALELO, DOS OLAS de recuperación (+8 s y +25 s) que repintan@NL@'\n"
    "    '    el menú al recuperar cada carpeta, estado «Cargando@NL@'\n"
    "    '    campeonatos…» mientras llega y botón REINTENTAR si la red@NL@'\n"
    "    '    falló del todo. El Oeste (y cualquier hermano) ya no se cae del@NL@'\n"
    "    '    menú por un hipo de red.@NL@@NL@'\n"
    "    '  · EL TELÓN DE TEATRO (el dueño: «está muy mal diseñado: debe@NL@'\n"
    "    '    estar alejado de la vista como a 2 metros y no es poner un@NL@'\n"
    "    '    pegote de pantalla sino que todo el entorno que nos rodea esté@NL@'\n"
    "    '    negro con el texto delante hasta que cargue el escenario»):@NL@'\n"
    "    '    rediseño total — ESFERA NEGRA invertida de 12 m colgada del@NL@'\n"
    "    '    rig y centrada en la cabeza cada tick (paredes, mesa, troqueles@NL@'\n"
    "    '    y passthrough desaparecen: el mundo entero se apaga) + TARJETA@NL@'\n"
    "    '    DE INTERMEDIO a 2,00 m exactos que sigue a la cabeza (giro y@NL@'\n"
    "    '    altura, siempre de cara) con doble marco en el color del@NL@'\n"
    "    '    campeonato, «CRAZY PING PONG PRESENTA» con aire entre letras,@NL@'\n"
    "    '    título autoajustado, «Montando el escenario...» y una BOLA que@NL@'\n"
    "    '    va y viene sobre una pista con red — el ping pong nunca se@NL@'\n"
    "    '    apaga. Fundido de salida que desmonta esfera y cartel. Tick en@NL@'\n"
    "    '    TIEMPO REAL y API intactas (mín 0,9 s + 0,3 s estables · tope@NL@'\n"
    "    '    12 s · si toca intro, el telón cede a la presentación).@NL@@NL@'\n"
    "    '  · Conserva TODO lo anterior (telón con espera honesta y candados@NL@'\n"
    "    '    con voz «Próximamente» r72; saque reglamentario del profesor y@NL@'\n"
    "    '    botes solo sobre la mesa, cartel GANAR entero y AJUSTES por@NL@'\n"
    "    '    subcategorías r71; troqueles siempre, panel sin solapes, voz@NL@'\n"
    "    '    del vaivén y blindaje total r70; una sola raqueta y golpes@NL@'\n"
    "    '    honestos r69; la raqueta del rival r68; la academia en tus@NL@'\n"
    "    '    manos r67; la academia sobre la mesa r66; el onboarding@NL@'\n"
    "    '    hablado r65; la estela de poderes, el rival adaptativo y la@NL@'\n"
    "    '    repetición r61; 5 poderes, voz del selector, expresiones,@NL@'\n"
    "    '    passthrough en caliente, SALÓN, PRO CIRCUITO, CCD, CRAZY TV y@NL@'\n"
    "    '    los 5 campeonatos).@NL@@NL@'"
)

GLOBALES = [
    ("V3.6.64-SDK6", "V3.6.65-SDK6"),
    ("3.6.64-SDK6", "3.6.65-SDK6"),
    ("v3664-sdk6", "v3665-sdk6"),
    ("3.6.64", "3.6.65"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.65-SDK6", "frente a V3.6.64-SDK6"),
    ("tras probar V3.6.65", "tras probar V3.6.64"),
]


def main():
    if DEST.exists():
        print("regenerando (release-v3665 ya existía)…")
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    print(f"copiado {ORIGEN.name} → {DEST.name}")

    for f in sorted(DEST.iterdir()):
        if not f.is_file():
            continue
        txt = f.read_text(encoding="utf-8")
        if f.name == "build_zip.py":
            i = txt.find(BLOQUE_INI)
            if i < 0:
                print("FALLO: marcador INI del bloque no encontrado")
                sys.exit(1)
            j = txt.find(BLOQUE_FIN, i)
            if j < 0:
                print("FALLO: marcador FIN del bloque no encontrado")
                sys.exit(1)
            j += len(BLOQUE_FIN)
            # la cola vieja sigue hasta un SEGUNDO BLOQUE_FIN (limpieza r73)
            j2 = txt.find(BLOQUE_FIN, j)
            if j2 >= 0 and j2 - j < 4000:
                j = j2 + len(BLOQUE_FIN)
                print("  ✓ cola vieja duplicada (v3663) retirada")
            txt = txt[:i] + BLOQUE_NUEVO.replace("@NL@", BS_N) + txt[j:]
            print(f"  ✓ {f.name}: notas FASE 67 insertadas")
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
                    print(f"  ✓ {f.name}: restaurado {viejo} → {nuevo} (×{n})")
        f.write_text(txt, encoding="utf-8")

    print(f"OK → {DEST}")


if __name__ == "__main__":
    main()
