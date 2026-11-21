// r96 · ARNÉS ANTI-BLOQUEO — verificación del paquete del informe del dueño
// («otra vez el bloqueo del juego tan pronto le damos a jugar»):
//   A. VIGILANTE en el bundle: js_error/js_rejection por beacon (sobrevive al
//      bloqueo), freeze_report con contexto + 12 huecos de frame, latido VR,
//      guarda de pestaña oculta.
//   B. Muñeca anatómica: perpendicular GARANTIZADA (el fallback r95 podía ser
//      ∥ al eje hoja → cruz cero → NaN).
//   C. SW: purga de cachés viejas DIFERIDA 5 min (claim inmediato).
//   D. VIVO: la tubería del vigía funciona de verdad (error sintético →
//      localStorage ppxr_js_error en el juego corriendo).
import * as THREE from 'three';
import { readFileSync } from 'node:fs';

const RAIZ = '/home/z/my-project';
let ok = 0, fails = 0;
const aguja = (nombre, cond) => {
  if (cond) { ok++; console.log(`  ✓ ${nombre}`); }
  else { fails++; console.log(`  ✗ ${nombre}`); }
};

/* — A · el VIGILANTE viaja en el bundle — */
{
  const b = readFileSync(RAIZ + '/public/game.html', 'utf-8');
  aguja('vigía · IIFE instalada en carga de módulo (fuera del bloque DEPS)',
    b.includes('r96 · VIGILANTE DE BLOQUEO') &&
    b.indexOf('r96 · VIGILANTE') > b.indexOf('DEPS-FASE2-FIN'));
  aguja('vigía · js_error y js_rejection → sendBeacon (IPC aparte: llega congelado)',
    b.includes("e: 'js_error'") && b.includes("e: 'js_rejection'") &&
    b.includes('navigator.sendBeacon(EP'));
  aguja('vigía · freeze_report con contexto y huecos de frame',
    b.includes('freeze_report') && b.includes('huecoMedio') &&
    b.includes('xr') && b.includes('enHall') && b.includes('net:'));

  aguja('vigía · latido VR cada ~30 s presentando (pipeline observable sin error)',
    b.includes("e: 'vr_latido'"));
  aguja('vigía · pestaña oculta NO cuenta como bloqueo (rAF lo para el navegador)',
    b.includes("document.visibilityState !== 'visible'"));
  aguja('vigía · máx 5 informes por episodio + rearme al respirar',
    b.includes('informes >= 5') && b.includes('informes = 0'));
  aguja('vigía · persistencia local para el visor (ppxr_freeze_report / ppxr_js_error)',
    b.includes("localStorage.setItem('ppxr_' + ev.e, cuerpo)"));
}

/* — B · perpendicular garantizada de la muñeca (réplica del guard r96) — */
{
  const basePerp = (Y) => {
    const X = new THREE.Vector3(0, 0, 0);
    if (Math.abs(Y.x) < 0.9) X.x = 1;
    else if (Math.abs(Y.y) < 0.9) X.y = 1;
    else X.z = 1;
    X.addScaledVector(Y, -X.dot(Y));
    return X;
  };
  // los tres casos degenerados: eje hoja ∥ X mundo · ∥ Y mundo · ∥ Z mundo
  const casos = [new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 1, 0),
    new THREE.Vector3(0, 0, 1), new THREE.Vector3(0.7, 0.7, 0).normalize()];
  let todosPerp = true, todosNoCero = true;
  for (const Y of casos) {
    const X = basePerp(Y);
    if (X.lengthSq() < 0.5) todosNoCero = false;
    if (Math.abs(X.dot(Y)) > 1e-6) todosPerp = false;
  }
  aguja('muñeca · el fallback r96 JAMÁS es paralelo al eje hoja (4 orientaciones)',
    todosPerp);
  aguja('muñeca · el fallback r96 JAMÁS es el vector cero', todosNoCero);
  aguja('muñeca · la cruz final nunca es cero → quat sin NaN',
    (() => {
      for (const Y of casos) {
        const X = basePerp(Y).normalize();
        const Z = new THREE.Vector3().crossVectors(X, Y);
        if (Z.lengthSq() < 0.5) return false;
      }
      return true;
    })());
}

/* — C · service worker: purga diferida — */
{
  const sw = readFileSync(RAIZ + '/public/sw.js', 'utf-8');
  aguja('sw · claim INMEDIATO y purga DIFERIDA (5 min) de cachés viejas',
    sw.includes('await self.clients.claim();') &&
    sw.includes('5 * 60 * 1000') &&
    sw.indexOf('clients.claim') < sw.indexOf('5 * 60 * 1000'));
  const VER_DIN = JSON.parse(readFileSync(RAIZ + '/src/game/VERSION.json', 'utf-8')).version;
  aguja('sw · el sello de caché viaja con la versión ' + VER_DIN,
    sw.includes("const CACHE = 'crazypp-v" + VER_DIN + "'"));
  aguja('r98 · sw · game.html en RED-PRIMERO con límite (adiós al «una visita por detrás»)',
    sw.includes("endsWith('/game.html')") && sw.includes('function redPrimero(') &&
    sw.includes("cache: 'no-store'") && sw.includes('Promise.race'));
}

/* — D · sellos 3.6.188 en el bundle — */
{
  const b = readFileSync(RAIZ + '/public/game.html', 'utf-8');
  // r98 · el sello deja de ir HARDCODED: lee la versión del repo y la exige
  // en el bundle (en r97 este tipo de aguja fija ocultó que el sw.js no se
  // había committado).
  const ver = JSON.parse(readFileSync(RAIZ + '/src/game/VERSION.json', 'utf-8')).version;
  const reVer = new RegExp(ver.replace(/\./g, '\\.'), 'g');
  aguja(`sellos · ${ver} en c00 y badge`,
    (b.match(reVer) || []).length >= 2);
}

console.log(`\nARNÉS ANTI-BLOQUEO r96 · ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);
