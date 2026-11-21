#!/bin/bash
# Auditoría dinámica — batería de arneses del dueño (bun / python3)
cd /home/z/my-project
LOG=scripts/auditoria_tests.log
: > "$LOG"
run_bun() {
  timeout 150 bun "$1" > /tmp/aud_t.out 2>&1
  local rc=$?
  local last
  last=$(tail -1 /tmp/aud_t.out | cut -c1-140)
  if [ $rc -eq 0 ]; then
    echo "✓ RC=0  $1 · $last" >> "$LOG"
  else
    echo "✗ RC=$rc  $1 · $last" >> "$LOG"
  fi
}
run_py() {
  timeout 150 python3 "$1" > /tmp/aud_t.out 2>&1
  local rc=$?
  local last
  last=$(tail -1 /tmp/aud_t.out | cut -c1-140)
  if [ $rc -eq 0 ]; then
    echo "✓ RC=0  $1 · $last" >> "$LOG"
  else
    echo "✗ RC=$rc  $1 · $last" >> "$LOG"
  fi
}
# núcleo (física y red) primero
run_bun scripts/test_fisica.mjs
run_bun scripts/test_fisica_c05.mjs
run_bun scripts/test_fisica_ittf.mjs
run_bun scripts/test_fisica_p0_r86.mjs
run_bun scripts/test_fisica_p0_r87.mjs
run_bun scripts/test_red_nucleo.mjs
run_bun scripts/qa_net_unit_v3628.mjs
run_bun scripts/test_cadena_r91.mjs
run_bun scripts/test_disparo_diferido_r99.mjs
# por rondas
run_bun scripts/test_f1_decode_v36112.mjs
run_bun scripts/test_m7e_persistencia_v36113.mjs
run_bun scripts/test_p4_ice_v36114.mjs
run_bun scripts/test_p4_ver_mismatch_v36115.mjs
run_bun scripts/test_p4_selfcheck_v36116.mjs
run_bun scripts/test_r21_bolas_v36117.mjs
run_bun scripts/test_r23_hall_spin_v36118.mjs
run_bun scripts/test_r24_spin_cabana_v36119.mjs
run_bun scripts/test_r25_sup_bola_v36120.mjs
run_bun scripts/test_r26_sup_v36121.mjs
run_bun scripts/test_r26b_sorpresa_v36122.mjs
run_bun scripts/test_r27_foro3d_v36123.mjs
run_bun scripts/test_r28_bola_salones_v36124.mjs
run_bun scripts/test_r29_sup_poderes_v36125.mjs
run_bun scripts/test_r30_fenix_salones_v36126.mjs
run_bun scripts/test_r31_higiene_v36127.mjs
run_bun scripts/test_r32_salones_v36128.mjs
run_bun scripts/test_r33_poderes_v36129.mjs
run_bun scripts/test_r34_fixes_v36130.mjs
run_bun scripts/test_r35_prisma_v36131.mjs
run_bun scripts/test_r36_red_v36132.mjs
run_bun scripts/test_r37_red_v36133.mjs
run_bun scripts/test_r38_rascacielos_v36134.mjs
run_bun scripts/test_r39_arcano_v36135.mjs
run_bun scripts/test_r40_arcano_v36136.mjs
run_bun scripts/test_r41_arcano_holo_v36137.mjs
run_bun scripts/test_r43_destellos_red_v36138.mjs
run_bun scripts/test_r45_vitrina_cielo_v36139.mjs
run_bun scripts/test_worker_r169.mjs
run_bun scripts/test_zip_editor.mjs
run_py scripts/test_ai_returns.py
echo "=== FIN de la batería ===" >> "$LOG"
