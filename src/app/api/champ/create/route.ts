import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { writeFile, unlink } from 'fs/promises';
import path from 'path';
import os from 'os';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * API del asistente de campeonatos (game/editor.html → Fase 7).
 * Recibe el paquete { package: manifest } y delega en tools/install_champ.py:
 * UNA sola implementación del validador (§7 de docs/ARQUITECTURA_CAMPEONATOS.md)
 * para el navegador, el CLI y la API. El campeonato queda en DRAFT.
 */
export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ ok: false, error: 'JSON inválido' }, { status: 400 });
  }
  const pkg = (body as { package?: unknown })?.package;
  if (!pkg || typeof pkg !== 'object') {
    return NextResponse.json({ ok: false, error: 'Falta el objeto "package"' }, { status: 400 });
  }
  const tmp = path.join(os.tmpdir(), `champ-pkg-${Date.now()}.json`);
  try {
    await writeFile(tmp, JSON.stringify({ package: pkg }, null, 2), 'utf8');
    const result = await new Promise<{ code: number; out: string }>((resolve) => {
      const p = spawn('python3', [path.join(process.cwd(), 'tools', 'install_champ.py'), 'install', tmp], {
        cwd: process.cwd(),
        timeout: 300_000,
      });
      let out = '';
      p.stdout.on('data', (d) => { out += d; });
      p.stderr.on('data', (d) => { out += d; });
      p.on('close', (code) => resolve({ code: code ?? 1, out }));
      p.on('error', (e) => resolve({ code: 1, out: String(e) }));
    });
    const ok = result.code === 0 && /instalado en estado DRAFT/.test(result.out);
    return NextResponse.json({
      ok,
      message: ok
        ? `Campeonato "${(pkg as { id?: string }).id}" instalado en BORRADOR (previsualízalo con /?champ=${(pkg as { id?: string }).id})`
        : 'El instalador rechazó el paquete (ver log)',
      log: result.out.slice(-4000),
    });
  } catch (e) {
    return NextResponse.json({ ok: false, error: String(e) }, { status: 500 });
  } finally {
    try { await unlink(tmp); } catch { /* */ }
  }
}
