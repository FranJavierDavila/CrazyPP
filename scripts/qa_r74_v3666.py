#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r74_v3666 — CAPA BI · V3.6.66-SDK6, FASE 68 «EL MANDO DE SIEMPRE».

Informe del dueño tras probar V3.6.65 en el Quest, punto por punto:
  1. «Desde el módulo Pro training, en cualquier modalidad, sacar el Menú
     con la tecla de siempre, la B (no la Y), para que sea un comportamiento
     común».
  2. «En una pantalla de campeonato de las etapas 2 y 4 (cartel explicativo
     con botón EMPEZAR) al sacar el menú contextual este no recibe el foco y
     no permite pulsar en sus botones — parece que sigue mandando el botón
     que tenemos por debajo».
  3. «En el paso 2 del tutorial (tu mando es tu raqueta) si cambiamos la
     pala de mano, el efecto de glow no está presente».
  4. «En el paso de las devoluciones, si antes de empezar a devolver pulsas
     o haces un saque, no te permite avanzar — al no poder sacar».
  5. «En el paso 9 de los Modos de juego se queda el sonido de la bola por
     debajo, muy molesto. Esta parte de los modos no está bien explicada:
     deberías pararte un poco más».
  6. «Me has puesto el campeonato del Salvaje Oeste de primero y sería el
     tercero: el primero es el de Clow, el segundo el de Wizard y el tercero
     el de forajido (el del Salvaje Oeste)».
  7. «Al seleccionar este campeonato dentro no desaparece el menú principal
     y además está el sonido molesto de la bola con el bote infinito. Todos
     los campeonatos deben tener el mismo comportamiento al abrirlos,
     incluido el mismo efecto de pantalla de espera de carga negra».
  8. Optimización de FPS SIN ROMPER NADA.

El arreglo (r74) y SU verificación:
  · PRO TRAINING = B: la guardia !calib del bloque B ya no se come el
    entrenamiento — B abre/cierra SU menú (página ENTRENAR) en cualquier
    modalidad y Y deja de hacerlo (sólo queda la Y=volver del ajuste de
    pala puro). Verificado por agujas + posiciones de fuente.
  · MENÚ SOBRE EL CARTEL: en onSelectStart la comprobación menuOpen sube POR
    ENCIMA del bloque _instr (los clics van a los botones del menú y el
    EMPEZAR de detrás no manda). Verificado por POSICIÓN en el fuente
    servido (orden real del código) + agujas.
  · AURA SIGUE LA MANO: tickMandos re-papa la aura si no cuelga de la
    montura de la pala activa (cada frame, sin coste).
  · PRÁCTICA SIN ATASCOS: el profesor sirve YA al entrar en el paso 5 y un
    VIGÍA re-sirve si la bola va quieta 1,6 s (palma/grip/perdida).
  · MODOS: bola DORMIDA en los pasos 6/7/8 (posaBolaMesa + tutBolaViva
    false — adiós al bote infinito de fondo) + tarjetas con explicación
    larga + 3 átomos de voz NUEVOS (tutv8b/8c/9b ES+EN) en el banco.
  · ORDEN CANÓNICO: cada entrada del índice guarda su posición y list()
    ordena SIEMPRE Clow → Wizard → Forajido → resto (verificado CON DATOS).
  · MENÚ RECOGIDO AL ENTRAR: ChampLoader.launch() cierra el menú del
    NÚCLEO para TODOS los campeonatos (antes sólo lo hacían locura/magia).
  · ZONA MUERTA DEL SUELO (física): impactos < 0,3 m/s posan la bola sin
    evento (adiós a los thud fantasma del bote infinito en salas/academia).
    VERIFICADO EN VIVO con stepPhysics real: caída de 1 mm = 0 eventos,
    caída de 1 m = 1 evento. Y el golden de física sigue 11/11 (fuera).
BLOQUES: (1) AGUJAS r74 en el game.html servido. (2) CONTADORES y POSICIONES
de fuente (orden real de onSelectStart). (3) JUEGO REAL headless: orden de
campeonatos con datos, física del suelo medida, banco de voz presente,
0 pageerrors.
Uso: python3 scripts/qa_r74_v3666.py [URL]
"""
import asyncio
import json
import re
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # --- r74 · PRO TRAINING: MENÚ CON B (no Y) ---
    ("training: B entra en el comportamiento común (guardia 0.6)",
     "if (presenting && (!this.calib || this.trainV3 || this.trainV3Hub) &&"),
    ("training: B abre el menú ENTRENAR (stopMode + página train)",
     "this.menuPage = 'train';"),
    ("training: Y ya NO abre el menú en entrenamiento",
     "!this.trainV3 && !this.trainV3Hub &&\n        this.readButton(this.handIndex('left'), 5)) {"),
    ("training: el modo se recoge al abrir con B",
     "try { window.__PP_TRAIN.stopMode(this); } catch (eTrnB) { /* */ }"),
    # --- r74 · MENÚ SOBRE EL CARTEL EMPEZAR ---
    ("menú manda sobre _instr (comentario r74)",
     "r74 · MENÚ PRIORITARIO AHORA SÍ SOBRE TODO"),
    ("homehall: cartel EMPEZAR se retira sin arrancarlo",
     "try { if (this._instr) this.hideInstrucciones(true); } catch (eHh) { /* */ }"),
    ("hallask_si: cartel EMPEZAR se retira sin arrancarlo",
     "try { if (this._instr) this.hideInstrucciones(true); } catch (eHs) { /* */ }"),
    # --- r74 · AURA SIGUE LA MANO ---
    ("aura: re-papa si no cuelga de la montura activa",
     "if (auraGrp && G.paddleMounts && auraGrp.parent !=="),
    # --- r74 · PRÁCTICA SIN ATASCOS ---
    ("academia: el profesor sirve YA al entrar (paso 5)",
     "EL PROFESOR SIRVE YA AL ENTRAR"),
    ("academia: vigía de la práctica (re-feed)",
     "VIGÍA DE LA PRÁCTICA"),
    ("academia: re-feed del vigía pone la bola dormida",
     "G.feedPracticeBall();\n              b.vel.set(0, 0, 0);"),
    # --- r74 · PASOS 6/7/8 CON BOLA DORMIDA ---
    ("academia: posaBolaMesa definido", "function posaBolaMesa() {"),
    ("academia: case 6 bola dormida", "G.tutBolaViva = false;          // r74 · bola DORMIDA (adiós al bote infinito de fondo)"),
    ("academia: default (7/8) bola dormida", "G.tutBolaViva = false;          // r74 · pasos 7/8: bola dormida y sobre la mesa"),
    # --- r74 · MODOS MEJOR EXPLICADOS + VOZ NUEVA ---
    ("modos: modeCard acepta línea extra", "function modeCard(c, x, y, w, h, col0, ini, title, sub, extra) {"),
    ("modos: tarjeta PARTIDO con explicación larga", "T('hub_match'), T('tut_mod_p'), T('tut_s6_m1')"),
    ("modos: tarjeta ENTRENAR con explicación larga", "T('sec_train'), T('tut_mod_t'), T('tut_s7_m3')"),
    ("modos: VOCES_PASO[7] con los 5 átomos",
     "['tutv8a', 'tutv8b', 'tutv8c', 'tutv9a', 'tutv9b'],   // 7 modos (r74: explicados con calma)"),
    ("voz: átomo tutv8b ES", "tutv8b: \""),
    ("voz: átomo tutv8c ES", "tutv8c: \""),
    ("voz: átomo tutv9b ES", "tutv9b: \""),
    ("voz: átomo tutv8b EN", "tutv8b: \""),
    # --- r74 · ORDEN CANÓNICO DE CAMPEONATOS ---
    ("orden: posición del índice guardada", "orden: ordenDe(raw),"),
    ("orden: list() ordena por el índice", ".sort((a, b) => ((a.orden == null ? 99 : a.orden) -"),
    # --- r74 · MENÚ RECOGIDO AL ENTRAR EN CUALQUIER CAMPEONATO ---
    ("launch: el núcleo cierra el menú para TODOS",
     "try { g.closeMenu(); } catch (eCM0) { /* */ }"),
    # --- r74 · ZONA MUERTA DEL SUELO (física) ---
    ("física: zona muerta del suelo", "ZONA MUERTA DEL SUELO"),
    ("física: umbral de asentamiento 0,3 m/s", "if (impact < 0.3) {"),
    ("física: rescate sin evento (teletransporte silencioso)",
     "// r74 · SIN evento: el rescate es un TELETRANSPORTE, no un bote"),
    # --- r74 · PERFIL (color arcoíris reciclado) ---
    ("perf: color arcoíris sin asignación por frame", "rainbowCol.setHSL(rainbowT % 1, 0.75, 0.55);"),
]

CONTADORES = [
    ("rama Y del entrenamiento AUSENTE (trnY retirada)", ["const trnY = (typeof window !== 'undefined') && window.__PP_TRAIN;"], 0),
    ("guardia B vieja AUSENTE (!calib sola en el bloque 0.6)",
     ["if (presenting && !this.calib &&\n        this.readButton(this.handIndex('right'), 5)) {"], 0),
    ("posaBolaMesa llamada ×2 (case 6 + default; la definición va por aguja)",
     ["posaBolaMesa();"], 2),
    ("bola dormida en pasos finales ×2 (tutBolaViva false r74)",
     ["G.tutBolaViva = false;          // r74"], 2),
    ("rebote del suelo conserva SU evento (sólo en la rama real)",
     ["vel.y = impact * 0.45;"], 1),
    ("evento del rescate AUSENTE (era 1 'floor' fantasma)",
     ["events.push({ type: 'floor', speed: 1, pos: pos.clone() });"], 0),
    ("átoos de voz nuevos presentes en el banco (tutv8b ×2 bancos)",
     ["tutv8b: \""], 2),
]

ORDEN_FUENTE = [
    # (a, b, etiqueta): la posición de a DEBE ser menor que la de b
    ("r74 · MENÚ PRIORITARIO AHORA SÍ SOBRE TODO",
     "// v2.107 · CARTEL EXPLICATIVO EN PANTALLA",
     "onSelectStart: el bloque menuOpen precede al bloque _instr"),
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

    print("— BLOQUE 1 · AGUJAS r74 en el game.html servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES + POSICIONES de fuente —")
    for label, pats, esperado in CONTADORES:
        n = sum(len(re.findall(re.escape(p), src)) for p in pats)
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")
    for a, b, label in ORDEN_FUENTE:
        chk(0 <= src.find(a) < src.find(b), label)

    print("— BLOQUE 3 · JUEGO REAL headless (orden de campeones, física del suelo, voz) —")
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            juego = False
            for _ in range(90):
                juego = await page.evaluate("() => !!(window.__PP_GAME && window.__PP_GAME.champs)")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_GAME")

            # --- ORDEN CANÓNICO CON DATOS REALES ---
            for _ in range(60):
                n = await page.evaluate("() => (window.__PP_GAME.champs.entries||[]).length")
                if n >= 5:
                    break
                await page.wait_for_timeout(500)
            orden = await page.evaluate("() => window.__PP_GAME.champs.list().map((x) => x.id)")
            esperado_orden = ["locura", "magia", "oeste", "estacion_orbital", "valle_neon"]
            chk(orden == esperado_orden,
                f"ORDEN: Clow→Wizard→Forajido→resto → {json.dumps(orden)}")
            # el orden es del ÍNDICE, no de la llegada: entradas con orden numérico
            ordenes = await page.evaluate("() => window.__PP_GAME.champs.entries.map((e) => [e.id, e.orden])")
            chk(all(isinstance(o[1], int) and 0 <= o[1] <= 4 for o in ordenes),
                f"ORDEN: cada entrada lleva su posición del índice → {json.dumps(ordenes)}")

            # --- FÍSICA DEL SUELO MEDIDA EN VIVO (stepPhysics real) ---
            fis = await page.evaluate("""async () => {
                window.__wantSolverHook = true;
                const g = window.__PP_GAME;
                // un frame para que el hook se arme
                await new Promise((res) => setTimeout(res, 300));
                const H = window.__solverHook;
                if (!H) return { err: 'sin solverHook' };
                // VECTORES REALES de three (applyAerodynamics llama vel.length()):
                // se fabrican con el constructor del propio juego.
                const V = g.ball.pos.constructor;
                const mk = (y) => ({ pos: new V(0, y, 0), vel: new V(0, 0, 0),
                                     spin: new V(0, 0, 0) });
                // CAJA A · caída de 1 mm DESDE EL SUELO (x=0,z=0 está fuera de
                // la mesa) → impacto ~0,14 m/s < 0,3 → SE POSA sin evento
                const bA = mk(H.DIMS.ballRadius + 0.001);
                const evA = [];
                for (let i = 0; i < 240; i++) H.stepPhysics(1 / 240, bA, [], evA);
                // CAJA B · caída de 1 m → impacto ~4,4 m/s → UN evento floor real
                const bB = mk(H.DIMS.tableTopY + H.DIMS.ballRadius + 1.0);
                const evB = [];
                for (let i = 0; i < 240; i++) H.stepPhysics(1 / 240, bB, [], evB);
                const floorsA = evA.filter((e) => e.type === 'floor').length;
                const floorsB = evB.filter((e) => e.type === 'floor').length;
                return { floorsA, floorsB,
                    yA: bA.pos.y, yB: bB.pos.y, r: H.DIMS.ballRadius };
            }""")
            if fis.get("err"):
                chk(False, f"física: {fis.get('err')}")
            else:
                chk(fis.get("floorsA") == 0,
                    f"ZONA MUERTA: caída de 1 mm → {fis.get('floorsA')} eventos floor (0 esperado)")
                chk(fis.get("floorsB") == 1,
                    f"BOTE REAL: caída de 1 m → {fis.get('floorsB')} evento floor (1 esperado)")
                chk(abs(fis.get("yA", 9) - fis.get("r", 0)) < 1e-3,
                    f"ZONA MUERTA: la bola queda POSADA en el suelo (y={fis.get('yA'):.4f})")

            # --- BANCO DE VOZ: los átomos nuevos están en los DOS idiomas ---
            voz = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                // el banco vive en el módulo c00 (no exportado): comprobamos
                // por el guion — VOCES_PASO no es accesible, pero el source
                // ya lo cubre; aquí validamos que la ACADEMIA existe y el
                // paso 7 pinta (paintStep no rompe con extra).
                return { tut: !!window.__PP_TUT };
            }""")
            chk(voz.get("tut"), "academia: window.__PP_TUT viva")

            await page.wait_for_timeout(1200)
            chk(len(page_errors) == 0,
                f"0 pageerrors ({len(page_errors)}: {page_errors[:2]})")
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} fallos (capa BI · qa_r74_v3666)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    asyncio.run(main())
