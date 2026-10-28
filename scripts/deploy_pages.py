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

REPO = '/home/z/my-project'
SITE = os.path.join(REPO, 'pages-site')
OWNER_REPO = 'FranJavierDavila/CrazyPP'
PAGES_URL = 'https://franjavierdavila.github.io/CrazyPP/'
PREFIX = '/CrazyPP'
PORT = 3006
MAX_FILE = 100_000_000
SOLO_ZIP = 'crazypp-live-service-SOLO.zip'

SITE_PATHS = ['public/game.html', 'public/championships', 'public/assets',
              'public/vendor', 'public/tv.html', 'public/robots.txt', 'public/logo.svg',
              'public/ugc']   # r85: EL TALLER UGC (editor de etapas/campeonatos)

# (original, sustituto, ocurrencias esperadas) — cualquier desvío ABORTA el despliegue
REWRITES = [
    ('src="/vendor/socket.io.min.js"', 'src="vendor/socket.io.min.js"', 1),
    ('href="/tv.html"', 'href="tv.html"', 1),
]
SMOKE_ALLOW_404 = ('/favicon.ico',)      # petición automática del navegador
SMOKE_ALLOW_PREFIX = ('/socket.io',      # sondeo del cliente incluido en vendor/
                      '/api/')           # ronda 11: bajo 127.0.0.1 el juego enruta la telemetría al receptor LOCAL (que en el sitio estático no existe — en producción real va al Worker); el beacon de 5 s cae al vacío y se tolera


def sh(args, **kw):
    return subprocess.run(args, cwd=REPO, check=True, capture_output=True, text=True, **kw)


def out(args, **kw):
    return sh(args, **kw).stdout.strip()


def ensure_excluded():
    exc = os.path.join(REPO, '.git', 'info', 'exclude')
    with open(exc) as f:
        cur = f.read()
    if 'pages-site' not in cur:
        with open(exc, 'a') as f:
            f.write('\npages-site\n')


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
    open(path, 'w', encoding='utf-8').write(html)


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
  :root { color-scheme: dark; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { min-height:100vh; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    background:#07090f; color:#e8ecf4; display:flex; align-items:center; justify-content:center;
    background-image:
      radial-gradient(60rem 30rem at 15% 0%, rgba(255,122,24,.16), transparent 60%),
      radial-gradient(50rem 26rem at 90% 100%, rgba(34,211,238,.14), transparent 60%); }
  main { max-width:640px; padding:48px 24px; text-align:center; }
  .chip { display:inline-block; font-size:12px; letter-spacing:.12em; text-transform:uppercase;
    color:#9fb0c8; border:1px solid #2a3550; border-radius:999px; padding:6px 14px; margin-bottom:22px; }
  h1 { font-size:clamp(34px,7vw,58px); font-weight:900; line-height:1.02; letter-spacing:-.02em;
    background:linear-gradient(92deg,#ffb347 0%, #ff7a18 45%, #22d3ee 100%);
    -webkit-background-clip:text; background-clip:text; color:transparent; }
  .sub { color:#9fb0c8; margin:14px 0 34px; font-size:16px; }
  .jugar { display:inline-block; font-size:22px; font-weight:800; text-decoration:none; color:#0a0d14;
    background:linear-gradient(92deg,#ffb347,#ff7a18); padding:18px 58px; border-radius:16px;
    box-shadow:0 10px 40px rgba(255,122,24,.35); transition:transform .15s ease, box-shadow .15s ease; }
  .jugar:hover { transform:translateY(-2px); box-shadow:0 14px 48px rgba(255,122,24,.5); }
  .como { margin-top:42px; text-align:left; background:#0c1019; border:1px solid #1c2438;
    border-radius:14px; padding:22px 24px; }
  .como h2 { font-size:14px; text-transform:uppercase; letter-spacing:.1em; color:#8fa3c0; margin-bottom:12px; }
  .como ol { margin-left:20px; line-height:1.9; font-size:15px; }
  .nota { margin-top:10px; font-size:13px; color:#7e8ea8; }
  nav { margin-top:34px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }
  nav a { color:#bfe9ff; text-decoration:none; font-size:14px; border:1px solid #23405c;
    padding:9px 16px; border-radius:10px; background:#0b1220; }
  nav a:hover { border-color:#22d3ee; }
  footer { margin-top:40px; font-size:12px; color:#5c6a82; }
  footer code { color:#7e8ea8; }
</style></head>
<body><main>
  <p class="chip">V@@VERSION@@ · commit @@COMMIT@@ · QA verde</p>
  <h1>CRAZY PING&nbsp;PONG</h1>
  <p class="sub">Ping-pong de superpoderes para Meta&nbsp;Quest&nbsp;3 · WebXR</p>
  <a class="jugar" href="game.html">▶&nbsp; JUGAR</a>
  <section class="como">
    <h2>Cómo jugar en Meta Quest 3</h2>
    <ol>
      <li>Abre esta página en el <b>navegador del visor</b>.</li>
      <li>Pulsa <b>JUGAR</b> y colócate ante la mesa.</li>
      <li>Toca el botón <b>VR</b> que aparece en pantalla.</li>
    </ol>
    <p class="nota">También funciona en el navegador de escritorio (modo 2D).</p>
  </section>
  <nav>
    <a href="tv.html">📺 TV en vivo</a>
    <a href="https://github.com/@@REPO@@/releases" target="_blank" rel="noreferrer">⬇ Descargar ZIPs</a>
    <a href="https://github.com/@@REPO@@" target="_blank" rel="noreferrer">💻 Código</a>
  </nav>
  <footer>Desplegado desde la rama <code>pages</code> · @@FECHA@@ · game @@GAME12@@</footer>
</main></body></html>
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
    idx = os.path.join(REPO, '.git', 'pages-index')
    if os.path.exists(idx):
        os.remove(idx)
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    sh(['git', 'read-tree', '--empty'], env=env)
    for root, _dirs, fs in os.walk(SITE):
        for f in fs:
            ap = os.path.join(root, f)
            rel = os.path.relpath(ap, SITE).replace(os.sep, '/')
            blob = out(['git', 'hash-object', '-w', ap])
            out(['git', 'update-index', '--add', '--cacheinfo', f'100644,{blob},{rel}'], env=env)
    tree = out(['git', 'write-tree'], env=env)
    parent = None
    try:
        parent = out(['git', 'rev-parse', 'refs/heads/pages'])
    except subprocess.CalledProcessError:
        pass
    fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    msg = (f'deploy pages: {version} · fuente {head[:9]} · '
           f'game {game_sha[:12]} (+{len(REWRITES)} reescrituras) · {fecha}')
    args = ['git', 'commit-tree', tree] + (['-p', parent] if parent else []) + ['-m', msg]
    commit = out(args, env=env)
    out(['git', 'update-ref', 'refs/heads/pages', commit])
    listed = int(out(['git', 'ls-tree', '-r', '--name-only', 'refs/heads/pages']).count('\n')) + 1
    if listed != nfiles:
        sys.exit(f'✗ la rama pages tiene {listed} ficheros pero el sitio {nfiles}')
    print(f'  ✓ refs/heads/pages → {commit[:9]} ({nfiles} ficheros'
          f'{" · commit encadenado" if parent else " · primer deploy"})')


def need_token():
    t = os.environ.get('GIT_TOKEN', '').strip()
    if not t:
        sys.exit('✗ GIT_TOKEN no está en el entorno. Sin escribirlo en fichero alguno: '
                 'GIT_TOKEN=... python3 scripts/deploy_pages.py --push ...')
    return t


def git_push(refspec):
    helper = "!f() { echo username=FranJavierDavila; echo password=$GIT_TOKEN; }; f"
    sh(['git', '-c', 'http.postBuffer=524288000',
        '-c', f'credential.helper={helper}', 'push', 'origin', refspec])


def do_push():
    need_token()
    git_push('refs/heads/pages:refs/heads/pages')
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
    git_push(f'refs/tags/{tag}')
    body = (f'CRAZY PING PONG **{version}**\n\n'
            f'- **Jugar sin descargar**: {PAGES_URL} (ábrela en el navegador del visor)\n'
            f'- **ZIPs**: COMPLETO (todo, ~125 MB) · ligera (~11 MB) · CLOUDFLARE · '
            f'SOLO (servicio live, 6 KB)\n'
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
    have = {a['name']: a['size'] for a in requests.get(
        f'{api}/releases/{rid}/assets?per_page=100', headers=H, timeout=(15, 60)).json()}
    for zp in zips:
        name = os.path.basename(zp)
        size = os.path.getsize(zp)
        if have.get(name) == size:
            print(f'  · asset {name} ya está (mismo tamaño) — omitido')
            continue
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
    ensure_excluded()
    head = out(['git', 'rev-parse', 'HEAD'])
    print(f'· ensamblando sitio desde HEAD {head[:9]} (git archive, solo trackeados)…')
    assemble()
    version = detect_version()
    print(f'· versión detectada: {version}')
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
