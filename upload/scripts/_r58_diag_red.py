#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnóstico: qué peticiones corren tras cargar game.html (networkidle
no llega — sup1 se agota en el goto)."""
import asyncio

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        pendientes = []
        page.on("request", lambda r: pendientes.append(("req", r.url[:110])))
        page.on("requestfinished", lambda r: pendientes.append(("fin", r.url[:110])))
        page.on("requestfailed", lambda r: pendientes.append(("FALLO", r.url[:110] + ' · ' + str(r.failure)[:40])))
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        for i in range(4):
            await page.wait_for_timeout(4000)
            nuevos = [e for e in pendientes][-6:]
            print(f'--- t={(i+1)*4}s · eventos={len(pendientes)} ---')
            for e in nuevos:
                print('   ', e[0], e[1])
        await browser.close()


asyncio.run(main())
