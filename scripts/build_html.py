#!/usr/bin/env python3
"""Ensambla el index.html final: partes JS + GLB en base64 + plantilla HTML."""
import base64, subprocess, sys, os

BASE = "/home/z/my-project"
# v2.27: SELECTOR DE IDIOMA (castellano/inglés) — diccionario i18n completo
#        (game_i18n.js), banco de voz inglés Piper en_US-lessac-medium con las
#        MISMAS claves (game_voice_en.js), causas de punto como CLAVES por la
#        red, selector en el overlay 2D y en el menú de muñeca (ES/EN),
#        cartel de fin de partido por idioma y respaldo speechSynthesis
#        localizado. Persistencia en localStorage ('pp_lang').
# v2.26: CARTELES OFICIALES de fin de partido — ¡HAS GANADO! / ¡HAS PERDIDO!
#        (arte JPEG incrustado en base64 en el cartel 3D + chip de marcador y
#        revancha) y mensajes de texto alineados; respaldo si la imagen tarda.
# v2.25: RIGOR MULTIJUGADOR — emisión en CRUDO y espejo 180° UNA vez en
#        recepción (fin del doble espejo: el rival ya no aparece en tu mismo
#        lado); spin espejado; sincronía por PUNTO DE VISTA en el invitado
#        (marcador/saque/ganador/causas/mensajes) + megafonía local; voz
#        WebRTC iniciada por el INVITADO al ID de sala (antes autocall) con
#        micro temprano en 2D, tope de 4 s y stream silencioso de respaldo;
#        owner instantáneo y sin fuga de _pendingHits.
# v2.24: cursor del menú SIN espejo vertical (apuntar con el punto = acertar);
#        selectstart/squeeze en un solo espacio + guardia anti-doble pulsación
#        (fin de las casillas "muertas", del teclado que duplicaba letras y de
#        la doble llamada a crear sala); guardias de re-entrada en NetLink.
# v2.23: voz en UN buffer compuesto (sin cortes entre cifras) + ducking del
#        ambiente; pala de la IA con golpes de derecha/revés y hoja que gira;
#        menú con hover en activos, casillas ☑/☐ y área táctil ampliada.
# v2.21: GLB de la pala con materiales OPAQUE (fin del efecto radiografía);
# v2.20: game_voice.js (banco de voz Piper/Opus en base64) va PRIMERO
# v2.27: i18n PRIMERO (T/TLang/setLang), luego los DOS bancos de voz y el juego
PARTS = ([f"{BASE}/scripts/game_i18n.js"]
         + [f"{BASE}/scripts/game_voice.js", f"{BASE}/scripts/game_voice_en.js"]
         + [f"{BASE}/scripts/game_part{i}.js" for i in (1, 2, 3)])
GLB = f"{BASE}/download/pingpong-quest3-v2/assets/pala.glb"
# v2.26/2.27: carteles de fin de partido POR IDIOMA (JPEG 1024x683)
POSTER_WIN = f"{BASE}/scripts/poster_win.jpg"
POSTER_LOSE = f"{BASE}/scripts/poster_lose.jpg"
POSTER_WIN_EN = f"{BASE}/scripts/poster_win_en.jpg"
POSTER_LOSE_EN = f"{BASE}/scripts/poster_lose_en.jpg"
OUT_DIR = f"{BASE}/download/pingpong-quest3-v2"
OUT = f"{OUT_DIR}/index.html"

js = "\n\n".join(open(p, encoding="utf-8").read() for p in PARTS)

# --- PeerJS inline (multijugador v2.19) ---
PEERJS = f"{BASE}/scripts/peerjs.min.js"
peerjs_js = open(PEERJS, encoding="utf-8").read()
if "</script>" in peerjs_js.lower():
    print("ERROR: peerjs.min.js contiene </script>")
    sys.exit(1)

# --- validación de sintaxis con node (sustituyendo los placeholders) ---
check = js.replace("__PALA_GLB_B64__", "Zm9v")
for ph in ("__POSTER_WIN_B64__", "__POSTER_LOSE_B64__", "__POSTER_WIN_EN_B64__", "__POSTER_LOSE_EN_B64__"):
    check = check.replace(ph, "data:image/jpeg;base64,Zm9v")
with open("/tmp/game_check.mjs", "w", encoding="utf-8") as f:
    f.write(check)
r = subprocess.run(["node", "--check", "/tmp/game_check.mjs"], capture_output=True, text=True)
if r.returncode != 0:
    print("ERROR DE SINTAXIS:\n", r.stderr)
    sys.exit(1)
print("sintaxis OK")

# --- incrustar GLB ---
b64 = base64.b64encode(open(GLB, "rb").read()).decode("ascii")
js = js.replace("__PALA_GLB_B64__", b64)

# --- v2.26/2.27: incrustar carteles oficiales por idioma (data URLs JPEG) ---
for ph, path in (("__POSTER_WIN_B64__", POSTER_WIN), ("__POSTER_LOSE_B64__", POSTER_LOSE),
                 ("__POSTER_WIN_EN_B64__", POSTER_WIN_EN), ("__POSTER_LOSE_EN_B64__", POSTER_LOSE_EN)):
    if os.path.isfile(path) and os.path.getsize(path) > 1000:
        pb = "data:image/jpeg;base64," + base64.b64encode(open(path, "rb").read()).decode("ascii")
        js = js.replace(ph, pb)
    else:
        # sin arte para ese idioma: cadena vacía -> el cartel usa el panel de respaldo
        js = js.replace(ph, "")
for ph in ("__POSTER_WIN_B64__", "__POSTER_LOSE_B64__", "__POSTER_WIN_EN_B64__", "__POSTER_LOSE_EN_B64__", "__PALA_GLB_B64__"):
    if ph in js:
        print(f"ERROR: placeholder sin sustituir {ph}")
        sys.exit(1)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Ping Pong XR · Meta Quest 3</title>
<meta name="description" content="Tenis de mesa realista en WebXR para Meta Quest 3: saque con mano libre, reglas ITTF y pala 3D real." />
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { height: 100%; overflow: hidden; background: #0b0e11; }
  body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: #e9edf2; }
  #c { position: fixed; inset: 0; display: block; pointer-events: none; }

  /* ---------- Overlay de bienvenida ---------- */
  #overlay {
    position: fixed; inset: 0; z-index: 20;
    display: flex; align-items: center; justify-content: center;
    background: rgba(6, 9, 13, 0.62); backdrop-filter: blur(7px);
    transition: opacity 0.45s ease;
  }
  #overlay.hidden { opacity: 0; pointer-events: none; }
  .card {
    width: min(600px, calc(100% - 36px));
    max-height: calc(100% - 30px);
    overflow-y: auto;
    background: rgba(15, 19, 25, 0.93);
    border: 1px solid rgba(232, 180, 90, 0.35);
    border-radius: 20px; padding: 28px 32px 24px;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.55);
  }
  .card h1 { font-size: 30px; letter-spacing: 0.5px; }
  .card h1 span { color: #e8b45a; }
  .tag { margin: 6px 0 16px; font-size: 14px; color: #9aa7b4; }
  ul.keys { list-style: none; margin-bottom: 16px; }
  ul.keys li { font-size: 14px; line-height: 1.75; color: #cfd8e0; margin-bottom: 7px; }
  ul.keys b {
    display: inline-block; min-width: 74px; text-align: center;
    color: #e8b45a; font-weight: 600;
    background: rgba(232, 180, 90, 0.1);
    border: 1px solid rgba(232, 180, 90, 0.4);
    border-radius: 7px; padding: 1px 8px; margin-right: 8px;
    font-size: 13px;
  }
  .diffrow { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
  .diffrow .lbl { font-size: 13px; color: #9aa7b4; margin-right: 4px; }
  .diff, .them {
    flex: 1; padding: 9px 0; font-size: 14px; font-weight: 600;
    color: #cfd8e0; background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 10px;
    cursor: pointer; transition: all 0.15s;
  }
  .diff:hover, .them:hover { border-color: rgba(232, 180, 90, 0.5); }
  .diff.active, .them.active { color: #10131a; background: #e8b45a; border-color: #e8b45a; }
  #status { font-size: 13.5px; color: #8d9aa8; min-height: 20px; margin-bottom: 12px; line-height: 1.5; }
  #vrbtn {
    width: 100%; padding: 16px; font-size: 17px; font-weight: 800; letter-spacing: 1.2px;
    color: #10131a; background: linear-gradient(135deg, #f0c069, #e8b45a);
    border: none; border-radius: 13px; cursor: pointer; margin-bottom: 10px;
  }
  #vrbtn:hover:not(:disabled) { filter: brightness(1.08); }
  #vrbtn:disabled { background: rgba(255, 255, 255, 0.08); color: #6b7683; cursor: not-allowed; }
  #spectate {
    width: 100%; padding: 12px; font-size: 14px; font-weight: 600;
    color: #aeb9c5; background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 11px; cursor: pointer;
  }
  #spectate:hover { border-color: rgba(255, 255, 255, 0.4); }
  .hint { margin-top: 14px; font-size: 12px; line-height: 1.65; color: #75828f; }
  .hint b { color: #9aa7b4; }

  /* ---------- Agarres guardados ---------- */
  .grips {
    border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 14px;
    padding: 12px 14px; margin-bottom: 16px;
  }
  .grips-head { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
  .grips-head .lbl { font-size: 12px; color: #9aa7b4; letter-spacing: 1px; white-space: nowrap; }
  #gripName {
    flex: 1; min-width: 0; background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.16); border-radius: 8px;
    color: #e9edf2; padding: 7px 10px; font-size: 13px; outline: none;
  }
  .grips-row { display: flex; gap: 6px; }
  #gripSel {
    flex: 1.4; min-width: 0; background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.16); border-radius: 8px;
    color: #e9edf2; padding: 7px 8px; font-size: 13px;
  }
  .mini {
    flex: 1; padding: 7px 4px; font-size: 12px; font-weight: 600; color: #cfd8e0;
    background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 8px; cursor: pointer; white-space: nowrap;
  }
  .mini:hover { border-color: rgba(232, 180, 90, 0.5); }
  #trainbtn {
    width: 100%; padding: 12px; font-size: 14px; font-weight: 700;
    color: #e8b45a; background: rgba(232, 180, 90, 0.10);
    border: 1px solid rgba(232, 180, 90, 0.45); border-radius: 11px;
    cursor: pointer; margin-bottom: 10px;
  }
  #trainbtn:hover:not(:disabled) { background: rgba(232, 180, 90, 0.18); }
  #trainbtn:disabled {
    color: #6b7683; background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.12); cursor: not-allowed;
  }
  #survbtn {
    width: 100%; padding: 12px; font-size: 14px; font-weight: 700;
    color: #9fd98a; background: rgba(127, 176, 105, 0.10);
    border: 1px solid rgba(127, 176, 105, 0.45); border-radius: 11px;
    cursor: pointer; margin-bottom: 10px;
  }
  #survbtn:hover:not(:disabled) { background: rgba(127, 176, 105, 0.18); }
  #survbtn:disabled {
    color: #6b7683; background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.12); cursor: not-allowed;
  }
  .row2 { display: flex; gap: 10px; margin-bottom: 10px; }
  #arbtn {
    flex: 1; padding: 11px 6px; font-size: 12.5px; font-weight: 700;
    color: #8fd3e8; background: rgba(87, 199, 255, 0.08);
    border: 1px solid rgba(87, 199, 255, 0.4); border-radius: 11px; cursor: pointer;
  }
  #arbtn:hover:not(:disabled) { background: rgba(87, 199, 255, 0.16); }
  #arbtn:disabled {
    color: #6b7683; background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.12); cursor: not-allowed;
  }
  #ambbtn {
    flex: 1; padding: 11px 6px; font-size: 12.5px; font-weight: 700;
    color: #cfd8e0; background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 11px; cursor: pointer;
  }
  #ambbtn:hover { border-color: rgba(232, 180, 90, 0.5); }

  /* ---------- Estadísticas y logros ---------- */
  .stats {
    border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 14px;
    padding: 12px 14px; margin-bottom: 16px;
  }
  .stats-head {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 8px;
  }
  .stats-head .lbl { font-size: 12px; color: #9aa7b4; letter-spacing: 1px; }
  .stats-head .mini { flex: 0 0 auto; padding: 4px 12px; }
  .stats-line { font-size: 13.5px; color: #cfd8e0; line-height: 1.55; margin-bottom: 9px; }
  .achrow { display: flex; flex-wrap: wrap; gap: 6px; }
  .ach {
    font-size: 11.5px; padding: 4px 9px; border-radius: 8px; white-space: nowrap;
    border: 1px solid rgba(255, 255, 255, 0.10); color: #5c6672;
    background: rgba(255, 255, 255, 0.03); cursor: default;
  }
  .ach.on {
    color: #e8b45a; border-color: rgba(232, 180, 90, 0.5);
    background: rgba(232, 180, 90, 0.08);
  }

  /* ---------- HUD (modo espectador) ---------- */
  #hud {
    position: fixed; left: 50%; bottom: 18px; transform: translateX(-50%);
    z-index: 15; display: none; align-items: center; gap: 12px;
    background: rgba(15, 19, 25, 0.88); border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 999px; padding: 9px 10px 9px 18px;
  }
  #hud.show { display: flex; }
  #hud-score { font-weight: 800; font-size: 16px; color: #f2f4f6; letter-spacing: 1px; }
  #hud-msg { font-size: 13px; color: #aeb9c5; max-width: 46vw; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  #hud-info {
    width: 30px; height: 30px; border-radius: 50%;
    background: rgba(232, 180, 90, 0.15); color: #e8b45a;
    border: 1px solid rgba(232, 180, 90, 0.4); font-size: 14px; font-weight: 700; cursor: pointer;
  }

  /* ---------- v2.27 · Selector de idioma ---------- */
  .langrow {
    display: flex; align-items: center; gap: 8px; margin-bottom: 14px;
  }
  .langrow .lbl { font-size: 13px; color: #9aa7b4; margin-right: 4px; }
  .langbtn {
    padding: 8px 0; width: 96px; font-size: 14px; font-weight: 700;
    color: #cfd8e0; background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 10px;
    cursor: pointer; transition: all 0.15s;
  }
  .langbtn:hover { border-color: rgba(232, 180, 90, 0.5); }
  .langbtn.active { color: #10131a; background: #e8b45a; border-color: #e8b45a; }
</style>
<script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"
    }
  }
</script>
</head>
<body>
<canvas id="c"></canvas>

<div id="overlay">
  <div class="card">
    <h1>🏓 PING PONG <span>XR</span></h1>
    <div class="tag" data-i18n="ov_tag">Reglas ITTF · saque con mano libre y física real · pala 3D · Meta Quest 3</div>
    <div class="langrow">
      <span class="lbl" data-i18n="ov_lang">🌐 Idioma / Language</span>
      <button class="langbtn active" data-lang="es">ESPAÑOL</button>
      <button class="langbtn" data-lang="en">ENGLISH</button>
    </div>
    <ul class="keys">
      <li data-i18n-html="ov_serve"></li>
      <li data-i18n-html="ov_hit"></li>
      <li data-i18n-html="ov_hand"></li>
      <li data-i18n-html="ov_menu"></li>
      <li data-i18n-html="ov_online"></li>
      <li data-i18n-html="ov_rules"></li>
      <li data-i18n-html="ov_spin"></li>
      <li data-i18n-html="ov_train"></li>
    </ul>
    <div class="diffrow">
      <span class="lbl" data-i18n="ov_difficulty">DIFICULTAD</span>
      <button class="diff" data-diff="easy">Fácil</button>
      <button class="diff active" data-diff="medium">Media</button>
      <button class="diff" data-diff="hard">Difícil</button>
    </div>
    <div class="diffrow">
      <span class="lbl" data-i18n="ov_room">SALA</span>
      <button class="them active" data-theme="pabellon">🏓 Pabellón</button>
      <button class="them" data-theme="neon">💜 Neón</button>
      <button class="them" data-theme="atardecer">🌅 Atardecer</button>
      <button class="them" data-theme="artico">❄️ Ártico</button>
    </div>
    <div class="grips">
      <div class="grips-head">
        <span class="lbl" data-i18n="ov_grips">AGARRES DE PALA</span>
        <input id="gripName" type="text" maxlength="24" data-i18n-ph="ov_grip_ph" placeholder="Nombre para guardar el ajuste actual" />
      </div>
      <div class="grips-row">
        <select id="gripSel"></select>
        <button class="mini" id="gripLoad" data-i18n="ov_grip_load">Cargar</button>
        <button class="mini" id="gripSave" data-i18n="ov_grip_save">Guardar</button>
        <button class="mini" id="gripDel" data-i18n="ov_grip_del">Borrar</button>
        <button class="mini" id="gripReset" data-i18n="ov_grip_reset">Natural</button>
      </div>
    </div>
    <div class="stats">
      <div class="stats-head">
        <span class="lbl" data-i18n="ov_progress">TU PROGRESO</span>
        <button class="mini" id="statsReset" data-i18n="ov_clear">Borrar</button>
      </div>
      <div class="stats-line" id="statsLine">—</div>
      <div class="achrow" id="achRow"></div>
    </div>
    <div id="status">Comprobando compatibilidad con WebXR…</div>
    <button id="survbtn" disabled data-i18n="ov_surv">🏆 SUPERVIVENCIA EN VR · ¿cuántos golpes aguantas?</button>
    <button id="trainbtn" disabled data-i18n="ov_train_btn">ENTRENAR GOLPES EN VR · ajustar pala</button>
    <button id="vrbtn" disabled data-i18n="ov_vr">ENTRAR EN VR</button>
    <div class="row2">
      <button id="arbtn" disabled data-i18n="ov_ar">🏠 PASSTHROUGH · tu habitación</button>
      <button id="ambbtn">🔊 Ambiente de torneo: SÍ</button>
    </div>
    <button id="spectate" data-i18n="ov_demo">Ver demo en pantalla (sin visor)</button>
    <div class="hint" data-i18n-html="ov_hint">
      <b>En el visor:</b> sube esta carpeta a <b>Netlify Drop</b> y abre el enlace con el
      <b>Meta Quest Browser</b> (requiere HTTPS). Sin visor, el modo demo juega IA contra IA.
    </div>
  </div>
</div>

<div id="hud">
  <span id="hud-score">0 : 0</span>
  <span id="hud-msg">…</span>
  <button id="hud-info" title="Información">i</button>
</div>

<script type="module">
__GAME_JS__
</script>
<!-- v2.19: PeerJS incrustado (P2P WebRTC para multijugador + voz) -->
<script>
__PEERJS_JS__
</script>
</body>
</html>
"""

html = HTML.replace("__GAME_JS__", js).replace("__PEERJS_JS__", peerjs_js)
os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {OUT}  ({os.path.getsize(OUT)/1e6:.2f} MB)")
