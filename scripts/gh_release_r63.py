#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gh_release_r63.py — Release v3.6.154-SDK6 + alineación de main por API GitHub.

Contexto: el reciclaje del sandbox purgó /home/z/my-project/.git (padre del
worktree upload/) y upload/.git quedó como puntero roto — reconstruir el git
local para deploy_pages.py --release exigiría un clon completo (~300 MB) y
Playwright. Este script replica EXACTAMENTE el resultado de do_release()
(scripts/deploy_pages.py) por API: tag ligero en el commit fuente, release
con el mismo nombre/cuerpo y los 4 assets con dedup por tamaño. Además
alinea origin/main con el linaje vivo (proyecto).

Uso (GIT_TOKEN por entorno, nunca en ficheros — regla de la casa):
    GIT_TOKEN=... python3 scripts/gh_release_r63.py check
    GIT_TOKEN=... python3 scripts/gh_release_r63.py download
    GIT_TOKEN=... python3 scripts/gh_release_r63.py release
    GIT_TOKEN=... python3 scripts/gh_release_r63.py align
    GIT_TOKEN=... python3 scripts/gh_release_r63.py verify
"""
import json
import os
import sys
import urllib.request

REPO = 'FranJavierDavila/CrazyPP'
API = f'https://api.github.com/repos/{REPO}'
UPLOADS = f'https://uploads.github.com/repos/{REPO}/releases'
VERSION = '3.6.154-SDK6'
TAG = f'v{VERSION}'
ZIPVER = VERSION.replace('.', '').lower()          # 36154-sdk6
SOLO = 'crazypp-live-service-SOLO.zip'
DESC = '/home/z/my-project/download/descargas_r63'
LOCAL = '/home/z/my-project/upload/download'       # salida del build_zip.py
ZIP_NAMES = [f'crazypp-v{ZIPVER}-CLOUDFLARE.zip',
             f'crazypp-v{ZIPVER}-COMPLETO.zip',
             f'crazypp-v{ZIPVER}-ligera.zip',
             SOLO]
BODY = (f'CRAZY PING PONG **{VERSION}**\n\n'
        f'- **Jugar sin descargar**: https://franjavierdavila.github.io/CrazyPP/'
        f' (ábrela en el navegador del visor)\n'
        f'- **ZIPs**: COMPLETO (todo, ~186 MB) · ligera (~58 MB) · '
        f'CLOUDFLARE (~186 MB) · SOLO (servicio live, 6 KB)\n'
        f'- QA del release: cuádruple verde + smoke 39/0 en producción\n')


def req(url, method='GET', token=None, body=None, ctype='application/json',
        timeout=(15, 300)):
    to = timeout[1] if isinstance(timeout, tuple) else timeout  # urllib: nº entero
    headers = {'Accept': 'application/vnd.github+json',
               'User-Agent': 'crazypp-deploy'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = None
    if body is not None:
        data = body if isinstance(body, bytes) else \
            json.dumps(body).encode('utf-8')
        headers['Content-Type'] = ctype
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=to) as resp:
            raw = resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read()
        status = e.code
    try:
        return status, json.loads(raw) if raw else None
    except ValueError:
        return status, raw


def token():
    t = os.environ.get('GIT_TOKEN', '').strip()
    if not t:
        sys.exit('✗ GIT_TOKEN no está en el entorno (regla de la casa: por '
                 'entorno, nunca en ficheros)')
    return t


def download_file(url, dest, token):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    headers = {'User-Agent': 'crazypp-deploy'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    r = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(r, timeout=(30, 900)[1]) as resp, \
            open(dest, 'wb') as f:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    return os.path.getsize(dest)


def zips_from_listing(lst):
    """Los 4 ZIPs del release: 3 de versión + SOLO fijo (contrato do_release)."""
    ver = [x for x in lst if x['name'].startswith(f'crazypp-{ZIPVER}-')]
    solo = [x for x in lst if x['name'] == SOLO]
    return sorted(ver, key=lambda x: x['name']) + solo


def step_check(tok):
    st, rel = req(f'{API}/releases/latest', token=tok)
    if st == 200:
        print(f"· releases/latest: {rel['tag_name']} · {rel['name']} · "
              f"{rel['published_at']}")
    else:
        print(f'· releases/latest: HTTP {st}')
    st, tags = req(f'{API}/tags?per_page=5', token=tok)
    if st == 200:
        print('· últimos tags: ' + ', '.join(t['name'] for t in tags))
    st, lst = req(f'{API}/contents/public/descargas?ref=proyecto', token=tok)
    if st == 200 and isinstance(lst, list):
        print(f'· public/descargas en árbol proyecto: {len(lst)} ficheros')
        for x in zips_from_listing(lst):
            print(f"    - {x['name']} · {x['size']:,} B · "
                  f"download_url={'sí' if x.get('download_url') else 'NO'}")
        n = len(zips_from_listing(lst))
        print(f'  → ZIPs del release {TAG}: {n} (esperados 4)')
    else:
        print(f'· public/descargas NO está en el árbol (HTTP {st}) — '
              'habrá que buscar el builder')
    st, cmp_ = req(f'{API}/compare/main...proyecto', token=tok)
    if st == 200:
        print(f"· compare main...proyecto: status={cmp_['status']} · "
              f"ahead={cmp_['ahead_by']} behind={cmp_['behind_by']}")
    st, ref = req(f'{API}/git/ref/heads/proyecto', token=tok)
    if st == 200:
        sha = ref['object']['sha']
        print(f'· heads: proyecto={sha[:9]}')
        for br in ('main', 'pages'):
            st2, r2 = req(f'{API}/git/ref/heads/{br}', token=tok)
            if st2 == 200:
                print(f"          {br}={r2['object']['sha'][:9]}")
    st, tr = req(f'{API}/git/ref/tags/{TAG}', token=tok)
    print(f'· tag {TAG}: ' + (f'YA EXISTE en {tr["object"]["sha"][:9]}'
                               if st == 200 else f'no existe (HTTP {st})'))


def step_download(tok):
    st, lst = req(f'{API}/contents/public/descargas?ref=proyecto', token=tok)
    if st != 200 or not isinstance(lst, list):
        sys.exit(f'✗ public/descargas no accesible en el árbol (HTTP {st})')
    zips = zips_from_listing(lst)
    if len(zips) != 4:
        sys.exit(f'✗ esperaba 4 ZIPs en el árbol, hay {len(zips)}: ' +
                 ', '.join(x['name'] for x in zips))
    os.makedirs(DESC, exist_ok=True)
    for x in zips:
        dest = os.path.join(DESC, x['name'])
        if os.path.exists(dest) and os.path.getsize(dest) == x['size']:
            print(f"  · {x['name']} ya está (mismo tamaño) — omitido")
            continue
        url = x.get('download_url')
        if not url:
            sys.exit(f"✗ {x['name']} sin download_url (>100 MB vía API) — "
                     'hará falta el builder')
        print(f"  · descargando {x['name']} ({x['size']/1e6:.1f} MB)…")
        got = download_file(url, dest, tok)
        ok = got == x['size']
        print(f"    → {got:,} B · {'OK' if ok else 'TAMAÑO DIFIERE'}")
        if not ok:
            sys.exit(f'✗ descarga de {x["name"]} corrupta')
    print('✓ los 4 ZIPs están en ' + DESC)


def step_release(tok):
    zips = []
    for name in ZIP_NAMES:
        p = os.path.join(LOCAL, name)
        if not os.path.exists(p):
            sys.exit(f'✗ falta el ZIP local {p} — ejecuta build_zip.py antes')
        zips.append({'name': name, 'size': os.path.getsize(p), 'path': p})
    print('· ZIPs locales: ' + ', '.join(
        f"{z['name']} ({z['size']/1e6:.1f} MB)" for z in zips))
    st, ref = req(f'{API}/git/ref/heads/proyecto', token=tok)
    sha = ref['object']['sha']
    # 1) tag ligero en el commit fuente (do_release: git tag -f <tag> HEAD)
    st, tr = req(f'{API}/git/ref/tags/{TAG}', token=tok)
    if st == 200:
        print(f"· tag {TAG} ya existía en {tr['object']['sha'][:9]}")
        if tr['object']['sha'] != sha:
            print(f"  · re-apuntando a {sha[:9]} (git tag -f)…")
            st, _ = req(f'{API}/git/refs/tags/{TAG}', method='PATCH', token=tok,
                        body={'sha': sha, 'force': True})
            print(f'    → HTTP {st}')
    else:
        st, _ = req(f'{API}/git/refs', method='POST', token=tok,
                    body={'ref': f'refs/tags/{TAG}', 'sha': sha})
        if st in (200, 201):
            print(f'✓ tag {TAG} → {sha[:9]}')
        else:
            sys.exit(f'✗ creando el tag (HTTP {st})')
    # 2) release (mismo nombre y cuerpo que do_release)
    st, rel = req(f'{API}/releases', method='POST', token=tok, body={
        'tag_name': TAG, 'name': f'CRAZY PING PONG {VERSION}',
        'body': BODY, 'draft': False, 'prerelease': False})
    if st == 422:
        st, rel = req(f'{API}/releases/tags/{TAG}', token=tok)
    if st not in (200, 201):
        sys.exit(f'✗ creando el release (HTTP {st}): {rel}')
    rid = rel['id']
    print(f"✓ release #{rid}: {rel['html_url']}")
    # 3) assets con dedup por tamaño (contrato do_release)
    st, have = req(f'{API}/releases/{rid}/assets?per_page=100', token=tok)
    have = {a['name']: a['size'] for a in (have or [])}
    for x in zips:
        name, size = x['name'], x['size']
        if have.get(name) == size:
            print(f'  · asset {name} ya está (mismo tamaño) — omitido')
            continue
        path = x['path']
        if not os.path.exists(path) or os.path.getsize(path) != size:
            sys.exit(f'✗ el ZIP local {name} cambió de tamaño — re-lanza build_zip.py')
        print(f'  · subiendo {name} ({size/1e6:.1f} MB)…')
        with open(path, 'rb') as fh:
            data = fh.read()
        st2, _ = req(f'{UPLOADS}/{rid}/assets?name={name}', method='POST',
                     token=tok, body=data, ctype='application/zip',
                     timeout=(30, 1800))
        if st2 not in (200, 201):
            sys.exit(f'✗ subiendo {name} (HTTP {st2})')
        print(f'    → HTTP {st2} OK')
    print('✓ release completo con 4 assets')


def step_align(tok):
    st, cmp_ = req(f'{API}/compare/main...proyecto', token=tok)
    if st != 200:
        sys.exit(f'✗ compare HTTP {st}')
    status = cmp_['status']
    st, ref = req(f'{API}/git/ref/heads/proyecto', token=tok)
    sha = ref['object']['sha']
    if status == 'identical':
        print(f'· main ya apunta a {sha[:9]} — nada que hacer')
        return
    force = status == 'diverged'
    print(f"· status={status} (ahead={cmp_['ahead_by']} "
          f"behind={cmp_['behind_by']}) → PATCH main {'FORZADO' if force else 'fast-forward'} a {sha[:9]}")
    st, _ = req(f'{API}/git/refs/heads/main', method='PATCH', token=tok,
                body={'sha': sha, 'force': force})
    if st in (200, 201):
        print(f'✓ origin/main → {sha[:9]} (linaje vivo)')
    else:
        sys.exit(f'✗ PATCH main HTTP {st}')


def step_verify(tok):
    st, rel = req(f'{API}/releases/latest', token=tok)
    ok1 = st == 200 and rel['tag_name'] == TAG
    print(f"· releases/latest: {rel.get('tag_name')} → "
          f"{'OK' if ok1 else 'FALLO'}")
    st, assets = req(f"{API}/releases/{rel['id']}/assets?per_page=100",
                     token=tok)
    names = ', '.join(f"{a['name']} ({a['size']/1e6:.1f} MB)"
                      for a in (assets or []))
    print(f'· assets ({len(assets or [])}): {names}')
    for br in ('main', 'proyecto', 'pages'):
        st, r = req(f'{API}/git/ref/heads/{br}', token=tok)
        print(f"· {br} = {r['object']['sha'][:9]}")
    print('✓ verificación terminada')


if __name__ == '__main__':
    t = token()
    step = sys.argv[1] if len(sys.argv) > 1 else 'check'
    {'check': step_check, 'download': step_download,
     'release': step_release, 'align': step_align,
     'verify': step_verify}[step](t)
