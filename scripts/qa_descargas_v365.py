#!/usr/bin/env python3
"""QA del HUB /descargas · V3.6.48-SDK6 (FASE 8: telemetría reparada).
Uso: python3 scripts/qa_descargas_v365.py"""
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
    'crazypp-v3648-sdk6-COMPLETO.zip': 131178477,  # FASE 10: id en stage/champion + champ_rank por __PP_TELE
    'crazypp-v3648-sdk6-ligera.zip': 16128890,
    'crazypp-v3648-sdk6-CLOUDFLARE.zip': 131165090,  # FASE 10: game.html al día
    'crazypp-live-service-SOLO.zip': 6089,
}

ADOPTANTES = (('oeste', 56, 'v3.6.4-SDK4'), ('magia', 32, 'v3.6.4-SDK4'),
              ('locura', 26, 'v3.6.4-SDK4'), ('valle_neon', 4, 'v3.6.5-SDK5'))

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
        await page.goto(BASE + '/descargas', wait_until='domcontentloaded')
        await page.wait_for_load_state('load')
        html = await page.content()
        chk(html.count('v3648-sdk6') >= 3, f'enlaces v3648-sdk6 ({html.count("v3648-sdk6")})')
        chk(html.count('3.6.48-SDK6') >= 5, f'menciones 3.6.48-SDK6 ({html.count("3.6.48-SDK6")})')
        for kw in ('createRival', 'createCartel', 'FASE 8', 'telemetría', 'array directo',
                   'FASE 7', 'SDK v1.x',
                   'decodeAudioData propio', 'rival_kraken.png',
                   'createPowerSign', 'createMusic', 'SDK de campeonatos',
                   'FASE 6', 'FASE 5', 'FASE 4', 'una sola fuente',
                   'SUPERPODERES REDEFINIDOS', 'congela la partida', 'rocas en 3D',
                   'vetas de óxido', 'rayo tractor', 'dron', 'ATRAPADA',
                   'caída vertical', 'gravedad cero', 'partículas blancas',
                   'risa', 'enfado', 'ASTRO', 'diana se ve 2 segundos',
                   'siempre vuelve a botar', 'REACTOR DE IMPULSO',
                   'ESCUDO DE PALA', 'etapa 4', 'PRECISIÓN CCD'):
            chk(kw in html, f'el hub menciona {kw!r}')
        for viejo in ('v310-srv2', 'v312-ccd1', 'v320-orb1', 'v321-orb2',
                      'v330-nuc1', 'v340-imp1', 'v341-riv1', 'v350-esc1',
                      'v351-imp2', 'v360-sup1', 'v361-sdk1', 'v362-sdk2', 'v363-sdk3',
                      'v364-sdk4', 'v365-sdk5',
                      '3.1.0-SRV2', '3.2.0-ORB1', '3.2.1-ORB2', '3.3.0-NUC1',
                      '3.4.0-IMP1', '3.4.1-RIV1', '3.5.0-ESC1', '3.5.1-IMP2',
                      '3.6.0-SUP1', '3.6.1-SDK1', '3.6.2-SDK2', '3.6.3-SDK3',
                      '3.6.4-SDK4', '3.6.5-SDK5'):
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

        print('== El SDK y los campeonatos viajan dentro del COMPLETO ==')
        with zipfile.ZipFile('/home/z/my-project/public/descargas/crazypp-v3648-sdk6-COMPLETO.zip') as z:
            nombres = z.namelist()
            chk('championships/sdk/champ_sdk.js' in nombres,
                'COMPLETO incluye championships/sdk/champ_sdk.js')
            if 'championships/sdk/champ_sdk.js' in nombres:
                sdkzip = z.read('championships/sdk/champ_sdk.js').decode('utf-8')
                chk("const SDK_VERSION = '1.5.4'" in sdkzip
                    and 'function precarga' in sdkzip
                    and 'export function createMusic' in sdkzip
                    and 'export function createPowerSign' in sdkzip
                    and 'export function createRival' in sdkzip
                    and 'export function createCartel' in sdkzip,
                    'SDK dentro del ZIP = v1.4.0 (música + tablón + rival + tablero)')
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
            # el orbital también viaja y también es cero-decode en FASE 7
            srcEOz = z.read('championships/estacion_orbital/index.js').decode('utf-8')
            chk('decodeAudioData(' not in srcEOz,
                'orbital (ZIP): sin decodeAudioData propio (el «arsenal» es createMusic)')
        with zipfile.ZipFile('/home/z/my-project/public/descargas/crazypp-v3648-sdk6-CLOUDFLARE.zip') as z:
            chk('championships/sdk/champ_sdk.js' in z.namelist(),
                'CLOUDFLARE incluye el SDK')
        with zipfile.ZipFile('/home/z/my-project/public/descargas/crazypp-v3648-sdk6-ligera.zip') as z:
            con_champ = [n for n in z.namelist()
                         if n.startswith('championships/') and n != 'championships/'
                         and 'PON-AQUI' not in n]
            chk(not con_champ,
                f'ligera sin campeonatos (solo el marcador de la casa) {con_champ[:2]}')

        print('== Juego + SDK servidos por gateway ==')
        r = await RC.get(GW + '/game.html')
        cuerpo = await r.text()
        chk("const VERSION = '3.6.48-SDK6'" in cuerpo, 'gateway: game.html = 3.6.48-SDK6')
        chk('__PP_PADDLE_SWEEP' in cuerpo, 'gateway: puente CCD del núcleo')
        sdk = await (await RC.get(GW + '/championships/sdk/champ_sdk.js')).text()
        chk("const SDK_VERSION = '1.5.4'" in sdk and 'export function createSfx' in sdk
            and 'function precarga' in sdk and 'export function createMusic' in sdk
            and 'export function createPowerSign' in sdk
            and 'export function createRival' in sdk
            and 'export function createCartel' in sdk,
            'gateway: champ_sdk.js v1.4.0 servido (SFX + música + tablón + rival + tablero)')
        mod = await (await RC.get(GW + '/championships/estacion_orbital/index.js')).text()
        chk("from '../sdk/champ_sdk.js'" in mod and 'createSfx(import.meta.url' in mod,
            'gateway: orbital importa el SDK')
        chk('createPowerSign(THREE' in mod and "coreo: 'v240'" in mod,
            'gateway: tablón del orbital delega en el SDK (v240)')
        chk('createRival(THREE' in mod and "modo: 'perezoso'" in mod,
            'gateway: standee del ASTRO delega en createRival (perezoso)')
        chk('createCartel(THREE' in mod and 'this._cartelSDK.pinta((c, W, H) => {',
            'gateway: tablero de misión delega en createCartel (arte propio)')
        chk('get _musSDK()' in mod and 'gateOn: true,' in mod,
            'gateway: música del orbital delega en createMusic (knobs BSO)')
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
        chk(man.get('version') == 16, 'gateway: manifest v16 (orbital adopta rival/tablero/música en SDK5)')
        chk([st['id'] for st in man['stages']] == ['duelo1', 'impulso', 'duelo2', 'escudo', 'final'],
            'gateway: camino del manifest = duelo1·impulso·duelo2·escudo·final')
        chk(any('v3.6.1-SDK1' in c for c in man.get('cambios', [])),
            'gateway: cambios incluye la entrada v3.6.1-SDK1 (historial)')
        chk(any('v3.6.5-SDK5' in n for n in man.get('notes', [])),
            'gateway: notes incluye la entrada v3.6.5-SDK5 (FASE 7, historial)')

        print('== FASE 5/6/7: música + tablón + rival por gateway ==')
        TOKENS = {
            'oeste': ("import { createSfx, createMusic, createBucle, createPowerSign, congela, getCore, assetURL } from '../sdk/champ_sdk.js'",
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
                      '_musicStop() { this._musSDKv.off(); }',
                      'createPowerSign(THREE', "coreo: 'clasica'", "arte: 'plano'",
                      'pintar: (aplicar) => this._pintarRespaldo(aplicar)',
                      'oesteCanvas(1024, 560)'),
            'magia': ("import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'",
                      '__sfxSDK', "precarga('risas.mp3')", "eng.play('risas.mp3', 1.0)",
                      'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                      'const __CORE = getCore() || {}',
                      'get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
                      'this._musSDK.sync();',
                      'createPowerSign(THREE', "coreo: 'clasica'", "arte: 'canvas1024'",
                      'fallbackURL: () => paintPowerBanner()'),
            'locura': ("import { createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'",
                       'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                       'const __CORE = getCore() || {}',
                       'createPowerSign(THREE', "coreo: 'v240'", 'halo: true',
                       "arte: 'fit1833'"),
            'valle_neon': ("import { createCartel, createMusic, createRival, getCore } from '../sdk/champ_sdk.js'",
                           'const CORE = getCore();',
                           'get _musSDK()', 'fadeIn: 1.2', 'ancla: false',
                           "syncMode: 'none'", 'gateOn: true', 'stopFade: 0.4',
                           'createRival(THREE', "modo: 'precarga'",
                           "base: 'rival_kraken.png'", "ext: 'png'",
                           'createCartel(THREE', 'this._cartelSDK.pinta((',
                           'this._rivalSDK.rivalEstado(st);'),
        }
        ORB_EXTRA = ("import { createCartel, createMusic, createPowerSign, createRival, createSfx, congela } from '../sdk/champ_sdk.js'",
                     'createRival(THREE', "modo: 'perezoso'", "base: 'rival.webp'",
                     'onTex: (t) => this._ownTex.add(t),',
                     'createCartel(THREE', 'this._cartelSDK.pinta((c, W, H) => {',
                     'this._rivalSDK.rivalEstado(estado);',
                     'get _musSDK()', 'vol: () => this._musicEffVol()',
                     'musicOn() { this._musSDK.on(); }')
        for mod_, vman, nota in ADOPTANTES:
            srcm = await (await RC.get(GW + f'/championships/{mod_}/index.js')).text()
            for tk in TOKENS[mod_]:
                chk(tk in srcm, f'gateway {mod_}: {tk[:58]}')
            chk('freezeT = Math.max' not in srcm, f'gateway {mod_}: sin freeze duplicado')
            chk(srcm.count('decodeAudioData(') == 0,
                f'gateway {mod_}: decodeAudioData solo en el SDK (0 en el módulo)')
            manm = await (await RC.get(GW + f'/championships/{mod_}/manifest.json')).json()
            chk(manm.get('version') == vman, f'gateway {mod_}: manifest v{vman}')
            chk(any(nota in n for n in manm.get('notes', [])),
                f'gateway {mod_}: nota {nota} en el historial')
        srcEO = await (await RC.get(GW + '/championships/estacion_orbital/index.js')).text()
        for tk in ORB_EXTRA:
            chk(tk in srcEO, f'gateway orbital: {tk[:58]}')
        chk(srcEO.count('decodeAudioData(') == 0,
            'gateway orbital: 0 decodeAudioData (el arsenal vive en createMusic)')

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
        await page.screenshot(path='/home/z/my-project/download/qa_sdk5_descargas_hub.png')
        await A.close()
        await RC.dispose()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
