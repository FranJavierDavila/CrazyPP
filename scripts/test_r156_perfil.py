#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r156 · ARNÉS BROWSER MI PERFIL — sirve public/ en :3008, abre game.html
headless y verifica el apartado nuevo COMPLETO por window.__game:
hub de 6 secciones, ficha, edición REAL por menuClick (país, avatar,
compra con arm de dos toques), economía v2 (IA/P2P/tope diario), logros
con monedas, saneado del perfil del rival y persistencia tras reload.
Patrón: test_r151_portada_salon.py · sonda: probe_r156.py."""
import os, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
PUBLIC = os.path.join(ROOT, 'public')
PORT = 3008


def serve():
    import http.server
    handler = http.server.SimpleHTTPRequestHandler
    os.chdir(PUBLIC)

    class H(handler):
        def log_message(self, *a):   # silencio
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H) as httpd:
        httpd.serve_forever()


def main():
    t = threading.Thread(target=serve, daemon=True)
    t.start()

    from playwright.sync_api import sync_playwright

    fails = []
    ok = 0

    def chk(cond, msg):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(msg)

    def nav(page, pid, tab=None):
        """Re-abre el menú en una página (el bucle de animación puede
        repintar: cada grupo de interacciones parte de un estado fresco)."""
        page.evaluate('''([pid, tab]) => {
            const g = window.__game;
            g.menuOpen = true;
            g.menuPage = pid;
            if (tab) g._peTab = tab;
            g.drawMenu();
        }''', [pid, tab])
        page.wait_for_timeout(150)

    def click_id(page, rid):
        """Click REAL del menú (menuClick por índice) con un reintento."""
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
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        perr = []
        page.on('pageerror', lambda e: perr.append(str(e)))
        page.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load', timeout=30_000)
        page.wait_for_timeout(8_000)   # boot + salón

        # 1 · sin pageerrors al arrancar + ficha con defaults SIEMPRE válidos
        chk(not perr, f'pageerrors arranque: {perr[:3]}')
        pf = page.evaluate('() => (window.__game._perfil || {})')
        chk(pf.get('avatar') == 'pinguino' and pf.get('marco') == 'bronce',
            f'defaults del perfil ({pf})')

        # 2 · hub de 6 secciones (el menú REAL del hall es el VESTÍBULO)
        nav(page, 'main')
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r) => r.id)')
        for rid in ['page:jugar', 'tab:multi', 'page:champs', 'page:perfil',
                    'page:opts', 'salirweb']:
            chk(rid in ids, f'hub 6 secciones: falta {rid}')
        chk('wrl:open' not in ids, 'hub: la tarjeta RANKING ya no está (va en Mi Perfil)')
        chk('traingo' not in ids and 'survgo' not in ids,
            'hub: modos movidos dentro de JUGAR')

        # 3 · MI PERFIL se dibuja sin errores y con sus controles
        chk(click_id(page, 'page:perfil') == 'ok', 'click Mi Perfil')
        page.wait_for_timeout(200)
        chk(page.evaluate('() => window.__game.menuPage') == 'perfil', 'navegación a la ficha')
        chk(not perr, f'pageerrors ficha: {perr[:3]}')
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r) => r.id)')
        chk('page:perfil_edit' in ids, 'ficha: botón EDITAR PERL→EDITAR presente')
        chk('wrl:open' in ids, 'ficha: botón RANKING MUNDIAL presente')

        # 4 · EDITAR: pestañas y país por click REAL del dispatcher
        chk(click_id(page, 'page:perfil_edit') == 'ok', 'click EDITAR')
        page.wait_for_timeout(200)
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r) => r.id)')
        for rid in ['petab:nombre', 'petab:pais', 'petab:avatar', 'petab:marco', 'pguardar']:
            chk(rid in ids, f'editor: falta {rid}')
        chk(not perr, f'pageerrors editor: {perr[:3]}')
        nav(page, 'perfil_edit', 'pais')
        chk(click_id(page, 'ppais:FR') == 'ok', 'click bandera FR')
        pf = page.evaluate('() => window.__game._perfil')
        chk(pf.get('pais') == 'FR', f'país aplicado en vivo ({pf.get("pais")})')
        ls = page.evaluate('() => localStorage.getItem("pp_perfil_v1")')
        chk('"pais":"FR"' in (ls or ''), f'pp_perfil_v1 persiste ({ls})')

        # 5 · avatar: compra con arm de DOS toques (primero SIN monedas → falta)
        nav(page, 'perfil_edit', 'avatar')
        chk(click_id(page, 'pavatar:gato') == 'ok', 'primer toque avatar gato (arm)')
        arm = page.evaluate('() => window.__game._compraArm')
        chk(arm and arm.get('id') == 'gato', f'arm armado ({arm})')
        chk(click_id(page, 'pavatar:gato') == 'ok', 'segundo toque avatar gato (compra)')
        pf = page.evaluate('() => window.__game._perfil')
        chk(pf.get('avatar') == 'pinguino',
            f'sin monedas: la compra NO aplica ({pf.get("avatar")})')
        nav(page, 'perfil_edit', 'avatar')
        page.evaluate('''() => { const g = window.__game;
            g.stats.data.monedas = 500; g.stats.save(); }''')
        chk(click_id(page, 'pavatar:gato') == 'ok', 'toque arm (monedas suficientes)')
        chk(click_id(page, 'pavatar:gato') == 'ok', 'toque compra')
        pf = page.evaluate('() => window.__game._perfil')
        chk(pf.get('avatar') == 'gato', f'avatar comprado y equipado ({pf.get("avatar")})')
        comp = page.evaluate('() => localStorage.getItem("pp_compras") || "[]"')
        chk('avatar:gato' in comp, f'pp_compras registra la compra ({comp})')
        mon = page.evaluate('() => window.__game.stats.data.monedas')
        chk(mon == 250, f'monedas descontadas 500-250=250 ({mon})')

        # 6 · economía v2 con deltas PUROS (logros pre-desbloqueados para no
        # contaminar: cada unlock paga 50 — se mide el base por modalidad)
        e = page.evaluate('''() => {
            const s = window.__game.stats;
            for (const a of (window.__PP_ACH_KEYS || [])) s.unlock(a);
            s.data.monedas = 1000; s.save();
            const m0 = s.data.monedas, x0 = s.data.xp;
            s.recordMatch(true, 'hard', { modo: 'ia', oppElo: 1200 });
            const ia = { m: s.data.monedas - m0, x: s.data.xp - x0 };
            const m1 = s.data.monedas, x1 = s.data.xp;
            for (let i = 0; i < 11; i++) s.recordMatch(true, 'medium', { modo: 'p2p', oppElo: 1000 });
            return { ia, p2p: { m: s.data.monedas - m1, x: s.data.xp - x1 } };
        }''') if page.evaluate('() => !!window.__PP_ACH_KEYS') else page.evaluate('''() => {
            const g = window.__game, s = g.stats;
            // sin lista expuesta: desbloquea lo auto-alcanzable vía recordMatch
            s.data.ach.primera = 1; s.data.ach.gigante = 1; s.data.ach.racha3 = 1;
            s.data.monedas = 1000; s.save();
            const m0 = s.data.monedas, x0 = s.data.xp;
            s.recordMatch(true, 'hard', { modo: 'ia', oppElo: 1200 });
            const ia = { m: s.data.monedas - m0, x: s.data.xp - x0 };
            const m1 = s.data.monedas, x1 = s.data.xp;
            for (let i = 0; i < 11; i++) s.recordMatch(true, 'medium', { modo: 'p2p', oppElo: 1000 });
            return { ia, p2p: { m: s.data.monedas - m1, x: s.data.xp - x1 } };
        }''')
        chk(e['ia']['m'] == 30, f'IA hard gana 25+5 monedas ({e["ia"]["m"]})')
        chk(e['ia']['x'] == 50, f'IA hard da 40+10 XP ({e["ia"]["x"]})')
        chk(e['p2p']['m'] == 400, f'P2P: 10 duelos pagan 40, el 11º toca al tope ({e["p2p"]["m"]})')
        chk(e['p2p']['x'] == 660, f'P2P: XP SIEMPRE (60×11) aunque las monedas se topen ({e["p2p"]["x"]})')

        # 7 · un logro NUEVO paga 50 (elige uno aún no conseguido)
        e = page.evaluate('''() => {
            const g = window.__game, s = g.stats;
            const pend = ['maraton', 'superviv', 'aces10', 'm50', 'x3', 'or5', 'p1']
                .find((k) => !s.data.ach[k]);
            if (!pend) return { skip: true };
            const m0 = s.data.monedas;
            const nuevo = s.unlock(pend);
            return { nuevo, d: s.data.monedas - m0, k: pend };
        }''')
        if not e.get('skip'):
            chk(e['nuevo'] is True and e['d'] == 50,
                f'unlock({e.get("k")}) paga 50 ({e})')

        # 8 · hallProfile lleva la ficha; onPeerHall rechaza basura
        e = page.evaluate('''() => {
            const g = window.__game;
            const hp = g.hallProfile();
            g.onPeerHall({ pv: 'ZZ', av: '<hack>', mc: 'x', nv: 99999,
                w: -5, el: 1e9, a: ['primera', 'noexist'], bl: ['hack'] });
            const peer = g._hallPeer;
            return { hp, peer };
        }''')
        chk(e['hp'].get('pv') == 'FR' and e['hp'].get('av') == 'gato',
            f'hallProfile: pv/av propios ({e["hp"].get("pv")}/{e["hp"].get("av")})')
        chk(e['hp'].get('nv', 0) >= 1, 'hallProfile: nivel presente')
        chk(e['peer'].get('pv') == '' and e['peer'].get('av') == 'pinguino'
            and e['peer'].get('mc') == 'bronce', f'onPeerHall sanea basura ({e["peer"]})')
        chk(e['peer'].get('nv') == 99, f'onPeerHall: nv acotado a 99 ({e["peer"].get("nv")})')
        chk('noexist' not in (e['peer'].get('a') or []), 'onPeerHall: insignias contra catálogo')

        # 9 · JUGAR: subpágina con las 5 modalidades (clicks reales)
        nav(page, 'main')
        chk(click_id(page, 'page:jugar') == 'ok', 'click JUGAR')
        page.wait_for_timeout(200)
        chk(page.evaluate('() => window.__game.menuPage') == 'jugar', 'subpágina JUGAR activa')
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        for rid in ['start', 'carrera:abre', 'traingo', 'survgo', 'tut:go']:
            chk(rid in ids, f'JUGAR: falta modalidad {rid}')
        chk(not perr, f'pageerrors jugar: {perr[:3]}')

        # 10 · Ajustes › Perfil SIN el editor de nombre (va en MI PERFIL)
        nav(page, 'opts')
        chk(click_id(page, 'page:optsPerfil') == 'ok', 'click categoría Perfil')
        page.wait_for_timeout(200)
        ids = page.evaluate('() => (window.__game.menuRects || []).map((r2) => r2.id)')
        chk('pname' not in ids, 'Ajustes › Perfil sin editor de nombre')

        # 11 · PERSISTENCIA tras reload: país/avatar/xp sobreviven
        xp_before = page.evaluate('() => window.__game.stats.data.xp')
        page.reload(wait_until='load')
        page.wait_for_timeout(8_000)
        e = page.evaluate('''() => {
            const g = window.__game;
            return { pf: g._perfil, xp: g.stats.data.xp };
        }''')
        chk(e['pf'].get('pais') == 'FR', f'reload: país persiste ({e["pf"].get("pais")})')
        chk(e['pf'].get('avatar') == 'gato', f'reload: avatar persiste ({e["pf"].get("avatar")})')
        chk(e['xp'] == xp_before, f'reload: XP persiste ({e["xp"]})')
        chk(not perr, f'pageerrors tras reload: {perr[:3]}')

        browser.close()

    print(f'\nARNÉS r156 MI PERFIL: {ok}/{ok + len(fails)} OK')
    for f in fails:
        print('  ✗ ' + f)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
