#!/usr/bin/env python3
"""QA RUNTIME v3.6.25 del audio del vagón — el informe del dueño tras
V3.6.24: «los caballos no se amortiguan ni desaparecen cuando los jinetes
no están, se alejan o mueren (antes sí) · vias.mp3 casi imperceptible ·
tunel y llegada no suenan NUNCA».

Arnés sobre el JUEGO REAL (dev) + SDK a nivel unidad:

  P1 · duración de los 4 mp3 (identificación de disparos por buffer).
  P2 · CICLO DE VIDA DEL GALOPE (juego conducido, eventos reales):
       forajido spawn → pool[0] SUENA con fade por distancia (gain real) ·
       _fjHerido() → el galope calla SECO y NO REVIVE en herido/fade
       (regresión v3.6.23: la auto-reparación revivía el bucle cada frame
       tras el off(true) — «no desaparece cuando mueren») · _fjGone →
       silencio estable · indios: _indHerido(rec) → SU motor calla y no
       revive · vias con nivel AUDIBLE (gain ≈ 0,30, no 0,13) · one-shots
       del juego POR EL MOTOR DEL GALOPE (v3.6.26): Tunel al BAJAR LA LUZ
       ('pre'→'in', 1 vez) y Tren_Llegada CONCATENADA con la voz (1 vez,
       al caer la locución real _voiceDur + 0,35).
  P3 · SDK v1.5.4 a nivel unidad:
       (a) play() devuelve BOOLEANO (true sólo si src.start() disparó) —
           el contrato que _pistaTrenStep necesita para no dar un disparo
           por perdido.
       (b) el pend del mismo nombre se CONSUME al arrancar de verdad
           (cero dobles disparos si el contexto rebota después).
       (c) on() MATA (stop+disconnect) la instancia huérfana de un ctx
           viejo en lugar de soltarla viva (el galope fantasma eterno).
       (d) heredados v1.5.2: on()/play() con ctx dormido despiertan por
           statechange; suena() honesta con ctx muerto; setVol respeta
           ignoraMute.

Uso: python3 scripts/qa_tren_audio_rt_v3626.py
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


# ── instrumentación: starts de AudioBufferSource + stops + GainNodes ────
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
  window.__STOP_N = 0;
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
    const pStop = AudioBufferSourceNode.prototype.stop;
    AudioBufferSourceNode.prototype.stop = function (...a) {
      try { window.__STOP_N++; } catch (e) { /* */ }
      return pStop.apply(this, a);
    };
  }
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

# ── P2: ciclo de vida del galope + vias + one-shots, sobre el juego ─────
DRIVE = r"""
async (durs) => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const G = window.__PP_GAME;
  const ctx = G.audio.ctx;
  try { await ctx.resume(); } catch (e) { /* */ }
  if (!window.__PP_OESTE) {
    try { await G.champs.preload('oeste'); } catch (e) { /* */ }
  }
  for (let i = 0; i < 80 && !(window.__PP_OESTE && window.__PP_OESTE.ctrl);
       i++) await sleep(100);
  const CTRL = window.__PP_OESTE && window.__PP_OESTE.ctrl();
  if (!CTRL) return { err: 'sin CTRL' };

  G.champs.activeId = 'oeste';
  CTRL.active = true;
  if (!CTRL.fx) {
    CTRL.fx = { flash() {}, spark() {}, smoke() {}, smokeGun() {},
      smokeCurtain() {}, scorch() {}, beam() {}, mecha() {}, texDot() {},
      texPuff() {}, laserUpdate() {}, laserVisible() {}, update() {} };
  }
  CTRL._instrK = 'tren';
  CTRL._startTren();
  const T = CTRL._tren;
  if (!T) return { err: 'sin TrenAction (cartel no bypassed)' };

  const out = {};
  const near = (a, b, tol) => Math.abs(a - b) <= tol;
  const countStarts = (dur) => window.__SRC_LOG.filter(
    (s) => near(s.dur, dur, 0.06)).length;
  const dt = 1 / 60;
  const stepN = async (n) => {
    for (let i = 0; i < n; i++) {
      try { T.step(dt); T.fxStep(dt); } catch (e) {
        if (!out.stepErr) out.stepErr = String(e).slice(0, 140);
      }
      if (i % 12 === 11) await sleep(0);
    }
  };
  const galGains = () => {
    try {
      const arr = window.__GAIN_NODES;
      return arr.length ? arr[arr.length - 1].gain.value : null;
    } catch (e) { return null; }
  };

  // INTRO → _depart (run) y vias en bucle
  for (let i = 0; i < 60 * 12 && T.phase === 'intro'; i++) {
    try { T.step(dt); T.fxStep(dt); } catch (e) {
      if (!out.stepErr) out.stepErr = String(e).slice(0, 140);
      break;
    }
    if (i % 12 === 11) await sleep(0);
  }
  out.faseRun = T.phase;
  for (let i = 0; i < 160 && !T._viasBuc.suena(); i++) {
    try { T.step(dt); T.fxStep(dt); } catch (e) { /* */ }
    await sleep(50);
  }
  out.viasViva = T._viasBuc.suena();
  await stepN(20);
  // nivel REAL de la rodadura (setVol por frame escribe en UN gain 0,30)
  out.viasNivel = (() => {
    for (const gn of window.__GAIN_NODES) {
      try { const v = gn.gain.value; if (v > 0.05 && v < 1) return +v.toFixed(4); }
      catch (e) { /* */ }
    }
    return null;
  })();

  // ── GALOPE DEL FORAJIDO: nace, se oye, MUERE y no resucita ──────────
  T._tunnelT = 99999;                    // sin túnel durante la prueba
  T._indCount = 0; T._indNext = 99999;   // agenda de indios dormida
  T._fjCount = 0; T._fjNext = 0.02;      // forajido AHORA
  const g0 = window.__GAIN_NODES.length;
  let esperado = 300;
  while (esperado-- > 0 && T._fjState === 'off') {
    T.step(dt); T.fxStep(dt);
    if (esperado % 12 === 11) await sleep(0);
  }
  out.fjEstado = T._fjState;
  for (let i = 0; i < 200 && !T.__galPool[0].suena(); i++) {
    T.step(dt); T.fxStep(dt); await sleep(30);
  }
  out.galSuenaVivo = T.__galPool[0].suena();
  // el spawn puede caer en 'paso' (cruza sin pararse): lo encauzo a 'ida'
  // para que LLEGUE a la ventana y podamos medir llegada→fuga
  if (T._fjState === 'paso') { T._fjState = 'ida'; T._fjT = 0; }
  for (let i = 0; i < 600 && T._fjState !== 'ventana'; i++) {
    T.step(dt); T.fxStep(dt);
    if (i % 12 === 11) await sleep(0);
  }
  await stepN(45);                       // fadeIn 0,25 s + asentamiento
  out.fjEstadoVentana = T._fjState;
  // el gain del galope: el ÚNICO GainNode creado desde el spawn (g0)
  const galGain = () => {
    try {
      const ggs = window.__GAIN_NODES.slice(g0);
      return ggs.length ? +ggs[ggs.length - 1].gain.value.toFixed(4) : null;
    } catch (e) { return null; }
  };
  out.galGainVentana = galGain();
  T._fjFuga();                           // se ALEJA galopando
  await stepN(90);                       // 1,5 s alejándose
  out.fjEstadoFuga = T._fjState;
  out.galGainFuga = galGain();

  // MUERTE: _fjHerido → off SECO. La regresión: la reparación lo revivía
  const cab0 = countStarts(durs['tren/caballos.mp3']);
  T._fjHerido();
  await stepN(6);                        // 0,1 s
  out.galSuenaTrasBala = T.__galPool[0].suena();   // true = REVIVE (bug)
  await stepN(114);                      // herido 1 s + fade ≈ 1 s
  out.galEstadoMuerto = T._fjState;
  out.galStartsTrasMuerte = countStarts(durs['tren/caballos.mp3']) - cab0;
  out.galSuenaMuerto = T.__galPool[0].suena();
  await stepN(90);                       // _fjGone + margen
  out.galStartsTrasGone = countStarts(durs['tren/caballos.mp3']) - cab0;
  out.galSuenaGone = T.__galPool[0].suena();

  // ── INDIOS: grupo → balear UNO → SU motor calla y no revive ─────────
  T._indNext = 0.02;
  let esp2 = 300;
  while (esp2-- > 0 && !T._inds.length) {
    T.step(dt); T.fxStep(dt);
    if (esp2 % 12 === 11) await sleep(0);
  }
  out.indGrupo = T._inds.length;
  const rec0 = T._inds[0];
  for (let i = 0; i < 200 && !(rec0.galK && T.__galPool[rec0.galK] &&
       T.__galPool[rec0.galK].suena()); i++) {
    T.step(dt); T.fxStep(dt); await sleep(30);
  }
  out.indGalSuena = rec0.galK ? T.__galPool[rec0.galK].suena() : null;
  const cab1 = countStarts(durs['tren/caballos.mp3']);
  T._indHerido(rec0);
  await stepN(120);
  out.indSuenaTrasBala = rec0.galK ? T.__galPool[rec0.galK].suena() : null;
  out.indStartsTrasBala = countStarts(durs['tren/caballos.mp3']) - cab1;

  // ── ONE-SHOTS del juego POR EL MOTOR DEL GALOPE (v3.6.26): túnel AL
  // BAJAR LA LUZ ('pre'→'in') y llegada CONCATENADA con la voz ─────────
  T._indGoneAll(); T._galCorta();
  T._tunnelT = 0.02;
  T.time = 90;                       // lejos del anuncio (bloquea=30)
  const tu0 = countStarts(durs['tren/Tunel.mp3']);
  // nace 'pre' y avanza POR DISTANCIA hasta que el borde trasero de la
  // boca pasa el ojo: la luz EMPIEZA a caer y AHÍ dispara el mp3
  let espIn = 2000;
  while (espIn-- > 0 && T._tunnelPhase !== 'in') {
    T.step(dt); T.fxStep(dt);
    if (espIn % 24 === 23) await sleep(0);
  }
  out.faseIn = T._tunnelPhase;
  await stepN(30);
  await sleep(700);
  await stepN(30);
  out.tunelStarts = countStarts(durs['tren/Tunel.mp3']) - tu0;
  T.time = 30.4;
  const ll0 = countStarts(durs['tren/Tren_Llegada.mp3']);
  // el silbato entra AL CAER la locución real (_voiceDur + 0,35): margen
  // generoso para la voz entera + el disparo del motor del galope
  await stepN(360);
  await sleep(400);
  await stepN(20);
  out.llStarts = countStarts(durs['tren/Tren_Llegada.mp3']) - ll0;
  return out;
}
"""

# ── P3: SDK a nivel unidad (contrato play() booleano, pend, huérfanos) ──
SDK154 = r"""
async (durs) => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const G = window.__PP_GAME;
  const sdkUrl = new URL('championships/sdk/champ_sdk.js', document.baseURI).href;
  const SDK = await import(sdkUrl);
  const modUrl = new URL('championships/oeste/index.js', document.baseURI).href;
  const out = {};
  const cabDur = durs['tren/caballos.mp3'];

  // (a) CAMINO POR DEFECTO (llamantes de un solo disparo): play() sin
  //     buffer → false, y el PEND auto-dispara UNA vez al aterrizar el
  //     decode; un rebote del ctx NO re-dispara (pend consumido).
  const ctx1 = new (window.AudioContext || window.webkitAudioContext)();
  try { await ctx1.resume(); } catch (e) { /* */ }
  const eng = SDK.createSfx(modUrl, () => ({ audio: { ctx: ctx1 } }),
    { ignoraMute: true });
  const name = 'tren/caballos.mp3';
  const nCab = () => window.__SRC_LOG.filter(
    (s) => Math.abs(s.dur - cabDur) < 0.06).length;
  out.playSinBuffer = eng.play(name, 0.5);       // false (pend encolado)
  for (let i = 0; i < 100 && !eng.tiene(name); i++) await sleep(60);
  await sleep(200);                              // margen del auto-disparo
  out.pendAutoDispara = nCab();                  // EXACTAMENTE 1
  const nAntesRebote = nCab();
  try { await ctx1.suspend(); } catch (e) { /* */ }
  await sleep(120);
  try { await ctx1.resume(); } catch (e) { /* */ }
  await sleep(400);
  out.reboteNuevos = nCab() - nAntesRebote;      // 0 (pend consumido)

  // (b) CAMINO sinPend (el del módulo, _pistaTrenStep): NUNCA auto-
  //     dispara; el reintento del módulo gobierna con el booleano.
  const ctxS = new (window.AudioContext || window.webkitAudioContext)();
  try { await ctxS.resume(); } catch (e) { /* */ }
  const eng2 = SDK.createSfx(modUrl, () => ({ audio: { ctx: ctxS } }),
    { ignoraMute: true });
  const name2 = 'tren/Tunel.mp3';
  const dur2 = durs['tren/Tunel.mp3'];
  const nTu = () => window.__SRC_LOG.filter(
    (s) => Math.abs(s.dur - dur2) < 0.06).length;
  const base2 = nTu();
  out.spSinBuffer = eng2.play(name2, 0.42, { sinPend: true });  // false
  for (let i = 0; i < 100 && !eng2.tiene(name2); i++) await sleep(60);
  await sleep(250);                              // nada debe auto-disparar
  out.spAutoDisparos = nTu() - base2;            // EXACTAMENTE 0
  out.spConBuffer = eng2.play(name2, 0.42, { sinPend: true });  // true
  out.spStarts = nTu() - base2;                  // EXACTAMENTE 1

  // (c) createBucle.on() MATA la instancia huérfana del ctx viejo
  const holder = { audio: { ctx: null } };
  const ctxA = new (window.AudioContext || window.webkitAudioContext)();
  holder.audio.ctx = ctxA;
  try { await ctxA.resume(); } catch (e) { /* */ }
  const b = SDK.createBucle(() => holder, {
    url: () => SDK.assetURL(modUrl, 'tren/caballos.mp3'),
    vol: () => 0.45, fadeIn: 0.05, stopFade: 0.1, ignoraMute: true,
  });
  b.on();
  for (let i = 0; i < 100 && !b.suena(); i++) await sleep(60);
  const stops0 = window.__STOP_N;
  const ctxB = new (window.AudioContext || window.webkitAudioContext)();
  holder.audio.ctx = ctxB;
  try { await ctxB.resume(); } catch (e) { /* */ }
  out.suenaCtxMuerto = b.suena();
  b.on();                                        // suelta la vieja → MATA
  await sleep(80);
  out.paróHuérfana = window.__STOP_N > stops0;
  await sleep(400);
  out.reparadoEnNuevo = b.suena();

  // (d) heredado: on() dormido despierta por statechange
  const ctx2 = new (window.AudioContext || window.webkitAudioContext)();
  try { await ctx2.suspend(); } catch (e) { /* */ }
  const b2 = SDK.createBucle(() => ({ audio: { ctx: ctx2 } }), {
    url: () => SDK.assetURL(modUrl, 'tren/vias.mp3'),
    vol: () => 0.3, fadeIn: 0.05, stopFade: 0.1, ignoraMute: true,
  });
  b2.on();
  await sleep(400);
  try { await ctx2.resume(); } catch (e) { /* */ }
  await sleep(700);
  out.dormidoDespierta = b2.suena();

  // (e) heredado: setVol respeta ignoraMute
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
  const lastVal = () => {
    try {
      const A2 = ctxB.__GAINS;
      return A2 && A2.length ? +A2[A2.length - 1].gain.value.toFixed(4) : null;
    } catch (e) { return null; }
  };
  const gGet = () => ({ audio: { ctx: ctxB, arcMute: true } });
  const b3 = SDK.createBucle(gGet, {
    url: () => SDK.assetURL(modUrl, 'tren/caballos.mp3'),
    vol: () => 0.5, fadeIn: 0.05, stopFade: 0.1, ignoraMute: true,
  });
  b3.on();
  for (let i = 0; i < 100 && !b3.suena(); i++) await sleep(60);
  b3.setVol(0.5);
  out.setVolIgnora = lastVal();

  // (f) v1.5.4 · precarga(): decodifica SIN sonar (cero src.start)
  const ctxP = new (window.AudioContext || window.webkitAudioContext)();
  try { await ctxP.resume(); } catch (e) { /* */ }
  const b4 = SDK.createBucle(() => ({ audio: { ctx: ctxP } }), {
    url: () => SDK.assetURL(modUrl, 'tren/Tunel.mp3'), ignoraMute: true,
  });
  const nP0 = window.__SRC_LOG.length;
  b4.precarga();
  for (let i = 0; i < 100 && !b4.estado().cargado; i++) await sleep(60);
  out.precCargado = b4.estado().cargado;
  out.precSonando = b4.estado().sonando;
  out.precStarts = window.__SRC_LOG.length - nP0;

  try { b.off(true); b2.off(true); b3.off(true); b4.off(true); } catch (e) { /* */ }
  try { ctx1.close(); ctx2.close(); ctxA.close(); ctxB.close(); ctxP.close(); } catch (e) {}
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

        print('== P1/P2 · DEV · ciclo de vida del galope (juego real) ==')
        page = await browser.new_page()
        try:
            await probe(page, DEV, INSTR, refresh=True)
            durs = await probe(page, DEV, DURS)
            for t, d in durs.items():
                chk(d > 0.5, 'P1 ' + t + ' decodifica (' + str(d) + ' s)')
            r = await probe(page, DEV, DRIVE, durs, timeout=120000)
            if r.get('err'):
                chk(False, 'P2 arranque: ' + r['err'])
            else:
                print('  fjEstado:', r.get('fjEstado'), '| pasos z:',
                      r.get('galZ0'), '→', r.get('galZ1'), '| stepErr:',
                      r.get('stepErr'))
                chk(r.get('faseRun') == 'run', 'P2 _depart (phase run)')
                chk(r.get('viasViva') is True, 'P2 vias viva en marcha')
                vn = r.get('viasNivel')
                chk(vn is not None and vn >= 0.28,
                    'P2 rodadura con nivel AUDIBLE (gain ' + str(vn)
                    + ' ≥ 0,28)')
                chk(r.get('galSuenaVivo') is True,
                    'P2 galope del forajido VIVO suena')
                gv = r.get('galGainVentana')
                gf = r.get('galGainFuga')
                chk(gv is not None and gv >= 0.4,
                    'P2 galope a la ventana con cuerpo (gain ' + str(gv)
                    + ' ≥ 0,4)')
                chk(gv is not None and gf is not None and gf < gv - 0.1,
                    'P2 el galope SE AMORTIGUA al alejarse en fuga ('
                    + str(gv) + ' → ' + str(gf) + ')')
                chk(r.get('galSuenaTrasBala') is False,
                    'P2 BALAZO: el galope calla SECO (no revive en herido)')
                chk(r.get('galStartsTrasMuerte', 1) == 0,
                    'P2 CERO disparos nuevos de galope tras la muerte ('
                    + str(r.get('galStartsTrasMuerte')) + ')')
                chk(r.get('galSuenaMuerto') is False,
                    'P2 galope sigue muerto tras herido+fade')
                chk(r.get('galSuenaGone') is False,
                    'P2 galope muerto tras _fjGone')
                chk(r.get('galStartsTrasGone', 1) == 0,
                    'P2 CERO disparos tras gone ('
                    + str(r.get('galStartsTrasGone')) + ')')
                chk(r.get('indGalSuena') is True,
                    'P2 galope del indio suena')
                chk(r.get('indSuenaTrasBala') is False,
                    'P2 indio abatido: SU caballo calla y no revive')
                chk(r.get('indStartsTrasBala', 1) == 0,
                    'P2 CERO disparos del galope del indio tras la bala ('
                    + str(r.get('indStartsTrasBala')) + ')')
                chk(r.get('faseIn') == 'in',
                    "P2 el túnel llegó a 'in' (la luz cayó)")
                chk(r.get('tunelStarts', 0) == 1,
                    'P2 SE BAJA LA LUZ (pre→in) → Tunel UNA vez ('
                    + str(r.get('tunelStarts')) + ')')
                chk(r.get('llStarts', 0) == 1,
                    'P2 voz terminada (_voiceDur+0,35) → Tren_Llegada UNA vez, concatenada ('
                    + str(r.get('llStarts')) + ')')
        except Exception as e:
            chk(False, 'P1/P2 DEV: ' + str(e)[:200])
        await page.close()

        print('== P3 · DEV · SDK contrato v1.5.4 ==')
        page = await browser.new_page()
        try:
            await probe(page, DEV, INSTR, refresh=True)
            durs = await probe(page, DEV, DURS)
            r = await probe(page, DEV, SDK154, durs, timeout=90000)
            print('  ' + json.dumps(r)[:420])
            chk(r.get('playSinBuffer') is False,
                'P3a play() sin buffer devuelve FALSE (el pend queda encolado)')
            chk(r.get('pendAutoDispara') == 1,
                'P3a el pend auto-dispara UNA vez al aterrizar el decode ('
                + str(r.get('pendAutoDispara')) + ')')
            chk(r.get('reboteNuevos') == 0,
                'P3a rebote suspend/resume NO re-dispara (pend consumido; '
                'nuevos=' + str(r.get('reboteNuevos')) + ')')
            chk(r.get('spSinBuffer') is False,
                'P3b sinPend sin buffer devuelve FALSE y NO encola pend')
            chk(r.get('spAutoDisparos') == 0,
                'P3b sinPend NUNCA auto-dispara (auto='
                + str(r.get('spAutoDisparos')) + ')')
            chk(r.get('spConBuffer') is True,
                'P3b sinPend con buffer y ctx vivo devuelve TRUE')
            chk(r.get('spStarts') == 1,
                'P3b el disparo del módulo suena UNA vez ('
                + str(r.get('spStarts')) + ')')
            chk(r.get('suenaCtxMuerto') is False,
                'P3c suena()=false con instancia de ctx muerto')
            chk(r.get('paróHuérfana') is True,
                'P3c on() MATA la instancia huérfana (stop del src viejo)')
            chk(r.get('reparadoEnNuevo') is True,
                'P3c la reparación arma el bucle en el ctx nuevo')
            chk(r.get('dormidoDespierta') is True,
                'P3d on() con ctx dormido despierta por statechange')
            sv = r.get('setVolIgnora')
            chk(sv is not None and abs(sv - 0.5) < 1e-6,
                'P3e setVol con ignoraMute escribe el volumen real ('
                + str(sv) + ')')
            chk(r.get('precCargado') is True,
                'P3f precarga() deja el buf CARGADO (v1.5.4)')
            chk(r.get('precSonando') is False,
                'P3f precarga() NO suena (sólo decodifica)')
            chk(r.get('precStarts') == 0,
                'P3f precarga() dispara CERO src.start (starts='
                + str(r.get('precStarts')) + ')')
        except Exception as e:
            chk(False, 'P3 SDK: ' + str(e)[:200])
        await page.close()

        await browser.close()

    print()
    print('RESULTADO: ' + str(ok_n[0]) + ' OK · ' + str(fail_n[0]) + ' fallos')
    sys.exit(0 if fail_n[0] == 0 else 1)


if __name__ == '__main__':
    asyncio.run(main())
