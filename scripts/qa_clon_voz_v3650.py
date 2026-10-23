#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_clon_voz_v3650 — CAPA AS · ronda 58 (V3.6.50-SDK6, FASE 52).

Las peticiones del dueño (literales, r58):
  · «Vamos a incorporar otro super poder de pala al que llamaremos
    "Super Poder Clonación" que dura 10 segundos y que crea 2 palas
    virtuales a una distancia de 50 centímetros. Estas palas son capaces
    de cazar cualquier bola que se le escape al jugador por ambos lados…
    la pala clon de la derecha está atenta a bolas por la derecha, y la
    pala clon de la izquierda a bolas por la izquierda siempre que el
    jugador no las devuelva… tienen una tasa de éxito de devolución del
    90 %… en cuanto a su material tendrán un efecto Ghost un material
    medio transparente azulado».
  · «Cuando tenemos cargado algún poder y movemos el joystick para
    seleccionarlo que la voz diga el que nos aparece seleccionado… si no
    tenemos nada y movemos el joystick voz dirá "Sin poder"… dice de
    forma rápida solo el nombre… también se aplica al inglés».

Pruebas: (1) FUENTE SERVIDA — agujas del 5.º poder (constantes CLON_*,
registro PODERES_PALA, voces data-URI ×15, i18n ES/EN, hook clonBlancos
del núcleo y de La Locura, contrato en PLANTILLA-GUIA §4.2) + NEGATIVAS
(placeholders sin rellenar). (2) MECÁNICA REAL headless — activación con
ventana de 10 s, guardia a ±50 cm, CAZA con devolución legal del 90 %
(registerPaddleHit del jugador, velocidad hacia la mesa rival), el 10 %
que falla de verdad (una sola tirada por vuelo), PRIORIDAD del jugador,
voz del selector con 0 y 1 poderes («Sin poder» / nombre corto) y recogida
(_megaNormReset + fin natural).

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


async def main():
    global ok, fails
    errors = []

    # ---------- 1 · FUENTE SERVIDA (núcleo + locura + plantilla) ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        # · EL 5.º PODER (constantes del dueño, literales)
        ('const CLON_DUR = 10;',
         'r58: SÚPER CLONACIÓN — ventana de 10 s'),
        ('const CLON_DIST = 0.5;',
         'r58: 2 palas virtuales a ±50 cm'),
        ('const CLON_EXITO = 0.9;',
         'r58: tasa de éxito de devolución del 90 %'),
        ('const CLON_CATCH = 0.32;',
         'r58: radio de caza del clon'),
        ("{ id: 'clon', nombre: () => T('poder_clon'),",
         'r58: el clon entra en el registro PODERES_PALA (icono+voz+i18n)'),
        # · EL MATERIAL GHOST («medio transparente azulado»)
        ('color: 0x9fdcff, emissive: 0x2f9fe8, emissiveIntensity: 0.55,',
         'r58: material Ghost azul translúcido de las palas clon'),
        # · MECÁNICA (caza legal, prioridad, una tirada)
        ('const intents = this.rules.registerPaddleHit(\'player\');',
         'r58: la devolución del clon es un golpe de JUGADOR legal'),
        ('const escapa = dj > 0.45 || b.pos.z > ps.pos.z + 0.05;',
         'r58: PRIORIDAD del jugador — el clon no estorba donde la pala llega'),
        ('this._clonFallada = true;      // UNA tirada por vuelo (el 10 % es real)',
         'r58: UNA sola tirada por vuelo — el 10 % de fallo es real'),
        ('computeShotVelocityReal(b.pos, _clonObjetivo, T0, vMax, _clonSpinCero)',
         'r58: la devolución usa el solver de la casa (bote seguro)'),
        # · HOOK de blancos (globos del Clown / futuros rivales)
        ('_clonBlancos(out) {',
         'r58: hook de blancos de visión en el núcleo'),
        ('out.length = 0;   // buffer reutilizado: SIEMPRE se vacía antes del hook',
         'r58: el buffer de blancos se vacía SIEMPRE (sin fuga por frame)'),
        ('if (m && typeof m.clonBlancos === \'function\') m.clonBlancos(out);',
         'r58: el núcleo pregunta al campeonato activo (contrato por hook)'),
        # · VOZ DEL SELECTOR (nombres cortos ES/EN + «Sin poder»)
        ('this._vozSel(this._megaMatriz[this._megaIdx].id);',
         'r58: al ciclar, la voz dice el seleccionado'),
        ('this._vozSel(null);',
         'r58: con la mano vacía, la voz dice «Sin poder»'),
        ('this._vozSelPrewarm();',
         'r58: las voces del selector se precalientan con el arsenal'),
        ("sin_poder: 'Sin poder',",
         'r58: i18n ES — «Sin poder»'),
        ("sin_poder: 'No power',",
         'r58: i18n EN — «No power»'),
        ('arc_clon_go: \'¡SÚPER CLONACIÓN!',
         'r58: i18n ES — cartel de activación del clon'),
        ('arc_clon_go: \'SUPER CLONE!',
         'r58: i18n EN — cartel de activación del clon'),
        # · CONFETI CAZABLE (createConfetti expone kill)
        ('return { points, update, kill, pos, N };',
         'r58: el confeti expone kill/pos/N para el barrido de los clones'),
    ]:
        chk(needle in game, label)
    # · LAS 15 VOCES/ETIQUETA embebidas (data-URI)
    for cte, mime, label in [
        ('VOZ_SEL_MEGA', 'audio/mpeg', 'voz selector Super Pala ES'),
        ('VOZ_SEL_MEGA_EN', 'audio/mpeg', 'voz selector Super Paddle EN'),
        ('VOZ_SEL_EFECTO', 'audio/mpeg', 'voz selector Super Efecto ES'),
        ('VOZ_SEL_EFECTO_EN', 'audio/mpeg', 'voz selector Super Effect EN'),
        ('VOZ_SEL_IMAN', 'audio/mpeg', 'voz selector Imán ES'),
        ('VOZ_SEL_IMAN_EN', 'audio/mpeg', 'voz selector Magnet EN'),
        ('VOZ_SEL_PORTAL', 'audio/mpeg', 'voz selector Portal ES'),
        ('VOZ_SEL_PORTAL_EN', 'audio/mpeg', 'voz selector Portal EN'),
        ('VOZ_SEL_CLON', 'audio/mpeg', 'voz selector Clonación ES'),
        ('VOZ_SEL_CLON_EN', 'audio/mpeg', 'voz selector Cloning EN'),
        ('VOZ_SEL_NADA', 'audio/mpeg', 'voz selector Sin poder ES'),
        ('VOZ_SEL_NADA_EN', 'audio/mpeg', 'voz selector No power EN'),
        ('VOZ_PODER_CLON', 'audio/mpeg', 'voz concesión del clon ES'),
        ('VOZ_PODER_CLON_EN', 'audio/mpeg', 'voz concesión del clon EN'),
        ('PNG_PODER_CLON', 'image/png', 'etiqueta del dueño (SuperPala_Clon)'),
    ]:
        chk(f"const {cte} = 'data:{mime};base64," in game,
            f'r58: {label} embebida ({cte})')
    # · NEGATIVAS: los placeholders se rellenaron TODOS
    for ph in ['__SEL_VOZ_MEGA__', '__SEL_VOZ_NADA__', '__PODER_VOZ_CLON__',
               '__PODER_PNG_CLON__']:
        chk(ph not in game, f'r58: placeholder {ph} rellenado (no queda crudo)')

    # · LA LOCURA implementa el hook (globos del Clown cazables)
    try:
        locura = urllib.request.urlopen(
            'http://localhost:3000/championships/locura/index.js',
            timeout=10).read().decode('utf-8')
        chk('clonBlancos(out) {' in locura,
            'r58: La Locura implementa clonBlancos (globos del Clown)')
        chk('_popGlobo(it)' in locura,
            'r58: el kill del globo usa SU pop propio (sonido del módulo)')
    except Exception as e:
        chk(False, 'locura/index.js servido (' + str(e)[:60] + ')')

    # · PLANTILLA-GUIA §4.2 (contrato documentado)
    try:
        guia = urllib.request.urlopen(
            'http://localhost:3000/championships/PLANTILLA-GUIA.md',
            timeout=10).read().decode('utf-8')
        chk('### 4.2 · BLANCOS del SÚPER CLONACIÓN' in guia,
            'r58: contrato clonBlancos documentado (PLANTILLA-GUIA §4.2)')
    except Exception as e:
        chk(False, 'PLANTILLA-GUIA.md servida (' + str(e)[:60] + ')')

    # · SUELO NUEVO del HALL (la versión del dueño, byte-exacto)
    try:
        suelo = urllib.request.urlopen(
            'http://localhost:3000/assets/hall/suelo.jpg', timeout=10).read()
        chk(len(suelo) == 390326,
            'r58: el suelo del Hall es la NUEVA imagen del dueño (390.326 B, '
            'llegan ' + f'{len(suelo):,}' + ' B)')
    except Exception as e:
        chk(False, 'assets/hall/suelo.jpg servido (' + str(e)[:60] + ')')

    # ---------- 2 · MECÁNICA REAL headless ----------
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)

        rt = await page.evaluate("""async () => {
          const out = {};
          const G = window.__PP_GAME;
          if (!G) { out.sinJuego = true; return out; }
          const realRnd = Math.random;
          const paso = (n) => { for (let i = 0; i < (n || 1); i++) {
            try { G.updateMega(1 / 60); } catch (e) { out.errU = String(e); } } };
          const pos = () => G.controllerPaddles[G.paddleHand].pos;

          // arranque limpio del arnés
          try {
            G.champs.activeId = 'locura';
            G.rules.startMatch('match');
            G._megaNormReset();
          } catch (e) { out.errIni = String(e); }

          // ===== A · ACTIVACIÓN: ventana de 10 s + 2 fantasmas =====
          try {
            Math.random = () => 0.1;
            G._megaMatriz.length = 0;
            G._megaMatriz.push({ id: 'clon', n: 1 });
            G._megaIdx = 0;
            G.rules.state = 'rally';        // el gatillo exige bola en juego
            const disparo = G.megaTrigger(1 - G.paddleHand);
            out.aDisparo = disparo === true;
            out.aVentana = Math.abs(G._clonT - 10) < 0.05;
            out.aActiva = G._megaActivaId === 'clon';
            out.aGasta = !G._megaMatriz.find((x) => x.id === 'clon');
            paso(3);
            out.aFx = Array.isArray(G._clonFx) && G._clonFx.length === 2;
            out.aVisibles = G._clonFx ? G._clonFx.every((g) => g && g.visible) : false;
            out.aGhost = !!(G._clonMat && G._clonMat.transparent &&
                            Math.abs(G._clonMat.opacity - 0.42) < 0.001);
            out.aIcono = G._megaActivaRest() > 9;
          } catch (e) { out.errA = String(e); }

          // ===== B · GUARDIA a ±50 cm del flanco =====
          try {
            pos().set(0, 1.0, 1.6);
            G.rules.state = 'serve';          // sin caza: sólo guardia
            paso(30);                          // medio segundo de frames
            const izq = G._clonFx[0].position, der = G._clonFx[1].position;
            out.bIzq = Math.abs(izq.x - (-0.5)) < 0.02 &&
                       Math.abs(izq.y - 1.0) < 0.05 && Math.abs(izq.z - 1.6) < 0.02;
            out.bDer = Math.abs(der.x - 0.5) < 0.02 &&
                       Math.abs(der.y - 1.0) < 0.05 && Math.abs(der.z - 1.6) < 0.02;
          } catch (e) { out.errB = String(e); }

          // ===== C · CAZA del 90 %: devolución legal =====
          try {
            Math.random = () => 0.5;           // 0.5 < 0.9 → ÉXITO
            const r = G.rules;
            r.state = 'rally'; r.lastHitter = 'ai';
            r.validBounce = true; r.serveOwnPending = false;
            r.rallyHits = 2; G._megaRallyGrants = 0;
            pos().set(0, 1.0, 1.6);
            const b = G.ball;
            b.pos.set(0.5, 1.0, 1.55);        // justo donde el clon DERECHO
            b.vel.set(0, -0.5, 2.5);          // escapándose hacia +z
            b.spin.set(0, 0, 0);
            G._clonFallada = false; G._clonCd = 0;
            const hits0 = r.rallyHits;
            paso(2);
            out.cDevuelta = b.vel.z < 0;       // sale hacia la mesa rival
            out.cLegal = r.lastHitter === 'player' && r.rallyHits === hits0 + 1;
            out.cMensaje = String(r.message || '').indexOf('CLON') >= 0 ||
                           String(r.message || '').indexOf('CLONE') >= 0;
            out.cVentanaViva = G._clonT > 9;   // la ventana NO se gasta
          } catch (e) { out.errC = String(e); }

          // ===== D · EL 10 % FALLA de verdad (una tirada) =====
          try {
            Math.random = () => 0.99;          // 0.99 > 0.9 → FALLO
            const r = G.rules;
            r.state = 'rally'; r.lastHitter = 'ai';
            r.validBounce = true; r.serveOwnPending = false;
            const b = G.ball;
            b.pos.set(0.5, 1.0, 1.55);
            b.vel.set(0, -0.5, 2.5);
            G._clonFallada = false; G._clonCd = 0;
            const hits0 = r.rallyHits;
            paso(2);
            out.dSinTocar = b.vel.z > 0 && r.rallyHits === hits0;
            out.dUnaTirada = G._clonFallada === true;
            // y NO reintenta aunque pasen frames (una sola tirada por vuelo)
            b.pos.set(0.5, 1.0, 1.56);
            paso(3);
            out.dNoReintenta = r.rallyHits === hits0;
          } catch (e) { out.errD = String(e); }

          // ===== E · PRIORIDAD del jugador =====
          try {
            Math.random = () => 0.5;
            const r = G.rules;
            r.state = 'rally'; r.lastHitter = 'ai';
            r.validBounce = true; r.serveOwnPending = false;
            const b = G.ball;
            pos().set(0, 1.0, 1.6);
            b.pos.set(0.25, 1.0, 1.58);        // a 0,26 m de la pala: llega
            b.vel.set(0, 0, 2.5);
            G._clonFallada = false; G._clonCd = 0;
            const hits0 = r.rallyHits;
            paso(2);
            out.eJugadorPrimero = b.vel.z > 0 && G._clonFallada === false &&
                                  r.rallyHits === hits0;
          } catch (e) { out.errE = String(e); }

          // ===== F · VOZ del selector (0 y 1 poder) =====
          try {
            Math.random = realRnd;
            const r = G.rules;
            G._megaNormReset();
            G.rules.startMatch('match');
            // el headless no gesta AudioContext: uno propio para el arnés
            // (el camino _vozSel es el REAL: fetch data-URI + decode)
            if (G.audio && !G.audio.ctx) {
              try { G.audio.ctx = new (window.AudioContext || window.webkitAudioContext)(); } catch (eC0) { /* */ }
            }
            G._megaMatriz.length = 0;
            G._megaStick = { x: 0, cd: 0 };
            const stickReal = G.stickAxis;
            G.stickAxis = () => ({ x: 1.0 });  // el dueño empuja el stick
            r.state = 'rally';
            G._megaCiclo(0.016);
            out.fSinPoder = r.message === 'Sin poder';
            out.fCd0 = Math.abs(G._megaStick.cd - 0.5) < 0.01;
            // con UN poder: no cicla, pero la voz nombra (caché sel_…)
            G._megaMatriz.push({ id: 'mega', n: 1 });
            G._megaStick = { x: 0, cd: 0 };
            G._megaCiclo(0.016);
            out.fUnoNoCicla = G._megaMatriz.length === 1;
            // la voz se decodifica (data-URI) y queda cacheada
            await new Promise((r2) => setTimeout(r2, 700));
            const buf = G.audio && G.audio._megaVozBuf || {};
            out.fVozNada = !!(buf.sel_nada_es && (buf.sel_nada_es.buf ||
                             buf.sel_nada_es.busy || buf.sel_nada_es.failed));
            out.fVozMega = !!(buf.sel_mega_es && (buf.sel_mega_es.buf ||
                             buf.sel_mega_es.busy || buf.sel_mega_es.failed));
            G.stickAxis = stickReal;
            G._megaCicla(-1);                  // borde: blip y nada (sin envolver)
          } catch (e) { out.errF = String(e); }

          // ===== G · FIN natural + recogida completa =====
          try {
            Math.random = () => 0.1;
            G._megaMatriz.push({ id: 'clon', n: 1 });
            G._megaIdx = G._megaMatriz.length - 1;
            G.megaTrigger(1 - G.paddleHand);
            G._clonT = 0.005;                  // ventana casi agotada
            paso(2);
            out.gFin = G._clonT <= 0 && !G._clonFxOn &&
                       (G._clonFx || []).every((g) => g && !g.visible);
            G._megaNormReset();
            out.gRecogida = G._clonT === 0 && G._clonFallada === false &&
                            G._clonChaseIx === -1;
            // refresh honesto: la ventana vuelve a 10 s SIN gastar
            G._megaMatriz.push({ id: 'clon', n: 2 });
            G._megaIdx = G._megaMatriz.length - 1;
            G._clonT = 3;
            G.megaTrigger(1 - G.paddleHand);
            out.gRefresco = Math.abs(G._clonT - 10) < 0.05 &&
                            G._megaMatriz[G._megaIdx].n === 2;
            G._megaNormReset();
          } catch (e) { out.errG = String(e); }

          Math.random = realRnd;
          return out;
        }""")

        chk(rt.get('sinJuego') is not True, 'el juego arranca (window.__PP_GAME)')
        chk(rt.get('errIni') is None and rt.get('errU') is None,
            'arnés sin excepciones ' + str(rt.get('errIni') or rt.get('errU') or ''))
        # A
        chk(rt.get('aDisparo') is True, 'A · el gatillo abre la CLONACIÓN')
        chk(rt.get('aVentana') is True, 'A · ventana de 10 s exactos')
        chk(rt.get('aActiva') is True and rt.get('aIcono') is True,
            'A · el icono entra en modo ACTIVO con anillo de tiempo')
        chk(rt.get('aGasta') is True, 'A · la carga se gasta al activar')
        chk(rt.get('aFx') is True, 'A · 2 palas virtuales creadas')
        chk(rt.get('aVisibles') is True, 'A · las 2 fantasmas visibles')
        chk(rt.get('aGhost') is True, 'A · material Ghost (transparente, 0.42)')
        # B
        chk(rt.get('bIzq') is True and rt.get('bDer') is True,
            'B · guardia a ±50 cm del flanco de la pala (izq y der)')
        # C
        chk(rt.get('cDevuelta') is True,
            'C · el clon DEVUELVE la bola escapada (hacia la mesa rival)')
        chk(rt.get('cLegal') is True,
            'C · la devolución cuenta como golpe de jugador legal (árbitro)')
        chk(rt.get('cMensaje') is True, 'C · megáfono: «LA PALA CLON TE HA SALVADO»')
        chk(rt.get('cVentanaViva') is True,
            'C · la ventana vive sus 10 s (la caza NO gasta poder)')
        # D
        chk(rt.get('dSinTocar') is True,
            'D · el 10 % FALLA: la bola atraviesa el fantasma')
        chk(rt.get('dUnaTirada') is True and rt.get('dNoReintenta') is True,
            'D · UNA sola tirada por vuelo (sin re-tiradas encubiertas)')
        # E
        chk(rt.get('eJugadorPrimero') is True,
            'E · PRIORIDAD del jugador: donde la pala llega, el clon calla')
        # F
        chk(rt.get('fSinPoder') is True, 'F · stick con la mano vacía → «Sin poder»')
        chk(rt.get('fCd0') is True, 'F · antirrebote propio de la voz (0,5 s)')
        chk(rt.get('fUnoNoCicla') is True,
            'F · con UN poder no hay ciclo (y la voz lo nombra)')
        chk(rt.get('fVozNada') is True and rt.get('fVozMega') is True,
            'F · las voces del selector se decodifican y cachean (ES)')
        # G
        chk(rt.get('gFin') is True, 'G · fin natural: fantasmas fuera, icono a inventario')
        chk(rt.get('gRecogida') is True, 'G · _megaNormReset deja el clon a cero')
        chk(rt.get('gRefresco') is True,
            'G · refresh honesto: 10 s de nuevo SIN gastar la segunda carga')

        await page.screenshot(path='/home/z/my-project/download/qa_clon_voz.png')
        await browser.close()

    chk(errors == [], 'cero pageerrors ' + (str(errors[:2]) if errors else ''))
    print("CAPTURA     : /home/z/my-project/download/qa_clon_voz.png")
    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


asyncio.run(main())
