#!/bin/bash
# ============================================================
# PUESTA A CERO DEL PROYECTO — Línea base única: crazypp-v2122.zip (V2.122)
# Ejecutado el 13/10/2026 con autorización expresa del propietario.
# Elimina TODAS las versiones, capturas, fuentes y herramientas
# anteriores a la V2.122. No se archiva nada: borrado definitivo.
# ============================================================
set -u
cd /home/z/my-project

echo "== 1) Capturas y artefactos antiguos en download/ =="
rm -f download/captura-v2*.png download/captura-preview-*.png \
      download/pingpong-*.png download/editor-captura-*.png
rm -rf download/pingpong-quest3 download/pingpong-quest3-v2

echo "== 2) Archivo de builds antiguas =="
rm -rf scripts/archive

echo "== 3) Historial git completo (535 MB de versiones muertas) =="
rm -rf .git

echo "== 4) Herramientas de desarrollo de la línea antigua =="
cd scripts
rm -rf voice launch_assets guia-preview
rm -f game_part1.js game_part2.js game_part3.js game_i18n.js \
      game_voice.js game_voice_en.js build_html.py extract_js.py \
      verify_v2*.py patch_v225.py patch_tests_v228.py shot_v2*.py \
      captura_v2*.py captura_menu_v223.py captura_ia_pose.py \
      diag*.py test_ai_returns.py returns*.json pp2_p*.txt \
      preview_*.png menu_v222.png ia_espera.png ia_swing.png \
      paddle_closeup*.png pala_front.png pala_back.png pala_canto.png \
      pala_rasante-*.png pala.glb.bak poster_*.jpg poster_*_raw.png \
      glb_*.py inspect_glb.py optimize_glb.py prepare_*.py \
      gen_voice.py gen_voice_en.py build_voice.py build_voice_en.py \
      game_module.mjs font-test*.pdf font-test*.png font-test.html \
      guia-cover-check.html download_final_check.png shot_v215*.png \
      2>/dev/null
cd ..

echo "== 5) Prototipo TypeScript antiguo del juego (src/) =="
rm -rf src/lib/game src/components/ping-pong-canvas.tsx

echo "== 6) Resultados temporales de herramientas =="
rm -rf tool-results

echo "== LIMPIEZA COMPLETADA =="
