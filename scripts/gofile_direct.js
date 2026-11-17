#!/usr/bin/env node
/* Captura la URL DIRECTA de un downloadPage de gofile.io con Chromium headless
 * (cuenta invitada automática: la API /contents da 401 con invitados, el
 * navegador logra el enlace real de descarga). Uso: node gofile_direct.js <url> */
const { chromium } = require('/home/z/.npm-global/lib/node_modules/playwright');

(async () => {
  const page_url = process.argv[2];
  if (!page_url) { console.error('uso: gofile_direct.js <downloadPage>'); process.exit(1); }
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ acceptDownloads: true });
  const page = await ctx.newPage();
  let direct = null;
  const grab = (u) => {
    try {
      if (u && /\/download\//.test(u) && !direct) { direct = u; console.log('DIRECT:', u); }
    } catch (e) { /* */ }
  };
  page.on('request', (r) => grab(r.url()));
  page.on('response', (r) => grab(r.url()));
  try {
    await page.goto(page_url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(6000);
    // botón de descarga del nuevo UI de gofile
    for (const sel of ['button:has-text("Download")', '[class*="download"]', 'a:has-text("Download")']) {
      const el = await page.$(sel);
      if (el) {
        const [dl] = await Promise.all([
          page.waitForEvent('download', { timeout: 20000 }).catch(() => null),
          el.click().catch(() => {}),
        ]);
        if (dl) { direct = dl.url(); console.log('DIRECT(dl):', direct); }
        break;
      }
    }
    if (!direct) await page.waitForTimeout(8000);
  } catch (e) {
    console.error('aviso:', String(e).slice(0, 160));
  }
  console.log('RESULT:', direct || 'NO_CAPTURADA');
  await browser.close();
  process.exit(direct ? 0 : 2);
})();
