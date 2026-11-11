#!/usr/bin/env node
/* CRAZY PING PONG · r34 (v3.6.139, FASE 145) — TEST de la ronda.
 * Correcciones a los superpoderes de pala (informe del dueño):
 *   A · FX de mesa al this.rig (Red/Elec/Efecto/Portal) — alineación.
 *   B · voz del selector para fenix/crono/oscuridad (ES/EN).
 *   C · SÚPER ELECTRICIDAD termina tras 1 bola perdida (fin por baja).
 *   D · retención del rayo: 1 s con halo + mini-rayos (ppTransito).
 *   E · Prisma: estela arcoíris sólo en el campo del rival.
 * Uso: node scripts/test_r34_fixes_v36139.mjs */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const RAIZ = '/home/z/my-project/upload';
let ok = 0, fails = 0;
const chk = (cond, label) => {
  if (cond) { ok++; console.log('  ✓ ' + label); }
  else { fails++; console.log('  ✗ FALLO: ' + label); }
};
const cuenta = (pajaro, aguja) => pajaro.split(aguja).length - 1;

const c12 = readFileSync(`${RAIZ}/src/game/core/c12_pingponggame.js`, 'utf8');
const c00 = readFileSync(`${RAIZ}/src/game/core/c00_pre_three.js`, 'utf8');
const body = readFileSync(`${RAIZ}/src/game/03_body.html`, 'utf8');
const sw = readFileSync(`${RAIZ}/public/sw.js`, 'utf8');
const game = readFileSync(`${RAIZ}/public/game.html`, 'utf8');

console.log('== 1) FIX A · ESPACIO DE LA MESA (this.rig) ==');
chk(c12.includes('this.rig.add(cuerpo);'), 'Red: cuerpo en el rig');
chk(cuenta(c12, 'this.rig.add(ln);   // r34: espacio de la mesa') === 2,
  'Red+Elec: arcos y rayos en el rig (×2)');
chk(c12.includes('this.rig.add(riel);   // r34: espacio de la mesa'),
  'Red: riel superior en el rig');
chk(c12.includes('this.rig.add(sp);') &&
    c12.includes('      this.rig.add(sp);'), 'Elec: niebla en el rig');
chk(c12.includes('this.rig.add(mt);   // r34: espacio de la mesa'),
  'Elec: pedacitos en el rig');
chk(c12.includes('this.rig.add(this._efectoBoteFx);   // r34: espacio de la mesa'),
  'Efecto: anillo de bote en el rig');
chk(c12.includes('this.rig.add(sp);   // r34: espacio de la mesa (Sprite: billboard propio)'),
  'Portal: sprites en el rig');
chk(!c12.includes('this.scene.add(cuerpo)') && !c12.includes('this.scene.add(riel)') &&
    !c12.includes('this.scene.add(mt)') && !c12.includes('this.scene.add(ln)'),
  'sin restos de FX de mesa en scene');
chk(cuenta(c12, 'this.scene.add(') === 11,
  `scene.add sólo los 11 legítimos (re-anclada r43: el visor del rival pasa al RIG — la esfera del casco remoto comparte marco con la pala): ${cuenta(c12, 'this.scene.add(')}`);
chk(c12.includes('this.rig.add(this._netVisor);'),
  're-anclada r43: la esfera del casco remoto en el RIG (alineada con la pala)');

console.log('== 2) FIX B · VOZ DEL SELECTOR (los 3 olvidados) ==');
for (const id of ['fenix', 'crono', 'oscuridad']) {
  const may = id.toUpperCase();
  chk(c12.includes(`else if (id === '${id}') par = [VOZ_PODER_${may}, VOZ_PODER_${may}_EN];`),
    `selector habla ${id} (voz de concesión)`);
  chk(c12.includes(`'${id}',`) || c12.includes(` '${id}',`),
    `precaliente incluye ${id}`);
}
chk(c12.includes("'fenix', 'crono', 'oscuridad',"),
  'lista del precaliente re-anclada (r34)');

console.log('== 3) FIX C · FIN POR BAJA (máx. 1 bola perdida) ==');
chk(c12.includes('try { this._elecFin(true); } catch (eF34) { /* */ }'),
  '_elecRompe cierra la tormenta (fin por baja)');
chk(c12.includes('_elecFin(porBaja) {'), '_elecFin acepta porBaja');
chk(c12.includes("if (!porBaja) this.rules.message = T('arc_elec_fin');"),
  'la baja NO pisa el mensaje del punto');

console.log('== 4) FIX D · RETENCIÓN DEL RAYO (1 s halo + mini-rayos) ==');
chk(c12.includes('const ELEC_AGARRA_T = 1.0;'), 'ELEC_AGARRA_T = 1 s');
chk(c12.includes('this._elecAgarraT = 0;') &&
    c12.includes('this._elecAgarraPos = new THREE.Vector3();') &&
    c12.includes('this._elecAgarraFx = null;'), 'estado del agarre inicializado');
chk(c12.includes('if (d2 <= r * r && this._elecAgarraT <= 0) this._elecAgarra();'),
  'el impacto AGARRA (con guardia anti-reentrante)');
chk(c12.includes('_buildElecAgarraFx() {'), 'FX del agarre (halo + mini-rayos)');
chk(c12.includes('_elecAgarra() {'), '_elecAgarra existe');
chk(c12.includes('b.ppTransito = true;'), 'el agarre congela con ppTransito (portal)');
chk(c12.includes('_elecAgarraFxOff() {'), 'apagado del FX del agarre');
chk(cuenta(c12, 'this._elecAgarraFxOff();') === 2,
  'apagado llamado en _elecRompe + _elecFin (×2)');
chk(c12.includes('      if (this._elecAgarraT > 0) {\n      this._elecAgarraT -= dt;') ||
    (c12.includes('if (this._elecAgarraT > 0) {') &&
     c12.includes('this._elecAgarraT -= dt;')), 'retención viva en _elecFrame');
chk(c12.includes('this._elecAgarraT <= 0 && this.ballMesh'),
  'el tránsito del portal NO oculta la bola agarrada');
chk(!c12.includes('const vR28') && !c12.includes('this._elecRotoT = 0.9;'),
  'hide+revive r28 retirado (la bola muerta cae VISIBLE)');
chk(c12.includes("T('arc_elec_caza')"), 'mensaje arc_elec_caza al agarrar');
chk(cuenta(c00, "arc_elec_caza:") === 2, 'i18n arc_elec_caza ES+EN (c00)');
chk(c00.includes("arc_elec_caza: '¡ALCANZADA! · el rayo retiene la bola'") &&
    c00.includes("arc_elec_caza: 'CAUGHT! · the bolt holds the ball'"),
  'textos ES/EN del mensaje');

console.log('== 5) FIX E · PRISMA sólo en el campo del rival ==');
chk(c12.includes("const enCampoRival = this.ball && this.ball.pos.z < DIMS.tableCenterZ;"),
  'firma prisma condicionada a la mitad rival');
chk(c12.includes('if (!enCampoRival) return null;'),
  'en nuestro campo la estela vuelve a la skin');
chk(c12.includes('return TRAIL_PODER.prisma;'),
  'ancla r33 conservada (return TRAIL_PODER.prisma;)');
chk(c12.includes('if (!enCampoRival) return null;\n      return TRAIL_PODER.prisma;'),
  'secuencia exacta null → prisma');

console.log('== 6) VERSIÓN 3.6.143-SDK6 · FASE 145 ==');
chk(c00.includes("const VERSION = '3.6.143-SDK6';"), 'c00 VERSION 3.6.143-SDK6');
chk(body.includes('>V3.6.143-SDK6</span>'), 'badge V3.6.143-SDK6');
chk(game.includes("const VERSION = '3.6.143-SDK6';") &&
    game.includes('>V3.6.143-SDK6</span>'), 'game.html sincronizado');
chk(sw.includes("crazypp-v3.6.143-SDK6"), 'sw.js CACHE 3.6.143-SDK6');

console.log('== 7) REGRESIÓN · registro, física y anclas r33 ==');
for (const id of ['mega', 'efecto', 'iman', 'portal', 'clon', 'red', 'elec',
  'fenix', 'crono', 'oscuridad', 'prisma', 'onda', 'salva', 'ancla']) {
  chk(c12.includes(`id: '${id}', nombre: () => T('poder_${id}')`),
    `registro intacto: ${id}`);
}
const sha = (b) => createHash('sha256').update(b).digest('hex').slice(0, 8);
const c04 = readFileSync(`${RAIZ}/src/game/core/c04_fisica_ccd.js`);
const c05 = readFileSync(`${RAIZ}/src/game/core/c05_colisiones_ia_golpeo.js`);
chk(sha(c04) === 'df8f71a3', `c04 byte-exacto (${sha(c04)})`);
chk(sha(c05) === '8bb62082', `c05 byte-exacto (${sha(c05)})`);
chk(!c04.includes('elecAgarra') && !c05.includes('elecAgarra') &&
    !c04.includes('ppAgarra') && !c05.includes('ppAgarra'),
  'c04/c05 sin rastros de la retención (física intacta)');
chk((c12.match(/data:audio\/mpeg;base64,/g) || []).length >= 30,
  'voces embebidas intactas (≥30 data-URI)');
chk(c12.includes("id === 'prisma') par = [VOZ_PODER_PRISMA, VOZ_PODER_PRISMA_EN];"),
  'voz selector r33 intacta (prisma/onda/salva/ancla)');

console.log('== 8) ENSAMBLADO sincronizado ==');
const golden = readFileSync(`${RAIZ}/src/game/GOLDEN_SHA256.txt`, 'utf8')
  .split('\n').map((l) => l.trim()).filter((l) => l && !l.startsWith('#'))[0];
const real = createHash('sha256').update(game).digest('hex');
chk(golden === real, `game.html == golden (${real.slice(0, 16)}…)`);

console.log(`\nRESULTADO: ${ok} ok · ${fails} fallos`);
process.exit(fails ? 1 : 0);
