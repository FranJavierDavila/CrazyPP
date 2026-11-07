#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.36 · SUPERPODER DE PALA · MATRIZ + SÚPER EFECTO (capa AE, en vivo).

El diseño del dueño sobre la norma ×3 de v3.6.35:
  · «en caso de salir un potenciador distinto que NO elimine los actuales…
    una flecha al lado del icono… con el joystick del mando lo podemos
    seleccionar dando a derecha o izquierda como si de una matriz de
    potenciadores cargados» — PODER DISTINTO ENTRA en la matriz (orden de
    llegada), joystick ⟷ cicla el seleccionado, SOLO 1 icono visible,
    flechas ‹ › solo cuando hay vecino (SIN envolver en los bordes),
    multiplicadores ×2/×3 intactos.
  · «vamos a incorporar un nuevo potenciador… SuperPala_Efecto» — el SÚPER
    EFECTO: spin GENERADO ×2 (nunca el acumulado) con tope 2×spinMax,
    bote/Magnus amplificados SOLO en la bola marcada, ventana de 8 s o
    5 golpes con efecto.
  · «Los potenciadores SOLO aparecen en los campeonatos… NO en una
    modalidad diferente con un partido contra la máquina fuera de los
    campeonatos» — gate champs.active en megaEnabled().
  · «la voz que anuncia el poder es horrible, no es voz nativa castellana,
    debe ser nativa castellana y en caso de jugar en inglés traducir el
    audio» — 4 voces Piper embebidas (es_ES-davefx / en_US-lessac),
    seleccionadas por __ppLang.

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del núcleo (matriz, ciclo, flechas, registro de
     2 poderes, constantes del efecto, física marcada, voces ES/EN) + i18n
     ES/EN + regresiones del modelo v3.6.35 (sustitución) + plantilla +
     locura v26 intacta
  2) MECÁNICA REAL en headless — fuera de campeonato NO carga ni el gatillo
     responde · en campeonato: 11 carga · 22/33 acumula · 44 tope · poder
     distinto ENTRA a la matriz y se selecciona · ciclo ⟷ SIN envolver ·
     súper efecto: ventana 8 s/5 golpes, recarga, FX cian, multiplicador en
     la pala · mega alarga · gasta el SELECCIONADO · conmutador y hall.

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
MOD = "http://localhost:3000/championships/locura/index.js"

ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


async def main():
    errors = []

    # ---------- 1 · FUENTE SERVIDA ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ('SUPERPODER DE PALA · MATRIZ + SÚPER EFECTO', 'bloque del superpoder en el núcleo'),
        ('const PODERES_PALA', 'REGISTRO EXTENSIBLE de poderes'),
        ("{ id: 'mega', nombre: () => T('poder_mega'),", 'entrada MEGA del registro'),
        ("{ id: 'efecto', nombre: () => T('poder_efecto'),", 'entrada EFECTO del registro (2.º poder)'),
        ('voz: VOZ_PODER_MEGA, vozEn: VOZ_PODER_MEGA_EN, png: PNG_PODER_MEGA',
         'mega: voz ES + voz EN + PNG en el registro'),
        ('const PNG_PODER_EFECTO', 'PNG del poder EFECTO embebido'),
        ('const VOZ_PODER_EFECTO', 'voz del poder EFECTO embebida'),
        ('const VOZ_PODER_MEGA_EN', 'voz EN del mega embebida (traducida)'),
        ('const EFECTO_DUR = 8;', 'SÚPER EFECTO: ventana de 8 s'),
        ('const EFECTO_GOLPES = 5;', 'SÚPER EFECTO: 5 golpes con efecto'),
        ('const EFECTO_SPIN_MUL = 2;', 'SÚPER EFECTO: spin generado ×2'),
        ('const EFECTO_SPIN_MIN = 25;', 'SÚPER EFECTO: umbral de «golpe con efecto»'),
        ('efectoSpinTope: 2,', 'física: tope de rotación 2×spinMax'),
        ('efectoMagnusMul: 1.5,', 'física: Magnus ×1,5 solo en la bola marcada'),
        ('efectoBoteMul: 1.8,', 'física: acople del bote ×1,8 solo en la marcada'),
        ('this._megaMatriz = [];', 'MATRIZ de poderes (estado nuevo)'),
        ('this._megaIdx = 0;', 'índice del poder SELECCIONADO'),
        ('this._megaMatriz.push(ent);', 'poder distinto ENTRA en la matriz (NO sustituye)'),
        ('this._megaIdx = this._megaMatriz.length - 1;', 'el poder nuevo se SELECCIONA solo'),
        ('this._megaCicla(x > 0 ? 1 : -1);', 'JOYSTICK ⟷ cicla la matriz (flanco + antirrebote)'),
        ('if (this._megaIdx > 0) chev(24, -1);', 'flecha ‹ SOLO con vecino a la izquierda'),
        ('if (this._megaIdx < this._megaMatriz.length - 1) chev(232, 1);',
         'flecha › SOLO con vecino a la derecha (sin envolver)'),
        ('if (ent.id === \'efecto\') return this._efectoTrigger(ent);',
         'el gatillo libera el poder SELECCIONADO'),
        ('this._efectoT = EFECTO_DUR;', 'activación del súper efecto'),
        ('if (--this._efectoGolpes <= 0) { this._efectoFin(); break; }', '5.º golpe con efecto CIERRA la ventana'),
        ('const key = id + ((__ppLang === \'en\') ? \'_en\' : \'_es\');',
         'voz por PODER e IDIOMA (__ppLang)'),
        ('return !!(this.champs && this.champs.active);',
         'GATE: superpoderes SOLO en campeonatos'),
        ('SOLO en campeonatos', 'i18n ES: «SOLO en campeonatos» en los avisos'),
        ('championships only', 'i18n EN: «championships only» en los avisos'),
        ('poder_efecto:', 'i18n: nombre del poder efecto'),
        ('¡POTENCIADOR DE SÚPER EFECTO!', 'ES: megáfono del efecto'),
        ('¡SÚPER EFECTO! · spin ×2 · 8 s o 5 golpes con efecto', 'ES: mensaje de activación'),
        ('SUPER SPIN BOOSTER!', 'EN: nombre del poder efecto'),
        ('SUPER SPIN! · ×2 spin · 8 s or 5 boosted shots', 'EN: mensaje de activación'),
        ('const eMul = (pad.ppEfectoMul || 1) > 1 && !pad.serveFlight &&',
         'física: multiplicador del brush viaja EN LA PALA (y sólo en el intercambio, r55)'),
        ('if (eMul > 1) tmpS.multiplyScalar(eMul);', 'física: ×2 SOLO al brush generado'),
        ('if (ball.spin.length() > eTope) ball.spin.setLength(eTope);',
         'física: tope de seguridad sobre el resultado'),
        ('ball.ppEfecto = true;', 'física: la bola golpeada sale MARCADA'),
        ('bounceOnTable(vel, spin, impact, eM);', 'física: bote amplificado solo marcada'),
        ('applyAerodynamics(ball.vel, ball.spin, h, ball.dragMul,',
         'física: Magnus amplificado solo marcada'),
        ('ball.ppEfecto = false;', 'IA: su golpe LIMPIA la marca'),
        ('const emul = (on && this._efectoT > 0) ? EFECTO_SPIN_MUL : 1;',
         'el multiplicador solo con la ventana ACTIVA'),
        ('const icoOn = on && this._megaMatriz.length > 0 && !this._megaSelActiva();',
         'SOLO UN icono visible (el seleccionado, fuera si está activo)'),
        ('pp_pala_mejorada_v1', 'conmutador persistente «Pala Mejorada»'),
        ('_megaNormReset()', 'recogida completa con dispose'),
        ('this.updateMega(dt);', 'la norma corre en el bucle animate'),
        ('V3.6.36-SDK6', 'sello de versión servido'),
    ]:
        chk(needle in game, label)
    # REGRESIÓN: el modelo v3.6.35 (sustitución) y sus restos NO vuelven
    chk('_megaLoads' not in game, 'regresión: el estado único de cargas v3.6.35 ya no existe')
    chk('_megaPoder ' not in game and 'this._megaPoder =' not in game,
        'regresión: «poder único sustituido» ya no existe')
    chk('this._megaPng =' not in game, 'regresión: el PNG único dio paso a _megaPngs')
    chk('DISTINTO: SUSTITUYE' not in game, 'regresión: la sustitución fue sustituida por la matriz')
    chk('tongtong' not in game, 'regresión: la voz no nativa tongtong fuera del juego')
    chk(game.count('data:audio/mpeg;base64,') >= 4, '4 voces nativas embebidas (mega/efecto × es/en)')
    chk(game.count('data:image/png;base64,') >= 2, '2 iconos de poder embebidos (mega + efecto)')

    # módulo locura v26 intacto (la norma vive en el núcleo)
    try:
        served = urllib.request.urlopen(MOD, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer el módulo locura servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ("trigger: 'norma_rally11'", 'locura: playerPower apunta a la norma'),
        ('MEGA PALA es NORMATIVA del NÚCLEO', 'locura: nota de la mudanza al núcleo'),
    ]:
        chk(needle in served, label)
    for ausente, label in [
        ('_megaMatriz', 'locura: sin estado de matriz (es del núcleo)'),
        ('_efectoT', 'locura: sin estado del efecto (es del núcleo)'),
    ]:
        chk(ausente not in served, 'regresión: ' + label)

    # plantilla: la norma de la matriz documentada para campeonatos nuevos
    try:
        guia = urllib.request.urlopen(
            'http://localhost:3000/championships/PLANTILLA-GUIA.md',
            timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer PLANTILLA-GUIA.md servida:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    chk('2.4 SUPERPODER DE PALA · MATRIZ + SÚPER EFECTO' in guia,
        'plantilla: la norma de la MATRIZ documentada (sección 2.4)')
    chk('ENTRA en la matriz** (orden de llegada; NO sustituye)' in guia,
        'plantilla: regla de la matriz documentada')
    chk('**SOLO en campeonatos**' in guia, 'plantilla: solo-campeonatos documentado')
    chk('8 s o 5 golpes con efecto' in guia, 'plantilla: ventana del súper efecto documentada')
    chk('Prohibido para los módulos' in guia,
        'plantilla: prohibición de duplicar la mecánica')

    # ---------- 2 · MECÁNICA REAL (headless) ----------
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
          const G = window.__PP_GAME;
          const out = {};
          if (!G) { out.sinJuego = true; return out; }
          try { window.__pp2DPlay = true; } catch (e) { /* */ }
          try { localStorage.removeItem('pp_mega_norm_hint'); } catch (e) { /* */ }
          try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) { /* */ }
          G.palaMejorada = true;
          const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
          const libre = (G.paddleHand === 0) ? 1 : 0;
          const rndReal = Math.random;

          // estado fresco
          out.porDefecto = G.palaMejorada === true &&
            Array.isArray(G._megaMatriz) && G._megaMatriz.length === 0 &&
            G._megaIdx === 0 && G._megaT === 0 && G._efectoT === 0 &&
            G._megaFx === null && G._efectoFx === null && G._megaIcon === null;
          out.hayAPI = typeof G.updateMega === 'function' &&
            typeof G.megaTrigger === 'function' &&
            typeof G._megaCicla === 'function' &&
            typeof G._efectoTrigger === 'function' &&
            typeof G._megaVoz === 'function' &&
            typeof G._megaIconRefresh === 'function';

          // PARTIDO + rally controlado
          try { G.rules.startMatch('match'); } catch (e) { out.errMatch = String(e); }
          const paso = () => { try { G.updateMega(1 / 60); } catch (e) { out.errUpd = String(e); } };

          // · FUERA DE CAMPEONATO: rally de 44 golpes NO carga NADA
          G.champs.activeId = '';
          G.rules.state = 'rally'; G.rules.rallyHits = 44;
          paso(); paso();
          out.fueraSinCarga = G._megaMatriz.length === 0 && G._megaIcon === null;
          let tFuera = null;
          try { tFuera = G.megaTrigger(libre); } catch (e) { out.errFuera = String(e); }
          out.fueraGatilloLibre = tFuera === false;   // NO consume, NO avisa

          // · EN CAMPEONATO (activoId puesto a mano): la norma opera
          G.champs.activeId = 'locura';
          Math.random = () => 0;                       // SIEMPRE 'mega' (ids[0])
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 10;
          paso(); paso();
          out.diezSinCarga = G._megaMatriz.length === 0;
          G.rules.rallyHits = 11; paso();
          out.cargada = G._megaMatriz.length === 1 &&
            G._megaMatriz[0].id === 'mega' && G._megaMatriz[0].n === 1 &&
            G._megaIdx === 0;
          out.iconoVivo = Array.isArray(G._megaIcon) &&
            G._megaIcon.filter((s) => s).length === 2 &&
            G._megaIcon[0].visible === true;
          out.iconoAnclado = Math.abs(G._megaIcon[0].position.y + 0.034) < 0.006 &&
            Math.abs(G._megaIcon[0].position.z - 0.004) < 0.002;

          // · MISMO PODER ACUMULA ×2/×3, tope ×3 honesto
          G.rules.rallyHits = 22; paso();
          out.dosCargas = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 2;
          G.rules.rallyHits = 33; paso();
          out.tresCargas = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 3;
          G.rules.rallyHits = 44; paso(); paso();
          out.topeTres = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 3;
          out.msgTope = (G.rules.message || '').indexOf('TOPE ×3') === 0;

          // · PODER DISTINTO: ENTRA en la matriz (posición 1) y se SELECCIONA
          Math.random = () => 0.999;                   // SIEMPRE 'efecto'
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.matrizDos = G._megaMatriz.length === 2 &&
            G._megaMatriz[0].id === 'mega' && G._megaMatriz[0].n === 3 &&
            G._megaMatriz[1].id === 'efecto' && G._megaMatriz[1].n === 1;
          out.selNuevo = G._megaIdx === 1;             // el último cogido
          out.ordenLlegada = G._megaMatriz[0].n === 3; // los ×3 de mega INTACTOS

          // · CICLO CON FLECHAS SIN ENVOLVER: ‹ en el 1, nada › en el último
          G._megaCicla(-1);
          out.ciclaIzq = G._megaIdx === 0;             // vuelve al primero
          G._megaCicla(-1);
          out.bordeIzq = G._megaIdx === 0;             // índice 0: NO envuelve
          G._megaCicla(1); G._megaCicla(1);
          out.ciclaDerYBorde = G._megaIdx === 1;       // al último y NO pasa

          // · SÚPER EFECTO: el gatillo (seleccionado = efecto) abre SU ventana
          G.rules.state = 'serve';
          let saq = null;
          try { saq = G.megaTrigger(libre); } catch (e) { out.errSaq = String(e); }
          out.saqueRespetado = saq === false && G._efectoT === 0 &&
            G._megaMatriz[1].n === 1;
          G.rules.state = 'rally';
          let ef = null;
          try { ef = G.megaTrigger(libre); } catch (e) { out.errEf = String(e); }
          paso();                       // el bucle escribe el multiplicador en la pala
          out.efectoAbre = ef === true && G._efectoT > 7.9 &&
            G._efectoGolpes === 5 && G._megaMatriz.length === 1;
          out.fxHubicacion = Array.isArray(G._efectoFx) &&
            G._efectoFx.filter((f) => f).length === 2;
          const fxE = G._efectoFx && G._efectoFx.find((f) => f);
          out.cantoCian = !!(fxE && fxE.userData.rim && fxE.userData.rimMats &&
                             fxE.userData.rimMats[0] &&
                             fxE.userData.rimMats[0].color.getHex() === 0x54d8f0);
          out.multEnPala = G.controllerPaddles[0].ppEfectoMul === 2 &&
            G.controllerPaddles[1].ppEfectoMul === 2;
          out.msgEfecto = (G.rules.message || '').indexOf('¡SÚPER EFECTO!') === 0;

          // · RECARGA con el efecto ACTIVO (consume la 2.ª carga del efecto
          //   y al quedarse a 0 la entrada SALE de la matriz — correcto)
          Math.random = () => 0.999;
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          const habiaEfecto = !!G._megaMatriz.find((x) => x.id === 'efecto');
          G._efectoT = 3.2;                            // ventana a medio gas
          let rec = null;
          try { rec = G.megaTrigger(libre); } catch (e) { out.errRec = String(e); }
          out.recarga = rec === true && habiaEfecto && G._efectoT > 7.9 &&
            G._efectoGolpes === 5 &&
            !G._megaMatriz.find((x) => x.id === 'efecto');   // carga gastada

          // · MEGA sigue en la matriz (con sus ×3): el índice quedó CLAMPEADO
          //   a 0 al salir el efecto → el seleccionado es el mega
          Math.random = () => 0;
          out.megaSigue = !!G._megaMatriz.find((x) => x.id === 'mega') &&
            G._megaIdx === 0;
          G._efectoT = 0; paso();                      // efecto fuera: icono del seleccionado
          let mgo = null;
          try { mgo = G.megaTrigger(libre); } catch (e) { out.errMgo = String(e); }
          out.megaLibera = mgo === true && G._megaT > 14.9;
          let ext = null;
          try { ext = G.megaTrigger(libre); } catch (e) { out.errExt = String(e); }
          out.megaAlarga = ext === true && G._megaT > 29.5;

          // · EL 5.º GOLPE CIERRA la ventana del efecto (vía _efectoFin)
          G._megaT = 0; paso();
          Math.random = () => 0.999;
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          G._efectoT = 7.0; G._efectoGolpes = 1;
          try { G._efectoFin(); } catch (e) { out.errFin = String(e); }
          out.finPorGolpes = G._efectoT === 0 && G._efectoGolpes === 0 &&
            G._efectoFxOn === false;
          paso();                                      // el bucle devuelve el ×1
          out.multFuera = !G.controllerPaddles[0].ppEfectoMul ||
            G.controllerPaddles[0].ppEfectoMul === 1;
          G._efectoT = 0;

          // · MANO VACÍA: aviso honesto (y el gatillo se come la pulsación)
          G._megaT = 0; paso(); paso();
          G._megaMatriz.length = 0;
          G._megaIdx = 0;
          let vac = null;
          try { vac = G.megaTrigger(libre); } catch (e) { out.errVac = String(e); }
          out.manoVacia = vac === true &&
            (G.rules.message || '').indexOf('SIN CARGAS') === 0;

          // · CONMUTADOR APAGADO (camino REAL del menú) y ENCENDIDO
          G.rules.state = 'rally'; G.rules.rallyHits = 11; Math.random = () => 0;
          paso();
          G.menuRects.push({ id: 'pmej' });
          try { G.menuClick(G.menuRects.length - 1); } catch (e) { out.errOff = String(e); }
          out.apagadoPersiste = (() => { try {
            return localStorage.getItem('pp_pala_mejorada_v1') === '0' &&
              G.palaMejorada === false; } catch (e) { return false; } })();
          paso(); paso();
          out.apagadoLimpia = G._megaMatriz.length === 0 && G._megaIcon === null;
          G.menuRects.push({ id: 'pmej' });
          try { G.menuClick(G.menuRects.length - 1); } catch (e) { out.errOn = String(e); }
          out.encendidoPersiste = (() => { try {
            return localStorage.getItem('pp_pala_mejorada_v1') === '1' &&
              G.palaMejorada === true; } catch (e) { return false; } })();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.vuelveANacer = G._megaMatriz.length === 1;

          // · HALL = ZONA NEUTRA
          G.inHall = true;
          let enHall = null;
          try { enHall = G.megaTrigger(libre); } catch (e) { out.errHall = String(e); }
          G.inHall = false;
          out.hallNeutro = enHall === false;

          // · VOCES: el registro trae voz ES y EN para los dos poderes
          out.vozMegaEs = typeof G._poderVoz('mega_es') === 'string' &&
            G._poderVoz('mega_es').indexOf('data:audio/mpeg;base64,') === 0;
          out.vozMegaEn = typeof G._poderVoz('mega_en') === 'string' &&
            G._poderVoz('mega_en').indexOf('data:audio/mpeg;base64,') === 0 &&
            G._poderVoz('mega_en') !== G._poderVoz('mega_es');
          out.vozEfectoEs = typeof G._poderVoz('efecto_es') === 'string' &&
            G._poderVoz('efecto_es').indexOf('data:audio/mpeg;base64,') === 0;
          out.vozEfectoEn = typeof G._poderVoz('efecto_en') === 'string' &&
            G._poderVoz('efecto_en') !== G._poderVoz('efecto_es');
          out.pngMegaDueno = !!(G._megaPngs['mega'] &&
            G._megaPngs['mega'].complete && G._megaPngs['mega'].naturalWidth === 256);
          out.pngEfecto = !!(G._megaPngs['efecto'] &&
            G._megaPngs['efecto'].complete && G._megaPngs['efecto'].naturalWidth === 256);

          Math.random = rndReal;
          out.erroresPagina = 0;
          return out;
        }""")
        await browser.close()

        if rt.get('sinJuego'):
            print('✗ window.__PP_GAME no existe (el juego no arrancó)')
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            sys.exit(1)

        for k, v in sorted(rt.items()):
            if k.startswith('err'):
                print(f'  · {k}: {v}')

        esperados = [
            ('porDefecto', 'estado fresco: matriz vacía y construcción perezosa'),
            ('hayAPI', 'API del superpoder (megaTrigger/_megaCicla/_efectoTrigger/_megaVoz)'),
            ('fueraSinCarga', 'FUERA de campeonato: un rally de 44 NO carga nada'),
            ('fueraGatilloLibre', 'FUERA de campeonato: el gatillo no es del poder (false)'),
            ('diezSinCarga', 'a los 10 golpes NO hay carga (faltan 1 para las 11)'),
            ('cargada', 'al golpe 11: +1 carga de MEGA en la MATRIZ (posición 0)'),
            ('iconoVivo', 'icono vivo en las DOS monturas'),
            ('iconoAnclado', 'icono ANCLADO al mango (y=−0,034 · z=0,004)'),
            ('dosCargas', 'al golpe 22 del MISMO rally: ×2 (acumula)'),
            ('tresCargas', 'al golpe 33: ×3'),
            ('topeTres', 'al golpe 44 NO hay cuarta carga (tope ×3)'),
            ('msgTope', 'megáfono del tope: «TOPE ×3 · ¡gasta una…»'),
            ('matrizDos', 'poder distinto ENTRA en la matriz: [mega ×3, efecto ×1]'),
            ('selNuevo', 'el poder nuevo se SELECCIONA solo (índice 1)'),
            ('ordenLlegada', 'los ×3 del mega se CONSERVAN (nada se elimina)'),
            ('ciclaIzq', 'joystick ⟷ izquierda: del índice 1 al 0'),
            ('bordeIzq', 'en el índice 0 NO envuelve (sin flecha izquierda)'),
            ('ciclaDerYBorde', 'al último y NO pasa (sin flecha derecha en el final)'),
            ('saqueRespetado', 'en saque el gatillo SACA (no gasta)'),
            ('efectoAbre', 'gatillo con EFECTO seleccionado: ventana 8 s / 5 golpes'),
            ('fxHubicacion', 'FX cian construido para las DOS monturas'),
            ('cantoCian', 'el canto del efecto es CIAN (0x54d8f0), no el oro del mega'),
            ('multEnPala', 'multiplicador ×2 en las DOS palas del jugador'),
            ('msgEfecto', 'megáfono: ¡SÚPER EFECTO! · spin ×2…'),
            ('recarga', 'efecto ACTIVO + gatillo: RECARGA la ventana (8 s / 5)'),
            ('megaSigue', 'el MEGA sigue en la matriz con sus ×3'),
            ('megaLibera', 'gatillo con MEGA seleccionado: LIBERA 15 s'),
            ('megaAlarga', 'MEGA activa + gatillo: ALARGA a ~30 s'),
            ('finPorGolpes', 'el 5.º golpe con efecto CIERRA la ventana'),
            ('multFuera', 'fin del efecto: multiplicador de la pala a 1'),
            ('manoVacia', 'matriz vacía: aviso honesto «SIN CARGAS»'),
            ('apagadoPersiste', 'conmutador OFF por el menú: persiste en pp_pala_mejorada_v1'),
            ('apagadoLimpia', 'conmutador OFF: matriz vacía e icono fuera (dispose)'),
            ('encendidoPersiste', 'conmutador ON por el menú: persiste encendido'),
            ('vuelveANacer', 'conmutador ON de nuevo: la norma vuelve a operar'),
            ('hallNeutro', 'hall: zona neutra (el gatillo no libera)'),
            ('vozMegaEs', 'voz NATIVA ES del mega embebida (data-URI)'),
            ('vozMegaEn', 'voz EN del mega embebida y DISTINTA de la ES'),
            ('vozEfectoEs', 'voz NATIVA ES del efecto embebida'),
            ('vozEfectoEn', 'voz EN del efecto embebida y DISTINTA de la ES'),
            ('pngMegaDueno', 'PNG del dueño (Crece) decodificado (256px)'),
            ('pngEfecto', 'PNG del poder EFECTO decodificado (256px)'),
        ]
        for k, label in esperados:
            chk(rt.get(k) is True, label)

    if errors:
        for e in errors[:5]:
            print('  · pageerror:', e[:200])
        chk(False, 'sin errores de página durante la mecánica real')
    else:
        chk(True, 'sin errores de página durante la mecánica real')

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


asyncio.run(main())
