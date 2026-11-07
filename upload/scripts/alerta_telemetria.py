#!/usr/bin/env python3
"""M5b · ALERTA DE TELEMETRÍA — reporte claro para el dueño (roadmap MEJORAS.md M5).

Qué hace
--------
Lee el agregado de producción del worker de telemetría (?resumen=1) y traduce
el bloque `alarmas` a un reporte de un vistazo: FPS medio en VR, errores JS,
sesiones VR cortas (posible crash al entrar) y golpes sin sonido (señales de
audio roto). Pensado para mirar a mano o colgarlo de un cron.

Uso
---
    python3 scripts/alerta_telemetria.py            # reporte humano
    python3 scripts/alerta_telemetria.py --json     # salida máquina (cron)
    python3 scripts/alerta_telemetria.py --sid XYZ  # reescala al subconjunto

Códigos de salida (para automatizar)
------------------------------------
    0  VERDE     — sin alarmas activas
    1  AMARILLO  — algo a vigilar
    2  ROJO      — actuar ya (bajo el mínimo jugable o errores por brotes)
    3  ERROR     — sin clave, red caída o respuesta no válida (NO es alarma)

Notas del taller
----------------
  · workers.dev bloquea la firma Python-urllib (error 1010) → SIEMPRE curl
    con UA de navegador (lección rondas 8 y 20).
  · La CLAVE vive en scripts/worker-tele/.clave-produccion (600, gitignored).
  · Los umbrales viven en el worker (fps < 60 rojo / < 72 amarillo con ≥3
    muestras; errores ≥3/sesión rojo / ≥1 amarillo; VR cortas ≥50 % rojo /
    ≥25 % amarillo; audio roto ≥3/sesión rojo / ≥1 amarillo). Aquí no se
    duplican umbrales: se reporta lo que el worker declara.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele"
FICHERO_CLAVE = os.path.join(RAIZ, "scripts", "worker-tele", ".clave-produccion")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")

ETIQUETA = {
    "fps_bajo": "FPS medio en VR",
    "errores_js": "Errores JS",
    "vr_cortas": "Sesiones VR cortas (<60 s)",
    "sin_sonido": "Golpes sin sonido",
}
ICONS = {"rojo": "✖", "amarillo": "▲", "verde": "✓"}


def curl(url):
    p = subprocess.run(
        ["curl", "-sS", "-m", "30", "-A", UA, url],
        capture_output=True, timeout=60,
    )
    return p.stdout.decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser(description="Alerta de telemetría CRAZY PING PONG")
    ap.add_argument("--json", action="store_true", help="salida máquina")
    ap.add_argument("--sid", default=None, help="reescale las alarmas a una sesión")
    args = ap.parse_args()

    clave = ""
    if os.path.exists(FICHERO_CLAVE):
        with open(FICHERO_CLAVE, "r", encoding="utf-8") as f:
            clave = f.read().strip()
    if not clave:
        print("FALTA CLAVE: scripts/worker-tele/.clave-produccion no existe")
        sys.exit(3)

    q = "?resumen=1&clave=" + clave + (("&sid=" + args.sid) if args.sid else "")
    bruto = curl(URL + q)
    try:
        res = json.loads(bruto)
    except ValueError:
        print("respuesta no JSON:", bruto[:200])
        sys.exit(3)
    if res.get("ok") is not True:
        print("error del worker:", res.get("error", bruto[:200]))
        sys.exit(3)

    alarmas = res.get("alarmas") or {}
    items = alarmas.get("items") or []
    nivel = alarmas.get("nivel") or "verde"

    if args.json:
        print(json.dumps({
            "nivel": nivel,
            "items": items,
            "total": res.get("total"),
            "sesionesUnicas": res.get("sesionesUnicas"),
            "arranques24h": res.get("arranques24h"),
            "fps": res.get("fps"),
            "ts": res.get("ts"),
        }, ensure_ascii=False, indent=1))
        sys.exit({"verde": 0, "amarillo": 1, "rojo": 2}.get(nivel, 3))

    ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    fps = res.get("fps") or {}
    dur = (res.get("vrDuracion") or {})
    durs = res.get("duraciones") or {}
    versiones = res.get("versiones") or []

    print("CRAZY PING PONG · ALARMA DE TELEMETRÍA · " + ahora)
    print("=" * 64)
    print("Almacén: {} · eventos: {} · sesiones: {} · arranques 24 h: {}".format(
        res.get("almacen", "d1:crazypp-tele"), res.get("total"),
        res.get("sesionesUnicas"), res.get("arranques24h")))
    if args.sid:
        print("Filtro: sid={}".format(args.sid))
    print("FPS medio VR: {} ({} muestras) · duración VR media: {} s".format(
        fps.get("medio", "-"), fps.get("muestras", 0),
        dur.get("media") if dur.get("media") is not None else "-"))
    if durs.get("media") is not None:
        print("Duración por visita: {} s (máx {} s, {} cierres)".format(
            durs.get("media"), durs.get("max"), durs.get("n")))
    if versiones:
        print("Versión más activa: v{} ({} eventos, {} sesiones)".format(
            versiones[0].get("v"), versiones[0].get("eventos"),
            versiones[0].get("sesiones")))
    print("-" * 64)

    if not items:
        print("✓ VERDE — sin alarmas: FPS, errores JS, sesiones VR y audio")
        print("  dentro de umbral (o sin datos suficientes para alarmar).")
    else:
        for it in sorted(items, key=lambda x: {"rojo": 0, "amarillo": 1}.get(x.get("nivel"), 2)):
            tag = (it.get("nivel") or "").upper()
            print("[{}] {} — {}".format(
                tag, ETIQUETA.get(it.get("id"), it.get("id")), it.get("msg", "")))
            d = it.get("datos") or {}
            if d:
                print("        datos: " + json.dumps(d, ensure_ascii=False))

    print("-" * 64)
    print("NIVEL GLOBAL: {} {}".format(
        ICONS.get(nivel, "?"), nivel.upper()))
    print("Referencias: FPS ≥72 confort · errores 0 ideal · VR <60 s posible crash")
    print("             · señales de audio roto: 0 ideal (M5b)")
    sys.exit({"verde": 0, "amarillo": 1, "rojo": 2}.get(nivel, 3))


if __name__ == "__main__":
    main()
