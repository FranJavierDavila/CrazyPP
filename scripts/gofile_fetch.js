#!/usr/bin/env node
/* Descarga el archivo desde gofile DENTRO del contexto del navegador
 * (cookies de la cuenta invitada) y lo guarda para comparar md5.
 * Uso: node gofile_fetch.js <downloadPage> <salida> */
const { chromium } = require('/home/z/.npm-global/lib/node_modules/playwright');
const fs = require('fs');

(async () => {
  const [pageUrl, outPath] = process.argv.slice(2);
  if (!pageUrl || !outPath) { console.error('uso: gofile_fetch.js <downloadPage> <salida>'); process.exit(1); }
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ acceptDownloads: true });
  const page = await ctx.newPage();
  let direct = null;
  page.on('response', (r) => {
    try {
      const u = r.url();
      if (u && /\/download\/web\//.test(u) && !direct) direct = u;
    } catch (e) { /* */ }
  });
  await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(6000);
  for (const sel of ['button:has-text("Download")', '[class*="download"]', 'a:has-text("Download")']) {
    const el = await page.$(sel);
    if (el) {
      const [dl] = await Promise.all([
        page.waitForEvent('download', { timeout: 25000 }).catch(() => null),
        el.click().catch(() => {}),
      ]);
      if (dl) direct = dl.url();
      break;
    }
  }
  await page.waitForTimeout(3000);
  if (!direct) { console.error('sin URL directa'); await browser.close(); process.exit(2); }
  console.log('DIRECT:', direct);
  // descarga con las cookies del contexto (APIRequestContext compartido)
  const resp = await ctx.request.get(direct, { timeout: 900000 });
  const buf = await resp.body();
  fs.writeFileSync(outPath, buf);
  console.log('bytes:', buf.length);
  await browser.close();
  process.exit(0);
})().catch((e) => { console.error('ERROR', String(e).slice(0, 300)); process.exit(3); });
