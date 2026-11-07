#!/usr/bin/env python3
"""Deriva los QA de la V3.6.2-SDK2 (FASE 4: SDK adoptado por los 5):
  · qa_sup1_v361.py  → qa_sup1_v362.py (versión + SDK v1.1.0 + sección nueva
    de los 4 campeonatos adoptantes; la entrada v3.6.1-SDK1 del orbital NO
    se toca — el manifest del orbital no cambia en esta fase)
  · qa_imp2_v351.py / qa_escudo_v350.py → parche de versión in situ
  · qa_descargas_v362.py → nuevo (tamaños reales de los 4 ZIPs)
Cada reemplazo se cuenta y se aserta: si el origen cambia, el derivador FALLA."""
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

def reemplazar(s, viejo, nuevo, esperado, etiqueta):
    n = s.count(viejo)
    assert n == esperado, f'{etiqueta}: {viejo!r} aparece {n} veces (esperado {esperado})'
    return s.replace(viejo, nuevo)

# ── 1. qa_sup1_v362.py ───────────────────────────────────────────
s = (SCR / 'qa_sup1_v361.py').read_text(encoding='utf-8')
s = reemplazar(s, 'QA del JUEGO · V3.6.1-SDK1', 'QA del JUEGO · V3.6.2-SDK2', 1, 'uso/doc')
s = reemplazar(s, "chk(ver == '3.6.1-SDK1', f'__PP_VERSION = {ver!r}')",
               "chk(ver == '3.6.2-SDK2', f'__PP_VERSION = {ver!r}')", 1, 'versión dev')
s = reemplazar(s, "chk('V3.6.1-SDK1' in badge, f'badge 2D = {badge!r}')",
               "chk('V3.6.2-SDK2' in badge, f'badge 2D = {badge!r}')", 1, 'badge')
s = reemplazar(s, "chk(await pg2.evaluate(\"window.__PP_VERSION\") == '3.6.1-SDK1', 'gateway: __PP_VERSION 3.6.1-SDK1')",
               "chk(await pg2.evaluate(\"window.__PP_VERSION\") == '3.6.2-SDK2', 'gateway: __PP_VERSION 3.6.2-SDK2')",
               1, 'versión gateway')
s = reemplazar(s, "\"const SDK_VERSION = '1.0.0'\"", "\"const SDK_VERSION = '1.1.0'\"", 1, 'SDK versión')
s = reemplazar(s, "'forma promesa (v2.125)', 'decodeAudioData(ab.slice(0))'):",
               "'forma promesa (v2.125)', 'decodeAudioData(ab.slice(0))',\n"
               "                   'function precarga', 'opts && opts.pan'):", 1, 'tokens SDK 1.1.0')
s = reemplazar(s, "chk(await page.evaluate(\"window.__PP_SDK || ''\") == '1.0.0',\n"
                  "            'window.__PP_SDK = 1.0.0 (SDK importado en cadena por el orbital)')",
               "chk(await page.evaluate(\"window.__PP_SDK || ''\") == '1.1.0',\n"
               "            'window.__PP_SDK = 1.1.0 (SDK importado en cadena por el orbital)')",
               1, 'check runtime __PP_SDK')
s = reemplazar(s, "            chk(tk in sdksrc, f'SDK: {tk}')",
               "            chk(tk in sdksrc, f'SDK: {tk}')\n"
               "\n"
               "        print('== FASE 4: los 4 campeonatos adoptantes ==')\n"
               "        for mod, vman in (('oeste', 49), ('magia', 29), ('locura', 21),\n"
               "                          ('valle_neon', 2)):\n"
               "            srcm = await page.evaluate(\n"
               "                f\"fetch('championships/{mod}/index.js').then(r=>r.text())\")\n"
               "            chk(\"from '../sdk/champ_sdk.js'\" in srcm, f'{mod}: importa el SDK')\n"
               "            chk('freezeT = Math.max' not in srcm, f'{mod}: sin freeze duplicado')\n"
               "            manm = await page.evaluate(\n"
               "                f\"fetch('championships/{mod}/manifest.json').then(r=>r.json())\")\n"
               "            chk(manm.get('version') == vman, f'{mod}: manifest v{vman}')\n"
               "            chk(any('v3.6.2-SDK2' in n for n in manm.get('notes', [])),\n"
               "                f'{mod}: nota SDK2 en el historial')",
               1, 'sección FASE 4 (4 adoptantes)')
# La entrada v3.6.1-SDK1 del ORBITAL (cambios) queda intacta: la línea del
# check lleva 2 menciones (token + etiqueta) y es la ÚNICA que debe quedar.
assert s.count('3.6.1-SDK1') == 2, s.count('3.6.1-SDK1')
(SCR / 'qa_sup1_v362.py').write_text(s, encoding='utf-8')
print('· qa_sup1_v362.py derivado (SDK 1.1.0 + sección FASE 4, orbital v14 intacto)')

# ── 2. qa_imp2_v351.py (parche de versión in situ) ───────────────
p = SCR / 'qa_imp2_v351.py'
s = p.read_text(encoding='utf-8')
if '3.6.1-SDK1' in s:
    s = reemplazar(s, '3.6.1-SDK1', '3.6.2-SDK2', 2, 'imp2 versión')
    p.write_text(s, encoding='utf-8')
    print('· qa_imp2_v351.py → 3.6.2-SDK2')
else:
    assert '3.6.2-SDK2' in s, 'imp2 sin versión conocida'
    print('· qa_imp2_v351.py ya estaba en 3.6.2-SDK2')

# ── 3. qa_escudo_v350.py (parche de versión in situ) ─────────────
p = SCR / 'qa_escudo_v350.py'
s = p.read_text(encoding='utf-8')
if '3.6.1-SDK1' in s:
    s = reemplazar(s, '3.6.1-SDK1', '3.6.2-SDK2', 4, 'escudo versión')
    p.write_text(s, encoding='utf-8')
    print('· qa_escudo_v350.py → 3.6.2-SDK2')
else:
    assert '3.6.2-SDK2' in s, 'escudo sin versión conocida'
    print('· qa_escudo_v350.py ya estaba en 3.6.2-SDK2')

# ── 4. qa_descargas_v362.py (nuevo) ──────────────────────────────
QA = '''#!/usr/bin/env python3
"""QA del HUB /descargas · V3.6.2-SDK2 (FASE 4: SDK adoptado por los 5).
Uso: python3 scripts/qa_descargas_v362.py"""
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
    'crazypp-v362-sdk2-COMPLETO.zip': 125213949,
    'crazypp-v362-sdk2-ligera.zip': 11452689,
    'crazypp-v362-sdk2-CLOUDFLARE.zip': 125201525,
    'crazypp-live-service-SOLO.zip': 6089,
}

ADOPTANTES = (('oeste', 49), ('magia', 29), ('locura', 21), ('valle_neon', 2))

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
        chk(html.count('v362-sdk2') >= 3, f'enlaces v362-sdk2 ({html.count("v362-sdk2")})')
        chk(html.count('3.6.2-SDK2') >= 5, f'menciones 3.6.2-SDK2 ({html.count("3.6.2-SDK2")})')
        for kw in ('SDK de campeonatos', 'champ_sdk', 'FASE 4', 'FASE 3', 'fuente única',
                   'SUPERPODERES REDEFINIDOS', 'congela la partida', 'rocas en 3D',
                   'vetas de óxido', 'rayo tractor', 'dron', 'ATRAPADA',
                   'caída vertical', 'gravedad cero', 'partículas blancas',
                   'risa', 'enfado', 'ASTRO', 'diana se ve 2 segundos',
                   'siempre vuelve a botar', 'REACTOR DE IMPULSO',
                   'ESCUDO DE PALA', 'etapa 4', 'PRECISIÓN CCD'):
            chk(kw in html, f'el hub menciona {kw!r}')
        for viejo in ('v310-srv2', 'v312-ccd1', 'v320-orb1', 'v321-orb2',
                      'v330-nuc1', 'v340-imp1', 'v341-riv1', 'v350-esc1',
                      'v351-imp2', 'v360-sup1', 'v361-sdk1',
                      '3.1.0-SRV2', '3.2.0-ORB1', '3.2.1-ORB2', '3.3.0-NUC1',
                      '3.4.0-IMP1', '3.4.1-RIV1', '3.5.0-ESC1', '3.5.1-IMP2',
                      '3.6.0-SUP1', '3.6.1-SDK1'):
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

        print('== El SDK y los 4 adoptantes viajan dentro del COMPLETO ==')
        with zipfile.ZipFile('/home/z/my-project/public/descargas/crazypp-v362-sdk2-COMPLETO.zip') as z:
            nombres = z.namelist()
            chk('championships/sdk/champ_sdk.js' in nombres,
                'COMPLETO incluye championships/sdk/champ_sdk.js')
            if 'championships/sdk/champ_sdk.js' in nombres:
                sdkzip = z.read('championships/sdk/champ_sdk.js').decode('utf-8')
                chk("const SDK_VERSION = '1.1.0'" in sdkzip and 'function precarga' in sdkzip,
                    'SDK dentro del ZIP = v1.1.0 (con precarga)')
            chk('championships/estacion_orbital/index.js' in nombres,
                'COMPLETO incluye el orbital (adoptante SDK1)')
            for mod, vman in ADOPTANTES:
                dentro = f'championships/{mod}/index.js' in nombres
                chk(dentro, f'COMPLETO incluye championships/{mod}/index.js')
                if dentro:
                    srcm = z.read(f'championships/{mod}/index.js').decode('utf-8')
                    chk("from '../sdk/champ_sdk.js'" in srcm, f'{mod} (ZIP): importa el SDK')
                    chk('freezeT = Math.max' not in srcm, f'{mod} (ZIP): sin freeze duplicado')
                manz = z.read(f'championships/{mod}/manifest.json').decode('utf-8')
                import json as _json
                chk(_json.loads(manz).get('version') == vman, f'{mod} (ZIP): manifest v{vman}')
        with zipfile.ZipFile('/home/z/my-project/public/descargas/crazypp-v362-sdk2-CLOUDFLARE.zip') as z:
            chk('championships/sdk/champ_sdk.js' in z.namelist(),
                'CLOUDFLARE incluye el SDK')
        with zipfile.ZipFile('/home/z/my-project/public/descargas/crazypp-v362-sdk2-ligera.zip') as z:
            con_champ = [n for n in z.namelist()
                         if n.startswith('championships/') and n != 'championships/'
                         and 'PON-AQUI' not in n]
            chk(not con_champ,
                f'ligera sin campeonatos (solo el marcador de la casa) {con_champ[:2]}')

        print('== Juego + SDK servidos por gateway ==')
        r = await RC.get(GW + '/game.html')
        cuerpo = await r.text()
        chk("const VERSION = '3.6.2-SDK2'" in cuerpo, 'gateway: game.html = 3.6.2-SDK2')
        chk('__PP_PADDLE_SWEEP' in cuerpo, 'gateway: puente CCD del núcleo')
        sdk = await (await RC.get(GW + '/championships/sdk/champ_sdk.js')).text()
        chk("const SDK_VERSION = '1.1.0'" in sdk and 'export function createSfx' in sdk
            and 'function precarga' in sdk,
            'gateway: champ_sdk.js v1.1.0 servido')
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
        chk(man.get('version') == 14, 'gateway: manifest v14 (orbital intacto en SDK2)')
        chk([st['id'] for st in man['stages']] == ['duelo1', 'impulso', 'duelo2', 'escudo', 'final'],
            'gateway: camino del manifest = duelo1·impulso·duelo2·escudo·final')
        chk(any('v3.6.1-SDK1' in c for c in man.get('cambios', [])),
            'gateway: cambios incluye la entrada v3.6.1-SDK1 (historial)')

        print('== FASE 4: los 4 campeonatos adoptantes por gateway ==')
        TOKENS = {
            'oeste': ("import { createSfx, congela, getCore } from '../sdk/champ_sdk.js'",
                      '__sfxSDK', "precarga('risas_forajido.mp3')",
                      "eng.play('risas.mp3', vol || 0.8, { pan: 0.4 })",
                      'congela(g, DUELO_P.drawT + DUELO_P.window + 0.35)',
                      'congela(g, 0.10)',
                      'congela(g, Math.max(this.powerSign.T_OUT, OESTE_POWER.warn) + 0.1)',
                      'const __CORE = getCore() || {}'),
            'magia': ("import { createSfx, congela, getCore } from '../sdk/champ_sdk.js'",
                      '__sfxSDK', "precarga('risas.mp3')", "eng.play('risas.mp3', 1.0)",
                      'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                      'const __CORE = getCore() || {}'),
            'locura': ("import { congela, getCore } from '../sdk/champ_sdk.js'",
                       'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                       'const __CORE = getCore() || {}'),
            'valle_neon': ("import { getCore } from '../sdk/champ_sdk.js'",
                           'const CORE = getCore();'),
        }
        DECODE_ESPERADO = {'oeste': 2, 'magia': 1, 'locura': 0, 'valle_neon': 1}
        for mod, vman in ADOPTANTES:
            srcm = await (await RC.get(GW + f'/championships/{mod}/index.js')).text()
            for tk in TOKENS[mod]:
                chk(tk in srcm, f'gateway {mod}: {tk[:58]}')
            chk('freezeT = Math.max' not in srcm, f'gateway {mod}: sin freeze duplicado')
            chk(srcm.count('decodeAudioData(') == DECODE_ESPERADO[mod],
                f'gateway {mod}: decodeAudioData solo en la música ({DECODE_ESPERADO[mod]})')
            manm = await (await RC.get(GW + f'/championships/{mod}/manifest.json')).json()
            chk(manm.get('version') == vman, f'gateway {mod}: manifest v{vman}')
            chk(any('v3.6.2-SDK2' in n for n in manm.get('notes', [])),
                f'gateway {mod}: nota SDK2 en el historial')

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
        await page.screenshot(path='/home/z/my-project/download/qa_sdk2_descargas_hub.png')
        await A.close()
        await RC.dispose()

    print(f'\\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
'''
(SCR / 'qa_descargas_v362.py').write_text(QA, encoding='utf-8')
print('· qa_descargas_v362.py escrito (4 ZIPs + SDK 1.1.0 + 4 adoptantes)')

print('\\nQA v362 listos.')
