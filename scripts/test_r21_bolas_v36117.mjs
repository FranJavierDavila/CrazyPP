#!/usr/bin/env node
/* CRAZY PING PONG · r21 · v3.6.117 · TEST DE SKINS DE BOLA.
 * Primera personalización de la BOLA en la historia del juego (la mesa
 * la tiene desde r96). Verifica la fuente REAL que corre en el Quest:
 *
 *   1 · BOLA_ASPECTOS (c02, importado VIVO): 16 skins, ids únicos, la
 *       OFICIAL primera, candados del vocabulario de casa, estela 0..1
 *       y aro sólo en Saturno · bolaAspectoPorId: id basura → blanca
 *   2 · c07 escena: createBall(skin) + applyBallSkin (mapa con dispose,
 *       material, aro de Saturno) + pintores procedurales deterministas
 *       + estela con BASE de skin + chispas (pool 5×8, sin asignar)
 *   3 · c12 juego: constructor pp_bolaskin · _bolaSkinDef/_bolaTinte/
 *       _bolaSkinLS/_bolaSkinReapply · hooks de campeonato (_mesaNativo →
 *       oficial, _mesaSkinReapply → recobra) · restauración de salida del
 *       hall consciente de skin · estela de reposo = skin · chispas en
 *       flashMarker + update(dt) en tick · UI (tarjeta BOLA, subpágina
 *       salabola, case bola_skin con candado y localStorage)
 *   4 · c09 netlink: HELLO v2 lleva sk (opcional, tolerante), el
 *       invitado la viste vía onPeerSkin (sólo guest, sin candado)
 *   5 · c00 i18n: las 20 claves nuevas en ES y EN
 *   6 · FÍSICA INTACTA: ni c04 ni c05 conocen las skins (garantía del
 *       dueño: cosmético puro — radio, masa, rebote y Magnus intocables)
 *
 * Uso: node --no-warnings scripts/test_r21_bolas_v36117.mjs
 */
import { BOLA_ASPECTOS, BOLA_ID_OFICIAL, bolaAspectoPorId } from '../src/game/core/c02_cfg_escena.js';
import { readFileSync } from 'node:fs';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');

/* — 1 · catálogo vivo (c02 importado) ———————————————————————— */
console.log('1 · BOLA_ASPECTOS (c02, fuente viva)');
chk(BOLA_ASPECTOS.length === 16, `catálogo: 16 skins (${BOLA_ASPECTOS.length})`);
chk(BOLA_ID_OFICIAL === 'blanca' && BOLA_ASPECTOS[0].id === 'blanca', 'la OFICIAL (blanca) es la primera');
const ids = BOLA_ASPECTOS.map((s) => s.id);
chk(new Set(ids).size === ids.length, 'ids únicos');
chk(ids.includes('saturno') && ids.includes('ocho') && ids.includes('tierra'),
  'clásicas + locura + planetas presentes (saturno/ocho/tierra)');
const locksOk = BOLA_ASPECTOS.every((s) => s.lock === null || s.lock === 'wins10' || s.lock === 'streak5');
chk(locksOk, 'candados del vocabulario de casa (null/wins10/streak5 — mismo sistema que las mesas)');
chk(BOLA_ASPECTOS.every((s) => (s.nameKey || '').indexOf('bola_asp_') === 0), 'nameKeys bola_asp_*');
chk(BOLA_ASPECTOS.every((s) => Array.isArray(s.trail) && s.trail.length === 3 &&
    s.trail.every((v) => v >= 0 && v <= 1)), 'trail RGB válido (3 canales 0..1)');
chk(BOLA_ASPECTOS.every((s) => s.ring === true || s.ring === false), 'ring booleano');
chk(BOLA_ASPECTOS.filter((s) => s.ring).map((s) => s.id).join() === 'saturno', 'aro SOLO en Saturno');
const TEXS = new Set(['estrellas', 'playa', 'futbol', 'ocho', 'ojo', 'holo', 'disco', 'marte', 'luna', 'tierra', 'lava', 'saturno']);
chk(BOLA_ASPECTOS.every((s) => s.tex === null || TEXS.has(s.tex)), 'tex ids conocidos por el pintor');
chk(BOLA_ASPECTOS.every((s) => typeof s.rough === 'number' && typeof s.metal === 'number' &&
    typeof s.emis === 'number' && typeof s.emisInt === 'number'), 'material completo (rough/metal/emis/emisInt)');
chk(bolaAspectoPorId('no-existe').id === 'blanca', 'id basura → blanca (respaldo)');
chk(bolaAspectoPorId(undefined).id === 'blanca' && bolaAspectoPorId(42).id === 'blanca', 'entradas basura → blanca sin petar');
chk(bolaAspectoPorId('saturno').trail.length === 3, 'porId devuelve la skin completa');

/* — 2 · c07 escena ————————————————————————————————————————————— */
console.log('2 · c07_escena_sala.js · pintores + chispas');
const c07 = lee('src/game/core/c07_escena_sala.js');
chk(c07.includes('export function applyBallSkin(mesh, skin)'), 'applyBallSkin exportado (malla viva, sin reconstruir)');
chk(c07.includes('export function createBall(skin)'), 'createBall acepta skin (compat: sin skin → blanca)');
chk(c07.includes('export function createChispas()'), 'createChispas exportado');
chk(c07.includes('const N_BURST = 5, N_PART = 8;'), 'chispas: pool fijo 5×8 (40 puntos, Quest 3 lo ni nota)');
chk(c07.includes('function bolaTex(tipo)') && c07.includes('BOLA_TEX_CANVAS[tipo]'), 'texturas procedurales con caché');
chk(c07.includes('document.createElement(\'canvas\')') && c07.includes('THREE.CanvasTexture'), 'canvas 2D → CanvasTexture (cero bytes en el bundle)');
chk(c07.includes('function _bolRng(seed)') && c07.includes('20261107'), 'RNG con semilla fija (determinista: Marte igual en los 2 cascos)');
chk(c07.includes('prevMap.dispose()'), 'el mapa anterior se LIBERA (sin fuga de GPU)');
chk(c07.includes("aro.name = 'ppBolaAro'"), 'aro de Saturno con nombre (toggle visible)');
chk(c07.includes('const trailUpdate = (ball, dt, tint, base) =>'), 'estela acepta BASE de skin');
chk(c07.includes('if (base && base.length === 3) { r = base[0]; g = base[1]; b = base[2]; }'), 'base de skin sin tint ni efecto → color de la skin');
chk(c07.includes("skin.tex ? bolaTex(skin.tex) : null"), 'skin sin tex → material plano');

/* — 3 · c12 juego ——————————————————————————————————————————————— */
console.log('3 · c12_pingponggame.js · integración');
const c12 = lee('src/game/core/c12_pingponggame.js');
chk(c12.includes("BOLA_ASPECTOS") && c12.includes("bolaAspectoPorId"), 'c12 importa el catálogo');
chk(c12.includes('applyBallSkin') && c12.includes('createChispas'), 'c12 importa applyBallSkin + createChispas');
chk(c12.includes("localStorage.getItem('pp_bolaskin')"), 'constructor lee pp_bolaskin');
chk(c12.includes('this._bolaTinte(this._bolaSkinDef(this.bolaSkin))'), 'skin del dueño aplicada al arranque');
chk(c12.includes('_bolaSkinDef(skinId) {'), '_bolaSkinDef con candado (espejo de _mesaSkinDef)');
chk(c12.includes("if (sk.lock && !this._mesaLibre(sk.lock)) sk = BOLA_ASPECTOS[0];"), 'candado reutiliza _mesaLibre (misma economía de desbloqueo)');
chk(c12.includes('_bolaSkinLS() {'), '_bolaSkinLS para reaplicar sin tocar lo guardado');
chk(c12.includes('const nativo = this.mesaOcupada();   // regla del dueño (como la mesa)'), 'REGLA DEL DUEÑO: champ → oficial');
chk(c12.includes('this._bolaTinte(BOLA_ASPECTOS[0])'), '_mesaNativo también pone la bola oficial');
chk(c12.includes('try { this._bolaSkinReapply(); } catch { /* */ }'), '_mesaSkinReapply recobra la skin al salir del champ');
chk(c12.includes('try { this._bolaTinte(this._bolaSkinDef(this._bolaSkinLS())); } catch (eSkin)'), 'salida del hall: restauración consciente de skin (adiós blanco seco)');
chk(c12.includes('const rt = this._bolaTrailRest || [0.75, 0.75, 0.75];'), 'estela de reposo = RGB de la skin');
chk(c12.includes('this.trailUpdate(this.ball, dt, this._trailTint, this._bolaTrailRest)'), 'trailUpdate recibe la base de skin');
chk(c12.includes('this.chispas.burst({ x: pos.x'), 'chispas en flashMarker (bote)');
chk(c12.includes('this._chispaRGB()'), 'chispas del COLOR de la skin');
chk(c12.includes('if (this.chispas) {\n      try { this.chispas.update(dt); } catch { /* */ }\n    }'), 'chispas.update(dt) en el tick');
chk(c12.includes("case 'salabola': {"), 'subpágina salabola');
chk(c12.includes("'page:optsSalaBola'"), 'tarjeta BOLA en SALA');
chk(c12.includes("arg === 'optsSalaBola'"), 'navegación permite optsSalaBola');
chk(c12.includes("case 'bola_skin': {"), 'dispatcher bola_skin');
chk(c12.includes("localStorage.setItem('pp_bolaskin', skB.id)"), 'elección persistida');
chk(c12.includes("this._mesaLockTxt(skB.lock) || T('mesa_lock_hint')"), 'candado avisado con el texto de casa');
chk(c12.includes('onPeerSkin(id) {'), 'onPeerSkin para la red');
chk(c12.includes("this.net.role === 'guest' && !this.mesaOcupada()"), 'sólo el INVITADO viste la skin del host (y el champ manda)');
chk(c12.includes('this._bolaTinte(bolaAspectoPorId(limpio))'), 'skin del rival sin candado (el host ya la desbloqueó)');

/* — 4 · c09 netlink ———————————————————————————————————————————— */
console.log('4 · c09_red_netlink.js · HELLO v2 con sk');
const c09 = lee('src/game/core/c09_red_netlink.js');
chk(c09.includes("sk: (this.game && typeof this.game.bolaSkin === 'string' && this.game.bolaSkin) || 'blanca'"), 'hello2 envía sk (con respaldo blanca)');
chk(c09.includes("const skR = (typeof m.sk === 'string') ? m.sk.slice(0, 24) : '';"), 'recepción saneada (corte 24)');
chk(c09.includes('this.game?.onPeerSkin?.(skR)'), 'entrega al juego con guardia opcional');
chk(c09.includes('try {\n          const skR'), 'skin envuelta en try (jamás rompe el enlace)');
chk(c09.includes('PPNET.verCompara(m.b, PPNET.VP.BUILD)'), 'PROTO/PHYS/BUILD intactos (verCompara sigue mandando)');

/* — 5 · c00 i18n ——————————————————————————————————————————————— */
console.log('5 · c00_pre_three.js · i18n ES/EN');
const c00 = lee('src/game/core/c00_pre_three.js');
const claves = ['bola_aspecto_lbl', 'cat_salabola', 'sub_bola_sub', 'bola_cosmetica', 'msg_bola_skin',
  'bola_asp_blanca', 'bola_asp_naranja', 'bola_asp_menta', 'bola_asp_estrellas', 'bola_asp_playa',
  'bola_asp_futbol', 'bola_asp_ocho', 'bola_asp_ojo', 'bola_asp_neon', 'bola_asp_holo',
  'bola_asp_disco', 'bola_asp_marte', 'bola_asp_luna', 'bola_asp_tierra', 'bola_asp_lava',
  'bola_asp_saturno'];
let i18nOk = true;
for (const k of claves) {
  const n = (c00.match(new RegExp(k + ':', 'g')) || []).length;
  if (n !== 2) { i18nOk = false; console.log(`      · ${k}: ${n} apariciones (deben ser 2 — ES y EN)`); }
}
chk(i18nOk, `las ${claves.length} claves nuevas están en ES y EN`);
chk(c00.includes("bola_cosmetica: 'Solo visual: la física de la bola NO cambia jamás'"), 'aviso cosmético ES');
chk(c00.includes("bola_cosmetica: 'Visual only: ball physics NEVER changes'"), 'aviso cosmético EN');
chk(c00.includes("bola_asp_saturno: 'Saturno'") && c00.includes("bola_asp_saturno: 'Saturn'"), 'Saturno ES/EN');

/* — 6 · física intacta —————————————————————————————————————————— */
console.log('6 · GARANTÍA · skins 100 % cosméticas');
const c04 = lee('src/game/core/c04_fisica_ccd.js');
const c05 = lee('src/game/core/c05_colisiones_ia_golpeo.js');
chk(!c04.includes('BOLA_ASPECTOS') && !c04.includes('bolaSkin') && !c04.includes('applyBallSkin'),
  'c04 (física CCD/Magnus) NO conoce las skins');
chk(!c05.includes('BOLA_ASPECTOS') && !c05.includes('bolaSkin') && !c05.includes('applyBallSkin'),
  'c05 (golpeo/colisión) NO conoce las skins');
chk(!c04.includes('pp_bolaskin') && !c05.includes('pp_bolaskin'), 'ninguna clave de skin en la física');

console.log(`\n${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
