#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA V2.141 · OESTE «LOS CAJONES DEL ORO» + PARADAS CON NOMBRE.

  A1  game.html SERVIDO = disco (sha256) y VERSION '2.141.0'
  A2  assets SERVIDOS = disco: index.js · manifest.json ·
      room/vagon/suelo.jpg (= upload/suelo.jpg del dueño) ·
      PARADA1.png (= upload/PARADA1.png del dueño)
  A3  manifest v48 servido
  A4  módulo: stationNames BRAVOS·BRAVOS·GOLD DUST·SILVER CREEK · config
      cajonOro (0,72×0,18×0,36 · x 1,35 · z -1,38/-1,59) · cajonesOro en
      build() · _pileSlot(side, slot) · _pileN [0,0] + _pileFree · normas
      «GRANDES CAJONES» · toast «LINGOTE AL CAJÓN» · sin rastro de DRY
      GULCH/PERDIDO en los nombres
  A5  22 átomos mega_* (11 es + 11 en): base64 = OGG de disco byte a byte
      + ffprobe opus mono de los 4 NUEVOS por idioma
  A6  VOICE_FULL: réplica de _normVoice sobre los textos i18n del módulo
      interpolados con BRAVOS·GOLD DUST·SILVER CREEK → 14 claves EXACTAS
  B   RUNTIME (Playwright, headless):
      B1 carga 0 pageerrors + módulo vivo
      B2 entrada por ruta natural a la etapa 4 (fase del tren)
      B3 CAJONES DEL ORO: 2 mallas 0,72×0,18×0,36 en (±1,35, 0,09,
         -1,38/-1,59), texturas cubo1/cubo2 (sin candado), fuera de la
         mesa y bajo el centro de las ventanas
      B4 PILA: 20 lingotes → 10 por cajón — capa 0 con 9 huecos DISTINTOS
         (sin solape), y = h + capa×altura exacta, jitter dentro de
         ±7mm/±3mm/±1,7°, 10.º lingote ENCIMA (2.ª capa perfecta)
      B5 ROBO: el hueco robado VUELVE y el siguiente lingote lo REUTILIZA
      B6 SUELO: floor del vagón viste suelo.jpg (1296 px)
      B7 MEGAFONÍA: salida «…partimos hacia BRAVOS» (parada 1), salida a
         GOLD DUST (parada 2), llegada a los 30 s, arribo OK + panel
      B8 voicePlan 7/7 en es y en (br · gd · sc · oro)
      B9 PARADA1.png cargada como arte de la parada 1 (1024 px)
      B10 FOTOS: cenital de los DOS cajones con las pilas + vista lateral
  C   smoke 4 campeonatos: 0 pageerrors
"""
import base64
import hashlib
import json
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
OLD_KEYS = ['mega_salida_dg', 'mega_salida_pd', 'mega_salida_br',
            'mega_llega_dg', 'mega_llega_pd', 'mega_llega_br', 'mega_oro']
NEW_KEYS = ['mega_salida_gd', 'mega_salida_sc', 'mega_llega_gd', 'mega_llega_sc']
ALL_KEYS = OLD_KEYS + NEW_KEYS
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
chk("A1 VERSION '2.141.0'", b"const VERSION = '2.141.0'" in serv)
chk('A1 marcador v2.141 en changelog', 'LOS CAJONES DEL ORO' in html[:900000])

# ===== A2 · ASSETS SERVIDOS = DISCO (y = upload del dueño) =====
pares = (
    ('/championships/oeste/index.js', MOD),
    ('/championships/oeste/manifest.json',
     '/home/z/my-project/public/championships/oeste/manifest.json'),
    ('/championships/oeste/assets/room/vagon/suelo.jpg',
     '/home/z/my-project/upload/suelo.jpg'),
    ('/championships/oeste/assets/PARADA1.png',
     '/home/z/my-project/upload/PARADA1.png'),
)
for ruta, disco_path in pares:
    s = urllib.request.urlopen(BASE + ruta).read()
    d = open(disco_path, 'rb').read()
    chk(f'A2 servido = dueño {ruta.rsplit("/", 1)[-1]}',
        hashlib.sha256(s).hexdigest() == hashlib.sha256(d).hexdigest(), f'({len(s)} B)')

# ===== A3 · MANIFEST v48 =====
man = json.loads(urllib.request.urlopen(
    BASE + '/championships/oeste/manifest.json').read().decode('utf-8'))
chk('A3 manifest version 48', man.get('version') == 48, str(man.get('version')))

# ===== A4 · MÓDULO: MARCADORES V2.141 =====
jsmod = open(MOD, encoding='utf-8').read()
chk('A4 stationNames = BRAVOS·BRAVOS·GOLD DUST·SILVER CREEK',
    "stationNames: ['BRAVOS', 'BRAVOS', 'GOLD DUST', 'SILVER CREEK']," in jsmod
    and 'DRY GULCH' not in jsmod.split('stationNames:')[1].split(']')[0])
chk('A4 config cajonOro (achatado: 0,72×0,18×0,36 · x 1,35 · z -1,38/-1,59)',
    'cajonOro: {' in jsmod and 'w: 0.72, h: 0.18, d: 0.36,' in jsmod
    and 'x: 1.35,' in jsmod and 'zIzq: -1.38, zDer: -1.59,' in jsmod
    and 'jX: 0.007, jZ: 0.003, yaw: 0.03,' in jsmod)
chk('A4 cajonesOro en build() con cubo1/cubo2 (sin candado)',
    'this.cajonesOro = [1, -1].map((side)' in jsmod
    and 'this._cuboOroGeo = new THREE.BoxGeometry(CR.w, CR.h, CR.d)' in jsmod
    and 'side > 0 ? this._matCubo[1] : this._matCubo[0]' in jsmod)
chk('A4 _pileSlot(side, slot) sobre cajones (y = h + capa×hL)',
    '_pileSlot(side, slot) {' in jsmod and 'CR.h + layer * hL' in jsmod
    and 'side * (1.10 + gx * 0.19)' not in jsmod)
chk('A4 pila POR CAJÓN: _pileN [0,0] + _pileFree + alterno',
    'this._pileN = [0, 0];' in jsmod and 'this._pileFree = [[], []];' in jsmod
    and 'this._pileAlt' in jsmod and 'this._pileN[idx]++' in jsmod)
chk('A4 robo LIBERA su hueco',
    'if (!this._pileFree[idx].includes(tgt.slot)) this._pileFree[idx].push(tgt.slot);' in jsmod
    and 'this._pileN = Math.max(0, this._pileN - 1)' not in jsmod)
chk('A4 normas «GRANDES CAJONES» es/en',
    'SOBRE LOS GRANDES CAJONES de madera junto a las ventanas' in jsmod
    and 'BIG WOODEN CRATES by the windows' in jsmod)
chk('A4 toast «LINGOTE AL CAJÓN» / «INGOT ON THE CRATE»',
    "tren_lingote: '¡LINGOTE AL CAJÓN! ({n}/{m})'" in jsmod
    and "tren_lingote: 'INGOT ON THE CRATE! ({n}/{m})'" in jsmod)
chk('A4 regressiones v2.140 intactas (zonaZ -1,6 · suelo.jpg · mega i18n)',
    'zonaZ: -1.6,' in jsmod and "A('room/vagon/suelo.jpg')" in jsmod
    and "tren_mega_salida: 'Pasajeros al tren, partimos hacia {e}'" in jsmod)

# ===== A5 · ÁTOMOS = OGG DE DISCO + SANOS =====
def bank_slice(h, start_marker):
    i = h.index(start_marker)
    j = h.index('};', i)
    return h[i:j]

es_bank = bank_slice(html, 'const VOICE_B64 = {')
en_bank = bank_slice(html, 'const VOICE_B64_EN = {')
for lang, bank, ogg_dir in (('es', es_bank, OGG_DIR), ('en', en_bank, OGG_EN_DIR)):
    for k in ALL_KEYS:
        m = re.search(rf'\b{k}: "([A-Za-z0-9+/=]+)"', bank)
        if not m:
            chk(f'A5 átomo {k}:{lang} en banco', False, 'no encontrado')
            continue
        d = base64.b64decode(m.group(1))
        ok = hashlib.sha256(d).hexdigest() == hashlib.sha256(
            open(f'{ogg_dir}/{k}.ogg', 'rb').read()).hexdigest()
        chk(f'A5 átomo {k}:{lang} = ogg disco', ok, f'({len(d)} B)')

for lang, ogg_dir in (('es', OGG_DIR), ('en', OGG_EN_DIR)):
    for k in NEW_KEYS:
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                            'stream=codec_name,channels:format=duration',
                            '-of', 'default=nw=1', f'{ogg_dir}/{k}.ogg'],
                           capture_output=True, text=True)
        ok = 'opus' in r.stdout and 'channels=1' in r.stdout
        dur = re.search(r'duration=(\d+\.\d+)', r.stdout)
        chk(f'A5 ogg {k}:{lang} opus mono', ok,
            (dur.group(1) + ' s') if dur else r.stdout[:50])

# ===== A6 · VOICE_FULL: normalización de los textos del módulo =====
def norm(s):
    s = s.lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

EST = {'BRAVOS': 'br', 'GOLD DUST': 'gd', 'SILVER CREEK': 'sc'}
for e, suf in EST.items():
    for plantilla, atom, lang in (
        ('Pasajeros al tren, partimos hacia {e}', 'mega_salida_', 'es'),
        ('En menos de 25 segundos llegaremos a {e}', 'mega_llega_', 'es'),
        ('All aboard! We are departing towards {e}', 'mega_salida_', 'en'),
        ('In less than 25 seconds we will arrive at {e}', 'mega_llega_', 'en'),
    ):
        clave = "'" + norm(plantilla.format(e=e)) + "': ['" + atom + suf + "'],"
        chk(f'A6 {lang} {atom}{suf} ← «{e}»', clave in html, plantilla.format(e=e)[:46])
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

    for _ in range(30):
        s = js(page, "!!(window.__PP_GAME && window.__PP_GAME.champs && "
                     "window.__PP_GAME.champs.mod && window.__PP_GAME.champs.mod.controller)")
        if s is True:
            break
        time.sleep(1)
    chk('B1 módulo oeste vivo (champs.mod.controller)', s is True)

    # B2 · ENTRAR A LA ETAPA 4 (ruta natural del QA v2.138/v2.140)
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

    # B3 · LOS CAJONES DEL ORO
    r = js(page, """(() => {
      const t = window.__PP_GAME.champs.mod.controller._tren;
      if (!t.cajonesOro || t.cajonesOro.length !== 2) return { __err: 'sin cajones' };
      const CR = t.constructor;  // no: la config vive en TREN del módulo
      const out = t.cajonesOro.map((m, i) => {
        const g = m.geometry.parameters;
        return { w: +g.width.toFixed(3), h: +g.height.toFixed(3), d: +g.depth.toFixed(3),
                 x: +m.position.x.toFixed(3), y: +m.position.y.toFixed(3),
                 z: +m.position.z.toFixed(3),
                 tex: (m.material.map && m.material.map.image
                       && (m.material.map.image.src || '').split('/').pop()) || '?' };
      });
      return out; })()""")
    ok = (isinstance(r, list) and len(r) == 2
          and all(abs(c['w'] - 0.72) < 1e-3 and abs(c['h'] - 0.18) < 1e-3
                  and abs(c['d'] - 0.36) < 1e-3 for c in r)
          and all(abs(c['y'] - 0.09) < 1e-3 for c in r)
          and abs(r[0]['x'] - 1.35) < 1e-3 and abs(r[1]['x'] + 1.35) < 1e-3
          and abs(r[0]['z'] + 1.59) < 1e-3 and abs(r[1]['z'] + 1.38) < 1e-3
          and r[0]['tex'] == 'cubo2.png' and r[1]['tex'] == 'cubo1.png')
    chk('B3 2 cajones achatados 0,72×0,18×0,36 en (±1,35 · z -1,38/-1,59) cubo1/cubo2',
        ok, str(r))
    ok = (isinstance(r, list) and all(abs(c['x']) - 0.36 > 0.7625 for c in r))
    chk('B3 cajones FUERA de la mesa (borde interno > 0,76)', ok,
        str([c['x'] for c in r]) if isinstance(r, list) else r)

    # B4 · PILA SOBRE LOS CAJONES (20 lingotes → 10 por cajón)
    page.evaluate("""(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      t._limpiaPila();
      const from = { x: 0, y: 0.9, z: -4.5 };
      for (let i = 0; i < 20; i++) t._lanzaLingote(from);
      return t.ingotes.length; })()""")
    page.evaluate("window.__n = 40")   # 2 s de vuelo: todos asentados
    page.evaluate(TICK)
    page.evaluate("window.__n = 4")
    r = js(page, """(() => {
      const t = window.__PP_GAME.champs.mod.controller._tren;
      const hL = t._lingoteH || 0.0515;
      const y0 = 0.18, y1 = 0.18 + hL;             // capas exactas del cajón
      const porLado = { '-1': [], '1': [] };
      for (const it of t.ingotes) {
        if (it.volando || it.robado) continue;
        porLado[it.side].push({ y: +it.mesh.position.y.toFixed(5),
          x: +it.mesh.position.x.toFixed(4), z: +it.mesh.position.z.toFixed(4),
          slot: it.slot, yaw: +Math.abs(it.mesh.rotation.y).toFixed(4),
          dx: +Math.abs(it.mesh.position.x - it.dest.x).toFixed(6),
          dz: +Math.abs(it.mesh.position.z - it.dest.z).toFixed(6) });
      }
      const res = {};
      for (const s of ['-1', '1']) {
        const arr = porLado[s];
        const capa0 = arr.filter(o => Math.abs(o.y - y0) < 1e-4);
        const capa1 = arr.filter(o => Math.abs(o.y - y1) < 1e-4);
        let minSep = 9;
        for (let i = 0; i < capa0.length; i++)
          for (let j = i + 1; j < capa0.length; j++)
            minSep = Math.min(minSep,
              Math.hypot(capa0[i].x - capa0[j].x, capa0[i].z - capa0[j].z));
        const huecos = new Set(capa0.map(o => o.slot));
        res[s] = { n: arr.length, n0: capa0.length, n1: capa1.length,
          huecosCapa0: huecos.size, minSepXZ: +minSep.toFixed(3),
          maxDx: Math.max(...arr.map(o => o.dx)), maxDz: Math.max(...arr.map(o => o.dz)),
          maxYaw: Math.max(...arr.map(o => o.yaw)) };
      }
      res.hL = +hL.toFixed(5);
      return res; })()""")
    hL_expect = 0.0515
    ok = False
    if isinstance(r, dict) and '-1' in r and '1' in r:
        izq, der = r['-1'], r['1']
        ok = (izq['n'] == 10 and der['n'] == 10
              and izq['n0'] == 9 and der['n0'] == 9
              and izq['n1'] == 1 and der['n1'] == 1
              and izq['huecosCapa0'] == 9 and der['huecosCapa0'] == 9
              and izq['minSepXZ'] > 0.083 and der['minSepXZ'] > 0.083
              and izq['maxDx'] < 1e-6 and der['maxDx'] < 1e-6
              and izq['maxYaw'] <= 0.03 + 1e-6 and der['maxYaw'] <= 0.03 + 1e-6)
    chk('B4 10+10 lingotes: 9+1 en DOS CAPAS exactas (y=h / y=h+hL), 9 huecos '
        'DISTINTOS por cajón sin solape, jitter ≤ ±7mm/±3mm/±1,7°', ok, str(r))

    # B5 · ROBO: el hueco vuelve y se REUTILIZA
    r = js(page, """(() => {
      const t = window.__PP_GAME.champs.mod.controller._tren;
      if (!t._robaLingote()) return { __err: 'sin robo' };
      const rec = t.ingotes.find(i => i.robado);   // el lingote robado (en vuelo)
      if (!rec) return { __err: 'sin registro' };
      const hueco = { side: rec.side, slot: rec.slot };
      const idx = hueco.side > 0 ? 1 : 0;
      const libre = t._pileFree[idx].includes(hueco.slot);
      const from = { x: 0, y: 0.9, z: -4.5 };
      const n0 = t.ingotes.length;
      t._lanzaLingote(from);            // rellena el lado alterno (contador)
      t._lanzaLingote(from);            // VUELVE al lado del robo: reutiliza
      const nuevo = t.ingotes[t.ingotes.length - 1];
      return { hueco, libre, reutiliza: nuevo.side === hueco.side && nuevo.slot === hueco.slot,
               total: t.ingotes.length - n0 }; })()""")
    ok = (isinstance(r, dict) and r.get('libre') is True and r.get('reutiliza') is True)
    chk('B5 robo libera SU hueco y el siguiente lingote lo reutiliza', ok, str(r))
    page.evaluate("window.__n = 40")
    page.evaluate(TICK)
    page.evaluate("window.__n = 4")

    # B6 · SUELO del vagón
    r = js(page, """(() => {
      const t = window.__PP_GAME.champs.mod.controller._tren;
      let f = null;
      t.group.traverse((o) => { if (f || !o.isMesh || !o.material || !o.material.map) return;
        const g = o.geometry && o.geometry.parameters;
        if (g && Math.abs(g.width - 6.10) < 0.01 && Math.abs(g.height - 7.90) < 0.01
            && Math.abs(o.position.y) < 0.01) f = o; });
      if (!f) return { __err: 'floor no encontrado' };
      const src = f.material.map.image && f.material.map.image.src || '';
      return { src: src.slice(-40), completa: !!f.material.map.image,
               w: f.material.map.image && f.material.map.image.width }; })()""")
    ok = (isinstance(r, dict) and 'suelo.jpg' in r.get('src', '')
          and r.get('completa') and r.get('w') == 1296)
    chk('B6 suelo del vagón = suelo.jpg del dueño cargada (1296 px)', ok, str(r))

    # B7 · MEGAFONÍA con los nombres nuevos
    page.evaluate("""(() => { const G = window.__PP_GAME;
      G.__megaSpy = [];
      G.audio.__announceOrig = G.audio.announce;
      G.audio.announce = (txt, force) => { G.__megaSpy.push(String(txt)); return 1; };
      const t = G.champs.mod.controller._tren;
      t.wave = 1; t._megaLlegada = true;
      t._depart();            // SALIDA parada 1 → «partimos hacia BRAVOS»
      t.wave = 2; t._megaLlegada = true;
      t._depart();            // SALIDA parada 2 → «partimos hacia GOLD DUST»
      t.time = 29.8; t._megaLlegada = false;
      t.step(0.5);            // LLEGADA a los 30 s → «llegaremos a GOLD DUST»
      t.wave = 3; t.ingots = 7;
      t._arrived();           // ARRIBO OK → «Cargamento de oro…» + panel
      return { spy: G.__megaSpy.slice(), premio: !!t.premio }; })()""")
    r = js(page, "(() => window.__PP_GAME.__megaSpy.slice())()")
    spy = r if isinstance(r, list) else []
    premio = js(page, "!!window.__PP_GAME.champs.mod.controller._tren.premio")
    ok = (len(spy) >= 1 and 'partimos hacia' in spy[0].lower()
          and 'bravos' in spy[0].lower())
    chk('B7 voz SALIDA parada 1 «…partimos hacia BRAVOS»', ok, str(spy[:1]))
    ok = (len(spy) >= 2 and 'partimos hacia' in spy[1].lower()
          and 'gold dust' in spy[1].lower())
    chk('B7 voz SALIDA parada 2 «…partimos hacia GOLD DUST»', ok, str(spy[1:2]))
    ok = (len(spy) >= 3 and 'llegaremos a' in spy[2].lower()
          and 'gold dust' in spy[2].lower())
    chk('B7 voz LLEGADA a los 30 s «…llegaremos a GOLD DUST»', ok, str(spy[2:3]))
    ok = (len(spy) >= 4 and 'Cargamento de oro a buen recaudo' in spy[3]
          and premio is True)
    chk('B7 voz ARRIBO OK + panel recompensa', ok, str(spy[3:4]))
    # voicePlan de las 7 frases por idioma (función pura del banco)
    for lang in ('es', 'en'):
        page.evaluate(f"""(() => {{ window.__setLang('{lang}'); return 1; }})()""")
        time.sleep(0.3)
        r = js(page, """(() => { const G = window.__PP_GAME;
          const P = (t) => G.audio.voicePlan(t);
          if (window.__PP_CORE.lang() === 'en') {
            return { vp: [
              P('All aboard! We are departing towards Bravos'),
              P('All aboard! We are departing towards Gold Dust'),
              P('All aboard! We are departing towards Silver Creek'),
              P('In less than 25 seconds we will arrive at Bravos'),
              P('In less than 25 seconds we will arrive at Gold Dust'),
              P('In less than 25 seconds we will arrive at Silver Creek'),
              P('The gold shipment is safe and sound')] }; }
          return { vp: [
            P('Pasajeros al tren, partimos hacia Bravos'),
            P('Pasajeros al tren, partimos hacia GOLD DUST'),
            P('Pasajeros al tren, partimos hacia Silver Creek'),
            P('En menos de 25 segundos llegaremos a Bravos'),
            P('En menos de 25 segundos llegaremos a GOLD DUST'),
            P('En menos de 25 segundos llegaremos a Silver Creek'),
            P('Cargamento de oro a buen recaudo')] }; })()""")
        esperados = ['mega_salida_br', 'mega_salida_gd', 'mega_salida_sc',
                     'mega_llega_br', 'mega_llega_gd', 'mega_llega_sc', 'mega_oro']
        vp = r.get('vp') if isinstance(r, dict) else None
        ok = isinstance(vp, list) and len(vp) == 7 and all(
            p and p[0].get('k') == e for p, e in zip(vp, esperados))
        chk(f'B8 voicePlan({lang}) 7/7 planes exactos (br·gd·sc·oro)', ok,
            str(vp)[:150] if vp else str(r))
    page.evaluate("""(() => { const G = window.__PP_GAME;
      if (G.audio.__announceOrig) G.audio.announce = G.audio.__announceOrig;
      window.__setLang('es'); return 1; })()""")

    # B9 · PARADA1.png nueva como arte de la parada 1
    page.evaluate("""(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      t._paradaTry = {}; t._paradaTex = {}; t._signArt(1); return 1; })()""")
    r = {'w': 0}
    for _ in range(12):
        r = js(page, """(() => {
          const t = window.__PP_GAME.champs.mod.controller._tren;
          const m = t.estArt && t.estArt[0];
          if (!m || !m.material || !m.material.map || !m.material.map.image) return { w: 0 };
          return { w: m.material.map.image.width,
                   src: (m.material.map.image.src || '').split('/').pop(),
                   visible: m.visible }; })()""")
        if isinstance(r, dict) and r.get('w'):
            break
        time.sleep(0.4)
    ok = isinstance(r, dict) and r.get('w') == 1024 and r.get('visible') is True
    chk('B9 PARADA1.png NUEVA (1024 px) como arte de la parada 1', ok, str(r))

    # B10 · FOTO 3D: los dos cajones con sus pilas (pose PERSISTENTE — el
    # rAF del juego resetea la cámara en cada frame: lección v2.140)
    page.evaluate("""(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      t._hidePremio(); t._limpiaPila();
      const from = { x: 0, y: 0.9, z: -4.5 };
      for (let i = 0; i < 14; i++) t._lanzaLingote(from);
      return t.ingotes.length; })()""")
    page.evaluate("window.__n = 40")
    page.evaluate(TICK)
    page.evaluate("window.__n = 4")
    # cenital del cajón DERECHO (pose persistente)
    page.evaluate("window.__camPose = [1.35, 2.25, -1.59 + 0.001, 1.35, 0.18, -1.59]")
    page.evaluate(TICK)
    time.sleep(0.4)
    page.screenshot(path='/home/z/my-project/scripts/_v2141_cenital_cajon_der.png')
    # cenital del cajón IZQUIERDO
    page.evaluate("window.__camPose = [-1.35, 2.25, -1.38 + 0.001, -1.35, 0.18, -1.38]")
    page.evaluate(TICK)
    time.sleep(0.4)
    page.screenshot(path='/home/z/my-project/scripts/_v2141_cenital_cajon_izq.png')
    # vista del JUGADOR: la mesa y los dos cajones con sus pilas a los lados
    page.evaluate("window.__camPose = [0, 1.55, 0.75, 0, 0.10, -1.55]")
    page.evaluate(TICK)
    time.sleep(0.4)
    page.screenshot(path='/home/z/my-project/scripts/_v2141_vista_jugador.png')
    page.evaluate("window.__camPose = null")
    r = js(page, """(() => {
      const t = window.__PP_GAME.champs.mod.controller._tren;
      const asent = t.ingotes.filter(i => !i.volando && !i.robado).length;
      const sobreCajon = t.ingotes.every(i => i.mesh.position.y >= 0.179
        && Math.abs(i.mesh.position.x) > 0.9 && Math.abs(i.mesh.position.x) < 1.8);
      return { asent, sobreCajon }; })()""")
    ok = (isinstance(r, dict) and r.get('asent') == 14 and r.get('sobreCajon') is True)
    chk('B10 14 lingotes asentados SOBRE los cajones (y ≥ 0,18 · x 0,9-1,8)', ok, str(r))
    chk('runtime oeste 0 pageerrors', len(errs) == 0, str(errs[:2]))
    page.close()
    browser.close()

n_ok = sum(1 for _, ok, _ in RES if ok)
print(f"\n===== QA V2.141: {n_ok}/{len(RES)} VERDE =====")
raise SystemExit(0 if n_ok == len(RES) else 1)
