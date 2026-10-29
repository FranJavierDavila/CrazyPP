#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r84_v3676 — CAPA BT · V3.6.75→3.6.86-SDK6, FASE 78 «DUELOS LOCOS».

Petición del dueño (r84): «Vamos con 2 y 3» —
  (2) DUELOS LOCOS: desbloquear el modo multijugador que lleva el candado
      «Próximamente» desde la r79 (cuando el dueño dijo «más adelante se
      definirán las reglas»).
  (3) Puerta frontal de EL PULSO CRAZY: completar el «paso 2» documentado
      en r76 — el cartel del HALL (la tarjeta del menú principal ya vive
      desde la r80 como _retoDiarioCard).

Lo implementado (r84, verificación de ESTA capa sobre el código REAL):
  · TARJETA DESBLOQUEADA: _modeCardDuelos (velo+candado+chip) ELIMINADO —
    la tarjeta vive en _modeCard con estética común (rayo, hover, chevron,
    autoajuste) y el click 'mjduel' hace _mjMode='duelos' (espejo de
    'mjnorm'): dos pasos r80 intactos (modo → sala).
  · TRANSPORTE: el modo viaja en el mstart (md) — lo decide el ANFITRIÓN
    (c09 _v2MaybeStart + c12 startOnlineMatch de revancha); el invitado lo
    recibe y obedece (c09 'mstart' → c12 onNetMatchStart, antes 'match'
    hard-coded). rules.startMatch normaliza 'duelos' y la serie mejor-de-3
    lo acepta (CLAIM/ACK, RESYNC y árbitro 100 % intactos).
  · PODERES (§DUELOS): cada 5 golpes propios (saque incluido) carga 1
    poder ALEATORIO; el gatillo de la mano libre lo libera con la bola en
    juego. TRES poderes netcode-safe:
      GIGANTE (12 s) — pala ×1,30 + radio ×1,38 local; el rival lo VE por
        el BIT 16 de pose.fl (transporte gratis, POSE=31 B intacto).
      FUEGO (10 s) — golpe de rally ×1,18 (tope 26 < cap 30 del validador
        §12: jamás rechazo anti-trampa); la velocidad viaja en el HIT.
      LOCA (10 s) — spin ×2 por el canal estándar del SÚPER EFECTO
        (ppEfectoMul en la pala); la curva viaja en el spin del HIT.
    El disparo del rival avisa por cable fiable ('pow') — SOLO UX.
  · CARTEL DEL HALL: dos placas de museo (drawHallSign) en los flancos de
    la pared de la puerta — «EL PULSO CRAZY · reto de hoy» y «TU RACHA» —
    repintadas con i18n viva en drawHall() (stub r58 revivido) y estado
    real de window.__PP_TRAIN (modoName/streak/bestStreak).

BLOQUES: (1) AGUJAS r84 en el servido (positivas + negativas del candado).
(2) CONTADORES exactos de claves y cables. (3) JUEGO REAL headless: arranque
del juego, menú multi con las dos tarjetas, click duelo → sala, MATCH_START
con md (compat 'match' intacta), árbitro 'duelos' con serie mejor-de-3,
máquina de poderes completa con net fiado (carga/gatillo/GIGANTE con radio y
escala/LOCA con multiplicador/expiración/aviso remoto), bit 16 en la pose y
placas del hall repintadas.
Uso: python3 qa_r84_v3676.py [URL]
"""
import asyncio
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
ok = fails = 0


def chk(cond, label):
    global ok, fails
    if cond:
        ok += 1
        print(f"  ✓ {label}")
    else:
        fails += 1
        print(f"  ✗ FALLO: {label}")


# ----------------------------------------------------------------------
JS_SRC = "() => fetch('?v=qa').then(r => r.text()).catch(() => document.documentElement.innerHTML)()"


async def agujas(page, src):
    print("— BLOQUE 1 · AGUJAS r84 en el servido —")
    POS = [
        ("tarjeta mjduel en _modeCard (estética común)",
         "this._modeCard(rects, 'mjduel', 40, 326, 944, 96, T('mj_duel_t')"),
        ("case 'mjduel' funcional", "case 'mjduel':"),
        ("click duelo → _mjMode='duelos'", "this._mjMode = 'duelos';"),
        ("anfitrión sella md en _v2MaybeStart",
         "const md = (this.game && this.game._mjMode === 'duelos') ? 'duelos' : 'match';"),
        ("revancha sella md en startOnlineMatch",
         "const md = (this._mjMode === 'duelos') ? 'duelos' : 'match';"),
        ("mstart receptor normaliza md", "(m.md === 'duelos') ? 'duelos' : 'match'"),
        ("onNetMatchStart obedece el md", "this.rules.startMatch(md);"),
        ("c06 normaliza 'duelos'", "(mode === 'duelos' ? 'duelos' : 'match')"),
        ("serie mejor-de-3 acepta duelos",
         "(this.mode === 'match' || this.mode === 'duelos') && this.bestOf > 1"),
        ("cable fiable del poder (def)", "sendDueloPower(id) { this.sendRel({ k: 'pow', p: id }); }"),
        ("cable fiable del poder (caso receptor)", "case 'pow':"),
        ("aviso remoto en el juego", "onRemoteDueloPower(id)"),
        ("carga por golpe (saque)", "this._dlChargeHit(); } catch (eDLs)"),
        ("carga por golpe (rally)", "this._dlChargeHit(); } catch (eDLh)"),
        ("gatillo duelos en el handler", "this._dlTrigger(i)) return;"),
        ("FUEGO: boost con guardia y tope 26", "this.ball.vel.multiplyScalar(1.18);"),
        ("LOCA: canal de spin ×2", ": (this._dlOn('loca') ? 2 : 1);"),
        ("GIGANTE: radio de golpeo", "DIMS.hitAssistRadius = this._BASE_HIT * 1.38;"),
        ("GIGANTE: bit 16 en la pose", "fl |= 16;"),
        ("GIGANTE: escala del avatar rival", "(smp.fl & 16) !== 0"),
        ("tick de poderes junto a updateMega", "this._dlUpdate(dt);"),
        ("i18n ES dl_gigante", "dl_gigante: 'PALA GIGANTE'"),
        ("i18n EN dl_gigante", "dl_gigante: 'GIANT PADDLE'"),
        ("i18n ES mode_duelos", "mode_duelos: '¡DUELOS LOCOS!"),
        ("cartel hall: placas registradas", "pulsoL: { cv: pulsoCvL, tex: pulsoTexL }"),
        ("cartel hall: repintado con i18n", "drawHallSign(ud.pulsoL.cv, T('pulso_hall_t'), subL);"),
        ("cartel hall: estado diario vivo", "TRH.state.daily"),
    ]
    for etiqueta, aguja in POS:
        chk(aguja in src, f"aguja · {etiqueta}")
    NEG = [
        ("el pintor candado _modeCardDuelos DESAPARECIÓ", "_modeCardDuelos(rects"),
        ("velo de bloqueado retirado de la tarjeta", "velo de bloqueado (patrón campeonatos)"),
        ("denial de 'mjduel' fuera (voz champ_locked_soon)", "case 'mjduel':\n        // r79 · DUELOS LOCOS bloqueado"),
    ]
    for etiqueta, aguja in NEG:
        chk(aguja not in src, f"negativa · {etiqueta}")


async def contadores(page, src):
    print("— BLOQUE 2 · CONTADORES exactos —")
    CNT = [
        ("dl_listo ES+EN", "dl_listo:", 2),
        ("dl_poder_listo ES+EN", "dl_poder_listo:", 2),
        ("dl_fuego ES+EN", "dl_fuego:", 2),
        ("dl_loca ES+EN", "dl_loca:", 2),
        ("dl_rival ES+EN", "dl_rival:", 2),
        ("pulso_hall_t ES+EN", "pulso_hall_t:", 2),
        ("pulso_racha_0 ES+EN", "pulso_racha_0:", 2),
        ("pulso_hall_m ES+EN", "pulso_hall_m:", 2),
        ("pulso_racha_t ES+EN", "pulso_racha_t:", 2),
        ("pulso_racha_s ES+EN", "pulso_racha_s:", 2),
        ("caso receptor 'pow'", "case 'pow':", 1),
        ("def sendDueloPower", "sendDueloPower(id)", 2),  # def + llamada en _dlTrigger
    ]
    for etiqueta, aguja, n in CNT:
        chk(src.count(aguja) == n, f"contador · {etiqueta} == {n} (hay {src.count(aguja)})")


JS_R84 = r"""
() => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  const R = { pasos: [], errores: [] };
  const paso = (s) => R.pasos.push(s);
  const tryP = (s, f) => { try { f(); paso(s); } catch (e) { R.errores.push(s + ': ' + e.message); } };

  // ---- prep: red FIADA (unidad) + modo duelos -------------------------
  tryP('net fiado', () => {
    G.net.online = true; G.net.v2 = 'ok'; G.net.role = 'host';
    G._powEnviados = [];
    G.net.sendDueloPower = (id) => G._powEnviados.push(id);
    G.net.setServeHeld = () => {};   // unidad: sin _ballAuth real
  });
  tryP('MATCH_START compat (md ausente → match)', () => {
    G.onNetMatchStart({ startAt: 0, fs: 'host', bo: 3 });
    if (G.mode !== 'match' || G.rules.mode !== 'match') throw new Error('modo ' + G.mode);
  });
  tryP('MATCH_START duelos (md del anfitrión)', () => {
    G.onNetMatchStart({ startAt: 0, fs: 'host', bo: 3, md: 'duelos' });
    if (G.mode !== 'duelos' || G.rules.mode !== 'duelos') throw new Error('modo ' + G.mode);
    if (G.rules.bestOf !== 3) throw new Error('bestOf');
    if (G._dlCargue !== 0 || G._dlLista || G._dlId !== '') throw new Error('estado dl sucio');
  });
  tryP('_dlEnabled exige red v2', () => {
    const v2 = G.net.v2; G.net.v2 = 'pending';
    if (G._dlEnabled()) throw new Error('debe ser false sin v2');
    G.net.v2 = v2;
    if (!G._dlEnabled()) throw new Error('debe ser true con v2');
  });
  // ---- carga: 5 golpes → poder listo ---------------------------------
  tryP('carga 5 golpes (saque+rally mezclados)', () => {
    G._dlReset();
    for (let i = 0; i < 5; i++) G._dlChargeHit();
    if (!G._dlLista) throw new Error('no está lista');
    if (!['gigante', 'fuego', 'loca'].includes(G._dlProximo)) throw new Error('poder ' + G._dlProximo);
  });
  tryP('el gatillo libera y avisa por cable', () => {
    const esperado = G._dlProximo;
    const consumido = G._dlTrigger(0);
    if (!consumido) throw new Error('no consumió');
    if (G._dlLista) throw new Error('sigue lista');
    if (G._dlId !== esperado) throw new Error('id ' + G._dlId);
    if (G._dlT <= 0) throw new Error('sin ventana');
    if (G._powEnviados.length !== 1 || G._powEnviados[0] !== esperado) throw new Error('cable ' + JSON.stringify(G._powEnviados));
    G._dlEsperado = esperado;
  });
  tryP('gatillo sin carga NO consume', () => {
    if (G._dlTrigger(0)) throw new Error('consumió sin carga');
  });
  // ---- GIGANTE: radio + escala ---------------------------------------
  tryP('GIGANTE: escala de la pala viva', () => {
    G._dlReset(); G._dlProximo = 'gigante'; G._dlLista = true;
    G._dlTrigger(0);
    if (!G._dlOn('gigante')) throw new Error('gigante no activo');
    // (el radio ×1,38 comparte EL MISMO bloque que la MEGA — aguja BT;
    //  aquí se verifica el efecto observable: la rampa de escala)
    for (let i = 0; i < 40; i++) G.updateMega(0.016);
    if (G._megaS < 1.25) throw new Error('escala ' + G._megaS);
  });
  // ---- LOCA: multiplicador de spin en la pala -------------------------
  tryP('LOCA: ppEfectoMul ×2 en las palas', () => {
    G._dlReset(); G._dlProximo = 'loca'; G._dlLista = true;
    G._dlTrigger(0);
    if (!G._dlOn('loca')) throw new Error('loca no activa');
    G.updateMega(0.016);
    const pads = G.controllerPaddles || [];
    if (!pads.length) throw new Error('sin controllerPaddles');
    for (const p of pads) if (p && p.ppEfectoMul !== 2) throw new Error('mul ' + p.ppEfectoMul);
  });
  // ---- expiración -----------------------------------------------------
  tryP('expiración: la ventana muere sola', () => {
    G._dlT = 0.05; G._dlUpdate(0.1);
    if (G._dlId !== '' || G._dlT !== 0) throw new Error('no expiró');
  });
  tryP('fuera de duelos todo se apaga', () => {
    G.rules.startMatch('match'); G.mode = 'match';
    if (G._dlEnabled()) throw new Error('enabled fuera de duelos');
    G._dlUpdate(0.016);
  });
  tryP('aviso remoto: mensaje y timer', () => {
    G.rules.startMatch('duelos');
    const antes = G.rules.message;
    G.onRemoteDueloPower('fuego');
    if (!(G._dlRemotoT > 0)) throw new Error('timer remoto');
    if (G.rules.message === antes) throw new Error('mensaje sin cambio');
    G.onRemoteDueloPower('no-existe');   // id raro: no rompe
  });
  tryP('bit 16 de pose.fl con GIGANTE', () => {
    if (!G.camera) throw new Error('sin cámara');
    const g1 = { position: { x: 0, y: 1, z: 0 }, quaternion: { x: 0, y: 0, z: 0, w: 1 } };
    G.grips = [g1, null]; G.paddleHand = 0;
    G._dlReset(); G._dlProximo = 'gigante'; G._dlLista = true; G._dlTrigger(0);
    let fl = G.net._samplePose(G).fl;
    if ((fl & 16) === 0) throw new Error('bit 16 ausente con gigante');
    G._dlReset();
    fl = G.net._samplePose(G).fl;
    if ((fl & 16) !== 0) throw new Error('bit 16 presente sin gigante');
  });
  tryP('árbol: serie mejor-de-3 con duelos', () => {
    G.rules.startMatch('duelos');
    G.rules.bestOf = 3;
    G.rules.forcePoint('player', 'net', undefined);
    G.rules.forcePoint('player', 'net', undefined);
    G.rules.forcePoint('player', 'net', undefined);
    // subir a 11-3 y dejar que update() resuelva el juego
    G.rules.scorePlayer = 11; G.rules.scoreAi = 3;
    G.rules.state = 'point'; G.rules.stateTimer = 0;
    G.rules.update(2.5);
    if (G.rules.gamesPlayer !== 1) throw new Error('gamesPlayer ' + G.rules.gamesPlayer);
  });
  tryP('hall: placas EL PULSO repintadas (píxel vivo)', () => {
    const ud = G.hallGroup && G.hallGroup.userData && G.hallGroup.userData.hall;
    if (!ud || !ud.pulsoL || !ud.pulsoR) throw new Error('sin placas en userData.hall');
    if (ud.pulsoL.cv.width !== 1024 || ud.pulsoL.cv.height !== 600) throw new Error('lienzo');
    // centinela: negro puro → drawHallSign pinta el panel de museo oscuro
    // (#241c15) — la COMPROBACIÓN es el píxel (needsUpdate lo resetea el
    // render loop entre frame y frame: carrera inevitable en vivo)
    const xL = ud.pulsoL.cv.getContext('2d');
    xL.fillStyle = '#000'; xL.fillRect(0, 0, 1024, 600);
    G.drawHall();
    const px = xL.getImageData(512, 300, 1, 1).data;
    if (px[0] === 0 && px[1] === 0 && px[2] === 0) throw new Error('sin repaint (negro)');
  });
  tryP('restaurar red (el rAF no toca caminos net)', () => {
    G.net.online = false; G.net.v2 = 'off';
    G.rules.startMatch('match'); G.mode = 'match';
  });
  return R;
}
"""

JS_MENU = r"""
() => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  const R = {};
  // r84 · menuClick recibe ÍNDICE de menuRects (firma real), no el id
  const click = (id) => {
    const i = (G.menuRects || []).findIndex(r => r.id === id);
    if (i >= 0) G.menuClick(i);
    return i;
  };
  try {
    G.net.online = false; G.net.v2 = 'off'; G.net.status = 'off';
    G._mjMode = null;
    G.menuPage = 'multi';
    G.drawMenu();
    const ids = (G.menuRects || []).map(r => r.id);
    R.hayDuelos = ids.indexOf('mjduel') >= 0;
    R.hayNormal = ids.indexOf('mjnorm') >= 0;
    click('mjduel');
    R.modoTrasClick = G._mjMode;
    G.drawMenu();
    const ids2 = (G.menuRects || []).map(r => r.id);
    R.salaRevelada = ids2.indexOf('net:host') >= 0 && ids2.indexOf('net:join') >= 0;
    click('mjsel');
    R.vueltaASeleccion = G._mjMode === null;
    click('mjnorm');
    R.normalSigue = G._mjMode === 'normal';
  } catch (e) { R.error = e.message; }
  return R;
}
"""


async def juego_real(page):
    print("— BLOQUE 3 · JUEGO REAL headless —")
    for _ in range(120):
        if await page.evaluate("() => !!window.__PP_GAME"):
            break
        await page.wait_for_timeout(500)
    chk(await page.evaluate("() => !!window.__PP_GAME"), "el juego arranca con __PP_GAME")

    res = await page.evaluate(JS_R84)
    if res.get("error"):
        chk(False, f"JS_R84: {res['error']}")
    else:
        for p in res.get("pasos", []):
            chk(True, f"real · {p}")
        for e in res.get("errores", []):
            chk(False, f"real · {e}")

    rm = await page.evaluate(JS_MENU)
    chk(not rm.get("error"), f"JS_MENU sin error ({rm.get('error')})" if rm.get("error") else "JS_MENU sin error")
    chk(rm.get("hayDuelos") is True, "menú multi: la tarjeta DUELOS LOCOS existe")
    chk(rm.get("hayNormal") is True, "menú multi: la tarjeta NORMAL sigue")
    chk(rm.get("modoTrasClick") == "duelos", "click duelo → _mjMode='duelos'")
    chk(rm.get("salaRevelada") is True, "elegido el modo: sala y código revelados (2 pasos r80)")
    chk(rm.get("vueltaASeleccion") is True, "◀ MODOS devuelve a la selección")
    chk(rm.get("normalSigue") is True, "NORMAL sigue eligiendo 'normal'")


async def main():
    global ok, fails
    src = None
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        errores = []
        page.on("pageerror", lambda e: errores.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        # el servido: el propio HTML (los agujas van contra el bundle vivo)
        src = await page.evaluate(
            "() => fetch(location.pathname + '?v=qa84').then(r => r.text())"
        )
        print(f"== qa_r84_v3676 · CAPA BT · {URL} ==")
        await agujas(page, src)
        await contadores(page, src)
        await juego_real(page)
        chk(len(errores) == 0, f"0 pageerrors (hay {len(errores)})" if not errores else f"pageerrors: {errores[:3]}")
        await browser.close()
    print(f"\n== RESULTADO: {ok} OK · {fails} FALLOS ==")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    asyncio.run(main())
