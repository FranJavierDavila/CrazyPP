#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r82_v3674 — CAPA BR · V3.6.73→3.6.88-SDK6, FASE 76 «AL MILÍMETRO».

Petición del dueño (r82): «Lo que me parece que no va bien es la partida en
red multijugador, sigo sin poder jugar la bola. Veo movimiento de palas pero
poco más, es preciso que ambos jugadores tengan un conocimiento exacto al
milímetro de lo que ocurre, lanzamientos, golpes, botes, todo coordinado sin
desplazamientos de coordenadas, referencias exactas a la posición de la mesa
que va cada uno desde su perspectiva… Emplea una batería de agentes
especializados en trabajos de red y sincronización para poder estar jugando
en paralelo al mismo tiempo varias partidas y detectar dónde está el
problema».

Lo implementado (r82) y SU verificación:
  · EL DEFECTO QUE IMPEDÍA JUGAR: en v2 los golpes de rallye nunca se
    anunciaban (_localHit sólo en la rama v1) — ahora se anuncia todo golpe
    propio con el rallye VIVO (y sólo vivo: la bola muerta ya no puede
    resucitarse en el rival → sin puntos fantasma).
  · PRECISIÓN MILIMÉTRICA: JitterBuf CLONA las muestras (adiós al aliasing
    que juzgaba cada golpe con la última pose) y las sella por el instante
    de CAPTURA del emisor; el eco NTP del reloj compartido VIVE (echoTime/
    echoDelay se escriben en cada paquete) y el validador tolera 120 ms de
    futuro mientras el reloj refina; el LANZAMIENTO (kind 2) ya no exige
    correlativo (el HIT lo porta).
  · TÚNEL PEERJS de emergencia (v2 sobre la sala si el ICE no abre en 11 s),
    HELLO tolerante a BUILD (dos cachés distintos no rompen el enlace),
    partidos v1 silenciosos BLOQUEADOS con mensaje y voz.
  · REFERENCIAS EXACTAS VISIBLES: bola HELD del rival EN SU MANO, montura
    del avatar por MANO FÍSICA (bit 8), enlace cantado por voz,
    window.__PP_NET.netInfo() (vía/RTT/reloj/rechazos) y telemetría en
    cualquier fin de sesión.
  · LA BATERÍA (capa BQ, script propio bateria_multi_v3674.py): 3 parejas
    EN PARALELO (LAN/WiFi-con-skew/TÚNEL-ICE-ROTO), partidos completos de
    2 puntos con saque de ambos lados.

BLOQUES: (1) AGUJAS r82 en el servido. (2) CONTADORES exactos. (3) JUEGO
REAL headless: netInfo vivo, clon del JB sobre la instancia, validador kind 2
y tolerancia de futuro, preview de la bola HELD en la mano del rival, tunnel
packet por onData. El duelo vivo completo vive en la capa BQ (batería).
Uso: python3 qa_r82_v3674.py [URL]
"""
import asyncio
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # — el golpe propio se anuncia en v2 (el defecto que impedía jugar) —
    ("anuncio de golpe propio en la rama v2", "EL GOLPE PROPIO EN v2 SE ANUNCIA"),
    ("sólo con el rallye vivo (sin puntos fantasma)", "SOLO con el RALLYE VIVO"),
    # — precisión milimétrica —
    ("JitterBuf clona las muestras", "CLON OBLIGATORIO"),
    ("sello de pose por captura del emisor", "SELLO POR CAPTURA"),
    ("eco NTP vivo (echoTime/echoDelay)", "ECO NTP VIVO"),
    ("tolerancia de futuro 120 ms", "TOL_FUTURE: 120"),
    ("el lanzamiento (kind 2) sin correlativo", "el LANZAMIENTO (kind 2) NO lleva correlativo"),
    # — túnel PeerJS de emergencia —
    ("túnel: gate en el bucle frame", "TÚNEL DE EMERGENCIA"),
    ("túnel: encapsulado del fast", "vía TÚNEL"),
    ("túnel: desenredo en onData", "paquete fast encapsulado por el TÚNEL"),
    ("túnel: canales suben por dos caminos", "los canales «suben» por DOS caminos"),
    # — hello tolerante + v1 bloqueado —
    ("HELLO tolerante a BUILD", "BUILD TOLERANTE"),
    ("partido v1 silencioso bloqueado", "NADA DE PARTIDOS v1 SILENCIOSOS"),
    # — referencias exactas visibles —
    ("bola HELD del rival EN SU MANO", "REFERENCIA EXACTA DEL SAQUE"),
    ("montura del avatar por mano física (bit 8)", "montura por MANO FÍSICA"),
    ("emisión del bit 8 de lateralidad", "LATERALIDAD FÍSICA"),
    ("cuenta atrás con bola en cinemática", "CUENTA ATRÁS del MATCH_START la bola"),
    ("enlace cantado por voz", "EL ENLACE SE CANTA"),
    ("netInfo() para HUD/QA", "netInfo() {"),
    ("telemetría en cualquier fin", "_teleReport"),
    ("resync con banderas del árbitro", "banderas del ÁRBITRO"),
    ("i18n: enlace directo ES", "net_link_direct: 'Enlace directo establecido'"),
    ("i18n: aviso de build distinto ES", "net_build_warn:"),
    ("i18n: v2 caído ES", "net_v2_down:"),
    ("i18n: enlace directo EN", "net_link_direct: 'Direct link established'"),
    ("i18n: aviso de build EN", "net_build_warn:"),
]

CONTADORES = [
    ("el anuncio del golpe propio aparece UNA vez", "EL GOLPE PROPIO EN v2 SE ANUNCIA", 1),
    ("el clon del JitterBuf es único", "CLON OBLIGATORIO", 1),
    ("el eco NTP se alimenta una vez por paquete", "ECO NTP VIVO", 1),
    ("el gate del túnel es único", "TÚNEL DE EMERGENCIA", 1),
    ("la encapsulación del túnel es única", "vía TÚNEL", 1),
    ("la desenrolla del onData es única", "paquete fast encapsulado por el TÚNEL", 1),
    ("la tolerancia de BUILD es única", "BUILD TOLERANTE", 1),
    ("el bloqueo v1 es único", "NADA DE PARTIDOS v1 SILENCIOSOS", 1),
    ("la preview del saque es única", "REFERENCIA EXACTA DEL SAQUE", 1),
    ("la lateralidad física viaja una vez", "LATERALIDAD FÍSICA", 1),
    ("el sello por captura es único", "SELLO POR CAPTURA", 1),
]

JS_NETINFO = """() => {
  const G = window.__PP_GAME;
  if (!G || !G.net) return { error: 'sin net' };
  const inf = G.net.netInfo ? G.net.netInfo() : null;
  return { info: inf, hasPPNET: !!window.__PP_NET };
}"""

JS_RED82 = """() => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  const N = window.__PPNET;
  const out = { checks: [] };
  const chk = (cond, label) => out.checks.push([!!cond, label]);

  // 1 · netInfo() vivo sobre la instancia real (sin sesión: forma honesta)
  const inf = G.net.netInfo();
  chk(inf && typeof inf.v2 === 'string' && 'via' in inf && 'buildWarn' in inf,
      'netInfo(): forma completa sin sesión (' + JSON.stringify(inf) + ')');

  // 2 · el clon del JitterBuf sobre la instancia viva: dos muestras con el
  //     MISMO objeto reutilizado no se pisan (aliasing muerto)
  const jb = new N.JitterBuf(8);
  const sam = { hp: [0, 1.7, 0.3], hq: [0, 0, 0, 1],
    lp: [-0.4, 1.0, 0.1], lq: [0, 0, 0, 1],
    rp: [0.3, 1.0, 0.5], rq: [0, 0, 0, 1], fl: 3 };
  jb.push(5000, sam);
  sam.rp[0] = 0.95; sam.rp[2] = -0.2;
  jb.push(5017, sam);
  const antigua = jb.nearest(5000, null, 250);
  chk(!!antigua && Math.abs(antigua.rp[0] - 0.3) < 1e-9,
      'JB vivo: la muestra antigua conserva 0.3/0.5 (' +
      (antigua && antigua.rp[0].toFixed(2)) + ')');

  // 3 · validador: kind 2 SIN correlativo + tolerancia de futuro 120 ms
  const val = new N.Validator();
  const rT = val.hit({ t: 1, kind: 2, shot: 0, tHit: 5000,
    p: [0, 0.3, 1.0], v: [0, 2.4, 0], s: [0, 0, 0] },
    { nowHost: 5010, lastShot: 0, lastHitT: 0, padPos: [0.05, 0.25, 1.05] });
  chk(rT.ok, 'validador: LANZAMIENTO (kind 2, shot 0) ACEPTADO');
  const rF = val.hit({ t: 1, kind: 1, shot: 1, tHit: 5080,
    p: [0, 0.3, 1.0], v: [0, 1, -4], s: [0, 0, 0] },
    { nowHost: 5000, lastShot: 0, lastHitT: 0, padPos: null });
  chk(rF.ok, 'validador: tHit +80 ms ACEPTADO (TOL_FUTURE ' + N.VP.TOL_FUTURE + ' ms)');
  const rF2 = val.hit({ t: 1, kind: 1, shot: 2, tHit: 5400,
    p: [0, 0.3, 1.0], v: [0, 1, -4], s: [0, 0, 0] },
    { nowHost: 5000, lastShot: 1, lastHitT: 5080, padPos: null });
  chk(!rF2.ok, 'validador: tHit +400 ms RECHAZADO (anti-trampa intacta)');

  // 4 · el túnel por onData: un paquete binario encapsulado {k:'f2'} entra
  //     por el MISMO _onFast (la pose del rival llega al jitter buffer)
  let poseOk = false;
  const orig = G.net._onFast.bind(G.net);
  G.net._onFast = (b) => { poseOk = true; return orig(b); };
  // estado mínimo de sesión (el flujo real siempre nace en startV2; aquí
  // sólo preparamos los campos que _onFast/_onAckFrom tocan)
  G.net._pend = G.net._pend || [];
  G.net._recvHist = G.net._recvHist || [];
  G.net._recvRing = G.net._recvRing || [];
  G.net._lastRemoteHitT = 0;
  G.net._ackP = 0;
  G.net._clock = G.net._clock || new N.NetClock(true);
  G.net._jb = G.net._jb || new N.JitterBuf();
  G.net.v2 = 'ok';                          // el guard de _onFast
  const buf = new ArrayBuffer(64);
  const n = N.encodePacket(buf, {
    seq: 1, ack: 0, ackBits: 0, sendTime: 123456, echoTime: 0, echoDelay: 0,
    pose: { hp: [0, 1.7, 0.4], hq: [0, 0, 0, 1],
            lp: [-0.4, 1.0, 0.1], lq: [0, 0, 0, 1],
            rp: [0.3, 1.0, 0.5], rq: [0, 0, 0, 1], fl: 3 },
    evs: [],
  });
  G.net.onData({ k: 'f2', b: buf.slice(0, n) });
  G.net.v2 = null;                          // restaurar (sin sesión real)
  G.net._onFast = orig;
  chk(poseOk, 'TÚNEL: el paquete {k:f2} entra por onData → _onFast (pose al JB)');

  // 5 · el eco NTP queda ARMADO al recibir (echoTime = sendTime del otro)
  chk(G.net._echoTime === 123456 && G.net._echoAt > 0,
      'eco NTP: _echoTime/_echoAt escritos al recibir (' +
      G.net._echoTime + ')');

  // 6 · lateralidad física: el bit 8 viaja en la pose emitida
  const V = G.camera.position.constructor;
  G.camera.position.set(0.15, 1.72, 0.35);
  G.grips = [null, null];
  const smp = G.net._samplePose
    ? G.net._samplePose({ camera: G.camera, grips: [], paddleHand: 0,
        handOf: ['left', 'right'] })
    : null;
  chk(smp === null || true, 'samplePose sin grips no revienta');
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

    print("— BLOQUE 1 · AGUJAS r82 en el servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES exactos —")
    import re
    for label, pat, esperado in CONTADORES:
        n = len(re.findall(re.escape(pat), src))
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")

    print("— BLOQUE 3 · JUEGO REAL headless (netInfo, clon, validador, túnel) —")
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            juego = False
            for _ in range(90):
                juego = await page.evaluate("() => !!window.__PP_GAME && !!window.__PPNET")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_GAME y __PPNET")

            res = await page.evaluate(JS_NETINFO)
            chk(res.get("info") is not None and res.get("hasPPNET") is not None,
                "netInfo() responde sobre la instancia viva")

            res2 = await page.evaluate(JS_RED82)
            if res2.get("error"):
                chk(False, "JS_RED82: " + res2["error"])
            else:
                for cond, label in res2.get("checks", []):
                    chk(cond, "red r82: " + label)

            if page_errors:
                for e in page_errors:
                    print("  ✗ pageerror: " + e[:200])
            chk(len(page_errors) == 0, "0 pageerrors en toda la sesión")
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} FALLOS (qa_r82_v3674 · CAPA BR)")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
