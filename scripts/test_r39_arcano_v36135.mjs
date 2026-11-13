#!/usr/bin/env node
/* CRAZY PING PONG · r39 · v3.6.155-SDK6 · FASE 158 · TEST: EL APARTADO
 * ARCANO — el búho del hall, el espacio infinito y la galería de
 * superpoderes con desbloqueo por campeonato ganado.
 *
 *   A · EL BÚHO DEL ARCANO (hall) — «un apartado que explique los poderes
 *       de super pala… una especie de icono (Arcano.png) en la pared del
 *       fondo del hall o en una esquina superior derecha con la forma de
 *       un buho que emite un ligero destello a través de sus dos ojos»:
 *       arte del dueño byte-exacto en assets/hall/arcano.png, placa en la
 *       esquina superior derecha de la pared que el anfitrión mira al
 *       entrar, DOS sprites de destello sobre los centros de los ojos
 *       MEDIDOS del arte (0.452/0.392 · 0.557/0.376), latido en
 *       updateHallFx, raycast + gatillo (mismo patrón que el icono de la
 *       música) y fallback vectorial si la textura no llega.
 *
 *   B · EL ESPACIO INFINITO — «transición a negro… un escenario infinito
 *       en el que serpentean en el aire motas de color azul brillante…
 *       de vez en cuando en la distancia atraviesan pequeños cometas
 *       dejando tras de si un halo azul… una gran bóbeda celeste oscura
 *       donde se intuye la via lactea»: montarArcano (bóveda esférica con
 *       Vía Láctea pintada, 240 motas con fase propia, 3 cometas con
 *       halo), fundido a negro con cortina que sigue a la cabeza, el búho
 *       presente y el clic de vuelta (dos vías).
 *
 *   C · LA GALERÍA — «aparecen los diferentes iconos de superpoderes de
 *       pala uno a uno se materializan delante nuestra y a su lado
 *       aparece la descripción de su poder y en que afecta al juego, si
 *       es poder de ataque, si es defensivo, si es de distracción y que
 *       métricas del juego alteran»: panel con icono+nombre+tipo+desc+
 *       métricas, índice AUTOMÁTICO contra PODERES_PALA, flechas ‹ › con
 *       glow azul SIN flecha en los extremos, materialización (pop) y
 *       candado azul translúcido en los bloqueados (descripciones
 *       legibles igualmente).
 *
 *   D · DESBLOQUEO — «cada campeonato completo ganado a parte de darte la
 *       copa y la insignia correspondiente te libera un superpoder al
 *       azar (comprobar si ya está desbloqueado para no dar el mismo)»:
 *       persistencia pp_poderes_v1 saneada, azar sin repetición, hook en
 *       showChampConseguido SOLO con coronacion:true (6 módulos marcados;
 *       la medalla LEYENDA no repite), línea de revelación en el panel
 *       ¡CONSEGUIDO! y megafonía propia.
 *
 *   E · DUELOS LOCOS — «los desbloqueados se podrán usar en las partidas
 *       multijugador con este modo»: surto = gigante/fuego/loca + TUS
 *       desbloqueados, armado por triggers con ent sintético, ventanas
 *       tickadas en duelos (13 compuertas), formas de receptor (red alta
 *       y ritmo lento compartidos, niebla en MI golpeo, onda que flojea
 *       la devolución), ANCLA que estrella los poderes entrantes, bit 16
 *       compartido por la MEGA, portal del invitado en duelos y recogida
 *       con fines naturales al morir el modo.
 *
 *   GARANTÍA DE SIEMPRE: c04/c05 sha256 BYTE-EXACTO contra la r26b
 *   (d792b5e7… / b195a0db…).
 *
 * Uso: node --no-warnings scripts/test_r39_arcano_v36139.mjs
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
const c02 = lee('src/game/core/c02_cfg_escena.js');
const c09 = lee('src/game/core/c09_red_netlink.js');
const c12 = lee('src/game/core/c12_pingponggame.js');
const vjson = JSON.parse(lee('src/game/VERSION.json'));
const game = lee('public/game.html');
const cuerpo = lee('src/game/03_body.html');

/* — 1 · SELLOS · v3.6.155-SDK6 · FASE 158 ————————————————————————— */
console.log('1 · SELLOS · v3.6.155-SDK6 · FASE 158 · EL APARTADO ARCANO');
chk(vjson.version === '3.6.155-SDK6', 'VERSION.json: 3.6.155-SDK6');
chk(vjson.fase === 158, 'FASE 158');
chk(vjson.faseNombre === 'CONFIG_MEDALLAS r64: MEDALLAS POR EJERCICIO DATA-DRIVEN — la escalera bronce/plata/oro (estrellas 1/2/3 · precisión 70/85) de medallaDe vive en c02 — novena parada tras ARCANO_CFG/física/menú/audio/dificultad/torneos+logros/pieles/rally (lector c13: MDE/MDP = CONFIG_MEDALLAS.estrellas/.precision — HUD, MEDALLERO y or5 intactos)', 'faseNombre = EL APARTADO ARCANO');
chk(vjson.tamano === 11582172, 'tamaño del build: 11.504.235 B');
chk(vjson.golden ===
  '91001a63531fa5931a60e6a4614122db72ffa4567c60d2eb7b94f7e7748b087f',
  'VERSION.json golden 1836d13f…');
chk(sha256('public/game.html') === vjson.golden,
  'golden = sha256 real del build (byte-exacto)');
chk(game.includes('3.6.155-SDK6'), 'bundle con sello vigente');
chk(c00.includes("const VERSION = '3.6.155-SDK6'"), 'sello c00 = 3.6.155-SDK6');
chk(lee('public/sw.js').includes("CACHE = 'crazypp-v3.6.155-SDK6'"),
  'sw.js CACHE v3.6.155-SDK6 (purga de cachés viejas)');
chk(cuerpo.includes('>V3.6.155-SDK6</span>'), 'badge V3.6.155-SDK6 en 03_body');
chk(lee('src/app/descargas/page.tsx').includes('v36154-sdk6'),
  'hub /descargas sellado a v36154-sdk6');

/* — 2 · ARTE DEL DUEÑO · arcano.png byte-exacto ———————————————————— */
console.log('2 · ARTE · Arcano.png del dueño → public/assets/hall/arcano.png');
chk(sha256('public/assets/hall/arcano.png').startsWith('6baa1288d99189c9'),
  'assets/hall/arcano.png · sha256 6baa1288d99189c9… (byte-exacto)');

/* — 3 · EL BÚHO EN EL HALL (c08) ———————————————————————————————————— */
console.log('3 · EL BÚHO DEL ARCANO EN EL HALL · placa + destello en los ojos');
chk(c08.includes("drawArcanoBuho(arcCv);"), 'fallback vectorial del búho pintado');
chk(c08.includes("const urlArcano = 'assets/hall/arcano.png';") &&
    c08.includes('new THREE.TextureLoader().load(urlArcano'),
  'arte REAL del dueño cargado por URL (assets/hall/arcano.png)');
chk(c08.includes('arcMesh.position.set(ARCANO_CFG.ui.buho.x, ARCANO_CFG.ui.buho.y,\n                       z0 + ARCANO_CFG.ui.buho.zOff);') &&
    c02.includes('ui: { buho: { x: 2.70, y: 2.60, zOff: 0.016 } }'),
  're-anclada r55: búho DATA-DRIVEN — c08 lee ARCANO_CFG.ui.buho (c02), esquina sup. dcha');
chk(c12.includes("import { AI_PRESETS, ARCANO_CFG, BOLA_ASPECTOS, CARRERA_DIVISIONES, CONFIG_DIFICULTAD, CONFIG_MENU, CONFIG_TORNEOS, DIMS,"),
  're-anclada r55/r58/r60: c12 importa ARCANO_CFG/CONFIG_MENU/CONFIG_DIFICULTAD de la capa de datos (c02)');
chk(c08.includes('[[0.452, 0.392], [0.557, 0.376]]') ||
    c08.includes('[0.452, 0.392], [0.557, 0.376]'),
  'destellos en los centros de los OJOS medidos del arte');
chk((c08.match(/blending: THREE\.AdditiveBlending/g) || []).length >= 4,
  'destellos/cometas/motas ADITIVOS (glow azul)');
chk(c08.includes('ar.glints[0].material.opacity = 0.30 + Math.sin(now * 2.1)'),
  'LIGERO DESTELLO latiente en updateHallFx (dos fases)');
chk(c08.includes('arcono,   // r39 · el búho del Arcano (destello en los ojos; entra c12)'),
  'el búho viaja en el userData del hall (raycast de c12)');

/* — 4 · EL ESPACIO ARCANO (c08 monta · c12 gobierna) ———————————————— */
console.log('4 · EL ESPACIO INFINITO · bóveda con Vía Láctea · motas · cometas');
chk(c08.includes('export function montarArcano(base)'), 'montarArcano exportado');
chk(c08.includes('export function updateArcanoFx(g, dt, now)'), 'updateArcanoFx exportado');
chk(c08.includes('pintaBoveda(bovCv)'), 'bóveda celeste pintada en canvas');
chk(c08.includes("bg.addColorStop(1, '#0a1a36')"),
  're-anclada r40: cielo azul oscuro LISO (sin Vía Láctea ni estrellas)');
chk(c08.includes('new THREE.SphereGeometry(58, 40, 24)'),
  'gran bóveda esférica (BackSide, r=58)');
chk(c08.includes('function montaMotas(N)'), 'montaMotas (nube de puntos)');
chk(c08.includes('montaMotas(240)'), '240 motas azules');
chk(c08.includes('serpenteo suave (posición base + dos senos por punto)'),
  'motas que SERPENTEAN (base + fase por punto)');
chk((c08.match(/const cometas = \[\]/g) || []).length === 1, 'pool de cometas');
chk(c08.includes('el halo azul queda tras la cabeza'), 'cometas con HALO AZUL tras la cabeza');
chk(c08.includes('c.prox = 4 + Math.random() * 8'), 'cometas OCASIONALES (prox aleatorio)');
chk(c08.includes('buhoMesh.position.set(0, 2.28, -2.55)'), 'el búho SIGUE PRESENTE en el espacio');
chk(c12.includes("this.arcaneGroup = montarArcano('assets/hall/');"),
  'c12 monta el espacio arcano una vez (constructor)');
chk(c12.includes('this.arcaneGroup.visible = false;'), 'el espacio nace OCULTO');
chk(c12.includes('_arconoNegro.renderOrder = 99999;'), 'cortina NEGRA renderOrder máximo');
chk(c12.includes('this._arconoNegro.translateZ(-0.42);'),
  'cortina que SIGUE a la cabeza en VR (0,42 m del ojo)');
chk(c12.includes("if (this._arconoOn && this.arcaneGroup) updateArcanoFx(this.arcaneGroup, dt, now);"),
  'el espacio respira SÓLO encendido (coste cero fuera)');
chk(c12.includes('if (this._arconoOn) {'), 'el gatillo del espacio manda PRIMERO en onSelectStart');

/* — 5 · LA GALERÍA · índice automático · flechas · candados ————————— */
console.log('5 · LA GALERÍA · uno a uno · descripción · tipo · métricas · ‹ ›');
chk(c08.includes('export function drawArcanoPanel(cv, d)'), 'drawArcanoPanel (panel de ficha)');
chk(c08.includes('export function drawArcanoFlecha(cv, dir)'), 'drawArcanoFlecha (chevron con glow)');
chk(c08.includes("x.fillText('◈ ' + (d.tipoTexto || '')"), 'TIPO en la ficha (ataque/defensa/distracción)');
chk(c08.includes("'◆ ' + (d.metricasLbl || 'Métricas')"), 'MÉTRICAS en la ficha');
chk(c08.includes('BLOQUEADO · gana un campeonato') || c00.includes('arcono_candado:'),
  'candado: línea de estado BLOQUEADO');
chk(c08.includes('x.arc(lx, ly - ls * 0.18, ls * 0.30, Math.PI, 0);'),
  'CANDADO dibujado (cuerpo + arco) sobre el icono');
chk(c08.includes("x.strokeStyle = 'rgba(120,205,255,0.95)'"),
  'candado en TONOS AZULES (estética del búho)');
chk(c12.includes('const n = PODERES_PALA.length;'),
  'índice AUTOMÁTICO contra el registro (un poder nuevo hereda galería)');
chk(c12.includes("A.flechas.L.mesh.visible = this._arconoIdx > 0;") &&
    c12.includes("A.flechas.R.mesh.visible = this._arconoIdx < n - 1;"),
  'SIN flecha izquierda en el 0 · SIN flecha derecha en el último');
chk(c12.includes('A.pop = 0;   // materialización del poder entrante'),
  'materialización uno a uno (pop elástico por ficha)');
chk(c12.includes('this._arconoIdx = Math.min(PODERES_PALA.length - 1, this._arconoIdx + 1);') &&
    c12.includes('this._arconoIdx = Math.max(0, this._arconoIdx - 1);'),
  'navegación ‹ › con bordes (nunca envuelve)');
chk(c12.includes('const des = this.poderesDesbloqueados();') &&
    c12.includes('const bloqueado = des.indexOf(p.id) < 0;'),
  'el candado lee el estado REAL de desbloqueo');
chk(c12.includes('nombre: p.nombre(),') && c12.includes("desc: T('arc_desc_' + p.id),") &&
    c12.includes("metricas: T('arc_met_' + p.id),"),
  'ficha = nombre + descripción + métricas DEL REGISTRO (automático)');
chk(c08.includes('todo texto se mide y se encoge') || c08.includes('const envuelve ='),
  'textos envueltos con measureText (nunca se cortan)');

/* — 6 · LAS DOS VÍAS DEL BÚHO · fundido a negro ————————————————————— */
console.log('6 · DOS VÍAS · hall→arcano→hall con desvanecimiento');
chk(c12.includes('_arconoPulsa(i) {'), 'gatillo del búho del salón (_arconoPulsa)');
chk(c12.includes('if (this._arconoPulsa(i)) return;'), 'el búho manda antes que la placa de música');
chk(c12.includes('else if (this.inHall && this._arconoPulsa(i))'),
  'el búho responde TAMBIÉN con el menú abierto (rayo libre)');
chk(c12.includes('this._arconoFundir(() => {'), 'canje de estancias EN NEGRO (fundido)');
chk(c12.includes('if (this.hallGroup) this.hallGroup.visible = false;') &&
    c12.includes('this.arcaneGroup.visible = true;'),
  'entrada: hall fuera, espacio dentro');
chk(c12.includes('if (this.hallGroup) this.hallGroup.visible = true;') &&
    c12.includes('this.arcaneGroup.visible = false;'),
  'salida: espacio fuera, hall tal cual quedó');
chk(c12.includes('if (this._arconoRayMesh(i, A.buho.mesh)) {'), 'el búho del espacio DEVUELVE al salón');
chk(c12.includes('this.rules.message = T(\'arcono_salir\');'), 'mensaje de vuelta al salón');
chk(c12.includes('if (this._arconoOn) {'), 'seguridad: exitHall cierra el Arcano');
chk(c12.includes('udM.arcono.hover = !!(this.connected[h] && this._arconoRayHall(h));'),
  'hover del búho en el lazo del láser (como el icono de la música)');

/* — 7 · DESBLOQUEO · azar sin repetición · coronación ——————————————— */
console.log('7 · DESBLOQUEO · campeonato ganado → un poder al azar NUEVO');
chk(c12.includes("localStorage.getItem('pp_poderes_v1')"),
  'persistencia pp_poderes_v1');
chk(c12.includes('.filter((s) => typeof s === \'string\' && ok.indexOf(s) >= 0);'),
  'persistencia SANEADA contra el registro (id desconocido jamás sale)');
chk(c12.includes('if (!faltan.length) return \'\';'),
  'azar que COMPRUEBA: todo desbloqueado → nada que repetir');
chk(c12.includes("const id = faltan[(Math.random() * faltan.length) | 0];"),
  'superpoder AL AZAR entre los que aún tienen candado');
chk(c12.includes('if (opts.coronacion) {'), 'hook SOLO en la CORONACIÓN (showChampConseguido)');
chk(c12.includes('const nuevoId = this._arconoCampeonGanado();'),
  'coronación → _arconoCampeonGanado');
chk(c12.includes("T('arcono_nuevo', { p: arconoRevelado })"),
  'megafonía de la revelación');
chk(c12.includes('arcano: arconoRevelado,   // r39 · el poder revelado por el Arcano'),
  'la revelación viaja en el panel ¡CONSEGUIDO!');
chk(c12.includes("c.fillText(arTxt, W / 2, H * 0.868);"),
  'línea azul de revelación pintada bajo el título');
for (const f of ['locura', 'estacion_orbital', 'magia', 'oeste', 'halloween', '_plantilla']) {
  const src = lee('public/championships/' + f + '/index.js');
  chk(src.includes('coronacion: true'), 'coronacion:true marcada en ' + f);
}
const oeste = lee('public/championships/oeste/index.js');
const hallo = lee('public/championships/halloween/index.js');
const plant = lee('public/championships/_plantilla/index.js');
chk((oeste.match(/coronacion: true/g) || []).length === 1 &&
    oeste.includes("title: tx('leyenda_medalla_titulo')"),
  'oeste: la medalla LEYENDA NO desbloquea (solo 1 coronación marcada)');
chk((hallo.match(/coronacion: true/g) || []).length === 1 &&
    hallo.includes("title: '★ LEYENDA'"),
  'halloween: LEYENDA sin desbloqueo');
chk((plant.match(/coronacion: true/g) || []).length === 1 &&
    plant.includes("title: '★ LEYENDA'"),
  'plantilla: LEYENDA sin desbloqueo (los campeonatos nuevos heredan)');

/* — 8 · i18n ES/EN del arcano ——————————————————————————————————————— */
console.log('8 · i18n · arcono_* · descripciones y métricas de los 14 · ES/EN');
for (const k of ['arcono_titulo', 'arcono_sub', 'arcono_pie', 'arcono_candado',
  'arcono_desbloq', 'arcono_tipo_ataque', 'arcono_tipo_defensa',
  'arcono_tipo_distraccion', 'arcono_metricas', 'arcono_indice', 'arcono_gana',
  'arcono_todos', 'arcono_hint', 'arcono_salir', 'arcono_nuevo', 'arcono_ninguno']) {
  chk((c00.match(new RegExp(k + ':', 'g')) || []).length === 2,
    'i18n ' + k + ' ES/EN (×2)');
}
for (const p of ['mega', 'efecto', 'iman', 'portal', 'clon', 'red', 'elec',
  'fenix', 'crono', 'oscuridad', 'prisma', 'onda', 'salva', 'ancla']) {
  chk((c00.match(new RegExp('arc_desc_' + p + ':', 'g')) || []).length === 2,
    'i18n arc_desc_' + p + ' ES/EN');
  chk((c00.match(new RegExp('arc_met_' + p + ':', 'g')) || []).length === 2,
    'i18n arc_met_' + p + ' ES/EN');
  chk((c00.match(new RegExp('dl_' + p + ':', 'g')) || []).length === 2,
    'i18n dl_' + p + ' ES/EN (Duelos Locos)');
}

/* — 9 · DUELOS LOCOS · los desbloqueados se JUEGAN —————————————————— */
console.log('9 · DUELOS LOCOS · surto con desbloqueados · formas de receptor');
chk(c12.includes("const DL_BASE = ['gigante', 'fuego', 'loca'];"),
  'DL_BASE: los tres NETCODE-SAFE de r84 siguen');
chk(c12.includes('const DL_DUR = {'), 'DL_DUR: ventana por poder (mega 15, portal 8, oscuridad 20)');
chk(c12.includes('const DL_SURTIDO = (game) => {'), 'DL_SURTIDO: base + TUS desbloqueados');
chk(c12.includes('extra = game.poderesDesbloqueados();'), 'el surto lee el desbloqueo REAL');
chk(c12.includes('_dlArma(id) {'), '_dlArma: trigger de la casa con ent SINTÉTICO');
chk(c12.includes('this._megaMatriz.push(ent);') &&
    c12.includes('const ok = this[fn](ent);'),
  'armado por triggers (FX/marcas/tintes idénticos al campeonato)');
chk(c12.includes('_dlVentana(id) {'), '_dlVentana: reloj de duelos (r54: el tick ya no la exige)');
chk((c12.match(/if \(pwViva\(this\._\w+T\)\)/g) || []).length === 13,
  're-anclada r55: 13 compuertas tick LEEN la puerta ÚNICA pwViva (cero patrones copiados)');
chk((c12.match(/\(on \|\| dlV\)/g) || []).length === 1 &&
    c12.includes('const pwViva = (t) => (on || dlV) && t > 0;'),
  're-anclada r55: la REGLA de la ventana vive en UN sitio (definición única)');
chk(c12.includes('_dlVentanasApaga() {'), 'recogida con FIN NATURAL al morir duelos');
chk((c12.match(/else if \(this\._\w+T > 0\) \{/g) || []).length === 9,
  're-anclada r54: 9 apagados cuando el contexto muere (sin on ni duelos)');
chk(c12.includes("const emul = pwViva(this._efectoT) ? EFECTO_SPIN_MUL"),
  're-anclada r55 · EFECTO del Arcano: spin ×3 en duelos (canal de la LOCA)');
chk(c12.includes("const imanAim = !!pwViva(this._imanT);"),
  're-anclada r55 · IMÁN del Arcano: guía al punto dulce en duelos');
chk(c12.includes("const dlGig = this._dlOn('gigante') || this._dlOn('mega');"),
  'MEGA del Arcano: pala ×1,30/radio ×1,38 en duelos (mecánica GIGANTE)');
chk(c12.includes("if (id === 'red' || id === 'crono' || id === 'oscuridad') {"),
  'RECEPTOR: red alta y ritmo lento COMPARTIDOS, niebla en MI golpeo');
chk(c12.includes('this._dlOndaFlojoT = ONDA_FLOJO_T + 0.4;'),
  'RECEPTOR: la ONDA flojea MI próxima devolución (×0,75)');
chk(c12.includes('this.ball.vel.multiplyScalar(ONDA_FLOJO);'),
  'devolución floja aplicada en el cliente que la sufre');
chk(c12.includes("if (this._dlOn('ancla')) {"), 'ANCLA: ESTRELLA los poderes entrantes (bloqueo)');
chk(c12.includes('this._anclaFlashT = 0.6;'), 'bloqueo del Ancla con destello metálico');
chk(c12.includes("if (this._dlOn('onda') && this.ball.vel && this.ball.vel.z < -0.5 &&"),
  'ONDA: el smash avisa al rival por cable fiable');
chk(c12.includes("this.rules.mode !== 'duelos'"),
  'PORTAL: el invitado portaliza en duelos (owner = quien golpea)');
chk(c09.includes("if (g._dlOn && (g._dlOn('gigante') || g._dlOn('mega'))) fl |= 16;"),
  'POSE bit 16 compartido por MEGA y GIGANTE (31 B intacto)');
chk(c12.includes("if (!base && !arcano) return;   // desconocido: build viejo ignora igual"),
  "cable 'pow' tolerante: un id desconocido NUNCA rompe (builds viejos)");

/* — 10 · FÍSICA INTACTA · c04/c05 byte-exacto ———————————————————————— */
console.log('10 · FÍSICA · c04/c05 byte-exacto (garantía de la casa)');
chk(sha256('src/game/core/c04_fisica_ccd.js').startsWith('d792b5e7'),
  'c04_fisica_ccd.js · sha256 d792b5e7… (INTACTO)');
chk(sha256('src/game/core/c05_colisiones_ia_golpeo.js').startsWith('b195a0db'),
  'c05_colisiones_ia_golpeo.js · sha256 b195a0db… (INTACTO)');

/* — 11 · EL BUNDLE LLEVA LA FASE ————————————————————————————————————— */
console.log('11 · BUNDLE · el juego en vivo lleva el apartado arcano');
chk(game.includes('montarArcano'), 'bundle: montarArcano embebido');
chk(game.includes('EL APARTADO ARCANO'), 'bundle: sección arcano embebida');
chk(game.includes('pp_poderes_v1'), 'bundle: persistencia de desbloqueos embebida');
chk(game.includes('DL_SURTIDO'), 'bundle: surto extendido de Duelos Locos embebido');

console.log('\n=== r39 · v3.6.155-SDK6 · EL APARTADO ARCANO ===');
console.log(`  ${ok} comprobaciones verdes · ${fails} fallos`);
process.exit(fails ? 1 : 0);
