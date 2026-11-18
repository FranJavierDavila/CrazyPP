#!/usr/bin/env python3
"""Sonda: ¿el beacon de telemetría dispara 501 contra el sitio estático?
Carga pages-site/game.html en headless 9 s y lista las respuestas /api/."""
import asyncio
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

SITE = '/home/z/my-project/pages-site'


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SITE, **kw)

    def log_message(self, *a):
        pass

    def do_POST(self):  # lo que hace el estático real: 501
        self.send_error(501, 'no POST in static')


httpd = ThreadingHTTPServer(('127.0.0.1', 3017), H)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        pg = await b.new_page()
        pg.on('response', lambda r: print('RESP', r.status, r.request.resource_type, r.url[-60:]) if '/api/' in r.url else None)
        pg.on('requestfailed', lambda r: print('FAIL', r.url[-60:], r.failure) if '/api/' in r.url else None)
        await pg.goto('http://127.0.0.1:3017/game.html', wait_until='domcontentloaded')
        await pg.wait_for_timeout(9000)
        ep = await pg.evaluate('() => window.PP_TELEMETRY_ENDPOINT || null')
        st = await pg.evaluate('() => window.__PP_TELE && { on: window.__PP_TELE.on, q: window.__PP_TELE.st.q.length, sent: window.__PP_TELE.st.sent }')
        print('endpoint:', ep, '· tele:', st)
        await b.close()


asyncio.run(main())
