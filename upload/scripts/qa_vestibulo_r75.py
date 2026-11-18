#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_vestibulo_r75.py — QA de la FASE 171 «LA RED EN SERIO» · r75 · V3.6.166-SDK6.

FASE 168 «ESCOGER HALL · EL CANDADO AVISA»:
  · MI CASA ya no tiene «Volver al Hall»: abre «ESCOGER HALL» (page:hallpick)
    con las 6 variantes como placas de museo — ACTIVA en oro, libres con
    latón, BLOQUEADAS con el candado de ARCANOS pintado encima.
  · el candado de ARCANOS sobre TODO botón bloqueado: campeonatos
    lockados, divisiones de carrera cerradas, skins de bola, temas de sala
    y variantes del hall en Ajustes.
  · las ÁREAS de Entrenamiento (drawArea) en placa de museo.
FASE 169 «EL MULTIJUGADOR EN TRES ZONAS»:
  · landing en ZONAS: CREAR PARTIDA (2 modos) · PARTIDAS DISPONIBLES
    (públicas del pulso) · SALA PRIVADA (código).
  · creación con PÚBLICA/PRIVADA (mjvis) — net.modoSala/visSala viajan al
    latido; privadas jamás se listan; invitaciones con modalidad.
FASE 170 «LA ALERTA DE DUELO»:
  · el anfitrión recibe la ALERTA (icono 2 personas + pitidos + voz) y
    NADA se cierra hasta que acepta: gate en startOnlineSession +
    _dueloPend + dueloask (SÍ arranca el duelo, NO cuelga).

Salida: RESULTADO: N OK · M fallos + capturas en download/r75_capturas/.
"""
import base64
import pathlib
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3669/game.html'
OUT = pathlib.Path('/home/z/my-project/download/r75_capturas')
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

  // — F168 · MI CASA: «Volver al Hall» fuera, «ESCOGER HALL» dentro —
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(60);
  const idsMain = (G.menuRects || []).map((r) => String(r.id));
  out.casaHallpick = idsMain.includes('page:hallpick');
  out.casaSinHomehall = !idsMain.includes('homehall');

  // — F168 · la página ESCOGER HALL: 6 placas + candados en las cerradas —
  const oc = G.PP_ICONS ? null : null;   // (el candado se cuenta vía canvas)
  G.menuPage = 'hallpick';
  G.drawMenu();
  await dorme(40);
  const idsHall = (G.menuRects || []).map((r) => String(r.id))
    .filter((i) => i.indexOf('hallv:') === 0);
  out.hallSeis = idsHall.length === 6;
  out.hallPanela1 = (G._menuPanelas || []).length === 1;
  // placa ACTIVA en oro: _hallVarDef coincide con la primera variante
  out.hallVarDef = !!G._hallVarDef && !!G._hallVarDef().id;

  // — F168 · candado de ARCANOS: la verificación VIVA de las 6 llamadas
  // es estática (PP_ICONS no se expone a window); en pantalla se verifica
  // A OJO en las láminas (hallpick, salabola, salaroom). Aquí: la página
  // hallpick dibuja y sus cerradas existen.
  out.hallCerradas = (() => {
    try {
      // hitos SIN cumplir en el jugador QA (0 victorias, ELO 1000…):
      // los candados de los halls deben estar CERRADOS
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

  // — F169 · CREAR SALA: la modalidad abre PÚBLICA/PRIVADA (mjvis) —
  // espía del hostRoom (sin PeerJS real en QA)
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
  // y la modalidad LOCA sella duelos
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
  const arr = G._dueloArrancar.bind(G);
  G._dueloArrancar = function () { arranco++; };
  G.net.role = 'host';
  G.startOnlineSession();
  await dorme(50);
  out.gatePend = G._dueloPend === true;
  out.alertaViva = !!G.dueloAlerta && !!G.dueloAlerta.mesh;
  out.arrancoNada = arranco === 0;
  // apuntar→ask: la página existe y trae SÍ/NO
  G._dueloAsk();
  await dorme(40);
  out.askPagina = G.menuPage === 'dueloask';
  const idsAsk = (G.menuRects || []).map((r) => String(r.id));
  out.askSiNo = idsAsk.includes('dueloask_si') && idsAsk.includes('dueloask_no');
  // SÍ arranca el duelo (espía)
  idx = (G.menuRects || []).findIndex((r) => r.id === 'dueloask_si');
  G.menuClick(idx, 0);
  await dorme(30);
  out.siArranca = arranco === 1 && G._dueloPend === false;
  // NO cuelga y no arranca
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
  await capt('multi', 'pngMulti', () => { G._mjMode = null; G.net.status = 'off'; });
  await capt('multi', 'pngElegir', () => { G._mjMode = 'normal'; });
  await capt('dueloask', 'pngDueloask', () => { G._dueloPend = true; });
  await capt('trainarea', 'pngTrainarea');
  await capt('salabola', 'pngSalabola');
  await capt('optsSalaRoom', 'pngSalaroom');
  G._dueloPend = false;
  G.menuPage = 'main';
  G.drawMenu();
  out.errs = (window.__PP_ERRS || []).length;
  return out;
}"""


async def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3669', '--bind', '127.0.0.1',
         '--directory', '/home/z/my-project/upload/public'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html local:', e)
        return
    chk('3.6.166-SDK6' in game, 'game.html sello 3.6.166-SDK6 (FASE 171 «LA RED EN SERIO»)')
    chk(game.count('duelo_acepta') >= 2,
        'banco de voz: fragmento duelo_acepta ES+EN embebido')
    chk('_multiZonas' in game and 'mjvis' in game and 'mjsal' in game,
        'fuentes: _multiZonas + mjvis + mjsal presentes')
    chk('drawMenuHallPick' in game and 'alertaDuelo' in game,
        'fuentes: drawMenuHallPick + alertaDuelo presentes')
    chk(game.count('PP_ICONS.candado(') == 6,
        'candado de ARCANOS: ' + str(game.count('PP_ICONS.candado(')) +
        '/6 superficies (hallpick, rejilla, bola, temas, salahall, rivales)')
    # ---- r75 · FASE 171 «LA RED EN SERIO» (agujas del informe del dueño) ----
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
        await browser.close()

    if out.get('sinJuego'):
        print('✗ window.__PP_GAME no llegó — el juego no arrancó')
        return
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
                        ('pngMulti', 'multi'), ('pngElegir', 'elegirVis'),
                        ('pngDueloask', 'dueloask'),
                        ('pngTrainarea', 'trainarea'),
                        ('pngSalabola', 'salabola'),
                        ('pngSalaroom', 'salaroom')]:
        data = out.get(key)
        if data and data.startswith('data:image/png'):
            (OUT / (nombre + '.png')).write_bytes(
                base64.b64decode(data.split(',', 1)[1]))
            guardadas += 1
    print('  capturas: ' + str(guardadas) + '/8 en ' + str(OUT))
    print('RESULTADO: ' + str(ok) + ' OK · ' + str(fails) + ' fallos')


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
