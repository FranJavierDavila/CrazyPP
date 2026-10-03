#!/usr/bin/env python3
"""Ensambla el index.html final: partes JS + GLB en base64 + plantilla HTML."""
import base64, subprocess, sys, os

BASE = "/home/z/my-project"
# v2.29: COLISIÓN PRECISA EN GOLPEOS RÁPIDOS (cooldown 0,24 s contra el doble
#        golpe fantasma, base de la pala interpolada en el barrido, velocidad
#        de pala más ágil y con techo, sin eventos pala+mesa en el mismo
#        subpaso) + AUDITORÍA DE AUDIO (megáfono independiente del ambiente,
#        hooks de reactivación por SESIÓN XR, prueba de sonido con
#        auto-reparación en Opciones) + MÚSICA DE FONDO EN VR (el tema star
#        suena en bucle mientras el menú principal esté abierto, y en la
#        portada; preferencia compartida pp_music).
# v2.28: NUEVO ARRANQUE — portada web animada minimalista (arte de cabecera
#        CRAZY PING PONG, palas con bandera como selector de idioma y el gran
#        botón cartoon JUGAR/PLAY EN VR que entra directamente en VR; música
#        de portada star.mp3 comprimida) y MENÚ PRINCIPAL EN VR como gran
#        panel flotante delante del jugador: cabecera con el arte + palas de
#        idioma y cuerpo en ACORDEÓN (Jugar Partido / Entrenar / Supervivencia
#        / Crazy "Sorpresas pronto.." / Opciones), una sola sección abierta.
# v2.27: SELECTOR DE IDIOMA (castellano/inglés) — diccionario i18n completo
#        (game_i18n.js), banco de voz inglés Piper en_US-lessac-medium con las
#        MISMAS claves (game_voice_en.js), causas de punto como CLAVES por la
#        red, cartel de fin de partido por idioma y respaldo speechSynthesis
#        localizado. Persistencia en localStorage ('pp_lang').
# v2.26: CARTELES OFICIALES de fin de partido (arte JPEG incrustado).
# v2.25: RIGOR MULTIJUGADOR — emisión en CRUDO y espejo 180° UNA vez en
#        recepción; sincronía por PUNTO DE VISTA en el invitado.
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
# v2.28: assets del nuevo arranque (portada + menú VR)
LA = f"{BASE}/scripts/launch_assets"
HERO = f"{LA}/hero.jpg"
PAD_ES = f"{LA}/pad_es.png"
PAD_EN = f"{LA}/pad_en.png"
PLAY_ES = f"{LA}/play_es.png"
PLAY_EN = f"{LA}/play_en.png"
MUSIC = f"{LA}/star.ogg"
MENU_LOGO = f"{LA}/menulogo.jpg"
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
for ph in ("__POSTER_WIN_B64__", "__POSTER_LOSE_B64__", "__POSTER_WIN_EN_B64__",
           "__POSTER_LOSE_EN_B64__", "__MENU_LOGO_B64__"):
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

def data_url(path, mime):
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode("ascii")

# --- v2.26/2.27: carteles oficiales por idioma (data URLs JPEG) ---
for ph, path in (("__POSTER_WIN_B64__", POSTER_WIN), ("__POSTER_LOSE_B64__", POSTER_LOSE),
                 ("__POSTER_WIN_EN_B64__", POSTER_WIN_EN), ("__POSTER_LOSE_EN_B64__", POSTER_LOSE_EN)):
    if os.path.isfile(path) and os.path.getsize(path) > 1000:
        js = js.replace(ph, data_url(path, "image/jpeg"))
    else:
        # sin arte para ese idioma: cadena vacía -> el cartel usa el panel de respaldo
        js = js.replace(ph, "")

# --- v2.28: arte de la cabecera del menú VR (recorte del logo) ---
js = js.replace("__MENU_LOGO_B64__", data_url(MENU_LOGO, "image/jpeg"))

for ph in ("__POSTER_WIN_B64__", "__POSTER_LOSE_B64__", "__POSTER_WIN_EN_B64__",
           "__POSTER_LOSE_EN_B64__", "__MENU_LOGO_B64__", "__PALA_GLB_B64__"):
    if ph in js:
        print(f"ERROR: placeholder sin sustituir {ph}")
        sys.exit(1)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>CRAZY PING PONG · Meta Quest 3</title>
<meta name="description" content="Tenis de mesa arcade en WebXR para Meta Quest 3: partido, entrenamiento, supervivencia y multijugador online P2P." />
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { height: 100%; overflow: hidden; background: #050810; }
  body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: #e9edf2; }
  #c { position: fixed; inset: 0; display: block; pointer-events: none; }

  /* ================= v2.28 · PORTADA ANIMADA ================= */
  #overlay {
    position: fixed; inset: 0; z-index: 20;
    display: flex; align-items: center; justify-content: center;
    background: radial-gradient(120% 90% at 50% 8%, #0b2050 0%, #071229 52%, #050810 100%);
    transition: opacity 0.45s ease;
  }
  #overlay.hidden { opacity: 0; pointer-events: none; }

  /* arte de fondo difuminado (Ken Burns lento) */
  .bgblur {
    position: absolute; inset: -90px; z-index: 0;
    background-image: url("__HERO_B64__");
    background-size: cover; background-position: center 38%;
    filter: blur(16px) brightness(0.42) saturate(1.25);
    animation: kenburns 30s ease-in-out infinite alternate;
  }
  @keyframes kenburns {
    from { transform: scale(1.06) translate(-1.2%, -1%); }
    to   { transform: scale(1.22) translate(1.4%, 1.6%); }
  }
  /* haces de luz de pabellón barriendo el fondo */
  .rays {
    position: absolute; top: -30%; height: 170%; width: 34vw; z-index: 0;
    background: linear-gradient(90deg, transparent 6%, rgba(96,166,255,0.13) 50%, transparent 94%);
    transform: rotate(14deg); filter: blur(3px);
    animation: sweep 10s ease-in-out infinite alternate;
  }
  .rays.r1 { left: 8vw; }
  .rays.r2 { right: 8vw; transform: rotate(-15deg); animation-delay: -4.5s; animation-duration: 12s; }
  @keyframes sweep {
    from { opacity: 0.25; transform: rotate(11deg) translateX(-4vw); }
    to   { opacity: 0.8;  transform: rotate(17deg) translateX(5vw); }
  }
  /* bolas flotantes que cruzan la escena */
  .bball {
    position: absolute; z-index: 1; border-radius: 50%;
    background: radial-gradient(circle at 34% 30%, #ffffff 0%, #e8ecf2 55%, #b9c2cf 100%);
    box-shadow: 0 0 22px rgba(255,255,255,0.55);
    animation: flyball linear infinite;
  }
  .bball.b1 { width: 26px; height: 26px; top: 62%; animation-duration: 9.5s; }
  .bball.b2 { width: 15px; height: 15px; top: 24%; animation-duration: 13s; animation-delay: -6s; opacity: 0.85; }
  .bball.b3 { width: 11px; height: 11px; top: 78%; animation-duration: 16s; animation-delay: -3s; opacity: 0.6; }
  @keyframes flyball {
    0%   { transform: translate(-8vw, 6vh); opacity: 0; }
    8%   { opacity: 1; }
    50%  { transform: translate(46vw, -9vh); }
    92%  { opacity: 1; }
    100% { transform: translate(108vw, 5vh); opacity: 0; }
  }
  /* estrellitas doradas titilando */
  .star { position: absolute; z-index: 1; width: 7px; height: 7px; border-radius: 50%;
    background: #ffd257; box-shadow: 0 0 10px #ffd257; animation: twinkle 3.2s ease-in-out infinite; }
  .star.s1 { left: 12%; top: 18%; } .star.s2 { left: 85%; top: 26%; animation-delay: -1.1s; }
  .star.s3 { left: 22%; top: 74%; animation-delay: -2s; } .star.s4 { left: 76%; top: 70%; animation-delay: -0.6s; }
  .star.s5 { left: 50%; top: 12%; animation-delay: -2.6s; } .star.s6 { left: 38%; top: 86%; animation-delay: -1.7s; }
  @keyframes twinkle {
    0%, 100% { opacity: 0.15; transform: scale(0.7); }
    50% { opacity: 0.95; transform: scale(1.25); }
  }

  .stage { position: relative; z-index: 2; display: flex; flex-direction: column;
    align-items: center; gap: 22px; width: 100%; padding: 18px;
    max-height: 100%; overflow-y: auto; }

  /* cabecera: arte oficial del juego flotando */
  .hero-wrap { animation: heroFloat 6s ease-in-out infinite; }
  .hero-wrap img {
    display: block; width: min(680px, 90vw); border-radius: 26px;
    border: 2px solid rgba(232, 180, 90, 0.45);
    box-shadow: 0 30px 90px rgba(2, 8, 24, 0.75), 0 0 46px rgba(59, 130, 246, 0.35);
    animation: heroGlow 6s ease-in-out infinite;
  }
  @keyframes heroFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-14px); }
  }
  @keyframes heroGlow {
    0%, 100% { box-shadow: 0 30px 90px rgba(2, 8, 24, 0.75), 0 0 46px rgba(59, 130, 246, 0.35); }
    50% { box-shadow: 0 30px 90px rgba(2, 8, 24, 0.75), 0 0 70px rgba(96, 166, 255, 0.55); }
  }

  /* selector de idioma: dos palas con bandera */
  .padrow { display: flex; gap: 26px; }
  .padbtn {
    display: flex; flex-direction: column; align-items: center; gap: 7px;
    background: rgba(255,255,255,0.055); border: 2px solid rgba(255,255,255,0.16);
    border-radius: 22px; padding: 12px 24px 9px; cursor: pointer;
    transition: transform 0.18s, border-color 0.18s, box-shadow 0.18s, background 0.18s;
  }
  .padbtn img {
    width: 84px; height: 84px; object-fit: contain;
    filter: drop-shadow(0 6px 14px rgba(0,0,0,0.55));
    animation: padBob 3.6s ease-in-out infinite;
  }
  .padbtn[data-lang="en"] img { animation-delay: -1.8s; }
  @keyframes padBob {
    0%, 100% { transform: rotate(-5deg) translateY(0); }
    50% { transform: rotate(5deg) translateY(-4px); }
  }
  .padbtn .padlbl { font-size: 13px; font-weight: 800; letter-spacing: 2.2px; color: #9aa7b4; }
  .padbtn:hover { transform: translateY(-4px); border-color: rgba(232,180,90,0.55); }
  .padbtn.active {
    border-color: #e8b45a; background: rgba(232, 180, 90, 0.12);
    box-shadow: 0 0 26px rgba(232, 180, 90, 0.35);
  }
  .padbtn.active .padlbl { color: #ffd257; }
  .padbtn.active img { filter: drop-shadow(0 0 16px rgba(232,180,90,0.65)) drop-shadow(0 6px 14px rgba(0,0,0,0.55)); }

  /* gran botón cartoon JUGAR / PLAY EN VR */
  #vrbtn { background: none; border: none; cursor: pointer; margin-top: 4px; }
  #vrbtn img {
    display: block; width: min(360px, 76vw);
    filter: drop-shadow(0 14px 26px rgba(0,0,0,0.6));
    animation: playPulse 1.9s ease-in-out infinite, playWiggle 4.8s ease-in-out infinite;
    transition: transform 0.18s;
  }
  #vrbtn:hover img { transform: scale(1.1); }
  #vrbtn:active img { transform: scale(0.97); }
  @keyframes playPulse {
    0%, 100% { filter: drop-shadow(0 14px 26px rgba(0,0,0,0.6)) drop-shadow(0 0 12px rgba(232,180,90,0.25)); }
    50% { filter: drop-shadow(0 14px 26px rgba(0,0,0,0.6)) drop-shadow(0 0 34px rgba(232,180,90,0.6)); }
  }
  @keyframes playWiggle {
    0%, 84%, 100% { rotate: 0deg; }
    88% { rotate: -2.4deg; }
    92% { rotate: 2.2deg; }
    96% { rotate: -1.2deg; }
  }

  #status { font-size: 13.5px; color: #8d9aa8; min-height: 20px; text-align: center;
    max-width: 720px; line-height: 1.5; }
  .footer { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #75828f; }
  .footlink {
    background: none; border: none; cursor: pointer; font-size: 13px; color: #8fd3e8;
    text-decoration: underline dotted; padding: 2px 4px;
  }
  .footlink:hover { color: #b7e7f5; }
  .footlink:disabled { color: #5c6672; text-decoration: none; cursor: not-allowed; }
  .dot { color: #4a5560; }

  #mutebtn {
    position: fixed; right: 16px; bottom: 14px; z-index: 30;
    width: 46px; height: 46px; border-radius: 50%;
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.28);
    font-size: 20px; cursor: pointer; transition: all 0.15s;
  }
  #mutebtn:hover { background: rgba(255,255,255,0.16); }
  #mutebtn.off { opacity: 0.55; }

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
  <div class="bgblur"></div>
  <div class="rays r1"></div>
  <div class="rays r2"></div>
  <span class="bball b1"></span>
  <span class="bball b2"></span>
  <span class="bball b3"></span>
  <span class="star s1"></span><span class="star s2"></span><span class="star s3"></span>
  <span class="star s4"></span><span class="star s5"></span><span class="star s6"></span>

  <main class="stage">
    <div class="hero-wrap">
      <img src="__HERO_B64__" alt="CRAZY PING PONG" />
    </div>

    <div class="padrow">
      <button class="padbtn" data-lang="es">
        <img id="padEs" src="__PAD_ES_B64__" alt="Español" />
        <span class="padlbl">ESPAÑOL</span>
      </button>
      <button class="padbtn" data-lang="en">
        <img id="padEn" src="__PAD_EN_B64__" alt="English" />
        <span class="padlbl">ENGLISH</span>
      </button>
    </div>

    <button id="vrbtn" aria-label="Jugar en VR">
      <img id="playEs" src="__PLAY_ES_B64__" alt="JUGAR EN VR" />
      <img id="playEn" src="__PLAY_EN_B64__" alt="PLAY IN VR" style="display:none" />
    </button>

    <div id="status">Comprobando compatibilidad con WebXR…</div>
    <div class="footer">
      <button id="spectate" class="footlink" data-i18n="ov_demo">Ver demo en pantalla (sin visor)</button>
      <span class="dot">·</span>
      <button id="arbtn" class="footlink" data-i18n="ov_ar">🏠 PASSTHROUGH · tu habitación</button>
    </div>
  </main>

  <button id="mutebtn" data-i18n-title="music_title">🔊</button>
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
<!-- v2.28/2.29: música de la portada Y del menú VR (arranca con el primer
     gesto; botón 🔊; el juego la decodifica a WebAudio dentro de VR) -->
<script>
(function () {
  var state = { audio: null, on: true, started: false };
  try { state.on = localStorage.getItem('pp_music') !== '0'; } catch (e) { /* */ }
  // v2.29: la MISMA pista la usa el juego dentro de VR (WebAudio)
  window.__PP_MUSIC_URL = '__MUSIC_B64__';
  function el() {
    if (!state.audio) {
      // una sola copia incrustada: __PP_MUSIC_URL (también la usa el juego en VR)
      state.audio = new Audio(window.__PP_MUSIC_URL);
      state.audio.loop = true;
      state.audio.volume = 0.5;
    }
    return state.audio;
  }
  function start() {
    if (!state.on) return;
    var a = el();
    var p = a.play();
    if (p && p.catch) p.catch(function () { /* el gesto llega después */ });
  }
  document.addEventListener('pointerdown', function () {
    if (!state.started) { state.started = true; start(); }
  });
  var mb = document.getElementById('mutebtn');
  function paint() {
    // v2.29: relee la preferencia (el menú de VR puede haberla cambiado)
    try { state.on = localStorage.getItem('pp_music') !== '0'; } catch (e) { /* */ }
    if (!mb) return;
    mb.textContent = state.on ? '\\uD83D\\uDD0A' : '\\uD83D\\uDD07';
    mb.classList.toggle('off', !state.on);
  }
  if (mb) {
    paint();
    mb.addEventListener('click', function (e) {
      e.stopPropagation();
      state.on = !state.on;
      try { localStorage.setItem('pp_music', state.on ? '1' : '0'); } catch (err) { /* */ }
      if (state.on) { state.started = true; start(); }
      else if (state.audio) state.audio.pause();
      paint();
    });
    document.addEventListener('pp-lang', paint);
  }
  // la sesión VR pausa la música de portada (dentro suena la de WebAudio);
  // al volver a la portada se reanuda respetando la preferencia MÁS RECIENTE
  window.__ppMusic = {
    pause: function () { if (state.audio) state.audio.pause(); },
    resume: function () {
      try { state.on = localStorage.getItem('pp_music') !== '0'; } catch (e) { /* */ }
      paint();
      if (state.on && state.started) start();
    },
  };
})();
</script>
</body>
</html>
"""

html = HTML.replace("__GAME_JS__", js).replace("__PEERJS_JS__", peerjs_js)

# --- v2.28: assets de la portada (data URLs) ---
html = html.replace("__HERO_B64__", data_url(HERO, "image/jpeg"))
html = html.replace("__PAD_ES_B64__", data_url(PAD_ES, "image/png"))
html = html.replace("__PAD_EN_B64__", data_url(PAD_EN, "image/png"))
html = html.replace("__PLAY_ES_B64__", data_url(PLAY_ES, "image/png"))
html = html.replace("__PLAY_EN_B64__", data_url(PLAY_EN, "image/png"))
html = html.replace("__MUSIC_B64__", data_url(MUSIC, "audio/ogg"))

for ph in ("__HERO_B64__", "__PAD_ES_B64__", "__PAD_EN_B64__", "__PLAY_ES_B64__",
           "__PLAY_EN_B64__", "__MUSIC_B64__", "__GAME_JS__", "__PEERJS_JS__"):
    if ph in html:
        print(f"ERROR: placeholder sin sustituir {ph}")
        sys.exit(1)

os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {OUT}  ({os.path.getsize(OUT)/1e6:.2f} MB)")
