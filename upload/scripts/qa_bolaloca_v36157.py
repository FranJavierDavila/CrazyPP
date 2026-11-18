#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA FASE 160 · BOLA LOCA + REGLA «SOLO 1 SUPERPODER EN MARCHA» (r66).

Peticiones del dueño verificadas:
  1) «el jugador solo pueda lanzar un superpoder de pala de cada vez…
     SOLO cuando este se termine podrá aplicar otro» — _poderVivoAlguno()
     + los DOS gatillos bloquean un poder DISTINTO (sin consumo), el
     MISMO poder se refresca (patrón imán r57).
  2) BOLA LOCA (15.º poder): la original del Wizard de magia — bola
     ×1,65 con radio físico, ciclo arcoíris (hue 0,30 · 0.9/0.58 +
     emissive 0.22), deriva aleatoria del mago (vaivén 4 m/s² a 8,5
     rad/s + ráfagas 2,5 m/s² cada 0,22 s), 10 s, icono del dueño
     (SuperPala_BolaLoca.png → 64 colores), voces Piper nativas ES/EN,
     anuncio con la MISMA voz del sistema (concesión + selector) y
     nombre corto en duelos (dl_bolaloca).
  3) SIEMPRE desbloqueada: poderesDesbloqueados la SIEMBRA (sin candado
     en el Arcano — la galería ABRE en ella), disponible DE INICIO en
     Duelos Locos (surto = base + desbloqueados − vieja loca) y
     EXCLUIDA del sorteo aleatorio de la coronación. En campeonatos, un
     superpoder más (el sorteo de cargas la puede conceder).

Pruebas: 1) FUENTE SERVIDA (agujas del núcleo + i18n ES/EN + conservación
r65) · 2) MECÁNICA REAL en headless (desbloqueo de serie, exclusión del
sorteo, regla solo-1 con bloqueo y liberación, refresco del MISMO poder,
bola ×1,65 con radio físico, deriva viva, ciclo de color, restauración
exacta).

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
    errors = []

    # ---------- 1 · FUENTE SERVIDA ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)

    for needle, label in [
        # registro + assets
        ("{ id: 'bolaloca', dur: ARCANO_CFG.ventanas.bolaloca, nombre: () => T('poder_bolaloca'),",
         'registro: entrada BOLA LOCA (15.º poder, al final — patrón r25/r33)'),
        ('voz: VOZ_PODER_BOLALOCA, vozEn: VOZ_PODER_BOLALOCA_EN, png: PNG_PODER_BOLALOCA',
         'bolaloca: voz ES + voz EN + PNG en el registro'),
        ('const PNG_PODER_BOLALOCA', 'icono del dueño embebido (data-URI)'),
        ('const VOZ_PODER_BOLALOCA_EN', 'voz EN embebida (traducida)'),
        # parámetros EXACTOS del mago (LOCA_BALL de championships/magia)
        ('const BOLALOCA_SCALE = 1.65;', 'bola ×1,65 (el mago)'),
        ('const BOLALOCA_HUE_V = 0.30;', 'ciclo de color 0,30 vueltas/s (el mago)'),
        ('const BOLALOCA_SWAY = 4.0;', 'vaivén 4 m/s² (el mago)'),
        ('const BOLALOCA_FREQ = 8.5;', 'frecuencia 8,5 rad/s (el mago)'),
        ('const BOLALOCA_JIT = 2.5;', 'ráfagas 2,5 m/s² (el mago)'),
        ('const BOLALOCA_JT = 0.22;', 'ráfagas cada 0,22 s (el mago)'),
        ('const BOLALOCA_DUR = ARCANO_CFG.ventanas.bolaloca;', 'ventana 10 s (c02)'),
        ('bolaloca: 10,', 'c02: ventana bolaloca de 10 s'),
        # regla SOLO 1
        ('_poderVivoAlguno()', 'helper de la regla «solo 1 poder en marcha»'),
        ('REGLA DEL DUEÑO: SOLO 1 superpoder de pala en marcha', 'gate del megaTrigger'),
        ('vivoDL && vivoDL !== idPend) return false', 'gate del _dlTrigger (duelos)'),
        ("if (ent.id === 'bolaloca') return this._bolalocaTrigger(ent);", 'dispatcher: gatillo libera bolaloca'),
        # trigger/frame/fin
        ('_bolalocaTrigger(ent) {', 'trigger propio (patrón efecto/iman)'),
        ('_bolalocaFrame(dt) {', 'frame propio (ciclo + deriva)'),
        ('_bolalocaFin() {', 'fin propio (restauración exacta)'),
        ('_bolalocaAplicaFx() {', 'aplicación del efecto (patrón _applyBallFx del mago)'),
        ('DIMS.ballRadius = this._bolalocaFx.r * BOLALOCA_SCALE;', 'radio físico acompaña (magia v2.72)'),
        ('m.material.color.setHSL(hue, 0.9, 0.58);', 'ciclo HSL del mago (0.9/0.58)'),
        ('m.material.emissive.setHSL(hue, 0.9, 0.22);', 'emissive del mago (0.9/0.22)'),
        ('Math.sin(this._bolalocaPh * BOLALOCA_FREQ)', 'vaivén sinusoidal del mago'),
        ('(Math.random() - 0.5) * 2 * BOLALOCA_JIT', 'ráfaga aleatoria del mago'),
        ('pwViva(this._bolalocaT)', 'puerta única pwViva (updateMega)'),
        ("['_bolalocaT', '_bolalocaFin']", '_dlVentanasApaga la recoge (fin natural)'),
        # desbloqueo de serie
        ('BOLA LOCA SIEMPRE DESBLOQUEADA', 'siembra de serie en poderesDesbloqueados'),
        ("lista.unshift('bolaloca');", 'la siembra la pone PRIMERA de la lista'),
        ("filter((id) => id !== 'loca')", 'surto: la vieja loca (spin) SALE — no duplica nombre'),
        ('bolaloca: ARCANO_CFG.ventanas.bolaloca,', 'DL_DUR: ventana de bolaloca en duelos'),
        ("bolaloca: '_bolalocaTrigger',", '_dlArma: el armado de duelos conoce bolaloca'),
        # galería del Arcano
        ("bolaloca: ['arcono_tipo_distraccion', '#c39bff']", 'ficha del Arcano: distracción violeta'),
        ('PODERES_PALA.findIndex', 'la galería ABRE en bolaloca (primer desbloqueado)'),
        # wiring secundario
        ("if (ent.id === 'bolaloca') return this._bolalocaT > 0;", 'icono: modo ACTIVO'),
        ("if (this._megaActivaId === 'bolaloca') return this._bolalocaT;", 'icono: anillo de tiempo'),
        ("else if (id === 'bolaloca') par = [VOZ_PODER_BOLALOCA, VOZ_PODER_BOLALOCA_EN];", 'selector: voz al ciclar'),
        ("this._megaVozPrecalentar('bolaloca');", 'precaliente: voz lista ANTES del gatillo'),
        ('la BOLA LOCA también calla en etapas 2/4', 'cortina: etapas de prueba sin poderes'),
        # i18n ES/EN
        ("dl_bolaloca: 'BOLA LOCA',", 'i18n ES: nombre corto de duelos'),
        ("dl_bolaloca: 'CRAZY BALL',", 'i18n EN: nombre corto de duelos'),
        ("arc_bolaloca_go: '¡BOLA LOCA!", 'i18n ES: aviso de activación'),
        ("arc_bolaloca_fin: 'BOLA LOCA agotada',", 'i18n ES: aviso de fin'),
        ("poder_bolaloca: '¡BOLA LOCA!',", 'i18n ES: nombre de concesión'),
        ("arc_bolaloca_go: 'CRAZY BALL!", 'i18n EN: aviso de activación'),
        ("arc_bolaloca_fin: 'CRAZY BALL worn off',", 'i18n EN: aviso de fin'),
        ("poder_bolaloca: 'CRAZY BALL!',", 'i18n EN: nombre de concesión'),
        ("poder_uno_activo: 'Ya hay un superpoder activo · espera a que termine',",
         'i18n ES: mensaje de la regla solo-1'),
        ("poder_uno_activo: 'A superpower is already active · wait for it to end',",
         'i18n EN: mensaje de la regla solo-1'),
        # conservación r65 (el saque sigue blindado)
        ('LA BOLA SIEMPRE VUELVE A TU MANO', 'conservación r65: watchdog del saque'),
        ('_srvManoValida(bh) {', 'conservación r65: pose fresca + plausible'),
        # recepción compat build viejo
        ("dl_loca: 'BOLA LOCA',", 'la vieja loca sigue VIVA para rivales build anterior'),
    ]:
        chk(needle in game, label)

    # conteos de data-URIs (los 3 nuevos van dentro)
    chk(game.count('data:image/png;base64,') >= 15,
        'iconos embebidos: el registro completo (15 poderes con PNG)')
    chk(game.count('data:audio/mpeg;base64,') >= 30,
        'voces embebidas: concesiones + selector ES/EN')

    # los assets de _poder160 existen en disco
    from pathlib import Path
    p160 = Path('/home/z/my-project/upload/scripts/_poder160')
    for f, label in [
        ('icono_bolaloca_64.png', 'icono cuantizado 64 colores en _poder160'),
        ('voz_bolaloca_es.mp3', 'voz Piper davefx (ES) en _poder160'),
        ('voz_bolaloca_en.mp3', 'voz Piper lessac (EN) en _poder160'),
    ]:
        chk((p160 / f).exists() and (p160 / f).stat().st_size > 1000, label)

    # el ORIGINAL del mago queda INTACTO (fuente de verdad de los parámetros)
    try:
        magia = urllib.request.urlopen(
            'http://localhost:3000/championships/magia/index.js',
            timeout=10).read().decode('utf-8')
        chk('scale: 1.65' in magia and 'hueSpeed: 0.30' in magia,
            'magia: LOCA_BALL intacto (fuente de verdad de los parámetros)')
        chk("kind: 'crazyball'" in magia, 'magia: la BOLA LOCA del Wizard vive')
    except Exception as e:
        chk(False, f'magia/index.js servido ({e})')

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
          G.palaMejorada = true;
          const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
          const libre = (G.paddleHand === 0) ? 1 : 0;
          const rndReal = Math.random;   // la casa: guardar el azar real
          const azar = (v) => { Math.random = () => v; };
          const azarReal = () => { Math.random = rndReal; };

          out.hayAPI = typeof G._poderVivoAlguno === 'function' &&
            typeof G._bolalocaTrigger === 'function' &&
            typeof G._bolalocaFrame === 'function' &&
            typeof G._bolalocaFin === 'function' &&
            typeof G._bolalocaAplicaFx === 'function' &&
            typeof G.poderesDesbloqueados === 'function' &&
            typeof G._arconoCampeonGanado === 'function';

          // · DESBLOQUEO DE SERIE: sin localStorage, la BOLA LOCA está
          try { localStorage.removeItem('pp_poderes_v1'); } catch (e) { /* */ }
          const des = G.poderesDesbloqueados();
          out.siembra = des.indexOf('bolaloca') === 0;
          out.siembraPersiste = (() => {
            try { return JSON.parse(
              localStorage.getItem('pp_poderes_v1') || '[]')
              .indexOf('bolaloca') === 0; } catch (e) { return false; }
          })();

          // · EXCLUSIÓN DEL SORTEO DE CORONACIÓN: con la mano vacía, el
          //   azar al fondo (0.999) NUNCA cae en bolaloca (no está con
          //   candado) — cae en el último CON candado ('ancla')
          azar(0.999);
          const ganado = G._arconoCampeonGanado();
          out.sorteoExcluye = ganado === 'ancla';
          azarReal();
          try { localStorage.removeItem('pp_poderes_v1'); } catch (e) { /* */ }

          // · PARTIDO de campeonato + rally controlado
          try { G.rules.startMatch('match'); } catch (e) { out.errMatch = String(e); }
          G.champs.activeId = 'locura';
          G.rules.state = 'rally';
          const paso = (s) => { try { G.updateMega(s || 1 / 60); } catch (e) { out.errUpd = String(e); } };

          // estado fresco de la ventana
          out.fresco = G._bolalocaT === 0 && G._bolalocaFx === null &&
            G._bolalocaReloj === 0;

          // · GRANT con Math.random=0 → ids[0] = 'mega' (conservación del
          //   orden histórico) — y bolaloca se concede con 0.999 (la ÚLTIMA)
          azar(0);
          G.rules.rallyHits = 20; paso();
          out.megaPrimera = G._megaMatriz.length === 1 &&
            G._megaMatriz[0].id === 'mega';
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally';
          azar(0.999);
          G.rules.rallyHits = 20; paso();
          out.bolalocaUltima = G._megaMatriz.some((x) => x.id === 'bolaloca');
          azarReal();
          G._megaMatriz.length = 0; G._megaIdx = 0; G._megaIcon = null;
          G._megaTexDirty = false;

          // · REGLA SOLO 1: bola loca activa BLOQUEA otro poder (sin gasto)
          //   (el radio físico DIMS.ballRadius se verifica por AGUJAS — el
          //   identificador no se expone en window; la física c04 lo lee
          //   VIVO en cada bote: «const r = DIMS.ballRadius»)
          const entB = { id: 'bolaloca', n: 1 };
          const entE = { id: 'efecto', n: 1 };
          G._megaMatriz.push(entB, entE);
          G._megaIdx = G._megaMatriz.indexOf(entB);
          G.ball.vel.set(2.4, 1.4, -3.2);
          const col0 = G.ballMesh.material.color.getHex();
          let r = null;
          try { r = G.megaTrigger(libre); } catch (e) { out.errTr = String(e); }
          out.activa = r === true && G._bolalocaT > 9.5;
          out.crece = Math.abs(G.ballMesh.scale.x - 1.65) < 1e-6;
          out.moradaArranque = G.ballMesh.material.color.getHex() === 0x8a4fff;

          // deriva viva + ciclo de color en 30 pasos de 50 ms
          const vx0 = G.ball.vel.x;
          for (let i = 0; i < 30; i++) { paso(0.05); await dorme(2); }
          out.deriva = Math.abs(G.ball.vel.x - vx0) > 0.01;
          out.cicloColor = G.ballMesh.material.color.getHex() !== 0x8a4fff &&
            G.ballMesh.material.color.getHex() !== col0;

          // bloqueo del OTRO poder (efecto seleccionado, bola loca viva)
          G._megaIdx = G._megaMatriz.indexOf(entE);
          const nE = entE.n;
          let r2 = null;
          try { r2 = G.megaTrigger(libre); } catch (e) { out.errBlq = String(e); }
          out.bloquea = r2 === true && G._efectoT === 0 && entE.n === nE;
          out.msgRegla = (G.rules.message || '')
            .indexOf('Ya hay un superpoder activo') === 0 ||
            (G.rules.message || '')
              .indexOf('A superpower is already active') === 0;

          // refresco del MISMO poder permitido (patrón imán r57): con OTRA
          // carga de bolaloca seleccionada mientras la ventana corre, el
          // gatillo REFRESCA (no bloquea — la regla prohíbe DOS poderes,
          // no recargar el vivo)
          const entB2 = { id: 'bolaloca', n: 1 };
          G._megaMatriz.push(entB2);
          G._megaIdx = G._megaMatriz.indexOf(entB2);
          const tAntes = G._bolalocaT;
          let r3 = null;
          try { r3 = G.megaTrigger(libre); } catch (e) { out.errRef = String(e); }
          out.refrescoMismo = r3 === true && G._bolalocaT > 9.5 &&
            G._bolalocaT >= tAntes;

          // · FIN NATURAL: la ventana corre y TODO se restaura EXACTO
          for (let i = 0; i < 230 && G._bolalocaT > 0; i++) {
            paso(0.05); await dorme(1);
          }
          out.finNatural = G._bolalocaT === 0;
          out.restaura = Math.abs(G.ballMesh.scale.x - 1) < 1e-6 &&
            G.ballMesh.material.color.getHex() === col0 &&
            G._bolalocaFx === null;

          // liberado el turno: el OTRO poder ya se puede lanzar
          G._megaIdx = G._megaMatriz.indexOf(entE);
          let r4 = null;
          try { r4 = G.megaTrigger(libre); } catch (e) { out.errLib = String(e); }
          out.libera = r4 === true && G._efectoT > 9.5;
          // y el efecto acabado libera de nuevo
          G._efectoT = 0; G._efectoWarn = false; G._efectoTickN = 0;
          try { if (G._efectoFin) G._efectoFin(); } catch (e) { /* */ }
          out.vivoNadie = G._poderVivoAlguno() === '';

          // limpieza honesta del estado de prueba
          G._megaMatriz.length = 0; G._megaIdx = 0; G._megaIcon = null;
          G._megaActivaId = null;
          G.champs.activeId = '';
          return out;
        }""")
        await browser.close()

        for k, v in sorted(rt.items()):
            if isinstance(v, bool):
                chk(v, 'mecánica: ' + k)
            else:
                chk(False, f'mecánica: {k} = {v}')
        chk(not errors, f'sin pageerrors ({len(errors)})')
        if errors:
            print('   pageerrors:', errors[:3])

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
