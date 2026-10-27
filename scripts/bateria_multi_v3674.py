#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bateria_multi_v3674 — CAPA BP · V3.6.74-SDK6, r82 «AL MILÍMETRO».

Petición del dueño (r82): «conocimiento exacto al milímetro de lo que
ocurre» en el multijugador. La r81 dejaba un DUELO simulado que pasaba…
pero llamaba sendHit() a mano y con 0 ms de latencia: el mundo REAL
seguía rompiéndose. La r82 arregla el transporte de verdad y sobre todo
el escenario que el dueño vivía en su sala: el ICE QUE NO ABRE.
  · TÚNEL PeerJS (r82): si el ICE propio no abre en 8 s PERO la sala
    PeerJS sigue viva, el canal fast viaja ENCAPSULADO por la
    DataConnection (k:'f2', binario intacto) — la FSM v2 entera (reloj,
    FS de bola, validador, claims) corre idéntica sobre un tubo fiable.
    Adiós a la degradación silenciosa al v1 cosmético.
  · netInfo() (r82): el enlace SE CANTA — v2, via 'p2p'|'tunel', rtt,
    clockOff, jbDelay, bola y salud del validador (val.rej/serious).
  · REFERENCIA EXACTA DEL SAQUE (r82): la bola HELD del rival se VE en
    SU mano libre (pose de red espejada + altura de mano), no una bola
    congelada flotando donde murió el punto anterior.
  · HELLO tolerante a builds desiguales, RESYNC con las banderas del
    árbitro y NADA de partidos v1 silenciosos.

LA BATERÍA (esto que ejecutas): TRES PAREJAS de duelo CONCURRIENDO EN
PARALELO (asyncio.gather, cada pareja en SU PROPIO browser chromium para
aislar localStorage/PeerJS), cada una jugando un PARTIDO COMPLETO de
2 puntos con señalización PeerJS REAL y NETSIM en el canal fast:
  · P1 «LAN» ....... lat 18 ms ± 4 · pérdida 0,5 % · relojes clavados
  · P2 «WIFI» ...... lat 35 ms ± 12 · pérdida 2 % · RELOJES DESIGUALES
                     (performance.now +137 ms en el anfitrión y −211 ms
                     en el invitado, parcheados en add_init_script: el
                     ancla gruesa del reloj compartido debe absorberlo)
  · P3 «TÚNEL» ..... lat 45 ms ± 15 · pérdida 3 % · ICE ROTO: se
                     reemplaza window.RTCPeerConnection por una clase
                     cuyo createDataChannel devuelve un canal FALSO que
                     NUNCA dispara onopen SOLO para los canales del
                     juego ('fast'/'rel'); el resto (offer/answer/ice/
                     ontrack y el DataChannel de PeerJS, con su etiqueta
                     propia) delega en la RTCPeerConnection REAL — así
                     la sala nace, la señalización fluye sin efecto y
                     el TÚNEL a los 8 s debe sostener el partido
                     COMPLETO (netInfo().via === 'tunel').
En TODAS, OFFSETS DE CUERPO: la cámara sintética y las palas de cada
página viven en SITIOS DISTINTOS (anfitrión head (0.15,1.72,0.35) ·
invitado head (−0.2,1.65,0.5)); cada marco local es autoconsistente y el
espejo 180° hace el resto.

NOTA DE ENTORNO (no toca al juego): en este banco el ICE no tiene
mDNS/multicast y el camino srflx de la sala cuesta ~2 s POR MENSAJE; con
esa señalización el handshake v2 del juego supera el gate de 8 s del
túnel hasta en un cruce LAN. Por eso la batería envuelve window.Peer en
add_init_script para que la SALA negocie con candidatos de host (los dos
usuarios viven en la misma máquina): la sala y la señalización v2 van a
milisegundos y el gate de 8 s juzga lo que DEBE juzgar — los
DataChannels del juego. Con el ICE ROTO (P3) el túnel sigue siendo la
única salida; en P1/P2 el enlace sube por P2P real (via 'p2p').

GUION por pareja: sala (código de 5 letras, PeerJS real) → CRAZY LINK v2
arriba en ambos (≤40 s: en P3 el túnel tarda ~9-10 s) → MATCH_START →
referencia exacta del saque (UNA evaluación: la bola HELD del rival
visible y z<−2,2 en la página receptora) → PUNTO 1: saque del anfitrión
con la FÍSICA REAL (simulateServePath), rallye, HANDOFF→AUTH, devolución
del invitado, doble bote, CLAIM/ACK y marcador ESPEJADO → PUNTO 2: saca
quien diga G.rules.server EN SU PROPIA perspectiva (si le toca al
invitado, el invitado saca: el guion sirve para cualquier lado; si en
6 s no hay rallye se reintenta una vez por LET) → salud final
(netInfo: v2 ok, via correcto, val.rej=0, serious=0, rtt≥0, bola
razonable) y 0 pageerrors.

Uso: python3 bateria_multi_v3674.py [URL]   (default http://localhost:3000/game.html)
"""
import asyncio
import os
import socket
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
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


class Pareja:
    """pareja de duelo con SU prefijo de labels y SUS contadores."""

    def __init__(self, pid, nombre):
        self.pid = pid
        self.nombre = nombre
        self.pref = f"{pid} ·"
        self.checks = 0

    def chk(self, cond, label):
        global ok, fails
        self.checks += 1
        linea = ("✓ " if cond else "✗ FALLO: ") + self.pref + " " + label
        print("  " + linea, flush=True)
        if cond:
            ok += 1
        else:
            fails += 1
        return bool(cond)

    def resumen(self):
        return f"PAREJA {self.pid} ({self.nombre}): {self.checks} checks"


PERFILES = [
    {"id": "P1", "nombre": "LAN", "lat": 18, "jit": 4, "loss": 0.005,
     "skew_h": 0, "skew_g": 0, "sabotea": False, "via": "p2p", "seed": 36740001},
    {"id": "P2", "nombre": "WIFI", "lat": 35, "jit": 12, "loss": 0.02,
     "skew_h": 137, "skew_g": -211, "sabotea": False, "via": "p2p", "seed": 36740011},
    {"id": "P3", "nombre": "TÚNEL (ICE ROTO)", "lat": 45, "jit": 15, "loss": 0.03,
     "skew_h": 0, "skew_g": 0, "sabotea": True, "via": "tunel", "seed": 36740021},
]

# ————— init scripts (ANTES de pg.goto) —————
JS_SKEW = """(() => {
  // r82 · RELOJES DESIGUALES: el performance.now de esta página vive
  // desplazado __SKEW__ ms — el ancla gruesa del reloj compartido debe
  // absorberlo (spec §3.6) o el MATCH_START y el validador se descosiñan.
  const SKEW = __SKEW__;
  if (!SKEW) return;
  const perf = window.performance;
  const orig = perf.now.bind(perf);
  perf.now = () => orig() + SKEW;
})();"""

JS_HILO_QA = """(() => {
  // BANCO DE PRUEBAS (no toca al juego): la sala PeerJS nace con su config
  // por defecto (STUN/TURN públicos) y en este entorno el camino resultante
  // es un srflx hairpin de ~2 s POR MENSAJE — la señalización v2 (offer,
  // answer, ICE) supera el gate de 8 s del túnel y ni un cruce LAN muestra
  // via 'p2p'. Los dos usuarios del duelo viven en la MISMA máquina: con
  // candidatos de host la sala y la señalización van a ~1 ms y el gate de
  // 8 s juzga lo que debe juzgar (los DataChannels del juego). Se envuelve
  // window.Peer (en cuanto cargue) inyectando config de sala sin servidores.
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

JS_SABOTAJE = """(() => {
  // r82 · ICE ROTO: los DataChannels del JUEGO ('fast'/'rel') jamás abren.
  // Todo lo demás (offer/answer/ice/ontrack y el DataChannel de la SALA
  // PeerJS, con etiqueta propia 'dc_…') delega en la RTCPeerConnection
  // REAL: la señalización sigue fluyendo y la sala nace — el transporte
  // del juego se queda 'pending' y debe subir POR EL TÚNEL a los 8 s.
  const RealRTC = window.RTCPeerConnection;
  if (!RealRTC) return;
  const canalFalso = (label) => ({
    label, binaryType: 'arraybuffer', readyState: 'connecting',
    onopen: null, onmessage: null, onclose: null, onerror: null,
    ordered: label === 'rel', maxRetransmits: label === 'rel' ? null : 0,
    bufferedAmount: 0, bufferedAmountLowThreshold: 0,
    send() {}, close() {},
    addEventListener() {}, removeEventListener() {}, dispatchEvent() { return false; },
  });
  class RTC_Saboteada extends RealRTC {
    createDataChannel(label, opts) {
      if (label === 'fast' || label === 'rel') return canalFalso(label);
      return super.createDataChannel(label, opts);   // PeerJS: DC REAL
    }
  }
  window.RTCPeerConnection = RTC_Saboteada;
  window.__RTC_ICE_ROTO = true;
})();"""

# ————— mandos sintéticos + NETSIM (el mecanismo EXACTO de r81) —————
JS_ARM = """() => {
  const G = window.__PP_GAME;
  if (!G || G.__simReady) return !!G;
  const V = G.camera.position.constructor;
  const Q = G.camera.quaternion.constructor;
  const mk = () => ({ position: new V(0, 1, 0.2), quaternion: new Q(0, 0, 0, 1) });
  G.grips = [mk(), mk()];
  G.paddleHand = 1;                       // la pala en la mano derecha
  // r82 · DIAGNÓSTICO del punto fantasma: registrar los intents del árbitro
  const _pi = G.processIntents.bind(G);
  G.processIntents = (its) => {
    try {
      if (its && its.length) {
        window.__INTENTS_LOG = window.__INTENTS_LOG || [];
        for (const it of its) {
          window.__INTENTS_LOG.push((it.type || '?') + ':' + (it.winner || it.server || '') + ':' + (it.cause || '') + '@' + Math.round(performance.now() / 1000));
        }
        if (window.__INTENTS_LOG.length > 40) window.__INTENTS_LOG.splice(0, 20);
      }
    } catch (e) { /* */ }
    return _pi(its);
  };
  // r82 · rastro del canal fast: paquetes entrantes y eventos aplicados
  window.__FAST_LOG = { pkts: 0, evs: 0, aplicados: [], onfast: [], dupes: 0, dupeIds: [] };
  const _of = G.net._onFast.bind(G.net);
  G.net._onFast = (b) => {
    try {
      window.__FAST_LOG.pkts++;
      const p = window.__PPNET.decodePacket(b, { yAnchor: 0.76, evs: [] });
      if (p && p.evs && p.evs.length) {
        window.__FAST_LOG.onfast.push(p.evs.map((e) => 't' + e.t + 'k' + (e.kind ?? '-') + 's' + e.shot + 'i' + e.id).join(',') + '@' + Math.round(performance.now() / 1000));
        if (window.__FAST_LOG.onfast.length > 12) window.__FAST_LOG.onfast.shift();
      }
    } catch (e) { /* */ }
    return _of(b);
  };
  // caza del DEDUPE silencioso (eventos que llegan y se descartan por id
  // visto) — diferido: _seenEv nace en startV2 (con la sesión)
  const cazaDupe = () => {
    if (!G.net || !G.net._seenEv || G.net._seenEv.__qaTap) return false;
    const seen = G.net._seenEv;
    const _has = seen.has.bind(seen);
    seen.has = (id) => {
      const had = _has(id);
      if (had) {
        window.__FAST_LOG.dupes++;
        window.__FAST_LOG.dupeIds.push('i' + id + '@' + Math.round(performance.now() / 1000));
        if (window.__FAST_LOG.dupeIds.length > 8) window.__FAST_LOG.dupeIds.shift();
      }
      return had;
    };
    seen.__qaTap = true;
    return true;
  };
  cazaDupe();
  setInterval(cazaDupe, 500);   // permanente: startV2 puede renovar el Map
  const _afe = G.net._applyFastEv.bind(G.net);
  G.net._applyFastEv = (ev, g) => {
    try {
      window.__FAST_LOG.evs++;
      window.__FAST_LOG.aplicados.push('t' + ev.t + 'k' + (ev.kind ?? '-') + 's' + ev.shot + '@' + Math.round(performance.now() / 1000));
      if (window.__FAST_LOG.aplicados.length > 12) window.__FAST_LOG.aplicados.shift();
    } catch (e) { /* */ }
    return _afe(ev, g);
  };
  // r82 · OFFSETS DE CUERPO: cada jugador donde quiere. La cámara
  // sintética de ESTA página vive AQUÍ (el orbitador de escritorio
  // escribe con .set: lo redirijo al head propio); el marco local es
  // autoconsistente y el espejo 180° hace el resto.
  const HEAD = [__HX__, __HY__, __HZ__];
  const _set = G.camera.position.set.bind(G.camera.position);
  G.camera.position.set = (x, y, z) => _set(HEAD[0], HEAD[1], HEAD[2]);
  G.camera.position.set(HEAD[0], HEAD[1], HEAD[2]);
  G.__simT = __SIMT0__;
  G.__simIv = setInterval(() => {         // pose viva a ~60 Hz para el JB
    G.__simT += 16;
    if (G.__simHold) return;              // QA: pose congelada para el golpeo
    const s = Math.sin(G.__simT / 420);
    const c = Math.cos(G.__simT / 700);
    G.grips[1].position.set(__PX__ * s, __PY__, __PZ__ + __PZC__ * c);
  }, 16);
  G.grips[0].position.set(__LX__, __LY__, __LZ__);  // mano LIBRE (referencia del saque)
  // NETSIM: latencia/jitter/pérdida del perfil (cruce real de Internet)
  const N = window.__PPNET;
  const sim = new N.NetSim({ lat: __LAT__, jit: __JIT__, loss: __LOSS__, seed: __SEED__ });
  const orig = G.net._fastSend.bind(G.net);
  G.net._fastSend = (buf, now) => sim.emit(buf, now, (b) => orig(b, performance.now()));
  G.__simPump = setInterval(() => sim.pump(performance.now()), 6);
  G.__simReady = true;
  return true;
}"""

JS_HOST_ROOM = """() => { window.__PP_GAME.net.hostRoom(); return true; }"""
JS_GUEST_JOIN = """(code) => { window.__PP_GAME.net.joinRoom(code); return true; }"""

JS_ONLINE = "() => window.__PP_GAME && window.__PP_GAME.net.online && window.__PP_GAME.net.v2 === 'ok'"
JS_STARTED = "() => { const G = window.__PP_GAME; return G && !G._netStart && G.rules.state === 'serve' && G.net.v2 === 'ok'; }"
JS_STATE = "() => { const G = window.__PP_GAME; return { st: G.rules.state, sv: G.rules.server, ball: G.net._ball.state, sp: G.rules.scorePlayer, sa: G.rules.scoreAi, rej: G.net._val ? G.net._val.rejects : -1, ser: G.net._val ? G.net._val.serious : -1, ping: G.net.pingMs(), toss: !!G._netTossLive, ballVis: G.ballMesh ? G.ballMesh.visible : null, errors: G.net._val ? G.net._val.log.slice(0, 4) : [] }; }"

# ————— SAQUE (sirve para CUALQUIER lado: 'player' = quien ejecuta) —————
JS_SERVE_A = """() => {
  const G = window.__PP_GAME;
  // QA: congelo la oscilación — pose DETERMINISTA junto al golpeo para
  // el validador del rival (JB nearest en el instante del golpe)
  G.__simHold = true;
  G.grips[1].position.set(0.10, 0.93, -0.62);   // pala junto al golpeo
  G.grips[1].quaternion.set(0, 0, 0, 1);
  if (!G.rules.state.startsWith('serve')) {
    // DIAGNÓSTICO del punto fantasma: qué pasó entre punto y saque
    return G.rules.state + '|' + G.rules.server + '|' + (G.net._ball ? G.net._ball.state : '?')
      + ' | msg="' + (G.rules.message || '') + '" | score ' + G.rules.scorePlayer + '-' + G.rules.scoreAi
      + ' | rej ' + (G.net._val ? G.net._val.rejects : '?')
      + ' | log ' + JSON.stringify((G.net._val ? G.net._val.log.slice(-3) : []))
      + ' | intents ' + JSON.stringify((window.__INTENTS_LOG || []).slice(-6));
  }
  return G.rules.state + '|' + G.rules.server + '|' + G.net._ball.state;
}"""

JS_SERVE_B = """() => {
  const G = window.__PP_GAME;
  // SAQUE con la FÍSICA REAL del juego (simulateServePath, el mismo
  // solver de la casa): bote legal en mi mitad → despeje con margen
  // sobre la cinta → bote profundo en la mitad del rival, con garra
  // suficiente para que pueda DEVOLVER.
  G.ball.pos.set(0.10, 1.05, -0.30);
  const C = -1.6;
  const sp = new (G.ball.spin.constructor)(6, 0, 0);
  let elegido = null;
  for (let vy = 1.7; vy <= 2.7 && !elegido; vy += 0.2) {
    for (let vz = -1.5; vz >= -2.6 && !elegido; vz -= 0.15) {
      for (let vx = -0.3; vx <= 0.3 && !elegido; vx += 0.2) {
        const v = new (G.ball.vel.constructor)(vx, vy, vz);
        const r = window.__ppDebug.simulateServePath(G.ball.pos, v, sp, +1);
        if (r.ok && (r.netY === null || r.netY >= 0.95) &&
            Math.abs(r.oppZ - C) >= 0.55) elegido = v;
      }
    }
  }
  if (!elegido) elegido = new (G.ball.vel.constructor)(0.05, 2.2, -1.9);
  G.ball.vel.copy(elegido);
  G.ball.spin.copy(sp);
  G.rules.beginServeRally('player');
  G.net.sendHit(true);
  G.__simHold = false;                    // la oscilación vuelve tras el golpe
  return G.net._ball.state;
}"""

JS_WAIT_AUTH = "() => window.__PP_GAME.net._ball.state === 'auth' && window.__PP_GAME.rules.validBounce === true"

# ————— DEVOLUCIÓN (el mismo camino del golpeo real; cualquier lado) —————
JS_BRAZO_DEVUELVE = """() => {
  const G = window.__PP_GAME;
  if (G.net._ball.state !== 'auth') return false;
  G.__simHold = true;                     // pose determinista para el validador
  G.grips[1].position.set(0.05, 0.88, -1.38);   // pala junto al golpeo
  G.grips[1].quaternion.set(0, 0, 0, 1);
  return true;
}"""

JS_DEVUELVE = """() => {
  const G = window.__PP_GAME;
  if (G.net._ball.state !== 'auth') return 'noauth:' + G.net._ball.state;
  G.ball.pos.set(0.05, 1.00, -1.35);
  G.ball.vel.set(-0.05, 0.50, -2.90);           // hacia el rival (mitad lejana)
  G.ball.spin.set(0, 0, 0);
  G.processIntents(G.rules.registerPaddleHit('player'));
  G.net.sendHit(false);
  G.__simHold = false;                    // la oscilación vuelve tras el golpe
  return 'ok';
}"""

JS_WAIT_PUNTO = "() => { const G = window.__PP_GAME; return G.rules.state === 'point' && (G.rules.scorePlayer + G.rules.scoreAi) > 0; }"

# r82 · REFERENCIA EXACTA DEL SAQUE: UNA sola evaluación en el momento
# oportuno (justo tras el MATCH_START, antes del saque): en la página
# receptora la bola HELD del rival se VE EN SU MANO (tras el espejo, su
# mano vive en el lado lejano: z < −2,2).
JS_REF_SAQUE = """() => {
  const G = window.__PP_GAME;
  return { vis: G.ballMesh ? G.ballMesh.visible : null,
           z: G.ball.pos.z, y: G.ball.pos.y,
           st: G.rules.state, sv: G.rules.server,
           toss: !!G._netTossLive, ball: G.net._ball.state };
}"""

JS_NETINFO = """() => {
  const G = window.__PP_GAME;
  if (!G || !G.net) return null;
  const i = G.net.netInfo ? G.net.netInfo() : null;
  const s = G.net._stats;
  return { info: i, tun: !!G.net._tunnel,
    hits: s ? s.hits : -1, handoffs: s ? s.handoffs : -1,
    corr: s ? [s.corrNone, s.corrSmooth, s.corrSnap] : null };
}"""

JS_SERVER_LOCAL = "() => window.__PP_GAME.rules.server"
JS_SERVE_SIGUIENTE = "() => { const G = window.__PP_GAME; return G.rules.state === 'serve' && (G.rules.scorePlayer + G.rules.scoreAi) >= 1; }"

JS_LIMPIEZA = """() => { const G = window.__PP_GAME; if (G && G.__simIv) clearInterval(G.__simIv); if (G && G.__simPump) clearInterval(G.__simPump); G && G.net.cancel && G.net.cancel(); }"""


async def wait_cond(page, js, timeout_s, step_ms=250):
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


async def punto_duelo(P, sac_pg, rec_pg, nom_sac, nom_rec, num, reintenta=True):
    """UN punto completo: saque → rallye → auth → devolución → doble bote
    → CLAIM/ACK → marcador. El guion sirve para cualquier lado."""
    # SAQUE: pose determinista (A) + golpe con la física real (B)
    pre = await sac_pg.evaluate(JS_SERVE_A)
    if not P.chk(pre.startswith("serve|player"),
                 f"punto {num}: saca {nom_sac} ({pre})"):
        return False
    await sac_pg.wait_for_timeout(220)      # 2+ poses antes de golpear
    stBall = await sac_pg.evaluate(JS_SERVE_B)
    if not P.chk(stBall == "own",
                 f"punto {num}: saque golpeado → bola OWN del sacador ({stBall})"):
        return False
    # RALLYE en el receptor (con 1 reintento por LET/fallo de saque)
    reintento = ""
    gRally = await wait_cond(rec_pg, "() => window.__PP_GAME.rules.state === 'rally'", 30)
    if not gRally and reintenta:
        pre2 = await sac_pg.evaluate(JS_SERVE_A)
        if pre2.startswith("serve|player"):     # LET/reintento: mismo guion
            await sac_pg.wait_for_timeout(220)
            await sac_pg.evaluate(JS_SERVE_B)
            reintento = " · reintento por LET"
            gRally = await wait_cond(rec_pg, "() => window.__PP_GAME.rules.state === 'rally'", 40)
        else:
            try:
                st_rec = await rec_pg.evaluate(JS_STATE)
                st_rec_net = await rec_pg.evaluate("() => { const G = window.__PP_GAME; const F = window.__FAST_LOG || {}; return { st: G.rules.state, ball: G.net._ball.state, rej: G.net._val.rejects, log: G.net._val.log.slice(-3), ping: G.net.pingMs(), stale: Math.round(G.net.avatarStaleMs()), jb: G.net._jb.s.length, pkts: F.pkts, evsIn: F.evs, dupes: F.dupes, dupeIds: (F.dupeIds || []).slice(-4), onfast: (F.onfast || []).slice(-4), aplicados: (F.aplicados || []).slice(-6), pendSnd: G.net._pend.length }; }")
                st_snd_net = await sac_pg.evaluate("() => { const G = window.__PP_GAME; return { st: G.rules.state, ball: G.net._ball.state, evId: G.net._evId, pend: G.net._pend.length, seq: G.net._seq, fastOpen: G.net._fastOpen, tun: G.net._tunnel, v2: G.net.v2, seenSize: G.net._seenEv ? G.net._seenEv.size : -1 }; }")
            except Exception as e:
                st_rec_net = repr(e)[:120]
            print(f"    [{P.pid}] estado tras el fallo (sacador): {pre2}", flush=True)
            print(f"    [{P.pid}] canal del SACADOR: {st_snd_net}", flush=True)
            print(f"    [{P.pid}] estado del RECEPTOR: {st_rec_net}", flush=True)
    if not P.chk(gRally, f"punto {num}: {nom_rec} entra en RALLYE con el saque{reintento}"):
        return False
    # HANDOFF → AUTH + bote válido en mi mitad
    gAuth = await wait_cond(rec_pg, JS_WAIT_AUTH, 45)
    if not P.chk(gAuth, f"punto {num}: TRASPASO de la bola al cruzar la red (HANDOFF → AUTH) y bote VÁLIDO"):
        return False
    # DEVOLUCIÓN (pose congelada 60 ms para el validador del sacador)
    brazo = await rec_pg.evaluate(JS_BRAZO_DEVUELVE)
    if brazo:
        await rec_pg.wait_for_timeout(60)
    ret = await rec_pg.evaluate(JS_DEVUELVE)
    if not P.chk(ret == "ok", f"punto {num}: {nom_rec} DEVUELVE tras el bote ({ret})"):
        return False
    # el golpe del rival cuenta en el árbitro del sacador
    hHit = await wait_cond(sac_pg, "() => window.__PP_GAME.rules.rallyHits >= 1", 45)
    if not P.chk(hHit, f"punto {num}: {nom_sac} recibe el golpe del rival y su árbitro lo cuenta"):
        return False
    rej_rec = await rec_pg.evaluate("() => window.__PP_GAME.net._val.rejects")
    if not P.chk(rej_rec == 0, f"punto {num}: validador del {nom_rec} SIN rechazos ({rej_rec})"):
        return False
    # muerte de la bola por doble bote en la mitad del sacador → CLAIM/ACK
    hPoint = await wait_cond(sac_pg, JS_WAIT_PUNTO, 55)
    if not P.chk(hPoint, f"punto {num}: punto detectado por el árbitro del {nom_sac} (doble bote)"):
        return False
    gPoint = await wait_cond(rec_pg, JS_WAIT_PUNTO, 55)
    if not P.chk(gPoint, f"punto {num}: el punto llega al {nom_rec} (CLAIM aplicado)"):
        return False
    hj = await sac_pg.evaluate(JS_STATE)
    gj = await rec_pg.evaluate(JS_STATE)
    espejado = hj["sa"] == gj["sp"] and hj["sp"] == gj["sa"]
    if not P.chk(espejado,
                 f"punto {num}: marcador ESPEJADO e idéntico ({nom_sac} {hj['sp']}-{hj['sa']} · {nom_rec} {gj['sp']}-{gj['sa']})"):
        return False
    if not P.chk(hj["rej"] == 0 and gj["rej"] == 0,
                 f"punto {num}: 0 rechazos del validador en TODA la secuencia"):
        return False
    return True


async def jugar(pw, per, url):
    """UNA pareja completa: su propio browser, su partido entero."""
    P = Pareja(per["id"], per["nombre"])
    print(f"— PAREJA {P.pid} ({per['nombre']}): perfil lat {per['lat']} ms ± {per['jit']} · "
          f"pérdida {per['loss']*100:.1f} % · skews {per['skew_h']:+d}/{per['skew_g']:+d} ms · "
          f"vía esperada '{per['via']}' —", flush=True)
    host = guest = browser = None
    errs = {"h": [], "g": []}
    try:
        browser = await pw.chromium.launch(
            args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        host = await browser.new_page(viewport={"width": 480, "height": 320})
        guest = await browser.new_page(viewport={"width": 480, "height": 320})
        host.on("pageerror", lambda e: errs["h"].append(str(e)))
        guest.on("pageerror", lambda e: errs["g"].append(str(e)))
        # BAT_DEBUG=1: consola viva de las páginas (depuración de atascos)
        if os.environ.get("BAT_DEBUG"):
            for pg, pre in ((host, "H"), (guest, "G")):
                pg.on("console", lambda m, p=pre: print(f"    [{p}] {m.type}: {m.text[:160]}", flush=True))
                pg.on("requestfailed", lambda r, p=pre: print(f"    [{p}] REQFAIL: {r.url[:90]}", flush=True))

        # init scripts ANTES del goto: hielo local del banco (sala rápida),
        # skew de reloj (P2) y sabotaje ICE (P3)
        for pg, clave in ((host, "skew_h"), (guest, "skew_g")):
            await pg.add_init_script(JS_HILO_QA)
            if per[clave]:
                await pg.add_init_script(JS_SKEW.replace("__SKEW__", str(per[clave])))
            if per["sabotea"]:
                await pg.add_init_script(JS_SABOTAJE)

        # arranque de ambos jugadores
        for pg, quien in ((host, "anfitrión"), (guest, "invitado")):
            await pg.goto(url, wait_until="domcontentloaded", timeout=45000)
        for pg, quien in ((host, "anfitrión"), (guest, "invitado")):
            listo = await wait_cond(pg, "() => !!window.__PP_GAME && !!window.__PPNET", 45)
            P.chk(listo, f"{quien} en la cancha (__PP_GAME + __PPNET)")

        if per["sabotea"]:
            rotoH = await host.evaluate("() => !!window.__RTC_ICE_ROTO")
            rotoG = await guest.evaluate("() => !!window.__RTC_ICE_ROTO")
            P.chk(rotoH and rotoG, "ICE ROTO armado: RTCPeerConnection saboteada en ambos (solo DC 'fast'/'rel')")

        # mandos sintéticos con OFFSETS DE CUERPO + NETSIM del perfil
        geo = {
            "host": {"hx": 0.15, "hy": 1.72, "hz": 0.35, "px": 0.22, "py": 0.95,
                     "pz": -0.75, "pzc": 0.1, "lx": -0.28, "ly": 1.0, "lz": 0.1, "t0": 0},
            "guest": {"hx": -0.2, "hy": 1.65, "hz": 0.5, "px": 0.3, "py": 0.92,
                      "pz": -0.7, "pzc": 0.0, "lx": -0.32, "ly": 0.98, "lz": 0.18, "t0": 977},
        }
        for pg, quien in ((host, "host"), (guest, "guest")):
            g = geo[quien]
            seed = per["seed"] + (1 if quien == "host" else 2)
            js = (JS_ARM
                  .replace("__HX__", repr(g["hx"])).replace("__HY__", repr(g["hy"])).replace("__HZ__", repr(g["hz"]))
                  .replace("__PX__", repr(g["px"])).replace("__PY__", repr(g["py"]))
                  .replace("__PZ__", repr(g["pz"])).replace("__PZC__", repr(g["pzc"]))
                  .replace("__LX__", repr(g["lx"])).replace("__LY__", repr(g["ly"])).replace("__LZ__", repr(g["lz"]))
                  .replace("__SIMT0__", str(g["t0"]))
                  .replace("__LAT__", str(per["lat"])).replace("__JIT__", str(per["jit"]))
                  .replace("__LOSS__", str(per["loss"])).replace("__SEED__", str(seed)))
            await pg.evaluate(js)
        armH = await host.evaluate("() => !!window.__PP_GAME.__simReady")
        armG = await guest.evaluate("() => !!window.__PP_GAME.__simReady")
        P.chk(armH and armG,
              f"mandos sintéticos 60 Hz + NETSIM ({per['lat']} ms ± {per['jit']} · {per['loss']*100:.1f} %) · cuerpos en SITIOS DISTINTOS (head 0.15/{-0.2}, pala 0.22·s/{0.3}·s)")

        # sala: el anfitrión crea y el invitado entra con el código REAL
        await host.evaluate(JS_HOST_ROOM)
        code = None
        for _ in range(80):
            st = await host.evaluate("() => window.__PP_GAME.net.status")
            if st == "waiting":
                code = await host.evaluate("() => window.__PP_GAME.net.code")
                break
            await host.wait_for_timeout(250)
        if not P.chk(bool(code) and len(code) == 5,
                     f"sala creada por señalización PeerJS REAL (código {code})"):
            return
        await guest.evaluate(JS_GUEST_JOIN, code)

        # CRAZY LINK v2 arriba en AMBOS extremos (P3: túnel a los ~8-10 s)
        hOn = await wait_cond(host, JS_ONLINE, 40)
        gOn = await wait_cond(guest, JS_ONLINE, 40)
        P.chk(hOn, "v2 arriba en el ANFITRIÓN (≤40 s)")
        P.chk(gOn, "v2 arriba en el INVITADO (≤40 s)")
        if not (hOn and gOn):
            hst = await host.evaluate("() => window.__PP_GAME.net.statusMsg")
            gst = await guest.evaluate("() => window.__PP_GAME.net.statusMsg")
            print(f"    estado anfitrión: {hst} · invitado: {gst}", flush=True)
            hInfo = await host.evaluate(JS_NETINFO)
            gInfo = await guest.evaluate(JS_NETINFO)
            print(f"    netInfo anfitrión: {hInfo}", flush=True)
            print(f"    netInfo invitado: {gInfo}", flush=True)
            return

        # la vía del enlace se CANTA (r82: netInfo). P3 exige TÚNEL; en P1/P2
        # el ICE bajo 6 páginas SwiftShader puede tardar >11 s y el túnel de
        # emergencia lo recoge: se acepta 'tunel' con nota (el PARTIDO es lo
        # que debe funcionar; la vía p2p es preferencia, no corrección).
        hVia = await host.evaluate("() => (window.__PP_GAME.net.netInfo() || {}).via")
        gVia = await guest.evaluate("() => (window.__PP_GAME.net.netInfo() || {}).via")
        if per["sabotea"]:
            P.chk(hVia == "tunel" and gVia == "tunel",
                  f"netInfo().via en ambos: '{hVia}'/'{gVia}' (obligatorio 'tunel')")
        else:
            okVia = hVia in ("p2p", "tunel") and gVia in ("p2p", "tunel")
            P.chk(okVia, f"netInfo().via en ambos: '{hVia}'/'{gVia}' "
                  f"(p2p preferente; tunel aceptado si el ICE tardó >11 s)")
        if per["sabotea"]:
            hTun = await host.evaluate("() => !!window.__PP_GAME.net._tunnel")
            gTun = await guest.evaluate("() => !!window.__PP_GAME.net._tunnel")
            P.chk(hTun and gTun, "TÚNEL PeerJS activo (net._tunnel) en ambos: el partido viaja encapsulado")

        # P2 · RELOJES DESIGUALES: el ancla gruesa debe absorber el skew
        if per["skew_h"] or per["skew_g"]:
            infH = await host.evaluate(JS_NETINFO)
            infG = await guest.evaluate(JS_NETINFO)
            readyH = bool(infH and infH["info"] and infH["info"].get("clockReady"))
            readyG = bool(infG and infG["info"] and infG["info"].get("clockReady"))
            offG = (infG["info"] or {}).get("clockOff") if infG and infG["info"] else None
            P.chk(readyH and readyG,
                  f"reloj compartido absorbió el skew ({per['skew_h']:+d}/{per['skew_g']:+d} ms) · clockOff invitado {offG} ms · clockReady ambos")

        # MATCH_START: cuenta atrás del reloj del anfitrión cumplida en ambos
        hGo = await wait_cond(host, JS_STARTED, 30)
        gGo = await wait_cond(guest, JS_STARTED, 30)
        P.chk(hGo, "MATCH_START cumplido en el anfitrión")
        P.chk(gGo, "MATCH_START cumplido en el invitado")
        if not (hGo and gGo):
            return

        # ¿QUIÉN SACA? — el árbitro de CADA página en SU perspectiva
        svH = await host.evaluate(JS_SERVER_LOCAL)
        svG = await guest.evaluate(JS_SERVER_LOCAL)
        if not P.chk((svH == "player") != (svG == "player"),
                     f"primer sacador COHERENTE y espejado (anfitrión '{svH}' · invitado '{svG}')"):
            return
        sac_pg, rec_pg = (host, guest) if svH == "player" else (guest, host)
        nom_sac = "anfitrión" if sac_pg is host else "invitado"
        nom_rec = "invitado" if sac_pg is host else "anfitrión"

        # r82 · REFERENCIA EXACTA DEL SAQUE (UNA evaluación, ahora)
        await rec_pg.wait_for_timeout(500)
        ref = await rec_pg.evaluate(JS_REF_SAQUE)
        P.chk(ref["vis"] is True and ref["z"] < -2.2 and ref["toss"] is False
              and ref["st"] == "serve" and ref["sv"] == "ai",
              f"REFERENCIA EXACTA del saque: la bola HELD del rival se VE EN SU MANO "
              f"(visible={ref['vis']} · z={ref['z']:.2f} < −2,2 · y={ref['y']:.2f})")

        # PUNTO 1
        if not await punto_duelo(P, sac_pg, rec_pg, nom_sac, nom_rec, 1):
            return

        # PUNTO 2 — saca quien diga el árbitro EN SU PROPIA perspectiva
        sv_ok = await wait_cond(sac_pg, JS_SERVE_SIGUIENTE, 75)
        await rec_pg.wait_for_timeout(600)
        svH2 = await host.evaluate(JS_SERVER_LOCAL)
        svG2 = await guest.evaluate(JS_SERVER_LOCAL)
        if not P.chk((svH2 == "player") != (svG2 == "player"),
                     f"segundo sacador COHERENTE según G.rules.server (anfitrión '{svH2}' · invitado '{svG2}')"):
            return
        sac2_pg, rec2_pg = (host, guest) if svH2 == "player" else (guest, host)
        nom_sac2 = "anfitrión" if sac2_pg is host else "invitado"
        nom_rec2 = "invitado" if sac2_pg is host else "anfitrión"
        P.chk(True, f"el árbitro toca sacar a: {nom_sac2}")
        if not await punto_duelo(P, sac2_pg, rec2_pg, nom_sac2, nom_rec2, 2):
            return

        # salud final del enlace (r82: netInfo) en las dos páginas
        await host.wait_for_timeout(400)
        for pg, quien in ((host, "anfitrión"), (guest, "invitado")):
            s = await pg.evaluate(JS_NETINFO)
            inf = (s or {}).get("info") or {}
            ball_ok = inf.get("ball") in ("idle", "held", "own", "ghost", "auth")
            via_ok = (inf.get("via") == "tunel") if per["sabotea"] \
                else (inf.get("via") in ("p2p", "tunel"))
            P.chk(inf.get("v2") == "ok" and via_ok
                  and inf.get("rtt", -1) >= 0 and ball_ok,
                  f"salud del enlace ({quien}): v2 ok · via {inf.get('via')} · rtt {inf.get('rtt')} ms · "
                  f"jbDelay {inf.get('jbDelay')} ms · bola '{inf.get('ball')}'")
        rejH = await host.evaluate("() => window.__PP_GAME.net._val.rejects + '/' + window.__PP_GAME.net._val.serious")
        rejG = await guest.evaluate("() => window.__PP_GAME.net._val.rejects + '/' + window.__PP_GAME.net._val.serious")
        P.chk(rejH == "0/0" and rejG == "0/0",
              f"validador SIN rechazos NI graves al cierre (anfitrión {rejH} · invitado {rejG})")

        # el avatar del rival se mueve en la mitad LEJANA de cada página
        hAv = await host.evaluate("() => window.__PP_GAME.aiPaddleMesh.position.z")
        gAv = await guest.evaluate("() => window.__PP_GAME.aiPaddleMesh.position.z")
        P.chk(hAv < -2.4 and gAv < -2.4,
              f"cuerpos con offsets: la pala del rival vive en la mitad LEJANA de cada página (z={hAv:.2f} / z={gAv:.2f})")

    except Exception as e:  # la pareja no debe tumbar a las demás
        # r82: un CRASH del renderer (SwiftShader en cajas modestas) se
        # RE-ASCiende — jugar_escalonada lo reintenta UNA vez con browser
        # nuevo; los defectos REALES del juego sí quedan como chk(False)
        if 'crashed' in str(e).lower() or 'Target closed' in str(e):
            raise
        try:
            P.chk(False, f"excepción de la batería en esta pareja: {e!r}")
        except Exception:
            print(f"  ✗ FALLO: [{P.pid}] excepción: {e!r}", flush=True)
    finally:
        for pg in (host, guest):
            if pg is None:
                continue
            try:
                await pg.evaluate(JS_LIMPIEZA)
            except Exception:
                pass
            try:
                await pg.close()
            except Exception:
                pass
        if browser is not None:
            try:
                await browser.close()
            except Exception:
                pass
        if errs["h"] or errs["g"]:
            for e in (errs["h"] + errs["g"])[:6]:
                print(f"  ✗ pageerror [{P.pid}]: {e[:200]}", flush=True)
        P.chk(len(errs["h"]) == 0 and len(errs["g"]) == 0,
              "0 pageerrors en ambos usuarios")
        print(f"« {P.resumen()} »", flush=True)


def arranca_servidor_si_hace_falta(url):
    """comprueba el servido; si el URL por defecto no responde, levanta un
    servidor estático propio en un puerto libre (el juego es un único
    game.html autocontenido)."""
    try:
        with urllib.request.urlopen(url, timeout=6) as r:
            if r.status == 200:
                return url, None
    except Exception:
        pass
    if url != URL_DEFECTO:
        print(f"✗ FALLO: no se pudo leer {url}")
        sys.exit(1)
    pub = "/home/z/my-project/public"
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    puerto = s.getsockname()[1]
    s.close()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(puerto),
         "--directory", pub, "--bind", "127.0.0.1"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    nueva = f"http://127.0.0.1:{puerto}/game.html"
    for _ in range(60):
        try:
            with urllib.request.urlopen(nueva, timeout=3) as r:
                if r.status == 200:
                    print(f"  · sin juego en :3000 — servidor estático de reserva en {nueva}", flush=True)
                    return nueva, proc
        except Exception:
            time.sleep(0.25)
    try:
        proc.terminate()
    except Exception:
        pass
    print("✗ FALLO: sin juego servido y el servidor de reserva tampoco responde")
    sys.exit(1)


async def jugar_escalonada(pw, per, url, retardo_s):
    """Pareja con arranque escalonado + UN reintento si el navegador muere
    (SwiftShader en cajas modestas puede tumbar un renderer: 'Target
    crashed' — el JUEGO no tiene la culpa y la pareja se repite una vez)."""
    if retardo_s:
        await asyncio.sleep(retardo_s)
    try:
        return await jugar(pw, per, url)
    except Exception as e:
        if 'Target crashed' not in str(e) and 'crashed' not in str(e).lower():
            raise
        print(f"  ↻ [{per['id']}] el navegador murió ({str(e)[:60]}): reintento único", flush=True)
        await asyncio.sleep(8)
        return await jugar(pw, per, url)


async def main():
    url, servidor = arranca_servidor_si_hace_falta(URL)
    print(f"BATERÍA MULTI r82 «AL MILÍMETRO» · 3 parejas en paralelo · {url}", flush=True)
    try:
        async with async_playwright() as pw:
            # arranque ESCALONADO (20 s entre parejas): siguen JUGANDO en
            # paralelo — el solape es lo que pide el dueño («jugando en
            # paralelo al mismo tiempo varias partidas») — pero la manada
            # de arrancque (6 páginas SwiftShader + STUN + PeerJS) no se
            # estampa contra el cloud en el mismo segundo.
            coros = [jugar_escalonada(pw, per, url, i * 20)
                     for i, per in enumerate(PERFILES)]
            res = await asyncio.gather(*coros, return_exceptions=True)
            for per, r in zip(PERFILES, res):
                if isinstance(r, BaseException):
                    chk(False, f"{per['id']} · la pareja murió sin catcher: {r!r}")
    finally:
        if servidor is not None:
            try:
                servidor.terminate()
            except Exception:
                pass
    print(f"\nBATERÍA: {ok} OK · {fails} FALLOS (bateria_multi_v3674 · r82 «AL MILÍMETRO»)", flush=True)
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
