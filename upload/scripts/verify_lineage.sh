#!/bin/bash
# CRAZY PING PONG · verify_lineage.sh
# El contenedor se recicla entre turnos y el repo local puede quedar en un
# snapshot VIEJO (ha pasado 3 veces: r56, r58 y Task 162). GitHub es la
# ÚNICA fuente de verdad. Ejecutar esto AL EMPEZAR cada turno de trabajo.
set -e
cd /home/z/my-project
[ -f scripts/worker-tele/.github-pat ] || { echo "FALTA .github-pat"; exit 1; }
TOKEN=$(cat scripts/worker-tele/.github-pat)
git fetch "https://${TOKEN}@github.com/FranJavierDavila/CrazyPP.git" \
  "+refs/heads/*:refs/remotes/origin/*" "+refs/tags/*:refs/tags/*" 2>&1 \
  | sed "s/${TOKEN}/***/g" | tail -1
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" != "$REMOTE" ]; then
  echo "REPO LOCAL DESALINEADO ($LOCAL != $REMOTE) — reset duro"
  git reset --hard origin/main
  git branch -f pages origin/pages 2>/dev/null || true
else
  echo "linaje OK ($LOCAL)"
fi
python3 -c "import json;d=json.load(open('src/game/VERSION.json'));print('VERSION.json:',d['version'],'| fase',d['fase'])"
git log --oneline -1 | cut -c1-80
