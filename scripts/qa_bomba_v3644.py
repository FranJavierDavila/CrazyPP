#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_bomba_v3644 — CAPA AM · ronda 52 (V3.6.74-SDK6, FASE 46).

La petición del dueño (literal): «Revisa el funcionamiento de los
superpoderes de pala… El Super iman no hace nada no se ve efecto ni se
nota nada sobre la pala… y en el Super efecto tampoco noto nada, además
de que la marca del bote va desfasada. El sonido de alerta de que se está
agotando no suena o no se percibe.» + el ladrillo BOMBA del ARKANOID 2
(etapa 4 del campeonato de La Locura): «aleatoriamente y al menos 1 vez
por partida aparezca un bloque de ladrillo negro sustituyendo a uno azul
con un dibujo de una bomba, permanece 4 segundos y salta a otro bloque
azul… una vez consumido ya no aparecen más durante la partida, se
reinicia con cada partida… si se destruye, con el disparo o con la
pelota detone estrepitosamente todos los bloques que están al menos
hasta un rango de 2 filas y columnas».

Pruebas: (1) FUENTE SERVIDA — agujas del NÚCLEO (campo continuo del
imán, estela del efecto, halo 0,21, marca del bote en la bola visual,
blips 988/1319 con háptica, imán 0,95/6,5/0,80 + rescate 7,5/1,05) y del
MÓDULO LOCURA (bomba completa: build, start-reset, update, salto 4 s,
garantía ≥1/partida, detonación radio 2×2, láser, colisión, i18n).
(2) PIL del bomba.webp (cartela blanca + silueta negra, 512×512).
(3) MECÁNICA REAL headless — el ArcadeController REAL del módulo con
bricks simulados: garantía de aparición, salto a 4 s con restauración
del azul, espera sin azules, detonación radio 2×2 exacta, no-vuelta.
(4) Núcleo headless — campo/estela construidas por el precaliente y
blips 3·2·1 espiados en el audio (frecuencias y gains v3.6.44).

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import io
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
MOD = "http://localhost:3000/championships/locura/index.js"
BOMBA = "http://localhost:3000/championships/locura/assets/bomba.webp"

ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


async def main():
    global ok, fails
    errors = []

    # ---------- 1 · FUENTE SERVIDA (núcleo) ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ('3.6.74-SDK6', 'versión servida: 3.6.74-SDK6 (ronda 52)'),
        # · v3.6.46 (r54) · NEGATIVAS: campo, flechas y estela RETIRADOS —
        #   el imán es GANCHO + PALA METÁLICA y el efecto es SPIN REAL
        ('RETIRADO (ronda 54, petición del dueño): _buildImanCampo',
         'imán (r54): campo y flechas RETIRADOS — diseño limpio de pala'),
        ('_imanPalaOsc(on) {', 'imán (r54): pala metálica −80 % (metódico)'),
        ('_imanOscuroC = hex20(', 'imán (r54): oscurecido real −80 % (hex sRGB exacto)'),
        # v3.6.49 (r57): GANCHO RETIRADO — GUÍA DE TIRO en el golpe
        ('imanAimProfundidad: 0.62,', 'r57: el imán es GUÍA DE TIRO (objetivo 62 % de la mesa rival)'),
        ('imanAimPisoVel: 9.5,', 'r57: piso de potencia del golpe guiado (golpes muy fuertes)'),
        ('RETIRADO (ronda 54): _buildEfectoTrail',
         'efecto (r54): estela RETIRADA — el efecto es el SPIN REAL'),
        ('efectoTipoUmbral: 0.55,', 'efecto (r54): clasificación del spin por barrido (c02)'),
        ('efectoBoteTopAvance: 1.55,', 'efecto (r54): topspin acelera el bote ×1,55 (c02)'),
        ('efectoBoteBackH: 0.16,', 'efecto (r54): backspin casi para el bote ×0,16 (c02)'),
        ('efectoBoteSideKick: 0.42,', 'efecto (r54): sidespin patada lateral 0,42 × |vz| (c02)'),
        # · imán r52 heredado (claves conservadas para rollback)
        ('imanRadio: 0.95,', 'imán: radio 0,95 m (c02)'),
        ('imanAcelMax: 6.5,', 'imán: aceleración 6,5 m/s² (c02)'),
        ('imanDvMax: 0.80,', 'imán: Δv 0,80 m/s (c02)'),
        ('imanRescateAcel: 7.5,', 'imán: rescate 7,5 m/s² (c02)'),
        ('imanRescateDv: 1.05,', 'imán: rescate Δv 1,05 m/s (c02)'),
        ('new THREE.RingGeometry(0.09, 0.115, 40)',
         'efecto: anillo de bote 0,09–0,115 m (antes 0,055–0,075)'),
        ('m.userData.boteT = 0.55;', 'efecto: el anillo de bote dura 0,55 s'),
        # · MARCA DEL BOTE EXACTA (fix del desfase)
        ('const pMar = (this.ball && this.ball.pos) ? this.ball.pos : e.pos;',
         'bote: la marca se clava a la bola VISUAL (no al subpaso físico)'),
        ('this.flashMarker(pMar);', 'bote: flashMarker usa la posición exacta'),
        # · CANTO VIVO en la pala (los cuatro poderes)
        ('color: colHex, transparent: true, opacity: 0.82,',
         'canto: opacity base 0,82 (antes 0,55 — se VE sobre la pala)'),
        ('const ro = (0.72 + 0.22 * Math.sin(tt * 5.1)) * blink;',
         'canto: pulso vivo 0,72 ± 0,22 durante toda la ventana'),
        # · AVISO DE FIN OÍDO Y SENTIDO
        ("const go = (fg, d, gn) => {", 'ticks: _poderTickBlip refactor v3644'),
        ('go(f, dur, 0.42);', 'ticks: gain 0,42 (antes 0,18 — se OYE)'),
        ('this.haptic(this.paddleHand, 0.55, 95);',
         'ticks: háptica fuerte en el último segundo (se SIENTE)'),
        ('this.haptic(this.paddleHand, 0.35, 55);',
         'ticks: háptica en los dos primeros ticks'),
    ]:
        chk(needle in game, label)

    # · AGUJAS NEGATIVAS (el defecto NO puede volver)
    chk('d <= DIMS.imanRadio && d > 1e-4 && b.vel && b.vel.z > 0.15' not in game,
        'imán NEGATIVO: la vieja condición vel.z > 0.15 de las flechas murió')
    chk('const f = n >= 3 ? 1568 : 1319;' not in game,
        'ticks NEGATIVO: los blips flojos de 0,07–0,09 s a gain 0,18 murieron')

    # ---------- 1b · FUENTE SERVIDA (módulo locura: la BOMBA) ----------
    try:
        mod_src = urllib.request.urlopen(MOD, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer el módulo locura servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ("window.__PP_BOMBA_URL = A('bomba.webp');",
         'bomba: URL del asset bomba.webp registrada'),
        ('this.bombMesh = new THREE.Mesh(this.brickGeo, this.blackMat);',
         'bomba: ladrillo NEGRO (misma blackMat del reloj)'),
        ('this.bombIcon = new THREE.Mesh(',
         'bomba: icono DELANTE del ladrillo (como el reloj del tiempo)'),
        ('this._bombBrick = null;    // { slot, t } — activo o null',
         'bomba: estado en el constructor'),
        ('this._bombBrick = null;\n    this._bombUsed = false;\n    this._bombWait = false;\n    this._bombNext = 2 + Math.random() * 10;\n    this._bombT = 0;\n    this._stageT = 0;',
         'bomba: SE REINICIA CON CADA PARTIDA (start — intervalo nuevo)'),
        ('if (this.bombMesh) this.bombMesh.visible = false;',
         'bomba: restos fuera del intento anterior (oculta en start)'),
        ('this._bombUpdate(dt);',
         'bomba: enganchada al update de la fase play'),
        ('if (this.variant !== 2) return;',
         'bomba: SOLO en la variante 2 (ARKANOID 2 — etapa 4 del camino)'),
        ('if (this._bombUsed) return;',
         'bomba: consumida = NUNCA más en la partida'),
        ('if (this._bombT >= 4) this._bombJump();',
         'bomba: 4 segundos en cada ladrillo → salta'),
        ('this._bombNext = 2 + Math.random() * 10;',
         'bomba: 1.ª aparición ALEATORIA dentro del 1.er intervalo (2-12 s — r53)'),
        ('bombaCada: 15,',
         'bomba: INTERVALOS DE 15 s (espec r53: «salga de manera aleatoria pero\n         con intervalos de 15 segundos si tiene ladrillos disponibles»)'),
        ('this._stageT += dt;',
         'bomba: reloj de la etapa que gobierna los intervalos (r53)'),
        ('this._bombNext = this._stageT + (this.C.bombaCada || 15);',
         'bomba: cada aparición programa la siguiente a +15 s (r53)'),
        ('if (this._eFase > 0) return;',
         'bomba: el final ELÉCTRICO la apaga (r53 — sin bomba en el gran final)'),
        ('if (azules.length && this._stageT >= this._bombNext) {',
         'bomba: sale SÓLO si hay azules disponibles y toca intervalo (r53)'),
        ('b.mesh.visible = false;              // el azul se OCULTA (sigue vivo)',
         'bomba: SUSTITUYE al azul (oculto, vivo; colisión salta el slot)'),
        ('if (this._bombBrick && b === this._bombBrick.slot) continue;',
         'bomba: la bola NO colisiona con el azul oculto bajo la bomba'),
        ('cur.mesh.visible = true;             // el azul original REAPARECE',
         'bomba: al saltar, el azul original vuelve'),
        ('this._bombWait = true;',
         'bomba: sin azules vivos → desaparece y espera'),
        ('_detonarBomba() {', 'bomba: detonación definida'),
        ('for (let dr = -2; dr <= 2; dr++) {\n        for (let dc = -2; dc <= 2; dc++) {',
         'bomba: DETONACIÓN en radio 2 filas × 2 columnas (la spec del dueño)'),
        ('if (b2 && b2.alive) this._breakBrick(b2);',
         'bomba: arrasa TODO lo vivo del radio (rojos Y azules)'),
        ('d.mesh.material = this.blackMat;',
         'bomba: escombros NEGROS de la propia bomba'),
        ("g.audio.playNoise(0.32, 180, 0.7, 0.4, pan);",
         'bomba: BOOM grave (trueno + caída al sub-grave)'),
        ("this._msg = T('ark_bomba_boom');",
         'bomba: cartel «¡BOOM! ¡DETONACIÓN!»'),
        ('if (ark._bombBrick && ark.bombMesh) meshes.push(ark.bombMesh);',
         'bomba: el LÁSER también la revienta (raycast)'),
        ('hitBomb = !hitBrick && !hitTime && hits[0].object === ark.bombMesh;',
         'bomba: impacto del rayo en la bomba identificado'),
        ('.filter((b) => b.alive && b.state !== \'elec\' &&',
         'bomba: el rayo del láser EXCLUYE el azul oculto (y el eléctrico, r53)'),
        ('this._detonarBomba();\n        }\n      }\n    }\n  }',
         'bomba: la bola la detona (colisión por subpaso)'),
        ('ark._detonarBomba();', 'bomba: el láser llama a la detonación'),
    ]:
        chk(needle in mod_src, label)

    # · i18n de la bomba vive en c00 → game.html compilado
    for needle, label in [
        ("ark_bomba_boom: '¡BOOM! ¡DETONACIÓN!',",
         'bomba: i18n ES «¡BOOM! ¡DETONACIÓN!» (c00→game.html)'),
        ("ark_bomba_boom: 'BOOM! DETONATION!',",
         'bomba: i18n EN «BOOM! DETONATION!» (c00→game.html)'),
    ]:
        chk(needle in game, label)

    # ---------- 2 · PIL del asset bomba.webp ----------
    try:
        data = urllib.request.urlopen(BOMBA, timeout=10).read()
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert('RGB')
        chk(im.size == (512, 512),
            f'bomba.webp: cartela 512×512 (real {im.size[0]}×{im.size[1]})')
        px = im.load()
        esquina = px[8, 8]
        centro = px[256, 316]
        chk(esquina[0] > 235 and esquina[1] > 235 and esquina[2] > 235,
            f'bomba.webp: cartela BLANCA como el reloj (esquina {esquina})')
        chk(centro[0] < 40 and centro[1] < 40 and centro[2] < 40,
            f'bomba.webp: silueta NEGRA de la bomba (centro {centro})')
        # la mecha/chispa (arriba a la derecha del cuello) también es negra
        mecha = px[330, 90]
        chk(mecha[0] < 90 and mecha[1] < 90 and mecha[2] < 90,
            f'bomba.webp: mecha y chispa presentes (px 330,90 = {mecha})')
    except Exception as e:
        chk(False, f'bomba.webp verificable: {e}')

    # ---------- 3 · MECÁNICA REAL headless (módulo real + bricks simulados) --
    # ---------- 4 · NÚCLEO headless (campo, estela, blips) -------------------
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)

        rt = await page.evaluate("""async () => {
          const out = {};
          const T3 = await import('three');   // importmap del juego
          const G = window.__PP_GAME;
          if (!G) { out.sinJuego = true; return out; }

          // ============ MÓDULO LOCURA REAL + BOMBA ============
          try {
            const mod = (await import('/championships/locura/index.js')).default;
            const ctx = window.__PP_CORE;
            if (!ctx) { out.sinCore = true; return out; }
            // init() devuelve PROMESA (fetch del manifest → wire → CTRL):
            // se espera y se da margen al montaje antes de leer mod.impl
            await mod.init({ game: G });
            await new Promise((r) => setTimeout(r, 500));
            const ctrl = mod.impl;
            if (!ctrl) { out.sinCtrl = true; return out; }
            const ark = ctrl.arkanoid;

            // --- andamio mínimo (la escena real no se monta en headless) ---
            ark.variant = 2;
            ark.C = { cols: 9, rows: 6, depth: 0.12, brickRest: 0.5 };
            ark._dying = [];
            ark._flash = () => {};
            ark.redMats = [{}, {}, {}];   // escombros: material por tono (mock)
            ark.blueMats = [{}, {}, {}];
            ark._debris = [];
            for (let i = 0; i < 14; i++) {
              ark._debris.push({ mesh: { visible: false, material: null,
                position: { x: 0, y: 0, z: 0, copy() {} } },
              vel: { set() {} }, life: 0 });
            }
            ark.bricks = [];
            for (let r = 0; r < 6; r++) {
              for (let c = 0; c < 9; c++) {
                const blue = ((r * 7 + c * 5 + 3) % 10) < 4;   // ~40 % azules
                ark.bricks.push({
                  alive: true, state: blue ? 'blue' : 'red',
                  matIdx: (r * 3 + c) % 3,
                  mesh: { visible: true, material: null,
                    position: { x: 0, y: 0, z: 0, copy() {} } },
                  home: new T3.Vector3(c * 0.2, r * 0.1, 0),
                  min: { x: c * 0.2 - 0.1, y: r * 0.1 - 0.05, z: -0.06,
                         max: 0 },
                  max: null,
                });
                const b = ark.bricks[ark.bricks.length - 1];
                b.min = { x: c * 0.2 - 0.1, y: r * 0.1 - 0.05, z: -0.06 };
                b.max = { x: c * 0.2 + 0.1, y: r * 0.1 + 0.05, z: 0.06 };
              }
            }
            ark.bombMesh = { visible: false, position: { copy() {} },
              scale: { setScalar() {} }, rotation: { set() {} } };
            ark.bombIcon = { visible: false, position: { copy() {} } };
            ark.bricksLeft = 54;
            ark._msg = ''; ark._msgT = 0; ark._hudDirty = false;
            ark._bombBrick = null; ark._bombUsed = false;
            ark._bombWait = false; ark._bombT = 0;
            ark._bombNext = 3; ark._stageT = 0;   // r53: 1.ª aparición a los 3 s
            ark._eFase = 0; ark._eSeed = null; ark._eMove = [];
            ark._eCadena = []; ark._eBoltT = 0; ark._eChispT = 0;

            // (a) INTERVALOS: aleatoria dentro del 1.er intervalo — con la
            //     1.ª aparición fijada a los 3 s sale al cruzarlos (r53);
            //     el spawn programa la SIGUIENTE a +15 s (3,0 + 15 = 18)
            for (let i = 0; i < 8; i++) ark._bombUpdate(0.5);   // 4 s ≥ 3 s
            out.aAparece = !!ark._bombBrick &&
              ark._bombBrick.slot.state === 'blue' &&
              ark._bombBrick.slot.mesh.visible === false &&
              ark.bombMesh.visible === true && ark.bombIcon.visible === true &&
              ark._bombNext === 18;   // siguiente aparición a +15 s exactos
            const slotA = ark._bombBrick.slot;

            // (b) SALTO a los 4 s: otro azul y el original REAPARECE
            for (let i = 0; i < 6; i++) ark._bombUpdate(0.7);    // 4,2 s
            out.bSalta = !!ark._bombBrick &&
              ark._bombBrick.slot !== slotA &&
              slotA.mesh.visible === true &&
              ark._bombBrick.slot.mesh.visible === false;

            // (c) DETONACIÓN radio 2×2: colocamos la bomba en el centro
            //     (fila 2, col 4 → índice 2*9+4=22) y detonamos
            ark._bombBrick = null;
            ark._bombUsed = false;
            ark.bombMesh.visible = false;
            ark.bombIcon.visible = false;
            for (const b of ark.bricks) { b.alive = true; b.mesh.visible = true; }
            ark._bombPlace(ark.bricks[22]);
            const antes = ark.bricks.filter((b) => b.alive).length;
            ark._detonarBomba();
            const rC = 2, cC = 4;
            let enRadioVivos = 0, fueraVivos = 0, muertos = 0;
            ark.bricks.forEach((b, i) => {
              const rr = Math.floor(i / 9), cc = i % 9;
              if (!b.alive) { muertos++; return; }
              if (Math.abs(rr - rC) <= 2 && Math.abs(cc - cC) <= 2) enRadioVivos++;
              else fueraVivos++;
            });
            out.cDetona = (enRadioVivos === 0 && muertos === 25 &&
              fueraVivos === 29 && ark._bombUsed === true &&
              ark.bombMesh.visible === false &&
              String(ark._msg).indexOf('BOOM') >= 0 && antes === 54);

            // (d) NUNCA VUELVE tras consumirse
            for (let i = 0; i < 20; i++) ark._bombUpdate(1);
            out.dNoVuelve = ark._bombBrick === null && ark._bombUsed === true;

            // (e) ESPERA sin azules y retorno en SU INTERVALO (r53)
            ark._bombUsed = false; ark._bombWait = true; ark._bombBrick = null;
            ark.bombMesh.visible = false; ark.bombIcon.visible = false;
            for (const b of ark.bricks) { b.alive = true; b.state = 'red';
              b.mesh.visible = true; }
            const bNuevo = ark.bricks[30];
            bNuevo.state = 'blue';                    // ya HAY azul disponible
            ark._bombUpdate(0.2);                     // pero NO toca intervalo
            out.eEspera = ark._bombBrick === null && ark._bombWait === true;
            ark._bombNext = ark._stageT;              // el intervalo CUMPLE
            ark._bombUpdate(0.2);
            out.eVuelve = !!ark._bombBrick &&
              ark._bombBrick.slot === bNuevo && bNuevo.mesh.visible === false;
          } catch (eB) { out.errBomba = (eB && eB.stack) ?
            String(eB.stack).split(String.fromCharCode(10)).slice(0, 4).join(' || ') : String(eB); }

          // ============ NÚCLEO: campo + estela + blips ============
          try {
            G.palaMejorada = true;
            try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) {}
            G.champs.activeId = 'locura';
            G.rules.startMatch('match');
            G.rules.state = 'point';
            // precaliente drena (13 piezas desde r54)
            for (let i = 0; i < 24; i++) {
              try { G.updateMega(1 / 60); } catch (eU) { out.errU = String(eU); }
            }
            // v3.6.46 · campo, flechas y estela RETIRADOS: el precaliente NO
            // debe construirlos y las propiedades NO deben existir
            out.campoRetirado = !G._imanCampo && !G._imanFlechas;
            out.estelaRetirada = !G._efectoTrail;
            out.palaMetalica = typeof G._imanPalaOsc === 'function';
            // blips: espía del audio
            const realOsc = G.audio.playOsc.bind(G.audio);
            const blips = [];
            G.audio.playOsc = (f0, f1, d, ty, gn, pan) => {
              blips.push({ f: f0, d, gn });
              return realOsc(f0, f1, d, ty, gn, pan);
            };
            G._poderTickBlip(1);
            G._poderTickBlip(2);
            G._poderTickBlip(3);
            await new Promise((r) => setTimeout(r, 220));   // doble blip +95 ms
            G.audio.playOsc = realOsc;
            out.blip12 = blips.length >= 4 &&
              blips[0].f === 988 && blips[0].gn >= 0.4 &&
              blips[0].d >= 0.14;
            const ult = blips.filter((b) => b.f === 1319);
            out.blip3 = ult.length >= 1 && ult[0].gn >= 0.4 && ult[0].d >= 0.18;
          } catch (eN) { out.errNucleo = String(eN); }
          return out;
        }""")

        if rt.get('sinJuego'):
            chk(False, 'headless: window.__PP_GAME presente')
        else:
            if rt.get('sinCore'):
                chk(False, 'headless: window.__PP_CORE presente (módulo locura)')
            elif rt.get('sinCtrl'):
                chk(False, f'headless: mod.impl presente — CTRL montado ({rt.get("errBomba", "sin err")})')
            else:
                chk(not rt.get('errBomba'),
                    f'mecánica bomba sin excepciones ({rt.get("errBomba", "limpia")})')
                chk(rt.get('aAparece') is True,
                    'mecánica (a): aparición ALEATORIA por INTERVALOS (r53) — '
                    'sustituye a un azul (oculto), icono y siguiente a +15 s')
                chk(rt.get('bSalta') is True,
                    'mecánica (b): a los 4 s SALTA a otro azul y el original reaparece')
                chk(rt.get('cDetona') is True,
                    'mecánica (c): DETONACIÓN radio 2×2 — 25 ladrillos del radio '
                    'destruidos, 29 de fuera intactos, cartel BOOM')
                chk(rt.get('dNoVuelve') is True,
                    'mecánica (d): consumida, la bomba NO reaparece en la partida')
                chk(rt.get('eEspera') is True and rt.get('eVuelve') is True,
                    'mecánica (e): sin intervalo ESPERA aunque haya azul; al '
                    'cumplir el intervalo VUELVE (cadencia 15 s — r53)')
                chk(not rt.get('errNucleo'),
                    f'núcleo headless sin excepciones ({rt.get("errNucleo", "limpio")})')
                chk(rt.get('campoRetirado') is True,
                    'núcleo (r54): campo y flechas del imán RETIRADOS — el '
                    'precaliente ya no los construye')
                chk(rt.get('estelaRetirada') is True,
                    'núcleo (r54): estela del efecto RETIRADA — el precaliente '
                    'ya no la construye')
                chk(rt.get('palaMetalica') is True,
                    'núcleo (r54): _imanPalaOsc existe (pala metálica −80 %)')
                chk(rt.get('blip12') is True,
                    'núcleo: blips «tres/dos» a 988 Hz · gain ≥ 0,4 · ≥ 0,14 s')
                chk(rt.get('blip3') is True,
                    'núcleo: blip final «uno» a 1319 Hz · gain ≥ 0,4 · ≥ 0,18 s')

    for e in errors[:4]:
        print('  · pageerror:', e[:140])
    chk(len(errors) == 0, f'sin pageerrors ({len(errors)})')

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(0 if fails == 0 else 1)


asyncio.run(main())
