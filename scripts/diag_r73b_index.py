#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_r73b — por qué list() viene vacío: fetch manual + consola."""
import asyncio
import json
import subprocess
import sys
import time
import os
import signal

from playwright.async_api import async_playwright

PORT = 8874
URL = f"http://localhost:{PORT}/game.html"


async def main():
    srv = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd="/home/z/my-project/public",
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )
    time.sleep(1.0)
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
            page = await browser.new_page(viewport={"width": 1280, "height": 720})
            msgs = []
            page.on("console", lambda m: msgs.append(f"[{m.type}] {m.text}"))
            page.on("pageerror", lambda e: msgs.append(f"[pageerror] {e}"))
            await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            for _ in range(120):
                listo = await page.evaluate("() => !!window.__PP_GAME")
                if listo:
                    break
                await page.wait_for_timeout(500)
            # fetch manual del índice y de un manifest
            r = await page.evaluate("""async () => {
                const out = {};
                try {
                    const r1 = await fetch('championships/championships.json');
                    out.idx = { ok: r1.ok, status: r1.status, url: r1.url };
                    const j = await r1.json();
                    out.ids = j.championships.map(c => typeof c === 'string' ? c : c.id);
                    const r2 = await fetch('championships/oeste/manifest.json');
                    out.man = { ok: r2.ok, status: r2.status, url: r2.url };
                } catch (e) { out.err = String(e); }
                return out;
            }""")
            print("fetch manual:", json.dumps(r, ensure_ascii=False))
            await page.wait_for_timeout(2500)
            data = await page.evaluate("() => (window.__PP_GAME.champs.entries||[]).map(e=>({id:e.id,estado:e.estado,error:e.error}))")
            print("entries tras 2.5 s:", json.dumps(data, ensure_ascii=False))
            print("--- consola [champs] y errores ---")
            for m in msgs:
                if "champs" in m.lower() or "error" in m.type if isinstance(m, str) and False else False:
                    pass
            for m in msgs:
                if "[champs" in m or "pageerror" in m or "Failed" in m or "404" in m:
                    print(" ", m[:220])
            await browser.close()
    finally:
        os.killpg(os.getpgid(srv.pid), signal.SIGTERM)


asyncio.run(main())
