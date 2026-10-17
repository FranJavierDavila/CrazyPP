#!/usr/bin/env node
/* Descarga el paquete V3.1.2 del dueño desde WeTransfer.
 * Uso: node scripts/fetch_wetransfer_v312.mjs [URL] [OUT_DIR]
 * Por defecto: https://we.tl/t-GDFyA4AxKEKthCCq → /home/z/my-project/download/v312
 */
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const SHORT = process.argv[2] || 'https://we.tl/t-GDFyA4AxKEKthCCq';
const OUT_DIR = process.argv[3] || '/home/z/my-project/download/v312';

const sh = (cmd) => {
  try { return execSync(cmd, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }); }
  catch (e) { return (e.stdout || '') + '\n[ERR] ' + (e.stderr || e.message); }
};

fs.mkdirSync(OUT_DIR, { recursive: true });

// 1) Resolver enlace corto → URL firmada
const effective = sh(`curl -sI -L "${SHORT}" -o /dev/null -w '%{url_effective}' --max-time 30`).trim();
console.log('URL efectiva:', effective);

const m = effective.match(/wetransfer\.com\/downloads\/([a-f0-9]{32}\d{14})\/([a-z0-9]+)\?(.*)/i);
if (!m) { console.error('No se pudo parsear el enlace firmado'); process.exit(1); }
const [, transferId, hash, query] = m;
console.log('transferId:', transferId, '| hash:', hash);

const cookieJar = `${OUT_DIR}/cookies.txt`;
// Visitar la página para obtener cookies necesarias
sh(`curl -s -L -c ${cookieJar} "https://wetransfer.com/downloads/${transferId}/${hash}?${query}" -o ${OUT_DIR}/page.html --max-time 60`);

// 2) Probar endpoints de API conocidos
const endpoints = [
  { url: `https://wetransfer.com/api/v4/transfers/${transferId}/download`, body: JSON.stringify({ security_hash: hash, intent: 'entire_transfer' }) },
  { url: `https://wetransfer.com/api/transfer-browser/transfers/${transferId}/download`, body: JSON.stringify({ security_hash: hash, intent: 'entire_transfer' }) },
  { url: `https://wetransfer.com/api/v3/transfers/${transferId}/download`, body: JSON.stringify({ security_hash: hash, intent: 'entire_transfer' }) },
];

let directLink = null;
for (const ep of endpoints) {
  const resp = sh(
    `curl -s -X POST "${ep.url}?${query}" -b ${cookieJar} -H "Content-Type: application/json" ` +
    `-H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36" ` +
    `-H "Accept: application/json" -H "Referer: https://wetransfer.com/" ` +
    `-d '${ep.body}' --max-time 30`
  );
  console.log('---', ep.url.split('/api/')[1], '→', resp.slice(0, 300));
  try {
    const j = JSON.parse(resp);
    if (j.direct_link) { directLink = j.direct_link; break; }
  } catch { /* siguiente endpoint */ }
}

if (!directLink) {
  // 3) Fallback: buscar direct_link incrustado en el HTML de la página
  const page = fs.readFileSync(`${OUT_DIR}/page.html`, 'utf8');
  const dm = page.match(/https:\/\/[^"\\ ]*wetransfer[^"\\ ]*download[^"\\ ]*/i);
  if (dm) directLink = dm[0].replace(/\\u002F/g, '/').replace(/\\\//g, '/');
}

if (!directLink) { console.error('SIN direct_link — habrá que usar el navegador'); process.exit(2); }
console.log('direct_link OK, descargando…');

const outFile = `${OUT_DIR}/paquete-v312.zip`;
sh(`curl -s -L -b ${cookieJar} -D ${OUT_DIR}/headers.txt "${directLink}" -o ${outFile} --max-time 1800 --retry 2`);
const size = fs.statSync(outFile).size;
console.log('Descargado:', outFile, size, 'bytes');

// Nombre real del fichero, si el servidor lo declara
try {
  const headers = fs.readFileSync(`${OUT_DIR}/headers.txt`, 'utf8');
  const cd = headers.match(/content-disposition:[^\n]*filename="?([^";\n]+)"?/i);
  if (cd) console.log('Content-Disposition filename:', cd[1]);
} catch { /* sin cabeceras */ }

console.log(sh(`unzip -t ${outFile} | tail -3`));
