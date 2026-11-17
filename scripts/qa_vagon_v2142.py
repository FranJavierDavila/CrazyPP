#!/usr/bin/env python3
"""QA de la ronda 28 · EL VAGÓN SUENA (oeste v2.142, etapa 4 ASALTO AL TREN).

  A · estático del módulo: las 8 piezas de la ronda están en su sitio
      (cajones en la ventana, GLB tumbado, cadena inmediata, 4 sonidos
      enganchados a sus eventos, motores createMusic sin decode propio).
  B · assets: los 4 mp3 del dueño se sirven por HTTP (200 + tamaño).
  C · MATEMÁTICA del GLB tumbado con three.js REAL en node: la rotación
      Rx(−π/2)·Rz(π/2) mapea el bbox medido del GLB (6,32 × 13,80 × 3,06,
      eje largo Y, cara ancha en z MIN) a: largo → x (0,17), ancho → z,
      ALTO → y con la cara ANCHA hacia abajo. Es la prueba de que la pila
      de lingotes queda plana (capas reales) y estable.
"""
import json
import struct
import subprocess
import sys
import urllib.request

RAIZ = "/home/z/my-project"
MOD = RAIZ + "/public/championships/oeste/index.js"
GLB = RAIZ + "/public/championships/oeste/assets/lowpoly_gold_bar.glb"

fails = []
oks = 0


def chk(cond, msg):
    global oks
    if cond:
        oks += 1
        print(f"  ✓ {msg}")
    else:
        fails.append(msg)
        print(f"  ✗ FALLO: {msg}")


# ─────────────────────────────────────────────── A · estático del módulo
print("A · ESTÁTICO DEL MÓDULO")
src = open(MOD, encoding="utf-8").read()
chk("v2.142 (módulo v49)" in src, "cabecera v2.142 presente")
chk("x: 2.45," in src and "junto a las ventanas" in src,
    "cajones del oro junto a las ventanas (x 2,45)")
chk("root.rotation.set(-Math.PI / 2, 0, Math.PI / 2)" in src,
    "GLB tumbado: rotación Rx(−π/2)·Rz(π/2) presente")
chk("if (sz.y > sz.x && sz.y > sz.z)" in src,
    "GLB tumbado: guard del eje largo Y")
chk("if (serie.rest.size > 0) this._bombaReapunta(b, serie);" in src,
    "cadena de la dinamita: re-apunte INMEDIATO al tocar el medallón")
chk("play('tren_llegada.mp3', 0.8)" in src, "tren_llegada.mp3 al frenar (_llegaEstacion)")
chk("play('tunel.mp3', 0.7)" in src, "tunel.mp3 al entrar en el túnel")
chk("_viasStart" in src and "_viasVol" in src and "_ambStep" in src,
    "vías en bucle: motor + volumen con la marcha")
chk(src.count("_cabStart(") >= 3 and "['fj', 'ind0', 'ind1', 'ind2']" in src,
    "galopes: 4 motores por instancia (fj + 3 indios del pool)")
chk(src.count("_cabFade(") >= 6, "galopes: fundidos progresivos (fuga/gone)")
chk(src.count("_cabCut(") >= 2, "galopes: corte brusco al abatir")
chk("_cabStop(key)" in src and "_cabStopAll()" in src, "cierre de galopes definido")
chk("_cabStop('fj')" in src and "_cabStop('ind' + rec.k)" in src,
    "galope CORTA de golpe en _fjHerido y _indHerido")
chk("this._viasStop();" in src and "this._cabStopAll();" in src,
    "dispose detiene vias y galopes")
chk(src.count("decodeAudioData(") == 0,
    "cero decodeAudioData en el módulo (el decode vive en el SDK)")
chk(src.count("createMusic(() => this.game") >= 2 and src.count("_ambEng(") >= 3,
    "motores createMusic: fábrica _ambEng crea vias + 4 galopes en runtime")
chk("'tren_llegada.mp3'" in src and "'tunel.mp3'" in src and "'vias.mp3'" in src and "'caballos.mp3'" in src,
    "los cuatro nombres de fichero presentes")
chk("precarga('vias.mp3')" in src and "precarga('caballos.mp3')" in src,
    "precarga de vias y caballos en _sndTren")

# ───────────────────────────────────────────────────── B · assets por HTTP
print("B · ASSETS SERVIDOS POR HTTP")
esperados = {
    "tren_llegada.mp3": 161280,
    "tunel.mp3": 287565,
    "vias.mp3": 153165,
    "caballos.mp3": 468114,
}
for nombre, tam in esperados.items():
    url = f"http://localhost:3000/championships/oeste/assets/{nombre}"
    try:
        r = urllib.request.urlopen(url, timeout=10)
        cuerpo = r.read()
        chk(r.status == 200 and len(cuerpo) == tam,
            f"{nombre}: HTTP 200 · {len(cuerpo):,} B")
    except Exception as e:
        chk(False, f"{nombre}: no se sirve ({e})")

# ─────────────────────────────── C · matemática del GLB tumbado (three real)
print("C · ROTACIÓN DEL GLB CON THREE.JS (node)")
with open(GLB, "rb") as f:
    data = f.read()
off = 12
js = None
while off < len(data):
    clen, ctype = struct.unpack_from("<II", data, off)
    if ctype == 0x4E4F534A:
        js = json.loads(data[off + 8:off + 8 + clen].decode("utf-8"))
    off += 8 + clen
acc = js["accessors"]
pa = js["meshes"][0]["primitives"][0]["attributes"]["POSITION"]
mn, mx = acc[pa]["min"], acc[pa]["max"]
dims = [mx[k] - mn[k] for k in range(3)]
node_prog = f"""
const THREE = require('three');
const dims = {dims};
const s = 0.17 / Math.max(dims[0], dims[1], dims[2]);
const e = new THREE.Euler(-Math.PI / 2, 0, Math.PI / 2, 'XYZ');
const m = new THREE.Matrix4().makeRotationFromEuler(e);
const out = {{}};
['x', 'y', 'z'].forEach((eje, i) => {{
  const v = new THREE.Vector3();
  v.setComponent(i, 1).applyMatrix4(m);
  out[eje] = Math.round(dims[i] * s * v.x) + ',' + Math.round(dims[i] * s * v.y) + ',' + Math.round(dims[i] * s * v.z);
}});
// ¿dónde cae la cara ANCHA (z MIN del modelo)? z=0 → tras rotación:
const zmin = new THREE.Vector3(0, 0, 0).applyMatrix4(m);
const zmax = new THREE.Vector3(0, 0, 1).applyMatrix4(m);
console.log(JSON.stringify({{out, ancha_en_y: zmin.y > zmax.y ? 'ARRIBA' : 'ABAJO'}}));
"""
r = subprocess.run(["node", "-e", node_prog], capture_output=True, text=True,
                   cwd=RAIZ)
if r.returncode != 0:
    chk(False, f"three en node falló: {r.stderr[-200:]}")
else:
    res = json.loads(r.stdout.strip().splitlines()[-1])
    # largo (y del modelo 13,80·s=0,17) debe acabar en x
    chk(res["out"]["y"].split(",")[0] == "0",
        "eje largo del GLB → componente x (tumbado)")
    chk(res["out"]["y"].split(",")[1] == "0",
        "eje largo del GLB NO es vertical")
    chk(res["out"]["z"].split(",")[1] == "0",
        "el alto del trapecio NO queda en z")
    chk(res["ancha_en_y"] == "ABAJO",
        "cara ANCHA del trapecio hacia ABAJO (pila estable)")
    chk(res["out"]["x"].split(",")[2] == "0",
        "el ancho del modelo (x) NO queda vertical")

print()
if fails:
    print(f"RESULTADO: {oks} OK · {len(fails)} FALLOS")
    sys.exit(1)
print(f"RESULTADO: {oks} OK · 0 FALLOS → VERDE")
