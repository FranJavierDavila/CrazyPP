#!/bin/bash
# batería QA FASE 146 (r52) — game.html 3.6.144-SDK6
cd /home/z/my-project/upload
LOG=/home/z/my-project/scripts/qa_r52_log.txt
: > "$LOG"
run_mjs() {
  local f="$1"
  echo "===== $f" >> "$LOG"
  timeout 240 node --no-warnings "$f" >> "$LOG" 2>&1
  local rc=$?
  local okv=$(grep -c '✓' "$LOG" | tail -1)
  echo "RESULTADO $f rc=$rc oks=$okv" >> "$LOG"
  echo "RESULTADO $f rc=$rc"
}
run_py() {
  local f="$1"; shift
  echo "===== $f $*" >> "$LOG"
  timeout 300 python3 "$f" "$@" >> "$LOG" 2>&1
  local rc=$?
  echo "RESULTADO $f rc=$rc" >> "$LOG"
  echo "RESULTADO $f rc=$rc"
}
for t in test_red_nucleo.mjs \
         test_r30_fenix_salones_v36126.mjs \
         test_r31_higiene_v36127.mjs \
         test_r32_salones_v36128.mjs \
         test_r33_poderes_v36129.mjs \
         test_r34_fixes_v36130.mjs \
         test_r35_prisma_v36131.mjs \
         test_r36_red_v36132.mjs \
         test_r37_red_v36133.mjs \
         test_r38_rascacielos_v36134.mjs \
         test_r39_arcano_v36135.mjs \
         test_r40_arcano_v36136.mjs \
         test_r41_arcano_holo_v36137.mjs \
         test_r43_destellos_red_v36138.mjs \
         test_r45_vitrina_cielo_v36139.mjs ; do
  run_mjs "scripts/$t"
done
echo "BATERIA_MJS_FIN" >> "$LOG"
tail -5 "$LOG"
