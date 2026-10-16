#!/usr/bin/env python3
"""QA v3.0.9-HALL1 · HALL DEL ANFITRIÓN + saque por dificultad + cilindro fuera:
  1) la página carga sin pageerrors y badge V3.0.9-HALL1
  2) SERVE_ASSIST_TIERS expuestos y serveTier() responde a la dificultad
     (easy > medium > hard en lerp/reach/vy) + persistencia ppxr_dif
  3) HALL: enterHall() enciende la estancia (rig en el hall, roomGroup fuera),
     drawHall() monta la fila de campeonatos y los lienzos; exitHall() restaura
  4) el cilindro de la cinta de agarre ya NO se crea (chequeo de código)
Capturas: download/qa_hall1_portada.png + qa_hall1_hall.png
"""
import asyncio, json
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT_PORTADA = "/home/z/my-project/download/qa_hall1_portada.png"
OUT_HALL = "/home/z/my-project/download/qa_hall1_hall.png"

# el cilindro retirado: geometría exacta de la antigua cinta de agarre
CILINDRO = "CylinderGeometry(0.0128, 0.0138, 0.048, 14)"

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
          out.badge = (document.querySelector('#verBadge') || {}).textContent || '';
          out.version = window.__PP_VERSION || null;
          out.hasGame = !!G;
          out.tiers = window.__ppDebug ? window.__ppDebug.serveTiers || null : null;
          // 2) tier sigue a la dificultad + persistencia
          G.setDifficulty('easy');
          out.tierEasy = JSON.parse(JSON.stringify(G.serveTier()));
          G.setDifficulty('hard');
          out.tierHard = JSON.parse(JSON.stringify(G.serveTier()));
          G.setDifficulty('medium');
          out.tierMedium = JSON.parse(JSON.stringify(G.serveTier()));
          out.difPersist = localStorage.getItem('ppxr_dif');
          // 3) HALL
          G.enterHall();
          out.hallEnter = {
            inHall: G.inHall,
            hallVisible: G.hallGroup ? G.hallGroup.visible : null,
            roomVisible: G.roomGroup ? G.roomGroup.visible : null,
            rigZ: G.rig ? +G.rig.position.z.toFixed(2) : null,
            msg: G.rules ? G.rules.message : null,
          };
          out.hallCanvas = (() => {
            const ud = G.hallGroup && G.hallGroup.userData.hall;
            if (!ud) return null;
            return { sign: !!ud.signTex, achs: !!ud.achsTex, circ: !!ud.circTex,
                     champSlots: ud.champRow.userData.slots.length,
                     n: ud.champRow.userData.n };
          })();
          await new Promise(r => setTimeout(r, 1200));  // insignias en vuelo
          out.hallExit0 = (() => { G.exitHall();
            return { inHall: G.inHall, hallVisible: G.hallGroup.visible,
                     roomVisible: G.roomGroup.visible, rigZ: +G.rig.position.z.toFixed(2) }; })();
          // volver a entrar para la captura
          G.enterHall();
          return out;
        }""")
        for k, v in checks.items():
            print(f"{k:12s}: {json.dumps(v, ensure_ascii=False)[:220]}")

        await page.screenshot(path=OUT_PORTADA)
        await page.wait_for_timeout(1500)
        await page.screenshot(path=OUT_HALL)
        await browser.close()

    # 4) cilindro retirado (chequeo estático del fichero servido)
    import urllib.request
    served = urllib.request.urlopen(URL, timeout=30).read().decode("utf-8", "ignore")
    cilindro_fuera = CILINDRO not in served
    print(f"{'cilindro':12s}: {'FUERA ✓' if cilindro_fuera else 'AÚN PRESENTE ✗'}")

    t = checks["tiers"]
    ok_tiers = (t and t["easy"]["lerp1"] == 0.62 and t["hard"]["lerp1"] == 0.30
                and checks["tierEasy"]["reach"] == 0.13
                and checks["tierHard"]["reach"] == 0.06
                and checks["tierMedium"]["lerp2"] == 0.75
                and checks["tierEasy"]["vy"] > checks["tierMedium"]["vy"] > checks["tierHard"]["vy"]
                and checks["difPersist"] == "medium")
    h = checks["hallEnter"]
    he = checks["hallExit0"]
    ok_hall = (h and h["inHall"] and h["hallVisible"] and h["roomVisible"] is False
               and h["rigZ"] == -16.2 and checks["hallCanvas"]
               and checks["hallCanvas"]["champSlots"] >= 1
               and he and not he["inHall"] and not he["hallVisible"]
               and he["roomVisible"] and he["rigZ"] == 0.0)
    ok = ("3.0.9-HALL1" in checks["badge"] and checks["version"] == "3.0.9-HALL1"
          and checks["hasGame"] and ok_tiers and ok_hall and cilindro_fuera
          and errors == [])
    print("pageerrors  :", errors or "ninguno")
    print("CAPTURAS    :", OUT_PORTADA, "+", OUT_HALL)
    print("RESULTADO   :", "OK" if ok else "REVISAR")

asyncio.run(main())
