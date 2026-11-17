#!/usr/bin/env node
/* Extrae los <script> inline del index.html y valida su sintaxis con node. */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const html = fs.readFileSync('/home/z/my-project/game/index.html', 'utf8');
const re = /<script(\s[^>]*)?>([\s\S]*?)<\/script>/gi;
let m, i = 0, fails = 0;
const tmp = '/home/z/my-project/scripts/_jscheck';
fs.mkdirSync(tmp, { recursive: true });
while ((m = re.exec(html)) !== null) {
  const attrs = m[1] || '';
  if (/\bsrc\s*=/.test(attrs)) continue;         // externos: fuera
  if (/type\s*=\s*["']importmap["']/.test(attrs)) continue;  // JSON, no JS
  const isModule = /type\s*=\s*["']module["']/.test(attrs);
  const code = m[2];
  if (!code.trim()) continue;
  i++;
  const f = path.join(tmp, `inline_${i}${isModule ? '.mjs' : '.js'}`);
  fs.writeFileSync(f, code);
  try {
    execSync(`node --check ${f}`, { stdio: 'pipe' });
    console.log(`OK    #${i} (${isModule ? 'module' : 'classic'}, ${(code.length / 1024).toFixed(0)} KB)`);
  } catch (e) {
    fails++;
    console.log(`FAIL  #${i}: ${e.stderr.toString().slice(0, 600)}`);
  }
}
console.log(i === 0 ? 'Sin scripts inline.' : `\n${i} bloques, ${fails} fallos`);
process.exit(fails ? 1 : 0);
