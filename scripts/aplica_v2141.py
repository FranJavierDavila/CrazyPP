#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.141 · Núcleo (game.html): VERSION 2.141.0 + changelog, 8 átomos NUEVOS
de megafonía (mega_salida/llega_gd·sc en VOICE_B64 es y VOICE_B64_EN) y sus
8 entradas VOICE_FULL (4 es + 4 en) — los NOMBRES NUEVOS de las paradas del
Salvaje Oeste: GOLD DUST y SILVER CREEK (BRAVOS ya sonaba desde v2.140).
Idempotente: si un marcador ya está, no lo duplica."""
import base64
import re
import sys

GAME = '/home/z/my-project/public/game.html'
OGG_DIR = '/home/z/my-project/scripts/voice/ogg'
OGG_EN_DIR = '/home/z/my-project/scripts/voice/ogg_en'

NEW_KEYS = ['mega_salida_gd', 'mega_salida_sc', 'mega_llega_gd', 'mega_llega_sc']

STORY = (
    'v2.141 · OESTE «LOS CAJONES DEL ORO» + PARADAS CON NOMBRE — ajustes del '
    'dueño sobre la v2.140 (etapa 4 «ASALTO AL TREN»): (1) LINGOTES SOBRE DOS '
    'GRANDES CAJONES — «los lingotes van a caer a ambos lados de la mesa pero '
    'cerca del centro de las ventanas, en el suelo, sobre dos grandes cajones '
    'de madera (podemos usar alguno de los que ya colocamos para destruir, los '
    'que no tienen el dibujo del candado)»: DOS cajones limpios del artista '
    '(cubo1/cubo2, sin candado) ACHATADOS (el doble de anchos: huella 0,72 m · '
    'la mitad de altos: 0,18 m) sobre el suelo del vagón, uno a cada lado de la '
    'mesa y CERCA DEL CENTRO DE LAS VENTANAS laterales (centros medidos sobre '
    'el arte 2395×864: izquierda u=0,472 → z -1,38 · derecha u=0,501 → z -1,59; '
    'x ±1,35 entre mesa y pared). En su cara superior se apilan los lingotes: '
    'rejilla 3×3 POR CAJÓN con hueco uniforme (sep 0,19 × 0,095 para un lingote '
    '0,17×0,08), capas EXACTAS (altura real del GLB + 1,5 mm — unos perfectamente '
    'encima de otros) y una PEQUEÑA VARIACIÓN de colocación (±7 mm · ±3 mm · '
    '±1,7° de yaw, holguras que NUNCA llegan a tocar al vecino) «para que no '
    'parezca tan perfecta»; cada lingote alterna IZQ/DER y ocupa el PRIMER hueco '
    'libre de SU cajón — si el forajido roba uno, SU hueco VUELVE a la lista '
    '(nada se solapa ni se mete unos dentro de otros). (2) PARADAS CON NOMBRE Y '
    'ARTE PROPIO — «primera parada nombre Bravos, imagen parada1.png, segunda '
    'parada nombre GOLD DUST, imagen parada2.png, tercera parada nombre Silver '
    'Creek, imagen parada3.png. Estos son los nombres que deberá decir la voz en '
    'las llegadas y las salidas»: stationNames = BRAVOS (depósito de salida) · '
    'BRAVOS · GOLD DUST · SILVER CREEK, y PARADA1.png se actualiza con el arte '
    'nuevo del dueño (1024×512, estación BRAVOS). MEGAFONÍA: 4 ÁTOMOS NUEVOS por '
    'idioma (mega_salida/llega_gd·sc — misma receta Piper es_ES-davefx / '
    'en_US-lessac → OGG Opus 28k, ES literal elegido por ASR, consistente con '
    '«Dry Gulch» de v2.140) con sus 8 entradas VOICE_FULL — la normalización de '
    'los textos del módulo sigue coincidiendo EXACTA. SUELO del vagón: '
    'room/vagon/suelo.jpg se actualiza con la TARIMA nueva del dueño (1296×1678, '
    'mismo mapeo 1:1). NORMAS de la etapa y avisos al día (el lingote se apila '
    'SOBRE LOS GRANDES CAJONES junto a las ventanas). Módulo OESTE v48 '
    '(manifest 48). Núcleo: solo banco de voz + planes + marcador · antes v2.140 · '
)


def main() -> int:
    h = open(GAME, encoding='utf-8').read()
    orig = h

    # 1 · VERSION + changelog (idempotente)
    if "const VERSION = '2.141.0'" not in h:
        old = "const VERSION = '2.140.0';   // "
        assert old in h, 'línea VERSION no encontrada'
        h = h.replace(old, "const VERSION = '2.141.0';   // " + STORY, 1)
        print('VERSION -> 2.141.0 + changelog')
    else:
        print('VERSION ya 2.141.0')

    # 2 · átomos nuevos en VOICE_B64 (es) y VOICE_B64_EN (en)
    def inject_bank(h, bank_marker, ogg_dir, tag):
        i = h.index(bank_marker)
        # insertar justo tras el átomo mega_oro del banco (el último mega_*)
        m = re.compile(r'(  mega_oro: "[A-Za-z0-9+/=]+",\n)', re.S).search(h, i)
        assert m, f'mega_oro no encontrado en {tag}'
        add = ''.join(
            f'  {k}: "{base64.b64encode(open(f"{ogg_dir}/{k}.ogg", "rb").read()).decode("ascii")}",\n'
            for k in NEW_KEYS)
        if f'  {NEW_KEYS[0]}: "' in h[i:i + 400000]:
            print(f'átomos ya presentes en {tag}')
            return h
        print(f'{tag}: +{len(NEW_KEYS)} átomos tras mega_oro '
              f'({sum(len(open(f"{ogg_dir}/{k}.ogg", "rb").read()) for k in NEW_KEYS)} B ogg)')
        return h[:m.end(1)] + add + h[m.end(1):]

    h = inject_bank(h, 'const VOICE_B64 = {', OGG_DIR, 'VOICE_B64 (es)')
    h = inject_bank(h, 'const VOICE_B64_EN = {', OGG_EN_DIR, 'VOICE_B64_EN (en)')

    # 3 · VOICE_FULL: 4 entradas por idioma (tras las de bravos)
    ins_es = (
        "    'pasajeros al tren partimos hacia gold dust': ['mega_salida_gd'],\n"
        "    'pasajeros al tren partimos hacia silver creek': ['mega_salida_sc'],\n"
        "    'en menos de 25 segundos llegaremos a gold dust': ['mega_llega_gd'],\n"
        "    'en menos de 25 segundos llegaremos a silver creek': ['mega_llega_sc'],\n")
    ins_en = (
        "    'all aboard we are departing towards gold dust': ['mega_salida_gd'],\n"
        "    'all aboard we are departing towards silver creek': ['mega_salida_sc'],\n"
        "    'in less than 25 seconds we will arrive at gold dust': ['mega_llega_gd'],\n"
        "    'in less than 25 seconds we will arrive at silver creek': ['mega_llega_sc'],\n")
    a1 = "    'en menos de 25 segundos llegaremos a bravos': ['mega_llega_br'],\n"
    a2 = "    'in less than 25 seconds we will arrive at bravos': ['mega_llega_br'],\n"
    assert a1 in h and a2 in h, 'anclas VOICE_FULL no encontradas'
    if 'partimos hacia gold dust' not in h:
        h = h.replace(a1, a1 + ins_es, 1)
        print('VOICE_FULL es: +4 entradas')
    else:
        print('VOICE_FULL es ya presente')
    if 'departing towards gold dust' not in h:
        h = h.replace(a2, a2 + ins_en, 1)
        print('VOICE_FULL en: +4 entradas')
    else:
        print('VOICE_FULL en ya presente')

    if h == orig:
        print('SIN CAMBIOS')
        return 0
    assert h.count('const VERSION = ') == 1
    open(GAME, 'w', encoding='utf-8').write(h)
    print(f'game.html escrito ({len(h)} bytes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
