/* r108 · ARNÉS — cometa de 3 capas, cristales de criptonita, clones
 *  campeones, halls seleccionables y el 16.º poder (cripto) — todo
 *  contra las FÁBRICAS REALES de c07 y los cables reales de c12/c00/c02:
 *   T1 cometa: TRES capas (chispas densas+pequeñas · rastro · HUMO
 *      azulado), chispas DETRÁS de la bola y el humo SIEMPRE azulado.
 *   T2 cristales: 1-5 por cosecha, altura final 20-50 cm REALES,
 *      colisión sólo en el volumen del cristal, rompe ≤ 0,3 s, fin
 *      disuelve todo, pool reusa sin asignar.
 *   T3 clones campeones: acierto 1.0, puestos PROPIOS (el espejo
 *      desapareció), predictor real en el frame, pose congelada.
 *   T4 halls: caso 'hallv' en el dispatcher (caída al cauce hall_var).
 *   T5 cripto: los cables del 16.º poder (registro, gatillo, tick,
 *      frame, tinta, colisión 1/3 + dirección aleatoria, cosecha 1-5,
 *      icono del dueño, firma verde, NO excluido del cometa, ventana 12).
 *   T6 fichas: arc_desc/arc_met de bolaloca (faltaban) y cripto en ES+EN.
 */
globalThis.window = globalThis;
// ctx absorbente recursivo: cualquier método devuelve otro absorbente
// (createLinearGradient().addColorStop() incluido) y toda propiedad se
// puede escribir — suficiente para las texturas procedurales de c07.
const absorb = new Proxy(function () {}, {
  get: (t, k) => (k === Symbol.toPrimitive ? () => 0 : absorb),
  apply: () => absorb,
  set: () => true,
});
const fakeCanvas = () => ({ width: 0, height: 0, getContext: () => absorb, style: {} });
globalThis.document = {
  getElementById: () => null,
  createElement: (tag) => (tag === 'canvas' ? fakeCanvas() : {}),
  addEventListener: () => {},
  visibilityState: 'visible',
};
try { globalThis.navigator = { userAgent: 'node-r108' }; } catch (e) { /* getter */ }

import * as THREE from 'three';
const c07 = await import('/home/z/my-project/src/game/core/c07_escena_sala.js');
const { createEstelaPoder, createCristalesCripto, createNubePrismas, createOndaEsfera } = c07;
const fs = await import('node:fs');
const c12 = fs.readFileSync('/home/z/my-project/src/game/core/c12_pingponggame.js', 'utf8');
const c00 = fs.readFileSync('/home/z/my-project/src/game/core/c00_pre_three.js', 'utf8');
const c02 = fs.readFileSync('/home/z/my-project/src/game/core/c02_cfg_escena.js', 'utf8');

let ok = 0, fail = 0;
function CHK(cond, msg) {
  if (cond) { ok++; console.log('  ✓ ' + msg); }
  else { fail++; console.log('  ✗ FALLO: ' + msg); }
}

/* ── T1 · COMETA DE 3 CAPAS ── */
{
  const E = createEstelaPoder();
  const rgb = [0.42, 1.0, 0.45];                 // verde cripto
  const velBola = new THREE.Vector3(0.3, 0.1, -6.0);
  const posBola = new THREE.Vector3(0.1, 1.05, 0.8);
  E.emitir(posBola, velBola, 1 / 60, rgb);
  E.emitir(posBola, velBola, 1 / 60, rgb);
  const capas = E.group.children.filter((c) => c.isPoints);
  CHK(capas.length === 3 && E.group.children.some((c) => c.visible),
    'T1 cometa con TRES capas (chispas · rastro · humo)');
  const [ch, ra, hm] = capas;
  CHK(ch.geometry.attributes.position.count === 220 && ra.geometry.attributes.position.count === 140 &&
      hm.geometry.attributes.position.count === 110,
    'T1 pools densos (chispas 220 · rastro 140 · humo 110)');
  CHK(ch.material.size <= 0.011 && hm.material.size >= 0.045,
    `T1 chispas PEQUEÑAS (${(ch.material.size * 1000).toFixed(1)} mm) y humo grande (${(hm.material.size * 100).toFixed(1)} cm)`);
  // densidad: 0,1 s de emisión a 170/s ≈ 17 chispas
  const E2 = createEstelaPoder();
  for (let i = 0; i < 6; i++) E2.emitir(posBola, velBola, 1 / 60, rgb);
  let vivas = 0;
  const pa = E2.group.children[0].geometry.attributes.position.array;
  for (let i = 0; i < 220; i++) if (pa[i * 3 + 1] > -5) vivas++;
  CHK(vivas >= 12, `T1 DENSIDAD real (${vivas} chispas en 0,1 s ≥ 12)`);
  // chispas DETRÁS (z mayor que la bola tras integrar)
  E2.update(1 / 60);
  let detras = 0, tot = 0;
  for (let i = 0; i < 220; i++) {
    if (pa[i * 3 + 1] <= -5) continue;
    tot++;
    if (pa[i * 3 + 2] > posBola.z) detras++;
  }
  CHK(tot > 0 && detras === tot, `T1 chispas DETRÁS de la bola (${detras}/${tot})`);
  // el HUMO es azulado INDEPENDIENTE del color del poder
  const ca = hm.geometry.attributes.color.array;
  const pb = hm.geometry.attributes.position.array;
  let azul = 0, nh = 0;
  for (let i = 0; i < 110; i++) {
    if (pb[i * 3 + 1] <= -5) continue;
    nh++;
    const r0 = ca[i * 3], g0 = ca[i * 3 + 1], b0 = ca[i * 3 + 2];
    if (b0 > r0 && b0 > 0.5) azul++;               // azul-dominante
  }
  CHK(nh > 0 && azul === nh, `T1 humo AZULADO siempre (${azul}/${nh} partículas azul-dominante con firma VERDE)`);
  // disipación completa
  for (let i = 0; i < 110; i++) E.update(1 / 60);
  CHK(!E.group.children.some((c) => c.visible),
    'T1 el cometa se disipa entero (1,8 s sin emisión → capas ocultas)');
}

/* ── T2 · CRISTALES DE CRIPTONITA ── */
{
  const CC = createCristalesCripto();
  const p = new THREE.Vector3(0.2, 0.76, -0.8);   // bote en la mesa rival
  const cosecha = CC.nace(p, 0.76);
  CHK(cosecha >= 1 && cosecha <= 5, `T2 cosecha ALEATORIA de ${cosecha} cristales (1-5)`);
  CHK(CC.group.children.filter((c) => c.visible).length === cosecha,
    'T2 los cristales nacen en el punto del bote');
  CC.update(1 / 60);
  // altura final REALES 20-50 cm: 4,1 unidades de geometría × escala
  const alturas = [];
  for (let i = 0; i < 30; i++) CC.update(1 / 60);   // 0,5 s → crecido
  for (const c of CC.group.children) {
    if (!c.visible) continue;
    alturas.push(4.1 * c.scale.y);
  }
  CHK(alturas.length === cosecha &&
      alturas.every((h) => h >= 0.19 && h <= 0.52),
    `T2 alturas REALES ${(alturas.map((h) => (h * 100).toFixed(0)).join('/'))} cm (20-50 cm — escala corregida)`);
  // colisión: el centro del cristal SÍ, lejos NO
  const c0 = CC.group.children.find((c) => c.visible);
  const cx = c0.position.x, cz = c0.position.z, cy = c0.position.y;
  const dentro = CC.colisiona(new THREE.Vector3(cx, cy + 0.15, cz), 0.02);
  const fuera = CC.colisiona(new THREE.Vector3(cx + 0.4, cy + 0.15, cz), 0.02);
  CHK(dentro >= 0 && fuera < 0, 'T2 colisión sólo en el VOLUMEN del cristal');
  // romper → desaparece ≤ 0,3 s
  const iR = CC.colisiona(new THREE.Vector3(cx, cy + 0.15, cz), 0.02);
  CC.rompe(iR);
  for (let i = 0; i < 20; i++) CC.update(1 / 60);
  CHK(!c0.visible, 'T2 el cristal roto desaparece ≤ 0,3 s (pedacitos por el burst del núcleo)');
  // fin de ventana: TODO se disuelve
  CC.nace(new THREE.Vector3(-0.2, 0.76, -0.9), 0.76);
  CC.fin();
  for (let i = 0; i < 20; i++) CC.update(1 / 60);
  CHK(CC.group.children.every((c) => !c.visible), 'T2 fin() disuelve la mesa entera');
  // el pool reusa sin asignar (36 naces sobre 24 instancias)
  for (let k = 0; k < 8; k++) CC.nace(p, 0.76);
  CC.update(1 / 60);
  CHK(CC.group.children.length === 24, 'T2 pool fijo de 24 (reusa, nunca asigna)');
}

/* ── T3 · CLONES CAMPEONES (cables reales de c12) ── */
{
  CHK(c12.includes('const CLON_EXITO = 1.0;'), 'T3 acierto SIEMPRE (CLON_EXITO 1.0)');
  CHK(!c12.includes('ps.pos.x + lado * CLON_DIST'),
    'T3 el ESPEJO desapareció (la guardia ya no copia la pala)');
  CHK(c12.includes('const CLON_POSTE_X = 0.62;') && c12.includes('const CLON_Z = DIMS.tableCenterZ + DIMS.tableHalfLength + 0.3;'),
    'T3 puestos PROPIOS de los asistentes (postes fijos ±62 cm)');
  CHK(c12.includes('const pr = predictStrike(b0, 1, !!r.validBounce);'),
    'T3 intercepción con el predictor REAL (predictStrike RK4)');
  CHK(c12.includes('(_pred && _pred.lado === lado ? 14 : 8)'),
    'T3 el campeón SPRINTA a la intercepción (kk 14/s)');
  CHK(c12.includes('if (this._clonPoseQ) grp.quaternion.copy(this._clonPoseQ);'),
    'T3 pose de guardia CONGELADA (jamás copia la pose viva del dueño)');
}

/* ── T4 · HALLS SELECCIONABLES ── */
{
  CHK(c12.includes("case 'hallv':"), 'T4 caso hallv presente en el dispatcher');
  const ixH = c12.indexOf("case 'hallv':");
  const ixV = c12.indexOf("case 'hall_var': {");
  CHK(ixH > 0 && ixV > ixH && ixV - ixH < 900,
    'T4 hallv CAE al cauce hall_var (los salones se seleccionan de verdad)');
}

/* ── T5 · SUPER CRIPTONITA (16.º poder) ── */
{
  CHK(c02.includes('cripto: 12,'), 'T5 ventana de 12 s (ARCANO_CFG.ventanas.cripto)');
  CHK(c12.includes("const CRIPTO_DUR = ARCANO_CFG.ventanas.cripto;"), 'T5 CRIPTO_DUR en el núcleo');
  CHK(c12.includes("if (ent.id === 'cripto') return this._criptoTrigger(ent);"), 'T5 gatillo registrado');
  CHK(c12.includes("['cripto', '_criptoT']];"), 'T5 en la regla SOLO-1-poder (poderes vivos)');
  CHK(c12.includes("{ id: 'cripto', dur: ARCANO_CFG.ventanas.cripto, nombre: () => T('poder_cripto'),"),
    'T5 entrada en PODERES_PALA (el último del registro)');
  CHK(c12.includes('png: PNG_PODER_CRIPTO },') && c12.includes("const PNG_PODER_CRIPTO = 'data:image/png;base64,"),
    'T5 icono DEL DUEÑO embebido (SuperPala_Criptonita.png cuantizado)');
  CHK(c12.includes('cripto: [0.42, 1.0, 0.45],'), 'T5 firma VERDE (estela + cometa leen la firma)');
  CHK(!c12.includes('cripto: 1, prisma') && !/R107_SIN_COMETA = \{[^}]*cripto/.test(c12),
    'T5 la cripto NO está excluida del cometa (su estela verde ES la firma)');
  CHK(c12.includes('_criptoTintAplicar()') && c12.includes('m.material.color.setHex(0x53ff6e);'),
    'T5 bola verde fosforito (tinta + emisivo, restauración exacta)');
  CHK(c12.includes('Math.sin(ph * 9.4)'), 'T5 pulso de luz verde vivo');
  CHK(c12.includes('this.cristalesCripto.nace(eC.pos, DIMS.tableTopY);'),
    'T5 cosecha al botar en la MESA DEL RIVAL (sólo side ai, sin edge)');
  CHK(c12.includes('const sp3 = Math.max(1.2, b.vel.length() / 3);'),
    'T5 freno a 1/3 de la velocidad al romper el cristal');
  CHK(c12.includes('const az = Math.random() * Math.PI * 2;') &&
      c12.includes('const el = 0.18 + Math.random() * 0.55;'),
    'T5 dirección COMPLETAMENTE ALEATORIA (azimut + elevación)');
  CHK(c12.includes("this.rules.message = T('cripto_rompe');"), 'T5 aviso «¡Cristal roto!»');
  CHK(c12.includes("if (ok.indexOf('cripto') >= 0 && lista.indexOf('cripto') < 0)"),
    'T5 nace DESBLOQUEADO (mismo trato que la Bola Loca)');
  CHK(c12.includes("cripto: ['arcono_tipo_ataque', '#6cff8a']"), 'T5 ficha: tipo ataque, verde');
}

/* ── T6 · FICHAS ES/EN (bolaloca faltaba + cripto) ── */
{
  for (const k of ['arc_desc_bolaloca:', 'arc_met_bolaloca:', 'arc_desc_cripto:',
    'arc_met_cripto:', 'poder_cripto:', 'arc_cripto_go:', 'arc_cripto_fin:',
    'cripto_rompe:']) {
    const n = c00.split(k).length - 1;
    CHK(n >= 2, `T6 ${k} presente en ES y EN (${n} dict)`);
  }
}

/* ── T7 · LAS OTRAS FÁBRICAS SIGUEN VIVAS (r107 intacto) ── */
{
  const NB = createNubePrismas();
  NB.nace(new THREE.Vector3(0, 1, 0.8), 30);
  NB.update(1 / 60);
  CHK(NB.group.visible, 'T7 nube de prismas intacta (r107)');
  const OE = createOndaEsfera();
  OE.nace(new THREE.Vector3(0, 1, 1.2));
  CHK(OE.viva(), 'T7 esfera de la onda intacta (r107)');
}

console.log(`\nCOMETA 3 CAPAS + CRISTALES + CAMPEONES + HALLS + CRIPTO r108 · ${ok} OK · ${fail} FALLOS`);
process.exit(fail ? 1 : 0);
