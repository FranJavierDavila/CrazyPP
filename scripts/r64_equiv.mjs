// r64_equiv.mjs — FASE 158 · prueba de equivalencia de medallaDe:
// la escalera VIEJA (literales 3/85, 2/70, 1) contra la NUEVA
// (CONFIG_MEDALLAS de c02 importada de verdad) sobre todos los combos
// estrellas × precisión posibles. Cero diferencias esperadas.
import { CONFIG_MEDALLAS } from '/home/z/my-project/upload/src/game/core/c02_cfg_escena.js';

const E = CONFIG_MEDALLAS.estrellas, P = CONFIG_MEDALLAS.precision;
console.log('tabla viva:', JSON.stringify(CONFIG_MEDALLAS));

const vieja = (stN, acc) => {
  if (stN >= 3) return acc >= 85 ? 3 : 2;
  if (stN === 2) return acc >= 70 ? 2 : 1;
  if (stN === 1) return 1;
  return 0;
};
const nueva = (stN, acc) => {
  if (stN >= E.oro) return acc >= P.oro ? 3 : 2;
  if (stN >= E.plata) return acc >= P.plata ? 2 : 1;
  if (stN >= E.bronce) return 1;
  return 0;
};

let dif = 0, combos = 0;
for (let stN = 0; stN <= 6; stN++) {
  for (let acc = 0; acc <= 100; acc++) {
    combos++;
    if (vieja(stN, acc) !== nueva(stN, acc)) { dif++; console.log('DIF', stN, acc, vieja(stN, acc), nueva(stN, acc)); }
  }
}
// valores sensoriales de la casa (los que cita la documentación r120):
const muestra = [[0,0],[1,0],[1,85],[2,69],[2,70],[2,85],[3,84],[3,85],[4,90]];
for (const [s,a] of muestra) console.log(`  stN=${s} acc=${a}% → medalla ${nueva(s,a)}`);
console.log(dif === 0 ? `EQUIVALENCIA OK — 0 diferencias en ${combos} combos` : `FALLO: ${dif} diferencias`);
process.exit(dif === 0 ? 0 : 1);
