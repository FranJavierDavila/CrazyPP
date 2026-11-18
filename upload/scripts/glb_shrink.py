#!/usr/bin/env python3
"""Reoptimiza un GLB reescalando sus texturas embebidas (bufferView) y
reconstruyendo el chunk BIN. La geometría se copia byte a byte.
Uso: python3 glb_shrink.py entrada.glb salida.glb [max_dim]"""
import struct, json, sys, io

src, dst = sys.argv[1], sys.argv[2]
MAX_DIM = int(sys.argv[3]) if len(sys.argv) > 3 else 700

from PIL import Image

data = open(src, "rb").read()
magic, version, _ = struct.unpack_from("<III", data, 0)
assert magic == 0x46546c67, "no es un GLB"

off = 12
chunks = {}
while off < len(data):
    clen, ctype = struct.unpack_from("<II", data, off)
    chunks[ctype] = data[off + 8: off + 8 + clen]
    off += 8 + clen

g = json.loads(chunks[0x4E4F534A].decode("utf-8"))
bin_chunk = chunks[0x004E4942]

img_views = {img["bufferView"] for img in g.get("images", []) if "bufferView" in img}
old_views = g.get("bufferViews", [])

new_bin = bytearray()
new_views = []
report = []
for i, bv in enumerate(old_views):
    boff, blen = bv.get("byteOffset", 0), bv.get("byteLength", 0)
    raw = bin_chunk[boff: boff + blen]
    if i in img_views:
        try:
            im = Image.open(io.BytesIO(raw))
            w, h = im.size
            m = max(w, h)
            if m > MAX_DIM:
                sc = MAX_DIM / m
                im = im.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS)
            out = io.BytesIO()
            if im.format == "JPEG" or (bv.get("mimeType") == "image/jpeg"):
                im.convert("RGB").save(out, "JPEG", quality=82, optimize=True)
            else:
                im.save(out, "PNG", optimize=True)
            raw = out.getvalue()
            report.append((i, f"{w}x{h} -> {im.size[0]}x{im.size[1]}  {blen:,} -> {len(raw):,} bytes"))
        except Exception as e:
            report.append((i, f"SIN CAMBIOS ({e})"))
    pad = (-len(new_bin)) % 4
    new_bin += b"\x00" * pad
    nv = {"buffer": bv.get("buffer", 0), "byteOffset": len(new_bin), "byteLength": len(raw)}
    if "byteStride" in bv and i not in img_views:
        nv["byteStride"] = bv["byteStride"]
    if "name" in bv:
        nv["name"] = bv["name"]
    new_bin += raw
    new_views.append(nv)

g["bufferViews"] = new_views
if "buffers" in g and g["buffers"]:
    g["buffers"][0]["byteLength"] = len(new_bin)

json_bytes = json.dumps(g, separators=(",", ":")).encode("utf-8")
json_pad = (-len(json_bytes)) % 4
json_bytes += b" " * json_pad
bin_pad = (-len(new_bin)) % 4
new_bin += b"\x00" * bin_pad

total = 12 + 8 + len(json_bytes) + 8 + len(new_bin)
out = bytearray()
out += struct.pack("<III", 0x46546c67, 2, total)
out += struct.pack("<II", len(json_bytes), 0x4E4F534A)
out += json_bytes
out += struct.pack("<II", len(new_bin), 0x004E4942)  # "BIN\0" — ¡el tipo de chunk BIN del spec glTF!
out += new_bin
open(dst, "wb").write(bytes(out))

for i, r in report:
    print(f"  view[{i:2}] {r}")
print(f"\nOK: {src} ({len(data):,}) -> {dst} ({len(bytes(out)):,} bytes)")
