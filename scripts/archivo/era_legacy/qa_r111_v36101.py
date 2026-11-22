#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r111_v36101.py — capa de QA de la ronda 111 (V3.6.111-SDK6).

HITO M4 del roadmap MEJORAS.md · ONBOARDING < 60 SEGUNDOS.

  1) ▶ JUGAR BOTÓN ÚNICO (c12 drawMenuHub): tarjeta 'start' a toda fila
     (944×136) en y=240, POR ENCIMA del banner de la academia; AJUSTES en
     la parrilla (media celda); sin restos del opts completo antiguo.
  2) HUB DIRECTO (c12 onSessionStart): menuPage='main' SIEMPRE (la página
     «¿PRIMERA VEZ?» ya no bloquea el arranque) + bienvenida en UNA línea
     (first_hint) para la 1.ª instalación.
  3) LA MESA DE LA CASA (c12): diorama IA-vs-IA en el hall — construir/
     tick, mesa miniatura sobre pedestal, cinemática pura (sin física ni
     árbitro), enganchado al tick del hall (coste cero en cancha).
  4) GUÍA DEL PRIMER SAQUE (c12): aros en la cancha real (TorusGeometry),
     haz pulsante, _srvGuideTry desde exitHall, marcado pp_srv_v1 tras 3
     saques, línea que SOBREVIVE al startMatch (hook onMatchStart),
     nunca en online ni academia, desmonte con dispose.
  5) IDIOMA DETECTADO (c00): navigator.language en 1.ª instalación con
     huellas pp_tut_asked/pp_seen_v1 como guardia; i18n ES/EN de las 3
     claves nuevas (hub_play, first_hint, srv_guide).
  6) ALTURA DE MESA AUTO (c12): muestreo de cabeza a 2,6-4,7 s, mediana,
     <1,30 m → preset baja (0,70), guardia pp_hauto_v1, nunca online.
  7) TELEMETRÍA (catálogo v6, 16 eventos): primer_rally (lat/dif, una por
     sesión, sólo partido local) + tut_end (done/aJugar/step) en c13.
  8) REGRESIÓN: r110 (duelo intacto), r109 (PWA), r107 (arneses), r106
     (hápticas), r59 (banner academia presente) y el sello de versión.
"""
import json
import os

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
VER = V['version']

print('== ESTÁTICA (game.html · M4) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8').read()

# 1 · ▶ JUGAR botón único
AGUJAS = [
    ("this._modeCard(rects, 'start', 40, 240, 944, 136, T('hub_play')",
     "tarjeta ▶ JUGAR a toda fila (944×136) en y=240"),
    ("'#37b24d', '#1e7c33', PP_ICONS.match, true);",
     '▶ JUGAR verde vivo con ancho completo (wide=true)'),
    # r115 · re-ancla: el HUB vive en parrilla (la escalera de carrera
    # M5b ocupa la media celda izquierda; la academia, la derecha)
    ("this._modeCard(rects, 'tut:go', X1, 394, CW, CH, T('tut_hub')",
     'banner de la academia en parrilla (X1, y=394, junto a carrera)'),
    ("this._modeCard(rects, 'page:opts', X1, y, CW, CH, T('opts_title')",
     'AJUSTES en la parrilla (media celda, X1)'),
    ('hub_play', 'i18n clave hub_play usada en c12'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'c12 HUB: ' + nombre)
CHK("this._modeCard(rects, 'page:opts', 40, y, 944, CH" not in GH,
    'c12 HUB: sin restos de la tarjeta AJUSTES completa antigua')

# 2 · HUB directo sin página bloqueante
CHK("this.menuPage = 'main';\n    this.menuSec = 'match';" in GH,
    "c12 onSessionStart: el HUB nace SIEMPRE en 'main' (sin tutask bloqueante)")
CHK('if (_tutFirst) this.rules.message = T(\'first_hint\');' in GH,
    'c12: bienvenida de 1.ª vez en UNA línea del árbitro')

# 3 · diorama LA MESA DE LA CASA — RETIRADO en r114 (petición expresa y
# REITERADA del dueño: «sigo viendo la mesa con las dos palas jugando en el
# Hall y ya dijimos que no la queremos, no aporta nada»). La capa pasa de
# exigir presencia a exigir AUSENCIA (re-ancla honesta de r114).
RETIRADA_DEMO = [
    ('_demoMuseoConstruir()', 'diorama: construcción'),
    ('_demoMuseoTick(dt, now)', 'diorama: latido enganchado al animate'),
    ('if (this._demoHall && this.inHall) this._demoMuseoTick(dt, now);',
     'diorama: guard del latido en el animate'),
    ('new THREE.BoxGeometry(0.84, 0.028, 1.50)', 'mesa miniatura (escala ~0,55)'),
    ('new THREE.CylinderGeometry(0.062, 0.062, 0.012, 14)', 'palas disco del diorama'),
    ('d.bola.position.lerpVectors(d.desde, d.hasta, k);',
     'rallye cinemático: parábolas scriptadas (sin física real)'),
    ('p2.rotation.x = 0.9;', 'swing seco del golpe del rival'),
]
for aguja, nombre in RETIRADA_DEMO:
    CHK(aguja not in GH, 'c12 diorama RETIRADO (r114): ' + nombre)
CHK('LA MESA DE LA CASA — RETIRADA' in GH, 'c12: marcador del retiro del diorama (r114)')

# 4 · guía del primer saque
AGUJAS_SRV = [
    ('_srvGuideTry()', 'guía: oferta (exitHall → cancha real)'),
    ('_srvGuideTick(dt)', 'guía: latido'),
    ('_srvGuideQuitar(visto)', 'guía: desmonte con dispose'),
    ("try { this._srvGuideTry(); } catch (eSG) { /* nunca rompe */ }",
     'guía: enganchada a exitHall (todos los caminos a la cancha)'),
    ('new THREE.TorusGeometry(0.085, 0.009, 8, 28)', 'aros guía (misma geometría academia)'),
    ('blending: THREE.AdditiveBlending, depthWrite: false,', 'haz pulsante aditivo'),
    ("if (this._srvCount >= 3) this._srvGuideQuitar(true);",
     'guía: 3 saques legales y se marca vista'),
    ("try { localStorage.setItem('pp_srv_v1', '1'); } catch { /* */ }",
     'guía: marcado como visto en localStorage (pp_srv_v1)'),
    ("if (this.mode !== 'match' || this.tutV1) return;",
     'guía: NUNCA en academia ni supervivencia'),
    ('if (this.net && this.net.online) return;',
     'guía: NUNCA en online'),
    ("if (this._srvGrp && this._srvGrp.visible) {\n            this.rules.message = T('srv_guide');",
     'guía: la línea sobrevive al startMatch (hook onMatchStart)'),
]
for aguja, nombre in AGUJAS_SRV:
    CHK(aguja in GH, 'c12 guía saque: ' + nombre)

# 5 · idioma detectado + altura auto
CHK("const nav = String(navigator.language || 'es').toLowerCase();" in GH,
    'c00: navigator.language leído en 1.ª instalación')
CHK("__ppLang = (nav.slice(0, 2) === 'es') ? 'es' : 'en';" in GH,
    'c00: es→ES · resto→EN')
CHK("!localStorage.getItem('pp_tut_asked') &&" in GH and
    "!localStorage.getItem('pp_seen_v1')" in GH,
    'c00: guardia de huellas (quien ya jugaba no cambia de idioma)')
CHK('pp_hauto_v1' in GH and 'if (hMed < 1.30) this._mesaAplicarY(0.70);' in GH,
    'c12: altura auto (mediana de cabeza → mesa baja si sentado)')

# 6 · i18n ES/EN de las claves nuevas
CHK("hub_play: '▶ JUGAR'," in GH, 'i18n ES: hub_play')
CHK("hub_play: '▶ PLAY'," in GH, 'i18n EN: hub_play')
CHK("first_hint: 'Bienvenido · pulsa ▶ JUGAR" in GH, 'i18n ES: first_hint')
CHK("first_hint: 'Welcome · press ▶ PLAY" in GH, 'i18n EN: first_hint')
CHK("srv_guide: 'GUÍA DE SAQUE ·" in GH, 'i18n ES: srv_guide')
CHK("srv_guide: 'SERVE GUIDE ·" in GH, 'i18n EN: srv_guide')

# 7 · telemetría del embudo (catálogo v6)
CHK("__PP_TELE.ev('primer_rally', {" in GH,
    'telemetría: primer_rally emitido (primer rallye real de la sesión)')
CHK('window.__PP_TELE.ev(\'tut_end\', {' in GH,
    'telemetría: tut_end emitido (cierre de la academia)')
CAT = json.load(open(os.path.join(RAIZ, 'scripts/telemetria_catalogo.json')))
# r115 · re-ancla: versión del catálogo comparable (v8 llega como str)
CHK(int(str(CAT['version']).lstrip('v')) >= 7, f"catálogo v7+ (={CAT['version']})")
CHK(len(CAT['eventos']) >= 17, f"catálogo documenta 17+ eventos (={len(CAT['eventos'])})")
nombres = {e['nombre'] for e in CAT['eventos']}
CHK({'primer_rally', 'tut_end'} <= nombres, 'catálogo: primer_rally + tut_end documentados')
CHK("lat: Math.round((Date.now() - (this._vrT0 || Date.now())) / 100) / 10," in GH,
    'telemetría: lat = segundos desde vr_start')

# 8 · sello de versión + regresión de hitos previos
CHK(f'{VER}' in GH, f'sello de versión {VER} presente en el juego')
REGRESION = [
    ('_megaNormReset', 'r62+ hápticas/poderes intactos'),
    ('r110 · SEMÁNTICA DEL BIT 4', 'r110 fix de duelo presente en el juego'),
    ("navigator.serviceWorker.register('sw.js'", 'r109 PWA intacta'),
    ('MAX_SPIN', 'r110 validador justo intacto'),
    ('PP_ICONS.tut', 'r59 banner academia intacto'),
]
for aguja, nombre in REGRESION:
    CHK(aguja in GH, 'regresión: ' + nombre)

print(f"\nRESULTADO: {len(OK)} OK · {len(FAIL)} FALLOS")
if FAIL:
    print('\nFALLOS:')
    for f in FAIL:
        print('  ✗ ' + f)
    raise SystemExit(1)
print('CAPA r111 VERDE: ▶ JUGAR único + HUB directo + (diorama retirado en r114) +')
print('guía del primer saque + idioma/altura detectados + catálogo v6.')
