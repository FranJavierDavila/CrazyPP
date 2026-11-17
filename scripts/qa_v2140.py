#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA V2.140 · EL VAGÓN A PUNTO (etapa 4 del Salvaje Oeste).

  A1  game.html SERVIDO = disco (sha256) y VERSION '2.140.0'
  A2  assets nuevos SERVIDOS = disco: index.js · manifest.json ·
      room/vagon/suelo.jpg · recompensa.png · forajido_robo.png ·
      risas_forajido.mp3
  A3  manifest v47 servido
  A4  módulo: zonaZ -1.6 · _pileSlot en el suelo (sin tableTopY) · yaw 0 ·
      floor con room/vagon/suelo.jpg · claves tren_mega_* es/en · announce
      en _depart/run/_arrived/_fail · métodos premio/risas · URLs nuevas
  A5  14 átomos mega_* en VOICE_B64/B64_EN: base64 = OGG de disco byte a
      byte + ffprobe opus mono
  A6  VOICE_FULL: réplica de _normVoice sobre los textos i18n del módulo
      interpolados con los 3 nombres de estación → 14 claves EXACTAS
  B   RUNTIME (Playwright, headless):
      B1 carga 0 pageerrors + banco de voz listo
      B2 entrada por ruta natural a la etapa 4 (fase del tren)
      B3 FIX BOTE: bola que bota en campo ENEMIGO (z=-1,9) NO es
         secuestrada (vel.z sigue hacia el fondo, sin ápice) y en campo
         JUGADOR (z=-1,2) SÍ se normaliza (vel.z +0,95, vy apex)
      B4 PILA: _pileSlot(0..23) — simetría de lados, y = plano × altura
         exacta, capas PERFECTAMENTE alineadas (x/z idénticos entre capas)
      B5 SUELO: el floor del vagón viste room/vagon/suelo.jpg cargada (1296px)
      B6 MEGAFONÍA: spy de announce — salida «Pasajeros al tren, partimos
         hacia Dry Gulch», llegada a los 30 s «En menos de 25 segundos
         llegaremos a Dry Gulch», arribo OK «Cargamento de oro a buen
         recaudo» + panel recompensa.png; voicePlan de las 14 frases
      B7 PANELES: _showPremio('robo') → mesh 0,78×1,56 con textura
         forajido_robo.png + pop elástico en fxStep; panel OK → 1,15
      B8 RISAS: risas_forajido.mp3 SERVIDO decodifica (WebAudio)
      B9 FOTO 3D: pila de 12 lingotes en el suelo + panel recompensa
  C   smoke 4 campeonatos: 0 pageerrors
"""
import base64
import hashlib
import re
import subprocess
import time
import unicodedata
import urllib.request

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:3000'
GAME = '/home/z/my-project/public/game.html'
MOD = '/home/z/my-project/public/championships/oeste/index.js'
OGG_DIR = '/home/z/my-project/scripts/voice/ogg'
OGG_EN_DIR = '/home/z/my-project/scripts/voice/ogg_en'
KEYS = ['mega_salida_dg', 'mega_salida_pd', 'mega_salida_br',
        'mega_llega_dg', 'mega_llega_pd', 'mega_llega_br', 'mega_oro']
RES = []


def chk(name, ok, extra=''):
    RES.append((name, ok, extra))
    print(f"{'✓' if ok else '✗'} {name} {extra}")


def js(page, expr):
    try:
        return page.evaluate(expr)
    except Exception as e:
        return {'__err': str(e)[:200]}


TICK = """(() => { const G = window.__PP_GAME;
  if (!window.__t) window.__t = performance.now();
  for (let i = 0; i < (window.__n || 4); i++) {
    window.__t += 50; G.lastTime = window.__t / 1000 - 0.05; G.freezeT = 0;
    G.animate(window.__t);
  } return 1; })()"""

POSE_JS = """(() => {
  const r = window.__PP_GAME.renderer;
  const real = r.render.bind(r);
  r.render = (scene, cam) => {
    const p = window.__camPose;
    if (p) { cam.position.set(p[0], p[1], p[2]); cam.lookAt(p[3], p[4], p[5]); }
    return real(scene, cam);
  };
  window.__camPose = null; return 1; })()"""


def pose(page, px, py, pz, tx, ty, tz):
    page.evaluate(f"window.__camPose = [{px},{py},{pz},{tx},{ty},{tz}]")
    page.evaluate(TICK)
    page.evaluate("window.__camPose = null")


serv = urllib.request.urlopen(BASE + '/game.html').read()
disco = open(GAME, 'rb').read()
html = serv.decode('utf-8')

# ===== A1 · SERVIDO = DISCO + VERSION =====
chk('A1 servido = disco', hashlib.sha256(serv).hexdigest() == hashlib.sha256(disco).hexdigest(),
    f'({len(serv)} B)')
chk("A1 VERSION '2.140.0'", b"const VERSION = '2.140.0'" in serv)

# ===== A2 · ASSETS NUEVOS SERVIDOS = DISCO =====
for ruta, disco_path in (
    ('/championships/oeste/index.js', MOD),
    ('/championships/oeste/manifest.json',
     '/home/z/my-project/public/championships/oeste/manifest.json'),
    ('/championships/oeste/assets/room/vagon/suelo.jpg',
     '/home/z/my-project/public/championships/oeste/assets/room/vagon/suelo.jpg'),
    ('/championships/oeste/assets/recompensa.png',
     '/home/z/my-project/public/championships/oeste/assets/recompensa.png'),
    ('/championships/oeste/assets/forajido_robo.png',
     '/home/z/my-project/public/championships/oeste/assets/forajido_robo.png'),
    ('/championships/oeste/assets/risas_forajido.mp3',
     '/home/z/my-project/public/championships/oeste/assets/risas_forajido.mp3'),
):
    s = urllib.request.urlopen(BASE + ruta).read()
    d = open(disco_path, 'rb').read()
    chk(f'A2 servido = disco {ruta.rsplit("/", 1)[-1]}',
        hashlib.sha256(s).hexdigest() == hashlib.sha256(d).hexdigest(), f'({len(s)} B)')

# ===== A3 · MANIFEST v47 =====
import json
man = json.loads(urllib.request.urlopen(
    BASE + '/championships/oeste/manifest.json').read().decode('utf-8'))
chk('A3 manifest version 47', man.get('version') == 47, str(man.get('version')))

# ===== A4 · MÓDULO: MARCADORES V2.140 =====
jsmod = open(MOD, encoding='utf-8').read()
chk('A4 zonaZ = -1.6 (sólo campo del jugador)', 'zonaZ: -1.6,' in jsmod and 'zonaZ: -2.2' not in jsmod)
chk('A4 _pileSlot en el suelo (sin tableTopY en la pila)',
    'layer * hL' in jsmod and 'side * (1.10 + gx * 0.19)' in jsmod and
    'tableTopY + 0.095' not in jsmod)
chk('A4 yaw 0 al aterrizar', 'dest, yaw: 0,' in jsmod and '(Math.random() - 0.5) * 1.4' not in jsmod)
chk('A4 floor del vagón = room/vagon/suelo.jpg',
    "boxMat(plainTex(A('room/vagon/suelo.jpg')))" in jsmod)
chk('A4 claves tren_mega_* es', "tren_mega_salida: 'Pasajeros al tren, partimos hacia {e}'" in jsmod
    and "tren_mega_llega: 'En menos de 25 segundos llegaremos a {e}'" in jsmod
    and "tren_mega_oro: 'Cargamento de oro a buen recaudo'" in jsmod)
chk('A4 claves tren_mega_* en', "tren_mega_salida: 'All aboard! We are departing towards {e}'" in jsmod
    and "tren_mega_llega: 'In less than 25 seconds we will arrive at {e}'" in jsmod
    and "tren_mega_oro: 'The gold shipment is safe and sound'" in jsmod)
chk('A4 announce en _depart/_arrived/_fail + trigger 30 s',
    jsmod.count("tx('tren_mega_salida'") == 1 and jsmod.count("tx('tren_mega_oro'") == 1
    and jsmod.count("tx('tren_mega_llega'") == 1 and 'this._megaLlegada' in jsmod)
chk('A4 métodos premio + risas + URLs',
    '_showPremio(kind)' in jsmod and '_hidePremio()' in jsmod
    and 'loadRisasForajido()' in jsmod and '_playRisasForajido(vol)' in jsmod
    and "recompensaUrl: A('recompensa.png')" in jsmod
    and "roboUrl: A('forajido_robo.png')" in jsmod
    and "risasForajidoUrl: A('risas_forajido.mp3')" in jsmod)

# ===== A5 · ÁTOMOS = OGG DE DISCO + SANOS =====
def bank_slice(h, start_marker):
    i = h.index(start_marker)
    j = h.index('};', i)
    return h[i:j]

es_bank = bank_slice(html, 'const VOICE_B64 = {')
en_bank = bank_slice(html, 'const VOICE_B64_EN = {')
for lang, bank, ogg_dir in (('es', es_bank, OGG_DIR), ('en', en_bank, OGG_EN_DIR)):
    for k in KEYS:
        m = re.search(rf'\b{k}: "([A-Za-z0-9+/=]+)"', bank)
        if not m:
            chk(f'A5 átomo {k}:{lang} en banco', False, 'no encontrado')
            continue
        d = base64.b64decode(m.group(1))
        ok = hashlib.sha256(d).hexdigest() == hashlib.sha256(
            open(f'{ogg_dir}/{k}.ogg', 'rb').read()).hexdigest()
        chk(f'A5 átomo {k}:{lang} = ogg disco', ok, f'({len(d)} B)')

for k in KEYS:
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'stream=codec_name,channels:format=duration',
                        '-of', 'default=nw=1', f'{OGG_DIR}/{k}.ogg'],
                       capture_output=True, text=True)
    ok = 'opus' in r.stdout and 'channels=1' in r.stdout
    chk(f'A5 ogg {k} opus mono', ok, r.stdout.replace('\n', ' ')[:60])

# ===== A6 · VOICE_FULL: normalización de los textos del módulo =====
def norm(s):
    s = s.lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

EST = ['DRY GULCH', 'PERDIDO', 'BRAVOS']
frases = []
for e in EST:
    frases.append((norm(f"Pasajeros al tren, partimos hacia {e}"),
                   f"'pasajeros al tren partimos hacia {e.lower()}'",
                   ['mega_salida_' + {'DRY GULCH': 'dg', 'PERDIDO': 'pd', 'BRAVOS': 'br'}[e]],
                   'es'))
    frases.append((norm(f"En menos de 25 segundos llegaremos a {e}"),
                   f"'en menos de 25 segundos llegaremos a {e.lower()}'",
                   ['mega_llega_' + {'DRY GULCH': 'dg', 'PERDIDO': 'pd', 'BRAVOS': 'br'}[e]],
                   'es'))
    frases.append((norm(f"All aboard! We are departing towards {e}"),
                   f"'all aboard we are departing towards {e.lower()}'",
                   ['mega_salida_' + {'DRY GULCH': 'dg', 'PERDIDO': 'pd', 'BRAVOS': 'br'}[e]],
                   'en'))
    frases.append((norm(f"In less than 25 seconds we will arrive at {e}"),
                   f"'in less than 25 seconds we will arrive at {e.lower()}'",
                   ['mega_llega_' + {'DRY GULCH': 'dg', 'PERDIDO': 'pd', 'BRAVOS': 'br'}[e]],
                   'en'))
for texto, clave, plan, lang in frases:
    chk(f'A6 normalización → {plan[0]} ({lang})',
        clave in html, texto[:52])
chk("A6 'cargamento de oro a buen recaudo' → ['mega_oro'] (es)",
    "'cargamento de oro a buen recaudo': ['mega_oro']," in html)
chk("A6 'the gold shipment is safe and sound' → ['mega_oro'] (en)",
    "'the gold shipment is safe and sound': ['mega_oro']," in html)

# ===== B · RUNTIME =====
with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox",
        "--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:150]))
    page.goto(BASE + '/game.html?champ=oeste', wait_until='domcontentloaded', timeout=60000)
    for _ in range(30):
        s = js(page, "!!(window.__PP_GAME && window.__PP_GAME.rules)")
        if s is True:
            break
        time.sleep(1)
    time.sleep(2)
    chk('B1 juego cargado 0 pageerrors', len(errs) == 0, str(errs[:2]))

    # esperar al MÓDULO del oeste (el init llega con el lanzamiento — v2.137)
    for _ in range(30):
        s = js(page, "!!(window.__PP_GAME && window.__PP_GAME.champs && "
                     "window.__PP_GAME.champs.mod && window.__PP_GAME.champs.mod.controller)")
        if s is True:
            break
        time.sleep(1)
    chk('B1 módulo oeste vivo (champs.mod.controller)', s is True)

    # B2 · ENTRAR A LA ETAPA 4 (ruta natural del QA v2.138)
    page.evaluate("""(() => { const o = document.getElementById('overlay');
      if (o) o.style.display = 'none'; return 1; })()""")
    page.evaluate(POSE_JS)
    page.evaluate("""(() => { const G = window.__PP_GAME, c = G.champs.mod.controller;
      c.stage = 4; c._armT = 0; c._duelOn = false; c.serveTrigger(0);
      return 1; })()""")
    page.evaluate(TICK)
    page.evaluate("""(() => { const G = window.__PP_GAME;
      if (G._instr) G.hideInstrucciones(false);
      if (G.champIntro && G.champIntro.group) G.champIntro.group.visible = false;
      return 1; })()""")
    fase = None
    for _ in range(20):
        t = js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller;
          return (c._tren && c._stageMode === 'tren') ? c._tren.phase : null; })()""")
        if t:
            fase = t
            break
        page.evaluate(TICK)
        time.sleep(0.3)
    chk('B2 etapa 4 activa (fase del tren)', bool(fase), str(fase))

    # B3 · FIX BOTE FANTASMA
    page.evaluate("""(() => { const G = window.__PP_GAME, c = G.champs.mod.controller, t = c._tren;
      if (t.phase !== 'run') t._depart();
      t._pod = null; if (t.pods) t.pods.forEach(p => p.mesh.visible = false);
      t._podT = 1e9;  // sin superpoderes durante el test
      return { fase: t.phase }; })()""")
    r = js(page, """(() => {
      const G = window.__PP_GAME, t = G.champs.mod.controller._tren, b = G.ball;
      const out = {};
      // CASO 1: bote en el CAMPO ENEMIGO cerca de la red (z = -1,9):
      // la bola CAE y CRUZA el plano de la mesa (top+r = 0,78) en este step
      b.pos.set(0.1, 0.86, -1.9); b.vel.set(0, -8.0, -0.5); b.spin.set(0, 0, 0);
      t._gastada = false;
      t._simBall(0.016);
      out.enemigo = { vz: +b.vel.z.toFixed(3), vy: +b.vel.y.toFixed(3), z: +b.pos.z.toFixed(3) };
      // CASO 2: bote en el CAMPO DEL JUGADOR (z = -1,2)
      b.pos.set(0.1, 0.86, -1.2); b.vel.set(0, -8.0, -0.5); b.spin.set(0, 0, 0);
      t._simBall(0.016);
      out.jugador = { vz: +b.vel.z.toFixed(3), vy: +b.vel.y.toFixed(3), z: +b.pos.z.toFixed(3) };
      return out; })()""")
    ok = (isinstance(r, dict) and 'enemigo' in r
          and r['enemigo']['vz'] < -0.3       # sigue hacia el fondo: NO devuelta
          and isinstance(r.get('jugador'), dict)
          and r['jugador']['vz'] > 0.5        # normalizada hacia la zona cómoda
          and r['jugador']['vy'] > 2.5)       # recalibrada al ápice (~3,72)
    chk('B3 bote fantasma FIX (enemigo NO secuestrada · jugador SÍ)', ok, str(r))

    # B4 · PILA: simetría + capas exactas
    r = js(page, """(() => {
      const t = window.__PP_GAME.champs.mod.controller._tren;
      const hL = t._lingoteH || 0.0515;
      const slots = [];
      for (let n = 0; n < 24; n++) { const v = t._pileSlot(n);
        slots.push([+v.x.toFixed(4), +v.y.toFixed(4), +v.z.toFixed(4)]); }
      const cap0 = slots.slice(0, 12), cap1 = slots.slice(12, 24);
      const simetrica = cap0.every((s, i) => i % 2 === 0 ? s[0] < 0 : s[0] > 0);
      const yOk = cap0.every((s, i) => Math.abs(s[1] - 0) < 1e-6)
        && cap1.every((s, i) => Math.abs(s[1] - hL) < 1e-6);
      const alineadas = cap1.every((s, i) =>
        Math.abs(Math.abs(s[0]) - Math.abs(cap0[i][0])) < 1e-6
        && Math.abs(s[2] - cap0[i][2]) < 1e-6);
      const xzIzq = [...new Set(cap0.filter((s, i) => i % 2 === 0)
        .map(s => s[0] + ',' + s[2]))];
      const xzDer = [...new Set(cap0.filter((s, i) => i % 2 === 1)
        .map(s => s[0] + ',' + s[2]))];
      return { hL: +hL.toFixed(4), simetrica, yOk, alineadas,
               huecosIzq: xzIzq.length, huecosDer: xzDer.length,
               slots: cap0.slice(0, 4) }; })()""")
    ok = (isinstance(r, dict) and r.get('simetrica') and r.get('yOk')
          and r.get('alineadas') and r.get('huecosIzq') == 6 and r.get('huecosDer') == 6)
    chk('B4 pila: lados alternos + capas EXACTAS + 6 huecos por pila', ok, str(r))

    # B5 · SUELO del vagón
    r = js(page, """(() => {
      const t = window.__PP_GAME.champs.mod.controller._tren;
      if (!t.group) return { __err: 'sin grupo' };
      let f = null;
      t.group.traverse((o) => { if (f || !o.isMesh || !o.material || !o.material.map) return;
        const g = o.geometry && o.geometry.parameters;
        if (g && Math.abs(g.width - 6.10) < 0.01 && Math.abs(g.height - 7.90) < 0.01
            && Math.abs(o.position.y) < 0.01) f = o; });
      if (!f) return { __err: 'floor no encontrado' };
      const src = f.material.map.image && f.material.map.image.src || '';
      return { src: src.slice(-40), completa: !!f.material.map.image,
               w: f.material.map.image && f.material.map.image.width }; })()""")
    ok = (isinstance(r, dict) and 'src' in r and 'suelo.jpg' in r.get('src', '')
          and r.get('completa') and r.get('w') == 1296)
    chk('B5 suelo del vagón = suelo.jpg cargada (1296 px)', ok, str(r))

    # B6 · MEGAFONÍA: spy de announce + voicePlan de las 14 frases
    page.evaluate("""(() => { const G = window.__PP_GAME;
      G.__megaSpy = [];
      G.audio.__announceOrig = G.audio.announce;
      G.audio.announce = (txt, force) => { G.__megaSpy.push(String(txt)); return 1; };
      const t = G.champs.mod.controller._tren;
      t._megaLlegada = true;  // silencia el trigger de llegada para el test de salida
      t._depart();            // SALIDA: voz «Pasajeros al tren, partimos hacia…»
      return { fase: t.phase }; })()""")
    page.evaluate(TICK)
    r = js(page, """(() => { const G = window.__PP_GAME;
      const spy = G.__megaSpy;
      const t = G.champs.mod.controller._tren;
      // llegada a los 30 s
      t.time = 29.8; t._megaLlegada = false;
      t.step(0.5);
      // arribo OK
      t.ingots = 3; t._arrived();
      return { spy: spy, trasArrived: G.__megaSpy.length, premio: !!t.premio }; })()""")
    ok = (isinstance(r, dict) and len(r.get('spy', [])) >= 1
          and 'partimos hacia' in r['spy'][0].lower().replace('Partimos', 'partimos')
          and 'dry gulch' in r['spy'][0].lower())
    chk('B6 voz de SALIDA «…partimos hacia DRY GULCH»', ok, str(r.get('spy', [])[:1]))
    ok2 = (isinstance(r, dict) and len(r.get('spy', [])) >= 2
           and 'llegaremos a' in r['spy'][1].lower()
           and 'dry gulch' in r['spy'][1].lower())
    chk('B6 voz de LLEGADA a los 30 s «…llegaremos a DRY GULCH»', ok2, str(r.get('spy', [])[1:2]))
    ok3 = (isinstance(r, dict) and len(r.get('spy', [])) >= 3
           and 'Cargamento de oro a buen recaudo' in r['spy'][2]
           and r.get('premio') is True)
    chk('B6 voz de ARRIBO OK + panel recompensa', ok3, str(r.get('spy', [])[2:3]))

    # voicePlan de las 14 frases (función pura del banco — sin ctx)
    for lang in ('es', 'en'):
        page.evaluate(f"""(() => {{ window.__setLang('{lang}'); return 1; }})()""")
        time.sleep(0.3)
        r = js(page, """(() => { const G = window.__PP_GAME;
          const P = (t) => G.audio.voicePlan(t);
          if (window.__setLang && window.__PP_CORE.lang() === 'en') {
            return { vp: [
              P('All aboard! We are departing towards Dry Gulch'),
              P('All aboard! We are departing towards Perdido'),
              P('All aboard! We are departing towards Bravos'),
              P('In less than 25 seconds we will arrive at Dry Gulch'),
              P('In less than 25 seconds we will arrive at Perdido'),
              P('In less than 25 seconds we will arrive at Bravos'),
              P('The gold shipment is safe and sound')] }; }
          return { vp: [
            P('Pasajeros al tren, partimos hacia Dry Gulch'),
            P('Pasajeros al tren, partimos hacia Perdido'),
            P('Pasajeros al tren, partimos hacia Bravos'),
            P('En menos de 25 segundos llegaremos a Dry Gulch'),
            P('En menos de 25 segundos llegaremos a Perdido'),
            P('En menos de 25 segundos llegaremos a Bravos'),
            P('Cargamento de oro a buen recaudo')] }; })()""")
        esperados = [f"mega_salida_{s}" for s in ('dg', 'pd', 'br')] + \
                    [f"mega_llega_{s}" for s in ('dg', 'pd', 'br')] + ['mega_oro']
        vp = r.get('vp') if isinstance(r, dict) else None
        ok = isinstance(vp, list) and len(vp) == 7 and all(
            p and p[0].get('k') == e for p, e in zip(vp, esperados))
        chk(f'B6 voicePlan({lang}) 7/7 planes exactos', ok, str(vp)[:160] if vp else str(r))

    page.evaluate("""(() => { const G = window.__PP_GAME;
      if (G.audio.__announceOrig) G.audio.announce = G.audio.__announceOrig;
      window.__setLang('es'); return 1; })()""")

    # B7 · PANELES: robo + pop elástico (la textura carga ASYNC: se espera)
    r = js(page, """(() => {
      const t = window.__PP_GAME.champs.mod.controller._tren;
      t._showPremio('robo');
      const m = t.premio;
      if (!m) return { __err: 'sin premio' };
      const s0 = +m.scale.x.toFixed(2);       // escala recién nacido (síncrono)
      t.fxStep(0.25); t.fxStep(0.25);         // el pop avanza en el propio evaluate
      return { s0,
               s1: +t.premio.scale.x.toFixed(3),
               w: +m.geometry.parameters.width.toFixed(3),
               h: +m.geometry.parameters.height.toFixed(3),
               y: +m.position.y.toFixed(2) }; })()""")
    s0_first = r.get('s0') if isinstance(r, dict) else None   # 0,2 al nacer
    for _ in range(10):     # espera a la textura async (máx ~3 s)
        if isinstance(r, dict) and 'forajido_robo.png' in r.get('src', ''):
            break
        time.sleep(0.3)
        r = js(page, """(() => {
          const m = window.__PP_GAME.champs.mod.controller._tren.premio;
          return m ? { w: +m.geometry.parameters.width.toFixed(3),
            h: +m.geometry.parameters.height.toFixed(3), s1: +m.scale.x.toFixed(3),
            src: (m.material.map.image && m.material.map.image.src || '').slice(-30),
            y: +m.position.y.toFixed(2) } : { __err: 'sin premio' }; })()""")
    ok = (isinstance(r, dict) and abs(r.get('w', 0) - 0.78) < 0.01
          and abs(r.get('h', 0) - 1.56) < 0.01 and s0_first == 0.2
          and 0.2 < r.get('s1', 0) <= 1.15 and 'forajido_robo.png' in r.get('src', '')
          and abs(r.get('y', 0) - 1.72) < 0.01)
    chk('B7 panel forajido_robo 0,78×1,56 @1,72 + pop elástico', ok,
        str(r) + f' · s0(nacido)={s0_first}')

    # B9 · FOTO 3D: 18 lingotes (capa completa 12 + 6 de la 2.ª) + panel recompensa
    page.evaluate("""(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      t._hidePremio(); t._showPremio('recompensa');
      const from = { x: 0, y: 0.9, z: -4.5 };   // objeto plano: Vector3.copy lo admite
      for (let i = 0; i < 18; i++) t._lanzaLingote(from);
      return t.ingotes.length; })()""")
    page.evaluate("window.__n = 40")   # 2 s de vuelo: todos asentados
    page.evaluate(TICK)
    page.evaluate("window.__n = 4")
    pose(page, 1.55, 1.35, 0.85, -0.7, 0.25, -1.35)
    time.sleep(0.4)
    page.screenshot(path='/home/z/my-project/scripts/_v2140_pila_lingotes.png')
    print('B9 foto pila + panel OK')
    r = js(page, """(() => {
      const t = window.__PP_GAME.champs.mod.controller._tren;
      const asentados = t.ingotes.filter(i => !i.volando).length;
      const capas = new Set(t.ingotes.map(i => +i.mesh.position.y.toFixed(4)));
      const alineados = t.ingotes.every(i => {
        const v = t._pileSlot(t.ingotes.indexOf(i));
        return v.distanceTo(i.mesh.position) < 0.005; });
      return { asentados, capas: capas.size, alineados }; })()""")
    ok = (isinstance(r, dict) and r.get('asentados') == 18 and r.get('capas', 0) == 2
          and r.get('alineados') is True)
    chk('B9 18 lingotes asentados en 2 capas PERFECTAMENTE alineadas', ok, str(r))
    chk('runtime oeste 0 pageerrors', len(errs) == 0, str(errs[:2]))
    page.close()

    # B8 · RISAS SERVIDAS decodifican (WebAudio, bytes servidos)
    page2 = ctx.new_page()
    er2 = []
    page2.on("pageerror", lambda e: er2.append(str(e)[:120]))
    r = js(page2, """async () => {
      const ab = await (await fetch('http://localhost:3000/championships/oeste/assets/risas_forajido.mp3')).arrayBuffer();
      const AC = window.AudioContext || window.webkitAudioContext;
      const ac = new AC();
      try { const buf = await ac.decodeAudioData(ab.slice(0));
        return { ok: true, d: +buf.duration.toFixed(2), ch: buf.numberOfChannels }; }
      catch (e) { return { ok: false, why: String(e).slice(0, 80) }; }
      finally { try { ac.close(); } catch (e) {} } }""")
    ok = isinstance(r, dict) and r.get('ok') and 1.0 <= r.get('d', 0) <= 12.0
    chk('B8 risas_forajido.mp3 servido decodifica', ok, str(r))
    page2.close()

    # ===== C · SMOKE 4 CAMPEONATOS =====
    for champ in ('locura', 'magia', 'oeste', 'estacion_orbital'):
        pg = ctx.new_page()
        er = []
        pg.on("pageerror", lambda e: er.append(str(e)[:120]))
        pg.goto(f'{BASE}/game.html?champ={champ}', wait_until='domcontentloaded', timeout=60000)
        for _ in range(30):
            s = js(pg, "!!(window.__PP_GAME && window.__PP_GAME.rules)")
            if s is True:
                break
            time.sleep(1)
        time.sleep(3)
        chk(f'C smoke {champ}: 0 pageerrors', len(er) == 0, str(er[:2]))
        pg.close()
    browser.close()

n_ok = sum(1 for _, ok, _ in RES if ok)
print(f"\n===== QA V2.140: {n_ok}/{len(RES)} VERDE =====")
raise SystemExit(0 if n_ok == len(RES) else 1)
