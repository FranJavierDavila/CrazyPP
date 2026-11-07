#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.33 · MEGA PALA 2.0 «NÚCLEO DE ENERGÍA» (capa AB, en vivo).

Informe del dueño tras V3.6.32:
  «El efecto de energía… está muy desajustado al tamaño de la pala y el
   aura dorada… se mete dentro de la propia pala quedando muy cutre. El
   jugador mientras juega no se entera de que tiene la Mega Pala y su uso
   debería ser voluntario, por ejemplo apretando el gatillo del mando.»

Rediseño completo que esta capa verifica:
  · FUERA el billboard de 34 cm (cero aura atravesando la hoja)
  · CANTO DE ENERGÍA: clon exacto de la pala montada, BackSide aditivo,
    escala 1,055 (borde que abraza la silueta desde FUERA)
  · NÚCLEO en la garganta TODO el partido + aro de carga + chispas
  · USO VOLUNTARIO: gatillo con la bola en juego libera la carga
    (c12 onSelectStart → ChampLoader.megaTrigger → módulo.megaTrigger);
    en 'serve' el gatillo sigue siendo del SAQUE
  · Cada partido arranca CARGADO (_megaMatch arma); recarga 14 s tras el
    efecto y CRAZY COMBO = recarga instantánea (o +8 s si ya está activa)
  · Aviso honesto sin carga; chime + destello al volver a estar lista
  · leave() recoge todo con dispose (el canto no toca geometrías GLB)

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del módulo locura + game.html servidos por
     el dev server (métodos nuevos, puente del núcleo, sin aura vieja)
  2) MECÁNICA REAL en headless — launch('locura'), poder forzado,
     megaTrigger con estado rally: liberación, consumo de carga,
     recarga, combo instantáneo, aviso sin carga, hostilidad en 'serve'
     y recogida completa en leaveAll

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
        served = urllib.request.urlopen(MOD, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer el módulo servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ('MEGA_RECARGA = 14', 'recarga automática de 14 s (constante)'),
        ('MEGA_ESCALA = 1.3', 'pala ×1,30 (constante del rediseño)'),
        ('MEGA_SHOCK_T = 0.55', 'onda de choque de 0,55 s'),
        ('megaTrigger(i) {', 'gatillo voluntario en el controller'),
        ("T('arc_mega_go')", 'mensaje «¡MEGA PALA!» al liberar'),
        ("T('arc_mega_cd')", 'aviso honesto «recargando»'),
        ("this._megaCd = MEGA_RECARGA;", 'liberar gasta la carga y arma recarga'),
        ("if (this._megaT <= 0) { this._megaReady = true; this._megaCd = 0; }",
         'partido arranca CARGADO (armado)'),
        ("r.message = T('arc_mega_hint');", 'pista única al primer partido'),
        ("localStorage.getItem('pp_arcade_mega_hint')", 'la pista es UNA vez (persistente)'),
        ('side: THREE.BackSide', 'canto: cascarón invertido (nunca dentro de la hoja)'),
        ('multiplyScalar(1.055)', 'canto escala 1,055 (ajustado a la silueta)'),
        ('m.children[0] ? m.children[0].clone(true) : null',
         'canto = clon EXACTO de la pala montada'),
        ('new THREE.SphereGeometry(0.011, 16, 12)', 'núcleo en la garganta'),
        ('halo.scale.setScalar(0.055)', 'halo PEQUEÑO (5,5 cm) del núcleo'),
        ('new THREE.TorusGeometry(0.028, 0.0028, 8, 32)', 'aro de carga'),
        ('new THREE.Points(sgeo, new THREE.PointsMaterial({', 'chispas orbitales'),
        ('new THREE.TorusGeometry(0.1, 0.006, 8, 48)', 'onda de choque al liberar'),
        ('U.sparks.geometry.attributes.position.needsUpdate = true',
         'chispas vivas (buffer animado)'),
        ('this._megaShock();', 'onda disparada al liberar/combo'),
        ('fx.userData.shockT = MEGA_SHOCK_T;', 'la onda es one-shot con reloj'),
        ('U.rim.visible = !!U.rimMats.length && megaAct;',
         'canto SOLO con el poder activo'),
        ('_megaFxDispose()', 'recogida con dispose (regla Quest)'),
        ('if (U.rimMats) for (const rm of U.rimMats) rm.dispose();',
         'dispose de materiales del canto (geometrías GLB intactas)'),
        ('if (this._megaHaloTex) { this._megaHaloTex.dispose()',
         'dispose de texturas compartidas'),
        ('this._megaReady = false;\n    this._megaCd = 0;',
         'leave() apaga carga y recarga'),
        ('megaTrigger(i) { return !!(CTRL && CTRL.megaTrigger && CTRL.megaTrigger(i)); },',
         'puente del export del módulo'),
        ("g.rules.state !== 'rally') return false;  // en saque, el gatillo SACA",
         'en saque el gatillo NO libera (sigue sacando)'),
        ("playOsc(520, 1040, 0.12, 'sine', 0.10, 0)",
         'chime «lista de nuevo» al completar recarga'),
        ("playOsc(220, 150, 0.12, 'sine', 0.08, 0)",
         'blip grave al apretar sin carga'),
    ]:
        chk(needle in served, label)
    # el aura vieja que se metía en la pala debe estar FUERA del módulo
    chk('aura.scale.setScalar(0.34)' not in served,
        'regresión: el billboard de 34 cm YA NO existe')
    chk('TorusGeometry(0.104' not in served and 'TorusGeometry(0.128' not in served,
        'regresión: los anillos sueltos de V3.6.32 fuera')
    chk('_megaAuraTex' not in served, 'regresión: textura del aura vieja fuera')
    chk("T('arc_combo')" in served and 'arc_mega' in served,
        'CRAZY COMBO sigue vivo (recarga) junto al nuevo vocabulario')

    # game.html servido: gancho del núcleo + puente ChampLoader + i18n
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ("if (this.rules.state === 'rally' && this.champs &&\n        typeof this.champs.megaTrigger === 'function') {",
         'núcleo: gatillo en RALLY llega al campeonato'),
        ('consumed = this.champs.megaTrigger(i) === true;',
         'núcleo: pulsación consumida corta la cadena'),
        ('megaTrigger(i) {\n    const m = this.mod;',
         'ChampLoader: puente megaTrigger al módulo activo'),
        ('arc_mega_go:', 'i18n ES: mensaje de liberación'),
        ('arc_mega_ready:', 'i18n ES: «lista · gatillo la libera»'),
        ('arc_mega_cd:', 'i18n ES: «recargando…»'),
        ('arc_mega_hint:', 'i18n ES: pista única'),
        ('MEGA PADDLE! Let it rip!', 'i18n EN: mensaje de liberación'),
        ('V3.6.33-SDK6', 'sello de versión servido'),
    ]:
        chk(needle in game, label)

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
          const C = G.champs;
          if (!C) { out.sinChamps = true; return out; }
          const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
          // el bucle del juego debe estar VIVO en 2D para que update() corra
          try { window.__pp2DPlay = true; } catch (e) { /* */ }
          // ---- catálogo cargado (sondeo hasta 60 s, patrón capa Z) ----
          let catalogo = false;
          try {
            for (let i = 0; i < 120 && !catalogo; i++) {
              await dorme(500);
              catalogo = C.list().length >= 5;
            }
          } catch (e) { catalogo = false; }
          out.catalogo = catalogo;
          if (!catalogo) return out;

          // ---- entrada REAL al campeonato (launch es async) ----
          try { await C.launch('locura'); } catch (e) { out.errLaunch = String(e); }
          const w = C.mod;
          const bk = window.__PP_LOCURA;
          let impl = null;
          for (let i = 0; i < 48 && !impl; i++) {
            impl = (bk && typeof bk.ctrl === 'function' && bk.ctrl()) ||
                   (w && w.impl) || null;
            if (!impl) await dorme(250);
          }
          out.tieneWrapper = !!w;
          if (impl && !impl.active && w && typeof w.start === 'function') {
            try { w.start(); } catch (eS) { out.errStart2 = String(eS); }
            await dorme(400);
          }
          // asiento del arranque async (rival/cartel/mapa): el update del
          // módulo toca esos subsystems y su init a veces no ha asentado
          await dorme(800);
          out.tieneImpl = !!impl && typeof impl.megaTrigger === 'function';
          if (!out.tieneImpl) return out;
          out.activo = impl.active === true;
          out.puenteChamps = typeof C.megaTrigger === 'function';

          // estado fresco del rediseño
          out.fresco = impl._megaT === 0 && impl._megaFx === null &&
                       impl._megaFxOn === false && impl._megaMatch === false;

          // ---- PARTIDO VIVO: forzado determinista (sin jugar rondas) ----
          if (!impl.powers.includes('mega_pala')) impl.powers.push('mega_pala');
          try { G.rules.startMatch('match'); } catch (e) { out.errMatch = String(e); }
          G.rules.state = 'serve';
          // ARMADO: el update detecta el partido vivo y arma la carga
          // (reintentos: el primer update puede rozar la init async)
          out.armado = false;
          out.errArm = null;
          for (let i = 0; i < 6 && !out.armado; i++) {
            try {
              G.rules.state = 'serve';
              impl.update(1 / 60);
            } catch (e) { out.errArm = String(e); }
            out.armado = impl._megaMatch === true && impl._megaReady === true;
            if (!out.armado) await dorme(300);
          }
          out.fxConstruido = Array.isArray(impl._megaFx) &&
            impl._megaFx.filter((fx) => fx).length === 2;
          out.fxVisible = impl._megaFxOn === true;
          const fxA = impl._megaFx && impl._megaFx.find((fx) => fx);
          out.piezas = fxA ? Object.keys(fxA.userData).length : 0;
          out.tieneCanto = !!(fxA && fxA.userData.rim && fxA.userData.rimMats);
          out.tieneNucleo = !!(fxA && fxA.userData.core && fxA.userData.halo &&
                               fxA.userData.ring);
          out.tieneChispas = !!(fxA && fxA.userData.sparks &&
                                fxA.userData.spkN === 26);
          out.tieneOnda = !!(fxA && fxA.userData.shock);
          // carga armada => canto oculto (sólo con el poder ACTIVO)
          out.cantoEnReposo = fxA ? fxA.userData.rim.visible === false : false;

          // ---- GATILLO EN SAQUE: NO libera (el saque es del saque) ----
          try { out.saqueLibre = impl.megaTrigger(0); } catch (e) { out.errSaq = String(e); }
          out.saqueRespetado = out.saqueLibre === false && impl._megaT === 0;

          // ---- GATILLO EN RALLY: LIBERA la carga ----
          G.rules.state = 'rally';
          try { out.libera = impl.megaTrigger(0); } catch (e) { out.errLib = String(e); }
          out.libro = out.libera === true;
          out.efectoActivo = impl._megaT > 7 && impl._megaWarn === false;
          out.cargaConsumida = impl._megaReady === false &&
            Math.abs(impl._megaCd - 14) < 0.01;
          out.ondaArriba = fxA ? fxA.userData.shockT > 0 : false;
          // 15 updates deterministas (~0,25 s): canto vivo, pala creciendo,
          // onda en vuelo y chispas moviéndose (la onda vive 0,55 s)
          try {
            for (let i = 0; i < 15; i++) impl.update(1 / 60);
          } catch (e) { out.errUpd = String(e); }
          out.cantoVivo = fxA ? fxA.userData.rim.visible === true : false;
          out.escalaSube = (G.paddleMounts && G.paddleMounts[0]) ?
            G.paddleMounts[0].scale.x > 1.05 : false;
          out.ondaViva = fxA ? fxA.userData.shockT > 0 : false;
          out.chispasAnimadas = fxA ?
            fxA.userData.sparks.geometry.attributes.position.array[0] !== 0.112 : false;

          // ---- SEGUNDO gatillo con el efecto vivo: se come la pulsación ----
          try {
            for (let i = 0; i < 30; i++) impl.update(1 / 60);   // total 0,75 s
          } catch (e) { out.errUpdB = String(e); }
          try { out.segunda = impl.megaTrigger(0); } catch (e) { out.errSeg = String(e); }
          out.segundaComida = out.segunda === true;

          // ---- AGOTAMIENTO: vuelve la escala y arranca la recarga ----
          try { impl._megaT = 0.2; } catch (e) { /* */ }
          try {
            for (let i = 0; i < 40; i++) impl.update(1 / 60);
          } catch (e) { out.errAgo = String(e); }
          out.escalaVuelve = (G.paddleMounts && G.paddleMounts[0]) ?
            G.paddleMounts[0].scale.x <= 1.05 : false;
          out.recargando = impl._megaReady === false && impl._megaCd > 12;

          // ---- GATILLO SIN CARGA: aviso honesto, sin efecto ----
          try { out.sinCarga = impl.megaTrigger(0); } catch (e) { out.errSC = String(e); }
          out.sinCargaOk = out.sinCarga === true && impl._megaT <= 0;

          // ---- RECARGA: el goteo la devuelve (avance determinista) ----
          try { impl._megaCd = 0.3; } catch (e) { /* */ }
          try {
            for (let i = 0; i < 30; i++) impl.update(1 / 60);
          } catch (e) { out.errRec = String(e); }
          out.recargada = impl._megaReady === true && impl._megaCd === 0 &&
            impl._megaFlash > 0;

          // ---- CRAZY COMBO: recarga INSTANTÁNEA (onPoint) ----
          try {
            impl._megaReady = false;
            impl._megaCd = 9;
            impl.onPoint({ winner: 'player', rallyHits: 6, survival: false });
          } catch (e) { out.errCombo = String(e); }
          out.comboRecarga = impl._megaReady === true && impl._megaCd === 0;
          // combo DURANTE el efecto: repone los 8 s
          try {
            impl._megaT = 1.5;
            impl.onPoint({ winner: 'player', rallyHits: 7, survival: false });
          } catch (e) { out.errCombo2 = String(e); }
          out.comboRepone = impl._megaT > 7.5;
          try { impl._megaT = 0; impl.update(1 / 60); } catch (e) { /* */ }

          // ---- SIN PODER: el gatillo NO es suyo (no consume nada) ----
          try {
            const idx = impl.powers.indexOf('mega_pala');
            impl.powers.splice(idx, 1);
            impl._megaReady = true;
            out.ajeno = impl.megaTrigger(0);
            out.ajenoOk = out.ajeno === false && impl._megaReady === true;
            impl.powers.push('mega_pala');
          } catch (e) { out.errAjeno = String(e); }

          // ---- LEAVE: recogida COMPLETA ----
          try { C.leaveAll(); } catch (e) { out.errLeave = String(e); }
          await dorme(400);
          if (G.paddleMounts && G.paddleMounts[0]) {
            out.escalaLeave = G.paddleMounts[0].scale.x;
            out.leaveLimpio = out.escalaLeave === 1;
          }
          out.fxNull = impl._megaFx === null;
          out.estadoLeave = impl._megaReady === false && impl._megaCd === 0 &&
            impl._megaMatch === false && impl._megaFxOn === false;
          out.puenteApagado = C.megaTrigger ? C.megaTrigger(0) === false : true;
          return out;
        }""")

        checks = [
            ('headless: juego y ChampLoader vivos', not (rt.get('sinJuego') or rt.get('sinChamps'))),
            ('headless: catálogo de campeonatos cargado (≤60 s)', rt.get('catalogo') is True),
            ('headless: launch(locura) sin error', not rt.get('errLaunch')),
            ('headless: startMatch sin error', not rt.get('errMatch')),
            ('headless: update de armado sin error', not rt.get('errArm')),
            ('headless: wrapper del módulo registrado', rt.get('tieneWrapper') is True),
            ('headless: impl de La Locura con megaTrigger()', rt.get('tieneImpl') is True),
            ('headless: impl activo (update vivo)', rt.get('activo') is True),
            ('headless: puente ChampLoader.megaTrigger presente', rt.get('puenteChamps') is True),
            ('headless: estado fresco del rediseño (fx null / sin match)', rt.get('fresco') is True),
            ('headless: partido vivo ARMA la carga (serve/rally)', rt.get('armado') is True),
            ('headless: energía construida en las DOS monturas', rt.get('fxConstruido') is True),
            ('headless: energía VISIBLE con el partido vivo', rt.get('fxVisible') is True),
            ('headless: userData completo (12 piezas)', rt.get('piezas') == 12),
            ('headless: canto + rimMats presentes', rt.get('tieneCanto') is True),
            ('headless: núcleo + halo + aro de carga presentes', rt.get('tieneNucleo') is True),
            ('headless: 26 chispas orbitales presentes', rt.get('tieneChispas') is True),
            ('headless: onda de choque presente', rt.get('tieneOnda') is True),
            ('headless: canto OCULTO con la pala cargada (sólo activo)', rt.get('cantoEnReposo') is True),
            ('headless: gatillo en SAQUE no libera', rt.get('saqueRespetado') is True),
            ('headless: gatillo en RALLY libera (consumida)', rt.get('libro') is True),
            ('headless: efecto activo 8 s sin aviso prematuro', rt.get('efectoActivo') is True),
            ('headless: carga consumida + recarga a 14 s', rt.get('cargaConsumida') is True),
            ('headless: onda de choque disparada al liberar', rt.get('ondaArriba') is True),
            ('headless: canto VIVO con el poder activo', rt.get('cantoVivo') is True),
            ('headless: la pala crece (>1,05) al liberar', rt.get('escalaSube') is True),
            ('headless: 45 updates sin error', 'errUpd' not in rt),
            ('headless: chispas animadas (buffer movido)', rt.get('chispasAnimadas') is True),
            ('headless: onda sigue viva en la animación', rt.get('ondaViva') is True),
            ('headless: 2.º gatillo con efecto vivo = pulsación comida', rt.get('segundaComida') is True),
            ('headless: agotamiento devuelve la escala (≤1,05)', rt.get('escalaVuelve') is True),
            ('headless: recarga en marcha tras agotar (>12 s)', rt.get('recargando') is True),
            ('headless: gatillo sin carga: aviso, sin efecto', rt.get('sinCargaOk') is True),
            ('headless: el goteo RECARGA (ready + destello)', rt.get('recargada') is True),
            ('headless: CRAZY COMBO recarga INSTANTÁNEA', rt.get('comboRecarga') is True),
            ('headless: combo durante el efecto repone 8 s', rt.get('comboRepone') is True),
            ('headless: sin poder el gatillo NO es suyo', rt.get('ajenoOk') is True),
            ('headless: leaveAll sin error', 'errLeave' not in rt),
            ('headless: leave devuelve monturas a escala 1', rt.get('leaveLimpio') is True),
            ('headless: leave retira la energía (fx null)', rt.get('fxNull') is True),
            ('headless: leave apaga carga/recarga/match/fx', rt.get('estadoLeave') is True),
            ('headless: puente apagado tras leave (false)', rt.get('puenteApagado') is True),
        ]
        for label, cond in checks:
            chk(cond, label)

        # agujas de diagnóstico (no fallan la capa por sí solas)
        print('  · agujas:', {k: v for k, v in rt.items()
              if k in ('piezas', 'escalaSube', 'escalaVuelve', 'libera',
                       'segunda', 'sinCarga', 'ajeno', 'comboRecarga',
                       'errArm', 'errMatch', 'armado')})

        await browser.close()

    if errors:
        for e in errors[:4]:
            print('  ✗ pageerror:', e[:300])
        fails_total = fails + len(errors)
    else:
        fails_total = fails

    print(f'RESULTADO: {ok} OK · {fails_total} fallos')
    sys.exit(1 if fails_total else 0)


if __name__ == '__main__':
    asyncio.run(main())
