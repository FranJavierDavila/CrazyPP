#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_bq_p1_r121 — corrida de UNA pareja (P1 LAN) del banco bateria_multi_v3674
con los PUNTOS 3-4 (saca el invitado, rotación ITTF). Validación rápida del
flujo completo sin la manada de 6 páginas (el banco entero va aparte)."""
import asyncio
import importlib.util
import sys

from playwright.async_api import async_playwright

spec = importlib.util.spec_from_file_location("bq", "scripts/bateria_multi_v3674.py")
bq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bq)
bq.URL = "http://localhost:3000/game.html"   # el módulo lee sys.argv[1] como URL


async def main():
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    url, servidor = bq.arranca_servidor_si_hace_falta(bq.URL)
    try:
        async with async_playwright() as pw:
            r = await bq.jugar(pw, bq.PERFILES[idx], url)
            if isinstance(r, BaseException):
                raise r
    finally:
        if servidor is not None:
            try:
                servidor.terminate()
            except Exception:
                pass
    print(f"\n{bq.PERFILES[idx]['id']} (4 PUNTOS): {bq.ok} OK · {bq.fails} FALLOS", flush=True)
    sys.exit(0 if bq.fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
