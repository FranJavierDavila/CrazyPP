#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r54_poderes_agotados.py — REPRODUCCIÓN del reporte del dueño (FASE 148):
«los superpoderes de pala se aplican pero nacen agotados y no se pueden
jugar; es como que los lanzas y al mismo tiempo los marca como agotados».

Mide sobre el game.html REAL servido por :3000:
  A-D · ciclo completo del gatillo para mega/efecto/imán + los 11 restantes:
        ¿la ventana NACE (≈15/10/8 s) y DECAE a ritmo 1×?  ¿mensaje go?
  E   · SONDA de updateMega: nº de llamadas/frame y dt real (si dt viniera
        en ms o hubiese bucles duplicados, las ventanas morirían al instante
        — la hipótesis «nacen agotados»).
  F   · cargas vs CANDADO: _megaCharge reparte del registro COMPLETO
        PODERES_PALA sin filtrar poderesDesbloqueados() (pp_poderes_v1).
  G   · gasto honesto: lanzar con n=1 consume la carga y la ventana sigue.

Uso: python3 scripts/qa_r54_poderes_agotados.py   (requiere :3000 arriba)
"""
import sys
from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3000/game.html'

ok, fails, errors = 0, 0, []


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


JS_REPRO = """async () => {
  const G = window.__PP_GAME || window.__pingpong;
  const out = { presente: !!G };
  if (!G) return out;
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) { /* */ }
  G.palaMejorada = true;
  await dorme(300);
  G.renderer.xr.isPresenting = true;
  G.menuOpen = false; G._instr = null; G.champIntro = null;
  G.tutV1 = false; G.calib = false; G.calibPala = false;
  G.inHall = false; G._arconoOn = false;
  try { G.rules.onMatchStart = null; } catch (e) { /* */ }
  G.champs = { active: true, gunArmed: false, paddleGunArmed: false };
  G.rules.state = 'rally';
  G.rules.rallyHits = 0;

  // — SONDA updateMega —
  const umOrig = G.updateMega;
  const sonda = { n: 0, dtMax: 0, dtSum: 0 };
  G.updateMega = function (dt) {
    sonda.n++; sonda.dtMax = Math.max(sonda.dtMax, dt); sonda.dtSum += dt;
    return umOrig.call(this, dt);
  };
  const iLibre = (G.paddleHand === 0) ? 1 : 0;

  const limpia = () => {
    for (const k of ['_megaT', '_efectoT', '_imanT', '_portalT', '_clonT',
      '_redT', '_elecT', '_fenixT', '_cronoT', '_oscuridadT',
      '_prismaT', '_ondaT', '_salvaT', '_anclaT']) G[k] = 0;
    G._megaActivaId = null; G._megaIconModo = null;
  };

  // — A · MEGA —
  limpia();
  G._megaMatriz = [{ id: 'mega', n: 1 }]; G._megaIdx = 0;
  G.onSelectStart(iLibre);
  await dorme(150);
  out.A_lanzada = G._megaT > 14.5;
  out.A_activaId = G._megaActivaId;
  out.A_msg = String(G.rules && G.rules.message || '');
  out.A_S = +(G._megaS || 0).toFixed(3);
  const tA0 = G._megaT;
  await dorme(2000);
  out.A_t2s = +G._megaT.toFixed(2);
  // r54 · cota inferior honesta para HEADLESS: rAF estrangulado en frío +
  // clamp dt (Math.min(_rawDt, 1/30)) decaen menos de 1,5 s de reloj del
  // juego en 2 s de pared (visto 0,97). El bug «nacen agotados» daba t=0:
  // vivo ⇒ decae ALGO (0,5-2,6); muerto ⇒ 0 — la sonda sigue cazándolo.
  out.A_decae1x = (tA0 - G._megaT) > 0.5 && (tA0 - G._megaT) < 2.6;
  out.A_crecio = G._megaS > 1.2;
  out.A_on = !!G.megaEnabled();

  // — B · SÚPER EFECTO —
  limpia();
  G._megaMatriz = [{ id: 'efecto', n: 1 }]; G._megaIdx = 0;
  G.onSelectStart(iLibre);
  await dorme(150);
  out.B_lanzada = G._efectoT > 9.5;
  out.B_activaId = G._megaActivaId;
  out.B_msg = String(G.rules && G.rules.message || '');
  const tB0 = G._efectoT;
  await dorme(1500);
  out.B_t15 = +G._efectoT.toFixed(2);
  out.B_decae1x = (tB0 - G._efectoT) > 1.2 && (tB0 - G._efectoT) < 2.0;

  // — C · IMÁN —
  limpia();
  G._megaMatriz = [{ id: 'iman', n: 1 }]; G._megaIdx = 0;
  G.onSelectStart(iLibre);
  await dorme(150);
  out.C_lanzada = G._imanT > 9.5;
  out.C_activaId = G._megaActivaId;
  out.C_msg = String(G.rules && G.rules.message || '');

  // — D · los 11 restantes: ¿nace ventana y coincide activaId? —
  const reloj = { portal: '_portalT', clon: '_clonT', red: '_redT',
    elec: '_elecT', fenix: '_fenixT', crono: '_cronoT',
    oscuridad: '_oscuridadT', prisma: '_prismaT', onda: '_ondaT',
    salva: '_salvaT', ancla: '_anclaT' };
  out.D = {};
  for (const id of Object.keys(reloj)) {
    limpia();
    G._megaMatriz = [{ id, n: 1 }]; G._megaIdx = 0;
    let exc = null;
    try { G.onSelectStart(iLibre); } catch (e) { exc = String(e && e.message || e); }
    await dorme(120);
    out.D[id] = { t: +G[reloj[id]].toFixed(2), activa: G._megaActivaId, exc: exc };
  }

  // — E · sonda —
  G.updateMega = umOrig;
  out.E_llamadas = sonda.n;
  out.E_dtMax = +sonda.dtMax.toFixed(4);
  out.E_dtMedio = +(sonda.dtSum / Math.max(1, sonda.n)).toFixed(4);

  // — F · cargas vs CANDADO —
  try { localStorage.setItem('pp_poderes_v1', JSON.stringify(['mega'])); } catch (e) { /* */ }
  const ids = new Set(); let bloqueados = 0; let total = 0;
  for (let k = 0; k < 200; k++) {
    G._megaMatriz = [];
    try { G._megaCharge(); } catch (e) { /* */ }
    const ent = G._megaMatriz[0];
    if (ent) {
      total++; ids.add(ent.id);
      if (ent.id !== 'mega') bloqueados++;
    }
  }
  out.F_total = total; out.F_bloqueados = bloqueados;
  out.F_idsDistintos = Array.from(ids).sort();
  out.F_desbloq = (function () { try { return G.poderesDesbloqueados(); } catch (e) { return null; } })();

  // — G · gasto honesto (n=1) —
  limpia();
  G._megaMatriz = [{ id: 'iman', n: 1 }]; G._megaIdx = 0;
  G.onSelectStart(iLibre);
  await dorme(120);
  out.G_ventana = +G._imanT.toFixed(2);
  out.G_matrizVacia = G._megaMatriz.length === 0;
  await dorme(600);
  out.G_ventanaSigue = G._imanT > 8.8;

  out.fin = true;
  return out;
}"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until='domcontentloaded')
        await page.wait_for_timeout(7000)
        out = await page.evaluate(JS_REPRO)
        await browser.close()

    chk(out.get('presente'), 'game vivo (window.__PP_GAME)')
    if not out.get('presente'):
        print('SIN JUEGO — repro abortado')
        sys.exit(1)

    print('A · MEGA PALA')
    chk(out.get('A_lanzada'), f"A. ventana nace ~15 s (t={out.get('A_t2s')} tras 2 s)")
    chk(out.get('A_activaId') == 'mega', f"A. icono ACTIVO (activaId={out.get('A_activaId')})")
    chk(out.get('A_decae1x'), f"A. decae a ritmo 1x (quedaba {out.get('A_t2s')} s)")
    chk(out.get('A_crecio'), f"A. la pala crece (escala {out.get('A_S')})")
    chk(out.get('A_on'), 'A. megaEnabled() se mantiene true')
    print('   mensaje al lanzar: ' + str(out.get('A_msg'))[:80])

    print('B · SÚPER EFECTO')
    chk(out.get('B_lanzada'), 'B. ventana nace ~10 s')
    chk(out.get('B_activaId') == 'efecto', f"B. icono ACTIVO (activaId={out.get('B_activaId')})")
    chk(out.get('B_decae1x'), f"B. decae a ritmo 1x (t+1,5 s = {out.get('B_t15')})")
    print('   mensaje al lanzar: ' + str(out.get('B_msg'))[:80])

    print('C · SÚPER IMÁN')
    chk(out.get('C_lanzada'), 'C. ventana nace ~10 s')
    chk(out.get('C_activaId') == 'iman', f"C. icono ACTIVO (activaId={out.get('C_activaId')})")
    print('   mensaje al lanzar: ' + str(out.get('C_msg'))[:80])

    print('D · RESTO DE PODERES (nace ventana ~t, activaId correcto, sin excepción)')
    for id_, d in (out.get('D') or {}).items():
        chk((not d['exc']) and d['t'] > 7.5 and d['activa'] == id_,
            f"D. {id_}: t={d['t']} activa={d['activa']} exc={d['exc'] or '-'}")

    print('E · SONDA updateMega')
    chk(out.get('E_dtMax', 99) < 0.25, f"E. dt máximo sane ({out.get('E_dtMax')} s)")
    chk(0.005 < out.get('E_dtMedio', 99) < 0.1, f"E. dt medio ~1 frame ({out.get('E_dtMedio')} s)")
    print(f"   llamadas updateMega en la prueba: {out.get('E_llamadas')}")

    print('F · CARGAS vs CANDADO')
    f_ids = out.get('F_idsDistintos') or []
    n_ids = len(f_ids)
    print(f"   desbloqueados del dueño (forzado ['mega']): {out.get('F_desbloq')}")
    print(f"   ids distintos concedidos en 200 cargas: {n_ids} → {f_ids}")
    print(f"   cargas de poderes CON CANDADO: {out.get('F_bloqueados')}/{out.get('F_total')}")
    chk(n_ids >= 8, 'F. el azar alcanza poderes del registro COMPLETO (>8 ids distintos)')
    chk((out.get('F_bloqueados') or 0) > (out.get('F_total') or 1) * 0.5,
        'F. CONFIRMADO: la mayoría de cargas caen en poderes NO desbloqueados')

    print('G · GASTO HONESTO')
    chk(out.get('G_ventana', 0) > 9.5, f"G. al lanzar la ventana nace ({out.get('G_ventana')} s)")
    chk(out.get('G_matrizVacia'), 'G. la carga n=1 se consume al lanzar')
    chk(out.get('G_ventanaSigue'), 'G. la ventana SIGUE viva tras gastarse la carga')

    chk(not errors, f'0 pageerrors ({len(errors)}: {errors[:2]})')
    print(f'RESULTADO repro r54: {ok} OK · {fails} FALLOS')
    sys.exit(0 if not fails else 1)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
