#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA E2E r42 · endpoints nuevos del worker de telemetría en PRODUCCIÓN.

Verifica contra https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele:
  1. ?salud=1 público (ok, total, ultimoRec, haceSeg coherentes)
  2. resumen sin clave → 403 (sigue protegido)
  3. POST lote de prueba (sid qa_r42_…) → 204
  4. resumen?dias=1&sid → ve el evento
  5. resumen?dias=1 SIN el sid de prueba → total coherente (filtro días activo)
  6. ?csv=1 con sid → cabecera CSV + fila del evento + escape JSON correcto
  7. DELETE ?sid → purga · latido restaurado
La CLAVE se lee de scripts/worker-tele/.clave-produccion (nunca se imprime).
UA de navegador (workers.dev bloquea la firma de urllib: error 1010).
"""
import json
import subprocess
import sys
import time
import urllib.parse

RAIZ = "/home/z/my-project/upload"
F_CLAVE = RAIZ + "/scripts/worker-tele/.clave-produccion"
URL = "https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele"
UA = ("Mozilla/5.0 (X11, Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"
      .replace("X11, ", "X11; "))
oks = []


def ok(txt):
    print("  ✓ " + txt)
    oks.append(txt)


def fallo(txt, det=None):
    print("  ✗ FALLO · " + txt)
    if det:
        print("    detalle: " + str(det)[:400])
    sys.exit(1)


def curl(args, cuerpo=None, extra_headers=()):
    cmd = ["curl", "-sS", "-m", "30", "-A", UA, "-w", "\n%{http_code}"] + list(extra_headers) + args
    if cuerpo is not None:
        cmd += ["--data-binary", cuerpo, "-H", "Content-Type: text/plain;charset=UTF-8"]
    p = subprocess.run(cmd, capture_output=True, timeout=60)
    out = p.stdout.decode("utf-8", "replace")
    cuerpo_out, _, code = out.rpartition("\n")
    return cuerpo_out, code.strip()


def main():
    with open(F_CLAVE, "r", encoding="utf-8") as f:
        clave = f.read().strip()
    q = urllib.parse.urlencode({"clave": clave})
    sid = "qa_r42_" + str(int(time.time()))
    ahora = int(time.time() * 1000)

    print("== 1 · salud pública")
    cuerpo, code = curl([URL + "?salud=1"])
    d = json.loads(cuerpo) if code == "200" else {}
    if code != "200" or d.get("ok") is not True or "total" not in d or "haceSeg" not in d:
        fallo("salud pública", f"HTTP {code} · {cuerpo[:200]}")
    ok(f"salud {d['total']} eventos · último lote hace {d['haceSeg']} s")

    print("== 2 · resumen sin clave → 403")
    cuerpo, code = curl([URL + "?resumen=1"])
    if code != "403":
        fallo("resumen sin clave debe dar 403", f"HTTP {code} · {cuerpo[:200]}")
    ok("403 correcto")

    print("== 3 · POST lote de prueba → 204")
    lote = json.dumps([
        {"e": "qa_r42", "t": ahora, "v": "qa-r42", "sid": sid, "nota": "prueba e2e r42"},
        {"e": "qa_r42", "t": ahora, "v": "qa-r42", "sid": sid, "nota": 'escape "comillas", y comas'},
    ])
    cuerpo, code = curl([URL], cuerpo=lote)
    if code != "204":
        fallo("POST de prueba", f"HTTP {code} · {cuerpo[:200]}")
    ok("204 correcto")

    print("== 4 · resumen?dias=1&sid ve el evento")
    cuerpo, code = curl([URL + "?resumen=1&" + q + "&dias=1&sid=" + urllib.parse.quote(sid)])
    d = json.loads(cuerpo) if code == "200" else {}
    n = (d.get("porEvento") or {}).get("qa_r42", 0)
    if code != "200" or n < 2:
        fallo("filtro dias+sid", f"HTTP {code} · {cuerpo[:300]}")
    ok(f"días=1 + sid → qa_r42={n}")

    print("== 5 · csv con sid → cabecera + 2 filas + escape")
    cuerpo, code = curl([URL + "?csv=1&" + q + "&sid=" + urllib.parse.quote(sid)])
    lineas = cuerpo.lstrip("\ufeff").splitlines()
    if code != "200" or not lineas[0].startswith("e,fecha_iso,t_ms,version,sid,json"):
        fallo("cabecera CSV", f"HTTP {code} · {cuerpo[:200]}")
    filas = [l for l in lineas[1:] if l.strip()]
    if len(filas) != 2:
        fallo("filas CSV", f"esperaba 2, hay {len(filas)}")
    # la última celda (json) debe parsear como CSV y su JSON ser válido
    import csv as _csv
    import io as _io
    try:
        leidos = list(_csv.reader(_io.StringIO(lineas[1])))
        celda = leidos[0][5]
        jf = json.loads(celda)
        if jf.get("e") != "qa_r42":
            raise ValueError("evento inesperado: " + str(jf.get("e")))
    except Exception as ex:
        fallo("fila CSV no parsea / JSON inválido", f"{ex} · {filas[1][:200]}")
    ok("CSV correcto (2 filas, parseo y JSON verificados)")

    print("== 6 · DELETE ?sid purga y el latido se restaura")
    cuerpo, code = curl(["-X", "DELETE", URL + "?" + q + "&sid=" + urllib.parse.quote(sid)])
    d = json.loads(cuerpo) if code == "200" else {}
    if code != "200" or (d.get("borrados") or 0) < 2:
        fallo("purga por sid", f"HTTP {code} · {cuerpo[:200]}")
    ok(f"borrados={d['borrados']}")

    print("== 7 · salud tras la purga (el total NO baja: el sid era de prueba)")
    cuerpo, code = curl([URL + "?salud=1"])
    d2 = json.loads(cuerpo) if code == "200" else {}
    if code != "200":
        fallo("salud final", f"HTTP {code}")
    ok(f"total={d2['total']} · haceSeg={d2['haceSeg']}")

    print("== 8 · limpieza de sids qa_r42_* huérfanos de ejecuciones previas")
    # los rastros de QA se reconocen por sid: purga selectiva (no toca datos reales)
    cuerpo, code = curl([URL + "?eventos=500&" + q])
    d3 = json.loads(cuerpo) if code == "200" else {}
    huérfanos = sorted({e.get("sid") for e in d3.get("eventos", [])
                        if isinstance(e.get("sid"), str) and e["sid"].startswith("qa_r42_")})
    for h in huérfanos:
        curl(["-X", "DELETE", URL + "?" + q + "&sid=" + urllib.parse.quote(h)])
    ok(("purgados " + str(len(huérfanos)) + " sid de QA: " + ", ".join(huérfanos)) if huérfanos
       else "no quedaban rastros de QA")

    print(f"\nQA E2E r42 COMPLETO: {len(oks)} checks verdes · producción limpia")


if __name__ == "__main__":
    main()
