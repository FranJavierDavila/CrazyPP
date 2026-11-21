// test_r110_cripto_fin_v36208.mjs — r110 · LA CRIPTONITA SE DESTRUYE AL EXPIRAR
// Bug de raíz (reporte del dueño, 21-11-2026): los cristales de Super
// Criptonita no desaparecían NUNCA — quedaban congelados toda la partida.
// Causa: fin() del pool solo MARCA la rotura (roto = 0) y el update() que
// la completa dejaba de correr: el cerrojo del frame era «_criptoT > 0» y
// _criptoFin() pone _criptoT = 0 ANTES de que la animación avance un paso.
// Fix de la ronda (tres piezas asertadas aquí):
//   1 · c12: el cerrojo deja correr el frame mientras queden roturas en
//       curso (cristalesCripto.pendientes() > 0).
//   2 · c07: el pool cuenta pendientes() y su fin() arranca un plazo duro
//       FIN_PLAZO — el vigilante de update() destruye TODO al vencerlo
//       (patrón del vigilante del portal, v3.6.42).
//   3 · c07: nace() cancela el plazo — re-armar el poder dentro del margen
//       no mata los cristales de la ventana nueva.
import { readFileSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  if (cond) { ok++; console.log('  ✓ ' + label); }
  else { fails++; console.log('  ✗ FALLO: ' + label); }
};
const RAIZ = '/home/z/my-project';
const c07 = readFileSync(RAIZ + '/src/game/core/c07_escena_sala.js', 'utf8');
const c12 = readFileSync(RAIZ + '/src/game/core/c12_pingponggame.js', 'utf8');
const vj = JSON.parse(readFileSync(RAIZ + '/src/game/VERSION.json', 'utf8'));

console.log('r110 · CRIPTONITA AL EXPIRAR — pool (c07)');
chk(c07.includes('const FIN_PLAZO = MUERTE + 0.25'),
  'plazo duro FIN_PLAZO definido (MUERTE + 0,25 s)');
chk(c07.includes('let finPlazo = -1;'),
  'estado finPlazo declarado (−1 = sin plazo)');
chk(/fin\(\) \{[\s\S]{0,200}?finPlazo = FIN_PLAZO;/.test(c07),
  'fin() marca las roturas Y arranca el plazo');
chk(/if \(finPlazo > 0\) \{[\s\S]{0,400}?finPlazo -= dt;[\s\S]{0,300}?P\[i\]\.t = -1; P\[i\]\.grp\.visible = false;/.test(c07),
  'update() lleva el vigilante: al vencer el plazo oculta TODO');
chk(/pendientes\(\) \{[\s\S]{0,200}?P\[i\]\.t >= 0 && P\[i\]\.roto >= 0/.test(c07),
  'pendientes() cuenta los cristales con rotura EN CURSO');
{
  const ini = c07.indexOf('nace(p, topY) {');
  const finBloque = c07.indexOf('return cuantos;', ini);
  chk(ini > 0 && finBloque > ini && c07.slice(ini, finBloque).includes('finPlazo = -1;'),
    'nace() cancela el plazo viejo (una ventana re-armada no se suicida)');
}
{
  const mFin = c07.match(/const FIN_PLAZO = MUERTE \+ ([\d.]+)/);
  const margen = mFin ? parseFloat(mFin[1]) : 0;
  chk(margen > 0 && margen < 0.5,
    'el plazo duro da margen a la rotura normal (MUERTE 0,3 + ' + margen + ' s) sin alargarla en exceso');
}

console.log('r110 · CRIPTONITA AL EXPIRAR — cerrojo del frame (c12)');
{
  const llamado = c12.indexOf('this._criptoFrame(dt);');
  const zona = llamado > 0 ? c12.slice(Math.max(0, llamado - 900), llamado) : '';
  chk(zona.includes('pendientes() > 0'),
    'el frame corre también con roturas pendientes (no solo _criptoT > 0)');
  chk(zona.includes('this.cristalesCripto &&'),
    'el cerrojo nuevo protege el pool nulo');
  chk(/_criptoFin\(\) \{[\s\S]{0,400}?cristalesCripto\.fin\(\)/.test(c12),
    '_criptoFin() sigue llamando al fin() del pool');
  chk(zona.includes('cristales congelados') || zona.includes('BUG DE RAÍZ'),
    'la causa raíz queda documentada junto al cerrojo');
}
{
  // el siembro por bote sigue cerrado fuera de ventana (sin cristales nuevos)
  const ini = c12.indexOf('if (this._criptoT > 0 && this.cristalesCripto)');
  chk(ini > 0, 'la siembra por bote sigue gated a _criptoT > 0');
}

console.log('r110 · SELLOS DE LA RONDA');
chk(vj.version === '3.6.208-SDK6', 'VERSION.json: 3.6.208-SDK6');
chk(vj.fase === 185, 'FASE 185');
chk(vj.hub === 'v36208-sdk6', 'hub v36208-sdk6');
chk(c00_version() === '3.6.208-SDK6', 'sello c00 = 3.6.208-SDK6');
chk(readFileSync(RAIZ + '/src/game/03_body.html', 'utf8').includes('3.6.208'),
  'badge del arranque (#verBadge) = 3.6.208');
{
  const game = readFileSync(RAIZ + '/public/game.html');
  const sha = createHash('sha256').update(game).digest('hex');
  chk(sha === vj.golden, 'golden coincide con el build (' + sha.slice(0, 12) + '…)');
  chk(vj.tamano === game.length, 'tamaño del build en VERSION.json (' + game.length + ' B)');
  chk(game.toString('utf8').includes('pendientes() > 0'),
    'el bundle lleva el cerrojo nuevo');
  chk(game.toString('utf8').includes('const FIN_PLAZO = MUERTE + 0.25'),
    'el bundle lleva el vigilante del pool');
}
function c00_version() {
  const m = readFileSync(RAIZ + '/src/game/core/c00_pre_three.js', 'utf8')
    .match(/const VERSION = '([^']+)';/);
  return m ? m[1] : '(sin sello)';
}

console.log('\nRESULTADO: ' + ok + ' OK · ' + fails + ' FALLOS' +
  (fails === 0 ? ' — LA MESA QUEDA LIMPIA' : ''));
process.exit(fails === 0 ? 0 : 1);
