#!/bin/bash
# Sella la V3.0.1: zip oficial + SHA256 + RELEASE + sync a descargas web.
set -e
cd /home/z/my-project
STAGE=scripts/tmp_seal
rm -rf "$STAGE" && mkdir -p "$STAGE/assets"
cp public/game.html "$STAGE/index.html"
cp public/assets/intro.mp4 "$STAGE/assets/"
cp -r public/championships "$STAGE/"
rm -f download/crazypp-v3.zip public/descargas/crazypp-v3.zip
(cd "$STAGE" && zip -q -9 -r /home/z/my-project/download/crazypp-v3.zip index.html assets championships)
cp download/crazypp-v3.zip public/descargas/crazypp-v3.zip
# integridad
unzip -t download/crazypp-v3.zip > /dev/null && echo "ZIP íntegro"
SHA=$(sha256sum download/crazypp-v3.zip | cut -d' ' -f1)
echo "$SHA  download/crazypp-v3.zip" > download/SHA256SUMS-V3.0.txt
cp download/SHA256SUMS-V3.0.txt public/descargas/SHA256SUMS-V3.0.txt
echo "SHA256 V3.0.1: $SHA"
ls -la download/crazypp-v3.zip
