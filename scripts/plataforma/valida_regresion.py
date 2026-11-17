"""Fase G · BATERÍA DE NO-REGRESIÓN de la plataforma de campeonatos.

Comprueba, con el juego real en Chromium:
  1. El menú CAMPEONATOS lista EXACTAMENTE los publicados (los borradores NO).
  2. Previsualización ?champ=<id> de un BORRADOR real: módulo carga, sala
     monta, UNA sola melodía audible, 0 errores JS. Si no hay borrador en el
     proyecto, la batería fabrica uno temporal desde la demo estacion_orbital,
     lo prueba y lo deja como estaba (prueba también el ciclo de vida).
  3. Cada campeonato publicado: launch → nunca 2 melodías, 0 errores JS.
Uso: python3 scripts/plataforma/valida_regresion.py [borrador_id]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
CHAMPS = RAIZ / 'public' / 'championships'
DEMO = 'estacion_orbital'
TMP = 'regresion_tmp'

fallos = []


def prepara_borrador():
    """Devuelve el id del borrador a previsualizar (crea uno temporal si hace falta)."""
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg and (CHAMPS / arg / 'manifest.json').is_file():
        m = json.loads((CHAMPS / arg / 'manifest.json').read_text(encoding='utf-8'))
        if m.get('estado', 'publicado') in ('borrador', 'validacion', 'listo'):
            return arg, False
    # clona la demo como borrador temporal
    if not (CHAMPS / DEMO).is_dir():
        return None, False
    if (CHAMPS / TMP).exists():
        shutil.rmtree(CHAMPS / TMP)
    shutil.copytree(CHAMPS / DEMO, CHAMPS / TMP)
    mf = CHAMPS / TMP / 'manifest.json'
    m = json.loads(mf.read_text(encoding='utf-8'))
    m['id'] = TMP
    m['estado'] = 'borrador'
    m['storage'] = f'pp_champ_{TMP}_*'
    mf.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding='utf-8')
    js = (CHAMPS / TMP / 'index.js').read_text(encoding='utf-8')
    js = js.replace(f"id: '{DEMO}'", f"id: '{TMP}'").replace(f"'pp_champ_{DEMO}_", f"'pp_champ_{TMP}_")
    (CHAMPS / TMP / 'index.js').write_text(js, encoding='utf-8')
    subprocess.run([sys.executable, str(RAIZ / 'scripts/plataforma/genera_indice.py')],
                   capture_output=True, timeout=60)
    return TMP, True


def limpia_borrador(temporal):
    if temporal and (CHAMPS / TMP).exists():
        shutil.rmtree(CHAMPS / TMP)
        subprocess.run([sys.executable, str(RAIZ / 'scripts/plataforma/genera_indice.py')],
                       capture_output=True, timeout=60)
        print('  · borrador temporal retirado e índice regenerado')


BORRADOR, TEMPORAL = prepara_borrador()


import atexit
atexit.register(lambda: limpia_borrador(TEMPORAL))

from playwright.sync_api import sync_playwright

INIT = """
(() => {
  window.__PP_SRC = [];
  const proto = AudioContext.prototype;
  const orig = proto.createBufferSource;
  proto.createBufferSource = function (...a) {
    const src = orig.apply(this, a);
    const rec = { ctx: this, loop: false, started: 0, stopped: 0,
      bufDur: 0, gain: null };
    const dLoop = Object.getOwnPropertyDescriptor(AudioBufferSourceNode.prototype, 'loop');
    Object.defineProperty(src, 'loop', {
      get() { return dLoop.get.call(src); },
      set(v) { rec.loop = !!v; dLoop.set.call(src, v); },
    });
    const dBuf = Object.getOwnPropertyDescriptor(AudioBufferSourceNode.prototype, 'buffer');
    Object.defineProperty(src, 'buffer', {
      get() { return dBuf.get.call(src); }, set(b) { rec.bufDur = b ? b.duration : 0; },
    });
    const _connect = src.connect.bind(src);
    src.connect = (dst, ...r) => {
      if (dst && dst.gain && dst.gain.value !== undefined) rec.gain = dst;
      return _connect(dst, ...r);
    };
    const _start = src.start.bind(src);
    src.start = (...sa) => { rec.started++; window.__PP_SRC.push(rec); return _start(...sa); };
    const _stop = src.stop.bind(src);
    src.stop = (...sa) => { rec.stopped++; return _stop(...sa); };
    return src;
  };
})();
"""

SNAP = """
() => {
  const G = window.__PP_GAME;
  const A = G.audio;
  const vivos = (window.__PP_SRC || [])
    .filter((s) => s.started > 0 && s.stopped === 0 && s.loop && s.bufDur > 3);
  const audibles = vivos.filter((s) => s.gain && (s.gain.gain.value || 0) > 0.002
    && s.ctx.state === 'running');
  return {
    menu: G.champs.list().map((x) => x.id),
    activo: G.champs.activeId,
    audibles: audibles.length,
    pistas: vivos.map((s) => +s.bufDur.toFixed(1)),
  };
}
"""

fallos = []


def chk(cond, msg):
    print(('  ✓ ' if cond else '  ✗ ') + msg)
    if not cond:
        fallos.append(msg)



def _prueba_borrador(b, INIT, borrador):
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    errs2 = []
    pg.on("pageerror", lambda e: errs2.append(str(e)))
    pg.add_init_script(INIT)
    pg.goto(f"http://localhost:3000/game.html?champ={borrador}",
            wait_until="load", timeout=60000)
    pg.wait_for_timeout(8000)
    pg.evaluate("""() => { const g = window.__PP_GAME;
      g.audio.ensure(); if (g.audio.ctx && g.audio.ctx.state !== 'running')
      g.audio.ctx.resume(); g.closeMenu(); }""")
    pg.wait_for_timeout(4000)
    s2 = pg.evaluate(SNAP)
    print(f'2 · PREVISUALIZACIÓN ?champ={borrador} (borrador, fuera del menú)')
    chk(s2['activo'] == borrador, f'el borrador se lanza por preview (activo={s2["activo"]})')
    chk(borrador not in s2['menu'], 'el borrador NO está en el catálogo público')
    chk(s2['audibles'] <= 1, f'NUNCA dos melodías ({s2["audibles"]}) · pistas {s2["pistas"]}')
    chk(len(errs2) == 0, f'0 errores JS en el borrador ({len(errs2)})')
    for e in errs2[:4]:
        print('    -', e[:150])
    pg.close()


with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])

    # ---- 1 · catálogo público (sin borradores) -------------------------
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.goto("http://localhost:3000/game.html", wait_until="load", timeout=60000)
    pg.wait_for_timeout(6000)
    pg.evaluate("""() => { const g = window.__PP_GAME;
      g.audio.ensure(); if (g.audio.ctx && g.audio.ctx.state !== 'running')
      g.audio.ctx.resume(); }""")
    # el índice carga en secuencia (fetch por campeonato): espera a que asiente
    s = None
    for _ in range(20):
        pg.wait_for_timeout(1000)
        s = pg.evaluate(SNAP)
        if len(s['menu']) >= 3:
            break
    print('1 · CATÁLOGO PÚBLICO')
    chk(s['menu'] == ['locura', 'magia', 'oeste'],
        f"el menú lista los publicados y solo ellos: {s['menu']}")
    chk(len(errs) == 0, f'0 errores JS en el arranque ({len(errs)})')
    for e in errs[:4]:
        print('    -', e[:150])
    pg.close()

    # ---- 2 · borrador por previsualización ------------------------------
    borrador = BORRADOR
    if not borrador:
        print('2 · PREVISUALIZACIÓN — sin borrador disponible: SALTADA')
    else:
        _prueba_borrador(b, INIT, borrador)

    # ---- 3 · cada campeonato publicado ----------------------------------
    for cid in ('locura', 'magia', 'oeste'):
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        errs3 = []
        pg.on("pageerror", lambda e: errs3.append(str(e)))
        pg.add_init_script(INIT)
        pg.goto("http://localhost:3000/game.html", wait_until="load", timeout=60000)
        pg.wait_for_timeout(6000)
        pg.evaluate("""() => { const g = window.__PP_GAME;
          g.audio.ensure(); if (g.audio.ctx && g.audio.ctx.state !== 'running')
          g.audio.ctx.resume();
          g.menuOpen = true; g.audio.setArcDuck(true); g.audio.setMusicWanted(true); }""")
        pg.wait_for_timeout(1000)
        pg.evaluate(f"() => window.__PP_GAME.champs.launch('{cid}')")
        pg.wait_for_timeout(2500)
        pg.evaluate("() => { window.__PP_GAME.closeMenu(); window.__PP_GAME.audio.setArcDuck(false); }")
        pg.wait_for_timeout(2500)
        s3 = pg.evaluate(SNAP)
        print(f'3 · PUBLICADO {cid}')
        chk(s3['activo'] == cid, 'lanza y queda activo')
        chk(s3['audibles'] <= 1, f'NUNCA dos melodías ({s3["audibles"]}) · pistas {s3["pistas"]}')
        chk(len(errs3) == 0, f'0 errores JS ({len(errs3)})')
        for e in errs3[:4]:
            print('    -', e[:150])
        pg.close()

    b.close()

print()
if fallos:
    print(f'✗ REGRESIÓN: {len(fallos)} fallos')
    sys.exit(1)
print('✓ SIN REGRESIONES — núcleo + 3 campeonatos + plataforma en orden')
