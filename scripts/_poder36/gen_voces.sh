#!/bin/bash
# v3.6.36 · FASE 38 — VOCES NATIVAS del Superpoder de Pala (petición del dueño:
# «la voz que anuncia el poder es horrible, no es voz nativa castellana»).
# ES = Piper es_ES-davefx-medium (LA MISMA VOZ NATIVA de la megafonía del juego)
# EN = Piper en_US-lessac-medium (el banco de voz EN del juego)
# Post-proceso = perfil PROBADO en el Quest (recorte de silencios + loudnorm +
# atempo animoso + MP3 mono 48 kHz).
set -e
BASE=/home/z/my-project
V=$BASE/scripts/voice
OUT=$BASE/scripts/_poder36
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
echo "— ES mega (davefx)…"
gen_es "¡Potenciador de pala gigante!" "$OUT/voz_mega_es.wav"
echo "— ES efecto (davefx)…"
gen_es "¡Súper efecto de pala!" "$OUT/voz_efecto_es.wav"
echo "— EN mega (lessac)…"
gen_en "Giant paddle booster!" "$OUT/voz_mega_en.wav"
echo "— EN efecto (lessac)…"
gen_en "Super spin booster!" "$OUT/voz_efecto_en.wav"

for k in mega efecto; do
  post "$OUT/voz_${k}_es.wav" "$OUT/voz_${k}_es.mp3"
  post "$OUT/voz_${k}_en.wav" "$OUT/voz_${k}_en.mp3"
done

echo "— Duraciones:"
for f in "$OUT"/voz_*_e[sn].mp3; do
  d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
  s=$(stat -c%s "$f")
  echo "  $(basename "$f"): ${d}s · ${s} B"
done
echo VOCES_OK
