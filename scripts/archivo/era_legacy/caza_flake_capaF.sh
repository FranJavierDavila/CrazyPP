#!/bin/bash
# caza_flake_capaF.sh — reproducir el flake de la capa F en su contexto real:
# qa_imp2 corre justo DESPUÉS de qa_sup1 (navegador caliente, mismo runtime).
# Uso: bash scripts/caza_flake_capaF.sh [N_pasadas]
N=${1:-5}
FALLOS=0
for i in $(seq 1 "$N"); do
  echo "=== ciclo $i: sup1 (calentamiento) → imp2 ==="
  python3 /home/z/my-project/scripts/qa_sup1_v365.py > /dev/null 2>&1
  python3 /home/z/my-project/scripts/qa_imp2_v351.py > /tmp/caza_f_p$i.txt 2>&1
  RES=$(tail -1 /tmp/caza_f_p$i.txt)
  if echo "$RES" | grep -q "0 fallos"; then
    echo "  ciclo $i: VERDE ($RES)"
  else
    echo "  ciclo $i: FLAKE → $RES"
    grep -n "✗" /tmp/caza_f_p$i.txt | head -8
    FALLOS=$((FALLOS+1))
    cp /tmp/caza_f_p$i.txt /tmp/caza_f_FALLO_$i.txt
  fi
done
echo "=== RESULTADO CAZA: $FALLOS/$N ciclos con flake ==="
