#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deploy_pages.py — Despliegue del juego a GitHub Pages (rama «pages» de CrazyPP).

Uso:
    python3 scripts/deploy_pages.py              # ensambla sitio + smoke + commit local en refs/heads/pages
    python3 scripts/deploy_pages.py --no-smoke   # sin prueba Playwright (no recomendado)
    python3 scripts/deploy_pages.py --push       # + push de la rama pages (requiere GIT_TOKEN en el entorno)
    python3 scripts/deploy_pages.py --release    # + tag v<version> + GitHub Release con los 4 ZIPs
    python3 scripts/deploy_pages.py --backup     # + push main:proyecto (respaldo anti-rollback al día)

Flujo de «sucesivos deploys» (tras cada versión con QA verde):
    GIT_TOKEN=... python3 scripts/deploy_pages.py --push --release --backup
Cada ejecución añade un commit encadenado a refs/heads/pages (historial de despliegues).

Sitio servido (~126 MB · límite Pages 1 GB · máx 100 MB/fichero):
    game.html (2 reescrituras ruta absoluta→relativa, contadas y asertadas)
    championships/ · assets/ · vendor/ · tv.html · robots.txt · logo.svg
    + index.html (portada generada) + .nojekyll + PAGES-VERSION.txt

Requisito único del dueño (UNA vez): GitHub → CrazyPP → Settings → Pages →
    «Deploy from a branch» → rama «pages» · carpeta /(root) → Save.
URL: https://franjavierdavila.github.io/CrazyPP/

Diseño sin riesgo para los servidores vivos (:3000/:81 intactos): el sitio se
ensambla desde `git archive HEAD` (solo ficheros trackeados, inmune al árbol de
trabajo) y el commit se crea con plumbing (GIT_INDEX_FILE + hash-object +
commit-tree) sin tocar jamás el working tree.
"""
import asyncio
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
import threading
import glob

REPO = os.environ.get('CPP_RAIZ') or '/home/z/my-project'   # r109-b: el default vuelve al REPO VIVO (el fósil upload/ de la era r127 está eliminado)
SITE = os.path.join(REPO, 'pages-site')
OWNER_REPO = 'FranJavierDavila/CrazyPP'
PAGES_URL = 'https://franjavierdavila.github.io/CrazyPP/'
PREFIX = '/CrazyPP'
PORT = 3006
MAX_FILE = 100_000_000
SOLO_ZIP = 'crazypp-live-service-SOLO.zip'

SITE_PATHS = ['public/game.html', 'public/championships', 'public/assets',
              'public/vendor', 'public/tv.html', 'public/robots.txt', 'public/logo.svg',
              'public/ugc',          # r85: EL TALLER UGC (editor de etapas/campeonatos)
              'public/telemetria.html',   # r87: PANEL de telemetría (URL estable en Pages)
              'public/vr_arm.glb',       # r93 · LOS BRAZOS del rival (GLB del dueño)
              'public/manifest.webmanifest', 'public/sw.js',   # r109 · M3 PWA
              'public/actualizar.html',  # r98 · PÁGINA NUCLEAR (borra SW+cachés)
              'public/logo-192.png', 'public/logo-512.png', 'public/logo-maskable-512.png']

# (original, sustituto, ocurrencias esperadas) — cualquier desvío ABORTA el despliegue
REWRITES = [
    ('src="/vendor/socket.io.min.js"', 'src="vendor/socket.io.min.js"', 1),
    ('href="/tv.html"', 'href="tv.html"', 1),
]
SMOKE_ALLOW_404 = ('/favicon.ico',)      # petición automática del navegador
SMOKE_ALLOW_PREFIX = ('/socket.io',      # sondeo del cliente incluido en vendor/
                      '/api/')           # ronda 11: bajo 127.0.0.1 el juego enruta la telemetría al receptor LOCAL (que en el sitio estático no existe — en producción real va al Worker); el beacon de 5 s cae al vacío y se tolera


def sh(args, **kw):
    kw.setdefault('cwd', REPO)   # r126: permite cwd distinto (p. ej. SITE)
    return subprocess.run(args, check=True, capture_output=True, text=True, **kw)


def out(args, **kw):
    return sh(args, **kw).stdout.strip()


def git_dir():
    """r61 · GIT_DIR real del repo (compatible con .git-dir y con WORKTREE:
    el reciclaje del sandbox convirtió upload/.git en un PUNTERO de worktree
    "gitdir: …/.git/worktrees/upload" — rev-parse resuelve el gitdir verdadero
    en ambos casos)."""
    try:
        return out(['git', 'rev-parse', '--absolute-git-dir']) or \
            os.path.join(REPO, '.git')
    except Exception:
        return os.path.join(REPO, '.git')


def ensure_excluded():
    # r61 · con upload/.git como PUNTERO de worktree no hay info/exclude
    # propio: el exclude era higiene local (que pages-site no aparezca en
    # el status) — si no se puede escribir, se continúa (el deploy usa
    # plumbing y jamás toca el índice del worktree).
    try:
        exc = os.path.join(git_dir(), 'info', 'exclude')
        os.makedirs(os.path.dirname(exc), exist_ok=True)
        with open(exc) as f:
            cur = f.read()
        if 'pages-site' not in cur:
            with open(exc, 'a') as f:
                f.write('\npages-site\n')
    except OSError as e:
        print(f'  · info/exclude no escribible ({e.__class__.__name__}): '
              'higiene local omitida — el deploy no la necesita')


def assemble():
    if os.path.exists(SITE):
        shutil.rmtree(SITE)
    os.makedirs(SITE)
    cmd = 'git archive HEAD ' + ' '.join(SITE_PATHS) + \
          ' | tar -x --strip-components=1 -C ' + SITE
    subprocess.run(cmd, cwd=REPO, shell=True, check=True)


def detect_version():
    html = open(os.path.join(SITE, 'game.html'), encoding='utf-8', errors='replace').read()
    m = (re.search(r"const\s+VERSION\s*=\s*['\"]([0-9A-Za-z.\-]+)['\"]", html)
         or re.search(r"__PP_VERSION\s*=\s*['\"]([0-9A-Za-z.\-]+)['\"]", html))
    if not m:
        sys.exit('✗ No encuentro window.__PP_VERSION en el game.html ensamblado')
    return m.group(1)


def apply_rewrites():
    path = os.path.join(SITE, 'game.html')
    html = open(path, encoding='utf-8').read()
    for orig, repl, expected in REWRITES:
        n = html.count(orig)
        if n != expected:
            sys.exit(f'✗ Reescritura {orig!r}: esperaba {expected}, hay {n}. '
                     f'Revisa game.html antes de desplegar.')
        html = html.replace(orig, repl)
    # r31 · escritura ATÓMICA (temp + os.replace) — el mount del repo no
    # honra O_TRUNC (lección r29): la escritura directa del game.html
    # REESCRITO dejó 2 bytes nulos de cola en el despliegue v3.6.127
    # (el tar extrae el fichero COMPLETO y la reescritura lo encoge).
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(html)
    os.replace(tmp, path)
    # GUARD byte-exacto: el game.html del sitio debe ser EXACTAMENTE el
    # del repo con las 2 reescrituras — ni un byte de más (los nulos de
    # cola de una escritura no truncada se detectan aquí y ABORTAN).
    esperado = open(os.path.join(REPO, 'public', 'game.html'), 'rb').read()
    for orig, repl, _ in REWRITES:
        esperado = esperado.replace(orig.encode('utf-8'), repl.encode('utf-8'))
    real = open(path, 'rb').read()
    if real != esperado:
        sys.exit(f'✗ game.html del sitio DIFIERE del esperado '
                 f'({len(real):,} B vs {len(esperado):,} B). Escritura sin '
                 f'truncar o corrupción — despliegue abortado.')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


LANDING = """<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CRAZY PING PONG · @@VERSION@@</title>
<link rel="icon" href="logo.svg" type="image/svg+xml">
<style>
  /* r152 · LA PORTADA CLÁSICA VIVE AQUÍ: desde r151 game.html entra directo
     al salón, así que la LANDING de la raíz hereda el aspecto de la portada
     que tenía game.html (logo, palas de idioma, JUGAR EN VR). El idioma se
     guarda en pp_lang (la MISMA clave que lee c00 al arrancar el juego) y
     el botón lleva a game.html?vr=1 → un toque cualquiera y estás en VR. */
  :root { color-scheme: dark; }
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { height:100%; }
  body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color:#e9edf2;
    background: radial-gradient(120% 90% at 50% 8%, #0b2050 0%, #071229 52%, #050810 100%);
    display:flex; align-items:center; justify-content:center; overflow:hidden; }
  #bg { position:fixed; inset:0; overflow:hidden; pointer-events:none; }
  .bgblur { position:absolute; inset:-90px;
    background-image:url("assets/externos/portada.jpg"); background-size:cover;
    background-position:center 38%;
    filter:blur(16px) brightness(0.42) saturate(1.25);
    animation:kenburns 30s ease-in-out infinite alternate; }
  @keyframes kenburns { from { transform:scale(1.06) translate(-1.2%,-1%); }
    to { transform:scale(1.22) translate(1.4%,1.6%); } }
  .rays { position:absolute; top:-30%; height:170%; width:34vw;
    background:linear-gradient(90deg, transparent 6%, rgba(96,166,255,0.13) 50%, transparent 94%);
    transform:rotate(14deg); filter:blur(3px);
    animation:sweep 10s ease-in-out infinite alternate; }
  .rays.r1 { left:8vw; }
  .rays.r2 { right:8vw; transform:rotate(-15deg); animation-delay:-4.5s; animation-duration:12s; }
  @keyframes sweep { from { opacity:0.25; transform:rotate(11deg) translateX(-4vw); }
    to { opacity:0.8; transform:rotate(17deg) translateX(5vw); } }
  .bball { position:absolute; border-radius:50%;
    background:radial-gradient(circle at 34% 30%, #ffffff 0%, #e8ecf2 55%, #b9c2cf 100%);
    box-shadow:0 0 22px rgba(255,255,255,0.55); animation:flyball linear infinite; }
  .bball.b1 { width:26px; height:26px; top:62%; animation-duration:9.5s; }
  .bball.b2 { width:15px; height:15px; top:24%; animation-duration:13s; animation-delay:-6s; opacity:0.85; }
  .bball.b3 { width:11px; height:11px; top:78%; animation-duration:16s; animation-delay:-3s; opacity:0.6; }
  @keyframes flyball { 0% { transform:translate(-8vw,6vh); opacity:0; } 8% { opacity:1; }
    50% { transform:translate(46vw,-9vh); } 92% { opacity:1; }
    100% { transform:translate(108vw,5vh); opacity:0; } }
  .star { position:absolute; width:7px; height:7px; border-radius:50%;
    background:#ffd257; box-shadow:0 0 10px #ffd257;
    animation:twinkle 3.2s ease-in-out infinite; }
  .star.s1 { left:12%; top:18%; } .star.s2 { left:85%; top:26%; animation-delay:-1.1s; }
  .star.s3 { left:22%; top:74%; animation-delay:-2s; } .star.s4 { left:76%; top:70%; animation-delay:-0.6s; }
  .star.s5 { left:50%; top:12%; animation-delay:-2.6s; } .star.s6 { left:38%; top:86%; animation-delay:-1.7s; }
  @keyframes twinkle { 0%,100% { opacity:0.15; transform:scale(0.7); }
    50% { opacity:0.95; transform:scale(1.25); } }
  main { position:relative; z-index:2; display:flex; flex-direction:column; align-items:center;
    gap:20px; width:100%; max-width:760px; padding:24px 18px; max-height:100vh; overflow-y:auto; }
  .hero-wrap { animation:heroFloat 6s ease-in-out infinite; }
  .hero-wrap img { display:block; width:min(340px, 72vw); height:auto;
    filter:drop-shadow(0 18px 40px rgba(0,0,0,0.6)); }
  @keyframes heroFloat { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-10px); } }
  .padrow { display:flex; gap:26px; }
  .padbtn { display:flex; flex-direction:column; align-items:center; gap:7px;
    background:rgba(255,255,255,0.055); border:2px solid rgba(255,255,255,0.16);
    border-radius:22px; padding:12px 24px 9px; cursor:pointer; color:#e9edf2;
    font-family:inherit; transition:transform .18s, border-color .18s, box-shadow .18s; }
  .padbtn img { width:84px; height:84px; object-fit:contain;
    filter:drop-shadow(0 6px 14px rgba(0,0,0,0.55)); }
  .padbtn .padlbl { font-size:13px; font-weight:800; letter-spacing:2.2px; color:#9aa7b4; }
  .padbtn:hover { transform:translateY(-3px); border-color:rgba(255,255,255,0.38); }
  .padbtn.sel { border-color:#ffd257; box-shadow:0 0 16px rgba(255,210,87,0.22); }
  .padbtn.sel .padlbl { color:#ffd257; }
  #vrbtn { background:none; border:none; cursor:pointer; display:block; }
  #vrbtn img { display:block; width:min(340px, 76vw); height:auto;
    filter:drop-shadow(0 14px 30px rgba(0,0,0,0.55)); transition:transform .18s; }
  #vrbtn:hover img { transform:scale(1.06); }
  #vrbtn:active img { transform:scale(0.97); }
  #status { font-size:13.5px; color:#8d9aa8; min-height:20px; text-align:center;
    max-width:720px; line-height:1.5; }
  .footer { display:flex; flex-wrap:wrap; align-items:center; justify-content:center;
    gap:8px 10px; font-size:13px; color:#75828f; }
  .footlink { background:none; border:none; cursor:pointer; font-family:inherit;
    font-size:13px; color:#8fd3e8; text-decoration:underline dotted; padding:2px 4px; }
  .dot { opacity:0.5; }
  #verBadge { font-size:12px; font-weight:700; letter-spacing:.08em; color:#ffd257; }
  .deploy { font-size:11px; color:#5c6a82; margin-top:2px; }
  .deploy code { color:#7e8ea8; }
  @media (max-width:560px) {
    .padbtn img { width:64px; height:64px; } .padrow { gap:14px; }
    .hero-wrap img { width:min(260px, 68vw); }
  }
</style></head>
<body>
<div id="bg">
  <div class="bgblur"></div>
  <div class="rays r1"></div>
  <div class="rays r2"></div>
  <span class="bball b1"></span><span class="bball b2"></span><span class="bball b3"></span>
  <span class="star s1"></span><span class="star s2"></span><span class="star s3"></span>
  <span class="star s4"></span><span class="star s5"></span><span class="star s6"></span>
</div>
<main>
  <div class="hero-wrap"><img src="assets/externos/portada.jpg" alt="CRAZY PING PONG"></div>
  <div class="padrow">
    <button class="padbtn" data-lang="es" type="button">
      <img src="assets/externos/pad_es.png" alt="Español"><span class="padlbl">ESPAÑOL</span>
    </button>
    <button class="padbtn" data-lang="en" type="button">
      <img src="assets/externos/pad_en.png" alt="English"><span class="padlbl">ENGLISH</span>
    </button>
  </div>
  <a id="vrbtn" href="game.html?vr=1" aria-label="Jugar en VR">
    <img id="playEs" src="assets/externos/jugar_es.png" alt="JUGAR EN VR">
    <img id="playEn" src="assets/externos/jugar_en.png" alt="PLAY IN VR" style="display:none">
  </a>
  <div id="status">Comprobando compatibilidad con WebXR…</div>
  <div class="footer">
    <a id="arlink" class="footlink" href="game.html?ar=1" style="display:none">🏠 PASSTHROUGH · tu habitación</a>
    <span class="dot" id="arDot" style="display:none">·</span>
    <a class="footlink" href="tv.html" target="_blank" rel="noreferrer">📺 TV en vivo</a>
    <span class="dot">·</span>
    <a class="footlink" href="https://ko-fi.com/escala3d" target="_blank" rel="noreferrer">☕ Apoyar en Ko-fi</a>
    <span class="dot">·</span>
    <span id="verBadge">V@@VERSION@@</span>
  </div>
  <p class="deploy">Desplegado desde la rama <code>pages</code> · @@FECHA@@ · game @@GAME12@@</p>
</main>
<script>
(function () {
  'use strict';
  function savedLang() {
    var l = null;
    try { l = localStorage.getItem('pp_lang'); } catch (e) { /* */ }
    if (l === 'es' || l === 'en') return l;
    var n = String(navigator.language || 'es').toLowerCase();
    return n.indexOf('en') === 0 ? 'en' : 'es';   // es* → ES · resto → EN (como c00)
  }
  var lang = savedLang();
  var xrOK = false, checked = false;
  var statusEl = document.getElementById('status');
  var TXT = {
    es: { ok: '✅ VR LISTO — ponte el visor y pulsa JUGAR',
          no: '🖥️ Sin visor: entra igual — el salón ya vive en 2D',
          sin: '🖥️ Este navegador no soporta WebXR — el juego funciona igual en 2D',
          chk: 'Comprobando compatibilidad con WebXR…' },
    en: { ok: '✅ VR READY — put the headset on and press PLAY',
          no: '🖥️ No headset: come in anyway — the hall already lives in 2D',
          sin: '🖥️ This browser does not support WebXR — the game works in 2D anyway',
          chk: 'Checking WebXR support…' }
  };
  function paint() {
    document.querySelectorAll('.padbtn').forEach(function (b) {
      b.classList.toggle('sel', b.dataset.lang === lang);
    });
    document.getElementById('playEs').style.display = lang === 'en' ? 'none' : '';
    document.getElementById('playEn').style.display = lang === 'en' ? '' : 'none';
    if (!checked) { statusEl.textContent = TXT[lang].chk; return; }
    statusEl.textContent = navigator.xr ? (xrOK ? TXT[lang].ok : TXT[lang].no) : TXT[lang].sin;
  }
  document.querySelectorAll('.padbtn').forEach(function (b) {
    b.addEventListener('click', function () {
      lang = b.dataset.lang;
      try { localStorage.setItem('pp_lang', lang); } catch (e) { /* */ }
      paint();
    });
  });
  if (navigator.xr && navigator.xr.isSessionSupported) {
    navigator.xr.isSessionSupported('immersive-vr').then(function (ok) {
      xrOK = ok; checked = true; paint();
    }).catch(function () { checked = true; paint(); });
    navigator.xr.isSessionSupported('immersive-ar').then(function (ok) {
      if (ok) {
        document.getElementById('arlink').style.display = '';
        document.getElementById('arDot').style.display = '';
      }
    }).catch(function () { /* */ });
  } else {
    checked = true;
  }
  paint();
})();
</script>
</body></html>
"""


def write_extras(version, head, game_sha):
    with open(os.path.join(SITE, '.nojekyll'), 'w') as f:
        f.write('')
    html = (LANDING
            .replace('@@VERSION@@', version)
            .replace('@@COMMIT@@', head[:9])
            .replace('@@REPO@@', OWNER_REPO)
            .replace('@@FECHA@@', datetime.datetime.now().strftime('%d-%m-%Y %H:%M'))
            .replace('@@GAME12@@', game_sha[:12]))
    with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    info = (f'version={version}\n'
            f'fuente_commit={head}\n'
            f'game_sha256={game_sha}\n'
            f'reescrituras={len(REWRITES)}\n'
            f'fecha={datetime.datetime.now().isoformat(timespec="seconds")}\n'
            f'url={PAGES_URL}\n')
    with open(os.path.join(SITE, 'PAGES-VERSION.txt'), 'w') as f:
        f.write(info)


def verify_site():
    files, total = [], 0
    for root, _dirs, fs in os.walk(SITE):
        for f in fs:
            ap = os.path.join(root, f)
            sz = os.path.getsize(ap)
            if sz > MAX_FILE:
                sys.exit(f'✗ {ap} pesa {sz} B > límite Pages 100 MB/fichero')
            files.append(os.path.relpath(ap, SITE))
            total += sz
    print(f'  · sitio: {len(files)} ficheros · {total/1e6:.1f} MB (límite Pages 1000 MB)')
    return len(files)


async def smoke(version):
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    from playwright.async_api import async_playwright

    class Prefixed(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=SITE, **k)

        def translate_path(self, path):
            if path == PREFIX:
                path = '/'
            elif path.startswith(PREFIX + '/'):
                path = path[len(PREFIX):]
            return super().translate_path(path)

        def log_message(self, *a):
            pass

    class QuietServer(ThreadingHTTPServer):
        def handle_error(self, *a):
            pass  # el navegador corta transferencias al cerrarse: ruido, no error

    httpd = QuietServer(('127.0.0.1', PORT), Prefixed)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{PORT}'

    bad404, failed, perr, nreq = [], [], [], 0

    def on_resp(r):
        nonlocal nreq
        if r.url.startswith(origin):
            nreq += 1
            if r.status >= 400:
                p = r.url.split(origin)[1]
                if not any(p.startswith(a) for a in SMOKE_ALLOW_PREFIX) and \
                   not any(p == a or p == a + '/' for a in SMOKE_ALLOW_404):
                    bad404.append((r.status, p))

    def on_fail(r):
        if r.url.startswith(origin) and r.failure and 'ERR_ABORTED' not in str(r.failure):
            failed.append((r.url.split(origin)[1], r.failure))

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=[
                '--enable-unsafe-swiftshader',
                '--autoplay-policy=no-user-gesture-required',
            ])
            page = await browser.new_page(viewport={'width': 1280, 'height': 800})
            page.on('response', on_resp)
            page.on('requestfailed', on_fail)
            page.on('pageerror', lambda e: perr.append(str(e)))
            await page.goto(f'{origin}{PREFIX}/game.html',
                            wait_until='domcontentloaded', timeout=60_000)
            await page.wait_for_timeout(22_000)
            ver = await page.evaluate('() => window.__PP_VERSION || null')
            await browser.close()
    finally:
        httpd.shutdown()

    print(f'  · smoke prefijo {PREFIX}: {nreq} peticiones al sitio')
    fails = []
    if ver != version:
        fails.append(f'__PP_VERSION={ver!r} (esperaba {version!r})')
    if bad404:
        fails.append(f'{len(bad404)} respuestas 4xx/5xx: ' +
                     '; '.join(f'{s} {u}' for s, u in bad404[:6]))
    if failed:
        fails.append(f'{len(failed)} peticiones fallidas: ' +
                     '; '.join(f'{u} [{r}]' for u, r in failed[:6]))
    if perr:
        fails.append(f'{len(perr)} pageerrors: ' + ' | '.join(perr[:3]))
    if fails:
        sys.exit('✗ SMOKE DEL PREFIJO FALLÓ:\n    ' + '\n    '.join(fails))
    print('  ✓ smoke verde: juego arrancado bajo prefijo /CrazyPP/, 0 fallos de red, 0 pageerrors')


def commit_pages_branch(version, head, game_sha, nfiles):
    idx = os.path.join(git_dir(), 'pages-index')
    if os.path.exists(idx):
        os.remove(idx)
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    sh(['git', 'read-tree', '--empty'], env=env)
    # r126 · bulk update: un solo `git add` con GIT_INDEX_FILE propio (antes:
    # hash-object + update-index POR FICHERO = 2 subprocessos por fichero y
    # timeouts en el mount lento del sandbox). CUIDADO (lección de ESTA ronda,
    # deploy da84c162a → sitio 404): el índice guarda rutas RELATIVAS A LA
    # RAÍZ DEL REPO — un `git add .` con cwd=SITE anida todo bajo
    # «pages-site/». Con --work-tree=SITE las rutas quedan en la RAÍZ del
    # tree, y core.fileMode=false sella 100644 como el bucle antiguo.
    sh(['git', '-c', 'core.fileMode=false',
        '--git-dir', git_dir(), '--work-tree', SITE,
        'add', '-f', '--all', '--', '.'], env=env, cwd=SITE)
    tree = out(['git', 'write-tree'], env=env)
    # r39 · COMMIT HUÉRFANO SIEMPRE (lección del incidente r39): el builder
    # legacy de Pages clona la rama y el historial ENCADENADO crece con cada
    # deploy (árboles completos por ronda) — dos builds seguidos marcaron
    # «Page build failed» hasta que la rama se APLASTÓ a un commit raíz
    # (1a266cb7, construido en ~2 min). Cada deploy nace RAÍZ: el clon del
    # builder pesa SIEMPRE lo mismo (solo el árbol del sitio).
    fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    msg = (f'deploy pages: {version} · fuente {head[:9]} · '
           f'game {game_sha[:12]} (+{len(REWRITES)} reescrituras) · {fecha}')
    commit = out(['git', 'commit-tree', tree, '-m', msg], env=env)
    out(['git', 'update-ref', 'refs/heads/pages', commit])
    listed = int(out(['git', 'ls-tree', '-r', '--name-only', 'refs/heads/pages']).count('\n')) + 1
    if listed != nfiles:
        sys.exit(f'✗ la rama pages tiene {listed} ficheros pero el sitio {nfiles}')
    print(f'  ✓ refs/heads/pages → {commit[:9]} ({nfiles} ficheros · commit huérfano — historia aplastada)')


def need_token():
    t = os.environ.get('GIT_TOKEN', '').strip()
    if not t:
        sys.exit('✗ GIT_TOKEN no está en el entorno. Sin escribirlo en fichero alguno: '
                 'GIT_TOKEN=... python3 scripts/deploy_pages.py --push ...')
    return t


def git_push(refspec, forzar=False):
    helper = "!f() { echo username=FranJavierDavila; echo password=$GIT_TOKEN; }; f"
    cmd = ['git', '-c', 'http.postBuffer=524288000',
           '-c', f'credential.helper={helper}', 'push', 'origin', refspec]
    if forzar:
        cmd.insert(cmd.index('push') + 1, '--force')
    sh(cmd)


def do_push():
    need_token()
    # r42 · --force DE SERIE (lección r41): cada deploy crea un COMMIT
    # HUÉRFANO (update-ref a un commit raíz), así que el push es SIEMPRE
    # non-fast-forward y antes se tenía que forzar a mano.
    git_push('refs/heads/pages:refs/heads/pages', forzar=True)
    remote = out(['git', 'ls-remote', 'origin', 'refs/heads/pages'])
    print(f'  ✓ rama pages en GitHub → {remote.split()[0][:9]}')
    print(f'    ACTIVA PAGES (una vez): Settings → Pages → Deploy from a branch → pages /(root) → Save')
    print(f'    URL: {PAGES_URL}')


def do_backup():
    need_token()
    git_push('main:proyecto')
    print('  ✓ respaldo anti-rollback al día: main → proyecto')


def do_release(version):
    import requests
    tok = need_token()
    H = {'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json'}
    zipver = version.replace('.', '').lower()
    zips = sorted(glob.glob(os.path.join(REPO, 'public', 'descargas', f'crazypp-v{zipver}-*.zip')))
    solo = os.path.join(REPO, 'public', 'descargas', SOLO_ZIP)
    if os.path.exists(solo):
        zips.append(solo)
    if len(zips) != 4:
        sys.exit(f'✗ esperaba 4 ZIPs en public/descargas, hay {len(zips)}: ' +
                 ', '.join(os.path.basename(z) for z in zips))
    tag = f'v{version}'
    sh(['git', 'tag', '-f', tag, 'HEAD'])
    # r112: el tag se re-crea FORZADO aquí arriba (tag -f), así que su push
    # también debe serlo — la re-release de la MISMA versión (r112 sobre
    # 3.6.209) rechazaba el push sin --force porque el tag ya existía.
    git_push(f'refs/tags/{tag}', forzar=True)
    body = (f'CRAZY PING PONG **{version}**\n\n'
            f'- **Jugar sin descargar**: {PAGES_URL} (ábrela en el navegador del visor)\n'
            f'- **ZIPs**: COMPLETO (todo, ~186 MB) · ligera (sin campeonatos, ~58 MB) · '
            f'CLOUDFLARE (estático puro, ~186 MB) · SOLO (servicio live, 6 KB)\n'
            f'- QA del release: cuádruple verde + smoke\n')
    api = f'https://api.github.com/repos/{OWNER_REPO}'
    r = requests.post(f'{api}/releases', headers=H, timeout=(15, 120), json={
        'tag_name': tag, 'name': f'CRAZY PING PONG {version}',
        'body': body, 'draft': False, 'prerelease': False})
    if r.status_code == 422:
        r = requests.get(f'{api}/releases/tags/{tag}', headers=H, timeout=(15, 60))
    r.raise_for_status()
    rel = r.json()
    rid = rel['id']
    have = {a['name']: a for a in requests.get(
        f'{api}/releases/{rid}/assets?per_page=100', headers=H, timeout=(15, 60)).json()}
    for zp in zips:
        name = os.path.basename(zp)
        size = os.path.getsize(zp)
        if have.get(name, {}).get('size') == size:
            print(f'  · asset {name} ya está (mismo tamaño) — omitido')
            continue
        # r112: asset con OTRO tamaño (re-release de la misma versión) — la API
        # rechaza nombres duplicados al subir, y el PAT fine-grained del dueño
        # NO puede borrar assets (404 en DELETE con Contents:write verificado
        # r112: PATCH 200 / DELETE 404). Estrategia SIN borrado: el viejo se
        # RENOMBRA con prefijo ANTIGUO- (queda a la vista, borrable a mano en
        # la UI) y el nuevo entra con su nombre canónico.
        if have.get(name, {}).get('size') == size:
            print(f'  · asset {name} ya está (mismo tamaño) — omitido')
            continue
        if name in have:
            rn = requests.patch(f'{api}/releases/assets/{have[name]["id"]}',
                                headers=H, timeout=(15, 60),
                                json={'name': 'ANTIGUO-' + name})
            rn.raise_for_status()
            print(f'  · asset viejo renombrado → ANTIGUO-{name}')
        print(f'  · subiendo {name} ({size/1e6:.1f} MB)…')
        with open(zp, 'rb') as fh:
            up = requests.post(f'https://uploads.github.com/repos/{OWNER_REPO}/releases/{rid}/assets?name={name}',
                               headers={**H, 'Content-Type': 'application/zip'},
                               data=fh.read(), timeout=(30, 1800))
        up.raise_for_status()
    print(f"  ✓ Release: {rel['html_url']}")


def main():
    flags = set(sys.argv[1:])
    unknown = flags - {'--push', '--release', '--backup', '--no-smoke'}
    if unknown:
        sys.exit(f'✗ flags desconocidos: {unknown}')
    if '--backup' in flags and '--push' not in flags:
        # r129 · lección propia: --backup empuja main→proyecto (respaldo
        # anti-rollback) pero NO publica la rama pages — sin --push el
        # sitio vivo no cambia y el deploy parece hecho sin haberse hecho.
        print('· aviso r129: --backup sin --push NO publica la rama pages\n'
              '  (el sitio vivo no cambia; añade --push para publicar).')
    ensure_excluded()
    head = out(['git', 'rev-parse', 'HEAD'])
    print(f'· ensamblando sitio desde HEAD {head[:9]} (git archive, solo trackeados)…')
    assemble()
    version = detect_version()
    print(f'· versión detectada: {version}')
    # r98 · VERIFICACIÓN DE SELLOS EN EL SITIO ENSAMBLADO: el sitio nace de
    # `git archive HEAD` (solo TRACKED) — en r97 el bump selló public/sw.js
    # en disco pero el commit SE OLVIDÓ DE ÉL y producción sirvió el sw.js
    # de 3.6.188: el SW del dueño nunca cambió, su caché nunca murió y el
    # juego viejo se sirvió 4 rondas («no cambió nada»). Si el sello del
    # sw.js o del game.html ensamblados no coincide con la versión detec-
    # tada, ABORTA antes de publicar nada.
    sw_sitio = os.path.join(SITE, 'sw.js')
    juego_sitio = os.path.join(SITE, 'game.html')
    sello_sw = f'crazypp-v{version}'
    with open(sw_sitio, encoding='utf-8') as f2:
        sw_txt = f2.read()
    with open(juego_sitio, encoding='utf-8') as f2:
        juego_txt = f2.read()
    if sello_sw not in sw_txt:
        sys.exit(f'✗ SELLO DEL SW DESALINEADO: el sw.js ensamblado (de git HEAD) '
                 f'no lleva {sello_sw!r} — ¿se olvidó `git add public/sw.js`? '
                 f'ABORTA: no publico un sitio que no puede actualizarse.')
    if version not in juego_txt:
        sys.exit(f'✗ SELLO DEL JUEGO DESALINEADO: el game.html ensamblado '
                 f'no lleva {version!r}.')
    if not os.path.exists(os.path.join(SITE, 'actualizar.html')):
        sys.exit('✗ FALTA public/actualizar.html en el sitio ensamblado '
                 '(¿se olvidó en SITE_PATHS o en el commit?)')
    print(f'· sellos verificados: sw.js {sello_sw} · game.html {version} · '
          'actualizar.html presente')
    apply_rewrites()
    game_sha = sha256(os.path.join(SITE, 'game.html'))
    write_extras(version, head, game_sha)
    nfiles = verify_site()
    if '--no-smoke' not in flags:
        print(f'· smoke Playwright bajo prefijo {PREFIX}/ (puerto {PORT}, 22 s)…')
        asyncio.run(smoke(version))
    commit_pages_branch(version, head, game_sha, nfiles)
    if '--push' in flags:
        do_push()
    if '--backup' in flags:
        do_backup()
    if '--release' in flags:
        do_release(version)
    print('· deploy terminado.')


if __name__ == '__main__':
    main()
