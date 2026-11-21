#!/bin/bash
# r109 · VOCES DE SUPER CRIPTONITA (petición del dueño: «el Superpoder de
# criptonita le falta el audio tanto en el juego como en la sala Arcano;
# en ambos lugares debe estar en castellano e inglés y con la entonación
# propia de cada lugar»).
# Receta PROBADA de la casa (r44/r45/r50): Piper es_ES-davefx-medium (ES) ·
# en_US-lessac-medium (EN) + post loudnorm del perfil del Quest → mp3
# 48 kHz mono 64k (el MISMO perfil embebido de las voces de concesión).
# La entonación propia de cada lugar ya vive en la arquitectura de la casa:
#   · JUEGO  — la voz ágil del selector (r58) y la de concesión (_megaVoz).
#   · ARCANO — la voz SOLEMNE del oráculo (r47: cinta lenta ×0,82 +
#     paso-bajo 2,8 kHz + sala ceremonial) sobre el MISMO banco.
# Dos ficheros, cero duplicados.
set -e
BASE=/home/z/my-project
PIPER=$BASE/scripts/voice/piper/piper
MES=$BASE/scripts/voice/models/es_ES-davefx-medium.onnx
MEN=$BASE/scripts/voice/models/en_US-lessac-medium.onnx
OUT=$BASE/scripts/r109_voces
mkdir -p "$OUT"

gen () { # $1=modelo $2=length_scale $3=sentence_silence $4=texto $5=salida_wav
  echo "$4" | "$PIPER" --model "$1" --length-scale "$2" \
    --sentence-silence "$3" --output_file "$5" 2>/dev/null
}

post () { # $1=wav_entrada $2=mp3_final
  ffmpeg -y -hide_banner -loglevel error -i "$1" -af \
    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11,atempo=1.04" \
    -ar 48000 -ac 1 -b:a 64k "$2"
}

echo "— ES (davefx)…"
gen "$MES" 0.92 0.08 "¡Súper criptonita!" "$OUT/voz_cripto_es.wav"
post "$OUT/voz_cripto_es.wav" "$OUT/voz_cripto_es.mp3"

echo "— EN (lessac)…"
gen "$MEN" 0.95 0.08 "Super cryptonite!" "$OUT/voz_cripto_en.wav"
post "$OUT/voz_cripto_en.wav" "$OUT/voz_cripto_en.mp3"

rm -f "$OUT"/voz_cripto_es.wav "$OUT"/voz_cripto_en.wav

echo
echo "— Verificación (fichero · Hz/canales · duración s · bytes):"
for f in "$OUT"/voz_cripto_*.mp3; do
  SR=$(ffprobe -v error -show_entries stream=sample_rate -of csv=p=0 "$f")
  CH=$(ffprobe -v error -show_entries stream=channels -of csv=p=0 "$f")
  DU=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  SZ=$(stat -c %s "$f")
  echo "$(basename "$f") · ${SR} Hz/${CH}ch · ${DU}s · ${SZ} B"
done
