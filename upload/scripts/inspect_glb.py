#!/usr/bin/env python3
"""Inspecciona un GLB: estructura JSON, tamaños, texturas y orientación de la geometría."""
import json, struct, sys, base64

path = sys.argv[1] if len(sys.argv) > 1 else "/home/z/my-project/upload/ping_pong_paddle.glb"
with open(path, "rb") as f:
    data = f.read()

magic, version, length = struct.unpack_from("<III", data, 0)
print(f"magic={magic:#x} version={version} total={length/1e6:.2f}MB file={len(data)/1e6:.2f}MB")

off = 12
json_len, json_type = struct.unpack_from("<II", data, off)
joff = off + 8
gltf = json.loads(data[joff:joff+json_len].decode("utf-8"))
bin_off = joff + json_len
bin_len, bin_type = struct.unpack_from("<II", data, bin_off)
bin_data = data[bin_off+8: bin_off+8+bin_len]
print(f"JSON chunk={json_len/1e6:.2f}MB BIN chunk={bin_len/1e6:.2f}MB")

print("\n--- asset ---"); print(json.dumps(gltf.get("asset", {}), indent=1)[:300])
print("\n--- meshes ---")
for i, m in enumerate(gltf.get("meshes", [])):
    print(f"[{i}] name={m.get('name')!r} prims={len(m.get('primitives', []))}")
print("\n--- nodes ---")
for i, n in enumerate(gltf.get("nodes", [])):
    print(f"[{i}] name={n.get('name')!r} mesh={n.get('mesh')} rot={n.get('rotation')} scale={n.get('scale')} trans={n.get('translation')}")
print("\n--- scenes ---"); print(json.dumps(gltf.get("scenes", [])))
print("\n--- materials ---")
for i, m in enumerate(gltf.get("materials", [])):
    pbr = m.get("pbrMetallicRoughness", {})
    print(f"[{i}] name={m.get('name')!r} baseColorTex={pbr.get('baseColorTexture')} baseColorFactor={pbr.get('baseColorFactor')} metallic={pbr.get('metallicFactor')} rough={pbr.get('roughnessFactor')}")
print("\n--- textures/images ---")
for i, im in enumerate(gltf.get("images", [])):
    bv = im.get("bufferView")
    size = 0
    mime = im.get("mimeType")
    name = im.get("name", "")
    if bv is not None:
        bvd = gltf["bufferViews"][bv]
        size = bvd.get("byteLength", 0)
    print(f"[{i}] name={name!r} mime={mime} bufferView={bv} size={size/1e6:.2f}MB")
print("\n--- accessors (POSITION) ---")
for i, a in enumerate(gltf.get("accessors", [])):
    if a.get("type") == "VEC3" and a.get("componentType") == 5126:
        mn = a.get("min"); mx = a.get("max")
        if mn and mx:
            print(f"[{i}] count={a.get('count')} min={[round(v,4) for v in mn]} max={[round(v,4) for v in mx]}")
