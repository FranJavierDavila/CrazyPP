#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_campeonato.py — Generador de campeonatos desde la PLANTILLA unificada (Ronda 25).

Crear un campeonato nuevo = arte + este comando + validación + registro.

Uso básico:
    python3 scripts/gen_campeonato.py --id bosque --titulo-es "Bosque Encantado"

Opciones:
    --id ID               identificador único ^[a-z0-9_-]{2,24}$ (obligatorio)
    --titulo-es TEXT      título en español (obligatorio)
    --titulo-en TEXT      título en inglés
    --desc-es TEXT        descripción corta (es)
    --rival-nombre TEXT   nombre del rival (def: ID en mayúsculas)
    --dificultad X        facil | media | dificil   (difMul 0.85 / 1.0 / 1.18)
    --arte DIR            carpeta con el arte (copia por nombre convencional)
    --dest DIR            destino (def: public/championships/<id>)
    --registrar           añade la entrada a championships.json
                          (solo tras validar en el headset; estado 'borrador')
    --sin-gun             campeonato sin pistola láser

Flujo recomendado (guía completa: public/championships/PLANTILLA-GUIA.md):
    1) prepara el arte con los nombres de _plantilla/assets/LEEME-ARTE.txt
    2) gen_campeonato.py ...  → crea la carpeta y valida con qa_plantilla.py
    3) qa en el headset (estado 'borrador' no aparece en el menú; para probar
       en local, pásalo a 'listo' y añádelo a championships.json con --registrar)
    4) al dar luz verde: estado 'publicado' + versión + sellos del proyecto
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANTILLA = os.path.join(RAIZ, "public", "championships", "_plantilla")
REGISTRO = os.path.join(RAIZ, "public", "championships", "championships.json")
DIFMUL = {"facil": 0.85, "media": 1.0, "dificil": 1.18}

ARTE_ESPERADO = [
    "sala_floor.jpg", "sala_ceil.jpg", "sala_back.jpg", "sala_front.jpg",
    "sala_left.jpg", "sala_right.jpg",
    "idle.webp", "duelo.webp", "derrotado.webp", "triunfante.webp",
    "bso.mp3", "superpoder.webp", "insignia.png",
    "power_0.png", "power_1.png", "mapa.png", "intro.mp4", "pistol.glb",
    "risas.mp3", "decor1.png", "decor2.png",
]


def fallo(msg):
    print("✗ " + msg)
    sys.exit(1)


def limpiar_doc(d):
    """Quita las claves documentales _comment/_doc del manifest generado."""
    if isinstance(d, dict):
        return {k: limpiar_doc(v) for k, v in d.items() if not k.startswith("_comment") and not k.startswith("_doc") and k != "_doc_" + ""}
    if isinstance(d, list):
        return [limpiar_doc(x) for x in d]
    return d


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--titulo-es", required=True)
    ap.add_argument("--titulo-en", default="")
    ap.add_argument("--desc-es", default="")
    ap.add_argument("--rival-nombre", default="")
    ap.add_argument("--dificultad", default="media", choices=list(DIFMUL))
    ap.add_argument("--arte", default="")
    ap.add_argument("--dest", default="")
    ap.add_argument("--registrar", action="store_true")
    ap.add_argument("--sin-gun", action="store_true")
    a = ap.parse_args()

    cid = a.id
    if not re.match(r"^[a-z0-9_-]{2,24}$", cid):
        fallo("id '%s' no cumple ^[a-z0-9_-]{2,24}$" % cid)
    if cid.startswith("_"):
        fallo("los ids no empiezan por '_' (reservado: _plantilla)")
    dest = a.dest if a.dest else os.path.join(RAIZ, "public", "championships", cid)
    dest = dest if os.path.isabs(dest) else os.path.join(RAIZ, dest)
    if os.path.exists(dest):
        fallo("el destino ya existe: %s" % dest)

    with open(os.path.join(PLANTILLA, "manifest.json"), "r", encoding="utf-8") as f:
        man = json.load(f)

    # 1) identidad
    man["id"] = cid
    man["version"] = 1
    man["estado"] = "borrador"
    man["storage"] = "pp_champ_%s_*" % cid
    man["title"] = {"es": a.titulo_es, "en": a.titulo_en or a.titulo_es}
    man["description"] = {"es": a.desc_es or a.titulo_es, "en": a.desc_es or a.titulo_es}
    rn = a.rival_nombre or cid.upper()
    man["rival"]["id"] = "%s_rival" % cid
    man["rival"]["name"] = rn
    man["trophy"]["name"] = {"es": "Trofeo %s" % a.titulo_es, "en": "%s Trophy" % (a.titulo_en or a.titulo_es)}
    man["coronacion"]["titulo"] = {"es": "¡CAMPEÓN %s!" % rn, "en": "%s CHAMPION!" % rn}
    man["coronacion"]["mensaje"] = {"es": "Has conquistado %s." % a.titulo_es, "en": "You conquered %s." % (a.titulo_en or a.titulo_es)}
    man["i18n"]["es"]["bienvenida"] = "Bienvenido a %s" % a.titulo_es
    man["i18n"]["en"]["bienvenida"] = "Welcome to %s" % (a.titulo_en or a.titulo_es)

    # 2) dificultad + gun
    man["camino"]["dificultad"]["difMul"] = DIFMUL[a.dificultad]
    if a.sin_gun:
        man.pop("playerGun", None)

    # 3) arte (antes de escribir el manifest: permite autodesactivar la pistola)
    os.makedirs(os.path.join(dest, "assets"), exist_ok=True)
    presentes, faltan = [], list(ARTE_ESPERADO)
    if a.arte:
        arte = a.arte if os.path.isabs(a.arte) else os.path.join(RAIZ, a.arte)
        if not os.path.isdir(arte):
            fallo("--arte no es una carpeta: %s" % arte)
        for fn in sorted(os.listdir(arte)):
            src = os.path.join(arte, fn)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(dest, "assets", fn))
                if fn in faltan:
                    presentes.append(fn)
                    faltan.remove(fn)
        extra = sorted(set(os.listdir(arte)) - set(ARTE_ESPERADO))
        if extra:
            print("  · ficheros de arte fuera de convención (copiados igualmente): %s" % ", ".join(extra))

    # 3b) pistola declarada pero sin modelo → se desactiva sola (sin trampas)
    notas_extra = []
    gun = man.get("playerGun")
    if gun and gun.get("activo") and "pistol.glb" not in presentes:
        gun["activo"] = False
        notas_extra.append("playerGun desactivado automáticamente: falta assets/pistol.glb (reactívalo al subirlo)")

    # 4) inventario legible + notas + escribir carpeta
    man["assets"] = "assets/ (sala_*.jpg x6, rival + estados webp, bso, superpoder, insignia, power_*.png%s)" % (", pistol.glb" if gun and gun.get("activo") else "")
    man["notes"] = ["v1 · Campeonato generado desde _plantilla (modelo unificado Ronda 25) con scripts/gen_campeonato.py · dificultad %s" % a.dificultad]
    if notas_extra:
        man["notes"].extend(notas_extra)
    man = limpiar_doc(man)

    with open(os.path.join(dest, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(os.path.join(PLANTILLA, "index.js"), "r", encoding="utf-8") as f:
        js = f.read()
    if "const MOD_ID = '_plantilla';" not in js:
        fallo("no se encontró MOD_ID en el index.js de la plantilla")
    js = js.replace("const MOD_ID = '_plantilla';", "const MOD_ID = '%s';" % cid)
    with open(os.path.join(dest, "index.js"), "w", encoding="utf-8") as f:
        f.write(js)
    shutil.copy2(os.path.join(PLANTILLA, "assets", "LEEME-ARTE.txt"),
                 os.path.join(dest, "assets", "LEEME-ARTE.txt"))

    # 6) registro opcional
    if a.registrar:
        with open(REGISTRO, "r", encoding="utf-8") as f:
            reg = json.load(f)
        ids = [e["id"] if isinstance(e, dict) else e for e in reg.get("championships", [])]
        if cid in ids:
            fallo("'%s' ya está en championships.json" % cid)
        reg["championships"].append(cid)
        reg["version"] = int(reg.get("version", 0)) + 1
        reg["generado"] = "generado por gen_campeonato.py (estado borrador)"
        with open(REGISTRO, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=1)

    # 7) validación
    print("✓ campeonato creado: %s" % dest)
    if a.arte:
        print("  · arte copiado: %d convencionales presentes, faltan %d" % (len(presentes), len(faltan)))
        if faltan:
            print("    → sube después: %s" % ", ".join(faltan))
    else:
        print("  · sin --arte: la carpeta espera el arte (ver assets/LEEME-ARTE.txt)")
    if a.registrar:
        print("  · registrado en championships.json (estado 'borrador': invisible en el menú)")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "qa_plantilla.py"), dest],
                       capture_output=True, text=True)
    print(r.stdout.rstrip())
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
