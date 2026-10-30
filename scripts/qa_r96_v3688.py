#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r96_v3688.py — capa de QA de la ronda 96 (V3.6.88-SDK6).

Los seis frentes del dueño de esta ronda:
 1) SALA Y ESCENA EN VIVO: al entrar en Ajustes › Sala y Escena el entorno
    deja el HALL y muestra la SALA DE PARTIDOS (sala + mesa + marcador,
    rig retrasado 1,15 m); al salir o cerrar el menú todo vuelve EXACTO.
 2) SALA y MESA como SUBMENÚS-BOTÓN (tarjetas con color e icono, estética
    del menú): cada uno abre SU página.
 3) ALTURA POR DESLIZADOR: raíl continuo 0,70–0,84 m (paso fino ±1 cm),
    fija la altura AL PUNTO apuntado, feedback EN VIVO (DIMS muta,
    relayoutMesa reacomoda, persiste pp_mesaaltoy).
 4) TOOLTIPS del menú (norma general): caja con 1-2 líneas al apuntar un
    control, i18n del idioma escogido; sin hover no pinta nada.
 5) SONIDOS SIN SOLAPES: etiqueta en SU fila + controles en la suya; las
    barras de volumen son CLICABLES (mvolset/fvolset al punto).
 6) PIELES DE MESA SÓLO PARTIDAS/ENTRENAMIENTO: en campeonato activo el
    tinte cae al azul nativo; champs.launch() restaura el nativo y
    leaveAll() reaplica el aspecto del dueño.
 7) AUDITORÍA DE FLUIDEZ: NITIDEZ (FFR) con 4 niveles que CAPAN la fovea
    del gobernador (techo honesto 0,65 — antes 0,8) y Quest 3 nace a 0,35.
"""
import functools, json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
CORE = os.path.join(RAIZ, 'src/game/core')
PORT = 8816
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (fuente + servido) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8', errors='ignore').read()
C00 = open(os.path.join(CORE, 'c00_pre_three.js'), encoding='utf-8').read()
C11 = open(os.path.join(CORE, 'c11_champloader.js'), encoding='utf-8').read()

AGUJAS = [
    # (1) vista en vivo
    ('_salaPreviewUpdate() {', 'c12: vista de sala — conmutador Hall↔cancha'),
    ('this.rig.position.set(0, 0, 1.15);', 'c12: rig retrasado 1,15 m para ver la mesa'),
    ('this.rig.position.set(0, 0, HALL.cz + 2.3);', 'c12: la vista devuelve al Hall EXACTO'),
    ('this._salaPreviewUpdate();\n    // flotación inicial', 'c12: la vista se vigila cada frame en updateMenu'),
    ('this._salaPreviewUpdate();\n    }', 'c12: cerrar el menú recoge la vista de sala'),
    ('this._salaPreview = false;   // r96: la vista de sala no sobrevive a la cancha', 'c12: exitHall limpia el flag'),
    ('sala_preview: \'Sala de partidos · los cambios se aplican en vivo\'', 'i18n ES: aviso de vista en vivo'),
    # (2) submenús-botón
    ("'page:optsSalaRoom'", 'c12: submenú SALA (tarjeta)'),
    ("'page:optsSalaMesa'", 'c12: submenú MESA (tarjeta)'),
    ("PP_ICONS.mesa)", 'c12: la tarjeta MESA usa el icono nuevo'),
    ('mesa(c, x, y) {', 'c00: icono MESA (tablero, red y patas)'),
    ("cat_salaroom: 'SALA'", 'i18n ES: título del submenú SALA'),
    ("cat_salamesa: 'MESA'", 'i18n ES: título del submenú MESA'),
    ("cat_salaroom: 'ROOM'", 'i18n EN: título del submenú SALA'),
    ("cat_salamesa: 'TABLE'", 'i18n EN: título del submenú MESA'),
    ("arg === 'optsSalaRoom' || arg === 'optsSalaMesa'", 'c12: navegación de los dos submenús'),
    # (3) deslizador
    ('const MESA_ALTO_MIN = 0.70;', 'c02: rango BAJO del deslizador'),
    ('const MESA_ALTO_MAX = 0.84;', 'c02: rango ALTO del deslizador'),
    ('_mesaAplicarY(yNum, opts) {', 'c12: altura CONTINUA (muta DIMS + relayout)'),
    ("id: 'mesa_altoy', slider: true", 'c12: raíl del deslizador interactivo'),
    ("localStorage.setItem('pp_mesaaltoy'", 'c12: altura fina persistente'),
    ("case 'mesa_altomen':   // r96 · paso fino ±1 cm", 'c12: botones − / + de 1 cm'),
    ('_menuSliderFrac(r, hit) {', 'c12: fracción del raíl por el punto apuntado'),
    ('this._menuHitPx[h] = { x: px, y: py };', 'c12: punto EXACTO del panel por mano'),
    ('this.menuClick(hov, i);   // r96: mano que pulsa', 'c12: el gatillo pasa la mano (deslizadores)'),
    ("mesa_zona_baja: 'Baja'", 'i18n ES: extremos del raíl'),
    ("mesa_zona_alta: 'Alta'", 'i18n ES: extremo alto del raíl'),
    # (4) tooltips
    ('_menuTipDraw(c, rects) {', 'c12: pintor del tooltip'),
    ('_menuTipKey(id) {', 'c12: resolución id → hint'),
    ("hint_mesa_altoy: 'Arrastra o apunta al raíl", 'i18n ES: tooltip del deslizador'),
    ("hint_mesa_altoy: 'Point along the rail", 'i18n EN: tooltip del deslizador'),
    ("hint_cat_sala: 'Sala y mesa: se abre la sala de partidos", 'i18n ES: tooltip de la categoría'),
    ("hint_perfFfr: 'Nitidez del visor", 'i18n ES: tooltip de la nitidez'),
    # (5) sonidos limpios
    ("id: idSet, slider: true", 'c12: barras de volumen CLICABLES'),
    ("case 'mvolset':   // r96 · barra CLICABLE", 'c12: handler de la barra de música'),
    ("etiqueta en SU fila", 'c12: etiqueta de volumen en su propia fila (sin solape)'),
    # (6) pieles fuera de campeonatos
    ('_mesaTinte(skin) {', 'c12: tinte central con regla de campeonato'),
    ('_mesaNativo() {', 'c12: azul nativo al entrar en campeonato'),
    ('_mesaSkinReapply() {', 'c12: aspecto del dueño al salir'),
    ('try { if (g._mesaNativo) g._mesaNativo(); } catch (eMN) { /* */ }', 'c11: el campeonato ARRANCA nativo'),
    ('try { if (this.game._mesaSkinReapply) this.game._mesaSkinReapply(); } catch (eMR) { /* */ }', 'c11: leaveAll reaplica la piel del dueño'),
    ('const nativo = this.mesaOcupada();', 'c12: la regla lee el campeonato activo'),
    # (7) fluidez / FFR
    ('const PERF_FFR_MODOS = {', 'c12: NITIDEZ (FFR) en 4 niveles'),
    ('setFfr(mode) {', 'c12: ajuste EN VIVO del tope de fovea'),
    ('foveaMax() {', 'c12: techo del gobernador (FFR o 0,65 honesto)'),
    ('return 0.65;', 'c12: techo 0,65 — adiós a la fovea 0,8 (deformación)'),
    ('quest3: { label: \'Quest 3\', scale: 1.40, fovea: 0.35, rate: 90 }', 'c12: Quest 3 nace MÁS NÍTIDO (0,35)'),
    ("case 'perfFfr': {", 'c12: handler NITIDEZ del menú'),
    ('ffr: this.ffr,   // r96 · tope de nitidez del dueño', 'c12: estado FFR expuesto a AJUSTES/QA'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

# versión sellada
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.88-SDK6', 'c00: VERSION sella 3.6.88-SDK6')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 90, 'VERSION.json: FASE 90')
CHK(V.get('hub') == 'v3688-sdk6', 'VERSION.json: hub v3688-sdk6')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(2500)

    # ---- 1 · DESLIZADOR: altura continua, DIMS en vivo, persistencia, clamp
    slide = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const topY = () => g.tableGroup.getObjectByName('ppTableTop').position.y;
      const netY = () => g.tableGroup.getObjectByName('ppTableNet').position.y;
      const out = { base: topY() };
      const y1 = g._mesaAplicarY(0.82);
      out.y1 = y1; out.top1 = topY(); out.net1 = netY();
      out.ls1 = localStorage.getItem('pp_mesaaltoy');
      out.preset1 = g.mesaAlto;   // preset más cercano
      // clamp por abajo y por arriba
      out.clampLo = g._mesaAplicarY(0.5);
      out.clampHi = g._mesaAplicarY(1.2);
      // paso fino
      g._mesaAplicarY(0.76);
      out.mas = g._mesaAplicarY(g.mesaAltoY + 0.01);
      out.menos = g._mesaAplicarY(g.mesaAltoY - 0.02);
      // leg patas honestas
      g._mesaAplicarY(0.84);
      out.leg84 = g.tableGroup.getObjectByName('ppTableLeg').scale.y;
      g._mesaAplicarY(0.76);
      out.base2 = topY();
      return out;
    }""")
    if 'err' in (slide or {}):
        CHK(False, 'deslizador: %s' % slide.get('err'))
    else:
        CHK(abs(slide['y1'] - 0.82) < 1e-9 and abs(slide['top1'] - 0.795) < 1e-6,
            'deslizador: 82 cm → tablero a 0,795 (DIMS muta en vivo)')
        CHK(abs(slide['net1'] - (0.82 + 0.1525 / 2)) < 1e-6,
            'deslizador: la red sube con la mesa (15,25 cm reglamentarios)')
        CHK(slide['ls1'] == '0.82' and slide['preset1'] == 'alta',
            'deslizador: pp_mesaaltoy persiste y el preset cercano sigue')
        CHK(abs(slide['clampLo'] - 0.70) < 1e-9 and abs(slide['clampHi'] - 0.84) < 1e-9,
            'deslizador: clamp honesto al rango 70-84 cm')
        CHK(abs(slide['mas'] - 0.77) < 1e-9 and abs(slide['menos'] - 0.75) < 1e-9,
            'deslizador: paso fino ±1 cm exacto')
        CHK(abs(slide['leg84'] - (0.84 - 0.05) / (0.76 - 0.05)) < 1e-3,
            'deslizador: patas re-escaladas honestas a 84 cm')
        CHK(abs(slide['base2'] - 0.735) < 1e-6, 'deslizador: vuelta a 76 cm limpia')

    # ---- 2 · PIELES SÓLO PARTIDAS/ENTRENAMIENTO (regla del dueño)
    piel = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const topC = () => g.tableGroup.getObjectByName('ppTableTop').material.color.getHexString();
      const edgeC = () => g.tableGroup.getObjectByName('ppTableApron').material.color.getHexString();
      const out = {};
      // libre: la piel del dueño se aplica
      g._mesaTinte({ top: 0x1c6b47, edge: 0x125033, id: 'verde' });
      out.libre = topC(); out.skinLibre = g.mesaSkin;
      // campeonato SIMULADO: el tinte cae al AZUL NATIVO aunque pida verde
      const realOcup = g.mesaOcupada;
      g.mesaOcupada = () => true;   // sombra del método de instancia
      g._mesaTinte({ top: 0x1c6b47, edge: 0x125033, id: 'verde' });
      out.champ = topC(); out.edgeChamp = edgeC(); out.skinChamp = g.mesaSkin;
      g._mesaNativo();
      out.nativo = topC();
      g.mesaOcupada = realOcup;
      // salida del campeonato: reaplica el aspecto GUARDADO del dueño
      localStorage.setItem('pp_mesaskin', 'verde');
      g._mesaSkinReapply();
      out.reap = topC(); out.skinReap = g.mesaSkin;
      // limpieza
      localStorage.setItem('pp_mesaskin', 'azul');
      g._mesaSkinReapply();
      out.fin = topC();
      return out;
    }""")
    if 'err' in (piel or {}):
        CHK(False, 'pieles: %s' % piel.get('err'))
    else:
        CHK(piel['libre'] == '1c6b47' and piel['skinLibre'] == 'verde',
            'pieles: sin campeonato, la piel del dueño SE APLICA (verde)')
        CHK(piel['champ'] == '17539e' and piel['edgeChamp'] == '0e3a73',
            'pieles: CON campeonato activo el tinte cae al AZUL NATIVO (La Locura ya no se tiñe)')
        CHK(piel['skinChamp'] == 'azul' and piel['nativo'] == '17539e',
            'pieles: _mesaNativo fija el azul oficial y el id')
        CHK(piel['reap'] == '1c6b47' and piel['skinReap'] == 'verde',
            'pieles: leaveAll→reapply devuelve la piel ELEGIDA (partidas/entrenamiento)')
        CHK(piel['fin'] == '17539e', 'pieles: limpieza final azul')

    # ---- 3 · VISTA DE SALA (Hall → sala de partidos y vuelta EXACTA)
    vista = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const out = {};
      // simulación de HALL (el headless sin VR nace en cancha)
      g.inHall = true;
      g._hallHidden = [g.tableGroup, g.aiPaddleMesh, g.demoPaddleMesh, g.scoreboardGroup]
        .filter(Boolean);
      for (const o of g._hallHidden) o.visible = false;
      if (g.hallGroup) g.hallGroup.visible = true;
      if (g.roomGroup) g.roomGroup.visible = false;
      g.hallZ = g.rig.position.z;
      // ENTRAR en la categoría SALA Y ESCENA
      g.menuOpen = true; g.menuPage = 'optsSala';
      g._salaPreviewUpdate();
      out.on = !!g._salaPreview;
      out.rigOn = +g.rig.position.z.toFixed(3);
      out.tableVis = g.tableGroup.visible;
      out.scoreVis = g.scoreboardGroup ? g.scoreboardGroup.visible : null;
      out.hallVis = g.hallGroup ? g.hallGroup.visible : null;
      out.roomVis = g.roomGroup ? g.roomGroup.visible : null;
      // página MESA: la vista SIGUE
      g.menuPage = 'optsSalaMesa';
      g._salaPreviewUpdate();
      out.sigue = !!g._salaPreview;
      // SALIR a otra categoría
      g.menuPage = 'optsJuego';
      g._salaPreviewUpdate();
      out.off = !!g._salaPreview;
      out.rigOff = +g.rig.position.z.toFixed(3);
      out.tableOff = g.tableGroup.visible;
      out.hallOff = g.hallGroup ? g.hallGroup.visible : null;
      // limpieza: estado de hall honesto
      g.menuOpen = false;
      g.inHall = false;
      g._hallHidden = null;
      for (const o of [g.tableGroup, g.scoreboardGroup]) if (o) o.visible = true;
      if (g.hallGroup) g.hallGroup.visible = false;
      if (g.roomGroup) g.roomGroup.visible = true;
      g.rig.position.set(0, 0, 0);
      return out;
    }""")
    if 'err' in (vista or {}):
        CHK(False, 'vista sala: %s' % vista.get('err'))
    else:
        CHK(vista.get('on') is True and abs(vista.get('rigOn', 0) - 1.15) < 1e-6,
            'vista sala: entrar en SALA Y ESCENA teletransporta a la cancha (rig +1,15)')
        CHK(vista.get('tableVis') is True and vista.get('scoreVis') is True,
            'vista sala: mesa y marcador VISIBLES (la sala de partidos a la vista)')
        CHK(vista.get('hallVis') is False and vista.get('roomVis') is True,
            'vista sala: el museo se oculta y la sala virtual se enciende')
        CHK(vista.get('sigue') is True,
            'vista sala: las subpáginas SALA/MESA mantienen la vista')
        CHK(vista.get('off') is False and abs(vista.get('rigOff', 0) + 16.2) < 0.01,  # HALL.cz -18,5 + 2,3
            'vista sala: al salir de la categoría, de vuelta al Hall EXACTO')
        CHK(vista.get('tableOff') is False and vista.get('hallOff') is True,
            'vista sala: mesa oculta y museo visible tras la vuelta')

    # ---- 4 · MENÚ: submenús, raíl y barras obedecen AL PUNTO apuntado
    menu = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const ids = (p) => { g.menuPage = p; g.drawMenu(); return g.menuRects.map(r => r.id); };
      const out = {};
      out.sala = ids('optsSala');
      out.salaRoom = ids('optsSalaRoom');
      out.salaMesa = ids('optsSalaMesa');
      out.sonido = ids('optsSonido');
      // clic en el CENTRO del raíl → ~77 cm
      g.menuPage = 'optsSalaMesa'; g.drawMenu();
      const r = g.menuRects.find(x => x.id === 'mesa_altoy');
      g._menuHitPx = [{ x: r.x + r.w * 0.5, y: r.y + 10 }, null];
      const i0 = g.menuRects.indexOf(r);
      g.menuClick(i0, 0);
      out.centro = Math.round(g.mesaAltoY * 1000) / 1000;
      // clic al 0% → 70 cm; al 100% → 84 cm
      g._menuHitPx = [{ x: r.x + r.w * 0.99, y: r.y + 10 }, null];
      g.menuClick(i0, 0);
      out.fin = Math.round(g.mesaAltoY * 1000) / 1000;
      g._menuHitPx = [{ x: r.x + 2, y: r.y + 10 }, null];
      g.menuClick(i0, 0);
      out.ini = Math.round(g.mesaAltoY * 1000) / 1000;
      // ±1 cm (desde el mínimo: + primero para no clampar)
      const im = g.menuRects.findIndex(x => x.id === 'mesa_altomen');
      const imas = g.menuRects.findIndex(x => x.id === 'mesa_altomas');
      g.menuClick(imas, 0);
      out.mas1 = Math.round(g.mesaAltoY * 1000) / 1000;
      g.menuClick(im, 0);
      out.menos = Math.round(g.mesaAltoY * 1000) / 1000;
      g.menuClick(imas, 0); g.menuClick(imas, 0);
      out.mas = Math.round(g.mesaAltoY * 1000) / 1000;
      // barra de volumen clicable al 30%
      g.menuPage = 'optsSonido'; g.drawMenu();
      const rv = g.menuRects.find(x => x.id === 'mvolset');
      g._menuHitPx = [{ x: rv.x + rv.w * 0.3, y: rv.y + 10 }, null];
      const iv = g.menuRects.indexOf(rv);
      g.menuClick(iv, 0);
      out.vol = g.audio.musicVol;
      g.audio.setMusicVol(1);
      // páginas sin errores
      for (const p of ['opts', 'optsJuego', 'optsSala', 'optsSalaRoom', 'optsSalaMesa',
                       'optsSonido', 'optsVisual', 'optsPerfil', 'optsRendi', 'optsPala',
                       'main', 'champs', 'rank', 'multi']) {
        g.menuPage = p; g.drawMenu();
      }
      g.menuPage = 'main'; g.drawMenu(); g.menuOpen = false;
      return out;
    }""")
    if 'err' in (menu or {}):
        CHK(False, 'menú: %s' % menu.get('err'))
    else:
        CHK('page:optsSalaRoom' in menu['sala'] and 'page:optsSalaMesa' in menu['sala'],
            'menú SALA Y ESCENA: las DOS tarjetas de submenú (botones con color e icono)')
        CHK('theme:neon' in menu['salaRoom'] and 'psthru' in menu['salaRoom'],
            'submenú SALA: los cuatro temas + passthrough')
        CHK('mesa_altoy' in menu['salaMesa'] and 'mesa_altomen' in menu['salaMesa'],
            'submenú MESA: raíl + paso fino')
        CHK(menu['sonido'].count('mvolset') == 1 and menu['sonido'].count('fvolset') == 1,
            'sonidos: las dos barras CLICABLES')
        CHK(abs(menu['centro'] - 0.77) < 0.014,
            'raíl: clic al centro ≈ 77 cm (%s)' % menu['centro'])
        CHK(abs(menu['fin'] - 0.84) < 0.014 and abs(menu['ini'] - 0.70) < 0.014,
            'raíl: extremos honestos (70/84 cm al punto apuntado)')
        CHK(abs(menu['mas1'] - (menu['ini'] + 0.01)) < 1e-9,
            'raíl: + sube 1 cm')
        CHK(abs(menu['menos'] - menu['ini']) < 1e-9,
            'raíl: − baja 1 cm (de vuelta al mínimo)')
        CHK(abs(menu['mas'] - (menu['ini'] + 0.02)) < 1e-9,
            'raíl: + sube 1 cm dos veces')
        CHK(abs(menu['vol'] - 0.3) < 0.011,
            'volumen: clic al 30%% de la barra fija 30%% (%s)' % menu['vol'])

    # ---- 5 · TOOLTIP: se pinta al apuntar y NO pinta sin hover
    tip = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const c = g.menuCanvas.getContext('2d');
      const MUESTRA = (x, y) => Array.from(c.getImageData(x, y, 1, 1).data);
      g.menuOpen = true; g.menuPage = 'optsSalaMesa';
      g.menuHover = [-1, -1];
      g.drawMenu();
      const r = g.menuRects.find(x => x.id === 'mesa_skin:verde');
      const ir = g.menuRects.indexOf(r);
      const pSin = MUESTRA(512, Math.max(4, r.y - 46));
      g.menuHover = [ir, -1];
      g.drawMenu();
      const pCon = MUESTRA(512, Math.max(4, r.y - 46));
      g.menuHover = [-1, -1];
      g.menuPage = 'main'; g.drawMenu(); g.menuOpen = false;
      return { sin: pSin, con: pCon };
    }""")
    if 'err' in (tip or {}):
        CHK(False, 'tooltip: %s' % tip.get('err'))
    else:
        CHK(tip['sin'] != tip['con'],
            'tooltip: apuntar el control pinta el hint (tinta nueva sobre el panel)')
        CHK(tip['con'][3] > 200,
            'tooltip: la caja es OPACA (legible sobre cualquier fondo)')

    # ---- 6 · FFR / NITIDEZ: tope del dueño + techo del gobernador
    ffr = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const p = g.perf; if (!p) return { err: 'sin perf' };
      const out = {};
      p.setFfr('max');
      out.max = p.fovea; out.capMax = p.foveaMax();
      p.setFfr('rinde');
      out.capRinde = p.foveaMax();
      p.fovea = 0.9;                 // el gobernador dispara: el techo manda
      p.setFfr('normal');
      out.normal = p.fovea;
      p.setFfr('def');
      out.capDef = p.foveaMax();
      out.ls = JSON.parse(localStorage.getItem('ppxr_perf_v1') || '{}').ffr;
      out.label = p.ffrLabel();
      // gobernador no pasa del techo
      p.fovea = 0.35; p._coolDown = 0;
      p._hist = [{ avg: 40, min: 30 }, { avg: 40, min: 30 }, { avg: 40, min: 30 }, { avg: 40, min: 30 }];
      p._stepDown();
      out.step = p.fovea;
      p.setFfr('def'); p.fovea = 0.35;
      return out;
    }""")
    if 'err' in (ffr or {}):
        CHK(False, 'ffr: %s' % ffr.get('err'))
    else:
        CHK(ffr.get('capMax') == 0, 'ffr: Máxima nitidez = fovea 0')
        CHK(abs(ffr.get('capRinde', -1) - 0.75) < 1e-9, 'ffr: nivel Rinde = 0,75')
        CHK(abs(ffr.get('normal', -1) - 0.5) < 1e-9, 'ffr: Normal aplica 0,5 EN VIVO (aunque viniera de 0,9)')
        CHK(abs(ffr.get('capDef', -1) - 0.65) < 1e-9, 'ffr: sin tope del dueño, techo honesto 0,65 (antes 0,8)')
        CHK(ffr.get('ls') == 'def', 'ffr: la elección persiste (ppxr_perf_v1)')
        CHK('Auto' in ffr.get('label', '') or 'AUTO' in ffr.get('label', ''),
            'ffr: etiqueta del modo por defecto legible')
        CHK(abs(ffr.get('step', -1) - 0.43) < 1e-9,
            'ffr: el gobernador con FPS bajos respeta el techo 0,65 (step→%s)' % ffr.get('step'))

    CHK(not errs, 'consola: 0 pageerrors (%s)' % (errs[:2] or 'limpio'))
    b.close()

srv.shutdown()
print('\n== RESUMEN r96 ==')
print('OK: %d · FALLOS: %d' % (len(OK), len(FAIL)))
for f in FAIL:
    print('  ✗ ' + f)
raise SystemExit(1 if FAIL else 0)
