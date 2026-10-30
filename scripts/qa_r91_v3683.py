#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r91_v3683.py — capa de QA en vivo de la ronda 91 (V3.6.88-SDK6).
Informe del dueño tras V3.6.82: «no suena la música de fondo en Halloween ·
las manos de zombi están mal recortadas y no sale la parte inferior (la
tierra y el brazo) · de la calabaza sólo se ve un trocito del rabito verde ·
NO TENEMOS EL MAPA EN LA PARED (en TODOS los campeonatos aparece perfecto) ·
ha vuelto el solapamiento del rival (dos imágenes superpuestas) · los sonidos
del zombi sólo suenan algunos · no he visto zombi_defeated ni cambios de cara
en el partido».
Raíces cazadas y verificadas AQUÍ:
 1) BSO: createMusic invocaba url/vol NO-función → TypeError tragado → muda
    (forma canónica en el módulo + SDK tolerante val()).
 2) MAPA: opacity-gate por setInterval DORMIDO (la sonda r91b cazó opacity 0
    con image vivo) → receta WizardMap EXACTA + textura en el CALLBACK del
    loader + respaldo por-frame en refresco().
 3) CALABAZA: _preparaCuerpoR88 convertía material en ARRAY → THREE r186
    (projectObject) con material-array SÓLO dibuja geometry.groups →
    LatheGeometry/TorusGeometry (SIN grupos) = CERO draw calls = «sólo el
    rabito» (CylinderGeometry sí tiene grupos).
 4) MANOS: el cultivo 0.70 escondía la tierra y el brazo → arte integral.
 5) RIVAL: tres motores pisándose (reaccion + legacy por-frame + norma r57)
    → una sola norma + hold del final (_finalT) + sonido por emoción."""
import os, sys, functools, json, subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
HAL = os.path.join(PUB, 'championships/halloween')
SDK = os.path.join(PUB, 'championships/sdk/champ_sdk.js')
PORT = 8811
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA ==')
man = json.load(open(os.path.join(HAL, 'manifest.json')))
CHK(man.get('version') == 3, 'manifest: version=3 (r91)')
CHK(any(n.startswith('v5 (r91)') for n in man.get('notes', [])), 'manifest: nota v5 (r91) presente')
au = man.get('audio', {})
CHK(au.get('music') == 'assets/melodia.mp3', 'manifest: BSO melodia.mp3 (r93 — melodía nueva del dueño)')
CHK(au.get('musicVolume') == 0.18, 'manifest: volumen BSO 0,18')
opts = au.get('musicOpts') or {}
CHK(opts.get('gateStart') is True and opts.get('gateOn') is False and opts.get('renace') is True,
    'manifest: musicOpts del motor probado (gateStart/renace, sin gateOn)')

PLA = open(os.path.join(HAL, 'index.js'), encoding='utf-8').read()
SDKS = open(SDK, encoding='utf-8').read()

# 1 · BSO — forma canónica + SDK tolerante (la r90 pasaba string/número)
CHK('url: so.music ? (() => A(String(so.music).replace(/^assets\\//, \'\'))) : null' in PLA,
    'index: createMusic con url COMO FUNCIÓN (forma canónica magia/oeste)')
CHK('vol: () => (so.musicVolume != null ? so.musicVolume : 0.15)' in PLA,
    'index: createMusic con vol COMO FUNCIÓN')
CHK('const val = (x, def) =>' in SDKS and 'return (typeof x === \'function\') ? x() : x;' in SDKS,
    'sdk: createMusic TOLERANTE (url/vol función o valor — el motor no puede volver a quedar mudo por forma)')
CHK('function objetivo() { return val(o.vol, 0.15) || 0.15; }' in SDKS and 'function srcURL() { return val(o.url, undefined); }' in SDKS,
    'sdk: objetivo()/srcURL() pasan por val()')

# 2 · MAPA — receta WizardMap + gate por CALLBACK + respaldo
CHK('const raiz = this.game.rig || this.game.scene;' in PLA and 'raiz.add(this.grupo)' in PLA,
    'index: el mapa cuelga del RIG (el padre de los 5 campeonatos que el dueño ve bien)')
CHK('this.pos = m.pos || [-2.98, 1.5, -0.9]' in PLA, 'index: posición WizardMap por defecto [-2.98, 1.5, -0.9]')
CHK('new THREE.TextureLoader().load(this._urlArte, (tex) =>' in PLA and 'this.plane.material.opacity = 1;' in PLA,
    'index: la textura del mapa se asigna DENTRO del callback del loader (gate imposible de perder)')
CHK('RESPALDO DEL GATE' in PLA and 'this.plane.material.opacity = 1' in PLA and 'refresco()' in PLA,
    'index: respaldo por-frame en refresco() (si hay imagen y el póster sigue apagado, se enciende)')
CHK('new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, opacity: 0 })' in PLA,
    'index: material SIN mapa + opacity 0 (patrón magia — nunca rectángulo negro)')

# 3 · CALABAZA — el bug material-array cazado
CHK('o.material = eraArray ? clonados : clonados[0];' in PLA,
    'index: material único vuelve SINGLE (THREE r186: material-array sin groups = cero draw calls)')
CHK('side: THREE.DoubleSide, color: 0xe8720c' in PLA.replace('\n', ' ').replace('  ', ' ') or ('THREE.DoubleSide' in PLA and '0xe8720c' in PLA),
    'index: cuerpo del lathe a PRUEBA DE CASCO (DoubleSide + naranja sólido)')
CHK('grp.traverse((o) => { if (o.isMesh) o.frustumCulled = false; })' in PLA,
    'index: frustumCulled OFF en la calabaza (ninguna esfera envolvente la colará)')

# 4 · MANOS — arte integral
CHK('const MANO_CULTIVO = 1.0;' in PLA and 'const MANO_OFF_Y = 0.0;' in PLA,
    'index: ARTE COMPLETO de la mano (cultivo 1.0/offset 0.0 — la tierra y el brazo SE VEN)')

# 5 · RIVAL — una sola norma + hold del final + sonido por emoción
CHK('this.rival.reaccion(' not in PLA, 'index: reaccion() RETIRADA de onPoint (la norma r57 del núcleo manda sola)')
CHK('SONIDO = { laughing: \'laugh\', crazy: \'crazy\', victory: \'victory\', defeated: \'defeated\' }' in PLA,
    'index: la emoción llega CON SU SONIDO (laugh/crazy/victory/defeated por rivalEmocion)')
CHK('enDuelo(en) { this.timer = 0;' in PLA, 'index: cada etapa nueva RECOMPONE la cara (timer 0)')
CHK('this._finalT = 4.2;' in PLA and 'if (this._finalT > 0) this._finalT -= dt;' in PLA,
    'index: hold de la cara final (defeated/victory viven 4,2 s — sala() ya no las pisa)')
CHK('if (this.rival && !(this._finalT > 0)) this.rival.estadoBase(\'idle\');' in PLA,
    'index: sala() NO resetea la cara final mientras el hold vive')
CHK('mus: () => MUSIC, sfxZ: () => ZONB' in PLA, 'index: puentes de diagnóstico mus/sfxZ')

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
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=4000)
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(9000)

    # ---- MAPA: grupo en RIG + opacity 1 + textura viva
    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
      const ctrl = H.ctrl(), g = ctrl.game;
      const out = { vive: true };
      const gr = ctrl.mapa.grupo, mp = ctrl.mapa.plane;
      out.grupo = { enRig: gr.parent === g.rig, pos: gr.position.toArray().map((v) => +v.toFixed(3)),
                    rotY: +gr.rotation.y.toFixed(4), hijos: gr.children.length };
      out.op = mp.material.opacity;
      out.map = !!mp.material.map;
      out.texViva = !!(mp.material.map && mp.material.map.image);
      out.cs = mp.material.map ? String(mp.material.map.colorSpace) : null;
      return out;
    }""")
    CHK(st.get('vive') is True, 'halloween vivo')
    if not st.get('vive'):
        print(json.dumps(st, indent=1)); srv.shutdown(); b.close(); sys.exit(1)
    g88 = st.get('grupo') or {}
    CHK(g88.get('enRig') is True, 'mapa: colgado del RIG (padre probado)')
    CHK(g88.get('pos') == [-2.98, 1.5, -0.9], 'mapa: pos WizardMap %s' % g88.get('pos'))
    CHK(abs((g88.get('rotY') or 0) - 1.5708) < 1e-3, 'mapa: PARALELO a la pared izquierda (rotY π/2)')
    CHK(st.get('op') == 1, 'mapa: opacity ABIERTA (el gate por callback no duerme)')
    CHK(st.get('texViva') is True and st.get('map') is True, 'mapa: TEXTURA VIVA asignada (image presente)')
    CHK(st.get('cs') == 'srgb', 'mapa: SRGB (saturación del arte del dueño)')

    # ---- CADENA DEL NÚCLEO → cara (lo que corre en un partido real)
    caras = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game; const C = H.ctrl();
      const cara = () => { try { const mm = C.rival.r.mat; return mm && mm.map && mm.map.image ? mm.map.image.src.split('/').pop() : null; } catch (e) { return 'ERR'; } };
      const out = { activo: !!(g.champs && g.champs.active) };
      g.rivalEmocion('laughing', 2.0, 'victory'); out.laughing = cara();
      g.rivalEmocion('angry', 2.0);               out.angry = cara();
      g.rivalEmocion('surprised', 2.0);           out.surprised = cara();
      g.rivalEmocion('defeated', 0);              out.defeated = cara();
      g.rivalEmocion('idle', 0);                  out.idle = cara();
      return out;
    }""")
    CHK(caras.get('activo') is True, 'norma: champs.active en el campeonato')
    CHK(caras.get('laughing') == 'laughing.webp', 'norma: núcleo laughing → cara laughing (%s)' % caras.get('laughing'))
    CHK(caras.get('angry') == 'angry.webp', 'norma: núcleo angry → cara angry')
    CHK(caras.get('surprised') == 'surprised.webp', 'norma: núcleo surprised → cara surprised')
    CHK(caras.get('defeated') == 'defeated.webp', 'norma: núcleo defeated → cara defeated')

    # ---- FINAL: defeated aguanta sala() (hold) y vuelve solo
    fin = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const C = H.ctrl();
      const cara = () => { try { const mm = C.rival.r.mat; return mm && mm.map && mm.map.image ? mm.map.image.src.split('/').pop() : null; } catch (e) { return 'ERR'; } };
      C.dueloVivo = true; C.onMatchOver(true);
      const inmediato = cara();
      C.sala();
      const trasSala = cara();
      return { inmediato, trasSala };
    }""")
    CHK(fin.get('inmediato') == 'defeated.webp', 'final: al vencerlo, defeated INMEDIATO (%s)' % fin.get('inmediato'))
    CHK(fin.get('trasSala') == 'defeated.webp', 'final: defeated SOBREVIVE a sala() (hold _finalT — el dueño por fin LO VE)')

    # ---- CALABAZA: material SINGLE + DoubleSide + color + frustum + en escena
    cal = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const V3 = (Object.getPrototypeOf(g.camera.position).constructor);
      if (!g.ball || !g.ball.pos) g.ball = { pos: new V3(), vel: new V3(), spin: new V3() };
      g.ball.pos.set(0.15, 0.95, -0.6);
      /* r94 · RE-ANCLAJE HONESTO: la calabaza sigue ahora la bola RENDERIZADA
       * (ballMesh.position — el lugar exacto donde la bola se pintaría, garantía
       * del informe del dueño). El núcleo sincroniza ballMesh ← ball.pos cada
       * frame (c12 §7) ANTES de champs.update; la sonda sintética hace lo mismo. */
      if (g.ballMesh) g.ballMesh.position.copy(g.ball.pos);
      const ctxP = {};
      H.pods.calabaza.inicio(g, { duration: 10 }, H.ctrl(), ctxP);
      H.pods.calabaza.paso(0.033, g, { duration: 10 }, H.ctrl(), ctxP);
      const C = ctxP.calabaza; if (!C) return { err: 'sin ctx' };
      const cuerpo = C.gltf.children[0];
      const m = cuerpo.material;
      cuerpo.updateWorldMatrix(true, false);
      const wp = cuerpo.getWorldPosition(new V3());
      return { enEscena: !!C.gltf.parent, esArray: Array.isArray(m),
               side: m.side, color: '#' + m.color.getHexString(), map: !!m.map,
               culled: cuerpo.frustumCulled, vis: cuerpo.visible,
               wp: [+wp.x.toFixed(2), +wp.y.toFixed(2), +wp.z.toFixed(2)] };
    }""")
    CHK(cal.get('enEscena') is True, 'calabaza: cuerpo EN ESCENA desde el disparo')
    CHK(cal.get('esArray') is False, 'calabaza: material SINGLE (el bug del array — LatheGeometry sin groups — CAZADO: %s)' % str(cal.get('esArray')))
    CHK(cal.get('side') == 2, 'calabaza: DoubleSide (a prueba de culled de caras)')
    CHK(str(cal.get('color', '')).lstrip('#').startswith(('e8', 'e7')),
        'calabaza: naranja sólido (%s — el paso de pudrición tñe desde e8720c)' % cal.get('color'))
    CHK(cal.get('culled') is False, 'calabaza: frustumCulled OFF')
    CHK(cal.get('vis') is True, 'calabaza: VISIBLE')
    CHK(cal.get('wp') == [0.15, 0.95, -0.6], 'calabaza: centrada en la bola %s' % cal.get('wp'))

    # ---- MANO: arte completo (repeat 1 / offset 0) al terminar de subir
    mano = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const ctxP = {};
      H.pods.mano.inicio(g, { duration: 20 }, H.ctrl(), ctxP);
      const M = ctxP.mano;
      return new Promise((res) => {
        const t0 = Date.now();
        const espera = () => {
          if (M.tex.length < 1 && Date.now() - t0 < 8000) return setTimeout(espera, 200);
          try { H.pods.mano._spawn(g, M); } catch (e) { res({ err: String(e) }); return; }
          const v = M.vivos[0];
          if (v) { for (let i = 0; i < 26; i++) H.pods.mano.paso(0.05, g, { duration: 20 }, H.ctrl(), ctxP); }
          if (!v) { res({ err: 'sin mano' }); return; }
          res({ rep: +v.tex.repeat.y.toFixed(3), off: +v.tex.offset.y.toFixed(3), fase: v.fase });
        };
        espera();
      });
    }""")
    CHK(mano.get('rep') == 1 and mano.get('off') == 0,
        'mano: ARTE INTEGRAL al subir (repeat=%s offset=%s — la tierra y el brazo del fondo VISIBLES)' % (mano.get('rep'), mano.get('off')))

    # ---- BSO: el efecto EXACTO del botón JUGAR de la intro y DURANTE el duelo
    pg.evaluate("""() => { const g = window.__PP_HALLOWEEN.ctrl().game; g.hideChampIntro(true); }""")
    pg.wait_for_timeout(9000)
    mus = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const m = H.mus() ? H.mus().estado() : null;
      return { mus: m, ctx: g.audio && g.audio.ctx ? g.audio.ctx.state : null };
    }""")
    CHK((mus.get('mus') or {}).get('sonando') is True, 'BSO: SONANDO tras la intro (JUGAR → hideChampIntro(true) → on())')
    CHK((mus.get('mus') or {}).get('cargado') is True, 'BSO: buffer cargado (melodia.mp3 178,4 s — r93)')
    pg.evaluate("""() => { window.__PP_HALLOWEEN.ctrl().serveTrigger(0); }""")
    pg.wait_for_timeout(5000)
    mus2 = pg.evaluate("""() => { const m = window.__PP_HALLOWEEN.mus(); return m ? m.estado() : null; }""")
    CHK((mus2 or {}).get('sonando') is True, 'BSO: SIGUE sonando durante el DUELO')

    # ---- SONIDOS del zombi: los 4 decodifican a 44100 EN ESTE NAVEGADOR
    dec = pg.evaluate("""async () => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      const out = [];
      for (const f of ['risas.mp3', 'zombi_crazy.mp3', 'zombi_victory.mp3', 'zombi_defeated.mp3']) {
        try {
          const r = await fetch('championships/halloween/assets/' + f);
          const ab = await g.audio.ctx.decodeAudioData(await r.arrayBuffer());
          out.push({ f, rate: ab.sampleRate, dur: +ab.duration.toFixed(2) });
        } catch (e) { out.push({ f, err: String(e).slice(0, 40) }); }
      }
      return out;
    }""")
    for d in dec:
        CHK(d.get('rate') == 44100 and 'err' not in d,
            'sonido: %s decodifica a 44100 (%s s)' % (d.get('f'), d.get('dur')))

    # ---- UN SOLO PLANO del zombi tras re-entrada (el solape no vuelve)
    pg.evaluate("""() => { window.__PP_HALLOWEEN.ctrl().startChamp(); }""")
    pg.wait_for_timeout(2500)
    uni = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const EST = ['present','idle','focused','surprised','panic','laughing','crazy','angry','picando','loosing','defeated','victory'];
      let n = 0;
      g.scene.children.forEach((c) => {
        let src = null;
        try { const m = c.material; const map = m && m.map; if (map && map.image && map.image.src) src = map.image.src; } catch (e) {}
        if (!src) return;
        const i = src.indexOf('/championships/halloween/assets/');
        if (i < 0) return;
        const base = src.slice(i + '/championships/halloween/assets/'.length).replace('.webp', '');
        if (EST.includes(base)) n++;
      });
      return n;
    }""")
    CHK(uni == 1, 'rival: EXACTAMENTE UN plano del zombi tras re-entrada (%s — el solape no vuelve)' % uni)

    # Capturas: sala + mapa
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(0.0, 1.55, 0.75);
      g.camera.lookAt(-1.2, 1.35, -1.9);
    }""")
    pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r91_sala.png'))
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(-0.5, 1.5, -0.55);
      g.camera.lookAt(-2.98, 1.48, -0.9);
    }""")
    pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r91_mapa.png'))
    print('· capturas r91 escritas')

    if errs:
        print('ERRORES DE PÁGINA:', errs[:6])
        CHK(False, 'sin pageerrors (%d)' % len(errs))
    else:
        CHK(True, 'sin pageerrors')
    b.close()
srv.shutdown()

print('== RESUMEN ==')
print('OK %d / FALLO %d' % (len(OK), len(FAIL)))
for f in FAIL:
    print('  ✗', f)
sys.exit(0 if not FAIL else 1)
