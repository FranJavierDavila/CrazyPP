#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r78_v3670 — CAPA BM · V3.6.76-SDK6, FASE 72 «EL NARRADOR HONESTO».

Nota del dueño (r78): «En el audio del tutorial en el apartado de modos se
dice que cada 20 toques ganamos un superpoder, pero esto NO es para los
partidos normales ya que los superpoderes SOLO aparecen en los campeonatos.
Cuando describe los modos llega un momento que dice "…y más…" cuando lo que
debería es decir Campeonatos (el modo de juego tipo arcade con poderes en
juego tanto para el rival como para el propio jugador cuando consigue
superar los 20 toques seguidos. Estos superpoderes se pueden visualizar con
un icono identificativo sobre el mango de nuestra pala y se pueden lanzar
apretando el gatillo, tienen una duración de 10 segundos. ¡Lucha con el
Rival y véncelo!)».

El arreglo (r78) y SU verificación:
  · VOZ (c00, banco Piper de la casa): tutv8a «…multijugador y campeonatos»
    (adiós «y más») · tutv8b SIN la carga de poder del partido normal ·
    tutv9a «Los campeonatos son el modo arcade: aquí sí hay superpoderes…»
    · tutv9c NUEVO (icono en el mango · gatillo · 10 s · lucha y vence) ·
    tutv9b rivales/historia + ranking + entrenar. tutv8c intacta byte a byte.
  · ORDEN (c13): VOCES_PASO[7] = 8a, 8b, 8c, 9a, 9c, 9b.
  · PIZARRA (c00): la caja PODERES ahora dice «SOLO CAMPEONATOS · 20 toques
    seguidos cargan · gatillo lanza · 10 s» (ES+EN) — audio y pizarra
    cuentan la MISMA verdad.
  · VERDAD DEL JUEGO (c12, intacta y re-anclada): megaEnabled() solo con
    champs.active · MEGA_GOLPES = 20 · MEGA_DUR = 15 (Mega Pala apila).

BLOQUES: (1) AGUJAS r78 + átomos BYTE-EXACTO (los 10 OGG del banco leídos de
disco y buscados dentro del game.html servido) + el VIEJO tutv8b (el que
prometía poderes en el partido) extraído de git y PROHIBIDO en el servido.
(2) CONTADORES + ORDEN del plan. (3) JUEGO REAL headless: banco de voz
decodificado, 6/6 átomos del paso 7 presentes, duraciones nuevas (tutv8b
corta = narración honesta, tutv9c larga = powers explicados) y speakPlan del
plan COMPLETO de la pizarra de modos = true, 0 pageerrors.
Uso: python3 scripts/qa_r78_v3670.py [URL]
"""
import asyncio
import base64
import os
import re
import subprocess
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
RAIZ = "/home/z/my-project"
DIR_CAPS = os.path.join(RAIZ, "download")
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


ATOMOS = ["tutv8a", "tutv8b", "tutv8c", "tutv9a", "tutv9b", "tutv9c"]
NUEVOS = ["tutv8a", "tutv8b", "tutv9a", "tutv9b", "tutv9c"]   # regenerados r78


def b64_de(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def b64_viejo_git(clave, banco):
    """Base64 del átomo ANTIGUO (la producción V3.6.69 de la ronda 77),
    anclado al banco pedido (VOICE_B64 o EN). Se busca el commit BASE de la
    ronda: el tag v3.6.69-SDK6 (release r77); si no existiera, HEAD~1.
    (HEAD ya NO vale tras el commit r78: contendría los átomos nuevos.)"""
    bases = ["v3.6.69-SDK6", "HEAD~1"]
    for ref in bases:
        r = subprocess.run(
            ["git", "-C", RAIZ, "show", f"{ref}:src/game/core/c00_pre_three.js"],
            capture_output=True)
        if r.returncode != 0:
            continue
        txt = r.stdout.decode("utf-8", "replace")
        if "const VERSION = '3.6.69-SDK6'" not in txt:
            continue   # no es la producción r77 (p. ej. HEAD ya rodado)
        i = txt.find(f"const {banco} = {{")
        if i < 0:
            return None
        m = re.search(r"\n[ \t]*" + clave + r': "([A-Za-z0-9+/=]+)"', txt[i:i + 3_000_000])
        return m.group(1) if m else None
    return None


PLAN77 = ["['tutv8a', 'tutv8b', 'tutv8c', 'tutv9a', 'tutv9b'],   // 7 modos (r74: explicados con calma)"]
PLAN78 = ["['tutv8a', 'tutv8b', 'tutv8c', 'tutv9a', 'tutv9c', 'tutv9b'],   // 7 modos (r74: con calma · r78: campeonatos = superpoderes)"]

AGUJAS = [
    # --- r78 · el plan del paso 7 (c13) ---
    ("VOCES_PASO[7] nuevo (6 átomos con tutv9c)", PLAN78[0]),
    ("VOCES_PASO[7] viejo (5 átomos) FUERA", None),   # aguja negativa abajo
    # --- r78 · la pizarra cuenta la misma verdad (c00) ---
    ("caja PODERES ES · solo campeonatos",
     "tut_pow_t: 'PODERES · SOLO CAMPEONATOS: 20 toques seguidos cargan · gatillo lanza · 10 s'"),
    ("caja PODERES EN · championships only",
     "tut_pow_t: 'POWERS · CHAMPIONSHIPS ONLY: 20 straight hits charge · trigger fires · 10 s'"),
    # --- r78 · la verdad del juego, intacta (c12) ---
    ("megaEnabled: SOLO campeonatos (v3.6.36, regla del dueño)",
     "return !!(this.champs && this.champs.active);"),
    ("MEGA_GOLPES = 20 (regla del dueño r56)",
     "const MEGA_GOLPES = 20;"),
    ("MEGA_DUR = 15 (Mega Pala apila)",
     "const MEGA_DUR = 15;"),
    ("EFECTO_DUR = 10 (ventana de 10 s)",
     "const EFECTO_DUR = 10;"),
    ("versión sellada 3.6.76-SDK6",
     "const VERSION = '3.6.76-SDK6';"),
]

JS_BANCO = """async () => {
  const G = window.__PP_GAME;
  if (!G || !G.audio) return { error: 'sin __PP_GAME.audio' };
  // el banco decodifica al crear el CONTEXTO de audio (gesto): en headless
  // nadie hace clic — el QA le da el gesto sintético del documento
  for (let i = 0; i < 30 && !G.audio.ctx; i++) {
    document.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
    await new Promise(r => setTimeout(r, 400));
  }
  for (let i = 0; i < 90 && !G.audio.vb; i++) {
    await new Promise(r => setTimeout(r, 500));
  }
  if (!G.audio.vb) return { error: 'banco de voz sin decodificar' };
  const keys = ['tutv8a','tutv8b','tutv8c','tutv9a','tutv9c','tutv9b'];
  const durs = {};
  const faltan = [];
  for (const k of keys) {
    const b = G.audio.vb.get(k);
    if (!b) faltan.push(k); else durs[k] = Math.round(b.duration * 100) / 100;
  }
  // plan COMPLETO del paso 7 (la pizarra de modos) — extremo a extremo
  const plan = keys.map(k => ({ k, gap: 0.32 }));
  let speakOk = false;
  try { speakOk = !!G.audio.speakPlan(plan); } catch (e) { speakOk = false; }
  return { faltan, durs, speakOk };
}"""


async def main():
    src = ""
    try:
        import urllib.request
        with urllib.request.urlopen(URL, timeout=15) as r:
            src = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"✗ FALLO: no se pudo leer {URL}: {e}")
        sys.exit(1)

    print("— BLOQUE 1 · AGUJAS r78 + átomos BYTE-EXACTO en el servido —")
    for label, needle in AGUJAS:
        if needle is None:
            continue
        chk(needle in src, label)
    chk(PLAN77[0] not in src, "VOCES_PASO[7] viejo (5 átomos) FUERA")
    # 10 átomos (ES+EN) byte-exacto contra el banco en disco
    for idi, d in (("ES", "ogg_es"), ("EN", "ogg_en")):
        for k in ATOMOS:
            p = os.path.join(RAIZ, "scripts/voice_r65", d, k + ".ogg")
            if not os.path.exists(p):
                chk(False, f"{idi}:{k} OGG en disco")
                continue
            chk(b64_de(p) in src, f"átomo {idi}:{k} byte-exacto en el servido")
    # el VIEJO tutv8b (prometía poderes en el partido normal) PROHIBIDO
    for banco in ("VOICE_B64", "VOICE_B64_EN"):
        viejo = b64_viejo_git("tutv8b", banco)
        if viejo and len(viejo) > 500:
            chk(viejo not in src, f"VIEJO tutv8b ({banco}) PROHIBIDO en el servido")
        else:
            chk(False, f"VIEJO tutv8b ({banco}) extraíble de git")
    # tutv8c NO cambia esta ronda: su OGG en disco debe seguir EN el servido
    # (ya cubierto arriba byte-exacto) y el viejo tutv8c de git DEBE seguir
    # presente (igualdad byte a byte, garantía de «solo lo necesario cambia»)
    viejo8c = b64_viejo_git("tutv8c", "VOICE_B64")
    if viejo8c and len(viejo8c) > 500:
        chk(viejo8c in src, "tutv8c SIN CAMBIOS (bytes idénticos a r77)")

    print("— BLOQUE 2 · CONTADORES + ORDEN del plan —")
    for label, pat, esperado in [
        ("tutv9c: 2 bancos (ES+EN) + 1 plan = 3", "tutv9c:", 2),
        ("'tutv9c' en el plan del paso 7 (c13)", "'tutv9c'", 1),
        ("caja PODERES ES nueva ×1", "PODERES · SOLO CAMPEONATOS", 1),
        ("caja PODERES EN nueva ×1", "POWERS · CHAMPIONSHIPS ONLY", 1),
        ("caja PODERES ES vieja ×0", "gatillo con la bola viva", 0),
        ("caja PODERES EN vieja ×0", "trigger with a live ball", 0),
        ("«y más» nunca en el plan fuente", "multijugador, y más", 0),
    ]:
        n = len(re.findall(re.escape(pat), src))
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")
    # ORDEN dentro del plan del paso 7
    i_plan = src.find("['tutv8a', 'tutv8b', 'tutv8c', 'tutv9a', 'tutv9c', 'tutv9b'")
    chk(i_plan >= 0, "plan del paso 7 presente en fuente")
    if i_plan >= 0:
        linea = src[i_plan:src.find("]", i_plan) + 1]
        pos = [linea.find(k) for k in ["tutv8a", "tutv8b", "tutv8c", "tutv9a", "tutv9c", "tutv9b"]]
        chk(all(p >= 0 for p in pos) and pos == sorted(pos),
            "orden del plan: 8a → 8b → 8c → 9a → 9c → 9b")

    print("— BLOQUE 3 · JUEGO REAL headless (banco de voz + plan completo) —")
    os.makedirs(DIR_CAPS, exist_ok=True)
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            juego = False
            for _ in range(90):
                juego = await page.evaluate("() => !!window.__PP_GAME")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_GAME")

            res = await page.evaluate(JS_BANCO, [])
            if res.get("error"):
                chk(False, "JS_BANCO: " + res["error"])
            else:
                chk(not res["faltan"], f"6/6 átomos del paso 7 decodificados {res.get('faltan')}")
                d = res.get("durs", {})
                chk(d.get("tutv9c", 0) > 8.0,
                    f"tutv9c NUEVO y LARGO (explica poderes) → {d.get('tutv9c')} s")
                chk(0 < d.get("tutv8b", 99) < 6.5,
                    f"tutv8b NUEVO y CORTO (sin la carga falsa) → {d.get('tutv8b')} s")
                chk(3.0 < d.get("tutv8a", 0) < 8.0,
                    f"tutv8a NUEVO (lista campeonatos) → {d.get('tutv8a')} s")
                chk(res.get("speakOk") is True,
                    "speakPlan del plan COMPLETO del paso 7 = true (extremo a extremo)")

            if page_errors:
                for e in page_errors:
                    print("  ✗ pageerror: " + e[:200])
            chk(len(page_errors) == 0, "0 pageerrors en toda la sesión")
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} FALLOS (qa_r78_v3670 · CAPA BM)")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
