#!/usr/bin/env python3
"""Sube un archivo a gofile.io (cuenta invitada) y verifica el md5.
Uso: python3 upload_gofile.py <archivo>"""
import sys, os, json, hashlib, re, subprocess, time

PATH = sys.argv[1] if len(sys.argv) > 1 else ''
if not PATH or not os.path.exists(PATH):
    sys.exit('archivo no encontrado: ' + PATH)

md5_local = hashlib.md5(open(PATH, 'rb').read()).hexdigest()
size_mb = os.path.getsize(PATH) / 1e6
print(f'archivo: {PATH} ({size_mb:.1f} MB) md5={md5_local}')

def api(method, url, **kw):
    import requests
    r = requests.request(method, url, timeout=180, **kw)
    return r

# 1) servidor disponible
try:
    r = api('GET', 'https://api.gofile.io/servers')
    js = r.json()
    server = js['data']['servers'][0]['name']
    print('servidor:', server)
except Exception as e:
    sys.exit('sin servidor gofile: ' + str(e))

# 2) subida
try:
    with open(PATH, 'rb') as f:
        r = api('POST', f'https://{server}.gofile.io/contents/uploadfile',
                files={'file': (os.path.basename(PATH), f)})
    js = r.json()
    print('respuesta:', json.dumps(js)[:400])
    d = js.get('data', {})
    page = d.get('downloadPage')
    md5 = d.get('md5') or (d.get('file') or {}).get('md5')
    fid = d.get('fileId') or (d.get('file') or {}).get('id')
    if page:
        print('DOWNLOAD_PAGE=' + page)
        print('FILE_ID=' + str(fid or ''))
        print('MD5_REMOTE=' + str(md5 or ''))
        print('MD5_OK=' + str(True) if (md5 and md5 == md5_local) else 'MD5_OK=False (remoto: %s)' % md5)
    else:
        sys.exit('sin downloadPage')
except Exception as e:
    sys.exit('fallo de subida: ' + str(e))
