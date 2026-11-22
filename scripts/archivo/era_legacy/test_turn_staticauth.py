#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TURN Allocate (RFC 5766 long-term) contra staticauth.openrelay.metered.ca
usando el esquema REST/static-auth de coturn que Metered documenta para Nextcloud:
  username = <expiry unix ts>
  password = base64(HMAC-SHA1(secret, username))   secreto público: openrelayprojectsecret
Prueba UDP :80 :443 :3478 y TCP :443.
"""
import base64
import hashlib
import hmac
import os
import socket
import struct
import time

MAGIC = 0x2112A442
ALLOCATE = 0x0003
HOST = "staticauth.openrelay.metered.ca"
SECRET = "openrelayprojectsecret"
USER = "openrelayproject"


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


def creds():
    username = str(int(time.time()) + 3600)  # expira en 1 h
    dig = hmac.new(SECRET.encode(), username.encode(), hashlib.sha1).digest()
    return username, base64.b64encode(dig).decode()


def build_allocate(u, pw, realm=None, nonce=None):
    attrs = attr(0x0019, b"\x11\x00\x00\x00")
    if realm and nonce:
        attrs += attr(0x0006, u.encode())
        attrs += attr(0x0014, realm.encode())
        attrs += attr(0x0015, nonce.encode())
    ln = len(attrs) + (24 if realm and nonce else 0)
    txid = os.urandom(12)
    msg = struct.pack("!HHI", ALLOCATE, ln, MAGIC) + txid + attrs
    if realm and nonce:
        key = hashlib.md5(f"{u}:{realm}:{pw}".encode()).digest()
        base = msg + struct.pack("!HH", 0x0008, 0x0014)
        msg = base + hmac.new(key, base, hashlib.sha1).digest()
    return msg, txid


def udp_try(port):
    u, pw = creds()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(6)
    try:
        msg, _ = build_allocate(u, pw)
        s.sendto(msg, (HOST, port))
        try:
            data, _ = s.recvfrom(2048)
        except socket.timeout:
            print(f"  UDP :{port} sin respuesta")
            return False
        t, ln, _ = struct.unpack("!HHI", data[:8])
        a = parse_attrs(data[8:8 + ln])
        if t == (ALLOCATE | 0x0110):
            e = a.get(0x0011)
            code = (e[1] & 0x07) * 100 + e[2] if e else -1
            realm = a.get(0x0014, b"").decode(errors="replace")
            nonce = a.get(0x0015, b"").decode(errors="replace")
            if code != 401:
                print(f"  UDP :{port} err={code}")
                return False
            msg2, txid2 = build_allocate(u, pw, realm, nonce)
            s.sendto(msg2, (HOST, port))
            try:
                d2, _ = s.recvfrom(2048)
            except socket.timeout:
                print(f"  UDP :{port} 2º Allocate sin respuesta")
                return False
            t2, l2, _ = struct.unpack("!HHI", d2[:8])
            a2 = parse_attrs(d2[8:8 + l2])
            if t2 == (ALLOCATE | 0x0100):
                r = a2.get(0x0016)
                life = a2.get(0x000D)
                lf = struct.unpack("!I", life)[0] if life and len(life) == 4 else None
                print(f"  UDP :{port} ✅ ALLOCATE OK relé={xor_addr(r) if r and len(r) >= 8 else '?'} lifetime={lf}s")
                return True
            if 0x0011 in a2:
                e2 = a2[0x0011]
                print(f"  UDP :{port} ❌ 2º Allocate err={(e2[1] & 0x07) * 100 + e2[2]}")
            else:
                print(f"  UDP :{port} respuesta 2ª type=0x{t2:04x}")
            return False
        print(f"  UDP :{port} respuesta inesperada type=0x{t:04x}")
        return False
    except OSError as e:
        print(f"  UDP :{port} error {e}")
        return False
    finally:
        s.close()


def tcp_try(port):
    u, pw = creds()
    try:
        s = socket.create_connection((HOST, port), timeout=8)
        s.settimeout(8)
        msg, _ = build_allocate(u, pw)
        s.sendall(msg)
        d = s.recv(2048)
        t, ln, _ = struct.unpack("!HHI", d[:8])
        a = parse_attrs(d[8:8 + ln])
        e = a.get(0x0011)
        code = (e[1] & 0x07) * 100 + e[2] if e else -1
        realm = a.get(0x0014, b"").decode(errors="replace")
        nonce = a.get(0x0015, b"").decode(errors="replace")
        if code == 401:
            msg2, _ = build_allocate(u, pw, realm, nonce)
            s.sendall(msg2)
            d2 = s.recv(2048)
            t2, l2, _ = struct.unpack("!HHI", d2[:8])
            a2 = parse_attrs(d2[8:8 + l2])
            if t2 == (ALLOCATE | 0x0100):
                r = a2.get(0x0016)
                print(f"  TCP :{port} ✅ ALLOCATE OK relé={xor_addr(r) if r and len(r) >= 8 else '?'}")
                s.close()
                return True
            if 0x0011 in a2:
                e2 = a2[0x0011]
                print(f"  TCP :{port} ❌ 2º Allocate err={(e2[1] & 0x07) * 100 + e2[2]}")
            else:
                print(f"  TCP :{port} respuesta 2ª type=0x{t2:04x}")
        else:
            print(f"  TCP :{port} 1ª respuesta type=0x{t:04x} err={code}")
        s.close()
        return False
    except OSError as e:
        print(f"  TCP :{port} error {type(e).__name__}")
        return False


if __name__ == "__main__":
    print(f"TURN Allocate static-auth -> {HOST} (user={USER}, esquema coturn REST)")
    ok = False
    for p in (80, 443, 3478):
        if udp_try(p):
            ok = True
    if tcp_try(443):
        ok = True
    print("RESULTADO:", "TURN STATIC-AUTH OPERATIVO ✅" if ok else "SIN RELÉ ❌")
    raise SystemExit(0 if ok else 1)
