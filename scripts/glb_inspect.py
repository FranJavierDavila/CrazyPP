#!/usr/bin/env python3
"""Inspecciona la estructura de un GLB: chunks, imágenes y tamaños."""
import struct, json, sys, base64

path = sys.argv[1] if len(sys.argv) > 1 else "/home/z/my-project/upload/ping_pong_paddle.glb"
data = open(path, "rb").read()
magic, version, length = struct.unpack_from("<III", data, 0)
print(f"magic={magic:#x} version={version} total={length:,} bytes file={len(data):,}")

off = 12
chunks = []
while off < len(data):
    clen, ctype = struct.unpack_from("<II", data, off)
    chunks.append((ctype, off + 8, clen))
    print(f"chunk type={ctype:#x} ({'JSON' if ctype==0x4e4f534a else 'BIN'}) len={clen:,}")
    off += 8 + clen

jtype, joff, jlen = chunks[0]
g = json.loads(data[joff:joff+jlen].decode("utf-8"))

print("\n--- images ---")
total_img = 0
for i, img in enumerate(g.get("images", [])):
    if "uri" in img and img["uri"].startswith("data:"):
        head, b64 = img["uri"].split(",", 1)
        n = len(b64) * 3 // 4
        total_img += n
        print(f"  [{i}] data URI {head.split(';')[0][5:]} ~{n:,} bytes")
    elif "uri" in img:
        print(f"  [{i}] uri={img['uri']}")
    else:
        bv = img.get("bufferView", -1)
        bvs = g.get("bufferViews", [{}])
        n = bvs[bv].get("byteLength", 0) if bv >= 0 else 0
        total_img += n
        mime = img.get("mimeType", "?")
        print(f"  [{i}] bufferView={bv} {mime} ~{n:,} bytes")
print(f"  TOTAL imágenes: {total_img:,} bytes")

print("\n--- accessors/bufferViews/meshes ---")
print(f"  accessors={len(g.get('accessors', []))} bufferViews={len(g.get('bufferViews', []))}")
print(f"  meshes={len(g.get('meshes', []))} materials={len(g.get('materials', []))}")
exts = g.get("extensionsUsed", [])
print(f"  extensions={exts}")
