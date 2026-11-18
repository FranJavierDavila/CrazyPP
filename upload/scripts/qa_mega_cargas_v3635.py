#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.35 · SUPERPODER DE PALA · CARGAS ×3 (capa AD, en vivo).

El diseño aprobado por el dueño sobre la norma v3.6.34:
  · «los superpoderes de pala se obtienen cada 11 golpes por norma… si
    jugando te vuelve a salir el mismo superpoder te ponga al lado del
    icono un +2… si lo usas descuentas 1» — CADA 11 golpes del rally =
    +1 carga (11, 22, 33…), tope ×3, misma-espacie acumula / distinta
    sustituye, cargas vivas SOLO en la partida en curso.
  · «cuando se consigue un superpoder… una voz muy animosa lo comunique»
    — voz TTS EMBEBIDA (data-URI) «¡Potenciador de pala gigante!».
  · icono DEL DUEÑO (SuperPala_Crece.png embebido) «anclado al mango…
    ligeramente por encima del mando… así forma parte de la pala» +
    etiqueta ×N.
  · «desplegar con el gatillo del mando contraria al mando que tiene la
    pala (conmuta si cambiamos la pala de mano)» — gatillo del mando
    LIBRE suelta el poder (respaldo en la pala si el campeonato ocupa la
    mano libre); ACTIVA + cargas = alarga +15 s (el tamaño nunca apila).

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del núcleo (registro, constantes, assets
     embebidos, regla de 11, ×N, voz) + i18n ES/EN + regresiones de la
     norma v3.6.34 sustituida + plantilla + locura v26 intacta
  2) MECÁNICA REAL en headless — 10 sin carga · 11 carga (×1) · 22 (×2)
     · 33 (×3) · 44 tope (msg «TOPE ×3») · gatillo libre libera 15 s ·
     gatillo con ACTIVA alarga · agotamiento restaura · icono vuelve con
     ×1 · saque respetado · rally nuevo resetea la cuenta · conmutador
     por el menú con persistencia · PNG del dueño decodificado

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
        ('SUPERPODER DE PALA · CARGAS ×3', 'bloque del superpoder en el núcleo'),
        ('const PODERES_PALA', 'REGISTRO EXTENSIBLE de poderes'),
        ("{ id: 'mega', nombre: () => T('poder_mega'), voz: VOZ_PODER_MEGA }",
         'entrada MEGA PALA del registro (id + nombre + voz)'),
        ('const MEGA_DUR = 15;', '15 s de efecto por carga'),
        ('const MEGA_TOPE = 3;', 'tope ×3 de cargas'),
        ('const MEGA_GOLPES = 11;', 'cada 11 golpes = +1 carga'),
        ('const MEGA_ICON_Y = -0.034;', 'icono ANCLADO al mango (base de la mano)'),
        ('data:image/png;base64,', 'PNG DEL DUEÑO embebido (data-URI)'),
        ('data:audio/mpeg;base64,', 'VOZ TTS embebida (data-URI)'),
        ("im.src = PNG_PODER_MEGA;", 'carga async del PNG del dueño'),
        ("c2.drawImage(this._megaPng, 0, 0, 256, 256);", 'la textura usa el PNG del dueño'),
        ("c2.fillText('×' + n, 203, 205);", 'etiqueta ×N de cargas acumuladas'),
        ('_megaIconRefresh()', 'redibujo del icono al cambiar cargas'),
        ('_megaVoz()', 'voz animosa en la carga'),
        ("const concede = Math.floor((r.rallyHits || 0) / MEGA_GOLPES);",
         'LA REGLA: cada 11 golpes del rally actual'),
        ('this._megaRallyGrants = concede;', 'cuenta de concesiones del rally'),
        ('this._megaRallyGrants = 0;', 'rally nuevo = cuenta nueva'),
        ('this._megaLoads >= MEGA_TOPE', 'tope ×3 con feedback honesto'),
        ('this._megaPoder = id;', 'poder distinto SUSTITUYE'),
        ('this._megaLoads++;', 'mismo poder ACUMULA'),
        ("msg += ' ×' + this._megaLoads;", 'megáfono con ×N'),
        ("const libre = (i !== this.paddleHand) || !this.renderer.xr.isPresenting;",
         'GATILLO DEL MANDO LIBRE (conmuta al cambiar de mano)'),
        ('const gunVive = !!(this.champs && this.champs.gunArmed);',
         'la pistola del Oeste conserva la mano libre'),
        ('this._megaT += MEGA_DUR;', 'ACTIVA + cargas = ALARGA (+15 s)'),
        ('sp.position.set(0, MEGA_ICON_Y, MEGA_ICON_Z);',
         'icono en la posición anclada (constantes)'),
        ('pp_pala_mejorada_v1', 'conmutador persistente «Pala Mejorada»'),
        ("case 'pmej':", 'handler del conmutador en el menú'),
        ('_megaNormReset()', 'recogida completa con dispose'),
        ('this.updateMega(dt);', 'la norma corre en el bucle animate'),
        ('DIMS.hitAssistRadius = this._BASE_HIT * 1.38;', 'radio ×1,38 SOLO activa'),
        ('pp_mega_norm_hint', 'pista «norma nueva» UNA vez por navegador'),
        ('arc_mega_full:', 'i18n ES: mensaje de tope ×3'),
        ('TOPE ×3 · ¡gasta una con el gatillo libre!', 'ES: texto del tope'),
        ('poder_mega:', 'i18n: nombre del poder'),
        ('¡POTENCIADOR DE PALA GIGANTE!', 'ES: «voz» en el megáfono'),
        ('GIANT PADDLE BOOSTER!', 'EN: nombre del poder'),
        ('MAX ×3 · spend one with the free-hand trigger!', 'EN: texto del tope'),
        ('SUPERPODER DE PALA: cada 11 golpes del rally = +1 carga',
         'ES: pista de la norma ×3'),
        ('PADDLE SUPERPOWER: every 11 rally hits = +1 charge',
         'EN: pista de la norma ×3'),
        ('V3.6.35-SDK6', 'sello de versión servido'),
    ]:
        chk(needle in game, label)
    # REGRESIÓN: la norma v3.6.34 sustituida NO vuelve (y el FX rechazado tampoco)
    chk('_megaReady' not in game, 'regresión: el estado booleano v3.6.34 ya no existe')
    chk('_megaRallyCharged' not in game, 'regresión: «una carga por rally» ya no existe')
    chk('(r.rallyHits || 0) > 10' not in game, 'regresión: la regla «> 10» fue sustituida')
    chk('sp.position.set(0, -0.105, 0.012);' not in game,
        'regresión: la posición flotante vieja del icono ya no existe')
    chk('new THREE.SphereGeometry(0.011, 16, 12)' not in game,
        'regresión: el NÚCLEO dorado sigue fuera')
    chk('MEGA_RECARGA' not in game, 'regresión: sin recarga a tiempo')

    # módulo locura v26 intacto (la mega vive en el núcleo)
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
        ('_buildMegaFx', 'locura: sin builder de FX propio'),
        ('megaTrigger(i) { return', 'locura: sin megaTrigger en el export'),
        ('_megaLoads', 'locura: sin estado de cargas (es del núcleo)'),
    ]:
        chk(ausente not in served, 'regresión: ' + label)

    # plantilla: la norma ×3 documentada para campeonatos nuevos
    try:
        guia = urllib.request.urlopen(
            'http://localhost:3000/championships/PLANTILLA-GUIA.md',
            timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer PLANTILLA-GUIA.md servida:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    chk('2.4 SUPERPODER DE PALA · CARGAS ×3' in guia,
        'plantilla: la norma ×3 documentada (sección 2.4)')
    chk('cada 11 golpes del rally** (11, 22, 33…) = **+1 carga**' in guia,
        'plantilla: regla de las cargas documentada')
    chk('gatillo del mando LIBRE**' in guia,
        'plantilla: gatillo del mando libre documentado')
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

          // estado fresco: construcción perezosa (nada existe sin carga)
          out.porDefecto = G.palaMejorada === true && G._megaLoads === 0 &&
            G._megaPoder === null && G._megaRallyGrants === 0 &&
            G._megaT === 0 && G._megaFx === null && G._megaIcon === null;
          out.hayNorma = typeof G.updateMega === 'function' &&
            typeof G.megaTrigger === 'function' &&
            typeof G.megaEnabled === 'function' &&
            typeof G._megaVoz === 'function' &&
            typeof G._megaIconRefresh === 'function';

          // PARTIDO + RALLY controlado
          try { G.rules.startMatch('match'); } catch (e) { out.errMatch = String(e); }
          const paso = () => { try { G.updateMega(1 / 60); } catch (e) { out.errUpd = String(e); } };

          // · A LOS 10 GOLPES NO HAY CARGA (falta 1 para las 11)
          G.rules.state = 'rally'; G.rules.rallyHits = 10;
          paso(); paso();
          out.diezSinCarga = G._megaLoads === 0 && G._megaIcon === null;

          // · AL 11: +1 CARGA — icono vivo (PNG del dueño) + pista (1.ª vez)
          G.rules.rallyHits = 11;
          paso();
          out.cargada = G._megaLoads === 1 && G._megaPoder === 'mega' &&
            G._megaRallyGrants === 1;
          out.iconoVivo = Array.isArray(G._megaIcon) &&
            G._megaIcon.filter((s) => s).length === 2 &&
            G._megaIcon[0].visible === true;
          out.iconoAnclado = Math.abs(G._megaIcon[0].position.y + 0.034) < 0.006 &&
            Math.abs(G._megaIcon[0].position.z - 0.004) < 0.002;   // ±vaivén 0,003
          out.pngDelDueno = !!(G._megaPng && G._megaPng.complete &&
                               G._megaPng.naturalWidth === 256);
          out.pistaNorma = (G.rules.message || '').indexOf(
            'SUPERPODER DE PALA: cada 11 golpes del rally = +1 carga') === 0;
          out.construccionPerezosa = G._megaFx === null;   // sin gatillo no hay FX

          // · CADA 11 GOLPES DEL MISMO RALLY: 22 → ×2 · 33 → ×3
          G.rules.rallyHits = 22; paso();
          out.dosCargas = G._megaLoads === 2 && G._megaRallyGrants === 2;
          out.etiquetaDos = G.rules.message === '¡POTENCIADOR DE PALA GIGANTE! ×2';
          G.rules.rallyHits = 33; paso();
          out.tresCargas = G._megaLoads === 3 && G._megaRallyGrants === 3;

          // · TOPE ×3: a 44 golpes NO hay cuarta carga (msg de tope + «toc»)
          G.rules.rallyHits = 44; paso(); paso();
          out.topeTres = G._megaLoads === 3;
          out.msgTope = G.rules.message === 'TOPE ×3 · ¡gasta una con el gatillo libre!';

          // · GATILLO EN SAQUE: respeta el saque (aunque haya cargas)
          G.rules.state = 'serve';
          let saq = null;
          try { saq = G.megaTrigger(libre); } catch (e) { out.errSaq = String(e); }
          out.saqueRespetado = saq === false && G._megaT === 0 &&
            G._megaLoads === 3;

          // · GATILLO DEL MANDO LIBRE EN RALLY: LIBERA (15 s), quedan ×2
          G.rules.state = 'rally';
          let lib = null;
          try { lib = G.megaTrigger(libre); } catch (e) { out.errLib = String(e); }
          out.libera = lib === true && G._megaT > 14.9 && G._megaLoads === 2;
          out.fxSoloActiva = Array.isArray(G._megaFx) &&
            G._megaFx.filter((f) => f).length === 2;
          const fxA = G._megaFx && G._megaFx.find((f) => f);
          out.cantoYonda = !!(fxA && fxA.userData.rim && fxA.userData.rimMats &&
                              fxA.userData.shock);
          out.sinNucleoEnFx = !!(fxA && fxA.userData.core === undefined &&
                                 fxA.userData.halo === undefined &&
                                 fxA.userData.ring === undefined &&
                                 fxA.userData.sparks === undefined);
          out.mensajeGo = G.rules.message === '¡MEGA PALA ACTIVA!';

          // · ACTIVA + gatillo con cargas: ALARGA +15 s (no apila tamaño)
          let ext = null;
          try { ext = G.megaTrigger(libre); } catch (e) { out.errExt = String(e); }
          out.alarga = ext === true && G._megaLoads === 1 && G._megaT > 29.5;

          // · AGOTAMIENTO: radio y escala de vuelta, icono vuelve con ×1
          G._megaT = 0.2;
          for (let i = 0; i < 40; i++) paso();          // ~0,66 s
          out.agotado = G._megaT <= 0 && fxA && fxA.visible === false;
          out.escalaVuelve = G.paddleMounts && G.paddleMounts[0] &&
            G.paddleMounts[0].scale.x < 1.1;
          out.iconoVuelve = G._megaIcon[0].visible === true &&
            G._megaLoads === 1;

          // · ÚLTIMA CARGA: la mano queda VACÍA y el icono se va
          let fin = null;
          try { fin = G.megaTrigger(libre); } catch (e) { out.errFin = String(e); }
          out.manoVacia = fin === true && G._megaLoads === 0 &&
            G._megaT > 14.9 && G._megaIcon[0].visible === false;

          // · RALLY NUEVO: cuenta nueva — vuelve a cargar (×1). El icono
          // sigue OCULTO mientras el efecto de la mano vacía siga ACTIVO;
          // al agotarse (timer a 0) vuelve a verse con la carga nueva.
          G.rules.state = 'point'; paso();
          G.rules.state = 'serve'; G.rules.rallyHits = 0; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.reArma = G._megaLoads === 1 && G._megaRallyGrants === 1;
          G._megaT = 0; paso(); paso();
          out.reArmaVisible = !!(G._megaIcon && G._megaIcon[0] &&
            G._megaIcon[0].visible === true);
          out.comboMsg = G.rules.message === '¡POTENCIADOR DE PALA GIGANTE!';

          // · CONMUTADOR APAGADO — camino REAL del menú (menuClick 'pmej'):
          // toggle + persistencia + recogida INMEDIATA (_megaNormReset)
          G.menuRects.push({ id: 'pmej' });
          try { G.menuClick(G.menuRects.length - 1); } catch (e) { out.errOff = String(e); }
          out.apagadoPersiste = (() => { try {
            return localStorage.getItem('pp_pala_mejorada_v1') === '0' &&
              G.palaMejorada === false; } catch (e) { return false; } })();
          paso(); paso();
          out.apagadoIconoFuera = G._megaIcon === null && G._megaIconOn === false;
          out.apagadoManoVacia = G._megaLoads === 0 && G._megaPoder === null;
          let conOff = null;
          try { conOff = G.megaTrigger(libre); } catch (e) { out.errOff2 = String(e); }
          out.apagadoGatilloLibre = conOff === false;
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.apagadoSinCarga = G._megaLoads === 0 && G._megaIcon === null;

          // · ENCENDIDO por el mismo camino real y la norma vuelve a operar
          G.menuRects.push({ id: 'pmej' });
          try { G.menuClick(G.menuRects.length - 1); } catch (e) { out.errOn = String(e); }
          out.encendidoPersiste = (() => { try {
            return localStorage.getItem('pp_pala_mejorada_v1') === '1' &&
              G.palaMejorada === true; } catch (e) { return false; } })();
          G.rules.state = 'serve'; G.rules.rallyHits = 0; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.vuelveANacer = G._megaLoads === 1 && G._megaIcon !== null;

          // · HALL = ZONA NEUTRA (el gatillo no libera allí)
          G.inHall = true;
          let enHall = null;
          try { enHall = G.megaTrigger(libre); } catch (e) { out.errHall = String(e); }
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
            ('porDefecto', 'estado fresco: mano vacía y construcción perezosa'),
            ('hayNorma', 'API del superpoder (megaTrigger/updateMega/_megaVoz/_megaIconRefresh)'),
            ('diezSinCarga', 'a los 10 golpes NO hay carga (faltan 1 para las 11)'),
            ('cargada', 'al golpe 11: +1 CARGA (×1, poder mega, cuenta 1)'),
            ('iconoVivo', 'icono vivo en las DOS monturas'),
            ('iconoAnclado', 'icono ANCLADO al mango (y=−0,034 · z=0,004)'),
            ('pngDelDueno', 'el PNG DEL DUEÑO está decodificado (256px)'),
            ('pistaNorma', 'la 1.ª carga muestra la pista «cada 11 golpes»'),
            ('construccionPerezosa', 'sin gatillo no existe ni una malla de FX'),
            ('dosCargas', 'al golpe 22 del MISMO rally: ×2'),
            ('etiquetaDos', 'megáfono: ¡POTENCIADOR DE PALA GIGANTE! ×2'),
            ('tresCargas', 'al golpe 33: ×3'),
            ('topeTres', 'al golpe 44 NO hay cuarta carga (tope ×3)'),
            ('msgTope', 'megáfono del tope: «TOPE ×3 · ¡gasta una…»'),
            ('saqueRespetado', 'en saque el gatillo SACA (no gasta)'),
            ('libera', 'gatillo del mando LIBRE: LIBERA 15 s (quedan ×2)'),
            ('fxSoloActiva', 'FX construido para las DOS monturas'),
            ('cantoYonda', 'FX = canto (rim) + onda de choque'),
            ('sinNucleoEnFx', 'FX SIN núcleo/halo/aro/chispas (adiós dorado)'),
            ('mensajeGo', 'megáfono: ¡MEGA PALA ACTIVA!'),
            ('alarga', 'ACTIVA + gatillo con cargas: ALARGA a ~30 s (no apila tamaño)'),
            ('agotado', 'agotamiento: canto fuera'),
            ('escalaVuelve', 'agotamiento: la pala vuelve a su tamaño'),
            ('iconoVuelve', 'el icono VUELVE con las cargas restantes (×1)'),
            ('manoVacia', 'última carga: mano vacía y icono fuera'),
            ('reArma', 'rally nuevo: cuenta nueva y vuelve a cargar (×1)'),
            ('reArmaVisible', 'el icono vuelve a verse al agotarse el efecto (×1)'),
            ('comboMsg', 'megáfono: ¡POTENCIADOR DE PALA GIGANTE!'),
            ('apagadoPersiste', 'conmutador OFF por el menú: persiste en pp_pala_mejorada_v1'),
            ('apagadoIconoFuera', 'conmutador OFF: recogida INMEDIATA (icono disposed)'),
            ('apagadoManoVacia', 'conmutador OFF: la mano se vacía (cargas a 0)'),
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
