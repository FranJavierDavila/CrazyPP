#!/usr/bin/env python3
"""v2.21 · Parchea el GLB de la pala: alphaMode BLEND -> OPAQUE.
Causa raíz del 'efecto invertido' persistente: el exportador marcó los 5
materiales como BLEND pese a que sus texturas RGB no tienen canal alfa y el
alfa base es 1. GLTFLoader (three#17706) responde con transparent=true +
depthWrite=false -> la pala se dibuja en el pase transparente SIN profundidad
y con DoubleSide se ven caras internas (efecto radiografía).
Cambiar a OPAQUE no altera ningún píxel (no hay alfa real) y restaura el pase
opaco con depthWrite correcto. El JSON se reempaqueta con padding de espacios
(4 bytes) como exige la spec GLB; el chunk BIN se copia intacto."""
import struct, json, sys

path = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/z/my-project/download/pingpong-quest3-v2/assets/pala.glb"
data = open(path, "rb").read()

off = 12
chunks = []
while off < len(data):
    clen, ctype = struct.unpack_from("<II", data, off)
    chunks.append([ctype, data[off + 8: off + 8 + clen]])
    off += 8 + clen

magic, ver, total = struct.unpack_from("<III", data, 0)
assert magic == 0x46546C67, "no es un GLB"

json_chunk = next(c[1] for c in chunks if c[0] == 0x4E4F534A)
bin_chunk = next(c[1] for c in chunks if c[0] in (0x004E4942, 0x494E4942))
g = json.loads(json_chunk.decode("utf-8"))

changed = 0
for m in g.get("materials", []):
    if m.get("alphaMode") == "BLEND":
        pbr = m.get("pbrMetallicRoughness", {})
        bcf = pbr.get("baseColorFactor", [1, 1, 1, 1])
        if len(bcf) >= 4 and bcf[3] < 1.0:
            print(f"  · {m.get('name','?')}: alfa base {bcf[3]} -> se conserva BLEND")
            continue
        m["alphaMode"] = "OPAQUE"
        changed += 1
        print(f"  · {m.get('name','?')}: BLEND -> OPAQUE")
assert changed > 0, "no había materiales BLEND que parchear"

js = json.dumps(g, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
pad = (-len(js)) % 4
js += b" " * pad                      # padding con espacios (spec GLB)

out = bytearray()
out += struct.pack("<III", magic, ver, 12 + 8 + len(js) + 8 + len(bin_chunk))
out += struct.pack("<II", len(js), 0x4E4F534A)
out += js
out += struct.pack("<II", len(bin_chunk), 0x004E4942)
out += bin_chunk
open(path, "wb").write(bytes(out))
print(f"OK · {changed} materiales parcheados · {len(data):,} -> {len(out):,} bytes")
