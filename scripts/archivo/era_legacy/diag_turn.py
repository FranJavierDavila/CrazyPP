#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnóstico: ¿UDP saliente bloqueado en el sandbox o problema de Open Relay?
1) Binding STUN de control a stun.l.google.com:19302 (UDP)
2) DNS de openrelay.metered.ca
3) TURN Allocate sobre TCP a openrelay.metered.ca:443 (mismas credenciales)
"""
import hashlib
import hmac
import os
import socket
import struct
import sys

MAGIC = 0x2112A442
BINDING = 0x0001
ALLOCATE = 0x0003


def pad4(b):
    return b + b"\x00" * ((4 - len(b) % 4) % 4)


def attr(t, v):
    return struct.pack("!HH", t, len(v)) + pad4(v)


def parse_attrs(data):
    out = {}
    off = 0
    while off + 4 <= len(data):
        t, ln = struct.unpack("!HH", data[off:off + 4])
        out[t] = data[off + 4:off + 4 + ln]
        off += 4 + ((ln + 3) // 4) * 4
    return out


def xor_addr(raw):
    port = struct.unpack("!H", raw[1:3])[0] ^ (MAGIC >> 16)
    xa = struct.unpack("!I", raw[3:7])[0] ^ MAGIC
    ip = ".".join(str((xa >> s) & 0xFF) for s in (24, 16, 8, 0))
    return ip, port


# 1) STUN de control (UDP)
try:
    ip = socket.gethostbyname("stun.l.google.com")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)
    txid = os.urandom(12)
    s.sendto(struct.pack("!HHI", BINDING, 0, MAGIC) + txid, (ip, 19302))
    try:
        data, _ = s.recvfrom(512)
        a = parse_attrs(data[8:struct.unpack("!H", data[2:4])[0] + 8])
        m = a.get(0x0020)
        print(f"STUN Google UDP: RESPUESTA ✅ mapped={xor_addr(m) if m else '?'}")
    except socket.timeout:
        print("STUN Google UDP: sin respuesta -> UDP saliente BLOQUEADO en sandbox")
    s.close()
except Exception as e:
    print(f"STUN Google UDP: error {e}")

# 2) DNS Open Relay
for h in ("openrelay.metered.ca", "staticauth.openrelay.metered.ca"):
    try:
        ips = {i[4][0] for i in socket.getaddrinfo(h, None, socket.AF_INET)}
        print(f"DNS {h}: {sorted(ips)}")
    except Exception as e:
        print(f"DNS {h}: ERROR {e}")

# 3) TURN Allocate sobre TCP (mismo protocolo STUN por stream TCP)
def build_allocate(creds=None):
    attrs = attr(0x0019, b"\x11\x00\x00\x00")
    mi = False
    if creds:
        u, realm, nonce, pw = creds
        attrs += attr(0x0006, u.encode())
        attrs += attr(0x0014, realm.encode())
        attrs += attr(0x0015, nonce.encode())
        mi = True
    ln = len(attrs) + (24 if mi else 0)
    msg = struct.pack("!HHI", ALLOCATE, ln, MAGIC) + os.urandom(12) + attrs
    if mi:
        key = hashlib.md5(f"{u}:{realm}:{pw}".encode()).digest()
        base = msg + struct.pack("!HH", 0x0008, 0x0014)
        msg = base + hmac.new(key, base, hashlib.sha1).digest()
    return msg


try:
    ip = socket.gethostbyname("openrelay.metered.ca")
    s = socket.create_connection((ip, 443), timeout=8)
    print(f"TCP openrelay.metered.ca:443 conectado ✅")
    s.settimeout(8)
    s.sendall(build_allocate())
    data = s.recv(2048)
    if not data:
        print("TCP TURN: conexión cerrada sin respuesta")
    else:
        mtype, mlen, _ = struct.unpack("!HHI", data[:8])
        a = parse_attrs(data[8:8 + mlen])
        if mtype == (ALLOCATE | 0x0110) and 0x0011 in a:
            e = a[0x0011]
            code = (e[1] & 0x07) * 100 + e[2]
            realm = a.get(0x0014, b"").decode(errors="replace")
            nonce = a.get(0x0015, b"").decode(errors="replace")
            print(f"TCP TURN: 401 realm='{realm}' nonce='{nonce[:24]}…'")
            if code == 401 and realm and nonce:
                s.sendall(build_allocate(("openrelayproject", realm, nonce, "openrelayproject")))
                d2 = s.recv(2048)
                t2, l2, _ = struct.unpack("!HHI", d2[:8])
                a2 = parse_attrs(d2[8:8 + l2])
                if t2 == (ALLOCATE | 0x0100):
                    r = a2.get(0x0016)
                    print(f"TCP TURN: ✅ ALLOCATE OK relé={xor_addr(r) if r else '?'}")
                elif 0x0011 in a2:
                    e2 = a2[0x0011]
                    print(f"TCP TURN: ❌ err={(e2[1] & 0x07) * 100 + e2[2]}")
                else:
                    print(f"TCP TURN: respuesta 2ª type=0x{t2:04x} attrs={list(a2)}")
        else:
            print(f"TCP TURN: respuesta inesperada type=0x{mtype:04x}")
    s.close()
except Exception as e:
    print(f"TCP TURN: error {type(e).__name__}: {e}")
