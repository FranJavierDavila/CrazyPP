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
 *   GET    /api/ice             → {ok, ts, turn, iceServers, ttl?} (público)
 *                                 TURN efímero de Cloudflare para la partida
 *                                 real (ronda 19 · P4) — ver su sección abajo
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
 *
 * Ronda M5b (roadmap MEJORAS.md M5 · alertas de telemetría): el bloque
 * `alarmas` gana el item `sin_sonido` (golpes sin sonido: errores con
 * marcador de audio o eventos golpe_sin_sonido) y nace el reporte del
 * dueño scripts/alerta_telemetria.py (lectura ?resumen=1 + salida clara).
 *
 * Ronda 18 (roadmap MEJORAS.md M2b): el resumen añade el bloque `alarmas`
 *   — interpreta los agregados y avisa de los tres síntomas que matan la
 *   retención en el casco. Tolerante: sin datos suficientes → «verde».
 *   fps_bajo    media de vr_end.fps < 72 con ≥3 muestras (amarillo; < 60 rojo)
 *   errores_js  eventos `error` por sesión ≥1 (amarillo; ≥3 rojo, top incluido)
 *   vr_cortas   sesiones VR cerradas de <60 s ≥25% con ≥3 (amarillo; ≥50% rojo)
 *   Estructura: {nivel:"verde"|"amarillo"|"rojo", items:[{id,nivel,msg,datos}]}
 *
 * Ronda 19 (P4 · primera partida real con 2 Quest): nace /api/ice —
 *   TURN de Cloudflare Realtime con credenciales efímeras (TTL 6 h)
 *   para que el enlace abra aunque haya NAT simétrico de por medio.
 *   El worker se auto-provisiona la TURN key (tabla cfg de D1) y sanea
 *   las urls (fuera el puerto 53, bloqueado por los navegadores).
 *   Sin TURN_API_TOKEN → STUN honesto y turn:false (degradación limpia).
 *
 * ronda 42 · TELEMETRÍA PROFESIONAL (control absoluto desde el repo):
 *   GET  /api/tele?salud=1        → PÚBLICO {ok, total, ultimoRec, haceSeg}
 *                                   (LED de salud del panel: ¿llegan lotes?)
 *   GET  /api/tele?csv=1          → CSV crudo (CLAVE; tope 20.000 filas;
 *                                   ?tope=N; filtros ?sid= y ?dias=N)
 *   ?dias=N                       → filtra por LLEGADA (columna rec) en
 *                                   resumen, eventos, csv y DELETE —
 *                                   combinable con ?sid= en todos
 *   DELETE /api/tele?dias=N       → retención: purga sólo lo ANTERIOR a N
 *                                   días (con ?sid= acota a esa sesión)
 *   El POST, el latido, el resumen y /api/ice quedan INTACTOS (contrato
 *   del juego 3.6.5-SDK6 sin cambios; el cliente no se toca).
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
 * ronda 19 · P4 — /api/ice · ICE servers para la PRIMERA PARTIDA REAL
 * --------------------------------------------------------------------
 * El TURN público OpenRelay/metered.ca que traía el juego está MUERTO:
 * sin TURN vivo, un casco tras NAT simétrico (hotspot, algunas fibras)
 * no llega a abrir el enlace P2P. Cloudflare Realtime ofrece TURN con
 * CREDENCIALES EFÍMERAS — este endpoint las acuña y las reparte:
 *
 *   GET  /api/ice → {ok, ts, turn: bool, iceServers: [...], ttl?}
 *                    público, sin clave: las credenciales son efímeras
 *                    y el juego es código público (nunca guarda secretos)
 *   POST /api/ice → 405
 *
 * Variables del worker (por dashboard, LEEME-P4-PRIMERA-PARTIDA.md):
 *   TURN_API_TOKEN  secret · API token del dueño con permiso
 *                   Realtime TURN → Edit. Si falta: STUN y turn:false.
 *   TURN_KEY_ID     opcional · si falta, el worker SE AUTO-PROVISIONA
 *                   la TURN key (POST /accounts/{id}/calls/turn_keys)
 *                   y la recuerda en la tabla `cfg` de D1.
 *   CF_ACCOUNT_ID   opcional · si falta, se deriva del token (GET /accounts).
 *   ICE_TTL_MS      opcional · caché por isolate (QA; defecto 4 min).
 *
 * Credenciales: POST rtc.live.cloudflare.com/v1/turn/keys/{key_id}/
 * credentials/generate-ice-servers {"ttl":21600} → 201 {iceServers}
 * (documentación oficial de Cloudflare Realtime, «Generate Credentials»).
 * Saneo local: sólo urls stun/turn/turns y FUERA el puerto 53 — nota
 * oficial de CF: los navegadores lo bloquean y el ICE esperaría el timeout.
 *
 * ronda 20 · P4-F4 — RUTA METERED SIN COSTE (juego entre casas distintas)
 * ---------------------------------------------------------------------
 * VERIFICADO EN SANDBOX (2026-11-07): el TURN público Open Relay está
 * RETIRADO — openrelay.metered.ca resuelve a 192.0.2.1 (IP-documentación,
 * RFC 5737) y staticauth.openrelay.metered.ca no responde ni por UDP ni
 * TCP con el esquema coturn. NADA de credenciales muertas al cliente.
 *
 * Alternativa sin tarjeta: cuenta gratuita de Metered (Open Relay, 20
 * GB/mes). El dueño crea la cuenta, y el worker acude a su API REST a
 * por credenciales dinámicas con SOLO dos variables nuevas (sin redeploy
 * de este código):
 *   METERED_APP      texto  · subdominio de la app (x.metered.live)
 *   METERED_API_KEY  secret · apiKey del panel de Metered
 * → GET https://{METERED_APP}.metered.live/api/v1/turn/credentials
 *   ?apiKey=… → 200 [ {urls:[…], username, credential}, … ]
 * (mismo formato que generate-ice-servers: pasa por el mismo saneo).
 *
 * PRIORIDAD: TURN_API_TOKEN (Cloudflare, gratis hasta 1 TB/mes) >
 * METERED_* (20 GB/mes) > STUN honesto con turn:false. El campo `fuente`
 * de la respuesta indica quién dio el relé (cloudflare|metered).
 * ==================================================================== */
const ICE_TTL_DEFECTO = 21600;        // 6 h de vida de la credencial TURN
const ICE_CACHE_MS = 4 * 60 * 1000;   // caché por isolate (≤15 llamadas/h)
const ICE_STUN_BASE = [
  { urls: ["stun:stun.cloudflare.com:3478", "stun:stun1.l.google.com:19302"] },
];
let iceCache = null;                  // { t0, resp } — por isolate

function iceTtlMs(env) {
  const n = Number(env && env.ICE_TTL_MS);
  return Number.isFinite(n) && n >= 0 ? n : ICE_CACHE_MS;
}

/** Sanea la respuesta de rtc.live: urls válidas, sin :53, TURN sin
 *  credencial fuera. Defensa en profundidad (el upstream ya es de CF). */
function saneaIceServers(lista) {
  if (!Array.isArray(lista)) return [];
  const fuera = [];
  for (const s of lista) {
    if (!s || !Array.isArray(s.urls)) continue;
    const urls = s.urls.filter((u) =>
      typeof u === "string" &&
      /^(stun|turn|turns):/.test(u) && !/:53(\?|$)/.test(u)
    );
    if (!urls.length) continue;
    if (/^turn/.test(urls[0]) &&
        (typeof s.username !== "string" || !s.username ||
         typeof s.credential !== "string" || !s.credential)) continue;
    const limpio = { urls };
    if (typeof s.username === "string" && s.username) limpio.username = s.username;
    if (typeof s.credential === "string" && s.credential) limpio.credential = s.credential;
    fuera.push(limpio);
  }
  return fuera;
}

/** Fusiona la base STUN con los servidores de un upstream, sin duplicar
 *  urls (las entradas con el mismo bloque urls se quedan en su 1ª vez). */
function fusionaIce(base, extra) {
  const vista = new Set(base.map((s) => s.urls.join(" ")));
  return base.concat((extra || []).filter((s) => s && Array.isArray(s.urls) &&
    !vista.has(s.urls.join(" "))));
}

/** Id de la cuenta: variable explícita o derivada del token (una vez). */
let iceAccId = "";
async function cuentaId(env, token, fetchImpl) {
  const a = env && env.CF_ACCOUNT_ID;
  if (typeof a === "string" && /^[0-9a-f]{32}$/.test(a)) return a;
  if (iceAccId) return iceAccId;
  const r = await fetchImpl("https://api.cloudflare.com/client/v4/accounts?per_page=1", {
    headers: { Authorization: `Bearer ${token}` },
  });
  const j = await r.json();
  const id = j && j.success && Array.isArray(j.result) && j.result[0] && j.result[0].id;
  if (typeof id !== "string" || !/^[0-9a-f]{32}$/.test(id)) {
    throw new Error("sin acceso a cuentas (token sin permiso?)");
  }
  iceAccId = id;
  return id;
}

/** Acuña credenciales y devuelve la respuesta /api/ice (con caché). */
async function iceRespuesta(env, fetchImpl) {
  const ahora = Date.now();
  if (iceCache && ahora - iceCache.t0 < iceTtlMs(env)) return iceCache.resp;

  let resp = null;
  const token = env && env.TURN_API_TOKEN;
  if (token) {
    try {
      await socialInit(env);                        // tabla cfg
      let keyId = env.TURN_KEY_ID;
      if (!keyId) {
        const fila = await env.DB.prepare("SELECT v FROM cfg WHERE k = 'turn_key_id'").first();
        keyId = fila && fila.v;
      }
      if (!keyId) {
        const acc = await cuentaId(env, token, fetchImpl);
        const r = await fetchImpl(
          `https://api.cloudflare.com/client/v4/accounts/${acc}/calls/turn_keys`,
          {
            method: "POST",
            headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
            body: JSON.stringify({ name: "crazypp-worker", buckets: 1, bucket_duration_seconds: 86400 }),
          }
        );
        const j = await r.json();
        if (j && j.success && j.result && j.result.key_id) {
          keyId = j.result.key_id;
          await env.DB.prepare(
            "INSERT INTO cfg (k, v) VALUES ('turn_key_id', ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v"
          ).bind(keyId).run();
        }
      }
      if (keyId) {
        const r = await fetchImpl(
          `https://rtc.live.cloudflare.com/v1/turn/keys/${keyId}/credentials/generate-ice-servers`,
          {
            method: "POST",
            headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
            body: JSON.stringify({ ttl: ICE_TTL_DEFECTO }),
          }
        );
        if (r.status === 201) {
          const j = await r.json();
          const servs = saneaIceServers(j && j.iceServers);
          if (servs.length) {
            resp = { ok: true, ts: ahora, turn: true, iceServers: servs, ttl: ICE_TTL_DEFECTO, fuente: "cloudflare" };
          }
        }
      }
    } catch { /* cae abajo → STUN honesto */ }
    if (!resp) resp = { ok: true, ts: ahora, turn: false, iceServers: ICE_STUN_BASE, error: "turn_upstream" };
  } else {
    // ronda 20 · P4-F4 — ruta Metered (cuenta gratuita del dueño, sin
    // tarjeta): si están las dos variables, pedimos credenciales dinámicas
    // a su API REST y las saneamos igual que las de Cloudflare.
    const mApp = env && env.METERED_APP;
    const mKey = env && env.METERED_API_KEY;
    if (typeof mApp === "string" && mApp && typeof mKey === "string" && mKey) {
      try {
        const r = await fetchImpl(
          `https://${mApp}.metered.live/api/v1/turn/credentials?apiKey=${encodeURIComponent(mKey)}`
        );
        if (r.status === 200) {
          const j = await r.json();
          const servs = saneaIceServers(j);
          const hayTurn = servs.some((s) => s.urls.some((u) => /^turn/.test(u)));
          if (hayTurn) {
            resp = { ok: true, ts: ahora, turn: true,
                     iceServers: fusionaIce(ICE_STUN_BASE, servs),
                     ttl: ICE_TTL_DEFECTO, fuente: "metered" };
          }
        }
      } catch { /* cae abajo → STUN honesto */ }
      if (!resp) {
        resp = { ok: true, ts: ahora, turn: false, iceServers: ICE_STUN_BASE, error: "metered_upstream" };
      }
    } else {
      resp = { ok: true, ts: ahora, turn: false, iceServers: ICE_STUN_BASE };
    }
  }
  iceCache = { t0: ahora, resp };
  return resp;
}

async function iceEndpoint(request, env, url, metodo) {
  if (metodo !== "GET") {
    return json({ ok: false, error: "método no soportado en /api/ice" }, 405);
  }
  try {
    return json(await iceRespuesta(env, fetch));
  } catch (e) {
    return json({ ok: true, ts: Date.now(), turn: false, iceServers: ICE_STUN_BASE, error: "ice_interno" });
  }
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
  // ronda 19: pequeño almacén de configuración (turn_key_id)
  `CREATE TABLE IF NOT EXISTS cfg (
     k TEXT PRIMARY KEY,
     v TEXT)`,
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
    if (url.pathname === "/api/ice") {
      return iceEndpoint(request, env, url, metodo);
    }

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

      // ronda 42 · SALUD pública (sin detalle): LED del panel. total y la
      // frescura del último lote recibido (MAX(rec)) — nada sensible.
      if (url.searchParams.get("salud") !== null) {
        const filaS = await env.DB
          .prepare("SELECT COUNT(*) n, MAX(rec) ultimo FROM eventos")
          .first();
        return json({
          ok: true,
          ts: Date.now(),
          total: filaS ? filaS.n : 0,
          ultimoRec: filaS ? filaS.ultimo : null,
          haceSeg: filaS && filaS.ultimo
            ? Math.round((Date.now() - filaS.ultimo) / 1000)
            : null,
        });
      }

      // latido público (sin detalle): {ok, total, ts} — filtro sid opcional
      if (
        url.searchParams.get("resumen") === null &&
        url.searchParams.get("eventos") === null &&
        url.searchParams.get("csv") === null &&
        url.searchParams.get("rank") === null   // r45 · el rank va detrás
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
      // ronda 42 · FILTRO ?dias=N — lo llegado en los últimos N días
      // (columna rec, llegada al SERVIDOR: robusta ante relojes de cliente).
      // Combina con ?sid= en resumen, eventos, csv y DELETE.
      const diasQ = parseInt(url.searchParams.get("dias"), 10);
      const diasMs = Number.isFinite(diasQ) && diasQ > 0
        ? Date.now() - diasQ * 86400000
        : null;
      const conds = [];
      const arg = [];
      if (sid) { conds.push("instr(sid, ?) > 0"); arg.push(sid); }
      if (diasMs !== null) { conds.push("rec >= ?"); arg.push(diasMs); }
      const fil = conds.length ? " WHERE " + conds.join(" AND ") : "";
      // sufijo para consultas que YA llevan WHERE base (p.ej. e='error')
      const suf =
        (sid ? " AND instr(sid, ?) > 0" : "") +
        (diasMs !== null ? " AND rec >= ?" : "");

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

      // ================================================================
      // r45/r46 · RANKINGS MUNDIALES (?rank=1 · CLAVE) — agrega por JUGADOR
      // ----------------------------------------------------------------
      // Fuente: los eventos con identidad mínima (pid anónimo + nombre
      // elegido) desde la build 3.6.139:
      //   perfil    {el,w,bs,st,pt,ach} → foto de progreso (último manda)
      //   resultado {m,a,b,w,bo}        → partidas, victorias, online
      //   logro     {k}                 → desbloqueos (c12·celebrate)
      // Ventana ?dias (defecto 90) por LLEGADA al servidor (rec): el
      // ranking es de temporada viva. Fold en JS sobre UNA consulta.
      // Devuelve {ok, rank:{jugadores, elo[], vics[], pts[], logros[]}} —
      // el panel (telemetria.html · pintaRank) pinta las 4 tablas.
      // ================================================================
      if (url.searchParams.get("rank") !== null) {
        const diasRankQ = parseInt(url.searchParams.get("dias"), 10);
        const diasRank = Number.isFinite(diasRankQ) && diasRankQ > 0
          ? diasRankQ : 90;
        const filasR = (
          await env.DB
            .prepare(
              "SELECT json FROM eventos WHERE rec >= ? AND " +
              "(e = 'perfil' OR e = 'resultado' OR e = 'logro') " +
              "ORDER BY id ASC LIMIT 8000"
            )
            .bind(Date.now() - diasRank * 86400000)
            .all()
        ).results.map((r) => JSON.parse(r.json));
        const porPid = new Map();
        for (const e of filasR) {
          const pid = String(e.pid || "").slice(0, 40);
          if (!pid) continue;   // sin pid (builds viejos) no hay ranking
          let j = porPid.get(pid);
          if (!j) {
            j = { n: "", el: 1000, w: 0, bs: 0, st: 0, pt: 0, ach: 0,
              part: 0, p2p: 0, ultimo: 0 };
            porPid.set(pid, j);
          }
          if (e.n) j.n = String(e.n).slice(0, 16);
          if ((e.t || 0) > j.ultimo) j.ultimo = e.t || 0;
          if (e.e === "perfil") {
            // ÚLTIMO perfil manda (la foto fresca del progreso)
            for (const k of ["el", "w", "bs", "st", "pt", "ach"]) {
              if (typeof e[k] === "number") j[k] = e[k];
            }
          } else if (e.e === "resultado") {
            // el w del PERFIL (victorias de por vida) manda: el resultado
            // sólo añade contadores de partidos firmados (part/p2p)
            j.part++;
            if (e.m === "p2p") j.p2p++;
          }
        }
        const ahora = Date.now();
        const todos = [...porPid.entries()].map(([pid, j]) => ({
          pid,
          n: j.n || ("jugador-" + pid.slice(0, 4)),
          el: j.el, w: j.w, part: j.part, p2p: j.p2p,
          pt: j.pt, st: j.st, bs: j.bs, ach: j.ach,
          hace: j.ultimo ? Math.max(0, Math.round((ahora - j.ultimo) / 1000)) : null,
        }));
        const top = (cmp) => todos.slice().sort(cmp).slice(0, 20);
        return json({
          ok: true,
          ts: ahora,
          rank: {
            jugadores: todos.length,
            elo: top((a, b) => b.el - a.el),
            vics: top((a, b) => b.w - a.w),
            pts: top((a, b) => b.pt - a.pt),
            logros: top((a, b) => b.ach - a.ach),
          },
        });
      }

      // ronda 42 · GET ?csv=1 → exportación cruda (CLAVE). Columnas: e,
      // fecha_iso, t_ms, version, sid, json (el JSON completo, citado y
      // escapado). ?tope=N (defecto 20.000, máx 50.000) · ?sid= · ?dias=.
      if (url.searchParams.get("csv") !== null) {
        const topeQ = parseInt(url.searchParams.get("tope"), 10);
        const tope = Math.min(
          50000,
          Math.max(1, Number.isFinite(topeQ) ? topeQ : 20000)
        );
        const filas = (
          await env.DB
            .prepare(
              "SELECT e, t, v, sid, json FROM eventos" + fil +
                " ORDER BY id DESC LIMIT ?"
            )
            .bind(...arg, tope)
            .all()
        ).results.reverse();
        const esc = (s) => '"' + String(s == null ? "" : s).replace(/"/g, '""') + '"';
        const lineas = ["e,fecha_iso,t_ms,version,sid,json"];
        for (const r of filas) {
          lineas.push(
            [
              esc(r.e),
              r.t ? new Date(r.t).toISOString() : "",
              r.t == null ? "" : String(r.t),
              esc(r.v),
              esc(r.sid),
              esc(r.json),
            ].join(",")
          );
        }
        // BOM para que Excel respete el UTF-8
        return new Response("\uFEFF" + lineas.join("\r\n"), {
          status: 200,
          headers: {
            "content-type": "text/csv; charset=utf-8",
            "content-disposition": 'attachment; filename="telemetria-crazypp.csv"',
            ...CORS,
          },
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
              suf
          )
          .bind(Date.now() - 86400000, ...arg)
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
              suf
          )
          .bind(...arg)
          .first()
      );
      const erroresTop = (
        await env.DB
          .prepare(
            "SELECT json_extract(json,'$.m') m, COUNT(*) n FROM eventos " +
              "WHERE e='error' AND json_extract(json,'$.m') IS NOT NULL" +
              suf +
              " GROUP BY m ORDER BY n DESC LIMIT 8"
          )
          .bind(...arg)
          .all()
      ).results.map((r) => [r.m, r.n]);
      // ── sin_sonido (M5b): señales de audio roto. Cuenta errores cuyo
      //    mensaje lleva marcador de audio (decode/AudioContext/sfx/sonido)
      //    más eventos golpe_sin_sonido (el juego aún no los envía: la
      //    alarma queda preparada para el día que lleguen — cero deploy).
      const sonidoRow = (
        await env.DB
          .prepare(
            "SELECT COUNT(*) n FROM eventos WHERE (" +
              "(e='golpe_sin_sonido' OR (e='error' AND (" +
              "instr(lower(COALESCE(json_extract(json,'$.m'),'')),'audio') > 0 OR " +
              "instr(lower(COALESCE(json_extract(json,'$.m'),'')),'sonido') > 0 OR " +
              "instr(lower(COALESCE(json_extract(json,'$.m'),'')),'decode') > 0 OR " +
              "instr(lower(COALESCE(json_extract(json,'$.m'),'')),'sfx') > 0)))" +
              suf +
              ")"
          )
          .bind(...arg)
          .first()
      );
      const champRank = {};
      for (const r of (
        await env.DB
          .prepare(
            "SELECT json_extract(json,'$.champ') champ, COUNT(*) partidas, " +
              "COALESCE(SUM(json_extract(json,'$.win') = 1), 0) victorias, " +
              "COALESCE(MAX(json_extract(json,'$.score')), 0) mejor, " +
              "COALESCE(SUM(json_extract(json,'$.stars')), 0) estrellas " +
              "FROM eventos WHERE e='champ_rank' AND json_extract(json,'$.champ') IS NOT NULL" +
              suf + " GROUP BY champ"
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
              suf
          )
          .bind(...arg)
          .first()
      );
      const vrDurRow = (
        await env.DB
          .prepare(
            "SELECT AVG(CAST(json_extract(json,'$.dur') AS REAL)) m, " +
              "MAX(CAST(json_extract(json,'$.dur') AS REAL)) mx, COUNT(*) n " +
              "FROM eventos WHERE e='vr_end' AND json_extract(json,'$.dur') IS NOT NULL" +
              suf
          )
          .bind(...arg)
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
              suf +
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
              suf +
              " ORDER BY id ASC LIMIT 2000"
          )
          .bind(...arg)
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

      // ── ALARMAS DE TELEMETRÍA (ronda 18 · roadmap MEJORAS.md M2b) ──
      // Interpreta los agregados de arriba y avisa de los tres síntomas
      // que matan la retención en el casco. Campo NUEVO y tolerante: si
      // no hay datos suficientes el nivel es «verde» y no se emite item.
      // Umbral fps: 72 = confort del Quest (regla del panel desde r14);
      // 60 = mínimo jugable. dur de vr_end/vr_ping en SEGUNDOS (c00).
      const alarmas = (() => {
        const items = [];
        // 1 · fps_bajo — media de vr_end.fps (≥3 muestras para no chirriar)
        if (fpsRow && fpsRow.m != null && fpsRow.n >= 3) {
          const medio = Math.round(fpsRow.m * 10) / 10;
          const nv = medio < 60 ? "rojo" : medio < 72 ? "amarillo" : null;
          if (nv) {
            items.push({
              id: "fps_bajo",
              nivel: nv,
              msg: "FPS medio en VR " + medio + " (" +
                (nv === "rojo" ? "bajo el mínimo jugable 60" : "bajo el confort 72") + ")",
              datos: { medio, muestras: fpsRow.n },
            });
          }
        }
        // 2 · errores_js — media de eventos `error` por sesión (top incluido)
        const errores = porEvento["error"] || 0;
        if (errores > 0 && sesUnicas > 0) {
          const media = Math.round((errores / sesUnicas) * 10) / 10;
          const nv = media >= 3 ? "rojo" : media >= 1 ? "amarillo" : null;
          if (nv) {
            items.push({
              id: "errores_js",
              nivel: nv,
              msg: "Errores JS " + media + " por sesión (" + errores + " en " +
                sesUnicas + " sesiones)" +
                (erroresTop[0] ? " · top: " + String(erroresTop[0][0]).slice(0, 80) : ""),
              datos: {
                errores,
                sesiones: sesUnicas,
                media,
                top: erroresTop[0] ? erroresTop[0][0] : null,
              },
            });
          }
        }
        // 3 · vr_cortas — sesiones VR de <60 s = posible crash al entrar
        //     (cerradas por vr_end o fechadas por ping; las abiertas sin dur
        //     no cuentan porque aún no se sabe cuánto durarán)
        const vrFin = ciclosVR.filter(
          (c) => c.estado !== "abierta" && typeof c.dur === "number"
        );
        const vrCortas = vrFin.filter((c) => c.dur < 60);
        if (vrFin.length >= 3) {
          const pct = Math.round((vrCortas.length / vrFin.length) * 100);
          const nv = pct >= 50 ? "rojo" : pct >= 25 ? "amarillo" : null;
          if (nv) {
            items.push({
              id: "vr_cortas",
              nivel: nv,
              msg: pct + "% de las sesiones VR duran <60 s (posible crash al entrar)",
              datos: { cortas: vrCortas.length, cerradas: vrFin.length, pct },
            });
          }
        }
        // 4 · sin_sonido (M5b) — señales de audio roto por sesión:
        //     ≥1 amarillo · ≥3 rojo (misma regla que errores_js)
        if (sonidoRow && sonidoRow.n > 0 && sesUnicas > 0) {
          const mediaS = Math.round((sonidoRow.n / sesUnicas) * 10) / 10;
          const nvS = mediaS >= 3 ? "rojo" : mediaS >= 1 ? "amarillo" : null;
          if (nvS) {
            items.push({
              id: "sin_sonido",
              nivel: nvS,
              msg: "Golpes sin sonido: " + sonidoRow.n +
                " señal(es) de audio roto en " + sesUnicas + " sesiones (" +
                mediaS + " por sesión)",
              datos: { senales: sonidoRow.n, sesiones: sesUnicas, media: mediaS },
            });
          }
        }
        const peso = { rojo: 2, amarillo: 1 };
        const nivel = items.reduce(
          (a, i) => (peso[i.nivel] > (peso[a] || 0) ? i.nivel : a),
          "verde"
        );
        return { nivel, items };
      })();

      // ── RETENCIÓN (r46 · D1/D7/D30) y DESBLOQUEOS (r46) — campos nuevos
      //    y tolerantes del resumen: sin datos de pid el panel muestra
      //    «sin datos» y nada se rompe.
      //    Retención por pid: primer día visto, días activos, y retorno el
      //    día +1 / dentro de la semana / dentro del mes. Con la identidad
      //    de la 3.6.139 la muestra crece sola al jugar.
      const retFilas = (
        await env.DB
          .prepare(
            "SELECT json_extract(json,'$.pid') pid, date(t/1000,'unixepoch') d " +
              "FROM eventos WHERE json_extract(json,'$.pid') IS NOT NULL AND " +
              "json_extract(json,'$.pid') != '' AND t IS NOT NULL " +
              "GROUP BY pid, d LIMIT 5000"
          )
          .all()
      ).results;
      const diasPorPid = new Map();
      for (const r of retFilas) {
        if (!diasPorPid.has(r.pid)) diasPorPid.set(r.pid, []);
        diasPorPid.get(r.pid).push(r.d);
      }
      const retencion = (() => {
        const hoy = new Date().toISOString().slice(0, 10);
        const msDia = 86400000;
        let eleg1 = 0, vol1 = 0, eleg7 = 0, vol7 = 0, eleg30 = 0, vol30 = 0;
        let recurrentes = 0;
        for (const [, dias] of diasPorPid) {
          if (dias.length > 1) recurrentes++;
          const ds = dias.slice().sort();
          const d0 = new Date(ds[0] + "T00:00:00Z").getTime();
          const set = new Set(dias);
          const diasVivos = Math.floor((Date.now() - d0) / msDia);
          if (diasVivos >= 1) {
            eleg1++;
            if (set.has(new Date(d0 + msDia).toISOString().slice(0, 10))) vol1++;
          }
          if (diasVivos >= 7) {
            eleg7++;
            for (let k = 2; k <= 7; k++) {
              if (set.has(new Date(d0 + k * msDia).toISOString().slice(0, 10))) { vol7++; break; }
            }
          }
          if (diasVivos >= 30) {
            eleg30++;
            for (let k = 8; k <= 30; k++) {
              if (set.has(new Date(d0 + k * msDia).toISOString().slice(0, 10))) { vol30++; break; }
            }
          }
        }
        void hoy;
        const pct = (v, e) => (e > 0 ? Math.round((v / e) * 100) : null);
        return {
          jugadores: diasPorPid.size,
          recurrentes: diasPorPid.size ? Math.round((recurrentes / diasPorPid.size) * 100) : null,
          d1: pct(vol1, eleg1), muestra1: eleg1,
          d7: pct(vol7, eleg7), muestra7: eleg7,
          d30: pct(vol30, eleg30), muestra30: eleg30,
        };
      })();
      const logrosTop = (
        await env.DB
          .prepare(
            "SELECT json_extract(json,'$.k') logro, COUNT(*) n FROM eventos " +
              "WHERE e='logro' AND json_extract(json,'$.k') IS NOT NULL" +
              suf + " GROUP BY logro ORDER BY n DESC LIMIT 24"
          )
          .bind(...arg)
          .all()
      ).results.map((r) => [r.logro, r.n]);

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
        retencion,
        logrosTop,
        alarmas,
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
      // ronda 42 · ?dias=N → retención: purga SÓLO lo anterior a N días
      // (rec < llegada). Con ?sid= acota a esa sesión. Sin filtros → total.
      const diasD = parseInt(url.searchParams.get("dias"), 10);
      const r = sid
        ? await env.DB.prepare("DELETE FROM eventos WHERE instr(sid, ?) > 0").bind(sid).run()
        : Number.isFinite(diasD) && diasD > 0
          ? await env.DB
              .prepare("DELETE FROM eventos WHERE rec < ?")
              .bind(Date.now() - diasD * 86400000)
              .run()
          : await env.DB.prepare("DELETE FROM eventos").run();
      return json({ ok: true, borrados: r.meta ? r.meta.changes : 0, ts: Date.now() });
    }

    return json({ ok: false, error: "ruta o método desconocido — usa /api/tele" }, 404);
  },
};
