#!/usr/bin/env node
/* v2.109 · Verificación funcional + visual de «ASALTO AL TREN · EL VAGÓN».
 * Servidor HTTP local + Playwright Chromium (swiftshader).
 * Flujo: jugador FORO3D (modo depuración) → launch('oeste') → replayLaunch(3)
 * → cartel (callback forzado: en headless el tiempo de juego va lento)
 * → TrenAction → comprobaciones + CAPTURAS del vagón y parallax.
 * Ciclo: intro (estación) → run (parallax) → candados → arrive → stop
 * (andén) → parada 2 (raíles) → fail → restauración de la sala. */
const { chromium } = require('/home/z/.npm-global/lib/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = '/home/z/my-project/crazypp';
const PORT = 8801;
const SHOTS = '/home/z/my-project/scripts';
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.webp': 'image/webp', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary', '.mp3': 'audio/mpeg',
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
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  await new Promise((r) => server.listen(PORT, r));
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--no-sandbox'] });
  const ctx = await browser.newContext({ viewport: { width: 960, height: 540 } });
  await ctx.addInitScript(() => {
    try { localStorage.setItem('pp_player_name', 'FORO3D'); } catch (e) { /* */ }
  });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(String(e)));
  await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'load', timeout: 60000 });
  await page.waitForFunction('!!window.__PP_GAME', null, { timeout: 60000 });
  await sleep(2500);
  // modo de PRUEBAS 2D del núcleo: activa el bucle en headless (testStep incluido)
  await page.evaluate('window.__pp2DPlay = true');
  await sleep(400);
  chk('T1 · sin errores de página al arrancar', errs.length === 0, errs.slice(0, 2).join(' | '));

  // entrar al OESTE y saltar a la etapa 4 (modo depuración)
  await page.evaluate(`(async () => {
    const g = window.__PP_GAME;
    await g.champs.launch('oeste');
    for (let i = 0; i < 60 && !g.champs.active; i++) await new Promise((r) => setTimeout(r, 100));
    const ctrl = window.__PP_OESTE && window.__PP_OESTE.ctrl();
    if (ctrl) { ctrl._armT = 0; ctrl.replayLaunch(3); }
  })()`);
  // el cartel explica la prueba; el callback dispara el TrenAction
  await page.waitForFunction(
    '(window.__PP_OESTE.ctrl()._instrK === "tren") || !!window.__PP_OESTE.ctrl()._tren',
    null, { timeout: 30000 });
  await page.evaluate('(() => { const g = window.__PP_GAME; if (g._instr && !g._instr.cb) g.hideInstrucciones(false); if (g._instr) g.hideInstrucciones(false); })()');
  await page.waitForFunction('!!window.__PP_OESTE.ctrl()._tren', null, { timeout: 20000 });
  await sleep(1500);

  chk('T2 · sin errores de página tras el salto', errs.length === 0, errs.slice(0, 2).join(' | '));
  chk('T3 · _stageMode = tren', await page.evaluate(
    "window.__PP_OESTE.ctrl()._stageMode === 'tren'"));
  chk('T4 · fase intro (parada en la estación 1)', await page.evaluate(
    "window.__PP_OESTE.ctrl()._tren.phase === 'intro'"));
  chk('T5 · tren DETENIDO (v=0, W=0)', await page.evaluate(
    'window.__PP_OESTE.ctrl()._tren.v === 0 && window.__PP_OESTE.ctrl()._tren.W === 0'));
  chk('T6 · sala clásica OCULTA (el vagón manda)', await page.evaluate(
    'window.__PP_GAME.roomGroup.visible === false'));
  chk('T7 · cámara FAR = 500 (parallax lejano visible)', await page.evaluate(
    'window.__PP_GAME.camera.far === 500'));
  chk('T8 · 10 scrollers (cielo + 4 planos × 2 lados)', await page.evaluate(
    'window.__PP_OESTE.ctrl()._tren.scrollers.length === 10'));
  chk('T9 · andén visible y centrado (estación BRAVOS)', await page.evaluate(
    "window.__PP_OESTE.ctrl()._tren.station.visible && Math.abs(window.__PP_OESTE.ctrl()._tren.station.position.z) < 0.01"));
  chk('T10 · 3 candados de la parada 1 (repisas)', await page.evaluate(
    'window.__PP_OESTE.ctrl()._tren.locks.length === 3'));

  // recorte alfa de las ventanas (carga asíncrona del arte)
  let cut = 0;
  for (let i = 0; i < 24; i++) {
    cut = await page.evaluate(`(() => {
      const t = window.__PP_OESTE.ctrl()._tren;
      let n = 0;
      t.group.traverse((m) => { if (m.material && m.material.transparent && m.material.map) n++; });
      return n;
    })()`);
    if (cut >= 2) break;
    await sleep(500);
  }
  chk('T11 · ventanas RECORTADAS (paredes con alfa cargadas)', cut >= 2, 'transparentes=' + cut);

  // descubrir el LIENZO 3D: fuera menú y overlays DOM
  await page.evaluate(`(() => {
    for (const id of ['overlay', 'wrlov', 'introov']) {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    }
  })()`);
  await sleep(600);

  // captura 1: intro — el vagón detenido en la estación
  await page.screenshot({ path: SHOTS + '/v2109_intro_estacion.png' });

  // ARRANCA: forzar el fin de la espera
  await page.evaluate('window.__PP_OESTE.ctrl()._tren._stoppedT = 99');
  await page.waitForFunction("window.__PP_OESTE.ctrl()._tren.phase === 'run'", null, { timeout: 20000 });
  chk('T12 · fase run tras arrancar', true);
  await page.waitForFunction(
    'window.__PP_OESTE.ctrl()._tren.v > 0.3 && window.__PP_OESTE.ctrl()._tren.W > 1.0',
    null, { timeout: 30000 });
  const vw = await page.evaluate('(() => { const t = window.__PP_OESTE.ctrl()._tren; return { v: +t.v.toFixed(2), W: +t.W.toFixed(1) }; })()');
  chk('T13 · el tren AVANZA (v>0.3, W>0.3)', vw.v > 0.3 && vw.W > 0.3, JSON.stringify(vw));

  // el parallax corre: dos muestras del offset de un plano
  const o1 = await page.evaluate('window.__PP_OESTE.ctrl()._tren.scrollers[2].tex.offset.x');
  await page.waitForFunction(
    'window.__PP_OESTE.ctrl()._tren.scrollers[2].tex.offset.x !== ' + JSON.stringify(o1),
    null, { timeout: 30000 });
  const o2 = await page.evaluate('window.__PP_OESTE.ctrl()._tren.scrollers[2].tex.offset.x');
  chk('T14 · el paisaje se DESPLAZA (offset cambia)', o1 !== o2, o1.toFixed(4) + ' → ' + o2.toFixed(4));

  // captura 2: marcha con parallax (vista frontal)
  await page.screenshot({ path: SHOTS + '/v2109_marcha_parallax.png' });

  // vistas desde el JUGADOR: ventana izquierda, derecha y cajas fuertes
  await page.evaluate(`(() => {
    const g = window.__PP_GAME;
    g.camera.position.set(0.55, 1.62, 1.55);
    g.camera.lookAt(-3.0, 1.72, -1.3);
  })()`);
  await sleep(500);
  await page.screenshot({ path: SHOTS + '/v2109_ventana_izq.png' });
  await page.evaluate(`(() => {
    const g = window.__PP_GAME;
    g.camera.position.set(-0.55, 1.62, 1.55);
    g.camera.lookAt(3.0, 1.65, -1.5);
  })()`);
  await sleep(500);
  await page.screenshot({ path: SHOTS + '/v2109_ventana_der.png' });
  await page.evaluate(`(() => {
    const g = window.__PP_GAME;
    g.camera.position.set(0, 1.62, 1.9);
    g.camera.lookAt(0, 1.0, -4.9);
  })()`);
  await sleep(500);
  await page.screenshot({ path: SHOTS + '/v2109_cajas_fuertes.png' });

  // COMPLETAR la parada 1: abrir las 3 cajas
  await page.evaluate(`(() => {
    const t = window.__PP_OESTE.ctrl()._tren;
    for (const l of t.locks.slice()) if (!l.opened) t._openSafe(l);
  })()`);
  await sleep(800);
  chk('T15 · fase arrive (freno al andén)', await page.evaluate(
    "window.__PP_OESTE.ctrl()._tren.phase === 'arrive'"));
  chk('T16 · andén convocado delante (z negativo)', await page.evaluate(
    'window.__PP_OESTE.ctrl()._tren.station.position.z < -1'));
  // acortar el freno: W al encuentro → _arrived en el próximo step
  await page.evaluate('(() => { const t = window.__PP_OESTE.ctrl()._tren; t.W = t.meetW; })()');
  await page.waitForFunction("window.__PP_OESTE.ctrl()._tren.phase === 'stop'", null, { timeout: 15000 });
  const st = await page.evaluate('(() => { const t = window.__PP_OESTE.ctrl()._tren; return { z: +t.station.position.z.toFixed(2), wave: t.wave }; })()');
  chk('T17 · andén centrado al detenerse y PARADA 2 armada', Math.abs(st.z) < 0.3 && st.wave === 2, JSON.stringify(st));
  await sleep(600);
  await page.screenshot({ path: SHOTS + '/v2109_anden_parada.png' });

  // partir hacia la PARADA 2 (cajas deslizantes en raíles)
  await page.evaluate('window.__PP_OESTE.ctrl()._tren._stoppedT = 99');
  await sleep(1500);
  chk('T18 · fase run en la parada 2', await page.evaluate(
    "window.__PP_OESTE.ctrl()._tren.phase === 'run' && window.__PP_OESTE.ctrl()._tren.wave === 2"));
  chk('T19 · cajas DESLIZANTES activas (slide)', await page.evaluate(
    'window.__PP_OESTE.ctrl()._tren.locks.length === 2 && !!window.__PP_OESTE.ctrl()._tren.locks[0].slide'));

  // FALLA por reloj (2:00 agotado) y cierre ordenado
  await page.evaluate('window.__PP_OESTE.ctrl()._tren.time = 0.05');
  await page.waitForFunction(
    "window.__PP_OESTE.ctrl()._tren && ['win','fail','idle'].includes(window.__PP_OESTE.ctrl()._tren.phase)",
    null, { timeout: 15000 });
  await page.evaluate('(() => { const c = window.__PP_OESTE.ctrl(); if (c._tren && c._tren.phase === "fail") c._tren._finish(); })()');
  await sleep(1200);
  chk('T20 · fallo gestionado: _tren liberado', await page.evaluate(
    '!window.__PP_OESTE.ctrl()._tren'));
  chk('T21 · sala clásica RESTAURADA', await page.evaluate(
    'window.__PP_GAME.roomGroup.visible === true'));
  chk('T22 · cámara FAR restaurada a 60', await page.evaluate(
    'window.__PP_GAME.camera.far === 60'));
  chk('T23 · sin errores de página en todo el ciclo', errs.length === 0, errs.slice(0, 3).join(' | '));

  await browser.close();
  server.close();
  console.log(fails === 0 ? '\n== TODO OK ==' : `\n== ${fails} FALLOS ==`);
  process.exit(fails === 0 ? 0 : 1);
})().catch((e) => { console.error('ERROR TEST:', e); process.exit(2); });
