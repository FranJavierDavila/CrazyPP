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

/* ======================================================================
 * r87 · RED SOCIAL DEL PULSO (presencia + invitaciones sobre D1)
 * ==================================================================== */
const SOCIAL_SCHEMA = [
  // r87-QA (lección): el DROP de las tablas antiguas NO puede vivir aquí —
  // cada isolate nuevo lo re-ejecutaría y BORRARÍA los latidos vivos de los
  // demás isolates. La migración del esquema legacy se hace UNA VEZ por la
  // API de D1 (scripts/deploy_worker.py / consola). Aquí sólo CREATE IF NOT
  // EXISTS, idempotente y seguro.
  `CREATE TABLE IF NOT EXISTS presencia (
     pid TEXT PRIMARY KEY,
     n TEXT, v TEXT, st TEXT, code TEXT,
     t INTEGER NOT NULL)`,
  `CREATE INDEX IF NOT EXISTS idx_pres_t ON presencia(t)`,
  `CREATE TABLE IF NOT EXISTS invitas (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     de TEXT NOT NULL, deN TEXT, para TEXT NOT NULL, code TEXT,
     t INTEGER NOT NULL)`,
  `CREATE INDEX IF NOT EXISTS idx_inv_para ON invitas(para)`,
  `CREATE INDEX IF NOT EXISTS idx_inv_t ON invitas(t)`,
];
let socialListo = false;
async function socialInit(env) {
  if (socialListo) return;
  await env.DB.batch(SOCIAL_SCHEMA.map((s) => env.DB.prepare(s)));
  socialListo = true;
}

const PRESENCIA_TTL = 90 * 1000;      // latidos vivos: 90 s
const INVITA_TTL = 6 * 3600 * 1000;   // las invitaciones viven 6 h
const INVITA_TOPE = 5;                // buzón máx. por destinatario

/** saneo suave: el juego es público — nada de HTML, nada de longitud. */
function texto(v, tope) {
  if (typeof v !== "string") return "";
  return v.replace(/[\u0000-\u001f\u007f]/g, "").trim().slice(0, tope);   // fuera caracteres de control
}
function pidOk(v) {
  return typeof v === "string" && /^[a-zA-Z0-9-]{4,32}$/.test(v);
}

async function social(request, env, url, metodo) {
  let crudo;
  try {
    crudo = await request.text();
  } catch {
    crudo = "";
  }
  if (crudo.length > 4096) return json({ ok: false, error: "cuerpo demasiado grande" }, 413);
  let cuerpo = {};
  if (crudo.length) {
    try { cuerpo = JSON.parse(crudo); } catch { return json({ ok: false, error: "json inválido" }, 400); }
    if (!cuerpo || typeof cuerpo !== "object" || Array.isArray(cuerpo)) {
      return json({ ok: false, error: "json inválido" }, 400);
    }
  }
  await socialInit(env);
  const ahora = Date.now();

  /* ------------------------------- PRESENCIA ------------------------- */
  if (url.pathname === "/api/presencia") {
    // purga perezosa: fuera los latidos muertos y las invitaciones viejas
    await env.DB.batch([
      env.DB.prepare("DELETE FROM presencia WHERE t < ?").bind(ahora - PRESENCIA_TTL),
      env.DB.prepare("DELETE FROM invitas WHERE t < ?").bind(ahora - INVITA_TTL),
    ]);

    if (metodo === "POST") {
      const pid = cuerpo.pid;
      if (cuerpo.bye) {
        if (pidOk(pid)) await env.DB.prepare("DELETE FROM presencia WHERE pid = ?").bind(pid).run();
        return json({ ok: true, bye: true, ts: ahora });
      }
      if (!pidOk(pid)) return json({ ok: false, error: "pid inválido" }, 400);
      const n = texto(cuerpo.n, 20) || "Jugador";
      const v = texto(cuerpo.v, 24);
      const st = ["libre", "sala", "juego"].includes(cuerpo.st) ? cuerpo.st : "libre";
      const code = texto(cuerpo.code, 12).toUpperCase();
      await env.DB.prepare(
        `INSERT INTO presencia (pid, n, v, st, code, t) VALUES (?, ?, ?, ?, ?, ?)
         ON CONFLICT(pid) DO UPDATE SET n=excluded.n, v=excluded.v,
           st=excluded.st, code=excluded.code, t=excluded.t`
      ).bind(pid, n, v, st, st === "sala" ? code : "", ahora).run();
      const { n: total } = await env.DB.prepare("SELECT COUNT(*) n FROM presencia").first();
      return json({ ok: true, n: total, ts: ahora });
    }

    if (metodo === "GET") {
      const { n: total } = await env.DB.prepare("SELECT COUNT(*) n FROM presencia").first();
      if (url.searchParams.get("lista") == null) {
        return json({ ok: true, n: total, ts: ahora });
      }
      const { results } = await env.DB.prepare(
        "SELECT pid, n, st, code, t FROM presencia ORDER BY t DESC LIMIT 30"
      ).all();
      const jugadores = (results || []).map((r) => ({
        pid: r.pid, n: r.n, st: r.st, code: r.code || "",
        hace: Math.max(0, Math.round((ahora - (r.t || ahora)) / 1000)),
      }));
      return json({ ok: true, n: total, jugadores, ts: ahora });
    }
    return json({ ok: false, error: "método no soportado en /api/presencia" }, 405);
  }

  /* ------------------------------- INVITAS --------------------------- */
  if (url.pathname === "/api/invita") {
    await env.DB.batch([
      env.DB.prepare("DELETE FROM presencia WHERE t < ?").bind(ahora - PRESENCIA_TTL),
      env.DB.prepare("DELETE FROM invitas WHERE t < ?").bind(ahora - INVITA_TTL),
    ]);

    if (metodo === "POST") {
      const de = cuerpo.de, para = cuerpo.para, code = texto(cuerpo.code, 12).toUpperCase();
      if (!pidOk(de) || !pidOk(para)) return json({ ok: false, error: "pid inválido" }, 400);
      if (de === para) return json({ ok: false, error: "invitar a uno mismo" }, 400);
      if (!code) return json({ ok: false, error: "sin código de sala" }, 400);
      // el REMITENTE debe tener su sala VIVA con ESE código (anti-spam):
      // latido st='sala' fresco. Si no, la invitación se rechaza.
      const remitente = await env.DB.prepare(
        "SELECT st, code FROM presencia WHERE pid = ? AND t > ?"
      ).bind(de, ahora - PRESENCIA_TTL).first();
      if (!remitente || remitente.st !== "sala" || remitente.code !== code) {
        return json({ ok: false, error: "sala no activa" }, 409);
      }
      const { n: ya } = await env.DB.prepare(
        "SELECT COUNT(*) n FROM invitas WHERE para = ?"
      ).bind(para).first();
      if (ya >= INVITA_TOPE) return json({ ok: false, error: "buzón lleno" }, 429);
      const r = await env.DB.prepare(
        "INSERT INTO invitas (de, deN, para, code, t) VALUES (?, ?, ?, ?, ?)"
      ).bind(de, texto(cuerpo.deN, 20) || "Jugador", para, code, ahora).run();
      return json({ ok: true, id: r.meta && r.meta.last_row_id, ts: ahora });
    }

    if (metodo === "GET") {
      const pid = url.searchParams.get("pid");
      if (!pidOk(pid)) return json({ ok: false, error: "pid inválido" }, 400);
      const { results } = await env.DB.prepare(
        "SELECT id, de, deN, code, t FROM invitas WHERE para = ? ORDER BY t DESC LIMIT 8"
      ).bind(pid).all();
      const invitas = (results || []).map((r) => ({
        id: r.id, de: r.de, deN: r.deN, code: r.code || "",
        hace: Math.max(0, Math.round((ahora - (r.t || ahora)) / 1000)),
      }));
      return json({ ok: true, invitas, ts: ahora });
    }

    if (metodo === "DELETE") {
      const pid = url.searchParams.get("pid");
      const id = parseInt(url.searchParams.get("id") || "0", 10) || 0;
      if (id > 0 && pidOk(pid)) {
        const r = await env.DB.prepare("DELETE FROM invitas WHERE id = ? AND para = ?").bind(id, pid).run();
        return json({ ok: true, borrados: r.meta ? r.meta.changes : 0 });
      }
      if (pidOk(pid)) {
        const r = await env.DB.prepare("DELETE FROM invitas WHERE para = ?").bind(pid).run();
        return json({ ok: true, borrados: r.meta ? r.meta.changes : 0 });
      }
      return json({ ok: false, error: "pid inválido" }, 400);
    }
    return json({ ok: false, error: "método no soportado en /api/invita" }, 405);
  }

  return json({ ok: false, error: "ruta social desconocida" }, 404);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const metodo = request.method;

    if (metodo === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }

    /* ================================================================
     * r87 · RED SOCIAL DEL PULSO — /api/presencia + /api/invita
     * ----------------------------------------------------------------
     * El medallón de jugadores en línea y el buzón de invitaciones del
     * menú Multijugador (c09c_red_social.js) viven AQUÍ, en el mismo
     * worker que la telemetría — ANTES mentía: el cliente existía pero
     * el worker no tenía rutas y el juego respondía 404 en silencio.
     *
     *   POST /api/presencia        {pid,n,v,st,code} → upsert (TTL 90 s)
     *                              {pid,bye:1}       → baja inmediata
     *   GET  /api/presencia        → {ok, n, ts} (número fresco)
     *   GET  /api/presencia?lista=1→ {ok, n, jugadores[]} (tope 30)
     *   POST /api/invita           {de,deN,para,code} → {ok, id}
     *                              (sólo si «de» tiene sala abierta VIVA)
     *   GET  /api/invita?pid=…     → {ok, invitas[]} (tope 8, TTL 6 h)
     *   DELETE /api/invita?pid=…   → consume todo el buzón del pid
     *
     * PRIVACIDAD (misma política que la telemetría): pid anónimo del
     * dispositivo, nombre de jugador elegido por el usuario, estado y
     * código de sala. SIN IP, SIN user-agent, SIN cabeceras.
     * No requiere clave (el juego es público: nunca guarda secretos).
     * ================================================================ */
    if (url.pathname === "/api/presencia" || url.pathname === "/api/invita") {
      return social(request, env, url, metodo);
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

      // ── EMBUDO POR CAMPEONATO (ronda 11): stage/champion llevan $.id desde
      //    3.6.8-SDK6 — el panel separa Magia de La Locura. Tolerante con
      //    datos viejos (eventos sin id quedan fuera; el embudo global ya
      //    los cubre desde porEvento). OJO: el alias es «champ», NO «id» —
      //    la tabla TIENE columna id (AUTOINCREMENT) y GROUP BY id agruparía
      //    por el id numérico de fila (cazado por el harness ronda 11).
      const porCampeonato = {};
      for (const r of (
        await env.DB
          .prepare(
            "SELECT json_extract(json,'$.id') champ, e, COUNT(*) n FROM eventos " +
              "WHERE e IN ('stage','champion') AND json_extract(json,'$.id') IS NOT NULL" +
              (sid ? " AND instr(sid, ?) > 0" : "") +
              " GROUP BY champ, e"
          )
          .bind(...arg)
          .all()
      ).results) {
        if (!porCampeonato[r.champ]) porCampeonato[r.champ] = {};
        porCampeonato[r.champ][r.e] = (porCampeonato[r.champ][r.e] || 0) + r.n;
      }

      // ── SESIONES VR (ronda 14): permanencia REAL en el casco. El vr_end
      //    cierra el ciclo (dur real); desde la ronda 12 el vr_ping cada
      //    5 min lo FECHA cuando el casco se apaga sin vr_end (caso
      //    k5ui6abo). Fold en JS sobre UNA consulta en orden de inserción:
      //    cada vr_start abre ciclo, el último ping manda en la dur
      //    estimada. Alias SQL tipo «id» prohibidos (lección ronda 11).
      const vrEv = (
        await env.DB
          .prepare(
            "SELECT json FROM eventos WHERE e IN ('vr_start','vr_end','vr_ping')" +
              (sid ? " AND instr(sid, ?) > 0" : "") +
              " ORDER BY id ASC LIMIT 2000"
          )
          .bind(...(sid ? [sid] : []))
          .all()
      ).results.map((r) => JSON.parse(r.json));
      const ciclosVR = [];
      let vrAct = null;
      for (const e of vrEv) {
        if (e.e === "vr_start") {
          vrAct = {
            sid: e.sid || "-",
            v: e.v || "-",
            inicio: e.t || 0,
            dur: null,
            durReal: false,
            estado: "abierta",
            fps: null,
            fpsMin: null,
            fpsMax: null,
            pings: 0,
            curva: [],
          };
          ciclosVR.push(vrAct);
        } else if (!vrAct) {
          continue; // vr_end/vr_ping huérfanos (sin vr_start): fuera
        } else if (e.e === "vr_end") {
          vrAct.estado = "cerrada";
          vrAct.durReal = true;
          if (typeof e.dur === "number") vrAct.dur = e.dur;
          if (typeof e.fps === "number") vrAct.fps = e.fps;
          if (typeof e.fpsMin === "number") vrAct.fpsMin = e.fpsMin;
          if (typeof e.fpsMax === "number") vrAct.fpsMax = e.fpsMax;
        } else if (e.e === "vr_ping") {
          vrAct.pings++;
          if (vrAct.estado !== "cerrada") vrAct.estado = "interrumpida";
          if (typeof e.dur === "number") vrAct.dur = e.dur;
          if (typeof e.fps === "number" && vrAct.curva.length < 24)
            vrAct.curva.push({
              m: e.t > vrAct.inicio ? Math.round((e.t - vrAct.inicio) / 60000) : 0,
              fps: e.fps,
            });
        }
      }
      const sesionesVR = ciclosVR.slice(-12).reverse();

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
        porCampeonato,
        sesionesVR,
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
