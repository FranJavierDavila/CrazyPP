#!/usr/bin/env python3
"""
CRAZY PING PONG · Despliegue AUTOMÁTICO del worker de telemetría (ronda 8)
===========================================================================

Hace TODO con un API token de Cloudflare:
  1. Verifica el token (GET /user/tokens/verify)
  2. Localiza la cuenta (o pide CF_ACCOUNT_ID si hay varias)
  3. Crea/reutiliza la base D1 «crazypp-tele»
  4. Sube el worker módulo (scripts/worker-tele/worker.js) con bindings:
       DB (D1) + CLAVE (secret_text)
  5. Asegura el subdomain workers.dev activado
  6. Verificación E2E real contra producción:
       latido · 403 sin clave · POST de prueba → 204 · resumen con clave →
       el evento de prueba está → DELETE por sid → total restaurado

USO
   export CF_API_TOKEN='...'          # token del dueño (permisos: Workers + D1)
   export CF_ACCOUNT_ID='...'         # solo si la cuenta tiene varias cuentas
   export TELE_CLAVE='...'            # opcional: clave de lectura del dueño
                                      # (si falta, se genera una fuerte)
   python3 scripts/deploy_worker.py

El token NUNCA se imprime. La CLAVE se muestra UNA vez y queda guardada en
scripts/worker-tele/.clave-produccion (en .gitignore, nunca se commitea).
Re-entrante: reutiliza la D1 existente y reemplaza el script del worker.
"""

import json
import os
import secrets
import ssl
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER_JS = os.path.join(RAIZ, "scripts", "worker-tele", "worker.js")
FICHERO_CLAVE = os.path.join(RAIZ, "scripts", "worker-tele", ".clave-produccion")
GITIGNORE = os.path.join(RAIZ, ".gitignore")

NOMBRE_SCRIPT = "crazypp-tele"
NOMBRE_D1 = "crazypp-tele"
BINDING_D1 = "DB"
VAR_CLAVE = "CLAVE"
COMPAT_DATE = "2024-09-01"

API = "https://api.cloudflare.com/client/v4"

pasos_ok = []


def paso(n, txt):
    print(f"\n== {n} · {txt}")


def ok(txt):
    print(f"   OK · {txt}")
    pasos_ok.append(txt)


def fallo(txt, det=None):
    print(f"\n   FALLO · {txt}")
    if det:
        print(f"   detalle: {det}")
    print("\nNada se rompió: el script es re-entrante, corrige y vuelve a lanzarlo.")
    sys.exit(1)


def req(metodo, ruta, token, cuerpo=None, ctype="application/json", crudo=None):
    """Petición a la API v4. Devuelve (status, json_dict|None)."""
    url = ruta if ruta.startswith("http") else API + ruta
    datos = crudo if crudo is not None else (
        json.dumps(cuerpo).encode() if cuerpo is not None else None
    )
    r = urllib.request.Request(url, data=datos, method=metodo)
    r.add_header("Authorization", f"Bearer {token}")
    if datos is not None:
        r.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(r, timeout=45, context=ssl.create_default_context()) as w:
            texto = w.read().decode("utf-8", "replace")
            try:
                return w.status, json.loads(texto)
            except json.JSONDecodeError:
                return w.status, {"_crudo": texto}
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            return e.code, None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        fallo("red contra la API de Cloudflare", str(e.reason) if hasattr(e, "reason") else str(e))


def exigir(status, j, contexto):
    if status >= 400 or not j or j.get("success") is not True:
        errs = None
        if j and isinstance(j.get("errors"), list):
            errs = "; ".join(f"{e.get('code')}: {e.get('message')}" for e in j["errors"])
        fallo(contexto, errs or f"HTTP {status}")


def multipart(worker_js, database_id, clave):
    """Construye el multipart del PUT del script módulo."""
    limite = "----cpp" + secrets.token_hex(12)
    meta = json.dumps({
        "main_module": "worker.js",
        "compatibility_date": COMPAT_DATE,
        "bindings": [
            {"type": "d1", "name": BINDING_D1, "id": database_id},
            {"type": "secret_text", "name": VAR_CLAVE, "text": clave},
        ],
    }).encode()
    mod = worker_js.encode()
    trozos = []
    for nombre, ctype, datos in (
        ("metadata", "application/json", meta),
        ("worker.js", "application/javascript+module", mod),
    ):
        trozos.append(
            f"--{limite}\r\nContent-Disposition: form-data; name=\"{nombre}\"; filename=\"{nombre}\"\r\n"
            f"Content-Type: {ctype}\r\n\r\n".encode() + datos + b"\r\n"
        )
    trozos.append(f"--{limite}--\r\n".encode())
    return b"".join(trozos), f"multipart/form-data; boundary={limite}"


def guarda_clave(clave):
    os.makedirs(os.path.dirname(FICHERO_CLAVE), exist_ok=True)
    with open(FICHERO_CLAVE, "w", encoding="utf-8") as f:
        f.write(clave + "\n")
    os.chmod(FICHERO_CLAVE, 0o600)
    # blindaje: la línea del fichero de clave nunca debe versionarse
    try:
        with open(GITIGNORE, "r+", encoding="utf-8") as g:
            contenido = g.read()
            if ".clave-produccion" not in contenido:
                g.seek(0, 2)
                if contenido and not contenido.endswith("\n"):
                    g.write("\n")
                g.write("# clave de lectura del worker de telemetría (NUNCA commitear)\n")
                g.write("scripts/worker-tele/.clave-produccion\n")
    except FileNotFoundError:
        pass


def main():
    print("=" * 74)
    print("CRAZY PING PONG · DESPLIEGUE AUTOMÁTICO DEL WORKER DE TELEMETRÍA (D1)")
    print("=" * 74)

    token = os.environ.get("CF_API_TOKEN", "").strip()
    if not token:
        print("\nFalta CF_API_TOKEN en el entorno.")
        print("El dueño crea el token en 30 s: dash.cloudflare.com → My Profile →")
        print("API Tokens → Create Token → plantilla «Edit Cloudflare Workers» +")
        print("permiso extra Account › D1 › Edit → Continue → pegar el token.")
        sys.exit(2)
    if not os.path.exists(WORKER_JS):
        fallo("no existe worker.js", WORKER_JS)
    with open(WORKER_JS, "r", encoding="utf-8") as f:
        worker_js = f.read()

    # ── 1 · token
    paso(1, "verificando el API token")
    st, j = req("GET", "/user/tokens/verify", token)
    if st == 403 or st == 401:
        fallo("el token no es válido o está caducado", f"HTTP {st}")
    exigir(st, j, "verificación del token")
    ok(f"token activo ({(j.get('result') or {}).get('status')})")

    # ── 2 · cuenta
    paso(2, "localizando la cuenta")
    st, j = req("GET", "/accounts?per_page=10", token)
    exigir(st, j, "listar cuentas")
    cuentas = j.get("result") or []
    if not cuentas:
        fallo("el token no ve ninguna cuenta")
    cuenta_id = os.environ.get("CF_ACCOUNT_ID", "").strip()
    if cuenta_id:
        if not any(c["id"] == cuenta_id for c in cuentas):
            fallo("CF_ACCOUNT_ID no pertenece a este token")
    elif len(cuentas) > 1:
        print("   El token ve varias cuentas; exporta CF_ACCOUNT_ID con una de:")
        for c in cuentas:
            print(f"     {c['id']}  {c['name']}")
        sys.exit(2)
    else:
        cuenta_id = cuentas[0]["id"]
    nombre_cuenta = next((c["name"] for c in cuentas if c["id"] == cuenta_id), cuenta_id)
    ok(f"cuenta {nombre_cuenta}")

    # ── 3 · subdomain workers.dev
    paso(3, "subdomain workers.dev de la cuenta")
    st, j = req("GET", f"/accounts/{cuenta_id}/workers/subdomain", token)
    if st == 200 and (j.get("result") or {}).get("subdomain"):
        subdomain = j["result"]["subdomain"]
    else:
        subdomain = "escala3dcorreoia"  # conocido de producción; se valida en E2E
        print(f"   aviso: API no dio subdomain ({st}), se usa el conocido «{subdomain}»")
    base_url = f"https://{NOMBRE_SCRIPT}.{subdomain}.workers.dev"
    ok(base_url)

    # ── 4 · D1
    paso(4, f"base D1 «{NOMBRE_D1}»")
    st, j = req("GET", f"/accounts/{cuenta_id}/d1/database?per_page=50", token)
    exigir(st, j, "listar bases D1")
    db = next((b for b in (j.get("result") or []) if b.get("name") == NOMBRE_D1), None)
    if db:
        database_id = db["uuid"]
        ok(f"reutilizada (uuid {database_id[:12]}…)")
    else:
        st, j = req("POST", f"/accounts/{cuenta_id}/d1/database", token,
                    cuerpo={"name": NOMBRE_D1})
        exigir(st, j, "crear base D1")
        database_id = (j.get("result") or {}).get("uuid")
        ok(f"creada (uuid {database_id[:12]}…)")

    # ── 5 · clave de lectura
    paso(5, "clave de lectura (CLAVE)")
    clave = os.environ.get("TELE_CLAVE", "").strip()
    if clave:
        ok("clave del dueño (TELE_CLAVE)")
    elif os.path.exists(FICHERO_CLAVE):
        with open(FICHERO_CLAVE, "r", encoding="utf-8") as f:
            clave = f.read().strip()
        ok("clave reutilizada de .clave-produccion")
    else:
        clave = "cpp-" + secrets.token_urlsafe(18)
        ok("clave nueva generada")
    guarda_clave(clave)
    ok("guardada en scripts/worker-tele/.clave-produccion (600, gitignored)")

    # ── 6 · subir el worker
    paso(6, f"subiendo el worker «{NOMBRE_SCRIPT}» (módulo + bindings D1 y CLAVE)")
    cuerpo, ctype = multipart(worker_js, database_id, clave)
    st, j = req("PUT", f"/accounts/{cuenta_id}/workers/scripts/{NOMBRE_SCRIPT}", token,
                crudo=cuerpo, ctype=ctype)
    exigir(st, j, "subida del worker")
    ok("worker desplegado")

    # ── 7 · subdomain activado
    paso(7, "asegurando workers.dev activado")
    st, j = req("POST", f"/accounts/{cuenta_id}/workers/scripts/{NOMBRE_SCRIPT}/subdomain",
                token, cuerpo={"enabled": True, "previews_enabled": True})
    if st >= 400:
        print(f"   aviso: no se pudo tocar el subdomain (HTTP {st}) — se comprueba en el E2E")
    else:
        ok("subdomain habilitado")

    # ── 8 · verificación E2E en producción
    paso(8, "verificación E2E en producción")
    url = base_url + "/api/tele"

    def probe(metodo, extra="", cuerpo_b=None, ctype_p="text/plain"):
        r = urllib.request.Request(url + extra, data=cuerpo_b, method=metodo)
        if cuerpo_b is not None:
            r.add_header("Content-Type", ctype_p)
        try:
            with urllib.request.urlopen(r, timeout=30) as w:
                return w.status, w.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")

    st, txt = probe("GET")
    lat = json.loads(txt) if st == 200 and txt.startswith("{") else {}
    if st != 200 or lat.get("ok") is not True:
        fallo("latido público", f"HTTP {st} · {txt[:200]}")
    total_antes = lat.get("total")
    ok(f"latido {lat} (total={total_antes})")

    st, txt = probe("GET", "?resumen=1")
    if st != 403:
        fallo("resumen sin clave DEBE dar 403", f"HTTP {st} · {txt[:200]}")
    ok("resumen sin clave → 403 (protegido)")

    sonda = "deploy-probe-" + secrets.token_hex(6)
    lote = json.dumps([
        {"e": "deploy_prueba", "t": int(time.time() * 1000), "v": "ronda8-deploy",
         "sid": sonda, "fps": 60},
        {"e": "deploy_prueba", "t": int(time.time() * 1000), "v": "ronda8-deploy",
         "sid": sonda},
    ]).encode()
    st, txt = probe("POST", "", cuerpo_b=lote, ctype_p="application/json")
    if st != 204:
        fallo("POST del lote de prueba", f"HTTP {st} · {txt[:200]}")
    ok("POST lote de prueba → 204")

    st, txt = probe("GET", f"?resumen=1&clave={clave}")
    res = json.loads(txt) if st == 200 and txt.startswith("{") else {}
    n = (res.get("porEvento") or {}).get("deploy_prueba", 0)
    if st != 200 or res.get("ok") is not True or n < 2:
        fallo("resumen con clave no ve los eventos de prueba",
              f"HTTP {st} · {txt[:300]}")
    ok(f"resumen con clave → total={res.get('total')} · sesiones={res.get('sesionesUnicas')} "
       f"· porEvento.deploy_prueba={n} · almacen={res.get('almacen')}")

    st, txt = probe("DELETE", f"?sid={sonda}&clave={clave}")
    bor = json.loads(txt) if st == 200 and txt.startswith("{") else {}
    if st != 200 or (bor.get("borrados") or 0) < 2:
        fallo("purga por sid", f"HTTP {st} · {txt[:200]}")
    ok(f"DELETE por sid → borrados={bor.get('borrados')}")

    st, txt = probe("GET")
    lat2 = json.loads(txt) if st == 200 and txt.startswith("{") else {}
    if lat2.get("total") != total_antes:
        fallo("el total no se restauró tras la purga", f"{lat} → {lat2}")
    ok(f"latido restaurado (total={lat2.get('total')}) · producción limpia")

    # ── fin
    print("\n" + "=" * 74)
    print("DESPLIEGUE COMPLETO Y VERIFICADO EN PRODUCCIÓN")
    print("=" * 74)
    print(f"\n  URL del worker : {base_url}/api/tele")
    print(f"  CLAVE (léela UNA vez y guárdala en tu gestor de contraseñas):\n")
    print(f"      {clave}\n")
    print("  Siguiente paso (tuyo, 30 s): abre el panel /telemetria → botón")
    print("  «Producción (D1)» → pega esta CLAVE (se recuerda en el navegador).")
    print("  El test en casco será entonces la primera lectura real del visor.")
    print("\n  (esta clave también queda en scripts/worker-tele/.clave-produccion)")
    sys.exit(0)


if __name__ == "__main__":
    main()
