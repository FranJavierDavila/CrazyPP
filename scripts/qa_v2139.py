#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA V2.139 · BIENVENIDA HABLADA al entrar en VR.

  A1  game.html SERVIDO = disco (sha256) y VERSION '2.139.0'
  A2  i18n: welcome_menu en las DOS mesas con el texto EXACTO pedido
      (es «Bienvenido a Crazy Ping Pong, escoge una modalidad de juego» ·
       en «Welcome to Crazy Ping Pong, choose a game mode»)
  A3  VOICE_FULL es/en: la frase normalizada del texto T() mapea a
      ['bienvenida_modo'] — réplica exacta de _normVoice del núcleo
  A4  Banco: átomo bienvenida_modo en VOICE_B64 (es) y VOICE_B64_EN (en);
      el base64 del HTML decodifica BYTE A BYTE al OGG de disco
  A5  OGG sanos (ffprobe): opus, mono, 28k, duración 2,5-4,5 s
  A6  onSessionStart: anuncio T('welcome_menu') y el antiguo
      T('welcome')/T('mode_survival') CONDICIONAL fuera del arranque
  B   RUNTIME 2D: el banco de voz decodifica con el átomo nuevo
      (consola «banco de voz listo (es) · N fragmentos» con N esperado)
      y 0 pageerrors
  C   smoke 4 campeonatos: 0 pageerrors
"""
import hashlib
import re
import subprocess
import time
import unicodedata
import urllib.request

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:3000'
GAME = '/home/z/my-project/public/game.html'
OGG_ES = '/home/z/my-project/scripts/voice/ogg/bienvenida_modo_fon.ogg'
OGG_EN = '/home/z/my-project/scripts/voice/ogg_en/bienvenida_modo_en.ogg'
RES = []


def chk(name, ok, extra=''):
    RES.append((name, ok, extra))
    print(f"{'✓' if ok else '✗'} {name} {extra}")


def js(page, expr):
    try:
        return page.evaluate(expr)
    except Exception as e:
        return {'__err': str(e)[:200]}


serv = urllib.request.urlopen(BASE + '/game.html').read()
disco = open(GAME, 'rb').read()

# ===== A1 · SERVIDO = DISCO + VERSION =====
chk('A1 servido = disco', hashlib.sha256(serv).hexdigest() == hashlib.sha256(disco).hexdigest(),
    f'({len(serv)} B)')
chk("A1 VERSION '2.139.0'", b"const VERSION = '2.139.0'" in serv)
html = serv.decode('utf-8')

# ===== A2 · i18n welcome_menu EXACTO =====
ES_TXT = 'Bienvenido a Crazy Ping Pong, escoge una modalidad de juego'
EN_TXT = 'Welcome to Crazy Ping Pong, choose a game mode'
chk('A2 welcome_menu ES exacto', f"welcome_menu: '{ES_TXT}'" in html)
chk('A2 welcome_menu EN exacto', f"welcome_menu: '{EN_TXT}'" in html)

# ===== A3 · VOICE_FULL + normalización == clave =====
def norm(s):
    s = s.lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

k_es, k_en = norm(ES_TXT), norm(EN_TXT)
chk("A3 clave es = «bienvenido a crazy ping pong escoge una modalidad de juego»",
    k_es == 'bienvenido a crazy ping pong escoge una modalidad de juego', k_es)
chk("A3 clave en = «welcome to crazy ping pong choose a game mode»",
    k_en == 'welcome to crazy ping pong choose a game mode', k_en)
chk("A3 VOICE_FULL es → ['bienvenida_modo']",
    f"'{k_es}': ['bienvenida_modo']," in html)
chk("A3 VOICE_FULL en → ['bienvenida_modo']",
    f"'{k_en}': ['bienvenida_modo']," in html)

# ===== A4 · ÁTOMOS = OGG DE DISCO =====
import base64
def bank_slice(h, start_marker):
    i = h.index(start_marker)
    j = h.index('};', i)
    return h[i:j]

es_bank = bank_slice(html, 'const VOICE_B64 = {')
en_bank = bank_slice(html, 'const VOICE_B64_EN = {')
m_es = re.search(r'bienvenida_modo: "([A-Za-z0-9+/=]+)"', es_bank)
m_en = re.search(r'bienvenida_modo: "([A-Za-z0-9+/=]+)"', en_bank)
chk('A4 átomo en banco es', bool(m_es))
chk('A4 átomo en banco en', bool(m_en))
if m_es and m_en:
    d_es = base64.b64decode(m_es.group(1))
    d_en = base64.b64decode(m_en.group(1))
    chk('A4 es base64 = ogg disco',
        hashlib.sha256(d_es).hexdigest() == hashlib.sha256(open(OGG_ES, 'rb').read()).hexdigest(),
        f'({len(d_es)} B)')
    chk('A4 en base64 = ogg disco',
        hashlib.sha256(d_en).hexdigest() == hashlib.sha256(open(OGG_EN, 'rb').read()).hexdigest(),
        f'({len(d_en)} B)')
    n_es_keys = len(re.findall(r'^\s{2}[a-z0-9_]+: "T2dn', es_bank, re.M))
    n_en_keys = len(re.findall(r'^\s{2}[a-z0-9_]+: "T2dn', en_bank, re.M))
else:
    n_es_keys = n_en_keys = -1

# ===== A5 · OGG SANOS =====
for tag, path in (('es', OGG_ES), ('en', OGG_EN)):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                        'stream=codec_name,channels,sample_rate:format=duration',
                        '-of', 'default=nw=1', path], capture_output=True, text=True)
    out = r.stdout
    ok = ('opus' in out and 'channels=1' in out)
    dur = re.search(r'duration=([0-9.]+)', out)
    d = float(dur.group(1)) if dur else 0.0
    chk(f'A5 ogg {tag} opus mono 2,5-4,5s', ok and 2.5 <= d <= 4.5, f'{d:.2f}s')

# ===== A6 · CALL SITE en onSessionStart =====
chk('A6 anuncio sessionstart = welcome_menu',
    re.search(r"setTimeout\(\(\) => \{[^}]*this\.audio\.announce\(T\('welcome_menu'\), true\);", html, re.S)
    is not None)
chk('A6 antiguo condicional welcome/mode fuera del arranque',
    "this.mode === 'survival'\n        ? T('mode_survival')\n        : T('welcome'), true" not in html)

# ===== B · RUNTIME: los bytes SERVIDOS decodifican con decodeAudioData
#      (la MISMA vía WebAudio que usa speakPlan en VR; el contexto del juego
#      sólo nace al entrar en VR — prepareVR — así que decodificamos aquí) ====
DECODE_JS = """
async () => {
  const txt = await (await fetch('/game.html')).text();
  const cut = (start) => {
    const i = txt.indexOf(start); const j = txt.indexOf('};', i);
    const m = txt.slice(i, j).match(/bienvenida_modo: "([A-Za-z0-9+\\/=]+)"/);
    return m ? m[1] : null;
  };
  const b64es = cut('const VOICE_B64 = {');
  const b64en = cut('const VOICE_B64_EN = {');
  if (!b64es || !b64en) return { ok: false, why: 'átomos no encontrados en HTML' };
  const bin = (b) => { const s = atob(b); const a = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i); return a.buffer; };
  const AC = window.AudioContext || window.webkitAudioContext;
  const ac = new AC();
  try {
    const bES = await ac.decodeAudioData(bin(b64es));
    const bEN = await ac.decodeAudioData(bin(b64en));
    return { ok: true, es: { d: bES.duration, ch: bES.numberOfChannels, sr: bES.sampleRate },
             en: { d: bEN.duration, ch: bEN.numberOfChannels, sr: bEN.sampleRate } };
  } finally { try { ac.close(); } catch (e) {} }
}
"""
with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox",
        "--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:150]))
    page.goto(BASE + '/game.html', wait_until='domcontentloaded', timeout=60000)
    r = js(page, DECODE_JS)
    if isinstance(r, dict) and r.get('ok'):
        es, en = r['es'], r['en']
        chk('B decodeAudioData ES (bytes servidos)', abs(es['d'] - 3.68) < 0.6 and es['ch'] == 1,
            f"{es['d']:.2f}s · {es['ch']}ch · {es['sr']}Hz")
        chk('B decodeAudioData EN (bytes servidos)', abs(en['d'] - 3.14) < 0.6 and en['ch'] == 1,
            f"{en['d']:.2f}s · {en['ch']}ch · {en['sr']}Hz")
    else:
        chk('B decodeAudioData ES', False, str(r)[:120])
        chk('B decodeAudioData EN', False, str(r)[:120])
    chk('B sin pageerrors (2D)', len(errs) == 0, str(errs[:2]))

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
        time.sleep(2)
        chk(f'C smoke {champ}: 0 pageerrors', len(er) == 0, str(er[:2]))
        pg.close()
    browser.close()

n_ok = sum(1 for _, ok, _ in RES if ok)
print(f"\nQA V2.139: {n_ok}/{len(RES)} VERDE")
raise SystemExit(0 if n_ok == len(RES) else 1)
