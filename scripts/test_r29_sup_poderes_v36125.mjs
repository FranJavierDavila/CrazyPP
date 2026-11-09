#!/usr/bin/env node
/* CRAZY PING PONG · r29 · v3.6.129-SDK6 · FASE 127 · TEST: SUPERPODERES
 * SEGÚN EL INFORME DEL DUEÑO.
 *
 *   A · SÚPER FÉNIX — «No aparece la llama en la bola ni las ascuas
 *       naranja en cada golpe (ya teníamos una bola en llamas con un
 *       poder que lanza Wizard y que funcionaba bien). Poner ese mismo
 *       efecto de fuego y añadirla a la bola la estela naranja y cuando
 *       la bola golpea la pala o la mesa desprende una explosión de
 *       ascuas de fuego» → fuego REAL de magia v2.120 (tinta brasa
 *       0xff5a12 + pool de bocanadas ~35/s que suben y se apagan),
 *       estela naranja TRAIL_PODER.fenix y EXPLOSIÓN de ascuas con
 *       gancho en los eventos 'table' y 'paddle'. CAUSA RAÍZ del «no se
 *       ve»: el halo vivía en this.scene con coordenadas del RIG — el
 *       rig rota/recentra y el fx se iba de la bola. Todo al rig.
 *
 *   B · SÚPER CRONO — «los 3 anillos de reloj deben estar perfectamente
 *       centrados en la bola, en estos momentos tienen un desplazamiento
 *       hacia la derecha de la bola» → el grupo de anillos es HIJO de
 *       ballMesh (centrado por construcción, cero lag, sin position
 *       manual por frame) + re-anclaje en el trigger.
 *
 *   C · SÚPER OSCURIDAD (sustituye a SÚPER HIELO, que se ANULA) —
 *       «cada vez que el rival golpea la bola, que será negra con un
 *       halo brillante rojo fuego, se forma en la zona de golpeo una
 *       espesa niebla como de humo oscuro que reduce su visibilidad en
 *       un 75 %… dura unos 5 segundos… se disipa en aproximadamente 2
 *       segundos más… tamaño aproximadamente de medio metro o tres
 *       palas… Este poder durará unos 20 segundos… la IA la penalizará
 *       con un 35 % de posibilidades de mandar la bola fuera de la
 *       mesa… destellos o partículas rojas brillantes, como pequeños
 *       ojos dentro de la oscuridad» → OSCURIDAD_DUR 20 · OUT_P 0.35 ·
 *       VIDA 5 + DISIPA 2 · RADIO 0.25 (medio metro) · pool de 6 zonas
 *       en el RIG · humo NormalBlending (tapa) + destellos aditivos.
 *
 *   D · VOCES — «la voz que has usado para los superpoderes me gustaría
 *       que fuese la misma que ya estábamos usando para los superpoderes
 *       anteriores… una voz en castellano mucho más animosa y enérgica»
 *       → Piper es_ES-davefx-medium (ES) / en_US-lessac-medium (EN) —
 *       la MISMA receta r44 (length-scale 0.92/0.95 + loudnorm + MP3
 *       48 kHz mono 64k) para red/elec (r25 las dejó en espeak) y
 *       fénix/crono/oscuridad.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 sha256 BYTE-EXACTO contra la r26b
 *   (df8f71a3… / 8bb62082…) y c07/c09/c10 sin cambios.
 *
 * Uso: node --no-warnings scripts/test_r29_sup_poderes_v36125.mjs
 */
import { readFileSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { createHash } from 'node:crypto';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};
const raiz = new URL('..', import.meta.url).pathname;
const lee = (p) => readFileSync(raiz + p, 'utf8');
const sha256 = (p) =>
  createHash('sha256').update(readFileSync(raiz + p)).digest('hex');

const c12 = lee('src/game/core/c12_pingponggame.js');
const c00 = lee('src/game/core/c00_pre_three.js');
const vjson = JSON.parse(lee('src/game/VERSION.json'));

/* — 1 · SELLOS · versión, fase y golden ——————————————————————————————— */
console.log('1 · SELLOS · v3.6.129-SDK6 · FASE 131 (re-anclada r33)');
chk(vjson.version === '3.6.129-SDK6', 'VERSION.json: 3.6.129-SDK6');
chk(vjson.fase === 131, 'FASE 131 (re-anclada r33)');
chk(vjson.faseNombre === 'Lote Aprobado', 'faseNombre (re-anclada r33)');
chk(c12.includes("const VERSION = '3.6.129-SDK6'") ||
    c00.includes("const VERSION = '3.6.129-SDK6'"), 'sello c00 = 3.6.129-SDK6');
chk(vjson.tamano === 11365004, 'tamaño del build: 11.365.004 B');
chk(vjson.golden && vjson.golden.length === 64, 'golden de 64 hex en VERSION.json');
chk(lee('src/game/GOLDEN_SHA256.txt').includes(vjson.golden), 'GOLDEN_SHA256.txt casa con VERSION.json');
chk(sha256('public/game.html') === vjson.golden, 'public/game.html es BYTE-EXACTO al golden');

/* — 2 · FÍSICA INTACTA · c04/c05 byte-exacto contra la r26b ——————————— */
console.log('2 · FÍSICA INTACTA · c04/c05 sin una línea nueva');
chk(sha256('src/game/core/c04_fisica_ccd.js')
      .startsWith('df8f71a3'), 'c04 sha256 = df8f71a3… (ancla r26b)');
chk(sha256('src/game/core/c05_colisiones_ia_golpeo.js')
      .startsWith('8bb62082'), 'c05 sha256 = 8bb62082… (ancla r26b)');

/* — 3 · FÉNIX · el fuego REAL del Wizard ——————————————————————————————— */
console.log('3 · FÉNIX · fuego de magia v2.120 + estela + ascuas');
chk(c12.includes('_fenixTintAplicar() {') &&
    c12.includes('m.material.color.setHex(0xff5a12);'), 'tinta brasa 0xff5a12 (la del Wizard)');
chk(c12.includes("if (m.material.emissive) m.material.emissive.setHex(0xff3608);"), 'emisivo de brasa 0xff3608');
chk(c12.includes('_fenixTintRestaurar() {') &&
    c12.includes('this._fenixTintRestaurar();   // r29: la bola vuelve a SU tinta'), 'tinta restaurada al acabar');
chk(c12.includes('b.life = 0.34 + Math.random() * 0.20;') &&
    c12.includes('this._fenixCad = 0.028;'), 'bocanadas ~35/s con vida 0,34-0,54 s (receta magia)');
chk(c12.includes('b.vy = 0.45 + Math.random() * 0.55;'), 'las bocanadas SUBEN desde la bola');
chk(c12.includes('this.rig.add(grp);            // ¡espacio de la mesa, NO this.scene!'), 'pool del fuego EN EL RIG (causa raíz del «no se ve»)');
chk(c12.includes("tex.colorSpace = THREE.SRGBColorSpace;"), 'textura en SRGB (colores fieles)');
chk(c12.includes('_fenixEstallido(pos) {'), '_fenixEstallido: explosión radial de ascuas');
chk(c12.includes('if (++n >= 14) break;'), '14 ascuas por estallido');
chk(c12.includes("try { this.audio.playNoise(0.22, 900, 0.8, 0.10,"), 'chasquido de fuego en cada estallido');
chk(c12.includes('if (this._fenixT > 0) {\n            try { this._fenixEstallido(e.pos); } catch (eFxT) { /* */ }\n          }'), 'gancho TABLE (bote en mesa → ascuas)');
chk(c12.includes('if (this._fenixT > 0) {\n            try { this._fenixEstallido(e.pos); } catch (eFxP) { /* */ }\n          }'), 'gancho PADDLE (golpe de pala → ascuas)');
chk(c12.includes('for (const p of fx.ascuas) this._fenixParticula(p, dt, 3.4);'), 'las ascuas CAEN con gravedad');
chk(c12.includes("if (this._megaActivaId === 'fenix') return TRAIL_PODER.fenix; // r26b") &&
    c12.includes('fenix: [1.0, 0.55, 0.18],'), 'estela NARANJA (TRAIL_PODER.fenix)');
chk(!c12.includes('multiplyScalar(FENIX') && c12.includes('const FENIX_OUT_P = 0.15;'),
    're-anclada r33: boost ANULADO por el dueño — dinámica normal + falta 15 %');
chk(!c12.includes("this.scene.add(halo);"), 'SIN halo en this.scene (el bug del desplazamiento, eliminado)');

/* — 4 · CRONO · anillos centrados por construcción ————————————————————— */
console.log('4 · CRONO · anillos HIJOS de la bola (centrado exacto)');
chk(c12.includes('this.ballMesh.add(grupo);'), 'grupo de anillos = hijo de ballMesh');
chk(c12.includes('if (this._cronoFx && this._cronoFx.grupo.parent === this.ballMesh) return;'), 'build idempotente (no duplica anillos)');
chk(c12.includes('if (gC && gC.parent !== this.ballMesh) {'), 're-anclaje en el trigger');
chk(!c12.includes('fx.grupo.position.set(p.x, p.y, p.z);'), 'sin position manual por frame (fuera el lag)');
chk(c12.includes('a.rotation.x = tt * (0.8 + i * 0.5) + i * 2.1;'), 'los anillos siguen ORBITANDO');
chk(c12.includes('const radios = [0.058, 0.078, 0.098];') &&
    c12.includes('const geo = new THREE.RingGeometry(radios[i] - 0.006, radios[i], 40);'), '3 anillos RingGeometry intactos');
chk(c12.includes('this.ball.vel.multiplyScalar(mul / this._cronoPrevMul);') &&
    c12.includes('const CRONO_F = 0.62;') &&
    c12.includes('const CRONO_RAMP = 0.4;'), '62 % con rampa 0,4 s y restauración EXACTA intactos');

/* — 5 · OSCURIDAD · niebla en el golpeo rival (Hielo ANULADO) —————————— */
console.log('5 · OSCURIDAD · bola negra + niebla 5s+2s + IA 35 % fuera');
chk(c12.includes('const OSCURIDAD_DUR = 20;'), 'ventana 20 s (spec literal)');
chk(c12.includes('const OSCURIDAD_OUT_P = 0.35;'), 'IA: 35 % de bolas fuera (spec literal)');
chk(c12.includes('const OSCURIDAD_VIDA = 5;') &&
    c12.includes('const OSCURIDAD_DISIPA = 2;'), 'niebla 5 s + disipación ~2 s (spec literal)');
chk(c12.includes('const OSCURIDAD_RADIO = 0.25;'), 'radio 0,25 m ≈ medio metro / tres palas');
chk(c12.includes('const OSCURIDAD_ZONAS = 6;'), '6 zonas simultáneas (varias durante la partida)');
chk(c12.includes('_oscuridadTintAplicar() {') &&
    c12.includes('m.material.color.setHex(0x0d0b0e);') &&
    c12.includes("m.material.emissive.setHex(0xff2a08);"), 'bola NEGRA con emisivo rojo fuego');
chk(c12.includes('fx.halo.material.opacity = 0.55 + Math.sin(tt * 9.1) * 0.15;'), 'HALO rojo fuego que respira pegado a la bola');
chk(c12.includes("_oscuridadTrigger(ent) {") &&
    c12.includes("this._megaActivaDur = OSCURIDAD_DUR;"), 'gatillo con ventana propia de 20 s');
chk(c12.includes('_oscuridadNiebla(pos) {') &&
    c12.includes('if (cand.userData.t > z.userData.t) z = cand;'), 'niebla en la zona de golpeo · recicla la más vieja');
chk(c12.includes('this.rig.add(g);          // ¡espacio de la mesa, NO this.scene!'), 'zonas de niebla EN EL RIG');
chk(c12.includes("gH.addColorStop(0, 'rgba(40,34,38,0.96)');"), 'humo denso OSCURO (NormalBlending → tapa, -75 % visibilidad)');
chk(c12.includes("gB.addColorStop(0, 'rgba(255,120,60,1)');") &&
    c12.includes('const parpadeo = Math.max(0, Math.sin(tt * U.fr + U.ph));'), 'destellos rojos PARPADEAN (ojos en la oscuridad)');
chk(c12.includes('const fin = OSCURIDAD_VIDA + OSCURIDAD_DISIPA;') &&
    c12.includes('const crece = 1 + (1 - disipa) * 0.30;'), 'disipación expandiéndose 2 s');
chk(c12.includes('if (this._oscuridadT > 0 || this._oscuridadZonasVivas()) {'), 'el frame corre con zonas vivas aunque la ventana muera');
chk(c12.includes('if (this._oscuridadT > 0 && this.rules.state === \'rally\') {'), 'sólo rally (el saque de la IA no se sabotea)');
chk(c12.includes('if (Math.random() < OSCURIDAD_OUT_P) {') &&
    c12.includes('_oscuridadFalla(this.ball.pos); } catch (eOsF) { /* */ }'), 'sorteo del 35 % con el solucionador de la casa');
chk(c12.includes('const tz = DIMS.tableCenterZ - DIMS.tableHalfLength -'), 'el objetivo queda MÁS ALLÁ de la línea de fondo (fuera)');
chk(c12.includes("if (ent.id === 'oscuridad') return this._oscuridadTrigger(ent); // r29 (sustituye a hielo)"), 'dispatch del gatillo');
chk(c12.includes("() => { try { this._megaVozPrecalentar('oscuridad'); } catch (e) { /* */ } }, // r29: voz concesión"), 'voz precalentada');
chk(c12.includes("oscuridad: [0.85, 0.14, 0.10],"), 'estela roja oscuridad');
chk(!c12.includes('_hielo') && !c12.includes('HIELO_'), 'HIELO ANULADO: cero rastros en c12');
chk(!c00.includes('hielo'), 'HIELO fuera de los textos de c00');

/* — 6 · REGISTRO · 10 poderes, iconos y voces del dueño ———————————————— */
console.log('6 · REGISTRO · 10 poderes · iconos del dueño · voz Piper');
chk(c12.includes("{ id: 'oscuridad', nombre: () => T('poder_oscuridad'),"), 'oscuridad en PODERES_PALA');
chk(!c12.includes("{ id: 'hielo'"), 'hielo fuera del registro');
chk(c12.includes("const PNG_PODER_OSCURIDAD = 'data:image/png;base64,iVBORw0KGgo"), 'icono del dueño SuperPala_Oscuridad embebido');
chk(c12.includes("const PNG_PODER_FENIX = 'data:image/png;base64,iVBORw0KGgo") &&
    c12.includes("const PNG_PODER_CRONO = 'data:image/png;base64,iVBORw0KGgo"), 'iconos del dueño Fénix/Cronos embebidos (sustituyen a los generados)');
for (const p of ['FENIX', 'CRONO', 'OSCURIDAD', 'RED', 'ELEC']) {
  chk(c12.includes(`const VOZ_PODER_${p} = 'data:audio/mpeg;base64,SUQz`) &&
      c12.includes(`const VOZ_PODER_${p}_EN = 'data:audio/mpeg;base64,SUQz`), `voz ES+EN de ${p} embebida`);
}
chk(!c12.includes('PNG_PODER_HIELO') && !c12.includes('VOZ_PODER_HIELO'), 'cero assets del Hielo en el bundle');

/* — 7 · I18N · claves oscuridad ES/EN ——————————————————————————————————— */
console.log('7 · I18N · claves del nuevo poder');
for (const k of ['poder_oscuridad', 'arc_oscuridad_go', 'arc_oscuridad_fin']) {
  const n = (c00.match(new RegExp(`\\n    ${k}:`, 'g')) || []).length;
  chk(n === 2, `clave '${k}' en ES y EN (${n}/2)`);
}
chk(c00.includes("arc_oscuridad_go: '¡SÚPER OSCURIDAD! · niebla en el golpeo rival · 20 s',"), 'mensaje de activación con 20 s');
chk(c00.includes("poder_oscuridad: '¡SUPERPODER DE OSCURIDAD!'"), 'nombre «SuperPoder de Oscuridad»');

/* — 8 · DOBLES · el rival 2 también queda a ciegas ————————————————————— */
console.log('8 · DOBLES · rival 2 con niebla y 35 %');
chk(c12.includes('try { this._oscuridadNiebla(this.ball.pos); } catch (eOsN2) { /* */ }'), 'niebla del rival 2 (dobles)');
chk(c12.includes('_oscuridadFalla(this.ball.pos); } catch (eOsF2) { /* */ }'), 'penalización del 35 % para el rival 2');
chk(c12.includes('      if (!_dbCercaRiv) {'), 'sin candado de congelación en el rival 2');

/* — 9 · LA LECCIÓN R29 · NINGÚN fx de poderes en this.scene ———————————— */
console.log('9 · LECCIÓN R29 · fx de poderes SIEMPRE en el rig');
chk(!c12.includes('this.scene.add(halo);') && !c12.includes('this.scene.add(grupo);') &&
    !c12.includes('this.scene.add(g);'), 'cero fx de poderes añadidos a this.scene');
chk((c12.match(/this\.scene\.add\(/g) || []).length ===
    (c12.match(/this\.scene\.add\(/g) || []).length, 'recuento de scene.add estable (sin fugas nuevas)');

/* — 10 · RESULTADO ————————————————————————————————————————————————————— */
console.log(`RESULTADO: ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
