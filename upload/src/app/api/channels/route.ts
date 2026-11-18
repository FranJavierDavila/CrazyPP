import { NextResponse } from "next/server";

/**
 * Proxy de respaldo de la guía CRAZY TV: si la petición llega al propio
 * Next (sin pasar por el gateway Caddy con XTransformPort), reenvía al
 * mini-servicio live-service (:3004). Con el gateway, Caddy ya enruta
 * /api/channels?XTransformPort=3004 directo al servicio y esta ruta ni
 * se entera.
 */
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const r = await fetch("http://localhost:3004/api/channels", {
      cache: "no-store",
    });
    const j = await r.json();
    return NextResponse.json(j);
  } catch {
    return NextResponse.json({ ok: false, channels: [], ts: Date.now() });
  }
}
