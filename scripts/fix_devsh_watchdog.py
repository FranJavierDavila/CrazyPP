#!/usr/bin/env python3
"""Aplica el watchdog del dev server a .zscripts/dev.sh partiendo del HEAD
de git, preservando el estilo de indentación original (diff quirúrgico).
El código de nivel superior va sin sangría; los bloques internos, con tab."""
import subprocess

T = chr(9)  # tab
ruta = "/home/z/my-project/.zscripts/dev.sh"
src = subprocess.run(
    ["git", "-C", "/home/z/my-project", "show", "HEAD:.zscripts/dev.sh"],
    capture_output=True, text=True, check=True
).stdout

viejo_wait = (
    'log_step_start "Waiting for Next.js dev server"\n'
    'wait_for_service "localhost" "3000" "Next.js dev server"\n'
    'log_step_end "Waiting for Next.js dev server"\n'
    "\n"
    'log_step_start "Health check"\n'
    'echo "[BUN] Performing health check..."\n'
    "curl -fsS localhost:3000 >/dev/null\n"
    'echo "[BUN] Health check passed"\n'
    'log_step_end "Health check"\n'
    "\n"
    "start_mini_services\n"
    "\n"
    'echo "Next.js dev server is running in background (PID: $DEV_PID)."\n'
    "echo \"Use 'kill $DEV_PID' to stop it.\"\n"
    'disown "$DEV_PID" 2>/dev/null || true\n'
    "unset DEV_PID\n"
)

nuevo = (
    'log_step_start "Waiting for Next.js dev server"\n'
    "# Con set -e un fallo aquí mataría el script antes de llegar al watchdog:\n"
    "# si el server no sube a la primera, el watchdog de abajo lo reanimará.\n"
    'wait_for_service "localhost" "3000" "Next.js dev server" \\\n'
    + T + '|| echo "[DEV] aviso: el server no respondió en 60 s; el watchdog lo reanimará"\n'
    'log_step_end "Waiting for Next.js dev server"\n'
    "\n"
    'log_step_start "Health check"\n'
    'echo "[BUN] Performing health check..."\n'
    "curl -fsS localhost:3000 >/dev/null \\\n"
    + T + T + '|| echo "[DEV] health check falló; el watchdog lo cubrirá"\n'
    'echo "[BUN] Health check passed"\n'
    'log_step_end "Health check"\n'
    "\n"
    "start_mini_services\n"
    "\n"
    "# ── Watchdog del dev server ──────────────────────────────────────────\n"
    "# El server de Next muere en idle y el preview se queda en 502 para\n"
    "# siempre: el boot lo arranca una vez y nada lo reanima. Este bucle\n"
    "# (hijo del boot, como el relay de mini-services, que sí sobrevive\n"
    "# toda la vida del sandbox) rearranca next dev cada vez que muera.\n"
    "# El trap cleanup de arriba solo actúa con INT/TERM (apagado real).\n"
    'echo "Next.js dev server is running in background (PID: $DEV_PID)."\n'
    'echo "[WATCHDOG] activo: si el server muere se rearranca automáticamente"\n'
    "while true; do\n"
    + T + "sleep 15\n"
    + T + 'if ! kill -0 "$DEV_PID" 2>/dev/null; then\n'
    + T + T + "echo \"[WATCHDOG] $(date '+%F %T') next dev (PID $DEV_PID) murió — reanimando...\"\n"
    + T + T + "bun run dev &\n"
    + T + T + "DEV_PID=$!\n"
    + T + T + "sleep 5\n"
    + T + "fi\n"
    "done\n"
)

if viejo_wait not in src:
    raise SystemExit("ERROR: bloque original no encontrado en HEAD (¿ya aplicado?)")

resultado = src.replace(viejo_wait, nuevo, 1)
with open(ruta, "w") as f:
    f.write(resultado)
print("dev.sh actualizado con watchdog (estilo original preservado)")
