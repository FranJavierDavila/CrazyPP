#!/usr/bin/env node
// r159 · validación de sintaxis: compara bloques <script> del build nuevo
// contra el build anterior (git HEAD). Sólo importa una DIFERENCIA entre
// ambos (los falsos positivos del parseo naïve se dan por iguales).
const { execFileSync } = require('child_process');
const fs = require('fs');

const TMP = '/tmp/r159_head_game.html';
if (!fs.existsSync(TMP)) {
  fs.writeFileSync(TMP,
    execFileSync('git', ['-C', '/home/z/my-project', 'show', 'HEAD:public/game.html'],
      { maxBuffer: 64 * 1024 * 1024 }));
}

function bloques(html) {
  const out = []; const re = /<script([^>]*)>([\s\S]*?)<\/script>/g; let m;
  while ((m = re.exec(html))) out.push({ attrs: m[1], js: m[2] });
  return out;
}

function estado(html) {
  const res = [];
  for (const b of bloques(html)) {
    const tipo = (b.attrs.match(/type="([^"]+)"/) || [])[1] || '';
    if (tipo.includes('json') || tipo.includes('importmap')) { res.push('no-js'); continue; }
    try { new Function(b.js); res.push('ok'); }
    catch (e) { res.push('err:' + e.message); }
  }
  return res;
}

const viejo = estado(fs.readFileSync(TMP, 'utf8'));
const nuevo = estado(fs.readFileSync('/home/z/my-project/public/game.html', 'utf8'));
console.log(`HEAD: ${viejo.length} bloques · NUEVO: ${nuevo.length} bloques`);
if (viejo.length !== nuevo.length) { console.log('✗ número de bloques cambia'); process.exit(1); }
let mal = 0;
for (let i = 0; i < nuevo.length; i++) {
  const igual = viejo[i] === nuevo[i];
  if (!igual) {
    mal++;
    console.log(`✗ bloque ${i} cambia:\n  HEAD : ${String(viejo[i]).slice(0, 120)}\n  NUEVO: ${String(nuevo[i]).slice(0, 120)}`);
  }
}
console.log(mal === 0 ? '✓ sintaxis idéntica a HEAD en todos los bloques (errores naïve pre-existentes, si los hay, no los introduce r159)' : '✗ ' + mal + ' bloques con diferencia');
process.exit(mal === 0 ? 0 : 1);
