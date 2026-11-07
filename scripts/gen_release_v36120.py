#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.120-SDK6 (r25).
Crea scripts/release-v36120/ a partir de scripts/release-v36119/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 122
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36120 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36120.py
    python3 scripts/release-v36120/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36119"
DEST = RAIZ / "scripts" / "release-v36120"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 122 — SÚPER RED + SÚPER ELECTRICIDAD +",
    "BOLA BLINDADA: dos poderes nuevos, cortina en etapas 2/4 y la bola",
    "online siempre en poder del sacador).",
    "  · 1 · CORTINA EN ETAPAS 2 Y 4 (informe del dueño: «los superpoderes",
    "    de Pala del jugador nunca deben aparecer en las etapas 2 y 4 de",
    "    los campeonatos — pruebas de habilidad»). Todos los módulos",
    "    exponen testActive(): el núcleo corta el GATILLO (megaEnabled),",
    "    las CONCESIONES (_megaCharge) y cuelga la CORTINA cada frame",
    "    (_poderesCortina): ventanas, FX, icono y radio de golpeo fuera.",
    "    Las cargas no gastadas de un duelo siguen siendo del jugador.",
    "  · 2 · SÚPER RED (SuperPala_Red.png del dueño, 6.º poder; spec",
    "    literal): «hace crecer la altura de la red el doble del valor",
    "    actual… dura activo 10 segundos». La red MUTA DIMS.netTopY ×2 EN",
    "    VIVO (física c04/c05, IA y saque la leen — lección r95: una sola",
    "    fuente de verdad) y el visual se re-acomoda al vuelo (plano,",
    "    cinta y postes, patrón relayoutMesa r95; altura de nacimiento",
    "    registrada UNA vez — idempotente). Restauración EXACTA al acabar",
    "    (fin natural, salida del campeonato, cortina o startMatch).",
    "  · 3 · SÚPER ELECTRICIDAD (SuperPala_Electrica.png del dueño, 7.º",
    "    poder; spec literal): tormenta de 10 s sobre el campo rival —",
    "    «nubes a metro y medio sobre la mesa del rival que descargan",
    "    rayos… gran estruendo sonoro y destello… la luz de la escena se",
    "    vuelve bastante oscura (casi parece de noche)… si alguno de los",
    "    rayos intercepta la bola del rival, la rompe en múltiples",
    "    pedacitos negros y pierde el punto».",
    "      · NUBES: 2 sprites procedurales a tableTopY+1,5 m sobre la",
    "        mitad del rival, vaivén vivo, entran/salen con la tormenta.",
    "      · RAYOS: pool de 3 líneas de 9 puntos (cero asignaciones por",
    "        descarga), cadencia ~1,15 s con jitter, destello de 0,25 s.",
    "      · NOCHE: hemi/dir/spot/env y fondo-niebla bajan a 0,18 sobre",
    "        los valores VIVOS capturados (tema o decorado del campeo-",
    "        nato) y vuelven EXACTOS al disiparse. CERO PointLights",
    "        nuevos (lección v2.92: recompilar shaders congela el frame).",
    "      · TRUENOS: 2 MP3 sintetizados (ffmpeg brown noise) alternos,",
    "        fetch+decode+cache y precaliente sin sonar.",
    "      · COLISIÓN RÁPIDA: distancia punto-segmento nube→mesa contra",
    "        la bola (un hipot, cero asignaciones; radio 0,17 m + bola).",
    "        Si intercepta: 10 pedacitos negros (tetraedros, pool de 12,",
    "        gravedad visual propia), la bola se OCULTA 0,9 s (el",
    "        integrador ni se entera) y el punto es del jugador por el",
    "        cauce del árbitro (applyPoint causa elec).",
    "  · 4 · CONTROL TOTAL DE LA BOLA ONLINE (_bolaGuard; informe del",
    "    dueño: «en algún saque no se ve la bola hasta que se lanza… al",
    "    iniciar una segunda partida vemos la bola en la mano del rival",
    "    cuando debería estar en la nuestra, o incluso no vemos la bola",
    "    ninguno»). La propiedad se RE-AFIRMA CADA FRAME desde el árbitro",
    "    (rules.server determinista por marcador, idéntico en ambos",
    "    extremos): MI SAQUE = bola en MI mano libre (o punto de saque en",
    "    escritorio, donde antes quedaba congelada) también durante la",
    "    cuenta atrás 3·2·1; SAQUE DEL RIVAL = su mano libre con pose",
    "    fresca (<500 ms) o punto de saque reglamentario si se apaga",
    "    (>0,6 s) — JAMÁS invisible; FSM idle en saque re-arma HELD (la",
    "    causa raíz de «no la vemos ninguno»); RALLYE = siempre visible +",
    "    guardia anti-NaN/anti-mundo (bola perdida vuelve jugable a mi",
    "    mitad). Telemetría bola_guard 1/5 s. c09 SIN cambios de códec.",
    "  · 5 · CONCESIÓN: los DOS poderes entran en la bolsa ALEATORIA de",
    "    PODERES_PALA (cada 20 toques del rally, tope ×3 — reglas de la",
    "    casa intactas). Iconos PNG del dueño cuantizados (19/26 KB),",
    "    voces ES/EN espeak embebidas, reservas de icono, voces del",
    "    selector, precaliente sin lag, firma de estela azul.",
    "  · 6 · I18N: 7 claves nuevas ES/EN (poder_red/elec, arc_red/elec_go",
    "    y _fin, cause_elec).",
    "  · FÍSICA INTACTA (garantía del dueño): c04/c05 SIN una línea nueva",
    "    (diff vacío contra la r24); c09 intacto; la bola rota sólo se",
    "    oculta — el punto lo aplica el árbitro.",
    "  · TEST NUEVO: test_r25_sup_bola_v36120 (150/0) — cortina, registro",
    "    de 7 poderes, red ×2 con restauración, tormenta completa, assets",
    "    embebidos con cabeceras reales, guardián de la bola, i18n doble,",
    "    garantías de física/códec y sellos. Regresión r24 89/0, r23 81/0",
    "    y r21 63/0. QA A-D verde (presupuesto re-anclado: +185 KB de",
    "    assets del dueño). bump BYTE-EXACTO (10.972.943 B · golden",
    "    db4ad92b…).",
    "  SE CONSERVA TODO: skins r21, P4.1/P4.2, M-RED3, M7e, CRAZY LINK",
    "    v2, ELO, matchmaking, retos, superpoderes r23/r24, hall cabaña.",
    "  · sellada a",
    "  3.6.120",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36119", "release-v36120"),
    ("staging-v36119", "staging-v36120"),
    ("V3.6.119-SDK6", "V3.6.120-SDK6"),
    ("3.6.119-SDK6", "3.6.120-SDK6"),
    ("v36119-sdk6", "v36120-sdk6"),
    ("v36119", "v36120"),
    ("3.6.119", "3.6.120"),
    ("fase 121", "fase 122"),
    ("FASE 121", "FASE 122"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r24 a FASE 122/3.6.120 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 122 — SPIN REALISTA +"
FIN_MARCADOR = "'  3.6.120" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.120-SDK6 lista: SPIN REALISTA (ganancia ×3.2 + costura y marca CRAZY en las planas) + HALL CABAÑA (el arte del dueño, liberado con 10 victorias, viaja por hp.hv).')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.120-SDK6 lista: SÚPER RED (red ×2 · 10 s) + SÚPER ELECTRICIDAD (tormenta sobre el rival) + CORTINA en etapas 2/4 + BOLA BLINDADA online (_bolaGuard).')"


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
        # bloque de notas → FASE 122 (sustitución EXACTA, lección r24:
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
    print(f"\nrelease-v36120 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36120/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
