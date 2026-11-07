#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deriva los QA de la V3.6.5-SDK5 (FASE 7 · CIERRE DEL SDK v1.x):
  · qa_sup1_v364.py  → qa_sup1_v365.py (versión + SDK v1.4.0 + secciones
    FASE 5/6 actualizadas + FASE 7 nueva: createRival/createCartel/música
    del orbital — 0 decodeAudioData en los 5)
  · qa_imp2_v351.py / qa_escudo_v350.py → parche de versión in situ +
    manifest orbital 15 → 16 (el check histórico vive en ambos)
  · qa_descargas_v365.py → nuevo (tamaños reales de los 4 ZIPs)
  · smoke_sdk5.py → nuevo (import en cadena + createRival/createCartel)
Cada reemplazo se cuenta y se aserta: si el origen cambia, el derivador FALLA."""
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

def reemplazar(s, viejo, nuevo, esperado, etiqueta):
    n = s.count(viejo)
    assert n == esperado, f'{etiqueta}: {viejo!r} aparece {n} veces (esperado {esperado})'
    return s.replace(viejo, nuevo)

# ── 1. qa_sup1_v365.py ───────────────────────────────────────────
s = (SCR / 'qa_sup1_v364.py').read_text(encoding='utf-8')
s = reemplazar(s, 'QA del JUEGO · V3.6.4-SDK4', 'QA del JUEGO · V3.6.5-SDK5', 1, 'uso/doc')
s = reemplazar(s, "chk(ver == '3.6.4-SDK4'", "chk(ver == '3.6.5-SDK5'", 1, 'versión dev')
s = reemplazar(s, "chk('V3.6.4-SDK4' in badge", "chk('V3.6.5-SDK5' in badge", 1, 'badge')
s = reemplazar(s, "== '3.6.4-SDK4', 'gateway: __PP_VERSION 3.6.4-SDK4'",
               "== '3.6.5-SDK5', 'gateway: __PP_VERSION 3.6.5-SDK5'", 1, 'gateway versión')
# manifest del orbital: v15 → v16 (check temprano)
s = reemplazar(s, "chk(man.get('version') == 15, f'manifest version = {man.get(\"version\")}')",
               "chk(man.get('version') == 16, f'manifest version = {man.get(\"version\")}')", 1, 'check orbital v16')
# SDK 1.4.0: versión + tokens nuevos
s = reemplazar(s, "\"const SDK_VERSION = '1.3.0'\", 'export function createSfx',",
               "\"const SDK_VERSION = '1.4.0'\", 'export function createSfx',", 1, 'SDK versión fuente')
s = reemplazar(s, "                   'V240 = o.coreo', 'pintorSuperPower'):",
               "                   'V240 = o.coreo',\n"
               "                   'export function createRival', \"o.modo === 'precarga'\",\n"
               "                   'export function createCartel', 'pintorSuperPower'):",
               1, 'tokens SDK 1.4.0')
# FASE 5: valle sube a v4 (mantiene su nota histórica SDK3)
s = reemplazar(s, "('valle_neon', 3, 'v3.6.3-SDK3')", "('valle_neon', 4, 'v3.6.3-SDK3')", 1, 'valle v4')
# FASE 6: orbital sube a v16 y ya NO conserva decodeAudioData
s = reemplazar(s, "('estacion_orbital', 15, 'v240')", "('estacion_orbital', 16, 'v240')", 1, 'orbital v16 FASE6')
s = reemplazar(s, "            ndec = srcm.count('decodeAudioData(')\n"
                  "            chk(ndec == (1 if mod == 'estacion_orbital' else 0),\n"
                  "                f'{mod}: decodeAudioData propio = {ndec} (orbital: SFX de arsenal, resto 0)')",
               "            ndec = srcm.count('decodeAudioData(')\n"
               "            chk(ndec == 0,\n"
               "                f'{mod}: decodeAudioData propio = {ndec} (FASE 7: cero en los 5)')",
               1, 'ndec cero en todos')
# NUEVA — FASE 7: standee + tablero en el SDK, música orbital incluida
FASE7 = """
        print('== FASE 7: standee + tablero en el SDK (createRival/createCartel) ==')
        for mod, vman, modo, base in (('estacion_orbital', 16, 'perezoso', 'rival.webp'),
                                      ('valle_neon', 4, 'precarga', 'rival_kraken.png')):
            srcm = await page.evaluate(
                f"fetch('championships/{mod}/index.js').then(r=>r.text())")
            chk('createRival(THREE' in srcm, f'{mod}: el standee delega en el SDK')
            chk(\"modo: '\" + modo + \"'\" in srcm, f'{mod}: motor {modo} conservado')
            chk(\"base: '\" + base + \"'\" in srcm, f'{mod}: arte {base} cableado')
            chk('createCartel(THREE' in srcm, f'{mod}: el tablero delega en el SDK')
            chk('this._cartelSDK.pinta(' in srcm, f'{mod}: el ARTE pinta en el lienzo del SDK')
            chk('get _musSDK()' in srcm, f'{mod}: la música delega en createMusic')
            manm = await page.evaluate(
                f"fetch('championships/{mod}/manifest.json').then(r=>r.json())")
            chk(manm.get('version') == vman, f'{mod}: manifest v{vman}')
            chk(any('v3.6.5-SDK5' in n for n in manm.get('notes', [])),
                f'{mod}: nota SDK5 en el historial')
        ndec = await page.evaluate(\"\"\"async () => {
          let n = 0;
          for (const m of ['oeste', 'magia', 'locura', 'estacion_orbital', 'valle_neon']) {
            const s = await fetch('championships/' + m + '/index.js').then(r => r.text());
            n += (s.match(/decodeAudioData[(]/g) || []).length;
          }
          return n;
        }\"\"\")
        chk(ndec == 0, f'decodeAudioData en los 5 módulos = {ndec} (FASE 7: cero; solo el SDK)')

        print('== ESCENA EN VIVO: campeonato cargado ==')"""
s = reemplazar(s, "\n        print('== ESCENA EN VIVO: campeonato cargado ==')", FASE7, 1, 'sección FASE 7')
# runtime __PP_SDK
s = reemplazar(s, "== '1.3.0',", "== '1.4.0',", 1, 'check runtime __PP_SDK (valor)')
s = reemplazar(s, "'window.__PP_SDK = 1.3.0", "'window.__PP_SDK = 1.4.0", 1, 'check runtime __PP_SDK (etiqueta)')
# el objetivo de la gravedad cero es ALEATORIO por diseño («rebota ENTRE las
# partículas de manera aleatoria») — el umbral sobre minY era flaky: el
# invariante determinista es la FRACCIÓN de frames sobre el suelo (>50%;
# en caída libre sería ~9%)
s = reemplazar(s, "let minY = 9, spd = 0, cambios = 0, lastT = ctrl._act.tgt;",
               "let minY = 9, spd = 0, cambios = 0, sobreCero = 0, lastT = ctrl._act.tgt;",
               1, 'sobreCero: contador')
s = reemplazar(s, "            minY = Math.min(minY, ball.pos.y);\n            spd = ball.vel.length();",
               "            minY = Math.min(minY, ball.pos.y);\n            if (ball.pos.y > 0) sobreCero++;\n            spd = ball.vel.length();",
               1, 'sobreCero: cuenta frames')
s = reemplazar(s, "          out.minY = minY; out.spd = spd; out.cambios = cambios;",
               "          out.minY = minY; out.spd = spd; out.cambios = cambios;\n          out.sobreCero = sobreCero / 300;",
               1, 'sobreCero: salida')
s = reemplazar(s, "chk(cer['minY'] > 0.4, f\"la bola flota: y mínima {cer['minY']:.2f} (gravedad compensada)\")",
               "chk(cer['sobreCero'] > 0.5, f\"la bola FLOTA: {round(cer['sobreCero'] * 100)}% de frames sobre el suelo (y mín {cer['minY']:.2f}; gravedad compensada)\")",
               1, 'sobreCero: check robusto')
# históricos intactos: notas SDK4 de la FASE 5/6 (oeste+magia+bucle, 3) +
# orbital SDK1 (2) + valle SDK3 (1)
assert s.count('3.6.4-SDK4') == 3, s.count('3.6.4-SDK4')
assert s.count('3.6.1-SDK1') == 2, s.count('3.6.1-SDK1')
assert s.count('3.6.3-SDK3') == 1, s.count('3.6.3-SDK3')
(SCR / 'qa_sup1_v365.py').write_text(s, encoding='utf-8')
print('· qa_sup1_v365.py derivado (SDK 1.4.0 + FASE 5/6/7, orbital v16, 0 decodeAudioData)')

# ── 2. qa_imp2_v351.py (parche de versión + manifest v16 in situ) ─
p = SCR / 'qa_imp2_v351.py'
s = p.read_text(encoding='utf-8')
cambios = 0
if '3.6.4-SDK4' in s:
    n = s.count('3.6.4-SDK4')
    s = reemplazar(s, '3.6.4-SDK4', '3.6.5-SDK5', n, 'imp2 versión')
    cambios += 1
else:
    assert '3.6.5-SDK5' in s, 'imp2 sin versión conocida'
n15 = s.count("man.get('version') == 15")
if n15:
    s = reemplazar(s, "man.get('version') == 15", "man.get('version') == 16", n15, 'imp2 manifest orbital v16')
    cambios += 1
if cambios:
    p.write_text(s, encoding='utf-8')
print(f'· qa_imp2_v351.py → 3.6.5-SDK5 + manifest v16 ({cambios} grupos de parches)')

# ── 3. qa_escudo_v350.py (parche de versión + manifest v16 in situ) ─
p = SCR / 'qa_escudo_v350.py'
s = p.read_text(encoding='utf-8')
cambios = 0
if '3.6.4-SDK4' in s:
    n = s.count('3.6.4-SDK4')
    s = reemplazar(s, '3.6.4-SDK4', '3.6.5-SDK5', n, 'escudo versión')
    cambios += 1
else:
    assert '3.6.5-SDK5' in s, 'escudo sin versión conocida'
n15 = s.count("man.get('version') == 15")
if n15:
    s = reemplazar(s, "man.get('version') == 15", "man.get('version') == 16", n15, 'escudo manifest orbital v16')
    cambios += 1
if cambios:
    p.write_text(s, encoding='utf-8')
print(f'· qa_escudo_v350.py → 3.6.5-SDK5 + manifest v16 ({cambios} grupos de parches)')

print('\\n(parte 2: qa_descargas_v365 + smoke_sdk5 en gen_qa_v365_b.py)')
