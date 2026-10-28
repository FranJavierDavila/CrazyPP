#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · ronda 23 · QA «CHAMPION LISTO» — el estado POST-VICTORIA
en producción, para los 5 campeonatos.
=======================================================================
El dueño está a 3 nodos del primer champion de la historia (oeste 3/5 →
Duelo Nv.2 → Tren → Duelo Final). Esta capa carga game.html de PRODUCCIÓN
en Chromium headless con el estado EXACTO que quedará tras ganar el Duelo
Final (pp_tele=0: el bot no contamina D1) y afirma la cadena completa de
«campeón»:

  · championFlag(id) = true para los 5 (oeste/locura/magia/EO/valle)
  · menuHint()          → «★ SUPERADO · …» (precedencia campeón, v2.128)
  · _stageHint(oeste)   → '' (callado: lo cubre el chip ★, ronda 19)
  · control negativo    → sin la clave champ, championFlag vuelve a false
  · storage restaurado intacto tras las variantes
  · 0 pageerrors durante el arranque

Auditoría de claves (ronda 23, escritura == lectura en los 5):
  oeste            pp_champ_oeste_champ           (index.js 12439 ↔ 11022)
  locura           pp_arcade_trophy               (3216 ↔ 2780)
  magia            pp_champ_magia_trophy          (4623 ↔ 3643, isChampion)
  estacion_orbital pp_champ_estacion_orbital_champ (7772 ↔ 6645)
  halloween        pp_champ_halloween_champ     (r85 · plantilla)

Uso: python3 scripts/qa_champion_listo.py [versión-esperada]
     (default: la de src/game/VERSION.json — la fuente de verdad)
"""
import asyncio
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'https://franjavierdavila.github.io/CrazyPP/game.html'


def version_fuente():
    try:
        with open(os.path.join(RAIZ, 'src', 'game', 'VERSION.json'),
                  encoding='utf-8') as f:
            return json.load(f).get('version')
    except Exception:
        return None


ESPERADA = sys.argv[1] if len(sys.argv) > 1 else (version_fuente() or '')

# Estado POST-VICTORIA de los 5 campeonatos (etapa final + marca de campeón)
ESTADO = {
    'pp_tele': '0',                                  # el bot NO deja huella en D1
    'pp_champ_oeste_champ': '1',                     # ← lo que escribirá _championFlow
    'pp_champ_oeste_stage': '5',
    'pp_arcade_trophy': '1',
    'pp_arcade_stage': '5',
    'pp_champ_magia_trophy': '1',
    'pp_champ_magia_stage': '4',
    'pp_champ_estacion_orbital_champ': '1',
    'pp_champ_estacion_orbital_stage': '4',
    'pp_champ_halloween_champ': '1',
    'pp_champ_halloween_stage': '5',
}

IDS = ['oeste', 'locura', 'magia', 'estacion_orbital', 'halloween']


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        perr = []
        page.on('pageerror', lambda e: perr.append(str(e)))
        await page.add_init_script(
            "try { for (const [k, v] of Object.entries("
            + repr(ESTADO).replace("'", '"') + ")) localStorage.setItem(k, v); "
            "} catch (e) {}"
        )
        await page.goto(URL, wait_until='domcontentloaded', timeout=60_000)
        # patrón qa_hub_hints (ronda 20): espera fija + poll del puente
        await page.wait_for_timeout(25_000)
        for _ in range(100):
            if await page.evaluate("() => !!(window.__game && window.__game.champs && window.__game.champs.championFlag)"):
                break
            await page.wait_for_timeout(500)
        else:
            ver = await page.evaluate("() => window.__PP_VERSION || null")
            print(f'✗ FALLO: window.__game.champs no llegó a tiempo · ver={ver}')
            print(f'  pageerrors capturados: {perr[:5] if perr else "ninguno"}')
            diagnostico = await page.evaluate("() => ({game: !!window.__game, champs: !!(window.__game && window.__game.champs), core: !!window.__PP_CORE, world: !!window.__PP_WORLD})")
            print(f'  window: {diagnostico}')
            await browser.close()
            return 1
        await page.wait_for_timeout(2_000)

        r = await page.evaluate("""() => {
          const CH = window.__game.champs;
          const out = { ver: window.__PP_VERSION || null, lang: null, pruebas: {} };
          out.lang = (window.__PP_CORE && window.__PP_CORE.lang) ? window.__PP_CORE.lang() : '?';
          const P = (nombre, fn) => { try { out.pruebas[nombre] = fn(); } catch (e) { out.pruebas[nombre] = 'EXC: ' + e; } };
          // 1 · los 5 campeones reconocidos
          for (const id of ['oeste','locura','magia','estacion_orbital','valle_neon'])
            P('flag_' + id, () => CH.championFlag(id));
          // 2 · precedencia del campeón en los consumidores reales
          P('menuHint', () => CH.menuHint());
          // oeste etapa 5 SIN ser campeón anuncia el DUELO FINAL (diseño
          // ronda 19); el campeón lo pisa la TARJETA (c12 1671) y menuHint
          // (c11 210) — reproducimos aquí el ORDEN EXACTO de la tarjeta:
          P('stage_oeste_campeon', () => CH._stageHint('oeste', 'pp_champ_oeste_'));
          P('stage_locura_campeon', () => CH._stageHint('locura', 'pp_arcade_'));
          P('resolucion_tarjeta_oeste', () => {
            // mismo orden que c12_pingponggame.js líneas 1665-1672
            let hint = CH._stageHint('oeste', 'pp_champ_oeste_') || '';
            if (CH.championFlag('oeste')) hint = (() => {
              const t = (window.__PP_CORE && window.__PP_CORE.T) ? window.__PP_CORE.T('champ_done_hint') : null;
              return t || '★ SUPERADO';
            })();
            return hint;
          });
          // 3 · control negativo: sin la clave, el Oeste deja de ser campeón
          localStorage.removeItem('pp_champ_oeste_champ');
          P('flag_oeste_sin_clave', () => CH.championFlag('oeste'));
          localStorage.setItem('pp_champ_oeste_champ', '1');
          P('flag_oeste_restaurado', () => CH.championFlag('oeste'));
          // 5 · LEYENDA (ronda 24): sellos 5/5 → tier por encima de SUPERADO
          localStorage.setItem('pp_champ_oeste_leyenda', '1');
          P('flag_leyenda_oeste', () => CH.leyendaFlag ? CH.leyendaFlag('oeste') : 'SIN leyendaFlag');
          P('resolucion_tarjeta_leyenda', () => {
            // mismo orden que c12 (ronda 24): etapa → SUPERADO → LEYENDA
            let hint = CH._stageHint('oeste', 'pp_champ_oeste_') || '';
            if (CH.championFlag('oeste')) hint = '★ SUPERADO';
            if (CH.leyendaFlag && CH.leyendaFlag('oeste')) {
              hint = (window.__PP_CORE && window.__PP_CORE.T) ? window.__PP_CORE.T('champ_leyenda_hint') : '★ LEYENDA';
            }
            return hint;
          });
          localStorage.removeItem('pp_champ_oeste_leyenda');
          P('flag_leyenda_off', () => CH.leyendaFlag('oeste'));
          // 4 · storage intacto
          P('storage_final', () => ({
            oeste: localStorage.getItem('pp_champ_oeste_champ'),
            locura: localStorage.getItem('pp_arcade_trophy'),
            magia: localStorage.getItem('pp_champ_magia_trophy'),
            eo: localStorage.getItem('pp_champ_estacion_orbital_champ'),
            valle: localStorage.getItem('pp_champ_valle_neon_champ'),
          }));
          return out;
        }""")
        await browser.close()

    ok = True

    def fallo(msg):
        nonlocal ok
        ok = False
        print(f'  ✗ {msg}')

    def bien(msg):
        print(f'  ✓ {msg}')

    print(f'versión: {r["ver"]} · idioma: {r["lang"]}')
    if r['ver'] != ESPERADA:
        fallo(f'versión {r["ver"]} ≠ {ESPERADA}')
    P = r['pruebas']
    for id_ in IDS:
        v = P.get('flag_' + id_)
        (bien if v is True else fallo)(f'championFlag({id_}) = {v!r}')
    DONE = '★ SUPERADO · rejuega cualquier etapa desde el mapa'
    mh = P.get('menuHint', '')
    if isinstance(mh, str) and mh.startswith('★ SUPERADO'):
        bien(f'menuHint() → «{mh}» (precedencia campeón)')
    else:
        fallo(f'menuHint() = {mh!r} ≠ {DONE!r}')
    STAGE5 = 'Etapa 5/5 · sigue donde la dejaste'
    v = P.get('stage_oeste_campeon')
    if v == STAGE5:
        bien('stage_oeste_campeon → «Etapa 5/5» (anuncio del Duelo FINAL; el campeón lo pisa abajo)')
    else:
        fallo(f'stage_oeste_campeon = {v!r}')
    res = P.get('resolucion_tarjeta_oeste', '')
    if isinstance(res, str) and res.startswith('★ SUPERADO'):
        bien(f'resolución de la TARJETA con campeón → «{res}» (championFlag pisa la etapa, c12 1671)')
    else:
        fallo(f'resolucion_tarjeta_oeste = {res!r}')
    for k in ('stage_locura_campeon',):
        v = P.get(k)
        (bien if v == '' else fallo)(f'{k} → callado (lo cubre el chip ★) = {v!r}')
    if P.get('flag_oeste_sin_clave') is False:
        bien('control negativo: sin clave champ → false (no hay flag clavado)')
    else:
        fallo(f'control negativo: flag_oeste_sin_clave = {P.get("flag_oeste_sin_clave")!r}')
    if P.get('flag_oeste_restaurado') is True:
        bien('clave restaurada → champion de nuevo true')
    else:
        fallo(f'flag_oeste_restaurado = {P.get("flag_oeste_restaurado")!r}')
    # ronda 24 · LEYENDA
    if P.get('flag_leyenda_oeste') is True:
        bien('leyendaFlag(oeste) con sello → true')
    else:
        fallo(f'flag_leyenda_oeste = {P.get("flag_leyenda_oeste")!r}')
    rl = P.get('resolucion_tarjeta_leyenda', '')
    if isinstance(rl, str) and rl.startswith('★ LEYENDA'):
        bien(f'resolución de la TARJETA con LEYENDA → «{rl}» (pisa a SUPERADO)')
    else:
        fallo(f'resolucion_tarjeta_leyenda = {rl!r}')
    if P.get('flag_leyenda_off') is False:
        bien('sin sello → leyendaFlag vuelve a false')
    else:
        fallo(f'flag_leyenda_off = {P.get("flag_leyenda_off")!r}')
    sf = P.get('storage_final') or {}
    esperado = {k: '1' for k in ('oeste', 'locura', 'magia', 'eo', 'valle')}
    if sf == esperado:
        bien('storage de los 5 campeones intacto tras las variantes')
    else:
        fallo(f'storage_final = {sf!r} ≠ {esperado!r}')
    if perr:
        fallo(f'pageerrors durante el arranque: {perr[:2]}')
    else:
        bien('0 pageerrors durante el arranque')

    print('✓ QA CHAMPION LISTO: VERDE' if ok else '✗ QA CHAMPION LISTO: FALLO')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
