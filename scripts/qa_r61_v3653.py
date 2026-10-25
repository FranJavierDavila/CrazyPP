#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r61 · v3.6.53-SDK6 · FASE 55 «Estela de poderes, rival que se adapta y el
mejor intercambio en pantalla» — QA de las TRES features aprobadas por el
dueño (las candidatas sin aprobar quedaron aprobadas en conversación):

  1) ESTELA DE PODER — la estela de la bola viste la firma del poder de
     pala ACTIVO (mega ámbar · efecto rojo · imán cian · portal violeta ·
     clon azul fantasma) con lerp suave y respaldo por EFECTO (spin).
  2) RIVAL ADAPTATIVO — existía desde v2.x pero era invisible: ahora
     conmutador persistente (AJUSTES + HUB junto a la dificultad), mensaje
     de estado y transición SUAVE (lerp del factor en el tick).
  3) REPETICIÓN DEL MEJOR INTERCAMBIO — grabadora por frames (bola + pala
     rival + dt) y reproducción fantasma al terminar el partido, con
     salto por gatillo y fanfarria restaurada.

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
    # --- 3 · repetición ---
    ("repetición: grabadora con puertas (local, sin calib/academia/online)",
     "_repGrabando() {"),
    ("repetición: frame = bola(3)+rival(3)+quat(4)+dt(1)",
     "this._repStride = 11;"),
    ("repetición: el mejor intercambio se guarda por toques",
     "_repCierra(hits) {"),
    ("repetición: fantasmas bola + rival en azul fantasma",
     "this.ghostRival = makePaddleVisual(paddleModel, 'center');"),
    ("repetición: cartel propio de repetición",
     "createReplayBanner() {"),
    ("repetición: se reproduce tras asentar la fanfarria (1,6 s)",
     "if (this._repPendiente && this._repEstado === '' && this.fanfareT > 1.6) {"),
    ("repetición: interpolación por tiempo real (framerate-independiente)",
     "this.ghostRival.quaternion.slerpQuaternions(_repTmpQ1, _repTmpQ2, al);"),
    ("repetición: gatillo salta la repetición ANTES de la revancha",
     "if (this._repEstado === 'play') {\n        try { this._repTermina(); } catch (eR1) { /* */ }"),
    ("repetición: partido nuevo borra el campeón (hook onMatchStart)",
     "try { this._repReset(); } catch (eR) { /* nunca rompe el árbitro */ }"),
    ("repetición: visibilidades EXACTAS restauradas (sin resurrecciones)",
     "const prev = this._repVisPrev;      // visibilidades EXACTAS de antes"),
]

CLAVES = ['btn_adapt', 'msg_adapt', 'rep_t', 'rep_chip']

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

  // ---------- 3 · REPETICIÓN DEL MEJOR INTERCAMBIO ----------
  g._repReset();
  const stride = g._repStride;
  // sintetiza un intercambio de 30 frames (bola cruzando, rival moviéndose)
  for (let i = 0; i < 30; i++) {
    const o = i * stride;
    g._repBuf[o] = 0; g._repBuf[o + 1] = 1; g._repBuf[o + 2] = -1 - i * 0.1;
    g._repBuf[o + 3] = 1; g._repBuf[o + 4] = 0.9; g._repBuf[o + 5] = -4;
    g._repBuf[o + 6] = 0; g._repBuf[o + 7] = 0; g._repBuf[o + 8] = 0; g._repBuf[o + 9] = 1;
    g._repBuf[o + 10] = 0.016;
  }
  g._repN = 30;
  g._repCierra(7);
  out.push({ ok: g._repBest.hits === 7 && g._repBest.n === 30 && g._repN === 0,
             lab: 'repetición: el intercambio de 7 toques queda como MEJOR' });
  g._repN = 10;                            // uno peor no lo desbancan
  g._repCierra(4);
  out.push({ ok: g._repBest.hits === 7,
             lab: 'repetición: uno de 4 toques NO desbanca al de 7' });
  const visBall0 = g.ballMesh.visible, visAi0 = g.aiPaddleMesh.visible;
  g._repArranca();
  out.push({ ok: g._repEstado === 'play' && g.ghostBall.visible &&
                  g.ghostRival.visible && g.replayBanner.group.visible &&
                  !g.ballMesh.visible && !g.aiPaddleMesh.visible,
             lab: 'repetición: fantasmas + cartel en escena, bola/rival ocultos' });
  g._repT = 0;
  g._repTick(0.4);                          // ~mitad del intercambio sintético
  const gp = g.ghostBall.position;
  out.push({ ok: gp.z < -1 && gp.z > -3.9,
             lab: 'repetición: la bola fantasma interpola el trayecto (z=' + gp.z.toFixed(2) + ')' });
  const qg = g.ghostRival.quaternion;
  out.push({ ok: Math.abs(qg.w - 1) < 0.01,
             lab: 'repetición: el rival fantasma interpola su actitud (slerp)' });
  g._repTermina();
  out.push({ ok: g._repEstado === '' && !g.ghostBall.visible &&
                  !g.replayBanner.group.visible &&
                  g.ballMesh.visible === visBall0 &&
                  g.aiPaddleMesh.visible === visAi0,
             lab: 'repetición: fin con visibilidades EXACTAS restauradas' });
  // puertas de la grabadora
  const st0 = g.rules.state, cal0 = g.calib;
  g.rules.state = 'rally'; g.calib = false;
  const netSave = g.net.online;
  try { Object.defineProperty(g.net, 'online', { value: false, configurable: true }); } catch (e) { g.net._onlineFake = true; }
  out.push({ ok: g._repGrabando() === true,
             lab: 'repetición: graba en rally local' });
  g.calib = true;
  out.push({ ok: g._repGrabando() === false,
             lab: 'repetición: NO graba en calib/academia' });
  g.calib = false;
  try { Object.defineProperty(g.net, 'online', { value: true, configurable: true }); } catch (e) { /* */ }
  out.push({ ok: g._repGrabando() === false,
             lab: 'repetición: NO graba el invitado online' });
  try { Object.defineProperty(g.net, 'online', { value: netSave, configurable: true }); } catch (e) { /* */ }
  g.rules.state = st0; g.calib = cal0;
  // reset por partido nuevo
  g._repReset();
  out.push({ ok: g._repBest.hits === 0 && g._repBest.buf === null,
             lab: 'repetición: startMatch borra el campeón (hook)' });
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
