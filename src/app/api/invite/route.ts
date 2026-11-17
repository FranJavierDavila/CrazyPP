import { NextRequest, NextResponse } from "next/server";

/**
 * CRAZY PING PONG · RECEPTOR LOCAL DE INVITACIONES (v3.6.28-LIVE1)
 * Hermano pequeño del Worker de Cloudflare de producción — SOLO desarrollo
 * y QA (localhost). Memoria compartida con /api/presence.
 *
 *   POST   /api/invite  → {de,n,para,sala} → {ok,id}
 *   DELETE /api/invite  → ?id=&para= (la consume el receptor) | ?de= (la
 *                          purga el emisor al cerrar su sala)
 */

type Invitacion = { de: string; n: string; para: string; c: string; ts: number };

const g = globalThis as unknown as { __ppInvites?: Map<string, Invitacion> };
const invites: Map<string, Invitacion> = (g.__ppInvites ||= new Map());

const TTL_INVITE = 120000;

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  let b: Record<string, unknown> = {};
  try {
    b = await req.json();
  } catch {
    return NextResponse.json({ ok: false, error: "json" }, { status: 400 });
  }
  const de = String(b.de ?? "").replace(/[^A-Za-z0-9-]/g, "");
  const para = String(b.para ?? "").replace(/[^A-Za-z0-9-]/g, "");
  const sala = String(b.sala ?? "")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "");
  if (de.length < 6 || para.length < 6 || sala.length !== 5 || de === para) {
    return NextResponse.json({ ok: false, error: "datos" }, { status: 400 });
  }
  const ahora = Date.now();
  for (const [k, v] of invites) if (ahora - v.ts > TTL_INVITE) invites.delete(k);
  // tope de 5 vivas por destinatario: caen las más viejas
  const delDestino = [...invites.entries()]
    .filter(([, v]) => v.para === para)
    .sort((x, y) => x[1].ts - y[1].ts);
  while (delDestino.length >= 5) {
    const vieja = delDestino.shift()!;
    invites.delete(vieja[0]);
  }
  const n =
    String(b.n ?? "")
      .replace(/[^\w \-.]/g, "")
      .trim()
      .slice(0, 12) || "RIVAL";
  const id =
    typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID()
      : "inv-" + ahora + "-" + Math.floor(Math.random() * 1e9);
  invites.set(id, { de, n, para, c: sala, ts: ahora });
  return NextResponse.json({ ok: true, id, ts: ahora });
}

export async function DELETE(req: NextRequest) {
  const url = new URL(req.url);
  const id = (url.searchParams.get("id") ?? "").replace(/[^A-Za-z0-9-]/g, "");
  const para = (url.searchParams.get("para") ?? "").replace(/[^A-Za-z0-9-]/g, "");
  const de = (url.searchParams.get("de") ?? "").replace(/[^A-Za-z0-9-]/g, "");
  if (id && para) {
    const inv = invites.get(id);
    if (inv && inv.para === para) invites.delete(id);
  } else if (de) {
    for (const [k, v] of invites) if (v.de === de) invites.delete(k);
  }
  return NextResponse.json({ ok: true, ts: Date.now() });
}
