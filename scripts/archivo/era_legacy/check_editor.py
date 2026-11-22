#!/usr/bin/env python3
"""Extrae los <script> inline del editor parcheado y los valida con node --check."""
import pathlib, re, subprocess, tempfile, sys

BASE = pathlib.Path("/home/z/my-project")
ED = BASE / "download/editor-campeonatos/index.html"
html = ED.read_text(encoding="utf-8")

# los bloques <script type="text/plain"> NO son JS: se validan aparte (módulo)
bloques = re.findall(r"<script([^>]*)>(.*?)</script>", html, re.S)
ok = True
njs = 0
for attrs, body in bloques:
    if "text/plain" in attrs:
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as f:
            f.write(body)
            mjs = f.name
        r = subprocess.run(["node", "--check", mjs], capture_output=True, text=True)
        print(("MÓDULO OK" if r.returncode == 0 else "MÓDULO FAIL:\n" + r.stderr[:2000]) + f"  ({len(body)} B)")
        ok = ok and r.returncode == 0
        continue
    if "src=" in attrs:
        print("script externo omitido:", attrs.strip())
        continue
    njs += 1
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(body)
        js = f.name
    r = subprocess.run(["node", "--check", js], capture_output=True, text=True)
    etiqueta = "app1" if "app1" in body[:200] else ("app2" if "app2" in body[:200] else ("app2b" if "app2b" in body[:200] else ("app3" if "app3" in body[:200] else f"#{njs}")))
    print(("OK  " if r.returncode == 0 else "FAIL\n" + r.stderr[:2000]) + f"  {etiqueta}  ({len(body)} B)")
    ok = ok and r.returncode == 0

# comprobaciones de coherencia
for debe in ('id="tpl-modulo"', "construirPaquete", "descargarPaquete", "generarVistasPrevias", "V3.0.3"):
    c = html.count(debe)
    print(f"{'OK ' if c else 'FALTA'} {debe} ×{c}")
for muerto in ("leemePruebas", "leemeDefinitivo", "resumenCajaTexto", "app.netlify.com/drop", '"fantasma"'):
    c = html.count(muerto)
    print(f"{'LIMPIO' if c == 0 else 'RESTO'} {muerto} ×{c}")

sys.exit(0 if ok else 1)
