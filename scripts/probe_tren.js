#!/usr/bin/env node
/* Sonda v2.109: qué pasa tras replayLaunch(3) en el oeste (modo depuración). */
const { chromium } = require('/home/z/.npm-global/lib/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = '/home/z/my-project/crazypp';
const PORT = 8803;
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
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.log('CONSOLE:', m.type(), m.text().slice(0, 240)); });
  await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'load', timeout: 60000 });
  await page.waitForFunction('!!window.__PP_GAME', null, { timeout: 60000 });
  await sleep(2000);
  const st1 = await page.evaluate(`(async () => {
    const g = window.__PP_GAME;
    await g.champs.launch('oeste');
    for (let i = 0; i < 60 && !g.champs.active; i++) await new Promise((r) => setTimeout(r, 100));
    const ctrl = window.__PP_OESTE && window.__PP_OESTE.ctrl();
    return { active: g.champs.active, hasCtrl: !!ctrl, stage: ctrl ? ctrl.stage : null,
             dbg: !!window.__PP_DEBUG, msg: g.rules.message, state: g.rules.state };
  })()`);
  console.log('ESTADO1:', JSON.stringify(st1));
  const st2 = await page.evaluate(`(() => {
    const ctrl = window.__PP_OESTE.ctrl();
    try { ctrl.replayLaunch(3); return { launched: true }; }
    catch (e) { return { launched: false, err: String(e) }; }
  })()`);
  console.log('REPLAY:', JSON.stringify(st2));
  for (let i = 0; i < 24; i++) {
    await sleep(1000);
    const s = await page.evaluate(`(() => {
      const ctrl = window.__PP_OESTE.ctrl();
      const g = window.__PP_GAME;
      return { stageMode: ctrl._stageMode, hasTren: !!ctrl._tren,
               phase: ctrl._tren ? ctrl._tren.phase : null,
               msg: g.rules.message, instrK: ctrl._instrK || null };
    })()`);
    console.log('T+' + (i + 1) + 's:', JSON.stringify(s));
    if (s.hasTren && s.phase !== 'intro') break;
  }
  await browser.close();
  server.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
