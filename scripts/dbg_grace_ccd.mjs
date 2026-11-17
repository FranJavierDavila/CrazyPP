// Debug de la gracia del saque con la CCD nueva (traza por frame)
import { chromium } from 'playwright';
const URL = process.env.QA_URL || 'http://localhost:3000/game.html';
const browser = await chromium.launch({ args: ['--use-gl=swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errs = [];
page.on('pageerror', (e) => errs.push(String(e)));
await page.goto(URL, { waitUntil: 'networkidle' });
await page.waitForFunction(() => !!window.__PP_FEEL_LAB, null, { timeout: 30000 });

const out = await page.evaluate(() => window.__PP_FEEL_LAB({ mode: 'grace', dbg: true }));
console.log('hit:', out.hit, 'hitMs:', out.hitMs, 'offX:', out.offX, 'lateMs:', out.lateMs);
for (const r of (out.trace || []).slice(0, 12)) console.log(JSON.stringify(r));
console.log('pageerrors:', errs.length);
await browser.close();
