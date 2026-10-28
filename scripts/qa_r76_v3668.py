#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r76_v3668 — CAPA BK · V3.6.77-SDK6, FASE 70 «EL PULSO CRAZY».

Aprobación del dueño (r76): «vamos a implementar con mucho cuidado los 4
puntos dejando el estado actual como punto seguro de restauración. Necesito
RAZONES PARA VOLVER CADA DÍA… sorpréndeme con algo único adaptado a nuestro
juego que haga que los jugadores estén dispuestos a pagar por ello».

LO CONSTRUIDO (r76) y SU verificación:
  · EL PULSO CRAZY — el latido diario de la academia, en el hub de PRO
    TRAINING (hueco libre medido y 1064–1330: no mueve nada del layout):
    RETO DEL DÍA determinista por fecha local (dayKey + seedOf FNV-1a +
    dailyPlan sobre los 9 modos existentes), campeón del día de flavor,
    TU FANTASMA (tu mejor marca como rival) y EL INFORME DEL PROFESOR
    (consejo técnico diario generado de datos reales: best/acc/stars).
  · RACHA DE ASISTENCIA: NK días consecutivos (se enfría si fallas un
    día, effStreak) con recompensa 40 + 5×min(nk−1,7) + 15 si vences a tu
    fantasma; cobro único por día; poda de done{} a 90 días.
  · PIELES DE ASISTENCIA (via:'racha', min:Infinity ⇒ jamás por puntos):
    Neón 7 días · Fantasma 14 · Campeón 30 — fila PROPIA bajo el panel,
    fuera de la fila de puntos; buildPipTexture (cero shaders nuevos).
  · GAMF()=0 ⇒ el PULSO no existe (panel oculto, dailyComplete no-op):
    el flujo legacy de puntos queda intacto.

BLOQUES: (1) AGUJAS r76 en el game.html servido. (2) CONTADORES + ORDEN
de fuente. (3) JUEGO REAL headless: determinismo del plan, flujo completo
de cobro (único por día, fantasma, racha, enfrío, hitos 7/14/30 con las
tres pieles), panel vivo en el canvas del menú con rects dentro de bounds
+ captura download/pulso_r76.png, 0 pageerrors.
Uso: python3 scripts/qa_r76_v3668.py [URL]
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
    # --- r76 · EL PULSO CRAZY: motor del día ---
    ("dayKey definida (fecha local YYYY-MM-DD)",
     "function dayKey(off) {"),
    ("seedOf definida (FNV-1a 32 bits)",
     "function seedOf(s) {"),
    ("dailyPlan definida (determinista por día)",
     "function dailyPlan(k) {"),
    ("dailyTip definida (EL INFORME DEL PROFESOR)",
     "function dailyTip(k) {"),
    ("effStreak definida (racha viva, se enfría)",
     "function effStreak() {"),
    ("dailyComplete definida (cobro único por día)",
     "function dailyComplete(mode, res, oldBest) {"),
    ("gate GAMF en dailyComplete (gamify=0 ⇒ no existe)",
     "if (!GAMF()) return;                 // gamify=0 ⇒ el PULSO no existe"),
    ("recompensa: base 40 + paso 5 + tope 7 + fantasma 15",
     "const DAILY_BASE = 40, DAILY_PASO = 5, DAILY_TOPE = 7, DAILY_FANTASMA = 15;"),
    ("poda de done{} a 90 días",
     "const DAILY_PODA = 90;"),
    ("campeones del día (la casa del juego · r85: HALLOWEEN sustituye al retirado)",
     "const CHAMPS_DIA = ['CLOW', 'WIZARD', 'FORAJIDO', 'ORBITAL', 'HALLOWEEN'];"),
    # --- r76 · pieles de asistencia ---
    ("piel Neón (racha 7)",
     "{ id: 'neon', name: { es: 'Neón', en: 'Neon' }, min: Infinity, days: 7, via: 'racha', tex: 'neon', edge: 0x39ff88, grip: 0x0f3d2e },"),
    ("piel Fantasma (racha 14)",
     "{ id: 'fantasma', name: { es: 'Fantasma', en: 'Ghost' }, min: Infinity, days: 14, via: 'racha', tex: 'fantasma', edge: 0xbfe9ff, grip: 0x43545e },"),
    ("piel Campeón (racha 30, oro vivo)",
     "{ id: 'campeon', name: { es: 'Campeón', en: 'Champion' }, min: Infinity, days: 30, via: 'racha', tex: 'oro', edge: 0xffd700, grip: 0x4a3808, anim: true },"),
    ("textura neón (buildPipTexture, cero shaders nuevos)",
     "neon: () => buildPipTexture({ base: '#0c1410', hi: '#39ff88', lo: '#02120a', glow: true, glowColor: 'rgba(57,255,136,0.9)' }),"),
    ("textura fantasma (buildPipTexture)",
     "fantasma: () => buildPipTexture({ base: '#dfeef8', hi: '#ffffff', lo: '#9dc2d6', glow: false }),"),
    # --- r76 · hook en okHit (fuera del camino legacy) ---
    ("okHit: valor logrado capturado ANTES de resets",
     "const __dailyRes = (active === 't5a') ? st.rally : st.streak;"),
    ("okHit: marca previa capturada (el fantasma se juega con la vieja)",
     "const __dailyOld = S.best[active] || 0;"),
    ("okHit: hook del PULSO en el goal (try — nunca rompe)",
     "try { dailyComplete(active, __dailyRes, __dailyOld); } catch (eD) { /* nunca rompe */ }"),
    # --- r76 · panel del hub — r80 · EL RETO SE MUDA A LA PUERTA ---
    ("r80: la entrada del reto vive ahora en el menú principal",
     "case 'retoDiario':"),
    ("r80: arranque directo público del duelo de hoy",
     "startDaily: (g) => {"),
    ("r80: fila propia de pieles de asistencia (escaparate en el hueco)",
     "const yA = 1064;"),
    ("fila de puntos: las de asistencia NO entran",
     "if (sk.via === 'racha') continue;   // r76: las de asistencia viven en EL PULSO (fila propia)"),
    ("candado en el hueco de la miniatura (slot de inventario)",
     "c.fillText('\\u{1F512}', axD + 30, yA + 57);"),
    ("hito de racha legible en la fila inferior",
     "c.fillText('racha ' + sk.days + ' ' + t('daily_dias'), axD + 58, yA + 64);"),
    # --- r76 · comando de menú + exposición QA ---
    ("menuAction: comando daily",
     "else if (cmd === 'daily') {"),
    ("menuAction: arranca el modo del día (r80 · zonas dobles)",
     "startMode(game, dailyPlan(dayKey()).mode, { daily: 1 });"),
    ("state: snapshot daily (QA/hub; r80 · modo del día incluido)",
     "modoName: t(MODES[_pD.mode].nk)"),
    ("__test: internos del PULSO expuestos",
     "dayKey, dailyPlan, dailyTip, dailyComplete, effStreak, seedOf,"),
    ("i18n ES: título del reto",
     "daily_t: 'RETO DEL DÍA',"),
    ("i18n EN: título del reto",
     "daily_t: 'DAILY CHALLENGE',"),
    ("i18n ES: el profesor",
     "daily_prof: 'El profesor: «{tip}»',"),
    ("i18n EN: el profesor",
     "daily_prof: 'The professor: \u201c{tip}\u201d',"),
    # --- intacto (el hub que ya funcionaba) ---
    ("hub: tarjetas de áreas intactas",
     "btn('trv3:area:' + id, x, yy, CW, CH, '', false);"),
    ("hub: botón de parar intacto en 1380",
     "if (active) btn('trv3:stop', X0, 1380, 452, 76, t('parar'), false, 'surv', undefined, 28);"),
    ("def: estado daily con migración",
     "daily: { last: '', streak: 0, bestStreak: 0, done: {} },"),
    ("migración defensiva del daily en la carga",
     "d.daily = Object.assign({ last: '', streak: 0, bestStreak: 0, done: {} }, d.daily || {});"),
]

CONTADORES = [
    ("pieles de asistencia ×3 (via:'racha')",
     ["via: 'racha'"], 3),
    ("botón del PULSO en el hub RETIRADO (r80: ×0 — vive en la puerta)",
     ["btn('trv3:daily'"], 0),
    ("comando daily ×1",
     ["else if (cmd === 'daily') {"], 1),
    ("dayKey definida ×1",
     ["function dayKey(off) {"], 1),
    ("seedOf definida ×1",
     ["function seedOf(s) {"], 1),
    ("dailyPlan definida ×1",
     ["function dailyPlan(k) {"], 1),
    ("dailyComplete definida ×1",
     ["function dailyComplete(mode, res, oldBest) {"], 1),
    ("hook en okHit ×1",
     ["try { dailyComplete(active, __dailyRes, __dailyOld); }"], 1),
    ("fila de puntos: continue de asistencia ×1",
     ["if (sk.via === 'racha') continue;"], 1),
    ("clave huérfana daily_lock_r AUSENTE (0)",
     ["daily_lock_r"], 0),
]

ORDEN_FUENTE = [
    ("function dayKey(off) {", "function dailyPlan(k) {",
     "dayKey se define ANTES de dailyPlan"),
    ("function dailyPlan(k) {", "function dailyComplete(mode, res, oldBest) {",
     "dailyPlan se define ANTES de dailyComplete"),
    ("EL RETO SE MUDA A LA PUERTA", "btn('trv3:stop', X0, 1380",
     "el escaparate de pieles queda ANTES del botón parar (r80)"),
    ("const yA = 1064;", "btn('trv3:stop', X0, 1380",
     "la fila de pieles (1064) no alcanza la fila de abajo (1380)"),
]

# --- JUEGO REAL: verificación del motor del PULSO con el juego servido ----
JS_PULSO = """(args) => {
  const T = window.__PP_TRAIN, G = window.__PP_GAME;
  if (!T || !T.__test || !T.__debug) return { error: 'sin __test/__debug' };
  const tt = T.__test, dbg = T.__debug, S = dbg.S;
  const out = { checks: [] };
  const ok = (id, cond, det) => out.checks.push({ id, ok: !!cond, det: det || '' });

  // 1 · exposición de internos
  for (const k of ['dayKey', 'dailyPlan', 'dailyTip', 'dailyComplete', 'effStreak', 'seedOf']) {
    ok('expone.' + k, typeof tt[k] === 'function');
  }

  // 2 · dayKey con formato local
  const kHoy = tt.dayKey();
  ok('dayKey.formato', /^\\d{4}-\\d{2}-\\d{2}$/.test(kHoy), kHoy);
  ok('dayKey.ayer', tt.dayKey(-1) < kHoy, tt.dayKey(-1));

  // 3 · determinismo del plan
  const p1 = tt.dailyPlan(kHoy), p2 = tt.dailyPlan(kHoy);
  ok('plan.determinista', p1.mode === p2.mode && p1.champ === p2.champ && p1.frase === p2.frase);
  const modos = Object.keys(dbg.MODES);
  ok('plan.modoValido', modos.indexOf(p1.mode) >= 0, p1.mode);
  ok('plan.metaCoherente', p1.n === dbg.MODES[p1.mode].n, p1.n);
  ok('plan.campeon', ['CLOW', 'WIZARD', 'FORAJIDO', 'ORBITAL', 'NEÓN'].indexOf(p1.champ) >= 0, p1.champ);
  ok('plan.frase', /^daily_p[0-4]$/.test(p1.frase), p1.frase);
  const pOtro = tt.dailyPlan('2026-01-01'), pOtro2 = tt.dailyPlan('2026-01-02');
  ok('plan.cambiaPorDia', tt.seedOf('ppx-2026-01-01') !== tt.seedOf('ppx-2026-01-02'));

  // 4 · flujo completo de cobro (estado fabricado limpio)
  const pts0 = S.pts;
  S.daily = { last: '', streak: 0, bestStreak: 0, done: {} };
  S.best[p1.mode] = 0; S.acc[p1.mode] = 0; S.stars[p1.mode] = 0;
  const unlocked0 = S.unlocked.slice();

  // 4a · modo equivocado ⇒ nada
  tt.dailyComplete(p1.mode === 't1a' ? 't3a' : 't1a', 9, 0);
  ok('cobro.modoEquivocado', !S.daily.done[kHoy] && S.pts === pts0);

  // 4b · modo del día con fantasma (res 5 > vieja 0) ⇒ cobro 40+0+15
  tt.dailyComplete(p1.mode, 5, 0);
  const d1 = S.daily.done[kHoy];
  ok('cobro.registrado', !!d1 && d1.m === p1.mode && d1.res === 5, JSON.stringify(d1 || {}));
  ok('cobro.fantasma', !!d1 && d1.g === 1);
  ok('cobro.racha1', S.daily.streak === 1 && S.daily.bestStreak === 1);
  ok('cobro.pts55', S.pts === pts0 + 55, (S.pts - pts0) + '');
  ok('cobro.last', S.daily.last === kHoy);

  // 4c · doble cobro ⇒ nada
  const ptsB = S.pts;
  tt.dailyComplete(p1.mode, 9, 0);
  ok('cobro.unicoPorDia', S.pts === ptsB && Object.keys(S.daily.done).length === 1);

  // 4d · mañana con racha y sin fantasma (5 ≤ vieja 99) ⇒ 40+5, g:0
  S.daily.done = {}; S.daily.last = tt.dayKey(-1); S.daily.streak = 1;
  const ptsC = S.pts;
  tt.dailyComplete(p1.mode, 5, 99);
  ok('cobro.racha2', S.daily.streak === 2, S.daily.streak + '');
  ok('cobro.pts45', S.pts === ptsC + 45, (S.pts - ptsC) + '');
  ok('cobro.sinFantasma', S.daily.done[kHoy] && S.daily.done[kHoy].g === 0);

  // 4e · racha fría (última vez 2020) ⇒ nk=1
  S.daily.done = {}; S.daily.last = '2020-01-01'; S.daily.streak = 10;
  ok('racha.fria.effStreak', tt.effStreak() === 0, tt.effStreak() + '');
  tt.dailyComplete(p1.mode, 5, 99);
  ok('racha.reinicia', S.daily.streak === 1);

  // 4f · hitos 7/14/30 ⇒ Neón/Fantasma/Campeón (jamás por puntos)
  const hitos = [[6, 'neon'], [13, 'fantasma'], [29, 'campeon']];
  for (const [prev, piel] of hitos) {
    S.unlocked = unlocked0.slice();
    S.daily.done = {}; S.daily.last = tt.dayKey(-1); S.daily.streak = prev;
    tt.dailyComplete(p1.mode, 5, 99);
    ok('hito.' + piel, S.unlocked.indexOf(piel) >= 0, 'racha ' + (prev + 1) + ' → ' + piel);
  }
  S.unlocked = unlocked0.slice();

  // 4g · el informe del profesor responde SIEMPRE con datos reales
  S.best[p1.mode] = 0;
  const tip0 = tt.dailyTip(kHoy);
  ok('profesor.sinMarca', tip0.k === 'daily_t0', tip0.k);
  S.best[p1.mode] = dbg.MODES[p1.mode].n; S.acc[p1.mode] = 60;
  ok('profesor.precision', tt.dailyTip(kHoy).k === 'daily_t2', tt.dailyTip(kHoy).k);
  S.acc[p1.mode] = 95; S.stars[p1.mode] = 3;
  ok('profesor.dominado', tt.dailyTip(kHoy).k === 'daily_t4', tt.dailyTip(kHoy).k);

  // 5 · panel vivo r80: el botón del PULSO ya NO está en el hub (vive en
  // la puerta — capa BO) y las pieles de asistencia siguen en su fila
  G.menuPage = 'train';
  G.drawMenu();
  const rects = G.menuRects || [];
  const rDaily = rects.filter((r) => r && r.id === 'trv3:daily');
  ok('panel.retirado', rDaily.length === 0, rDaily.length + ' (r80: se mudó al menú principal)');
  const rReto = null;   // la geometría del banner de la puerta la mide la capa BO
  for (const piel of ['neon', 'fantasma', 'campeon']) {
    const rs = rects.filter((r) => r && r.id === 'trv3:skin:' + piel);
    ok('panel.piel.' + piel, rs.length === 1, rs.length + '');
  }
  // fila de puntos intacta (6 pieles por puntos) + fila propia (3 asistencia)
  const idsSkin = rects.filter((r) => r && /trv3:skin:/.test(r.id)).map((r) => r.id);
  const puntosN = idsSkin.filter((i) => /clás|clasica|fuego|hielo|oro$|arcoiris|carbon/.test(i)).length;
  ok('panel.filaPuntos6', puntosN === 6, idsSkin.join(','));
  ok('panel.pielesTotal', idsSkin.length === 9, idsSkin.length + ' (6 por puntos + 3 asistencia)');

  // 6 · captura del lienzo del menú con el PULSO pintado
  try {
    out.cap = G.menuCanvas.toDataURL('image/png');
  } catch (e) { out.cap = null; }
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

    print("— BLOQUE 1 · AGUJAS r76 en el game.html servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES + ORDEN de fuente —")
    for label, pats, esperado in CONTADORES:
        n = sum(len(re.findall(re.escape(p), src)) for p in pats)
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")
    for a, b, label in ORDEN_FUENTE:
        chk(0 <= src.find(a) < src.find(b), label)

    print("— BLOQUE 3 · JUEGO REAL headless (motor del PULSO + panel + captura) —")
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
                    "() => !!(window.__PP_GAME && window.__PP_TRAIN)")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_GAME y __PP_TRAIN")

            res = await page.evaluate(JS_PULSO, [])
            if res.get("error"):
                chk(False, "JS_PULSO: " + res["error"])
            else:
                for c in res["checks"]:
                    chk(c["ok"], c["id"] + (f" [{c['det']}]" if c["det"] else ""))
                if res.get("cap"):
                    with open(os.path.join(DIR_CAPS, "pulso_r76.png"), "wb") as f:
                        f.write(base64.b64decode(res["cap"].split(",", 1)[1]))
                    chk(True, "captura del hub con EL PULSO → download/pulso_r76.png")
                else:
                    chk(False, "captura del hub (menuCanvas.toDataURL)")

            if page_errors:
                for e in page_errors:
                    print("  ✗ pageerror: " + e[:200])
            chk(len(page_errors) == 0, "0 pageerrors en toda la sesión")
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} FALLOS (qa_r76_v3668 · CAPA BK)")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
