#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r62 · v3.6.54-SDK6 · FASE 56 «Sonido real, háptica que mide y el momento
cine» — QA de las features de la ronda. r115 · RE-ANCA HONESTA: la cámara
lenta de la REPETICIÓN (feature 3a de la r62) se retiró con el replay que
suprimió el dueño — la capa verifica ahora su AUSENCIA; la dilatación de la
BOLA DE PARTIDO (match point) sigue viva:

  1) SONIDO REAL — muestras por síntesis modal física (bola de 40 mm contra
     cada superficie) incrustadas en base64, decodificadas una sola vez y
     tocadas con playbackRate mapeado a la VELOCIDAD del impacto + jitter
     anti-ametralladora. El CANTO estrena «ping» metálico propio (e.edge).
     Fallback: la síntesis de siempre (el audio NUNCA rompe el juego).
  2) HÁPTICA ESCALADA — intensidad Y duración crecen con la velocidad real
     en los golpes (rally + saque). ARKANOID conserva su refuerzo v2.44.
  3) CÁMARA LENTA — la BOLA DE PARTIDO se dilata en vivo (física 0,34× con
     regreso suave ~1,15 s, sólo local). La cámara lenta del replay
     (REP_SLOWMO + pastilla ámbar) se retiró en r115 con la repetición.

Uso: python3 scripts/qa_r62_v3654.py        (servidor dev en :3000)
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
    # --- 1 · sonido real (c03 + c05 + c12) ---
    ("sfx: muestras incrustadas en base64 (const módulo)",
     "const PP_SFX_REALES_B64 = {"),
    ("sfx: las 5 superficies presentes",
     "  suelo: '"),
    ("sfx: decodificador asíncrono único",
     "_loadSfxReales(ctx) {"),
    ("sfx: umbral mesa+pala para activar el camino real",
     "if (ok.mesa && ok.pala) {"),
    ("sfx: playbackRate acotado al disparar",
     "src.playbackRate.value = Math.max(0.5, Math.min(2.2, rate));"),
    ("sfx: tono por impacto + jitter anti-ametralladora",
     "const jit = 0.985 + Math.random() * 0.03;"),
    ("sfx: PALA real primero, síntesis de respaldo",
     "if (this._playReal('pala', pan, 0.72 * s, this._sfxRate(strength, 0.84, 1.34))) return;"),
    ("sfx: MESA real «pock»",
     "if (this._playReal('mesa', pan, 0.5 * s, this._sfxRate(strength, 0.86, 1.30))) return;"),
    ("sfx: CANTO metálico con cola (método nuevo)",
     "tableEdge(pan, strength) {"),
    ("sfx: RED con la fuerza del golpe",
     "if (this._playReal('red', pan, 0.5 * s, this._sfxRate(s, 0.88, 1.22))) return;"),
    ("sfx: SUELO sordo",
     "if (this._playReal('suelo', pan, 0.42 * s, this._sfxRate(s, 0.86, 1.18))) return;"),
    ("sfx: c05 marca el bote de CANTO",
     "events.push({ type: 'table', edge: true, side: pos.z > C ? 'player' : 'ai', speed: 1.5, pos: pos.clone() });"),
    ("sfx: el juego despacha el canto a su ping",
     "this.audio.tableEdge(pan, Math.min(1, 0.45 + e.speed / 8));"),
    ("sfx: la red recibe la velocidad del evento",
     "this.audio.net(pan, Math.min(1, (e.speed || 0.8) / 5));"),
    # --- 2 · háptica escalada ---
    ("háptica: intensidad de rally escalada por velocidad",
     "Math.min(1, (arkOn ? 0.68 : 0.35) + sH * 0.65),"),
    ("háptica: DURACIÓN de rally escalada (34→96 ms)",
     "arkOn ? 85 : Math.round(34 + 62 * sH));"),
    ("háptica: SAQUE escalado (intensidad y duración)",
     "Math.min(1, 0.45 + sS * 0.5), Math.round(55 + 45 * sS));"),
    # --- 3 · cámara lenta (r115: la del replay se retiró con él) ---
    ("cine: reloj de dilatación en el tick",
     "if (this._dilT > 0) {"),
    ("cine: regreso suave del factor (punch 0,34 → 1)",
     "this._dilF = 1 + (0.34 - 1) * Math.min(1, _kDil * 2.2);"),
    ("cine: game-over arma la dilatación SOLO local",
     "if (!this.net.online) this._dilArranca();"),
    # r79: el call lleva el observador de traspaso _xNet (mismo dt dilatado)
    ("cine: la física de la bola recibe el dt dilatado",
     "stepPhysics(dt * this._dilF, this.ball, pads, this.events, _xNet);"),
]

NEGATIVAS = [
    ("háptica: la fija antigua del rally (0.5 + speed/9) retirada",
     "Math.min(1, (arkOn ? 0.68 : 0.5) + e.speed / 9),"),
    ("háptica: la fija antigua del saque (0.8/90) retirada",
     "this.haptic(e.paddleIndex ?? this.paddleHand, 0.8, 90);"),
    ("sfx: la llamada de red sin fuerza retirada",
     "this.audio.net(pan);"),
    ("r115: la cámara lenta del replay retirada con la repetición",
     "const REP_SLOWMO = 0.5;"),
    ("r115: el reloj del replay retirado",
     "this._repT += dt * REP_SLOWMO;"),
    ("r115: la pastilla ámbar del cartel retirada",
     "const txtSlow = T('rep_slow');"),
]

CLAVES = []

MECANICA = """async () => {
  const out = [];
  const g = window.__game;

  // ---------- 1 · SONIDO REAL ----------
  g.audio.hadGesture = true;
  g.audio._create();
  await new Promise(r => setTimeout(r, 600));
  out.push({ ok: !!g.audio.ctx && g.audio.ctx.state === 'running',
             lab: 'sfx: contexto de audio creado (running)' });
  // sondeo con plazo: la decodificación es asíncrona y el RAF headless va a
  // trompos — el INVARIANTE es que estén las 5, no el microtiming
  let b = g.audio._sfxBufs;
  const cinco = (x) => !!(x && x.mesa && x.pala && x.canto && x.red && x.suelo);
  for (let i = 0; i < 30 && !cinco(b); i++) {
    await new Promise(r => setTimeout(r, 300));
    b = g.audio._sfxBufs;
  }
  out.push({ ok: cinco(b),
             lab: 'sfx: las 5 muestras decodificadas (' + (b ? Object.keys(b).join('+') : 'null') + ')' });
  if (b) {
    const durs = [b.mesa.duration, b.pala.duration, b.canto.duration,
                  b.red.duration, b.suelo.duration];
    out.push({ ok: Math.abs(durs[0] - 0.070) < 0.005 && Math.abs(durs[1] - 0.060) < 0.005 &&
                    Math.abs(durs[2] - 0.170) < 0.005 && Math.abs(durs[3] - 0.090) < 0.005 &&
                    Math.abs(durs[4] - 0.100) < 0.005,
               lab: 'sfx: duraciones de diseño (70/60/170/90/100 ms)' });
    out.push({ ok: g.audio._playReal('mesa', 0, 0.5, 1.0) === true,
               lab: 'sfx: _playReal dispara la muestra (true)' });
    // tono por impacto: suave ≈ lo · smash ≈ hi · jitter ±1,5%
    const lo = g.audio._sfxRate(0, 0.86, 1.30);
    const hi = g.audio._sfxRate(1, 0.86, 1.30);
    out.push({ ok: lo > 0.845 && lo < 0.875 && hi > 1.283 && hi < 1.317,
               lab: 'sfx: tono por impacto en banda (lo ' + lo.toFixed(3) + ' · hi ' + hi.toFixed(3) + ')' });
    const d1 = g.audio._sfxRate(0.5, 0.86, 1.30);
    const d2 = g.audio._sfxRate(0.5, 0.86, 1.30);
    out.push({ ok: d1 !== d2,
               lab: 'sfx: jitter anti-ametralladora (dos llamadas difieren)' });
  }
  // fallback: sin buffers, la síntesis responde sin romper nada
  const bufsReales = g.audio._sfxBufs;
  g.audio._sfxBufs = null;
  out.push({ ok: g.audio._playReal('mesa', 0, 0.5, 1.0) === false,
             lab: 'sfx: sin muestras, _playReal devuelve false (fallback)' });
  let sintesisViva = true;
  try { g.audio.tableBounce(0, 0.5); g.audio.paddle(0, 0.5);
        g.audio.net(0, 0.5); g.audio.thud(0, 0.5); g.audio.tableEdge(0, 0.5); }
  catch (e) { sintesisViva = false; }
  out.push({ ok: sintesisViva,
             lab: 'sfx: la síntesis de respaldo no lanza NADA (audio nunca rompe)' });
  g.audio._sfxBufs = bufsReales;
  // despacho real: canto → tableEdge · llano → tableBounce · red con fuerza
  const rec = {};
  for (const k of ['tableEdge', 'tableBounce', 'net']) {
    rec[k] = [];
    const orig = g.audio[k].bind(g.audio);
    g.audio[k] = (pan, s) => rec[k].push(s);
  }
  g._lastBounceSfx = 0;
  g.processEvents([{ type: 'table', edge: true, speed: 1.5, pos: { x: 0.1, y: 1, z: -1 } }]);
  g._lastBounceSfx = 0;
  g.processEvents([{ type: 'table', speed: 4.2, pos: { x: -0.2, y: 1, z: -1 } }]);
  g._lastBounceSfx = 0;
  g.processEvents([{ type: 'net', speed: 2.5, pos: { x: 0, y: 1, z: 0 } }]);
  out.push({ ok: rec.tableEdge.length === 1 && rec.tableBounce.length === 1 &&
                  Math.abs(rec.net[0] - 0.5) < 0.01,
             lab: 'sfx: despacho real canto/llano/red (red fuerza ' + (rec.net[0] || 0).toFixed(2) + ')' });
  for (const k of ['tableEdge', 'tableBounce', 'net']) delete g.audio[k];

  // ---------- 2 · HÁPTICA ESCALADA ----------
  const vibras = [];
  const hapticReal = g.haptic.bind(g);
  g.haptic = (idx, f, d) => vibras.push([f, d]);
  const st0 = g.rules.state;
  g.rules.state = 'serve';                      // no-arkanoid
  g._lastBounceSfx = 0;
  g.processEvents([{ type: 'paddle', who: 'player', speed: 0.9,
                     pos: { x: 0, y: 1, z: 0 }, paddleIndex: 0 }]);
  g._lastBounceSfx = 0;
  g.processEvents([{ type: 'paddle', who: 'player', speed: 9,
                     pos: { x: 0, y: 1, z: 0 }, paddleIndex: 0 }]);
  const suave = vibras[0], smash = vibras[1];
  out.push({ ok: !!suave && !!smash && suave[0] < smash[0] && suave[1] < smash[1],
             lab: 'háptica: dejada (' + suave[0].toFixed(2) + '/' + suave[1] + ' ms) < smash (' +
                  smash[0].toFixed(2) + '/' + smash[1] + ' ms)' });
  out.push({ ok: Math.abs(smash[0] - 1) < 0.01 && smash[1] === 96,
             lab: 'háptica: el smash llega al techo (intensidad 1 · 96 ms)' });
  g.rules.state = 'arkanoid';
  g._lastBounceSfx = 0;
  g.processEvents([{ type: 'paddle', who: 'player', speed: 0.9,
                     pos: { x: 0, y: 1, z: 0 }, paddleIndex: 0 }]);
  out.push({ ok: vibras[2][1] === 85,
             lab: 'háptica: ARKANOID conserva su refuerzo v2.44 (85 ms)' });
  g.rules.state = st0;
  g.haptic = hapticReal;

  // ---------- 3 · CÁMARA LENTA ----------
  // 3a · dilatación de la bola de partido (reloj REAL del bucle)
  out.push({ ok: g._dilT === 0 && g._dilF === 1,
             lab: 'cine: sin dilatación el tiempo corre normal (_dilF=1)' });
  g._dilArranca();
  out.push({ ok: g._dilT === 1.15,
             lab: 'cine: _dilArranca arma 1,15 s de dilatación' });
  await new Promise(r => setTimeout(r, 300));
  // zona-punch: mientras _dilT > 0,52 el factor es 0,34 SEA CUAL SEA el
  // ritmo del RAF headless (invariante del diseño, no el microtiming;
  // comparación con tolerancia — 1+(0.34-1) no es bit-exacto a 0.34)
  out.push({ ok: g._dilT > 0 && Math.abs(g._dilF - 0.34) < 1e-9,
             lab: 'cine: la dilatación pega el punch (factor ' + g._dilF.toFixed(3) + ' · reloj ' + g._dilT.toFixed(2) + ')' });
  // sondeo LARGO: el reloj real agota su ventana (el RAF headless puede ir
  // a ~6 fps o menos con la suite cargada — 1,15 s de juego pueden costar
  // >20 s reales; plazo de 60 s para cualquier carga)
  for (let i = 0; i < 200 && g._dilT > 0; i++) {
    await new Promise(r => setTimeout(r, 300));
  }
  out.push({ ok: g._dilT === 0 && g._dilF === 1,
             lab: 'cine: regreso completo a tiempo normal (sin salto brusco)' });
  // 3b · r115: la repetición a la mitad se RETIRÓ con el replay
  out.push({ ok: typeof g._repTick === 'undefined' && typeof g._repArranca === 'undefined',
             lab: 'cine: el motor del replay ya no existe (retiro r115)' });
  // 3c · la dilatación NO se arma online (guard)
  const onlineSave = g.net.online;
  try { Object.defineProperty(g.net, 'online', { value: true, configurable: true }); } catch (e) { /* */ }
  g._dilT = 0;
  g.processIntents([{ type: 'game-over', winner: 'player' }]);
  out.push({ ok: g._dilT === 0,
             lab: 'cine: online NO se dilata (la bola la conduce el rival)' });
  try { Object.defineProperty(g.net, 'online', { value: onlineSave, configurable: true }); } catch (e) { /* */ }
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

        print("--- 1 · AGUJAS r62 en el juego servido ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 2 · NEGATIVAS (lo viejo retirado) ---")
        for label, aguja in NEGATIVAS:
            chk(aguja not in src, label)

        print("--- 3 · i18n ES/EN balanceado ---")
        for clave in CLAVES:
            n = len(re.findall(rf"^\s+{clave}: '", src, re.M))
            chk(n == 2, f"clave {clave} en ES y EN (×{n})")

        print("--- 4 · MECÁNICA REAL headless ---")
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
