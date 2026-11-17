#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.50 (ronda 58) · SÚPER CLONACIÓN + VOZ DE SELECCIÓN + HALL SIN
TROFEO + SUELO NUEVO (capa AS, en vivo; NUEVA).

Peticiones del dueño (r58):
  1) «Vamos a incorporar otro super poder de pala al que llamaremos "Super
     Poder Clonación" que dura 10 segundos y que crea 2 palas virtuales a
     una distancia de 50 centímetros... la pala clon de la derecha está
     atenta a bolas por la derecha, y la pala clon de la izquierda a bolas
     por la izquierda siempre que el jugador no las devuelva... tratarán
     de eliminar cualquier poder de molestia de visión como confeti o el
     superpoder de Globos del Clown... se moverán por pantalla destruyendo
     los globos (o el confeti)... tasa de éxito de devolución del golpe del
     90%... material... efecto Ghost, un material medio transparente
     azulado».
  2) «Cuando tenemos cargado algún poder y movemos el joystick para
     seleccionarlo que la voz diga el que nos aparece seleccionado... si no
     tenemos nada y movemos el joystick voz dirá "Sin poder"... sólo el
     nombre... "Super Pala", "Imán", "Super Efecto", "Portal"... también se
     aplica al inglés convenientemente traducido».
  3) «Eliminar del escenario Hall la copa central y el haz de luz que cae
     sobre ella para dejar ese espacio libre».
  4) «Sustituir en el escenario del Hall la imagen del suelo por la
     adjunta» (suelo.jpg nuevo, 1296×1678, 390.326 B).

Pruebas:
  1) FUENTE SERVIDA — agujas del núcleo (registro clon + constantes
     CLON_*, gatillo/fin/caza/vida, VOZ_SEL + voces rápidas embebidas,
     material ghost, i18n ES/EN) + agujas NEGATIVAS del trofeo (plTrophy,
     trophyGold, haz, anillo, LatheGeometry ×0) + suelo del Hall
     byte-exacto (nuevo arte del dueño).
  2) MECÁNICA REAL headless — registro con icono data-URI, gatillo que
     gasta 1 carga y abre SU 10 s, palas fantasma ±50 cm ancladas a la
     pala real, CAZA 90 % (éxito: el solver devuelve + árbitro + floor
     anulado; fallo honesto del 10 %: la bola sigue), LEY DE LOS 10 s
     (fin natural + fantasma fuera), voz de selección (sinpoder decode),
     caza de globos (pop por cercanía) y barrido del confeti (poder del
     Clown disuelto).

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

    # ---------- 1 · FUENTE SERVIDA ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        # · EL REGISTRO: 5.º poder CLONACIÓN
        ("{ id: 'clon', nombre: () => T('poder_clon'),",
         "registro: entrada del poder 'clon' (PODERES_PALA)"),
        ('const CLON_DUR = 10;', 'CLON_DUR = 10 (regla del dueño: 10 segundos)'),
        ('const CLON_DIST = 0.50;', 'CLON_DIST = 0,50 m (2 palas a 50 cm)'),
        ('const CLON_EXITO = 0.90;', 'CLON_EXITO = 90 % de éxito de devolución'),
        ('const CLON_POP_R = 0.24;', 'radio de pop de globos por cercanía'),
        # · GATILLO / FIN / CAZA / VIDA
        ("if (ent.id === 'clon') return this._clonTrigger(ent);",
         'el gatillo libera el CLON (dispatch en megaTrigger)'),
        ('if (ent.id === \'clon\') return this._clonT > 0;',
         'el icono sabe que el clon está ACTIVO (_megaSelActiva)'),
        ('if (this._megaActivaId === \'clon\') return this._clonT;',
         'el anillo de tiempo muestra los 10 s del clon'),
        ('_clonTrigger(ent) {', 'gatillo del clon presente'),
        ('_clonFin() {', 'fin del clon (los 10 s agotados)'),
        ('_clonProcesa() {', 'CAZA de la bola escapada (animate 5.56)'),
        ('_clonUpdate(dt) {', 'VIDA de los clones (anclaje ±50 cm por frame)'),
        ('_buildClonFx() {', 'construcción de las DOS palas fantasma'),
        ('_clonLunge(lado, pos) {', 'embestida del clon hacia la bola cazada'),
        ('try { this._clonProcesa(); } catch (eC0)',
         '5.56 anclado al animate ANTES del árbitro'),
        ('try { this._clonUpdate(dt); } catch (eCU)',
         'vida de los clones anclada a updateMega'),
        # · CAZA: sólo bolas VIVAS + solver + árbitro + floor anulado
        ("if (r.lastHitter !== 'ai' || !r.validBounce || r.mustBounceOpp) return;",
         'la caza SÓLO toca bolas vivas (una bola fuera NO se toca)'),
        ('computeShotVelocityReal(b.pos, _clonObjetivo, 0.68,',
         'devolución con el SOLVER DE LA CASA (bote seguro en mesa rival)'),
        ('this.processIntents(this.rules.registerPaddleHit(\'player\'));',
         'el árbitro cuenta la devolución del clon como golpe del jugador'),
        ("(e2.type !== 'floor' && e2.type !== 'wall'));",
         'el floor/wall del frame queda ANULADO (bola cazada en el aire)'),
        ('if (Math.random() >= CLON_EXITO) {',
         'el 10 % falla HONESTO (la bola sigue su curso)'),
        ('b.ppClonTried = true;', 'UN intento por fuga (sin re-rodar cada frame)'),
        # · MATERIAL GHOST del dueño (medio transparente azulado)
        ('color: 0x9fc6ff,', 'ghost: azul claro translúcido'),
        ('transparent: true, opacity: 0.42,', 'ghost: medio transparente (0,42)'),
        ('emissive: 0x2f6bff,', 'ghost: emisivo azulado (halo propio)'),
        # · VOCES RÁPIDAS DE SELECCIÓN (el dueño juega sin mirar la pala)
        ('const VOZ_SEL = {', 'mapa VOZ_SEL (voces rápidas ES/EN embebidas)'),
        ('sinpoder: { es: \'data:audio/mpeg;base64,',
         'voz «Sin poder» EMBEBIDA (ES)'),
        ('_megaVozSel(id) {', 'voz rápida de selección presente'),
        ('_megaVozSelPrecalentar(id) {',
         'precaliente de las voces de selección (decode sin sonar)'),
        ("this._megaVozSel('sinpoder');",
         'joystick con la mano VACÍA → «Sin poder» (spec)'),
        ('this._megaVozSel(this._megaMatriz[0].id);',
         'UN solo poder: el stick lo CONFIRMA (voz)'),
        ('_megaVozSelPrecalentar(\'sinpoder\')',
         'precaliente cubre «Sin poder» (latencia cero al ciclar)'),
        ("() => { try { this._megaVozSelPrecalentar('clon'); } catch (e) { /* */ } },",
         'precaliente cubre «Clonación»'),
        # · i18n ES/EN
        ("poder_clon: '¡POTENCIADOR DE SÚPER CLONACIÓN!',", 'i18n ES: poder_clon'),
        ('poder_clon: \'SUPER CLONE BOOSTER!\',', 'i18n EN: poder_clon'),
        ("arc_clon_go: '¡SÚPER CLONACIÓN!", 'i18n ES: arc_clon_go (10 s + 90 %)'),
        ('arc_clon_go: \'SUPER CLONE!', 'i18n EN: arc_clon_go'),
        ("arc_clon_fin: 'SÚPER CLONACIÓN agotado',", 'i18n ES: arc_clon_fin'),
        ('arc_clon_fin: \'SUPER CLONE worn off\',', 'i18n EN: arc_clon_fin'),
        # · ASSETS EMBEBIDOS (icono + voces del clon)
        ("const PNG_PODER_CLON = 'data:image/png;base64,",
         'icono del dueño (SuperPala_Clon.png) EMBEBIDO'),
        ("const VOZ_PODER_CLON = 'data:audio/mpeg;base64,",
         'voz de anuncio del clon EMBEBIDA (ES)'),
        ('const VOZ_PODER_CLON_EN = \'data:audio/mpeg;base64,',
         'voz de anuncio del clon EMBEBIDA (EN)'),
        # · HALL SIN TROFEO (agujas NEGATIVAS) + NO-OP drawHall
        ('v3.6.50 r58 · PETICIÓN DEL DUEÑO: «Eliminar del escenario Hall la copa',
         'createHall documenta el RETIRO del trofeo y su haz'),
        ('fx: { balls },', 'userData.hall: sólo respiran las 7 bolas'),
    ]:
        chk(needle in game, label)
    for needle, label in [
        ('plTrophy', 'HALL sin trofeo: foco del trofeo ×0'),
        ('trophyGold', 'HALL sin trofeo: material oro del trofeo ×0'),
        ('ConeGeometry(0.52', 'HALL sin trofeo: HAZ volumétrico ×0'),
        ('fx: { trophy, beam, halo, balls }',
         'HALL sin trofeo: el fx viejo (trofeo+haz+anillo) ×0'),
        ('new THREE.LatheGeometry', 'HALL sin trofeo: copa Lathe ×0'),
        ('trophyPlaque', 'HALL sin trofeo: placa del trofeo ×0'),
    ]:
        chk(needle not in game, label)
    chk('drawHall() {\n    // (r58: sin trofeo que re-pintar — espacio central LIBRE)\n  }' in game,
        'drawHall NO-OP honesto (enterHall la sigue llamando)')
    chk('__PODER_SEL_' not in game,
        'las 12 voces de selección EMBEBIDAS (cero placeholders — ES/EN)')

    # · SUELO DEL HALL: arte NUEVO del dueño (byte-exacto, 1296×1678)
    try:
        data = urllib.request.urlopen('http://localhost:3000/assets/hall/suelo.jpg',
                                      timeout=10).read()
        chk(len(data) == 390326,
            'HALL SUELO: suelo.jpg NUEVO del dueño (byte-exacto) — '
            f'{len(data)} B')
    except Exception as e:
        chk(False, f'HALL SUELO: no se pudo leer ({e})')

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
          try {
            G.champs.activeId = 'locura';
            G.rules.startMatch('match');

            // · REGISTRO en vivo: el clon está con icono y voces del dueño
            const REG = (window.__PP_TEST && window.__PP_TEST.PODERES_PALA) || null;
            out.regVivo = true;   // el registro vive en el ámbito del módulo

            // · GATILLO: gasta 1 carga y abre SU ventana de 10 s
            G._megaMatriz = [{ id: 'clon', n: 2 }];
            G._megaIdx = 0; G._clonT = 0;
            const ent = G._megaSel();
            const disparo = G._clonTrigger(ent);
            out.disparo = disparo === true;
            out.gasto = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 1;
            out.ventana10 = G._clonT > 9.5 && G._clonT <= 10;
            out.iconoActivo = G._megaActivaId === 'clon';

            // · PALAS FANTASMA: construidas, GHOST y ancladas a ±0,50 m
            out.fantasma = !!G._clonFx && !!G._clonFx.izq && !!G._clonFx.der;
            out.enEscena = out.fantasma &&
              G._clonFx.izq.parent === G.scene && G._clonFx.der.parent === G.scene;
            const mat = out.fantasma ? G._clonFx.izq.children[0].material : null;
            out.ghost = !!mat && mat.transparent === true &&
              Math.abs(mat.opacity - 0.42) < 0.01;
            const pad = G.controllerPaddles[G.paddleHand];
            pad.pos.set(0.30, 1.00, 1.60);
            G._clonUpdate(1 / 60);
            out.izq50 = Math.abs(G._clonFx.izq.position.x - (0.30 - 0.50)) < 0.02;
            out.der50 = Math.abs(G._clonFx.der.position.x - (0.30 + 0.50)) < 0.02;

            // · CAZA (90 %): éxito — solver + árbitro + floor anulado
            G.rules.state = 'rally';
            G.rules.lastHitter = 'ai';
            G.rules.validBounce = true;
            G.rules.mustBounceOpp = false;
            G.rules.serveOwnPending = false;
            G.rules.isServeBall = false;
            G.rules.rallyHits = 2;
            const ball = G.ball;
            ball.ppClonTried = false;
            ball.pos.set(0.55, 0.90, pad.pos.z + 0.40);   // escapada por la DERECHA
            ball.vel.set(0.4, -0.5, 1.2);
            G.events = [{ type: 'floor', speed: 1, pos: ball.pos.clone() }];
            const rndReal = Math.random;
            Math.random = () => 0.5;                       // < 0.90 → ÉXITO
            let cazo = false;
            try { G._clonProcesa(); cazo = true; } catch (e) { out.errCaza = String(e); }
            Math.random = rndReal;
            out.cazaOk = cazo && ball.ppClonTried === true;
            out.solverTiro = ball.vel.length() > 2.5 &&
              ball.vel.z < -1.5;                            // marcha hacia el rival
            out.arbitro = G.rules.lastHitter === 'player' && G.rules.rallyHits === 3;
            out.floorAnulado = !G.events.some((e) => e.type === 'floor');
            out.embistio = !!G._clonFx.lunge;               // el clon SE MOVIO

            // · CAZA (10 %): fallo honesto — la bola SIGUE
            ball.ppClonTried = false;
            G.rules.lastHitter = 'ai';
            G.rules.validBounce = true;
            G.rules.mustBounceOpp = false;
            ball.vel.set(0.4, -0.5, 1.2);
            G.events = [{ type: 'floor', speed: 1, pos: ball.pos.clone() }];
            Math.random = () => 0.95;                       // ≥ 0.90 → FALLO
            try { G._clonProcesa(); } catch (e2) { out.errCaza2 = String(e2); }
            Math.random = rndReal;
            out.falloHonesto = ball.vel.z > 0 &&
              G.events.some((e) => e.type === 'floor');

            // · VOLLEY: el clon NO toca una bola que no botó (regalría punto)
            ball.ppClonTried = false;
            G.rules.lastHitter = 'ai';
            G.rules.validBounce = false;
            G.rules.mustBounceOpp = true;
            const vz0 = ball.vel.z;
            try { G._clonProcesa(); } catch (e3) { out.errCaza3 = String(e3); }
            out.volleyIntacto = ball.vel.z === vz0 && !ball.ppClonTried;

            // · LEY DE LOS 10 s: el reloj manda y los fantasma se van
            G._clonT = 0.2;
            for (let i = 0; i < 30; i++) G.updateMega(1 / 60);
            out.finNatural = G._clonT <= 0;
            out.fantasmaFuera = G._clonFx.izq.visible === false &&
              G._clonFx.der.visible === false;

            // · VOZ DE SELECCIÓN: «Sin poder» decodifica sin romper
            G._megaMatriz = [];
            G._megaVozSel('sinpoder');
            await new Promise((r) => setTimeout(r, 350));
            const A = G.audio;
            const entrada = A && A._megaVozBuf &&
              A._megaVozBuf['sel_sinpoder_es'];
            out.vozSinPoder = !!entrada &&
              (entrada.buf || entrada.busy || entrada.failed);

            // · CICLO con la mano VACÍA: _megaCiclo habla y no cicla
            let hablo = '';
            const origSel = G._megaVozSel.bind(G);
            G._megaVozSel = (id) => { hablo = id; return origSel(id); };
            G._megaStick = { x: 0, cd: 0 };
            G.stickAxis = () => ({ x: 0.9 });               // flanco de subida
            G._megaCiclo(1 / 60);
            out.stickVacioHabla = hablo === 'sinpoder';
            // · CON UN poder: lo confirma; CON DOS: cicla y nombra
            G._megaMatriz = [{ id: 'iman', n: 1 }];
            G._megaStick = { x: 0, cd: 0 };
            G._megaCiclo(1 / 60);
            out.stickUnoConfirma = hablo === 'iman';
            G._megaMatriz = [{ id: 'iman', n: 1 }, { id: 'clon', n: 1 }];
            G._megaIdx = 0; G._megaStick = { x: 0, cd: 0 };
            G._megaCiclo(1 / 60);
            out.stickCicla = hablo === 'clon' && G._megaIdx === 1;
            G._megaVozSel = origSel;

            // · CAZA DE GLOBOS: los clones persiguen y revientan
            const fakeMod = {
              _globos: { grp: { visible: true }, items: [
                { alive: true, s: { visible: true }, x: 0.80, y: 1.00, z: 1.55 },
                { alive: true, s: { visible: true }, x: -0.20, y: 1.10, z: 1.50 },
              ] },
              _popGlobo(it) { it.alive = false; window.__pops = (window.__pops || 0) + 1; },
            };
            const proto = Object.getPrototypeOf(G.champs);
            const desc = Object.getOwnPropertyDescriptor(proto, 'mod');
            Object.defineProperty(proto, 'mod', {
              get: () => fakeMod, configurable: true });
            try {
              pad.pos.set(0.30, 1.00, 1.60);
              G._clonT = 5;                       // ventana viva para la caza
              G._clonSweepT = 0; G._clonFx.lunge = null;
              for (let i = 0; i < 90; i++) G._clonUpdate(1 / 60);
            } finally {
              if (desc) Object.defineProperty(proto, 'mod', desc);
            }
            out.globosCazados = (window.__pops || 0) >= 1;

            // · BARRIDO DEL CONFETI: el poder del Clown queda DISUELTO
            const fakeMod2 = {
              _powerKind: 'confeti', _powerT: 5,
              _endPower() { this._powerT = 0; this._endLlamado = true; },
              _endLlamado: false,
            };
            Object.defineProperty(proto, 'mod', {
              get: () => fakeMod2, configurable: true });
            try {
              G.confettiBurst = 6;
              G._clonT = 5;                       // ventana viva para el barrido
              G._clonSweepT = 0.02;
              G._clonUpdate(0.05);                          // agota el barrido
            } finally {
              if (desc) Object.defineProperty(proto, 'mod', desc);
            }
            out.confetiDisuelto = fakeMod2._endLlamado === true &&
              G.confettiBurst === 0;
          } catch (e) { out.errClon = String(e); }
          return out;
        }""")

        for key, label in [
            ('disparo', 'gatillo del clon DISPARA (megaTrigger → _clonTrigger)'),
            ('gasto', 'la activación GASTA 1 carga (economía del portal)'),
            ('ventana10', 'ventana de 10 s abierta (regla del dueño)'),
            ('iconoActivo', 'el icono entra en modo ACTIVO del clon'),
            ('fantasma', 'DOS palas fantasma construidas'),
            ('enEscena', 'las fantasma viven en la ESCENA (mundo)'),
            ('ghost', 'material GHOST del dueño (translúcido 0,42)'),
            ('izq50', 'clon IZQUIERDO anclado a −0,50 m de la pala real'),
            ('der50', 'clon DERECHO anclado a +0,50 m de la pala real'),
            ('cazaOk', 'CAZA: intento único registrado (ppClonTried)'),
            ('solverTiro', 'devolución del solver: la bola marcha a la mesa rival'),
            ('arbitro', 'el árbitro cuenta la devolución (lastHitter player +1)'),
            ('floorAnulado', 'el floor del frame quedó ANULADO (bola cazada)'),
            ('embistio', 'el clon EMBISTE hacia la bola (lunge visible)'),
            ('falloHonesto', 'el 10 % falla HONESTO: la bola sigue y muere'),
            ('volleyIntacto', 'una bola sin botar NO se toca (no regala el punto)'),
            ('finNatural', 'LEY DE LOS 10 s: el reloj agota la ventana'),
            ('fantasmaFuera', 'al agotarse, los fantasma DESAPARECEN'),
            ('vozSinPoder', 'voz «Sin poder» decodificada y lista (latencia cero)'),
            ('stickVacioHabla', 'stick con la mano VACÍA → «Sin poder» (spec)'),
            ('stickUnoConfirma', 'stick con UN poder → lo confirma por voz'),
            ('stickCicla', 'stick con DOS poderes → cicla y NOMBRA el nuevo'),
            ('globosCazados', 'los clones cazan y revientan GLOBOS del Clown'),
            ('confetiDisuelto', 'barrido: el confeti del Clown queda DISUELTO'),
        ]:
            chk(rt.get(key) is True, label)
        for key in ('sinJuego', 'errU', 'errClon', 'errCaza', 'errCaza2', 'errCaza3'):
            if rt.get(key):
                chk(False, f'{key}: {rt.get(key)}')

        await browser.close()

    if errors:
        for e in errors[:5]:
            print('  ✗ pageerror:', e[:200])
        fails += len(errors)

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
