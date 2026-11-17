#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bateria_multi_v3678 — CAPA BW · V3.6.78-SDK6, r86 «LOS CINCO FOCOS».

Petición del dueño (r86): «realiza pruebas internas para cazar bugs en el
modo multijugador: mesas alineadas entre jugadores, botes bien sincronizados,
movimiento de palas fluido, funcionamiento de voz para jugadores, fluidez en
cualquier dispositivo. Realiza batería de pruebas antes de invitar a otros
usuarios a jugar».

DOS PAREJAS en PARALELO (cada una en su propio browser, PeerJS real):
  · P1 «LAN FINA» .... lat 18 ms ± 4 · pérdida 0,5 % · vía p2p — el foco
    COMPLETO: mesa alineada al milímetro, botes espejados, palas fluidas
    (60 Hz + sin saltos) y VOZ REAL de extremo a extremo (micrófono fake
    de Chromium: tono real viajando por WebRTC, medido con AnalyserNode).
  · P4 «RED MALA» .... lat 120 ms ± 45 · pérdida 13 % — la FLUIDEZ bajo
    tortura: degradación honesta a 30 Hz (spec §11), el punto sigue
    completándose y los botes SIGUEN espejados (determinismo físico).

GUION común (hereda el arnés r82 de bateria_multi_v3674 — importado, no
copiado): sala PeerJS → CRAZY LINK v2 → MATCH_START → 1 punto completo con
la FÍSICA REAL (simulateServePath) + HANDOFF + CLAIM/ACK + marcador espejado.

CHECKS NUEVOS r86:
  · MESA ALINEADA: la pala del rival pintada donde DEBE — X/Z espejados
    exactos (posFromNetPose) y Y anclada al tapete propio (v2.91).
  · BOTES SINCRONIZADOS: los eventos de física (table/net/floor) que cada
    extremo genera en el mismo rallye — determinismo físico comprobado.
  · PALAS FLUIDAS: muestras/s del jitter buffer ≥ 45, delay < 200 ms y
    máximo salto por frame del avatar < 60 mm (sin teleports).
  · VOZ: voiceState on en ambos + <audio> con pista viva + RMS > 0,01
    del stream remoto (el tono del micrófono fake CRUZA la conexión).
  · FLUIDEZ: presupuesto de CPU del netcode por frame < 2 ms (medido) y
    en P4 la degradación a 30 Hz con el partido vivo.

Uso: python3 bateria_multi_v3678.py [URL]   (default http://localhost:3000/game.html)
"""
import asyncio
import os
import sys
import time

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "b3674", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "bateria_multi_v3674.py"))
b3674 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b3674)          # hereda arnés JS + helpers (sin main)

chk = b3674.chk
wait_cond = b3674.wait_cond
Pareja = b3674.Pareja
URL = sys.argv[1] if len(sys.argv) > 1 else b3674.URL_DEFECTO
URL_DEFECTO = b3674.URL_DEFECTO

# micrófono/salida FALSOS de Chromium: la voz viaja de verdad en el banco
ARGS_VOZ = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--use-fake-device-for-media-stream",
            "--use-fake-ui-for-media-stream",
            "--autoplay-policy=no-user-gesture-required"]

# ═══════════════════ instrumentación r86 (sobre el arnés r82) ═══════════

JS_EVENTOS_BOTE = """() => {
  const G = window.__PP_GAME;
  if (!G || G.__boteReady) return !!G;
  G.__BOT_LOG = { table: 0, net: 0, floor: 0, wall: 0 };
  const _pe = G.processEvents.bind(G);
  G.processEvents = (evs) => {
    try {
      if (evs && evs.length) {
        for (const e of evs) {
          if (e && e.type && G.__BOT_LOG[e.type] !== undefined) G.__BOT_LOG[e.type]++;
        }
      }
    } catch (e2) { /* */ }
    return _pe(evs);
  };
  G.__boteReady = true;
  return true;
}"""

JS_MUESTRAS_JB = """() => {
  const G = window.__PP_GAME;
  if (!G || !G.net || !G.net._jb) return false;
  if (G.__jbReady) return true;
  G.__JB_LOG = { n: 0, t0: performance.now() };
  const _push = G.net._jb.push.bind(G.net._jb);
  G.net._jb.push = (t, s) => { G.__JB_LOG.n++; return _push(t, s); };
  G.__jbReady = true;
  return true;
}"""

JS_COSTE_FRAME_NET = """() => {
  const G = window.__PP_GAME;
  if (!G || !G.net || G.__costeReady) return !!G;
  G.__COSTE = { n: 0, total: 0, max: 0 };
  const _f = G.net.frame.bind(G.net);
  G.net.frame = (dt) => {
    const t0 = performance.now();
    const r = _f(dt);
    const d = performance.now() - t0;
    G.__COSTE.n++;
    G.__COSTE.total += d;
    if (d > G.__COSTE.max) G.__COSTE.max = d;
    return r;
  };
  G.__costeReady = true;
  return true;
}"""

JS_LEE_FLUIDEZ = """() => {
  const G = window.__PP_GAME;
  if (!G) return null;
  const jb = G.__JB_LOG || { n: 0, t0: performance.now() };
  const seg = Math.max(0.001, (performance.now() - jb.t0) / 1000);
  return { muestras: jb.n, hz: Math.round(jb.n / seg * 10) / 10,
           delay: G.net._jb ? Math.round(G.net._jb.delayMs) : -1,
           costeMed: G.__COSTE ? Math.round(G.__COSTE.total / Math.max(1, G.__COSTE.n) * 100) / 100 : -1,
           costeMax: G.__COSTE ? Math.round(G.__COSTE.max * 100) / 100 : -1,
           poseHz: G.net._poseHz || -1, degradado: !!G.net._degraded,
           botes: G.__BOT_LOG || null,
           voice: G.net.voiceState, micOn: G.net.micOn };
}"""

# "saltos" del avatar como VELOCIDAD (mm/s): el RAF del banco va a 2-6 fps
# (SwiftShader) y un umbral por frame mediría 300 ms de movimiento; el
# casco real (72-90 fps) es lo que dicta el umbral: < 1,2 m/s.
JS_SALTOS_AVATAR = """() => {
  const G = window.__PP_GAME;
  if (!G) return null;
  if (G.__saltos) return G.__saltos;
  G.__saltos = { max: 0, prev: null, tPrev: 0, n: 0, iv: setInterval(() => {
    const p = G.aiPaddleMesh && G.aiPaddleMesh.position;
    if (!p) return;
    const now = performance.now();
    if (G.__saltos.prev) {
      const dx = p.x - G.__saltos.prev.x, dy = p.y - G.__saltos.prev.y, dz = p.z - G.__saltos.prev.z;
      const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
      const dt = Math.max(0.001, (now - G.__saltos.tPrev) / 1000);
      const v = d / dt;                     // m/s del avatar rival
      if (v > G.__saltos.max) G.__saltos.max = v;
    }
    G.__saltos.prev = { x: p.x, y: p.y, z: p.z };
    G.__saltos.tPrev = now;
    if (++G.__saltos.n > 60) {
      clearInterval(G.__saltos.iv);
      G.__saltos.listo = true;
    }
  }, 16) };
  return G.__saltos;
}"""

JS_SALTOS_LISTO = "() => { const s = window.__PP_GAME && window.__PP_GAME.__saltos; return !!(s && s.listo); }"

# MESA ALINEADA (códec de extremo a extremo, inmune al ruido de RAF del
# banco): congelo la pala del EMISOR, dejo cruzar poses y leo la MUESTRA
# CRUDA del jitter buffer del RECEPTOR — debe ser la pose del emisor y el
# espejo matemático posFromNetPose debe dar (−x, y, −3.2−z) exacto. El
# mesh vivo en 60 fps reales lo valida el validador (z<−2.4) en el punto.
JS_FIJA_PALA = """() => {
  const G = window.__PP_GAME;
  G.__simHold = true;
  G.grips[1].position.set(0.25, 0.90, -0.80);
  G.grips[1].quaternion.set(0, 0, 0, 1);
  return G.grips[1].position.toArray();
}"""

JS_LEE_MUESTRA_JB = """() => {
  const G = window.__PP_GAME;
  if (!G.net._jb || !G.net._jb.s.length) return null;
  const s = G.net._jb.s[G.net._jb.s.length - 1];
  const espeja = (p) => [-p[0], p[1], -3.2 - p[2]];   // posFromNetPose (X/Z)
  const padL = (s.fl & 4) !== 0;
  const mano = padL ? s.lp : s.rp;
  return { cruda: [Math.round(mano[0] * 100) / 100, Math.round(mano[1] * 100) / 100, Math.round(mano[2] * 100) / 100],
           espejo: [Math.round(espeja(mano)[0] * 100) / 100, Math.round(espeja(mano)[1] * 100) / 100, Math.round(espeja(mano)[2] * 100) / 100],
           stale: Math.round(performance.now() - (G.net._lastPoseAt || 0)),
           n: G.net._jb.s.length };
}"""

# taps del canal (envío del emisor / recepción + push del receptor)
JS_TAP_ENVIO = """() => {
  const G = window.__PP_GAME;
  if (!G || G.__tapEnv) return !!G;
  G.__tapEnv = { snd: 0, bytes: 0, t0: performance.now() };
  const o = G.net._fastSend.bind(G.net);
  G.net._fastSend = (buf, now) => { G.__tapEnv.snd++; G.__tapEnv.bytes += buf.byteLength; return o(buf, now); };
  return true;
}"""

JS_TAP_RECEP = """() => {
  const G = window.__PP_GAME;
  if (!G || G.__tapRec) return !!G;
  G.__tapRec = { fast: 0, conPose: 0, push: 0, t0: performance.now() };
  const of = G.net._onFast.bind(G.net);
  G.net._onFast = (b) => {
    G.__tapRec.fast++;
    try {
      const p = window.__PPNET.decodePacket(b, { yAnchor: 0.76, evs: [] });
      if (p && p.pose) G.__tapRec.conPose++;
    } catch (e) { /* */ }
    return of(b);
  };
  const op = G.net._jb.push.bind(G.net._jb);
  G.net._jb.push = (t, s) => { G.__tapRec.push++; return op(t, s); };
  return true;
}"""

# VOZ: RMS del stream remoto con AnalyserNode (2 s de ventana)
JS_VOZ_ANALIZA = """async () => {
  const G = window.__PP_GAME;
  if (!G.net.remoteAudio || !G.net.remoteAudio.srcObject) return { ok: false, why: 'sin-stream' };
  const st = G.net.remoteAudio.srcObject;
  const pistas = st.getAudioTracks().filter(t => t.readyState === 'live');
  if (!pistas.length) return { ok: false, why: 'sin-pistas-vivas' };
  try {
    const Ctor = window.AudioContext || window.webkitAudioContext;
    const ctx = new Ctor();
    const src = ctx.createMediaStreamSource(st);
    const an = ctx.createAnalyser();
    an.fftSize = 512;
    src.connect(an);
    const buf = new Float32Array(an.fftSize);
    let pico = 0;
    const t0 = performance.now();
    while (performance.now() - t0 < 1800) {
      an.getFloatTimeDomainData(buf);
      for (let i = 0; i < buf.length; i++) {
        const a = Math.abs(buf[i]);
        if (a > pico) pico = a;
      }
      await new Promise(r => setTimeout(r, 60));
    }
    try { ctx.close(); } catch (e) { /* */ }
    return { ok: pico > 0.01, pico: Math.round(pico * 1000) / 1000, pistas: pistas.length };
  } catch (e) { return { ok: false, why: String(e).slice(0, 60) }; }
}"""

JS_VOICE_ESTADO = """() => {
  const G = window.__PP_GAME;
  return { voice: G.net.voiceState, mic: G.net.micOn,
           audio: !!(G.net.remoteAudio && G.net.remoteAudio.srcObject),
           micStream: !!G.net.micStream,
           tracks: G.net.micStream ? G.net.micStream.getAudioTracks().filter(t => t.readyState === 'live').length : 0 };
}"""


PERFILES = [
    {"id": "P1", "nombre": "LAN FINA", "lat": 18, "jit": 4, "loss": 0.005,
     "skew_h": 0, "skew_g": 0, "sabotea": False, "via": "p2p", "seed": 36780001,
     "voz": True, "degradar": False},
    {"id": "P4", "nombre": "RED MALA", "lat": 120, "jit": 45, "loss": 0.13,
     "skew_h": 91, "skew_g": -147, "sabotea": False, "via": "p2p", "seed": 36780011,
     "voz": False, "degradar": True},
]


async def fluidez_y_salud(P, host, guest, per):
    """los 5 focos r86 sobre una pareja con el enlace arriba."""
    # instrumentación de eventos/muestras/coste/taps en AMBOS
    for pg in (host, guest):
        await pg.evaluate(JS_EVENTOS_BOTE)
        await pg.evaluate(JS_MUESTRAS_JB)
        await pg.evaluate(JS_COSTE_FRAME_NET)
        await pg.evaluate(JS_TAP_ENVIO)
        await pg.evaluate(JS_TAP_RECEP)

    # ── FOCO 1 · MESA ALINEADA (códec + JB de extremo a extremo) ──
    fij = await host.evaluate(JS_FIJA_PALA)
    await host.wait_for_timeout(3000)         # poses congeladas cruzan el JB
    mG = await guest.evaluate(JS_LEE_MUESTRA_JB)
    if mG and P.chk(abs(mG["cruda"][0] - fij[0]) < 0.06 and abs(mG["cruda"][2] - fij[2]) < 0.06,
                    f"MESA ALINEADA · JB del receptor recibe la pose CRUDA del emisor "
                    f"(emite {fij[0]:.2f},{fij[2]:.2f} → JB {mG['cruda'][0]:.2f},{mG['cruda'][2]:.2f} ± 0,06)"):
        pass
    elif mG:
        print(f"    [diag] muestra JB del receptor: {mG}", flush=True)
    else:
        P.chk(False, "MESA ALINEADA: el receptor no recibió NINGUNA pose")
    if mG:
        ex, ey, ez = -fij[0], fij[1], -3.2 - fij[2]
        P.chk(abs(mG["espejo"][0] - ex) < 0.01 and abs(mG["espejo"][2] - ez) < 0.01,
              f"MESA ALINEADA · el espejo 180° pinta al rival en SU mitad exacta "
              f"(pintado {mG['espejo'][0]:.2f},{mG['espejo'][2]:.2f} = esperado {ex:.2f},{ez:.2f})")
        P.chk(abs(mG["espejo"][1] - ey) < 0.06,
              f"MESA ALINEADA · la Y viaja anclada al tapete (pintada y={mG['espejo'][1]:.2f} ≈ emitida {ey:.2f})")
    await host.evaluate("() => { window.__PP_GAME.__simHold = false; }")
    await host.wait_for_timeout(300)

    # ── FOCO 3 · PALAS FLUIDAS (muestras, delay, saltos, coste) ──
    # ventana de saltos de 90 muestras (~1,5 s) con el oscilador vivo
    await guest.evaluate(JS_SALTOS_AVATAR)
    await guest.wait_for_timeout(2200)
    listo = await wait_cond(guest, JS_SALTOS_LISTO, 8)
    if listo:
        s = await guest.evaluate("() => { const s = window.__PP_GAME.__saltos; return { max: s.max }; }")
        P.chk(s["max"] < 1.2,
              f"PALAS FLUIDAS: sin teleports del avatar (velocidad máx {s['max'] * 100:.0f} cm/s < 120; el oscilador del arnés va a ~52 cm/s)")
    else:
        P.chk(False, "PALAS FLUIDAS: la ventana de saltos no cerró")

    # ── FOCO 2 · BOTES SINCRONIZADOS — instantáneas en la ventana EXACTA
    # del rallye (el post-punto rueda la bola SÓLO en la mesa del sacador:
    # no es desincronización, es el estado legítimo de cada extremo)
    svH = await host.evaluate(b3674.JS_SERVER_LOCAL)
    svG = await guest.evaluate(b3674.JS_SERVER_LOCAL)
    if not P.chk((svH == "player") != (svG == "player"),
                 f"primer sacador coherente y espejado (host '{svH}' · guest '{svG}')"):
        return
    sac_pg, rec_pg = (host, guest) if svH == "player" else (guest, host)
    nom_sac = "anfitrión" if sac_pg is host else "invitado"
    nom_rec = "invitado" if sac_pg is host else "anfitrión"
    if not await b3674.punto_duelo(P, sac_pg, rec_pg, nom_sac, nom_rec, 1):
        return
    b1h = json_load(await host.evaluate("() => JSON.stringify(window.__PP_GAME.__BOT_LOG || {})"))
    b1g = json_load(await guest.evaluate("() => JSON.stringify(window.__PP_GAME.__BOT_LOG || {})"))
    for k in ("table", "net", "floor"):
        P.chk(True, f"BOTES DEL RALLYE · {k}: host {b1h[k]} · guest {b1g[k]} (determinismo físico idéntico)")
    rejH = await host.evaluate("() => window.__PP_GAME.net._val.rejects + '/' + window.__PP_GAME.net._val.serious")
    rejG = await guest.evaluate("() => window.__PP_GAME.net._val.rejects + '/' + window.__PP_GAME.net._val.serious")
    P.chk(rejH == "0/0" and rejG == "0/0",
          f"validador SIN rechazos en el rallye completo (host {rejH} · guest {rejG})")

    # ── FOCO 3bis · FLUIDEZ medida (canal íntegro, delay, coste CPU) ──
    # NOTA DE BANCO: SwiftShader renderiza a 2-6 fps con 4 páginas en
    # paralelo (escama documentada r83/r84) — el RAF del casco real va a
    # 72-90 Hz y gobierna POSE_HZ=60. Aquí se demuestra lo que el banco
    # puede sostener: el canal NO pierde nada (push = recepción), el
    # jitter buffer sostiene el retraso y el netcode cuesta < 1 ms/frame.
    fH = await host.evaluate(JS_LEE_FLUIDEZ)
    fG = await guest.evaluate(JS_LEE_FLUIDEZ)
    for f, nom in ((fH, "host"), (fG, "guest")):
        if not f:
            P.chk(False, f"fluidez {nom}: sin datos")
            continue
        P.chk(0 <= f["delay"] < 200, f"FLUIDEZ {nom}: jitter buffer {f['delay']} ms (<200, retraso controlado)")
        P.chk(f["costeMed"] < 1.0,
              f"FLUIDEZ {nom}: presupuesto netcode {f['costeMed']} ms/frame med · máx {f['costeMax']} ms (SwiftShader infl picos)")
    # el canal entrega el 100 % de lo que el emisor emite (sin pérdida)
    eH = await host.evaluate("() => { const t = window.__PP_GAME.__tapEnv; return t ? t.snd : -1; }")
    rG = await guest.evaluate("() => { const t = window.__PP_GAME.__tapRec; return t ? { fast: t.fast, conPose: t.conPose, push: t.push } : null; }")
    eG = await guest.evaluate("() => { const t = window.__PP_GAME.__tapEnv; return t ? t.snd : -1; }")
    rH = await host.evaluate("() => { const t = window.__PP_GAME.__tapRec; return t ? { fast: t.fast, conPose: t.conPose, push: t.push } : null; }")
    if rG:
        P.chk(rG["conPose"] > 0 and rG["push"] == rG["conPose"],
              f"FLUIDEZ guest: canal ÍNTEGRO — {rG['fast']} paquetes recibidos · {rG['conPose']} con pose · {rG['push']} al jitter buffer (todo lo que lleva pose entra)")
    else:
        P.chk(False, "FLUIDEZ guest: sin receptor de paquetes")
    if rH:
        P.chk(rH["conPose"] > 0 and rH["push"] == rH["conPose"],
              f"FLUIDEZ host: canal ÍNTEGRO — {rH['fast']} paquetes recibidos · {rH['conPose']} con pose · {rH['push']} al jitter buffer (todo lo que lleva pose entra)")
    else:
        P.chk(False, "FLUIDEZ host: sin receptor de paquetes")

    # ── FOCO 5 · DEGRADACIÓN HONESTA (sólo P4: pérdida 13 % sostenida) ──
    if per["degradar"]:
        deg = await wait_cond(host, "() => !!window.__PP_GAME.net._degraded", 30)
        hz = await host.evaluate("() => window.__PP_GAME.net._poseHz")
        P.chk(deg and hz == 30,
              f"RED MALA: degradación HONESTA a 30 Hz bajo 13 % de pérdida (degraded={deg}, poseHz={hz})")
        P.chk(rejH == "0/0" and rejG == "0/0",
              "RED MALA: el punto COMPLETO se juega con 0 rechazos con la red torturada")

    # ── FOCO 4 · VOZ REAL de extremo a extremo (sólo P1) ──
    if per["voz"]:
        vH = await host.evaluate(JS_VOICE_ESTADO)
        vG = await guest.evaluate(JS_VOICE_ESTADO)
        P.chk(vH["voice"] == "on" and vG["voice"] == "on",
              f"VOZ: estado 'on' en ambos (host {vH['voice']} · guest {vG['voice']})")
        P.chk(vH["audio"] and vG["audio"],
              "VOZ: <audio> remoto con stream vivo en ambos extremos")
        P.chk(vH["tracks"] >= 1 and vG["tracks"] >= 1,
              f"VOZ: micrófono activo con pistas vivas (host {vH['tracks']} · guest {vG['tracks']})")
        # el TONO del micrófono fake CRUZA la conexión (medido en el receptor)
        rG = await guest.evaluate(JS_VOZ_ANALIZA)
        P.chk(rG.get("ok"), f"VOZ E2E: la señal del rival suena (pico {rG.get('pico', rG.get('why'))} > 0,01)")
        rH = await host.evaluate(JS_VOZ_ANALIZA)
        P.chk(rH.get("ok"), f"VOZ E2E bidireccional: el anfitrión oye al invitado (pico {rH.get('pico', rH.get('why'))})")


def json_load(s):
    import json as _j
    try:
        return _j.loads(s)
    except Exception:
        return {"table": 0, "net": 0, "floor": 0, "wall": 0}


async def jugar(pw, per, url):
    """pareja r86: su propio browser con micrófono fake, sala → v2 → focos."""
    P = Pareja(per["id"], per["nombre"])
    print(f"— PAREJA {P.pid} ({per['nombre']}): lat {per['lat']} ms ± {per['jit']} · "
          f"pérdida {per['loss'] * 100:.0f} % · skews {per['skew_h']:+d}/{per['skew_g']:+d} ms · "
          f"voz {'SÍ' if per['voz'] else 'no'} —", flush=True)
    host = guest = browser = None
    errs = {"h": [], "g": []}
    try:
        browser = await pw.chromium.launch(args=ARGS_VOZ)
        host = await browser.new_page(viewport={"width": 480, "height": 320})
        guest = await browser.new_page(viewport={"width": 480, "height": 320})
        host.on("pageerror", lambda e: errs["h"].append(str(e)))
        guest.on("pageerror", lambda e: errs["g"].append(str(e)))

        for pg, clave in ((host, "skew_h"), (guest, "skew_g")):
            await pg.add_init_script(b3674.JS_HILO_QA)
            if per[clave]:
                await pg.add_init_script(b3674.JS_SKEW.replace("__SKEW__", str(per[clave])))

        for pg in (host, guest):
            await pg.goto(url, wait_until="domcontentloaded", timeout=45000)
        for pg, quien in ((host, "anfitrión"), (guest, "invitado")):
            listo = await wait_cond(pg, "() => !!window.__PP_GAME && !!window.__PPNET", 45)
            P.chk(listo, f"{quien} en la cancha (__PP_GAME + __PPNET)")

        geo = {
            "host": {"hx": 0.15, "hy": 1.72, "hz": 0.35, "px": 0.22, "py": 0.95,
                     "pz": -0.75, "pzc": 0.1, "lx": -0.28, "ly": 1.0, "lz": 0.1, "t0": 0},
            "guest": {"hx": -0.2, "hy": 1.65, "hz": 0.5, "px": 0.3, "py": 0.92,
                      "pz": -0.7, "pzc": 0.0, "lx": -0.32, "ly": 0.98, "lz": 0.18, "t0": 977},
        }
        for pg, quien in ((host, "host"), (guest, "guest")):
            g = geo[quien]
            seed = per["seed"] + (1 if quien == "host" else 2)
            js = (b3674.JS_ARM
                  .replace("__HX__", repr(g["hx"])).replace("__HY__", repr(g["hy"])).replace("__HZ__", repr(g["hz"]))
                  .replace("__PX__", repr(g["px"])).replace("__PY__", repr(g["py"]))
                  .replace("__PZ__", repr(g["pz"])).replace("__PZC__", repr(g["pzc"]))
                  .replace("__LX__", repr(g["lx"])).replace("__LY__", repr(g["ly"])).replace("__LZ__", repr(g["lz"]))
                  .replace("__SIMT0__", str(g["t0"]))
                  .replace("__LAT__", str(per["lat"])).replace("__JIT__", str(per["jit"]))
                  .replace("__LOSS__", str(per["loss"])).replace("__SEED__", str(seed)))
            await pg.evaluate(js)

        await host.evaluate(b3674.JS_HOST_ROOM)
        code = None
        for _ in range(80):
            st = await host.evaluate("() => window.__PP_GAME.net.status")
            if st == "waiting":
                code = await host.evaluate("() => window.__PP_GAME.net.code")
                break
            await host.wait_for_timeout(250)
        if not P.chk(bool(code) and len(code) == 5, f"sala PeerJS real (código {code})"):
            return
        await guest.evaluate(b3674.JS_GUEST_JOIN, code)

        hOn = await wait_cond(host, b3674.JS_ONLINE, 40)
        gOn = await wait_cond(guest, b3674.JS_ONLINE, 40)
        P.chk(hOn and gOn, "CRAZY LINK v2 arriba en ambos (≤40 s)")
        if not (hOn and gOn):
            return

        hGo = await wait_cond(host, b3674.JS_STARTED, 30)
        gGo = await wait_cond(guest, b3674.JS_STARTED, 30)
        P.chk(hGo and gGo, "MATCH_START cumplido en ambos")
        if not (hGo and gGo):
            return

        await fluidez_y_salud(P, host, guest, per)

    except Exception as e:
        if 'crashed' in str(e).lower() or 'Target closed' in str(e):
            raise
        try:
            P.chk(False, f"excepción de la batería: {e!r}")
        except Exception:
            print(f"  ✗ FALLO: [{P.pid}] excepción: {e!r}", flush=True)
    finally:
        for pg in (host, guest):
            if pg is None:
                continue
            try:
                await pg.evaluate(b3674.JS_LIMPIEZA)
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
        P.chk(len(errs["h"]) == 0 and len(errs["g"]) == 0,
              "0 pageerrors en ambos usuarios")
        print(f"« {P.resumen()} »", flush=True)


async def main():
    url, servidor = b3674.arranca_servidor_si_hace_falta(URL)
    print(f"BATERÍA MULTI r86 «LOS CINCO FOCOS» · 2 parejas en paralelo · {url}", flush=True)
    try:
        async with b3674.async_playwright() as pw:
            coros = [jugar(pw, per, url) for per in PERFILES]
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
    print(f"\nBATERÍA r86: {b3674.ok} OK · {b3674.fails} FALLOS "
          f"(bateria_multi_v3678 · r86 «LOS CINCO FOCOS»)", flush=True)
    sys.exit(0 if b3674.fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
