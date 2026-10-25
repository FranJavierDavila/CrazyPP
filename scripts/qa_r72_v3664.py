#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r72_v3664 — CAPA BG · V3.6.66-SDK6, FASE 66 «EL TELÓN Y EL CANDADO».

Informe del dueño tras probar V3.6.63 en el Quest, punto por punto:
  1. «En el tutorial en el paso 3 existe solapamiento de texto en el cartel».
  2. «En el paso 4 el texto "El intercambio" también se pisa con el texto
     que tiene arriba».
  3. «En el paso 7 los textos están algo pegados».
  4. «En el paso 8 de Modos están mal colocados, revisa y encájalos bien».
  5. «Faltan los iconos de los botones de Entrenamiento: Dirección, Altura,
     Saque, Efecto y Ritmo».
  6. «En el campeonato de Estación Orbital no se visualiza "Astro"».
  7. «Al cargar los escenarios se ve cómo se va cargando: mejor pantalla
     negra "Montando el escenario..." hasta que esté todo cargado».
  8. «Estación Orbital y Valle Neón bloqueados con candado sobre el nombre,
     voz "Próximamente" al intentar entrar; sólo Modo Depuración (FORO3D)».

El arreglo (r72) y SU verificación:
  · CAUSA RAÍZ DE LOS SOLAPES (1-4): los títulos de paso (y 214..244)
    chocan con la cabecera «LA ACADEMIA CRAZY» (y 192..232) que
    paintHeader dibuja en TODOS los pasos. Todos los títulos bajan a su
    fila (y=262..272) y los cuerpos se reexpanden con aire medido.
  · PASO 8: el wrap2 del texto PODERES no tenía parámetro x y pintaba
    SIEMPRE en el centro de la pizarra (680) — ENCIMA de la tarjeta
    ENTRENAR; además la píldora «GATILLO · continuar» (552..594) pisaba
    la fila inferior (terminaba en 566). Ahora el texto vive DENTRO de su
    caja ámbar (centro x=996) y la píldora sube a la fila del título.
  · ICONOS DE ENTRENAMIENTO: 6 funciones vectoriales nuevas en PP_ICONS
    (dir/alt/spin/saque/rit + candado) y las 5 tarjetas de AREAS dibujan
    el suyo dentro del medallón. Verificado pintándolos en canvas real
    (píxeles no uniformes) y navegando el hub de entrenamiento.
  · ASTRO VISIBLE: el grupo del campeonato orbital colgaba de g.scene
    (mundo crudo) mientras mesa/sala viven en g.rig — el RECENTRADO del
    Quest giraba el rig y lo dejaba descolocado. Ahora game.rig.add
    (convención CLOWN/WIZARD), guard idempotente en build() y el stop()
    del muro restaura al rival. Verificado con el módulo REAL: el padre
    del grupo ES el rig y rivalMesh está visible.
  · TELÓN DE CARGA: showChampCurtain (plano 3D negro depthTest:false,
    visible en XR) + ChampLoader.launch lo muestra ANTES de importar el
    módulo y lo levanta en fundido cuando la sala tiene sus 6 caras
    (mín 0,9 s + 0,3 s estables · tope 12 s). Verificado lanzando La
    Locura real: el telón nace, pinta «Montando el escenario...» y se
    desmonta solo.
  · CANDADOS: LOCKED = ['estacion_orbital','valle_neon'] en ChampLoader,
    guard en launch() con voz announce('Próximamente'), tarjeta atenuada
    con candado sobre el nombre + chip plateado, y BYPASS con el Modo
    Depuración (nombre FORO3D → ppDebugMode). Verificado con el loader
    real: bloqueado no arranca y con FORO3D sí.

BLOQUES: (1) AGUJAS de fuente r72 en el game.html servido. (2) CONTADORES
(geometría vieja ausente, nueva presente ×N). (3) MÓDULO ORBITAL: padre
rig + guard + stop del muro + manifest v17 cruzado con VERSION.json.
(4) JUEGO REAL headless: candados por datos, launch bloqueado vs FORO3D,
telón vivo→desmontado, iconos pintados con píxeles, errores de página.
Uso: python3 scripts/qa_r72_v3664.py [URL]"""
import asyncio
import re
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
ORBITAL = "/home/z/my-project/public/championships/estacion_orbital/index.js"
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # --- r72 · TELÓN DE CARGA ---
    ("telón: showChampCurtain existe", "showChampCurtain(id) {"),
    ("telón: tick en animate", "this._updateChampCurtain();"),
    ("telón: texto i18n con puntos animados", "T('champ_telon').replace(/\\.+$/, '') + pts"),
    ("telón: tope de seguridad 12 s (tiempo real)", "if (rt - S.listoDesde >= 0.3 || S.t >= 12) S.fade = rt;"),
    # r73 · TELÓN DE TEATRO: la v72 anclaba un plano a 0.72 m; la v73 trae
    # esfera negra de 12 m (BackSide, renderOrder 65) + cartel a 2 m que
    # sigue a la cabeza. Aguja re-anclada a la verdad r73.
    ("telón: esfera negra que traga el mundo", "new THREE.SphereGeometry(12, 28, 18), matEs"),
    ("telón: cartel a 2 m delante (tick a la cabeza)", "S.group.position.set(S._v1.x + S._v2.x * 2.0, dy, S._v1.z + S._v2.z * 2.0);"),
    ("telón: renderOrder por encima de la intro", "mesh.renderOrder = 70;"),
    # --- r72 · CANDADOS ---
    ("candado: LOCKED con los dos campeonatos", "static LOCKED = ['estacion_orbital', 'valle_neon'];"),
    ("candado: bypass Modo Depuración (FORO3D)", "try { return !ppDebugMode(); } catch (e) { return true; }"),
    ("candado: guard en launch() con voz", "try { g.audio.announce(T('champ_locked_soon'), true); } catch (eV) { /* */ }"),
    ("candado: flag locked en list()", "locked: this.isLocked(e.id),"),
    ("candado: tarjeta atenuada", "const lockado = !!ch.locked;"),
    ("candado: dibujo sobre el nombre", "PP_ICONS.candado(c, 186 + twCh + 26, y + 34, 1.35)"),
    ("candado: chip plateado PRÓXIMAMENTE", "const chipTxtL = T('champ_locked_chip');"),
    ("candado: sin chevron ni VER PRESENTACIÓN", "if (!lockado) {\n        btn('champintro:' + ch.id,"),
    # --- r72 · ICONOS de Entrenamiento (PP_ICONS) ---
    ("icono DIRECCIÓN (diana + flecha)", "dir(c, x, y) {            // DIRECCIÓN: diana + flecha al objetivo"),
    ("icono ALTURA (arco sobre la red)", "alt(c, x, y) {            // ALTURA: arco limpio por encima de la red"),
    ("icono EFECTO (bola con giro)", "spin(c, x, y) {           // EFECTO: bola con estela de giro"),
    ("icono SAQUE (doble bote)", "saque(c, x, y) {          // SAQUE: la trayectoria del doble bote"),
    ("icono RITMO (metrónomo)", "rit(c, x, y) {            // RITMO: metrónomo"),
    # r73 · el candado es translate+scale (la v72 lo desplazaba ×1,35)
    ("icono CANDADO", "candado(c, x, y, s) {     // r73 · candado (campeonatos PRÓXIMAMENTE)"),
    ("AREAS lleva ic por área", "{ id: 'dir', ic: 'dir', ik: 'a_dir'"),
    ("tarjeta dibuja el icono en el medallón", "const ico = ic && PP_ICONS[ic];"),
    # --- r72 · CARTEL sin solapes (reflow) ---
    ("paso 1: título a su fila 272", "line(c, T('tut_m_t'), 272, 40, '#ffd257');"),
    ("paso 2 demo: título a 272", "line(c, T('tut_d3_t'), 272, 38, '#ffd257');"),
    ("paso 2 práctica: título a 272", "line(c, T('tut_s3_t'), 272, 40, '#ffd257');"),
    ("paso 2 práctica: contador repartido", "c.fillText(Math.min(saqCount, SAQ_META) + ' / ' + SAQ_META, PIZ_CX, 466);"),
    ("paso 3/4: EL INTERCAMBIO a 272", "line(c, T('tut_d4_t'), 272, 40, '#ffd257');"),
    ("paso 4: EL MARCADOR a 272", "line(c, T('tut_d5_t'), 272, 40, '#ffd257');"),
    ("paso 5: práctica del profe a 272", "line(c, T('tut_s4_t'), 272, 42, '#ffd257');"),
    ("paso 6: botones a 272", "line(c, T('tut_s5_t'), 272, 40, '#ffd257');"),
    ("paso 7: LOS MODOS a 262", "line(c, T('tut_mods_t'), 262, 34, '#ffd257');"),
    ("paso 7: píldora junto al título (x=986)", "pill(c, T('tut_hint_next'), 252, { w: 300, h: 32, x: 986"),
    ("paso 7: PODERES DENTRO de su caja (x=996)", "wrap2(c, T('tut_pow_t'), 536, 14, '#ffe08a', 312, 11, 996);"),
    ("helpers: wrap2 acepta x", "function wrap2(c, txt, y, size, col, maxW, lh, x) {"),
    ("helpers: pill acepta centro propio", "const cx = (opts.x != null) ? opts.x : PIZ_CX;"),
    # --- r72 · i18n ES/EN ---
    ("i18n ES: Próximamente", "champ_locked_soon: 'Próximamente',"),
    ("i18n ES: chip", "champ_locked_chip: 'PRÓXIMAMENTE',"),
    ("i18n ES: telón", "champ_telon: 'Montando el escenario...',"),
    ("i18n EN: coming soon", "champ_locked_soon: 'Coming soon',"),
    ("i18n EN: telón", "champ_telon: 'Setting up the arena...',"),
]

AGUJAS_ORBITAL = [
    ("ASTRO: grupo anclado AL RIG (convención CLOWN/WIZARD)", "g.rig.add(this.group);"),
    ("ASTRO: nada colgado ya de g.scene", "g.scene.add(this.group);"),
    ("ASTRO: guard idempotente del standee", "if (!this._rivalSDK) {"),
    ("muro: stop() restaura al rival", "if (aStop && aStop.rivalMesh) aStop.rivalMesh.visible = true;"),
]

CONTADORES = [
    ("siete títulos de paso en su fila (272/262)",
     [r"line\(c, T\('tut_m_t'\), 272", r"line\(c, T\('tut_d3_t'\), 272", r"line\(c, T\('tut_s3_t'\), 272",
      r"line\(c, T\('tut_d4_t'\), 272", r"line\(c, T\('tut_d5_t'\), 272", r"line\(c, T\('tut_s4_t'\), 272",
      r"line\(c, T\('tut_s5_t'\), 272", r"line\(c, T\('tut_mods_t'\), 262"], 8),
    ("GEOMETRÍA VIEJA FUERA (títulos que pisaban la cabecera)",
     [r"T\('tut_m_t'\), 236", r"T\('tut_d3_t'\), 244", r"T\('tut_s3_t'\), 214",
      r"T\('tut_d4_t'\), 236", r"T\('tut_d5_t'\), 250", r"T\('tut_s4_t'\), 224",
      r"T\('tut_s5_t'\), 240", r"T\('tut_mods_t'\), 208"], 0),
    ("6 iconos nuevos en PP_ICONS (dir/alt/spin/saque/rit/candado)",
     [r"\bdir\(c, x, y\)", r"\balt\(c, x, y\)", r"\bspin\(c, x, y\)",
      r"\bsaque\(c, x, y\)", r"\brit\(c, x, y\)", r"\bcandado\(c, x, y, s\)"], 6),
]


async def main():
    src = ""
    try:
        import urllib.request
        with urllib.request.urlopen(URL, timeout=15) as r:
            src = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"✗ FALLO: no se pudo leer {URL}: {e}")
        sys.exit(1)

    print("— BLOQUE 1 · AGUJAS r72 en el game.html servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES de geometría —")
    for label, pats, esperado in CONTADORES:
        n = len(re.findall(pats[0], src)) if False else sum(len(re.findall(p, src)) for p in pats)
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")

    print("— BLOQUE 3 · MÓDULO ORBITAL (Astro) + manifest cruzado —")
    try:
        with open(ORBITAL, "r", encoding="utf-8") as f:
            osrc = f.read()
        for label, needle in AGUJAS_ORBITAL:
            presente = needle in osrc
            if needle == "g.scene.add(this.group);":
                chk(not presente, label + " (ausencia)")
            else:
                chk(presente, label)
        import json
        man = json.load(open("/home/z/my-project/public/championships/estacion_orbital/manifest.json"))
        ver = json.load(open("/home/z/my-project/src/game/VERSION.json"))
        chk(man.get("version") == 17, "manifest orbital → v17")
        chk(ver["manifests"]["estacion_orbital"] == 17, "VERSION.json manifests orbital → 17")
        chk("ASTRO EN EL ESPACIO CORRECTO" in osrc, "nota de historial r72 en el módulo")
    except Exception as e:
        chk(False, f"bloque orbital: {e}")

    print("— BLOQUE 4 · JUEGO REAL headless (candados, telón, iconos) —")
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            await page.wait_for_function("() => window.__PP_GAME && window.__PP_GAME.champs", timeout=30000)
        except Exception:
            pass
        juego = await page.evaluate("() => !!(window.__PP_GAME && window.__PP_GAME.champs)")
        chk(juego, "el juego arranca con ChampLoader (window.__PP_GAME)")

        if juego:
            # esperar al ÍNDICE real de campeonatos (fetch async del loader)
            try:
                await page.wait_for_function(
                    "() => window.__PP_GAME.champs.entries.length >= 4", timeout=20000)
            except Exception:
                pass
            # --- CANDADOS por datos (list real del índice publicado) ---
            datos = await page.evaluate("""() => {
                const L = window.__PP_GAME.champs.list();
                const d = {};
                for (const c of L) d[c.id] = !!c.locked;
                return d;
            }""")
            chk(datos.get("estacion_orbital") is True, "list(): estacion_orbital locked=true")
            chk(datos.get("valle_neon") is True, "list(): valle_neon locked=true")
            chk(datos.get("locura") is False, "list(): locura libre")
            chk(datos.get("oeste") is False, "list(): oeste libre")

            # --- LAUNCH BLOQUEADO (sin FORO3D): no arranca ---
            await page.evaluate("() => { try { localStorage.removeItem('pp_player_name'); } catch (e) {} }")
            res_bloqueado = await page.evaluate("""async () => {
                const g = window.__PP_GAME;
                try { await g.champs.launch('estacion_orbital'); } catch (e) { return { err: String(e) }; }
                return { activo: g.champs.activeId || '', telon: !!g.champCurtain };
            }""")
            chk(res_bloqueado.get("activo") != "estacion_orbital",
                "BLOQUEADO: launch no activa el campeonato")
            chk(not res_bloqueado.get("telon"), "BLOQUEADO: ni telón (guard antes de nada)")

            # --- BYPASS FORO3D (Modo Depuración): sí arranca ---
            await page.evaluate("""() => {
                localStorage.setItem('pp_player_name', 'FORO3D');
                if (window.ppDebugRefresh) window.ppDebugRefresh();
            }""")
            dbg = await page.evaluate("() => window.__PP_DEBUG === true")
            chk(dbg, "Modo Depuración activo con FORO3D (__PP_DEBUG)")
            # restaurar nombre neutro y re-probar el desbloqueo por debug:
            # launch con debug activo SÍ pasa el guard → el módulo importa.
            res_debug = await page.evaluate("""async () => {
                const g = window.__PP_GAME;
                try { await g.champs.launch('estacion_orbital'); } catch (e) { return { err: String(e) }; }
                return { activo: g.champs.activeId || '' };
            }""")
            chk(res_debug.get("activo") == "estacion_orbital",
                "FORO3D: launch SÍ activa estacion_orbital")

            # --- ASTRO EN EL RIG (módulo real) ---
            astro = await page.evaluate("""() => {
                const m = window.__PP_GAME.champs.moduleIfLoaded('estacion_orbital');
                if (!m || !m.controller) return null;
                const C = m.controller;
                return {
                    parentEsRig: !!(C.group && C.group.parent === window.__PP_GAME.rig),
                    rivalVivo: !!C.rivalMesh,
                    rivalVisible: !!(C.rivalMesh && C.rivalMesh.visible),
                    enRigNoScene: !!(C.group && C.group.parent &&
                        C.group.parent === window.__PP_GAME.rig),
                };
            }""")
            chk(bool(astro and astro.get("parentEsRig")), "ASTRO: el grupo del campeonato cuelga del RIG")
            chk(bool(astro and astro.get("rivalVivo")), "ASTRO: standee creado")
            chk(bool(astro and astro.get("rivalVisible")), "ASTRO: rivalMesh visible en sala")

            # --- TELÓN: nace con La Locura y se desmonta solo ---
            await page.evaluate("() => { try { window.__PP_GAME.champs.leaveAll(); } catch (e) {} }")
            telon_vivo = await page.evaluate("""async () => {
                const g = window.__PP_GAME;
                localStorage.removeItem('pp_intro_locura');   // sin intro: telón puro
                g.champs.introPendiente = () => false;        // la primera vez también
                try { await g.champs.launch('locura'); } catch (e) { return { err: String(e) }; }
                return { activo: g.champs.activeId || '', telon: !!g.champCurtain,
                    texto: g.champCurtain ? String(g.champCurtain.ttl || '') : '' };
            }""")
            chk(telon_vivo.get("activo") == "locura", "TELÓN: La Locura arranca")
            chk(bool(telon_vivo.get("telon")), "TELÓN: nace negro con el launch")
            chk("LOCURA" in (telon_vivo.get("texto") or "").upper(), "TELÓN: lleva el título del campeonato")
            desmonta = await page.evaluate("""() => new Promise((res) => {
                const t0 = Date.now();
                const iv = setInterval(() => {
                    if (!window.__PP_GAME.champCurtain) { clearInterval(iv); res(true); }
                    else if (Date.now() - t0 > 16000) { clearInterval(iv); res(false); }
                }, 250);
            })""")
            chk(desmonta, "TELÓN: se desmonta solo (sala cargada · <16 s)")

            # --- ICONOS pintados (píxeles reales en canvas) ---
            ico = await page.evaluate("""() => {
                const cv = document.createElement('canvas');
                cv.width = 120; cv.height = 120;
                const c = cv.getContext('2d');
                const out = {};
                const muestra = (name, fn) => {
                    c.clearRect(0, 0, 120, 120);
                    c.fillStyle = '#10131a'; c.fillRect(0, 0, 120, 120);
                    try { fn(c, 60, 60); } catch (e) { out[name] = 'EXC:' + e; return; }
                    const d = c.getImageData(30, 30, 60, 60).data;
                    let noBg = 0;
                    for (let i = 0; i < d.length; i += 4) {
                        if (d[i] !== 16 || d[i + 1] !== 19 || d[i + 2] !== 26) noBg++;
                    }
                    out[name] = noBg;
                };
                const I = (window.__PP_GAME._ppIconsProbe && window.__PP_GAME._ppIconsProbe()) || null;
                if (!I) return null;
                for (const k of ['dir', 'alt', 'spin', 'saque', 'rit', 'candado']) {
                    if (typeof I[k] === 'function') muestra(k, I[k]);
                    else out[k] = 0;
                }
                return out;
            }""")
            if ico is None:
                chk(False, "iconos: sonda PP_ICONS disponible en __PP_GAME")
            else:
                for k in ["dir", "alt", "spin", "saque", "rit", "candado"]:
                    v = ico.get(k)
                    chk(isinstance(v, int) and v > 40, f"icono {k} pinta píxeles ({v})")

        await browser.close()

    print("— BLOQUE 5 · ERRORES DE PÁGINA —")
    errores = [e for e in page_errors if "favicon" not in e.lower()]
    chk(not errores, f"0 excepciones de página ({len(errores)} vistas)")
    for e in errores[:4]:
        print("    ·", e[:160])

    print(f"\nRESULTADO: {ok} OK · {fails} FALLOS")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    asyncio.run(main())
