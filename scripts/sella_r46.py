#!/usr/bin/env python3
"""SELLA R46 · v3.6.139-SDK6 (FASE 141) — re-sella el golden tras los cambios
legítimos de src/ de esta ronda (r46):

  · c00_pre_three.js  — gobernador de telemetría (__PP_TELE.partida + hold)
  · c12_pingponggame.js — declara partida online viva al gobernador (animate)
  · c06_logros_stats_ia_rival.js — evento 'logro' en unlock() (desbloqueos)
  · (r45, sesión anterior, ya en el build: candado.png, constelación de palas,
    skin de pala por HELLO v2 `sp`, perfil/resultado para rankings mundiales)
  · worker-tele v3 — ?rank=1 · retencion · logrosTop (probado 102/0 en local)
  · telemetria.html — secciones Retención + Desbloqueos de logros

Pasos: build_game.py --escribir → golden nuevo (GOLDEN_SHA256.txt + VERSION.json
golden/tamano) → contra-verificación BYTE-EXACTO → qa_version.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GAME = RAIZ / "public" / "game.html"
GOLDEN = RAIZ / "src" / "game" / "GOLDEN_SHA256.txt"
VJSON = RAIZ / "src" / "game" / "VERSION.json"

NOTA = ("# SHA256 del game.html que produjo esta división (3.6.139-SDK6, fase 141 · "
        "La vitrina del cielo — candado del dueño, constelación de palas y rankings "
        "mundiales; re-sellado por sella_r46.py tras el gobernador de telemetría, "
        "el evento 'logro' y el worker v3 ?rank=1/retención/logrosTop)\n")


def main() -> int:
    # 1. build definitivo
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "build_game.py"), "--escribir"],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout[-400:])
    if r.returncode != 0:
        sys.stdout.write(r.stderr)
        return 1

    # 2. golden nuevo
    sha = hashlib.sha256(GAME.read_bytes()).hexdigest()
    tam = GAME.stat().st_size
    GOLDEN.write_text(NOTA + sha + "\n", encoding="utf-8")
    vdat = json.loads(VJSON.read_text(encoding="utf-8"))
    vdat["golden"] = sha
    vdat["tamano"] = tam
    VJSON.write_text(json.dumps(vdat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"· golden nuevo: {sha[:16]}… ({tam:,} B) · VERSION.json actualizado")

    # 3. contra-verificación BYTE-EXACTO
    r2 = subprocess.run([sys.executable, str(RAIZ / "scripts" / "build_game.py")],
                        capture_output=True, text=True)
    exacto = "BYTE-EXACTO" in r2.stdout
    print("· contra-verificación BYTE-EXACTO:", "OK" if exacto else "FALLO")
    if not exacto:
        sys.stdout.write(r2.stdout[-400:])
        return 1

    # 4. qa_version
    r3 = subprocess.run([sys.executable, str(RAIZ / "scripts" / "qa_version.py")],
                        capture_output=True, text=True)
    cola = [l for l in r3.stdout.splitlines() if "RESULTADO" in l or "FALLO" in l]
    sys.stdout.write("\n".join(cola[-8:]) + "\n")
    return 0 if "0 FALLOS" in r3.stdout else 1


if __name__ == "__main__":
    sys.exit(main())
