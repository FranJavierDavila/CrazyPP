#!/usr/bin/env python3
"""QA r97 · EL BUNDLE SE EJECUTA — la capa que faltaba (la lección del bloqueo
r93-r96: los arneses de agujas leen TEXTO y los módulos fuente, pero el bundle
ENSAMBLADO de producción nunca se ejecutaba; un TypeError por frame
(crossVectors sobre Quaternion) pasó 4 rondas invisible porque el ESCUDO DEL
BUCLE lo tragaba — «menú vivo pero gatillos muertos» en el casco).

Este arnés sirve public/ TAL CUAL (el artefacto desplegable), arranca el juego
REAL y exige:
  A · CERO líneas «escudo del bucle» en consola (el escudo JAMÁS traga nada)
  B · cero pageerrors / cero «Uncaught»
  C · el vigía r96/r97 expuesto y operativo (window.__PP_VIGIA.suelta)
  D · flujo hall→JUGAR completo: state serve · menú cerrado
  E · LOS BRAZOS TRABAJAN DE VERDAD: agarre mano↔mango medido en vivo (el
      driver de la muñeca anatómica ejecuta su base ortonormal — el punto
      EXACTO donde r95 rompió) + temblor de reposo acotado.

Uso: python3 scripts/qa_bundle_r97.py   (arranca y mata su propio servidor)
"""
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright

RAIZ = Path('/home/z/my-project')
PUERTO = 8779
BASE = f'http://localhost:{PUERTO}'
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


def version_repo():
    return json.loads((RAIZ / 'src/game/VERSION.json').read_text())['version']


async def main():
    ver = version_repo()
    srv = subprocess.Popen(
        [sys.executable, '-m', 'http.server', str(PUERTO), '-d', str(RAIZ / 'public')],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(2.0)
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader', '--disable-background-timer-throttling',
                  '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows'])
            page = await browser.new_page(viewport={'width': 1280, 'height': 800})
            consola = []
            page.on('console', lambda m: consola.append(m.text))
            errores = []
            page.on('pageerror', lambda e: errores.append(str(e)))

            print('== A · BOOT DEL BUNDLE DE PRODUCCIÓN ==')
            await page.goto(BASE + '/game.html?cb=' + str(int(time.time())),
                            wait_until='domcontentloaded')
            await page.wait_for_function(
                "() => window.__PP_GAME && window.__PP_VERSION", timeout=60000)
            ver_viva = await page.evaluate("window.__PP_VERSION || ''")
            chk(ver_viva == ver, f'versión viva = {ver_viva!r} (repo {ver!r})')
            # el GLB de brazos carga ASÍNCRONO (decode 4-5 MB en SwiftShader)
            await page.wait_for_function(
                "() => window.__PP_GAME.aiArmGlb && window.__PP_GAME.aiArmGlb.listo"
                " && window.__PP_GAME.aiArmGlb.brazos && window.__PP_GAME.aiArmGlb.brazos.length",
                timeout=45000)
            glb = await page.evaluate('() => window.__PP_GAME.aiArmGlb.listo')
            chk(glb is True, f'GLB de brazos cargado (listo={glb})')

            escudo = [c for c in consola if 'escudo del bucle' in c]
            chk(not escudo, f'CERO líneas de «escudo del bucle» ({len(escudo)})'
                + (f' → 1.ª: {escudo[0][:130]!r}' if escudo else ''))
            chk(not errores, f'CERO pageerrors ({len(errores)})'
                + (f' → {errores[0][:130]!r}' if errores else ''))
            uncaught = [c for c in consola if 'Uncaught' in c]
            chk(not uncaught, f'CERO «Uncaught» en consola ({len(uncaught)})')

            print('== C · VIGÍA EXPUESTO ==')
            vigia = await page.evaluate(
                "() => !!(window.__PP_VIGIA && typeof window.__PP_VIGIA.suelta === 'function')")
            chk(vigia, 'window.__PP_VIGIA.suelta instalado (el escudo tiene canal)')
            if vigia:
                await page.evaluate(
                    "() => window.__PP_VIGIA.suelta({ e: 'probe_vigia_r97' })")
                persistido = await page.evaluate(
                    "() => !!localStorage.getItem('ppxr_probe_vigia_r97')")
                chk(persistido, 'suelta() persiste en localStorage del visor')

            print('== E · BRAZOS EN REPOSO (el driver ejecuta su base — ANTES del JUGAR) ==')
            # el switchMode reconstruye la escena: el GLB se remonta ASÍNCRONO
            await page.wait_for_function(
                "() => window.__PP_GAME.aiArmGlb && window.__PP_GAME.aiArmGlb.listo"
                " && window.__PP_GAME.aiArmGlb.brazos && window.__PP_GAME.aiArmGlb.brazos.length",
                timeout=20000)
            await page.evaluate("""() => {
              const gg = window.__PP_GAME, RR = gg.aiArmGlb;
              const V = gg.aiPaddleMesh.position.constructor;
              window.__qa97 = { RR, gg, V,
                // AMBOS brazos: uno lleva la pala (agarre ~0) y el otro es el
                // brazo libre (bota la bola en la demo — distancia grande y
                // legítima). El INVARIANTE: la mano de la pala SIEMPRE en el
                // mango, incluso a mitad de un golpeo.
                mide() {
                  RR.root.updateMatrixWorld(true);
                  const eje = new V(0, 1, 0).applyQuaternion(gg.aiPaddleMesh.quaternion);
                  const mango = gg.aiPaddleMesh.position.clone().addScaledVector(eje, -0.1303);
                  const grips = RR.brazos.map((b) => {
                    const mano = new V().setFromMatrixPosition(b.mano.matrixWorld);
                    return mano.distanceTo(mango) * 1000;
                  });
                  return { grip_mm: Math.min(...grips), grips,
                    nan: grips.some((g) => g !== g) };
                } };
            }""")
            grips = []
            for _ in range(8):
                g = await page.evaluate("() => window.__qa97.mide()")
                grips.append(g)
                await page.wait_for_timeout(700)
            nan = any(g['nan'] for g in grips)
            grip0 = grips[0]['grip_mm']
            grip_max = max(g['grip_mm'] for g in grips)
            chk(len(grips) >= 8, f'muestreo brazos completado ({len(grips)} medidas CDP)')
            chk(not nan, 'sin NaN en las medidas')
            chk(grip0 < 10.0,
                f'agarre AL MONTAR = {grip0:.1f} mm (<10: la mano NACE exacta en el '
                'mango — el ancla r95 se construye: el punto EXACTO donde r95 rompía '
                'con el TypeError)')
            chk(grip_max < 120.0,
                f'seguimiento acotado (máx {grip_max:.1f} mm: el filtro OneEuro persigue '
                'al golpeo de la demo SIN explosiones ni NaN)')
            print(f'    · grip del brazo de la pala: {[round(g["grip_mm"], 1) for g in grips]}')
            print('== D · FLUJO HALL→JUGAR (el del dueño) ==')
            await page.evaluate("() => window.__PP_GAME.enterHall()")
            await page.wait_for_timeout(1200)
            await page.evaluate("""() => {
              const gg = window.__PP_GAME;
              gg.closeTrainingV3();
              if (gg.calibPala) gg.exitCalib();
              if (gg.champs) gg.champs.leaveAll();
              gg.exitHall();
              gg.doblesActivo = false;
              if (gg.mode !== 'match') gg.switchMode('match');
              else { gg.rules.bestOf = 5; gg.rules.startMatch('match'); gg.resetToss(); }
              gg.closeMenu();
            }""")
            await page.wait_for_timeout(1500)
            estado = await page.evaluate(
                "() => window.__PP_GAME.rules.state + '/' + window.__PP_GAME.rules.server")
            chk(estado == 'serve/player', f'partido servido: {estado}')
            menu_abierto = await page.evaluate('() => window.__PP_GAME.menuOpen')
            chk(menu_abierto is False, 'menú cerrado tras JUGAR')
            escudo2 = [c for c in consola if 'escudo del bucle' in c]
            chk(not escudo2, f'CERO escudo tras el arranque del partido ({len(escudo2)})'
                + (f' → 1.ª: {escudo2[0][:130]!r}' if escudo2 else ''))

            escudo3 = [c for c in consola if 'escudo del bucle' in c]
            chk(not escudo3, f'CERO escudo durante el muestreo ({len(escudo3)})'
                + (f' → 1.ª: {escudo3[0][:130]!r}' if escudo3 else ''))

            await browser.close()
    finally:
        srv.terminate()
    print(f'\nQA BUNDLE r97 ({ver}) · {ok} OK · {fails} FALLOS')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
