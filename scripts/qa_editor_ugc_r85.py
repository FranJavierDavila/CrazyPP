#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_editor_ugc_r85.py — humo end-to-end de EL TALLER UGC (Playwright, file://)
   1) carga sin pageerrors · 2) plantilla nueva · 3) carga el manifest de halloween
   4) verifica etapas/nodos/título · 5) validar OK · 6) exportar → JSON válido."""
import json, sys
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
URL = 'file://' + RAIZ + '/public/ugc/index.html'
MAN = RAIZ + '/public/championships/halloween/manifest.json'

ok = fallos = 0
def CHK(cond, nombre):
    global ok, fallos
    print(('  [OK]  ' if cond else '  [FALLO] ') + nombre)
    if cond: ok += 1
    else: fallos += 1

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 900})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(400)

    CHK(len(errs) == 0, 'carga inicial sin pageerrors')
    CHK(pg.locator('h1').inner_text().find('TALLER UGC') >= 0, 'cabecera del Taller')

    # plantilla nueva
    pg.click('#btnPlantilla')
    pg.wait_for_timeout(150)
    CHK('Plantilla nueva' in pg.locator('#estado').inner_text(), 'plantilla de cero creada')
    CHK(pg.locator('#listaEtapas .etapa').count() == 5, 'plantilla con 5 etapas')

    # carga el manifest REAL de halloween
    pg.set_input_files('#cargaMan', MAN)
    pg.wait_for_timeout(250)
    st = pg.locator('#estado').inner_text()
    CHK('Halloween' in st, 'manifest de halloween cargado: ' + st.replace('\n', ' '))
    CHK(pg.locator('#f_titulo_es').input_value() == 'Campeonato de Halloween', 'título ES correcto')
    CHK(pg.locator('#f_rival_nombre').input_value() == 'ZOMBI', 'rival ZOMBI')
    CHK(pg.locator('#listaEtapas .etapa').count() == 5, '5 etapas pintadas')
    CHK(pg.locator('#chipsEstados .chip.on').count() == 12, '12 estados del zombi marcados')
    CHK(pg.locator('#listaNodos .liTx').count() == 5, '5 nodos del mapa')

    # validar
    pg.click('#btnValidar')
    pg.wait_for_timeout(150)
    CHK('Sin errores de validación' in pg.locator('#estado').inner_text(), 'validación VERDE del manifest real')

    # abrir la sección CAMINO (está plegada por defecto)
    if 'abierta' not in (pg.locator('#sec-camino').get_attribute('class') or ''):
        pg.click('#sec-camino > h2')
        pg.wait_for_timeout(120)

    # edición viva: renombrar una etapa + añadir/eliminar
    pg.locator('#listaEtapas .etapa input').nth(1).fill('La Cripta Sellada v2')
    pg.wait_for_timeout(80)
    pg.click('#btnAddDuelo')
    pg.wait_for_timeout(120)
    CHK(pg.locator('#listaEtapas .etapa').count() == 6, 'añadir duelo → 6 etapas')
    n_aviso = pg.locator('#infoNodos').inner_text()
    CHK('deben ser EXACTAMENTE 6' in n_aviso, 'aviso de nodos ≠ etapas tras añadir')
    # quitar el añadido (última fila, botón 🗑)
    pg.locator('#listaEtapas .etapa').nth(5).locator('button', has_text='🗑').click()
    pg.wait_for_timeout(120)
    CHK(pg.locator('#listaEtapas .etapa').count() == 5, 'vuelta a 5 etapas')

    # exportar → JSON válido en el diálogo
    pg.click('#btnExportar')
    pg.wait_for_timeout(200)
    pre = pg.locator('#dlgJsonPre').inner_text()
    try:
        data = json.loads(pre)
        exp_ok = True
    except Exception:
        data = {}
        exp_ok = False
    CHK(exp_ok, 'manifest exportado es JSON válido')
    CHK(data.get('id') == 'halloween' and data.get('storage') == 'pp_champ_halloween_*', 'id/storage coherentes')
    CHK(len(data.get('stages', [])) == 5, 'export: 5 etapas')
    CHK(len(data.get('mapa', {}).get('nodos', [])) == 5, 'export: 5 nodos')

    # captura para el worklog
    pg.screenshot(path=RAIZ + '/scripts/_r85_editor_ugc.png', full_page=False)

    CHK(len(errs) == 0, 'cero pageerrors al final (0 fallos de consola)')
    if errs:
        print('   pageerrors:', errs[:3])
    b.close()

print('RESUMEN: %d OK · %d FALLO' % (ok, fallos))
sys.exit(1 if fallos else 0)
