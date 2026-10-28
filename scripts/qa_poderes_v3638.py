#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.38 · PODERES — INMEDIATEZ del gatillo + halo/bote EXACTOS +
flechas EN EL PLANO del icono + LOD 50 %/mirada (capa AG, en vivo).

Peticiones del dueño implementadas esta ronda (tras probar V3.6.37):
  1. «detecto un pequeño lag en el juego cuando desde el gatillo se lanza
     un superpoder para nuestra pala… debemos evitarlo a todas costa, debe
     sentirse que la aplicación es inmediata» — TRES ataques al lag:
     (a) el redibujo del icono ya NO corre en el frame del gatillo (se
     marca _megaTexDirty y lo ejecuta updateMega; al lanzar, el icono se
     oculta y el trabajo se ahorra entero);
     (b) la textura del icono es PERSISTENTE (canvas + CanvasTexture UNA
     vez, recalentada con needsUpdate — ni una creación/disposal más);
     (c) PRECALIENTE: desde la primera carga, el arsenal (cantos mega/
     efecto/imán, halo, anillo de bote, flechas) se construye POR
     ADELANTADO y REPARTIDO — una pieza por frame. El gatillo solo enciende.
  2. «el halo rojo y el bote rojo desfasados en relación a la bola» — el
     halo ES HIJO del ballMesh (viaja con su transform: cero desfase
     posible) y el anillo de bote está PRECALENTADO (el primer bote
     marcado ya no construye nada).
  3. «las flechitas deben estar en el mismo plano del icono… prácticamente
     tocándose tangencialmente… mirando hacia la cámara» — anclaje en
     MUNDO cada frame: centro del icono + lateral de CÁMARA × separación
     tangencial (gap 6 % del icono); sprites billboard = mismo plano,
     sin solaparse, mirando al ojo.
  4. «el tamaño de los iconos y flechas sean más pequeños mientras jugamos
     (50 %) y recuperen su tamaño si miramos el palo de nuestra pala» —
     LOD por MIRADA (_megaLodUpdate): rally → 0,5; mirando el mango
     (cos ≥ 0,978 ≈ 12°) o fuera del rally → 1,0, con transición
     exponencial suave.

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas de los 4 cambios + regresiones (halo que se
     copiaba por frame YA NO existe; el refresh con dispose YA NO existe;
     reglas del imán/efecto/matrix intactas).
  2) MECÁNICA REAL en headless — precaliente que drena solo (7 piezas sin
     tocar el gatillo), textura del icono persistente (misma referencia
     tras redibujos), gatillo que NO dibuja (dirty diferido), halo hijo de
     la bola, flechas coplanares con el icono (misma distancia a cámara) y
     tangenciales, LOD 50 % en rally → 100 % en saque y con la mirada
     forzada, MEGA alarga (regresión), golden de física intacto (capa B).

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

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

    # ---------- 1 · FUENTE SERVIDA ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        # 1 · INMEDIATEZ del gatillo
        ('this._megaTexDirty = true;', 'gasta/cicla/carga MARCAN el redibujo (diferido)'),
        ('if (this._megaTexDirty && icoOn && this._megaIcon) {',
         'updateMega ejecuta el redibujo diferido (nunca en el frame del gatillo)'),
        ('this._megaIconCv = document.createElement(\'canvas\');',
         'canvas del icono PERSISTENTE (se crea UNA vez)'),
        ('this._megaTex.needsUpdate = true;   // recalentada in-place',
         'textura del icono recalentada in-place (needsUpdate)'),
        ('_megaPrewarm() {', 'PRECALIENTE del arsenal definido'),
        ('this._megaPrewarmQ = [', 'cola del precaliente (piezas)'),
        ('() => { try { this._buildMegaFx(); } catch (e) { /* */ } },',
         'precaliente: canto MEGA por adelantado'),
        ('() => { try { this._buildEfectoFx(); } catch (e) { /* */ } },',
         'precaliente: canto EFECTO por adelantado'),
        ('() => { try { this._buildImanFx(); } catch (e) { /* */ } },',
         'precaliente: canto IMÁN por adelantado'),
        ('() => { try { this._buildEfectoHalo(); } catch (e) { /* */ } },',
         'precaliente: HALO por adelantado'),
        ('() => { try { this._efectoBotePrewarm(); } catch (e) { /* */ } },',
         'precaliente: ANILLO de bote por adelantado'),
        ('() => { try { this._buildMegaArrows(); } catch (e) { /* */ } },',
         'precaliente: FLECHAS por adelantado'),
        ('this._megaPrewarm();', 'la carga DISPARA el precaliente'),
        ('const pasoW = this._megaPrewarmQ.shift();',
         'el precaliente se REPARTE: una pieza por frame'),
        ('_efectoBotePrewarm() {', 'anillo de bote: construcción aislada'),
        # 2 · HALO/BOTE EXACTOS
        ('this.ballMesh.add(sp);', 'halo HIJO del ballMesh (viaja con la bola)'),
        ('el halo ES HIJO de la bola', 'halo: posición por transform, sin copias'),
        # 3 · FLECHAS EN EL PLANO del icono
        ('hijas de la ESCENA (mundo)', 'flechas: anclaje en MUNDO (no en la montura)'),
        ('const camB = this._camBasis();', 'flechas: base de CÁMARA por frame'),
        ('la línea ojo→icono: la flecha queda EN el plano del icono',
         'flechas: lateral EXACTO del plano billboard (perpendicular al ojo→icono)'),
        ('const off = ws * 0.5 + as * 0.5 + ws * 0.06;',
         'flechas: separación TANGENCIAL (casi tocándose)'),
        ('.addScaledVector(lat, parSA[1] * off);',
         'flechas: centro del icono + lateral del plano (mismo plano)'),
        # 4 · LOD 50 % / MIRADA
        ('const MEGA_LOD_JUEGO = 0.5;', 'LOD: 50 % en juego (dueño)'),
        ('const MEGA_LOD_MIRA = 0.978;', 'LOD: umbral de mirada al mango (≈12°)'),
        ('_megaLodUpdate(dt) {', 'LOD: transición exponencial definida'),
        ('_megaMirandoMango() {', 'LOD: ¿mira DIRECTAMENTE al mango?'),
        ('this._megaLodUpdate(dt);', 'LOD: corre con el icono cada frame'),
        ('const sc = MEGA_ICON_S * pop * this._megaLOD *',
         'LOD: escala del icono multiplica el LOD'),
        ('_camBasis() {', 'base de cámara XR/escritorio (sin asignaciones)'),
        # Reglas intactas (regresión de la ronda 45)
        ('const IMAN_DUR = 10;', 'imán: ventana 10 s (r56: regla del dueño)'),
        ('const EFECTO_DUR = 10;', 'efecto: ventana 10 s (r56: regla del dueño)'),
        ('const MEGA_GOLPES = 20;', 'mega: carga cada 20 toques (r56: «no antes de 20»)'),
        ('const MEGA_ICON_S = 0.048;', 'icono: tamaño base intacto'),
        ('const MEGA_ARROW_S = 0.020;', 'flechas: tamaño base intacto'),
        ('return !!(this.champs && this.champs.active);',
         'gate: superpoderes SOLO en campeonatos'),
        ('V3.6.79-SDK6', 'sello de versión servida'),
    ]:
        chk(needle in game, label)
    # REGRESIONES de los defects que se atacan
    chk('this._efectoHalo.position.copy(this.ball.pos);' not in game,
        'regresión: el halo ya NO se copia por frame (hijo de la bola)')
    chk('if (this._megaTex) this._megaTex.dispose();' not in game,
        'regresión: el refresh ya NO dispone/recrea la textura del icono')
    chk('MEGA_ICON_Y, MEGA_ICON_Z + 0.004' not in game,
        'regresión: las flechas ya NO cuelgan del eje local de la montura')
    chk(game.count('_megaPrewarm') >= 3, 'precaliente cableado (kick + cola + consumo)')
    chk(game.count('data:audio/mpeg;base64,') >= 6, '6 voces nativas embebidas intactas')
    chk(game.count('data:image/png;base64,') >= 3, '3 iconos de poder embebidos intactos')

    # ---------- 2 · MECÁNICA REAL (headless) ----------
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
          const G = window.__PP_GAME;
          const out = {};
          if (!G) { out.sinJuego = true; return out; }
          try { window.__pp2DPlay = true; } catch (e) { /* */ }
          try { localStorage.removeItem('pp_mega_norm_hint'); } catch (e) { /* */ }
          try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) { /* */ }
          G.palaMejorada = true;
          const libre = (G.paddleHand === 0) ? 1 : 0;
          const rndReal = Math.random;

          // · PRECALIENTE (re-anclado r50): la cola se arma AL EMPEZAR LA
          //    PARTIDA (anti-lag del dueño: 13 piezas — cantos, imagen del
          //    portal, icono y 4 voces) y al ganar la carga ya está DRENADA
          G.champs.activeId = 'locura';
          G.rules.startMatch('match');
          out.colaAlEmpezar = Array.isArray(G._megaPrewarmQ) &&
            G._megaPrewarmQ.length >= 13;   // r50: anti-lag total
          Math.random = () => 0.1;                 // siempre 'mega'
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errU0 = String(e); }
          G.rules.state = 'rally'; G.rules.rallyHits = 20;
          try { G.updateMega(1 / 60); } catch (e) { out.errU1 = String(e); }
          // drenar: una pieza por frame — SIN tocar el gatillo
          for (let i = 0; i < 20; i++) {
            try { G.updateMega(1 / 60); } catch (e) { out.errD = String(e); }
          }
          out.colaArmada = out.colaAlEmpezar === true;
          out.colaDrenada = Array.isArray(G._megaPrewarmQ) &&
            G._megaPrewarmQ.length === 0;
          out.arsenalCaliente = !!G._megaFx && !!G._efectoFx &&
            typeof G._imanPalaOsc === 'function' &&   // r54: pala metálica
            !!G._efectoHalo && !!G._efectoBoteFx && !!G._megaArrows;

          // · ICONO PERSISTENTE: la textura es SIEMPRE la misma referencia
          G._megaIdx = 0;
          const texAntes = G._megaTex;
          G._megaTexDirty = true;
          try { G.updateMega(1 / 60); } catch (e) { out.errT = String(e); }
          out.texturaMisma = G._megaTex === texAntes && texAntes !== null;
          out.dirtyProcesado = G._megaTexDirty === false;

          // · GATILLO MEGA: NO dibuja en el gatillo (dirty diferido;
          // v3.6.40 el icono NO desaparece al activar — pasa a modo ACTIVO
          // con el anillo de tiempo, petición del dueño en ronda 48)
          G.rules.state = 'rally';
          let tM = null;
          try { tM = G.megaTrigger(libre); } catch (e) { out.errM = String(e); }
          try { G.updateMega(1 / 60); } catch (e) { out.errM1 = String(e); }
          out.megaAbre = tM === true && G._megaT > 14.9;
          out.iconoModoActivo = G._megaIconOn === true &&
            G._megaIconModo === 'act' && G._megaActivaId === 'mega';
          // MEGA ya activa + gatillo = ALARGA (regresión v3.6.36/37)
          Math.random = () => 0.1;
          G.rules.state = 'point'; G.updateMega(1 / 60);
          G.rules.state = 'rally'; G.rules.rallyHits = 20; G.updateMega(1 / 60);
          const tAntes = G._megaT;
          let tM2 = null;
          try { tM2 = G.megaTrigger(libre); } catch (e) { out.errM2 = String(e); }
          out.megaAlarga = tM2 === true && G._megaT > tAntes + 14.9;

          // · HALO HIJO DE LA BOLA (cero desfase posible)
          try { G._megaPrewarmQ = G._megaPrewarmQ || []; } catch (e) { /* */ }
          G._efectoT = 4; G.ball.ppEfecto = true;
          G.updateMega(1 / 60);
          out.haloHijoBola = !!G._efectoHalo &&
            G._efectoHalo.parent === G.ballMesh;
          out.haloEnOrigenLocal =
            G._efectoHalo.position.lengthSq() < 1e-12;
          out.haloVisible = G._efectoHalo.visible === true;
          // el halo SE MUEVE con la bola sin que nadie lo copie
          G.ball.pos.set(0.4, 1.2, 0.8);
          G.ballMesh.position.copy(G.ball.pos);
          const mundo1 = G._efectoHalo.getWorldPosition(
            new (Object.getPrototypeOf(G.ball.pos).constructor)());
          out.haloViaja = mundo1.distanceTo(G.ball.pos) < 0.002;
          G.ball.ppEfecto = false; G.updateMega(1 / 60);
          out.haloFuera = G._efectoHalo.visible === false;

          // · FLECHAS: coplanares con el icono y tangenciales
          // (matriz con DOS entradas: efecto + imán — tras las pruebas
          // anteriores la matriz está vacía: se reconstruye aquí)
          G._efectoT = 0; G._megaT = 0; G._megaActivaId = null;
          G.updateMega(1 / 60);          // v3.6.40: todo apagado → inventario
          Math.random = () => 0.5;
          G.rules.state = 'point'; G.updateMega(1 / 60);
          G.rules.state = 'rally'; G.rules.rallyHits = 20; G.updateMega(1 / 60);
          Math.random = () => 0.9;
          G.rules.state = 'point'; G.updateMega(1 / 60);
          G.rules.state = 'rally'; G.rules.rallyHits = 20; G.updateMega(1 / 60);
          out.dosEnMatriz = G._megaMatriz.length === 2;
          out.flechasEnEscena = Array.isArray(G._megaArrows) &&
            !!G._megaArrows[G.paddleHand] &&
            G._megaArrows[G.paddleHand].every((s) => s && s.parent === G.scene);
          const icoV = G._megaIcon[G.paddleHand];
          const flechaV = G._megaArrows[G.paddleHand].find((s) => s.visible);
          if (flechaV) {
            const V3 = Object.getPrototypeOf(G.ball.pos).constructor;
            const pi = icoV.getWorldPosition(new V3());
            const pf = flechaV.getWorldPosition(new V3());
            const cam = G._camBasis();
            out.camBaseViva = !!cam && cam.right.lengthSq() > 0.5;
            // COPLANAR: (flecha−icono) ⊥ (ojo→icono) — en el plano billboard
            const nOI = pi.clone().sub(cam.pos).normalize();
            out.mismoPlano = Math.abs(
              pf.clone().sub(pi).dot(nOI)) < 0.004;
            // tangencial: separación ≈ off, sin solape
            const sep = pf.distanceTo(pi);
            const ws = icoV.scale.x * (G.paddleMounts[G.paddleHand].scale.x || 1);
            const offEsp = ws * 0.5 + ws * (0.020 / 0.048) * 0.5 + ws * 0.06;
            out.tangencial = Math.abs(sep - offEsp) < 0.002 &&
              sep > ws * 0.5;   // NO solapa el icono
            // billboard delante del ojo: icono y flecha en la MISMA dirección
            out.miraACamara = pi.clone().sub(cam.pos).normalize()
              .dot(pf.clone().sub(cam.pos).normalize()) > 0.99;
          } else { out.flechasEnEscena = false; }

          // · LOD: 50 % en rally, 100 % fuera y con la MIRADA
          G.rules.state = 'rally'; G._megaLOD = 1;
          for (let i = 0; i < 90; i++) G.updateMega(1 / 60);   // 1,5 s
          out.lodMedioEnRally = G._megaLOD < 0.55 &&
            G._megaIcon[G.paddleHand].scale.x < 0.031;
          G.rules.state = 'serve';
          for (let i = 0; i < 60; i++) G.updateMega(1 / 60);
          out.lodEnteroEnSaque = G._megaLOD > 0.95;
          G.rules.state = 'rally';
          const realMira = G._megaMirandoMango;
          G._megaMirandoMango = () => true;              // mirada forzada
          for (let i = 0; i < 60; i++) G.updateMega(1 / 60);
          out.lodEnteroMirando = G._megaLOD > 0.95;
          G._megaMirandoMango = realMira;

          // · sin cargas: gatillo honesto + física intacta es capa B
          Math.random = rndReal;
          out.finOk = true;
          return out;
        }""")
        for k in sorted(rt.keys()):
            v = rt[k]
            if k.startswith('err'):
                chk(False, f'error runtime {k}: {v}')
            elif k == 'sinJuego':
                chk(False, 'window.__PP_GAME no disponible')
            elif isinstance(v, bool):
                chk(v, 'runtime · ' + k)
            else:
                chk(True, f'runtime · {k} = {v}')

        await browser.close()

    if errors:
        for e in errors[:5]:
            print('  ✗ pageerror:', e[:200])
        fails += len(errors)

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(0 if fails == 0 else 1)


if __name__ == '__main__':
    asyncio.run(main())
