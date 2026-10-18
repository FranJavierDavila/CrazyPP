// Regenera techo + izquierda del Escudo de Pala en vista PLANA (sin perspectiva)
import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';
import path from 'path';

const OUT = '/home/z/my-project/public/championships/estacion_orbital/assets/escudo_pala';
const STYLE = 'stylized video game 2D background art, cartoon cel-shaded style, clean bold outlines, ' +
  'blue grey and orange color palette, crisp detail, no text, no watermark';

const PIEZAS = [
  {
    f: 'techo.jpg', s: '864x1152',
    p: 'Flat 2D game asset: spaceship ceiling panel seen perfectly straight-on from directly below, ' +
       'orthographic front view with NO perspective and NO depth, like a texture sheet. Symmetric industrial ' +
       'composition: central rectangular white light panel surrounded by metal beams, rivets, ventilation ' +
       'grilles, small pipes along the edges, orange hazard corner markings, dark blue grey metal. ' +
       'No floor, no walls, no corridor, no vanishing point, no door. ' + STYLE,
  },
  {
    f: 'izquierda.png', s: '1440x736',
    p: 'Flat 2D game asset: one continuous spaceship interior wall section seen perfectly straight-on, ' +
       'orthographic front view with NO perspective and NO depth, like a texture sheet. Covered with technical ' +
       'metal panels, two glowing control consoles with tiny screens, orange emergency light strips, warning ' +
       'decals, visible battle damage with scorched panels and small dents, pipes along the top edge. ' +
       'NO windows, no floor, no corridor, no vanishing point, no side walls. ' + STYLE,
  },
];

const zai = await ZAI.create();
for (const { f, s, p } of PIEZAS) {
  const out = path.join(OUT, f);
  const bak = path.join(OUT, 'descarte_' + f.replace('.', '_v1.'));
  try { fs.renameSync(out, bak); } catch (e) { /* */ }
  let hecho = false;
  for (let i = 0; i < 3 && !hecho; i++) {
    try {
      const r = await zai.images.generations.create({ prompt: p, size: s });
      const b64 = r.data[0].base64;
      if (!b64) throw new Error('respuesta sin base64');
      fs.writeFileSync(out, Buffer.from(b64, 'base64'));
      console.log('✓', f, fs.statSync(out).size, 'B');
      hecho = true;
    } catch (e) {
      console.error(`✗ ${f} intento ${i + 1}:`, e.message);
      await new Promise((r2) => setTimeout(r2, 1200 * (i + 1)));
    }
  }
  if (!hecho) { console.error('FALLO definitivo:', f); process.exit(1); }
}
console.log('OK');
