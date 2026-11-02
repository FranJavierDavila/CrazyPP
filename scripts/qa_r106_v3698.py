#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r106_v3698.py — capa de QA de la ronda 106 (V3.6.99-SDK6).

HITO M1 del roadmap MEJORAS.md · GAME FEEL — hápticas calibradas.
(Auditoría corregida: la mitad de AUDIO de M1 ya existía desde r62 «SFX
REALES» — muestras modales + rate por velocidad + jitter; se verifica aquí
como regresión. Lo que r106 implementa es la HÁPTICA:)

  1) BOTE DE MESA: antes 0,18 FIJA y FUERA del guard anti-spam de 60 ms
     (cada evento de mesa vibraba: ráfaga esquina+canto = ametralladora).
     Ahora DENTRO del guard y proporcional a la velocidad:
       bote llano  → 0,08 + 0,16·s  · 50–80 ms
       canto (edge)→ 0,14 + 0,16·s  · 28 ms (pico más alto, seco)
  2) RED: vibración sutil nueva 0,15 / 45 ms (el roce de la malla se siente).
  3) REGRESIÓN cero: SFX reales r62 (5 muestras + rate), háptica de pala
     escalada r62, panel/fuentes r104, mips/throttle/cursor r105.
"""
import functools, json, os, re as _re
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8843
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (game.html) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8').read()

AGUJAS = [
    # 1 · M1 · háptica del bote calibrada (dentro del guard)
    ('M1 · r106 · HÁPTICA DEL BOTE CALIBRADA',
     'comentario de la M1 presente (bote calibrado, guard, canto)'),
    ('const s6 = Math.min(1, e.speed / 6);',
     's6: velocidad normalizada del bote (0→1)'),
    ('this.haptic(this.paddleHand, 0.08 + 0.16 * s6, Math.round(50 + 30 * s6));',
     'bote llano: amplitud 0,08–0,24 y duración 50–80 ms por velocidad'),
    ('this.haptic(this.paddleHand, 0.14 + 0.16 * s6, 28);',
     'canto: pico más alto (0,14–0,30) y seco (28 ms)'),
    # 2 · M1 · red palpable
    ('this.haptic(this.paddleHand, 0.15, 45);',
     'red: vibración sutil 0,15 / 45 ms (M1)'),
    ('el roce de la malla SE SIENTE',
     'comentario de intención de la red palpable'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

RETIRADAS = [
    ('this.haptic(this.paddleHand, 0.18);',
     'háptica del bote FIJA 0,18 RETIRADA (era ametralladora fuera del guard)'),
]
for aguja, nombre in RETIRADAS:
    CHK(aguja not in GH, 'game.html: ' + nombre)

# r62 · SFX REALES intactos (regresión de audio — la otra mitad de M1)
CHK("const nombres = ['mesa', 'pala', 'canto', 'red', 'suelo'];" in GH,
    'r62: 5 muestras físicas intactas (mesa/pala/canto/red/suelo)')
CHK('return (lo + (hi - lo) * s) * jit;' in GH,
    'r62: rate por velocidad + jitter ±1,5 % intacto')
CHK('src.playbackRate.value = Math.max(0.5, Math.min(2.2, rate));' in GH,
    'r62: playbackRate de la muestra intacto')
CHK('if (this._playReal(\'pala\', pan, 0.72 * s,' in GH,
    'r62: pala toca muestra real con fallback intacto')
CHK('if (this._playReal(\'canto\', pan, 0.42 * s,' in GH,
    'r62: canto con muestra propia intacto')

# r105/r104/r102/r103/r101 intactas (regresión cero)
CHK('this.menuTex.generateMipmaps = false;' in GH, 'r105: mips OFF intacto')
CHK('if ((nowH - (this._menuHoverDrawAt || 0)) >= 90) {' in GH,
    'r105: throttle de hover 90 ms intacto')
CHK('dot.position.set((hit.uv.x - 0.5) * 0.90, (hit.uv.y - 0.5) * 1.35, 0.004);' in GH,
    'r105: cursor en el plano REAL 0,90×1,35 intacto')
CHK('new THREE.PlaneGeometry(0.90, 1.35),' in GH, 'r104: panel 0,90×1,35 intacto')
CHK('const MENU_FS = 1.16;' in GH, 'r104: fuentes ×1,16 intactas')
CHK('PROTO: 2,' in GH, 'r102: pala rival FIEL intacta (códec)')
CHK('const BARRA_LBL_X = () => HW() + 0.42;' in GH, 'r103: rótulo derecha intacto')

# versión sellada
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.99-SDK6', 'c00: VERSION sella 3.6.99-SDK6')
CHK('>V3.6.99-SDK6</span>' in open(os.path.join(RAIZ, 'src/game/03_body.html'), encoding='utf-8').read(),
    'portada: badge V3.6.99-SDK6')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 100, 'VERSION.json: FASE 100')
CHK(V.get('hub') == 'v3699-sdk6', 'VERSION.json: hub v3699-sdk6')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo: háptica calibrada con eventos inyectados) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

SHOTS = os.path.join(RAIZ, 'scripts', 'qa_shots_r106')
os.makedirs(SHOTS, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(2000)

    # ---- 1 · M1 · háptica del bote/red con eventos sintéticos reales
    hap = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      if (!g) return { err: 'sin __PP_GAME' };
      // en escritorio xr.isPresenting es false y las hápticas de proceso no
      // suenan: se sustituye el XR del renderer por uno PRESENTE (M1 vivo)
      const xrReal = g.renderer.xr;
      g.renderer.xr = { isPresenting: true };
      const llamadas = [];
      const orig = g.haptic.bind(g);
      g.haptic = (i, a, m) => { llamadas.push([i, +a.toFixed(3), m]); return orig(i, a, m); };
      const P = (x, z) => ({ x, y: 0.78, z });
      try {
        g.processEvents([
          { type: 'table', speed: 1.2, pos: P(0.3, 0.2) },   // bote suave → ÚNICO con vibración (guard)
          { type: 'table', speed: 5.9, pos: P(-0.3, 0.2) },  // ráfaga en el mismo instante → sin vibrar
          { type: 'floor', speed: 4.0, pos: P(0.0, 0.5) },   // suelo: sin háptica
          { type: 'wall',  speed: 3.0, pos: P(0.0, 0.5) },   // muro: sin háptica
        ]);
        var trasRafaga = llamadas.slice();
        llamadas.length = 0;
        g._lastBounceSfx = 0;   // el guard expira: el siguiente bote SÍ vibra
        g.processEvents([
          { type: 'table', edge: true, speed: 5.9, pos: P(0.25, 0.2) },  // canto
          { type: 'net',   speed: 4.2, pos: P(-0.2, 0.0) },              // red
        ]);
        var cantoRed = llamadas.slice();
      } finally {
        g.haptic = orig;
        g.renderer.xr = xrReal;
      }
      return { rafaga: trasRafaga, cantoRed: cantoRed,
               s6_softe: 1.2 / 6, s6_hard: 5.9 / 6 };
    }""")
    if 'err' in hap:
        CHK(False, 'RUNTIME háptica: %s' % hap['err'])
    else:
        rf = hap['rafaga']; cr = hap['cantoRed']
        CHK(len(rf) == 1, 'guard vivo: ráfaga de 2 botes → 1 sola vibración (%d)' % len(rf))
        s6s = hap['s6_softe']
        CHK(len(rf) == 1 and abs(rf[0][1] - (0.08 + 0.16 * s6s)) < 1e-6,
            'bote suave: amplitud 0,08+0,16·s en vivo (%s ≈ 0,112)' % (rf[0] if rf else '—'))
        CHK(len(rf) == 1 and rf[0][2] == round(50 + 30 * s6s) and rf[0][0] == 0,
            'bote suave: %d ms en el mando de la pala (50+30·s con s=%.2f)' % (rf[0][2] if rf else -1, s6s))
        CHK(all(r[1] != 0.18 for r in rf), 'la 0,18 fija ha DESAPARECIDO del bote')
        # canto: pico alto y seco
        edge = next((r for r in cr if r[2] == 28), None)
        CHK(edge is not None and abs(edge[1] - round(0.14 + 0.16 * hap['s6_hard'], 3)) < 1e-6,
            'canto: 0,14+0,16·s con 28 ms en vivo (%s)' % (edge or '—'))
        net = next((r for r in cr if r[2] == 45), None)
        CHK(net is not None and abs(net[1] - 0.15) < 1e-6,
            'red: 0,15 / 45 ms en vivo (%s)' % (net or '—'))
        CHK(len(cr) == 2, 'canto+red: exactamente 2 vibraciones, suelo/muro no vibraron')

    # ---- 2 · r62 · audio por capas sigue vivo (la otra mitad de M1)
    au = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const a = g.audio;
      const out = { metodos: ['paddle', 'tableBounce', 'tableEdge', 'net', 'thud']
        .every(k => typeof a[k] === 'function'),
        rate: typeof a._sfxRate === 'function',
        sonan: true };
      try { a.paddle(0, 0.5); a.tableBounce(0, 0.5); a.tableEdge(0, 0.6);
            a.net(0, 0.6); a.thud(0, 0.5); } catch (e) { out.sonan = false; }
      return out;
    }""")
    CHK(au.get('metodos'), 'r62: métodos de impacto por material intactos')
    CHK(au.get('rate'), 'r62: _sfxRate (tono por velocidad + jitter) intacto')
    CHK(au.get('sonan'), 'r62: los 5 impactos suenan sin excepción (con fallback)')

    # ---- 3 · el juego sigue vivo y el menú abre (regresión r105)
    ab = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      try { g.toggleMenu(); } catch (e) { return { err: 'toggle: ' + (e && e.message) }; }
      return { abierto: g.menuOpen, w: g.menuMesh.geometry.parameters.width };
    }""")
    CHK(ab.get('err') is None and ab.get('abierto') is True and abs(ab.get('w', 0) - 0.90) < 1e-9,
        'menú 0,90 m abierto en vivo sin errores (%s)' % (ab.get('err') or 'OK'))
    pg.wait_for_timeout(900)
    pg.screenshot(path=os.path.join(SHOTS, 'menu_abierto_r106.png'))

    CHK(errs == [], 'RUNTIME: cero pageerrors (%s)' % (errs or 'limpio'))
    b.close()

srv.shutdown()

print('\n== RESUMEN qa_r106_v3698 ==')
print('  OK: %d · FALLOS: %d' % (len(OK), len(FAIL)))
if FAIL:
    print('\n'.join('  ✗ ' + f for f in FAIL))
    raise SystemExit(1)
print('  VERDE: M1 — hápticas calibradas (bote/canto/red) + r62/r105 intactos')
