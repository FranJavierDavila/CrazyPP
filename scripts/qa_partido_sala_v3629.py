#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.29 · SALA DEL PARTIDO + MEJOR DE 3 (capa X, en vivo Playwright).

Ronda 37 (FASE 31), dos entregas del dueño en una:
  A) EL ESCENARIO DEL PARTIDO (Match) VISTE EL ARTE POR DEFECTO:
     1) arranque limpio SIN pageerrors
     2) champRoom.defaultKeys = las 6 claves (frente/fondo/izq/der/suelo/techo)
     3) las 6 caras de la cancha clásica con SU map aplicado (suelo, techo y
        4 paredes — assets/partido/, dimensiones canónicas de createRoom)
     4) IZQUIERDA y DERECHA comparten IMAGEN (misma textura, petición expresa)
     5) complementos del núcleo ocultos bajo el arte (rejilla, paneles, tiras)
     6) contrato P2P: applySync espeja la serie (bo/gp/ga/gw) sin romper
  B) MEJOR DE 3 (árbitro real, en vivo):
     7) juego 1 (11-5): serie 1-0, marcador a cero, saque del otro, intent
        'serve' con gameEnd — el enfrentamiento SIGUE
     8) juego 2 (11-8): serie acabada → state 'over' + intent 'game-over' +
        mensaje de ENFRENTAMIENTO (2·victorias > bestOf)
     9) bestOf=1 (campeonatos): el primer juego decide, mensajes clásicos
    10) marcador 3D: repinta con la serie sin excepciones
    11) agujas del servido: assets/partido/*, keys i18n, bestOf=3 en los
        caminos del partido libre y bestOf=1 en el launch de campeonatos
    12) los 5 JPG servidos con 200 y peso real
Captura: download/qa_partido_sala.png (la cancha vestida)
Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT = "/home/z/my-project/download/qa_partido_sala.png"

PESOS = {  # bytes exactos de los JPG del dueño (upload/partido.zip)
    "frente.jpg": 342732,
    "fondo.jpg": 447871,
    "izquierda.jpg": 395715,
    "suelo.jpg": 248567,
    "techo.jpg": 390609,
}

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
          const out = { hasGame: !!G, errs: [] };
          if (!G) return out;

          /* ---- A · ARTE POR DEFECTO DEL PARTIDO ---- */
          const cr = G.champRoom;
          out.hasChampRoom = !!cr;
          if (!cr) return out;
          let dk = cr.defaultKeys || [];
          for (let i = 0; i < 30 && dk.length < 6; i++) {
            await new Promise(r => setTimeout(r, 500));
            dk = cr.defaultKeys || [];
          }
          out.defaultKeys = dk.slice().sort();
          const ud = G.roomGroup ? G.roomGroup.userData : null;
          out.hasUd = !!ud;
          if (!ud) return out;
          const mats = [];
          if (ud.floorMat) mats.push(['floor', ud.floorMat]);
          if (ud.ceilMat) mats.push(['ceil', ud.ceilMat]);
          (ud.wallMats || []).forEach((m, i) => mats.push(['wall' + i, m]));
          out.maps = mats.map(([k, m]) => [k, !!(m && m.map)]);
          out.allMapped = out.maps.every(([, v]) => v);
          // izquierda y derecha comparten textura (wallMats[0] y [1])
          const wm = ud.wallMats || [];
          out.sharedSides = !!(wm[0] && wm[1] && wm[0].map && wm[0].map === wm[1].map);
          // complementos ocultos bajo el arte
          out.gridHidden = ud.grid ? ud.grid.visible === false : null;
          out.panelsHidden = (ud.panels || []).every(pn => pn.visible === false);
          out.stripsHidden = (ud.strips || []).every(s => s.visible === false);

          /* ---- A6 · CONTRATO P2P (applySync espeja la serie) ---- */
          try {
            G.net.applySync({ st: 'serve', sv: 'player', sp: 3, sa: 1,
              md: 'match', ow: 'host', rh: 0,
              bo: 3, gp: 1, ga: 0, gw: { w: 'player', p: 11, q: 8 } });
            out.p2p = { bo: G.rules.bestOf, gp: G.rules.gamesPlayer,
                        ga: G.rules.gamesAi };
          } catch (e) { out.p2p = { err: String(e) }; }

          /* ---- B · MEJOR DE 3 con el ÁRBITRO REAL ---- */
          const R = G.rules;
          R.bestOf = 3;
          R.startMatch('match');
          // juego 1: 11-5 para el jugador (causa 'out', siempre válida)
          for (let i = 0; i < 16; i++) R.applyPoint(i < 11 ? 'player' : 'ai', 'out');
          const evs1 = [];
          for (let k = 0; k < 8 && R.state === 'point'; k++) evs1.push(...R.update(0.5));
          out.g1 = {
            state: R.state, sp: R.scorePlayer, sa: R.scoreAi,
            gp: R.gamesPlayer, ga: R.gamesAi, gameNo: R.gameNo, srv: R.server,
            msg: R.message,
            serveIntent: evs1.find(e => e.type === 'serve') || null,
          };
          // juego 2: 11-8 → serie acabada
          for (let i = 0; i < 19; i++) R.applyPoint(i < 11 ? 'player' : 'ai', 'out');
          const evs2 = [];
          for (let k = 0; k < 8 && R.state === 'point'; k++) evs2.push(...R.update(0.5));
          out.g2 = {
            state: R.state, gp: R.gamesPlayer, ga: R.gamesAi, msg: R.message,
            overIntent: evs2.find(e => e.type === 'game-over') || null,
          };
          // bestOf=1 (campeonatos): el primer juego decide
          R.bestOf = 1;
          R.startMatch('match');
          for (let i = 0; i < 12; i++) R.applyPoint(i < 1 ? 'player' : 'ai', 'out');
          const evs3 = [];
          for (let k = 0; k < 8 && R.state === 'point'; k++) evs3.push(...R.update(0.5));
          out.g3 = { state: R.state, msg: R.message, gp: R.gamesPlayer,
                     over: evs3.some(e => e.type === 'game-over') };
          // marcador 3D con la serie: repinta sin excepciones
          let sbOk = true;
          try {
            G.scoreboardUpdate({ player: 0, ai: 0, server: 'player',
              message: 'qa serie', mode: 'match', rally: 0, rallyes: 0, best: 0,
              gamesPlayer: 1, gamesAi: 0, bestOf: 3 });
          } catch (e) { sbOk = false; out.sbErr = String(e); }
          out.sbOk = sbOk;
          // dejar el juego en saque limpio de partido libre
          R.bestOf = 3;
          R.startMatch('match');
          return out;
        }""")

        chk(checks.get("hasGame"), "el juego arranca (window.__PP_GAME)")
        if not checks.get("hasGame"):
            await browser.close()
            print(f"RESULTADO: {ok} OK · {fails + 1} fallos")
            sys.exit(1)
        chk(checks.get("hasChampRoom"), "champRoom presente en el juego vivo")

        dk = checks.get("defaultKeys") or []
        chk(dk == sorted(["floor", "ceil", "left", "right", "back", "front"]),
            "las 6 claves del arte por defecto cargan " + str(dk))
        chk(checks.get("allMapped") is True,
            "las 6 caras de la cancha clásica tienen SU map "
            + str(checks.get("maps")))
        chk(checks.get("sharedSides") is True,
            "izquierda y derecha comparten IMAGEN (misma textura)")
        chk(checks.get("gridHidden") is True and checks.get("panelsHidden") is True
            and checks.get("stripsHidden") is True,
            "rejilla, paneles y tiras ocultos bajo el arte")

        p2p = checks.get("p2p") or {}
        chk(p2p.get("bo") == 3 and p2p.get("gp") == 1 and p2p.get("ga") == 0,
            "applySync P2P espeja la serie (bo/gp/ga) " + str(p2p))

        g1 = checks.get("g1") or {}
        chk(g1.get("state") == 'serve' and g1.get("sp") == 0 and g1.get("sa") == 0,
            "juego 1 acabado: marcador a cero y a servir "
            + str(g1.get("state")) + "/" + str(g1.get("sp")) + "-" + str(g1.get("sa")))
        chk(g1.get("gp") == 1 and g1.get("ga") == 0 and g1.get("gameNo") == 2,
            "serie 1-0 tras el primer juego (gameNo 2)")
        si = g1.get("serveIntent") or {}
        ge = si.get("gameEnd") or {}
        chk(si.get("type") == 'serve' and ge.get("winner") == 'player'
            and ge.get("gp") == 1 and ge.get("ga") == 0 and ge.get("bo") == 3,
            "intent 'serve' con gameEnd (el enfrentamiento SIGUE)")
        chk(g1.get("srv") == 'ai',
            "el saque del juego 2 abre el OTRO (ITTF), srv=" + str(g1.get("srv")))
        chk('serie 1-0' in str(g1.get("msg", "")),
            "mensaje de juego ganado con la serie " + str(g1.get("msg"))[:52])

        g2 = checks.get("g2") or {}
        oi = g2.get("overIntent") or {}
        chk(g2.get("state") == 'over' and g2.get("gp") == 2,
            "2 victorias = campeón del enfrentamiento (state over, 2-0)")
        chk(oi.get("type") == 'game-over' and oi.get("winner") == 'player',
            "intent 'game-over' SÓLO al acabar la serie")
        chk('ENFRENTAMIENTO PARA TI' in str(g2.get("msg", "")),
            "mensaje de enfrentamiento completo " + str(g2.get("msg"))[:56])

        g3 = checks.get("g3") or {}
        chk(g3.get("state") == 'over' and g3.get("over") is True
            and g3.get("gp") == 0 and 'HAS PERDIDO' in str(g3.get("msg", "")),
            "bestOf=1 (campeonatos): a un solo juego, mensajes clásicos")

        chk(checks.get("sbOk") is True,
            "marcador 3D repinta con la serie sin excepciones "
            + str(checks.get("sbErr") or ""))

        # captura de la cancha vestida: salir del hall, ocultar la portada 2D
        # (#overlay) y fotografiar el lienzo 3D con el arte por defecto
        try:
            await page.evaluate("""() => {
              const G = window.__PP_GAME;
              if (G && G.inHall) G.exitHall();
              const ov = document.getElementById('overlay');
              if (ov) ov.style.display = 'none';
            }""")
            await page.wait_for_timeout(1200)
            await page.screenshot(path=OUT)
            await page.evaluate("""() => {
              const ov = document.getElementById('overlay');
              if (ov) ov.style.display = '';
            }""")
        except Exception as e:
            print("  (captura fallida: " + str(e) + ")")
        await browser.close()

    if errors:
        for e in errors[:5]:
            print("  pageerror: " + e)
    chk(not errors, "0 pageerrors durante toda la sesión")

    # agujas estáticas del fichero SERVIDO
    served = urllib.request.urlopen(URL, timeout=30).read().decode("utf-8", "ignore")
    for needle, label in [
        ("assets/partido/izquierda.jpg", "arte lateral compartido (servido)"),
        ("assets/partido/' + f + '.jpg", "carga de las 4 caras restantes (servido)"),
        ("floor: 'suelo', ceil: 'techo', back: 'fondo', front: 'frente'",
         "mapa de ficheros de las caras del partido (servido)"),
        ("defaultTexs.right = tex", "izquierda.jpg compartida a DOS materiales"),
        ("ARTE POR DEFECTO DEL PARTIDO", "sello del arte por defecto"),
        ("game_won_you", "mensaje de juego ganado (ES)"),
        ("over_win_bo", "mensaje de enfrentamiento ganado (ES)"),
        ("ann_victory_bo", "megafonía del enfrentamiento (ES)"),
        ("sb_bo", "etiqueta MEJOR DE N del marcador"),
        ("bestOf = 3", "el partido libre opta al mejor de 3"),
        ("g.rules.bestOf = 1", "los duelos de campeonato siguen a juego único"),
        ("resetGame()", "reset de juego sin tocar la serie"),
        ("gp: r.gamesPlayer", "la serie viaja en el paquete P2P"),
        ("lastGame", "resultado del juego viaja al invitado (send-once)"),
    ]:
        chk(needle in served, label)

    # los 5 JPG servidos con 200 y peso REAL
    base = URL.rsplit("/", 1)[0]
    for f, peso in PESOS.items():
        try:
            raw = urllib.request.urlopen(base + "/assets/partido/" + f,
                                         timeout=30).read()
            chk(len(raw) == peso,
                f"assets/partido/{f} servido con peso real ({len(raw)} B)")
        except Exception as e:
            chk(False, f"assets/partido/{f} descargable ({e})")

    print(f"RESULTADO: {ok} OK · {fails} fallos")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    asyncio.run(main())
