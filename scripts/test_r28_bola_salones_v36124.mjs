#!/usr/bin/env node
/* CRAZY PING PONG · r28 · v3.6.124 · TEST: BOLA JAMÁS OCULTA + SALONES DE LUJO.
 *
 *   A · BUG del dueño: «jugando en un campeonato con Wizard, después de
 *       lanzar el poder de pala Super Electricidad cuando el rival estaba
 *       sacando la bola no se veía, quedaba oculta… revisa si es causa
 *       del superpoder y vigila que no queda la bola oculta, ya que
 *       imposibilita el juego».
 *       CAUSA RAÍZ (triple): (1) _elecRompe ocultaba la bola SIEMPRE,
 *       incluso quieta preparando el saque; (2) la caducidad de los 0,9 s
 *       sólo re-encendía con state !== 'rally' (el saque de magia vive
 *       como rally → saltaba la reaparición); (3) _elecFin sólo re-
 *       encendía con _elecRotoT <= 0 y estado rally — pero _elecFrame
 *       (el tick que cuenta los 0,9 s) SÓLO corre con _elecT > 0: si la
 *       tormenta moría dentro de la ventana (fin de 10 s, cortina 2/4,
 *       salida), la bola quedaba oculta PARA SIEMPRE (offline no corre
 *       _bolaGuard y los saques de la CPU no re-encienden).
 *       CURA: ① no ocultar si la bola no vuela (|vel| > 0,5), ② la
 *       caducidad re-enciende SIEMPRE (respetando el tránsito de portal),
 *       ③ _elecFin re-enciende SIEMPRE si había bola rota, ④ la estela
 *       vuelve con el showTrail del dueño.
 *
 *   C · «las nuevas salas de Hall son muy cutres… la diferencia es
 *       abismal» con los decorados de La Locura y Wizard — REDISEÑO:
 *       arte PIL nuevo (18 imágenes, 3 salones × 6 caras) con gradientes
 *       multi-parada, oclusión ambiental, glow de 3 pasadas, props
 *       detallados (recreativas con partida viva, Tierra con continentes/
 *       nubes/terminador, shoji con Fuji, tokonoma con ensō) + MOBILIARIO
 *       3D POR SALÓN en c08 (recreativas emisivas con flicker, globo
 *       terráqueo con anillo orbital que gira y flota, tōrō de piedra +
 *       bambúes) montado por vestir()/montarProps y animado en
 *       updateHallFx. Proporciones EXACTAS de los planos (SOF del JPEG).
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 (física) SIN una sola línea nueva.
 *
 * Uso: node --no-warnings scripts/test_r28_bola_salones_v36124.mjs
 */
import { readFileSync, statSync } from 'node:fs';
import { execSync } from 'node:child_process';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');

const c12 = lee('src/game/core/c12_pingponggame.js');
const c08 = lee('src/game/core/c08_hall_hud.js');
const game = lee('public/game.html');

/* — 1 · BUG · el estallido NO oculta una bola quieta (saque) ————————— */
console.log('1 · ESTALLIDO · bola quieta (saque) JAMÁS se oculta');
chk(c12.includes('const vR28 = (this.ball && this.ball.vel) || null;'),
  'guard de velocidad presente en _elecRompe');
chk(c12.includes('(Math.abs(vR28.x) + Math.abs(vR28.y) + Math.abs(vR28.z)) > 0.5'),
  'umbral de vuelo |vel| > 0,5');
chk(/if \(volandoR28\) \{\s*\n\s*if \(this\.ballMesh\) this\.ballMesh\.visible = false/.test(c12),
  'sólo se oculta si VOLANDO');
chk(c12.includes("this._elecRotoT = 0;   // bola quieta (saque): visible y al asunto"),
  'bola quieta: sin ventana de ocultación');

/* — 2 · BUG · la caducidad de los 0,9 s re-enciende SIEMPRE ——————————— */
console.log('2 · CADUCIDAD · reaparición sin condición de estado');
chk(!/if \(this\._elecRotoT <= 0 && this\.rules\.state !== 'rally'\)/.test(c12),
  'el guard viejo (state !== rally) está FUERA');
chk(/_elecRotoT <= 0 && this\.ballMesh &&\s*\n\s*!\(this\.ball && this\.ball\.ppTransito\)/.test(c12),
  'caducidad re-enciende respetando sólo el tránsito de portal');
const idxExpira = c12.indexOf('BUG DEL DUEÑO');
chk(idxExpira > 0, 'la cura documenta el informe del dueño (r28)');

/* — 3 · BUG · _elecFin re-enciende aunque la tormenta muera ——————————— */
console.log('3 · FIN DE TORMENTA · red de seguridad sin estado');
chk(/_elecFin\(\) \{[\s\S]*?if \(this\._elecRotoT > 0\) \{\s*\n\s*this\._elecRotoT = 0;/.test(c12),
  '_elecFin apaga _elecRotoT y re-enciende SIEMPRE con bola rota');
chk(/red de seguridad SIN condición de estado/.test(c12), 'comentario de la cura presente');
chk(!/if \(this\.rules\.state === 'rally' && this\._elecRotoT <= 0\) \{\s*\n\s*if \(this\.ballMesh\) this\.ballMesh\.visible = true;\s*\n\s*\}\s*\n\s*this\.rules\.message = T\('arc_elec_fin'\)/.test(c12),
  'el guard viejo de _elecFin está fuera');

/* — 4 · BUG · la estela también vuelve ————————————————————————————————— */
console.log('4 · ESTELA · restaurada con el showTrail del dueño');
const mencionesTrail = (c12.match(/this\.trailObj\.visible = \(this\.showTrail !== false\) && !this\.inHall/g) || []).length;
chk(mencionesTrail === 2, 'estela restaurada en caducidad Y en _elecFin (2 sitios)');

/* — 5 · FÍSICA INTACTA · c04/c05 sha256 = r26b/r27 ———————————————————— */
console.log('5 · FÍSICA INTACTA · c04/c05 sha256');
const SHA_C04 = 'df8f71a3a91e06b6f3e31e21baf2eee78cb563defd358d4560a7bb6fb1aa70ec';
const SHA_C05 = '8bb620820e4974d4ccab8308060d4b8fd7328c812b103f9309bd98654cf81d65';
const sha = (p) => execSync(`sha256sum "${raiz}${p}"`).toString().split(' ')[0];
chk(sha('src/game/core/c04_fisica_ccd.js') === SHA_C04, 'c04 BYTE-EXACTO');
chk(sha('src/game/core/c05_colisiones_ia_golpeo.js') === SHA_C05, 'c05 BYTE-EXACTO');

/* — 6 · SALONES · arte nuevo generado con proporciones EXACTAS ———————— */
console.log('6 · SALONES · 18 imágenes con SOF exacto');
const PLANOS = { frente: [1849, 864], fondo: [1849, 864], izquierda: [2395, 864],
  derecha: [2395, 864], suelo: [1296, 1678], techo: [1296, 1678] };
const sofJpeg = (p) => {
  const b = readFileSync(raiz + p);
  let i = 2;
  while (i < b.length - 9) {
    if (b[i] !== 0xFF) { i++; continue; }
    const m = b[i + 1];
    if (m >= 0xC0 && m <= 0xCF && m !== 0xC4 && m !== 0xC8 && m !== 0xCC) {
      return [b.readUInt16BE(i + 7), b.readUInt16BE(i + 5)];
    }
    i += 2 + b.readUInt16BE(i + 2);
  }
  return null;
};
let imgsOk = 0;
for (const sal of ['neon', 'observatorio', 'dojo']) {
  for (const [pieza, [w, h]] of Object.entries(PLANOS)) {
    const p = `public/assets/hall/${sal}/${pieza}.jpg`;
    try {
      const dim = sofJpeg(p);
      if (dim && dim[0] === w && dim[1] === h) imgsOk++;
      else console.log(`    ✗ ${p}: ${JSON.stringify(dim)}`);
    } catch { console.log(`    ✗ ${p}: no existe`); }
  }
}
chk(imgsOk === 18, `18/18 imágenes con proporciones EXACTAS (hay ${imgsOk})`);
// el arte nuevo es MÁS PESADO que el r26b (más detalle, no menos)
const kb = (p) => statSync(raiz + p).size / 1024;
chk(kb('public/assets/hall/neon/frente.jpg') > 100, 'neon/frente con detalle (más de 100 KB)');
chk(kb('public/assets/hall/dojo/suelo.jpg') > 140, 'dojo/suelo con trama (más de 140 KB)');

/* — 7 · MOBILIARIO 3D · props por salón en c08 ———————————————————————— */
console.log('7 · PROPS 3D · c08 monta y anima el mobiliario');
chk(c08.includes('MOBILIARIO 3D POR SALÓN'), 'bloque r28 documentado');
chk(c08.includes("b === 'assets/hall/neon/'") && c08.includes('RECREATIVAS reales'),
  'neón: recreativas 3D');
chk(c08.includes('GLOBO TERRÁQUEO') && c08.includes('TorusGeometry(0.46'), 'observatorio: globo + anillo');
chk(c08.includes('TŌRŌ (farolillo de piedra)') && c08.includes('bambúes'), 'dojo: tōrō + bambúes');
chk(c08.includes('montarProps(vbase);'), 'props montados al crear el hall');
chk(/try \{ if \(typeof montarProps === 'function'\) montarProps\(b\); \} catch/.test(c08),
  'vestir() re-monta los props al cambiar de salón');
chk(c08.includes('fx: { balls, props: _propAnim }'), 'props expuestos en ud.fx');
chk(c08.includes('u.flicker.emissiveIntensity'), 'flicker CRT en updateHallFx');
chk(c08.includes('if (u.giro) m.rotation.y += dt * u.giro;'), 'globo/anillo giran en updateHallFx');
chk(!/new THREE\.PointLight\(/.test(c08.slice(c08.indexOf('MOBILIARIO 3D POR SALÓN'), c08.indexOf('g.userData.hall = {'))),
  'cero PointLights nuevos (lección v2.92)');

/* — 8 · BUILD · sellos ————————————————————————————————————————————————— */
console.log('8 · BUILD · sello vigente (re-anclada r30: 3.6.126-SDK6)');
const vj = JSON.parse(lee('src/game/VERSION.json'));
chk(vj.version === '3.6.126-SDK6', 'VERSION.json = 3.6.126-SDK6 (re-anclada r30)');
chk(vj.fase === 128, 'FASE 128 (re-anclada r30)');
chk(game.includes('3.6.126-SDK6'), 'bundle con sello vigente (re-anclada r30)');
const golden = (lee('src/game/GOLDEN_SHA256.txt').match(/\b[0-9a-f]{64}\b/) || [''])[0];
chk(vj.golden === golden, 'golden coherente');
chk(vj.tamano === Buffer.byteLength(game), 'tamaño coherente');
chk(game.includes('volandoR28') && game.includes('MOBILIARIO 3D POR SALÓN'),
  'el bundle lleva las dos curas (bug + salones)');

/* — 9 · SANIDAD · las rondas anteriores viven ————————————————————————— */
console.log('9 · SANIDAD · sin regresiones');
chk(game.includes('window.__PP_DEBUG) return true'), 'r27: bypass FORO3D vive');
chk(game.includes('ELEC_ATRAE_P'), 'r26b: bola atractora vive');
chk(game.includes('CRONO_F'), 'r26b: Súper Crono vive');
chk(game.includes('ELEC_NIEBLA_N = 14'), 'r26: niebla densa vive');
chk(game.includes('RED_ARC_N'), 'r26: barrera eléctrica vive');

console.log(`\nR28 · ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
