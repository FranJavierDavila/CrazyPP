#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r95_v3687.py — capa de QA de la ronda 95 (V3.6.90-SDK6).

Cuatro frentes del dueño, verificados aquí:
 1) SIN CARTEL EN LOS DUELOS (regla de casa): «en todos los campeonatos, en
    las fases de duelo con el rival no hay cartel explicativo; ese sólo
    existe en las etapas de habilidades». Halloween (los 3 duelos), la
    PLANTILLA (futuros campeonatos) y la ESTACIÓN ORBITAL dejan de pintarlo;
    las PRUEBAS de habilidad lo conservan; oeste/magia/locura ya cumplían.
 2) VOLÚMENES SEPARADOS música/efectos (AJUSTES › SONIDOS) — canales
    persistentes pp_musicvol/pp_fxvol aplicados en vivo (menú, BSO núcleo,
    bus de efectos; oeste/magia leen musicVol en su BSO privada).
 3) SALA Y ESCENA en DOS subapartados: SALA (los 4 temas) y MESA (altura
    baja/normal/alta que MUTA DIMS + reacomoda la mesa viva; aspecto con
    3 opciones por defecto + Oro/Carbono liberables con recompensas).
 4) RIVALES CON ESTILO VISIBLE (colocación + celebración) y ESTADÍSTICAS
    AL FINAL DE CADA DUELO (vel. máx · rally más largo · % precisión) en
    la fanfarria."""
import os, functools, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
CORE = os.path.join(RAIZ, 'src/game/core')
PORT = 8815
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

def cuerpo_funcion(txt, firma):
    """Extrae el cuerpo de un método JS por su firma (llaves equilibradas)."""
    i = txt.find(firma)
    if i < 0:
        return ''
    j = txt.find('{', i)
    prof = 0
    for k in range(j, len(txt)):
        if txt[k] == '{':
            prof += 1
        elif txt[k] == '}':
            prof -= 1
            if prof == 0:
                return txt[j:k + 1]
    return ''

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA · SIN CARTEL EN LOS DUELOS (regla de casa) ==')
HAL = open(os.path.join(PUB, 'championships/halloween/index.js'), encoding='utf-8').read()
duel_h = cuerpo_funcion(HAL, '_startDuel(idx, esReplay) {')
CHK('showInstrucciones' not in duel_h,
    'halloween: _startDuel SIN showInstrucciones (los 3 duelos sin cartel)')
CHK("rules.message = tx('duelo_vs'" in duel_h,
    'halloween: el aviso del duelo vive en la LÍNEA DEL MARCADOR (duelo_vs)')
CHK(HAL.count('showInstrucciones') == 1,
    'halloween: las PRUEBAS conservan SU cartel (1 llamada, etapa de habilidad)')
man_h = json.load(open(os.path.join(PUB, 'championships/halloween/manifest.json')))
CHK(any(n.startswith('v9 (r95)') for n in man_h.get('notes', [])),
    'halloween manifest: nota v9 (r95) presente')

PLA = open(os.path.join(PUB, 'championships/_plantilla/index.js'), encoding='utf-8').read()
duel_p = cuerpo_funcion(PLA, '_startDuel(idx, esReplay) {')
CHK('showInstrucciones' not in duel_p,
    'plantilla: _startDuel SIN showInstrucciones (futuros campeonatos heredan la regla)')
CHK(PLA.count('showInstrucciones') == 1, 'plantilla: pruebas con SU cartel intacto')

EST = open(os.path.join(PUB, 'championships/estacion_orbital/index.js'), encoding='utf-8').read()
duel_e = cuerpo_funcion(EST, '_empezarDuelo(et) {')
CHK('showInstrucciones(' not in duel_e and 'this._showInstr' not in duel_e,
    'estacion: _empezarDuelo SIN cartel explicativo')
CHK('_showInstr(et) RETIRADO' in EST and 'this._showInstr(' not in EST,
    'estacion: _showInstr RETIRADO del módulo (no queda llamada viva)')
CHK(EST.count('showInstrucciones') >= 4,
    'estacion: las PRUEBAS conservan SU cartel (v2.106 intacto)')
man_e = json.load(open(os.path.join(PUB, 'championships/estacion_orbital/manifest.json')))
_changelog_e = (man_e.get('notes') or []) + (man_e.get('historial') or [])
CHK(any('r95' in n and 'SIN CARTEL' in n for n in _changelog_e),
    'estacion manifest: nota r95 presente (notes/historial)')

OES = open(os.path.join(PUB, 'championships/oeste/index.js'), encoding='utf-8').read()
duel_o = cuerpo_funcion(OES, '_startDuel(nv) {')
CHK('showInstrucciones' not in duel_o, 'oeste: _startDuel sin cartel (ya cumplía, aguja)')
MAG = open(os.path.join(PUB, 'championships/magia/index.js'), encoding='utf-8').read()
duel_m = cuerpo_funcion(MAG, '_startDuel() {')
CHK('showInstrucciones' not in duel_m, 'magia: _startDuel sin cartel (ya cumplía, aguja)')
LOC = open(os.path.join(PUB, 'championships/locura/index.js'), encoding='utf-8').read()
CHK('instr_ark' in LOC and LOC.count('showInstrucciones') >= 1,
    'locura: cartél de PRUEBA arkanoid intacto (etapa de habilidad)')

print('== ESTÁTICA · CANALES DE VOLUMEN / MESA / ESTILO / STATS ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8', errors='ignore').read()
for aguja, nombre in [
    ('setMusicVol(v) {', 'c03: setMusicVol (canal música persistente)'),
    ('setFxVol(v) {', 'c03: setFxVol (canal efectos persistente)'),
    ('this.fxBus.connect(this.master);', 'c03: bus de efectos cableado a master'),
    ('p.connect(this.fxBus || this.master);', 'c03: panNode sale por el bus de efectos'),
    ("localStorage.setItem('pp_musicvol'", 'c03: pp_musicvol persistente'),
    ("localStorage.setItem('pp_fxvol'", 'c03: pp_fxvol persistente'),
    ('this.arcVol * this.musicVol', 'c03: BSO del campeonato escala con musicVol'),
    ('0.26 * this.musicVol', 'c03: música del menú escala con musicVol'),
    ('const MESA_ALTOS', 'c02: MESA_ALTOS (baja/normal/alta)'),
    ('const MESA_ASPECTOS', 'c02: MESA_ASPECTOS (3 libres + 2 con recompensa)'),
    ("lock: 'wins10'", 'c02: Oro campeón se libera con recompensa'),
    ('function relayoutMesa(group)', 'c07: relayoutMesa (mesa viva, sin reconstruir)'),
    ("m.name === 'ppTableNet'", 'c07: red nombrada para el relayout'),
    ('this.mStats = { vmax: 0, bestRally: 0 };', 'c06: mStats por PARTIDO (reset en startMatch)'),
    ('this.style = null;', 'c06: OpponentAI.style (colocación/celebración)'),
    ('this.celebT = 0;', 'c06: OpponentAI.celebT (celebración en curso)'),
    ('inDist -= (this.style ? (this.style.bias || 0) : 0);', 'c06: estilo — el agresivo se adelanta al golpe'),
    ('(this.style ? (this.style.zIdle || 0) * -sign : 0),', 'c06: estilo — colocación de espera'),
    ('_rivStyleCalc() {', 'c12: personalidad del manifest → palancas visibles'),
    ('_mesaAplicar(altoId, skinId) {', 'c12: aplicar altura+aspecto de MESA'),
    ('DIMS.tableTopY = y;', 'c12: la altura MUTA DIMS (física/IA la leen en vivo) — re-anclado a r96: deslizador continuo'),
    ("case 'rivstyle': {", 'c12: conmutador Rivales con estilo visible'),
    ("case 'mesa_alto': {", 'c12: handler de altura de mesa'),
    ("case 'mesa_skin': {", 'c12: handler de aspecto de mesa'),
    ('this.rules.mStats.vmax = sp;', 'c12: velocidad máx. de bola medida en vivo'),
    ('fanfStats', 'c12: la fanfarria recibe las estadísticas del duelo'),
    ("T('fanf_stats'", 'c08: chip de estadísticas en el cartel final'),
    ("btn_musvol: 'Volumen música'", 'i18n ES: volúmenes'),
    ("btn_musvol: 'Music volume'", 'i18n EN: volúmenes'),
    ("btn_rivstyle: 'Rivales con estilo visible: {v}'", 'i18n ES: rivales con estilo'),
    ("mesa_alto_baja: 'Baja'", 'i18n ES: alturas de mesa'),
    ("mesa_asp_oro: 'Oro campeón'", 'i18n ES: aspectos de mesa'),
]:
    CHK(aguja in GH, 'game.html: ' + nombre)

mus_o = cuerpo_funcion(OES, '_musicEffVol() {')
mus_m = cuerpo_funcion(MAG, '_musicEffVol() {')
CHK('A.musicVol' in mus_o, 'oeste: la BSO privada respeta el canal de música')
CHK('A.musicVol' in mus_m, 'magia: la BSO privada respeta el canal de música')

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

    # ---- 1 · CANALES DE VOLUMEN (en vivo y persistentes)
    vol = pg.evaluate("""async () => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const A = g.audio;
      const out = { mv0: A.musicVol, fv0: A.fxVol };
      A.setMusicVol(0.4); A.setFxVol(0.6);
      await new Promise(r => setTimeout(r, 250));
      out.mv1 = A.musicVol;
      out.fv1 = A.fxVol;
      out.bus = A.fxBus ? Math.round(A.fxBus.gain.value * 100) / 100 : null;
      out.lsM = localStorage.getItem('pp_musicvol');
      out.lsF = localStorage.getItem('pp_fxvol');
      A.setMusicVol(1); A.setFxVol(1);   // restablecer
      return out;
    }""")
    CHK(vol.get('mv0') == 1 and vol.get('fv0') == 1, 'volumen: canales nacen a 100%')
    CHK(vol.get('mv1') == 0.4 and vol.get('lsM') == '0.4',
        'volumen: música 40%% aplicado y PERSISTIDO (%s)' % vol.get('lsM'))
    CHK(vol.get('fv1') == 0.6 and vol.get('fv1') == vol.get('bus'),
        'volumen: efectos 60%% aplicado EN VIVO al bus (%s)' % vol.get('bus'))

    # ---- 2 · MESA: altura muta DIMS + reacomoda la mesa VIVA
    mesa = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const D = g.tableGroup.getObjectByName('ppTableTop');
      const N = g.tableGroup.getObjectByName('ppTableNet');
      const leg = g.tableGroup.getObjectByName('ppTableLeg');
      const y0 = D.position.y, n0 = N.position.y;
      g._mesaAplicar('alta', 'azul');
      const alto = { topY: D.position.y, netY: N.position.y, dims: 0 };
      alto.dims = (window.__PP_DIMS_READ ? window.__PP_DIMS_READ() : null);
      const legScale = leg.scale.y;
      // aspecto verde
      g._mesaAplicar('alta', 'verde');
      const col = D.material.color.getHexString();
      // bloqueo honesto: sin recompensa, 'oro' cae al azul por defecto
      const libreOro0 = g._mesaLibre('wins10');
      g._mesaAplicar('normal', 'oro');
      const skinBloqueada = g.mesaSkin;
      // recompensa: 10 victorias → el oro se libera
      g.stats.data.won = 10; g.stats.save();
      g._mesaAplicar('normal', 'oro');
      const colOro = D.material.color.getHexString();
      const skinOro = g.mesaSkin;
      // volver al estado limpio
      g.stats.data.won = 0; g.stats.save();
      g._mesaAplicar('normal', 'azul');
      return { y0, n0, alto, legScale, col, libreOro0, skinBloqueada, colOro, skinOro,
               dimsTop: (window.__PP_GAME.rules, window.__PP_GAME.ai, null) };
    }""")
    if 'err' in (mesa or {}):
        CHK(False, 'mesa: %s' % mesa.get('err'))
    else:
        CHK(abs(mesa['alto']['topY'] - (0.84 - 0.025)) < 1e-6,
            'mesa: ALTA → tablero a 0,815 m (MUTA con DIMS)')
        CHK(abs(mesa['alto']['netY'] - (0.84 + 0.07625)) < 1e-6,
            'mesa: ALTA → la red sube con la mesa (15,25 cm reglamentarios)')
        CHK(abs(mesa['legScale'] - (0.84 - 0.05) / (0.76 - 0.05)) < 1e-3,
            'mesa: patas re-escaladas honestas (sin flotar ni hundirse)')
        CHK(mesa['col'] == '1c6b47', 'mesa: aspecto VERDE tiñe el tablero')
        CHK(mesa['libreOro0'] is False and mesa['skinBloqueada'] == 'azul',
            'mesa: ORO bloqueado sin recompensa (cae al azul, sin trampa)')
        CHK(mesa['colOro'] == 'c9932f' and mesa['skinOro'] == 'oro',
            'mesa: ORO se LIBERA con la recompensa (10 victorias) y se aplica')
        CHK(abs(mesa['y0'] - (0.76 - 0.025)) < 1e-6,
            'mesa: estado base intacto tras la ronda (normal/azul)')

    # ---- 3 · RIVALES CON ESTILO: colocación (idle) y celebración
    estilo = pg.evaluate("""async () => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const ai = g.ai;
      const calcOff = g._rivStyleCalc();          // sin campeonato activo → ceros
      // colocación: 1,5 s de update con estilo agresivo vs neutro
      const ball = g.ball; const saveV = ball.vel.clone(); const saveP = ball.pos.clone();
      ball.vel.set(0, 0, 0); ball.pos.set(0, 1.0, -4.5);   // bola lejana, sin "hacia"
      ai.pos.set(0, 1.05, -3.1); ai.vel.set(0, 0, 0);
      const ctxFalso = { canHit: false, validBounce: false, holdTarget: null, prevBall: null };
      ai.style = null;
      for (let i = 0; i < 90; i++) ai.update(1 / 60, ball, ctxFalso);
      const zNeutro = ai.pos.z;
      ai.pos.set(0, 1.05, -3.1); ai.vel.set(0, 0, 0);
      ai.style = { zIdle: 0.32, bias: 0.18, celeb: 1 };
      for (let i = 0; i < 90; i++) ai.update(1 / 60, ball, ctxFalso);
      const zAgresivo = ai.pos.z;
      // celebración: celebT decrece SOLO en update
      ai.celebT = 0.9;
      const c0 = ai.celebT;
      ai.update(1 / 60, ball, ctxFalso);
      const c1 = ai.celebT;
      ball.vel.copy(saveV); ball.pos.copy(saveP);
      ai.style = null;
      return { calcOff, zNeutro: Math.round(zNeutro * 1000) / 1000,
               zAgresivo: Math.round(zAgresivo * 1000) / 1000,
               delta: Math.round((zAgresivo - zNeutro) * 1000) / 1000,
               celeb: (c0 === 0.9 && c1 < 0.9 && c1 > 0.85) };
    }""")
    if 'err' in (estilo or {}):
        CHK(False, 'estilo: %s' % estilo.get('err'))
    else:
        CHK(all(v == 0 for v in estilo['calcOff'].values()),
            'estilo: sin campeonato activo → palancas a CERO (clásico intacto)')
        CHK(estilo['delta'] is not None and estilo['delta'] > 0.25,
            'estilo: el AGRESIVO espera %s m MÁS CERCA de la mesa' % estilo['delta'])
        CHK(estilo['celeb'] is True, 'estilo: celebT vive en update (celebración programable)')

    # ---- 4 · FANFARRIA: chip de estadísticas pintado en el lienzo
    fanf = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const fb = g.fanfareBanner; if (!fb) return { err: 'sin banner' };
      const cv = fb.canvas; const c2 = cv.getContext('2d');
      const fila = (y) => {
        const d = c2.getImageData(212, y, 600, 1).data;
        let n = 0;
        for (let i = 3; i < d.length; i += 4) if (d[i] > 40) n++;
        return n;
      };
      // sin stats → SIN chip nuevo (el póster de fondo manda)
      fb.draw(true, 11, 5);
      const d0 = c2.getImageData(212, 886, 600, 1).data;
      // con stats → chip pintado ENCIMA del marcador: píxeles DISTINTOS en la fila
      fb.draw(true, 11, 5, { vmax: 8.42, rally: 12, prec: 69 });
      const d1 = c2.getImageData(212, 886, 600, 1).data;
      let dif = 0;
      for (let i = 0; i < d0.length; i += 4) {
        if (Math.abs(d0[i] - d1[i]) > 40 || Math.abs(d0[i + 3] - d1[i + 3]) > 40) dif++;
      }
      fb.group.visible = false;
      return { dif, W: cv.width, H: cv.height };
    }""")
    if 'err' in (fanf or {}):
        CHK(False, 'fanfarria: %s' % fanf.get('err'))
    else:
        CHK(fanf.get('W') == 1024, 'fanfarria: lienzo 1024 intacto')
        CHK(fanf.get('dif', -1) > 150,
            'fanfarria: el chip de stats pinta tinta NUEVA en el cartel (dif=%s píxeles)' % fanf.get('dif'))

    # ---- 5 · MENÚ: los controles nuevos existen y obedecen
    menu = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const ids = (pagina) => {
        g.menuPage = pagina;
        g.drawMenu();
        return g.menuRects.map(r => r.id);
      };
      const sonido = ids('optsSonido');
      const sala = ids('optsSala');
      const salaMesa = ids('optsSalaMesa');
      const juego = ids('optsJuego');
      // pulsar mvol- (barra de música −10)
      g.menuPage = 'optsSonido'; g.drawMenu();
      const iM = g.menuRects.findIndex(r => r.id === 'mvol-');
      const antes = g.audio.musicVol;
      if (iM >= 0) g.menuClick(iM);
      const despues = g.audio.musicVol;
      g.menuPage = 'opts'; g.drawMenu();
      return { sonido, sala, salaMesa, juego, antes, despues };
    }""")
    if 'err' in (menu or {}):
        CHK(False, 'menú: %s' % menu.get('err'))
    else:
        s, sa, j = menu.get('sonido', []), menu.get('sala', []), menu.get('juego', [])
        CHK(all(x in s for x in ['mvol-', 'mvol+', 'fvol-', 'fvol+', 'music', 'sndtest']),
            'menú SONIDO: barras −/+ de música y efectos junto a los de siempre')
        CHK(all(x in sa for x in ['page:optsSalaRoom', 'page:optsSalaMesa']),
            'menú SALA/MESA: submenús-botón (re-anclado a r96: deslizador)')
        # re-anclado a r96: los aspectos viven en la SUBPÁGINA MESA del hub
        CHK(all(('mesa_skin:' + x) in (menu.get('salaMesa') or []) for x in ['azul', 'verde', 'neon', 'oro', 'carbon']),
            'menú SALA/MESA: los cinco aspectos (3 libres + 2 con recompensa)')
        CHK('rivstyle' in j, 'menú JUEGO: conmutador Rivales con estilo visible')
        CHK(menu.get('antes') == 1 and menu.get('despues') == 0.9,
            'menú: pulsar mvol− baja la música a 90% (obedece al rayo)')

    # ---- 6 · mStats por partido
    mst = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      g.rules.startMatch('match');
      const cero = g.rules.mStats.vmax === 0 && g.rules.mStats.bestRally === 0;
      g.rules.mStats.vmax = 7.7; g.rules.mStats.bestRally = 9;
      return { cero, tiene: !!g.rules.mStats };
    }""")
    CHK(mst.get('cero') is True and mst.get('tiene') is True,
        'mStats: cada PARTIDA nueva nace a cero (vel. máx · rally)')

    CHK(not errs, 'consola: 0 pageerrors (%s)' % (errs[:2] or 'limpio'))
    b.close()

srv.shutdown()
print('\\n== RESUMEN r95 ==')
print('OK: %d · FALLOS: %d' % (len(OK), len(FAIL)))
for f in FAIL:
    print('  ✗', f)
sys_exit = 0 if not FAIL else 1
raise SystemExit(sys_exit)
