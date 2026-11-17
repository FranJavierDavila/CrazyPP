#!/usr/bin/env python3
"""Trazador: ¿quién escribe rules.state='serve' después de startChamp ('champtest')?"""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=estacion_orbital"

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader",
                                      "--disable-web-security", "--no-sandbox"])
    page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
    page.add_init_script("""
      window.__STATE_LOG = [];
      // interceptor temprano: se instala cuando exista __PP_GAME.rules
      (function poll() {
        const G = window.__PP_GAME;
        if (G && G.rules && !G.rules.__ppSpy) {
          G.rules.__ppSpy = true;
          let v = G.rules.state;
          Object.defineProperty(G.rules, 'state', {
            get() { return v; },
            set(nv) {
              if (nv !== v) {
                window.__STATE_LOG.push({
                  from: v, to: nv, t: performance.now() | 0,
                  stack: (new Error().stack || '').split('\\n').slice(1, 6).join(' | ')
                });
              }
              v = nv;
            }, configurable: true });
          window.__STATE_LOG.push({ from: '?', to: v, t: performance.now() | 0, stack: 'SPY-INSTALLED' });
        }
        setTimeout(poll, 5);
      })();
    """)
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(12)
    log = page.evaluate("window.__STATE_LOG.slice(0, 40)")
    for e in log:
        print(f"  {e['t']:>6}ms {e['from']} → {e['to']}   {e['stack'][:220]}")
    browser.close()
