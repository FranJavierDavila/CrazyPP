#!/usr/bin/env python3
"""Repara el tipo de chunk BIN de un GLB (glb_shrink.py escribió 0x494E4942
"BINI" en lugar de 0x004E4942 "BIN\\0") y valida el archivo completo:
chunks, límites de bufferViews/accessors y mimeType real de cada imagen.
Uso: python3 glb_repair.py archivo.glb [--write]"""
import struct, json, sys

path = sys.argv[1]
WRITE = "--write" in sys.argv

data = bytearray(open(path, "rb").read())
magic, ver, total = struct.unpack_from("<III", data, 0)
assert magic == 0x46546C67, "no es un GLB"
assert len(data) == total, f"tamaño declarado {total} != real {len(data)}"

off = 12
json_chunk = None
bin_hdr_off = None
bin_chunk = None
while off < len(data):
    clen, ctype = struct.unpack_from("<II", data, off)
    if ctype == 0x4E4F534A:
        json_chunk = data[off + 8: off + 8 + clen]
    elif ctype in (0x004E4942, 0x494E4942):
        bin_hdr_off = off + 4          # posición de los 4 bytes del tipo
        bin_chunk = bytes(data[off + 8: off + 8 + clen])
        if ctype == 0x494E4942 and WRITE:
            print(f"CHUNK BIN con tipo inválido 0x494E4942 en offset {off + 4}: parcheando a 0x004E4942")
            struct.pack_into("<I", data, off + 4, 0x004E4942)
    else:
        print(f"⚠️ chunk desconocido type={ctype:#x} len={clen}")
    off += 8 + clen

g = json.loads(json_chunk.decode("utf-8"))
n_views = len(g.get("bufferViews", []))
buf_len = len(bin_chunk)

print(f"GLB: {len(data):,} bytes · bufferViews={n_views} · chunk BIN={buf_len:,}")
errors = []
fixed = {}

# --- buffers[0].byteLength debe cubrir el chunk BIN ---
if g.get("buffers") and g["buffers"][0].get("byteLength") != buf_len:
    old = g["buffers"][0].get("byteLength")
    g["buffers"][0]["byteLength"] = buf_len
    fixed["buffers[0].byteLength"] = f"{old:,} -> {buf_len:,}"

# --- todo bufferView NECESITA "buffer": 0 (glTF 2.0) — glb_shrink.py lo perdía ---
for i, bv in enumerate(g.get("bufferViews", [])):
    if "buffer" not in bv:
        bv["buffer"] = 0
        fixed[f"bufferView[{i}].buffer"] = "añadido (obligatorio en glTF 2.0)"

# --- imágenes: firma real vs mimeType declarado (corregir al escribir) ---
for i, img in enumerate(g.get("images", [])):
    bv = img.get("bufferView")
    if bv is None:
        continue
    view = g["bufferViews"][bv]
    raw = bin_chunk[view["byteOffset"]: view["byteOffset"] + view["byteLength"]]
    real = "image/jpeg" if raw[:3] == b"\xff\xd8\xff" else (
        "image/png" if raw[:4] == b"\x89PNG" else "DESCONOCIDO")
    decl = img.get("mimeType", "?")
    if real == "DESCONOCIDO":
        errors.append(f"imagen[{i}]: bytes no son ni PNG ni JPEG")
        continue
    if real != decl:
        if WRITE:
            fixed[f"img[{i}].mimeType"] = f"{decl} -> {real}"
            img["mimeType"] = real
            decl = real
        else:
            errors.append(f"imagen[{i}]: mimeType declarado {decl} pero bytes son {real}")
    print(f"  img[{i:2}] {decl:11} ({len(raw):,} B)")
for i, bv in enumerate(g.get("bufferViews", [])):
    bo, bl = bv.get("byteOffset", 0), bv.get("byteLength", 0)
    if bo + bl > buf_len:
        errors.append(f"bufferView[{i}] se sale del chunk BIN ({bo}+{bl} > {buf_len})")

# --- accessors dentro de sus bufferViews ---
for i, ac in enumerate(g.get("accessors", [])):
    bv = ac.get("bufferView")
    if bv is None:
        continue
    view = g["bufferViews"][bv]
    comp = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}[ac["componentType"]]
    ncomp = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[ac["type"]]
    need = ac["count"] * ncomp * comp
    stride = view.get("byteStride") or ncomp * comp
    span = (ac.get("byteOffset", 0) + (ac["count"] - 1) * stride + ncomp * comp) if ac["count"] else 0
    if span > view.get("byteLength", 0):
        errors.append(f"accessor[{i}] necesita {span} > bufferView[{bv}]={view.get('byteLength')}")

# --- imágenes: firma real vs mimeType declarado ---
for i, img in enumerate(g.get("images", [])):
    bv = img.get("bufferView")
    if bv is None:
        continue
    view = g["bufferViews"][bv]
    raw = bin_chunk[view["byteOffset"]: view["byteOffset"] + view["byteLength"]]
    real = "image/jpeg" if raw[:3] == b"\xff\xd8\xff" else (
        "image/png" if raw[:4] == b"\x89PNG" else "DESCONOCIDO")
    decl = img.get("mimeType", "?")
    ok = "✓" if real == decl else "⚠️"
    if real != decl:
        errors.append(f"imagen[{i}]: mimeType declarado {decl} pero bytes son {real}")
    print(f"  img[{i:2}] {decl:11} bytes={real:11} {ok} ({len(raw):,} B)")

# --- mallas/primitivas referencian accessors válidos ---
n_acc = len(g.get("accessors", []))
for m in g.get("meshes", []):
    for p in m.get("primitives", []):
        for k, idx in p.get("attributes", {}).items():
            if idx >= n_acc:
                errors.append(f"mesh '{m.get('name')}' atributo {k} -> accessor {idx} inexistente")
        if p.get("indices", -1) >= n_acc:
            errors.append(f"mesh '{m.get('name')}' índices -> accessor inexistente")

if errors:
    print("\n❌ ERRORES:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

# --- reescribir el GLB si hubo parches en el JSON ---
if WRITE and fixed:
    json_bytes = json.dumps(g, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((-len(json_bytes)) % 4)
    out = bytearray()
    total = 12 + 8 + len(json_bytes) + 8 + len(bin_chunk)
    out += struct.pack("<III", 0x46546C67, 2, total)
    out += struct.pack("<II", len(json_bytes), 0x4E4F534A)
    out += json_bytes
    out += struct.pack("<II", len(bin_chunk), 0x004E4942)
    out += bin_chunk
    open(path, "wb").write(bytes(out))
    print(f"\n🔧 Parches aplicados:")
    for k, v in fixed.items():
        print(f"  - {k}")
    print(f"✅ GLB válido y reparado -> {path} ({len(data):,} bytes)")
elif WRITE:
    print(f"\n✅ GLB válido y reparado (solo chunk BIN) -> {path} ({len(data):,} bytes)")
else:
    print("\n✅ GLB válido (solo lectura; usa --write para parchear)")
