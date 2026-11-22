#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_plantilla.py — Validador del modelo unificado de campeonatos (Ronda 25).

Uso:
    python3 scripts/qa_plantilla.py <carpeta_campeonato> [--compat]

  --compat   modo legado (campeonatos orgánicos pre-plantilla): los fallos
             de bloques unificados se reportan como AVISO y no como FALLO.

Valida (estático, sin navegador):
  · manifest.json presente, JSON válido y claves obligatorias del contrato 1
  · id/storage/estado/camino/powers/powerTrigger/stages con rangos del modelo
  · inventario de assets: todo lo declarado en manifest existe en assets/
  · index.js: contrato champ_sdk (export default + métodos obligatorios)
  · coherencia del camino (patrón duelo→prueba→duelo→prueba→final)
Salida: informe con [OK]/[AVISO]/[FALLO] y código de salida 0/1.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KINDS_PRUEBA = {"duelo", "dianas", "arkanoid", "objetos", "custom", "escudo", "impulso", "tren"}
KINDS_PODER_IMPL = {"confeti", "globos", "bola"}          # implementados por la plantilla
KINDS_PODER_KNOWN = KINDS_PODER_IMPL | {
    "arena", "burla", "custom", "dinamita", "disparo", "estampida",
    "mareo", "orbe", "split", "portals", "fuego", "sombras", "crazyball",
    "mano", "moscas", "calabaza", "gelatina",
}
ESTADOS_VIDA = {"borrador", "validacion", "listo", "publicado", "desactivado"}
METRICAS_CORONACION = {"puntos", "duelos", "fecha"}
METODOS_CONTRATO = ["init", "start", "leave", "resetRecords", "update", "onPoint",
                    "onMatchOver", "aiMul", "serveTrigger", "reenter", "replayMap",
                    "replayHover", "replayLaunch", "musicOff", "testActive", "testStep"]

ok, avisos, fallos = [], [], []


def OK(msg): ok.append(msg)
def AVISO(msg): avisos.append(msg)
def FALLO(msg): fallos.append(msg)


def asset_existe(carpeta, ruta):
    if not ruta or not isinstance(ruta, str):
        return False
    rel = ruta.replace("^assets/", "").replace("assets/", "", 1) if ruta.startswith("assets/") else ruta
    return os.path.isfile(os.path.join(carpeta, "assets", rel))


def valida(carpeta, compat):
    man_path = os.path.join(carpeta, "manifest.json")
    idx_path = os.path.join(carpeta, "index.js")
    cid = os.path.basename(os.path.normpath(carpeta))

    if not os.path.isfile(man_path):
        FALLO("manifest.json no encontrado"); return
    if not os.path.isfile(idx_path):
        FALLO("index.js no encontrado"); return
    try:
        with open(man_path, "r", encoding="utf-8") as f:
            man = json.load(f)
        OK("manifest.json JSON válido")
    except ValueError as e:
        FALLO("manifest.json no parsea: %s" % e); return

    # ---- contrato básico (schema contract 1) ----
    for k in ("id", "version", "contract", "title", "description", "rival", "storage"):
        if k not in man:
            FALLO("falta clave obligatoria '%s' del contrato 1" % k)
    OK("claves de contrato 1 presentes") if all(k in man for k in ("id", "version", "contract", "title", "rival", "storage")) else None

    mid = man.get("id", "")
    if mid != cid:
        AVISO("manifest.id (%s) != nombre de carpeta (%s)" % (mid, cid))
    if mid != "_plantilla" and not re.match(r"^[a-z0-9_-]{2,24}$", mid):
        FALLO("id '%s' no cumple ^[a-z0-9_-]{2,24}$" % mid)
    else:
        OK("id válido: %s" % mid)

    st = man.get("storage", "")
    if re.match(r"^pp_champ_[a-z0-9_]+_\*$", st) or st.startswith("pp_arcade_"):
        OK("storage con prefijo de núcleo: %s" % st)
        if mid != "_plantilla" and not st.startswith("pp_champ_%s_" % mid) and not st.startswith("pp_arcade_"):
            AVISO("storage %s no deriva de pp_champ_%s_" % (st, mid))
    else:
        (AVISO if compat else FALLO)("storage '%s' no sigue pp_champ_<id>_*" % st)

    if man.get("estado") in ESTADOS_VIDA:
        OK("estado de ciclo de vida: %s" % man.get("estado"))
    else:
        (AVISO if compat else FALLO)("estado '%s' fuera del ciclo borrador→publicado" % man.get("estado"))
    if man.get("contract") != 1:
        AVISO("contract != 1 (el núcleo actual habla contract 1)")

    t = man.get("title", {})
    if not isinstance(t, dict) or not t.get("es"):
        FALLO("title.es obligatorio")
    else:
        OK("title.es: %s" % t["es"][:40])

    # ---- modelo unificado: camino ----
    cam = man.get("camino") or {}
    if cam:
        dif = cam.get("dificultad", {})
        modo = dif.get("modo", "formula")
        if modo not in ("formula", "tabla"):
            (AVISO if compat else FALLO)("camino.dificultad.modo '%s' inválido" % modo)
        elif modo == "tabla" and not dif.get("tabla"):
            FALLO("camino.dificultad.modo='tabla' sin tabla")
        else:
            OK("camino.dificultad modo=%s" % modo)
        wm = cam.get("worldMetric", "duelwins")
        if wm not in ("duelwins", "wins", "puntos"):
            (AVISO if compat else FALLO)("camino.worldMetric '%s' inválido" % wm)
        ley = cam.get("leyenda") or {}
        if ley.get("activa"):
            a = ley.get("aiMulMul", 1.15)
            if not (1.0 <= a <= 2.0):
                AVISO("camino.leyenda.aiMulMul=%.2f fuera de [1.0,2.0]" % a)
            cs = ley.get("chanceSuma", 0.06)
            if not (0 <= cs <= 0.3):
                AVISO("camino.leyenda.chanceSuma=%.2f fuera de [0,0.3]" % cs)
            OK("RUTA LEYENDA activa (aiMul ×%.2f, chance +%.2f)" % (a, cs))
    else:
        AVISO("sin bloque 'camino' (modelo unificado): el módulo usa sus respaldos")

    # ---- stages ----
    stages = man.get("stages") or []
    if not (3 <= len(stages) <= 7):
        (AVISO if compat else FALLO)("stages=%s fuera del rango habitual 3..7" % len(stages))
    else:
        OK("stages: %d etapas" % len(stages))
    for i, s in enumerate(stages):
        for k in ("id", "name", "kind"):
            if not s.get(k):
                FALLO("stages[%d] sin '%s'" % (i, k))
        if s.get("kind") not in KINDS_PRUEBA:
            FALLO("stages[%d].kind '%s' desconocido (%s)" % (i, s.get("kind"), sorted(KINDS_PRUEBA)))
        if s.get("kind") == "custom" and not s.get("module"):
            FALLO("stages[%d] kind=custom sin 'module'" % i)
    if stages:
        kinds = [s.get("kind") for s in stages]
        if kinds[0] == "duelo" and kinds[-1] == "duelo":
            OK("patrón duelo→…→duelo final (convención de los 5)")
        else:
            AVISO("el camino no empieza/termina en duelo (los 5 actuales sí)")

    # ---- powers + powerTrigger ----
    powers = man.get("powers") or []
    if len(powers) > 4:
        AVISO("powers=%d (máx recomendado 4)" % len(powers))
    for i, p in enumerate(powers):
        k = p.get("kind")
        if k not in KINDS_PODER_KNOWN:
            FALLO("powers[%d].kind '%s' desconocido" % (i, k))
        if k == "custom" and not p.get("module"):
            FALLO("powers[%d] kind=custom sin 'module'" % i)
        if k in KINDS_PODER_IMPL:
            OK("power implementado por plantilla: %s" % k)
        ch = p.get("chance")
        if ch is not None and not (0 <= ch <= 1):
            FALLO("powers[%d].chance=%.2f fuera de [0,1]" % (i, ch))
        act = p.get("activacion")
        if act is not None and act not in ("rally", "puntos"):
            (AVISO if compat else FALLO)("powers[%d].activacion '%s' inválida (rally|puntos)" % (i, act))
    pt = man.get("powerTrigger") or {}
    if pt:
        ch = pt.get("chance", 0.32)
        if not (0 < ch <= 1):
            FALLO("powerTrigger.chance=%.2f fuera de (0,1]" % ch)
        cd = pt.get("cooldown", 13.0)
        if cd < 4:
            AVISO("powerTrigger.cooldown=%.1f muy bajo (<4 s)" % cd)
        bolsa = pt.get("bolsa", "rotatoria")
        if bolsa not in ("rotatoria", "antirepeticion"):
            (AVISO if compat else FALLO)("powerTrigger.bolsa '%s' inválida" % bolsa)
        OK("powerTrigger unificado (chance %.2f · cooldown %.1f · bolsa %s)" % (ch, cd, bolsa))

    # ---- rival ----
    rv = man.get("rival") or {}
    if not rv.get("id") or not rv.get("name") or not rv.get("kind"):
        FALLO("rival.id/name/kind obligatorios")
    else:
        OK("rival: %s (%s)" % (rv.get("name"), rv.get("kind")))
    pers = rv.get("personalidad") or {}
    for k in ("agresividad", "precision", "constancia"):
        v = pers.get(k)
        if v is not None and not (1 <= v <= 5):
            AVISO("rival.personalidad.%s=%s fuera de 1..5" % (k, v))

    # ---- inventario de assets ----
    faltan = []
    room = man.get("room") or {}
    for k in ("floor", "ceil", "back", "front", "left", "right"):
        if room.get(k) and not asset_existe(carpeta, room[k]):
            faltan.append(room[k])
    audio = man.get("audio") or {}
    if audio.get("music") and not asset_existe(carpeta, audio["music"]):
        faltan.append(audio["music"])
    for p in powers:
        if p.get("icon") and not asset_existe(carpeta, p["icon"]):
            faltan.append(p["icon"])
    mapa = man.get("mapa") or {}
    if mapa.get("modo") == "arte" and mapa.get("arte") and not asset_existe(carpeta, mapa["arte"]):
        faltan.append(mapa["arte"])
    cor = man.get("coronacion") or {}
    if cor.get("insignia") and not asset_existe(carpeta, cor["insignia"]):
        faltan.append(cor["insignia"])
    tro = man.get("trophy") or {}
    if tro.get("arte") and not asset_existe(carpeta, tro["arte"]):
        faltan.append(tro["arte"])
    gun = man.get("playerGun") or {}
    if gun.get("activo") and gun.get("glb") and not asset_existe(carpeta, gun["glb"]):
        faltan.append(gun["glb"])
    inv = man.get("assets", "")
    for m in re.findall(r"assets/[A-Za-z0-9_./-]+", inv or ""):
        if "..." in m or m.endswith("/"):
            continue
        if not asset_existe(carpeta, m):
            faltan.append(m + " (inventario)")
    if faltan:
        for f in sorted(set(faltan)):
            if mid == "_plantilla":
                AVISO("plantilla sin arte (esperado): %s — el generador lo pide al crear" % f)
            else:
                (AVISO if compat else FALLO)("asset ausente: %s" % f)
    else:
        OK("inventario de assets completo")

    # ---- i18n ----
    i18n = man.get("i18n") or {}
    es = i18n.get("es") or {}
    faltan_tx = [k for k in ("bienvenida", "coronacion_titulo", "coronacion_msg") if not es.get(k)]
    if faltan_tx:
        (AVISO if compat else FALLO)("i18n.es sin claves: %s" % ", ".join(faltan_tx))
    else:
        OK("i18n.es mínimo presente")

    # ---- coronación ----
    if cor:
        malas = [s for s in (cor.get("stats") or []) if s not in METRICAS_CORONACION]
        if malas:
            FALLO("coronacion.stats desconocidas: %s (válidas: %s)" % (malas, sorted(METRICAS_CORONACION)))
        else:
            OK("coronación configurada (dur %s, stats %s)" % (cor.get("dur", 14), cor.get("stats")))

    # ---- index.js: contrato champ_sdk ----
    with open(idx_path, "r", encoding="utf-8") as f:
        js = f.read()
    if "export default" not in js:
        FALLO("index.js sin export default (contrato champ_sdk)")
    else:
        OK("export default presente")
    falta_met = [m for m in METODOS_CONTRATO if not re.search(r"function\s+%s\b|%s\s*\(" % (m, m), js)]
    falta_met = [m for m in METODOS_CONTRATO if not re.search(r"\b%s\b" % re.escape(m), js)]
    if falta_met:
        FALLO("index.js sin métodos del contrato: %s" % ", ".join(falta_met))
    else:
        OK("contrato champ_sdk completo (%d métodos)" % len(METODOS_CONTRATO))
    if "champ_sdk.js" not in js:
        AVISO("index.js no importa del SDK común (../sdk/champ_sdk.js)")
    if re.search(r"\bdebugger\b", js):
        FALLO("index.js contiene 'debugger'")
    for sec in ("sdk/", "assets/"):
        pass
    secreto = re.search(r"ghp_[A-Za-z0-9]{20,}|cfut_[A-Za-z0-9]{20,}|cpp-[A-Za-z0-9_]{20,}", js)
    if secreto:
        FALLO("index.js parece contener un SECRETO (patrón %s)" % secreto.group(0)[:8])
    else:
        OK("sin secretos embebidos")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    compat = "--compat" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    carpeta = args[0] if os.path.isabs(args[0]) else os.path.join(RAIZ, args[0])
    if not os.path.isdir(carpeta):
        print("✗ carpeta no existe: %s" % carpeta)
        sys.exit(2)
    valida(carpeta, compat)
    print("=" * 74)
    print("QA PLANTILLA · %s %s" % (os.path.basename(os.path.normpath(carpeta)), "(modo compat)" if compat else ""))
    print("=" * 74)
    for m in ok:
        print("  [OK]    " + m)
    for m in avisos:
        print("  [AVISO] " + m)
    for m in fallos:
        print("  [FALLO] " + m)
    print("-" * 74)
    print("  %d OK · %d avisos · %d fallos → %s" % (len(ok), len(avisos), len(fallos), "VERDE" if not fallos else "ROJO"))
    sys.exit(0 if not fallos else 1)


if __name__ == "__main__":
    main()
