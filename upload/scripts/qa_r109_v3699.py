#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r109_v3699.py — capa de QA de la ronda 109 (V3.6.111-SDK6).

HITO M3 del roadmap MEJORAS.md · PWA INSTALABLE.

  1) FICHEROS PWA: manifest.webmanifest (start_url ./game.html, scope ./,
     display fullscreen, orientation landscape, 3 iconos), sw.js (sello
     const CACHE = crazypp-v<versión> — el 4.º sello físico que el bump
     gobierna; SWR para game.html; network-first para datos vivos;
     cache-first para assets; purga en activate) e iconos de la casa
     (192/512/maskable, PIL: tamaños + contenido no vacío + maskable
     dentro del 80 % central).
  2) PORTADA INSTALADORA (c13): registro del SW en contexto seguro,
     detección standalone, beforeinstallprompt capturado, botón con
     diálogo nativo o caminito manual, toasts #ppToast, telemetría
     pwa_* anónima, i18n ES/EN.
  3) INFRA: deploy_pages SITE_PATHS publica los 5 ficheros · bump_version
     parchea el sello del SW · qa_version verifica la cadena nueva ·
     hub /descargas con la guía PWA · build_zip lleva la PWA a los 4 ZIPs.
  4) REGRESIÓN: r106 (hápticas calibradas), r105 (mips/hover/cursor),
     r104 (panel/fuentes), r102 (pala rival), r62 (SFX reales).
"""
import functools, json, os, subprocess, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from PIL import Image
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8844
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
VER = V['version']

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (game.html + PWA) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8').read()

# 1 · portada instaladora (c13)
AGUJAS = [
    ('r109 · M3 PWA INSTALABLE', 'comentario del hito presente (c13)'),
    ("navigator.serviceWorker.register('sw.js', { scope: './' })",
     'registro del service worker en contexto seguro'),
    ("window.matchMedia('(display-mode: fullscreen)').matches",
     'detección de standalone (fullscreen/standalone/minimal-ui)'),
    ("window.addEventListener('beforeinstallprompt'", 'beforeinstallprompt capturado'),
    ('e.preventDefault();               // el diálogo lo manda NUESTRO botón',
     'el diálogo nativo lo dispara NUESTRO botón'),
    ("window.addEventListener('appinstalled'", 'appinstalled escuchado'),
    ('pwa_standalone', 'telemetría pwa_standalone'),
    ('pwa_prompt', 'telemetría pwa_prompt (con outcome)'),
    ('pwa_installed', 'telemetría pwa_installed'),
    ('pwa_manual_hint', 'telemetría pwa_manual_hint (camino manual)'),
    ('window.__ppPwaToast = ppToast', 'toast reutilizable expuesto (M4)'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

# 2 · i18n ES/EN (c00)
CHK("ov_pwa: '📲 INSTALAR EN EL CASCO'" in GH, 'i18n ES: ov_pwa')
CHK("ov_pwa: '📲 INSTALL ON HEADSET'" in GH, 'i18n EN: ov_pwa')
CHK('pwa_manual: ' in GH and 'pwa_installed: ' in GH, 'i18n: toasts ES (pwa_manual/pwa_installed)')
CHK('pwa_ready: ' in GH, 'i18n: pwa_ready (ES+EN)')

# 3 · head y portada (00_head / 03_body ya dentro del game.html)
CHK('<link rel="manifest" href="manifest.webmanifest" />' in GH,
    'head: link rel=manifest (ruta relativa /CrazyPP/)')
CHK('<meta name="theme-color" content="#0b2050" />' in GH, 'head: theme-color')
CHK('#ppToast {' in GH, 'CSS del toast #ppToast presente')
CHK('id="pwabtn"' in GH and 'data-i18n="ov_pwa"' in GH, 'portada: botón #pwabtn con i18n')

# 4 · manifest.webmanifest
man = json.load(open(os.path.join(PUB, 'manifest.webmanifest')))
CHK(man.get('name', '').startswith('CRAZY PING PONG'), 'manifest: nombre de la casa')
CHK(man.get('start_url') == './game.html' and man.get('scope') == './',
    'manifest: start_url ./game.html + scope ./ (funciona bajo /CrazyPP/)')
CHK(man.get('display') == 'fullscreen', 'manifest: display fullscreen')
CHK(man.get('orientation') == 'landscape', 'manifest: orientation landscape')
CHK(len(man.get('icons', [])) >= 3, 'manifest: 3 iconos declarados')

# 5 · sw.js: sintaxis + sello + estrategias
r = subprocess.run(['node', '--check', os.path.join(PUB, 'sw.js')], capture_output=True, text=True)
CHK(r.returncode == 0, 'sw.js: node --check OK')
SW = open(os.path.join(PUB, 'sw.js'), encoding='utf-8').read()
CHK(f"const CACHE = 'crazypp-v{VER}';" in SW,
    f'sw.js: sello const CACHE = crazypp-v{VER} (4.º sello, el bump gobierna la caché)')
CHK("url.pathname.endsWith('/game.html')" in SW, 'sw.js: game.html con estrategia propia')
CHK('caches.delete(k)' in SW, 'sw.js: activate purga las cachés de versiones viejas')
CHK('self.skipWaiting()' in SW and 'clients.claim()' in SW, 'sw.js: skipWaiting + claim (actualización inmediata)')
CHK('url.origin !== self.location.origin' in SW, 'sw.js: sólo GET same-origin (telemetría/PeerJS pasan)')
CHK('networkFirst' in SW and 'cacheFirst' in SW, 'sw.js: network-first (datos vivos) + cache-first (assets)')

# 6 · iconos con PIL (tamaños + contenido + maskable al 80 %)
for nombre, esperado in (('logo-192.png', 192), ('logo-512.png', 512), ('logo-maskable-512.png', 512)):
    p = os.path.join(PUB, nombre)
    try:
        im = Image.open(p); im.load()
        CHK(im.size == (esperado, esperado), f'{nombre}: {esperado}×{esperado} OK ({os.path.getsize(p):,} B)')
        px = im.convert('RGB').load()
        # contenido no vacío: píxeles claros (bola/anillo) y color de la goma roja
        hay_blanco = hay_rojo = False
        for x in range(0, im.width, 4):
            for y in range(0, im.height, 4):
                rr, gg, bb = px[x, y]
                if rr > 220 and gg > 220 and bb > 220: hay_blanco = True
                if rr > 140 and gg < 90 and bb < 90: hay_rojo = True
        CHK(hay_blanco and hay_rojo, f'{nombre}: emblema dibujado (bola + goma roja visibles)')
        if 'maskable' in nombre:
            # los bordes (zona recortable) deben ser FONDO azul noche
            m = int(im.width * 0.08)
            bordes = [px[m, im.height // 2], px[im.width - m, im.height // 2],
                      px[im.width // 2, m], px[im.width // 2, im.height - m]]
            chk2 = all(rr < 40 and gg < 55 and bb < 110 for rr, gg, bb in bordes)
            CHK(chk2, 'logo-maskable-512.png: contenido dentro del 80 % central (bordes = fondo)')
    except Exception as e:
        CHK(False, f'{nombre}: ilegible ({e})')

# 7 · infraestructura
dp = open(os.path.join(RAIZ, 'scripts/deploy_pages.py'), encoding='utf-8').read()
for f in ('public/manifest.webmanifest', 'public/sw.js',
          'public/logo-192.png', 'public/logo-512.png', 'public/logo-maskable-512.png'):
    CHK(f"'{f}'" in dp, f'deploy_pages: SITE_PATHS publica {f.split("/", 1)[1]}')
bv = open(os.path.join(RAIZ, 'scripts/bump_version.py'), encoding='utf-8').read()
CHK('SWJS = RAIZ' in bv and "const CACHE = 'crazypp-v{nueva}'" in bv,
    'bump_version: 4.º sello (sw.js CACHE) parcheado en cada bump')
qv = open(os.path.join(RAIZ, 'scripts/qa_version.py'), encoding='utf-8').read()
CHK('const CACHE = \'crazypp-v{ver}\'' in qv or "const CACHE = 'crazypp-v{ver}'" in qv,
    'qa_version: cadena nueva verificada (SW + manifest + iconos)')
hub = open(os.path.join(RAIZ, 'src/app/descargas/page.tsx'), encoding='utf-8').read()
CHK('📲 Instalar en el casco (PWA' in hub, 'hub /descargas: guía PWA presente')
bz = open(os.path.join(RAIZ, 'scripts/release-v3699/build_zip.py'), encoding='utf-8').read()
CHK('Copiando PWA (manifest + sw + iconos)' in bz, 'build_zip: la PWA viaja en los 4 ZIPs')

# 8 · versión sellada
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.111-SDK6', 'c00: VERSION sella 3.6.111-SDK6')
CHK('>V3.6.111-SDK6</span>' in open(os.path.join(RAIZ, 'src/game/03_body.html'), encoding='utf-8').read(),
    'portada: badge V3.6.111-SDK6')
# r115 · re-ancla: la FASE vive en el bump (VERSION.json es la fuente de verdad)
CHK(V.get('fase') >= 106, f"VERSION.json: FASE {V.get('fase')} (>= 106, r114 ancla por estancia)")
CHK(V.get('hub') == 'v36111-sdk6', 'VERSION.json: hub v36111-sdk6')

# 9 · regresión (r106/r105/r104/r102/r62 intactas)
CHK('const s6 = Math.min(1, e.speed / 6);' in GH, 'r106: háptica del bote calibrada intacta')
CHK('this.haptic(this.paddleHand, 0.14 + 0.16 * s6, 28);' in GH, 'r106: canto distinguible intacto')
CHK('this.menuTex.generateMipmaps = false;' in GH, 'r105: mips OFF intacto')
CHK('if ((nowH - (this._menuHoverDrawAt || 0)) >= 90) {' in GH, 'r105: throttle de hover intacto')
CHK('new THREE.PlaneGeometry(0.90, 1.35),' in GH, 'r104: panel 0,90×1,35 intacto')
CHK('const MENU_FS = 1.16;' in GH, 'r104: fuentes ×1,16 intactas')
CHK('PROTO: 3,' in GH, 'r102/r110: pala rival FIEL intacta (PROTO 3, bit4 mano izquierda)')
CHK("const nombres = ['mesa', 'pala', 'canto', 'red', 'suelo'];" in GH, 'r62: 5 muestras físicas intactas')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (portada viva: SW registrado + instaladora) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

SHOTS = os.path.join(RAIZ, 'scripts', 'qa_shots_r109')
os.makedirs(SHOTS, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    # r111 · el arnés declara SU idioma (la detección M4 de c00 respeta
    # navigator.language; el Chromium de QA nace en-US → sin esto, la
    # portada saldría en inglés y las agujas ES fallarían)
    pg = b.new_page(viewport={'width': 1280, 'height': 720}, locale='es-ES')
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)

    # 1 · el service worker se registra y queda ACTIVO (scope raíz)
    reg = pg.evaluate("navigator.serviceWorker.getRegistration('/').then(r => r ? { hay: true, activo: !!r.active, script: (r.active && r.active.scriptURL || '').split('/').pop() } : { hay: false })")
    pg.wait_for_timeout(1500)
    reg = pg.evaluate("navigator.serviceWorker.getRegistration('/').then(r => r ? { hay: true, activo: !!r.active, script: (r.active && r.active.scriptURL || '').split('/').pop() } : { hay: false })")
    CHK(bool(reg.get('hay')), 'RUNTIME: registro del SW presente (scope /)')
    CHK(reg.get('activo') is True and reg.get('script') == 'sw.js',
        'RUNTIME: sw.js ACTIVO y controlando (skipWaiting+claim)')

    # 2 · manifest e iconos se sirven HTTP 200
    sv = pg.evaluate("""Promise.all([
      fetch('manifest.webmanifest').then(r => r.status),
      fetch('sw.js').then(r => r.status),
      fetch('logo-192.png').then(r => r.status),
      fetch('logo-512.png').then(r => r.status),
      fetch('logo-maskable-512.png').then(r => r.status),
    ])""")
    CHK(sv == [200, 200, 200, 200, 200], 'RUNTIME: manifest + sw + 3 iconos servidos 200 (%s)' % sv)

    # 3 · el manifiesto del documento enlaza bien
    mlink = pg.evaluate("document.querySelector('link[rel=manifest]') && document.querySelector('link[rel=manifest]').getAttribute('href')")
    CHK(mlink == 'manifest.webmanifest', 'RUNTIME: link[rel=manifest] relativo (%s)' % mlink)

    # 4 · gancho de QA + estado de la instaladora
    st = pg.evaluate("() => window.__ppPwa ? { standalone: window.__ppPwa.standalone, registered: window.__ppPwa.registered, prompt: !!window.__ppPwa.prompt } : null")
    CHK(bool(st) and st.get('registered') is True, 'RUNTIME: __ppPwa.registered = true')
    CHK(bool(st) and st.get('standalone') is False, 'RUNTIME: no-standalone en navegador (botón visible)')

    # 5 · botón visible y con texto ES
    btn = pg.evaluate("() => { const b = document.getElementById('pwabtn'); return b ? { visible: b.offsetParent !== null, txt: b.textContent.trim() } : null; }")
    CHK(bool(btn) and btn.get('visible') and 'INSTALAR' in btn.get('txt', ''),
        'RUNTIME: botón 📲 visible con texto ES (%s)' % (btn or {}).get('txt'))

    # 6 · click del botón: DOS caminos legítimos, probados SIN CARRERA
    #   a) si beforeinstallprompt se capturó (headless lo dispara aquí:
    #      manifest+SW+iconos instalables) → botón dorado (pwaOn).
    #   b) camino manual determinista: anulado el prompt, el click DEBE
    #      enseñar el toast «Instálala en 2 toques…».
    pre = pg.evaluate("() => ({ prompt: !!(window.__ppPwa && window.__ppPwa.prompt), on: (document.getElementById('pwabtn')||{}).classList ? document.getElementById('pwabtn').classList.contains('pwaOn') : false })")
    if pre.get('prompt'):
        CHK(pre.get('on') is True, 'RUNTIME: beforeinstallprompt capturado → botón en modo NATIVO (pwaOn dorado)')
    else:
        CHK(True, 'RUNTIME: sin evento nativo todavía (headless, carrera esperada) — camino manual a prueba')
    pg.evaluate("() => { if (window.__ppPwa) window.__ppPwa.prompt = null; }")   # camino manual DETERMINISTA
    pg.click('#pwabtn')
    pg.wait_for_timeout(400)
    toast = pg.evaluate("() => { const t = document.getElementById('ppToast'); return t ? { show: t.classList.contains('show'), txt: (t.textContent || '').slice(0, 40) } : null; }")
    CHK(bool(toast) and toast.get('show') is True and 'toques' in toast.get('txt', ''),
        'RUNTIME: click → toast manual «Instálala en 2 toques…» visible')

    # 7 · i18n en vivo: cambiar a EN repinta el botón (pp-lang)
    pg.evaluate("window.__setLang && window.__setLang('en')")
    pg.wait_for_timeout(500)
    btnEN = pg.evaluate("() => { const b = document.getElementById('pwabtn'); return b ? b.textContent.trim() : ''; }")
    CHK('INSTALL' in btnEN, 'RUNTIME: idioma EN → botón «📲 INSTALL ON HEADSET» (%s)' % btnEN)
    pg.evaluate("window.__setLang && window.__setLang('es')")

    # 8 · toast programático (reutilizable para M4)
    pg.evaluate("window.__ppPwaToast && window.__ppPwaToast('<b>prueba</b>', 1500)")
    pg.wait_for_timeout(200)
    t2 = pg.evaluate("() => document.getElementById('ppToast').classList.contains('show')")
    CHK(t2 is True, 'RUNTIME: __ppPwaToast reutilizable funciona')

    pg.screenshot(path=os.path.join(SHOTS, 'portada_r109.png'))
    CHK(errs == [], 'RUNTIME: cero pageerrors (%s)' % (errs or 'limpio'))
    b.close()

srv.shutdown()

print('\n== RESUMEN qa_r109_v3699 ==')
print('  OK: %d · FALLOS: %d' % (len(OK), len(FAIL)))
if FAIL:
    print('\n'.join('  ✗ ' + f for f in FAIL))
    raise SystemExit(1)
print('  VERDE: M3 PWA INSTALABLE — manifest+SW+iconos+portada instaladora, caché gobernada por el bump')
