#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.34 · MEGA PALA NORMATIVA del núcleo (capa AC, en vivo).

Correcciones del dueño tras V3.6.33:
  · «eliminar el núcleo dorado» — FUERA núcleo/halo/aro/chispas (y todo FX
    dentro de la pala). El aviso de carga es el ICONO sobre el mango.
  · «un pequeño icono sobre el mango… un dibujo de la pala con una
    referencia a que se hace grande… acompañado de un sonido característico»
    — sprite-billboard 5,6 cm (pala dorada + 4 flechas) + jingle propio.
  · «se puede activar cuando un rally supera los 10 golpes… extensivo a
    todos los campeonatos y las plantillas» — la carga NACE en el núcleo:
    rally de 11+ golpes = carga (una por rally), regla idéntica en locura,
    magia, oeste, orbital, valle_neon y cualquier campeonato nuevo.
  · «opción "Pala Mejorada"… conmutador» — toggle en AJUSTES
    (pp_pala_mejorada_v1): apagado = pala 100 % normal.

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del núcleo (game.html) y del módulo locura
     (v26: sin mega interna) + i18n ES/EN + regresiones del FX rechazado
  2) MECÁNICA REAL en headless — el objeto del juego directamente: sin
     carga a 10 golpes, carga a 11 (icono vivo), saque respetado,
     liberación por gatillo (radio/escala/canto/onda), segundo gatillo
     comido, agotamiento con restauración, una carga por rally, re-arma en
     rally nuevo, conmutador apagado = pala normal, hall = zona neutra

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
        ('MEGA PALA NORMATIVA (núcleo)', 'sección de la norma en el núcleo'),
        ('megaTrigger(i) {', 'gatillo voluntario COMO MÉTODO DEL JUEGO'),
        ("this.rules.state !== 'rally') return false;", 'en saque el gatillo SACA'),
        ("T('arc_mega_cd')", 'aviso honesto sin carga'),
        ('_megaCharge()', 'carga normativa (rally 11+)'),
        ('(r.rallyHits || 0) > 10', 'la regla: SUPERAR los 10 golpes'),
        ('_megaRallyCharged', 'una carga por rally (cuenta nueva en el siguiente)'),
        ('_megaIconTex()', 'icono de carga dibujado en canvas'),
        ('ppMegaIcon', 'icono marcado en las monturas'),
        ('sp.position.set(0, -0.105, 0.012);', 'icono SOBRE EL MANGO (no sobre la hoja)'),
        ('pp_pala_mejorada_v1', 'conmutador persistente «Pala Mejorada»'),
        ("case 'pmej':", 'handler del conmutador en el menú'),
        ("btn('pmej', 56, y, 912, 56,", 'botón de ancho completo en AJUSTES'),
        ('_megaNormReset()', 'recogida completa con dispose'),
        ('this.updateMega(dt);', 'la norma corre en el bucle animate'),
        ('DIMS.hitAssistRadius = this._BASE_HIT * 1.38;', 'radio ×1,38 SOLO activa'),
        ('DIMS.hitAssistRadius = this._BASE_HIT;', 'restauración del radio (apagado/fin)'),
        ('side: THREE.BackSide', 'canto de energía: cascarón invertido'),
        ('multiplyScalar(1.055)', 'canto escala 1,055 (abraza la silueta)'),
        ('new THREE.TorusGeometry(0.1, 0.006, 8, 48)', 'onda de choque one-shot'),
        ('pp_mega_norm_hint', 'pista «norma nueva» UNA vez por navegador'),
        ("msg = T('arc_mega_hint')", 'la pista se muestra en la 1.ª carga'),
        ("this.rules.message = T('arc_mega_go');", 'mensaje al liberar'),
        ('arc_mega_hint:', 'i18n ES: pista de la norma'),
        ('NORMA NUEVA: un rally de 11+ golpes carga tu MEGA PALA', 'ES: texto nuevo (sin núcleo dorado)'),
        ('NEW RULE: an 11+ hit rally charges your MEGA PADDLE', 'EN: texto nuevo'),
        ('¡CRAZY COMBO! ¡MEGA PALA CARGADA!', 'ES: combo = carga'),
        ('CRAZY COMBO! MEGA PADDLE CHARGED!', 'EN: combo = carga'),
        ('¡MEGA PALA ACTIVA!', 'ES: mensaje de activación'),
        ('btn_pmej:', 'i18n: etiqueta del conmutador'),
        ('Pala Mejorada: {v}', 'ES: etiqueta del conmutador'),
        ('Enhanced Paddle: {v}', 'EN: etiqueta del conmutador'),
        ('V3.6.34-SDK6', 'sello de versión servido'),
    ]:
        chk(needle in game, label)
    # REGRESIÓN: el FX rechazado por el dueño NO vuelve
    chk('new THREE.SphereGeometry(0.011, 16, 12)' not in game,
        'regresión: el NÚCLEO dorado ya no existe en el núcleo')
    chk('new THREE.TorusGeometry(0.028, 0.0028, 8, 32)' not in game,
        'regresión: el ARO DE CARGA ya no existe')
    chk('new THREE.Points(sgeo' not in game,
        'regresión: las CHISPAS orbitales ya no existen')
    chk('MEGA_RECARGA' not in game, 'regresión: sin recarga a tiempo (la norma es el rally)')

    # módulo locura v26: la mega interna RETIRADA (vive en el núcleo)
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
    # manifest v26 (historial FASE 36) — fichero aparte del módulo
    try:
        man = urllib.request.urlopen(
            'http://localhost:3000/championships/locura/manifest.json',
            timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer el manifest de locura servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    chk('"version": 26' in man, 'locura: manifest v26')
    chk('note_v26' in man and 'FASE 36' in man,
        'locura: historial FASE 36 (mudanza de la mega al núcleo)')
    for ausente, label in [
        ('_buildMegaFx', 'locura: sin builder de FX propio'),
        ('megaTrigger(i) { return', 'locura: sin megaTrigger en el export'),
        ('MEGA_RECARGA = 14', 'locura: sin recarga a tiempo'),
        ('new THREE.SphereGeometry(0.011, 16, 12)', 'locura: sin núcleo dorado'),
        ('multiplyScalar(1.055)', 'locura: sin canto duplicado'),
    ]:
        chk(ausente not in served, 'regresión: ' + label)

    # plantilla: la norma documentada para campeonatos nuevos
    try:
        guia = urllib.request.urlopen(
            'http://localhost:3000/championships/PLANTILLA-GUIA.md',
            timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer PLANTILLA-GUIA.md servida:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    chk('2.4 MEGA PALA NORMATIVA' in guia,
        'plantilla: la norma documentada (sección 2.4)')
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
          const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
          try { window.__pp2DPlay = true; } catch (e) { /* */ }
          try { localStorage.removeItem('pp_mega_norm_hint'); } catch (e) { /* */ }
          try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) { /* */ }
          G.palaMejorada = true;

          // estado fresco: construcción perezosa (nada existe sin carga)
          out.porDefecto = G.palaMejorada === true && G._megaReady === false &&
            G._megaT === 0 && G._megaFx === null && G._megaIcon === null;
          out.hayNorma = typeof G.updateMega === 'function' &&
            typeof G.megaTrigger === 'function' &&
            typeof G.megaEnabled === 'function';

          // PARTIDO + RALLY controlado
          try { G.rules.startMatch('match'); } catch (e) { out.errMatch = String(e); }
          const paso = () => { try { G.updateMega(1 / 60); } catch (e) { out.errUpd = String(e); } };

          // · A LOS 10 GOLPES NO HAY CARGA (la regla es SUPERARlos)
          G.rules.state = 'rally'; G.rules.rallyHits = 10;
          paso(); paso();
          out.diezSinCarga = G._megaReady === false && G._megaIcon === null;

          // · AL 11: CARGA — icono vivo + pista de la norma (1.ª vez)
          G.rules.rallyHits = 11;
          paso();
          out.cargada = G._megaReady === true && G._megaRallyCharged === true;
          out.iconoVivo = Array.isArray(G._megaIcon) &&
            G._megaIcon.filter((s) => s).length === 2 &&
            G._megaIcon[0].visible === true;
          out.iconoEnMango = Math.abs(G._megaIcon[0].position.y + 0.105) < 0.02;
          out.pistaNorma = G.rules.message ===
            'NORMA NUEVA: un rally de 11+ golpes carga tu MEGA PALA (mira el icono sobre el mango) · gatillo con la bola en juego para soltarla';
          out.construccionPerezosa = G._megaFx === null;   // sin gatillo no hay FX

          // · GATILLO EN SAQUE: respeta el saque
          G.rules.state = 'serve';
          let saq = false;
          try { saq = G.megaTrigger(0) === false; } catch (e) { out.errSaq = String(e); }
          out.saqueRespetado = saq && G._megaT === 0;

          // · GATILLO EN RALLY: LIBERA (8 s de MEGA PALA)
          G.rules.state = 'rally';
          let lib = false;
          try { lib = G.megaTrigger(0) === true; } catch (e) { out.errLib = String(e); }
          out.libera = lib && G._megaT > 7.9 && G._megaReady === false;
          out.fxSoloActiva = Array.isArray(G._megaFx) &&
            G._megaFx.filter((f) => f).length === 2;
          const fxA = G._megaFx && G._megaFx.find((f) => f);
          out.cantoYonda = !!(fxA && fxA.userData.rim && fxA.userData.rimMats &&
                              fxA.userData.shock);
          out.sinNucleoEnFx = !!(fxA && fxA.userData.core === undefined &&
                                 fxA.userData.halo === undefined &&
                                 fxA.userData.ring === undefined &&
                                 fxA.userData.sparks === undefined);
          out.iconoCede = G._megaIcon[0].visible === false;
          out.ondaArriba = fxA ? fxA.userData.shockT > 0 : false;
          out.mensajeGo = G.rules.message === '¡MEGA PALA ACTIVA!';
          for (let i = 0; i < 15; i++) paso();          // ~0,25 s
          out.cantoVivo = fxA ? fxA.userData.rim.visible === true : false;
          out.escalaSube = G.paddleMounts && G.paddleMounts[0] &&
            G.paddleMounts[0].scale.x > 1.05;
          out.ondaViva = fxA ? fxA.userData.shockT > 0 : false;

          // · SEGUNDO gatillo con el efecto vivo: se come la pulsación
          let seg = null;
          try { seg = G.megaTrigger(1); } catch (e) { out.errSeg = String(e); }
          out.segundaComida = seg === true && G._megaT > 0;

          // · AGOTAMIENTO: radio y escala de vuelta
          G._megaT = 0.2;
          for (let i = 0; i < 40; i++) paso();          // ~0,66 s
          out.agotado = G._megaT <= 0 && fxA && fxA.visible === false;
          out.escalaVuelve = G.paddleMounts && G.paddleMounts[0] &&
            G.paddleMounts[0].scale.x < 1.1;

          // · UNA CARGA POR RALLY (más golpes en el MISMO rally no re-llenan)
          G.rules.rallyHits = 15;
          paso();
          out.sinDoble = G._megaReady === false;

          // · RALLY NUEVO: cuenta nueva — vuelve a cargar
          G.rules.state = 'point'; paso();
          G.rules.state = 'serve'; G.rules.rallyHits = 0; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.reArma = G._megaReady === true && G._megaIcon[0].visible === true;
          out.comboMsg = G.rules.message === '¡CRAZY COMBO! ¡MEGA PALA CARGADA!';

          // · CONMUTADOR APAGADO — camino REAL del menú (menuClick 'pmej'):
          // toggle + persistencia + recogida INMEDIATA (_megaNormReset)
          G.menuRects.push({ id: 'pmej' });
          try { G.menuClick(G.menuRects.length - 1); } catch (e) { out.errOff = String(e); }
          out.apagadoPersiste = (() => { try {
            return localStorage.getItem('pp_pala_mejorada_v1') === '0' &&
              G.palaMejorada === false; } catch (e) { return false; } })();
          paso(); paso();
          out.apagadoIconoFuera = G._megaIcon === null && G._megaIconOn === false;
          let conOff = null;
          try { conOff = G.megaTrigger(0); } catch (e) { out.errOff2 = String(e); }
          out.apagadoGatilloLibre = conOff === false;
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.apagadoSinCarga = G._megaReady === false && G._megaIcon === null;

          // · ENCENDIDO por el mismo camino real y la norma vuelve a operar
          G.menuRects.push({ id: 'pmej' });
          try { G.menuClick(G.menuRects.length - 1); } catch (e) { out.errOn = String(e); }
          out.encendidoPersiste = (() => { try {
            return localStorage.getItem('pp_pala_mejorada_v1') === '1' &&
              G.palaMejorada === true; } catch (e) { return false; } })();
          G.rules.state = 'serve'; G.rules.rallyHits = 0; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.vuelveANacer = G._megaReady === true && G._megaIcon !== null;

          // · HALL = ZONA NEUTRA (el gatillo no libera allí)
          G.inHall = true;
          let enHall = null;
          try { enHall = G.megaTrigger(0); } catch (e) { out.errHall = String(e); }
          G.inHall = false;
          out.hallNeutro = enHall === false;

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
            ('porDefecto', 'estado fresco: conmutador ON y construcción perezosa'),
            ('hayNorma', 'API de la norma en el juego (megaTrigger/updateMega/megaEnabled)'),
            ('diezSinCarga', 'a los 10 golpes NO hay carga (la regla es superarlos)'),
            ('cargada', 'al golpe 11: CARGADA'),
            ('iconoVivo', 'icono vivo en las DOS monturas'),
            ('iconoEnMango', 'icono sobre el mango (y=−0,105, no sobre la hoja)'),
            ('pistaNorma', 'la 1.ª carga muestra la pista «norma nueva»'),
            ('construccionPerezosa', 'sin gatillo no existe ni una malla de FX'),
            ('saqueRespetado', 'en saque el gatillo SACA (no libera)'),
            ('libera', 'gatillo en rally: LIBERA los 8 s'),
            ('fxSoloActiva', 'FX construido para las DOS monturas'),
            ('cantoYonda', 'FX = canto (rim) + onda de choque'),
            ('sinNucleoEnFx', 'FX SIN núcleo/halo/aro/chispas (adiós dorado)'),
            ('iconoCede', 'al activar, el icono cede el sitio'),
            ('mensajeGo', 'megáfono: ¡MEGA PALA ACTIVA!'),
            ('cantoVivo', 'canto de energía visible durante el efecto'),
            ('escalaSube', 'la pala CRECE (×1,30 en marcha)'),
            ('ondaViva', 'onda de choque en vuelo'),
            ('segundaComida', 'segundo gatillo con efecto vivo: pulsación comida'),
            ('agotado', 'agotamiento: canto fuera'),
            ('escalaVuelve', 'agotamiento: la pala vuelve a su tamaño'),
            ('sinDoble', 'una CARGA por rally (15 golpes no re-llenan)'),
            ('reArma', 'rally nuevo: cuenta nueva y vuelve a cargar'),
            ('comboMsg', 'megáfono: ¡CRAZY COMBO! ¡MEGA PALA CARGADA!'),
            ('apagadoPersiste', 'conmutador OFF por el menú: persiste en pp_pala_mejorada_v1'),
            ('apagadoIconoFuera', 'conmutador OFF: recogida INMEDIATA (icono disposed)'),
            ('apagadoGatilloLibre', 'conmutador OFF: el gatillo NO es del poder'),
            ('apagadoSinCarga', 'conmutador OFF: un rally de 11+ NO carga'),
            ('encendidoPersiste', 'conmutador ON por el menú: persiste encendido'),
            ('vuelveANacer', 'conmutador ON de nuevo: la norma vuelve a operar'),
            ('hallNeutro', 'hall: zona neutra (el gatillo no libera)'),
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
