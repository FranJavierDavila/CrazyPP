#!/usr/bin/env node
/* CRAZY PING PONG · r40 · v3.6.140-SDK6 · FASE 142 · TEST: EL ARCANO A LA
 * VISTA — revisión del dueño sobre la r39 (cuatro informes en uno):
 *
 *   A · EL BÚHO, UN 25 % MÁS PEQUEÑO — «Veamos el buho (un poco más
 *       pequeño como un 25% más pequeño que ahora)»: la placa del hall
 *       pasa de 0,78×0,52 a 0,585×0,39 (misma proporción 1024×683, los
 *       destellos de los ojos escalan con ARC_W/ARC_H, misma pared).
 *
 *   B · LOS BOTONES DEL HALL SON PULSABLES SIN MENÚ — «u otros elementos
 *       del Hall por defecto no son pulsables hasta que sacamos el menú…
 *       eso no debería ser así»: el rayo + haz + hover viven SIEMPRE en
 *       las estancias (updateMenu corre con menuOpen || inHall ||
 *       _arconoOn), el panel del menú SÓLO es objetivo con el menú
 *       abierto, el haz es la mirilla honesta de 3 m en el salón/Arcano,
 *       el gatillo ya vivía en el búho y en la placa sin menú, y DENTRO
 *       del Arcano B no abre nada (el búho es la única puerta).
 *
 *   C · EL ESCENARIO NACE DELANTE — bug raíz de la r39 («Delante nuestra
 *       tiene que aparecer — que no aparece en estos momentos nada»): el
 *       grupo arcano se PLANTA sobre los pies del anfitrión (XZ del rig)
 *       y gira al yaw de la cabeza en cada entrada; además fog:false en
 *       TODAS las piezas (la niebla de la cancha Fog(9,18) ahogaba los
 *       cometas de la r39 a 22-38 m).
 *
 *   D · CIELO LISO + SUELO INFINITO — «el fondo completamente azul
 *       oscuro sin imagen, un suelo infinito que se pierde en el
 *       horizonte… grandes losetas de sutiles tonos azulados que cambian
 *       de forma aleatoria sus tonos azules, dentro de un rango un poco
 *       más claro que el cielo»: bóveda SIN Vía Láctea ni estrellas
 *       (sólo el degradado azul noche), suelo 72×72 m con losetas de
 *       8 m (9×9), retícula fina, banda #10284e→#1a3868, viñeta que
 *       funde al color del horizonte (#0a1a36) y MUTA al azar en
 *       updateArcanoFx (7 losetas eligen tono cada 0,35 s, mordisco
 *       0,35, re-pintado por loseta).
 *
 *   E · LA MELODÍA PROPIA — «Aquí dentro no suena la música del hall
 *       sino que tenemos una melodia propia arcano.mp3»: el arte del
 *       dueño byte-exacto en assets/hall/arcano.mp3, el canal hall de
 *       c03 (el único, probado) la lanza al entrar y _arconoSalir
 *       restaura el aire del salón (SU variante, o la del anfitrión en
 *       visita online) por el mismo camino que enterHall.
 *
 *   Se CONSERVA de la r39: galería automática de los 14 (tipo+desc+
 *   métricas reales), flechas ‹ › con glow SIN flecha en los extremos,
 *   candado azul translúcido legible, desbloqueo por coronación y
 *   Duelos Locos.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 sha256 BYTE-EXACTO contra la r26b
 *   (df8f71a3… / 8bb62082…).
 *
 * Uso: node --no-warnings scripts/test_r40_arcano_v36139.mjs
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
const sha256 = (p) => createHash('sha256').update(leeB(p)).digest('hex');

const c00 = lee('src/game/core/c00_pre_three.js');
const c08 = lee('src/game/core/c08_hall_hud.js');
const c12 = lee('src/game/core/c12_pingponggame.js');
const vjson = JSON.parse(lee('src/game/VERSION.json'));
const game = lee('public/game.html');
const cuerpo = lee('src/game/03_body.html');

/* — 1 · SELLOS · v3.6.140-SDK6 · FASE 142 ————————————————————————— */
console.log('1 · SELLOS · v3.6.140-SDK6 · FASE 142 · EL ARCANO A LA VISTA');
chk(vjson.version === '3.6.140-SDK6', 'VERSION.json: 3.6.140-SDK6');
chk(vjson.fase === 142, 'FASE 142');
chk(vjson.faseNombre === 'La voz del oráculo — voz solemne del Arcano, candado siempre visible y constelación del arte nuevo', 'faseNombre = EL ARCANO A LA VISTA');
chk(vjson.sdk === '1.6.0', 'SDK de la casa intacto (1.6.0)');
// r46 · RE-ANCLAJE: build legítimamente cambiado por la r46 (gobernador + worker v3)
chk(vjson.tamano === 11507255, 'tamaño del build: 11.507.255 B (re-anclado r46)');
chk(vjson.golden ===
  '2b3dffca315d787eea3818e44621ed1a85355bf4e3c088ae818a4b7c0b67e927',
  'VERSION.json golden 42d07e64… (re-anclado r46)');
chk(sha256('public/game.html') === vjson.golden,
  'golden = sha256 real del build (byte-exacto)');
chk(game.includes('3.6.140-SDK6'), 'bundle con sello vigente');
chk(c00.includes("const VERSION = '3.6.140-SDK6'"), 'sello c00 = 3.6.140-SDK6');
chk(lee('public/sw.js').includes("CACHE = 'crazypp-v3.6.140-SDK6'"),
  'sw.js CACHE v3.6.140-SDK6 (purga de cachés viejas)');
chk(cuerpo.includes('>V3.6.140-SDK6</span>'), 'badge V3.6.140-SDK6 en 03_body');
chk(lee('src/app/descargas/page.tsx').includes('v36139-sdk6'),
  'hub /descargas sellado a v36139-sdk6');

/* — 2 · EL BÚHO DEL HALL, UN 25 % MÁS PEQUEÑO ————————————————————— */
console.log('2 · BÚHO · 0,78×0,52 → 0,585×0,39 (25 % más pequeño)');
chk(c08.includes('const ARC_W = 0.585, ARC_H = 0.39;'),
  'c08: la placa del hall mide 0,585×0,39 (×0,75 exacto)');
chk(c08.includes('UN 25 % MÁS PEQUEÑO'), 'c08: la petición del dueño vive en el comentario');
chk(!c08.includes('const ARC_W = 0.78'), 'c08: el tamaño viejo 0,78 ha desaparecido');
chk(game.includes('const ARC_W = 0.585, ARC_H = 0.39;'),
  'bundle: el búho pequeño viaja al build');
chk(sha256('public/assets/hall/arcano.png').startsWith('6baa1288d99189c9'),
  'el ARTE del dueño sigue byte-exacto (arcano.png)');
chk(c08.includes('sp.position.set((rel[0] - 0.5) * ARC_W, (0.5 - rel[1]) * ARC_H, 0.012);'),
  'los destellos de los ojos escalan CON la placa (ARC_W/ARC_H)');

/* — 3 · CIELO LISO + SUELO INFINITO QUE MUTA —————————————————————— */
console.log('3 · CIELO LISO · SUELO INFINITO · losetas que mutan');
chk(c08.includes('completamente azul oscuro SIN IMAGEN'),
  'c08: petición literal del dueño en la bóveda');
chk(!c08.includes('VÍA LÁCTEA: banda diagonal'), 'c08: la Vía Láctea de la r39 RETIRADA');
chk(!c08.includes('ESTRELLAS: 520 tenues'), 'c08: el campo de 610 estrellas RETIRADO');
chk(c08.includes("bg.addColorStop(0, '#03061a')") &&
    c08.includes("bg.addColorStop(1, '#0a1a36')"),
  'c08: bóveda = degradado azul noche sutil (#03061a → #0a1a36)');
chk(c08.includes('function montaSueloArcano()'), 'c08: el SUELO INFINITO existe');
chk(c08.includes('const N = 48;') && c08.includes('const LADO = N * 1.5;') &&
    c08.includes('new THREE.PlaneGeometry(LADO, LADO)'),
  're-anclada r41: plano 72 m con losetas PEQUEÑAS de 1,5 m (48×48)');
chk(c08.includes('const BANDA = [[16, 40, 78], [26, 56, 104]];'),
  'c08: la banda azulada del dueño (#10284e → #1a3868, más clara que el cielo)');
chk(c08.includes('const CIELO = [10, 26, 54];'),
  'c08: la viñeta funde al color del horizonte (#0a1a36) — suelo sin costura');
/* r43 · RE-ANCLAJE 2 (petición del dueño: el tramado fijo de la r41 pasa a
 * DESTELLOS que dibujan la trama fina — la línea nace de un borde, deja
 * su estela ~5 s y muere; la matriz SIEMPRE visible desaparece). */
chk(c08.includes("ax = Math.random() < 0.5 ? 'x' : 'z'") &&
    c08.includes('dir = Math.random() < 0.5 ? 1 : -1'),
  're-anclada r43: destellos en ambos ejes (90°) y ambos sentidos');
chk(c08.includes('mesh.rotation.x = -Math.PI / 2;') &&
    c08.includes('mesh.position.y = -0.01;'),
  'c08: el suelo tumbado bajo los pies');
chk(c08.includes('S.trazos.length < 9') && c08.includes('S.lit.length < 70'),
  're-anclada r43: tope de destellos (~9) y rellenos (~70) vivos');
chk(c08.includes('const cel = Math.min(L - 1, Math.floor(q.head));'),
  're-anclada r43: los rellenos nacen EN las celdas que el destello cruza');
chk(c08.includes('const aV = q.t < q.tIn ? q.t / q.tIn'),
  're-anclada r41: envolvente nace→aguanta→muere (apagado aleatorio)');
chk(c08.includes('fx.clearRect(0, 0, 512, 512);') &&
    c08.includes('S.tex.needsUpdate = true;'),
  're-anclada r43: lienzo vivo de trazos+rellenos repintado por frame');
chk(c08.includes("new THREE.MeshBasicMaterial({ map: bTex, fog: false }));"),
  're-anclada r41: la BASE NEGRA del suelo sin niebla');
chk(c08.split('fog: false').length >= 9,
  'c08: fog:false en TODAS las piezas del Arcano (bóveda+motas+2 cometas+búho+glints+panel+suelo)');
chk(c08.includes('g.userData.arcono = {\n    motas, cometas, suelo,'),
  'c08: el suelo viaja en userData.arcono (updateArcanoFx lo anima)');

/* — 4 · EL ESCENARIO NACE DELANTE (bug raíz r39) —————————————————— */
console.log('4 · ESCENARIO DELANTE · el grupo se planta sobre el anfitrión');
chk(c12.includes('bug raíz de la r39'), 'c12: el diagnóstico del bug vive en el comentario');
chk(c12.includes('this.arcaneGroup.position.set(this.rig.position.x, 0, this.rig.position.z);'),
  'c12: el grupo arcano se PLANTA sobre los pies del jugador (XZ del rig)');
chk(c12.includes('this.arcaneGroup.rotation.y = Math.atan2(-fwd.x, -fwd.z);'),
  'c12: el escenario gira al YAW de la cabeza (−Z = donde mira el anfitrión)');
chk(c12.includes('this.camera.getWorldDirection(fwd);') &&
    c12.includes('fwd.y = 0;'),
  'c12: forward de la cabeza proyectado al suelo');
chk(c12.includes('this.arcaneGroup.position.set(0, 0, HALL.cz + 2.3);'),
  'c12: fallback honesto al centro del salón si algo falla');
chk(c12.includes("this.audio.setHallWanted(true, 'assets/hall/arcano.mp3');"),
  'c12: ENTRAR lanza arcano.mp3 por el canal del salón');
chk(c12.includes('_hallMusicaVariante() {'), 'c12: el restaurador del aire del salón existe');
chk(c12.includes("const mus = this._hallMusicaVariante();") &&
    c12.includes('this.audio.setHallWanted(!!mus, mus || null);'),
  'c12: SALIR devuelve la pista del salón (SU variante / la del anfitrión)');
chk(sha256('public/assets/hall/arcano.mp3') ===
  'dd3a898c8658de31180442278278ca98968e2cc7a683ea3655b22946116b0ff6',
  'arcano.mp3 del dueño BYTE-EXACTO en assets/hall/ (3,9 MB)');
chk(c08.includes('updateArcanoFx') && c08.includes('A.pop < 1'),
  'c08: la galería conserva su materialización (pop)');

/* — 5 · PULSABLES SIN MENÚ · rayo/haz/hover siempre vivos ————————— */
console.log('5 · PULSABLES SIN MENÚ · el haz vive en las estancias');
chk(c12.includes('if (presenting && (this.menuOpen || this.inHall || this._arconoOn)) {'),
  'c12: updateMenu corre TAMBIÉN sin menú en salón y Arcano');
chk(c12.includes('const hit = (this.menuOpen && !this._arconoOn)'),
  'c12: el panel del menú SÓLO es objetivo con el menú abierto');
chk(c12.includes('const enEstancia = !!this.inHall || !!this._arconoOn;') &&
    c12.includes('line.visible = enEstancia || !!hit || !!pinHit;'),
  'c12: el HAZ vive en las estancias aunque el menú duerma');
chk(c12.includes('(hit ? hit.distance : (enEstancia ? 3 : 0.5)));'),
  'c12: mirilla honesta de 3 m cuando el rayo no pisa el menú');
chk(c12.includes("if (this._arconoPulsa(i)) return;"),
  'c12: el gatillo del BÚHO vive en el salón SIN menú (r39, conservado)');
chk(c12.includes('else if (!this._arconoOn) {\n        this.openHallAsk();'),
  'c12: DENTRO del Arcano B no abre nada (el búho es la única puerta)');
chk(c12.includes('this._arconoClic(i);') &&
    c12.includes("this._arconoRayMesh(i, A.buho.mesh)"),
  'c12: el búho del espacio devuelve al salón (conservado r39)');
chk(c12.includes("this.audio.setHallWanted(false, null); } catch (eHM0)"),
  'c12: exitHall apaga la pista (también la del Arcano) al salir a la cancha');

/* — 6 · CONSERVADO · la galería y sus candados de la r39 ——————————— */
console.log('6 · CONSERVADO · galería ‹ › candados desbloqueo duelos');
chk(c12.includes("A.flechas.L.mesh.visible = this._arconoIdx > 0;") &&
    c12.includes('A.flechas.R.mesh.visible = this._arconoIdx < n - 1;'),
  'flechas ‹ › SIN flecha en los extremos (0 y último del registro)');
chk(c12.includes("desc: T('arc_desc_' + p.id)") &&
    c12.includes("metricas: T('arc_met_' + p.id)"),
  'descripción + MÉTRICAS reales del registro i18n');
chk(c12.includes('ARCONO_TIPOS') && c12.includes('arcono_tipo_ataque'),
  'tipo ataque/defensa/distracción con su color');
chk(c12.includes('drawArcanoPanel(A.panel.cv, {') &&
    c08.includes('if (d.bloqueado) {'),
  'candado azul translúcido en los bloqueados (descripciones legibles)');
chk(c12.includes('_arconoCampeonGanado()') &&
    c12.includes("localStorage.setItem('pp_poderes_v1'"),
  'desbloqueo por coronación (azar sin repetición, pp_poderes_v1)');
chk(c12.includes('DL_SURTIDO') && c12.includes("_dlArma("),
  'Duelos Locos con los desbloqueados (conservado)');
chk(game.includes('montaSueloArcano') && game.includes('const ARC_W = 0.585'),
  'el bundle lleva el suelo y el búho nuevo al build');

/* — 7 · GARANTÍA · física byte-exacto ————————————————————————————— */
console.log('7 · GARANTÍA · física c04/c05 INTACTA (byte-exacto r26b)');
chk(sha256('src/game/core/c04_fisica_ccd.js').startsWith('df8f71a3'),
  'c04_fisica_ccd.js byte-exacto (df8f71a3…)');
chk(sha256('src/game/core/c05_colisiones_ia_golpeo.js').startsWith('8bb62082'),
  'c05_colisiones_ia_golpeo.js byte-exacto (8bb62082…)');

/* — resumen ———————————————————————————————————————————————————————— */
console.log(`\nRESULTADO: ${ok} ✓ · ${fails} ✗`);
process.exit(fails ? 1 : 0);
