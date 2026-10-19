/**
 * CRAZY PING PONG · WORKER DE TELEMETRÍA DE PRODUCCIÓN · ronda 8
 * Reemplaza al worker anterior (que aceptaba lotes pero no exponía lectura):
 * ahora los eventos caen en una base D1 (SQLite serverless) y se PUEDEN LEER.
 *
 * Contrato (hermano del receptor local /api/telemetria, ronda 6):
 *   POST   /api/tele            → lote → D1 · responde 204 SIN cuerpo
 *                                 (acepta ARRAY DIRECTO, el contrato del juego
 *                                 desde 3.6.5-SDK6, y el wrapper {app,events}
 *                                 antiguo por tolerancia)
 *   GET    /api/tele            → latido {ok, total, ts} (público, sin detalle)
 *   GET    /api/tele?resumen=1  → agregados completos (REQUIERE clave)
 *   GET    /api/tele?eventos=N  → últimos N crudos (REQUIERE clave)
 *   DELETE /api/tele?sid=…      → purga (REQUIERE clave; sin sid → total)
 *   OPTIONS                    → preflight CORS
 *
 * CLAVE (variable del worker, nombre exacto: CLAVE): protege resumen/eventos/
 * DELETE. Se pasa por ?clave=… o cabecera X-Clave. El POST NO lleva clave
 * (el juego no puede guardar secretos: es código público).
 *
 * PRIVACIDAD (misma política que el juego y el receptor local): se guarda
 * EXACTAMENTE el JSON del evento — NUNCA la IP, ni el user-agent, ni ninguna
 * cabecera. Tabla eventos con columnas extraídas (e, t, v, sid) para las
 * agregaciones SQL; el JSON completo vive en la columna `json`.
 *
 * Límites: cuerpo ≤ 256 KB (413) · evento ≤ 2000 B (descartado del lote sin
 * romperlo) · lote ≤ 500 eventos · evento sin `e` válida (1..40 chars) →
 * descartado. Esquema auto-inicializado (CREATE TABLE IF NOT EXISTS).
 *
 * Ronda 9 (visor analítico): el resumen añade sin romper nada —
 *   duraciones  {media,max,n} de page_close.dur (permanencia por sesión)
 *   vrDuracion  {media,max,n} de vr_end.dur (permanencia en VR real)
 *   porDia      [{dia,eventos,boots,sesiones}] últimos 30 días (DAU)
 *   versiones   [{v,eventos,sesiones}] (adopción por versión)
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "content-type, x-clave",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS, DELETE",
};

const MAX_BODY = 256 * 1024;
const MAX_EVENTO = 2000;
const MAX_LOTE = 500;

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS eventos (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     e TEXT NOT NULL,
     t INTEGER,
     v TEXT,
     sid TEXT,
     json TEXT NOT NULL,
     rec INTEGER NOT NULL)`,
  `CREATE INDEX IF NOT EXISTS idx_ev_t ON eventos(t)`,
  `CREATE INDEX IF NOT EXISTS idx_ev_e ON eventos(e)`,
  `CREATE INDEX IF NOT EXISTS idx_ev_sid ON eventos(sid)`,
];

/** Inicialización perezosa del esquema (una vez por isolate). */
let listo = false;
async function init(env) {
  if (listo) return;
  await env.DB.batch(SCHEMA.map((s) => env.DB.prepare(s)));
  listo = true;
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...CORS },
  });
}

/** Valida y normaliza un evento del lote. Devuelve null si es basura. */
function sanea(e) {
  if (!e || typeof e !== "object" || Array.isArray(e)) return null;
  if (typeof e.e !== "string" || !e.e.length || e.e.length > 40) return null;
  if (e.t !== undefined && typeof e.t !== "number") return null;
  let s;
  try {
    s = JSON.stringify(e);
  } catch {
    return null;
  }
  if (!s || s.length > MAX_EVENTO) return null;
  return {
    e: e.e,
    t: e.t ?? null,
    v: e.v ?? null,
    sid: e.sid ?? null,
    json: s,
    rec: Date.now(),
  };
}

/** La clave llega por ?clave= o cabecera X-Clave y casa con env.CLAVE. */
function claveOk(url, request, env) {
  if (!env.CLAVE) return false; // sin CLAVE configurada no hay lectura
  const dada = url.searchParams.get("clave") ?? request.headers.get("x-clave");
  return typeof dada === "string" && dada === env.CLAVE;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const metodo = request.method;

    if (metodo === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }

    // ------------------------------------------------------------- POST
    if (metodo === "POST") {
      let crudo;
      try {
        crudo = await request.text();
      } catch {
        return json({ ok: false, error: "sin cuerpo" }, 400);
      }
      if (!crudo.length) return json({ ok: false, error: "cuerpo vacío" }, 400);
      if (crudo.length > MAX_BODY) {
        return json({ ok: false, error: "cuerpo demasiado grande" }, 413);
      }
      let lote;
      try {
        lote = JSON.parse(crudo); // sendBeacon llega como text/plain: se parsea igual
      } catch {
        return json({ ok: false, error: "json inválido" }, 400);
      }
      const evs = Array.isArray(lote)
        ? lote
        : lote && typeof lote === "object" && Array.isArray(lote.events)
          ? lote.events
          : null;
      if (!evs) {
        return json(
          { ok: false, error: "se espera un array de eventos o {app,events}" },
          400
        );
      }
      const filas = [];
      for (const e of evs.slice(0, MAX_LOTE)) {
        const r = sanea(e);
        if (r) filas.push(r);
      }
      if (filas.length) {
        await init(env);
        const st = env.DB.prepare(
          "INSERT INTO eventos (e, t, v, sid, json, rec) VALUES (?, ?, ?, ?, ?, ?)"
        );
        await env.DB.batch(
          filas.map((f) => st.bind(f.e, f.t, f.v, f.sid, f.json, f.rec))
        );
      }
      // Contrato de producción vigente: 204 sin cuerpo (el juego no lee la respuesta)
      return new Response(null, { status: 204, headers: CORS });
    }

    // -------------------------------------------------------------- GET
    if (metodo === "GET") {
      await init(env);

      // latido público (sin detalle): {ok, total, ts} — filtro sid opcional
      if (
        url.searchParams.get("resumen") === null &&
        url.searchParams.get("eventos") === null
      ) {
        const sid = url.searchParams.get("sid");
        const total = sid
          ? (
              await env.DB
                .prepare("SELECT COUNT(*) n FROM eventos WHERE instr(sid, ?) > 0")
                .bind(sid)
                .first()
            ).n
          : (await env.DB.prepare("SELECT COUNT(*) n FROM eventos").first()).n;
        return json({ ok: true, total, ts: Date.now() });
      }

      // resumen y eventos son PRIVADOS: requieren la clave
      if (!claveOk(url, request, env)) {
        if (!env.CLAVE) {
          return json(
            { ok: false, error: "worker sin CLAVE configurada: crea la variable CLAVE en el worker" },
            503
          );
        }
        return json(
          { ok: false, error: "clave requerida (?clave=… o cabecera X-Clave)" },
          403
        );
      }

      const sid = url.searchParams.get("sid");
      const fil = sid ? " WHERE instr(sid, ?) > 0" : "";
      const arg = sid ? [sid] : [];

      // GET ?eventos=N → últimos N crudos (ascendente, igual que el local)
      if (url.searchParams.get("eventos") !== null) {
        const n = Math.max(
          0,
          Math.min(500, parseInt(url.searchParams.get("eventos"), 10) || 0)
        );
        const filas = (
          await env.DB
            .prepare("SELECT json FROM eventos" + fil + " ORDER BY id DESC LIMIT ?")
            .bind(...arg, n)
            .all()
        ).results;
        return json({
          ok: true,
          eventos: filas.map((r) => JSON.parse(r.json)).reverse(),
          ts: Date.now(),
        });
      }

      // GET ?resumen=1 → agregados (misma forma que el receptor local)
      const total = (
        await env.DB.prepare("SELECT COUNT(*) n FROM eventos" + fil).bind(...arg).first()
      ).n;
      const sesUnicas = (
        await env.DB
          .prepare("SELECT COUNT(DISTINCT COALESCE(sid,'-')) n FROM eventos" + fil)
          .bind(...arg)
          .first()
      ).n;
      const arranques = (
        await env.DB
          .prepare(
            "SELECT COUNT(*) n FROM eventos WHERE e='boot' AND t >= ?" +
              (sid ? " AND instr(sid, ?) > 0" : "")
          )
          .bind(Date.now() - 86400000, ...(sid ? [sid] : []))
          .first()
      ).n;
      const porEvento = {};
      for (const r of (
        await env.DB
          .prepare("SELECT e, COUNT(*) n FROM eventos" + fil + " GROUP BY e")
          .bind(...arg)
          .all()
      ).results) {
        porEvento[r.e] = r.n;
      }
      const sesiones = (
        await env.DB
          .prepare(
            "SELECT COALESCE(sid,'-') sid, MIN(t) primero, MAX(t) ultimo, " +
              "COUNT(*) n FROM eventos" + fil +
              " GROUP BY sid ORDER BY ultimo DESC LIMIT 50"
          )
          .bind(...arg)
          .all()
      ).results;
      const fpsRow = (
        await env.DB
          .prepare(
            "SELECT AVG(CAST(json_extract(json,'$.fps') AS REAL)) m, COUNT(*) n " +
              "FROM eventos WHERE e='vr_end' AND json_extract(json,'$.fps') IS NOT NULL" +
              (sid ? " AND instr(sid, ?) > 0" : "")
          )
          .bind(...(sid ? [sid] : []))
          .first()
      );
      const erroresTop = (
        await env.DB
          .prepare(
            "SELECT json_extract(json,'$.m') m, COUNT(*) n FROM eventos " +
              "WHERE e='error' AND json_extract(json,'$.m') IS NOT NULL" +
              (sid ? " AND instr(sid, ?) > 0" : "") +
              " GROUP BY m ORDER BY n DESC LIMIT 8"
          )
          .bind(...(sid ? [sid] : []))
          .all()
      ).results.map((r) => [r.m, r.n]);
      const champRank = {};
      for (const r of (
        await env.DB
          .prepare(
            "SELECT json_extract(json,'$.champ') champ, COUNT(*) partidas, " +
              "COALESCE(SUM(json_extract(json,'$.win') = 1), 0) victorias, " +
              "COALESCE(MAX(json_extract(json,'$.score')), 0) mejor, " +
              "COALESCE(SUM(json_extract(json,'$.stars')), 0) estrellas " +
              "FROM eventos WHERE e='champ_rank' AND json_extract(json,'$.champ') IS NOT NULL" +
              (sid ? " AND instr(sid, ?) > 0" : "") + " GROUP BY champ"
          )
          .bind(...arg)
          .all()
      ).results) {
        champRank[r.champ] = {
          partidas: r.partidas,
          victorias: r.victorias,
          mejor: r.mejor,
          estrellas: r.estrellas,
        };
      }
      const ultimos = (
        await env.DB
          .prepare("SELECT json FROM eventos" + fil + " ORDER BY id DESC LIMIT 20")
          .bind(...arg)
          .all()
      ).results.map((r) => JSON.parse(r.json)).reverse();

      // ── ANÁLISIS DE VENTA (ronda 9): duraciones, VR, por día, versiones
      //    (campos NUEVOS en el resumen: compatibilidad intacta con lo previo)
      const durRow = (
        await env.DB
          .prepare(
            "SELECT AVG(CAST(json_extract(json,'$.dur') AS REAL)) m, " +
              "MAX(CAST(json_extract(json,'$.dur') AS REAL)) mx, COUNT(*) n " +
              "FROM eventos WHERE e='page_close' AND json_extract(json,'$.dur') IS NOT NULL" +
              (sid ? " AND instr(sid, ?) > 0" : "")
          )
          .bind(...(sid ? [sid] : []))
          .first()
      );
      const vrDurRow = (
        await env.DB
          .prepare(
            "SELECT AVG(CAST(json_extract(json,'$.dur') AS REAL)) m, " +
              "MAX(CAST(json_extract(json,'$.dur') AS REAL)) mx, COUNT(*) n " +
              "FROM eventos WHERE e='vr_end' AND json_extract(json,'$.dur') IS NOT NULL" +
              (sid ? " AND instr(sid, ?) > 0" : "")
          )
          .bind(...(sid ? [sid] : []))
          .first()
      );
      const whereDia = fil ? fil + " AND t IS NOT NULL" : " WHERE t IS NOT NULL";
      const porDia = (
        await env.DB
          .prepare(
            "SELECT date(t/1000,'unixepoch') dia, COUNT(*) eventos, " +
              "SUM(CASE WHEN e='boot' THEN 1 ELSE 0 END) boots, " +
              "COUNT(DISTINCT CASE WHEN e='boot' THEN sid END) sesiones " +
              "FROM eventos" + whereDia +
              " GROUP BY dia ORDER BY dia DESC LIMIT 30"
          )
          .bind(...arg)
          .all()
      ).results;
      const versiones = (
        await env.DB
          .prepare(
            "SELECT COALESCE(v,'-') v, COUNT(*) eventos, " +
              "COUNT(DISTINCT COALESCE(sid,'-')) sesiones " +
              "FROM eventos" + fil +
              " GROUP BY v ORDER BY eventos DESC LIMIT 12"
          )
          .bind(...arg)
          .all()
      ).results;

      return json({
        ok: true,
        ts: Date.now(),
        total,
        sesionesUnicas: sesUnicas,
        arranques24h: arranques,
        porEvento,
        sesiones,
        fps: {
          medio: fpsRow && fpsRow.m !== null ? Math.round(fpsRow.m * 10) / 10 : null,
          muestras: fpsRow ? fpsRow.n : 0,
        },
        erroresTop,
        champRank,
        ultimos,
        duraciones: {
          media: durRow && durRow.m != null ? Math.round(durRow.m) : null,
          max: durRow && durRow.mx != null ? Math.round(durRow.mx) : null,
          n: durRow ? durRow.n : 0,
        },
        vrDuracion: {
          media: vrDurRow && vrDurRow.m != null ? Math.round(vrDurRow.m) : null,
          max: vrDurRow && vrDurRow.mx != null ? Math.round(vrDurRow.mx) : null,
          n: vrDurRow ? vrDurRow.n : 0,
        },
        porDia,
        versiones,
        almacen: "d1:crazypp-tele",
      });
    }

    // ----------------------------------------------------------- DELETE
    if (metodo === "DELETE") {
      if (!claveOk(url, request, env)) {
        return json({ ok: false, error: "clave requerida" }, 403);
      }
      await init(env);
      const sid = url.searchParams.get("sid");
      const r = sid
        ? await env.DB.prepare("DELETE FROM eventos WHERE instr(sid, ?) > 0").bind(sid).run()
        : await env.DB.prepare("DELETE FROM eventos").run();
      return json({ ok: true, borrados: r.meta ? r.meta.changes : 0, ts: Date.now() });
    }

    return json({ ok: false, error: "ruta o método desconocido — usa /api/tele" }, 404);
  },
};
