#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.27 · HALL OF FAME (capa W, en vivo con Playwright).

El Hall del Anfitrión se convierte en HALL OF FAME de ping pong (ronda 35):
  1) arranque limpio SIN pageerrors
  2) enterHall() enciende el museo y exitHall() lo apaga (rig, roomGroup)
  3) ESTRUCTURA DEL MUSEO: cartel HALL OF FAME, neón CRAZY PING PONG,
     placa de RÉCORD Y RANKING, 6 medallones de LOGROS CRAZY (aro + cara),
     6 vitrinas de pieles (base + hoja + placa), fila de campeonatos con
     placa de nombre, TROFEO con copa LatheGeometry + asas + haz + anillo,
     7 bolas doradas flotantes y 3 luces propias
  4) LAS SORPRESAS RESPIRAN: updateHallFx gira el trofeo y anima el vaivén
     (dos muestras del rotation.y separadas 400 ms → delta > 0)
  5) ESTADO DEL TROFEO: sin campeón → material plateado + placa de espera
  6) AGUJAS del fichero servido: drawHallParquet / LatheGeometry /
     updateHallFx(this.hallGroup presentes; los pintores viejos
     drawHallAchs y drawHallCirc FUERA
Capturas: download/qa_hall_fama_portada.png + qa_hall_fama_hall.png
Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import json
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT_PORTADA = "/home/z/my-project/download/qa_hall_fama_portada.png"
OUT_HALL = "/home/z/my-project/download/qa_hall_fama_hall.png"

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
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)

        checks = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const out = {};
          out.hasGame = !!G;
          if (!G) return out;
          G.enterHall();
          await new Promise(r => setTimeout(r, 800));
          out.enter = {
            inHall: G.inHall,
            hallVisible: G.hallGroup ? G.hallGroup.visible : null,
            roomVisible: G.roomGroup ? G.roomGroup.visible : null,
            rigZ: G.rig ? +G.rig.position.z.toFixed(2) : null,
          };
          const ud = G.hallGroup && G.hallGroup.userData.hall;
          if (!ud) { out.ud = null; return out; }
          out.ud = {
            sign: !!(ud.signCv && ud.signTex),
            neon: !!(ud.neonCv && ud.neonTex),
            rank: !!(ud.rankCv && ud.rankTex),
            quote: !!(ud.quoteCv && ud.quoteTex),
            trophyPlaque: !!(ud.trophyCv && ud.trophyTex),
            headerAchs: !!ud.headerAchsTex,
            headerPalas: !!ud.headerPalasTex,
            medals: (ud.medalCvs || []).length,
            medalRims: (ud.medalRims || []).length,
            vitrinas: (ud.vitrinas || []).length,
            vitrinaOk: (ud.vitrinas || []).every(v => v.blade && v.plateCv && v.plateTex),
            champSlots: ud.champRow.userData.slots.length,
            champNames: ud.champRow.userData.slots.every(s => !!s.nameCv),
            balls: ud.fx ? ud.fx.balls.length : 0,
            trophy: !!(ud.fx && ud.fx.trophy && ud.fx.beam && ud.fx.halo),
            cupLathe: !!(ud.trophyCup && ud.trophyCup.geometry &&
                         ud.trophyCup.geometry.type === 'LatheGeometry'),
            handles: (ud.trophyHandles || []).length,
            lights: (ud.lights || []).length,
            cupSilver: ud.trophyCup ? ud.trophyCup.material === ud.trophySilver : null,
          };
          // redraw completo en vivo (idioma + estados): no debe lanzar
          let redrawOk = true;
          try { G.drawHall(); } catch (e) { redrawOk = false; out.redrawErr = String(e); }
          out.redrawOk = redrawOk;
          // las sorpresas respiran: dos muestras del giro del trofeo
          const r0 = ud.fx.trophy.rotation.y;
          await new Promise(r => setTimeout(r, 400));
          const r1 = ud.fx.trophy.rotation.y;
          out.trophySpin = +(r1 - r0).toFixed(4);
          // las bolas flotantes navegan: desplazamiento TOTAL de las 7
          // (con 7 fases distintas, alguna se mueve siempre)
          const y0s = ud.fx.balls.map(b => b.position.y);
          await new Promise(r => setTimeout(r, 500));
          out.ballMoved = ud.fx.balls.some((b, i) =>
            Math.abs(b.position.y - y0s[i]) > 0.002);
          // salida limpia y regreso para la captura
          G.exitHall();
          out.exit = {
            inHall: G.inHall,
            hallVisible: G.hallGroup.visible,
            roomVisible: G.roomGroup.visible,
            rigZ: +G.rig.position.z.toFixed(2),
          };
          G.enterHall();
          return out;
        }""")

        chk(checks.get("hasGame"), "el juego arranca (window.__PP_GAME)")
        e = checks.get("enter") or {}
        chk(bool(e.get("inHall")) and bool(e.get("hallVisible"))
            and e.get("roomVisible") is False and e.get("rigZ") == -16.2,
            "enterHall enciende el museo (rig en el hall, cancha fuera)")
        x = checks.get("exit") or {}
        chk((not x.get("inHall")) and (not x.get("hallVisible"))
            and bool(x.get("roomVisible")) and x.get("rigZ") == 0.0,
            "exitHall restaura la cancha")

        ud = checks.get("ud")
        chk(ud is not None, "userData.hall montado")
        if ud:
            chk(ud.get("sign") and ud.get("neon") and ud.get("rank")
                and ud.get("quote") and ud.get("trophyPlaque"),
                "lienzos del museo: cartel + neón + ranking + cita + placa del trofeo")
            chk(ud.get("headerAchs") and ud.get("headerPalas"),
                "cabeceras de las paredes laterales")
            chk(ud.get("medals") == 6 and ud.get("medalRims") == 6,
                "6 medallones de logros (cara + aro)")
            chk(ud.get("vitrinas") == 6 and ud.get("vitrinaOk"),
                "6 vitrinas de pieles con hoja y placa")
            chk(ud.get("champSlots", 0) >= 1 and ud.get("champNames"),
                "fila de campeonatos con placa de nombre")
            chk(ud.get("balls") == 7, "7 bolas doradas flotantes")
            chk(ud.get("trophy") and ud.get("cupLathe") and ud.get("handles") == 2,
                "trofeo: copa Lathe + 2 asas + haz + anillo")
            chk(ud.get("lights") == 3, "3 luces propias del museo")
            chk(ud.get("cupSilver") is True,
                "sin campeón: trofeo PLATEADO esperando")
            chk(checks.get("redrawOk"),
                "drawHall() repinta sin excepciones "
                + str(checks.get("redrawErr") or ""))
            spin = checks.get("trophySpin")
            chk(isinstance(spin, (int, float)) and spin > 0,
                "el trofeo GIRA (updateHallFx vivo, delta " + str(spin) + ")")
            chk(checks.get("ballMoved") is True,
                "las bolas flotantes navegan (vaivén vivo)")

        await page.screenshot(path=OUT_PORTADA)
        await page.wait_for_timeout(1200)
        await page.screenshot(path=OUT_HALL)
        await browser.close()

    # agujas estáticas del fichero SERVIDO
    served = urllib.request.urlopen(URL, timeout=30).read().decode("utf-8", "ignore")
    for needle, label in [
        ("drawHallParquet", "parqué con emblema de la casa (servido)"),
        ("LatheGeometry", "copa del trofeo por tornearia (servido)"),
        ("updateHallFx(this.hallGroup", "gancho de las sorpresas en animate (servido)"),
        ("HALL OF FAME", "cartel HALL OF FAME (servido)"),
        ("HALL_SKIN_NAMES", "nombres de pieles para las vitrinas (servido)"),
    ]:
        chk(needle in served, label)
    for viejo in ("drawHallAchs", "drawHallCirc"):
        chk(viejo not in served, "pintor antiguo " + viejo + " retirado")

    chk(errors == [], "cero pageerrors " + (str(errors[:2]) if errors else ""))
    print("CAPTURAS    :", OUT_PORTADA, "+", OUT_HALL)
    print(f"RESULTADO: {ok} OK · {fails} fallos")
    sys.exit(1 if fails else 0)

asyncio.run(main())
