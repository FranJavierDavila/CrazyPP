#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.138-SDK6 (r43).
Crea scripts/release-v36138/ a partir de scripts/release-v36137/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 140
    (con ABORTE DURO si los marcadores no casan — lección r33)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36138 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36138.py
    python3 scripts/release-v36138/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36137"
DEST = RAIZ / "scripts" / "release-v36138"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 140 — EL SUELO DE DESTELLOS y el DUELO",
    "HONESTO Y FLUIDO — el informe del dueño tras la v3.6.137 en el",
    "casco, cuatro frentes: el SUELO ARCANO rediseñado (la trama fina",
    "SÓLO existe donde un destello la dibuja — líneas mucho más",
    "delgadas que se cruzan a 90° en ambos sentidos, nacen en un fondo",
    "y llegan al otro, dejan su estela ~5 s y desaparecen, con los",
    "rellenos en las celdas que atraviesan), el LETRERO «Salir/Exit»",
    "sobre el búho al apuntarlo (letras azules con el halo azulón, la",
    "misma estética del búho), la ESFERA DEL CASCO REMOTO en el RIG",
    "(se acabó la deriva de ~1 m respecto a la vertical de la pala) y",
    "los tres ajustes del DUELO ONLINE: bola VISIBLE en todos los",
    "saques, CONVERGENCIA del fantasma en la zona de juicio (los",
    "buenos/fallos vuelven a coincidir) y FLUIDEZ — física en tiempo",
    "real (la bola jamás va a cámara lenta) y el camino de envío sin",
    "allocations por paquete — adiós a los micro-parones del GC).",
    "  · 1 · EL SUELO DE DESTELLOS (c08·montaSueloArcano rediseñada +",
    "    updateArcanoFx): FUERA la matriz estática de la r41 — un lienzo",
    "    vivo 512² repinta cada frame DESTELLOS-corredores que recorren",
    "    líneas de la retícula fina (48×48 losetas de 1,5 m) en AMBOS",
    "    ejes (cruces de 90°) y AMBOS sentidos, naciendo en un borde y",
    "    muriendo en el opuesto; tras la cabeza viaja la ESTELA = la",
    "    propia línea (0,8 px ≈ 5 cm reales — mucho más delgada que la",
    "    r41) con cabeza aditiva blanco-azul, aguanta ~5 s y se funde en",
    "    0,9 s; las celdas que el destello atraviesa encenden su RELLENO",
    "    azul (banda del dueño, envolvente nacer→aguantar→morir, tope",
    "    70 vivas y ~9 destellos simultáneos — coste acotado).",
    "  · 2 · EL LETRERO DE SALIDA (c08/c12/c00): drawArcanoSalir —",
    "    letras azules con TRIPLE pasada de halo (halo→cuerpo→alma, la",
    "    técnica del neón del Hall) sobre el búho (y 2,95); sprite de",
    "    HALO azul aditivo detrás; se FUNDE con el hover del búho (op",
    "    0→1, ascenso leve al entrar) y el texto viaja con el IDIOMA",
    "    vivo (arcono_boton_salir: Salir / Exit, repintado en",
    "    _arconoRepinta).",
    "  · 3 · LA ESFERA DEL CASCO EN EL RIG (c12): la esfera negra del",
    "    rival era el ÚNICO objeto colgado de la ESCENA raíz; pala,",
    "    bola, mesa y marcador cuelgan del RIG y el recentrado de la",
    "    sesión gira el rig (yaw del casco al entrar en VR) — la esfera,",
    "    fuera del rig, quedaba ROTADA respecto a todo lo demás: deriva",
    "    fija de ~1 m a la derecha, altura correcta, persistente en",
    "    cualquier extremo (el informe exacto del dueño). Ahora comparte",
    "    marco con la pala: si la pala está bien alineada, la cabeza",
    "    TAMBIÉN.",
    "  · 4 · BOLA VISIBLE EN TODOS LOS SAQUES (c12/c09): rama nueva del",
    "    guardián para el lanzamiento del rival EN VUELO (_netTossLive)",
    "    — la malla se re-enciende SIN tocar el estado y el flag CADUCA",
    "    a los 2,5 s sellado por _netTossAt (c12 + los DOS caminos de",
    "    c09: SNAP de rescate y HIT kind 2) — si el HIT del saque se",
    "    pierde o es rechazado, el guardián retoma el mando; el fallback",
    "    del rival entra YA si la malla está oculta (sin los 0,6 s",
    "    ciegos).",
    "  · 5 · DUELO HONESTO (c09): CONVERGENCIA EN LA ZONA DE JUICIO —",
    "    el fantasma integra su física local y los SNAP la corregían con",
    "    un lerp blando (0,25/0,12): unos pocos cm de divergencia SOBRE",
    "    LA MESA cambiaban la percepción del punto (fallo visto como",
    "    bueno). Dentro del rectángulo de mesa + 30 cm y bajo tapete +",
    "    42 cm, la corrección se endurece (0,62/0,38): el dueño VE lo",
    "    mismo que juzga el árbitro del emisor. Fuera de la mesa, el",
    "    lerp suave de siempre (nada de teleports perceptibles).",
    "  · 6 · FLUIDEZ — DOS PALANCAS (c12/c09): (a) FÍSICA EN TIEMPO",
    "    REAL: dtFis = el tiempo REAL del frame (capado a 1/12 s;",
    "    stepPhysics subescala a 480 Hz, tope 96 subpasos) — la bola ya",
    "    NO va a cámara lenta cuando un frame pasa de 33 ms (el dt de",
    "    timers/UI/red sigue capado a 1/30, spec A intacta; la",
    "    dilatación CRONOS se aplica sobre dtFis); (b) TX SIN",
    "    ALLOCATIONS: búfer reutilizado _txBuf (uno por enlace) + VISTA",
    "    al DataChannel (send copia los bytes de la vista) — fuera los",
    "    ~160 new ArrayBuffer + slice + spread POR SEGUNDO que",
    "    alimentaban al GC en plena partida (los micro-parones); el",
    "    túnel PeerJS conserva el slice (serializa su copia).",
    "  · 7 · QA: test_r43_destellos_red_v36138 NUEVO 79/0 (sellos FASE",
    "    140, suelo de destellos con VIDA 5 s, letrero Salir/Exit,",
    "    esfera en el rig, saques, convergencia, dtFis, TX sin",
    "    allocations, PROTO 3 intacto) · PROBE EN VIVO 9/9 (entrada,",
    "    letrero oculto→hover→retirada, tinta del idioma vivo, base",
    "    negra por píxel, trazos vivos con eje/sentido, VIDA 5 s,",
    "    rellenos acotados, ojos oscilando, 0 pageerrors) · regresión",
    "    re-anclada (sella_r43_viva): r41 92/0 · r40 62/0 · r39 165/0 ·",
    "    r38 51/0 · r37 46/0 · r36 30/0 · r35 36/0 · r34 62/0 · r33 77/0 ·",
    "    r32 49/0 · r31 47/0 · r30 54/0 · r24 89/0 · test_red_nucleo",
    "    (PPNET) 60/0.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec (PROTO 3).",
    "  SE CONSERVA TODO: el Arcano holográfico r41 (motas de polvo,",
    "    flechas descruzadas, iconos a sangre, voz por poder, ojos",
    "    azul↔rojo, candado flotante), apartado arcano r39/r40 (búho 25",
    "    %, pulsables sin menú, escenario delante, arcano.mp3), salón de",
    "    la partida r38, multijugador r37/r36, Prisma visible r35, fixes",
    "    r34, lote r33, salones r32, higiene r31, Fénix r30,",
    "    Oscuridad/Crono, voces Piper, iconos del dueño, bola atractora",
    "    r26b, barrera eléctrica, FORO3D r27, skins r21, cortina etapas",
    "    2/4, _bolaGuard, P4, CRAZY LINK v2, ELO, matchmaking,",
    "    halloween.",
    "  · sellada a",
    "  3.6.138",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36137", "release-v36138"),
    ("staging-v36137", "staging-v36138"),
    ("V3.6.137-SDK6", "V3.6.138-SDK6"),
    ("3.6.137-SDK6", "3.6.138-SDK6"),
    ("v36137-sdk6", "v36138-sdk6"),
    ("v36137", "v36138"),
    ("3.6.137", "3.6.138"),
    ("fase 139", "fase 140"),
    ("FASE 139", "FASE 140"),
    ("Fase 139", "Fase 140"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36137 son las de la r41, ya re-selladas a FASE 140 por los tokens):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 140 — EL ARCANO HOLOGRÁFICO: el pulido"
                + NL + "'")
FIN_MARCADOR = ("    '  · sellada a" + NL + "'" + chr(10) +
                "    '  3.6.138" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.138-SDK6 lista: el Arcano holográfico — "
                     "motas de polvo circulares, suelo negro con matriz fina y "
                     "rellenos que nacen y mueren al azar, flechas descruzadas "
                     "(‹ izquierda · › derecha), iconos a sangre completa, panel "
                     "con aparición holográfica, la voz que presenta cada poder, "
                     "ojos del búho azul↔rojo y candado flotante con halo rojo "
                     "pulsante; test r41 92/0, probe en vivo 9/9 y regresión "
                     "re-anclada verde." + "')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.138-SDK6 lista: el suelo de destellos — "
                     "la trama fina sólo existe donde un destello la dibuja "
                     "(90°, ambos sentidos, estela ~5 s), letrero Salir/Exit "
                     "sobre el búho, la esfera del casco remoto en el RIG, "
                     "saques sin bola invisible, convergencia del fantasma en "
                     "la zona de juicio y fluido: física en tiempo real + TX "
                     "sin allocations; test r43 79/0, probe en vivo 9/9 y "
                     "regresión re-anclada verde." + "')")


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    for p in DEST.rglob('*'):
        if not p.is_file() or p.suffix in ('.pyc',) or '__pycache__' in str(p):
            continue
        try:
            txt = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        # bloque de notas → FASE 140 (sustitución ASERTADA — lección r33).
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            f = txt.find(FIN_MARCADOR, i)
            if f < 0:
                raise SystemExit('ABORTE: FIN_MARCADOR no hallado tras INI')
            txt = txt[:i] + _NOTAS + txt[f + len(FIN_MARCADOR):]
            notas_ok = 1
        else:
            notas_ok = 0
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA, 1)
            linea_ok = 1
        elif LINEA_FINAL_NUEVA in txt:
            linea_ok = 1
        else:
            linea_ok = 0
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f'OK gen_release_v36138 · {tocados} ficheros re-sellados · '
          f'notas FASE 140 {notas_ok}/1 · línea final {linea_ok}/1')


if __name__ == '__main__':
    main()
