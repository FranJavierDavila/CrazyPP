import { NextRequest, NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

/**
 * CRAZY PING PONG · RECEPTOR LOCAL DE TELEMETRÍA (ronda 6 · roadmap P1)
 *
 * Hermano pequeño del Worker de Cloudflare de producción, pero COMPLETO:
 *  · POST acepta el lote del juego EN AMBOS formatos (tolerante):
 *      - wrapper {"app":"crazy-pingpong","events":[…]}  ← __PP_TELE.flush()
 *      - array directo [ {e,…}, … ]                     ← champ_rank (Magia)
 *    por sendBeacon (text/plain) o fetch (application/json). El Worker de
 *    producción SOLO acepta el array (hallazgo ronda 6, ver
 *    scripts/telemetria_catalogo.json) — aquí no: mientras el fix del juego
 *    llega a una release, el receptor local admite los dos.
 *  · GET  ?resumen=1          → agregados (por evento, sesiones, fps, errores,
 *                               champ_rank, últimos 20, y desde ronda 9:
 *                               duraciones, vrDuracion, porDia, versiones)
 *                               con filtro opcional ?sid=
 *  · GET  ?eventos=N          → últimos N eventos crudos (filtro ?sid=)
 *  · GET  (sin params)        → latido {ok, total, ts}
 *  · DELETE ?sid=…            → purga (con o sin filtro)
 *  · OPTIONS                  → preflight CORS (paridad con el Worker)
 *
 * PRIVACIDAD (misma política que el juego): se guarda EXACTAMENTE el JSON del
 * evento — NUNCA IP, ni user-agent, ni cabeceras. Almacén: telemetria/
 * eventos.jsonl (git-ignorado) con rotación a .old al pasar ~8 MB.
 */

export const dynamic = "force-dynamic";

const DIR = path.join(process.cwd(), "telemetria");
const FILE = path.join(DIR, "eventos.jsonl");
const MAX_BYTES = 8 * 1024 * 1024; // rotación
const MAX_EVENTO = 2000; // bytes serializados por evento
const MAX_BODY = 256 * 1024;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "content-type",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};

type Ev = Record<string, unknown>;

/** Lee todo el JSONL (una línea = un evento con _rec de llegada). */
async function leer(): Promise<Ev[]> {
  try {
    const raw = await fs.readFile(FILE, "utf8");
    const out: Ev[] = [];
    for (const line of raw.split("\n")) {
      const s = line.trim();
      if (!s) continue;
      try {
        const o = JSON.parse(s) as Ev;
        if (o && typeof o === "object") out.push(o);
      } catch {
        /* línea corrupta: se ignora */
      }
    }
    return out;
  } catch {
    return [];
  }
}

/** Rotación simple: si el fichero pasa de MAX_BYTES → eventos.jsonl.old */
async function rotarSiToca() {
  try {
    const st = await fs.stat(FILE);
    if (st.size > MAX_BYTES) {
      await fs.rename(FILE, FILE + ".old");
    }
  } catch {
    /* no existe aún */
  }
}

/** Valida y normaliza un evento del lote. Devuelve null si es basura. */
function sanea(e: unknown): Ev | null {
  if (!e || typeof e !== "object" || Array.isArray(e)) return null;
  const o = e as Ev;
  if (typeof o.e !== "string" || !o.e.length || o.e.length > 40) return null;
  const t = o.t;
  if (t !== undefined && typeof t !== "number") return null;
  try {
    if (JSON.stringify(o).length > MAX_EVENTO) return null;
  } catch {
    return null;
  }
  // sello de llegada local (NO es PII: hora del servidor)
  return { ...o, _rec: Date.now() };
}

async function guarda(evs: unknown[]): Promise<number> {
  const buenos: string[] = [];
  for (const e of evs) {
    const r = sanea(e);
    if (r) buenos.push(JSON.stringify(r));
  }
  if (buenos.length) {
    await rotarSiToca();
    await fs.mkdir(DIR, { recursive: true });
    await fs.appendFile(FILE, buenos.join("\n") + "\n", "utf8");
  }
  return buenos.length;
}

function filtrarSid(list: Ev[], sid: string | null): Ev[] {
  if (!sid) return list;
  return list.filter(
    (e) => typeof e.sid === "string" && (e.sid as string).includes(sid)
  );
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: CORS });
}

export async function POST(req: NextRequest) {
  let crudo: string;
  try {
    crudo = await req.text();
  } catch {
    return NextResponse.json(
      { ok: false, error: "sin cuerpo" },
      { status: 400, headers: CORS }
    );
  }
  if (!crudo.length) {
    return NextResponse.json(
      { ok: false, error: "cuerpo vacío" },
      { status: 400, headers: CORS }
    );
  }
  if (crudo.length > MAX_BODY) {
    return NextResponse.json(
      { ok: false, error: "cuerpo demasiado grande" },
      { status: 413, headers: CORS }
    );
  }
  let json: unknown;
  try {
    json = JSON.parse(crudo); // sendBeacon llega como text/plain: se parsea igual
  } catch {
    return NextResponse.json(
      { ok: false, error: "json inválido" },
      { status: 400, headers: CORS }
    );
  }
  let evs: unknown[];
  if (Array.isArray(json)) evs = json;
  else if (json && typeof json === "object" && Array.isArray((json as Ev).events))
    evs = (json as Ev).events as unknown[];
  else
    return NextResponse.json(
      { ok: false, error: "se espera un array de eventos o {app,events}" },
      { status: 400, headers: CORS }
    );
  const n = await guarda(evs);
  return NextResponse.json(
    { ok: true, guardados: n, ts: Date.now() },
    { headers: CORS }
  );
}

export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams;
  const sid = sp.get("sid");
  const todos = filtrarSid(await leer(), sid);

  const nEventos = sp.get("eventos");
  if (nEventos !== null) {
    const n = Math.max(0, Math.min(500, parseInt(nEventos, 10) || 0));
    return NextResponse.json(
      { ok: true, eventos: todos.slice(-n), ts: Date.now() },
      { headers: CORS }
    );
  }

  if (sp.get("resumen") !== null) {
    const porEvento: Record<string, number> = {};
    const sesMap = new Map<
      string,
      { sid: string; primero: number; ultimo: number; n: number }
    >();
    const fps: number[] = [];
    const errores = new Map<string, number>();
    const champ: Record<
      string,
      { partidas: number; victorias: number; mejor: number; estrellas: number }
    > = {};
    let arranques24h = 0;
    const h24 = Date.now() - 24 * 3600 * 1000;

    // ronda 9 (análisis de venta) — paridad con el worker de producción
    const durs: number[] = [];
    const vrDurs: number[] = [];
    const porDiaMap = new Map<
      string,
      { eventos: number; boots: number; sids: Set<string> }
    >();
    const verMap = new Map<string, { eventos: number; sids: Set<string> }>();

    for (const e of todos) {
      const k = String(e.e ?? "?");
      porEvento[k] = (porEvento[k] || 0) + 1;
      const t =
        typeof e.t === "number" ? e.t : typeof e._rec === "number" ? e._rec : 0;
      const s = String(e.sid ?? "-");
      const prev = sesMap.get(s);
      sesMap.set(s, {
        sid: s,
        primero: prev ? Math.min(prev.primero, t) : t,
        ultimo: prev ? Math.max(prev.ultimo, t) : t,
        n: (prev?.n || 0) + 1,
      });
      if (k === "boot" && t >= h24) arranques24h++;
      if (k === "vr_end" && typeof e.fps === "number") fps.push(e.fps as number);
      if (k === "error" && typeof e.m === "string")
        errores.set(e.m, (errores.get(e.m) || 0) + 1);
      if (k === "champ_rank" && typeof e.champ === "string") {
        const c = (champ[e.champ] ||= {
          partidas: 0,
          victorias: 0,
          mejor: 0,
          estrellas: 0,
        });
        c.partidas++;
        if (e.win === true) c.victorias++;
        if (typeof e.score === "number")
          c.mejor = Math.max(c.mejor, e.score as number);
        if (typeof e.stars === "number") c.estrellas += e.stars as number;
      }
      // ronda 9
      if (k === "page_close" && typeof e.dur === "number") durs.push(e.dur as number);
      if (k === "vr_end" && typeof e.dur === "number") vrDurs.push(e.dur as number);
      if (typeof e.t === "number" && (e.t as number) > 0) {
        const dia = new Date(e.t as number).toISOString().slice(0, 10);
        let d = porDiaMap.get(dia);
        if (!d) {
          d = { eventos: 0, boots: 0, sids: new Set<string>() };
          porDiaMap.set(dia, d);
        }
        d.eventos++;
        if (k === "boot") {
          d.boots++;
          if (s !== "-") d.sids.add(s);
        }
      }
      const v = typeof e.v === "string" ? e.v : "-";
      let vv = verMap.get(v);
      if (!vv) {
        vv = { eventos: 0, sids: new Set<string>() };
        verMap.set(v, vv);
      }
      vv.eventos++;
      vv.sids.add(s);
    }

    const sesiones = [...sesMap.values()]
      .sort((a, b) => b.ultimo - a.ultimo)
      .slice(0, 50);
    const erroresTop = [...errores.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8);
    const fpsMedio = fps.length
      ? Math.round((fps.reduce((a, b) => a + b, 0) / fps.length) * 10) / 10
      : null;

    const statDur = (a: number[]) =>
      a.length
        ? {
            media: Math.round(a.reduce((x, y) => x + y, 0) / a.length),
            max: Math.round(Math.max(...a)),
            n: a.length,
          }
        : { media: null, max: null, n: 0 };
    const porDia = [...porDiaMap.entries()]
      .sort((a, b) => (a[0] < b[0] ? 1 : -1))
      .slice(0, 30)
      .map(([dia, d]) => ({
        dia,
        eventos: d.eventos,
        boots: d.boots,
        sesiones: d.sids.size,
      }));
    const versiones = [...verMap.entries()]
      .map(([v, x]) => ({ v, eventos: x.eventos, sesiones: x.sids.size }))
      .sort((a, b) => b.eventos - a.eventos)
      .slice(0, 12);

    return NextResponse.json(
      {
        ok: true,
        ts: Date.now(),
        total: todos.length,
        sesionesUnicas: sesMap.size,
        arranques24h,
        porEvento,
        sesiones,
        fps: { medio: fpsMedio, muestras: fps.length },
        erroresTop,
        champRank: champ,
        ultimos: todos.slice(-20),
        duraciones: statDur(durs),
        vrDuracion: statDur(vrDurs),
        porDia,
        versiones,
        almacen: "telemetria/eventos.jsonl",
      },
      { headers: CORS }
    );
  }

  return NextResponse.json(
    { ok: true, total: todos.length, ts: Date.now() },
    { headers: CORS }
  );
}

export async function DELETE(req: NextRequest) {
  const sid = req.nextUrl.searchParams.get("sid");
  const todos = await leer();
  // quedan = los que NO casan con el filtro (sin ?sid= → purga total)
  const quedan = sid
    ? todos.filter(
        (e) => !(typeof e.sid === "string" && (e.sid as string).includes(sid))
      )
    : [];
  const borrados = todos.length - quedan.length;
  if (borrados > 0) {
    await fs.mkdir(DIR, { recursive: true });
    await fs.writeFile(
      FILE,
      quedan.map((e) => JSON.stringify(e)).join("\n") +
        (quedan.length ? "\n" : ""),
      "utf8"
    );
  }
  return NextResponse.json(
    { ok: true, borrados, ts: Date.now() },
    { headers: CORS }
  );
}
