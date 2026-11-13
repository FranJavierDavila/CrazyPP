#!/usr/bin/env node
/* CRAZY PING PONG · r41 · v3.6.153-SDK6 · FASE 156 · TEST: EL ARCANO
 * HOLOGRÁFICO — el pulido del dueño sobre el espacio arcano (ocho
 * informes en uno):
 *
 *   1 · MOTAS DE POLVO — «Las partículas flotantes más pequeñas y
 *       circulares, como motas de polvo»: textura radial (punto REDONDO,
 *       jamás el cuadrado del PointsMaterial pelado) y la mitad de
 *       tamaño (0,055 → 0,026).
 *
 *   2 · EL SUELO NEGRO DE LOSETAS — «El patrón de losetas del suelo más
 *       pequeñas y mejor definidas… el suelo sea negro y se descubran
 *       las losetas en posiciones aleatorias: se verán las LÍNEAS de la
 *       matriz de losetas pero su relleno azul será aleatorio, unas
 *       aparecen otras se apagan de forma completamente aleatoria»:
 *       BASE negra (radial al color del horizonte #0a1a36 — costura
 *       imposible), MATRIZ estática de 48×48 losetas de 1,5 m con sus
 *       líneas SIEMPRE visibles, y RELLENOS vivos (nacen→aguantan→
 *       mueren AL AZAR con la banda azul del dueño).
 *
 *   3 · FLECHAS INTERCAMBIADAS — «las flechas están al revés,
 *       intercambiar los iconos: la flecha izquierda en la parte derecha
 *       y la flecha derecha en la parte izquierda»: el chevron ‹ vive en
 *       x +0,93 y el › en x −0,93 (el ICONO manda, no el lado).
 *
 *   4 · ICONOS A SANGRE COMPLETA — «Todos los iconos deben ser más
 *       grande, es la forma que tenemos de identificarlos, deben ocupar
 *       TODO el espacio que tiene el círculo azul que los perimetra»:
 *       escala 1,28R → 1,96R recortada al círculo (sin letterbox), y el
 *       icono se atenúa cuando el poder está bloqueado.
 *
 *   5 · APARICIÓN HOLOGRÁFICA — «La aparición de los paneles es muy
 *       pobre, me gustaría un efecto de holograma que se va formando,
 *       futurista y llamativo, con disolución»: DOS lienzos (cv = ficha
 *       completa, holo = lienzo vivo) y arconoHoloFrame compone bandas
 *       que viajan, disolución de motas, barrido de condensación,
 *       parpadeo de encendido y aberración que se cierra (k = 0..1,
 *       ~1,1 s; a k=1 copia exacta y duerme).
 *
 *   6 · LA VOZ PRESENTA CADA PODER — «Cada poder debe ser presentado
 *       mediante la voz»: _arconoRepinta llama a _vozSel (nombre corto
 *       embebido ES/EN, la misma vía del selector); en la ENTRADA el
 *       hint habla primero y el poder entra 2,3 s después (UNA voz
 *       viva, jamás dos a la vez).
 *
 *   7 · HALO EN LOS OJOS DEL BÚHO — «El buho puede tener un efecto de
 *       halo en sus ojos animado que oscila de azul a rojo»: el color de
 *       los dos glints del espacio viaja 0x49b6ff ↔ 0xff3524 con un seno
 *       lento y el halo respira con la misma fase.
 *
 *   8 · CANDADO FLOTANTE CON HALO ROJO — «Los candados deben situarse
 *       un poco hacia adelante del icono del poder, con un halo animado
 *       rojo que indica su bloqueo. La posición no debe tapar el icono
 *       pero debe ser claramente visible, halo pulsante rojo»: GRUPO
 *       propio delante del medallón (z −2,28 vs panel −2,35, borde
 *       inf-derecho del círculo), glifo azul en SU lienzo
 *       (drawArcanoCandado) y sprite de HALO ROJO pulsante animado en
 *       updateArcanoFx; c12 sincroniza la visibilidad con el estado REAL.
 *
 *   CONSERVADO de la r39/r40: galería automática (tipo+desc+métricas),
 *   flechas SIN flecha en los extremos, desbloqueo por coronación,
 *   Duelos Locos, escenario DELANTE, pulsables sin menú y arcano.mp3.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 sha256 BYTE-EXACTO contra la r26b
 *   (d792b5e7… / b195a0db…).
 *
 * Uso: node --no-warnings scripts/test_r41_arcano_holo_v36139.mjs
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

/* — 1 · SELLOS · v3.6.153-SDK6 · FASE 156 ————————————————————————— */
console.log('1 · SELLOS · v3.6.153-SDK6 · FASE 156 · CONFIG_PIELES r62: LAS PIELES SON DATA-DRIVEN — los metadatos de las 9 pieles de pala (id · nombre ES/EN · coste min o días/vía racha · pintura tex/edge/grip · anim · modelUrl GLB) viven en c02 — séptima parada tras ARCANO_CFG/física/menú/audio/dificultad/torneos+logros (lector c13: SKINS = CONFIG_PIELES.pieles · RACHA_SKINS por filtro · orden/save/pintura/tienda intactos)');
chk(vjson.version === '3.6.153-SDK6', 'VERSION.json: 3.6.153-SDK6');
chk(vjson.fase === 156, 'FASE 156');
chk(vjson.faseNombre === 'CONFIG_PIELES r62: LAS PIELES SON DATA-DRIVEN — los metadatos de las 9 pieles de pala (id · nombre ES/EN · coste min o días/vía racha · pintura tex/edge/grip · anim · modelUrl GLB) viven en c02 — séptima parada tras ARCANO_CFG/física/menú/audio/dificultad/torneos+logros (lector c13: SKINS = CONFIG_PIELES.pieles · RACHA_SKINS por filtro · orden/save/pintura/tienda intactos)', 'faseNombre = CONFIG_PIELES r62: LAS PIELES SON DATA-DRIVEN — los metadatos de las 9 pieles de pala (id · nombre ES/EN · coste min o días/vía racha · pintura tex/edge/grip · anim · modelUrl GLB) viven en c02 — séptima parada tras ARCANO_CFG/física/menú/audio/dificultad/torneos+logros (lector c13: SKINS = CONFIG_PIELES.pieles · RACHA_SKINS por filtro · orden/save/pintura/tienda intactos)');
chk(vjson.sdk === '1.6.0', 'SDK de la casa intacto (1.6.0)');
// r46 · RE-ANCLAJE: build legítimamente cambiado por la r46 (gobernador + worker v3)
chk(vjson.tamano === 11578430, 'tamaño del build: 11.507.255 B (re-anclado r46)');
chk(vjson.golden ===
  'c2b75fe924b10a1a0161fedfda4a88f005910356e617c8407c2e6a2dcebf24e0',
  'VERSION.json golden 42d07e64… (re-anclado r46)');
chk(sha256('public/game.html') === vjson.golden,
  'golden = sha256 real del build (byte-exacto)');
chk(game.includes('3.6.153-SDK6'), 'bundle con sello vigente');
chk(c00.includes("const VERSION = '3.6.153-SDK6'"), 'sello c00 = 3.6.153-SDK6');
chk(lee('public/sw.js').includes("CACHE = 'crazypp-v3.6.153-SDK6'"),
  'sw.js CACHE v3.6.153-SDK6 (purga de cachés viejas)');
chk(cuerpo.includes('>V3.6.153-SDK6</span>'), 'badge V3.6.153-SDK6 en 03_body');
chk(lee('src/app/descargas/page.tsx').includes('v36139-sdk6'),
  'hub /descargas sellado a v36139-sdk6');

/* — 2 · MOTAS DE POLVO · circulares y más pequeñas ———————————————— */
console.log('2 · MOTAS DE POLVO · circulares (textura radial) y la mitad de tamaño');
chk(c08.includes('const dot = spriteRadial(3,'), 'c08: textura radial de la mota (punto REDONDO)');
chk(c08.includes('size: 0.026, map: dot,'), 'c08: la MITAD de tamaño (0,055 → 0,026)');
chk(!c08.includes('size: 0.055'), 'c08: el tamaño cuadrado viejo 0,055 desapareció');
chk(c08.includes('map: dot, transparent: true, opacity: 0.9'),
  'c08: la mota lleva SU textura (map: dot)');
chk(game.includes('const dot = spriteRadial(3,'), 'bundle: las motas de polvo viajan al build');

/* — 3 · EL SUELO NEGRO DE LOSETAS ————————————————————————————————— */
console.log('3 · SUELO NEGRO · matriz fija de 48×48 · rellenos que nacen y mueren');
chk(c08.includes('function montaSueloArcano()'), 'c08: montaSueloArcano (rediseñada r41)');
chk(c08.includes('const N = 48;') && c08.includes('const LADO = N * 1.5;'),
  'c08: losetas PEQUEÑAS de 1,5 m (48×48 — la r40 eran 9×9 de 8 m)');
chk(c08.includes("bgR.addColorStop(0, '#03060d');"), 'c08: la BASE es NEGRA bajo los pies');
chk(c08.includes("bgR.addColorStop(1, 'rgb(' + CIELO[0] + ',' + CIELO[1] + ',' + CIELO[2] + ')');"),
  'c08: la base funde al color del horizonte (#0a1a36 — costura imposible)');
/* r43 · RE-ANCLAJE (petición del dueño: «eliminar del suelo el tramado de
 * líneas… destellos que dejan una estela que es la propia línea, que se ve
 * unos 5 segundos y desaparece»): la MATRIZ ESTÁTICA de la r41 desaparece —
 * las 5 agujas de líneas siempre visibles/nodos/rellenos aleatorios se
 * sustituyen por las del trazado de destellos (test_r43 las detalla). */
chk(c08.includes('S.trazos.push({') && c08.includes("ax, ln, dir,"),
  'c08 [r43]: el trazado de DESTELLOS sustituye a la matriz estática (re-anclado)');
chk(c08.includes('const VIDA = 5.0;'),
  'c08 [r43]: la línea dibujada aguanta ~5 s (re-anclado)');
chk(c08.includes('const BANDA = [[16, 40, 78], [26, 56, 104]];'),
  'c08: el RELLENO usa la banda azul del dueño (#10284e → #1a3868)');
chk(c08.includes('lit: [],        // rellenos vivos de celdas atravesadas'),
  'c08 [r43]: rellenos vivos LIGADOS a las celdas que los destellos cruzan (re-anclado)');
chk(c08.includes('if (cel !== q.ultima && S.lit.length < 70 && Math.random() < 0.20) {'),
  'c08 [r43]: los rellenos nacen EN el recorrido del destello (re-anclado)');
chk(c08.includes('t: 0, tIn: 0.3 + Math.random() * 0.5, hold: 1.2 + Math.random() * 2.4,'),
  'c08 [r43]: vida aleatoria del relleno (nace → aguanta → muere) (re-anclado)');
chk(c08.includes('if (q.t >= fin) { S.lit.splice(k, 1); continue; }'),
  'c08: las losetas SE APAGAN solas (unas aparecen, otras desaparecen)');
chk(c08.includes('const al = q.alfa * aV * (1 - rr * rr);'),
  'c08: el relleno se disuelve hacia el horizonte (viñeta)');
chk(c08.includes('const mesh = new THREE.Mesh(new THREE.PlaneGeometry(LADO, LADO),') &&
    c08.includes('new THREE.MeshBasicMaterial({ map: bTex, fog: false }));'),
  'c08: base/malla/rellenos con fog:false (la niebla jamás toca el suelo)');
chk(c08.includes('malla.position.y = 0.002;') && !c08.includes('fills.position.y'),
  'c08 [r43]: el trazado vivo flota sobre la base (un solo plano de líneas+rellenos — sin z-fighting) (re-anclado)');
chk(c08.includes("tCtx: tcv.getContext('2d')"),
  'c08 [r43]: el estado vivo del suelo (trazos + lit) viaja en el userData (re-anclado)');

/* — 4 · FLECHAS INTERCAMBIADAS (glifos descruzados) ————————————————— */
console.log('4 · FLECHAS · ‹ a la IZQUIERDA · › a la DERECHA (icono = lado = acción)');
chk(c08.includes("const s = dir === 'L' ? 1 : -1;"),
  'c08: glifos DESCruzados — dir L dibuja ‹ (antes dibujaba ›)');
chk(!c08.includes("const s = dir === 'L' ? -1 : 1;"),
  'c08: el cruce viejo de glifos desapareció');
chk(c08.includes("mesh.position.set(k === 'L' ? -0.93 : 0.93, 1.32, -2.35);"),
  'c08: el ‹ vive a la IZQUIERDA (−0,93) y el › a la DERECHA (+0,93)');
chk(c08.includes('INTERCAMBIADOS (petición del dueño'),
  'c08: la petición del dueño vive en el comentario');
chk(c12.includes('A.flechas.L.mesh.visible = this._arconoIdx > 0;') &&
    c12.includes('A.flechas.R.mesh.visible = this._arconoIdx < n - 1;'),
  'c12: SIN ‹ en el 0 y SIN › en el último (el icono coincide con la acción)');
chk(c12.includes("this._arconoIdx = Math.min(PODERES_PALA.length - 1, this._arconoIdx + 1);") &&
    c12.includes('this._arconoIdx = Math.max(0, this._arconoIdx - 1);'),
  'c12: ‹ retrocede · › avanza (icono = acción, intacto)');

/* — 5 · ICONOS A SANGRE COMPLETA —————————————————————————————————— */
console.log('5 · ICONOS · TODO el medallón (1,96R recortado al círculo)');
chk(c08.includes('const k = (icR * 1.96) / Math.max(iw, ih);'),
  'c08: escala 1,96R (ocupa TODO el círculo; antes 1,28R)');
chk(!c08.includes('const k = (icR * 1.28)'), 'c08: el margen viejo 1,28R desapareció');
chk(c08.includes('x.arc(icX, icY, icR - 1, 0, Math.PI * 2);') &&
    c08.includes('x.clip();'),
  'c08: recortado al PROPIO círculo (sin letterbox)');
chk(c08.includes('if (d.bloqueado) {') && c08.includes('x.globalAlpha = 0.42;'),
  'c08: bloqueado → icono ATENUADO (el candado destaca, nada lo tapa)');
chk(game.includes('const k = (icR * 1.96)'), 'bundle: el icono grande viaja al build');

/* — 6 · LA APARICIÓN HOLOGRÁFICA —————————————————————————————————— */
console.log('6 · HOLOGRAMA · la ficha se FORMA (bandas, disolución, barrido)');
chk(c08.includes('function arconoHoloFrame(x, base, k, sem) {'),
  'c08: arconoHoloFrame (la composición del holograma)');
chk(c08.includes('const panHolo = hallCanvas(1024, 700);') &&
    c08.includes('panHolo.getContext(\'2d\').drawImage(panCv, 0, 0);'),
  'c08: DOS lienzos — cv (ficha completa) + holo (lienzo vivo)');
chk(c08.includes('panel: { mesh: panMesh, cv: panCv, tex: panTex, holo: panHolo }'),
  'c08: el panel viaja con cv+holo en el userData');
chk(c08.includes('const rev = Math.min(1.12, k * 1.3);'),
  'c08: frente de condensación (el barrido que baja FORMANDO)');
chk(c08.includes("x.globalCompositeOperation = 'destination-out';"),
  'c08: DISOLUCIÓN real (motas que se re-componen)');
chk(c08.includes("x.globalCompositeOperation = 'lighter';"),
  'c08: banda de barrido aditiva (futurista, con glow)');
chk(c08.includes('const viaja = (1 - k) * (1 - y / H);'),
  'c08: bandas horizontales que viajan y se asientan');
chk(c08.includes('arconoHoloFrame(P.holo.getContext(\'2d\'), P.cv, A.pop, A.holoSem);'),
  'c08: updateArcanoFx compone cv→holo mientras pop < 1');
chk(c08.includes('A.pop = Math.min(1, A.pop + dt * 0.92);'),
  'c08: ~1,1 s de formación (llamativo pero no eterno)');
chk(c08.includes('c2.drawImage(P.cv, 0, 0);'),
  'c08: condensada → copia EXACTA y la textura duerme (coste cero)');
chk(c12.includes('A.pop = 0;   // materialización del poder entrante'),
  'c12: cada poder ENTRA materializándose (conservado)');
chk(c12.includes('drawArcanoPanel(A.panel.cv, {'),
  'c12: pinta la ficha COMPLETA en cv (el holograma la compone)');
chk(game.includes('function arconoHoloFrame('), 'bundle: el holograma viaja al build');

/* — 7 · LA VOZ PRESENTA CADA PODER ————————————————————————————————— */
console.log('7 · VOZ · cada poder se OYE (nombre corto embebido ES/EN)');
chk(c12.includes('_arconoRepinta(conVoz) {'), 'c12: repinta con control de voz');
chk(c12.includes('try { this._vozSelSolemne(p.id); } catch (eV1) { /* sin audio: nunca rompe */ }'),
  'c12: la voz SOLEMNE r47 suena al materializarse (flechas ‹ ›)');
chk(c12.includes('this._arconoRepinta(false);   // r41 · el hint habla primero…'),
  'c12: en la ENTRADA el hint habla primero');
chk(c12.includes("}, 2300);"), 'c12: la voz del poder entra 2,3 s después (UNA voz viva)');
chk(c12.includes('if (p0) this._vozSelSolemne(p0.id);'), 'c12: el poder del índice vivo se presenta SOLEMNE');
chk(c12.includes('_vozSelFuente(key) {'), 'c12: las 14 voces embebidas ES/EN intactas');

/* — 8 · HALO EN LOS OJOS DEL BÚHO (azul ↔ rojo) ——————————————————— */
console.log('8 · BÚHO · halo en los ojos OSCILANDO azul ↔ rojo');
chk(c08.includes('const _ARCO_OJO_A = new THREE.Color(0x49b6ff);') &&
    c08.includes('const _ARCO_OJO_B = new THREE.Color(0xff3524);'),
  'c08: los dos polos del halo (azul búho ↔ rojo bloqueo)');
chk(c08.includes('const tO = 0.5 + 0.5 * Math.sin(now * 1.5);'),
  'c08: seno lento (oscila y VUELVE, jamás un salto)');
chk(c08.includes('_arcoOjoT.copy(_ARCO_OJO_A).lerp(_ARCO_OJO_B, tO);') &&
    c08.includes('B.glints[0].material.color.copy(_arcoOjoT);'),
  'c08: el COLOR de los destellos viaja la banda azul↔rojo');
chk(c08.includes('const scO = 0.115 + tO * 0.05;') &&
    c08.includes('B.glints[0].scale.setScalar(scO);'),
  'c08: el HALO respira con la misma fase (escala del sprite)');
chk(c08.includes('_arcoOjoT = new THREE.Color();'),
  'c08: raspador de módulo (cero basura por frame)');

/* — 9 · EL CANDADO FLOTANTE con halo rojo pulsante ———————————————— */
console.log('9 · CANDADO · DELANTE del icono · halo rojo pulsante · no tapa');
chk(c08.includes('export function drawArcanoCandado(cv) {'),
  'c08: drawArcanoCandado (glifo en SU lienzo, exportado)');
chk(c08.includes('x.arc(lx, ly - ls * 0.18, ls * 0.30, Math.PI, 0);'),
  'c08: el candado azul de siempre (cuerpo + arco) en su lienzo');
chk(c08.includes("x.strokeStyle = 'rgba(120,205,255,0.95)'"),
  'c08: candado en TONOS AZULES (la estética del búho, conservada)');
chk(c08.includes("x.strokeStyle = 'rgba(255,70,50,0.6)';"),
  'c08: el aro del discoscape AVISA en rojo (bloqueo)');
chk(c08.includes('candado.position.set(-0.612, 1.585, -2.20);'),
  'c08: DELANTE del medallón — r47: un paso MÁS (z −2,20 vs panel −2,35, jamás coplanar: se ve SIEMPRE) con renderOrder fijo 6/7');
chk(c08.includes('candado.visible = false;'),
  'c08: nace oculto (sólo los bloqueados lo enseñan)');
chk(c08.includes("map: spriteRadial(4, 'rgba(255,150,120,0.92)', 'rgba(255,45,30,0.4)', 'rgba(255,0,0,0)'),"),
  'c08: sprite del HALO ROJO (aditivo, fog:false)');
chk(c08.includes('candado: { grupo: candado, halo: candHalo }, pop: 1, holoSem: 0,'),
  'c08: el candado viaja en userData.arcono');
chk(c08.includes('const pC = 0.5 + 0.5 * Math.sin(now * 3.2);') &&
    c08.includes('CD.halo.material.opacity = 0.34 + pC * 0.5;'),
  'c08: HALO PULSANTE animado (escala + opacidad por seno)');
chk(c08.includes('CD.halo.scale.setScalar(0.24 + pC * 0.13);'),
  'c08: el halo RESPIRA (0,24 → 0,37)');
chk(c12.includes('if (A.candado) A.candado.grupo.visible = bloqueado;'),
  'c12: visibilidad sincronizada con el estado REAL de desbloqueo');
chk(c08.includes('const lx = W / 2, ly = H * 0.56, ls = W * 0.5;'),
  'c08: el glifo centrado en SU lienzo 128×128 (independiente del panel)');

/* — 10 · CONSERVADO · galería, desbloqueo, duelos, melodía ————————— */
console.log('10 · CONSERVADO · galería automática · desbloqueo · arcano.mp3');
chk(c08.includes('montaMotas(240)'), '240 motas (conservadas, ahora de polvo)');
chk(c08.includes("x.fillText('◈ ' + (d.tipoTexto || '')"), 'TIPO en la ficha (conservado)');
chk(c08.includes("'◆ ' + (d.metricasLbl || 'Métricas')"), 'MÉTRICAS en la ficha (conservado)');
chk(c12.includes("desc: T('arc_desc_' + p.id)") && c12.includes("metricas: T('arc_met_' + p.id)"),
  'descripción + métricas reales del registro (conservado)');
chk(c12.includes('_arconoCampeonGanado()') && c12.includes("localStorage.setItem('pp_poderes_v1'"),
  'desbloqueo por coronación (conservado)');
chk(c12.includes('DL_SURTIDO'), 'Duelos Locos con los desbloqueados (conservado)');
chk(c12.includes("this.audio.setHallWanted(true, 'assets/hall/arcano.mp3');"),
  'arcano.mp3 suena en el espacio (conservado r40)');
chk(c12.includes('const mus = this._hallMusicaVariante();'),
  'salir restaura la pista del salón (conservado r40)');
chk(c12.includes('this.arcaneGroup.position.set(this.rig.position.x, 0, this.rig.position.z);'),
  'el escenario nace DELANTE (conservado r40)');
chk(c12.includes('if (presenting && (this.menuOpen || this.inHall || this._arconoOn)) {'),
  'pulsables SIN menú (conservado r40)');
chk(c08.split('fog: false').length >= 13,
  'fog:false en TODAS las piezas del Arcano (+base/malla/rellenos/candado)');

/* — 11 · GARANTÍA · física byte-exacto ————————————————————————————— */
console.log('11 · GARANTÍA · física c04/c05 INTACTA (byte-exacto r26b)');
chk(sha256('src/game/core/c04_fisica_ccd.js').startsWith('d792b5e7'),
  'c04_fisica_ccd.js byte-exacto (d792b5e7…)');
chk(sha256('src/game/core/c05_colisiones_ia_golpeo.js').startsWith('b195a0db'),
  'c05_colisiones_ia_golpeo.js byte-exacto (b195a0db…)');

/* — resumen ———————————————————————————————————————————————————————— */
console.log(`\nRESULTADO: ${ok} ✓ · ${fails} ✗`);
process.exit(fails ? 1 : 0);
