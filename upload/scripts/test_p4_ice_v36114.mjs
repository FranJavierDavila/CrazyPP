#!/usr/bin/env node
/* CRAZY PING PONG · r125 · P4 — TESTS DEL ICE DE LA PRIMERA PARTIDA REAL
 * Ejecuta la FUENTE REAL (src/game/core/c09_red_netlink.js) en Node — el
 * mismo código que corre en el Quest — y verifica, sin visor y sin DOM:
 *
 *   1 · ICE_CFG local: OpenRelay (muerto) FUERA, STUN Google + Cloudflare,
 *       iceCandidatePoolSize intacto.
 *   2 · _sanearICE: urls válidas, puerto 53 fuera (sin confundirlo con
 *       :5349), TURN sin credencial fuera, entradas degeneradas fuera.
 *   3 · ICE_ASYNC: respuesta del worker adoptada y cacheada (2ª llamada
 *       sin fetch), caída del worker → STUN local honesto, JSON basura →
 *       local, remoto inservible → local, refresco al expirar el TTL,
 *       endpoint vacío → local sin tocar red, derivación de la base desde
 *       PP_TELEMETRY_ENDPOINT.
 *
 * Carga al estilo build_game.py: el bloque DEPS-FASE2 (imports generados
 * que en el monofile comparten ámbito) se elimina antes de importar —
 * c09 queda sin dependencias y el módulo es 100% el de producción.
 *
 * Uso: node --no-warnings scripts/test_p4_ice_v36114.mjs
 * ( registrado como capa QA de la ronda r125 · P4 )
 */
import { readFileSync, writeFileSync } from 'node:fs';

const _src = readFileSync(new URL('../src/game/core/c09_red_netlink.js', import.meta.url), 'utf8')
  .replace(/\/\* DEPS-FASE2-INICIO[\s\S]*?DEPS-FASE2-FIN \*\/\n?/g, '');
const _tmp = '/tmp/c09_p4_under_test.mjs';
writeFileSync(_tmp, _src);
const { NetLink } = await import('file://' + _tmp);

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  ok += cond ? 1 : 0;
  fails += cond ? 0 : 1;
};
const dorme = (ms) => new Promise((r) => setTimeout(r, ms));

/* estado de red limpio entre tests */
const reset = () => { NetLink._iceRem = null; NetLink._iceRemT0 = 0; NetLink._iceFailT0 = 0; };
const _fetchReal = globalThis.fetch;
delete globalThis.PP_ICE_ENDPOINT;
delete globalThis.PP_TELEMETRY_ENDPOINT;

try {
  /* 1 · ICE_CFG local: el TURN muerto NO vuelve jamás */
  const loc = NetLink.ICE_CFG();
  chk(!JSON.stringify(loc).includes('openrelay'),
    '1 · ICE_CFG: OpenRelay (muerto) fuera del fallback local');
  chk(Array.isArray(loc.iceServers) && loc.iceServers.length === 1 &&
      loc.iceServers[0].urls.every((u) => u.startsWith('stun:')) &&
      loc.iceServers[0].urls.some((u) => u.includes('stun.cloudflare.com')) &&
      loc.iceServers[0].urls.some((u) => u.includes('stun.l.google.com')),
    `1 · ICE_CFG: sólo STUN Google + Cloudflare (${JSON.stringify(loc.iceServers)})`);
  chk(loc.iceCandidatePoolSize === 4, '1 · ICE_CFG: pool de candidatos intacto (4)');

  /* 2 · _sanearICE: cinturón y tirantes */
  const san = NetLink._sanearICE([
    { urls: ['stun:stun.cloudflare.com:3478'] },
    { urls: ['turn:turn.cloudflare.com:53?transport=udp'], username: 'u', credential: 'c' },
    { urls: ['turn:turn.cloudflare.com:3478?transport=udp'], username: 'u', credential: 'c' },
    { urls: ['turns:turn.cloudflare.com:5349?transport=tcp'], username: 'u', credential: 'c' },
    { urls: ['turn:turn.cloudflare.com:80?transport=tcp'], username: '', credential: '' },
    { urls: ['nota:mal'] },
    null,
    { urls: ['stun:buena'] , username: 'x', credential: 'y' },
  ]);
  chk(san.length === 4, `2 · saneo: 4 servidores vivos (${san.length})`);
  chk(san.every((s) => s.urls.every((u) => !/:53(\?|$)/.test(u))),
    '2 · saneo: puerto 53 fuera (sin confundirlo con :5349)');
  chk(san.every((s) => s.urls.every((u) => /^(stun|turn|turns):/.test(u))),
    '2 · saneo: esquemas stun/turn/turns sólo');
  chk(san.every((s) => !s.urls[0].startsWith('turn') || (s.username && s.credential)),
    '2 · saneo: TURN siempre con username/credential');
  chk(NetLink._sanearICE(null).length === 0 && NetLink._sanearICE('x').length === 0 &&
      NetLink._sanearICE([{}]).length === 0,
    '2 · saneo: entradas degeneradas sin lanzar');

  /* 3a · ICE_ASYNC: worker vivo → TURN adoptado y cacheado */
  reset();
  let fetches = 0;
  globalThis.PP_ICE_ENDPOINT = 'https://worker.test/api';
  globalThis.fetch = async () => {
    fetches++;
    return { ok: true, json: async () => ({
      ok: true, turn: true, ttl: 21600,
      iceServers: [
        { urls: ['stun:stun.cloudflare.com:3478'] },
        { urls: ['turn:turn.cloudflare.com:3478?transport=udp', 'turn:turn.cloudflare.com:53?transport=udp'],
          username: 'u1', credential: 'c1' },
        { urls: ['turn:sin-credencial:80'], username: '', credential: '' },
      ],
    }) };
  };
  const rem = await NetLink.ICE_ASYNC();
  chk(fetches === 1 && rem.iceServers.length === 2,
    `3a · ICE_ASYNC: remoto adoptado, 1 fetch (${fetches}) y saneado (${rem.iceServers.length} servidores)`);
  chk(rem.iceServers[1].username === 'u1' && rem.iceServers[1].urls.length === 1,
    '3a · ICE_ASYNC: TURN con credencial y sin :53');
  chk(rem.iceCandidatePoolSize === 4, '3a · ICE_ASYNC: pool intacto en el remoto');
  const rem2 = await NetLink.ICE_ASYNC();
  chk(fetches === 1 && rem2 === rem, '3a · ICE_ASYNC: 2ª llamada servida de caché (sin fetch)');

  /* 3b · TTL expirado → refresca */
  NetLink.ICE_REM_TTL = 30;
  await dorme(45);
  await NetLink.ICE_ASYNC();
  chk(fetches === 2, '3b · ICE_ASYNC: TTL expirado → refresca (2º fetch)');
  NetLink.ICE_REM_TTL = 4 * 60 * 1000;

  /* 3c · worker caído → STUN local honesto y no martillea */
  reset();
  fetches = 0;
  globalThis.fetch = async () => { fetches++; throw new Error('conexión rehusada'); };
  const caido = await NetLink.ICE_ASYNC();
  chk(fetches === 1 && JSON.stringify(caido).includes('stun.cloudflare.com') &&
      !JSON.stringify(caido).includes('turn:'),
    `3c · worker caído → STUN local (${fetches} fetch, sin TURN)`);
  const caido2 = await NetLink.ICE_ASYNC();
  chk(fetches === 1 && caido2.iceServers.length === 1,
    '3c · caído: la 2ª llamada en 60 s NO repite el fetch (no martillea)');
  NetLink._iceFailT0 = 0;

  /* 3d · JSON basura → local */
  reset(); fetches = 0;
  globalThis.fetch = async () => { fetches++; return { ok: true, json: async () => ({ no_es: 'ice' }) }; };
  const basura = await NetLink.ICE_ASYNC();
  chk(fetches === 1 && basura.iceServers.length === 1 &&
      basura.iceServers[0].urls.every((u) => u.startsWith('stun:')),
    '3d · respuesta sin iceServers → local honesto');
  NetLink._iceFailT0 = 0;

  /* 3e · remoto inservible (todo basura) → local */
  reset(); fetches = 0;
  globalThis.fetch = async () => { fetches++; return { ok: true, json: async () => ({
    ok: true, iceServers: [{ urls: ['x:mal'] }, { urls: ['turn:sin-cred:1'], username: '', credential: '' }] }) }; };
  const inserv = await NetLink.ICE_ASYNC();
  chk(fetches === 1 && !JSON.stringify(inserv).includes('turn:'),
    '3e · remoto inservible tras saneo → local honesto');
  NetLink._iceFailT0 = 0;

  /* 3f · endpoint vacío → local sin tocar red */
  reset(); fetches = 0;
  delete globalThis.PP_ICE_ENDPOINT;
  const sinBase = await NetLink.ICE_ASYNC();
  chk(fetches === 0 && sinBase.iceServers.length === 1,
    '3f · sin endpoint de worker → local, cero red');

  /* 3g · base derivada de PP_TELEMETRY_ENDPOINT (hermana de c09c.base()) */
  globalThis.PP_TELEMETRY_ENDPOINT = 'https://w.test/api/tele';
  chk(NetLink._iceBase() === 'https://w.test/api',
    `3g · base derivada de telemetría (${NetLink._iceBase()})`);
  globalThis.PP_TELEMETRY_ENDPOINT = 'https://w.test/api/tele/';
  chk(NetLink._iceBase() === 'https://w.test/api', '3g · base con barra final tolerada');
  globalThis.PP_ICE_ENDPOINT = 'https://qa.test/hielo/';
  chk(NetLink._iceBase() === 'https://qa.test/hielo', '3g · PP_ICE_ENDPOINT manda (QA) y sin barra final');
} catch (e) {
  chk(false, 'excepción del harness: ' + (e && e.stack || String(e)));
} finally {
  globalThis.fetch = _fetchReal;
}

console.log(`RESULTADO: ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);
