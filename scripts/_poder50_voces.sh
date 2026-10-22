#!/bin/bash
# v3.6.42 · FASE 44 — VOCES NATIVAS del SÚPER PORTAL (ronda 50).
# El dueño: «la voz del nuevo superpoder no la entiendo, no sale en castellano».
# La de r49 (2,78 s de «ES») estaba corrupta. Receta PROBADA de la casa
# (r44/r45): ES = Piper es_ES-davefx-medium · EN = Piper en_US-lessac-medium
# + post-proceso loudnorm del perfil del Quest.
set -e
BASE=/home/z/my-project
V=$BASE/scripts/voice
OUT=$BASE/scripts/_poder50
PIPER=$V/piper/piper

gen_es () {  # $1=texto $2=salida_wav
  echo "$1" | "$PIPER" --model "$V/models/es_ES-davefx-medium.onnx" \
    --length-scale 0.92 --sentence-silence 0.08 --output_file "$2" 2>/dev/null
}
gen_en () {
  echo "$1" | "$PIPER" --model "$V/models/en_US-lessac-medium.onnx" \
    --length-scale 0.95 --sentence-silence 0.08 --output_file "$2" 2>/dev/null
}

post () {  # $1=wav_entrada $2=mp3_final
  ffmpeg -y -hide_banner -loglevel error -i "$1" -af \
    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11,atempo=1.04" \
    -ar 48000 -ac 1 -b:a 64k "$2"
}

mkdir -p "$OUT"
echo "— ES portal (davefx)…"
gen_es "¡Súper portal!" "$OUT/voz_portal_es.wav"
echo "— EN portal (lessac)…"
gen_en "Super portal!" "$OUT/voz_portal_en.wav"

post "$OUT/voz_portal_es.wav" "$OUT/voz_portal_es.mp3"
post "$OUT/voz_portal_en.wav" "$OUT/voz_portal_en.mp3"

echo "— Duraciones:"
for f in "$OUT"/voz_portal_e[sn].mp3; do
  d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
  s=$(stat -c%s "$f")
  echo "  $(basename "$f"): ${d}s · ${s} B"
done
echo VOCES_PORTAL_OK
