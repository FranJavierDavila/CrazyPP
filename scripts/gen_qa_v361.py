#!/usr/bin/env python3
"""Deriva los QA de la V3.6.1-SDK1:
  · qa_sup1_v360.py  → qa_sup1_v361.py  (versión + tokens SDK + engine __sdkSfx
    en las pruebas en vivo + checks del SDK como fichero)
  · qa_imp2_v351.py  → parche de versión in situ (3.6.1-SDK1)
  · qa_escudo_v350.py→ parche de versión in situ (3.6.1-SDK1)
Cada reemplazo se cuenta y se aserta: si el origen cambia, el derivador FALLA."""
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

def reemplazar(s, viejo, nuevo, esperado, etiqueta):
    n = s.count(viejo)
    assert n == esperado, f'{etiqueta}: {viejo!r} aparece {n} veces (esperado {esperado})'
    return s.replace(viejo, nuevo)

# ── 1. qa_sup1_v361.py ────────────────────────────────────────────
s = (SCR / 'qa_sup1_v360.py').read_text(encoding='utf-8')
s = reemplazar(s, 'qa_sup1_v360', 'qa_sup1_v361', 1, 'uso/doc')
s = reemplazar(s, '3.6.0-SUP1', '3.6.1-SDK1', 7, 'versión')
s = reemplazar(
    s,
    "            # freeze del aviso\n"
    "            'this.game.freezeT = Math.max(this.game.freezeT || 0,',",
    "            # freeze del aviso — v3.6.1: vive en el SDK (una sola fuente)\n"
    "            'congela(this.game, (def.warn || 2.0) + 0.15)',\n"
    "            \"from '../sdk/champ_sdk.js'\", 'createSfx(import.meta.url', '__sdkSfx',",
    1, 'token freeze→SDK')
s = reemplazar(
    s,
    "            \"a._sfx('risa_astro.mp3')\", 'decodeAudioData(ab.slice(0))',",
    "            \"a._sfx('risa_astro.mp3')\",",
    1, 'token decodeAudioData (ahora en el SDK)')
s = reemplazar(s, "man.get('version') == 13", "man.get('version') == 14", 1, 'manifest v14')
s = reemplazar(
    s,
    'if (ctrl._sfxBufs && ctrl._sfxBufs[k]) return true;',
    'if (ctrl.__sdkSfx && ctrl.__sdkSfx.tiene(k)) return true;',
    1, 'engine SFX en vivo (__sdkSfx.tiene)')
s = reemplazar(
    s,
    "        print('== ESCENA EN VIVO: campeonato cargado ==')",
    "        print('== SDK DE CAMPEONATOS (champ_sdk.js) ==')\n"
    "        sdksrc = await page.evaluate(\"fetch('championships/sdk/champ_sdk.js').then(r=>r.text())\")\n"
    "        for tk in (\"const SDK_VERSION = '1.0.0'\", 'export function createSfx',\n"
    "                   'export function congela', 'export function descongela',\n"
    "                   'export function getCore', 'export function assetURL',\n"
    "                   'forma promesa (v2.125)', 'decodeAudioData(ab.slice(0))'):\n"
    "            chk(tk in sdksrc, f'SDK: {tk}')\n"
    "\n"
    "        print('== ESCENA EN VIVO: campeonato cargado ==')",
    1, 'sección SDK (fichero)')
s = reemplazar(
    s,
    "        chk(ctx['state'] in ('sala', 'duelo'), f\"controlador vivo (state {ctx['state']})\")",
    "        chk(ctx['state'] in ('sala', 'duelo'), f\"controlador vivo (state {ctx['state']})\")\n"
    "        chk(await page.evaluate(\"window.__PP_SDK || ''\") == '1.0.0',\n"
    "            'window.__PP_SDK = 1.0.0 (SDK importado en cadena por el orbital)')",
    1, 'check runtime __PP_SDK')
assert '3.6.0-SUP1' not in s and '_sfxBufs' not in s
(SCR / 'qa_sup1_v361.py').write_text(s, encoding='utf-8')
print('· qa_sup1_v361.py derivado (tokens SDK + engine vivo + manifest v14)')

# ── 2. qa_imp2_v351.py (parche de versión in situ, idempotente) ──
p = SCR / 'qa_imp2_v351.py'
s = p.read_text(encoding='utf-8')
cambios_imp2 = [
    ("chk(ver == '3.6.0-SUP1', f'__PP_VERSION = {ver!r}')",
     "chk(ver == '3.6.1-SDK1', f'__PP_VERSION = {ver!r}')"),
    ("chk('V3.6.0-SUP1' in badge, f'badge 2D = {badge!r}')",
     "chk('V3.6.1-SDK1' in badge, f'badge 2D = {badge!r}')"),
    ("chk(man.get('version') == 13, f'manifest version = {man.get(\"version\")}')",
     "chk(man.get('version') == 14, f'manifest version = {man.get(\"version\")}')"),
]
for viejo, nuevo in cambios_imp2:
    if viejo in s:
        s = s.replace(viejo, nuevo)
p.write_text(s, encoding='utf-8')
assert '3.6.0-SUP1' not in s, 'imp2 con restos de versión vieja'
print('· qa_imp2_v351.py → 3.6.1-SDK1 (versión, badge y manifest v14)')

# ── 3. qa_escudo_v350.py (parche de versión in situ, idempotente) ─
p = SCR / 'qa_escudo_v350.py'
s = p.read_text(encoding='utf-8')
if "chk(man.get('version') == 13," in s:
    s = s.replace("chk(man.get('version') == 13, f'manifest version = {man.get(\"version\")}')",
                  "chk(man.get('version') == 14, f'manifest version = {man.get(\"version\")}')")
    p.write_text(s, encoding='utf-8')
print('· qa_escudo_v350.py → versión 3.6.1-SDK1 + manifest v14')

print('\nQA v361 listos.')
