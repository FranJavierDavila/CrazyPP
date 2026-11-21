#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnóstico r42 · telemetría de producción.

1. GET  ?eventos=50&clave  → qué hay en D1 (fechas, versiones, sids)
2. POST lote diagnóstico    → ¿la ingestión acepta? (sid diag_r42_…)
3. GET  ?resumen=1&clave   → el estado que vería el panel
4. DELETE ?sid=diag_r42_…  → limpieza del evento de prueba
La CLAVE nunca se imprime. UA de navegador (workers.dev bloquea urllib: 1010).
"""
import json
import subprocess
import sys
import time
import urllib.parse

RAIZ = "/home/z/my-project/upload"
F_CLAVE = "/home/z/my-project/scripts/worker-tele/.clave-produccion"
URL = "https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")


def lee_clave():
    with open(F_CLAVE, "r", encoding="utf-8") as f:
        return f.read().strip()


def curl(args, cuerpo=None):
    cmd = ["curl", "-sS", "-m", "30", "-A", UA, "-w", "\n%{http_code}"] + args
    if cuerpo is not None:
        cmd += ["--data-binary", cuerpo, "-H",
                "Content-Type: text/plain;charset=UTF-8"]
    p = subprocess.run(cmd, capture_output=True, timeout=60)
    out = p.stdout.decode("utf-8", "replace")
    if "\n" not in out:
        return out, "?"
    cuerpo_out, code = out.rsplit("\n", 1)
    return cuerpo_out, code.strip()


def main():
    clave = lee_clave()
    q = urllib.parse.urlencode({"clave": clave})

    print("== 1 · GET ?eventos=50 (qué hay en D1)")
    cuerpo, code = curl([URL + "?eventos=50&" + q])
    print("   HTTP", code)
    try:
        d = json.loads(cuerpo)
        evs = d.get("eventos", [])
        print("   eventos recibidos:", len(evs))
        for e in evs:
            t = e.get("t")
            fecha = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(t / 1000)) if isinstance(t, (int, float)) else "?"
            print(f"   · {e.get('e','?'):12} v={e.get('v','?'):16} t={fecha} sid={str(e.get('sid'))[:14]} extra={ {k: v for k, v in e.items() if k not in ('e','t','v','sid')} }")
    except Exception as ex:
        print("   ✗ JSON inválido:", str(ex), cuerpo[:200])

    print("== 2 · POST lote diagnóstico (sid=diag_r42_xxx)")
    sid = "diag_r42_" + str(int(time.time()))
    lote = [
        {"e": "boot", "t": int(time.time() * 1000), "v": "diag-r42", "sid": sid, "platform": "2d"},
        {"e": "diag_ping", "t": int(time.time() * 1000), "v": "diag-r42", "sid": sid, "nota": "prueba de ingestión r42"},
    ]
    cuerpo, code = curl([URL], cuerpo=json.dumps(lote))
    print("   HTTP", code, "cuerpo:", repr(cuerpo[:120]))

    print("== 3 · GET latido + resumen (lo que vería el panel)")
    cuerpo, code = curl([URL])
    print("   latido HTTP", code, cuerpo[:120])
    cuerpo, code = curl([URL + "?resumen=1&" + q])
    print("   resumen HTTP", code)
    try:
        d = json.loads(cuerpo)
        print("   total:", d.get("total"), "· sesionesUnicas:", d.get("sesionesUnicas"),
              "· arranques24h:", d.get("arranques24h"))
        print("   porEvento:", json.dumps(d.get("porEvento", {}), ensure_ascii=False)[:400])
        print("   porDia:", json.dumps(d.get("porDia", []), ensure_ascii=False)[:400])
        print("   versiones:", json.dumps(d.get("versiones", []), ensure_ascii=False)[:300])
        print("   alarmas:", json.dumps(d.get("alarmas", {}), ensure_ascii=False)[:300])
    except Exception as ex:
        print("   ✗ JSON inválido:", str(ex), cuerpo[:200])

    print("== 4 · DELETE del lote de diagnóstico")
    cuerpo, code = curl(["-X", "DELETE", URL + "?" + urllib.parse.urlencode({"clave": clave, "sid": sid})])
    print("   HTTP", code, cuerpo[:120])


if __name__ == "__main__":
    sys.exit(main())
