/**
 * test_worker_r169.mjs — EJECUCIÓN REAL de la lógica social del worker
 * (scripts/worker-tele/worker.js) con un D1 SIMULADO fiel a sus
 * sentencias: ALTER idempotente, presencia con mj/vis (PRIVADA por
 * defecto), listado GET con passthrough, invitaciones con mj y su
 * guardia anti-spam, y limpieza del buzón.
 *
 * Uso: node scripts/test_worker_r169.mjs
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { strict as assert } from 'node:assert';

/* — copia del worker real a /tmp como .mjs (sólo para importar) — */
const FUENTE = '/home/z/my-project/upload/scripts/worker-tele/worker.js';
mkdirSync('/tmp/worker_test_r169', { recursive: true });
const DESTINO = '/tmp/worker_test_r169/worker.mjs';
writeFileSync(DESTINO, readFileSync(FUENTE));
const worker = await import(DESTINO);

/* --------------------- D1 SIMULADO --------------------- */
function makeD1() {
  const presencia = new Map();   // pid → fila
  const invitas = [];            // filas con id autoincremental
  const columnas = {
    presencia: ['pid', 'n', 'v', 'st', 'code', 't'],
    invitas: ['id', 'de', 'deN', 'para', 'code', 't'],
  };
  let ids = 0;
  const RE_ONCONFLICT_PRES =
    /INSERT INTO presencia \(pid, n, v, st, code, mj, vis, t\) VALUES \(\?, \?, \?, \?, \?, \?, \?, \?\)/;
  const RE_INSERT_INV =
    /INSERT INTO invitas \(de, deN, para, code, mj, t\) VALUES \(\?, \?, \?, \?, \?, \?\)/;
  function stmt(sql, args = []) {
    /* DEVUELVE LA PROMESA DEL RESULTADO directamente (el worker hace
     * await prepare(...).run() — nunca consume un objeto {run,first,all}) */
    const s = sql.replace(/\s+/g, ' ').trim();
    if (s.startsWith('CREATE TABLE') || s.startsWith('CREATE INDEX')) {
      return (async () => ({}))();
    }
    if (s.startsWith('ALTER TABLE')) {
      // D1 FALLA si la columna ya existe (el worker debe tragárselo)
      const m = s.match(/^ALTER TABLE (presencia|invitas) ADD COLUMN (\w+)/);
      if (!m || columnas[m[1]].includes(m[2])) {
        throw new Error('duplicate column name: ' + m[2]);
      }
      return (async () => { columnas[m[1]].push(m[2]); return {}; })();
    }
    if (s.startsWith('DELETE FROM presencia WHERE t <')) {
      return (async () => {
        for (const [k, r] of [...presencia]) if (r.t < args[0]) presencia.delete(k);
        return { meta: { changes: 0 } };
      })();
    }
    if (s.startsWith('DELETE FROM invitas WHERE t <')) {
      return (async () => {
        let n = 0;
        for (let i = invitas.length - 1; i >= 0; i--) {
          if (invitas[i].t < args[0]) { invitas.splice(i, 1); n++; }
        }
        return { meta: { changes: n } };
      })();
    }
    if (s.startsWith('DELETE FROM presencia WHERE pid')) {
      return (async () => {
        presencia.delete(args[0]);
        return { meta: { changes: 1 } };
      })();
    }
    if (RE_ONCONFLICT_PRES.test(s)) {
      return (async () => {
        const [pid, n, v, st, code, mj, vis, t] = args;
        presencia.set(pid, { pid, n, v, st, code, mj, vis, t });
        return { meta: { changes: 1 } };
      })();
    }
    if (s.startsWith('SELECT COUNT(*) n FROM presencia')) {
      return (async () => ({ n: presencia.size }))();
    }
    if (s.startsWith('SELECT pid, n, st, code, mj, vis, t FROM presencia')) {
      return (async () => ({
        results: [...presencia.values()]
          .sort((a, b) => b.t - a.t).slice(0, 30),
      }))();
    }
    if (s.startsWith('SELECT st, code FROM presencia WHERE pid')) {
      return (async () => {
        const r = presencia.get(args[0]);
        return (r && r.t > args[1]) ? { st: r.st, code: r.code } : null;
      })();
    }
    if (s.startsWith('SELECT COUNT(*) n FROM invitas WHERE para')) {
      return (async () => ({
        n: invitas.filter((r) => r.para === args[0]).length }))();
    }
    if (RE_INSERT_INV.test(s)) {
      return (async () => {
        invitas.push({ id: ++ids, de: args[0], deN: args[1], para: args[2],
          code: args[3], mj: args[4], t: args[5] });
        return { meta: { last_row_id: ids } };
      })();
    }
    if (s.startsWith('SELECT id, de, deN, code, mj, t FROM invitas WHERE para')) {
      return (async () => ({
        results: invitas.filter((r) => r.para === args[0])
          .sort((a, b) => b.t - a.t).slice(0, 8) }))();
    }
    if (s.startsWith('DELETE FROM invitas WHERE id = ? AND para = ?')) {
      return (async () => {
        const i = invitas.findIndex((r) => r.id === args[0] && r.para === args[1]);
        if (i >= 0) invitas.splice(i, 1);
        return { meta: { changes: i >= 0 ? 1 : 0 } };
      })();
    }
    if (s.startsWith('DELETE FROM invitas WHERE para = ?')) {
      return (async () => {
        const antes = invitas.length;
        for (let i = invitas.length - 1; i >= 0; i--) {
          if (invitas[i].para === args[0]) invitas.splice(i, 1);
        }
        return { meta: { changes: antes - invitas.length } };
      })();
    }
    throw new Error('SQL NO SIMULADA: ' + s);
  }
  return {
    prepare: (sql) => {
      const q = {
        args: [],
        sql,
        bind(...a) { this.args = a; return this; },
        run() { return stmt(this.sql, this.args); },
        first() { return stmt(this.sql, this.args); },
        all() { return stmt(this.sql, this.args); },
      };
      return q;
    },
    batch: async (lote) => {
      for (const q of lote) await q.run();
      return [];
    },
    _estado: { presencia, invitas, columnas },
  };
}

/* --------------------- llama al worker --------------------- */
async function llamada(d1, metodo, url, cuerpo) {
  const req = {
    method: metodo,
    url,
    text: async () => cuerpo || '',
  };
  const res = await worker.default.fetch(req, { DB: d1 });
  const txt = await res.text();
  return { status: res.status, body: JSON.parse(txt) };
}

const BASE = 'https://worker.test/api';
let pasan = 0, fallos = 0;
const check = (cond, label) => {
  console.log((cond ? '  OK  ' : '  FALLO: ') + label);
  if (cond) pasan++; else fallos++;
};

const d1 = makeD1();

/* 1 · arranque: CREATEs + 3 ALTERs (columnas nuevas) */
let r = await llamada(d1, 'GET', BASE + '/presencia');
check(r.status === 200 && r.body.ok, 'arranque social: CREATE + ALTER idempotente');
check(d1._estado.columnas.presencia.includes('mj') &&
      d1._estado.columnas.presencia.includes('vis') &&
      d1._estado.columnas.invitas.includes('mj'),
  'columnas nuevas en presencia (mj, vis) e invitas (mj)');

/* 2 · latido del ANFITRIÓN: sala pública en Duelos Locos */
r = await llamada(d1, 'POST', BASE + '/presencia', JSON.stringify({
  pid: 'aabbccddeeff1122', n: 'Ana', v: '3.6.165', st: 'sala',
  code: 'ABC12', mj: 'duelos', vis: 'pub' }));
check(r.body.ok, 'latido del anfitrión aceptado');

/* 3 · latido de una PRIVADA + uno libre */
await llamada(d1, 'POST', BASE + '/presencia', JSON.stringify({
  pid: '1122334455667788', n: 'Bea', v: '3.6.165', st: 'sala',
  code: 'ZZZ99', mj: 'normal', vis: 'pri' }));
await llamada(d1, 'POST', BASE + '/presencia', JSON.stringify({
  pid: '9988776655443322', n: 'Ciro', v: '3.6.165', st: 'libre' }));

/* 4 · GET lista: passthrough de mj/vis — y PRIVADA por defecto */
r = await llamada(d1, 'GET', BASE + '/presencia?lista=1');
const js = r.body.jugadores || [];
check(js.length === 3, 'listado con los 3 latidos');
const ana = js.find((j) => j.n === 'Ana');
const bea = js.find((j) => j.n === 'Bea');
const ciro = js.find((j) => j.n === 'Ciro');
check(ana && ana.mj === 'duelos' && ana.vis === 'pub' && ana.code === 'ABC12',
  'Ana viaja con su modalidad (duelos) y visibilidad (pub)');
check(bea && bea.mj === 'normal' && bea.vis === 'pri',
  'Bea (privada) viaja con mj normal y vis pri');
check(ciro && ciro.st === 'libre' && ciro.code === '' && ciro.vis === 'pri',
  'Ciro (libre): sin código y PRIVADO por defecto');

/* 5 · invitación con modalidad: sólo si la sala del remitente está viva */
r = await llamada(d1, 'POST', BASE + '/invita', JSON.stringify({
  de: 'aabbccddeeff1122', deN: 'Ana', para: '9988776655443322',
  code: 'ABC12', k: 'inv', mj: 'duelos' }));
check(r.body.ok, 'invitación aceptada (sala del remitente viva + código igual)');
const idInv = r.body.id;
r = await llamada(d1, 'POST', BASE + '/invita', JSON.stringify({
  de: '9988776655443322', deN: 'Ciro', para: 'aabbccddeeff1122',
  code: 'ABC12', mj: 'normal' }));
check(r.status === 409, 'invitación de un jugador SIN sala → 409 sala no activa');
r = await llamada(d1, 'POST', BASE + '/invita', JSON.stringify({
  de: 'aabbccddeeff1122', deN: 'Ana', para: 'aabbccddeeff1122',
  code: 'ABC12' }));
check(r.status === 400, 'invitarse a uno mismo → 400');

/* 6 · el buzón devuelve la modalidad */
r = await llamada(d1, 'GET', BASE + '/invita?pid=9988776655443322');
check(r.body.ok && r.body.invitas.length === 1 &&
      r.body.invitas[0].mj === 'duelos' &&
      r.body.invitas[0].code === 'ABC12',
  'buzón del invitado: la invitación viaja con mj=duelos');

/* 7 · consumir el buzón (aceptar) */
r = await llamada(d1, 'DELETE', BASE + '/invita?pid=9988776655443322');
check(r.body.ok && r.body.borrados === 1, 'DELETE del buzón lo vacía');
r = await llamada(d1, 'GET', BASE + '/invita?pid=9988776655443322');
check(r.body.invitas.length === 0, 'buzón vacío tras aceptar');

/* 8 · IDEMPOTENCIA REAL: segunda «migración» con ALTERs duplicados —
 *    D1 lanza "duplicate column" y el worker DEBE seguir sirviendo */
r = await llamada(d1, 'POST', BASE + '/presencia', JSON.stringify({
  pid: 'aabbccddeeff1122', n: 'Ana', v: '3.6.165', st: 'sala',
  code: 'ABC12', mj: 'duelos', vis: 'pub' }));
check(r.status === 200 && r.body.ok,
  'segunda pasada con ALTERs duplicados: el worker sigue vivo (try/catch)');
check(d1._estado.columnas.presencia.filter((c) => c === 'mj').length === 1,
  'la columna mj NO se duplica en la migración');

/* 9 · bye: la baja borra la fila */
r = await llamada(d1, 'POST', BASE + '/presencia', JSON.stringify({
  pid: '1122334455667788', bye: 1 }));
check(r.body.ok, 'bye del latido');
r = await llamada(d1, 'GET', BASE + '/presencia?lista=1');
check((r.body.jugadores || []).length === 2, 'la fila de Bea desapareció del pulso');

/* 10 · saneo: mj/vis fuera de catálogo → caen al seguro */
await llamada(d1, 'POST', BASE + '/presencia', JSON.stringify({
  pid: '5544332211aabbcc', n: 'Dana', st: 'sala', code: 'QQ777',
  mj: 'hacker', vis: 'todos' }));
r = await llamada(d1, 'GET', BASE + '/presencia?lista=1');
const dana = (r.body.jugadores || []).find((j) => j.n === 'Dana');
check(dana && dana.mj === 'normal' && dana.vis === 'pri',
  'valores raros de mj/vis caen a normal/pri (saneo del worker)');

console.log('\nRESULTADO: ' + pasan + ' OK · ' + fallos + ' fallos');
process.exit(fallos ? 1 : 0);
