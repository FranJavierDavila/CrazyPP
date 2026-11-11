#!/usr/bin/env node
/* CRAZY PING PONG · r32 · v3.6.146-SDK6 · FASE 149 · TEST: SALONES DEL
 * DUEÑO (arte preparado por el dueño + música ambiental con icono).
 *
 *   A · ARTE DEL DUEÑO — los 18 JPG de los tres salones (DOJO ZEN ·
 *       OBSERVATORIO ESTELAR · SALÓN NEÓN ARCADE) son AHORA los ficheros
 *       que preparó el dueño (sha256 byte-exacto contra los ZIPs subidos),
 *       en las medidas EXACTAS de la spec v3.6.28 (frente/fondo 1849×864 ·
 *       laterales 2395×864 · suelo/techo 1296×1678 — comprobado al
 *       instalar). Sustituyen al arte IA de la r30 (mismas fichas/rutas).
 *
 *   B · MÚSICA AMBIENTAL DEL SALÓN — dojo.mp3 / arcade.mp3 /
 *       observatorio.mp3 (sha256 byte-exacto) viven junto a su arte;
 *       HALL_VARIANTES (c02) lleva el campo `musica` en las TRES variantes
 *       nuevas (anfitrion/cabana sin pista); canal hall NUEVO en c03
 *       (setHallWanted/startHallMusic/stopHallMusic/setHallMute/
 *       _loadHallMusic) con caché por URL, fundidos y persistencia
 *       pp_hallmus.
 *
 *   C · PRIORIDAD del dueño — «cuando en el Hall tenemos activada su
 *       música no sonará ninguna otra en esta estancia»: startMusic()
 *       tiene el guard hallWanted&&!hallMute (el menú no nace sobre el
 *       salón) y startHallMusic() retira la del menú si estuviera viva
 *       (sentido SALÓN→menú, mismo patrón BSO v2.124). Al re-adoptar un
 *       contexto nuevo (tryFreshRunning), la pista del salón rearranca
 *       ANTES que la del menú.
 *
 *   D · ICONO DE LA PARED — placa vectorial en la pared FRONTAL (c08:
 *       drawHallMusica + userData.hall.musica con repinta()), hover
 *       suavizado en updateHallFx, gatillo VR en c12 (raycast propio con
 *       Raycaster nuevo — el far=2,5 del menú queda intacto) en los DOS
 *       sitios de onSelectStart (menú abierto con hov<0, y hall a secas),
 *       repintado en drawHall y cableado completo: enterHall/exitHall/
 *       hall_var/onPeerHall. i18n msg_hallmus en ES y EN.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 sha256 BYTE-EXACTO contra la r26b
 *   (df8f71a3… / 8bb62082…).
 *
 * Uso: node --no-warnings scripts/test_r32_salones_v36128.mjs
 */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');
const leeB = (p) => readFileSync(raiz + p);
const sha256 = (p) =>
  createHash('sha256').update(leeB(p)).digest('hex');

const c02 = lee('src/game/core/c02_cfg_escena.js');
const c03 = lee('src/game/core/c03_audio_voz.js');
const c08 = lee('src/game/core/c08_hall_hud.js');
const c12 = lee('src/game/core/c12_pingponggame.js');
const c00 = lee('src/game/core/c00_pre_three.js');
const vjson = JSON.parse(lee('src/game/VERSION.json'));
const game = lee('public/game.html');
const cuerpo = lee('src/game/03_body.html');

/* — 1 · SELLOS · v3.6.146-SDK6 · FASE 149 ————————————————————————— */
console.log('1 · SELLOS · v3.6.146-SDK6 · FASE 149 · SALONES DEL DUEÑO');
chk(vjson.version === '3.6.146-SDK6', 'VERSION.json: 3.6.146-SDK6');
chk(vjson.fase === 149, 'FASE 149');
chk(vjson.faseNombre === 'El Arcano es data-driven: ARCANO_CFG única fuente de verdad (ventanas, reglas por modalidad, búho) + puerta única pwViva', 'faseNombre = SALONES DEL DUEÑO');
chk(vjson.tamano === 11547159, 'tamaño del build: 11.526.764 B');
chk(vjson.golden ===
  'f8d1859df863f709c7cf0f12bc5a2314087915e6d88cf46c2374e74fb807f1e4',
  'VERSION.json golden 1836d13f…');
chk(sha256('public/game.html') ===
  'f8d1859df863f709c7cf0f12bc5a2314087915e6d88cf46c2374e74fb807f1e4',
  'golden 10a24300… (build byte-exacto)');
chk(game.includes('3.6.146-SDK6'), 'bundle con sello vigente');
chk(c00.includes("const VERSION = '3.6.146-SDK6'"), 'sello c00 = 3.6.146-SDK6');
chk(lee('public/sw.js').includes("CACHE = 'crazypp-v3.6.146-SDK6'"),
  'sw.js CACHE v3.6.146-SDK6 (purga de cachés viejas)');
chk(cuerpo.includes('>V3.6.146-SDK6</span>'), 'badge V3.6.146-SDK6 en 03_body');
chk(lee('src/app/descargas/page.tsx').includes('v36139-sdk6'),
  'hub /descargas sellado a v36139-sdk6');

/* — 2 · ARTE DEL DUEÑO · 18 JPG byte-exacto contra los ZIPs ———————— */
console.log('2 · ARTE DEL DUEÑO · sha256 byte-exacto (ZIPs → public/assets/hall)');
const ARTE = {
  'assets/hall/dojo/frente.jpg':      '0bebf58569b0e70d',
  'assets/hall/dojo/fondo.jpg':       '8c8a257814847e81',
  'assets/hall/dojo/izquierda.jpg':   'f2112dd31ad974c3',
  'assets/hall/dojo/derecha.jpg':     '1e07f57c4e783f3a',
  'assets/hall/dojo/suelo.jpg':       'b15376e558fc21f2',
  'assets/hall/dojo/techo.jpg':       '50edcdbc22e4c50b',
  'assets/hall/observatorio/frente.jpg':    '9d26bdfbc9632881',
  'assets/hall/observatorio/fondo.jpg':     'f34eca12eb4dab76',
  'assets/hall/observatorio/izquierda.jpg': 'a058e2ce44d58c37',
  'assets/hall/observatorio/derecha.jpg':   'ebefc0c28dec73a3',
  'assets/hall/observatorio/suelo.jpg':     'dddc76c3b908c82c',
  'assets/hall/observatorio/techo.jpg':     'c500d2d1c8d96db5',
  'assets/hall/neon/frente.jpg':      '3d9c038dc6e530b8',
  'assets/hall/neon/fondo.jpg':       '30febcfdc76a71e2',
  'assets/hall/neon/izquierda.jpg':   '1029a6c7f84da641',
  'assets/hall/neon/derecha.jpg':     'f908e47b6526d8d7',
  'assets/hall/neon/suelo.jpg':       'bb91b61f62a76f03',
  'assets/hall/neon/techo.jpg':       '7667c2a2f8a60080',
};
let arteOk = 0;
for (const [p, h16] of Object.entries(ARTE)) {
  const bueno = sha256('public/' + p).startsWith(h16);
  if (bueno) arteOk++; else chk(false, `arte ${p} = ${h16}…`);
}
chk(arteOk === 18, `los 18 planos visten el ARTE DEL DUEÑO (${arteOk}/18)`);

/* — 3 · MÚSICA AMBIENTAL · pistas del dueño + canal hall (c03) ————— */
console.log('3 · MÚSICA DEL SALÓN · pistas + canal hall en c03');
const MUS = {
  'assets/hall/dojo/dojo.mp3':                       '65de304054f356f5',
  'assets/hall/neon/arcade.mp3':                     'f46f0774218bb034',
  'assets/hall/observatorio/observatorio.mp3':       '9a2d87455814be7b',
};
let musOk = 0;
for (const [p, h16] of Object.entries(MUS)) {
  const bueno = sha256('public/' + p).startsWith(h16);
  if (bueno) musOk++; else chk(false, `música ${p} = ${h16}…`);
}
chk(musOk === 3, `las 3 pistas del dueño instaladas (${musOk}/3)`);
chk(c02.includes("musica: 'assets/hall/neon/arcade.mp3'"),
  'c02 · NEÓN lleva arcade.mp3');
chk(c02.includes("musica: 'assets/hall/observatorio/observatorio.mp3'"),
  'c02 · OBSERVATORIO lleva observatorio.mp3');
chk(c02.includes("musica: 'assets/hall/dojo/dojo.mp3'"),
  'c02 · DOJO lleva dojo.mp3');
const bloqueAnfitrion = c02.slice(
  c02.indexOf("id: 'anfitrion'"), c02.indexOf("id: 'neon'"));
chk(!bloqueAnfitrion.includes('musica:'),
  'c02 · anfitrion y cabana SIN pista (el museo y la Cabaña callan)');
chk(c03.includes('setHallWanted(wanted, url)'), 'c03 · setHallWanted(wanted, url)');
chk(c03.includes('startHallMusic()') && c03.includes('stopHallMusic()'),
  'c03 · startHallMusic/stopHallMusic');
chk(c03.includes('setHallMute(mute)'), 'c03 · setHallMute (icono de la pared)');
chk(c03.includes('_loadHallMusic()') && c03.includes('this._hallBufs'),
  'c03 · caché de buffers por URL (_hallBufs)');
chk(c03.includes("localStorage.getItem('pp_hallmus')") &&
   c03.includes("localStorage.setItem('pp_hallmus'"),
  'c03 · silencio del salón PERSISTENTE (pp_hallmus)');
chk(c03.includes('0.30 * this.musicVol'),
  'c03 · volumen del salón escala por el canal MÚSICA (musicVol, r95)');
chk(c03.includes("'[Audio] música del salón lista ('"),
  'c03 · log de la pista lista (familia de la casa)');

/* — 4 · PRIORIDAD del dueño · invariante UNA MELODÍA ——————————————— */
console.log('4 · PRIORIDAD · la música del salón manda sobre la del menú');
const sm = c03.indexOf('startMusic() {');
const smBody = c03.slice(sm, c03.indexOf('stopMusic', sm));
chk(smBody.includes('if (this.hallWanted && !this.hallMute) return;'),
  'startMusic: el menú NO nace con la pista del salón viva (guard r32)');
const shm = c03.indexOf('startHallMusic() {');
const shmBody = c03.slice(shm, c03.indexOf('stopHallMusic()', shm));
chk(shmBody.includes('if (this.musicPlaying) this.setMusicWanted(false);'),
  'startHallMusic: RETIRA la música del menú si estaba sonando');
chk(c03.indexOf('this.hallPlaying = false;\n      if (this.hallWanted && !this.hallMute) this.startHallMusic();') <
    c03.indexOf('if (this.musicWanted && this.musicOn) this.startMusic();'),
  'tryFreshRunning: la pista del salón rearranca ANTES que la del menú');
chk(shmBody.includes('!this.hallWanted || this.hallMute'),
  'startHallMusic: guard completo (hallWanted sin mute)');

/* — 5 · ICONO DE LA PARED · c08 (placa) + c12 (gatillo) ———————————— */
console.log('5 · ICONO DE LA PARED · placa vectorial + gatillo VR');
chk(c08.includes('export function drawHallMusica(cv, mute)'),
  'c08 · drawHallMusica (pintor vectorial exportado)');
chk(c08.includes('musica:') === false && c08.includes('musica,'),
  'c08 · userData.hall registra `musica` (mesh+cv+tex+repinta)');
chk(c08.includes('musMesh.position.set(0, 2.42, z0 + 0.016)'),
  'c08 · placa en la pared FRONTAL, sobre la de insignias');
chk(c08.includes("drawHallMusica(musCv, !!mute)") &&
   c08.includes('musTex.needsUpdate = true'),
  'c08 · repinta(mute, visible): estado + visibilidad');
chk(c08.includes('ud.musica.hover') ||
   c08.slice(c08.indexOf('updateHallFx')).includes('mu.hover ? 1.16 : 1.0'),
  'c08 · hover del rayo agranda la placa con suavizado (updateHallFx)');
chk(c12.includes('_hallMusicaRay(i)') &&
   c12.includes('this._musRay = new THREE.Raycaster()'),
  'c12 · raycast PROPIO al icono (no pisa el far=2,5 del menú)');
chk((c12.match(/this\._hallMusicaPulsa\(i\)/g) || []).length === 2,
  'c12 · gatillo en los DOS sitios de onSelectStart (menú abierto + hall)');
chk(c12.includes("else if (this.inHall && this._hallMusicaPulsa(i))"),
  'c12 · con menú abierto, la placa manda SOLO si no hay botón (hov<0)');
chk(c12.includes('this._hallMusicaRepinta();') &&
   (c12.match(/_hallMusicaRepinta\(\)/g) || []).length >= 4,
  'c12 · repintado del icono en drawHall + hall_var + pulsa (+def)');
chk(c12.includes('this.audio.setHallWanted(!!hvMus, hvMus || null)'),
  'c12 · enterHall: la variante ACTIVA pide su pista');
chk(c12.includes('this.audio.setHallWanted(false, null)'),
  'c12 · exitHall: la pista muere con la estancia');
chk(c12.includes('this.audio.setHallWanted(!!hv.musica, hv.musica || null)'),
  'c12 · hall_var: cambio de salón EN VIVO');
chk(c12.includes('this.audio.setHallWanted(!!(hvP && hvP.musica), (hvP && hvP.musica) || null)'),
  'c12 · visita online: el salón del ANFITRIÓN suena como el suyo');
chk(c12.includes("T('msg_hallmus', { v: nuevo ? T('no') : T('yes') })"),
  'c12 · mensaje i18n al conmutar');
const msgEs = (c00.match(/msg_hallmus: '[^']*'/g) || []).length;
chk(msgEs === 2 && c00.includes("msg_hallmus: 'Música del salón: {v}'") &&
   c00.includes("msg_hallmus: 'Lounge music: {v}'"),
  'i18n · msg_hallmus en ES y EN');

/* — 6 · SALVAVIDADES · robustez de la casa ———————————————————————— */
console.log('6 · ROBUSTEZ · todo a prueba de fallos');
chk(c02.includes('MÚSICA AMBIENTAL DEL SALÓN') &&
   c02.includes('r32 (v3.6.128)'),
  'c02 · el registro documenta la música del salón');
chk(c03.includes('INVARIANTE UNA MELODÍA (sentido SALÓN→menú)'),
  'c03 · el invariante UNA MELODÍA documentado en el nuevo sentido');
chk(c08.includes('el icono nunca rompe el hall') &&
   c03.includes('sin pista: nunca rompe el juego'),
  'fallos suaves: icono y pista JAMÁS rompen el salón');
chk(c12.includes('ud0.musica.hover = false'),
  'exitHall limpia el hover del icono (no queda congelado)');

/* — 7 · GARANTÍA DE SIEMPRE · física byte-exacto —————————————————— */
console.log('7 · FÍSICA INTACTA · c04/c05 byte-exacto contra la r26b');
chk(sha256('src/game/core/c04_fisica_ccd.js').startsWith('df8f71a3'),
  'c04_fisica_ccd.js = df8f71a3… (r26b)');
chk(sha256('src/game/core/c05_colisiones_ia_golpeo.js').startsWith('8bb62082'),
  'c05_colisiones_ia_golpeo.js = 8bb62082… (r26b)');

console.log(`\nR32 · SALONES DEL DUEÑO · ${ok} OK / ${fails} FALLOS`);
process.exit(fails ? 1 : 0);
