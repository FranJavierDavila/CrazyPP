"""gen_release_v3663 — clona scripts/release-v3662 → scripts/release-v3663
y mete las NOTAS de la FASE 65 «EL SERVICIO HONESTO» en build_zip.py
(marcadores reales del bloque), heredando guards intactos.

Idempotente: si release-v3663 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3662"
DEST = RAIZ / "scripts" / "release-v3663"
BS_N = chr(92) + "n"

# ── marcadores del bloque de notas del build_zip r70 (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 64 — LA ACADEMIA PERFECTA: el\\n'"
BLOQUE_FIN = "    '    CRAZY TV y los 5 campeonatos).\\n\\n'"

BLOQUE_NUEVO = "    'Rama    : main · SDK6 (FASE 65 — EL SERVICIO HONESTO: el@NL@'\n    'informe del dueño tras probar V3.6.62 en el Quest, punto por punto,@NL@'\n    '«Vamos a hacerlo bien y dejar la academia PERFECTA»)@NL@@NL@'\n    'Novedades de esta versión (frente a V3.6.62-SDK6):@NL@@NL@'\n    '  · EL SAQUE DEL PROFESOR, REGLAMENTARIO (el dueño: «cuando el@NL@'\n    '    profesor realiza un saque lo hace mal: tiene que botar primero@NL@'\n    '    en su campo y después en el nuestro»). La bola-demo vivía a la@NL@'\n    '    ALTURA de la mesa 17 cm detrás del borde: ningún arco que parte@NL@'\n    '    descendiendo puede botar antes en SU campo desde ahí — el solver@NL@'\n    '    no hallaba candidatos y caía SIEMPRE al fallback (lob directo al@NL@'\n    '    campo del jugador: UN solo bote). Ahora la bola flota ELEVADA@NL@'\n    '    (TY+0.34) justo tras el borde: el solver devuelve saques con bote@NL@'\n    '    propio profundo + bote en el nuestro, verificado 40/40 con la@NL@'\n    '    física real de los módulos (margen de red ≥ 49 mm).@NL@@NL@'\n    '  · BOTES SOBRE LA MESA, NO EN EL SUELO (el dueño: «está dando por@NL@'\n    '    saque correcto si la bola bota en nuestro campo aunque no bote@NL@'\n    '    en el del rival»): la valla antigua (z + vel.y + y<TY+0.35)@NL@'\n    '    aceptaba el bote en el SUELO — un saque largo que se marchaba@NL@'\n    '    fuera del fondo «botaba» más allá de la mesa y contaba. Ahora@NL@'\n    '    cada bote exige el RECTÁNGULO real del campo (x y z de la mesa)@NL@'\n    '    y pegado a la superficie (y<TY+12 cm), en el saque del jugador Y@NL@'\n    '    en la demo del profesor. Volea, medio saque, LARGO, LATERAL y@NL@'\n    '    cruzar sin botar = «OTRA VEZ»; solo el doble bote cuenta.@NL@@NL@'\n    '  · CARTEL SIN RECORTES (el dueño: «con 10-10 se alternan los@NL@'\n    '    saques… la palabra GAN aparece cortada y debería decir GANAR»):@NL@'\n    '    «¡+2 PARA GANAR!» a 54 px no cabía en el lienzo de 256 px del@NL@'\n    '    cartel holográfico. Ahora el cartel MIDE el texto y encoge la@NL@'\n    '    fuente hasta caber (autoajuste, para cualquier cadena futura en@NL@'\n    '    ES y EN) y el plano crece a 0.50 m — GANAR entero.@NL@@NL@'\n    '  · NIVEL DE CPU Y RIVAL ADAPTATIVO, DENTRO DE AJUSTES (el dueño:@NL@'\n    '    «los apartados de Nivel de la CPU y Opción de rival adaptativo@NL@'\n    '    deben ir dentro del apartado de Ajustes»): fuera del menú@NL@'\n    '    principal — viven en AJUSTES › JUEGO junto a la Pala Mejorada.@NL@'\n    '    La dificultad vigente sigue a la vista en la tarjeta de PARTIDO.@NL@@NL@'\n    '  · AJUSTES POR SUBCATEGORÍAS (el dueño: «mejor organizado por@NL@'\n    '    subcategorías con iconos explícitos de cada una, un diseño@NL@'\n    '    bonito y agradable»): cinco TARJETAS con icono propio (chip@NL@'\n    '    JUEGO · casa SALA Y ESCENA · altavoz SONIDO · ojo VISUALES ·@NL@'\n    '    persona PERFIL Y DATOS), subtítulo con ESTADO VIVO de lo que se@NL@'\n    '    ajusta dentro, y subpágina propia por categoría con todos sus@NL@'\n    '    controles. Nada desaparece: el apoyo Ko-fi queda al pie.@NL@@NL@'\n    '  · Conserva TODO lo anterior (troqueles siempre, panel sin solapes,@NL@'\n    '    voz del vaivén, voz que muere al salir y blindaje total r70;@NL@'\n    '    una sola raqueta y golpes honestos r69; la raqueta del rival@NL@'\n    '    r68 con saques al paso de la hoja; la academia en tus manos@NL@'\n    '    r67; la academia sobre la mesa r66; el onboarding hablado r65;@NL@'\n    '    la academia a punto r64; el toque profesional r62; la estela de@NL@'\n    '    poderes, el rival adaptativo y la repetición r61; 5 poderes,@NL@'\n    '    voz del selector, expresiones, bomba y eléctrico, passthrough@NL@'\n    '    en caliente, SALÓN, PRO CIRCUITO, CCD, CRAZY TV y los 5@NL@'\n    '    campeonatos).@NL@@NL@'\n"

GLOBALES = [
    ("V3.6.62-SDK6", "V3.6.63-SDK6"),
    ("3.6.62-SDK6", "3.6.63-SDK6"),
    ("v3662-sdk6", "v3663-sdk6"),
    ("3.6.62", "3.6.63"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.63-SDK6", "frente a V3.6.62-SDK6"),
    ("tras probar V3.6.63", "tras probar V3.6.62"),
]


def main():
    if DEST.exists():
        print("regenerando (release-v3663 ya existía)…")
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
            print(f"  ✓ {f.name}: notas FASE 65 insertadas")
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
