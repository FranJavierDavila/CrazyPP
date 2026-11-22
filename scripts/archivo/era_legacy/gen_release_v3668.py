#!/usr/bin/env python3
"""gen_release_v3668 — hereda scripts/release-v3667 → scripts/release-v3668
e inserta las NOTAS de la FASE 70 «EL PULSO CRAZY» en build_zip.py.

Idempotente: si release-v3668 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3667"
DEST = RAIZ / "scripts" / "release-v3668"

BZ = DEST / "build_zip.py"

BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 69 — TODO ENCAJA: el informe del\\n'"
BLOQUE_VIEJO_FIN = "    '    los 5 campeonatos).\\n\\n'"

BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 70 — EL PULSO CRAZY: la aprobación\\n'
    'del dueño — «me fío de tu criterio… los 4 puntos con el estado\\n'
    'actual como punto seguro de restauración. Necesito RAZONES PARA\\n'
    'VOLVER CADA DÍA… sorpréndeme con algo único adaptado a nuestro\\n'
    'juego que haga que los jugadores estén dispuestos a pagar»)\\n\\n'
    'Novedades de esta versión (frente a V3.6.67-SDK6):\\n\\n'
    '  · EL PULSO CRAZY (punto 1 + la petición nueva): el latido diario\\n'
    '    de la academia, en el hub de PRO TRAINING — RETO DEL DÍA\\n'
    '    determinista por fecha LOCAL del visor (el mismo duelo para\\n'
    '    toda la academia, cambia a medianoche) sobre los 9 modos que\\n'
    '    ya existen, con campeón del día de la casa (Clow, Wizard,\\n'
    '    Forajido, Orbital, Neón) y frase de la casa. RACHA DE\\n'
    '    ASISTENCIA: días consecutivos que se enfrían si fallas uno\\n'
    '    (effStreak), recompensa 40 + 5×min(racha−1, 7) + 15 si vences\\n'
    '    a TU FANTASMA (tu mejor marca del modo del día como rival),\\n'
    '    cobro ÚNICO por día y poda honesta de 90 días.\\n\\n'
    '  · PIELES DE ASISTENCIA — la colección que los puntos NO compran\\n'
    '    (min:Infinity): NEÓN al llegar a 7 días de racha, FANTASMA a\\n'
    '    14 y CAMPEÓN (oro vivo animado) a 30. Fila PROPIA bajo el\\n'
    '    panel del Pulso, con candado en el hueco de la miniatura y el\\n'
    '    hito legible debajo. Texturas con los builders de la casa\\n'
    '    (buildPipTexture): cero shaders nuevos, cero coste por frame.\\n\\n'
    '  · EL INFORME DEL PROFESOR (punto 2 — entrenador IA con la\\n'
    '    telemetría existente): un consejo técnico diario generado de\\n'
    '    los datos REALES del jugador (mejor marca, precisión y\\n'
    '    estrellas del modo del día), en ES y EN, dentro del propio\\n'
    '    panel. Los retos asíncronos con fantasmas de OTROS jugadores\\n'
    '    (punto 3) quedan declarados para una futura ronda: hoy el\\n'
    '    fantasma es el tuyo, y es real. El panel es canvas estático\\n'
    '    del menú (punto 4: cero coste por frame en juego) y GAMF()=0\\n'
    '    desactiva el Pulso por completo (flujo legacy intacto).\\n\\n'
    '  · PUNTO SEGURO DE RESTAURACIÓN: tag v3.6.67-r75-baseline sobre\\n'
    '    la producción V3.6.67-SDK6 (blob da947845) antes de tocar una\\n'
    '    sola línea. QA: capa BK qa_r76_v3668 (93/0: agujas, contadores\\n'
    '    y JUEGO REAL — determinismo del plan, cobro único, fantasma,\\n'
    '    racha fría, hitos 7/14/30 con las tres pieles, informe del\\n'
    '    profesor con datos, panel vivo dentro de bounds y captura).\\n\\n'
    '  · Conserva TODO lo anterior (r75: los modos todo encaja;\\n'
    '    r74: B en el Pro Training, menú sobre el cartel EMPEZAR, glow\\n'
    '    que sigue la mano, devoluciones sin atascos, modos con calma\\n'
    '    y sin bola sonora, orden Clow→Wizard→Forajido, telón común y\\n'
    '    zona muerta del suelo; r73: menú al cielo del render,\\n'
    '    candados bien colocados, índice resiliente y telón de teatro;\\n'
    '    r72: panel sin solapes y telón con espera honesta; r71: saque\\n'
    '    reglamentario del profesor y AJUSTES por subcategorías;\\n'
    '    r69-r67: una sola raqueta, golpes honestos, academia en tus\\n'
    '    manos; r66-r65: sobre la mesa, onboarding hablado; r61:\\n'
    '    estela de poderes, rival adaptativo y repetición; 5 poderes,\\n'
    '    voz del selector, expresiones, passthrough en caliente,\\n'
    '    SALÓN, PRO CIRCUITO, CCD, CRAZY TV y los 5 campeonatos).\\n\\n'
"""


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        print("✗ marcadores del bloque de notas no encontrados")
        return 1
    nuevo = txt[:i] + BLOQUE_NUEVO + txt[j + len(BLOQUE_VIEJO_FIN):]
    BZ.write_text(nuevo, encoding="utf-8")
    # el directorio heredado NO debe quedar referenciado por el nuevo
    txt2 = BZ.read_text(encoding="utf-8")
    if "FASE 69" in txt2.split("Hashes SHA256")[0]:
        print("✗ resto de notas viejas en el bloque")
        return 1
    print("✓ release-v3668 creado (notas FASE 70 «EL PULSO CRAZY»)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
