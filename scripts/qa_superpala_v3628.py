#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.28 · SUPERPODERES DE PALA (capa X, estática + en vivo).

Reglas del dueño que esta capa defiende:
  1) CONCESIÓN: los superpoderes de pala SOLO se conceden superados los
     20 toques del jugador — NUNCA antes (toque 20 → IMÁN, 40 → EFECTO,
     60 → IMÁN… alternando; las faltas no cuentan como toque).
  2) SUPER IMÁN (10 s): ralentiza la bola del rival que viene y la dirige
     al CENTRO de nuestra pala; no actúa en nuestro saque ni fuera de
     rallye ni en las pruebas (Ark).
  3) SUPER EFECTO (10 s): SOLO entra al devolver un golpe del rival en el
     rallye — NUNCA sobre el saque (ni el nuestro: estado 'serve'; ni el
     del rival: isServeBall) — y SOLO se manifiesta en el bote sobre la
     mesa del RIVAL; la ventaja es siempre nuestra y el perjudicado
     siempre él. Pasados los 10 s, TODO vuelve a la normalidad.

Parte ESTÁTICA: anclas exactas en el fuente (c00/c04/c05/c06/c12) y en el
fichero servido. Parte EN VIVO: arranque sin pageerrors, cadencia de
concesión (19 no concede · 20 concede), reloj de 10 s y reset por partida.
Salida: RESULTADO: N OK · M fallos (contrato qa_todo)."""
import asyncio
import sys
import urllib.request
from pathlib import Path

from playwright.async_api import async_playwright

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src' / 'game' / 'core'
URL = "http://localhost:3000/game.html"

ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1

def lee(p):
    return Path(p).read_text(encoding='utf-8', errors='replace')

def ancla(txt, aguja, label):
    chk(aguja in txt, label)

def main_estatica():
    c00 = lee(SRC / 'c00_pre_three.js')
    c04 = lee(SRC / 'c04_fisica_ccd.js')
    c05 = lee(SRC / 'c05_colisiones_ia_golpeo.js')
    c06 = lee(SRC / 'c06_logros_stats_ia_rival.js')
    c12 = lee(SRC / 'c12_pingponggame.js')

    print('— ESTÁTICA · estado y reglas (c04) —')
    ancla(c04, 'const PP_SUPER = {', 'c04: estado PP_SUPER declarado')
    ancla(c04, 'UMBRAL: 20,', 'c04: concesión SOLO superados los 20 toques')
    ancla(c04, 'DURACION_S: 10,', 'c04: el poder dura 10 s')
    ancla(c04, 'notaToque()', 'c04: alimentado por toques válidos')
    ancla(c04, "activar(p) {", 'c04: activación con reloj')
    ancla(c04, "reset() {", 'c04: reset por partida')

    print('— ESTÁTICA · árbitro (c06) —')
    i_dbl = c06.find("dblhit")
    i_volley = c06.find("'volley'")
    i_nota = c06.find("PP_SUPER.notaToque()")
    chk(i_nota > 0 and i_nota > i_volley > i_dbl,
        'c06: notaToque SOLO tras las faltas (doble golpe/volea no cuentan)')
    chk("if (who === 'player') PP_SUPER.notaToque();" in c06,
        'c06: solo los toques del JUGADOR alimentan la concesión')
    i_start = c06.find('startMatch(mode)')
    i_reset = c06.find('PP_SUPER.reset();')
    chk(i_reset > i_start > 0, 'c06: startMatch renueva los poderes (reset)')

    print('— ESTÁTICA · bote con efecto (c05) —')
    ancla(c05, "if (ladoBote === 'ai' && ball.__spEfecto) {",
          'c05: el efecto SOLO se manifiesta en la mesa del RIVAL')
    chk("ladoBote === 'player' && ball.__spEfecto" not in c05,
        'c05: el bote en NUESTRA mesa nunca se altera (ventaja solo nuestra)')
    ancla(c05, "ball.__spEfecto = null;", 'c05: un bote gasta el efecto')
    ancla(c05, "vel.z *= 1.30; vel.y *= 0.62;", 'c05: TOPSPIN dispara baja y rápida')
    ancla(c05, "vel.z *= 0.52; vel.y *= 1.05;", 'c05: BACKSPIN frena y corta')

    print('— ESTÁTICA · guardas del dueño (c12) —')
    ancla(c12, "PP_SUPER.iman() && this.rules.state === 'rally' && !this.tossed",
          'c12: IMÁN solo en rallye y jamás en nuestro saque')
    ancla(c12, "PP_SUPER.efecto() && this.rules.lastHitter === 'ai'",
          'c12: EFECTO solo devolviendo golpes del rival')
    ancla(c12, "!this.rules.isServeBall",
          'c12: EFECTO nunca sobre el saque del rival (isServeBall fuera)')
    ancla(c12, "PP_SUPER.pendiente", 'c12: concesión anunciada por el juego')
    ancla(c12, "PP_SUPER.activar(poder);", 'c12: el reloj de 10 s arranca al conceder')
    ancla(c12, "this.ballMesh.material.emissive.setHex(0x555044)",
          'c12: agotado el poder la bola vuelve a su tinta base')
    ancla(c12, "if (this.rules.state !== 'rally' && this.ball.__spEfecto) this.ball.__spEfecto = null;",
          'c12: fuera de rallye no queda rastro del efecto')

    print('— ESTÁTICA · i18n (c00) —')
    ancla(c00, "sp_iman: '¡SUPER IMÁN!", 'c00: cartel ES del imán')
    ancla(c00, "sp_efecto: '¡SUPER EFECTO!", 'c00: cartel ES del efecto')
    ancla(c00, "sp_fin: 'Poderes agotados · juego normal',", 'c00: cartel ES de caducidad')
    ancla(c00, "sp_iman: 'SUPER MAGNET!", 'c00: cartel EN del imán')
    ancla(c00, "sp_efecto: 'SUPER SPIN!", 'c00: cartel EN del efecto')
    ancla(c00, "sp_fin: 'Powers spent · normal game',", 'c00: cartel EN de caducidad')


async def main_viva():
    global ok, fails
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)
        await page.evaluate("() => { window.__wantSolverHook = true; }")
        await page.wait_for_timeout(1200)

        r = await page.evaluate("""() => {
          const H = window.__solverHook;
          if (!H || !H.PP_SUPER) return { hook: false };
          const P = H.PP_SUPER;
          const out = { hook: true };
          out.consts = { umbral: P.UMBRAL, cadencia: P.CADENCIA, dur: P.DURACION_S };
          out.arranque = { pendiente: P.pendiente, iman: P.iman(), efecto: P.efecto(),
                           toques: P.toques };
          // cadencia: 19 toques NO conceden (no antes de 20)
          for (let i = 0; i < 19; i++) P.notaToque();
          out.a19 = { toques: P.toques, pendiente: P.pendiente };
          // toque 20 → IMÁN
          P.notaToque();
          out.a20 = { toques: P.toques, pendiente: P.pendiente };
          // el juego consumiría: activar + limpiar
          const imanDur = (() => {
            P.activar(P.pendiente); P.pendiente = null;
            const d = P.imanHasta - performance.now() / 1000;
            return d;
          })();
          out.imanDur = imanDur;
          out.imanActivo = P.iman();
          out.efectoActivoTrasIman = P.efecto();
          // 19 más no conceden; el 40 → EFECTO
          for (let i = 0; i < 19; i++) P.notaToque();
          out.a39 = { pendiente: P.pendiente };
          P.notaToque();
          out.a40 = { pendiente: P.pendiente };
          const imanHastaPre = P.imanHasta;
          P.activar(P.pendiente); P.pendiente = null;
          out.efectoDur = P.efectoHasta - performance.now() / 1000;
          out.efectoActivo = P.efecto();
          out.imanHastaIntacto = (P.imanHasta === imanHastaPre);
          // reset de partida: todo a cero y nada concedido
          P.reset();
          out.reset = { toques: P.toques, proximo: P.proximo, pendiente: P.pendiente,
                        iman: P.iman(), efecto: P.efecto() };
          return out;
        }""")

        print('— EN VIVO · arranque —')
        chk(r.get('hook'), 'hook QA expuesto (__solverHook.PP_SUPER)')
        chk(len(errors) == 0, f'sin pageerrors ({len(errors)})')
        if not r.get('hook'):
            return
        c = r['consts']
        chk(c['umbral'] == 20 and c['cadencia'] == 20,
            f'constantes de concesión 20/20 (umbral {c["umbral"]}, cadencia {c["cadencia"]})')
        chk(c['dur'] == 10, f'duración del poder = 10 s ({c["dur"]})')
        a = r['arranque']
        chk(not a['pendiente'] and not a['iman'] and not a['efecto'] and a['toques'] == 0,
            'arranque limpio: nada concedido antes de tiempo')
        chk(r['a19']['pendiente'] is None and r['a19']['toques'] == 19,
            'a 19 toques NADA concedido (no antes de los 20)')
        chk(r['a20']['pendiente'] == 'iman' and r['a20']['toques'] == 20,
            'al toque 20 se concede el SUPER IMÁN')
        chk(9.5 <= r['imanDur'] <= 10.5,
            f'reloj del imán: 10 s desde la activación ({r["imanDur"]:.2f} s)')
        chk(r['imanActivo'] and not r['efectoActivoTrasIman'],
            'imán activo no enciende el efecto (poderes independientes)')
        chk(r['a39']['pendiente'] is None, 'a 39 toques todavía nada (cadencia 20)')
        chk(r['a40']['pendiente'] == 'efecto', 'al toque 40 se concede el SUPER EFECTO')
        chk(9.5 <= r['efectoDur'] <= 10.5,
            f'reloj del efecto: 10 s desde la activación ({r["efectoDur"]:.2f} s)')
        chk(r['efectoActivo'] and r['imanHastaIntacto'],
            'efecto activo no toca el reloj del imán (poderes independientes)')
        q = r['reset']
        chk(q['toques'] == 0 and q['proximo'] == 20 and q['pendiente'] is None
                and not q['iman'] and not q['efecto'],
            'reset de partida: contador y poderes a cero')

        # fichero servido: las guardas del dueño viajan al Quest
        srv = await page.content()
        ancla(srv, "PP_SUPER.iman() && this.rules.state === 'rally' && !this.tossed",
              'servido: guarda del IMÁN (rallye, jamás nuestro saque)')
        ancla(srv, "PP_SUPER.efecto() && this.rules.lastHitter === 'ai'",
              'servido: guarda del EFECTO (solo devoluciones al rival)')
        ancla(srv, "ladoBote === 'ai' && ball.__spEfecto",
              'servido: bote con efecto SOLO en mesa rival')
        ancla(srv, 'DURACION_S: 10,', 'servido: 10 s de vida del poder')
        ancla(srv, 'sp_iman', 'servido: cartel del imán viaja i18n')

        await browser.close()


def main():
    print('=' * 68)
    print('QA v3.6.28 · SUPERPODERES DE PALA (20 toques · imán · efecto 10 s)')
    print('=' * 68)
    main_estatica()
    try:
        asyncio.run(main_viva())
    except Exception as e:
        print(f'  ✗ FALLO: capa en vivo no pudo ejecutarse: {e}')
        globals()['fails'] = globals()['fails'] + 1
    print('-' * 68)
    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(0 if fails == 0 else 1)


if __name__ == '__main__':
    main()
