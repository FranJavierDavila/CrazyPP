#!/usr/bin/env node
/* CRAZY PING PONG · r128 · TESTS DE LA VERIFICACIÓN DE CLAIMS (A1, A3).
 * Ejecuta la FUENTE REAL (src/game/core/c09b_red_nucleo.js) en Node:
 *
 *   1 · claimPlausible: acepta el claim legítimo siguiente (r=applied+1)
 *   2 · claimPlausible: RECHAZA duplicados (r ≤ aplicado) → camino clásico
 *   3 · claimPlausible: RECHAZA saltos imposibles (r > aplicado+2)
 *   4 · claimPlausible: RECHAZA ganadores inválidos y valores no numéricos
 *   5 · claimPlausible: RECHAZA ráfagas (<250 ms entre claims aceptados)
 *   6 · MatchSync.onClaim SIN la ventana de c09: el primero se aplica igual
 *       (documento del porqué de la ventana: la pureza no puede verificar)
 *   7 · A3: el alfabeto del código sigue sin 0/O/1/I/L (31 símbolos)
 *
 * La VENTANA de 600 ms vive en c09 (NetLink._holdClaim, necesita window/
 * timers y el árbitro local): este test cubre la DECISIÓN pura que la
 * gobierna. Uso: node --no-warnings scripts/test_r128_claims.mjs
 */
import { PPNET } from '../src/game/core/c09b_red_nucleo.js';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};

const P = PPNET;
const T0 = 10_000;

/* — 1 · claim legítimo siguiente ———————————————————————————————————— */
chk(P.claimPlausible({ r: 5, w: 'ai', c: 'net_stay' }, 4, T0, 0) === true,
    '1 · claim del rally siguiente se acepta a verificación');
chk(P.claimPlausible({ r: 6, w: 'let', c: 'let' }, 4, T0 + 1000, 0) === true,
    '1 · r=aplicado+2 sigue dentro del sesgo de red permitido');

/* — 2 · duplicados → camino clásico (no «implausible») ——————————————— */
chk(P.claimPlausible({ r: 4, w: 'ai', c: 'out' }, 4, T0, 0) === false,
    '2 · r == aplicado (duplicado) no entra a verificación');
chk(P.claimPlausible({ r: 3, w: 'ai', c: 'out' }, 4, T0, 0) === false,
    '2 · r < aplicado (antiguo) no entra a verificación');

/* — 3 · saltos imposibles ———————————————————————————————————————————— */
chk(P.claimPlausible({ r: 50, w: 'player', c: 'out' }, 4, T0, 0) === false,
    '3 · salto de rallyId (+46) rechazado');
chk(P.claimPlausible({ r: 7, w: 'player', c: 'out' }, 4, T0, 0) === false,
    '3 · salto de rallyId (+3) rechazado');

/* — 4 · valores inválidos ———————————————————————————————————————————— */
chk(P.claimPlausible({ r: 5, w: 'host', c: 'out' }, 4, T0, 0) === false,
    '4 · ganador inválido («host») rechazado');
chk(P.claimPlausible({ r: 5, w: '', c: 'out' }, 4, T0, 0) === false,
    '4 · ganador vacío rechazado');
chk(P.claimPlausible({ r: '5', w: 'ai', c: 'out' }, 4, T0, 0) === false,
    '4 · rallyId como string rechazado (cliente manipulado)');
chk(P.claimPlausible({ r: -1, w: 'ai', c: 'out' }, 4, T0, 0) === false,
    '4 · rallyId negativo rechazado');
chk(P.claimPlausible(null, 4, T0, 0) === false,
    '4 · claim nulo rechazado');
chk(P.claimPlausible({ r: NaN, w: 'ai', c: 'out' }, 4, T0, 0) === false,
    '4 · rallyId NaN rechazado');

/* — 5 · cadencia (anti-ráfaga) ——————————————————————————————————————— */
chk(P.claimPlausible({ r: 5, w: 'ai', c: 'out' }, 4, T0, T0 - 100) === false,
    '5 · segundo claim a 100 ms rechazado (ráfaga)');
chk(P.claimPlausible({ r: 5, w: 'ai', c: 'out' }, 4, T0, T0 - 249) === false,
    '5 · segundo claim a 249 ms rechazado');
chk(P.claimPlausible({ r: 5, w: 'ai', c: 'out' }, 4, T0, T0 - 250) === true,
    '5 · segundo claim a 250 ms entra (cadencia mínima)');
chk(P.claimPlausible({ r: 5, w: 'ai', c: 'out' }, 4, T0, null) === true,
    '5 · sin marca previa (primer claim de la sesión) entra');

/* — 6 · MatchSync puro sin ventana (documenta por qué existe) ————————— */
{
  const s = new P.MatchSync('host');
  const a = s.onClaim({ r: 9, w: 'player', c: 'out' }, 'ai');
  chk(a.apply === true && a.agree === true,
      '6 · onClaim puro aplica el primero sin confrontar (motivo de la ventana en c09)');
  const b = s.onClaim({ r: 9, w: 'ai', c: 'out' }, 'player');
  chk(b.apply === false && b.agree === false,
      '6 · el segundo claim del mismo rally confronta y DISCREPA (resync)');
}

/* — 7 · A3: alfabeto del código de sala ——————————————————————————————— */
{
  // import del c09 real no es posible en Node (window/Peer): verificamos la
  // constante por fuente, mismo patrón que usan las baterías de higiene.
  const fs = await import('node:fs');
  const fnt = fs.readFileSync(
    new URL('../src/game/core/c09_red_netlink.js', import.meta.url), 'utf8');
  const m = /CODE_CHARS = '([A-Z0-9]+)'/.exec(fnt);
  chk(!!m && m[1].length === 31, '7 · CODE_CHARS mantiene 31 símbolos');
  chk(!!m && !/[01OI]/.test(m[1]), '7 · CODE_CHARS sin 0/O/1/I/L (dictable por voz)');
  chk(fnt.includes('getRandomValues(buf)'),
      '7 · genCode usa crypto.getRandomValues (A3)');
  chk(fnt.includes('_holdClaim') && fnt.includes('claimPlausible'),
      '7 · c09 cablea la ventana de verificación (A1)');
}

console.log(`\nRESULTADO: ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);
