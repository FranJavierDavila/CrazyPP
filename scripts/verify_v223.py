#!/usr/bin/env python3
"""Verificación headless v2.23:
  1) VOZ SIN CORTES: speakPlan compone UN solo AudioBuffer (1 fuente) con
     micro-fades; el silencio entre cifras es el del plan (≤0.11 s) y la
     pausa antes de "saque para ti" queda en su sitio (~0.3 s). Sin clipping.
  2) DUCKING: el ambiente (ambBus) baja durante la locución y se recupera.
  3) GATE del megáfono (voz off -> cero fuentes).
  4) PALA DE LA IA: golpes de DERECHA y REVÉS con la hoja girando (carga al
     lado del golpe -> cruce al terminar), cara CERRADA con liftado y ABIERTA
     con cortada, espera con hoja inclinada (no pared vertical), postura de
     saque diestra.
  5) MENÚ: hover también en botones activos (feedback de píxeles en TODOS),
     casillas ☑/☐, área táctil ampliada, modo/dificultad cambian sin cerrar.
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

        # ---------- banco de voz listo ----------
        bank = await page.evaluate("""() => {
            const g = window.__game;
            g.audio.kick();
            return new Promise((res) => {
                let n = 0;
                const iv = setInterval(() => {
                    n++;
                    if (g.audio.vb && g.audio.vb.size && g.audio.vbTrim) {
                        clearInterval(iv); res({ ok: true, n: g.audio.vb.size });
                    } else if (n > 60) { clearInterval(iv); res({ ok: false }); }
                }, 100);
            });
        }""")
        print("banco de voz:", json.dumps(bank))
        if not bank.get("ok"):
            fails.append("el banco de voz no quedó listo (vb/vbTrim)")

        # ---------- 1) VOZ COMPUESTA: 1 fuente, gaps EXACTOS, sin chasquidos ----------
        comp = await page.evaluate("""() => {
            const g = window.__game;
            const A = g.audio;
            let nStart = 0, captured = null;
            const orig = AudioBufferSourceNode.prototype.start;
            const origCBS = A.ctx.createBufferSource.bind(A.ctx);
            A.ctx.createBufferSource = () => {
                const s = origCBS();
                const os = s.start.bind(s);
                s.start = function() { nStart++; captured = s; return os.apply(this, arguments); };
                return s;
            };
            let ok;
            try { ok = A.speakPlan(A.voicePlan('5 a 3, saque para ti')); }
            finally {
                A.ctx.createBufferSource = origCBS;
                AudioBufferSourceNode.prototype.start = orig;
            }
            if (!ok || !captured) return { ok, nStart };
            const buf = captured.buffer;
            const ch = buf.getChannelData(0);
            const sr = buf.sampleRate;
            // segmentos con voz
            const thr = 0.02;
            const segs = [];
            let inSeg = false, st = 0;
            let peak = 0;
            for (let i = 0; i < ch.length; i++) {
                const v = Math.abs(ch[i]);
                if (v > peak) peak = v;
                const loud = v > thr;
                if (loud && !inSeg) { inSeg = true; st = i; }
                else if (!loud && inSeg) { inSeg = false; segs.push([st, i]); }
            }
            if (inSeg) segs.push([st, ch.length]);
            // fusionar micro-cortes < 30 ms (dentro de una misma palabra)
            const merged = [];
            for (const [a, b] of segs) {
                if (merged.length && a - merged[merged.length - 1][1] < sr * 0.03) {
                    merged[merged.length - 1][1] = b;
                } else merged.push([a, b]);
            }
            const gaps = [];
            for (let i = 1; i < merged.length; i++) {
                gaps.push(+((merged[i][0] - merged[i - 1][1]) / sr).toFixed(4));
            }
            return { ok, nStart: nStart, nWords: merged.length, gaps,
                     dur: +buf.duration.toFixed(3), peak: +peak.toFixed(3),
                     headSil: +(merged.length ? merged[0][0] / sr : 0).toFixed(3) };
        }""")
        print("voz compuesta:", json.dumps(comp))
        if not comp.get("ok") or comp.get("nStart") != 1:
            fails.append(f"la locución no es UNA fuente compuesta: nStart={comp.get('nStart')}")
        if comp.get("nWords", 0) < 4:
            fails.append(f"se esperaban ≥4 segmentos de palabra: {comp.get('nWords')}")
        gaps = comp.get("gaps") or []
        if len(gaps) >= 4:
            intra = gaps[:2]                    # cinco→a→tres
            # la última átomo-palabra puede tener pausas internas naturales:
            # la pausa de FRASE es el mayor gap a partir de la 3ª palabra
            phrase = max(gaps[2:])
            if max(intra) > 0.11:
                fails.append(f"cortes entre cifras aún audibles: {intra}")
            if not (0.16 <= phrase <= 0.5):
                fails.append(f"la pausa antes de 'saque para ti' no es natural: {phrase}")
        else:
            fails.append(f"no se pudieron medir los gaps entre palabras: {gaps}")
        if comp.get("peak", 0) > 1.0:
            fails.append(f"el buffer compuesto satura (peak={comp['peak']})")
        if not (0.25 <= comp.get("headSil", 0) <= 0.45):
            fails.append(f"la cabecera del chime no está en su sitio: {comp.get('headSil')}")

        # ---------- 2) DUCKING del pabellón ----------
        A = await page.evaluate("() => { const g = window.__game; g.audio.kick(); return !!g.audio.ambBus; }")
        if not A:
            fails.append("no existe el bus de ambiente (ambBus)")
        else:
            duck1 = await page.evaluate("""() => {
                const g = window.__game;
                g.audio.announce('victoria 5 a 3', true);
                return new Promise((res) => {
                    setTimeout(() => res({ low: g.audio.ambBus.gain.value }), 700);
                });
            }""")
            duck2 = await page.evaluate("""() => new Promise((res) => {
                const g = window.__game;
                setTimeout(() => res({ back: g.audio.ambBus.gain.value }), 5600);
            })""")
            print("ducking:", json.dumps(duck1), "→", json.dumps(duck2))
            if duck1["low"] > 0.5:
                fails.append(f"el ambiente no se agacha durante la locución: {duck1['low']}")
            if duck2["back"] < 0.85:
                fails.append(f"el ambiente no se recupera tras la locución: {duck2['back']}")

        # ---------- 3) GATE del megáfono ----------
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

        # ---------- 4) PALA DE LA IA: golpes con lado y giro ----------
        pose = await page.evaluate("""() => {
            const g = window.__game;
            const V = Object.getPrototypeOf(g.ball.pos).constructor;
            const st0 = g.rules.state, sv0 = g.rules.server;
            const bp = g.ball.pos.clone(), bv = g.ball.vel.clone(), bs = g.ball.spin.clone();
            const out = {};
            const bladeOf = (m) => new V(0, 1, 0).applyQuaternion(m.quaternion);
            const faceOf = (m) => new V(0, 0, 1).applyQuaternion(m.quaternion);
            const tiltDeg = (v) => +((Math.acos(Math.max(-1, Math.min(1, v.y))) * 180 / Math.PI)).toFixed(1);
            const converge = (frames) => { for (let i = 0; i < (frames || 260); i++) g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.001); };
            const setSwing = (t, contact, kind, fh, speed) => {
                g.ai.swing = { t, dur: 0.3, contact,
                               dir: new V(0, 0, 1), vdir, speed, roll: 0, kind, fh };
                converge();
            };

            // A) ESPERA: hoja INCLINADA (no vertical), cara hacia la bola
            g.rules.state = 'rally';
            g.ai.swing = null;
            g.ball.pos.set(-0.3, 1.1, -1.0);
            for (let i = 0; i < 140; i++) g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.016);
            const bA = bladeOf(g.aiPaddleMesh), fA = faceOf(g.aiPaddleMesh);
            const toBall = g.ball.pos.clone().sub(g.aiPaddleMesh.position).normalize();
            out.idleTilt = tiltDeg(bA);
            out.idleFace = +fA.dot(toBall).toFixed(3);

            // B) DERECHA (drive, fh=+1): punta cargada al lado del golpe y CRUZA
            g.ball.vel.set(0.5, 1.2, 6);
            const vdir = g.ball.vel.clone().normalize();
            setSwing(0, new V(-0.3, 0.95, -1.45), 'drive', 1, 1);
            out.fhStartBladeX = +bladeOf(g.aiPaddleMesh).x.toFixed(3);
            out.fhStartTilt = tiltDeg(bladeOf(g.aiPaddleMesh));
            out.fhStartFaceYdelta = +(faceOf(g.aiPaddleMesh).y - vdir.y).toFixed(3);
            setSwing(0.3, new V(-0.3, 0.95, -1.45), 'drive', 1, 1);
            out.fhEndBladeX = +bladeOf(g.aiPaddleMesh).x.toFixed(3);
            out.fhEndTilt = tiltDeg(bladeOf(g.aiPaddleMesh));
            out.fhEndFaceDot = +faceOf(g.aiPaddleMesh).dot(vdir).toFixed(3);
            g.ai.swing = null;

            // C) REVÉS (fh=-1): espejo del cruce
            setSwing(0, new V(0.3, 0.95, -1.45), 'drive', -1, 1);
            out.bhStartBladeX = +bladeOf(g.aiPaddleMesh).x.toFixed(3);
            setSwing(0.3, new V(0.3, 0.95, -1.45), 'drive', -1, 1);
            out.bhEndBladeX = +bladeOf(g.aiPaddleMesh).x.toFixed(3);
            g.ai.swing = null;

            // D) CORTADA (push): cara ABIERTA (face.y por encima de la salida)
            setSwing(0, new V(-0.2, 0.9, -1.45), 'push', 1, 0.8);
            out.pushFaceYdelta = +(faceOf(g.aiPaddleMesh).y - vdir.y).toFixed(3);
            g.ai.swing = null;

            // E) POSICIÓN del follow-through: el brazo cruza el cuerpo (x se invierte)
            setSwing(0, new V(-0.3, 0.95, -1.45), 'drive', 1, 1);
            out.fhStartPosX = +g.aiPaddleMesh.position.x.toFixed(3);
            setSwing(0.3, new V(-0.3, 0.95, -1.45), 'drive', 1, 1);
            out.fhEndPosX = +g.aiPaddleMesh.position.x.toFixed(3);
            g.ai.swing = null;

            // F) SAQUE DIESTRO: el cuerpo queda al lado contrario de la bola
            g.setupAIServe();
            out.aiStanceRel = +(g.aiServeStance.x - g.aiServeSpot.x).toFixed(3);
            g.setupDemoServe();
            out.demoStanceRel = +(g.demoServeStance.x - g.demoServeSpot.x).toFixed(3);

            // restaurar
            g.rules.state = st0; g.rules.server = sv0;
            g.ball.pos.copy(bp); g.ball.vel.copy(bv); g.ball.spin.copy(bs);
            return out;
        }""")
        print("pose pala:", json.dumps(pose))
        if not (10 <= pose["idleTilt"] <= 60):
            fails.append(f"en espera la hoja sigue vertical o se desmadra: {pose['idleTilt']}°")
        if pose["idleFace"] < 0.5:
            fails.append(f"en espera la cara no ofrece a la bola: {pose['idleFace']}")
        if pose["fhStartBladeX"] >= -0.05:
            fails.append(f"el drive no carga la punta al lado del golpe (x={pose['fhStartBladeX']})")
        if pose["fhEndBladeX"] <= 0.05:
            fails.append(f"el drive no cruza el cuerpo al terminar (x={pose['fhEndBladeX']})")
        if pose["fhEndTilt"] - pose["fhStartTilt"] < 8:
            fails.append(f"la hoja apenas rota durante el golpe: {pose['fhStartTilt']}°→{pose['fhEndTilt']}°")
        if pose["fhStartFaceYdelta"] >= 0.0:
            fails.append(f"el liftado no cierra la cara en el contacto: {pose['fhStartFaceYdelta']}")
        # la cortada ABRE respecto al liftado (misma salida, cara más alta)
        if pose["pushFaceYdelta"] - pose["fhStartFaceYdelta"] < 0.12:
            fails.append(f"la cortada no abre la cara frente al liftado: push={pose['pushFaceYdelta']} vs drive={pose['fhStartFaceYdelta']}")
        if pose["bhStartBladeX"] <= 0.05 or pose["bhEndBladeX"] >= -0.05:
            fails.append(f"el revés no invierte el lado del golpe: {pose['bhStartBladeX']}→{pose['bhEndBladeX']}")
        if not (pose["fhStartPosX"] < -0.2 and pose["fhEndPosX"] > pose["fhStartPosX"] + 0.1):
            fails.append(f"el brazo no cruza la posición del cuerpo: {pose['fhStartPosX']}→{pose['fhEndPosX']}")
        if not (0.1 <= pose["aiStanceRel"] <= 0.25) or not (-0.25 <= pose["demoStanceRel"] <= -0.1):
            fails.append(f"la postura de saque no es diestra: ai={pose['aiStanceRel']} demo={pose['demoStanceRel']}")

        # ---------- 5) MENÚ: hover en TODOS, casillas, área táctil, estado ----------
        menu = await page.evaluate("""() => {
            const g = window.__game;
            if (g.menuOpen) g.toggleMenu();
            g.mode = 'match'; g.difficulty = 'medium';
            g.toggleMenu();
            g.drawMenu();
            const out = { ids: g.menuRects.map((r) => r.id) };
            // área táctil ampliada
            const easy = g.menuRects.find((r) => r.id === 'diff:easy');
            out.easyW = easy.w; out.easyH = easy.h;
            // hover: TODOS los botones (activos incluidos) deben cambiar píxeles
            const c2 = g.menuCanvas.getContext('2d');
            const snap = () => c2.getImageData(0, 0, 512, 640).data;
            g.menuHover = [-1, -1]; g.drawMenu();
            const base = snap();
            const diffs = [];
            for (let i = 0; i < g.menuRects.length; i++) {
                g.menuHover = [i, -1]; g.drawMenu();
                const d = snap();
                let n = 0;
                for (let k = 0; k < d.length; k += 4) {
                    if (Math.abs(d[k] - base[k]) > 10 || Math.abs(d[k + 1] - base[k + 1]) > 10
                        || Math.abs(d[k + 2] - base[k + 2]) > 10) n++;
                }
                diffs.push(n);
                g.menuHover = [-1, -1];
            }
            out.diffs = diffs;
            // efectos de estado (el menú SIGUE abierto en modo/dificultad)
            const idx = (id) => g.menuRects.findIndex((r) => r.id === id);
            g.menuClick(idx('mode:survival'));
            out.modeAfter = g.mode; out.openAfterMode = g.menuOpen;
            g.menuClick(idx('mode:match'));
            g.menuClick(idx('diff:hard'));
            out.diffAfter = g.difficulty; out.openAfterDiff = g.menuOpen;
            g.menuClick(idx('diff:medium'));
            const amb0 = g.audio.ambience;
            g.menuClick(idx('amb'));
            out.ambAfter = g.audio.ambience; out.ambChanged = g.audio.ambience !== amb0;
            g.menuClick(idx('amb'));   // dejar como estaba
            const voz0 = g.audio.voice;
            g.menuClick(idx('voz'));
            out.vozAfter = g.audio.voice; out.vozPersist = localStorage.getItem('ppxr_voz_v1');
            g.menuClick(idx('voz'));
            g.menuClick(idx('trail'));
            out.trailAfter = g.showTrail;
            g.menuClick(idx('trail'));
            g.menuClick(idx('tab:multi'));
            out.pageAfterTab = g.menuPage;
            g.menuClick(idx('tab:main'));
            g.menuClick(idx('close'));
            out.openAfterClose = g.menuOpen;
            return out;
        }""")
        print("menú:", json.dumps(menu, ensure_ascii=False))
        need = ['mode:match', 'mode:survival', 'diff:easy', 'diff:medium', 'diff:hard',
                'theme:pabellon', 'theme:neon', 'theme:atardecer', 'theme:artico',
                'amb', 'trail', 'voz', 'tab:main', 'tab:multi', 'close']
        for nid in need:
            if nid not in menu["ids"]:
                fails.append(f"falta el botón {nid}")
        if menu["easyW"] != 146 or menu["easyH"] != 48:
            fails.append(f"el área táctil no está ampliada: {menu['easyW']}×{menu['easyH']} (esperado 146×48)")
        dead = [menu["ids"][i] for i, d in enumerate(menu["diffs"]) if d < 40]
        if dead:
            fails.append(f"botones sin feedback visual al apuntarlos: {dead}")
        if menu["modeAfter"] != 'survival' or not menu["openAfterMode"]:
            fails.append(f"el modo no cambia visiblemente: {menu['modeAfter']} open={menu['openAfterMode']}")
        if menu["diffAfter"] != 'hard' or not menu["openAfterDiff"]:
            fails.append(f"la dificultad no cambia visiblemente: {menu['diffAfter']} open={menu['openAfterDiff']}")
        if not menu["ambChanged"]:
            fails.append("el ambiente no bascula")
        if menu["vozPersist"] not in ('0', '1'):
            fails.append("el megáfono no persiste")
        if menu["pageAfterTab"] != 'multi':
            fails.append("las pestañas no navegan")
        if menu["openAfterClose"]:
            fails.append("Cerrar menú no cierra")

        # ---------- capturas de la pala para revisión ----------
        shots = await page.evaluate("""() => {
            const g = window.__game;
            const V = Object.getPrototypeOf(g.ball.pos).constructor;
            g.rules.state = 'rally';
            // espera con bola en el lado del revés de la CPU (cuerpo girado)
            g.ball.pos.set(0.3, 1.15, -0.9);
            g.ai.swing = null;
            for (let i = 0; i < 140; i++) g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.016);
            const p1 = g.aiPaddleMesh.position.clone();
            const cam = (p, dx, dy, dz) => {
                g.camera.position.set(p.x + dx, p.y + dy, p.z + dz);
                g.camera.lookAt(p.x, p.y, p.z);
                g.camera.updateMatrixWorld(true);
                g.renderer.render(g.scene, g.camera);
                return g.renderer.domElement.toDataURL('image/png');
            };
            const out = { espera: cam(p1, 1.4, 0.6, 1.7) };
            // follow-through de un drive cruzando el cuerpo
            const vdir = new V(0.4, 1.1, 6).normalize();
            g.ai.swing = { t: 0.12, dur: 0.3, contact: new V(-0.32, 0.95, -1.45),
                           dir: new V(0, 0, 1), vdir, speed: 1.2, roll: 0.1,
                           kind: 'drive', fh: 1 };
            for (let i = 0; i < 60; i++) g.updateAIPaddlePose(g.aiPaddleMesh, g.ai, 'ai', 0.016);
            const p2 = g.aiPaddleMesh.position.clone();
            g.ai.swing = null;
            out.swing = cam(p2, 1.5, 0.55, 1.6);
            return out;
        }""")
        import base64 as b64mod
        for name in ("espera", "swing"):
            png = b64mod.b64decode(shots[name].split(',', 1)[1])
            path = f"/home/z/my-project/download/captura-v223-pala-{name}.png"
            open(path, "wb").write(png)
            print("captura:", path, len(png), "bytes")

        if g_open := False:
            pass
        await page.evaluate("() => { const g = window.__game; if (g.menuOpen) g.toggleMenu(); }")
        await browser.close()

    print("errores página:", errors if errors else "ninguno")
    if errors: fails.append("hubo errores de página")
    if fails:
        print("FALLOS:"); [print(" -", f) for f in fails]; sys.exit(1)
    print("TODO OK")

asyncio.run(main())
