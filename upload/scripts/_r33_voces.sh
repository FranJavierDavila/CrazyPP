#!/bin/bash
# CRAZY PING PONG · r33 (v3.6.129, FASE 131) — VOCES de los 4 superpoderes
# nuevos (Prisma · Onda de Choque · Salvavidas · Ancla). Receta EXACTA de
# la casa r29 (scripts/_r29_gen_assets.sh): ES = Piper es_ES-davefx-medium
# · --length-scale 0.92 · silencio 0.08 · EN = Piper en_US-lessac-medium ·
# --length-scale 0.95 · post = silenceremove + loudnorm + atempo 1.04 →
# MP3 48 kHz mono 64 kbps.
set -e
RAIZ=/home/z/my-project/upload
OUT=$RAIZ/scripts/_r33_assets
V=$RAIZ/scripts/_r29_voice
mkdir -p "$OUT"

PIPER=$V/piper/piper
MES=$V/modelos/davefx.onnx
MEN=$V/modelos/en_US-lessac-medium.onnx

gen_es () {  # $1=texto  $2=salida_wav
  echo "$1" | "$PIPER" --model "$MES" --length-scale 0.92 --sentence-silence 0.08 --output_file "$2" 2>/dev/null
}
gen_en () {
  echo "$1" | "$PIPER" --model "$MEN" --length-scale 0.95 --sentence-silence 0.08 --output_file "$2" 2>/dev/null
}
post () {  # $1=wav  $2=mp3
  ffmpeg -y -hide_banner -loglevel error -i "$1" -af \
    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11,atempo=1.04" \
    -ar 48000 -ac 1 -b:a 64k "$2"
}
gen () {  # $1=texto $2=lang $3=salida
  if [ "$2" = es ]; then gen_es "$1" "$3.wav"; else gen_en "$1" "$3.wav"; fi
  post "$3.wav" "$3.mp3"
  rm -f "$3.wav"
}

echo "— Prisma…"
gen "¡Súper prisma!"     es "$OUT/voz_prisma_es"
gen "Super prism!"       en "$OUT/voz_prisma_en"
echo "— Onda de choque…"
gen "¡Onda de choque!"   es "$OUT/voz_onda_es"
gen "Shockwave!"         en "$OUT/voz_onda_en"
echo "— Salvavidas…"
gen "¡Súper salvavidas!" es "$OUT/voz_salva_es"
gen "Life saver!"        en "$OUT/voz_salva_en"
echo "— Ancla…"
gen "¡Súper ancla!"      es "$OUT/voz_ancla_es"
gen "Super anchor!"      en "$OUT/voz_ancla_en"

ls -la "$OUT" | grep mp3
