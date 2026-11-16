#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_vestibulo_r77.py — QA de la FASE 173 «GARANTÍA DE RED» · r77 · V3.6.168-SDK6.

FASE 173 (petición del dueño: «otro procedimiento para asegurar la calidad
de las partidas en red, algo que nos dé más fluidez… queremos una solución
garantizada»):
  · SALIDA DEL TÚNEL: el ICE directo (con el TURN de Cloudflare el
    handshake puede tardar >11 s) puede abrir DESPUÉS de que el túnel
    tomó el mando — si ambos DC propios abren, el túnel se retira SOLO
    y la pose vuelve a 60 Hz (y el watchdog de ICE re-arma).
  · TÚNEL ADAPTATIVO: el túnel SCTP entra a 30 Hz (seguro contra
    head-of-line) pero SUBE a 60 Hz con 2 ventanas de 2 s sanas
    (pérdida < 4 %, jitter < 18 ms, muestra suficiente) y vuelve a 30
    en el momento si el enlace se aprieta.
  · SNAP ADAPTATIVO: la bola vuela a 30 Hz de SNAP cuando el enlace va
    sano (20 Hz apretado) — el rival VE la bola más fluida.
  · QOS CON DATOS: qos()/qosTexto() (RED 24 ms · EXCELENTE en AJUSTES ›
    RENDIMIENTO) + evento net_qos cada 60 s de enlace al panel.

REGRESIÓN ÍNTEGRA r76 (FASE 172: piso 72, sonda 68/55, emergencia
honesta, vr_ping con perf) y r75/r74 (hallpick + candado, tres zonas
MULTI, alerta de duelo, jitter buffer 220/160, contrapresión, guarda de
revancha y resync del anfitrión).

Salida: RESULTADO: N OK · M fallos + capturas en download/r77_capturas/.
"""
import base64
import os
import pathlib
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

RAIZ = os.environ.get('CPP_RAIZ') or '/home/z/my-project/crazypp_repo'
URL = 'http://127.0.0.1:3669/game.html'
OUT = pathlib.Path('/home/z/my-project/download/r77_capturas')
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
  const pf = window.__PP_PERF || null;

  // — F172 · el gobernador está vivo y su piso es 72 —
  out.perfVivo = !!pf && typeof pf.status === 'function';
  if (pf) {
    out.rateArranque = pf.rate;
    out.pisoOk = pf.rate >= 72;
    out.tier = pf.tier;

    // escalera: a 90 que no se sostiene → 72 (bajaTasa)
    pf.rate = 90;
    pf._stepDown(true);
    out.noventaATierra = pf.rate === 72;

    // escalera: en el piso regala IMAGEN primero (fovea), nunca la tasa
    pf.rate = 72; pf.fovea = 0.30; pf.scale = 1.20;
    const fv0 = pf.fovea;
    pf._stepDown(false);
    out.imagenPrimero = pf.rate === 72 && pf.fovea > fv0 + 0.05;

    // emergencia honesta: imagen al mínimo (fovea tope + escala 0,8) y
    // aún sin margen → 60
    pf.fovea = pf.foveaMax(); pf.scale = 0.8; pf.rate = 72;
    pf._stepDown(false);
    out.emergencia60 = pf.rate === 60;

    // sonda: la barra nueva pasa con 68/55 (antes 63)
    pf.probe = { round: 0, t: 0, n: 0, acc: 0, min: 999, why: 'qa' };
    pf._probeRound(69, 56);
    out.sonda68Pasa = !!pf.lastCal && pf.lastCal.fps === 69 && !pf.probe;
    pf.probe = { round: 0, t: 0, n: 0, acc: 0, min: 999, why: 'qa' };
    const fv1 = pf.fovea;
    pf._probeRound(64, 56);   // NO pasa → escalón 0: fovea +0,10
    out.sonda64Falla = !pf.lastCal || pf.lastCal.fps !== 64;
    out.sondaEscalona = pf.probe && pf.probe.round === 1;
    pf.probe = null;

    // el piso también al SUBIR: nunca por debajo de 72 si hay margen
    // (la escala ya al perfil del tier → el escalón toca la tasa)
    pf.scale = 1.2; pf.rate = 60;
    pf._stepUp();
    out.subidaAPiso = pf.rate >= 72;

    // restaurar estado honesto para el resto del QA
    pf.rate = 72; pf.scale = 1.2; pf.fovea = Math.min(pf.fovea, pf.foveaMax());
    pf.save();
  }

  // — F173 · GARANTÍA DE RED: QoS legible + túnel adaptativo + salida —
  {
    const N = G.net;
    out.qosVivo = !!N && typeof N.qos === 'function' &&
      typeof N.qosTexto === 'function' && typeof N._teleQos === 'function';
    if (N) {
      // apagado: qos() honesto a 'off' y qosTexto vacío
      const q0 = N.qos();
      out.qosOff = !!q0 && q0.e === 'off';
      out.qosTxtOff = N.qosTexto() === '';

      // enlace SANO simulado: reloj stub + anillo limpio → EXCELENTE
      const clock0 = N._clock;
      N.v2 = 'ok';
      N._clock = { apply: () => {}, markSent: () => {}, jitter: 8,
        rttStats: () => ({ med: 24 }) };
      N._recvRing = []; for (let i = 100; i < 160; i++) N._recvRing.push(i);
      N._gaps = 0;
      const q1 = N.qos();
      out.qosExcelente = q1.e === 'excelente' && q1.ping === 24 && q1.jit === 8;
    const qt = N.qosTexto() || '';
    out.qosTxtOk = qt.indexOf('RED 24') === 0 || qt.indexOf('NET 24') === 0;

      // TÚNEL ADAPTATIVO: 2 ventanas sanas → 60 Hz (antes 30 para siempre)
      // (se stubbean _sendFast/_drainFast: lo que se valida es la SALUD del
      // túnel dentro de frame() — el códec ya lo cubre test_red_nucleo y
      // estos campos nacen con la partida)
      const send0 = N._sendFast, drain0 = N._drainFast;
      N._sendFast = () => {}; N._drainFast = () => {};
      N._tunnel = true; N._poseHz = 30;
      N._tunT = 0; N._tunSalud = 0; N.online = true;
      N.frame(0.1);            // ventana 1: sana → _tunSalud 1 (aún 30)
      const v1 = N._tunSalud === 1 && N._poseHz === 30;
      N._tunT = 0;
      N.frame(0.1);            // ventana 2: sana → 60 Hz
      out.tunSube = v1 && N._poseHz === 60 && N._tunSalud >= 2;

      // enlace apretado (jitter 40 ms): vuelve a 30 en el momento
      N._clock.jitter = 40; N._tunT = 0; N._tunSalud = 2;
      N.frame(0.1);
      out.tunBaja = N._poseHz === 30;

      // SALIDA DEL TÚNEL: los DC propios abrieron → 60 Hz y túnel fuera
      N._clock.jitter = 8;
      N._exitTunnel('directo');
      out.tunExit = !N._tunnel && N._poseHz === 60;

      // restaurar estado honesto de la red
      N.online = false; N.v2 = 'pending'; N._tunnel = false;
      N._poseHz = 60; N._recvRing = []; N._gaps = 0;
      N._tunT = 0; N._tunSalud = 0;
      N._clock = clock0;
      N._sendFast = send0; N._drainFast = drain0;
    }
  }

  // — F168 · MI CASA: «Volver al Hall» fuera, «ESCOGER HALL» dentro —
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(60);
  const idsMain = (G.menuRects || []).map((r) => String(r.id));
  out.casaHallpick = idsMain.includes('page:hallpick');
  out.casaSinHomehall = !idsMain.includes('homehall');

  // — F168 · la página ESCOGER HALL: 6 placas + candados en las cerradas —
  G.menuPage = 'hallpick';
  G.drawMenu();
  await dorme(40);
  const idsHall = (G.menuRects || []).map((r) => String(r.id))
    .filter((i) => i.indexOf('hallv:') === 0);
  out.hallSeis = idsHall.length === 6;
  out.hallPanela1 = (G._menuPanelas || []).length === 1;
  out.hallVarDef = !!G._hallVarDef && !!G._hallVarDef().id;
  out.hallCerradas = (() => {
    try {
      return typeof G._mesaLibre === 'function' &&
        !G._mesaLibre('hito_won25') && !G._mesaLibre('hito_elo1100') &&
        !G._mesaLibre('hito_rally20') && !G._mesaLibre('hito_aces5') &&
        !G._mesaLibre('wins10');
    } catch (e) { return false; }
  })();

  // — F169 · landing MULTI en tres zonas —
  G.menuPage = 'multi';
  if (G._mjMode) G._mjMode = null;
  G.drawMenu();
  await dorme(40);
  const idsMulti = (G.menuRects || []).map((r) => String(r.id));
  out.multiModos = idsMulti.includes('mjnorm') && idsMulti.includes('mjduel');
  out.multiPrivada = idsMulti.includes('net:join');
  out.multiZonasOk = G._multiZonas && G.net.modoSala === 'normal' &&
    G.net.visSala === 'pri';

  // — F169 · CREAR SALA: PÚBLICA/PRIVADA (mjvis) —
  let hostLlamado = 0;
  const hr = G.net.hostRoom;
  G.net.hostRoom = function () { hostLlamado++; this.status = 'waiting';
    this.code = 'ABCD1'; };
  let idx = (G.menuRects || []).findIndex((r) => r.id === 'mjnorm');
  G.menuClick(idx, 0);
  await dorme(30);
  out.elegirVis = (G.menuRects || []).some((r) => r.id === 'mjvis:pub') &&
    (G.menuRects || []).some((r) => r.id === 'mjvis:pri');
  idx = (G.menuRects || []).findIndex((r) => r.id === 'mjvis:pub');
  G.menuClick(idx, 0);
  await dorme(30);
  out.pubCrea = hostLlamado === 1 && G.net.visSala === 'pub' &&
    G.net.modoSala === 'normal';
  G.net.status = 'off'; G.net.code = '';
  if (G._mjMode) G._mjMode = null;
  G.menuPage = 'multi';
  G.drawMenu();
  await dorme(30);
  idx = (G.menuRects || []).findIndex((r) => r.id === 'mjduel');
  G.menuClick(idx, 0);
  await dorme(30);
  idx = (G.menuRects || []).findIndex((r) => r.id === 'mjvis:pri');
  out.visPriExiste = idx >= 0;
  G.menuClick(idx, 0);
  await dorme(30);
  out.locoPrivada = hostLlamado === 2 && G.net.visSala === 'pri' &&
    G.net.modoSala === 'duelos';
  G.net.status = 'off'; G.net.code = '';
  G.net.hostRoom = hr;

  // — F170 · LA ALERTA: el gate del anfitrión + el ASK —
  let arranco = 0;
  G._dueloArrancar = function () { arranco++; };
  G.net.role = 'host';
  G.startOnlineSession();
  await dorme(50);
  out.gatePend = G._dueloPend === true;
  out.alertaViva = !!G.dueloAlerta && !!G.dueloAlerta.mesh;
  out.arrancoNada = arranco === 0;
  G._dueloAsk();
  await dorme(40);
  out.askPagina = G.menuPage === 'dueloask';
  const idsAsk = (G.menuRects || []).map((r) => String(r.id));
  out.askSiNo = idsAsk.includes('dueloask_si') && idsAsk.includes('dueloask_no');
  idx = (G.menuRects || []).findIndex((r) => r.id === 'dueloask_si');
  G.menuClick(idx, 0);
  await dorme(30);
  out.siArranca = arranco === 1 && G._dueloPend === false;
  G.net.role = 'host';
  G._dueloPend = true;
  G.menuPage = 'dueloask';
  G.drawMenu();
  await dorme(30);
  idx = (G.menuRects || []).findIndex((r) => r.id === 'dueloask_no');
  const hang = G.net.hangup;
  let colgo = 0;
  G.net.hangup = function () { colgo++; };
  G.menuClick(idx, 0);
  await dorme(30);
  out.noCuelga = colgo === 1 && arranco === 1 && !G._dueloPend;
  G.net.hangup = hang;
  G.net.role = null;
  G._dueloPend = false;
  G.hideDueloAlerta(true);

  // — panelas montadas == lados del dato + rects en bounds (r70) —
  const ESPERAN = {
    main: 3, multi: 1, join: 1, name: 1, gripname: 1,
    rankini: 1, rank: 1, rankme: 1, champs: 2, champuno: 1, champhist: 1,
    train: 2, trainext: 2, trainarea: 1, carrera: 1, carreradiv: 1,
    opts: 2, optsJuego: 1, optsSala: 1, optsSonido: 1, optsVisual: 1,
    optsPerfil: 1, optsRendi: 1, optsPala: 1,
    salirask: 1, hallask: 1, hallpick: 1, dueloask: 1,
  };
  out.ladosMalos = [];
  out.paginasMalas = [];
  for (const pg of Object.keys(ESPERAN)) {
    G.menuPage = pg;
    if (pg === 'multi') { G._mjMode = null; G.net.status = 'off'; G.net.code = ''; }
    G.drawMenu();
    await dorme(25);
    const n = G._menuPanelas.length;
    if (n !== ESPERAN[pg]) out.ladosMalos.push(pg + ':' + n);
    const rs = G.menuRects || [];
    const malas = rs.filter((r) => r.x < -2 || r.y < -2 ||
      r.x + r.w > 3698 || r.y + r.h > 1402).map((r) => r.id);
    if (!rs.length || malas.length) {
      out.paginasMalas.push(pg + ':' + (malas.join(',') || 'sin rects'));
    }
  }
  out.ladosOk = out.ladosMalos.length === 0;
  out.todasLimpias = out.paginasMalas.length === 0;

  // — capturas —
  const capt = async (pg, key, pre) => {
    if (pre) pre();
    G.menuPage = pg;
    G.drawMenu();
    await dorme(130);
    out[key] = G.menuCanvas.toDataURL('image/png');
  };
  await capt('main', 'pngMain');
  await capt('hallpick', 'pngHallpick');
  await capt('optsRendi', 'pngRendi');
  await capt('multi', 'pngMulti', () => { G._mjMode = null; G.net.status = 'off'; });
  await capt('dueloask', 'pngDueloask', () => { G._dueloPend = true; });
  await capt('salabola', 'pngSalabola');
  G._dueloPend = false;
  G.menuPage = 'main';
  G.drawMenu();
  out.errs = (window.__PP_ERRS || []).length;
  return out;
}"""


async def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3669', '--bind', '127.0.0.1',
         '--directory', os.path.join(RAIZ, 'public')],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html local:', e)
        return
    # ---- sellos de versión ----
    chk('3.6.168-SDK6' in game, 'game.html sello 3.6.168-SDK6 (FASE 173 «GARANTÍA DE RED»)')
    vjson = open(os.path.join(RAIZ, 'src/game/VERSION.json'), encoding='utf-8').read()
    chk('3.6.168-SDK6' in vjson and 'GARANTIA DE RED' in vjson,
        'VERSION.json sella 3.6.168 + FASE 173')
    swjs = open(os.path.join(RAIZ, 'public/sw.js'), encoding='utf-8').read()
    chk("crazypp-v3.6.168-SDK6" in swjs, 'sw.js CACHE sella v3.6.168 (purga de cachés viejas)')
    hub = open(os.path.join(RAIZ, 'src/app/descargas/page.tsx'), encoding='utf-8').read()
    chk('V3.6.168-SDK6' in hub, 'hub /descargas sella V3.6.168-SDK6')

    # ---- F172 · agujas estáticas del piso 72 ----
    chk('PERF_PISO = 72' in game, 'PISO 72 declarado (PERF_PISO, r76)')
    chk('fpsAvg >= 68 && fpsMin >= 55' in game,
        'sonda: barra nueva 68 media / peor segundo 55 (72 sostenidos)')
    chk('fpsAvg >= 63 && fpsMin >= 55' not in game,
        'sonda: la barra vieja 63 (suelo 60) está FUERA')
    chk(game.count('this.rate = PERF_PISO;') >= 3,
        'escalera: 90→72 en la sonda y en el gobernador (3 asignaciones al piso)')
    chk('fpsAvg >= 60 ? Math.min(this.rate, PERF_PISO) : 60' in game,
        'emergencia honesta: 60 SOLO con la media bajo 60 (imagen al mínimo)')
    chk('const bajandoTasa' in game and 'const bajandoImg' in game,
        'gobernador: baja tasa (90→72) y baja imagen separadas (r76)')
    chk('avg < 56 || (avg < 60 && min < 48)' not in game,
        'gobernador: los umbrales viejos de 60 están FUERA')
    chk('Math.max(PERF_PISO, typeof d.rate' in game,
        'perfil guardado bajo 72 se recupera al piso al cargar (r76)')
    chk('this.scale = Math.max(0.8, this.scale - 0.15)' in game,
        'escala de emergencia hasta 0,80 (regala imagen antes que tasa)')
    chk('red < 68' in game and 'red >= 70' in game,
        'telemetría: congelado en partida online bajo 68 (r76)')
    chk('red < 58' not in game, 'telemetría: el congelado viejo 58 está FUERA')
    chk('d2.perf = perf' in game and 'onl: st.partida ? 1 : 0' in game,
        'vr_ping lleva el ESTADO DEL GOBERNADOR (tgt/srate/tier/sc/fv/onl, r76)')

    # ---- F173 · agujas estáticas de la GARANTÍA DE RED ----
    chk("if (this._tunnel && this._fastOpen && this._relOpen) {\n      this._exitTunnel('directo');" in game,
        'SALIDA DEL TÚNEL: DC directo abre → el túnel se retira solo (r77)')
    chk('this._poseHz = PPNET.VP.POSE_HZ;\n    this._tunT = 0; this._tunSalud = 0;' in game,
        '_exitTunnel devuelve la pose a 60 Hz y limpia la salud (r77)')
    chk('this._tunSalud >= 2 ? PPNET.VP.POSE_HZ : PPNET.VP.POSE_HZ_LOW' in game and
        'lw.n >= 30' in game and 'this._clock.jitter < 18' in game,
        'TÚNEL ADAPTATIVO: 2 ventanas de 2 s sanas → 60 Hz (r77)')
    chk("this._teleQos(quiero === PPNET.VP.POSE_HZ ? 'tun_sube' : 'tun_baja')" in game,
        'cada cambio de cadencia del túnel deja huella net_qos (r77)')
    chk('const snapHz = this._poseHz >= PPNET.VP.POSE_HZ ? 30 : PPNET.VP.SNAP_HZ;' in game,
        'SNAP ADAPTATIVO: la bola vuela a 30 Hz con enlace sano (r77)')
    chk("'net_qos'" in game and '_qosAcc >= 60' in game,
        'QOS CON DATOS: net_qos cada 60 s de enlace al panel (r77)')
    chk("? 'excelente' : 'bien'" in game and
        "e = this._poseHz >= PPNET.VP.POSE_HZ ? 'tun60' : 'tun30'" in game,
        'qos() con estados honestos (excelente/bien/ajustada/tun60/tun30, r77)')
    chk('qosTexto' in game and "' · ' + (this.net.qosTexto() || '')" in game,
        'subtítulo de AJUSTES › RENDIMIENTO lleva la RED en vivo (r77)')
    chk("net_red: 'RED {p} ms · {e}'" in game and "net_red: 'NET {p} ms · {e}'" in game,
        'i18n ES+EN de la línea RED (r77)')

    # ---- REGRESIÓN r75 (FASES 168-171) — agujas estáticas íntegras ----
    chk(game.count('duelo_acepta') >= 2,
        'banco de voz: fragmento duelo_acepta ES+EN embebido (r74)')
    chk('_multiZonas' in game and 'mjvis' in game and 'mjsal' in game,
        'fuentes: _multiZonas + mjvis + mjsal presentes (r74)')
    chk('drawMenuHallPick' in game and 'alertaDuelo' in game,
        'fuentes: drawMenuHallPick + alertaDuelo presentes (r74)')
    chk(game.count('PP_ICONS.candado(') == 6,
        'candado de ARCANOS: ' + str(game.count('PP_ICONS.candado(')) +
        '/6 superficies (r74)')
    chk('INTERP_MAX: 220' in game and 'EXTRAP_MAX: 0.160' in game,
        'jitter buffer: tope adaptativo 220 ms + extrapolación 160 ms (r75)')
    chk('2 * iv + 3 * jitterMs' in game,
        'jitter buffer: autoDelay reserva para el PICO (3×jitter, r75)')
    chk('bp > 131072' in game and 'bp > 32768' in game and 'dc.bufferedAmount' in game,
        'contrapresión: pose reemplazable NO encola (32 KB / ahogado 128 KB, r75)')
    chk(game.count('this._poseHz = PPNET.VP.POSE_HZ_LOW;') == 2,
        'túnel + degradación: pose 30 Hz en _enterTunnel y en el degradado (2/2, r75)')
    chk('jitterAlto' in game and 'jitterOk' in game,
        'degradación por JITTER (EMA > 28 ms baja a 30 Hz, r75)')
    chk('recien = performance.now() - (this._mstartAt || 0) < 8000' in game and
        '!recien && !enMarcha' in game,
        'revancha: guarda anti doble arranque (8 s + partido vivo, r75)')
    chk('this.net._mstartAt = performance.now()' in game and
        'this._netResyncT = setTimeout' in game,
        'match start: sello _mstartAt + resync proactivo del anfitrión (700 ms, r75)')

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        errores = []
        page.on('pageerror', lambda e: errores.append(str(e)))
        await page.goto(URL, wait_until='load', timeout=60000)
        await page.wait_for_timeout(3800)
        out = await page.evaluate(JS)

        # — F172 · PISO 72 al CARGAR: perfil guardado con rate 60 → se
        #   recupera al piso (segunda carga con localStorage pre-sembrado) —
        await page.add_init_script(
            "try { localStorage.setItem('ppxr_perf_v1',"
            " JSON.stringify({tier:'gen', auto:true, scale:1.2, rate:60,"
            " fovea:0.55})); } catch (e) {}")
        await page.goto(URL, wait_until='load', timeout=60000)
        await page.wait_for_timeout(3200)
        piso = await page.evaluate(
            "() => { const pf = window.__PP_PERF;"
            " return pf ? { rate: pf.rate, tier: pf.tier } : null; }")
        await browser.close()

    if out.get('sinJuego'):
        print('✗ window.__PP_GAME no llegó — el juego no arrancó')
        return
    # — F172 vivas —
    chk(out.get('perfVivo'), 'el gobernador está vivo (__PP_PERF.status)')
    chk(out.get('pisoOk'), 'el piso de arranque es ≥72 (perfil del casco)')
    chk(out.get('noventaATierra'), '90 que no se sostiene → 72 (el piso intacto)')
    chk(out.get('imagenPrimero'), 'en el piso regala IMAGEN (fovea) antes que la tasa')
    chk(out.get('emergencia60'), '60 SOLO como emergencia (imagen al mínimo)')
    chk(out.get('sonda68Pasa'), 'sonda: 69/56 PASA (barra del dueño 68/55)')
    chk(out.get('sonda64Falla') and out.get('sondaEscalona'),
        'sonda: 64/56 NO pasa y escalona (fovea +0,10)')
    chk(out.get('subidaAPiso'), 'recuperación: de 60 se sube al piso ≥72')
    # — F173 vivas —
    chk(out.get('qosVivo'), 'la QoS está viva (net.qos / qosTexto / _teleQos)')
    chk(out.get('qosOff'), 'qos() honesto en OFF (e=off sin enlace)')
    chk(out.get('qosTxtOff'), 'qosTexto() vacío sin enlace (sin basura en AJUSTES)')
    chk(out.get('qosExcelente'), 'qos(): enlace sano → EXCELENTE (ping 24 · jit 8)')
    chk(out.get('qosTxtOk'), 'qosTexto(): «RED 24 ms · EXCELENTE»')
    chk(out.get('tunSube'), 'túnel adaptativo: 2 ventanas sanas → 60 Hz')
    chk(out.get('tunBaja'), 'túnel adaptativo: jitter 40 ms → vuelve a 30 al momento')
    chk(out.get('tunExit'), 'salida del túnel: DC directo abre → 60 Hz, túnel fuera')
    chk(piso and piso.get('rate') == 72 and piso.get('tier') == 'gen',
        'carga: perfil guardado a 60 se recupera AL PISO 72 (gen)')
    # — regresión r75/r74 vivas —
    chk(out.get('casaHallpick'), 'MI CASA abre ESCOGER HALL (page:hallpick)')
    chk(out.get('casaSinHomehall'), 'MI CASA ya NO tiene «Volver al Hall»')
    chk(out.get('hallSeis'), 'ESCOGER HALL con las 6 variantes')
    chk(out.get('hallPanela1'), 'hallpick en una panela (lados del dato)')
    chk(out.get('hallVarDef'), '_hallVarDef vivo (variante actual)')
    chk(out.get('hallCerradas'), 'halls cerrados SIN cumplir el hito (≥3)')
    chk(out.get('multiModos'), 'ZONA CREAR: los dos modos')
    chk(out.get('multiPrivada'), 'ZONA PRIVADA: el código')
    chk(out.get('multiZonasOk'), 'landing _multiZonas + sala PRIVADA por defecto')
    chk(out.get('elegirVis'), 'la modalidad abre PÚBLICA/PRIVADA')
    chk(out.get('pubCrea'), 'PÚBLICA crea con visSala=pub + modo normal')
    chk(out.get('visPriExiste'), 'PRIVADA disponible también en Duelos Locos')
    chk(out.get('locoPrivada'), 'LOCA crea PRIVADA con modoSala=duelos')
    chk(out.get('gatePend'), 'GATE: el anfitrión recibe duelo PENDIENTE')
    chk(out.get('alertaViva'), 'ALERTA viva: quad de DOS PERSONAS en el rig')
    chk(out.get('arrancoNada'), 'nada se cierra sin aceptar (arranque 0)')
    chk(out.get('askPagina'), 'el icono abre el ASK de confirmación')
    chk(out.get('askSiNo'), 'ASK con SÍ y NO')
    chk(out.get('siArranca'), 'SÍ = se arranca el duelo (una sola vez)')
    chk(out.get('noCuelga'), 'NO = se cuelga y nada arranca')
    chk(out.get('ladosOk'), 'panelas montadas == lados del dato (28 págs)')
    chk(out.get('todasLimpias'), 'rects en bounds en TODAS las páginas')
    chk(not errores, 'sin pageerrors (' + str(len(errores)) + ')')

    guardadas = 0
    for key, nombre in [('pngMain', 'main'), ('pngHallpick', 'hallpick'),
                        ('pngRendi', 'rendi'), ('pngMulti', 'multi'),
                        ('pngDueloask', 'dueloask'),
                        ('pngSalabola', 'salabola')]:
        data = out.get(key)
        if data and data.startswith('data:image/png'):
            (OUT / (nombre + '.png')).write_bytes(
                base64.b64decode(data.split(',', 1)[1]))
            guardadas += 1
    print('  capturas: ' + str(guardadas) + '/6 en ' + str(OUT))
    print('RESULTADO: ' + str(ok) + ' OK · ' + str(fails) + ' fallos')


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
