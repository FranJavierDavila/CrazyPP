#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r93_v3685.py — capa de QA de la ronda 93 (V3.6.87-SDK6).
Informe del dueño tras V3.6.84: «sustituimos la melodía por "melodia.mp3"
del campeonato por la que adjunto · en el super poder de la calabaza existe
un desfase de la bola cuando la golpea el rival que está desfasada, en
cambio cuando la golpeo yo esta correcta, es una deriva de precisión entre
ambas palas · me gustaría que los diseños de las etiquetas que salen con
cada superpoder hagas unos diseños para los cuatro más realistas y
tenebrosos según el superpoder».

Raíces verificadas AQUÍ:
 1) BSO NUEVA: melodia.mp3 (44100/256 CBR) sustituye a midnight_volley.mp3
    (retirado del repo) — mismo motor createMusic/manifest.audio.music.
 2) DESFASE DEL RIVAL: la r92 arrastraba el punto de contacto hacia la pala
    y RECOLOCABA la bola en la tangente — salto visible de hasta 4,5 cm con
    la calabaza (Ø 0,13) y follow-through naciendo 5 cm por encima. r93:
    la bola se queda en el punto del BARRIDO (mismo trato que la bola
    normal) y la HOJA viaja a la piel — swing contact = tangente (7,5 cm)
    + flat (sin ascenso inicial en c12).
 3) ETIQUETAS: los cuatro power_*.webp son medallones circulares nuevos
    512×512 RGBA (arte fotorealista 1024×1024 distinto por poder)."""
import os, sys, functools, json, struct, subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
HAL = os.path.join(PUB, 'championships/halloween')
SDK = os.path.join(PUB, 'championships/sdk/champ_sdk.js')
C06 = os.path.join(RAIZ, 'src/game/core/c06_logros_stats_ia_rival.js')
C12 = os.path.join(RAIZ, 'src/game/core/c12_pingponggame.js')
PORT = 8813
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA ==')
man = json.load(open(os.path.join(HAL, 'manifest.json')))
CHK(man.get('version') == 3, 'manifest: version=3')
CHK(any(n.startswith('v7 (r93)') for n in man.get('notes', [])), 'manifest: nota v7 (r93) presente')
au = man.get('audio', {})
CHK(au.get('music') == 'assets/melodia.mp3', 'manifest: BSO melodia.mp3 (melodía nueva del dueño)')
CHK(au.get('musicVolume') == 0.18, 'manifest: volumen BSO 0,18')
opts = au.get('musicOpts') or {}
CHK(opts.get('gateStart') is True and opts.get('gateOn') is False and opts.get('renace') is True,
    'manifest: musicOpts del motor probado (gateStart/renace, sin gateOn)')

# 1 · MELODÍA — fichero, perfil y ausencia del viejo
p_mel = os.path.join(HAL, 'assets/melodia.mp3')
CHK(os.path.exists(p_mel) and os.path.getsize(p_mel) > 5_000_000,
    'assets: melodia.mp3 presente (%s B)' % (os.path.getsize(p_mel) if os.path.exists(p_mel) else 0))
CHK(not os.path.exists(os.path.join(HAL, 'assets/midnight_volley.mp3')),
    'assets: midnight_volley.mp3 RETIRADO del repo')
try:
    pr = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                         'stream=sample_rate,bit_rate', '-of', 'json', p_mel],
                        capture_output=True, text=True, timeout=30)
    st = json.loads(pr.stdout or '{}')['streams'][0]
    CHK(st.get('sample_rate') == '44100' and st.get('bit_rate') == '256000',
        'assets: melodia.mp3 a 44100/256 CBR (el perfil que el casco decodifica)')
except Exception as e:
    CHK(False, 'assets: perfil de melodia.mp3 legible (%s)' % e)
PLA = open(os.path.join(HAL, 'index.js'), encoding='utf-8').read()
CHK('midnight' not in PLA.lower(), 'index: cero referencias vivas a midnight (sólo historia del manifest)')

# 2 · DESFASE DEL RIVAL — c06/c12: bola en el barrido, hoja en la piel
C6 = open(C06, encoding='utf-8').read()
C12S = open(C12, encoding='utf-8').read()
CHK('let toca = null;' in C6, 'c06: punto tangente SOLO para el swing (toca)')
CHK('const sT = Math.min(1, TOCA / dC);' in C6,
    'c06: tangente calculada SIN arrastrar el punto de contacto (sT clamp 1)')
CHK('cx = this.pos.x + dcx * sC;' not in C6 and 'const sC = TOCA / dC;' not in C6,
    'c06: el ARRASTRE de la r92 FUERA (la bola ya no salta hacia la pala)')
CHK('return this.mishit(ball, toca);' in C6, 'c06: el golpe torpe también recibe la tangente')
CHK(C6.count('contact: toca ? new THREE.Vector3(toca.x, toca.y, toca.z)') == 2,
    'c06: swing limpio Y mishit nacen en la TANGENTE (2 contactos)')
CHK(C6.count('flat: !!toca') == 2, 'c06: flag flat en ambos swings (hoja ya EN contacto)')
CHK('const reach = ball.ppCalabaza ? 0.12 : 0.21;' in C6,
    'c06: alcance 0,12 con calabaza / 0,21 norma probada (r92 intacto)')
CHK('const rise0 = sw.flat ? 0 : 0.05;' in C12S,
    'c12: SIN ascenso inicial de 5 cm cuando flat (la hoja nace en la piel)')

# 3 · ETIQUETAS — medallones circulares nuevos, distintos por poder
try:
    from PIL import Image
    import numpy as np
    ICONS = ['power_mano.webp', 'power_moscas.webp', 'power_calabaza.webp', 'power_gelatina.webp']
    RAW = os.path.join(RAIZ, 'scripts', 'staging-r93')
    arts = []
    for f in ICONS:
        p = os.path.join(HAL, 'assets', f)
        im = Image.open(p).convert('RGBA')
        kb = os.path.getsize(p) // 1024
        CHK(im.size == (512, 512) and kb >= 50,
            'etiquetas: %s 512×512 RGBA rica (%d KB — los viejos eran 13-25 KB)' % (f, kb))
        a = np.asarray(im)
        CHK(int(a[8, 8][3]) == 0 and int(a[256, 256][3]) == 255,
            'etiquetas: %s RECORTE CIRCULAR (esquina alfa 0, centro opaco)' % f)
        arts.append(a[:, :, :3].astype(int))
    for i in range(3):
        d = int(np.abs(arts[i] - arts[i + 1]).mean())
        CHK(d > 8, 'etiquetas: %s ≠ %s (diferencia media %d — arte DISTINTO por poder)' % (ICONS[i], ICONS[i + 1], d))
    if os.path.isdir(RAW):
        for f in ['mano_raw.png', 'moscas_raw.png', 'calabaza_raw.png', 'gelatina_raw.png']:
            im = Image.open(os.path.join(RAW, f))
            CHK(im.size == (1024, 1024), 'etiquetas: arte fotorealista %s 1024×1024 en staging' % f)
    else:
        # r94 · re-anclaje honesto: el staging del arte RAW nunca se versionó y no
        # sobrevive al snapshot; los medallones DESPLEGADOS ya están verificados
        # por píxeles arriba (tamaño, recorte circular y arte distinto por poder).
        print('  (aviso: staging-r93 no versionado — saltado el chequeo del arte RAW;'
              ' los medallones desplegados están verificados por píxeles)')
except ImportError:
    print('  (aviso: PIL/numpy no disponible — saltado el chequeo de píxeles)')

# sellos del bundle recién construido
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8', errors='ignore').read()
CHK(GH.count("const VERSION = '3.6.87-SDK6'") == 1, 'bundle: sello const VERSION 3.6.87-SDK6')
CHK('>V3.6.87-SDK6<' in GH, 'bundle: badge V3.6.87-SDK6 en el servido')
CHK('const rise0 = sw.flat ? 0 : 0.05;' in GH, 'bundle: aguja c12 rise0/flat en el servido')
CHK('contact: toca ? new THREE.Vector3(toca.x, toca.y, toca.z)' in GH,
    'bundle: aguja c06 tangente-para-el-swing en el servido')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    # portada: el botón JUGAR es la IMAGEN playEs (vrbtn 460,581 + 360×90);
    # el intro del campeonato es un POSTER 3D — su botón no es DOM. El efecto
    # EXACTO del botón JUGAR del intro es hideChampIntro(true) (c12:4241).
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(6000)
    pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN && window.__PP_HALLOWEEN.ctrl().game;
      if (g && g.champIntro) g.hideChampIntro(true);
    }""")
    pg.wait_for_timeout(3000)

    # ---- recursos nuevos servidos (melodía + 4 medallones)
    rec = pg.evaluate("""async () => {
      const R = (u) => fetch(u).then(r => r.status);
      const out = {};
      out.melodia = await R('championships/halloween/assets/melodia.mp3');
      out.mano = await R('championships/halloween/assets/power_mano.webp');
      out.moscas = await R('championships/halloween/assets/power_moscas.webp');
      out.cala = await R('championships/halloween/assets/power_calabaza.webp');
      out.gela = await R('championships/halloween/assets/power_gelatina.webp');
      out.viejo = await R('championships/halloween/assets/midnight_volley.mp3');
      return out;
    }""")
    CHK(all(rec.get(k) == 200 for k in ['melodia', 'mano', 'moscas', 'cala', 'gela']),
        'servido: melodia.mp3 y los 4 medallones responden 200 (%s)' % rec)
    CHK(rec.get('viejo') == 404, 'servido: midnight_volley.mp3 404 (retirado)')

    # ---- BSO: melodia.mp3 decodifica y suena (efecto del botón JUGAR)
    # r94 · sondeo PACIENTE: el decode de melodia.mp3 (4,3 MB) y el arranque
    # del ctx de audio compiten con SwiftShader en headless — se espera a que
    # el estado llegue a sonando (hasta 10 s) en vez de fotografiar un instante.
    mus = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; if (!H) return null;
      const est = () => (H.mus() ? H.mus().estado() : null);
      let m = est();
      for (let i = 0; i < 50; i++) {
        m = est();
        if (m && m.cargado && m.querido && m.sonando) break;
        await new Promise(r => setTimeout(r, 200));
      }
      return m;
    }""")
    CHK((mus or {}).get('cargado') is True, 'BSO: buffer de melodia.mp3 CARGADO en el navegador')
    CHK((mus or {}).get('querido') is True, 'BSO: QUERIDA tras JUGAR (hideChampIntro(true) → on())')
    CHK((mus or {}).get('sonando') is True, 'BSO: SONANDO (melodia.mp3 178,4 s por el mismo motor createMusic)')

    # ---- GOLPE DEL RIVAL con la IA REAL (la semántica r93)
    golpe = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const ai = g.ai; if (!ai) return { err: 'sin ai' };
      const D = window.__PP_CORE.DIMS;
      const C = D.tableCenterZ;
      const out = {};
      const prepara = (marca, offX, zAI) => {
        ai.hitCooldown = 0; ai.swing = null; ai.predictValid = false;
        ai.pos.set(offX, 1.0, zAI); ai.vel.set(0, 0, 0);
        g.ball.pos.set(0.10, 1.0, C - 0.60);
        g.ball.vel.set(0, 0, -6);                    // hacia la IA (sign −1)
        g.ball.spin.set(0, 0, 0);
        g.ball.ppCalabaza = marca;
        const prev = g.ball.pos.clone(); prev.z += 0.06;   // un paso atrás
        const posAI = ai.pos.clone();
        const ctx = { canHit: true, validBounce: true, prevBall: prev,
                      oppPadX: 0, oppPadZ: C + 1.2, rallyHits: 3 };
        const v = ai.update(0.008, g.ball, ctx);
        return { golpeo: !!v,
                 dist: +(g.ball.pos.distanceTo(posAI)).toFixed(4),
                 distContact: ai.swing ? +(ai.swing.contact.distanceTo(posAI)).toFixed(4) : null,
                 flat: ai.swing ? ai.swing.flat === true : null,
                 bolaEnContacto: ai.swing ? +(g.ball.pos.distanceTo(ai.swing.contact)).toFixed(4) : null };
      };
      // A) CON marca: 3 repeticiones — la bola se queda en el BARRIDO (no
      //    salta a la tangente) y la HOJA nace en la piel (0,075, flat)
      out.veces = [];
      for (let i = 0; i < 3; i++) out.veces.push(prepara(true, 0.20, C - 0.60));
      // B) CON marca y pala lejos: alcance 0,12 NO llega (fallo natural)
      out.lejos = prepara(true, 0.28, C - 0.60);
      // C) SIN marca: alcance probado 0,21, contacto en el barrido, sin flat
      out.sin = prepara(false, 0.28, C - 0.60);
      return out;
    }""")
    if 'err' in (golpe or {}):
        CHK(False, 'golpe IA: ai viva (%s)' % golpe['err'])
    else:
        veces = golpe.get('veces') or []
        CHK(all(v.get('golpeo') for v in veces),
            'calabaza: la IA GOLPEA con la marca (3/3 — alcance 0,12)')
        CHK(all(v.get('flat') is True for v in veces),
            'calabaza: swing FLAT con la marca (hoja ya EN contacto, sin ascenso)')
        CHK(all(v.get('distContact') is not None and 0.069 <= v['distContact'] <= 0.081 for v in veces),
            'calabaza: la HOJA nace en la PIEL de la calabaza (dist contact=%s ≈ 0,075)' %
            [v.get('distContact') for v in veces])
        CHK(all(v.get('bolaEnContacto') is not None and v['bolaEnContacto'] > 0.004 for v in veces),
            'calabaza: la bola NO se recoloca en la tangente (dist bola↔contacto=%s — el salto de la r92 era 0,000)' %
            [v.get('bolaEnContacto') for v in veces])
        CHK(all(v.get('dist') is not None and v['dist'] > 0.08 for v in veces),
            'calabaza: la bola se queda en el PUNTO DEL BARRIDO (dist pala=%s — deriva de precisión cazada)' %
            [v.get('dist') for v in veces])
        lejos = golpe.get('lejos') or {}
        CHK(lejos.get('golpeo') is False, 'calabaza: a 18 cm el alcance 0,12 NO golpea (fallo natural)')
        sin = golpe.get('sin') or {}
        CHK(sin.get('golpeo') is True, 'bola normal: la IA golpea con el alcance probado 0,21')
        CHK(sin.get('flat') is False, 'bola normal: sin flat (swing normal intacto)')
        CHK(sin.get('dist') is not None and sin['dist'] > 0.12,
            'bola normal: contacto en el barrido sin arrastre (dist=%s — norma genérica intacta)' % sin.get('dist'))

    # ---- ETIQUETA en vivo: el medallón nuevo en el cartel de superpoder
    etiq = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
      const sg = ctrl.poderes && ctrl.poderes.sign; if (!sg) return { err: 'sin sign' };
      sg.show('championships/halloween/assets/power_calabaza.webp');
      for (let i = 0; i < 40; i++) {
        await new Promise(r => setTimeout(r, 100));
        let icono = null;
        sg.group && sg.group.traverse((n) => {
          if (n.isMesh && n.material && n.material.map && n.material.map.image &&
              n.material.map.image.src && n.material.map.image.src.indexOf('power_') >= 0) icono = n;
        });
        if (icono) {
          const img = icono.material.map.image;
          return { src: img.src.slice(-22), w: img.naturalWidth || img.width,
                   h: img.naturalHeight || img.height, visible: icono.visible };
        }
      }
      return { err: 'icono no llegó' };
    }""")
    if 'err' in (etiq or {}):
        CHK(False, 'etiqueta en vivo: %s' % etiq['err'])
    else:
        CHK(etiq.get('src', '').endswith('power_calabaza.webp'), 'etiqueta en vivo: textura power_calabaza.webp en el cartel')
        CHK(etiq.get('w') == 512 and etiq.get('h') == 512, 'etiqueta en vivo: medallón 512×512 decodificado')
        CHK(etiq.get('visible') is True, 'etiqueta en vivo: el icono VISIBLE bajo el cartel')

    # captura con el medallón nuevo en pantalla (evidencia para el dueño)
    pg.evaluate("""() => { const sg = window.__PP_HALLOWEEN.ctrl().poderes.sign;
                           if (sg) sg.show('championships/halloween/assets/power_calabaza.webp'); }""")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r93_etiqueta_rt.png'))

    CHK(len(errs) == 0, 'cero pageerrors en toda la sesión (%s)' % (errs[:2] if errs else 'limpio'))
    b.close()
srv.shutdown()

print('')
print('== MARCADOR r93: %d OK · %d FALLO ==' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('  ✗', f)
    sys.exit(1)
print('VERDE')
