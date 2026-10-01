#!/usr/bin/env python3
"""Ensambla el index.html final: partes JS + GLB en base64 + plantilla HTML."""
import base64, subprocess, sys, os

BASE = "/home/z/my-project"
PARTS = [f"{BASE}/scripts/game_part{i}.js" for i in (1, 2, 3)]
GLB = f"{BASE}/download/pingpong-quest3-v2/assets/pala.glb"
OUT_DIR = f"{BASE}/download/pingpong-quest3-v2"
OUT = f"{OUT_DIR}/index.html"

js = "\n\n".join(open(p, encoding="utf-8").read() for p in PARTS)

# --- validación de sintaxis con node (sustituyendo el placeholder) ---
check = js.replace("__PALA_GLB_B64__", "Zm9v")
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
  .diff {
    flex: 1; padding: 9px 0; font-size: 14px; font-weight: 600;
    color: #cfd8e0; background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 10px;
    cursor: pointer; transition: all 0.15s;
  }
  .diff:hover { border-color: rgba(232, 180, 90, 0.5); }
  .diff.active { color: #10131a; background: #e8b45a; border-color: #e8b45a; }
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
  <div class="card">
    <h1>🏓 PING PONG <span>XR</span></h1>
    <div class="tag">Reglas ITTF · saque con mano libre y física real · pala 3D · Meta Quest 3</div>
    <ul class="keys">
      <li><b>SAQUE</b> La bola descansa en tu <b>mano libre</b>. Aprieta <b>GRIP</b> y suéltalo hacia arriba: la bola sale con la velocidad real de tu mano. (Gatillo = saque asistido)</li>
      <li><b>GOLPE</b> Golpea la bola <b>al caer</b> con la pala (otro mando), desde detrás de la línea de fondo. El saque debe botar en <b>tu campo</b> y luego en el del rival.</li>
      <li><b>A / X</b> Cambia la pala de mano en cualquier momento</li>
      <li><b>REGLAS</b> Rozar la red en saque y pasar = <b>LET</b> (se repite) · volear antes del bote o dar doble golpe = falta · partido a 11 con ventaja de 2</li>
      <li><b>EFECTO</b> Barre la pala de abajo a arriba al golpear para dar lift; de arriba abajo para cortar</li>
    </ul>
    <div class="diffrow">
      <span class="lbl">DIFICULTAD</span>
      <button class="diff" data-diff="easy">Fácil</button>
      <button class="diff active" data-diff="medium">Media</button>
      <button class="diff" data-diff="hard">Difícil</button>
    </div>
    <div id="status">Comprobando compatibilidad con WebXR…</div>
    <button id="vrbtn" disabled>ENTRAR EN VR</button>
    <button id="spectate">Ver demo en pantalla (sin visor)</button>
    <div class="hint">
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
</body>
</html>
"""

html = HTML.replace("__GAME_JS__", js)
os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {OUT}  ({os.path.getsize(OUT)/1e6:.2f} MB)")
