#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r113_v36103.py — capa de QA de la ronda 113 (V3.6.104-SDK6).

SEIS AJUSTES DEL DUEÑO sobre el juego vivo:

  1) CHINCHETA DEL MENÚ (c12): icono SIEMPRE visible en el centro superior
     del panel (quad hijo del menuGroup con canvas 128²), POR DEFECTO OFF;
     anchorMenu() con guarda (pin puesto = NUNCA re-ancla, flotación
     cancelada); hit-test propio del rayo por mano (hover -2); pulso =
     _menuPinToggle (ancla/suelta, arpegio + háptica + rótulo); i18n
     menu_pin_on/off ES/EN (c00). Al soltar vuelve a anclarse a la cabeza.
  2) FÍSICA DEL GOLPE FUERTE (c02+c05): techo de pala 12→16, techo de bola
     14→18, filtro de mano más rápido (ventana 0,045→0,032 · lerp 0,85→0,90),
     empuje de cuerpo 0,22→0,40 y DIRECCIÓN AL OBJETIVO (la salida gira
     hacia el swing hasta 45° en swings vivos; jugador only, sin saque,
     sólo intercambio, jamás invierte el cruce).
  3) CPU INTELIGENTE (c06): el fallo es ESFUERZO — base tibia (missBase×0,25),
     bolas rápidas (+0,06/m/s sobre 7) y escoradas/colocación extrema
     (+0,60/m de viaje sobre 0,85); tope 0,85; portal intacto. La IA ya no
     regala puntos con bolas cómodas a la pala.
  4) SUPERPODERES JUSTOS (5 campeonatos): el flanco del anuncio se INVIERTEn
     — el poder se anuncia SÓLO con la bola yendo hacia el RIVAL
     (vel.z < -0,35), nunca con la bola viniendo hacia el jugador: el
     congelado del cartel ya no roba el golpeo. Locura/Magia/Oeste/
     Halloween/Orbital.
  5) LA LOCURA · ETAPA 4 (ARKANOID 2) RELAJADA: 9×5=45 ladrillos (antes 54),
     210 s (antes 150), blueStart 0,24 (antes 0,30), convertFirst 20 s
     (antes 12), convertEvery 11 s (antes 7), bombaCada 20 s (antes 15).
  6) REGRESIÓN: r112 estilos, r111 diorama, r110 bit4, r109 PWA, r62 mega.
"""
import json
import os
import re
import socket
import subprocess
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

RAIZ = '/home/z/my-project'
OK = []
FAIL = []


def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)


V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
VER = V['version']

print('== ESTÁTICA (game.html · r113) ==')
GH = open(os.path.join(RAIZ, 'public/game.html'), encoding='utf-8').read()

# ── 1 · CHINCHETA (c12 dentro del build) ──
AGUJAS_PIN = [
    ('this.menuPin = false;', 'chincheta: OFF por defecto (petición expresa)'),
    ('this._menuPinMesh = new THREE.Mesh(', 'chincheta: quad propio del panel'),
    ('this._menuPinMesh.position.set(0, 0.707, 0.006);', 'chincheta: centro superior del panel'),
    ('_menuPinDraw() {', 'chincheta: dibujo del icono (OFF plateado / ON dorado)'),
    ('if (this.menuPin) { this._menuAnchorUntil = 0; return; }',
     'chincheta: anchorMenu NO re-ancla con el pin puesto'),
    ('_menuPinToggle(hand) {', 'chincheta: pulso = anclar/soltar'),
    ('if (hov === -2) this._menuPinToggle(i);', 'chincheta: el gatillo la pega/suelta (hover -2)'),
    ('if (this.menuOpen && this._menuPinMesh) {', 'chincheta: hit-test del rayo sobre el pin'),
    ("T(this.menuPin ? 'menu_pin_on' : 'menu_pin_off')", 'chincheta: rótulo i18n del estado'),
]
for aguja, nombre in AGUJAS_PIN:
    CHK(aguja in GH, nombre)

# ── 2 · FÍSICA DEL GOLPE FUERTE (c02+c05) ──
AGUJAS_FIS = [
    ('paddleVelClamp: 16,', 'física: techo de pala 12→16 (el smash real ya no se recorta)'),
    ('maxBallSpeed: 18,', 'física: techo de bola 14→18 (golpe fuerte se siente fuerte)'),
    ('velWindow: 0.032,', 'física: ventana del filtro 45→32 ms (el pico llega al contacto)'),
    ('velLerp: 0.90,', 'física: lerp del filtro 0,85→0,90'),
    ('padN * 0.40 * (PK ? PK.power : 1)', 'física: empuje de cuerpo 0,22→0,40'),
    ('r113 · DIRECCIÓN AL OBJETIVO', 'física: bloque de dirección al objetivo'),
    ('const kAim = 0.45 * Math.min(1, (swing - 2.5) / 6);',
     'física: mezcla hasta 45° sólo en swings vivos (>2,5 m/s)'),
    ('pad.who === \'player\' && !pad.serveFlight &&', 'física: dirección SÓLO jugador, nunca en saque'),
    ('if (tmpAim2.z * ball.vel.z >= 0) {', 'física: guardia — jamás invierte el cruce'),
]
for aguja, nombre in AGUJAS_FIS:
    CHK(aguja in GH, nombre)
CHK('paddleVelClamp: 12,' not in GH, 'física: el techo viejo de pala (12) desapareció')
CHK('maxBallSpeed: 14,' not in GH, 'física: el techo viejo de bola (14) desapareció')

# ── 3 · CPU INTELIGENTE (c06) ──
AGUJAS_CPU = [
    ('const viaje = Math.hypot(cx - this.pos.x, cz - this.pos.z);',
     'cpu: viaje = distancia que la IA debe recorrer'),
    ('this.cfg.missBase * 0.25 +', 'cpu: base tibia (la torpeza del nivel, suavizada)'),
    ('Math.max(0, ballSpeed - 7) * 0.06 +', 'cpu: bolas rápidas pagan (+0,06/m/s sobre 7)'),
    ('Math.max(0, viaje - 0.85) * 0.60 +', 'cpu: escoradas/colocación extrema pagan (+0,60/m sobre 0,85)'),
    ('Math.min(0.85,', 'cpu: tope honesto del fallo (0,85)'),
]
for aguja, nombre in AGUJAS_CPU:
    CHK(aguja in GH, nombre)
CHK('Math.max(0, ballSpeed - 7) * 0.05' not in GH,
    'cpu: el fallo viejo plano (×0,05 sin esfuerzo) desapareció')

# ── 4 · SUPERPODERES JUSTOS (5 campeonatos, ficheros servidos) ──
print('== CAMPEONATOS (flanco invertido + ARK2) ==')
FLANCOS = {
    'locura': ('const toward = ball.vel.z < -0.35;', None),
    'magia': ('const toward = ball.vel.z < -0.35;', None),
    'oeste': ('const toward = ball.vel.z < -0.35;', None),
    'halloween': ('if (!b || !(b.vel.z < -0.35)) return;', None),
    'estacion_orbital': ('const toward = g.ball.vel.z < -0.35;', None),
}
VIEJOS = [
    ('locura', 'ball.vel.z > 0.35'),
    ('magia', 'ball.vel.z > 0.35'),
    ('oeste', 'ball.vel.z > 0.35'),
    ('halloween', 'b.vel.z > 0.35'),
    ('estacion_orbital', 'g.ball.vel.z > 0.35'),
]
for champ, (aguja, _) in FLANCOS.items():
    t = open(os.path.join(RAIZ, f'public/championships/{champ}/index.js'),
             encoding='utf-8').read()
    CHK(aguja in t, f'{champ}: el poder se anuncia SÓLO con la bola hacia el rival')
for champ, viejo in VIEJOS:
    t = open(os.path.join(RAIZ, f'public/championships/{champ}/index.js'),
             encoding='utf-8').read()
    CHK(viejo not in t, f'{champ}: el flanco viejo (bola hacia el jugador) desapareció')

# ── 5 · LA LOCURA · ETAPA 4 RELAJADA ──
t_loc = open(os.path.join(RAIZ, 'public/championships/locura/index.js'),
             encoding='utf-8').read()
AGUJAS_ARK = [
    ('cols: 9, rows: 5, gap: 0.012,', 'ark2: muro 9×5 (45 ladrillos, antes 54)'),
    ('time: 210,         // r113: 3,5 minutos (antes 2,5)', 'ark2: 210 s'),
    ('blueStart: 0.24,', 'ark2: 24% azules (antes 30%)'),
    ('convertFirst: 20,', 'ark2: gracia 20 s antes de convertir (antes 12)'),
    ('convertEvery: 11,', 'ark2: conversión cada 11 s (antes 7)'),
    ('bombaCada: 20,', 'ark2: bomba cada 20 s (antes 15)'),
]
for aguja, nombre in AGUJAS_ARK:
    CHK(aguja in t_loc, nombre)

# ── 6 · SELLO + i18n + regresión ──
CHK(f'{VER}' in GH, f'sello de versión {VER} presente en el juego')
SW = open(os.path.join(RAIZ, 'public/sw.js'), encoding='utf-8').read()
CHK(f"crazypp-v{VER}" in SW, f'PWA: caché sw.js gobernada por el bump ({VER})')
CHK('menu_pin_off:' in GH and 'menu_pin_on:' in GH, 'i18n: claves de la chincheta (ES)')
CHK('Pushpin: menu follows your head' in GH and 'Pushpin set: menu pinned here' in GH,
    'i18n: claves de la chincheta (EN)')
REGRESION = [
    ('_megaNormReset', 'r62+ hápticas/poderes intactos'),
    ('r110 · SEMÁNTICA DEL BIT 4', 'r110 fix de duelo presente'),
    ("navigator.serviceWorker.register('sw.js'", 'r109 PWA intacta'),
    ('LA MESA DE LA CASA — RETIRADA', 'r114 diorama retirado (petición del dueño)'),
    ("localStorage.getItem('pp_estilo_v1') || 'clasico'", 'r112 estilos intactos'),
]
for aguja, nombre in REGRESION:
    CHK(aguja in GH, 'regresión: ' + nombre)
CHK('_demoMuseoConstruir()' not in GH,
    'r114: el diorama IA-vs-IA del Hall está FUERA del servido')

# ── EN VIVO: la chincheta respira (menú + ancla + toggle) ──
print('== EN VIVO (chincheta del menú) ==')


def _puerto_libre():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


PORT = _puerto_libre()


def _servir():
    # parcial con directory (el class-attr NO funciona: __init__ lo pisa)
    from functools import partial
    clase = partial(SimpleHTTPRequestHandler,
                    directory=os.path.join(RAIZ, 'public'))
    clase.log_message = lambda *a, **k: None
    httpd = HTTPServer(('127.0.0.1', PORT), clase)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


_httpd = _servir()
try:
    from playwright.sync_api import sync_playwright
    JS_PIN = """(() => {
      const g = window.__PP_GAME;
      if (!g) return { err: 'sin __PP_GAME' };
      const r = {};
      r.menuPin0 = g.menuPin;
      r.tieneMesh = !!g._menuPinMesh;
      r.hijoDelGrupo = !!(g._menuPinMesh && g._menuPinMesh.parent === g.menuGroup);
      r.canvas128 = !!(g._menuPinCv && g._menuPinCv.width === 128);
      // abre el menú y ancla
      g.menuOpen = true; g.menuGroup.visible = true; g.anchorMenu();
      const p0 = g.menuGroup.position.clone();
      // pin ON: anchorMenu NO mueve el panel aunque la cámara cambie
      g._menuPinToggle(0);
      r.menuPinTrasPulso = g.menuPin;
      g.menuGroup.position.x += 3.33;   // simulación: el panel en otro sitio
      g.anchorMenu();
      r.fijoConPin = Math.abs(g.menuGroup.position.x - (p0.x + 3.33)) < 1e-6;
      // pin OFF: soltar re-ancla delante de la cabeza
      g._menuPinToggle(0);
      r.menuPinTrasSoltar = g.menuPin;
      g.anchorMenu();
      r.reanclado = Math.abs(g.menuGroup.position.x - (p0.x + 3.33)) > 0.5;
      // cierre limpio
      g.menuOpen = false; g.menuGroup.visible = false;
      return r;
    })()"""
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                     '--use-angle=swiftshader',
                                     '--autoplay-policy=no-user-gesture-required'])
        pg = b.new_page(viewport={'width': 320, 'height': 240})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
        # espera POLLEADA a __PP_GAME (el boot es asíncrono: modelos/audio)
        for _ in range(40):
            if pg.evaluate('!!window.__PP_GAME'):
                break
            pg.wait_for_timeout(500)
        pg.wait_for_timeout(1200)
        pg.mouse.click(640, 600)
        pg.wait_for_timeout(1200)
        r = pg.evaluate(JS_PIN)
        if r.get('err'):
            CHK(False, 'en vivo: ' + r['err'])
        else:
            CHK(r.get('menuPin0') is False, 'en vivo: chincheta nace OFF')
            CHK(r.get('tieneMesh'), 'en vivo: el quad de la chincheta existe')
            CHK(r.get('hijoDelGrupo'), 'en vivo: la chincheta viaja con el panel')
            CHK(r.get('canvas128'), 'en vivo: lienzo del icono 128²')
            CHK(r.get('menuPinTrasPulso') is True, 'en vivo: pulso → pin ON')
            CHK(r.get('fijoConPin'), 'en vivo: con pin puesto anchorMenu NO mueve el panel')
            CHK(r.get('menuPinTrasSoltar') is False, 'en vivo: segundo pulso → pin OFF')
            CHK(r.get('reanclado'), 'en vivo: al soltar el panel vuelve a anclarse')
        CHK(not errs, 'en vivo: cero excepciones de página ' + (str(errs[:2]) if errs else ''))
        b.close()
except ImportError:
    CHK(False, 'en vivo: playwright no disponible (capa estática ya validada)')
finally:
    _httpd.shutdown()

print(f"\nRESULTADO: {len(OK)} OK · {len(FAIL)} FALLOS")
if FAIL:
    print('\nFALLOS:')
    for f in FAIL:
        print('  ✗ ' + f)
    raise SystemExit(1)
print('CAPA r113 VERDE: chincheta del menú, física del golpe fuerte,')
print('CPU inteligente, superpoderes justos en 5 campeonatos y etapa 4 relajada.')
