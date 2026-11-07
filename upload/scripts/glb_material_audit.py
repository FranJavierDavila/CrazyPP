#!/usr/bin/env python3
"""Auditoría de MATERIALES y TEXTURAS del GLB (alphaMode, alfa real de cada PNG).
Hipótesis v2.21: el 'efecto invertido' persistente son píxeles descartados por
alphaTest / transparencia de la textura, no el winding (que ya auditamos OK)."""
import struct, json, sys, io, zlib

path = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/z/my-project/download/pingpong-quest3-v2/assets/pala.glb"
data = open(path, "rb").read()
off = 12
g = bin_chunk = None
while off < len(data):
    clen, ctype = struct.unpack_from("<II", data, off)
    body = data[off + 8: off + 8 + clen]
    if ctype == 0x4E4F534A:
        g = json.loads(body.decode("utf-8"))
    elif ctype in (0x004E4942, 0x494E4942):
        bin_chunk = body
    off += 8 + clen

def png_alpha_stats(raw):
    """Devuelve (ancho, alto, %píxeles con alfa<0.5, alfa mínima) de un PNG."""
    try:
        img = raw
        assert img[:8] == b"\x89PNG\r\n\x1a\n"
        pos = 8
        w = h = bitd = ctype_ = None
        idat = b""
        while pos < len(img):
            ln, typ = struct.unpack_from(">I4s", img, pos)
            chunk = img[pos + 8: pos + 8 + ln]
            if typ == b"IHDR":
                w, h, bitd, ctype_ = struct.unpack_from(">IIBB", chunk)
            elif typ == b"IDAT":
                idat += chunk
            pos += 12 + ln
        if ctype_ not in (6, 4):
            return (w, h, None, None, ctype_)  # sin canal alfa (RGB/L)
        ch = 4 if ctype_ == 6 else 2
        rawd = zlib.decompress(idat)
        stride = w * ch
        # desfiltrar
        out = bytearray()
        prev = bytearray(stride)
        p = 0
        for y in range(h):
            f = rawd[p]; p += 1
            line = bytearray(rawd[p:p + stride]); p += stride
            if f == 1:
                for i in range(ch, stride):
                    line[i] = (line[i] + line[i - ch]) & 0xFF
            elif f == 2:
                for i in range(stride):
                    line[i] = (line[i] + prev[i]) & 0xFF
            elif f == 3:
                for i in range(stride):
                    a = line[i - ch] if i >= ch else 0
                    line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
            elif f == 4:
                for i in range(stride):
                    a = line[i - ch] if i >= ch else 0
                    b = prev[i]
                    c = prev[i - ch] if i >= ch else 0
                    pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                    pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                    line[i] = (line[i] + pr) & 0xFF
            out += line
            prev = line
        aidx = ch - 1
        total = w * h
        half = sum(1 for i in range(total) if out[i * ch + aidx] < 128)
        amin = min(out[i * ch + aidx] for i in range(total))
        amax = max(out[i * ch + aidx] for i in range(total))
        return (w, h, 100.0 * half / total, (amin, amax), ctype_)
    except Exception as e:
        return None

print("--- materiales ---")
for mi, m in enumerate(g.get("materials", [])):
    pbr = m.get("pbrMetallicRoughness", {})
    print(f"[{mi}] {m.get('name','?'):12s} alphaMode={m.get('alphaMode','OPAQUE'):8s} "
          f"alphaCutoff={m.get('alphaCutoff','-')} doubleSided={m.get('doubleSided')} "
          f"baseColorFactor={pbr.get('baseColorFactor')} metal={pbr.get('metallicFactor')} "
          f"rough={pbr.get('roughnessFactor')} tex={'sí' if 'baseColorTexture' in pbr else 'no'} "
          f"ext={list(m.get('extensions', {}).keys())}")

print("\n--- texturas (alfa real) ---")
for ii, img in enumerate(g.get("images", [])):
    bv = g["bufferViews"][img["bufferView"]]
    raw = bin_chunk[bv.get("byteOffset", 0): bv.get("byteOffset", 0) + bv["byteLength"]]
    mime = img.get("mimeType", "?")
    st = png_alpha_stats(raw) if mime == "image/png" else None
    if st and st[2] is not None:
        w, h, pct, rng, ct = st
        print(f"[{ii}] {img.get('name','?'):20s} {w}x{h} tipoColor={ct} "
              f"alfa<50%: {pct:.1f}% de los píxeles, rango alfa={rng}")
    elif st:
        w, h, _, _, ct = st
        print(f"[{ii}] {img.get('name','?'):20s} {w}x{h} tipoColor={ct} SIN canal alfa "
              f"({len(raw):,} bytes)")
    else:
        print(f"[{ii}] {img.get('name','?'):20s} {mime} {len(raw):,} bytes (sin análisis de alfa)")

print("\n--- texturas referenciadas por material (sampler) ---")
for mi, m in enumerate(g.get("materials", [])):
    pbr = m.get("pbrMetallicRoughness", {})
    ti = pbr.get("baseColorTexture", {}).get("index")
    if ti is not None:
        src = g["textures"][ti].get("source")
        print(f"[{mi}] {m.get('name','?'):12s} -> imagen {src}")
