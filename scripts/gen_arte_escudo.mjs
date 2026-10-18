// Arte propio de la etapa «ESCUDO DE PALA · DEFENSA DEL CASCO» (V3.5.0-ESC1)
// 6 imágenes de sala (14 m fondo × 10 m ancho × 6 m alto) + pantallainfo HUD.
// Estilo: el del dueño en Estación Orbital — 2D cel-shaded, azul/gris/naranja.
import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';
import path from 'path';

const OUT = '/home/z/my-project/public/championships/estacion_orbital/assets/escudo_pala';
fs.mkdirSync(OUT, { recursive: true });

const STYLE = 'stylized video game 2D background art, cartoon cel-shaded style, clean bold outlines, ' +
  'sci-fi spaceship interior, blue grey and orange color palette, crisp detail, no text, no watermark';

const PIEZAS = [
  {
    f: 'frente.jpg', s: '1344x768',
    p: 'Front wall of a spaceship defense deck: a huge breached hull opening in the center sealed by a translucent glowing blue hexagonal energy containment field, deep space visible through the field with a small fleet of menacing pirate raiders and a large planet with rings, thick metal ribs around the breach, side wall panels with orange emergency lights and pipes, ' + STYLE,
  },
  {
    f: 'izquierda.png', s: '1440x736',
    p: 'Long interior bulkhead wall of a spaceship defense deck, NO windows: technical metal panels, glowing control consoles with tiny screens, orange emergency light strips, warning decals, visible battle damage with scorched panels, dents and a small sparking cable, pipes and cable trays along the top, ' + STYLE,
  },
  {
    f: 'derecha.png', s: '1440x736',
    p: 'Long interior bulkhead wall of a spaceship defense deck, NO windows: technical metal panels, a wall-mounted tool rack and storage lockers, glowing control console, orange emergency light strips, visible battle damage with scorched panels and hull dents, a wall fire extinguisher, pipes along the top, ' + STYLE,
  },
  {
    f: 'trasera.jpg', s: '1344x768',
    p: 'Rear bulkhead wall of a spaceship defense deck: heavy armored wall with a large central recessed archway framed by thick metal ribs and hexagon bolt patterns, the archway interior filled with dark faint blue hexagonal grid glow, side cabinets and equipment lockers, orange warning lights on top, NO windows, ' + STYLE,
  },
  {
    f: 'techo.jpg', s: '864x1152',
    p: 'Ceiling of a spaceship defense deck viewed from below: industrial metal beams crossing, rectangular white light panels glowing, ventilation ducts, cables, orange hazard markings, symmetric composition, ' + STYLE,
  },
  {
    f: 'suelo.jpg', s: '864x1152',
    p: 'Metal deck floor of a spaceship defense deck viewed from straight above: riveted plated metal floor with panel lines, a single glowing circular defense platform near the bottom center with blue hexagon energy pattern and orange rim lights, scattered yellow hazard stripes and subtle scuffs, ' + STYLE,
  },
  {
    f: 'pantallainfo.png', s: '1440x736',
    p: 'Wide sci-fi HUD monitor screen frame for a spaceship game UI, empty screen: dark navy display with a very subtle hexagon pattern and thin grid, rounded metal bezel, blue and orange corner brackets, small blank status chips along the bottom edge, the center is completely empty with no text and no icons, ' + STYLE,
  },
];

const zai = await ZAI.create();
for (const { f, s, p } of PIEZAS) {
  const out = path.join(OUT, f);
  if (fs.existsSync(out) && fs.statSync(out).size > 40000) {
    console.log('· ya existe, salto', f);
    continue;
  }
  let hecho = false;
  for (let i = 0; i < 3 && !hecho; i++) {
    try {
      const r = await zai.images.generations.create({ prompt: p, size: s });
      const b64 = r.data[0].base64;
      if (!b64) throw new Error('respuesta sin base64');
      fs.writeFileSync(out, Buffer.from(b64, 'base64'));
      console.log('✓', f, s, fs.statSync(out).size, 'B');
      hecho = true;
    } catch (e) {
      console.error(`✗ ${f} intento ${i + 1}:`, e.message);
      await new Promise((r2) => setTimeout(r2, 1200 * (i + 1)));
    }
  }
  if (!hecho) { console.error('FALLO definitivo:', f); process.exit(1); }
}
console.log('ARTE ESCUDO COMPLETO:', fs.readdirSync(OUT).join(', '));
