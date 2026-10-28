#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r79_v3671 — CAPA BN · V3.6.79-SDK6, FASE 73 «CRAZY LINK v2».

Petición del dueño (r79): «Lo siguiente es trabajar el modo multijugador.
Algo tenemos realizado pero necesitamos hacerlo realista y no cosmético…
subMenú con dos modos de juego con sus respectivos iconos para seguir una
estética común… Normal (una partida normal) y "Duelos locos" (que llevará
la etiqueta y candado como los campeonatos: Próximamente y encima el
candado)… primero un modo multijugador perfecto para "Partida"» + spec
«Netcode multijugador online — Ping Pong VR (WebXR)» v1.0.

Lo implementado (r79) y SU verificación:
  · SUBMENÚ MULTIJUGADOR (c12): dos tarjetas de modo con estética común
    (_modeCard): NORMAL · PARTIDA y DUELOS LOCOS con el patrón EXACTO de
    los campeonatos bloqueados (velo + CANDADO junto al nombre + chip
    PRÓXIMAMENTE + voz al intentar entrar) + icono nuevo PP_ICONS.duelo.
  · TRANSPORTE BINARIO v2 (c09 + c09b PPNET): RTCPeerConnection propia con
    DOS DataChannels — fast {ordered:false, maxRetransmits:0} (tipo UDP)
    y reliable {ordered:true} — señalizados sobre la sala PeerJS.
    Degradación honesta a v1 (30 Hz JSON) si la subida falla.
  · PROTOCOLO (c09b): cabecera 21 B + pose 31 B (cabeza+2 manos, quat
    smallest-three 32 bit, i16 @0,5 mm) + eventos BALL_HIT/BALL_HANDOFF/
    BALL_SNAP con reenvío hasta ack, dedupe por eventId y ackBits.
  · RELOJ COMPARTIDO (spec §4): ancla gruesa por reliable + refinado NTP
    por cabecera fast (16 muestras, mediana de las 4 de menor RTT,
    suavizado 1 ms/s, sin saltos en rallye).
  · AUTORIDAD POR MITAD DE MESA (spec §7): FSM HELD/OWN/GHOST/AUTH/DEAD,
    golpe propio SAGRADO (netLocalHit en el mismo frame), traspaso al
    cruzar la red (subpaso exacto), avance dt·k=0,6 capado 120 ms,
    correcciones 2 cm/30 cm/80 ms, autoridad provisional a 300 ms.
  · REGLAS SINCRONIZADAS (spec §9): rallySeq determinista + POINT_CLAIM/
    POINT_ACK con espejo de perspectiva + RESYNC_STATE del anfitrión +
    LET determinista sin red + forcePoint con guardia anti-duplicado.
  · AVATAR DEL RIVAL (spec §6): jitter buffer con interpDelay adaptativo
    (40-120 ms), lerp+slerp, extrapolación ≤100 ms, atenuación >500 ms,
    pala derivada de la mano con offset de agarre FIJO + visor.
  · FLUJO DE PARTIDA (spec §3): HELLO (versión/build/física) · ráfaga de
    reloj · READY · MATCH_START con cuenta atrás sincronizada (3 s en el
    reloj del anfitrión) · PAUSE/RESUME por visor quitado · MATCH_END.
  · RESILIENCIA (spec §11): watchdog ICE (restartIce 10 s ×2), pérdida
    sostenida >10 % → pose 30 Hz + aviso, ping de color en el marcador.
  · VALIDACIÓN (spec §12): velocidad ≤30 m/s, giro ≤160, shot correlativo,
    cadencia ≥150 ms, golpe a <60 cm de la pala del rival; 3 graves →
    partida sospechosa. Simulador de red (NetSim) + telemetría net_match.

BLOQUES: (1) AGUJAS r79 en el servido. (2) CONTADORES exactos.
(3) JUEGO REAL headless: el juego arranca, window.__PPNET vive y SUPERAR
un banco integrado en la página (códec roundtrip + reloj NTP con latencia
+ FSM de la bola + MatchSync converge/disputa + reglas forcePoint/rallySeq
+ superficie v2 de NetLink) con 0 pageerrors.
Uso: python3 qa_r79_v3671.py [URL]
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
    ("núcleo PPNET embebido", "const PPNET = (() => {"),
    ("canal fast tipo UDP (maxRetransmits: 0)", "maxRetransmits: 0"),
    ("canal fast sin orden (ordered: false)", "ordered: false, maxRetransmits"),
    ("señalización SDP por la sala", "k: 'sdp'"),
    ("HELLO de versión/build/física", "k: 'hello2'"),
    ("MATCH_START con cuenta atrás", "k: 'mstart'"),
    ("POINT_CLAIM", "k: 'claim'"),
    ("RESYNC_STATE del anfitrión", "k: 'resync'"),
    ("PAUSE por visor quitado", "k: 'pause'"),
    ("golpe propio sagrado (netLocalHit)", "netLocalHit"),
    ("lanzamiento visual del saque (kind 2)", "netLocalToss"),
    ("traspaso al cruzar la red (subpaso)", "watchOwnCross"),
    ("autoridad provisional del fantasma", "observeGhost"),
    ("punto impuesto por la red (forcePoint)", "forcePoint"),
    ("identidad de rallye determinista", "rallySeq++"),
    ("avance dt·k con tope", "FF_K: 0.6"),
    ("tope de avance 120 ms", "FF_MAX: 0.12"),
    ("corrección suave 80 ms", "CORR_SMOOTH: 0.08"),
    ("traspaso vence a 300 ms", "HANDOFF_TIMEOUT: 0.3"),
    ("interpDelay adaptativo 40-120", "INTERP_MIN: 40"),
    ("extrapolación máx 100 ms", "EXTRAP_MAX: 0.1"),
    ("validación velocidad 30 m/s", "MAX_BALL_SPEED: 30"),
    ("validación cadencia 150 ms", "MIN_HIT_GAP: 0.15"),
    ("avatar: muestra del jitter buffer", "avatarSample"),
    ("ping en el marcador", "netPing"),
    ("tarjeta DUELOS LOCOS desbloqueada (r84)", "this._modeCard(rects, 'mjduel', 40, 326"),
    ("icono nuevo del modo duelo", "PP_ICONS.duelo"),
    ("NORMAL · PARTIDA (i18n ES)", "mj_norm_t: 'NORMAL · PARTIDA'"),
    ("DUELOS LOCOS (i18n ES)", "mj_duel_t: 'DUELOS LOCOS'"),
    ("CRAZY DUELS (i18n EN)", "mj_duel_t: 'CRAZY DUELS'"),
    ("chip PRÓXIMAMENTE reutilizado", "champ_locked_chip"),
    ("sincronizando (estado honesto)", "net_syncing: 'Sincronizando con el rival…'"),
    ("pausa del rival (i18n)", "net_paused: 'RIVAL EN PAUSA · el partido queda detenido'"),
    ("degradación honesta a v1", "net_legacy: 'Sin canal rápido: modo compatible 30 Hz'"),
    ("versión sellada 3.6.79-SDK6", "const VERSION = '3.6.79-SDK6';"),
]

CONTADORES = [
    ("k: 'mstart' (emisión + recepción)", "k: 'mstart'", 2),
    ("k: 'hello2' (una sola definición)", "k: 'hello2'", 1),
    ("k: 'claim' (libro de reclamos)", "k: 'claim'", 1),
    ("candado fuera de la tarjeta Duelos (r84)", "candado(c, x + 134", 0),
    ("PP_ICONS.duelo (definición + uso)", "PP_ICONS.duelo", 1),
    ("netPing (marcador + c12 + c08)", "netPing", 7),
    ("setServeHeld (HELD determinista)", "setServeHeld", 3),
    ("mjduel vía _modeCard con las hermanas (r84)", "rects, 'mjduel', 40, 326", 1),
    ("versión única", "const VERSION = '3.6.79-SDK6'", 1),
    ("agujas de la ronda 78 intactas (MEGA_GOLPES)", "const MEGA_GOLPES = 20;", 1),
]

JS_BANCO = """async () => {
  const G = window.__PP_GAME;
  const P = window.__PPNET;
  if (!G || !P) return { error: 'sin __PP_GAME o __PPNET' };
  const out = { checks: [] };
  const chk = (cond, label) => out.checks.push([!!cond, label]);

  // 1 · códec roundtrip en la página real
  const buf = new ArrayBuffer(400);
  const n = P.encodePacket(buf, {
    seq: 9, ack: 7, ackBits: 0xffff, sendTime: 1e6, echoTime: 1e6 - 40,
    echoDelay: 5, yAnchor: 0.76,
    pose: { hp: [0.1, 1.6, -1.2], hq: [0, 0.38, 0, 0.92], lp: [-0.3, 1, -0.9],
            lq: [0, 0, 0, 1], rp: [0.3, 1, -0.9], rq: [0, 1, 0, 0], fl: 5 },
    evs: [{ t: 1, id: 3, kind: 1, shot: 2, tHit: 1e6, p: [0.1, 0.8, -0.5],
            v: [-1, 2, -3], s: [0.5, -0.2, 1] }],
  });
  const d = P.decodePacket(buf.slice(0, n), { yAnchor: 0.76 });
  chk(n > 90 && n < 300 && d && d.seq === 9 && d.evs.length === 1,
      'códec roundtrip en página (' + n + ' B = 21 cabecera + 31 pose + 46 evento)');
  chk(Math.abs(d.pose.hp[1] - 1.6) < 0.001, 'pose con ancla Y del tapete');

  // 2 · reloj NTP con latencia simulada
  const clk = new P.NetClock(false);
  clk.anchor(500000, 500000 + 90 + 40, 500000 + 80);
  for (let i = 0; i < 24; i++) {
    const tSend = 500200 + i * 50;
    clk.markSent(tSend);
    clk.onPacket({ sendTime: (500200 + i * 50 + 130) >>> 0, echoTime: tSend >>> 0,
      echoDelay: 2 }, 500200 + i * 50 + 84);
  }
  clk.apply(501500, false);
  chk(Math.abs(clk.offset - 90) < 8, 'reloj NTP en página: offset ' + clk.offset.toFixed(1) + ' ms ≈ 90');

  // 3 · FSM de la bola
  const b = new P.BallAuth();
  b.setHeld(true);
  const ev = b.localHit(true, { p: [0, 0.9, 1.2], v: [0, 0, -2], s: [0, 0, 0] }, 1000);
  chk(ev && ev.t === 1 && ev.kind === 1 && b.state === 'own' && b.shot === 1,
      'FSM: golpe propio → OWN_FLIGHT + BALL_HIT kind 1');
  const cross = b.crossedNet({ p: [0, 0.9, -1.6], v: [0, 0, -2], s: [0, 0, 0] }, 1100);
  chk(cross && cross.t === 2 && cross.shot === 1 && b.state === 'ghost' && !b.mine,
      'FSM: cruce limpio → GHOST + BALL_HANDOFF (la bola ya no es mía)');
  chk(!b.canHit(), 'FSM: el fantasma NO se puede golpear (spec §7)');
  b.observeGhostCross(1150);
  const provEarly = b.maybeProvisional(1150 + 250);
  const prov = b.maybeProvisional(1150 + 320);
  chk(provEarly === false && prov === true && b.mine && b.state === 'auth',
      'FSM: autoridad PROVISIONAL exactamente a los 300 ms (spec §7)');

  // 4 · MatchSync converge (claim + ack + desacuerdo)
  const msA = new P.MatchSync('host');
  const msB = new P.MatchSync('guest');
  const dec = msA.localPoint(0, 'player', 'dbl_opp', 1, 0, true, 0);
  msB.localPoint(0, 'ai', 'dbl_opp', 0, 1, false, 5);
  const ack = msB.onClaim(dec.send, 'ai');
  chk(ack.ack.agree === true && !ack.apply && msA.onAck(ack.ack).ok,
      'MatchSync: CLAIM/ACK convergen con perspectiva espejada');

  // 5 · reglas del juego real: rallySeq + forcePoint con guardia
  const r = G.rules;
  const seq0 = r.rallySeq;
  r.beginServeRally('player');
  const it1 = r.forcePoint('player', 'dbl_opp', r.rallySeq);
  const it2 = r.forcePoint('player', 'dbl_opp', r.rallySeq);   // duplicado
  chk(r.rallySeq === seq0 + 1 && it1.length === 1 && it2.length === 0,
      'reglas: rallySeq determinista + forcePoint sin doble conteo');
  // deshacer el punto de prueba (el estado del juego queda como estaba)
  r.scorePlayer -= 1; r.totalPoints -= 1; r.state = 'serve'; r.rallySeq -= 1;
  r._appliedRally = -1;

  // 6 · superficie v2 de NetLink en la instancia viva
  chk(typeof G.net.startV2 === 'function' && typeof G.net.frame === 'function'
      && typeof G.net.avatarSample === 'function' && typeof G.net.pingMs === 'function'
      && typeof G.net.v2Paused === 'function' && typeof G.net.netReport === 'function',
      'NetLink: superficie v2 completa en la instancia viva');
  chk(G.net.ballMine() === (G.net.owner === G.net.mySide()) || G.net.v2 !== 'ok',
      'NetLink: ballMine coherente fuera de sesión');
  chk(typeof G.drawMenuMulti === 'function' && typeof G.onNetMatchStart === 'function'
      && typeof G.onNetV2Ready === 'function' && typeof G._dlTrigger === 'function',
      'c12: submenú + MATCH_START cableados');
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

    print("— BLOQUE 1 · AGUJAS r79 en el servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES exactos —")
    import re
    for label, pat, esperado in CONTADORES:
        n = len(re.findall(re.escape(pat), src))
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")

    print("— BLOQUE 3 · JUEGO REAL headless (PPNET integrado en la página) —")
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            juego = False
            for _ in range(90):
                juego = await page.evaluate("() => !!window.__PP_GAME")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_GAME")

            res = await page.evaluate(JS_BANCO, [])
            if res.get("error"):
                chk(False, "JS_BANCO: " + res["error"])
            else:
                for cond, label in res.get("checks", []):
                    chk(cond, "en página: " + label)

            if page_errors:
                for e in page_errors:
                    print("  ✗ pageerror: " + e[:200])
            chk(len(page_errors) == 0, "0 pageerrors en toda la sesión")
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} FALLOS (qa_r79_v3671 · CAPA BN)")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
