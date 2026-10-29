#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r80_v3672 — CAPA BO · V3.6.71→3.6.86-SDK6, FASE 74 «EL RETO DIARIO EN
LA PUERTA».

Informe del dueño (r80): «en el submenu del multijugador has colocado mal
los botones que se están pisando con el marco superior del menú y los
idiomas. Ponerlo bien. Al pulsar sobre estos modos de juego multijugador
es cuando aparecen las opciones de sala y código. Otra cosa, La opción del
reto del dia debe estar especialmente destacada en la parte de abajo del
menú principal (y la retiramos del apartado de entrenamiento) Un botón con
la pala troquelada con el texto "Reto Diario!" y un pequeño resplandor en
su perímetro para llamar la atención… Las pruebas que se pongan que no
sean muy exigentes… por ejemplo que las zonas de bote… sean más permisivas
y grandes… digamos que el doble de anchas. Esto es para no desanimar al
jugador».

Lo implementado (r80) y SU verificación:
  · SUBMENÚ QUE RESPIRA (c12 drawMenuMulti): las dos tarjetas de modo BAJAN
    bajo la cabecera (y 216/326 — antes pisaban el título y las palas de
    idioma, y 42-172) y el panel de sala se reasienta en y=446.
  · SALA TRAS EL MODO: this._mjMode — sin elegir modo NO hay sala ni
    código (sólo el aviso «elige un modo»); al pulsar NORMAL aparecen
    CREAR SALA / INTRODUCIR CÓDIGO + chip «◀ MODOS». Cancelar/colgar
    devuelve a la selección de modos.
  · EL RETO DIARIO EN LA PUERTA (c12 _retoDiarioCard): botón estrella al
    pie del menú principal con la PALA TROQUELADA (silueta recortada,
    borde punteado de troquel, agujeros de perforación y oreja de
    colgante), texto literal «Reto Diario!» y RESPLANDOR en el perímetro
    (halo con sombra + dos aureolas; verde cuando ya está hecho hoy).
    El sub-estado vive en __PP_TRAIN.state.daily (modo del día incluido).
  · FUERA DEL ENTRENAMIENTO: el panel r76 del hub se RETIRA; quedan las
    pieles de asistencia (el escaparate de lo que la racha libera).
  · ARRANQUE DIRECTO: PP_TRAIN.startDaily(game) — cierra el menú y arranca
    el modo del día marcado como reto (st.daily=1); el caso 'trv3:daily'
    comparte camino.
  · EL RETO PERMISIVO (c13 zonaDims): PINTOR (drawQuad) y JUEZ
    (judgeAiBounce) comparten dimensiones — con el reto diario las zonas
    de bote son el DOBLE de anchas: bandas laterales 10→20 cm, franja de
    fondo 12→24 cm, doble bote junto a la red 0,51→1,02 m de vano, franja
    de fondo del saque 15→30 cm, filas del objetivo (deep abarca
    profunda+media · mid abarca media+corta) y centro prohibido a la
    mitad (0,30→0,15 m). En entrenamiento normal, TODO queda igual.

BLOQUES: (1) AGUJAS r80 en el servido. (2) CONTADORES exactos (incluido
el RETIRO del panel: «trv3:daily», X0 → ×0). (3) JUEGO REAL headless:
geometría del submenú y del HUB medida por rects, aparición de la sala al
pulsar NORMAL, startDaily real sobre la instancia viva, zonaDims dobles y
juez comparativo (el mismo bote falla en normal y vale en el reto) con
0 pageerrors.
Uso: python3 qa_r80_v3672.py [URL]
"""
import asyncio
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # — el submenú que respira —
    ("tarjetas bajo la cabecera (y 216)", "this._modeCard(rects, 'mjnorm', 40, 216, 944, 96"),
    ("DUELOS bajo NORMAL (y 326, tarjeta r84)", "this._modeCard(rects, 'mjduel', 40, 326, 944, 96"),
    # r88 · re-anclaje honesto: r87 reasentó el panel bajo la tarjeta de
    # invitación (y 446 → 466 + hInv); la aguja quedó obsoleta desde
    # entonces (BO no estuvo en la lista de re-anclajes de r87).
    ("panel de sala reasentado bajo las invitaciones (y 466 + hInv)", "const yPanel = 466 + hInv;"),
    ("estado de modo elegido (_mjMode)", "this._mjMode = null"),
    ("sin modo no hay sala", "} else if (!this._mjMode) {"),
    ("aviso «elige un modo»", "mj_pick: 'Elige un modo de juego para continuar'"),
    ("chip volver a MODOS", "mj_sel_back: '◀  MODOS'"),
    ("cancelar sala devuelve a modos", "vuelta a la selección de modos"),
    # — el reto diario en la puerta —
    ("tarjeta estrella (def)", "_retoDiarioCard(rects, x, y, w, h)"),
    ("tarjeta estrella en el HUB", "this._retoDiarioCard(rects, 40, y, 944, 118)"),
    ("texto literal del dueño (ES)", "daily_btn_t: 'Reto Diario!'"),
    ("texto del dueño (EN)", "daily_btn_t: 'Daily Challenge!'"),
    ("pala troquelada: borde punteado", "setLineDash([5.5, 5])"),
    ("agujeros de troquel", "agujeros de troquel"),
    ("resplandor del perímetro", "c.shadowColor = hecho ? 'rgba(104,211,145,0.85)' : 'rgba(255,210,87,0.9)'"),
    ("estado del reto en el banner", "Duelo de hoy: {m} · racha: {n}"),
    ("promesa de retorno (zonas dobles)", "zonas el doble de amplias · nuevo duelo cada medianoche"),
    ("caso retoDiario en el menú", "case 'retoDiario'"),
    ("API startDaily pública", "startDaily: (g) => {"),
    ("modo del día en state.daily", "modoName: t(MODES[_pD.mode].nk)"),
    # — el reto permisivo (zonas dobles compartidas pintor/juez) —
    ("dims compartidas (def)", "function zonaDims() {"),
    ("dims expuestas a la QA", "zonaDims,"),
    ("bandas laterales dobles", "t1bBanda: diario ? 0.20 : 0.10"),
    ("franja de fondo doble", "t1bFondo: diario ? 0.24 : 0.12"),
    ("doble bote: vano doble", "t4aProf: diario ? 1.07 : 0.56"),
    ("franja del saque doble", "t4bFondo: diario ? 0.30 : 0.15"),
    ("centro prohibido a la mitad", "t1aCentro: diario ? 0.075 : 0.15"),
    ("filas del objetivo crecen", "t1aDeepF: diario ? 0.25 : 0.5"),
    ("el PINTOR usa las dims", "const ZD = zonaDims();"),
    ("el JUEZ usa las dims", "const ZJ = zonaDims();"),
    ("sesión marcada como reto", "st.daily = (opts && opts.daily) ? 1 : 0;"),
    ("startMode con opciones", "function startMode(game, id, opts)"),
    ("teardown apaga el reto", "st.daily = 0;"),
    # — la r79 queda intacta —
    ("tarjeta duelo con gradiente morado propio (r84)", "'#3b3550', '#241f33', PP_ICONS.duelo)"),
    ("versión sellada de nacimiento", "const VERSION = '3.6.86-SDK6';"),
]

CONTADORES = [
    ("_retoDiarioCard (def + llamada + 2 comentarios)", "_retoDiarioCard", 4),
    ("caso retoDiario (uno solo)", "case 'retoDiario'", 1),
    ("caso mjnorm (uno solo)", "case 'mjnorm'", 1),
    ("caso mjsel (uno solo)", "case 'mjsel'", 1),
    ("startDaily (def + usos)", "startDaily", 4),
    ("zonaDims (todas las apariciones)", "zonaDims", 17),
    ("zonaDims() (def + 8 usos + comentarios)", "zonaDims()", 13),
    # r88 · c09c_red_social.js (r87) añade 1 aparición: 12 → 13
    ("_mjMode (todas las apariciones, +md r84 y c09c r87)", "_mjMode", 13),
    ("mj_pick definido ES+EN", "mj_pick:", 2),
    ("daily_btn_t definido ES+EN", "daily_btn_t:", 2),
    ("botón diario del hub RETIRADO (×0)", '"trv3:daily", X0', 0),
    ("versión única", "const VERSION = '3.6.86-SDK6'", 1),
    ("candado de Duelos retirado (r84)", "candado(c, x + 134", 0),
]

JS_BANCO = """async () => {
  const G = window.__PP_GAME;
  const TR = window.__PP_TRAIN;
  if (!G || !TR) return { error: 'sin __PP_GAME o __PP_TRAIN' };
  const out = { checks: [] };
  const chk = (cond, label) => out.checks.push([!!cond, label]);

  // 1 · superficie r80
  chk(typeof G._retoDiarioCard === 'function', 'c12: _retoDiarioCard existe');
  chk(G._mjMode === null, 'c12: _mjMode nace null (sin modo no hay sala)');
  chk(typeof TR.startDaily === 'function', 'c13: API startDaily pública');
  chk(typeof TR.__test.zonaDims === 'function', 'c13: zonaDims expuesto para QA');

  // 2 · submenú: cabecera intacta, tarjetas bajo ella, sala OCULTA
  G.menuPage = 'multi'; G._mjMode = null; G.drawMenu();
  let rs = G.menuRects || [];
  const byId = (id) => rs.find((r) => r.id === id);
  const mj = byId('mjnorm'), du = byId('mjduel');
  const les = byId('lang:es'), len2 = byId('lang:en');
  chk(!!mj && !!du, 'submenú: tarjetas NORMAL + DUELOS LOCOS presentes');
  chk(!!les && !!len2, 'submenú: palas de idioma presentes');
  chk(!!mj && mj.y >= 210, 'submenú: NORMAL bajo la cabecera (y=' + (mj ? mj.y : -1) + ' ≥ 210)');
  chk(!!du && !!mj && du.y >= mj.y + mj.h, 'submenú: DUELOS debajo de NORMAL sin solape');
  chk(!!les && !!mj && (les.y + les.h) <= mj.y + 6 && (len2.y + len2.h) <= mj.y + 6,
      'submenú: las tarjetas NO pisan los idiomas');
  chk(!byId('net:host') && !byId('net:join'), 'submenú: SIN sala ni código antes de elegir modo');
  chk(!byId('mjsel'), 'submenú: sin chip MODOS mientras no hay sala');

  // 3 · al pulsar NORMAL aparecen sala y código
  G._mjMode = 'normal'; G.drawMenu();
  rs = G.menuRects || [];
  const host = rs.find((r) => r.id === 'net:host');
  chk(!!host, 'submenú: CREAR SALA aparece tras elegir NORMAL');
  chk(!!rs.find((r) => r.id === 'net:join'), 'submenú: INTRODUCIR CÓDIGO aparece tras elegir NORMAL');
  chk(!!rs.find((r) => r.id === 'mjsel'), 'submenú: chip «◀ MODOS» presente con la sala abierta');
  chk(!!host && host.y > 400 && (host.y + host.h) < 1370,
      'submenú: la sala vive bajo las tarjetas y sin pisar el pie (y=' + (host ? host.y : -1) + ')');
  const mj2 = rs.find((r) => r.id === 'mjnorm');
  chk(!!mj2 && mj2.y >= 210, 'submenú: las tarjetas SIGUEN bajo la cabecera con la sala abierta');

  // 4 · HUB: RETO DIARIO al pie, nada fuera del lienzo
  G.menuPage = 'main'; G.drawMenu();
  rs = G.menuRects || [];
  const rd = rs.find((r) => r.id === 'retoDiario');
  const opts = rs.find((r) => r.id === 'page:opts');
  const closeB = rs.find((r) => r.id === 'close');
  chk(!!rd, 'HUB: botón RETO DIARIO presente');
  chk(!!opts && !!rd && rd.y > opts.y, 'HUB: el reto vive al pie (debajo de AJUSTES)');
  chk(!!closeB && !!rd && closeB.y > rd.y, 'HUB: cierre por debajo del reto');
  chk(!!rd && (rd.y + rd.h) <= 1536, 'HUB: el reto cabe en el lienzo (sin desbordar)');
  let fuera = 0;
  for (const r of rs) if (r.y + r.h > 1536 || r.y < 0) fuera++;
  chk(fuera === 0, 'HUB: ningún rect sale del lienzo (' + rs.length + ' rects)');

  // 5 · el reto arranca el duelo de hoy con zonas dobles
  const planHoy = TR.__test.dailyPlan(TR.__test.dayKey()).mode;
  TR.startDaily(G);
  chk(G.trainV3 === planHoy, 'reto: startDaily arranca el modo de hoy (' + planHoy + ')');
  chk(TR.__debug.st.daily === 1, 'reto: sesión marcada como RETO DIARIO');
  const zd = TR.__test.zonaDims();
  chk(zd.diario === 1 && zd.t1bBanda === 0.20 && zd.t1bFondo === 0.24
      && zd.t4aProf === 1.07 && zd.t4bFondo === 0.30 && zd.t1aCentro === 0.075
      && zd.t1aDeepF === 0.25 && zd.t1aMidF === 0,
      'reto: zonas el DOBLE de anchas (bandas 0,20 · fondo 0,24 · bote 1,07 · saque 0,30 · centro 0,075)');
  const stHoy = TR.state.daily;
  chk(!!stHoy && stHoy.modo === planHoy && typeof stHoy.modoName === 'string' && stHoy.modoName.length > 0,
      'reto: el banner sabe el modo del día («' + (stHoy ? stHoy.modoName : '') + '»)');

  // 6 · el juez comparativo: el MISMO bote falla en normal y vale en el reto
  const C = -1.6, HL = 1.37;                     // DIMS de la casa (c02)
  TR.startMode(G, 't1a', {});                    // entrenamiento normal
  const zdNorm = TR.__test.zonaDims();           // dims de siempre (sesión normal viva)
  TR.__debug.st.target = { z: 'mid', x: -1 };
  TR.__test.judgeAiBounce({ x: -0.5, z: C - HL * 0.15 });   // bote corto (fila short)
  const falloNormal = TR.__debug.st.streak === 0;
  TR.startMode(G, 't1a', { daily: 1 });          // reto diario
  TR.__debug.st.target = { z: 'mid', x: -1 };
  TR.__test.judgeAiBounce({ x: -0.5, z: C - HL * 0.15 });
  const valeReto = TR.__debug.st.streak === 1;
  chk(falloNormal, 'juez: en entrenamiento normal el bote corto FALLA (fronteras de siempre)');
  chk(valeReto, 'juez: en el RETO DIARIO el mismo bote VALE (zona doble)');
  chk(zdNorm.diario === 0 && zdNorm.t1aCentro === 0.15 && zdNorm.t1bBanda === 0.10
      && zdNorm.t4aProf === 0.56 && zdNorm.t4bFondo === 0.15,
      'juez: sin reto las dims son EXACTAMENTE las de siempre');
  // centro prohibido del reto: la mitad (0,075) — un bote a 0,10 vale en el reto
  TR.__debug.st.target = { z: 'mid', x: 1 };
  TR.__test.judgeAiBounce({ x: 0.10, z: C - HL * 0.4 });
  chk(TR.__debug.st.streak === 2, 'juez: en el reto el centro prohibido es el doble de estrecho (|x|=0,10 vale)');
  TR.stopMode(G);

  // 7 · entrenamiento: panel diario retirado, pieles vivas
  G.menuPage = 'train'; G.drawMenu();
  rs = G.menuRects || [];
  chk(!rs.find((r) => r.id === 'trv3:daily'), 'entrenamiento: el panel del reto YA NO está (se mudó a la puerta)');
  chk(!!rs.find((r) => r.id && String(r.id).indexOf('trv3:skin:') === 0),
      'entrenamiento: pieles de asistencia vivas (escaparate de la racha)');
  return out;
}"""


async def main():
    src = ""
    try:
        import urllib.request
        with urllib.request.urlopen(URL, timeout=15) as r:
            src = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"✗ FALLO: no se pudo leer {URL}: {e}")
        sys.exit(1)

    print("— BLOQUE 1 · AGUJAS r80 en el servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES exactos —")
    import re
    for label, pat, esperado in CONTADORES:
        n = len(re.findall(re.escape(pat), src))
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")

    print("— BLOQUE 3 · JUEGO REAL headless (submenú, HUB, reto y juez) —")
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            juego = False
            for _ in range(90):
                juego = await page.evaluate("() => !!window.__PP_GAME")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_GAME")

            res = await page.evaluate(JS_BANCO, [])
            if res.get("error"):
                chk(False, "JS_BANCO: " + res["error"])
            else:
                for cond, label in res.get("checks", []):
                    chk(cond, "en página: " + label)

            if page_errors:
                for e in page_errors:
                    print("  ✗ pageerror: " + e[:200])
            chk(len(page_errors) == 0, "0 pageerrors en toda la sesión")
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} FALLOS (qa_r80_v3672 · CAPA BO)")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
