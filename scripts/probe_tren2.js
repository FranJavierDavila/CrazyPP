#!/usr/bin/env node
/* Sonda 2: gates de replayLaunch + showInstrucciones paso a paso. */
const { chromium } = require('/home/z/.npm-global/lib/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = '/home/z/my-project/crazypp';
const PORT = 8805;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.webp': 'image/webp', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary', '.mp3': 'audio/mpeg' };
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
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  await new Promise((r) => server.listen(PORT, r));
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--no-sandbox'] });
  const ctx = await browser.newContext();
  await ctx.addInitScript(() => { try { localStorage.setItem('pp_player_name', 'FORO3D'); } catch (e) {} });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => console.log('PAGEERROR:', String(e).slice(0, 300)));
  page.on('console', (m) => { if (m.type() === 'warning' || m.type() === 'error') console.log('CONSOLE:', m.text().slice(0, 400)); });
  await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'load', timeout: 60000 });
  await page.waitForFunction('!!window.__PP_GAME', null, { timeout: 60000 });
  await sleep(2000);
  const st = await page.evaluate(`(async () => {
    const g = window.__PP_GAME;
    await g.champs.launch('oeste');
    for (let i = 0; i < 60 && !g.champs.active; i++) await new Promise((r) => setTimeout(r, 100));
    const ctrl = window.__PP_OESTE && window.__PP_OESTE.ctrl();
    if (!ctrl) return { noCtrl: true };
    ctrl._armT = 0;
    const gates = {
      active: ctrl.active, inited: ctrl.inited, stageMode: ctrl._stageMode,
      duelOn: ctrl._duelOn, armT: ctrl._armT, stage: ctrl.stage,
      online: g.net.online, hasShowInstr: typeof g.showInstrucciones,
      mapVisible: ctrl.mapa ? ctrl.mapa.visible : null,
    };
    // reproducir manualmente la secuencia de replayLaunch
    try {
      ctrl._replayReal = 1;
      ctrl.stage = 4;
      ctrl._refreshMap();
      ctrl.paintCartel();
      g.rules.message = 'probe';
      ctrl._startTren();
      gates.afterStartTren = { instrK: ctrl._instrK, stageMode: ctrl._stageMode, msg: g.rules.message };
    } catch (e) { gates.err = String(e && e.stack ? e.stack.split('\\n').slice(0,3).join(' | ') : e); }
    return gates;
  })()`);
  console.log('GATES:', JSON.stringify(st, null, 1));
  for (let i = 0; i < 16; i++) {
    await sleep(1000);
    const s = await page.evaluate(`(() => {
      const ctrl = window.__PP_OESTE.ctrl();
      return { hasTren: !!ctrl._tren, phase: ctrl._tren ? ctrl._tren.phase : null,
               instrK: ctrl._instrK || null };
    })()`);
    console.log('T+' + (i + 1) + 's:', JSON.stringify(s));
    if (s.hasTren) break;
  }
  await browser.close();
  server.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
