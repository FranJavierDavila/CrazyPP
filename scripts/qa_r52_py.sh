#!/bin/bash
# batería QA FASE 146 (r52) — parte Python
cd /home/z/my-project/upload
LOG=/home/z/my-project/scripts/qa_r52_log_py.txt
: > "$LOG"
run_py() {
  local f="$1"; shift
  echo "===== $f $*" >> "$LOG"
  timeout 300 python3 "$f" "$@" >> "$LOG" 2>&1
  echo "RESULTADO $f rc=$?" >> "$LOG"
  echo "RESULTADO $f rc=$?"
}
run_py scripts/qa_r50_gatillo_oeste.py
run_py scripts/qa_r84_v3676.py
run_py scripts/qa_sup1_v366.py
run_py scripts/qa_r46_humo_gobernador.py
run_py scripts/qa_telemetria.py
run_py scripts/qa_rendimiento.py
run_py scripts/qa_version.py
echo "BATERIA_PY_FIN" >> "$LOG"
tail -3 "$LOG"
