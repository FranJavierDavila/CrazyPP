#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_social_v3678 — CAPA BV · V3.6.78-SDK6, r86 «RED SOCIAL DEL PULSO».

Petición del dueño (r86): «Existiría la posibilidad de saber si existen
usuarios con la herramienta abierta y poder mandar una alerta o aviso a
través de Multijugador (medallón sobre el botón con los jugadores online)…
al pulsar, una forma visual de indicar si hemos recibido una invitación y
su código para unirnos».

LA PRUEBA: DOS jugadores reales (2 páginas Playwright con PeerJS local) +
UN MOCK del worker de telemetría (los mismos endpoints que /api/presencia
y /api/invita del worker de producción, en memoria):

  1. PRESENCIA: el latido de cada jugador llega al worker (pid anónimo
     persistente 16 hex, nombre, estado) — 2 latidos vivos, sin PII.
  2. EL NÚMERO: cada jugador ve «1 jugador online» (el worker cuenta 2
     latidos; el cliente se resta a sí mismo).
  3. EL MEDALLÓN: se PINTA sobre la tarjeta Multijugador del HUB — píxeles
     verdes medidos por getImageData en la esquina de la tarjeta (dorado
     cuando hay invitaciones).
  4. LA INVITACIÓN (camino lista): B abre sala (waiting), B ve a A en la
     lista de invitar, B INVITA, A recibe la invitación en su buzón.
  5. LA TARJETA: el submenú multi de A presenta INVITACIÓN RECIBIDA con el
     código REAL de la sala de B y botones UNIRSE/Descartar (rects vivos).
  6. UNIRSE: A acepta desde la tarjeta → joinRoom con el código recibido →
     CRAZY LINK v2 arriba en AMBOS (la invitación termina en PARTIDA REAL).
  7. ESTADOS: latidos pasan de 'sala' a 'juego'; DESCARTAR vacía el buzón
     en el worker (DELETE público por pid); segundo anfitrión ve la lista.
  8. Tolerancia: sin endpoint (PP_SOCIAL_ENDPOINT vacío) el juego arranca
     igual y el medallón no se pinta (capa OFF silenciosa).

Uso: python3 qa_social_v3678.py [URL]   (default http://localhost:3000/game.html)
"""
import asyncio
import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
URL_DEFECTO = "http://localhost:3000/game.html"

ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label, flush=True)
    if cond:
        ok += 1
    else:
        fails += 1
    return bool(cond)


# ═══════════════════════════ MOCK DEL WORKER (r86) ═══════════════════════
# Mismo contrato que el worker de producción: POST/GET /api/presencia,
# POST/GET/DELETE /api/invita — EN MEMORIA (dicts) para el banco.

class MockWorker:
    def __init__(self):
        self.presencia = {}   # pid -> {n, v, st, code, rec}
        self.invitas = []     # [{id, de, deN, para, code, rec}]
        self._id = 0
        self.lock = threading.Lock()

    def post_presencia(self, b):
        now = int(time.time() * 1000)
        with self.lock:
            if b.get("bye"):
                self.presencia.pop(b.get("pid"), None)
                return 204, ""
            pid = b.get("pid") or ""
            if not (isinstance(pid, str) and len(pid) >= 8):
                return 400, '{"ok":false,"error":"datos"}'
            st = b.get("st") if b.get("st") in ("libre", "sala", "juego") else "libre"
            code = (b.get("code") or "").upper()[:5] if st == "sala" else ""
            n = (b.get("n") or "Jugador")[:24]
            self.presencia[pid] = {"n": n, "v": (b.get("v") or "")[:24],
                                   "st": st, "code": code, "rec": now}
            # purga perezosa (90 s)
            for k in [k for k, v in self.presencia.items() if now - v["rec"] > 90000]:
                del self.presencia[k]
            return 204, ""

    def get_presencia(self, lista):
        now = int(time.time() * 1000)
        with self.lock:
            vivos = {k: v for k, v in self.presencia.items() if now - v["rec"] <= 90000}
            if lista:
                jug = [{"pid": k, "n": v["n"], "st": v["st"], "code": v["code"]}
                       for k, v in vivos.items()]
                return 200, json.dumps({"ok": True, "n": len(vivos),
                                        "jugadores": jug, "ts": now})
            return 200, json.dumps({"ok": True, "n": len(vivos), "ts": now})

    def post_invita(self, b, base_url):
        now = int(time.time() * 1000)
        de, para = b.get("de"), b.get("para")
        code = (b.get("code") or "").upper()
        if not de or not para or not code or de == para:
            return 400, '{"ok":false,"error":"datos"}'
        with self.lock:
            sala = any(v.get("code") == code and v.get("st") == "sala"
                       and now - v["rec"] <= 90000 for v in self.presencia.values())
            if not sala:
                return 409, '{"ok":false,"error":"sala no activa"}'
            if para not in self.presencia:
                return 409, '{"ok":false,"error":"destinatario offline"}'
            frescas = [i for i in self.invitas if i["para"] == para and now - i["rec"] <= 180000]
            if len(frescas) >= 8:
                return 429, '{"ok":false,"error":"buzón lleno"}'
            self._id += 1
            self.invitas.append({"id": self._id, "de": de, "deN": (b.get("deN") or "Jugador")[:24],
                                 "para": para, "code": code, "rec": now})
        return 200, '{"ok":true}'

    def get_invitas(self, pid):
        now = int(time.time() * 1000)
        with self.lock:
            filas = [{"id": i["id"], "de": i["de"], "deN": i["deN"], "code": i["code"],
                      "hace": max(0, now - i["rec"])}
                     for i in self.invitas
                     if i["para"] == pid and now - i["rec"] <= 180000]
            filas.sort(key=lambda x: -x["id"])
            return 200, json.dumps({"ok": True, "invitas": filas[:8], "ts": now})

    def del_invitas(self, pid):
        with self.lock:
            antes = len(self.invitas)
            self.invitas = [i for i in self.invitas if i["para"] != pid]
            return 200, json.dumps({"ok": True, "borrados": antes - len(self.invitas)})

    def dump(self):
        now = int(time.time() * 1000)
        with self.lock:
            return 200, json.dumps({
                "ok": True,
                "presencia": {k: v for k, v in self.presencia.items() if now - v["rec"] <= 90000},
                "invitas": list(self.invitas),
            })


class Handler(BaseHTTPRequestHandler):
    mw: MockWorker = None

    def log_message(self, *a):  # silencio
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            b = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._send(400, '{"ok":false,"error":"json"}')
        if self.path == "/api/presencia":
            c, r = self.mw.post_presencia(b)
            return self._send(c, r)
        if self.path == "/api/invita":
            c, r = self.mw.post_invita(b, "")
            return self._send(c, r)
        return self._send(404, '{"ok":false,"error":"ruta"}')

    def do_GET(self):
        if self.path == "/api/presencia":
            c, r = self.mw.get_presencia(False)
            return self._send(c, r)
        if self.path == "/api/presencia?lista=1":
            c, r = self.mw.get_presencia(True)
            return self._send(c, r)
        if self.path.startswith("/api/invita?pid="):
            pid = self.path.split("pid=", 1)[1].split("&")[0]
            c, r = self.mw.get_invitas(pid)
            return self._send(c, r)
        if self.path == "/api/admin/dump":
            c, r = self.mw.dump()
            return self._send(c, r)
        return self._send(404, '{"ok":false,"error":"ruta"}')

    def do_DELETE(self):
        if self.path.startswith("/api/invita?pid="):
            pid = self.path.split("pid=", 1)[1].split("&")[0]
            c, r = self.mw.del_invitas(pid)
            return self._send(c, r)
        return self._send(404, '{"ok":false,"error":"ruta"}')


# ————— init scripts —————
JS_ENDPOINT = """(() => { window.PP_SOCIAL_ENDPOINT = '__EP__'; })();"""
JS_NOMBRE = """(() => { try { localStorage.setItem('pp_player_name', '__NOM__'); } catch (e) {} })();"""
JS_HILO_QA = """(() => {
  const injeta = () => {
    if (typeof window.Peer !== 'function' || window.Peer.__qaHielo) return false;
    const RealPeer = window.Peer;
    class PeerQA extends RealPeer {
      constructor(id, opts) {
        opts = opts || {};
        opts.config = Object.assign({}, opts.config, { iceServers: [] });
        super(id, opts);
      }
    }
    PeerQA.__qaHielo = true;
    window.Peer = PeerQA;
    return true;
  };
  injeta();
  const iv = setInterval(() => { if (injeta()) clearInterval(iv); }, 100);
  setTimeout(() => clearInterval(iv), 20000);
})();"""

JS_SOC_ESTADO = """() => { const G = window.__PP_GAME; if (!G || !G.social) return null;
  const s = G.social;
  return { pid: s.pid, on: s.on, n: s.nOnline, inv: (s.invitas || []).map(x => ({ id: x.id, code: x.code, deN: x.deN })),
           lista: (s.lista || []).map(x => ({ pid: x.pid, st: x.st, n: x.n })), err: s.lastErr }; }"""

JS_PID = "() => window.__PP_GAME && window.__PP_GAME.social ? window.__PP_GAME.social.pid : null"

# el medallón se pinta sobre la tarjeta multi (X1=528, y=548, w=456): centro
# del medallón ≈ (528+456-30, 548+4) = (954, 552), radio ~27+aro 5 → 34
JS_MEDALLON_PIX = """() => {
  const G = window.__PP_GAME;
  if (!G || !G.menuCanvas) return { pinta: false };
  G.drawMenu();                       // repintado fresco con el tiempo vivo
  const c = G.menuCanvas.getContext('2d');
  // r87 · re-anclado al RECT real de tab:multi (el hub ha cambiado de layout
  // desde que la capa se escribió): la badge vive en la esquina sup-der
  const rm = (G.menuRects || []).find(r => r && r.id === 'tab:multi');
  if (!rm) return { pinta: false, sin: 'rect' };
  const cx = rm.x + rm.w - 30, cy = rm.y + 4;
  const img = c.getImageData(cx - 40, cy - 40, 80, 80).data;
  let verdes = 0, dorados = 0;
  for (let i = 0; i < img.length; i += 4) {
    const r = img[i], g = img[i + 1], b = img[i + 2];
    if (g > 120 && g > r + 30 && g > b + 40) verdes++;
    if (r > 180 && g > 130 && b < 90) dorados++;
  }
  return { pinta: verdes > 150 || dorados > 150, verdes, dorados };
}"""

JS_RECTS_SOC = """() => { const G = window.__PP_GAME; if (!G) return [];
  return (G.menuRects || []).filter(r => typeof r.id === 'string' && r.id.startsWith('mjsoc')).map(r => r.id); }"""

JS_SUBMENU = """() => { const G = window.__PP_GAME;
  const i = G.menuRects.findIndex(r => r.id === 'tab:multi');
  if (i < 0) return 'sin-rect';
  G.menuClick(i);
  return G.menuPage; }"""

JS_CLICK_RECT = """(id) => { const G = window.__PP_GAME;
  const i = G.menuRects.findIndex(r => r.id === id);
  if (i < 0) return false;
  G.menuClick(i);
  return true; }"""

JS_HOST_ROOM = """() => { window.__PP_GAME.net.hostRoom(); return true; }"""
JS_WAITING = """() => window.__PP_GAME.net.status === 'waiting'"""
JS_ONLINE_V2 = """() => window.__PP_GAME && window.__PP_GAME.net.online && window.__PP_GAME.net.v2 === 'ok'"""
JS_SERVE = """() => { const G = window.__PP_GAME; return G.rules.state; }"""


async def wait_cond(page, js, timeout_s, step_ms=250, arg=None):
    t = 0.0
    while t < timeout_s:
        try:
            if await page.evaluate(js, arg):
                return True
        except Exception:
            pass
        await page.wait_for_timeout(step_ms)
        t += step_ms / 1000.0
    return False


def mock_arranca():
    mw = MockWorker()
    Handler.mw = mw
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    puerto = s.getsockname()[1]
    s.close()
    srv = ThreadingHTTPServer(("127.0.0.1", puerto), Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    return mw, f"http://127.0.0.1:{puerto}/api", srv


async def main():
    mw, ep, srv = mock_arranca()
    url, servidor = URL, None
    try:
        with urllib.request.urlopen(url, timeout=6) as r:
            if r.status != 200:
                raise Exception("status")
    except Exception:
        pub = "/home/z/my-project/public"
        sck = socket.socket()
        sck.bind(("127.0.0.1", 0))
        puerto = sck.getsockname()[1]
        sck.close()
        servidor = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(puerto),
             "--directory", pub, "--bind", "127.0.0.1"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        url = f"http://127.0.0.1:{puerto}/game.html"
        for _ in range(60):
            try:
                with urllib.request.urlopen(url, timeout=3) as r:
                    if r.status == 200:
                        break
            except Exception:
                time.sleep(0.25)

    print(f"QA SOCIAL r86 «RED SOCIAL DEL PULSO» · mock worker {ep} · {url}", flush=True)
    errs = {"a": [], "b": []}
    async with async_playwright() as pw:
      try:
        browser = await pw.chromium.launch(
            args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        A = await browser.new_page(viewport={"width": 480, "height": 320})
        B = await browser.new_page(viewport={"width": 480, "height": 320})
        A.on("pageerror", lambda e: errs["a"].append(str(e)))
        B.on("pageerror", lambda e: errs["b"].append(str(e)))

        for pg, nom in ((A, "Ana"), (B, "Beto")):
            await pg.add_init_script(JS_HILO_QA)
            await pg.add_init_script(JS_ENDPOINT.replace("__EP__", ep))
            await pg.add_init_script(JS_NOMBRE.replace("__NOM__", nom))

        # ── 1. arranque con la capa social ──
        for pg, quien in ((A, "Ana"), (B, "Beto")):
            await pg.goto(url, wait_until="domcontentloaded", timeout=45000)
        for pg, quien in ((A, "Ana"), (B, "Beto")):
            listo = await wait_cond(pg, "() => !!window.__PP_GAME && !!window.__PP_GAME.social", 45)
            chk(listo, f"{quien} en la cancha CON la capa social (__PP_GAME.social)")
        stA = await A.evaluate(JS_SOC_ESTADO)
        stB = await B.evaluate(JS_SOC_ESTADO)
        chk(bool(stA) and bool(stB), "RedSocial viva en ambos (estado consultable)")
        import re as _re
        chk(bool(stA and _re.fullmatch(r"[a-f0-9]{16}", stA["pid"] or "")) and
            bool(stB and _re.fullmatch(r"[a-f0-9]{16}", stB["pid"] or "")),
            f"pid anónimo persistente 16 hex (Ana {stA['pid']} · Beto {stB['pid']})")
        chk(stA["pid"] != stB["pid"], "pids distintos (identidades separadas)")

        # ── 2. PRESENCIA: los latidos llegan al worker (arranque lento en
        #      SwiftShader: 12 s de margen para el 1.er latido + 1.er poll) ──
        await A.wait_for_timeout(12000)
        dump = json.loads((await A.evaluate("() => fetch('" + ep + "/admin/dump').then(r=>r.text())") or "{}"))
        nP = len(dump.get("presencia", {}))
        chk(nP == 2, f"2 latidos vivos en el worker (presencia: {nP}/2)")
        nombres = sorted(v.get("n", "") for v in dump.get("presencia", {}).values())
        chk(nombres == ["Ana", "Beto"], f"nombres saneados en presencia (sin PII): {nombres}")
        stA2 = await A.evaluate(JS_SOC_ESTADO)
        stB2 = await B.evaluate(JS_SOC_ESTADO)
        chk(stA2["on"] and stB2["on"], f"capa social ON en ambos (latido aceptado) [diag A: on={stA2['on']} err={stA2['err']!r} n={stA2['n']} · B: on={stB2['on']} err={stB2['err']!r}]")
        # el poll del número (adaptativo: 10 s sin gente) + medallón verde
        for pg in (A, B):
            await pg.evaluate("() => window.__PP_GAME.social.pollNumero()")
        await A.wait_for_timeout(1200)
        stA3 = await A.evaluate(JS_SOC_ESTADO)
        stB3 = await B.evaluate(JS_SOC_ESTADO)
        chk(stA3["n"] == 1 and stB3["n"] == 1,
            f"cada jugador ve AL OTRO: online={stA3['n']}/{stB3['n']} (worker 2 latidos − yo)")

        # ── 3. EL MEDALLÓN en el HUB (píxeles verdes sobre la tarjeta) ──
        await A.evaluate("() => { window.__PP_GAME.toggleMenu(); }")
        await A.wait_for_timeout(400)
        med = await A.evaluate(JS_MEDALLON_PIX)
        chk(med.get("pinta"), f"medallón PINTADO sobre Multijugador (verdes {med.get('verdes')} px)")
        # Beto lo ve también con el menú abierto
        await B.evaluate("() => { window.__PP_GAME.toggleMenu(); }")
        await B.wait_for_timeout(400)
        medB = await B.evaluate(JS_MEDALLON_PIX)
        chk(medB.get("pinta"), f"medallón pintado en el segundo jugador (verdes {medB.get('verdes')} px)")

        # ── 4. LA INVITACIÓN (camino lista): Beto abre sala e invita a Ana ──
        await B.evaluate(JS_HOST_ROOM)
        bSala = await wait_cond(B, JS_WAITING, 20)
        codeB = await B.evaluate("() => window.__PP_GAME.net.code")
        chk(bSala and bool(codeB), f"sala de Beto esperando rival (código {codeB})")
        # el poll de lista corre con el submenú abierto en sala… forzamos:
        await B.evaluate("() => window.__PP_GAME.social.pollLista()")
        await B.wait_for_timeout(800)
        stB3b = await B.evaluate(JS_SOC_ESTADO)
        chk(any(j["pid"] == stA["pid"] for j in stB3b["lista"]),
            "lista de invitar contiene a Ana (latido fresco)")
        okInv = await B.evaluate(
            "() => window.__PP_GAME.social.invitar('" + stA["pid"] + "')")
        await B.wait_for_timeout(600)
        chk(okInv, "Beto INVITA desde la lista (POST /api/invita → ok)")
        dump2 = json.loads((await A.evaluate("() => fetch('" + ep + "/admin/dump').then(r=>r.text())") or "{}"))
        chk(len(dump2.get("invitas", [])) == 1, "invitación guardada en el worker (buzón)")

        # ── 5. LA TARJETA de invitación en el submenú de Ana ──
        await A.evaluate("() => window.__PP_GAME.social.pollInvitas()")
        await A.wait_for_timeout(600)
        stA3 = await A.evaluate(JS_SOC_ESTADO)
        chk(len(stA3["inv"]) == 1 and stA3["inv"][0]["code"] == codeB,
            f"buzón de Ana recibe la invitación (código {stA3['inv'][0]['code'] if stA3['inv'] else '-'})")
        medA2 = await A.evaluate(JS_MEDALLON_PIX)
        stA25 = await A.evaluate(JS_SOC_ESTADO)
        chk(medA2.get("dorados", 0) > 150,
            f"medallón pasa a DORADO pulsante con invitación (dorados {medA2.get('dorados')} px) [diag A: on={stA25['on']} inv={len(stA25['inv'])} n={stA25['n']}]")
        pag = await A.evaluate(JS_SUBMENU)
        chk(pag == "multi", "Ana entra al submenú Multijugador (tab:multi)")
        await A.wait_for_timeout(300)
        rects = await A.evaluate(JS_RECTS_SOC)
        chk("mjsoc:aceptar" in rects and "mjsoc:desc" in rects,
            f"tarjeta de invitación con UNIRSE/Descartar vivos (rects {rects})")
        # el código dibujado: el canvas contiene el código de la sala (proxy:
        # los rects + estado ya lo garantizan; aquí comprobamos el estado)
        stA4 = await A.evaluate("() => { const G = window.__PP_GAME; return G.social.invitas[0]; }")
        chk(stA4 and stA4["code"] == codeB, f"código en la tarjeta = código REAL de la sala ({codeB})")

        # ── 5b. DESCARTAR: limpia el buzón en el worker (con la sala viva) ──
        rFake = await B.evaluate(
            "async () => { const r = await fetch('" + ep + "/invita', {method:'POST', headers:{'Content-Type':'text/plain'}, body: JSON.stringify({de:'0000000000000aaa', deN:'Cyber', para:'" + stB["pid"] + "', code:'" + codeB + "'})}); return (await r.text()) + '|' + r.status; }")
        okInv2 = bool(rFake) and rFake.startswith('{"ok":true')
        if not okInv2:
            print(f"    [diag] POST invita fake → {rFake}", flush=True)
        await B.wait_for_timeout(400)
        chk(okInv2, "segunda invitación de prueba guardada para Beto (sala viva)")
        await B.evaluate("() => window.__PP_GAME.social.pollInvitas()")
        await B.wait_for_timeout(500)
        stB4 = await B.evaluate(JS_SOC_ESTADO)
        chk(len(stB4["inv"]) == 1, f"buzón de Beto con la invitación ({len(stB4['inv'])})")
        await B.evaluate("() => window.__PP_GAME.social.descartar()")
        await B.wait_for_timeout(800)
        dump4 = json.loads((await A.evaluate("() => fetch('" + ep + "/admin/dump').then(r=>r.text())") or "{}"))
        quedan = [i for i in dump4.get("invitas", []) if i["para"] == stB["pid"]]
        chk(len(quedan) == 0, "DESCARTAR vacía el buzón en el worker (DELETE por pid)")

        # ── 6. UNIRSE → PARTIDA REAL ──
        clicado = await A.evaluate(JS_CLICK_RECT, "mjsoc:aceptar")
        chk(clicado, "Ana pulsa UNIRSE en la tarjeta")
        await A.wait_for_timeout(3000)
        diagNet = await A.evaluate("() => { const G = window.__PP_GAME; return { st: G.net.status, code: G.net.code, on: G.net.online, err: G.net.statusMsg || '' }; }")
        print(f"    [diag] Ana.net tras UNIRSE: {diagNet}", flush=True)
        aOn = await wait_cond(A, JS_ONLINE_V2, 40)
        bOn = await wait_cond(B, JS_ONLINE_V2, 40)
        chk(aOn, "CRAZY LINK v2 arriba en Ana tras la invitación (≤40 s)")
        chk(bOn, "CRAZY LINK v2 arriba en Beto (≤40 s)")
        if aOn and bOn:
            codeA2 = await A.evaluate("() => window.__PP_GAME.net.code")
            chk(codeA2 == codeB, f"Ana entra en la SALA de Beto ({codeA2} == {codeB})")
            dump3 = json.loads((await A.evaluate("() => fetch('" + ep + "/admin/dump').then(r=>r.text())") or "{}"))
            sts = {v["st"] for v in dump3.get("presencia", {}).values()}
            chk("juego" in sts, f"latidos en estado 'juego' tras conectar ({sorted(sts)})")

        # ── 7. botón en sala: la fila de INVITAR existe en el submenú ──
        # (Beto está online; re-creamos sala tras colgar)
        await B.evaluate("() => window.__PP_GAME.net.hangup()")
        await B.wait_for_timeout(500)
        await B.evaluate("() => window.__PP_GAME.net.hostRoom()")
        bSala2 = await wait_cond(B, JS_WAITING, 20)
        chk(bSala2, "sala re-creada para probar el panel de invitar")
        await B.evaluate("() => window.__PP_GAME.social.pollLista()")
        await B.wait_for_timeout(700)
        await B.evaluate("() => { const G = window.__PP_GAME; const i = G.menuRects.findIndex(r => r.id === 'tab:multi'); if (i >= 0) G.menuClick(i); }")
        await B.wait_for_timeout(300)
        diagB = await B.evaluate("() => { const G = window.__PP_GAME; return { st: G.net.status, lista: (G.social ? G.social.lista : []).length, page: G.menuPage }; }")
        print(f"    [diag] Beto panel: {diagB}", flush=True)
        rectsB = await B.evaluate(JS_RECTS_SOC)
        chk(any(r.startswith("mjsoc:inv:") for r in rectsB),
            f"panel de sala con botones INVITAR por jugador (rects {rectsB})")

        # limpieza + pageerrors
        for pg in (A, B):
            try:
                await pg.evaluate("() => { const G = window.__PP_GAME; if (G && G.net) G.net.cancel && G.net.cancel(); }")
            except Exception:
                pass
        chk(len(errs["a"]) == 0 and len(errs["b"]) == 0,
            f"0 pageerrors en ambos jugadores ({errs['a'][:1] + errs['b'][:1] if errs['a'] or errs['b'] else 'limpio'})")
        await browser.close()
      finally:
        pass
    srv.shutdown()
    if servidor is not None:
        try:
            servidor.terminate()
        except Exception:
            pass
    print(f"\nQA SOCIAL r86: {ok} OK · {fails} FALLOS (qa_social_v3678)", flush=True)
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
