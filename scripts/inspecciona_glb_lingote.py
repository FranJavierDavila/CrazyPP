#!/usr/bin/env python3
"""Inspecciona lowpoly_gold_bar.glb: bbox real (accessors POSITION de las
mallas), orientación del eje largo y contenido JSON. Sirve para calibrar el
apilado de lingotes sobre los cajones del oro (petición del dueño: que no se
metan unos dentro de otros)."""
import json
import struct
import sys

GLB = "/home/z/my-project/public/championships/oeste/assets/lowpoly_gold_bar.glb"


def main():
    with open(GLB, "rb") as f:
        data = f.read()
    magic, ver, total = struct.unpack_from("<III", data, 0)
    print(f"magic={magic:#x} version={ver} bytes={total} (fichero {len(data)})")
    off = 12
    js = None
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunk = data[off + 8: off + 8 + clen]
        if ctype == 0x4E4F534A:  # 'JSON'
            js = json.loads(chunk.decode("utf-8"))
        off += 4 + clen
    if js is None:
        print("SIN chunk JSON"); sys.exit(1)

    accs = js.get("accessors", [])
    meshes = js.get("meshes", [])
    nodes = js.get("nodes", [])
    print(f"nodos={len(nodes)} mallas={len(meshes)} accessors={len(accs)}")

    # bbox global en espacio modelo (sin transformadas de nodo raras: las
    # listamos; si hay escaladas las apuntamos aparte)
    gmin = [1e9] * 3
    gmax = [-1e9] * 3
    for mi, m in enumerate(meshes):
        for prim in m.get("primitives", []):
            pa = prim.get("attributes", {}).get("POSITION")
            if pa is None:
                continue
            a = accs[pa]
            mn, mx = a.get("min"), a.get("max")
            if not mn or not mx:
                continue
            for k in range(3):
                gmin[k] = min(gmin[k], mn[k])
                gmax[k] = max(gmax[k], mx[k])
            print(f"  malla[{mi}] '{m.get('name','')}' POS min={mn} max={mx}")
    if gmax[0] < 1e8:
        sz = [gmax[k] - gmin[k] for k in range(3)]
        print(f"BBOX modelo: min={gmin} max={gmax}")
        print(f"TAMAÑO  x={sz[0]:.4f}  y={sz[1]:.4f}  z={sz[2]:.4f}")
        eje = "x" if sz[0] >= sz[1] and sz[0] >= sz[2] else ("y" if sz[1] >= sz[2] else "z")
        print(f"EJE LARGO: {eje}")
    for ni, n in enumerate(nodes[:12]):
        keys = {k: n[k] for k in ("name", "translation", "rotation", "scale") if k in n}
        print(f"  nodo[{ni}] {keys}")

    # ¿Qué cara del trapecio es la ANCHA? (para tumbar la barra con la base
    # ancha hacia abajo) — muestrea el ancho X en los extremos de Z.
    bufs = js.get("buffers", [])
    bufvs = js.get("bufferViews", [])
    for mi, m in enumerate(meshes):
        for prim in m.get("primitives", []):
            pa = prim.get("attributes", {}).get("POSITION")
            if pa is None:
                continue
            a = accs[pa]
            ct = a.get("componentType")
            norm = a.get("normalized", False)
            bv = bufvs[a["bufferView"]]
            boff = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
            bin_chunk = None
            off = 12
            while off < len(data):
                clen, ctype = struct.unpack_from("<II", data, off)
                if ctype == 0x004E4942:  # 'BIN\0'
                    bin_chunk = data[off + 8: off + 8 + clen]
                off += 8 + clen
            if bin_chunk is None:
                print("  sin chunk BIN"); continue
            n = a["count"]
            import array as _arr
            if ct == 5126:      # FLOAT
                arr = _arr.array("f")
                arr.frombytes(bin_chunk[boff:boff + n * 12])
            elif ct == 5123:    # USHORT
                arr = _arr.array("H")
                arr.frombytes(bin_chunk[boff:boff + n * 6])
                if norm:
                    arr = [v / 65535.0 for v in arr]
                else:
                    arr = [float(v) for v in arr]
            else:
                print(f"  componentType {ct} no soportado"); continue
            zs = arr[2::3]
            xs = arr[0::3]
            zmin, zmax = min(zs), max(zs)
            band = (zmax - zmin) * 0.08
            lo = [x for x, z in zip(xs, zs) if z <= zmin + band]
            hi = [x for x, z in zip(xs, zs) if z >= zmax - band]
            print(f"  TRAPECIO: ancho X en z MIN={max(lo)-min(lo):.3f} · "
                  f"en z MAX={max(hi)-min(hi):.3f}  (z {zmin:.2f}…{zmax:.2f})")
            print(f"  → cara ANCHA en z {'MIN' if (max(lo)-min(lo)) > (max(hi)-min(hi)) else 'MAX'}")


if __name__ == "__main__":
    main()
