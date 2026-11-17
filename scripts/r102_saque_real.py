#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r102_saque_real — SAQUE con el GESTO REAL en multijugador v2 (r102).

La batería r82 (bateria_multi_v3674) saca con simulateServePath +
beginServeRally a mano: JAMÁS ejercita releaseBallHand → tossFromHand →
bola al aire → golpeo REAL de la pala (presenting=false ⇒ pads vacíos).
En el Quest real presenting=true y el saque vive EN ESE camino. Esta
prueba reproduce el dispositivo en el banco:

  ·xr.isPresenting = true (property real de three 0.186, session null es
   seguro: updateCamera sale pronto con session===null)
  ·G.connected = [true, true] → controllerPaddles activos → pads vivos
  ·lanzo la bola con releaseBallHand(ballHand) tras mover la mano libre
   hacia arriba (velocidad REAL de updatePaddleSim)
  ·golpeo con la pala: barrido ascendente del grip a través de la bola
   que cae (collidePaddleSweep + CCD de la casa, sin atajos)

Comprueba, para el SAQUE DEL ANFITRIÓN y el DEL INVITADO:
  1. el lanzamiento sale (tossed, vy>0) y la bola es MÍA (FSM mine)
  2. RALLYE en AMBOS extremos (beginServeRally local + HIT validado remoto)
  3. TRASPASO (HANDOFF→AUTH) y 0 rechazos del validador
Más SONDAS de espejo de pose (pala del rival: posición y orientación).
"""
import asyncio
import os
import sys
import urllib.request

from playwright.async_api import async_playwright

URL_DEFECTO = "http://localhost:3000/game.html"

ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label, flush=True)
    if cond:
        ok += 1
    else:
        fails += 1
    return bool(cond)


# ————— init scripts (ANTES de pg.goto) —————
JS_HILO_QA = """(() => {
  const injeta = () => {
    if (typeof window.Peer !== 'function' || window.Peer.__qaHielo) return false;
    const RealPeer = window.Peer;
    class PeerQA extends RealPeer {
      constructor(id, opts) {
        opts = opts || {};
        opts.config = Object.assign({}, opts.config, { iceServers: [] });
        super(id, opts);
      }
    }
    PeerQA.__qaHielo = true;
    window.Peer = PeerQA;
    return true;
  };
  injeta();
  const iv = setInterval(() => { if (injeta()) clearInterval(iv); }, 100);
  setTimeout(() => clearInterval(iv), 20000);
})();"""

# ————— mandos sintéticos + presentando + NETSIM —————
JS_ARM = """() => {
  const G = window.__PP_GAME;
  if (!G || G.__simReady) return !!G;
  const V = G.camera.position.constructor;
  const Q = G.camera.quaternion.constructor;
  const mk = () => ({ position: new V(0, 1, 0.2), quaternion: new Q(0, 0, 0, 1) });
  G.grips = [mk(), mk()];
  G.paddleHand = 1;                       // pala en la derecha; bola en la izquierda
  const _pi = G.processIntents.bind(G);
  G.processIntents = (its) => {
    try {
      if (its && its.length) {
        window.__INTENTS_LOG = window.__INTENTS_LOG || [];
        for (const it of its) {
          window.__INTENTS_LOG.push((it.type || '?') + ':' + (it.winner || it.server || '') + ':' + (it.cause || ''));
        }
        if (window.__INTENTS_LOG.length > 40) window.__INTENTS_LOG.splice(0, 20);
      }
    } catch (e) { /* */ }
    return _pi(its);
  };
  const HEAD = [__HX__, __HY__, __HZ__];
  const _set = G.camera.position.set.bind(G.camera.position);
  G.camera.position.set = (x, y, z) => _set(HEAD[0], HEAD[1], HEAD[2]);
  G.camera.position.set(HEAD[0], HEAD[1], HEAD[2]);
  G.__simHold = true;                     // pose bajo control del guion
  G.grips[0].position.set(__LX__, __LY__, __LZ__);   // mano libre
  G.grips[1].position.set(__PX__, __PY__, __PZ__);   // pala
  const N = window.__PPNET;
  const sim = new N.NetSim({ lat: __LAT__, jit: __JIT__, loss: __LOSS__, seed: __SEED__ });
  const orig = G.net._fastSend.bind(G.net);
  G.net._fastSend = (buf, now) => sim.emit(buf, now, (b) => orig(b, performance.now()));
  G.__simPump = setInterval(() => sim.pump(performance.now()), 6);
  // r102 · BANDERAS de carrera (el rallye del receptor dura ~300 ms: un
  // sondeo externo lo pierde) — muestreo interno cada 80 ms
  window.__FLAGS = { rally: false, auth: false, ghost: false, tossEvt: false,
    maxRej: 0, serious: 0, samples: 0 };
  G.__flagIv = setInterval(() => {
    try {
      const F = window.__FLAGS, b = G.net._ball, st = G.rules.state;
      F.samples++;
      if (st === 'rally') F.rally = true;
      if (b) {
        if (b.state === 'auth') F.auth = true;
        if (b.state === 'ghost') F.ghost = true;
      }
      if (G._netTossLive) F.tossEvt = true;
      if (G.net._val) { F.maxRej = Math.max(F.maxRej, G.net._val.rejects); F.serious = G.net._val.serious;
        if (G.net._val.log.length) F.rejLog = G.net._val.log.slice(-4); }
    } catch (e) { /* */ }
  }, 80);
  G.__simReady = true;
  return true;
}"""

JS_PRESENTA = """() => {
  // El DISPOSITIVO: presenting=true (colisiones de pala vivas, saque real)
  const G = window.__PP_GAME;
  G.renderer.xr.isPresenting = true;      // three 0.186: propiedad simple
  G.connected = [true, true];
  return { p: G.renderer.xr.isPresenting, con: G.connected };
}"""

JS_HOST_ROOM = """() => { window.__PP_GAME.net.hostRoom(); return true; }"""
JS_GUEST_JOIN = """(code) => { window.__PP_GAME.net.joinRoom(code); return true; }"""

JS_ONLINE = "() => window.__PP_GAME && window.__PP_GAME.net.online && window.__PP_GAME.net.v2 === 'ok'"
JS_STARTED = "() => { const G = window.__PP_GAME; return G && !G._netStart && G.rules.state === 'serve' && G.net.v2 === 'ok'; }"

# ————— SAQUE REAL (gesto del dispositivo) —————
JS_SAQUE_REAL = """async () => {
  const G = window.__PP_GAME;
  if (G.rules.state !== 'serve' || G.rules.server !== 'player' || G.tossed) {
    return { err: G.rules.state + '|' + G.rules.server + '|tossed:' + G.tossed };
  }
  if (G._netStart) return { err: 'cuenta-atras' };
  const bh = G.ballHand;
  const fsm0 = G.net._ball.state + '/' + G.net._ball.mine;
  const b0 = { x: +G.ball.pos.x.toFixed(3), y: +G.ball.pos.y.toFixed(3), z: +G.ball.pos.z.toFixed(3) };
  const h0 = { x: +G.grips[bh].position.x.toFixed(3), y: +G.grips[bh].position.y.toFixed(3) };
  // 1) subir la mano libre con velocidad REAL y CONSTANTE (~2 m/s al soltar):
  //    subida previa lenta + tramo de velocidad constante (la media móvil de
  //    70 ms converge al valor del tramo) + soltar EN el tramo constante
  G.grips[bh].position.set(-0.24, 1.0, 0.05);           // mano a casa (la bola sigue)
  await new Promise((r) => setTimeout(r, 60));
  let f = 0;
  await new Promise((res) => {
    const iv = setInterval(() => {
      f++;
      let y = 1.0;
      if (f <= 8) y = 1.0 + 0.015 * f;                  // arranque suave (~0,9 m/s)
      else y = 1.12 + 0.032 * (f - 8);                  // tramo constante (~2,0 m/s)
      G.grips[bh].position.set(-0.24, y, 0.05);
      if (f >= 14) { clearInterval(iv); res(); }
    }, 16);
  });
  const vMano = +G.controllerPaddles[bh].vel.y.toFixed(2);
  // 2) SOLTAR por el camino REAL (releaseBallHand → tossFromHand)
  G.releaseBallHand(bh);
  await new Promise((r) => setTimeout(r, 130));
  return { tossed: G.tossed, vy: +G.ball.vel.y.toFixed(2), y: +G.ball.pos.y.toFixed(2),
           fsm: G.net._ball.state, mine: G.net._ball.mine, fsm0, vMano, b0, h0,
           msg: G.rules.message };
}"""

# ————— GOLPE REAL (barrido de la pala por la bola que cae) —————
JS_GOLPE_REAL = """async () => {
  const G = window.__PP_GAME;
  const ph = G.paddleHand;
  if (!G.tossed) return { err: 'sin-toss', st: G.rules.state };
  // PUNTO MUERTO: la casa lo SEÑALA (apexSignaled) — barrido hacia la mesa
  // a la altura EXACTA del apex (bola casi parada: contacto limpio,
  // dirección frontal cerca del saque legal → la asistencia redondea)
  await new Promise((res) => {
    let g = 0;
    const iv = setInterval(() => {
      if (G.apexSignaled || ++g > 94) { clearInterval(iv); res(); }
    }, 16);
  });
  const yc = G.ball.pos.y - 0.02;
  G.grips[ph].quaternion.set(-0.12, 0, 0, 0.993);   // ~14°: cara casi vertical
  for (let p = 0; p < 3; p++) {
    await new Promise((res) => {
      let f = 0;
      const iv = setInterval(() => {
        f++;
        const t = Math.min(1, f / 10);
        G.grips[ph].position.set(-0.24, yc, 0.28 - 0.34 * t);
        if (f >= 10) { clearInterval(iv); res(); }
      }, 12);
    });
    G.grips[ph].position.set(-0.24, yc, 0.28);        // reposición al inicio
    await new Promise((r) => setTimeout(r, 30));
    if (!G.tossed) break;                             // ya golpeó: parar
  }
  G.grips[ph].quaternion.set(0, 0, 0, 1);
  G.grips[ph].position.set(0.22, 0.95, -0.75);          // pala a casa (no contamina)
  G.grips[0].position.set(-0.28, 1.0, 0.1);             // mano libre a casa
  await new Promise((r) => setTimeout(r, 400));
  return { st: G.rules.state, fsm: G.net._ball.state, tossed: G.tossed,
           vy: +G.ball.vel.y.toFixed(2), v: +G.ball.vel.length().toFixed(2),
           msg: G.rules.message, rej: G.net._val ? G.net._val.rejects : -1,
           log: G.net._val ? G.net._val.log.slice(-3) : [],
           intents: (window.__INTENTS_LOG || []).slice(-4) };
}"""

JS_RECV_STATE = """() => {
  const G = window.__PP_GAME;
  return { st: G.rules.state, fsm: G.net._ball.state, toss: !!G._netTossLive,
           rej: G.net._val ? G.net._val.rejects : -1,
           log: G.net._val ? G.net._val.log.slice(-4) : [],
           by: +G.ball.pos.y.toFixed(2), bz: +G.ball.pos.z.toFixed(2),
           msg: G.rules.message,
           intents: (window.__INTENTS_LOG || []).slice(-4) };
}"""

JS_WAIT_RALLY = "() => window.__PP_GAME.rules.state === 'rally'"
JS_WAIT_AUTH = "() => window.__PP_GAME.net._ball.state === 'auth'"

# ————— SONDA DE ESPEJO: pose determinista de la pala en el EXTREMO —————
JS_SONDA_SET = """() => {
  const G = window.__PP_GAME;
  // agarre en el EXTREMO derecho del sacador, hoja girada (cuat conocidos)
  G.__simHold = true;
  G.grips[1].position.set(0.62, 1.00, -0.55);
  G.grips[1].quaternion.set(0, 0.3826834, 0, 0.9238795);   // yaw +45°
  G.grips[0].position.set(-0.24, 1.0, 0.05);
  G.grips[0].quaternion.set(0, 0, 0, 1);
  return true;
}"""

JS_SONDA_LOCAL = """() => {
  const G = window.__PP_GAME;
  // cadena LOCAL: qVis = gripQ ⊗ mountQuatFor(hand); hoja = qVis·(0,1,0)·0.1303
  const T3 = G.camera.position.constructor;   // THREE importado en página
  const q = new (G.camera.quaternion.constructor)();
  const mq = (G.paddleMounts && G.paddleMounts[G.paddleHand] && G.paddleMounts[G.paddleHand].quaternion)
    || null;
  q.copy(G.grips[1].quaternion);
  if (mq) q.multiply(mq);
  const hoja = new T3(0, 1, 0).applyQuaternion(q);
  const centro = new T3(0, (2.1115 - -2.9) * 0.026, 0).applyQuaternion(q).add(G.grips[1].position);
  return { dir: [+hoja.x.toFixed(4), +hoja.y.toFixed(4), +hoja.z.toFixed(4)],
           cen: [+centro.x.toFixed(4), +centro.y.toFixed(4), +centro.z.toFixed(4)],
           mount: !!mq };
}"""

JS_SONDA_GHOST = """() => {
  const G = window.__PP_GAME;
  const m = G.aiPaddleMesh;
  if (!m) return null;
  const T3 = G.camera.position.constructor;
  const hoja = new T3(0, 1, 0).applyQuaternion(m.quaternion);
  return { dir: [+hoja.x.toFixed(4), +hoja.y.toFixed(4), +hoja.z.toFixed(4)],
           cen: [+m.position.x.toFixed(4), +m.position.y.toFixed(4), +m.position.z.toFixed(4)],
           stale: Math.round(G.net.avatarStaleMs()) };
}"""

JS_NETINFO = """() => {
  const G = window.__PP_GAME;
  if (!G || !G.net) return null;
  const i = G.net.netInfo ? G.net.netInfo() : null;
  return { info: i, hits: G.net._stats ? G.net._stats.hits : -1,
           handoffs: G.net._stats ? G.net._stats.handoffs : -1 };
}"""

JS_LIMPIEZA = """() => { const G = window.__PP_GAME; if (G && G.__simPump) clearInterval(G.__simPump); G && G.net.cancel && G.net.cancel(); }"""


async def wait_cond(page, js, timeout_s, step_ms=200):
    t = 0.0
    while t < timeout_s:
        try:
            if await page.evaluate(js):
                return True
        except Exception:
            pass
        await page.wait_for_timeout(step_ms)
        t += step_ms / 1000.0
    return False


async def saque_real(sac_pg, rec_pg, nom_sac, nom_rec, tag, detalle=True):
    """SAQUE con el GESTO REAL del dispositivo + verificación completa.
    Con REINTENTOS: un vuelo que falta (serve_out del guion sintético)
    devuelve el saque al mismo jugador y se vuelve a intentar (hasta 3).
    Antes de CADA intento se espera el ASIENTO del intent 'serve' (la
    transición punto→saque corre por rules.update y compite con el guion)."""
    SETTLE = ("() => { const G = window.__PP_GAME; return G.rules.state === 'serve' && "
              "G.rules.server === 'player' && !G.tossed && !G._netStart; }")
    auth_visto = False
    for intento in (1, 2, 3):
        if not await wait_cond(sac_pg, SETTLE, 30):
            dump = await sac_pg.evaluate("() => { const G = window.__PP_GAME; return { st: G.rules.state, sv: G.rules.server, to: G.tossed, ns: !!G._netStart, fsm: G.net._ball.state, sp: G.rules.scorePlayer, sa: G.rules.scoreAi, msg: G.rules.message, intents: (window.__INTENTS_LOG||[]).slice(-6) }; }")
            return chk(False, f"{tag}: el saque no llegó a asentarse (intento {intento}) · {dump}")
        await sac_pg.wait_for_timeout(700)              # el intent 'serve' asentado
        # el saque pudo ROTAR (punto en juego al asentarse): re-leer y ceder
        svNow = await sac_pg.evaluate("() => window.__PP_GAME.rules.server")
        if svNow != 'player':
            return False
        pre = await sac_pg.evaluate(JS_SAQUE_REAL)
        if 'err' in pre:
            if intento == 3:
                return chk(False, f"{tag}: lanzamiento no arrancó ({pre['err']})")
            continue
        if detalle:
            chk(pre['fsm0'].endswith('true'),
                f"{tag}: bola HELD mía antes del lanzamiento (FSM {pre['fsm0']})")
            chk(pre['b0']['y'] > 0.9 and abs(pre['b0']['x'] - pre['h0']['x']) < 0.05,
                f"{tag}: bola apoyada en la MANO LIBRE (bola {pre['b0']} · mano {pre['h0']})")
        if not (pre['tossed'] is True and pre['vy'] > 0.8):
            print(f"      intento {intento}: lanzamiento no voló ({pre})", flush=True)
            continue
        chk(True, f"{tag}: LANZAMIENTO real vuela (intento {intento} · vy {pre['vy']} m/s · vel mano {pre['vMano']})")
        # GOLPE REAL con la pala
        golpe = await sac_pg.evaluate(JS_GOLPE_REAL)
        if 'err' in golpe:
            return chk(False, f"{tag}: golpeo imposible ({golpe['err']})")
        # el contacto REAL registra (rallye) o el árbitro juzga el vuelo
        # (serve_out con la FSM en own: la CADENA funciona; el vuelo lo
        # juzga el árbitro y el guion sintético no es un saque de campeonato)
        okContacto = golpe['st'] == 'rally' or \
            (golpe['st'] == 'point' and golpe['fsm'] == 'own' and
             any('serve_out' in i for i in golpe['intents']))
        if detalle:
            chk(okContacto,
                f"{tag}: GOLPE REAL de la pala registra ({golpe['st']} · FSM {golpe['fsm']} · «{golpe['msg']}» · v {golpe['v']} m/s)")
        if not okContacto:
            print(f"      debug sacador: {golpe}", flush=True)
            continue
        # el receptor: ghost (HIT kind 1 validado) → rallye → AUTH (traspaso)
        await wait_cond(rec_pg, "() => window.__FLAGS && window.__FLAGS.ghost", 20)
        await rec_pg.wait_for_timeout(2500)          # margen para el traspaso
        rs = await rec_pg.evaluate("() => window.__FLAGS")
        if detalle:
            chk(rs['ghost'] and rs['rally'],
                f"{tag}: {nom_rec} ve el saque (ghost) y entra en RALLYE (banderas {rs})")
        if rs['auth']:
            auth_visto = True
            chk(True, f"{tag}: TRASPASO HANDOFF→AUTH — bola JUGABLE en el receptor (intento {intento})")
            break
    ser = await rec_pg.evaluate("() => window.__PP_GAME.net._val.serious")
    chk(ser == 0, f"{tag}: validador del receptor sin GRAVES (serious {ser})")
    if not auth_visto:
        chk(False, f"{tag}: la bola nunca fue JUGABLE en el receptor (3 intentos)")
    return auth_visto


async def run(pw, url):
    print("— r102 · SAQUE REAL multijugador (gesto del dispositivo) —", flush=True)
    browser = None
    errs = {"h": [], "g": []}
    try:
        browser = await pw.chromium.launch(
            args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        host = await browser.new_page(viewport={"width": 480, "height": 320})
        guest = await browser.new_page(viewport={"width": 480, "height": 320})
        host.on("pageerror", lambda e: errs["h"].append(str(e)))
        guest.on("pageerror", lambda e: errs["g"].append(str(e)))
        if os.environ.get("BAT_DEBUG"):
            for pg, pre in ((host, "H"), (guest, "G")):
                pg.on("console", lambda m, p=pre: print(f"    [{p}] {m.type}: {m.text[:160]}", flush=True))

        for pg in (host, guest):
            await pg.add_init_script(JS_HILO_QA)
        for pg in (host, guest):
            await pg.goto(url, wait_until="domcontentloaded", timeout=45000)
        for pg, quien in ((host, "anfitrión"), (guest, "invitado")):
            listo = await wait_cond(pg, "() => !!window.__PP_GAME && !!window.__PPNET", 45)
            chk(listo, f"{quien} en la cancha (__PP_GAME + __PPNET)")

        geo = {
            "host": {"hx": 0.15, "hy": 1.72, "hz": 0.35, "px": 0.22, "py": 0.95,
                     "pz": -0.75, "lx": -0.28, "ly": 1.0, "lz": 0.1},
            "guest": {"hx": -0.2, "hy": 1.65, "hz": 0.5, "px": 0.3, "py": 0.92,
                      "pz": -0.7, "lx": -0.32, "ly": 0.98, "lz": 0.18},
        }
        for pg, quien in ((host, "host"), (guest, "guest")):
            g = geo[quien]
            js = (JS_ARM
                  .replace("__HX__", repr(g["hx"])).replace("__HY__", repr(g["hy"])).replace("__HZ__", repr(g["hz"]))
                  .replace("__PX__", repr(g["px"])).replace("__PY__", repr(g["py"])).replace("__PZ__", repr(g["pz"]))
                  .replace("__LX__", repr(g["lx"])).replace("__LY__", repr(g["ly"])).replace("__LZ__", repr(g["lz"]))
                  .replace("__LAT__", "18").replace("__JIT__", "4")
                  .replace("__LOSS__", "0.005").replace("__SEED__", "10200001"))
            await pg.evaluate(js)
        chk(await host.evaluate("() => !!window.__PP_GAME.__simReady") and
            await guest.evaluate("() => !!window.__PP_GAME.__simReady"),
            "mandos sintéticos + NETSIM LAN 18 ms")

        await host.evaluate(JS_HOST_ROOM)
        code = None
        for _ in range(80):
            st = await host.evaluate("() => window.__PP_GAME.net.status")
            if st == "waiting":
                code = await host.evaluate("() => window.__PP_GAME.net.code")
                break
            await host.wait_for_timeout(250)
        if not chk(bool(code) and len(code) == 5, f"sala PeerJS REAL (código {code})"):
            return
        await guest.evaluate(JS_GUEST_JOIN, code)
        hOn = await wait_cond(host, JS_ONLINE, 40)
        gOn = await wait_cond(guest, JS_ONLINE, 40)
        chk(hOn and gOn, "CRAZY LINK v2 arriba en ambos")
        if not (hOn and gOn):
            print("    H:", await host.evaluate(JS_NETINFO), flush=True)
            print("    G:", await guest.evaluate(JS_NETINFO), flush=True)
            return

        # EL DISPOSITIVO: presenting + mandos conectados en ambos
        pH = await host.evaluate(JS_PRESENTA)
        pG = await guest.evaluate(JS_PRESENTA)
        chk(pH['p'] and pG['p'] and pH['con'][0] and pG['con'][1],
            "presenting=true + mandos conectados (camino REAL del Quest)")

        hGo = await wait_cond(host, JS_STARTED, 30)
        gGo = await wait_cond(guest, JS_STARTED, 30)
        chk(hGo and gGo, "MATCH_START cumplido en ambos")
        if not (hGo and gGo):
            return

        svH = await host.evaluate("() => window.__PP_GAME.rules.server")
        svG = await guest.evaluate("() => window.__PP_GAME.rules.server")
        chk((svH == 'player') != (svG == 'player'),
            f"primer sacador espejado (anfitrión '{svH}' · invitado '{svG}')")
        sac_pg, rec_pg = (host, guest) if svH == 'player' else (guest, host)
        nom_sac = "anfitrión" if sac_pg is host else "invitado"
        nom_rec = "invitado" if sac_pg is host else "anfitrión"

        # SONDA de espejo ANTES del primer punto: pose determinista del EXTREMO
        await host.evaluate(JS_SONDA_SET)
        await host.wait_for_timeout(600)            # ≥10 poses al JB del rival
        loc = await host.evaluate(JS_SONDA_LOCAL)
        gho = await guest.evaluate(JS_SONDA_GHOST)
        if loc and gho and gho.get('stale', 9e9) < 400:
            exp_dir = [-loc['dir'][0], loc['dir'][1], -loc['dir'][2]]
            exp_cen = [-loc['cen'][0], loc['cen'][1], -3.2 - loc['cen'][2]]
            dot = sum(a * b for a, b in zip(exp_dir, gho['dir']))
            ang = __import__('math').degrees(__import__('math').acos(max(-1, min(1, dot))))
            dpos = __import__('math').dist(exp_cen, gho['cen'])
            chk(ang < 6 and dpos < 0.06,
                f"ESPEJO de la pala en el extremo: hoja {ang:.1f}° de error · centro {dpos * 100:.1f} cm "
                f"(dir {gho['dir']} vs exp {[round(v, 3) for v in exp_dir]} · cen {gho['cen']} vs exp {[round(v, 3) for v in exp_cen]})")
        else:
            chk(False, f"ESPEJO de la pala: sonda sin datos (loc {loc} · ghost {gho})")
        await host.evaluate("() => { const G = window.__PP_GAME; G.grips[1].position.set(0.22, 0.95, -0.75); G.grips[1].quaternion.set(0, 0, 0, 1); G.grips[0].position.set(-0.28, 1.0, 0.1); }")

        # SAQUES REALES hasta que AMBOS lados hayan servido con la bola
        # JUGABLE al otro lado (el árbitro rota el saque cada 2 puntos: el
        # guion obedece a quien toque, como los jugadores reales)
        servidos = {"host": False, "guest": False}
        for intento in range(1, 11):
            svH = await host.evaluate("() => window.__PP_GAME.rules.server")
            sac_pg, rec_pg = (host, guest) if svH == 'player' else (guest, host)
            lado = "host" if sac_pg is host else "guest"
            nom_sac = "anfitrión" if lado == "host" else "invitado"
            nom_rec = "invitado" if lado == "host" else "anfitrión"
            detalle = not servidos[lado]
            r = await saque_real(sac_pg, rec_pg, nom_sac, nom_rec,
                                 f"saque {intento} de {nom_sac}", detalle)
            if r:
                servidos[lado] = True
            if all(servidos.values()):
                break
        chk(servidos["host"] and servidos["guest"],
            f"saque REAL con la bola JUGABLE al otro lado desde LOS DOS lados "
            f"(anfitrión {servidos['host']} · invitado {servidos['guest']})")

        rejH = await host.evaluate("() => window.__PP_GAME.net._val.rejects + '/' + window.__PP_GAME.net._val.serious")
        rejG = await guest.evaluate("() => window.__PP_GAME.net._val.rejects + '/' + window.__PP_GAME.net._val.serious")
        chk(rejH == "0/0" and rejG == "0/0",
            f"validador limpio al cierre (H {rejH} · G {rejG})")
        chk(not errs["h"] and not errs["g"],
            f"0 pageerrors (H {len(errs['h'])} · G {len(errs['g'])})")
        if errs["h"] or errs["g"]:
            print("    errs H:", errs["h"][:3], flush=True)
            print("    errs G:", errs["g"][:3], flush=True)
    except Exception as e:
        print(f"  ✗ EXCEPCIÓN: {e!r}", flush=True)
        global fails
        fails += 1
    finally:
        for pg in (locals().get('host'), locals().get('guest')):
            if pg is None:
                continue
            try:
                await pg.evaluate(JS_LIMPIEZA)
            except Exception:
                pass
        if browser:
            try:
                await browser.close()
            except Exception:
                pass
    print(f"— RESULTADO r102 saque real: {ok} ✓ · {fails} ✗ —", flush=True)
    return fails


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else URL_DEFECTO
    try:
        urllib.request.urlopen(url, timeout=5)
    except Exception as e:
        print(f"✗ el juego no responde en {url}: {e}", flush=True)
        return 1
    async with async_playwright() as pw:
        return await run(pw, url)


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(main()) else 0)
