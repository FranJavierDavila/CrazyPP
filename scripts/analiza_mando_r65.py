#!/usr/bin/env python3
"""r65 · Analiza Mando.glb: extrae POSITION/TEXCOORD_0, calcula clusters
espaciales y deduce las ANCLAS de cada pieza (stick, botones, gatillo, grip)
en el espacio del modelo. Además prueba compresión WebP de Pizarra.png.
"""
import json, struct, sys
import numpy as np

GLB = "/home/z/my-project/upload/_r65/Mando.glb"
data = open(GLB, "rb").read()
jlen = struct.unpack("<I", data[12:16])[0]
j = json.loads(data[20:20 + jlen])
off = 20 + jlen
blen = struct.unpack("<I", data[off:off + 4])[0]
binx = data[off + 8:off + 8 + blen]

acc = j["accessors"]
views = j["bufferViews"]
prim = j["meshes"][0]["primitives"][0]

def leer(nombre, comps):
    a = acc[prim["attributes"][nombre]]
    v = views[a["bufferView"]]
    ini = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    arr = np.frombuffer(binx, dtype=np.float32 if a["componentType"] == 5126 else np.uint16,
                        count=a["count"] * comps, offset=ini)
    return arr.reshape(-1, comps)

P = leer("POSITION", 3)
UV = leer("TEXCOORD_0", 2)
print(f"vértices: {len(P)} · bbox min {P.min(0).round(2)} max {P.max(0).round(2)}")

# nodos: transformación del nodo del mesh (Sketchfab suele escalar/rotar)
def node_xform(n):
    m = np.eye(4)
    if "matrix" in n:
        m = np.array(n["matrix"], dtype=np.float64).reshape(4, 4).T
    else:
        t = n.get("translation", [0, 0, 0])
        r = n.get("rotation", [0, 0, 0, 1])
        s = n.get("scale", [1, 1, 1])
        x, y, z, w = r
        R = np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]) * np.array(s)
        m[:3, :3] = R
        m[:3, 3] = t
    return m

# aplica la cadena de padres hasta el mesh
nodes = j["nodes"]
mesh_node = None
for i, n in enumerate(nodes):
    if "mesh" in n:
        mesh_node = i
print("nodos:", [(i, n.get("name"), "mesh" in n) for i, n in enumerate(nodes)])
M = np.eye(4)
if mesh_node is not None:
    # construye cadena hacia arriba
    padre = {}
    for i, n in enumerate(nodes):
        for c in n.get("children", []):
            padre[c] = i
    cadena = []
    cur = mesh_node
    while cur is not None:
        cadena.append(cur)
        cur = padre.get(cur)
    for ci in reversed(cadena):
        M = M @ node_xform(nodes[ci])
Ph = (M @ np.hstack([P, np.ones((len(P), 1))]).T).T[:, :3]
print(f"tras xform: bbox min {Ph.min(0).round(2)} max {Ph.max(0).round(2)}")
np.save("/tmp/mando_P.npy", Ph)
np.save("/tmp/mando_UV.npy", UV)

# clusters por rejilla en la zona alta (candidatos stick/botones)
def clusters(pts, etiqueta=""):
    pts = np.asarray(pts)
    if len(pts) == 0:
        print(f"{etiqueta}: sin puntos"); return
    print(f"{etiqueta}: {len(pts)} pts · centro {pts.mean(0).round(2)} · "
          f"min {pts.min(0).round(2)} max {pts.max(0).round(2)}")

ymax = Ph[:, 1].max()
alto, ancho, fondo = Ph[:, 1].max() - Ph[:, 1].min(), Ph[:, 0].max() - Ph[:, 0].min(), Ph[:, 2].max() - Ph[:, 2].min()
print(f"dimensiones (unidades modelo): alto Y {alto:.1f} · ancho X {ancho:.1f} · fondo Z {fondo:.1f}")

# top de la cabeza: los puntos más altos del 12%
top = Ph[Ph[:, 1] > Ph[:, 1].max() - 0.12 * alto]
# separa en clusters por X (stick vs botones)
cx = top[:, 0].mean()
clusters(izq := top[top[:, 0] < cx], etiqueta="CABEZA lado -X")
clusters(der := top[top[:, 0] >= cx], etiqueta="CABEZA lado +X")

# gatillo: protrusión frontal — busca en el tercio frontal el subconjunto
# con Z mayor
frente = Ph[Ph[:, 2] > Ph[:, 2].max() - 0.18 * fondo]
clusters(frente[frente[:, 1] > np.median(Ph[:, 1])], etiqueta="FRENTE arriba (gatillo?)")
clusters(frente[frente[:, 1] <= np.median(Ph[:, 1])], etiqueta="FRENTE abajo")

# laterales X
izq_all = Ph[Ph[:, 0] < Ph[:, 0].min() + 0.15 * ancho]
der_all = Ph[Ph[:, 0] > Ph[:, 0].max() - 0.15 * ancho]
clusters(izq_all[izq_all[:, 1] > Ph[:, 1].max() - 0.45 * alto], etiqueta="LATERAL -X alto (grip?)")
clusters(der_all[der_all[:, 1] > Ph[:, 1].max() - 0.45 * alto], etiqueta="LATERAL +X alto (grip?)")

# --- Pizarra: zona negra exacta + webp ---
from PIL import Image
im = Image.open(f"/home/z/my-project/upload/_r65/Pizarra.png").convert("RGBA")
a = np.array(im)
opaco = a[:, :, 3] > 200
oscuro = opaco & (a[:, :, :3].mean(axis=2) < 55)
ys, xs = np.where(oscuro)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print(f"PIZARRA: bbox tablero oscuro x[{x0},{x1}] y[{y0},{y1}] de {im.size}")
# rectángulo seguro (interior, con margen de 12 px respecto al marco)
print(f"PIZARRA: zona de texto segura sugerida x[{x0+28},{x1-28}] y[{y0+28},{y1-28}]")
im.save("/tmp/pizarra.webp", "WEBP", quality=88, method=6)
import os as _os
print(f"PIZARRA webp: {_os.path.getsize('/tmp/pizarra.webp')/1024:.0f} KB (png 602 KB)")
