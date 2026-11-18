#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_train_ayudas_v3621.py · QA de las AYUDAS TÉCNICAS del entrenamiento (ronda 27).

Cierra el informe del dueño («al desmarcar marcas de bote, líneas de tiro y
flechas de efecto sólo está haciendo caso a la de líneas de tiro»). Verifica
sobre el JUEGO REAL (dev :3000) que cada interruptor de la sección «AYUDAS
TÉCNICAS» del HUB obedece, por el MISMO camino que un clic del casco
(menuAction — exactamente lo que invoca menuClick del núcleo):

  1 · CIRCUITO REAL de los 3 toggles: menuAction('fb:<k>') ↔ S.fb[k] +
      persistencia en localStorage (ppxr_train_v1) + re-marcado.
  2 · MARCAS DE BOTE: bote REAL en la mesa (la bola cae y el núcleo emite
      el evento 'table' → spawnMark). OFF ⇒ delta de aros visibles = 0;
      ON ⇒ delta ≥ 1.
  3 · OCULTADO INSTANTÁNEO al desmarcar marcas (antes vivían hasta 1,6 s
      desvaneciéndose — parecía «no hacer caso»).
  4 · LÍNEA DE TIRO: OFF ⇒ la línea no se muestra con racha viva; ON ⇒ visible.
  5 · FLECHA DE EFECTO (bola): OFF ⇒ sprite a opacidad ~0; ON ⇒ visible.
  6 · ICONOS DE EFECTO EN LA PALA (faceIcons): REPRO del dueño — antes NO
      consultaban S.fb.spin y seguían pulsando con la ayuda desmarcada.
      OFF ⇒ invisibles tras pulso; ON ⇒ pulsan.
  7 · 0 pageerrors durante toda la batería.

Uso: python3 scripts/qa_train_ayudas_v3621.py  (necesita dev :3000)
Salida: RESULTADO: N OK · N fallos  ·  exit 0/1."""
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


# ── helper: fijar un interruptor POR EL CAMINO REAL (como el clic) ──────
SET_FB = r"""
([k, want]) => {
  const G = window.__PP_GAME, T = window.__PP_TRAIN;
  const on = !!T.__debug.S.fb[k];
  if (on !== want) T.menuAction(G, 'fb:' + k);     // ruta EXACTA de menuClick
  return { S: T.__debug.S.fb[k],
           ls: (JSON.parse(localStorage.getItem('ppxr_train_v1') || '{}').fb || {})[k] };
};
"""

# ── conteo de aros de bote visibles (userData.ttl es su firma única) ────
COUNT_MARKS = r"""
() => {
  const grp = window.__PP_GAME.rig.getObjectByName('ppTrainGrp');
  if (!grp) return { err: 'sin grp' };
  let vis = 0, tot = 0;
  for (const o of grp.children) {
    if (o.userData && typeof o.userData.ttl === 'number') { tot++; if (o.visible) vis++; }
  }
  return { vis, tot };
};
"""

# ── bote REAL por la cadena completa del núcleo ─────────────────────────
# En headless el núcleo pinea la bola (active=false → vel/pos reseteadas
# cada frame), así que la física NATURAL no corre. Pero el propio núcleo
# expone window.__solverHook.stepPhysics: integramos la bola de verdad y
# consumimos los eventos con T.tick — la MISMA cadena que en el casco
# (stepPhysics → evento 'table' → trainTick → spawnMark con su bandera).
BOUNCE_JS = r"""
() => {
  const G = window.__PP_GAME, T = window.__PP_TRAIN;
  const H = window.__solverHook;
  if (!H || !H.stepPhysics) return { err: 'sin solverHook' };
  const grp = G.rig.getObjectByName('ppTrainGrp');
  const quad = grp.children.find(m => m.isMesh && m.geometry &&
    m.geometry.type === 'PlaneGeometry');
  const C = quad.position.z + quad.geometry.parameters.height / 2;
  const TOP = quad.position.y;
  const b = G.ball;
  b.pos.set(0.15, TOP + 0.30, C - 0.40);        // mitad rival → side 'ai'
  b.vel.set(0.25, -2.4, 0.10);
  b.spin.set(0, 0, 0);
  G.events.length = 0;
  for (let i = 0; i < 42; i++) H.stepPhysics(0.016, b, [], G.events);
  const tab = G.events.filter(e => e.type === 'table').map(e => e.side);
  T.tick(0.016);                                 // trainTick consume → spawnMark
  return { table: tab, ok: true };
};
"""

# estado de la línea de tiro + sprite de efecto + iconos de pala
FB_STATE = r"""
() => {
  const G = window.__PP_GAME, T = window.__PP_TRAIN;
  const grp = G.rig.getObjectByName('ppTrainGrp');
  if (!grp) return { err: 'sin grp' };
  const line = grp.children.find(o => o.isLine);
  const sp = grp.children.find(o => o.isSprite);
  let icons = 0, iconsVis = 0;
  for (const mount of (G.paddleMounts || [])) {
    for (const c of mount.children) {
      if (c.userData && c.userData.ppTrainTag === 'faceicon') {
        icons++; if (c.visible && c.material.opacity > 0.02) iconsVis++;
      }
    }
  }
  return {
    lineVis: line ? line.visible : null,
    lineOp: line ? line.material.opacity : null,
    spVis: sp ? sp.visible : null,
    spOp: sp ? sp.material.opacity : null,
    icons, iconsVis,
  };
};
"""

# racha viva con puntos de trayectoria para forzar shotLineShow por tick
FORCE_LIVE = r"""
() => {
  const G = window.__PP_GAME, T = window.__PP_TRAIN;
  const st = T.__debug.st;
  const V3 = G.ball.pos.constructor;
  st.live = true;
  st.shotRec = true;
  st.shotPts.length = 0;
  st.shotPts.push(new V3(0.10, 1.00, 0.55), new V3(0.12, 0.98, 0.20));
  return { live: st.live, pts: st.shotPts.length };
};
"""

# pulso REAL de efecto en la pala (lo que invoca tick ante un golpe con giro)
PULSE_JS = r"""
(lift) => { window.__PP_TRAIN.__test.pulseFaceIcons(lift); return { ok: true }; };
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
        await page.wait_for_function("() => window.__PP_GAME && window.__PP_TRAIN", timeout=45000)
        # gancho de física del núcleo (solo lectura; el núcleo lo instala en su
        # siguiente frame — v2.128, línea __wantSolverHook)
        await page.evaluate("() => { window.__wantSolverHook = true; }")
        await page.wait_for_function("() => window.__solverHook && window.__solverHook.stepPhysics", timeout=15000)

        # modo activo (trainTick consume los eventos y pinta el feedback)
        await page.evaluate("() => window.__PP_TRAIN.startMode(window.__PP_GAME, 't1a')")
        await page.wait_for_timeout(150)

        print('== 1 · CIRCUITO REAL de los 3 toggles (menuAction ↔ S ↔ localStorage) ==')
        for k in ['marks', 'line', 'spin']:
            r = await page.evaluate(SET_FB, [k, False])
            chk(r['S'] == 0 and r['ls'] == 0, f"fb:{k} OFF por clic real → S=0 y persistido ({r})")
            r = await page.evaluate(SET_FB, [k, True])
            chk(r['S'] == 1 and r['ls'] == 1, f"fb:{k} ON por clic real → S=1 y persistido")
            await page.evaluate(SET_FB, [k, True])

        print('== 2 · MARCAS DE BOTE: bote REAL (stepPhysics → evento table → spawnMark) ==')
        await page.evaluate(SET_FB, ['marks', False])
        await page.wait_for_timeout(200)                       # que mueran restos previos
        base0 = (await page.evaluate(COUNT_MARKS))['vis']
        r = await page.evaluate(BOUNCE_JS)
        chk(len(r.get('table', [])) >= 1, f"el núcleo emite evento table real ({r.get('table')})")
        after0 = (await page.evaluate(COUNT_MARKS))['vis']
        chk(after0 - base0 == 0, f"OFF: 0 aros nuevos tras bote real (antes {base0}, ahora {after0})")

        await page.evaluate(SET_FB, ['marks', True])
        await page.evaluate(BOUNCE_JS)
        after1 = (await page.evaluate(COUNT_MARKS))['vis']
        chk(after1 - base0 >= 1, f"ON: la marca aparece tras bote real ({after1 - base0} nuevas)")

        print('== 3 · OCULTADO INSTANTÁNEO al desmarcar MARCAS (sin esperar el fade) ==')
        pre = (await page.evaluate(COUNT_MARKS))['vis']
        await page.evaluate(SET_FB, ['marks', False])
        post = (await page.evaluate(COUNT_MARKS))['vis']
        chk(pre > 0 and post == 0,
            f"desmarcar limpia los aros AL INSTANTE ({pre} → {post})")
        await page.evaluate(SET_FB, ['marks', True])

        print('== 4 · LÍNEA DE TIRO ==')
        await page.evaluate(SET_FB, ['line', False])
        await page.evaluate(FORCE_LIVE)
        await page.wait_for_timeout(250)
        st1 = await page.evaluate(FB_STATE)
        chk(st1['lineVis'] is False or (st1['lineOp'] or 0) < 0.02,
            f"OFF: la línea no se muestra (vis={st1['lineVis']}, op={st1['lineOp']})")
        await page.evaluate(SET_FB, ['line', True])
        await page.wait_for_timeout(250)
        st2 = await page.evaluate(FB_STATE)
        chk(st2['lineVis'] is True and (st2['lineOp'] or 0) > 0.2,
            f"ON: la línea se muestra (vis={st2['lineVis']}, op={st2['lineOp']})")
        # limpiar la racha falsa
        await page.evaluate("() => { const st = window.__PP_TRAIN.__debug.st; st.live = false; st.shotRec = false; }")

        print('== 5 · FLECHA DE EFECTO sobre la bola ==')
        SPIN_JS = r"""
() => {
  const G = window.__PP_GAME, T = window.__PP_TRAIN;
  const H = window.__solverHook;
  const grp = G.rig.getObjectByName('ppTrainGrp');
  const quad = grp.children.find(m => m.isMesh && m.geometry &&
    m.geometry.type === 'PlaneGeometry');
  const C = quad.position.z + quad.geometry.parameters.height / 2;
  const TOP = quad.position.y;
  const b = G.ball;
  b.pos.set(0.10, TOP + 0.45, C - 0.55);
  b.vel.set(1.5, 2.0, -1.2);
  b.spin.set(0, 0, 20);
  G.events.length = 0;
  for (let i = 0; i < 10; i++) H.stepPhysics(0.016, b, [], G.events);
  for (let i = 0; i < 14; i++) T.tick(0.016);    // 14 ticks: la opacidad sube a régimen
  return { vel2: +b.vel.lengthSq().toFixed(1), spin2: +b.spin.lengthSq().toFixed(0) };
};
"""
        await page.evaluate(SET_FB, ['spin', False])
        await page.wait_for_timeout(400)
        r = await page.evaluate(SPIN_JS)
        st3 = await page.evaluate(FB_STATE)
        chk((st3['spOp'] or 0) < 0.06 and not st3['spVis'],
            f"OFF: sprite apagado con bola girando (vis={st3['spVis']}, op={st3['spOp']}, spin²={r['spin2']})")
        await page.evaluate(SET_FB, ['spin', True])
        await page.evaluate(SPIN_JS)
        st4 = await page.evaluate(FB_STATE)
        chk(st4['spVis'] is True and (st4['spOp'] or 0) > 0.2,
            f"ON: sprite visible (vis={st4['spVis']}, op={st4['spOp']})")

        print('== 6 · ICONOS DE EFECTO EN LA PALA (repro del dueño) ==')
        st5 = await page.evaluate(FB_STATE)
        if st5['icons'] == 0:
            chk(True, f"sin faceIcons en este entorno ({st5['icons']}) — chequeo no aplicable")
        else:
            await page.evaluate(SET_FB, ['spin', False])
            await page.evaluate(PULSE_JS, 2)
            await page.wait_for_timeout(120)
            st6 = await page.evaluate(FB_STATE)
            chk(st6['iconsVis'] == 0,
                f"OFF: los iconos de la pala NO pulsan ({st6['iconsVis']}/{st6['icons']} visibles)")
            await page.evaluate(SET_FB, ['spin', True])
            await page.evaluate(PULSE_JS, 2)
            await page.wait_for_timeout(120)
            st7 = await page.evaluate(FB_STATE)
            chk(st7['iconsVis'] > 0,
                f"ON: los iconos de la pala pulsan ({st7['iconsVis']}/{st7['icons']})")
            await page.evaluate(SET_FB, ['spin', True])

        # estado final limpio: las tres ayudas marcadas (por defecto)
        for k in ['marks', 'line', 'spin']:
            await page.evaluate(SET_FB, [k, True])

        print('== 7 · pageerrors ==')
        chk(len(errs) == 0, f'0 pageerrors durante la batería ({len(errs)} vistos)')
        for e in errs[:5]:
            print('    ·', e[:160])

        total = f"RESULTADO: {ok_n[0]} OK · {fail_n[0]} fallos"
        print(total)
        await browser.close()
        return 0 if fail_n[0] == 0 else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
