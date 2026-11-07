#!/usr/bin/env python3
"""Vuelca la telemetría de producción D1 a snapshots locales para informe.py.

Uso:
    python3 scripts/vuelca_tele.py [prefijo]

Crea:
    scripts/_eventos_<prefijo>.json   (eventos crudos, ?eventos=1)
    scripts/_resumen_<prefijo>.json   (agregado, ?resumen=1 con clave)

Notas del taller:
  · workers.dev bloquea la firma Python-urllib (error 1010) → SIEMPRE curl
    con UA de navegador (lección rondas 8 y 20).
  · La CLAVE vive en scripts/worker-tele/.clave-produccion (600, gitignored).
  · El resumen SIN clave debe dar 403 — aquí vamos con clave del dueño.
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele"
FICHERO_CLAVE = os.path.join(RAIZ, "scripts", "worker-tele", ".clave-produccion")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")


def curl(url):
    p = subprocess.run(
        ["curl", "-sS", "-m", "30", "-A", UA, url],
        capture_output=True, timeout=60,
    )
    return p.stdout.decode("utf-8", "replace")


def main():
    prefijo = sys.argv[1] if len(sys.argv) > 1 else "r23"
    clave = ""
    if os.path.exists(FICHERO_CLAVE):
        with open(FICHERO_CLAVE, "r", encoding="utf-8") as f:
            clave = f.read().strip()
    if not clave:
        print("FALTA CLAVE: scripts/worker-tele/.clave-produccion no existe")
        sys.exit(1)

    # eventos crudos (REQUIEREN clave; máx 500 por petición — lección worker)
    bruto = curl(URL + "?eventos=500&clave=" + clave)
    try:
        ev = json.loads(bruto)
    except ValueError:
        print("eventos: respuesta no JSON:", bruto[:200])
        sys.exit(1)
    if ev.get("ok") is not True:
        print("eventos: error del worker:", ev.get("error", bruto[:200]))
        sys.exit(1)
    eventos = ev.get("eventos") or ev.get("result") or ev
    n_ev = len(eventos) if isinstance(eventos, list) else -1
    ruta_ev = os.path.join(RAIZ, "scripts", f"_eventos_{prefijo}.json")
    with open(ruta_ev, "w", encoding="utf-8") as f:
        json.dump(eventos, f, ensure_ascii=False, indent=1)

    # resumen agregado (con clave)
    bruto_r = curl(URL + "?resumen=1&clave=" + clave)
    try:
        res = json.loads(bruto_r)
    except ValueError:
        print("resumen: respuesta no JSON:", bruto_r[:200])
        sys.exit(1)
    ruta_res = os.path.join(RAIZ, "scripts", f"_resumen_{prefijo}.json")
    with open(ruta_res, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)

    print(f"eventos → {ruta_ev}  (n={n_ev})")
    print(f"resumen → {ruta_res}  (ok={res.get('ok')}, total={res.get('total')})")


if __name__ == "__main__":
    main()
