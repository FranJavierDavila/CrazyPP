#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.32 · MEGA PALA CON FEEDBACK VISUAL (capa AA, en vivo).

Petición del dueño tras V3.6.31:
  «Si la MEGA PALA sí existe debería dar feedback visual de alguna forma,
  aumentando el tamaño de la raqueta y poniendo una alerta visual como de
  energía o algún efecto que indique que la pala del jugador tiene ese
  poder.»

La MEGA PALA (poder de La Locura: Crazy Combo con rally de 6 tras vencer
al Clown · radio de detección ×1,38 · 8 s) era INVISIBLE. Ahora:
  · la pala CRECE a ×1,30 (montura visual, física intacta)
  · aura dorada + doble anillo de energía girando en la hoja
  · power-up sonoro + háptica al activarse; parpadeo en los <2 s finales
  · leave() recoge todo con dispose y las monturas vuelven a escala 1

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del módulo locura servido por el dev server
     (métodos nuevos, escala 1.3, dispose en leave, aviso <2 s, arpegio)
  2) MECÁNICA REAL en headless — launch('locura'), poder forzado,
     _megaFxStart(), muestreo de la escala de la montura, energía viva,
     agotamiento (vuelta suave a escala 1) y restauración en leaveAll

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
        ('_megaFxStart()', 'arranque del efecto (método nuevo)'),
        ('_buildMegaFx()', 'construcción perezosa de la energía'),
        ('_megaFxDispose()', 'recogida con dispose (regla Quest)'),
        ('this._megaFxDispose();', 'leave() recoge MEGA PALA + radio + escala'),
        ('this._megaFxStart();', 'activación en Crazy Combo con poder'),
        ('? 1.3 : 1.0', 'pala crece a ×1,30 mientras dura el poder'),
        ('AdditiveBlending', 'aura/anillos aditivos (energía)'),
        ('TorusGeometry(0.104', 'anillo interior en el borde de la hoja'),
        ('TorusGeometry(0.128', 'anillo exterior (halo)'),
        ('createRadialGradient', 'aura con gradiente radial dorado'),
        ('this._megaWarn = true', 'aviso único de agotamiento'),
        ("playOsc(420, 860", 'arpegio arcade al activarse'),
        ("playOsc(880, 440", 'sfx descendente en los <2 s finales'),
        ('haptic(g.paddleHand, 0.75, 180)', 'háptica de power-up'),
        ('this._megaS = 0', 'estado de escala inicializado'),
        ('cero directo: restaura YA', 'regresión del radio (startMatch) cubierta'),
    ]:
        chk(needle in served, label)
    chk("T('arc_combo')" in served, 'regresión: el mensaje CRAZY COMBO sigue vivo')

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
          // v3.6.32: con el arreglo de la carrera eager↔launch (c11), start()
          // ya encuentra el módulo cableado; el sondeo es cinturón y tirantes
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
          out.tieneImpl = !!impl && typeof impl._megaFxStart === 'function';
          if (!out.tieneImpl) return out;
          out.activo = impl.active === true;
          // estado fresco: en reposo _megaS converge a 1.0 (update vivo) y
          // _megaFx es null / _megaFxOn false (energía apagada)
          out.fresco = (impl._megaS === 0 || Math.abs(impl._megaS - 1) < 0.02) &&
                       impl._megaFx === null && impl._megaFxOn === false;
          const pp = impl && impl.data && impl.data.playerPower;
          out.poder = !!pp && pp.kind === 'mega_pala';
          out.alcance = !!pp && pp.reachMul === 1.38;
          out.duracion = !!pp && pp.duration >= 7;

          // ---- ACTIVACIÓN (poder forzado: sin jugar 4 rondas) ----
          // v3.6.32: headless swiftshader ronda los 4 fps — en vez de esperar
          // tiempo real, AVANCE DETERMINISTA llamando impl.update(1/60): el
          // bucle vivo se verifica aparte (decremento de _megaT)
          try {
            if (!impl.powers.includes('mega_pala')) impl.powers.push('mega_pala');
            impl._megaT = pp.duration || 8;
            impl._megaFxStart();
          } catch (e) { out.errStart = String(e); }
          for (let i = 0; i < 45 && !out.errUpd; i++) {
            try { impl.update(1 / 60); } catch (e) { out.errUpd = String(e); }
          }
          const hand = G.paddleHand | 0;
          out.monta = !!(G.paddleMounts && G.paddleMounts[hand]);
          if (out.monta) {
            out.escalaOn = G.paddleMounts[hand].scale.x;
            out.crecio = out.escalaOn > 1.15;
          }
          out.fxVivo = impl._megaFxOn === true && !!impl._megaFx &&
            impl._megaFx.every((fx) => !fx || fx.visible === true);
          const fxA = impl._megaFx && impl._megaFx.find((fx) => fx);
          out.piezas = fxA ? fxA.children.length : 0;   // aura + 2 anillos
          out.anillos = fxA ? !!(fxA.userData.ring && fxA.userData.ring2) : false;
          out.auraSprite = fxA ? !!fxA.userData.aura : false;

          // ---- AGOTAMIENTO: vuelta suave a la normalidad (determinista) ----
          try { impl._megaT = 0.25; } catch (e) { /* */ }
          for (let i = 0; i < 70 && !out.errUpd2; i++) {
            try { impl.update(1 / 60); } catch (e) { out.errUpd2 = String(e); }
          }
          if (out.monta) {
            out.escalaOff = G.paddleMounts[hand].scale.x;
            out.volvio = out.escalaOff <= 1.02;
          }
          out.fxApagado = impl._megaFxOn === false;

          // ---- BUCLE VIVO: el juego REAL decrementa _megaT por frame ----
          try { impl._megaT = 5; } catch (e) { /* */ }
          await dorme(1100);
          out.bucleVivo = impl._megaT > 0.5 && impl._megaT < 4.95;

          // ---- LEAVE: recogida COMPLETA ----
          try { C.leaveAll(); } catch (e) { out.errLeave = String(e); }
          await dorme(400);
          if (out.monta) {
            out.escalaLeave = G.paddleMounts[hand].scale.x;
            out.leaveLimpio = out.escalaLeave === 1;
          }
          out.fxNull = impl._megaFx === null;
          return out;
        }""")

        for label, cond in [
            ('headless: juego y ChampLoader vivos', not (rt.get('sinJuego') or rt.get('sinChamps'))),
            ('headless: catálogo de campeonatos cargado (≤60 s)', rt.get('catalogo') is True),
            ('headless: launch(locura) sin error', 'errLaunch' not in rt),
            ('headless: wrapper del módulo registrado', rt.get('tieneWrapper') is True),
            ('headless: impl de La Locura activo (update vivo)', rt.get('activo') is True),
            ('headless: impl de La Locura con _megaFxStart()', rt.get('tieneImpl') is True),
            ('headless: estado fresco del efecto (fx null / energía apagada)', rt.get('fresco') is True),
            ('headless: playerPower.kind = mega_pala (manifest v24)', rt.get('poder') is True),
            ('headless: reachMul 1.38 · duración 8 s intactos', rt.get('alcance') is True and rt.get('duracion') is True),
            ('headless: _megaFxStart() sin error', 'errStart' not in rt),
            ('headless: 45 updates manuales sin error', 'errUpd' not in rt),
            ('headless: montura de pala presente', rt.get('monta') is True),
            ('headless: la pala CRECIÓ (>1.15) con el poder vivo', rt.get('crecio') is True),
            ('headless: energía VIVA (visible en ambas monturas)', rt.get('fxVivo') is True),
            ('headless: aura + 2 anillos por montura (3 piezas)', rt.get('piezas') == 3),
            ('headless: userData anillos presente', rt.get('anillos') is True),
            ('headless: aura es Sprite (billboard)', rt.get('auraSprite') is True),
            ('headless: al agotarse la pala vuelve (≤1.02)', rt.get('volvio') is True),
            ('headless: energía apagada al agotarse', rt.get('fxApagado') is True),
            ('headless: bucle vivo decrementa _megaT (integración real)', rt.get('bucleVivo') is True),
            ('headless: leaveAll sin error', 'errLeave' not in rt),
            ('headless: tras leaveAll montura a escala exacta 1', rt.get('leaveLimpio') is True),
            ('headless: tras leaveAll fx retirado (null)', rt.get('fxNull') is True),
        ]:
            chk(cond, label + (f' [escalaOn={rt.get("escalaOn")}, off={rt.get("escalaOff")}, leave={rt.get("escalaLeave")}]'
                if 'CRECI' in label or 'vuelve' in label or 'escala exacta' in label else ''))

        await browser.close()

    chk(errors == [], 'cero pageerrors ' + (str(errors[:2]) if errors else ''))
    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)

asyncio.run(main())
