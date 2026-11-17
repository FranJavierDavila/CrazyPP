#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r78.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 174 · r78
(https://franjavierdavila.github.io/CrazyPP/game.html — V3.6.171-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva el sello 3.6.167, el PISO 72
    (PERF_PISO), la sonda 68/55, la emergencia honesta, el congelado 68,
    el vr_ping con el estado del gobernador y TODAS las agujas r75 de red;
    sw.js servido sella v3.6.167; PAGES-VERSION.txt con fuente_commit.
  · FUNCIONAL: el juego VIVO en producción — __PP_PERF con piso ≥72,
    escalera 90→72 / imagen primero / emergencia 60, sonda 68 pasa y 64
    escalona, carga del perfil 60→72 (segunda visita pre-sembrada),
    MI CASA → ESCOGER HALL (regresión r74) y 0 pageerrors.
Uso: python3 scripts/prod_smoke_r76.py"""
import asyncio
import os
import urllib.request

from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.171-SDK6'

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const out = {};
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  const pf = window.__PP_PERF || null;
  out.perfVivo = !!pf && typeof pf.status === 'function';
  if (pf) {
    out.pisoArranque = pf.rate >= 72;
    pf.rate = 90; pf._stepDown(true);
    out.noventaATierra = pf.rate === 72;
    pf.rate = 72; pf.fovea = 0.30; pf.scale = 1.20;
    const fv0 = pf.fovea;
    pf._stepDown(false);
    out.imagenPrimero = pf.rate === 72 && pf.fovea > fv0 + 0.05;
    pf.fovea = pf.foveaMax(); pf.scale = 0.8; pf.rate = 72;
    pf._stepDown(false);
    out.emergencia60 = pf.rate === 60;
    pf.probe = { round: 0, t: 0, n: 0, acc: 0, min: 999, why: 'qa' };
    pf._probeRound(69, 56);
    out.sonda68Pasa = !!pf.lastCal && pf.lastCal.fps === 69 && !pf.probe;
    pf.rate = 72; pf.scale = 1.2;
    pf.fovea = Math.min(pf.fovea, pf.foveaMax());
  }
  const G = window.__PP_GAME;
  if (!G) { out.sinJuego = true; return out; }

  // — F173 · GARANTÍA DE RED en producción —
  {
    const N = G.net;
    out.qosVivo = !!N && typeof N.qos === 'function' && typeof N.qosTexto === 'function';
    if (N) {
      N.v2 = 'ok';
      const clock0 = N._clock;
      N._clock = { apply: () => {}, markSent: () => {}, jitter: 8,
        rttStats: () => ({ med: 24 }) };
      N._recvRing = []; for (let i = 100; i < 160; i++) N._recvRing.push(i);
      N._gaps = 0;
      const q1 = N.qos();
      out.qosExcelente = q1.e === 'excelente' && q1.ping === 24 && q1.jit === 8;
      // túnel adaptativo + salida (códec stubbeado: nace con la partida)
      const send0 = N._sendFast, drain0 = N._drainFast;
      N._sendFast = () => {}; N._drainFast = () => {};
      N._tunnel = true; N._poseHz = 30; N._tunT = 0; N._tunSalud = 0;
      N.online = true;
      N.frame(0.1); N._tunT = 0; N.frame(0.1);
      out.tunSube = N._poseHz === 60 && N._tunSalud >= 2;
      N._clock.jitter = 40; N._tunT = 0; N._tunSalud = 2;
      N.frame(0.1);
      out.tunBaja = N._poseHz === 30;
      N._clock.jitter = 8;
      N._exitTunnel('directo');
      out.tunExit = !N._tunnel && N._poseHz === 60;
      N.online = false; N.v2 = 'pending'; N._tunnel = false;
      N._poseHz = 60; N._recvRing = []; N._gaps = 0;
      N._tunT = 0; N._tunSalud = 0;
      N._clock = clock0;
      N._sendFast = send0; N._drainFast = drain0;
    }
  }

  // — F174 · MENÚS EN PROFUNDIDAD en producción —
  {
    out.motorBandas = typeof G._menuBandas === 'function';
    const PAGS = ['optsJuego', 'optsSalaMesa', 'optsSonido', 'optsRendi',
      'optsPala', 'join', 'name', 'gripname'];
    const ESP = {
      optsJuego: ['diff:easy', 'alertas', 'estilo:prev', 'close'],
      optsSalaMesa: ['mesa_altomen', 'mesa_skin:', 'reto97', 'close'],
      optsSonido: ['mvol-', 'mvolset', 'close'],
      optsRendi: ['perfAuto', 'perfFfr:max', 'close'],
      optsPala: ['palaGo', 'gname', 'homehall', 'close'],   // sin agarres guardados: la fila gripLoad no existe (correcto)
      join: ['key:A', 'key:del', 'key:ok', 'tab:main'],
      name: ['nkey:A', 'nkey:sp', 'nkey:0', 'tab:main'],
      gripname: ['gkey:A', 'gkey:sp', 'page:optsPala'],
    };
    const pag0 = G.menuPage;
    let sinSolape = true, enBanda = true, idsVivos = true, mal = '';
    for (const pg of PAGS) {
      G.menuPage = pg;
      G.drawMenu();
      await dorme(15);
      const rs = (G.menuRects || []).filter((r) => r && r.id);
      const ids = rs.map((r) => String(r.id));
      for (const e of (ESP[pg] || [])) {
        if (!ids.some((i) => i.indexOf(e) === 0)) { idsVivos = false; mal = pg + ':' + e; }
      }
      for (const r of rs) {
        if (r.x < 1104 || r.x + r.w > 2592 || r.y < 0 || r.y + r.h > 1400) enBanda = false;
      }
      for (let i = 0; i < rs.length && sinSolape; i++) {
        for (let j = i + 1; j < rs.length; j++) {
          const a = rs[i], b = rs[j];
          const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
          const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
          if (ox > 2 && oy > 2) sinSolape = false;
        }
      }
    }
    G.menuPage = pag0; G.drawMenu();
    out.f174Ids = idsVivos; out.f174Mal = mal;
    out.f174Banda = enBanda; out.f174Solapes = sinSolape;
    // sala pública en espera: botón vivo + chip en MI CASA
    const st0 = G.net.status, cd0 = G.net.code;
    G.net.status = 'waiting'; G.net.code = 'ZZ9PQ'; G.net.online = false;
    G.menuPage = 'multi'; G.drawMenu(); await dorme(15);
    const idsM = (G.menuRects || []).map((r) => String(r.id));
    out.btnEspera = idsM.includes('net:espera') && idsM.includes('net:cancel');
    G._salaEnEspera = true; G.menuPage = 'main'; G.drawMenu(); await dorme(15);
    const sub = String(G._vestSubPorId('tab:multi') || '');
    out.chipEspera = sub.indexOf('ZZ9PQ') >= 0;
    G.net.status = st0; G.net.code = cd0; G._salaEnEspera = false;
    out.alertasOn = G.alertasOn !== false;
  }

  G.menuPage = 'main';
  G.drawMenu();
  await dorme(60);
  const idsMain = (G.menuRects || []).map((r) => String(r.id));
  out.casaHallpick = idsMain.includes('page:hallpick');
  // — F175 · SIEMPRE ANCLADO en producción —
  out.pinPorDefecto = G.menuPin === true;
  G._menuAnchorEst = 'otra';
  G._menuAnclaHeal();
  out.healMantienePin = G.menuPin === true;
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(40);
  const idsMain79 = (G.menuRects || []).map((r) => String(r.id));
  const idxHP79 = idsMain79.indexOf('page:hallpick');
  if (idxHP79 >= 0) {
    G.menuClick(idxHP79, 0);
    await dorme(30);
    out.hallpickAbre = G.menuPage === 'hallpick';
    G.menuPage = 'main';
    G.drawMenu();
    await dorme(20);
  }
  // — F176 · las áreas de ENTRENAR viven DENTRO de la panela —
  G.menuPage = 'trainarea';
  G._trainSel = 'dir';
  G.drawMenu();
  await dorme(25);
  const rsTA80 = (G.menuRects || []).filter((r) => r && r.id &&
    String(r.id).indexOf('lang:') !== 0);
  out.areaDentroC = rsTA80.length > 0 &&
    rsTA80.every((r) => r.x >= 1104 && r.x + r.w <= 2592) &&
    rsTA80.some((r) => String(r.id).indexOf('trv3:start:') === 0);
  out.errs = (window.__PP_ERRS || []).length;
  return out;
}"""


async def main():
    game = get(URL)
    chk('3.6.171-SDK6' in game, 'game.html SERVIDO sella 3.6.171-SDK6')
    chk('PERF_PISO = 72' in game, 'PISO 72 servido (PERF_PISO, r76)')
    chk('fpsAvg >= 68 && fpsMin >= 55' in game and
        'fpsAvg >= 63 && fpsMin >= 55' not in game,
        'sonda servida con la barra 68/55 (la 63 vieja FUERA)')
    chk('fpsAvg >= 60 ? Math.min(this.rate, PERF_PISO) : 60' in game,
        'emergencia honesta servida (60 solo con media < 60)')
    chk('const bajandoTasa' in game and 'const bajandoImg' in game,
        'gobernador servido: tasa e imagen separadas (r76)')
    chk('Math.max(PERF_PISO, typeof d.rate' in game,
        'perfil bajo 72 se recupera al piso (servido)')
    chk('red < 68' in game and 'red >= 70' in game and 'red < 58' not in game,
        'congelado de telemetría en red servido a 68 (r76)')
    chk('d2.perf = perf' in game, 'vr_ping con el estado del gobernador (servido)')
    chk('INTERP_MAX: 220' in game and 'EXTRAP_MAX: 0.160' in game and
        'bp > 32768' in game, 'regresión r75 servida: jitter buffer + contrapresión')
    chk('recien = performance.now() - (this._mstartAt || 0) < 8000' in game,
        'regresión r75 servida: guarda de revancha')
    swjs = get(BASE + '/sw.js')
    chk('crazypp-v3.6.171-SDK6' in swjs, 'sw.js SERVIDO sella v3.6.169 (purga PWA)')
    try:
        pv = get(BASE + '/PAGES-VERSION.txt')
        chk('2311902' in pv, 'PAGES-VERSION.txt: fuente_commit 2311902 (r78)')
    except Exception as e:
        chk(False, 'PAGES-VERSION.txt legible (' + str(e)[:60] + ')')
    # ---- F173 · agujas de la GARANTÍA DE RED servidas ----
    chk("this._exitTunnel('directo');" in game and
        'if (this._tunnel && this._fastOpen && this._relOpen)' in game,
        'SALIDA DEL TÚNEL servida (DC directo abre → túnel fuera, r77)')
    chk('this._tunSalud >= 2 ? PPNET.VP.POSE_HZ : PPNET.VP.POSE_HZ_LOW' in game and
        "'tun_sube' : 'tun_baja'" in game,
        'TÚNEL ADAPTATIVO servido: 2 ventanas sanas → 60 Hz (r78)')
    chk('const snapHz = this._poseHz >= PPNET.VP.POSE_HZ ? 30 : PPNET.VP.SNAP_HZ;' in game,
        'SNAP ADAPTATIVO servido (bola a 30 Hz con enlace sano, r77)')
    chk("'net_qos'" in game and '_qosAcc >= 60' in game and 'qosTexto' in game,
        'QOS CON DATOS servida: net_qos 60 s + línea RED en AJUSTES (r78)')
    # ---- F174 · agujas de MENÚS EN PROFUNDIDAD servidas ----
    chk('_menuBandas(rects, items, opts) {' in game,
        'MOTOR _menuBandas servido (filas a panel completo, r78)')
    chk('const yFin = this._menuBandas(rects, items, { yMax: 1244 });' in game,
        'AJUSTES nivel 3 entero en bandas (11 casos + cierre, r78)')
    chk("btn('diff:easy', 56, y, 292, 66" not in game and
        "btn(`key:${CHARS[i]}`" not in game,
        'painters legados de tarjeta 1024×1536 FUERA (r78)')
    chk('if (this.alertasOn !== false) this.alertaDuelo();' in game and
        'pp_alertas_v1' in game,
        'SISTEMA DE ALERTAS servido (ON por defecto + silencio honesto, r78)')
    chk("btn('net:espera'" in game and 'hub_multi_espera' in game,
        'SALA PÚBLICA EN ESPERA servida (Dejar en espera + chip, r78)')
    # ---- F175 · SIEMPRE ANCLADO servido ----
    chk('new THREE.Vector3(fwdX, 0, fwdZ), D_REF);' in game,
        'ANCLA AL CENTRO DEL CUERPO servida (yaw del RIG, r79)')
    chk('if (this.menuPin) { this.menuPin = false; this._menuPinDraw(); }'
        not in game and "arg === 'hallpick'" in game and
        "idSet: 'chmus:set'" in game and "case 'pala:si':" in game and
        'hecha: superada,' in game and 'muerta: !superada && !esActual,' in game,
        'FASE 175 servida: heal sin soltar el pin + hallpick + slider de música'
        ' + autorización PALA + escalera con estados (r79)')
    # ---- F176 · MENUS QUE RESPIRAN servido ----
    chk('this._menuAnclaXr = !!(this.renderer && this.renderer.xr &&' in game and
        'this.recenterFrames === 0 && this.menuOpen) this.anchorMenu(true);' in game,
        'ANCLA EN VR servida (firma XR + re-ancla al fin del recentrado, r80)')
    chk("'trainext', 'trainarea'," not in game and
        "'rankme', 'rank', 'champhist'" in game,
        'ENTRENAR con transform LEG servido (áreas DENTRO de la panela, r80)')
    chk('_iconoClave(nombre) {' in game and
        "optsSalaRoom: { tituloKey: 'cat_salaroom'" in game and
        "id: 'page:optsSalaHall', icono: 'sala'," not in game,
        'iconos con alias + conchas nivel 3 + HALL fuera de Ajustes (r80)')

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        errores = []
        page.on('pageerror', lambda e: errores.append(str(e)))
        await page.goto(URL, wait_until='load', timeout=60000)
        await page.wait_for_timeout(4200)
        out = await page.evaluate(JS)
        # segunda visita: perfil guardado a 60 → debe recuperar el PISO 72
        await page.add_init_script(
            "try { localStorage.setItem('ppxr_perf_v1',"
            " JSON.stringify({tier:'gen', auto:true, scale:1.2, rate:60,"
            " fovea:0.55})); } catch (e) {}")
        await page.goto(URL, wait_until='load', timeout=60000)
        await page.wait_for_timeout(3600)
        piso = await page.evaluate(
            "() => { const pf = window.__PP_PERF;"
            " return pf ? { rate: pf.rate, tier: pf.tier } : null; }")
        await browser.close()

    if out.get('sinJuego'):
        print('✗ el juego no arrancó en producción')
        return
    chk(out.get('perfVivo'), '__PP_PERF vivo en producción')
    chk(out.get('pisoArranque'), 'piso de arranque ≥72 (perfil gen del smoke)')
    chk(out.get('noventaATierra'), '90→72 en vivo (piso intacto)')
    chk(out.get('imagenPrimero'), 'en el piso regala IMAGEN (fovea) en vivo')
    chk(out.get('emergencia60'), '60 solo como emergencia en vivo')
    chk(out.get('sonda68Pasa'), 'sonda 69/56 PASA en producción')
    chk(piso and piso.get('rate') == 72, 'perfil guardado a 60 → AL PISO 72 en producción')
    # — F173 vivas —
    chk(out.get('qosVivo'), 'QoS viva en producción (net.qos / qosTexto)')
    chk(out.get('qosExcelente'), 'qos(): enlace sano → EXCELENTE (ping 24 · jit 8) en producción')
    chk(out.get('tunSube'), 'túnel 30→60 con 2 ventanas sanas EN PRODUCCIÓN')
    chk(out.get('tunBaja'), 'jitter 40 ms → vuelve a 30 al momento en producción')
    chk(out.get('tunExit'), 'salida del túnel → 60 Hz y túnel fuera en producción')
    # — F174 vivas —
    chk(out.get('motorBandas'), 'MOTOR bandas + ENTRENAR VIVO + AIRE en producción')
    chk(out.get('f174Ids'), 'ids vivos en 8 páginas migradas en producción'
        + ('' if out.get('f174Ids') else ' (' + str(out.get('f174Mal')) + ')'))
    chk(out.get('f174Banda'), 'todo el contenido en panela C en producción')
    chk(out.get('f174Solapes'), 'CERO solapes en producción')
    chk(out.get('btnEspera'), '«Dejar en espera · MI CASA» en producción')
    chk(out.get('chipEspera'), 'chip «SALA ZZ9PQ EN ESPERA · pública» en producción')
    chk(out.get('alertasOn'), 'alertas ABIERTAS por defecto en producción')
    # — F175 vivas —
    chk(out.get('pinPorDefecto') and out.get('healMantienePin'),
        'chincheta ON y el HEAL NO la suelta en producción')
    chk(out.get('hallpickAbre'), 'ESCOGER HALL abre en producción (despacho page)')
    # — F176 vivas —
    chk(out.get('areaDentroC'),
        'ENTRENAR: las áreas viven DENTRO de la panela en producción')
    chk(out.get('casaHallpick'), 'regresión r74: MI CASA abre ESCOGER HALL')
    chk(not errores and not out.get('errs'), 'sin pageerrors en producción')
    print('RESULTADO: ' + str(ok) + ' OK · ' + str(fails) + ' fallos')


if __name__ == '__main__':
    asyncio.run(main())
