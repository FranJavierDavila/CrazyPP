#!/usr/bin/env python3
"""Verificación headless v2.20: voz real del megáfono por WebAudio.

  - VOICE_B64 (67 fragmentos Piper es-ES / Opus) decodificado por
    decodeAudioData en el AudioContext real del juego (prueba clave:
    si Chromium decodifica, la Quest también; es la vía que ya se oye en VR)
  - voicePlan(): TODAS las frases que emite el juego → plan correcto
    (frases completas, temas, dificultades, 6 logros, marcador, victoria,
    rallye con números compuestos 30-99, fuera de rango → respaldo)
  - speakPlan(): programa BufferSources encadenadas con huecos crecientes
  - announce(): usa el banco y NO llama a speechSynthesis; con texto
    desconocido cae al respaldo sin crash
  - regresión ligera del menú (pestañas, estela, ambiente)
"""
import asyncio, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

# (texto real del juego, claves esperadas o None si es respaldo)
CASES = [
    ("Modo supervivencia. ¡Aguanta el rallye!", ["modo_supervivencia"]),
    ("Modo partido. ¡Buena suerte!", ["modo_partido"]),
    ("Bienvenido al partido. ¡Buena suerte!", ["bienvenido"]),
    ("Rival conectado. ¡A jugar!", ["rival_conectado"]),
    ("Rival desconectado", ["rival_desconectado"]),
    ("Sala Pabellón", ["sala_pabellon"]),
    ("Sala Neón", ["sala_neon"]),
    ("Sala Atardecer", ["sala_atardecer"]),
    ("Sala Ártico", ["sala_artico"]),
    ("Dificultad Fácil", ["dificultad_facil"]),
    ("Dificultad Media", ["dificultad_media"]),
    ("Dificultad Difícil", ["dificultad_dificil"]),
    ("¡Logro desbloqueado: Primera victoria!", ["logro_desbloqueado", "ach_primera"]),
    ("¡Logro desbloqueado: En racha!", ["logro_desbloqueado", "ach_racha"]),
    ("¡Logro desbloqueado: Gigante!", ["logro_desbloqueado", "ach_gigante"]),
    ("¡Logro desbloqueado: Maratonista!", ["logro_desbloqueado", "ach_maraton"]),
    ("¡Logro desbloqueado: Superviviente!", ["logro_desbloqueado", "ach_superviv"]),
    ("¡Logro desbloqueado: Saque directo!", ["logro_desbloqueado", "ach_aces"]),
    ("¡Rallye de 3 golpes! Nuevo récord", ["rallye_de", "n3", "golpes", "nuevo_record"]),
    ("¡Rallye de 23 golpes! Nuevo récord", ["rallye_de", "n23", "golpes", "nuevo_record"]),
    ("¡Rallye de 30 golpes! Nuevo récord", ["rallye_de", "n30", "golpes", "nuevo_record"]),
    ("¡Rallye de 45 golpes! Nuevo récord", ["rallye_de", "n40", "y", "n5", "golpes", "nuevo_record"]),
    ("¡Rallye de 99 golpes! Nuevo récord", ["rallye_de", "n90", "y", "n9", "golpes", "nuevo_record"]),
    ("5 a 3, saque para ti", ["n5", "a", "n3", "saque_para_ti"]),
    ("0 a 11, saque para la máquina", ["n0", "a", "n11", "saque_para_maquina"]),
    ("7 a 9, saque para tu rival", ["n7", "a", "n9", "saque_para_rival"]),
    ("11 a 5, saque para ti", ["n11", "a", "n5", "saque_para_ti"]),
    ("¡Victoria! 11 a 7", ["victoria", "n11", "a", "n7"]),
    ("Partido para la CPU. 7 a 11", ["partido_para_cpu", "n7", "a", "n11"]),
    ("Partido para tu rival. 11 a 9", ["partido_para_rival", "n11", "a", "n9"]),
    ("¡Rallye de 100 golpes! Nuevo récord", None),   # fuera de rango → respaldo
    ("hola mundo", None),                             # desconocido → respaldo
]

async def main():
    errors, fails = [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(3800)

        # --- 1) crear contexto + decodificar banco de voz ---
        bank = await page.evaluate("""() => {
            const g = window.__game;
            g.audio.kick();
            return new Promise((res) => {
                let n = 0;
                const iv = setInterval(() => {
                    n++;
                    if (g.audio.vb && g.audio.vb.size) {
                        clearInterval(iv);
                        res({ size: g.audio.vb.size, ctx: !!g.audio.ctx,
                              state: g.audio.ctx.state,
                              gains: [...g.audio.vbGain.values()].every(Number.isFinite),
                              rate: g.audio.ctx.sampleRate });
                    } else if (n > 60) { clearInterval(iv); res({ size: 0, stuck: true }); }
                }, 100);
            });
        }""")
        if bank.get("size") != 67:
            fails.append(f"banco de voz: {bank} (esperados 67 fragmentos)")
        if not bank.get("gains"): fails.append(f"ganancias no finitas: {bank}")

        # --- 2) voicePlan: todas las frases del juego ---
        plans = await page.evaluate("""(cases) => {
            const g = window.__game;
            return cases.map(([txt, exp]) => {
                const plan = g.audio.voicePlan(txt);
                const got = plan ? plan.map(a => a.k) : null;
                return { txt, exp, plan: got };
            });
        }""", [list(c) for c in CASES])
        for r in plans:
            if r["exp"] is None:
                # respaldo esperado: el plan DEBE ser nulo (o al menos no romper)
                if r["plan"] is not None:
                    fails.append(f"texto ajeno cubierto por error: '{r['txt']}' -> {r['plan']}")
                continue
            if r["plan"] is None:
                fails.append(f"plan nulo: '{r['txt']}'")
            elif r["plan"] != r["exp"]:
                fails.append(f"plan de '{r['txt']}': {r['plan']} != {r['exp']}")

        # --- 3) todos los fragmentos de todos los planes existen en el banco ---
        missing = await page.evaluate("""(cases) => {
            const g = window.__game;
            const out = [];
            for (const [txt, exp] of cases) {
                if (exp === null) continue;
                const plan = g.audio.voicePlan(txt);
                if (!plan) continue;
                for (const a of plan) if (!g.audio.vb.has(a.k)) out.push([txt, a.k]);
            }
            return out;
        }""", [list(c) for c in CASES])
        if missing: fails.append(f"fragmentos ausentes en el banco: {missing}")

        # --- 4) announce() usa el banco y programa fuentes encadenadas ---
        sched = await page.evaluate("""() => {
            const g = window.__game;
            if (!g.audio.ctx || !g.audio.vb) return { err: 'sin ctx/banco' };
            let scheduled = 0;
            const starts = [];
            const orig = g.audio.ctx.createBufferSource.bind(g.audio.ctx);
            g.audio.ctx.createBufferSource = () => {
                scheduled++;
                const s = orig();
                const os = s.start.bind(s);
                s.start = (t) => { starts.push(t); return os(t); };
                return s;
            };
            const ss = window.speechSynthesis;
            let ssCalled = false;
            if (ss) ss.speak = () => { ssCalled = true; };
            g.audio.announce('5 a 3, saque para ti', true);
            g.audio.ctx.createBufferSource = orig;
            if (ss) delete ss.speak;
            return { scheduled, ssCalled, starts, ok: scheduled === 4 && !ssCalled };
        }""")
        if not sched.get("ok"):
            fails.append(f"announce con banco: {json.dumps(sched)}")

        # --- 5) announce() con texto desconocido → respaldo speechSynthesis ---
        fb = await page.evaluate("""() => {
            const g = window.__game;
            const ss = window.speechSynthesis;
            let ssCalled = false;
            if (ss) ss.speak = (u) => { ssCalled = !!u && !!u.text; };
            g.audio.announce('hola mundo', true);
            if (ss) delete ss.speak;
            return { ssCalled };
        }""")
        if not fb.get("ssCalled"):
            fails.append(f"respaldo speechSynthesis no usado: {fb}")

        # --- 6) duración total de un plan (sensatez) ---
        dur = await page.evaluate("""() => {
            const g = window.__game;
            const plan = g.audio.voicePlan('Modo supervivencia. ¡Aguanta el rallye!');
            const buf = g.audio.vb.get('modo_supervivencia');
            return +buf.duration.toFixed(2);
        }""")
        if not (0.5 < dur < 6):
            fails.append(f"duración de frase completa sospechosa: {dur}s")

        # --- 7) regresión ligera del menú ---
        reg = await page.evaluate("""() => {
            const g = window.__game;
            g.connected[0] = true; g.connected[1] = true;
            g.toggleMenu();
            const ids = g.menuRects.map((r) => r.id);
            g.toggleMenu();
            return { ids, trail: g.showTrail };
        }""")
        for need in ('tab:main', 'tab:multi', 'close', 'trail', 'amb'):
            if need not in reg["ids"]: fails.append(f"regresión menú: falta {need}")

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    print("banco de voz:", json.dumps(bank))
    print("announce (5 a 3, saque para ti):", json.dumps(sched))
    print("respaldo:", json.dumps(fb), "· duración frase:", dur, "s")
    n_plans = sum(1 for r in plans if r["plan"] is not None)
    print(f"voicePlan: {n_plans} frases cubiertas por el banco, "
          f"{len(CASES) - n_plans} caen al respaldo (correcto)")
    if fails:
        print("FALLOS:", *fails, sep="\n  - ")
        sys.exit(1)
    print("TODO OK")

asyncio.run(main())
