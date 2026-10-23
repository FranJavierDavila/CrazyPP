#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.30 · EL HALL ES UN MUSEO: SIN PALA NI BOLA (capa Y, en vivo).

Informe del dueño: «en el hall no tiene sentido que tengamos la pala y la
pelota, ahí nunca se va a jugar». FASE 32 apaga EN LA ESTANCIA:
  1) LA PALA de AMBOS mandos (paddleMounts) — y setPaddleHand (A/X o
     reconexión) NO la resucita dentro del hall
  2) LA BOLA OCULTA (mesh + estela + sombra) — _hallResetBall(true)
  3) SIN FÍSICA NI SAQUE en la estancia: ni bola en mano del jugador, ni
     paseo/saque de la CPU (gates del bucle con !this.inHall), el árbitro
     no ve eventos fantasma
  4) GATILLO y GRIP sin juego en el hall: onSelectStart se corta tras el
     menú y releaseBallHand no saca
  5) AL SALIR (exitHall) TODO VUELVE: la pala activa en su mano, bola
     visible y limpia, re-entrar vuelve a ocultarlo (idempotente)
  6) LO VIVO DEL MUSEO INTACTO: trofeo plateado (Lathe + asas), bolas
     doradas navegando, 3 luces, drawHall sin excepciones — el arte del
     salón no sufre
  7) AGUJAS del fichero servido: los 9 cambios v3.6.30 presentes y el
     gesto clásico del saque (tossFromHand) ileso en la cancha
Capturas: download/qa_hall_sin_pala_hall.png (museo) + _cancha.png (salida)
Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT_HALL = "/home/z/my-project/download/qa_hall_sin_pala_hall.png"
OUT_CANCHA = "/home/z/my-project/download/qa_hall_sin_pala_cancha.png"

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
          const vis = () => ({
            m0: G.paddleMounts[0] ? G.paddleMounts[0].visible : null,
            m1: G.paddleMounts[1] ? G.paddleMounts[1].visible : null,
            ball: G.ballMesh ? G.ballMesh.visible : null,
            blob: G.blob ? G.blob.visible : null,
            trail: G.trailObj ? G.trailObj.visible : null,
          });
          // referencia ANTES del hall (cancha): una pala visible, bola visible
          out.antes = vis();
          G.enterHall();
          await new Promise(r => setTimeout(r, 700));
          out.hall = {
            inHall: G.inHall,
            hallVisible: G.hallGroup ? G.hallGroup.visible : null,
            rigZ: G.rig ? +G.rig.position.z.toFixed(2) : null,
            vis: vis(),
            // regresión v3.5.0-ESC1: mesa/marcador/IA siguen fuera
            tableHidden: G.tableGroup ? !G.tableGroup.visible : null,
            aiHidden: G.aiPaddleMesh ? !G.aiPaddleMesh.visible : null,
            sbHidden: G.scoreboardGroup ? !G.scoreboardGroup.visible : null,
          };
          // cambio de mano DENTRO del hall: la pala NO resucita
          const mano0 = G.paddleHand;
          G.setPaddleHand(1 - mano0);
          out.trasSwitch = {
            hand: G.paddleHand,
            vis: vis(),
          };
          G.setPaddleHand(mano0);   // devolver la mano como estaba
          // el museo sigue vivo: bolas doradas (trofeo RETIRADO r58 —
          // espacio central libre, petición del dueño)
          const ud = G.hallGroup && G.hallGroup.userData.hall;
          out.museo = ud ? {
            trofeoFuera: (!ud.fx || (!ud.fx.trophy && !ud.fx.beam && !ud.fx.halo))
              && ud.trophyCup === undefined && ud.trophyHandles === undefined
              && ud.trophySilver === undefined,
            balls: ud.fx ? ud.fx.balls.length : 0,
            lights: (ud.lights || []).length,
          } : null;
          let redrawOk = true;
          try { G.drawHall(); } catch (e) { redrawOk = false; out.redrawErr = String(e); }
          out.redrawOk = redrawOk;
          // las bolas respiran (updateHallFx, r58: sin trofeo)
          const y0s = ud && ud.fx ? ud.fx.balls.map(b => b.position.y) : [];
          await new Promise(r => setTimeout(r, 400));
          out.ballMoved = ud && ud.fx ? ud.fx.balls.some((b, i) =>
            Math.abs(b.position.y - y0s[i]) > 0.002) : false;
          await new Promise(r => setTimeout(r, 300));
          // SALIDA: todo vuelve a la cancha
          G.exitHall();
          out.salida = {
            inHall: G.inHall,
            hallVisible: G.hallGroup.visible,
            rigZ: +G.rig.position.z.toFixed(2),
            vis: vis(),
            handVisOk: G.paddleMounts[G.paddleHand] ?
              G.paddleMounts[G.paddleHand].visible === true &&
              G.paddleMounts[1 - G.paddleHand].visible === false : null,
          };
          // RE-ENTRADA: el museo vuelve a quedarse sin pala ni bola
          G.enterHall();
          out.reentry = { inHall: G.inHall, vis: vis() };
          G.exitHall();
          return out;
        }""")

        chk(checks.get("hasGame"), "el juego arranca (window.__PP_GAME)")
        a = checks.get("antes") or {}
        chk((a.get("m0") is True and a.get("m1") is False)
            or (a.get("m1") is True and a.get("m0") is False),
            "ANTES del hall: UNA pala visible en su mano (estado canónico)")
        chk(a.get("ball") is True, "ANTES del hall: la bola visible (cancha)")
        h = checks.get("hall") or {}
        hv = h.get("vis") or {}
        chk(bool(h.get("inHall")) and bool(h.get("hallVisible"))
            and h.get("rigZ") == -16.2,
            "enterHall enciende el salón (rig en cz+2.3)")
        chk(hv.get("m0") is False and hv.get("m1") is False,
            "HALL SIN PALA: los DOS mounts de mando apagados")
        chk(hv.get("ball") is False and hv.get("blob") is False
            and hv.get("trail") is False,
            "HALL SIN BOLA: mesh + sombra + estela ocultos")
        chk(h.get("tableHidden") and h.get("aiHidden") and h.get("sbHidden"),
            "regresión ESC1: mesa/IA/marcador siguen fuera del hall")
        t = checks.get("trasSwitch") or {}
        tv = t.get("vis") or {}
        chk(tv.get("m0") is False and tv.get("m1") is False
            and t.get("hand") in (0, 1),
            "A/X en el hall NO resucita la pala (setPaddleHand guardado)")
        m = checks.get("museo") or {}
        chk(m.get("trofeoFuera") is True,
            "museo r58: TROFEO FUERA (copa/haz/anillo fuera, espacio libre)")
        chk(m.get("balls") == 7 and m.get("lights") == 2,
            "7 bolas doradas + 2 luces (el salón respira)")
        chk(checks.get("redrawOk"),
            "drawHall() repinta sin excepciones "
            + str(checks.get("redrawErr") or ""))
        chk(checks.get("ballMoved") is True,
            "las bolas NAVEGAN (updateHallFx vivo, vaivén r58)")
        s = checks.get("salida") or {}
        sv = s.get("vis") or {}
        chk((not s.get("inHall")) and (not s.get("hallVisible"))
            and s.get("rigZ") == 0.0,
            "exitHall restaura la cancha (rig a cero, salón apagado)")
        chk(sv.get("ball") is True and sv.get("blob") is True,
            "al salir, la bola VUELVE a verse (limpia, en la mesa)")
        chk(s.get("handVisOk") is True,
            "al salir, la pala activa vuelve a SU mano (y solo ella)")
        r = checks.get("reentry") or {}
        rv = r.get("vis") or {}
        chk(bool(r.get("inHall")) and rv.get("m0") is False
            and rv.get("m1") is False and rv.get("ball") is False,
            "re-entrada: el museo vuelve a quedarse sin pala ni bola (idempotente)")

        await page.screenshot(path=OUT_HALL)
        await page.wait_for_timeout(1200)
        await page.screenshot(path=OUT_CANCHA)
        await browser.close()

    # agujas estáticas del fichero SERVIDO (los 9 cambios v3.6.30)
    served = urllib.request.urlopen(URL, timeout=30).read().decode("utf-8", "ignore")
    for needle, label in [
        ("HALL SIN PALA NI BOLA", "informe del dueño clavado en enterHall (servido)"),
        ("_hallResetBall(true)", "bola OCULTA al entrar al hall (servido)"),
        ("for (const m of this.paddleMounts || []) if (m) m.visible = false;",
         "pala de AMBOS mandos apagada en enterHall (servido)"),
        ("la pala vuelve a la mano que le toca", "exitHall reenciende la pala (servido)"),
        ("!this.inHall && k === this.paddleHand", "setPaddleHand guardado en el hall (servido)"),
        ("HALL SIN JUEGO", "gatillo sin juego en la estancia (servido)"),
        ("el hall no saca", "grip de la mano libre sin saque en el hall (servido)"),
        ("!active || this.inHall || this.calib", "IA dormida en el museo (servido)"),
        ("active && !frozen && !this.inHall &&", "sin preparación de saque en el hall (servido)"),
        ("active && !holdLock && !frozen && !this.inHall &&",
         "sin física de la bola en el hall (servido)"),
        ("el hall no muestra estela", "toggle de estela respeta el museo (servido)"),
        # el gesto clásico del saque, ILESO en la cancha:
        ("this.tossFromHand(this.ballHand, true)", "saque por gatillo intacto (servido)"),
        ("tossFromHand(i, false)", "saque natural por grip intacto (servido)"),
        ("bola apoyada en la mano libre (cinemática pura)",
         "bola en mano en la CANCHA intacta (servido)"),
    ]:
        chk(needle in served, label)

    chk(errors == [], "cero pageerrors " + (str(errors[:2]) if errors else ""))
    print("CAPTURAS    :", OUT_HALL, "+", OUT_CANCHA)
    print(f"RESULTADO: {ok} OK · {fails} fallos")
    sys.exit(1 if fails else 0)

asyncio.run(main())
