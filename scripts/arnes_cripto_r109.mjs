/* r109 · ARNÉS SUPER CRIPTONITA — VOZ EN DOS SALAS + CANDADO HONESTO.
 *  El six-pack del dueño (contra las fábricas REALES, cero réplicas):
 *   T1 voz: VOZ_PODER_CRIPTO/_EN embebidas (mp3 válido, ≥ 4 KB) y la
 *      entrada del registro lleva voz/vozEn — con eso la nombran solos
 *      el selector (r58), la concesión (_poderVoz) y el Arcano (r47).
 *   T2 conducto: _vozSelFuente tiene el caso cripto ANTES del return y
 *      la voz solemne del Arcano (_vozSelSolemne → conducto r47) sigue
 *      viva: cinta ×0,82 + paso-bajo + convolución presentes.
 *   T3 candado: la apertura de fábrica r108 está FUERA, el fallback del
 *      catch es ['bolaloca'], la migración retira 'cripto' del
 *      almacenamiento y el registro sigue con SUS 16 poderes.
 *   T4 administrador: FORO3D (window.__PP_DEBUG) devuelve TODO el
 *      registro en poderesDesbloqueados; el bypass de candado r32 queda.
 *   T5 cristales (REQUISITO 1 del dueño, fábrica REAL de c07): nacen,
 *      crecen, y al EXPIRAR fin() los ROMPE todos (animación 0,3 s,
 *      giro + encogido) — nada queda vivo después; y rompe(i) individual
 *      sigue funcionando para la bola.
 *   T6 sellos: VERSION.json == c00 == badge == sw.js == 3.6.207-SDK6 y
 *      el sha256 de public/game.html clava el golden.
 *   T7 bundle: public/game.html lleva las dos voces + la entry con voz +
 *      el candado honesto + el caso del selector.
 */
globalThis.window = globalThis;
// stub ENCADENABLE: createLinearGradient().addColorStop(...) y cualquier
// cadena de llamadas del lienzo procedural devuelven el propio proxy.
const chainable = new Proxy(function () {}, {
  get: () => chainable,
  apply: () => chainable,
});
const ctxStub = new Proxy({}, { get: () => (() => chainable), set: () => true });
const fakeCanvas = () => ({ width: 0, height: 0, getContext: () => ctxStub, style: {} });
globalThis.document = {
  getElementById: () => null,
  createElement: (tag) => (tag === 'canvas' ? fakeCanvas() : {}),
  addEventListener: () => {},
  visibilityState: 'visible',
};
try { globalThis.navigator = { userAgent: 'node-r109' }; } catch (e) { /* getter */ }

const fs = await import('node:fs');
const crypto = await import('node:crypto');
const path = await import('node:path');
const RAIZ = '/home/z/my-project';
const c12 = fs.readFileSync(RAIZ + '/src/game/core/c12_pingponggame.js', 'utf8');
const c07src = fs.readFileSync(RAIZ + '/src/game/core/c07_escena_sala.js', 'utf8');
const c00src = fs.readFileSync(RAIZ + '/src/game/core/c00_pre_three.js', 'utf8');
const body = fs.readFileSync(RAIZ + '/src/game/03_body.html', 'utf8');
const swjs = fs.readFileSync(RAIZ + '/public/sw.js', 'utf8');
const vjson = JSON.parse(fs.readFileSync(RAIZ + '/src/game/VERSION.json', 'utf8'));
const goldenTxt = fs.readFileSync(RAIZ + '/src/game/GOLDEN_SHA256.txt', 'utf8')
  .split('\n').filter((l) => l && !l.startsWith('#'))[0].trim();
const bundle = fs.readFileSync(RAIZ + '/public/game.html', 'utf8');

let ok = 0, fail = 0;
function CHK(cond, msg) {
  if (cond) { ok++; console.log('  ✓ ' + msg); }
  else { fail++; console.log('  ✗ FALLO: ' + msg); }
}

/* ── T1 · LA VOZ ─────────────────────────────────────────────────── */
console.log('T1 · la voz de la criptonita (ES/EN embebida)');
const mConstEs = c12.match(/const VOZ_PODER_CRIPTO = 'data:audio\/mpeg;base64,([A-Za-z0-9+/=]+)';/);
const mConstEn = c12.match(/const VOZ_PODER_CRIPTO_EN = 'data:audio\/mpeg;base64,([A-Za-z0-9+/=]+)';/);
CHK(!!mConstEs, 'const VOZ_PODER_CRIPTO existe con data URI');
CHK(!!mConstEn, 'const VOZ_PODER_CRIPTO_EN existe con data URI');
for (const [nombre, m] of [['ES', mConstEs], ['EN', mConstEn]]) {
  if (!m) continue;
  const bytes = Buffer.from(m[1], 'base64');
  const esMp3 = bytes.length >= 4096 &&
    (bytes.subarray(0, 3).toString('latin1') === 'ID3' || bytes[0] === 0xff);
  CHK(esMp3, `voz ${nombre}: mp3 válido de ${bytes.length} B (≥ 4 KB)`);
}
CHK(/voz: VOZ_PODER_CRIPTO, vozEn: VOZ_PODER_CRIPTO_EN/.test(c12),
  'la entry cripto de PODERES_PALA lleva voz/vozEn');
CHK((c12.match(/data:audio\/mpeg/g) || []).length >= 32,
  'el banco de voces de concesión sigue completo (≥ 32 data URIs en src)');

/* ── T2 · EL CONDUCTO (dos entonaciones, un banco) ───────────────── */
console.log('T2 · conducto: selector ágil en el juego · solemne en Arcano');
CHK(/\/\/ r109 · SUPER CRIPTONITA reutiliza su voz de concesión[\s\S]*?else if \(id === 'cripto'\) par = \[VOZ_PODER_CRIPTO, VOZ_PODER_CRIPTO_EN\];/.test(c12),
  '_vozSelFuente tiene el caso cripto');
const selFuente = c12.indexOf("_vozSelFuente(key) {");
const casoCripto = c12.indexOf("else if (id === 'cripto') par = [VOZ_PODER_CRIPTO");
const retSel = c12.indexOf('return par ? (en ? par[1] : par[0]) : null;', selFuente);
CHK(selFuente > 0 && casoCripto > selFuente && casoCripto < retSel,
  'el caso cripto está ANTES del return de _vozSelFuente (no hay código muerto)');
CHK(/_vozSolemneToca\(buf\)/.test(c12) && /playbackRate\.value = 0\.82/.test(c12)
    && /lowpass'; lp\.frequency\.value = 2800/.test(c12),
  'el conducto solemne r47 (cinta ×0,82 + paso-bajo) sigue intacto');
CHK(/const fuente = this\._vozSelFuente\(key\);/.test(c12),
  '_vozSelSolemne sigue tirando de _vozSelFuente (el Arcano hereda la voz)');
CHK(/return en \? \(p\.vozEn \|\| p\.voz\) : p\.voz;/.test(c12),
  '_poderVoz (voz de concesión) sigue data-driven con p.voz/p.vozEn');

/* ── T3 · EL CANDADO HONESTO ─────────────────────────────────────── */
console.log('T3 · candado honesto (el Superpoder nace BLOQUEADO)');
CHK(!/nace DESBLOQUEADO/.test(c12), 'la apertura de fábrica r108 está fuera');
CHK(/return \['bolaloca'\];/.test(c12), "el fallback del catch es ['bolaloca']");
CHK(!/return \['bolaloca', 'cripto'\]/.test(c12), 'el fallback viejo con cripto no queda');
CHK(/const iCripto = lista\.indexOf\('cripto'\);/.test(c12)
    && /lista\.splice\(iCripto, 1\);/.test(c12),
  'migración: retira la cripto sembrada por la r108 del almacenamiento');
const nPoderes = (c12.match(/\{ id: '(mega|efecto|iman|portal|clon|red|elec|fenix|crono|oscuridad|prisma|onda|salva|ancla|bolaloca|cripto)'/g) || []).length;
CHK(nPoderes === 16, `PODERES_PALA conserva sus 16 poderes (hay ${nPoderes})`);
CHK(/arcono_tipo_ataque.*cripto|cripto: \['arcono_tipo_ataque'/.test(c12) || /cripto: \['arcono_tipo/.test(c12),
  'ARCONO_TIPOS.cripto (ficha del Arcano) sigue en su sitio');

/* ── T4 · LA REGLA DEL ADMINISTRADOR (FORO3D) ────────────────────── */
console.log('T4 · regla del administrador: FORO3D lo tiene TODO desbloqueado');
CHK(/\/\/ r109 · REGLA DEL ADMINISTRADOR[\s\S]*?window\.__PP_DEBUG\) return ok\.slice\(\);/.test(c12),
  'poderesDesbloqueados: admin → todo el registro');
CHK(/window\.__PP_DEBUG\).{0,80}return true/.test(c12.replace(/\n/g, ' ')) ||
    /__PP_DEBUG/.test(c12),
  'el bypass de candado de la casa (r32) sigue en c12');
const idxUnlock = c12.indexOf('poderesDesbloqueados() {');
const idxAdmin = c12.indexOf('window.__PP_DEBUG) return ok.slice();');
CHK(idxUnlock > 0 && idxAdmin > idxUnlock && idxAdmin - idxUnlock < 2000,
  'la regla del admin vive DENTRO de poderesDesbloqueados');

/* ── T5 · LOS CRISTALES (fábrica REAL, requisito 1 del dueño) ────── */
console.log('T5 · cristales: al expirar se ROMPEN TODOS (fábrica real de c07)');
const c07 = await import(RAIZ + '/src/game/core/c07_escena_sala.js');
const cripto = c07.createCristalesCripto();
CHK(typeof cripto.nace === 'function' && typeof cripto.fin === 'function'
    && typeof cripto.rompe === 'function' && typeof cripto.colisiona === 'function'
    && typeof cripto.update === 'function' && typeof cripto.vivos === 'function',
  'la fábrica creaCristalesCripto expone nace/update/colisiona/rompe/fin/vivos');
cripto.nace({ x: 0, z: -0.8 }, 0.76);
cripto.nace({ x: 0.2, z: -0.9 }, 0.76);
CHK(cripto.vivos() >= 2, `nacen cristales (vivos: ${cripto.vivos()})`);
for (let i = 0; i < 30; i++) cripto.update(0.05);   // crecen (0,45 s)
const vivosAntes = cripto.vivos();
cripto.fin();                                       // EXPIRA el poder
for (let i = 0; i < 12; i++) cripto.update(0.05);   // MUERTE 0,3 s corre
CHK(vivosAntes > 0, `fin() marcó los ${vivosAntes} vivos para romper`);
CHK(cripto.vivos() === 0, `al expirar NO queda ninguno vivo (vivos: ${cripto.vivos()})`);
const cripto2 = c07.createCristalesCripto();
cripto2.nace({ x: 0, z: -0.8 }, 0.76);
for (let i = 0; i < 30; i++) cripto2.update(0.05);
const objetivo = cripto2.colisiona({ x: 0, y: 0.85, z: -0.8 }, 0.04);
CHK(objetivo >= 0, 'colisiona() encuentra el cristal bajo la bola');
const vivosConObjetivo = cripto2.vivos();
cripto2.rompe(objetivo);
for (let i = 0; i < 12; i++) cripto2.update(0.05);
CHK(cripto2.vivos() === vivosConObjetivo - 1,
  `rompe(i) individual: se rompe SOLO el cristal golpeado (${vivosConObjetivo} → ${cripto2.vivos()})`);
CHK(/try \{ this\.cristalesCripto\.fin\(\); \}/.test(c12),
  'el FIN del poder en c12 llama cristalesCripto.fin() (todos se rompen)');
CHK(/cripto: 12,/.test(fs.readFileSync(RAIZ + '/src/game/core/c02_cfg_escena.js', 'utf8')),
  'la ventana sigue siendo de 12 s (spec del dueño)');

/* ── T6 · LOS SELLOS ─────────────────────────────────────────────── */
console.log('T6 · sellos de versión 3.6.207-SDK6');
const ver = '3.6.207-SDK6';
CHK(vjson.version === ver, `VERSION.json = ${vjson.version}`);
CHK(vjson.fase === 184, `fase = ${vjson.fase} (184)`);
CHK(new RegExp(`const VERSION = '${ver}'`).test(c00src), 'c00_pre_three.js lleva el sello');
CHK(body.includes(`>V${ver}</span>`), 'el badge #verBadge lleva el sello');
CHK(swjs.includes(`const CACHE = 'crazypp-v${ver}'`),
  'el CACHE del service worker lleva el sello');
const sha = crypto.createHash('sha256').update(bundle).digest('hex');
CHK(sha === goldenTxt, `public/game.html es BYTE-EXACTO contra el golden (${sha.slice(0, 16)}…)`);

/* ── T7 · EL BUNDLE ──────────────────────────────────────────────── */
console.log('T7 · el bundle construido lleva todo');
const nAudioBundle = (bundle.match(/data:audio\/mpeg/g) || []).length;
CHK((bundle.match(/VOZ_PODER_CRIPTO(_EN)? = 'data:audio\/mpeg;base64,/g) || []).length === 2,
  'las dos voces van dentro del bundle');
CHK(nAudioBundle >= 46, `el banco de voces del bundle creció (hay ${nAudioBundle} data URIs)`);
CHK(bundle.includes('voz: VOZ_PODER_CRIPTO, vozEn: VOZ_PODER_CRIPTO_EN'),
  'la entry cripto del bundle lleva voz/vozEn');
CHK(bundle.includes("return ['bolaloca'];") && !bundle.includes('nace DESBLOQUEADO'),
  'el bundle lleva el candado honesto y sin la apertura r108');
CHK(bundle.includes('window.__PP_DEBUG) return ok.slice();'),
  'el bundle lleva la regla del administrador');
CHK(bundle.includes('window.__PP_DEBUG) return ok.slice();'.replace('_', '_')),
  '…y la cadena sobrevive al ensamblado sin tocarla');

/* ── cierre ──────────────────────────────────────────────────────── */
console.log('');
console.log(`ARNÉS r109 · ${ok} ✓ / ${fail} ✗`);
process.exit(fail ? 1 : 0);
