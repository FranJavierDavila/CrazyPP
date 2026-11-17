#!/usr/bin/env node
/**
 * CRAZY PING PONG · r45 · E2E LOCAL del endpoint RANK (?rank=1) del worker
 * de telemetría — el worker.js REAL (mismo patrón que test_local.mjs) contra
 * el simulador de D1 sobre node:sqlite. Cero red, cero nube, cero wrangler.
 *
 * Escenario:
 *   1 · dos jugadores firman perfil/resultado/logro (pids distintos, dos
 *       perfiles cada uno — el MÁS FRESCO manda) + un evento SIN pid (build
 *       viejo) que NO debe entrar al ranking.
 *   2 · GET ?rank=1 sin clave → 403.
 *   3 · GET ?rank=1 con clave → 4 tablas top-20 con los valores esperados.
 *   4 · el latido público (?rank sin más... el latido puro) sigue vivo.
 * Salida estilo casa: RESULTADO: N OK · M FALLOS
 */
import { DatabaseSync } from "node:sqlite";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const FUENTE = readFileSync(join(AQUI, "worker.js"), "utf8");
const modulo = await import(
  "data:text/javascript;base64," + Buffer.from(FUENTE).toString("base64")
);
const worker = modulo.default;

class D1Sim {
  constructor() { this.db = new DatabaseSync(":memory:"); }
  _mk(sql, args) {
    const norm = args.map((a) => (a === undefined ? null : a));
    return {
      first: async () => this.db.prepare(sql).get(...norm) ?? null,
      all: async () => ({ results: this.db.prepare(sql).all(...norm) }),
      run: async () => {
        const r = this.db.prepare(sql).run(...norm);
        return { success: true, meta: { changes: Number(r.changes), last_row_id: Number(r.lastInsertRowid) } };
      },
    };
  }
  prepare(sql) { return { ...this._mk(sql, []), bind: (...args) => this._mk(sql, args) }; }
  async batch(stmts) { for (const s of stmts) await s.run(); }
}

const env = { DB: new D1Sim(), CLAVE: "qa-rank-45" };
const req = (path, init) => new Request("https://w.test" + path, init);
const j = (r) => r.json();

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? "  ✓ " : "  ✗ FALLO: ") + label);
  if (cond) ok++; else fails++;
};

/* — 1 · carga: dos jugadores + un build viejo sin pid ———————— */
const AHORA = Date.now();
const ev = (e, pid, n, extra, haceMs) => ({
  e, t: AHORA - (haceMs || 0), v: "3.6.139-SDK6", sid: "sid-" + (pid || "viejo"),
  ...(pid ? { pid, n } : {}), ...extra,
});
const lote = [
  // jugador A — perfil VIEJO (hace 2 h) y perfil FRESCO (ahora): manda el fresco
  ev("perfil", "aaaaaaaaaaaaaaaa", "Ana", { el: 1200, w: 5, bs: 3, st: 4, pt: 700, ach: 2 }, 7200000),
  ev("perfil", "aaaaaaaaaaaaaaaa", "Ana", { el: 1250, w: 6, bs: 4, st: 6, pt: 900, ach: 3 }, 0),
  ev("resultado", "aaaaaaaaaaaaaaaa", "Ana", { m: "p2p", a: 11, b: 7, w: 1, bo: 1 }, 60000),
  ev("resultado", "aaaaaaaaaaaaaaaa", "Ana", { m: "ia", a: 11, b: 3, w: 1, bo: 3 }, 30000),
  ev("logro", "aaaaaaaaaaaaaaaa", "Ana", { k: "aces10" }, 20000),
  // jugador B — perfil único, ELO más alto, pero sin victorias online
  ev("perfil", "bbbbbbbbbbbbbbbb", "Beto", { el: 1310, w: 2, bs: 9, st: 2, pt: 2400, ach: 5 }, 5000),
  ev("resultado", "bbbbbbbbbbbbbbbb", "Beto", { m: "ia", a: 4, b: 11, w: 0, bo: 3 }, 4000),
  // build viejo SIN pid: fuera del ranking
  ev("perfil", null, null, { el: 9999, w: 99, pt: 99999, ach: 99 }, 1000),
];
const rPost = await worker.fetch(req("/api/tele", {
  method: "POST", body: JSON.stringify(lote),
  headers: { "content-type": "text/plain" },
}), env, { waitUntil: async () => {} });
chk(rPost.status === 204, "POST del lote mixto → 204 (" + rPost.status + ")");

/* — 2 · el rank sin clave → 403 ————————————————————————————— */
const rNo = await worker.fetch(req("/api/tele?rank=1"), env, { waitUntil: async () => {} });
chk(rNo.status === 403, "GET ?rank=1 SIN clave → 403 (" + rNo.status + ")");

/* — 3 · el latido público sigue vivo (rank no lo devora) ———— */
const rLat = await worker.fetch(req("/api/tele"), env, { waitUntil: async () => {} });
const dLat = await j(rLat);
chk(dLat.ok === true && dLat.total === 8, "latido público vivo (total 8: " + dLat.total + ")");

/* — 4 · el rank con clave → 4 tablas correctas ———————————————— */
const rOk = await worker.fetch(req("/api/tele?rank=1&clave=" + env.CLAVE), env, { waitUntil: async () => {} });
const d = await j(rOk);
chk(d.ok === true && d.rank, "GET ?rank=1 con clave → ok con rank");
chk(d.rank.jugadores === 2, "2 jugadores identificados (los builds sin pid fuera): " + d.rank.jugadores);
const ana = d.rank.elo.find((x) => x.n === "Ana");
const beto = d.rank.elo.find((x) => x.n === "Beto");
chk(!!ana && !!beto, "Ana y Beto presentes en la tabla de ELO");
chk(ana && ana.el === 1250, "Ana con su perfil MÁS FRESCO (ELO 1250, no 1200): " + (ana && ana.el));
chk(d.rank.elo[0].n === "Beto", "Beto primero por ELO (1310 > 1250)");
chk(ana && ana.w === 6 && ana.pt === 900 && ana.st === 6 && ana.bs === 4,
  "Ana: w6 pt900 st6 bs4 (el perfil fresco manda entero)");
chk(ana && ana.vics === 2 && ana.part === 2 && ana.p2p === 1,
  "Ana: 2 resultados (2 victorias, 1 online)");
chk(ana && ana.ach === 3, "Ana: 3 logros (perfil) — el logro_evento coincide");
chk(d.rank.vics[0].n === "Ana", "Ana primera en VICTORIAS (6 > 2)");
chk(d.rank.pts[0].n === "Beto", "Beto primero en PUNTOS (2400 > 900)");
chk(d.rank.logros[0].n === "Beto", "Beto primero en LOGROS (5 > 3)");
chk(ana && typeof ana.hace === "number", "frescura (hace) presente");
chk(d.rank.elo.length <= 20 && d.rank.vics.length <= 20, "top-20 acotado");

console.log(`\nRESULTADO: ${ok} OK · ${fails} FALLOS (test_rank_r45 · worker ?rank=1)`);
process.exit(fails ? 1 : 0);
