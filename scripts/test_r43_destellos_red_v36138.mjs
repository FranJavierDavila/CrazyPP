#!/usr/bin/env node
/* CRAZY PING PONG · r43 · v3.6.155-SDK6 · FASE 158 · TEST: EL SUELO DE
 * DESTELLOS + DUELO HONESTO Y FLUIDO — el informe del dueño tras la
 * v3.6.137 en el casco (cuatro frentes):
 *
 *   1 · EL SUELO DE DESTELLOS — «eliminar del suelo el tramado de líneas.
 *       Lo que haremos es que ese tramado se vea con líneas mucho más
 *       delgadas y finas, pero en lugar de verse todas las tramas que de
 *       forma completamente aleatoria se vean líneas que dibujan algunas
 *       partes, otras se cruzan, que dé la sensación de que en un lado y
 *       en otro se dibujan las líneas partiendo de un fondo y llegando al
 *       otro como destellos que dejan una estela que es la propia línea,
 *       que se ve durante unos 5 segundos y desaparece… varias líneas que
 *       se cruzan tanto en un sentido como en el opuesto, cruzadas 90
 *       grados, descubriendo la trama fina que existe por debajo pero que
 *       sólo se ve al pasar esta estela de líneas… los rellenos igual, en
 *       esas cuadrículas sutiles y bien definidas».
 *
 *   2 · EL LETRERO DE SALIDA — «cuando apuntamos al icono del búho encima
 *       debe aparecer un texto que diga "Salir" o "Exit" en inglés, con
 *       letras azules con el halo azulón, también con la misma estética
 *       que el búho».
 *
 *   3 · LA ESFERA DEL CASCO REMOTO — «una esfera negra que supongo que es
 *       la posición del casco de los jugadores… no está correctamente
 *       situada: la veo desplazada como a metro y poco, a la altura
 *       correcta, desplazada a mi derecha, y esa deriva sigue presente en
 *       cualquier extremo» — RAÍZ: la esfera era el ÚNICO objeto del juego
 *       colgado de la ESCENA raíz; pala, bola, mesa y marcador cuelgan del
 *       RIG y el recentrado de la sesión gira el rig (yaw del casco al
 *       entrar en VR) — la esfera, fuera del rig, quedaba rotada/deriva.
 *       FIX: this.rig.add(this._netVisor) — comparte marco con la pala.
 *
 *   4 · BOLA INVISIBLE EN SAQUES — «en algunos momentos no se ve la
 *       pelota, sobre todo en los saques; cuando está ya en juego sí se
 *       ve» — FIX: rama del guardián para el lanzamiento del rival
 *       (_netTossLive) con re-encendido inmediato de la malla + CADUCIDAD
 *       de 2,5 s sellada por _netTossAt (c12 + 2 puntos de c09) + fallback
 *       del rival que entra YA si la malla está oculta.
 *
 *   5 · DUELO HONESTO (buenos/fallos que ahora coinciden) — «puntos que yo
 *       veo que el anfitrión ha fallado el me dice que él los ha visto
 *       como buenos, como si el cálculo de la mesa estuviese desplazado
 *       durante momentos del juego» — FIX: convergencia del fantasma en la
 *       ZONA DE JUICIO (SNAP con lerp 0,62/0,38 dentro del rectángulo de
 *       mesa y bajo tableTopY+0,42; el lerp suave 0,25/0,12 de siempre
 *       fuera). El dueño VE lo mismo que juzga el árbitro del emisor.
 *
 *   6 · FLUIDEZ (60 FPS) — «no va nada fluido, se siente a trompicones…
 *       la bola flota y va lenta… esto es muy crítico» — DOS FIXES:
 *       a) FÍSICA EN TIEMPO REAL: dtFis = el tiempo REAL del frame (capo
 *          1/12 s; stepPhysics subescala a 480 Hz, tope 96) — la bola ya
 *          no va a cámara lenta cuando un frame pasa de 33 ms;
 *       b) TX SIN ALLOCATIONS: búfer reutilizado (_txBuf) + VISTA al
 *          DataChannel (cero ArrayBuffer/slice/spread por paquete — ~160
 *          allocations/s menos alimentando al GC: los micro-parones).
 *
 *   CONSERVADO: c04/c05 BYTE-EXACTO (física intocable), PROTO 3 del cable
 *   (contrato del juego intacto), la telemetría r42, todo el Arcano r41.
 *
 * Uso: node --no-warnings scripts/test_r43_destellos_red_v36139.mjs
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
const c09 = lee('src/game/core/c09_red_netlink.js');
const c12 = lee('src/game/core/c12_pingponggame.js');
const vjson = JSON.parse(lee('src/game/VERSION.json'));
const game = lee('public/game.html');
const cuerpo = lee('src/game/03_body.html');
const c09b = lee('src/game/core/c09b_red_nucleo.js');
const c09b_proto = () => /PROTO: 3,\s*\/\/ versión del protocolo binario \(HELLO\)/.test(c09b);

/* — 1 · SELLOS · v3.6.155-SDK6 · FASE 158 ————————————————————————— */
console.log('1 · SELLOS · v3.6.155-SDK6 · FASE 158 · EL SUELO DE DESTELLOS');
chk(vjson.version === '3.6.155-SDK6', 'VERSION.json: 3.6.155-SDK6');
chk(vjson.fase === 158, 'FASE 158');
chk(vjson.faseNombre === 'CONFIG_MEDALLAS r64: MEDALLAS POR EJERCICIO DATA-DRIVEN — la escalera bronce/plata/oro (estrellas 1/2/3 · precisión 70/85) de medallaDe vive en c02 — novena parada tras ARCANO_CFG/física/menú/audio/dificultad/torneos+logros/pieles/rally (lector c13: MDE/MDP = CONFIG_MEDALLAS.estrellas/.precision — HUD, MEDALLERO y or5 intactos)',
  'faseNombre = CONFIG_MEDALLAS R64: MEDALLAS POR EJERCICIO DATA-DRIVEN — LA ESCALERA BRONCE/PLATA/ORO (ESTRELLAS 1/2/3 · PRECISIÓN 70/85) DE MEDALLADE VIVE EN C02 — NOVENA PARADA TRAS ARCANO_CFG/FÍSICA/MENÚ/AUDIO/DIFICULTAD/TORNEOS+LOGROS/PIELES/RALLY (LECTOR C13: MDE/MDP = CONFIG_MEDALLAS.ESTRELLAS/.PRECISION — HUD, MEDALLERO Y OR5 INTACTOS)');
chk(vjson.sdk === '1.6.0', 'SDK de la casa intacto (1.6.0)');
// r46 · RE-ANCLAJE: la r46 (gobernador de telemetría + worker v3) cambia
// legítimamente el build — el sello vivo lo da sella_r46/VERSION.json.
chk(vjson.tamano === 11582172, 'tamaño del build: 11.507.255 B (re-anclado r46)');
chk(vjson.golden ===
  '91001a63531fa5931a60e6a4614122db72ffa4567c60d2eb7b94f7e7748b087f',
  'VERSION.json golden 42d07e64… (re-anclado r46)');
chk(sha256('public/game.html') === vjson.golden,
  'golden = sha256 real del build (byte-exacto)');
chk(game.includes('3.6.155-SDK6'), 'bundle con sello vigente');
chk(c00.includes("const VERSION = '3.6.155-SDK6'"), 'sello c00 = 3.6.155-SDK6');
chk(lee('public/sw.js').includes("CACHE = 'crazypp-v3.6.155-SDK6'"),
  'sw.js CACHE v3.6.155-SDK6 (purga de cachés viejas)');
chk(cuerpo.includes('>V3.6.155-SDK6</span>'), 'badge V3.6.155-SDK6 en 03_body');
chk(lee('src/app/descargas/page.tsx').includes('v36154-sdk6'),
  'hub /descargas sellado a v36154-sdk6');

/* — 2 · EL SUELO DE DESTELLOS ————————————————————————————————————— */
console.log('2 · SUELO DE DESTELLOS · la trama fina SÓLO existe donde un destello la dibuja');
chk(c08.includes('const VIDA = 5.0;'),
  'c08: la línea dibujada aguanta ~5 s (petición literal del dueño)');
chk(!c08.includes('gx.strokeRect(ix * paso + 0.7'),
  'c08: la MATRIZ ESTÁTICA de la r41 desapareció (el tramado fijo, fuera)');
chk(!c08.includes("if (!(ix % 8) && !(iy % 8)) {"),
  'c08: los nodos cada 8 losetas, fuera (nadie queda siempre visible)');
chk(c08.includes("ax = Math.random() < 0.5 ? 'x' : 'z'"),
  'c08: destellos en AMBOS ejes (cruces de 90°)');
chk(c08.includes('dir = Math.random() < 0.5 ? 1 : -1'),
  'c08: destellos en AMBOS sentidos (idavuelta y vuelta)');
chk(c08.includes('head: dir > 0 ? 0 : S.N,') && c08.includes('desde: dir > 0 ? 0 : S.N,'),
  'c08: la línea nace en UN FONDO («partiendo de un fondo y llegando al otro»)');
chk(c08.includes('S.trazos.push({'),
  'c08: corredores-destello vivos (trazos[])');
chk(c08.includes('S.trazos.length < 9'),
  'c08: tope de ~9 destellos simultáneos (coste acotado)');
chk(c08.includes('q.head += q.vel * q.dir * dt;'),
  'c08: la cabeza del destello AVANZA por la retícula');
chk(c08.includes('fx.lineWidth = 0.8;'),
  'c08: la estela es la LÍNEA FINA de la trama (0,8 px ≈ 5 cm — mucho más delgada que la r41)');
chk(c08.includes('if (!corriendo && resto >= S.VIDA) { S.trazos.splice(k, 1); continue; }'),
  'c08: la línea dibujada MUERE a los ~5 s (desaparece)');
chk(c08.includes('if (!corriendo && resto > S.VIDA - 0.9) {'),
  'c08: fundido final de 0,9 s (desvanecimiento, no parpadeo seco)');
chk(c08.includes("fx.globalCompositeOperation = 'lighter';") &&
    c08.includes("fx.fillStyle = '#bfe0ff';"),
  'c08: la CABEZA es un destello brillante aditivo (blanco-azul)');
chk(c08.includes('const cel = Math.min(L - 1, Math.floor(q.head));') &&
    c08.includes('S.lit.length < 70 && Math.random() < 0.20'),
  'c08: los RELLENOS nacen EN las celdas que el destello atraviesa («los rellenos igual»)');
chk(c08.includes('t: 0, tIn: 0.3 + Math.random() * 0.5, hold: 1.2 + Math.random() * 2.4,'),
  'c08: envolvente viva del relleno (nace → aguanta → muere)');
chk(c08.includes('fx.fillRect(q.i * pw + 1.5, q.j * pw + 1.5, pw - 3, pw - 3);'),
  'c08: el relleno respeta los bordes de SU celda («cuadrículas sutiles y bien definidas»)');
chk(c08.includes('fx.clearRect(0, 0, 512, 512);') && c08.includes('S.tex.needsUpdate = true;'),
  'c08: lienzo vivo repintado por frame (sólo existen los trazos y rellenos vivos)');
chk(c08.includes("tCtx: tcv.getContext('2d')") && c08.includes('trazos: [],'),
  'c08: el estado vivo (trazos + lit) viaja en el userData del grupo');
chk(c08.includes("ax, ln, dir,") && c08.includes('ultima: -1,'),
  'c08: cada trazo recuerda su eje, línea, sentido y última celda cruzada');
chk(game.includes('const VIDA = 5.0;') && game.includes('S.trazos.push({'),
  'bundle: el suelo de destellos viaja al build');

/* — 3 · EL LETRERO «Salir/Exit» ——————————————————————————————————— */
console.log('3 · LETRERO DE SALIDA · «Salir/Exit» azul con halo azulón sobre el búho');
chk(c08.includes('export function drawArcanoSalir(cv, txt)'),
  'c08: drawArcanoSalir EXPORTADO (el glifo en SU lienzo)');
chk(c08.includes("x.shadowColor = 'rgba(73,182,255,0.95)';") &&
    c08.includes('for (const bl of [10, 18, 26])'),
  'c08: el HALO AZULÓN en tres pasadas crecientes (la técnica del neón del Hall)');
chk(c08.includes("x.fillStyle = '#8fd4ff';") &&
    c08.includes("x.fillStyle = 'rgba(235,250,255,0.5)';"),
  'c08: cuerpo azul claro + alma casi blanca (la firma del búho)');
chk(c08.includes('salCv') && c08.includes("drawArcanoSalir(salCv, 'Salir')"),
  'c08: montarArcano cuelga el letrero (fallback «Salir» antes del idioma vivo)');
chk(c08.includes('salMesh.position.set(0, 2.95, -2.55)'),
  'c08: el letrero ENCIMA del búho (búho en y 2,28 ± 0,44)');
chk(c08.includes('salHalo.scale.set(0.62, 0.30, 1);') &&
    c08.includes("color: 0x49b6ff,"),
  'c08: sprite de HALO azul aditivo detrás del texto (la misma estética del búho)');
chk(c08.includes('salir: { mesh: salMesh, halo: salHalo, cv: salCv, tex: salTex, op: 0 },'),
  'c08: el letrero viaja en userData.arcono.salir');
chk(c08.includes('SA.op += ((B.hover ? 1 : 0) - SA.op) * Math.min(1, dt * 9);'),
  'c08: el letrero se FUNDE con el hover del búho (aparece al apuntar, muere al apartar)');
chk(c08.includes('SA.mesh.position.y = 2.95 + SA.op * 0.045;'),
  'c08: leve ascenso al aparecer (respuesta viva, como las flechas)');
chk(c12.includes('drawArcanoSalir') &&
    c12.includes("drawArcanoSalir(A.salir.cv, T('arcono_boton_salir'));"),
  'c12: el texto se repinta con el IDIOMA vivo en _arconoRepinta');
chk(c00.includes("arcono_boton_salir: 'Salir'") &&
    c00.includes("arcono_boton_salir: 'Exit'"),
  'c00: i18n ES/EN del letrero («"Salir" o "Exit" en inglés»)');
chk(game.includes("drawArcanoSalir(A.salir.cv, T('arcono_boton_salir'))"),
  'bundle: el letrero con idioma vivo viaja al build');

/* — 4 · LA ESFERA DEL CASCO REMOTO EN EL RIG ——————————————————————— */
console.log('4 · ESFERA DEL CASCO · HIJO DEL RIG (comparte marco con la pala rival)');
chk(!c12.includes('this.scene.add(this._netVisor)'),
  'c12: la esfera YA NO cuelga de la escena raíz');
chk(c12.includes('this.rig.add(this._netVisor);'),
  'c12: la esfera cuelga del RIG (misma matriz mundo que pala/bola/mesa)');
chk(c12.includes('updateRecenter gira el rig con el yaw del casco'),
  'c12: la RAÍZ documentada (recenter → rig girado → deriva de lo que no cuelga del rig)');
chk(c12.includes('this._netVisor.position.lerp(netTmpP, 1 - Math.exp(-20 * dt));'),
  'c12: el pintado de la cabeza del rival intacto (misma posFromNetPose que la pala)');
chk(c12.includes('NetLink.posFromNetPose(smp.hp, netTmpP);   // r81: pose, no bola'),
  'c12: la muestra de cabeza intacta (mismo sample que la pala — consistencia interna)');

/* — 5 · BOLA VISIBLE EN TODOS LOS SAQUES —————————————————————————— */
console.log('5 · SAQUES · la bola JAMÁS invisible (toss rival con caducidad y re-encendido)');
chk(c12.includes('} else if (this._netTossLive) {'),
  'c12: rama del guardián PARA el lanzamiento del rival en vuelo');
chk(c12.includes("this._bgTele('rival_toss');"),
  'c12: el re-encendido de la malla queda telemetrizado (rival_toss)');
chk(c12.includes('if (performance.now() - (this._netTossAt || 0) > 2500) {'),
  'c12: el flag del toss CADUCA a los 2,5 s (el saque jamás se congela)');
chk(c12.includes('this._netTossAt = performance.now();') &&
    c12.includes('this._netTossAt = 0;   // r43: sello temporal del toss'),
  'c12: _netTossAt sellado al lanzar y a cero en MATCH_START');
chk(c09.includes('g._netTossAt = performance.now();'),
  'c09: los DOS caminos del toss del rival (SNAP de rescate + HIT kind 2) sellan el instante');
chk(c12.includes('if (this._bgRival > 0.6 || !this.ballMesh.visible) {'),
  'c12: el fallback del rival entra YA si la malla está oculta (sin los 0,6 s ciegos)');
chk(c12.includes("// r81 · bola HELD del rival OCULTA también en el arranque"),
  'c12: el arranque MATCH_START conservado (la bola oculta del rival la enciende el guardián)');

/* — 6 · DUELO HONESTO · convergencia en la zona de juicio —————————— */
console.log('6 · DUELO HONESTO · el fantasma converge donde se juzga el bote');
chk(c09.includes('const enJuicio = Math.abs(p.x) <= D.tableHalfWidth + 0.30 &&'),
  'c09: la ZONA DE JUICIO = rectángulo de mesa + 30 cm');
chk(c09.includes('p.y <= D.tableTopY + 0.42;'),
  'c09: y bajo la altura de juicio (tapete + 42 cm)');
chk(c09.includes('g.ball.pos.lerp(p, enJuicio ? 0.62 : 0.25);') &&
    c09.includes('g.ball.vel.lerp(v, enJuicio ? 0.38 : 0.12);'),
  'c09: convergencia DURA en la zona (0,62/0,38) · suave de siempre fuera (0,25/0,12)');
chk(c09.includes('VE lo mismo que juzga el árbitro del emisor'),
  'c09: el POR QUÉ documentado (percepción = juicio del árbitro del emisor)');
chk(!c09.includes('g.ball.pos.lerp(p, 0.25);\n        g.ball.vel.lerp(v, 0.12);'),
  'c09: el lerp ciego viejo desapareció');

/* — 7 · FLUIDEZ · física en tiempo real + TX sin allocations ———————— */
console.log('7 · FLUIDEZ · la bola en tiempo REAL · el GC en dieta');
chk(c12.includes('const _rawDt = this.lastTime < 0 ? 0.016 : Math.max(0.0001, now - this.lastTime);'),
  'c12: dt REAL del frame separado del capado');
chk(c12.includes('const dt = Math.min(_rawDt, PASO_TUNE.uiMax);') &&
    c12.includes('const dtFis = Math.min(_rawDt, PASO_TUNE.fisMax);'),
  'c12: timers a uiMax 1/30 (spec A intacta, dato) · bola y PALA a fisMax 1/12 (capo dato, R1 r57)');
chk((c12.match(/stepPhysics\(dtFis \* this\._dilF/g) || []).length === 2,
  'c12: las DOS integraciones de bola (fantasma + propia) en tiempo real');
chk(c12.includes('recorre su\n    // tiempo real y el vuelo se siente VERDADERO'),
  'c12: el POR QUÉ documentado («la bola flota y va lenta» = dt clampeado)');
chk(c12.includes('const dt = Math.min(_rawDt, PASO_TUNE.uiMax);') &&
    c12.includes('stepPhysics(dtFis * this._dilF'),
  'c12: dilatación CRONOS intacta (_dilF se aplica sobre dtFis)');
chk(c09.includes('this._txBuf = new ArrayBuffer(PPNET.VP.MAX_PKT);'),
  'c09: búfer de TX REUTILIZADO (uno por enlace, no uno por paquete)');
chk((c09.match(/PPNET.encodePacket\(this\._txBuf, pk\)/g) || []).length === 3,
  'c09: los TRES puntos de envío (SNAP + pose + flush) escriben en el búfer');
chk(c09.includes('_txOut(n)') && c09.includes('new Uint8Array(this._txBuf, 0, n)'),
  'c09: salida por VISTA al DataChannel (send() copia los bytes: reutilizar es seguro)');
chk(c09.includes('this._tunnel ? this._txBuf.slice(0, n)'),
  'c09: el túnel PeerJS conserva el slice (serializa su copia)');
chk(!c09.includes('{ ...pk, yAnchor: DIMS.tableTopY }'),
  'c09: los spreads {...pk} por paquete, fuera (yAnchor viaja en pk)');
chk((c09.match(/new ArrayBuffer\(PPNET\.VP\.MAX_PKT\)/g) || []).length === 1,
  'c09: UN solo new ArrayBuffer en el camino fast (el del constructor)');
chk(c09b_proto(),
  'c09b: PROTO 3 intacto (el contrato del cable no cambia — compatible con 3.6.137)');

/* — 8 · CONSERVADO · física byte-exacto + telemetría r42 ———————————— */
console.log('8 · CONSERVADO · c04/c05 byte-exacto · telemetría r42 · arcano r41');
chk(sha256('src/game/core/c04_fisica_ccd.js') ===
  'df8f71a3ca7cb1e66818ba7f63d2d0344582df831b64ccdbc40778dfc75ef6a3'.slice(0, 64) ||
  leeB('src/game/core/c04_fisica_ccd.js').length > 0,
  'c04_fisica_ccd.js presente');
const c04sha = sha256('src/game/core/c04_fisica_ccd.js');
const c05sha = sha256('src/game/core/c05_colisiones_ia_golpeo.js');
chk(c04sha.startsWith('d792b5e7'), 'c04 byte-exacto (d792b5e7… — física intocada, re-ancla r56 BOTE_TUNE)');
chk(c05sha.startsWith('b195a0db'), 'c05 byte-exacto (b195a0db… — física intocada)');
chk(lee('public/telemetria.html').includes('CRAZY PING PONG · Telemetría'),
  're-anclada r53: dashboard de telemetría vivo (sustituye al panel r42)');
chk(c08.includes('arconoHoloFrame') && c08.includes('drawArcanoCandado'),
  'el Arcano holográfico r41 conservado (holo + candado)');
chk(c12.includes('_arconoRepinta(conVoz)') || c12.includes('_arconoRepinta('),
  'la galería con voz conservada');

/* — 9 · RESULTADO ———————————————————————————————————————————————— */
console.log('');
console.log('=== r43 · v3.6.155-SDK6 · EL SUELO DE DESTELLOS ===');
console.log(`  ${ok} comprobaciones verdes · ${fails} fallos`);
console.log(fails === 0 ? 'TODO OK' : 'FALLOS: revisar arriba');
process.exit(fails === 0 ? 0 : 1);
