#!/usr/bin/env python3
"""gen_release_v3666 — hereda scripts/release-v3665 → scripts/release-v3666
e inserta las NOTAS de la FASE 68 «EL MANDO DE SIEMPRE» en build_zip.py.

Idempotente: si release-v3666 ya existe, se regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3665"
DEST = RAIZ / "scripts" / "release-v3666"
BS_N = chr(92) + "n"

# ── marcadores del bloque de notas del build_zip (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 67 — EL MENÚ MANDA: el informe del\\n'"
BLOQUE_FIN = "    '    los 5 campeonatos).\\n\\n'"

BLOQUE_NUEVO = (
    "    'Rama    : main · SDK6 (FASE 68 — EL MANDO DE SIEMPRE: el informe@NL@'\n"
    "    'del dueño tras probar V3.6.65 en el Quest, punto por punto)@NL@@NL@'\n"
    "    'Novedades de esta versión (frente a V3.6.65-SDK6):@NL@@NL@'\n"
    "    '  · PRO TRAINING: EL MENÚ SE SACA CON B (el dueño: «desde el módulo@NL@'\n"
    "    '    Pro training, en cualquier modalidad, sacar el Menú con la tecla@NL@'\n"
    "    '    de siempre, la B (no la Y), para que sea un comportamiento@NL@'\n"
    "    '    común»): la guardia del bloque B ya no se comía el entrenamiento@NL@'\n"
    "    '    (B estaba MUERTO ahí y sólo Y abría) — en CUALQUIER modalidad B@NL@'\n"
    "    '    abre/cierra SU menú (el hub ENTRENAR, con el modo recogido) y Y@NL@'\n"
    "    '    deja de abrir menús (conserva su Y=volver del ajuste de pala).@NL@@NL@'\n"
    "    '  · EL MENÚ MANDA TAMBIÉN SOBRE EL CARTEL EMPEZAR (el dueño: «en las@NL@'\n"
    "    '    etapas 2 y 4, al sacar el menú contextual no recibe el foco y no@NL@'\n"
    "    '    permite pulsar sus botones — parece que sigue mandando el botón@NL@'\n"
    "    '    de debajo»): en onSelectStart la comprobación del menú sube POR@NL@'\n"
    "    '    ENCIMA del bloque del cartel — los clics van a los botones del@NL@'\n"
    "    '    menú y un gatillo que roza el EMPEZAR de detrás ya NO arranca la@NL@'\n"
    "    '    etapa; al cerrar el menú, el cartel sigue intacto. Cubre menú y@NL@'\n"
    "    '    prompt del Hall; y si sales al Hall, el cartel se retira sin@NL@'\n"
    "    '    arrancar nada.@NL@@NL@'\n"
    "    '  · EL GLOW SIGUE LA MANO (el dueño: «si cambiamos la pala de mano@NL@'\n"
    "    '    ese efecto de glow no está presente»): la AURA dorada del paso@NL@'\n"
    "    '    «tu mando es tu raqueta» se montaba UNA vez sobre la montura de@NL@'\n"
    "    '    la mano de entonces — con A/X quedaba huérfana en la mano vacía.@NL@'\n"
    "    '    Ahora se re-papa cada frame a la montura ACTIVA (mismo glow,@NL@'\n"
    "    '    cero coste).@NL@@NL@'\n"
    "    '  · LAS DEVOLUCIONES NUNCA SE ATASCAN (el dueño: «si antes de@NL@'\n"
    "    '    empezar a devolver pulsas o haces un saque, no puedes avanzar»):@NL@'\n"
    "    '    el paso 5 esperaba a que la bola quedara MUERTA a ras de suelo@NL@'\n"
    "    '    para alimentar — entrando con la bola en la palma del profesor@NL@'\n"
    "    '    (alta y quieta) la espera era ETERNA. Ahora el profesor SIRVE YA@NL@'\n"
    "    '    al entrar y un VIGÍA re-sirve si la bola va quieta 1,6 s (en la@NL@'\n"
    "    '    palma, agarrada con grip o perdida).@NL@@NL@'\n"
    "    '  · LOS MODOS, EXPLICADOS CON CALMA (el dueño: «se queda el sonido@NL@'\n"
    "    '    de la bola por debajo, muy molesto… no está bien explicada»):@NL@'\n"
    "    '    (1) bola DORMIDA en los pasos 6/7/8 (adiós al bote infinito de@NL@'\n"
    "    '    fondo — descansa sobre la mesa, sin física, sin sonido); (2) las@NL@'\n"
    "    '    6 tarjetas de la pizarra ganan SU línea de detalle en ámbar; y@NL@'\n"
    "    '    (3) TRES VOCES NUEVAS (tutv8b/8c/9b, ES+EN, banco Piper de la@NL@'\n"
    "    '    casa) que narran partido/supervivencia/multi, campeonatos,@NL@'\n"
    "    '    ranking y entrenar — el paso respira.@NL@@NL@'\n"
    "    '  · ORDEN CANÓNICO DE CAMPEONATOS (el dueño: «me has puesto el@NL@'\n"
    "    '    Salvaje Oeste de primero y sería el tercero: el primero es el de@NL@'\n"
    "    '    Clow, el segundo el de Wizard y el tercero el de forajido»): con@NL@'\n"
    "    '    los manifest en paralelo (r73) el menú ordenaba por LLEGADA de@NL@'\n"
    "    '    la red. Ahora cada entrada guarda SU posición del índice y el@NL@'\n"
    "    '    menú ordena SIEMPRE Clow → Wizard → Forajido → resto.@NL@@NL@'\n"
    "    '  · ABRIR UN CAMPEONATO, IGUAL PARA TODOS (el dueño: «al seleccionar@NL@'\n"
    "    '    este campeonato dentro no desaparece el menú principal… todos@NL@'\n"
    "    '    los campeonatos deben tener el mismo comportamiento»): el cierre@NL@'\n"
    "    '    del menú sube al NÚCLEO (ChampLoader.launch) — locura y magia ya@NL@'\n"
    "    '    no lo hacen en SU start() y el Oeste ya no se queda con él@NL@'\n"
    "    '    abierto; el telón negro de teatro es el mismo para los cinco.@NL@@NL@'\n"
    "    '  · ADIÓS AL BOTE INFINITO (el dueño: «el sonido molesto de la bola@NL@'\n"
    "    '    con el bote infinito») + FPS: ZONA MUERTA del suelo en la física@NL@'\n"
    "    '    — impactos < 0,3 m/s posan la bola SIN evento (bolas aparcadas@NL@'\n"
    "    '    de las salas y restos de rallies ya no repiten thud ni generan@NL@'\n"
    "    '    basura por frame; el rescate bajo el suelo deja de botar y de@NL@'\n"
    "    '    sonar). El golden de física pasa 11/11 intacto. Además, el@NL@'\n"
    "    '    color arcoíris de la piel recicla su THREE.Color (cero@NL@'\n"
    "    '    asignaciones por frame).@NL@@NL@'\n"
    "    '  · Conserva TODO lo anterior (menú al cielo del render, candados@NL@'\n"
    "    '    bien colocados, índice resiliente y telón de teatro r73; saque@NL@'\n"
    "    '    reglamentario del profesor y AJUSTES por subcategorías r71;@NL@'\n"
    "    '    panel sin solapes y telón con espera honesta r72; una sola@NL@'\n"
    "    '    raqueta y golpes honestos r69; la raqueta del rival r68; la@NL@'\n"
    "    '    academia en tus manos r67; sobre la mesa r66; el onboarding@NL@'\n"
    "    '    hablado r65; la estela de poderes, el rival adaptativo y la@NL@'\n"
    "    '    repetición r61; 5 poderes, voz del selector, expresiones,@NL@'\n"
    "    '    passthrough en caliente, SALÓN, PRO CIRCUITO, CCD, CRAZY TV y@NL@'\n"
    "    '    los 5 campeonatos).@NL@@NL@'"
)

GLOBALES = [
    ("V3.6.65-SDK6", "V3.6.66-SDK6"),
    ("3.6.65-SDK6", "3.6.66-SDK6"),
    ("v3665-sdk6", "v3666-sdk6"),
    ("3.6.65", "3.6.66"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.66-SDK6", "frente a V3.6.65-SDK6"),
    ("tras probar V3.6.66", "tras probar V3.6.65"),
]


def main():
    if DEST.exists():
        print("regenerando (release-v3666 ya existía)…")
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
            print(f"  ✓ {f.name}: notas FASE 68 insertadas")
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
