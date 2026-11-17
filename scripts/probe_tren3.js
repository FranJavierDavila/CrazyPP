#!/usr/bin/env node
/* Sonda 3 v2.109: vista del jugador con cámara congelada + diagnóstico parallax. */
const { chromium } = require('/home/z/.npm-global/lib/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = '/home/z/my-project/crazypp';
const PORT = 8807;
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
  await sleep(1000);
  // marcha
  await page.evaluate('window.__PP_OESTE.ctrl()._tren._stoppedT = 99');
  await page.waitForFunction("window.__PP_OESTE.ctrl()._tren.phase === 'run'", null, { timeout: 20000 });
  await page.waitForFunction('window.__PP_OESTE.ctrl()._tren.W > 2', null, { timeout: 40000 });
  // descubrir el lienzo 3D
  await page.evaluate(`(() => {
    for (const id of ['overlay', 'wrlov', 'introov']) {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    }
  })()`);
  await sleep(500);

  // diagnóstico: posiciones de los planos y del andén
  const diag = await page.evaluate(`(() => {
    const t = window.__PP_OESTE.ctrl()._tren;
    const out = { W: +t.W.toFixed(1), v: +t.v.toFixed(2), stationZ: +t.station.position.z.toFixed(1), layers: [] };
    t.group.traverse((m) => {
      if (m.isMesh && m.geometry && m.geometry.type === 'PlaneGeometry' &&
          m.material && m.material.map && m.renderOrder >= 1 && m.renderOrder <= 5) {
        out.layers.push({ ro: m.renderOrder, p: m.position.toArray().map((v) => +v.toFixed(1)),
          w: +m.geometry.parameters.width, h: +m.geometry.parameters.height,
          op: +m.material.opacity, tr: !!m.material.transparent, vis: m.visible });
      }
    });
    return out;
  })()`);
  console.log('DIAG:', JSON.stringify(diag, null, 1));

  // ocultar el andén para ver sólo parallax (fxStep fuerza visible:
  // mandar el andén a 1e9 m hace rel=1e9 y se esconde solo)
  await page.evaluate('window.__PP_OESTE.ctrl()._tren.stationW = 1e9');
  for (const [name, px, py, pz, tx, ty, tz] of [
    ['izq', 0.55, 1.62, 1.55, -3.0, 1.72, -1.3],
    ['der', -0.55, 1.62, 1.55, 3.0, 1.65, -1.5],
  ]) {
    await page.evaluate(`(() => {
      const g = window.__PP_GAME;
      const c = g.camera;
      c.position.set(${px}, ${py}, ${pz});
      c.lookAt(${tx}, ${ty}, ${tz});
      c.matrixAutoUpdate = false;
      c.updateMatrix();
      c.matrixWorldNeedsUpdate = true;
    })()`);
    await sleep(700);
    await page.screenshot({ path: '/home/z/my-project/scripts/v2109_fija_' + name + '.png' });
    await page.evaluate('window.__PP_GAME.camera.matrixAutoUpdate = true');
  }
  // con andén, vista izquierda (restaurar el andén de la parada vigente)
  await page.evaluate('window.__PP_OESTE.ctrl()._tren.stationW = window.__PP_OESTE.ctrl()._tren.meetW || 0');
  await page.evaluate(`(() => {
    const g = window.__PP_GAME;
    const c = g.camera;
    c.position.set(0.55, 1.62, 1.55);
    c.lookAt(-3.0, 1.55, -1.3);
    c.matrixAutoUpdate = false;
    c.updateMatrix();
    c.matrixWorldNeedsUpdate = true;
  })()`);
  await sleep(700);
  await page.screenshot({ path: '/home/z/my-project/scripts/v2109_fija_anden.png' });
  await page.evaluate('window.__PP_GAME.camera.matrixAutoUpdate = true');
  await browser.close();
  server.close();
  console.log('SONDA3 FIN');
})().catch((e) => { console.error('ERR', e); process.exit(1); });
