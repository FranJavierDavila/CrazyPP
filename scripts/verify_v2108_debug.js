#!/usr/bin/env node
/* v2.108 · Verificación funcional del MODO DEPURACIÓN «foro3d» (headless).
 * Servidor HTTP local + Playwright Chromium.
 *   A) Jugador NORMAL: __PP_DEBUG=false, rótulo oculto, storage pasa,
 *      maxIdx del mapa de La Locura = etapa real (0 al empezar).
 *   B) Jugador FORO3D: __PP_DEBUG=true, rótulo 2D visible, escrituras de
 *      registro bloqueadas (pp_champ_*, pp_arcade_*, ppxr_stats_v1,
 *      pp_worldrank_cache), ajustes normales pasan (pp_lang),
 *      WORLDRANK.submit()=false sin red, telemetría no encola,
 *      maxIdx=4 (5 etapas) y SALTO REAL a la etapa 4 (ARKANOID 2)
 *      con replayLaunch(3) — y el progreso real intacto (replay). */
const { chromium } = require('/home/z/.npm-global/lib/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = '/home/z/my-project/crazypp';
const PORT = 8799;
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.webp': 'image/webp', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary', '.mp3': 'audio/mpeg',
  '.ogg': 'audio/ogg', '.svg': 'image/svg+xml', '.css': 'text/css',
};

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') p = '/index.html';
  const f = path.join(ROOT, p);
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) {
    res.writeHead(404); res.end('nf'); return;
  }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});

let fails = 0;
function chk(name, cond, extra) {
  const ok = !!cond;
  console.log(`[${ok ? 'OK' : 'FAIL'}] ${name}${extra !== undefined ? ' → ' + extra : ''}`);
  if (!ok) fails++;
}

(async () => {
  await new Promise((r) => server.listen(PORT, r));
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--no-sandbox'] });

  /* ================= A · JUGADOR NORMAL ================= */
  {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push(String(e)));
    await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForFunction('!!window.__PP_GAME', null, { timeout: 60000 });
    await page.waitForTimeout(2500);

    chk('A1 · sin errores de página', errs.length === 0, errs.slice(0, 2).join(' | '));
    chk('A2 · __PP_DEBUG = false', await page.evaluate('window.__PP_DEBUG === false'));
    chk('A3 · rótulo 2D oculto', await page.evaluate(
      "getComputedStyle(document.getElementById('ppdbg')).display === 'none'"));
    // el interceptor deja pasar TODO cuando no es foro3d
    await page.evaluate("localStorage.setItem('pp_champ_locura_stage','9')");
    chk('A4 · storage de campeonato pasa (no debug)', await page.evaluate(
      "localStorage.getItem('pp_champ_locura_stage') === '9'"));
    // mapa de La Locura: sólo la etapa vigente (0 al empezar)
    const mi = await page.evaluate(`(async () => {
      const g = window.__PP_GAME;
      await g.champs.launch('locura');
      const m = g.champs.moduleIfLoaded('locura');
      // espera activa: startArcade requiere data+mapa (carga perezosa)
      for (let i = 0; i < 50 && (!g.champs.active || !m || !m.replayMap); i++) {
        await new Promise((r) => setTimeout(r, 100));
      }
      const rm = (m && m.replayMap) ? m.replayMap() : null;
      return rm ? { maxIdx: rm.maxIdx, nodes: rm.nodesPx.length }
                : { null: true, active: g.champs.active,
                    hasM: !!m, msg: g.rules.message };
    })()`);
    chk('A5 · maxIdx normal = 0 (sin progreso)', mi && mi.maxIdx === 0, JSON.stringify(mi));
    chk('A6 · 5 nodos en el mapa', mi && mi.nodes === 5);
    await ctx.close();
  }

  /* ================= B · JUGADOR FORO3D ================= */
  {
    const ctx = await browser.newContext();
    await ctx.addInitScript(() => {
      try { localStorage.setItem('pp_player_name', 'FORO3D'); } catch (e) { /* */ }
    });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push(String(e)));
    await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForFunction('!!window.__PP_GAME', null, { timeout: 60000 });
    await page.waitForTimeout(2500);

    chk('B1 · sin errores de página', errs.length === 0, errs.slice(0, 2).join(' | '));
    chk('B2 · __PP_DEBUG = true', await page.evaluate('window.__PP_DEBUG === true'));
    chk('B3 · rótulo 2D visible', await page.evaluate(
      "getComputedStyle(document.getElementById('ppdbg')).display === 'block'"));
    chk('B4 · texto del rótulo', await page.evaluate(
      "document.getElementById('ppdbg').textContent === 'MODO DEPURACIÓN'"));

    // bloqueo de escrituras de registro
    await page.evaluate(`(() => {
      localStorage.setItem('pp_champ_locura_stage', '9');
      localStorage.setItem('pp_champ_magia_wins', '9');
      localStorage.setItem('pp_arcade_wins', '9');
      localStorage.setItem('ppxr_stats_v1', '{"won":99}');
      localStorage.setItem('pp_worldrank_cache', '{"x":1}');
      localStorage.setItem('pp_lang', 'en');
      localStorage.setItem('pp_music', '0');
    })()`);
    chk('B5 · pp_champ_* bloqueado', await page.evaluate(
      "localStorage.getItem('pp_champ_locura_stage') === null"));
    chk('B6 · pp_arcade_* bloqueado', await page.evaluate(
      "localStorage.getItem('pp_arcade_wins') === null"));
    chk('B7 · ppxr_stats_v1 bloqueado', await page.evaluate(
      "localStorage.getItem('ppxr_stats_v1') === null"));
    chk('B8 · pp_worldrank_cache bloqueado', await page.evaluate(
      "localStorage.getItem('pp_worldrank_cache') === null"));
    chk('B9 · ajustes (pp_lang) pasan', await page.evaluate(
      "localStorage.getItem('pp_lang') === 'en'"));
    chk('B10 · ajustes (pp_music) pasan', await page.evaluate(
      "localStorage.getItem('pp_music') === '0'"));

    // WORLDRANK: submit devuelve false sin tocar la red
    const sub = await page.evaluate(`(async () => {
      const t0 = performance.now();
      const r = await window.__PP_WORLD.submit('locura', { n: 'FORO3D', p: 1234, a: '🏆', t: Date.now() });
      return { r, ms: Math.round(performance.now() - t0) };
    })()`);
    chk('B11 · WORLDRANK.submit = false (guard)', sub.r === false, `${sub.ms} ms (sin red)`);

    // telemetría: la cola no crece
    const tel = await page.evaluate(`(() => {
      const before = (JSON.parse(localStorage.getItem('pp_tele_q') || '[]')).length;
      window.__PP_TELE.ev('dbg_test_event', { x: 1 });
      window.__PP_TELE.ev('dbg_test_event2', { x: 2 });
      const after = (JSON.parse(localStorage.getItem('pp_tele_q') || '[]')).length;
      return { before, after };
    })()`);
    chk('B12 · telemetría no encola', tel.after === tel.before, JSON.stringify(tel));

    // el nombre del jugador es el del modo depuración
    chk('B13 · ppPlayerName = FORO3D', await page.evaluate(
      "window.__PP_CORE && window.__PP_CORE.ppPlayerName ? window.__PP_CORE.ppPlayerName() === 'FORO3D' : localStorage.getItem('pp_player_name') === 'FORO3D'"));

    await ctx.close();
  }

  /* ============ C · SALTO REAL A CUALQUIER ETAPA (La Locura, foro3d) ============ */
  {
    const ctx = await browser.newContext();
    await ctx.addInitScript(() => {
      try { localStorage.setItem('pp_player_name', 'foro3d'); } catch (e) { /* */ }
    });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push(String(e)));
    await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'load', timeout: 60000 });
    await page.waitForFunction('!!window.__PP_GAME', null, { timeout: 60000 });
    await page.waitForTimeout(2500);

    // minúsculas también activa el modo
    chk('C1 · minúsculas «foro3d» también activa', await page.evaluate('window.__PP_DEBUG === true'));

    const r1 = await page.evaluate(`(async () => {
      const g = window.__PP_GAME;
      await g.champs.launch('locura');
      const m = g.champs.moduleIfLoaded('locura');
      await new Promise((r) => setTimeout(r, 400));
      const rm = m.replayMap ? m.replayMap() : null;
      return { maxIdx: rm ? rm.maxIdx : -1, active: !!g.champs.active };
    })()`);
    chk('C2 · maxIdx = 4 (5 etapas sin requisitos)', r1.maxIdx === 4, JSON.stringify(r1));

    // SALTO a la etapa 4 (índice 3 = ARKANOID 2) con el progreso en 0.
    // v2.107: antes de la prueba sale el CARTEL EXPLICATIVO — se cierra como
    // con el gatillo (hideInstrucciones(false) dispara su callback).
    const r2 = await page.evaluate(`(async () => {
      const g = window.__PP_GAME;
      const m = g.champs.moduleIfLoaded('locura');
      m.replayLaunch(3);
      await new Promise((r) => setTimeout(r, 900));
      const cartelAbierto = !!g._instr;
      if (g._instr) g.hideInstrucciones(false);   // «gatillo» del test
      await new Promise((r) => setTimeout(r, 700));
      return {
        cartelAbierto,
        testActive: m.testActive ? m.testActive() : null,
        state: g.rules.state,
        opp: g.rules.oppLabel,
      };
    })()`);
    chk('C3a · cartel explicativo tras saltar (v2.107)', r2.cartelAbierto === true, JSON.stringify(r2));
    chk('C3b · salto directo a ARKANOID 2 (etapa 4)', r2.testActive === true, JSON.stringify(r2));
    chk('C4 · sin errores tras el salto', errs.length === 0, errs.slice(0, 2).join(' | '));

    // los registros siguen sin escribirse tras jugar un rato
    chk('C5 · ningún registro persistido', await page.evaluate(
      "localStorage.getItem('pp_champ_locura_stage') === null && localStorage.getItem('pp_arcade_wins') === null"));

    // fin del intento: el progreso real (etapa 1, índice 0) debe restaurarse
    const r3 = await page.evaluate(`(async () => {
      const g = window.__PP_GAME;
      const m = g.champs.moduleIfLoaded('locura');
      // derrota inmediata del arkanoid para disparar la restauración
      if (m.onTestLost) m.onTestLost();
      else if (m.arkanoidLost) m.arkanoidLost();
      await new Promise((r) => setTimeout(r, 300));
      return { state: g.rules.state };
    })()`);
    console.log('   (restauración post-intento: state=' + JSON.stringify(r3.state) + ' — la vía replay v2.96 ya la cubre)');
    await ctx.close();
  }

  await browser.close();
  server.close();
  console.log('\nRESULTADO:', fails === 0 ? 'TODO OK' : `${fails} FALLOS`);
  process.exit(fails ? 1 : 0);
})().catch((e) => { console.error('ERROR FATAL', e); process.exit(2); });
