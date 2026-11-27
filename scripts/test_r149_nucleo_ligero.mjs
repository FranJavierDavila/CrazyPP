#!/usr/bin/env node
/* =====================================================================
 * r149 · 14ª pasada · REPASO INTENSIVO de TODO EL JUEGO (núcleo ligero)
 * =====================================================================
 * Territorio sin auditoría profunda reciente: c03 (audio/voz), c07
 * (escena sala), c06 (motor de reglas — releído completo, curtido r79-97)
 * y c11 (champloader — leaveAll/intros/resetRecords, sin defectos). El
 * barrido amplio del subagente sobre c01/c02/c03/c07 devolvió DOS
 * hallazgos verificados contra sus llamadores (c12/c13):
 *
 *   F-A1 [BUG REAL · c03]: startHallMusic CONSUMÍA la petición de música
 *   del menú (setMusicWanted(false) destruye musicWanted) y la rama de
 *   restauración del icono de mute de la pared (setHallMute → «el aire
 *   vuelve al menú SOLO si él ya lo había pedido») quedaba MUERTA para
 *   ese flujo: silenciar el salón ya no devolvía el aire al menú aunque
 *   el menú estuviera abierto delante del jugador. FIX: recordar la
 *   petición (_menuReq) al consumirla, re-ARMARLA (setMusicWanted(true))
 *   al silenciar el salón, y expirarla al salir del salón o al pedir el
 *   menú una petición fresca.
 *
 *   F-A2 [RIESGO · c07]: vaivén de los troqueles sin guard — un pack
 *   externo de campeonato sin `sway` en decor.pieces producía
 *   0.006 * undefined = NaN en rotation.z CADA FRAME (matriz corrupta
 *   silenciosa, el mismo patrón NaN que el repo ya cazó en panNode).
 *
 * Este arnés ejecuta el CÓDIGO REAL por extracción (mismo método r147/
 * r148): la máquina de música completa de c03 (startHallMusic,
 * stopHallMusic, setHallMute, setHallWanted, setMusicWanted, startMusic,
 * stopMusic) cableada sobre un AudioContext simulado, y el guard de sway
 * (estático + expresión). Escenarios:
 *   A. EL BUG: salón retira el aire del menú → mute de la pared LO DEVUELVE
 *      (antes: musicWanted destruido → rama muerta → menú mudo).
 *   B. petición fresca del menú sustituye a la recuerda del salón.
 *   C. salir del salón EXPIRA la recuerda (sin resurrección fuera de contexto).
 *   D. musicOn=false bloquea la restauración (el maestro manda).
 *   E. mute sin petición previa del menú: nada se inventa.
 *   F. no-regresión: reactivar el icono vuelve a levantar el salón.
 *   G. guard de sway: ausente → 0.5 · cero explícito → 0 · 0.9 → 0.9. */

import { readFileSync } from 'node:fs';

const C03 = readFileSync('/home/z/my-project/src/game/core/c03_audio_voz.js', 'utf8');
const C07 = readFileSync('/home/z/my-project/src/game/core/c07_escena_sala.js', 'utf8');

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

function audio() {
  const CONFIG_AUDIO = {
    salon: { base: 0.30, entradaS: 1.0, salidaS: 1.0 },
    musica: { base: 0.42, entradaS: 0.9, salidaS: 1.2 },
  };
  const gan = () => ({
    gain: { value: 0, setValueAtTime() {}, linearRampToValueAtTime() {}, cancelScheduledValues() {} },
    connect() {},
  });
  const ctx = {
    currentTime: 0,
    createGain: gan,
    createBufferSource: () => ({ buffer: null, loop: false, connect() {}, start() {} }),
  };
  const glob = {
    CONFIG_AUDIO,
    localStorage: { setItem() {}, getItem() { return null; } },
    window: { setTimeout() {} },
  };
  const nombres = Object.keys(glob);
  const f = (nm) => new Function(...nombres, 'return function ' + extraerMetodo(C03, nm) + ';')(
    ...nombres.map((k) => glob[k]));

  const self = {
    ctx, master: {},
    musicOn: true, musicWanted: false, musicPlaying: false, musicVol: 1,
    hallWanted: false, hallMute: false, hallPlaying: false, hallVol: 1,
    _hallUrl: null, _hallBufs: {}, _musicBuf: { b: 1 }, _arcDucked: false,
    _menuReq: false,
    kick() {},
    setArcDuck() { this._arcDucked = true; },
    _loadMusic() {},
  };
  for (const nm of ['startHallMusic', 'stopHallMusic', 'setHallMute', 'setHallWanted',
    'setMusicWanted', 'startMusic', 'stopMusic']) self[nm] = f(nm);
  return self;
}

/* el flujo del BUG: menú sonando + elegir salón con pista + silenciar */
function flujoBug(s) {
  s.musicWanted = true; s.musicPlaying = true;      // menú abierto: aire vivo
  s.setHallWanted(true, 'assets/hall/neon/arcade.mp3'); // picker: salón con pista
  s._hallBufs[s._hallUrl] = { b: 1 };               // pista ya descargada
  s.startHallMusic();                               // entra el salón
  return s;
}

console.log('— F-A1 · c03: la máquina de música REAL (menu ↔ salón ↔ icono)');
{
  const s = audio();
  flujoBug(s);
  chk(s.hallPlaying === true && s.musicWanted === false && s._menuReq === true,
    'A1 · el salón retira el aire del menú RECUERDANDO la petición (_menuReq)');
  s.setHallMute(true);                              // icono de la pared
  chk(s.hallPlaying === false,
    'A1 · el icono silencia el salón');
  chk(s.musicWanted === true && s.musicPlaying === true,
    `A1 · EL AIRE VUELVE al menú (musicWanted=${s.musicWanted}, musicPlaying=${s.musicPlaying}) — antes quedaba mudo`);
  chk(s._menuReq === false, 'A1 · la recuerda se consume al restaurar');
}
{
  const s = audio();
  flujoBug(s);
  s.setMusicWanted(true);                           // el menú lo pide fresco
  chk(s._menuReq === false && s.musicPlaying === false,
    'B · petición fresca sustituye a la recuerda; con el salón sonando el guard UNA MELODÍA la rechaza (prioridad del dueño)');
}
{
  const s = audio();
  flujoBug(s);
  s.setHallWanted(false);                           // abandona el salón
  chk(s._menuReq === false && s.hallPlaying === false,
    'C · salir del salón EXPIRA la recuerda');
  s.setHallMute(true);
  chk(s.musicPlaying === false,
    'C · fuera de contexto el icono NO resucita música que el menú ya no pide');
}
{
  const s = audio();
  flujoBug(s);
  s.musicOn = false;                                // maestro de música OFF
  s.setHallMute(true);
  chk(s.musicPlaying === false,
    'D · musicOn=false bloquea la restauración (el maestro manda)');
}
{
  const s = audio();
  s.musicWanted = false; s.musicPlaying = false;
  s.setHallWanted(true, 'assets/hall/neon/arcade.mp3');
  s._hallBufs[s._hallUrl] = { b: 1 };
  s.startHallMusic();
  s.setHallMute(true);
  chk(s.musicPlaying === false && s.musicWanted === false,
    'E · mute sin petición previa del menú: nada se inventa');
}
{
  const s = audio();
  flujoBug(s);
  s.setHallMute(true);
  s.setHallMute(false);                             // icono: reactivar
  chk(s.hallPlaying === true && s.musicWanted === false,
    'F · no-regresión: reactivar el icono vuelve a levantar el salón y retira el menú (prioridad del dueño)');
}

console.log('— F-A2 · c07: guard del vaivén de los troqueles');
{
  chk(C07.includes('p.cfg.sway != null ? p.cfg.sway : 0.5'),
    'G · la línea de sway lleva el guard (ausente → 0.5)');
  const f = (sway) => 0.006 * (sway != null ? sway : 0.5);
  chk(Number.isFinite(f(undefined)) && f(undefined) === 0.003,
    'G · pack sin sway → vaivén definido (0.003), sin NaN');
  chk(f(0) === 0, 'G · el cero explícito se respeta (troquel quieto legítimo)');
  chk(f(0.9) === 0.0054, 'G · los valores reales (0.3-0.9) pasan intactos');
}

console.log(fail === 0
  ? `✓ REPASO r149: ${ok} OK · F-A1 amarrado (máquina de música real) + F-A2 guard`
  : `✗ REPASO r149: ${ok} OK · ${fail} FALLO(S)`);
process.exit(fail === 0 ? 0 : 1);
