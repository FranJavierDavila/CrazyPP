#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r157 · ARNÉS EN VIVO contra Pages (https://franjavierdavila.github.io/
CrazyPP/game.html) — prueba DEFINITIVA de que el despliegue contiene
MI PERFIL completo: tarjeta en el vestíbulo, ficha, EDITAR con las 5
pestañas (nombre/país/avatar/marco/datos), 65 países clicables, telemetría
y borrado en DATOS, AJUSTES sin la tarjeta «PERFIL Y DATOS» retirada y el
raíl de altura restaurado. Sin servidor local: TODO contra producción.
Patrón: test_r156_perfil.py (nav + menuClick real por índice)."""
import sys

URL = 'https://franjavierdavila.github.io/CrazyPP/game.html?probe=r157live'


def main():
    from playwright.sync_api import sync_playwright

    fails = []
    ok = 0
    perr = []

    def chk(cond, msg):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(msg)

    def nav(page, pid, tab=None):
        page.evaluate('''([pid, tab]) => {
            const g = window.__game;
            g.menuOpen = true;
            g.menuPage = pid;
            if (tab) g._peTab = tab;
            g.drawMenu();
        }''', [pid, tab])
        page.wait_for_timeout(150)

    def click_id(page, rid):
        for _ in range(2):
            r = page.evaluate('''(rid) => {
                const g = window.__game;
                const i = (g.menuRects || []).findIndex((r) => r && r.id === rid);
                if (i < 0) return 'sin rect: ' + rid;
                g.menuClick(i, null);
                return 'ok';
            }''', rid)
            if r == 'ok':
                return 'ok'
            nav(page, page.evaluate('() => window.__game.menuPage'),
                page.evaluate('() => window.__game._peTab || undefined'))
        return r

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--use-gl=swiftshader'])
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: perr.append(str(e)))
        page.goto(URL, wait_until='load', timeout=60_000)
        for _ in range(60):
            if page.evaluate('() => !!window.__game'):
                break
            page.wait_for_timeout(1_000)
        chk(page.evaluate('() => !!window.__game'), 'EN VIVO: __game arranca')
        page.wait_for_timeout(4_000)

        # 1 · VESTÍBULO: la tarjeta MI PERFIL existe y RESPONDE (click real)
        nav(page, 'main')
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        chk('page:perfil' in ids, 'EN VIVO vestíbulo: tarjeta MI PERFIL presente')
        chk(click_id(page, 'page:perfil') == 'ok' and
            page.evaluate('() => window.__game.menuPage') == 'perfil',
            'EN VIVO: click MI PERFIL → ficha')

        # 2 · FICHA → EDITAR PERFIL
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        chk('page:perfil_edit' in ids, 'EN VIVO ficha: botón EDITAR PERFIL')
        chk(click_id(page, 'page:perfil_edit') == 'ok' and
            page.evaluate('() => window.__game.menuPage') == 'perfil_edit',
            'EN VIVO: click EDITAR → editor')

        # 3 · Las 5 pestañas + país REAL clicable (65) + nombre
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        for t in ['nombre', 'pais', 'avatar', 'marco', 'datos']:
            chk('petab:' + t in ids, f'EN VIVO editor: pestaña {t}')
        chk(click_id(page, 'petab:pais') == 'ok', 'EN VIVO: click pestaña PAÍS')
        page.wait_for_timeout(150)
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        n_paises = len([i for i in ids if i and i.startswith('ppais:')])
        chk(n_paises >= 60, f'EN VIVO país: {n_paises} banderas clicables (≥60)')
        chk(click_id(page, 'ppais:FR') == 'ok', 'EN VIVO: click bandera FR (escoger país)')
        chk(click_id(page, 'petab:nombre') == 'ok', 'EN VIVO: click pestaña NOMBRE')
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        chk('pname' in ids, 'EN VIVO nombre: editor del nombre presente')

        # 4 · DATOS: telemetría + borrado (el antiguo PERFIL Y DATOS)
        chk(click_id(page, 'petab:datos') == 'ok', 'EN VIVO: click pestaña DATOS')
        page.wait_for_timeout(150)
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        for rid in ['tele', 'reset', 'pguardar']:
            chk(rid in ids, f'EN VIVO datos: control {rid}')
        chk(click_id(page, 'tele') == 'ok', 'EN VIVO: click toggle telemetría')

        # 5 · AJUSTES SIN «PERFIL Y DATOS» + raíl de altura restaurado
        nav(page, 'opts')
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        chk('page:optsPerfil' not in ids, 'EN VIVO ajustes: SIN tarjeta PERFIL Y DATOS')
        chk('page:optsRendi' in ids and 'page:optsPala' in ids,
            'EN VIVO ajustes: resto de categorías intacto')
        nav(page, 'optsSala')
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        if 'page:optsSalaMesa' in ids:
            chk(click_id(page, 'page:optsSalaMesa') == 'ok', 'EN VIVO: click subvista MESA')
            page.wait_for_timeout(150)
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        chk('mesa_altoy' in ids, 'EN VIVO sala›mesa: raíl de altura (deslizador restaurado)')

        chk(not perr, f'EN VIVO pageerrors: {perr[:3]}')
        browser.close()

    print(f'\nEN VIVO (Pages producción): {ok}/{ok + len(fails)} OK')
    if fails:
        for f in fails:
            print('  ✗ ' + f)
        sys.exit(1)


if __name__ == '__main__':
    main()
