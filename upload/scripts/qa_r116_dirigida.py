#!/usr/bin/env python3
"""QA DIRIGIDA V3.6.106 · sólo las zonas tocadas HOY (regla del dueño:
sin QA integral — lo nuevo y sus interconexiones directas).

1 · Arranque limpio (0 pageerrors).
2 · ACADEMIA paso 4 (EL INTERCAMBIO): la bola del saque que cae al suelo
    SIN cruce vuelve al saque AL INSTANTE (antes: rfFase clavado en
    'vuelo' para siempre = «se queda sin poder hacer nada»). Con el mock
    del juego de la casa (patrón qa_r66_v3658).
3 · PRO TRAINING: drawHub y drawArea «PASE BAJO» se dibujan sin excepción
    y la parrilla de áreas nace en y=236 (fila LOGROS libre).

Uso: python3 scripts/qa_r116_dirigida.py  (necesita dev :3000)
Salida: RESULTADO: N OK · N fallos · exit 0/1
"""
import asyncio
import sys

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'
ok_n = [0]
fail_n = [0]
errs = []


def chk(cond, label):
    if cond:
        ok_n[0] += 1
        print('  ✓ ' + label)
    else:
        fail_n[0] += 1
        print('  ✗ FALLO: ' + label)


# ── 2 · paso 4 del tutorial con el mock de la casa ──────────────────────
TUT_PASO4 = r"""
async () => {
  const out = [];
  const THREE = await import('three');
  const T = window.__PP_TUT;
  if (!T) return [{ ok: false, lab: '__PP_TUT ausente' }];

  const V = (x, y, z) => ({
    x, y, z,
    copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; },
    set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; },
    length() { return Math.hypot(this.x, this.y, this.z); },
  });
  const mkJuego = (mano) => { const G = ({
    net: { online: false }, champs: null,
    trainV3: null, trainV3Hub: false, tutV1: null, calib: false,
    rules: { state: 'point', server: 'ai', message: '', bestOf: 3,
      startMatch(m) { this.state = 'serve'; this.server = 'player'; } },
    ball: { pos: V(0, 1.0, 0.4), vel: V(0, 0, 0), spin: V(0, 0, 0) },
    renderer: { xr: { isPresenting: true } },
    controllerPaddles: [{ vel: V(0, 0, 0) }, { vel: V(0, 0, 0) }],
    paddleHand: mano, tossed: false, mode: 'match',
    sources: [{ gamepad: { buttons: [] } }, { gamepad: { buttons: [] } }],
    audio: { playOsc: () => {}, announce: () => {}, serve: () => {},
             paddle: () => {}, voice: true,
             speakPlan(plan) { this.__voz = (this.__voz || [])
               .concat(plan.map((p) => p.k)); return true; } },
    stickAxis(h) { return this.__stick || { x: 0, y: 0 }; },
    haptic: () => {},
    resetToss() { this.tossed = false; },
    tossFromHand(i, a) { this.tossed = true; },
    feedPracticeBall() { this.__feeds = (this.__feeds || 0) + 1; },
    exitHall() {}, enterCalib() { this.calib = true; },
    exitCalib() { this.calib = false; this.__exitCalib = (this.__exitCalib || 0) + 1; },
    closeMenu() {}, goHomeHall() { return true; },
    toggleMenu() {}, anchorMenu() {}, drawMenu() {},
    hideInstrucciones() {}, _instr: null,
    menuOpen: false, menuPage: 'main',
    calibPanel: { group: { visible: true } },
    confettiBurst: 0,
    scene: new THREE.Scene(),
    rig: new THREE.Group(),
    paddleModelRef: null,
    sceneAddSpy: 0,
  });
  const grips = [new THREE.Group(), new THREE.Group()];
  const mounts = [new THREE.Group(), new THREE.Group()];
  grips[0].add(mounts[0]); grips[1].add(mounts[1]);
  G.grips = grips; G.paddleMounts = mounts; G.handOf = ['left', 'right'];
  return G;
  };

  let G = mkJuego(1);
  G.scene.add(G.rig);
  T.start(G);
  let e = T.estado();
  out.push({ ok: e.activo && e.paso === 0, lab: 'arranque: paso 0' });

  // paso 1 (mandos): gatillo → grip → stick → botones → vaivén (r66)
  T.onTrigger(0); T.tick(0.05);          // paso 0 → paso 1 (subfase 0: GATILLO)
  T.onTrigger(0); T.tick(0.05);          // gatillo hecho → subfase 1 (GRIP)
  G.sources[0].gamepad.buttons = [{ pressed: false }, { pressed: true }];
  T.tick(0.016); T.tick(0.05);           // grip hecho → subfase 2 (STICK)
  G.__stick = { x: 0.7, y: 0 };
  T.tick(0.016); T.tick(0.05);           // stick hecho → subfase 3 (BOTONES)
  G.sources[0].gamepad.buttons[4] = { pressed: true };
  T.tick(0.016); T.tick(0.05);           // botones → subfase 4 (VAIVÉN)
  for (let i = 0; i < 30; i++) T.tick(0.1);
  G.controllerPaddles[G.paddleHand].vel.set(1.5, 1.2, 1.5);
  T.tick(0.2); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.paso === 2, lab: 'paso 1 dominado → paso 2 SAQUE (got ' + e.paso + ')' });

  // paso 2 (SAQUE): demo (espera demoT>2.5) → práctica → 3 saques válidos
  // r71 · botes REALES sobre la mesa (C=-1.6 · TL 1.37 · TW 0.7625 · TY 0.76)
  for (let i = 0; i < 60 && e.demoT < 2.6; i++) { T.tick(0.1); e = T.estado(); }
  T.onTrigger(0); T.tick(0.05);          // demo → práctica (demoT>2.5)
  e = T.estado();
  const enPractica = e.paso === 2;
  for (let s = 0; s < 3; s++) {
    T.onTrigger(0);
    // recién lanzada: bola VIVA subiendo (si no, la muerta del tick
    // anterior la cancela antes de los botes)
    G.ball.pos.set(0.3, 1.15, 0.9); G.ball.vel.set(0, 2.2, -0.6);
    T.tick(0.016);
    // bote 1: TU campo, SOBRE la mesa (z ∈ [-1.54, -0.23], y < 0.88)
    G.ball.pos.set(0.2, 0.85, -0.9); G.ball.vel.set(0, 0.8, -0.5);
    T.tick(0.016);
    // bote 2: campo del rival (z ∈ [-2.97, -1.65])
    G.ball.pos.set(-0.2, 0.85, -2.2); G.ball.vel.set(0, 0.6, -0.5);
    T.tick(0.016);
    e = T.estado();
    // la bola muere → muerta reinicia el latch para el siguiente saque
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);
  }
  e = T.estado();
  out.push({ ok: enPractica && e.paso === 3, lab: 'paso 2 (SAQUE) superado → paso 4 INTERCAMBIO (got ' + e.paso + ' · saques ' + e.saq + ')' });

  // ===== EL ARREGLO DE HOY: bola del saque caída al suelo en 'vuelo' =====
  e = T.estado();
  if (e.paso === 3) {
    T.onTrigger(0);
    G.ball.pos.set(0.3, 1.15, 0.9); G.ball.vel.set(0, 2.2, -0.6);  // recién lanzada
    T.tick(0.016);
    e = T.estado();
    out.push({ ok: e.rfFase === 'vuelo', lab: "gatillo del paso 4 → rfFase='vuelo' (got " + e.rfFase + ')' });
    // la bola CAE AL SUELO sin cruzar (fallaste el golpeo)
    G.ball.pos.set(0.4, 0.02, 2.2); G.ball.vel.set(0, 0, 0);
    T.tick(0.016); T.tick(0.016);
    e = T.estado();
    out.push({ ok: e.rfFase === 'saque', lab: "bola muerta en el suelo → rfFase='saque' AL INSTANTE (got " + e.rfFase + ')' });
    out.push({ ok: G.tossed === false && G.rules.state === 'serve',
               lab: 'toss reiniciado y estado serve: puedes sacar OTRA VEZ' });
    // y el gatillo vuelve a funcionar (no hay bloqueo)
    T.onTrigger(0);
    G.ball.pos.set(0.3, 1.15, 0.9); G.ball.vel.set(0, 2.2, -0.6);
    T.tick(0.016);
    e = T.estado();
    out.push({ ok: e.rfFase === 'vuelo', lab: 'el gatillo vuelve a sacar: PASO 4 DESBLOQUEADO' });
  } else {
    out.push({ ok: false, lab: 'no se alcanzó el paso 4 (paso=' + e.paso + ')' });
  }
  try { T.stop({ done: false }); } catch (err) { /* */ }
  return out;
};
"""

# ── 3 · PRO TRAINING: hub y área se dibujan; parrilla en y=236 ──────────
TRAIN_HUB = r"""
() => {
  const G = window.__PP_GAME, T = window.__PP_TRAIN;
  const cv = document.createElement('canvas');
  cv.width = 1024; cv.height = 1456;
  const c = cv.getContext('2d');
  const rects = [];
  const btn = (id, x, y, w, h) => { rects.push({ id, x, y, w, h }); };
  const label = () => {};
  let errHub = '', errArea = '', y1a = null;
  try {
    T.drawHub(G, c, rects, btn, label);
    const a1 = rects.find((r) => r.id === 'trv3:area:dir');
    y1a = a1 ? a1.y : null;
  } catch (e) { errHub = String(e && e.message || e); }
  let errArea2 = '';
  try {
    T.menuAction(G, 'area:alt');             // área ALTURA: PASE BAJO (t2a)
    T.drawArea(G, c, rects, btn, label);
  } catch (e) { errArea2 = String(e && e.message || e); }
  return { errHub, errArea2, y1a, nRects: rects.length };
};
"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded')
        await page.wait_for_function("() => window.__PP_GAME && window.__PP_TUT && window.__PP_TRAIN",
                                     timeout=60000)

        print('== 1 · ARRANQUE: 0 pageerrors ==')
        await page.wait_for_timeout(1200)
        chk(len(errs) == 0, f"0 pageerrors en arranque ({len(errs)})")

        print('== 2 · ACADEMIA PASO 4: bola del saque al suelo → OTRA VEZ al instante ==')
        res = await page.evaluate(TUT_PASO4)
        for r in res:
            chk(r.get('ok'), r.get('lab', '?'))

        print('== 3 · PRO TRAINING: hub (y=236) y «PASE BAJO» sin excepción ==')
        r = await page.evaluate(TRAIN_HUB)
        chk(r.get('errHub') == '' and r.get('y1a') == 236,
            f"drawHub sin excepción y 1.ª tarjeta en y=236 (got {r.get('y1a')}) {r.get('errHub')}")
        chk(r.get('errArea2') == '' and r.get('nRects', 0) > 10,
            f"drawArea «PASE BAJO» sin excepción ({r.get('nRects')} rects) {r.get('errArea2')}")

        await browser.close()

    print(f"\nRESULTADO: {ok_n[0]} OK · {fail_n[0]} fallos")
    if errs:
        print('PAGEERRORS:', errs[:3])
    sys.exit(1 if (fail_n[0] or errs) else 0)


if __name__ == '__main__':
    asyncio.run(main())
