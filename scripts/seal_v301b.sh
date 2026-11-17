#!/bin/bash
# Re-sella la V3.0.1 (build con sello de versión en pantalla):
# zip oficial crazypp-v3.zip + espejo crazypp-v3.0.1.zip + SHA256SUMS (2 líneas).
set -e
cd /home/z/my-project
STAGE=scripts/tmp_seal
rm -rf "$STAGE" && mkdir -p "$STAGE/assets"
cp public/game.html "$STAGE/index.html"
cp public/assets/intro.mp4 "$STAGE/assets/"
cp -r public/championships "$STAGE/"
rm -f download/crazypp-v3.zip public/descargas/crazypp-v3.zip \
      download/crazypp-v3.0.1.zip public/descargas/crazypp-v3.0.1.zip
(cd "$STAGE" && zip -q -9 -r /home/z/my-project/download/crazypp-v3.zip index.html assets championships)
cp download/crazypp-v3.zip download/crazypp-v3.0.1.zip
cp download/crazypp-v3.zip public/descargas/crazypp-v3.zip
cp download/crazypp-v3.zip public/descargas/crazypp-v3.0.1.zip
# integridad
unzip -t download/crazypp-v3.zip > /dev/null && echo "ZIP íntegro"
SHA=$(sha256sum download/crazypp-v3.zip | cut -d' ' -f1)
printf '%s  crazypp-v3.zip\n%s  crazypp-v3.0.1.zip\n' "$SHA" "$SHA" > download/SHA256SUMS-V3.0.txt
cp download/SHA256SUMS-V3.0.txt public/descargas/SHA256SUMS-V3.0.txt
# verificación sha256sum -c desde la carpeta
(cd download && sha256sum -c SHA256SUMS-V3.0.txt)
# versión dentro del zip
unzip -p download/crazypp-v3.zip index.html | grep -o "VERSION = '[0-9.]*'" | head -1
unzip -p download/crazypp-v3.zip index.html | grep -c "verBadge" || true
echo "SHA256 V3.0.1 (build con sello): $SHA"
stat -c '%n %s' download/crazypp-v3.zip download/crazypp-v3.0.1.zip
