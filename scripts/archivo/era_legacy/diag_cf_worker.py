#!/usr/bin/env python3
"""diag_cf_worker.py — diagnóstico autoritativo del worker crazypp-tele por API.

1. Bindings REALES del worker desplegado (nombres/tipos; los secrets no
   devuelven valor).
2. sha256 del código desplegado vs scripts/worker-tele/worker.js local.
3. Estado de la base D1 crazypp-tele.
4. Consulta SQL directa a la D1 (SELECT COUNT(*) FROM eventos): prueba la
   base AL MARGEN del worker.
5. Tail del último error si el endpoint de observabilidad lo expone.

GIT-style: CF_API_TOKEN por entorno, nunca se imprime.
"""
import hashlib
import json
import os
import sys
import urllib.request

API = "https://api.cloudflare.com/client/v4"
TOKEN = os.environ.get("CF_API_TOKEN", "").strip()
if not TOKEN:
    sys.exit("✗ CF_API_TOKEN no está en el entorno")

REQ_H = {"Authorization": f"Bearer {TOKEN}",
         "Content-Type": "application/json"}


def req(metodo, ruta, cuerpo=None, ctype=None):
    pet = urllib.request.Request(API + ruta, method=metodo,
                                 data=json.dumps(cuerpo).encode() if cuerpo else None,
                                 headers={"Authorization": f"Bearer {TOKEN}",
                                          "Content-Type": ctype or "application/json"})
    try:
        with urllib.request.urlopen(pet, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


st, j = req("GET", "/accounts?per_page=10")
cuenta = (j.get("result") or [{}])[0].get("id")
if not cuenta:
    sys.exit("✗ el token no ve cuentas")
print(f"· cuenta {cuenta[:12]}…")

# ── 1 · bindings reales del worker ────────────────────────────────
st, j = req("GET", f"/accounts/{cuenta}/workers/scripts/crazypp-tele/settings")
if st != 200:
    print(f"✗ settings HTTP {st}: {json.dumps(j.get('errors', []))[:200]}")
    bindings = []
else:
    bindings = (j.get("result") or {}).get("bindings") or []
print("· bindings del worker desplegado:")
for b in bindings:
    extra = f" id={b.get('id', '')[:12]}…" if b.get("id") else ""
    texto = " (con text)" if b.get("text") else " (sin text)"
    print(f"   {b.get('type'):14s} {b.get('name')}{extra}{texto}")
d1 = next((b for b in bindings if b.get("type") == "d1"), None)

# ── 2 · código desplegado vs local ────────────────────────────────
pet = urllib.request.Request(
    f"{API}/accounts/{cuenta}/workers/scripts/crazypp-tele",
    headers={"Authorization": f"Bearer {TOKEN}"})
try:
    with urllib.request.urlopen(pet, timeout=30) as r:
        remoto = r.read()
    h_remoto = hashlib.sha256(remoto).hexdigest()
    with open("/home/z/my-project/scripts/worker-tele/worker.js", "rb") as f:
        h_local = hashlib.sha256(f.read()).hexdigest()
    print(f"· sha256 desplegado {h_remoto[:16]}… · local {h_local[:16]}… · "
          + ("IDÉNTICOS" if h_remoto == h_local else "DIFERENTES ⚠"))
except urllib.error.HTTPError as e:
    print(f"· código desplegado: HTTP {e.code} (no crítico)")

# ── 3 · estado de la D1 ───────────────────────────────────────────
if d1 and d1.get("id"):
    st, j = req("GET", f"/accounts/{cuenta}/d1/database/{d1['id']}")
    res = j.get("result") or {}
    if st == 200:
        print(f"· D1 «{res.get('name')}» estado={res.get('status', '?')} · "
              f"tamaño={res.get('file_size', '?')} · versión={res.get('version', '?')}")
    else:
        print(f"✗ D1 info HTTP {st}: {json.dumps(j.get('errors', []))[:200]}")

    # ── 4 · SQL directo al margen del worker ──────────────────────
    st, j = req("POST", f"/accounts/{cuenta}/d1/database/{d1['id']}/query",
                cuerpo={"sql": "SELECT COUNT(*) n FROM eventos"})
    res = j.get("result") or {}
    if st == 200 and res.get("rows"):
        print(f"· SQL directo: eventos = {res['rows'][0].get('n')} filas (¡la base responde!)")
    else:
        errs = "; ".join(f"{e.get('code')}: {e.get('message')}" for e in j.get("errors", []))
        print(f"✗ SQL directo HTTP {st}: {errs[:220]}")
        # ¿existe la tabla?
        st, j = req("POST", f"/accounts/{cuenta}/d1/database/{d1['id']}/query",
                    cuerpo={"sql": "SELECT name FROM sqlite_master WHERE type='table'"})
        res = j.get("result") or {}
        if st == 200 and res.get("rows"):
            tablas = [r.get("name") for r in res["rows"]]
            print(f"· tablas en la D1: {tablas}")
else:
    print("✗ el worker desplegado NO tiene binding D1")
