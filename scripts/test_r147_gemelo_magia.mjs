#!/usr/bin/env node
/* =====================================================================
 * r147 · 12ª pasada · EL GEMELO DE MAGIA + C-F1 REAL (La Locura)
 * =====================================================================
 * r145 cerró C-F1 en La Locura «sobre el papel»: el cálculo de la
 * variante recordada leía this.arkanoid DENTRO de ArcadeArkanoid (campo
 * que no existe ahí — lo tiene el controlador) y el parámetro jamás
 * llegó a arkanoid.start(). El fix era un NO-OP y la segunda oportunidad
 * seguía derivando la variante de la etapa YA RESTAURADA.
 *
 * Este arnés ejecuta el CÓDIGO REAL de ambos campeonatos por extracción
 * (los ficheros son scripts de navegador, no módulos): se recorta el
 * método exacto del fichero y se corre con mocks — la prueba es
 * conductual, no sólo un grep. Cubre:
 *   1. locura · startArkanoid(varianteForzada): el param AHORA llega vivo
 *      a arkanoid.start() (y sobrevive al modal de instrucciones).
 *   2. locura · _afterResult: _lastVariant = this.variant (la instancia
 *      ES el arkanoid) → la 2ª oportunidad relanza la variante JUGADA,
 *      aunque la etapa restaurada sea 5 (campeón rejugando).
 *   3. locura · start(): la derivación de respeta el param forzado.
 *   4. magia · _afterResult (gemelo menor): startOrb(this._complex) —
 *      el campeón en etapa 5 que pierde la rejugada del orbe COMPLEJO
 *      repite el COMPLEJO, no el NORMAL (más fácil).
 *   5. Cableado estático: las líneas viejas muertas ya NO existen y los
 *      guard r144 / deriva de entrada (4057/4875) siguen intactos. */

import { readFileSync } from 'node:fs';

const LO = readFileSync('/home/z/my-project/public/championships/locura/index.js', 'utf8');
const MA = readFileSync('/home/z/my-project/public/championships/magia/index.js', 'utf8');

let ok = 0, fail = 0;
const chk = (c, l) => {
  console.log((c ? '  ✓ ' : '  ✗ FALLO: ') + l);
  ok += c ? 1 : 0; fail += c ? 0 : 1;
};

/** Extrae un método `name` de la fuente (clase con indentación de 2) y lo
 *  devuelve como función ejecutable con los globales libres inyectados. */
function extraerMetodo(fuente, nombre, globales = {}) {
  const re = new RegExp('\\n  ' + nombre + '\\(([^)]*)\\)\\s*\\{');
  const m = fuente.match(re);
  if (!m) throw new Error('método no encontrado: ' + nombre);
  const ini = m.index + 1;
  let prof = 0, fin = -1;
  for (let i = fuente.indexOf('{', ini); i < fuente.length; i++) {
    if (fuente[i] === '{') prof++;
    else if (fuente[i] === '}') { prof--; if (prof === 0) { fin = i + 1; break; } }
  }
  const cuerpo = fuente.slice(ini, fin);
  const nombres = Object.keys(globales);
  const fabrica = new Function(...nombres,
    'return function ' + cuerpo + ';');
  return { fn: fabrica(...nombres.map((k) => globales[k])), codigo: cuerpo };
}

/* ---------- 1 · locura · startArkanoid: el param llega VIVO --------- */
console.log('— F-M1a · locura: startArkanoid hilan el param (r147)');
{
  const { fn } = extraerMetodo(LO, 'startArkanoid', { GAME: undefined, T: undefined });
  let capturada = 'sin llamar';
  const self = {
    active: true, data: { id: 'locura' }, _instrK: 'ark', arkQueued: true,
    map: null,
    arkanoid: { start: (v) => { capturada = v; } },
  };
  fn.call(self, 1);
  chk(capturada === 1,
    `el param FORZADO llega vivo a arkanoid.start() (llegó ${String(capturada)})`);
  capturada = 'sin llamar';
  fn.call(self, undefined);
  chk(capturada === undefined,
    'sin param: undefined (la deriva de etapa queda aguas abajo, como siempre)');
}

/* ---------- 2 · locura · _afterResult: la variante JUGADA ----------- */
console.log('— F-M1b · locura: _afterResult recuerda la variante real');
{
  const { fn } = extraerMetodo(LO, '_afterResult');
  let relanzada = 'sin llamar';
  const self = {
    _lastWin: false, variant: 1,          // el campeón rejugó ARKANOID 1
    game: { rules: {}, audio: {}, rival: {} },
    stop() { /* apagado de nivel */ },
    ctrl: { stage: 5,                     // la etapa RESTAURADA (campeón)
      startArkanoid: (v) => { relanzada = v; } },
  };
  fn.call(self);
  chk(relanzada === 1,
    `la 2ª oportunidad relanza la variante JUGADA (1), no la derivada de la etapa restaurada 5 (llegó ${String(relanzada)})`);
  // y con la variante 2 jugada (orbe complejo equivalente)
  relanzada = 'sin llamar';
  const self2 = { ...self, variant: 2 };
  fn.call(self2);
  chk(relanzada === 2, 'con ARKANOID 2 jugado, la 2ª oportunidad es ARKANOID 2');
}

/* ---------- 3 · locura · start(): el forzado vence a la deriva ------ */
console.log('— F-M1c · locura: start() respeta varianteForzada');
{
  const m = LO.match(/this\.variant = varianteForzada \|\|\s*\n\s*\(\(this\.ctrl && this\.ctrl\.stage >= 3\) \? 2 : 1\);/);
  chk(!!m, 'la línea de deriva de start() está intacta (el forzado vence)');
  const varianteForzada = 1;
  const self = { ctrl: { stage: 5 } };
  (function () {
    const varianteForzada = 1;
    eval('this.variant = varianteForzada || ((this.ctrl && this.ctrl.stage >= 3) ? 2 : 1);');
  }).call(self);
  chk(self.variant === 1, 'campeón (stage 5) + forzado 1 → variante 1 (no 2)');
  const vf2 = undefined;
  const self2 = { ctrl: { stage: 5 } };
  (function () {
    const varianteForzada = vf2;
    eval('this.variant = varianteForzada || ((this.ctrl && this.ctrl.stage >= 3) ? 2 : 1);');
  }).call(self2);
  chk(self2.variant === 2, 'sin forzado + stage 5 → deriva 2 (entrada normal intacta)');
}

/* ---------- 4 · magia · _afterResult: gemelo menor ------------------ */
console.log('— F-M2 · magia: startOrb(this._complex), no stage restaurado');
{
  const { fn } = extraerMetodo(MA, '_afterResult', { T: undefined });
  let relanzada = 'sin llamar';
  const self = {
    _lastWin: false, _complex: true,      // rejugó el orbe COMPLEJO (etapa 3)
    stop() { /* */ },
    ctrl: { stage: 5,                     // etapa RESTAURADA (campeón)
      startOrb: (v) => { relanzada = v; }, _startDuel() { /* */ } },
  };
  fn.call(self);
  chk(relanzada === true,
    `campeón rejugando el orbe COMPLEJO: la 2ª oportunidad es COMPLEJA (llegó ${String(relanzada)})`);
  relanzada = 'sin llamar';
  const self2 = { ...self, _complex: false };
  fn.call(self2);
  chk(relanzada === false,
    'campeón rejugando el orbe NORMAL: la 2ª oportunidad es NORMAL (no se endurece sola)');
  // victoria → duelo siguiente (camino intacto)
  let duelo = false;
  const self3 = { _lastWin: true, _complex: true, stop() { /* */ },
    ctrl: { stage: 5, startOrb() { /* */ }, _startDuel() { duelo = true; } } };
  fn.call(self3);
  chk(duelo, 'victoria del orbe → duelo siguiente (camino normal intacto)');
}

/* ---------- 5 · cableado estático ----------------------------------- */
console.log('— cableado: lo muerto eliminado, lo vivo intacto');
{
  chk(LO.includes('startArkanoid(varianteForzada) {'),
    'locura · la firma de startArkanoid declara el param');
  chk(LO.includes('this.startArkanoid(varianteForzada);'),
    'locura · el callback del modal de instrucciones hila el param');
  chk(LO.includes('this.arkanoid.start(varianteForzada);'),
    'locura · arkanoid.start recibe el param (antes llegaba muerto)');
  chk(LO.includes('this._lastVariant = this.variant || undefined;'),
    'locura · _lastVariant lee la variante de la INSTANCIA (this)');
  chk(!LO.includes('this._lastVariant = (this.arkanoid && this.arkanoid.variant)'),
    'locura · la línea muerta r145 (this.arkanoid) ya NO existe');
  chk(LO.includes('if (a.stage <= 3) a._setStage(4);'),
    'locura · el guard r144 (stage≥4 jamás rebaja) sigue intacto');
  chk(MA.includes('this.ctrl.startOrb(this._complex); return;'),
    'magia · _afterResult relanza con la variante JUGADA (this._complex)');
  chk(!MA.includes('this.ctrl.startOrb(this.ctrl.stage === 3)'),
    'magia · la deriva por etapa restaurada ya NO existe en _afterResult');
  chk((MA.match(/this\.startOrb\(this\.stage === 3\);/g) || []).length === 2,
    'magia · las entradas normales (cola 4057 · rejugada 4875) siguen derivando por etapa CORRECTAMENTE');
  chk(MA.includes('this._complex = !!complex;'),
    'magia · startOrb sigue sellando _complex (fuente de verdad de la variante)');
}

console.log(fail === 0
  ? `✓ GEMELO MAGIA + C-F1 REAL: ${ok} OK · la segunda oportunidad repite SIEMPRE la prueba jugada`
  : `✗ GEMELO MAGIA + C-F1 REAL: ${ok} OK · ${fail} FALLO(S)`);
process.exit(fail === 0 ? 0 : 1);
