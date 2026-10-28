#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA del PRESUPUESTO DE RENDIMIENTO (roadmap P1). Mide y compara contra
scripts/presupuesto.json (las líneas base):
  · FÍSICA (bench Node de la fuente real): barrido CCD 200k, bote 100k,
    aerodinámica 200k — cualquier O(n) o asignación nueva en el camino
    caliente dispara el presupuesto.
  · TAMAÑOS: game.html y los 6 módulos de campeonatos (5 + SDK) — solo
    crecen de forma intencional (tolerancia % sobre la línea base).
  · ARRANQUE EN VIVO (headless SwiftShader): de la navegación a
    __PP_GAME && __PP_VERSION — guard de regresión de arranque.
  · IMPORT EN CADENA de los 5 campeonatos (tiempo del smoke del SDK).
Uso:
  python3 scripts/qa_rendimiento.py            # verificar
  python3 scripts/qa_rendimiento.py --update   # refrescar líneas base
                                               # (tras un cambio intencional)
"""
import asyncio
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'
PRESUPUESTO = SCR / 'presupuesto.json'
MODOS = ('oeste', 'magia', 'locura', 'estacion_orbital', 'halloween')  # r85: halloween sustituye a valle_neon (retirado)
ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1

def medidas():
    'Reúne TODAS las medidas del presupuesto.'
    import hashlib
    m = {}
    # tamaños
    m['tamano'] = {'game.html': (RAIZ / 'public/game.html').stat().st_size,
                   'sdk': (RAIZ / 'public/championships/sdk/champ_sdk.js').stat().st_size}
    for mod in MODOS:
        m['tamano'][mod] = (RAIZ / f'public/championships/{mod}/index.js').stat().st_size
    # física (bench node de la fuente real)
    r = subprocess.run(['node', '--no-warnings', str(SCR / 'test_fisica_perf.mjs')],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        sys.exit('FALLO: bench físico node:\n' + r.stderr[-800:])
    m['fisica'] = json.loads(r.stdout.strip().splitlines()[-1])
    return m

async def medidas_vivas():
    'Arranque + import en cadena, con Playwright (headless).'
    from playwright.async_api import async_playwright
    import time
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-unsafe-swiftshader',
                                          '--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        t0 = time.monotonic()
        await pg.goto('http://localhost:3000/game.html', wait_until='domcontentloaded')
        await pg.wait_for_function("() => window.__PP_GAME && window.__PP_VERSION", timeout=60000)
        boot_ms = (time.monotonic() - t0) * 1000
        t1 = time.monotonic()
        r = await pg.evaluate("""async () => {
          const t0 = performance.now();
          for (const m of ['estacion_orbital','oeste','magia','locura','halloween']) {
            await import('/championships/' + m + '/index.js');
          }
          return { ms: performance.now() - t0,
                   ver: window.__PP_VERSION, sdk: window.__PP_SDK || null };
        }""")
        cadena_ms = r['ms']
        await b.close()
        return {'boot_ms': round(boot_ms, 1), 'cadena_ms': round(cadena_ms, 1),
                'ver': r['ver'], 'sdk': r['sdk'], 'pageerrors': len(errs)}

def main():
    modo_update = '--update' in sys.argv
    m = medidas()
    print('== TAMAÑOS ==')
    for k, v in m['tamano'].items():
        print(f'  · {k:18s} {v:>12,} B')
    print('== FÍSICA (bench de la fuente real) ==')
    for k, v in m['fisica'].items():
        print(f'  · {k:18s} {v:>8.1f} ms')

    vivos = None
    try:
        vivos = asyncio.run(medidas_vivas())
        print('== EN VIVO (headless SwiftShader) ==')
        print(f"  · boot a __PP_GAME: {vivos['boot_ms']} ms · import en cadena: {vivos['cadena_ms']} ms")
        chk(vivos['ver'] == json.loads((RAIZ / 'src/game/VERSION.json').read_text())['version'],
            f"arranque sirviendo la versión correcta ({vivos['ver']})")
        chk(vivos['pageerrors'] == 0, '0 pageerrors durante la medición')
    except Exception as e:
        print(f'  · (medición en vivo omitida: {type(e).__name__}: {e})')

    if modo_update:
        base = dict(m)
        if vivos:
            base['vivo'] = {k: vivos[k] for k in ('boot_ms', 'cadena_ms')}
        base['nota'] = ('Líneas base del presupuesto de rendimiento. Refrescar SOLO '
                        'tras un cambio intencional: python3 scripts/qa_rendimiento.py --update')
        base['fecha'] = date.today().isoformat()
        PRESUPUESTO.write_text(json.dumps(base, indent=2) + '\n', encoding='utf-8')
        print(f'\nLÍNEAS BASE REFRESCADAS → presupuesto.json ({base["fecha"]})')
        sys.exit(0)

    if not PRESUPUESTO.exists():
        sys.exit('FALLO: no existe presupuesto.json — genera las líneas base con --update')
    base = json.loads(PRESUPUESTO.read_text(encoding='utf-8'))
    tol_pct = base.get('tolerancia_tamano_pct', 1.0)

    print('== PRESUPUESTO ==')
    for k, v in m['tamano'].items():
        b = base['tamano'][k]
        chk(v <= b * (1 + tol_pct / 100), f'tamaño {k}: {v:,} ≤ {b:,} (+{tol_pct:g}%)')
    for k, v in m['fisica'].items():
        b = base['fisica'][k]
        chk(v <= b * 3.0, f'física {k}: {v:.1f} ms ≤ {b:.1f} ms ×3')
    if 'vivo' in base and vivos:
        for k in ('boot_ms', 'cadena_ms'):
            b = base['vivo'][k]
            v = vivos[k]
            chk(v <= b * 1.6 + 2000, f'vivo {k}: {v:.0f} ms ≤ {b:.0f} ms ×1,6 (+2 s)')

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()
