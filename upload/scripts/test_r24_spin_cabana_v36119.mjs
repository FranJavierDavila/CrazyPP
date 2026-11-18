#!/usr/bin/env node
/* CRAZY PING PONG · r24 · v3.6.119 · TEST: SPIN REALISTA + HALL CABAÑA.
 * Las dos peticiones del dueño tras probar la r23 en el visor:
 *
 *   1 · «EL GIRO ES MUY SUTIL Y POCO REALISTA, al dar efecto no se nota
 *        el spin que debería tener la bola» — DOS causas y DOS curas:
 *        · Ganancia 0.14 → 0.45 (c12): |ω|=110 (tope) ≈ 7,9 rev/s
 *          (39,5°/frame a 72 Hz, bajo el umbral de estrobo); |ω|=25
 *          (EFECTO_SPIN_MIN) ≈ 1,8 rev/s; efecto medio ≈ 4,3 rev/s.
 *        · Textura (c07/c02): las 4 skins planas (blanca/naranja/menta/
 *          neón) eran COLOR LISO — una esfera uniforme no delata su ω
 *          NI a 8 rev/s. bolaTex les pinta COSTURA ecuatorial + MARCA
 *          «CRAZY» (dos caras opuestas, como las bolas de fábrica).
 *        · GARANTÍA DE SIEMPRE: c04/c05 (física) siguen sin conocer el
 *          mesh, el render ni el hall — cero referencias nuevas.
 *
 *   2 · HALLCABANA.ZIP → «imágenes para crear un Hall nuevo que se
 *        libere con algún logro» — HALL CABAÑA (v3.6.119):
 *        · c02: HALL_VARIANTES (museo 'anfitrion' + 'cabana' lock wins10,
 *          bases de arte assets/hall/ y assets/hall/cabana/) +
 *          hallVariantePorId().
 *        · c08: createHall(base) viste la carpeta que toque · vestir()
 *          re-viste EN VIVO (dispose del arte anterior) · applyHallVariant
 *          exportada (no-op seguro).
 *        · c12: LS 'pp_hallvar' + _hallVarLS/_hallVarDef (candado
 *          _mesaLibre, patrón skin de bola) · createHall(this._hallVarDef()
 *          .base) en el constructor · enterHall elige arte (local → tuyo;
 *          visita online → LA DEL ANFITRIÓN vía hp.hv saneado) · tarjeta
 *          salahall con fila de variantes (🔒 si cerrada; oculta de
 *          visita) · case 'hall_var' (guarda + re-viste + mensaje) ·
 *          hints hall_var:anfitrion / hall_var:cabana.
 *        · RED (patrón sk/hp — cero cambios en c09): hallProfile() lleva
 *          hv (id de catálogo) · onPeerHall lo SANEA (H_OK) y, si el
 *          invitado está dentro del hall, re-viste AL VUELO.
 *        · ASSETS: 6 JPG reales del dueño (frente/fondo/izquierda/derecha/
 *          suelo/techo) en public/assets/hall/cabana/ con las proporciones
 *          EXACTAS de los planos del hall (1849×864 · 2395×864 · 1296×1678).
 *        · c00: 6 claves nuevas ES/EN.
 *
 * Uso: node --no-warnings scripts/test_r24_spin_cabana_v36119.mjs
 */
import { BOLA_ASPECTOS, HALL_VARIANTES, hallVariantePorId } from '../src/game/core/c02_cfg_escena.js';
import { readFileSync, existsSync, statSync } from 'node:fs';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');

/* — 1 · SPIN REALISTA · ganancia y tick intactos (c12) ————————————— */
console.log('1 · SPIN REALISTA · ganancia ×3.2 (c12)');
const c12 = lee('src/game/core/c12_pingponggame.js');
chk(c12.includes('BOLA_TUNE = { spinGanancia: 0.45 }') &&
    c12.includes('const BOLA_SPIN_GANANCIA = BOLA_TUNE.spinGanancia;'), 'ganancia 0.45 (|ω|=110 → ~7,9 rev/s · |ω|=25 → ~1,8 rev/s) — r56: dato en BOLA_TUNE');
chk(!c12.includes('BOLA_SPIN_GANANCIA = 0.14') && !c12.includes('spinGanancia: 0.14'), 'no queda rastro de la 0.14');
chk(c12.includes('m.rotateOnWorldAxis(BOLA_SPIN_AX, w * dt * BOLA_SPIN_GANANCIA);'), 'rotateOnWorldAxis sobre el ω real (sin tocar)');
chk(c12.includes('if (w < 0.5) return;'), 'reposo honesto intacto');
chk(c12.includes('r24 (v3.6.119) · «EL GIRO ES MUY SUTIL Y POCO REALISTA»'), 'comentario de la ronda junto al tick');

/* — 2 · SPIN LEGIBLE · textura de las planas (c02 + c07) ———————————— */
console.log('2 · SPIN LEGIBLE · costura + marca CRAZY en las 4 planas');
const c02 = lee('src/game/core/c02_cfg_escena.js');
const c07 = lee('src/game/core/c07_escena_sala.js');
for (const id of ['blanca', 'naranja', 'menta', 'neon']) {
  const s = BOLA_ASPECTOS.find((x) => x.id === id);
  chk(s && s.tex === id, `c02 · skin '${id}' lleva tex propia (ya no color liso)`);
  chk(c07.includes(`tipo === '${id}'`), `c07 · bolaTex pinta '${id}'`);
}
chk(c07.includes('CRAZY'), 'c07 · marca de fábrica CRAZY (como las bolas reales)');
chk(c07.includes("c.strokeStyle = 'rgba(58,50,42,0.32)'; c.lineWidth = 3;\n    c.beginPath(); c.moveTo(0, 128); c.lineTo(512, 128); c.stroke();"), 'c07 · costura ecuatorial (poliplástico)');
const ids4 = new Set(['blanca', 'naranja', 'menta', 'neon']);
chk(BOLA_ASPECTOS.every((s) => ids4.has(s.id) ? !!s.tex : true), 'ninguna skin de bola queda sin textura');
chk(c02.includes("id: 'blanca', lock: null") && c02.includes("BOLA_ID_OFICIAL = BOLA_ASPECTOS[0].id"), 'la oficial sigue siendo blanca (regla del dueño intacta)');

/* — 3 · FÍSICA INTACTA (garantía de la casa) ———————————————————————— */
console.log('3 · FÍSICA INTACTA · c04/c05 sin render ni hall');
const c04 = lee('src/game/core/c04_fisica_ccd.js');
const c05 = lee('src/game/core/c05_colisiones_ia_golpeo.js');
for (const [nombre, src] of [['c04', c04], ['c05', c05]]) {
  chk(!src.includes('ballMesh'), `${nombre}: no conoce ballMesh`);
  chk(!src.includes('rotateOnWorldAxis'), `${nombre}: no rota meshes`);
  chk(!src.includes('HALL_VARIANTES') && !src.includes('pp_hallvar'), `${nombre}: no conoce el hall variant`);
  chk(!src.includes('applyHallVariant'), `${nombre}: no re-viste nada`);
}

/* — 4 · HALL CABAÑA · catálogo (c02) ————————————————————————————————— */
console.log('4 · HALL CABAÑA · catálogo HALL_VARIANTES (c02)');
chk(Array.isArray(HALL_VARIANTES) && HALL_VARIANTES.length === 6, '6 variantes (re-anclada r38: museo + cabaña + neón + orbital + dojo + rascacielos)');
chk(HALL_VARIANTES[0].id === 'anfitrion' && HALL_VARIANTES[0].lock === null && HALL_VARIANTES[0].base === 'assets/hall/', "'anfitrion': museo clásico, sin candado, arte base");
chk(HALL_VARIANTES[1].id === 'cabana' && HALL_VARIANTES[1].lock === 'wins10', "'cabana' se libera con el logro wins10 (10 victorias — o 6★)");
chk(HALL_VARIANTES[1].base === 'assets/hall/cabana/', "'cabana' apunta a su carpeta de arte");
chk(hallVariantePorId('cabana').id === 'cabana' && hallVariantePorId('no-existe').id === 'anfitrion', 'hallVariantePorId: fallback honesto al museo');
chk(c02.includes('r24 (v3.6.119) · VARIANTES DEL HALL DEL ANFITRIÓN'), 'comentario de la ronda en c02');

/* — 5 · HALL CABAÑA · re-vestido en vivo (c08) —————————————————————— */
console.log('5 · HALL CABAÑA · createHall(base) + applyHallVariant (c08)');
const c08 = lee('src/game/core/c08_hall_hud.js');
chk(c08.includes('export function createHall(base) {'), 'createHall admite la base de arte');
chk(c08.includes("const vbase = (typeof base === 'string' && base) ? base : 'assets/hall/';"), 'base con respaldo honesto al museo');
chk(c08.includes("front: vbase + 'frente.jpg'"), 'las 6 rutas nacen de la base');
chk(c08.includes('const vestir = (b) => {'), 'vestir(): re-vestido sin reconstruir el grupo');
chk(c08.includes("texPaths.front = b + 'frente.jpg';"), 'vestir() repinta las 6 claves');
chk(c08.includes('if (texs[key] && texs[key] !== tex && texs[key].dispose) {'), 'el arte anterior se libera (dispose, sin fugas)');
chk(c08.includes('base: vbase, vestir,'), 'userData.hall lleva base + vestir');
chk(c08.includes('export function applyHallVariant(g, base) {'), 'applyHallVariant exportada');
chk(c08.includes('if (typeof base !== \'string\' || !base || ud.base === base) return false;'), 'no-op seguro (cadena inválida o igual)');

/* — 6 · HALL CABAÑA · juego, LS y candado (c12) ————————————————————— */
console.log('6 · HALL CABAÑA · LS, candado y entrada (c12)');
chk(c12.includes("_hallVarLS() {\n    try { return localStorage.getItem('pp_hallvar') || ''; } catch { return ''; }\n  }"), "LS 'pp_hallvar' con guardia");
chk(c12.includes('_hallVarDef() {'), '_hallVarDef: variante validada');
chk(c12.includes('if (hv.lock && !this._mesaLibre(hv.lock)) hv = HALL_VARIANTES[0];'), 'candado _mesaLibre: sin 10 victorias → museo (patrón skin de bola)');
chk(c12.includes('this.hallGroup = createHall(this._hallVarDef().base);   // r24'), 'el constructor nace ya vestido con TU variante');
chk(c12.includes('const hvTgt = (online && this._hallPeer && this._hallPeer.hv)'), 'enterHall elige arte: local → tuyo · visita → el del anfitrión');
chk(c12.includes('try { applyHallVariant(this.hallGroup, hvTgt.base); } catch (eHV) { /* */ }'), 're-vestido en enterHall (a prueba de fallos)');
chk(c12.includes("case 'hall_var': {"), "case 'hall_var' en el dispatcher");
chk(c12.includes("try { localStorage.setItem('pp_hallvar', hv.id); } catch { /* */ }"), 'elección persistente');
chk(c12.includes('try { applyHallVariant(this.hallGroup, hv.base); } catch (eHV) { /* */ }'), 'al elegir se re-viste EN VIVO');
chk(c12.includes("if (hv.lock && !this._mesaLibre(hv.lock)) {"), "candado en el handler (mensaje de _mesaLockTxt)");
chk(c12.includes("btn('hall_var:' + v.id, 56 + (i % 3) * 312,"), 'rejilla de variantes en salahall (3 col — re-anclada r26b: 5 halls)');
chk(c12.includes("(libreH ? '' : '🔒 ') + T(v.nameKey)"), 'candado visible en la UI');
chk(c12.includes('if (!per.peer) {') && c12.includes("label(T('hall_var_lbl')"), 'selector oculto de visita (el arte manda el anfitrión)');
chk(c12.includes("'hall_var:anfitrion': 'hint_hall_var_a', 'hall_var:cabana': 'hint_hall_var_c',"), 'hints de las dos variantes');

/* — 7 · HALL CABAÑA · RED (patrón sk/hp, c09 sin tocar) ————————————— */
console.log('7 · HALL CABAÑA · hv viaja en hp (saneado)');
const c09 = lee('src/game/core/c09_red_netlink.js');
chk(c12.includes('hv: this._hallVarDef().id,   // r24'), 'hallProfile() envía hv (id de catálogo)');
chk(c09.includes("this.game.hallProfile() : undefined"), 'c09 sigue pasando hp entero (cero cambios de códec)');
chk(c12.includes('const H_OK = HALL_VARIANTES.map((v) => v.id);   // r24'), 'saneo: H_OK contra catálogo');
chk(c12.includes("hv: (typeof hp.hv === 'string' && H_OK.indexOf(hp.hv) >= 0) ? hp.hv : '',"), 'hv saneado (string de catálogo o vacío)');
chk(c12.includes('try { applyHallVariant(this.hallGroup, hallVariantePorId(this._hallPeer.hv).base); } catch (eHV) { /* */ }'), 'de visita dentro del hall: el arte cambia AL VUELO con el hello');

/* — 8 · ASSETS · las 6 imágenes del dueño ——————————————————————————— */
console.log('8 · ASSETS · public/assets/hall/cabana/');
const cab = 'public/assets/hall/cabana/';
const esperado = {
  'frente.jpg': [1849, 864], 'fondo.jpg': [1849, 864],
  'izquierda.jpg': [2395, 864], 'derecha.jpg': [2395, 864],
  'suelo.jpg': [1296, 1678], 'techo.jpg': [1296, 1678],
};
for (const [f, dims] of Object.entries(esperado)) {
  const p = raiz + cab + f;
  const hay = existsSync(p);
  const sz = hay ? statSync(p).size : 0;
  chk(hay && sz > 50000 && sz < 900000, `${f} presente y comprimido (${(sz / 1024) | 0} KB)`);
  if (hay) {
    const buf = readFileSync(p);
    const esJpg = buf[0] === 0xFF && buf[1] === 0xD8;
    chk(esJpg, `${f} es JPEG real`);
    // dimensiones del SOI (marcador SOF0/2): las proporciones EXACTAS de los planos
    let w = 0, h = 0;
    for (let i = 2; i < buf.length - 9; i++) {
      if (buf[i] !== 0xFF) continue;
      const m = buf[i + 1];
      if (m === 0xC0 || m === 0xC2) {
        h = buf.readUInt16BE(i + 5); w = buf.readUInt16BE(i + 7); break;
      }
    }
    chk(w === dims[0] && h === dims[1], `${f} mantiene ${dims[0]}×${dims[1]} (mapeo 1:1 del plano)`);
  }
}
chk(!c08.includes("load('assets/hall"), 'el bundle NO hardcodea arte (toda carga va por texPaths/catálogo)');
chk(!c12.includes('assets/hall/cabana'), 'c12 no hardcodea rutas de arte (fuente única: c02)');

/* — 9 · I18N · 6 claves nuevas ES/EN ————————————————————————————————— */
console.log('9 · I18N · ES/EN (c00)');
const c00 = lee('src/game/core/c00_pre_three.js');
const claves = ['hall_var_lbl', 'hall_var_anfitrion', 'hall_var_cabana', 'msg_hall_var', 'hint_hall_var_a', 'hint_hall_var_c'];
for (const k of claves) {
  const n = c00.split(k + ':').length - 1;
  chk(n === 2, `${k} existe en ES y EN (${n}/2)`);
}
chk(c00.includes('hall_var_cabana: ' + "'LA CABAÑA'"), "ES: 'LA CABAÑA'");
chk(c00.includes('hall_var_cabana: ' + "'THE CABIN'"), "EN: 'THE CABIN'");
chk(c00.includes("hint_hall_var_c: 'La Cabaña: chimenea, barra y nieve — se libera con 10 victorias'"), 'ES: el hint cuenta el logro que la libera');

/* — 10 · FASE · versión ————————————————————————————————————————————— */
console.log('10 · SELLOS');
chk(c12.includes('r24 (v3.6.119)'), 'c12 sellado a la ronda');

console.log(`\nR24 · ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
