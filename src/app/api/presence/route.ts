import { NextRequest, NextResponse } from "next/server";

/**
 * CRAZY PING PONG · RECEPTOR LOCAL DE PRESENCIA (v3.6.28-LIVE1)
 * Hermano pequeño del Worker de Cloudflare de producción — SOLO desarrollo
 * y QA (localhost). Almacén en memoria del proceso del dev server.
 *
 *   POST  /api/presence  → latido {pid,n,st,c,v} → {ok,online,jugando,
 *                          jugadores[],invites[]} (mismo contrato del Worker)
 *   GET   /api/presence  → {ok,online,ts}
 *
 * PRIVACIDAD (igual que producción): se guarda SOLO el JSON del juego —
 * NUNCA IP, ni user-agent, ni cabeceras.
 */

const TTL_JUGADOR = 70000;
const TTL_INVITE = 120000;

type Estado = { n: string; st: string; c: string; ts: number };
type Invitacion = { de: string; n: string; para: string; c: string; ts: number };

const g = globalThis as unknown as {
  __ppPresence?: Map<string, Estado>;
  __ppInvites?: Map<string, Invitacion>;
};
const presencia: Map<string, Estado> = (g.__ppPresence ||= new Map());
const invites: Map<string, Invitacion> = (g.__ppInvites ||= new Map());

function limpia(ahora: number) {
  for (const [k, v] of presencia) if (ahora - v.ts > TTL_JUGADOR) presencia.delete(k);
  for (const [k, v] of invites) if (ahora - v.ts > TTL_INVITE) invites.delete(k);
}

export const dynamic = "force-dynamic";

export async function GET() {
  const ahora = Date.now();
  limpia(ahora);
  return NextResponse.json({ ok: true, online: presencia.size, ts: ahora });
}

export async function POST(req: NextRequest) {
  let b: Record<string, unknown> = {};
  try {
    b = await req.json();
  } catch {
    return NextResponse.json({ ok: false, error: "json" }, { status: 400 });
  }
  const pid = String(b.pid ?? "").replace(/[^A-Za-z0-9-]/g, "");
  if (pid.length < 6) {
    return NextResponse.json({ ok: false, error: "pid" }, { status: 400 });
  }
  const st = ["menu", "sala", "partida", "off"].includes(String(b.st))
    ? String(b.st)
    : "menu";
  const ahora = Date.now();
  limpia(ahora);
  if (st === "off") {
    presencia.delete(pid);
    return NextResponse.json({ ok: true, online: presencia.size });
  }
  const n =
    String(b.n ?? "")
      .replace(/[^\w \-.]/g, "")
      .trim()
      .slice(0, 12) || "P" + pid.replace(/[^A-Za-z0-9]/g, "").slice(-4).toUpperCase();
  const c = String(b.c ?? "")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "")
    .slice(0, 5);
  presencia.set(pid, { n, st, c, ts: ahora });
  const jugadores = [...presencia.entries()]
    .filter(([k]) => k !== pid)
    .map(([pid2, v]) => ({ pid: pid2, n: v.n, st: v.st, c: v.c }))
    .slice(0, 8);
  const mias = [...invites.entries()]
    .filter(([, v]) => v.para === pid)
    .map(([id, v]) => ({ id, n: v.n, c: v.c, ts: v.ts }))
    .slice(0, 5);
  return NextResponse.json({
    ok: true,
    online: presencia.size,
    jugando: [...presencia.values()].filter((v) => v.st === "partida").length,
    jugadores,
    invites: mias,
    ts: ahora,
  });
}
