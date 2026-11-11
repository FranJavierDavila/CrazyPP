#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r50_gatillo_oeste.py — FASE 145 · QA del CONTRATO DE CONSUMO fireGun.

El bug: en el duelo del forajido (Oeste) el arma estaba ARMADA todo el
partido y la rama del revólver se comía el gatillo libre aunque fireGun
fuera un no-op entre salvas — el superpoder de pala jamás salía.

Este QA verifica, sobre el game.html REAL servido por :3000 y con el
enrutado REAL (onSelectStart):
  1 · si champs.fireGun(i) devuelve TRUE  → el pulso se CONSUME (el arma
      dispara; megaTrigger NO se llama; _megaT sigue 0).
  2 · si champs.fireGun(i) devuelve FALSE (arma fuera de ventana, el caso
      del Oeste entre salvas) → el pulso CAE al megaTrigger: la MEGA PALA
      se ACTIVA (_megaT ≈ 15) y la carga se gasta de la matriz.
  3 · si champs.fireGun(i) LANZA una excepción → el pulso también cae al
      megaTrigger (el try/catch del contrato no tumba el gatillo).
  4 · contrato de los MÓDULOS en public/ (estático): oeste/locura/
      estacion_orbital devuelven bool y propagan; halloween/plantilla ya
      lo hacían.
  5 · el respaldo por gatillo de PALA sigue vivo en el Oeste (gunVive):
      con gunArmed y gatillo de la mano de la pala, megaTrigger acepta.

Uso: python3 scripts/qa_r50_gatillo_oeste.py   (requiere :3000 arriba)
"""
import re
import sys
from pathlib import Path
from playwright.async_api import async_playwright

RAIZ = Path('/home/z/my-project/upload')
URL = 'http://127.0.0.1:3000/game.html'

ok, fails, errors = 0, 0, []


def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


JS_CONTRATO = """async () => {
  const G = window.__PP_GAME;
  const out = { presente: !!G };
  if (!G) return out;
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  try { window.__pp2DPlay = true; } catch (e) { /* */ }
  try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) { /* */ }
  G.palaMejorada = true;
  await dorme(300);

  // Simulación de VISOR: isPresenting es una propiedad de datos escribible
  // en three 0.170 (this.isPresenting = false en el constructor). Sin ella,
  // onSelectStart vuelve en el guard de entrada y el enrutado no corre.
  G.renderer.xr.isPresenting = true;
  // Estado limpio de las ramas PRIORITARIAS del gatillo (menú, cartel,
  // intro de campeonato, academia, ajuste, hall, espacio Arcano):
  G.menuOpen = false; G._instr = null; G.champIntro = null;
  G.tutV1 = false; G.calib = false; G.calibPala = false;
  G.inHall = false; G._arconoOn = false;

  // Escenario común: campeonato «activo», rally vivo, matriz con 1 carga.
  const entradas = [];
  // loader real, módulo FALSO controlado por el test:
  G.champs = {
    active: true,
    gunArmed: true,                 // el arma del Oeste armada TODO el duelo
    paddleGunArmed: false,          // fuera de la ventana de 3 s
    fireGun: (i) => { entradas.push(i); return out.consumir; },
  };
  G.rules.state = 'rally';
  G.rules.rallyHits = 0;
  G._megaMatriz = [{ id: 'mega', n: 1 }];
  G._megaIdx = 0;
  G._megaRallyGrants = 0;
  G._megaT = 0; G._megaWarn = false; G._megaTickN = 0;
  const manoPala = G.paddleHand;            // en 2D cualquier i vale
  const iLibre = (manoPala === 0) ? 1 : 0;

  // — CASO 1 · el arma CONSUME (fireGun true): mega no se inmuta —
  out.consumir = true;
  entradas.length = 0;
  G.onSelectStart(iLibre);
  await dorme(120);
  out.c1_armaLlamada = entradas.length === 1 && entradas[0] === iLibre;
  out.c1_megaApagada = G._megaT === 0;
  out.c1_cargaIntacta = !!(G._megaMatriz[0] && G._megaMatriz[0].n === 1);

  // — CASO 2 · el arma NO consume (false — el Oeste entre salvas): CAE a mega —
  out.consumir = false;
  entradas.length = 0;
  G.onSelectStart(iLibre);
  await dorme(120);
  out.c2_armaLlamada = entradas.length === 1;
  out.c2_megaActiva = G._megaT > 14.5 && G._megaT <= 15.001;
  out.c2_cargaGastada = G._megaMatriz.length === 0 || G._megaMatriz[0].n === 0;

  // recargar la matriz para el caso 3
  G._megaT = 0; G._megaMatriz = [{ id: 'mega', n: 1 }];

  // — CASO 3 · el arma LANZA: el contrato no tumba el gatillo —
  G.champs.fireGun = (i) => { entradas.push(i); throw new Error('arma rota'); };
  entradas.length = 0;
  let excepcion = false;
  try { G.onSelectStart(iLibre); } catch (e) { excepcion = true; }
  await dorme(120);
  out.c3_sinExcepcionAlCallejero = !excepcion;
  out.c3_megaActiva = G._megaT > 14.5;

  // recargar y probar el RESPALDO por gatillo de la PALA (gunVive)
  G._megaT = 0; G._megaMatriz = [{ id: 'mega', n: 1 }];
  out.consumir = false;
  G.champs.fireGun = (i) => { entradas.push(i); return out.consumir; };

  // — CASO 5 · gatillo de la MANO DE LA PALA con gunArmed: respaldo vivo —
  // (fuera de ventana: paddleGunArmed false ⇒ el arma ni se consulta
  //  para esa mano; el pulso va directo al mega)
  entradas.length = 0;
  G.onSelectStart(manoPala);
  await dorme(120);
  out.c5_armaNoConsultadaEnPala = entradas.length === 0;
  out.c5_megaActiva = G._megaT > 14.5;

  out.fin = true;
  return out;
}"""


async def main():
    # — 4 · contrato ESTÁTICO de los módulos (public/) —
    print('4 · CONTRATO ESTÁTICO DE LOS MÓDULOS')
    esperados = {
        'championships/oeste/index.js': [
            (r'fireGun\(i\) \{ return CTRL \? \(CTRL\.fireGun\(i\) === true\) : false; \}', 1),
            (r"if \(!\(this\._duelo && this\._duelo\.phase === 'duel'\)\) return false;", 1),
            (r'if \(now - \(this\._gunLast \|\| 0\) < 0\.16\) return true;', 1),
        ],
        'championships/locura/index.js': [
            (r'if \(!mount\) return false;', 1),
            (r'if \(now - this\._gunLast < 0\.16\) return true;', 1),
            (r'return CTRL \? \(CTRL\.fireGun\(i\) === true\) : false;', 1),
        ],
        'championships/estacion_orbital/index.js': [
            (r'if \(!mount\) return false;', 1),
            (r'if \(now - this\._gunLast < 0\.16\) return true;', 1),
            (r'return CTRL\.fireGun\(i\) === true;', 1),
        ],
        'championships/halloween/index.js': [
            (r'return this\.pistola \? this\.pistola\.disparo\(i\) : false;', 1),
        ],
    }
    for rel, pares in esperados.items():
        txt = (RAIZ / 'public' / rel).read_text(encoding='utf-8')
        for pat, n in pares:
            real = len(re.findall(pat, txt))
            chk(real == n, f'{rel.split("/")[1]}: {pat[:52]}… ×{real} (esperado {n})')

    # — mecánica real (headless sobre :3000) —
    print('1-3+5 · ENRUTADO REAL (onSelectStart sobre game.html)')
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until='domcontentloaded')
        await page.wait_for_timeout(7000)
        out = await page.evaluate(JS_CONTRATO)
        await browser.close()

    chk(out.get('presente'), 'game vivo (window.__PP_GAME)')
    if not out.get('presente'):
        print('RESULTADO QA r50:', ok, 'OK ·', fails, 'FALLOS')
        sys.exit(1)
    # CASO 1 · arma consume
    chk(out.get('c1_armaLlamada'), '1. fireGun(true): el arma recibe el pulso')
    chk(out.get('c1_megaApagada'), '1. fireGun(true): el superpoder NO se activa')
    chk(out.get('c1_cargaIntacta'), '1. fireGun(true): la carga queda intacta')
    # CASO 2 · arma no consume → mega (EL BUG DEL OESTE)
    chk(out.get('c2_armaLlamada'), '2. fireGun(false): el arma es consultada')
    chk(out.get('c2_megaActiva'), '2. fireGun(false): el pulso CAE al megaTrigger (FIX OESTE)')
    chk(out.get('c2_cargaGastada'), '2. fireGun(false): la carga se gasta')
    # CASO 3 · excepción controlada
    chk(out.get('c3_sinExcepcionAlCallejero'), '3. fireGun que LANZA: sin excepción al callejero')
    chk(out.get('c3_megaActiva'), '3. fireGun que LANZA: el pulso cae al mega')
    # CASO 5 · respaldo por pala
    chk(out.get('c5_armaNoConsultadaEnPala'), '5. gatillo de la PALA fuera de ventana: el arma ni se consulta')
    chk(out.get('c5_megaActiva'), '5. gatillo de la PALA: respaldo vivo (gunVive)')
    # higiene
    chk(not errors, f'0 pageerrors ({len(errors)}: {errors[:2]})')

    print(f'RESULTADO QA r50: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
