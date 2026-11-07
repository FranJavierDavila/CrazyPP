#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deriva los QA de la V3.6.3-SDK3 (FASE 5: createMusic):
  · qa_sup1_v362.py  → qa_sup1_v363.py (versión + SDK v1.2.0 + sección nueva
    FASE 5 «la música en el SDK»; la entrada v3.6.1-SDK1 del orbital NO se
    toca — el manifest del orbital no cambia en esta fase)
  · qa_imp2_v351.py / qa_escudo_v350.py → parche de versión in situ
  · qa_descargas_v363.py → nuevo (tamaños reales de los 4 ZIPs)
Cada reemplazo se cuenta y se aserta: si el origen cambia, el derivador FALLA."""
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

def reemplazar(s, viejo, nuevo, esperado, etiqueta):
    n = s.count(viejo)
    assert n == esperado, f'{etiqueta}: {viejo!r} aparece {n} veces (esperado {esperado})'
    return s.replace(viejo, nuevo)

# ── 1. qa_sup1_v363.py ───────────────────────────────────────────
s = (SCR / 'qa_sup1_v362.py').read_text(encoding='utf-8')
s = reemplazar(s, "QA del JUEGO · V3.6.2-SDK2", "QA del JUEGO · V3.6.3-SDK3", 1, 'uso/doc')
# sección FASE 4 → FASE 5 (la música en el SDK)
FASE4 = """        print('== FASE 4: los 4 campeonatos adoptantes ==')
        for mod, vman in (('oeste', 49), ('magia', 29), ('locura', 21),
                          ('valle_neon', 2)):
            srcm = await page.evaluate(
                f"fetch('championships/{mod}/index.js').then(r=>r.text())")
            chk("from '../sdk/champ_sdk.js'" in srcm, f'{mod}: importa el SDK')
            chk('freezeT = Math.max' not in srcm, f'{mod}: sin freeze duplicado')
            manm = await page.evaluate(
                f"fetch('championships/{mod}/manifest.json').then(r=>r.json())")
            chk(manm.get('version') == vman, f'{mod}: manifest v{vman}')
            chk(any('v3.6.2-SDK2' in n for n in manm.get('notes', [])),
                f'{mod}: nota SDK2 en el historial')"""
FASE5 = """        print('== FASE 5: la música en el SDK (createMusic) ==')
        for mod, vman in (('oeste', 50), ('magia', 30), ('valle_neon', 3)):
            srcm = await page.evaluate(
                f"fetch('championships/{mod}/index.js').then(r=>r.text())")
            chk("from '../sdk/champ_sdk.js'" in srcm, f'{mod}: importa el SDK')
            chk('get _musSDK()' in srcm, f'{mod}: la música delega en createMusic')
            chk('decodeAudioData(' not in srcm, f'{mod}: sin decodeAudioData propio')
            chk('freezeT = Math.max' not in srcm, f'{mod}: sin freeze duplicado')
            manm = await page.evaluate(
                f"fetch('championships/{mod}/manifest.json').then(r=>r.json())")
            chk(manm.get('version') == vman, f'{mod}: manifest v{vman}')
            chk(any('v3.6.3-SDK3' in n for n in manm.get('notes', [])),
                f'{mod}: nota SDK3 en el historial')
        locura = await page.evaluate(
            "fetch('championships/locura/index.js').then(r=>r.text())")
        chk('congela(g,' in locura and 'freezeT = Math.max' not in locura,
            'locura (sin cambios en FASE 5): congela del SDK, sin freeze propio')
        chk('decodeAudioData(' not in locura, 'locura: sin decodeAudioData propio')"""
s = reemplazar(s, FASE4, FASE5, 1, 'sección FASE 4 → FASE 5')
# gotos endurecidos: networkidle queda a merced de peticiones externas
# colgadas (CDN/telemetría); esperar el SELLO __PP_VERSION es más fuerte
# (el módulo entero —three del CDN incluido— ejecutó) e inmune a eso.
s = reemplazar(s, "        await page.goto(BASE + '/game.html', wait_until='networkidle')\n"
                  "        ver = await page.evaluate(\"window.__PP_VERSION || ''\")",
               "        await page.goto(BASE + '/game.html', wait_until='domcontentloaded')\n"
               "        # QA más dura que networkidle: el juego debe ARRANCAR (el sello\n"
               "        # de versión solo existe si el módulo entero ejecutó) y no le\n"
               "        # afecta una petición colgada del arranque.\n"
               "        await page.wait_for_function(\"() => window.__PP_GAME && window.__PP_VERSION\", timeout=45000)\n"
               "        ver = await page.evaluate(\"window.__PP_VERSION || ''\")",
               1, 'goto dev endurecido')
s = reemplazar(s, "        await pg2.goto(GW + '/game.html', wait_until='networkidle')",
               "        await pg2.goto(GW + '/game.html', wait_until='domcontentloaded')\n"
               "        await pg2.wait_for_function(\"() => window.__PP_GAME && window.__PP_VERSION\", timeout=45000)",
               1, 'goto gateway endurecido')
# tokens del SDK (tupla de la sección SDK del fuente servido)
s = reemplazar(s, "                   'function precarga', 'opts && opts.pan'):",
               "                   'function precarga', 'opts && opts.pan',\n"
               "                   'export function createMusic',\n"
               "                   'o.gateStart !== false && arcPlaying()'):",
               1, 'tokens SDK 1.2.0')
s = reemplazar(s, "\"const SDK_VERSION = '1.1.0'\"", "\"const SDK_VERSION = '1.2.0'\"", 1, 'SDK versión fuente')
s = reemplazar(s, "== '1.1.0',", "== '1.2.0',", 1, 'check runtime __PP_SDK (valor)')
s = reemplazar(s, "'window.__PP_SDK = 1.1.0", "'window.__PP_SDK = 1.2.0", 1, 'check runtime __PP_SDK (etiqueta)')
# el resto de menciones de versión (ver + badge + gateway ×2) suben juntas
s = reemplazar(s, '3.6.2-SDK2', '3.6.3-SDK3', 4, 'menciones de versión restantes')
# la única entrada histórica que queda es la del orbital (v3.6.1-SDK1)
assert s.count('3.6.1-SDK1') == 2, s.count('3.6.1-SDK1')
assert s.count('3.6.2-SDK2') == 0, s.count('3.6.2-SDK2')
(SCR / 'qa_sup1_v363.py').write_text(s, encoding='utf-8')
print('· qa_sup1_v363.py derivado (SDK 1.2.0 + sección FASE 5, orbital v14 intacto)')

# ── 2. qa_imp2_v351.py (parche de versión in situ) ───────────────
p = SCR / 'qa_imp2_v351.py'
s = p.read_text(encoding='utf-8')
if '3.6.2-SDK2' in s:
    n = s.count('3.6.2-SDK2')
    s = reemplazar(s, '3.6.2-SDK2', '3.6.3-SDK3', n, 'imp2 versión')
    p.write_text(s, encoding='utf-8')
    print(f'· qa_imp2_v351.py → 3.6.3-SDK3 ({n} menciones)')
else:
    assert '3.6.3-SDK3' in s, 'imp2 sin versión conocida'
    print('· qa_imp2_v351.py ya estaba en 3.6.3-SDK3')

# ── 3. qa_escudo_v350.py (parche de versión in situ) ─────────────
p = SCR / 'qa_escudo_v350.py'
s = p.read_text(encoding='utf-8')
if '3.6.2-SDK2' in s:
    n = s.count('3.6.2-SDK2')
    s = reemplazar(s, '3.6.2-SDK2', '3.6.3-SDK3', n, 'escudo versión')
    p.write_text(s, encoding='utf-8')
    print(f'· qa_escudo_v350.py → 3.6.3-SDK3 ({n} menciones)')
else:
    assert '3.6.3-SDK3' in s, 'escudo sin versión conocida'
    print('· qa_escudo_v350.py ya estaba en 3.6.3-SDK3')

# ── 4. qa_descargas_v363.py (nuevo) ──────────────────────────────
QA = '''#!/usr/bin/env python3
"""QA del HUB /descargas · V3.6.3-SDK3 (FASE 5: la música en el SDK).
Uso: python3 scripts/qa_descargas_v363.py"""
import asyncio
import sys
import zipfile

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'
GW = 'http://localhost:81'
ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1

ZIPS = {
    'crazypp-v363-sdk3-COMPLETO.zip': 125216557,
    'crazypp-v363-sdk3-ligera.zip': 11454675,
    'crazypp-v363-sdk3-CLOUDFLARE.zip': 125203941,
    'crazypp-live-service-SOLO.zip': 6089,
}

ADOPTANTES = (('oeste', 50, 'v3.6.3-SDK3'), ('magia', 30, 'v3.6.3-SDK3'),
              ('locura', 21, 'v3.6.2-SDK2'), ('valle_neon', 3, 'v3.6.3-SDK3'))

async def tam(base, nombre):
    r = await RC.head(base + '/descargas/' + nombre)
    return int(r.headers.get('content-length') or -1)

async def main():
    global A, RC
    async with async_playwright() as p:
        RC = await p.request.new_context()
        A = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await A.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))

        print('== HUB /descargas (dev :3000) ==')
        await page.goto(BASE + '/descargas', wait_until='networkidle')
        html = await page.content()
        chk(html.count('v363-sdk3') >= 3, f'enlaces v363-sdk3 ({html.count("v363-sdk3")})')
        chk(html.count('3.6.3-SDK3') >= 5, f'menciones 3.6.3-SDK3 ({html.count("3.6.3-SDK3")})')
        for kw in ('createMusic', 'SDK de campeonatos', 'FASE 5', 'FASE 4', 'una sola fuente',
                   'SUPERPODERES REDEFINIDOS', 'congela la partida', 'rocas en 3D',
                   'vetas de óxido', 'rayo tractor', 'dron', 'ATRAPADA',
                   'caída vertical', 'gravedad cero', 'partículas blancas',
                   'risa', 'enfado', 'ASTRO', 'diana se ve 2 segundos',
                   'siempre vuelve a botar', 'REACTOR DE IMPULSO',
                   'ESCUDO DE PALA', 'etapa 4', 'PRECISIÓN CCD'):
            chk(kw in html, f'el hub menciona {kw!r}')
        for viejo in ('v310-srv2', 'v312-ccd1', 'v320-orb1', 'v321-orb2',
                      'v330-nuc1', 'v340-imp1', 'v341-riv1', 'v350-esc1',
                      'v351-imp2', 'v360-sup1', 'v361-sdk1', 'v362-sdk2',
                      '3.1.0-SRV2', '3.2.0-ORB1', '3.2.1-ORB2', '3.3.0-NUC1',
                      '3.4.0-IMP1', '3.4.1-RIV1', '3.5.0-ESC1', '3.5.1-IMP2',
                      '3.6.0-SUP1', '3.6.1-SDK1', '3.6.2-SDK2'):
            chk(viejo not in html, f'sin residuos de {viejo}')
        botones = await page.locator('a[download]').count()
        chk(botones == 4, f'4 botones de descarga ({botones})')

        print('== ZIPs byte-exactos vía dev (:3000) ==')
        for n, esperado in ZIPS.items():
            t = await tam(BASE, n)
            chk(t == esperado, f'{n} = {t:,} B (esperado {esperado:,})')

        print('== ZIPs byte-exactos vía gateway (:81) ==')
        for n, esperado in ZIPS.items():
            t = await tam(GW, n)
            chk(t == esperado, f'{n} = {t:,} B vía gateway')

        print('== El SDK y los 4 campeonatos viajan dentro del COMPLETO ==')
        with zipfile.ZipFile('/home/z/my-project/public/descargas/crazypp-v363-sdk3-COMPLETO.zip') as z:
            nombres = z.namelist()
            chk('championships/sdk/champ_sdk.js' in nombres,
                'COMPLETO incluye championships/sdk/champ_sdk.js')
            if 'championships/sdk/champ_sdk.js' in nombres:
                sdkzip = z.read('championships/sdk/champ_sdk.js').decode('utf-8')
                chk("const SDK_VERSION = '1.2.0'" in sdkzip
                    and 'function precarga' in sdkzip
                    and 'export function createMusic' in sdkzip,
                    'SDK dentro del ZIP = v1.2.0 (con createMusic)')
            chk('championships/estacion_orbital/index.js' in nombres,
                'COMPLETO incluye el orbital (adoptante SDK1)')
            for mod, vman, nota in ADOPTANTES:
                dentro = f'championships/{mod}/index.js' in nombres
                chk(dentro, f'COMPLETO incluye championships/{mod}/index.js')
                if dentro:
                    srcm = z.read(f'championships/{mod}/index.js').decode('utf-8')
                    chk("from '../sdk/champ_sdk.js'" in srcm, f'{mod} (ZIP): importa el SDK')
                    chk('freezeT = Math.max' not in srcm, f'{mod} (ZIP): sin freeze duplicado')
                    chk('decodeAudioData(' not in srcm,
                        f'{mod} (ZIP): sin decodeAudioData propio (vive en el SDK)')
                manz = z.read(f'championships/{mod}/manifest.json').decode('utf-8')
                import json as _json
                chk(_json.loads(manz).get('version') == vman, f'{mod} (ZIP): manifest v{vman}')
        with zipfile.ZipFile('/home/z/my-project/public/descargas/crazypp-v363-sdk3-CLOUDFLARE.zip') as z:
            chk('championships/sdk/champ_sdk.js' in z.namelist(),
                'CLOUDFLARE incluye el SDK')
        with zipfile.ZipFile('/home/z/my-project/public/descargas/crazypp-v363-sdk3-ligera.zip') as z:
            con_champ = [n for n in z.namelist()
                         if n.startswith('championships/') and n != 'championships/'
                         and 'PON-AQUI' not in n]
            chk(not con_champ,
                f'ligera sin campeonatos (solo el marcador de la casa) {con_champ[:2]}')

        print('== Juego + SDK servidos por gateway ==')
        r = await RC.get(GW + '/game.html')
        cuerpo = await r.text()
        chk("const VERSION = '3.6.3-SDK3'" in cuerpo, 'gateway: game.html = 3.6.3-SDK3')
        chk('__PP_PADDLE_SWEEP' in cuerpo, 'gateway: puente CCD del núcleo')
        sdk = await (await RC.get(GW + '/championships/sdk/champ_sdk.js')).text()
        chk("const SDK_VERSION = '1.2.0'" in sdk and 'export function createSfx' in sdk
            and 'function precarga' in sdk and 'export function createMusic' in sdk,
            'gateway: champ_sdk.js v1.2.0 servido (SFX + música)')
        mod = await (await RC.get(GW + '/championships/estacion_orbital/index.js')).text()
        chk("from '../sdk/champ_sdk.js'" in mod and 'createSfx(import.meta.url' in mod,
            'gateway: orbital importa el SDK')
        chk('class EscudoCasco' in mod and "id: 'escudo'" in mod,
            'gateway: módulo sirve el ESCUDO DE PALA (etapa 4)')
        chk("{ kind: 'prueba', id: 'impulso', name: 'Reactor de impulso' }" in mod,
            'gateway: impulso en la etapa 2')
        chk('function _geoMeteorito' in mod and 'dronTractor' in mod,
            'gateway: meteoritos 3D + dron del tractor')
        chk('_tractorTrap' in mod and 'caída vertical pura' in mod,
            'gateway: bola atrapada + caída vertical')
        chk('const ATT = 7.5' in mod, 'gateway: gravedad cero atrae la bola')
        chk("this._sfx('risa_astro.mp3')" in mod and "this._sfx('enfado_astro.mp3')" in mod,
            'gateway: audios del ASTRO cableados')
        chk('congela(this.game, (def.warn || 2.0) + 0.15)' in mod,
            'gateway: freeze del aviso vía congela() del SDK')
        chk('this.game.freezeT = Math.max' not in mod,
            'gateway: sin el freeze duplicado (una sola fuente)')
        chk('dianaVis: 2.0' in mod, 'gateway: diana visible 2 s')
        chk('this._restT > 0.6' in mod, 'gateway: reposo → la pelota vuelve a la base')
        chk("(D.tableCenterZ || -1.6) - 1.70" in mod, 'gateway: ASTRO a distancia fija (z −3,30)')
        chk('(D.tableCenterZ || -1.6) - 2.22' not in mod, 'gateway: sin el spot antiguo (z −3,82)')
        man = await (await RC.get(GW + '/championships/estacion_orbital/manifest.json')).json()
        chk(man.get('version') == 14, 'gateway: manifest v14 (orbital intacto en SDK3)')
        chk([st['id'] for st in man['stages']] == ['duelo1', 'impulso', 'duelo2', 'escudo', 'final'],
            'gateway: camino del manifest = duelo1·impulso·duelo2·escudo·final')
        chk(any('v3.6.1-SDK1' in c for c in man.get('cambios', [])),
            'gateway: cambios incluye la entrada v3.6.1-SDK1 (historial)')

        print('== FASE 5: la música viaja en el SDK (por gateway) ==')
        TOKENS = {
            'oeste': ("import { createSfx, createMusic, congela, getCore } from '../sdk/champ_sdk.js'",
                      '__sfxSDK', "precarga('risas_forajido.mp3')",
                      "eng.play('risas.mp3', vol || 0.8, { pan: 0.4 })",
                      'congela(g, DUELO_P.drawT + DUELO_P.window + 0.35)',
                      'congela(g, 0.10)',
                      'congela(g, Math.max(this.powerSign.T_OUT, OESTE_POWER.warn) + 0.1)',
                      'const __CORE = getCore() || {}',
                      'get _musSDK()', "puede: () => this._stageMode !== 'tren'",
                      'get _musSDKv()', "syncMode: 'direct'",
                      'excluso: () => this.ctrl._musSDK.sonando()',
                      '_musicStart() { this._musSDKv.on(); }',
                      '_musicStop() { this._musSDKv.off(); }'),
            'magia': ("import { createSfx, createMusic, congela, getCore } from '../sdk/champ_sdk.js'",
                      '__sfxSDK', "precarga('risas.mp3')", "eng.play('risas.mp3', 1.0)",
                      'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                      'const __CORE = getCore() || {}',
                      'get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
                      'this._musSDK.sync();'),
            'valle_neon': ("import { createMusic, getCore } from '../sdk/champ_sdk.js'",
                           'const CORE = getCore();',
                           'get _musSDK()', 'fadeIn: 1.2', 'ancla: false',
                           "syncMode: 'none'", 'gateOn: true', 'stopFade: 0.4'),
            'locura': ("import { congela, getCore } from '../sdk/champ_sdk.js'",
                       'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                       'const __CORE = getCore() || {}'),
        }
        for mod, vman, nota in ADOPTANTES:
            srcm = await (await RC.get(GW + f'/championships/{mod}/index.js')).text()
            for tk in TOKENS[mod]:
                chk(tk in srcm, f'gateway {mod}: {tk[:58]}')
            chk('freezeT = Math.max' not in srcm, f'gateway {mod}: sin freeze duplicado')
            chk(srcm.count('decodeAudioData(') == 0,
                f'gateway {mod}: decodeAudioData solo en el SDK (0 en el módulo)')
            manm = await (await RC.get(GW + f'/championships/{mod}/manifest.json')).json()
            chk(manm.get('version') == vman, f'gateway {mod}: manifest v{vman}')
            chk(any(nota in n for n in manm.get('notes', [])),
                f'gateway {mod}: nota {nota} en el historial')

        intro = await RC.head(GW + '/assets/intro.mp4')
        chk(int(intro.headers.get('content-length') or -1) == 5779719,
            'intro oficial byte-perfecta por gateway')
        for f, esperado in (('risa_astro.mp3', 81408), ('enfado_astro.mp3', 37616)):
            m = await RC.head(GW + '/championships/estacion_orbital/assets/' + f)
            chk(int(m.headers.get('content-length') or -1) == esperado,
                f'gateway: {f} byte-exacto ({esperado} B)')
        diana = await RC.head(GW + '/championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png')
        chk(int(diana.headers.get('content-length') or -1) == 409356,
            'gateway: diana_quantica.png byte-exacta')

        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_sdk3_descargas_hub.png')
        await A.close()
        await RC.dispose()

    print(f'\\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
'''
(SCR / 'qa_descargas_v363.py').write_text(QA, encoding='utf-8')
print('· qa_descargas_v363.py escrito (4 ZIPs + SDK 1.2.0 + música en el SDK)')

print('\\nQA v363 listos.')
