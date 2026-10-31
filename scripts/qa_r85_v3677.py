#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r85_v3677.py — CAPA BU (r85 · V3.6.91-SDK6)
   Halloween (campeonato del dueño: ZOMBI + mapa + cartel normas) ·
   Retiro del Valle Neón · Dificultad del Reto Diario (DAILY_DIF) ·
   EL TALLER UGC (editor standalone) · parches de núcleo (NORMAS_SKIN,
   filtro de temas, CHAMP_STAGE_TOTAL, cartel de etapas dinámico)."""
import json, os, re, subprocess, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(RAIZ, 'public', 'game.html')
CH = os.path.join(RAIZ, 'public', 'championships', 'halloween')
AS = os.path.join(CH, 'assets')

ok, fallos = [], []
def CHK(cond, msg):
    (ok if cond else fallos).append(msg)
    print(('  [OK]    ' if cond else '  [FALLO] ') + msg)

G = open(GAME, encoding='utf-8').read()

print('== 1 · AGUJAS DEL BUILD (game.html) ==')
for aguja, minimo in [
    ('const DAILY_DIF = { DESDE: \'2026-11-01\', CADA: 14, PASO: 1, TOPE: 3 }', 1),
    ('function dailySub(k)', 1),
    ('function objN()', 1),
    ('st.streak >= objN()', 1),
    ("' + objN()", 2),                       # HUD contador + objetivo pintado
    ('NORMAS_SKIN.defs[tema]', 1),            # filtro r85 de showInstrucciones
    ('halloween: 5', 1),                      # CHAMP_STAGE_TOTAL
    ("'HALLOWEEN'", 1),                       # CHAMPS_DIA
    ('championships/halloween/assets/normas_halloween.png', 1),  # skin del artista precargada
    ("rect: [166, 122, 906, 454]", 1),
]:
    n = G.count(aguja)
    CHK(n >= minimo, 'aguja %s ×%d (≥%d)' % (aguja[:52], n, minimo))

print('== 2 · NEGATIVAS (retiro del Valle Neón) ==')
CHK('valle_neon: 5' not in G, 'CHAMP_STAGE_TOTAL sin valle_neon')
CHK("'NEÓN'" not in G, 'CHAMPS_DIA sin NEÓN')
CHK('Valle Neón' not in G, 'bundle sin el título del valle')

print('== 3 · MANIFEST DEL CAMPEONATO ==')
m = json.load(open(os.path.join(CH, 'manifest.json'), encoding='utf-8'))
CHK(m['id'] == 'halloween' and m['estado'] == 'publicado', 'id halloween · publicado')
CHK(m['title']['es'] == 'Campeonato de Halloween', 'título ES')
CHK(m['storage'] == 'pp_champ_halloween_*', 'storage nuevo (progreso limpio)')
sts = m['stages']
CHK(len(sts) == 5 and [s['kind'] for s in sts] == ['duelo', 'dianas', 'duelo', 'dianas', 'duelo'],
    '5 etapas duelo→prueba→duelo→prueba→final')
CHK(sts[4]['rules'].get('jefe') is True, 'DUELO FINAL con jefe')
CHK(sts[1]['name'] == 'La Cripta Sellada' and sts[3]['name'] == 'El Pozo del Cometa',
    'pruebas 2 y 4 con nombre del artista (cripta/pozo)')
mp = m['mapa']
CHK(mp['modo'] == 'arte' and mp['arte'] == 'assets/mapa.webp', 'mapa modo arte (póster del dueño)')
nodos = mp.get('nodos', [])
espera = [(148, 392), (355, 592), (875, 202), (890, 556), (1265, 332)]
CHK(len(nodos) == 5 and all(n['x'] == x and n['y'] == y for n, (x, y) in zip(nodos, espera)),
    '5 nodos medidos sobre el arte del dueño (medallones 1-5)')
rv = m['rival']
CHK(rv['name'] == 'ZOMBI', 'rival ZOMBI')
CHK(rv['states'] == ['present', 'idle', 'focused', 'surprised', 'panic', 'laughing',
                     'crazy', 'angry', 'picando', 'loosing', 'defeated', 'victory'],
    '12 poses EXACTAS del zip del dueño')
CHK(m['rivalVisual']['base'] == 'present.webp' and m['rivalVisual']['ext'] == 'webp',
    'rivalVisual base present.webp ext webp')
pods = m['powers']
CHK([p['kind'] for p in pods] == ['mano', 'moscas', 'calabaza', 'gelatina'],
    'poderes r86: los 4 REALES del dueño (Mano · Moscas · Calabaza · Gelatina)')
# r89/r91/r93 · re-anclaje honesto: gelatina dura 12 s (petición del dueño en r89:
# «este efecto podemos prolongarlo hasta los 12 segundos») y la BSO es
# melodia.mp3 desde la r93 (midnight_volley fue la de r90; el dueño cambió la melodía)
CHK([p['duration'] for p in pods] == [10, 10, 10, 12],
    'poderes: mano/moscas/calabaza 10 s · gelatina 12 s (petición del dueño r89)')
CHK([p.get('chance') for p in pods] == [0.30, 0.28, 0.30, 0.30], 'chance rally de los 4')
CHK(all(p['icon'].startswith('assets/power_') for p in pods), 'medallón circular por poder')
CHK(m['audio']['music'] == 'assets/melodia.mp3' and m['audio']['sounds']['laugh'] == 'assets/risas.mp3',
    'audio: BSO melodia.mp3 del dueño (r93) + risa')
CHK(len(m['room']) >= 6 and m['room']['floor'] == 'assets/sala_floor.jpg', 'sala 6 planos')
dec = m['decor']['pieces']
CHK([d['file'] for d in dec] == ['assets/decor_arana.png', 'assets/decor_calabaza.png',
                                 'assets/decor_lapida.png', 'assets/decor_ojos.png'],
    'decor r86: los 4 TROQUELES del dueño')
CHK(all(d['h'] > 0.5 and abs(d['x']) > 1.5 for d in dec), 'troqueles en flancos, fuera de la mesa')
CHK(m['coronacion']['titulo']['es'] == '¡ZOMBI DERROTADO!', 'coronación temática')
CHK(len(m['i18n']['es']['instr_lineas']) >= 4 and 'por anunciar' in m['i18n']['es']['instr_lineas'][3],
    'normas provisionales de las etapas 2 y 4 (mecánica por anunciar)')
CHK(m.get('playerGun') is None, 'sin pistola (gun desactivada)')
CHK('playerGun' not in json.dumps(m), 'manifest sin playerGun')

print('== 4 · ASSETS EN DISCO ==')
oblig = ['rival.webp'] + [s + '.webp' for s in rv['states']] + ['mapa.webp', 'normas_halloween.png',
    'sala_floor.jpg', 'sala_ceil.jpg', 'sala_back.jpg', 'sala_front.jpg', 'sala_left.jpg',
    'sala_right.jpg', 'bso.wav', 'risas.mp3', 'insignia.png',
    # r86 · escenario real + superpoderes del dueño
    'mano1.webp', 'mano2.webp', 'mano3.webp', 'losa.jpg', 'superpower.webp',
    'gelatina.webp', 'calabaza.glb', 'mosca.webp',
    'power_mano.webp', 'power_moscas.webp', 'power_calabaza.webp', 'power_gelatina.webp',
    'decor_arana.png', 'decor_calabaza.png', 'decor_lapida.png', 'decor_ojos.png',
    'LEEME-ASSETS.txt']
for f in oblig:
    p = os.path.join(AS, f)
    CHK(os.path.exists(p) and os.path.getsize(p) > 500, 'assets/%s (%s B)' %
        (f, os.path.getsize(p) if os.path.exists(p) else 'AUSENTE'))

print('== 5 · REGLA DE ORO: ALFA EN LAS ESQUINAS (12 poses) ==')
try:
    from PIL import Image
    malos = []
    for st in rv['states']:
        im = Image.open(os.path.join(AS, st + '.webp')).convert('RGBA')
        w, h = im.size
        esq = [im.getpixel(p)[3] for p in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
        if max(esq) > 30:
            malos.append(st)
    CHK(malos == [], 'esquinas alfa<30 en las 12 poses %s' % ('' if not malos else '→ ' + str(malos)))
except Exception as e:
    CHK(False, 'alfa poses: excepción %s' % e)

print('== 6 · ÍNDICE DE CAMPEONATOS ==')
reg = json.load(open(os.path.join(RAIZ, 'public', 'championships', 'championships.json'), encoding='utf-8'))
ids = [e['id'] if isinstance(e, dict) else e for e in reg['championships']]
CHK(ids == ['locura', 'magia', 'oeste', 'estacion_orbital', 'halloween'], 'índice: 4 históricos + halloween')
CHK('valle_neon' not in ids, 'valle_neon fuera del índice')
CHK(not os.path.exists(os.path.join(RAIZ, 'public', 'championships', 'valle_neon')),
    'carpeta valle_neon eliminada')

print('== 7 · EL TALLER UGC (editor standalone) ==')
ED = os.path.join(RAIZ, 'public', 'ugc', 'index.html')
CHK(os.path.exists(ED) and os.path.getsize(ED) > 40000, 'public/ugc/index.html (%d B)' % os.path.getsize(ED) if os.path.exists(ED) else 'AUSENTE')
ed = open(ED, encoding='utf-8').read() if os.path.exists(ED) else ''
for aguja in ['TALLER UGC', 'Cargar manifest.json', 'Validar', 'Exportar manifest.json',
              'function validar(', 'nodos del mapa', 'Los 4 pasos de un campeonato UGC']:
    CHK(aguja in ed, 'editor contiene "%s"' % aguja)
for secreto in ['github_pat_', 'cfut_', 'CLAVE=']:
    CHK(secreto not in ed, 'editor SIN secreto "%s"' % secreto)

print('== 8 · UNIDAD: ESCALONADO DEL RETO DIARIO ==')
src13 = open(os.path.join(RAIZ, 'src', 'game', 'core', 'c13_ui_arranque.js'), encoding='utf-8').read()
mm = re.search(r"const DAILY_DIF = (\{[^;]+\});", src13)
mf = re.search(r"function dailySub\(k\) \{.*?\n    \}", src13, re.S)
CHK(mm is not None and mf is not None, 'bloques DAILY_DIF + dailySub extraíbles de la fuente')
js = mm.group(0) + '\n' + mf.group(0).replace('    ', '  ') + """
const casos = [
  ['2026-10-30', 0], ['2026-10-31', 0], ['2026-11-01', 1], ['2026-11-14', 1],
  ['2026-11-15', 2], ['2026-11-29', 3], ['2026-12-13', 3], ['2027-05-01', 3],
];
let mal = 0;
for (const [k, esperado] of casos) {
  const got = dailySub(k);
  if (got !== esperado) { console.log('  caso ' + k + ' → ' + got + ' (esperaba ' + esperado + ')'); mal++; }
}
console.log('CASOS ' + (casos.length - mal) + '/' + casos.length);
if (mal) process.exit(1);
"""
r = subprocess.run(['node', '-e', js], capture_output=True, text=True)
CHK(r.returncode == 0 and 'CASOS 8/8' in r.stdout, 'escalera: 0 hasta 31 Oct · 1 Nov +1 · 15 Nov +2 · 29 Nov +3 (tope) [%s]' % r.stdout.strip().splitlines()[-1] if r.stdout else 'sin salida')
# plan del día: sin subida ANTES de DESDE (hoy 2026-10-28)
mm2 = re.search(r"mode, n: M\.n \+ dailySub\(k\),", src13)
CHK(mm2 is not None, 'dailyPlan aplica el objetivo escalado (punto ÚNICO)')

print('== 9 · PLANTILLA Y MÓDULO DE HALLOWEEN ==')
pl = open(os.path.join(RAIZ, 'public', 'championships', '_plantilla', 'index.js'), encoding='utf-8').read()
hi = open(os.path.join(CH, 'index.js'), encoding='utf-8').read()
CHK("'/5 ·" not in pl and 'CTRL.totalEtapas()' in pl, 'plantilla: cartel con total REAL de etapas')
CHK('CTRL.totalEtapas()' in hi, 'módulo halloween hereda el cartel dinámico (plantilla r85)')
CHK("const MOD_ID = 'halloween';" in hi, 'módulo halloween con MOD_ID propio')
for metodo in ['init', 'start', 'leave', 'resetRecords', 'onPoint', 'onMatchOver', 'aiMul',
               'replayMap', 'replayHover', 'replayLaunch', 'musicOff', 'isChampion']:
    CHK(metodo in hi, 'contrato del módulo: %s' % metodo)
CHK('createRival' in hi and 'createCartel' in hi and 'createMusic' in hi, 'módulo usa el SDK (rival/cartel/música)')

print()
print('BU · RESUMEN: %d OK · %d FALLO' % (len(ok), len(fallos)))
if fallos:
    print('FALLOS:')
    for f in fallos:
        print('  - ' + f)
sys.exit(1 if fallos else 0)
