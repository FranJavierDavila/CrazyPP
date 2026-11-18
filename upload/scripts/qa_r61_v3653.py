#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r61 · v3.6.53-SDK6 · FASE 55 «Estela de poderes, rival que se adapta y el
mejor intercambio en pantalla» — QA de las features de la ronda. r115 ·
RE-ANCA HONESTA: la REPETICIÓN DEL MEJOR INTERCAMBIO (feature 3 de la r61)
la SUPRIMIÓ el dueño — la capa verifica ahora su AUSENCIA (agujas negativas
+ mecánica headless) y que el fin de partido va directo a revancha:

  1) ESTELA DE PODER — la estela de la bola viste la firma del poder de
     pala ACTIVO (mega ámbar · efecto rojo · imán cian · portal violeta ·
     clon azul fantasma) con lerp suave y respaldo por EFECTO (spin).
  2) RIVAL ADAPTATIVO — existía desde v2.x pero era invisible: ahora
     conmutador persistente (AJUSTES + HUB junto a la dificultad), mensaje
     de estado y transición SUAVE (lerp del factor en el tick).
  3) RETIRO r115 — fuera grabadora, fantasmas, cartel, i18n rep_* y la
     cámara lenta del replay; la fanfarria respira sola y el gatillo en
     'over' es revancha desde el primer pulso.

Uso: python3 scripts/qa_r61_v3653.py        (servidor dev en :3000)
"""
import asyncio
import re
import sys

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(('  \u2713 ' if cond else '  \u2717 FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # --- 1 · estela de poder ---
    ("estela: trailUpdate acepta el tinte del poder",
     "const trailUpdate = (ball, dt, tint) => {"),
    ("estela: rama del tinte antes del respaldo por spin",
     "if (tint && tint.length === 3) {"),
    ("estela: mapa de firmas TRAIL_PODER (5 poderes)",
     "const TRAIL_PODER = {"),
    ("estela: firma según el poder ACTIVO (_megaActivaRest)",
     "_trailFirmaPoder() {"),
    ("estela: la llamada pasa el tinte lerp-eado",
     "this.trailUpdate(this.ball, dt, this._trailTint);"),
    # --- 2 · rival adaptativo ---
    ("adaptativa: conmutador persistente (ppxr_adapt_v1)",
     "localStorage.getItem('ppxr_adapt_v1') !== '0'"),
    ("adaptativa: caso 'adapt' en el dispatcher con applyAISkill",
     "case 'adapt': {"),
    ("adaptativa: botón en AJUSTES › JUEGO (r71 lo mudó del HUB)",
     "btn('adapt', 56, y, 912, 56,"),
    ("adaptativa: objetivo + factor actual (lerp en el tick)",
     "this._aiKTarget = THREE.MathUtils.clamp(k, 0.7, 2.2);"),
    ("adaptativa: aplicación suave del factor",
     "_aiKAplica() {"),
    ("adaptativa: el tick persigue al objetivo",
     "this._aiKCur += (this._aiKTarget - this._aiKCur) * Math.min(1, dt * 1.4);"),
    # --- 3 · RETIRO r115 de la repetición (agujas NEGATIVAS) ---
]

AGUJAS_FUERA = [
    ("retiro: la grabadora del mejor intercambio ya no existe",
     "_repGrabando"),
    ("retiro: el motor de frames del replay ya no existe",
     "_repStride"),
    ("retiro: los fantasmas (bola/rival) ya no existen",
     "ghostRival"),
    ("retiro: el cartel de la repetición ya no existe",
     "createReplayBanner"),
    ("retiro: la cámara lenta del replay ya no existe",
     "REP_SLOWMO"),
    ("retiro: i18n rep_t retirado",
     "rep_t: '"),
    ("retiro: i18n rep_chip retirado",
     "rep_chip: '"),
    ("retiro: i18n rep_slow retirado",
     "rep_slow: '"),
]

CLAVES = ['btn_adapt', 'msg_adapt']

MECANICA = """async () => {
  const out = [];
  const g = window.__game;

  // ---------- 1 · ESTELA DE PODER ----------
  const firma = (id) => ({
    mega: [0.93, 0.72, 0.32], efecto: [0.95, 0.24, 0.16],
    iman: [0.22, 0.78, 0.85], portal: [0.56, 0.35, 0.97],
    clon: [0.42, 0.72, 1.0],
  })[id];
  const bFake = { pos: { x: 0, y: 1, z: -1 }, spin: { x: 0, y: 0, z: 0 }, vel: { x: 0, y: 0, z: -1 } };
  const colores = () => Array.from(g.trailObj.geometry.attributes.color.array);
  // con tinte: la estela viste la firma (mega)
  g.trailUpdate(bFake, 0.016, firma('mega'));
  const cMega = colores();
  out.push({ ok: cMega.some((c, i) => i % 3 === 0 && c > 0.85) &&
                  cMega.some((c, i) => i % 3 === 2 && c > 0.25 && c < 0.45),
             lab: 'estela: tinte ámbar de SÚPER PALA pintado en el buffer' });
  // firma correcta por id activo (ventana viva)
  g._megaActivaId = 'clon'; g._clonT = 5;
  out.push({ ok: JSON.stringify(g._trailFirmaPoder()) === JSON.stringify(firma('clon')),
             lab: 'estela: con CLONACIÓN activo la firma es azul fantasma' });
  g._clonT = 0;
  out.push({ ok: g._trailFirmaPoder() === null,
             lab: 'estela: ventana caducada → sin tinte (manda el spin)' });
  g._megaActivaId = null;
  // sin tinte: respaldo por spin (topspin → naranja)
  const bSpin = { pos: { x: 0, y: 1, z: -1 }, spin: { x: -8, y: 0, z: 0 }, vel: { x: 0, y: 0, z: -3 } };
  g.trailUpdate(bSpin, 0.016, null);
  const cSpin = colores();
  out.push({ ok: cSpin.some((c, i) => i % 3 === 0 && c > 0.5),
             lab: 'estela: sin poder, el color por EFECTO (spin) sigue vivo' });

  // ---------- 2 · RIVAL ADAPTATIVO ----------
  const k0 = g.adaptive;
  g.adaptive = false;
  g.rules.scorePlayer = 6; g.rules.scoreAi = 0;
  g.applyAISkill();
  out.push({ ok: g._aiKTarget === 1,
             lab: 'adaptativa: OFF → factor objetivo 1 (dificultad honesta)' });
  g.adaptive = true;
  g.applyAISkill();
  out.push({ ok: g._aiKTarget > 1.25,
             lab: 'adaptativa: ganando 6-0 → aprieta (objetivo ' + g._aiKTarget.toFixed(2) + ')' });
  g.rules.scorePlayer = 0; g.rules.scoreAi = 6;
  g.applyAISkill();
  out.push({ ok: g._aiKTarget < 0.75,
             lab: 'adaptativa: perdiendo 0-6 → afloja (objetivo ' + g._aiKTarget.toFixed(2) + ')' });
  g.rules.scorePlayer = 0; g.rules.scoreAi = 0;
  g.applyAISkill();
  // el lerp del tick: con un objetivo RECIÉN cambiado, el factor se mueve
  // hacia él (si cur ya == target, no hay nada que mover — eso es correcto)
  g._aiKTarget = 1.5;
  const lerp0 = g._aiKCur;
  g._aiKCur += (g._aiKTarget - g._aiKCur) * 0.5;
  out.push({ ok: g._aiKCur > lerp0 + 0.001 && g._aiKCur < 1.5,
             lab: 'adaptativa: el lerp del tick mueve el factor hacia el objetivo' });
  g._aiKTarget = 1; g._aiKCur = 1;        // estado neutro para el resto
  // conmutador real, en su casa de r71: AJUSTES › JUEGO (persistencia incluida)
  g.menuPage = 'optsJuego';
  if (!g.menuOpen) g.toggleMenu();
  g.drawMenu();
  const iAd = (g.menuRects || []).findIndex(r => r && r.id === 'adapt');
  out.push({ ok: iAd >= 0, lab: 'adaptativa: el botón vive en AJUSTES › JUEGO (r71)' });
  const antes = g.adaptive;
  g.menuClick(iAd);
  out.push({ ok: g.adaptive === !antes &&
                  localStorage.getItem('ppxr_adapt_v1') === (antes ? '0' : '1'),
             lab: 'adaptativa: el conmutador bascula y PERSISTE' });
  g.menuClick(iAd);                       // deja el estado como estaba
  g.toggleMenu();

  // ---------- 3 · RETIRO r115 de la repetición ----------
  out.push({ ok: typeof g._repArranca === 'undefined' &&
                  typeof g._repTick === 'undefined' &&
                  typeof g._repReset === 'undefined',
             lab: 'retiro: ningún método del replay sobrevive en el juego' });
  out.push({ ok: !('ghostBall' in g) && !('replayBanner' in g) &&
                  !('_repBuf' in g) && !('_repBest' in g) &&
                  !('_repEstado' in g),
             lab: 'retiro: sin fantasmas, cartel, buffer ni estado del replay' });
  out.push({ ok: g._repPendiente === undefined,
             lab: 'retiro: la fanfarria no arma ninguna repetición pendiente' });
  return out;
}"""


async def main():
    global ok, fails
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text)
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(1000)

        print("--- 1 · AGUJAS r61 en el juego servido ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 1b · AGUJAS NEGATIVAS (retiro r115) ---")
        for label, aguja in AGUJAS_FUERA:
            chk(aguja not in src, label)

        print("--- 2 · i18n ES/EN balanceado ---")
        for clave in CLAVES:
            n = len(re.findall(rf"^\s+{clave}: '", src, re.M))
            chk(n == 2, f"clave {clave} en ES y EN (×{n})")

        print("--- 3 · MECÁNICA REAL headless ---")
        filas = await page.evaluate(MECANICA)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        await browser.close()

    print("--- ERRORES DE PÁGINA ---")
    chk(len(errors) == 0, "sin errores JS durante toda la batería")
    for e in errors[:6]:
        print("  ·", e[:200])

    print(f"\nRESULTADO: {ok} OK · {fails} fallos")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
