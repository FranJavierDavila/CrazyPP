#!/usr/bin/env python3
"""v2.122 · bump de manifests + note_v2122 (auditoría de música / una melodía)."""
import json, collections, io

NOTES = {
    'oeste': ('v2.122 (módulo v41) AUDITORÍA DE MÚSICA — UNA MELODÍA SIEMPRE: '
              'FIX del SOLAPO del TREN — al arrancar la prueba del tren la BSO '
              'del saloon seguía sonando (ranura _mus del ForajidoStand) y el '
              'TrenAction arrancaba ARRIBA vagon.mp3 (ranura _mus propia): DOS '
              'pistas melódicas solapadas durante todo el trayecto (y vagon.mp3 '
              'era inaudible bajo la BSO). Ahora: _startTren retira la BSO del '
              'saloon ANTES de arrancar el tren (musicOff) y _endPrueba la trae '
              'de vuelta en la sala (musicOn, idempotente — en el asedio la BSO '
              'sigue viva y no se duplica). El rumble de la locomotora (ruido) '
              'y los jingles de oleada (puntuales) no cambian. Núcleo 2.122.0: '
              'invariante UNA MELODÍA en startMusic() del núcleo — la música del '
              'menú fuerza el duck de la BSO del campeonato aunque algún camino '
              'futuro olvide setArcDuck. Sin cambios de jugabilidad ni de arte.'),
    'locura': ('v2.122 (módulo v15) AUDITORÍA DE MÚSICA — UNA MELODÍA SIEMPRE: '
               'revisión de los 4 canales del campeonato (BSO del núcleo, '
               'música del menú VR, risas y jingles): sin solapos — la BSO '
               'sóla suena durante la partida (setArcWanted), se apaga al salir '
               'y al terminar, y el menú del núcleo la silencia con el duck '
               '(v2.37) que ahora el núcleo FUERZA en startMusic (invariante '
               'v2.122). El arkanoid mantiene la BSO de fondo (una sola '
               'melodía). Sin cambios de jugabilidad ni de arte.'),
    'magia': ('v2.122 (módulo v25) AUDITORÍA DE MÚSICA — UNA MELODÍA SIEMPRE: '
              'la BSO del Wizard (bso.mp3, ranura _mus propia) ya respeta el '
              'duck del menú por _syncMusicGain (v2.78) y el núcleo 2.122.0 '
              'FUERZA ese duck al arrancar la música del menú (invariante UNA '
              'MELODÍA). Sin segunda fuente melódica en el campeonato (fuego, '
              'sombras, portales y risa son efectos puntuales). Sin cambios de '
              'jugabilidad ni de arte.'),
}

BASE = '/home/z/my-project/game/championships'
for folder, (ver, note) in zip(
        ['oeste', 'locura', 'magia'],
        [(41, NOTES['oeste']), (15, NOTES['locura']), (25, NOTES['magia'])]):
    p = f'{BASE}/{folder}/manifest.json'
    with open(p, encoding='utf-8') as fh:
        d = json.load(fh, object_pairs_hook=collections.OrderedDict)
    d['version'] = ver
    # nota nueva SIEMPRE al final (orden estable de claves)
    d[f'note_v2122'] = note
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    print(f'{p}: version -> {ver} · note_v2122 añadida ({len(note)} chars)')
