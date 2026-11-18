#!/usr/bin/env node
/* ronda 30 (v3.6.126) · GENERADOR IA DE LOS 3 SALONES — arte de ilustración
 * rica (nivel Locura/Magia) con el modelo de generación de imagen.
 * 18 imágenes: neon/observatorio/dojo × frente,fondo,izquierda,derecha,suelo,techo.
 * Salida: scripts/_r30_assets/gen/<hall>_<plano>.png (luego recorta _r30_postproceso_halls.py)
 * Reintentos con retroceso ante 429/5xx. Uso: node scripts/_r30_gen_halls.mjs [--solo neon] */
import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';
import path from 'path';

const OUT = '/home/z/my-project/scripts/_r30_assets/gen';
fs.mkdirSync(OUT, { recursive: true });

const ESTILO = 'richly detailed stylized video game environment art, painterly illustration, dramatic volumetric lighting, ambient occlusion, deep shadows in corners, rich saturated colors, subtle texture grain, masterpiece quality, no text, no letters, no watermark, no people';
const MURO = 'straight-on frontal view of a single interior wall filling the entire frame';
const LATERAL = 'wide panoramic banner view of one long interior wall, repeating rhythm, seen straight from the center of the room';
const SUELO = 'top-down flat view of a floor filling the entire frame';
const TECHO = 'bottom-up flat view of a ceiling filling the entire frame';

const PROMPTS = {
  neon: {
    frente: `${MURO} of a 1980s retro video game arcade hall: a row of glowing arcade cabinets with bright CRT screens showing a tiny colorful pixel table tennis game, huge neon emblem shaped like a table tennis paddle striking a ball, purple pink and cyan neon tubes, tangled cables, dark wall panels with scuffs and stickers, moody dark ambiance lit only by neon glow, glow reflecting on glossy surfaces, ${ESTILO}`,
    fondo: `${MURO} of a 1980s retro arcade hall: prize counter with shelves of plush toys and golden trophies, glowing jukebox, huge neon setting sun with classic horizontal cuts over a wireframe grid horizon on the back wall, pink and cyan neon strips, dark moody room lit by neon, ${ESTILO}`,
    izquierda: `${LATERAL} of a 1980s retro arcade: wall-mounted CRT monitors flickering with colorful static, rows of small neon marquee signs shaped like arrows and stars, cable trays and ventilation grilles, checkered neon wainscoting, sticker graffiti, purple and pink glow washing the wall, ${ESTILO}`,
    derecha: `${LATERAL} of a 1980s retro arcade: long wall of tall arcade cabinets in perspective rhythm, their marquees glowing magenta and cyan, a big neon clock and neon arrows, dark scuffed panels, cables hanging, atmosphere of purple haze and floating dust in light beams, ${ESTILO}`,
    suelo: `${SUELO} of a retro arcade: black glossy checkered tiles reflecting pink and cyan neon light, worn scuffs and faded coin stickers, glowing neon grid lines converging toward a large central circular emblem of a glowing table tennis paddle and ball embedded in the floor, dust and small debris, ${ESTILO}`,
    techo: `${TECHO} of a retro arcade: dark metal ceiling panels with tangled neon tubes in purple pink and cyan, hanging arcade banners, small spotlights with visible volumetric beams and dusty haze, cable bundles, rusty vents, ${ESTILO}`,
  },
  observatorio: {
    frente: `${MURO} of a space station observation deck: huge panoramic window with hexagonal frame revealing planet Earth with blue oceans, white clouds and glowing thin atmosphere limb over a deep starfield, window frame with bolts and rubber seals, yellow-black warning chevrons, base lined with control consoles with glowing buttons and small green trajectory screens, cool blue light filling the room, ${ESTILO}`,
    fondo: `${MURO} of a space station: massive circular airlock hatch with locking wheel and status lamps, red emergency light glow, pipes with valves and pressure gauges, tool racks, small round porthole with stars, riveted metal panels with wear and scratches, ${ESTILO}`,
    izquierda: `${LATERAL} of a space station corridor wall: riveted metal panels with scratches and wear, glowing white strip lights, cable runs with clips, screens showing orbital trajectory charts, yellow-black hazard stripes at the base, small portholes with starfield, fire extinguisher mounted on panel, ${ESTILO}`,
    derecha: `${LATERAL} of a space station laboratory wall: equipment racks with blinking lights, translucent screens with glowing orbital diagrams, bundles of cables, ventilation ducts, a small observation window with Earth limb visible, cool white and cyan lighting with red accent lamps, ${ESTILO}`,
    suelo: `${SUELO} of a space station deck: diamond-tread metal plates with scuffs and wear, yellow-black hazard borders, glowing blue guide light strips converging toward a central circular hatch with locking bolts, subtle reflections, sci-fi grime, ${ESTILO}`,
    techo: `${TECHO} of a space station: structural trusses and ribs, ribbed light diffusers glowing cool white, thick cable bundles with connectors, round air ducts, small amber warning lights, metallic wear, ${ESTILO}`,
  },
  dojo: {
    frente: `${MURO} of a traditional japanese martial arts dojo at dusk, completely EMPTY training hall with NO furniture and NO bed: tokonoma alcove with a hanging kakejiku scroll painted with a large black enso brush circle, ikebana flower arrangement in a ceramic vase, dark polished wooden pillars, warm glow of an andon paper lantern, cherry blossom branch visible through a shoji panel, soft evening light, ${ESTILO}`,
    fondo: `${MURO} of a traditional japanese dojo: wall of shoji sliding screens glowing warm orange with the silhouette of Mount Fuji and cranes behind the paper, carved ranma transom above, low shelf with bonsai tree and calligraphy brushes, wooden pillars, serene warm light, ${ESTILO}`,
    izquierda: `${LATERAL} of a traditional japanese dojo: wooden pillars and shoji sliding doors with soft garden silhouette behind the paper, vertical naginata and bokken weapon stand, pair of hanging scrolls, carved wooden transom, warm lantern light pooling on the wood, ${ESTILO}`,
    derecha: `${LATERAL} of a traditional japanese dojo interior: row of shoji panels with sunset glow behind the paper, dark wooden beam structure, mounted armor stand with kabuto helmet, cherry blossom petals drifting, hanging andon lanterns, warm amber light, ${ESTILO}`,
    suelo: `${SUELO} of a japanese dojo: tatami straw mats with dark green cloth borders in the classic pattern, visible weave texture, a large ink enso brush circle painted across the central mats, scattered pink cherry blossom petals, warm evening light from shoji screens, wooden veranda edge on one side, ${ESTILO}`,
    techo: `${TECHO} of a japanese dojo: dark exposed wooden beams and rafters, square washi paper panels glowing warm amber between the beams, rope ties, subtle smoke haze in the lantern light, fine wood grain, ${ESTILO}`,
  },
};

const TAM = { frente: '1536x768', fondo: '1536x768', izquierda: '1536x768', derecha: '1536x768', suelo: '864x1152', techo: '864x1152' };
const solo = process.argv.includes('--solo') ? process.argv[process.argv.indexOf('--solo') + 1] : null;
const trabajos = [];
for (const hall of Object.keys(PROMPTS)) {
  if (solo && hall !== solo) continue;
  for (const plano of Object.keys(PROMPTS[hall])) trabajos.push({ hall, plano });
}

const zai = await ZAI.create();
let ok = 0, fallo = 0;
for (let i = 0; i < trabajos.length; i += 3) {
  const lote = trabajos.slice(i, i + 3);
  await Promise.all(lote.map(async ({ hall, plano }) => {
    const dest = path.join(OUT, `${hall}_${plano}.png`);
    if (fs.existsSync(dest) && fs.statSync(dest).size > 100000) { ok++; console.log(`⏭  ${hall}/${plano} ya existe`); return; }
    for (let intento = 1; intento <= 4; intento++) {
      try {
        const r = await zai.images.generations.create({ prompt: PROMPTS[hall][plano], size: TAM[plano] });
        const b64 = r && r.data && r.data[0] && r.data[0].base64;
        if (!b64) throw new Error('respuesta sin base64');
        const buf = Buffer.from(b64, 'base64');
        if (buf.length < 50000) throw new Error(`imagen sospechosamente pequeña (${buf.length} B)`);
        fs.writeFileSync(dest, buf);
        ok++; console.log(`✓ ${hall}/${plano} ${(buf.length / 1024) | 0} KB`);
        return;
      } catch (e) {
        console.log(`✗ ${hall}/${plano} intento ${intento}: ${e.message}`);
        if (intento < 4) await new Promise((res) => setTimeout(res, 15000 * intento));
        else fallo++;
      }
    }
  }));
}
console.log(`\nGENERADOS ${ok}/${trabajos.length} · FALLOS ${fallo}`);
process.exit(fallo > 0 ? 1 : 0);
