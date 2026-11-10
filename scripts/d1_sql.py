#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · CONSOLA SQL DIRECTA contra la D1 de producción (r42).

CONTROL ABSOLUTO: consulta/purga la base «crazypp-tele» por la API de
Cloudflare SIN pasar por el worker (independiente de CLAVE y del servicio).

Uso:
    python3 scripts/d1_sql.py "SELECT e, COUNT(*) n FROM eventos GROUP BY e"
    python3 scripts/d1_sql.py --escritura "DELETE FROM eventos WHERE rec < 1730000000000"
    python3 scripts/d1_sql.py --tablas        # esquema + conteos rápidos

Notas:
  · El token vive en scripts/worker-tele/.cf-token (gitignored). NUNCA se
    imprime.
  · Sin --escritura sólo se permiten sentencias SELECT (cinturón de
    seguridad).
  · La API de api.cloudflare.com NO bloquea urllib (el bloqueo 1010 es de
    workers.dev), así que vamos directos con urllib.
"""
import json
import os
import re
import ssl
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F_TOKEN = os.path.join(RAIZ, "scripts", "worker-tele", ".cf-token")
F_DBID = os.path.join(RAIZ, "scripts", "worker-tele", ".d1-id")
NOMBRE_D1 = "crazypp-tele"
API = "https://api.cloudflare.com/client/v4"


def lee_token():
    if not os.path.exists(F_TOKEN):
        sys.exit(f"✗ no existe {F_TOKEN}")
    with open(F_TOKEN, "r", encoding="utf-8") as f:
        t = f.read().strip()
    if not t:
        sys.exit("✗ el fichero de token está vacío")
    return t


def req(metodo, ruta, token, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    r = urllib.request.Request(API + ruta, data=datos, method=metodo)
    r.add_header("Authorization", f"Bearer {token}")
    if datos is not None:
        r.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(r, timeout=45,
                                context=ssl.create_default_context()) as w:
        return json.loads(w.read().decode("utf-8", "replace"))


def exige(j, contexto):
    if not j or j.get("success") is not True:
        errs = "; ".join(
            f"{e.get('code')}: {e.get('message')}" for e in (j.get("errors") or [])
        ) if j else "respuesta vacía"
        sys.exit(f"✗ {contexto}: {errs}")
    return j["result"]


def database_id(token):
    # caché local (ahorra dos llamadas por invocación)
    try:
        with open(F_DBID, "r", encoding="utf-8") as f:
            uid = f.read().strip()
        if re.fullmatch(r"[0-9a-f-]{32}", uid):
            return uid
    except FileNotFoundError:
        pass
    j = req("GET", "/accounts?per_page=5", token)
    cuentas = exige(j, "listar cuentas")
    if not cuentas:
        sys.exit("✗ el token no ve ninguna cuenta")
    acc = cuentas[0]["id"]
    j = req("GET", f"/accounts/{acc}/d1/database?per_page=50", token)
    dbs = exige(j, "listar bases D1")
    db = next((b for b in dbs if b.get("name") == NOMBRE_D1), None)
    if not db:
        sys.exit(f"✗ no encuentro la base «{NOMBRE_D1}»")
    with open(F_DBID, "w", encoding="utf-8") as f:
        f.write(db["uuid"])
    return db["uuid"]


def imprime(resultados):
    for res in resultados:
        filas = res.get("results") or []
        if not filas:
            print("(0 fila(s))\n")
            continue
        if isinstance(filas[0], dict):
            cols = list(filas[0].keys())
            matriz = [[f.get(c) for c in cols] for f in filas]
        else:
            cols = res.get("columns") or []
            matriz = filas
        anchos = [len(str(c)) for c in cols]
        for fila in matriz:
            for i, v in enumerate(fila):
                anchos[i] = min(60, max(anchos[i], len(str(v))))
        print(" | ".join(str(c).ljust(anchos[i]) for i, c in enumerate(cols)))
        print("-+-".join("-" * a for a in anchos))
        for fila in matriz:
            print(" | ".join(str(v).ljust(anchos[i])[:60]
                             for i, v in enumerate(fila)))
        print(f"({len(matriz)} fila(s))\n")


def main():
    args = sys.argv[1:]
    escritura = "--escritura" in args
    tablas = "--tablas" in args
    sentencias = [a for a in args if not a.startswith("--")]
    token = lee_token()
    uid = database_id(token)

    if tablas:
        sentencias = [
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name",
            "SELECT COUNT(*) AS eventos_totales FROM eventos",
            "SELECT e, COUNT(*) n FROM eventos GROUP BY e ORDER BY n DESC LIMIT 25",
            "SELECT MAX(rec) AS ultimo_lote_ms FROM eventos",
        ]
    if not sentencias:
        sys.exit(__doc__)
    for s in sentencias:
        if not escritura and not re.match(r"(?is)\s*SELECT\b", s.strip()):
            sys.exit("✗ sin --escritura sólo se permiten SELECT")

    acc = _cuenta(token)
    for s in sentencias:
        j = req("POST", f"/accounts/{acc}/d1/database/{uid}/query", token, {"sql": s})
        res = exige(j, "consulta D1")
        print(f"== {s[:100]}")
        imprime(res if isinstance(res, list) else [res])


def _cuenta(token):
    j = req("GET", "/accounts?per_page=5", token)
    return exige(j, "listar cuentas")[0]["id"]


if __name__ == "__main__":
    main()
