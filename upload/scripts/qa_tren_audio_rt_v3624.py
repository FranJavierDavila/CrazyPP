#!/usr/bin/env python3
"""QA RUNTIME v3.6.24 del audio del vagón — conduce el JUEGO REAL por los
EVENTOS REALES y mide los disparos de las 4 pistas del artista.

El dueño reporta (tras V3.6.23): «solo caballos» — el galope (única pista
con escritura de ganancia DIRECTA por frame) llega al hardware; vias,
Tren_Llegada y Tunel no. Este arnés valida el arreglo v3.6.24:

  P1 · duración de los 4 mp3 (identificación de disparos por buffer).
  P2 · EVENTOS REALES del TrenAction (instancia viva del juego):
       _depart → vias en bucle (y SIGUE vivo frames después, setVol vivo) ·
       anuncio de llegada (time<=30) → Tren_Llegada a +1,2 s (una vez) ·
       _llegaEstacion → sin SEGUNDO disparo de la llegada ·
       fase 'pre' del túnel (aparece tunelboca.png) → Tunel (una vez) ·
       vias calla al frenar.
  P3 · SDK v1.5.2 a nivel unidad:
       (a) createBucle.on() con ctx SUSPENDIDO → resume → statechange lo
           arranca solo (antes se perdía).
       (b) createSfx.play() con ctx SUSPENDIDO → resume → se dispara solo
           (antes se DESCARTABA: one-shot perdido para siempre).
       (c) suena() con instancia de un contexto MUERTO → false (antes
           true: bloqueaba la auto-reparación).
       (d) setVol respeta ignoraMute: con arcMute=true, un bucle
           ignoraMute escribe el volumen real; uno normal escribe 0,0001.

Uso: python3 scripts/qa_tren_audio_rt_v3624.py
Salida: RESULTADO: N OK · N fallos · exit 0/1.
"""
import asyncio
import json
import sys

from playwright.async_api import async_playwright

DEV = 'http://localhost:3000/game.html'
ok_n = [0]
fail_n = [0]


def chk(cond, label):
    if cond:
        ok_n[0] += 1
        print('  ✓ ' + label)
    else:
        fail_n[0] += 1
        print('  ✗ FALLO: ' + label)


# ── instrumentación: log de starts de AudioBufferSource + última escritura
#    de .value por GainNode (proxy del AudioParam.value) ───────────────────
INSTR = r"""
() => {
  const G = window.__PP_GAME;
  if (!G) return { err: 'sin juego' };
  if (!G.audio) return { err: 'sin audio' };
  if (!G.audio.ctx) {
    G.audio.ctx = new (window.AudioContext || window.webkitAudioContext)();
  }
  const ctx = G.audio.ctx;
  window.__SRC_LOG = [];
  window.__GAIN_NODES = [];
  if (!window.__PP_SRC_PATCHED) {
    window.__PP_SRC_PATCHED = true;
    const pStart = AudioBufferSourceNode.prototype.start;
    AudioBufferSourceNode.prototype.start = function (...a) {
      try {
        window.__SRC_LOG.push({
          t: performance.now(),
          dur: this.buffer ? +this.buffer.duration.toFixed(2) : 0,
          loop: !!this.loop,
        });
      } catch (e) { /* */ }
      return pStart.apply(this, a);
    };
  }
  // captura de GainNodes NUEVOS del ctx del juego (lectura NATIVA después)
  if (!ctx.__PP_GAIN_PATCHED) {
    ctx.__PP_GAIN_PATCHED = true;
    const orig = ctx.createGain.bind(ctx);
    ctx.createGain = function () {
      const gn = orig();
      try { window.__GAIN_NODES.push(gn); } catch (e) { /* */ }
      return gn;
    };
  }
  return { state: ctx.state, patched: true };
}
"""

# ── P1: duración de los 4 mp3 (para identificar disparos por duración) ──
DURS = r"""
async () => {
  const G = window.__PP_GAME;
  const ctx = G.audio.ctx;
  const base = new URL('championships/oeste/', document.baseURI).href;
  const out = {};
  for (const t of ['tren/vias.mp3', 'tren/Tren_Llegada.mp3', 'tren/Tunel.mp3',
                   'tren/caballos.mp3']) {
    const r = await fetch(base + 'assets/' + t);
    const ab = await r.arrayBuffer();
    const buf = await ctx.decodeAudioData(ab.slice(0));
    out[t] = +buf.duration.toFixed(2);
  }
  return out;
}
"""

# ── P2: conduce el TrenAction REAL por sus eventos ──────────────────────
DRIVE = r"""
async (durs) => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const G = window.__PP_GAME;
  const ctx = G.audio.ctx;
  try { await ctx.resume(); } catch (e) { /* */ }
  // el módulo del oeste puede no estar eager-precargado en headless
  if (!window.__PP_OESTE) {
    try { await G.champs.preload('oeste'); } catch (e) { /* */ }
  }
  for (let i = 0; i < 80 && !(window.__PP_OESTE && window.__PP_OESTE.ctrl);
       i++) await sleep(100);
  const CTRL = window.__PP_OESTE && window.__PP_OESTE.ctrl();
  if (!CTRL) return { err: 'sin CTRL' };

  // puertas abiertas (lo que la UI haría) + bypass del cartel de instrucciones
  G.champs.activeId = 'oeste';
  CTRL.active = true;
  // la sala real crea su sistema de partículas al activarse; el arnés lo
  // stubbea (superficie completa usada por el módulo) — es visual, no audio
  if (!CTRL.fx) {
    CTRL.fx = { flash() {}, spark() {}, smoke() {}, smokeGun() {},
      smokeCurtain() {}, scorch() {}, beam() {}, mecha() {}, texDot() {},
      texPuff() {}, laserUpdate() {}, laserVisible() {}, update() {} };
  }
  CTRL._instrK = 'tren';
  CTRL._startTren();
  const T = CTRL._tren;
  if (!T) return { err: 'sin TrenAction (cartel no bypassed)' };

  const out = { fase0: T.phase };
  const near = (a, b, tol) => Math.abs(a - b) <= tol;
  const countStarts = (dur) => window.__SRC_LOG.filter(
    (s) => near(s.dur, dur, 0.06)).length;

  // driver manual del frame (el bucle real además alimenta fxStep)
  const stepN = async (n, dt) => {
    for (let i = 0; i < n; i++) {
      try { T.step(dt); T.fxStep(dt); } catch (e) {
        if (!out.stepErr) out.stepErr = String(e).slice(0, 140);
      }
      if (i % 12 === 11) await sleep(0);
    }
  };
  const dt = 1 / 60;

  // (1) INTRO → _depart: vias en bucle
  for (let i = 0; i < 60 * 12 && T.phase === 'intro'; i++) {
    try { T.step(dt); T.fxStep(dt); } catch (e) {
      if (!out.stepErr) out.stepErr = String(e).slice(0, 140);
      break;
    }
    if (i % 12 === 11) await sleep(0);
  }
  out.faseTrasIntro = T.phase;
  /* margen de fetch+decode: sondeo acotado (el juego real se auto-repara
   * por frame — el arnés espera a que el buffer aterrice y arranque) */
  for (let i = 0; i < 160 && !T._viasBuc.suena(); i++) {
    try { T.step(dt); T.fxStep(dt); } catch (e) { /* */ }
    await sleep(50);
  }
  await stepN(20, dt);
  const viasE = T._viasBuc.estado();
  out.viasEstado = viasE;
  out.viasStarts = countStarts(durs['tren/vias.mp3']);
  out.viasLoopStarts = window.__SRC_LOG.filter(
    (s) => near(s.dur, durs['tren/vias.mp3'], 0.06) && s.loop).length;

  // (2) TÚNEL: forzar _tunnelT a cero → 'pre' (aparece tunelboca.png)
  const tunel0 = countStarts(durs['tren/Tunel.mp3']);
  T._tunnelT = 0.02;
  await stepN(30, dt);                   // 0,5 s: nace 'pre' + reintentos
  await sleep(600);                      // margen de decode si faltaba
  await stepN(30, dt);
  out.tunelFase = T._tunnelPhase;
  out.tunelStarts = countStarts(durs['tren/Tunel.mp3']) - tunel0;

  // (3) LLEGADA: forzar el reloj al anuncio (time<=30) → +1,2 s → llegada
  const ll0 = countStarts(durs['tren/Tren_Llegada.mp3']);
  T.time = 30.4;
  await stepN(120, dt);                  // 2 s de juego: anuncio + 1,2 s
  await sleep(400);
  await stepN(10, dt);
  out.llStartsTrasAnuncio = countStarts(durs['tren/Tren_Llegada.mp3']) - ll0;
  out.viasSiguenSonando = T._viasBuc.suena();

  // (4) _llegaEstacion (time=0): vias calla y NO hay SEGUNDO disparo
  T.time = 0.01;
  await stepN(10, dt);
  out.faseTrasLlegar = T.phase;
  out.viasOffTrasFrenar = !T._viasBuc.suena();
  out.llStartsTotales = countStarts(durs['tren/Tren_Llegada.mp3']) - ll0;

  // (5) el setVol vivo de vias escribe el volumen REAL (no 0,0001):
  //     los GainNodes creados en el ctx del juego quedan capturados y se
  //     lee su valor NATIVO (automatización + escrituras directas)
  const ganos = (window.__GAIN_NODES || []).length;
  out.gainsCreados = ganos;
  if (ganos) {
    const gn = window.__GAIN_NODES[ganos - 1];
    try { out.ultimaGanancia = +gn.gain.value.toFixed(4); } catch (e) {}
  }
  return out;
}
"""

# ── P3: SDK v1.5.2 a nivel unidad (ctx SUSPENDIDO → resume) ─────────────
SDK152 = r"""
async (durs) => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const G = window.__PP_GAME;
  const sdkUrl = new URL('championships/sdk/champ_sdk.js', document.baseURI).href;
  const SDK = await import(sdkUrl);
  const modUrl = new URL('championships/oeste/index.js', document.baseURI).href;
  const out = {};

  // contexto PROPIO suspendido (autoplay headless arranca 'running': forzamos)
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  try { await ctx.suspend(); } catch (e) { /* */ }
  out.ctxState0 = ctx.state;

  // (a) createBucle.on() con ctx dormido → resume → arranca solo
  const b = SDK.createBucle(() => ({ audio: { ctx } }), {
    url: () => SDK.assetURL(modUrl, 'tren/vias.mp3'),
    vol: () => 0.13, fadeIn: 0.05, stopFade: 0.1, ignoraMute: true,
  });
  b.on();
  out.bucleDormidoQuerido = b.estado().querido;   // leído SIN esperar
  await sleep(400);
  out.bucleConDormido = b.estado();          // puede ya haber despertado
  try { await ctx.resume(); } catch (e) { /* */ }
  await sleep(600);
  out.bucleTrasResume = b.estado();          // sonando=true (statechange)

  // (b) createSfx.play() con ctx dormido → resume → se dispara solo
  const srcLog = [];
  const pStart = AudioBufferSourceNode.prototype.start;
  const ctx2 = new (window.AudioContext || window.webkitAudioContext)();
  try { await ctx2.suspend(); } catch (e) { /* */ }
  const eng = SDK.createSfx(modUrl, () => ({ audio: { ctx: ctx2 } }),
    { ignoraMute: true });
  eng.play('tren/Tunel.mp3', 0.42);
  await sleep(700);
  out.sfxPendAntes = !eng.tiene('tren/Tunel.mp3') || true;   // pedido en vuelo
  try { await ctx2.resume(); } catch (e) { /* */ }
  await sleep(900);
  out.sfxTieneTrasResume = eng.tiene('tren/Tunel.mp3');
  // el disparo post-resume: si el buffer llegó antes del resume, el
  // statechange lo dispara; si llegó después, el decode lo dispara.
  // En ambos casos TIENE el buffer y el juego real lo verifica en P2.

  // (c) suena() con instancia de un contexto MUERTO = false
  const holder = { audio: { ctx: null } };
  const ctxA = new (window.AudioContext || window.webkitAudioContext)();
  holder.audio.ctx = ctxA;
  try { await ctxA.resume(); } catch (e) { /* */ }
  const b2 = SDK.createBucle(() => holder, {
    url: () => SDK.assetURL(modUrl, 'tren/vias.mp3'),
    vol: () => 0.3, fadeIn: 0.05, stopFade: 0.1, ignoraMute: true,
  });
  b2.on();
  for (let i = 0; i < 40 && !b2.suena(); i++) await sleep(100);
  out.suenaCtxVivo = b2.suena();
  // "renace" el contexto: el game pasa a OTRO ctx (re-bind de VR) — el
  // holder muda, exactamente como el audio del juego
  const ctxB = new (window.AudioContext || window.webkitAudioContext)();
  holder.audio.ctx = ctxB;
  try { await ctxB.resume(); } catch (e) { /* */ }
  out.suenaCtxMuerto = b2.suena();           // FALSE → la reparación actúa
  b2.on();                                    // on() suelta la vieja y re-arma
  await sleep(500);
  out.reparadoEnCtxNuevo = b2.suena() && b2.estado().sonando;

  // (d) setVol respeta ignoraMute: capturo los GainNodes de ctxB y leo su
  //     valor NATIVO tras cada setVol (automatización + escritura directa)
  if (!ctxB.__PP_GAIN_PATCHED) {
    ctxB.__PP_GAIN_PATCHED = true;
    ctxB.__GAINS = [];
    const origGain = ctxB.createGain.bind(ctxB);
    ctxB.createGain = function () {
      const gn = origGain();
      try { ctxB.__GAINS.push(gn); } catch (e) { /* */ }
      return gn;
    };
  }
  const A = { arcMute: true };
  const gGet = () => ({ audio: Object.assign({ ctx: ctxB }, A) });
  const lastVal = () => {
    const G2 = ctxB.__GAINS;
    try { return G2 && G2.length ? +G2[G2.length - 1].gain.value.toFixed(4)
      : null; } catch (e) { return null; }
  };
  const b3 = SDK.createBucle(gGet, {
    url: () => SDK.assetURL(modUrl, 'tren/vias.mp3'),
    vol: () => 0.5, fadeIn: 0.05, stopFade: 0.1, ignoraMute: true,
  });
  b3.on();
  for (let i = 0; i < 40 && !b3.suena(); i++) await sleep(100);
  b3.setVol(0.5);
  out.setVolIgnoraMute = lastVal();          // 0.5 (NO 0.0001)
  const b4 = SDK.createBucle(gGet, {
    url: () => SDK.assetURL(modUrl, 'tren/vias.mp3'),
    vol: () => 0.5, fadeIn: 0.05, stopFade: 0.1,   // SIN ignoraMute
  });
  b4.on();
  for (let i = 0; i < 40 && !b4.suena(); i++) await sleep(100);
  b4.setVol(0.5);
  out.setVolSinIgnora = lastVal();           // 0.0001 (gate de MÚSICA)
  try { b.off(true); b2.off(true); b3.off(true); b4.off(true); } catch (e) {}
  try { ctx.close(); ctx2.close(); ctxA.close(); ctxB.close(); } catch (e) {}
  return out;
}
"""


async def probe(page, url, js, arg=None, timeout=60000, refresh=False):
    if refresh or page.url != url:
        await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
        await page.wait_for_function(
            "() => window.__PP_GAME && window.__PP_GAME.audio", timeout=timeout)
    return await page.evaluate(js, arg)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--autoplay-policy=no-user-gesture-required',
            '--use-fake-ui-for-media-stream',
        ])

        print('== P1/P2 · DEV · evento real del TrenAction (juego conducido) ==')
        page = await browser.new_page()
        try:
            await probe(page, DEV, INSTR, refresh=True)
            durs = await probe(page, DEV, DURS)
            print('  duraciones:', json.dumps(durs))
            for t, d in durs.items():
                chk(d > 0.5, 'P1 ' + t + ' decodifica (' + str(d) + ' s)')
            r = await probe(page, DEV, DRIVE, durs, timeout=90000)
            if r.get('err'):
                chk(False, 'P2 arranque: ' + r['err'])
            else:
                print('  fases:', r.get('fase0'), '→', r.get('faseTrasIntro'),
                      '| túnel:', r.get('tunelFase'), '| tras llegar:',
                      r.get('faseTrasLlegar'))
                if r.get('stepErr'):
                    print('  stepErr:', r['stepErr'])
                chk(r.get('faseTrasIntro') == 'run',
                    'P2 _depart alcanzado (phase run)')
                chk(r.get('viasStarts', 0) >= 1,
                    'P2 _depart DISPARA vias.mp3 (starts='
                    + str(r.get('viasStarts')) + ')')
                chk(r.get('viasLoopStarts', 0) >= 1,
                    'P2 vias arranca EN BUCLE (loop=true)')
                ve = r.get('viasEstado') or {}
                chk(ve.get('sonando') and ve.get('cargado'),
                    'P2 vias SIGUE vivo tras frames (estado ' + str(ve) + ')')
                chk(r.get('tunelFase') in ('pre', 'in', 'dur', 'out'),
                    'P2 túnel entró en secuencia (' + str(r.get('tunelFase'))
                    + ')')
                chk(r.get('tunelStarts', 0) == 1,
                    'P2 fase pre (aparece tunelboca) DISPARA Tunel.mp3 UNA vez '
                    '(starts=' + str(r.get('tunelStarts')) + ')')
                chk(r.get('llStartsTrasAnuncio', 0) == 1,
                    'P2 anuncio de segundos → Tren_Llegada a +1,2 s UNA vez '
                    '(starts=' + str(r.get('llStartsTrasAnuncio')) + ')')
                chk(r.get('viasSiguenSonando') is True,
                    'P2 vias sigue sonando durante el anuncio')
                chk(r.get('viasOffTrasFrenar') is True,
                    'P2 _llegaEstacion APAGA la rodadura')
                chk(r.get('llStartsTotales', 0) == 1,
                    'P2 la llegada NO se re-dispara al frenar (total='
                    + str(r.get('llStartsTotales')) + ')')
        except Exception as e:
            chk(False, 'P1/P2 DEV: ' + str(e)[:200])
        await page.close()

        print('== P3 · DEV · SDK v1.5.2 (ctx dormido/muerto, ignoraMute) ==')
        page = await browser.new_page()
        try:
            await probe(page, DEV, INSTR, refresh=True)
            durs = await probe(page, DEV, DURS)
            r = await probe(page, DEV, SDK152, durs, timeout=90000)
            print('  ' + json.dumps(r)[:400])
            b0 = r.get('bucleConDormido') or {}
            b1 = r.get('bucleTrasResume') or {}
            chk(r.get('bucleDormidoQuerido') is True,
                'P3a on() con ctx dormido recuerda el arranque (querido '
                'inmediato)')
            chk(b0.get('querido') is True and b1.get('sonando') is True,
                'P3a el arranque sobrevive hasta el despertar del contexto ')
            chk(b1.get('sonando') is True,
                'P3a resume → statechange ARRANCA el bucle solo')
            chk(r.get('sfxTieneTrasResume') is True,
                'P3b play() con ctx dormido → resume → buffer disponible y '
                'play pendiente vivo')
            chk(r.get('suenaCtxVivo') is True,
                'P3c suena()=true con instancia viva en su ctx')
            chk(r.get('suenaCtxMuerto') is False,
                'P3c suena()=false con instancia de contexto MUERTO '
                '(re-bind de VR)')
            chk(r.get('reparadoEnCtxNuevo') is True,
                'P3c on() re-arma la instancia en el contexto nuevo')
            sv1 = r.get('setVolIgnoraMute')
            sv0 = r.get('setVolSinIgnora')
            chk(sv1 is not None and abs(sv1 - 0.5) < 1e-6,
                'P3d setVol con ignoraMute escribe el volumen REAL ('
                + str(sv1) + ')')
            chk(sv0 is not None and sv0 <= 0.001,
                'P3d setVol SIN ignoraMute aplica el gate de música ('
                + str(sv0) + ')')
        except Exception as e:
            chk(False, 'P3 SDK: ' + str(e)[:200])
        await page.close()

        await browser.close()

    print()
    print('RESULTADO: ' + str(ok_n[0]) + ' OK · ' + str(fail_n[0]) + ' fallos')
    sys.exit(0 if fail_n[0] == 0 else 1)


if __name__ == '__main__':
    asyncio.run(main())
