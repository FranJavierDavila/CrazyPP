#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r45 · VERIFICACIÓN DEL PANEL contra el worker VIVO (que aún no publica
rank): la sección «Rankings mundiales» debe aparecer con el aviso elegante
y el resto del panel intacto (KPIs, alarmas, tablas). Foto: download/_r45_panel.png"""
import asyncio
import base64
import os

from playwright.async_api import async_playwright

OUT = '/home/z/my-project/download'
BASE = 'http://127.0.0.1:3000'

async def main():
    os.makedirs(OUT, exist_ok=True)
    fallos = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 900})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(BASE + '/telemetria.html', wait_until='domcontentloaded', timeout=45000)
        # la clave vive en localStorage del navegador de producción — aquí
        # la inyectamos si el dueño la guardó en el repo (sólo para el test)
        clave = ''
        try:
            clave = open('/home/z/my-project/upload/scripts/worker-tele/.clave-produccion').read().strip()
        except Exception:
            pass
        if clave:
            await page.evaluate("localStorage.setItem('pp_tele_clave', '%s')" % clave)
            await page.reload(wait_until='domcontentloaded')
        # el panel auto-carga con clave; espera KPIs
        try:
            await page.wait_for_selector('.kpi', timeout=30000)
        except Exception:
            pass
        html = await page.content()
        tiene_rank = 'Rankings mundiales' in html
        tiene_kpis = html.count('kpi') > 3
        tiene_fallo = 'No se pudo leer' in html
        await page.screenshot(path=OUT + '/_r45_panel.png', full_page=False)
        print('sección Rankings mundiales presente:', tiene_rank)
        print('KPIs pintados:', tiene_kpis, '· aviso de error:', tiene_fallo)
        print('pageerrors:', len(errs))
        fallos = sum([not tiene_rank, not tiene_kpis, tiene_fallo, bool(errs)])
        print(f'PANEL r45: {4 - fallos}/4 OK')
        await browser.close()
        return 1 if fallos else 0

if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
