#!/usr/bin/env python3
"""Búsqueda de gestos de saque REALISTAS cuya salida física pura sea un saque
legal (para fijar la rejilla del caso 1 de la QA V3.1.0-SRV2).

Geometría realista: contacto tras la línea de fondo (z > -0.23), bola delante
del CENTRO de la hoja, cara ligeramente CERRADA (pitch positivo = normal
abajo-adelante, como un saque real), swing hacia la red."""
import asyncio
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"

SEARCH_JS = """
async () => {
  const L = window.__PP_SERVE_LAB, D = window.__ppDebug;
  if (!L || !D) return { fatal: 'sin ganchos' };
  const found = [];
  const pitches = [8, 12, 16, 20, 24, 28, 32];
  const pvzs = [-1.8, -2.2, -2.6, -3.0, -3.4];
  const pvys = [-0.4, -0.2, 0, 0.2];
  const padYs = [1.0, 1.1, 1.2];
  const padZs = [0.05, 0.2, 0.35];
  outer:
  for (const pitch of pitches) {
    for (const pvz of pvzs) {
      for (const pvy of pvys) {
        for (const padY of padYs) {
          for (const padZ of padZs) {
            const r = L({ yawDeg: 180, pitchDeg: pitch, padVelZ: pvz, padVelY: pvy,
              padY, padZ, assist: false });
            if (!r.hit) continue;
            if (r.exitZ > -1.0) continue;
            found.push({ pitch, pvz, pvy, padY, padZ, exitSpeed: r.exitSpeed,
              exitZ: r.exitZ });
          }
        }
      }
    }
  }
  return { n: found.length, sample: found.slice(0, 12) };
}
"""

# La simulación hay que hacerla con la velocidad de salida: hacemos una 2ª
# pasada en JS con evaluate dedicado (simulateServePath necesita Vector3).
SIM_JS = """
(o) => {
  const D = window.__ppDebug;
  const V3 = window.__PP_GAME.ball.pos.constructor;
  const v = new V3(o.vx, o.vy, o.vz);
  const p = new V3(o.px, o.py, o.pz);
  return D.simulateServePath(p, v, new V3(), 1);
}
"""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(BASE + "/game.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(4500)
        r = await page.evaluate(SEARCH_JS)
        if r.get("fatal"):
            print("FATAL:", r["fatal"]); await browser.close(); return
        print(f"golpes con exitZ<-1.0: {r['n']}")
        # 2ª pasada: simular el vuelo real de cada golpe y quedarse con los LEGALES
        detail_js = """
        async () => {
          const L = window.__PP_SERVE_LAB, D = window.__ppDebug;
          const V3 = window.__PP_GAME.ball.pos.constructor;
          const res = [];
          const pitches = [8, 12, 16, 20, 24, 28, 32];
          const pvzs = [-1.8, -2.2, -2.6, -3.0, -3.4];
          const pvys = [-0.4, -0.2, 0, 0.2];
          const padYs = [1.0, 1.1, 1.2];
          const padZs = [0.05, 0.2, 0.35];
          for (const pitch of pitches) {
            for (const pvz of pvzs) {
              for (const pvy of pvys) {
                for (const padY of padYs) {
                  for (const padZ of padZs) {
                    const r = L({ yawDeg: 180, pitchDeg: pitch, padVelZ: pvz,
                      padVelY: pvy, padY, padZ, assist: false });
                    if (!r.hit || r.exitZ > -1.0) continue;
                    const v = new V3(r.exitVel[0], r.exitVel[1], r.exitVel[2]);
                    // posición de la bola tras el contacto = lab la recoloca;
                    // aproximamos con la posición de contacto del lab:
                    // usamos la MISMA fórmula: pad + n*dist + up*0.14
                    const q = new (window.__PP_GAME.ball.pos.constructor)();
                    // posición exacta la da el propio lab vía exitVel + pos:
                    // re-simulamos desde la posición que el lab dejó escrita
                    // en el objeto ball (no expuesta) -> usamos fórmula:
                    const rad = Math.PI / 180;
                    const n = new V3(0, -Math.sin(pitch * rad), -Math.cos(pitch * rad));
                    // yaw 180: n=(0,-sin p,-cos p); up de la pala:
                    const up = new V3(0, Math.sin(pitch * rad), -Math.cos(pitch * rad));
                    // up local (0,1,0) con Euler YXZ(pitch,180): Ry(180)*Rx(p)*(0,1,0)
                    // Rx(p)*(0,1,0) = (0, cos p, sin p); Ry(180) -> (0, cos p, -sin p)
                    const upv = new V3(0, Math.cos(pitch * rad), -Math.sin(pitch * rad));
                    const padPos = new V3(0.30, padY, padZ);
                    const bp = padPos.clone().addScaledVector(n, 0.05)
                      .addScaledVector(upv, 0.14);
                    const sim = D.simulateServePath(bp, v, new V3(0, 0, 0), 1);
                    if (sim.ok) res.push({ pitch, pvz, pvy, padY, padZ,
                      spd: r.exitSpeed, exitZ: r.exitZ,
                      oppZ: sim.oppZ, netY: sim.netY });
                    if (res.length >= 10) return res;
                  }
                }
              }
            }
          }
          return res;
        }
        """
        legals = await page.evaluate(detail_js)
        print(f"LEGALES encontrados: {len(legals)}")
        for g in legals:
            print(f"  pitch={g['pitch']:+d} pvz={g['pvz']} pvy={g['pvy']:+.1f} "
                  f"padY={g['padY']} padZ={g['padZ']} spd={g['spd']:.2f} "
                  f"exitZ={g['exitZ']:.2f} oppZ={g['oppZ']:.2f} netY={g['netY']}")
        await browser.close()

asyncio.run(main())
