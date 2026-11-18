#!/usr/bin/env python3
"""gen_release_v3675 — hereda scripts/release-v3674 → scripts/release-v3675
e inserta las NOTAS de la FASE 77 «LA PALA AL MILÍMETRO» en build_zip.py.

Idempotente: si release-v3675 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3674"
DEST = RAIZ / "scripts" / "release-v3675"

BZ = DEST / "build_zip.py"

# Bloque de notas FASE 76 (r82) que sale entero
BLOQUE_VIEJO_INI = ("    'Rama    : main · SDK6 (FASE 76 — AL MILÍMETRO: «sigo sin poder jugar\\n'")
BLOQUE_VIEJO_FIN = ("    '    espejado idéntico y 0 rechazos del validador (capa BQ).\\n\\n'")

# Bloque nuevo FASE 77 (r83)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 77 — LA PALA AL MILÍMETRO: «Dentro del Pro\\n'
    'Training tenemos el ajuste de la posición de la pala, pero no tiene\\n'
    'sentido ahí, así que vamos a moverlo al apartado de Ajustes y crear un\\n'
    'subapartado que nos de acceso a la configuración de la pala (botón\\n'
    'bonito y colorido como el resto de la interface y con su iconito\\n'
    'correspondiente)… forzando a que cuando entramos en ajuste de pala\\n'
    'siempre se active el passthrow para poder ver nuestros mandos reales…\\n'
    '(pasar a passthrow debe ser inmediato sin salir de la pantalla de\\n'
    'configuración). Si esto no fuese posible, entonces visualizaríamos la\\n'
    'réplica de los mandos colocándolos perfectamente alineados y\\n'
    'coincidentes con los reales… me falta poder girar en el eje Z y mover\\n'
    'en el eje Z… Igual visualmente se pueden representar los ejes locales\\n'
    'sobre la pala y dibujar claramente visibles sobre los mismos una\\n'
    'flecha con el desplazamiento o giro que estamos realizando… La\\n'
    'guardamos con un nombre y esa configuración queda permanente\\n'
    'almacenada en nuestro dispositivo… al salir se recupera la visión\\n'
    'anterior del Hall eliminado los elementos o modos usados»))\\n\\n'
    'Novedades de esta versión (frente a V3.6.74-SDK6):\\n\\n'
    '  · AJUSTES › PALA (7.ª categoría, botón rosa con su icono de pala):\\n'
    '    la subpágina da acceso a AJUSTAR LA PALA AHORA, GUARDAR ESTE\\n'
    '    AGARRE, VOLVER AL AGARRE NATURAL y la lista de agarres guardados\\n'
    '    (CARGAR / Quitar). La tarjeta del Pro Training se MUDA aquí\\n'
    '    (adiós «POSICIÓN DE LA PALA» dentro de ENTRENAR).\\n\\n'
    '  · MODO DE AJUSTE AL MILÍMETRO (AJUSTES › PALA › AJUSTAR LA PALA EN\\n'
    '    VR): PASSTHROUGH INMEDIATO en caliente (_pstAplicar — la sesión\\n'
    '    immersive-ar no se cierra: ni un frame de web, «sin salir de la\\n'
    '    pantalla»), gizmo de EJES LOCALES RGB sobre la montura de la pala\\n'
    '    con LA FLECHA DEL AJUSTE por eje (raíl + flecha que viaja con el\\n'
    '    valor VIVO: dirección = signo, magnitud = distancia) y panel\\n'
    '    FRONTAL elevado que sigue a la cabeza (por encima de la vista, sin\\n'
    '    pisar la pala) con barras de color por eje (X rojo · Y verde · Z\\n'
    '    azul), valores en vivo (mm y grados) y chip PASSTHROUGH/RÉPLICA.\\n\\n'
    '  · RÉPLICAS GLB DE LOS MANDOS: los mismos modelos Touch Plus del\\n'
    '    tutorial, anclados a los grips — coinciden 1:1 con los mandos\\n'
    '    reales por construcción; sólo viven SI el passthrough no está\\n'
    '    disponible (en Quest 3 se ve el mando REAL debajo).\\n\\n'
    '  · EJES Z DIRECTOS: CLICK del stick derecho conmuta GIRO X·Y ⇄ Z\\n'
    '    (rodar) y CLICK del izquierdo MOV X·Y ⇄ Z (acercar/alejar); los\\n'
    '    atajos GRIP de siempre se conservan. AGARRES con nombre\\n'
    '    PERMANENTES en el dispositivo (ppxr_grips_v1): A guarda, X\\n'
    '    vuelve al natural, el menú carga y borra.\\n\\n'
    '  · SALIDAS LIMPIAS: B abre el MENÚ COMÚN (con Volver al Hall dentro)\\n'
    '    e Y sale directo; al salir se recupera la visión anterior del Hall\\n'
    '    SIN arrastrar nada (gizmo, réplicas, panel, passthrough y\\n'
    '    visibilidades restaurados; al quitar el casco también).\\n\\n'
    '  · Conserva TODO lo anterior (r82: multijugador al milímetro con\\n'
    '    batería en paralelo; r81: autocalibrador de FPS; r80: Reto\\n'
    '    Diario en la puerta; r79-r71: CRAZY LINK v2, academia en tus\\n'
    '    manos, AJUSTES por subcategorías, passthrough en caliente; 5\\n'
    '    campeonatos, 5 poderes, CCD, CRAZY TV y el Hall Of Fame).\\n\\n'
"""


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    # 1 · identidad de la release: v3674 → v3675 / V3.6.74 → V3.6.75
    txt = txt.replace("V3.6.74-SDK6", "V3.6.75-SDK6")
    txt = txt.replace("3.6.74-SDK6", "3.6.75-SDK6")   # guards contra game_src
    txt = txt.replace("v3674-sdk6", "v3675-sdk6")
    txt = txt.replace("release-v3674", "release-v3675")
    txt = txt.replace("staging-v3674", "staging-v3675")
    txt = txt.replace('grep -c "3.6.74"', 'grep -c "3.6.75"')
    txt = txt.replace("menciones 3.6.74", "menciones 3.6.75")
    txt = txt.replace("no es el v3674", "no es el v3675")
    txt = txt.replace("n3674 = int", "n3675 = int")
    txt = txt.replace("{n3674}", "{n3675}")
    txt = txt.replace("if n3674 < 4:", "if n3675 < 4:")

    # 2 · notas: bloque FASE 76 → bloque FASE 77
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 76 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + BLOQUE_NUEVO + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.75-SDK6'" in txt, "guard VERSION"
    assert "V3.6.75-SDK6" in txt, "badge"
    assert "FASE 77" in txt, "notas FASE 77"
    assert "FASE 76" not in txt, "quedan notas FASE 76"
    print("✓ release-v3675 creada (notas FASE 77, guards V3.6.75-SDK6)")


if __name__ == "__main__":
    main()
