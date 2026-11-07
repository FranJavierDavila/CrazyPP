#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r64 · verificación rápida de la academia editada (pre-QA formal).

Comprueba en vivo (Playwright headless sobre :3000):
  1. cero pageerrors al cargar.
  2. La ACADEMIA arranca sobre el grafo REAL (window.__game):
     panel + mando 3D presentes, pose inicial 'frente'.
  3. Al forzar step 3 vía onTrigger/vaivén real, la pose pasa a 'lado'
     y el panel se desplaza (tick con isPresenting simulado).
  4. Tres saques válidos (con cerrojo anti-doble recuento) → paso 4.
  5. Seis devoluciones → paso 5 (botones).
"""
import asyncio
import sys

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

MECANICA = """async () => {
  const out = [];
  const THREE = await import('three');
  const T = window.__PP_TUT;
  const g = window.__game;
  if (!T || !g) return [{ ok: false, lab: 'modulo/juego presentes' }];

  // juego simulado CON rig real (para grafo + poses + mando 3D)
  const V = (x, y, z) => ({
    x, y, z,
    copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; },
    set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; },
    length() { return Math.hypot(this.x, this.y, this.z); },
  });
  const G = {
    net: { online: false }, champs: null,
    trainV3: null, trainV3Hub: false, tutV1: null, calib: false,
    rules: { state: 'point', server: 'ai', message: '', bestOf: 3,
      startMatch(m) { this.state = 'serve'; this.server = 'player'; } },
    ball: { pos: V(0, 1.0, 0.4), vel: V(0, 0, 0), spin: V(0, 0, 0) },
    renderer: { xr: { isPresenting: true } },
    controllerPaddles: [{ vel: V(0, 0, 0) }, { vel: V(0, 0, 0) }],
    paddleHand: 1, ballHand: 0, tossed: false, mode: 'match',
    sources: [{ gamepad: { buttons: [] } }, { gamepad: { buttons: [] } }],
    audio: { playOsc: () => {}, announce: () => {}, serve: () => {} },
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
    rig: new THREE.Group(),          // RIG REAL para verificar el grafo
  };
  const buscaPanel = () => G.rig.children.filter(ch =>
    ch.type === 'Group' && Math.abs(ch.position.y - 1.52) < 0.01 &&
    Math.abs(ch.position.z + 0.86) < 0.01 && ch.children.length > 0);
  let panelRef = null;               // referencia viva (el panel SE MUEVE con la pose)
  const buscaMando = () => {
    if (!panelRef) return [];
    return panelRef.children.filter(ch => ch.name === 'ppTutMando');
  };
  const partesMando = () => {
    const m = buscaMando()[0];
    if (!m) return [];
    const nombres = [];
    m.traverse(o => { if (o.name && o.name.startsWith('tut_')) nombres.push(o.name); });
    return nombres;
  };

  // 1 · arranque
  T.start(G);
  let e = T.estado();
  out.push({ ok: e.activo === true, lab: 'arranque activo' });
  out.push({ ok: e.pose === 'frente', lab: 'pose inicial frente (' + e.pose + ')' });
  out.push({ ok: buscaPanel().length === 1, lab: 'panel en el rig (1)' });
  panelRef = buscaPanel()[0];
  out.push({ ok: buscaMando().length === 1, lab: 'mando 3D junto al panel (1)' });
  const partes = partesMando();
  out.push({ ok: partes.length === 6, lab: '6 partes del Touch Plus (' + partes.length + '): ' + partes.join(',') });

  // 2 · el mando GIRA
  const m0 = buscaMando()[0];
  // rotation.y vive en el subgrupo tilt->spin: localizamos el hijo giratorio
  const spin = m0.children[0].children[0];
  const y0 = spin.rotation.y;
  for (let i = 0; i < 20; i++) T.tick(0.05);
  out.push({ ok: spin.rotation.y > y0 + 0.3, lab: 'mando giratorio (dY=' + (spin.rotation.y - y0).toFixed(3) + ')' });
  // 3 · resalte del mando por paso
  e = T.estado();
  out.push({ ok: e.mandoHl === 'cuerpo', lab: 'paso 0 resalta el cuerpo (' + e.mandoHl + ')' });
  T.onTrigger(0);   // → paso 1
  T.tick(0.05);     // un tick para que tickMando actualice el resalte
  e = T.estado();
  const hlOk = ['gatillo', 'grip', 'stick', 'botones'].includes(e.mandoHl);
  out.push({ ok: hlOk, lab: 'paso 1 cicla piezas (' + e.mandoHl + ')' });

  // 4 · vaivén → paso 2 → 3 y POSE 'lado' con desplazamiento real
  T.onTrigger(0);   // → paso 2
  G.controllerPaddles[1].vel.set(1.5, 1.2, 1.5);   // pala en mano 1 (derecha)
  for (let i = 0; i < 6; i++) T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.paso === 3, lab: 'vaivén → paso 3 (' + e.paso + ')' });
  out.push({ ok: e.pose === 'lado', lab: 'paso 3 → pose lado (' + e.pose + ')' });
  for (let i = 0; i < 40; i++) T.tick(0.05);       // el lerp lleva el panel al lado
  const px = panelRef.position.x;
  out.push({ ok: px < -0.35, lab: 'panel APARTADO a la izquierda con pala dcha (x=' + px.toFixed(3) + ')' });

  // 5 · tres saques válidos (cerrojo anti doble recuento)
  const saca = () => {
    T.onTrigger(0);                                  // gatillo → toss
    G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
    T.tick(0.016); T.tick(0.016);                    // el 2.º tick NO debe recontar
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);                        // bola muerta → rearme
  };
  saca(); e = T.estado();
  out.push({ ok: e.saq === 1 && e.paso === 3, lab: 'saque 1/3 contado una vez (saq=' + e.saq + ')' });
  saca(); e = T.estado();
  out.push({ ok: e.saq === 2 && e.paso === 3, lab: 'saque 2/3 (saq=' + e.saq + ')' });
  saca(); e = T.estado();
  out.push({ ok: e.paso === 4, lab: 'saque 3/3 → paso 4 (EL INTERCAMBIO)' });
  out.push({ ok: T.estado().pose === 'lado', lab: 'paso 4 sigue en pose lado' });

  // 6 · seis devoluciones → paso 5 (ciclo completo: golpe → bote lejano →
  // profesor devuelve → golpe… como la QA r59)
  for (let i = 0; i < 6; i++) {
    G.ball.pos.set(0.1, 1.1, -1.75); G.ball.vel.set(0, -0.5, -3.0);
    T.tick(0.016);                                   // golpe válido del jugador
    G.ball.pos.set(0.2, 0.9, -2.3); G.ball.vel.set(0, 0.5, -2.0);
    T.tick(0.016);                                   // siembra el bote lejano
    G.ball.vel.y = 0.4;
    T.tick(0.016);                                   // el profesor devuelve
  }
  e = T.estado();
  out.push({ ok: e.paso === 5, lab: '6 devoluciones → paso 5 (hits tras avance=' + e.hitCount + ')' });

  // 7 · A/X → paso 6 y la pose vuelve a 'frente'
  G.paddleHand = 0; T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.paso === 6 && e.pose === 'frente', lab: 'paso 6 → pose frente de nuevo (' + e.pose + ')' });

  // 8 · salida limpia: panel + mando DESAPARECEN del grafo
  T.stop({ aJugar: true, done: true });
  out.push({ ok: buscaPanel().length === 0, lab: 'salida: panel fuera del grafo' });
  out.push({ ok: G.rig.children.length === 0, lab: 'salida: rig sin residuos (' + G.rig.children.length + ')' });
  return out;
}"""


async def main():
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text)
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(900)

        print("--- MECÁNICA r64 sobre el grafo (rig real) ---")
        filas = await page.evaluate(MECANICA)
        ok = fails = 0
        for f in filas:
            print(('  \u2713 ' if f["ok"] else '  \u2717 FALLO: ') + f["lab"])
            if f["ok"]:
                ok += 1
            else:
                fails += 1
        await browser.close()

    print("--- ERRORES DE PÁGINA ---")
    if errors:
        for e in errors[:6]:
            print("  ·", e[:220])
    fails += len(errors)
    print(f"\nRESULTADO: {ok} OK · {fails} fallos")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
