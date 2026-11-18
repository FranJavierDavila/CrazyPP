#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Respaldo completo local de CRAZY PING PONG — punto: Ronda 24 cerrada (V3.6.18-SDK6).

Genera en /home/z/my-project/download/:
  1) crazypp_respaldofuente_<ver>_<fecha>.zip  — árbol de trabajo completo sin regenerables
  2) crazypp_git_completo_<fecha>.bundle       — historia git completa (--all, clonable)
  3) credenciales_respaldadas_<fecha>.txt      — PAT GitHub + token CF + clave D1 (chmod 600)
  4) SHA256SUMS_<fecha>.txt                    — integridad de 1-3

Uso: python3 scripts/backup_completo.py
"""
import datetime
import hashlib
import os
import subprocess
import sys
import zipfile
from zoneinfo import ZoneInfo

ROOT = "/home/z/my-project"
OUT = os.path.join(ROOT, "download")
# fecha en el huso del usuario (Europe/Madrid), no UTC del sandbox
FECHA = datetime.datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
VER = "v3.6.18-SDK6"
COMMIT_MAIN = "55394ac"
COMMIT_PAGES = "11446a2"
GOLDEN = "25ea3e39"

ZIP_PATH = os.path.join(OUT, "crazypp_respaldofuente_%s_%s.zip" % (VER, FECHA))
BUNDLE_PATH = os.path.join(OUT, "crazypp_git_completo_%s.bundle" % FECHA)
CREDS_PATH = os.path.join(OUT, "credenciales_respaldadas_%s.txt" % FECHA)
SUMS_PATH = os.path.join(OUT, "SHA256SUMS_%s.txt" % FECHA)
LEEME_ZIP = "RESPALDO-LEEME.txt"

# Exclusiones: regenerables / entregables duplicados / secretos (van aparte)
EXCL_DIRS = {
    "node_modules", ".next", ".git", "download", "skills", "tmp_frames",
    "tool-results", "__pycache__", ".cache", ".npm", ".vercel", "coverage",
    "pages-site",  # checkout local de la rama pages: 100% recuperable del bundle
}
EXCL_PREFIXES = (
    "scripts/staging-v369", "scripts/staging-cloudflare",
    "public/descargas",           # staging de los mismos ZIPs de release (regenerable)
)
EXCL_BASENAMES = {
    ".cf-token", ".clave-produccion", ".github-pat", ".DS_Store",
    "crazypp-v308-trn1-CLOUDFLARE.zip",  # build obsoleto (superseded por v3.6.18)
}
EXCL_SUFFIXES = (".pyc",)


def excluido(rel, es_dir):
    if es_dir:
        partes = rel.split("/")
        if any(p in EXCL_DIRS for p in partes):
            return True
        for pref in EXCL_PREFIXES:
            if rel == pref or rel.startswith(pref + "/"):
                return True
        return False
    base = rel.split("/")[-1]
    if base in EXCL_BASENAMES or base.endswith(EXCL_SUFFIXES):
        return True
    if any(rel == pref or rel.startswith(pref + "/") for pref in EXCL_PREFIXES):
        return True
    partes = rel.split("/")
    if any(p in EXCL_DIRS for p in partes[:-1]):
        return True
    return False


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def humano(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return ("%.1f %s" % (n, u)) if u != "B" else ("%d B" % n)
        n /= 1024.0


LEEME = u"""RESPALDO COMPLETO — CRAZY PING PONG
====================================
Punto de respaldo : Ronda 24 cerrada (post-campeón listo) · %(ver)s en producción
Producción        : https://franjavierdavila.github.io/CrazyPP/
Fecha             : %(fecha)s
Commit main       : %(main)s   ·   rama pages: %(pages)s   ·   golden: %(golden)s

CONTENIDO DEL KIT
-----------------
1) crazypp_respaldofuente_%(ver)s_%(fecha)s.zip
   Árbol de trabajo completo: src/ (juego + módulos c00-c13), public/ (5 campeonatos +
   assets + game.html + vendor), scripts/ (cadena completa de despliegue y QA), configs,
   worklog.md. NO incluye regenerables: node_modules/, .next/, .git/, download/,
   public/descargas/, scripts/staging-*/, pages-site/ (copia local de la rama pages:
   se recupera del bundle con `git checkout pages`), el build obsoleto
   upload/crazypp-v308-trn1-CLOUDFLARE.zip, __pycache__ ni las credenciales (van aparte).
2) crazypp_git_completo_%(fecha)s.bundle
   COPIA MAESTRA — toda la historia git: ramas main / pages / proyecto / exp/live-tv
   y tags v3.6.2 → v3.6.18. Con este archivo solo se reconstruye el proyecto entero.
3) credenciales_respaldadas_%(fecha)s.txt  (CONFIDENCIAL)
   GitHub PAT, token Cloudflare y clave de producción D1.
4) SHA256SUMS_%(fecha)s.txt — sumas de integridad de 1-3.
5) Ya en download/ (build exacto desplegado): crazypp-v3618-sdk6-COMPLETO.zip,
   crazypp-v3618-sdk6-CLOUDFLARE.zip, crazypp-v3618-sdk6-ligera.zip,
   crazypp-live-service-SOLO.zip.

CÓMO RESTAURAR
--------------
A. Desde el bundle (recomendado):
     git clone crazypp_git_completo_%(fecha)s.bundle crazypp
     cd crazypp && npm install
     # para volver a conectar con GitHub:
     git remote set-url origin https://github.com/FranJavierDavila/CrazyPP.git
     git fetch origin
B. Desde el ZIP de fuente: descomprimir (todo queda en crazypp/) y usar tal cual;
   npm install solo si se quiere desarrollar/reconstruir.
C. Recredenciales: escribir los valores de credenciales_*.txt en
   scripts/worker-tele/.cf-token, .clave-produccion y .github-pat (chmod 600).
D. Reconstruir releases: pipeline documentado en worklog.md
   (bump_version.py → gen_release → build_zip.py → sella_rXX.py → qa_todo.py → deploy_pages.py).
   Build web estándar: npm run build — el juego vive en src/game/ y public/.

VERIFICAR INTEGRIDAD
--------------------
  sha256sum -c SHA256SUMS_%(fecha)s.txt

Notas:
- La clave antigua cpp-PNfGJcYnpvzjFHdO3jrVi3mR quedó invalidada en la Ronda 22.
- public/descargas/ y scripts/staging-*/ son staging regenerable de los ZIPs de release.
""" % {
    "ver": VER, "fecha": FECHA,
    "main": COMMIT_MAIN, "pages": COMMIT_PAGES, "golden": GOLDEN,
}

CREDS = u"""CONFIDENCIAL · CRAZY PING PONG · credenciales de operación (respaldo %(fecha)s)
==================================================================================

GitHub PAT (push a origin · cuenta FranJavierDavila · archivo scripts/worker-tele/.github-pat):
%(pat)s

Cloudflare API token (despliegue nativo del worker de telemetría ·
archivo scripts/worker-tele/.cf-token):
%(cft)s

Clave de producción D1 (panel /telemetria → "Producción (D1)" ·
archivo scripts/worker-tele/.clave-produccion):
%(clave)s

Notas:
- Guardar este archivo junto al resto del kit, en un lugar seguro.
- Tras restaurar: escribir .cf-token, .clave-produccion y .github-pat en
  scripts/worker-tele/ (chmod 600). Los tres están gitignored; NUNCA versionarlos
  (GitHub Push Protection rechaza pushes con secretos).
- La clave antigua cpp-PNfGJcYnpvzjFHdO3jrVi3mR quedó invalidada en la Ronda 22.
""" % {
    "fecha": FECHA,
    "pat": open(os.path.join(ROOT, "scripts/worker-tele/.github-pat")).read().strip(),
    "cft": open(os.path.join(ROOT, "scripts/worker-tele/.cf-token")).read().strip(),
    "clave": open(os.path.join(ROOT, "scripts/worker-tele/.clave-produccion")).read().strip(),
}


def paso1_bundle():
    print("== 1/4 · git bundle (--all) ==")
    r = subprocess.run(["git", "-C", ROOT, "bundle", "create", BUNDLE_PATH, "--all"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("FALLO bundle: %s" % r.stderr[-500:])
    v = subprocess.run(["git", "-C", ROOT, "bundle", "verify", BUNDLE_PATH],
                       capture_output=True, text=True)
    if v.returncode != 0:
        sys.exit("FALLO verify bundle: %s" % v.stderr[-500:])
    print("   OK ·", humano(os.path.getsize(BUNDLE_PATH)))
    print("   ", v.stdout.strip().splitlines()[-1] if v.stdout.strip() else "")


def paso2_zip():
    print("== 2/4 · ZIP fuente completa ==")
    n_fich, n_bytes = 0, 0
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(LEEME_ZIP, LEEME)
        for dirpath, dirnames, filenames in os.walk(ROOT):
            rel_dir = os.path.relpath(dirpath, ROOT)
            # podar directorios excluidos en caliente
            dirnames[:] = [d for d in dirnames
                           if not excluido(os.path.normpath(os.path.join(rel_dir, d))
                                           if rel_dir != "." else d, True)]
            for fn in sorted(filenames):
                abs_p = os.path.join(dirpath, fn)
                rel = os.path.normpath(os.path.join(rel_dir, fn)) if rel_dir != "." else fn
                if excluido(rel, False):
                    continue
                try:
                    z.write(abs_p, os.path.join("crazypp", rel))
                    n_fich += 1
                    n_bytes += os.path.getsize(abs_p)
                except OSError as e:
                    print("   aviso: %s (%s)" % (rel, e))
    print("   OK · %s ficheros · %s originales" % (n_fich, humano(n_bytes)))
    print("   ZIP:", humano(os.path.getsize(ZIP_PATH)))
    return n_fich


def paso3_creds():
    print("== 3/4 · credenciales (chmod 600) ==")
    with open(CREDS_PATH, "w", encoding="utf-8") as f:
        f.write(CREDS)
    os.chmod(CREDS_PATH, 0o600)
    print("   OK ·", CREDS_PATH)


def paso4_sums():
    print("== 4/4 · SHA256SUMS + verificación CRC del ZIP ==")
    lineas = []
    for p in (BUNDLE_PATH, ZIP_PATH, CREDS_PATH):
        lineas.append("%s  %s" % (sha256(p), os.path.basename(p)))
    with open(SUMS_PATH, "w", encoding="utf-8") as f:
        f.write("# SHA256 · kit de respaldo CRAZY PING PONG · %s\n" % FECHA)
        f.write("\n".join(lineas) + "\n")
    with zipfile.ZipFile(ZIP_PATH) as z:
        malo = z.testzip()
        if malo:
            sys.exit("FALLO CRC en: %s" % malo)
        total = sum(i.file_size for i in z.infolist())
    print("   CRC OK · %d miembros · %s descomprimido" % (len(z.infolist()), humano(total)))
    for l in lineas:
        print("   ", l)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    t0 = datetime.datetime.now()
    paso1_bundle()
    paso2_zip()
    paso3_creds()
    paso4_sums()
    print("\nRESPALDO COMPLETO EN %.1f s" % (datetime.datetime.now() - t0).total_seconds())
    print("Kit en:", OUT)
