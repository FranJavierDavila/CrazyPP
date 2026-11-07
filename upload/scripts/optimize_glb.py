#!/usr/bin/env python3
"""Optimiza el GLB de la pala: reduce texturas a 1024px, PNG opacos -> JPEG, reconstruye GLB."""
import json, struct, io, sys
from PIL import Image

SRC = "/home/z/my-project/upload/ping_pong_paddle.glb"
DST = "/home/z/my-project/download/pingpong-quest3-v2/assets/pala.glb"
MAX_DIM = 1024
NORMAL_IMGS = {3, 7, 11, 15, 19}  # normal maps: mantener PNG (evita artefactos)

data = open(SRC, "rb").read()
jl, = struct.unpack_from("<I", data, 12)
gltf = json.loads(data[20:20+jl].decode())
bl, btype = struct.unpack_from("<II", data, 20 + jl)
bin_data = data[28 + jl: 28 + jl + bl]

def bv_bytes(idx):
    bv = gltf["bufferViews"][idx]
    off = bv.get("byteOffset", 0)
    return bin_data[off: off + bv["byteLength"]]

# --- procesar imágenes ---
new_images = {}  # idx -> (bytes, mime)
total_old = total_new = 0
for i, im in enumerate(gltf.get("images", [])):
    raw = bv_bytes(im["bufferView"])
    total_old += len(raw)
    img = Image.open(io.BytesIO(raw))
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    w, h = img.size
    if max(w, h) > MAX_DIM:
        s = MAX_DIM / max(w, h)
        img = img.resize((round(w*s), round(h*s)), Image.LANCZOS)
    out = io.BytesIO()
    if has_alpha:
        img.save(out, "PNG", optimize=True)
        mime = "image/png"
    else:
        q = 90 if i in NORMAL_IMGS else 82
        img.convert("RGB").save(out, "JPEG", quality=q, optimize=True)
        mime = "image/jpeg"
    b = out.getvalue()
    total_new += len(b)
    new_images[i] = (b, mime)
    print(f"img[{i}] {im['mimeType']} {w}x{h} {len(raw)//1024}KB -> {img.size[0]}x{img.size[1]} {len(b)//1024}KB {mime}")

print(f"texturas: {total_old/1e6:.2f}MB -> {total_new/1e6:.2f}MB")

# --- reconstruir buffer: geometría (bvs 0-3 intactos) + imágenes nuevas ---
geom_end = gltf["bufferViews"][3]["byteOffset"] + gltf["bufferViews"][3]["byteLength"]
new_bin = bytearray(bin_data[:geom_end])
for i in sorted(new_images):
    b, _ = new_images[i]
    while len(new_bin) % 4: new_bin.append(0)  # alinear a 4
    off = len(new_bin)
    new_bin += b
    bv = gltf["bufferViews"][gltf["images"][i]["bufferView"]]
    bv["byteOffset"] = off
    bv["byteLength"] = len(b)
    gltf["images"][i]["mimeType"] = new_images[i][1]
while len(new_bin) % 4: new_bin.append(0)

# --- serializar GLB ---
json_b = bytearray(json.dumps(gltf, separators=(",", ":")).encode("utf-8"))
while len(json_b) % 4: json_b.append(0x20)
bin_pad = new_bin
glb = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(json_b) + 8 + len(bin_pad))
glb += struct.pack("<II", len(json_b), 0x4E4F534A) + json_b
glb += struct.pack("<II", len(bin_pad), 0x004E4942) + bytes(bin_pad)

import os
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "wb").write(glb)
print(f"OK -> {DST}  {len(glb)/1e6:.2f}MB (original 5.02MB)")
