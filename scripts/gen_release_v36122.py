#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.122-SDK6 (r26b).
Crea scripts/release-v36122/ a partir de scripts/release-v36121/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 124
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36122 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36122.py
    python3 scripts/release-v36122/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36121"
DEST = RAIZ / "scripts" / "release-v36122"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 124 — BOLA ATRACTORA + 3 SUPERPODERES",
    "NUEVOS + 3 HALL NUEVOS POR HITOS: informe del dueño tras la r26 —",
    "la tormenta caza la bola y el juego estrena 3 poderes y 3 salas).",
    "  · 1 · BOLA ATRACTORA (dueño: la tormenta «tiene que aumentar la",
    "    posibilidad de impactar a la bola que actuará como atractora de",
    "    los rayos de la tormenta incrementando en un 25 % la posibilidad",
    "    de alcanzar la bola y destruirla»). UN rayo de cada CUATRO",
    "    (ELEC_ATRAE_P = 0.25) BUSCA la bola cuando juega sobre la mitad",
    "    del rival: nace en la niebla más cercana, TERMINA EN ELLA, se",
    "    TIÑE de violeta (ELEC_ATRAE_COL, material individual del pool)",
    "    y va casi RECTO (jitter 0.09→0.018): se la ve curvarse hacia su",
    "    blanco. Chispas violetas en el impacto. El resto de rayos cae",
    "    al azar con su colisión de siempre (0,17 m + bola, punto por el",
    "    árbitro INTACTOS). Bola en tránsito de portal jamás cazada.",
    "  · 2 · SÚPER FÉNIX (8.º poder; dueño: «otros 3 superpoderes de",
    "    pala muy llamativos… icono circular… ventaja de juego…",
    "    duraciones sobre 10 segundos… SuperPoder de XXXX»). LA BOLA DE",
    "    FUEGO: mis golpes válidos salen con +18 % de rapidez (FENIX_MUL,",
    "    tope 26 m/s del validador §12, el techo que ya respetaba el",
    "    «fuego» de DUELOS LOCOS), halo de llama ADITIVO pegado a la",
    "    bola (gradiente radial que respira), ascuas naranjas del pool",
    "    en cada golpe y estela naranja (TRAIL_PODER.fenix).",
    "  · 3 · SÚPER CRONO (9.º poder). EL TIEMPO LENTO: la bola vuela al",
    "    62 % (CRONO_F) con rampa suave de entrada/salida de 0,4 s y",
    "    RESTAURACIÓN EXACTA de la rapidez al cerrar (delta relativo",
    "    entre frames; la cortina de etapas 2/4 restaura también). Tres",
    "    anillos de reloj plata-cian orbitan la bola. Sin escala en",
    "    online (nadie desincroniza).",
    "  · 4 · SÚPER HIELO (10.º poder). PALA RIVAL CONGELADA: 3 ráfagas",
    "    de 1,6 s (arranques 1.0/4.2/7.4 s) dejan la IA sin moverse —",
    "    ai.update SALTADO durante la ráfaga (y el rival 2 en dobles).",
    "    Cascarón de hielo facetado con aristas cristalinas + 12 copos",
    "    (LCG semillado) sobre la pala rival; CRACK sonoro en cada",
    "    ráfaga. Los SAQUES del rival JAMÁS se congelan (sólo rally).",
    "    Los 3 poderes: ventanas de 10 s (patrón red/elec: reloj único,",
    "    blips 3·2·1, refresco honesto, cortina, precaliente de voces y",
    "    FX), insignia circular 256×256 y voces ES/EN embebidas",
    "    (espeak-ng → MP3; cero red, offline en el Quest).",
    "  · 5 · 3 HALL NUEVOS POR HITOS (dueño: «otros 3 diseños de Hall",
    "    nuevos bien cuidados para mapear… desbloqueos por hitos",
    "    conseguidos»): SALÓN NEÓN ARCADE (synthwave: recreativas,",
    "    rejillas de neón, CRTs; hito: un rally de 20 golpes —",
    "    bestRally≥20), OBSERVATORIO ESTELAR (paneles, ojos de buey, la",
    "    Tierra al ventanal; hito: ELO 1100) y DOJO ZEN (shoji,",
    "    tokonoma con ensō, tatami, cerezos; hito: 5 saques directos —",
    "    aces≥5). Arte 100 % PROCEDURAL con las MISMAS fichas y",
    "    proporciones EXACTAS de los planos (frente/fondo 1849×864 ·",
    "    laterales 2395×864 · suelo/techo 1296×1678): cero bytes nuevos",
    "    en el bundle, fichas nuevas en assets/hall/<id>/. Catálogo de",
    "    5 variantes en salahall (rejilla de 3 columnas, patrón",
    "    salamesa/salabola) + candados con texto de hito + hints.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 (física), c07/c08",
    "    (sala/hall render), c09 (códec) y c10 SIN una línea nueva (diff",
    "    vacío contra la r26); cero PointLights nuevos (lección v2.92);",
    "    cero asignaciones por frame (pools reciclados).",
    "  · TEST NUEVO: test_r26b_sorpresa_v36122 (158/0) — atractoraa,",
    "    los 3 poderes, I18N, halls (dimensiones EXACTAS verificadas",
    "    leyendo el SOF del JPEG) y garantías. Regresión r26 109/0",
    "    (chispas y garantía c02 re-ancladas: ahora lleva los 3 halls),",
    "    r25 150/0 (chispas re-ancladas: color por modo del rayo),",
    "    r24 89/0 (fila→rejilla y 2→5 variantes re-ancladas), r23 81/0",
    "    y r21 63/0. bump BYTE-EXACTO (11.174.354 B · golden fd9d9bad…).",
    "  SE CONSERVA TODO: niebla densa y ráfagas r26, barrera eléctrica,",
    "    skins r21, hall cabaña, cortina etapas 2/4, _bolaGuard, P4,",
    "    CRAZY LINK v2, ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.122",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36121", "release-v36122"),
    ("staging-v36121", "staging-v36122"),
    ("V3.6.121-SDK6", "V3.6.122-SDK6"),
    ("3.6.121-SDK6", "3.6.122-SDK6"),
    ("v36121-sdk6", "v36122-sdk6"),
    ("v36121", "v36122"),
    ("3.6.121", "3.6.122"),
    ("fase 123", "fase 124"),
    ("FASE 123", "FASE 124"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r26 a FASE 124/3.6.122 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 124 — NIEBLA DENSA +"
FIN_MARCADOR = "'  3.6.122" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.122-SDK6 lista: NIEBLA DENSA (14 puffs que hierve y se ilumina) + RÁFAGAS ≈35 rayos + BARRERA ELÉCTRICA en la SÚPER RED.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.122-SDK6 lista: BOLA ATRACTORA (1 de cada 4 rayos la buscan) + SÚPER FÉNIX/CRONO/HIELO + HALLS NEÓN/OBSERVATORIO/DOJO por hitos.')"


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    for f in sorted(DEST.iterdir()):
        if not f.is_file():
            continue
        txt = f.read_text(encoding='utf-8')
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        # bloque de notas → FASE 124 (sustitución EXACTA, lección r24:
        # sin conservar la comilla de cierre del marcador FIN)
        i = txt.find(INI_MARCADOR)
        j = txt.find(FIN_MARCADOR, i) if i >= 0 else -1
        if i >= 0 and j >= 0:
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR):]
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f"\nrelease-v36122 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36122/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
