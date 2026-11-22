#!/usr/bin/env python3
"""gen_release_v3682 — hereda scripts/release-v3681 → scripts/release-v3682
e inserta las NOTAS de la FASE 84 «HALLOWEEN SUENA Y SE JUEGA (r90)» en
build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Idempotente: si release-v3682 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3681"
DEST = RAIZ / "scripts" / "release-v3682"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)
NLL = NL + NL               # \n\n literal

# ── bloque FASE 83 COMPLETO en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 83 — INFORME r89: el mapa cuelga ENMAR-" + NL + "'"
BLOQUE_VIEJO_FIN = ("    '    victory.mp3 cuando él gana; precarga completa en el arranque." + NL + "'")

# líneas de texto PLANO de las notas FASE 84 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 84 — INFORME r90: HALLOWEEN SUENA Y SE",
    "    'JUEGA. La BSO es Midnight_Volley, los sonidos del zombi viajan por",
    "    'el motor PROBADO del casco, el mapa luce su color real, las manos",
    "    'cortan SIN montículo y ATRAPAN la bola como Burla, las vísceras",
    "    'detectan su cuadrado exacto con humillo continuo y la calabaza por",
    "    'fin SE VE y se juega.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.81-SDK6):",
    "    '",
    "    '  · BSO REAL DEL CAMPEONATO (petición del dueño: «añadir la música",
    "    '    de fondo Midnight_Volley.mp3»): bso.wav PROVISIONAL fuera — la",
    "    '    pista del dueño (153,6 s) entra re-codificada al PERFIL PROBADO",
    "    '    del casco (44100 Hz · 256 kbps CBR), con el mismo motor de",
    "    '    música de siempre (createMusic: fundido, ancla y rena-",
    "    '    cimiento; el interruptor de MÚSICA del arcade la gobierna).",
    "    '",
    "    '  · SONIDOS DEL ZOMBI AL MOTOR PROBADO (informe: «los sonidos que",
    "    '    te pasé no se escuchan crazy/defeated/victory»): LA LECCIÓN DEL",
    "    '    TREN (cinco versiones, Tasks 129→134) era createSfx JAMÁS llegó",
    "    '    al hardware de la Quest mientras createBucle sonó SIEMPRE — los",
    "    '    cuatro sonidos del zombi (risa/crazy/victory/defeated) son hoy",
    "    '    un createBucle propio con disparo on(), revival por statechange",
    "    '    y reloj de corte honesto (off antes del wrap del bucle). Y",
    "    '    zombi_victory.mp3 venía a 24 kHz — EL PERFIL QUE EL CASCO NO",
    "    '    DECODIFICA (el Tunel mudo de v3.6.25): los cuatro re-codifica-",
    "    '    dos a 44100/256 CBR y verificados por decodificación real.",
    "    '",
    "    '  · MAPA CON SU COLOR (informe: «la que estás poniendo está poco",
    "    '    saturada y muy lavada de color»): la textura del arte nacía SIN",
    "    '    colorSpace — el renderer la trataba como LINEAL y desaturaba el",
    "    '    póster. SRGBColorSpace + anisotropía, y el ARTE NUEVO del dueño",
    "    '    (mismo 1380×752: los 5 nodos quedan clavados).",
    "    '",
    "    '  · MANOS SIN MONTÍCULO (informe: «retirar monticulo.png de la mesa,",
    "    '    se superpone con mano1/2/3 y esta se corta»): el montículo sale",
    "    '    de la mesa — la mano nace DIRECTA con su tierra integrada.",
    "    '",
    "    '  · COLISIÓN BOLA↔MANO = MOTOR DE BURLA (informe: «¿qué pasa que la",
    "    '    bola no hace nada al atravesar o chocar con las manos? con Clown",
    "    '    con el superpoder Burla era muy similar y funcionaba perfecta-",
    "    '    mente»): (1) BUG RAÍZ cazado — el código llamaba bola.vel.set",
    "    '    sobre game.ball.POS (un Vector3 SIN .vel): TypeError tragado por",
    "    '    el catch del motor, la mano quedaba marcada y NADA pasaba (así",
    "    '    llevaba desde r87); (2) CCD por SEGMENTO subdividido a ≤3 cm —",
    "    '    la bola NO atraviesa la mano entre frames; (3) caja en el marco",
    "    '    LOCAL de la mano (vale por DELANTE y por DETRÁS) y banda DESDE",
    "    '    LA MESA (el test antiguo flotaba a +0,46 m y las bolas de rallye",
    "    '    pasaban por debajo). Al chocar: la bola SE PARA Y CAE (0,-0.4,0",
    "    '    como Burla), crujido seco y la mano REVIENTA en 6 trocitos.",
    "    '",
    "    '  · VÍSCERAS SIN DESFASE + HUMILLO CONTINUO (informe: «desfase entre",
    "    '    la posición de la textura y la zona de colisión… mientras dure",
    "    '    el efecto desde las texturas esté saliendo el humillo verde",
    "    '    fosforito continuamente»): la zona de impacto ES el CUADRADO",
    "    '    visual exacto de la mancha (punto de la bola al marco local por",
    "    '    quaternion inverso — el círculo salado de r89 no cubría esquinas",
    "    '    ni respetaba el giro) y cada mancha echa SU humillo por turnos",
    "    '    (~6 efluvios/s, tope 70 sprites) durante TODO el poder (12 s).",
    "    '",
    "    '  · CALABAZA GARANTIZADA (informe: «sigue sin verse, o lo soluciona-",
    "    '    mos si se puede o tenemos que buscar otra forma»): OTRA FORMA —",
    "    '    el GLB de Sketchfab se RETIRA del runtime (cargaba pero NUNCA se",
    "    '    pintó en el casco en 4 rondas y al marcarse «listo» bloqueaba el",
    "    '    respaldo: bola oculta). La calabaza ES el cuerpo PROCEDURAL de",
    "    '    la casa (LatheGeometry con costillas pintadas + rabo + zarcillo,",
    "    '    el pipeline del trofeo del Hall) y nace EN EL DISPARO — sin",
    "    '    esperas, sin swaps, sin congelación extra del aviso (2 s norma-",
    "    '    les), PUDRICIÓN hasta el estallido con CHOFFF intactas y PESO",
    "    '    ESTÁNDAR (decisión del dueño).",
    "    '",
]

# ── 1. heredar el directorio ─────────────────────────────────────────────
if DEST.exists():
    shutil.rmtree(DEST)
shutil.copytree(ORIGEN, DEST)
print(f'· heredado {ORIGEN.name} → {DEST.name}')

# ── 2. reescribir build_zip.py ───────────────────────────────────────────
src = BZ.read_text(encoding='utf-8')
for a, b in [
    ("release-v3681", "release-v3682"),
    ("staging-v3681", "staging-v3682"),
    ("v3681-sdk6", "v3682-sdk6"),
    ("V3.6.81-SDK6", "V3.6.82-SDK6"),
]:
    src = src.replace(a, b)

# bloque de notas: sustituir el FASE 83 completo por el FASE 84
i0 = src.find(BLOQUE_VIEJO_INI)
assert i0 >= 0, 'no encuentro el inicio del bloque FASE 83'
i1 = src.find(BLOQUE_VIEJO_FIN, i0)
assert i1 >= 0, 'no encuentro el fin del bloque FASE 83'
i1 += len(BLOQUE_VIEJO_FIN)
# cada línea: abre comilla (ya viene en _NOTAS) + texto + \n + cierra comilla,
# unidas por salto de línea REAL (implíc-concatenation como el bloque original)
nuevo = chr(10).join(ln + NL + "'" for ln in _NOTAS)
src = src[:i0] + nuevo + src[i1:]
BZ.write_text(src, encoding='utf-8')
print(f'· build_zip.py reescrito: notas FASE 84 ({len(_NOTAS)} líneas), versiones → v3682-sdk6')
print('OK — ejecuta: python3 scripts/release-v3682/build_zip.py')
