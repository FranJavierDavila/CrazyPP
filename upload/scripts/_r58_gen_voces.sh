#!/bin/bash
# v3.6.50 · FASE 52 (r58) — VOCES NATIVAS del SÚPER CLONACIÓN + VOZ DEL
# SELECTOR (petición del dueño: mover el joystick y que la voz diga el
# poder seleccionado, «de forma rápida solo el nombre», y «Sin poder»
# con la mano vacía). Misma receta probada de las rondas 44/46/48:
# ES = Piper es_ES-davefx-medium (LA voz castellana de la megafonía)
# EN = Piper en_US-lessac-medium + post-proceso del perfil del Quest.
set -e
BASE=/home/z/my-project
V=$BASE/scripts/voice
OUT=$BASE/scripts/_r58
PIPER=$V/piper/piper

gen_es () {  # $1=texto $2=salida_wav $3=length_scale
  echo "$1" | "$PIPER" --model "$V/models/es_ES-davefx-medium.onnx" \
    --length-scale "${3:-0.92}" --sentence-silence 0.08 --output_file "$2" 2>/dev/null
}
gen_en () {
  echo "$1" | "$PIPER" --model "$V/models/en_US-lessac-medium.onnx" \
    --length-scale "${3:-0.95}" --sentence-silence 0.08 --output_file "$2" 2>/dev/null
}

post () {  # $1=wav_entrada $2=mp3_final $3=atempo
  ffmpeg -y -hide_banner -loglevel error -i "$1" -af \
    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11,atempo=${3:-1.04}" \
    -ar 48000 -ac 1 -b:a 64k "$2"
}

mkdir -p "$OUT"

echo "— VOCES DEL SELECTOR (nombres cortos y rápidos, atempo 1.12)…"
gen_es "Super Pala"     "$OUT/sel_mega_es.wav"
gen_en "Super paddle"   "$OUT/sel_mega_en.wav"
gen_es "Super Efecto"   "$OUT/sel_efecto_es.wav"
gen_en "Super effect"   "$OUT/sel_efecto_en.wav"
gen_es "Imán"           "$OUT/sel_iman_es.wav"
gen_en "Magnet"         "$OUT/sel_iman_en.wav"
gen_es "Portal"         "$OUT/sel_portal_es.wav"
gen_en "Portal"         "$OUT/sel_portal_en.wav"
gen_es "Clonación"      "$OUT/sel_clon_es.wav"
gen_en "Cloning"        "$OUT/sel_clon_en.wav"
gen_es "Sin poder"      "$OUT/sel_nada_es.wav"
gen_en "No power"       "$OUT/sel_nada_en.wav"
for par in mega efecto iman portal clon nada; do
  post "$OUT/sel_${par}_es.wav" "$OUT/sel_${par}_es.mp3" 1.12
  post "$OUT/sel_${par}_en.wav" "$OUT/sel_${par}_en.mp3" 1.12
done

echo "— VOZ DE CONCESIÓN del SÚPER CLONACIÓN (animosa, atempo 1.04)…"
gen_es "¡Súper clonación de pala!" "$OUT/voz_clon_es.wav"
gen_en "Super clone booster!"      "$OUT/voz_clon_en.wav"
post "$OUT/voz_clon_es.wav" "$OUT/voz_clon_es.mp3" 1.04
post "$OUT/voz_clon_en.wav" "$OUT/voz_clon_en.mp3" 1.04

echo "— LIMPIEZA de wav intermedios…"
rm -f "$OUT"/*.wav

echo "— Duraciones y tamaños:"
for f in "$OUT"/*.mp3; do
  d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
  s=$(stat -c%s "$f")
  echo "  $(basename "$f"): ${d}s · ${s} B"
done
echo VOCES_R58_OK
