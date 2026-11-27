#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F3b (auditoría r120 · ola 3 · r129) · PUERTA DE QA para el UGC de campeonatos.

Hoy los campeonatos son del dueño; el día que se publiquen módulos de
TERCEROS, el champloader los importa al mismo realm con el juego completo en
la mano (c11:246/261) — la seguridad se construye ANTES, en el repo:

  1 · MANIFEST — espejo en build de la validación runtime que r128/F3b
      añadió al champloader: campos required del championship.schema.json
      (id coherente con la carpeta, version ≥ 1, contract ≤ 1, title.es,
      description.es, rival{id,name,kind}, storage, assets).
  2 · CÓDIGO — auditoría estática de patrones prohibidos en los módulos
      (eval/new Function, document.cookie/write, serviceWorker, indexedDB,
      XMLHttpRequest, WebAssembly) y de CUALQUIER URL absoluta http(s) en
      fetch/import (exfiltración o código remoto; todo el UGC legítimo
      carga por URLs RELATIVAS — verificado en los 7 módulos + sdk).

El sandbox duro de terceros (iframe postMessage / Worker) exige el
contrato 2 del SDK — el champloader ya rechaza contract > 1 con aviso
visible, así que la migración puede ser gradual sin romper nada.

Salida estilo casa: '  ✓ …' / '  ✗ FALLO: …' + RESULTADO: N OK · M FALLOS.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
CHAMPS = RAIZ / 'public/championships'

REQ = ['id', 'version', 'contract', 'title', 'description', 'rival', 'storage', 'assets']
PROHIBIDOS = [
    (r'\beval\s*\(', 'eval()'),
    (r'\bnew\s+Function\b', 'new Function'),
    (r'document\.cookie', 'document.cookie'),
    (r'document\.write', 'document.write'),
    (r'navigator\.serviceWorker', 'navigator.serviceWorker'),
    (r'\bindexedDB\b', 'indexedDB'),
    (r'XMLHttpRequest', 'XMLHttpRequest'),
    (r'\bWebAssembly\b', 'WebAssembly'),
]
URL_ABS = re.compile(r'''(?:fetch|import)\s*\(\s*[`'"](?:https?:)?//''')

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print((cond and '  ✓ ' or '  ✗ FALLO: ') + label)
    ok += cond and 1 or 0
    fails += (not cond) and 1 or 0


def main():
    modulos = sorted(CHAMPS.glob('*/index.js'))
    sdk = CHAMPS / 'sdk/champ_sdk.js'

    for m in modulos:
        carpeta = m.parent.name
        mf = m.parent / 'manifest.json'
        # 1 · manifest contra el contrato obligatorio
        try:
            man = json.loads(mf.read_text(encoding='utf-8')) if mf.exists() else None
        except Exception as e:
            man = None
            chk(False, f'{carpeta}: manifest.json no parseable ({e})')
        if man is not None:
            faltan = [k for k in REQ if k not in man]
            chk(not faltan, f'{carpeta}: manifest con contrato completo ({faltan or "sin huecos"})')
            chk(man.get('id') == carpeta, f'{carpeta}: manifest.id == carpeta')
            chk(isinstance(man.get('version'), (int, float)) and man['version'] >= 1,
                f'{carpeta}: version ≥ 1 ({man.get("version")})')
            chk(isinstance(man.get('contract'), (int, float)) and man['contract'] <= 1,
                f'{carpeta}: contract ≤ 1 ({man.get("contract")})')
            t = man.get('title') or {}
            chk(isinstance(t, dict) and bool(t.get('es')), f'{carpeta}: title.es presente')
            d = man.get('description') or {}
            chk(isinstance(d, dict) and bool(d.get('es')), f'{carpeta}: description.es presente')
            r = man.get('rival') or {}
            chk(isinstance(r, dict) and r.get('id') and r.get('name') and r.get('kind'),
                f'{carpeta}: rival{{id,name,kind}} presente')
            chk(isinstance(man.get('storage'), str) and bool(man['storage']),
                f'{carpeta}: storage presente')
            chk(isinstance(man.get('assets'), str) and bool(man['assets']),
                f'{carpeta}: assets presente')
        else:
            chk(False, f'{carpeta}: manifest.json ausente')

        # 2 · código: patrones prohibidos + URLs absolutas en fetch/import
        try:
            codigo = m.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            chk(False, f'{carpeta}: index.js ilegible ({e})')
            continue
        for rx, nombre in PROHIBIDOS:
            hits = re.findall(rx, codigo)
            chk(not hits, f'{carpeta}: sin {nombre} ({len(hits)} apariciones)')
        absu = URL_ABS.findall(codigo)
        chk(not absu, f'{carpeta}: sin fetch/import con URL absoluta ({len(absu)})')

    if sdk.exists():
        codigo = sdk.read_text(encoding='utf-8', errors='replace')
        for rx, nombre in PROHIBIDOS:
            hits = re.findall(rx, codigo)
            chk(not hits, f'sdk: sin {nombre} ({len(hits)} apariciones)')
        absu = URL_ABS.findall(codigo)
        chk(not absu, f'sdk: sin fetch/import con URL absoluta ({len(absu)})')
    else:
        chk(False, 'sdk: champ_sdk.js ausente')

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
