#!/usr/bin/env python3
"""gen_release_v3674 — hereda scripts/release-v3672 → scripts/release-v3674
e inserta las NOTAS de la FASE 75 «SESENTA SEGUROS» en build_zip.py.

Idempotente: si release-v3674 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3672"
DEST = RAIZ / "scripts" / "release-v3674"

BZ = DEST / "build_zip.py"

# Bloque de notas FASE 74 (r80) que sale entero
BLOQUE_VIEJO_INI = ("    'Rama    : main · SDK6 (FASE 74 — EL RETO DIARIO EN LA PUERTA: informe\\n'")
BLOQUE_VIEJO_FIN = ("    '    mismas dimensiones); en entrenamiento normal TODO queda igual. La\\n'\n"
                    "    '    dificultad irá subiendo con el tiempo.\\n\\n'")

# Bloque nuevo FASE 75 (r81)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 75 — SESENTA SEGUROS: «debemos tener una\\n'
    'herramienta para poder calibrar los FPS según el modelo de gafas… para\\n'
    'unas Oculus 2 las partidas van muy lentas y la experiencia es muy mala…\\n'
    'un autocalibrador que asegure al menos 60 FPS seguros en cualquier\\n'
    'dispositivo. Por cierto en modo de multijugador no está calibrando bien\\n'
    'los movimientos entre los dos jugadores, no deja sacar ni jugar. Puedes\\n'
    'simular una conexión realista entre dos usuarios para verificar que\\n'
    'funciona»))\\n\\n'
    'Novedades de esta versión (frente a V3.6.72-SDK6):\\n\\n'
    '  · AUTOCALIBRADOR DE FPS (PERF GOVERNOR): perfil POR CASCO detectado\\n'
    '    por GPU real — Quest 3 (Adreno 740) mantiene su 1.40×/0.50/90-120\\n'
    '    de siempre; Quest 2 (Adreno 650) nace FLUIDO (1.05×/0.65/72 Hz);\\n'
    '    genérico 1.20×. SONDA de calibración al entrar en VR (rondas de\\n'
    '    2,8 s hasta sostener ≥63 FPS de media con peor segundo ≥55) y\\n'
    '    GOBERNADOR continuo (baja con voz si el promedio cae, recupera si\\n'
    '    sobra margen; foveation y tasa objetivo EN VIVO, escala para la\\n'
    '    próxima sesión). Todo persiste por casco y se ve en AJUSTES ›\\n'
    '    RENDIMIENTO (FPS en vivo, AUTO/manual y RECALIBRAR).\\n\\n'
    '  · EL MULTIJUGADOR YA SE PUEDE JUGAR — cuatro defectos de fondo\\n'
    '    cazados con el nuevo DUELO SIMULADO: (1) DOBLE ESPEJO: el receptor\\n'
    '    volvía a aplicar la involución que ya viajaba en el paquete\\n'
    '    (R∘R = identidad) y la bola y la pala del rival aterrizaban en el\\n'
    '    lado CONTRARIO de la mesa desde v2.19 — ahora UN solo espejo por\\n'
    '    camino; (2) VALIDADOR: comparaba el golpe con la pose cruda del\\n'
    '    rival (marcos distintos → TODO golpe remoto rechazado: «no deja\\n'
    '    sacar ni jugar») — ahora mismo marco y mismo instante\\n'
    '    (JitterBuf.nearest), y el lanzamiento mira la mano LIBRE; (3) los\\n'
    '    CLAIM/ACK usaban rules.rallyId (no existía: undefined) y el\\n'
    '    marcador se congelaba tras el primer punto — identidad real:\\n'
    '    rallySeq; (4) el glue indexaba un THREE.Vector3 (p[0] = undefined\\n'
    '    → bola NaN). Además: la volea la juzga el árbitro DE ESA MITAD\\n'
    '    (spec §7), la bola HELD del rival nace oculta, el lanzamiento\\n'
    '    libera el hold y los ICE tempranos se encolan (redes reales).\\n\\n'
    '  · DUELO SIMULADO (la herramienta del dueño): dos páginas reales\\n'
    '    conectadas por la señalización PeerJS REAL con NETSIM (35 ms ± 12\\n'
    '    ms, 2 % de pérdida) SACAN, INTERCAMBIAN y PUNTÚAN con marcador\\n'
    '    espejado idéntico y 0 rechazos — QA capa BP, 135 comprobaciones.\\n\\n'
"""


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    # 1 · identidad de la release: v3672 → v3674 / V3.6.72 → V3.6.74
    txt = txt.replace("V3.6.72-SDK6", "V3.6.74-SDK6")
    txt = txt.replace("3.6.72-SDK6", "3.6.74-SDK6")   # guards contra game_src
    txt = txt.replace("v3672-sdk6", "v3674-sdk6")
    txt = txt.replace("release-v3672", "release-v3674")
    txt = txt.replace("staging-v3672", "staging-v3674")
    txt = txt.replace('grep -c "3.6.72"', 'grep -c "3.6.74"')
    txt = txt.replace("menciones 3.6.72", "menciones 3.6.74")
    txt = txt.replace("no es el v3672", "no es el v3674")
    txt = txt.replace("n3672 = int", "n3673 = int")
    txt = txt.replace("{n3672}", "{n3673}")
    txt = txt.replace("if n3672 < 4:", "if n3673 < 4:")

    # 2 · notas: bloque FASE 74 → bloque FASE 75
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 74 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + BLOQUE_NUEVO + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.74-SDK6'" in txt, "guard VERSION"
    assert "V3.6.74-SDK6" in txt, "badge"
    assert "FASE 75" in txt, "notas FASE 75"
    assert "FASE 74" not in txt, "quedan notas FASE 74"
    print("✓ release-v3674 creada (notas FASE 75, guards V3.6.74-SDK6)")


if __name__ == "__main__":
    main()
