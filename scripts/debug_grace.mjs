import { chromium } from 'playwright';
const browser = await chromium.launch({ args: ['--use-gl=swiftshader'] });
const page = await browser.newPage();
await page.goto('http://localhost:3000/game.html', { waitUntil: 'networkidle' });
await page.waitForFunction(() => !!window.__PP_FEEL_LAB);
const out = await page.evaluate(() => {
  window.__PP_HITLOG = { on: true, rows: [] };
  const r = window.__PP_FEEL_LAB({ mode: 'grace' });
  const rows = window.__PP_HITLOG.rows.slice(0, 12);
  // además: state de la bola al final
  window.__PP_HITLOG.on = false;
  return { r, rows };
});
console.log('grace result', JSON.stringify(out.r));
for (const r of out.rows) console.log(JSON.stringify(r));
await browser.close();
