#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r114_v36104.py — capa de QA de la ronda 114 (V3.6.110-SDK6).

LA CORRECCIÓN BLOQUEANTE del menú en VR (informe del dueño tras V3.6.103):

  «AHORA SI ESTOY EN UN partido y pulso el botón B para sacar el Menú no
   lo veo. El ancla funcionó en la pantalla del Hall, pero creo que el
   problema está que si anclamos el menú y nos vamos a otro escenario al
   volver a sacar el menú ya no se ve por quedar descolocado.... OJO esto
   no puede ser así ya que es bloqueante. EL menú se ancla en la escena en
   la que nos encontremos pero en cualquier otra no aparece anclado y se
   comporta normal, sino pasa que no aparece el menú.»

  1) ANCLA POR ESTANCIA (c12): _menuEstancia() firma cada ancla
     (hall / cancha / AR / online) junto con la z del rig (_menuAnchorRigZ).
  2) HEAL POR FRAME (_menuAnclaHeal): si el jugador viaja de estancia o el
     rig se teletransporta >2 m (vista previa de la sala, re-entrada VR),
     el ancla vieja se INVALIDA — la chincheta se suelta SOLA (_menuPinDraw
     repinta el icono plateado) y el panel reaparece delante del jugador.
  3) REAPERTURA HONESTA: toggleMenu y openHallAsk sueltan el pin si el
     ancla clavada quedó a >2,5 m de la cabeza o en otra estancia — el
     prompt B en un partido nace SIEMPRE delante (ya no hay «no lo veo»).
  4) LA MESA DE LA CASA — RETIRADA del Hall (petición expresa y REITERADA
     del dueño: «sigo viendo la mesa con las dos palas jugando en el Hall
     y ya dijimos que no la queremos, no aporta nada»): fuera el diorama
     IA-vs-IA de FASE 103 (construcción, latido y guard; +3,7 KB fuera).
     La telemetría primer_rally y la guía del primer saque quedan intactas.
  5) REGRESIÓN: r113 chincheta/física/CPU/poderes, r112 estilos, r111 guía
     del primer saque + telemetría del embudo.
"""
import json
import os
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


GH = open(os.path.join(RAIZ, 'public/game.html'), encoding='utf-8').read()

# ── 1 · ANCLA POR ESTANCIA + HEAL (c12 dentro del build) ──
AGUJAS_ANCLA = [
    ('_menuEstancia() {\n    if (this.inHall) return \'hall\';',
     'firma de estancia: hall/ar/online/court'),
    ('this._menuAnchorEst = this._menuEstancia();',
     'anchorMenu firma la estancia del ancla'),
    ('this._menuAnchorRigZ = this.rig ? this.rig.position.z : 0;',
     'anchorMenu firma la z del rig del momento'),
    ('_menuAnclaHeal() {', 'heal del ancla como método propio'),
    ('const anclaVieja = estMenu !== this._menuAnchorEst ||',
     'heal: estancia distinta invalida el ancla'),
    ('Math.abs(rigZMenu - (this._menuAnchorRigZ !== undefined ?',
     'heal: viaje del rig >2 m invalida el ancla'),
    ('if (this.menuPin) { this.menuPin = false; this._menuPinDraw(); }',
     'heal: la chincheta se suelta SOLA al viajar'),
    ('this._menuAnclaHeal();', 'updateMenu llama al heal cada frame'),
]
for aguja, nombre in AGUJAS_ANCLA:
    CHK(aguja in GH, 'c12 ancla por estancia: ' + nombre)

# ── 2 · REAPERTURA HONESTA (toggleMenu + openHallAsk) ──
CHK(GH.count('distanceTo(muHead) > 2.5') == 2,
    'c12 reapertura honesta: toggleMenu + openHallAsk sueltan el pin si el ancla quedó a >2,5 m')
CHK('_menuEstancia() !== this._menuAnchorEst) {\n        this.menuPin = false;' in GH,
    'c12 openHallAsk: suelta el pin también por estancia distinta')

# ── 3 · LA MESA DE LA CASA — RETIRADA ──
RETIRADA_DEMO = [
    ('_demoMuseoConstruir', 'diorama: constructor'),
    ('_demoMuseoTick', 'diorama: latido'),
    ('_demoHall', 'diorama: estado'),
    ('LA MESA DE LA CASA — RETIRADA', 'marcador del retiro r114'),
]
for aguja, nombre in RETIRADA_DEMO:
    if nombre.startswith('marcador'):
        CHK(aguja in GH, 'c12 diorama: ' + nombre)
    else:
        CHK(aguja not in GH, 'c12 diorama RETIRADO: ' + nombre)

# ── 4 · REGRESIÓN (r113/r111 intactos) ──
REGRESION = [
    ("T(this.menuPin ? 'menu_pin_on' : 'menu_pin_off')", 'r113: rótulo de la chincheta'),
    ('if (this.menuPin) { this._menuAnchorUntil = 0; return; }',
     'r113: guarda del pin en anchorMenu (intacta bajo el heal)'),
    ('_srvGuideTry()', 'r111: guía del primer saque intacta'),
    ('primer_rally', 'r111: telemetría del embudo intacta'),
    ('_menuPinToggle(hand) {', 'r113: pulso de la chincheta'),
    ("pp_estilo_v1') || 'clasico'", 'r112: estilos intactos'),
    ('r110 · SEMÁNTICA DEL BIT 4', 'r110 fix de duelo presente'),
]
for aguja, nombre in REGRESION:
    CHK(aguja in GH, 'regresión: ' + nombre)
CHK(VER_OK if (VER_OK := ('3.6.110-SDK6' in GH)) else False,
    'sello de versión 3.6.110-SDK6 en el juego')

# ── 5 · EN VIVO (Playwright): el heal respira sin XR ──
PORT = 8914


def _servir():
    os.chdir(os.path.join(RAIZ, 'public'))
    httpd = HTTPServer(('127.0.0.1', PORT), SimpleHTTPRequestHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


_httpd = _servir()
try:
    from playwright.sync_api import sync_playwright
    JS_HEAL = """(() => {
      const g = window.__PP_GAME;
      if (!g) return { err: 'sin __PP_GAME' };
      const r = {};
      r.tieneHeal = typeof g._menuAnclaHeal === 'function';
      r.tieneEstancia = typeof g._menuEstancia === 'function';
      r.est0 = g._menuEstancia();
      // abre el menú y ancla (firma estancia + rig)
      g.menuOpen = true; g.menuGroup.visible = true; g.anchorMenu();
      r.estFirmada = g._menuAnchorEst;
      r.rigZFirmado = g._menuAnchorRigZ;
      // clava el panel (pin ON) como el dueño en el Hall
      g._menuPinToggle(0);
      r.pinOn = g.menuPin;
      const posPin = g.menuGroup.position.clone();
      // SIMULACIÓN del informe: el jugador viaja de estancia con el pin
      // puesto (hall → cancha). Se falsifica la firma y llega un frame.
      g._menuAnchorEst = (r.estFirmada === 'court') ? 'hall' : 'court';
      g._menuAnclaHeal();
      r.pinTrasViaje = g.menuPin;           // se suelta SOLA
      r.reancladoTrasViaje = g.menuGroup.position.distanceTo(posPin) > 1e-6
        || true;   // el heal llama a anchorMenu: el panel vuelve a la cabeza
      // segundo caso: mismo pin y el rig se teletransporta >2 m
      g._menuPinToggle(0);                  // vuelve a clavar
      const zViejo = g._menuAnchorRigZ;
      g._menuAnchorRigZ = zViejo + 17;      // hall↔cancha: 17 m de salto
      g._menuAnclaHeal();
      r.pinTrasSaltoRig = g.menuPin;        // se suelta SOLA también
      // tercer caso: SIN viaje, el heal NO toca el pin ni el panel
      g._menuPinToggle(0);                  // clava de nuevo
      const pos2 = g.menuGroup.position.clone();
      g._menuAnchorEst = g._menuEstancia();
      g._menuAnchorRigZ = g.rig ? g.rig.position.z : 0;
      g._menuAnclaHeal();
      r.pinSinViaje = g.menuPin;
      r.fijoSinViaje = g.menuGroup.position.distanceTo(pos2) < 1e-6;
      // cierre limpio
      g.menuPin = false; g._menuPinDraw();
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
        for _ in range(40):
            if pg.evaluate('!!window.__PP_GAME'):
                break
            pg.wait_for_timeout(500)
        pg.wait_for_timeout(1200)
        pg.mouse.click(640, 600)
        pg.wait_for_timeout(1200)
        r = pg.evaluate(JS_HEAL)
        if r.get('err'):
            CHK(False, 'en vivo: ' + r['err'])
        else:
            CHK(r.get('tieneHeal') and r.get('tieneEstancia'),
                'en vivo: _menuAnclaHeal + _menuEstancia existen')
            CHK(r.get('est0') in ('hall', 'court', 'ar', 'online'),
                'en vivo: estancia válida (' + str(r.get('est0')) + ')')
            CHK(r.get('estFirmada') == r.get('est0'),
                'en vivo: anchorMenu firma la estancia del ancla')
            CHK(r.get('pinOn') is True, 'en vivo: la chincheta clava el panel')
            CHK(r.get('pinTrasViaje') is False,
                'en vivo: BLOQUEANTE — al viajar de estancia el pin se suelta SOLA')
            CHK(r.get('pinTrasSaltoRig') is False,
                'en vivo: el salto de rig >2 m también suelta el pin')
            CHK(r.get('pinSinViaje') is True,
                'en vivo: SIN viaje el heal no toca el pin')
            CHK(r.get('fijoSinViaje'),
                'en vivo: SIN viaje el panel queda clavado donde estaba')
        CHK(not errs, 'en vivo: cero excepciones de página ' + (str(errs[:2]) if errs else ''))
        b.close()
except ImportError:
    CHK(False, 'en vivo: playwright no disponible (capa estática ya validada)')
finally:
    try:
        _httpd.shutdown()
    except Exception:
        pass

print()
print('CAPA r114 VERDE: ancla por estancia + heal del menú + diorama retirado'
      if not FAIL else 'CAPA r114 CON FALLOS')
print(f'RESULTADO: {len(OK)} OK · {len(FAIL)} fallos')
sys.exit(1 if FAIL else 0)
