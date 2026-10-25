"""gen_release_v3664 — clona scripts/release-v3663 → scripts/release-v3664
y mete las NOTAS de la FASE 66 «EL TELÓN Y EL CANDADO» en build_zip.py
(marcadores reales del bloque), heredando guards intactos.

Idempotente: si release-v3664 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3663"
DEST = RAIZ / "scripts" / "release-v3664"
BS_N = chr(92) + "n"

# ── marcadores del bloque de notas del build_zip r71 (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 65 — EL SERVICIO HONESTO: el\\n'"
BLOQUE_FIN = "    '    campeonatos).\\n\\n'"

BLOQUE_NUEVO = "    'Rama    : main · SDK6 (FASE 66 — EL TELÓN Y EL CANDADO: el@NL@'\n    'informe del dueño tras probar V3.6.63 en el Quest, punto por punto,@NL@'\n    '«que se vea montado, no montándose»)@NL@@NL@'\n    'Novedades de esta versión (frente a V3.6.63-SDK6):@NL@@NL@'\n    '  · CARTEL DE LA ACADEMIA SIN SOLAPES (el dueño: «en el paso 3 existe@NL@'\n    '    solapamiento de texto», «en el paso 4 EL INTERCAMBIO se pisa con@NL@'\n    '    el texto de arriba», «en el paso 7 los textos están algo@NL@'\n    '    pegados»): la causa raíz era una sola — los títulos de paso@NL@'\n    '    (y 214..244) se pintaban DENTRO de la banda de la cabecera «LA@NL@'\n    '    ACADEMIA CRAZY» (y 192..232) que dibuja paintHeader en TODOS los@NL@'\n    '    pasos. Ahora cada título tiene SU fila (y=272, LOS MODOS y=262)@NL@'\n    '    y los cuerpos se reexpanden con aire medido línea a línea.@NL@@NL@'\n    '  · PASO 8 · LOS MODOS, REENCUADRADO (el dueño: «los textos están@NL@'\n    '    mal colocados, revisa y encájalos bien»): el texto PODERES se@NL@'\n    '    dibujaba SIEMPRE en el centro de la pizarra (x=680) — ENCIMA de@NL@'\n    '    la tarjeta ENTRENAR (el wrap2 antiguo no aceptaba x) — y la@NL@'\n    '    píldora «GATILLO · continuar» (552..594) pisaba la fila inferior@NL@'\n    '    (terminaba en 566). Ahora PODERES vive DENTRO de su caja ámbar@NL@'\n    '    (centro x=996), la píldora sube a la fila del título (a su@NL@'\n    '    derecha) y la rejilla respira con alturas limpias.@NL@@NL@'\n    '  · ICONOS EN ENTRENAMIENTO (el dueño: «faltan los iconos de los@NL@'\n    '    botones de los apartados de Entrenamiento: Dirección, Altura,@NL@'\n    '    Saque, Efecto y Ritmo, para dejarlo bonito»): seis iconos@NL@'\n    '    vectoriales nuevos en PP_ICONS — diana+flecha DIRECCIÓN, arco@NL@'\n    '    sobre la red ALTURA, bola con estela de giro EFECTO, trayectoria@NL@'\n    '    del doble bote SAQUE, metrónomo RITMO y CANDADO — y las cinco@NL@'\n    '    tarjetas del hub pintan el suyo dentro del medallón.@NL@@NL@'\n    '  · ASTRO, VISIBLE OTRA VEZ (el dueño: «en Estación Orbital no se@NL@'\n    '    visualiza a Astro»): el grupo del campeonato orbital colgaba de@NL@'\n    '    g.scene (mundo crudo) mientras mesa, sala y mapa viven en g.rig —@NL@'\n    '    el RECENTRADO del Quest (25 frames tras cada sesión XR) giraba el@NL@'\n    '    rig y lo dejaba descolocado: era la causa REAL de las tres@NL@'\n    '    correcciones de coordenadas anteriores. Ahora game.rig.add@NL@'\n    '    (convención CLOWN/WIZARD), guard idempotente del standee en@NL@'\n    '    build() (las re-entradas ya no lo duplican) y el stop() del muro@NL@'\n    '    de arkanoid restaura al rival. Manifest del orbital → v17.@NL@@NL@'\n    '  · EL TELÓN DE CARGA (el dueño: «se visualizan los cambios de cómo@NL@'\n    '    se va cargando el escenario… preferible una pantalla negra con@NL@'\n    '    Montando el escenario... que espere hasta que esté todo@NL@'\n    '    cargado»): showChampCurtain — plano 3D negro anclado al rig con@NL@'\n    '    título del campeonato, puntos animados y barra que respira@NL@'\n    '    (visible DENTRO del visor: el DOM no existe en XR). ChampLoader@NL@'\n    '    lo muestra ANTES de importar el módulo y lo levanta en fundido@NL@'\n    '    cuando la sala tiene sus 6 caras cargadas (mínimo 0,9 s + 0,3 s@NL@'\n    '    de lecturas estables · tope de seguridad 12 s · corre en TIEMPO@NL@'\n    '    REAL: una carga lenta no alarga la espera). Si toca intro, el@NL@'\n    '    telón cede a la presentación en cuanto el módulo arranca.@NL@@NL@'\n    '  · CANDADOS EN LOS CAMPEONATOS (el dueño: «Estación Orbital y Valle@NL@'\n    '    Neón bloqueados con un candado visible sobre el propio nombre;@NL@'\n    '    si intentamos entrar, una voz dirá Próximamente; solo podremos@NL@'\n    '    acceder en Modo Depuración FORO3D»): ChampLoader.LOCKED + guard@NL@'\n    '    en launch() (cubre tarjeta, VER PRESENTACIÓN y ?champ=) con voz@NL@'\n    '    announce force, tarjeta atenuada con candado sobre el nombre,@NL@'\n    '    chip plateado PRÓXIMAMENTE y sin chevron ni presentación. Las@NL@'\n    '    reglas de desbloqueo llegarán después: HOY abre el MODO@NL@'\n    '    DEPURACIÓN (nombre de usuario FORO3D → ppDebugMode).@NL@@NL@'\n    '  · Conserva TODO lo anterior (saque reglamentario del profesor y@NL@'\n    '    botes solo sobre la mesa, cartel GANAR entero y AJUSTES por@NL@'\n    '    subcategorías con CPU+adaptativo dentro r71; troqueles siempre,@NL@'\n    '    panel sin solapes, voz del vaivén, voz que muere al salir y@NL@'\n    '    blindaje total r70; una sola raqueta y golpes honestos r69; la@NL@'\n    '    raqueta del rival r68; la academia en tus manos r67; la academia@NL@'\n    '    sobre la mesa r66; el onboarding hablado r65; la estela de@NL@'\n    '    poderes, el rival adaptativo y la repetición r61; 5 poderes, voz@NL@'\n    '    del selector, expresiones, passthrough en caliente, SALÓN, PRO@NL@'\n    '    CIRCUITO, CCD, CRAZY TV y los 5 campeonatos).@NL@@NL@'"

GLOBALES = [
    ("V3.6.63-SDK6", "V3.6.64-SDK6"),
    ("3.6.63-SDK6", "3.6.64-SDK6"),
    ("v3663-sdk6", "v3664-sdk6"),
    ("3.6.63", "3.6.64"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.64-SDK6", "frente a V3.6.63-SDK6"),
    ("tras probar V3.6.64", "tras probar V3.6.63"),
]


def main():
    if DEST.exists():
        print("regenerando (release-v3664 ya existía)…")
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
            txt = txt[:i] + BLOQUE_NUEVO.replace("@NL@", BS_N) + txt[j:]
            print(f"  ✓ {f.name}: notas FASE 66 insertadas")
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
