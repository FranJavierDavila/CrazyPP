#!/usr/bin/env python3
"""Verificación headless v2.19: multijugador online (PeerJS simulado) + voz.
  - PeerJS incrustado disponible
  - menú con pestañas: AJUSTES / MULTIJUGADOR / teclado de código
  - crear sala (Peer simulado) → código válido → estado 'waiting'
  - conexión del invitado simulada → sesión online (oppLabel 'tu rival')
  - protocolo: pose recibida, bola por red, golpeo del rival aplicado al
    anfitrión (marco espejo), sync de reglas sombra en el invitado
  - matemática del espejo: ida y vuelta posición/quaternion
  - voz: toggle de micro sin crash (getUserMedia falla en headless → 'denied')
  - colgar → vuelta a partido local contra la CPU
"""
import asyncio, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

MOCK_PEER = """() => {
    // PeerJS simulado: suficiente para el flujo crear/unirse/recibir
    window.__peers = []; window.__conns = []; window.__calls = [];
    class FakeConn {
        constructor() {
            this.open = false;
            this.sent = [];
            this._cbs = {};
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
            // microtarea: los timers anidados son poco fiables en headless
            queueMicrotask(() => this._cbs.open && this._cbs.open(id || 'peer-auto'));
        }
        on(ev, cb) { this._cbs[ev] = cb; return this; }
        connect() {
            const c = new FakeConn();
            queueMicrotask(() => c.emitOpen());
            return c;
        }
        call() { return new FakeCall(); }
        destroy() { this._cbs.close && this._cbs.close(); }
        reconnect() {}
        emitConnection(conn) { this._cbs.connection && this._cbs.connection(conn); }
    };
    window.__FakeConn = FakeConn;
}"""

async def click_rect(page, rid):
    return await page.evaluate(f"""() => {{
        const g = window.__game;
        const idx = g.menuRects.findIndex((r) => r.id === '{rid}');
        if (idx < 0) return false;
        g.menuClick(idx);
        return true;
    }}""")

async def main():
    errors, fails = [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4200)
        await page.evaluate(MOCK_PEER)

        # --- 1) PeerJS disponible y red inicial off ---
        base = await page.evaluate("""() => {
            const g = window.__game;
            return { peer: typeof Peer !== 'undefined',
                     status: g.net.status, online: g.net.online,
                     opp: g.rules.oppLabel };
        }""")
        if not base["peer"]: fails.append("PeerJS no cargado")
        if base["status"] != "off" or base["online"]: fails.append(f"red inicial: {base}")

        # --- 2) menú con pestañas ---
        await page.evaluate("""() => {
            const g = window.__game;
            g.connected[0] = true; g.connected[1] = true;
            g.toggleMenu();
        }""")
        ids = (await page.evaluate("() => window.__game.menuRects.map((r) => r.id)"))
        for need in ('tab:main', 'tab:multi', 'close', 'trail', 'amb'):
            if need not in ids: fails.append(f"falta {need} en página principal")

        # --- 3) pestaña MULTIJUGADOR: crear sala con Peer simulado ---
        if not await click_rect(page, 'tab:multi'): fails.append("pestaña multi no clicable")
        mids = await page.evaluate("() => window.__game.menuRects.map((r) => r.id)")
        for need in ('net:host', 'net:join', 'tab:main', 'close'):
            if need not in mids: fails.append(f"falta {need} en página multi")
        if not await click_rect(page, 'net:host'): fails.append("botón CREAR SALA no está")
        await page.wait_for_timeout(80)
        created = await page.evaluate("""() => {
            const g = window.__game;
            return { st: g.net.status, code: g.net.code,
                     role: g.net.role, peerId: window.__peers[0]?.id };
        }""")
        import re
        if created["st"] != "waiting": fails.append(f"crear sala: {created}")
        if not re.fullmatch(r"[A-Z0-9]{5}", created["code"] or ""):
            fails.append(f"código inválido: {created}")
        if created["peerId"] != "ppxr3-" + created["code"]:
            fails.append(f"id de sala mal formado: {created}")

        # --- 4) el 'invitado' se conecta (simulado) → sesión online ---
        await page.evaluate("""() => {
            const conn = new window.__FakeConn();
            window.__peers[0].emitConnection(conn);
            setTimeout(() => conn.emitOpen(), 0);
        }""")
        await page.wait_for_timeout(120)
        onl = await page.evaluate("""() => {
            const g = window.__game;
            return { online: g.net.online, role: g.net.role, st: g.net.status,
                     opp: g.rules.oppLabel, state: g.rules.state,
                     owner: g.net.owner, msg: g.rules.message };
        }""")
        if not onl["online"] or onl["role"] != "host": fails.append(f"conexión no establecida: {onl}")
        if onl["opp"] != "tu rival": fails.append(f"oppLabel: {onl}")
        if onl["state"] != "serve": fails.append(f"partido online no arrancado: {onl}")
        if onl["owner"] != "host": fails.append(f"dueño de la bola: {onl}")

        # --- 5) protocolo: pose del rival + bola por red + golpeo aplicado ---
        proto = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            // pose del rival (marco anfitrión): debe aparecer espejada
            net.onData({ k: 'p', pad: [0.2, 1.0, -1.0, 0, 0, 0, 1] });
            const rp = net.remotePaddle;
            // bola del rival (dueño 'guest')
            net.owner = 'guest';
            net.onData({ k: 'p', b: { p: [0.1, 1.2, -1.4], v: [0, -1, 2.4], s: [0, 0, 0] } });
            // golpeo del rival: se aplica en el anfitrión y abre el rallye
            g.rules.state = 'rally'; g.rules.lastHitter = 'player';
            g.rules.isServeBall = false; g.rules.serveOwnPending = false;
            net.onData({ k: 'h', sv: 0, p: [-0.3, 1.1, -1.9], v: [0.2, 0.4, -2.6], s: [0, 0, 0] });
            net.drainNetwork(g);
            return {
                padLocal: rp ? [rp.p[0], rp.p[2]] : null,
                ball: [+g.ball.pos.x.toFixed(2), +g.ball.pos.y.toFixed(2), +g.ball.pos.z.toFixed(2)],
                state: g.rules.state, owner: net.owner,
                lastHitter: g.rules.lastHitter,
            };
        }""")
        # la pose se almacena en MARCO DE RED; el espejo se aplica al renderizar
        if proto["padLocal"] != [0.2, -1.0]:
            fails.append(f"pose rival en marco red: {proto['padLocal']} != [0.2, -1.0]")
        # golpe en (−0.3, 1.1, −1.9) -> local (0.3, 1.1, −1.3)
        if proto["ball"][0] != 0.3 or proto["ball"][2] != -1.3:
            fails.append(f"golpeo rival mal aplicado: {proto['ball']}")
        if proto["state"] != "rally" or proto["lastHitter"] != "ai":
            fails.append(f"registro de golpeo rival: {json.dumps(proto)}")

        # --- 6) sync al invitado (reglas sombra) — probamos applySync directo ---
        # v2.25: SINCRONÍA POR PUNTO DE VISTA. El anfitrión envía etiquetas
        # host-relativas ('player'=anfitrión). En el invitado se intercambian:
        # sp<->sa y server invertido. Con y={sv:'ai', sp:1, sa:0}: el anfitrión
        # va 1-0 abajo... en marcos del anfitrión "ai" (invitado) marca 0 y
        # "player" (anfitrión) 1; el invitado ve MI marcador = y.sa = 0 y saca
        # el invitado (sv 'ai' en marco del anfitrión = invitado = yo).
        sync = await page.evaluate("""() => {
            const g = window.__game;
            const net = g.net;
            net.role = 'guest';       // fingir el lado invitado para applySync
            const before = { sp: g.rules.scorePlayer, mode: g.mode };
            net.applySync({ st: 'rally', sv: 'ai', sp: 1, sa: 0,
                            md: 'match', ow: 'guest', rh: 2 });
            const after = { sp: g.rules.scorePlayer, sa: g.rules.scoreAi,
                            st: g.rules.state, srv: g.rules.server,
                            mode: g.mode, owner: net.owner };
            net.role = 'host';        // restaurar
            return { before, after };
        }""")
        # en el invitado: scorePlayer (yo) = y.sa = 0; scoreAi (rival) = y.sp = 1
        if sync["after"]["sp"] != 0 or sync["after"]["sa"] != 1:
            fails.append(f"marcador sombra sin perspectiva: {json.dumps(sync)}")
        if sync["after"]["srv"] != "player":
            fails.append(f"sacador sombra sin perspectiva: {json.dumps(sync)}")
        if sync["after"]["st"] != "rally":
            fails.append(f"reglas sombra no aplicadas: {json.dumps(sync)}")
        if sync["after"]["owner"] != "guest": fails.append(f"owner por sync: {json.dumps(sync)}")

        # --- 7) matemática del espejo: ida y vuelta ---
        mir = await page.evaluate("""() => {
            const g = window.__game;
            const N = window.__NetLink;
            const V3 = g.ball.pos.constructor;
            const out = new V3();
            const p = new V3(0.4, 1.3, -0.8);
            const net = N.posToNet(p);
            N.posFromNet(net, out);
            return { okP: out.distanceTo(p) < 1e-6 };
        }""")
        # (la comprobación de quaternion se hace aparte con sintaxis segura)
        mir2 = await page.evaluate("""() => {
            const g = window.__game;
            const N = window.__NetLink;
            const Qt = g.menuGroup.quaternion.constructor;
            const E = g.menuGroup.rotation.constructor;
            const q = new Qt().setFromEuler(new E(0.2, 0.5, -0.3, 'YXZ'));
            const a = N.quatToNet(q);
            const back = N.quatFromNet(a, new Qt());
            // la ida y vuelta puede devolver -q: MISMA rotación (doble cubiertura)
            const dot = Math.abs(back.x * q.x + back.y * q.y + back.z * q.z + back.w * q.w);
            return { ok: dot > 1 - 1e-9, dot: +dot.toFixed(9) };
        }""")
        if not mir.get("okP"): fails.append(f"espejo posición ida/vuelta: {mir}")
        if not mir2.get("ok"): fails.append(f"espejo quaternion ida/vuelta: {mir2}")

        # --- 8) colgar (lado anfitrión): vuelta al partido local contra la CPU ---
        await page.evaluate("""() => {
            const g = window.__game;
            const idx = g.menuRects.findIndex((r) => r.id === 'net:hangup');
            if (idx >= 0) g.menuClick(idx);
        }""")
        await page.wait_for_timeout(80)
        end = await page.evaluate("""() => {
            const g = window.__game;
            return { online: g.net.online, opp: g.rules.oppLabel,
                     state: g.rules.state, st: g.net.status };
        }""")
        if end["online"]: fails.append(f"sigue online tras colgar: {end}")
        if end["opp"] != "la CPU": fails.append(f"oppLabel tras colgar: {end}")

        # --- 9) teclado del código: cancelar sala, escribir ABC29 y conectar ---
        await page.evaluate("""() => { const g = window.__game; if (g.menuOpen) g.toggleMenu();
                                       g.rules.state = 'serve'; g.toggleMenu(); }""")
        if not await click_rect(page, 'tab:multi'): fails.append("tab multi (2ª vez)")
        mids2 = await page.evaluate("() => window.__game.menuRects.map((r) => r.id)")
        # tras colgar el estado es 'off': sin net:cancel, con net:host y net:join
        if 'net:join' not in mids2: fails.append(f"multi sin net:join: {mids2}")
        if not await click_rect(page, 'net:join'): fails.append("ir al teclado")
        jids = await page.evaluate("() => window.__game.menuRects.map((r) => r.id)")
        for need in ('key:A', 'key:9', 'key:del', 'key:ok', 'key:cancel', 'close'):
            if need not in jids: fails.append(f"falta tecla {need}")
        for ch in ('A', 'B', 'C', '2', '3'):
            await click_rect(page, f'key:{ch}')
        code = await page.evaluate("() => window.__game._joinCode")
        if code != "ABC23": fails.append(f"código tecleado: {code}")
        if not await click_rect(page, 'key:del'): fails.append("tecla borrar")
        code = await page.evaluate("() => window.__game._joinCode")
        if code != "ABC2": fails.append(f"borrado: {code}")
        await click_rect(page, 'key:9')
        ok = await click_rect(page, 'key:ok')
        await page.wait_for_timeout(80)
        joined = await page.evaluate("""() => {
            const g = window.__game;
            return { st: g.net.status, role: g.net.role, page: g.menuPage,
                     online: g.net.online, opp: g.rules.oppLabel };
        }""")
        if not ok or joined["role"] != "guest" or joined["online"] is not True:
            fails.append(f"unirse con código: {json.dumps(joined)}")
        if joined["opp"] != "tu rival": fails.append(f"invitado oppLabel: {joined}")

        # --- 10) voz: toggle de micro en página multi (invitado online) ---
        await page.evaluate("""() => {
            const g = window.__game;
            g.menuPage = 'multi';
            g.drawMenu();
        }""")
        voz = await page.evaluate("""() => {
            const g = window.__game;
            const before = g.net.micOn;
            const idx = g.menuRects.findIndex((r) => r.id === 'net:mic');
            let clicked = false;
            if (idx >= 0) { g.menuClick(idx); clicked = true; }
            return { clicked, before, after: g.net.micOn, voice: g.net.voiceState };
        }""")
        if not voz["clicked"] or voz["before"] == voz["after"]:
            fails.append(f"toggle de voz: {voz}")

        # --- 11) colgar (invitado) y capturas de páginas del menú ---
        await page.evaluate("""() => {
            const g = window.__game;
            const idx = g.menuRects.findIndex((r) => r.id === 'net:hangup');
            if (idx >= 0) g.menuClick(idx);
        }""")
        await page.wait_for_timeout(80)
        end2 = await page.evaluate("""() => ({ online: window.__game.net.online,
                                               opp: window.__game.rules.oppLabel })""")
        if end2["online"] or end2["opp"] != "la CPU":
            fails.append(f"colgar invitado: {end2}")

        # --- 12) capturas de las páginas del menú ---
        await page.evaluate("""() => {
            const g = window.__game;
            g.menuPage = 'main'; g.toggleMenu();
            if (g.menuOpen) g.toggleMenu();   // asegurar cerrado y reabrir
            g.rules.state = 'serve';
            g.toggleMenu();
            g.menuGroup.position.set(0.55, 1.05, -0.75);
            g.menuGroup.lookAt(2.2, 1.5, 1.4);
            g.menuGroup.updateMatrixWorld(true);
        }""")
        await page.wait_for_timeout(300)
        await page.screenshot(path="/home/z/my-project/scripts/preview_v219_menu_main.png")
        await page.evaluate("""() => {
            const g = window.__game;
            g.menuPage = 'multi';
            g.drawMenu();
        }""")
        await page.wait_for_timeout(200)
        await page.screenshot(path="/home/z/my-project/scripts/preview_v219_menu_multi.png")
        await page.evaluate("""() => {
            const g = window.__game;
            g.menuPage = 'join';
            g._joinCode = 'AB2';
            g.drawMenu();
        }""")
        await page.wait_for_timeout(200)
        await page.screenshot(path="/home/z/my-project/scripts/preview_v219_menu_join.png")

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    print("crear sala:", json.dumps(created))
    print("conexión:", json.dumps(onl))
    print("protocolo:", json.dumps(proto))
    if fails:
        print("FALLOS:", *fails, sep="\n  - ")
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
