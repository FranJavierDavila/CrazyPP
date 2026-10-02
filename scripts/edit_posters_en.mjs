// v2.27 · Genera los carteles ingleses editando el arte del usuario
// (solo cambia el texto del rótulo; el resto del arte se conserva).
import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';

const jobs = [
  {
    src: '/home/z/my-project/upload/victoria.png',
    out: '/home/z/my-project/scripts/poster_win_en_raw.png',
    prompt: "Replace ONLY the Spanish text on the yellow ribbon banner that reads '¡HAS GANADO!' with the English text 'YOU WON!' in the same bold cartoon lettering style, same yellow letters with dark outline, same position and size. Keep absolutely everything else identical: the CRAZY PING PONG logo, the red paddle, the white ball, yellow stars, blue stadium background, crowd, flags, table and net.",
  },
  {
    src: '/home/z/my-project/upload/derrota.png',
    out: '/home/z/my-project/scripts/poster_lose_en_raw.png',
    prompt: "Replace ONLY the Spanish text '¡HAS PERDIDO!' on the dark navy brush-stroke banner with the English text 'YOU LOST!' in the same white bold cartoon lettering with red brush stroke behind, same position and size. Keep absolutely everything else identical: the CRAZY PING PONG logo, the red X marks, red paddle, white ball, blue stadium background, crowd, flags, table and net.",
  },
];

const zai = await ZAI.create();
for (const j of jobs) {
  const b64 = fs.readFileSync(j.src).toString('base64');
  const dataUrl = `data:image/png;base64,${b64}`;
  console.log('editando', j.out, '...');
  const r = await zai.images.generations.edit({
    prompt: j.prompt,
    images: [{ url: dataUrl }],
    size: '1344x768',
  });
  if (!r?.data?.[0]?.base64) throw new Error('respuesta sin imagen para ' + j.out);
  fs.writeFileSync(j.out, Buffer.from(r.data[0].base64, 'base64'));
  console.log('OK ->', j.out);
}
