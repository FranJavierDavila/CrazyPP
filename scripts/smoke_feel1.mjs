// Smoke del laboratorio __PP_FEEL_LAB (grace/decay/stroke) sobre game.html
import { chromium } from 'playwright';

const URL = process.env.QA_URL || 'http://localhost:3000/game.html';
const browser = await chromium.launch({ args: ['--use-gl=swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errs = [];
page.on('pageerror', (e) => errs.push(String(e)));
await page.goto(URL, { waitUntil: 'networkidle' });
await page.waitForFunction(() => !!window.__PP_FEEL_LAB, null, { timeout: 30000 });

const out = await page.evaluate(() => {
  const L = window.__PP_FEEL_LAB;
  const tune = window.__ppDebug.serveTune;
  const res = {};
  // 1) GRACE ON: cruce justo fuera del borde -> la hoja lo alcanza unos ms después
  res.graceOn = L({ mode: 'grace' });
  // 2) GRACE OFF (lateMs=0): mismo intento -> sin golpe
  const saved = tune.lateMs;
  tune.lateMs = 0;
  res.graceOff = L({ mode: 'grace' });
  tune.lateMs = saved;
  // 3) DECAY: botes en decaimiento sobre pala quieta
  res.decay = L({ mode: 'decay' });
  // 4) STROKE: suelo de salida pleno con pala en movimiento
  res.stroke = L({ mode: 'stroke' });
  res.version = window.__game ? 'ok' : 'no-game';
  return res;
});

console.log('== graceOn ==', JSON.stringify(out.graceOn));
console.log('== graceOff ==', JSON.stringify(out.graceOff));
console.log('== decay ==', JSON.stringify({ bounces: out.decay.bounces, restSpeed: out.decay.restSpeed, gap: out.decay.gap, fellThrough: out.decay.fellThrough, eventCount: out.decay.eventCount }));
console.log('== stroke ==', JSON.stringify(out.stroke));
console.log('pageerrors:', errs.length, errs.slice(0, 3));

const okGrace = out.graceOn.hit && out.graceOn.hitMs >= 0 && out.graceOn.hitMs <= 25;
const okOff = !out.graceOff.hit;
const d = out.decay;
const okDecay = d.bounces.length >= 5 &&
  d.bounces.every((v, i) => i === 0 || v < d.bounces[i - 1]) &&
  !d.fellThrough && d.restSpeed < 0.2 && d.gap > 0.015 && d.gap < 0.05;
const okStroke = out.stroke.maxExit >= 2.25;
console.log('RESULT:', (okGrace && okOff && okDecay && okStroke && errs.length === 0) ? 'OK' : 'FAIL');
await browser.close();
