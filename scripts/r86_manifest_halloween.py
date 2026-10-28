#!/usr/bin/env python3
"""r86 · manifest de halloween v2: 4 superpoderes reales del dueño + 4 troqueles."""
import json

P = '/home/z/my-project/public/championships/halloween/manifest.json'
m = json.load(open(P))

m['version'] = 2

m['powers'] = [
    {"kind": "mano", "name": "Mano de zombi", "icon": "assets/power_mano.webp",
     "cooldown": 15, "duration": 10, "warn": 2, "activacion": "rally", "chance": 0.30},
    {"kind": "moscas", "name": "Plaga de Moscas", "icon": "assets/power_moscas.webp",
     "cooldown": 18, "duration": 10, "warn": 2, "activacion": "rally", "chance": 0.28},
    {"kind": "calabaza", "name": "Calabaza", "icon": "assets/power_calabaza.webp",
     "cooldown": 16, "duration": 10, "warn": 2, "activacion": "rally", "chance": 0.30},
    {"kind": "gelatina", "name": "Gelatina Asquerosa", "icon": "assets/power_gelatina.webp",
     "cooldown": 14, "duration": 10, "warn": 2, "activacion": "rally", "chance": 0.30},
]

m['decor'] = {
    "pieces": [
        {"file": "assets/decor_arana.png", "h": 1.15, "x": -2.30, "z": -2.75, "sway": 0.5},
        {"file": "assets/decor_calabaza.png", "h": 1.30, "x": 2.45, "z": -2.35, "sway": 0.5},
        {"file": "assets/decor_lapida.png", "h": 1.00, "x": -2.35, "z": -1.15, "sway": 0.55},
        {"file": "assets/decor_ojos.png", "h": 0.85, "x": 2.00, "z": -0.80, "sway": 0.5},
    ],
}

m['assets'] = ("assets/ (12 poses del zombi del dueño en webp, mapa.webp del dueño, "
               "normas_halloween.png del dueño, sala_*.jpg REALES del dueño (paredes.zip), "
               "decor_arana/calabaza/lapida/ojos.png REALES del dueño (troqueles.zip), "
               "mano1/2/3.webp del dueño (traen el montículo integrado), losa.jpg del dueño "
               "(mesa.jpg), superpower.webp del dueño (SuperPower.png), gelatina.webp del dueño, "
               "calabaza.glb del dueño, power_mano/moscas/calabaza/gelatina.webp de la casa "
               "(medallones), mosca.webp de la casa, bso.wav PROVISIONAL, risas.mp3 PROVISIONAL, "
               "insignia.png)")

m['notes'] = [
    "v1 (r85) · Campeonato de Halloween — el campeonato del Valle Neón se RETIRA a petición del dueño y su hueco lo ocupa Halloween: rival ZOMBI con las 12 poses del artista (upload/zombi.zip), mapa del artista con 5 nodos medidos (upload/Mapa.png) y cartel de normas del artista (upload/zombi_normas.png) para las etapas 2 y 4.",
    "v2 (r86) · ESCENARIO REAL: las 6 paredes de la estancia del artista sustituyen al cementerio procedimental (paredes.zip), los 4 troqueles del artista entran en decor.pieces (troqueles.zip), la mesa viste la LOSA de piedra del artista (mesa.jpg, patrón madera del Oeste) y los 2 poderes provisionales (Niebla de tumba/Orbe espectral) dejan paso a los 4 SUPERPODERES REALES del zombi (10 s, anuncio SuperPower.png + medallón circular abajo-derecha + congelación): Mano de zombi (las 3 manos del artista salen de su montículo, estorban y frenan la bola — al chocar la bola se para, se cae y la mano revienta en trocitos), Plaga de Moscas (enjambre revoloteando en la cara del jugador, se espantan con la pala), Calabaza (la bola se vuelve calabaza.glb ×3, pesada y con salida aleatoria tras cada bote en la mesa) y Gelatina Asquerosa (manchas que contaminan la bola: verde fosforito, ×3 de peso, arrastra y suelta humillo verde).",
    "PROVISIONAL pendiente del artista: bso (del valle), risa e insignia; mecánicas de las etapas 2 y 4 (hoy dianas).",
]

json.dump(m, open(P, 'w'), indent=2, ensure_ascii=False)
print('manifest v2 OK · powers:', [p['kind'] for p in m['powers']],
      '· decor:', len(m['decor']['pieces']))
