#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r110_v36100.py — capa de QA de la ronda 110 (V3.6.102-SDK6).

HITO M4 del roadmap MEJORAS.md · ONBOARDING < 60 SEGUNDOS.

  1) JUGAR YA: la oferta de primera vez salta DIRECTO al rally real (menú
     cerrado) y deja una sola línea de saque (m4_hint) marcada como vista
     en localStorage (ppxr_m4_hint) — sin repetirse nunca.
  2) DEMO VIVA DETRÁS DEL MENÚ: con el menú abierto en VR y un partido
     virgen esperando saque, la demo juega el lado del jugador con la
     MISMA OpponentAI honesta del rival (saca, golpea en el rallye); los
     puntos de la demo NO cuentan (marcador virgen 0-0 y saque limpio);
     el volumen de efectos se atenúa mientras juega y se restaura al
     cerrar; la portada 2D sigue igual (la retirada v2.30 se respeta).
  3) TELEMETRÍA primer_rally (una vez por sesión, sin la demo): mide
     cuánto tarda el jugador en estar en un rally real (<60 s, criterio).
  4) REGRESIÓN: r109 (PWA), r106 (háptica), r105 (menú), r104, r102, r62.
"""
import functools, json, os, subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8846
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
VER = V['version']

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (game.html) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8').read()

AGUJAS = [
    ('r110 · M4 · DEMO VIVA DETRÁS DEL MENÚ', 'comentario del hito presente'),
    ('this._demoMenuOn = demoDetras;', 'flip sticky de la demo del menú'),
    ('if (presenting && !this._demoMenuOn) {   // r110: con la demo del menú activa, saca la demo',
     'el saque del jugador cede a la demo mientras el menú está abierto'),
    ('LA DEMO VUELVE A GOLPEAR POR SU LADO', 'la demo golpea en el rallye (v2.30 revertido SOLO en menú)'),
    ('this.demoPaddleMesh.visible = !presenting || this._demoMenuOn;',
     'pala de la demo visible detrás del menú'),
    ('el punto de la demo NO cuenta', 'rollback del punto de la demo (marcador virgen)'),
    ("window.__PP_TELE.ev('primer_rally', { s: sPrimer })", 'telemetría primer_rally'),
    ('El rally de la DEMO tras el menú NO cuenta', 'la demo se excluye del primer_rally'),
    ('ppxr_m4_hint', 'marca localStorage del aviso de saque'),
    ("gme.rules.message = T('m4_hint');", 'una línea de saque al saltar la oferta'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

# i18n ES/EN
CHK("tutask_no: '▶ JUGAR YA'" in GH, 'i18n ES: oferta con ▶ JUGAR YA')
CHK("tutask_no: '▶ PLAY NOW'" in GH, 'i18n EN: oferta con ▶ PLAY NOW')
CHK("m4_hint: 'SAQUE:" in GH, 'i18n ES: m4_hint')
CHK("m4_hint: 'SERVE:" in GH, 'i18n EN: m4_hint')

# catálogo de telemetría
cat = json.load(open(os.path.join(RAIZ, 'scripts/telemetria_catalogo.json')))
CHK(cat.get('version') == 6 and cat.get('ronda') == 110, 'catálogo: v6 · ronda 110')
CHK(any(e['nombre'] == 'primer_rally' for e in cat['eventos']), 'catálogo: primer_rally documentado')

# versión sellada (tras el bump)
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.102-SDK6', 'c00: VERSION sella 3.6.102-SDK6')
CHK('>V3.6.102-SDK6</span>' in open(os.path.join(RAIZ, 'src/game/03_body.html'), encoding='utf-8').read(),
    'portada: badge V3.6.102-SDK6')
CHK(V.get('fase') == 102, 'VERSION.json: FASE 102')
CHK(V.get('hub') == 'v36102-sdk6', 'VERSION.json: hub v36102-sdk6')

# regresión
CHK("const CACHE = 'crazypp-v3.6.102-SDK6';" in open(os.path.join(PUB, 'sw.js'), encoding='utf-8').read(),
    'r109: sw.js CACHE sellada a la nueva versión (bump gobierna la caché)')
CHK('const s6 = Math.min(1, e.speed / 6);' in GH, 'r106: háptica del bote intacta')
CHK('this.menuTex.generateMipmaps = false;' in GH, 'r105: mips OFF intacto')
CHK('const MENU_FS = 1.16;' in GH, 'r104: fuentes ×1,16 intactas')
CHK('PROTO: 2,' in GH, 'r102: pala rival FIEL intacta')
CHK("const nombres = ['mesa', 'pala', 'canto', 'red', 'suelo'];" in GH, 'r62: SFX reales intactos')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo: JUGAR YA + demo detrás del menú + primer_rally) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

SHOTS = os.path.join(RAIZ, 'scripts', 'qa_shots_r110')
os.makedirs(SHOTS, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)

    # ---- 1 · JUGAR YA: saltar la oferta = menú cerrado + aviso una vez
    pg.evaluate("() => { try { localStorage.removeItem('pp_tut_done'); localStorage.removeItem('pp_tut_asked'); localStorage.removeItem('ppxr_m4_hint'); } catch (e) {} }")
    salto = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      g.rules.message = '';
      window.__PP_TUT.menuAction(g, 'no');
      return {
        abierto: g.menuOpen, pagina: g.menuPage,
        msg: (g.rules.message || '').slice(0, 60),
        marca: localStorage.getItem('ppxr_m4_hint'),
        esHint: (g.rules.message || '').indexOf('SAQUE') === 0,
      };
    }""")
    CHK(salto.get('abierto') is False and salto.get('pagina') == 'main',
        'JUGAR YA: menú cerrado y de vuelta al juego (%s)' % salto)
    CHK(salto.get('marca') == '1' and salto.get('esHint') is True,
        'JUGAR YA: aviso de saque una línea (marcado en localStorage)')
    salto2 = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      g.rules.message = '';
      window.__PP_TUT.menuAction(g, 'no');
      return { msg: g.rules.message || '', marca: localStorage.getItem('ppxr_m4_hint') };
    }""")
    CHK(salto2.get('msg') == '' and salto2.get('marca') == '1',
        'JUGAR YA: el aviso NO se repite (ya visto)')

    # ---- 2 · DEMO DETRÁS DEL MENÚ (XR simulado presente + reloj propio)
    pg.evaluate("""() => {
      const g = window.__PP_GAME;
      g.rules.startMatch('match');                 // partido VIRGEN
      g.rules.state = 'serve'; g.rules.server = 'player';
      g._fxVolPrev = null; g._demoMenuOn = false;
      window.__fxVolAntes = g.audio.fxVol;
      window.__xrReal = g.renderer.xr;             // restaurar al final
      // XR simulado SIN sustituir el objeto: three llama a métodos reales en
      // render (getEnvironmentBlendMode) — sólo ensombrecemos isPresenting.
      Object.defineProperty(g.renderer.xr, 'isPresenting', { value: true, configurable: true });
      g.toggleMenu();                              // menú abierto en VR
      g.renderer.setAnimationLoop(null);           // reloj propio del QA
      window.__t0 = performance.now() + 800;
      window.__tMs = window.__t0 + 16;
      window.__paso = () => { window.__tMs += 16.7; g.animate(window.__tMs); };
      window.__stats = { maxPuntos: 0, vioRally: false, golpesDemo: 0, sacoDemo: false };
      const origReg = g.rules.registerPaddleHit.bind(g.rules);
      g.rules.registerPaddleHit = (who) => {
        if (who === 'player') window.__stats.golpesDemo++;
        return origReg(who);
      };
    }""")
    # conduce ~22 s de juego en tandas (SwiftShader: presupuesto de pared)
    pg.evaluate("""() => { const t0 = performance.now();
      while (window.__tMs - window.__t0 < 6000 && performance.now() - t0 < 4800) window.__paso(); }""")
    paso1 = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      return { on: g._demoMenuOn, fx: g.audio.fxVol, antes: window.__fxVolAntes,
               visible: g.demoPaddleMesh.visible, estado: g.rules.state,
               marcador: [g.rules.scorePlayer, g.rules.scoreAi] };
    }""")
    CHK(paso1.get('on') is True, 'demo: el menú abierto la ACTIVA (partido virgen al saque)')
    CHK(abs((paso1.get('fx') or 0) - 0.3) < 1e-6 and (paso1.get('antes') or 0) > 0.3,
        'demo: efectos atenuados a 0,3 mientras juega (antes %s)' % paso1.get('antes'))
    CHK(paso1.get('visible') is True, 'demo: pala de la demo VISIBLE')
    for _ronda in range(3):
        pg.evaluate("""() => { const t0 = performance.now();
          while (window.__tMs - window.__t0 < %d && performance.now() - t0 < 4800) {
            window.__paso();
            const g = window.__PP_GAME, s = window.__stats;
            if (g.rules.state === 'rally') s.vioRally = true;
            s.maxPuntos = Math.max(s.maxPuntos, g.rules.scorePlayer + g.rules.scoreAi);
            if (g.ball && g.ball.vel.lengthSq() > 1 && g.rules.state === 'serve') s.sacoDemo = true;
          } }""" % (6000 * (_ronda + 2)))
    vivo = pg.evaluate("""() => {
      const g = window.__PP_GAME, s = window.__stats;
      return { on: g._demoMenuOn, golpes: s.golpesDemo, vioRally: s.vioRally,
               maxPuntos: s.maxPuntos, marcador: [g.rules.scorePlayer, g.rules.scoreAi],
               estado: g.rules.state, primerRally: window.__ppPrimerRally === undefined ? 'ausente' : 'presente' };
    }""")
    CHK(vivo.get('golpes', 0) >= 1, 'demo: la demo GOLPEA en el rallye (registro %s golpes de su lado)' % vivo.get('golpes'))
    CHK(vivo.get('maxPuntos', 9) <= 1 and vivo.get('marcador') == [0, 0],
        'demo: los puntos de la demo NO cuentan (marcador final %s · máximo visto %s — 1 frame antes del rollback)'
        % (vivo.get('marcador'), vivo.get('maxPuntos')))
    CHK(vivo.get('primerRally') == 'ausente',
        'primer_rally: la demo NO lo dispara (se mide al JUGADOR)')
    # cierre del menú → recogida en paz (pasos FIJOS: determinista, sin
    # depender del ritmo de SwiftShader — 600 pasos = 10 s de juego)
    pg.evaluate("""() => { window.__PP_GAME.toggleMenu(); }""")
    cierre = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      for (let i = 0; i < 600; i++) window.__paso();
      return { on: g._demoMenuOn, fx: g.audio.fxVol, antes: window.__fxVolAntes,
               estado: g.rules.state, servidor: g.rules.server,
               menu: g.menuOpen, hall: g.inHall,
               marcador: [g.rules.scorePlayer, g.rules.scoreAi] };
    }""")
    CHK(cierre.get('on') is False, 'cierre: la demo se recoge (menú cerrado · dump %s)' % cierre)
    CHK(abs((cierre.get('fx') or 0) - (cierre.get('antes') or 0)) < 1e-6,
        'cierre: volumen de efectos RESTAURADO (%s → %s)' % (cierre.get('antes'), cierre.get('fx')))
    CHK(cierre.get('estado') == 'serve' and cierre.get('servidor') == 'player' and cierre.get('marcador') == [0, 0],
        'cierre: partido limpio al saque del jugador sin puntos inflados (%s/%s %s)' %
        (cierre.get('estado'), cierre.get('servidor'), cierre.get('marcador')))
    # restaurar el xr real (el bucle NO se restaura: el reloj sintético quedó
    # POR DELANTE del real y un rAF posterior daría dt negativo — lección r107)
    pg.evaluate("""() => { const g = window.__PP_GAME;
      delete g.renderer.xr.isPresenting;           // vuelve el getter del prototipo
      if (window.__xrReal) g.renderer.xr = window.__xrReal; }""")
    pg.wait_for_timeout(600)

    pg.screenshot(path=os.path.join(SHOTS, 'r110_menu.png'))
    CHK(errs == [], 'RUNTIME: cero pageerrors (%s)' % (errs or 'limpio'))
    b.close()

srv.shutdown()

print('\n== RESUMEN qa_r110_v36100 ==')
print('  OK: %d · FALLOS: %d' % (len(OK), len(FAIL)))
if FAIL:
    print('\n'.join('  ✗ ' + f for f in FAIL))
    raise SystemExit(1)
print('  VERDE: M4 — JUGAR YA + demo viva tras el menú + primer_rally (sin la demo)')
