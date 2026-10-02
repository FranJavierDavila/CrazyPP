#!/usr/bin/env python3
"""Verificación headless v2.25 — rigor multijugador (los bugs del usuario):
  1) SIN DOBLE ESPEJO: la pala y la bola del rival aparecen en el lado
     LEJANO de la mesa (antes el doble transform las ponía en TU lado).
     Emisión en CRUDO + espejo UNA vez en recepción (pala, bola, golpeos,
     spin y botes).
  2) SINCRONÍA POR PUNTO DE VISTA: el invitado ve el marcador/sacador/ganador
     en SU perspectiva (antes invertidos) y MENSAJES regenerados en local.
  3) MEGAFONÍA DEL INVITADO: el invitado anuncia marcador y fin de partido
     (antes callaba: sin voz ni sonidos de puntuación en online).
  4) VOZ ENTRE JUGADORES: la llamada WebRTC la inicia el INVITADO hacia el
     ID de la sala (antes el anfitrión se llamaba a sí mismo: nadie oía a
     nadie) y el micrófono se pide en 2D (hostRoom/joinRoom), no en VR.
  5) OWNER instantáneo en el invitado al recibir golpeo + sin fuga de
     _pendingHits.
Estáticos + protocolo con cable virtual FakeConn<->FakeConn entre dos
NetLink (host e invitado simulados sobre la misma instancia, por fases).
"""
import asyncio, json, sys, re
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

src = open(HTML, encoding="utf-8").read()
fails = []

# ---------------- estáticos sobre la build ----------------
def static_check():
    # 4) la llamada de voz SOLO en la rama del invitado
    n_call = len(re.findall(r"this\.peer\.call\(NetLink\.ROOM_PREFIX", src))
    if n_call != 1: fails.append(f"peer.call debe aparecer 1 vez (invitado), hay {n_call}")
    if "this.role === 'guest' && this.peer" not in src:
        fails.append("la llamada de voz no está guardada por rol invitado")
    # micrófono temprano en crear/unirse (2D) + rescates de audio en red
    n_early = len(re.findall(r"this\.initVoice\(\)\.catch\(\(\) => \{ /\* sin voz", src))
    if n_early < 3: fails.append(f"initVoice temprano esperado >=3 (host/join/wireConn), hay {n_early}")
    if "this.game?.audio?.kick();  // v2.25: rescate de audio al abrir la sesión" not in src:
        fails.append("falta el kick de audio al abrir la sesión online")
    # 1) emisión en crudo (sin transformar al enviar)
    if "NetLink.rawPos(gp.position)" not in src or "NetLink.rawQuat(gp.quaternion)" not in src:
        fails.append("tick() no emite la pose en crudo")
    if "p: NetLink.rawPos(g.ball.pos)," not in src or "v: NetLink.rawPos(g.ball.vel)," not in src:
        fails.append("sendHit/tick no emiten la bola en crudo")
    # spin espejado al recibir
    if "NetLink.spinFromNet(s.s, ball.spin)" not in src or "NetLink.spinFromNet(h.s, g.ball.spin)" not in src:
        fails.append("el spin no se espeja al recibir")
    # 5) sin fuga de _pendingHits en el invitado
    if "if (this.role === 'host') this._pendingHits.push(d);" not in src:
        fails.append("el invitado sigue encolando golpeos (fuga)")
    # remapeo de causas
    if "static remapCause" not in src or "CAUSE_SWAP" not in src:
        fails.append("falta el remapeo de causas por punto de vista")

MOCK_PEER = """() => {
    // PeerJS simulado con CABLE: call() queda registrado para verificar
    // quién llama y a qué id; emitCall para simular llamadas entrantes.
    window.__peers = []; window.__conns = []; window.__calls = [];
    window.__callArgs = [];
    class FakeConn {
        constructor() {
            this.open = false; this.sent = []; this._cbs = {};
            window.__conns.push(this);
        }
        on(ev, cb) { this._cbs[ev] = cb; return this; }
        emitOpen() { this.open = true; this._cbs.open && this._cbs.open(); }
        send(m) { this.sent.push(m); }
        close() { this.open = false; this._cbs.close && this._cbs.close(); }
        emitData(m) { this._cbs.data && this._cbs.data(m); }
    }
    class FakeCall {
        constructor() { this._cbs = {}; window.__calls.push(this); }
        on(ev, cb) { this._cbs[ev] = cb; return this; }
        answer() { this._cbs.stream && queueMicrotask(() => this._cbs.stream({ fake: true })); }
        close() {}
    }
    window.Peer = class {
        constructor(id) {
            this.id = id; this._cbs = {};
            window.__peers.push(this);
            queueMicrotask(() => this._cbs.open && this._cbs.open(id || 'peer-auto'));
        }
        on(ev, cb) { this._cbs[ev] = cb; return this; }
        connect() {
            const c = new FakeConn();
            queueMicrotask(() => c.emitOpen());
            return c;
        }
        call(id, stream) {
            window.__callArgs.push({ id, hasStream: !!stream });
            return new FakeCall();
        }
        destroy() { this._cbs.close && this._cbs.close(); }
        reconnect() {}
        emitConnection(conn) { this._cbs.connection && this._cbs.connection(conn); }
        emitCall(call) { this._cbs.call && this._cbs.call(call); }
    };
    window.__FakeConn = FakeConn;
    window.__FakeCall = FakeCall;
}"""

# Capturar megafonía/sonidos sin tocar el resto del juego
SPY_AUDIO = """() => {
    const g = window.__game;
    g.__ann = []; g.__points = []; g.__apla = []; g.__ohh = [];
    g.audio.announce = (t, f) => { g.__ann.push({ t: String(t), f: !!f }); };
    g.audio.point = (w) => { g.__points.push(w); };
    g.audio.applause = (w) => { g.__apla.push(w); };
    g.audio.ohh = () => { g.__ohh.push(1); };
    return true;
}"""

async def main():
    static_check()
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
            "--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4200)
        await page.evaluate(MOCK_PEER)
        ok = await page.evaluate("() => !!window.__game && !!window.__NetLink")
        if not ok: fails.append("no hay __game/__NetLink")

        # ============ FASE A · LADO ANFITRIÓN ============
        await page.evaluate(SPY_AUDIO)
        host = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            // sesión online LADO ANFITRIÓN con conn simulado
            net.role = 'host'; net.code = 'AB2CD'; net.online = true;
            net.conn = new window.__FakeConn(); net.conn.emitOpen();
            g.startOnlineSession();             // rama anfitrión -> startOnlineMatch
            return { state: g.rules.state, server: g.rules.server,
                     owner: net.owner, opp: g.rules.oppLabel };
        }""")
        if host["server"] != "player" or host["state"] != "serve":
            fails.append(f"anfitrión no arranca con su saque: {json.dumps(host)}")
        if host["owner"] != "host": fails.append(f"owner inicial: {json.dumps(host)}")
        if host["opp"] != "tu rival": fails.append(f"oppLabel online: {json.dumps(host)}")

        # A1) tick del anfitrión: pose EN CRUDO + sync host-relativo
        a1 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            g.grips[0].position.set(0.2, 1.0, -0.3);
            g.grips[0].quaternion.set(0, 0, 0, 1);
            g.controllerPaddles[0].active = true; g.paddleHand = 0;
            net.conn.sent.length = 0;
            net.tick(0.05);
            const pkts = net.conn.sent.slice();
            net.conn.sent.length = 0;
            return { pkts, spin: [g.ball.spin.x, g.ball.spin.y, g.ball.spin.z] };
        }""")
        pkt = next((q for q in a1["pkts"] if q.get("k") == "p"), None)
        if not pkt: fails.append(f"el anfitrión no emite 'p': {a1}")
        else:
            pad = pkt.get("pad")
            if not pad or abs(pad[0] - 0.2) > 1e-6 or abs(pad[2] - (-0.3)) > 1e-6:
                fails.append(f"la pose NO viaja en crudo: {pad}")
            if not pad or abs(pad[3] * pad[3] + pad[4] * pad[4] + pad[5] * pad[5] + pad[6] * pad[6] - 1) > 1e-6:
                fails.append(f"quaternion mal formado: {pad}")
            y = pkt.get("y")
            if not y or y.get("sv") != "player":
                fails.append(f"sync host-relativo: {y}")

        # A2) golpeo del invitado (CRUDO) -> anfitrión espeja UNA vez
        a2 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            // rallye abierto en el anfitrión: el jugador (host) golpeó último
            g.rules.state = 'rally'; g.rules.lastHitter = 'player';
            g.rules.isServeBall = false; g.rules.serveOwnPending = false;
            g.rules.mustBounceOpp = true; g.rules.validBounce = true;
            net.onData({ k: 'h', sv: 0, p: [0.3, 1.0, -0.3], v: [0.2, 0.4, -2.6],
                         s: [0.4, 1.0, -0.2] });
            net.drainNetwork(g);
            return { ball: [+g.ball.pos.x.toFixed(3), +g.ball.pos.y.toFixed(3), +g.ball.pos.z.toFixed(3)],
                     vel: [+g.ball.vel.z.toFixed(2)],
                     spin: [+g.ball.spin.x.toFixed(2), +g.ball.spin.y.toFixed(2), +g.ball.spin.z.toFixed(2)],
                     owner: net.owner, lastHitter: g.rules.lastHitter };
        }""")
        # (0.3, 1.0, -0.3) -> espejo UNA vez: (-0.3, 1.0, -2.9) — lado LEJANO
        if a2["ball"] != [-0.3, 1.0, -2.9]:
            fails.append(f"golpeo del invitado mal espejado: {a2['ball']} (esperado [-0.3, 1.0, -2.9])")
        if a2["spin"] != [-0.4, 1.0, 0.2]:
            fails.append(f"spin sin espejar: {a2['spin']}")
        if a2["owner"] != "guest" or a2["lastHitter"] != "ai":
            fails.append(f"registro del golpeo: {json.dumps(a2)}")

        # A3) pala remota dibujada en el lado lejano (transform único al pintar)
        a3 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            net.onData({ k: 'p', pad: [0.25, 1.05, -0.35, 0, 0, 0, 1] });
            const rp = net.remotePaddle;
            const N = window.__NetLink;
            const V3 = g.ball.pos.constructor;
            const Qt = g.menuGroup.quaternion.constructor;
            const p = N.posFromNet(rp.p, new V3());
            const q = N.quatFromNet(rp.q, new Qt());
            return { z: +p.z.toFixed(3), x: +p.x.toFixed(3),
                     farSide: p.z < -2.8,
                     qRot: Math.abs(q.w) < 1e-6 && Math.abs(q.y - 1) < 1e-6 };
        }""")
        if not a3["farSide"] or a3["z"] != -2.85:
            fails.append(f"la pala del rival no cae en el lado lejano: {json.dumps(a3)}")
        if not a3["qRot"]:
            fails.append(f"la orientación de la pala no se gira 180°: {json.dumps(a3)}")

        # A4) bote del invitado en SU campo (guest z=-2.3 lejos de él) -> en el
        # anfitrión cae en el campo CERCANO del anfitrión ('player')
        a4 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            g.events.length = 0;
            net.onData({ k: 'p', e: [['T', 0.1, 0.76, -2.3]] });
            net.drainNetwork(g);
            const ev = g.events.find((e) => e.type === 'table');
            return ev ? { side: ev.side, z: +ev.pos.z.toFixed(2) } : null;
        }""")
        if not a4 or a4["side"] != "player" or a4["z"] != -0.9:
            fails.append(f"bote del rival mal remapeado: {a4}")

        # A5) punto del anfitrión: intent capturado + send-once en el sync
        a5 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            g.processIntents(g.rules.applyPoint('player', 'doble golpe'));
            const capt = net.lastPoint;
            net.tick(0.05);
            const withPt = net.conn.sent.find((m) => m.y && m.y.pt) || null;
            const ptSent = withPt ? JSON.parse(JSON.stringify(withPt.y.pt)) : null;
            // 'point' -> 'serve' (intents del árbitro): announce + owner
            g.processIntents(g.rules.update(2.5));
            net.conn.sent.length = 0;    // aislar el segundo tick
            net.tick(0.05);
            const again = net.conn.sent.find((m) => m.y && m.y.pt) || null;
            return { capt, ptSent, sentAgain: !!again,
                     ann: g.__ann.slice(), sp: g.rules.scorePlayer,
                     srv: g.rules.server, owner: net.owner };
        }""")
        if not a5["capt"] or a5["capt"]["w"] != "player" or a5["capt"]["c"] != "doble golpe":
            fails.append(f"el punto no se captura estructurado: {json.dumps(a5['capt'])}")
        if not a5["ptSent"]: fails.append(f"el punto no viaja en el sync: {a5['ptSent']}")
        if a5["sentAgain"]: fails.append("el punto se envía más de una vez (send-once roto)")
        if a5["sp"] != 1: fails.append(f"marcador del anfitrión: {a5['sp']}")
        serve_ann = next((x for x in a5["ann"] if "saque para" in x["t"]), None)
        if not serve_ann or serve_ann["t"] != "1 a 0, saque para ti":
            fails.append(f"megafonía del anfitrión: {json.dumps(a5['ann'])}")
        if a5["srv"] != "player" or a5["owner"] != "host":
            fails.append(f"saque/owner tras el punto: {json.dumps(a5)}")

        # ============ FASE B · LADO INVITADO (misma instancia) ============
        b0 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            net.teardown(); net.role = 'guest'; net.online = true;
            net.conn = new window.__FakeConn(); net.conn.emitOpen();
            g.rules.startMatch('match');        // estado sombra en reposo
            net.owner = 'host';
            g.__ann.length = 0; g.__points.length = 0;
            return true;
        }""")

        # B1) primer sync del anfitrión (su saque 0-0): el invitado NO sostiene
        b1 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            net.onData({ k: 'p', y: { st: 'serve', sv: 'player', sp: 0, sa: 0,
                                      md: 'match', ow: 'host', rh: 0 } });
            return { srv: g.rules.server, sp: g.rules.scorePlayer,
                     msg: g.rules.message, mode: g.mode };
        }""")
        if b1["srv"] != "ai":
            fails.append(f"el invitado cree que saca él (perspectiva): {json.dumps(b1)}")
        if b1["sp"] != 0: fails.append(f"marcador sombra inicial: {json.dumps(b1)}")

        # B2) punto del anfitrión (1-0, causa 'doble golpe'): el invitado lo ve
        # como punto del RIVAL, con chime perdedor y mensaje en su perspectiva
        b2 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            net.onData({ k: 'p', y: { st: 'point', sv: 'player', sp: 1, sa: 0,
                                      md: 'match', ow: 'host', rh: 2,
                                      pt: { w: 'player', c: 'doble golpe', rh: 2 } } });
            return { sp: g.rules.scorePlayer, sa: g.rules.scoreAi,
                     msg: g.rules.message,
                     pts: g.__points.slice(), msgState: g.rules.state };
        }""")
        if b2["sp"] != 0 or b2["sa"] != 1:
            fails.append(f"marcador del invitado SIN perspectiva (yo={b2['sp']}, rival={b2['sa']}): esperado 0-1")
        if b2["msg"] != "Punto para tu rival · doble golpe":
            fails.append(f"mensaje del punto sin perspectiva: '{b2['msg']}'")
        if b2["pts"] != [False]:
            fails.append(f"chime del punto mal perspective (esperado [False]): {b2['pts']}")

        # B3) siguiente saque (del invitado): announce local "0 a 1, saque para ti"
        b3 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            g.__ann.length = 0;
            net.onData({ k: 'p', y: { st: 'serve', sv: 'ai', sp: 1, sa: 0,
                                      md: 'match', ow: 'guest', rh: 0 } });
            return { srv: g.rules.server, msg: g.rules.message,
                     ann: g.__ann.slice() };
        }""")
        if b3["srv"] != "player":
            fails.append(f"saque del invitado no reflejado: {json.dumps(b3)}")
        if b3["msg"] != "Tu saque · GATILLO para lanzar y golpear":
            fails.append(f"mensaje de saque propio: '{b3['msg']}'")
        if not any(x["t"] == "0 a 1, saque para ti" for x in b3["ann"]):
            fails.append(f"el invitado NO anuncia el marcador: {json.dumps(b3['ann'])}")

        # B4) golpeo del invitado: emisión EN CRUDO (el anfitrión espejará)
        b4 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            g.ball.pos.set(0.3, 1.0, -0.3);
            g.ball.vel.set(0.2, 0.4, -2.6);
            g.ball.spin.set(0.4, 1.0, -0.2);
            net.conn.sent.length = 0;
            net.sendHit(false);
            const h = net.conn.sent.find((m) => m.k === 'h');
            return { h: h ? { p: h.p, v: h.v, s: h.s, sv: h.sv } : null,
                     owner: net.owner };
        }""")
        h = b4["h"]
        if not h: fails.append("el invitado no emite su golpeo")
        else:
            if h["p"] != [0.3, 1.0, -0.3] or h["v"] != [0.2, 0.4, -2.6]:
                fails.append(f"el golpeo del invitado NO va en crudo: {h}")
            if h["s"] != [0.4, 1.0, -0.2]: fails.append(f"spin del golpeo: {h}")
            if h["sv"] != 0: fails.append(f"sv del golpeo de rallye: {h}")
        if b4["owner"] != "guest": fails.append(f"owner tras golpeo propio: {b4['owner']}")

        # B5) golpeo del anfitrión recibido: owner cambia AL INSTANTE y sin fuga
        b5 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            net.onData({ k: 'h', sv: 0, p: [0, 1, 0], v: [0, 0, 1], s: [0, 0, 0] });
            const pend = net._pendingHits.length;
            return { owner: net.owner, pend };
        }""")
        if b5["owner"] != "host": fails.append(f"owner no cambia al recibir golpeo del rival: {b5}")
        if b5["pend"] != 0: fails.append(f"el invitado encola golpeos (fuga): {b5}")

        # B6) causa remapeada: el anfitrión gana con 'doble bote: tu rival no
        # llegó' (el invitado no llegó) -> el invitado lo cuenta desde SU lado
        b6 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            net.onData({ k: 'p', y: { st: 'point', sv: 'player', sp: 2, sa: 0,
                                      md: 'match', ow: 'host', rh: 5,
                                      pt: { w: 'player', c: 'doble bote: tu rival no llegó', rh: 5 } } });
            const N = window.__NetLink;
            return { msg: g.rules.message, sp: g.rules.scorePlayer, sa: g.rules.scoreAi,
                     swap1: N.remapCause('no la devolviste', true),
                     swap2: N.remapCause('golpeaste tu propio campo', true),
                     neutral: N.remapCause('doble golpe', true) };
        }""")
        if b6["msg"] != "Punto para tu rival · doble bote: no llegaste":
            fails.append(f"causa remapeada incorrecta: '{b6['msg']}'")
        if b6["sp"] != 0 or b6["sa"] != 2:
            fails.append(f"marcador 0-2 sin perspectiva: {json.dumps(b6)}")
        if b6["swap1"] != "tu rival no la devolvió" or b6["swap2"] != "tu rival golpeó su campo" or b6["neutral"] != "doble golpe":
            fails.append(f"tabla de causas: {json.dumps(b6)}")

        # B7) fin de partido ganado por el anfitrión (host-rel 'player'): el
        # invitado pierde — fanfarria perdedora + announce en su perspectiva
        b7 = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            g.__ann.length = 0; g.__apla.length = 0;
            let fanfare = null;
            g.startFanfare = (w) => { fanfare = w; };
            net.onData({ k: 'p', y: { st: 'over', sv: 'player', sp: 11, sa: 5,
                                      md: 'match', ow: 'host', rh: 0, wn: 'player' } });
            return { fanfare, ann: g.__ann.slice(), apla: g.__apla.slice(),
                     sp: g.rules.scorePlayer, msg: g.rules.message };
        }""")
        if b7["fanfare"] is not False:
            fails.append(f"el invitado celebra una derrota: {json.dumps(b7)}")
        if not any("Partido para tu rival" in x["t"] for x in b7["ann"]):
            fails.append(f"anuncio de derrota ausente: {json.dumps(b7['ann'])}")

        # ============ FASE C · VOZ (invitado llama al ID de la sala) ============
        # En este entorno headless getUserMedia queda COLGADO: el tope de 4 s
        # de initVoiceWithCap debe dispararse y llamar IGUALMENTE con el stream
        # silencioso de respaldo (la voz del rival llegará). En la Quest real
        # el micro responde y se envía el micro.
        await page.evaluate("() => { window.__game.net.teardown(); window.__callArgs.length = 0; window.__calls.length = 0; }")
        voz = await page.evaluate("""() => new Promise((res) => {
            const g = window.__game;
            const net = g.net;
            net.joinRoom('ZZ9TQ');           // micro temprano + peer simulado
            setTimeout(() => {
                const args = window.__callArgs.slice();
                res({ calls: window.__calls.length, args,
                      mic: !!net.micStream, voice: net.voiceState,
                      status: net.status, role: net.role });
            }, 5200);
        })""")
        if voz["role"] != "guest": fails.append(f"joinRoom no pone rol invitado: {voz}")
        if voz["status"] != "online": fails.append(f"sesión invitado: {voz}")
        if voz["calls"] < 1:
            fails.append(f"el invitado no inició la llamada de voz (tope roto): {json.dumps(voz)}")
        else:
            if not any(a["id"] == "ppxr3-ZZ9TQ" for a in voz["args"]):
                fails.append(f"la llamada no va al ID de la sala: {json.dumps(voz['args'])}")
            if not all(a["hasStream"] for a in voz["args"]):
                fails.append(f"la llamada va sin stream (ni siquiera el silencioso): {json.dumps(voz['args'])}")

        # C2) el anfitrión responde a la llamada entrante (wireCall + stream)
        await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            net.teardown(); net.role = 'host'; net.code = 'ZZ9TQ';
            const call = new window.__FakeCall();
            net.wireCall(call);
            if (call._cbs.stream) call._cbs.stream({ fake: true });
        }""")
        await page.wait_for_timeout(150)
        c2 = await page.evaluate("""() => {
            const g = window.__game;
            return { voice: g.net.voiceState, audio: !!g.net.remoteAudio };
        }""")
        if c2["voice"] != "on" or not c2["audio"]:
            fails.append(f"respuesta a la llamada entrante: {json.dumps(c2)}")

        # capturas del banco: el panel del invitado con marcador propio
        shot = await page.evaluate("""() => {
            const g = window.__game;
            g.net.teardown();
            g.rules.startMatch('match');
            g.connected = [true, true];
            g.toggleMenu();
            g.renderer.xr.isPresenting = false;
            g.camera.position.set(0, 0.16, 0.75);
            g.camera.lookAt(0, 0.16, 0);
            g.camera.updateMatrixWorld(true);
            g.renderer.render(g.scene, g.camera);
            const d = g.renderer.domElement.toDataURL('image/png');
            g.renderer.xr.isPresenting = true;
            return d;
        }""")
        import base64 as b64
        png = b64.b64decode(shot.split(",", 1)[1])
        open("/home/z/my-project/download/captura-v225-banco.png", "wb").write(png)

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    if errors: fails.append("hubo errores de página")
    if fails:
        print("FALLOS:")
        for f in fails: print("  -", f)
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
