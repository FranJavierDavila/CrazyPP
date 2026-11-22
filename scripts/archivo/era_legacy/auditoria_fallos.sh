#!/bin/bash
# Re-ejecuta SOLO los tests fallidos guardando su salida completa
cd /home/z/my-project
mkdir -p scripts/auditoria_fallos
for t in qa_net_unit_v3628 test_cadena_r91 test_m7e_persistencia_v36113 \
         test_p4_ver_mismatch_v36115 test_p4_selfcheck_v36116 \
         test_r21_bolas_v36117 test_r23_hall_spin_v36118 test_r24_spin_cabana_v36119 \
         test_r25_sup_bola_v36120 test_r26_sup_v36121 test_r26b_sorpresa_v36122 \
         test_r27_foro3d_v36123 test_r28_bola_salones_v36124 test_r29_sup_poderes_v36125 \
         test_r30_fenix_salones_v36126 test_r31_higiene_v36127 test_r32_salones_v36128 \
         test_r33_poderes_v36129 test_r34_fixes_v36130 test_r35_prisma_v36131 \
         test_r36_red_v36132 test_r37_red_v36133 test_r38_rascacielos_v36134 \
         test_r39_arcano_v36135 test_r40_arcano_v36136 test_r41_arcano_holo_v36137 \
         test_r43_destellos_red_v36138 test_r45_vitrina_cielo_v36139 \
         test_worker_r169 test_zip_editor; do
  f="scripts/$t.mjs"
  timeout 150 bun "$f" > "scripts/auditoria_fallos/$t.out" 2>&1
  echo "$t → RC=$?"
done
timeout 150 python3 scripts/test_ai_returns.py > scripts/auditoria_fallos/test_ai_returns.out 2>&1; echo "test_ai_returns → RC=$?"
echo FIN
