#!/usr/bin/env node
/**
 * CRAZY PING PONG · E2E LOCAL del worker de telemetría (ronda 8).
 * Ejecuta el worker.js REAL (import dinámico por data: URL para ESM) contra
 * un simulador de D1 construido sobre node:sqlite (estable en Node ≥22.5;
 * este sandbox tiene Node 24). Cero red, cero nube, cero wrangler:
 * el mismo código que irá a producción, las mismas SQL, el mismo contrato.
 *
 * Salida estilo casa: '  ✓ …' / '  ✗ FALLO: …' + RESULTADO: N OK · M FALLOS
 */
import { DatabaseSync } from "node:sqlite";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const FUENTE = readFileSync(join(AQUI, "worker.js"), "utf8");

/** Importa el módulo ESM del worker sin tocar el sistema de ficheros. */
const modulo = await import(
  "data:text/javascript;base64," + Buffer.from(FUENTE).toString("base64")
);
const worker = modulo.default;

/** Simulador del binding D1 sobre node:sqlite (API: prepare/bind/first/all/run/batch).
 *  OJO: node:sqlite compila la SQL al PREPARAR, D1 real al EJECUTAR → el shim
 *  es PEREZOSO (compila en run/first/all) o los CREATE INDEX del esquema
 *  explotarían por prepararlos antes que el CREATE TABLE. */
class D1Sim {
  constructor() {
    this.db = new DatabaseSync(":memory:");
  }
  _mk(sql, args) {
    const norm = args.map((a) => (a === undefined ? null : a));
    return {
      first: async () => this.db.prepare(sql).get(...norm) ?? null,
      all: async () => ({ results: this.db.prepare(sql).all(...norm) }),
      run: async () => {
        const r = this.db.prepare(sql).run(...norm);
        return {
          success: true,
          meta: { changes: Number(r.changes), last_row_id: Number(r.lastInsertRowid) },
        };
      },
    };
  }
  prepare(sql) {
    return { ...this._mk(sql, []), bind: (...args) => this._mk(sql, args) };
  }
  async batch(stmts) {
    const out = [];
    this.db.exec("BEGIN");
    try {
      for (const s of stmts) out.push(await s.run());
      this.db.exec("COMMIT");
    } catch (e) {
      this.db.exec("ROLLBACK");
      throw e;
    }
    return out;
  }
}

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? "  ✓ " : "  ✗ FALLO: ") + label);
  ok += cond ? 1 : 0;
  fails += cond ? 0 : 1;
};

const env = { DB: new D1Sim(), CLAVE: "qa-clave-r8" };
const BASE = "https://worker.test/api/tele";
const req = (path, opts = {}) => new Request(BASE + path, opts);
const cuerpo = (r) => r.text().then((t) => (t.startsWith("{") || t.startsWith("[") ? JSON.parse(t) : t));

const ev = (e, extra = {}) => ({ e, t: Date.now(), v: "qa", sid: "s-r8", ...extra });

try {
  // A · latido vacío
  let r = await worker.fetch(req("/"), env, {});
  chk(r.status === 200 && (await cuerpo(r)).total === 0, "latido público en almacén vacío");

  // B · POST array directo (contrato del juego) → 204 sin cuerpo
  const lote = [
    ev("boot", { platform: "2d" }),
    ev("qa_e", { n: 1 }),
    ev("qa_e", { n: 2 }),
    ev("vr_end", { dur: 61, fps: 60 }),
    ev("error", { m: "qa_error_r8" }),
    { e: "champ_rank", champ: "magia", win: true, score: 123, stars: 2, bricks: 10, ext: 0, left: 12.5, v: "2.81.0", sid: "s-r8", t: Date.now() },
  ];
  r = await worker.fetch(
    req("/", { method: "POST", body: JSON.stringify(lote), headers: { "content-type": "text/plain" } }), env, {}
  );
  chk(r.status === 204, `POST array directo → 204 sin cuerpo (${r.status})`);

  // C · tolerancia wrapper {app,events} (contrato antiguo)
  r = await worker.fetch(
    req("/", { method: "POST", body: JSON.stringify({ app: "crazy-pingpong", events: [ev("qa_e", { n: 3 })] }), headers: { "content-type": "text/plain" } }), env, {}
  );
  chk(r.status === 204, "POST wrapper {app,events} tolerado → 204");

  // D · saneo: basura 400 · sin «e» descartado · evento grande descartado · 413
  r = await worker.fetch(req("/", { method: "POST", body: "esto no es json" }), env, {});
  chk(r.status === 400, `POST basura → 400 (${r.status})`);
  await worker.fetch(
    req("/", { method: "POST", body: JSON.stringify([{ t: 1 }, ev("qa_sin_e")]), headers: { "content-type": "text/plain" } }), env, {}
  );
  let j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(j.porEvento["qa_sin_e"] === 1 && j.total === 8,
    `saneo selectivo: {t:1} descartado, qa_sin_e guardado, el lote sobrevive (total ${j.total})`);
  r = await worker.fetch(
    req("/", { method: "POST", body: JSON.stringify([{ e: "qa_grande", m: "x".repeat(2100) }]) }), env, {}
  );
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(r.status === 204 && j.total === 8, `evento >2000 B descartado del lote (${r.status}, total sigue ${j.total})`);
  r = await worker.fetch(req("/", { method: "POST", body: "x".repeat(256 * 1024 + 1) }), env, {});
  chk(r.status === 413, `cuerpo >256 KB → 413 (${r.status})`);

  // E · privacidad de lectura: sin clave → 403; clave mala → 403
  r = await worker.fetch(req("/?resumen=1"), env, {});
  chk(r.status === 403, `resumen sin clave → 403 (${r.status})`);
  r = await worker.fetch(req("/?resumen=1&clave=otra"), env, {});
  chk(r.status === 403, `resumen con clave equivocada → 403 (${r.status})`);
  r = await worker.fetch(req("/?eventos=2"), env, {});
  chk(r.status === 403, `eventos sin clave → 403 (${r.status})`);
  r = await worker.fetch(req("/?sid=s-r8", { method: "DELETE" }), env, {});
  chk(r.status === 403, `DELETE sin clave → 403 (${r.status})`);

  // F · resumen completo con clave (agregados SQL)
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(j.ok === true && j.almacen === "d1:crazypp-tele", `resumen con clave ok (almacén ${j.almacen})`);
  chk(j.total === 8, `total agregado (${j.total})`);
  chk(j.porEvento["boot"] === 1 && j.porEvento["qa_e"] === 3 && j.porEvento["vr_end"] === 1,
    `porEvento SQL (${JSON.stringify(j.porEvento)})`);
  chk(j.sesionesUnicas === 1, `sesiones únicas (${j.sesionesUnicas})`);
  chk(j.arranques24h === 1, `arranques 24 h (${j.arranques24h})`);
  chk(j.fps.medio === 60 && j.fps.muestras === 1, `fps SQL medio/muestras (${j.fps.medio}/${j.fps.muestras})`);
  chk(Array.isArray(j.erroresTop) && j.erroresTop[0]?.[0] === "qa_error_r8" && j.erroresTop[0]?.[1] === 1,
    `erroresTop forma [m,n] (${JSON.stringify(j.erroresTop)})`);
  const magia = j.champRank["magia"];
  chk(magia && magia.partidas === 1 && magia.victorias === 1 && magia.mejor === 123 && magia.estrellas === 2,
    `champRank SQL partidas/victorias/mejor/estrellas (${JSON.stringify(magia)})`);
  chk(Array.isArray(j.sesiones) && j.sesiones[0]?.sid === "s-r8" && j.sesiones[0]?.n === 8,
    `sesiones con primero/ultimo/n (${JSON.stringify(j.sesiones[0])})`);
  chk(j.ultimos.length === 8 && j.ultimos[5]?.e === "champ_rank" && j.ultimos[7]?.e === "qa_sin_e",
    `últimos crudos en orden ascendente (${j.ultimos.length})`);

  // G · GET ?eventos=N con clave + filtro sid
  j = await cuerpo(await worker.fetch(req("/?eventos=2&clave=qa-clave-r8"), env, {}));
  chk(j.eventos.length === 2 && j.eventos[0].e === "qa_e",
    `?eventos=2 devuelve los 2 últimos (${j.eventos.length}: ${j.eventos.map((x) => x.e).join(",")})`);
  j = await cuerpo(await worker.fetch(req("/?eventos=9&clave=qa-clave-r8&sid=s-r8"), env, {}));
  chk(j.eventos.length === 8, `filtro ?sid en eventos (${j.eventos.length})`);

  // H · clave por cabecera X-Clave
  r = await worker.fetch(req("/?resumen=1", { headers: { "x-clave": "qa-clave-r8" } }), env, {});
  chk(r.status === 200, "lectura con clave por cabecera X-Clave");

  // L · ANÁLISIS (ronda 9): duraciones, vrDuracion, porDia, versiones
  const hoy = new Date().toISOString().slice(0, 10);
  await worker.fetch(
    req("/", {
      method: "POST",
      body: JSON.stringify([
        ev("page_close", { dur: 300 }),
        ev("page_close", { dur: 600, sid: "s-r9" }),
        ev("boot", { sid: "s-r9" }),
      ]),
      headers: { "content-type": "text/plain" },
    }),
    env,
    {}
  );
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(j.duraciones && j.duraciones.n === 2 && j.duraciones.media === 450 && j.duraciones.max === 600,
    `duraciones SQL media/max/n de page_close.dur (${JSON.stringify(j.duraciones)})`);
  chk(j.vrDuracion && j.vrDuracion.n === 1 && j.vrDuracion.media === 61 && j.vrDuracion.max === 61,
    `vrDuracion SQL de vr_end.dur (${JSON.stringify(j.vrDuracion)})`);
  chk(Array.isArray(j.porDia) && j.porDia[0]?.dia === hoy && j.porDia[0]?.eventos === 11 &&
      j.porDia[0]?.boots === 2 && j.porDia[0]?.sesiones === 2,
    `porDia SQL dia/eventos/boots/sesiones (${JSON.stringify(j.porDia[0])})`);
  chk(Array.isArray(j.versiones) && j.versiones[0]?.v === "qa" && j.versiones[0]?.eventos === 10 && j.versiones[0]?.sesiones === 2,
    `versiones SQL eventos/sesiones (${JSON.stringify(j.versiones[0])})`);
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8&sid=s-r9"), env, {}));
  chk(j.duraciones.n === 1 && j.duraciones.media === 600 && j.porDia[0]?.eventos === 2 && j.versiones[0]?.eventos === 2,
    `análisis con filtro ?sid (${j.duraciones.n}/${j.duraciones.media}/${j.porDia[0]?.eventos}/${j.versiones[0]?.eventos})`);

  // I · DELETE con clave (purga por sid, paridad con el receptor local)
  r = await worker.fetch(
    req("/?sid=s-r8", { method: "DELETE", headers: { "x-clave": "qa-clave-r8" } }), env, {}
  );
  j = await cuerpo(r);
  chk(j.borrados === 9, `DELETE ?sid purga su ámbito (${j.borrados})`);
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(j.total === 2, `tras la purga parcial quedan solo los de s-r9 (${j.total})`);
  r = await worker.fetch(req("/", { method: "DELETE", headers: { "x-clave": "qa-clave-r8" } }), env, {});
  j = await cuerpo(r);
  chk(j.borrados === 2, `purga total borra el resto (${j.borrados})`);
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(j.total === 0 && j.duraciones.n === 0 && j.porDia.length === 0,
    "tras la purga total el almacén queda a 0 (con análisis vacíos)");

  // M · EMBUDO POR CAMPEONATO (ronda 11): stage/champion llevan id desde 3.6.8
  await worker.fetch(
    req("/", {
      method: "POST",
      body: JSON.stringify([
        ev("stage", { n: 1, id: "magia", sid: "r11-a" }),
        ev("stage", { n: 2, id: "magia", sid: "r11-a" }),
        ev("champion", { id: "magia", sid: "r11-a" }),
        ev("stage", { n: 1, id: "locura", sid: "r11-a" }),
        ev("champion", { id: "locura", sid: "r11-b" }),
        ev("stage", { n: 3 }), // viejo SIN id → fuera del porCampeonato
      ]),
      headers: { "content-type": "text/plain" },
    }),
    env,
    {}
  );
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(j.porCampeonato?.magia?.stage === 2 && j.porCampeonato?.magia?.champion === 1,
    `porCampeonato agrega magia stage/champion (${JSON.stringify(j.porCampeonato?.magia)})`);
  chk(j.porCampeonato?.locura?.stage === 1 && j.porCampeonato?.locura?.champion === 1,
    `porCampeonato separa locura (${JSON.stringify(j.porCampeonato?.locura)})`);
  chk(j.porCampeonato?.qa === undefined,
    "stage/champion SIN id quedan fuera del porCampeonato (tolerante con datos viejos)");
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8&sid=r11-a"), env, {}));
  chk(j.porCampeonato?.magia?.stage === 2 && j.porCampeonato?.magia?.champion === 1 &&
      j.porCampeonato?.locura?.champion === undefined,
    "porCampeonato respeta el filtro ?sid (locura sin su champion de otro sid)");
  r = await worker.fetch(req("/", { method: "DELETE", headers: { "x-clave": "qa-clave-r8" } }), env, {});
  j = await cuerpo(r);
  chk(j.borrados === 6, `purga final del bloque r11 (${j.borrados})`);

  // N · SESIONES VR (ronda 14): ciclos vr_start → vr_ping* → vr_end por sid
  await worker.fetch(
    req("/", {
      method: "POST",
      body: JSON.stringify([
        ev("vr_end", { dur: 99, fps: 77, sid: "r14-h" }), // huérfano: sin vr_start → fuera
        ev("vr_start", { mode: "match", sid: "r14-a" }),
        ev("vr_ping", { dur: 300, fps: 70, sid: "r14-a" }),
        ev("vr_end", { dur: 540, fps: 65, fpsMin: 40, fpsMax: 80, sid: "r14-a" }),
        ev("vr_start", { mode: "match", sid: "r14-b" }),
        ev("vr_ping", { dur: 300, fps: 60, sid: "r14-b" }),
        ev("vr_ping", { dur: 600, fps: 55, sid: "r14-b" }), // muere sin vr_end
        ev("vr_start", { mode: "match", sid: "r14-c" }),    // abierta sin pings
      ]),
      headers: { "content-type": "text/plain" },
    }),
    env,
    {}
  );
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(Array.isArray(j.sesionesVR) && j.sesionesVR.length === 3,
    `sesionesVR lista 3 ciclos (${j.sesionesVR?.length})`);
  chk(!j.sesionesVR.some((x) => x.sid === "r14-h"),
    "vr_end huérfano (sin vr_start) queda fuera de sesionesVR");
  const sa = j.sesionesVR.find((x) => x.sid === "r14-a");
  chk(sa && sa.estado === "cerrada" && sa.durReal === true && sa.dur === 540 &&
      sa.fps === 65 && sa.fpsMin === 40 && sa.fpsMax === 80 && sa.pings === 1,
    `cerrada: dur/fps/fpsMin/fpsMax del vr_end (${JSON.stringify(sa)})`);
  chk(sa && Array.isArray(sa.curva) && sa.curva.length === 1 &&
      sa.curva[0].fps === 70 && sa.curva[0].m === 0,
    `curva del ping (${JSON.stringify(sa?.curva)})`);
  const sb = j.sesionesVR.find((x) => x.sid === "r14-b");
  chk(sb && sb.estado === "interrumpida" && sb.durReal === false &&
      sb.dur === 600 && sb.pings === 2 && sb.curva.length === 2,
    `interrumpida fechada por el ÚLTIMO ping (${JSON.stringify(sb)})`);
  const sc = j.sesionesVR.find((x) => x.sid === "r14-c");
  chk(sc && sc.estado === "abierta" && sc.dur === null && sc.pings === 0,
    `abierta sin pings (${JSON.stringify(sc)})`);
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8&sid=r14-a"), env, {}));
  chk(j.sesionesVR?.length === 1 && j.sesionesVR[0]?.sid === "r14-a",
    "sesionesVR respeta el filtro ?sid");
  r = await worker.fetch(req("/", { method: "DELETE", headers: { "x-clave": "qa-clave-r8" } }), env, {});
  j = await cuerpo(r);
  chk(j.borrados === 8, `purga final del bloque r14 (${j.borrados})`);

  // J · CORS en todas las respuestas
  r = await worker.fetch(req("/", { method: "OPTIONS" }), env, {});
  chk(r.status === 204 && r.headers.get("access-control-allow-origin") === "*",
    "OPTIONS → 204 + ACAO *");
  r = await worker.fetch(req("/", { method: "POST", body: "[]" }), env, {});
  chk(r.headers.get("access-control-allow-origin") === "*", "POST lleva CORS");

  // K · privacidad: el worker jamás toca IP ni UA
  chk(!/headers\.get\(\s*['"]user-agent/i.test(FUENTE), "el worker NO lee la cabecera user-agent");
  chk(!FUENTE.includes("request.headers.get('cf") && !FUENTE.includes('request.headers.get("cf'),
    "el worker NO lee cabeceras cf-* (IP/geo)");
} catch (e) {
  chk(false, "excepción del harness: " + (e?.stack || String(e)));
}

console.log(`RESULTADO: ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);
