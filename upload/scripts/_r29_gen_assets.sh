#!/bin/bash
# CRAZY PING PONG · r29 (v3.6.125, FASE 127) — ASSETS de la ronda:
#  1) ICONOS del dueño (SuperPala_Fenix / SuperPala_Cronos / SuperPala_Oscuridad)
#     cuantizados a 256 colores (patrón de la casa r25/r26b, 256×256).
#  2) VOCES de los superpoderes con LA VOZ NATIVA de siempre (informe del
#     dueño: «la voz que has usado para los superpoderes me gustaría que
#     fuese la misma que ya estábamos usando para los superpoderes
#     anteriores… una voz en castellano mucho más animosa y enérgica»):
#     receta EXACTA de r44/r45 (scripts/_poder36/gen_voces.sh) —
#     ES = Piper es_ES-davefx-medium · --length-scale 0.92 · silencio 0.08
#     EN = Piper en_US-lessac-medium · --length-scale 0.95 · silencio 0.08
#     post = silenceremove + loudnorm + atempo 1.04 → MP3 48 kHz mono 64k.
#     Regenera red/elec (r25 las dejó en espeak-ng) y fénix/crono (r26b), y
#     crea la voz del NUEVO Súper Oscuridad.
set -e
RAIZ=/home/z/my-project/upload
OUT=$RAIZ/scripts/_r29_assets
V=$RAIZ/scripts/_r29_voice
mkdir -p "$OUT"

# ── 1) ICONOS: cuantización 256 colores (mismo tratamiento que r25/r26b) ──
python3 - <<'PYEOF'
from PIL import Image
from pathlib import Path
RAIZ = Path('/home/z/my-project/upload')
OUT = RAIZ / 'scripts' / '_r29_assets'
pares = [
    ('SuperPala_Fenix.png', 'icon_fenix.png'),
    ('SuperPala_Cronos.png', 'icon_crono.png'),
    ('SuperPala_Oscuridad.png', 'icon_oscuridad.png'),
]
for src, dst in pares:
    im = Image.open(RAIZ / src).convert('RGBA')
    if im.size != (256, 256):
        im = im.resize((256, 256), Image.LANCZOS)
    q = im.quantize(colors=256, method=Image.FASTOCTREE, dither=Image.FLOYDSTEINBERG)
    q.save(OUT / dst, optimize=True)
    print(f'{dst}: {(OUT / dst).stat().st_size} B')
PYEOF

# ── 2) VOCES: Piper davefx/lessac + post del Quest ──
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

gen "¡Súper fénix!"        es "$OUT/voz_fenix_es"
gen "Super phoenix!"       en "$OUT/voz_fenix_en"
gen "¡Súper crono!"        es "$OUT/voz_crono_es"
gen "Super chrono!"        en "$OUT/voz_crono_en"
gen "¡Súper oscuridad!"    es "$OUT/voz_oscuridad_es"
gen "Super darkness!"      en "$OUT/voz_oscuridad_en"
gen "¡Súper red!"          es "$OUT/voz_red_es"
gen "Super net!"           en "$OUT/voz_red_en"
gen "¡Súper electricidad!" es "$OUT/voz_elec_es"
gen "Super electricity!"   en "$OUT/voz_elec_en"

echo "— Duraciones:"
for f in "$OUT"/voz_*.mp3; do
  d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
  s=$(stat -c%s "$f")
  echo "  $(basename "$f"): ${d}s · ${s} B"
done
echo R29_ASSETS_OK
