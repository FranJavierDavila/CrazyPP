#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.28 · SALÓN DEL ARTISTA (capa W, en vivo con Playwright).

El Hall adopta las DIMENSIONES de las salas de campeonato y se viste con
el ARTE DEL ARTISTA mapeado cara a cara (ronda 36, FASE 30):
  1) arranque limpio SIN pageerrors
  2) enterHall() enciende el salón y exitHall() lo apaga (rig, roomGroup)
  3) DIMENSIONES DE SALA: suelo 6,10×7,90 m · paredes 2,85 m de alto
     (frontal/back 6,10 · laterales 7,90 — las canónicas de createRoom)
  4) LAS SEIS CARAS VISTEN ARTE: las 6 texturas assets/hall/*.jpg cargan
     (frente, fondo, izquierda, derecha, suelo, techo) con SRGB
  5) MOBILIARIO VIVO: TROFEO con copa LatheGeometry + 2 asas + haz +
     anillo, 7 bolas doradas flotantes y 3 luces propias
  6) LAS SORPRESAS RESPIRAN: updateHallFx gira el trofeo y anima el
     vaivén (dos muestras del rotation.y separadas 400 ms → delta > 0)
  7) ESTADO DEL TROFEO: sin campeón → material plateado + placa de espera
  8) AGUJAS del fichero servido: assets/hall/*.jpg presentes en el
     fuente, updateHallFx(this.hallGroup, spawn HALL.cz + 2.3, dims 3.05;
     los pintores de pared del museo FUERA del repintado (ud.signTex,
     ud.neonTex, ud.vitrinas, ud.medalCvs ausentes)
  9) los 6 JPG servidos por el servidor con 200 y peso real
Capturas: download/qa_hall_salon_portada.png + qa_hall_salon_hall.png
Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT_PORTADA = "/home/z/my-project/download/qa_hall_salon_portada.png"
OUT_HALL = "/home/z/my-project/download/qa_hall_salon_hall.png"

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
          // esperar a que las 6 texturas del arte terminen de cargar
          let loaded = Object.keys(ud.texs || {}).length;
          for (let i = 0; i < 30 && loaded < 6; i++) {
            await new Promise(r => setTimeout(r, 500));
            loaded = Object.keys(ud.texs || {}).length;
          }
          out.texsLoaded = loaded;
          out.texWant = (ud.texWant || []).length;
          out.srgb = Object.values(ud.texs || {}).every(
            t => t.colorSpace === 3001 || t.colorSpace === 'srgb');  // SRGBColorSpace
          // DIMENSIONES DE SALA (las canónicas de createRoom)
          const dims = (m) => m ? [ +m.geometry.parameters.width.toFixed(2),
                                   +m.geometry.parameters.height.toFixed(2) ] : null;
          out.dims = {
            floor: dims(ud.floor),
            walls: (ud.walls || []).map(dims),
            ceil: dims(ud.ceil),
          };
          out.wallsHaveMap = (ud.walls || []).every(w => w && w.material && w.material.map);
          out.floorHasMap = !!(ud.floor && ud.floor.material && ud.floor.material.map);
          out.ceilHasMap = !!(ud.ceil && ud.ceil.material && ud.ceil.material.map);
          out.retired = {
            signTex: ud.signTex === undefined,
            neonTex: ud.neonTex === undefined,
            vitrinas: ud.vitrinas === undefined,
            medalCvs: ud.medalCvs === undefined,
          };
          out.balls = ud.fx ? ud.fx.balls.length : 0;
          out.trophy = !!(ud.fx && ud.fx.trophy && ud.fx.beam && ud.fx.halo);
          out.cupLathe = !!(ud.trophyCup && ud.trophyCup.geometry &&
                            ud.trophyCup.geometry.type === 'LatheGeometry');
          out.handles = (ud.trophyHandles || []).length;
          out.lights = (ud.lights || []).length;
          out.cupSilver = ud.trophyCup ? ud.trophyCup.material === ud.trophySilver : null;
          // redraw completo en vivo: no debe lanzar
          let redrawOk = true;
          try { G.drawHall(); } catch (e) { redrawOk = false; out.redrawErr = String(e); }
          out.redrawOk = redrawOk;
          // las sorpresas respiran: dos muestras del giro del trofeo
          const r0 = ud.fx.trophy.rotation.y;
          await new Promise(r => setTimeout(r, 400));
          const r1 = ud.fx.trophy.rotation.y;
          out.trophySpin = +(r1 - r0).toFixed(4);
          // las bolas flotantes navegan
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
            "enterHall enciende el salón (rig en cz+2.3, cancha fuera)")
        x = checks.get("exit") or {}
        chk((not x.get("inHall")) and (not x.get("hallVisible"))
            and bool(x.get("roomVisible")) and x.get("rigZ") == 0.0,
            "exitHall restaura la cancha")

        # (v3.6.28: el evaluate devuelve las claves PLANAS — texsLoaded,
        # dims, retired, ... — sin objeto anidado «ud»)
        chk(checks.get("texsLoaded") == 6 and checks.get("texWant") == 6,
            "las 6 texturas del arte cargan (frente/fondo/izq/der/suelo/techo)")
        chk(checks.get("srgb") is True, "texturas en espacio de color SRGB")
        d = checks.get("dims") or {}
        chk(d.get("floor") == [6.1, 7.9],
            "suelo con medidas de sala 6,10×7,90 " + str(d.get('floor')))
        walls = d.get("walls") or []
        chk(len(walls) == 4
            and all(w in ([6.1, 2.85], [7.9, 2.85]) for w in walls),
            "4 paredes a 2,85 m de alto (6,10 las cortas · 7,90 las largas)")
        chk(d.get("ceil") == [6.1, 7.9], "techo con medidas de sala 6,10×7,90")
        chk(checks.get("floorHasMap") and checks.get("ceilHasMap")
            and checks.get("wallsHaveMap"),
            "las 6 caras tienen SU textura puesta (map aplicado)")
        r = checks.get("retired") or {}
        chk(all(r.values()),
            "pintores del museo retirados del ud (sin sign/neon/vitrinas/medallas)")
        chk(checks.get("balls") == 7, "7 bolas doradas flotantes")
        chk(checks.get("trophy") and checks.get("cupLathe")
            and checks.get("handles") == 2,
            "trofeo: copa Lathe + 2 asas + haz + anillo")
        chk(checks.get("lights") == 3, "3 luces propias del salón")
        chk(checks.get("cupSilver") is True,
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
        ("assets/hall/frente.jpg", "arte frontal servido (aguja en fuente)"),
        ("assets/hall/fondo.jpg", "arte fondo con la puerta (aguja en fuente)"),
        ("assets/hall/izquierda.jpg", "arte ventanal izquierdo (aguja en fuente)"),
        ("assets/hall/derecha.jpg", "arte insignias derecho (aguja en fuente)"),
        ("assets/hall/suelo.jpg", "arte del suelo con emblema (aguja en fuente)"),
        ("assets/hall/techo.jpg", "arte del techo con círculo (aguja en fuente)"),
        ("LatheGeometry", "copa del trofeo por tornearia (servido)"),
        ("updateHallFx(this.hallGroup", "gancho de las sorpresas en animate (servido)"),
        ("hx: 3.05", "HALL a ancho de sala 6,10 (servido)"),
        ("depth: 7.9", "HALL a fondo de sala 7,90 (servido)"),
        ("SRGBColorSpace", "carga de arte con color correcto (servido)"),
    ]:
        chk(needle in served, label)
    for viejo in ("ud.signTex", "ud.neonTex", "ud.vitrinas", "ud.medalCvs",
                  "drawHallAchs", "drawHallCirc"):
        chk(viejo not in served, "repintado antiguo " + viejo + " retirado")

    # los 6 JPG vivos en el servidor con peso real
    for f in ("frente", "fondo", "izquierda", "derecha", "suelo", "techo"):
        try:
            data = urllib.request.urlopen(
                "http://localhost:3000/assets/hall/" + f + ".jpg", timeout=30).read()
            chk(len(data) > 100000, "assets/hall/" + f + ".jpg servido ("
                + f"{len(data):,}" + " B)")
        except Exception as ex:
            chk(False, "assets/hall/" + f + ".jpg servido (" + str(ex)[:60] + ")")

    chk(errors == [], "cero pageerrors " + (str(errors[:2]) if errors else ""))
    print("CAPTURAS    :", OUT_PORTADA, "+", OUT_HALL)
    print(f"RESULTADO: {ok} OK · {fails} fallos")
    sys.exit(1 if fails else 0)

asyncio.run(main())
