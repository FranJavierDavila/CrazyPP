#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · ronda 20 · QA DE LOS HINTS DEL HUB (ronda 19) EN VIVO
=======================================================================
Carga game.html de PRODUCCIÓN en Chromium headless, inyecta el estado real
del dueño en localStorage ANTES de que corra el juego (pp_tele=0: el bot no
contamina D1) y afirma el comportamiento de ChampLoader._stageHint y
menuHint() — la lógica «TU CAMINO TE ESPERA»:

  · oeste 3/5 (estado real del dueño)     → «Etapa 3/5 · sigue donde la…»
  · locura pp_arcade_stage=2 (récord)     → «Etapa 3/5 · …»
  · etapa de SALIDA (oeste 1 / resto 0)   → '' (no es progreso)
  · locura stage=5 (marcador de campeón)  → '' (lo cubre el chip ★)
  · magia sin registro                    → ''
  · oeste 5/5                             → «Etapa 5/5 · …»
  · menuHint() con locura/oeste con progreso → devuelve etapa, no victorias
  · 0 pageerrors durante el arranque

Uso: python3 scripts/qa_hub_hints.py [versión-esperada]  (default 3.6.16-SDK6)
"""
import asyncio
import sys

URL = 'https://franjavierdavila.github.io/CrazyPP/game.html'
ESPERADA = sys.argv[1] if len(sys.argv) > 1 else '3.6.16-SDK6'

ESTADO = {
    'pp_tele': '0',                       # el bot NO deja huella en D1
    'pp_champ_oeste_stage': '3',          # estado REAL del dueño (Task 117)
    'pp_arcade_stage': '2',               # récord de La Locura (stage n=2)
    'pp_champ_magia_stage': '0',          # salida: no se anuncia
}


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
            "try { for (const [k, v] of Object.entries(" + repr(ESTADO).replace("'", '"') + ")) localStorage.setItem(k, v); "
            "localStorage.removeItem('pp_champ_oeste_champ'); localStorage.removeItem('pp_arcade_trophy'); } catch (e) {}"
        )
        await page.goto(URL, wait_until='domcontentloaded', timeout=60_000)
        # v2: espera FIJA 25 s (el patrón del debug que funcionó) + poll hasta 50 s más
        await page.wait_for_timeout(25_000)
        # espera al puente window.__game.champs (módulo privado → sólo el puente)
        for _ in range(100):
            if await page.evaluate("() => !!(window.__game && window.__game.champs && window.__game.champs._stageHint)"):
                break
            await page.wait_for_timeout(500)
        else:
            ver = await page.evaluate("() => window.__PP_VERSION || null")
            print(f'✗ FALLO: window.__game.champs no llegó a tiempo · ver={ver}')
            print(f'  pageerrors capturados: {perr[:5] if perr else "ninguno"}')
            diagnostico = await page.evaluate("() => ({game: !!window.__game, champs: !!(window.__game && window.__game.champs), core: !!window.__PP_CORE, world: !!window.__PP_WORLD, gun: !!window.__gunLoaded})")
            print(f'  window: {diagnostico}')
            await browser.close()
            return 1
        await page.wait_for_timeout(2_000)

        r = await page.evaluate("""() => {
          const CH = window.__game.champs;
          const g = (k) => localStorage.getItem(k);
          const out = { ver: window.__PP_VERSION || null, lang: null, pruebas: {} };
          out.lang = (window.__PP_CORE && window.__PP_CORE.lang) ? window.__PP_CORE.lang() : '?';
          const P = (nombre, fn) => { try { out.pruebas[nombre] = fn(); } catch (e) { out.pruebas[nombre] = 'EXC: ' + e; } };
          // estado real del dueño SIN tocar storage
          P('oeste_3', () => CH._stageHint('oeste', 'pp_champ_oeste_'));
          P('locura_2', () => CH._stageHint('locura', 'pp_arcade_'));
          P('magia_0', () => CH._stageHint('magia', 'pp_champ_magia_'));
          P('sin_registro', () => CH._stageHint('estacion_orbital', 'pp_champ_estacion_orbital_'));
          // variantes simuladas (escribe, prueba, deja el estado real de nuevo)
          const set = (k, v) => { v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); };
          set('pp_champ_oeste_stage', '1'); P('oeste_1_salida', () => CH._stageHint('oeste', 'pp_champ_oeste_'));
          set('pp_champ_oeste_stage', '5'); P('oeste_5_final', () => CH._stageHint('oeste', 'pp_champ_oeste_'));
          set('pp_champ_oeste_stage', '9'); P('oeste_9_corrupto', () => CH._stageHint('oeste', 'pp_champ_oeste_'));
          set('pp_champ_oeste_stage', '3');
          set('pp_arcade_stage', '5');      P('locura_5_campeon', () => CH._stageHint('locura', 'pp_arcade_'));
          set('pp_arcade_stage', '2');
          P('menuHint', () => CH.menuHint());
          P('storage_oeste', () => g('pp_champ_oeste_stage'));
          P('storage_locura', () => g('pp_arcade_stage'));
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
    HINT3 = 'Etapa 3/5 · sigue donde la dejaste'
    if P.get('oeste_3') == HINT3:
        bien(f'oeste 3/5 (estado real del dueño) → «{P["oeste_3"]}»')
    else:
        fallo(f'oeste_3 = {P.get("oeste_3")!r} ≠ {HINT3!r}')
    if P.get('locura_2') == HINT3:
        bien('locura 2→3/5 (récord) → ok')
    else:
        fallo(f'locura_2 = {P.get("locura_2")!r}')
    for k, esperado in (('magia_0', ''), ('sin_registro', ''), ('oeste_1_salida', ''),
                        ('oeste_9_corrupto', ''), ('locura_5_campeon', '')):
        if P.get(k) == esperado:
            bien(f'{k} → callado (correcto)')
        else:
            fallo(f'{k} = {P.get(k)!r} ≠ \'\'')
    if P.get('oeste_5_final') == 'Etapa 5/5 · sigue donde la dejaste':
        bien('oeste 5/5 → anuncia el DUELO FINAL')
    else:
        fallo(f'oeste_5_final = {P.get("oeste_5_final")!r}')
    mh = P.get('menuHint', '')
    if isinstance(mh, str) and mh.startswith('Etapa 3/5'):
        bien(f'menuHint() → «{mh}» (etapa antes que victorias)')
    else:
        fallo(f'menuHint() = {mh!r}')
    if P.get('storage_oeste') == '3' and P.get('storage_locura') == '2':
        bien('storage del dueño restaurado intacto tras las variantes')
    else:
        fallo(f'storage final: oeste={P.get("storage_oeste")!r} locura={P.get("storage_locura")!r}')
    if perr:
        fallo(f'pageerrors durante el arranque: {perr[:2]}')
    else:
        bien('0 pageerrors durante el arranque')

    print('✓ QA HUB HINTS: VERDE' if ok else '✗ QA HUB HINTS: FALLO')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
