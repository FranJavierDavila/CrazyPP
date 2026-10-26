#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r73_v3665 — CAPA BH · V3.6.67-SDK6, FASE 67 «EL MENÚ MANDA».

Informe del dueño tras probar V3.6.64 en el Quest, punto por punto:
  1. «Cuando desplegamos un Menú estemos donde estemos debe ser la ventana
     que manda y debe verse siempre la primera, aunque por debajo tengamos
     cualquier otra».
  2. «En el menú principal en los campeonatos bloqueados está bien puesto
     el texto Próximamente pero los candados están mal colocados y aparecen
     desplazados».
  3. «En el menú principal me ha desaparecido el campeonato del Salvaje
     Oeste, tienes que recuperarlo y ponerlo accesible».
  4. «El telón de carga está muy mal diseñado: debe estar alejado de la
     vista como a 2 metros y no es poner un pegote de pantalla sino que
     todo el entorno que nos rodea esté negro con el texto delante».
  5. Mejora sorpresa: la tarjeta de intermedio de teatro (marco del
     campeonato, «PRESENTA», bola que va y viene sobre la pista).

El arreglo (r73) y SU verificación:
  · MENÚ MANDA: la familia del menú sube al cielo del render — panel 9998,
    cursores 9999, rayos 9997 — por ENCIMA de instrucciones (9994/9995),
    mapa del oeste (9990..9996) y telón (65/70). Verificado EN VIVO.
  · CANDADO: la v72 hacía scale(k) ANTES de dibujar en (x,y) absolutos —
    el candado se pintaba a 1,35× la posición (fantasma junto al pie del
    menú). Ahora translate(x,y) + scale(k) y cuerpo alrededor del origen.
    Verificado pintándolo en canvas real: píxeles junto al ancla y CERO
    píxeles en la posición desplazada.
  · OESTE SIEMPRE: el índice y los manifest se pedían UNA vez — una
    petición perdida lo borraba del menú para siempre. Ahora fetch con
    cache:'no-cache' + reintentos exponenciales + manifest EN PARALELO +
    DOS OLAS de recuperación (+8 s / +25 s) + estado «CARGANDO…» + botón
    REINTENTAR (recargar()).
  · TELÓN DE TEATRO: esfera negra invertida de 12 m centrada en la cabeza
    (renderOrder 65, traga paredes/mesa/passthrough) + tarjeta de
    intermedio a 2,00 m que sigue la cabeza (giro y altura) con marco del
    color del campeonato, «CRAZY PING PONG PRESENTA», título autoajustado,
    «Montando el escenario...» y una bola que va y viene sobre la pista.
    Fundido que desmonta esfera+cartel. Tick en TIEMPO REAL (r72 intacto).

BLOQUES: (1) AGUJAS r73 en el game.html servido. (2) CONTADORES (geometría
vieja ausente, nueva presente). (3) JUEGO REAL headless: menú manda en
vivo, candado medido en píxeles, índice resiliente con datos, telón de
teatro nace→2,00 m→se desmonta solo, 0 pageerrors.
Uso: python3 scripts/qa_r73_v3665.py [URL]"""
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
    # --- r73 · EL MENÚ MANDA ---
    ("menú: panel al cielo (9998)", "this.menuMesh.renderOrder = 9998;"),
    ("menú: cursores por encima (9999)", "dot.renderOrder = 9999;"),
    ("menú: rayos bajo el panel (9997)", "beam.renderOrder = 9997;"),
    # --- r73 · CANDADO BIEN COLOCADO ---
    ("candado: translate ANTES de scale", "c.save(); c.translate(x, y); c.scale(k, k);"),
    ("candado: cuerpo alrededor del origen", "if (c.roundRect) c.roundRect(-13, -8, 26, 20, 5); else c.rect(-13, -8, 26, 20);"),
    # --- r73 · ÍNDICE RESILIENTE (OESTE SIEMPRE) ---
    ("índice: fetch con reintentos", "async _fetchJSON(url, intentos) {"),
    ("índice: sin caché del navegador", "cache: 'no-cache'"),
    ("índice: manifest en paralelo", "Promise.all(list.map(async (raw) => {"),
    ("índice: olas de recuperación", "OLAS DE RECUPERACIÓN"),
    ("índice: recarga manual", "recargar() {"),
    ("índice: previsualización en método propio", "_previsualiza() {"),
    ("menú: estado CARGANDO", "T('champ_cargando')"),
    ("menú: botón REINTENTAR", "btn('champretry', 312, y, 400, 58, T('champ_reintentar')"),
    ("menú: case champretry", "case 'champretry':"),
    # --- r73 · TELÓN DE TEATRO ---
    ("telón: esfera negra de 12 m", "new THREE.SphereGeometry(12, 28, 18), matEs"),
    ("telón: esfera invertida (BackSide)", "color: 0x000000, side: THREE.BackSide,"),
    ("telón: esfera pinta ANTES del cartel (65)", "esfera.renderOrder = 65;"),
    ("telón: cartel sobre la esfera (70)", "mesh.renderOrder = 70;"),
    ("telón: cartel a 2 m siguiendo la cabeza", "S.group.position.set(S._v1.x + S._v2.x * 2.0, dy, S._v1.z + S._v2.z * 2.0);"),
    ("telón: esfera centrada en el visor", "S.esfera.position.copy(S._v1);"),
    ("telón: colores por campeonato", "_telonCols(id) {"),
    ("telón: PRESENTA en la tarjeta", "T('champ_telon_presenta').split('').join(' ')"),
    ("telón: bola en la pista", "c.arc(bx, by, 9, 0, Math.PI * 2); c.fill();"),
    ("telón: fundido apaga esfera y cartel", "S.matEs.opacity = k;"),
    # --- i18n r73 ---
    ("i18n ES: cargando", "champ_cargando: 'Cargando campeonatos…',"),
    ("i18n ES: reintentar", "champ_reintentar: '⟳  REINTENTAR',"),
    ("i18n ES: presenta", "champ_telon_presenta: 'CRAZY PING PONG PRESENTA',"),
    ("i18n EN: cargando", "champ_cargando: 'Loading championships…',"),
    ("i18n EN: reintentar", "champ_reintentar: '⟳  RETRY',"),
    ("i18n EN: presenta", "champ_telon_presenta: 'CRAZY PING PONG PRESENTS',"),
]

CONTADORES = [
    ("geometría vieja AUSENTE (plano pegote 0,72 m)", ["group.position.set(0, 1.66, -0.72);"], 0),
    ("geometría vieja AUSENTE (scale antes de translate)", ["c.save(); c.scale(k, k);"], 0),
    ("renderOrder viejo AUSENTE en la familia del menú",
     ["this.menuMesh.renderOrder = 990;", "dot.renderOrder = 991;", "beam.renderOrder = 940;"], 0),
    ("esfera del telón presente ×1", ["new THREE.SphereGeometry(12, 28, 18)"], 1),
    ("olís de recuperación presentes", ["for (let ola = 0; ola < 2 && fallados.length; ola++)"], 1),
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

    print("— BLOQUE 1 · AGUJAS r73 en el game.html servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES de geometría —")
    for label, pats, esperado in CONTADORES:
        n = sum(len(re.findall(re.escape(p), src)) for p in pats)
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")

    print("— BLOQUE 3 · JUEGO REAL headless (menú manda, candado, índice, telón) —")
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

            # --- MENÚ MANDA: órdenes reales del render ---
            ordenes = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return { panel: g.menuMesh.renderOrder,
                    dots: g.menuDots.map(d => d.renderOrder),
                    beams: g.menuLines.map(b => b.renderOrder) };
            }""")
            chk(ordenes.get("panel") == 9998, f"MENÚ MANDA: panel renderOrder {ordenes.get('panel')} (9998)")
            chk(all(d == 9999 for d in ordenes.get("dots", [])), "MENÚ MANDA: cursores 9999")
            chk(all(b == 9997 for b in ordenes.get("beams", [])), "MENÚ MANDA: rayos 9997")

            # --- CANDADO: píxeles junto al ancla y CERO desplazados ---
            cand = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                const cv = document.createElement('canvas');
                cv.width = 360; cv.height = 160;
                const c = cv.getContext('2d');
                c.fillStyle = '#10131a'; c.fillRect(0, 0, 360, 160);
                const AX = 200, AY = 80;
                g._ppIconsProbe().candado(c, AX, AY, 1.35);
                const d = c.getImageData(0, 0, 360, 160).data;
                const fondo = (r, g2, b) => Math.abs(r-16)<10 && Math.abs(g2-19)<10 && Math.abs(b-26)<10;
                let enAncla = 0, desplazados = 0;
                for (let y = 0; y < 160; y += 2) {
                    for (let x = 0; x < 360; x += 2) {
                        const i = (y * 360 + x) * 4;
                        if (fondo(d[i], d[i+1], d[i+2])) continue;
                        const cerca = Math.abs(x - AX) <= 24 && Math.abs(y - AY) <= 24;
                        const lejos = (x > AX + 30) || (y > AY + 30);
                        if (cerca) enAncla++;
                        if (lejos) desplazados++;
                    }
                }
                return { enAncla, desplazados };
            }""")
            chk(cand.get("enAncla", 0) > 30,
                f"CANDADO: pinta junto al ancla ({cand.get('enAncla')} px)")
            chk(cand.get("desplazados", 99) == 0,
                f"CANDADO: cero píxeles desplazados ({cand.get('desplazados')})")

            # --- ÍNDICE RESILIENTE: datos reales ---
            for _ in range(40):
                n = await page.evaluate("() => (window.__PP_GAME.champs.entries||[]).length")
                if n >= 5:
                    break
                await page.wait_for_timeout(500)
            # r73: cargando pasa a false tras el preload eager (locura) — esperar
            for _ in range(30):
                car = await page.evaluate("() => window.__PP_GAME.champs.cargando === false")
                if car:
                    break
                await page.wait_for_timeout(500)
            datos = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                const L = g.champs.list();
                return { n: L.length, ids: L.map(x => x.id),
                    oeste: L.find(x => x.id === 'oeste'),
                    cargando: g.champs.cargando,
                    recargar: typeof g.champs.recargar === 'function',
                    fetchJSON: typeof g.champs._fetchJSON === 'function' };
            }""")
            chk(datos.get("n") == 5, f"ÍNDICE: 5 campeonatos en el menú ({datos.get('n')})")
            chk(bool(datos.get("oeste")) and datos["oeste"].get("locked") is False,
                "ÍNDICE: EL SALVAJE OESTE está y es ACCESIBLE")
            chk(datos.get("cargando") is False, "ÍNDICE: la carga termina (cargando=false)")
            chk(datos.get("recargar") and datos.get("fetchJSON"),
                "ÍNDICE: recargar() + _fetchJSON() vivos")

            # --- TELÓN DE TEATRO EN VIVO ---
            telon = await page.evaluate("""async () => {
                const g = window.__PP_GAME;
                g.champs.leaveAll();
                localStorage.removeItem('pp_intro_locura');
                g.champs.introPendiente = () => false;
                await g.champs.launch('locura');
                const S = g.champCurtain;
                if (!S) return { vivo: false };
                const gp = S.group.position, ep = S.esfera.position;
                await new Promise(r => setTimeout(r, 1200));
                const gp2 = g.champCurtain ? g.champCurtain.group.position : null;
                return { vivo: true, ttl: S.ttl,
                    esferaRig: S.esfera.parent === g.rig,
                    radio: S.esfera.geometry.parameters.radius,
                    backside: S.esfera.material.side === 1,
                    ordenEsfera: S.esfera.renderOrder, ordenPanel: S.mesh.renderOrder,
                    dist: Math.hypot(gp.x - ep.x, gp.z - ep.z),
                    enRig: S.group.parent === g.rig,
                    sigueVivo: !!g.champCurtain,
                    seMueve: gp2 ? (Math.abs(gp2.x - gp.x) + Math.abs(gp2.z - gp.z)) > 0.001 : false };
            }""")
            chk(telon.get("vivo"), "TELÓN: nace con el launch")
            chk(telon.get("esferaRig") and telon.get("radio") == 12 and telon.get("backside"),
                "TELÓN: esfera 12 m BackSide colgada del rig")
            chk(telon.get("ordenEsfera") == 65 and telon.get("ordenPanel") == 70,
                "TELÓN: esfera 65 < cartel 70")
            chk(abs((telon.get("dist") or 0) - 2.0) < 0.02,
                f"TELÓN: cartel a 2,00 m de la cabeza ({telon.get('dist')})")
            # r73 · SEGUIR A LA CABEZA: gira el rig (simula un recentrado del
            # Quest) — la cabeza en espacio rig CAMBIA y la esfera la persigue.
            sigue = await page.evaluate("""async () => {
                const g = window.__PP_GAME;
                if (!g.champCurtain) return { ok: false };
                const antes = g.champCurtain.esfera.position.clone
                    ? { x: g.champCurtain.esfera.position.x, z: g.champCurtain.esfera.position.z } : null;
                if (!antes) {
                    const p0 = g.champCurtain.esfera.position;
                    antes = { x: p0.x, z: p0.z };
                }
                g.rig.rotation.y = (g.rig.rotation.y || 0) + 0.7;
                await new Promise(r => setTimeout(r, 500));
                const p1 = g.champCurtain.esfera.position;
                return { ok: true,
                    movio: Math.hypot(p1.x - antes.x, p1.z - antes.z) > 0.05,
                    dist: Math.hypot(g.champCurtain.group.position.x - p1.x,
                        g.champCurtain.group.position.z - p1.z) };
            }""")
            chk(sigue.get("ok") and sigue.get("movio") and abs((sigue.get("dist") or 0) - 2.0) < 0.02,
                f"TELÓN: esfera y cartel persiguen a la cabeza (Δ {sigue.get('movio')} · d {sigue.get('dist')})")
            desmonta = await page.evaluate("""() => new Promise((res) => {
                const t0 = Date.now();
                const iv = setInterval(() => {
                    if (!window.__PP_GAME.champCurtain) { clearInterval(iv); res(true); }
                    else if (Date.now() - t0 > 16000) { clearInterval(iv); res(false); }
                }, 250);
            })""")
            chk(desmonta, "TELÓN: se desmonta solo (sala cargada · <16 s)")

            chk(len(page_errors) == 0,
                f"cero pageerrors ({len(page_errors)}: {page_errors[:2]})")
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} fallos")
    sys.exit(1 if fails else 0)


asyncio.run(main())
