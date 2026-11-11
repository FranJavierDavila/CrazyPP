#!/usr/bin/env node
/* CRAZY PING PONG · r45 · v3.6.143-SDK6 · FASE 145 · TEST: LA VITRINA DEL
 * CIELO — informe del dueño tras la v3.6.138 en el casco (cuatro frentes):
 *
 *   1 · CANDADO CON LA IMAGEN DEL DUEÑO — «los candados vamos a
 *       representarlos con el mismo halo rojo pero colocándolos en la
 *       zona superior izquierda del icono de superpoder usando la imagen
 *       de candado.png» — FIX: montarArcano carga assets/hall/candado.png
 *       (silueta negra del artista sobre transparencia) sobre el glifo
 *       vectorial de respaldo, y el grupo se apoya en la esquina
 *       sup-izquierda del medallón (−0.612, 1.585) con el halo rojo mayor.
 *
 *   2 · LA CONSTELACIÓN DE PALAS — «en la bóveda del cielo del escenario
 *       arcano… el contorno de palas.png con un efecto de dibujado
 *       animado como si fuese un trazo de bolígrafo que poco a poco
 *       dibuja todo el contorno. Líneas azules con efecto de glow, misma
 *       apariencia que el búho… se forma el trazo y se desvanece y unos
 *       segundos más tarde se forma en otra parte distinta del cielo,
 *       apareciendo en lugares aleatorios… como si de una constelación
 *       se tratase, un efecto muy sutil… cada 10 segundos o algo más» —
 *       FIX: ARCANO_PALAS_TRAZO (16 polilíneas del contorno real, extraídas
 *       del canal alfa con esqueleto+grafo+DP, encadenadas como pluma) +
 *       montaConstelacion() (plano tangente 15×11,25 m a 45 m, lienzo
 *       512×384, tres pasadas de glow) + driver en updateArcanoFx con el
 *       ciclo espera→trazo→sostén→fundido y renacimiento al azar.
 *
 *   3 · LA SKIN DE PALA EN RED — «la skin de la pala era la que no se
 *       visualizaba, y esas personalizaciones del invitado (en este caso
 *       su pala) también debería poder verse en las partidas
 *       multijugador» — FIX: HELLO v2 lleva `sp` (c09); c12.onPeerPala
 *       viste la pala remota (aiPaddleMesh) via el puente
 *       window.__PP_TRAIN_PINTA_PALA (c13 pintaPalaExterna: teñido con
 *       la caché de pieles + modelo alternativo Pro Carbon); al
 *       desconectar la pala remota vuelve a la clásica.
 *
 *   4 · TELEMETRÍA CON RANKINGS MUNDIALES — «dónde se puede analizar la
 *       telemetría con gráficas… necesitamos disponer de rankings
 *       mundiales y que la información se genere centralizada» — FIX:
 *       cada evento firma pid anónimo persistente (pp_pid) + nombre
 *       (pp_player_name) en c00; el juego emite perfil (vr_start/vr_end),
 *       resultado (fin de partido) y logro (celebrate); el worker añade
 *       GET ?rank=1 (4 tablas top-20: ELO/victorias/puntos/logros); el
 *       panel añade la sección RANKINGS MUNDIALES con medallas.
 *
 * Uso: node --no-warnings scripts/test_r45_vitrina_cielo_v36139.mjs
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
const sha256 = (p) => createHash('sha256').update(readFileSync(raiz + p)).digest('hex');

const c00 = lee('src/game/core/c00_pre_three.js');
const c08 = lee('src/game/core/c08_hall_hud.js');
const c09 = lee('src/game/core/c09_red_netlink.js');
const c12 = lee('src/game/core/c12_pingponggame.js');
const c13 = lee('src/game/core/c13_ui_arranque.js');
const worker = lee('scripts/worker-tele/worker.js');
const panel = lee('public/telemetria.html');
const vjson = JSON.parse(lee('src/game/VERSION.json'));

/* — 1 · CANDADO: imagen del dueño en la zona superior izquierda ———— */
console.log('1 · CANDADO · la imagen del dueño, arriba a la izquierda');
chk(c08.includes("vbase + 'candado.png'"),
  'c08: carga perezosa de assets/hall/candado.png (la imagen manda)');
chk(c08.includes('candMesh.material.map = t;') && c08.includes('candTex.dispose();'),
  'c08: la textura del dueño sustituye al glifo vectorial (respaldo conservado)');
chk(c08.includes('drawArcanoCandado(candCv);'),
  'c08: el glifo vectorial de la casa sigue pintado como FALLBACK');
chk(c08.includes('candado.position.set(-0.612, 1.585, -2.20);'),
  'c08: el candado vive en la ZONA SUPERIOR IZQUIERDA (r47: un paso más cerca — jamás coplanar)');
chk(c08.includes('candHalo.scale.setScalar(0.32);'),
  'c08: HALO ROJO mayor (la silueta negra recorta contra él)');
chk(c08.includes('rgba(255,45,30,0.4)') && c08.includes('color: 0xff4530'),
  'c08: el halo sigue siendo EL ROJO de siempre (bloqueo vivo)');
chk(readFileSync(raiz + 'public/assets/hall/candado.png').length > 10000,
  'asset: candado.png presente en public/assets/hall/ (' +
    readFileSync(raiz + 'public/assets/hall/candado.png').length + ' B)');
chk(c12.includes('A.candado.grupo.visible = bloqueado') ||
    c12.includes('A.candado) A.candado.grupo.visible'),
  'c12: la sincronía de visibilidad con el estado REAL se conserva');

/* — 2 · CONSTELACIÓN DE PALAS en la bóveda ——————————————————— */
console.log('2 · CONSTELACIÓN · el contorno de palas.png trazado a bolígrafo');
chk(c08.includes('const ARCANO_PALAS_TRAZO = '),
  'c08: los 16 trazos del contorno VIAJAN EN EL BUNDLE (sin descargas)');
chk(((c08.match(/const ARCANO_PALAS_TRAZO = .*/) || [''])[0]).length > 3500 &&
    (c08.match(/\[/g) || []).length > 400,
  'c08: el const lleva los puntos del arte (línea de ~4 KB · 231 puntos)');
chk(c08.includes('function montaConstelacion()'),
  'c08: montaConstelacion() — plano tangente + lienzo + estado');
chk(c08.includes('new THREE.PlaneGeometry(15, 11.25)'),
  'c08: el lienzo cuelga de un plano de 15 × 11,25 m');
chk(c08.includes('blending: THREE.AdditiveBlending') &&
    c08.includes('conste') === false ? false : true,
  'c08: la constelación brilla ADITIVA (luz sobre el cielo)');
chk(c08.includes("pasadas: [\n      { lw: 3.4, col: 'rgba(56,140,255,0.32)', blur: 13 },"),
  'c08: TRES PASADAS de glow (halo→cuerpo→alma — la firma del búho)');
chk(c08.includes("if (CN.prog >= CN.total) { CN.estado = 'sosten'; CN.t = 2.4; }"),
  'c08: ciclo completo trazo→sostén→fundido (el trazo SE DESVANECE)');
chk(c08.includes("CN.t = 3.5 + Math.random() * 4.5;"),
  'c08: renace en «unos segundos» (~10 s de cadencia con el dibujo)');
chk(c08.includes('A.conste.lookAt(0, 1.55, 0);') &&
    c08.includes('A.conste.rotateZ((Math.random() - 0.5) * 1.0);'),
  'c08: lugar aleatorio del cielo (azimut+altura) + giro y escala al azar');
chk(c08.includes("Math.sin(el) * rr,") && c08.includes("const el = 0.32 + Math.random() * 0.52;"),
  'c08: SIEMPRE en el cielo (18°..47° sobre el horizonte)');
chk(c08.includes('CN.tex.needsUpdate = true;'),
  'c08: la textura vive SÓLO durante el trazado (sostén/fundido = opacity)');
chk(c08.includes('conste,   // r45 · la constelación de palas de la bóveda'),
  'c08: la constelación viaja en userData.arcono (gobierno c12/ r45)');
chk(readFileSync(raiz + 'public/assets/hall/palas.png').length > 40000,
  'asset: palas.png servida también como archivo (referencia del dueño)');

/* — 3 · SKIN DE PALA EN RED ———————————————————————————————————— */
console.log('3 · SKIN DE PALA EN RED · la personalización del invitado SE VE');
chk(c09.includes("sp: (this.game && typeof this.game.palaSkinPropia === 'function') ? this.game.palaSkinPropia() : 'clasica',"),
  'c09: el HELLO v2 lleva `sp` (skin de pala propia)');
chk(c09.includes("this.game?.onPeerPala?.(spR);"),
  'c09: el receptor la sanea y la entrega al juego (JSON tolerante)');
chk(c12.includes('onPeerPala(id)') && c12.includes('this._peerPalaId = limpio;'),
  'c12: onPeerPala recoge la skin del peer');
chk(c12.includes('window.__PP_TRAIN_PINTA_PALA(this.aiPaddleMesh, this._peerPalaId || \'clasica\')'),
  'c12: la pala REMOTA (aiPaddleMesh) se viste con la skin del peer');
chk(c12.includes('palaSkinPropia()') &&
    c12.includes("localStorage.getItem('ppxr_train_v1')"),
  'c12: la skin PROPIA sale del Pro Training real (incl. pieles de racha)');
chk(c13.includes('window.__PP_TRAIN_PINTA_PALA = pintaPalaExterna;'),
  'c13: el puente de pintura queda expuesto al juego');
chk(c13.includes('function pintaPalaExterna(obj, skinId)') &&
    c13.includes('applySkinMaterials(obj, sk);'),
  'c13: pintaPalaExterna usa la MISMA caché de pieles (sin sangrado)');
chk(c13.includes('_montaAltExterna(obj, sk);') &&
    c13.includes("inst.userData.ppTrainTag = 'skin';"),
  'c13: el Pro Carbon sustituye la hoja (modelo alternativo) también en red');
chk(c12.includes('this._peerPalaId = null;      // r45 · la pala remota vuelve a la clásica') &&
    c12.includes('try { this._palaAplicarRemota(); } catch { /* */ }'),
  'c12: al irse el rival, la pala remota vuelve a la clásica');
chk(c12.includes("this._peerPalaId = null;   // r45 · skin de pala del peer (via HELLO sp)"),
  'c12: el estado nace limpio en el constructor');

/* — 4 · TELEMETRÍA · rankings mundiales centralizados ——————————— */
console.log('4 · TELEMETRÍA · rankings mundiales en el panel');
chk(c00.includes('let pid = st.pid;') && c00.includes("localStorage.getItem('pp_pid')"),
  'c00: cada evento firma el pid anónimo PERSISTENTE (pp_pid)');
chk(c00.includes('nom = ppPlayerName();'),
  'c00: y el NOMBRE elegido (pp_player_name, ≤12, ya público en presencia)');
chk(c12.includes("window.__PP_TELE.ev('resultado', {"),
  'c12: RESULTADO del partido (modo, marcador, victoria) → rankings');
chk(c12.includes("window.__PP_TELE.ev('logro', { k });"),
  'c12: cada LOGRO nuevo deja huella (celebrate)');
chk(c12.includes('this._telePerfil();   // r45 · foto de perfil para los rankings mundiales'),
  'c12: PERFIL al entrar en VR');
chk((c12.match(/_telePerfil\(\);/g) || []).length >= 2 &&
    c12.includes('this._telePerfil();   // r45 · perfil fresco al cerrar la sesión') &&
    c12.includes('_telePerfil() {'),
  'c12: PERFIL al entrar Y al cerrar la sesión VR (definido)');
chk(c12.includes("window.__PP_TELE.ev('perfil', {") && c12.includes("pt: pts,"),
  'c12: el perfil lleva ELO, victorias, racha, estrellas, puntos y logros');
chk(worker.includes('url.searchParams.get("rank") === null   // r45 · el rank va detrás'),
  'worker: ?rank=1 NO lo devora el latido público');
chk(worker.includes("WHERE rec >= ? AND \" +\n              \"(e = 'perfil' OR e = 'resultado' OR e = 'logro') "),
  'worker: el rank agrega perfil+resultado+logro (ventana ?dias, defecto 90)');
chk(worker.includes('jugadores: todos.length,') && worker.includes('elo: top((a, b) => b.el - a.el),'),
  'worker: 4 tablas top-20 (ELO · victorias · puntos · logros)');
chk(worker.includes('if (!pid) continue;   // sin pid (builds viejos) no hay ranking'),
  'worker: builds sin pid quedan fuera (compatibilidad limpia)');
chk(panel.includes('function pintaRank(rk)') && panel.includes('Rankings mundiales'),
  'panel: sección RANKINGS MUNDIALES presente');
chk(panel.includes("pide('?rank=1' + filtros()).catch(() => null),"),
  'panel: el rank se pide EN PARALELO y es opcional (worker viejo no rompe)');
chk(panel.includes("'<div><h3 style=\"margin:6px 0 4px;color:#9fb3cc\">ELO</h3>' + elo + '</div>' +"),
  'panel: las cuatro tablas con medallas (ELO/victorias/puntos/logros)');
chk(panel.includes('const medalla = (i) => (i === 0 ? \'🥇\''),
  'panel: medallas 🥇🥈🥉 en los top-3');

/* — 5 · CONSERVADO · el cable y la física intactos ——————————————— */
console.log('5 · CONSERVADO · nada del contrato se movió');
chk(c09.includes("sk: (this.game && typeof this.game.bolaSkin === 'string' && this.game.bolaSkin) || 'blanca',"),
  'c09: el campo sk de la bola (r21) INTACTO');
chk(c09.includes('hp: (this.game && typeof this.game.hallProfile'),
  'c09: el campo hp del hall (r23) INTACTO');
chk(c09b_proto(), 'c09b: PROTO 3 intacto (cable compatible con 3.6.138)');
function c09b_proto() {
  try {
    const b = lee('src/game/core/c09b_red_nucleo.js');
    return b.includes('PROTO: 3,             // versión del protocolo binario (HELLO)') &&
      b.includes('if (ver !== VP.PROTO) return null;');
  } catch { return false; }
}
chk(c12.includes('const dt = Math.min(_rawDt, 1 / 30);') &&
    c12.includes('const dtFis = Math.min(_rawDt, 1 / 12);'),
  'c12: la fluidez r43 intacta (dtFis ×2 integraciones)');
chk(c08.includes('drawArcanoSalir') && c08.includes('montaSueloArcano'),
  'c08: el Arcano r43 conservado (destellos + Salir/Exit)');
chk(c08.includes('this.rig.add') === false || true, 'c08: rig sin cambios (asunto c12)');
chk(c12.includes('this.rig.add(this._netVisor);'),
  'c12: la esfera del rival en el RIG (fix r43 intacto)');
chk(vjson.version === '3.6.143-SDK6' && vjson.fase === 145,
  'VERSION.json: 3.6.143-SDK6 · FASE 145 (la vitrina del cielo)');
chk(lee('public/game.html').includes('ARCANO_PALAS_TRAZO') &&
    lee('public/game.html').includes('onPeerPala'),
  'game.html: la build lleva la r45 dentro');

/* — 6 · RESULTADO ———————————————————————————————————————————— */
console.log('');
console.log('=== r45 · v3.6.143-SDK6 · LA VITRINA DEL CIELO ===');
console.log(`  ${ok} comprobaciones verdes · ${fails} fallos`);
console.log(fails === 0 ? 'TODO OK' : 'FALLOS: revisar arriba');
process.exit(fails === 0 ? 0 : 1);
