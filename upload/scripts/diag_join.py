#!/usr/bin/env python3
"""Sonda: por qué joinRoom se queda en 'joining' con el Peer simulado."""
import asyncio
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

MOCK = """() => {
    window.__log = [];
    class FakeConn {
        constructor(tag) {
            this.open = false; this._cbs = {}; this.tag = tag || 'conn';
            window.__log.push('FakeConn ctor ' + this.tag);
        }
        on(ev, cb) { this._cbs[ev] = cb; return this; }
        emitOpen() { this.open = true; window.__log.push('conn emitOpen'); this._cbs.open && this._cbs.open(); }
        send(m) { this.sent = this.sent || []; this.sent.push(m); }
        close() {}
    }
    window.Peer = class {
        constructor(id) {
            this.id = id; this._cbs = {};
            window.__log.push('Peer ctor ' + (id || 'auto'));
            setTimeout(() => { window.__log.push('peer open fire'); this._cbs.open && this._cbs.open(id || 'peer-auto'); }, 0);
        }
        on(ev, cb) { window.__log.push('peer.on ' + ev); this._cbs[ev] = cb; return this; }
        connect(target) {
            window.__log.push('connect -> ' + target);
            const c = new FakeConn(target);
            window.__log.push('connect: programando timer');
            setTimeout(() => { window.__log.push('conn timer dispara'); try { c.emitOpen(); } catch (e) { window.__log.push('emitOpen ERROR: ' + e.message); } }, 0);
            return c;
        }
        call() { return { on() {}, close() {} }; }
        destroy() { window.__log.push('peer destroy'); }
        reconnect() {}
        emitConnection(conn) { this._cbs.connection && this._cbs.connection(conn); }
    };
    window.__FakeConn = FakeConn;
}"""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: print("PAGEERROR:", e))
        page.on("console", lambda m: print("CONSOLE:", m.text[:200]))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4200)
        await page.evaluate(MOCK)
        r = await page.evaluate("""() => {
            const g = window.__game;
            g.connected[0] = true; g.connected[1] = true;
            g.toggleMenu();
            // flujo: tab multi -> join -> teclear -> ok
            g.menuClick(g.menuRects.findIndex((r) => r.id === 'tab:multi'));
            g.menuClick(g.menuRects.findIndex((r) => r.id === 'net:join'));
            for (const ch of ['A', 'B', '2', '9', 'K']) {
                g.menuClick(g.menuRects.findIndex((r) => r.id === 'key:' + ch));
            }
            const code = g._joinCode;
            g.menuClick(g.menuRects.findIndex((r) => r.id === 'key:ok'));
            return { code, st: g.net.status, role: g.net.role };
        }""")
        print("tras key:ok:", r)
        await page.wait_for_timeout(300)
        r2 = await page.evaluate("""() => ({
            st: window.__game.net.status, online: window.__game.net.online,
            role: window.__game.net.role, log: window.__log,
            nPeers: window.__peers ? window.__peers.length : -1,
        })""")
        print("después de 300 ms:", {k: v for k, v in r2.items() if k != 'log'})
        print("log:", r2["log"])
        await browser.close()

asyncio.run(main())
