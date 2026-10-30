#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r75_v3667 — CAPA BJ · V3.6.87-SDK6, FASE 69 «TODO ENCAJA».

Informe del dueño tras probar V3.6.66 en el Quest:
  «En la pantalla del tutorial de Modos, algunos textos quedan fuera del
   contenedor; es preciso recolocarlos de otra forma para que se lean bien
   y quede todo bien encajado».

Diagnóstico MEDIDO EN VIVO (r75): en la pizarra LOS MODOS (paso 8) la línea
de detalle ámbar (extra) de las tarjetas BAJAS de 300 px — RANKING MUNDIAL
y ENTRENAR — agotaba el mínimo de fitFont (10 px) y aún así medía 353 px y
324 px frente a los 214 px disponibles (300 − 86 de icono+margen): el texto
SALÍA de la tarjeta y se comía la vecina (igual en EN: 333/341 px).

El arreglo (r75) y SU verificación:
  · cardWrap NUEVA: reduce la fuente (fitFont) y si aún no cabe ENVUELVE
    por palabras en ≤maxLines líneas que miden TODAS ≤maxW; red de
    seguridad con elipsis al mínimo. Nada sale del marco, con cualquier
    fuente del visor, en ES y en EN.
  · modeCard REDISEÑADA: título/sub/extra pasan por cardWrap (≤1/1/2
    líneas) y las anclas bajan en las tarjetas bajas (h<88) para que la
    extra de 2 líneas respire sin pisar al subtítulo.
  · wrap2 BLINDADA: cada mitad de la división se re-ajusta a maxW (antes
    se pintaban al ancho que dieran). Hoy el dibujado es idéntico
    (mitades 252/261 ≤ 312) — es armadura para cadenas futuras.
  · VERIFICACIÓN EN VIVO: las funciones SERVIDAS (rr, fitFont, line, pill,
    wrap2, cardWrap, modeCard) se extraen del propio game.html y se pintan
    sobre un canvas REAL con las cadenas reales de las 6 tarjetas en ES y
    EN + la caja PODERES: cada línea medida con measureText debe caber en
    su tarjeta (horizontal) y sus glifos dentro del marco (vertical,
    actualBoundingBox). Además se guarda una CAPTURA de la pizarra
    reconstruida (download/pizarra_modos_r75_ES.png / _EN.png).
BLOQUES: (1) AGUJAS r75 en el game.html servido. (2) CONTADORES (ramas
viejas AUSENTES) + ORDEN de fuente. (3) JUEGO REAL headless: academia viva,
matriz de contención con las funciones servidas, capturas, 0 pageerrors.
Uso: python3 scripts/qa_r75_v3667.py [URL]
"""
import asyncio
import base64
import os
import re
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
RAIZ = "/home/z/my-project"
DIR_CAPS = os.path.join(RAIZ, "download")
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # --- r75 · CARDWRAP: envoltura garantizada ---
    ("cardWrap definida (fitFont + envoltura ≤maxLines + elipsis)",
     "function cardWrap(c, txt, size, weight, minS, maxW, maxLines) {"),
    ("cardWrap: red de seguridad con elipsis",
     "// red de seguridad: elipsis al mínimo (jamás fuera del contenedor)"),
    ("cardWrap: preferencia 1 línea legible (≥11 px)",
     "const suelo1 = Math.max(minS, 11);"),
    # --- r75 · MODECARD: todo el texto por cardWrap ---
    ("modeCard mantiene la firma r74 (extra)",
     "function modeCard(c, x, y, w, h, col0, ini, title, sub, extra) {"),
    ("modeCard: título por cardWrap (1 línea)",
     "const tt = cardWrap(c, title, 21, '800', 14, tw, 1);"),
    ("modeCard: subtítulo por cardWrap (1 línea)",
     "const ts = cardWrap(c, sub, 15, '500', 10, tw, 1);"),
    ("modeCard: extra por cardWrap (hasta 2 líneas)",
     "const te = extra ? cardWrap(c, extra, 13, '600', 9, tw, 2) : null;"),
    ("modeCard: extra de 2 líneas (rama)",
     "if (te.lines.length === 2) {"),
    ("modeCard: fila alta/baja según h",
     "const filaAlta = h >= 88;"),
    ("modeCard: anclas compactas/altas (título)",
     "c.fillText(tt.lines[0], x + 68, y + (compacta ? 24 : 27));"),
    ("modeCard: anclas compactas/altas (subtítulo)",
     "c.fillText(ts.lines[0], x + 68, y + (compacta ? 42 : 50));"),
    ("modeCard: extra 2 líneas L1 a y+h−25",
     "c.fillText(te.lines[0], x + 68, y + h - 25);"),
    ("modeCard: extra 2 líneas L2 a y+h−12",
     "c.fillText(te.lines[1], x + 68, y + h - 12);"),
    ("modeCard: extra 1 línea se queda en y+h−14",
     "c.fillText(te.lines[0], x + 68, y + h - 14);"),
    # --- r75 · WRAP2 blindado ---
    ("wrap2: mitad 1 re-ajustada a maxW",
     "const s1 = fitFont(c, l1, size, '600', maxW, 9);"),
    ("wrap2: mitad 2 re-ajustada a maxW",
     "const s2 = fitFont(c, l2, size, '600', maxW, 9);"),
    ("wrap2: las mitades se pintan con SU tamaño y SU maxW",
     "line(c, l2, y + (lh || 14), s2, col, undefined, x, maxW);"),
    # --- intacto r67/r72/r74 (el pintor de LOS MODOS) ---
    ("pintor: título LOS MODOS a 262 (r72 intacto)",
     "line(c, T('tut_mods_t'), 262, 34, '#ffd257');"),
    ("pintor: tarjeta PARTIDO con su extra",
     "T('hub_match'), T('tut_mod_p'), T('tut_s6_m1')"),
    ("pintor: tarjeta ENTRENAR con su extra",
     "modeCard(c, 506, 496, 300, 80, 'rgba(28,126,214,0.8)', 'T', T('sec_train'), T('tut_mod_t'), T('tut_s7_m3'));"),
    ("pintor: tarjeta RANKING con su extra",
     "modeCard(c, 190, 496, 300, 80, 'rgba(12,166,120,0.8)', 'R', T('sec_rank'), T('tut_mod_r'), T('tut_s7_m2'));"),
    ("pintor: caja PODERES con wrap2 (r72 intacto)",
     "wrap2(c, T('tut_pow_t'), 536, 14, '#ffe08a', 312, 11, 996);"),
    ("pintor: rejilla llama a modeCard con las 4 altas",
     "modeCard(c, x, y, W, H, col, ini, ti, su, ex);"),
    ("voz: VOCES_PASO[7] con los 6 átomos (r74 intacto)",
     "['tutv8a', 'tutv8b', 'tutv8c', 'tutv9a', 'tutv9c', 'tutv9b'],   // 7 modos (r74: con calma · r78: campeonatos = superpoderes)"),
]

CONTADORES = [
    ("dibujo directo de la extra AUSENTE (fitFont+fillText a pelo)",
     ["fitFont(c, extra, 13, '600', w - 86, 10);"], 0),
    ("anclas viejas de título/sub AUSENTES",
     ["c.fillText(title, x + 68, y + (extra ? 27 : 32));",
      "c.fillText(sub, x + 68, y + (extra ? 50 : 62));"], 0),
    ("cardWrap llamada ×3 en modeCard (tt/ts/te)",
     ["const tt = cardWrap(", "const ts = cardWrap(",
      "extra ? cardWrap(c, extra"], 3),
    ("cardWrap definida ×1",
     ["function cardWrap(c, txt, size, weight, minS, maxW, maxLines) {"], 1),
    ("rama de 2 líneas ×1 y rama de 1 línea ×1",
     ["if (te.lines.length === 2) {",
      "c.fillText(te.lines[0], x + 68, y + h - 14);"], 2),
    ("wrap2 con re-ajuste de mitades ×2 (s1/s2)",
     ["const s1 = fitFont(c, l1, size, '600', maxW, 9);",
      "const s2 = fitFont(c, l2, size, '600', maxW, 9);"], 2),
    ("las 6 tarjetas pasan SU extra (tut_s6_m1..3 / tut_s7_m1..3)",
     ["T('tut_s6_m1')", "T('tut_s6_m2')", "T('tut_s6_m3')",
      "T('tut_s7_m1')", "T('tut_s7_m2')", "T('tut_s7_m3')"], 6),
]

ORDEN_FUENTE = [
    ("function cardWrap(c, txt, size, weight, minS, maxW, maxLines) {",
     "function modeCard(c, x, y, w, h, col0, ini, title, sub, extra) {",
     "cardWrap se define ANTES de modeCard (lectura limpia)"),
]

# --- las cadenas REALES de las 6 tarjetas (ES y EN, dict c00) -------------
TARJETAS = [
    ("PARTIDO", 480, 88, "PARTIDO", "Contra la CPU al mejor de 3",
     "PARTIDO · contra la CPU (3 niveles). Al mejor de 3 sets.",
     "MATCH", "vs the CPU · best of 3",
     "MATCH · against the CPU (3 levels). Best of 3 sets."),
    ("SUPERVIVENCIA", 480, 88, "SUPERVIVENCIA", "Aguanta el máximo de rallyes",
     "SUPERVIVENCIA · aguanta el máximo de rallyes seguidos.",
     "SURVIVAL", "Survive endless rallies",
     "SURVIVAL · survive as many consecutive rallies as you can."),
    ("MULTIJUGADOR", 480, 88, "MULTIJUGADOR", "Online con un código de 5 letras",
     "MULTIJUGADOR · online con un código de 5 letras.",
     "MULTIPLAYER", "Online with a 5-letter code",
     "MULTIPLAYER · online with a 5-letter code."),
    ("CAMPEONATOS", 480, 88, "CAMPEONATOS", "6 rivales con su historia",
     "CAMPEONATOS · 6 rivales con su historia. ¡Corona la OESTE!",
     "CHAMPIONSHIPS", "6 rivals, each with a story",
     "CHAMPIONSHIPS · 6 rivals with their own story. Crown the WEST!"),
    ("RANKING MUNDIAL", 300, 80, "RANKING MUNDIAL", "Compite con el mundo",
     "RANKING MUNDIAL · compite con jugadores de todo el mundo.",
     "WORLD RANKING", "Compete with the world",
     "WORLD RANKING · compete with players from everywhere."),
    ("ENTRENAR", 300, 80, "ENTRENAR", "5 áreas para tu técnica",
     "ENTRENAR · PRO TRAINING: 5 áreas para pulir tu técnica.",
     "TRAINING", "5 areas to polish technique",
     "TRAINING · PRO TRAINING: 5 areas to polish your technique."),
]

PODERES_ES = "PODERES · SOLO CAMPEONATOS: 20 toques seguidos cargan · gatillo lanza · 10 s"
PODERES_EN = "POWERS · CHAMPIONSHIPS ONLY: 20 straight hits charge · trigger fires · 10 s"
TITULOS = {"ES": "LOS MODOS", "EN": "THE MODES"}

POS = [(190, 296), (690, 296), (190, 396), (690, 396), (190, 496), (506, 496)]
COLS = ["rgba(47,158,68,0.8)", "rgba(232,89,12,0.8)", "rgba(112,72,232,0.8)",
        "rgba(184,134,11,0.8)", "rgba(12,166,120,0.8)", "rgba(28,126,214,0.8)"]
INIS = ["P", "S", "M", "C", "R", "T"]


def extrae_funcion(src, nombre):
    """Extrae `function nombre(...) {...}` del fuente por apareamiento de llaves."""
    m = re.search(r"function " + nombre + r"\(", src)
    if not m:
        return None
    i = src.index("{", m.end() - 1)
    prof = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            prof += 1
        elif src[j] == "}":
            prof -= 1
            if prof == 0:
                return src[m.start():j + 1]
    return None


JS_PINTA = """(args) => {
  const funcs = args[0], tarjetas = args[1], idioma = args[2];
  const PODERES = args[3], TITULO = args[4];
  const cv = document.createElement('canvas');
  cv.width = 1408; cv.height = 768;
  const c = cv.getContext('2d');
  const LINE_MAXW = 960, PIZ_CX = 680;
  // funciones SERVIDAS (extraídas del game.html en vivo)
  const rr = new Function('return ' + funcs.rr)();
  const fitFont = new Function('return ' + funcs.fitFont)();
  const line = new Function('c', 'txt', 'y', 'size', 'col', 'align', 'x', 'maxW',
    'const fitFont = ' + funcs.fitFont + '; const LINE_MAXW = 960, PIZ_CX = 680; return (' + funcs.line + ')(c, txt, y, size, col, align, x, maxW);');
  const pill = new Function('c', 'txt', 'y', 'opts',
    'const rr = ' + funcs.rr + '; return (' + funcs.pill + ')(c, txt, y, opts);');
  const cardWrap = new Function('return ' + funcs.cardWrap)();
  const modeCard = new Function('c', 'x', 'y', 'w', 'h', 'col0', 'ini', 'title', 'sub', 'extra',
    'const rr = ' + funcs.rr + '; const cardWrap = ' + funcs.cardWrap + ';' +
    ' return (' + funcs.modeCard + ')(c, x, y, w, h, col0, ini, title, sub, extra);');
  const wrap2 = new Function('c', 'txt', 'y', 'size', 'col', 'maxW', 'lh', 'x',
    'const fitFont = ' + funcs.fitFont + '; const LINE_MAXW = 960, PIZ_CX = 680;' +
    ' const line = ' + funcs.line + ';' +
    ' return (' + funcs.wrap2 + ')(c, txt, y, size, col, maxW, lh, x);');

  // fondo de la pizarra (rama fallback de paintStep)
  rr(c, 8, 8, 1392, 752, 30);
  const bg = c.createLinearGradient(0, 0, 0, 768);
  bg.addColorStop(0, 'rgba(13,19,34,0.97)');
  bg.addColorStop(1, 'rgba(8,11,20,0.97)');
  c.fillStyle = bg; c.fill();
  c.strokeStyle = 'rgba(232,180,90,0.75)'; c.lineWidth = 4; c.stroke();
  // cabecera (réplica fiel de paintHeader)
  c.textAlign = 'left'; c.textBaseline = 'middle';
  c.shadowColor = 'rgba(255,210,87,0.4)'; c.shadowBlur = 8;
  c.fillStyle = '#ffd257';
  c.font = '900 40px system-ui, sans-serif';
  c.fillText('LA ACADEMIA CRAZY', 300, 212);
  c.shadowBlur = 0;
  c.font = '700 20px system-ui, sans-serif';
  c.fillStyle = '#cfd8e0'; c.textAlign = 'right';
  c.fillText('PASO 8 DE 9', 1150, 206);
  for (let i = 0; i < 9; i++) {
    const dx = 1146 - (9 - 1 - i) * 24;
    c.beginPath(); c.arc(dx, 240, i === 7 ? 7.5 : 5, 0, Math.PI * 2);
    c.fillStyle = i < 7 ? '#7fb069' : (i === 7 ? '#ffd257' : 'rgba(255,255,255,0.28)');
    c.fill();
  }
  // pintor del paso 7 (réplica con las funciones SERVIDAS)
  const POS = [[190, 296], [690, 296], [190, 396], [690, 396], [190, 496], [506, 496]];
  const COLS = ['rgba(47,158,68,0.8)', 'rgba(232,89,12,0.8)', 'rgba(112,72,232,0.8)',
    'rgba(184,134,11,0.8)', 'rgba(12,166,120,0.8)', 'rgba(28,126,214,0.8)'];
  const INIS = ['P', 'S', 'M', 'C', 'R', 'T'];
  line(c, TITULO, 262, 34, '#ffd257');
  pill(c, 'GATILLO · continuar', 252, { w: 300, h: 32, x: 986, col: 'rgba(232,180,90,0.28)', size: 18 });
  const W = 480, H = 88;
  for (let i = 0; i < 4; i++) {
    const [x, y] = POS[i];
    const t = tarjetas[i];
    modeCard(c, x, y, W, H, COLS[i], INIS[i],
      idioma === 'ES' ? t[3] : t[6], idioma === 'ES' ? t[4] : t[7],
      idioma === 'ES' ? t[5] : t[8]);
  }
  const t4 = tarjetas[4], t5 = tarjetas[5];
  modeCard(c, 190, 496, 300, 80, COLS[4], 'R',
    idioma === 'ES' ? t4[3] : t4[6], idioma === 'ES' ? t4[4] : t4[7],
    idioma === 'ES' ? t4[5] : t4[8]);
  modeCard(c, 506, 496, 300, 80, COLS[5], 'T',
    idioma === 'ES' ? t5[3] : t5[6], idioma === 'ES' ? t5[4] : t5[7],
    idioma === 'ES' ? t5[5] : t5[8]);
  rr(c, 822, 496, 348, 80, 14);
  c.fillStyle = 'rgba(232,180,90,0.14)'; c.fill();
  c.strokeStyle = 'rgba(232,180,90,0.45)'; c.lineWidth = 2; c.stroke();
  wrap2(c, PODERES, 536, 14, '#ffe08a', 312, 11, 996);
  // medición de contención con las MISMA funciones servidas
  const informe = [];
  let mal = 0;
  const twOf = (w) => w - 86;
  for (let i = 0; i < tarjetas.length; i++) {
    const t = tarjetas[i];
    const [, , h, , , , , ,] = t;
    const title = idioma === 'ES' ? t[3] : t[6];
    const sub = idioma === 'ES' ? t[4] : t[7];
    const extra = idioma === 'ES' ? t[5] : t[8];
    const y = POS[i][1], tw = twOf(i < 4 ? 480 : 300);
    const tt = cardWrap(c, title, 21, '800', 14, tw, 1);
    const ts = cardWrap(c, sub, 15, '500', 10, tw, 1);
    const te = cardWrap(c, extra, 13, '600', 9, tw, 2);
    const compacta = !(h >= 88) || te.lines.length === 2;
    c.font = '800 ' + tt.size + 'px system-ui, sans-serif';
    const wT = c.measureText(tt.lines[0]).width;
    c.font = '500 ' + ts.size + 'px system-ui, sans-serif';
    const wS = c.measureText(ts.lines[0]).width;
    let wE = 0;
    for (const ln of te.lines) {
      c.font = '600 ' + te.size + 'px system-ui, sans-serif';
      wE = Math.max(wE, c.measureText(ln).width);
    }
    const filas = [
      { y: y + (compacta ? 24 : 27), px: tt.size, t: tt.lines[0], w: '800' },
      { y: y + (compacta ? 42 : 50), px: ts.size, t: ts.lines[0], w: '500' },
    ];
    if (te.lines.length === 2) {
      filas.push({ y: y + h - 25, px: te.size, t: te.lines[0], w: '600' });
      filas.push({ y: y + h - 12, px: te.size, t: te.lines[1], w: '600' });
    } else {
      filas.push({ y: y + h - 14, px: te.size, t: te.lines[0], w: '600' });
    }
    let vOk = true, det = '';
    for (const f of filas) {
      c.font = f.w + ' ' + f.px + 'px system-ui, sans-serif';
      const m = c.measureText(f.t);
      const arriba = f.y - (m.actualBoundingBoxAscent || f.px * 0.7);
      const abajo = f.y + (m.actualBoundingBoxDescent || f.px * 0.25);
      if (arriba < y + 2 || abajo > y + h - 2) {
        vOk = false;
        det += '[' + Math.round(arriba) + '..' + Math.round(abajo) + ' en ' + f.t.slice(0, 12) + '] ';
      }
      f.top = arriba; f.bot = abajo;
    }
    // r75 · COLISIÓN DE TINTA entre filas consecutivas (sub ↔ extra1 ↔ extra2):
    // la tinta de una fila no puede pisar la de la siguiente (≥0 px gap)
    for (let k = 1; k < filas.length; k++) {
      if (filas[k].top < filas[k - 1].bot - 0.01) {
        vOk = false;
        det += 'COLISIÓN ' + filas[k - 1].t.slice(0, 10) + '↔' + filas[k].t.slice(0, 10) + ' ';
      }
    }
    const okC = wT <= tw && wS <= tw && wE <= tw && vOk;
    if (!okC) mal++;
    informe.push({ card: t[0] + '·' + idioma, tw, wT: Math.round(wT), wS: Math.round(wS),
      wE: Math.round(wE), lin: te.lines.length, ok: okC, det });
  }
  // PODERES: las mitades del wrap2 servido deben caber en 312
  fitFont(c, PODERES, 14, '600', 312, 12);
  let podOk = true, podMax = 0;
  if (c.measureText(PODERES).width > 312) {
    const sep = PODERES.lastIndexOf(' ', Math.ceil(PODERES.length / 2));
    for (const ln of [PODERES.slice(0, sep), PODERES.slice(sep + 1)]) {
      fitFont(c, ln, 14, '600', 312, 9);
      podMax = Math.max(podMax, c.measureText(ln).width);
    }
    podOk = podMax <= 312;
  }
  return { informe: informe, mal: mal, podOk: podOk, podMax: Math.round(podMax) };
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

    print("— BLOQUE 1 · AGUJAS r75 en el game.html servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES (ramas viejas ausentes) + ORDEN de fuente —")
    for label, pats, esperado in CONTADORES:
        n = sum(len(re.findall(re.escape(p), src)) for p in pats)
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")
    for a, b, label in ORDEN_FUENTE:
        chk(0 <= src.find(a) < src.find(b), label)

    # funciones SERVIDAS para el bloque en vivo
    funcs = {}
    for nombre in ["rr", "fitFont", "line", "pill", "wrap2", "cardWrap", "modeCard"]:
        f = extrae_funcion(src, nombre)
        if not f:
            print(f"✗ FALLO: función {nombre} no encontrada en el servido")
            sys.exit(1)
        funcs[nombre] = f

    print("— BLOQUE 3 · JUEGO REAL headless (contención con funciones servidas + capturas) —")
    os.makedirs(DIR_CAPS, exist_ok=True)
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            juego = False
            for _ in range(90):
                juego = await page.evaluate(
                    "() => !!(window.__PP_GAME && window.__PP_TUT)")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_GAME y __PP_TUT")

            for idioma, poderes in (("ES", PODERES_ES), ("EN", PODERES_EN)):
                res = await page.evaluate(
                    JS_PINTA,
                    [funcs, [list(t) for t in TARJETAS], idioma, poderes,
                     TITULOS[idioma]])
                for inf in res["informe"]:
                    chk(inf["ok"],
                        f"{inf['card']}: T={inf['wT']} S={inf['wS']} "
                        f"E={inf['wE']}×{inf['lin']}l ≤ tw={inf['tw']} "
                        f"{'✓ dentro' if inf['ok'] else 'FUERA ' + inf['det']}")
                chk(res["mal"] == 0,
                    f"{idioma}: las 6 tarjetas SIN desbordes ({res['mal']})")
                chk(res["podOk"],
                    f"{idioma}: caja PODERES dentro (máx {res['podMax']} ≤ 312)")
                # captura para el dueño: re-pintamos en un canvas del DOM
                # y exportamos los PÍXELES con toDataURL (sin compositing)
                await page.evaluate(
                    """(args) => {
                      const funcs = args[0], tarjetas = args[1], idioma = args[2];
                      const PODERES = args[3], TITULO = args[4];
                      const prev = document.getElementById('qa75cv');
                      if (prev) prev.remove();
                      const cv = document.createElement('canvas');
                      cv.id = 'qa75cv'; cv.className = '__qa75';
                      cv.width = 1408; cv.height = 768;
                      cv.style.width = '1408px'; cv.style.height = '768px';
                      document.body.appendChild(cv);
                      const c = cv.getContext('2d');
                      const LINE_MAXW = 960, PIZ_CX = 680;
                      const rr = new Function('return ' + funcs.rr)();
                      const fitFont = new Function('return ' + funcs.fitFont)();
                      const line = new Function('c','txt','y','size','col','align','x','maxW',
                        'const fitFont = ' + funcs.fitFont + '; const LINE_MAXW = 960, PIZ_CX = 680; return (' + funcs.line + ')(c, txt, y, size, col, align, x, maxW);');
                      const pill = new Function('c','txt','y','opts',
                        'const rr = ' + funcs.rr + '; return (' + funcs.pill + ')(c, txt, y, opts);');
                      const cardWrap = new Function('return ' + funcs.cardWrap)();
                      const modeCard = new Function('c','x','y','w','h','col0','ini','title','sub','extra',
                        'const rr = ' + funcs.rr + '; const cardWrap = ' + funcs.cardWrap + ';' +
                        ' return (' + funcs.modeCard + ')(c, x, y, w, h, col0, ini, title, sub, extra);');
                      const wrap2 = new Function('c','txt','y','size','col','maxW','lh','x',
                        'const fitFont = ' + funcs.fitFont + '; const LINE_MAXW = 960, PIZ_CX = 680;' +
                        ' const line = ' + funcs.line + ';' +
                        ' return (' + funcs.wrap2 + ')(c, txt, y, size, col, maxW, lh, x);');
                      rr(c, 8, 8, 1392, 752, 30);
                      const bg = c.createLinearGradient(0, 0, 0, 768);
                      bg.addColorStop(0, 'rgba(13,19,34,0.97)');
                      bg.addColorStop(1, 'rgba(8,11,20,0.97)');
                      c.fillStyle = bg; c.fill();
                      c.strokeStyle = 'rgba(232,180,90,0.75)'; c.lineWidth = 4; c.stroke();
                      c.textAlign = 'left'; c.textBaseline = 'middle';
                      c.shadowColor = 'rgba(255,210,87,0.4)'; c.shadowBlur = 8;
                      c.fillStyle = '#ffd257';
                      c.font = '900 40px system-ui, sans-serif';
                      c.fillText('LA ACADEMIA CRAZY', 300, 212);
                      c.shadowBlur = 0;
                      c.font = '700 20px system-ui, sans-serif';
                      c.fillStyle = '#cfd8e0'; c.textAlign = 'right';
                      c.fillText('PASO 8 DE 9', 1150, 206);
                      for (let i = 0; i < 9; i++) {
                        const dx = 1146 - (9 - 1 - i) * 24;
                        c.beginPath(); c.arc(dx, 240, i === 7 ? 7.5 : 5, 0, Math.PI * 2);
                        c.fillStyle = i < 7 ? '#7fb069' : (i === 7 ? '#ffd257' : 'rgba(255,255,255,0.28)');
                        c.fill();
                      }
                      line(c, TITULO, 262, 34, '#ffd257');
                      pill(c, 'GATILLO · continuar', 252, { w: 300, h: 32, x: 986, col: 'rgba(232,180,90,0.28)', size: 18 });
                      const W = 480, H = 88;
                      const POS = [[190, 296], [690, 296], [190, 396], [690, 396], [190, 496], [506, 496]];
                      const COLS = ['rgba(47,158,68,0.8)', 'rgba(232,89,12,0.8)', 'rgba(112,72,232,0.8)',
                        'rgba(184,134,11,0.8)', 'rgba(12,166,120,0.8)', 'rgba(28,126,214,0.8)'];
                      const INIS = ['P', 'S', 'M', 'C', 'R', 'T'];
                      for (let i = 0; i < tarjetas.length; i++) {
                        const t = tarjetas[i];
                        const alto = i < 4;
                        modeCard(c, POS[i][0], POS[i][1], alto ? 480 : 300, alto ? 88 : 80,
                          COLS[i], INIS[i],
                          idioma === 'ES' ? t[3] : t[6], idioma === 'ES' ? t[4] : t[7],
                          idioma === 'ES' ? t[5] : t[8]);
                      }
                      rr(c, 822, 496, 348, 80, 14);
                      c.fillStyle = 'rgba(232,180,90,0.14)'; c.fill();
                      c.strokeStyle = 'rgba(232,180,90,0.45)'; c.lineWidth = 2; c.stroke();
                      wrap2(c, PODERES, 536, 14, '#ffe08a', 312, 11, 996);
                      c.fillStyle = '#8b98a5';
                      c.font = '600 18px system-ui, sans-serif';
                      c.textAlign = 'center'; c.textBaseline = 'middle';
                      c.fillText('B · saltar · STICK · repetir la voz', 680, 604);
                    }""",
                    [funcs, [list(t) for t in TARJETAS], idioma, poderes,
                     TITULOS[idioma]])
                b64 = await page.evaluate(
                    "() => document.getElementById('qa75cv').toDataURL('image/png')")
                ruta = os.path.join(DIR_CAPS, f"pizarra_modos_r75_{idioma}.png")
                with open(ruta, "wb") as fp:
                    fp.write(base64.b64decode(b64.split(",", 1)[1]))
                print(f"  · captura {idioma} → {ruta}")
        finally:
            await browser.close()

    await asyncio.sleep(0.1)
    print(f"\nRESULTADO: {ok} OK · {fails} fallos (capa BJ · qa_r75_v3667)")
    sys.exit(1 if fails else 0)


asyncio.run(main())
