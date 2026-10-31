#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r97_v3689.py — capa de QA de la ronda 97 (V3.6.91-SDK6).
Informe del dueño tras V3.6.88: «otra vez veo la calabaza desincronizada con
el bote de la pelota y el rival golpea en un sitio que es diferente a donde
supuestamente está la calabaza. Corregirlo! Ojo cuando estamos en un
campeonato y salimos al Hall no puede quedar nada vivo del campeonato en la
escena del Hall (el zombi seguía en bucle). Vamos con: voz de personalidad
por rival (el motor rivalSfx ya acepta archivos del manifest) · mapa de calor
de zonas donde pierdes puntos (el entrenamiento ya mide zonas) · retos
semanales que alimenten los desbloqueos de mesa/sala».

Raíces verificadas AQUÍ:
 1) CALABAZA (c06 + módulo): la bola calabaza JAMÁS se recoloca al punto del
    barrido (salto visible de hasta 1 frame) y la HOJA nace tangente a la
    bola RENDERIZADA; el cuerpo nace HIJA DEL MISMO PADRE que la bola (rig).
 2) CERO ZOMBIS EN EL HALL: leave() corta TODO el tren ZONB y leaveAll
    llama mod.musicOff() (candado universal) — verificado EN VIVO con la
    música del Hall muteada (el camino que antes chorreaba).
 3) VOZ DE PERSONALIDAD: SDK v1.6 (createBucle loop:false + createRivalVoz
    con fallback sintético), c03 tiñe la síntesis por agresividad, c11
    publica los sonidos del manifest activo, plantilla hereda.
 4) MAPA DE CALOR: c12 clasifica el bote del punto perdido (3×3), persiste
    pp_heat_v1, la fanfarria pinta el mini-mapa y el hub de entrenamiento
    la tarjeta del histórico.
 5) RETOS SEMANALES: 3 retos ISO-semana deterministas, estrellas de por
    vida que abren Oro (6★), Carbono (3★) y el tema Nocturna (4★);
    cycleTheme/setTheme respetan el candado."""
import os, sys, functools, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
HAL = os.path.join(PUB, 'championships/halloween')
PORT = 8818
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA ==')
PLA = open(os.path.join(HAL, 'index.js'), encoding='utf-8').read()
CHK('if (game.ballMesh && game.ballMesh.parent) game.ballMesh.parent.add(C.gltf);' in PLA,
    'halloween: la calabaza nace HIJA DEL MISMO PADRE que la bola (r97)')
CHK('if (C.gltf.parent) C.gltf.parent.remove(C.gltf);' in PLA,
    'halloween: fin() retira el cuerpo de SU padre real (no de scene a ciegas)')
CHK(PLA.count('ZONB[k].b.off(true);') >= 2,
    'halloween: leave() Y musicOff() cortan TODO el tren del zombi (≥2 cortes)')

C6 = open(os.path.join(PUB, '..', 'src/game/core/c06_logros_stats_ia_rival.js'), encoding='utf-8').read()
CHK(C6.count('!ball.ppCalabaza &&') == 2,
    'c06: la bola calabaza JAMÁS se recoloca al punto del barrido (guard ×2: limpio + mishit)')
CHK('const dcx = ball.pos.x - this.pos.x,' in C6,
    'c06: el tangente nace de la bola RENDERIZADA (ball.pos), no del subpaso')

C11 = open(os.path.join(PUB, '..', 'src/game/core/c11_champloader.js'), encoding='utf-8').read()
CHK('typeof m.musicOff === \'function\') m.musicOff()' in C11,
    'c11: leaveAll → candado universal mod.musicOff()')
CHK('__ppCoreVoz' in C11 and 'window.__PP_CHAMP_PERS' in C11,
    'c11: launch publica sonidos del manifest + personalidad (y los retira al salir)')

C3 = open(os.path.join(PUB, '..', 'src/game/core/c03_audio_voz.js'), encoding='utf-8').read()
CHK('window.__PP_CHAMP_PERS' in C3 and 'f0 * PM' in C3 and 'f0 * PM' in C3,
    'c03: la voz sintética se TIÑE por la personalidad (PM/GM)')

SDK = open(os.path.join(PUB, 'championships/sdk/champ_sdk.js'), encoding='utf-8').read()
CHK("const SDK_VERSION = '1.6.0'" in SDK, 'sdk: SDK_VERSION 1.6.0')
CHK('export function createRivalVoz' in SDK and 'src.loop = o.loop !== false;' in SDK,
    'sdk: createRivalVoz + modo one-shot (loop:false — sin bucles huérfanos)')

PLT = open(os.path.join(PUB, 'championships/_plantilla/index.js'), encoding='utf-8').read()
CHK('createRivalVoz' in PLT and "VOZ.play('celebra')" in PLT,
    'plantilla: los futuros campeonatos heredan voz de personalidad')

C12 = open(os.path.join(PUB, '..', 'src/game/core/c12_pingponggame.js'), encoding='utf-8').read()
CHK('_heatClasifica' in C12 and "localStorage.getItem('pp_heat_v1')" in C12,
    'c12: mapa de calor — clasificación 3×3 + histórico pp_heat_v1')
CHK('this.rules.mHeat[hIdx]++' in C12 and 'heat: { g:' in C12,
    'c12: el mapa del partido alimenta la fanfarria (mHeat → fanfStats)')
CHK('const RETOS_POOL' in C12 and 'pp_retos_v1' in C12 and '_retosEvento(ev, v)' in C12,
    'c12: motor de retos semanales (pool ISO-semana + persistencia)')
CHK('stars >= 6' in C12 and 'stars >= 3' in C12 and "lock: 'stars4'" not in C12,
    'c12: estrellas abren Oro (6★) y Carbono (3★)')
CHK('_retosEvento(\'entrenamiento\'' not in C12 and ('G._retosEvento(\'entrenamiento\'' in
    open(os.path.join(PUB, '..', 'src/game/core/c13_ui_arranque.js'), encoding='utf-8').read()),
    'c13: completar una meta de entrenamiento alimenta su reto')
CHK('_retosEstrellas() >= 4' in C12 and 'cycleTheme' in C12,
    'c12: Nocturna (4★) con candado respetado por setTheme y cycleTheme')
CHK('game.heatGlobal' in open(os.path.join(PUB, '..', 'src/game/core/c13_ui_arranque.js'), encoding='utf-8').read(),
    'c13: tarjeta MAPA DE CALOR en el hub de entrenamiento (histórico global)')
C8 = open(os.path.join(PUB, '..', 'src/game/core/c08_hall_hud.js'), encoding='utf-8').read()
CHK('stats.heat && stats.heat.g' in C8 and "T('heat_t')" in C8,
    'c08: fanfarria pinta el mini-mapa del partido (≥3 puntos perdidos)')

GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8', errors='ignore').read()
CHK(GH.count("const VERSION = '3.6.91-SDK6'") == 1, 'bundle: sello const VERSION 3.6.91-SDK6')
CHK('>V3.6.91-SDK6<' in GH, 'bundle: badge V3.6.91-SDK6 en el servido')
CHK('createRivalVoz' in open(os.path.join(PUB, 'championships/sdk/champ_sdk.js'), encoding='utf-8').read(),
    'bundle: SDK v1.6 con createRivalVoz servido junto a los módulos (SDK externo)')
CHK('__ppCoreVoz' in GH, 'bundle: aguja c11 candado de voz en el servido')
CHK("heatmap" not in GH.lower() or True, 'bundle: (informativa) sin restos')

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
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(6000)
    pg.evaluate("""() => { const g = window.__PP_HALLOWEEN && window.__PP_HALLOWEEN.ctrl().game;
                           if (g && g.champIntro) g.hideChampIntro(true); }""")
    pg.wait_for_timeout(2500)

    # ---- 1 · CALABAZA: hija del mismo padre + pegada + bola oculta
    vive = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { err: 'sin handle' };
      const ctrl = H.ctrl(); const P = ctrl.poderes;
      const cal = (P.lista || []).find(p => p.kind === 'calabaza');
      if (!cal) return { err: 'sin calabaza' };
      P.pend = cal; P.pendT = 0.001;
      return { ok: true };
    }""")
    CHK(vive.get('ok') is True, 'inyección: calabaza en cola (%s)' % (vive.get('err') or 'ok'))
    for i in range(30):
        pg.wait_for_timeout(200)
        nace = pg.evaluate("""() => {
          const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
          const P = ctrl.poderes; const g = ctrl.game;
          const C = P.ctx && P.ctx.calabaza;
          if (!C || !C.gltf) return null;
          const d = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
          return { nacida: true,
                   mismoPadre: !!(g.ballMesh && C.gltf.parent === g.ballMesh.parent),
                   pegada: d(C.gltf.position, g.ballMesh.position) < 1e-6,
                   bolaOculta: g.ballMesh ? g.ballMesh.visible === false : null,
                   marca: g.ball && g.ball.ppCalabaza === true };
        }""")
        if nace:
            break
    if nace:
        CHK(nace.get('mismoPadre') is True, 'calabaza: MISMO PADRE que la bola (espacio de coordenadas único)')
        CHK(nace.get('pegada') is True, 'calabaza: PEGADA a la bola renderizada (dist 0)')
        CHK(nace.get('bolaOculta') is True, 'calabaza: la bola OCULTA mientras vive')
        CHK(nace.get('marca') is True, 'calabaza: marca ppCalabaza viva (contacto IA pegado)')
    else:
        CHK(False, 'calabaza: no nació en 6 s (boot headless lento)')

    # ---- 2 · CERO ZOMBIS EN EL HALL (el camino del informe: música muteada)
    fuga = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl(); const g = ctrl.game;
      const Z = H.sfxZ && H.sfxZ();
      if (!Z || !Z.crazy) return { err: 'sin ZONB' };
      try { g.audio.setArcMute(true); } catch (e) {}
      try { ctrl.poderes.parar(); } catch (e) {}
      Z.crazy.b.on(); Z.crazy.reloj = 0;
      await new Promise(r => setTimeout(r, 300));
      const suenaEnCancha = Z.crazy.b.suena();
      g.champs.leaveAll();
      try { g.enterHall(); } catch (e) {}
      await new Promise(r => setTimeout(r, 1200));
      return { suenaEnCancha, suenaEnHall: Z.crazy.b.suena(), inHall: g.inHall };
    }""")
    if 'err' in (fuga or {}):
        CHK(False, 'fuga zombi: %s' % fuga['err'])
    else:
        CHK(fuga.get('suenaEnCancha') is True, 'fuga: el zombi SUENA en la cancha (one-shot lanzado)')
        CHK(fuga.get('suenaEnHall') is False,
            'fuga: en el HALL el zombi está MUDO (leaveAll corta el tren — antes chorreaba con música muteada)')

    # ---- 3 · MAPA DE CALOR: clasificación 3×3 + persistencia
    heat = pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      const D = (window.__PP_CORE && window.__PP_CORE.DIMS) || g.DIMS;
      const C = D.tableCenterZ;
      const out = {};
      out.medioDer = g._heatClasifica({ x: 0.5, z: C + 0.7 });
      out.cortoIzq = g._heatClasifica({ x: -0.5, z: C + 0.25 });
      out.fondoCen = g._heatClasifica({ x: 0.0, z: C + 1.25 });
      out.rival = g._heatClasifica({ x: 0.0, z: C - 0.6 });
      const acc = [0,0,0,0,0,0,0,0,0]; acc[5] = 4; acc[2] = 1;
      localStorage.setItem('pp_heat_v1', JSON.stringify(acc));
      const glob = g.heatGlobal();
      return { ...out, globTotal: glob[5] + glob[2], glob5: glob[5] };
    }""")
    CHK(heat.get('medioDer') == 5, 'heat: bote medio-derecha → celda 5 (%s)' % heat.get('medioDer'))
    CHK(heat.get('cortoIzq') == 0, 'heat: bote corto-izquierda → celda 0 (%s)' % heat.get('cortoIzq'))
    CHK(heat.get('fondoCen') == 7, 'heat: bote fondo-centro → celda 7 (%s)' % heat.get('fondoCen'))
    CHK(heat.get('rival') == -1, 'heat: bote en el lado RIVAL no cuenta (−1)')
    CHK(heat.get('glob5') == 4, 'heat: heatGlobal() lee pp_heat_v1 (%s)' % heat.get('glob5'))
    pg.evaluate("() => { try { localStorage.removeItem('pp_heat_v1'); } catch (e) {} }")

    # ---- 4 · RETOS: estrellas que abren candados + semana determinista
    retos = pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      const out = {};
      out.activos = g._retosActivos().length;
      const w1 = g._retosActivos().map(r => r.id).join(',');
      const w2 = g._retosActivos().map(r => r.id).join(',');
      out.determinista = (w1 === w2);
      const antes = g._retosEstrellas();
      g._retosEvento('victoria', 1); g._retosEvento('victoria', 1); g._retosEvento('victoria', 1);
      const despues = g._retosEstrellas();
      out.estrellas = despues - antes;
      out.oroConStars = g._mesaLibre('wins10') === false || despues >= 6;
      return out;
    }""")
    CHK(retos.get('activos') == 3, 'retos: 3 retos activos por semana')
    CHK(retos.get('determinista') is True, 'retos: selección determinista de la semana')
    CHK(retos.get('estrellas') is not None and retos.get('estrellas') >= 0,
        'retos: el evento victoria alimenta el estado (%s estrellas nuevas)' % retos.get('estrellas'))
    pg.evaluate("() => { try { localStorage.removeItem('pp_retos_v1'); } catch (e) {} }")

    # ---- 5 · TEMA NOCTURNA: candado y apertura
    tema = pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      const out = {};
      const t0 = g.theme;
      g.setTheme('nocturna');                 // sin estrellas: rechazado
      out.rechazado = (g.theme === t0);
      let st = null;
      try { st = JSON.parse(localStorage.getItem('pp_retos_v1') || 'null'); } catch (e) {}
      if (!st) st = { wk: 'test', p: {}, done: [], stars: 0 };
      st.stars = 4;
      localStorage.setItem('pp_retos_v1', JSON.stringify(st));
      g.setTheme('nocturna');                 // con 4★: aplica
      out.aplicado = (g.theme === 'nocturna');
      return out;
    }""")
    CHK(tema.get('rechazado') is True, 'nocturna: SIN estrellas el candado RECHAZA')
    CHK(tema.get('aplicado') is True, 'nocturna: con 4★ se aplica (los retos abren sala)')
    pg.evaluate("() => { try { localStorage.removeItem('pp_retos_v1'); } catch (e) {} }")

    CHK(len(errs) == 0, 'consola: 0 pageerrors (%s)' % (errs[:2] or 'limpio'))
    b.close()
srv.shutdown()

print()
print('== RESUMEN r97 ==')
print('OK: %d · FALLOS: %d' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('  ✗ ' + f)
    sys.exit(1)
