#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.140 · Aplica al NÚCLEO (public/game.html) la megafonía de las
estaciones del Salvaje Oeste:

  (1) VERSION '2.139.0' → '2.140.0' + changelog de la versión (prefijo de
      la línea de changelog, que conserva TODO el histórico).
  (2) 7 átomos nuevos en VOICE_B64 (es) y VOICE_B64_EN (en): mega_salida_dg
      · mega_salida_pd · mega_salida_br · mega_llega_dg · mega_llega_pd ·
      mega_llega_br · mega_oro (OGG Opus 28k mono de la receta Piper).
  (3) 14 entradas en VOICE_FULL (7 es + 7 en) — el texto normalizado de las
      frases i18n del módulo (tren_mega_* con {e} = nombre de la estación)
      debe coincidir EXACTO (réplica de _normVoice: lower + NFD sin
      diacríticos + [^a-z0-9]+ → espacio).

Idempotente: si el marcador ya está, no vuelve a insertar.
"""
import base64
import os
import re
import sys

BASE = "/home/z/my-project"
HTML = f"{BASE}/public/game.html"
OGG_ES = f"{BASE}/scripts/voice/ogg"
OGG_EN = f"{BASE}/scripts/voice/ogg_en"

KEYS = ["mega_salida_dg", "mega_salida_pd", "mega_salida_br",
        "mega_llega_dg", "mega_llega_pd", "mega_llega_br", "mega_oro"]

VOICE_FULL_ES = """    'pasajeros al tren partimos hacia dry gulch': ['mega_salida_dg'],
    'pasajeros al tren partimos hacia perdido': ['mega_salida_pd'],
    'pasajeros al tren partimos hacia bravos': ['mega_salida_br'],
    'en menos de 25 segundos llegaremos a dry gulch': ['mega_llega_dg'],
    'en menos de 25 segundos llegaremos a perdido': ['mega_llega_pd'],
    'en menos de 25 segundos llegaremos a bravos': ['mega_llega_br'],
    'cargamento de oro a buen recaudo': ['mega_oro'],
"""

VOICE_FULL_EN = """    'all aboard we are departing towards dry gulch': ['mega_salida_dg'],
    'all aboard we are departing towards perdido': ['mega_salida_pd'],
    'all aboard we are departing towards bravos': ['mega_salida_br'],
    'in less than 25 seconds we will arrive at dry gulch': ['mega_llega_dg'],
    'in less than 25 seconds we will arrive at perdido': ['mega_llega_pd'],
    'in less than 25 seconds we will arrive at bravos': ['mega_llega_br'],
    'the gold shipment is safe and sound': ['mega_oro'],
"""

CHANGELOG = (
    "const VERSION = '2.140.0';   // v2.140 · OESTE «EL VAGÓN A PUNTO» — 4 observaciones del dueño "
    "en el casco (etapa 4 «ASALTO AL TREN»): (1) BOTES FANTASMA junto a la red («si la pelota bota "
    "en el campo enemigo cerca de la red viene devuelta al jugador como si rebotase contra algo "
    "invisible»): el bote arkanoi de v2.113 tenía su frontera zonaZ en -2,2 y dejaba 60 cm de MESA "
    "RIVAL dentro de la zona del jugador — cualquier bote lento ahí era SECUESTRADO (ápice 1,45 m + "
    "vel.z +0,95 hacia el jugador). FIX: zonaZ = red (-1,6): el bote gestionado sólo vive en el "
    "campo del JUGADOR; en campo enemigo la bola SIGUE SU TRAYECTORIA física (si muere botando, la "
    "recoge el vórtice de siempre — quieta 0,9 s → respawn). (2) LINGOTES APILADOS EN EL SUELO "
    "(«mejor que se apilen a ambos lados del suelo visibles por la cámara… deben estar unos "
    "perfectamente encima de otros»): fuera de la mesa rival — DOS pilas SIMÉTRICAS en el suelo del "
    "vagón junto a la red (x ±1,10…±1,38 · z -1,00…-0,82), el lingote alterna IZQUIERDA/DERECHA y "
    "llena capas de 6 (2 columnas × 3 filas); al completar un plano se apila ENCIMA con la altura "
    "REAL del lingote (medida del prototipo GLB al cargar + 1,5 mm de holgura — nada de offsets "
    "fijos: la 2.ª capa de v2.111 flotaba a +0,095 y DESALINEADA en z) y yaw 0 al aterrizar (antes "
    "giraba ±40°): pilas limpias y legibles. (3) SUELO DEL VAGÓN con la TARIMA del dueño "
    "(room/vagon/suelo.jpg 1296×1678, mapeo 1:1 al plano 6,10×7,90 — tablas transversales a la "
    "marcha): fuera la arena procedural de v2.111. (4) MEGAFONÍA DE ESTACIÓN — voz pregrabada del "
    "banco (misma receta Piper es_ES-davefx/en_US-lessac → OGG Opus 28k) por la vía announce → "
    "voicePlan → speakPlan (WebAudio VR-SAFE, con el CHIME del megáfono y ducking del ambiente): "
    "SALIDAS «Pasajeros al tren, partimos hacia…» [destino]; a los 30 s del final del trayecto «En "
    "menos de 25 segundos llegaremos a…» [estación] (UNA vez por trayecto); ARRIBO CON ORO «¡"
    "Cargamento de oro a buen recaudo!» + PANEL recompensa.png (pop elástico, patrón insignia, se "
    "ve toda la parada); ARRIBO SIN ORO panel forajido_robo.png + LAS RISAS DEL FORAJIDO "
    "(risas_forajido.mp3 del dueño, precargadas al entrar al vagón y con reintento en el step). "
    "FRASES i18n es/en (tren_mega_salida/llega/oro) con los NOMBRES de las estaciones interpolados "
    "(BRAVOS·DRY GULCH·PERDIDO) y 7 ÁTOMOS NUEVOS por idioma (mega_salida/llega_dg·pd·br + "
    "mega_oro) con sus 14 entradas VOICE_FULL — la normalización de los textos del módulo coincide "
    "EXACTA (verificada con la réplica de _normVoice en el QA). NORMAS de la etapa actualizadas: "
    "los lingotes se apilan en el SUELO del vagón. Módulo OESTE v47 (manifest v47). Núcleo: solo "
    "banco de voz + planes + marcador · antes v2.139 · "
)


def atom_entries(ogg_dir, comment):
    lines = [comment]
    for k in KEYS:
        raw = open(os.path.join(ogg_dir, k + ".ogg"), "rb").read()
        b64 = base64.b64encode(raw).decode("ascii")
        assert "</" not in b64
        lines.append(f'  {k}: "{b64}",')
    return "\n".join(lines) + "\n"


def main() -> int:
    html = open(HTML, encoding="utf-8").read()
    if "v2.140 · OESTE «EL VAGÓN A PUNTO»" in html:
        print("ya aplicado — nada que hacer")
        return 0

    # (1) VERSION + changelog
    anchor = "const VERSION = '2.139.0';   // v2.139 · "
    assert html.count(anchor) == 1, f"ancla VERSION: {html.count(anchor)}"
    html = html.replace(anchor, CHANGELOG)

    # (2) átomos en ambos bancos
    for opener, ogg_dir, comment in (
        ("const VOICE_B64 = {\n", OGG_ES,
         "  /* v2.140 · MEGAFONÍA de las estaciones del Oeste (etapa 4): salidas,\n"
         "     llegada a los 30 s y oro a buen recaudo — Piper es_ES-davefx */"),
        ("const VOICE_B64_EN = {\n", OGG_EN,
         "  /* v2.140 · Oeste station PA (en_US-lessac) */"),
    ):
        assert html.count(opener) == 1, f"ancla banco {ogg_dir}"
        html = html.replace(opener, opener + atom_entries(ogg_dir, comment) + "\n")

    # (3) VOICE_FULL es/en
    a_es = "    'bienvenido a crazy ping pong escoge una modalidad de juego': ['bienvenida_modo'],\n"
    a_en = "    'welcome to crazy ping pong choose a game mode': ['bienvenida_modo'],\n"
    assert html.count(a_es) == 1 and html.count(a_en) == 1, "anclas VOICE_FULL"
    html = html.replace(a_es, a_es + VOICE_FULL_ES)
    html = html.replace(a_en, a_en + VOICE_FULL_EN)

    open(HTML, "w", encoding="utf-8").write(html)
    n_mega = html.count("mega_salida_dg")
    print(f"OK · VERSION 2.140.0 · átomos insertados · mega_salida_dg aparece {n_mega} veces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
