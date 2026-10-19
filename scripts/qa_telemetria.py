#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · QA CAPA J · TELEMETRÍA (ronda 6, roadmap P1).
Verifica la cadena completa del anónimo __PP_TELE sin tocar el juego:
  A. Catálogo ↔ fuente        — los 8 eventos del catálogo son TODOS los que
                                emite el código (y viceversa); PII y hallazgos.
  B. Contrato del receptor    — POST wrapper/array/texto/json, saneo, OPTIONS,
                                GET resumen/eventos, DELETE, límites de tamaño.
  C. Juego → receptor (E2E)   — Playwright en :3000: boot llega, auto-flush al
                                llegar a 10, flush manual, error capturado,
                                FPS, pagehide → page_close y OPT-OUT hermético.
  D. Panel + PII + artefacto  — /telemetria en :3000 y :81, API por el gateway,
                                auditoría de claves (nada fuera del catálogo) y
                                el artefacto game.html lleva la telemetría.
Uso: python3 scripts/qa_telemetria.py   (requiere dev :3000 y gateway :81)
"""
import asyncio
import glob
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.async_api import async_playwright

RAIZ = Path('/home/z/my-project')
BASE = 'http://localhost:3000'
GW = 'http://localhost:81'
API = BASE + '/api/telemetria'
UA = ('Mozilla/5.0 (X11; Linuxx86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/131.0.0.0 Safari/537.36').replace('Linuxx86_64', 'Linux x86_64')
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def peticion(metodo, cuerpo=None, ctype='text/plain;charset=UTF-8', url=API):
    req = urllib.request.Request(url, method=metodo)
    req.add_header('User-Agent', UA)
    if cuerpo is not None:
        req.add_header('Content-Type', ctype)
        if isinstance(cuerpo, (dict, list)):
            cuerpo = json.dumps(cuerpo)
        req.data = cuerpo.encode('utf-8')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            crudo = r.read().decode('utf-8', 'replace')
            try:
                return r.status, json.loads(crudo) if crudo.startswith('{') or crudo.startswith('[') else crudo
            except json.JSONDecodeError:
                return r.status, crudo
    except urllib.error.HTTPError as e:
        crudo = (e.read() or b'').decode('utf-8', 'replace')
        try:
            return e.code, json.loads(crudo) if crudo.startswith('{') else crudo
        except json.JSONDecodeError:
            return e.code, crudo
    except Exception as e:
        return -1, str(e)


def get_json(url, timeout=30):
    st, cuerpo = peticion('GET', url=url)
    return st, (cuerpo if isinstance(cuerpo, (dict, list)) else {})


# ---------------------------------------------------------------- BLOQUE A
def bloque_catalogo():
    print('== A · CATÁLOGO ↔ FUENTE ==')
    cat = json.loads((RAIZ / 'scripts' / 'telemetria_catalogo.json').read_text(encoding='utf-8'))
    nombres_cat = {e['nombre'] for e in cat['eventos']}

    found = set()
    patrones = []
    for f in glob.glob(str(RAIZ / 'src/game/core/*.js')) + \
             glob.glob(str(RAIZ / 'public/championships/*/index.js')):
        txt = Path(f).read_text(encoding='utf-8', errors='replace')
        for m in re.finditer(r"__PP_TELE\.ev\('([a-zA-Z_0-9]+)'", txt):
            found.add(m.group(1))
            patrones.append((f, m.group(1)))
        # los 3 eventos DE CICLO DE VIDA se emiten DESDE DENTRO de la IIFE de
        # __PP_TELE con la función local ev() (sin prefijo): boot, page_close, error
        if f.endswith('c00_pre_three.js'):
            for m in re.finditer(r"(?<![\w.])ev\('([a-zA-Z_0-9]+)'", txt):
                found.add(m.group(1))
                patrones.append((f, m.group(1)))
        for m in re.finditer(r"e:\s*'([a-zA-Z_0-9]+)'", txt):
            if m.group(1) == 'champ_rank':
                found.add('champ_rank')
                patrones.append((f, 'champ_rank'))

    chk(len(nombres_cat) == 8, f'el catálogo documenta 8 eventos ({len(nombres_cat)})')
    chk(found == nombres_cat,
        f'todos los eventos del código están en el catálogo y viceversa '
        f'(fuente: {sorted(found)} / catálogo: {sorted(nombres_cat)})')

    fich = set()
    for e in cat['eventos']:
        origen = re.split(r'\s·\s|\s\(', e['origen'])[0]
        fich.add(origen)
    chk(all((RAIZ / f).exists() for f in fich),
        'los ficheros de origen del catálogo existen')
    chk(all(('campos' in e and 'origen' in e and 'momento' in e)
            for e in cat['eventos']), 'cada evento lleva origen, momento y campos')
    chk(cat['politica_pii']['sin_ip'] and cat['politica_pii']['sin_user_agent'],
        'política PII declarada: sin IP y sin user-agent')
    chk(len(cat['hallazgos_ronda6']) >= 3,
        f"hallazgos de la ronda 6 documentados ({len(cat['hallazgos_ronda6'])})")

    # el ARTEFACTO lleva la telemetría (sin cambiar su golden)
    juego = (RAIZ / 'public/game.html').read_text(encoding='utf-8', errors='replace')
    chk('window.__PP_TELE = __PP_TELE' in juego, 'game.html expone window.__PP_TELE')
    chk("window.PP_TELEMETRY_ENDPOINT = 'https://" in juego,
        'game.html lleva el endpoint del shell (04_boot)')
    return cat


# ---------------------------------------------------------------- BLOQUE B
def bloque_contrato():
    print('== B · CONTRATO DEL RECEPTOR (HTTP) ==')
    sb = 'qa-b'  # sid del bloque B (se purga al final)
    ev = lambda n, **kw: dict(e=n, t=int(time.time() * 1000), v='qa', sid=sb, **kw)

    st, j = peticion('POST', {'app': 'crazy-pingpong', 'events': [ev('qa_http1'), ev('qa_http2')]})
    chk(st == 200 and j.get('guardados') == 2,
        f'POST wrapper del juego (text/plain) aceptado → guardados {j.get("guardados", "?")}')
    st, j = peticion('POST', [ev('qa_http1')])
    chk(st == 200 and j.get('guardados') == 1,
        f'POST array directo aceptado (estilo champ_rank) → {j.get("guardados", "?")}')
    st, j = peticion('POST', [dict(e='champ_rank', champ='magia', win=True, score=123,
                                   stars=2, bricks=10, ext=0, left=12.5, v='2.81.0', sid=sb,
                                   t=int(time.time() * 1000))],
                     ctype='application/json')
    chk(st == 200 and j.get('guardados') == 1,
        f'POST application/json (champ_rank real de Magia) aceptado → {j.get("guardados", "?")}')
    st, _ = peticion('POST', 'esto no es json')
    chk(st == 400, f'POST basura rechazado ({st})')
    st, _ = peticion('POST', '[{"t":1}]')  # sin campo e
    chk(st == 200, 'POST evento sin «e» no rompe el lote (saneo selectivo)')
    st, j = get_json(API + '?resumen=1&sid=' + sb)
    chk(j.get('porEvento', {}).get('qa_http1') == 2 and j.get('porEvento', {}).get('qa_http2') == 1,
        'resumen ?sid filtra y agrega por evento correctamente')
    cr = j.get('champRank', {}).get('magia', {})
    chk(cr.get('partidas') == 1 and cr.get('victorias') == 1 and cr.get('mejor') == 123,
        'champ_rank agregado por campeonato (partidas/victorias/mejor)')

    grande = dict(ev('qa_grande'), m='x' * 2100)
    st, j = peticion('POST', [grande])
    chk(st == 200 and j.get('guardados') == 0,
        f'evento de {len(json.dumps(grande))} B (>2000) DESCARTADO del lote sin romperlo ' \
        f'(guardados {j.get("guardados", "?")})')
    cuerpo_grande = json.dumps([ev('qa_x', m='y' * 900)] * 300)
    st, _ = peticion('POST', cuerpo_grande)
    chk(st == 413, f'cuerpo >256 KB rechazado ({st})')

    req = urllib.request.Request(API, method='OPTIONS')
    req.add_header('User-Agent', UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        acao = r.headers.get('access-control-allow-origin')
    chk(r.status == 204 and acao == '*', 'OPTIONS preflight → 204 + ACAO *')

    st, j = get_json(API + '?eventos=2')
    chk(st == 200 and isinstance(j.get('eventos'), list) and len(j['eventos']) <= 2,
        f'GET ?eventos=2 devuelve ≤2 crudos ({len(j.get("eventos", []))})')
    st, j = get_json(API)
    chk(st == 200 and j.get('ok') is True and 'total' in j, 'GET latido → {ok, total, ts}')

    st, j = peticion('DELETE', url=API + '?sid=' + sb)
    chk(st == 200 and j.get('borrados') == 4,
        f'DELETE ?sid purga SOLO su ámbito → borrados {j.get("borrados", "?")}')
    st, j = get_json(API + '?resumen=1&sid=' + sb)
    chk(j.get('total') == 0, 'tras la purga el ámbito queda a 0 (los demás intactos)')


# ---------------------------------------------------------------- BLOQUE C
async def bloque_e2e():
    print('== C · JUEGO → RECEPTOR (E2E en vivo) ==')
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])

        # ---- sesión 1: telemetría ACTIVADA, endpoint fijado al receptor local
        ctx = await browser.new_context(viewport={'width': 1280, 'height': 800})
        # lock del endpoint: 04_boot.html asigna el worker DESPUÉS del init →
        # definimos la propiedad SIN setter para que el valor sobreviva.
        await ctx.add_init_script(
            "Object.defineProperty(window, 'PP_TELEMETRY_ENDPOINT',"
            "{ get() { return '/api/telemetria'; }, set() {}, configurable: true });")
        page = await ctx.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded')
        await page.wait_for_function("() => window.__PP_TELE", timeout=45000)
        sid = await page.evaluate("() => window.__PP_TELE.st.sid")
        chk(bool(sid), f'el juego expone __PP_TELE con sid aleatorio ({sid})')
        ep = await page.evaluate("() => window.PP_TELEMETRY_ENDPOINT")
        chk(ep == '/api/telemetria', f'endpoint fijado al receptor local pese a 04_boot ({ep})')

        async def cuenta(tipo=None):
            st, j = get_json(API + '?resumen=1&sid=' + str(sid))
            if tipo:
                return j.get('porEvento', {}).get(tipo, 0)
            return j.get('total', 0)

        # boot: encolado al evaluar el módulo, 1.er flush a los 5 s
        t0 = time.time()
        llego = False
        while time.time() - t0 < 20:
            if await cuenta('boot') >= 1:
                llego = True
                break
            await asyncio.sleep(0.5)
        chk(llego, f'el evento boot del juego llega al receptor ({time.time()-t0:.1f} s)')

        # auto-flush al llegar a 10 encolados (ev ×12 → ≥10 en el receptor)
        await page.evaluate(
            "() => { for (let i = 0; i < 12; i++) __PP_TELE.ev('qa_auto', { n: i }); }")
        t0 = time.time()
        n_auto = 0
        while time.time() - t0 < 10:
            n_auto = await cuenta('qa_auto')
            if n_auto >= 10:
                break
            await asyncio.sleep(0.5)
        chk(n_auto >= 10, f'auto-flush con cola ≥10 dispara el lote ({n_auto} eventos qa_auto)')

        # flush manual → los 12 (OJO anti-flake: el beacon es ASÍNCRONO — se
        # sondea con plazo en vez de medir justo tras el evaluate)
        sent0 = await page.evaluate("() => __PP_TELE.st.sent")
        await page.evaluate("() => __PP_TELE.flush(true)")
        t0 = time.time()
        n12 = 0
        while time.time() - t0 < 10:
            n12 = await cuenta('qa_auto')
            if n12 == 12:
                break
            await asyncio.sleep(0.5)
        chk(n12 == 12, f'flush(true) envía el resto → 12/12 ({n12})')
        sent1 = await page.evaluate("() => __PP_TELE.st.sent")
        chk(sent1 > sent0, f' diagnóstico st.sent incrementa ({sent0} → {sent1})')

        # error de página capturado (listener window error)
        # OJO anti-flake: el beacon es ASÍNCRONO → sondeo con plazo (igual que
        # el resto de llegadas; medir justo tras el evaluate es una lotería)
        await page.evaluate(
            "() => window.dispatchEvent(new ErrorEvent('error',"
            "{ message: 'qa_error_ctrl' }))")
        await page.evaluate("() => __PP_TELE.flush(true)")
        t0 = time.time()
        errs = []
        while time.time() - t0 < 10:
            st, j = get_json(API + '?resumen=1&sid=' + str(sid))
            errs = [m for m, _ in j.get('erroresTop', [])]
            if any('qa_error_ctrl' in m for m in errs):
                break
            await asyncio.sleep(0.5)
        chk(any('qa_error_ctrl' in m for m in errs),
            f'window error → evento error con su mensaje ({errs[:2]})')

        # muestreo de FPS barato (200 frames × 0,03 s → 33 fps)
        fps = await page.evaluate(
            "() => { for (let i = 0; i < 200; i++) __PP_TELE.noteFrame(0.03);"
            " const f = __PP_TELE.fpsAvg(); __PP_TELE.ev('qa_fps', { fps: f }); return f; }")
        await page.evaluate("() => __PP_TELE.flush(true)")
        chk(fps == 33, f'noteFrame/fpsAvg muestrea correctamente (200×0,03 s → {fps} fps)')
        t0 = time.time()
        n_fps = 0
        while time.time() - t0 < 10:
            n_fps = await cuenta('qa_fps')
            if n_fps >= 1:
                break
            await asyncio.sleep(0.5)
        chk(n_fps >= 1, f'el evento qa_fps con el FPS llega al receptor ({n_fps})')

        # pagehide → page_close + flush síncrono
        await page.evaluate("() => window.dispatchEvent(new Event('pagehide'))")
        t0 = time.time()
        n_pc = 0
        while time.time() - t0 < 8:
            n_pc = await cuenta('page_close')
            if n_pc >= 1:
                break
            await asyncio.sleep(0.5)
        chk(n_pc >= 1, f'pagehide → page_close con duración llega ({n_pc})')

        chk(len(errors) == 0, f'0 pageerrors en la sesión del juego ({len(errors)})')
        await ctx.close()

        # ---- sesión 2: OPT-OUT hermético (pp_tele='0' antes de cargar)
        ctx2 = await browser.new_context(viewport={'width': 1280, 'height': 800})
        await ctx2.add_init_script("try { localStorage.setItem('pp_tele', '0'); } catch {} ")
        await ctx2.add_init_script(
            "Object.defineProperty(window, 'PP_TELEMETRY_ENDPOINT',"
            "{ get() { return '/api/telemetria'; }, set() {}, configurable: true });")
        page2 = await ctx2.new_page()
        await page2.goto(BASE + '/game.html', wait_until='domcontentloaded')
        await page2.wait_for_function("() => window.__PP_TELE", timeout=45000)
        sid2 = await page2.evaluate("() => __PP_TELE.st.sid")
        on2 = await page2.evaluate("() => __PP_TELE.st.on")
        chk(on2 is False, 'con pp_tele=0 la telemetría arranca DESACTIVADA (st.on false)')
        q2 = await page2.evaluate(
            "() => { __PP_TELE.ev('qa_no', {}); __PP_TELE.flush(true);"
            " return __PP_TELE.st.q.length; }")
        chk(q2 == 0, 'con opt-out los eventos NO se encolan (st.q vacío)')
        await asyncio.sleep(6)  # margen por si algo escapara (1.er flush a 5 s)
        st, j = get_json(API + '?resumen=1&sid=' + str(sid2))
        chk(j.get('total', 0) == 0,
            f'el sid del opt-out NO tiene NINGÚN evento en el receptor ({j.get("total")})')
        await ctx2.close()
        await browser.close()

        # (la purga del sid del E2E ocurre tras la auditoría PII, en el bloque D)
        return sid


# ---------------------------------------------------------------- BLOQUE D
def bloque_panel(sid_e2e):
    print('== D · PANEL, PII Y GATEWAY ==')
    st, cuerpo = peticion('GET', url=BASE + '/telemetria')
    chk(st == 200 and 'Telemetría anónima' in cuerpo,
        f'panel /telemetria en :3000 → {st} con su cabecera')
    st, j = get_json(GW + '/api/telemetria')
    chk(st == 200 and j.get('ok') is True, 'API de telemetría alcanzable por el gateway :81')
    st, cuerpo = peticion('GET', url=GW + '/telemetria')
    chk(st == 200 and 'Telemetría anónima' in cuerpo, 'panel /telemetria por el gateway :81')

    # PII: todo lo recibido del E2E respeta el catálogo (claves permitidas)
    cat = json.loads((RAIZ / 'scripts' / 'telemetria_catalogo.json').read_text(encoding='utf-8'))
    campos = {e['nombre']: {c['nombre'] for c in e['campos']} for e in cat['eventos']}
    base = {'e', 't', 'v', 'sid', '_rec'}
    st, j = get_json(API + '?eventos=500&sid=' + str(sid_e2e))
    malos = []
    for e in j.get('eventos', []):
        n = e.get('e', '?')
        permitidos = base | (campos.get(n, set()) if n in campos else set())
        if n.startswith('qa_'):
            permitidos |= {'n', 'fps'}
        extra = {k for k in e.keys() if k not in permitidos}
        if extra:
            malos.append((n, sorted(extra)))
    chk(not malos, f'auditoría PII: todas las claves del E2E están en el catálogo ({malos[:3]})')
    prohibidas = {'ip', 'ua', 'useragent', 'user_agent', 'referer'}
    con_prohibida = [e.get('e') for e in j.get('eventos', [])
                     if prohibidas & {k.lower() for k in e.keys()}]
    chk(not con_prohibida, 'ningún evento lleva IP/UA/referer')

    # limpieza AL FINAL (la auditoría PII necesita los eventos del E2E vivos)
    peticion('DELETE', url=API + '?sid=' + str(sid_e2e))


async def main():
    print('QA TELEMETRÍA · ronda 6 (roadmap P1) · juego intacto')
    cat = bloque_catalogo()
    bloque_contrato()
    sid = await bloque_e2e()
    bloque_panel(sid)
    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
