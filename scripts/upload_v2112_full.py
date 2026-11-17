#!/usr/bin/env python3
"""Re-subida v2.112 con captura de la respuesta COMPLETA de gofile (el
frontend web está caído; verificamos contra el host de store directo)."""
import hashlib, json, os, sys, time
import requests

PATH = "/home/z/my-project/download/crazypp-v2112.zip"

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

digest = md5(PATH)
size = os.path.getsize(PATH)
print(f"[i] {os.path.basename(PATH)}  {size:,} B  md5={digest}")

url = "https://store1.gofile.io/contents/uploadfile"
with open(PATH, "rb") as f:
    r = requests.post(url, files={"file": ("crazypp-v2112.zip", f)},
                      timeout=1800)
print("[i] estado:", r.status_code)
j = r.json()
print("[i] respuesta completa:", json.dumps(j)[:800])
if j.get("status") != "ok":
    sys.exit(1)
d = j["data"]
fid = d.get("fileId") or d.get("id")
page = d.get("downloadPage")
print("[OK] fileId:", fid)
print("[OK] página:", page)
with open("/home/z/my-project/scripts/upload_last.json", "w") as f:
    json.dump({"page": page, "fileId": fid, "md5": digest, "size": size,
               "name": d.get("fileName") or "crazypp-v2112.zip",
               "raw": d}, f, indent=2)
