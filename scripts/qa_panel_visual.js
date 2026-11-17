// Verificación visual del panel v2 (r42): salud LED + datos reales con clave.
// La clave se inyecta en localStorage ANTES de cargar; jamás se imprime.
const { chromium } = require('playwright');
const fs = require('fs');

const CLAVE = fs.readFileSync('/home/z/my-project/upload/scripts/worker-tele/.clave-produccion', 'utf8').trim();
const URL = 'https://franjavierdavila.github.io/CrazyPP/telemetria.html';

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await ctx.addInitScript((c) => { try { localStorage.setItem('pp_tele_clave', c); } catch (e) {} }, CLAVE);
  const page = await ctx.newPage();
  const errores = [];
  page.on('pageerror', (e) => errores.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errores.push(m.text()); });

  await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });

  // LED de salud (público)
  const led = await page.getAttribute('#led', 'class');
  const saludTxt = await page.textContent('#saludtxt');
  console.log('LED:', led, '·', saludTxt);

  // el panel autocarga (hay clave): espera a que aparezcan KPIs
  await page.waitForSelector('.kpis', { timeout: 30000 });
  await page.waitForTimeout(1200);
  const kpis = await page.$$eval('.kpi', (els) => els.map((e) => e.querySelector('.t').textContent + '=' + e.querySelector('.n').textContent));
  console.log('KPIs:', JSON.stringify(kpis));
  const secciones = await page.$$eval('section h2', (els) => els.map((e) => e.textContent));
  console.log('Secciones:', secciones.join(' | '));

  // capturas: arriba (salud+KPIs) y abajo (eventos crudos)
  await page.screenshot({ path: '/tmp/render/panel_top.png', clip: { x: 0, y: 0, width: 1280, height: 900 } });
  await page.evaluate(() => document.querySelector('section:last-of-type').scrollIntoView());
  await page.waitForTimeout(400);
  await page.screenshot({ path: '/tmp/render/panel_bottom.png', clip: { x: 0, y: 0, width: 1280, height: 900 } });

  // clic en la primera fila de eventos → expande JSON
  const fila = await page.$('.fila-ev');
  if (fila) { await fila.click(); await page.waitForTimeout(300); const abierta = await page.$('.fila-ex.abierta pre.json'); console.log('Expandir JSON:', abierta ? 'OK' : 'NO'); }

  console.log('errores de página:', errores.length ? errores.slice(0, 5) : '0');
  await browser.close();
})().catch((e) => { console.error('FALLO:', e.message); process.exit(1); });
