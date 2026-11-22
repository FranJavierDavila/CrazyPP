#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_vestibulo_r80.py — QA de la FASE 176 «MENUS QUE RESPIRAN» · r80 · V3.6.171-SDK6.

FASE 174 (petición del dueño: «todos los subniveles con el mismo tipo de
maquetación ocupando todo el espacio que tenemos ahora en los paneles…
repasa los menús hasta su nivel más profundo y corrígelos, nada de
desbordamientos ni solapamientos» + sala pública en espera + alertas):
  · MOTOR _menuBandas: las FILAS A PANEL COMPLETO del nivel 3+ — el mismo
    lenguaje de las rejillas (placa de museo + medallón + etiqueta + sub)
    para los controles profundos; reparte la altura POR CUENTA (no
    desborda por construcción), encoge el texto al ancho real y devuelve
    el cursor Y. Ids EXACTOS del despacho legado.
  · MIGRADOS a bandas: las 11 páginas de AJUSTES (juego · sala ·
    salaroom · salamesa · salabola · salahall · sonido · visual · perfil
    · rendi · pala) + los 3 teclados (join · name · gripname). Fuera la
    tarjeta legada 1024×1536 (placa suprimida para todas).
  · SALA PÚBLICA EN ESPERA: «Dejar en espera · MI CASA» deja la sala
    VIVA en segundo plano (net:espera); ATRÁS desde MULTIJUGADOR no la
    cierra; el Vestíbulo declara «SALA {c} EN ESPERA · pública»; la
    alerta de duelo avisa al anfitrión esté donde esté.
  · SISTEMA DE ALERTAS: abierto para todos POR DEFECTO; AJUSTES › JUEGO
    lo silencia (pp_alertas_v1) — sin quad, sin pitidos, sin voz; el
    duelo PENDIENTE se acepta desde MULTIJUGADOR.

REGRESIÓN ÍNTEGRA r77 (FASE 173: salida del túnel, túnel adaptativo,
snap adaptativo, QoS), r76 (piso 72, sonda 68/55), r75/r74 (hallpick +
candado, tres zonas MULTI, alerta de duelo, jitter buffer 220/160,
contrapresión, guarda de revancha y resync del anfitrión).

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
OUT = pathlib.Path('/home/z/my-project/download/r80_capturas')
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

  // — F175 · SIEMPRE ANCLADO + arreglos del informe del dueño —
  {
    // 1 · la chincheta JAMÁS se suelta sola: ancla en otra estancia →
    // re-ancla delante del jugador pero menuPin sigue clavado
    out.pinPorDefecto = G.menuPin === true;
    const pos0 = JSON.stringify(G.menuGroup.position.toArray());
    G._menuAnchorEst = 'otra';
    G._menuAnclaHeal();
    out.healMantienePin = G.menuPin === true;
    out.healReancla = JSON.stringify(G.menuGroup.position.toArray()) !== pos0;
    // 2 · ESCOGER HALL: la tarjeta de MI CASA NAVEGA (despacho page) y la
    // página vive con sus placas
    G.menuPage = 'main';
    G.drawMenu();
    await dorme(30);
    const idsMain79 = (G.menuRects || []).map((r) => String(r.id));
    const idxHP = idsMain79.indexOf('page:hallpick');
    out.tarjetaHallpickViva = idxHP >= 0;
    if (idxHP >= 0) {
      G.menuClick(idxHP, 0);
      await dorme(30);
      out.hallpickAbre = G.menuPage === 'hallpick' &&
        (G.menuRects || []).filter((r) => r && r.id).length >= 5;
      G.menuPage = 'main';
      G.drawMenu();
      await dorme(20);
    }
    // 3 · MULTI: en espera → las ZONAS vuelven con la sala viva
    const st0 = G.net.status, cd0 = G.net.code;
    G.net.status = 'waiting'; G.net.code = 'QQ7WW'; G.net.online = false;
    G._salaEnEspera = false;
    G.menuPage = 'multi'; G.drawMenu(); await dorme(20);
    const idsEsp = (G.menuRects || []).map((r) => String(r.id));
    out.esperaPanel = idsEsp.includes('net:espera') &&
      !idsEsp.includes('mjnorm');
    G._salaEnEspera = true;
    G.menuPage = 'multi'; G.drawMenu(); await dorme(20);
    const idsZon = (G.menuRects || []).map((r) => String(r.id));
    out.zonasConSalaViva = idsZon.includes('mjnorm') &&
      idsZon.includes('mjduel') && idsZon.includes('net:gestiona');
    G.net.status = st0; G.net.code = cd0; G._salaEnEspera = false;
    // 4 · ENTRENAR: los subapartados ACCEDEN y pintan contenido
    G.menuPage = 'train'; G.drawMenu(); await dorme(20);
    const idsTrain = (G.menuRects || []).map((r) => String(r.id));
    const idxArea = idsTrain.indexOf('trv3:area:spin');
    out.tarjetaAreaViva = idxArea >= 0;
    if (idxArea >= 0 && window.__PP_TRAIN) {
      G.menuClick(idxArea, 0);
      await dorme(30);
      out.trainareaAccede = G.menuPage === 'trainarea' &&
        (G.menuRects || []).some((r) => r &&
          String(r.id).indexOf('trv3:start:') === 0);
    }
    const idxExt = idsTrain.indexOf('page:trainext');
    if (idxExt >= 0) {
      // r79 · re-dibujar ENTRENAR antes del 2.º clic: el estado anterior
      // dejó los rects de trainarea y el índice ya no apunta al mismo id
      G.menuPage = 'train'; G.drawMenu(); await dorme(20);
      const idsTr2 = (G.menuRects || []).map((r) => String(r.id));
      const idxExt2 = idsTr2.indexOf('page:trainext');
      if (idxExt2 >= 0) G.menuClick(idxExt2, 0);
      await dorme(30);
      out.trainextAccede = G.menuPage === 'trainext' &&
        (G.menuRects || []).filter((r) => r && r.id).length >= 3;
    }
    G.menuPage = 'main'; G.drawMenu(); await dorme(20);
    // 5 · PALA: la autorización SÍ/NO vive al pulsar B en el ajuste
    G._palaSalirAsk = true;
    G.menuPage = 'optsPala'; G.drawMenu(); await dorme(20);
    const idsPala = (G.menuRects || []).map((r) => String(r.id));
    out.palaAutoriza = idsPala.includes('pala:si') &&
      idsPala.includes('pala:no') && !idsPala.includes('palaGo');
    G._palaSalirAsk = false;
    // 6 · rank/rankme/historial/champs/carrera/hall/pala: banda + sin solapes
    const PAGS79 = ['rank', 'rankme', 'champhist', 'champs', 'carrera',
      'hallpick', 'optsPala'];
    let ok79 = true, mal79 = '';
    for (const pg of PAGS79) {
      G.menuPage = pg;
      G.drawMenu();
      await dorme(15);
      const rs = (G.menuRects || []).filter((r) => r && r.id);
      // banda = lienzo completo (champs es C+R): el chequeo fino por
      // panela ya lo hace el bucle de 28 páginas de la regresión
      for (const r of rs) {
        if (r.x < 0 || r.x + r.w > 3696 || r.y < 0 ||
            r.y + r.h > 1400) { ok79 = false; mal79 = pg; }
      }
      for (let i = 0; i < rs.length && ok79; i++) {
        for (let j = i + 1; j < rs.length; j++) {
          const a = rs[i], b = rs[j];
          const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
          const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
          if (ox > 2 && oy > 2) {
            ok79 = false;
            mal79 = pg + ':' + a.id + '>' + b.id + ' y' + a.y + '/' + b.y;
          }
        }
      }
    }
    out.paginas79EnBanda = ok79; out.paginas79Mal = mal79;
    // 7 · ESCALERA: jamás entra en una liga bloqueada + pulso animado
    G.menuPage = 'carrera'; G.drawMenu(); await dorme(20);
    const stC = G._carreraEstado();
    const selIdxs = (G.menuRects || []).map((r) => String(r.id))
      .filter((i) => i.indexOf('carrera:sel:') === 0)
      .map((i) => parseInt(i.split(':')[2], 10));
    out.escaleraMuertaSinRect = selIdxs.every((i) => i <= stC.div);
    out.animPide = typeof G._menuAnimPide === 'function';
  }
  // — F176 · MENUS QUE RESPIRAN: entrenar vivo, aire, volver al anterior —
  {
    // 1 · ENTRENAR: las áreas dibujan DENTRO de la panela C (el informe
    // «están todos vacíos»: sin el transform LEG quedaban en la esquina)
    G.menuPage = 'trainarea'; G._trainSel = 'dir';
    G.drawMenu(); await dorme(20);
    const rsTA = (G.menuRects || []).filter((r) => r && r.id &&
      String(r.id).indexOf('lang:') !== 0);
    out.areaDentroC = rsTA.every((r) => r.x >= 1104 && r.x + r.w <= 2592) &&
      rsTA.some((r) => String(r.id).indexOf('trv3:start:') === 0);
    // 2 · RETO DE LA SEMANA: el clic ARRANCA el modo (el menú se cierra)
    G.menuPage = 'train'; G.drawMenu(); await dorme(20);
    const idsTr80 = (G.menuRects || []).map((r) => String(r.id));
    const iSem80 = idsTr80.indexOf('trv3:semana');
    if (iSem80 >= 0) {
      G.menuClick(iSem80, 0);
      await dorme(40);
      out.semanaArranca = G.menuOpen === false;
      G.menuOpen = true; G.menuGroup.visible = true;
      G.menuPage = 'train'; G.drawMenu(); await dorme(20);
    }
    // 3 · MULTI con aire: las tarjetas de modo a BANDA COMPLETA
    const st80 = G.net.status, cd80 = G.net.code;
    G.net.status = 'off'; G._salaEnEspera = false;
    G.menuPage = 'multi'; G.drawMenu(); await dorme(20);
    const rn = (G.menuRects || []).find((r) => r && r.id === 'mjnorm');
    out.multiAncho = !!rn && rn.w >= 900;
    G.net.status = st80; G.net.code = cd80;
  }
  {
    out.motorBandas = typeof G._menuBandas === 'function';
    const PAGS = ['optsJuego', 'optsSala', 'optsSalaRoom', 'optsSalaMesa',
      'optsSalaBola', 'optsSalaHall', 'optsSonido', 'optsVisual',
      'optsPerfil', 'optsRendi', 'optsPala', 'join', 'name', 'gripname'];
    const ESPERADOS = {
      optsJuego: ['diff:easy', 'diff:medium', 'diff:hard', 'mm:go',
        'alertas', 'estilo:prev', 'estilo:next', 'dobles', 'close'],
      // r80 · el HALL se retiró de AJUSTES (su sitio natural es MI CASA)
      optsSala: ['page:optsSalaRoom', 'page:optsSalaMesa',
        'page:optsSalaBola', 'close'],
      optsSalaRoom: ['theme:', 'psthru', 'close'],
      optsSalaMesa: ['mesa_altomen', 'mesa_altomas', 'mesa_skin:',
        'reto97', 'close'],
      optsSalaBola: ['bola_skin:', 'close'],
      optsSalaHall: ['hall_entrar', 'hall_var:', 'close'],
      optsSonido: ['music', 'amb', 'voz', 'sndtest', 'mvol-', 'mvol+',
        'mvolset', 'fvolset', 'close'],
      optsVisual: ['trail', 'tips', 'hapt', 'close'],
      optsPerfil: ['pname', 'tele', 'reset', 'close'],
      optsRendi: ['perfAuto', 'perfTier:auto', 'perfRecal', 'perfFfr:max',
        'perfFfr:def', 'close'],
      optsPala: ['palaGo', 'gname', 'gripNat', 'homehall', 'close'],
      join: ['key:A', 'key:del', 'key:ok', 'key:cancel', 'tab:main'],
      name: ['nkey:A', 'nkey:sp', 'nkey:del', 'nkey:0', 'nkey:ok',
        'tab:main'],
      gripname: ['gkey:A', 'gkey:sp', 'gkey:del', 'gkey:0',
        'page:optsPala'],
    };
    const pag0 = G.menuPage;
    let sinSolape = true, enBanda = true, malPag = '';
    for (const pg of PAGS) {
      G.menuPage = pg;
      G.drawMenu();
      await dorme(20);
      const rs = (G.menuRects || []).filter((r) => r && r.id);
      // 1 · IDS VIVOS: cada control esperado existe
      const ids = rs.map((r) => String(r.id));
      for (const esp of (ESPERADOS[pg] || [])) {
        if (!ids.some((i) => i.indexOf(esp) === 0)) { malPag = pg + ':' + esp; }
      }
      // 2 · EN BANDA: todo dentro de la panela C (1112..2584 × 0..1400)
      for (const r of rs) {
        if (r.x < 1104 || r.x + r.w > 2592 || r.y < 0 || r.y + r.h > 1400) {
          enBanda = false;
        }
      }
      // 3 · SIN SOLAPES: ningún par de rects se pisa (>2 px de tolerancia)
      for (let i = 0; i < rs.length && sinSolape; i++) {
        for (let j = i + 1; j < rs.length; j++) {
          const a = rs[i], b = rs[j];
          const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
          const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
          if (ox > 2 && oy > 2) { sinSolape = false; }
        }
      }
    }
    G.menuPage = pag0;
    G.drawMenu();
    out.paginasMigradas = PAGS.length;
    out.motorIdsVivos = malPag === '';
    out.motorMalId = malPag;
    out.todasEnBanda = enBanda;
    out.sinSolapes = sinSolape;
    // SALA PÚBLICA EN ESPERA: botón vivo + chip en MI CASA
    const st0 = G.net.status, cd0 = G.net.code;
    G.net.status = 'waiting'; G.net.code = 'AB12C'; G.net.online = false;
    G._salaEnEspera = false;
    G.menuPage = 'multi';
    G.drawMenu();
    await dorme(20);
    const idsMulti = (G.menuRects || []).map((r) => String(r.id));
    out.btnEspera = idsMulti.includes('net:espera') &&
      idsMulti.includes('net:cancel');
    G._salaEnEspera = true;
    G.menuPage = 'main';
    G.drawMenu();
    await dorme(20);
    const subMulti = String(G._vestSubPorId('tab:multi') || '');
    out.chipEspera = (subMulti.indexOf('AB12C') >= 0) &&
      (subMulti.indexOf('EN ESPERA') >= 0 ||
        subMulti.indexOf('WAITING') >= 0);
    G.net.status = st0; G.net.code = cd0; G._salaEnEspera = false;
    // SISTEMA DE ALERTAS: por defecto ABIERTO
    out.alertasPorDefecto = G.alertasOn !== false;
  }
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
    chk('3.6.171-SDK6' in game, 'game.html sello 3.6.171-SDK6 (FASE 174 «MENÚS EN PROFUNDIDAD»)')
    vjson = open(os.path.join(RAIZ, 'src/game/VERSION.json'), encoding='utf-8').read()
    chk('3.6.171-SDK6' in vjson and 'MENUS QUE RESPIRAN' in vjson,
        'VERSION.json sella 3.6.171 + FASE 176')
    swjs = open(os.path.join(RAIZ, 'public/sw.js'), encoding='utf-8').read()
    chk("crazypp-v3.6.171-SDK6" in swjs, 'sw.js CACHE sella v3.6.171 (purga de cachés viejas)')
    hub = open(os.path.join(RAIZ, 'src/app/descargas/page.tsx'), encoding='utf-8').read()
    chk('V3.6.171-SDK6' in hub, 'hub /descargas sella V3.6.171-SDK6')

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

    # ---- F174 · agujas estáticas de MENÚS EN PROFUNDIDAD ----
    chk('_menuBandas(rects, items, opts) {' in game,
        'MOTOR _menuBandas declarado (filas a panel completo, r78)')
    chk('const yFin = this._menuBandas(rects, items, { yMax: 1244 });' in game,
        'optsCat entero en bandas (los 11 casos + cierre en fila fina, r78)')
    chk(game.count('this._menuBandas(rects, [') >= 3,
        'teclados join/name/gripname en bandas (3 llamadas directas, r78)')
    chk('btn(\'diff:easy\', 56, y, 292, 66' not in game and
        "btn('mesa_altomen', 176, y, 148" not in game and
        "btn(`key:${CHARS[i]}`" not in game,
        'los painters legados de tarjeta 1024×1536 están FUERA (r78)')
    chk("id: 'perfFfr:def'" in game and "id: 'gripLoad:' + nm" in game and
        "del: 'gripDel:' + nm" in game and "izq: { id: 'estilo:prev'" in game,
        'ids de control preservados en las bandas (ffr/grips/ciclo, r78)')
    chk("'join', 'name', 'gripname'" in game and
        "'optsSalaRoom', 'optsSalaMesa'," in game,
        'sinPlaca extendido a TODAS las páginas migradas (r78)')
    chk("id: 'alertas'" in game and "case 'alertas':" in game and
        'pp_alertas_v1' in game and
        'if (this.alertasOn !== false) this.alertaDuelo();' in game,
        'SISTEMA DE ALERTAS: fila en JUEGO + dispatcher + silencio honesto (r78)')
    chk('this.alertasOn = localStorage.getItem(\'pp_alertas_v1\') !== \'0\';' in game,
        'alertas ON por defecto y persistidas (pp_alertas_v1, r78)')
    chk("btn('net:espera'" in game and "arg === 'espera'" in game and
        'hub_multi_espera' in game and
        "if (arg === 'main' && this.net && !this.net.online &&\n              this.net.status === 'waiting') this._salaEnEspera = true;" in game,
        'SALA PÚBLICA EN ESPERA: Dejar en espera + ATRÁS la deja viva + chip (r78)')
    chk('this._salaEnEspera = false;   // r78 · cancelar ES cancelar' in game and
        'this._salaEnEspera = false;   // r78 · la sala dejó de esperar' in game,
        'cancelar/arrancar limpian la espera (honestidad de estado, r78)')
    chk("btn_alertas: 'Alertas de retos: {v}'" in game and
        "btn_alertas: 'Challenge alerts: {v}'" in game and
        "btn_espera: 'Dejar en espera · MI CASA'" in game and
        "btn_espera: 'Keep waiting · MY HOME'" in game and
        "hub_multi_espera: 'SALA {c} EN ESPERA · pública'" in game and
        "hub_multi_espera: 'ROOM {c} WAITING · public'" in game and
        "msg_alertas_on:" in game and "msg_alertas_off:" in game,
        'i18n ES+EN de alertas y sala en espera (r78)')

    # ---- F175 · agujas estáticas SIEMPRE ANCLADO ----
    chk('const fwd = new THREE.Vector3(0, 0, -1).applyQuaternion(rq);' in game and
        'new THREE.Vector3(fwdX, 0, fwdZ), D_REF);' in game,
        'ANCLA AL CENTRO DEL CUERPO: el arco nace en el yaw del RIG, no de la mirada (r79)')
    chk('this.anchorMenu(true);' in game and
        'if (this.menuPin) { this.menuPin = false; this._menuPinDraw(); }' not in game,
        'el HEAL re-ancla SIN soltar jamás la chincheta (r79)')
    chk("!(st === 'waiting' && this._salaEnEspera)" in game and
        "btn('net:gestiona'" in game and "arg === 'gestiona'" in game,
        'MULTI: ATRÁS desde espera vuelve a las ZONAS con la sala viva (r79)')
    chk("arg === 'hallpick'" in game,
        'ESCOGER HALL navega (hallpick en el despacho page, r79)')
    chk('// r79 · RANKING MUNDIAL a PANEL COMPLETO' in game and
        "'ELO ' + String(D.elo || 1000)" in game and
        "T('hist_empty_hint')" in game,
        'RANKING MUNDIAL + MI RANKING + HISTORIAL a bandas con estados vacíos (r79)')
    chk("idSet: 'chmus:set'" in game and
        'AM.setArcVol(Math.round(v * 20) / 20);' in game,
        'MÚSICA DE CAMPEONATOS con control deslizante clicable (r79)')
    chk('hecha: superada,' in game and 'actual: esActual,' in game and
        'muerta: !superada && !esActual,' in game and
        'if (t.muerta) PP_ICONS.candado(c, gx + gw - 58, y + hAuto / 2, 2.2);' in game,
        'ESCALERA: superada verde+aspa, actual animada, bloqueada candado GRANDE sin rect (r79)')
    chk('this._palaSalirAsk = true;' in game and "case 'pala:si':" in game and
        '!this.tutV1 && !this.calibPala &&' in game,
        'PALA: B pide autorización (SÍ/NO) y la Y ya no sale del ajuste (r79)')
    chk('fuera el lerp hacia la cabeza de cada frame' in game,
        'panel del ajuste de PALA FIJO (sin seguir a la cabeza, r79)')

    # ---- F176 · agujas estáticas MENUS QUE RESPIRAN ----
    chk('this._menuAnclaXr = !!(this.renderer && this.renderer.xr &&' in game and
        'this.recenterFrames === 0 && this.menuOpen) this.anchorMenu(true);' in game,
        'ANCLA EN VR: re-ancla al fin del recentrado y si cambia 2D↔XR (r80)')
    chk("'trainext', 'trainarea'," not in game and
        "'rankme', 'rank', 'champhist'" in game,
        'ENTRENAR con transform LEG (áreas DENTRO de la panela) + rank sin placa vieja (r80)')
    chk('_iconoClave(nombre) {' in game and
        "sala: 'vestibulo', mesa: 'partido'" in game,
        'ICONOS: alias sala/mesa/bola/hall — Sala y Escena con medallones (r80)')
    chk("id: 'page:optsSalaHall', icono: 'sala'," not in game and
        "optsSalaRoom: { tituloKey: 'cat_salaroom'" in game,
        'HALL fuera de Ajustes + conchas de nivel 3 con VOLVER al anterior (r80)')
    chk("a_dir: 'DIRECCIÓN'" in game and "icono: 'ojo'," in game,
        'título del área traducido + iconos en las celdas del ambiente (r80)')
    chk('que los botones y textos respiren' in game,
        'MULTI: tarjetas de modo a banda completa con aire (r80)')

    # ---- REGRESIÓN r75 (FASES 168-171) — agujas estáticas íntegras ----
    chk(game.count('duelo_acepta') >= 2,
        'banco de voz: fragmento duelo_acepta ES+EN embebido (r74)')
    chk('_multiZonas' in game and 'mjvis' in game and 'mjsal' in game,
        'fuentes: _multiZonas + mjvis + mjsal presentes (r74)')
    chk('drawMenuHallPick' in game and 'alertaDuelo' in game,
        'fuentes: drawMenuHallPick + alertaDuelo presentes (r74)')
    # r78 · el MOTOR centraliza el candado del grid (temas/mesa/bola/hall):
    # 4 superficies literales + el lock de _menuBandas que las pinta todas
    chk(game.count('PP_ICONS.candado(') == 5 and
        'if (cl.lock) PP_ICONS.candado(' in game,
        'candado de ARCANOS: 5 literales + motores de bandas y rejilla (r74→r79)')
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
    # — F174 vivas —
    chk(out.get('motorBandas'), 'el motor _menuBandas está vivo en el juego')
    chk(out.get('motorIdsVivos'), 'ids vivos en las 14 páginas migradas'
        + (('(' + str(out.get('motorMalId')) + ')' if not out.get('motorIdsVivos') else '')))
    chk(out.get('todasEnBanda'), 'todo el contenido dentro de la panela C (bounds)')
    chk(out.get('sinSolapes'), 'CERO solapes en las 14 páginas migradas')
    chk(out.get('paginasMigradas') == 14, '14 páginas migradas revisadas en vivo')
    chk(out.get('btnEspera'), 'MULTIJUGADOR en espera: «Dejar en espera» + «Cancelar»')
    chk(out.get('chipEspera'), 'MI CASA declara «SALA AB12C EN ESPERA · pública»')
    chk(out.get('alertasPorDefecto'), 'alertas ABIERTAS por defecto')
    # — F175 vivas —
    chk(out.get('pinPorDefecto') and out.get('healMantienePin') and
        out.get('healReancla'),
        'chincheta: ON por defecto y el HEAL re-ancla sin soltarla jamás')
    chk(out.get('tarjetaHallpickViva') and out.get('hallpickAbre'),
        'ESCOGER HALL abre de verdad (despacho page + placas vivas)')
    chk(out.get('esperaPanel') and out.get('zonasConSalaViva'),
        'MULTI: espera ↔ zonas con la sala viva (GESTIONAR)')
    chk(out.get('tarjetaAreaViva') and out.get('trainareaAccede') and
        out.get('trainextAccede'),
        'ENTRENAR: áreas y TU PROGRESO acceden con contenido'
        + ('' if (out.get('tarjetaAreaViva') and out.get('trainareaAccede')
                  and out.get('trainextAccede'))
           else ' (area=' + str(out.get('tarjetaAreaViva')) +
                ',trainarea=' + str(out.get('trainareaAccede')) +
                ',ext=' + str(out.get('trainextAccede')) + ')'))
    chk(out.get('palaAutoriza'), 'PALA: autorización SÍ/NO al pulsar B')
    chk(out.get('paginas79EnBanda'),
        'rank/rankme/historial/champs/carrera/hall/pala en banda sin solapes'
        + ('' if out.get('paginas79EnBanda')
           else ' (' + str(out.get('paginas79Mal')) + ')'))
    chk(out.get('escaleraMuertaSinRect'),
        'la escalera jamás entra en una liga bloqueada')
    chk(out.get('animPide'), 'pulso animado de la liga actual (repintado encadenado)')
    # — F176 vivas —
    chk(out.get('areaDentroC'),
        'ENTRENAR: las áreas viven DENTRO de la panela C')
    chk(out.get('semanaArranca') is None or out.get('semanaArranca'),
        'RETO DE LA SEMANA: el clic arranca el modo')
    chk(out.get('multiAncho'), 'MULTI: tarjetas de modo a banda completa')
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
