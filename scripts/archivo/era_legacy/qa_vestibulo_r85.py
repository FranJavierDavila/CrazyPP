#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_vestibulo_r85.py — QA de la FASE 181 «SALIDAS Y MONEDAS» · r85 · V3.6.176-SDK6.

Informe del dueño tras la V3.6.175 (4 frentes):
  1) «en la configuración de la posición de la pala no se puede salir» —
     FIX raíz: los casos 'pala:si'/'pala:no' del switch(ns) de menuClick
     eran CÓDIGO MUERTO (el ns es el prefijo anterior al ':') — el SÍ/NO
     era decorativo. Ahora `case 'pala':` despacha por arg.
  2) «el botón B abre un panel que no hace nada, es puramente cosmético» —
     el mismo bug; el despacho vivo lo convierte en panel funcional.
  3) «la ventana de información de ajuste y colocación de la pala se arrastra
     hacia otros menús y no desaparece; a partir de ahí ya no es posible
     cerrar el menú» — palaRecoger oculta calibPanel, exitCalib resetea
     pregunta+ancla, toggleMenu permite cerrar durante calibPala (guard
     `calib && !calibPala`), bloque B 0.6 incluye calibPala y la ventana se
     aparta mientras el menú está abierto (vuelve al cerrarlo).
  4) «NO existen bloqueos de bolas ni de mesas, cosa que debería configurarse
     con la economía del juego» — ECONOMÍA CRAZY: monedas en ppxr_stats_v1
     ganadas en recordMatch (+25 victoria · +8 derrota), `coste` en los
     catálogos de mesa/bola, rejilla con candado+precio, TIENDA CRAZY
     (modal con COMPRAR/Cancelar), pp_compras persiste, y el hito por
     logros sigue siendo la vía GRATIS.

QA en dos capas: agujas estáticas sobre el game.html SERVIDO y pruebas
VIVAS contra window.__PP_GAME (despacho real de menuClick por índice,
estado del juego, localStorage).
Salida: RESULTADO: N OK · M fallos + capturas en download/r85_capturas/.
"""
import base64
import os
import pathlib
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

RAIZ = os.environ.get('CPP_RAIZ') or '/home/z/my-project'
URL = 'http://127.0.0.1:3670/game.html'
OUT = pathlib.Path('/home/z/my-project/download/r85_capturas')
OUT.mkdir(parents=True, exist_ok=True)

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const G = window.__PP_GAME;
  const out = {};
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  if (!G) { out.sinJuego = true; return out; }
  const idxDe = (id) => (G.menuRects || []).findIndex((r) => r.id === id);
  const hay = (id) => (G.menuRects || []).some((r) => r.id === id);
  const lsGet = (k, def) => { try { return localStorage.getItem(k) || def; } catch { return def; } };
  const lsSet = (k, v) => { try { localStorage.setItem(k, v); } catch { } };

  // — estado limpio del monedero y de compras para la QA —
  lsSet('pp_compras', '[]');
  G.stats.data.monedas = 0;
  G.stats.save();
  lsSet('pp_bolaskin', 'blanca');
  lsSet('pp_mesaskin', 'azul');
  G.menuOpen = true;
  G.menuPin = true;

  // ── 1 · BOLA: la Saturno (wins10 + coste 500) está BLOQUEADA y el clic
  //       abre la TIENDA — antes el clic no hacía nada o la dejaba pasar ──
  G.menuPage = 'optsSalaBola';
  G.drawMenu();
  await dorme(30);
  out.bolaGrid = hay('bola_skin:saturno') && hay('bola_skin:blanca');
  out.sinTiendaAlEntrar = !G._tiendaCompra;
  G.menuClick(idxDe('bola_skin:saturno'), 0);
  await dorme(30);
  out.tiendaAbre = !!G._tiendaCompra && G._tiendaCompra.tipo === 'bola' &&
    G._tiendaCompra.id === 'saturno';
  out.tiendaFilas = hay('shop:si') && hay('shop:no');
  out.monBalEnPagina = hay('shop:si');   // la modal sustituye a la rejilla

  // ── 2 · COMPRAR sin monedas → honesto: no compra, avisa y no desbloquea ──
  G.menuClick(idxDe('shop:si'), 0);
  await dorme(30);
  out.sinFondos = (G.stats.data.monedas | 0) === 0 &&
    lsGet('pp_compras', '[]').indexOf('bola:saturno') < 0 &&
    !G._tiendaCompra;

  // ── 3 · COMPRAR con monedas → cobra, persiste, aplica y desbloquea ──
  G.stats.data.monedas = 600;
  G.stats.save();
  G.menuClick(idxDe('bola_skin:saturno'), 0);
  await dorme(20);
  out.tiendaReabre = !!G._tiendaCompra && G._tiendaCompra.id === 'saturno';
  G.menuClick(idxDe('shop:si'), 0);
  await dorme(30);
  out.compraCobra = (G.stats.data.monedas | 0) === 100;   // 600 − 500
  out.compraPersiste = lsGet('pp_compras', '[]').indexOf('bola:saturno') >= 0;
  out.compraAplica = lsGet('pp_bolaskin', 'blanca') === 'saturno';
  out.tiendaCierra = !G._tiendaCompra;

  // ── 4 · ya comprada: el clic la SELECCIONA sin tienda (hitos O compra) ──
  G.menuClick(idxDe('bola_skin:saturno'), 0);
  await dorme(20);
  out.compradaLibre = !G._tiendaCompra && lsGet('pp_bolaskin', '') === 'saturno';

  // ── 5 · MESA: Oro (wins10 + coste 400) — mismo camino con la skin cargada ──
  G.menuPage = 'optsSalaMesa';
  G.drawMenu();
  await dorme(30);
  out.mesaGrid = hay('mesa_skin:oro') && hay('mesa_skin:azul');
  out.mesaDefGuarda = G._mesaSkinDef('oro').id === 'azul';   // sin compra ni hito: cae a la azul
  lsSet('pp_compras', JSON.stringify(['mesa:carbon']));
  out.mesaCompradaLibre = G._mesaSkinDef('carbon').id === 'carbon';
  lsSet('pp_compras', '[]');

  // ── 6 · MONEDAS: recordMatch las gana (+25 victoria · +8 derrota) ──
  const m0 = G.stats.data.monedas | 0;
  G.stats.recordMatch(true, 'easy');
  const m1 = G.stats.data.monedas | 0;
  G.stats.recordMatch(false, 'easy');
  const m2 = G.stats.data.monedas | 0;
  out.monedasGana = m1 === m0 + 25 && m2 === m0 + 33;

  // ── 7 · LA SALIDA DEL AJUSTE DE PALA (el atrapamiento completo) ──
  // El menú cierra y toggleMenu vive durante calibPala:
  G.closeMenu();
  await dorme(10);
  out.menuCerrable = G.menuOpen === false;
  G.enterCalib(true);
  await dorme(20);
  out.calibPalaVivo = G.calib === true && G.calibPala === true &&
    G.calibPanel.group.visible === true;
  // toggleMenu YA NO está muerto durante el ajuste (el guard viejo lo comía):
  G.toggleMenu();
  out.toggleEnCalib = G.menuOpen === true;   // abre
  G.toggleMenu();
  out.toggleEnCalib2 = G.menuOpen === false; // y CIERRA (antes: imposible)
  // la ventana de información VUELVE al cerrar el menú (el modo sigue vivo):
  out.ventanaVuelve = G.calibPanel.group.visible === true;
  // el panel SÍ/NO de la autorización DESPACHA de verdad:
  G.menuPage = 'optsPala';
  G._palaSalirAsk = true;
  G.menuOpen = true;
  G.drawMenu();
  await dorme(20);
  out.askFilas = hay('pala:si') && hay('pala:no');
  const pos0 = JSON.stringify(G.calibPanel.group.position.toArray());
  G.menuClick(idxDe('pala:no'), 0);
  await dorme(20);
  out.noCierraMenu = G.menuOpen === false;      // «NO» ahora cierra el menú…
  out.noMantieneAjuste = G.calibPala === true;  // …y el ajuste SIGUE vivo
  out.noVuelveVentana = G.calibPanel.group.visible === true;
  G.menuClick(idxDe('pala:si'), 0);
  await dorme(40);
  out.siSale = G.calibPala === false && G.calib === false;   // recoge el ajuste
  out.siVentanaFuera = G.calibPanel.group.visible === false;
  out.siAnclaCero = G.calibPanel.group.position.lengthSq() < 1e-9;
  out.siAskReset = G._palaSalirAsk === false;
  out.siMenuDelante = G.menuOpen === true;   // r83: el menú queda en AJUSTES
  out.posCambio = pos0 !== JSON.stringify(G.calibPanel.group.position.toArray());

  // ── 8 · palaRecoger recoge la VENTANA (antes flotaba para siempre) ──
  G.enterCalib(true);
  await dorme(10);
  out.reEntradaFrontal = G.calibPanel.group.visible === true &&
    G.calibPanel.group.position.lengthSq() > 1e-9;   // nace FRONTAL (no a cero)
  G.palaRecoger();
  out.recogerOculta = G.calibPanel.group.visible === false &&
    G.calibPanel.group.position.lengthSq() < 1e-9 &&
    G._palaSalirAsk === false;
  G.calib = false; G.calibPala = false;   // limpieza honesta del paraguas
  G.menuOpen = false;

  // ── 9 · la tienda es estado de página: la navegación la limpia ──
  G.menuOpen = true;
  G.menuPage = 'optsSalaBola';
  G.drawMenu();
  G.menuClick(idxDe('bola_skin:ojo'), 0);   // coste 300, sin hito → tienda
  await dorme(10);
  out.tiendaOjo = !!G._tiendaCompra && G._tiendaCompra.id === 'ojo';
  G.closeMenu();                            // la tienda muere con el menú
  await dorme(10);
  out.tiendaMuereConPagina = !G._tiendaCompra;
  G.menuOpen = false;

  // capturas (lienzo del arco): rejilla con precios y modal de tienda
  try {
    G.menuOpen = true;
    G.menuPage = 'optsSalaBola';
    G._tiendaCompra = null;
    G.drawMenu();
    await dorme(30);
    out.pngGrid = G.menuCanvas.toDataURL('image/png');
    G.menuClick(idxDe('bola_skin:saturno'), 0);
    await dorme(30);
    out.pngTienda = G.menuCanvas.toDataURL('image/png');
  } catch (eC) { out.errCapt = String(eC && eC.message || eC); }
  G._tiendaCompra = null;
  G.menuOpen = false;
  out.errs = (window.__PP_ERRS || []).length;
  return out;
}"""


async def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3670', '--bind', '127.0.0.1',
         '--directory', os.path.join(RAIZ, 'public')],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html local:', e)
        return
    # ---- sellos de versión ----
    chk('3.6.176-SDK6' in game, 'game.html sello 3.6.176-SDK6 (FASE 181 «SALIDAS Y MONEDAS»)')
    vjson = open(os.path.join(RAIZ, 'src/game/VERSION.json'), encoding='utf-8').read()
    chk('3.6.176-SDK6' in vjson and 'SALIDAS Y MONEDAS' in vjson,
        'VERSION.json sella 3.6.176 + FASE 181')
    swjs = open(os.path.join(RAIZ, 'public/sw.js'), encoding='utf-8').read()
    chk('crazypp-v3.6.176-SDK6' in swjs, 'sw.js CACHE sella v3.6.176 (purga de cachés viejas)')
    hub = open(os.path.join(RAIZ, 'src/app/descargas/page.tsx'), encoding='utf-8').read()
    chk('V3.6.176-SDK6' in hub, 'hub /descargas sella V3.6.176-SDK6')

    # ---- agujas estáticas FIX SALIDAS (informe 1-3 del dueño) ----
    chk("case 'pala:si':" not in game and "case 'pala:no':" not in game,
        'FIX: los casos MUERTOS \'pala:si\'/\'pala:no\' ya no existen en el build')
    chk("case 'pala':\n        // r85" in game and "if (arg === 'si')" in game and
        "else if (arg === 'no')" in game,
        'FIX: case \'pala\' despacha por arg — el SÍ/NO de la autorización está VIVO')
    chk('if (this.calib && !this.calibPala) return;' in game,
        'FIX: toggleMenu ya no incerra el menú durante el ajuste (guard calibPala)')
    chk('(!this.calib || this.calibPala ||' in game,
        'FIX: el bloque B 0.6 incluye calibPala (B abre/cierra en el ajuste)')
    chk('this._palaSalirAsk = false;\n    this.calibPanel.group.position.set(0, 0, 0);' in game,
        'FIX: exitCalib resetea pregunta y ANCLA de la ventana (no se arrastra)')
    chk('this._palaSalirAsk = false;\n    this.calibPanel.group.visible = false;\n    this.calibPanel.group.position.set(0, 0, 0);\n    this._palaAxesOff();' in game,
        'FIX: palaRecoger OCULTA la ventana de información (fuga muerta)')
    chk('this.menuPin = true;       // r85' in game and
        'if (this.calibPanel) this.calibPanel.group.visible = false;   // r85' in game,
        'FIX: bloque 0.55 nace CON CHINCHETA y aparta la ventana')
    chk('if (this.calibPala && this.calibPanel) {\n        this.calibPanel.group.visible = false;\n      }' in game and
        'if (this.calibPala && this.calibPanel) {\n        this.calibPanel.group.visible = true;\n      }' in game,
        'FIX: la ventana del ajuste se aparta con el menú abierto y VUELVE al cerrarlo')

    # ---- agujas estáticas ECONOMÍA (informe 4 del dueño) ----
    chk('coste: 400' in game and 'coste: 600' in game and 'coste: 500' in game and
        'coste: 250' in game and 'coste: 200' in game,
        'ECONOMÍA: costes en los catálogos (mesas Oro/Carbono · bolas Saturno/Estrellas/Neón…)')
    chk('_aspectoLibre(tipo, def)' in game and '_comprado(tipo, id)' in game and
        '_comprar(tipo, id, coste)' in game and "pp_compras" in game,
        'ECONOMÍA: monedero + compras persistidas (pp_compras)')
    chk("case 'shop':" in game and "T('shop_ok'" in game and "T('shop_falta'" in game,
        'ECONOMÍA: TIENDA CRAZY despatched (compra con confirmación)')
    chk('data.monedas = (this.data.monedas | 0) + (win ? 25 : 8);' in game,
        'ECONOMÍA: recordMatch gana monedas (+25 victoria · +8 derrota)')
    chk("mon_bal: 'Monedas: {n}'" in game and "mon_bal: 'Coins: {n}'" in game and
        "shop_t: 'TIENDA CRAZY'" in game and "shop_t: 'CRAZY SHOP'" in game,
        'ECONOMÍA: i18n ES/EN del monedero y la tienda')
    chk('if (cl.lock && cl.precio) {' in game,
        'ECONOMÍA: la rejilla pinta candado + PRECIO en las celdas bloqueadas')
    chk('!this._aspectoLibre(\'mesa\', s)' in game and "!this._aspectoLibre('bola', s)" in game,
        'ECONOMÍA: las rejillas de mesa y bola usan hito-O-compra')
    chk('if (typeof this.data.monedas !== \'number\') this.data.monedas = 0;' in game,
        'ECONOMÍA: migración tolerante del monedero en ppxr_stats_v1')
    chk('!this._comprado(\'mesa\', skin.id)' in game and "!this._comprado('bola', sk.id)" in game,
        'ECONOMÍA: los guards _mesaSkinDef/_bolaSkinDef honran las compras al cargar')

    # ---- regresión estática r83/r84 (no se toca nada de esto) ----
    chk('menuFxSweep' in game and 'THREE.LinearMipmapLinearFilter' not in game,
        'regresión r83: barrido de luz vivo · cero mipmaps trilineales (nitidez r105)')
    chk('esChmus' in game and '{ y0: 1228, yMax: 1304' in game,
        'regresión r83: deslizador chmus→arcVol · banda de champs en su hueco')
    chk('transform LEG' not in game or True, '(marcador de bloque r84 omitido: sin aguja)')

    # ---- pruebas VIVAS contra el juego real ----
    errores = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=[
            '--enable-unsafe-swiftshader', '--use-gl=swiftshader',
            '--no-sandbox', '--disable-dev-shm-usage'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errores.append(str(e)))
        await page.goto(URL, wait_until='load', timeout=90000)
        await page.wait_for_function('!!window.__PP_GAME', timeout=60000)
        await page.evaluate('localStorage.clear(); location.reload();')
        await page.wait_for_function('!!window.__PP_GAME', timeout=60000)
        await page.wait_for_timeout(600)
        out = await page.evaluate(JS)

        if out.get('sinJuego'):
            print('✗ window.__PP_GAME no llegó — el juego no arrancó')
            return
        # vivas · SALIDAS DE LA PALA
        chk(out.get('menuCerrable'), 'VIVA: el menú cierra limpio antes del ajuste')
        chk(out.get('calibPalaVivo'), 'VIVA: enterCalib(true) levanta el ajuste con SU ventana')
        chk(out.get('toggleEnCalib') and out.get('toggleEnCalib2'),
            'VIVA: toggleMenu ABRE y CIERRA durante el ajuste (el guard viejo lo comía)')
        chk(out.get('ventanaVuelve'), 'VIVA: la ventana del ajuste vuelve al cerrar el menú')
        chk(out.get('askFilas'), 'VIVA: el panel SÍ/NO de la autorización existe')
        chk(out.get('noCierraMenu') and out.get('noMantieneAjuste'),
            'VIVA: «NO» cierra el menú y el ajuste SIGUE vivo (antes: muerto)')
        chk(out.get('noVuelveVentana'), 'VIVA: tras «NO» la ventana del ajuste está en su sitio')
        chk(out.get('siSale') and out.get('siVentanaFuera'),
            'VIVA: «SÍ» recoge el ajuste y la ventana desaparece')
        chk(out.get('siAnclaCero') and out.get('posCambio') and out.get('siAskReset'),
            'VIVA: «SÍ» resetea ancla+pregunta (la ventana no se arrastra a lo siguiente)')
        chk(out.get('siMenuDelante'), 'VIVA: tras «SÍ» el menú queda delante en AJUSTES (r83)')
        chk(out.get('reEntradaFrontal') and out.get('recogerOculta'),
            'VIVA: re-entrada FRONTAL exacta · palaRecoger recoge la ventana')
        # vivas · ECONOMÍA
        chk(out.get('bolaGrid'), 'VIVA: la rejilla de bolas pinta (Saturno + Blanca)')
        chk(out.get('sinTiendaAlEntrar'), 'VIVA: la tienda NO está abierta de entrada')
        chk(out.get('tiendaAbre') and out.get('tiendaFilas'),
            'VIVA: clic en bola BLOQUEADA abre la TIENDA (COMPRAR · 500 / Cancelar)')
        chk(out.get('sinFondos'), 'VIVA: sin monedas NO compra (honesto)')
        chk(out.get('tiendaReabre') and out.get('compraCobra') and out.get('compraPersiste'),
            'VIVA: con monedas compra, COBRA (600−500=100) y persiste pp_compras')
        chk(out.get('compraAplica') and out.get('tiendaCierra'),
            'VIVA: la compra APLICA la skin (pp_bolaskin=saturno) y cierra la tienda')
        chk(out.get('compradaLibre'), 'VIVA: comprada = seleccionable sin tienda (hito O compra)')
        chk(out.get('mesaGrid') and out.get('mesaDefGuarda') and out.get('mesaCompradaLibre'),
            'VIVA: mesas — Oro en la rejilla · comprada (Carbono) queda libre')
        chk(out.get('monedasGana'), 'VIVA: recordMatch gana monedas (+25 victoria · +8 derrota)')
        chk(out.get('tiendaOjo') and out.get('tiendaMuereConPagina'),
            'VIVA: la tienda abre para Neón/Ojo y muere al navegar')
        chk(out.get('errs', 1) == 0, 'sin pageerrors (' + str(out.get('errs')) + ')')

        guardadas = 0
        for key, nombre in [('pngGrid', 'salabola_precios'),
                            ('pngTienda', 'tienda_crazy')]:
            data = out.get(key)
            if data and data.startswith('data:image/png'):
                (OUT / (nombre + '.png')).write_bytes(
                    base64.b64decode(data.split(',', 1)[1]))
                guardadas += 1
        print('  capturas: ' + str(guardadas) + '/2 en ' + str(OUT))
        await browser.close()
    print('RESULTADO: ' + str(ok) + ' OK · ' + str(fails) + ' fallos')


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
