#!/bin/bash
# CRAZY PING PONG · r26b (v3.6.122, FASE 124) — VOCES de los 3 superpoderes
# nuevos (patrón de la casa r25: espeak-ng → post ffmpeg → MP3 48 kHz mono
# 64 kbps → data-URI embebida en c12).
set -e
OUT=/home/z/my-project/upload/scripts/_r26b_assets
mkdir -p "$OUT"

post () {  # $1=wav entrada  $2=mp3 final
  ffmpeg -y -hide_banner -loglevel error -i "$1" -af \
    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11,atempo=1.04" \
    -ar 48000 -ac 1 -b:a 64k "$2"
}

gen () {   # $1=voz  $2=velocidad  $3=pitch  $4=texto  $5=salida
  espeak-ng -v "$1" -s "$2" -p "$3" -a 180 -w "$5.wav" "$4" 2>/dev/null
  post "$5.wav" "$5.mp3"
  rm -f "$5.wav"
}

echo "— Fénix…"
gen es        152 40 "¡Súper fénix!"        "$OUT/voz_fenix_es"
gen en-us     148 42 "Super phoenix!"       "$OUT/voz_fenix_en"
echo "— Crono…"
gen es        150 42 "¡Súper crono!"        "$OUT/voz_crono_es"
gen en-us     146 44 "Super chrono!"        "$OUT/voz_crono_en"
echo "— Hielo…"
gen es        148 38 "¡Súper hielo!"        "$OUT/voz_hielo_es"
gen en-us     144 40 "Super ice!"           "$OUT/voz_hielo_en"

ls -la "$OUT" | rg 'mp3'
