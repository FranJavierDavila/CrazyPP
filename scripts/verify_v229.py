#!/usr/bin/env python3
"""v2.29 · Verificación: colisión precisa en golpeos rápidos + audio + música.

1) ESTÁTICOS: cooldown 0,24, barrido con base interpolada, techo de velocidad
   de pala, megáfono independiente del ambiente, música VR (__PP_MUSIC_URL),
   prueba de sonido con auto-reparación, hooks XR por sesión.
2) FÍSICA (unit, vía __solverHook): swing rápido que ALCANZA y SOBREPASA la
   bola (follow-through): exactamente 1 evento 'paddle' en 1,2 s (adiós doble
   golpe); la bola sale hacia delante y se aleja. Swing CON ROTACIÓN de base
   entre frames: el cruce se registra. Sin eventos pala+mesa simultáneos.
3) AUDIO/MÚSICA: musicOn por defecto, setMusicWanted enciende/apaga el bucle
   (musicPlaying) con el contexto 'running', preferencia pp_music compartida,
   prueba de sonido no rompe y segunda pulsación repara (rebind).
4) MENÚ: Opciones incluye Música y Probar sonido; acordeón intacto.
5) Capturas portada + menú ES/EN y sin errores de página.
"""
import asyncio, base64, json, sys
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
fails = []

def check(cond, msg):
    if not cond:
        fails.append(msg)
        print("  FAIL:", msg)
    else:
        print("  ok:", msg)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4500)

        # ============ 1) ESTÁTICOS ============
        print("== estáticos ==")
        src = open(HTML, encoding="utf-8").read()
        for needle in ("paddleHitCooldown: 0.24", "paddleVelClamp", "velInst",
                       "prevNormal", "ipNormal", "VEL_WINDOW = 0.045",
                       "setMusicWanted", "startMusic", "stopMusic", "testSound",
                       "__PP_MUSIC_URL", "__audioHooksSession",
                       "btn_music", "btn_sndtest", "msg_sndrepair",
                       "if (!this.voice) return;", "data:audio/ogg;base64"):
            check(needle in src, f"HTML contiene {needle}")
        # la pista solo va incrustada UNA vez (deduplicada)
        check(src.count("data:audio/ogg;base64") == 1, "música incrustada UNA sola vez")
        # megáfono desacoplado del ambiente (ya no hay gate conjunto)
        check("!this.voice || !this.ambience) return" not in src,
              "megáfono ya no depende del ambiente")

        # ============ 2) FÍSICA: DOBLE GOLPE ============
        print("== física (swing rápido) ==")
        # el gancho se publica desde el bucle si __wantSolverHook está activo
        await page.evaluate("() => { window.__wantSolverHook = true; }")
        await page.wait_for_timeout(400)
        phys = await page.evaluate("""() => {
          const H = window.__solverHook;
          const g = window.__game;
          if (!H || !g) return { err: 'sin hook' };
          const V = g.ball.pos.constructor;
          const DIMS = H.DIMS;
          // --- caso A: smash que sobrepasa la bola (follow-through) ---
          const ball = { pos: new V(0.2, 1.05, DIMS.tableCenterZ + 0.55),
                         vel: new V(-0.3, -1.2, 0.4), spin: new V(0, 0, 0) };
          const pad = { pos: new V(), prev: new V(), vel: new V(),
                        omega: new V(0,0,0),
                        prevQuat: null, quatInit: true, velBuf: [], prevT: 1,
                        normal: new V(0, 0, -1), right: new V(1, 0, 0),
                        up: new V(0, 1, 0),
                        prevNormal: new V(0, 0, -1), prevRight: new V(1, 0, 0),
                        prevUp: new V(0, 1, 0),
                        cooldown: 0, who: 'player', index: 0, active: true,
                        extraReach: 0 };
          const q = g.controllerPaddles ? null : null;
          const events = [];
          const dt = 1 / 72;
          let t = 0, hits = 0, firstHitT = -1, padTableSameFrame = 0, exitVz = 0;
          const startZ = DIMS.tableCenterZ + 0.75;
          // la pala cruza la bola a ~5 m/s y sigue de largo 0,35 m, frena,
          // retrocede suave (el rebote real del brazo)
          while (t < 1.2) {
            pad.prev.copy(pad.pos);
            pad.prevNormal.copy(pad.normal);
            pad.prevRight.copy(pad.right);
            pad.prevUp.copy(pad.up);
            let z;
            if (t < 0.16) z = startZ - 5.2 * t;                    // aproximación
            else if (t < 0.30) z = startZ - 5.2 * 0.16 - 1.2 * (t - 0.16); // sigue de largo
            else z = pad.pos.z + 0.35 * dt;                        // frena casi del todo
            pad.pos.set(0.2, 1.0, z);
            pad.vel.copy(pad.pos).sub(pad.prev).divideScalar(dt);
            if (pad.vel.length() > (DIMS.paddleVelClamp || 12)) pad.vel.setLength(DIMS.paddleVelClamp);
            const before = events.length;
            H.stepPhysics(dt, ball, [pad], events);
            const newEv = events.slice(before);
            const hasPad = newEv.some((e) => e.type === 'paddle');
            const hasTable = newEv.some((e) => e.type === 'table');
            if (hasPad && hasTable) padTableSameFrame++;
            if (hasPad) { hits++; if (firstHitT < 0) { firstHitT = t; exitVz = ball.vel.z; } }
            t += dt;
          }
          // --- caso B: swing lateral CON ROTACIÓN de base (muñeca rápida) ---
          // la bola cruza el plano de la hoja (altura del CENTRO de la hoja)
          // mientras la normal gira 5°/frame: el barrido con base interpolada
          // debe registrar el cruce UNA sola vez.
          const ball2 = { pos: new V(0.05, 1.14, DIMS.tableCenterZ + 0.5),
                          vel: new V(0.1, 0.4, 0.05), spin: new V(0, 0, 0) };
          const pad2 = { pos: new V(), prev: new V(), vel: new V(),
                         omega: new V(0,0,0), prevQuat: null, quatInit: true,
                         velBuf: [], prevT: 1,
                         normal: new V(0, 0, -1), right: new V(1, 0, 0), up: new V(0, 1, 0),
                         prevNormal: new V(0, 0, -1), prevRight: new V(1, 0, 0), prevUp: new V(0, 1, 0),
                         cooldown: 0, who: 'player', index: 0, active: true, extraReach: 0 };
          const ev2 = [];
          let t2 = 0, hits2 = 0;
          while (t2 < 0.6) {
            pad2.prev.copy(pad2.pos);
            pad2.prevNormal.copy(pad2.normal);
            pad2.prevRight.copy(pad2.right);
            pad2.prevUp.copy(pad2.up);
            // barrido diagonal a ~4,5 m/s que atraviesa el plano de la bola
            pad2.pos.set(-0.6 + 4.5 * t2, 1.0, DIMS.tableCenterZ + 0.66 - 0.78 * t2);
            pad2.vel.copy(pad2.pos).sub(pad2.prev).divideScalar(t2 > 0 ? (1 / 72) : 1);
            const a = 5 * Math.PI / 180;   // giro de muñeca por frame
            const nx = pad2.normal.x * Math.cos(a) + pad2.normal.z * Math.sin(a);
            const nz = -pad2.normal.x * Math.sin(a) + pad2.normal.z * Math.cos(a);
            pad2.normal.set(nx, 0, nz).normalize();
            const before2 = ev2.length;
            H.stepPhysics(1 / 72, ball2, [pad2], ev2);
            for (let i = before2; i < ev2.length; i++) if (ev2[i].type === 'paddle') hits2++;
            t2 += 1 / 72;
          }
          return { hits, firstHitT, padTableSameFrame, exitVz: exitVz.toFixed(2),
                   hits2,
                   evTypes: ev2.map((e) => e.type) };
        }""")
        if "err" in phys:
            fails.append(phys["err"]); print(phys)
        else:
            print(json.dumps(phys))
            check(phys["hits"] == 1, f"caso A: EXACTAMENTE 1 golpe (hubo {phys['hits']})")
            check(phys["padTableSameFrame"] == 0, "caso A: nunca pala+mesa en el mismo frame")
            check(float(phys["exitVz"]) < -2.0, f"caso A: la bola sale hacia la mesa (vz={phys['exitVz']})")
            check(phys["hits2"] == 1, f"caso B: el swing con rotación registra UNA vez ({phys['hits2']})")

        # ============ 3) AUDIO / MÚSICA ============
        print("== audio / música ==")
        aud = await page.evaluate("""() => new Promise(async (res) => {
          const g = window.__game;
          g.audio.ensure();
          // gesto sintético para el contexto en headless
          document.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
          await new Promise((r) => setTimeout(r, 500));
          const out = { ctxState: g.audio.ctx ? g.audio.ctx.state : 'none' };
          out.musicOnDefault = g.audio.musicOn;
          g.audio.setMusicWanted(true);
          await new Promise((r) => setTimeout(r, 1800));   // decode de la pista
          out.playingAfterWanted = g.audio.musicPlaying;
          out.gainWanted = g.audio.musicWanted;
          g.audio.setMusicWanted(false);
          await new Promise((r) => setTimeout(r, 1200));
          out.playingAfterStop = g.audio.musicPlaying;
          // preferencia compartida
          g.audio.setMusic(false);
          out.prefOff = localStorage.getItem('pp_music');
          out.onAfterOff = g.audio.musicOn;
          g.audio.setMusic(true);
          out.prefOn = localStorage.getItem('pp_music');
          // prueba de sonido: 1ª pulsación suena; 2ª seguida repara
          const r1 = g.audio.testSound();
          const r2 = g.audio.testSound();   // < 5 s -> reparación (rebind)
          out.test1 = r1; out.test2 = r2;
          out.rebuildsAfterTest = g.audio.rebuilds;
          await new Promise((r) => setTimeout(r, 700));
          res(out);
        })""")
        print(json.dumps(aud))
        check(aud.get("ctxState") == "running", "contexto de audio 'running' en la portada")
        check(aud.get("musicOnDefault") is True, "música activa por defecto")
        check(aud.get("playingAfterWanted") is True, "menú -> la música suena (bucle WebAudio)")
        check(aud.get("playingAfterStop") is False, "menú cerrado -> la música para")
        check(aud.get("prefOff") == "0" and aud.get("onAfterOff") is False, "setMusic(false) persiste")
        check(aud.get("prefOn") == "1", "setMusic(true) restaura la preferencia")
        check(aud.get("test1") is False and aud.get("test2") is True, "2ª prueba seguida dispara la reparación")
        check(aud.get("rebuildsAfterTest", 0) >= 1, "la reparación re-vinculó el contexto")

        # ============ 4) MENÚ: Opciones con Música + Probar sonido ============
        print("== menú ==")
        menu = await page.evaluate("""() => {
            const g = window.__game;
            g.rules.startMatch('match');
            g.renderer.xr.isPresenting = false;
            g.menuPage = 'main'; g.menuSec = 'opts'; g.menuOpen = true;
            g.menuGroup.visible = true;
            g.camera.position.set(0, 1.4, 0.9);
            g.camera.lookAt(0, 1.2, -1.2);
            g.camera.updateMatrixWorld(true);
            g.anchorMenu(); g.drawMenu();
            const ids = g.menuRects.map((r) => r.id);
            // acordeón intacto: secciones presentes, match contraído
            const accOk = ids.includes('sec:match') && !ids.includes('start');
            // click en música: alterna y persiste
            const mi = ids.indexOf('music');
            const before = g.audio.musicOn;
            g.menuClick(mi);
            const after = g.audio.musicOn;
            const msg1 = g.rules.message;
            g.menuClick(mi);   // volver a dejarla activa
            const restored = g.audio.musicOn;
            // sndtest: pinta mensaje y no rompe
            const si = ids.indexOf('sndtest');
            g.menuClick(si);
            const msgTest = g.rules.message;
            return { ids, accOk, before, after, restored, msg1, msgTest,
                     hasSnd: ids.includes('sndtest') };
        }""")
        if menu.get("err"):
            fails.append(menu["err"]); print(menu)
        else:
            check(menu["accOk"], "acordeón intacto (opts abierta, match contraído)")
            check(menu["hasSnd"], "Opciones: botón Probar sonido presente")
            check(menu["before"] is True and menu["after"] is False and menu["restored"] is True,
                  "botón Música alterna la preferencia y la restaura")
            check("Música" in (menu["msg1"] or "") or "Music" in (menu["msg1"] or ""),
                  f"mensaje de música ({menu['msg1']})")
            check(bool(menu["msgTest"]), f"mensaje de la prueba de sonido ({menu['msgTest']})")

        # capturas del menú ES/EN (una sola evaluate por captura)
        for lang, path in (("es", "/home/z/my-project/download/captura-v229-menu-es.png"),
                           ("en", "/home/z/my-project/download/captura-v229-menu-en.png")):
            shot = await page.evaluate(f"""() => {{
                const g = window.__game;
                window.__setLang('{lang}', g);
                g.rules.startMatch('match');
                g.menuPage = 'main'; g.menuSec = 'opts'; g.menuOpen = true;
                g.menuGroup.visible = true;
                g.camera.position.set(0, 1.4, 0.9);
                g.camera.lookAt(0, 1.3, -1.2);
                g.camera.updateMatrixWorld(true);
                g.anchorMenu(); g.drawMenu();
                g.renderer.render(g.scene, g.camera);
                return g.renderer.domElement.toDataURL('image/png');
            }}""")
            open(path, "wb").write(base64.b64decode(shot.split(",", 1)[1]))
        await page.evaluate("() => { window.__setLang('es', window.__game); }")

        # ============ 5) PORTADA ============
        print("== portada ==")
        land = await page.evaluate("""() => {
          const ov = document.getElementById('overlay');
          const hero = document.querySelector('.hero-wrap img');
          const act = document.querySelector('.padbtn.active');
          return { hidden: ov.classList.contains('hidden'),
                   heroOk: !!hero && hero.src.startsWith('data:image/jpeg'),
                   actLang: act ? act.dataset.lang : null,
                   musicUrl: (window.__PP_MUSIC_URL || '').startsWith('data:audio/ogg'),
                   mute: !!document.getElementById('mutebtn') };
        }""")
        check(not land["hidden"], "portada visible")
        check(land["heroOk"] and land["musicUrl"] and land["mute"],
              "portada: hero + pista compartida + botón música")
        await page.screenshot(path="/home/z/my-project/download/captura-v229-portada-es.png")

        check(not errors, f"sin errores de página ({errors[:2]})")
        await browser.close()

    if fails:
        print("\nFALLOS:", len(fails))
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("\nTODO OK")

asyncio.run(main())
