#!/usr/bin/env node
/* Sonda 4 v2.109: sentido del parallax (2 tiros separados) + TÚNEL forzado. */
const { chromium } = require('/home/z/.npm-global/lib/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = '/home/z/my-project/crazypp';
const PORT = 8809;
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
  const ctx = await browser.newContext({ viewport: { width: 960, height: 540 } });
  await ctx.addInitScript(() => { try { localStorage.setItem('pp_player_name', 'FORO3D'); } catch (e) {} });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => console.log('PAGEERROR:', String(e).slice(0, 200)));
  await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'load', timeout: 60000 });
  await page.waitForFunction('!!window.__PP_GAME', null, { timeout: 60000 });
  await sleep(2000);
  await page.evaluate('window.__pp2DPlay = true');
  await page.evaluate(`(async () => {
    const g = window.__PP_GAME;
    await g.champs.launch('oeste');
    for (let i = 0; i < 60 && !g.champs.active; i++) await new Promise((r) => setTimeout(r, 100));
    const ctrl = window.__PP_OESTE.ctrl();
    ctrl._armT = 0; ctrl.replayLaunch(3);
  })()`);
  await page.waitForFunction('(window.__PP_OESTE.ctrl()._instrK === "tren") || !!window.__PP_OESTE.ctrl()._tren', null, { timeout: 30000 });
  await page.evaluate('window.__PP_GAME.hideInstrucciones(false)');
  await page.waitForFunction('!!window.__PP_OESTE.ctrl()._tren', null, { timeout: 20000 });
  await sleep(800);
  await page.evaluate(`(() => {
    for (const id of ['overlay', 'wrlov', 'introov']) {
      const el = document.getElementById(id); if (el) el.style.display = 'none';
    }
    const t = window.__PP_OESTE.ctrl()._tren;
    t._stoppedT = 99;
  })()`);
  await page.waitForFunction("window.__PP_OESTE.ctrl()._tren.phase === 'run'", null, { timeout: 20000 });
  await page.waitForFunction('window.__PP_OESTE.ctrl()._tren.W > 3', null, { timeout: 60000 });
  // ocultar andén
  await page.evaluate('window.__PP_OESTE.ctrl()._tren.stationW = 1e9');
  // cámara fija hacia la ventana DERECHA
  const cam = `(() => {
    const g = window.__PP_GAME; const c = g.camera;
    c.position.set(-0.4, 1.62, 1.5); c.lookAt(3.0, 1.7, -1.5);
    c.matrixAutoUpdate = false; c.updateMatrix(); c.matrixWorldNeedsUpdate = true;
  })()`;
  await page.evaluate(cam);
  await sleep(600);
  await page.screenshot({ path: '/home/z/my-project/scripts/v2109_dir_A.png' });
  await page.evaluate('window.__PP_GAME.camera.matrixAutoUpdate = true');
  await sleep(5000);   // deja correr el tren (v≈2.6 → ~10 m de mundo)
  await page.evaluate(cam);
  await sleep(600);
  await page.screenshot({ path: '/home/z/my-project/scripts/v2109_dir_B.png' });
  await page.evaluate('window.__PP_GAME.camera.matrixAutoUpdate = true');
  // TÚNEL forzado
  await page.evaluate(`(() => {
    const t = window.__PP_OESTE.ctrl()._tren;
    t._tunnelPhase = 'in'; t._tunnelT2 = 1.2;
  })()`);
  await sleep(900);
  await page.evaluate(cam);
  await sleep(600);
  await page.screenshot({ path: '/home/z/my-project/scripts/v2109_tunel.png' });
  await page.evaluate('window.__PP_GAME.camera.matrixAutoUpdate = true');
  await browser.close();
  server.close();
  console.log('SONDA4 FIN');
})().catch((e) => { console.error('ERR', e); process.exit(1); });
