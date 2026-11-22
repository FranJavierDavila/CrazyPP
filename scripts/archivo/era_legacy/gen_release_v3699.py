#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3699 — hereda scripts/release-v3698 → scripts/release-v3699
e inserta las NOTAS de la FASE 101 «M3 PWA INSTALABLE (r109)».

Ronda 109: segundo hito del roadmap MEJORAS.md. El juego de GitHub Pages
se vuelve APP instalable (manifest + service worker + iconos de la casa +
portada instaladora), con el BUMP gobernando la caché (4.º sello físico:
const CACHE de sw.js).

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas. Idempotente (regenera desde v3698).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3698"
DEST = RAIZ / "scripts" / "release-v3699"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 100 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada ya dice 3.6.99)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 100 — M1 GAME FEEL · HÁPTICAS CALIBRADAS" + NL + "'"
BLOQUE_VIEJO_FIN = " · sellada a 3.6.99" + NL + "'"

# líneas de texto PLANO de las notas FASE 101 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 101 — M3 PWA INSTALABLE",
    "    '(r109).",
    "    'Segundo hito del roadmap MEJORAS.md: la web oficial del juego se",
    "    'vuelve APP instalable — icono en el casco, arranque sin teclear URL",
    "    'y actualizaciones automáticas. Adiós al ?v= y a la caché del Quest.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.98-SDK6):",
    "    '",
    "    '  · manifest.webmanifest (fullscreen landscape con el emblema de la",
    "    '    casa como icono 192/512 + variante maskable) y SERVICE WORKER",
    "    '    sw.js: game.html stale-while-revalidate, campeonatos/UGC/",
    "    '    PAGES-VERSION network-first, assets cache-first con relleno",
    "    '    bajo demanda, purga de cachés viejas en activate.",
    "    '",
    "    '  · EL BUMP GOBIERNA LA CACHÉ: const CACHE = crazypp-v<versión> es",
    "    '    el 4.º SELLO FÍSICO (bump_version.py lo parchea + qa_version.py",
    "    '    lo verifica) — cada versión nueva invalida la caché sola.",
    "    '",
    "    '  · PORTADA INSTALADORA: botón «📲 INSTALAR EN EL CASCO» en el pie",
    "    '    (diálogo nativo beforeinstallprompt si el navegador lo dispara,",
    "    '    caminito manual de 2 toques si no), detección de standalone (el",
    "    '    botón se oculta dentro de la app ya instalada) y telemetría",
    "    '    anónima pwa_standalone/pwa_prompt/pwa_installed/pwa_manual_hint.",
    "    '",
    "    '  · Hub /descargas con la guía PWA · deploy_pages publica manifest +",
    "    '    sw.js + iconos en /CrazyPP/ · i18n ES/EN · cero cambios de",
    "    '    gameplay (los arneses M2a quedan intactos).",
    "    '",
    "    '  QA r109 en verde (agujas estáticas + juego vivo: SW registrado,",
    "    '  manifest servido, iconos verificados con PIL, botón y toasts en",
    "    '  la portada, regresión r106/r105/r104/r62 intacta) · sellada a 3.6.99",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3699 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.99.
    for viejo, nuevo in (("V3.6.98-SDK6", "V3.6.99-SDK6"),
                         ("3.6.98-SDK6", "3.6.99-SDK6"),
                         ("v3698-sdk6", "v3699-sdk6"),
                         ("3.6.98", "3.6.99"),
                         ("V3.6.98", "V3.6.99"),
                         ("v3698", "v3699"),
                         ("release-v3698", "release-v3699"),
                         ("staging-v3698", "staging-v3699")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 100 → FASE 101 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 100 → FASE 101 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 100 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
