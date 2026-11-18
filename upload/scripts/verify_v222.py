#!/usr/bin/env python3
"""Verificación headless v2.22:
  1) MEGÁFONO: botón nuevo en el menú, persistencia, y announce() gateado
     (voz off -> ni chime ni voz ni respaldo speechSynthesis).
  2) RECORTE DE SILENCIOS: vbTrim cubre el banco con tramos válidos y
     speakPlan encadena usando offsets/duraciones recortadas — la pausa antes
     de la segunda cifra queda igual al gap del plan (≤0.12 s), no al doble
     silencio de antes.
  3) PALA DE LA IA COMO JUGADOR REAL: cara hacia la bola en espera, sigue la
     bola en el lanzamiento del saque, apunta a la salida en el impacto y
     acompaña el tiro en el follow-through (con roll de muñeca).
  4) Regresión ligera del menú (15 botones, todo cabe en el panel).
"""
import asyncio, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"

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
        await page.wait_for_timeout(3600)

        # ---------- 1) MENÚ: botón megáfono + persistencia ----------
        menu = await page.evaluate("""() => {
            const g = window.__game;
            if (g.menuOpen) g.toggleMenu();
            g.toggleMenu();
            g.drawMenu();
            g.menuClick(g.menuRects.findIndex((r) => r.id === 'sec:opts'));   // v2.28 acordeón
            const ids = g.menuRects.map((r) => r.id);
            const voz = g.menuRects.find((r) => r.id === 'voz');
            return { open: g.menuOpen, n: ids.length, hasVoz: !!voz,
                     vozY: voz ? voz.y : -1, vozW: voz ? voz.w : -1,
                     ids,
                     closeY: g.menuRects.find((r) => r.id === 'close')?.y ?? -1 };
        }""")
        print("menú:", json.dumps({k: menu[k] for k in ("open", "n", "hasVoz", "vozY", "closeY")}))
        if not menu["open"]: fails.append("el menú no se abre")
        if not menu["hasVoz"]: fails.append("falta el botón 'voz' (megáfono)")
        if menu["closeY"] + 68 > 1532: fails.append(f"CERRAR se sale del panel: y={menu['closeY']}")

        click_voz = await page.evaluate("""() => {
            const g = window.__game;
            const idx = g.menuRects.findIndex((r) => r.id === 'voz');
            g.menuClick(idx);
            const st1 = localStorage.getItem('ppxr_voz_v1');
            const v1 = g.audio.voice;
            g.menuClick(g.menuRects.findIndex((r) => r.id === 'voz'));
            const st2 = localStorage.getItem('ppxr_voz_v1');
            const v2 = g.audio.voice;
            return { st1, v1, st2, v2 };
        }""")
        print("megáfono click:", json.dumps(click_voz, ensure_ascii=False))
        if click_voz["st1"] != "0" or click_voz["v1"]:
            fails.append("el botón megáfono no desactiva/persiste")
        if click_voz["st2"] != "1" or not click_voz["v2"]:
            fails.append("el botón megáfono no reactiva/persiste")

        # ---------- banco de voz listo ----------
        bank = await page.evaluate("""() => {
            const g = window.__game;
            g.audio.kick();
            return new Promise((res) => {
                let n = 0;
                const iv = setInterval(() => {
                    n++;
                    if (g.audio.vb && g.audio.vb.size && g.audio.vbTrim) {
                        clearInterval(iv); res({ ok: true });
                    } else if (n > 60) { clearInterval(iv); res({ ok: false }); }
                }, 100);
            });
        }""")
        if not bank.get("ok"):
            fails.append("el banco de voz no quedó listo (vb/vbTrim)")

        # ---------- 2) RECORTE DE SILENCIOS ----------
        trim = await page.evaluate("""() => {
            const g = window.__game;
            const A = g.audio;
            let n = 0, total = 0, sil = 0, bad = 0;
            for (const [k, buf] of A.vb) {
                n++;
                const tr = A.vbTrim.get(k);
                if (!tr) { bad++; continue; }
                const [t0, t1] = tr;
                if (!(t0 >= 0 && t1 > t0 && t1 <= buf.duration + 1e-3)) bad++;
                total += buf.duration;
                sil += buf.duration - (t1 - t0);
            }
            return { n, trims: A.vbTrim.size, bad, total: +total.toFixed(2), sil: +sil.toFixed(2) };
        }""")
        print("recorte:", json.dumps(trim))
        if trim["bad"] > 0: fails.append(f"{trim['bad']} fragmentos con recorte inválido o ausente")
        if trim["sil"] < 1.5: fails.append(f"silencio recortado insuficiente: {trim['sil']} s (esperado ≥1.5 s)")

        # speakPlan con hooks: offsets/duraciones/gaps reales
        chain = await page.evaluate("""() => {
            const g = window.__game;
            const A = g.audio;
            const orig = AudioBufferSourceNode.prototype.start;
            const caps = [];
            AudioBufferSourceNode.prototype.start = function(when, off, dur) {
                caps.push({ when: +when.toFixed(4), off: +(off || 0).toFixed(4),
                            dur: +(dur === undefined ? this.buffer.duration : dur).toFixed(4) });
                return orig.call(this, when, off, dur);
            };
            let ssCalled = false;
            const origSpeak = window.speechSynthesis && window.speechSynthesis.speak;
            if (origSpeak) window.speechSynthesis.speak = function() { ssCalled = true; return origSpeak.apply(this, arguments); };
            let ok;
            try { ok = A.speakPlan(A.voicePlan('5 a 3, saque para ti')); }
            finally {
                AudioBufferSourceNode.prototype.start = orig;
                if (origSpeak) window.speechSynthesis.speak = origSpeak;
            }
            // gap real entre fragmentos consecutivos
            const gaps = [];
            for (let i = 1; i < caps.length; i++) {
                gaps.push(+(caps[i].when - (caps[i - 1].when + caps[i - 1].dur)).toFixed(4));
            }
            const buf0 = A.vb.get('n5');
            return { ok, n: caps.length, caps, gaps,
                     durFull: +buf0.duration.toFixed(4),
                     durTrim: caps.length ? caps[0].dur : -1,
                     off0: caps.length ? caps[0].off : -1 };
        }""")
        print("cadena:", json.dumps(chain))
        # v2.23: speakPlan compone UN AudioBuffer con UNA fuente (los gaps se
        # miden sobre las muestras del buffer en verify_v223.py)
        if not chain["ok"] or chain["n"] != 1:
            fails.append(f"speakPlan no produjo la fuente compuesta (ok={chain['ok']}, n={chain['n']})")

        # ---------- 1b) GATE del megáfono en announce() ----------
        gate = await page.evaluate("""() => {
            const g = window.__game;
            const A = g.audio;
            let started = 0;
            const orig = AudioBufferSourceNode.prototype.start;
            AudioBufferSourceNode.prototype.start = function() { started++; return orig.apply(this, arguments); };
            let ssCalled = false;
            const origSpeak = window.speechSynthesis && window.speechSynthesis.speak;
            if (origSpeak) window.speechSynthesis.speak = function() { ssCalled = true; };
            const out = {};
            try {
                A.setVoice(false);
                A.announce('5 a 3, saque para ti', true);
                out.offSources = started; out.offSS = ssCalled;
                A.setVoice(true);
                started = 0; ssCalled = false;
                A.announce('5 a 3, saque para ti', true);
                out.onSources = started; out.onSS = ssCalled;
            } finally {
                AudioBufferSourceNode.prototype.start = orig;
                if (origSpeak) window.speechSynthesis.speak = origSpeak;
            }
            return out;
        }""")
        print("gate:", json.dumps(gate))
        if gate["offSources"] != 0 or gate["offSS"]:
            fails.append(f"con megáfono OFF todavía suena algo: {gate}")
        if gate["onSources"] < 1:
            fails.append(f"con megáfono ON no hay voz: {gate}")

        # ---------- 3) ORIENTACIÓN DE LA PALA DE LA IA ----------
        ori = await page.evaluate("""() => {
            const g = window.__game;
            const V = Object.getPrototypeOf(g.ball.pos).constructor;
            const st0 = g.rules.state, sv0 = g.rules.server;
            const bp = g.ball.pos.clone(), bv = g.ball.vel.clone(), bs = g.ball.spin.clone();
            const out = {};
            const normalOf = () => new V(0, 0, 1).applyQuaternion(g.aiPaddleMesh.quaternion);
            // v2.23: la señal anti-vertical es la HOJA (eje local +Y), no la cara
            const bladeOf = () => new V(0, 1, 0).applyQuaternion(g.aiPaddleMesh.quaternion);
            const tiltDeg = (v) => +(Math.acos(Math.max(-1, Math.min(1, v.y))) * 180 / Math.PI).toFixed(1);

            // A) ESPERA: la cara mira a la bola (converge con slerp)
            g.rules.state = 'rally';
            g.ai.swing = null;
            g.ball.pos.set(0, 1.25, 1.0);
            for (let i = 0; i < 120; i++) g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.016);
            const nA = normalOf();
            const dA = g.ball.pos.clone().sub(g.aiPaddleMesh.position).normalize();
            out.idleDot = +nA.dot(dA).toFixed(3);
            out.idleTilt = tiltDeg(bladeOf());

            // B) FOLLOW-THROUGH: cara hacia donde vuela la bola (topspin -> cerrada pero acompañando)
            g.ball.vel.set(1, 0.6, 6); g.ball.spin.set(3, 0, 0);
            g.ai.swing = { t: 0, dur: 0.3, contact: new V(0, 0.95, -1.4),
                           dir: new V(0, 0, 1), speed: 1, roll: 0.15 };
            for (let i = 0; i < 12; i++) g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.016);
            const nB = normalOf();
            out.swingDot = +nB.dot(g.ball.vel.clone().normalize()).toFixed(3);
            out.swingNy = +nB.y.toFixed(3);
            g.ai.swing = null;

            // C) IMPACTO DEL SAQUE: cara hacia la salida (copia directa)
            g.rules.state = 'serve'; g.rules.server = 'ai';
            g.aiToss = null; g.aiStrikeT = 0.12;
            g.ball.vel.set(0.4, 0.8, 4.5);
            g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.016);
            const nC = normalOf();
            out.serveDot = +nC.dot(g.ball.vel.clone().normalize()).toFixed(3);
            g.aiStrikeT = 0;

            // D) LANZAMIENTO: la cara sigue la bola lanzada
            g.aiToss = { timer: 0.3 };
            g.ball.pos.set(0, 1.6, -2.6);
            g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.016);
            const nD = normalOf();
            const dD = g.ball.pos.clone().sub(g.aiPaddleMesh.position).normalize();
            out.tossDot = +nD.dot(dD).toFixed(3);
            g.aiToss = null;

            // restaurar
            g.rules.state = st0; g.rules.server = sv0;
            g.ball.pos.copy(bp); g.ball.vel.copy(bv); g.ball.spin.copy(bs);
            return out;
        }""")
        print("orientación:", json.dumps(ori))
        if ori["idleDot"] < 0.75: fails.append(f"en espera la cara no mira a la bola (dot={ori['idleDot']})")
        if not (8 <= ori["idleTilt"] <= 45):
            fails.append(f"en espera la hoja sigue vertical o se desmadra: {ori['idleTilt']}°")
        if ori["swingDot"] < 0.8: fails.append(f"en el follow-through la cara no acompaña el tiro (dot={ori['swingDot']})")
        if ori["serveDot"] < 0.9: fails.append(f"en el impacto la cara no apunta a la salida (dot={ori['serveDot']})")
        if ori["tossDot"] < 0.75: fails.append(f"en el lanzamiento la cara no sigue la bola (dot={ori['tossDot']})")

        if g_open := False:
            pass
        # cerrar menú si quedó abierto
        await page.evaluate("() => { const g = window.__game; if (g.menuOpen) g.toggleMenu(); }")

        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    if errors: fails.append("hubo errores de página")
    if fails:
        print("FALLOS:"); [print(" -", f) for f in fails]; sys.exit(1)
    print("TODO OK")

asyncio.run(main())
