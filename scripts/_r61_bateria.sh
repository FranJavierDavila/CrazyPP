#!/bin/bash
# r61 · batería QA verde (patrón r60: node 20 + python 12 + re-ancla r23)
# Log: /tmp/qa_r61_bateria.log
cd /home/z/my-project/upload/scripts
L=/tmp/qa_r61_bateria.log
: > "$L"

run() { # run <nombre> <timeout> <cmd...>
  local nombre="$1" tmo="$2"; shift 2
  echo "=== $nombre ===" >> "$L"
  timeout "$tmo" "$@" >> "$L" 2>&1
  local rc=$?
  echo "=== RC $nombre = $rc ===" >> "$L"
}

# ---- NODE (20) ----
run test_fisica        120 node --no-warnings test_fisica.mjs
run test_fisica_c05    120 node --no-warnings test_fisica_c05.mjs
run test_r21           120 node --no-warnings test_r21_bolas_v36117.mjs
run test_r23_reancla   120 node --no-warnings test_r23_hall_spin_v36118.mjs
run test_r24           120 node --no-warnings test_r24_spin_cabana_v36119.mjs
run test_r26b          120 node --no-warnings test_r26b_sorpresa_v36122.mjs
run test_r30           120 node --no-warnings test_r30_fenix_salones_v36126.mjs
run test_r31           120 node --no-warnings test_r31_higiene_v36127.mjs
run test_r32           120 node --no-warnings test_r32_salones_v36128.mjs
run test_r33           120 node --no-warnings test_r33_poderes_v36129.mjs
run test_r34           120 node --no-warnings test_r34_fixes_v36130.mjs
run test_r35           120 node --no-warnings test_r35_prisma_v36131.mjs
run test_r36           120 node --no-warnings test_r36_red_v36132.mjs
run test_r37           120 node --no-warnings test_r37_red_v36133.mjs
run test_r38           120 node --no-warnings test_r38_rascacielos_v36134.mjs
run test_r39           240 node --no-warnings test_r39_arcano_v36135.mjs
run test_r40           240 node --no-warnings test_r40_arcano_v36136.mjs
run test_r41           240 node --no-warnings test_r41_arcano_holo_v36137.mjs
run test_r43           240 node --no-warnings test_r43_destellos_red_v36138.mjs
run test_r45           120 node --no-warnings test_r45_vitrina_cielo_v36139.mjs
run test_red_nucleo    180 node --no-warnings test_red_nucleo.mjs

# ---- PYTHON (12) ----
run qa_r54_agotados    300 python3 qa_r54_poderes_agotados.py
run qa_version         180 python3 qa_version.py
run qa_sup1_v366       600 python3 qa_sup1_v366.py
run qa_r84             600 python3 qa_r84_v3676.py
run qa_rendimiento     420 python3 qa_rendimiento.py
run qa_r50             300 python3 qa_r50_gatillo_oeste.py
run qa_r46_humo        300 python3 qa_r46_humo_gobernador.py
run qa_telemetria      420 python3 qa_telemetria.py
run qa_dashboard_r53   300 python3 qa_dashboard_r53.py
run qa_dashboard_r56   300 python3 qa_dashboard_r56.py
run qa_r118_dirigida   420 python3 qa_r118_dirigida.py
run qa_r119_dirigida   420 python3 qa_r119_dirigida.py

echo "=== BATERIA COMPLETA ===" >> "$L"
grep -E "^=== RC|RESULTADO" "$L" | tail -80
