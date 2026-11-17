#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.139 · BIENVENIDA HABLADA — aplica los cambios en public/game.html:

  1) VERSION 2.138.0 → 2.139.0 + entrada de changelog
  2) VOICE_B64 (es):  átomo nuevo bienvenida_modo (grafía fonética «Kreisi»,
     verificada por ASR — el literal sonaba «cricket»)
  3) VOICE_B64_EN (en): átomo nuevo bienvenida_modo
  4) VOICE_FULL es/en: frase completa → ['bienvenida_modo']
  5) i18n es/en: clave nueva welcome_menu
  6) onSessionStart: el anuncio de los 1400 ms pasa a ser T('welcome_menu')
     (el menú principal está abierto en ese momento)

Idempotente: si 'bienvenida_modo' ya está en el HTML, no repite inserciones.
"""
import re
import sys

GAME = "/home/z/my-project/public/game.html"
OGG_ES = "/home/z/my-project/scripts/voice/ogg/bienvenida_modo_fon.ogg"
OGG_EN = "/home/z/my-project/scripts/voice/ogg_en/bienvenida_modo_en.ogg"

html = open(GAME, encoding="utf-8").read()
orig = html


def b64(path: str) -> str:
    import base64
    raw = open(path, "rb").read()
    s = base64.b64encode(raw).decode("ascii")
    assert "</" not in s, "base64 contiene </"
    return s


B64_ES, B64_EN = b64(OGG_ES), b64(OGG_EN)

# ---------------------------------------------------------------- 1) VERSION
if "const VERSION = '2.139.0'" not in html:
    OLD_V = "const VERSION = '2.138.0';   // v2.138 · "
    NEW_V = (
        "const VERSION = '2.139.0';   // v2.139 · BIENVENIDA HABLADA — el dueño: «que al iniciar "
        "el juego en VR nos abriese con el siguiente mensaje de voz para la bienvenida (en "
        "castellano o inglés según el idioma)» → al ENTRAR EN VR el megáfono dice «Bienvenido a "
        "Crazy Ping Pong, escoge una modalidad de juego» (EN: «Welcome to Crazy Ping Pong, choose "
        "a game mode») justo cuando el MENÚ PRINCIPAL abre y recibe al jugador (el anuncio del "
        "modo sigue sonando al escogerla/cambiarla) · DOS ÁTOMOS NUEVOS en el banco de voz "
        "(bienvenida_modo es/en) con la receta Piper de siempre (es_ES-davefx-medium · "
        "en_US-lessac-medium → OGG Opus 28k mono) — la marca se sintetiza con grafía fonética "
        "«Kreisi Ping Pong» porque el modelo es-ES leyendo «Crazy» salía «cricket» (verificado "
        "por ASR sobre los dos candidatos; el EN la lee bien literal) · RUTA 100 % VR-SAFE: "
        "VOICE_FULL → speakPlan por WebAudio (la misma vía del megáfono, audible dentro de la "
        "sesión inmersiva donde speechSynthesis NO funciona), respaldo speechSynthesis 2D intacto "
        "· i18n: clave nueva welcome_menu en las dos mesas · núcleo: solo el anuncio de "
        "sessionstart + banco + planes · antes v2.138 · "
    )
    assert html.count(OLD_V) == 1, "ancla VERSION no única"
    html = html.replace(OLD_V, NEW_V)
    print("1) VERSION → 2.139.0 + changelog OK")

# ------------------------------------------------- 2/3) ÁTOMOS al banco es/en
if "bienvenida_modo:" not in html:
    # banco ES: primer «  bienvenido: "» tras «const VOICE_B64 = {»
    i0 = html.index("const VOICE_B64 = {")
    anchor = html.index('  bienvenido: "', i0)
    html = html[:anchor] + f'  bienvenida_modo: "{B64_ES}",\n' + html[anchor:]
    # banco EN: igual tras «const VOICE_B64_EN = {»
    j0 = html.index("const VOICE_B64_EN = {")
    anchor2 = html.index('  bienvenido: "', j0)
    html = html[:anchor2] + f'  bienvenida_modo: "{B64_EN}",\n' + html[anchor2:]
    print("2/3) átomos bienvenida_modo insertados en VOICE_B64 (es) y VOICE_B64_EN (en)")

# --------------------------------------------------------- 4) VOICE_FULL es/en
if "'bienvenido a crazy ping pong escoge una modalidad de juego'" not in html:
    a = "'bienvenido al partido buena suerte': ['bienvenido'],"
    assert html.count(a) == 1
    html = html.replace(
        a,
        a + "\n    'bienvenido a crazy ping pong escoge una modalidad de juego': "
            "['bienvenida_modo'],")
    print("4a) VOICE_FULL es OK")

if "'welcome to crazy ping pong choose a game mode'" not in html:
    b = "'welcome to the match good luck': ['bienvenido'],"
    assert html.count(b) == 1
    html = html.replace(
        b,
        b + "\n    'welcome to crazy ping pong choose a game mode': "
            "['bienvenida_modo'],")
    print("4b) VOICE_FULL en OK")

# ------------------------------------------------------------- 5) i18n es/en
if "welcome_menu:" not in html:
    es_a = "welcome: 'Bienvenido al partido. ¡Buena suerte!',"
    assert html.count(es_a) == 1
    html = html.replace(
        es_a,
        es_a + "\n    welcome_menu: 'Bienvenido a Crazy Ping Pong, "
               "escoge una modalidad de juego',")
    en_a = "welcome: 'Welcome to the match. Good luck!',"
    assert html.count(en_a) == 1
    html = html.replace(
        en_a,
        en_a + "\n    welcome_menu: 'Welcome to Crazy Ping Pong, choose a game mode',")
    print("5) i18n welcome_menu es/en OK")

# --------------------------------------------- 6) anuncio en onSessionStart
OLD_ANN = """    window.setTimeout(() => {
      this.audio.announce(this.mode === 'survival'
        ? T('mode_survival')
        : T('welcome'), true);
    }, 1400);"""
NEW_ANN = """    window.setTimeout(() => {
      // v2.139 · BIENVENIDA HABLADA: el MENÚ PRINCIPAL recibe al jugador
      // (abierto en este momento) — la voz da la bienvenida y guía a escoger
      // modalidad. Banco de voz por WebAudio: audible en VR (speechSynthesis
      // no suena en inmersivo); respaldo 2D intacto. Al escoger modalidad,
      // el menú anuncia la suya (modo_partido/modo_survival como siempre).
      this.audio.announce(T('welcome_menu'), true);
    }, 1400);"""
if OLD_ANN in html:
    assert html.count(OLD_ANN) == 1
    html = html.replace(OLD_ANN, NEW_ANN)
    print("6) anuncio de sessionstart → welcome_menu OK")
elif "welcome_menu" in html and "T('welcome_menu'), true);" in html:
    print("6) ya aplicado")
else:
    print("6) !! ANUNCIO NO ENCONTRADO — revisar"); sys.exit(1)

if html == orig:
    print("SIN CAMBIOS (todo ya aplicado)")
else:
    with open(GAME, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nGUARDADO: {GAME} ({len(html)} bytes)")
