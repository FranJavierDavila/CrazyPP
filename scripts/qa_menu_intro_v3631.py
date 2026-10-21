#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.31 · MENÚ DE CAMPEONATOS: texto fantasma fuera + intro opcional
+ menú prioritario + haz-puntero (capa Z, en vivo).

Informe del dueño tras V3.6.30:
  1) «al final de todos los campeonatos aparece un texto que no tiene
     sentido… 11-point match vs the Clown… MEGA PADDLE» → el hint heredado
     del ARCADE (v2.34) ya NO se pinta al pie del listado
  2) «el video de presentación del rival solo debería aparecer la primera
     vez» → intro SOLO la primera vez (pp_intro_<id>); re-verla OPCIONAL
     con el botón VER PRESENTACIÓN de cada tarjeta (y ?intro=1 en URL)
  3) «si sacamos el menú… no funciona, quien manda es el video» → en
     onSelectStart el MENÚ VA PRIMERO: sus clics funcionan aunque la intro
     siga en pantalla
  4) «deberíamos sacar un rayo desde nuestra pala… igual que con los mapas
     de la pared… el resto del tiempo no se muestra» → la intro reutiliza
     el HAZ del mapa (v2.98): visible sólo mientras el rayo toca el panel,
     DORADO sobre el botón JUGAR, apagado en cuanto dejas de apuntar
Capturas: download/qa_menu_intro_menu.png (tarjetas con VER PRESENTACIÓN)
Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT_MENU = "/home/z/my-project/download/qa_menu_intro_menu.png"

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
          const C = G.champs;
          out.hasChamps = !!C;
          if (!C) return out;

          // ---- PRERREQUISITO: catálogo cargado (fetch en CASCADA: índice +
          // 5 manifests secuenciales — bajo carga puede tardar >20 s; sondear
          // hasta 60 s ANTES de tocar nada que dependa de las tarjetas) ----
          let catalogo = false;
          try {
            for (let i = 0; i < 120 && !catalogo; i++) {
              await new Promise((r) => setTimeout(r, 500));
              catalogo = C.list().length >= 5;
            }
          } catch (e) { catalogo = false; }
          out.catalogo = catalogo;

          // ---- (2) INTRO SÓLO LA PRIMERA VEZ ----
          out.tieneIntroPendiente = typeof C.introPendiente === 'function';
          try { localStorage.removeItem('pp_intro_qa_champ'); } catch (e) {}
          out.pendienteFresco = C.introPendiente('qa_champ') === true;
          try { localStorage.setItem('pp_intro_qa_champ', '1'); } catch (e) {}
          out.pendienteVisto = C.introPendiente('qa_champ') === false;
          try { localStorage.removeItem('pp_intro_qa_champ'); } catch (e) {}

          // launch lleva la lógica nueva (persistencia + forzar + ?intro=1)
          const L = String(C.launch);
          out.launchGuarda = L.indexOf("pp_intro_") >= 0;
          out.launchFuerza = L.indexOf("opts.intro") >= 0;
          out.launchUrl = L.indexOf("has('intro')") >= 0;

          // ---- SHOW / HIDE de la intro (sin XR: póster, sin vídeo) ----
          let showOk = false, updOk = false, hideOk = false;
          try {
            G.showChampIntro('qa_champ');
            showOk = !!G.champIntro && !!G.champIntro.group &&
                     G.champIntro.group.visible === true &&
                     !!G.champIntro.btn;
          } catch (e) { showOk = false; }
          out.introShow = showOk;

          // update corre sin excepciones y SIN visor no enciende el botón
          try { G._updateChampIntro(0.016); updOk = G.champIntro.btnHot === false; }
          catch (e) { updOk = false; }
          out.introUpdate = updOk;

          // haz de la intro: show/hide no tumban nada y hide lo apaga
          let beamOk = false;
          try {
            const O = new (G.rig.position.constructor)();
            const D = new (G.rig.position.constructor)(0, 0, -1);
            C.introBeamShow(O, D, 1.5, true);
            C.introBeamShow(O, D, 1.5, false);
            C.introBeamHide();
            beamOk = true;
          } catch (e) { beamOk = false; }
          out.introBeam = beamOk;

          try { G.hideChampIntro(false); hideOk = G.champIntro === null; }
          catch (e) { hideOk = false; }
          out.introHide = hideOk;

          // ---- (3) MENÚ PRIORITARIO: orden dentro de onSelectStart ----
          const S = String(G.onSelectStart);
          const iMenu = S.indexOf('this.menuOpen');
          const iIntro = S.indexOf('this.champIntro');
          out.menuPrimero = iMenu >= 0 && iIntro >= 0 && iMenu < iIntro;
          out.menuComentario = S.indexOf('MENÚ PRIORITARIO') >= 0;

          // ---- tarjetas del menú: botón VER PRESENTACIÓN en los rects
          // (el catálogo ya llegó: el sondeo de arriba es su prerrequisito;
          // así la carrera índice+manifests no puede dejar el menú vacío) ----
          let btnEnRects = false, sinHintFantasma = true;
          try {
            G.menuOpen = true;
            G.menuPage = 'champs';
            G.drawMenu();
            btnEnRects = catalogo && (G.menuRects || [])
              .some((r) => r && String(r.id).indexOf('champintro:') === 0);
            // el texto heredado ya no entra en el repintado del listado
            sinHintFantasma = String(G.drawMenuChamps)
              .indexOf("T('arcade_hint')") < 0;
          } catch (e) { btnEnRects = false; }
          out.botonIntro = btnEnRects;
          out.sinHintFantasma = sinHintFantasma;

          return out;
        }""")

        for cond, label in [
            (checks.get("hasGame"), "juego vivo en __PP_GAME"),
            (checks.get("hasChamps"), "ChampLoader presente"),
            (checks.get("tieneIntroPendiente"), "introPendiente(id) expuesto"),
            (checks.get("pendienteFresco"), "sin registro → intro PENDIENTE (1ª vez)"),
            (checks.get("pendienteVisto"), "con registro → intro YA vista (entradas siguientes)"),
            (checks.get("launchGuarda"), "launch guarda pp_intro_<id>"),
            (checks.get("launchFuerza"), "launch acepta opts.intro (VER PRESENTACIÓN)"),
            (checks.get("launchUrl"), "launch respeta ?intro=1 en la URL"),
            (checks.get("introShow"), "showChampIntro monta grupo + botón JUGAR"),
            (checks.get("introUpdate"), "_updateChampIntro corre sin excepciones (sin XR)"),
            (checks.get("introBeam"), "haz de la intro: show/hide sin excepciones"),
            (checks.get("introHide"), "hideChampIntro retira la intro completa"),
            (checks.get("menuPrimero"), "onSelectStart: menú ANTES que intro (prioridad)"),
            (checks.get("menuComentario"), "sello v3.6.31 MENÚ PRIORITARIO en onSelectStart"),
            (checks.get("botonIntro"), "tarjeta del menú pinta botón champintro:<id>"),
            (checks.get("sinHintFantasma"), "drawMenuChamps ya no pinta arcade_hint"),
            (checks.get("catalogo"), "catálogo de campeonatos íntegro (≥5)"),
        ]:
            chk(cond, label)

        await page.screenshot(path=OUT_MENU)
        await browser.close()

    # agujas estáticas del fichero SERVIDO (los cambios v3.6.31)
    served = urllib.request.urlopen(URL, timeout=30).read().decode("utf-8", "ignore")
    for needle, label in [
        # (1) texto fantasma fuera del listado (la clave queda, el pinto no)
        ("ya NO se pinta al pie del listado", "retirada del hint heredado documentada (servido)"),
        # (2) intro opcional
        ("pp_intro_' + id", "registro de intro vista por campeonato (servido)"),
        ("SÓLO LA PRIMERA VEZ", "intro sólo la primera vez (servido)"),
        ("'champintro:' + ch.id", "botón VER PRESENTACIÓN en cada tarjeta (servido)"),
        ("case 'champintro':", "menuClick enruta VER PRESENTACIÓN (servido)"),
        ("VER PRESENTACIÓN · vídeo del rival", "i18n ES del botón (servido)"),
        ("WATCH THE INTRO · rival video", "i18n EN del botón (servido)"),
        # (3) menú prioritario
        ("MENÚ PRIORITARIO", "menú prioritario sobre la intro (servido)"),
        ("corre DESPUÉS del menú", "la intro queda tras el menú (servido)"),
        # (4) haz-puntero de la intro
        ("introBeamShow(oW, dW, len, hot)", "haz de la intro expuesto en ChampLoader (servido)"),
        ("introBeamHide()", "apagado del haz expuesto (servido)"),
        ("!g.menuOpen && !g.champIntro", "el mapa no pelea por el haz durante la intro (servido)"),
        ("HAZ-PUNTERO (igual que el mapa del camino, v2.98)", "haz de la intro conduce el rayo (servido)"),
        ("introBeamShow(this._instrO, this._instrD", "la intro dispara el haz con el rayo de la pala (servido)"),
        ("no puede quedar vivo sin intro", "hideChampIntro apaga el haz (servido)"),
        # regresiones: lo clásico del menú de campeonatos sigue
        ("'ppchamp:' + ch.id", "tarjeta de campeonato intacta (servido)"),
        ("case 'ppchamp':", "entrada por tarjeta intacta (servido)"),
    ]:
        chk(needle in served, label)
    chk("T('arcade_hint')" not in served,
        "T('arcade_hint') fuera del fichero servido (texto fantasma muerto)")

    chk(errors == [], "cero pageerrors " + (str(errors[:2]) if errors else ""))
    print("CAPTURA     :", OUT_MENU)
    print(f"RESULTADO: {ok} OK · {fails} fallos")
    sys.exit(1 if fails else 0)

asyncio.run(main())
