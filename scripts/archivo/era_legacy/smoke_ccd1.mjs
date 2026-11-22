// Smoke del laboratorio __PP_CCD_LAB (v3.1.2-CCD1) + regresión FEEL sobre game.html
import { chromium } from 'playwright';

const URL = process.env.QA_URL || 'http://localhost:3000/game.html';
const browser = await chromium.launch({ args: ['--use-gl=swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errs = [];
page.on('pageerror', (e) => errs.push(String(e)));
await page.goto(URL, { waitUntil: 'networkidle' });
await page.waitForFunction(() => !!window.__PP_CCD_LAB, null, { timeout: 30000 });

const out = await page.evaluate(() => {
  const L = window.__PP_CCD_LAB;
  const F = window.__PP_FEEL_LAB;
  const res = {};
  // -- aceptación CCD (spec J) --
  res.rain = L({ mode: 'rain' });                       // 10k offsets, 40 m/s
  res.rainAng = L({ mode: 'rainAngled', n: 4000 });     // entradas oblicuas 25°
  res.ref = L({ mode: 'ref', n: 300 });                 // vs fuerza bruta
  res.fastPad = L({ mode: 'fastPad' });                 // pala 20 m/s
  res.frameDrop = L({ mode: 'frameDrop' });             // cruce en 33 ms
  res.spinBlade = L({ mode: 'spinBlade' });             // rotación 35 rad/s
  res.spinSlow = L({ mode: 'spinBlade', omega: 6 });    // rotación lenta: golpe de cara
  res.edge = L({ mode: 'edge' });                       // canto/esquina
  res.energy = L({ mode: 'energy' });                   // coherencia energética
  res.perf = L({ mode: 'perf' });                       // coste
  // -- regresión FEEL (los 3 ajustes del dueño intactos) --
  res.graceOn = F({ mode: 'grace' });
  res.decay = F({ mode: 'decay' });
  res.stroke = F({ mode: 'stroke' });
  res.version = document.querySelector('#verBadge')?.textContent || '?';
  return res;
});

console.log('== rain      ==', JSON.stringify(out.rain));
console.log('== rainAng   ==', JSON.stringify(out.rainAng));
console.log('== ref       ==', JSON.stringify(out.ref));
console.log('== fastPad   ==', JSON.stringify(out.fastPad));
console.log('== frameDrop ==', JSON.stringify(out.frameDrop));
console.log('== spinBlade ==', JSON.stringify(out.spinBlade));
console.log('== spinSlow  ==', JSON.stringify(out.spinSlow));
console.log('== edge      ==', JSON.stringify(out.edge));
console.log('== energy    ==', JSON.stringify(out.energy));
console.log('== perf      ==', JSON.stringify(out.perf));
console.log('== graceOn   ==', JSON.stringify(out.graceOn));
console.log('== decay     ==', JSON.stringify({ b: out.decay.bounces, rest: out.decay.restSpeed, gap: out.decay.gap, fell: out.decay.fellThrough }));
console.log('== stroke    ==', JSON.stringify(out.stroke));
console.log('badge:', out.version, '| pageerrors:', errs.length, errs.slice(0, 3));

const ok =
  out.rain.hitRate === 1 && out.rain.tunnels === 0 &&
  out.rainAng.hitRate === 1 && out.rainAng.tunnels === 0 &&
  out.ref.maxDtMs < 0.05 && out.ref.maxPosMm < 0.1 &&
  out.fastPad.hit && out.fastPad.exitSpeed > 1 &&   // (la pala a 20 m/s alcanza a la bola tras el golpe: 'through' no es criterio)
  out.frameDrop.hit &&
  out.spinBlade.hit && out.spinBlade.ndot > 0.3 &&
  out.spinSlow.hit && out.spinSlow.ndot > 0.8 &&
  out.edge.hits === out.edge.n && out.edge.tunnels === 0 && out.edge.doubles === 0 &&
  out.energy.ok &&
  out.perf.sweepUs < 5 && out.perf.frameUs < 100 &&
  out.graceOn.hit && out.graceOn.hitMs <= 25 &&
  out.decay.bounces.length >= 5 && !out.decay.fellThrough &&
  out.stroke.maxExit >= 2.25 &&
  errs.length === 0;
console.log('RESULT:', ok ? 'OK' : 'FAIL');
await browser.close();
process.exit(ok ? 0 : 1);
