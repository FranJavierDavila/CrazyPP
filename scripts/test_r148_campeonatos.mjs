#!/usr/bin/env node
/* =====================================================================
 * r148 · 13ª pasada · REPASO INTENSIVO de los 4 campeonatos restantes
 * =====================================================================
 * Barrido del patrón C-F1 (2ª oportunidad/rejugada que deriva la variante
 * de la etapa YA RESTAURADA) por estacion_orbital, valle_neon, halloween
 * y oeste — lectura completa de sus ciclos de rejugada, derrota y avance.
 *
 * Resultado del barrido: estacion/valle limpios (sin 2ª oportunidad
 * automática: vuelven a la sala y cada arranque re-deriva en start()).
 * Pero la lectura destapó F-O1 en HALLOWEEN: onMatchOver sólo llamaba
 * _stageClear si GANABAS — una rejugada de DUELO perdida dejaba el _replay
 * pegado y la victoria real siguiente entraba por la rama de rejugada de
 * _stageClear (el avance legítimo se perdía). _finPrueba ya llamaba
 * _stageClear con win O derrota en las PRUEBAS: el duelo era el agujero.
 * FIX r148: _stageClear(this.dueloIdx, won, 'duelo') SIEMPRE.
 *
 * Este arnés ejecuta el CÓDIGO REAL por extracción (mismo método que
 * test_r147): los métodos se recortan del fuente y se corren con mocks —
 * conductual, no un grep. Escenarios:
 *   A. halloween · F-O1: derrota de duelo EN REJUGADA → _replay limpio y
 *      etapa real restaurada en storage (con el código viejo quedaba pegado).
 *   B. halloween · derrota de duelo normal → _stageClear retorna sin
 *      efectos (cero escrituras, sin avance) — la fix no cambia el camino.
 *   C. halloween · victoria de duelo en rejugada → restaura (sin avance).
 *   D. halloween · victoria normal → avanza a idx+1.
 *   E. halloween · rejugada ganada por CAMPEÓN en modo leyenda → sello
 *      leyenda_n + restauración (el sello usa el idx almacenado).
 *   F. oeste · _endPrueba DERROTA en rejugada → restaura en MEMORIA y NO
 *      escribe storage (la entrada de rejugada tampoco escribe: consistente).
 *   G. oeste · _endPrueba VICTORIA en rejugada → _stageClear real restaura
 *      Y PERSISTE (defensivo; el storage ya tenía la etapa real).
 *   H. oeste · replayLaunch: campeón (etapa 5) rejugando el nodo 2 →
 *      _replayReal=5 + _startAsedio (dificultad del nodo rejugado).
 *   I. oeste · replayLaunch: nodo VIGENTE sin ser campeón → serveTrigger,
 *      sin rejugada. */

import { readFileSync } from 'node:fs';

const HA = readFileSync('/home/z/my-project/public/championships/halloween/index.js', 'utf8');
const OE = readFileSync('/home/z/my-project/public/championships/oeste/index.js', 'utf8');

let ok = 0, fail = 0;
const chk = (c, l) => {
  console.log((c ? '  ✓ ' : '  ✗ FALLO: ') + l);
  ok += c ? 1 : 0; fail += c ? 0 : 1;
};

function extraerMetodo(fuente, nombre) {
  const re = new RegExp('\\n  ' + nombre + '\\(([^)]*)\\)\\s*\\{');
  const m = fuente.match(re);
  if (!m) throw new Error('método no encontrado: ' + nombre);
  const ini = m.index + 1;
  let prof = 0, fin = -1;
  for (let i = fuente.indexOf('{', ini); i < fuente.length; i++) {
    if (fuente[i] === '{') prof++;
    else if (fuente[i] === '}') { prof--; if (prof === 0) { fin = i + 1; break; } }
  }
  return fuente.slice(ini, fin);
}

function fabricar(nombre, fuente, globales) {
  const nombres = Object.keys(globales);
  const f = new Function(...nombres, 'return function ' + extraerMetodo(fuente, nombre) + ';');
  return f(...nombres.map((k) => globales[k]));
}

/* ---------- storage simulado (cuenta escrituras) -------------------- */
function storageInicial() {
  const datos = { stage: '4', rank: '[]' };
  const escrituras = [];
  const sGet = (k) => (k in datos ? datos[k] : null);
  const sSet = (k, v) => { escrituras.push([k, v]); datos[k] = v; };
  return { datos, escrituras, sGet, sSet };
}

/* ---------- halloween: onMatchOver + _stageClear REALES ------------- */
function halloween() {
  const st = storageInicial();
  const glob = {
    sGet: st.sGet, sSet: st.sSet, tx: () => 'x', SFX: null,
    telemetria: () => {}, rankingMundial: () => {}, CORE: null, MAN: { id: 'hal' },
  };
  const onMatchOver = fabricar('onMatchOver', HA, glob);
  const stageClear = fabricar('_stageClear', HA, glob);
  const base = () => ({
    dueloVivo: true, dueloIdx: 1,
    man: { id: 'hal' },
    _replay: null, _leyendaOn: false,
    game: { rules: { scorePlayer: 7, scoreAi: 3 } },
    rival: { final() {} },
    camino: { leyenda: { activa: true } },
    isChampion() { return false; },
    totalEtapas() { return 99; },
    _refrescaCartel() {}, _championFlow() {}, _leyendaFlow() {},
    _sellos() { return 0; }, haptic() {},
    puntos() { return 120; }, duelwins() { return 3; },
    _puntosAdd() {},
    salaLlamadas: 0, sala() { this.salaLlamadas++; },
  });
  return { onMatchOver, stageClear, base, st };
}

console.log('— F-O1 · halloween: la rejugada de DUELO perdida restaura (fix r148)');
{
  const { onMatchOver, stageClear, base, st } = halloween();
  const self = base();
  self._stageClear = stageClear;
  self._replay = { real: 4 };                 // campeón rejugando una etapa vieja
  onMatchOver.call(self, 'ai');               // el núcleo envía 'ai' (c06:513)
  chk(self._replay === null && st.datos.stage === '4',
    `A · derrota de duelo en REJUGADA: _replay limpio y stage real restaurado (replay=${String(self._replay)}, stage=${st.datos.stage})`);
  chk(!self.dueloVivo, 'A · el duelo queda cerrado');
  chk(self.salaLlamadas === 1, 'A · la sala retoma el control');
}
{
  const { onMatchOver, stageClear, base, st } = halloween();
  const self = base();
  self._stageClear = stageClear;
  const antes = st.escrituras.length;
  onMatchOver.call(self, 'ai');               // derrota NORMAL (sin rejugada)
  chk(!st.escrituras.slice(antes).some(([k]) => k === 'stage') && st.datos.stage === '4',
    'B · derrota de duelo NORMAL: cero escrituras de stage y la etapa se repite (la fix no cambia el camino)');
}
{
  const { onMatchOver, stageClear, base, st } = halloween();
  const self = base();
  self._stageClear = stageClear;
  self._replay = { real: 4 };
  onMatchOver.call(self, 'player');           // victoria en rejugada
  chk(self._replay === null && st.datos.stage === '4',
    'C · victoria de duelo en rejugada: restaura el progreso real (sin avance)');
}
{
  const { onMatchOver, stageClear, base, st } = halloween();
  const self = base();
  self._stageClear = stageClear;
  self.dueloIdx = 1;
  onMatchOver.call(self, 'player');           // victoria NORMAL
  chk(st.datos.stage === '2',
    'D · victoria de duelo normal: avanza a la etapa siguiente (stage=2)');
}
{
  const { onMatchOver, stageClear, base, st } = halloween();
  const self = base();
  self._stageClear = stageClear;
  self.isChampion = () => true;               // campeón en modo LEYENDA
  self._leyendaOn = true;
  self._replay = { real: 4 };
  self.dueloIdx = 1;
  onMatchOver.call(self, 'player');           // rejugada ganada como campeón
  chk(st.datos.leyenda_2 === '1' && st.datos.stage === '4' && self._replay === null,
    'E · rejugada ganada en modo leyenda: sello leyenda_2 + restauración (idx almacenado)');
}

/* ---------- oeste: _endPrueba + _stageClear + replayLaunch ---------- */
console.log('— oeste: ciclo de rejugada (memoria vs storage)');
{
  const st = storageInicial();
  const glob = {
    clamp: (v, a, b) => Math.max(a, Math.min(b, v)), tx: () => 'x',
    STATE_NAME: 'sala', ARBUSTO: { x: 0, z: 0 }, OESTE: { x: 0, z: 0 },
    sGet: st.sGet, sSet: st.sSet, SFX: null,
    localStorage: { setItem: (k, v) => st.sSet(k, v), getItem: (k) => st.sGet(k) },
  };
  const endPrueba = fabricar('_endPrueba', OE, glob);
  const stageClear = fabricar('_stageClear', OE, glob);
  const base = () => ({
    stage: 2, _replayReal: 5, _leyendaOn: false, _armT: 0,
    _netParts: [], _gunMuzzle: null,
    _freeGunApply() {}, _gunVisible() {},
    mapa: { visible: false, refresh() {} }, cartel: { visible: false },
    sprite: { visible: false, position: { set() {} }, rotation: { z: 0 } }, spriteBaseY: 0,
    arbustoGroup: { visible: false, position: { set() {} } },
    arbustoSombra: { position: { set() {} } },
    game: { rules: { state: '', message: '' }, ball: {}, audio: { announce() {} },
      renderer: { xr: { isPresenting: false } },
      scoreboardGroup: { visible: false }, roomGroup: { visible: false },
      champDecor: null, aiPaddleMesh: { visible: false } },
    setState() {}, _parkMainBall() {}, paintCartel() {}, musicOn() {},
    _refreshMap() {}, _stageClear() {}, _sellosLeyenda() { return 0; },
    _leyendaFlow() {}, _setStateSilent() {}, sfx() {}, haptic() {},
    storageKey(k) { return 'pp_arcade_' + k; },
  });
  // F · derrota en rejugada: restaura en MEMORIA, cero escrituras
  const self = base();
  endPrueba.call(self, false, 2);
  chk(self.stage === 5 && self._replayReal === null,
    `F · _endPrueba(false) en rejugada: stage vuelve a 5 en memoria (stage=${self.stage})`);
  const escribioStage = st.escrituras.some(([k]) => /stage/.test(k));
  chk(!escribioStage,
    'F · y NO escribe storage (la entrada de rejugada tampoco escribió: siempre estuvo bien)');
  // G · victoria en rejugada: _stageClear real restaura Y persiste
  const self2 = base();
  self2._stageClear = stageClear;
  endPrueba.call(self2, true, 2);
  chk(self2.stage === 5 && st.datos['pp_arcade_stage'] === '5',
    `G · _endPrueba(true) en rejugada: _stageClear real restaura y persiste (stage=${st.datos['pp_arcade_stage']})`);
  // H · replayLaunch del campeón (nodo 2 = asedio)
  const self3 = base();
  self3.stage = 5; self3._champion = true; self3._replayReal = null;
  let lanzado = '';
  self3._startAsedio = () => { lanzado = 'asedio'; };
  self3._startTren = () => { lanzado = 'tren'; };
  self3._startDuel = () => { lanzado = 'duelo'; };
  self3.serveTrigger = () => { lanzado = 'serve'; };
  const replayLaunch = fabricar('replayLaunch', OE, glob);
  replayLaunch.call(self3, 1);                // nodo 2 (idx 1)
  chk(self3._replayReal === 5 && self3.stage === 2 && lanzado === 'asedio',
    `H · campeón rejugando el nodo 2: _replayReal=5, stage=2, asedio con su dificultad (${lanzado})`);
  // I · nodo VIGENTE sin ser campeón: sin rejugada
  const self4 = base();
  self4.stage = 2; self4._champion = false; self4._replayReal = null;
  let libre = '';
  self4._startAsedio = () => { libre = 'asedio'; };
  self4._startTren = () => { libre = 'tren'; };
  self4._startDuel = () => { libre = 'duelo'; };
  self4.serveTrigger = () => { libre = 'serve'; };
  replayLaunch.call(self4, 1);                // mismo nodo vigente
  chk(self4._replayReal === null && libre === 'serve',
    'I · nodo vigente sin ser campeón: serveTrigger, sin modo rejugada');
}

/* ---------- cableado estático --------------------------------------- */
console.log('— cableado: la fix r148 queda amarrada');
{
  chk(HA.includes("this._stageClear(this.dueloIdx, won, 'duelo');"),
    'halloween · onMatchOver llama _stageClear SIEMPRE (win o derrota)');
  chk(!HA.includes('if (won) this._stageClear(this.dueloIdx, true'),
    'halloween · la llamada condicional vieja ya NO existe');
  chk(HA.includes('if (!gana) return;'),
    'halloween · el retorno sin efectos en derrota normal sigue intacto');
}

console.log(fail === 0
  ? `✓ REPASO INTENSIVO r148: ${ok} OK · F-O1 amarrado y ciclo de rejugada de oeste verificado`
  : `✗ REPASO INTENSIVO r148: ${ok} OK · ${fail} FALLO(S)`);
process.exit(fail === 0 ? 0 : 1);
