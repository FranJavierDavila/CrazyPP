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

  // O · ALARMAS DE TELEMETRÍA (ronda 18 · roadmap MEJORAS.md M2b):
  // fps_bajo · errores_js · vr_cortas — el resumen interpreta los agregados;
  // sin datos suficientes → verde y sin items. dur en segundos (c00).
  const al = (jj) => jj.alarmas;

  // O1 · perfil malo: fps rojo (media 54,3) + vr cortas rojo (2/3) + errores amarillo (4/3)
  await worker.fetch(
    req("/", {
      method: "POST",
      body: JSON.stringify([
        ev("boot", { sid: "r18-a" }),
        ev("vr_start", { sid: "r18-a" }), ev("vr_end", { dur: 45, fps: 50, sid: "r18-a" }),
        ev("error", { m: "boom_a", sid: "r18-a" }), ev("error", { m: "boom_a", sid: "r18-a" }),
        ev("boot", { sid: "r18-b" }),
        ev("vr_start", { sid: "r18-b" }), ev("vr_end", { dur: 50, fps: 55, sid: "r18-b" }),
        ev("error", { m: "boom_b", sid: "r18-b" }), ev("error", { m: "boom_b", sid: "r18-b" }),
        ev("boot", { sid: "r18-c" }),
        ev("vr_start", { sid: "r18-c" }), ev("vr_end", { dur: 300, fps: 58, sid: "r18-c" }),
      ]),
      headers: { "content-type": "text/plain" },
    }),
    env,
    {}
  );
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(al(j) && al(j).nivel === "rojo", `O1 · nivel global rojo (${al(j)?.nivel})`);
  const aFps = al(j).items.find((x) => x.id === "fps_bajo");
  const aErr = al(j).items.find((x) => x.id === "errores_js");
  const aCortas = al(j).items.find((x) => x.id === "vr_cortas");
  chk(aFps && aFps.nivel === "rojo" && aFps.datos.medio === 54.3 && aFps.datos.muestras === 3,
    `O1 · fps_bajo ROJO con medio 54,3 y 3 muestras (${JSON.stringify(aFps)})`);
  chk(aErr && aErr.nivel === "amarillo" && aErr.datos.errores === 4 && aErr.datos.sesiones === 3,
    `O1 · errores_js AMARILLO 4 errores / 3 sesiones (${JSON.stringify(aErr)})`);
  chk(aCortas && aCortas.nivel === "rojo" && aCortas.datos.cortas === 2 && aCortas.datos.cerradas === 3 && aCortas.datos.pct === 67,
    `O1 · vr_cortas ROJO 2/3 = 67% (${JSON.stringify(aCortas)})`);
  await worker.fetch(req("/", { method: "DELETE", headers: { "x-clave": "qa-clave-r8" } }), env, {});

  // O2 · perfil sano: 3 sesiones VR largas y fluidas, 0 errores → verde sin items
  await worker.fetch(
    req("/", {
      method: "POST",
      body: JSON.stringify([
        ev("boot", { sid: "r18-d" }), ev("vr_start", { sid: "r18-d" }), ev("vr_end", { dur: 600, fps: 88, sid: "r18-d" }),
        ev("boot", { sid: "r18-e" }), ev("vr_start", { sid: "r18-e" }), ev("vr_end", { dur: 900, fps: 85, sid: "r18-e" }),
        ev("boot", { sid: "r18-f" }), ev("vr_start", { sid: "r18-f" }), ev("vr_end", { dur: 120, fps: 90, sid: "r18-f" }),
      ]),
      headers: { "content-type": "text/plain" },
    }),
    env,
    {}
  );
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(al(j) && al(j).nivel === "verde" && al(j).items.length === 0,
    `O2 · perfil sano → VERDE sin items (${JSON.stringify(al(j))})`);
  await worker.fetch(req("/", { method: "DELETE", headers: { "x-clave": "qa-clave-r8" } }), env, {});

  // O3 · fronteras: fps amarillo (68 ≥ 60 y < 72) + errores rojo (3 por sesión)
  await worker.fetch(
    req("/", {
      method: "POST",
      body: JSON.stringify([
        ev("boot", { sid: "r18-g" }), ev("vr_start", { sid: "r18-g" }), ev("vr_end", { dur: 200, fps: 68, sid: "r18-g" }),
        ev("error", { m: "x1", sid: "r18-g" }), ev("error", { m: "x1", sid: "r18-g" }), ev("error", { m: "x2", sid: "r18-g" }),
        ev("boot", { sid: "r18-h" }), ev("vr_start", { sid: "r18-h" }), ev("vr_end", { dur: 300, fps: 70, sid: "r18-h" }),
        ev("error", { m: "x1", sid: "r18-h" }), ev("error", { m: "x2", sid: "r18-h" }), ev("error", { m: "x3", sid: "r18-h" }),
        ev("boot", { sid: "r18-i" }), ev("vr_start", { sid: "r18-i" }), ev("vr_end", { dur: 400, fps: 66, sid: "r18-i" }),
        ev("error", { m: "x1", sid: "r18-i" }), ev("error", { m: "x2", sid: "r18-i" }), ev("error", { m: "x3", sid: "r18-i" }),
        // top inequívoco: x1=4 > x2=3 > x3=2 · total 9 errores / 3 sesiones = media 3
      ]),
      headers: { "content-type": "text/plain" },
    }),
    env,
    {}
  );
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  const aF2 = al(j).items.find((x) => x.id === "fps_bajo");
  const aE2 = al(j).items.find((x) => x.id === "errores_js");
  chk(aF2 && aF2.nivel === "amarillo" && aF2.datos.medio === 68,
    `O3 · fps_bajo AMARILLO con medio 68 (frontera <72) (${JSON.stringify(aF2)})`);
  chk(aE2 && aE2.nivel === "rojo" && aE2.datos.media === 3 && aE2.datos.top === "x1",
    `O3 · errores_js ROJO con 3 por sesión y top incluido (${JSON.stringify(aE2)})`);
  chk(!al(j).items.some((x) => x.id === "vr_cortas"),
    "O3 · vr_cortas NO dispara con las 3 sesiones largas");
  chk(al(j).nivel === "rojo", `O3 · nivel global = el PEOR de los items (${al(j).nivel})`);
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8&sid=r18-g"), env, {}));
  const aE3 = al(j).items.find((x) => x.id === "errores_js");
  chk(aE3 && aE3.datos.errores === 3 && aE3.datos.sesiones === 1,
    `O3 · alarmas respetan el filtro ?sid (${JSON.stringify(aE3?.datos)})`);
  await worker.fetch(req("/", { method: "DELETE", headers: { "x-clave": "qa-clave-r8" } }), env, {});

  // O4 · almacén vacío → verde (nada que alarmar)
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(al(j) && al(j).nivel === "verde" && al(j).items.length === 0,
    "O4 · almacén vacío → VERDE (nada que alarmar)");

  // O5 · sin_sonido (roadmap MEJORAS.md M5 · alertas de telemetría):
  //     señales de audio roto = errores con marcador audio/sonido/decode/sfx
  //     + eventos golpe_sin_sonido. Los errores SIN marcador NO cuentan.
  await worker.fetch(
    req("/", {
      method: "POST",
      body: JSON.stringify([
        ev("boot", { sid: "m5b-a" }),
        ev("error", { m: "decodeAudioData falló", sid: "m5b-a" }),
        ev("error", { m: "boom_a sin marcador", sid: "m5b-a" }), // fuera
        ev("boot", { sid: "m5b-b" }),
        ev("golpe_sin_sonido", { sid: "m5b-b" }),
        ev("boot", { sid: "m5b-c" }),
        ev("error", { m: "AudioContext suspendido", sid: "m5b-c" }),
      ]),
      headers: { "content-type": "text/plain" },
    }),
    env,
    {}
  );
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  const aSon = al(j).items.find((x) => x.id === "sin_sonido");
  chk(aSon && aSon.nivel === "amarillo" && aSon.datos.senales === 3 && aSon.datos.sesiones === 3,
    `O5 · sin_sonido AMARILLO 3 señales / 3 sesiones (${JSON.stringify(aSon)})`);
  const aErr5 = al(j).items.find((x) => x.id === "errores_js");
  chk(aErr5 && aErr5.datos.errores === 3 && aErr5.datos.sesiones === 3,
    `O5 · errores_js sigue contando TODOS los errores (3: 2 audio + 1 sin marcador, sin filtrar) (${JSON.stringify(aErr5?.datos)})`);
  chk(al(j).items.find((x) => x.id === "fps_bajo") === undefined &&
      al(j).items.find((x) => x.id === "vr_cortas") === undefined,
    "O5 · fps_bajo y vr_cortas NO se ven afectados por el bloque M5b");

  // O5b · rojo: 6 señales más en m5b-a → 9 señales / 3 sesiones = media 3
  await worker.fetch(
    req("/", {
      method: "POST",
      body: JSON.stringify([1, 2, 3, 4, 5, 6].map((i) =>
        ev("error", { m: "sfx crear fallo " + i, sid: "m5b-a" })
      )),
      headers: { "content-type": "text/plain" },
    }),
    env,
    {}
  );
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  const aSonR = al(j).items.find((x) => x.id === "sin_sonido");
  chk(aSonR && aSonR.nivel === "rojo" && aSonR.datos.senales === 9 && aSonR.datos.media === 3,
    `O5b · sin_sonido ROJO 9 señales / 3 sesiones = media 3 (${JSON.stringify(aSonR)})`);
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8&sid=m5b-c"), env, {}));
  chk(al(j).items.find((x) => x.id === "sin_sonido")?.datos.senales === 1,
    "O5b · sin_sonido respeta el filtro ?sid (m5b-c: 1 señal)");
  await worker.fetch(req("/", { method: "DELETE", headers: { "x-clave": "qa-clave-r8" } }), env, {});
  j = await cuerpo(await worker.fetch(req("/?resumen=1&clave=qa-clave-r8"), env, {}));
  chk(al(j).nivel === "verde" && al(j).items.length === 0,
    "O5c · tras la purga el almacén vuelve a VERDE sin items");

  // ================================================================
  // P4 · ronda 19 — /api/ice (TURN efímero de Cloudflare Realtime)
  // OJO: req() cuelga de BASE (…/api/tele) — aquí usamos reqIce con base
  // limpia, y UNA sola D1 para toda la fase (los flags de init del módulo
  // son por isolate: el primer socialInit crea las tablas en esa DB).
  // ================================================================
  const _fetchReal = globalThis.fetch;
  const reqIce = (path, opts = {}) => new Request("https://worker.test" + path, opts);
  const DBICE = new D1Sim();
  try {
    // P1 · sin token → STUN honesto, turn:false (degradación limpia)
    const envIce = { DB: DBICE, CLAVE: "qa-clave-r8", ICE_TTL_MS: 0 };
    r = await worker.fetch(reqIce("/api/ice"), envIce, {});
    j = await cuerpo(r);
    chk(r.status === 200 && j.ok === true && j.turn === false,
      `P1 · /api/ice sin token → turn:false (${r.status})`);
    chk(Array.isArray(j.iceServers) && j.iceServers.length === 1 &&
        j.iceServers[0].urls.every((u) => u.startsWith("stun:")),
      `P1 · sin token: sólo STUN (${JSON.stringify(j.iceServers)})`);

    // P2 · POST → 405
    r = await worker.fetch(reqIce("/api/ice", { method: "POST", body: "{}" }), envIce, {});
    chk(r.status === 405, `P2 · POST /api/ice → 405 (${r.status})`);

    // P3 · token+key → TURN de Cloudflare saneado (sin :53, con credencial)
    const RESP_RTC = {
      iceServers: [
        { urls: ["stun:stun.cloudflare.com:3478"] },
        { urls: ["turn:turn.cloudflare.com:3478?transport=udp", "turn:turn.cloudflare.com:53?transport=udp"],
          username: "u123", credential: "c456" },
        { urls: ["turn:turn.cloudflare.com:80?transport=tcp"], username: "", credential: "" },
        { urls: ["nota:mal"] },
        { urls: ["turns:turn.cloudflare.com:5349?transport=tcp"], username: "u123", credential: "c456" },
      ],
    };
    let llamadasRtc = 0;
    globalThis.fetch = async (url) => {
      const s = String(url);
      if (s.includes("/credentials/generate-ice-servers")) {
        llamadasRtc++;
        return { status: 201, json: async () => RESP_RTC };
      }
      return { status: 400, json: async () => ({ success: false, errors: [], result: null }) };
    };
    const envIce2 = { DB: DBICE, CLAVE: "qa-clave-r8", ICE_TTL_MS: 0,
      TURN_API_TOKEN: "qa-token", TURN_KEY_ID: "qa-key" };
    r = await worker.fetch(reqIce("/api/ice"), envIce2, {});
    j = await cuerpo(r);
    chk(r.status === 200 && j.turn === true && j.ttl === 21600,
      `P3 · token+key → turn:true ttl 6 h (${j.turn})`);
    const turnServs = j.iceServers.filter((s) => s.urls.some((u) => u.startsWith("turn")));
    chk(j.iceServers.length === 3 && turnServs.length === 2,
      `P3 · saneo: 3 servidores (stun + 2 turn con credencial) (${JSON.stringify(j.iceServers)})`);
    chk(j.iceServers.every((s) => s.urls.every((u) => !/:53(\?|$)/.test(u))),
      "P3 · el puerto 53 NO sale en las urls (sin confundirlo con :5349)");
    chk(turnServs.every((s) => s.username && s.credential),
      "P3 · TURN siempre con username/credential");

    // P4 · caché por isolate: dos llamadas seguidas sin upstream y misma ts
    const envIce3 = { DB: DBICE, CLAVE: "qa-clave-r8", ICE_TTL_MS: 600000,
      TURN_API_TOKEN: "qa-token", TURN_KEY_ID: "qa-key" };
    const j1 = await cuerpo(await worker.fetch(reqIce("/api/ice"), envIce3, {}));
    const antes = llamadasRtc;
    const j2 = await cuerpo(await worker.fetch(reqIce("/api/ice"), envIce3, {}));
    chk(llamadasRtc === antes && j1.ts === j2.ts && j1.turn === true,
      `P4 · caché: 2ª llamada sin upstream y misma ts (${llamadasRtc - antes} llamadas)`);

    // P5 · auto-provisión de la TURN key (token sin TURN_KEY_ID) + persistencia en cfg
    globalThis.fetch = async (url) => {
      const s = String(url);
      if (s.includes("/accounts?per_page=1")) {
        return { status: 200, json: async () => ({ success: true, result: [{ id: "a".repeat(32) }] }) };
      }
      if (s.includes("/calls/turn_keys")) {
        return { status: 200, json: async () => ({ success: true, result: { key_id: "k9" } }) };
      }
      if (s.includes("/credentials/generate-ice-servers")) {
        llamadasRtc++;
        return { status: 201, json: async () => ({
          iceServers: [{ urls: ["turn:turn.cloudflare.com:3478?transport=udp"], username: "u", credential: "c" }] }) };
      }
      return { status: 400, json: async () => ({ success: false }) };
    };
    const envIce4 = { DB: DBICE, CLAVE: "qa-clave-r8", ICE_TTL_MS: 0, TURN_API_TOKEN: "qa-token" };
    r = await worker.fetch(reqIce("/api/ice"), envIce4, {});
    j = await cuerpo(r);
    chk(j.turn === true, `P5 · auto-provisión de key → turn:true (${j.turn})`);
    const filaKey = await envIce4.DB.prepare("SELECT v FROM cfg WHERE k = 'turn_key_id'").first();
    chk(filaKey && filaKey.v === "k9", `P5 · key persistida en cfg (${filaKey && filaKey.v})`);

    // P6 · upstream caído → STUN honesto con error:'turn_upstream'
    globalThis.fetch = async () => ({ status: 500, json: async () => ({}) });
    const envIce5 = { DB: DBICE, CLAVE: "qa-clave-r8", ICE_TTL_MS: 0,
      TURN_API_TOKEN: "qa-token", TURN_KEY_ID: "qa-key" };
    r = await worker.fetch(reqIce("/api/ice"), envIce5, {});
    j = await cuerpo(r);
    chk(r.status === 200 && j.turn === false && j.error === "turn_upstream" &&
        j.iceServers.every((s) => s.urls.some((u) => u.startsWith("stun:"))),
      `P6 · rtc.live caído → STUN honesto (${j.error})`);

    // P7 · CORS
    r = await worker.fetch(reqIce("/api/ice"), envIce5, {});
    chk(r.headers.get("access-control-allow-origin") === "*", "P7 · /api/ice lleva CORS");

    // P8 · ruta Metered (ronda 20 · P4-F4): cuenta gratuita del dueño,
    // credenciales dinámicas por API REST — mismo saneo que Cloudflare
    globalThis.fetch = async (url) => {
      const s = String(url);
      if (s.includes("metered.live/api/v1/turn/credentials")) {
        return { status: 200, json: async () => [
          { urls: ["stun:global.metered.ca:80"] },
          { urls: ["turn:global.metered.ca:80?transport=udp"], username: "mu", credential: "mc" },
          { urls: ["turn:global.metered.ca:53?transport=udp"], username: "mu", credential: "mc" },
          { urls: ["turn:global.metered.ca:443?transport=tcp"], username: "", credential: "" },
          { urls: ["turns:global.metered.ca:443?transport=tcp"], username: "mu", credential: "mc" },
        ] };
      }
      return { status: 500, json: async () => ({}) };
    };
    const envM = { DB: DBICE, CLAVE: "qa-clave-r8", ICE_TTL_MS: 0,
      METERED_APP: "crazypp", METERED_API_KEY: "qa-key-m" };
    r = await worker.fetch(reqIce("/api/ice"), envM, {});
    j = await cuerpo(r);
    chk(r.status === 200 && j.turn === true && j.fuente === "metered" && j.ttl === 21600,
      `P8 · Metered configurada → turn:true fuente=metered (${j.turn}/${j.fuente})`);
    const mTurn = j.iceServers.filter((s) => s.urls.some((u) => u.startsWith("turn")));
    chk(mTurn.length === 2 && mTurn.every((s) => s.username && s.credential),
      `P8 · saneo: 2 turn con credencial (:53 y sin credencial fuera) (${mTurn.length})`);
    chk(j.iceServers.some((s) => s.urls.some((u) => u.startsWith("stun:stun.cloudflare.com"))),
      "P8 · la fusión mantiene el STUN base");

    // P9 · Metered rota → degradación limpia a STUN honesto
    globalThis.fetch = async () => ({ status: 500, json: async () => ({}) });
    const envM2 = { DB: DBICE, CLAVE: "qa-clave-r8", ICE_TTL_MS: 0,
      METERED_APP: "crazypp", METERED_API_KEY: "qa-key-m" };
    r = await worker.fetch(reqIce("/api/ice"), envM2, {});
    j = await cuerpo(r);
    chk(r.status === 200 && j.turn === false && j.error === "metered_upstream" &&
        j.iceServers.every((s) => s.urls.some((u) => u.startsWith("stun:"))),
      `P9 · metered caída → STUN honesto con error (${j.error})`);

    // P10 · prioridad: si hay TURN_API_TOKEN, NO se llama a metered
    let llamadasMetered = 0;
    globalThis.fetch = async (url) => {
      const s = String(url);
      if (s.includes("metered.live")) { llamadasMetered++; return { status: 200, json: async () => [] }; }
      if (s.includes("/credentials/generate-ice-servers")) {
        return { status: 201, json: async () => ({
          iceServers: [{ urls: ["turn:turn.cloudflare.com:3478?transport=udp"], username: "u", credential: "c" }] }) };
      }
      return { status: 400, json: async () => ({ success: false }) };
    };
    const envAmbos = { DB: DBICE, CLAVE: "qa-clave-r8", ICE_TTL_MS: 0,
      TURN_API_TOKEN: "qa-token", TURN_KEY_ID: "qa-key",
      METERED_APP: "crazypp", METERED_API_KEY: "qa-key-m" };
    r = await worker.fetch(reqIce("/api/ice"), envAmbos, {});
    j = await cuerpo(r);
    chk(j.turn === true && j.fuente === "cloudflare" && llamadasMetered === 0,
      `P10 · CF tiene prioridad sobre Metered (${llamadasMetered} llamadas a metered)`);

    // P11 · Metered sin servidores turn válidos → STUN honesto
    globalThis.fetch = async () => ({ status: 200, json: async () => [{ urls: ["stun:global.metered.ca:80"] }] });
    const envM3 = { DB: DBICE, CLAVE: "qa-clave-r8", ICE_TTL_MS: 0,
      METERED_APP: "crazypp", METERED_API_KEY: "qa-key-m" };
    r = await worker.fetch(reqIce("/api/ice"), envM3, {});
    j = await cuerpo(r);
    chk(r.status === 200 && j.turn === false && j.error === "metered_upstream",
      `P11 · metered sin turn válido → STUN honesto (${j.error})`);
  } finally {
    globalThis.fetch = _fetchReal;
  }

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
