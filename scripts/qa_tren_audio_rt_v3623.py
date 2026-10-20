#!/usr/bin/env python3
"""QA RUNTIME del audio del vagón (v3.6.23) — por qué NO se oye el tren.

El dueño reporta: ni rodadura, ni llegadas, ni túneles se oyen; los
sintéticos de los jinetes SÍ. Los sintéticos (playOsc/playNoise) no pasan
por fetch/decode ni por el gate arcMute/_arcDucked; los 4 mp3 nuevos sí.
Este arnés mide la cadena COMPLETA en el juego real (no estática):

  P1 · ctx del juego: existe, estado antes/después de resume(), sampleRate.
  P2 · los 4 mp3 del tren: fetch HTTP → bytes → decodeAudioData → duración.
  P3 · AUDIBILIDAD REAL: src→gain→analyser→destination sobre EL ctx del
       juego; pico medido en el analizador (la cadena del juego suena).
  P4 · MOTORES SDK reales (import del champ_sdk): createBucle con los opts
       EXACTOS de TrenAction para vias → estado() tras on(); createSfx sin
       precarga → tiene() antes/después (ventana de silencio del 1er play).
  P5 · GATE DEL MUTE: con audio.arcMute=true, objetivo() del SDK cae a
       0,0001 → el bucle «suena» (estado sonando) pero INAUDIBLE — el
       mecanismo exacto que explica el informe (los sintéticos ignoran
       arcMute; por eso esos sí se oyen).
  P6 · PRODUCCIÓN: versión servida, los 4 mp3 (fetch+decode) y las agujas
       del cableado dentro del index.js SERVIDO.

Uso: python3 scripts/qa_tren_audio_rt_v3623.py
Salida: RESULTADO: N OK · N fallos · exit 0/1.
"""
import asyncio
import sys

from playwright.async_api import async_playwright

DEV = 'http://localhost:3000/game.html'
PROD = 'https://franjavierdavila.github.io/CrazyPP/game.html'
ok_n = [0]
fail_n = [0]


def chk(cond, label):
    if cond:
        ok_n[0] += 1
        print('  ✓ ' + label)
    else:
        fail_n[0] += 1
        print('  ✗ FALLO: ' + label)


# ── P1+P2+P3: contexto, fetch/decode y audibilidad de los 4 mp3 ─────────
CADENA = r"""
async () => {
  const G = window.__PP_GAME;
  const A = G.audio;
  if (!A) return { err: 'sin audio' };
  let ctx = A.ctx;                      // en el casco nace al 1er gesto
  if (!ctx) { ctx = new (window.AudioContext || window.webkitAudioContext)();
    try { A.ctx = ctx; } catch (e) { /* sonda: sólo lectura */ } }
  const out = { ctxPreexistente: !!G.audio.ctx && ctx === G.audio.ctx,
    state0: ctx.state, sr: ctx.sampleRate, arcMute: !!A.arcMute,
    arcDucked: !!A._arcDucked };
  try { await ctx.resume(); } catch (e) { /* headless */ }
  out.state1 = ctx.state;
  let modUrl = null;
  for (const r of performance.getEntriesByType('resource')) {
    if (r.name.includes('championships/oeste/index.js')) modUrl = r.name;
  }
  if (!modUrl) modUrl = new URL('championships/oeste/index.js', document.baseURI).href;
  out.modUrl = modUrl;
  out.tracks = [];
  for (const t of ['tren/vias.mp3', 'tren/Tren_Llegada.mp3', 'tren/Tunel.mp3',
                   'tren/caballos.mp3']) {
    const url = new URL('./assets/' + t, modUrl).href;
    const row = { t };
    try {
      const r = await fetch(url);
      row.http = r.status;
      const ab = await r.arrayBuffer();
      row.bytes = ab.byteLength;
      const buf = await ctx.decodeAudioData(ab.slice(0));
      row.dur = +buf.duration.toFixed(2);
      const src = ctx.createBufferSource(); src.buffer = buf;
      const gn = ctx.createGain(); gn.gain.value = 0.45;
      const an = ctx.createAnalyser(); an.fftSize = 1024;
      src.connect(gn); gn.connect(an); an.connect(ctx.destination);
      const data = new Float32Array(an.fftSize);
      src.start();
      let peak = 0;
      for (let i = 0; i < 12; i++) {
        await new Promise((res) => setTimeout(res, 20));
        an.getFloatTimeDomainData(data);
        for (let j = 0; j < data.length; j += 4) {
          const v = Math.abs(data[j]); if (v > peak) peak = v;
        }
      }
      try { src.stop(); } catch (e) { /* */ }
      try { gn.disconnect(); an.disconnect(); } catch (e) { /* */ }
      row.peak = +peak.toFixed(3);
      row.audible = peak > 0.01;
    } catch (e) { row.err = String(e).slice(0, 160); }
    out.tracks.push(row);
  }
  return out;
}
"""

# ── P4+P5: motores SDK reales + gate del mute ────────────────────────────
MOTORES = r"""
async () => {
  const G = window.__PP_GAME;
  const A = G.audio;
  if (!A.ctx) { A.ctx = new (window.AudioContext || window.webkitAudioContext)(); }
  const ctx = A.ctx;
  try { await ctx.resume(); } catch (e) { /* */ }
  const sdkUrl = new URL('championships/sdk/champ_sdk.js', document.baseURI).href;
  const SDK = await import(sdkUrl);
  const modUrl = new URL('championships/oeste/index.js', document.baseURI).href;
  const out = {};
  // bucle vias con los opts EXACTOS de TrenAction
  const b = SDK.createBucle(() => G, {
    url: () => SDK.assetURL(modUrl, 'tren/vias.mp3'),
    vol: () => 0.13, fadeIn: 0.6, stopFade: 0.9,
  });
  b.on();
  await new Promise((r) => setTimeout(r, 2500));
  out.vias = b.estado();
  // GATE DEL MUTE: objeto NUEVO con arcMute=true → objetivo() = 0,0001
  G.audio.arcMute = true;
  const b2 = SDK.createBucle(() => G, {
    url: () => SDK.assetURL(modUrl, 'tren/vias.mp3'),
    vol: () => 0.13, fadeIn: 0.05, stopFade: 0.1,
  });
  b2.on();
  await new Promise((r) => setTimeout(r, 1500));
  out.viasMute = b2.estado();
  // v1.5.1: con ignoraMute:true el mismo mute NO afecta (nace y suena)
  const b3 = SDK.createBucle(() => G, {
    url: () => SDK.assetURL(modUrl, 'tren/vias.mp3'),
    vol: () => 0.13, fadeIn: 0.05, stopFade: 0.1, ignoraMute: true,
  });
  b3.on();
  await new Promise((r) => setTimeout(r, 1200));
  out.viasIgnora = b3.estado();
  // createSfx con ignoraMute:true (el motor del TrenAction desde v3.6.23)
  const eng2 = SDK.createSfx(modUrl, () => G, { ignoraMute: true });
  eng2.play('tren/Tunel.mp3', 0.42);
  await new Promise((r) => setTimeout(r, 1200));
  out.sfxIgnoraTiene = eng2.tiene('tren/Tunel.mp3');
  G.audio.arcMute = false;
  try { b.off(true); b2.off(true); b3.off(true); } catch (e) { /* */ }
  // createSfx SIN precarga: el 1er play() no suena (aún decodificando)
  const eng = SDK.createSfx(modUrl, () => G);
  out.sfxTiene0 = eng.tiene('tren/Tunel.mp3');
  eng.play('tren/Tunel.mp3', 0.42);
  await new Promise((r) => setTimeout(r, 1500));
  out.sfxTiene1 = eng.tiene('tren/Tunel.mp3');
  return out;
}
"""

# ── P6: producción — versión, 4 mp3 y agujas del index.js servido ───────
PROD_CHK = r"""
async () => {
  const out = { ver: window.__PP_VERSION || null };
  const base = new URL('championships/oeste/', document.baseURI).href;
  const tracks = ['tren/vias.mp3', 'tren/Tren_Llegada.mp3', 'tren/Tunel.mp3',
                  'tren/caballos.mp3'];
  out.tracks = [];
  let ctx = null;
  try {
    const G = window.__PP_GAME;
    if (G && G.audio) {
      ctx = G.audio.ctx;
      if (!ctx) { ctx = new (window.AudioContext || window.webkitAudioContext)();
        try { G.audio.ctx = ctx; } catch (e) { /* */ } }
      try { await ctx.resume(); } catch (e) { /* */ }
    }
  } catch (e) { /* */ }
  for (const t of tracks) {
    const row = { t };
    try {
      const r = await fetch(base + 'assets/' + t);
      row.http = r.status;
      const ab = await r.arrayBuffer();
      row.bytes = ab.byteLength;
      if (ctx) {
        const buf = await ctx.decodeAudioData(ab.slice(0));
        row.dur = +buf.duration.toFixed(2);
      }
    } catch (e) { row.err = String(e).slice(0, 160); }
    out.tracks.push(row);
  }
  try {
    const r = await fetch(base + 'index.js');
    const txt = await r.text();
    out.idxBytes = txt.length;
    const agujas = ['tren/vias.mp3', 'tren/Tren_Llegada.mp3', 'tren/Tunel.mp3',
                    'tren/caballos.mp3', '_viasBuc', '_galBuc', 'createBucle'];
    out.agujas = {};
    for (const a of agujas) out.agujas[a] = txt.includes(a);
  } catch (e) { out.idxErr = String(e).slice(0, 160); }
  return out;
}
"""


async def probe(page, url, js, timeout=60000):
    await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
    await page.wait_for_function(
        "() => window.__PP_GAME && window.__PP_GAME.audio",
        timeout=timeout)
    return await page.evaluate(js)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--autoplay-policy=no-user-gesture-required',
            '--use-fake-ui-for-media-stream',
        ])

        print('== DEV · cadena completa (ctx + fetch/decode + AUDIBILIDAD) ==')
        page = await browser.new_page()
        try:
            r = await probe(page, DEV, CADENA)
            print('  ctx:', r.get('state0'), '→', r.get('state1'),
                  '| sr', r.get('sr'), '| arcMute', r.get('arcMute'),
                  '| ducked', r.get('arcDucked'))
            chk(r.get('state1') == 'running', 'ctx del juego RUNNING tras resume')
            for t in r.get('tracks', []):
                if t.get('err'):
                    chk(False, t['t'] + ' → ' + t['err'])
                    continue
                chk(t['http'] == 200, t['t'] + ' HTTP 200 (' + str(t['bytes']) + ' B)')
                chk(t.get('dur', 0) > 0.5,
                    t['t'] + ' decodifica (' + str(t['dur']) + ' s)')
                chk(t.get('audible'), t['t'] + ' AUDIBLE en la cadena del juego '
                    '(pico ' + str(t.get('peak')) + ')')
        except Exception as e:
            chk(False, 'DEV cadena: ' + str(e)[:160])
        await page.close()

        print('== DEV · motores SDK reales + gate del mute ==')
        page = await browser.new_page()
        try:
            r = await probe(page, DEV, MOTORES)
            v = r.get('vias', {})
            chk(v.get('cargado') and v.get('sonando'),
                'createBucle(vias) cargado+sonando tras on() ' + str(v))
            vm = r.get('viasMute', {})
            chk(vm.get('sonando'),
                'con arcMute=1 el bucle NACE (pero gain 0,0001 → INAUDIBLE) '
                + str(vm))
            vi = r.get('viasIgnora', {})
            chk(vi.get('sonando'),
                'v1.5.1 ignoraMute:true — con arcMute=1 el bucle SUENA '
                + str(vi))
            chk(r.get('sfxIgnoraTiene') is True,
                'createSfx ignoraMute:true sin crash y cachea')
            chk(r.get('sfxTiene0') is False and r.get('sfxTiene1') is True,
                'createSfx 1er play() sin buffer (silencio) y cachea tras decode')
        except Exception as e:
            chk(False, 'DEV motores: ' + str(e)[:160])
        await page.close()

        print('== PRODUCCIÓN · versión + 4 mp3 + agujas del index.js servido ==')
        page = await browser.new_page()
        try:
            r = await probe(page, PROD, PROD_CHK, timeout=75000)
            chk(bool(r.get('ver')), 'producción sirve __PP_VERSION='
                + str(r.get('ver')))
            for t in r.get('tracks', []):
                if t.get('err'):
                    chk(False, 'PROD ' + t['t'] + ' → ' + t['err'])
                    continue
                chk(t['http'] == 200, 'PROD ' + t['t'] + ' HTTP 200 ('
                    + str(t['bytes']) + ' B' + (', ' + str(t.get('dur')) + ' s'
                    if t.get('dur') else '') + ')')
            ag = r.get('agujas', {})
            faltan = [k for k, v in ag.items() if not v]
            chk(not faltan, 'agujas del cableado EN EL SERVIDO'
                + (' — faltan: ' + ', '.join(faltan) if faltan else ''))
        except Exception as e:
            chk(False, 'PROD: ' + str(e)[:160])
        await page.close()

        await browser.close()

    print()
    print('RESULTADO: ' + str(ok_n[0]) + ' OK · ' + str(fail_n[0])
          + ' fallos')
    sys.exit(0 if fail_n[0] == 0 else 1)


if __name__ == '__main__':
    asyncio.run(main())
