#!/usr/bin/env python3
# r87 · MIGRACIÓN ONE-SHOT del esquema social de D1 (crazypp-tele):
#  la tabla `presencia` legacy (columna ts, de una intentona anterior) y
#  `invites` se retiran UNA VEZ y nacen con el contrato del worker actual.
#  El runtime NUNCA borra (los DROP por isolate se comían los latidos).
import json
import sys

sys.path.insert(0, "/home/z/my-project/scripts")
from deploy_worker import req  # noqa: E402

TOKEN = open("/home/z/my-project/scripts/worker-tele/.cf-token").read().strip()
UUID = "24ee07a2-c04b-475f-ba72-257d374c06e9"

SQL = [
    "DROP TABLE IF EXISTS presencia",
    "DROP TABLE IF EXISTS invites",
    """CREATE TABLE IF NOT EXISTS presencia (
         pid TEXT PRIMARY KEY,
         n TEXT, v TEXT, st TEXT, code TEXT,
         t INTEGER NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS idx_pres_t ON presencia(t)",
    """CREATE TABLE IF NOT EXISTS invitas (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         de TEXT NOT NULL, deN TEXT, para TEXT NOT NULL, code TEXT,
         t INTEGER NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS idx_inv_para ON invitas(para)",
    "CREATE INDEX IF NOT EXISTS idx_inv_t ON invitas(t)",
]

st, j = req("GET", "/accounts?per_page=10", TOKEN)
cuenta = j["result"][0]["id"]
for sql in SQL:
    st, res = req("POST", f"/accounts/{cuenta}/d1/database/{UUID}/query", TOKEN, {"sql": sql})
    ok = (res.get("result") or [{}])[0].get("success")
    print(("OK  " if ok else "FALLO ") + sql.replace("\n", " ")[:80])
st, res = req("POST", f"/accounts/{cuenta}/d1/database/{UUID}/query", TOKEN,
              {"sql": "SELECT name, sql FROM sqlite_master WHERE type IN ('table','index') AND name NOT LIKE 'sqlite%' AND name != '_cf_KV'"})
for row in (res.get("result") or [{}])[0].get("results", []):
    print("·", row.get("name"), "::", (row.get("sql") or "")[:100].replace("\n", " "))
print("MIGRACIÓN COMPLETA")
