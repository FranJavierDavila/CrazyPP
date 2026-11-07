#!/usr/bin/env python3
"""Auditoría de caras del GLB de la pala (v2.21).
Por cada primitiva: volumen firmado (winding) y alineación de las normales
del atributo con el winding (dot(normal_attr, normal_cara) medio).
Diagnostica el caso que fixInvertedMeshes NO cubre: winding correcto con
normales invertidas -> la pala se ve 'al revés' aun con DoubleSide.
Uso: python3 glb_face_audit.py [ruta.glb]"""
import struct, json, sys

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
assert g is not None and bin_chunk is not None, "GLB inválido"

def accessor(ai):
    a = g["accessors"][ai]
    bv = g["bufferViews"][a["bufferView"]]
    start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    comp = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}[a["componentType"]]
    n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
    return start, comp, n, a["count"]

def read_vecs(ai):
    start, comp, n, count = accessor(ai)
    sz = struct.calcsize("<" + comp)
    stride = bv_stride = g["bufferViews"][g["accessors"][ai]["bufferView"]].get("byteStride") or (sz * n)
    out = []
    for i in range(count):
        o = start + i * stride
        out.append(struct.unpack_from("<" + comp * n, bin_chunk, o))
    return out

names = g.get("nodes", [])
def node_name(ni):
    nd = names[ni] if ni < len(names) else {}
    return nd.get("name", f"node{ni}")

print(f"{'malla':28s} {'prim':4s} {'mat':12s} {'tris':>7s} {'vol':>12s} {'ndot':>7s}  veredicto")
total_bad = 0
for mi, mesh in enumerate(g.get("meshes", [])):
    for pi, prim in enumerate(mesh["primitives"]):
        pos = read_vecs(prim["attributes"]["POSITION"])
        idx = None
        if "indices" in prim:
            idx = [v[0] for v in read_vecs(prim["indices"])]
        ntri = (len(idx) if idx else len(pos)) // 3
        vol = 0.0
        ndots = []
        has_nrm = "NORMAL" in prim["attributes"]
        nrm = read_vecs(prim["attributes"]["NORMAL"]) if has_nrm else None
        for t in range(ntri):
            i0 = idx[t * 3] if idx else t * 3
            i1 = idx[t * 3 + 1] if idx else t * 3 + 1
            i2 = idx[t * 3 + 2] if idx else t * 3 + 2
            ax, ay, az = pos[i0]; bx, by, bz = pos[i1]; cx, cy, cz = pos[i2]
            e1 = (bx - ax, by - ay, bz - az)
            e2 = (cx - ax, cy - ay, cz - az)
            fn = (e1[1] * e2[2] - e1[2] * e2[1],
                  e1[2] * e2[0] - e1[0] * e2[2],
                  e1[0] * e2[1] - e1[1] * e2[0])
            vol += (ax * fn[0] + ay * fn[1] + az * fn[2]) / 6.0
            if has_nrm:
                # normal media del atributo en los 3 vértices (mundo del modelo)
                nx = sum(nrm[i][0] for i in (i0, i1, i2)) / 3
                ny = sum(nrm[i][1] for i in (i0, i1, i2)) / 3
                nz = sum(nrm[i][2] for i in (i0, i1, i2)) / 3
                ln = (nx * nx + ny * ny + nz * nz) ** 0.5
                lf = (fn[0] * fn[0] + fn[1] * fn[1] + fn[2] * fn[2]) ** 0.5
                if ln > 1e-9 and lf > 1e-9:
                    ndots.append((nx * fn[0] + ny * fn[1] + nz * fn[2]) / (ln * lf))
        mat = prim.get("material")
        mname = g["materials"][mat].get("name", f"m{mat}") if mat is not None else "-"
        nd = sum(ndots) / len(ndots) if ndots else float("nan")
        verdict = []
        if vol < -1e-10:
            verdict.append("WINDING INVERTIDO")
            total_bad += 1
        if has_nrm and ndots and nd < -0.3:
            verdict.append("NORMALES CONTRA WINDING")
            total_bad += 1
        if not verdict:
            verdict.append("ok")
        print(f"{mesh.get('name','?')[:28]:28s} {pi:<4d} {mname[:12]:12s} {ntri:7d} {vol:12.4f} {nd:7.2f}  {', '.join(verdict)}")

print(f"\nPRIMITIVAS CON PROBLEMAS: {total_bad}")
