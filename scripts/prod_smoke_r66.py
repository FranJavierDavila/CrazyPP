#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r66.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 160
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.157-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva la FASE 160 (BOLA LOCA con sus
    parámetros EXACTOS del mago · regla SOLO 1 SUPERPODER EN MARCHA con
    _poderVivoAlguno y los DOS gatillos · siembra de serie · surto sin la
    vieja loca · galería que ABRE en bolaloca · i18n ES/EN) y la
    conservación r65 (blindaje del saque: _srvManoValida · watchdog
    bola→mano) + sw/portada a 3.6.157 + hub a v36157-sdk6.
  · FUNCIONAL: el juego VIVO — la regla decide en vivo (bola loca activa
    BLOQUEA el efecto sin consumo · refresco del mismo permitido · fin
    natural con restauración ×1.65) y _srvManoValida decide (mano cerca →
    true · lejos → false). Restauración honesta del localStorage.
Uso: python3 scripts/prod_smoke_r66.py"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.157-SDK6'

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const G = window.__PP_GAME || window.__pingpong;
  const out = { presente: !!G };
  if (!G) return out;
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  // — r66 · LA REGLA SOLO-1 DECIDE EN VIVO —
  try {
    const libre = (G.paddleHand === 0) ? 1 : 0;
    G.palaMejorada = true;
    try { G.rules.startMatch('match'); } catch (e) { /* */ }
    G.champs.activeId = 'locura';
    G.rules.state = 'rally';
    const entB = { id: 'bolaloca', n: 1 };
    const entE = { id: 'efecto', n: 1 };
    G._megaMatriz.length = 0;
    G._megaMatriz.push(entB, entE);
    G._megaIdx = 0;
    out.activa = G.megaTrigger(libre) === true && G._bolalocaT > 9.5;
    out.crece = Math.abs(G.ballMesh.scale.x - 1.65) < 1e-6;
    out.vivo = G._poderVivoAlguno() === 'bolaloca';
    G._megaIdx = 1;
    const nE = entE.n;
    out.bloquea = G.megaTrigger(libre) === true && G._efectoT === 0 &&
      entE.n === nE;
    const entB2 = { id: 'bolaloca', n: 1 };
    G._megaMatriz.push(entB2);
    G._megaIdx = G._megaMatriz.indexOf(entB2);
    const tA = G._bolalocaT;
    out.refresca = G.megaTrigger(libre) === true && G._bolalocaT >= tA;
    for (let i = 0; i < 240 && G._bolalocaT > 0; i++) {
      try { G.updateMega(0.05); } catch (e) { /* */ }
      await dorme(1);
    }
    out.finYRestaura = G._bolalocaT === 0 &&
      Math.abs(G.ballMesh.scale.x - 1) < 1e-6 && G._bolalocaFx === null;
    // desbloqueo de serie en producción
    try { localStorage.removeItem('pp_poderes_v1'); } catch (e) { /* */ }
    out.siembra = G.poderesDesbloqueados().indexOf('bolaloca') === 0;
    try { localStorage.removeItem('pp_poderes_v1'); } catch (e) { /* */ }
    G._megaMatriz.length = 0; G._megaIdx = 0; G._megaIcon = null;
    G._megaActivaId = null; G.champs.activeId = '';
  } catch (e) { out.errRegla = String(e); }
  // — r65 · EL BLINDAJE DEL SAQUE SIGUE DECIDIENDO (_srvManoValida) —
  try {
    const V3 = G.camera.position.constructor;
    const cerca = { active: true, pos: G.camera.position.clone().add(
      new V3(0.12, -0.25, -0.30)) };
    out.manoCerca = G._srvManoValida(cerca) === true;
    const lejos = { active: true, seenT: performance.now(),
      pos: G.camera.position.clone().add(new V3(0, 0, 2.6)) };
    out.manoLejos = G._srvManoValida(lejos) === false;
  } catch (e) { out.errSaque = String(e); }
  return out;
}"""


async def main():
    # ESTÁTICO
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html de producción:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        # FASE 160 · la BOLA LOCA servida
        ("{ id: 'bolaloca', dur: ARCANO_CFG.ventanas.bolaloca, nombre: () => T('poder_bolaloca'),",
         'registro: entrada BOLA LOCA (15.º poder)'),
        ('const BOLALOCA_SCALE = 1.65;', 'bola ×1,65 (el mago)'),
        ('const BOLALOCA_HUE_V = 0.30;', 'ciclo de color 0,30 (el mago)'),
        ('const BOLALOCA_SWAY = 4.0;', 'vaivén 4 m/s² (el mago)'),
        ('const BOLALOCA_JT = 0.22;', 'ráfagas cada 0,22 s (el mago)'),
        ('_poderVivoAlguno()', 'regla: helper solo-1'),
        ('REGLA DEL DUEÑO: SOLO 1 superpoder de pala en marcha', 'regla: gate del megaTrigger'),
        ('vivoDL && vivoDL !== idPend) return false', 'regla: gate del _dlTrigger'),
        ('BOLA LOCA SIEMPRE DESBLOQUEADA', 'siembra de serie'),
        ("filter((id) => id !== 'loca')", 'surto sin la vieja loca'),
        ('PODERES_PALA.findIndex', 'galería que ABRE en bolaloca'),
        ("dl_bolaloca: 'BOLA LOCA',", 'i18n ES duelos'),
        ("poder_uno_activo: 'Ya hay un superpoder activo · espera a que termine',",
         'i18n ES de la regla'),
        ("poder_uno_activo: 'A superpower is already active · wait for it to end',",
         'i18n EN de la regla'),
        # conservación r65
        ('LA BOLA SIEMPRE VUELVE A TU MANO', 'conservación r65: watchdog del saque'),
        ('_srvManoValida(bh) {', 'conservación r65: pose fresca + plausible'),
        # sello de versión
        ("const VERSION = '3.6.157-SDK6'", 'sello c00 a 3.6.157'),
    ]:
        chk(needle in game, label)
    chk(game.count('data:image/png;base64,') >= 15,
        'iconos del registro completo embebidos')
    # sw + hub
    try:
        sw = get(BASE + '/sw.js')
        chk("const CACHE = 'crazypp-v3.6.157-SDK6'" in sw, 'sw.js a 3.6.157')
    except Exception as e:
        chk(False, f'sw.js servido ({e})')
    try:
        hub = get(BASE + '/descargas')
        chk('v36157-sdk6' in hub and 'V3.6.157-SDK6' in hub,
            'hub /descargas apunta a v36157 (titular FASE 160)')
    except Exception as e:
        chk(False, f'hub /descargas ({e})')

    # FUNCIONAL
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on('pageerror', lambda e: errors.append(str(e)))
        try:
            await page.goto(URL, wait_until='domcontentloaded', timeout=90000)
            await page.wait_for_timeout(9000)
            rt = await page.evaluate(JS)
        except Exception as e:
            print('✗ El juego de producción no arrancó:', e)
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            await browser.close()
            sys.exit(1)
        await browser.close()

    for k in ['presente', 'activa', 'crece', 'vivo', 'bloquea', 'refresca',
              'finYRestaura', 'siembra', 'manoCerca', 'manoLejos']:
        chk(rt.get(k) is True, 'en vivo: ' + k)
    for k in ['errRegla', 'errSaque']:
        if rt.get(k):
            chk(False, f'en vivo: {k} = {rt[k]}')
    chk(not errors, f'sin pageerrors ({len(errors)})')
    if errors:
        print('   pageerrors:', errors[:3])

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
